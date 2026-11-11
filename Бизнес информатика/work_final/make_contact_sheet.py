from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика\work_final\deck_screenshots")
paths = [root / f"page-{i}.png" for i in range(1, 11)]
thumb_w, thumb_h = 640, 360
label_h = 30
sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * 5), "white")
draw = ImageDraw.Draw(sheet)
for i, path in enumerate(paths):
    im = Image.open(path).convert("RGB")
    im.thumbnail((thumb_w, thumb_h))
    x = (i % 2) * thumb_w
    y = (i // 2) * (thumb_h + label_h)
    sheet.paste(im, (x, y))
    draw.text((x + 10, y + thumb_h + 6), f"Слайд {i + 1}", fill="#1F4E79")
out = root / "contact_sheet_final.jpg"
sheet.save(out, quality=90, optimize=True)
for path in paths + [out]:
    print(f"{path.name}: {path.stat().st_size} bytes")
