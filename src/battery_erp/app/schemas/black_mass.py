import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from battery_erp.app.models.enums import BlackMassStatus


class BlackMassComposition(BaseModel):
    co: float = Field(0, ge=0, le=100, description="Cobalt weight %")
    ni: float = Field(0, ge=0, le=100, description="Nickel weight %")
    mn: float = Field(0, ge=0, le=100, description="Manganese weight %")
    li: float = Field(0, ge=0, le=100, description="Lithium weight %")
    al: float = Field(0, ge=0, le=100, description="Aluminum weight %")
    fe: float = Field(0, ge=0, le=100, description="Iron weight %")
    cu: float = Field(0, ge=0, le=100, description="Copper weight %")
    f: float = Field(0, ge=0, le=100, description="Fluorine weight %")
    p: float = Field(0, ge=0, le=100, description="Phosphorus weight %")
    ti: float = Field(0, ge=0, le=100, description="Titanium weight %")
    zn: float = Field(0, ge=0, le=100, description="Zinc weight %")


class BlackMassCreate(BaseModel):
    batch_number: str
    lot_number: str = ""
    supplier_id: uuid.UUID | None = None
    gross_weight_kg: float = Field(ge=0)
    tare_weight_kg: float = Field(ge=0)
    storage_location: str = ""
    composition: BlackMassComposition = BlackMassComposition()
    notes: str = ""


class BlackMassUpdate(BaseModel):
    storage_location: str | None = None
    status: BlackMassStatus | None = None
    composition: BlackMassComposition | None = None
    notes: str | None = None


class BlackMassConsume(BaseModel):
    process_batch_id: uuid.UUID
    kg_consumed: float = Field(gt=0)


class BlackMassResponse(BaseModel):
    id: uuid.UUID
    batch_number: str
    lot_number: str
    supplier_id: uuid.UUID | None
    date_received: datetime
    gross_weight_kg: float
    tare_weight_kg: float
    net_weight_kg: float
    storage_location: str
    status: BlackMassStatus
    composition: dict
    notes: str

    model_config = {"from_attributes": True}
