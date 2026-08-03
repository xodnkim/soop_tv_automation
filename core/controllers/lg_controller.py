"""
lg_controller.py
- LG webOS(ares-cli) TV 제어 담당 (클로드 수정 반영 완료)
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

class LGTVController(BaseTVController):
    def __init__(self, device_name: str = config.LG_DEVICE_NAME, app_id: str = config.LG_APP_ID):
        self.device_name = device_name
        self.app_id = app_id

    def stop_app(self):
        print(f"[LG TV] 앱 종료 시도 ({self.app_id})...")
        _run(f"ares-launch -d {self.device_name} -c {self.app_id}", timeout=10, label="lg stop")
        time.sleep(1.0)

    def launch_and_get_inspect_port(self) -> int:
            print(f"[LG TV] 앱 실행 시도 ({self.app_id})...")
            _run(f"ares-launch -d {self.device_name} {self.app_id}", timeout=15, label="lg launch")
            time.sleep(2.0)

            print(f"[LG TV] 인스펙터 포트 추출 시도...")
            # stdout/stderr를 PIPE로 연결하되 백그라운드로 안전하게 실행
            proc = subprocess.Popen(
                f"ares-inspect -d {self.device_name} {self.app_id}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            port = None
            start_time = time.time()

            while time.time() - start_time < 10:
                line = proc.stdout.readline()
                if line:
                    print(f"[LG TV] inspect log: {line.strip()}")
                    match = re.search(r"(?:port\s*:?\s*|localhost:)(\d+)", line, re.IGNORECASE)
                    if match:
                        port = int(match.group(1))
                        break
                time.sleep(0.1)

            # 포트 얻은 즉시 프로세스 강제 도살 및 스트림 닫기 (터미널 점유 방지)
            try:
                proc.stdout.close()
                proc.terminate()
                proc.kill()
            except Exception:
                pass

            if not port:
                raise RuntimeError("[LG TV] 디버그 포트 추출 실패")

            print(f"[LG TV] 디버그 포트 획득 완료: {port}")
            return port

    def get_existing_debug_port(self) -> int | None:
        """현재 열려있는 포트 세션이 있는지 확인 (CDP 응답 검사)"""
        # 공통 포트 범위나 브라우저 엔드포인트 수신 여부 확인
        try:
            res = _run(f"ares-inspect -d {self.device_name} {self.app_id} --display", timeout=5)
            if res and res.stdout:
                match = re.search(r"(?:port\s*:\s*|localhost:)(\d+)", res.stdout, re.IGNORECASE)
                if match:
                    port = int(match.group(1))
                    r = requests.get(f"http://localhost:{port}/json", timeout=2)
                    if r.status_code == 200:
                        return port
        except Exception:
            pass
        return None

    def restart_app_in_debug_mode(self, reuse_if_running: bool = True) -> int:
        if reuse_if_running:
            existing_port = self.get_existing_debug_port()
            if existing_port:
                print(f"[LG TV] 기존 디버그 포트({existing_port})를 재사용합니다.")
                return existing_port

        self.stop_app()
        port = self.launch_and_get_inspect_port()
        time.sleep(1.5)
        return port