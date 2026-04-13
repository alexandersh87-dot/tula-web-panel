# core/dictors.py
import asyncio
from services.google_sheets import fetch_sheet
from collections import Counter
import re
from datetime import datetime

SHEET_ID = "1frLGyZ9w7JQohJZTPaNxgvgDrhsN1cc8xnw7HIWkWUc"

# Приводим к нижнему регистру для надёжного сравнения
ALLOWED_LOWER = {name.lower() for name in ["Матюхина", "Дрынкин", "Черепанова", "Визиренко", "Лебедев"]}

PLAN_SHARE = {
    "Матюхина": 0.25,
    "Черепанова": 0.25,
    "Лебедев": 0.25,
    "Визиренко": 0.125,
    "Дрынкин": 0.125,
}

MONTH_NAMES = {
    1: "январь", 2: "февраль", 3: "март", 4: "апрель",
    5: "май", 6: "июнь", 7: "июль", 8: "август",
    9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь",
}

def get_dictors_text():
    df = asyncio.run(fetch_sheet(SHEET_ID))
    if df.shape[1] < 9:
        raise Exception("В таблице меньше 9 столбцов (ожидается столбец I)")

    col_a = df.iloc[:, 0].astype(str)   # дата (столбец A)
    col_i = df.iloc[:, 8].astype(str)   # дикторы (столбец I)

    valid_names = []
    month_candidates = []

    for i in range(len(col_a)):
        raw_name = str(col_i.iloc[i]).strip()
        date_str = str(col_a.iloc[i]).strip()

        # Нормализуем имя: убираем пробелы, приводим к нижнему регистру
        name_clean = raw_name.lower().strip()

        if name_clean in ALLOWED_LOWER:
            # Восстанавливаем оригинальное имя для вывода (с сохранением регистра из таблицы)
            original_name = raw_name.strip()
            valid_names.append(original_name)

            # Пытаемся извлечь месяц из даты
            match = re.search(r"\b(\d{1,2})\.(\d{1,2})\b", date_str)
            if match:
                try:
                    month_num = int(match.group(2))
                    if 1 <= month_num <= 12:
                        month_candidates.append(month_num)
                except ValueError:
                    pass

    if not valid_names:
        # Для отладки: покажем первые 5 значений из столбца I
        sample_names = [str(col_i.iloc[i]).strip() for i in range(min(5, len(col_i)))]
        raise Exception(f"Нет упоминаний дикторов из списка. Примеры из столбца I: {sample_names}")

    # Определяем месяц отчёта
    if month_candidates:
        from collections import Counter as MonthCounter
        report_month_num = MonthCounter(month_candidates).most_common(1)[0][0]
    else:
        report_month_num = datetime.now().month

    now = datetime.now()
    year = now.year
    if now.month == 12 and report_month_num in (1, 2):
        year = now.year + 1
    elif now.month in (1, 2) and report_month_num >= 10:
        year = now.year - 1

    report_label = f"{MONTH_NAMES[report_month_num]} {year}"
    total = len(valid_names)
    fact = Counter(valid_names)
    lines = [f"План по дикторам за {report_label}:"]
    for name in ["Матюхина", "Черепанова", "Лебедев", "Визиренко", "Дрынкин"]:
        plan_val = PLAN_SHARE[name] * total
        fact_val = fact.get(name, 0)
        pct = (fact_val / plan_val * 100) if plan_val > 0 else 0
        lines.append(f"{name} — план: {plan_val:.2f}, факт: {fact_val} → {pct:.1f}%")

    return "\n".join(lines)