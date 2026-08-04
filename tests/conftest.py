"""
conftest.py
- Factory 패턴 적용으로 Tizen/LG 무관하게 동적 실행 지원
- 녹화(Screencast) 및 실패 시 스크린샷 캡처
"""
import base64
import concurrent.futures
import os
import time
from datetime import datetime

import cv2
import numpy as np
import pytest

from config import config
from core.driver import SoopDriver
from core.controller_factory import get_tv_controller

os.makedirs(config.VIDEO_DIR, exist_ok=True)
os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)

_global_recorder = None

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

@pytest.fixture(scope="session")
def driver():
    controller = get_tv_controller()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(controller.restart_app_in_debug_mode, reuse_if_running=True)
        try:
            port = future.result(timeout=config.SETUP_TIMEOUT_SEC)
        except concurrent.futures.TimeoutError:
            pytest.fail(f"TV 연결/앱 실행 준비 {config.SETUP_TIMEOUT_SEC}초 초과 실패.")

    d = SoopDriver(port)
    try:
        yield d
    finally:
        # 테스트 완료 후 소켓 및 백그라운드 스레드 정리
        d.close()

def _soft_reset_to_home(driver):
    try:
        driver.cdp.evaluate("window.location.reload();")
        # 리로드 후 홈 화면 h2가 나타날 때까지 대기 (요소 실제 렌더링 확인)
        deadline = time.time() + 8
        while time.time() < deadline:
            time.sleep(0.5)
            try:
                val = driver.cdp.evaluate(
                    '(function(){'
                    'var el = document.evaluate("//h2[normalize-space()=\'홈\']",'
                    ' document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;'
                    'return el ? el.textContent : null;'
                    '})()'
                )
                if val:
                    break
            except Exception:
                pass
        # 세션 복원(local storage → 니켌네임 버튼 갱신)이 완료될 때까지 추가 대기
        time.sleep(2)
    except Exception as e:
        print(f"[SOFT RESET WARN] {e}")
        time.sleep(3)  # 실패 시 fallback

@pytest.fixture(autouse=True)
def reset_to_home_between_tests(driver):
    _soft_reset_to_home(driver)
    yield
    _soft_reset_to_home(driver)

class ScreencastRecorder:
    def __init__(self, cdp, video_path, width, height, fps=10):
        self.cdp = cdp
        self.width = max(int(width) or 1920, 2)
        self.height = max(int(height) or 1080, 2)
        self.last_frame = None
        self.frame_count = 0
        self._handler = self._on_frame
        fourcc = cv2.VideoWriter_fourcc(*"MJPG")
        self.writer = cv2.VideoWriter(video_path, fourcc, fps, (self.width, self.height))

    def _on_frame(self, params):
        try:
            data = base64.b64decode(params["data"])
            arr = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is not None:
                img = cv2.resize(img, (self.width, self.height))
                self.writer.write(img)
                self.last_frame = img
                self.frame_count += 1
        except Exception:
            pass
        finally:
            try:
                self.cdp.send_async("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
            except Exception:
                pass

    def start(self):
        self.cdp.on_event("Page.screencastFrame", self._handler)
        self.cdp.send(
            "Page.startScreencast",
            {"format": "jpeg", "quality": 80, "maxWidth": self.width, "maxHeight": self.height, "everyNthFrame": 1},
        )

    def stop(self):
        self.cdp.off_event("Page.screencastFrame", self._handler)
        try:
            self.cdp.send("Page.stopScreencast")
        except Exception:
            pass
        time.sleep(0.3)
        self.writer.release()

@pytest.fixture(scope="session", autouse=True)
def record_full_session(driver):
    global _global_recorder
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(config.VIDEO_DIR, f"full_session_{ts}.avi")
    _global_recorder = ScreencastRecorder(driver.cdp, video_path, 1920, 1080)
    try:
        _global_recorder.start()
        print(f"\n[녹화 시작] -> {video_path}")
    except Exception as e:
        print(f"[VIDEO ERROR] {e}")

    yield

    if _global_recorder:
        _global_recorder.stop()
        print(f"\n[녹화 완료] -> {video_path}")

@pytest.fixture(autouse=True)
def handle_test_report(request, driver):
    test_name = request.node.name
    print(f"\n[TEST START] {test_name}")
    yield
    failed = any(
        getattr(request.node, phase, None) and getattr(request.node, phase).failed
        for phase in ("rep_setup", "rep_call", "rep_teardown")
    )
    if failed:
        print(f"[TEST FAILED] {test_name}")
        if _global_recorder and _global_recorder.last_frame is not None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = test_name.replace("/", "_")
            fail_path = os.path.join(config.SCREENSHOT_DIR, f"FAIL_{safe_name}_{ts}.png")
            cv2.imwrite(fail_path, _global_recorder.last_frame)
            print(f"[FAIL SCREENSHOT] -> {fail_path}")
    else:
        print(f"[TEST PASSED] {test_name}")

def pytest_sessionfinish(session, exitstatus):
    """모든 테스트 세션이 종료되면 잔여 자식 프로세스/스레드를 깔끔하게 정리"""
    import gc
    gc.collect()
    print("\n[SESSION FINISHED] 모든 자원 해제 완료.")

        