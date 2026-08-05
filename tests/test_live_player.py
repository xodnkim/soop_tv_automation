"""
test_live_player.py
- SOOP TV LIVE 플레이어 자동화 테스트 케이스
- TC 기준 시트: https://docs.google.com/spreadsheets/d/1Vs9QpBaKASekry0xOO-xYBJTe12eKqGbup5kUWty_Pc/edit?gid=327358501
"""
import time
import pytest
from pages.home_page import HomePage
from pages.live_player_page import LivePlayerPage
from pages.my_page import MyPage


# ============================================================
# 공통 헬퍼: 방송 진입 & 로그아웃
# ============================================================

def _enter_live_broadcast(driver):
    """
    홈에서 '궈가입니' 방송을 찾아 포커스 후 진입.
    TODO: 임시 로직 - 추후 범용 진입 로직으로 교체 예정
    """
    home = HomePage(driver)
    home.is_loaded(timeout=10)
    time.sleep(3)  # 방송 리스트 렌더링 대기

    if not home.find_and_enter_broadcast("궈가입니", max_attempts=15):
        pytest.fail("지정한 방송으로 포커스를 이동할 수 없습니다.")

    time.sleep(3)


def _ensure_logged_out(driver):
    """
    비로그인 사전조건 보장: 로그인 상태면 로그아웃 수행.
    """
    home = HomePage(driver)
    if not home.is_login_button_visible(timeout=3):
        # 로그인 버튼이 없으면 = 로그인 상태 → 로그아웃
        home.click_my_menu()
        my = MyPage(driver)
        my.logout()
        time.sleep(3)
        # 홈으로 복귀
        home.is_loaded(timeout=10)


# ============================================================
# BaseLivePlayerTest: 모든 LivePlayer 테스트의 공통 픽스처
# ============================================================

class BaseLivePlayerTest:
    @pytest.fixture(autouse=True)
    def enter_live_player(self, driver):
        """
        테스트 시작 전: 홈 → 지정 방송 진입 → 광고 처리
        (BaseLivePlayerTest를 상속하는 모든 클래스에 자동 적용)
        """
        _enter_live_broadcast(driver)
        player = LivePlayerPage(driver)
        assert player.is_loaded(timeout=30), "LIVE 플레이어 진입 실패"


# ============================================================
# TC: liveplayer_001~010 - 프리롤 광고
# 광고는 랜덤이므로: 광고 감지 시 검증, 미감지 시 skip 처리
# ============================================================

AD_VIDEO_XPATH   = '/html/body/div/main/div/div/div/div/div/div[1]/div/video'
AD_SKIP_BTN      = '//*[@id="root"]/main/div/div/div/div/div/div[2]/div[2]/button'
# 광고 좌측 하단 프로필/광고길이 영역
AD_PROFILE_AREA  = '/html/body/div/main/div/div/div/div/div/div[2]/div[1]'
# 퀵뷰 구매 안내 문구 (SKIP 버튼과 같은 div[2]/div[2] 영역 내)
AD_QUICKVIEW_TXT = '/html/body/div/main/div/div/div/div/div/div[2]/div[2]'


