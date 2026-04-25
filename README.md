# 🎬 Vibe Video Upscaler

<p align="center">
  <img src="src-tauri/icons/icon.png" alt="Vibe Video Upscaler 로고" width="128" height="128">
</p>

<p align="center">
  <b>AI로 저해상도 영상을 4K 고화질로 변환하세요.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/Tauri-FFC131?style=for-the-badge&logo=tauri&logoColor=white" alt="Tauri">
  <img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white" alt="Rust">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
</p>

---

## 🌟 주요 기능

- **🚀 고성능 업스케일링:** Real-ESRGAN AI 모델을 활용해 영상 품질을 최대 4K까지 향상.
- **⚡ 하이브리드 아키텍처:** React/Next.js 프론트엔드 + Rust 컨트롤러 + Python AI 엔진의 조합.
- **🎨 모던 UI/UX:** 다크 테마 대시보드, 실시간 진행률 표시, GPU 가속 지원.
- **📦 포터블 실행:** 별도 환경 설정 없이 바로 실행 가능한 단일 패키지로 배포.
- **🔄 스마트 파이프라인:** FFmpeg 기반 자동 프레임 추출 → AI 추론 → 오디오/영상 병합.

## 🏗️ 아키텍처

**사이드카(Sidecar) 아키텍처** 기반으로 동작합니다:

1. **프론트엔드 (Next.js):** 사용자 인터페이스 및 상태 관리.
2. **백엔드 (Rust/Tauri):** 프로세스 조율, 권한 관리, 시스템 통신.
3. **코어 엔진 (Python 사이드카):** FFmpeg 처리 및 AI 모델 추론 실행.

## 🚀 시작하기

### 사전 요구사항

- **Node.js** v20 이상
- **Rust 툴체인**
- **Python 3.10 이상** (`pyinstaller` 포함)
- **FFmpeg** (설치 후 PATH 등록)

### 설치

1. **저장소 클론:**
    ```bash
    git clone https://github.com/jeiel85/updio.git
    cd updio
    ```

2. **의존성 설치:**
    ```bash
    npm install
    pip install pyinstaller
    ```

### 개발 및 빌드

1. **Python 엔진(사이드카) 빌드:**
    ```bash
    npm run build:sidecar
    ```

2. **개발 앱 실행:**
    ```bash
    npx tauri dev
    ```

3. **프로덕션 빌드:**
    ```bash
    npx tauri build
    ```

## 🛠️ 기술 구현 상세

- **Rust 백엔드:** `tauri-plugin-shell`로 사이드카를 안전하게 실행하고, `Emitter`로 실시간 진행 상황을 스트리밍.
- **Python 사이드카:** JSON 기반 stdout 프로토콜로 Rust 레이어와 통신.
- **CI/CD:** GitHub Actions로 빌드 및 릴리즈 자동화 (인스톨러 + 포터블 zip 제공).

## 📜 참고 프로젝트

- **[Video2X](https://github.com/k4yt3x/video2x):** 프레임 기반 영상 처리 로직 참고.
- **[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN):** 핵심 AI 업스케일 엔진.
- **[Tauri Framework](https://tauri.app/):** 데스크탑 앱 프레임워크.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jeiel85">jeiel85</a>
</p>
