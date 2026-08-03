"""
test_home.py
- 홈 화면 자동화 테스트 케이스
"""
from pages.home_page import HomePage

def test_home_label_visible(driver):
    home = HomePage(driver)
    assert home.is_loaded(), "'홈' 라벨을 찾지 못했습니다"
    assert "홈" in home.home_label_text(), f"텍스트 불일치: '{home.home_label_text()}'"

def test_popular_live_section_visible(driver):
    home = HomePage(driver)
    assert home.is_live_section_visible(), "'인기 LIVE' 영역을 찾지 못했습니다"

def test_popular_user_clip_section_visible(driver):
    home = HomePage(driver)
    assert home.is_user_clip_section_visible(), "'인기 유저 클립' 영역을 찾지 못했습니다"

def test_popular_upload_vod_section_visible(driver):
    home = HomePage(driver)
    assert home.is_upload_vod_section_visible(), "'인기 업로드 VOD' 영역을 찾지 못했습니다"

def test_click_fourth_top_menu_button(driver):
    home = HomePage(driver)
    assert home.click_fourth_top_menu(), "4번째 상단 메뉴 버튼 클릭 실패"