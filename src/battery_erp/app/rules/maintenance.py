"""Maintenance scheduling and work order generation rules."""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class InspectionSchedule:
    equipment: str
    last_inspection: date | None
    next_due: date | None
    status: str  # "on_time", "due_soon", "overdue", "never_inspected"
    days_until_due: int | None


def check_inspection_schedule(
    equipment: str,
    last_inspection_date: date | None,
    today: date | None = None,
    interval_days: int = 30,
    reminder_days: int = 7,
) -> InspectionSchedule:
    """Check if a monthly inspection is due."""
    if today is None:
        today = date.today()

    if last_inspection_date is None:
        return InspectionSchedule(
            equipment=equipment,
            last_inspection=None,
            next_due=None,
            status="never_inspected",
            days_until_due=None,
        )

    next_due = last_inspection_date + timedelta(days=interval_days)
    days_until = (next_due - today).days

    if days_until < 0:
        status = "overdue"
    elif days_until <= reminder_days:
        status = "due_soon"
    else:
        status = "on_time"

    return InspectionSchedule(
        equipment=equipment,
        last_inspection=last_inspection_date,
        next_due=next_due,
        status=status,
        days_until_due=days_until,
    )


@dataclass
class WorkOrderSuggestion:
    equipment: str
    description: str
    priority: str
    source_item_description: str


# Categories that map to HIGH priority
_HIGH_PRIORITY_CATEGORIES = {
    "hydraulics inspection",
    "electrical",
    "electric motor maintenance",
    "heat exchangers",
}


def generate_work_orders_from_inspection(
    flagged_items: list[dict],
) -> list[WorkOrderSuggestion]:
    """Auto-generate work order suggestions from flagged inspection items.

    Each item dict: {category, item_description, followup_notes}
    """
    suggestions = []
    for item in flagged_items:
        category = item.get("category", "").lower()
        if category in _HIGH_PRIORITY_CATEGORIES:
            priority = "high"
        else:
            priority = "medium"

        desc = item.get("item_description", "")
        notes = item.get("followup_notes", "")
        full_desc = f"{desc}. {notes}".strip() if notes else desc

        suggestions.append(
            WorkOrderSuggestion(
                equipment=item.get("equipment", "Unknown"),
                description=full_desc,
                priority=priority,
                source_item_description=desc,
            )
        )

    return suggestions
