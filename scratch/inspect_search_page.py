import time
import subprocess
from core.cdp_client import CDPClient

def run_debug():
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
        if "ws=" in line:
            ws_url = line.split("ws=")[1].strip()
            break
            
    if not ws_url:
        print("Failed to get ws url")
        return
        
    ws_url = "ws://" + ws_url
    cdp = CDPClient(ws_url)
    
    # 1. Click Search Button
    js_click_search = """
    (function(){
        let el = document.evaluate('//button[.="검색"]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        if(el) { el.click(); return true; }
        return false;
    })()
    """
    clicked = cdp.evaluate(js_click_search)
    print("Clicked search button:", clicked)
    time.sleep(3)
    
    # 2. Get inputs
    js_inputs = """
    (function(){
        let inputs = document.querySelectorAll('input');
        let res = [];
        for(let i=0; i<inputs.length; i++) {
            res.push({
                placeholder: inputs[i].placeholder,
                type: inputs[i].type,
                className: inputs[i].className
            });
        }
        return res;
    })()
    """
    inputs = cdp.evaluate(js_inputs)
    print("Inputs on search page:", inputs)
    
    # 3. Get all h3
    js_h3 = """
    (function(){
        let h3s = document.querySelectorAll('h3');
        let res = [];
        for(let i=0; i<h3s.length; i++) {
            res.push(h3s[i].textContent.trim());
        }
        return res;
    })()
    """
    h3s = cdp.evaluate(js_h3)
    print("H3s on search page:")
    for h in h3s:
        print(h.encode('utf-8', 'ignore').decode('utf-8'))
        
    p.terminate()

if __name__ == '__main__':
    run_debug()
