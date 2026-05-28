import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from battery_erp.app.db.session import get_db
from battery_erp.app.models.domain import BlackMassBatch
from battery_erp.app.models.enums import BlackMassStatus
from battery_erp.app.schemas.black_mass import (
    BlackMassConsume,
    BlackMassCreate,
    BlackMassResponse,
    BlackMassUpdate,
)

router = APIRouter()


def _next_batch_number(db: Session) -> str:
    year = datetime.now().year
    result = db.execute(
        select(BlackMassBatch)
        .where(BlackMassBatch.batch_number.like(f"BM-{year}-%"))
        .order_by(BlackMassBatch.batch_number.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    if last:
        seq = int(last.batch_number.split("-")[-1]) + 1
    else:
        seq = 1
    return f"BM-{year}-{seq:04d}"


@router.post("", response_model=BlackMassResponse, status_code=201)
def create_black_mass(data: BlackMassCreate, db: Session = Depends(get_db)) -> BlackMassBatch:
    net = data.gross_weight_kg - data.tare_weight_kg
    batch = BlackMassBatch(
        batch_number=data.batch_number or _next_batch_number(db),
        lot_number=data.lot_number,
        supplier_id=data.supplier_id,
        gross_weight_kg=data.gross_weight_kg,
        tare_weight_kg=data.tare_weight_kg,
        net_weight_kg=max(net, 0),
        storage_location=data.storage_location,
        status=BlackMassStatus.RECEIVED,
        composition=data.composition.model_dump(),
        notes=data.notes,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("", response_model=list[BlackMassResponse])
def list_black_mass(
    status: BlackMassStatus | None = None,
    db: Session = Depends(get_db),
) -> list[BlackMassBatch]:
    q = select(BlackMassBatch).order_by(BlackMassBatch.date_received.desc())
    if status:
        q = q.where(BlackMassBatch.status == status)
    return list(db.scalars(q).all())


@router.get("/{batch_id}", response_model=BlackMassResponse)
def get_black_mass(batch_id: uuid.UUID, db: Session = Depends(get_db)) -> BlackMassBatch:
    batch = db.get(BlackMassBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Black mass batch not found")
    return batch


@router.put("/{batch_id}", response_model=BlackMassResponse)
def update_black_mass(
    batch_id: uuid.UUID,
    data: BlackMassUpdate,
    db: Session = Depends(get_db),
) -> BlackMassBatch:
    batch = db.get(BlackMassBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Black mass batch not found")

    if data.storage_location is not None:
        batch.storage_location = data.storage_location
    if data.status is not None:
        batch.status = data.status
    if data.composition is not None:
        batch.composition = data.composition.model_dump()
    if data.notes is not None:
        batch.notes = data.notes

    db.commit()
    db.refresh(batch)
    return batch


@router.patch("/{batch_id}/consume", response_model=BlackMassResponse)
def consume_black_mass(
    batch_id: uuid.UUID,
    data: BlackMassConsume,
    db: Session = Depends(get_db),
) -> BlackMassBatch:
    batch = db.get(BlackMassBatch, batch_id)
    if not batch:
        raise HTTPException(404, "Black mass batch not found")
    if batch.net_weight_kg < data.kg_consumed:
        raise HTTPException(400, "Insufficient black mass in batch")

    batch.net_weight_kg -= data.kg_consumed
    batch.status = (
        BlackMassStatus.DEPLETED if batch.net_weight_kg <= 0 else BlackMassStatus.IN_PROCESS
    )
    db.commit()
    db.refresh(batch)
    return batch
