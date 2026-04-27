import os
import urllib.request
import zipfile
import shutil
import subprocess

def setup_dev_env():
    print("🚀 Starting local development setup...")
    
    bin_dir = os.path.join("src-tauri", "binaries")
    os.makedirs(bin_dir, exist_ok=True)
    
    ffmpeg_zip = "ffmpeg.zip"
    ffmpeg_url = "https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-essentials_build.zip"
    
    if not os.path.exists(ffmpeg_zip):
        print(f"📥 Downloading FFmpeg from {ffmpeg_url}...")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip)
    
    temp_dir = "ffmpeg_temp"
    if not os.path.exists(temp_dir):
        print("📦 Extracting FFmpeg...")
        with zipfile.ZipFile(ffmpeg_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
            
    print("📋 Copying FFmpeg binaries...")
    for root, dirs, files in os.walk(temp_dir):
        if "ffmpeg.exe" in files:
            src = os.path.join(root, "ffmpeg.exe")
            dst = os.path.join(bin_dir, "ffmpeg-x86_64-pc-windows-msvc.exe")
            shutil.copy(src, dst)
        if "ffprobe.exe" in files:
            src = os.path.join(root, "ffprobe.exe")
            dst = os.path.join(bin_dir, "ffprobe-x86_64-pc-windows-msvc.exe")
            shutil.copy(src, dst)
            
    print("🔨 Building Python Sidecar...")
    subprocess.run(["npm", "run", "build:sidecar"], check=True, shell=True)
    
    print("✅ Setup complete! You can now run 'npx tauri dev'")

if __name__ == "__main__":
    setup_dev_env()
