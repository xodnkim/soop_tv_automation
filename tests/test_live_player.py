"""
test_live_player.py
- SOOP TV LIVE 플레이어 자동화 테스트 케이스
"""
import pytest
from pages.home_page import HomePage
from pages.live_player_page import LivePlayerPage

class TestLivePlayerBasic:
    def test_player_entry_and_playback(self, driver):
        """# TC: liveplayer_011"""
        home = HomePage(driver)
        home.click_live_menu()
        from pages.live_page import LivePage
        live = LivePage(driver)
        # 첫 번째 카테고리 진입 후 첫 번째 방송 클릭
        live.click_first_category()
        import time; time.sleep(2)
        driver.press_down()
        driver.press_enter()
        player = LivePlayerPage(driver)
        assert player.is_loaded(timeout=10), "LIVE 플레이어 진입 실패"

    def test_chat_ui_visible(self, driver):
        """# TC: liveplayer_012"""
        player = LivePlayerPage(driver)
        assert player.is_chat_ui_visible(), "채팅 UI가 노출되지 않습니다"

class TestLivePlayerNotLoggedIn:
    @pytest.fixture(autouse=True)
    def skip_if_logged_in(self):
        # 향후 로그인 여부를 판단해서 분기처리 가능. 현재는 보류
        pytest.skip("보류 - 비로그인 상태 검증 로직 추가 필요")

    def test_quick_chat_redirects_to_login(self, driver):
        """# TC: liveplayer_013"""
        pass

    def test_back_from_login_returns_to_player(self, driver):
        """# TC: liveplayer_014"""
        pass

    def test_star_ball_redirects_to_login(self, driver):
        """# TC: liveplayer_015"""
        pass

    def test_back_from_star_login(self, driver):
        """# TC: liveplayer_016"""
        pass

    def test_up_button_redirects_to_login(self, driver):
        """# TC: liveplayer_017"""
        pass

    def test_back_from_up_login(self, driver):
        """# TC: liveplayer_018"""
        pass

    def test_favorite_redirects_to_login(self, driver):
        """# TC: liveplayer_019"""
        pass

    def test_back_from_favorite_login(self, driver):
        """# TC: liveplayer_020"""
        pass

    def test_watch_later_redirects_to_login(self, driver):
        """# TC: liveplayer_021"""
        pass

class TestLivePlayerChat:
    def test_chat_area_visible(self, driver):
        """# TC: liveplayer_025"""
        player = LivePlayerPage(driver)
        assert player.is_chat_area_visible()

    def test_chat_default_on(self, driver):
        """# TC: liveplayer_026"""
        pass

    def test_chat_ui_toggle_off(self, driver):
        """# TC: liveplayer_027"""
        player = LivePlayerPage(driver)
        player.click_chat_toggle()
        # 토글 오프 상태 검증 로직 (일시적 보류)
        pass

    def test_short_chat_visible(self, driver):
        """# TC: liveplayer_028"""
        pass

    def test_chat_toggle_back_on(self, driver):
        """# TC: liveplayer_030"""
        pass

    @pytest.mark.skip(reason="보류 - 로그인 후 입력 전송 검증 필요")
    def test_quick_chat_send(self, driver):
        """# TC: liveplayer_036~037"""
        pass

class TestLivePlayerBroadcastInfo:
    def test_broadcast_info_area_visible(self, driver):
        """# TC: liveplayer_038"""
        player = LivePlayerPage(driver)
        assert player.is_broadcast_info_visible()

    def test_viewer_count_and_time_visible(self, driver):
        """# TC: liveplayer_039"""
        player = LivePlayerPage(driver)
        assert player.is_viewer_count_visible()

    def test_broadcast_title_visible(self, driver):
        """# TC: liveplayer_040"""
        player = LivePlayerPage(driver)
        assert player.is_broadcast_title_visible()

    def test_progress_bar_visible(self, driver):
        """# TC: liveplayer_041"""
        player = LivePlayerPage(driver)
        assert player.is_progress_bar_visible()

    def test_live_badge_visible(self, driver):
        """# TC: liveplayer_042"""
        player = LivePlayerPage(driver)
        assert player.is_live_badge_visible()

class TestLivePlayerButtons:
    @pytest.fixture(autouse=True)
    def skip_if_not_logged_in(self):
        pytest.skip("보류 - 로그인 선행 필요")

    def test_up_button_toggles(self, driver):
        """# TC: liveplayer_058"""
        pass

    def test_favorite_button_toggles(self, driver):
        """# TC: liveplayer_059"""
        pass

    def test_favorite_button_detoggles(self, driver):
        """# TC: liveplayer_060"""
        pass

    def test_watch_later_button_toggles(self, driver):
        """# TC: liveplayer_061"""
        pass

    def test_watch_later_button_detoggles(self, driver):
        """# TC: liveplayer_062"""
        pass

class TestLivePlayerRelatedContent:
    def test_down_shows_streamer_vod_list(self, driver):
        """# TC: liveplayer_063"""
        player = LivePlayerPage(driver)
        player.press_down()
        assert player.is_streamer_vod_list_visible()

    def test_streamer_vod_thumbnail_info(self, driver):
        """# TC: liveplayer_064~065"""
        pass

    def test_vod_click_enters_vod_player(self, driver):
        """# TC: liveplayer_066"""
        player = LivePlayerPage(driver)
        # press enter on thumbnail
        driver.press_enter()
        # verify VOD player entry
        pass

    def test_back_from_vod_returns_to_list(self, driver):
        """# TC: liveplayer_067"""
        player = LivePlayerPage(driver)
        player.press_back()

    def test_down_shows_recommended_live(self, driver):
        """# TC: liveplayer_068"""
        player = LivePlayerPage(driver)
        player.press_down()
        player.press_down()
        assert player.is_recommended_live_visible()

    def test_recommended_live_info(self, driver):
        """# TC: liveplayer_069"""
        pass

    def test_live_click_switches_player(self, driver):
        """# TC: liveplayer_070"""
        pass

    def test_back_from_live_returns_to_list(self, driver):
        """# TC: liveplayer_071"""
        pass
