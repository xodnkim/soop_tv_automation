"""
base_page.py
- 모든 Page Object가 상속받는 공통 부모.
"""


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def is_loaded(self, timeout: float = 10) -> bool:
        """각 페이지에서 구현: 대표 요소가 보이면 True"""
        raise NotImplementedError

    def wait_until_loaded(self, timeout: float = 10) -> bool:
        """페이지 렌더링이 완료될 때까지 스마트 대기"""
        return self.is_loaded(timeout=timeout)
