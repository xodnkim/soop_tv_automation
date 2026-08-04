"""
home_page.py
- SOOP TV 홈 화면 Page Object
- XPath: 실제 DOM 탐색으로 추출한 텍스트 기반 안정적인 XPath 사용
"""
from pages.base_page import BasePage


class HomePage(BasePage):
    # ---- 상단 메뉴 버튼 ----
    BTN_LOGIN         = '//button[.="로그인"]'
    BTN_SEARCH        = '//button[.="검색"]'
    BTN_HOME          = '//button[.="홈"]'
    BTN_LIVE          = '//button[.="LIVE"]'
    BTN_VOD           = '//button[.="VOD"]'
    BTN_ESPORTS       = '//button[.="e스포츠"]'
    BTN_MY            = '//button[.="MY"]'
    BTN_SETTINGS      = '//button[.="설정"]'

    # ---- 홈 라벨 / 섹션 타이틀 ----
    HOME_LABEL              = '//h2[normalize-space()="홈"]'
    LIVE_SECTION_TITLE      = '//h3[normalize-space()="인기 LIVE"]'
    USER_CLIP_SECTION_TITLE = '//h3[normalize-space()="인기 유저 클립"]'
    UPLOAD_VOD_SECTION_TITLE= '//h3[normalize-space()="인기 업로드 VOD"]'
    REPLAY_SECTION_TITLE    = '//h3[normalize-space()="인기 다시보기"]'

    # ---- 더보기 버튼 ----
    BTN_LIVE_MORE       = '//button[normalize-space()="인기 LIVE 더보기"]'
    BTN_CLIP_MORE       = '//button[normalize-space()="인기 유저 클립 더보기"]'
    BTN_VOD_MORE        = '//button[normalize-space()="인기 업로드 VOD 더보기"]'
    BTN_REPLAY_MORE     = '//button[normalize-space()="인기 다시보기 더보기"]'

    # ---- 콘텐츠 카드 (각 섹션의 첫 번째 항목) ----
    FIRST_LIVE_CARD     = '(//button[contains(@class,"kGpOLI")])[1]'
    FIRST_CLIP_CARD     = '(//button[normalize-space()="인기 유저 클립 더보기"]//preceding-sibling::button[contains(@class,"kGpOLI")])[last()]'

    # ==== is_loaded ====
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.HOME_LABEL, timeout=timeout)

    def home_label_text(self) -> str:
        return self.driver.text_of(self.HOME_LABEL)

    # ==== 로그인 상태 확인 ====
    def is_logged_in(self, timeout: float = 15) -> bool:
        """로그인 성공 여부: 상단 첫 번째 버튼이 '로그인' 텍스트가 아니면 로그인된 상태"""
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            text = self.driver.text_of(self.BTN_LOGIN)
            if text and text.strip() != '로그인':
                return True
            # '로그인' 버튼 자체가 사라진 경우 (DOM 교체)
            if not self.driver.is_visible(self.BTN_LOGIN, timeout=1):
                return True
            time.sleep(0.5)
        return False

    # ==== 로그인 버튼 여부 ====
    def is_login_button_visible(self, timeout: float = 3) -> bool:
        """로그인 버튼('로그인' 텍스트) 표시 여부 - 짧은 타임아웃으로 상태 빠르게 판단"""
        return self.driver.is_visible(self.BTN_LOGIN, timeout=timeout)

    def is_logged_out(self, timeout: float = 5) -> bool:
        """로그인 버튼이 '로그인' 텍스트인지 확인 (timeout 내에 '로그인' 버튼이 나타나야 True)"""
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            text = self.driver.text_of(self.BTN_LOGIN, timeout=1)
            if text.strip() == '로그인':
                return True
            time.sleep(0.3)
        return False

    def click_login(self) -> bool:
        return self.driver.click(self.BTN_LOGIN)

    # ==== 섹션 표시 여부 ====
    def is_live_section_visible(self) -> bool:
        return self.driver.is_visible(self.LIVE_SECTION_TITLE)

    def is_user_clip_section_visible(self) -> bool:
        return self.driver.is_visible(self.USER_CLIP_SECTION_TITLE)

    def is_upload_vod_section_visible(self) -> bool:
        return bool(self.driver.find(self.UPLOAD_VOD_SECTION_TITLE, scroll_into_view=True))

    def is_replay_section_visible(self) -> bool:
        return bool(self.driver.find(self.REPLAY_SECTION_TITLE, scroll_into_view=True))

    # ==== 메뉴 이동 ====
    def click_live_menu(self) -> bool:
        return self.driver.click(self.BTN_LIVE)

    def click_vod_menu(self) -> bool:
        return self.driver.click(self.BTN_VOD)

    def click_esports_menu(self) -> bool:
        return self.driver.click(self.BTN_ESPORTS)

    def click_my_menu(self) -> bool:
        return self.driver.click(self.BTN_MY)

    def click_settings_menu(self) -> bool:
        return self.driver.click(self.BTN_SETTINGS)

    def click_fourth_top_menu(self) -> bool:
        """4번째 탭 (LIVE) 클릭"""
        return self.driver.click(self.BTN_LIVE)

    # ==== 검색 진입 ====
    def open_search(self):
        self.driver.click(self.BTN_SEARCH)
        from pages.search_page import SearchPage
        search = SearchPage(self.driver)
        search.wait_until_loaded(timeout=10)
        return search

    # ==== 더보기 버튼 ====
    def click_live_more(self) -> bool:
        return self.driver.click(self.BTN_LIVE_MORE)

    def click_clip_more(self) -> bool:
        return self.driver.click(self.BTN_CLIP_MORE)

    def click_vod_more(self) -> bool:
        return self.driver.click(self.BTN_VOD_MORE)

    def click_replay_more(self) -> bool:
        return self.driver.click(self.BTN_REPLAY_MORE)