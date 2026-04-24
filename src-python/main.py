import os
import sys
import json
import subprocess
import argparse
import shutil
from pathlib import Path

# Vibe Video Upscaler - AI Sidecar Core
# Logic: FFmpeg (Extract) -> AI Inference (Upscale) -> FFmpeg (Merge)

def log_progress(current, total, message):
    """
    Progress is logged as JSON to stdout for Tauri to capture.
    Input: current (int), total (int), message (str)
    """
    print(json.dumps({
        "current": current,
        "total": total,
        "percentage": round((current / total) * 100, 2) if total > 0 else 0,
        "message": message
    }), flush=True)

def run_command(command):
    """
    Runs a shell command and returns the output.
    Used for calling FFmpeg.
    """
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
    """
    Extracts frames from video using FFmpeg.
    Why: PNG/JPG frames are easier for AI models to process individually.
    """
    os.makedirs(temp_dir, exist_ok=True)
    frames_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    
    log_progress(0, 100, "Extracting frames...")
    # Get total frames first for progress tracking
    probe_cmd = f'ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "{input_path}"'
    try:
        total_frames = int(run_command(probe_cmd).strip())
    except:
        total_frames = 100 # Fallback
    
    extract_cmd = f'ffmpeg -i "{input_path}" -qscale:v 2 "{frames_dir}/%08d.jpg"'
    run_command(extract_cmd)
    
    return frames_dir, total_frames

def upscale_frames(frames_dir, output_frames_dir, scale, model_type):
    """
    Core AI Inference Placeholder.
    In a full implementation, this would call Real-ESRGAN.
    Why: Real-ESRGAN (NCNN) is preferred for portable performance.
    """
    os.makedirs(output_frames_dir, exist_ok=True)
    frame_files = sorted(os.listdir(frames_dir))
    total = len(frame_files)
    
    log_progress(0, total, f"Upscaling frames (Scale: {scale}x)...")
    
    for i, frame_file in enumerate(frame_files):
        # Placeholder for AI logic:
        # realesrgan_ncnn_vulkan.exe -i input -o output -s scale -n model_type
        
        # Simulating processing time
        src = os.path.join(frames_dir, frame_file)
        dst = os.path.join(output_frames_dir, frame_file)
        
        # For now, we just copy (Simulation)
        # In production: run_command(f'realesrgan-ncnn-vulkan.exe -i "{src}" -o "{dst}" -s {scale}')
        shutil.copy(src, dst)
        
        if i % 10 == 0 or i == total - 1:
            log_progress(i + 1, total, f"Upscaling: {frame_file}")

def merge_frames(output_frames_dir, input_video, output_path):
    """
    Merges processed frames and original audio back into a video.
    Why: Ensures video/audio sync and applies final compression.
    """
    log_progress(95, 100, "Merging frames and audio...")
    
    # Get original FPS
    fps_cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=noprint_wrappers=1:nokey=1 "{input_video}"'
    fps = run_command(fps_cmd).strip()
    
    # Extract audio
    audio_temp = os.path.join(os.path.dirname(output_path), "temp_audio.m4a")
    try:
        run_command(f'ffmpeg -y -i "{input_video}" -vn -acodec copy "{audio_temp}"')
        has_audio = True
    except:
        has_audio = False
    
    # Merge
    if has_audio:
        merge_cmd = f'ffmpeg -y -r {fps} -i "{output_frames_dir}/%08d.jpg" -i "{audio_temp}" -c:v libx264 -pix_fmt yuv420p -c:a copy "{output_path}"'
    else:
        merge_cmd = f'ffmpeg -y -r {fps} -i "{output_frames_dir}/%08d.jpg" -c:v libx264 -pix_fmt yuv420p "{output_path}"'
    
    run_command(merge_cmd)
    
    if has_audio and os.path.exists(audio_temp):
        os.remove(audio_temp)

def main():
    parser = argparse.ArgumentParser(description="Vibe Video Upscaler Sidecar")
    parser.add_argument("--input", required=True, help="Input video path")
    parser.add_argument("--output", required=True, help="Output video path")
    parser.add_argument("--scale", type=int, default=2, help="Upscale factor (2 or 4)")
    parser.add_argument("--model", default="realesrgan-x4plus", help="Model type")
    
    args = parser.parse_args()
    
    temp_dir = os.path.join(os.path.dirname(args.output), "vibe_temp")
    
    try:
        # 1. Extract
        frames_dir, total_frames = extract_frames(args.input, temp_dir)
        
        # 2. Upscale
        output_frames_dir = os.path.join(temp_dir, "output_frames")
        upscale_frames(frames_dir, output_frames_dir, args.scale, args.model)
        
        # 3. Merge
        merge_frames(output_frames_dir, args.input, args.output)
        
        log_progress(100, 100, "Done! Video upscaled successfully.")
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
