import time
import subprocess
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
    
    time.sleep(5)
    
    print("Clicking settings via keyboard...")
    for _ in range(3):
        driver.press_left()
        time.sleep(0.5)
        focused_text = driver.cdp.evaluate("document.activeElement ? document.activeElement.textContent : ''")
        print(f"Focused after left: '{focused_text}'")
        if focused_text and any(m in focused_text for m in ["로그인", "검색", "홈", "LIVE", "VOD", "e스포츠", "MY", "설정"]):
            break
            
    for _ in range(10):
        driver.press_down()
        time.sleep(0.5)
        focused_text = driver.cdp.evaluate("document.activeElement ? document.activeElement.textContent : ''")
        print(f"Focused after down: '{focused_text}'")
        if "설정" in focused_text:
            driver.press_enter()
            break
            
    time.sleep(2)
    active_text = driver.cdp.evaluate("document.activeElement ? document.activeElement.textContent : ''")
    print(f"Active Element after 2s: '{active_text}'")

    driver.close()
    p.terminate()

if __name__ == '__main__':
    run_debug()