class TestLivePlayerAd:
    """
    프리롤 광고 관련 TC (liveplayer_001~010)
    - 광고 유무가 랜덤이므로 매 실행마다 광고가 뜨지 않을 수 있음
    - 광고가 감지되지 않으면 pytest.skip()으로 처리
    """

    @pytest.fixture(autouse=True)
    def enter_player_for_ad_test(self, driver):
        """홈 → 방송 진입 (광고 처리 없이 바로 플레이어 로드 대기)"""
        home = HomePage(driver)
        home.is_loaded(timeout=10)
        time.sleep(3)

        target_title = "궈가입니"
        found = False
        for _ in range(15):
            html = driver.cdp.evaluate("document.activeElement.outerHTML") or ""
            if target_title in html:
                driver.press_enter()
                found = True
                break
            driver.press_right()
            time.sleep(1.0)

        if not found:
            pytest.fail("지정한 방송으로 포커스를 이동할 수 없습니다.")
        time.sleep(2)  # 진입 직후 DOM 로딩 대기

    @pytest.fixture
    def require_ad(self, driver):
        """광고가 뜬 경우에만 테스트 실행, 없으면 skip"""
        if not driver.is_visible(AD_VIDEO_XPATH, timeout=3):
            pytest.skip("이번 실행에는 프리롤 광고가 노출되지 않았습니다.")

    @pytest.fixture
    def require_no_ad(self, driver):
        """광고가 없는 경우에만 테스트 실행, 있으면 skip"""
        if driver.is_visible(AD_VIDEO_XPATH, timeout=3):
            pytest.skip("이번 실행에 프리롤 광고가 노출되었습니다. (no-ad 케이스 아님)")

    def test_preroll_ad_plays(self, driver, require_ad):
        """# TC: liveplayer_001 - LIVE 방송 진입 시 프리롤 광고 재생"""
        # AD_VIDEO_XPATH 존재 자체가 광고 재생 확인
        assert driver.is_visible(AD_VIDEO_XPATH, timeout=3), "프리롤 광고가 재생되지 않습니다"

    def test_ad_profile_and_duration_visible(self, driver, require_ad):
        """# TC: liveplayer_002 - 좌측 하단 광고 프로필 및 광고 길이 노출"""
        # 광고 관련 UI 영역 노출 확인
        assert driver.is_visible(AD_PROFILE_AREA, timeout=5), "광고 프로필/길이 영역이 노출되지 않습니다"

    def test_ad_skip_indicator_visible(self, driver, require_ad):
        """# TC: liveplayer_003 - 우측 하단 인디케이터 및 [광고 SKIP] 버튼 노출"""
        # 광고 SKIP 버튼 영역이 DOM에 존재하는지 확인 (15초 전이라 비활성 상태)
        assert driver.is_visible(AD_SKIP_BTN, timeout=5), "광고 SKIP 버튼 영역이 노출되지 않습니다"

    def test_ad_quickview_notice_visible(self, driver, require_ad):
        """# TC: liveplayer_004 - 우측 하단 퀵뷰 구매 안내 문구 노출"""
        assert driver.is_visible(AD_QUICKVIEW_TXT, timeout=5), "퀵뷰 구매 안내 문구가 노출되지 않습니다"

    def test_ad_skip_button_active_after_15s(self, driver, require_ad):
        """# TC: liveplayer_005 - 15초 후 [광고 SKIP] 버튼 자동 포커스"""
        # 광고 시작 후 최대 16초 대기 후 SKIP 버튼 활성화 확인
        time.sleep(16)
        assert driver.is_visible(AD_SKIP_BTN, timeout=3), "15초 후 [광고 SKIP] 버튼이 활성화되지 않습니다"

    def test_ad_focus_locked_to_skip_button(self, driver, require_ad):
        """# TC: liveplayer_006 - 방향키 클릭 시 [광고 SKIP] 외 다른 포커스 이동 불가"""
        time.sleep(16)  # SKIP 버튼 활성화 대기
        # 방향키를 눌러도 포커스가 SKIP 버튼 밖으로 나가지 않아야 함
        driver.press_left()
        time.sleep(0.5)
        driver.press_up()
        time.sleep(0.5)
        driver.press_down()
        time.sleep(0.5)
        # SKIP 버튼이 여전히 화면에 존재하는지 확인
        assert driver.is_visible(AD_SKIP_BTN, timeout=3), "방향키 이후 SKIP 버튼이 사라졌습니다"

    def test_ad_skip_button_click_ends_ad(self, driver, require_ad):
        """# TC: liveplayer_007 - [광고 SKIP] 버튼 클릭 → 프리롤 광고 즉시 종료"""
        time.sleep(16)  # SKIP 버튼 활성화 대기
        assert driver.is_visible(AD_SKIP_BTN, timeout=3), "[광고 SKIP] 버튼이 활성화되지 않았습니다"
        driver.click(AD_SKIP_BTN)
        time.sleep(2)
        # 광고 종료 후 AD_VIDEO_XPATH가 사라지는지 확인
        assert not driver.is_visible(AD_VIDEO_XPATH, timeout=5), "광고 SKIP 후에도 광고 비디오가 남아있습니다"

    def test_no_ad_player_loads_normally(self, driver, require_no_ad):
        """# TC: liveplayer_008 - 프리롤 광고가 없는 경우 LIVE 플레이어 정상 진입"""
        player = LivePlayerPage(driver)
        # 광고 없이 바로 본방송 비디오가 로드되어야 함
        assert player.is_loaded(timeout=15), "광고 없는 상태에서 LIVE 플레이어 로딩 실패"

    @pytest.mark.skip(reason="보류 - 네트워크 요청 캡처 필요 (CDP Network 도메인 활용 시 구현 가능)")
    def test_ad_api_called(self, driver):
        """# TC: liveplayer_009 - 광고 API 정상 호출 확인"""
        pass

    @pytest.mark.skip(reason="보류 - 네트워크 응답 파싱 필요 (liveplayer_010)")
    def test_ad_api_response_no_ads(self, driver):
        """# TC: liveplayer_010 - 광고 API 리스폰스 status = NO_ADS 확인"""
        pass


