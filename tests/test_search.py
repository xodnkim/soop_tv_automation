"""
test_search.py
- 시나리오 1: LNB 돋보기(검색) 클릭 -> 키워드 입력 -> 리모컨 확인(Enter) 제출 -> Pass
- 시나리오 2: 이어서 최근 검색어 영역에 해당 키워드가 정상 등록되어 존재하는지 검증 (Pass)
"""
import pytest
from pages.home_page import HomePage


def test_search_and_verify_recent_keyword(driver):
    home = HomePage(driver)
    target_keyword = "꾸리꾸리"

    # ===== [시나리오 1] LNB 돋보기 클릭 -> '테스트' 입력 -> 확인 키 제출 =====
    print("\n[Test] 1. LNB 검색(돋보기) 버튼 클릭")
    search_page = home.open_search()
    assert search_page.is_loaded(), "검색 화면이 로딩되지 않았습니다"

    print(f"[Test] 1. 입력창에 '{target_keyword}' 입력 및 리모컨 확인 키 전송")
    search_page.search(target_keyword)

    print("[Test] 1. 검색 제출 완료 -> Pass")

    # ===== [시나리오 2] 이어서 최근 검색어 영역에 입력한 키워드가 존재하는지 검증 =====
    print(f"[Test] 2. 최근 검색어 목록에 '{target_keyword}' 존재 여부 검증")
    assert search_page.has_recent_keyword(target_keyword), (
        f"최근 검색어 영역에 '{target_keyword}' 키워드가 존재하지 않습니다."
    )
    print(f"[Test] 2. 최근 검색어 '{target_keyword}' 존재 확인 완료 -> Pass")
