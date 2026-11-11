from pathlib import Path
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Pt, Cm, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика")
UNPACKED = ROOT / "work_pz6" / "output" / "unpacked"
VERIFY_DIR = Path(r"C:\Users\ppljc\AppData\Roaming\kimi-desktop\daimon-share\daimon\runtime\kimi-code\home\plugins\managed\kimi-word\skills\kimi-word\scripts\verify")
sys.path.insert(0, str(VERIFY_DIR))
from opc import edit_docx

FONT = "Times New Roman"
BODY_SIZE = Pt(14)
TABLE_SIZE = Pt(11)


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
    set_paragraph_format(p, align=align, first=first, before=before, after=after,
                         keep_next=keep_next)
    if text:
        set_run(p.add_run(text), size=size, bold=bold, italic=italic)
    return p


def add_heading(doc, text, page_break=False):
    if page_break:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Cm(0)
        p.add_run().add_break(WD_BREAK.PAGE)
    return add_p(doc, text, bold=True, first=False, keep_next=True)


def add_task(doc, number, text):
    p = add_p(doc, f"{number}. {text}", first=False)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.75)
    return p


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
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
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


def set_cell(cell, text, *, size=TABLE_SIZE, bold=False,
             align=WD_ALIGN_PARAGRAPH.LEFT, fill=None):
    cell.text = ""
    p = cell.paragraphs[0]
    set_paragraph_format(p, align=align, first=False, line=1.0)
    set_run(p.add_run(str(text)), size=size, bold=bold)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)
    if fill:
        set_cell_shading(cell, fill)


def set_table_width(table, widths_pt):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(round(sum(widths_pt) * 20))))
    tbl_w.set(qn("w:type"), "dxa")
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            if idx < len(widths_pt):
                cell.width = Pt(widths_pt[idx])
                tc_w = cell._tc.get_or_add_tcPr().find(qn("w:tcW"))
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


def add_indicator_table(doc, headers, rows, widths):
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.style = "Table Grid"
    for c, header in enumerate(headers):
        set_cell(table.cell(0, c), header, bold=True,
                 align=WD_ALIGN_PARAGRAPH.CENTER, fill="D9D9D9")
    set_repeat_table_header(table.rows[0])
    prevent_row_split(table.rows[0])
    for r, values in enumerate(rows, 1):
        prevent_row_split(table.rows[r])
        for c, value in enumerate(values):
            align = WD_ALIGN_PARAGRAPH.CENTER if c == 0 else WD_ALIGN_PARAGRAPH.LEFT
            set_cell(table.cell(r, c), value, align=align)
    set_table_width(table, widths)
    return table


