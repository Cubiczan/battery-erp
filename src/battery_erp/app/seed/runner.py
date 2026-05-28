"""Seed database with SOP reference data."""

from sqlalchemy.orm import Session

from battery_erp.app.models.domain import Chemical
from battery_erp.app.models.enums import InspectionFormType
from battery_erp.app.seed.chemicals import CHEMICAL_CATALOG
from battery_erp.app.seed.inspection_items import get_inspection_template
from battery_erp.app.seed.process_steps import PROCESS_STEP_TEMPLATES


def seed_chemicals(db: Session) -> int:
    existing = db.query(Chemical).count()
    if existing > 0:
        return 0
    count = 0
    for chem in CHEMICAL_CATALOG:
        db.add(Chemical(**chem))
        count += 1
    db.commit()
    return count


def seed_all(db: Session) -> dict[str, int]:
    results = {}
    results["chemicals"] = seed_chemicals(db)
    results["process_step_templates"] = len(PROCESS_STEP_TEMPLATES)
    results["glmc1_inspection_items"] = len(get_inspection_template(InspectionFormType.GLMC_1))
    results["glmld1_inspection_items"] = len(get_inspection_template(InspectionFormType.GLMLD_1))
    return results
