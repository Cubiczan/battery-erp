import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from battery_erp.app.models.enums import BatchStatus, StepStatus, ValveState, Vessel


class ProcessBatchCreate(BaseModel):
    recipe_id: uuid.UUID
    black_mass_batch_id: uuid.UUID
    black_mass_weight_kg: float = Field(gt=0)
    shift_date: date
    plant_manager_id: uuid.UUID | None = None
    operator_id: uuid.UUID | None = None
    forklift_operator_id: uuid.UUID | None = None
    notes: str = ""


class ProcessBatchResponse(BaseModel):
    id: uuid.UUID
    batch_number: str
    recipe_id: uuid.UUID
    black_mass_batch_id: uuid.UUID
    black_mass_weight_kg: float
    status: BatchStatus
    shift_date: date
    start_time: datetime | None
    end_time: datetime | None
    jsa_completed: bool
    ppe_verified: bool
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StepUpdate(BaseModel):
    status: StepStatus | None = None
    recorded_value: str | None = None
    notes: str | None = None


class StepResponse(BaseModel):
    id: uuid.UUID
    process_batch_id: uuid.UUID
    vessel: Vessel
    step_number: int
    description: str
    responsible_role: str
    status: StepStatus
    started_at: datetime | None
    completed_at: datetime | None
    recorded_value: str | None
    estimated_duration_min: int
    notes: str

    model_config = {"from_attributes": True}


class ValveVerifyRequest(BaseModel):
    valve_id: str
    actual_state: ValveState
    verified_by_id: uuid.UUID


class BatchFlagRequest(BaseModel):
    description: str
    severity: str = "warning"
