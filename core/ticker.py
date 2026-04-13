# core/ticker.py
import asyncio
from services.google_sheets import fetch_sheet
from datetime import datetime
import random
import re

SHEET_ID = "1frLGyZ9w7JQohJZTPaNxgvgDrhsN1cc8xnw7HIWkWUc"

EXCLUDE_WORDS = ["погода", "дайджест", "цифра", "заявили", "рассказали"]

def should_exclude(text: str) -> bool:
    return any(word in text.lower() for word in EXCLUDE_WORDS)

def get_ticker_text():
    df = asyncio.run(fetch_sheet(SHEET_ID))
    if df.shape[1] < 4:
        raise Exception("В таблице меньше 4 столбцов")

    today = datetime.now().strftime("%d.%m")
    today_alt = today.lstrip("0")

    col_a = df.iloc[:, 0].astype(str)
    col_b = df.iloc[:, 1].astype(str)
    col_d = df.iloc[:, 3].astype(str)

    news = []
    for i in range(len(col_a)):
        date_cell = col_a.iloc[i].strip()
        title = col_b.iloc[i].strip()
        filter_cell = col_d.iloc[i].strip()

        if not title or title == "nan":
            continue
        if filter_cell in ("С/Х", "Реклама"):
            continue
        if date_cell not in (today, today_alt):
            continue
        if should_exclude(title):
            continue
        news.append(title)

    if not news:
        raise Exception(f"Нет подходящих новостей на дату {today}")

    selected = random.sample(news, min(20, len(news)))
    clean = [n.rstrip(".,!?;:") for n in selected]
    formatted = [f"0 {item.upper()} //" for item in clean]
    return "\n".join(formatted)