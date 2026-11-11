from pathlib import Path
import sys
from copy import deepcopy

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.shared import Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика")
UNPACKED = ROOT / "work_pz5" / "sample" / "unpacked"
VERIFY_DIR = Path(r"C:\Users\ppljc\AppData\Roaming\kimi-desktop\daimon-share\daimon\runtime\kimi-code\home\plugins\managed\kimi-word\skills\kimi-word\scripts\verify")
sys.path.insert(0, str(VERIFY_DIR))
from opc import edit_docx

FONT = "Times New Roman"
BODY_SIZE = Pt(14)
TABLE_SIZE = Pt(11)
TEXT_WIDTH_PT = 467.75


def set_run(run, size=BODY_SIZE, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    return run


def set_paragraph_format(p, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY, first=True,
                         line=1.5, before=0, after=0, keep_next=False):
    p.alignment = align
    pf = p.paragraph_format
    pf.first_line_indent = Cm(1.25) if first else Cm(0)
    pf.line_spacing = line
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.keep_with_next = keep_next
    return p


def add_p(doc, text="", *, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
          first=True, size=BODY_SIZE, before=0, after=0, keep_next=False):
    p = doc.add_paragraph()
    set_paragraph_format(p, align=align, first=first, before=before, after=after, keep_next=keep_next)
    if text:
        set_run(p.add_run(text), size=size, bold=bold, italic=italic)
    return p


def add_heading(doc, text, page_break=False):
    if page_break:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.add_run().add_break(WD_BREAK.PAGE)
    return add_p(doc, text, bold=True, first=False, before=0, after=0, keep_next=True)


def add_caption(doc, text):
    return add_p(doc, text, first=False, keep_next=True)


def set_cell_shading(cell, fill="D9D9D9"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=60, start=70, bottom=60, end=70):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def set_cell(cell, text, *, size=TABLE_SIZE, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT,
             fill=None, first=False):
    cell.text = ""
    p = cell.paragraphs[0]
    set_paragraph_format(p, align=align, first=first, line=1.0)
    set_run(p.add_run(str(text)), size=size, bold=bold)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)
    if fill:
        set_cell_shading(cell, fill)
    return cell


def set_table_width(table, widths_pt):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    total = int(round(sum(widths_pt) * 20))
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(total))
    tbl_w.set(qn("w:type"), "dxa")
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            if idx < len(widths_pt):
                cell.width = Pt(widths_pt[idx])
                tc_pr = cell._tc.get_or_add_tcPr()
                tc_w = tc_pr.find(qn("w:tcW"))
                if tc_w is not None:
                    tc_w.set(qn("w:w"), str(int(round(widths_pt[idx] * 20))))
                    tc_w.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_pt:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(int(round(width * 20))))
        grid.append(col)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    set_run(run, size=Pt(12))
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_begin, instr, fld_sep, text, fld_end])


S = [
    "Единый цикл «продукты дома — рецепт — меню — список покупок — контроль сроков годности»",
    "Распознавание продуктов по фото и быстрый ручной ввод",
    "Комплексный функционал: напоминания о сроках годности, автосписок покупок и меню на неделю",
    "Персонализация: фильтры по рациону, расчёт калорийности и стоимости блюд",
    "Понятная ценность для пользователя: экономия времени и денег, сокращение пищевых отходов",
    "Масштабируемая модель Freemium с дополнительными B2B-источниками дохода",
]
W = [
    "Небольшая стартовая база рецептов и отсутствие сформированного сообщества",
    "Зависимость качества сервиса от точности распознавания и актуальности вводимых данных",
    "Низкая узнаваемость нового продукта и риск недостаточного удержания пользователей",
    "Зависимость от магазинов приложений, облачных ML-сервисов и API партнёров",
    "Значительные затраты на разработку, контент и безопасность при неопределённой готовности платить",
]
O = [
    "Рост цен на продукты питания и повышение интереса к экономии семейного бюджета",
    "Рост интереса к осознанному потреблению и снижению пищевых отходов",
    "Развитие ИИ и компьютерного зрения для распознавания продуктов и рекомендаций",
    "Развитие сервисов доставки продуктов и открытых API для интеграций",
    "Популярность здорового питания, контроля КБЖУ и персональных программ питания",
]
T = [
    "Ужесточение требований к персональным данным и рост киберугроз",
    "Снижение реальных доходов населения и готовности оплачивать подписки",
    "Конкуренция с Supercook, Cookpad, «Едим Дома» и сервисами доставки готовой еды",
    "Ограничения для иностранного ПО, магазинов приложений и облачных сервисов",
    "Рост стоимости технологической инфраструктуры и зависимость от внешних провайдеров",
]

