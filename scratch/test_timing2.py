import time
import subprocess
import json
from core.cdp_client import CDPClient
from core.driver import SoopDriver

def run_debug():
    p = subprocess.Popen(
        ['ares-inspect.cmd', '-d', 'LG_SMART', 'com.soop.stg.app'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    
    ws_url = None
    for _ in range(30):
        line = p.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        if "ws=" in line:
            ws_url = line.split("ws=")[1].strip()
            break
            
    if not ws_url:
        print("Failed to get ws url")
        return
        
    ws_url = "ws://" + ws_url
    driver = SoopDriver(ws_url)
    
    print("Reloading page...")
    driver.cdp.evaluate("window.location.reload();")
    
    print("Waiting for 홈...")
    deadline = time.time() + 8
    while time.time() < deadline:
        time.sleep(0.5)
        try:
            val = driver.cdp.evaluate(
                '(function(){'
                'var el = document.evaluate("//h2[normalize-space()=\'홈\']",'
                ' document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;'
                'return el ? el.textContent : null;'
                '})()'
            )
            if val:
                break
        except Exception:
            pass
    
    time.sleep(2)
    
    print("Clicking settings immediately (via mouse_click)...")
    xpath = '//button[.="설정"]'
    info = driver.find(xpath, timeout=10, scroll_into_view=True)
    if info and info.get("found"):
        coord_js = f"""
        (function() {{
            var el = document.evaluate({json.dumps(xpath)}, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if(!el) return null;
            var rect = el.getBoundingClientRect();
            return {{x: rect.left + rect.width/2, y: rect.top + rect.height/2}};
        }})()
        """
        coord = driver.cdp.evaluate(coord_js)
        if isinstance(coord, dict) and 'x' in coord:
            x, y = coord['x'], coord['y']
            driver.cdp.send("Input.dispatchMouseEvent", {
                "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1
            })
            time.sleep(0.05)
            driver.cdp.send("Input.dispatchMouseEvent", {
                "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1
            })
            print("Mouse clicked")
            
    time.sleep(2)
    active_text = driver.cdp.evaluate("document.activeElement ? document.activeElement.textContent : ''")
    print(f"Active Element after 2s: '{active_text}'")
    active_html = driver.cdp.evaluate("document.activeElement ? document.activeElement.outerHTML : ''")
    print(f"Active Element HTML: {active_html}")

    driver.close()
    p.terminate()

if __name__ == '__main__':
    run_debug()
