---
doc_type: domain_architecture_diagram
title: D-GOV_DRIFT 漂移检测架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 38_d_gov_drift / 漂移检测 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示漂移检测（D-GOV_DRIFT）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 20:00:20
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 漂移检测（D-GOV_DRIFT）的模块分布。共 25 个模块 / 25 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (24 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   docs__03_modules___domain_governance__drift_detector__bluep... │
│   scripts/governance/d5_architecture/validators/validate_auth... │
│   scripts/governance/d5_architecture/validators/validate_ssot... │
│   src/zephyr/governance/artifact_scanner.py  [production]        │
│   src/zephyr/governance/audit_orchestrator/integrity.py  [pro... │
│   src/zephyr/governance/audit_trail/drift_bridge.py  [product... │
│   src/zephyr/governance/audit_trail/self_monitor.py  [product... │
│   src/zephyr/governance/drift_detection/baseline_manager.py  ... │
│   src/zephyr/governance/drift_detection/chaos_injector.py  [p... │
│   src/zephyr/governance/drift_detection/migration_plan.yaml  ... │
│   src/zephyr/governance/drift_detector.py  [prototype]           │
│   src/zephyr/governance/integrity.py  [production]               │
│   src/zephyr/governance/red_blue_validator/ai_self_diagnosis.... │
│   tests/test_ba_chaos_injector.py  [prototype]                   │
│   tests/test_baseline_manager.py  [prototype]                    │
│   tests/test_chaos_injector.py  [prototype]                      │
│   tests/test_context_drift_detector.py  [prototype]              │
│   tests/test_contract_drift_detector.py  [prototype]             │
│   ...还有 6 个模块 / 6 more modules                              │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (1 modules)                 │
├──────────────────────────────────────────────────────────────────┤
│   F6-drift-detector/  [design]                                   │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 25 个模块 / 25 modules）。

### L1 基础层 / Foundation Layer (24 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | docs/03_modules/_domain_governance/drift_detector/bluepri... | docs__03_modules___domain_governance_... | design | planned |
| 2 | scripts/governance/d5_architecture/validators/validate_au... | scripts/governance/d5_architecture/va... | production | generated |
| 3 | scripts/governance/d5_architecture/validators/validate_ss... | scripts/governance/d5_architecture/va... | production | generated |
| 4 | src/zephyr/governance/artifact_scanner.py | src/zephyr/governance/artifact_scanne... | production | generated |
| 5 | src/zephyr/governance/audit_orchestrator/integrity.py | src/zephyr/governance/audit_orchestra... | production | generated |
| 6 | src/zephyr/governance/audit_trail/drift_bridge.py | src/zephyr/governance/audit_trail/dri... | production | generated |
| 7 | src/zephyr/governance/audit_trail/self_monitor.py | src/zephyr/governance/audit_trail/sel... | production | generated |
| 8 | src/zephyr/governance/drift_detection/baseline_manager.py | src/zephyr/governance/drift_detection... | prototype | generated |
| 9 | src/zephyr/governance/drift_detection/chaos_injector.py | src/zephyr/governance/drift_detection... | prototype | generated |
| 10 | src/zephyr/governance/drift_detection/migration_plan.yaml | src/zephyr/governance/drift_detection... | production | deprecated |
| 11 | src/zephyr/governance/drift_detector.py | src/zephyr/governance/drift_detector.py | prototype | generated |
| 12 | src/zephyr/governance/integrity.py | src/zephyr/governance/integrity.py | production | generated |
| 13 | src/zephyr/governance/red_blue_validator/ai_self_diagnosi... | src/zephyr/governance/red_blue_valida... | production | generated |
| 14 | tests/test_ba_chaos_injector.py | tests/test_ba_chaos_injector.py | prototype | generated |
| 15 | tests/test_baseline_manager.py | tests/test_baseline_manager.py | prototype | generated |
| 16 | tests/test_chaos_injector.py | tests/test_chaos_injector.py | prototype | generated |
| 17 | tests/test_context_drift_detector.py | tests/test_context_drift_detector.py | prototype | generated |
| 18 | tests/test_contract_drift_detector.py | tests/test_contract_drift_detector.py | prototype | generated |
| 19 | tests/test_drift_detector_ee.py | tests/test_drift_detector_ee.py | prototype | generated |
| 20 | tests/test_drift_detector_gate.py | tests/test_drift_detector_gate.py | prototype | generated |
| 21 | tests/test_model_drift_detector.py | tests/test_model_drift_detector.py | prototype | generated |
| 22 | tests/unit/drift_detector/__init__.py | tests/unit/drift_detector/__init__.py | prototype | generated |
| 23 | tests/unit/drift_detector/conftest.py | tests/unit/drift_detector/conftest.py | prototype | generated |
| 24 | tests/unit/drift_detector/test_drift_core.py | tests/unit/drift_detector/test_drift_... | prototype | generated |

### 未分类 / Unclassified (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F6-drift-detector/ | F6-drift-detector/ | design | stable |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 2 条 / 2 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│        依赖关系图 / Dependency Graph (共 2 条 / 2 edges)         │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 1 条 / edges                                 │
│   [config_depends]: 1 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   self_monitor.py → drift_bridge.py                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (1 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   conftest.py → __init__.py                                      │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `38_d_gov_drift_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
