"""Recipe calculation engine derived from GLMC 1.0 Operating SOP Data Entry sheet.

Reference values (500kg batch, 98% H2SO4, 34% H2O2):
  H2SO4: 1446.83 kg
  H2O2:  279.41 liters
"""

from dataclasses import dataclass

# SOP reference: 500kg batch with 98% H2SO4
_H2SO4_REF_KG_500 = 1446.83
_H2SO4_REF_BATCH_KG = 500.0
_H2SO4_REF_CONC = 98.0

# SOP reference: 500kg batch with 34% H2O2
_H2O2_REF_LITERS_500 = 279.41
_H2O2_REF_BATCH_KG = 500.0
_H2O2_REF_CONC = 34.0

# When using 50% H2SO4, the SOP says "Skip This Step" or uses 4582 kg
_H2SO4_50PCT_REF_KG_500 = 4582.0


@dataclass
class RecipeResult:
    batch_size_kg: float
    h2so4_concentration_pct: float
    h2o2_concentration_pct: float
    h2so4_kg: float
    h2o2_liters: float
    dm_water_liters: float
    h2so4_skip_step: bool
    dosing_steps: int


def calculate_recipe(
    batch_size_kg: float,
    h2so4_concentration_pct: float = 98.0,
    h2o2_concentration_pct: float = 34.0,
) -> RecipeResult:
    """Calculate chemical dosages for a GLMC batch.

    Scales linearly from the SOP reference values (500kg, 98% H2SO4, 34% H2O2).
    The SOP divides H2SO4 and H2O2 into 4 equal dosing steps for a 500kg batch.
    """
    scale = batch_size_kg / _H2SO4_REF_BATCH_KG

    if h2so4_concentration_pct <= 50.0:
        h2so4_kg = _H2SO4_50PCT_REF_KG_500 * scale
        skip_step = True
    else:
        h2so4_kg = _H2SO4_REF_KG_500 * scale * (_H2SO4_REF_CONC / h2so4_concentration_pct)
        skip_step = False

    h2o2_liters = _H2O2_REF_LITERS_500 * scale * (_H2O2_REF_CONC / h2o2_concentration_pct)

    # SOP: 3000L DM water for 500kg, scale proportionally
    dm_water_liters = 3000.0 * scale

    # V-001 has 4 main dosing rounds (Step 1.x through 4.x) for 500kg
    dosing_steps = 4

    return RecipeResult(
        batch_size_kg=batch_size_kg,
        h2so4_concentration_pct=h2so4_concentration_pct,
        h2o2_concentration_pct=h2o2_concentration_pct,
        h2so4_kg=round(h2so4_kg, 2),
        h2o2_liters=round(h2o2_liters, 2),
        dm_water_liters=round(dm_water_liters, 2),
        h2so4_skip_step=skip_step,
        dosing_steps=dosing_steps,
    )


def h2so4_per_dosing_step(recipe: RecipeResult) -> float:
    """H2SO4 per dosing step in kg. SOP: split total evenly across 4 steps."""
    if recipe.dosing_steps <= 0:
        return 0.0
    return round(recipe.h2so4_kg / recipe.dosing_steps, 2)


def h2o2_per_dosing_step(recipe: RecipeResult) -> float:
    """H2O2 per dosing step in liters. SOP: split total evenly across 4 steps."""
    if recipe.dosing_steps <= 0:
        return 0.0
    return round(recipe.h2o2_liters / recipe.dosing_steps, 2)
