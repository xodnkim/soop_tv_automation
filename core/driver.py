"""
driver.py
- CDP 세션 하나를 감싸는 상위 드라이버.
- Page Object들은 이 드라이버의 메서드(find/click/type_text 등)만 호출하고,
  XPath 평가/JS 실행 같은 CDP 세부사항은 몰라도 되도록 캡슐화한다.
  (Selenium의 WebDriver 역할과 동일한 포지션)
"""
import json
import time

from core.cdp_client import CDPClient, get_page_ws_url
from config import config


class SoopDriver:
    def __init__(self, port: int):
        ws_url = get_page_ws_url(f"http://localhost:{port}")
        self.cdp = CDPClient(ws_url)
        self.cdp.send("Page.enable")
        self.cdp.send("Runtime.enable")

    def close(self):
        self.cdp.close()

    # ---------- 조회 ----------
    def find(self, xpath: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT, scroll_into_view: bool = False):
        """xpath로 요소를 찾아 {found, text, width, height}를 반환 (최대 timeout초 재시도)"""
        xpath_js = json.dumps(xpath)
        scroll_code = "el.scrollIntoView({block: 'center'});" if scroll_into_view else ""
        expression = f"""
        (function() {{
            var el = document.evaluate({xpath_js}, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (!el) return {{found: false}};
            {scroll_code}
            var rect = el.getBoundingClientRect();
            return {{
                found: true,
                text: (el.textContent || '').trim(),
                width: rect.width,
                height: rect.height
            }};
        }})()
        """
        deadline = time.time() + timeout
        last = None
        while time.time() < deadline:
            last = self.cdp.evaluate(expression)
            if last and last.get("found") and last.get("width", 0) > 0 and last.get("height", 0) > 0:
                return last
            time.sleep(0.3)
        return last

    def wait_for(self, xpath: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT) -> bool:
        """지정한 xpath 요소가 화면에 나타날 때까지 스마트 폴링 대기 (Explicit Wait)"""
        info = self.find(xpath, timeout=timeout)
        return bool(info and info.get("found"))

    def is_visible(self, xpath: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT) -> bool:
        result = self.find(xpath, timeout=timeout)
        return bool(result and result.get("found"))


    def text_of(self, xpath: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT) -> str:
        result = self.find(xpath, timeout=timeout)
        return (result or {}).get("text", "")

    # ---------- 조작 ----------
    def click(self, xpath: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT) -> bool:
        """element.click() + 리모컨 확인(Enter) 키 이벤트를 함께 전송 (앱 구현 방식 무관하게 커버)"""
        info = self.find(xpath, timeout=timeout, scroll_into_view=True)
        if not (info and info.get("found")):
            return False

        xpath_js = json.dumps(xpath)
        click_js = f"""
        (function() {{
            var el = document.evaluate({xpath_js}, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (!el) return false;
            el.scrollIntoView({{block: 'center'}});
            el.focus();
            el.click();
            return true;
        }})()
        """
        self.cdp.evaluate(click_js)
        self.press_enter()
        return True

    def type_text(self, xpath: str, text: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT):
        """React 컨트롤드 인풋 대응: 네이티브 setter로 값 주입 + input/change 이벤트 강제 발생"""
        info = self.find(xpath, timeout=timeout, scroll_into_view=True)
        if not (info and info.get("found")):
            return False, None

        xpath_js = json.dumps(xpath)
        text_js = json.dumps(text)
        input_js = f"""
        (function() {{
            var el = document.evaluate({xpath_js}, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (!el) return null;
            el.focus();
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(el, {text_js});
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return el.value;
        }})()
        """
        result_value = self.cdp.evaluate(input_js)
        return (result_value == text), result_value

    def press_enter(self):
        """리모컨 확인(OK) 버튼과 동일한 Enter 키 이벤트 전송"""
        params = {"type": "keyDown", "windowsVirtualKeyCode": 13, "key": "Enter", "code": "Enter"}
        self.cdp.send("Input.dispatchKeyEvent", params)
        params["type"] = "keyUp"
        self.cdp.send("Input.dispatchKeyEvent", params)