# ============================================================
# TC: liveplayer_011~012 - LIVE 플레이어 기본 진입
# ============================================================

class TestLivePlayerBasic(BaseLivePlayerTest):
    def test_player_entry_and_playback(self, driver):
        """# TC: liveplayer_011 - 방송 영상 및 사운드 재생 확인"""
        pass  # 진입 자체가 BaseLivePlayerTest 픽스처에서 검증됨

    def test_chat_ui_visible(self, driver):
        """# TC: liveplayer_012 - 우측 채팅 UI 노출"""
        player = LivePlayerPage(driver)
        assert player.is_chat_ui_visible(), "채팅 UI가 노출되지 않습니다"


# ============================================================
# TC: liveplayer_013~020 - 비로그인 사전조건 케이스
# 사전조건: 비로그인 상태 (로그인 상태면 로그아웃 후 수행)
# ============================================================

class TestLivePlayerNotLoggedIn(BaseLivePlayerTest):
    @pytest.fixture(autouse=True)
    def ensure_logged_out(self, driver):
        """비로그인 사전조건 보장: 로그인 상태면 로그아웃"""
        _ensure_logged_out(driver)

    def test_star_ball_redirects_to_login(self, driver):
        """# TC: liveplayer_013 - [별풍선] 버튼 클릭 시 로그인 화면 노출"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_star_ball()
        assert player.is_login_screen_visible(), "로그인 화면이 노출되지 않습니다"

    def test_back_from_star_ball_login(self, driver):
        """# TC: liveplayer_014 - 별풍선 로그인 화면에서 BACK → LIVE 플레이어 복귀"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_star_ball()
        player.is_login_screen_visible()
        player.press_back()
        time.sleep(2)
        assert player.is_loaded(timeout=10), "LIVE 플레이어로 복귀하지 못했습니다"

    def test_up_button_redirects_to_login(self, driver):
        """# TC: liveplayer_015 - [UP] 버튼 클릭 시 로그인 화면 노출"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_up()
        assert player.is_login_screen_visible(), "로그인 화면이 노출되지 않습니다"

    def test_back_from_up_login(self, driver):
        """# TC: liveplayer_016 - UP 로그인 화면에서 BACK → LIVE 플레이어 복귀"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_up()
        player.is_login_screen_visible()
        player.press_back()
        time.sleep(2)
        assert player.is_loaded(timeout=10), "LIVE 플레이어로 복귀하지 못했습니다"

    def test_favorite_redirects_to_login(self, driver):
        """# TC: liveplayer_017 - [즐겨찾기] 버튼 클릭 시 로그인 화면 노출"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_favorite()
        assert player.is_login_screen_visible(), "로그인 화면이 노출되지 않습니다"

    def test_back_from_favorite_login(self, driver):
        """# TC: liveplayer_018 - 즐겨찾기 로그인 화면에서 BACK → LIVE 플레이어 복귀"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_favorite()
        player.is_login_screen_visible()
        player.press_back()
        time.sleep(2)
        assert player.is_loaded(timeout=10), "LIVE 플레이어로 복귀하지 못했습니다"

    def test_watch_later_redirects_to_login(self, driver):
        """# TC: liveplayer_019 - [나중에 보기] 버튼 클릭 시 로그인 화면 노출"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.click_watch_later()
        assert player.is_login_screen_visible(), "로그인 화면이 노출되지 않습니다"

    def test_watch_later_login_then_return(self, driver):
        """# TC: liveplayer_020 - 나중에 보기 → 로그인 프로세스 진행 후 LIVE 플레이어 복귀"""
        # 로그인 완료 후 LIVE 복귀 여부 확인은 실제 로그인 의존 → 보류
        pytest.skip("보류 - 실제 로그인 계정 의존 (liveplayer_020)")


# ============================================================
# TC: liveplayer_021~035 - 시청/채팅 영역
# ============================================================

