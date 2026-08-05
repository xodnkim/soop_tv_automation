"""
test_cdn_performance.py
- SOOP TV 스마트 TV 앱 스트림 네트워크 헬스 및 CDN 이상 탐지 테스트 (Stream Network Health & Smoke Suite)
- CDP Network 도메인을 활용한 트래픽 검증: HTTP 에러(4xx/5xx), Content-Type 미스매치, HLS 세그먼트 수신 상태, CDN 도메인 검증
"""
import time
import pytest
from core.cdn_monitor import StreamNetworkMonitor
from pages.home_page import HomePage
from pages.live_player_page import LivePlayerPage


class BaseCDNTest:
    @pytest.fixture(autouse=True)
    def enter_live_player_and_monitor(self, driver):
        """홈 → 지정 방송 진입 전 모니터링을 미리 켜서 초기 비디오 세그먼트부터 수집"""
        self.monitor = StreamNetworkMonitor(driver)
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
    def test_live_stream_network_health_and_anomaly_check(self, driver):
        """
        [스트림 네트워크 헬스 검증] LIVE 방송 시청 중 CDP 패킷 분석으로 CDN 무음 에러 및 패킷 이상 감지
        - HTTP 4xx/5xx 상태 코드 에러 여부
        - Content-Type 미스매치 여부 (CDN 장애 시 HTML 에러 페이지가 200 OK로 수신되는 현상 탐지)
        - Cache-Control / ETag 헤더 적용률 검증
        """
        # 10초 추가 시청하며 미디어 세그먼트 수신 추적
        time.sleep(10)

        stats = self.monitor.get_stats()

        print("\n==================================================")
        print("     [SOOP TV 스트림 네트워크 헬스 리포트]  ")
        print("==================================================")
        print(f" - 총 모니터링 경과 시간: {stats['total_monitoring_time']} 초")
        print(f" - 수신된 총 미디어 요청 수: {stats['total_media_requests']} 건")
        print(f" - 비디오 세그먼트(.ts) 수신 수: {stats['ts_total']} 건")
        print(f" - HLS 플레이리스트(.m3u8) 수신 수: {stats['m3u8_total']} 건 (갱신 주기: 약 {stats['avg_m3u8_interval']}초)")
        print(f" - .ts 수신 간격 (평균/최소/최대): {stats['avg_ts_interval']}s / {stats['min_ts_interval']}s / {stats['max_ts_interval']}s")
        print(f" - HTTP 4xx/5xx 에러 건수: {stats['http_error_count']} 건")
        print(f" - Content-Type 미스매치 건수: {stats['type_mismatch_count']} 건")
        print(f" - Cache-Control 헤더 적용률: {stats['cacheable_ratio']}%")
        print("--------------------------------------------------")
        if stats['records']:
            print(" [수신된 미디어 패킷 샘플 목록]")
            for i, r in enumerate(stats['records'][:5], 1):
                print(f"  {i}. [{r['status']}] {r['content_type']} | {r['url'][:75]}...")
        print("==================================================")

        # 1. 미디어 패킷 수신 검증
        assert stats['total_media_requests'] > 0, "방송 재생 중 미디어 트래픽(HLS/세그먼트)을 감지하지 못했습니다."
        assert stats['ts_total'] > 0, "비디오 세그먼트(.ts) 수신 기록이 0건입니다."

        # 2. HTTP Status 에러 검증 (4xx/5xx 발생 시 FAILED)
        assert stats['http_error_count'] == 0, f"미디어 수신 중 HTTP 에러 발생: {stats['anomalies']}"

        # 3. Content-Type 미스매치 검증 (HTML 에러 페이지 수신 방지)
        assert stats['type_mismatch_count'] == 0, f"Content-Type 미스매치 장애 감지: {stats['anomalies']}"

        # 4. 세그먼트 수신 연속성/버퍼링 검증 (간격이 8초 이상 벌어지면 FAILED)
        assert stats['buffering_error_count'] == 0, f"비디오 패킷 수신 지연(버퍼링) 감지: {stats['anomalies']}"

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
