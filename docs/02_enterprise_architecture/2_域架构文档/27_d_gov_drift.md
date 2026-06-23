---
doc_type: domain_architecture_doc
title: D-GOV_DRIFT drift_detection架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 27_d_gov_drift 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 27 | Number | 27 |
| 域ID | D-GOV_DRIFT | Domain ID | D-GOV_DRIFT |
| 域名称 | drift_detection | Domain Name | drift_detection |
| 层级 | L2_domain | Layer | L2_domain |
| 模块数 | 38 | Module Count | 38 |
| 域内依赖 | 2 | Internal Dependencies | 2 |
| 跨域入边 | 65 | Cross-domain Incoming | 65 |
| 跨域出边 | 39 | Cross-domain Outgoing | 39 |
| 设计态模块 | 1 | Design Modules | 1 |
| 原型态模块 | 15 | Prototype Modules | 15 |
| 生产态模块 | 22 | Production Modules | 22 |
| 容量 | 38/200 (正常) | Capacity | 38/200 (正常) |
| 描述 | 39个漂移检测器注册与调度 | Description | 39个漂移检测器注册与调度 |

## 模块清单 / Module List

共 38 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| docs/01_policies_and_standards/_registry/catalogs/script_health_registry.yaml |  | production | orphan | docs/01_policies_and_standards/_registry/catalogs/script_health_registry.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml |  | production | orphan |
| .../01_policies_and_standards/rules/trae_035_task_construction_verification.yaml |  | production | orphan | .../01_policies_and_standards/rules/trae_035_task_construction_verification.yaml |  | production | orphan |
| docs/01_policies_and_standards/rules/trae_039_ai_hallucination_detection.yaml |  | production | orphan | docs/01_policies_and_standards/rules/trae_039_ai_hallucination_detection.yaml |  | production | orphan |
| docs/03_modules/_domain_governance/drift_detector/blueprint.md | docs__03_modules___domain_governance_... | design | design_only | docs/03_modules/_domain_governance/drift_detector/blueprint.md | docs__03_modules___domain_governance_... | design | design_only |
| scripts/governance/d11_compliance/validate_blueprint_overlap.py |  | production | draft | scripts/governance/d11_compliance/validate_blueprint_overlap.py |  | production | draft |
| scripts/governance/d11_compliance/validate_truth_source_cascade.py |  | production | draft | scripts/governance/d11_compliance/validate_truth_source_cascade.py |  | production | draft |
| scripts/governance/d5_architecture/validators/validate_authority_registry.py |  | production | draft | scripts/governance/d5_architecture/validators/validate_authority_registry.py |  | production | draft |
| scripts/governance/d5_architecture/validators/validate_ssot.py |  | production | draft | scripts/governance/d5_architecture/validators/validate_ssot.py |  | production | draft |
| src/zephyr/governance/artifact_scanner.py |  | production | draft | src/zephyr/governance/artifact_scanner.py |  | production | draft |
| src/zephyr/governance/audit_orchestrator/integrity.py |  | production | draft | src/zephyr/governance/audit_orchestrator/integrity.py |  | production | draft |
| src/zephyr/governance/audit_trail/drift_bridge.py |  | production | draft | src/zephyr/governance/audit_trail/drift_bridge.py |  | production | draft |
| src/zephyr/governance/audit_trail/self_monitor.py |  | production | draft | src/zephyr/governance/audit_trail/self_monitor.py |  | production | draft |
| src/zephyr/governance/drift_detection/_detector_registry.yaml |  | production | orphan | src/zephyr/governance/drift_detection/_detector_registry.yaml |  | production | orphan |
| src/zephyr/governance/drift_detection/baseline_manager.py |  | prototype | draft | src/zephyr/governance/drift_detection/baseline_manager.py |  | prototype | draft |
| src/zephyr/governance/drift_detection/chaos_injector.py |  | prototype | draft | src/zephyr/governance/drift_detection/chaos_injector.py |  | prototype | draft |
| src/zephyr/governance/drift_detection/migration_plan.yaml |  | production | orphan | src/zephyr/governance/drift_detection/migration_plan.yaml |  | production | orphan |
| src/zephyr/governance/drift_detector.py |  | prototype | draft | src/zephyr/governance/drift_detector.py |  | prototype | draft |
| src/zephyr/governance/integrity.py |  | production | draft | src/zephyr/governance/integrity.py |  | production | draft |
| src/zephyr/governance/red_blue_validator/ai_self_diagnosis.py |  | production | draft | src/zephyr/governance/red_blue_validator/ai_self_diagnosis.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/breaking_change_detector.py |  | production | draft | src/zephyr/governance/rule_enforcement/breaking_change_detector.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/drift_detector.py |  | prototype | draft | src/zephyr/governance/rule_enforcement/drift_detector.py |  | prototype | draft |
| src/zephyr/governance/rule_enforcement/gate_health.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_health.py |  | production | draft |
| src/zephyr/governance/rule_enforcement/gate_integrity_guard.py |  | production | draft | src/zephyr/governance/rule_enforcement/gate_integrity_guard.py |  | production | draft |
| ...zephyr/governance/rule_enforcement/invariants/en_002_enforcement_validator.py |  | production | draft | ...zephyr/governance/rule_enforcement/invariants/en_002_enforcement_validator.py |  | production | draft |
| ...phyr/governance/rule_enforcement/invariants/en_002_enforcement_validator.yaml |  | production | orphan | ...phyr/governance/rule_enforcement/invariants/en_002_enforcement_validator.yaml |  | production | orphan |
| src/zephyr/governance/rule_enforcement/truth_source_validator.py |  | production | draft | src/zephyr/governance/rule_enforcement/truth_source_validator.py |  | production | draft |
| tests/test_ba_chaos_injector.py |  | prototype | draft | tests/test_ba_chaos_injector.py |  | prototype | draft |
| tests/test_baseline_manager.py |  | prototype | draft | tests/test_baseline_manager.py |  | prototype | draft |
| tests/test_chaos_injector.py |  | prototype | draft | tests/test_chaos_injector.py |  | prototype | draft |
| tests/test_context_drift_detector.py |  | prototype | draft | tests/test_context_drift_detector.py |  | prototype | draft |
| tests/test_contract_drift_detector.py |  | prototype | draft | tests/test_contract_drift_detector.py |  | prototype | draft |
| tests/test_drift_detector_ee.py |  | prototype | draft | tests/test_drift_detector_ee.py |  | prototype | draft |
| tests/test_drift_detector_gate.py |  | prototype | draft | tests/test_drift_detector_gate.py |  | prototype | draft |
| tests/test_model_drift_detector.py |  | prototype | draft | tests/test_model_drift_detector.py |  | prototype | draft |
| tests/unit/drift_detector/__init__.py |  | prototype | draft | tests/unit/drift_detector/__init__.py |  | prototype | draft |
| tests/unit/drift_detector/conftest.py |  | prototype | draft | tests/unit/drift_detector/conftest.py |  | prototype | draft |
| tests/unit/drift_detector/test_drift_core.py |  | prototype | draft | tests/unit/drift_detector/test_drift_core.py |  | prototype | draft |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

