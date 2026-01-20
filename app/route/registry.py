from typing import Annotated
from fastapi import APIRouter, Depends, Body
import time
from bs4 import BeautifulSoup

from app.core import get_gateway_service, logger
from app.service import GatewayService
from app.model import PatientRequest, PatientFoundItem

router = APIRouter(prefix="/registry", tags=["registry"])


def _clean_html_field(raw_html: str | None) -> str | None:
    if not raw_html:
        return None
    text = BeautifulSoup(raw_html, "html.parser").get_text(strip=True)
    return text if text else None


@router.post(
    path="/patient",
    response_model=list[PatientFoundItem],
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
            ambulat_card_number = patient.get("PersonAmbulatCard_Num") or None,
            person_id=str(patient.get("Person_id")),
            person_card_id=str(patient.get("PersonCard_id")) if patient.get("PersonCard_id") else None,
            server_id=str(patient.get("Server_id")),
            person_env_id=str(patient.get("PersonEvn_id")),
            attach_lpu_id=str(patient.get("AttachLpu_id"))
        )

        result_items.append(record)

    return result_items