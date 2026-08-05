import time
import subprocess
import json
from core.cdp_client import CDPClient
from core.driver import SoopDriver
from pages.home_page import HomePage

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
    
    # Reload page to simulate test environment
    print("Reloading page...")
    driver.cdp.evaluate("window.location.reload();")
    time.sleep(5)
    
    # Try mouse click
    xpath = '//button[.="설정"]'
    
    print("Trying mouse click on Settings...")
    info = driver.find(xpath, timeout=10, scroll_into_view=True)
    if info and info.get("found"):
        js = f"""
        (function() {{
            var el = document.evaluate({json.dumps(xpath)}, document, null,
                                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if(!el) return null;
            var rect = el.getBoundingClientRect();
            return {{x: rect.left + rect.width/2, y: rect.top + rect.height/2}};
        }})()
        """
        coord = driver.cdp.evaluate(js)
        if coord:
            x, y = coord['x'], coord['y']
            print(f"Clicking at {x}, {y}")
            driver.cdp.send("Input.dispatchMouseEvent", {
                "type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1
            })
            time.sleep(0.1)
            driver.cdp.send("Input.dispatchMouseEvent", {
                "type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1
            })
            print("Mouse click sent")
        else:
            print("Coord not found")
    else:
        print("Settings button not found")
        
    time.sleep(3)
    
    # Check if we are on Settings
    from pages.settings_page import SettingsPage
    settings = SettingsPage(driver)
    loaded = settings.is_loaded(timeout=3)
    print("Settings page loaded via mouse_click?", loaded)
    
    driver.close()
    p.terminate()

if __name__ == '__main__':
    run_debug()
