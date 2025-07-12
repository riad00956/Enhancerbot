import sys
from PIL import Image
import numpy as np
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import os

if len(sys.argv) != 3:
    print("Usage: python enhance_image.py <input_image_path> <output_image_path>")
    sys.exit(1)

input_img_path = sys.argv[1]
output_img_path = sys.argv[2]

# Check if model file exists, if not, it should have been downloaded by startCommand
model_path = 'RealESRGAN_x4plus.pth'
if not os.path.exists(model_path):
    print(f"Error: Model file '{model_path}' not found. Please ensure it is downloaded.")
    sys.exit(1)

try:
    # Load model
    model = RRDBNet(num_in_ch=3, num_out_ch=3, nf=64, nb=23, scale=4)
    # Ensure model is on CPU if CUDA is not available or desired for small instances
    # If running on a GPU instance, you might want to specify device='cuda'
    upscaler = RealESRGANer(
        scale=4,
        model_path=model_path,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False # Use half=True for faster inference with FP16 on compatible GPUs
    )

    img = Image.open(input_img_path).convert("RGB")
    
    # RealESRGAN expects a NumPy array
    img_np = np.array(img)

    print(f"Enhancing {os.path.basename(input_img_path)}...")
    _, _, output_np = upscaler.enhance(img_np, outscale=4)

    # Convert back to PIL Image and save
    Image.fromarray(output_np).save(output_img_path)
    print(f"Image enhanced and saved to {output_img_path}")

except Exception as e:
    print(f"Error during image enhancement for {input_img_path}: {e}")
    sys.exit(1)

