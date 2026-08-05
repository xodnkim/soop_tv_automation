import time
from pages.base_page import BasePage

class LivePage(BasePage):
    """LIVE 메뉴 페이지 객체"""
    
    # ---- 기본 UI ----
    LIVE_LABEL          = '//h2[normalize-space()="LIVE"]'
    
    # ---- 카테고리 ----
    # 이미지 src에 category_img를 포함하는 버튼을 카테고리로 간주
    CATEGORY_LIST       = '//button[.//img[contains(@src, "category_img")]]'
    
    # ---- 더보기 버튼 ----
    BTN_MORE            = '//button[contains(normalize-space(), "더보기")]'
    
    def is_loaded(self, timeout: float = 10) -> bool:
        """LIVE 탭 진입 완료 대기"""
        return self.driver.is_visible(self.LIVE_LABEL, timeout=timeout)
        
    def is_first_category_focused(self) -> bool:
        """
        '전체' 카테고리가 포커스되어 있는지 확인 (live_001)
        """
        js = """
        (function(){
            var el = document.activeElement;
            return el ? el.textContent.trim() : '';
        })()
        """
        text = self.driver.cdp.evaluate(js)
        return text == "전체"
        
    def get_category_count(self) -> int:
        """
        노출된 카테고리 버튼의 총 개수 (live_002)
        """
        nodes = self.driver.cdp.evaluate(
            '(function(){ '
            'var els = document.evaluate(`//button[.//img[contains(@src, "category_img")]]`, '
            'document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null); '
            'return els.snapshotLength; '
            '})()'
        )
        return int(nodes) if nodes else 0

    def navigate_to_last_category(self, count: int) -> None:
        """
        현재 첫번째 카테고리에서 오른쪽 방향키를 눌러 마지막 카테고리로 이동
        """
        for _ in range(count - 1):
            self.driver.press_right()
            time.sleep(0.3)
            
    def click_last_category_right(self) -> bool:
        """
        마지막 카테고리에서 오른쪽 방향키를 눌렀을 때 처음으로 순환되는지 확인 (live_003)
        """
        self.driver.press_right()
        time.sleep(0.5)
        return self.is_first_category_focused()

    def click_first_category(self) -> bool:
        """
        현재 포커스된(첫번째) 카테고리 클릭 (live_004)
        """
        self.driver.press_enter()
        time.sleep(1)
        return True

    def is_more_list_visible(self) -> bool:
        """
        카테고리 클릭 후 더보기(또는 상세) 페이지가 노출되는지 확인 (live_004)
        """
        # 더보기 페이지에 진입하면 보통 전체 더보기 버튼들이 리스트 형태로 노출되거나 
        # LIVE/VOD 방송 리스트가 노출됨
        return self.driver.is_visible('//button[.//em]', timeout=5)
        
    def is_live_list_visible_in_section(self) -> bool:
        """
        LIVE 섹션 내 방송 리스트(썸네일 등) 노출 확인 (live_015)
        """
        # 시청자수 <em>이 포함된 썸네일 버튼이 1개 이상 노출되는지 확인
        return self.driver.is_visible('//button[.//em]', timeout=5)
