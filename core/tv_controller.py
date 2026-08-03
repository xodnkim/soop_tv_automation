"""
tv_controller.py
- TV(sdb) 레벨 제어 담당: 연결, 앱 종료/실행, 포트 포워딩.
- CDP(Chrome DevTools Protocol) 레벨 제어는 core/driver.py가 담당하며,
  이 클래스는 오직 "sdb 명령"만 다룬다 (관심사 분리).

[실측으로 확인된 사항 — 이 TV/펌웨어 기준]
- 'sdb shell 0 app_launcher -s <appId>' 로 먼저 일반 실행시키는 단계는
  아무 반응이 없다 (조용히 무시됨).
- 'sdb shell 0 debug <appId>' 명령 자체가 앱을 새로 실행시키면서 동시에
  디버그 모드로 붙여준다 -> 별도 실행 단계 불필요.
- 'sdb shell 0 kill <appId>' 처럼 전체 appId(패키지ID.앱ID)를 넘기면
  종료가 안 된다. kill은 앞부분 packageId만 받는다.
  (예: 'SYhkcwoXQo.SOOPSTG' -> 'SYhkcwoXQo'만 사용)
"""

import re
import subprocess
import time

from config import config


def _run(cmd: str, timeout: float = config.SUBPROCESS_TIMEOUT_SEC, label: str = ""):
    """모든 sdb 호출에 공통으로 timeout을 강제. 걸리면 로그 남기고 None 반환."""
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT][{label or cmd}] {timeout}초 동안 응답 없음 -> 건너뜁니다.")
        return None


class TVController:
    def __init__(self, tv_ip: str = config.TV_IP, app_id: str = config.APP_ID):
        self.tv_ip = tv_ip
        self.app_id = app_id
        self.package_id = app_id.split(".")[0]

    def connect(self):
        connect_cmd = f'"{config.SDB_PATH}" connect {self.tv_ip}:{config.SDB_PORT}'
        res = _run(connect_cmd, timeout=15, label="connect")
        out = ((res.stdout or "") + (res.stderr or "")) if res else ""
        print(f"[TV] connect: {out.strip()}")

        res_devices = _run(f'"{config.SDB_PATH}" devices', timeout=10, label="devices")
        devices_out = ((res_devices.stdout or "") + (res_devices.stderr or "")) if res_devices else ""
        print(f"[TV] devices:\n{devices_out.strip()}")
        if self.tv_ip not in devices_out:
            raise RuntimeError(
                f"'sdb devices' 목록에 {self.tv_ip}가 없습니다. TV 연결 실패.\n{devices_out}\n"
                "-> 개발자 모드/IP 등록, 같은 네트워크 여부를 확인하세요."
            )
        print(f"[TV] 연결 확인됨: {self.tv_ip}")

    def reset_forwarding(self):
        _run(f'"{config.SDB_PATH}" forward --remove-all', timeout=10, label="forward --remove-all")

    def stop_app(self):
        """kill은 packageId(마침표 앞부분)만 받는다 (실측 확인됨)."""
        print(f"[TV] 앱 종료 시도 (packageId={self.package_id})...")
        res = _run(f'"{config.SDB_PATH}" shell 0 kill {self.package_id}', timeout=10, label="kill")
        out = ((res.stdout or "") + (res.stderr or "")) if res else ""
        print(f"[TV] kill 결과: {out.strip()}")
        if "Terminated" not in out:
            print("[TV][WARN] 'Terminated' 문구가 안 보입니다. 실제 종료 여부를 화면으로 확인하세요.")
        time.sleep(1.5)

    def launch_debug(self) -> int:
        """디버그 모드로 앱을 실행하고 디버그 포트 번호를 반환한다."""
        debug_cmd = f'"{config.SDB_PATH}" shell 0 debug {self.app_id}'
        res = _run(debug_cmd, timeout=15, label="debug")
        stdout = (res.stdout or "").strip() if res else ""
        stderr = (res.stderr or "").strip() if res else ""
        print(f"[TV] debug stdout: {stdout}")
        if stderr:
            print(f"[TV] debug stderr: {stderr}")

        match = re.search(r"port:\s*(\d+)", stdout, re.IGNORECASE)
        if not match:
            raise RuntimeError(
                f"디버그 포트를 추출하지 못했습니다.\n명령: {debug_cmd}\n"
                f"stdout: {stdout}\nstderr: {stderr}\n"
                "-> 앱이 디버그 서명된 빌드인지, 개발자 모드가 켜져 있는지 확인하세요."
            )
        return int(match.group(1))

    def forward_port(self, port: int):
        res = _run(f'"{config.SDB_PATH}" forward tcp:{port} tcp:{port}', timeout=10, label="forward tcp")
        if res is None:
            raise RuntimeError(f"포트 포워딩(tcp:{port})이 타임아웃되어 실패했습니다.")
        print(f"[TV] forward: {res.stdout.strip()}")


    def get_existing_debug_port(self) -> int | None:
        """현재 이미 포워딩되어 활성화된 CDP 디버그 포트가 있으면 포트 번호 반환, 없으면 None"""
        import requests
        res = _run(f'"{config.SDB_PATH}" forward --list', timeout=5, label="forward list")
        if not res or not res.stdout:
            return None
        
        # 'tcp:XXXXX tcp:YYYYY' 패턴 추출
        matches = re.findall(r"tcp:(\d+)\s+tcp:(\d+)", res.stdout)
        for local_port_str, _ in matches:
            port = int(local_port_str)
            try:
                r = requests.get(f"http://localhost:{port}/json", timeout=2)
                if r.status_code == 200 and isinstance(r.json(), list):
                    print(f"[TV] 이미 열려있는 디버그 포트 재사용: {port}")
                    return port
            except Exception:
                continue
        return None

    def restart_app_in_debug_mode(self, reuse_if_running: bool = True) -> int:
        """
        reuse_if_running=True일 경우 이미 켜져있는 디버그 포트가 있으면 앱 재시작 없이 즉시 포트 반환.
        없을 경우에만 TV 연결 -> 기존 앱 종료 -> 디버그 모드 새로 실행.
        """
        if reuse_if_running:
            existing_port = self.get_existing_debug_port()
            if existing_port:
                print(f"[TV] 0초 만에 기존 디버그 포트({existing_port})로 바인딩합니다.")
                return existing_port

        self.connect()
        self.reset_forwarding()
        self.stop_app()
        port = self.launch_debug()
        self.forward_port(port)
        time.sleep(2.0)
        return port

