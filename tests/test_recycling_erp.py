"""Unit tests for Green Li-ion Recycling ERP business rules.

Tests verify calculations against known SOP reference values.
"""

import pytest
from datetime import date, timedelta

from battery_erp.app.rules.recipe import (
    calculate_recipe,
    h2so4_per_dosing_step,
    h2o2_per_dosing_step,
)
from battery_erp.app.rules.nmc import (
    calculate_molar_ratios,
    calculate_nmc_dosage,
    ppm_to_mol_per_l,
    MW_NI,
    MW_MN,
    MW_CO,
)
from battery_erp.app.rules.valve import (
    check_valve_conflicts,
    validate_step_valve_positions,
    get_vessel_valve_requirements,
)
from battery_erp.app.rules.costing import (
    calculate_batch_cost,
    cost_per_kg_product,
    calculate_yield,
    CostInput,
)
from battery_erp.app.rules.inventory import (
    check_chemical_reorder,
    select_black_mass_fifo,
    calculate_tote_stock,
)
from battery_erp.app.rules.maintenance import (
    check_inspection_schedule,
    generate_work_orders_from_inspection,
)
from battery_erp.app.rules.supplier import score_supplier, three_quote_check
from battery_erp.app.models.enums import ValveState, Vessel
from battery_erp.app.seed.chemicals import CHEMICAL_CATALOG
from battery_erp.app.seed.process_steps import PROCESS_STEP_TEMPLATES
from battery_erp.app.seed.inspection_items import GLMC_1_ITEMS, GLMLD_1_ITEMS


# ─── Recipe Calculator ────────────────────────────────────────────────

class TestRecipeCalculator:
    def test_sop_reference_500kg_98pct(self):
        """SOP reference: 500kg batch, 98% H2SO4 -> 1446.83 kg H2SO4."""
        result = calculate_recipe(500.0, h2so4_concentration_pct=98.0)
        assert result.h2so4_kg == 1446.83
        assert result.h2o2_liters == 279.41
        assert result.dm_water_liters == 3000.0
        assert result.h2so4_skip_step is False
        assert result.dosing_steps == 4

    def test_scaled_750kg(self):
        """750kg should be 1.5x the 500kg reference."""
        result = calculate_recipe(750.0)
        assert result.h2so4_kg == pytest.approx(1446.83 * 1.5, rel=1e-2)
        assert result.h2o2_liters == pytest.approx(279.41 * 1.5, rel=1e-2)
        assert result.dm_water_liters == 4500.0

    def test_scaled_1000kg(self):
        """1000kg should be 2x the 500kg reference."""
        result = calculate_recipe(1000.0)
        assert result.h2so4_kg == pytest.approx(1446.83 * 2.0, rel=1e-2)
        assert result.h2o2_liters == pytest.approx(279.41 * 2.0, rel=1e-2)

    def test_50pct_h2so4_uses_alternate_reference(self):
        """50% H2SO4 uses the alternate 4582 kg reference and sets skip flag."""
        result = calculate_recipe(500.0, h2so4_concentration_pct=50.0)
        assert result.h2so4_kg == 4582.0
        assert result.h2so4_skip_step is True

    def test_dosing_step_split(self):
        """H2SO4 and H2O2 should split evenly into 4 dosing steps."""
        result = calculate_recipe(500.0)
        step_acid = h2so4_per_dosing_step(result)
        step_peroxide = h2o2_per_dosing_step(result)
        assert step_acid == pytest.approx(1446.83 / 4, rel=1e-2)
        assert step_peroxide == pytest.approx(279.41 / 4, rel=1e-2)

    def test_zero_batch_size(self):
        result = calculate_recipe(0.0)
        assert result.h2so4_kg == 0.0
        assert result.h2o2_liters == 0.0


# ─── NMC Ratio Engine ─────────────────────────────────────────────────

