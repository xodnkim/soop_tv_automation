import time
from pages.base_page import BasePage

class VodPage(BasePage):
    """VOD 메뉴 페이지 객체"""
    
    # ---- 기본 UI ----
    VOD_LABEL          = '//h2[normalize-space()="VOD"]'
    
    # ---- 카테고리 ----
    CATEGORY_LIST       = '//button[.//img[contains(@src, "category_img")]]'
    
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.VOD_LABEL, timeout=timeout)
        
    def is_first_category_focused(self) -> bool:
        js = """
        (function(){
            var el = document.activeElement;
            return el ? el.textContent.trim() : '';
        })()
        """
        text = self.driver.cdp.evaluate(js)
        return text == "전체"
        
    def get_category_count(self) -> int:
        nodes = self.driver.cdp.evaluate(
            '(function(){ '
            'var els = document.evaluate(`//button[.//img[contains(@src, "category_img")]]`, '
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
        return self.is_first_category_focused()

    def click_first_category(self) -> bool:
        self.driver.press_enter()
        time.sleep(1)
        return True

    def is_more_list_visible(self) -> bool:
        return self.driver.is_visible('//button[.//img]', timeout=5)
        
    def is_vod_list_visible_in_section(self) -> bool:
        # VOD는 조회수나 다른 정보가 포함된 썸네일 노출
        return self.driver.is_visible('//button[.//img]', timeout=5)
