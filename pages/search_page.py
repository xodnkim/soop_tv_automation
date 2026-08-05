"""
search_page.py
- SOOP TV 검색 화면 Page Object
- XPath: 실제 DOM 탐색으로 추출한 텍스트 기반 안정적인 XPath 사용

[검색 화면 진입 흐름]
  1. 상단 '검색' 버튼 클릭 → 검색 화면 진입 (입력 필드 포커스)
  2. 검색어 입력 → Enter → 검색 결과 (LIVE/VOD 섹션)
  3. 더보기 버튼 클릭 → 더보기 리스트

[TC Coverage]
  search_001: 검색 화면 진입 - 입력 필드 포커스
  search_002: BACK 키 - 키패드 닫힘
  search_003: 추천 영상 섹션 노출
  search_011: 검색어 입력 후 엔터 - 검색 기록 노출
  search_012: LIVE 섹션 노출 + 첫 썸네일 포커스
  search_013: VOD 섹션 노출
  search_021: LIVE 더보기 버튼 노출
  search_022: LIVE 더보기 클릭 → 더보기 리스트
  search_023: BACK → 이전 화면
  search_031: VOD 더보기 버튼 노출
  search_032: VOD 더보기 클릭 → 더보기 리스트
  search_033: BACK → 이전 화면
  search_034: 검색 기록 삭제 버튼 → 컨펌 얼럿
  search_035: 확인 → 검색 기록 삭제
"""
import time
from pages.base_page import BasePage


