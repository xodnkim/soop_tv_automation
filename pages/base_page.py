"""
base_page.py
- Page Object 공통 상위 클래스
"""
class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def is_loaded(self, timeout: float = 10) -> bool:
        raise NotImplementedError

    def wait_until_loaded(self, timeout: float = 10) -> bool:
        return self.is_loaded(timeout=timeout)