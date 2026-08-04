"""
lg_controller.py
- LG webOS(ares-cli) TV 제어 담당.

[중요] ares-inspect가 여는 SSH 터널(포트포워딩)은 Node.js 프로세스 내부에서
직접 구현된 것이라(별도 ssh.exe를 부르는 방식이 아님), 그 프로세스를 죽이는
순간 터널도 같이 닫힌다. 그래서:
  - 포트를 얻은 뒤에도 절대 proc를 죽이면 안 된다 (살려둬야 포트가 유지됨)
  - 세션이 끝날 때만 stop_inspect()로 정리한다
  - Windows에서 shell=True로 띄우면 cmd.exe(부모) -> node.exe(진짜 프로세스, 자식)
    구조라서 proc.terminate()/kill()은 부모만 죽이고 자식은 고아로 남는다.
    반드시 taskkill /T(트리 전체)로 죽여야 진짜로 정리된다.
"""
import re
import subprocess
import sys
import threading
import queue
import time

from config import config
from core.controllers.base_controller import BaseTVController


def _run(cmd: str, timeout: float = config.SUBPROCESS_TIMEOUT_SEC, label: str = ""):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT][{label or cmd}] {timeout}초 동안 응답 없음 -> 건너뜁니다.")
        return None


class LGTVController(BaseTVController):
    def __init__(self, device_name: str = None, app_id: str = None):
        self.device_name = device_name or config.LG_DEVICE_NAME
        self.app_id = app_id or config.LG_APP_ID
        self._inspect_proc = None  # ares-inspect 백그라운드 프로세스 (터널 유지용, 절대 조기 종료 금지)

    def stop_app(self):
        print(f"[LG] 앱 종료 시도 (appId={self.app_id})...")
        res = _run(f"ares-launch -d {self.device_name} -c {self.app_id}", timeout=15, label="ares-launch close")
        out = ((res.stdout or "") + (res.stderr or "")) if res else ""
        print(f"[LG] close 결과: {out.strip()}")
        time.sleep(1.5)

    def launch_app(self):
        print(f"[LG] 앱 실행 (appId={self.app_id})...")
        res = _run(f"ares-launch -d {self.device_name} {self.app_id}", timeout=15, label="ares-launch")
        out = ((res.stdout or "") + (res.stderr or "")) if res else ""
        print(f"[LG] launch 결과: {out.strip()}")
        time.sleep(2.0)

    def stop_inspect(self):
        """
        보관 중인 ares-inspect 프로세스를 완전히 종료한다 (트리 전체).
        Windows: taskkill /F /T 로 cmd.exe + node.exe 자식까지 싹 정리.
        그 외 OS: 일반 terminate/kill.
        """
        if not self._inspect_proc or self._inspect_proc.poll() is not None:
            self._inspect_proc = None
            return

        print(f"[LG] ares-inspect 프로세스 정리 중 (PID={self._inspect_proc.pid})...")
        if sys.platform.startswith("win"):
            subprocess.run(
                f"taskkill /F /T /PID {self._inspect_proc.pid}",
                shell=True, capture_output=True,
            )
        else:
            self._inspect_proc.terminate()
            try:
                self._inspect_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._inspect_proc.kill()
        self._inspect_proc = None

    def open_inspect_port(self, timeout: float = 20.0) -> int:
        """
        ares-inspect를 백그라운드(Popen)로 띄워서 프로세스를 살려둔 채로
        stdout에서 포트 번호가 찍힌 줄을 찾을 때까지 기다린다.
        포트를 찾아도 프로세스는 절대 죽이지 않고 self._inspect_proc에 보관한다.
        """
        self.stop_inspect()  # 이전 세션이 남아있으면 먼저 정리

        cmd = f"ares-inspect -d {self.device_name} {self.app_id}"
        print(f"[LG] {cmd}  (백그라운드로 유지)")
        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )

        line_queue: "queue.Queue[str]" = queue.Queue()

        def _reader():
            for line in proc.stdout:
                line_queue.put(line)

        threading.Thread(target=_reader, daemon=True).start()

        deadline = time.time() + timeout
        ws_url = None
        seen_lines = []
        while time.time() < deadline:
            remaining = max(0.1, deadline - time.time())
            try:
                line = line_queue.get(timeout=remaining)
            except queue.Empty:
                break
            seen_lines.append(line.rstrip())
            print(f"[LG] inspect: {line.rstrip()}")
            match = re.search(r"http://localhost:(\d+)", line)
            ws_match = re.search(r"\?ws=(.*)", line)
            if ws_match:
                ws_url = "ws://" + ws_match.group(1).strip()
                break
            elif match and not ws_url:
                # Fallback to port if ws_url is somehow not in the same line or format
                ws_url = int(match.group(1))
                # Don't break here, keep reading in case the ws URL appears next

        if ws_url is None:
            # 포트를 못 구했으면 이 시도는 실패 -> 여기서만 죽여도 됨 (터널이 필요 없으므로)
            if sys.platform.startswith("win"):
                subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
            else:
                proc.terminate()
            raise RuntimeError(
                f"디버그 포트를 추출하지 못했습니다.\n명령: {cmd}\n"
                f"출력:\n" + "\n".join(seen_lines) + "\n"
                "-> 앱이 실제로 TV에서 실행 중인지, Key Server가 ON 상태였는지 확인하세요."
            )

        # 성공했으면 절대 죽이지 않고 보관 (이게 살아있어야 포트가 유지됨)
        self._inspect_proc = proc
        print(f"[LG] 터널 유지 중 (PID={proc.pid}, target={ws_url})")
        return ws_url

    def restart_app_in_debug_mode(self, reuse_if_running: bool = True) -> int | str:
        if reuse_if_running:
            try:
                return self.open_inspect_port()
            except RuntimeError:
                print("[LG] 기존 세션에 바로 붙기 실패 -> 앱을 재시작합니다.")

        self.stop_app()
        self.launch_app()
        return self.open_inspect_port()