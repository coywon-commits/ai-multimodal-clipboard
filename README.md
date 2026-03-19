# AI Clipboard - 텍스트 & 이미지 복사/붙여넣기 도구

> AI 채팅창의 텍스트와 이미지를 한 번에 추출하여 다른 AI 채팅창에 붙여넣기

## 개요

AI 채팅(ChatGPT, Claude, Gemini, Perplexity)에서 대화 내용을 복사할 때, 텍스트는 복사되지만 이미지는 따로 다운로드해서 다시 업로드해야 하는 불편함을 해결합니다.

이 도구를 사용하면:
1. **Chrome 확장**으로 텍스트 + 이미지를 한 번에 추출
2. **Python 앱**으로 다른 AI 채팅에 한 번에 붙여넣기

## 구성 요소

### 1. Chrome 확장 프로그램

AI 채팅 페이지에서 텍스트와 이미지를 추출합니다.

**지원 사이트:**
- ✅ ChatGPT (chat.openai.com, chatgpt.com)
- ✅ Claude (claude.ai)
- ✅ Gemini (gemini.google.com)
- ✅ Perplexity (perplexity.ai)

### 2. Python 앱

시스템 트레이에 상주하며 단축키로 붙여넣기를 자동화합니다.

**단축키:**
| 단축키 | 기능 |
|--------|------|
| `Ctrl+Shift+V` | 저장된 텍스트 + 이미지 순차 붙여넣기 |
| `Ctrl+Shift+R` | 저장된 데이터 초기화 |

## 설치 방법

### Chrome 확장 설치

1. Chrome 브라우저에서 `chrome://extensions` 열기
2. 우측 상단 **개발자 모드** 활성화
3. **압축해제된 확장 프로그램을 로드합니다** 클릭
4. `chrome-extension` 폴더 선택

### Python 앱 설치

```bash
# 1. Python 폴더로 이동
cd python-app

# 2. 가상환경 생성 (선택)
python -m venv venv
venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 앱 실행
python main.py
```

## 사용 방법

### STEP 1: 추출 (Chrome 확장)

1. AI 채팅 페이지(ChatGPT, Claude 등)에서 대화 진행
2. Chrome 확장 아이콘(📋) 클릭
3. **추출하기** 버튼 클릭
4. 텍스트와 이미지가 로컬에 저장됨

### STEP 2: 붙여넣기 (Python 앱)

1. Python 앱 실행 (시스템 트레이에 아이콘 표시)
2. 다른 AI 채팅 입력창 클릭
3. `Ctrl+Shift+V` 누르기
4. 텍스트와 이미지가 순차적으로 붙여넣기됨

## 폴더 구조

```
chrom extention copypaste/
├── DESIGN.md               # 설계 문서
├── README.md               # 사용 설명서 (현재 파일)
│
├── chrome-extension/       # Chrome 확장 프로그램
│   ├── manifest.json       # 확장 설정
│   ├── popup/              # 팝업 UI
│   ├── content/            # 각 사이트별 추출 로직
│   ├── background/         # 백그라운드 서비스
│   └── icons/              # 아이콘
│
└── python-app/             # Python 붙여넣기 앱
    ├── main.py             # 메인 엔트리포인트
    ├── app/                # 핵심 기능 모듈
    ├── storage/            # 저장소 관리
    ├── ui/                 # UI 컴포넌트
    └── requirements.txt    # 의존성
```

## 데이터 저장 위치

추출된 데이터는 다음 위치에 저장됩니다:

```
C:\Users\{사용자}\AppData\Local\AIClipboard\
├── text.txt          # 추출된 텍스트
├── images/           # 추출된 이미지들
│   ├── img_001.png
│   ├── img_002.png
│   └── ...
└── metadata.json     # 메타데이터
```

## 문제 해결

### 확장이 작동하지 않음
- 확장을 다시 로드해 보세요 (chrome://extensions에서 새로고침 아이콘)
- 페이지를 새로고침 후 다시 시도

### 이미지가 추출되지 않음
- 일부 이미지는 CORS 정책으로 추출이 제한될 수 있습니다
- 페이지에서 이미지가 완전히 로드된 후 시도해 주세요

### 붙여넣기가 안 됨
- Python 앱이 실행 중인지 확인 (시스템 트레이 아이콘)
- 입력창이 활성화된 상태에서 단축키를 누르세요
- 관리자 권한으로 실행해 보세요

## 라이선스

MIT License
