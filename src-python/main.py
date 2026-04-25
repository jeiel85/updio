import os
import sys
import json
import subprocess
import argparse
import shutil
import platform
from pathlib import Path

# Vibe Video Upscaler - AI Sidecar Core
# Improved: Robust path resolution for local development and production

# Global paths for FFmpeg/FFprobe
FFMPEG_EXE = "ffmpeg"
FFPROBE_EXE = "ffprobe"

def log_progress(current, total, message):
    print(json.dumps({
        "current": current,
        "total": total,
        "percentage": round((current / total) * 100, 2) if total > 0 else 0,
        "message": message
    }), flush=True)

def run_command(args):
    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f"FFmpeg Error: {stderr.strip()}")
        return stdout
    except FileNotFoundError:
        raise Exception(f"Executable '{args[0]}' not found. Please install FFmpeg or check sidecar bundling.")
    except Exception as e:
        raise Exception(f"Execution error: {str(e)}")

def extract_frames(input_path, temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    frames_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    log_progress(0, 100, "Extracting frames...")
    
    probe_args = [
        FFPROBE_EXE, "-v", "error", "-select_streams", "v:0", 
        "-count_packets", "-show_entries", "stream=nb_read_packets", 
        "-of", "csv=p=0", input_path
    ]
    try:
        total_frames = int(run_command(probe_args).strip())
    except:
        total_frames = 100 
    
    extract_args = [
        FFMPEG_EXE, "-y", "-i", input_path, "-qscale:v", "2", 
        os.path.join(frames_dir, "%08d.jpg")
    ]
    run_command(extract_args)
    
    return frames_dir, total_frames

def upscale_frames(frames_dir, output_frames_dir, scale, model_type):
    os.makedirs(output_frames_dir, exist_ok=True)
    frame_files = sorted(os.listdir(frames_dir))
    total = len(frame_files)
    
    log_progress(0, total, f"Upscaling frames (Scale: {scale}x)...")
    
    for i, frame_file in enumerate(frame_files):
        src = os.path.join(frames_dir, frame_file)
        dst = os.path.join(output_frames_dir, frame_file)
        shutil.copy(src, dst)
        if i % 10 == 0 or i == total - 1:
            log_progress(i + 1, total, f"Upscaling: {frame_file}")

def merge_frames(output_frames_dir, input_video, output_path):
    log_progress(95, 100, "Merging frames and audio...")
    
    fps_args = [
        FFPROBE_EXE, "-v", "error", "-select_streams", "v:0", 
        "-show_entries", "stream=r_frame_rate", 
        "-of", "default=noprint_wrappers=1:nokey=1", input_video
    ]
    try:
        fps = run_command(fps_args).strip()
    except:
        fps = "30"
    
    audio_temp = os.path.join(os.path.dirname(output_path), "temp_audio_src.m4a")
    has_audio = False
    try:
        run_command([FFMPEG_EXE, "-y", "-i", input_video, "-vn", "-acodec", "copy", audio_temp])
        has_audio = True if os.path.exists(audio_temp) and os.path.getsize(audio_temp) > 0 else False
    except:
        has_audio = False
    
    if has_audio:
        merge_args = [
            FFMPEG_EXE, "-y", "-r", fps, "-i", os.path.join(output_frames_dir, "%08d.jpg"),
            "-i", audio_temp, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy", output_path
        ]
    else:
        merge_args = [
            FFMPEG_EXE, "-y", "-r", fps, "-i", os.path.join(output_frames_dir, "%08d.jpg"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path
        ]
    
    run_command(merge_args)
    
    if os.path.exists(audio_temp):
        os.remove(audio_temp)

def find_executable(name):
    """
    Search order:
    1. System PATH (Best for local development)
    2. Tauri Sidecar format in the current executable directory
    3. Same directory as the executable
    """
    # 1. Check system PATH
    path_exe = shutil.which(name)
    if path_exe:
        return path_exe
        
    # 2. Check Tauri Sidecar directory (for production)
    exe_dir = os.path.dirname(sys.executable)
    triples = ["x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"]
    for triple in triples:
        sidecar_path = os.path.join(exe_dir, f"{name}-{triple}.exe")
        if os.path.exists(sidecar_path):
            return sidecar_path
            
    # 3. Check same directory without triple
    direct_path = os.path.join(exe_dir, f"{name}.exe")
    if os.path.exists(direct_path):
        return direct_path
        
    return name # Fallback to name and let it fail gracefully in run_command

def main():
    global FFMPEG_EXE, FFPROBE_EXE
    parser = argparse.ArgumentParser(description="Vibe Video Upscaler Sidecar")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument("--model", default="realesrgan-x4plus")
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--ffprobe", default="ffprobe")
    
    args = parser.parse_args()
    
    FFMPEG_EXE = find_executable(args.ffmpeg)
    FFPROBE_EXE = find_executable(args.ffprobe)
    
    temp_dir = os.path.join(os.path.dirname(args.output), "vibe_workspace")
    
    try:
        frames_dir, total_frames = extract_frames(args.input, temp_dir)
        output_frames_dir = os.path.join(temp_dir, "output_frames")
        upscale_frames(frames_dir, output_frames_dir, args.scale, args.model)
        merge_frames(output_frames_dir, args.input, args.output)
        log_progress(100, 100, "Done!")
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
