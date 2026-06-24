---
doc_type: domain_architecture_diagram
title: D-BEHAVIORAL_AUDIT 行为审计架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 04_d_behavioral_audit / 行为审计 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示行为审计（D-BEHAVIORAL_AUDIT）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 行为审计（D-BEHAVIORAL_AUDIT）的模块分布。共 60 个模块 / 60 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (60 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/behavioral_audit/absence_manager.py  [production]   │
│   src/zephyr/behavioral_audit/ai_construction_detectors.py  [... │
│   src/zephyr/behavioral_audit/ai_context_injector.py  [produc... │
│   src/zephyr/behavioral_audit/architecture_contracts.py  [pro... │
│   src/zephyr/behavioral_audit/architecture_principles.py  [pr... │
│   src/zephyr/behavioral_audit/backcompat_checker.py  [product... │
│   src/zephyr/behavioral_audit/baseline_manager.py  [production]  │
│   src/zephyr/behavioral_audit/baseline_poisoning_guard.py  [p... │
│   src/zephyr/behavioral_audit/benchmark_integrity.py  [produc... │
│   src/zephyr/behavioral_audit/brain_integration.py  [production] │
│   src/zephyr/behavioral_audit/canary_controller.py  [production] │
│   src/zephyr/behavioral_audit/cascade_detector.py  [production]  │
│   src/zephyr/behavioral_audit/chaos_injector.py  [production]    │
│   src/zephyr/behavioral_audit/code_review_ai.py  [production]    │
│   src/zephyr/behavioral_audit/config_consistency.py  [product... │
│   src/zephyr/behavioral_audit/contract_drift_detector.py  [pr... │
│   src/zephyr/behavioral_audit/correlation_engine.py  [product... │
│   src/zephyr/behavioral_audit/credibility_engine.py  [product... │
│   ...还有 42 个模块 / 42 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 60 个模块 / 60 modules）。

### L1 基础层 / Foundation Layer (60 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/behavioral_audit/absence_manager.py | src/zephyr/behavioral_audit/absence_m... | production | draft |
| 2 | src/zephyr/behavioral_audit/ai_construction_detectors.py | src/zephyr/behavioral_audit/ai_constr... | production | draft |
| 3 | src/zephyr/behavioral_audit/ai_context_injector.py | src/zephyr/behavioral_audit/ai_contex... | production | draft |
| 4 | src/zephyr/behavioral_audit/architecture_contracts.py | src/zephyr/behavioral_audit/architect... | production | draft |
| 5 | src/zephyr/behavioral_audit/architecture_principles.py | src/zephyr/behavioral_audit/architect... | production | draft |
| 6 | src/zephyr/behavioral_audit/backcompat_checker.py | src/zephyr/behavioral_audit/backcompa... | production | draft |
| 7 | src/zephyr/behavioral_audit/baseline_manager.py | src/zephyr/behavioral_audit/baseline_... | production | draft |
| 8 | src/zephyr/behavioral_audit/baseline_poisoning_guard.py | src/zephyr/behavioral_audit/baseline_... | production | draft |
| 9 | src/zephyr/behavioral_audit/benchmark_integrity.py | src/zephyr/behavioral_audit/benchmark... | production | draft |
| 10 | src/zephyr/behavioral_audit/brain_integration.py | src/zephyr/behavioral_audit/brain_int... | production | draft |
| 11 | src/zephyr/behavioral_audit/canary_controller.py | src/zephyr/behavioral_audit/canary_co... | production | draft |
| 12 | src/zephyr/behavioral_audit/cascade_detector.py | src/zephyr/behavioral_audit/cascade_d... | production | draft |
| 13 | src/zephyr/behavioral_audit/chaos_injector.py | src/zephyr/behavioral_audit/chaos_inj... | production | draft |
| 14 | src/zephyr/behavioral_audit/code_review_ai.py | src/zephyr/behavioral_audit/code_revi... | production | draft |
| 15 | src/zephyr/behavioral_audit/config_consistency.py | src/zephyr/behavioral_audit/config_co... | production | draft |
| 16 | src/zephyr/behavioral_audit/contract_drift_detector.py | src/zephyr/behavioral_audit/contract_... | production | draft |
| 17 | src/zephyr/behavioral_audit/correlation_engine.py | src/zephyr/behavioral_audit/correlati... | production | draft |
| 18 | src/zephyr/behavioral_audit/credibility_engine.py | src/zephyr/behavioral_audit/credibili... | production | draft |
| 19 | src/zephyr/behavioral_audit/cross_env_consistency.py | src/zephyr/behavioral_audit/cross_env... | production | draft |
| 20 | src/zephyr/behavioral_audit/cross_module_score.py | src/zephyr/behavioral_audit/cross_mod... | production | draft |
| 21 | src/zephyr/behavioral_audit/dashboard.py | src/zephyr/behavioral_audit/dashboard.py | production | draft |
| 22 | src/zephyr/behavioral_audit/data_classification.py | src/zephyr/behavioral_audit/data_clas... | production | draft |
| 23 | src/zephyr/behavioral_audit/data_lifecycle.py | src/zephyr/behavioral_audit/data_life... | production | draft |
| 24 | src/zephyr/behavioral_audit/data_source_reliability.py | src/zephyr/behavioral_audit/data_sour... | production | draft |
| 25 | src/zephyr/behavioral_audit/dependency_manager.py | src/zephyr/behavioral_audit/dependenc... | production | draft |
| 26 | src/zephyr/behavioral_audit/detector_dispatcher.py | src/zephyr/behavioral_audit/detector_... | production | draft |
| 27 | src/zephyr/behavioral_audit/drift_cron_scheduler.py | src/zephyr/behavioral_audit/drift_cro... | production | draft |
| 28 | src/zephyr/behavioral_audit/drift_engine.py | src/zephyr/behavioral_audit/drift_eng... | production | draft |
| 29 | src/zephyr/behavioral_audit/drift_hotfix_bypass.py | src/zephyr/behavioral_audit/drift_hot... | production | draft |
| 30 | src/zephyr/behavioral_audit/drift_infrastructure.py | src/zephyr/behavioral_audit/drift_inf... | production | draft |
| 31 | src/zephyr/behavioral_audit/drift_models.py | src/zephyr/behavioral_audit/drift_mod... | production | draft |
| 32 | src/zephyr/behavioral_audit/drift_result_types.py | src/zephyr/behavioral_audit/drift_res... | production | draft |
| 33 | src/zephyr/behavioral_audit/drift_training.py | src/zephyr/behavioral_audit/drift_tra... | production | draft |
| 34 | src/zephyr/behavioral_audit/file_attr_checker.py | src/zephyr/behavioral_audit/file_attr... | production | draft |
| 35 | src/zephyr/behavioral_audit/forensics_engine.py | src/zephyr/behavioral_audit/forensics... | production | draft |
| 36 | src/zephyr/behavioral_audit/gate_persistence.py | src/zephyr/behavioral_audit/gate_pers... | production | draft |
| 37 | src/zephyr/behavioral_audit/git_bisector.py | src/zephyr/behavioral_audit/git_bisec... | production | draft |
| 38 | src/zephyr/behavioral_audit/gitignore_auditor.py | src/zephyr/behavioral_audit/gitignore... | production | draft |
| 39 | src/zephyr/behavioral_audit/handoff_manager.py | src/zephyr/behavioral_audit/handoff_m... | production | draft |
| 40 | src/zephyr/behavioral_audit/headless_scanner.py | src/zephyr/behavioral_audit/headless_... | production | draft |
| 41 | src/zephyr/behavioral_audit/incremental_scanner.py | src/zephyr/behavioral_audit/increment... | production | draft |
| 42 | src/zephyr/behavioral_audit/ml_engineering.py | src/zephyr/behavioral_audit/ml_engine... | production | draft |
| 43 | src/zephyr/behavioral_audit/model_drift_monitor.py | src/zephyr/behavioral_audit/model_dri... | production | draft |
| 44 | src/zephyr/behavioral_audit/naming_magic_checker.py | src/zephyr/behavioral_audit/naming_ma... | production | draft |
| 45 | src/zephyr/behavioral_audit/orphan_scanner.py | src/zephyr/behavioral_audit/orphan_sc... | production | draft |
| 46 | src/zephyr/behavioral_audit/performance_baseline.py | src/zephyr/behavioral_audit/performan... | production | draft |
| 47 | src/zephyr/behavioral_audit/python_compat.py | src/zephyr/behavioral_audit/python_co... | production | draft |
| 48 | src/zephyr/behavioral_audit/regime_detector.py | src/zephyr/behavioral_audit/regime_de... | production | draft |
| 49 | src/zephyr/behavioral_audit/resource_guard.py | src/zephyr/behavioral_audit/resource_... | production | draft |
| 50 | src/zephyr/behavioral_audit/roi_engine.py | src/zephyr/behavioral_audit/roi_engin... | production | draft |
| 51 | src/zephyr/behavioral_audit/rollback_bridge.py | src/zephyr/behavioral_audit/rollback_... | production | draft |
| 52 | src/zephyr/behavioral_audit/scan_mutex.py | src/zephyr/behavioral_audit/scan_mute... | production | draft |
| 53 | src/zephyr/behavioral_audit/self_check.py | src/zephyr/behavioral_audit/self_chec... | production | draft |
| 54 | src/zephyr/behavioral_audit/self_test_verifier.py | src/zephyr/behavioral_audit/self_test... | production | draft |
| 55 | src/zephyr/behavioral_audit/suppression_learner.py | src/zephyr/behavioral_audit/suppressi... | production | draft |
| 56 | src/zephyr/behavioral_audit/symlink_checker.py | src/zephyr/behavioral_audit/symlink_c... | production | draft |
| 57 | src/zephyr/behavioral_audit/system_topology.py | src/zephyr/behavioral_audit/system_to... | production | draft |
| 58 | src/zephyr/behavioral_audit/tamper_proof_audit.py | src/zephyr/behavioral_audit/tamper_pr... | production | draft |
| 59 | src/zephyr/behavioral_audit/test_fixture_checker.py | src/zephyr/behavioral_audit/test_fixt... | production | draft |
| 60 | src/zephyr/behavioral_audit/trend_analyzer.py | src/zephyr/behavioral_audit/trend_ana... | production | draft |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 12 条 / 12 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 12 条 / 12 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [import_depends]: 12 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (12 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   ai_construction_detectors.py → drift_models.py                 │
│   chaos_injector.py → drift_engine.py                            │
│   detector_dispatcher.py → drift_models.py                       │
│   drift_cron_scheduler.py → drift_engine.py                      │
│   drift_engine.py → drift_models.py                              │
│   drift_engine.py → drift_infrastructure.py                      │
│   drift_infrastructure.py → drift_models.py                      │
│   drift_training.py → drift_models.py                            │
│   drift_result_types.py → drift_engine.py                        │
│   drift_result_types.py → drift_models.py                        │
│   headless_scanner.py → drift_models.py                          │
│   scan_mutex.py → drift_models.py                                │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `04_d_behavioral_audit_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
