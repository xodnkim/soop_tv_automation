"""
settings_page.py
- SOOP TV 설정 화면 Page Object
"""
import time
from pages.base_page import BasePage


class SettingsPage(BasePage):
    SETTINGS_LABEL          = '//h2[normalize-space()="설정"]'
    BTN_PREVIEW_SETTING     = '//button[normalize-space()="미리보기 설정"]'
    BTN_PREVIEW_ON          = '//button[normalize-space()="ON"]'
    BTN_PREVIEW_OFF         = '//button[normalize-space()="OFF"]'
    BTN_MOBILE_APP          = '//button[normalize-space()="모바일 앱"]'
    BTN_TERMS               = '//button[normalize-space()="이용약관"]'
    BTN_SUPPORT             = '//button[normalize-space()="고객센터"]'
    BTN_OPENSOURCE          = '//button[normalize-space()="오픈소스 정보"]'
    BTN_APP_INFO            = '//button[normalize-space()="앱 정보"]'
    QR_CODE                 = '//img[contains(@alt,"Android") or contains(@alt,"iOS") or contains(@src,"aos") or contains(@src,"ios")]'
    APP_VERSION             = '//*[contains(normalize-space(),"버전") or contains(normalize-space(),"v1.")]'

    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.SETTINGS_LABEL, timeout=timeout)

    def is_preview_setting_focused(self) -> bool:
        js = """
        (function(){
            var el = document.activeElement;
            return el && el.textContent && el.textContent.trim().indexOf("미리보기 설정") !== -1;
        })()
        """
        try:
            return bool(self.driver.cdp.evaluate(js))
        except Exception:
            return False

    def are_on_off_buttons_visible(self) -> bool:
        return self.driver.is_visible(self.BTN_PREVIEW_ON, timeout=2) and \
               self.driver.is_visible(self.BTN_PREVIEW_OFF, timeout=2)

    def click_preview_setting(self) -> bool:
        return self.driver.click(self.BTN_PREVIEW_SETTING)

    def click_off(self) -> bool:
        return self.driver.click(self.BTN_PREVIEW_OFF)

    def click_on(self) -> bool:
        return self.driver.click(self.BTN_PREVIEW_ON)

    def is_off_checked(self) -> bool:
        js = """
        (function(){
            var el = document.evaluate('//button[normalize-space()="OFF"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if(!el) return false;
            // 체크 상태 확인 (aria-checked나 class 기준 추정)
            return el.className.indexOf('checked') !== -1 || el.getAttribute('aria-checked') === 'true' || el.querySelector('svg');
        })()
        """
        try:
            return bool(self.driver.cdp.evaluate(js))
        except Exception:
            return False

    def focus_mobile_app(self) -> bool:
        return self.driver.click(self.BTN_MOBILE_APP)

    def is_qr_visible(self) -> bool:
        return self.driver.is_visible(self.QR_CODE, timeout=5)

    def focus_terms(self) -> bool:
        return self.driver.click(self.BTN_TERMS)

    def focus_support(self) -> bool:
        return self.driver.click(self.BTN_SUPPORT)

    def focus_opensource(self) -> bool:
        return self.driver.click(self.BTN_OPENSOURCE)

    def click_opensource(self) -> bool:
        return self.driver.click(self.BTN_OPENSOURCE)

    def focus_app_info(self) -> bool:
        return self.driver.click(self.BTN_APP_INFO)

    def is_version_visible(self) -> bool:
        return self.driver.is_visible(self.APP_VERSION, timeout=5)
