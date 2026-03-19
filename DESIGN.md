# AI 채팅 복사/붙여넣기 도구

> AI 채팅창의 텍스트 + 이미지를 한 번에 추출하여 다른 AI 채팅창에 한 번에 붙여넣기

---

## 전체 조감도

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              사용자 워크플로우                                │
└─────────────────────────────────────────────────────────────────────────────┘

  [원본 AI 채팅]                    [로컬 저장소]                [대상 AI 채팅]
  ┌─────────────┐                  ┌─────────────┐              ┌─────────────┐
  │  ChatGPT    │                  │             │              │   Claude    │
  │  ┌───────┐  │    Chrome 확장   │  text.txt   │   Python 앱  │  ┌───────┐  │
  │  │ 텍스트 │  │ ═══════════════▶│  img_01.png │══════════════▶│  │ 텍스트 │  │
  │  │ 이미지1 │  │    버튼 클릭    │  img_02.png │  Ctrl+Shift+V │  │ 이미지1 │  │
  │  │ 이미지2 │  │                │  img_03.png │              │  │ 이미지2 │  │
  │  └───────┘  │                  │     ...     │              │  └───────┘  │
  └─────────────┘                  └─────────────┘              └─────────────┘
```

---

## 시스템 구성

### 1. Chrome 확장 프로그램 (추출 담당)

| 항목 | 설명 |
|------|------|
| 역할 | AI 채팅 페이지에서 텍스트 + 이미지 추출 |
| 동작 | 확장 아이콘 클릭 → 현재 대화의 텍스트/이미지 자동 수집 → 로컬에 저장 |
| 기술 | JavaScript, Chrome Extension API |

**지원 AI 사이트:**
- ✅ ChatGPT (chat.openai.com)
- ✅ Claude (claude.ai)
- ✅ Gemini (gemini.google.com)
- ✅ Perplexity (perplexity.ai)

### 2. Python 앱 (붙여넣기 담당)

| 항목 | 설명 |
|------|------|
| 역할 | 저장된 텍스트 + 이미지를 대상 AI 채팅에 순차 붙여넣기 |
| 동작 | 단축키 → 텍스트 붙여넣기 → 이미지들 순차 붙여넣기 |
| 기술 | Python, PyQt5/PySide6, keyboard, Pillow, pyautogui |

**단축키:**
| 단축키 | 기능 |
|--------|------|
| `Ctrl+Shift+V` | 저장된 텍스트 + 이미지 순차 붙여넣기 |
| `Ctrl+Shift+R` | 저장된 데이터 초기화 |

### 3. 로컬 저장소

```
C:\Users\{사용자}\AppData\Local\AIClipboard\
├── text.txt          # 추출된 텍스트
├── images/
│   ├── img_001.png   # 추출된 이미지 1
│   ├── img_002.png   # 추출된 이미지 2
│   └── ...
└── metadata.json     # 추출 정보 (출처 AI, 시간 등)
```

---

## 상세 작동 흐름

### STEP 1: 추출 (Chrome 확장)

```
사용자가 ChatGPT에서 대화 진행
         │
         ▼
Chrome 확장 아이콘 클릭
         │
         ▼
Content Script가 페이지 분석
         │
         ├── 텍스트 추출 (선택 영역 또는 전체 대화)
         │
         └── 이미지 추출 (img 태그의 src → fetch → blob)
         │
         ▼
Native Messaging으로 Python 앱에 전달
    또는
Downloads API로 로컬 폴더에 저장
         │
         ▼
저장 완료 알림
```

### STEP 2: 붙여넣기 (Python 앱)

```
사용자가 Claude 채팅 입력창 클릭
         │
         ▼
Ctrl+Shift+V 누름
         │
         ▼
Python 앱이 로컬 저장소에서 데이터 로드
         │
         ├── 1. text.txt 내용을 클립보드에 복사
         │      → Ctrl+V 시뮬레이션 (텍스트 붙여넣기)
         │      → 0.3초 대기
         │
         ├── 2. img_001.png를 클립보드에 복사
         │      → Ctrl+V 시뮬레이션 (이미지 업로드)
         │      → 0.5초 대기
         │
         ├── 3. img_002.png를 클립보드에 복사
         │      → Ctrl+V 시뮬레이션 (이미지 업로드)
         │      → 0.5초 대기
         │
         └── ... (모든 이미지 반복)
         │
         ▼
