"""Prep a portrait for ASCII: remove background, CLAHE contrast, composite on white.

usage: python scripts/prep_photo.py source-photo.jpg [source-prepped.png]
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
out = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"

rgba = np.array(remove(Image.open(src).convert("RGB")))
gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
alpha = rgba[..., 3].astype(np.float32) / 255
result = (gray * alpha + 255 * (1 - alpha)).astype(np.uint8)  # background -> white

# recorta al sujeto con un pequeño margen
result = np.dstack([result, rgba[..., 3]])  # conserva el alfa como máscara del sujeto
ys, xs = np.nonzero(rgba[..., 3] > 16)
if xs.size:
    m = int(0.03 * max(result.shape[:2]))
    result = result[max(ys.min() - m, 0):ys.max() + m, max(xs.min() - m, 0):xs.max() + m]

Image.fromarray(result, "LA").save(out)
print(f"-> {out} {result.shape[1]}x{result.shape[0]}")
