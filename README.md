# 📊 FM Korea 게시물 수집기

FM Korea의 특정 작성자 게시물을 자동으로 수집하고 **NotebookLM**에서 분석할 수 있는 형태로 변환하는 도구입니다.

## ✨ 주요 기능

- **회원번호로 자동 검색**: 회원번호만 입력하면 모든 게시물을 자동으로 수집
- **Cloudflare 우회**: Playwright 스텔스 모드로 봇 차단 우회
- **메모리 효율적**: 게시물을 개별 파일로 즉시 저장하여 메모리 절약
- **NotebookLM 호환**: 수집된 데이터를 자동으로 Markdown 형식으로 변환
- **AI 분석 준비**: NotebookLM에 업로드하여 Gemini로 투자 패턴 분석
- **모던 UI**: Next.js + Tailwind CSS 다크 모드 인터페이스

## 🛠️ 기술 스택

- **프론트엔드**: Next.js 15 + React 19 + Tailwind CSS
- **데스크톱**: Tauri 2.x (예정)
- **스크래퍼**: Python 3.14 + Playwright + playwright-stealth
- **파싱**: BeautifulSoup4
- **분석**: NotebookLM (Google Gemini)

## 🔄 워크플로우

```
1. 회원번호 입력
   ↓
2. FM Korea 게시물 자동 수집 (Playwright)
   ↓
3. 개별 JSON 파일로 저장 (data/raw/)
   ↓
4. NotebookLM 형식 Markdown 변환 (data/notebooklm/)
   ↓
5. NotebookLM에 업로드
   ↓
6. Gemini AI로 투자 패턴 분석
```

## 📦 설치 방법

### 1. 사전 요구사항

- Node.js 18+ 및 npm
- Python 3.10+
- Git

### 2. 프로젝트 클론

```bash
git clone <repository-url>
cd fmkorea
```

### 3. Python 환경 설정

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source .venv/bin/activate

# 패키지 설치
pip install -r python/requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 4. Node.js 환경 설정

```bash
npm install
```

## 🚀 사용 방법

### 방법 1: UI 사용 (권장)

```bash
# 개발 서버 실행
npm run dev

# 브라우저에서 http://localhost:3000 접속
```

**UI 사용법**:
1. **회원번호로 검색** 탭 선택
2. 회원번호 입력 (예: `3902132645`)
3. 최대 페이지 수 설정
4. "분석 시작" 버튼 클릭
5. 진행 상황 확인

### 방법 2: Python CLI 직접 실행

#### 회원번호로 검색

```bash
.venv\Scripts\python.exe python\main.py member 3902132645 10
```

- `member`: 모드 (회원번호 검색)
- `3902132645`: FM Korea 회원번호
- `10`: 최대 페이지 수

**출력**:
- `data/raw/`: 개별 JSON 파일
- `data/notebooklm/`: NotebookLM용 Markdown 파일
- `data/notebooklm/분석_가이드.md`: 분석 가이드

#### 직접 URL 입력

```bash
.venv\Scripts\python.exe python\main.py urls "[\"https://www.fmkorea.com/...\", \"https://www.fmkorea.com/...\"]"
```

### 방법 3: NotebookLM으로 분석

1. **NotebookLM 접속**: https://notebooklm.google.com
2. **새 노트북 생성**: "New notebook" 클릭
3. **파일 업로드**: 
   - `data/notebooklm/fmkorea_posts_YYYYMMDD_HHMMSS.md` 업로드
   - `data/notebooklm/분석_가이드.md` 업로드 (선택)
4. **질문하기**: 
   - "이 작성자의 주요 투자 철학은 무엇인가요?"
   - "가장 자주 언급하는 섹터는?"
   - "리스크 관리 전략은?"
   - 등등 자유롭게 질문

### 방법 4: Markdown만 변환 (이미 수집된 데이터)

```bash
.venv\Scripts\python.exe python\exporter\notebooklm.py data/raw true
```

- `data/raw`: JSON 파일 위치
- `true`: 하나의 파일로 통합 (false면 개별 파일)

## 📁 프로젝트 구조

