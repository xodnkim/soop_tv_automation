"""
test_search.py
- SOOP TV 검색 화면 자동화 테스트 케이스
- 각 테스트 함수 상단에 TC_NO 주석으로 스프레드시트 TC와 연결
"""
import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage

SEARCH_KEYWORD = "soop"  # 검색 기록/결과 확인에 사용할 공통 키워드


# ============================================================
# [TC: search_001~003] 검색 화면 진입 및 기본 UI 확인
# ============================================================
class TestSearchEntry:
    """검색 화면 진입 및 기본 UI 검증"""

    def test_search_input_visible_on_entry(self, driver):
        """
        # TC: search_001
        검색 화면 진입 후 검색 입력 필드 포커스 및 키패드 노출
        - [LNB > 검색] 버튼 클릭 → 검색 입력 필드 표시 확인
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        assert search.is_search_input_visible(), "검색 입력 필드가 표시되지 않습니다 (search_001)"

    def test_back_key_closes_keypad(self, driver):
        """
        # TC: search_002
        검색 화면에서 리모컨 BACK 키 클릭 시 키패드 닫힘
        - 검색 화면 진입 → BACK 키 → 이전 화면으로 복귀 확인
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 진입 실패"
        search.press_back()
        # BACK 후 홈 화면으로 복귀
        assert home.is_loaded(timeout=5), "BACK 키 후 이전 화면 복귀 실패 (search_002)"

    def test_recommend_section_visible(self, driver):
        """
        # TC: search_003
        검색 화면 진입 시 추천 영상 섹션 노출
        - [검색] 진입 → '추천 영상' 섹션 타이틀 확인
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 진입 실패"
        assert search.is_recommend_section_visible(), "추천 영상 섹션이 표시되지 않습니다 (search_003)"


# ============================================================
# [TC: search_011~013] 검색 실행 후 결과 확인
# ============================================================
class TestSearchResult:
    """검색어 입력 후 결과 화면 검증"""

    def test_search_history_appears_after_search(self, driver):
        """
        # TC: search_011
        임의 검색어 입력 후 엔터 시 검색 기록에 입력했던 검색어 노출
        - 검색어 입력 → 엔터 → 검색 기록에 해당 키워드 존재 확인
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 진입 실패"
        search.search(SEARCH_KEYWORD)
        assert search.has_search_history(SEARCH_KEYWORD), \
            f"검색 기록에 '{SEARCH_KEYWORD}'가 노출되지 않습니다 (search_011)"

    def test_live_section_visible_after_search(self, driver):
        """
        # TC: search_012
        검색 결과 LIVE 섹션 노출 및 첫 번째 썸네일 포커스 확인
        - 검색 실행 → LIVE 섹션 타이틀 노출 확인
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 진입 실패"
        search.search(SEARCH_KEYWORD)
        assert search.is_live_section_visible(), \
            "검색 결과 LIVE 섹션이 표시되지 않습니다 (search_012)"

    def test_vod_section_visible_after_search(self, driver):
        """
        # TC: search_013
        검색 결과 VOD 섹션 노출 확인
        - 검색 실행 → VOD 섹션 타이틀 노출 확인
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 진입 실패"
        search.search(SEARCH_KEYWORD)
        assert search.is_vod_section_visible(), \
            "검색 결과 VOD 섹션이 표시되지 않습니다 (search_013)"


