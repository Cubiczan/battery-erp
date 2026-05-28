import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from battery_erp.app.db.session import get_db
from battery_erp.app.models.domain import ProcessBatch, ProcessStep
from battery_erp.app.models.enums import BatchStatus, StepStatus
from battery_erp.app.schemas.process import (
    ProcessBatchCreate,
    ProcessBatchResponse,
    StepResponse,
    StepUpdate,
)

router = APIRouter()


def _next_batch_number(db: Session) -> str:
    year = datetime.now().year
    result = db.execute(
        select(ProcessBatch)
        .where(ProcessBatch.batch_number.like(f"GLMC-{year}-%"))
        .order_by(ProcessBatch.batch_number.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    if last:
        seq = int(last.batch_number.split("-")[-1]) + 1
    else:
        seq = 1
    return f"GLMC-{year}-{seq:04d}"


@router.post("", response_model=ProcessBatchResponse, status_code=201)
def create_batch(data: ProcessBatchCreate, db: Session = Depends(get_db)) -> ProcessBatch:
    batch = ProcessBatch(
        batch_number=_next_batch_number(db),
        recipe_id=data.recipe_id,
        black_mass_batch_id=data.black_mass_batch_id,
        black_mass_weight_kg=data.black_mass_weight_kg,
        shift_date=data.shift_date,
        plant_manager_id=data.plant_manager_id,
        operator_id=data.operator_id,
        forklift_operator_id=data.forklift_operator_id,
        notes=data.notes,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("", response_model=list[ProcessBatchResponse])
def list_batches(
    status: BatchStatus | None = None,
    db: Session = Depends(get_db),
) -> list[ProcessBatch]:
    q = select(ProcessBatch).order_by(ProcessBatch.created_at.desc())
    if status:
        q = q.where(ProcessBatch.status == status)
    return list(db.scalars(q).all())


@router.get("/{batch_id}", response_model=ProcessBatchResponse)
def get_batch(batch_id: uuid.UUID, db: Session = Depends(get_db)) -> ProcessBatch:
    batch = db.get(ProcessBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Process batch not found")
    return batch


@router.get("/{batch_id}/steps", response_model=list[StepResponse])
def list_steps(batch_id: uuid.UUID, db: Session = Depends(get_db)) -> list[ProcessStep]:
    return list(
        db.scalars(
            select(ProcessStep)
            .where(ProcessStep.process_batch_id == batch_id)
            .order_by(ProcessStep.step_number)
        ).all()
    )


@router.patch("/{batch_id}/steps/{step_id}", response_model=StepResponse)
def update_step(
    batch_id: uuid.UUID,
    step_id: uuid.UUID,
    data: StepUpdate,
    db: Session = Depends(get_db),
) -> ProcessStep:
    step = db.get(ProcessStep, step_id)
    if not step or step.process_batch_id != batch_id:
        raise HTTPException(404, "Step not found")

    # Enforce sequential completion
    if data.status == StepStatus.COMPLETED:
        prev = db.scalars(
            select(ProcessStep)
            .where(
                ProcessStep.process_batch_id == batch_id,
                ProcessStep.step_number < step.step_number,
                ProcessStep.status.not_in([StepStatus.COMPLETED, StepStatus.SKIPPED]),
            )
        ).first()
        if prev:
            raise HTTPException(
                400, f"Step {prev.step_number} must be completed first"
            )
        step.completed_at = datetime.now()

    if data.status == StepStatus.IN_PROGRESS and step.started_at is None:
        step.started_at = datetime.now()

    if data.status is not None:
        step.status = data.status
    if data.recorded_value is not None:
        step.recorded_value = data.recorded_value
    if data.notes is not None:
        step.notes = data.notes

    db.commit()
    db.refresh(step)
    return step