class TestNMCEngine:
    def test_ppm_to_mol_conversion(self):
        """Verify basic ppm->mol/L math: 58693 ppm Ni = 1 mol/L."""
        result = ppm_to_mol_per_l(58693.0, MW_NI)
        assert result == pytest.approx(1.0, rel=1e-3)

    def test_molar_ratios_balanced_622(self):
        """If ICP shows perfect 6:2:2 molar ratio, ratios should reflect that."""
        ni_ppm = MW_NI * 1000 * 6  # 6 mol/L
        mn_ppm = MW_MN * 1000 * 2  # 2 mol/L
        co_ppm = MW_CO * 1000 * 2  # 2 mol/L
        result = calculate_molar_ratios(ni_ppm, mn_ppm, co_ppm)
        assert result.actual_ratio_ni == pytest.approx(3.0, rel=1e-2)
        assert result.actual_ratio_mn == pytest.approx(1.0, rel=1e-2)
        assert result.actual_ratio_co == pytest.approx(1.0, rel=1e-2)

    def test_dosage_within_tolerance_returns_no_additions(self):
        """When ICP results match target within 5%, decision should be within_tolerance."""
        ni_ppm = MW_NI * 1000 * 6
        mn_ppm = MW_MN * 1000 * 2
        co_ppm = MW_CO * 1000 * 2
        result = calculate_nmc_dosage(
            ni_ppm=ni_ppm, mn_ppm=mn_ppm, co_ppm=co_ppm,
            v003_volume_liters=7000.0,
        )
        assert result.decision == "within_tolerance"
        assert result.coso4_7h2o_kg == 0.0
        assert result.mnso4_h2o_kg == 0.0

    def test_dosage_co_deficit_triggers_addition(self):
        """Low cobalt should trigger CoSO4 addition."""
        ni_ppm = MW_NI * 1000 * 6
        mn_ppm = MW_MN * 1000 * 2
        co_ppm = MW_CO * 1000 * 1  # Only 1 mol/L instead of 2
        result = calculate_nmc_dosage(
            ni_ppm=ni_ppm, mn_ppm=mn_ppm, co_ppm=co_ppm,
            v003_volume_liters=7000.0,
        )
        assert result.decision == "continue_dosing"
        assert result.coso4_7h2o_kg > 0

    def test_dosage_mn_deficit_triggers_addition(self):
        """Low manganese should trigger MnSO4 addition."""
        ni_ppm = MW_NI * 1000 * 6
        mn_ppm = MW_MN * 1000 * 1  # Only 1 mol/L instead of 2
        co_ppm = MW_CO * 1000 * 2
        result = calculate_nmc_dosage(
            ni_ppm=ni_ppm, mn_ppm=mn_ppm, co_ppm=co_ppm,
            v003_volume_liters=7000.0,
        )
        assert result.decision == "continue_dosing"
        assert result.mnso4_h2o_kg > 0

    def test_zero_icp_returns_skip(self):
        result = calculate_nmc_dosage(0, 0, 0, v003_volume_liters=7000)
        assert result.decision == "skip_step"

    def test_nh4oh_and_naoh_calculated(self):
        """NH4OH and NaOH should always be calculated when metals are present."""
        result = calculate_nmc_dosage(
            ni_ppm=29449.658, mn_ppm=3740.263, co_ppm=5249.824,
            v003_volume_liters=7280.8,
        )
        assert result.nh4oh_liters > 0
        assert result.naoh_liters > 0


# ─── Valve Validation ─────────────────────────────────────────────────

class TestValveValidation:
    def test_no_conflicts_when_all_closed(self):
        states = {"XV-213": ValveState.CLOSED, "XV-212": ValveState.CLOSED}
        conflicts = check_valve_conflicts(states)
        assert len(conflicts) == 0

    def test_detects_v002_diverter_conflict(self):
        """XV-213 and XV-212 cannot both be open (recirculate vs V-003)."""
        states = {"XV-213": ValveState.OPEN, "XV-212": ValveState.OPEN}
        conflicts = check_valve_conflicts(states)
        assert len(conflicts) == 1
        assert conflicts[0].valve_a == "XV-213"

    def test_detects_acid_recirculation_conflict(self):
        """XV-109 and MV-466 cannot both be open."""
        states = {"XV-109": ValveState.OPEN, "MV-466": ValveState.OPEN}
        conflicts = check_valve_conflicts(states)
        assert len(conflicts) == 1

    def test_detects_simultaneous_dosing_conflict(self):
        """XV-102 (H2O2) and XV-109 (H2SO4) shouldn't dose simultaneously."""
        states = {"XV-102": ValveState.OPEN, "XV-109": ValveState.OPEN}
        conflicts = check_valve_conflicts(states)
        assert len(conflicts) == 1

    def test_validate_step_positions_all_match(self):
        required = [("XV-110", ValveState.CLOSED), ("XV-101", ValveState.CLOSED)]
        actual = {"XV-110": ValveState.CLOSED, "XV-101": ValveState.CLOSED}
        valid, mismatches = validate_step_valve_positions(required, actual)
        assert valid is True
        assert len(mismatches) == 0

    def test_validate_step_positions_mismatch(self):
        required = [("XV-110", ValveState.CLOSED)]
        actual = {"XV-110": ValveState.OPEN}
        valid, mismatches = validate_step_valve_positions(required, actual)
        assert valid is False
        assert len(mismatches) == 1

    def test_validate_step_positions_missing_valve(self):
        required = [("XV-999", ValveState.CLOSED)]
        actual = {}
        valid, mismatches = validate_step_valve_positions(required, actual)
        assert valid is False
        assert "not verified" in mismatches[0]

    def test_v001_has_valve_registry(self):
        reqs = get_vessel_valve_requirements(Vessel.V001)
        assert len(reqs) >= 7
        valve_ids = [r.valve_id for r in reqs]
        assert "XV-110" in valve_ids
        assert "XV-109" in valve_ids


