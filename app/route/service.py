from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import check_api_key, get_gateway_service
from app.model import PayTypeResponse
from app.service import GatewayService

router = APIRouter(
    prefix="/service", tags=["Сервисные ручки"], dependencies=[Depends(check_api_key)]
)


@router.get(
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
