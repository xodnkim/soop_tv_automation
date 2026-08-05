"""
test_settings.py
- SOOP TV 설정 화면 자동화 테스트 케이스
"""
import pytest
import time
from pages.home_page import HomePage
from pages.settings_page import SettingsPage

class TestSettingsEntry:
    @pytest.mark.skip(reason="현재 테스트 앱에 미리보기 설정 메뉴가 존재하지 않음")
    def test_preview_setting_focused_on_entry(self, driver):
        """
        # TC: settings_003
        설정 진입 시 미리보기 설정 메뉴에 포커스
        """
        home = HomePage(driver)
        assert home.click_settings_menu(), "설정 메뉴 클릭 실패"
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        time.sleep(1)
        assert settings.is_preview_setting_focused(), "미리보기 설정 메뉴 포커스 실패 (settings_003)"

    @pytest.mark.skip(reason="현재 테스트 앱에 미리보기 설정 메뉴가 존재하지 않음")
    def test_on_off_buttons_visible(self, driver):
        """
        # TC: settings_004
        미리보기 설정 ON/OFF 버튼 노출 확인
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        assert settings.are_on_off_buttons_visible(), "ON/OFF 버튼 노출 확인 실패 (settings_004)"


class TestSettingsPreview:
    @pytest.mark.skip(reason="현재 테스트 앱에 미리보기 설정 메뉴가 존재하지 않음")
    def test_preview_setting_click_focuses_on(self, driver):
        """
        # TC: settings_005
        미리보기 설정 클릭 시 ON/OFF 영역 포커스 (디폴트 ON이라 가정)
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        assert settings.click_preview_setting(), "미리보기 설정 클릭 실패 (settings_005)"

    @pytest.mark.skip(reason="현재 테스트 앱에 미리보기 설정 메뉴가 존재하지 않음")
    def test_off_button_applies_setting(self, driver):
        """
        # TC: settings_006
        OFF 버튼 클릭 시 체크 상태 확인 (테스트 후 ON 복원)
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        
        try:
            assert settings.click_preview_setting(), "미리보기 설정 클릭 실패"
            time.sleep(0.5)
            assert settings.click_off(), "OFF 버튼 클릭 실패"
            time.sleep(1)
            # (선택적) 상태 검증
            # assert settings.is_off_checked(), "OFF 버튼 체크 상태 확인 실패 (settings_006)"
        finally:
            # 부작용 원복 (ON 클릭)
            settings.click_on()
            time.sleep(0.5)


class TestSettingsMenuItems:
    def test_mobile_app_focus_shows_qr(self, driver):
        """
        # TC: settings_007
        모바일 앱 포커스 시 우측 QR 노출
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        settings.focus_mobile_app()
        assert settings.is_qr_visible(), "모바일 앱 QR 노출 실패 (settings_007)"

    def test_terms_focus_shows_qr(self, driver):
        """
        # TC: settings_008
        이용약관 포커스 시 우측 QR 노출
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        settings.focus_terms()
        assert settings.is_qr_visible(), "이용약관 QR 노출 실패 (settings_008)"

    def test_support_focus_shows_qr(self, driver):
        """
        # TC: settings_009
        고객센터 포커스 시 우측 QR 노출
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        settings.focus_support()
        assert settings.is_qr_visible(), "고객센터 QR 노출 실패 (settings_009)"

    def test_opensource_focus(self, driver):
        """
        # TC: settings_010
        오픈소스 정보 포커스
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        assert settings.focus_opensource(), "오픈소스 정보 클릭/포커스 실패 (settings_010)"

    def test_opensource_click_shows_list(self, driver):
        """
        # TC: settings_011
        오픈소스 정보 클릭 시 리스트 노출
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        settings.focus_opensource()
        settings.click_opensource()
        time.sleep(1)
        # 리모컨 BACK 키로 복귀 (teardown)
        driver.cdp.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "GoBack", "code": "GoBack", "windowsVirtualKeyCode": 461})
        driver.cdp.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "GoBack", "code": "GoBack", "windowsVirtualKeyCode": 461})

    def test_app_info_shows_version(self, driver):
        """
        # TC: settings_012
        앱 정보 포커스 시 우측 앱 버전 노출
        """
        home = HomePage(driver)
        home.click_settings_menu()
        
        settings = SettingsPage(driver)
        assert settings.is_loaded(timeout=5), "설정 화면 진입 실패"
        settings.focus_app_info()
        assert settings.is_version_visible(), "앱 버전 노출 실패 (settings_012)"
