"""
config.py
- 환경별로 바뀔 수 있는 값들을 한 곳에 모아둔다 (TV IP, 앱 ID, 타임아웃 등).
- 환경변수로 오버라이드 가능 -> CI에서 TV가 바뀌어도 코드 수정 없이 실행 가능.
"""
import os

# ----- TV / 앱 -----
TV_IP = os.environ.get("SOOP_TV_IP", "192.168.137.192")
APP_ID = os.environ.get("SOOP_APP_ID", "SYhkcwoXQo.SOOPSTG")
SDB_PORT = 26101
SDB_PATH = os.environ.get("SDB_PATH", r"D:\smarttv_auto\tools\sdb.exe")

# ----- 타임아웃 -----
SUBPROCESS_TIMEOUT_SEC = 10       # 개별 sdb 명령 타임아웃
SETUP_TIMEOUT_SEC = int(os.environ.get("SOOP_SETUP_TIMEOUT", 60))  # 세션 준비 전체 타임아웃
ELEMENT_WAIT_TIMEOUT = 10         # 요소 탐색 대기 타임아웃 (초)

# ----- 출력 경로 -----
OUTPUT_DIR = "test_results"
VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")
SCREENSHOT_DIR = os.path.join(OUTPUT_DIR, "screenshots")
