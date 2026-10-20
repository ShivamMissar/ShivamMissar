"""Stage A of the ASCII portrait: cut out the background and boost local contrast.

usage: python scripts/prep_photo.py <photo> [out.png]

Output is a grayscale+alpha PNG: L = CLAHE-boosted luminance, A = subject mask.
Background removal uses rembg when it's installed; without it the whole frame is kept.
"""
import sys
import os

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "portrait-prepped.png")

img = ImageOps.exif_transpose(Image.open(src)).convert("RGBA")

try:
    from rembg import remove  # heavy (downloads a model); runs in CI, optional locally
    img = remove(img)
    print("background removed with rembg")
except Exception as e:  # not installed, or model download failed
    print(f"rembg unavailable ({type(e).__name__}): keeping original background")

# square-crop around the subject so the portrait fills the frame
alpha = np.array(img.split()[-1])
ys, xs = np.where(alpha > 32)
if len(xs):
    cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
    half = int(max(xs.max() - xs.min(), ys.max() - ys.min()) * 0.55)
    img = img.crop((cx - half, cy - half, cx + half, cy + half))

rgb = np.array(img.convert("RGB"))
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
gray = clahe.apply(gray)
mask = np.array(img.split()[-1])

os.makedirs(os.path.dirname(out), exist_ok=True)
Image.merge("LA", (Image.fromarray(gray), Image.fromarray(mask))).save(out)
print("wrote", out)
