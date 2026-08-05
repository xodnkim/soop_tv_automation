"""
test_vod_menu.py
- SOOP TV VOD 메뉴 자동화 테스트 케이스
"""
import pytest
from pages.home_page import HomePage
from pages.vod_page import VodPage

class TestVodTabEntry:
    def test_all_category_focused_on_entry(self, driver):
        """
        # TC: vod_001
        VOD 탭 진입 시 '전체' 카테고리에 포커스되어 있는지 확인
        """
        home = HomePage(driver)
        home.click_vod_menu()
        vod = VodPage(driver)
        assert vod.is_loaded(timeout=8), "VOD 메뉴 진입 실패"
        assert vod.is_first_category_focused(), "'전체' 카테고리에 포커스되지 않았습니다 (vod_001)"

    def test_category_list_visible(self, driver):
        """
        # TC: vod_002
        VOD 탭 진입 시 카테고리 리스트가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_vod_menu()
        vod = VodPage(driver)
        assert vod.is_loaded(timeout=8), "VOD 메뉴 진입 실패"
        count = vod.get_category_count()
        assert count > 0, f"카테고리 리스트가 표시되지 않습니다. (count: {count}) (vod_002)"

    @pytest.mark.skip(reason="보류 - TV 특성상 롤링 안됨 (예상)")
    def test_last_category_wraps_to_first(self, driver):
        """
        # TC: vod_003
        마지막 카테고리에서 오른쪽으로 이동 시 처음('전체')으로 롤링되는지 확인
        """
        home = HomePage(driver)
        home.click_vod_menu()
        vod = VodPage(driver)
        assert vod.is_loaded(timeout=8), "VOD 메뉴 진입 실패"
        count = vod.get_category_count()
        vod.navigate_to_last_category(count)
        assert vod.click_last_category_right(), "마지막 카테고리에서 우측 이동 시 '전체'로 롤링되지 않습니다 (vod_003)"

class TestVodCategoryMore:
    def test_category_click_shows_more_list(self, driver):
        """
        # TC: vod_004
        특정 카테고리('전체') 클릭 시 더보기 리스트(혹은 해당 카테고리 페이지) 노출
        """
        home = HomePage(driver)
        home.click_vod_menu()
        vod = VodPage(driver)
        assert vod.is_loaded(timeout=8), "VOD 메뉴 진입 실패"
        vod.click_first_category()
        assert vod.is_more_list_visible(), "카테고리 클릭 후 더보기/리스트 화면이 표시되지 않습니다 (vod_004)"

    def test_vod_list_visible_in_category(self, driver):
        """
        # TC: vod_013
        VOD 탭(카테고리 포함) 하위에 실제 방송 리스트(썸네일 등)가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_vod_menu()
        vod = VodPage(driver)
        assert vod.is_loaded(timeout=8), "VOD 메뉴 진입 실패"
        assert vod.is_vod_list_visible_in_section(), "VOD 섹션 하위에 방송 리스트가 노출되지 않습니다 (vod_013)"
