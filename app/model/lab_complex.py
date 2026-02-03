from typing import Optional

from pydantic import BaseModel, Field


class LabComplexRequest(BaseModel):
    med_service_id: str = Field(
        ..., description="ID медицинской службы (MedService_id)"
    )
    usluga_complex_id: str = Field(
        ..., description="ID комплексной услуги (UslugaComplex_id)"
    )
    usluga_complex_med_service_id: str = Field(
        ..., description="ID связки услуги и службы (UslugaComplexMedService_id)"
    )

    model_config = {"extra": "ignore"}


class CollectionPointItem(BaseModel):
    med_service_id: Optional[str] = Field(None, validation_alias="MedService_id")
    server_id: Optional[str] = Field(None, validation_alias="Server_id")
    med_service_name: Optional[str] = Field(None, validation_alias="MedService_Name")
    med_service_type_id: Optional[str] = Field(
        None, validation_alias="MedServiceType_id"
    )
    lpu_id_nick: Optional[str] = Field(None, validation_alias="Lpu_id_Nick")
    lpu_building_id_name: Optional[str] = Field(
        None, validation_alias="LpuBuilding_id_Name"
    )
    address: Optional[str] = Field(None, validation_alias="Address_Address")

    model_config = {"populate_by_name": True}


class ComplexServiceItem(BaseModel):
    usluga_complex_med_service_id: Optional[str] = Field(
        None, validation_alias="UslugaComplexMedService_id"
    )
    usluga_complex_pid: Optional[str] = Field(
        None, validation_alias="UslugaComplex_pid"
    )
    usluga_complex_id: Optional[str] = Field(None, validation_alias="id")
    text: Optional[str] = Field(None, validation_alias="text")

    model_config = {"populate_by_name": True}


class LabComplexResponse(BaseModel):
    collection_points: list[CollectionPointItem]
    services_in_service: list[ComplexServiceItem]
