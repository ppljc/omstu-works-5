from pathlib import Path
from pptx import Presentation

root = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика\БИ")
out = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика\work_final")
for name in ["БИитог.pptx", "Ценностное предложение.pptx"]:
    prs = Presentation(root / name)
    lines = [f"FILE: {name}", f"SLIDES: {len(prs.slides)}", f"SIZE_EMU: {prs.slide_width} x {prs.slide_height}"]
    for i, slide in enumerate(prs.slides, 1):
        lines.append(f"\n=== SLIDE {i} ===")
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False):
                text = " | ".join(p.text for p in shape.text_frame.paragraphs if p.text.strip())
                if text.strip():
                    lines.append(f"TEXT [{shape.left},{shape.top},{shape.width},{shape.height}]: {text}")
            elif shape.shape_type == 13:
                lines.append(f"IMAGE [{shape.left},{shape.top},{shape.width},{shape.height}]: {shape.name}")
            elif getattr(shape, "has_table", False):
                lines.append("TABLE:")
                for row in shape.table.rows:
                    lines.append(" || ".join(cell.text.replace("\n", " | ") for cell in row.cells))
            elif getattr(shape, "has_chart", False):
                lines.append(f"CHART: {shape.name}")
        if slide.has_notes_slide:
            note = slide.notes_slide.notes_text_frame.text.strip()
            if note:
                lines.append(f"NOTES: {note}")
    (out / f"{Path(name).stem}_structure.txt").write_text("\n".join(lines), encoding="utf-8")
    print(name, len(prs.slides))
