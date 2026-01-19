from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

from app.core import logger
from app.service import GatewayService
from app.model import TimetableRequest
from app.model.gateway_request import GatewayRequest
from app.service import parse_timetable_html


def _group_and_sort_slots(flat_slots: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Группирует слоты по датам, сортирует даты по хронологии,
    а внутри дат сортирует слоты по времени.
    """
    grouped = defaultdict(list)
    for slot in flat_slots:
        date_key = slot["date"]
        grouped[date_key].append(slot)

    # Сортируем ключи (даты)
    sorted_dates = sorted(
        grouped.keys(),
        key=lambda d: datetime.strptime(d, "%d.%m.%Y")
    )

    # Собираем итоговый словарь и сортируем время
    result = {}
    for date_str in sorted_dates:
        slots = grouped[date_str]
        slots.sort(key=lambda s: s["time"])
        result[date_str] = slots

    return result


async def fetch_full_timetable_loop(
        service: GatewayService,
        payload: TimetableRequest
) -> Dict[str, List[Dict]]:
    all_slots = []
    current_start_date_str = payload.start_day

    MAX_ITERATIONS = 10
    iteration = 0

    logger.info(f"[TIMETABLE] Старт выгрузки с: {current_start_date_str}")

    while iteration < MAX_ITERATIONS:
        iteration += 1

        current_data = payload.model_dump(by_alias=True)
        current_data["StartDay"] = current_start_date_str

        gateway_request_body = {
            "params": {"c": "TimetableResource", "m": "getTimetableResource"},
            "data": current_data
        }

        req_model = GatewayRequest.model_validate(gateway_request_body)

        try:
            html_content = await service.request_html(json=req_model.model_dump())
        except Exception as e:
            logger.error(f"[TIMETABLE] Ошибка HTTP запроса: {e}")
            break

        parsed = parse_timetable_html(html_content)
        slots = parsed["slots"]
        last_date_str = parsed["last_date"]

        logger.debug(f"[TIMETABLE] Итерация {iteration}: найдено слотов: {len(slots)}")

        # --- ИСПРАВЛЕНИЕ ТУТ ---
        # Если ЕВМИАС вернул сетку, но в ней нет ни одного слота (free или busy),
        # значит мы ушли за пределы реального расписания.
        if not slots:
            logger.info("[TIMETABLE] Слоты не найдены (пустая сетка). Остановка цикла.")
            break

        all_slots.extend(slots)

        # Если даты в навигации кончились (редкий кейс, но возможен)
        if not last_date_str:
            logger.info("[TIMETABLE] Нет дат в навигации. Остановка цикла.")
            break

        try:
            last_date_dt = datetime.strptime(last_date_str, "%d.%m.%Y")
            next_start_dt = last_date_dt + timedelta(days=1)
            current_start_date_str = next_start_dt.strftime("%d.%m.%Y")
        except ValueError:
            break

    # Группировка
    grouped_result = _group_and_sort_slots(all_slots)

    logger.info(f"[TIMETABLE] Выгрузка завершена. Дней: {len(grouped_result)}. Слотов: {len(all_slots)}")
    return grouped_result