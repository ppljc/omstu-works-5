from pathlib import Path
import yaml

ROOT = Path(r"C:\Users\ppljc\omstu-works-5\Бизнес информатика\Итоговые материалы FridgeChef\Презентация FridgeChef")
PAGES = ROOT / "pages"
PAGES.mkdir(parents=True, exist_ok=True)

C = {
    "navy": "#1F4E79", "blue": "#4472C4", "mid": "#8EAADB",
    "pale": "#DCE6F5", "bg": "#F7F9FC", "text": "#263445",
    "muted": "#5B677A", "green": "#70AD47", "greenPale": "#E9F3E4",
    "white": "#FFFFFF", "line": "#B7C7DC", "light": "#EDF2F8",
    "orange": "#C55A11", "gray": "#8A94A6"
}

class Dumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

def fill(color):
    return {"type": "solid", "color": color}

def text(eid, bounds, value, size=18, color="$text", bold=False,
         align=("left", "top"), line_height=1.15, wrap=True, style=None):
    content = {"text": value, "fontSize": size, "color": color,
               "fontFamily": "Arial", "bold": bold, "align": list(align),
               "lineHeight": line_height, "wrap": wrap}
    if style:
        content["style"] = style
    return {"elementId": eid, "elementType": "text", "bounds": bounds, "content": content}

def shape(eid, bounds, name="rect", color="$pale", border=None, opacity=None, rotation=None):
    item = {"elementId": eid, "elementType": "shape", "bounds": bounds,
            "shapeName": name, "fill": fill(color)}
    if border:
        item["border"] = border
    if opacity is not None:
        item["opacity"] = opacity
    if rotation is not None:
        item["rotation"] = rotation
    return item

def line(eid, bounds, color="$line", width=1, arrow=None):
    item = {"elementId": eid, "elementType": "line", "bounds": bounds,
            "viewBox": [1, 1], "points": "0,0 1,1", "curve": "sharp",
            "border": {"style": "solid", "width": width, "color": color}}
    if arrow:
        item["arrow"] = arrow
    return item

def hline(eid, x, y, w, color="$line", width=1):
    return {"elementId": eid, "elementType": "line", "bounds": [x, y, w, 1],
            "viewBox": [w, 1], "points": f"0,0 {w},0", "curve": "sharp",
            "border": {"style": "solid", "width": width, "color": color}}

def vline(eid, x, y, h, color="$line", width=1):
    return {"elementId": eid, "elementType": "line", "bounds": [x, y, 1, h],
            "viewBox": [1, h], "points": f"0,0 0,{h}", "curve": "sharp",
            "border": {"style": "solid", "width": width, "color": color}}

def icon(eid, bounds, name, color="$blue"):
    return {"elementId": eid, "elementType": "icon", "bounds": bounds,
            "iconName": name, "fill": fill(color)}

def bullets(items, margin=4):
    return "".join(f'<p style="margin-top:{margin}px">• {item}</p>' for item in items)

def base(num, title_value=None, subtitle=None):
    e = [shape(f"decor_top_{num}", [835, -65, 210, 145], "ellipse", "$pale"),
         shape(f"decor_bottom_{num}", [-105, 455, 275, 150], "ellipse", "$pale"),
         shape(f"accent_{num}", [48, 27, 34, 5], "rect", "$green")]
    if title_value:
        e.append(text(f"title_{num}", [48, 38, 820, 45], title_value, 28, "$navy", True, wrap=False))
    if subtitle:
        e.append(text(f"subtitle_{num}", [49, 78, 820, 24], subtitle, 12, "$muted", wrap=False))
    e.append(text(f"page_{num}", [891, 505, 35, 18], f"{num:02d}", 10, "$muted", align=("right", "middle"), wrap=False))
    return {"pageType": "content", "background": fill("$bg"), "elements": e}

