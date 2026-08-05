"""
test_cdn_performance.py
- SOOP TV 스마트 TV 앱 CDN 성능 및 네트워크 품질 검증 테스트
- 비디오 스트림 CDN 캐시 히트율(Cache Hit Ratio), HLS 세그먼트 수신 상태, 도메인 모니터링
"""
import time
import pytest
from core.cdn_monitor import CDNCacheMonitor
from pages.home_page import HomePage
from pages.live_player_page import LivePlayerPage


class BaseCDNTest:
    @pytest.fixture(autouse=True)
    def enter_live_player_for_cdn_test(self, driver):
        """홈 → 지정 방송 진입 후 플레이어 로드 대기"""
        home = HomePage(driver)
        home.is_loaded(timeout=10)
        time.sleep(3)

        target_title = "궈가입니"
        found = False
        for _ in range(15):
            html = driver.cdp.evaluate("document.activeElement.outerHTML") or ""
            if target_title in html:
                driver.press_enter()
                found = True
                break
            driver.press_right()
            time.sleep(1.0)

        if not found:
            pytest.fail("지정한 방송으로 포커스를 이동할 수 없습니다.")

        time.sleep(3)
        player = LivePlayerPage(driver)
        assert player.is_loaded(timeout=30), "LIVE 플레이어 진입 실패"


class TestCDNPerformance(BaseCDNTest):
    def test_live_stream_cdn_cache_hit_ratio(self, driver):
        """
        [CDN 성능] LIVE 방송 시청 중 CDN 비디오 세그먼트 요청 캡처 및 캐시 히트율(Cache Hit Ratio) 측정
        - 15초 동안 재생 중 수신되는 .ts / .m4s / .m3u8 요청의 Response Header(X-Cache, Age 등) 분석
        """
        monitor = CDNCacheMonitor(driver)
        monitor.start()

        # 15초간 방송 재생하며 CDP 네트워크 트래픽 수집
        time.sleep(15)

        monitor.stop()
        stats = monitor.get_stats()

        print("\n==========================================")
        print("          [CDN 캐시 히트율 측정 결과]       ")
        print("==========================================")
        print(f" - 감지된 총 패킷 요청 수: {stats['total_requests']}")
        print(f" - 비디오 세그먼트 수: {stats['segment_total']}")
        print(f" - 세그먼트 캐시 HIT 수: {stats['segment_hits']}")
        print(f" - 세그먼트 캐시 MISS 수: {stats['segment_misses']}")
        print(f" - 세그먼트 캐시 히트율: {stats['segment_hit_ratio']}%")
        if stats['records']:
            print("\n[감지된 미디어 URL 예시]")
            for r in stats['records'][:3]:
                print(f"  * [{r['cache_status']}] {r['url'][:90]}... (Header: {r['header']})")
        print("==========================================")

        assert stats['total_requests'] > 0, "CDP 네트워크 모니터링 중 미디어 세그먼트 요청을 감지하지 못했습니다."

    def test_cdn_stream_domain_and_manifest_validity(self, driver):
        """
        [CDN 도메인] <video> 태그의 HLS 스트림 URL이 정상 CDN 서버 도메인을 타는지 검증
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
