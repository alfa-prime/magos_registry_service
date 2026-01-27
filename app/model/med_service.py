from typing import Optional
from pydantic import BaseModel, Field


class ResearchListRequest(BaseModel):
    """ Модель запроса для получения списка исследований в службе """
    group_id: str = Field(..., description="ID группы услуг (MedService_id)")


class MedServiceListResponse(BaseModel):
    """ Модель для ответа на запрос справочника услуг (группы) """
    name: str = Field(validation_alias="MedService_Name")
    id: str = Field(validation_alias="MedService_id")


class ResearchListItemResponse(BaseModel):
    """ Модель для ответа на запрос списка услуг в группе """
    usluga_complex_name: Optional[str] = Field(None, validation_alias="UslugaComplex_Name")
    usluga_complex_code: Optional[str] = Field(None, validation_alias="UslugaComplex_Code")
    group_id: Optional[str] = Field(None, description="ID родительской группы")
    unique_key_id: Optional[str] = Field(None, validation_alias="UniqueKey_id")
    med_service_caption: Optional[str] = Field(None, validation_alias="MedService_Caption")
    med_service_name: Optional[str] = Field(None, validation_alias="MedService_Name")
    med_service_nick: Optional[str] = Field(None, validation_alias="MedService_Nick")
    med_service_id: Optional[str] = Field(None, validation_alias="MedService_id")
    med_service_type_id: Optional[str] = Field(None, validation_alias="MedServiceType_id")
    med_service_type_sys_nick: Optional[str] = Field(None, validation_alias="MedServiceType_SysNick")
    usluga_complex_id: Optional[str] = Field(None, validation_alias="UslugaComplex_id")
    usluga_complex_med_service_id: Optional[str] = Field(None, validation_alias="UslugaComplexMedService_id")
    usluga_complex_resource_id: Optional[str] = Field(None, validation_alias="UslugaComplexResource_id")
    resource_id: Optional[str] = Field(None, validation_alias="Resource_id")
    lpu_unit_id: Optional[str] = Field(None, validation_alias="LpuUnit_id")
    lpu_section_id: Optional[str] = Field(None, validation_alias="LpuSection_id")
    lpu_section_profile_id: Optional[str] = Field(None, validation_alias="LpuSectionProfile_id")