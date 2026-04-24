# Vibe Video Upscaler

AI-powered video upscaling desktop application built with Tauri, Next.js, and Python.

## 🏗️ Architecture

- **Frontend:** React / Next.js + Tailwind CSS
- **Backend (Controller):** Rust (Tauri)
- **Core Engine (Sidecar):** Python (PyTorch, OpenCV, FFmpeg)
- **Build Tools:** NPM, Cargo, PyInstaller

## 🚀 Setup & Build

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Rust](https://www.rust-lang.org/)
- [Python 3.10+](https://www.python.org/)
- [FFmpeg](https://ffmpeg.org/) (must be in system PATH)

### 2. Install Dependencies
```bash
# Install Node dependencies
npm install

# Install Python dependencies (for sidecar development)
pip install pyinstaller
```

### 3. Build Sidecar (Python Engine)
The sidecar must be built before the Tauri app can run or build.
```bash
npm run build:sidecar
```
This creates a bundled executable in `src-tauri/binaries/`.

### 4. Run Development Mode
```bash
npm run tauri dev
```

### 5. Build Production App
```bash
npm run tauri build
```

## 🛠️ Project Structure
- `src/`: Next.js Frontend
- `src-tauri/`: Rust Backend & Tauri configuration
- `src-python/`: Python Sidecar source code
- `scripts/`: Build and automation scripts
- `Vibe-Video-Upscaler.md`: Project requirements and design document

## 📝 Note on AI Engine
The current Python sidecar includes a logic placeholder for Real-ESRGAN. To enable full AI upscaling, you should:
1. Download `realesrgan-ncnn-vulkan` binaries.
2. Update `src-python/main.py` to call the engine instead of the placeholder copy command.
3. Bundle the engine binaries with the sidecar using PyInstaller's `--add-data` flag.
