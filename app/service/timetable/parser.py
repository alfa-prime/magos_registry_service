import re
from typing import Dict, Any
from bs4 import BeautifulSoup


def parse_timetable_html(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")

    # --- 1. Извлекаем ДНИ НЕДЕЛИ из шапки таблицы ---
    # Структура: <tr class=head><td class="work"><b>ПН</b> 12</td>...</tr>
    column_days = []
    # Ищем строку с классом head, внутри ячейки, внутри тег b
    header_cells = soup.select("tr.head td b")

    for b_tag in header_cells:
        column_days.append(b_tag.get_text(strip=True))

    # --- 2. Извлекаем ПОЛНЫЕ ДАТЫ из футера ---
    column_dates = []
    footer_links = soup.select("tr.foot td.erlink a")
    date_pattern = re.compile(r"openDayListTTR\('(\d{2}\.\d{2}\.\d{4})'\)")

    for link in footer_links:
        onclick_val = link.get("onclick", "")
        match = date_pattern.search(onclick_val)
        if match:
            column_dates.append(match.group(1))

    if not column_dates:
        return {"last_date": None, "slots": []}

    # --- 3. Парсим слоты ---
    slots = []
    time_rows = soup.select("tr.time")
    slot_id_pattern = re.compile(r"recordPerson\(\s*(\d+)")

    for row in time_rows:
        cells = row.find_all("td", recursive=False)

        for idx, cell in enumerate(cells):
            # Защита от выхода за границы массивов
            if idx >= len(column_dates):
                break

            current_date = column_dates[idx]

            # Берем день недели из массива, который собрали в шаге 1.
            # Если вдруг структура разъехалась (маловероятно), ставим заглушку.
            current_day = column_days[idx] if idx < len(column_days) else "?"

            classes = cell.get("class", [])

            # --- Свободный слот ---
            if "free" in classes:
                time_text = cell.get_text(strip=True)
                if not time_text:
                    continue

                onclick_val = cell.get("onclick", "")
                slot_id = None
                match_id = slot_id_pattern.search(onclick_val)
                if match_id:
                    slot_id = match_id.group(1)

                slots.append({
                    "date": current_date,
                    "day": current_day,  # <--- Берем из HTML
                    "time": time_text,
                    "status": "free",
                    "slot_id": slot_id,
                })

            # --- Занятый слот ---
            elif any(cls.endswith("_person") for cls in classes):
                raw_text = cell.get_text(strip=True)
                time_text = raw_text[:5]
                qtip_html = cell.get("ext:qtip", "")

                slots.append({
                    "date": current_date,
                    "day": current_day,  # <--- Берем из HTML
                    "time": time_text,
                    "status": "busy",
                    "details": qtip_html
                })

    return {
        "last_date": column_dates[-1] if column_dates else None,
        "slots": slots
    }