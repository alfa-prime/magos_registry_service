from pydantic import BaseModel, Field


class PayTypeResponse(BaseModel):
    name: str = Field(validation_alias="paytype_name")
    id: int = Field(validation_alias="paytype_id")
