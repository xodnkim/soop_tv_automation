"""
conftest.py
- 세션 시작부터 끝까지의 모든 과정을 단 하나의 통으로 연결된 동영상 파일로 저장 (full_session_*.avi)
- 오직 실패(FAIL)한 테스트 케이스에 대해서만 실패 순간의 스크린샷(FAIL_*.png)을 저장
- Windows 콘솔 안전 문자([TEST PASSED], [TEST FAILED])로 리포트 시각화
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
from core.tv_controller import TVController

os.makedirs(config.VIDEO_DIR, exist_ok=True)
os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)

# 녹화기에서 최신 프레임을 공유하기 위해 모듈 전역 보관
_global_recorder = None


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def driver():
    """
    세션 전체에서 한 번만 TV 연결 및 디버그 포트 바인딩.
    이미 디버그 모드로 켜져 있다면 0초 만에 포트 재사용 (Soft Attach).
    """
    controller = TVController()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(controller.restart_app_in_debug_mode, reuse_if_running=True)
        try:
            port = future.result(timeout=config.SETUP_TIMEOUT_SEC)
        except concurrent.futures.TimeoutError:
            pytest.fail(
                f"TV 연결/앱 실행 준비가 {config.SETUP_TIMEOUT_SEC}초 안에 끝나지 않았습니다. "
                "터미널의 [TV] 로그를 보면 어느 단계에서 멈췄는지 확인할 수 있습니다."
            )

    d = SoopDriver(port)
    yield d
    d.close()


def _soft_reset_to_home(driver):
    """프로세스 kill 없이 1.0초 만에 초기 홈 화면으로 페이지 리로드(Soft Reset)"""
    try:
        driver.cdp.evaluate("window.location.reload();")
        time.sleep(1.2)
    except Exception as e:
        print(f"[SOFT RESET WARN] {e}")


@pytest.fixture(autouse=True)
def reset_to_home_between_tests(driver):
    """각 테스트 실행 직전 및 끝난 직후 초기 홈 화면으로 강제 복귀 (독립성 보장)"""
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
        if not self.writer.isOpened():
            print(f"[VIDEO][ERROR] VideoWriter 열기 실패: {video_path}")

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
        except Exception as e:
            print(f"[VIDEO][FRAME ERROR] {e}")
        finally:
            try:
                self.cdp.send_async("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
            except Exception as e:
                print(f"[VIDEO][ACK ERROR] {e}")

    def start(self):
        self.cdp.on_event("Page.screencastFrame", self._handler)
        self.cdp.send(
            "Page.startScreencast",
            {
                "format": "jpeg", "quality": 80,
                "maxWidth": self.width, "maxHeight": self.height,
                "everyNthFrame": 1,
            },
        )

    def stop(self):
        self.cdp.off_event("Page.screencastFrame", self._handler)
        try:
            self.cdp.send("Page.stopScreencast")
        except Exception as e:
            print(f"[VIDEO][STOP ERROR] {e}")
        time.sleep(0.3)
        self.writer.release()
        if self.frame_count == 0:
            print("[VIDEO][WARN] 수신된 프레임이 0개입니다.")


def _viewport(cdp):
    try:
        layout = cdp.send("Page.getLayoutMetrics")
        size = layout.get("cssContentSize") or layout.get("layoutViewport") or {}
        return int(size.get("width", 1920)) or 1920, int(size.get("height", 1080)) or 1080
    except Exception as e:
        print(f"[VIEWPORT][WARN] 뷰포트 조회 실패, 기본값 사용: {e}")
        return 1920, 1080


@pytest.fixture(scope="session", autouse=True)
def record_full_session(driver):
    """테스트 실행 '시작부터 끝까지' 전체 과정을 1개의 통합 동영상으로 녹화"""
    global _global_recorder
    width, height = _viewport(driver.cdp)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(config.VIDEO_DIR, f"full_session_{ts}.avi")

    _global_recorder = ScreencastRecorder(driver.cdp, video_path, width, height)
    try:
        _global_recorder.start()
        print(f"\n[SESSION VIDEO RECORDING START] -> {video_path}")
    except Exception as e:
        print(f"[VIDEO][ERROR] 전체 동영상 녹화 시작 실패: {e}")

    yield

    if _global_recorder:
        _global_recorder.stop()
        print(f"\n[SESSION VIDEO RECORDING FINISHED] 전체 동영상 저장 완료 -> {video_path}")


@pytest.fixture(autouse=True)
def handle_test_report(request, driver):
    """개별 테스트 실행 결과를 명확히 출력하고, '오직 실패한 케이스만' 스크린샷 저장"""
    test_name = request.node.name
    print(f"\n========================================")
    print(f"[TEST RUNNING] {test_name}")
    print(f"========================================")

    yield

    failed = any(
        getattr(request.node, phase, None) and getattr(request.node, phase).failed
        for phase in ("rep_setup", "rep_call", "rep_teardown")
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = test_name.replace("/", "_")

    if failed:
        print(f"[TEST FAILED] {test_name}")
        if _global_recorder and _global_recorder.last_frame is not None:
            fail_path = os.path.join(config.SCREENSHOT_DIR, f"FAIL_{safe_name}_{ts}.png")
            cv2.imwrite(fail_path, _global_recorder.last_frame)
            print(f"[FAIL SCREENSHOT SAVED] -> {fail_path}")
    else:
        print(f"[TEST PASSED] {test_name}")
