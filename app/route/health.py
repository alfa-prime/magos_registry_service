from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.core import check_api_key, get_gateway_service, settings
from app.service import GatewayService
from app.model import GatewayRequest
from app.core.decorators import route_handler

router = APIRouter(
    prefix="/health",
    tags=["Проверка здоровья"],
    dependencies=[Depends(check_api_key)],
)


@router.get(
    path="/ping",
    summary="Стандартная проверка работоспособности",
    description="Возвращает 'pong', если сервис запущен и отвечает на запросы.",
)
@route_handler(debug=settings.DEBUG_ROUTE)
async def check():
    return {"ping": "pong"}


@router.post("/check-json")
@route_handler(debug=settings.DEBUG_ROUTE)
async def check_gateway_json(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
        request: Request
):
    response = await gateway_service.request_json(
        json={"params": {"c": "Common", "m": "getCurrentDateTime"}}
    )
    return response


@router.post("/test-html-resource", response_class=HTMLResponse)
async def get_timetable_html(
        gateway_service: Annotated[GatewayService, Depends(get_gateway_service)],
):
    payload_data = {
        "params": {"c": "TimetableResource", "m": "getTimetableResource"},
        "data": {
            "IsForDirection": "1",
            "StartDay": "12.01.2026",
            "Resource_id": "3010101000001297",
            "UslugaComplexMedService_id": "3010101000045588",
            "EvnDirection_IsReceive": "1",
            "Person_id": "3010101001541772",
            "ARMType_id": "647",
            "PanelID": "TTRDirectionPanel",
        },
    }

    request_model = GatewayRequest.model_validate(payload_data)
    content = await gateway_service.request_html(json=request_model.model_dump())

    return HTMLResponse(content=content)
