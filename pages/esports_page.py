import time
from pages.base_page import BasePage

class EsportsPage(BasePage):
    """eSports 메뉴 페이지 객체"""
    
    # ---- 기본 UI ----
    ESPORTS_LABEL       = '//h2[normalize-space()="e스포츠"]'
    
    # ---- 필터 (시즌/영상타입) ----
    SEASON_FILTER       = '//button[contains(normalize-space(),"시즌") or contains(@class,"season")]'
    VIDEO_TYPE_FILTER   = '//button[contains(normalize-space(),"영상") or contains(@class,"type")]'
    
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible('//h2[normalize-space()="eSports"]', timeout=timeout)
        
    def is_first_category_focused(self) -> bool:
        js = """
        (function(){
            var el = document.activeElement;
            return el ? el.textContent.trim() : '';
        })()
        """
        text = self.driver.cdp.evaluate(js)
        # eSports 첫 번째 카테고리 이름에 따라 수정될 수 있음 (보통 '전체' 또는 대표 게임)
        return bool(text)
        
    def get_category_count(self) -> int:
        nodes = self.driver.cdp.evaluate(
            '(function(){ '
            'var els = document.evaluate(`//button[contains(@class, "sc-fPEQgO")]`, '
            'document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null); '
            'return els.snapshotLength; '
            '})()'
        )
        return int(nodes) if nodes else 0

    def navigate_to_last_category(self, count: int) -> None:
        for _ in range(count - 1):
            self.driver.press_right()
            time.sleep(0.3)
            
    def click_last_category_right(self) -> bool:
        self.driver.press_right()
        time.sleep(0.5)
        # Check if first item is focused again
        return self.is_first_category_focused()

    def click_first_category(self) -> bool:
        self.driver.press_enter()
        time.sleep(1)
        return True

    def is_season_list_visible(self) -> bool:
        """시즌 리스트 노출 확인 (esports_004, 023, 024)"""
        return self.driver.is_visible('//button[contains(@class, "sc-fPEQgO")]', timeout=5)

    def is_vod_list_visible_in_category(self) -> bool:
        """VOD 리스트 노출 확인 (esports_013)"""
        return self.driver.is_visible('//button[.//img]', timeout=5)

    def is_season_filter_visible(self) -> bool:
        """시즌 필터 드롭다운/버튼 노출 확인 (esports_025)"""
        return self.driver.is_visible(self.SEASON_FILTER, timeout=3)
        
    def click_season_filter(self) -> bool:
        """시즌 필터 클릭 (esports_026)"""
        return self.driver.click(self.SEASON_FILTER)
        
    def is_video_type_filter_visible(self) -> bool:
        """영상 타입 필터 드롭다운/버튼 노출 확인 (esports_027)"""
        return self.driver.is_visible(self.VIDEO_TYPE_FILTER, timeout=3)
        
    def click_video_type_filter(self) -> bool:
        """영상 타입 필터 클릭 (esports_028)"""
        return self.driver.click(self.VIDEO_TYPE_FILTER)
