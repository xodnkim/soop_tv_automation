"""
base_controller.py
- Tizen과 LG 컨트롤러가 반드시 구현해야 하는 공통 추상 클래스
"""
from abc import ABC, abstractmethod

class BaseTVController(ABC):
    @abstractmethod
    def restart_app_in_debug_mode(self, reuse_if_running: bool = True) -> int:
        """
        앱을 디버그 모드로 준비하고 연결 가능한 CDP 포트를 반환한다.
        reuse_if_running=True일 경우 이미 열려있는 디버그 포트가 있으면 즉시 반환.
        """
        pass