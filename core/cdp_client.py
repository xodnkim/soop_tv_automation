"""
cdp_client.py
- WebSocket 기반 최소 CDP(Chrome DevTools Protocol) 클라이언트 (플랫폼 공용)
"""
import json
import queue
import threading
import time
import requests
import websocket

def get_page_ws_url(cdp_http_url: str) -> str:
    start = time.time()
    last_err = None
    while time.time() - start < 15:
        try:
            resp = requests.get(f"{cdp_http_url}/json", timeout=5)
            resp.raise_for_status()
            targets = resp.json()
            page_targets = [t for t in targets if t.get("type") == "page"]
            if page_targets:
                return page_targets[0]["webSocketDebuggerUrl"]
        except Exception as e:
            last_err = e
        time.sleep(1)
    
    raise RuntimeError(f"'{cdp_http_url}/json' 에서 page 타겟을 찾을 수 없습니다 (Timeout 15s). Last error: {last_err}")

class CDPClient:
    def __init__(self, ws_url: str, connect_timeout: float = 5.0):
        self.ws_url = ws_url
        self._msg_id = 0
        self._id_lock = threading.Lock()
        self._pending = {}
        self._pending_lock = threading.Lock()
        self._event_handlers = {}

        self.ws = websocket.WebSocketApp(ws_url, on_message=self._on_message)
        self._thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self._thread.start()

        start = time.time()
        while not (self.ws.sock and self.ws.sock.connected):
            if time.time() - start > connect_timeout:
                raise TimeoutError(f"CDP websocket 연결 실패: {ws_url}")
            time.sleep(0.05)

    def _next_id(self) -> int:
        with self._id_lock:
            self._msg_id += 1
            return self._msg_id

    def _on_message(self, ws, message):
        data = json.loads(message)
        if "id" in data:
            with self._pending_lock:
                q = self._pending.pop(data["id"], None)
            if q is not None:
                q.put(data)
        elif "method" in data:
            for handler in self._event_handlers.get(data["method"], []):
                handler(data.get("params", {}))

    def send(self, method: str, params: dict | None = None, timeout: float = 10.0) -> dict:
        msg_id = self._next_id()
        q: queue.Queue = queue.Queue()
        with self._pending_lock:
            self._pending[msg_id] = q
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        try:
            data = q.get(timeout=timeout)
        except queue.Empty:
            with self._pending_lock:
                self._pending.pop(msg_id, None)
            raise TimeoutError(f"CDP 응답 타임아웃: {method}")
        if "error" in data:
            raise RuntimeError(f"CDP error on {method}: {data['error']}")
        return data.get("result", {})

    def send_async(self, method: str, params: dict | None = None):
        msg_id = self._next_id()
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))

    def on_event(self, method: str, callback):
        self._event_handlers.setdefault(method, []).append(callback)

    def off_event(self, method: str, callback):
        handlers = self._event_handlers.get(method)
        if handlers and callback in handlers:
            handlers.remove(callback)

    def evaluate(self, expression: str, timeout: float = 10.0):
        result = self.send(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True},
            timeout=timeout,
        )
        return result.get("result", {}).get("value")

    def close(self):
            try:
                self._event_handlers.clear()
                if hasattr(self, 'ws') and self.ws:
                    self.ws.keep_running = False
                    self.ws.close()
                    # 소켓 객체 완전히 제거
                    if hasattr(self.ws, 'sock') and self.ws.sock:
                        self.ws.sock.close()
            except Exception as e:
                print(f"[CDP CLOSE WARN] {e}")