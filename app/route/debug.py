from typing import Annotated, Dict, Any, List
from fastapi import APIRouter, Depends, Body
import time
from bs4 import BeautifulSoup

from app.core import get_gateway_service, logger
from app.service import GatewayService
from app.model import TimetableRequest, PatientRequest, PatientFoundItem, PatientSearchResponse, ResearchGroupRequest
from app.service import fetch_full_timetable_loop
from app.temp_json.time_table_json import TIME_TABLE_JSON

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/timetable_json")
async def get_timetable_json():
    return TIME_TABLE_JSON


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
        json={
            "params": {
                "c": "Usluga",
                "m": "loadUslugaComplexList"
            },
            "data": request_data
        }
    )
    return response


# async def get_target_ids(service: GatewayService):
#     target = await service.request_json(
#         json={
#             "params": {
#                 "c": "MedServiceLink",
#                 "m": "loadList",
#             },
#             "data": {
#                 "object": "MedServiceLink",
#                 "MedService_id": "3010101000016781",
#                 "ARMType": "pzm",
#                 "MedServiceLinkType_id": "1",
#                 "MedServiceType_SysNick": "lab",
#             }
#         }
#     )
#     result_target = []
#     for item in target:
#         result_target.append({
#             "id": item.get("MedServiceLink_id"),
#             "name": item.get("MedService_lid_Name")
#         })
#     return result_target
#
#
# async def get_source_ids(service: GatewayService):
#     source = await service.request_json(
#         json={
#             "params": {
#                 "c": "MedServiceLink",
#                 "m": "loadList",
#             },
#             "data": {
#                 "object": "MedServiceLink",
#                 "MedService_id": "3010101000012640",
#                 "ARMType": "pzm",
#                 "MedServiceLinkType_id": "1",
#                 "MedServiceType_SysNick": "lab",
#             }
#         }
#     )
#     result_source = []
#     for item in source:
#         result_source.append({
#             "id": item.get("MedServiceLink_id"),
#             "name": item.get("MedService_lid_Name")
#         })
#     return result_source
#
#
# async def merge_ids(target: list, source: list):
#     # EXCLUDE_NAMES = [  # noqa
#     #     "Общеклинические исслед. ММЦ",
#     #     "Инфекционная иммунология ММЦ",
#     #     "Инвитро Цитологические исследования",
#     #     "Инвитро Риск развития многофакторных заболеваний",
#     #     "Инвитро Репродуктивное здоровье",
#     #     "Инвитро ПЦР-диагностика инфекционных заболеваний",
#     # ]
#
#     final_result = []
#
#     for source_item in source:
#         for target_item in target:
#             # if (source_item.get("name") == target_item.get("name")) and (source_item.get("name") not in EXCLUDE_NAMES):
#             if source_item.get("name") == target_item.get("name"):
#                 final_result.append({
#                     "name": source_item.get("name"),
#                     "source_id": source_item.get("id"),
#                     "target_id": target_item.get("id")
#                 })
#     return final_result
#
#
# async def get_source_services(service: GatewayService, ids: list[dict]):
#     result = {}
#     for item in ids:
#         response = await service.request_json(
#             json={
#                 "params": {
#                     "c": "MedServiceLinkUslugaComplexLink",
#                     "m": "loadGrid"
#                 },
#                 "data": {
#                     "MedServiceLink_id": item.get("source_id"),
#                     "object": "MedServiceLinkUslugaComplexLink",
#                 }
#             }
#         )
#
#         record = []
#         for item_ in response:
#             record.append({
#                 "name": item_.get("UslugaComplex_Name"),
#                 "id": item_.get("UslugaComplex_id"),
#                 "code": item_.get("UslugaComplex_Code")
#             })
#
#         result[item.get("target_id")] = record
#     return result
#
#
# @router.post("/test")
# async def test(gateway_service: Annotated[GatewayService, Depends(get_gateway_service)]):
#     target_ids = await get_target_ids(service=gateway_service)
#     source_ids = await get_source_ids(service=gateway_service)
#     merged_ids = await merge_ids(source=source_ids, target=target_ids)
#     source_services = await get_source_services(gateway_service, merged_ids)
#
#     for source_id, source_service_list in source_services.items():
#         for elem in source_service_list:
#             response = await gateway_service.request_json(
#                 json={
#                     "params": {
#                         "c": "MedServiceLinkUslugaComplexLink",
#                         "m": "doSave",
#                     },
#                     "data": {
#                         "MedServiceLink_id": source_id,
#                         "UslugaComplex_id": elem.get("id"),
#                         "UslugaComplex_Code": elem.get("code"),
#                         "UslugaComplex_Name": elem.get("name"),
#                         "MedServiceLinkUslugaComplexLink_begDate": "01.01.2026",
#                     }
#                 }
#             )
#             logger.debug(response)
#     # print(merged_ids)
#     # print(source_services)
#     return {"all done."}
