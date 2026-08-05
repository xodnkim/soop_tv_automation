"""
cdn_monitor.py
- CDP Network 이벤트를 활용한 CDN 캐시 히트율(Cache Hit Ratio) 측정 모듈
- HTTP Response Header(X-Cache, CF-Cache-Status, Age 등)를 실시간 감시 및 수집
"""
import time


class CDNCacheMonitor:
    def __init__(self, driver):
        self.driver = driver
        self.is_monitoring = False
        self.records = []
        self._handler = self._on_response_received

    def start(self):
        """CDP Network 도메인 활성화 및 캡처 시작"""
        self.records.clear()
        self.is_monitoring = True
        try:
            self.driver.cdp.send("Network.enable")
            self.driver.cdp.on_event("Network.responseReceived", self._handler)
        except Exception as e:
            print(f"[CDN MONITOR WARN] Network.enable 설정 실패: {e}")

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

        # 비디오 세그먼트, HLS 플레이리스트, 미디어 관련 파일 필터링
        url_lower = url.lower()
        is_media_url = any(ext in url_lower for ext in [".ts", ".m3u8", ".m4s", "playlist", "segment", "chunk", "live", "auth_playlist"])
        
        if is_media_url:
            headers = response.get("headers", {})
            # Header 키를 소문자로 정규화
            headers_lower = {str(k).lower(): str(v) for k, v in headers.items()}

            cache_status = "UNKNOWN"
            detected_header = None

            # 주요 CDN 캐시 응답 헤더 모니터링
            for header_name in ["x-cache", "cf-cache-status", "x-proxy-cache", "x-cache-hits", "x-served-by", "x-soop-cache", "via"]:
                if header_name in headers_lower:
                    val = headers_lower[header_name].upper()
                    detected_header = f"{header_name}={headers_lower[header_name]}"
                    if "HIT" in val:
                        cache_status = "HIT"
                        break
                    elif "MISS" in val or "EXPIRED" in val:
                        cache_status = "MISS"
                        break

            # Secondary 체크: Age 헤더 (Age > 0 시 캐시된 것으로 판별)
            if cache_status == "UNKNOWN" and "age" in headers_lower:
                age_val = headers_lower["age"]
                detected_header = f"age={age_val}"
                if age_val.isdigit() and int(age_val) > 0:
                    cache_status = "HIT"
                elif age_val == "0":
                    cache_status = "MISS"

            self.records.append({
                "url": url,
                "status": response.get("status"),
                "cache_status": cache_status,
                "header": detected_header,
                "timestamp": time.time()
            })

    def get_stats(self) -> dict:
        """수집된 네트워크 기록 통계 반환"""
        total = len(self.records)
        hits = sum(1 for r in self.records if r["cache_status"] == "HIT")
        misses = sum(1 for r in self.records if r["cache_status"] == "MISS")
        unknowns = sum(1 for r in self.records if r["cache_status"] == "UNKNOWN")

        # 비디오 세그먼트(.ts, .m4s)만 추출한 통계
        segment_records = [r for r in self.records if any(ext in r["url"].lower() for ext in [".ts", ".m4s"])]
        seg_total = len(segment_records)
        seg_hits = sum(1 for r in segment_records if r["cache_status"] == "HIT")
        seg_misses = sum(1 for r in segment_records if r["cache_status"] == "MISS")

        ratio = (hits / total * 100) if total > 0 else 0.0
        seg_ratio = (seg_hits / seg_total * 100) if seg_total > 0 else 0.0

        return {
            "total_requests": total,
            "hit_count": hits,
            "miss_count": misses,
            "unknown_count": unknowns,
            "hit_ratio": round(ratio, 2),
            "segment_total": seg_total,
            "segment_hits": seg_hits,
            "segment_misses": seg_misses,
            "segment_hit_ratio": round(seg_ratio, 2),
            "records": self.records
        }