ST = [
    [3, 3, 2, 4, 3, 3],
    [4, 3, 4, 3, 5, 5],
    [5, 4, 5, 4, 4, 4],
    [3, 4, 3, 3, 3, 5],
    [3, 4, 3, 4, 3, 5],
]
WT = [
    [3, 3, 3, 4, 4],
    [2, 2, 3, 2, 4],
    [4, 3, 4, 3, 3],
    [2, 3, 2, 4, 3],
    [3, 3, 2, 4, 4],
]
SO = [
    [5, 3, 4, 4, 5, 4],
    [4, 3, 5, 3, 5, 4],
    [4, 5, 4, 5, 3, 4],
    [4, 3, 5, 3, 4, 5],
    [3, 3, 4, 5, 4, 4],
]
WO = [
    [3, 3, 3, 2, 4],
    [3, 3, 4, 2, 4],
    [4, 5, 3, 4, 4],
    [4, 3, 3, 5, 4],
    [5, 3, 3, 2, 4],
]

s_totals = [sum(SO[r][c] for r in range(5)) + sum(ST[r][c] for r in range(5)) for c in range(6)]
w_totals = [sum(WO[r][c] for r in range(5)) + sum(WT[r][c] for r in range(5)) for c in range(5)]
o_totals = [sum(SO[r]) + sum(WO[r]) for r in range(5)]
t_totals = [sum(ST[r]) + sum(WT[r]) for r in range(5)]
so_total = sum(map(sum, SO))
st_total = sum(map(sum, ST))
wo_total = sum(map(sum, WO))
wt_total = sum(map(sum, WT))

solutions = [
    ("S–O", "S1 + O1", "Запустить кампанию «Готовь из того, что есть — экономь каждый день» с акцентом на снижение расходов на продукты.", 15),
    ("S–O", "S2 + O3", "Развивать ИИ-распознавание продуктов по фото и персональные рекомендации с быстрой ручной коррекцией.", 14),
    ("S–O", "S3 + O2", "Добавить личную статистику использованных продуктов, сэкономленных средств и предотвращённых пищевых отходов.", 13),
    ("S–O", "S3 + O4", "Интегрировать автосписок покупок с сервисами доставки для заказа недостающих продуктов.", 14),
    ("S–O", "S4 + O5", "Создать проверенные нутрициологами шаблоны меню с расчётом КБЖУ, фильтрами по рациону и аллергенам.", 12),
    ("S–O", "S6 + O1", "Сохранить бюджетные рецепты и базовый учёт продуктов в бесплатной версии, вынося расширенную аналитику в Premium.", 11),
    ("S–T", "S1 + T3", "Позиционировать FridgeChef как решение полного цикла домашнего питания, а не очередной каталог рецептов.", 13),
    ("S–T", "S4 + T1", "Внедрить минимизацию собираемых данных, явное согласие и автоматическое удаление фотографий после распознавания.", 15),
    ("S–T", "S6 + T2", "Предложить пробный период, семейный и годовой тарифы, а также разовые покупки тематических меню.", 12),
    ("S–T", "S6 + T4", "Обеспечить публикацию в RuStore, альтернативную оплату подписки и переносимость облачной инфраструктуры.", 13),
    ("S–T", "S5 + T3", "Показывать в маркетинге измеримую выгоду: минуты на поиск рецепта, стоимость блюда и количество сэкономленных продуктов.", 10),
    ("W–O", "W1 + O5", "Привлечь нутрициологов, шеф-поваров и фуд-блогеров к наполнению и проверке базы рецептов.", 14),
    ("W–O", "W2 + O3", "Сформировать набор размеченных данных и механизм обратной связи для регулярного дообучения модели распознавания.", 13),
    ("W–O", "W3 + O2", "Запустить сообщество и челлендж «Неделя без выброшенной еды» для вовлечения и удержания пользователей.", 10),
    ("W–O", "W4 + O4", "Создать единый партнёрский модуль для подключения нескольких служб доставки без привязки к одному оператору.", 11),
    ("W–O", "W5 + O1", "Использовать бесплатные бюджетные функции для роста аудитории и монетизировать дополнительные возможности поэтапно.", 9),
    ("W–T", "W2 + T1", "Внедрить шифрование, разграничение доступа и резервный ручной сценарий без обязательной загрузки фотографий.", 14),
    ("W–T", "W3 + T2", "Снизить барьер входа сильной бесплатной версией, простым онбордингом и полезными напоминаниями вместо агрессивной монетизации.", 11),
    ("W–T", "W4 + T4", "Использовать отечественные облачные и платёжные сервисы, RuStore и распространение через официальный сайт.", 12),
    ("W–T", "W4 + T5", "Проектировать независимую от провайдера архитектуру и регулярно контролировать стоимость ML-вычислений и интеграций.", 9),
]


