# Green Li-ion Recycling ERP

**Hydrometallurgical battery recycling process management system for Green Li-ion Inc., Atoka, Oklahoma.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-50%20passing-brightgreen)](tests/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![AWS](https://img.shields.io/badge/AWS-Lambda%20%2B%20Bedrock-FF9900)](https://aws.amazon.com/)

---

## What This Is

A purpose-built ERP for **lithium-ion battery black mass recycling** via hydrometallurgical processing. Manages the full plant workflow from black mass receiving through chemical leaching, metal precipitation, and product recovery. Every process step, chemical dose, lab result, and cost is tracked to the batch level.

Built from the actual Standard Operating Procedures (SOPs) used at the Green Li-ion GLMC and MLD facilities.

---

## Process Overview

```
Black Mass Receiving          Chemical Tote Setup
       |                            |
       v                            v
+------------------+    +----------------------+
| Recipe Calculator |<---| Composition Analysis |
| (H2SO4/H2O2      |    | (Co%, Ni%, Mn%, Li%) |
|  dosing per SOP)  |    +----------------------+
+--------+---------+
         |
         v
+-----------------------------------------------------+
|  V-001: LEACHING                                     |
|  DM Water (3000L) + Black Mass (500kg batch)         |
|  4 dosing cycles: H2SO4 + H2O2 + 50L water rinse    |
|  Agitation at 54Hz, gas scrubber monitoring           |
+-----------------------------------------------------+
         |  Filter Press F-001
         v
+-----------------------------------------------------+
|  V-002: SEPARATION                                   |
|  Ca(OH)2 dosing for impurity removal                 |
|  NaOH pH adjustment to 5.0-5.2 (22 dosing rounds)   |
|  Filter Press F-002 -> filtrate to V-003             |
+-----------------------------------------------------+
         |  ICP Lab Analysis
         v
+-----------------------------------------------------+
|  V-003: NMC PRECIPITATION                            |
|  ICP results -> molar ratio calculation              |
|  CoSO4*7H2O / MnSO4*H2O additions to target 6:2:2  |
|  NH4OH + NaOH for metal precipitation                |
|  Output: NMC precursor (Ni-Mn-Co hydroxide)          |
+-----------------------------------------------------+
         |
         v
+-----------------------------------------------------+
|  V-004: LITHIUM PRECIPITATION                        |
|  Na2CO3 addition for Li2CO3 recovery                 |
|  Filter Press F-004                                  |
|  Output: Lithium carbonate                           |
+-----------------------------------------------------+
         |
         v
+-----------------------------------------------------+
|  MLD CRYSTALLIZATION (separate system)               |
|  MVR compressor, crystallizer, seal flush water      |
|  Output: High-purity lithium salts                   |
+-----------------------------------------------------+
```

**Products:** NMC precursor, lithium carbonate, graphite (from F-001 filter cake)

---

## Functional Modules

| Module | Description |
|---|---|
| **Black Mass Inventory** | FIFO tracking with elemental composition (Co, Ni, Mn, Li, Al, Fe, Cu) |
| **Chemical Inventory** | Tote-level tracking for H2SO4, H2O2, NaOH, NH4OH, CoSO4, MnSO4, Ca(OH)2, Na2CO3 |
| **Recipe Calculator** | Scales SOP reference values (500kg/98% H2SO4 -> 1446.83kg) for any batch size |
| **NMC Ratio Engine** | ICP ppm -> molar ratios -> CoSO4/MnSO4 dosage to hit target 6:2:2 ratio |
| **Process Execution** | 68 SOP steps (Pre-Start -> V-001 -> V-002) with role assignment and sequential enforcement |
| **Valve Validation** | 22 valves tracked across V-001, V-002, V-004 with conflict detection |
| **Lab Samples** | ICP analysis entry with auto-calculated molar ratios and dosage recommendations |
| **Batch Costing** | 10-chemical cost rollup + utilities + labor per the SOP Commercial sheet |
| **Maintenance** | Digital GLMC-1 (27 items) and GLMLD-1 (22 items) monthly inspection forms |
| **Work Orders** | Auto-generated from flagged inspection items with priority routing |
| **Spare Parts** | Three-quote procurement workflow per SOP Spare Parts procedure |
| **Supplier Scoring** | Composite score: quality 35%, OTD 35%, lead time 20%, certifications 10% |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API** | Python 3.12, FastAPI, Pydantic v2 |
| **ORM** | SQLAlchemy 2.0, Alembic migrations |
| **Database** | PostgreSQL 16 |
| **Cloud** | AWS Lambda (via Mangum), API Gateway, RDS, S3, Cognito |
| **AI** | Amazon Bedrock (Claude) for process assistant and SOP Q&A |
| **Local Dev** | Docker Compose (PostgreSQL + Redis + API) |
| **Testing** | pytest (50 tests covering all business rules) |
| **Linting** | ruff, mypy (strict) |

---

## Project Structure

```
battery-erp/
  src/battery_erp/
    app/
      api/                  # FastAPI routers
        black_mass.py       #   POST/GET/PUT/PATCH black mass batches
        chemicals.py        #   GET chemicals, POST totes, reorder alerts
        recipes.py          #   POST calculate, POST create, POST approve
        process.py          #   POST batches, GET steps, PATCH step completion
        lab.py              #   POST samples, POST nmc-calculate, GET dosage
      models/
        enums.py            # 20+ enums (BatchStatus, Vessel, ValveState, ...)
        domain.py           # 22 SQLAlchemy models (User -> PurchaseOrder)
      rules/                # Pure business logic (no DB dependencies)
        recipe.py           #   H2SO4/H2O2 dosing from SOP reference values
        nmc.py              #   ICP -> molar ratios -> dosage calculations
        valve.py            #   Valve registry, conflict detection
        costing.py          #   Batch cost rollup, yield calculation
        inventory.py        #   FIFO selection, reorder alerts
        maintenance.py      #   Inspection scheduling, work order generation
        supplier.py         #   Composite scoring, three-quote check
      schemas/              # Pydantic v2 request/response models
      seed/                 # SOP-derived reference data
        chemicals.py        #   9 chemicals from SOP Appendix A
        process_steps.py    #   68 process step templates
        inspection_items.py #   GLMC-1 (27) + GLMLD-1 (22) inspection items
        runner.py           #   Database seeder
      config.py             # pydantic-settings (ERP_ prefix)
      main.py               # FastAPI app with 5 routers
      lambda_handler.py     # AWS Lambda entry point (Mangum)
      db/
        base.py             # SQLAlchemy DeclarativeBase
        session.py          # Engine, SessionLocal, get_db()
  alembic/
    versions/
      0001_initial_schema.py  # All 22 tables
  tests/
    test_recycling_erp.py     # 50 unit tests
  Dockerfile
  docker-compose.yml
  pyproject.toml
  alembic.ini
```

---

## Quick Start

### Local Development (Docker)

```bash
git clone https://codeberg.org/cubiczan/battery-erp.git
cd battery-erp
git checkout recycling-erp-phase1

# Start PostgreSQL + Redis + API
docker compose up -d

# API available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

### Without Docker

```bash
pip install -e ".[dev]"

# Set database URL
export ERP_DATABASE_URL=postgresql://erp:erp@localhost:5432/battery_erp

# Run migrations
alembic upgrade head

# Start API
uvicorn battery_erp.app.main:app --reload
```

### Run Tests

```bash
pip install -e ".[dev]"
pytest tests/test_recycling_erp.py -v
# 50 passed -- recipe calc, NMC engine, valve conflicts, costing, inventory, maintenance, supplier scoring
```

---

## API Endpoints

```
# Health
GET    /health

# Black Mass Management
POST   /api/v1/black-mass                     # Register new batch
GET    /api/v1/black-mass                     # List (filterable by status)
GET    /api/v1/black-mass/{id}                # Detail + composition
PUT    /api/v1/black-mass/{id}                # Update
PATCH  /api/v1/black-mass/{id}/consume        # Record consumption

# Chemical & Tote Management
GET    /api/v1/chemicals                      # List with computed stock levels
POST   /api/v1/chemicals/totes                # Register tote
PATCH  /api/v1/chemicals/totes/{id}/connect   # Connect to vessel
PATCH  /api/v1/chemicals/totes/{id}/level     # Update level
GET    /api/v1/chemicals/reorder-alerts       # Below-min-stock alerts

# Recipe Management
POST   /api/v1/recipes/calculate              # Pure calculation (no persist)
POST   /api/v1/recipes                        # Create recipe
GET    /api/v1/recipes                        # List
POST   /api/v1/recipes/{id}/approve           # Approve

# GLMC Process Execution
POST   /api/v1/batches                        # Create batch (auto-seeds 68 steps)
GET    /api/v1/batches                        # List
GET    /api/v1/batches/{id}                   # Detail
GET    /api/v1/batches/{id}/steps             # All steps
PATCH  /api/v1/batches/{id}/steps/{step_id}   # Complete step (sequential enforcement)

# Lab & NMC Calculations
POST   /api/v1/lab/samples                    # Submit ICP sample
GET    /api/v1/lab/samples                    # List samples
POST   /api/v1/lab/nmc-calculate              # Calculate NMC dosage
GET    /api/v1/lab/samples/{id}/dosage        # Dosage recommendation + persist
```

---

## Key Business Rules (from SOPs)

| Rule | Description |
|---|---|
| **Recipe Scaling** | Linear from SOP reference: 500kg batch -> 1446.83 kg H2SO4 (98%), 279.41 L H2O2 (34%) |
| **4-Step Dosing** | H2SO4 and H2O2 split into 4 equal dosing rounds per V-001 SOP |
| **NMC Target** | 6:2:2 Ni:Mn:Co molar ratio with 5% tolerance band |
| **Step Sequencing** | Process steps enforced in order; pre-start must complete before V-001 |
| **Valve Conflicts** | XV-213/XV-212 (diverter), XV-109/MV-466 (acid), XV-102/XV-109 (dual dosing) blocked |
| **FIFO Inventory** | Oldest black mass batch consumed first |
| **Chemical Reorder** | Alert when stock <= min_stock; critical when stock = 0 |
| **30-Day Inspection** | Monthly maintenance due; 7-day reminder; overdue tracking |
| **Three-Quote Rule** | Spare part POs require 3 quotes minimum |
| **Supplier Scoring** | Composite: quality 35% + OTD 35% + lead time 20% + certs 10% -> A/B/C/D grade |

---

## AWS Architecture (Production)

```
CloudFront -> API Gateway (HTTP) -> AWS Lambda (FastAPI via Mangum)
                                        |
                    +-------------------+-------------------+
                    |                   |                   |
              RDS PostgreSQL      ElastiCache         Amazon Bedrock
              (via RDS Proxy)       (Redis)         (Claude - SOP Q&A,
                                                    recipe advisor)

Cognito (auth) | SES (email alerts) | SNS/SQS (events) | S3 (docs/SOPs)
```

---

## SOP Source Documents

| Document | Content |
|---|---|
| GLMC 1.0 Operating SOP.xlsx | Start-up procedure, V-001 through V-004 steps, recipe calculator, NMC sheet, commercial costs |
| User Manual of MLD (EC Config.).xlsx | MVR system, crystallizer, seal flush, condensate water |
| GLMC-1 Monthly Maintenance Inspection Form.xlsx | 27 inspection items across 6 categories |
| GLMLD-1 Monthly Maintenance Inspection Form.xlsx | 22 inspection items across 5 categories |
| Black_Mass_Inventory_Template.xlsx | Batch tracking template |
| SOP Spare Parts.xlsx | 6-step procurement workflow |

---

## License

MIT. See [LICENSE](LICENSE).

Copyright 2026 Shyam Desigan, Green Li-ion Inc. All rights reserved.
