"""Script to generate font-models (Python 3 compatible).

Builds a per-font linear model mapping point size (y) to glyph
pixel height (h): h ≈ a*y + b. Results are saved as a pickle dict
mapping font name -> np.array([a, b]).
"""

import os
import argparse
import pygame
from pygame import freetype
from text_utils import FontState
import numpy as np
import matplotlib.pyplot as plt
import pickle as cp


pygame.init()
try:
	freetype.init()
except Exception:
	pass


ys = np.arange(8, 200)
A = np.c_[ys, np.ones_like(ys)]

xs = []
models = {}  # linear model

# Output directory name for visualization plots
OUTDIR = "font_model_plots"

parser = argparse.ArgumentParser(description="Generate per-font linear models of glyph height vs point size.")
parser.add_argument("--viz", action="store_true", help="Save diagnostic plots for each font")
args = parser.parse_args()
VIZ = args.viz

FS = FontState()
print("Total fonts:", len(FS.fonts))
plots_dir = None
if VIZ:
	plots_dir = os.path.join(os.path.dirname(__file__), "results", OUTDIR)
	os.makedirs(plots_dir, exist_ok=True)
# plt.figure()
for i in range(len(FS.fonts)):
	font_path = FS.fonts[i]
	try:
		font = freetype.Font(font_path, size=12)
	except Exception as e:
		print("Skipping font (failed to load):", font_path, "-", e)
		continue
	print("Processing:", getattr(font, "name", os.path.basename(font_path)))
	h = []
	for y in ys:
		h.append(font.get_sized_glyph_height(float(y)))
	h = np.array(h)
	m, _, _, _ = np.linalg.lstsq(A, h)
	models[font.name] = m
	xs.append(h)

	if VIZ:
		try:
			yhat = A @ m
			fig = plt.figure(figsize=(5, 3))
			plt.plot(ys, h, label="measured h(y)")
			plt.plot(ys, yhat, label="linear fit")
			plt.xlabel("point size y")
			plt.ylabel("glyph height h")
			plt.title("{}".format(font.name))
			plt.grid(True, alpha=0.3)
			plt.legend(fontsize=8)
			plt.tight_layout()
			safe_fontname = "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in font.name)
			dir_name = os.path.basename(os.path.dirname(font_path))
			file_stem = os.path.splitext(os.path.basename(font_path))[0]
			safe_dir = "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in dir_name)
			safe_stem = "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in file_stem)
			filename = "{}__{}__{}__{}.png".format(safe_fontname, safe_dir, safe_stem, i)
			fig.savefig(os.path.join(plots_dir, filename), dpi=150)
			plt.close(fig)
		except Exception as e:
			print("Plot save failed for", font.name, "-", e)

out_dir = os.path.join(os.path.dirname(__file__), "data", "models")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "font_px2pt.cp")
with open(out_path, "wb") as f:
    cp.dump(models, f)
print("Saved:", out_path)