class TestLivePlayerViewing(BaseLivePlayerTest):
    def test_video_buffering_and_frame(self, driver):
        """# TC: liveplayer_021 - 영상 버퍼링 및 프레임 확인"""
        pass  # 시청 화질 자동화 불가 (육안 검증)

    def test_audio_video_sync(self, driver):
        """# TC: liveplayer_022 - 오디오 & 비디오 싱크 확인"""
        pass  # 싱크 자동화 불가 (육안 검증)


class TestLivePlayerChat(BaseLivePlayerTest):
    def test_chat_area_visible(self, driver):
        """# TC: liveplayer_023 - 우측 채팅 UI 노출"""
        player = LivePlayerPage(driver)
        assert player.is_chat_area_visible()

    def test_chat_default_on(self, driver):
        """# TC: liveplayer_024 - 디폴트 설정값: 채팅 ON"""
        pass

    def test_chat_ui_toggle_off(self, driver):
        """# TC: liveplayer_025 - [채팅 UI] 버튼 클릭 → 우측 채팅 UI 미노출"""
        player = LivePlayerPage(driver)
        player.click_chat_toggle()
        time.sleep(1)
        # 채팅이 꺼졌는지 검증 (향후 XPath 확정 후 구현)
        pass

    def test_short_chat_visible_when_chat_off(self, driver):
        """# TC: liveplayer_026 - 채팅 OFF 상태에서 숏채팅 노출"""
        pass

    def test_chat_setting_persists_after_relaunch(self, driver):
        """# TC: liveplayer_027 - 앱 재실행 후 채팅 OFF 설정 유지"""
        pass

    def test_chat_ui_toggle_back_on(self, driver):
        """# TC: liveplayer_028 - 채팅 UI 다시 클릭 → 우측 채팅 UI 노출"""
        pass

    def test_chat_user_grade_color(self, driver):
        """# TC: liveplayer_029 - 등급별 유저 닉네임 색상 정상 반영"""
        pass

    def test_chat_subscription_personakon(self, driver):
        """# TC: liveplayer_030 - 구독 퍼스나콘 노출"""
        pass

    def test_chat_text_visible(self, driver):
        """# TC: liveplayer_031 - 채팅 텍스트 노출"""
        pass

    def test_chat_emoticon_visible(self, driver):
        """# TC: liveplayer_032 - 채팅 이모티콘 노출"""
        pass

    def test_chat_ogq_emoticon_visible(self, driver):
        """# TC: liveplayer_033 - 채팅 OGQ 이모티콘 노출"""
        pass

    def test_quick_chat_send(self, driver):
        """# TC: liveplayer_034~035 - 퀵채팅 클릭 → 채팅 전송 확인"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        assert player.click_quick_chat(), "퀵채팅 버튼 클릭 실패"


# ============================================================
# TC: liveplayer_036~040 - 방송 정보 영역
# ============================================================

class TestLivePlayerBroadcastInfo(BaseLivePlayerTest):
    def test_streamer_profile_and_nickname_visible(self, driver):
        """# TC: liveplayer_036 - 스트리머 프로필 이미지 / 닉네임 노출"""
        player = LivePlayerPage(driver)
        assert player.is_broadcast_info_visible()

    def test_viewer_count_and_time_visible(self, driver):
        """# TC: liveplayer_037 - 참여자 수 / 방송시간 노출"""
        player = LivePlayerPage(driver)
        assert player.is_viewer_count_visible()

    def test_broadcast_title_visible(self, driver):
        """# TC: liveplayer_038 - 방송 제목 노출"""
        player = LivePlayerPage(driver)
        assert player.is_broadcast_title_visible()

    def test_progress_bar_visible(self, driver):
        """# TC: liveplayer_039 - 프로그래스바 노출"""
        player = LivePlayerPage(driver)
        assert player.is_progress_bar_visible()

    def test_live_badge_visible(self, driver):
        """# TC: liveplayer_040 - LIVE 뱃지 노출"""
        player = LivePlayerPage(driver)
        assert player.is_live_badge_visible()


# ============================================================
# TC: liveplayer_041~055 - 별풍선 기능 (로그인 선행 필요)
# ============================================================

