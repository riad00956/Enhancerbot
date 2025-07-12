
import sys
import os
import subprocess

input_video = sys.argv[1]
frame_dir = "frames"
enhanced_dir = "enhanced_frames"
output_video = f"enhanced_{input_video}"

os.makedirs(frame_dir, exist_ok=True)
os.makedirs(enhanced_dir, exist_ok=True)

subprocess.run(["ffmpeg", "-i", input_video, f"{frame_dir}/frame_%05d.png"])
for frame in os.listdir(frame_dir):
    subprocess.run(["python", "enhance_image.py", f"{frame_dir}/{frame}"])
    os.rename(f"enhanced_{frame_dir}/{frame}", f"{enhanced_dir}/{frame}")

subprocess.run([
    "ffmpeg", "-framerate", "30", "-i", f"{enhanced_dir}/frame_%05d.png",
    "-i", input_video, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
    "-c:a", "copy", output_video
])