subgoals = [
    (
        "Подцель 1. Продукт: к 30.06.2027 опубликовать MVP мобильного приложения FridgeChef с базовым циклом «продукты дома — рецепт — список покупок — контроль сроков годности».",
        [
            "Разработать UX/UI-прототип, архитектуру приложения и сценарии онбординга. Срок — 28.02.2027. Исполнители — системный аналитик и UI/UX-дизайнер.",
            "Реализовать учёт продуктов с ручным вводом и распознаванием по фото, а также подбор рецептов по имеющимся ингредиентам. Срок — 30.04.2027. Исполнители — mobile-, backend- и ML-разработчики.",
            "Добавить пошаговые рецепты с таймером, напоминания о сроках годности, планирование меню и автоматический список покупок. Срок — 31.05.2027. Исполнители — mobile- и backend-разработчики.",
            "Провести функциональное, нагрузочное и UX-тестирование, устранить критические ошибки и опубликовать MVP в RuStore и на официальном сайте. Срок — 30.06.2027. Исполнители — QA-инженер, Product Owner и DevOps-инженер.",
        ],
    ),
    (
        "Подцель 2. Контент: к 30.09.2027 сформировать базу не менее чем из 1 000 проверенных пошаговых рецептов.",
        [
            "Подготовить и проверить первые 500 пошаговых рецептов, включая бюджетные и быстрые блюда, с указанием калорийности и стоимости. Срок — 30.06.2027. Исполнители — контент-менеджер, нутрициолог и шеф-повар.",
            "Расширить базу до 1 000 рецептов и организовать их редакционную проверку перед публикацией. Срок — 30.09.2027. Исполнители — контент-менеджер, нутрициолог и шеф-повар.",
        ],
    ),
    (
        "Подцель 3. Аудитория: к 31.12.2027 достичь 5 000 активных пользователей приложения в месяц.",
        [
            "Запустить продвижение в социальных сетях через короткие видео, рецепты и коммуникацию «Готовь из того, что есть — экономь каждый день». Срок — 31.08.2027. Исполнитель — маркетолог.",
            "Организовать публикации с фуд-блогерами и нутрициологами для привлечения целевой аудитории. Срок — 30.09.2027. Исполнители — менеджер по партнёрствам и маркетолог.",
            "Запустить реферальную программу, персональные подборки и челлендж «Неделя без выброшенной еды» для роста активной аудитории. Срок — 31.12.2027. Исполнители — маркетолог, Product Owner и mobile-разработчик.",
        ],
    ),
    (
        "Подцель 4. Монетизация: к 30.11.2027 достичь 250 активных Premium-подписок.",
        [
            "Настроить приём оплаты и тариф Premium стоимостью 299 рублей в месяц с расширенной аналитикой, планированием меню и персональными рекомендациями. Срок — 31.08.2027. Исполнители — backend-разработчик и финансовый аналитик.",
            "Внедрить пробный период, годовой и семейный тарифы для повышения привлекательности платной подписки. Срок — 30.09.2027. Исполнители — Product Owner и маркетолог.",
        ],
    ),
    (
        "Подцель 5. Партнёрские интеграции: к 30.11.2027 подключить два сервиса доставки продуктов к автоматическому списку покупок.",
        [
            "Интегрировать автосписок покупок с двумя сервисами доставки и предусмотреть единый модуль подключения новых партнёров. Срок — 30.11.2027. Исполнители — backend-разработчик и менеджер по партнёрствам.",
        ],
    ),
    (
        "Подцель 6. Защита данных: к 30.06.2027 внедрить систему защиты персональных данных пользователей приложения.",
        [
            "Внедрить минимизацию собираемых данных, явное согласие, шифрование, разграничение доступа, резервное копирование и автоматическое удаление фотографий после распознавания. Срок — 30.06.2027. Исполнители — backend-разработчик, DevOps-инженер и специалист по информационной безопасности.",
        ],
    ),
    (
        "Подцель 7. Поддержка пользователей: к 30.09.2027 обеспечить решение не менее 90% обращений без повторного контакта.",
        [
            "Настроить чат поддержки и сформировать базу знаний по основным сценариям приложения. Срок — 31.08.2027. Исполнители — специалист поддержки и контент-менеджер.",
            "Ввести анализ причин обращений и повторных контактов, регулярно дополнять базу знаний и корректировать сценарии поддержки. Срок — 30.09.2027. Исполнители — специалист поддержки и Product Owner.",
        ],
    ),
]

qualitative_rows = [
    ("1", "Полезность и персонализация рекомендаций\nСредняя оценка рекомендаций — не менее 4,5 из 5",
     "Пользователь получает блюда, соответствующие имеющимся продуктам, вкусовым предпочтениям и ограничениям рациона",
     "Опрос после использования рекомендации, оценки рецептов, доля сохранённых и отмеченных как приготовленные блюд"),
    ("2", "Удобство ключевых сценариев\nНе менее 85% участников выполняют сценарий без помощи; SUS — не менее 80 баллов",
     "Добавление продуктов, подбор рецепта и формирование списка покупок интуитивно понятны и не вызывают критических ошибок",
     "Модерируемое UX-тестирование, шкала SUS, анализ времени и ошибок при выполнении сценариев"),
    ("3", "Качество контента и поддержки\nСредняя оценка рецептов и поддержки — не менее 4,5 из 5",
     "Рецепты проверены и понятны, а обращения решаются без повторного контакта и потери доверия к сервису",
     "Рейтинги и отзывы, редакционная проверка рецептов, опрос после обращения, доля повторных обращений"),
]

