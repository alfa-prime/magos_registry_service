import asyncio
import math
from datetime import datetime, timedelta
from collections import defaultdict

from app.core import logger
from app.service import GatewayService
from app.model import TimetableRequestFunc, TimetableRequestLab
from app.model.gateway_request import GatewayRequest
from app.service import parse_timetable_html

# --- КОНФИГУРАЦИЯ ---
DAYS_STEP = 14  # Шаг сетки ЕВМИАС (2 недели)


def _calc_chunks(months: float) -> int:
    """
    Конвертирует месяцы в количество запросов (чанков).
    30.5 дней * months / 14 дней.
    """
    if months <= 0:
        return 1

    days = months * 30.5
    chunks = math.ceil(days / DAYS_STEP)
    return max(1, chunks)  # Минимум 1 запрос


def _group_and_sort_slots(flat_slots: list[dict]) -> dict[str, list[dict]]:
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
        grouped.keys(), key=lambda d: datetime.strptime(d, "%d.%m.%Y")
    )

    # Собираем итоговый словарь и сортируем время
    result = {}
    for date_str in sorted_dates:
        slots = grouped[date_str]
        slots.sort(key=lambda s: s["time"])
        result[date_str] = slots

    return result


async def _execute_html_request(service: GatewayService, json_body: dict) -> list[dict]:
    try:
        req_model = GatewayRequest.model_validate(json_body)
        html_content = await service.request_html(json=req_model.model_dump())
        parsed = parse_timetable_html(html_content)
        return parsed["slots"]
    except Exception as e:
        logger.error(f"[TIMETABLE] Ошибка запроса: {e}")
        return []


async def _fetch_loop_generic(
    service: GatewayService,
    base_payload: dict,
    start_date_str: str,
    controller: str,
    method: str,
    chunks: int,
) -> dict[str, list[dict]]:
    """
    Универсальный цикл параллельной выгрузки.
    """
    logger.info(
        f"[TIMETABLE] Старт выгрузки ({controller}.{method}) на {chunks} чанков с {start_date_str}"
    )

    try:
        start_dt = datetime.strptime(start_date_str, "%d.%m.%Y")
    except ValueError:
        start_dt = datetime.now()

    tasks = []

    for i in range(chunks):
        offset_date = start_dt + timedelta(days=i * DAYS_STEP)
        offset_date_str = offset_date.strftime("%d.%m.%Y")

        # Копируем базовые данные и обновляем дату старта
        current_data = base_payload.copy()
        current_data["StartDay"] = offset_date_str

        gateway_request_body = {
            "params": {"c": controller, "m": method},
            "data": current_data,
        }

        tasks.append(_execute_html_request(service, gateway_request_body))

    # Запускаем параллельно
    results_list = await asyncio.gather(*tasks, return_exceptions=True)

    all_slots = []
    for result in results_list:
        if isinstance(result, list):
            all_slots.extend(result)
        else:
            logger.warning(f"[TIMETABLE] Ошибка в потоке: {result}")

    if not all_slots:
        logger.info("[TIMETABLE] Слоты не найдены.")
        return {}

    grouped_result = _group_and_sort_slots(all_slots)

    logger.info(
        f"[TIMETABLE] Готово. Дней: {len(grouped_result)}. Слотов: {len(all_slots)}"
    )
    return grouped_result


# === PUBLIC FUNCTIONS ===


async def fetch_func_timetable_loop(
    service: GatewayService, payload: TimetableRequestFunc
) -> dict[str, list[dict]]:
    """Расписание для Func (TimetableResource)"""

    chunks_count = _calc_chunks(payload.search_months)

    return await _fetch_loop_generic(
        service=service,
        base_payload=payload.model_dump(by_alias=True),
        start_date_str=payload.start_day,
        controller="TimetableResource",
        method="getTimetableResource",
        chunks=chunks_count,
    )


async def fetch_lab_timetable_loop(
    service: GatewayService, payload: TimetableRequestLab
) -> dict[str, list[dict]]:
    """Расписание для Lab (TimetableMedService)"""

    chunks_count = _calc_chunks(payload.search_months)

    return await _fetch_loop_generic(
        service=service,
        base_payload=payload.model_dump(by_alias=True),
        start_date_str=payload.start_day,
        controller="TimetableMedService",
        method="getTimetableMedService",
        chunks=chunks_count,
    )
