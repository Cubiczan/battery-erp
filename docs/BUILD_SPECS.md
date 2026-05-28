# GreenLi-ion Battery Recycling ERP - Build Specifications

**Project:** Revamp of [codeberg.org/cubiczan/battery-erp](https://codeberg.org/cubiczan/battery-erp)  
**Target Platform:** AWS (funded via AWS grant)  
**Prepared by:** Shyam Desigan, Green Li-ion Inc.  
**Date:** 2026-05-20  
**Version:** 1.0  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State & Gap Analysis](#2-current-state--gap-analysis)
3. [GreenLi-ion Process Overview](#3-greenli-ion-process-overview)
4. [Functional Requirements](#4-functional-requirements)
5. [Domain Data Models](#5-domain-data-models)
6. [Business Rules Engine](#6-business-rules-engine)
7. [User Roles & Permissions](#7-user-roles--permissions)
8. [UI/UX Requirements](#8-uiux-requirements)
9. [AWS Architecture](#9-aws-architecture)
10. [API Specification](#10-api-specification)
11. [Integrations](#11-integrations)
12. [Non-Functional Requirements](#12-non-functional-requirements)
13. [Data Migration & Seeding](#13-data-migration--seeding)
14. [Testing Strategy](#14-testing-strategy)
15. [Deployment & DevOps](#15-deployment--devops)
16. [Phased Delivery Plan](#16-phased-delivery-plan)
17. [Appendices](#17-appendices)

---

## 1. Executive Summary

Green Li-ion operates a hydrometallurgical battery recycling facility in Atoka, Oklahoma. The plant processes lithium-ion battery black mass through two primary systems:

- **GLMC (Green Li-ion Metal Concentration):** A multi-vessel leaching and precipitation process that recovers nickel, manganese, cobalt (as NMC precursor), lithium carbonate, and graphite from black mass feedstock.
- **MLD (Mechanical Lithium Dissolution):** A crystallization system using Mechanical Vapor Recompression (MVR) to produce high-purity lithium salts.

The existing `battery-erp` repository is a Python-based ERP designed for battery **manufacturing** (cell/pack production). It must be completely reoriented to serve battery **recycling and hydrometallurgical processing**. The core domain shifts from cell chemistries and pack assembly to black mass processing, chemical dosing, vessel operations, filtration, precipitation, and product recovery.

### What to Keep from the Existing Repo

| Existing Module | Disposition | Rationale |
|---|---|---|
| `core/models.py` - Supplier, PurchaseOrder, InventoryRecord | **Adapt** | Supplier scoring and PO logic applies, but models need new fields for chemicals/black mass |
| `core/models.py` - RawMaterial | **Adapt** | Rename to `Chemical` with concentration, tote-level tracking |
| `core/models.py` - CellChemistry, BatteryCell, BatteryPack, BOMItem | **Remove** | Not applicable to recycling |
| `core/models.py` - ManufacturingBatch | **Replace** | Replace with `ProcessBatch` (GLMC) and `MLDBatch` (MLD) |
| `core/rules.py` - BOM cost rollups | **Replace** | Replace with per-batch cost tracking (chemicals + utilities + labor) |
| `core/rules.py` - Inventory management | **Adapt** | Apply to black mass, chemicals, spare parts, and products |
| `supply_chain` module | **Adapt** | Keep supplier scoring; add chemical vendor management |
| `pricing` module | **Replace** | Replace commodity pricing with chemical cost tracking and product pricing (NMC, Li2CO3, graphite) |
| `analytics` module | **Expand** | Add process analytics, yield tracking, maintenance dashboards |
| Microsoft Fabric integration | **Replace** | Replace with AWS Lambda + Bedrock + QuickSight/Athena |

### What to Build New

- Black mass inventory and composition tracking
- GLMC process execution engine (V-001 through V-004 with SOP step enforcement)
- Recipe calculator and NMC ratio engine
- MLD crystallization process tracking
- Lab sample management (ICP analysis)
- Maintenance inspection system (monthly forms for GLMC-1 and GLMLD-1)
- Spare parts management with three-quote procurement
- Environmental compliance tracking
- Batch costing and yield analysis
- Valve position tracking and checklist enforcement

---

## 2. Current State & Gap Analysis

### Existing Repository Architecture

```
battery-erp/
  src/battery_erp/
    core/
      models.py    # 10 dataclasses, 5 enums
      rules.py     # 8 business rule functions
    supply_chain/  # Supplier scoring, PO management, dual-sourcing
    pricing/       # Commodity prices, AlphaVantage/FRED integration
    analytics/     # Inventory, supply chain, manufacturing reports
  tests/           # 32 unit tests
  notebooks/       # AWS analytics (QuickSight, Athena)
```

### Gap Summary

| Capability | Existing Repo | GreenLi-ion Need |
|---|---|---|
| **Core domain** | Battery cell/pack manufacturing | Black mass recycling & hydrometallurgical processing |
| **Input tracking** | Raw materials (lithium, cobalt, nickel by weight) | Black mass (with full elemental composition), chemicals (H2SO4, H2O2, NaOH, NH4OH, CoSO4, MnSO4) with tote-level tracking |
| **Process control** | Manufacturing batch yield tracking | Multi-vessel SOP execution (V-001 leaching, V-002 separation, V-003 NMC precipitation, V-004 Li precipitation) with step-by-step operator guidance |
| **Lab integration** | None | ICP analysis, NMC ratio calculation, sample tracking |
| **Recipe management** | BOM calculation by cell chemistry | Dynamic recipe engine based on black mass composition |
| **MLD operations** | None | MVR system, crystallizer, condensate/seal water systems |
| **Maintenance** | None | Monthly inspection forms (GLMC-1, GLMLD-1), work orders, downtime logging |
| **Spare parts** | None | Parts catalog, min/max inventory, three-quote procurement |
| **Products** | Battery cells and packs | NMC precursor, lithium carbonate, graphite |
| **Compliance** | None | Environmental permits, HAZOP tracking, gas scrubber logs, wastewater monitoring |
| **Cloud platform** | Microsoft Fabric Lakehouse | AWS (Lambda, API Gateway, RDS, S3, Bedrock, QuickSight) |
| **UI** | None (library only) | Full web application with operator dashboards, process screens, inspection forms |

---

## 3. GreenLi-ion Process Overview

### 3.1 GLMC Process Flow

```
Black Mass Receiving
        |
        v
[Recipe Calculation] <-- Black mass composition analysis
        |                 (Co%, Ni%, Mn%, Li%, Al%, Fe%, Cu%)
        v
+------------------+
| V-001: Leaching  |  <- DM Water (3000L) + Black Mass (500kg batch)
|   H2SO4 (98%)    |     + H2SO4 dosing + H2O2 dosing
|   H2O2 (34%)     |     Steam heat to 70C, agitate, gas scrubber
|   Gas Scrubber I  |
+------------------+
        |
        v  (via Filter F-001)
+------------------+
| V-002: Separation|  <- Al/Fe/Cu removal via Ca(OH)2 precipitation
|   Ca(OH)2 dosing |     pH adjustment to 5.5-6.0
|   Filter F-002   |     Cake collection (impurities)
+------------------+     Filtrate -> V-003
        |
        v
+------------------+
| V-003: NMC       |  <- ICP analysis determines Ni:Mn:Co ratio
| Precipitation    |     CoSO4 + MnSO4 dosing to hit target ratio
|   CoSO4, MnSO4   |     NH4OH (19%) + NaOH (25%) for precipitation
|   NH4OH, NaOH    |     Target NMC ratios: 6-2-2, 8-1-1, etc.
+------------------+
        |
        v
+------------------+
| V-004: Lithium   |  <- Na2CO3 dosing for lithium carbonate precipitation
| Precipitation    |     Heat to 75C
|   Na2CO3         |     Filter F-004, hot water wash
|   Filter F-004   |     Product: Li2CO3
+------------------+
        |
        v
[Product Collection]
  - NMC Precursor (from V-003)
  - Lithium Carbonate (from V-004)
  - Graphite (from V-002 filter cake)
  - Wastewater (effluent from V-003/V-004)
```

### 3.2 MLD Process Flow

```
Feed Solution Input
        |
        v
[Seal Flush Water System]  <- P-0301A/B, pressure ~2bar
        |
        v
[Condensate Water System]  <- V-0202 tank, P-0202 pump
        |
        v
[MVR System]               <- Mechanical Vapor Recompression
        |                      Compressor, heat exchangers
        v
[Crystallizing System]     <- Crystallizer circulation pump
        |                      Belt tension monitoring
        v
[Product Recovery]         <- High-purity lithium salt crystals
```

### 3.3 Maintenance Workflow

**Monthly Inspections (two separate forms):**

- **GLMC-1 Form:** Hydraulic system, filter press (open/closed position), AODD pumps, agitators (oil level, bearing temps, motor grease), package/skid condition, electrical, automated valves
- **GLMLD-1 Form:** Electric motors (fans, bearings), pumps (on-line and off-line), crystallizer pump belts, tubing/conduit, foundation bolts, cooling tower, heat exchangers, skid washing

**Spare Parts Workflow:**
1. Identify failing or critical part
2. Request quotes from 3 sources
3. Set min/max stock levels with production team
4. Receive, inspect quality/quantity
5. Notify production + leadership
6. Enter in tracker + create PO/invoice in Precoro

---

## 4. Functional Requirements

### Module FR-01: Black Mass Management

| ID | Requirement | Priority |
|---|---|---|
| FR-01.1 | Register incoming black mass with batch/lot number, supplier, weight (by load cell), date received | P0 |
| FR-01.2 | Record elemental composition per batch: Co, Ni, Mn, Li, Al, Fe, Cu, F, P, Ti, Zn (as weight %) | P0 |
| FR-01.3 | Track storage location and current quantity per batch | P0 |
| FR-01.4 | Record consumption per process batch (link black mass batch to GLMC process batch) | P0 |
| FR-01.5 | Auto-calculate available inventory across all batches | P0 |
| FR-01.6 | Status tracking: Received, In Storage, In Process, Depleted | P1 |
| FR-01.7 | Blend tracking when multiple BM batches are combined | P1 |

### Module FR-02: Chemical Inventory & Tote Management

| ID | Requirement | Priority |
|---|---|---|
| FR-02.1 | Track chemicals: H2SO4 (98%), H2O2 (34%), NaOH (25%), NH4OH (19%), CoSO4*7H2O, MnSO4*H2O, Ca(OH)2, Na2CO3, soda ash | P0 |
| FR-02.2 | Tote-level tracking: lot number, current level/weight, connection status (connected/stored), location | P0 |
| FR-02.3 | Record tote connections and disconnections per process batch | P0 |
| FR-02.4 | Track consumption per batch via tote tank marking gauge readings | P0 |
| FR-02.5 | Min/max reorder points per chemical | P0 |
| FR-02.6 | Alert when sulfuric acid tote is exposed to rain or requires weather protection | P1 |
| FR-02.7 | Cam lock inspection log for sulfuric acid totes | P1 |
| FR-02.8 | Chemical cost per unit ($/liter, $/lb, $/kg) tracking | P0 |

### Module FR-03: Recipe Management & Calculation Engine

| ID | Requirement | Priority |
|---|---|---|
| FR-03.1 | Input: black mass composition (element percentages) and batch size (kg) | P0 |
| FR-03.2 | Auto-calculate H2SO4 dosage based on batch size and acid concentration | P0 |
| FR-03.3 | Auto-calculate H2O2 dosage based on batch size and peroxide concentration | P0 |
| FR-03.4 | Support configurable batch sizes: 500kg, 750kg, 1000kg | P0 |
| FR-03.5 | Support configurable acid concentrations: 50% and 98% H2SO4 | P0 |
| FR-03.6 | NMC ratio engine: given ICP results (Ni, Mn, Co in ppm) and V-003 volume, calculate required CoSO4 and MnSO4 additions to reach target NMC ratio (e.g., 6-2-2, 8-1-1) with configurable tolerance (default 5%) | P0 |
| FR-03.7 | Auto-calculate NH4OH and NaOH dosage for NMC precipitation | P0 |
| FR-03.8 | Recipe version control and approval workflow | P1 |
| FR-03.9 | "CONTINUE DOSING" / "SKIP THIS STEP" decision logic based on ICP results vs. target ratio | P0 |

### Module FR-04: GLMC Process Execution

| ID | Requirement | Priority |
|---|---|---|
| FR-04.1 | **Pre-Start Checklist:** JSA completion, PPE verification, air scrubber pH, spill kits, fire extinguishers, soda ash, valve positions, muster points | P0 |
| FR-04.2 | **Black Mass Preparation:** Select BM batch, record weight, stage empty tote, transfer required amount, label new bag, position on hopper | P0 |
| FR-04.3 | **Chemical Tote Setup:** PPE check, material handling procedure, tote valve verification, cam lock inspection (H2SO4), connection, labeling, fluid level measurement | P0 |
| FR-04.4 | **Utilities Startup:** Air compressor, connex fan, demin water system, dilution air regulator (45 psi) | P0 |
| FR-04.5 | **Valve Position Check:** Per-step valve open/close state for all systems: DM water, black mass, dilution air, gas scrubber, NaOH, H2SO4, H2O2, steam supply, cooling water | P0 |
| FR-04.6 | **V-001 Operations:** DM water dosage (3000L), NaOH pump start, agitator AG-001, BM dosage, gas scrubber I start, dilution air (XV-125), H2SO4 dosing (via P-401, metered by tote gauge), H2O2 dosing (via P-305), steam heating to 70C, 2-hour agitation, sampling | P0 |
| FR-04.7 | **V-002 Operations:** Transfer from V-001 via F-001, Ca(OH)2 dosing, pH monitoring (target 5.5-6.0), heating to 60C, 1-hour agitation, filtration via F-002, cake collection/weighing, air blowing, vessel washing | P0 |
| FR-04.8 | **V-003 Operations (NMC):** ICP sample submission, ratio calculation, CoSO4/MnSO4 dosing, NH4OH dosing, NaOH dosing for precipitation, heating to 55-60C, pH monitoring, agitation, product recovery | P0 |
| FR-04.9 | **V-004 Operations (Li Precipitation):** Na2CO3 dosing, heating to 75C, agitation, filtration via F-004, hot water washing (2500L at 75C), Li2CO3 cake collection | P0 |
| FR-04.10 | Per-step operator assignment (Plant Manager, Operator, Fork Lift Operator, All) | P0 |
| FR-04.11 | Per-step timestamp recording and completion checkbox | P0 |
| FR-04.12 | Per-step value recording (temperatures, pressures, levels, pH, weights) | P0 |
| FR-04.13 | Estimated time per step tracking vs actual duration | P1 |
| FR-04.14 | Abnormal condition alerts: temperature jumps, overpressure (PI readings), abnormal pump noise/vibration | P1 |
| FR-04.15 | Gas scrubber monitoring: pH, airflow, NaOH consumption rate | P1 |

### Module FR-05: MLD Process Execution

| ID | Requirement | Priority |
|---|---|---|
| FR-05.1 | Seal flush water system: pump P-0301A/B status, pressure (~2bar), valve positions (QV series), flow indicators | P0 |
| FR-05.2 | Condensate water system: V-0202 level (target 200mm initial), pump P-0202, recirculation valve QV0206 | P0 |
| FR-05.3 | MVR system: compressor status, heat exchanger monitoring | P0 |
| FR-05.4 | Crystallizing system: circulation pump belt tension, product recovery | P0 |
| FR-05.5 | Control panel status logging | P0 |
| FR-05.6 | CWS (Cooling Water System) operation log | P0 |
| FR-05.7 | MVR operation log | P0 |

### Module FR-06: Lab & Quality Management

| ID | Requirement | Priority |
|---|---|---|
| FR-06.1 | Record ICP analysis results per sample: Ni, Mn, Co concentrations (ppm) | P0 |
| FR-06.2 | Auto-calculate actual NMC molar ratios from ICP results | P0 |
| FR-06.3 | Link samples to process batch and vessel | P0 |
| FR-06.4 | Filter cake weight tracking per filtration step | P0 |
| FR-06.5 | Product quality records (NMC precursor purity, Li2CO3 grade, graphite moisture) | P1 |
| FR-06.6 | Sample chain of custody | P2 |

### Module FR-07: Product Inventory & Sales

| ID | Requirement | Priority |
|---|---|---|
| FR-07.1 | Track output products: NMC precursor, lithium carbonate, graphite (wet weight in kg) | P0 |
| FR-07.2 | Link products to source process batch | P0 |
| FR-07.3 | Storage location and status tracking | P0 |
| FR-07.4 | Yield calculation: input black mass weight vs. output product weights | P0 |
| FR-07.5 | Product pricing and sales order management | P1 |

### Module FR-08: Maintenance Management

| ID | Requirement | Priority |
|---|---|---|
| FR-08.1 | **GLMC-1 Monthly Inspection Form** (digital version): Fluid services, downtime log review, operator feedback, hydraulic inspection, filter press (open/closed), AODD pumps, agitators (oil level, bearing temps, motor grease), package/skid (bolts, sump drains, cleanliness, sight glasses, electrical, automated valves) | P0 |
| FR-08.2 | **GLMLD-1 Monthly Inspection Form** (digital version): Fluid services, downtime log review, operator feedback, electric motors (visual, operation, fans, bearings), pumps (on-line: leaks/noise/foaming/temps; off-line: fluid level/moisture), package (belt tension, tubing, mounts, cooling tower, skid wash), heat exchangers (pressure, plate fouling) | P0 |
| FR-08.3 | Per-item status: Check (X), N/A, or recorded value (e.g., "Dirty" for skid condition) | P0 |
| FR-08.4 | Inspector name, date, signature capture | P0 |
| FR-08.5 | Comments/problems/parts used free-text section | P0 |
| FR-08.6 | Downtime log for unscheduled maintenance events | P0 |
| FR-08.7 | Maintenance work order generation from inspection findings | P1 |
| FR-08.8 | Monthly schedule with due-date alerts and overdue notifications | P1 |

### Module FR-09: Spare Parts Management

| ID | Requirement | Priority |
|---|---|---|
| FR-09.1 | Spare parts catalog with part number, description, applicable equipment | P0 |
| FR-09.2 | Min/max stock levels per part (set collaboratively with production) | P0 |
| FR-09.3 | Three-quote procurement workflow: request, receive, compare, approve | P0 |
| FR-09.4 | Receiving inspection: quality and quantity verification | P0 |
| FR-09.5 | Notification to production and leadership when parts arrive | P1 |
| FR-09.6 | Integration with Precoro for PO and invoice creation | P1 |
| FR-09.7 | Parts usage tracking linked to maintenance work orders | P1 |

### Module FR-10: Batch Costing & Commercial

| ID | Requirement | Priority |
|---|---|---|
| FR-10.1 | Per-batch cost roll-up: black mass ($/mt), water ($/L), NaOH ($/L), H2SO4 ($/L), H2O2 ($/L), Ca(OH)2 ($/lb), CoSO4 ($/lb), MnSO4 ($/lb), NH4OH ($/L) | P0 |
| FR-10.2 | Actual chemical volumes/weights consumed per batch (from tote readings) | P0 |
| FR-10.3 | Utility costs: electricity, steam, compressed air | P1 |
| FR-10.4 | Labor cost allocation per batch | P2 |
| FR-10.5 | Cost per kg of each output product | P0 |
| FR-10.6 | Margin analysis: input cost vs product revenue | P1 |

### Module FR-11: Safety & Compliance

| ID | Requirement | Priority |
|---|---|---|
| FR-11.1 | JSA (Job Safety Analysis) completion log per shift | P0 |
| FR-11.2 | PPE verification checklist (suit, gloves, boots, respirator, gas monitor) | P0 |
| FR-11.3 | Gas scrubber pH and flow logging | P0 |
| FR-11.4 | Wastewater volume and discharge tracking | P1 |
| FR-11.5 | OKDEQ permit compliance tracking | P1 |
| FR-11.6 | HAZOP action item tracking (per 2301-222B HAZOP study) | P2 |
| FR-11.7 | Emergency Action Plan (EAP) acknowledgment tracking | P2 |
| FR-11.8 | Spill kit and fire extinguisher inspection log | P1 |

### Module FR-12: Supplier & Procurement

| ID | Requirement | Priority |
|---|---|---|
| FR-12.1 | Supplier profiles: name, contact, materials supplied, certifications, lead times | P0 |
| FR-12.2 | Composite supplier scoring (adapt existing: quality 35%, on-time delivery 35%, lead time 20%, certifications 10%) | P0 |
| FR-12.3 | Purchase order lifecycle: Draft -> Submitted -> Confirmed -> Shipped -> Delivered | P0 |
| FR-12.4 | Three-quote comparison for spare parts and chemicals | P0 |
| FR-12.5 | Dual-sourcing recommendations for critical chemicals (H2SO4, H2O2) | P1 |
| FR-12.6 | Precoro integration for PO/invoice sync | P1 |

---

## 5. Domain Data Models

### 5.1 Core Entities

```
BlackMassBatch
  - id: UUID
  - batch_number: string (unique, e.g., "BM-2026-0142")
  - lot_number: string
  - supplier_id: FK -> Supplier
  - date_received: datetime
  - gross_weight_kg: decimal
  - tare_weight_kg: decimal
  - net_weight_kg: decimal (computed)
  - storage_location: string
  - status: enum (RECEIVED, IN_STORAGE, IN_PROCESS, DEPLETED)
  - composition: JSON {Co: %, Ni: %, Mn: %, Li: %, Al: %, Fe: %, Cu: %, F: %, P: %, Ti: %, Zn: %}
  - notes: text
  - created_at, updated_at: datetime

Chemical
  - id: UUID
  - name: string (e.g., "Sulfuric Acid")
  - formula: string (e.g., "H2SO4")
  - concentration_pct: decimal (e.g., 98.0)
  - molecular_weight: decimal
  - unit: enum (KG, LITRE, LB)
  - unit_cost: decimal
  - hazard_class: string
  - sds_document_url: string
  - min_stock: decimal
  - max_stock: decimal
  - current_stock: decimal (computed from totes)

ChemicalTote
  - id: UUID
  - chemical_id: FK -> Chemical
  - lot_number: string
  - capacity: decimal
  - current_level: decimal
  - unit: enum (KG, LITRE)
  - location: string
  - status: enum (IN_STORAGE, CONNECTED, EMPTY, RETURNED)
  - connected_to_vessel: string (nullable, e.g., "V-001")
  - date_received: datetime
  - cam_lock_inspected: boolean (for H2SO4)
  - weather_protected: boolean (for H2SO4)
  - notes: text

Recipe
  - id: UUID
  - name: string (e.g., "Standard 500kg NMC-622")
  - batch_size_kg: decimal
  - target_nmc_ratio: string (e.g., "6-2-2")
  - h2so4_concentration_pct: decimal
  - h2o2_concentration_pct: decimal
  - naoh_concentration_pct: decimal
  - nh4oh_concentration_pct: decimal
  - dm_water_liters: decimal
  - h2so4_kg: decimal (calculated)
  - h2o2_liters: decimal (calculated)
  - version: integer
  - status: enum (DRAFT, APPROVED, ACTIVE, RETIRED)
  - approved_by: FK -> User
  - created_at, updated_at: datetime

ProcessBatch (GLMC)
  - id: UUID
  - batch_number: string (unique, e.g., "GLMC-2026-0087")
  - recipe_id: FK -> Recipe
  - black_mass_batch_id: FK -> BlackMassBatch
  - black_mass_weight_kg: decimal
  - status: enum (PRE_START, V001_ACTIVE, V002_ACTIVE, V003_ACTIVE, V004_ACTIVE, COMPLETE, ABORTED)
  - shift_date: date
  - start_time: datetime
  - end_time: datetime (nullable)
  - plant_manager: FK -> User
  - operator: FK -> User
  - forklift_operator: FK -> User
  - jsa_completed: boolean
  - ppe_verified: boolean
  - notes: text

ProcessStep
  - id: UUID
  - process_batch_id: FK -> ProcessBatch
  - vessel: enum (PRE_START, V001, V002, V003, V004, POST)
  - step_number: integer
  - description: text
  - responsible_role: enum (PLANT_MANAGER, OPERATOR, FORKLIFT_OPERATOR, ALL)
  - assigned_to: FK -> User
  - status: enum (PENDING, IN_PROGRESS, COMPLETED, SKIPPED, FLAGGED)
  - started_at: datetime (nullable)
  - completed_at: datetime (nullable)
  - recorded_value: string (nullable, for temperatures/pressures/levels/weights)
  - estimated_duration_min: integer
  - actual_duration_min: integer (computed)
  - notes: text

ValvePosition
  - id: UUID
  - process_step_id: FK -> ProcessStep
  - valve_id: string (e.g., "XV-110", "MV-462")
  - required_state: enum (OPEN, CLOSED)
  - verified: boolean
  - verified_by: FK -> User
  - verified_at: datetime

LabSample
  - id: UUID
  - sample_number: string
  - process_batch_id: FK -> ProcessBatch
  - vessel: enum (V001, V002, V003, V004)
  - sample_point: string (e.g., "MV-429")
  - collected_at: datetime
  - collected_by: FK -> User
  - ni_ppm: decimal (nullable)
  - mn_ppm: decimal (nullable)
  - co_ppm: decimal (nullable)
  - li_ppm: decimal (nullable)
  - ph: decimal (nullable)
  - temperature_c: decimal (nullable)
  - solution_volume_liters: decimal
  - calculated_ni_mol_per_l: decimal (computed)
  - calculated_mn_mol_per_l: decimal (computed)
  - calculated_co_mol_per_l: decimal (computed)
  - actual_nmc_ratio: string (computed, e.g., "7.6:1.0:1.4")
  - notes: text

NMCDosageCalculation
  - id: UUID
  - lab_sample_id: FK -> LabSample
  - target_nmc_ratio: string (e.g., "6-2-2")
  - tolerance_pct: decimal (default 5.0)
  - decision: enum (CONTINUE_DOSING, SKIP_STEP, WITHIN_TOLERANCE)
  - coso4_7h2o_kg: decimal
  - coso4_di_water_liters: decimal
  - mnso4_h2o_kg: decimal
  - mnso4_di_water_liters: decimal
  - nh4oh_liters: decimal
  - naoh_liters: decimal
  - calculated_at: datetime

Product
  - id: UUID
  - product_type: enum (NMC_PRECURSOR, LITHIUM_CARBONATE, GRAPHITE, WASTEWATER)
  - process_batch_id: FK -> ProcessBatch
  - weight_kg: decimal
  - moisture_pct: decimal (nullable)
  - purity_pct: decimal (nullable)
  - nmc_ratio: string (nullable, for NMC products)
  - storage_location: string
  - status: enum (COLLECTED, IN_STORAGE, SHIPPED, SOLD)
  - collected_at: datetime
  - quality_grade: string (nullable)

MLDBatch
  - id: UUID
  - batch_number: string
  - feed_source_batch_id: FK -> ProcessBatch (nullable)
  - status: enum (STARTUP, RUNNING, SHUTDOWN, COMPLETE)
  - start_time, end_time: datetime
  - operator: FK -> User
  - seal_flush_pressure_bar: decimal
  - condensate_tank_level_mm: decimal
  - mvr_compressor_status: string
  - crystallizer_status: string
  - product_weight_kg: decimal (nullable)
  - notes: text

MLDOperationLog
  - id: UUID
  - mld_batch_id: FK -> MLDBatch
  - log_type: enum (CWS, MVR)
  - timestamp: datetime
  - parameter: string
  - value: string
  - operator: FK -> User

MaintenanceInspection
  - id: UUID
  - form_type: enum (GLMC_1, GLMLD_1)
  - inspector_name: string
  - inspection_date: date
  - last_inspection_date: date (nullable)
  - status: enum (IN_PROGRESS, COMPLETED, REVIEWED)
  - signature: string (or image blob)
  - comments: text

MaintenanceItem
  - id: UUID
  - inspection_id: FK -> MaintenanceInspection
  - category: string (e.g., "Hydraulics Inspection", "AODD Pump Maintenance")
  - item_description: text
  - check_type: enum (CHECKBOX, VALUE, NA)
  - result: string (e.g., "X", "N/A", "Dirty", "125F")
  - requires_followup: boolean
  - followup_notes: text

MaintenanceWorkOrder
  - id: UUID
  - source_inspection_id: FK -> MaintenanceInspection (nullable)
  - equipment: string
  - description: text
  - priority: enum (CRITICAL, HIGH, MEDIUM, LOW)
  - status: enum (OPEN, IN_PROGRESS, PARTS_ORDERED, COMPLETE)
  - assigned_to: string
  - due_date: date
  - completed_date: date (nullable)
  - parts_used: JSON []
  - downtime_hours: decimal

SparePart
  - id: UUID
  - part_number: string
  - description: text
  - applicable_equipment: string[]
  - min_stock: integer
  - max_stock: integer
  - current_stock: integer
  - unit_cost: decimal
  - lead_time_days: integer
  - location: string
  - last_ordered: date (nullable)

SparePartQuote
  - id: UUID
  - spare_part_id: FK -> SparePart
  - supplier_id: FK -> Supplier
  - quote_number: string
  - unit_price: decimal
  - lead_time_days: integer
  - valid_until: date
  - status: enum (REQUESTED, RECEIVED, SELECTED, EXPIRED)

Supplier
  - id: UUID
  - name: string
  - contact_name: string
  - email: string
  - phone: string
  - address: text
  - materials_supplied: string[] (chemicals, black mass, spare parts)
  - quality_rating: decimal (0-100)
  - on_time_delivery_pct: decimal
  - avg_lead_time_days: integer
  - certifications: string[]
  - composite_score: decimal (computed)
  - status: enum (ACTIVE, INACTIVE, UNDER_REVIEW)

PurchaseOrder
  - id: UUID
  - po_number: string
  - supplier_id: FK -> Supplier
  - order_type: enum (CHEMICAL, BLACK_MASS, SPARE_PART)
  - line_items: JSON [{item, quantity, unit, unit_price, total}]
  - total_amount: decimal
  - status: enum (DRAFT, SUBMITTED, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)
  - order_date: date
  - expected_delivery: date
  - actual_delivery: date (nullable)
  - precoro_po_id: string (nullable, for sync)
  - notes: text

GasScrubberLog
  - id: UUID
  - process_batch_id: FK -> ProcessBatch
  - scrubber_id: string (e.g., "GS-I", "GS-II")
  - timestamp: datetime
  - ph_reading: decimal
  - airflow_status: string
  - naoh_consumption_liters: decimal
  - operator: FK -> User

BatchCost
  - id: UUID
  - process_batch_id: FK -> ProcessBatch
  - black_mass_batch_number: string
  - black_mass_cost_per_mt: decimal
  - black_mass_kg_used: decimal
  - water_cost_per_liter: decimal
  - water_liters_used: decimal
  - naoh_cost_per_liter: decimal
  - naoh_liters_used: decimal
  - h2so4_cost_per_liter: decimal
  - h2so4_liters_used: decimal
  - h2o2_cost_per_liter: decimal
  - h2o2_liters_used: decimal
  - caoh2_cost_per_lb: decimal
  - caoh2_lbs_used: decimal
  - coso4_cost_per_lb: decimal
  - coso4_lbs_used: decimal
  - mnso4_cost_per_lb: decimal
  - mnso4_lbs_used: decimal
  - nh4oh_cost_per_liter: decimal
  - nh4oh_liters_used: decimal
  - na2co3_cost_per_lb: decimal
  - na2co3_lbs_used: decimal
  - total_chemical_cost: decimal (computed)
  - utility_cost: decimal
  - labor_cost: decimal
  - total_batch_cost: decimal (computed)
  - cost_per_kg_nmc: decimal (computed)
  - cost_per_kg_li2co3: decimal (computed)

User
  - id: UUID
  - username: string
  - full_name: string
  - email: string
  - role: enum (ADMIN, PLANT_MANAGER, OPERATOR, FORKLIFT_OPERATOR, MAINTENANCE_TECH, LAB_TECH, PROCUREMENT, VIEWER)
  - is_active: boolean
```

### 5.2 Entity Relationship Diagram

```
BlackMassBatch ---< ProcessBatch >--- Recipe
                        |
                        |---< ProcessStep >---< ValvePosition
                        |
                        |---< LabSample ---< NMCDosageCalculation
                        |
                        |---< Product
                        |
                        |---< BatchCost
                        |
                        |---< GasScrubberLog
                        |
                        +--- MLDBatch ---< MLDOperationLog

Supplier ---< PurchaseOrder
    |
    +---< SparePartQuote >--- SparePart

MaintenanceInspection ---< MaintenanceItem
         |
         +---< MaintenanceWorkOrder

Chemical ---< ChemicalTote

User (referenced by all entities as operator/inspector/approver)
```

---

## 6. Business Rules Engine

### 6.1 Recipe Calculation Rules

**Rule R-01: H2SO4 Dosage Calculation**
```
Given: batch_size_kg, h2so4_concentration_pct
Calculate: h2so4_kg = f(batch_size_kg, concentration)

Lookup table (from SOP Data Entry sheet):
  batch_size=500kg, concentration=98% -> 1446.83 kg H2SO4
  batch_size=750kg, concentration=98% -> scaled proportionally
  batch_size=1000kg, concentration=98% -> scaled proportionally
  batch_size=500kg, concentration=50% -> 4582 kg (skip step flag)
```

**Rule R-02: H2O2 Dosage Calculation**
```
Given: batch_size_kg, h2o2_concentration_pct
Calculate: h2o2_liters = f(batch_size_kg, concentration)

Reference: batch_size=500kg, concentration=34% -> 279.41 liters
```

**Rule R-03: NMC Ratio Engine**
```
Given:
  - ICP results: Ni_ppm, Mn_ppm, Co_ppm
  - V-003 volume (liters)
  - Target NMC ratio (e.g., Ni:Mn:Co = 6:2:2)
  - Tolerance (default 5%)

Step 1: Convert ppm to g/L -> mol/L using molecular weights
  Ni: MW=58.69, Mn: MW=54.94, Co: MW=58.93

Step 2: Calculate actual molar ratios
  actual_ratio = [Ni_mol, Mn_mol, Co_mol] normalized to smallest

Step 3: Compare to target ratio within tolerance
  If within tolerance -> WITHIN_TOLERANCE (no dosing needed)
  If outside tolerance -> CONTINUE_DOSING

Step 4: Calculate required additions
  CoSO4*7H2O (kg) = f(Co_deficit_mol, V003_volume, MW_CoSO4_7H2O=281.1)
  DI water for CoSO4 = CoSO4_kg * 1.2 (dissolution ratio)
  MnSO4*H2O (kg) = f(Mn_deficit_mol, V003_volume, MW_MnSO4_H2O=169.0)
  DI water for MnSO4 = MnSO4_kg * 2.6 (dissolution ratio)
  NH4OH 19% (L) = f(total_metal_mol, stoichiometric_ratio)
  NaOH 25% (L) = f(total_metal_mol, stoichiometric_ratio)
```

**Rule R-04: Batch Cost Roll-Up**
```
Total batch cost = SUM of:
  - black_mass_kg * (black_mass_$/mt / 1000)
  - water_liters * water_$/L
  - naoh_liters * naoh_$/L
  - h2so4_liters * h2so4_$/L
  - h2o2_liters * h2o2_$/L
  - caoh2_lbs * caoh2_$/lb
  - coso4_lbs * coso4_$/lb
  - mnso4_lbs * mnso4_$/lb
  - nh4oh_liters * nh4oh_$/L
  - na2co3_lbs * na2co3_$/lb
  + utility_cost + labor_cost

Cost per kg product:
  cost_per_kg_nmc = total_batch_cost * allocation_pct / nmc_weight_kg
  cost_per_kg_li2co3 = total_batch_cost * allocation_pct / li2co3_weight_kg
```

### 6.2 Process Validation Rules

**Rule R-05: SOP Step Sequencing**
- Steps within each vessel must be completed in order
- Pre-start checklist must be 100% complete before V-001 can begin
- V-001 must reach "agitation complete" before transfer to V-002
- ICP results must be entered before V-003 dosing calculations are released
- V-004 temperature must reach 75C before filtration can begin

**Rule R-06: Valve State Enforcement**
- Before each process step, system displays required valve positions
- Operator must confirm each valve position before proceeding
- Conflicting valve states (e.g., both inlet and drain open) are blocked

**Rule R-07: Safety Interlocks (Soft)**
- Gas scrubber must be running before H2SO4 dosing
- PPE checklist must be verified before chemical handling steps
- Weather check alert when sulfuric acid tote is connected
- Dilution air must be confirmed before acid dosing

### 6.3 Inventory Rules

**Rule R-08: Chemical Reorder**
```
For each chemical:
  available = SUM(tote.current_level WHERE tote.status IN (IN_STORAGE, CONNECTED))
  IF available <= chemical.min_stock THEN trigger reorder alert
  suggested_order_qty = chemical.max_stock - available
```

**Rule R-09: Black Mass FIFO**
```
When assigning BM to a process batch:
  Select oldest batch with status=IN_STORAGE and quantity >= required_amount
  Decrement batch quantity
  If batch quantity reaches 0, set status=DEPLETED
```

**Rule R-10: Spare Parts Three-Quote Rule**
```
Before approving a spare part PO:
  COUNT(quotes WHERE spare_part_id = X AND status = RECEIVED) >= 3
  Selected quote must be justified (lowest cost OR documented reason for alternative)
```

### 6.4 Maintenance Rules

**Rule R-11: Monthly Inspection Scheduling**
```
For each equipment (GLMC-1, GLMLD-1):
  next_due = last_inspection_date + 30 days
  IF today > next_due THEN status = OVERDUE, send notification
  IF today > next_due - 7 THEN status = DUE_SOON, send reminder
```

**Rule R-12: Work Order Generation**
```
After inspection completion:
  FOR each item WHERE requires_followup = true:
    Auto-create MaintenanceWorkOrder with:
      description = item.description + item.followup_notes
      priority = based on item category (hydraulic/electrical = HIGH, cosmetic = LOW)
      source_inspection_id = inspection.id
```

### 6.5 Yield & Analytics Rules

**Rule R-13: Batch Yield Calculation**
```
metal_recovery_pct = (output_metal_kg / input_metal_kg) * 100

Where:
  input_metal_kg = black_mass_kg * (element_pct / 100)
  output_metal_kg derived from product weights and compositions

Track per-batch and rolling average trends
```

**Rule R-14: Supplier Composite Score**
```
score = (quality_rating * 0.35) + (on_time_delivery_pct * 0.35) +
        ((100 - normalized_lead_time) * 0.20) + (certification_score * 0.10)

Rank suppliers per material category (chemicals, black mass, spare parts)
```

---

## 7. User Roles & Permissions

| Role | Process | Lab | Maintenance | Procurement | Admin |
|---|---|---|---|---|---|
| **Admin** | Full | Full | Full | Full | Full |
| **Plant Manager** | Execute + approve + view all | View | View + approve | Approve POs | User management |
| **Operator** | Execute assigned steps, record values | Submit samples | Submit requests | View | None |
| **Forklift Operator** | Execute material handling steps | None | Submit requests | View | None |
| **Lab Technician** | View process status | Full (enter ICP, trigger calcs) | None | None | None |
| **Maintenance Tech** | View | None | Full (inspect, create WOs, manage parts) | Request parts | None |
| **Procurement** | View batch costs | None | View parts needs | Full (POs, suppliers, quotes) | None |
| **Viewer** | Read-only dashboards | Read-only | Read-only | Read-only | None |

---

## 8. UI/UX Requirements

### 8.1 Layout

- **Responsive web application** (desktop-first, tablet-compatible for plant floor use)
- **Left sidebar navigation** with module icons
- **Top bar** with user info, notifications bell, active batch indicator
- **Dark/light mode** (plant floor visibility in varying lighting)

### 8.2 Key Screens

**Dashboard (Home)**
- Active GLMC batch status with current vessel highlighted
- Active MLD batch status
- Chemical inventory levels (bar chart with min/max lines)
- Black mass inventory summary
- Overdue maintenance alerts
- Low-stock spare parts alerts
- Recent batch yields trend chart

**Process Execution Screen (GLMC)**
- Left panel: Process flow diagram showing V-001 through V-004 with current step highlighted
- Center panel: Current step details with:
  - Step description
  - Responsible role and assigned operator
  - Value input fields (temperature, pressure, level, pH, weight)
  - Valve position checklist with open/close toggles
  - Timer (estimated vs elapsed)
  - "Complete Step" button
  - "Flag Issue" button
- Right panel: Batch summary (BM batch, recipe, start time, running costs)

**Recipe Calculator Screen**
- Input: Black mass composition entry (element percentages)
- Input: Batch size selector (500/750/1000 kg)
- Output: Calculated chemical dosages with "Create Batch" button
- NMC tab: ICP result entry -> auto-calculated ratios -> dosage recommendations

**Lab Results Screen**
- ICP entry form with auto-calculation of molar ratios
- Visual NMC ratio indicator (actual vs target with tolerance band)
- Dosing recommendation: CONTINUE DOSING / SKIP / WITHIN TOLERANCE
- History of samples per batch

**Maintenance Inspection Forms**
- Digital replica of GLMC-1 and GLMLD-1 paper forms
- Checkbox grids with category headers
- Value entry fields where applicable (temperatures, conditions)
- Comments section
- Digital signature capture
- "Generate Work Orders" button for flagged items

**Inventory Screens**
- Black Mass: batch list with composition sparklines, searchable, filterable
- Chemicals: tote list grouped by chemical, level indicators, connection status
- Spare Parts: parts grid with stock vs min/max visual, reorder actions
- Products: output inventory with link back to source batch

**Supplier & Procurement Screens**
- Supplier scorecard with composite scoring breakdown
- PO pipeline with Kanban-style status view
- Three-quote comparison table for spare parts

**Reports & Analytics**
- Batch cost breakdown (stacked bar by cost category)
- Yield trends over time
- Chemical consumption per batch
- Maintenance compliance (inspections on-time vs late)
- Supplier performance trends

---

## 9. AWS Architecture

### 9.1 Architecture Diagram

```
                         [Route 53]
                             |
                         [CloudFront]
                             |
                    +--------+--------+
                    |                 |
              [S3 - Static]    [API Gateway (HTTP)]
              (React SPA)          |
                              [AWS Lambda]
                              (Python FastAPI via Mangum)
                                   |
                    +--------------+--------------+-----------+
                    |              |              |           |
              [RDS PostgreSQL] [ElastiCache] [S3 - Docs]  [Bedrock]
              (Primary DB)     (Redis)       (SOPs,       (Claude-powered
                    |          (sessions,     reports,      process assistant,
                    |           caching)      signatures)   recipe advisor,
                    |                                       SOP Q&A)
              [RDS Read Replica]
                    |
              [QuickSight / Athena]
              (Analytics & Dashboards)

  [Cognito] ---- Authentication
  [SES] -------- Email notifications
  [SNS/SQS] ---- Event-driven notifications
  [CloudWatch] - Monitoring & logging
  [Secrets Manager] - API keys, DB credentials
  [IoT Core] --- (Future: sensor integration)
```

### 9.2 Service Selection Rationale

| Service | Purpose | Justification |
|---|---|---|
| **AWS Lambda** | API backend (serverless functions) | Zero idle cost; auto-scaling; FastAPI via Mangum adapter; pay-per-request ideal for shift-based plant operations |
| **API Gateway (HTTP)** | API management & Lambda trigger | Low-latency HTTP routing; rate limiting; request validation; API keys for integrations |
| **Amazon Bedrock** | AI-powered process assistant | Claude model for SOP Q&A, recipe optimization suggestions, anomaly detection in ICP results, natural-language batch status queries |
| **RDS PostgreSQL** | Relational database | Complex joins across process batches, lab results, costs; JSONB for flexible composition data; proven for ERP workloads |
| **ElastiCache (Redis)** | Session store, caching | Fast session lookup for plant floor users; cache recipe calculations and dashboard queries |
| **S3** | Static hosting + document storage | React SPA hosting via CloudFront; SOPs, inspection signatures, lab reports stored durably |
| **CloudFront** | CDN | Low-latency SPA delivery; HTTPS termination |
| **Cognito** | Authentication | User pools for plant staff; role-based access; MFA for admin/manager roles |
| **QuickSight** | BI dashboards | Cost-effective analytics; embedded dashboards; connects directly to RDS |
| **SES** | Email | Maintenance reminders, reorder alerts, inspection due notifications |
| **SNS/SQS** | Event messaging | Decouple notifications from API; batch completion events trigger cost calculations |
| **CloudWatch** | Observability | Logs, metrics, alarms for Lambda invocations and batch processing |
| **Secrets Manager** | Credentials | Database passwords, Precoro API keys, Bedrock configuration, no hardcoded secrets |
| **IoT Core** | Future sensor integration | Temperature probes, pressure transmitters, pH meters when SCADA integration is ready |

### 9.3 Sizing Estimates (Initial)

| Resource | Size | Notes |
|---|---|---|
| Lambda | 512 MB memory, 30s timeout | Provisioned concurrency: 5 for shift hours; scales automatically |
| API Gateway | HTTP API | Lower latency and cost vs REST API; sufficient for ERP |
| Bedrock (Claude) | On-demand | ~100-200 queries/day for process assistant, SOP Q&A |
| RDS PostgreSQL | db.t3.medium (2 vCPU, 4GB) | Multi-AZ for production |
| RDS Storage | 100 GB gp3 | ~2-3 batches/day, growing slowly |
| RDS Proxy | Included | Required for Lambda→RDS connection pooling |
| ElastiCache | cache.t3.micro | Session store + light caching |
| S3 | Pay-per-use | Documents: ~10GB/year estimated |
| CloudFront | Standard distribution | Minimal traffic |

### 9.4 Estimated Monthly AWS Cost

| Service | Estimated Monthly Cost |
|---|---|
| Lambda (provisioned concurrency + on-demand) | ~$35 |
| API Gateway (HTTP API) | ~$5 |
| Bedrock (Claude, ~5K requests/month) | ~$50 |
| RDS PostgreSQL (db.t3.medium, Multi-AZ) | ~$130 |
| RDS Proxy | ~$15 |
| ElastiCache (cache.t3.micro) | ~$15 |
| S3 + CloudFront | ~$5 |
| Cognito (< 50 users) | Free tier |
| SES (< 1000 emails/month) | ~$1 |
| CloudWatch | ~$10 |
| Secrets Manager | ~$2 |
| **Total estimated** | **~$270/month** |

*Note: These are rough estimates. Actual costs depend on usage patterns. Lambda costs significantly lower than ECS Fargate during off-shift hours (zero idle cost). Reserved instances can reduce RDS costs by ~40%.*

---

## 10. API Specification

### 10.1 Technology Stack

| Layer | Technology | Rationale |
|---|---|---|
| **API Framework** | Python 3.12 + FastAPI + Mangum | Async support, auto-generated OpenAPI docs, type hints; Mangum adapts FastAPI for Lambda |
| **ORM** | SQLAlchemy 2.0 + Alembic | Mature, well-documented, handles complex queries; Alembic for migrations |
| **Validation** | Pydantic v2 | FastAPI native; strict type validation; JSON schema generation |
| **AI/LLM** | Amazon Bedrock (Claude) + LangChain | Process assistant, SOP Q&A, recipe optimization, anomaly alerts |
| **Testing** | pytest + httpx | Async test client; existing repo uses pytest |
| **Auth** | Cognito JWT tokens | Verified in FastAPI middleware |
| **Task queue** | SQS + Lambda (event-driven) | Async cost calculations, report generation, notification dispatch (no Celery needed with Lambda) |

### 10.2 API Endpoints (RESTful)

```
# Black Mass Management
POST   /api/v1/black-mass                    # Register new batch
GET    /api/v1/black-mass                    # List batches (filterable)
GET    /api/v1/black-mass/{id}               # Get batch details + composition
PUT    /api/v1/black-mass/{id}               # Update batch
PATCH  /api/v1/black-mass/{id}/consume       # Record consumption by process batch

# Chemical & Tote Management
GET    /api/v1/chemicals                     # List chemicals with stock levels
POST   /api/v1/chemicals/totes               # Register new tote
PATCH  /api/v1/chemicals/totes/{id}/connect  # Connect tote to vessel
PATCH  /api/v1/chemicals/totes/{id}/level    # Update tote level reading
GET    /api/v1/chemicals/reorder-alerts      # Get chemicals below min stock

# Recipe Management
POST   /api/v1/recipes                       # Create recipe
GET    /api/v1/recipes                       # List recipes
POST   /api/v1/recipes/calculate             # Calculate dosages from composition
POST   /api/v1/recipes/{id}/approve          # Approve recipe

# GLMC Process Execution
POST   /api/v1/batches                       # Create new process batch
GET    /api/v1/batches                       # List batches (filterable by status, date)
GET    /api/v1/batches/{id}                  # Full batch detail with steps
GET    /api/v1/batches/{id}/steps            # Get all steps for batch
PATCH  /api/v1/batches/{id}/steps/{step_id}  # Complete/update a step
POST   /api/v1/batches/{id}/steps/{step_id}/valves  # Verify valve positions
POST   /api/v1/batches/{id}/flag             # Flag abnormal condition
GET    /api/v1/batches/{id}/cost             # Get running batch cost

# Lab & NMC Calculations
POST   /api/v1/lab/samples                   # Submit lab sample
GET    /api/v1/lab/samples                   # List samples
POST   /api/v1/lab/nmc-calculate             # Calculate NMC dosing from ICP results
GET    /api/v1/lab/samples/{id}/dosage       # Get dosage recommendation

# MLD Operations
POST   /api/v1/mld/batches                   # Create MLD batch
PATCH  /api/v1/mld/batches/{id}              # Update MLD batch status
POST   /api/v1/mld/batches/{id}/logs         # Add operation log entry

# Products
POST   /api/v1/products                      # Register product output
GET    /api/v1/products                      # List products
GET    /api/v1/products/yield-summary        # Yield analysis

# Maintenance
POST   /api/v1/maintenance/inspections       # Create inspection
GET    /api/v1/maintenance/inspections       # List inspections
PUT    /api/v1/maintenance/inspections/{id}  # Update inspection items
POST   /api/v1/maintenance/inspections/{id}/complete  # Complete + auto-create WOs
GET    /api/v1/maintenance/work-orders       # List work orders
PATCH  /api/v1/maintenance/work-orders/{id}  # Update work order status

# Spare Parts
GET    /api/v1/spare-parts                   # List parts with stock levels
POST   /api/v1/spare-parts/quotes            # Submit quote
GET    /api/v1/spare-parts/{id}/quotes       # Compare quotes (3-quote view)
POST   /api/v1/spare-parts/{id}/reorder      # Create PO from best quote

# Suppliers & Procurement
GET    /api/v1/suppliers                     # List with composite scores
POST   /api/v1/suppliers                     # Add supplier
GET    /api/v1/suppliers/{id}/scorecard      # Detailed scoring breakdown
POST   /api/v1/purchase-orders               # Create PO
GET    /api/v1/purchase-orders               # List POs (Kanban states)
PATCH  /api/v1/purchase-orders/{id}/status   # Advance PO status

# Safety & Compliance
POST   /api/v1/safety/jsa                    # Log JSA completion
POST   /api/v1/safety/gas-scrubber           # Log scrubber reading
GET    /api/v1/safety/compliance-status      # Dashboard data

# Analytics & Reports
GET    /api/v1/analytics/batch-costs         # Cost analysis across batches
GET    /api/v1/analytics/yields              # Yield trends
GET    /api/v1/analytics/chemical-usage      # Chemical consumption trends
GET    /api/v1/analytics/maintenance-compliance  # Inspection timeliness
GET    /api/v1/analytics/supplier-performance    # Supplier trend data

# Users & Auth
POST   /api/v1/auth/login                   # Cognito auth
GET    /api/v1/users/me                     # Current user profile
GET    /api/v1/users                        # List users (admin only)
```

---

## 11. Integrations

### 11.1 Precoro (Procurement)

| Feature | Direction | Method |
|---|---|---|
| Sync POs created in ERP to Precoro | ERP -> Precoro | REST API |
| Sync invoice status from Precoro | Precoro -> ERP | Webhook or polling |
| Match PO to invoice | Bidirectional | PO number cross-reference |

**Priority:** P1 (post-MVP). Initially, POs are managed in ERP with manual Precoro entry.

### 11.2 Future Integrations

| System | Purpose | Priority |
|---|---|---|
| **SCADA/PLC** | Real-time temperature, pressure, pH, level readings from vessels | P2 |
| **IoT sensors** | Tote level sensors, gas scrubber pH probes | P2 |
| **QuickBooks/Xero** | Financial accounting sync | P2 |
| **SharePoint** | SOP document management (existing MLD SOP lives on SharePoint) | P2 |
| **Email/SMS** | Maintenance alerts, reorder notifications | P1 (via SES/SNS) |

---

## 12. Non-Functional Requirements

### 12.1 Performance

| Metric | Target |
|---|---|
| API response time (P95) | < 500ms |
| Dashboard load time | < 3 seconds |
| Recipe calculation | < 1 second |
| NMC dosage calculation | < 1 second |
| Concurrent users | 15-20 (plant staff) |

### 12.2 Availability

| Metric | Target |
|---|---|
| Uptime | 99.5% (plant operates Monday-Friday shifts) |
| RDS Multi-AZ failover | < 5 minutes |
| Data backup | Daily automated snapshots, 30-day retention |
| RPO (Recovery Point Objective) | < 1 hour |
| RTO (Recovery Time Objective) | < 4 hours |

### 12.3 Security

| Requirement | Implementation |
|---|---|
| Authentication | AWS Cognito with MFA for admin/manager roles |
| Authorization | Role-based access control (RBAC) per Section 7 |
| Data encryption at rest | RDS encryption, S3 SSE-S3 |
| Data encryption in transit | TLS 1.2+ everywhere |
| Secrets management | AWS Secrets Manager (no hardcoded credentials) |
| Audit logging | CloudTrail + application-level audit log (who changed what, when) |
| Network isolation | VPC with private subnets for RDS/Lambda; API Gateway as public entry point; RDS Proxy for connection pooling |
| Input validation | Pydantic models on all API inputs |
| SQL injection prevention | SQLAlchemy parameterized queries (no raw SQL) |

### 12.4 Data Retention

| Data Type | Retention |
|---|---|
| Process batch records | 7 years (regulatory) |
| Lab results | 7 years |
| Maintenance inspections | 5 years |
| Financial/cost data | 7 years |
| Audit logs | 3 years |
| User sessions | 30 days |

---

## 13. Data Migration & Seeding

### 13.1 Seed Data (from SOPs)

| Data | Source | Action |
|---|---|---|
| Chemical catalog (H2SO4, H2O2, NaOH, etc.) | GLMC 1.0 Operating SOP | Seed table with formulas, MW, concentrations, hazard classes |
| Valve registry | GLMC 1.0 Operating SOP (V-001 through V-004 sections) | Seed all XV-xxx, MV-xxx valves with associated vessel |
| Process step templates | Start-up SOP Structure sheet | Seed step sequences for each vessel |
| GLMC-1 inspection items | GLMC-1 Monthly Maintenance form | Seed 35+ inspection line items with categories |
| GLMLD-1 inspection items | GLMLD-1 Monthly Maintenance form | Seed 25+ inspection line items with categories |
| Spare parts SOP workflow | Spare Parts SOP | Configure procurement workflow rules |
| Black mass composition template | Black Mass Inventory Template | Seed elemental composition fields |
| NMC calculation parameters | NMC sheet (molecular weights, dissolution ratios) | Seed calculation engine constants |

### 13.2 Migration from Existing Battery-ERP

No data migration required from the existing repo; it contains only code structure and sample data for battery manufacturing. The models and business rules will be rewritten per this spec.

---

## 14. Testing Strategy

### 14.1 Test Pyramid

| Level | Scope | Target Coverage | Tools |
|---|---|---|---|
| **Unit** | Business rules (recipe calc, NMC engine, cost roll-up, valve validation) | 90%+ | pytest |
| **Integration** | API endpoints, database queries, auth flows | 80%+ | pytest + httpx + testcontainers (PostgreSQL) |
| **E2E** | Critical user flows (create batch, execute steps, enter lab results, complete inspection) | Key flows | Playwright |
| **Load** | API under concurrent load (15-20 users) | P95 < 500ms | Locust |

### 14.2 Critical Test Scenarios

1. **Recipe calculation accuracy:** Given known BM composition, verify H2SO4/H2O2 dosages match SOP reference values
2. **NMC ratio engine:** Given known ICP results, verify CoSO4/MnSO4 calculations match the NMC spreadsheet
3. **Process step sequencing:** Verify steps cannot be completed out of order
4. **Valve conflict detection:** Verify conflicting valve states are rejected
5. **Batch cost roll-up:** Verify total matches sum of components
6. **Inventory depletion:** Verify BM and chemical inventories decrement correctly
7. **Maintenance auto-WO:** Verify flagged inspection items generate work orders
8. **Three-quote enforcement:** Verify PO approval blocked without 3 quotes for spare parts
9. **Role-based access:** Verify operators cannot access admin functions
10. **Concurrent batch execution:** Verify two batches can run simultaneously without data leakage

---

## 15. Deployment & DevOps

### 15.1 CI/CD Pipeline

```
GitHub Actions (or AWS CodePipeline)
  |
  +-- On PR: lint (ruff) -> type check (mypy) -> unit tests -> integration tests
  |
  +-- On merge to main: package Lambda zip/layer -> deploy to staging via SAM/CDK
  |
  +-- On release tag: promote staging Lambda version to production alias
```

### 15.2 Infrastructure as Code

| Tool | Scope |
|---|---|
| **AWS CDK** (or **SAM/Terraform**) | VPC, Lambda, API Gateway, RDS, RDS Proxy, S3, CloudFront, Cognito, Bedrock, IAM roles |
| **Docker** | Local development image (Python + FastAPI); Lambda layer packaging |
| **Alembic** | Database migrations (versioned, reversible) |

### 15.3 Environments

| Environment | Purpose | AWS Account Strategy |
|---|---|---|
| **Development** | Local development with Docker Compose (PostgreSQL + Redis + API) | N/A (local) |
| **Staging** | Pre-production validation, mirrors production architecture | Same or separate AWS account |
| **Production** | Live plant operations | Dedicated AWS account recommended |

---

## 16. Phased Delivery Plan

### Phase 1: Foundation & Core Process (Weeks 1-8)

**Deliverables:**
- AWS infrastructure provisioned (VPC, Lambda, API Gateway, RDS, RDS Proxy, S3, Cognito)
- User authentication and RBAC
- Black mass management (FR-01)
- Chemical inventory and tote tracking (FR-02)
- Recipe calculation engine (FR-03)
- GLMC process execution for V-001 and V-002 (FR-04.1 through FR-04.7)
- Basic dashboard

**Exit Criteria:** Operator can register black mass, calculate a recipe, and execute V-001/V-002 steps with value recording.

### Phase 2: Full GLMC + Lab Integration (Weeks 9-14)

**Deliverables:**
- V-003 NMC precipitation with ICP integration (FR-04.8)
- V-004 lithium precipitation (FR-04.9)
- Lab sample management and NMC ratio engine (FR-06)
- Product output tracking (FR-07)
- Batch costing (FR-10)
- Process analytics dashboards

**Exit Criteria:** End-to-end GLMC batch from black mass to product collection with full cost tracking.

### Phase 3: MLD + Maintenance (Weeks 15-20)

**Deliverables:**
- MLD process execution (FR-05)
- GLMC-1 digital maintenance inspection form (FR-08.1)
- GLMLD-1 digital maintenance inspection form (FR-08.2)
- Work order generation (FR-08.7)
- Spare parts management (FR-09)
- Maintenance scheduling and alerts

**Exit Criteria:** Maintenance tech can complete monthly inspections digitally; work orders auto-generated.

### Phase 4: Procurement + Integrations + Polish (Weeks 21-26)

**Deliverables:**
- Supplier management with scoring (FR-12)
- Three-quote procurement workflow
- Precoro integration (FR-09.6, FR-12.6)
- Safety and compliance tracking (FR-11)
- QuickSight embedded dashboards
- Email notifications (SES)
- Performance optimization and load testing
- User training documentation

**Exit Criteria:** Full system operational with all modules, integrations, and reporting.

### Total Timeline Estimate: 26 weeks (6 months)

**Team Recommendation:**
- 1 Backend Engineer (Python/FastAPI, senior)
- 1 Frontend Engineer (React/TypeScript, senior)
- 1 Full-stack Engineer (junior-mid, assist both sides)
- 1 DevOps/Cloud Engineer (AWS, part-time or shared)
- 1 QA Engineer (part-time, ramp in Phase 2)
- 1 Project Manager

---

## 17. Appendices

### Appendix A: Chemical Reference Data

| Chemical | Formula | MW | Concentration | Unit | Hazard |
|---|---|---|---|---|---|
| Sulfuric Acid | H2SO4 | 98.08 | 98% (also 50%) | L, kg | Corrosive |
| Hydrogen Peroxide | H2O2 | 34.01 | 34% | L | Oxidizer |
| Sodium Hydroxide | NaOH | 40.00 | 25% | L | Corrosive |
| Ammonium Hydroxide | NH4OH | 35.05 | 19% | L | Corrosive, toxic gas |
| Cobalt Sulfate Heptahydrate | CoSO4*7H2O | 281.10 | Solid | kg | Toxic |
| Manganese Sulfate Monohydrate | MnSO4*H2O | 169.02 | Solid | kg | Irritant |
| Calcium Hydroxide | Ca(OH)2 | 74.09 | Solid | lb | Irritant |
| Sodium Carbonate | Na2CO3 | 105.99 | Solid | lb | Irritant |
| Soda Ash | Na2CO3 | 105.99 | Solid | lb | Irritant |

### Appendix B: Vessel & Equipment Registry

| Equipment ID | Type | System | Notes |
|---|---|---|---|
| V-001 | Leaching Vessel | GLMC | H2SO4 + H2O2 leaching |
| V-002 | Separation Vessel | GLMC | Ca(OH)2 impurity removal |
| V-003 | NMC Precipitation Vessel | GLMC | Metal salt adjustment + precipitation |
| V-004 | Li Precipitation Vessel | GLMC | Na2CO3 lithium recovery |
| F-001 | Filter Press | GLMC | V-001 to V-002 transfer |
| F-002 / F-002A | Filter Press | GLMC | V-002 separation, cake collection |
| F-004 | Filter Press | GLMC | V-004 Li2CO3 recovery |
| AG-001 | Agitator | GLMC V-001 | |
| AG-002 | Agitator | GLMC V-002 | |
| AG-003 | Agitator | GLMC V-003 | |
| AG-004 | Agitator | GLMC V-004 | |
| P-001 | Transfer Pump | GLMC | V-001 discharge |
| P-002 | Transfer Pump | GLMC | V-002 discharge |
| P-004 | Transfer Pump | GLMC | V-004 discharge |
| P-305 | H2O2 Feed Pump | GLMC | VFD controlled, 40Hz |
| P-401 | H2SO4 Feed Pump | GLMC | VFD controlled, 12-50Hz ramp |
| GS-I | Gas Scrubber I | GLMC | NaOH circulation |
| V-0202 | Condensate Tank | MLD | |
| P-0202 | Condensate Pump | MLD | |
| P-0301A/B | Seal Flush Pump | MLD | ~2bar discharge |

### Appendix C: Key Valve Registry (Partial)

| Valve ID | System | Location | Type |
|---|---|---|---|
| XV-101 | GLMC V-001 | BM rotary airlock | Isolation |
| XV-102 | GLMC V-001 | H2O2 supply | Isolation |
| XV-109 | GLMC V-001 | H2SO4 dosing | Isolation |
| XV-110 | GLMC V-001 | DM water supply | Isolation |
| XV-125 | GLMC V-001 | Dilution air | Isolation |
| XV-205 | GLMC V-002 | DM water supply | Isolation |
| XV-208 | GLMC V-002 | P-002 inlet | Isolation |
| XV-210 | GLMC V-002 | P-002 start | Control |
| XV-211 | GLMC V-002 | Filtration | Isolation |
| XV-213 | GLMC V-002 | 3-way valve | Diverter (recirculate vs V-003) |
| XV-222-226 | GLMC V-002 | Various | Filtration circuit |
| XV-401 | GLMC V-004 | P-004 inlet | Isolation |
| XV-402 | GLMC V-004 | Air supply to P-004 | Isolation |
| XV-404 | GLMC V-004 | 3-way valve | Diverter (recirculate vs wastewater) |
| XV-405 | GLMC V-004 | Wastewater outlet | Isolation |
| XV-408-417 | GLMC V-004 | Various | Filtration circuit |
| MV-462 | GLMC V-001 | NaOH recirculation | Manual |
| MV-466 | GLMC V-001 | H2SO4 recirculation | Manual |
| MV-429 | GLMC V-004 | Sample point | Manual |
| QV0301/0304 | MLD | Soft water supply | Manual |
| SV-0301A/B | MLD | Soft water solenoid | Auto |
| QV0313/307 | MLD | Pump recirculation | Manual |

### Appendix D: Molecular Weight Constants for NMC Calculations

| Element/Compound | MW (g/mol) |
|---|---|
| Ni | 58.69 |
| Mn | 54.94 |
| Co | 58.93 |
| Li | 6.94 |
| CoSO4*7H2O | 281.10 |
| MnSO4*H2O | 169.02 |

### Appendix E: SOP Source Documents

| Document | Location | Sheets/Sections |
|---|---|---|
| GLMC 1.0 Operating SOP.xlsx | Updated SOP's folder | Rev Control, Start-up SOP Structure, Data Entry, V-001, V-002, NMC, V-003, Lithium Pre, V-004, Commercial |
| User Manual of MLD (EC Config.).xlsx | Updated SOP's folder | Seal Flush Water, Condensate Water, MVR System, Crystallizing System, Control Panel, Pic_1, Pic_2, Operation, Warning, LOG(CWS), LOG(MVR) |
| Black_Mass_Inventory_Template.xlsx | Updated SOP's folder | Black Mass Inventory |
| GLMC-1 Monthly Maintenance Inspection Form.xlsx | Updated SOP's folder | A Service |
| GLMLD-1 Monthly Maintenance Inspection Form.xlsx | Updated SOP's folder | EN8399 |
| SOP Spare Parts.xlsx | Updated SOP's folder | Sheet1 |

---

*This document is confidential and proprietary to Green Li-ion Inc. Distribution is limited to authorized development partners under NDA.*

*Copyright 2026 Shyam Desigan, Green Li-ion Inc. All rights reserved.*
