import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from battery_erp.app.db.session import get_db
from battery_erp.app.models.domain import Recipe
from battery_erp.app.models.enums import RecipeStatus
from battery_erp.app.rules.recipe import calculate_recipe, h2o2_per_dosing_step, h2so4_per_dosing_step
from battery_erp.app.schemas.recipe import (
    RecipeCalculateRequest,
    RecipeCalculateResponse,
    RecipeCreate,
    RecipeResponse,
)

router = APIRouter()


@router.post("/calculate", response_model=RecipeCalculateResponse)
def calculate_dosages(data: RecipeCalculateRequest) -> RecipeCalculateResponse:
    result = calculate_recipe(
        batch_size_kg=data.batch_size_kg,
        h2so4_concentration_pct=data.h2so4_concentration_pct,
        h2o2_concentration_pct=data.h2o2_concentration_pct,
    )
    return RecipeCalculateResponse(
        batch_size_kg=result.batch_size_kg,
        h2so4_concentration_pct=result.h2so4_concentration_pct,
        h2o2_concentration_pct=result.h2o2_concentration_pct,
        h2so4_kg=result.h2so4_kg,
        h2o2_liters=result.h2o2_liters,
        dm_water_liters=result.dm_water_liters,
        h2so4_skip_step=result.h2so4_skip_step,
        dosing_steps=result.dosing_steps,
        h2so4_per_step_kg=h2so4_per_dosing_step(result),
        h2o2_per_step_liters=h2o2_per_dosing_step(result),
    )


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db)) -> Recipe:
    calc = calculate_recipe(
        batch_size_kg=data.batch_size_kg,
        h2so4_concentration_pct=data.h2so4_concentration_pct,
        h2o2_concentration_pct=data.h2o2_concentration_pct,
    )
    recipe = Recipe(
        name=data.name,
        batch_size_kg=data.batch_size_kg,
        target_nmc_ratio=data.target_nmc_ratio,
        h2so4_concentration_pct=data.h2so4_concentration_pct,
        h2o2_concentration_pct=data.h2o2_concentration_pct,
        naoh_concentration_pct=data.naoh_concentration_pct,
        nh4oh_concentration_pct=data.nh4oh_concentration_pct,
        dm_water_liters=data.dm_water_liters,
        h2so4_kg=calc.h2so4_kg,
        h2o2_liters=calc.h2o2_liters,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("", response_model=list[RecipeResponse])
def list_recipes(
    status: RecipeStatus | None = None,
    db: Session = Depends(get_db),
) -> list[Recipe]:
    q = select(Recipe).order_by(Recipe.created_at.desc())
    if status:
        q = q.where(Recipe.status == status)
    return list(db.scalars(q).all())


@router.post("/{recipe_id}/approve", response_model=RecipeResponse)
def approve_recipe(
    recipe_id: uuid.UUID,
    approved_by_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(404, "Recipe not found")
    recipe.status = RecipeStatus.APPROVED
    recipe.approved_by_id = approved_by_id
    db.commit()
    db.refresh(recipe)
    return recipe
