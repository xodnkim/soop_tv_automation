"""
test_search.py
- 검색 화면 및 최근 검색어 검증 테스트 케이스
"""
from pages.home_page import HomePage

def test_search_and_verify_recent_keyword(driver):
    home = HomePage(driver)
    target_keyword = "꾸리꾸리"

    search_page = home.open_search()
    assert search_page.is_loaded(), "검색 화면 로딩 실패"

    search_page.search(target_keyword)

    assert search_page.has_recent_keyword(target_keyword), (
        f"최근 검색어 영역에 '{target_keyword}' 키워드가 존재하지 않습니다."
    )