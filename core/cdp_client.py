"""
cdp_client.py
- TV에 내장된 Chromium은 Browser/Target 도메인을 지원하지 않아 (Browser context management is not supported)
  Playwright의 connect_over_cdp()가 실패한다.
- 이 클라이언트는 Page/Runtime 도메인만 사용하는 최소 CDP 클라이언트로,
  websocket으로 직접 JSON-RPC 프로토콜을 주고받는다.
"""

import json
import queue
import threading
import time

import requests
import websocket  # pip install websocket-client


def get_page_ws_url(cdp_http_url: str) -> str:
    """http://localhost:<port> 에서 첫 번째 page 타겟의 webSocketDebuggerUrl을 가져온다"""
    resp = requests.get(f"{cdp_http_url}/json", timeout=5)
    resp.raise_for_status()
    targets = resp.json()
    page_targets = [t for t in targets if t.get("type") == "page"]
    if not page_targets:
        raise RuntimeError(f"'{cdp_http_url}/json' 에서 page 타겟을 찾을 수 없습니다: {targets}")
    return page_targets[0]["webSocketDebuggerUrl"]


class CDPClient:
    """Page/Runtime 등 도메인 명령을 주고받는 최소 CDP 클라이언트"""

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
        """명령을 보내고 응답(result)을 기다려서 반환. 에러면 예외 발생."""
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
        """응답을 기다리지 않고 보내기만 함 (이벤트 콜백 안에서 호출할 때 데드락 방지용)"""
        msg_id = self._next_id()
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))

    def on_event(self, method: str, callback):
        self._event_handlers.setdefault(method, []).append(callback)

    def off_event(self, method: str, callback):
        """on_event로 등록한 콜백을 해제한다. 없으면 조용히 무시."""
        handlers = self._event_handlers.get(method)
        if handlers and callback in handlers:
            handlers.remove(callback)

    def evaluate(self, expression: str, timeout: float = 10.0):
        """JS 표현식을 실행하고 값을 반환 (returnByValue=True)"""
        result = self.send(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True},
            timeout=timeout,
        )
        return result.get("result", {}).get("value")

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass
