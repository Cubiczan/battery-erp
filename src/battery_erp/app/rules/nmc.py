"""NMC ratio engine derived from the GLMC 1.0 Operating SOP 'NMC' sheet.

Converts ICP ppm results to molar ratios, compares to target NMC ratio,
and calculates CoSO4/MnSO4 additions needed to reach the target.

Reference molecular weights (from SOP Appendix D):
  Ni: 58.693, Mn: 54.938, Co: 58.933
  CoSO4*7H2O: 281.103, MnSO4*H2O: 169.02
"""

from dataclasses import dataclass

MW_NI = 58.693
MW_MN = 54.938
MW_CO = 58.933
MW_COSO4_7H2O = 281.103
MW_MNSO4_H2O = 169.02

# Dissolution ratios from SOP NMC sheet
COSO4_WATER_RATIO = 1.2  # kg DI water per kg CoSO4
MNSO4_WATER_RATIO = 2.6  # kg DI water per kg MnSO4

# Ammonia and NaOH dosing: from SOP NMC sheet calculated values
# 467.98 L/m3 of 19% ammonia per mol/L total metal
# 210.03 L/m3 of 25% NaOH per mol/L total metal
NH4OH_L_PER_M3_PER_MOL = 467.98
NAOH_L_PER_M3_PER_MOL = 210.03


@dataclass
class NMCRatioResult:
    ni_mol_per_l: float
    mn_mol_per_l: float
    co_mol_per_l: float
    actual_ratio_ni: float
    actual_ratio_mn: float
    actual_ratio_co: float
    total_metal_mol_per_l: float


@dataclass
class NMCDosageResult:
    decision: str  # "continue_dosing", "skip_step", "within_tolerance"
    target_ratio: tuple[int, int, int]
    actual_ratio: tuple[float, float, float]
    coso4_7h2o_kg: float
    coso4_di_water_liters: float
    mnso4_h2o_kg: float
    mnso4_di_water_liters: float
    nh4oh_liters: float
    naoh_liters: float


def ppm_to_mol_per_l(ppm: float, molecular_weight: float) -> float:
    """Convert ppm (mg/L) to mol/L. ICP results in ppm = mg/L for solutions."""
    g_per_l = ppm / 1000.0
    return g_per_l / molecular_weight


def calculate_molar_ratios(ni_ppm: float, mn_ppm: float, co_ppm: float) -> NMCRatioResult:
    """Calculate molar concentrations and NMC ratio from ICP results."""
    ni_mol = ppm_to_mol_per_l(ni_ppm, MW_NI)
    mn_mol = ppm_to_mol_per_l(mn_ppm, MW_MN)
    co_mol = ppm_to_mol_per_l(co_ppm, MW_CO)
    total = ni_mol + mn_mol + co_mol

    # Normalize to smallest component
    min_mol = min(ni_mol, mn_mol, co_mol)
    if min_mol > 0:
        ratio_ni = ni_mol / min_mol
        ratio_mn = mn_mol / min_mol
        ratio_co = co_mol / min_mol
    else:
        ratio_ni = ratio_mn = ratio_co = 0.0

    return NMCRatioResult(
        ni_mol_per_l=round(ni_mol, 8),
        mn_mol_per_l=round(mn_mol, 8),
        co_mol_per_l=round(co_mol, 8),
        actual_ratio_ni=round(ratio_ni, 4),
        actual_ratio_mn=round(ratio_mn, 4),
        actual_ratio_co=round(ratio_co, 4),
        total_metal_mol_per_l=round(total, 8),
    )


def calculate_nmc_dosage(
    ni_ppm: float,
    mn_ppm: float,
    co_ppm: float,
    v003_volume_liters: float,
    target_ni: int = 6,
    target_mn: int = 2,
    target_co: int = 2,
    tolerance_pct: float = 5.0,
) -> NMCDosageResult:
    """Full NMC dosage calculation from ICP results.

    Steps (from SOP NMC sheet):
    1. Convert ppm -> g/L -> mol/L
    2. Calculate actual NMC ratio
    3. Compare to target within tolerance
    4. If outside tolerance, calculate CoSO4 and MnSO4 additions
    5. Calculate NH4OH and NaOH for precipitation
    """
    ratios = calculate_molar_ratios(ni_ppm, mn_ppm, co_ppm)

    # Target: normalize so Ni defines the scale
    # e.g., for 6-2-2: we want Mn and Co each at (2/6) of Ni's molar concentration
    target_sum = target_ni + target_mn + target_co
    target_ni_frac = target_ni / target_sum
    target_mn_frac = target_mn / target_sum
    target_co_frac = target_co / target_sum

    actual_sum = ratios.ni_mol_per_l + ratios.mn_mol_per_l + ratios.co_mol_per_l
    if actual_sum <= 0:
        return NMCDosageResult(
            decision="skip_step",
            target_ratio=(target_ni, target_mn, target_co),
            actual_ratio=(0, 0, 0),
            coso4_7h2o_kg=0,
            coso4_di_water_liters=0,
            mnso4_h2o_kg=0,
            mnso4_di_water_liters=0,
            nh4oh_liters=0,
            naoh_liters=0,
        )

    # Use Ni as the reference: the target total metal concentration is set by
    # making Ni's fraction equal to target_ni_frac
    # total_target = Ni_mol / target_ni_frac
    total_target_mol_per_l = ratios.ni_mol_per_l / target_ni_frac

    required_mn_mol_per_l = total_target_mol_per_l * target_mn_frac
    required_co_mol_per_l = total_target_mol_per_l * target_co_frac

    mn_deficit_mol_per_l = max(0, required_mn_mol_per_l - ratios.mn_mol_per_l)
    co_deficit_mol_per_l = max(0, required_co_mol_per_l - ratios.co_mol_per_l)

    # Check if within tolerance
    mn_pct_off = (
        abs(ratios.mn_mol_per_l - required_mn_mol_per_l) / required_mn_mol_per_l * 100
        if required_mn_mol_per_l > 0
        else 0
    )
    co_pct_off = (
        abs(ratios.co_mol_per_l - required_co_mol_per_l) / required_co_mol_per_l * 100
        if required_co_mol_per_l > 0
        else 0
    )

    if mn_pct_off <= tolerance_pct and co_pct_off <= tolerance_pct:
        decision = "within_tolerance"
    else:
        decision = "continue_dosing"

    v003_m3 = v003_volume_liters / 1000.0

    # CoSO4*7H2O needed: deficit_mol/L * volume_L * MW_salt / 1000 (to kg)
    coso4_kg = co_deficit_mol_per_l * v003_volume_liters * MW_COSO4_7H2O / 1000.0
    coso4_water = coso4_kg * COSO4_WATER_RATIO

    # MnSO4*H2O needed
    mnso4_kg = mn_deficit_mol_per_l * v003_volume_liters * MW_MNSO4_H2O / 1000.0
    mnso4_water = mnso4_kg * MNSO4_WATER_RATIO

    # NH4OH and NaOH: based on total metal mol/L and volume
    nh4oh_liters = NH4OH_L_PER_M3_PER_MOL * total_target_mol_per_l * v003_m3
    naoh_liters = NAOH_L_PER_M3_PER_MOL * total_target_mol_per_l * v003_m3

    return NMCDosageResult(
        decision=decision,
        target_ratio=(target_ni, target_mn, target_co),
        actual_ratio=(
            ratios.actual_ratio_ni,
            ratios.actual_ratio_mn,
            ratios.actual_ratio_co,
        ),
        coso4_7h2o_kg=round(coso4_kg, 3),
        coso4_di_water_liters=round(coso4_water, 3),
        mnso4_h2o_kg=round(mnso4_kg, 3),
        mnso4_di_water_liters=round(mnso4_water, 3),
        nh4oh_liters=round(nh4oh_liters, 3),
        naoh_liters=round(naoh_liters, 3),
    )