# ─── Batch Costing ────────────────────────────────────────────────────

class TestBatchCosting:
    def test_cost_rollup_sums_correctly(self):
        inputs = CostInput(
            black_mass_cost_per_mt=2000.0, black_mass_kg_used=500.0,
            water_cost_per_liter=0.005, water_liters_used=4000.0,
            h2so4_cost_per_liter=0.50, h2so4_liters_used=800.0,
            utility_cost=150.0, labor_cost=300.0,
        )
        result = calculate_batch_cost(inputs)
        expected_bm = 500.0 * (2000.0 / 1000.0)  # 1000.0
        expected_water = 4000.0 * 0.005  # 20.0
        expected_acid = 800.0 * 0.50  # 400.0
        assert result.black_mass_cost == expected_bm
        assert result.water_cost == expected_water
        assert result.h2so4_cost == expected_acid
        assert result.total_batch_cost == expected_bm + expected_water + expected_acid + 150.0 + 300.0

    def test_zero_inputs_zero_cost(self):
        result = calculate_batch_cost(CostInput())
        assert result.total_batch_cost == 0.0

    def test_cost_per_kg_product(self):
        assert cost_per_kg_product(10000.0, 50.0) == 200.0
        assert cost_per_kg_product(10000.0, 50.0, allocation_pct=50.0) == 100.0

    def test_cost_per_kg_zero_weight(self):
        assert cost_per_kg_product(10000.0, 0.0) == 0.0

    def test_yield_calculation(self):
        """500kg BM at 20% Ni = 100kg Ni input. 85kg recovered = 85%."""
        assert calculate_yield(500.0, 20.0, 85.0) == 85.0

    def test_yield_zero_input(self):
        assert calculate_yield(0.0, 20.0, 85.0) == 0.0


# ─── Inventory ────────────────────────────────────────────────────────

class TestInventory:
    def test_reorder_alert_below_min(self):
        alert = check_chemical_reorder("H2SO4", "H2SO4", 3000, 5000, 15000)
        assert alert is not None
        assert alert.suggested_order_qty == 12000.0
        assert alert.urgency == "standard"

    def test_reorder_alert_zero_stock(self):
        alert = check_chemical_reorder("H2SO4", "H2SO4", 0, 5000, 15000)
        assert alert is not None
        assert alert.urgency == "critical"

    def test_no_alert_above_min(self):
        alert = check_chemical_reorder("H2SO4", "H2SO4", 6000, 5000, 15000)
        assert alert is None

    def test_fifo_selects_oldest_first(self):
        batches = [
            {"id": "b2", "batch_number": "BM-2", "date_received": "2026-02-01", "net_weight_kg": 400, "status": "in_storage"},
            {"id": "b1", "batch_number": "BM-1", "date_received": "2026-01-01", "net_weight_kg": 300, "status": "in_storage"},
        ]
        selections = select_black_mass_fifo(batches, 500.0)
        assert len(selections) == 2
        assert selections[0]["batch_number"] == "BM-1"
        assert selections[0]["kg_to_consume"] == 300.0
        assert selections[1]["kg_to_consume"] == 200.0

    def test_fifo_skips_depleted(self):
        batches = [
            {"id": "b1", "batch_number": "BM-1", "date_received": "2026-01-01", "net_weight_kg": 300, "status": "depleted"},
            {"id": "b2", "batch_number": "BM-2", "date_received": "2026-02-01", "net_weight_kg": 500, "status": "in_storage"},
        ]
        selections = select_black_mass_fifo(batches, 400.0)
        assert len(selections) == 1
        assert selections[0]["batch_number"] == "BM-2"

    def test_tote_stock_calculation(self):
        totes = [
            {"current_level": 500, "status": "connected"},
            {"current_level": 800, "status": "in_storage"},
            {"current_level": 200, "status": "empty"},
        ]
        assert calculate_tote_stock(totes) == 1300


