"""Valve position validation engine.

Enforces SOP valve states per vessel/step and detects conflicts.
"""

from dataclasses import dataclass

from battery_erp.app.models.enums import ValveState, Vessel


@dataclass
class ValveRequirement:
    valve_id: str
    required_state: ValveState
    vessel: Vessel
    system: str


# Valve registry from SOP Appendix C — required states per vessel operation
VALVE_REGISTRY: dict[Vessel, list[ValveRequirement]] = {
    Vessel.V001: [
        ValveRequirement("XV-110", ValveState.CLOSED, Vessel.V001, "DM Water"),
        ValveRequirement("XV-101", ValveState.CLOSED, Vessel.V001, "Black Mass"),
        ValveRequirement("XV-125", ValveState.CLOSED, Vessel.V001, "Dilution Air"),
        ValveRequirement("XV-109", ValveState.CLOSED, Vessel.V001, "H2SO4"),
        ValveRequirement("XV-102", ValveState.CLOSED, Vessel.V001, "H2O2"),
        ValveRequirement("MV-462", ValveState.CLOSED, Vessel.V001, "NaOH Recirc"),
        ValveRequirement("MV-466", ValveState.CLOSED, Vessel.V001, "H2SO4 Recirc"),
    ],
    Vessel.V002: [
        ValveRequirement("XV-205", ValveState.CLOSED, Vessel.V002, "DM Water"),
        ValveRequirement("XV-208", ValveState.CLOSED, Vessel.V002, "P-002 Inlet"),
        ValveRequirement("XV-210", ValveState.CLOSED, Vessel.V002, "P-002 Start"),
        ValveRequirement("XV-211", ValveState.CLOSED, Vessel.V002, "Filtration"),
        ValveRequirement("XV-213", ValveState.CLOSED, Vessel.V002, "3-Way Diverter"),
        ValveRequirement("XV-222", ValveState.CLOSED, Vessel.V002, "Filtration Circuit"),
        ValveRequirement("XV-223", ValveState.CLOSED, Vessel.V002, "Filtration Circuit"),
        ValveRequirement("XV-224", ValveState.CLOSED, Vessel.V002, "Filtration Circuit"),
        ValveRequirement("XV-225", ValveState.CLOSED, Vessel.V002, "Filtration Circuit"),
        ValveRequirement("XV-226", ValveState.CLOSED, Vessel.V002, "Filtration Circuit"),
    ],
    Vessel.V004: [
        ValveRequirement("XV-401", ValveState.CLOSED, Vessel.V004, "P-004 Inlet"),
        ValveRequirement("XV-402", ValveState.CLOSED, Vessel.V004, "Air Supply"),
        ValveRequirement("XV-404", ValveState.CLOSED, Vessel.V004, "3-Way Diverter"),
        ValveRequirement("XV-405", ValveState.CLOSED, Vessel.V004, "Wastewater"),
        ValveRequirement("MV-429", ValveState.CLOSED, Vessel.V004, "Sample Point"),
    ],
}

# Conflicting valve pairs: these cannot both be OPEN simultaneously
VALVE_CONFLICTS: list[tuple[str, str]] = [
    ("XV-213", "XV-212"),  # V-002: recirculate vs forward to V-003
    ("XV-404", "XV-405"),  # V-004: recirculate vs wastewater
    ("XV-109", "MV-466"),  # V-001: H2SO4 dosing vs recirculation
    ("XV-102", "XV-109"),  # V-001: H2O2 and H2SO4 shouldn't dose simultaneously
]


@dataclass
class ValveConflict:
    valve_a: str
    valve_b: str
    reason: str


def get_vessel_valve_requirements(vessel: Vessel) -> list[ValveRequirement]:
    """Get default valve positions for a vessel's pre-start check."""
    return VALVE_REGISTRY.get(vessel, [])


def check_valve_conflicts(
    valve_states: dict[str, ValveState],
) -> list[ValveConflict]:
    """Check for conflicting valve states. Returns empty list if no conflicts."""
    conflicts = []
    for valve_a, valve_b in VALVE_CONFLICTS:
        state_a = valve_states.get(valve_a)
        state_b = valve_states.get(valve_b)
        if state_a == ValveState.OPEN and state_b == ValveState.OPEN:
            conflicts.append(
                ValveConflict(
                    valve_a=valve_a,
                    valve_b=valve_b,
                    reason=f"{valve_a} and {valve_b} cannot both be OPEN",
                )
            )
    return conflicts


def validate_step_valve_positions(
    required: list[tuple[str, ValveState]],
    actual: dict[str, ValveState],
) -> tuple[bool, list[str]]:
    """Validate that actual valve positions match requirements.

    Returns (all_valid, list_of_mismatches).
    """
    mismatches = []
    for valve_id, required_state in required:
        actual_state = actual.get(valve_id)
        if actual_state is None:
            mismatches.append(f"{valve_id}: not verified")
        elif actual_state != required_state:
            mismatches.append(
                f"{valve_id}: required {required_state.value}, actual {actual_state.value}"
            )
    return len(mismatches) == 0, mismatches
