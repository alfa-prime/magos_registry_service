from pydantic import BaseModel, Field
from datetime import datetime


class TimetableRequest(BaseModel):
    # person_id: str = Field(..., alias="Person_id", description="ID пациента")
    start_day: str = Field(
        default_factory=lambda: datetime.now().strftime("%d.%m.%Y"),
        alias="StartDay",
        description="Дата начала (по умолчанию — текущая дата)"
    )
    resource_id: str = Field(..., alias="Resource_id")
    usluga_complex_id: str = Field(..., alias="UslugaComplexMedService_id")
    arm_type_id: str = Field("647", alias="ARMType_id")
    panel_id: str = Field("TTRDirectionPanel", alias="PanelID")
    is_for_direction: str = Field("1", alias="IsForDirection")
    evn_direction_is_receive: str = Field("1", alias="EvnDirection_IsReceive")

    model_config = {
        "populate_by_name": True
    }