완료 알림 (토스트 또는 사운드)
```

---

## 기술적 세부사항

### Chrome 확장 구조

```
chrome-extension/
├── manifest.json         # 확장 설정 (Manifest V3)
├── popup/
│   ├── popup.html        # 팝업 UI
│   ├── popup.js          # 팝업 로직
│   └── popup.css         # 팝업 스타일
├── content/
│   ├── chatgpt.js        # ChatGPT용 추출 로직
│   ├── claude.js         # Claude용 추출 로직
│   ├── gemini.js         # Gemini용 추출 로직
│   └── perplexity.js     # Perplexity용 추출 로직
├── background/
│   └── service-worker.js # 백그라운드 서비스
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── native-host/          # (선택) Native Messaging 설정
    └── manifest.json
```

### Python 앱 구조

```
python-app/
├── main.py               # 메인 엔트리포인트
├── app/
│   ├── __init__.py
│   ├── clipboard.py      # 클립보드 관리
│   ├── hotkey.py         # 단축키 등록
│   ├── paste.py          # 붙여넣기 자동화
│   └── tray.py           # 시스템 트레이
├── storage/
│   └── manager.py        # 로컬 저장소 관리
├── ui/
│   └── tray_icon.py      # 트레이 아이콘 UI
├── requirements.txt
└── setup.py              # 설치 스크립트
```

---

## 개발 순서

### Phase 1: 기본 기능 (MVP)

| 순서 | 작업 | 예상 |
|------|------|------|
| 1-1 | Python 앱 기본 구조 (트레이 아이콘, 단축키) | ⭐⭐ |
| 1-2 | Chrome 확장 기본 구조 (팝업, manifest) | ⭐⭐ |
| 1-3 | ChatGPT용 추출 로직 | ⭐⭐⭐ |
| 1-4 | 텍스트 붙여넣기 기능 | ⭐⭐ |
| 1-5 | 이미지 순차 붙여넣기 기능 | ⭐⭐⭐ |

### Phase 2: 확장 지원

| 순서 | 작업 | 예상 |
|------|------|------|
| 2-1 | Claude 추출 로직 | ⭐⭐⭐ |
| 2-2 | Gemini 추출 로직 | ⭐⭐⭐ |
| 2-3 | Perplexity 추출 로직 | ⭐⭐⭐ |

### Phase 3: 고급 기능

| 순서 | 작업 | 예상 |
|------|------|------|
| 3-1 | 선택 영역만 추출 옵션 | ⭐⭐ |
| 3-2 | 히스토리 기능 (이전 추출 내용 보관) | ⭐⭐ |
| 3-3 | 설정 UI (단축키 변경, 대기 시간 조절) | ⭐⭐ |

---

## 폴더 구조 (최종)

```
chrom extention copypaste/
├── DESIGN.md                 # 이 문서
├── README.md                 # 사용 설명서
│
├── chrome-extension/         # Chrome 확장 프로그램
│   ├── manifest.json
│   ├── popup/
│   ├── content/
│   ├── background/
│   └── icons/
│
├── python-app/               # Python 붙여넣기 앱
│   ├── main.py
│   ├── app/
│   ├── storage/
│   ├── ui/
│   └── requirements.txt
│
└── docs/                     # 추가 문서
    ├── installation.md       # 설치 가이드
    └── troubleshooting.md    # 문제 해결
```

---

## 제한사항 및 고려사항

### 기술적 제한

1. **각 AI 사이트 구조 차이**: 사이트마다 HTML 구조가 다르므로 별도 추출 로직 필요
2. **사이트 업데이트**: AI 사이트가 업데이트되면 추출 로직 수정 필요할 수 있음
3. **이미지 접근 제한**: 일부 이미지는 CORS 정책으로 직접 다운로드 불가 → blob URL로 우회

### 사용자 경험

1. **붙여넣기 타이밍**: AI 채팅 입력창이 활성화된 상태에서 단축키 사용
2. **이미지 업로드 시간**: 이미지 크기/개수에 따라 시간 소요
3. **초기화 필요**: 새로운 내용 추출 전 Ctrl+Shift+R로 초기화 권장

---

## 다음 단계

1. ✅ 설계 문서 작성 (현재)
2. ⬜ Python 앱 기본 구조 생성
3. ⬜ Chrome 확장 기본 구조 생성
4. ⬜ ChatGPT 추출 로직 구현
5. ⬜ 붙여넣기 기능 구현
6. ⬜ 테스트 및 디버깅

---

**시작할 준비가 되셨으면 말씀해 주세요!**