quantitative_rows = [
    ("1", "Месячная активная аудитория (MAU)\nНе менее 5 000 пользователей к 31.12.2027",
     "Достаточный масштаб активной аудитории для устойчивой монетизации и развития партнёрств",
     "Количество уникальных пользователей, выполнивших хотя бы одно целевое действие за календарный месяц"),
    ("2", "Количество активных Premium-подписок\nНе менее 250 к 30.11.2027",
     "Платные возможности востребованы и обеспечивают достижение целевой выручки",
     "Количество пользователей с действующей оплаченной подпиской на отчётную дату"),
    ("3", "Конверсия в Premium\nНе менее 5%",
     "Не менее 5% месячной активной аудитории переходят на платный тариф",
     "Количество активных Premium-подписчиков / MAU × 100%"),
    ("4", "Ежемесячная регулярная выручка (MRR)\nНе менее 74 750 рублей",
     "250 подписок по 299 рублей формируют целевой уровень регулярной выручки",
     "Количество активных Premium-подписок × средняя ежемесячная цена подписки"),
    ("5", "Удержание на 30-й день (Retention 30)\nНе менее 30%",
     "Приложение становится частью регулярного сценария планирования питания, а не разовой загрузкой",
     "Количество пользователей когорты, активных на 30-й день / размер когорты новых пользователей × 100%"),
    ("6", "Стоимость привлечения пользователя (CAC)\nНе более 250 рублей",
     "Затраты на привлечение соответствуют возможностям монетизации и масштабирования проекта",
     "Расходы на привлечение за период / количество новых зарегистрированных пользователей за период"),
]

