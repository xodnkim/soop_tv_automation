import time
from pages.base_page import BasePage

class MyTabPage(BasePage):
    """MY 메뉴 페이지 객체"""
    
    # ---- 기본 UI ----
    MY_LABEL                = '//h2[normalize-space()="MY"]'
    
    # ---- 섹션 타이틀 ----
    FAVORITE_ALL_SECTION    = '//*[contains(normalize-space(),"즐겨찾기 전체")]'
    SUBSCRIBED_LIVE_SECTION = '//*[contains(normalize-space(),"구독한 스트리머의 LIVE")]'
    SUBSCRIBED_VOD_SECTION  = '//*[contains(normalize-space(),"구독한 스트리머의 VOD")]'
    FAVORITED_LIVE_SECTION  = '//*[contains(normalize-space(),"즐겨찾기 한 LIVE")]'
    FAVORITED_CLIP_SECTION  = '//*[contains(normalize-space(),"즐겨찾기 한 유저클립")]'
    FAVORITED_VOD_SECTION   = '//*[contains(normalize-space(),"즐겨찾기 한 업로드 VOD")]'
    FAN_LIVE_SECTION        = '//*[contains(normalize-space(),"팬 가입한 스트리머의 LIVE")]'
    FAN_VOD_SECTION         = '//*[contains(normalize-space(),"팬 가입한 스트리머의 VOD")]'
    RECENT_LIVE_SECTION     = '//*[contains(normalize-space(),"최근 본 LIVE")]'
    RECENT_VOD_SECTION      = '//*[contains(normalize-space(),"최근 본 VOD")]'
    RECOMMEND_SECTION       = '//*[contains(normalize-space(),"추천 스트리머")]'
    WATCH_LATER_SECTION     = '//*[contains(normalize-space(),"나중에 보기")]'
    UP_VOD_SECTION          = '//*[contains(normalize-space(),"UP 누른 VOD")]'
    
    # ---- 더보기 버튼 ----
    BTN_FAVORITE_MORE       = '//button[contains(normalize-space(),"즐겨찾기 전체 더보기")]'
    BTN_SUBSCRIBED_LIVE_MORE= '//button[contains(normalize-space(),"구독한 스트리머의 LIVE 더보기")]'
    BTN_SUBSCRIBED_VOD_MORE = '//button[contains(normalize-space(),"구독한 스트리머의 VOD 더보기")]'
    BTN_FAVORITED_LIVE_MORE = '//button[contains(normalize-space(),"즐겨찾기 한 LIVE 더보기")]'
    BTN_FAVORITED_CLIP_MORE = '//button[contains(normalize-space(),"즐겨찾기 한 유저클립 더보기")]'
    BTN_FAVORITED_VOD_MORE  = '//button[contains(normalize-space(),"즐겨찾기 한 업로드 VOD 더보기")]'
    BTN_FAN_LIVE_MORE       = '//button[contains(normalize-space(),"팬 가입한 스트리머의 LIVE 더보기")]'
    BTN_FAN_VOD_MORE        = '//button[contains(normalize-space(),"팬 가입한 스트리머의 VOD 더보기")]'
    BTN_RECENT_LIVE_MORE    = '//button[contains(normalize-space(),"최근 본 LIVE 더보기")]'
    BTN_RECENT_VOD_MORE     = '//button[contains(normalize-space(),"최근 본 VOD 더보기")]'
    BTN_WATCH_LATER_MORE    = '//button[contains(normalize-space(),"나중에 보기 더보기")]'
    BTN_UP_VOD_MORE         = '//button[contains(normalize-space(),"UP 누른 VOD 더보기")]'
    
    # ---- 즐겨찾기 스트리머 컨텍스트 메뉴 ----
    CONTEXT_MENU            = '//*[contains(@class,"context") or contains(@class,"menu")]'
    BTN_CONTEXT_PROFILE     = '//button[contains(normalize-space(),"방송국")]'
    BTN_CONTEXT_JOIN_LIVE   = '//button[contains(normalize-space(),"LIVE 참여")]'
    BTN_CONTEXT_FAV_DEL     = '//button[contains(normalize-space(),"즐겨찾기 삭제")]'
    
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.MY_LABEL, timeout=timeout)
        
    def _is_section_visible(self, xpath: str) -> bool:
        return bool(self.driver.find(xpath, scroll_into_view=True))
        
    def _click_more(self, xpath: str) -> bool:
        return self.driver.click(xpath, scroll_into_view=True)

    # 섹션 노출 확인 메서드들
    def is_favorite_all_section_visible(self) -> bool:
        return self._is_section_visible(self.FAVORITE_ALL_SECTION)
        
    def is_subscribed_live_section_visible(self) -> bool:
        return self._is_section_visible(self.SUBSCRIBED_LIVE_SECTION)
        
    def is_subscribed_vod_section_visible(self) -> bool:
        return self._is_section_visible(self.SUBSCRIBED_VOD_SECTION)
        
    def is_favorited_live_section_visible(self) -> bool:
        return self._is_section_visible(self.FAVORITED_LIVE_SECTION)
        
    def is_favorited_clip_section_visible(self) -> bool:
        return self._is_section_visible(self.FAVORITED_CLIP_SECTION)
        
    def is_favorited_vod_section_visible(self) -> bool:
        return self._is_section_visible(self.FAVORITED_VOD_SECTION)
        
    def is_fan_live_section_visible(self) -> bool:
        return self._is_section_visible(self.FAN_LIVE_SECTION)
        
    def is_fan_vod_section_visible(self) -> bool:
        return self._is_section_visible(self.FAN_VOD_SECTION)
        
    def is_recent_live_section_visible(self) -> bool:
        return self._is_section_visible(self.RECENT_LIVE_SECTION)
        
    def is_recent_vod_section_visible(self) -> bool:
        return self._is_section_visible(self.RECENT_VOD_SECTION)
        
    def is_recommend_streamer_section_visible(self) -> bool:
        return self._is_section_visible(self.RECOMMEND_SECTION)
        
    def is_watch_later_section_visible(self) -> bool:
        return self._is_section_visible(self.WATCH_LATER_SECTION)
        
    def is_up_vod_section_visible(self) -> bool:
        return self._is_section_visible(self.UP_VOD_SECTION)

    # 더보기 버튼 노출 확인
    def is_favorite_more_button_visible(self) -> bool:
        return self._is_section_visible(self.BTN_FAVORITE_MORE)

    # 더보기 클릭 메서드들
    def click_favorite_more(self) -> bool:
        return self._click_more(self.BTN_FAVORITE_MORE)
        
    def click_subscribed_live_more(self) -> bool:
        return self._click_more(self.BTN_SUBSCRIBED_LIVE_MORE)
        
    def click_subscribed_vod_more(self) -> bool:
        return self._click_more(self.BTN_SUBSCRIBED_VOD_MORE)
        
    def click_favorited_live_more(self) -> bool:
        return self._click_more(self.BTN_FAVORITED_LIVE_MORE)
        
    def click_favorited_clip_more(self) -> bool:
        return self._click_more(self.BTN_FAVORITED_CLIP_MORE)
        
    def click_favorited_vod_more(self) -> bool:
        return self._click_more(self.BTN_FAVORITED_VOD_MORE)
        
    def click_fan_live_more(self) -> bool:
        return self._click_more(self.BTN_FAN_LIVE_MORE)
        
    def click_fan_vod_more(self) -> bool:
        return self._click_more(self.BTN_FAN_VOD_MORE)
        
    def click_recent_live_more(self) -> bool:
        return self._click_more(self.BTN_RECENT_LIVE_MORE)
        
    def click_recent_vod_more(self) -> bool:
        return self._click_more(self.BTN_RECENT_VOD_MORE)
        
    def click_watch_later_more(self) -> bool:
        return self._click_more(self.BTN_WATCH_LATER_MORE)
        
    def click_up_vod_more(self) -> bool:
        return self._click_more(self.BTN_UP_VOD_MORE)

    # 즐겨찾기 스트리머 정보 (my_002~003)
    def get_streamer_info(self) -> bool:
        """스트리머 썸네일 정보 표시 확인"""
        return self.driver.is_visible('//button[.//img]', timeout=3)
        
    def click_first_streamer(self) -> bool:
        """첫 번째 즐겨찾기 스트리머 롱프레스 (또는 클릭)"""
        # TV 앱의 경우 롱프레스 기능이 있다면 이를 호출하거나, 일단 클릭 수행
        return self.driver.click('//button[.//img]')
        
    def is_context_menu_visible(self) -> bool:
        """롱프레스 시 나타나는 컨텍스트 메뉴 확인"""
        return self.driver.is_visible(self.BTN_CONTEXT_PROFILE, timeout=3)
        
    def is_live_join_button_in_menu(self) -> bool:
        return self.driver.is_visible(self.BTN_CONTEXT_JOIN_LIVE, timeout=2)
        
    def is_favorite_delete_button(self) -> bool:
        return self.driver.is_visible(self.BTN_CONTEXT_FAV_DEL, timeout=2)
        
    def click_favorite_delete(self) -> bool:
        return self.driver.click(self.BTN_CONTEXT_FAV_DEL)
        
    def is_delete_toast_visible(self) -> bool:
        """즐겨찾기 삭제 토스트 노출 확인"""
        # 토스트 메시지 클래스 확인
        return self.driver.is_visible('//*[contains(normalize-space(),"삭제")]', timeout=3)
