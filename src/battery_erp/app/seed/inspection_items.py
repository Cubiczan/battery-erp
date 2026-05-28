"""Inspection item templates from GLMC-1 and GLMLD-1 Monthly Maintenance forms."""

from battery_erp.app.models.enums import CheckType, InspectionFormType

GLMC_1_ITEMS: list[dict] = [
    {"category": "Pre-Inspection", "item_description": "Review last inspection date", "check_type": CheckType.CHECKBOX},
    {"category": "Pre-Inspection", "item_description": "Review and complete any necessary fluid services", "check_type": CheckType.CHECKBOX},
    {"category": "Pre-Inspection", "item_description": "Review down time log for unscheduled maintenance", "check_type": CheckType.CHECKBOX},
    {"category": "Pre-Inspection", "item_description": "Review maintenance requests and speak with operator", "check_type": CheckType.CHECKBOX},
    # Hydraulics
    {"category": "Hydraulics Inspection", "item_description": "Grease rollers", "check_type": CheckType.CHECKBOX},
    {"category": "Hydraulics Inspection", "item_description": "Check for loose or missing bolts", "check_type": CheckType.CHECKBOX},
    {"category": "Hydraulics Inspection", "item_description": "Check for air and hydraulic leaks", "check_type": CheckType.CHECKBOX},
    {"category": "Hydraulics Inspection", "item_description": "Check for loose piping or pipe supports", "check_type": CheckType.CHECKBOX},
    # Filter Press Open
    {"category": "Filter Press Open Position", "item_description": "Check for leaks", "check_type": CheckType.CHECKBOX},
    {"category": "Filter Press Open Position", "item_description": "Inspect fluid levels of hydraulic tanks", "check_type": CheckType.CHECKBOX},
    {"category": "Filter Press Open Position", "item_description": "Inspect filters and O-rings", "check_type": CheckType.CHECKBOX},
    # AODD Pump
    {"category": "AODD Pump Maintenance", "item_description": "Air supply connections - visually inspect", "check_type": CheckType.CHECKBOX},
    {"category": "AODD Pump Maintenance", "item_description": "Check for loose or missing bolts", "check_type": CheckType.CHECKBOX},
    {"category": "AODD Pump Maintenance", "item_description": "On-line: inspect for leaks while running", "check_type": CheckType.CHECKBOX},
    {"category": "AODD Pump Maintenance", "item_description": "On-line: inspect for abnormal noises and vibration", "check_type": CheckType.CHECKBOX},
    # Agitator
    {"category": "Agitator Maintenance", "item_description": "Oil level - verify proper level", "check_type": CheckType.CHECKBOX},
    {"category": "Agitator Maintenance", "item_description": "Inspect for loose bolts", "check_type": CheckType.CHECKBOX},
    {"category": "Agitator Maintenance", "item_description": "Grease motors where applicable", "check_type": CheckType.CHECKBOX},
    {"category": "Agitator Maintenance", "item_description": "Verify proper operation", "check_type": CheckType.CHECKBOX},
    {"category": "Agitator Maintenance", "item_description": "Listen for unusual noises", "check_type": CheckType.CHECKBOX},
    {"category": "Agitator Maintenance", "item_description": "Shoot bearing temps where available", "check_type": CheckType.VALUE},
    # Package/Skid
    {"category": "Package/Skid Maintenance", "item_description": "Check for loose or missing bolts", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Sump drains working properly", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Condition of skid (clean or dirty)", "check_type": CheckType.VALUE},
    {"category": "Package/Skid Maintenance", "item_description": "Sight glasses & gauges - clean or repair", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Inspect electrical connections or conduit", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Check for loose automated valves", "check_type": CheckType.CHECKBOX},
]

GLMLD_1_ITEMS: list[dict] = [
    {"category": "Pre-Inspection", "item_description": "Review last inspection date", "check_type": CheckType.CHECKBOX},
    {"category": "Pre-Inspection", "item_description": "Review and complete any necessary fluid services", "check_type": CheckType.CHECKBOX},
    {"category": "Pre-Inspection", "item_description": "Review down time log for unscheduled maintenance", "check_type": CheckType.CHECKBOX},
    {"category": "Pre-Inspection", "item_description": "Review maintenance requests and speak with operator", "check_type": CheckType.CHECKBOX},
    # Electric Motors
    {"category": "Electric Motor Maintenance", "item_description": "Visually inspect motors for problems", "check_type": CheckType.CHECKBOX},
    {"category": "Electric Motor Maintenance", "item_description": "Ensure proper operation of motors", "check_type": CheckType.CHECKBOX},
    {"category": "Electric Motor Maintenance", "item_description": "Inspect motor fans - blades clean and intact", "check_type": CheckType.CHECKBOX},
    {"category": "Electric Motor Maintenance", "item_description": "Motor bearings - verify temps within limits", "check_type": CheckType.VALUE},
    {"category": "Electric Motor Maintenance", "item_description": "Motor bearings - inspect (no grease unless problem)", "check_type": CheckType.CHECKBOX},
    # Pumps
    {"category": "Pump Maintenance", "item_description": "On-line: visually inspect for leaks", "check_type": CheckType.CHECKBOX},
    {"category": "Pump Maintenance", "item_description": "On-line: listen for abnormal noises", "check_type": CheckType.CHECKBOX},
    {"category": "Pump Maintenance", "item_description": "On-line: check for abnormal foaming", "check_type": CheckType.CHECKBOX},
    {"category": "Pump Maintenance", "item_description": "On-line: shoot temp and record abnormals", "check_type": CheckType.VALUE},
    {"category": "Pump Maintenance", "item_description": "Off-line: check fluid level", "check_type": CheckType.CHECKBOX},
    {"category": "Pump Maintenance", "item_description": "Off-line: check fluid for moisture (milky)", "check_type": CheckType.CHECKBOX},
    # Package/Skid
    {"category": "Package/Skid Maintenance", "item_description": "Crystallizer pump belts - inspect & check tension", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Tubing & conduit - check tightness and connections", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Foundation bolts and chocks - check firmness", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Cooling tower - inspect & clean", "check_type": CheckType.CHECKBOX},
    {"category": "Package/Skid Maintenance", "item_description": "Wash skid as necessary", "check_type": CheckType.CHECKBOX},
    # Heat Exchangers
    {"category": "Heat Exchangers", "item_description": "Monitor pressures", "check_type": CheckType.CHECKBOX},
    {"category": "Heat Exchangers", "item_description": "Check and clean plates for fouling (external)", "check_type": CheckType.CHECKBOX},
]


def get_inspection_template(form_type: InspectionFormType) -> list[dict]:
    if form_type == InspectionFormType.GLMC_1:
        return GLMC_1_ITEMS
    return GLMLD_1_ITEMS
