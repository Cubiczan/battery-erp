"""Inventory rules: FIFO for black mass, reorder alerts for chemicals."""

from dataclasses import dataclass


@dataclass
class ReorderAlert:
    chemical_name: str
    formula: str
    current_stock: float
    min_stock: float
    suggested_order_qty: float
    urgency: str


def check_chemical_reorder(
    name: str,
    formula: str,
    current_stock: float,
    min_stock: float,
    max_stock: float,
) -> ReorderAlert | None:
    """Check if a chemical needs reordering. Returns None if stock is adequate."""
    if current_stock > min_stock:
        return None

    suggested = max_stock - current_stock
    urgency = "critical" if current_stock <= 0 else "standard"

    return ReorderAlert(
        chemical_name=name,
        formula=formula,
        current_stock=round(current_stock, 2),
        min_stock=round(min_stock, 2),
        suggested_order_qty=round(suggested, 2),
        urgency=urgency,
    )


def select_black_mass_fifo(
    batches: list[dict],
    required_kg: float,
) -> list[dict]:
    """Select black mass batches using FIFO (oldest first).

    Each batch dict must have: id, batch_number, date_received, net_weight_kg, status.
    Returns list of {batch_id, batch_number, kg_to_consume} dicts.
    """
    sorted_batches = sorted(batches, key=lambda b: b["date_received"])
    selections = []
    remaining = required_kg

    for batch in sorted_batches:
        if remaining <= 0:
            break
        if batch.get("status") not in ("in_storage", "received"):
            continue

        available = batch["net_weight_kg"]
        consume = min(available, remaining)
        selections.append({
            "batch_id": batch["id"],
            "batch_number": batch["batch_number"],
            "kg_to_consume": round(consume, 2),
        })
        remaining -= consume

    return selections


def calculate_tote_stock(totes: list[dict]) -> float:
    """Sum current levels from active totes (in_storage or connected)."""
    return sum(
        t["current_level"]
        for t in totes
        if t.get("status") in ("in_storage", "connected")
    )
