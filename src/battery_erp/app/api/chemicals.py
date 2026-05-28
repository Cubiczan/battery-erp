import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from battery_erp.app.db.session import get_db
from battery_erp.app.models.domain import Chemical, ChemicalTote
from battery_erp.app.models.enums import ToteStatus
from battery_erp.app.rules.inventory import calculate_tote_stock, check_chemical_reorder
from battery_erp.app.schemas.chemical import (
    ChemicalResponse,
    ToteConnect,
    ToteCreate,
    ToteLevelUpdate,
    ToteResponse,
)

router = APIRouter()


@router.get("", response_model=list[ChemicalResponse])
def list_chemicals(db: Session = Depends(get_db)) -> list[dict]:
    chemicals = list(db.scalars(select(Chemical).order_by(Chemical.name)).all())
    results = []
    for chem in chemicals:
        totes = list(
            db.scalars(select(ChemicalTote).where(ChemicalTote.chemical_id == chem.id)).all()
        )
        stock = calculate_tote_stock(
            [{"current_level": t.current_level, "status": t.status.value} for t in totes]
        )
        results.append({**ChemicalResponse.model_validate(chem).model_dump(), "current_stock": stock})
    return results


@router.post("/totes", response_model=ToteResponse, status_code=201)
def create_tote(data: ToteCreate, db: Session = Depends(get_db)) -> ChemicalTote:
    chem = db.get(Chemical, data.chemical_id)
    if not chem:
        raise HTTPException(404, "Chemical not found")

    tote = ChemicalTote(
        chemical_id=data.chemical_id,
        lot_number=data.lot_number,
        capacity=data.capacity,
        current_level=data.current_level,
        unit=data.unit,
        location=data.location,
        cam_lock_inspected=data.cam_lock_inspected,
        weather_protected=data.weather_protected,
        notes=data.notes,
    )
    db.add(tote)
    db.commit()
    db.refresh(tote)
    return tote


@router.patch("/totes/{tote_id}/connect", response_model=ToteResponse)
def connect_tote(
    tote_id: uuid.UUID,
    data: ToteConnect,
    db: Session = Depends(get_db),
) -> ChemicalTote:
    tote = db.get(ChemicalTote, tote_id)
    if not tote:
        raise HTTPException(404, "Tote not found")
    tote.connected_to_vessel = data.vessel
    tote.status = ToteStatus.CONNECTED
    db.commit()
    db.refresh(tote)
    return tote


@router.patch("/totes/{tote_id}/level", response_model=ToteResponse)
def update_tote_level(
    tote_id: uuid.UUID,
    data: ToteLevelUpdate,
    db: Session = Depends(get_db),
) -> ChemicalTote:
    tote = db.get(ChemicalTote, tote_id)
    if not tote:
        raise HTTPException(404, "Tote not found")
    tote.current_level = data.current_level
    if tote.current_level <= 0:
        tote.status = ToteStatus.EMPTY
    db.commit()
    db.refresh(tote)
    return tote


@router.get("/reorder-alerts")
def get_reorder_alerts(db: Session = Depends(get_db)) -> list[dict]:
    chemicals = list(db.scalars(select(Chemical)).all())
    alerts = []
    for chem in chemicals:
        totes = list(
            db.scalars(select(ChemicalTote).where(ChemicalTote.chemical_id == chem.id)).all()
        )
        stock = calculate_tote_stock(
            [{"current_level": t.current_level, "status": t.status.value} for t in totes]
        )
        alert = check_chemical_reorder(
            chem.name, chem.formula, stock, float(chem.min_stock), float(chem.max_stock)
        )
        if alert:
            alerts.append({
                "chemical_name": alert.chemical_name,
                "formula": alert.formula,
                "current_stock": alert.current_stock,
                "min_stock": alert.min_stock,
                "suggested_order_qty": alert.suggested_order_qty,
                "urgency": alert.urgency,
            })
    return alerts
