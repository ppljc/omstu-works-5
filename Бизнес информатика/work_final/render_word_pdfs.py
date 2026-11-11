from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика\work_final")
JOBS = [
    ("passport_preview", "passport_render", "Паспорт"),
    ("speech_preview", "speech_render", "Выступление"),
]
for pdf_stem, out_name, label in JOBS:
    pdf_path = ROOT / f"{pdf_stem}.pdf"
    out_dir = ROOT / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    page_paths = []
    for index, page in enumerate(doc):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5), alpha=False)
        page_path = out_dir / f"page-{index + 1:02d}.png"
        pix.save(page_path)
        page_paths.append(page_path)
    print(f"{label}: {len(page_paths)} страниц")
    for group_start in range(0, len(page_paths), 4):
        group = page_paths[group_start:group_start + 4]
        thumb_w, thumb_h, label_h = 500, 707, 28
        sheet = Image.new("RGB", (thumb_w * 2, (thumb_h + label_h) * 2), "#D9E1EC")
        draw = ImageDraw.Draw(sheet)
        for j, path in enumerate(group):
            im = Image.open(path).convert("RGB")
            im.thumbnail((thumb_w - 8, thumb_h - 8))
            x = (j % 2) * thumb_w + (thumb_w - im.width) // 2
            y = (j // 2) * (thumb_h + label_h) + 4
            sheet.paste(im, (x, y))
            draw.text(((j % 2) * thumb_w + 8, (j // 2) * (thumb_h + label_h) + thumb_h + 5),
                      f"{label}, страница {group_start + j + 1}", fill="#1F4E79")
        sheet_path = out_dir / f"sheet-{group_start // 4 + 1:02d}.jpg"
        sheet.save(sheet_path, quality=90, optimize=True)
        print(f"{sheet_path.name}: {sheet_path.stat().st_size} bytes")
