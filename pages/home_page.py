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

    # ==== is_loaded ====
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.HOME_LABEL, timeout=timeout)

    def home_label_text(self) -> str:
        return self.driver.text_of(self.HOME_LABEL)

    # ==== 로그인 상태 확인 ====
    def is_logged_in(self, timeout: float = 15) -> bool:
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            text = self.driver.text_of(self.BTN_LOGIN)
            if text and text.strip() != '로그인':
                return True
            if not self.driver.is_visible(self.BTN_LOGIN, timeout=1):
                return True
            time.sleep(0.5)
        return False

    def is_login_button_visible(self, timeout: float = 3) -> bool:
        return self.driver.is_visible(self.BTN_LOGIN, timeout=timeout)

    def is_logged_out(self, timeout: float = 5) -> bool:
        import time
        deadline = time.time() + timeout
        while time.time() < deadline:
            text = self.driver.text_of(self.BTN_LOGIN, timeout=1)
            if text.strip() == '로그인':
                return True
            time.sleep(0.3)
        return False

    # ==== 사이드바 메뉴 클릭 헬퍼 (방향키 기반) ====
    def _click_sidebar_menu(self, target_text: str) -> bool:
        import time
        # 1. 왼쪽 방향키로 사이드바 영역 진입 시도
        for _ in range(3):
            self.driver.press_left()
            time.sleep(0.5)
            
            focused_text = self.driver.cdp.evaluate("document.activeElement ? document.activeElement.textContent : ''")
            if focused_text and any(m in focused_text for m in ["로그인", "검색", "홈", "LIVE", "VOD", "e스포츠", "MY", "설정"]):
                break
                
        menu_order = ["로그인", "검색", "홈", "LIVE", "VOD", "e스포츠", "MY", "설정"]
        
        # 2. 위아래 방향키로 타겟 메뉴 찾기
        for _ in range(15):
            focused_text = self.driver.cdp.evaluate("document.activeElement ? document.activeElement.textContent : ''")
            if not focused_text:
                focused_text = ""
                
            if target_text == focused_text.strip():
                self.driver.press_enter()
                time.sleep(1)
                return True
                
            current_idx = -1
            target_idx = menu_order.index(target_text) if target_text in menu_order else -1
            
            for i, m in enumerate(menu_order):
                if m == focused_text.strip():
                    current_idx = i
                    break
                    
            if current_idx == -1:
                # 사이드바 요소가 아니면 무조건 Down 해봄
                self.driver.press_down()
            elif current_idx < target_idx:
                self.driver.press_down()
            else:
                self.driver.press_up()
                
            time.sleep(0.5)
            
        return False

    def click_login(self) -> bool:
        return self._click_sidebar_menu("로그인")

    def click_live_menu(self) -> bool:
        return self._click_sidebar_menu("LIVE")

    def click_vod_menu(self) -> bool:
        return self._click_sidebar_menu("VOD")

    def click_esports_menu(self) -> bool:
        return self._click_sidebar_menu("e스포츠")

    def click_my_menu(self) -> bool:
        return self._click_sidebar_menu("MY")

    def click_settings_menu(self) -> bool:
        return self._click_sidebar_menu("설정")

    def click_fourth_top_menu(self) -> bool:
        return self._click_sidebar_menu("LIVE")

    def click_search(self) -> bool:
        return self._click_sidebar_menu("검색")

    def open_search(self):
        self.click_search()
        from pages.search_page import SearchPage
        search = SearchPage(self.driver)
        search.wait_until_loaded(timeout=10)
        return search

    # ==== 섹션 표시 여부 ====
    def is_live_section_visible(self) -> bool:
        return self.driver.is_visible(self.LIVE_SECTION_TITLE)

    def is_user_clip_section_visible(self) -> bool:
        return self.driver.is_visible(self.USER_CLIP_SECTION_TITLE)

    def is_upload_vod_section_visible(self) -> bool:
        return bool(self.driver.find(self.UPLOAD_VOD_SECTION_TITLE, scroll_into_view=True))

    def is_replay_section_visible(self) -> bool:
        return bool(self.driver.find(self.REPLAY_SECTION_TITLE, scroll_into_view=True))

    # ==== 더보기 버튼 ====
    def click_live_more(self) -> bool:
        return self.driver.click(self.BTN_LIVE_MORE)

    def click_clip_more(self) -> bool:
        return self.driver.click(self.BTN_CLIP_MORE)

    def click_vod_more(self) -> bool:
        return self.driver.click(self.BTN_VOD_MORE)

    def click_replay_more(self) -> bool:
        return self.driver.click(self.BTN_REPLAY_MORE)

    # ==== 방송 탐색 헬퍼 (POM) ====
    def find_and_enter_broadcast(self, target_title: str, max_attempts: int = 15) -> bool:
        """홈 화면에서 리모컨 우측 방향키로 포커스를 이동시키며 지정된 방송을 찾아 엔터 진입"""
        import time
        for _ in range(max_attempts):
            html = self.driver.cdp.evaluate("document.activeElement.outerHTML") or ""
            if target_title in html:
                self.driver.press_enter()
                return True
            self.driver.press_right()
            time.sleep(1.0)
        return False