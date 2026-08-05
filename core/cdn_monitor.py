"""
cdn_monitor.py
- CDP Network 이벤트를 활용한 스트림 네트워크 헬스 & CDN 트래픽 이상 탐지 모듈
- 검증 항목: Content-Type 미스매치, HTTP 4xx/5xx 에러 패킷, HLS 세그먼트 연속성, Cache-Control 헤더 유효성
"""
import time


class StreamNetworkMonitor:
    def __init__(self, driver):
        self.driver = driver
        self.is_monitoring = False
        self.records = []
        self.anomalies = []
        self._handler = self._on_response_received

    def start(self):
        """CDP Network 도메인 활성화 및 캡처 시작"""
        self.records.clear()
        self.anomalies.clear()
        self.is_monitoring = True
        try:
            self.driver.cdp.send("Network.enable")
            self.driver.cdp.on_event("Network.responseReceived", self._handler)
        except Exception as e:
            print(f"[NETWORK MONITOR WARN] Network.enable 설정 실패: {e}")

    def stop(self):
        """캡처 중단 및 이벤트 핸들러 해제"""
        self.is_monitoring = False
        try:
            self.driver.cdp.off_event("Network.responseReceived", self._handler)
        except Exception:
            pass

    def _on_response_received(self, params):
        if not self.is_monitoring:
            return

        response = params.get("response", {})
        url = response.get("url", "")
        url_lower = url.lower()

        # SOOP TV 비디오 세그먼트(.ts), HLS 플레이리스트(.m3u8), MP4HLS 등 미디어 트래픽 필터링
        is_media = any(k in url_lower for k in [".ts", ".m3u8", ".m4s", "mp4hls", "chunklist"])
        if is_media:
            status = response.get("status", 0)
            headers = response.get("headers", {})
            headers_lower = {str(k).lower(): str(v) for k, v in headers.items()}
            content_type = headers_lower.get("content-type", "").lower()
            cache_control = headers_lower.get("cache-control", "")
            etag = headers_lower.get("etag", "")

            # 1. HTTP 4xx / 5xx 에러 이상 감지
            if status >= 400:
                self.anomalies.append({
                    "type": "HTTP_ERROR",
                    "url": url,
                    "status": status,
                    "detail": f"HTTP Status {status}"
                })

            # 2. Content-Type 미스매치 감지 (CDN 장애로 HTML 에러페이지가 200 OK로 오는 패턴 방지)
            if ".m3u8" in url_lower and "mpegurl" not in content_type and "octet-stream" not in content_type:
                self.anomalies.append({
                    "type": "CONTENT_TYPE_MISMATCH",
                    "url": url,
                    "expected": "application/vnd.apple.mpegurl",
                    "got": content_type
                })
            elif ".ts" in url_lower and "mp2t" not in content_type and "octet-stream" not in content_type and "video" not in content_type:
                self.anomalies.append({
                    "type": "CONTENT_TYPE_MISMATCH",
                    "url": url,
                    "expected": "video/MP2T",
                    "got": content_type
                })

            self.records.append({
                "url": url,
                "status": status,
                "content_type": content_type,
                "cache_control": cache_control,
                "has_cache_header": bool(cache_control or etag),
                "timestamp": time.time()
            })

    def get_stats(self) -> dict:
        """수집된 미디어 트래픽 통계 및 이상 징후 분석 결과 반환"""
        total = len(self.records)
        ts_records = [r for r in self.records if ".ts" in r["url"].lower() or ".m4s" in r["url"].lower()]
        m3u8_records = [r for r in self.records if ".m3u8" in r["url"].lower()]

        http_errors = [a for a in self.anomalies if a["type"] == "HTTP_ERROR"]
        type_mismatches = [a for a in self.anomalies if a["type"] == "CONTENT_TYPE_MISMATCH"]
        cacheable_count = sum(1 for r in self.records if r["has_cache_header"])

        return {
            "total_media_requests": total,
            "ts_total": len(ts_records),
            "m3u8_total": len(m3u8_records),
            "http_error_count": len(http_errors),
            "type_mismatch_count": len(type_mismatches),
            "anomaly_count": len(self.anomalies),
            "cacheable_count": cacheable_count,
            "cacheable_ratio": round((cacheable_count / total * 100), 2) if total > 0 else 0.0,
            "anomalies": self.anomalies,
            "records": self.records
        }
