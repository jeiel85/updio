# 🎬 AI Video Upscaler 프로젝트 요구사항 정의서 (Master Prompt)

## 1. 프로젝트 개요
* **프로젝트명:** Vibe Video Upscaler
* **핵심 목표:** Tauri(Rust)와 Python AI 엔진을 결합하여, 저화질(AVI, MP4 등) 영상을 1080p 또는 4K로 업스케일링하는 고성능 데스크톱 앱 개발.
* **개발 철학:** * UI는 세련된 웹 기술로, 연산은 강력한 Rust와 Python AI 모델로 분리 처리.
    * 사용자가 별도의 환경 설정 없이 실행 파일 하나로 구동 가능한 포터블 환경 지향.

## 2. 기술 스택 (Architecture)
* **Frontend:** React / Next.js + Tailwind CSS (Tauri 가이드 준수)
* **Backend (Controller):** Rust (Tauri Framework)
* **Core Engine (Sidecar):** Python 3.10+ (PyTorch, OpenCV, FFmpeg-python)
* **AI Models:** Real-ESRGAN (xinntao), Video2X 파이프라인 논리 구조 참조.
* **Build Tools:** NPM (Frontend), Cargo (Backend), PyInstaller (AI Sidecar Bundling).

## 3. 핵심 참조 오픈소스
AI 구현 시 아래 레포지토리의 아키텍처 및 명령줄 인터페이스(CLI) 로직을 참고할 것.
1. **Video2X (https://github.com/k4yt3x/video2x):** 프레임 분할 및 오디오 병합의 전체 워크플로우.
2. **Real-ESRGAN (https://github.com/xinntao/Real-ESRGAN):** `realesrgan-ncnn-vulkan` 가중치를 이용한 고해상도 복원 엔진.

## 4. 상세 기능 요구사항

### 4.1. Python AI 사이드카 (Core)
* **입력:** 원본 파일 경로, 출력 경로, 확대 배율(2x/4x), 타겟 해상도, 모델 타입.
* **프로세스:**
    1. **FFmpeg 추출:** 영상을 무손실 PNG/JPG 프레임으로 분리하고 오디오를 별도 추출.
    2. **AI 인퍼런스:** 분리된 프레임을 Real-ESRGAN 모델로 순차 업스케일링. (VRAM 최적화를 위해 배치 처리 로직 포함)
    3. **FFmpeg 병합:** 처리된 프레임을 원본 FPS에 맞춰 다시 인코딩하고 오디오를 결합.
* **통신:** 진행률(현재 프레임/전체 프레임)을 `stdout`으로 JSON 형식으로 실시간 출력.

### 4.2. Tauri & Rust 제어부 (Backend)
* **사이드카 관리:** `tauri::api::process::Command`를 사용해 Python `.exe` 실행 파일을 백그라운드 프로세스로 관리.
* **이벤트 브릿지:** Python의 진행 상태 로그를 캡처하여 프런트엔드(React)로 실시간 전달.
* **리소스 관리:** 프로그램 종료 시 진행 중인 모든 하위 프로세스(Python, FFmpeg)를 안전하게 강제 종료(Kill) 처리.

### 4.3. UI/UX 디자인 (Frontend)
* **메인 화면:** 파일 드래그 앤 드롭 영역, 해상도 선택 드롭다운, GPU 가속 토글 버튼.
* **진행 정보:** 전체 진행률을 나타내는 프로그레스 바와 현재 처리 중인 프레임 번호 실시간 표시.
* **완료 알림:** 작업 완료 시 시스템 알림 발송 및 출력 폴더 바로가기 제공.

## 5. 자동화 빌드 및 배포 요건 (CRITICAL)
* **의존성 자동 관리:** * 사용자가 파이썬을 따로 설치하지 않아도 되도록, PyInstaller를 통해 파이썬 환경과 라이브러리를 포함한 단일 사이드카 실행 파일을 생성하는 `scripts/build_sidecar.py`를 작성할 것.
* **Tauri 설정:** `tauri.conf.json`에 해당 사이드카를 등록하고, 아키텍처별(x86_64, arm64) 바이너리 매칭 설정을 포함할 것.
* **코드 주석:** 모든 함수 상단에는 Input, Output, 핵심 로직을 명시하고, 단순한 코드 설명이 아닌 '왜(Why)' 이 방식을 선택했는지에 대한 의사결정 근거를 주석으로 기록할 것.

## 6. 예외 처리
* GPU 가속(CUDA/Vulkan) 실패 시 CPU 모드로 자동 폴백(Fallback).
* 충분한 디스크 공간이 없을 경우 사전에 경고 메시지 출력.