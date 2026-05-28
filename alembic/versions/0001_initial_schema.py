"""Initial schema — all 22 domain tables for recycling ERP.

Revision ID: 0001
Revises: None
Create Date: 2026-05-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("role", sa.String(30), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("contact_name", sa.String(200), server_default=""),
        sa.Column("email", sa.String(200), server_default=""),
        sa.Column("phone", sa.String(50), server_default=""),
        sa.Column("address", sa.Text, server_default=""),
        sa.Column("materials_supplied", postgresql.JSON, server_default="[]"),
        sa.Column("quality_rating", sa.Numeric(5, 2), server_default="0"),
        sa.Column("on_time_delivery_pct", sa.Numeric(5, 2), server_default="0"),
        sa.Column("avg_lead_time_days", sa.Integer, server_default="30"),
        sa.Column("certifications", postgresql.JSON, server_default="[]"),
        sa.Column("status", sa.String(30), server_default="active"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "black_mass_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("lot_number", sa.String(50), server_default=""),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=True),
        sa.Column("date_received", sa.DateTime, server_default=sa.func.now()),
        sa.Column("gross_weight_kg", sa.Numeric(10, 2), server_default="0"),
        sa.Column("tare_weight_kg", sa.Numeric(10, 2), server_default="0"),
        sa.Column("net_weight_kg", sa.Numeric(10, 2), server_default="0"),
        sa.Column("storage_location", sa.String(100), server_default=""),
        sa.Column("status", sa.String(30), server_default="received"),
        sa.Column("composition", postgresql.JSON, server_default="{}"),
        sa.Column("notes", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "chemicals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("formula", sa.String(50), nullable=False),
        sa.Column("concentration_pct", sa.Numeric(5, 2), server_default="100"),
        sa.Column("molecular_weight", sa.Numeric(8, 3), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("unit_cost", sa.Numeric(10, 4), server_default="0"),
        sa.Column("hazard_class", sa.String(100), server_default=""),
        sa.Column("sds_document_url", sa.String(500), server_default=""),
        sa.Column("min_stock", sa.Numeric(10, 2), server_default="0"),
        sa.Column("max_stock", sa.Numeric(10, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "chemical_totes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("chemical_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chemicals.id"), nullable=False),
        sa.Column("lot_number", sa.String(50), server_default=""),
        sa.Column("capacity", sa.Numeric(10, 2), nullable=False),
        sa.Column("current_level", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=False),
        sa.Column("location", sa.String(100), server_default=""),
        sa.Column("status", sa.String(30), server_default="in_storage"),
        sa.Column("connected_to_vessel", sa.String(20), nullable=True),
        sa.Column("date_received", sa.DateTime, server_default=sa.func.now()),
        sa.Column("cam_lock_inspected", sa.Boolean, server_default="false"),
        sa.Column("weather_protected", sa.Boolean, server_default="false"),
        sa.Column("notes", sa.Text, server_default=""),
    )

    op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("batch_size_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("target_nmc_ratio", sa.String(20), server_default="6-2-2"),
        sa.Column("h2so4_concentration_pct", sa.Numeric(5, 2), server_default="98"),
        sa.Column("h2o2_concentration_pct", sa.Numeric(5, 2), server_default="34"),
        sa.Column("naoh_concentration_pct", sa.Numeric(5, 2), server_default="25"),
        sa.Column("nh4oh_concentration_pct", sa.Numeric(5, 2), server_default="19"),
        sa.Column("dm_water_liters", sa.Numeric(10, 2), server_default="3000"),
        sa.Column("h2so4_kg", sa.Numeric(10, 2), server_default="0"),
        sa.Column("h2o2_liters", sa.Numeric(10, 2), server_default="0"),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("status", sa.String(30), server_default="draft"),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "process_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("black_mass_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("black_mass_batches.id"), nullable=False),
        sa.Column("black_mass_weight_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(30), server_default="pre_start"),
        sa.Column("shift_date", sa.Date, nullable=False),
        sa.Column("start_time", sa.DateTime, nullable=True),
        sa.Column("end_time", sa.DateTime, nullable=True),
        sa.Column("plant_manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("forklift_operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("jsa_completed", sa.Boolean, server_default="false"),
        sa.Column("ppe_verified", sa.Boolean, server_default="false"),
        sa.Column("notes", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "process_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_batches.id"), nullable=False),
        sa.Column("vessel", sa.String(20), nullable=False),
        sa.Column("step_number", sa.Integer, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("responsible_role", sa.String(30), nullable=False),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(30), server_default="pending"),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column("recorded_value", sa.String(200), nullable=True),
        sa.Column("estimated_duration_min", sa.Integer, server_default="0"),
        sa.Column("notes", sa.Text, server_default=""),
    )

    op.create_table(
        "valve_positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_step_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_steps.id"), nullable=False),
        sa.Column("valve_id", sa.String(20), nullable=False),
        sa.Column("required_state", sa.String(20), nullable=False),
        sa.Column("verified", sa.Boolean, server_default="false"),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("verified_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "lab_samples",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("sample_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("process_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_batches.id"), nullable=False),
        sa.Column("vessel", sa.String(20), nullable=False),
        sa.Column("sample_point", sa.String(20), server_default=""),
        sa.Column("collected_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("collected_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("ni_ppm", sa.Numeric(12, 3), nullable=True),
        sa.Column("mn_ppm", sa.Numeric(12, 3), nullable=True),
        sa.Column("co_ppm", sa.Numeric(12, 3), nullable=True),
        sa.Column("li_ppm", sa.Numeric(12, 3), nullable=True),
        sa.Column("ph", sa.Numeric(5, 2), nullable=True),
        sa.Column("temperature_c", sa.Numeric(5, 1), nullable=True),
        sa.Column("solution_volume_liters", sa.Numeric(10, 2), server_default="0"),
        sa.Column("notes", sa.Text, server_default=""),
    )

    op.create_table(
        "nmc_dosage_calculations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lab_sample_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lab_samples.id"), nullable=False),
        sa.Column("target_nmc_ratio", sa.String(20), nullable=False),
        sa.Column("tolerance_pct", sa.Numeric(5, 2), server_default="5.0"),
        sa.Column("decision", sa.String(30), nullable=False),
        sa.Column("coso4_7h2o_kg", sa.Numeric(10, 3), server_default="0"),
        sa.Column("coso4_di_water_liters", sa.Numeric(10, 3), server_default="0"),
        sa.Column("mnso4_h2o_kg", sa.Numeric(10, 3), server_default="0"),
        sa.Column("mnso4_di_water_liters", sa.Numeric(10, 3), server_default="0"),
        sa.Column("nh4oh_liters", sa.Numeric(10, 3), server_default="0"),
        sa.Column("naoh_liters", sa.Numeric(10, 3), server_default="0"),
        sa.Column("calculated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_type", sa.String(30), nullable=False),
        sa.Column("process_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_batches.id"), nullable=False),
        sa.Column("weight_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("moisture_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("purity_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("nmc_ratio", sa.String(20), nullable=True),
        sa.Column("storage_location", sa.String(100), server_default=""),
        sa.Column("status", sa.String(30), server_default="collected"),
        sa.Column("collected_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("quality_grade", sa.String(20), nullable=True),
    )

    op.create_table(
        "mld_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("batch_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("feed_source_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_batches.id"), nullable=True),
        sa.Column("status", sa.String(30), server_default="startup"),
        sa.Column("start_time", sa.DateTime, nullable=True),
        sa.Column("end_time", sa.DateTime, nullable=True),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("seal_flush_pressure_bar", sa.Numeric(5, 2), nullable=True),
        sa.Column("condensate_tank_level_mm", sa.Numeric(7, 1), nullable=True),
        sa.Column("mvr_compressor_status", sa.String(100), server_default=""),
        sa.Column("crystallizer_status", sa.String(100), server_default=""),
        sa.Column("product_weight_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("notes", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "mld_operation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("mld_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mld_batches.id"), nullable=False),
        sa.Column("log_type", sa.String(20), nullable=False),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now()),
        sa.Column("parameter", sa.String(100), nullable=False),
        sa.Column("value", sa.String(200), nullable=False),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    op.create_table(
        "gas_scrubber_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_batches.id"), nullable=False),
        sa.Column("scrubber_id", sa.String(20), nullable=False),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now()),
        sa.Column("ph_reading", sa.Numeric(5, 2), nullable=False),
        sa.Column("airflow_status", sa.String(100), server_default=""),
        sa.Column("naoh_consumption_liters", sa.Numeric(10, 2), server_default="0"),
        sa.Column("operator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    op.create_table(
        "batch_costs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_batch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("process_batches.id"), unique=True, nullable=False),
        sa.Column("black_mass_cost_per_mt", sa.Numeric(10, 2), server_default="0"),
        sa.Column("black_mass_kg_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("water_cost_per_liter", sa.Numeric(8, 4), server_default="0"),
        sa.Column("water_liters_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("naoh_cost_per_liter", sa.Numeric(8, 4), server_default="0"),
        sa.Column("naoh_liters_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("h2so4_cost_per_liter", sa.Numeric(8, 4), server_default="0"),
        sa.Column("h2so4_liters_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("h2o2_cost_per_liter", sa.Numeric(8, 4), server_default="0"),
        sa.Column("h2o2_liters_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("caoh2_cost_per_lb", sa.Numeric(8, 4), server_default="0"),
        sa.Column("caoh2_lbs_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("coso4_cost_per_lb", sa.Numeric(8, 4), server_default="0"),
        sa.Column("coso4_lbs_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("mnso4_cost_per_lb", sa.Numeric(8, 4), server_default="0"),
        sa.Column("mnso4_lbs_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("nh4oh_cost_per_liter", sa.Numeric(8, 4), server_default="0"),
        sa.Column("nh4oh_liters_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("na2co3_cost_per_lb", sa.Numeric(8, 4), server_default="0"),
        sa.Column("na2co3_lbs_used", sa.Numeric(10, 2), server_default="0"),
        sa.Column("utility_cost", sa.Numeric(10, 2), server_default="0"),
        sa.Column("labor_cost", sa.Numeric(10, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "maintenance_inspections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("form_type", sa.String(30), nullable=False),
        sa.Column("inspector_name", sa.String(200), nullable=False),
        sa.Column("inspection_date", sa.Date, nullable=False),
        sa.Column("last_inspection_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(30), server_default="in_progress"),
        sa.Column("signature", sa.String(500), server_default=""),
        sa.Column("comments", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "maintenance_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("maintenance_inspections.id"), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("item_description", sa.Text, nullable=False),
        sa.Column("check_type", sa.String(20), nullable=False),
        sa.Column("result", sa.String(200), server_default=""),
        sa.Column("requires_followup", sa.Boolean, server_default="false"),
        sa.Column("followup_notes", sa.Text, server_default=""),
    )

    op.create_table(
        "maintenance_work_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("maintenance_inspections.id"), nullable=True),
        sa.Column("equipment", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("status", sa.String(30), server_default="open"),
        sa.Column("assigned_to", sa.String(200), server_default=""),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("completed_date", sa.Date, nullable=True),
        sa.Column("parts_used", postgresql.JSON, server_default="[]"),
        sa.Column("downtime_hours", sa.Numeric(6, 2), server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "spare_parts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("part_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("applicable_equipment", postgresql.JSON, server_default="[]"),
        sa.Column("min_stock", sa.Integer, server_default="0"),
        sa.Column("max_stock", sa.Integer, server_default="0"),
        sa.Column("current_stock", sa.Integer, server_default="0"),
        sa.Column("unit_cost", sa.Numeric(10, 2), server_default="0"),
        sa.Column("lead_time_days", sa.Integer, server_default="0"),
        sa.Column("location", sa.String(100), server_default=""),
        sa.Column("last_ordered", sa.Date, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "spare_part_quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("spare_part_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("spare_parts.id"), nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("quote_number", sa.String(50), server_default=""),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("lead_time_days", sa.Integer, server_default="0"),
        sa.Column("valid_until", sa.Date, nullable=True),
        sa.Column("status", sa.String(30), server_default="requested"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "purchase_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("po_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("order_type", sa.String(30), nullable=False),
        sa.Column("line_items", postgresql.JSON, server_default="[]"),
        sa.Column("total_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("status", sa.String(30), server_default="draft"),
        sa.Column("order_date", sa.Date, nullable=False),
        sa.Column("expected_delivery", sa.Date, nullable=True),
        sa.Column("actual_delivery", sa.Date, nullable=True),
        sa.Column("precoro_po_id", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text, server_default=""),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("purchase_orders")
    op.drop_table("spare_part_quotes")
    op.drop_table("spare_parts")
    op.drop_table("maintenance_work_orders")
    op.drop_table("maintenance_items")
    op.drop_table("maintenance_inspections")
    op.drop_table("batch_costs")
    op.drop_table("gas_scrubber_logs")
    op.drop_table("mld_operation_logs")
    op.drop_table("mld_batches")
    op.drop_table("products")
    op.drop_table("nmc_dosage_calculations")
    op.drop_table("lab_samples")
    op.drop_table("valve_positions")
    op.drop_table("process_steps")
    op.drop_table("process_batches")
    op.drop_table("recipes")
    op.drop_table("chemical_totes")
    op.drop_table("chemicals")
    op.drop_table("black_mass_batches")
    op.drop_table("suppliers")
    op.drop_table("users")