with edit_docx(str(UNPACKED)) as doc:
    # Обновляем номер работы на сохранённой титульной странице.
    for p in doc.paragraphs:
        if "Отчет по практическому занятию" in p.text:
            for run in p.runs:
                if "№5" in run.text:
                    run.text = run.text.replace("№5", "№6")
            break

    # Сохраняем титульный лист, колонтитулы и параметры раздела; заменяем только основную часть.
    body = doc._element.body
    sect_pr = body.sectPr
    start = None
    for child in list(body):
        if child.tag == qn("w:p"):
            text = "".join(node.text or "" for node in child.iter(qn("w:t")))
            if text.startswith("1 Главная цель проекта по SMART"):
                start = child
                break
    if start is None:
        raise RuntimeError("Не найдено начало основной части отчёта ПЗ6")
    removing = False
    for child in list(body):
        if child is start:
            removing = True
        if removing and child is not sect_pr:
            body.remove(child)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = BODY_SIZE
    normal._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)

    doc.core_properties.title = "Отчёт по практическому занятию №6 — FridgeChef"
    doc.core_properties.subject = "SMART-цель, дерево подцелей и показатели эффективности проекта"

    add_heading(doc, "1 Главная цель проекта по SMART")
    add_p(doc, "К 31.12.2027 достичь ежемесячной регулярной выручки FridgeChef не менее 74 750 рублей за счёт Premium-подписки.")
    add_p(doc, "Главная цель содержит один результат — достижение целевой ежемесячной регулярной выручки. Она является конкретной, поскольку определяет источник дохода — Premium-подписку; измеримой, поскольку результат проверяется показателем MRR; достижимой за счёт поэтапного развития продукта, аудитории и платных функций; значимой для коммерческой устойчивости проекта. Срок достижения ограничен 31.12.2027. Запуск приложения, рост аудитории и количество подписок вынесены в отдельные подцели и не дублируются как дополнительные результаты главной цели.")

    add_heading(doc, "2 Дерево подцелей и задач проекта")
    add_p(doc, "Дерево подцелей построено с учётом бизнес-модели Freemium, результатов конкурентного анализа, PEST- и SWOT-анализа. Каждая подцель сформулирована как один измеримый результат, а связанные действия вынесены в задачи. Таким образом, соблюдается принцип «одна подцель — один результат».")
    for title, tasks in subgoals:
        add_p(doc, title, bold=True, first=False, keep_next=True)
        add_p(doc, "Задачи:", bold=True, first=False, keep_next=True)
        for idx, task in enumerate(tasks, 1):
            add_task(doc, idx, task)

    add_heading(doc, "3 Показатели эффективности проекта", page_break=True)
    add_p(doc, "Для измерения эффективности FridgeChef предложены качественные и количественные показатели. Первые оценивают пользовательский опыт, полезность рекомендаций, удобство и доверие; вторые позволяют проверить масштаб аудитории, удержание, монетизацию и экономичность привлечения.")
    add_p(doc, "Качественные показатели:", bold=True, first=False, keep_next=True)
    add_caption(doc, "Таблица 1 – Качественные показатели эффективности проекта FridgeChef")
    add_indicator_table(
        doc,
        ("№", "Показатель", "Критерий оценки", "Способ измерения"),
        qualitative_rows,
        [25, 145, 150, 147.75],
    )
    add_p(doc, "Качественные показатели направлены на проверку ключевого ценностного предложения. Персонализация подтверждает, что приложение действительно подбирает подходящие блюда, а не просто предоставляет каталог рецептов. Удобство сценариев снижает трудоёмкость учёта продуктов — один из главных рисков удержания. Качество контента и поддержки формирует доверие к рекомендациям и сервису, необходимое для повторного использования и перехода на платный тариф.")

    add_p(doc, "Количественные показатели:", bold=True, first=False, keep_next=True)
    add_caption(doc, "Таблица 2 – Количественные показатели эффективности проекта FridgeChef")
    add_indicator_table(
        doc,
        ("№", "Показатель", "Критерий оценки", "Формула расчёта / способ измерения"),
        quantitative_rows,
        [25, 135, 135, 172.75],
    )
    add_p(doc, "Количественные показатели образуют взаимосвязанную систему. Аудитория в 5 000 активных пользователей и конверсия 5% соответствуют 250 Premium-подписчикам. При цене 299 рублей в месяц это даёт MRR 74 750 рублей. Retention 30 не менее 30% подтверждает формирование пользовательской привычки, а CAC не более 250 рублей ограничивает стоимость масштабирования. Совместный контроль этих метрик предотвращает ситуацию, при которой рост аудитории достигается без удержания или экономически оправданной монетизации.")

    add_heading(doc, "Вывод", page_break=True)
    add_p(doc, "В отчёте сформулирована SMART-цель проекта FridgeChef, направленная на один результат — достижение целевой ежемесячной регулярной выручки. Дерево включает семь подцелей: публикацию MVP, создание базы рецептов, достижение целевой активной аудитории, получение 250 Premium-подписок, подключение двух сервисов доставки, внедрение системы защиты данных и обеспечение целевого качества поддержки. Каждая подцель содержит только один измеримый результат и декомпозирована на задачи со сроками и ответственными исполнителями.")
    add_p(doc, "Содержание целей опирается на результаты предыдущих практических работ. Единый цикл «продукты дома — рецепт — меню — список покупок — сроки годности» закрепляет конкурентное преимущество приложения. Развитие бесплатной версии и Premium-подписки соответствует бизнес-модели Freemium. Интеграции с доставкой, работа с нутрициологами и фуд-блогерами используют выявленные рыночные возможности, а меры защиты данных и технологической независимости учитывают основные PEST- и SWOT-риски.")
    add_p(doc, "Предложенные качественные показатели позволяют оценить полезность рекомендаций, удобство ключевых сценариев, качество рецептов и поддержки. Количественные показатели связывают аудиторию, конверсию, выручку, удержание и стоимость привлечения. Целевые значения согласованы между собой: 5 000 активных пользователей при конверсии 5% обеспечивают 250 подписок и 74 750 рублей ежемесячной регулярной выручки.")
    add_p(doc, "Ключевыми условиями достижения цели являются параллельное развитие MVP и контента, точность распознавания продуктов, простота ручной коррекции, регулярное пополнение базы рецептов и формирование привычки использования. Первоочередное внимание следует уделить базовому пользовательскому сценарию и защите данных, а расширение рекламной и партнёрской монетизации проводить по мере роста активной аудитории. Такой порядок реализации позволяет превратить преимущества FridgeChef в устойчивый и масштабируемый цифровой бизнес.")

print("Содержимое отчёта ПЗ6 сформировано в рабочей копии")
print(f"Подцелей: {len(subgoals)}; задач: {sum(len(tasks) for _, tasks in subgoals)}")
print(f"Качественных показателей: {len(qualitative_rows)}; количественных: {len(quantitative_rows)}")