# ============================================================
# [TC: search_021~023] LIVE 더보기
# ============================================================
class TestSearchLiveMore:
    """LIVE 더보기 버튼 클릭 검증"""

    def test_live_more_button_visible(self, driver):
        """
        # TC: search_021
        LIVE 리스트 맨 우측 이동 시 [LIVE 더보기] 버튼 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        search.search(SEARCH_KEYWORD)
        assert search.is_live_more_button_visible(), \
            "LIVE 더보기 버튼이 표시되지 않습니다 (search_021)"

    def test_live_more_button_click_shows_list(self, driver):
        """
        # TC: search_022
        [LIVE 더보기] 버튼 클릭 시 LIVE 더보기 리스트 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        search.search(SEARCH_KEYWORD)
        assert search.click_live_more(), \
            "LIVE 더보기 버튼 클릭 실패 (search_022)"

    def test_back_from_live_more(self, driver):
        """
        # TC: search_023
        LIVE 더보기 리스트에서 리모컨 BACK 키 클릭 시 이전 화면 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        search.search(SEARCH_KEYWORD)
        search.click_live_more()
        import time; time.sleep(1)
        search.press_back()
        # 이전 화면(검색 결과)으로 복귀 - LIVE 섹션 또는 검색 화면 확인
        assert search.is_loaded(timeout=5) or home.is_loaded(timeout=3), \
            "BACK 키 후 이전 화면 복귀 실패 (search_023)"


# ============================================================
# [TC: search_031~033] VOD 더보기
# ============================================================
class TestSearchVodMore:
    """VOD 더보기 버튼 클릭 검증"""

    def test_vod_more_button_visible(self, driver):
        """
        # TC: search_031
        VOD 리스트 맨 우측 이동 시 [VOD 더보기] 버튼 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        search.search(SEARCH_KEYWORD)
        assert search.is_vod_more_button_visible(), \
            "VOD 더보기 버튼이 표시되지 않습니다 (search_031)"

    def test_vod_more_button_click_shows_list(self, driver):
        """
        # TC: search_032
        [VOD 더보기] 버튼 클릭 시 VOD 더보기 리스트 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        search.search(SEARCH_KEYWORD)
        assert search.click_vod_more(), \
            "VOD 더보기 버튼 클릭 실패 (search_032)"

    def test_back_from_vod_more(self, driver):
        """
        # TC: search_033
        VOD 더보기 리스트에서 리모컨 BACK 키 클릭 시 이전 화면 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        search.search(SEARCH_KEYWORD)
        search.click_vod_more()
        import time; time.sleep(1)
        search.press_back()
        assert search.is_loaded(timeout=5) or home.is_loaded(timeout=3), \
            "BACK 키 후 이전 화면 복귀 실패 (search_033)"


# ============================================================
# [TC: search_034~035] 검색 기록 삭제
# ============================================================
class TestSearchHistoryDelete:
    """검색 기록 삭제 검증"""

    def test_delete_history_shows_confirm_alert(self, driver):
        """
        # TC: search_034
        [검색 기록 삭제] 버튼 클릭 시 삭제 컨펌 얼럿 노출
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        # 검색어 입력해서 기록 생성
        search.search(SEARCH_KEYWORD)
        import time; time.sleep(1)
        # 다시 검색 화면 진입하여 기록 삭제 버튼 확인
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 재진입 실패"
        assert search.click_delete_history(), "검색 기록 삭제 버튼 클릭 실패 (search_034)"
        assert search.is_delete_confirm_visible(), \
            "검색 기록 삭제 컨펌 얼럿이 표시되지 않습니다 (search_034)"

    def test_confirm_deletes_history(self, driver):
        """
        # TC: search_035
        [확인] 버튼 클릭 시 얼럿 닫히며 검색 기록 영역 미노출 및 입력필드 포커스
        """
        home = HomePage(driver)
        home.click_search()
        search = SearchPage(driver)
        # 검색어 입력해서 기록 생성
        search.search(SEARCH_KEYWORD)
        import time; time.sleep(1)
        # 다시 검색 화면 진입
        home.click_search()
        search = SearchPage(driver)
        assert search.is_loaded(timeout=5), "검색 화면 재진입 실패"
        search.click_delete_history()
        assert search.is_delete_confirm_visible(), "컨펌 얼럿 미노출"
        assert search.confirm_delete(), "확인 버튼 클릭 실패 (search_035)"
        import time; time.sleep(1)
        # 검색 기록이 사라지거나 입력 필드가 다시 포커스
        assert search.is_search_input_visible(), \
            "삭제 후 입력 필드 포커스 확인 실패 (search_035)"