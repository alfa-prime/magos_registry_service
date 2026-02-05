import asyncio
from typing import Annotated, Any
from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import (
    MedServiceListResponse,
    ResearchListRequest,
    ResearchListItemResponse,
    LabComplexResponse,
    LabComplexRequest,
)
from app.service import (
    GatewayService,
    fetch_med_service_list,
    fetch_research_list,
    fetch_collection_point_list,
    fetch_complex_service_list,
)

router = APIRouter(
    prefix="/registry",
    tags=["Основные запросы"],
    dependencies=[Depends(check_api_key)],
)


# ШАГ 1. Получить список служб
@router.post(
    path="/get_med_service_list",
    response_model=list[MedServiceListResponse],
    summary="Список служб.",
    description="Возвращает список служб (наименование + id)",
)
async def get_service_groups(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
):
    return await fetch_med_service_list(gateway_service)


# ШАГ 2. Получить список комплексных уcлуг в службе
@router.post(
    path="/get_complete_service",
    response_model=list[ResearchListItemResponse],
    summary="Список услуг в службе",
    description="Возвращает список услуг. Модель ответа зависит от типа услуги (lab/func).",
)
async def get_research_groups_list(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: ResearchListRequest = Body(
        ...,
        openapi_examples={
            "Biochemistry": {
                "summary": "Биохимия ММЦ",
                "description": "",
                "value": {"group_id": "3010101000006800"},
            },
            "Mammography": {
                "summary": "Маммография",
                "description": "",
                "value": {"group_id": "3010101000006230"},
            },
            "UltraSoundMMC": {
                "summary": "Кабинет УЗИ стационар ММЦ",
                "description": "",
                "value": {"group_id": "3010101000006233"},
            },
        },
    ),
):
    return await fetch_research_list(gateway_service, payload)


@router.post(
    path="/lab_complex_details",
    response_model=LabComplexResponse,
    summary="Список исследований в лабораторной услуге + список пунктов забора биоматериалов",
    description="Возвращает список пунктов забора биоматериалов 'collection_points' и список исследований 'services_in_service'.",
)
async def get_lab_complex_details(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: LabComplexRequest = Body(
        ...,
        openapi_examples={
            "Биохимия": {
                "summary": "Пример: Биохимия ММЦ",
                "value": {
                    "med_service_id": "3010101000006800",
                    "usluga_complex_id": "206894",
                    "usluga_complex_med_service_id": "3010101000053307",
                    "med_service_type_sys_nick": "lab"
                },
            }
        },
    ),
) -> Any:

    if payload.med_service_type_sys_nick != "lab":
        return {
            "collection_points": [],
            "services_in_service": [],
        }

    collection_points_task = fetch_collection_point_list(gateway_service, payload)
    complex_services_task = fetch_complex_service_list(gateway_service, payload)

    collection_points_data, complex_services_data = await asyncio.gather(
        collection_points_task, complex_services_task
    )

    return {
        "collection_points": collection_points_data,
        "services_in_service": complex_services_data,
    }
