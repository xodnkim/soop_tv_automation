# SOOP Tizen TV 자동화 테스트 (POM 구조)

Samsung Tizen TV에서 실행 중인 SOOP 앱을 CDP(Chrome DevTools Protocol)로 제어해
검증하는 pytest 기반 자동화 테스트 프로젝트입니다.

## 디렉토리 구조

```
soop_tv_automation/
├── config/
│   └── config.py          # TV IP, 앱 ID, 타임아웃 등 환경설정 (환경변수로 오버라이드 가능)
├── core/
│   ├── cdp_client.py       # Page/Runtime 도메인 기반 저수준 CDP 클라이언트 (websocket 직통)
│   ├── tv_controller.py    # sdb 레벨 제어: TV 연결 / 앱 종료·실행 / 포트 포워딩
│   └── driver.py           # CDP 세션을 감싸는 상위 드라이버 (find/click/type_text 등)
├── pages/
│   ├── base_page.py         # 모든 Page Object의 공통 부모
│   ├── home_page.py         # 홈 화면 locator + 동작
│   └── search_page.py       # 검색 화면 locator + 동작
├── tests/
│   ├── conftest.py          # 세션 드라이버 준비, 테스트별 녹화/실패캡처
│   ├── test_home.py         # 홈 화면 요소 검증
│   └── test_search.py       # 검색 시나리오 (페이지 전환 포함)
├── test_results/            # 실행 결과물 (영상/스크린샷) - git 추적 안 함
├── pytest.ini
├── requirements.txt
└── README.md
```

## 레이어 구조 (왜 이렇게 나눴는가)

```
tests/          "무엇을 검증할지" 만 다룸 (비즈니스 시나리오)
   ↓ 호출
pages/          "이 화면에 어떤 요소가 있고 어떤 동작이 가능한지" (locator + 동작)
   ↓ 호출
core/driver.py  "요소를 어떻게 찾고 조작하는지" (find/click/type_text - CDP 세부사항 캡슐화)
   ↓ 호출
core/cdp_client.py  "TV와 어떻게 통신하는지" (websocket, CDP 프로토콜)

core/tv_controller.py  "TV 자체를 어떻게 켜고 끄고 연결하는지" (sdb 명령, driver와 별개 관심사)
```

각 레이어는 자신의 관심사만 알고 있습니다. 예를 들어 `test_home.py`는 xpath를 전혀
모르고, `home_page.py`는 CDP 프로토콜을 전혀 모릅니다. 화면 구조가 바뀌면
`pages/*.py`의 locator만 고치면 되고, 테스트 로직이나 통신 방식은 건드릴 필요가
없습니다.
