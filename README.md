# 🎬 Vibe Video Upscaler

<p align="center">
  <img src="src-tauri/icons/icon.png" alt="Vibe Video Upscaler Logo" width="128" height="128">
</p>

<p align="center">
  <b>Transform low-resolution videos into cinematic 4K masterpieces with AI.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/Tauri-FFC131?style=for-the-badge&logo=tauri&logoColor=white" alt="Tauri">
  <img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white" alt="Rust">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
</p>

---

## 🌟 Key Features

- **🚀 High-Performance Upscaling:** Leverages Real-ESRGAN and AI models to enhance video quality up to 4K.
- **⚡ Hybrid Architecture:** A sleek React/Next.js frontend powered by a blazing-fast Rust controller and Python AI engine.
- **🎨 Modern UI/UX:** Dark-themed, interactive dashboard with real-time progress tracking and GPU acceleration support.
- **📦 Portable Environment:** Designed to be bundled into a single executable—no complex local environment setup required.
- **🔄 Smart Pipeline:** Automatic frame extraction, batch AI inference, and seamless audio/video merging using FFmpeg.

## 🏗️ Architecture

The project follows a high-performance **Sidecar Architecture**:

1.  **Frontend (Next.js):** Handles the user interface and state management.
2.  **Backend (Rust/Tauri):** Orchestrates the process, manages permissions, and communicates with the system.
3.  **Core Engine (Python Sidecar):** Executes the heavy lifting—FFmpeg processing and AI model inference.

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v20+)
- **Rust Toolchain**
- **Python 3.10+** (with `pyinstaller`)
- **FFmpeg** (installed and added to PATH)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jeiel85/updio.git
    cd updio
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    pip install pyinstaller
    ```

### Development & Build

1.  **Build the Python Engine (Sidecar):**
    ```bash
    npm run build:sidecar
    ```

2.  **Launch the development app:**
    ```bash
    npx tauri dev
    ```

3.  **Build the production executable:**
    ```bash
    npx tauri build
    ```

## 🛠️ Technical Implementation Details

- **Rust Backend:** Uses `tauri-plugin-shell` for secure sidecar execution and `Emitter` for real-time progress streaming.
- **Python Sidecar:** Implements a JSON-based stdout protocol to communicate with the Rust layer.
- **CI/CD:** Fully automated GitHub Actions workflow for cross-platform builds and automatic releases.

## 📜 Credits & References

- **[Video2X](https://github.com/k4yt3x/video2x):** Reference for frame-based video processing logic.
- **[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN):** Core AI enhancement engine.
- **[Tauri Framework](https://tauri.app/):** The foundation for the desktop application.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/jeiel85">jeiel85</a>
</p>
