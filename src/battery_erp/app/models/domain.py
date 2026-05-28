import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from battery_erp.app.db.base import Base
from battery_erp.app.models.enums import (
    BatchStatus,
    BlackMassStatus,
    CheckType,
    ChemicalUnit,
    InspectionFormType,
    InspectionStatus,
    MLDBatchStatus,
    MLDLogType,
    NMCDecision,
    OrderType,
    POStatus,
    ProductStatus,
    ProductType,
    QuoteStatus,
    RecipeStatus,
    ResponsibleRole,
    StepStatus,
    SupplierStatus,
    ToteStatus,
    UserRole,
    ValveState,
    Vessel,
    WorkOrderPriority,
    WorkOrderStatus,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    contact_name: Mapped[str] = mapped_column(String(200), default="")
    email: Mapped[str] = mapped_column(String(200), default="")
    phone: Mapped[str] = mapped_column(String(50), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    materials_supplied: Mapped[list] = mapped_column(JSON, default=list)
    quality_rating: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    on_time_delivery_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    avg_lead_time_days: Mapped[int] = mapped_column(Integer, default=30)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[SupplierStatus] = mapped_column(
        Enum(SupplierStatus), default=SupplierStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(back_populates="supplier")
    spare_part_quotes: Mapped[list["SparePartQuote"]] = relationship(back_populates="supplier")


class BlackMassBatch(Base):
    __tablename__ = "black_mass_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    lot_number: Mapped[str] = mapped_column(String(50), default="")
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True
    )
    date_received: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    gross_weight_kg: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    tare_weight_kg: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    net_weight_kg: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    storage_location: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[BlackMassStatus] = mapped_column(
        Enum(BlackMassStatus), default=BlackMassStatus.RECEIVED
    )
    composition: Mapped[dict] = mapped_column(JSON, default=dict)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    process_batches: Mapped[list["ProcessBatch"]] = relationship(back_populates="black_mass_batch")


class Chemical(Base):
    __tablename__ = "chemicals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    formula: Mapped[str] = mapped_column(String(50))
    concentration_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=100)
    molecular_weight: Mapped[float] = mapped_column(Numeric(8, 3))
    unit: Mapped[ChemicalUnit] = mapped_column(Enum(ChemicalUnit))
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 4), default=0)
    hazard_class: Mapped[str] = mapped_column(String(100), default="")
    sds_document_url: Mapped[str] = mapped_column(String(500), default="")
    min_stock: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    max_stock: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    totes: Mapped[list["ChemicalTote"]] = relationship(back_populates="chemical")


class ChemicalTote(Base):
    __tablename__ = "chemical_totes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chemical_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chemicals.id")
    )
    lot_number: Mapped[str] = mapped_column(String(50), default="")
    capacity: Mapped[float] = mapped_column(Numeric(10, 2))
    current_level: Mapped[float] = mapped_column(Numeric(10, 2))
    unit: Mapped[ChemicalUnit] = mapped_column(Enum(ChemicalUnit))
    location: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[ToteStatus] = mapped_column(Enum(ToteStatus), default=ToteStatus.IN_STORAGE)
    connected_to_vessel: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_received: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    cam_lock_inspected: Mapped[bool] = mapped_column(Boolean, default=False)
    weather_protected: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")

    chemical: Mapped["Chemical"] = relationship(back_populates="totes")


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    batch_size_kg: Mapped[float] = mapped_column(Numeric(10, 2))
    target_nmc_ratio: Mapped[str] = mapped_column(String(20), default="6-2-2")
    h2so4_concentration_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=98)
    h2o2_concentration_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=34)
    naoh_concentration_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=25)
    nh4oh_concentration_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=19)
    dm_water_liters: Mapped[float] = mapped_column(Numeric(10, 2), default=3000)
    h2so4_kg: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    h2o2_liters: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[RecipeStatus] = mapped_column(Enum(RecipeStatus), default=RecipeStatus.DRAFT)
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    process_batches: Mapped[list["ProcessBatch"]] = relationship(back_populates="recipe")


class ProcessBatch(Base):
    __tablename__ = "process_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    recipe_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recipes.id"))
    black_mass_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("black_mass_batches.id")
    )
    black_mass_weight_kg: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[BatchStatus] = mapped_column(Enum(BatchStatus), default=BatchStatus.PRE_START)
    shift_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    plant_manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    forklift_operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    jsa_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    ppe_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="process_batches")
    black_mass_batch: Mapped["BlackMassBatch"] = relationship(back_populates="process_batches")
    steps: Mapped[list["ProcessStep"]] = relationship(
        back_populates="process_batch", order_by="ProcessStep.step_number"
    )
    lab_samples: Mapped[list["LabSample"]] = relationship(back_populates="process_batch")
    products: Mapped[list["Product"]] = relationship(back_populates="process_batch")
    gas_scrubber_logs: Mapped[list["GasScrubberLog"]] = relationship(
        back_populates="process_batch"
    )
    batch_cost: Mapped["BatchCost | None"] = relationship(back_populates="process_batch")


