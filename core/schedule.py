# core/schedule.py
import asyncio
from services.google_sheets import fetch_sheet
from datetime import datetime, timedelta

SHEET_ID = "1aIzRQ3AC7kWniSb0lezK616oAwNS41qs_Xm6j2RdBVI"

ROLE_RANGES = {
    "Режиссёры монтажа": (3, 9),
    "Выпускающие редакторы": (11, 17),
    "Дикторы": (25, 32),
}

DATE_ROWS = [3, 11, 18, 25]
LEAVE_ROWS = list(range(33, 39))

MONTAGE_SHIFT_MAP = {
    "1": "1-я смена (9:00 - 17:30)",
    "2": "2-я смена (9:30 - 18:00)",
    "3": "3-я смена (11:00 - 19:30)",
    "4": "4-я смена (12:00 - 20:30)",
    "д": "дежурство",
    "о": "отпуск",
    "б": "болезнь",
    "отг": "отгул",
}

EDITOR_SHIFT_MAP = {
    "1": "1-я смена (7:00 - 15:30)",
    "2": "2-я смена (10:00 - 18:30)",
    "3": "3-я смена (12:00 - 20:30)",
    "д": "дежурство",
    "о": "отпуск",
    "б": "болезнь",
    "отг": "отгул",
}

DICTOR_SHIFT_MAP = {
    "1": "1-я смена (8:30 - 17:00)",
    "2": "2-я смена (10:00 - 18:30)",
    "3": "3-я смена (10:00 - 19:00)",
    "4": "4-я смена (12:00 - 20:30)",
    "д": "дежурство",
    "о": "отпуск",
    "б": "болезнь",
    "отг": "отгул",
}

MONTH_NAMES = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
}

def format_schedule_for_day(df, target_day: int):
    col_index = None
    for j in range(1, df.shape[1]):
        for row_idx in DATE_ROWS:
            if row_idx >= len(df):
                continue
            cell = str(df.iloc[row_idx, j]).strip()
            if cell.isdigit() and int(cell) == target_day:
                col_index = j
                break
        if col_index is not None:
            break

    if col_index is None:
        return f"Нет данных на {target_day}-е число"

    now = datetime.now()
    month_name = MONTH_NAMES[now.month]
    lines = [f"**{target_day} {month_name}**"]

    for role_name, (start_row, end_row) in ROLE_RANGES.items():
        lines.append(f"\n**{role_name}**")

        if role_name == "Режиссёры монтажа":
            shift_map = MONTAGE_SHIFT_MAP
        elif role_name == "Выпускающие редакторы":
            shift_map = EDITOR_SHIFT_MAP
        elif role_name == "Дикторы":
            shift_map = DICTOR_SHIFT_MAP
        else:
            shift_map = {}

        staff_list = []
        for i in range(start_row, min(end_row + 1, len(df))):
            surname = str(df.iloc[i, 0]).strip()
            if surname in ("nan", "", "–", "-"):
                continue
            shift_key = str(df.iloc[i, col_index]).strip().lower()
            shift_text = shift_map.get(shift_key, shift_key if shift_key else "—")

            if shift_key in ("1", "2", "3", "4"):
                priority = int(shift_key)
            else:
                priority = 99

            output_line = f"{shift_text} - {surname}"
            staff_list.append((priority, output_line))

        staff_list.sort(key=lambda x: x[0])
        if staff_list:
            lines.extend([line for _, line in staff_list])
        else:
            lines.append("—")

    leave_lines = []
    for row_idx in LEAVE_ROWS:
        if row_idx >= len(df):
            break
        surname = str(df.iloc[row_idx, 0]).strip()
        if surname in ("nan", "", "–", "-"):
            continue
        status = str(df.iloc[row_idx, col_index]).strip().lower()
        if status in ("о", "отпуск"):
            leave_lines.append(surname)

    if leave_lines:
        lines.append("\n**Отпуска:**")
        lines.extend(leave_lines)

    return "\n".join(lines)

def get_schedule_text(period: str):
    df = asyncio.run(fetch_sheet(SHEET_ID))
    now = datetime.now()

    if period == "today":
        days = [now.day]
    elif period == "tomorrow":
        days = [(now + timedelta(days=1)).day]
    elif period == "week_curr":
        monday = now - timedelta(days=now.weekday())
        days = [(monday + timedelta(days=i)).day for i in range(7)]
    else:
        raise ValueError("Неизвестный период")

    parts = []
    for d in days:
        part = format_schedule_for_day(df, d)
        parts.append(part)

    return "\n\n".join(parts)