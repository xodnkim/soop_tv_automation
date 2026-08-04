"""
my_page.py
- SOOP TV MY 탭 및 프로필 팝업 Page Object
- 로그아웃: 상단 프로필 버튼(닉네임) 클릭 → 로그아웃 버튼 클릭
"""
from pages.base_page import BasePage


class MyPage(BasePage):
    # ---- MY 탭 ----
    MY_LABEL              = '//h2[normalize-space()="MY"]'
    FAVORITE_SECTION      = '//h3[contains(., "즐겨찾기")]'
    SUBSCRIBED_VOD_SECTION= '//h3[normalize-space()="구독한 스트리머의 VOD"]'

    # ---- 프로필 팝업 (프로필 버튼 클릭 후 노출) ----
    BTN_PROFILE           = '(//button[contains(@class,"fNmhpX")])[1]'  # 상단 왼쪽 첫 번째 버튼
    BTN_LOGOUT            = '//button[normalize-space()="로그아웃"]'

    # ---- 로그아웃 확인 팝업 ('로그아웃 하시겠습니까?' 대화상자) ----
    LOGOUT_CONFIRM_TITLE  = '//*[contains(.,"로그아웃 하시겠습니까")]'
    BTN_LOGOUT_CANCEL     = '//button[normalize-space()="취소"]'
    BTN_LOGOUT_CONFIRM    = '//button[normalize-space()="확인"]'

    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.MY_LABEL, timeout=timeout)

    def open_profile_popup(self) -> bool:
        """상단 프로필(닉네임) 버튼 클릭 → 로그아웃 팝업 노출"""
        return self.driver.click(self.BTN_PROFILE)

    def click_logout(self) -> bool:
        """프로필 팝업에서 로그아웃 버튼 클릭"""
        return self.driver.click(self.BTN_LOGOUT)

    def logout(self) -> bool:
        """프로필 팝업 열기 → 로그아웃 클릭 → 확인 버튼 클릭"""
        self.open_profile_popup()
        if not self.driver.is_visible(self.BTN_LOGOUT, timeout=5):
            return False
        self.click_logout()
        # 확인 팝업이 뜨면 '확인' 클릭
        if self.driver.is_visible(self.BTN_LOGOUT_CONFIRM, timeout=5):
            return self.driver.click(self.BTN_LOGOUT_CONFIRM)
        return True
