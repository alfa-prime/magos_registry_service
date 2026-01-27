from app.model import ResearchListRequest
from app.service import GatewayService


async def fetch_research_list(service: GatewayService, payload: ResearchListRequest):
    json = {
        "params": {
            "c": "Reg",
            "m": "getDirectionMedServiceList"
        },
        "data": {
            "MedService_id": payload.group_id,
            "object": "MedService",
            "start": "0",
            "limit": "100",
            "Filter_Lpu_Nick": "ФГБУЗ ММЦ им. Н.И. Пирогова ФМБА России",
            "Filter_includeDopProfiles": "0",
            "ARMType": "regpol6",
            "FormName": "swDirectionMasterWindow",
            "DirType_Code": "9",
            "DirType_id": "10",
            "LpuUnitLevel": "1",
            "ListForDirection": "1",
            "isAutoAPLCovid": "0",
            "isSecondRead": "false",
            "isOnlyPolka": "0",
            "groupByMedService": "1",
        }
    }
    response = await service.request_json(json=json)
    data = response if isinstance(response, list) else response.get("data", [])

    for item in data:
        item["group_id"] = payload.group_id

    data = sorted(
        data,
        key=lambda x: x.get("UslugaComplex_Name") or ""
    )

    return data
