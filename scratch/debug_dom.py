import time
import subprocess
from core.cdp_client import CDPClient

def run_debug():
    # Start ares-inspect
    print("Starting ares-inspect...")
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
        print("[INSPECT]", line.strip())
        if "ws=" in line:
            ws_url = line.split("ws=")[1].strip()
            break
            
    if not ws_url:
        print("Failed to get ws url")
        return
        
    print("Got ws_url:", ws_url)
    ws_url = "ws://" + ws_url
    
    cdp = CDPClient(ws_url)
    
    # Get all buttons
    js = """
    (function(){
        let btns = document.querySelectorAll('button');
        let res = [];
        for(let i=0; i<btns.length; i++) {
            res.push({
                text: btns[i].textContent.trim(),
                className: btns[i].className,
                aria: btns[i].getAttribute('aria-label')
            });
        }
        return res;
    })()
    """
    btns = cdp.evaluate(js)
    print("Found buttons:")
    for b in btns:
        print(b)
        
    p.terminate()

if __name__ == '__main__':
    run_debug()
