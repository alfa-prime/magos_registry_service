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
        json = {
            "params": {
                "c": "Usluga",
                "m": "loadUslugaComplexList"
            },
            "data": request_data
        }
    )
    return response


async def get_target_ids(service: GatewayService):
    target = await service.request_json(
        json={
            "params": {
                "c": "MedServiceLink",
                "m": "loadList",
            },
            "data": {
                "object": "MedServiceLink",
                "MedService_id": "3010101000016781",
                "ARMType": "pzm",
                "MedServiceLinkType_id": "1",
                "MedServiceType_SysNick": "lab",
            }
        }
    )
    result_target = []
    for item in target:
        result_target.append({
            "id": item.get("MedServiceLink_id"),
            "name": item.get("MedService_lid_Name")
        })
    return result_target


async def get_source_ids(service: GatewayService):
    source = await service.request_json(
        json={
            "params": {
                "c": "MedServiceLink",
                "m": "loadList",
            },
            "data": {
                "object": "MedServiceLink",
                "MedService_id": "3010101000012640",
                "ARMType": "pzm",
                "MedServiceLinkType_id": "1",
                "MedServiceType_SysNick": "lab",
            }
        }
    )
    result_source = []
    for item in source:
        result_source.append({
            "id": item.get("MedServiceLink_id"),
            "name": item.get("MedService_lid_Name")
        })
    return result_source


async def merge_ids(target: list, source: list):
    # EXCLUDE_NAMES = [  # noqa
    #     "Общеклинические исслед. ММЦ",
    #     "Инфекционная иммунология ММЦ",
    #     "Инвитро Цитологические исследования",
    #     "Инвитро Риск развития многофакторных заболеваний",
    #     "Инвитро Репродуктивное здоровье",
    #     "Инвитро ПЦР-диагностика инфекционных заболеваний",
    # ]

    final_result = []

    for source_item in source:
        for target_item in target:
            # if (source_item.get("name") == target_item.get("name")) and (source_item.get("name") not in EXCLUDE_NAMES):
            if source_item.get("name") == target_item.get("name"):
                final_result.append({
                    "name": source_item.get("name"),
                    "source_id": source_item.get("id"),
                    "target_id": target_item.get("id")
                })
    return final_result


async def get_source_services(service: GatewayService, ids: list[dict]):
    result = {}
    for item in ids:
        response = await service.request_json(
            json={
                "params": {
                    "c": "MedServiceLinkUslugaComplexLink",
                    "m": "loadGrid"
                },
                "data": {
                    "MedServiceLink_id": item.get("source_id"),
                    "object": "MedServiceLinkUslugaComplexLink",
                }
            }
        )


        record = []
        for item_ in response:
            record.append({
                "name": item_.get("UslugaComplex_Name"),
                "id": item_.get("UslugaComplex_id"),
                "code": item_.get("UslugaComplex_Code")
            })

        result[item.get("target_id")] = record
    return result




@router.post("/test")
async def test(gateway_service: Annotated[GatewayService, Depends(get_gateway_service)]):
    target_ids = await get_target_ids(service=gateway_service)
    source_ids = await get_source_ids(service=gateway_service)
    merged_ids = await merge_ids(source=source_ids, target=target_ids)
    source_services = await get_source_services(gateway_service, merged_ids)

    for source_id, source_service_list in source_services.items():
        for elem in source_service_list:
            response = await gateway_service.request_json(
                json={
                    "params": {
                        "c": "MedServiceLinkUslugaComplexLink",
                        "m": "doSave",
                    },
                    "data": {
                        "MedServiceLink_id": source_id,
                        "UslugaComplex_id": elem.get("id"),
                        "UslugaComplex_Code": elem.get("code"),
                        "UslugaComplex_Name": elem.get("name"),
                        "MedServiceLinkUslugaComplexLink_begDate": "01.01.2026",
                    }
                }
            )
            logger.debug(response)
    # print(merged_ids)
    # print(source_services)
    return {"all done."}







