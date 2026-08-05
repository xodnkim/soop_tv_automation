"""
test_my_menu.py
- SOOP TV MY 메뉴 자동화 테스트 케이스
"""
import pytest
from pages.home_page import HomePage
from pages.my_tab_page import MyTabPage

pytestmark = pytest.mark.skip(reason="보류 - 로그인 선행 필요 (QR/인증)")

class TestMyFavoriteAll:
    def test_favorite_section_title_visible(self, driver):
        """# TC: my_001"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_loaded(timeout=8)
        assert my.is_favorite_all_section_visible()

    def test_streamer_info_visible(self, driver):
        """# TC: my_002"""
        pass

    def test_recent_broadcast_time_visible(self, driver):
        """# TC: my_003"""
        pass

    def test_streamer_click_shows_context_menu(self, driver):
        """# TC: my_004"""
        pass

    def test_context_menu_profile_info(self, driver):
        """# TC: my_005"""
        pass

    def test_live_join_button_if_live(self, driver):
        """# TC: my_006"""
        pass

    def test_favorite_delete_button_visible(self, driver):
        """# TC: my_007"""
        pass

    def test_favorite_delete_shows_toast(self, driver):
        """# TC: my_010"""
        pass

    def test_favorite_more_button_visible(self, driver):
        """# TC: my_011"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_favorite_more_button_visible()

    def test_favorite_more_button_click(self, driver):
        """# TC: my_012"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_favorite_more()

    def test_back_from_favorite_more(self, driver):
        """# TC: my_013"""
        pass

class TestMySubscribedLive:
    def test_subscribed_live_section_visible(self, driver):
        """# TC: my_021"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_subscribed_live_section_visible()

    def test_subscribed_live_more_button(self, driver):
        """# TC: my_030"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_subscribed_live_more()

    def test_subscribed_live_more_list(self, driver):
        """# TC: my_031"""
        pass

class TestMySubscribedVod:
    def test_subscribed_vod_section_visible(self, driver):
        """# TC: my_038"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_subscribed_vod_section_visible()

    def test_subscribed_vod_more_button(self, driver):
        """# TC: my_047"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_subscribed_vod_more()

class TestMyFavoritedLive:
    def test_favorited_live_section_visible(self, driver):
        """# TC: my_055"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_favorited_live_section_visible()

    def test_favorited_live_more_button(self, driver):
        """# TC: my_064"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_favorited_live_more()

class TestMyFavoritedClip:
    def test_favorited_clip_section_visible(self, driver):
        """# TC: my_072"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_favorited_clip_section_visible()

    def test_favorited_clip_more_button(self, driver):
        """# TC: my_082"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_favorited_clip_more()

class TestMyFavoritedVod:
    def test_favorited_vod_section_visible(self, driver):
        """# TC: my_091"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_favorited_vod_section_visible()

    def test_favorited_vod_more_button(self, driver):
        """# TC: my_102"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_favorited_vod_more()

class TestMyFanLive:
    def test_fan_live_section_visible(self, driver):
        """# TC: my_112"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_fan_live_section_visible()

    def test_fan_live_more_button(self, driver):
        """# TC: my_121"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_fan_live_more()

class TestMyFanVod:
    def test_fan_vod_section_visible(self, driver):
        """# TC: my_129"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_fan_vod_section_visible()

    def test_fan_vod_more_button(self, driver):
        """# TC: my_138"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_fan_vod_more()

class TestMyRecentLive:
    def test_recent_live_section_visible(self, driver):
        """# TC: my_146"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_recent_live_section_visible()

    def test_recent_live_more_button(self, driver):
        """# TC: my_155"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_recent_live_more()

class TestMyRecentVod:
    def test_recent_vod_section_visible(self, driver):
        """# TC: my_163"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_recent_vod_section_visible()

    def test_recent_vod_more_button(self, driver):
        """# TC: my_172"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_recent_vod_more()

class TestMyRecommendAndWatchLater:
    def test_recommend_streamer_section_visible(self, driver):
        """# TC: my_180"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_recommend_streamer_section_visible()

    def test_watch_later_section_visible(self, driver):
        """# TC: my_189"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_watch_later_section_visible()

    def test_watch_later_more_button(self, driver):
        """# TC: my_198"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_watch_later_more()

class TestMyUpVod:
    def test_up_vod_section_visible(self, driver):
        """# TC: my_206"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.is_up_vod_section_visible()

    def test_up_vod_more_button(self, driver):
        """# TC: my_215"""
        home = HomePage(driver)
        home.click_my_menu()
        my = MyTabPage(driver)
        assert my.click_up_vod_more()
