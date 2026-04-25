import os
import sys
import subprocess
import shutil
from pathlib import Path

# Vibe Video Upscaler - Sidecar Build Script
# Why: Tauri requires sidecars to be bundled executables. 
# PyInstaller allows us to package Python + dependencies into a single binary.

def get_target_triple():
    """
    Returns the target triple for the current platform.
    Tauri expects binaries in the format: {name}-{target-triple}.exe
    """
    if sys.platform == "win32":
        # Simplified for this environment, ideally we should check arch
        return "x86_64-pc-windows-msvc"
    elif sys.platform == "darwin":
        return "x86_64-apple-darwin" # or aarch64-apple-darwin
    else:
        return "x86_64-unknown-linux-gnu"

def build_sidecar():
    print("Starting Sidecar Build Process...")
    
    triple = get_target_triple()
    app_name = "vibe-engine"
    sidecar_name = f"{app_name}-{triple}"
    
    script_path = os.path.abspath("src-python/main.py")
    output_dir = os.path.abspath("src-tauri/binaries")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Bundling Python script with PyInstaller for {triple}...")
    
    # Run PyInstaller
    # --onefile: Single executable
    # --noconsole: No terminal window
    # --name: Specific name for the binary
    # --distpath: Where to put the final binary
    # --add-data: Bundle the upscalers and models
    
    # Path separators: ; on Windows, : on Unix
    sep = ";" if sys.platform == "win32" else ":"
    absolute_bin_path = os.path.abspath("src-python/bin")
    bin_data = f"{absolute_bin_path}{sep}."
    
    try:
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--noconsole",
            "--name", sidecar_name,
            "--distpath", output_dir,
            "--workpath", "build/pyinstaller",
            "--specpath", "build/pyinstaller",
            "--add-data", bin_data,
            script_path
        ], check=True)
        print(f"Sidecar built successfully: {output_dir}/{sidecar_name}")
    except FileNotFoundError:
        print("Error: PyInstaller not found. Please run 'pip install pyinstaller'.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: PyInstaller failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    build_sidecar()
