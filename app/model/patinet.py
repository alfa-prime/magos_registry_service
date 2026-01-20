from typing import Optional

from pydantic import BaseModel, Field, constr


# модель для запроса
class PatientRequest(BaseModel):
    last_name: str = Field(...)
    first_name: str = Field(...)
    middle_name: Optional[str] = Field(None)
    birthday: constr(pattern=r"\d{2}\.\d{2}\.\d{4}") = Field(...)


# модели для ответа
class PatientFoundItem(BaseModel):
    surname: str
    name: str
    patronymic: Optional[str] = None
    full_name: str
    birthday: str
    age: str
    polis: Optional[str] = None
    inn: Optional[str] = None
    phone: Optional[str] = None
    address_registration: Optional[str] = None  # Person_PAddress
    address_residential: Optional[str] = None  # Person_UAddress
    attach_lpu_name: Optional[str] = None
    lpu_region_name: Optional[str] = None

    ambulat_card_number: Optional[str] = None
    person_id: str
    person_card_id: Optional[str] = None
    server_id: Optional[str] = None
    person_env_id: Optional[str] = None  # PersonEvn_id
    attach_lpu_id: Optional[str] = None


class PatientSearchResponse(BaseModel):
    data: list[PatientFoundItem]
