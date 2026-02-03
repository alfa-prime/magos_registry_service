from typing import Optional
from pydantic import BaseModel, Field


class ResearchGroupRequest(BaseModel):
    med_service_id: str = Field(..., alias="MedService_id")
    resource_id: Optional[str] = Field("", alias="Resource_id")

    model_config = {"populate_by_name": True}
