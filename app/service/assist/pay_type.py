from typing import Any

from app.service import GatewayService
from app.core import logger


async def fetch_pay_type_list(
    gateway_service: GatewayService,
) -> list[dict[str, Any]] | dict[str, Any]:
    params = {"c": "MongoDBWork", "m": "getData", "object": "PayType"}
    data = {"object": "PayType"}

    response = await gateway_service.request_json(json={"params": params, "data": data})
    logger.debug(response[:300])
    return response
