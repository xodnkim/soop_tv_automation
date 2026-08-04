"""
test_home.py
- SOOP TV 홈 화면 자동화 테스트 케이스
- TC 대상: Android TV 기본 기능 > 앱 실행 / 홈 화면 섹션 검증
"""
import pytest
from pages.home_page import HomePage


# ============================================================
# [Depth1: 앱 실행] [Depth2: OS 홈] [Depth3: 앱]
# ============================================================
class TestAppLaunch:
    """앱 실행 진입점 - 홈 화면 진입 확인"""

    def test_home_label_visible(self, driver):
        """TC: 홈 화면 진입 시 '홈' 라벨 노출 확인"""
        home = HomePage(driver)
        assert home.is_loaded(), "'홈' 라벨을 찾지 못했습니다"
        assert "홈" in home.home_label_text(), f"텍스트 불일치: '{home.home_label_text()}'"

    def test_login_button_visible_when_not_logged_in(self, driver):
        """TC: 로그인 전 상태에서 상단 '로그인' 버튼 노옶 확인"""
        home = HomePage(driver)
        if not home.is_logged_out():
            pytest.skip("이미 로그인된 상태 — 로그인 전 테스트 스킵")
        assert home.is_login_button_visible(), "로그인 버튼이 상단에 표시되지 않습니다"


# ============================================================
# [Depth1: 홈] [Depth2: 홈 화면 섹션] 노출 검증
# ============================================================
class TestHomeSections:
    """홈 화면 섹션 노출 검증"""

    def test_popular_live_section_visible(self, driver):
        """TC: 홈 화면 > '인기 LIVE' 섹션 타이틀 노출 확인"""
        home = HomePage(driver)
        assert home.is_live_section_visible(), "'인기 LIVE' 영역을 찾지 못했습니다"

    def test_popular_user_clip_section_visible(self, driver):
        """TC: 홈 화면 > '인기 유저 클립' 섹션 타이틀 노출 확인"""
        home = HomePage(driver)
        assert home.is_user_clip_section_visible(), "'인기 유저 클립' 영역을 찾지 못했습니다"

    def test_popular_upload_vod_section_visible(self, driver):
        """TC: 홈 화면 > '인기 업로드 VOD' 섹션 타이틀 노출 확인 (스크롤 필요)"""
        home = HomePage(driver)
        assert home.is_upload_vod_section_visible(), "'인기 업로드 VOD' 영역을 찾지 못했습니다"

    def test_popular_replay_section_visible(self, driver):
        """TC: 홈 화면 > '인기 다시보기' 섹션 타이틀 노출 확인 (스크롤 필요)"""
        home = HomePage(driver)
        assert home.is_replay_section_visible(), "'인기 다시보기' 영역을 찾지 못했습니다"


# ============================================================
# [Depth1: 홈] [Depth2: 상단 메뉴] 이동 검증
# ============================================================
class TestTopMenuNavigation:
    """상단 탭 메뉴 클릭 후 화면 전환 검증"""

    def test_click_live_menu(self, driver):
        """TC: 상단 메뉴 'LIVE' 탭 클릭 성공 확인"""
        home = HomePage(driver)
        assert home.click_live_menu(), "'LIVE' 메뉴 버튼 클릭 실패"

    def test_click_vod_menu(self, driver):
        """TC: 상단 메뉴 'VOD' 탭 클릭 성공 확인"""
        home = HomePage(driver)
        assert home.click_vod_menu(), "'VOD' 메뉴 버튼 클릭 실패"

    def test_click_esports_menu(self, driver):
        """TC: 상단 메뉴 'e스포츠' 탭 클릭 성공 확인"""
        home = HomePage(driver)
        assert home.click_esports_menu(), "'e스포츠' 메뉴 버튼 클릭 실패"

    def test_click_my_menu(self, driver):
        """TC: 상단 메뉴 'MY' 탭 클릭 성공 확인"""
        home = HomePage(driver)
        assert home.click_my_menu(), "'MY' 메뉴 버튼 클릭 실패"

    def test_click_settings_menu(self, driver):
        """TC: 상단 메뉴 '설정' 탭 클릭 성공 확인"""
        home = HomePage(driver)
        assert home.click_settings_menu(), "'설정' 메뉴 버튼 클릭 실패"

    def test_click_fourth_top_menu_button(self, driver):
        """TC: 4번째 상단 메뉴 버튼(LIVE) 클릭"""
        home = HomePage(driver)
        assert home.click_fourth_top_menu(), "4번째 상단 메뉴 버튼 클릭 실패"


# ============================================================
# [Depth1: 홈] [Depth2: 섹션 더보기 버튼] 클릭 검증
# ============================================================
class TestSectionMoreButton:
    """각 섹션 '더보기' 버튼 클릭 검증"""

    def test_live_more_button_clickable(self, driver):
        """TC: '인기 LIVE 더보기' 버튼 클릭 가능 확인"""
        home = HomePage(driver)
        assert home.click_live_more(), "'인기 LIVE 더보기' 버튼 클릭 실패"

    def test_clip_more_button_clickable(self, driver):
        """TC: '인기 유저 클립 더보기' 버튼 클릭 가능 확인"""
        home = HomePage(driver)
        assert home.click_clip_more(), "'인기 유저 클립 더보기' 버튼 클릭 실패"

    def test_vod_more_button_clickable(self, driver):
        """TC: '인기 업로드 VOD 더보기' 버튼 클릭 가능 확인"""
        home = HomePage(driver)
        assert home.click_vod_more(), "'인기 업로드 VOD 더보기' 버튼 클릭 실패"

    def test_replay_more_button_clickable(self, driver):
        """TC: '인기 다시보기 더보기' 버튼 클릭 가능 확인"""
        home = HomePage(driver)
        assert home.click_replay_more(), "'인기 다시보기 더보기' 버튼 클릭 실패"