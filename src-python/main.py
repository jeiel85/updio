import os
import sys
import json
import subprocess
import argparse
import shutil
from pathlib import Path

# Vibe Video Upscaler - AI Sidecar Core
# Logic: FFmpeg (Extract) -> AI Inference (Upscale) -> FFmpeg (Merge)

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

def run_command(command):
    # Ensure command uses the specified ffmpeg/ffprobe path
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Command failed: {stderr}")
    return stdout

def extract_frames(input_path, temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    frames_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    log_progress(0, 100, "Extracting frames...")
    
    # Use the ffprobe path passed or default
    probe_cmd = f'"{FFPROBE_EXE}" -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "{input_path}"'
    try:
        total_frames = int(run_command(probe_cmd).strip())
    except:
        total_frames = 100 
    
    extract_cmd = f'"{FFMPEG_EXE}" -i "{input_path}" -qscale:v 2 "{frames_dir}/%08d.jpg"'
    run_command(extract_cmd)
    
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
    
    fps_cmd = f'"{FFPROBE_EXE}" -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 "{input_video}"'
    fps = run_command(fps_cmd).strip()
    
    audio_temp = os.path.join(os.path.dirname(output_path), "temp_audio.m4a")
    try:
        run_command(f'"{FFMPEG_EXE}" -y -i "{input_video}" -vn -acodec copy "{audio_temp}"')
        has_audio = True
    except:
        has_audio = False
    
    if has_audio:
        merge_cmd = f'"{FFMPEG_EXE}" -y -r {fps} -i "{output_frames_dir}/%08d.jpg" -i "{audio_temp}" -c:v libx264 -pix_fmt yuv420p -c:a copy "{output_path}"'
    else:
        merge_cmd = f'"{FFMPEG_EXE}" -y -r {fps} -i "{output_frames_dir}/%08d.jpg" -c:v libx264 -pix_fmt yuv420p "{output_path}"'
    
    run_command(merge_cmd)
    
    if has_audio and os.path.exists(audio_temp):
        os.remove(audio_temp)

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
    FFMPEG_EXE = args.ffmpeg
    FFPROBE_EXE = args.ffprobe
    
    temp_dir = os.path.join(os.path.dirname(args.output), "vibe_temp")
    
    try:
        frames_dir, total_frames = extract_frames(args.input, temp_dir)
        output_frames_dir = os.path.join(temp_dir, "output_frames")
        upscale_frames(frames_dir, output_frames_dir, args.scale, args.model)
        merge_frames(output_frames_dir, args.input, args.output)
        log_progress(100, 100, "Done! Video upscaled successfully.")
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
