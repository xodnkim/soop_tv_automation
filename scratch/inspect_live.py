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
    
    # Navigate to LIVE tab
    from pages.home_page import HomePage
    home = HomePage(driver)
    print("Navigating to LIVE menu...")
    home.click_live_menu()
    
    time.sleep(3)
    
    html = driver.cdp.evaluate("document.body.innerHTML")
    with open("scratch/live_menu_html.txt", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved LIVE menu HTML")
        
    driver.close()
    p.terminate()

if __name__ == '__main__':
    run_debug()
