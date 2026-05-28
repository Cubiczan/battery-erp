import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from battery_erp.app.models.enums import Vessel


class LabSampleCreate(BaseModel):
    process_batch_id: uuid.UUID
    vessel: Vessel
    sample_point: str = ""
    collected_by_id: uuid.UUID | None = None
    ni_ppm: float | None = None
    mn_ppm: float | None = None
    co_ppm: float | None = None
    li_ppm: float | None = None
    ph: float | None = None
    temperature_c: float | None = None
    solution_volume_liters: float = Field(ge=0)
    notes: str = ""


class LabSampleResponse(BaseModel):
    id: uuid.UUID
    sample_number: str
    process_batch_id: uuid.UUID
    vessel: Vessel
    sample_point: str
    collected_at: datetime
    ni_ppm: float | None
    mn_ppm: float | None
    co_ppm: float | None
    li_ppm: float | None
    ph: float | None
    temperature_c: float | None
    solution_volume_liters: float
    notes: str

    model_config = {"from_attributes": True}


class NMCCalculateRequest(BaseModel):
    ni_ppm: float = Field(gt=0)
    mn_ppm: float = Field(gt=0)
    co_ppm: float = Field(gt=0)
    v003_volume_liters: float = Field(gt=0)
    target_ni: int = Field(default=6, ge=1)
    target_mn: int = Field(default=2, ge=1)
    target_co: int = Field(default=2, ge=1)
    tolerance_pct: float = Field(default=5.0, ge=0, le=50)


class NMCCalculateResponse(BaseModel):
    decision: str
    target_ratio: tuple[int, int, int]
    actual_ratio: tuple[float, float, float]
    coso4_7h2o_kg: float
    coso4_di_water_liters: float
    mnso4_h2o_kg: float
    mnso4_di_water_liters: float
    nh4oh_liters: float
    naoh_liters: float
