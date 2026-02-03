from datetime import datetime
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import (
    TimetableResponse,
    TimetableRequestFunc,
    TimetableRequestLab,
)
from app.service import (
    GatewayService,
    fetch_func_timetable_loop,
    fetch_lab_timetable_loop,
)


router = APIRouter(
    prefix="/timetable",
    tags=["Получение расписаний"],
    dependencies=[Depends(check_api_key)],
)


@router.post(
    path="/func",
    response_model=TimetableResponse,
    summary="Получение расписания для функциональных услуг (рентген, узи, ...)",
    description="Возвращает доступные и занятые слоты для выбранной услуги и ресурса. "
                "Количество месяцев, за которые будет парситься расписание, указано в .env",
)
async def get_full_timetable_func(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: TimetableRequestFunc = Body(
        ...,
        openapi_examples={
            "Маммография (тест)": {
                "summary": "Маммография - Маммография. Быстрый запрос (2 недели)",
                "value": {
                    "StartDay": datetime.now().strftime("%d.%m.%Y"),
                    "Resource_id": "3010101000001297",
                    "UslugaComplexMedService_id": "3010101000045588",
                    "search_months": 0.5
                },
            },
            "Маммография (полный)": {
                "summary": "Маммография - Маммография. Полный запрос",
                "value": {
                    "StartDay": datetime.now().strftime("%d.%m.%Y"),
                    "Resource_id": "3010101000001297",
                    "UslugaComplexMedService_id": "3010101000045588",
                },
            },
            "Кабинет УЗИ ММЦ": {
                "summary": "Кабинет УЗИ ММЦ - Дуплексное сканирование артерий почек. Полный запрос",
                "value": {
                    "StartDay": datetime.now().strftime("%d.%m.%Y"),
                    "Resource_id": "3010101000001303",
                    "UslugaComplexMedService_id": "3010101000045662",
                },
            },
        },
    ),
) -> Any:
    results = await fetch_func_timetable_loop(gateway_service, payload)

    # Считаем общее количество слотов для статистики
    total_slots = sum(len(day_slots) for day_slots in results.values())

    return {
        "status": "success",
        "total_days": len(results),
        "total_slots": total_slots,
        "data": results,
    }


@router.post(
    path="/lab",
    response_model=TimetableResponse,
    summary="Получение расписания для лабораторий (анализы)",
    description="Возвращает доступные и занятые слоты для выбранной услуги и ресурса. "
                "Количество месяцев, за которые будет парситься расписание, указано в .env",
)
async def get_full_timetable_lab(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: TimetableRequestLab = Body(
        ...,
        openapi_examples={
            "Биохимия ММЦ (тест)": {
                "summary": "Пункт забора - Поликлиника каб. 121. Быстрый запрос (2 недели)",
                "value": {
                    # "Person_id": "3010101002119698",
                    "StartDay": datetime.now().strftime("%d.%m.%Y"),
                    "MedService_id": "3010101000011422",
                    "search_months": 0.5
                },
            },
            "Биохимия ММЦ (полный)": {
                "summary": "Пункт забора - Поликлиника каб. 121. Полный запрос",
                "value": {
                    # "Person_id": "3010101002119698",
                    "StartDay": datetime.now().strftime("%d.%m.%Y"),
                    "MedService_id": "3010101000011422",
                },
            },
        },
    ),
) -> Any:
    results = await fetch_lab_timetable_loop(gateway_service, payload)
    total_slots = sum(len(day_slots) for day_slots in results.values())
    return {
        "status": "success",
        "total_days": len(results),
        "total_slots": total_slots,
        "data": results,
    }
