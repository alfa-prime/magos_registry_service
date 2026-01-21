from typing import Annotated, Any

from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import (
    PayTypeResponse,
    MedServiceGroupResponse,
    MedServiceListRequest,
    MedServiceItemResponse, TimetableRequest
)
from app.service import GatewayService, fetch_full_timetable_loop

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


@router.post(
    path="/med_service_groups",
    response_model=list[MedServiceGroupResponse],
    summary="Справочник групп услуг.",
    description="Справочник групп услуг. Возвращает список групп услуг (наименование группы и id)",
)
async def get_med_service_groups(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
):
    response = await gateway_service.request_json(
        json={
            "params": {
                "c": "Reg",
                "m": "getDirectionMedServiceList"
            },
            "data": {
                "object": "MedService",
                "start": "0",
                "limit": "100",
                "Filter_Lpu_Nick": "ФГБУЗ ММЦ им. Н.И. Пирогова ФМБА России",
                "Filter_includeDopProfiles": "0",
                "ARMType": "regpol6",
                "FormName": "swDirectionMasterWindow",
                "DirType_Code": "9",
                "DirType_id": "10",
                "LpuUnitLevel": "1",
                "ListForDirection": "1",
                "isAutoAPLCovid": "0",
                "isSecondRead": "false",
                "isOnlyPolka": "0",
                "groupByMedService": "1",

            }
        }
    )
    return response


@router.post(
    path="/med_service_group_list",
    response_model=list[MedServiceItemResponse],
    summary="Справочник списка услуг в определенной группе",
    description="Справочник списка услуг в определенной группе. Возвращает список услуг (наименование и ids).",
)
async def get_med_service_list(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
        payload: MedServiceListRequest = Body(..., examples=[{"group_id": "3010101000006230"}]),
):
    response = await gateway_service.request_json(
        json={
            "params": {
                "c": "Reg",
                "m": "getDirectionMedServiceList"
            },
            "data": {
                "MedService_id": payload.group_id,
                "object": "MedService",
                "start": "0",
                "limit": "100",
                "Filter_Lpu_Nick": "ФГБУЗ ММЦ им. Н.И. Пирогова ФМБА России",
                "Filter_includeDopProfiles": "0",
                "ARMType": "regpol6",
                "FormName": "swDirectionMasterWindow",
                "DirType_Code": "9",
                "DirType_id": "10",
                "LpuUnitLevel": "1",
                "ListForDirection": "1",
                "isAutoAPLCovid": "0",
                "isSecondRead": "false",
                "isOnlyPolka": "0",
                "groupByMedService": "1",
            }
        }
    )

    raw_data = response if isinstance(response, list) else response.get("data", [])

    for item in raw_data:
        item["group_id"] = payload.group_id

    return raw_data


@router.post(
    path="/timetable",
    summary="Получение расписания для услуги"
)
async def get_full_timetable(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
        payload: TimetableRequest = Body(..., examples=[{
            "Resource_id": "3010101000001297",  # from service/med_service_group_list
            "UslugaComplexMedService_id": "3010101000045588"  # from service/med_service_group_list
        }])
) -> dict[str, Any]:
    results = await fetch_full_timetable_loop(gateway_service, payload)

    # Считаем общее количество слотов для статистики
    total_slots = sum(len(day_slots) for day_slots in results.values())

    return {
        "status": "success",
        "total_days": len(results),
        "total_slots": total_slots,
        "data": results
    }
