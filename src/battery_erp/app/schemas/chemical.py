import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from battery_erp.app.models.enums import ChemicalUnit, ToteStatus


class ChemicalResponse(BaseModel):
    id: uuid.UUID
    name: str
    formula: str
    concentration_pct: float
    molecular_weight: float
    unit: ChemicalUnit
    unit_cost: float
    hazard_class: str
    min_stock: float
    max_stock: float
    current_stock: float = 0

    model_config = {"from_attributes": True}


class ToteCreate(BaseModel):
    chemical_id: uuid.UUID
    lot_number: str = ""
    capacity: float = Field(gt=0)
    current_level: float = Field(ge=0)
    unit: ChemicalUnit
    location: str = ""
    cam_lock_inspected: bool = False
    weather_protected: bool = False
    notes: str = ""


class ToteResponse(BaseModel):
    id: uuid.UUID
    chemical_id: uuid.UUID
    lot_number: str
    capacity: float
    current_level: float
    unit: ChemicalUnit
    location: str
    status: ToteStatus
    connected_to_vessel: str | None
    date_received: datetime
    cam_lock_inspected: bool
    weather_protected: bool
    notes: str

    model_config = {"from_attributes": True}


class ToteConnect(BaseModel):
    vessel: str = Field(description="e.g. V-001, V-002")


class ToteLevelUpdate(BaseModel):
    current_level: float = Field(ge=0)
