from typing import Annotated, Any
from fastapi import APIRouter, Depends, Body

from app.core import check_api_key, get_gateway_service
from app.model import (
    PayTypeResponse,
)
from app.service import (
    GatewayService,
    fetch_pay_type_list,
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



