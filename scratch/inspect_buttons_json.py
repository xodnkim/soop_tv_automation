import time
import json
import subprocess
from core.cdp_client import CDPClient

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
                aria: btns[i].getAttribute('aria-label'),
                id: btns[i].id
            });
        }
        return res;
    })()
    """
    btns = cdp.evaluate(js)
    with open('scratch/buttons_debug.json', 'w', encoding='utf-8') as f:
        json.dump(btns, f, ensure_ascii=False, indent=2)
        
    print("Saved to scratch/buttons_debug.json")
    p.terminate()

if __name__ == '__main__':
    run_debug()
