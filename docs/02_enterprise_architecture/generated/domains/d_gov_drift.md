---
doc_type: domain_architecture_doc
title: D-GOV_DRIFT drift_detection架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-GOV_DRIFT drift_detection架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-GOV_DRIFT |
| 域名称 | drift_detection |
| 架构层 | L2_domain |
| 模块总数 | 22 |
| 设计态模块 | 0 |
| 原型态模块 | 0 |
| 生产态模块 | 22 |
| 容量 | 22/200 (正常) |
| 描述 | 39个漂移检测器注册与调度 |

## 模块清单

共 22 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| docs/01_policies_and_standards/_registry/catalogs/script_health_registry.yaml | DOM-GOV-001 | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_016_arch_drift_detection.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| .../01_policies_and_standards/rules/trae_035_task_construction_verification.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| docs/01_policies_and_standards/rules/trae_039_ai_hallucination_detection.yaml | MOD-GOV-DOCS | orphan | production | 0 | 0 |
| scripts/governance/d11_compliance/validate_blueprint_overlap.py | MOD-GOV-SCRIPTS | draft | production | 2 | 0 |
| scripts/governance/d11_compliance/validate_truth_source_cascade.py | MOD-GOV-SCRIPTS | draft | production | 2 | 0 |
| scripts/governance/d5_architecture/validators/validate_authority_registry.py | MOD-GOV-SCRIPTS-ARCH | draft | production | 2 | 0 |
| scripts/governance/d5_architecture/validators/validate_ssot.py | MOD-GOV-SCRIPTS-ARCH | draft | production | 2 | 1 |
| src/zephyr/governance/artifact_scanner.py | MOD-L10-001 | draft | production | 2 | 0 |
| src/zephyr/governance/audit_orchestrator/integrity.py | MOD-INF-027 | draft | production | 2 | 3 |
| src/zephyr/governance/audit_trail/drift_bridge.py | MOD-INF-027 | draft | production | 8 | 1 |
| src/zephyr/governance/audit_trail/self_monitor.py | MOD-INF-027 | draft | production | 6 | 1 |
| src/zephyr/governance/drift_detection/_detector_registry.yaml | MOD-INF-023 | orphan | production | 0 | 0 |
| src/zephyr/governance/drift_detection/migration_plan.yaml | MOD-INF-023 | orphan | production | 0 | 0 |
| src/zephyr/governance/integrity.py | MOD-INF-027 | draft | production | 14 | 3 |
| src/zephyr/governance/red_blue_validator/ai_self_diagnosis.py | SRC-066 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/breaking_change_detector.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/gate_health.py | MOD-INF-007 | draft | production | 2 | 0 |
| src/zephyr/governance/rule_enforcement/gate_integrity_guard.py | MOD-INF-007 | draft | production | 2 | 0 |
| ...zephyr/governance/rule_enforcement/invariants/en_002_enforcement_validator.py | MOD-INF-007 | draft | production | 3 | 1 |
| ...phyr/governance/rule_enforcement/invariants/en_002_enforcement_validator.yaml | MOD-INF-007 | orphan | production | 0 | 0 |
| src/zephyr/governance/rule_enforcement/truth_source_validator.py | MOD-INF-007 | draft | production | 1 | 2 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-GOV_AUDIT | 6 | import_depends |
| D-GOVERNANCE | 3 | import_depends |
| D-INTEGRATION | 2 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 36 | test_depends,import_depends,config_depends |
| D-GOV_AUDIT | 6 | import_depends |
| D-GOV_RULE | 4 | import_depends |
| D-TRADING | 2 | import_depends |
| D-COMPLIANCE | 2 | import_depends |
| D-OPS | 1 | import_depends |

## 域内依赖图

详见 [d_gov_drift_dependency.mmd](d_gov_drift_dependency.mmd)
