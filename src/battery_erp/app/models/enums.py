import enum


class BlackMassStatus(str, enum.Enum):
    RECEIVED = "received"
    IN_STORAGE = "in_storage"
    IN_PROCESS = "in_process"
    DEPLETED = "depleted"


class ChemicalUnit(str, enum.Enum):
    KG = "kg"
    LITRE = "litre"
    LB = "lb"


class ToteStatus(str, enum.Enum):
    IN_STORAGE = "in_storage"
    CONNECTED = "connected"
    EMPTY = "empty"
    RETURNED = "returned"


class RecipeStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    RETIRED = "retired"


class BatchStatus(str, enum.Enum):
    PRE_START = "pre_start"
    V001_ACTIVE = "v001_active"
    V002_ACTIVE = "v002_active"
    V003_ACTIVE = "v003_active"
    V004_ACTIVE = "v004_active"
    COMPLETE = "complete"
    ABORTED = "aborted"


class Vessel(str, enum.Enum):
    PRE_START = "pre_start"
    V001 = "v001"
    V002 = "v002"
    V003 = "v003"
    V004 = "v004"
    POST = "post"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FLAGGED = "flagged"


class ResponsibleRole(str, enum.Enum):
    PLANT_MANAGER = "plant_manager"
    OPERATOR = "operator"
    FORKLIFT_OPERATOR = "forklift_operator"
    ALL = "all"


class ValveState(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class ProductType(str, enum.Enum):
    NMC_PRECURSOR = "nmc_precursor"
    LITHIUM_CARBONATE = "lithium_carbonate"
    GRAPHITE = "graphite"
    WASTEWATER = "wastewater"


class ProductStatus(str, enum.Enum):
    COLLECTED = "collected"
    IN_STORAGE = "in_storage"
    SHIPPED = "shipped"
    SOLD = "sold"


class NMCDecision(str, enum.Enum):
    CONTINUE_DOSING = "continue_dosing"
    SKIP_STEP = "skip_step"
    WITHIN_TOLERANCE = "within_tolerance"


class MLDBatchStatus(str, enum.Enum):
    STARTUP = "startup"
    RUNNING = "running"
    SHUTDOWN = "shutdown"
    COMPLETE = "complete"


class MLDLogType(str, enum.Enum):
    CWS = "cws"
    MVR = "mvr"


class InspectionFormType(str, enum.Enum):
    GLMC_1 = "glmc_1"
    GLMLD_1 = "glmld_1"


class InspectionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"


class CheckType(str, enum.Enum):
    CHECKBOX = "checkbox"
    VALUE = "value"
    NA = "na"


class WorkOrderPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WorkOrderStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PARTS_ORDERED = "parts_ordered"
    COMPLETE = "complete"


class QuoteStatus(str, enum.Enum):
    REQUESTED = "requested"
    RECEIVED = "received"
    SELECTED = "selected"
    EXPIRED = "expired"


class OrderType(str, enum.Enum):
    CHEMICAL = "chemical"
    BLACK_MASS = "black_mass"
    SPARE_PART = "spare_part"


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class SupplierStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PLANT_MANAGER = "plant_manager"
    OPERATOR = "operator"
    FORKLIFT_OPERATOR = "forklift_operator"
    MAINTENANCE_TECH = "maintenance_tech"
    LAB_TECH = "lab_tech"
    PROCUREMENT = "procurement"
    VIEWER = "viewer"