# ─── Maintenance ──────────────────────────────────────────────────────

class TestMaintenance:
    def test_overdue_inspection(self):
        today = date(2026, 5, 28)
        last = date(2026, 4, 15)  # 43 days ago — overdue
        result = check_inspection_schedule("GLMC-1", last, today=today)
        assert result.status == "overdue"
        assert result.days_until_due < 0

    def test_due_soon_inspection(self):
        today = date(2026, 5, 28)
        last = date(2026, 5, 2)  # Due Jun 1 — 4 days away
        result = check_inspection_schedule("GLMC-1", last, today=today)
        assert result.status == "due_soon"

    def test_on_time_inspection(self):
        today = date(2026, 5, 28)
        last = date(2026, 5, 15)  # Due Jun 14 — 17 days away
        result = check_inspection_schedule("GLMC-1", last, today=today)
        assert result.status == "on_time"

    def test_never_inspected(self):
        result = check_inspection_schedule("GLMC-1", None)
        assert result.status == "never_inspected"

    def test_work_order_high_priority_for_hydraulics(self):
        items = [{"category": "Hydraulics Inspection", "item_description": "Leak found", "followup_notes": "Replace seal", "equipment": "F-001"}]
        orders = generate_work_orders_from_inspection(items)
        assert len(orders) == 1
        assert orders[0].priority == "high"

    def test_work_order_medium_priority_default(self):
        items = [{"category": "Package/Skid Maintenance", "item_description": "Dirty skid", "followup_notes": "", "equipment": "V-001"}]
        orders = generate_work_orders_from_inspection(items)
        assert orders[0].priority == "medium"


# ─── Supplier Scoring ─────────────────────────────────────────────────

class TestSupplierScoring:
    def test_grade_a_supplier(self):
        result = score_supplier("s1", "ChemCo", 95.0, 92.0, 14, ["ISO9001", "ISO14001", "REACH"])
        assert result.grade == "A"
        assert result.composite_score >= 80

    def test_grade_d_supplier(self):
        result = score_supplier("s2", "BadCo", 30.0, 40.0, 90, [])
        assert result.grade == "D"

    def test_three_quote_check_pass(self):
        ok, msg = three_quote_check(3)
        assert ok is True

    def test_three_quote_check_fail(self):
        ok, msg = three_quote_check(1)
        assert ok is False
        assert "2 more" in msg


# ─── Seed Data Integrity ─────────────────────────────────────────────

class TestSeedData:
    def test_chemical_catalog_has_9_entries(self):
        assert len(CHEMICAL_CATALOG) == 9

    def test_chemical_catalog_has_h2so4(self):
        names = [c["name"] for c in CHEMICAL_CATALOG]
        assert "Sulfuric Acid" in names

    def test_process_steps_cover_all_vessels(self):
        vessels = {t[0].value for t in PROCESS_STEP_TEMPLATES}
        assert "pre_start" in vessels
        assert "v001" in vessels
        assert "v002" in vessels

    def test_process_steps_count(self):
        assert len(PROCESS_STEP_TEMPLATES) == 68

    def test_glmc1_inspection_items_count(self):
        assert len(GLMC_1_ITEMS) == 27

    def test_glmld1_inspection_items_count(self):
        assert len(GLMLD_1_ITEMS) == 22

    def test_step_numbers_sequential(self):
        numbers = [t[1] for t in PROCESS_STEP_TEMPLATES]
        assert numbers == sorted(numbers)
        assert numbers[0] == 1
        assert numbers[-1] == 68
