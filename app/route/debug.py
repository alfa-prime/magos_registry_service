from typing import Annotated, Dict, Any, List
from fastapi import APIRouter, Depends, Body
import time
from bs4 import BeautifulSoup

from app.core import get_gateway_service, logger
from app.service import GatewayService
from app.model import TimetableRequest, PatientRequest, PatientFoundItem, PatientSearchResponse
from app.service import fetch_full_timetable_loop
from app.temp_json.time_table_json import TIME_TABLE_JSON

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/timetable_json")
async def get_timetable_json():
    return TIME_TABLE_JSON


@router.post("/timetable", summary="Полная выгрузка расписания")
async def get_full_timetable(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
        payload: TimetableRequest = Body(..., examples=[{
            "Person_id": "3010101001541772",
            "Resource_id": "3010101000001297",
            "UslugaComplexMedService_id": "3010101000045588"
        }])
) -> Dict[str, Any]:
    results = await fetch_full_timetable_loop(gateway_service, payload)

    # Считаем общее количество слотов для статистики
    total_slots = sum(len(day_slots) for day_slots in results.values())

    return {
        "status": "success",
        "total_days": len(results),
        "total_slots": total_slots,
        "data": results
    }


def _clean_html_field(raw_html: str | None) -> str | None:
    if not raw_html:
        return None
    text = BeautifulSoup(raw_html, "html.parser").get_text(strip=True)
    return text if text else None


@router.post(
    path="/patient",
    response_model=PatientSearchResponse,
    summary="Поиск пациента в ЕВМИАС по ФИО и ДР"
)
async def patient_search(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
        payload: PatientRequest = Body(..., examples=[{
            "last_name": "жулидова",
            "first_name": "елена",
            "middle_name": "вячеславовна",
            "birthday": "08.08.1972"
        }])
):
    logger.info("Start search patient")
    logger.debug(payload)

    response = await gateway_service.request_json(
        json={
            "params": {
                "c": "Person6E",
                "m": "getPersonGrid",
                "_dc": int(time.time())
            },
            "data": {
                "start": "0",
                "limit": "100",
                "Double_ids": "[]",
                "Person_Surname": payload.last_name,
                "Person_Firname": payload.first_name,
                "Person_Secname": payload.middle_name,
                "Person_Birthday": payload.birthday,
                "Org_id": "13103164",
                "showAll": "1",
                "dontShowUnknowns": "1",
                "page": "1",

            }
        }
    )

    raw_patients = response.get("data", []) or []

    result_items = []

    for patient in raw_patients:
        raw_s = patient.get("Person_Surname")
        raw_n = patient.get("Person_Firname")
        raw_p = patient.get("Person_Secname")

        s_title = raw_s.title() if raw_s else ""
        n_title = raw_n.title() if raw_n else ""
        p_title = raw_p.title() if raw_p else None

        record = PatientFoundItem(
            surname=s_title,
            name=n_title,
            patronymic=p_title,
            full_name=" ".join(filter(None, [s_title, n_title, p_title])),
            birthday=patient.get("Person_Birthday", ""),
            age=str(patient.get("Person_Age", "")),
            polis=_clean_html_field(patient.get("Polis_Num")),
            phone=_clean_html_field(patient.get("Person_Phone")),
            inn=patient.get("Person_Inn") or None,
            address_registration=patient.get("Person_PAddress") or None,
            address_residential=patient.get("Person_UAddress") or None,
            attach_lpu_name=patient.get("AttachLpu_Name"),
            lpu_region_name=patient.get("LpuRegion_Name"),
            person_id=str(patient.get("Person_id")),
            person_card_id=str(patient.get("PersonCard_id")) if patient.get("PersonCard_id") else None,
            server_id=str(patient.get("Server_id")),
            person_env_id=str(patient.get("PersonEvn_id")),
            attach_lpu_id=str(patient.get("AttachLpu_id"))
        )

        result_items.append(record)

    return result_items