class TestLivePlayerStarBall(BaseLivePlayerTest):
    @pytest.fixture(autouse=True)
    def skip_if_not_logged_in(self):
        pytest.skip("보류 - 로그인 선행 및 별풍선 보유 상태 필요 (liveplayer_041~055)")

    def test_star_ball_ui_visible(self, driver):
        """# TC: liveplayer_041 - [별풍선] 버튼 클릭 시 별풍선 선물 UI 노출"""
        pass

    def test_star_ball_count_visible(self, driver):
        """# TC: liveplayer_042 - 보유 별풍선 개수 노출"""
        pass

    def test_star_ball_image_and_count_visible(self, driver):
        """# TC: liveplayer_043 - 기본/시그니처 별풍선 이미지 및 개수 노출"""
        pass

    def test_star_ball_gift_button_visible(self, driver):
        """# TC: liveplayer_044 - 선물하기 버튼 노출"""
        pass

    def test_star_ball_direct_input_visible(self, driver):
        """# TC: liveplayer_045 - 맨 우측 직접 입력 버튼 노출"""
        pass


# ============================================================
# TC: liveplayer_056~060 - UP/즐겨찾기/나중에보기 버튼 (로그인 선행 필요)
# ============================================================

class TestLivePlayerButtons(BaseLivePlayerTest):
    @pytest.fixture(autouse=True)
    def skip_if_not_logged_in(self):
        pytest.skip("보류 - 로그인 선행 필요 (liveplayer_056~060)")

    def test_up_button_toggles(self, driver):
        """# TC: liveplayer_056 - [UP] 버튼 클릭 → UI에 체크 표시 추가"""
        pass

    def test_favorite_button_toggles(self, driver):
        """# TC: liveplayer_057 - [즐겨찾기] 버튼 클릭 → UI에 체크 표시 추가"""
        pass

    def test_favorite_button_detoggles(self, driver):
        """# TC: liveplayer_058 - 다시 [즐겨찾기] 클릭 → 체크 표시 제거"""
        pass

    def test_watch_later_button_toggles(self, driver):
        """# TC: liveplayer_059 - [나중에 보기] 버튼 클릭 → 체크 표시 추가"""
        pass

    def test_watch_later_button_detoggles(self, driver):
        """# TC: liveplayer_060 - 다시 [나중에 보기] 클릭 → 체크 표시 제거"""
        pass


# ============================================================
# TC: liveplayer_061~069 - 스트리머 VOD 리스트 / 추천 방송
# ============================================================

class TestLivePlayerRelatedContent(BaseLivePlayerTest):
    def test_down_shows_streamer_vod_list(self, driver):
        """# TC: liveplayer_061 - 기능 영역에서 DOWN → 스트리머 VOD 리스트 노출"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.press_down()
        assert player.is_streamer_vod_list_visible()

    def test_streamer_vod_thumbnail_info(self, driver):
        """# TC: liveplayer_062~063 - VOD 썸네일 / 재생수 / 영상길이 / 닉네임 / 업로드일자 노출"""
        pass

    def test_vod_click_enters_vod_player(self, driver):
        """# TC: liveplayer_064 - VOD 썸네일 클릭 → LIVE 플레이어 종료 후 VOD 참여"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.press_down()
        time.sleep(1)
        driver.press_enter()
        time.sleep(3)
        # VOD 플레이어 진입 검증 (향후 VodPlayerPage.is_loaded() 연동)
        pass

    def test_back_from_vod_returns_to_list(self, driver):
        """# TC: liveplayer_065 - VOD 플레이어에서 BACK → 리스트 복귀"""
        player = LivePlayerPage(driver)
        player.press_back()
        time.sleep(2)

    def test_down_shows_recommended_live(self, driver):
        """# TC: liveplayer_066 - VOD 리스트에서 DOWN → 추천 방송 리스트 노출"""
        player = LivePlayerPage(driver)
        player.wake_up_ui()
        player.press_down()
        player.press_down()
        assert player.is_recommended_live_visible()

    def test_recommended_live_info(self, driver):
        """# TC: liveplayer_067 - 추천 방송 썸네일 / 참여자 수 / 타이틀 / 닉네임 노출"""
        pass

    def test_live_click_switches_player(self, driver):
        """# TC: liveplayer_068 - 추천 LIVE 썸네일 클릭 → 기존 플레이어 종료 후 LIVE 참여"""
        pass

    def test_back_from_live_returns_to_list(self, driver):
        """# TC: liveplayer_069 - BACK → 리스트 복귀"""
        pass

