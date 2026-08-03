"""
tizen_controller.py
- 삼성 Tizen(sdb) TV 제어 담당
"""
import re
import subprocess
import time
import requests
from config import config
from core.controllers.base_controller import BaseTVController

def _run(cmd: str, timeout: float = config.SUBPROCESS_TIMEOUT_SEC, label: str = ""):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT][{label or cmd}] {timeout}초 동안 응답 없음 -> 건너뜁니다.")
        return None

class TizenTVController(BaseTVController):
    def __init__(self, tv_ip: str = config.TIZEN_IP, app_id: str = config.TIZEN_APP_ID):
        self.tv_ip = tv_ip
        self.app_id = app_id
        self.package_id = app_id.split(".")[0]

    def connect(self):
        connect_cmd = f'"{config.SDB_PATH}" connect {self.tv_ip}:{config.SDB_PORT}'
        res = _run(connect_cmd, timeout=15, label="tizen connect")
        out = ((res.stdout or "") + (res.stderr or "")) if res else ""
        print(f"[Tizen TV] connect: {out.strip()}")

        res_devices = _run(f'"{config.SDB_PATH}" devices', timeout=10, label="tizen devices")
        devices_out = ((res_devices.stdout or "") + (res_devices.stderr or "")) if res_devices else ""
        if self.tv_ip not in devices_out:
            raise RuntimeError(f"[Tizen TV] 목록에 {self.tv_ip}가 없습니다. 연결 실패.")
        print(f"[Tizen TV] 연결 확인됨: {self.tv_ip}")

    def reset_forwarding(self):
        _run(f'"{config.SDB_PATH}" forward --remove-all', timeout=10, label="forward remove-all")

    def stop_app(self):
        print(f"[Tizen TV] 앱 종료 시도 (packageId={self.package_id})...")
        res = _run(f'"{config.SDB_PATH}" shell 0 kill {self.package_id}', timeout=10, label="tizen kill")
        out = ((res.stdout or "") + (res.stderr or "")) if res else ""
        print(f"[Tizen TV] kill 결과: {out.strip()}")
        time.sleep(1.5)

    def launch_debug(self) -> int:
        debug_cmd = f'"{config.SDB_PATH}" shell 0 debug {self.app_id}'
        res = _run(debug_cmd, timeout=15, label="tizen debug")
        stdout = (res.stdout or "").strip() if res else ""
        
        match = re.search(r"port:\s*(\d+)", stdout, re.IGNORECASE)
        if not match:
            raise RuntimeError(f"[Tizen TV] 디버그 포트 추출 실패:\n{stdout}")
        return int(match.group(1))

    def forward_port(self, port: int):
        res = _run(f'"{config.SDB_PATH}" forward tcp:{port} tcp:{port}', timeout=10, label="tizen forward")
        if res is None:
            raise RuntimeError(f"[Tizen TV] 포트 포워딩 타임아웃: tcp:{port}")
        print(f"[Tizen TV] forward: {res.stdout.strip()}")

    def get_existing_debug_port(self) -> int | None:
        res = _run(f'"{config.SDB_PATH}" forward --list', timeout=5, label="tizen forward list")
        if not res or not res.stdout:
            return None
        matches = re.findall(r"tcp:(\d+)\s+tcp:(\d+)", res.stdout)
        for local_port_str, _ in matches:
            port = int(local_port_str)
            try:
                r = requests.get(f"http://localhost:{port}/json", timeout=2)
                if r.status_code == 200 and isinstance(r.json(), list):
                    return port
            except Exception:
                continue
        return None

    def restart_app_in_debug_mode(self, reuse_if_running: bool = True) -> int:
        if reuse_if_running:
            existing_port = self.get_existing_debug_port()
            if existing_port:
                print(f"[Tizen TV] 기존 디버그 포트({existing_port}) 바인딩")
                return existing_port

        self.connect()
        self.reset_forwarding()
        self.stop_app()
        port = self.launch_debug()
        self.forward_port(port)
        time.sleep(2.0)
        return port