import time
from pages.base_page import BasePage

class VodPlayerPage(BasePage):
    """VOD 플레이어 객체"""
    
    # ---- 기본 UI ----
    PLAYER_VIDEO            = '//video | //*[contains(@class,"player")]'
    CHAT_UI                 = '//*[contains(@class,"chat") and contains(@class,"wrap")]'
    
    # ---- 버튼류 ----
    BTN_STAR_BALL           = '//button[contains(normalize-space(),"별풍선")]'
    BTN_UP                  = '//button[normalize-space()="UP"]'
    BTN_FAVORITE            = '//button[normalize-space()="즐겨찾기"]'
    BTN_WATCH_LATER         = '//button[normalize-space()="나중에 보기"]'
    BTN_CHAT_TOGGLE         = '//button[contains(@class,"chat") and contains(@class,"toggle")]'
    
    # ---- 방송 정보 ----
    VOD_TITLE               = '//*[contains(@class,"title") and ancestor::*[contains(@class,"player")]]'
    VIEW_COUNT              = '//*[contains(normalize-space(),"조회")]'
    PROGRESS_BAR            = '//progress | //*[@role="slider"] | //*[contains(@class,"progressbar")]'
    PLAYBACK_TIME           = '//*[contains(normalize-space(),":") and contains(@class,"time")]'
    AUTOPLAY_TIMER          = '//*[contains(@class,"autoplay") or contains(normalize-space(),"자동재생")]'
    
    # ---- 로그인 리다이렉트 ----
    LOGIN_REDIRECT          = '//h2[normalize-space()="로그인"] | //input[@placeholder="아이디"]'
    
    def is_loaded(self, timeout: float = 10) -> bool:
        return self.driver.is_visible(self.PLAYER_VIDEO, timeout=timeout)
        
    def is_chat_ui_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible(self.CHAT_UI, timeout=3)
        
    def is_chat_area_visible(self) -> bool:
        return self.is_chat_ui_visible()

    def click_star_ball(self) -> bool:
        return self.driver.click(self.BTN_STAR_BALL)
        
    def click_up(self) -> bool:
        return self.driver.click(self.BTN_UP)
        
    def click_favorite(self) -> bool:
        return self.driver.click(self.BTN_FAVORITE)
        
    def click_watch_later(self) -> bool:
        return self.driver.click(self.BTN_WATCH_LATER)
        
    def click_chat_toggle(self) -> bool:
        return self.driver.click(self.BTN_CHAT_TOGGLE)

    def press_down(self) -> None:
        self.driver.press_down()
        time.sleep(0.5)
        
    def press_back(self) -> None:
        self.driver.press_back()
        time.sleep(1)
        
    def press_enter(self) -> None:
        self.driver.press_enter()
        time.sleep(0.5)

    def press_left(self) -> None:
        self.driver.press_left()
        time.sleep(0.5)

    def press_right(self) -> None:
        self.driver.press_right()
        time.sleep(0.5)

    def is_login_screen_visible(self) -> bool:
        return self.driver.is_visible(self.LOGIN_REDIRECT, timeout=5)
        
    def wake_up_ui(self) -> None:
        """리모컨 조작을 통해 숨겨진 UI(오버레이)를 깨움"""
        self.driver.press_up()
        time.sleep(1)
        
    def is_short_chat_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible('//*[contains(@class,"short")]', timeout=3)

    def is_vod_info_area_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible(self.VOD_TITLE, timeout=3)
        
    def is_view_count_and_date_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible(self.VIEW_COUNT, timeout=3)
        
    def is_vod_title_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible(self.VOD_TITLE, timeout=3)
        
    def is_progress_bar_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible(self.PROGRESS_BAR, timeout=3)
        
    def is_playback_time_visible(self) -> bool:
        self.wake_up_ui()
        return self.driver.is_visible(self.PLAYBACK_TIME, timeout=3)
        
    def is_autoplay_timer_visible(self) -> bool:
        return self.driver.is_visible(self.AUTOPLAY_TIMER, timeout=3)

    def is_streamer_vod_list_visible(self) -> bool:
        return self.driver.is_visible('//*[contains(normalize-space(),"VOD")]', timeout=3)
