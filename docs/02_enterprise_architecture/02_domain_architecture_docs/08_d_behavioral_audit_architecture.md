---
doc_type: domain_architecture_diagram
title: D-BEHAVIORAL_AUDIT 行为审计架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 08_d_behavioral_audit / 行为审计 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示行为审计（D-BEHAVIORAL_AUDIT）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 行为审计（D-BEHAVIORAL_AUDIT）的模块分布。共 79 个模块 / 79 modules。

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
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (19 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   tests/adversarial/test_f3_extreme.py  [production]             │
│   tests/adversarial/test_rollback_concurrent_extreme.py  [pro... │
│   tests/adversarial/test_rollback_partial_extreme.py  [produc... │
│   tests/adversarial/test_rollback_scheduler.py  [production]     │
│   tests/red_blue/__init__.py  [production]                       │
│   tests/red_blue/_test_lock_target.py  [production]              │
│   tests/red_blue/test_async_monitor.py  [production]             │
│   tests/red_blue/test_circuit_breaker.py  [production]           │
│   tests/red_blue/test_constitution_engine.py  [production]       │
│   tests/red_blue/test_context_pipeline_red_blue.py  [production] │
│   tests/red_blue/test_defense_runner.py  [production]            │
│   tests/red_blue/test_event_integration.py  [production]         │
│   tests/red_blue/test_f14_pipeline_extreme.py  [production]      │
│   tests/red_blue/test_f18_governance_adversarial.py  [product... │
│   tests/red_blue/test_f1_extreme.py  [production]                │
│   tests/red_blue/test_game_day_scheduler.py  [production]        │
│   tests/red_blue/test_injection_engine.py  [production]          │
│   tests/red_blue/test_phase_manager_integration.py  [production] │
│   tests/red_blue/test_red_blue_validator.py  [production]        │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 79 个模块 / 79 modules）。

### L1 基础层 / Foundation Layer (60 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/behavioral_audit/absence_manager.py | src/zephyr/behavioral_audit/absence_m... | production | generated |
| 2 | src/zephyr/behavioral_audit/ai_construction_detectors.py | src/zephyr/behavioral_audit/ai_constr... | production | generated |
| 3 | src/zephyr/behavioral_audit/ai_context_injector.py | src/zephyr/behavioral_audit/ai_contex... | production | generated |
| 4 | src/zephyr/behavioral_audit/architecture_contracts.py | src/zephyr/behavioral_audit/architect... | production | generated |
| 5 | src/zephyr/behavioral_audit/architecture_principles.py | src/zephyr/behavioral_audit/architect... | production | generated |
| 6 | src/zephyr/behavioral_audit/backcompat_checker.py | src/zephyr/behavioral_audit/backcompa... | production | generated |
| 7 | src/zephyr/behavioral_audit/baseline_manager.py | src/zephyr/behavioral_audit/baseline_... | production | generated |
| 8 | src/zephyr/behavioral_audit/baseline_poisoning_guard.py | src/zephyr/behavioral_audit/baseline_... | production | generated |
| 9 | src/zephyr/behavioral_audit/benchmark_integrity.py | src/zephyr/behavioral_audit/benchmark... | production | generated |
| 10 | src/zephyr/behavioral_audit/brain_integration.py | src/zephyr/behavioral_audit/brain_int... | production | generated |
| 11 | src/zephyr/behavioral_audit/canary_controller.py | src/zephyr/behavioral_audit/canary_co... | production | generated |
| 12 | src/zephyr/behavioral_audit/cascade_detector.py | src/zephyr/behavioral_audit/cascade_d... | production | generated |
| 13 | src/zephyr/behavioral_audit/chaos_injector.py | src/zephyr/behavioral_audit/chaos_inj... | production | generated |
| 14 | src/zephyr/behavioral_audit/code_review_ai.py | src/zephyr/behavioral_audit/code_revi... | production | generated |
| 15 | src/zephyr/behavioral_audit/config_consistency.py | src/zephyr/behavioral_audit/config_co... | production | generated |
| 16 | src/zephyr/behavioral_audit/contract_drift_detector.py | src/zephyr/behavioral_audit/contract_... | production | generated |
| 17 | src/zephyr/behavioral_audit/correlation_engine.py | src/zephyr/behavioral_audit/correlati... | production | generated |
| 18 | src/zephyr/behavioral_audit/credibility_engine.py | src/zephyr/behavioral_audit/credibili... | production | generated |
| 19 | src/zephyr/behavioral_audit/cross_env_consistency.py | src/zephyr/behavioral_audit/cross_env... | production | generated |
| 20 | src/zephyr/behavioral_audit/cross_module_score.py | src/zephyr/behavioral_audit/cross_mod... | production | generated |
| 21 | src/zephyr/behavioral_audit/dashboard.py | src/zephyr/behavioral_audit/dashboard.py | production | generated |
| 22 | src/zephyr/behavioral_audit/data_classification.py | src/zephyr/behavioral_audit/data_clas... | production | generated |
| 23 | src/zephyr/behavioral_audit/data_lifecycle.py | src/zephyr/behavioral_audit/data_life... | production | generated |
| 24 | src/zephyr/behavioral_audit/data_source_reliability.py | src/zephyr/behavioral_audit/data_sour... | production | generated |
| 25 | src/zephyr/behavioral_audit/dependency_manager.py | src/zephyr/behavioral_audit/dependenc... | production | generated |
| 26 | src/zephyr/behavioral_audit/detector_dispatcher.py | src/zephyr/behavioral_audit/detector_... | production | generated |
| 27 | src/zephyr/behavioral_audit/drift_cron_scheduler.py | src/zephyr/behavioral_audit/drift_cro... | production | generated |
| 28 | src/zephyr/behavioral_audit/drift_engine.py | src/zephyr/behavioral_audit/drift_eng... | production | generated |
| 29 | src/zephyr/behavioral_audit/drift_hotfix_bypass.py | src/zephyr/behavioral_audit/drift_hot... | production | generated |
| 30 | src/zephyr/behavioral_audit/drift_infrastructure.py | src/zephyr/behavioral_audit/drift_inf... | production | generated |
| 31 | src/zephyr/behavioral_audit/drift_models.py | src/zephyr/behavioral_audit/drift_mod... | production | generated |
| 32 | src/zephyr/behavioral_audit/drift_result_types.py | src/zephyr/behavioral_audit/drift_res... | production | generated |
| 33 | src/zephyr/behavioral_audit/drift_training.py | src/zephyr/behavioral_audit/drift_tra... | production | generated |
| 34 | src/zephyr/behavioral_audit/file_attr_checker.py | src/zephyr/behavioral_audit/file_attr... | production | generated |
| 35 | src/zephyr/behavioral_audit/forensics_engine.py | src/zephyr/behavioral_audit/forensics... | production | generated |
| 36 | src/zephyr/behavioral_audit/gate_persistence.py | src/zephyr/behavioral_audit/gate_pers... | production | generated |
| 37 | src/zephyr/behavioral_audit/git_bisector.py | src/zephyr/behavioral_audit/git_bisec... | production | generated |
| 38 | src/zephyr/behavioral_audit/gitignore_auditor.py | src/zephyr/behavioral_audit/gitignore... | production | generated |
| 39 | src/zephyr/behavioral_audit/handoff_manager.py | src/zephyr/behavioral_audit/handoff_m... | production | generated |
| 40 | src/zephyr/behavioral_audit/headless_scanner.py | src/zephyr/behavioral_audit/headless_... | production | generated |
| 41 | src/zephyr/behavioral_audit/incremental_scanner.py | src/zephyr/behavioral_audit/increment... | production | generated |
| 42 | src/zephyr/behavioral_audit/ml_engineering.py | src/zephyr/behavioral_audit/ml_engine... | production | generated |
| 43 | src/zephyr/behavioral_audit/model_drift_monitor.py | src/zephyr/behavioral_audit/model_dri... | production | generated |
| 44 | src/zephyr/behavioral_audit/naming_magic_checker.py | src/zephyr/behavioral_audit/naming_ma... | production | generated |
| 45 | src/zephyr/behavioral_audit/orphan_scanner.py | src/zephyr/behavioral_audit/orphan_sc... | production | generated |
| 46 | src/zephyr/behavioral_audit/performance_baseline.py | src/zephyr/behavioral_audit/performan... | production | generated |
| 47 | src/zephyr/behavioral_audit/python_compat.py | src/zephyr/behavioral_audit/python_co... | production | generated |
| 48 | src/zephyr/behavioral_audit/regime_detector.py | src/zephyr/behavioral_audit/regime_de... | production | generated |
| 49 | src/zephyr/behavioral_audit/resource_guard.py | src/zephyr/behavioral_audit/resource_... | production | generated |
| 50 | src/zephyr/behavioral_audit/roi_engine.py | src/zephyr/behavioral_audit/roi_engin... | production | generated |
| 51 | src/zephyr/behavioral_audit/rollback_bridge.py | src/zephyr/behavioral_audit/rollback_... | production | generated |
| 52 | src/zephyr/behavioral_audit/scan_mutex.py | src/zephyr/behavioral_audit/scan_mute... | production | generated |
| 53 | src/zephyr/behavioral_audit/self_check.py | src/zephyr/behavioral_audit/self_chec... | production | generated |
| 54 | src/zephyr/behavioral_audit/self_test_verifier.py | src/zephyr/behavioral_audit/self_test... | production | generated |
| 55 | src/zephyr/behavioral_audit/suppression_learner.py | src/zephyr/behavioral_audit/suppressi... | production | generated |
| 56 | src/zephyr/behavioral_audit/symlink_checker.py | src/zephyr/behavioral_audit/symlink_c... | production | generated |
| 57 | src/zephyr/behavioral_audit/system_topology.py | src/zephyr/behavioral_audit/system_to... | production | generated |
| 58 | src/zephyr/behavioral_audit/tamper_proof_audit.py | src/zephyr/behavioral_audit/tamper_pr... | production | generated |
| 59 | src/zephyr/behavioral_audit/test_fixture_checker.py | src/zephyr/behavioral_audit/test_fixt... | production | generated |
| 60 | src/zephyr/behavioral_audit/trend_analyzer.py | src/zephyr/behavioral_audit/trend_ana... | production | generated |

### 未分类 / Unclassified (19 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | tests/adversarial/test_f3_extreme.py | tests/adversarial/test_f3_extreme.py | production | generated |
| 2 | tests/adversarial/test_rollback_concurrent_extreme.py | tests/adversarial/test_rollback_concu... | production | generated |
| 3 | tests/adversarial/test_rollback_partial_extreme.py | tests/adversarial/test_rollback_parti... | production | generated |
| 4 | tests/adversarial/test_rollback_scheduler.py | tests/adversarial/test_rollback_sched... | production | generated |
| 5 | tests/red_blue/__init__.py | tests/red_blue/__init__.py | production | generated |
| 6 | tests/red_blue/_test_lock_target.py | tests/red_blue/_test_lock_target.py | production | generated |
| 7 | tests/red_blue/test_async_monitor.py | tests/red_blue/test_async_monitor.py | production | generated |
| 8 | tests/red_blue/test_circuit_breaker.py | tests/red_blue/test_circuit_breaker.py | production | generated |
| 9 | tests/red_blue/test_constitution_engine.py | tests/red_blue/test_constitution_engi... | production | generated |
| 10 | tests/red_blue/test_context_pipeline_red_blue.py | tests/red_blue/test_context_pipeline_... | production | generated |
| 11 | tests/red_blue/test_defense_runner.py | tests/red_blue/test_defense_runner.py | production | generated |
| 12 | tests/red_blue/test_event_integration.py | tests/red_blue/test_event_integration.py | production | generated |
| 13 | tests/red_blue/test_f14_pipeline_extreme.py | tests/red_blue/test_f14_pipeline_extr... | production | generated |
| 14 | tests/red_blue/test_f18_governance_adversarial.py | tests/red_blue/test_f18_governance_ad... | production | generated |
| 15 | tests/red_blue/test_f1_extreme.py | tests/red_blue/test_f1_extreme.py | production | generated |
| 16 | tests/red_blue/test_game_day_scheduler.py | tests/red_blue/test_game_day_schedule... | production | generated |
| 17 | tests/red_blue/test_injection_engine.py | tests/red_blue/test_injection_engine.py | production | generated |
| 18 | tests/red_blue/test_phase_manager_integration.py | tests/red_blue/test_phase_manager_int... | production | generated |
| 19 | tests/red_blue/test_red_blue_validator.py | tests/red_blue/test_red_blue_validato... | production | generated |

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
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `08_d_behavioral_audit_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
