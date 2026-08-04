"""
test_login.py
- SOOP TV 로그인 / 로그아웃 자동화 테스트 케이스
- TC 대상: Android TV 기본 기능 > 로그인 > LNB > 앱 내부 로그인

[로그인 화면 진입 흐름 - 실제 DOM 기반]
  홈 '로그인' 버튼 포커스+Enter → QR코드 모달 → 'ID/PW로 로그인' 클릭 → ID/PW 입력

[자동화 제외 항목]
  - QR코드 로그인 (스마트폰 필요)
  - 인증번호 로그인 (외부 기기 필요)
  - SNS 연동 로그인
"""
import pytest
from pages.home_page import HomePage
from pages.login_page import LoginPage

TEST_ID = "xodn9900"
TEST_PW = "dkvmflzk12!"


class TestLoginFlow:
    """[Depth1: 로그인] [Depth2: LNB] 앱 로그인 전체 흐름"""

    def test_login_button_visible(self, driver):
        """TC: 로그인 전 상태에서 상단 '로그인' 버튼 노온 확인"""
        home = HomePage(driver)
        if not home.is_logged_out():
            pytest.skip("이미 로그인된 상태입니다")
        assert home.is_login_button_visible(), "상단 로그인 버튼이 보이지 않습니다"

    def test_login_button_opens_qr_screen(self, driver):
        """TC: '로그인' 버튼 클릭 시 QR코드 로그인 모달 진입 확인"""
        home = HomePage(driver)
        if not home.is_logged_out(timeout=5):
            pytest.skip("이미 로그인된 상태입니다")
        home.click_login()
        login = LoginPage(driver)
        assert login.is_qr_screen_loaded(timeout=10), "QR 로그인 화면으로 전환되지 않았습니다"

    def test_id_pw_login_button_visible_on_qr_screen(self, driver):
        """TC: QR 로그인 화면에 'ID/PW로 로그인' 버튼 노출 확인"""
        home = HomePage(driver)
        login = LoginPage(driver)
        if not login.is_qr_screen_loaded(timeout=3):
            if not home.is_login_button_visible():
                pytest.skip("이미 로그인된 상태입니다")
            home.click_login()
        assert login.is_qr_screen_loaded(timeout=10), "QR 화면이 아닙니다"
        assert driver.is_visible(login.BTN_ID_PW_LOGIN), "'ID/PW로 로그인' 버튼이 보이지 않습니다"

    def test_navigate_to_id_pw_login_screen(self, driver):
        """TC: 'ID/PW로 로그인' 클릭 시 아이디/비밀번호 입력 화면 진입 확인"""
        home = HomePage(driver)
        login = LoginPage(driver)
        if not login.is_qr_screen_loaded(timeout=3):
            if not home.is_login_button_visible():
                pytest.skip("이미 로그인된 상태입니다")
            home.click_login()
        login.go_to_id_pw_login()
        assert login.is_loaded(timeout=10), "ID/PW 입력 화면으로 전환되지 않았습니다"

    def test_id_input_visible(self, driver):
        """TC: ID/PW 입력 화면에 아이디 입력 필드 노출 확인"""
        home = HomePage(driver)
        login = LoginPage(driver)
        if not login.is_loaded(timeout=3):
            if not home.is_login_button_visible():
                pytest.skip("이미 로그인된 상태입니다")
            home.click_login()
            login.go_to_id_pw_login()
        assert login.is_loaded(timeout=10), "ID/PW 입력 화면 없음"
        assert driver.is_visible(login.ID_INPUT), "아이디 입력 필드가 보이지 않습니다"
        assert driver.is_visible(login.PW_INPUT), "비밀번호 입력 필드가 보이지 않습니다"

    def test_login_with_valid_credentials(self, driver):
        """TC: 올바른 ID/PW로 로그인 성공 확인 (상단 버튼이 닉네임으로 변경)"""
        home = HomePage(driver)
        if not home.is_logged_out(timeout=5):
            pytest.skip("이미 로그인된 상태입니다")
        home.click_login()
        login = LoginPage(driver)
        assert login.is_qr_screen_loaded(timeout=10), "QR 화면 진입 실패"
        result = login.login(TEST_ID, TEST_PW)
        assert result, "로그인 버튼 제출 실패"
        # 로그인 성공 확인: 상단 버튼 텍스트가 '로그인'에서 닉네임으로 변경됨
        assert home.is_logged_in(timeout=20), "로그인 실패 (상단 버튼이 닉네임으로 변경되지 않음)"


class TestLogoutFlow:
    """[Depth1: 로그인] [Depth2: LNB] 로그아웃 흐름"""

    def test_logout_from_profile_popup(self, driver):
        """TC: 상단 프로필 이미지 클릭 → 로그아웃 버튼 노출 확인"""
        from pages.my_page import MyPage
        home = HomePage(driver)
        if home.is_logged_out():
            pytest.skip("로그인되지 않은 상태 — 먼저 로그인 필요")
        my = MyPage(driver)
        # 상단 프로필 버튼 클릭
        my.open_profile_popup()
        assert driver.is_visible(my.BTN_LOGOUT, timeout=10), "프로필 팝업에 로그아웃 버튼이 보이지 않습니다"

    def test_logout_completes(self, driver):
        """TC: 상단 프로필 클릭 → 로그아웃 클릭 → '로그인' 버튼 재노출 확인"""
        from pages.my_page import MyPage
        home = HomePage(driver)
        if home.is_logged_out(timeout=5):
            pytest.skip("로그인되지 않은 상태")
        my = MyPage(driver)
        assert my.logout(), "로그아웃 실패"
        # 로그아웃 자체에 애니메이션 시간 추가 후 '로그인' 버튼 재노출 확인
        assert home.is_logged_out(timeout=15), "로그아웃 후 '로그인' 버튼이 다시 노출되지 않습니다"