```
fmkorea/
├── src/                        # Next.js 프론트엔드
│   ├── app/
│   │   ├── page.tsx           # 메인 UI
│   │   ├── layout.tsx
│   │   └── globals.css
├── python/                     # Python 백엔드
│   ├── scraper/               # 스크래핑 모듈
│   │   ├── browser.py         # Cloudflare 우회
│   │   ├── collector.py       # 게시물 수집
│   │   └── parser.py          # HTML 파싱
│   ├── exporter/              # 내보내기 모듈
│   │   └── notebooklm.py      # NotebookLM 형식 변환
│   ├── main.py                # CLI 진입점
│   └── requirements.txt
├── data/
│   ├── raw/                   # 수집된 게시물 (JSON)
│   └── notebooklm/            # NotebookLM용 Markdown
├── package.json
└── README.md
```

## 📊 출력 데이터

### 수집된 게시물 (`data/raw/post_*.json`)

```json
{
  "url": "https://www.fmkorea.com/...",
  "title": "게시물 제목",
  "content": "본문 내용...",
  "date": "2026-01-05",
  "views": 1234,
  "metadata": {
    "author": "작성자",
    "comments": 56,
    "votes": 78
  }
}
```

### NotebookLM용 Markdown (`data/notebooklm/fmkorea_posts_*.md`)

```markdown
# FM Korea 게시물 모음

**수집 일시**: 2026-01-05 18:30:00
**총 게시물 수**: 50

---

<!-- 게시물 1/50 -->

# 게시물 제목

## 메타데이터

- **URL**: https://www.fmkorea.com/...
- **작성일**: 2026-01-05
- **조회수**: 1,234
- **댓글 수**: 56
- **추천 수**: 78

## 본문

본문 내용...

---
```

이 Markdown 파일을 NotebookLM에 업로드하면 Gemini가 자동으로 분석합니다.

## ⚙️ 설정

### Cloudflare 우회 설정

`python/scraper/browser.py`에서 설정 가능:

```python
# GUI 모드 (사용자가 진행 상황 확인 가능)
browser = await create_stealth_browser(headless=False)

# 헤드리스 모드 (백그라운드 실행)
browser = await create_stealth_browser(headless=True)
```

### 지연 시간 조정

`python/scraper/browser.py`:

```python
# 랜덤 지연 시간 (초)
await random_delay(min_sec=2.0, max_sec=5.0)
```

## ⚠️ 주의사항

### 법적 및 윤리적 고려사항

이 도구는 **개인적인 학습 및 연구 목적**으로만 사용해야 합니다.

**금지 사항**:
- ❌ 대량 스크래핑으로 서버에 부하 발생
- ❌ 수집된 데이터의 상업적 이용
- ❌ 개인정보 수집 또는 재배포

### Cloudflare 챌린지

FM Korea는 Cloudflare를 사용하므로, 간혹 "Verify you are human" 체크박스가 나타날 수 있습니다.

**대처 방법**:
1. GUI 모드(`headless=False`)로 실행
2. 브라우저 창에서 수동으로 체크박스 클릭
3. 스크립트가 자동으로 계속 진행됨

## 🐛 문제 해결

### Playwright 브라우저 설치 오류

```bash
# Chromium 재설치
.venv\Scripts\python.exe -m playwright install chromium --force
```

### 한글 깨짐 문제

모든 파일은 UTF-8로 인코딩되어 저장됩니다. 텍스트 에디터에서 UTF-8로 열어주세요.

### 메모리 부족

게시물은 수집 즉시 개별 파일로 저장되므로 메모리 문제가 발생하지 않습니다. 만약 문제가 발생하면 최대 페이지 수를 줄여주세요.

## 📝 TODO

- [ ] Tauri 백엔드 통합
- [ ] UI에서 NotebookLM 파일 다운로드 버튼
- [ ] 증분 업데이트 (이미 수집한 게시물 스킵)
- [ ] 데이터베이스 연동 (SQLite)
- [ ] 여러 작성자 동시 수집
- [ ] 수집 스케줄링 (정기적 자동 수집)

## 📄 라이선스

MIT License

## 🤝 기여

이슈 및 풀 리퀘스트 환영합니다!

## 📧 문의

문제가 발생하면 GitHub Issues에 등록해주세요.
