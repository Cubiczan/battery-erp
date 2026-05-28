"""Process step templates from GLMC 1.0 Operating SOP.

Each template is (vessel, step_number, description, responsible_role, estimated_duration_min).
These get instantiated per ProcessBatch.
"""

from battery_erp.app.models.enums import ResponsibleRole, Vessel

PROCESS_STEP_TEMPLATES: list[tuple[Vessel, int, str, ResponsibleRole, int]] = [
    # --- PRE-START (Start-up SOP Structure sheet) ---
    (Vessel.PRE_START, 1, "JSA completed by entire shift operational team", ResponsibleRole.PLANT_MANAGER, 15),
    (Vessel.PRE_START, 2, "Discuss muster points, PPE, expected times", ResponsibleRole.PLANT_MANAGER, 5),
    (Vessel.PRE_START, 3, "Black mass recipe completed and discussed in JSA meeting", ResponsibleRole.OPERATOR, 10),
    (Vessel.PRE_START, 4, "Review air scrubbers, record pH reading", ResponsibleRole.OPERATOR, 5),
    (Vessel.PRE_START, 5, "Ensure no fluids on ground, debris removed", ResponsibleRole.ALL, 5),
    (Vessel.PRE_START, 6, "All persons put on required PPE, buddy system check", ResponsibleRole.ALL, 10),
    (Vessel.PRE_START, 7, "Ensure soda ash is in place and fresh", ResponsibleRole.OPERATOR, 3),
    (Vessel.PRE_START, 8, "Check spill kits and fire extinguishers", ResponsibleRole.OPERATOR, 5),
    (Vessel.PRE_START, 9, "Verify all valves in correct positions", ResponsibleRole.OPERATOR, 15),
    (Vessel.PRE_START, 10, "Discuss intended stopping point and results", ResponsibleRole.PLANT_MANAGER, 5),
    (Vessel.PRE_START, 11, "Record time of start", ResponsibleRole.PLANT_MANAGER, 1),
    # Black Mass Preparation
    (Vessel.PRE_START, 12, "Select BM bag, record batch/lot number", ResponsibleRole.OPERATOR, 5),
    (Vessel.PRE_START, 13, "Record BM bag weight by load cell", ResponsibleRole.FORKLIFT_OPERATOR, 5),
    (Vessel.PRE_START, 14, "Stage empty tote bag below recorded bag", ResponsibleRole.FORKLIFT_OPERATOR, 5),
    (Vessel.PRE_START, 15, "Transfer required BM amount using bag lift tool", ResponsibleRole.ALL, 15),
    (Vessel.PRE_START, 16, "Close and store BM properly", ResponsibleRole.FORKLIFT_OPERATOR, 5),
    (Vessel.PRE_START, 17, "Label new BM bag with lot number", ResponsibleRole.OPERATOR, 2),
    (Vessel.PRE_START, 18, "Locate BM bag on hopper, cut bottom of bag", ResponsibleRole.FORKLIFT_OPERATOR, 10),
    (Vessel.PRE_START, 19, "Inform team BM is in place", ResponsibleRole.FORKLIFT_OPERATOR, 1),
    # Chemical Tote Setup
    (Vessel.PRE_START, 20, "PPE for chemical handling (suit, gloves, boots, respirator, gas monitor)", ResponsibleRole.FORKLIFT_OPERATOR, 5),
    (Vessel.PRE_START, 21, "Follow material handling procedure for chemical tote", ResponsibleRole.FORKLIFT_OPERATOR, 10),
    (Vessel.PRE_START, 22, "H2SO4 tote: check weather, inspect cam lock, connect", ResponsibleRole.FORKLIFT_OPERATOR, 15),
    (Vessel.PRE_START, 23, "H2O2 tote: verify valve closed, connect, label", ResponsibleRole.FORKLIFT_OPERATOR, 10),
    (Vessel.PRE_START, 24, "Measure fluid levels on tote tanks", ResponsibleRole.FORKLIFT_OPERATOR, 5),
    (Vessel.PRE_START, 25, "Record lot numbers and tote readiness time", ResponsibleRole.FORKLIFT_OPERATOR, 2),
    # Utilities
    (Vessel.PRE_START, 26, "Turn on air compressor", ResponsibleRole.FORKLIFT_OPERATOR, 3),
    (Vessel.PRE_START, 27, "Turn on connex fan", ResponsibleRole.FORKLIFT_OPERATOR, 1),
    (Vessel.PRE_START, 28, "Turn on Demin water system", ResponsibleRole.FORKLIFT_OPERATOR, 3),
    (Vessel.PRE_START, 29, "Set dilution air regulator to 45 psi", ResponsibleRole.FORKLIFT_OPERATOR, 2),
    (Vessel.PRE_START, 30, "Inform team utilities are ready", ResponsibleRole.FORKLIFT_OPERATOR, 1),
    # Recipe handover
    (Vessel.PRE_START, 31, "Recipe prepared: water and dosing amounts calculated", ResponsibleRole.PLANT_MANAGER, 10),
    (Vessel.PRE_START, 32, "Hand over recipe to operator — plant ready to operate", ResponsibleRole.PLANT_MANAGER, 2),

    # --- V-001: Leaching (V-001 sheet, 4 dosing cycles) ---
    (Vessel.V001, 33, "DM Water: Open XV-110, dose 3000L into V-001 via FT-101", ResponsibleRole.OPERATOR, 20),
    (Vessel.V001, 34, "Record V-001 level", ResponsibleRole.OPERATOR, 1),
    (Vessel.V001, 35, "Start NaOH pump, adjust MV-462 recirculation", ResponsibleRole.OPERATOR, 5),
    (Vessel.V001, 36, "Turn on agitator AG-001", ResponsibleRole.OPERATOR, 2),
    (Vessel.V001, 37, "Turn on rotary airlock MRV-010, open XV-101, dose BM", ResponsibleRole.OPERATOR, 20),
    (Vessel.V001, 38, "Continue agitation during BM dosing for 10 min", ResponsibleRole.OPERATOR, 10),
    (Vessel.V001, 39, "Turn on gas scrubber I, check blower", ResponsibleRole.OPERATOR, 5),
    (Vessel.V001, 40, "Open XV-125 for dilution air", ResponsibleRole.OPERATOR, 2),
    # Dosing Step 1
    (Vessel.V001, 41, "Step 1.1: Start P-401 (12-18Hz→50Hz), open XV-109, dose H2SO4", ResponsibleRole.OPERATOR, 30),
    (Vessel.V001, 42, "Step 1.1: Close XV-109, open MV-466 recirculation, record temp", ResponsibleRole.OPERATOR, 5),
    (Vessel.V001, 43, "Step 1.2: Start P-305 (40Hz), open XV-102, dose H2O2", ResponsibleRole.OPERATOR, 20),
    (Vessel.V001, 44, "Step 1.3: Dose 50L DM water, record temp and level", ResponsibleRole.OPERATOR, 5),
    # Dosing Step 2
    (Vessel.V001, 45, "Step 2.1: Open XV-109, dose H2SO4, record temp/level", ResponsibleRole.OPERATOR, 30),
    (Vessel.V001, 46, "Step 2.2: Open XV-102, dose H2O2", ResponsibleRole.OPERATOR, 20),
    (Vessel.V001, 47, "Step 2.3: Dose 50L DM water, record temp/level", ResponsibleRole.OPERATOR, 5),
    # Dosing Step 3
    (Vessel.V001, 48, "Step 3.1: Open XV-109, dose H2SO4, record temp/level", ResponsibleRole.OPERATOR, 30),
    (Vessel.V001, 49, "Step 3.2: Open XV-102, dose H2O2", ResponsibleRole.OPERATOR, 20),
    (Vessel.V001, 50, "Step 3.3: Dose 50L DM water, record temp/level", ResponsibleRole.OPERATOR, 5),
    # Dosing Step 4
    (Vessel.V001, 51, "Step 4.1: Open XV-109, dose H2SO4, record temp/level", ResponsibleRole.OPERATOR, 30),
    (Vessel.V001, 52, "Step 4.2: Open XV-102, dose H2O2", ResponsibleRole.OPERATOR, 20),
    (Vessel.V001, 53, "Step 4.3: Dose 50L DM water, record temp/level", ResponsibleRole.OPERATOR, 5),
    # Final steps
    (Vessel.V001, 54, "Step 5: Dose 800L DM water, rest 10 min, record temp/level", ResponsibleRole.OPERATOR, 15),
    (Vessel.V001, 55, "Cooling: if >75C add 800L DM water, dilution air for cooling", ResponsibleRole.OPERATOR, 30),
    (Vessel.V001, 56, "Continue agitation at 54Hz until ready for filtration", ResponsibleRole.OPERATOR, 120),

    # --- V-002: Separation ---
    (Vessel.V002, 57, "Close F-001, ensure press ready. Temp < 82C", ResponsibleRole.OPERATOR, 5),
    (Vessel.V002, 58, "Filter V-001 solution through F-001, recirculate 5 min", ResponsibleRole.OPERATOR, 15),
    (Vessel.V002, 59, "Collect filtrate in V-002", ResponsibleRole.OPERATOR, 30),
    (Vessel.V002, 60, "Wash V-001 with 300L water through F-001 to V-002", ResponsibleRole.OPERATOR, 15),
    (Vessel.V002, 61, "Air dry F-001 for 5 min, measure wet graphite weight", ResponsibleRole.OPERATOR, 10),
    (Vessel.V002, 62, "Ca(OH)2 dosing: check LT201, start AG-200, add Ca(OH)2", ResponsibleRole.OPERATOR, 20),
    (Vessel.V002, 63, "NaOH pH adjustment: start P-402, dose via XV-204 to pH 5.0-5.2", ResponsibleRole.OPERATOR, 60),
    (Vessel.V002, 64, "Filter through F-002: set valves, start P-002, recirculate", ResponsibleRole.OPERATOR, 30),
    (Vessel.V002, 65, "Redirect XV-213 to V-003, collect filtrate", ResponsibleRole.OPERATOR, 30),
    (Vessel.V002, 66, "Air blow F-002 for 5 min", ResponsibleRole.OPERATOR, 5),
    (Vessel.V002, 67, "Wash V-002 with 300L water, pump through F-002 to V-003", ResponsibleRole.OPERATOR, 15),
    (Vessel.V002, 68, "F-002 cake dumping: collect filter cake, weigh, sample", ResponsibleRole.OPERATOR, 20),
]
