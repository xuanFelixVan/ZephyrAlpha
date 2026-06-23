---
doc_type: domain_architecture_doc
title: D-BEHAVIORAL_AUDIT 行为审计架构文档
version: "1.0"
status: active
date: 2026-06-23
owner: auto-generator
ttl: permanent
---

# D-BEHAVIORAL_AUDIT 行为审计架构文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-23 13:28:28
> 数据源: depgraph.db nodes表 + edges表

## 域概览

| 属性 | 值 |
|------|-----|
| 域ID | D-BEHAVIORAL_AUDIT |
| 域名称 | 行为审计 |
| 架构层 | L1_foundation |
| 模块总数 | 60 |
| 设计态模块 | 0 |
| 原型态模块 | 0 |
| 生产态模块 | 60 |
| 容量 | 60/150 (正常) |
| 描述 | 行为审计域(从D-SECURITY拆出,behavioral_auditor) |

## 模块清单

共 60 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 蓝图ID | 构建状态 | 设计成熟度 | 入度 | 出度 |
|---------|--------|---------|-----------|:---:|:---:|
| src/zephyr/behavioral_audit/absence_manager.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/ai_construction_detectors.py | MOD-INF-033 | draft | production | 6 | 1 |
| src/zephyr/behavioral_audit/ai_context_injector.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/architecture_contracts.py | MOD-INF-023 | draft | production | 2 | 0 |
| src/zephyr/behavioral_audit/architecture_principles.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/backcompat_checker.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/baseline_manager.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/baseline_poisoning_guard.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/benchmark_integrity.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/brain_integration.py | MOD-INF-033 | draft | production | 1 | 8 |
| src/zephyr/behavioral_audit/canary_controller.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/cascade_detector.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/chaos_injector.py | MOD-INF-033 | draft | production | 6 | 1 |
| src/zephyr/behavioral_audit/code_review_ai.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/config_consistency.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/contract_drift_detector.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/correlation_engine.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/credibility_engine.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/cross_env_consistency.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/cross_module_score.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/dashboard.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/data_classification.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/data_lifecycle.py | MOD-INF-023 | draft | production | 2 | 0 |
| src/zephyr/behavioral_audit/data_source_reliability.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/dependency_manager.py | MOD-INF-023 | draft | production | 2 | 0 |
| src/zephyr/behavioral_audit/detector_dispatcher.py | MOD-INF-033 | draft | production | 3 | 1 |
| src/zephyr/behavioral_audit/drift_cron_scheduler.py | MOD-INF-033 | draft | production | 1 | 2 |
| src/zephyr/behavioral_audit/drift_engine.py | MOD-INF-033 | draft | production | 17 | 4 |
| src/zephyr/behavioral_audit/drift_hotfix_bypass.py | MOD-INF-033 | draft | production | 6 | 1 |
| src/zephyr/behavioral_audit/drift_infrastructure.py | MOD-INF-033 | draft | production | 12 | 1 |
| src/zephyr/behavioral_audit/drift_models.py | MOD-INF-033 | draft | production | 26 | 0 |
| src/zephyr/behavioral_audit/drift_result_types.py | MOD-INF-033 | draft | production | 4 | 2 |
| src/zephyr/behavioral_audit/drift_training.py | MOD-INF-033 | draft | production | 3 | 1 |
| src/zephyr/behavioral_audit/file_attr_checker.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/forensics_engine.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/gate_persistence.py | MOD-INF-033 | draft | production | 3 | 1 |
| src/zephyr/behavioral_audit/git_bisector.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/gitignore_auditor.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/handoff_manager.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/headless_scanner.py | MOD-INF-033 | draft | production | 3 | 1 |
| src/zephyr/behavioral_audit/incremental_scanner.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/ml_engineering.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/model_drift_monitor.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/naming_magic_checker.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/orphan_scanner.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/performance_baseline.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/python_compat.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/regime_detector.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/resource_guard.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/roi_engine.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/rollback_bridge.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/scan_mutex.py | MOD-INF-033 | draft | production | 3 | 1 |
| src/zephyr/behavioral_audit/self_check.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/self_test_verifier.py | MOD-INF-033 | draft | production | 4 | 0 |
| src/zephyr/behavioral_audit/suppression_learner.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/symlink_checker.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/system_topology.py | MOD-INF-023 | draft | production | 1 | 0 |
| src/zephyr/behavioral_audit/tamper_proof_audit.py | MOD-INF-033 | draft | production | 3 | 1 |
| src/zephyr/behavioral_audit/test_fixture_checker.py | MOD-INF-033 | draft | production | 3 | 0 |
| src/zephyr/behavioral_audit/trend_analyzer.py | MOD-INF-033 | draft | production | 3 | 1 |

## 跨域依赖

### 本域依赖的其他域（出边）

| 目标域 | 依赖数 | 依赖类型 |
|--------|:---:|---------|
| D-INTEGRATION | 3 | import_depends |
| D-GOVERNANCE | 3 | import_depends |
| D-SHARED | 1 | import_depends |
| D-GOV_AUDIT | 1 | import_depends |

### 依赖本域的其他域（入边）

| 源域 | 依赖数 | 依赖类型 |
|------|:---:|---------|
| D-GOVERNANCE | 103 | test_depends,import_depends |
| D-SECURITY | 51 | import_depends |
| D-OPS | 2 | import_depends,runtime |
| D-TRADING | 1 | import_depends |
| D-INFRA_RUNTIME | 1 | import_depends |
| D-GOV_RULE | 1 | import_depends |
| D-GOV_AUDIT | 1 | import_depends |

## 域内依赖图

详见 [d_behavioral_audit_dependency.mmd](d_behavioral_audit_dependency.mmd)
