"""
search_page.py
- 검색 화면의 locator와 동작을 캡슐화.
"""
from pages.base_page import BasePage


class SearchPage(BasePage):
    # ----- Locators -----
    SEARCH_INPUT = '//input[@placeholder="검색어"]'
    SEARCH_INPUT_ALT = '//*[@id="root"]/main/div/div[2]/div/div/div/div/div/div[1]/div/div/input'
    RESULT_AREA = '//*[@id="root"]/main/div/div[2]/div/div/div/div/div/div[2]/div'
    RECENT_SEARCH_CONTAINER = '//*[@id="root"]/main/div[2]/div[2]/div/div/div/div[2]/div'

    # ----- Actions / Assertions -----
    def is_loaded(self, timeout: float = 10) -> bool:
        if self.driver.is_visible(self.SEARCH_INPUT, timeout=timeout):
            return True
        return self.driver.is_visible(self.SEARCH_INPUT_ALT, timeout=2)

    def search(self, keyword: str) -> "SearchPage":
        """검색어 입력 후 리모컨 확인(Enter)으로 제출"""
        target_input = self.SEARCH_INPUT if self.driver.is_visible(self.SEARCH_INPUT, timeout=5) else self.SEARCH_INPUT_ALT
        self.driver.type_text(target_input, keyword)
        self.driver.press_enter()
        return self

    def result_text(self) -> str:
        return self.driver.text_of(self.RESULT_AREA)

    def has_result_containing(self, keyword: str) -> bool:
        return keyword in self.result_text()

    def has_recent_keyword(self, keyword: str, timeout: float = 10.0) -> bool:
        """최근 검색어 영역(사용자 지정 Container) 내부에서 키워드 존재 여부 검증 (스마트 대기)"""
        # 1. 사용자 지정 최근 검색어 영역 내부 스마트 탐색
        xpath_inside = f'{self.RECENT_SEARCH_CONTAINER}//*[contains(text(), "{keyword}")]'
        if self.driver.is_visible(xpath_inside, timeout=timeout):
            return True
        
        # 2. 지정 컨테이너 텍스트 검사
        container_text = self.driver.text_of(self.RECENT_SEARCH_CONTAINER, timeout=2)
        if keyword in container_text:
            return True

        # 3. 문서 전체 텍스트 fallback 검사
        xpath_global = f'//*[contains(text(), "{keyword}")]'
        return self.driver.is_visible(xpath_global, timeout=2)
