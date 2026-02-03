from typing import Any

from app.model import LabComplexRequest
from app.service import GatewayService


async def fetch_collection_point_list(
    service: GatewayService, payload: LabComplexRequest
) -> list[dict[str, Any]] | dict[str, Any]:
    params = {
        "c": "MedService",
        "m": "loadList",
    }

    data = {
        "MedServiceType_SysNick": "pzm",
        "MedService_lid": payload.med_service_id,
        "UslugaComplex_id": payload.usluga_complex_id,
    }

    json = {"params": params, "data": data}
    return await service.request_json(json=json)