@router.post("/get_ids")
async def get_ids(gateway_service: Annotated[GatewayService, Depends(get_gateway_service)]):
    response = await gateway_service.request_json(
        json = {
            "params": {
                "c": "MedServiceLinkUslugaComplexLink",
                "m": "loadGrid"
            },
            "data": {
                "MedServiceLink_id": "3010101000005329",
                "object": "MedServiceLinkUslugaComplexLink",
            }
        }
    )
    result = []
    for item in response:
        result.append({
            "name": item.get("UslugaComplex_Name"),
            "id": item.get("UslugaComplex_id"),
            "code": item.get("UslugaComplex_Code")
        })

    for item in result:
        response = await gateway_service.request_json(
            json={
                "params": {
                    "c": "MedServiceLinkUslugaComplexLink",
                    "m": "doSave",
                },
                "data": {
                    "MedServiceLink_id": "3010101000006102",
                    "UslugaComplex_id": item.get("id"),
                    "UslugaComplex_Code": item.get("code"),
                    "UslugaComplex_Name": item.get("name"),
                    "MedServiceLinkUslugaComplexLink_begDate": "01.01.2026",
                }
            }
        )
        logger.debug(response)


# @router.post("/collection_point")
# async def get_collection_point_list(
#         gateway_service: Annotated[GatewayService, Depends(get_gateway_service)]
# ):
#     response = await gateway_service.request_json(
#         json={
#             "params": {
#                 "c": "MedService",
#                 "m": "loadList"
#             },
#             "data": {
#                 "MedServiceType_SysNick": "pzm",
#                 "MedService_lid": "3010101000006800",
#             }
#         }
#     )
#     logger.debug(f"Collection points : {len(response)}")
#     return response
#
#
# @router.post("/timetable", summary="Полная выгрузка расписания")
# async def get_full_timetable(
#         gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
#         payload: TimetableRequest = Body(..., examples=[{
#             "Person_id": "3010101001541772",
#             "Resource_id": "3010101000001297",
#             "UslugaComplexMedService_id": "3010101000045588"
#         }])
# ) -> Dict[str, Any]:
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
#
#
# def _clean_html_field(raw_html: str | None) -> str | None:
#     if not raw_html:
#         return None
#     text = BeautifulSoup(raw_html, "html.parser").get_text(strip=True)
#     return text if text else None
#
#
# @router.post(
#     path="/patient",
#     response_model=PatientSearchResponse,
#     summary="Поиск пациента в ЕВМИАС по ФИО и ДР"
# )
# async def patient_search(
#         gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
#         payload: PatientRequest = Body(..., examples=[{
#             "last_name": "жулидова",
#             "first_name": "елена",
#             "middle_name": "вячеславовна",
#             "birthday": "08.08.1972"
#         }])
# ):
#     logger.info("Start search patient")
#     logger.debug(payload)
#
#     response = await gateway_service.request_json(
#         json={
#             "params": {
#                 "c": "Person6E",
#                 "m": "getPersonGrid",
#                 "_dc": int(time.time())
#             },
#             "data": {
#                 "start": "0",
#                 "limit": "100",
#                 "Double_ids": "[]",
#                 "Person_Surname": payload.last_name,
#                 "Person_Firname": payload.first_name,
#                 "Person_Secname": payload.middle_name,
#                 "Person_Birthday": payload.birthday,
#                 "Org_id": "13103164",
#                 "showAll": "1",
#                 "dontShowUnknowns": "1",
#                 "page": "1",
#
#             }
#         }
#     )
#
#     raw_patients = response.get("data", []) or []
#
#     result_items = []
#
#     for patient in raw_patients:
#         raw_s = patient.get("Person_Surname")
#         raw_n = patient.get("Person_Firname")
#         raw_p = patient.get("Person_Secname")
#
#         s_title = raw_s.title() if raw_s else ""
#         n_title = raw_n.title() if raw_n else ""
#         p_title = raw_p.title() if raw_p else None
#
#         record = PatientFoundItem(
#             surname=s_title,
#             name=n_title,
#             patronymic=p_title,
#             full_name=" ".join(filter(None, [s_title, n_title, p_title])),
#             birthday=patient.get("Person_Birthday", ""),
#             age=str(patient.get("Person_Age", "")),
#             polis=_clean_html_field(patient.get("Polis_Num")),
#             phone=_clean_html_field(patient.get("Person_Phone")),
#             inn=patient.get("Person_Inn") or None,
#             address_registration=patient.get("Person_PAddress") or None,
#             address_residential=patient.get("Person_UAddress") or None,
#             attach_lpu_name=patient.get("AttachLpu_Name"),
#             lpu_region_name=patient.get("LpuRegion_Name"),
#             person_id=str(patient.get("Person_id")),
#             person_card_id=str(patient.get("PersonCard_id")) if patient.get("PersonCard_id") else None,
#             server_id=str(patient.get("Server_id")),
#             person_env_id=str(patient.get("PersonEvn_id")),
#             attach_lpu_id=str(patient.get("AttachLpu_id"))
#         )
#
#         result_items.append(record)
#
#     return result_items
