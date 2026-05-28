import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from battery_erp.app.models.enums import RecipeStatus
from battery_erp.app.schemas.black_mass import BlackMassComposition


class RecipeCalculateRequest(BaseModel):
    composition: BlackMassComposition
    batch_size_kg: float = Field(ge=100, le=2000, description="500, 750, or 1000 kg typical")
    h2so4_concentration_pct: float = Field(default=98.0, ge=10, le=100)
    h2o2_concentration_pct: float = Field(default=34.0, ge=10, le=100)


class RecipeCalculateResponse(BaseModel):
    batch_size_kg: float
    h2so4_concentration_pct: float
    h2o2_concentration_pct: float
    h2so4_kg: float
    h2o2_liters: float
    dm_water_liters: float
    h2so4_skip_step: bool
    dosing_steps: int
    h2so4_per_step_kg: float
    h2o2_per_step_liters: float


class RecipeCreate(BaseModel):
    name: str
    batch_size_kg: float = Field(ge=100, le=2000)
    target_nmc_ratio: str = "6-2-2"
    h2so4_concentration_pct: float = 98.0
    h2o2_concentration_pct: float = 34.0
    naoh_concentration_pct: float = 25.0
    nh4oh_concentration_pct: float = 19.0
    dm_water_liters: float = 3000.0


class RecipeResponse(BaseModel):
    id: uuid.UUID
    name: str
    batch_size_kg: float
    target_nmc_ratio: str
    h2so4_concentration_pct: float
    h2o2_concentration_pct: float
    naoh_concentration_pct: float
    nh4oh_concentration_pct: float
    dm_water_liters: float
    h2so4_kg: float
    h2o2_liters: float
    version: int
    status: RecipeStatus
    approved_by_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
