"""
test_live_menu.py
- SOOP TV LIVE 메뉴 자동화 테스트 케이스
"""
import pytest
from pages.home_page import HomePage
from pages.live_page import LivePage

class TestLiveTabEntry:
    def test_all_category_focused_on_entry(self, driver):
        """
        # TC: live_001
        LIVE 탭 진입 시 '전체' 카테고리에 포커스되어 있는지 확인
        """
        home = HomePage(driver)
        home.click_live_menu()
        live = LivePage(driver)
        assert live.is_loaded(timeout=8), "LIVE 메뉴 진입 실패"
        assert live.is_first_category_focused(), "'전체' 카테고리에 포커스되지 않았습니다 (live_001)"

    def test_category_list_visible(self, driver):
        """
        # TC: live_002
        LIVE 탭 진입 시 카테고리 리스트가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_live_menu()
        live = LivePage(driver)
        assert live.is_loaded(timeout=8), "LIVE 메뉴 진입 실패"
        count = live.get_category_count()
        assert count > 0, f"카테고리 리스트가 표시되지 않습니다. (count: {count}) (live_002)"

    @pytest.mark.skip(reason="보류 - TV 특성상 롤링 안됨 (예상)")
    def test_last_category_wraps_to_first(self, driver):
        """
        # TC: live_003
        마지막 카테고리에서 오른쪽으로 이동 시 처음('전체')으로 롤링되는지 확인
        """
        home = HomePage(driver)
        home.click_live_menu()
        live = LivePage(driver)
        assert live.is_loaded(timeout=8), "LIVE 메뉴 진입 실패"
        count = live.get_category_count()
        assert count > 0, "카테고리가 없습니다"
        
        live.navigate_to_last_category(count)
        assert live.click_last_category_right(), "마지막 카테고리에서 우측 이동 시 '전체'로 롤링되지 않습니다 (live_003)"

class TestLiveCategoryMore:
    def test_category_click_shows_more_list(self, driver):
        """
        # TC: live_004
        특정 카테고리('전체') 클릭 시 더보기 리스트(혹은 해당 카테고리 페이지) 노출
        """
        home = HomePage(driver)
        home.click_live_menu()
        live = LivePage(driver)
        assert live.is_loaded(timeout=8), "LIVE 메뉴 진입 실패"
        live.click_first_category()
        assert live.is_more_list_visible(), "카테고리 클릭 후 더보기/리스트 화면이 표시되지 않습니다 (live_004)"

    def test_live_list_visible_in_category(self, driver):
        """
        # TC: live_015
        LIVE 탭(카테고리 포함) 하위에 실제 방송 리스트(썸네일 등)가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_live_menu()
        live = LivePage(driver)
        assert live.is_loaded(timeout=8), "LIVE 메뉴 진입 실패"
        assert live.is_live_list_visible_in_section(), "LIVE 섹션 하위에 방송 리스트가 노출되지 않습니다 (live_015)"
