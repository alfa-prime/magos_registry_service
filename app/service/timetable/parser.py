import re
from typing import Dict, Any
from bs4 import BeautifulSoup


def _extract_qtip_data(qtip_html: str) -> dict:
    """
    Парсит содержимое всплывающей подсказки (ext:qtip).
    Извлекает комментарий (div.ttcomments) и остальной текст.
    """
    if not qtip_html:
        return {"comment": None, "info": None}

    soup = BeautifulSoup(qtip_html, "html.parser")

    # 1. Ищем специфический комментарий (в блоке div class='ttcomments')
    comment = None
    comment_div = soup.find("div", class_="ttcomments")
    if comment_div:
        # Извлекаем текст, например "САХАР С НАГРУЗКОЙ СУРИКОВА ЕЛЕНА..."
        comment = comment_div.get_text(separator=" ", strip=True)
        # Удаляем этот блок из дерева, чтобы он не попал в general info
        comment_div.decompose()

    # 2. Удаляем жирный заголовок "Свободно" (он нам не нужен в тексте)
    bold_status = soup.find("b", string="Свободно")
    if bold_status:
        bold_status.decompose()

    # 3. Всё остальное — это общая информация (например "По направлению")
    # get_text соберет оставшийся текст, strip=True уберет лишние пробелы и br
    info = soup.get_text(separator=" ", strip=True)

    # Если info пустой, ставим None
    if not info:
        info = None

    return {"comment": comment, "info": info}


def parse_timetable_html(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")

    # --- 1. Извлекаем ДНИ НЕДЕЛИ ---
    column_days = []
    header_cells = soup.select("tr.head td b")
    for b_tag in header_cells:
        column_days.append(b_tag.get_text(strip=True))

    # --- 2. Извлекаем ПОЛНЫЕ ДАТЫ ---
    column_dates = []
    footer_links = soup.select("tr.foot td.erlink a")
    date_pattern = re.compile(r"openDayList\w+\('(\d{2}\.\d{2}\.\d{4})'\)")

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
            if idx >= len(column_dates):
                break

            current_date = column_dates[idx]
            current_day = column_days[idx] if idx < len(column_days) else "?"
            classes = cell.get("class", [])

            # === СВОБОДНЫЙ СЛОТ ===
            if "free" in classes:
                time_text = cell.get_text(strip=True)
                if not time_text:
                    continue

                onclick_val = cell.get("onclick", "")
                slot_id = None
                match_id = slot_id_pattern.search(onclick_val)
                if match_id:
                    slot_id = match_id.group(1)

                # --- ЛОГИКА ПАРСИНГА qtip ---
                qtip_raw = cell.get("ext:qtip", "")
                parsed_qtip = _extract_qtip_data(qtip_raw)

                slots.append(
                    {
                        "date": current_date,
                        "day": current_day,
                        "time": time_text,
                        "status": "free",
                        "slot_id": slot_id,
                        "comment": parsed_qtip["comment"],
                        "info": parsed_qtip["info"],
                    }
                )

            # === ЗАНЯТЫЙ СЛОТ ===
            elif any(cls.endswith("_person") for cls in classes):
                raw_text = cell.get_text(strip=True)
                time_text = raw_text[:5]
                qtip_html = cell.get("ext:qtip", "")

                slots.append(
                    {
                        "date": current_date,
                        "day": current_day,
                        "time": time_text,
                        "status": "busy",
                        "details": qtip_html,
                    }
                )

    return {
        "last_date": column_dates[-1] if column_dates else None,
        "slots": slots,
    }
