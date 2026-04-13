# core/digests.py
import asyncio
from services.google_sheets import fetch_sheet
from datetime import datetime
import re

SHEET_ID = "1frLGyZ9w7JQohJZTPaNxgvgDrhsN1cc8xnw7HIWkWUc"

RUBRIC_ORDER_00_40 = ["Политика", "Благоустройство", "Общество", "Культура", "Спорт"]
RUBRIC_ORDER_20 = ["Политика", "Общество", "Авто", "Культура", "Опрос"]

def parse_time(time_str: str):
    time_str = time_str.strip()
    if not time_str or time_str == "nan" or time_str == "":
        return None
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return None
        h, m = int(parts[0]), int(parts[1])
        return h * 60 + m
    except (ValueError, AttributeError):
        return None

def get_digest_text():
    df = asyncio.run(fetch_sheet(SHEET_ID))
    if df.shape[1] < 8:
        raise Exception("В таблице меньше 8 столбцов")

    today = datetime.now().strftime("%d.%m")
    today_alt = today.lstrip("0")
    current_time_minutes = datetime.now().hour * 60 + datetime.now().minute
    is_before_noon = current_time_minutes < 12 * 60

    col_a = df.iloc[:, 0].astype(str)
    col_b = df.iloc[:, 1].astype(str)
    col_c = df.iloc[:, 2].astype(str)
    col_d = df.iloc[:, 3].astype(str)
    col_e = df.iloc[:, 4].astype(str)
    col_h = df.iloc[:, 7].astype(str)

    items = []
    for i in range(len(col_a)):
        date_cell = col_a.iloc[i].strip()
        title = col_b.iloc[i].strip()
        comment = col_c.iloc[i].strip()
        fmt = col_d.iloc[i].strip()
        rubric = col_e.iloc[i].strip()
        time_added = col_h.iloc[i].strip()

        if not title or title == "nan":
            continue
        if date_cell not in (today, today_alt):
            continue
        parsed_time = parse_time(time_added)
        if parsed_time is None:
            continue
        if is_before_noon:
            if parsed_time > 12 * 60:
                continue
        else:
            if parsed_time <= 12 * 60:
                continue

        rubric_key = rubric.lower().strip()
        block = None
        if fmt in ("Шторки Р", "Хайлайты Р"):
            if rubric_key in [r.lower() for r in RUBRIC_ORDER_00_40]:
                block = "00_40"
        elif fmt in ("Шторки Ф", "Хайлайты Ф"):
            if rubric_key in [r.lower() for r in RUBRIC_ORDER_20]:
                block = "20"

        if block:
            items.append({
                "title": title,
                "comment": comment if comment and comment != "nan" else None,
                "rubric": rubric_key,
                "block": block
            })

    if not items:
        return f"Нет подходящих новостей на дату {today}"

    block_00_40 = [i for i in items if i["block"] == "00_40"]
    block_20 = [i for i in items if i["block"] == "20"]

    def sort_key(item, order):
        order_lower = [r.lower() for r in order]
        try:
            return order_lower.index(item["rubric"])
        except ValueError:
            return 999

    block_00_40.sort(key=lambda x: sort_key(x, RUBRIC_ORDER_00_40))
    block_20.sort(key=lambda x: sort_key(x, RUBRIC_ORDER_20))

    block_00_40 = block_00_40[:5]
    block_20 = block_20[:5]

    lines = []
    lines.append("00, 40 минут:")
    for item in block_00_40:
        lines.append(f"- {item['title']}")
        if item["comment"]:
            lines.append(f"__{item['comment']}__")

    lines.append("")
    lines.append("20 минут:")
    for item in block_20:
        lines.append(f"- {item['title']}")
        if item["comment"]:
            lines.append(f"__{item['comment']}__")

    return "\n".join(lines)