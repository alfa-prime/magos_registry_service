# Модель запроса к шлюзу API

from typing import Any, Dict
from pydantic import BaseModel, Field


class RequestParams(BaseModel):
    c: str = Field(..., description="Класс")
    m: str = Field(..., description="Метод")


class GatewayRequest(BaseModel):
    path: str = Field(default="/", description="Путь (по умолчанию корень)")
    method: str = Field(
        default="POST", description="Метод (по умолчанию POST)"
    )

    params: RequestParams
    data: Dict[str, Any]
