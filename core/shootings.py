# core/shootings.py
import asyncio
from services.google_sheets import fetch_sheet
from datetime import datetime, timedelta

SHEET_ID = "10FDlXeoCd0wi9gWqNzH5qQlft9g-ucEvLeYdbsWQRMU"

def clean_cell(value: str) -> str:
    s = str(value).strip()
    if s == "nan" or s == "":
        return "—"
    return s

def get_shootings_text(period: str):
    df = asyncio.run(fetch_sheet(SHEET_ID))
    if df.empty:
        raise Exception("Таблица пуста")

    MONTH_NAMES = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
    }

    now = datetime.now()
    if period == "today":
        target_date = now
        label = "сегодня"
    else:
        target_date = now + timedelta(days=1)
        label = "завтра"

    day = target_date.day
    month_name = MONTH_NAMES[target_date.month]
    target_str = f"{day} {month_name}"

    shooting_rows = []
    for i in range(len(df)):
        date_cell = str(df.iloc[i, 0]).strip()
        if date_cell == target_str:
            shooting_rows.append(i)

    if not shooting_rows:
        return f"Нет запланированных съёмок на {label}."

    blocks = []
    for row_idx in shooting_rows:
        time_val = clean_cell(df.iloc[row_idx, 1])
        title_val = clean_cell(df.iloc[row_idx, 2])
        place_val = clean_cell(df.iloc[row_idx, 3])
        contact_val = clean_cell(df.iloc[row_idx, 4])
        corr_val = clean_cell(df.iloc[row_idx, 5])
        format_val = clean_cell(df.iloc[row_idx, 6])
        video_val = clean_cell(df.iloc[row_idx, 7])
        transport_val = clean_cell(df.iloc[row_idx, 8])

        lines = [
            f"**{time_val}**",
            f"Съёмка: {title_val}",
            f"Место: {place_val}",
            f"Контакт: {contact_val}",
            f"Корреспондент: {corr_val}",
            f"Формат: {format_val}",
            f"Видеограф: {video_val}",
            f"Транспорт: {transport_val}"
        ]
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks)