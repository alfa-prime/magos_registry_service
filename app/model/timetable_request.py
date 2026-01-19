from pydantic import BaseModel, Field


# ВНИМАНИЕ! в данный момент модель заточена для получения расписания маммографии
class TimetableRequest(BaseModel):
    person_id: str = Field(..., alias="Person_id", description="ID пациента")
    start_day: str = Field(..., alias="StartDay", description="Дата начала (ДД.ММ.ГГГГ)")

    resource_id: str = Field("3010101000001297", alias="Resource_id")
    usluga_complex_id: str = Field("3010101000045588", alias="UslugaComplexMedService_id")
    arm_type_id: str = Field("647", alias="ARMType_id")
    panel_id: str = Field("TTRDirectionPanel", alias="PanelID")
    is_for_direction: str = Field("1", alias="IsForDirection")
    evn_direction_is_receive: str = Field("1", alias="EvnDirection_IsReceive")

    model_config = {
        "populate_by_name": True
    }
