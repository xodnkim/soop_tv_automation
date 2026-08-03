"""
config.py
- TV / 환경별 설정값 통합 관리
- TV_TYPE ("tizen" | "lg") 환경변수에 따라 타깃 플랫폼 전환
"""
import os

# ----- 타깃 플랫폼 선택 ("lg" 또는 "tizen") -----
TV_TYPE = os.environ.get("TV_TYPE", "lg").lower()

# ----- 삼성 Tizen 설정 -----
TIZEN_IP = os.environ.get("SOOP_TV_IP", "192.168.137.192")
TIZEN_APP_ID = os.environ.get("SOOP_APP_ID", "SYhkcwoXQo.SOOPSTG")
SDB_PORT = 26101
SDB_PATH = os.environ.get("SDB_PATH", r"D:\smarttv_auto\tools\sdb.exe")

# ----- LG webOS 설정 -----
LG_DEVICE_NAME = os.environ.get("LG_DEVICE_NAME", "LG_SMART")
LG_APP_ID = os.environ.get("LG_APP_ID", "com.soop.stg.app")

# ----- 타임아웃 -----
SUBPROCESS_TIMEOUT_SEC = 10
SETUP_TIMEOUT_SEC = int(os.environ.get("SOOP_SETUP_TIMEOUT", 60))
ELEMENT_WAIT_TIMEOUT = 10

# ----- 출력 경로 -----
OUTPUT_DIR = "test_results"
VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")
SCREENSHOT_DIR = os.path.join(OUTPUT_DIR, "screenshots")