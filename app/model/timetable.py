from typing import Optional

from pydantic import BaseModel, Field
from datetime import datetime

from app.core import settings


class TimetableRequestFunc(BaseModel):
    # todo: пока без Person_id там посмотрим
    # person_id: str = Field(..., alias="Person_id", description="ID пациента")
    start_day: str = Field(
        default_factory=lambda: datetime.now().strftime("%d.%m.%Y"),
        alias="StartDay",
        description="Дата начала (по умолчанию — текущая дата)",
    )

    # Основные данные для запроса
    resource_id: str = Field(..., alias="Resource_id")
    usluga_complex_id: str = Field(..., alias="UslugaComplexMedService_id")

    # Технические поля
    arm_type_id: str = Field("647", alias="ARMType_id")
    panel_id: str = Field("TTRDirectionPanel", alias="PanelID")
    is_for_direction: str = Field("1", alias="IsForDirection")
    evn_direction_is_receive: str = Field("1", alias="EvnDirection_IsReceive")

    # За какое количество месяцев получить расписание
    # Для тестов в swagger передать 0.5, так при получении полного расписания swagger может свалится
    search_months: float = Field(
        default=settings.TIMETABLE_PERIOD_IN_MONTH,
        ge=0.1,
        description="На сколько месяцев вперед искать расписание. (0.5 для теста)",
    )

    model_config = {"populate_by_name": True}


class TimetableRequestLab(BaseModel):
    # todo: пока без Person_id там посмотрим
    # person_id: str = Field(..., alias="Person_id", description="ID пациента")

    start_day: str = Field(
        default_factory=lambda: datetime.now().strftime("%d.%m.%Y"),
        alias="StartDay",
        description="Дата начала",
    )

    # Основные данные для запроса
    med_service_id: str = Field(
        ...,
        alias="MedService_id",
        description="ID услуги (из списка пунктов забора)",
    )

    # Технические поля
    arm_type_id: str = Field("647", alias="ARMType_id")
    panel_id: str = Field("TTMSDirectionPanel", alias="PanelID")
    is_for_direction: str = Field("1", alias="IsForDirection")
    evn_direction_is_receive: str = Field("1", alias="EvnDirection_IsReceive")
    dir_type_code: str = Field("9", alias="DirType_Code")

    # За какое количество месяцев получить расписание
    # Для тестов в swagger передать 0.5, так при получении полного расписания swagger может свалится
    search_months: float = Field(
        default=settings.TIMETABLE_PERIOD_IN_MONTH,
        ge=0.1,
        description="На сколько месяцев вперед искать расписание. (0.5 для теста)",
    )

    model_config = {"populate_by_name": True}


class TimetableSlot(BaseModel):
    date: str
    day: str
    time: str
    status: str  # "free" или "busy"
    # slot_id приходит только если слот "free". Нужен для записи.
    slot_id: Optional[str] = None
    comment: Optional[str] = Field(
        None,
        description="Комментарий из тултипа (например: 'САХАР С НАГРУЗКОЙ')",
    )
    info: Optional[str] = Field(
        None, description="Доп. инфо (например: 'По направлению')"
    )
    # details приходит если слот "busy". Там HTML с данными о записи.
    details: Optional[str] = None


class TimetableResponse(BaseModel):
    status: str = "success"
    total_days: int
    total_slots: int
    # Ключ словаря — дата (например "21.01.2026"), значение — список слотов
    data: dict[str, list[TimetableSlot]]