class ProcessStep(Base):
    __tablename__ = "process_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_batches.id")
    )
    vessel: Mapped[Vessel] = mapped_column(Enum(Vessel))
    step_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    responsible_role: Mapped[ResponsibleRole] = mapped_column(Enum(ResponsibleRole))
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), default=StepStatus.PENDING)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    recorded_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    estimated_duration_min: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")

    process_batch: Mapped["ProcessBatch"] = relationship(back_populates="steps")
    valve_positions: Mapped[list["ValvePosition"]] = relationship(back_populates="process_step")


class ValvePosition(Base):
    __tablename__ = "valve_positions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_steps.id")
    )
    valve_id: Mapped[str] = mapped_column(String(20))
    required_state: Mapped[ValveState] = mapped_column(Enum(ValveState))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    process_step: Mapped["ProcessStep"] = relationship(back_populates="valve_positions")


class LabSample(Base):
    __tablename__ = "lab_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    process_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_batches.id")
    )
    vessel: Mapped[Vessel] = mapped_column(Enum(Vessel))
    sample_point: Mapped[str] = mapped_column(String(20), default="")
    collected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    collected_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    ni_ppm: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    mn_ppm: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    co_ppm: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    li_ppm: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    ph: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    temperature_c: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    solution_volume_liters: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    notes: Mapped[str] = mapped_column(Text, default="")

    process_batch: Mapped["ProcessBatch"] = relationship(back_populates="lab_samples")
    dosage_calculations: Mapped[list["NMCDosageCalculation"]] = relationship(
        back_populates="lab_sample"
    )


class NMCDosageCalculation(Base):
    __tablename__ = "nmc_dosage_calculations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lab_sample_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lab_samples.id")
    )
    target_nmc_ratio: Mapped[str] = mapped_column(String(20))
    tolerance_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=5.0)
    decision: Mapped[NMCDecision] = mapped_column(Enum(NMCDecision))
    coso4_7h2o_kg: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    coso4_di_water_liters: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    mnso4_h2o_kg: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    mnso4_di_water_liters: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    nh4oh_liters: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    naoh_liters: Mapped[float] = mapped_column(Numeric(10, 3), default=0)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lab_sample: Mapped["LabSample"] = relationship(back_populates="dosage_calculations")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_type: Mapped[ProductType] = mapped_column(Enum(ProductType))
    process_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_batches.id")
    )
    weight_kg: Mapped[float] = mapped_column(Numeric(10, 2))
    moisture_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    purity_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    nmc_ratio: Mapped[str | None] = mapped_column(String(20), nullable=True)
    storage_location: Mapped[str] = mapped_column(String(100), default="")
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus), default=ProductStatus.COLLECTED
    )
    collected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    quality_grade: Mapped[str | None] = mapped_column(String(20), nullable=True)

    process_batch: Mapped["ProcessBatch"] = relationship(back_populates="products")


class MLDBatch(Base):
    __tablename__ = "mld_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    feed_source_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_batches.id"), nullable=True
    )
    status: Mapped[MLDBatchStatus] = mapped_column(
        Enum(MLDBatchStatus), default=MLDBatchStatus.STARTUP
    )
    start_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    seal_flush_pressure_bar: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    condensate_tank_level_mm: Mapped[float | None] = mapped_column(Numeric(7, 1), nullable=True)
    mvr_compressor_status: Mapped[str] = mapped_column(String(100), default="")
    crystallizer_status: Mapped[str] = mapped_column(String(100), default="")
    product_weight_kg: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    operation_logs: Mapped[list["MLDOperationLog"]] = relationship(back_populates="mld_batch")


class MLDOperationLog(Base):
    __tablename__ = "mld_operation_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mld_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mld_batches.id")
    )
    log_type: Mapped[MLDLogType] = mapped_column(Enum(MLDLogType))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    parameter: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(String(200))
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    mld_batch: Mapped["MLDBatch"] = relationship(back_populates="operation_logs")


