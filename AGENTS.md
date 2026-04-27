<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# 🛠 Maintenance & Monitoring Guidelines

## 버전 업데이트 및 배포 후 점검 사항
모든 버전 업데이트(Version Bump) 또는 주요 기능 푸시 후에는 반드시 다음 단계를 수행하여 배포 무결성을 보장한다.

1. **GitHub Actions 빌드 모니터링**
   - `gh run list --workflow build.yml` 명령어로 빌드 상태를 추적한다.
   - 실패 시 `gh run view --log-failed`를 통해 원인을 분석하고 즉시 수정 푸시를 진행한다.

2. **릴리즈 아티팩트(Assets) 검증**
   - `gh release view` 명령어를 통해 다음 파일들이 정상적으로 업로드되었는지 확인한다.
     - `*.msi` 또는 `*.exe` (설치형 인스톨러)
     - `*portable.zip` (무설치 포터블 버전)
   - 파일 크기가 0이거나 누락된 경우 워크플로우를 재실행하거나 수동으로 보완한다.

3. **배포 채널 동기화 점검**
   - GitHub Pages (`docs/` 기반 랜딩 페이지) 배포 성공 여부를 확인한다.
   - `README.md` 및 `HISTORY.md`에 버전 정보와 주요 변경 사항이 올바르게 반영되었는지 검토한다.

4. **포터블 버전 무결성**
   - 포터블 ZIP 내부에 `updio.exe`, `vibe-engine.exe`, `ffmpeg.exe` 등 필수 바이너리가 모두 포함되어 있는지 경로 로직을 상시 점검한다.
