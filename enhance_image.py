
import sys
from PIL import Image
import numpy as np
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

input_img = sys.argv[1]
output_img = f"enhanced_{input_img}"

model = RRDBNet(num_in_ch=3, num_out_ch=3, nf=64, nb=23, scale=4)
upscaler = RealESRGANer(scale=4, model_path='RealESRGAN_x4plus.pth', model=model, tile=0, tile_pad=10)

img = Image.open(input_img).convert("RGB")
_, _, output = upscaler.enhance(np.array(img), outscale=4)

Image.fromarray(output).save(output_img)
