from pathlib import Path

from PIL import Image

src = Path(__file__).resolve().parents[1] / "FineFits-icon.png"
out = Path(__file__).resolve().parents[1] / "frontend" / "public"
out.mkdir(parents=True, exist_ok=True)

img = Image.open(src).convert("RGBA")

w, h = img.size
if w != h:
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))

sizes = {
    "icon-16.png": 16,
    "icon-32.png": 32,
    "apple-touch-icon.png": 180,
    "icon-192.png": 192,
    "icon-512.png": 512,
    "logo.png": 256,
}

for name, size in sizes.items():
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(out / name, format="PNG", optimize=True)

ico_sizes = [16, 32, 48]
ico_images = [img.resize((s, s), Image.Resampling.LANCZOS) for s in ico_sizes]
ico_images[0].save(
    out / "favicon.ico",
    format="ICO",
    sizes=[(s, s) for s in ico_sizes],
    append_images=ico_images[1:],
)

print("Generated icons in", out)
