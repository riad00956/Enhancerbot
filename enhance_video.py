import sys
import os
import subprocess
import shutil # For rmtree

if len(sys.argv) != 3:
    print("Usage: python enhance_video.py <input_video_path> <output_video_path>")
    sys.exit(1)

input_video = sys.argv[1]
output_video = sys.argv[2]

# Define temporary directories relative to where enhance_video.py is run
# This assumes bot.py sets the current working directory, or temp_files is global
TEMP_DIR = "temp_files" # Needs to match bot.py's TEMP_DIR for consistent cleanup
FRAME_DIR = os.path.join(TEMP_DIR, "frames")
ENHANCED_FRAME_DIR = os.path.join(TEMP_DIR, "enhanced_frames")


# Clean up and create directories for this run
if os.path.exists(FRAME_DIR):
    shutil.rmtree(FRAME_DIR)
if os.path.exists(ENHANCED_FRAME_DIR):
    shutil.rmtree(ENHANCED_FRAME_DIR)

os.makedirs(FRAME_DIR, exist_ok=True)
os.makedirs(ENHANCED_FRAME_DIR, exist_ok=True)


print(f"Extracting frames from {input_video} to {FRAME_DIR}...")
try:
    subprocess.run(
        ["ffmpeg", "-i", input_video, f"{FRAME_DIR}/frame_%05d.png"],
        capture_output=True, text=True, check=True
    )
except subprocess.CalledProcessError as e:
    print(f"FFmpeg frame extraction failed:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
    sys.exit(1)

frames = sorted(os.listdir(FRAME_DIR))
total_frames = len(frames)
print(f"Found {total_frames} frames. Enhancing...")

for i, frame_name in enumerate(frames):
    input_frame_path = os.path.join(FRAME_DIR, frame_name)
    output_frame_path = os.path.join(ENHANCED_FRAME_DIR, frame_name) # Save enhanced frame directly to enhanced dir

    print(f"Enhancing frame {i+1}/{total_frames}: {frame_name}...")
    try:
        subprocess.run(
            ["python", "enhance_image.py", input_frame_path, output_frame_path],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error enhancing frame {frame_name}:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        # Continue to next frame or exit, depending on desired robustness
        # For now, we'll exit to indicate a problem
        sys.exit(1)

print(f"Combining enhanced frames from {ENHANCED_FRAME_DIR} into {output_video}...")
try:
    # Get original video's framerate for re-encoding, if possible
    # A more robust solution would extract this with ffprobe
    # For simplicity, assuming a default framerate (e.g., 30) or trying to match input
    subprocess.run([
        "ffmpeg", "-framerate", "30", "-i", f"{ENHANCED_FRAME_DIR}/frame_%05d.png",
        "-i", input_video, "-map", "0:v", "-map", "1:a?", # Use 1:a? to make audio optional
        "-c:v", "libx264", "-pix_fmt", "yuv420p", # Ensure compatible pixel format for most players
        "-preset", "medium", "-crf", "23", # Balance quality and file size
        "-c:a", "copy", output_video
    ], capture_output=True, text=True, check=True)
    print("Video enhancement complete.")

except subprocess.CalledProcessError as e:
    print(f"FFmpeg video re-encoding failed:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
    sys.exit(1)
finally:
    # Clean up frame directories at the end of enhancement
    if os.path.exists(FRAME_DIR):
        shutil.rmtree(FRAME_DIR)
    if os.path.exists(ENHANCED_FRAME_DIR):
        shutil.rmtree(ENHANCED_FRAME_DIR)

