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
    
    html = driver.cdp.evaluate("document.body.innerHTML")
    
    import re
    # Extract all img tags
    imgs = re.findall(r'<img[^>]+>', html)
    for img in imgs:
        print(img)
        
    # Also extract text around QR
    print(driver.cdp.evaluate("document.body.innerText"))

    driver.close()
    p.terminate()

if __name__ == '__main__':
    run_debug()
