import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from battery_erp.app.db.session import get_db
from battery_erp.app.models.domain import LabSample, NMCDosageCalculation
from battery_erp.app.models.enums import NMCDecision
from battery_erp.app.rules.nmc import calculate_nmc_dosage
from battery_erp.app.schemas.lab import (
    LabSampleCreate,
    LabSampleResponse,
    NMCCalculateRequest,
    NMCCalculateResponse,
)

router = APIRouter()


def _next_sample_number(db: Session) -> str:
    year = datetime.now().year
    result = db.execute(
        select(LabSample)
        .where(LabSample.sample_number.like(f"ICP-{year}-%"))
        .order_by(LabSample.sample_number.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    if last:
        seq = int(last.sample_number.split("-")[-1]) + 1
    else:
        seq = 1
    return f"ICP-{year}-{seq:04d}"


@router.post("/samples", response_model=LabSampleResponse, status_code=201)
def submit_sample(data: LabSampleCreate, db: Session = Depends(get_db)) -> LabSample:
    sample = LabSample(
        sample_number=_next_sample_number(db),
        process_batch_id=data.process_batch_id,
        vessel=data.vessel,
        sample_point=data.sample_point,
        collected_by_id=data.collected_by_id,
        ni_ppm=data.ni_ppm,
        mn_ppm=data.mn_ppm,
        co_ppm=data.co_ppm,
        li_ppm=data.li_ppm,
        ph=data.ph,
        temperature_c=data.temperature_c,
        solution_volume_liters=data.solution_volume_liters,
        notes=data.notes,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


@router.get("/samples", response_model=list[LabSampleResponse])
def list_samples(
    process_batch_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
) -> list[LabSample]:
    q = select(LabSample).order_by(LabSample.collected_at.desc())
    if process_batch_id:
        q = q.where(LabSample.process_batch_id == process_batch_id)
    return list(db.scalars(q).all())


@router.post("/nmc-calculate", response_model=NMCCalculateResponse)
def calculate_nmc(data: NMCCalculateRequest) -> NMCCalculateResponse:
    result = calculate_nmc_dosage(
        ni_ppm=data.ni_ppm,
        mn_ppm=data.mn_ppm,
        co_ppm=data.co_ppm,
        v003_volume_liters=data.v003_volume_liters,
        target_ni=data.target_ni,
        target_mn=data.target_mn,
        target_co=data.target_co,
        tolerance_pct=data.tolerance_pct,
    )
    return NMCCalculateResponse(
        decision=result.decision,
        target_ratio=result.target_ratio,
        actual_ratio=result.actual_ratio,
        coso4_7h2o_kg=result.coso4_7h2o_kg,
        coso4_di_water_liters=result.coso4_di_water_liters,
        mnso4_h2o_kg=result.mnso4_h2o_kg,
        mnso4_di_water_liters=result.mnso4_di_water_liters,
        nh4oh_liters=result.nh4oh_liters,
        naoh_liters=result.naoh_liters,
    )


@router.get("/samples/{sample_id}/dosage", response_model=NMCCalculateResponse)
def get_dosage_recommendation(
    sample_id: uuid.UUID,
    target_ni: int = 6,
    target_mn: int = 2,
    target_co: int = 2,
    tolerance_pct: float = 5.0,
    db: Session = Depends(get_db),
) -> NMCCalculateResponse:
    sample = db.get(LabSample, sample_id)
    if not sample:
        raise HTTPException(404, "Sample not found")
    if not all([sample.ni_ppm, sample.mn_ppm, sample.co_ppm]):
        raise HTTPException(400, "Sample missing ICP results (Ni, Mn, Co)")
    if sample.solution_volume_liters <= 0:
        raise HTTPException(400, "Sample missing solution volume")

    result = calculate_nmc_dosage(
        ni_ppm=float(sample.ni_ppm),
        mn_ppm=float(sample.mn_ppm),
        co_ppm=float(sample.co_ppm),
        v003_volume_liters=float(sample.solution_volume_liters),
        target_ni=target_ni,
        target_mn=target_mn,
        target_co=target_co,
        tolerance_pct=tolerance_pct,
    )

    # Persist the calculation
    calc = NMCDosageCalculation(
        lab_sample_id=sample_id,
        target_nmc_ratio=f"{target_ni}-{target_mn}-{target_co}",
        tolerance_pct=tolerance_pct,
        decision=NMCDecision(result.decision),
        coso4_7h2o_kg=result.coso4_7h2o_kg,
        coso4_di_water_liters=result.coso4_di_water_liters,
        mnso4_h2o_kg=result.mnso4_h2o_kg,
        mnso4_di_water_liters=result.mnso4_di_water_liters,
        nh4oh_liters=result.nh4oh_liters,
        naoh_liters=result.naoh_liters,
    )
    db.add(calc)
    db.commit()

    return NMCCalculateResponse(
        decision=result.decision,
        target_ratio=result.target_ratio,
        actual_ratio=result.actual_ratio,
        coso4_7h2o_kg=result.coso4_7h2o_kg,
        coso4_di_water_liters=result.coso4_di_water_liters,
        mnso4_h2o_kg=result.mnso4_h2o_kg,
        mnso4_di_water_liters=result.mnso4_di_water_liters,
        nh4oh_liters=result.nh4oh_liters,
        naoh_liters=result.naoh_liters,
    )
