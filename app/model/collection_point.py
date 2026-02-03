from typing import Optional
from pydantic import BaseModel, Field


class CollectionPointRequest(BaseModel):
    med_service_lid: str = Field(..., alias="MedService_lid")
    usluga_complex_id: str = Field(..., alias="UslugaComplex_id")

    model_config = {"populate_by_name": True}


class CollectionPointListItemResponse(BaseModel):
    """Модель для ответа на запрос списка услуг в группе"""

    med_service_id: Optional[str] = Field(
        None, validation_alias="MedService_id"
    )
    server_id: Optional[str] = Field(None, validation_alias="Server_id")
    med_service_name: Optional[str] = Field(
        None, validation_alias="MedService_Name"
    )
    med_service_type_id: Optional[str] = Field(
        None, validation_alias="MedServiceType_id"
    )
    lpu_id_nick: Optional[str] = Field(
        None, validation_alias="Lpu_id_Nick"
    )
    lpu_building_id_name: Optional[str] = Field(
        None, validation_alias="LpuBuilding_id_Name"
    )
    address: Optional[str] = Field(
        None, validation_alias="Address_Address"
    )

