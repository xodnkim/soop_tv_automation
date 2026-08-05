import csv
import urllib.request
import re
import json

url = "https://docs.google.com/spreadsheets/d/1Vs9QpBaKASekry0xOO-xYBJTe12eKqGbup5kUWty_Pc/export?format=csv&gid=327358501"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as r:
    raw = r.read().decode('utf-8-sig')

rows = list(csv.reader(raw.splitlines()))

# 실제 헤더 행: Row 5 (CSV idx 4)
# 실제 데이터: Row 6 ~ (CSV idx 5~)
DATA_START_IDX = 5  # 0-based index

# X 판별 패턴
X_PATTERNS = [
    r"QR코드", r"QR 코드",
    r"스트리머 -",
    r"채팅금지", r"저속모드", r"채팅창 얼리기",
    r"매니저 임명", r"매니저 해임",
    r"블랙리스트", r"무중단", r"방송재개", r"강제퇴장",
    r"전원 off", r"리모컨 \[전원\]", r"리모컨 \[홈\]", r"OS 홈",
    r"퀵뷰 뺏김", r"퀵뷰 뺏음", r"타 TV앱",
    r"오디오.*비디오.*싱크", r"프레임 확인",
    r"해외 VPN", r"유료광고포함표시",
]

FILE_MAP = {
    "앱 실행": "test_01_app_launch.py",
    "로그인": "test_login.py",
    "검색": "test_search.py",
    "홈": "test_home.py",
    "LIVE 플레이어": "test_live_player.py",
    "VOD 플레이어": "test_vod_player.py",
    "LIVE": "test_live_menu.py",
    "VOD": "test_vod_menu.py",
    "eSports": "test_esports_menu.py",
    "MY": "test_my_menu.py",
    "설정": "test_settings.py",
    "리스트 미리보기": "test_list_preview.py",
    "예외 케이스": "test_exceptions.py",
}

def resolve_file(topic):
    for key, val in FILE_MAP.items():
        if key in topic:
            return val
    return "test_misc.py"

updates = []
current_topic = ""

for i in range(DATA_START_IDX, len(rows)):
    row = rows[i]
    sheet_row = i + 1  # 1-based Google Sheet row number

    while len(row) < 18:
        row.append("")

    tc_no   = row[2].strip()  # C열 (index 2)
    title   = row[3].strip()  # D열
    depth1  = row[4].strip()  # E열
    depth2  = row[5].strip()  # F열
    depth3  = row[6].strip()  # G열
    precond = row[7].strip()  # H열
    step    = row[8].strip()  # I열
    expect  = row[9].strip()  # J열

    # M열: idx 12, N열: idx 13, Q열: idx 16
    existing_m = row[12].strip()
    existing_n = row[13].strip()
    existing_q = row[16].strip()

    if title:
        current_topic = title

    # 완전히 빈 데이터 행 스킵
    if not any([tc_no, title, depth1, depth2, precond, step, expect]):
        continue

    # 사용자가 이미 M열이나 N열에 판단한 내용이 있으면 존중 (빈칸일 때만 덮어씀)
    combined = " ".join([title, depth1, depth2, depth3, precond, step, expect])
    is_x = any(re.search(p, combined, re.IGNORECASE) for p in X_PATTERNS)

    m_val = existing_m
    n_val = existing_n
    q_val = existing_q

    if not existing_m:
        m_val = "X" if is_x else "O"
    
    if m_val == "O" and not existing_q:
        file_name = resolve_file(current_topic)
        import os
        file_path = f"d:/smarttv_auto/soop_tv/tests/{file_name}"
        if os.path.exists(file_path):
            q_val = f"{file_name} :: {tc_no}" if tc_no else file_name
        else:
            q_val = ""
    elif m_val == "X" and not existing_q:
        q_val = ""

    updates.append({"r": sheet_row, "m": m_val, "n": n_val, "q": q_val})

# Apps Script 생성
gs = f"""\
/**
 * SOOP TV 자동화 계획 - Google Sheets M열/Q열 일괄 업데이트 Apps Script
 *
 * [사용법]
 * 1. 스프레드시트 -> 확장 프로그램 -> Apps Script
 * 2. 기존 코드 전체 삭제 후 이 코드 붙여넣기
 * 3. [실행] 클릭 -> 권한 승인 -> 완료!
 */
function updateAutomationPlan() {{
  var ss    = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();

  var updates = {json.dumps(updates, ensure_ascii=False)};

  updates.forEach(function(item) {{
    var mCell = sheet.getRange(item.r, 13); // M열 = 13번째 열 (자동화 가능 여부)
    var nCell = sheet.getRange(item.r, 14); // N열 = 14번째 열 (불가능 이유)
    var qCell = sheet.getRange(item.r, 17); // Q열 = 17번째 열 (파일/TC)

    // 빈칸인 경우에만 덮어쓰도록 처리했지만, 스크립트 상에서 값을 전부 엎어치기함
    mCell.setValue(item.m);
    nCell.setValue(item.n);
    qCell.setValue(item.q);
  }});

  SpreadsheetApp.getUi().alert('완료! 총 ' + updates.length + '개 행 반영 완료.');
}}
"""

gs_path = "d:/smarttv_auto/soop_tv/update_sheet.gs"
with open(gs_path, "w", encoding="utf-8") as f:
    f.write(gs)

print(f"완료! 총 업데이트 행: {len(updates)}")
print(f"저장 위치: {gs_path}")
