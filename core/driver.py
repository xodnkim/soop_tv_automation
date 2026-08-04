"""
driver.py
- CDP 세션을 감싸는 상위 드라이버 (플랫폼 공용)
- 최상단 고정 레이어(Fixed Overlay) 방식으로 TV 화면에 하이라이트 박스 100% 표시 보장
"""
import json
import time

from core.cdp_client import CDPClient, get_page_ws_url
from config import config


class SoopDriver:
    def __init__(self, port_or_url):
        if isinstance(port_or_url, str) and port_or_url.startswith("ws"):
            ws_url = port_or_url
        else:
            ws_url = get_page_ws_url(f"http://localhost:{port_or_url}")
        self.cdp = CDPClient(ws_url)
        self.cdp.send("Page.enable")
        self.cdp.send("Runtime.enable")

    def close(self):
        self.cdp.close()

    # ---------- TV 화면 최상단 하이라이트 레이어 생성 (100% 보장) ----------
    def highlight_element(self, xpath: str, duration_sec: float = 0.8):
        """
        DOM 최상단(body)에 z-index: 999999의 고정 오버레이 레이어를 생성하여
        대상 요소의 뷰포트 위치와 크기에 맞게 피복 (앱 내부 CSS 스코프 무관하게 100% 표시)
        """
        try:
            xpath_js = json.dumps(xpath)
            highlight_js = f"""
            (function() {{
                var el = document.evaluate({xpath_js}, document, null,
                                            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (!el) return false;

                // 요소의 뷰포트 기준 위치 및 크기 계산
                var rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return false;

                // 화면 최상단 하이라이트 오버레이 생성
                var overlay = document.createElement('div');
                overlay.id = '__auto_highlight_overlay__';
                overlay.style.position = 'fixed';
                overlay.style.left = rect.left + 'px';
                overlay.style.top = rect.top + 'px';
                overlay.style.width = rect.width + 'px';
                overlay.style.height = rect.height + 'px';
                overlay.style.border = '4px solid #ff0055';               // 핫핑크 형광 테두리
                overlay.style.backgroundColor = 'rgba(255, 0, 85, 0.45)'; // 반투명 핫핑크 배경
                overlay.style.boxShadow = '0 0 20px rgba(255, 0, 85, 0.9)';// 글로우 효과
                overlay.style.zIndex = '999999';                           // 최상단 레이어 강제
                overlay.style.pointerEvents = 'none';                      // 클릭 이벤트 투과
                overlay.style.boxSizing = 'border-box';

                document.body.appendChild(overlay);

                // 지정된 시간(초) 후 오버레이 레이어 제거
                setTimeout(function() {{
                    var target = document.getElementById('__auto_highlight_overlay__');
                    if (target && target.parentNode) {{
                        target.parentNode.removeChild(target);
                    }}
                }}, {int(duration_sec * 1000)});

                return true;
            }})()
            """
            self.cdp.evaluate(highlight_js)
            time.sleep(duration_sec)  # 눈으로 확인할 시간 대기
        except Exception:
            pass

    # ---------- 조회 ----------
    def find(self, xpath: str, timeout: float = config.ELEMENT_WAIT_TIMEOUT, scroll_into_view: bool = False, highlight: bool = True):
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
                # 요소를 정상 감지한 경우 TV 화면상 위치에 최상단 하이라이트 박스 노출
                if highlight:
                    self.highlight_element(xpath, duration_sec=0.8)
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
        """element.click() + 리모컨 확인(Enter) 키 이벤트를 함께 전송"""
        info = self.find(xpath, timeout=timeout, scroll_into_view=True, highlight=True)
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
        info = self.find(xpath, timeout=timeout, scroll_into_view=True, highlight=True)
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