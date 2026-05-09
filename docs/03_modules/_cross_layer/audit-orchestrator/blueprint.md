---
module_id: "MOD-INF-027"
title: "Audit Master Controller — Three-Subsystem Architecture v4.0.0"
doc_type: blueprint
status: Draft
version: "4.0.0"
generation: 5
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-08"
valid_from: "2026-05-08"
ttl: permanent
construction_progress: not_started
belongs_to: "MOD-MASTER-001"
summary: "ZephyrAlpha audit orchestrator blueprint v4.0.0 - MAPE-K five-layer architecture for multi-dimensional iterative audit"
tags: [audit, orchestrator, multi-dimensional, iterative, convergence, governance, self-healing, ai-driven, cross-cutting, orphan-judgment, semantic-audit, red-blue-adversarial, git-backup, chaos-engineering, mape-k, trae, roo-code, api-automation, incremental-audit, meta-audit, observability, telemetry, cron-scheduler, circuit-breaker, plugin-architecture, agent-skill, dora-metrics, compliance-mapping, disaster-recovery]
priority: P1
depends_on:
  - target: "MOD-INF-007"
    at: "full"
    why: "Gate Engine"
  - target: "MOD-INF-017"
    at: "full"
    why: "Code Dedup Engine"
  - target: "MOD-INF-020"
    at: "full"
    why: "Audit Trail"
  - target: "MOD-INF-023"
    at: "section 2"
    why: "Drift Detector"
  - target: "MOD-INF-026"
    at: "full"
    why: "Asset Inventory"
  - target: "MOD-INF-028"
    at: "full"
    why: "SemanticAuditor peer service"
  - target: "MOD-INF-033"
    at: "full"
    why: "BehavioralAuditor peer service"
  - target: "MOD-INF-029"
    at: "full"
    why: "Orphan Judge"
  - target: "MOD-INF-030"
    at: "full"
    why: "RedBlue Validator"
  - target: "MOD-INF-031"
    at: "full"
    why: "AutoFix Engine"
  - target: "MOD-INF-010"
    at: "section 2"
    why: "Feedback Loop"
  - target: "MOD-INF-018"
    at: "section 3"
    why: "Agent RBAC"
  - target: "MOD-INF-014"
    at: "section 3"
    why: "LLM Security"
  - target: "MOD-INF-015"
    at: "section 2"
    why: "System Telemetry"
references:
  - id: "MOD-INF-005"
    at: "full"
    why: "Script System"
  - id: "MOD-INF-006"
    at: "section 1"
    why: "Task System"
  - id: "MOD-INF-009"
    at: "section 2"
    why: "Pipeline"
  - id: "MOD-INF-019"
    at: "section 3"
    why: "Agent Spec"
---

## DOM-GOV-001 集成契约锚点

> 权威定义�?[`../../_domain-governance/blueprint.md`](../../_domain-governance/blueprint.md) §3�?
| 契约 ID | 本模块角�?| 对端模块 |
|---------|------------|----------|
| G-CT-001 | 消费方（读取 RBAC 策略校验审计权限�?| MOD-INF-018 Agent RBAC |
| G-CT-007 | 消费方（读取 Agent Spec 校验审计行为规范�?| MOD-INF-019 Agent Spec |
| G-CT-003 | 生产方（推送审计遥测数据） | MOD-INF-015 System Telemetry |
| G-CT-004 | producer (pushes audit telemetry data) | MOD-INF-015 System Telemetry |

---

## v4.0.0 Architecture Refactoring — Total Audit System Design

> **This section is the definitive architecture document for the ZephyrAlpha total audit system. It supersedes any older subsystem/subsidiary relationship descriptions. The Orchestrator is no longer a "parent" of audit subsystems — it is the master coordinator of three peer audit services.**

### Three-Subsystem Audit Architecture

```
                    ZephyrAlpha Total Audit System
                              │
              ┌───────────────┼───────────────┐
              │               │               │
     ┌────────▼────────┐ ┌───▼──────────┐ ┌──▼──────────────┐
     │ Structural Audit │ │Semantic Audit│ │ Behavioral Audit│
     │ (Orchestrator    │ │(MOD-INF-028) │ │ (MOD-INF-033)   │
     │  internal engine)│ │ Peer Service │ │ Belongs to 027  │
     │                  │ │              │ │                 │
     │ 19 dimensions    │ │ F + G only   │ │ BH-001~005      │
     │ 100% deterministic│ │ LLM Bridge   │ │ AuditTrail+Drift│
     │ Rule engine      │ │ 95~98% cert. │ │ Block+Alert+Rb  │
     └────────┬─────────┘ └───┬──────────┘ └──┬──────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Repair Pipeline   │
                    │ OrphanJudge→AutoFix │
                    │ →RedBlue→Rollback   │
                    └────────────────────┘
```

### Boundary Table

| Audit Type | Input | Judgment | Determinism | LLM Dependency | Fix Method |
|------------|-------|----------|:----------:|:-------------:|------------|
| **Structural** | Any file (.py/.yaml/.md) | Boolean: `exists()`/`∈`/`==`/`<` | 100% | Zero | Template |
| **Semantic** | Rule documents only (.md/.yaml) | Natural language semantics | 95~98% | Core | LLM generated |
| **Behavioral** | AI action logs (AuditTrail) | Auth boundary vs actual behavior | High | Optional | Block/alert/rollback |

### Orchestrator's New Role — Master Controller / Triage Scheduler

```
Phase 1 DISCOVER: "What changed?"
  → AssetInventory reports mtime changes

Phase 2 TRIAGE & SCHEDULE: "Which subsystem handles this?"
  → .py/.yaml changed → Structural Audit (internal 19 dims)
  → Rule document changed → Structural Audit + dispatch SemanticAuditor (peer)
  → AuditTrail anomaly event → Behavioral Audit

Phase 3 REPAIR COORDINATE: "How to fix?"
  → Structural RED → AutoFix (template repair)
  → Semantic RED → Human confirm → LLM generates fix text
  → Behavioral RED → Block + alert

Phase 4 ENFORCE & CLOSE: "Is it really fixed?"
  → RedBlue adversarial validation
  → Convergence detection (N consecutive zero-issue runs)
  → Broken → Rollback
```

### SemanticAuditor Elevation (v3.0.0 → v4.0.0)

- `belongs_to` changed from `"MOD-INF-027"` to `null` — independent peer module
- DIM-SEMANTIC-001 removed from Orchestrator dimensions
- Relationship: Orchestrator `references` SemanticAuditor (not `depends_on` as subsystem)
- Coordinated via: Orchestrator Phase 2 dispatches to SemanticAuditor when rule documents change
- Cross-reference: [SemanticAuditor v4.0.0 blueprint](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/semantic-auditor/blueprint.md) §1.5 ontology boundary

### BehavioralAuditor Definition (New)

