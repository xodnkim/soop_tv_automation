"""
test_cdn_performance.py
- SOOP TV 스마트 TV 앱 CDN 성능 및 네트워크 품질 검증 테스트
- 비디오 스트림 CDN 캐시 히트율(Cache Hit Ratio), HLS 세그먼트(.ts) 수신 상태, CDN 도메인 모니터링
"""
import time
import pytest
from core.cdn_monitor import CDNCacheMonitor
from pages.home_page import HomePage
from pages.live_player_page import LivePlayerPage


class BaseCDNTest:
    @pytest.fixture(autouse=True)
    def enter_live_player_and_monitor(self, driver):
        """홈 → 지정 방송 진입 전 모니터링을 미리 켜서 초기 비디오 세그먼트부터 수집"""
        self.monitor = CDNCacheMonitor(driver)
        self.monitor.start()

        home = HomePage(driver)
        home.is_loaded(timeout=10)
        time.sleep(3)

        if not home.find_and_enter_broadcast("궈가입니", max_attempts=15):
            pytest.fail("지정한 방송으로 포커스를 이동할 수 없습니다.")

        time.sleep(3)
        player = LivePlayerPage(driver)
        assert player.is_loaded(timeout=30), "LIVE 플레이어 진입 실패"

        yield

        self.monitor.stop()


class TestCDNPerformance(BaseCDNTest):
    def test_live_stream_cdn_cache_hit_ratio(self, driver):
        """
        [CDN 성능 검증] LIVE 방송 진입 및 재생 중 비디오 세그먼트(.ts) 캡처 및 캐시 히트율/캐시 정책 분석
        """
        # 추가 재생 10초간 세그먼트 패킷 지켜보기
        time.sleep(10)

        stats = self.monitor.get_stats()

        print("\n==================================================")
        print("          [SOOP TV CDN 성능 및 캐시 분석 리포트]  ")
        print("==================================================")
        print(f" - 수신된 총 미디어 요청 수: {stats['total_media_requests']} 건")
        print(f" - 비디오 세그먼트(.ts) 요청 수: {stats['ts_total']} 건")
        print(f" - HLS 플레이리스트(.m3u8) 요청 수: {stats['m3u8_total']} 건")
        print(f" - 세그먼트 캐시 HIT: {stats['ts_hits']} 건 / MISS: {stats['ts_misses']} 건")
        print(f" - 세그먼트 캐시 히트율: {stats['ts_hit_ratio']}%")
        print(f" - Cache-Control 정책 적용률: {stats['cacheable_ratio']}%")
        print("--------------------------------------------------")
        if stats['records']:
            print(" [수신된 대표 미디어 패킷 샘플]")
            for i, r in enumerate(stats['records'][:5], 1):
                print(f"  {i}. [{r['cache_status']}] {r['url'][:80]}...")
                print(f"     -> Header: {r['info']}")
        print("==================================================")

        assert stats['total_media_requests'] > 0, "방송 재생 중 미디어 트래픽(HLS/세그먼트)을 감지하지 못했습니다."
        assert stats['ts_total'] > 0, "비디오 세그먼트(.ts) 수신 기록이 0건입니다."

    def test_cdn_stream_domain_and_manifest_validity(self, driver):
        """
        [CDN 도메인 검증] <video> 태그의 HLS 스트림 URL이 정규 CDN 서버 도메인을 타는지 검증
        """
        stream_url = driver.cdp.evaluate(
            "(function() {"
            "  var video = document.querySelector('video');"
            "  if (!video) return '';"
            "  var src = video.src;"
            "  if (!src) {"
            "    var source = video.querySelector('source');"
            "    src = source ? source.src : '';"
            "  }"
            "  return src;"
            "})()"
        ) or ""

        print(f"\n[감지된 비디오 스트림 URL] -> {stream_url}")

        assert stream_url != "", "<video> 태그에서 스트림 소스 URL을 추출하지 못했습니다."
        assert ".m3u8" in stream_url.lower(), f"유효한 HLS 마스터 플레이리스트 경로가 아닙니다: {stream_url}"
        assert any(domain in stream_url.lower() for domain in ["sooplive.com", "afreecatv.com", "cdn"]), \
            f"검증되지 않은 CDN 도메인 주소입니다: {stream_url}"
