"""Batch costing engine from GLMC 1.0 Operating SOP 'Commerical' sheet."""

from dataclasses import dataclass


@dataclass
class CostInput:
    black_mass_cost_per_mt: float = 0.0
    black_mass_kg_used: float = 0.0
    water_cost_per_liter: float = 0.0
    water_liters_used: float = 0.0
    naoh_cost_per_liter: float = 0.0
    naoh_liters_used: float = 0.0
    h2so4_cost_per_liter: float = 0.0
    h2so4_liters_used: float = 0.0
    h2o2_cost_per_liter: float = 0.0
    h2o2_liters_used: float = 0.0
    caoh2_cost_per_lb: float = 0.0
    caoh2_lbs_used: float = 0.0
    coso4_cost_per_lb: float = 0.0
    coso4_lbs_used: float = 0.0
    mnso4_cost_per_lb: float = 0.0
    mnso4_lbs_used: float = 0.0
    nh4oh_cost_per_liter: float = 0.0
    nh4oh_liters_used: float = 0.0
    na2co3_cost_per_lb: float = 0.0
    na2co3_lbs_used: float = 0.0
    utility_cost: float = 0.0
    labor_cost: float = 0.0


@dataclass
class CostBreakdown:
    black_mass_cost: float
    water_cost: float
    naoh_cost: float
    h2so4_cost: float
    h2o2_cost: float
    caoh2_cost: float
    coso4_cost: float
    mnso4_cost: float
    nh4oh_cost: float
    na2co3_cost: float
    total_chemical_cost: float
    utility_cost: float
    labor_cost: float
    total_batch_cost: float


def calculate_batch_cost(inputs: CostInput) -> CostBreakdown:
    """Roll up per-batch costs from chemical consumption and rates."""
    bm = inputs.black_mass_kg_used * (inputs.black_mass_cost_per_mt / 1000.0)
    water = inputs.water_liters_used * inputs.water_cost_per_liter
    naoh = inputs.naoh_liters_used * inputs.naoh_cost_per_liter
    h2so4 = inputs.h2so4_liters_used * inputs.h2so4_cost_per_liter
    h2o2 = inputs.h2o2_liters_used * inputs.h2o2_cost_per_liter
    caoh2 = inputs.caoh2_lbs_used * inputs.caoh2_cost_per_lb
    coso4 = inputs.coso4_lbs_used * inputs.coso4_cost_per_lb
    mnso4 = inputs.mnso4_lbs_used * inputs.mnso4_cost_per_lb
    nh4oh = inputs.nh4oh_liters_used * inputs.nh4oh_cost_per_liter
    na2co3 = inputs.na2co3_lbs_used * inputs.na2co3_cost_per_lb

    total_chem = bm + water + naoh + h2so4 + h2o2 + caoh2 + coso4 + mnso4 + nh4oh + na2co3
    total = total_chem + inputs.utility_cost + inputs.labor_cost

    return CostBreakdown(
        black_mass_cost=round(bm, 2),
        water_cost=round(water, 2),
        naoh_cost=round(naoh, 2),
        h2so4_cost=round(h2so4, 2),
        h2o2_cost=round(h2o2, 2),
        caoh2_cost=round(caoh2, 2),
        coso4_cost=round(coso4, 2),
        mnso4_cost=round(mnso4, 2),
        nh4oh_cost=round(nh4oh, 2),
        na2co3_cost=round(na2co3, 2),
        total_chemical_cost=round(total_chem, 2),
        utility_cost=round(inputs.utility_cost, 2),
        labor_cost=round(inputs.labor_cost, 2),
        total_batch_cost=round(total, 2),
    )


def cost_per_kg_product(
    total_batch_cost: float,
    product_weight_kg: float,
    allocation_pct: float = 100.0,
) -> float:
    """Calculate cost per kg for a specific product from the batch."""
    if product_weight_kg <= 0:
        return 0.0
    allocated = total_batch_cost * (allocation_pct / 100.0)
    return round(allocated / product_weight_kg, 2)


def calculate_yield(
    black_mass_kg: float,
    element_pct: float,
    product_weight_kg: float,
) -> float:
    """Metal recovery percentage: output / theoretical input."""
    input_kg = black_mass_kg * (element_pct / 100.0)
    if input_kg <= 0:
        return 0.0
    return round((product_weight_kg / input_kg) * 100.0, 2)
