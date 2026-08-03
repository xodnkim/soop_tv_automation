"""
search_page.py
- SOOP 앱 검색 화면 Page Object
"""
from pages.base_page import BasePage

class SearchPage(BasePage):
    SEARCH_INPUT = '//input[@placeholder="검색어"]'
    SEARCH_INPUT_ALT = '//*[@id="root"]/main/div/div[2]/div/div/div/div/div/div[1]/div/div/input'
    RESULT_AREA = '//*[@id="root"]/main/div/div[2]/div/div/div/div/div/div[2]/div'
    RECENT_SEARCH_CONTAINER = '//*[@id="root"]/main/div[2]/div[2]/div/div/div/div[2]/div'

    def is_loaded(self, timeout: float = 10) -> bool:
        if self.driver.is_visible(self.SEARCH_INPUT, timeout=timeout):
            return True
        return self.driver.is_visible(self.SEARCH_INPUT_ALT, timeout=2)

    def search(self, keyword: str) -> "SearchPage":
        target_input = self.SEARCH_INPUT if self.driver.is_visible(self.SEARCH_INPUT, timeout=5) else self.SEARCH_INPUT_ALT
        self.driver.type_text(target_input, keyword)
        self.driver.press_enter()
        return self

    def result_text(self) -> str:
        return self.driver.text_of(self.RESULT_AREA)

    def has_recent_keyword(self, keyword: str, timeout: float = 10.0) -> bool:
        xpath_inside = f'{self.RECENT_SEARCH_CONTAINER}//*[contains(text(), "{keyword}")]'
        if self.driver.is_visible(xpath_inside, timeout=timeout):
            return True
        container_text = self.driver.text_of(self.RECENT_SEARCH_CONTAINER, timeout=2)
        if keyword in container_text:
            return True
        xpath_global = f'//*[contains(text(), "{keyword}")]'
        return self.driver.is_visible(xpath_global, timeout=2)