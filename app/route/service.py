from typing import Annotated, Any
from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import (
    PayTypeResponse,
    MedServiceListResponse,
    ResearchListRequest,
    ResearchListItemResponse,
    TimetableRequest, ResearchGroupRequest
)
from app.service import (
    GatewayService,
    fetch_full_timetable_loop,
    fetch_med_service_list,
    fetch_research_list,
)

router = APIRouter(
    prefix="/service", tags=["Сервисные ручки"], dependencies=[Depends(check_api_key)]
)


@router.post(
    path="/pay_type",
    response_model=list[PayTypeResponse],
    summary="Типы оплаты",
    description="Справочник типов оплаты. Возвращает тип и его id",
)
async def get_pay_type(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
):
    response = await gateway_service.request_json(
        json={
            "params": {
                "c": "MongoDBWork",
                "m": "getData",
                "object": "PayType"
            },
            "data": {
                "object": "PayType",
            }
        }
    )
    return response


# ШАГ 1. Получить список служб
@router.post(
    path="/service_list",
    response_model=list[MedServiceListResponse],
    summary="Список служб.",
    description="Возвращает список служб (наименование и id)",
)
async def get_service_groups(gateway_service: Annotated[GatewayService, Depends(get_gateway_service)]):
    return await fetch_med_service_list(gateway_service)


# ШАГ 2. Получить список исследований в службе
@router.post(
    path="/research_groups_list",
    response_model=list[ResearchListItemResponse],
    summary="Список исследований в определенной службе",
    description="Возвращает список услуг (наименование и id)."
)
async def get_research_groups_list(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
        payload: ResearchListRequest = Body(
            ...,
            openapi_examples={
                "Biochemistry": {
                    "summary": "Биохимия ММЦ",
                    "description": "",
                    "value": {
                        "group_id": "3010101000006800"
                    },
                },
                "Mammography": {
                    "summary": "Маммография",
                    "description": "",
                    "value": {
                        "group_id": "3010101000006230"
                    },
                },
            }
        ),
):
    return await fetch_research_list(gateway_service, payload)


@router.post("/research_group")
async def get_research_group(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: ResearchGroupRequest,
):
    request_data = {
        "Lpu_uid": "13102423",
        "medServiceComplexOnly": "1",
        "level": "0",
        "MedService_id": payload.med_service_id,
    }

    if payload.resource_id:
        request_data["Resource_id"] = payload.resource_id

    response = await gateway_service.request_json(
        json = {
            "params": {
                "c": "Usluga",
                "m": "loadUslugaComplexList"
            },
            "data": request_data
        }
    )
    return response



# @router.post(
#     path="/med_service_complex_list",
#     # response_model=list[MedServiceItemResponse],
#     summary="Справочник списка услуг в определенной группе",
#     description="Справочник списка услуг в определенной группе. Возвращает список услуг (наименование и ids)."
# )


# @router.post(
#     path="/timetable",
#     summary="Получение расписания для услуги"
# )
# async def get_full_timetable(
#         gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
#         payload: TimetableRequest = Body(..., examples=[{
#             "Resource_id": "3010101000001297",  # from service/med_service_group_list
#             "UslugaComplexMedService_id": "3010101000045588"  # from service/med_service_group_list
#         }])
# ) -> dict[str, Any]:
#     results = await fetch_full_timetable_loop(gateway_service, payload)
#
#     # Считаем общее количество слотов для статистики
#     total_slots = sum(len(day_slots) for day_slots in results.values())
#
#     return {
#         "status": "success",
#         "total_days": len(results),
#         "total_slots": total_slots,
#         "data": results
#     }
