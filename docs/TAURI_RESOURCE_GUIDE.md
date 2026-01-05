# 📦 Tauri 리소스 번들링 가이드 (트러블슈팅)

이 문서는 Tauri 애플리케이션 빌드(`npm run tauri:build`) 시 외부 리소스(Python 스크립트 등)를 포함할 때 발생하는 경로 문제와 해결 방법을 다룹니다.

## 🛑 문제 현상

`tauri.conf.json`의 `bundle.resources`에 상위 디렉토리(`../`) 경로를 포함할 경우 빌드가 실패하는 현상.

```json
// tauri.conf.json (문제 발생 설정)
"resources": [
  "../python/**" 
]
```

**에러 메시지:**
```
glob pattern ../python/** path not found or didn't match any files.
Error: failed to build app: failed to build app
```

## 🔍 원인 분석

1. **경로 컨텍스트 불일치:** Tauri 빌드 시스템(Rust cargo)은 `src-tauri` 디렉토리를 기준으로 동작합니다. 보안 및 샌드박스 정책으로 인해 프로젝트 루트(`src-tauri`의 상위)로 벗어나는 상대 경로(`../`) 참조가 제한되거나, 글로브 패턴(`**`)이 올바르게 확장되지 않는 경우가 있습니다.
2. **Windows 경로 처리:** Windows 환경에서는 경로 구분자나 심볼릭 링크 처리 방식의 차이로 인해 상위 디렉토리 참조가 더욱 불안정할 수 있습니다.

## ✅ 해결 방법

### 1. 리소스를 `src-tauri` 내부로 이동 (권장)

가장 안정적인 방법은 외부 리소스를 `src-tauri` 디렉토리 내부로 복사하여 빌드 범위 안에 두는 것입니다.

**수정 전 구조:**
```
project/
├── python/        <-- 외부 (참조 불가)
└── src-tauri/
    └── tauri.conf.json
```

**수정 후 구조:**
```
project/
└── src-tauri/
    ├── python-embed/  <-- 내부 (참조 가능)
    └── tauri.conf.json
```

**tauri.conf.json 설정:**
```json
"resources": [
  "python-embed/**"
]
```

### 2. 자동화 스크립트 활용 (`beforeBuildCommand`)

원본 소스를 유지하고 싶다면, 빌드 전에 필요한 파일을 `src-tauri` 내부로 복사하는 스크립트를 추가합니다.

**package.json:**
```json
"scripts": {
  "copy-resources": "cp -r ../python src-tauri/python-embed",
  "tauri:build": "npm run copy-resources && tauri build"
}
```

## 💡 요약

Tauri 빌드 시 **"모든 리소스는 `src-tauri` 폴더 안에 있어야 한다"**는 원칙을 지키면 경로 문제를 100% 예방할 수 있습니다. 상위 폴더(`../`)를 참조하려고 하지 말고, 파일을 안으로 가져오세요.