def add_cover(doc):
    for text in [
        "Федеральное государственное автономное образовательное",
        "учреждение высшего образования",
    ]:
        add_p(doc, text, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "", align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "«ОМСКИЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ»",
          bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "Кафедра математических методов и\nинформационных технологий в экономике",
          bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    for _ in range(3):
        add_p(doc, "", align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "Отчет по практическому занятию №5", bold=True,
          align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "по дисциплине", align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "«Бизнес-информатика»", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    add_p(doc, "по проекту «FridgeChef»", align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    for _ in range(2):
        add_p(doc, "", first=False)
    for text in [
        "Выполнили ст. гр. ИВТ-244",
        "__________А. Д. Фельдт",
        "__________С. Д. Ахмедеев",
        "__________А. В. Шмидт",
        '"____"___________20__г.',
        "Принял",
        "_________О. Г. Шевелева",
        '"____"___________20__ г.',
    ]:
        p = add_p(doc, text, first=False)
        p.paragraph_format.left_indent = Cm(9.5)
    for _ in range(2):
        add_p(doc, "", first=False)
    p = add_p(doc, "Омск 2026", align=WD_ALIGN_PARAGRAPH.CENTER, first=False)
    p.add_run().add_break(WD_BREAK.PAGE)


def add_swot_table(doc):
    table = doc.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    groups = [
        (table.cell(0, 0), "Сильные стороны", "S", S),
        (table.cell(0, 1), "Возможности", "O", O),
        (table.cell(1, 0), "Слабые стороны", "W", W),
        (table.cell(1, 1), "Угрозы", "T", T),
    ]
    for cell, title, prefix, items in groups:
        cell.text = ""
        p = cell.paragraphs[0]
        set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, line=1.0)
        set_run(p.add_run(title), size=TABLE_SIZE, bold=True)
        set_cell_shading(cell, "E7E6E6")
        for idx, item in enumerate(items, 1):
            p = cell.add_paragraph()
            set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, first=False, line=1.0)
            set_run(p.add_run(f"{prefix}{idx}. {item}"), size=Pt(10))
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        set_cell_margins(cell)
    set_table_width(table, [233.8, 233.8])
    return table


def add_cross_matrix(doc):
    table = doc.add_table(rows=15, cols=15)
    table.style = "Table Grid"
    size = Pt(8)
    center = WD_ALIGN_PARAGRAPH.CENTER
    for row in table.rows:
        prevent_row_split(row)
        for c in row.cells:
            set_cell(c, "", size=size, align=center)
    table.cell(0, 0).merge(table.cell(1, 1))
    set_cell(table.cell(0, 0), "Факторы", size=size, bold=True, align=center, fill="D9D9D9")
    table.cell(0, 2).merge(table.cell(0, 7))
    set_cell(table.cell(0, 2), "Сильные стороны", size=size, bold=True, align=center, fill="D9D9D9")
    table.cell(0, 8).merge(table.cell(1, 8))
    set_cell(table.cell(0, 8), "∑(T)", size=size, bold=True, align=center, fill="E7E6E6")
    table.cell(0, 9).merge(table.cell(0, 13))
    set_cell(table.cell(0, 9), "Слабые стороны", size=size, bold=True, align=center, fill="D9D9D9")
    table.cell(0, 14).merge(table.cell(1, 14))
    set_cell(table.cell(0, 14), "∑(T)", size=size, bold=True, align=center, fill="E7E6E6")
    for c in range(6):
        set_cell(table.cell(1, 2 + c), f"S{c+1}", size=size, bold=True, align=center, fill="E7E6E6")
    for c in range(5):
        set_cell(table.cell(1, 9 + c), f"W{c+1}", size=size, bold=True, align=center, fill="E7E6E6")
    table.cell(2, 0).merge(table.cell(6, 0))
    set_cell(table.cell(2, 0), "Угрозы", size=size, bold=True, align=center, fill="E7E6E6")
    for r in range(5):
        rr = 2 + r
        set_cell(table.cell(rr, 1), f"T{r+1}", size=size, bold=True, align=center, fill="E7E6E6")
        for c in range(6):
            set_cell(table.cell(rr, 2+c), ST[r][c], size=size, align=center)
        set_cell(table.cell(rr, 8), sum(ST[r]), size=size, bold=True, align=center, fill="F2F2F2")
        for c in range(5):
            set_cell(table.cell(rr, 9+c), WT[r][c], size=size, align=center)
        set_cell(table.cell(rr, 14), sum(WT[r]), size=size, bold=True, align=center, fill="F2F2F2")
    set_cell(table.cell(7, 0), "∑", size=size, bold=True, align=center, fill="E7E6E6")
    set_cell(table.cell(7, 1), "∑(S)", size=size, bold=True, align=center, fill="E7E6E6")
    for c in range(6):
        set_cell(table.cell(7, 2+c), sum(ST[r][c] for r in range(5)), size=size, bold=True, align=center, fill="F2F2F2")
    set_cell(table.cell(7, 8), st_total, size=size, bold=True, align=center, fill="D9D9D9")
    for c in range(5):
        set_cell(table.cell(7, 9+c), sum(WT[r][c] for r in range(5)), size=size, bold=True, align=center, fill="F2F2F2")
    set_cell(table.cell(7, 14), wt_total, size=size, bold=True, align=center, fill="D9D9D9")
    table.cell(8, 0).merge(table.cell(8, 7))
    set_cell(table.cell(8, 0), "", size=size, align=center)
    set_cell(table.cell(8, 8), "∑(O)", size=size, bold=True, align=center, fill="E7E6E6")
    table.cell(8, 9).merge(table.cell(8, 13))
    set_cell(table.cell(8, 9), "", size=size, align=center)
    set_cell(table.cell(8, 14), "∑(O)", size=size, bold=True, align=center, fill="E7E6E6")
    table.cell(9, 0).merge(table.cell(13, 0))
    set_cell(table.cell(9, 0), "Возможности", size=size, bold=True, align=center, fill="E7E6E6")
    for r in range(5):
        rr = 9 + r
        set_cell(table.cell(rr, 1), f"O{r+1}", size=size, bold=True, align=center, fill="E7E6E6")
        for c in range(6):
            set_cell(table.cell(rr, 2+c), SO[r][c], size=size, align=center)
        set_cell(table.cell(rr, 8), sum(SO[r]), size=size, bold=True, align=center, fill="F2F2F2")
        for c in range(5):
            set_cell(table.cell(rr, 9+c), WO[r][c], size=size, align=center)
        set_cell(table.cell(rr, 14), sum(WO[r]), size=size, bold=True, align=center, fill="F2F2F2")
    set_cell(table.cell(14, 0), "∑", size=size, bold=True, align=center, fill="E7E6E6")
    set_cell(table.cell(14, 1), "∑(S)", size=size, bold=True, align=center, fill="E7E6E6")
    for c in range(6):
        set_cell(table.cell(14, 2+c), sum(SO[r][c] for r in range(5)), size=size, bold=True, align=center, fill="F2F2F2")
    set_cell(table.cell(14, 8), so_total, size=size, bold=True, align=center, fill="D9D9D9")
    for c in range(5):
        set_cell(table.cell(14, 9+c), sum(WO[r][c] for r in range(5)), size=size, bold=True, align=center, fill="F2F2F2")
    set_cell(table.cell(14, 14), wo_total, size=size, bold=True, align=center, fill="D9D9D9")
    widths = [42, 31] + [30.25] * 13
    set_table_width(table, widths)
    return table


def add_summary_table(doc):
    table = doc.add_table(rows=13, cols=4)
    table.style = "Table Grid"
    for r in range(13):
        prevent_row_split(table.rows[r])
    for c, text in enumerate(["Сильные стороны", "", "Слабые стороны", ""]):
        set_cell(table.cell(0, c), text, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    table.cell(0, 0).merge(table.cell(0, 1))
    table.cell(0, 2).merge(table.cell(0, 3))
    for i in range(6):
        set_cell(table.cell(i+1, 0), f"S{i+1}. {S[i]}", size=Pt(10))
        set_cell(table.cell(i+1, 1), s_totals[i], size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        if i < 5:
            set_cell(table.cell(i+1, 2), f"W{i+1}. {W[i]}", size=Pt(10))
            set_cell(table.cell(i+1, 3), w_totals[i], size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        else:
            set_cell(table.cell(i+1, 2), "", size=Pt(10))
            set_cell(table.cell(i+1, 3), "", size=Pt(10))
    for c, text in enumerate(["Возможности", "", "Угрозы", ""]):
        set_cell(table.cell(7, c), text, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    table.cell(7, 0).merge(table.cell(7, 1))
    table.cell(7, 2).merge(table.cell(7, 3))
    for i in range(5):
        set_cell(table.cell(i+8, 0), f"O{i+1}. {O[i]}", size=Pt(10))
        set_cell(table.cell(i+8, 1), o_totals[i], size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell(table.cell(i+8, 2), f"T{i+1}. {T[i]}", size=Pt(10))
        set_cell(table.cell(i+8, 3), t_totals[i], size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_table_width(table, [205, 30, 202.75, 30])
    return table


def add_solutions_table(doc):
    table = doc.add_table(rows=21, cols=3)
    table.style = "Table Grid"
    headers = ["Квадрант", "Пересекаемые факторы", "Предлагаемое решение / мероприятие"]
    for c, h in enumerate(headers):
        set_cell(table.cell(0, c), h, size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    set_repeat_table_header(table.rows[0])
    for i, (quad, factors, text, _) in enumerate(solutions, 1):
        prevent_row_split(table.rows[i])
        set_cell(table.cell(i, 0), quad, size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell(table.cell(i, 1), factors, size=Pt(10), align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell(table.cell(i, 2), text, size=Pt(10))
    set_table_width(table, [55, 80, 332.75])
    return table


def add_scores_table(doc):
    table = doc.add_table(rows=21, cols=2)
    table.style = "Table Grid"
    set_cell(table.cell(0, 0), "Решение / мероприятие / стратегия", size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    set_cell(table.cell(0, 1), "Оценка", size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    set_repeat_table_header(table.rows[0])
    for i, (_, _, text, score) in enumerate(solutions, 1):
        prevent_row_split(table.rows[i])
        set_cell(table.cell(i, 0), f"{i}. {text}", size=Pt(10))
        set_cell(table.cell(i, 1), score, size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_table_width(table, [417.75, 50])
    return table


def add_ranking_table(doc):
    ranks = {}
    for i, (_, _, text, score) in enumerate(solutions, 1):
        ranks.setdefault(score, []).append((i, text))
    table = doc.add_table(rows=len(ranks)+1, cols=3)
    table.style = "Table Grid"
    for c, h in enumerate(["Ранг", "Оценка", "Мероприятие"]):
        set_cell(table.cell(0, c), h, size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    for rank, score in enumerate(sorted(ranks, reverse=True), 1):
        row = table.rows[rank]
        prevent_row_split(row)
        set_cell(row.cells[0], rank, size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell(row.cells[1], score, size=Pt(10), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        row.cells[2].text = ""
        for j, (idx, text) in enumerate(ranks[score]):
            p = row.cells[2].paragraphs[0] if j == 0 else row.cells[2].add_paragraph()
            set_paragraph_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, first=False, line=1.0)
            set_run(p.add_run(f"{idx}. {text}"), size=Pt(10))
        set_cell_margins(row.cells[2])
    set_table_width(table, [45, 50, 372.75])
    return table


with edit_docx(str(UNPACKED)) as doc:
    body = doc._element.body
    sect_pr = body.sectPr
    for child in list(body):
        if child is not sect_pr:
            body.remove(child)

    from docx.enum.style import WD_STYLE_TYPE
    styles_by_lower_name = {style.name.lower(): style for style in doc.styles}
    for style_name in ("Header", "Footer"):
        style = styles_by_lower_name.get(style_name.lower())
        if style is None:
            style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        style._element.set(qn("w:styleId"), style_name)
        style.font.name = FONT
        style.font.size = Pt(12)
        style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = BODY_SIZE
    normal._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)

    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)
    section.header_distance = Cm(1)
    section.footer_distance = Cm(1)
    section.different_first_page_header_footer = True
    section.header.paragraphs[0].text = ""
    section.footer.paragraphs[0].text = ""
    add_page_number(section.footer.paragraphs[0])
    section.first_page_footer.paragraphs[0].text = ""

    add_cover(doc)

    add_heading(doc, "1 Определение внутренних и внешних факторов, влияющих на проект")
    add_p(doc, "Для проведения SWOT-анализа проекта FridgeChef — мобильного приложения, которое подбирает рецепты из имеющихся дома продуктов, контролирует сроки годности, планирует меню и формирует список покупок, — были выделены внутренние факторы (сильные и слабые стороны, контролируемые командой проекта) и внешние факторы (возможности и угрозы макросреды и конкурентного окружения). Состав факторов опирается на карту ценностного предложения, бизнес-модель, конкурентный анализ и PEST-анализ, выполненные в предыдущих практических работах. Результаты представлены в таблице 1.")
    add_caption(doc, "Таблица 1 – SWOT-анализ проекта FridgeChef")
    add_swot_table(doc)
    add_p(doc, "", first=False)

    add_p(doc, "Сильные стороны (Strengths) — внутренние факторы", bold=True, first=False, keep_next=True)
    add_p(doc, "Главной сильной стороной FridgeChef является объединение полного бытового цикла в одном приложении: пользователь вносит продукты, получает подходящие рецепты, планирует меню, формирует список недостающих покупок и отслеживает сроки годности. Конкурентный анализ показал, что Supercook силён в подборе по ингредиентам, а Cookpad и «Едим Дома» — в контенте и сообществе, однако ни один из рассмотренных сервисов не закрывает весь этот цикл комплексно. Распознавание продуктов по фото снижает трудоёмкость ввода, а ручная коррекция сохраняет управляемость процесса. Персональные рекомендации, расчёт калорийности и стоимости блюд расширяют ценность для семей, занятых пользователей и сторонников здорового питания. Экономия времени и денег и сокращение пищевых отходов формируют понятное ценностное предложение. Модель Freemium позволяет наращивать аудиторию на бесплатных функциях и постепенно подключать подписку, партнёрские комиссии и нативные интеграции.")

    add_p(doc, "Слабые стороны (Weaknesses) — внутренние факторы", bold=True, first=False, keep_next=True)
    add_p(doc, "На старте проект уступает крупным кулинарным платформам по объёму проверенной базы рецептов, количеству отзывов и силе сообщества. Качество ключевого сценария зависит от точности компьютерного зрения и дисциплины пользователя при указании остатков и сроков годности: ошибки распознавания или неактуальные данные снижают полезность рекомендаций. Новый сервис не обладает узнаваемым брендом и должен сформировать привычку регулярного использования, поскольку разовое скачивание само по себе не обеспечивает удержания. Дополнительные ограничения создают зависимость от магазинов приложений, облачных ML-сервисов и API служб доставки. Наконец, разработка, наполнение контентом и защита данных требуют затрат ещё до подтверждения устойчивой платёжной конверсии.")

    add_p(doc, "Возможности (Opportunities) — внешние факторы", bold=True, first=False, keep_next=True)
    add_p(doc, "PEST-анализ выделил рост цен на продукты как наиболее значимый фактор внешней среды: он повышает интерес домохозяйств к планированию расходов, бюджетным меню и использованию уже купленных продуктов. Социокультурный тренд на осознанное потребление усиливает спрос на напоминания о сроках годности и статистику сокращения отходов. Развитие ИИ и компьютерного зрения позволяет улучшать распознавание и рекомендации без пропорционального роста ручного труда. Открытые API и партнёрские программы служб доставки открывают путь к оформлению заказа из автосписка и получению комиссий. Интерес к здоровому питанию и контролю КБЖУ создаёт возможности для специализированных меню и сотрудничества с нутрициологами.")

    add_p(doc, "Угрозы (Threats) — внешние факторы", bold=True, first=False, keep_next=True)
    add_p(doc, "Приложение обрабатывает фотографии, предпочтения и сведения о рационе, поэтому требования к защите персональных данных и киберугрозы являются существенными рисками. Снижение располагаемых доходов может ограничить конверсию в Premium и повысить чувствительность аудитории к цене подписки. Конкурентное давление исходит одновременно от сервисов подбора рецептов, крупных кулинарных сообществ и доставки готовой еды, которая сокращает потребность в домашней готовке. Ограничения иностранных магазинов приложений и облачных сервисов способны затронуть распространение, оплату и инфраструктуру. Рост стоимости вычислений и внешних интеграций может увеличить операционные расходы и снизить эффект экономии на масштабе.")

    add_heading(doc, "2 SWOT-матрица перекрестного количественного анализа взаимодействия факторов", page_break=True)
    add_p(doc, "На втором этапе выполнена экспертная оценка взаимодействия внутренних и внешних факторов. Построены четыре перекрёстные матрицы: «сильные стороны — возможности» (S–O), «сильные стороны — угрозы» (S–T), «слабые стороны — возможности» (W–O) и «слабые стороны — угрозы» (W–T). Каждое пересечение оценено по шкале от 1 до 5 баллов, где 1 означает слабое взаимодействие, а 5 — очень сильное, стратегически значимое. Для S–O балл отражает способность сильной стороны усилить использование возможности, для S–T — способность противодействовать угрозе, для W–O — влияние слабой стороны на реализацию возможности, для W–T — уязвимость проекта при совместном действии факторов. Результаты приведены в таблице 2.")
    add_caption(doc, "Таблица 2 – SWOT-таблица перекрестного количественного анализа взаимодействия факторов")
    add_cross_matrix(doc)

    add_caption(doc, "Таблица 3 – Сводная таблица с количественной оценкой важности факторов")
    add_summary_table(doc)
    add_p(doc, f"После суммирования оценок по четырём матрицам наибольший результат получен в квадранте S–O — {so_total} баллов. Это свидетельствует о высоком потенциале использования рыночных возможностей за счёт уже заложенных в концепцию преимуществ. Матрица S–T набрала {st_total} баллов, что показывает наличие содержательных способов защиты от угроз, прежде всего за счёт комплексного функционала и гибкой бизнес-модели. Результат W–O составил {wo_total} балла: слабые стороны заметно ограничивают реализацию возможностей и требуют последовательной проработки. Наименьшая сумма — {wt_total} баллов в W–T — означает, что критические сочетания уязвимостей и угроз управляемы при условии заблаговременного принятия мер.")
    add_p(doc, f"Соотношение S–O к W–T составляет примерно {so_total/wt_total:.1f}".replace(".", ",") + ". Следовательно, потенциал наступательного развития превышает совокупную значимость наиболее опасных сочетаний слабых сторон и угроз. Наиболее значимыми внутренними преимуществами по итогам суммирования являются единый цикл домашнего питания и комплексный функционал. Среди внешних факторов высокие итоговые оценки получили развитие ИИ, рост цен на продукты, осознанное потребление и API-интеграции. Наиболее чувствительными слабыми сторонами являются зависимость от внешних сервисов и затраты при неопределённой готовности аудитории платить.")

    add_heading(doc, "3 SWOT-матрица предлагаемых решений", page_break=True)
    add_p(doc, "На основе перекрёстного анализа сформулированы 20 стратегических мероприятий. Решения S–O направлены на усиление конкурентных преимуществ и использование возможностей, S–T — на защиту от угроз, W–O — на преодоление слабых сторон через внешние возможности, W–T — на снижение наиболее опасных уязвимостей. Перечень мероприятий представлен в таблице 4.")
    add_caption(doc, "Таблица 4 – SWOT-матрица предлагаемых решений")
    add_solutions_table(doc)

    add_heading(doc, "4 Сводная таблица с количественной оценкой влияния предлагаемых решений", page_break=True)
    add_p(doc, "Для определения очерёдности реализации каждое мероприятие оценено по шкале от 1 до 15 баллов. Оценка учитывает значимость связанных факторов, ожидаемое влияние на ценностное предложение и устойчивость бизнес-модели, а также срочность меры. Чем выше балл, тем раньше решение целесообразно включить в дорожную карту проекта. Результаты оценки приведены в таблице 5.")
    add_caption(doc, "Таблица 5 – Сводная таблица с количественной оценкой влияния предлагаемых решений")
    add_scores_table(doc)
    add_p(doc, "Высший приоритет получили маркетинг экономии и защита персональных данных: первая мера напрямую использует самую значимую рыночную возможность, вторая формирует обязательную основу доверия и законной работы сервиса. В группу высокого приоритета вошли развитие распознавания, интеграция списка покупок с доставкой, наполнение базы рецептов и технические меры информационной безопасности. Средний приоритет имеют решения по удержанию, гибкой монетизации и снижению зависимости от внешних платформ. Ранжирование представлено в таблице 6.")
    add_caption(doc, "Таблица 6 – Ранжирование предлагаемых решений")
    add_ranking_table(doc)
    add_p(doc, "Итоговая стратегия предполагает четыре этапа. На первом этапе (0–3 месяца) необходимо сформировать минимально жизнеспособный продукт с базовым учётом продуктов, подбором рецептов и списком покупок, обеспечить конфиденциальность и запустить коммуникацию вокруг экономии. На втором этапе (3–6 месяцев) следует расширять проверенную базу рецептов, улучшать распознавание по фото и внедрять статистику сокращения отходов. На третьем этапе (6–12 месяцев) планируются интеграции с доставкой, гибкие тарифы, персональные меню и партнёрская монетизация. На четвёртом этапе (после 12 месяцев) основное внимание уделяется масштабированию сообщества, развитию партнёрской сети и снижению зависимости от отдельных провайдеров.")

    add_heading(doc, "5 Вывод", page_break=True)
    add_p(doc, "В результате проведённого SWOT-анализа проекта FridgeChef были систематизированы внутренние и внешние факторы, определены их количественные взаимосвязи, сформулированы стратегические решения и установлена очерёдность их реализации. Анализ опирался на результаты предыдущих этапов: ценностное предложение и профиль пользователя, бизнес-модель Остервальдера и Пенье, сравнение с Supercook, Cookpad и «Едим Дома», а также PEST-анализ внешней среды.")
    add_p(doc, "Ключевым преимуществом проекта является комплексное решение задачи домашнего питания: от учёта имеющихся продуктов и выбора блюда до планирования меню, покупок и контроля сроков годности. Это отличает FridgeChef как от сервисов подбора по ингредиентам, так и от традиционных кулинарных порталов. Дополнительную ценность создают распознавание по фото, персонализация, расчёт стоимости и калорийности, а также понятный для массовой аудитории результат — экономия времени, денег и сокращение пищевых отходов.")
    add_p(doc, f"Количественный анализ подтвердил преобладание наступательного потенциала: матрица S–O набрала {so_total} баллов, S–T — {st_total}, W–O — {wo_total}, W–T — {wt_total}. Наиболее перспективными внешними направлениями являются использование интереса к экономии и осознанному потреблению, развитие ИИ-функций и интеграции с доставкой. Основными зонами риска остаются небольшая стартовая база контента, необходимость регулярного обновления данных пользователем, защита персональных данных, конкуренция и зависимость от внешних платформ.")
    add_p(doc, "Для превращения преимуществ в устойчивый бизнес предложено 20 мероприятий. Высший приоритет получили продвижение через измеримую экономию и комплексная защита данных. Далее следуют развитие ИИ-распознавания, наполнение базы рецептов при участии специалистов, интеграция автосписка с доставкой и усиление информационной безопасности. Предусмотрены также меры по удержанию аудитории, гибкой монетизации и технологической независимости.")
    add_p(doc, "Итоговую стратегию можно сформулировать как «Экономичное и безопасное домашнее питание на основе ИИ». Она относится к оптимистическому типу, поскольку направлена на активное использование рыночных возможностей и формирование отдельной ниши комплексного управления домашним питанием. Одновременно стратегия содержит элементы реалистического подхода: поэтапные инвестиции, развитие бесплатной версии, защита данных и снижение зависимости от внешних сервисов.")
    add_p(doc, "Таким образом, FridgeChef обладает благоприятным SWOT-профилем и потенциалом коммерциализации. Успех проекта зависит не только от широты заявленного функционала, но и от качества базовых сценариев, точности распознавания, регулярного пополнения рецептов и способности сформировать устойчивую пользовательскую привычку. Последовательная реализация предложенной дорожной карты позволит использовать сильные стороны проекта, снизить влияние уязвимостей и создать основу для долгосрочного масштабирования.")

print("Содержимое отчёта сформировано в рабочей копии")
print(f"S–O={so_total}; S–T={st_total}; W–O={wo_total}; W–T={wt_total}")
print("S:", s_totals)
print("W:", w_totals)
print("O:", o_totals)
print("T:", t_totals)