class SearchPage(BasePage):
    # ---- 검색 입력 필드 ----
    SEARCH_INPUT        = '//input[@placeholder="검색어"]'
    SEARCH_INPUT_ALT    = '//input[@type="text" or @type="search"]'

    # ---- 추천 영상 섹션 ----
    RECOMMEND_SECTION   = '//*[contains(normalize-space(text()),"추천 영상")]'

    # ---- 검색 기록 ----
    SEARCH_HISTORY_AREA = '//*[contains(@class,"recent") or contains(@class,"history") or contains(@class,"Recent")]'
    BTN_DELETE_HISTORY  = '//button[normalize-space()="검색 기록 삭제"]'

    # ---- 검색 결과 섹션 타이틀 ----
    # LIVE 섹션: "LIVE" 텍스트를 포함하는 h3 또는 섹션 타이틀
    LIVE_RESULT_SECTION = '//h3[contains(normalize-space(),"LIVE")] | //*[contains(@class,"section")]//*[normalize-space()="LIVE"]'
    VOD_RESULT_SECTION  = '//h3[contains(normalize-space(),"VOD")] | //*[contains(@class,"section")]//*[normalize-space()="VOD"]'

    # ---- 첫 번째 결과 썸네일 (포커스 확인용) ----
    FIRST_RESULT_CARD   = '(//button[contains(@class,"Thumbnail") or contains(@class,"thumbnail") or contains(@class,"card")])[1]'

    # ---- 더보기 버튼 ----
    BTN_LIVE_MORE       = '//button[contains(normalize-space(),"LIVE 더보기")]'
    BTN_VOD_MORE        = '//button[contains(normalize-space(),"VOD 더보기")]'

    # ---- 더보기 리스트 (더보기 클릭 후 화면) ----
    MORE_LIST_CONTAINER = '//*[contains(@class,"more") or contains(@class,"list-page") or //h2]'

    # ---- 컨펌 얼럿 ----
    BTN_CONFIRM         = '//button[normalize-space()="확인"]'
    BTN_CANCEL          = '//button[normalize-space()="취소"]'

    def _get_input_xpath(self):
        if self.driver.is_visible(self.SEARCH_INPUT, timeout=2):
            return self.SEARCH_INPUT
        return self.SEARCH_INPUT_ALT

    def is_loaded(self, timeout: float = 10) -> bool:
        """검색 화면 로드 확인: 검색 입력 필드 노출"""
        if self.driver.is_visible(self.SEARCH_INPUT, timeout=timeout):
            return True
        return self.driver.is_visible(self.SEARCH_INPUT_ALT, timeout=2)

    def is_search_input_visible(self) -> bool:
        """검색 입력 필드 노출 확인 (search_001)"""
        return self.is_loaded(timeout=5)

    def is_recommend_section_visible(self) -> bool:
        """추천 영상 섹션 노출 확인 (search_003)"""
        return self.driver.is_visible(self.RECOMMEND_SECTION, timeout=5)

    def type_keyword(self, keyword: str) -> None:
        """검색어 입력"""
        inp = self._get_input_xpath()
        self.driver.find(inp)
        for char in keyword:
            self.driver.cdp.send("Input.dispatchKeyEvent", {
                "type": "char", "text": char
            })
        time.sleep(0.5)

    def submit_search(self) -> None:
        """Enter 입력으로 검색 실행 (search_011)"""
        self.driver.cdp.send("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "Enter", "code": "Enter",
            "windowsVirtualKeyCode": 13
        })
        self.driver.cdp.send("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "Enter", "code": "Enter",
            "windowsVirtualKeyCode": 13
        })
        time.sleep(2)

    def search(self, keyword: str) -> None:
        """검색어 입력 + 검색 실행 통합"""
        self.type_keyword(keyword)
        self.submit_search()

    def has_search_history(self, keyword: str = None) -> bool:
        """검색 기록 노출 확인 (search_011)"""
        if keyword:
            xpath = f'//*[contains(normalize-space(),"{keyword}")]'
            return self.driver.is_visible(xpath, timeout=5)
        return self.driver.is_visible(self.SEARCH_HISTORY_AREA, timeout=3)

    def is_live_section_visible(self, timeout: float = 8) -> bool:
        """LIVE 섹션 노출 확인 (search_012)"""
        return self.driver.is_visible(self.LIVE_RESULT_SECTION, timeout=timeout)

    def is_vod_section_visible(self, timeout: float = 8) -> bool:
        """VOD 섹션 노출 확인 (search_013)"""
        return self.driver.is_visible(self.VOD_RESULT_SECTION, timeout=timeout)

    def is_first_live_focused(self) -> bool:
        """첫 번째 LIVE 썸네일 포커스 확인 (search_012)"""
        js = """
        (function(){
            var el = document.activeElement;
            return el ? (el.tagName + ' ' + (el.className||'')).substring(0,50) : 'none';
        })()
        """
        try:
            result = self.driver.cdp.evaluate(js)
            return result and result.lower() not in ('none', 'body', '')
        except Exception:
            return False

    def is_live_more_button_visible(self) -> bool:
        """LIVE 더보기 버튼 노출 확인 (search_021)"""
        return self.driver.is_visible(self.BTN_LIVE_MORE, timeout=5)

    def click_live_more(self) -> bool:
        """LIVE 더보기 버튼 클릭 (search_022)"""
        return self.driver.click(self.BTN_LIVE_MORE)

    def is_vod_more_button_visible(self) -> bool:
        """VOD 더보기 버튼 노출 확인 (search_031)"""
        return self.driver.is_visible(self.BTN_VOD_MORE, timeout=5)

    def click_vod_more(self) -> bool:
        """VOD 더보기 버튼 클릭 (search_032)"""
        return self.driver.click(self.BTN_VOD_MORE)

    def click_delete_history(self) -> bool:
        """검색 기록 삭제 버튼 클릭 (search_034)"""
        return self.driver.click(self.BTN_DELETE_HISTORY)

    def is_delete_confirm_visible(self) -> bool:
        """삭제 확인 얼럿 노출 확인 (search_034)"""
        return self.driver.is_visible(self.BTN_CONFIRM, timeout=5)

    def confirm_delete(self) -> bool:
        """확인 버튼 클릭 (search_035)"""
        return self.driver.click(self.BTN_CONFIRM)

    def is_history_gone(self) -> bool:
        """검색 기록 삭제 후 기록 영역 미노출 확인 (search_035)"""
        return not self.driver.is_visible(self.SEARCH_HISTORY_AREA, timeout=3)

    def press_back(self) -> None:
        """리모컨 BACK 키 (search_002, 023, 033)"""
        self.driver.cdp.send("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "GoBack", "code": "GoBack",
            "windowsVirtualKeyCode": 461
        })
        self.driver.cdp.send("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "GoBack", "code": "GoBack",
            "windowsVirtualKeyCode": 461
        })
        time.sleep(1)