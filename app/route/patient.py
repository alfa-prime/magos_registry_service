from typing import Annotated
from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import PatientFoundItem, PatientRequest
from app.service import GatewayService, fetch_patients_list

router = APIRouter(
    prefix="/patient",
    tags=["Поиск пациентов"],
    dependencies=[Depends(check_api_key)],
)


@router.post(
    path="/search_patient",
    response_model=list[PatientFoundItem],
    summary="Поиск пациента в ЕВМИАС по ФИО и ДР",
    description="Возвращает список найденных пациентов",
)
async def get_patients_list(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: PatientRequest = Body(
        ...,
        examples=[
            {
                "last_name": "жулидова",
                "first_name": "елена",
                "middle_name": "вячеславовна",
                "birthday": "08.08.1972",
            }
        ],
    ),
):
    return await fetch_patients_list(gateway_service, payload)