class GasScrubberLog(Base):
    __tablename__ = "gas_scrubber_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_batches.id")
    )
    scrubber_id: Mapped[str] = mapped_column(String(20))
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ph_reading: Mapped[float] = mapped_column(Numeric(5, 2))
    airflow_status: Mapped[str] = mapped_column(String(100), default="")
    naoh_consumption_liters: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    operator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    process_batch: Mapped["ProcessBatch"] = relationship(back_populates="gas_scrubber_logs")


class BatchCost(Base):
    __tablename__ = "batch_costs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("process_batches.id"), unique=True
    )
    black_mass_cost_per_mt: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    black_mass_kg_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    water_cost_per_liter: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    water_liters_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    naoh_cost_per_liter: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    naoh_liters_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    h2so4_cost_per_liter: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    h2so4_liters_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    h2o2_cost_per_liter: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    h2o2_liters_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    caoh2_cost_per_lb: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    caoh2_lbs_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    coso4_cost_per_lb: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    coso4_lbs_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    mnso4_cost_per_lb: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    mnso4_lbs_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    nh4oh_cost_per_liter: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    nh4oh_liters_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    na2co3_cost_per_lb: Mapped[float] = mapped_column(Numeric(8, 4), default=0)
    na2co3_lbs_used: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    utility_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    labor_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    process_batch: Mapped["ProcessBatch"] = relationship(back_populates="batch_cost")


class MaintenanceInspection(Base):
    __tablename__ = "maintenance_inspections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_type: Mapped[InspectionFormType] = mapped_column(Enum(InspectionFormType))
    inspector_name: Mapped[str] = mapped_column(String(200))
    inspection_date: Mapped[date] = mapped_column(Date)
    last_inspection_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus), default=InspectionStatus.IN_PROGRESS
    )
    signature: Mapped[str] = mapped_column(String(500), default="")
    comments: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    items: Mapped[list["MaintenanceItem"]] = relationship(back_populates="inspection")
    work_orders: Mapped[list["MaintenanceWorkOrder"]] = relationship(back_populates="inspection")


class MaintenanceItem(Base):
    __tablename__ = "maintenance_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("maintenance_inspections.id")
    )
    category: Mapped[str] = mapped_column(String(100))
    item_description: Mapped[str] = mapped_column(Text)
    check_type: Mapped[CheckType] = mapped_column(Enum(CheckType))
    result: Mapped[str] = mapped_column(String(200), default="")
    requires_followup: Mapped[bool] = mapped_column(Boolean, default=False)
    followup_notes: Mapped[str] = mapped_column(Text, default="")

    inspection: Mapped["MaintenanceInspection"] = relationship(back_populates="items")


class MaintenanceWorkOrder(Base):
    __tablename__ = "maintenance_work_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_inspection_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("maintenance_inspections.id"), nullable=True
    )
    equipment: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[WorkOrderPriority] = mapped_column(Enum(WorkOrderPriority))
    status: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus), default=WorkOrderStatus.OPEN
    )
    assigned_to: Mapped[str] = mapped_column(String(200), default="")
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    parts_used: Mapped[list] = mapped_column(JSON, default=list)
    downtime_hours: Mapped[float] = mapped_column(Numeric(6, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    inspection: Mapped["MaintenanceInspection | None"] = relationship(
        back_populates="work_orders"
    )


class SparePart(Base):
    __tablename__ = "spare_parts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    applicable_equipment: Mapped[list] = mapped_column(JSON, default=list)
    min_stock: Mapped[int] = mapped_column(Integer, default=0)
    max_stock: Mapped[int] = mapped_column(Integer, default=0)
    current_stock: Mapped[int] = mapped_column(Integer, default=0)
    unit_cost: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)
    location: Mapped[str] = mapped_column(String(100), default="")
    last_ordered: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    quotes: Mapped[list["SparePartQuote"]] = relationship(back_populates="spare_part")


class SparePartQuote(Base):
    __tablename__ = "spare_part_quotes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spare_part_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("spare_parts.id")
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id")
    )
    quote_number: Mapped[str] = mapped_column(String(50), default="")
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[QuoteStatus] = mapped_column(Enum(QuoteStatus), default=QuoteStatus.REQUESTED)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    spare_part: Mapped["SparePart"] = relationship(back_populates="quotes")
    supplier: Mapped["Supplier"] = relationship(back_populates="spare_part_quotes")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id")
    )
    order_type: Mapped[OrderType] = mapped_column(Enum(OrderType))
    line_items: Mapped[list] = mapped_column(JSON, default=list)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[POStatus] = mapped_column(Enum(POStatus), default=POStatus.DRAFT)
    order_date: Mapped[date] = mapped_column(Date)
    expected_delivery: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_delivery: Mapped[date | None] = mapped_column(Date, nullable=True)
    precoro_po_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")
