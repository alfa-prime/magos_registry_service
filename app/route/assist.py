from typing import Annotated, Any
from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import PayTypeResponse, CollectionPointRequest, CollectionPointListItemResponse
from app.service import (
    GatewayService,
    fetch_pay_type_list,
    fetch_collection_point_list,
)

router = APIRouter(
    prefix="/assist",
    tags=["Вспомогательные запросы"],
    dependencies=[Depends(check_api_key)],
)


@router.post(
    path="/pay_type",
    response_model=list[PayTypeResponse],
    summary="Типы оплаты",
    description="Справочник типов оплаты. Возвращает name + id",
)
async def get_pay_type_list(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
) -> list[dict[str, Any]] | dict[str, Any]:
    return await fetch_pay_type_list(gateway_service)


@router.post(
    path="/collection_point",
    response_model=list[CollectionPointListItemResponse],
    summary="Пункты забора биоматериала",
    description="Справочник пунктов забора биоматериала",
)
async def get_collection_point_list(
    gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
    payload: CollectionPointRequest = Body(
        ...,
        openapi_examples={
            "Биохимия ММЦ": {
                "summary": "Биохимия ММЦ - Анализ крови биохимический общетерапевтический",
                "value": {
                    "MedService_lid": "3010101000006800",
                    "UslugaComplex_id": "206894",
                },
            },
        },
    ),
) -> list[dict[str, Any]] | dict[str, Any]:
    return await fetch_collection_point_list(gateway_service, payload)
