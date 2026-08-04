"""
login_page.py
- SOOP TV 로그인 화면 Page Object
- XPath: 실제 DOM 탐색으로 확인한 구조 기반

[로그인 화면 진입 흐름]
  1. 홈 상단 '로그인' 버튼 포커스 + Enter → QR코드 로그인 모달
  2. 'ID/PW로 로그인' 버튼 클릭 → ID/PW 입력 화면
  3. 아이디/비밀번호 입력 → '로그인' 버튼 클릭

[QR 로그인, 인증번호 로그인은 자동화 X]
"""
from pages.base_page import BasePage


class LoginPage(BasePage):
    # ---- QR 로그인 화면 (진입 시 첫 화면) ----
    BTN_QR_COMPLETE      = '//button[normalize-space()="QR코드 스캔 후 완료"]'
    BTN_AUTH_NUMBER      = '//button[normalize-space()="인증번호 로그인"]'
    BTN_ID_PW_LOGIN      = '//button[normalize-space()="ID/PW로 로그인"]'

    # ---- ID/PW 입력 화면 ----
    ID_INPUT             = '//input[@placeholder="아이디"]'
    PW_INPUT             = '//input[@placeholder="비밀번호"]'
    BTN_LOGIN_SUBMIT     = '//button[normalize-space()="로그인" and not(contains(@class,"fNmhpX"))]'
    BTN_OTHER_LOGIN      = '//button[normalize-space()="다른 방식으로 로그인"]'

    def is_qr_screen_loaded(self, timeout: float = 10) -> bool:
        """QR 로그인 모달이 뜬 상태인지 확인"""
        return self.driver.is_visible(self.BTN_ID_PW_LOGIN, timeout=timeout)

    def is_loaded(self, timeout: float = 10) -> bool:
        """ID/PW 입력 화면 진입 여부 확인"""
        return self.driver.is_visible(self.ID_INPUT, timeout=timeout)

    def go_to_id_pw_login(self) -> bool:
        """QR 화면에서 ID/PW 로그인 화면으로 전환"""
        return self.driver.click(self.BTN_ID_PW_LOGIN)

    def enter_id(self, user_id: str):
        self.driver.type_text(self.ID_INPUT, user_id)

    def enter_pw(self, password: str):
        self.driver.type_text(self.PW_INPUT, password)

    def submit(self) -> bool:
        return self.driver.click(self.BTN_LOGIN_SUBMIT)

    def login(self, user_id: str, password: str) -> bool:
        """QR 화면 → ID/PW 화면 → 로그인 완료까지 한번에"""
        self.go_to_id_pw_login()
        if not self.is_loaded(timeout=5):
            return False
        self.enter_id(user_id)
        self.enter_pw(password)
        return self.submit()
