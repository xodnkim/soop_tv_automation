import time
import subprocess
from core.cdp_client import CDPClient
from pages.home_page import HomePage
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
    
    print("Navigating to Settings...")
    home = HomePage(driver)
    res = home.click_settings_menu()
    print("click_settings_menu returned:", res)
    
    time.sleep(3)
    
    # Check if settings page is loaded
    from pages.settings_page import SettingsPage
    settings = SettingsPage(driver)
    is_loaded = settings.is_loaded(timeout=5)
    print("Settings page loaded:", is_loaded)
    
    # Save a screenshot if not loaded
    if not is_loaded:
        driver.cdp.send("Page.enable")
        import base64
        res = driver.cdp.send("Page.captureScreenshot", {"format": "png"})
        if res and res.get("data"):
            with open("scratch/settings_debug.png", "wb") as f:
                f.write(base64.b64decode(res["data"]))
            print("Saved screenshot to scratch/settings_debug.png")
            
    driver.close()
    p.terminate()

if __name__ == '__main__':
    run_debug()
