🤖 Project Master Instruction (Standard v1.0)
이 문서는 프로젝트의 일관성을 유지하고, 제미나이(Gemini)가 코드 생성 및 프로젝트 관리를 수행할 때 준수해야 할 최상위 지침입니다.

🛠️ 1. 프로젝트 가변 설정 (Project Specifics)
이 섹션은 프로젝트의 성격에 따라 변경되는 기술 스택 및 환경 설정입니다.

핵심 목표: Next.js 기반 웹 서비스 개발, Playwright 자동화 시스템 구축, Tauri/Capacitor 기반 데스크톱 및 모바일 앱 개발.

기술 스택:

Web: Next.js (App Router) - easynext 베이스.

Desktop/Mobile: Tauri (PC/Rust), Capacitor (Android) - CORS 우회 및 시스템 제어용.

UI/UX: TypeScript, Tailwind CSS, Shadcn/UI, Magic UI.

Automation: Playwright (Python/JS) - Selenium 사용 절대 금지.

Python GUI: customtkinter (Modern UI).

Environment: Node.js (npm), Python Virtual Environment (.venv).

운영 명령어:

개발: npm run dev | 빌드: npm run build

테스트(GUI): npx playwright test --ui

Python: source .venv/bin/activate && python main.py

특이사항:

CORS 대응: PC 환경은 Tauri(Rust), 안드로이드 환경은 Capacitor 기술 스택을 최우선 검토하여 우회를 구현한다.

Vercel 제약: Hobby Plan의 10초 타임아웃을 고려하여 무거운 로직은 분리하거나 최적화한다.

Playwright: 사용자가 과정을 볼 수 있도록 --headless 모드를 강제하지 않는다.

🏗️ 2. 개발 및 소통 원칙 (Core Principles - 공통)
모든 프로젝트에서 변하지 않는 기본 원칙입니다.

언어 및 인코딩: 모든 답변과 산출물은 한글로 작성하며, 한국어 문자는 반드시 UTF-8로 인코딩한다.

간결성(Conciseness): 불필요한 설명은 최소화하고 작업 결과와 핵심 로그 위주로 보고한다.

정직성(Honesty): 모르는 내용이나 에러 발생 시 추측하지 않고 솔직히 인정하며 대안을 제시한다.

문서 관리: 모든 Markdown 파일은 프로젝트 루트의 docs/ 폴더 안에 저장한다.

리팩토링(Tidying): 기존 기능을 깨뜨리지 않도록 아주 작은 단위부터 변화를 준다.

가시성: 모든 프로세스 진행 시 **진행률(Progress Bar 또는 로그)**을 표시하여 사용자에게 상태를 알린다.

🤖 3. 제미나이 최적화 및 코드 무결성 (Gemini Integrity - 공통)
생략 금지 (No Truncation): 코드를 수정할 때 // ... 또는 /* 기존 코드 */와 같은 생략을 절대 하지 않는다. 파일 전체 내용을 제공하여 사용자가 바로 복사-붙여넣기 할 수 있게 한다.

사전 분석 (Chain of Thought): 코드를 작성하기 전, 수정 내용이 기존 기능에 미칠 영향을 먼저 한 문장으로 분석한 뒤 작성을 시작한다.

컨텍스트 보존: 새로운 기능 추가 시 기존의 import, 타입 정의, 환경 변수 설정을 임의로 삭제하거나 변경하지 않는다.

원자적 수정 (Atomic Modification): 한 번에 하나의 기능만 수정한다. 여러 파일 수정 시 순서를 제안하고 승인 후 진행한다.

비교 검토 (Diff Summary): 코드 작성 후, 기존 코드와의 차이점을 Diff 스타일로 짧게 요약하여 보고한다.

📦 4. Git Push Workflow (5단계 필수 절차 - 공통)
"git에 푸시해줘" 요청 시 다음 절차를 엄격히 준수한다.

변경사항 정리: git status 확인 후 논리적 단위로 스테이징. Conventional Commits 규칙 준수.

문서 업데이트: docs/AGENTS.md 또는 README.md에 변경 사항 반영 후 커밋.

Feature 브랜치 푸시: 현재 브랜치를 원격에 push.

Main 브랜치 병합: main으로 체크아웃 후 merge. 충돌 시 즉시 보고 및 해결책 제시.

최종 푸시: 병합된 main을 origin main에 push.