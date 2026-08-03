"""
home_page.py
- SOOP 앱 홈 화면의 locator와 동작을 캡슐화.
- 테스트 코드는 xpath를 몰라도 되고, home.is_loaded() 같은 의미 있는 이름만 호출한다.
"""
from pages.base_page import BasePage


class HomePage(BasePage):
    # ----- Locators -----
    HOME_LABEL = '//*[@id="root"]/main/div/div[2]/div/h2'
    LIVE_SECTION_TITLE = '//*[@id="root"]/main/div/div[2]/div/div/div/section[1]/h3'
    USER_CLIP_SECTION_TITLE = '//*[@id="root"]/main/div/div[2]/div/div/div/section[2]/h3'
    UPLOAD_VOD_SECTION_TITLE = '//*[@id="root"]/main/div/div[2]/div/div/div/section[3]/h3'
    TOP_MENU_BUTTON_4 = '//*[@id="root"]/main/div/div[1]/div/div/button[4]'
    SEARCH_ENTRY_BUTTON = '//*[@id="root"]/main/div/div[1]/div/div/button[2]'

    # ----- Actions / Assertions -----
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.HOME_LABEL, timeout=timeout)

    def home_label_text(self) -> str:
        return self.driver.text_of(self.HOME_LABEL)

    def is_live_section_visible(self) -> bool:
        return self.driver.is_visible(self.LIVE_SECTION_TITLE)

    def is_user_clip_section_visible(self) -> bool:
        return self.driver.is_visible(self.USER_CLIP_SECTION_TITLE)

    def is_upload_vod_section_visible(self) -> bool:
        # 화면 하단에 있어 스크롤이 필요한 섹션 -> find()가 내부적으로 scrollIntoView 처리
        return bool(self.driver.find(self.UPLOAD_VOD_SECTION_TITLE, scroll_into_view=True))

    def click_fourth_top_menu(self) -> bool:
        return self.driver.click(self.TOP_MENU_BUTTON_4)

    def open_search(self):
        """검색 화면으로 이동하고 SearchPage 객체를 반환 (페이지 전환 체이닝 + 스마트 대기)"""
        self.driver.click(self.SEARCH_ENTRY_BUTTON)
        from pages.search_page import SearchPage
        search = SearchPage(self.driver)
        search.wait_until_loaded(timeout=10)
        return search