def save_page(filename, page):
    path = PAGES / filename
    path.write_text(yaml.dump(page, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")

# 1 — Cover
p = base(1)
e = p["elements"]
e += [
    text("cover_kicker", [55, 83, 440, 25], "ЦИФРОВОЙ ПРОЕКТ • ОмГТУ", 12, "$green", True, wrap=False),
    text("cover_title", [52, 119, 535, 75], "FridgeChef", 52, "$navy", True, wrap=False),
    hline("cover_line", 55, 207, 390, "$mid", 2),
    text("cover_subtitle", [55, 227, 500, 75], "Что приготовить из того,\nчто уже есть дома", 24, "$text", False, line_height=1.2),
    text("cover_desc", [55, 315, 475, 68], "Рецепты по имеющимся продуктам, контроль сроков годности, меню на неделю и автоматический список покупок.", 16, "$muted", line_height=1.3),
    text("cover_group", [55, 427, 470, 24], "ИВТ-244", 14, "$navy", True, wrap=False),
    text("cover_team", [55, 454, 520, 52], "А. В. Шмидт  •  С. Д. Ахмедеев  •  А. Д. Фельдт", 13, "$text", wrap=False),
    shape("phone_outer", [645, 72, 225, 420], "roundRect", "$navy"),
    shape("phone_inner", [655, 83, 205, 398], "roundRect", "$white"),
    text("phone_brand", [674, 101, 165, 28], "FridgeChef", 17, "$navy", True, align=("center", "middle"), wrap=False),
    text("phone_fridge", [675, 140, 160, 22], "Ваш холодильник", 12, "$muted", align=("center", "middle"), wrap=False),
    icon("phone_carrot", [678, 176, 20, 20], "fas:carrot", "$green"),
    text("phone_item1", [707, 173, 125, 25], "Овощи — 4 шт.", 12, "$text", wrap=False),
    icon("phone_cheese", [678, 209, 20, 20], "fas:cheese", "$green"),
    text("phone_item2", [707, 206, 125, 25], "Сыр — 200 г", 12, "$text", wrap=False),
    icon("phone_egg", [678, 242, 20, 20], "fas:egg", "$green"),
    text("phone_item3", [707, 239, 125, 25], "Яйца — 6 шт.", 12, "$text", wrap=False),
    shape("phone_button", [676, 280, 162, 35], "roundRect", "$green"),
    text("phone_button_text", [681, 283, 152, 28], "Подобрать рецепт", 12, "$white", True, align=("center", "middle"), wrap=False),
    hline("phone_sep", 678, 337, 158, "$pale", 1),
    icon("phone_food", [680, 354, 31, 31], "fas:bowl-food", "$blue"),
    text("phone_recipe", [720, 349, 116, 30], "Паста с овощами", 13, "$navy", True),
    text("phone_meta", [720, 382, 115, 38], "20 минут\n4 порции", 11, "$muted"),
    text("phone_badge", [678, 435, 158, 22], "Подходит по запасам", 10, "$green", True, align=("center", "middle"), wrap=False)
]
save_page("01_cover.page", p)

# 2 — Customer profile
p = base(2, "Пользователь и его задачи", "Профиль сформирован в ПЗ1: занятые пользователи, семьи, студенты и начинающие кулинары")
e = p["elements"]
e += [
    text("problem_label", [52, 123, 290, 22], "ЕЖЕДНЕВНЫЙ ВОПРОС", 11, "$green", True, wrap=False),
    text("problem_big", [50, 153, 325, 118], "Что\nприготовить?", 36, "$navy", True, line_height=1.08),
    text("problem_body", [52, 284, 300, 98], "Решение должно быть быстрым, понятным и учитывать реальные продукты дома — без длительного поиска по каталогам.", 17, "$text", line_height=1.3),
    icon("problem_icon", [56, 409, 42, 42], "fas:clock", "$blue"),
    text("problem_outcome", [112, 404, 255, 60], "Ключевой мотив:\nэкономия времени и денег", 16, "$navy", True),
    vline("profile_divider", 391, 126, 330, "$line", 1),
    icon("jobs_icon", [424, 127, 27, 27], "fas:list-check", "$blue"),
    text("jobs_title", [465, 124, 170, 28], "Задачи", 21, "$navy", True, wrap=False),
    text("jobs_list", [465, 157, 425, 82], bullets(["Решить, что приготовить", "Проверить запасы дома", "Составить меню и список покупок", "Быстро приготовить блюдо"]), 14, "$text", line_height=1.15),
    hline("profile_line1", 424, 245, 460, "$line", 1),
    icon("pains_icon", [424, 263, 27, 27], "fas:triangle-exclamation", "$blue"),
    text("pains_title", [465, 258, 170, 28], "Проблемы", 21, "$navy", True, wrap=False),
    text("pains_list", [465, 292, 425, 68], bullets(["Нет времени и кулинарного опыта", "Продукты забываются и портятся", "Нет системы планирования", "Лишние и дублирующие покупки"]), 14, "$text", line_height=1.1),
    hline("profile_line2", 424, 370, 460, "$line", 1),
    icon("gains_icon", [424, 389, 27, 27], "fas:arrow-trend-up", "$green"),
    text("gains_title", [465, 384, 170, 28], "Выгоды", 21, "$navy", True, wrap=False),
    text("gains_list", [465, 419, 430, 60], "Мгновенные рецепты  •  напоминания о сроках\nготовые меню  •  автосписок  •  пошаговая готовка", 14, "$text", line_height=1.3)
]
save_page("02_customer.page", p)

# 3 — Value proposition
p = base(3, "Ценностное предложение", "Один сценарий связывает продукты, приготовление и планирование")
e = p["elements"]
e += [
    icon("value_quote_icon", [53, 119, 34, 34], "fas:quote-left", "$green"),
    text("value_quote", [53, 161, 385, 174], "Быстро понять, что приготовить из продуктов, которые уже есть дома — и при этом экономить время, деньги и еду.", 27, "$navy", True, line_height=1.22),
    text("value_explain", [55, 354, 365, 85], "Приложение подходит и занятому пользователю, и начинающему кулинару: рекомендации учитывают запасы, время, сложность и ограничения рациона.", 15, "$muted", line_height=1.3),
    vline("value_divider", 472, 127, 330, "$line", 1),
    text("flow_title", [510, 119, 320, 28], "Как работает FridgeChef", 20, "$navy", True, wrap=False)
]
flow = [
    ("01", "Добавить продукты", "Фото или ручной ввод", "fas:camera"),
    ("02", "Получить рецепты", "По ингредиентам и предпочтениям", "fas:bowl-food"),
    ("03", "Приготовить", "Пошагово и с таймером", "fas:utensils"),
    ("04", "Спланировать", "Меню на неделю", "fas:calendar-days"),
    ("05", "Купить недостающее", "Автоматический список", "fas:cart-shopping")
]
for i, (num, ttl, desc, ico) in enumerate(flow):
    y = 158 + i * 62
    e += [text(f"flow_num_{i}", [510, y, 42, 30], num, 20, "$green", True, wrap=False),
          icon(f"flow_icon_{i}", [563, y+1, 23, 23], ico, "$blue"),
          text(f"flow_ttl_{i}", [601, y-2, 275, 25], ttl, 16, "$navy", True, wrap=False),
          text(f"flow_desc_{i}", [601, y+23, 285, 23], desc, 12, "$muted", wrap=False)]
    if i < 4:
        e.append(hline(f"flow_line_{i}", 563, y+51, 315, "$light", 1))
e += [shape("value_bottom", [0, 500, 960, 40], "rect", "$pale"),
      text("value_bottom_text", [53, 505, 840, 25], "Результат: меньше рутины, лишних покупок и выброшенных продуктов", 15, "$navy", True, align=("center", "middle"), wrap=False)]
save_page("03_value.page", p)

# 4 — Business model canvas
p = base(4, "Бизнес-модель Freemium", "B2C-подписка дополняется партнёрскими комиссиями и маркированными интеграциями")
e = p["elements"]
def cell(heading, items, color="$text", fill_color=None, rowSpan=None, colSpan=None):
    c = {"text": f"<p><strong>{heading}</strong></p>" + bullets(items, 2),
         "fontSize": 10.5, "fontFamily": "Arial", "color": color,
         "lineHeight": 1.05, "align": ["left", "top"]}
    if fill_color:
        c["fill"] = fill(fill_color)
    if rowSpan:
        c["rowSpan"] = rowSpan
    if colSpan:
        c["colSpan"] = colSpan
    return c
rows = [
    [cell("Ключевые партнёры", ["Магазины приложений и платежи", "Нутрициологи и шеф-повары", "Облачные и ML-сервисы"], rowSpan=2),
     cell("Деятельность", ["Разработка и поддержка", "База рецептов и модерация", "Маркетинг и партнёрства"]),
     cell("Ценностное предложение", ["Рецепты по имеющимся продуктам", "Сроки годности и запасы", "Меню и автосписок покупок", "Экономия времени и денег"], fill_color="$greenPale", rowSpan=2),
     cell("Отношения с клиентами", ["Self-service и автоматизация", "Персональные рекомендации", "Отзывы и сообщество"]),
     cell("Сегменты", ["Занятые горожане", "Семьи и студенты", "Сторонники ЗОЖ", "B2B: доставка и бренды"], rowSpan=2)],
    [cell("Ресурсы", ["Приложение и алгоритмы", "База рецептов и продуктов", "Команда и контент"]),
     cell("Каналы", ["Соцсети и фуд-блогеры", "RuStore и сайт", "Push и реферальная программа"])],
    [cell("Структура издержек", ["Разработка и ML-вычисления", "Контент, маркетинг и поддержка", "Комиссии платформ"], colSpan=2),
     cell("Потоки доходов", ["Premium — 299 ₽/мес.", "Тематические подборки", "Комиссии партнёров и реклама"], fill_color="$pale", colSpan=3)]
]
e.append({"elementId": "business_canvas", "elementType": "table", "bounds": [34, 102, 892, 385],
          "columnWidths": [0.19, 0.18, 0.24, 0.18, 0.21], "rowHeights": [0.43, 0.32, 0.25], "rows": rows,
          "style": {"cellStyle": {"border": {"style": "solid", "width": 0.8, "color": "$line"}, "fill": fill("$white")}}})
e.append(text("business_note", [54, 496, 840, 23], "Последовательность: бесплатная аудитория → Premium → B2B-монетизация после накопления активной базы", 12, "$navy", True, align=("center", "middle"), wrap=False))
save_page("04_business_model.page", p)

# 5 — Competitors
p = base(5, "Конкурентная позиция", "Экспертная оценка по шести критериям из ПЗ3, шкала 0–10")
e = p["elements"]
chart = {"elementId": "competitor_radar", "elementType": "chart", "bounds": [28, 104, 580, 375],
         "data": {"cols": ["Критерий", "Supercook", "Cookpad", "Едим Дома", "FridgeChef"],
                  "rows": [["Цена", 8, 7, 8, 7], ["Скорость", 9, 5, 5, 9], ["Учёт и сроки", 5, 1, 1, 9],
                           ["Планирование", 2, 3, 5, 8], ["Рецепты", 7, 9, 9, 6], ["Удобство", 6, 8, 8, 8]]},
         "series": [
             {"type": "radar", "encode": {"category": "Критерий", "y": "Supercook"}, "name": "Supercook", "lineColor": "#8A94A6", "width": 1.5, "areaColor": "#00000000"},
             {"type": "radar", "encode": {"category": "Критерий", "y": "Cookpad"}, "name": "Cookpad", "lineColor": "#8EAADB", "width": 1.5, "areaColor": "#00000000"},
             {"type": "radar", "encode": {"category": "Критерий", "y": "Едим Дома"}, "name": "Едим Дома", "lineColor": "#C55A11", "width": 1.5, "areaColor": "#00000000"},
             {"type": "radar", "encode": {"category": "Критерий", "y": "FridgeChef"}, "name": "FridgeChef", "lineColor": "#70AD47", "width": 3, "areaColor": "#70AD4733"}],
         "spokeAxis": {"min": 0, "max": 10, "label": {"fontSize": 10, "color": "$muted"}},
         "legend": {"show": True, "position": "bottom", "fontSize": 11, "color": "$text"},
         "fontFamily": "Arial"}
e.append(chart)
e += [vline("comp_divider", 620, 124, 328, "$line", 1),
      text("score_label", [650, 117, 240, 23], "ИТОГО ПО КРИТЕРИЯМ", 11, "$green", True, wrap=False),
      text("score_big", [647, 142, 155, 64], "47", 52, "$navy", True, wrap=False),
      text("score_max", [738, 168, 80, 30], "/ 60", 20, "$muted", wrap=False)]
scores = [("Supercook", 37, "$gray"), ("Едим Дома", 36, "$orange"), ("Cookpad", 33, "$mid")]
for i, (name, val, col) in enumerate(scores):
    y = 225 + i * 52
    e += [text(f"score_name_{i}", [650, y, 145, 22], name, 13, "$text", wrap=False),
          text(f"score_val_{i}", [835, y, 45, 22], str(val), 14, "$navy", True, align=("right", "top"), wrap=False),
          shape(f"score_bg_{i}", [650, y+26, 230, 5], "rect", "$light"),
          shape(f"score_bar_{i}", [650, y+26, round(230*val/47, 1), 5], "rect", col)]
e += [text("comp_advantage", [650, 394, 240, 56], "Главное отличие — полный цикл домашнего питания", 18, "$navy", True, line_height=1.2),
      text("comp_growth", [52, 487, 810, 26], "Зона роста: наполнение базы рецептов и развитие сообщества", 13, "$muted", wrap=False)]
save_page("05_competitors.page", p)

# 6 — Commercialization
p = base(6, "Коммерциализация и масштабирование", "Доходы подключаются по мере подтверждения пользовательской ценности")
e = p["elements"]
e += [text("commercial_big", [52, 125, 330, 112], "Сначала —\nполезная\nбесплатная версия", 30, "$navy", True, line_height=1.1),
      text("commercial_body", [54, 259, 320, 100], "Она формирует привычку и аудиторию. Расширенные функции и партнёрская монетизация добавляются постепенно, без агрессивной монетизации на старте.", 16, "$text", line_height=1.3),
      icon("commercial_icon", [56, 395, 40, 40], "fas:users", "$green"),
      text("commercial_caption", [110, 392, 270, 56], "Сетевой эффект создают\nконтент, отзывы и рекомендации", 14, "$muted"),
      vline("commercial_divider", 410, 126, 330, "$line", 1)]
stages = [
    ("01", "MVP и бесплатная база", ["Учёт продуктов и рецепты", "Сроки годности и список покупок"]),
    ("02", "Premium и контент", ["299 ₽/мес., меню и аналитика", "Подборки от специалистов"]),
    ("03", "Партнёрская экосистема", ["Доставка и комиссии с заказов", "Маркированные интеграции брендов"])
]
for i, (num, ttl, its) in enumerate(stages):
    y = 124 + i * 113
    e += [text(f"comm_num_{i}", [445, y, 52, 42], num, 30, "$green", True, wrap=False),
          text(f"comm_ttl_{i}", [513, y, 355, 29], ttl, 20, "$navy", True, wrap=False),
          text(f"comm_list_{i}", [513, y+35, 365, 55], bullets(its, 3), 14, "$text", line_height=1.15)]
    if i < 2:
        e.append(hline(f"comm_line_{i}", 445, y+96, 425, "$line", 1))
e += [text("scale_text", [448, 474, 445, 35], "Далее: семейные аккаунты • персональные программы • white-label для ритейла", 12, "$muted", align=("center", "middle"))]
save_page("06_commercialization.page", p)

# 7 — PEST
p = base(7, "Внешняя среда: PEST", "Наиболее значимые факторы по взвешенной экспертной оценке из ПЗ4")
e = p["elements"]
factors = [
    ("Рост цен на продукты", 0.531, "$green"),
    ("Защита персональных данных", 0.508, "$blue"),
    ("ИИ и компьютерное зрение", 0.508, "$blue"),
    ("Осознанное потребление", 0.485, "$green"),
    ("Доставка и API-интеграции", 0.292, "$mid"),
    ("Снижение доходов", 0.277, "$mid")
]
for i, (name, val, col) in enumerate(factors):
    y = 123 + i * 56
    width = round(260 * val / 0.55, 1)
    e += [text(f"pest_name_{i}", [50, y, 235, 38], name, 13, "$text", line_height=1.15),
          shape(f"pest_bg_{i}", [291, y+7, 260, 11], "rect", "$light"),
          shape(f"pest_bar_{i}", [291, y+7, width, 11], "rect", col),
          text(f"pest_val_{i}", [558, y, 55, 28], f"{val:.3f}".replace(".", ","), 13, "$navy", True, align=("right", "top"), wrap=False)]
e += [vline("pest_divider", 632, 126, 332, "$line", 1),
      icon("pest_opp_icon", [661, 125, 28, 28], "fas:arrow-trend-up", "$green"),
      text("pest_opp_title", [704, 123, 170, 28], "Возможности", 20, "$navy", True, wrap=False),
      text("pest_opp", [662, 165, 235, 105], bullets(["Экономия и бюджетные меню", "Меньше пищевых отходов", "ИИ-рекомендации", "Интеграции с доставкой"]), 14, "$text", line_height=1.15),
      hline("pest_line", 661, 289, 230, "$line", 1),
      icon("pest_risk_icon", [661, 310, 28, 28], "fas:shield-halved", "$blue"),
      text("pest_risk_title", [704, 307, 170, 28], "Условия", 20, "$navy", True, wrap=False),
      text("pest_risk", [662, 349, 235, 92], bullets(["Локализация данных", "Сильная бесплатная версия", "Ручная коррекция фото", "Переносимая инфраструктура"]), 14, "$text", line_height=1.1),
      text("pest_conclusion", [52, 475, 830, 32], "Стратегический акцент: экономия для пользователя + безопасность данных + развитие ИИ", 15, "$navy", True, align=("center", "middle"), wrap=False)]
save_page("07_pest.page", p)

# 8 — SWOT
p = base(8, "SWOT: стратегия развития", "Перекрёстный анализ показал преобладание наступательного потенциала")
e = p["elements"]
def swot_cell(title, items, fill_color="$white"):
    return {"text": f"<p><strong>{title}</strong></p>" + bullets(items, 3), "fontSize": 12.5,
            "fontFamily": "Arial", "color": "$text", "lineHeight": 1.1,
            "align": ["left", "top"], "fill": fill(fill_color)}
swot_rows = [
    [swot_cell("S — Сильные стороны", ["Единый цикл домашнего питания", "Фото-ввод и персонализация", "Понятная экономия для пользователя"]),
     swot_cell("O — Возможности", ["Рост цен и интерес к экономии", "Осознанное потребление", "ИИ, API доставки и здоровое питание"], "$greenPale")],
    [swot_cell("W — Слабые стороны", ["Небольшая стартовая база рецептов", "Зависимость от точности данных", "Низкая узнаваемость и затраты"]),
     swot_cell("T — Угрозы", ["Требования к данным и киберриски", "Конкуренция и снижение доходов", "Зависимость от внешних платформ"])]
]
e.append({"elementId": "swot_matrix", "elementType": "table", "bounds": [48, 105, 865, 260],
          "columnWidths": [0.5, 0.5], "rowHeights": [0.5, 0.5], "rows": swot_rows,
          "style": {"cellStyle": {"border": {"style": "solid", "width": 1, "color": "$line"}}}})
metrics = [("S–O", "121", "использовать возможности"), ("S–T", "111", "защищать преимущества"),
           ("W–O", "87", "устранять ограничения"), ("W–T", "77", "снижать уязвимости")]
for i, (code, val, caption) in enumerate(metrics):
    x = 54 + i * 218
    e += [text(f"swot_code_{i}", [x, 389, 55, 22], code, 13, "$muted", True, wrap=False),
          text(f"swot_val_{i}", [x+58, 378, 62, 39], val, 28, "$navy" if i else "$green", True, wrap=False),
          text(f"swot_cap_{i}", [x, 422, 190, 25], caption, 11, "$muted", wrap=False)]
    if i < 3:
        e.append(vline(f"swot_sep_{i}", x+199, 385, 55, "$line", 1))
e += [text("swot_strategy", [53, 473, 850, 34], "Стратегия: экономичное и безопасное домашнее питание на основе ИИ", 18, "$navy", True, align=("center", "middle"), wrap=False)]
save_page("08_swot.page", p)

# 9 — Roadmap and KPI
p = base(9, "Дорожная карта и целевые показатели", "Контрольная точка — 31 декабря 2027 года")
e = p["elements"]
e.append(hline("road_axis", 82, 146, 790, "$mid", 2))
road = [
    (82, "01–06.2027", "Продукт и MVP", ["UX/UI и архитектура", "Базовый цикл и защита данных", "Первые 500 рецептов"]),
    (294, "07–09.2027", "Контент и запуск", ["До 1 000 рецептов", "Продвижение и блогеры", "Пробный период и тарифы"]),
    (506, "08–11.2027", "Монетизация", ["250 Premium-подписок", "Две интеграции доставки", "Партнёрские рецепты"]),
    (718, "09–12.2027", "Масштабирование", ["Реферальная программа", "Поддержка и аналитика", "Челленджи и удержание"])
]
for i, (x, date, ttl, its) in enumerate(road):
    e += [shape(f"road_dot_{i}", [x, 137, 18, 18], "ellipse", "$green" if i == 3 else "$blue"),
          text(f"road_date_{i}", [x-2, 104, 185, 25], date, 13, "$navy", True, wrap=False),
          text(f"road_ttl_{i}", [x-2, 172, 185, 28], ttl, 18, "$navy", True, wrap=False),
          text(f"road_list_{i}", [x-2, 207, 180, 105], bullets(its, 5), 12.5, "$text", line_height=1.15)]
e.append(hline("kpi_line", 52, 342, 850, "$line", 1))
kpis = [("5 000", "MAU"), ("250", "Premium"), ("74 750 ₽", "MRR"), ("≥ 30%", "Retention 30"), ("≤ 250 ₽", "CAC")]
for i, (val, label) in enumerate(kpis):
    x = 48 + i * 174
    e += [text(f"kpi_val_{i}", [x, 371, 160, 43], val, 27 if i != 2 else 24, "$navy" if i != 2 else "$green", True, align=("center", "middle"), wrap=False),
          text(f"kpi_label_{i}", [x, 416, 160, 23], label, 12, "$muted", align=("center", "middle"), wrap=False)]
    if i < 4:
        e.append(vline(f"kpi_sep_{i}", x+166, 377, 58, "$line", 1))
e.append(text("kpi_note", [54, 470, 840, 28], "Качество: оценка рекомендаций ≥ 4,5/5 • SUS ≥ 80 • поддержка без повторного контакта ≥ 90%", 13, "$text", align=("center", "middle"), wrap=False))
save_page("09_roadmap.page", p)

# 10 — Final
p = base(10)
e = p["elements"]
e += [text("final_kicker", [55, 91, 350, 24], "FRIDGECHEF", 13, "$green", True, wrap=False),
      text("final_title", [52, 132, 565, 130], "Готовим из того,\nчто есть.", 42, "$navy", True, line_height=1.1),
      text("final_subtitle", [55, 278, 510, 65], "Экономим время, деньги\nи продукты.", 25, "$text", line_height=1.2),
      hline("final_line", 55, 365, 455, "$mid", 2),
      text("final_message", [55, 387, 530, 50], "Единый цикл домашнего питания\nс ИИ и персональными рекомендациями", 17, "$muted"),
      text("final_thanks", [55, 462, 380, 35], "Спасибо за внимание!", 20, "$navy", True, wrap=False),
      icon("final_fridge", [680, 129, 118, 118], "fas:kitchen-set", "$blue"),
      icon("final_food", [749, 235, 88, 88], "fas:bowl-food", "$green"),
      icon("final_calendar", [640, 303, 65, 65], "fas:calendar-days", "$mid"),
      icon("final_cart", [784, 351, 70, 70], "fas:cart-shopping", "$blue"),
      text("final_team", [627, 457, 285, 45], "Шмидт А. В. • Ахмедеев С. Д.\nФельдт А. Д. • ИВТ-244", 12, "$muted", align=("center", "middle"))]
save_page("10_final.page", p)

main = {
    "version": "v2",
    "title": "FridgeChef — ценностное предложение и план развития",
    "size": [960, 540],
    "theme": {
        "colors": C,
        "textStyles": {
            "title": {"fontSize": 28, "fontFamily": "Arial", "color": "$navy", "bold": True},
            "body": {"fontSize": 16, "fontFamily": "Arial", "color": "$text", "lineHeight": 1.25},
            "caption": {"fontSize": 11, "fontFamily": "Arial", "color": "$muted"}
        }
    },
    "pages": [f"pages/{name}" for name in [
        "01_cover.page", "02_customer.page", "03_value.page", "04_business_model.page",
        "05_competitors.page", "06_commercialization.page", "07_pest.page", "08_swot.page",
        "09_roadmap.page", "10_final.page"]]
}
(ROOT / "FridgeChef.pptd").write_text(yaml.dump(main, Dumper=Dumper, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
print(ROOT / "FridgeChef.pptd")