```mermaid
graph TD
    subgraph D_GOV_DRIFT["D-GOV_DRIFT drift_detection"]
        docs_01_policies_and_standards_registry_catalogs_script_health_registry_yaml["docs/01_policies_and_standards/_registry/catalo... production"]
        docs_01_policies_and_standards_rules_trae_016_arch_drift_detection_yaml["docs/01_policies_and_standards/rules/trae_016_a... production"]
        docs_01_policies_and_standards_rules_trae_035_task_construction_verification_yaml["docs/01_policies_and_standards/rules/trae_035_t... production"]
        docs_01_policies_and_standards_rules_trae_039_ai_hallucination_detection_yaml["docs/01_policies_and_standards/rules/trae_039_a... production"]
        docs_03_modules_domain_governance_drift_detector_blueprint_md["docs__03_modules___domain_governance__drift_det... design"]
        scripts_governance_d11_compliance_validate_blueprint_overlap_py["scripts/governance/d11_compliance/validate_blue... production"]
        scripts_governance_d11_compliance_validate_truth_source_cascade_py["scripts/governance/d11_compliance/validate_trut... production"]
        scripts_governance_d5_architecture_validators_validate_authority_registry_py["scripts/governance/d5_architecture/validators/v... production"]
        scripts_governance_d5_architecture_validators_validate_ssot_py["scripts/governance/d5_architecture/validators/v... production"]
        src_zephyr_governance_artifact_scanner_py["src/zephyr/governance/artifact_scanner.py production"]
        src_zephyr_governance_audit_orchestrator_integrity_py["src/zephyr/governance/audit_orchestrator/integr... production"]
        src_zephyr_governance_audit_trail_drift_bridge_py["src/zephyr/governance/audit_trail/drift_bridge.py production"]
        src_zephyr_governance_audit_trail_self_monitor_py["src/zephyr/governance/audit_trail/self_monitor.py production"]
        src_zephyr_governance_drift_detection_detector_registry_yaml["src/zephyr/governance/drift_detection/_detector... production"]
        src_zephyr_governance_drift_detection_baseline_manager_py["src/zephyr/governance/drift_detection/baseline_... prototype"]
        src_zephyr_governance_drift_detection_chaos_injector_py["src/zephyr/governance/drift_detection/chaos_inj... prototype"]
        src_zephyr_governance_drift_detection_migration_plan_yaml["src/zephyr/governance/drift_detection/migration... production"]
        src_zephyr_governance_drift_detector_py["src/zephyr/governance/drift_detector.py prototype"]
        src_zephyr_governance_integrity_py["src/zephyr/governance/integrity.py production"]
        src_zephyr_governance_red_blue_validator_ai_self_diagnosis_py["src/zephyr/governance/red_blue_validator/ai_sel... production"]
        src_zephyr_governance_rule_enforcement_breaking_change_detector_py["src/zephyr/governance/rule_enforcement/breaking... production"]
        src_zephyr_governance_rule_enforcement_drift_detector_py["src/zephyr/governance/rule_enforcement/drift_de... prototype"]
        src_zephyr_governance_rule_enforcement_gate_health_py["src/zephyr/governance/rule_enforcement/gate_hea... production"]
        src_zephyr_governance_rule_enforcement_gate_integrity_guard_py["src/zephyr/governance/rule_enforcement/gate_int... production"]
        src_zephyr_governance_rule_enforcement_invariants_en_002_enforcement_validator_py["src/zephyr/governance/rule_enforcement/invarian... production"]
        src_zephyr_governance_rule_enforcement_invariants_en_002_enforcement_validator_yaml["src/zephyr/governance/rule_enforcement/invarian... production"]
        src_zephyr_governance_rule_enforcement_truth_source_validator_py["src/zephyr/governance/rule_enforcement/truth_so... production"]
        tests_test_ba_chaos_injector_py["tests/test_ba_chaos_injector.py prototype"]
        tests_test_baseline_manager_py["tests/test_baseline_manager.py prototype"]
        tests_test_chaos_injector_py["tests/test_chaos_injector.py prototype"]
    end
    src_zephyr_governance_audit_trail_self_monitor_py -->|import_depends| src_zephyr_governance_audit_trail_drift_bridge_py
    D_GOVERNANCE["D-GOVERNANCE design"]
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_GOVERNANCE
    D_GOV_AUDIT["D-GOV_AUDIT design"]
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_GOV_AUDIT
    D_AUTONOMY_PERM["D-AUTONOMY_PERM design"]
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_AUTONOMY_PERM
    D_GOV_RULE["D-GOV_RULE production"]
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_GOV_RULE
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_GOVERNANCE
    docs_03_modules_domain_governance_drift_detector_blueprint_md -.->|runtime| D_GOVERNANCE
    src_zephyr_governance_drift_detector_py -.->|config_depends| D_GOVERNANCE
    src_zephyr_governance_integrity_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_governance_integrity_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_governance_integrity_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_governance_audit_orchestrator_integrity_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_governance_audit_orchestrator_integrity_py -.->|import_depends| D_GOV_AUDIT
    src_zephyr_governance_audit_orchestrator_integrity_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_governance_audit_trail_drift_bridge_py -->|import_depends| D_GOVERNANCE
    D_GOV_AUDIT -.->|runtime| docs_03_modules_domain_governance_drift_detector_blueprint_md
    D_GOVERNANCE -.->|runtime| docs_03_modules_domain_governance_drift_detector_blueprint_md
    D_TRADING["D-TRADING prototype"]
    D_TRADING -.->|runtime| docs_03_modules_domain_governance_drift_detector_blueprint_md
    D_GOVERNANCE -.->|contract| docs_03_modules_domain_governance_drift_detector_blueprint_md
    D_GOVERNANCE -.->|runtime| docs_03_modules_domain_governance_drift_detector_blueprint_md
    D_GOVERNANCE -.->|runtime| docs_03_modules_domain_governance_drift_detector_blueprint_md
    D_COMPLIANCE["D-COMPLIANCE prototype"]
    D_COMPLIANCE -.->|import_depends| src_zephyr_governance_artifact_scanner_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_governance_artifact_scanner_py
    D_COMPLIANCE -.->|import_depends| src_zephyr_governance_integrity_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_governance_integrity_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_governance_integrity_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_governance_integrity_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_governance_integrity_py
    D_GOV_AUDIT -->|import_depends| src_zephyr_governance_integrity_py
    D_GOV_AUDIT -->|import_depends| src_zephyr_governance_integrity_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_script_health_registry_yaml,docs_01_policies_and_standards_rules_trae_016_arch_drift_detection_yaml,docs_01_policies_and_standards_rules_trae_035_task_construction_verification_yaml,docs_01_policies_and_standards_rules_trae_039_ai_hallucination_detection_yaml,scripts_governance_d11_compliance_validate_blueprint_overlap_py,scripts_governance_d11_compliance_validate_truth_source_cascade_py,scripts_governance_d5_architecture_validators_validate_authority_registry_py,scripts_governance_d5_architecture_validators_validate_ssot_py,src_zephyr_governance_artifact_scanner_py,src_zephyr_governance_audit_orchestrator_integrity_py,src_zephyr_governance_audit_trail_drift_bridge_py,src_zephyr_governance_audit_trail_self_monitor_py,src_zephyr_governance_drift_detection_detector_registry_yaml,src_zephyr_governance_drift_detection_migration_plan_yaml,src_zephyr_governance_integrity_py,src_zephyr_governance_red_blue_validator_ai_self_diagnosis_py,src_zephyr_governance_rule_enforcement_breaking_change_detector_py,src_zephyr_governance_rule_enforcement_gate_health_py,src_zephyr_governance_rule_enforcement_gate_integrity_guard_py,src_zephyr_governance_rule_enforcement_invariants_en_002_enforcement_validator_py,src_zephyr_governance_rule_enforcement_invariants_en_002_enforcement_validator_yaml,src_zephyr_governance_rule_enforcement_truth_source_validator_py production
    class docs_03_modules_domain_governance_drift_detector_blueprint_md,src_zephyr_governance_drift_detection_baseline_manager_py,src_zephyr_governance_drift_detection_chaos_injector_py,src_zephyr_governance_drift_detector_py,src_zephyr_governance_rule_enforcement_drift_detector_py,tests_test_ba_chaos_injector_py,tests_test_baseline_manager_py,tests_test_chaos_injector_py design
    class D_GOV_RULE external_prod
    class D_GOVERNANCE,D_GOV_AUDIT,D_AUTONOMY_PERM,D_TRADING,D_COMPLIANCE external_design
```

