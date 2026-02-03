from typing import Any

from app.model import LabComplexRequest
from app.service import GatewayService


async def fetch_complex_service_list(
    service: GatewayService, payload: LabComplexRequest
) -> list[dict[str, Any]] | dict[str, Any]:
    params = {
        "c": "MedService",
        "m": "loadCompositionTree",
    }

    data = {
        "UslugaComplexMedService_id": payload.usluga_complex_med_service_id,
    }

    json = {"params": params, "data": data}
    return await service.request_json(json=json)
