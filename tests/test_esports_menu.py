"""
test_esports_menu.py
- SOOP TV eSports 메뉴 자동화 테스트 케이스
"""
import pytest
from pages.home_page import HomePage
from pages.esports_page import EsportsPage

class TestEsportsTabEntry:
    def test_first_category_focused_on_entry(self, driver):
        """
        # TC: esports_001
        eSports 탭 진입 시 첫 번째 카테고리에 포커스되어 있는지 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        assert esports.is_loaded(timeout=8), "eSports 메뉴 진입 실패"
        import time; time.sleep(2)
        assert esports.is_first_category_focused(), "첫 번째 카테고리에 포커스되지 않았습니다 (esports_001)"

    def test_category_list_visible(self, driver):
        """
        # TC: esports_002
        eSports 탭 진입 시 카테고리 리스트가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        assert esports.is_loaded(timeout=8), "eSports 메뉴 진입 실패"
        count = esports.get_category_count()
        assert count > 0, f"카테고리 리스트가 표시되지 않습니다. (count: {count}) (esports_002)"

    @pytest.mark.skip(reason="보류 - TV 특성상 롤링 안됨 (예상)")
    def test_last_category_wraps_to_first(self, driver):
        """
        # TC: esports_003
        마지막 카테고리에서 오른쪽으로 이동 시 처음으로 롤링되는지 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        assert esports.is_loaded(timeout=8), "eSports 메뉴 진입 실패"
        count = esports.get_category_count()
        esports.navigate_to_last_category(count)
        assert esports.click_last_category_right(), "마지막 카테고리에서 우측 이동 시 처음으로 롤링되지 않습니다 (esports_003)"

class TestEsportsCategoryMore:
    def test_category_click_shows_season_list(self, driver):
        """
        # TC: esports_004
        카테고리 클릭 시 시즌 리스트가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        assert esports.is_loaded(timeout=8), "eSports 메뉴 진입 실패"
        esports.click_first_category()
        assert esports.is_season_list_visible(), "카테고리 클릭 후 시즌 리스트 화면이 표시되지 않습니다 (esports_004)"

    def test_vod_list_visible_in_category(self, driver):
        """
        # TC: esports_013
        eSports 탭(카테고리 포함) 하위에 실제 VOD 리스트가 노출되는지 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        assert esports.is_loaded(timeout=8), "eSports 메뉴 진입 실패"
        assert esports.is_vod_list_visible_in_category(), "VOD 섹션 하위에 방송 리스트가 노출되지 않습니다 (esports_013)"

class TestEsportsCategoryDetail:
    @pytest.mark.skip(reason="보류 - 필터 적용 검증 로직 추가 필요")
    def test_latest_season_filter_applied(self, driver):
        """
        # TC: esports_023
        카테고리 진입 시 기본으로 최신 시즌 필터가 적용되어 있는지 확인
        """
        pass

    @pytest.mark.skip(reason="보류 - 필터별 검증 로직 추가 필요")
    def test_season_related_vod_visible(self, driver):
        """
        # TC: esports_024
        시즌 관련 VOD가 노출되는지 확인
        """
        pass

    def test_season_filter_options_visible(self, driver):
        """
        # TC: esports_025
        시즌 필터 옵션 노출 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        esports.click_first_category()
        assert esports.is_season_filter_visible(), "시즌 필터 옵션이 노출되지 않습니다 (esports_025)"

    def test_season_filter_changes_sort(self, driver):
        """
        # TC: esports_026
        시즌 필터 클릭 시 동작 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        esports.click_first_category()
        assert esports.click_season_filter(), "시즌 필터 옵션 클릭 실패 (esports_026)"

    def test_video_type_filter_options_visible(self, driver):
        """
        # TC: esports_027
        영상 타입 필터 옵션 노출 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        esports.click_first_category()
        assert esports.is_video_type_filter_visible(), "영상 타입 필터 옵션이 노출되지 않습니다 (esports_027)"

    def test_video_type_filter_changes_sort(self, driver):
        """
        # TC: esports_028
        영상 타입 필터 클릭 시 동작 확인
        """
        home = HomePage(driver)
        home.click_esports_menu()
        esports = EsportsPage(driver)
        esports.click_first_category()
        assert esports.click_video_type_filter(), "영상 타입 필터 옵션 클릭 실패 (esports_028)"
