"""Supplier scoring — adapted from existing battery-erp supply_chain module.

Weights per BUILD_SPECS: quality 35%, OTD 35%, lead time 20%, certifications 10%.
"""

from dataclasses import dataclass


@dataclass
class SupplierScore:
    supplier_id: str
    name: str
    composite_score: float
    quality_score: float
    otd_score: float
    lead_time_score: float
    certification_score: float
    grade: str


def score_supplier(
    supplier_id: str,
    name: str,
    quality_rating: float,
    on_time_delivery_pct: float,
    avg_lead_time_days: int,
    certifications: list[str],
) -> SupplierScore:
    quality = min(quality_rating, 100.0)
    otd = min(on_time_delivery_pct, 100.0)

    if avg_lead_time_days <= 14:
        lead = 100.0
    elif avg_lead_time_days <= 30:
        lead = 80.0
    elif avg_lead_time_days <= 60:
        lead = 60.0
    else:
        lead = 40.0

    cert = min(len(certifications) * 3.0, 10.0)

    composite = quality * 0.35 + otd * 0.35 + lead * 0.20 + cert

    if composite >= 80:
        grade = "A"
    elif composite >= 65:
        grade = "B"
    elif composite >= 50:
        grade = "C"
    else:
        grade = "D"

    return SupplierScore(
        supplier_id=supplier_id,
        name=name,
        composite_score=round(composite, 1),
        quality_score=quality,
        otd_score=otd,
        lead_time_score=lead,
        certification_score=cert,
        grade=grade,
    )


def three_quote_check(quote_count: int) -> tuple[bool, str]:
    """Verify spare part procurement has at least 3 quotes."""
    if quote_count >= 3:
        return True, "Three-quote requirement met"
    return False, f"Need {3 - quote_count} more quote(s) before PO approval"