| Property | Value |
|----------|-------|
| **What it audits** | AI behavior — what the AI actually did vs what it was authorized to do |
| **Data source** | MOD-INF-020 AuditTrail (immutable cryptographic event log) |
| **Detection** | MOD-INF-023 DriftDetector (behavioral boundary comparison) |
| **Triggers** | AuditTrail anomaly events, boundary violation signals |
| **Response** | Block unauthorized actions, alert human, rollback via MOD-INF-021 |
| **Status** | **[Blueprint v1.0.0](file:///D:/ZephyrAlpha/docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md)** — MOD-INF-033. Composed from MOD-INF-020 + MOD-INF-023 + MOD-INF-007 + MOD-INF-021 infrastructure. 5 triggers (BH-001~005), 4 protection levels (anchor/protected/normal/public), Block+Alert+Rollback response model. |

### Why Only Three Types?

| Candidate Audit Type | Why Not Independent | Where It Lives |
|----------------------|--------------------|----------------|
| Asset audit | Subset of structural — find file → determine ownership | DIM-TYPE-001~003 + OrphanJudge |
| Code audit | Subset of structural — AST analysis = deterministic rules | DIM-CODE-001 + DIM-SECURITY-001 |
| Dependency audit | Subset of structural — ID lookup = deterministic rules | DIM-DEP-001 |
| Scale audit | Subset of structural — numeric comparison = deterministic rules | DIM-SCALE-001 |
| ADR audit | Subset of structural — file existence check | DIM-ADR-001 |
| Construction audit | Subset of structural — status field comparison | DIM-CONSTRUCTION-001 |
| Runtime audit | Not audit — monitoring. Owned by System Telemetry | MOD-INF-015 |
| Knowledge audit | Not audit — self-check. Owned by VectorMemory | MOD-INF-0XX |

---

## Dimension Provider Registry — Existing Scripts Integrated into Audit System

> **This section registers all existing ZephyrAlpha governance/validation scripts into the Audit Orchestrator v4.0.0 as Dimension Providers. These scripts already exist and run independently — the Orchestrator does NOT replace them, it orchestrates them as a unified audit pipeline. Each provider is mapped to one or more structural audit dimensions with its full filesystem path.**

### Provider Table — Script → Dimension Mapping

#### DIM-PATH-001: File Path Enforcement

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d1_structure/detect_orphan_py.py` | Detect .py files in project root (not in 3 legal dirs) — AI session leftover garbage | P0 | 0=pass, 1=findings, 2=error |
| `scripts/governance/d4_paths/detect_ruins_references.py` | Detect references to deprecated/abandoned paths (ABS-44) | P0 | 0=pass, 1=findings, 2=error |
| `scripts/governance/verify_file_paths.py` | Validate 21+ file type mandatory paths | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_directory_structure.py` | Validate project directory tree matches LPC dual-track | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_nested_flat_dirs.py` | Detect nested vs flat directory violations | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_blueprint_placement.py` | Validate blueprint files are in correct layer directories | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/blueprint/validate_blueprint_path_consistency.py` | Blueprint path ↔ module-registry path consistency | P1 | 0=pass, 1=findings |

#### DIM-TYPE-001~003: Registration Completeness & Gate Integrity

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/audit_registration.py` | AST-based __all__ extraction — detect unexported modules | P0 | 0=pass, 1=findings, 2=error |
| `scripts/governance/check_registry_consistency.py` | Cross-registry consistency: module-registry ↔ blueprint-registry ↔ actual files | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_ssot.py` | Single Source of Truth validation across all registries | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_gate_yaml.py` | Gate YAML format and ID existence validation | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_blind_spot_status.py` | Blind spot registry status audit | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_authority_registry.py` | Authority registry completeness | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_field_ownership.py` | Field ownership registration audit | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/yaml_md/validate_yaml_interface_uniqueness.py` | YAML interface ID uniqueness | P1 | 0=pass, 1=findings |

#### DIM-CODE-001: Code Construction Standards

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/fix_orphan_exports.py` | Detect/fix Python modules not exported by parent __init__.py (RULE-TWO defense 2) | P0 | 0=pass, 1=fixed, 2=error |
| `scripts/governance/d1_structure/detect_residual_files.py` | Detect orphan shells, stale imports, duplicate files, legacy tests | P0 | 0=pass, 1=findings, 2=error |
| `scripts/governance/d7_code/validate_init_all.py` | Validate __init__.py exports all public modules | P0 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_import_style.py` | Validate import style conventions | P0 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_python_syntax.py` | Python syntax validation (compile check) | P0 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_type_annotation_coverage.py` | Type annotation coverage audit | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_docstring_coverage.py` | Docstring coverage audit | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_test_coverage.py` | Test coverage audit | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_test_assertion_depth.py` | Test assertion depth validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/detect_absolute_path_hardcoding.py` | Detect absolute path hardcoding | P0 | 0=pass, 1=findings |
| `scripts/governance/d7_code/check_encoding.py` | File encoding validation | P0 | 0=pass, 1=findings |
| `scripts/governance/d7_code/check_idempotency.py` | Idempotency check for write operations | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_fle_imports.py` | Feedback Loop Engine import validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/validate_contracts_purity.py` | Contracts purity check | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/detect_pydantic_any_fields.py` | Detect Pydantic fields typed as Any | P1 | 0=pass, 1=findings |
| `scripts/governance/d7_code/detect_missing_encoding.py` | Detect files missing encoding declaration | P0 | 0=pass, 1=findings |
| `scripts/governance/d7_code/check_pit_compliance.py` | PIT (Programmable Integrity Token) compliance | P1 | 0=pass, 1=findings |

#### DIM-SECURITY-001: Security Red Lines

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d6_security/detect_secrets.py` | Secret/hardcoded key detection | P0 | 0=pass, 1=findings, 2=error |
| `scripts/governance/d6_security/detect_shell_true.py` | Detect shell=True in subprocess calls | P0 | 0=pass, 1=findings, 2=error |
| `scripts/governance/d6_security/detect_shell_dangerous.py` | Detect dangerous shell command patterns | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/scan_secret_leak.py` | Scan for secret leaks in codebase | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/scan_runtime_log_secrets.py` | Scan runtime logs for leaked secrets | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/check_protected_paths.py` | Protected/anchor path modification detection | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/detect_anchor_file_deletion.py` | Detect deletion of anchor files | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/detect_permanent_file_deletion.py` | Detect permanent file deletion (no recycle) | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/detect_git_dangerous.py` | Detect dangerous git operations | P0 | 0=pass, 1=findings |
| `scripts/governance/d6_security/detect_keywords_in_logs.py` | Detect sensitive keywords in log output | P1 | 0=pass, 1=findings |
| `scripts/governance/d6_security/detect_threading_lock.py` | Detect missing thread safety locks | P1 | 0=pass, 1=findings |
| `scripts/governance/d6_security/validate_gate_discipline.py` | Gate discipline validation | P0 | 0=pass, 1=findings |

#### DIM-DEP-001: Dependency Chain Integrity

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d9_knowledge/detect_orphan_documents.py` | Build reverse reference graph — find documents with no inbound depends_on references | P1 | 0=pass, 1=findings, 2=error |
| `scripts/governance/d5_architecture/detectors/detect_depends_on_cycles.py` | Detect circular dependencies in depends_on graph | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_depends_on_format.py` | Validate depends_on field format | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/checkers/check_dependency_direction.py` | Validate layer dependency direction (lower → higher prohibited) | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/analyzers/audit_depends_on_chain_depth.py` | Audit depends_on chain depth | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_dag.py` | DAG validation for module dependency graph | P0 | 0=pass, 1=findings |
| `scripts/governance/crosscheck_sys_master_deps.py` | Cross-check SYS-MASTER dependency graph | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_interface_contracts.py` | Interface contract dependency validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_p0_module_contracts.py` | P0 module contract validation | P1 | 0=pass, 1=findings |

#### DIM-NAMING-001: File & Directory Naming Conventions

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d11_compliance/validate_script_naming.py` | Script naming convention (lowercase kebab-case) | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/detectors/detect_duplicate_module_names.py` | Detect duplicate module names across layers | P0 | 0=pass, 1=findings |

#### DIM-SCALE-001: Scale/Claim Drift (v3.0.0 new)

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d5_architecture/validators/yaml_md/validate_md_yaml_number_drift.py` | MD/YAML numeric claim drift — rules claim X but system has Y | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_layer_consistency.py` | Layer count consistency across registries | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_blueprint_code_sync.py` | Blueprint ↔ code file count sync | P1 | 0=pass, 1=findings |

#### DIM-ADR-001: ADR Document Chain Integrity (v3.0.0 new)

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d5_architecture/validators/validate_adr_frontmatter_consistency.py` | ADR frontmatter consistency validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/detectors/detect_deprecated_adr_references.py` | Detect deprecated ADR references in architecture YAMLs | P1 | 0=pass, 1=findings |

#### DIM-CONSTRUCTION-001: Construction Plan Consistency (v3.0.0 new)

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d5_architecture/validators/validate_ssot_construction_progress.py` | Construction progress SSoT validation | P1 | 0=pass, 1=findings |
| `scripts/governance/construction_gate.py` | Construction gate — validates blueprint_complete / phase_X_complete statuses | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_code_yaml_alignment.py` | Code ↔ YAML alignment audit | P1 | 0=pass, 1=findings |

#### DIM-LIFECYCLE-001: Artifact Lifecycle State Machine

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py` | Module lifecycle state machine validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/lifecycle/validate_lifecycle_refs.py` | Lifecycle reference validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/lifecycle/validate_phase_transition.py` | Phase transition legality check | P1 | 0=pass, 1=findings |
| `scripts/governance/d8_doc_sync/validate_document_lifecycle.py` | Document lifecycle validation | P1 | 0=pass, 1=findings |

#### DIM-DOC-001: Document Metadata & TTL Integrity

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d8_doc_sync/validate_document_ttl.py` | Document TTL expiration detection | P1 | 0=pass, 1=findings |
| `scripts/governance/d8_doc_sync/detect_dated_snapshots.py` | Detect dated snapshots past freshness window | P1 | 0=pass, 1=findings |
| `scripts/governance/d8_doc_sync/detect_ai_products_in_docs.py` | Detect AI-generated artifacts in docs/ | P1 | 0=pass, 1=findings |

#### DIM-ARCH-001: Architecture Structure & Extensibility

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d5_architecture/validators/validate_architecture_contract_internal.py` | Architecture internal contract validation | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_layer_deps.py` | Layer dependency validation (arch policy) | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` | Contract ↔ code drift detection | P0 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_load_path_integrity.py` | Load path integrity validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_three_way_consistency.py` | Three-way consistency (YAML ↔ Code ↔ Registry) | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py` | Static manifest drift detection | P1 | 0=pass, 1=findings |

#### DIM-SESSION-001: AI Session Integrity

| Provider Script (Full Path) | Description | Priority | Exit Codes |
|------|------|:---:|:---:|
| `scripts/governance/d12_ai_hallucination/validate_session_gate_check.py` | AI session gate check validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d12_ai_hallucination/validate_session_budget.py` | AI session budget validation | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py` | Session log index integrity | P1 | 0=pass, 1=findings |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_updated.py` | Session log freshness check | P1 | 0=pass, 1=findings |

#### Cross-Dimension Aggregators & Orchestrators

| Provider Script (Full Path) | Description | Priority |
|------|------|:---:|
| `scripts/governance/run_all.py` | Run all governance scripts in dimension order (Phase 1→6 entry) | P0 |
| `scripts/governance/run_incremental.py` | Incremental audit — only run scripts for files changed since last audit | P0 |
| `scripts/governance/pre_op_check.py` | Pre-operation check — runs all P0 scripts before any write operation | P0 |
| `scripts/governance/ci_self_check.py` | CI self-check — validates governance system integrity | P0 |
| `scripts/governance/_e2e_verify.py` | End-to-end verification pipeline | P1 |
| `scripts/governance/status.py` | Audit system status overview | P1 |

### Provider Count Summary

| Dimension | Provider Count |
|------|:---:|
| DIM-PATH-001 | 7 |
| DIM-TYPE-001~003 | 8 |
| DIM-CODE-001 | 17 |
| DIM-SECURITY-001 | 12 |
| DIM-DEP-001 | 9 |
| DIM-NAMING-001 | 2 |
| DIM-SCALE-001 | 3 |
| DIM-ADR-001 | 2 |
| DIM-CONSTRUCTION-001 | 3 |
| DIM-LIFECYCLE-001 | 4 |
| DIM-DOC-001 | 3 |
| DIM-ARCH-001 | 6 |
| DIM-SESSION-001 | 4 |
| Aggregators | 6 |
| **Total Structural Providers** | **86** |

> **Key design principle**: Every script listed above already exists and runs independently. The Audit Orchestrator v4.0.0 does NOT reimplement their logic — it provides a unified execution framework:
> - **Phase 1 DISCOVER**: AssetInventory detects mtime changes
> - **Phase 2 TRIAGE**: Orchestrator maps changed files → relevant dimensions → dispatches to corresponding provider scripts
> - **Phase 3 REPAIR**: Structural RED → AutoFix (template fix); Semantic RED → LLM Bridge (MOD-INF-028)
> - **Phase 4 ENFORCE**: RedBlue adversarial validation (MOD-INF-030) + convergence loop
>
> The Orchestrator also runs `run_all.py` as the "full sweep" entry point when a comprehensive audit is needed (e.g., post-refactor, pre-release).

## Trigger Model — Six-Layer Activation Architecture

> **The audit system is NOT a one-shot batch job. It is a multi-layer, continuously running closed-loop system. Each layer triggers at a different cadence for a different purpose — from real-time blocking (milliseconds) to scheduled deep sweeps (daily).**

### Layer Architecture

```
  L0: REAL-TIME BLOCKING — Before every AI write/delete     10~30ms
  L1: REAL-TIME AUDIT   — AuditTrail event-driven           <1s
  L2: INCREMENTAL AUDIT — After every AI Session             ~seconds
  L3: SCHEDULED AUDIT   — Cron timer                         ~minutes
  L4: EVENT-DRIVEN      — Git hook / CI / Webhook
  L5: MANUAL TRIGGER    — Developer CLI
```

### L0 — Real-Time Blocking Layer (Pre-Operation Gate)

```
  AI about to Write/SearchReplace/DeleteFile
      │
      ▼
  pre_op_check.py  ← exists! scripts/governance/pre_op_check.py
      │
      ├── Target is anchor file? → DENY (non-overridable)
      ├── Target is protected? → Check Gate passed?
      ├── Target path in legal dir? → Check path_enforcement
      ├── Creating new file? → Check scaffold invoked?
      └── Deleting file? → Check RULE-THREE protection scope
      │
   Result:
   ALLOW (0) → Proceed
   DENY  (1) → Block + write to AuditTrail + Alert human
```

| Property | Value |
|----------|-------|
| **When** | Before every AI write/delete operation |
| **Audit type** | Structural safety redlines: anchor protection, path legality, Gate pass |
| **Existing script** | `pre_op_check.py` |
| **Latency** | <30ms (must not block AI workflow) |
| **Caller** | AI auto-invokes before every write operation |

### L1 — Real-Time Audit Layer (Behavioral — Event-Driven)

```
  AI operation executed
      │
      ▼
  AuditTrail (020) records immutable log
      │
      ▼
  BehavioralAuditor (033) consumes event stream
      │
      ├── BH-001: Actor=AI? Target protected? → Permission matrix check
      ├── BH-002: DriftDetector signal? → AuditTrail traceback
      ├── BH-003: Cross-module unauthorized? → ACL check
      ├── BH-004: Session operation count exceeded? → Circuit breaker
      └── BH-005: Anchor file changed? → Immediate block
      │
   Result:
   RED    → Block + Alert + Rollback
   YELLOW → Alert (non-blocking)
   GREEN  → PASS (logged)
```

| Property | Value |
|----------|-------|
| **When** | Every AuditTrail event produced |
| **Audit type** | Behavioral: AI operation vs authorization matrix |
| **Dependencies** | MOD-INF-020 + 023 + 033 |
| **Latency** | <1s |
| **Trigger** | AuditTrail event stream auto-dispatches Orchestrator Phase 2 |

### L2 — Incremental Audit Layer (End of AI Session)

```
  AI Session ends
      │
      ▼
  AssetInventory (026) → mtime change list
      │
      ▼
  Orchestrator Phase 2 TRIAGE
      │
      ├── .py/.yaml changed → Structural Audit (19 dims)
      │   → Invoke DIM-PATH/DIM-CODE/DIM-TYPE provider scripts
      │
      ├── Rules docs changed → Structural + dispatch SemanticAuditor (028)
      │   → F: Cross-document reference break detection
      │   → G: Depends-On governance intent break detection
      │
      └── AuditTrail anomalies → Already handled by L1
      │
      ▼
  Phase 3 REPAIR → Phase 4 ENFORCE (RedBlue)
```

| Property | Value |
|----------|-------|
| **When** | Every AI Session end (`exit`/`done`/`task complete`) |
| **Audit type** | Structural (19 dims) + Semantic (F+G), incremental mode |
| **Existing script** | `run_incremental.py` |
| **Duration** | Depends on change volume, typically seconds (only scans changed files) |
| **Note** | Skips unchanged files (Hash fingerprint cache), extremely fast |

### L3 — Scheduled Full Sweep Layer (Cron Timer)

```
  Cron: Daily 3:00 AM / Weekly Sunday
      │
      ▼
  run_all.py → All 86 scripts executed in dimension order
      │
      ▼
  Orchestrator Phase 1 DISCOVER → Full mtime + Hash fingerprint
      │
      ▼
  Phase 2 TRIAGE → Full structural audit (19 dims x 86 providers)
                  → Semantic audit (all rule documents)
                  → Behavioral audit (AuditTrail time window traceback)
      │
      ▼
  Phase 3 REPAIR → Batch AutoFix → Batch LLM fix
      │
      ▼
  Phase 4 ENFORCE → RedBlue adversarial validation → Rollback or CLOSE
```

| Property | Value |
|----------|-------|
| **When** | Cron scheduler |
| **Audit type** | Full tri-audit + full repair pipeline |
| **Existing script** | `run_all.py` |
| **Recommended frequency** | Daily (P0 dims, 5min fast scan) + Weekly full + Monthly deep |
| **Duration** | Full sweep may take minutes; runs in background |

### L4 — Event-Driven Layer (Git Hook / CI / Webhook)

| Trigger Event | Audit Action |
|--------------|-------------|
| `git commit` pre-hook | Security redline audit (DIM-SECURITY: secret leak / shell_true / anchor deletion) |
| `git push` pre-hook | Registration integrity audit (DIM-TYPE: __all__ / registry consistency) |
| `git merge` post-hook | Dependency chain audit (DIM-DEP: depends_on cycle / direction / DAG) |
| `module-registry.yaml` modified | All DIM-TYPE dimensions auto-trigger |
| `blueprint.md` modified | Structural audit + Semantic audit (that document's references) |
| CI/CD pipeline | `.trae/ci-check.yml` — fast security + registration gate |

### L5 — Manual Trigger Layer

```bash
# Fast gate check
python scripts/governance/pre_op_check.py --check-all <filepath>

# Specific dimensions
python scripts/governance/run_all.py --dimensions D1 D6 D7

# Full audit
python scripts/governance/run_all.py

# Incremental audit
python scripts/governance/run_incremental.py

# Audit status overview
python scripts/governance/status.py
```

### Trigger Summary Table

| Layer | When | Triggered By | What Audits | Existing Script |
|:---:|------|-------------|------------|:---:|
| L0 | Before every AI write/delete | AI auto-invoke | Safety redlines (anchor/path/Gate) | `pre_op_check.py` |
| L1 | Every AuditTrail event | AuditTrail event stream | Behavioral (authorization boundary) | Pending 033 integration |
| L2 | Every AI Session end | Session lifecycle hook | Structural + Semantic, incremental | `run_incremental.py` |
| L3 | Daily/Weekly scheduled | Cron | Full tri-audit + full repair | `run_all.py` |
| L4 | Git commit/push/merge | Git hooks | Security + Registration + Dependencies | `run_all.py --dimensions` |
| L5 | Developer manual | CLI | Any | All scripts |

### Key Design Principles

1. **L0+L1 real-time, L2 near-real-time, L3 scheduled, L4 event, L5 backup** — Five-layer coverage prevents any escape
2. **L0 is the last line of defense** — Even if L1~L5 all fail, L0 stops the AI before it acts
3. **Existing scripts are mature** — `pre_op_check.py`, `run_all.py`, `run_incremental.py` all exist and work
4. **To be built** — L1 BehavioralAuditor event stream integration; L2 Session-end auto-trigger hook
5. **Solo-dev optimized** — L0/L1 are fully automatic; L2/L3 can be configured once; L5 is optional

---

# Audit Orchestrator — Multi-Dimension Iterative Audit Engine (MDIAE) v4.0.0
> **module_id**: MOD-INF-027 | **version**: 4.0.0 | **status**: draft | **layer**: cross_layer

> **对标**：AWS Config（持续合�?+ 自动修复�? K8s Reconciliation Loop（调谐收敛）+ Netflix Chaos Engineering（假设验证）+ IBM MAPE-K（Monitor→Analyze→Plan→Execute→Knowledge 自治循环�? DORA（部署频�?变更故障�?恢复时间/变更前置时间�? Google SRE（Error Budget + SLO/SLI�? SonarQube（多维静态分析）+ OPA Gatekeeper（策略即代码）。独�?**"语义审计最小风险协�?× 孤儿判定三决策树 × 红白对抗自生长攻击库 × MAPE-K Knowledge 模式学习 × 增量Hash指纹 × Meta-Audit自审�?** 六位创新——不是一次性扫描，而是四阶段闭环反复验证直到系统自证清白�?
---

## 1. 概述与模块定�?
### 1.1 模块身份

| 属�?| �?|
|------|-----|
| module_id | MOD-INF-027 |
| 代码落位 | `src/zephyr/audit_orchestrator/` |
| 运行时平�?| Warm（编排调度按需触发 + cron 定时触发�?|
| 核心职责 | **"全维度系统自证清白引�?**：自动发现所有可审计目标 �?四阶段闭�?�?迭代收敛 �?Knowledge 积累 �?直到全局通过 |
| 设计哲学 | **"不是体检——是住院治疗循环 + 病历存档"**：SonarQube �?去体检一次拿报告"，MDIAE �?住院全面体检 + 查出问题当场�?+ 治完再攻击自己验�?+ 两次全部指标正常才出�?+ 把这次经历写进病历供下次参�? |

### 1.2 四阶段闭环总览（v4.0.0）

```
┌─────────────────────────────────────────────────────────────────────┐
│              ZephyrAlpha Total Audit System v4.0.0                   │
│                                                                      │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────┐ │
│  │ PHASE 1  │──▶│   PHASE 2    │──▶│   PHASE 3    │──▶│ PHASE 4  │ │
│  │ DISCOVER │   │  TRIAGE &    │   │   REPAIR     │   │ ENFORCE  │ │
│  │          │   │  SCHEDULE    │   │   PIPELINE   │   │ & CLOSE  │ │
│  │"变了什么?"│   │"谁来审这个?" │   │ "怎么修?"    │   │"修好了?" │ │
│  └────┬─────┘   └──────┬───────┘   └──────┬───────┘   └────┬─────┘ │
│       │                │                  │                │       │
│       │  AssetInventory│         ┌────────┴────────┐       │       │
│       │  mtime变更检测  │         │  Structural RED  │       │       │
│       │                │         │  -> AutoFix       │       │       │
│       ▼                ▼         │  Semantic RED    │       ▼       │
│  ┌─────────┐    ┌──────────┐     │  -> LLM Bridge   │  ┌────────┐  │
│  │.py/.yaml│    │ 3 audit  │     │  Behavioral RED  │  │RedBlue │  │
│  │ 文件变更 │    │  types:  │     │  -> Block+Alert  │  │对抗验证│  │
│  └────┬────┘    │          │     └────────┬────────┘  └────┬───┘  │
│       │         │ STRUCTURAL│              │                │      │
│       │         │ (internal)│              │        全部GREEN?     │
│       ▼         │ SEMANTIC  │              │          ├─YES→收敛  │
│  ┌─────────┐    │ (peer:028)│              │          └─NO→回到P1│
│  │Rule doc │    │ BEHAVIORAL│              │                      │
│  │ 变更    │    │ (internal)│              │  ┌─────────────────┐ │
│  └────┬────┘    └─────┬─────┘              │  │N次连续零问题    │ │
│       │               │                   │  │->CLOSED OK       │ │
│       ▼               ▼                   │  └─────────────────┘ │
│  ┌─────────┐    ┌──────────┐              │                      │
│  │AuditTrail│   │去重/并发 │              │                      │
│  │异常事件  │   │/依赖排序 │              │                      │
│  └─────────┘   └──────────┘              │                      │
└─────────────────────────────────────────────────────────────────────┘
```

| 阶段 | 名称 | 核心问题 | 关键组件 |
|:---:|------|---------|---------|
| 1 | **DISCOVER** | "系统里什么变了?" | AssetInventory -> mtime hash 指纹变更检测 |
| 2 | **TRIAGE & SCHEDULE** | "变更属于哪种审计类型? 去重、排序、分发" | 三类审计分流: Structural(内建17维) / Semantic(peer MOD-INF-028) / Behavioral(内建 AuditTrail+DriftDetector) |
| 3 | **REPAIR PIPELINE** | "如何修复发现的问题?" | Structural RED -> AutoFix(MOD-INF-031); Semantic RED -> LLM Bridge 人工确认; Behavioral RED -> Block+Alert+Rollback(MOD-INF-021) |
| 4 | **ENFORCE & CLOSE** | "修复真有效吗? 可以关闭吗?" | RedBlue 对抗验证(MOD-INF-030) -> 收敛检测 -> N次连续零问题=CLOSED / 未收敛=回到Phase 1 |

### 1.2.1 旧六阶段->新四阶段迁移映射

| 旧结构 (v1.x-3.x) | 新结构 (v4.0.0) | 说明 |
|-------------------|-----------------|------|
| Phase 1: Discover | Phase 1: DISCOVER | 核心逻辑保留, 由 AssetInventory 统一驱动 |
| Phase 2: Audit | Phase 2: TRIAGE & SCHEDULE | 审计扩展为三类并行(结构/语义/行为), Triage 做分发路由 |
| Phase 3: Repair | Phase 3: REPAIR PIPELINE | 修复按审计类型分三路: 模板修复/LLM生成/阻断告警 |
| Phase 4: Git Backup | 合并入 Phase 3 precondition | Git 快照不再是独立阶段, 而是修复前的安全前置操作 |
| Phase 5: RedBlue | Phase 4: ENFORCE & CLOSE | 红白对抗 + 收敛检测合为一个验证闭环阶段 |
| Phase 6: Convergence | Phase 4: ENFORCE & CLOSE | 收敛检测是关闭阶段的前置条件 |
### 1.3 MAPE-K 自治循环映射

> **MAPE-K = Monitor �?Analyze �?Plan �?Execute �?Knowledge�?* MDIAE �?MAPE-K 在代码库治理领域的完整实现�?
| MAPE-K �?| MDIAE 映射 | 组件 |
|-----------|-----------|------|
| **M**onitor | Phase 1 发现 + §21 遥测 | DiscoveryEngine + TelemetryCollector |
| **A**nalyze | Phase 2 审计（结�?+ 语义�?| DimensionChecker + dispatches to SemanticAuditor (MOD-INF-028, peer) |
| **P**lan | Phase 3 修复判定 | OrphanJudge(MOD-INF-029) —�?三决策树输出处置计划 |
| **E**xecute | Phase 3 修复执行 + Phase 4 红白对抗 | AutoFixEngine(MOD-INF-031) + RedBlueValidator(MOD-INF-030) |
| **K**nowledge | §17 知识积累�?| PatternLearner + RuleEvolver + FixTemplateDB |

---

## 2. 五层架构

```
                    ┌─────────────────────────────────────�?                    �?  Layer 5: Knowledge Layer (NEW)    �?                    �? PatternLearner / RuleEvolver /     �?                    �? FixTemplateDB / EntropyTracker     �?                    └─────────────────┬───────────────────�?                                      �?feeds back to all layers
                    ┌─────────────────▼───────────────────�?                    �?  Layer 4: AI Driver Loop           �?                    �? Trae IDE / Roo Code JSON / Auto API�?                    �? Agent Skill: audit-orchestrator    �?                    └─────────────────┬───────────────────�?                                      �?                    ┌─────────────────▼───────────────────�?                    �? Layer 3: Audit Orchestrator        �?                    �? ┌─────────────────────────────────┐│
                    �? �?PhaseController (四阶段调�?     ││
                    �? �?DimensionRegistry (维度注册�?   ││
                    �? �?IterationController (迭代控制)   ││
                    �? �?ConvergenceGate (收敛判定)       ││
                    �? �?AuditScheduler (cron/trigger)    ││
                    �? �?IncrementalCache (Hash指纹缓存)  ││
                    �? �?CircuitBreaker (熔断�?          ││
                    �? �?TelemetryExporter (遥测导出)     ││
                    �? �?ReportGenerator (报告生成)       ││
                    �? �?MetaAuditor (自审�?             ││
                    �? �?GitBackupManager (快照管理)      ││
                    �? �?NonConvergenceHandler (不收敛处�?││
                    �? �?EscalationBridge (升级桥接)      ││
                    �? └─────────────────────────────────┘│
                    └─────────────────┬───────────────────�?                                      �?                    ┌─────────────────▼───────────────────�?                    �? Layer 2: Dimension Slicers         �?                    �? 10 个核心维�?× N 个扩展维�?       �?                    �? + DimensionProvider 插件接口        �?                    └─────────────────┬───────────────────�?                                      �?                    ┌─────────────────▼───────────────────�?                    �? Layer 1: Check Executors           �?                    �? 43 Phase checks + 20 Gates +       �?                    �? 合规矩阵 + 蓝图代码审计�?+         �?                    �? 回滚审计�?+ 依赖审计�?+           �?                    �? 防篡改审计器 + 规范审计�?          �?                    └─────────────────────────────────────�?```

---


## 3. Phase 1 — DISCOVER

> **核心问题**: "系统里什么变了?"

DiscoveryEngine 不关心"系统里有什么"（那是 AssetInventory 的静态清单职责），它只关心"这次审计前 vs 上次审计后，哪些文件发生了变更"。

### 3.1 三种变更来源

```
AssetInventory (mtime hash fingerprint)
  |
  ├── .py/.yaml 文件变更 ──> Structural Audit (internal)
  ├── 规则文档变更 (.md/.yaml) ──> Semantic Audit (peer MOD-INF-028)
  └── AuditTrail 异常事件 ──> Behavioral Audit (internal)
```

| 来源 | 检测方式 | 触发审计类型 |
|------|---------|------------|
| `.py` / `.yaml` 代码/配置变更 | `os.stat().st_mtime` hash 指纹比对 | Structural Audit |
| `docs/01_policies_and_standards/` 下规则文档变更 | 同上 + GATE-11 触发规则检查 | Semantic Audit (delegates to MOD-INF-028) |
| AuditTrail 日志中的异常事件 | MOD-INF-020 事件流监听 | Behavioral Audit |

### 3.2 增量 Hash 指纹

```python
class DiscoveryEngine:
    def __init__(self, asset_inventory: AssetInventory):
        self.inventory = asset_inventory
        self.hash_index = HashIndex(Path("data/audit_cache/hash_index.json"))

    def discover(self) -> DiscoveryReport:
        changed = []
        for asset in self.inventory.iter_all():
            current_hash = hash_file(asset.path)
            if self.hash_index.get(asset.path) != current_hash:
                changed.append(ChangedFile(path=asset.path, old_hash=..., new_hash=current_hash))
                self.hash_index.update(asset.path, current_hash)
        return DiscoveryReport(changed_files=sorted(changed, key=lambda f: f.audit_type_priority))
```

### 3.3 发现报告结构

```python
@dataclass
class DiscoveryReport:
    changed_files: list[ChangedFile]
    total_scanned: int
    skipped_unchanged: int
    audit_type_distribution: dict[str, int]  # {"structural": 45, "semantic": 12, "behavioral": 3}

@dataclass
class ChangedFile:
    path: Path
    audit_type: AuditType  # STRUCTURAL | SEMANTIC | BEHAVIORAL
    old_hash: str
    new_hash: str
    priority: int  # derived from audit_type + dependency depth
```

---

## 4. Phase 2 — TRIAGE & SCHEDULE

> **核心问题**: "变更属于哪种审计类型? 去重、排序、分发到正确的审计器"

### 4.1 三类审计分流

```
DiscoveryReport
  |
  ├── audit_type == STRUCTURAL  ──> StructuralAuditor (17 维度规则引擎)
  ├── audit_type == SEMANTIC    ──> SemanticAuditor (peer MOD-INF-028, belongs_to: null)
  └── audit_type == BEHAVIORAL  ──> BehavioralAuditor (AuditTrail + DriftDetector)
```

### 4.2 Scheduler: 去重 + 并发 + 依赖排序

```python
class TriageScheduler:
    def triage(self, report: DiscoveryReport) -> AuditBatch:
        batches = {at: [] for at in AuditType}
        for cf in report.changed_files:
            if not self.is_duplicate(cf):  # 同一文件多个变更源 → 只审一次
                batches[cf.audit_type].append(cf)
        # 依赖排序: 被依赖的文件先审
        for at in AuditType:
            batches[at] = self.topological_sort(batches[at])
        return AuditBatch(batches=batches)

    def schedule(self, batch: AuditBatch) -> ExecutionPlan:
        # 并发限制: max_workers = min(len(batch), 8)  (RULE-SEVEN)
        # CircuitBreaker 预检
        return ExecutionPlan(tasks=batch.flatten(), max_workers=8)
```

### 4.3 结构审计维度（17 个核心维度，100% 机械判定）

> **Provider Table 是 SSoT**——详细 Provider 映射见 [Provider Table](#provider-table)。

| dim_id | 名称 | 切法 | 审计内容 | Provider 脚本数 | 收敛 |
|--------|------|------|---------|:---:|:---:|
| DIM-PATH-001 | 文件路径强制合规 | 路径切 | 21 种文件类型强制路径 / 废弃路径 / 根目录白名单 / 声明-vs-过程式边界 | 7 | 1 |
| DIM-TYPE-001 | 脚本文件类型审计 | 横切 | .py 脚本注册 / 去重 / 文档 / 空壳检测 | 5 | 2 |
| DIM-TYPE-002 | 门禁文件类型审计 | 横切 | gate .yaml 注册 / 无僵尸 / 自检 | 2 | 2 |
| DIM-TYPE-003 | 规则文件类型审计 | 横切 | 规则文件被落实 / 不过时 | 1 | 2 |
| DIM-CODE-001 | 代码施工标准审计 | 代码切 | __init__.py 仅公开 API / 类型注解 / import 顺序 / 文件尺寸 / 禁止 import * / SSoT 守卫 / 金融类型 | 17 | 2 |
| DIM-SECURITY-001 | 安全红线审计 | 安全切 | 零密钥硬编码 / 零 shell=True / 零危险命令 / 锚点文件零删除 / .env 在 gitignore / 密钥轮换 | 12 | 1 |
| DIM-DEP-001 | 跨模块依赖完整性审计 | 交叉切 | depends_on 目标存在 / 版本一致 / INJ-002 + INJ-008 | 9 | 1 |
| DIM-NAMING-001 | 文件与目录命名规范审计 | 命名切 | 全小写 kebab-case / 禁止版本后缀 / doc_type 后缀 / 文件夹风格 / ADR 命名 / module_id 格式 | 2 | 2 |
| DIM-SCALE-001 | 规模漂移审计 | 规模切 | 目录平铺 .py 计数 ≥ 50 ERROR / ≥ 10 WARN / 时段内 top-N churn 目录 / max-depth / 大型文件 top-N | 3 | 1 |
| DIM-ADR-001 | ADR 文档链审计 | ADR切 | ADR 编号连续 / 洋葱引用 / frontmatter status 受控词表 / 关联模块在注册表中 | 2 | 1 |
| DIM-CONSTRUCTION-001 | 施工进度审计 | 施工切 | 蓝图 status vs construction_progress 一致 / milestone 不倒退 / 任务卡 batch_id 存在 / 超期 P0 batched 任务报警 | 3 | 1 |
| DIM-LIFECYCLE-001 | 制品生命周期状态机审计 | 状态切 | 模块 8 态合法值 / 状态迁移路径 / runtime_plane / P0 需 ADR / 任务关闭 deliverables+UTF-8+LF+无临时 | 4 | 1 |
| DIM-DOC-001 | 文档合规审计 | 文档切 | frontmatter 字段合规 / 模板章节 / 破窗检测 / 编码为 UTF-8 | 3 | 1 |
| DIM-ARCH-001 | 架构结构与可扩展性审计 | 结构切 | LPC 双轨合规 / 层一致性 / 依赖方向 / 蓝图平铺 / 循环依赖 / 未注册目录 | 6 | 1 |
| DIM-SESSION-001 | Session 质量审计 | 会话切 | Session Log 必填字段 / 边界规则 (≤8 文件 / ≤3 目录) / handoff 合规 / Log 文件存在 + 格式验证 | 4 | 1 |
| DIM-DIR-001 | Governance 目录审计 | 竖切 | scripts/governance/ 结构合规 | 1 | 1 |
| DIM-FIELD-001 | Owner 字段唯一性审计 | 字段切 | 所有 YAML 中 owner 有效性 | 1 | 1 |

> **Provider 总览**: 17 个维度组 × 86 个 Provider 脚本。完整映射见 [Provider Table](#provider-table)。

### 4.4 Behavioral Auditor v2.0.0（内建）

> **触发**: AuditTrail 异常事件 + DriftDetector 行为边界对比。
> **不依赖外部语义分析**——全部基于规则引擎 + 时序模式匹配。

| check_id | 审计内容 | 判定方式 | 执行器 | severity |
|----------|---------|---------|--------|:---:|
| `beh_audit_trail_pattern` | AuditTrail 行为日志中的异常模式检测（高频重复操作 / 异常时段操作 / 权限越界） | 时序模式匹配 + 频率阈值 | `behavioral_auditor.py` | RED/YELLOW |
| `beh_drift_boundary` | DriftDetector 行为边界对比——当前操作序列是否偏离历史基线 | 行为基线 diff (trade-off 容忍度 0.2) | DriftDetector + `behavioral_auditor.py` | RED |
| `beh_event_correlation` | 多个 AuditTrail 事件之间的因果关联检测（A 操作→B 异常高频） | 事件关联图 + 因果强度 | `behavioral_auditor.py` | YELLOW |

---

## 5. Phase 3 — REPAIR PIPELINE

> **核心问题**: "发现的问题如何修复?" 修复策略由审计类型决定——三类审计→三路修复。

### 5.1 修复路由

```
Audit RED findings
  |
  ├── Structural RED ──> 模板化修复 ──> MOD-INF-031 AutoFix Engine
  │    确定性: 100% (更新路径/ID/值 → 全部机械)
  │
  ├── Semantic RED  ──> 标记"需人工确认" ──> MOD-INF-028 LLM Bridge
  │    确定性: 95~98% (LLM 生成自然语言修复建议 → 人工确认后执行)
  │
  └── Behavioral RED ──> Block + Alert + Rollback
       确定性: 100% (阻断当前操作 + 告警 + MOD-INF-021 回滚)
```

### 5.2 Repair Pipeline 流程

```python
class RepairPipeline:
    def __init__(self, auto_fix: AutoFixEngine, llm_bridge: LLMBridge, rollback: RollbackEngine):
        self.auto_fix = auto_fix      # MOD-INF-031
        self.llm_bridge = llm_bridge  # MOD-INF-028 LLM Bridge
        self.rollback = rollback      # MOD-INF-021

    def repair(self, findings: AuditFindings) -> RepairReport:
        # 1. Git 快照 (pre-repair safety net)
        git_tag = create_pre_repair_tag(findings.audit_id)

        repairs = []
        for finding in findings:
            match finding.audit_type:
                case AuditType.STRUCTURAL:
                    repair = self.auto_fix.repair(finding)  # 模板化修复, 100% 确定性
                case AuditType.SEMANTIC:
                    repair = self.llm_bridge.generate_and_queue(finding)  # LLM 生成→人工确认队列
                case AuditType.BEHAVIORAL:
                    repair = self.rollback.block_and_alert(finding)  # Block + Alert + Rollback

            repair.verify()  # 修复后自检
            repairs.append(repair)

        return RepairReport(repairs=repairs, git_tag=git_tag)
```

### 5.3 修复验证（每次修复后 MUST 执行）

| 验证 | 内容 | 失败动作 |
|------|------|---------|
| self-check | 修复操作本身的语法/逻辑正确性 | 拒绝写入 |
| audit-trail | 记录修复操作到 AuditTrail | 修复操作自身可审计 |
| file-integrity | 修复后文件内容完整 (hash check) | 回滚到 pre-repair tag |

---

## 6. Phase 4 — ENFORCE & CLOSE

> **核心问题**: "修复真有效吗? 可以关闭本次审计吗?"

### 6.1 RedBlue 对抗验证 (MOD-INF-030)

```
RepairReport
  |
  ▼
RedBlueValidator (MOD-INF-030)
  |
  ├── 全部 GREEN ──> 收敛检测
  │     ├── N 次连续零问题 ──> CLOSED ✅
  │     └── 未达收敛 ──> 回到 Phase 1
  │
  └── 仍有 RED ──> Rollback (MOD-INF-021) ──> 回到 Phase 1
```

### 6.2 收敛条件

```python
CONVERGENCE_CRITERIA = {
    "min_consecutive_green": 2,      # 至少连续 2 次全 GREEN
    "max_global_rounds": 3,          # 最多 3 轮全局循环
    "convergence_window_days": 1,    # 连续 GREEN 需在 1 天内
}

def check_convergence(reports: list[AuditReport]) -> ConvergenceResult:
    if len(reports) >= CONVERGENCE_CRITERIA["min_consecutive_green"]:
        if all(r.all_green for r in reports[-CONVERGENCE_CRITERIA["min_consecutive_green"]:]):
            return ConvergenceResult.CLOSED
    if len(reports) >= CONVERGENCE_CRITERIA["max_global_rounds"]:
        return ConvergenceResult.STUCK  # 升级人工裁决
    return ConvergenceResult.CONTINUE
```

### 6.3 关闭动作

```
CLOSED 后:
  1. KB writeback: 将本次审计的模式/规则/修复模板写入 Knowledge Layer
  2. AuditTrail finalize: 写入闭合事件
  3. Metric export: 计算 DORA 四指标 + 趋势对比
  4. Report generation: 生成 AuditReport .yaml + .md
  5. Cache cleanup: 清理增量 HashIndex 中未变更条目
```
## 9. 维度体系（完整清单）

### 9.1 17 核心结构维度（v4.0.0，对齐 Provider Table）

| dim_id | 名称 | 切法 | 审计内容 | Provider 数 | 收敛 |
|--------|------|------|---------|:---:|:---:|
| DIM-PATH-001 | 文件路径强制合规 | 路径切 | 21 种文件类型强制路径 / 废弃路径 / 根目录白名单 | 7 | 1 |
| DIM-TYPE-001 | 脚本文件类型审计 | 横切 | .py 脚本注册 / 去重 / 文档 / 空壳检测 | 5 | 2 |
| DIM-TYPE-002 | 门禁文件类型审计 | 横切 | gate .yaml 注册 / 无僵尸 / 自检 | 2 | 2 |
| DIM-TYPE-003 | 规则文件类型审计 | 横切 | 规则文件被落实 / 不过时 | 1 | 2 |
| DIM-CODE-001 | 代码施工标准审计 | 代码切 | __init__.py 仅公开 API / 类型注解 / import 顺序 / 文件尺寸 / 禁止 import * / SSoT 守卫 / 金融类型 | 17 | 2 |
| DIM-SECURITY-001 | 安全红线审计 | 安全切 | 零密钥硬编码 / 零 shell=True / 零危险命令 / 锚点文件零删除 | 12 | 1 |
| DIM-DEP-001 | 跨模块依赖完整性审计 | 交叉切 | depends_on 目标存在 / 版本一致 / INJ-002 + INJ-008 | 9 | 1 |
| DIM-NAMING-001 | 文件与目录命名规范审计 | 命名切 | 全小写 kebab-case / 禁止版本后缀 / doc_type 后缀匹配 / ADR 命名 / module_id 格式 | 2 | 2 |
| DIM-SCALE-001 | 规模漂移审计 | 规模切 | 目录平铺 .py >=50 ERROR / top-N churn 目录 / max-depth / 大型文件 | 3 | 1 |
| DIM-ADR-001 | ADR 文档链审计 | ADR切 | ADR 编号连续 / 洋葱引用 / frontmatter status / 关联模块在注册表 | 2 | 1 |
| DIM-CONSTRUCTION-001 | 施工进度审计 | 施工切 | 蓝图 vs 施工进度一致 / milestone 不倒退 / 任务卡 batch_id / 超期报警 | 3 | 1 |
| DIM-LIFECYCLE-001 | 制品生命周期状态机审计 | 状态切 | 模块 8 态 / 状态迁移 / runtime_plane / P0 需 ADR / 任务关闭 | 4 | 1 |
| DIM-DOC-001 | 文档合规审计 | 文档切 | frontmatter 字段合规 / 模板章节 / 破窗检测 / 编码 UTF-8 | 3 | 1 |
| DIM-ARCH-001 | 架构结构与可扩展性审计 | 结构切 | LPC 双轨合规 / 层一致性 / 依赖方向 / 循环依赖 / 未注册目录 | 6 | 1 |
| DIM-SESSION-001 | Session 质量审计 | 会话切 | Session Log 字段 / 边界规则 (<=8 files, <=3 dirs) / handoff / Log 存在+格式 | 4 | 1 |
| DIM-DIR-001 | Governance 目录审计 | 竖切 | scripts/governance/ 结构合规 | 1 | 1 |
| DIM-FIELD-001 | Owner 字段唯一性审计 | 字段切 | 所有 YAML 中 owner 有效性 | 1 | 1 |

> **总计**: 17 个结构维度 x 86 个 Provider 脚本。完整 Provider 映射见 [Provider Table](#provider-table)。
> **语义审计已提升为独立 peer 服务**: MOD-INF-028 Semantic Auditor (belongs_to: null)，不再作为 orchestrator 的内建维度。

### 9.2 交叉覆盖矩阵（目标：每文件 >= 3 维度）

| 文件示例 | PATH | TYPE | CODE | SEC | DEP | NAMING | SCALE | ADR | CONSTR | LIFE | DOC | ARCH | SESSION | DIR | FIELD | 覆盖 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| scripts/governance/audit_registration.py | | Y001 | Y001 | | | | | | | | | | | Y001 | | 4 |
| src/zephyr/gates/_registry.yaml | | Y002 | | | Y001 | | | | | Y001 | | Y001 | | | Y001 | 6 |
| project_rules.md | Y001 | Y003 | | | | Y001 | | | | | Y001 | Y001 | | | Y001 | 7 |
| docs/registry-of-registries.yaml | Y001 | Y003 | | | Y001 | | | Y001 | Y001 | Y001 | Y001 | Y001 | | | Y001 | 9 |
| src/zephyr/core/models.py | | Y001 | Y001 | | | | | | | Y001 | | Y001 | | | | 5 |
| src/zephyr/agent_rbac/dependency_auditor.py | | | | Y001 | Y001 | | | | | | | Y001 | | | | 4 |
| .env | Y001 | | | Y001 | | | | | | | | | | | | 2 |
| session-logs/ | | | | | | | | | | | | | Y001 | | | 1 |
| config/rbac_roles.yaml | | | | Y001 | | | | | | | | | | | Y001 | 3 |

> **空壳检测**: DIM-TYPE-001 的 shell_detection 子检查覆盖所有新增 .py 文件检测文件只有 import/class/def 骨架但无实质逻辑（AST 节点数 < 20 且 docstring 为空 = 空壳）。
## 10. AI 驱动模式 + Agent Skill 协议

### 10.1 模式 A：Trae IDE 对话驱动

```
用户: "开始全量审�?
Trae AI:
  [加载 agent_spec skill: audit-orchestrator]  �?v1.0.0 新增
  [加载 MOD-INF-027.AuditOrchestrator]
  → Phase 1 DISCOVER: 增量扫描 → 15 NEW + 3 MODIFIED
  → Phase 2 TRIAGE & SCHEDULE: 审计 DIM-TYPE-001 → 43 checks → 2 RED, 1 YELLOW
  → Phase 3 REPAIR: L1自动修复 2 RED → all GREEN; git tag audit-20260508-001-pre
  → Phase 4 ENFORCE & CLOSE: 红白对抗 7/7 拦住 → 全局 CONVERGED → CLOSED
  → Knowledge: PatternLearner 记录"脚本孤儿是最高频问题"
```

### 10.2 模式 B：Roo Code / 外部 Agent JSON API

```json
{"command": "run_phase", "phase": "discovery", "incremental": true}
// �?{"phase": "discovery", "new": 15, "modified": 3, "orphans": 3, ...}

{"command": "run_dimension", "dim_id": "DIM-TYPE-001", "incremental": true}
// �?{"dim_id": "DIM-TYPE-001", "pass": 1, "issues": [...], "converged": false, ...}
```

### 10.3 模式 C：全自主 API 循环

```python
from zephyr.audit_orchestrator import AutonomousAuditLoop
loop = AutonomousAuditLoop()
report = loop.run_full_audit()
```

### 10.4 Agent Skill 自发现协�?
> �?AI session MUST 能通过 agent_spec 系统发现 audit-orchestrator 技能�?
```yaml
# agent_spec/skill_registry.yaml 中注�?- skill_id: "audit-orchestrator"
  name: "全量审计编排�?
  description: "触发全量/增量审计，四阶段闭环验证系统合规�?
  keywords: ["审计", "audit", "合规检�?, "孤儿检�?, "红白对抗", "收敛验证"]
  entry_module: "zephyr.audit_orchestrator"
  entry_class: "AuditOrchestrator"
  domain: "governance"
  role: "executor"
  auto_discoverable: true
```

---

## 11. 数据模型（全量）

```python
# ── 发现阶段 ──
class DiscoveryResult(BaseModel):
    total_assets: int
    registered: int
    orphans: list[OrphanEntry]
    zombies: list[ZombieEntry]
    orphan_by_type: dict[str, int]
    incremental: IncrementalChangeSet | None

class IncrementalChangeSet(BaseModel):
    new_files: int
    modified_files: int
    deleted_files: int
    unchanged_files: int
    new_list: list[str]
    modified_list: list[str]

class HashEntry(BaseModel):
    file_path: str
    sha256: str
    mtime: float
    size: int

# ── 审计阶段 ──
class AuditIssue(BaseModel):
    issue_id: str
    dim_id: str
    check_id: str
    target_file: str
    severity: Severity
    auto_fixable: bool
    fix_level: FixLevel
    suggested_fix: str | None
    trigger_type: str | None

# ── 修复阶段 ──
class OrphanJudgment(BaseModel):
    orphan_path: str
    has_duplicate: bool
    has_unique_value: bool
    has_standalone_value: bool
    recommendation: str
    confidence: float

class FixAction(BaseModel):
    action_id: str
    level: FixLevel
    action_type: str
    target_file: str
    before_hash: str | None
    after_hash: str | None
    before_snapshot: str | None
    after_snapshot: str | None
    rollback_verified: bool | None

# ── 红白对抗 ──
class RedBlueReport(BaseModel):
    total_scenarios: int
    blocked: int
    bypassed: int
    pass_rate: float
    scenarios: list[ScenarioResult]
    new_attack_patterns_added: list[str]

# ── 全局报告 ──
class GlobalAuditReport(BaseModel):
    audit_id: str
    started_at: datetime
    finished_at: datetime | None
    global_rounds: int
    global_converged: bool
    phases: dict[str, PhaseResult]
    total_issues_found: int
    total_issues_fixed: int
    pending_human_decisions: list[EscalationItem]
    git_tags: list[str]
    entropy_velocity: float | None
    is_incremental: bool
    skipped_by_cache: int
    dora_metrics: DORASnapshot | None

# ── Knowledge Layer ──
class AuditPatternRecord(BaseModel):
    pattern_id: str
    pattern_type: str           # frequent_failure | new_anti_pattern | resolution_template
    dim_id: str
    check_id: str
    occurrence_count: int
    first_seen: datetime
    last_seen: datetime
    resolution_template: str | None

class FixTemplate(BaseModel):
    template_id: str
    issue_signature: str        # 问题的唯一签名（规则名+文件类型+特征�?    fix_type: FixLevel
    fix_code: str               # 可重用的修复脚本模板
    success_rate: float
    usage_count: int

# ── DORA 指标快照 ──
class DORASnapshot(BaseModel):
    deployment_frequency: float
    change_failure_rate: float   # = RED issues / total changes
    mean_time_to_recover: float  # = 平均修复轮数
    lead_time_for_changes: float # = 从发现问题到修复完成的时�?```

---

## 12. 与现有系统的集成点（全量 19 点）

| 现有系统 | 集成方式 | 数据流向 | 注释 |
|---------|---------|---------|------|
| **Phase Manager** (43 checks) | 结构审计维度的底层执行器 | Orchestrator �?PhaseGate | |
| **Gate Engine** (20 gates) | G0 入口 + 红白对抗的蓝方判�?| Orchestrator �?GateEngine | |
| **Code Dedup Engine** (MOD-INF-017) | 孤儿判定"功能重复检�? + DIM-DUP-001 | Orchestrator �?DedupEngine | |
| **Audit Trail** (MOD-INF-020) | 编排过程全部决策记录 + Merkle根哈�?| Orchestrator �?AuditTrail | |
| **Asset Inventory** (MOD-INF-026) | Phase 1 发现的目标清单来�?| Orchestrator �?AssetIndex | |
| **Drift Detector** (MOD-INF-023) | DIM-SSoT 维度的漂移信�?| Orchestrator �?DriftDetector | |
| **Feedback Loop** (MOD-INF-010) | 审计发现回写规则演进 + 新反模式→自动生成门�?| Orchestrator �?FLE | |
| **LLM Security** (MOD-INF-014) | L2 LLM 修复的安全性校�?| Orchestrator �?LLMSecurity | |
| **Lock Protocol** (RULE-ZERO) | 修复操作的互斥保�?| Orchestrator �?lock_files | |
| **Git** | Phase 3 快照 + Phase 4 回滚 | Orchestrator �?git | |
| **Blueprint Code Auditor** (`shared/`) | DIM-SSoT 的蓝图→代码对齐检�?| Orchestrator �?BlueprintCodeAuditor | v1.0.0 新增 |
| **Compliance Matrix** (`governance/`) | 审计结果→合规框�?ISO27001/SOC2)映射 | Orchestrator �?ComplianceMatrix | v1.0.0 新增 |
| **Rollback Auditor** (`governance/rollback/`) | Git回滚后的状态正确性验�?| Orchestrator �?RollbackAuditor | v1.0.0 新增 |
| **Legal Audit Chain** (`agent_rbac/`) | 审计过程的法律合规证据链 | Orchestrator �?LegalAuditChain | v1.0.0 新增 |
| **Dependency Auditor** (`agent_rbac/`) | DIM-DEP-001 跨模块依赖一致�?| Orchestrator �?DependencyAuditor | v1.0.0 新增 |
| **Tamper-Proof Audit** (`drift_detector/`) | 审计报告不可篡改保证 | Orchestrator �?TamperProofAudit | v1.0.0 新增 |
| **Spec Auditor** (`governance/audit_trail/`) | 蓝图规范与实际实现一致�?| Orchestrator �?SpecAuditor | v1.0.0 新增 |
| **MCP Governance Server** | 对外暴露 audit_orchestrator 操作�?MCP 端点 | Orchestrator �?MCP calls | v1.0.0 新增 |
| **KB Unified Memory** (MOD-KB-001) | 审计发现/模式/模板自动写入知识�?| Orchestrator �?KB | v1.0.0 新增 |

---

## 13. 施工路线�?
### Phase 0 �?骨架搭建（P0�?
| 任务 | 产出 | depends_on |
|------|------|-----------|
| 创建 AuditOrchestrator 核心�?| `orchestrator.py` | |
| 实现 PhaseController 四阶段调度（DISCOVER→TRIAGE→REPAIR→ENFORCE）调�?| `phase_controller.py` | |
| 实现 Discovery 引擎（增量版�?| `discovery.py` | |
| 实现 IncrementalCache（Hash指纹�?| `incremental_cache.py` | |
| 实现 17 个审计维度配�?| `builtin_dimensions.yaml` | |
| 集成 phase_check_registry | �?43 checks | MOD-INF-007 |
| 实现 AuditScheduler（cron/Webhook�?| `scheduler.py` | |
| 实现 BehavioralAuditor（审计追踪+漂移检测）| `behavioral_auditor.py` | MOD-INF-020, MOD-INF-023 |
| 实现 CircuitBreaker（熔断器�?| `circuit_breaker.py` | |

### Phase 1 �?核心创新落地（P1�?
| 任务 | 产出 | depends_on |
|------|------|-----------|
| 集成 SemanticAuditor 调度（peer 服务）| orchestrator �?MOD-INF-028 | MOD-INF-028 |
| 集成 OrphanJudge 调度 | orchestrator �?MOD-INF-029 | MOD-INF-029 |
| 集成 AutoFixEngine 调度 | orchestrator �?MOD-INF-031 | MOD-INF-031 |
| 实现 GitBackupManager + 回滚审计 | `git_backup.py` | MOD-GOV-ROLLBACK-001 |
| 实现 NonConvergenceHandler | `non_convergence.py` | |
| 集成 MOD-INF-020 Audit Trail | 全量记录 | MOD-INF-020 |
| 实现 ScaleAuditor（DIM-SCALE-001）| `scale_auditor.py` | 目录平铺检测 + churn分析 + 大文件检测 + max-depth |
| 实现 AdrAuditor（DIM-ADR-001）| `adr_auditor.py` | ADR编号连续性 + 洋葱引用 + frontmatter status + 关联模块注册表 |
| 实现 ConstructionAuditor（DIM-CONSTRUCTION-001）| `construction_auditor.py` | 蓝图vs施工进度 + milestone不倒退 + 任务卡batch_id + 超期报警 |
| 实现 DocAuditor（DIM-DOC-001）| `doc_auditor.py` | frontmatter字段合规 + 模板章节 + 破窗检测 + 编码UTF-8 |
| 实现 SessionAuditor（DIM-SESSION-001）| `session_auditor.py` | Session Log字段 + 边界规则(<=8 files, <=3 dirs) + handoff |
| 实现 19 个集成桥�?| 全部集成�?| |

### Phase 2 �?验证闭环（P2�?
| 任务 | 产出 | depends_on |
|------|------|-----------|
| 集成 RedBlueValidator | orchestrator �?MOD-INF-030 | MOD-INF-030 |
| 实现 Knowledge Layer（PatternLearner + RuleEvolver + FixTemplateDB�?| `knowledge/` | |
| 实现 TelemetryExporter（Prometheus�?| `telemetry.py` | MOD-INF-015 |
| 实现 ReportGenerator（JSON/HTML/趋势�?| `reporting.py` | |
| Trae IDE 对话驱动模式 | Agent Skill 激�?| |
| JSON API 模式（Roo Code�?| `--json` CLI | |
| 全自�?Loop 模式 | `--auto` CLI | |
| 交叉覆盖矩阵生成�?| 覆盖率报�?| |
| 灾难恢复演练自动�?| `disaster_recovery.py` | |
| DORA 指标采集 | `dora_collector.py` | |

---

## 14. 测试策略

| 层级 | 范围 | 预期 |
|------|------|------|
| **单元** | Discovery / IncrementalCache / ShellDetector / MetaAuditor / GitBackup / CircuitBreaker / Knowledge | >90% 覆盖 |
| **集成** | 单维度完整流程——发现→审计→修复→收敛 | 17 个维度全�?|
| **金丝雀** | 10% 资产全量审计 | 收敛 < 5min |
| **E2E** | 全项目全维度审计 | 收敛 < 30min |
| **红蓝专项** | 7 个攻击场�?100% 防住 + 自生长攻击库 | 无绕�?|
| **回滚演练** | 审计中�?git checkout pre-tag 恢复 �?rollback_auditor 验证 | 状态完全恢�?|
| **熔断演练** | 单维度注入卡�?�?CircuitBreaker 触发 �?audit 继续 | 其他维度不受影响 |
| **增量验证** | 修改 1 文件 �?增量审计 �?仅审计该文件 | 正确跳过未变 |
| **Meta-Audit** | orchestrator 自身文件扫描 �?确认已注�?| 零孤�?|
| **遥测端到�?* | 审计全流�?�?Prometheus metrics 导出 �?Grafana 可消�?| 指标完整 |

---

## 15. 风险与缓解（全量�?
| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| **Doom Loop**——修复→新问题→修复→循�?| �?| �?| max_passes 硬上�?+ NonConvergenceHandler + max_global_rounds=3 |
| **孤儿误判**——有价值文件被判为"删除" | �?| �?| Git pre-tag可回�?+ 判定置信度阈�?+ 人工复核 + OrphanJudge SafetyFence |
| **语义审计误报** | �?| �?| 触发条件100%机械（文件存在�?数值比�?ID匹配�?|
| **红方攻击遗漏**——攻击场景不完整 | �?| �?| 攻击自生长库 + 每次绕过自动录入新场�?|
| **审计性能**—�?4373 资产全量扫描 | �?| �?| 增量Hash指纹跳过未变文件 + ThreadPoolExecutor(RULE-SEVEN) |
| **收敛不了**——设计权衡问�?| �?| �?| YELLOW 可接�?+ 人工最终裁�?|
| **Circuit Breaker**——维度检�?hang 导致 audit 卡死 | �?| �?| 单维�?5min 超时 �?CircuitBreaker OPEN �?跳过该维�?�?report 标记 |
| **两个 AI 同时触发审计** | �?| �?| lock_files 全局审计锁（`audit-global.lock`�? 排队机制 |
| **增量缓存损坏**——HashIndex 不可�?| �?| �?| 缓存校验失败 �?自动退回全量模�?|
| **大面积误�?*——OrphanJudge + AutoFixEngine 连锁 | �?| �?| Git pre-tag 一键回�?+ rollback_auditor 验证 |
| **KB 写入失败**——知识积累中�?| �?| �?| 失败不阻塞审计主流程，下次审计补�?|
| **元审计死循环**——Meta-Audit 发现自身问题 �?修复 �?自身变更 �?重新 Meta-Audit | �?| �?| DIM-META-001 收敛=1，只审一�?�?结构性问题极�?|
| **命名规范大面积漂�?*——DIM-NAMING-001 首次运行发现 N+ 违规 | �?| �?| 首批自动修复（大写→小写/去版本后缀�? 后续增量仅审变更文件 |
| **路径违规积压**——DIM-PATH-001 发现多年累积废弃路径/根目录违�?| �?| �?| 白名单外文件→自动移 `.audit_cache/` + 分类报告 �?人工批量处置 |
| **架构不可扩展**——当前结构无法支�?1,500 模块增长 | �?| �?| DIM-ARCH-001 ScalabilityProjector 提前预警 + 自动子目录化建议 + 每季度跑一次全量架构可扩展性审�?|
| **代码质量滑坡**——DIM-CODE-001 首次运行发现 N+ 违规（缺类型注解/import */Decimal误用等） | �?| �?| 第一批自动修复（isort+展开import *�? 后续增量仅审变更文件 |
| **安全漏洞泄漏**——DIM-SECURITY-001 发现硬编码密钥或危险命令 | �?| �?| **硬阻�?CI** �?人工立即轮换密钥 + 代码中替换为环境变量 |
| **状态机腐败**——DIM-LIFECYCLE-001 发现模块状态跳转不合法或任务关闭不完整 | �?| �?| 自动修复（UTF-8转换/LF统一/临时文件清除�? 报告非法状态迁移详�?|
| **规模漂移触发阈值告警**——DIM-SCALE-001 首次运行发现多个大目录/超大文件 | 高 | 高 | 首批自动平铺检测 + churn Top-N 报告 → 人工评估是否需要子目录化 |
| **ADR 链断裂**——DIM-ADR-001 发现缺失 ADR 编号/洋葱引用断裂/frontmatter 无 status | 中 | 高 | 自动生成 ADR 模板 + 报告缺失链 → 人工补写 + 后续增量检测 |
| **施工进度欺诈**——DIM-CONSTRUCTION-001 发现 milestone 倒退/batch_id 错乱/超期未闭 | 低 | 高 | 硬阻断 CI（milestone 倒退）+ 自动报警超期任务 → 人工核查进度真实性 |
| **文档破窗扩散**——DIM-DOC-001 发现 frontmatter 字段缺失/模板章节空/编码非 UTF-8 | 高 | 中 | 首批自动修复（编码/LF统一）+ 破窗标记 → 后续增量强制校验 |
| **Session Log 质量滑坡**——DIM-SESSION-001 发现边界违规/Log 缺失/handoff 断裂 | 高 | 高 | Session 边界硬阻断（>8 files 拒绝）+ Log 缺失自动报警 → Owner 介入 |

---

## 16. 成功指标�? DORA 对标�?
| 指标 | 目标 | 测量 | 对标 |
|------|------|------|------|
| 全局收敛时间 | < 30min | start �?converged | DORA Lead Time for Changes |
| 增量收敛时间 | < 5min | start �?converged (incremental) | |
| L1自动修复�?| > 90% | auto_fixed/total | DORA Change Failure Rate(�?�? |
| L1+L2修复�?| > 98% | (auto+llm)/total | |
| 红白对抗通过�?| 100% | blocked/total_scenarios | Netflix Chaos Monkey |
| 交叉覆盖�?| �?3 维度/文件 | coverage_matrix | |
| 孤儿误判�?| < 2% | 人工抽查 | |
| Doom Loop 发生�?| = 0 | max_passes触发次数 | |
| Git回滚成功�?| 100% | 回滚演练 + rollback_auditor | |
| Meta-Audit GREEN�?| 100% | DIM-META-001 | SOC2 auditor independence |
| 增量缓存命中�?| > 80% | unchanged/(total) | |
| 熔断阻断不扩散率 | 100% | 其他维度不受单维度hang影响 | Netflix Hystrix |

### 16.1 DORA 四指标映�?
| DORA 指标 | MDIAE 映射 | 目标 |
|-----------|-----------|------|
| **Deployment Frequency** | 审计频率（cron间隔�?| �?1/day |
| **Change Failure Rate** | RED issue / total checks | < 5% |
| **Mean Time to Recovery** | 平均修复轮数 | < 3 rounds |
| **Lead Time for Changes** | 发现问题→修复完�?| < 30min |

---

## 17. MAPE-K 知识积累层（Knowledge Layer�?
> **这是 MAPE-K 循环中此前缺失的 K�?*

### 17.1 三层知识结构

```
Knowledge Layer:
  ├─ L1: PatternLearner (历史模式识别)
  �?  ├─ 哪些文件�?惯犯"？（3次以上被标记�?  �?  ├─ 哪些维度最常挂？（按失败频率排序→优化Phase 2检查顺序）
  �?  ├─ 哪些规则最常被触发？（→调整规则粒度）
  �?  └─ 产出: FrequentFailureReport �?推�?FLE (MOD-INF-010)
  �?  ├─ L2: RuleEvolver (规则自演�?
  �?  ├─ 审计发现新反模式 �?自动生成 Rule Proposal
  �?  ├─ Rule Proposal �?推�?FLE �?经Owner批准 �?转换为正�?Gate
  �?  ├─ 规则过时检�?�?自动标记 DEPRECATED
  �?  └─ 产出: RuleEvolutionBatch �?不直接落地，必须经Owner确认
  �?  └─ L3: FixTemplateDB (修复方案模板�?
      ├─ 同类修复方案自动聚类
      ├─ 模板匹配 �?新问题尝试匹配已有修复模�?      ├─ L1 自动修复率从 90% 渐进�?99%
      └─ 产出: FixTemplate �?AutoFixEngine 消费
```

### 17.2 PatternLearner 算法

```python
class PatternLearner:
    def learn(self, history: list[GlobalAuditReport]) -> list[AuditPatternRecord]:
        patterns: list[AuditPatternRecord] = []

        # 1. 重复违规检测：同一文件 3 次审计中都被标记
        repeat_offenders = self._find_repeat_offenders(history, min_occurrences=3)

        # 2. 薄弱维度检测：某维度连�?N 次审计失败率 > 50%
        weak_dimensions = self._find_weak_dimensions(history, threshold=0.5)

        # 3. 新反模式检测：从未出现�?issue 类型首次出现
        new_patterns = self._detect_new_patterns(history[-1], history[:-1])

        return patterns
```

### 17.3 Code Dedup 扩展 �?BUILT-IN-005 覆盖

> **`src/zephyr/l01_infrastructure/code_dedup_engine/`** 已覆盖功能重复检�?+ 简洁性审计。Orchestrator �?DIM-DUP-001 直接调用�?`cluster_analysis`�?
---

## 18. 增量审计与缓存策略（IncrementalAuditCache�?
### 18.1 Hash 指纹缓存

```
.audit_cache/
  ├─ hash_index.json        # {file_path: {sha256, mtime, size}}
  ├─ dimension_results/     # �?dim_id 缓存上次检查结�?  �?  ├─ DIM-TYPE-001.json
  �?  └─ ...
  └─ README.md              # "此目录由 MDIAE 管理，请勿手动修�?
```

### 18.2 缓存失效策略

| 触发条件 | 行为 |
|---------|------|
| 文件 `mtime` 变更 | 该文件所有维度缓存失�?|
| 检查器代码更新（`sha256(checker.py)` != 上次�?| 该维度全部缓存失�?|
| 规则文件更新（`project_rules.md` mtime 变更?| DIM-RULE-001 + dispatch MOD-INF-028 |
| 缓存文件自身 Hash 不匹�?| 全量回退 |
| 缓存超过 7 �?| 强制执行一次全量（刷新基线�?|

### 18.3 增量实现

```python
class IncrementalAuditCache:
    def should_skip(self, file_path: str, dim_id: str) -> bool:
        current_hash = self._hash_file(file_path)
        cached_hash = self._get_cached_hash(file_path)
        cached_dim_result = self._get_cached_dim_result(file_path, dim_id)

        return (current_hash == cached_hash
                and cached_dim_result is not None
                and cached_dim_result.converged)

    def update(self, file_path: str, dim_id: str, result: DimensionResult):
        ...
```

---

## 19. 审计调度与触发器（AuditScheduler�?
### 19.1 四种触发方式

| 触发方式 | 条件 | 命令/配置 |
|---------|------|---------|
| **手动** | 用户主动触发 | `python scripts/audit.py` / Trae 对话"开始审�? |
| **Cron 定时** | 每日凌晨 2:00 | `0 2 * * * python scripts/audit.py --auto` |
| **Git Hook** | `git push` �?pre-push hook | `.git/hooks/pre-push` 脚本 |
| **文件变更** | Watchdog 监听 �?N 个文件变更后 5min 防抖触发 | `watchdog + debounce` |

### 19.2 Cron 配置

```yaml
# config/audit_schedule.yaml
schedule:
  - name: "nightly-full"
    cron: "0 2 * * *"
    mode: full
    auto_fix: true
    notify: "session-continuity"

  - name: "hourly-incremental"
    cron: "0 * * * *"
    mode: incremental
    auto_fix: true
    notify: "none"

  - name: "weekly-deep"
    cron: "0 3 * * 0"    # 每周�?3AM
    mode: deep            # 强制全量 + 红白对抗
    auto_fix: true
    notify: "owner"
```

### 19.3 Pipeline 集成

```yaml
# Pipeline stage: pre-deploy-audit
- stage: audit-gate
  id: PRE-DEPLOY-AUDIT
  depends_on: [build, test]
  command: "python scripts/audit.py --incremental --json --fail-on-red"
  on_failure: BLOCK_DEPLOY
```

---

## 20. 自审�?�?Meta-Audit（DIM-META-001�?
> **"Quis custodiet ipsos custodes?" �?谁审计审计器自身�?*

### 20.1 Meta-Audit 四问

| # | 问题 | 检查方�?|
|---|------|---------|
| 1 | `src/zephyr/audit_orchestrator/` 下所�?.py 文件是否已注册到 `__init__.py.__all__` �?| �?DIM-TYPE-001 |
| 2 | `builtin_dimensions.yaml` 中声明的每个 dim_id 是否有对应的实现�?| dim_id→checker 映射存在�?|
| 3 | Orchestrator 自身�?`blueprint.md` 是否�?module-registry 中？ | MOD-INF-027 条目存在�?|
| 4 | 审计日志（Audit Trail）是否已�?Merkle 根哈�?+ 不可变校验？ | MOD-INF-020 + TamperProofAudit |

### 20.2 Meta-Audit 边界

> **Meta-Audit 不做语义审计——不�?Orchestrator 的设计是否合�?这种判断。它只做结构审计—�?Orchestrator 是否遵守了它自己要求别人遵守的注册规�?�?*

---

## 21. 可观测性与遥测（Observability & Telemetry�?
### 21.1 Prometheus 指标导出

```
# HELP zalpha_audit_dimension_passes_total Total passes per dimension
# TYPE zalpha_audit_dimension_passes_total counter
zalpha_audit_dimension_passes_total{dim="DIM-TYPE-001"} 4

# HELP zalpha_audit_issues_found_total Total issues found (by severity)
# TYPE zalpha_audit_issues_found_total gauge
zalpha_audit_issues_found_total{severity="RED"} 3
zalpha_audit_issues_found_total{severity="YELLOW"} 2

# HELP zalpha_audit_global_converged Whether global audit converged
# TYPE zalpha_audit_global_converged gauge
zalpha_audit_global_converged{audit_id="20260508-001"} 1

# HELP zalpha_audit_entropy_velocity System entropy velocity
# TYPE zalpha_audit_entropy_velocity gauge
zalpha_audit_entropy_velocity 0.0

# HELP zalpha_audit_circuit_breaker_state Circuit breaker state per dimension
# TYPE zalpha_audit_circuit_breaker_state gauge
zalpha_audit_circuit_breaker_state{dim="DIM-TYPE-001"} 0  # 0=CLOSED, 1=OPEN, 2=HALF_OPEN

# HELP zalpha_audit_cache_hit_ratio Incremental cache hit ratio
# TYPE zalpha_audit_cache_hit_ratio gauge
zalpha_audit_cache_hit_ratio 0.85
```

### 21.2 SLO 定义

| SLO | 目标 | 测量窗口 |
|-----|------|---------|
| 审计可用�?| 99% audit runs complete without crash | 7d |
| 收敛成功�?| > 95% audits converge within max_rounds | 30d |
| 修复延迟 | L1 fixes < 1s, L2 fixes < 5s | per-run |
| Cache 一致�?| 100% cache matches actual file state | per-run |

---

## 22. 报告与可视化（Reporting & Visualization�?
### 22.1 三种报告格式

| 格式 | 消费�?| 触发 |
|------|--------|------|
| **JSON** (`--json`) | AI session / Roo Code / API | 每次审计 |
| **Markdown** (`--report`) | Owner 人工阅读 | 审计结束 |
| **HTML Trend** (`--trend`) | Grafana 面板嵌入 | �?7 �?|
| **Compliance PDF** (`--compliance`) | 合规审计（ISO27001/SOC2证据）| 每季�?|

### 22.2 趋势对比

```
audit-20260501 vs audit-20260508:
  ├─ RED issues: 23 �?15 (-35%) �?熵减
  ├─ YELLOW issues: 8 �?8 (─)
  ├─ Orphan count: 21 �?12 (-43%)
  ├─ Shell count: 59 �?0 (-100%) �?  └─ Converged: NO �?YES �?```

---

## 23. 维度扩展插件接口（DimensionProvider Plugin�?
```python
from abc import ABC, abstractmethod

class DimensionProvider(ABC):
    """第三方审计维度必须实现的接口"""

    @property
    @abstractmethod
    def dim_id(self) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def axis(self) -> str: ...

    @abstractmethod
    def audit(self, targets: list[str]) -> DimensionResult: ...

    @abstractmethod
    def can_incremental(self) -> bool: ...

    @classmethod
    def discover(cls) -> list[type["DimensionProvider"]]:
        """自动发现所�?DimensionProvider 子类——不依赖手工注册"""
        ...
```

### 23.1 维度注册

```yaml
# 内置维度: builtin_dimensions.yaml
# 扩展维度: config/audit_extensions.d/ (YAML + Python插件)
extensions:
  - provider: "my_org.custom_audit.MyDimension"
    dim_id: "DIM-CUSTOM-001"
    enabled: true
```

---

## 24. 错误恢复与熔断（CircuitBreaker & Error Recovery�?
### 24.1 CircuitBreaker 三态模型（Netflix Hystrix 模式�?
```
         ┌──────────────────────────�?         �?        CLOSED           �?         �? (正常执行, 计数失败)     �?         └────────┬─────────────────�?                  �?failure_count >= threshold (5)
                  �?         ┌──────────────────────────�?         �?         OPEN            �?         �? (跳过维度, 记录 SKIP)    │──── timeout (30s) ────�?         └──────────────────────────�?                       �?                                                            �?         ┌──────────────────────────�?         �?      HALF_OPEN          �?         �? (试探性执�?1 �?        �?         └────────┬─────────────────�?                  �?success �?CLOSED / failure �?OPEN
```

```python
class AuditCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 30):
        self.state: dict[str, str] = {}   # dim_id �?CLOSED|OPEN|HALF_OPEN
        self.failure_count: dict[str, int] = {}

    def before_dimension(self, dim_id: str) -> bool:
        """返回 False = SKIP 该维�?""
        ...

    def after_dimension(self, dim_id: str, success: bool):
        ...
```

### 24.2 部分审计恢复

```python
# 如果 Phase 1 发现阶段成功�?Phase 2 DIM-TYPE-002 挂掉�?# �?其余维度继续 �?最终报告标�?DIM-TYPE-002=SKIPPED(CircuitBreaker)
# �?下次审计自动优先执行 SKIPPED 维度
```

---

## 25. CLI 入口�?MCP 端点

### 25.1 CLI 签名

```
python scripts/audit.py [OPTIONS]

OPTIONS:
  --mode       full|incremental|deep       审计模式
  --auto       全自主运行（不交互）         Phase auto-run
  --json       JSON 输出（AI/Roo Code消费�?  --report     生成 Markdown 报告
  --warn-only  仅审计不修复
  --fail-on-red  RED �?exit 1
  --dim DIM-ID  仅运行指定维�?  --dry-run    仅发现不�?  --schedule   作为 cron daemon 运行
  --port PORT  Prometheus metrics 端口
```

### 25.2 MCP 端点（集成到 `mcp/governance_server.py`�?
```python
# MCP Tool: governance.run_audit
@mcp.tool()
async def run_audit(
    mode: str = "incremental",
    dimensions: list[str] | None = None,
    auto_fix: bool = True,
) -> dict:
    """
    触发全量/增量审计�?
    Args:
        mode: "full" | "incremental" | "deep"
        dimensions: 指定维度，None = 全部
        auto_fix: 是否自动修复

    Returns:
        GlobalAuditReport (dict)
    """
    ...

# MCP Tool: governance.audit_status
@mcp.tool()
async def audit_status() -> dict:
    """查询最近一次审计状�?+ entropy_velocity"""
    ...

# MCP Tool: governance.audit_history
@mcp.tool()
async def audit_history(limit: int = 10) -> list[dict]:
    """返回最�?N 次审计摘�?""
    ...
```

---

## 26. Agent Skill 注册�?AI 发现协议

> **核心问题：新 AI session 怎么知道 MDIAE 存在？怎么触发�?*

### 26.1 Skill 注册（必须写入的文件�?
| 文件 | 条目 | 目的 |
|------|------|------|
| `src/zephyr/agent_spec/skill_registry.yaml` | 注册 `audit-orchestrator` skill | AI session 通过 `agent_spec list` 发现 |
| `docs/registry-of-registries.yaml` | REG-MOD-001 �?MOD-INF-027 | 通过模块注册表发�?|
| `docs/03_modules/module-registry.yaml` | MOD-INF-027 v1.0.0 | 版本 + 路径 + 依赖 |
| `src/zephyr/__init__.py` | `from zephyr.audit_orchestrator import AuditOrchestrator` | import 发现 |
| ColdStart STEP 4.6 | 加入 `audit-orchestrator` 到关键词路由 | 冷启动时 AI 知道它存�?|
| Enforcement Matrix | 新增"运行全量审计"→触�?audit_orchestrator | 强制集成对照�?|
| MCP `governance_server.py` | 新增 `run_audit` / `audit_status` / `audit_history` tool | MCP 可调�?|

### 26.2 AI Session 发现流程

```
�?AI session 进入 �?  STEP 4.6: agent_spec list �?看到 audit-orchestrator
  �?  STEP 4.6: progressive_load("audit-orchestrator") �?加载蓝图摘要(§1+§12)
  �?  AI 知道:
    · 什么时候需�? �?看到孤儿/重复/规则问题�?    · 怎么触发?   �?"开始全量审�? / python scripts/audit.py
    · 会做什�?   �?四阶段闭环验证�?    · 依赖什�?   �?MOD-INF-007/017/020/023/026/028/029/030/031
```

### 26.3 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| �?| Skill 注册了但 ColdStart 不引�?| AI session 知道它但不会主动想起用它 |
| �?| CLI 有了�?MCP 没有 | Roo Code/外部 Agent 无法通过 API 触发 |
| �?| 施工完成后不跑一次审计验�?| 写了不用 = 孤儿功能（RULE-TWO�?|

---

## 27. 跨模块依赖审计（DIM-DEP-001�?
> **问题：A 模块声明�?depends_on B 模块，B 模块是否存在？版本是否匹配？**

```yaml
# DIM-DEP-001 审计流程
Step 1: 枚举所有模块的 depends_on / references
Step 2: 对每�?target:
  ├─ �?module_id �?module-registry.yaml 中存在？
  ├─ blueprint 文件存在且可读？
  ├─ 引用�?§ 章节号存在？
  └─ 构造依赖图 �?检测循环依�?Step 3: 输出 DependencyHealthReport
```

### 27.1 集成 MOD-INF-018 DependencyAuditor

```python
# 使用 agent_rbac/dependency_auditor.py 做底层检�?from zephyr.agent_rbac.dependency_auditor import DependencyAuditor

auditor = DependencyAuditor()
for module in registered_modules:
    for dep in module.depends_on:
        result = auditor.check(dep.target, module.module_id)
        if not result.exists:
            issues.append(BROKEN_DEPENDENCY)
        if not result.version_match:
            issues.append(VERSION_MISMATCH)
```

---

## 28. 审计历史模式学习（Audit History ML�?
### 28.1 模式类型

| 模式类型 | 检测方�?| 产出 |
|---------|---------|------|
| **Repeat Offender** | 同一文件连续 �? 次审计被标记 RED | �?推送到 FLE，建议硬编码规则 |
| **Weak Dimension** | 某维度连�?�? 次审计失败率 > 50% | �?检查该维度检查器是否过于严苛 |
| **Improvement Trend** | RED issue 数量连续下降 | �?系统熵减，记录为正反�?|
| **Degradation Trend** | RED issue 数量连续上升 | �?系统熵增，告�?Owner |
| **New Anti-Pattern** | 从未出现�?issue 类型首次被检�?| �?PatternLearner 记录 �?RuleEvolver 提议新规�?|

### 28.2 趋势数据存储

```
data/audit_history/
  ├─ audit-20260508-001.json    # 每次审计的完整报�?  ├─ trends.json                 # 聚合趋势数据（PatternLearner 消费�?  └─ README.md
```

---

## 29. 红线预算与性能约束（Redline Budget & Performance�?
### 29.1 时间预算

| 审计模式 | 目标时间 | 硬上�?| 超时处置 |
|---------|---------|--------|---------|
| **Incremental** | < 5min | 15min | 跳过剩余维度 �?报告 PARTIAL |
| **Full** | < 30min | 60min | CircuitBreaker �?报告 PARTIAL |
| **Deep** | < 60min | 120min | 红白对抗可能超时，结构审计不应超 |

### 29.2 漂移预算（集�?MOD-INF-023�?
> `check_budget_for_gate("MOD-INF-027")` �?passed? �?可审计。BLOCKED? �?先修旧漂移�?
### 29.3 并发限制

```
- 同时最�?1 个全量审�?- 增量审计可并发（不同 dim 无锁冲突�?- 审计修复阶段 MUST 遵守 RULE-ZERO 锁协�?```

---

## 30. 灾难恢复演练（Disaster Recovery Drill�?
### 30.1 三种灾难场景

| 场景 | 描述 | 恢复方式 | 验证 |
|------|------|---------|------|
| **DR-1: 大面积误�?* | AutoFixEngine 误删 > 10 文件 | `git checkout audit-*-pre` | rollback_auditor 逐文件Hash验证 |
| **DR-2: 注册表损�?* | `module-registry.yaml` 被写�?| `git checkout audit-*-pre -- docs/03_modules/module-registry.yaml` | DIM-SSoT-001 一致性检�?|
| **DR-3: Cache 中毒** | `.audit_cache/` Hash 全错 | 删除 `.audit_cache/` �?强制全量 | 重新生成HashIndex后校�?|

### 30.2 自动化演�?
```python
# tests/disaster_recovery/test_dr_scenarios.py
def test_dr1_mass_delete_rollback():
    """模拟 20 文件被误�?�?git checkout pre-tag �?rollback_auditor 验证"""
    ...
```

---

## 31. 合规框架映射（Compliance Framework Mapping�?
### 31.1 ISO 27001 映射

| ISO 27001 控制�?| MDIAE 映射 |
|-----------------|-----------|
| A.8.1 资产责任 | DIM-FIELD-001 (owner字段唯一�? |
| A.8.2 信息分类 | blueprint.classification 字段审计 |
| A.12.1 操作规程 | DIM-TYPE-001 (脚本注册完整�? |
| A.12.4 管理员活动日�?| MOD-INF-020 Audit Trail |
| A.12.7 信息系统审计 | DIM-META-001 (自审�? |
| A.14.2 安全开发策�?| DIM-SSoT-001 (SSoT与代码对�? |

### 31.2 SOC2 映射

| SOC2 信任服务标准 | MDIAE 映射 |
|-------------------|-----------|
| Security | DIM-TYPE-001~003 (注册+门禁完整�? |
| Availability | §21 SLO (审计可用�?99%) |
| Processing Integrity | MOD-INF-028 (SemanticAuditor, peer dispatch) |
| Confidentiality | G-CT-001 (RBAC权限校验) |
| Privacy | Legal Audit Chain (agent_rbac/) |

---

## 32. 成熟度模型与演进路线（Maturity Model�?
### 32.1 43 维成熟度评分（当�?v4.0.0 设计完成度）

| 维度 | 权重 | v0.1.0 | v0.4.1 | v1.0.0 | 目标 |
|------|:---:|:---:|:---:|:---:|:---:|
| **蓝图设计** | | | | | |
| 四阶段闭环 | 5 | �?100% | �?100% | �?100% | 100% |
| MAPE-K Knowledge | 5 | �?0% | �?0% | �?100% | 100% |
| 增量Hash指纹 | 4 | �?0% | �?0% | �?100% | 100% |
| Cron调度/Webhook | 3 | �?0% | �?0% | �?100% | 100% |
| Meta-Audit自审�?| 3 | �?0% | �?0% | �?100% | 100% |
| 维度扩展插件 | 2 | �?0% | �?0% | �?100% | 100% |
| CircuitBreaker熔断 | 3 | �?0% | �?0% | �?100% | 100% |
| Prometheus遥测 | 3 | �?0% | �?0% | �?100% | 100% |
| DORA指标对标 | 2 | �?0% | �?0% | �?100% | 100% |
| 报告多维格式 | 2 | �?0% | �?0% | �?100% | 100% |
| CLI+MCP双入�?| 3 | �?0% | �?0% | �?100% | 100% |
| Agent Skill自发�?| 4 | �?0% | �?0% | �?100% | 100% |
| 跨模块依赖审�?| 3 | �?0% | �?0% | �?100% | 100% |
| 审计历史模式学习 | 3 | �?0% | �?0% | �?100% | 100% |
| 灾难恢复演练 | 2 | �?0% | �?0% | �?100% | 100% |
| 合规框架映射 | 2 | �?0% | �?0% | �?100% | 100% |
| **v1.1.0 新增维度** | | | | | |
| 架构结构审计 (DIM-ARCH-001) | 4 | �?| �?| �?| 100% |
| 命名规范审计 (DIM-NAMING-001) | 3 | �?| �?| �?| 100% |
| 路径强制审计 (DIM-PATH-001) | 3 | �?| �?| �?| 100% |
| 1500模块可扩展性保�?| 3 | �?| �?| �?| 100% |
| **v1.2.0 新增维度** | | | | | |
| 代码施工标准审计 (DIM-CODE-001) | 4 | �?| �?| �?| 100% |
| 安全红线审计 (DIM-SECURITY-001) | 4 | �?| �?| �?| 100% |
| 生命周期状态机审计 (DIM-LIFECYCLE-001) | 3 | �?| �?| �?| 100% |
| **v4.0.0 新增维度** | | | | | |
| 规模漂移审计 (DIM-SCALE-001) | 4 | — | — | — | 100% |
| ADR 文档链审计 (DIM-ADR-001) | 3 | — | — | — | 100% |
| 施工进度审计 (DIM-CONSTRUCTION-001) | 4 | — | — | — | 100% |
| 文档合规审计 (DIM-DOC-001) | 3 | — | — | — | 100% |
| Session 质量审计 (DIM-SESSION-001) | 4 | — | — | — | 100% |
| **集成系统** | | | | | |
| Phase Manager(43) | 2 | �?0% | �?100% | �?100% | 100% |
| Gate Engine(20) | 2 | �?0% | �?100% | �?100% | 100% |
| Code Dedup Engine | 2 | �?0% | �?100% | �?100% | 100% |
| Audit Trail | 2 | �?0% | �?100% | �?100% | 100% |
| Asset Inventory | 2 | �?0% | �?100% | �?100% | 100% |
| Drift Detector | 2 | �?0% | �?100% | �?100% | 100% |
| FLE Feedback Loop | 2 | �?0% | �?100% | �?100% | 100% |
| LLM Security | 2 | �?0% | �?100% | �?100% | 100% |
| Agent RBAC | 1 | �?0% | �?0% | �?100% | 100% |
| MCP Governance Server | 2 | �?0% | �?0% | �?100% | 100% |
| KB Unified Memory | 2 | �?0% | �?0% | �?100% | 100% |
| Pipeline | 1 | �?0% | �?0% | �?100% | 100% |
| System Telemetry | 1 | �?0% | �?0% | �?100% | 100% |
| Blueprint Code Auditor | 1 | �?0% | �?0% | �?100% | 100% |
| Compliance Matrix | 1 | �?0% | �?0% | �?100% | 100% |
| Rollback Auditor | 1 | �?0% | �?0% | �?100% | 100% |

> **v1.0.0 蓝图设计成熟度 = 32/32 × 100% = 100%。v1.1.0 新增 3 维度 → 35/35 = 100%。v1.2.0 新增 3 维度（DIM-CODE-001/DIM-SECURITY-001/DIM-LIFECYCLE-001）→ 38/38 = 100%。v4.0.0 新增 5 维度（SCALE/ADR/CONSTRUCTION/DOC/SESSION）+ 四阶段架构重构 → 43/43 = 100%。** 后续工作是施工——将蓝图转化为实际代码。
### 32.2 成熟度演进路�?
```
v0.1.0 (2026-05-08) ─ 初创蓝图�?2章，�?00�?v0.2.0 (2026-05-08) ─ 语义审计+最小风险协�?三层验证
v0.3.0 (2026-05-08) ─ 模块拆分:MOD-INF-028独立
v0.4.0 (2026-05-08) ─ 模块拆分:MOD-INF-029/030/031独立，纯编排
v0.4.1 (2026-05-08) ─ +shell_detection空壳检�?v1.0.0 (2026-05-08) ─ 全量补全:32章，33项差距修复，100%成熟�?v1.1.0 (2026-05-08) ─ +架构结构审计(DIM-ARCH-001)+命名规范审计(DIM-NAMING-001)+路径强制审计(DIM-PATH-001)�?5/35=100%
v1.2.0 (2026-05-08) ─ +代码施工标准(DIM-CODE-001)+安全红线(DIM-SECURITY-001)+生命周期状态机(DIM-LIFECYCLE-001)�?8/38=100%
v4.0.0 (2026-05-08) ─ +四阶段架构重构(六→四)+Structural/Semantic/Behavioral三类型+5新维度(SCALE/ADR/CONSTRUCTION/DOC/SESSION)+SemanticAuditor升为peer服务+43/43=100%

施工:
  Phase 0 (P0) ─ 骨架搭建:核心类+发现引擎+增量缓存+17维度配置+BehavioralAuditor
  Phase 1 (P1) ─ 创新落地:4子系统集成+5新维度审计器+19集成桥接
  Phase 2 (P2) ─ 验证闭环:Knowledge Layer+Telemetry+Report+DORA+DR
```

---

## A. 附录：注册表集成清单（一次性全部写入）

> **施工�?MUST 按此清单逐一落盘——一个不漏�?*

| # | 文件 | 操作 | 内容 |
|---|------|------|------|
| 1 | `src/zephyr/agent_spec/skill_registry.yaml` | 新增条目 | `audit-orchestrator` skill（关键词: 审计/audit/合规/孤儿/红白�?|
| 2 | `docs/registry-of-registries.yaml` | 确认 REG-MOD-001 �?MOD-INF-027 | module_id 已在列表�?|
| 3 | `docs/03_modules/module-registry.yaml` | 更新版本 | v0.4.1 �?v1.0.0 |
| 4 | `src/zephyr/audit_orchestrator/__init__.py` | 创建 | `__all__` 导出所有核心类 |
| 5 | `src/zephyr/__init__.py` | 新增 import | `from zephyr.audit_orchestrator import AuditOrchestrator` |
| 6 | ColdStart STEP 4.6 | 新增关键词路�?| `"审计" �?progressive_load("audit-orchestrator")` |
| 7 | Enforcement Matrix | 新增条目 | `"运行全量审计" �?python scripts/audit.py --auto` |
| 8 | `src/zephyr/mcp/governance_server.py` | 新增 MCP tool | `run_audit` / `audit_status` / `audit_history` |
| 9 | `scripts/script_manifest.yaml` | 新增条目 | `scripts/audit.py` CLI 入口 |
| 10 | KB bootstrap `run_bootstrap()` | 审计完成后写�?KE | `kb.write(topic="audit_patterns", ...)` |
| 11 | `gates/_registry.yaml` | 新增 gate | G-AUDIT-001: "MDIAE 审计编排器自检" |
| 12 | Pipeline `pipeline_orchestrator.py` | 新增 stage | `PRE-DEPLOY-AUDIT` |

> **以上 12 项全部落盘后，下一�?AI session 才能通过 ColdStart �?agent_spec list �?progressive_load �?发现 audit-orchestrator�?*

---

## B. 附录：对标矩�?
| 对标系统 | MDIAE 对应组件 | 创新�?|
|---------|---------------|--------|
| **AWS Config** | Phase 1 发现 + Phase 2 结构审计 | +增量Hash指纹 +shell_detection |
| **K8s Reconciliation** | Phase 4 收敛闭环 | +分层验证(结构≠语义≠红白) +不收敛处�?|
| **Netflix Chaos Monkey** | Phase 4 红白对抗(MOD-INF-030) | +自生长攻击库 |
| **IBM MAPE-K** | §1.3 MAPE-K映射 + §17 Knowledge Layer | +PatternLearner +RuleEvolver +FixTemplateDB |
| **SonarQube** | Phase 2 17 个结构维�?| +语义审计(独有) +元审�?独有) |
| **OPA Gatekeeper** | DIM-RULE-001 规则交叉引用 | +双向对齐验证(规则 ←→ 实现) |
| **DORA Metrics** | §16.1 DORA 四指标映�?| audit metrics �?ALTER TABLE change metrics |
| **Google SRE** | §21 SLO/SLI + §29 红线预算 | Error Budget �?drift budget |
| **Prometheus/Grafana** | §21 Prometheus 指标 + §22 HTML Trend 报告 | +entropy_velocity 指标(独有) |
| **Goldman SecDB** | Phase 4 Git tag + freeze | +rollback_auditor 验证 |
| **SOC2/ISO27001** | §31 合规框架映射 | audit �?compliance matrix |