> (依赖图最多显示前 30 个节点，共 38 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 12 | runtime,config_depends,import_depends,test_depends | D-GOVERNANCE | 12 | runtime,config_depends,import_depends,test_depends |
| D-BEHAVIORAL_AUDIT | 11 | import_depends,test_depends | D-BEHAVIORAL_AUDIT | 11 | import_depends,test_depends |
| D-GOV_AUDIT | 8 | runtime,import_depends | D-GOV_AUDIT | 8 | runtime,import_depends |
| D-SECURITY | 3 | import_depends,test_depends | D-SECURITY | 3 | import_depends,test_depends |
| D-INTEGRATION | 3 | import_depends | D-INTEGRATION | 3 | import_depends |
| D-GOV_RULE | 1 | runtime | D-GOV_RULE | 1 | runtime |
| D-AUTONOMY_PERM | 1 | runtime | D-AUTONOMY_PERM | 1 | runtime |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 36 | runtime,contract,test_depends,import_depends,config_depends | D-GOVERNANCE | 36 | runtime,contract,test_depends,import_depends,config_depends |
| D-GOV_AUDIT | 16 | runtime,import_depends,test_depends | D-GOV_AUDIT | 16 | runtime,import_depends,test_depends |
| D-TRADING | 5 | runtime,import_depends | D-TRADING | 5 | runtime,import_depends |
| D-GOV_RULE | 4 | import_depends | D-GOV_RULE | 4 | import_depends |
| D-COMPLIANCE | 2 | import_depends | D-COMPLIANCE | 2 | import_depends |
| D-SECURITY | 1 | import_depends | D-SECURITY | 1 | import_depends |
| D-OPS | 1 | import_depends | D-OPS | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
