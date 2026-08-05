"""
cdn_monitor.py
- CDP Network 이벤트를 활용한 CDN 세그먼트 및 캐시 히트율/캐시 설정 측정 모듈
- SOOP TV 실제 미디어 트래픽(.ts, .m3u8, mp4hls) 파이프라인 분석
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
        url_lower = url.lower()

        # SOOP TV 비디오 세그먼트(.ts), HLS 플레이리스트(.m3u8), MP4HLS 등 미디어 트래픽 필터링
        is_media = any(k in url_lower for k in [".ts", ".m3u8", ".m4s", "mp4hls", "chunklist"])
        if is_media:
            headers = response.get("headers", {})
            headers_lower = {str(k).lower(): str(v) for k, v in headers.items()}

            cache_status = "UNKNOWN"
            detected_info = []

            # 1. CDN 직접 캐시 헤더 확인 (X-Cache, CF-Cache-Status 등)
            for header_name in ["x-cache", "cf-cache-status", "x-proxy-cache", "x-cache-hits", "x-soop-cache"]:
                if header_name in headers_lower:
                    val = headers_lower[header_name].upper()
                    detected_info.append(f"{header_name}={val}")
                    if "HIT" in val:
                        cache_status = "HIT"
                        break
                    elif "MISS" in val or "EXPIRED" in val:
                        cache_status = "MISS"
                        break

            # 2. Age 헤더 확인 (Age > 0 일 때 캐시 HIT)
            if cache_status == "UNKNOWN" and "age" in headers_lower:
                age_val = headers_lower["age"]
                detected_info.append(f"age={age_val}")
                if age_val.isdigit() and int(age_val) > 0:
                    cache_status = "HIT"
                elif age_val == "0":
                    cache_status = "MISS"

            # 3. Cache-Control & ETag 헤더 확인 (캐시 정책 적용 여부)
            cache_control = headers_lower.get("cache-control", "")
            etag = headers_lower.get("etag", "")
            if cache_control:
                detected_info.append(f"cache-control={cache_control}")
            if etag:
                detected_info.append(f"etag={etag[:15]}")

            # HTTP 304 (Not Modified) 수신 시 캐시 HIT
            if response.get("status") == 304:
                cache_status = "HIT"

            self.records.append({
                "url": url,
                "status": response.get("status"),
                "content_type": headers_lower.get("content-type", ""),
                "cache_status": cache_status,
                "info": " | ".join(detected_info) if detected_info else "No Cache Headers",
                "timestamp": time.time()
            })

    def get_stats(self) -> dict:
        """수집된 네트워크 세그먼트 패킷 통계 분석"""
        total = len(self.records)

        # .ts / .m4s 비디오 조각 세그먼트
        ts_records = [r for r in self.records if ".ts" in r["url"].lower() or ".m4s" in r["url"].lower()]
        ts_total = len(ts_records)
        ts_hits = sum(1 for r in ts_records if r["cache_status"] == "HIT")
        ts_misses = sum(1 for r in ts_records if r["cache_status"] == "MISS")

        # .m3u8 플레이리스트
        m3u8_records = [r for r in self.records if ".m3u8" in r["url"].lower()]
        m3u8_total = len(m3u8_records)

        # Cache-Control max-age 가 적용된 캐시 가능 패킷 비율
        cacheable_count = sum(1 for r in self.records if "max-age" in r["info"].lower())

        ts_hit_ratio = round((ts_hits / ts_total * 100), 2) if ts_total > 0 else 0.0
        cacheable_ratio = round((cacheable_count / total * 100), 2) if total > 0 else 0.0

        return {
            "total_media_requests": total,
            "ts_total": ts_total,
            "ts_hits": ts_hits,
            "ts_misses": ts_misses,
            "ts_hit_ratio": ts_hit_ratio,
            "m3u8_total": m3u8_total,
            "cacheable_count": cacheable_count,
            "cacheable_ratio": cacheable_ratio,
            "records": self.records
        }
