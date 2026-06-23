---
doc_type: domain_architecture_doc
title: D-BEHAVIORAL_AUDIT 行为审计架构文档
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 04_d_behavioral_audit 域文档

> 本文档由 generate_domain_doc.py 从 depgraph.db 自动生成
> 最后更新: 2026-06-24 02:24:12
> 数据源: depgraph.db nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 04 | Number | 04 |
| 域ID | D-BEHAVIORAL_AUDIT | Domain ID | D-BEHAVIORAL_AUDIT |
| 域名称 | 行为审计 | Domain Name | 行为审计 |
| 层级 | L1_foundation | Layer | L1_foundation |
| 模块数 | 60 | Module Count | 60 |
| 域内依赖 | 12 | Internal Dependencies | 12 |
| 跨域入边 | 160 | Cross-domain Incoming | 160 |
| 跨域出边 | 8 | Cross-domain Outgoing | 8 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 0 | Prototype Modules | 0 |
| 生产态模块 | 60 | Production Modules | 60 |
| 容量 | 60/150 (正常) | Capacity | 60/150 (正常) |
| 描述 | 行为审计域(从D-SECURITY拆出,behavioral_auditor) | Description | 行为审计域(从D-SECURITY拆出,behavioral_auditor) |

## 模块清单 / Module List

共 60 个模块（按路径排序，最多显示前 200 个）

| 模块路径 | 模块名称 | 设计成熟度 | 构建状态 | Module Path | Module Name | Maturity | Build Status |
|---------|---------|-----------|---------|-------------|-------------|----------|--------------|
| src/zephyr/behavioral_audit/absence_manager.py |  | production | draft | src/zephyr/behavioral_audit/absence_manager.py |  | production | draft |
| src/zephyr/behavioral_audit/ai_construction_detectors.py |  | production | draft | src/zephyr/behavioral_audit/ai_construction_detectors.py |  | production | draft |
| src/zephyr/behavioral_audit/ai_context_injector.py |  | production | draft | src/zephyr/behavioral_audit/ai_context_injector.py |  | production | draft |
| src/zephyr/behavioral_audit/architecture_contracts.py |  | production | draft | src/zephyr/behavioral_audit/architecture_contracts.py |  | production | draft |
| src/zephyr/behavioral_audit/architecture_principles.py |  | production | draft | src/zephyr/behavioral_audit/architecture_principles.py |  | production | draft |
| src/zephyr/behavioral_audit/backcompat_checker.py |  | production | draft | src/zephyr/behavioral_audit/backcompat_checker.py |  | production | draft |
| src/zephyr/behavioral_audit/baseline_manager.py |  | production | draft | src/zephyr/behavioral_audit/baseline_manager.py |  | production | draft |
| src/zephyr/behavioral_audit/baseline_poisoning_guard.py |  | production | draft | src/zephyr/behavioral_audit/baseline_poisoning_guard.py |  | production | draft |
| src/zephyr/behavioral_audit/benchmark_integrity.py |  | production | draft | src/zephyr/behavioral_audit/benchmark_integrity.py |  | production | draft |
| src/zephyr/behavioral_audit/brain_integration.py |  | production | draft | src/zephyr/behavioral_audit/brain_integration.py |  | production | draft |
| src/zephyr/behavioral_audit/canary_controller.py |  | production | draft | src/zephyr/behavioral_audit/canary_controller.py |  | production | draft |
| src/zephyr/behavioral_audit/cascade_detector.py |  | production | draft | src/zephyr/behavioral_audit/cascade_detector.py |  | production | draft |
| src/zephyr/behavioral_audit/chaos_injector.py |  | production | draft | src/zephyr/behavioral_audit/chaos_injector.py |  | production | draft |
| src/zephyr/behavioral_audit/code_review_ai.py |  | production | draft | src/zephyr/behavioral_audit/code_review_ai.py |  | production | draft |
| src/zephyr/behavioral_audit/config_consistency.py |  | production | draft | src/zephyr/behavioral_audit/config_consistency.py |  | production | draft |
| src/zephyr/behavioral_audit/contract_drift_detector.py |  | production | draft | src/zephyr/behavioral_audit/contract_drift_detector.py |  | production | draft |
| src/zephyr/behavioral_audit/correlation_engine.py |  | production | draft | src/zephyr/behavioral_audit/correlation_engine.py |  | production | draft |
| src/zephyr/behavioral_audit/credibility_engine.py |  | production | draft | src/zephyr/behavioral_audit/credibility_engine.py |  | production | draft |
| src/zephyr/behavioral_audit/cross_env_consistency.py |  | production | draft | src/zephyr/behavioral_audit/cross_env_consistency.py |  | production | draft |
| src/zephyr/behavioral_audit/cross_module_score.py |  | production | draft | src/zephyr/behavioral_audit/cross_module_score.py |  | production | draft |
| src/zephyr/behavioral_audit/dashboard.py |  | production | draft | src/zephyr/behavioral_audit/dashboard.py |  | production | draft |
| src/zephyr/behavioral_audit/data_classification.py |  | production | draft | src/zephyr/behavioral_audit/data_classification.py |  | production | draft |
| src/zephyr/behavioral_audit/data_lifecycle.py |  | production | draft | src/zephyr/behavioral_audit/data_lifecycle.py |  | production | draft |
| src/zephyr/behavioral_audit/data_source_reliability.py |  | production | draft | src/zephyr/behavioral_audit/data_source_reliability.py |  | production | draft |
| src/zephyr/behavioral_audit/dependency_manager.py |  | production | draft | src/zephyr/behavioral_audit/dependency_manager.py |  | production | draft |
| src/zephyr/behavioral_audit/detector_dispatcher.py |  | production | draft | src/zephyr/behavioral_audit/detector_dispatcher.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_cron_scheduler.py |  | production | draft | src/zephyr/behavioral_audit/drift_cron_scheduler.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_engine.py |  | production | draft | src/zephyr/behavioral_audit/drift_engine.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_hotfix_bypass.py |  | production | draft | src/zephyr/behavioral_audit/drift_hotfix_bypass.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_infrastructure.py |  | production | draft | src/zephyr/behavioral_audit/drift_infrastructure.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_models.py |  | production | draft | src/zephyr/behavioral_audit/drift_models.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_result_types.py |  | production | draft | src/zephyr/behavioral_audit/drift_result_types.py |  | production | draft |
| src/zephyr/behavioral_audit/drift_training.py |  | production | draft | src/zephyr/behavioral_audit/drift_training.py |  | production | draft |
| src/zephyr/behavioral_audit/file_attr_checker.py |  | production | draft | src/zephyr/behavioral_audit/file_attr_checker.py |  | production | draft |
| src/zephyr/behavioral_audit/forensics_engine.py |  | production | draft | src/zephyr/behavioral_audit/forensics_engine.py |  | production | draft |
| src/zephyr/behavioral_audit/gate_persistence.py |  | production | draft | src/zephyr/behavioral_audit/gate_persistence.py |  | production | draft |
| src/zephyr/behavioral_audit/git_bisector.py |  | production | draft | src/zephyr/behavioral_audit/git_bisector.py |  | production | draft |
| src/zephyr/behavioral_audit/gitignore_auditor.py |  | production | draft | src/zephyr/behavioral_audit/gitignore_auditor.py |  | production | draft |
| src/zephyr/behavioral_audit/handoff_manager.py |  | production | draft | src/zephyr/behavioral_audit/handoff_manager.py |  | production | draft |
| src/zephyr/behavioral_audit/headless_scanner.py |  | production | draft | src/zephyr/behavioral_audit/headless_scanner.py |  | production | draft |
| src/zephyr/behavioral_audit/incremental_scanner.py |  | production | draft | src/zephyr/behavioral_audit/incremental_scanner.py |  | production | draft |
| src/zephyr/behavioral_audit/ml_engineering.py |  | production | draft | src/zephyr/behavioral_audit/ml_engineering.py |  | production | draft |
| src/zephyr/behavioral_audit/model_drift_monitor.py |  | production | draft | src/zephyr/behavioral_audit/model_drift_monitor.py |  | production | draft |
| src/zephyr/behavioral_audit/naming_magic_checker.py |  | production | draft | src/zephyr/behavioral_audit/naming_magic_checker.py |  | production | draft |
| src/zephyr/behavioral_audit/orphan_scanner.py |  | production | draft | src/zephyr/behavioral_audit/orphan_scanner.py |  | production | draft |
| src/zephyr/behavioral_audit/performance_baseline.py |  | production | draft | src/zephyr/behavioral_audit/performance_baseline.py |  | production | draft |
| src/zephyr/behavioral_audit/python_compat.py |  | production | draft | src/zephyr/behavioral_audit/python_compat.py |  | production | draft |
| src/zephyr/behavioral_audit/regime_detector.py |  | production | draft | src/zephyr/behavioral_audit/regime_detector.py |  | production | draft |
| src/zephyr/behavioral_audit/resource_guard.py |  | production | draft | src/zephyr/behavioral_audit/resource_guard.py |  | production | draft |
| src/zephyr/behavioral_audit/roi_engine.py |  | production | draft | src/zephyr/behavioral_audit/roi_engine.py |  | production | draft |
| src/zephyr/behavioral_audit/rollback_bridge.py |  | production | draft | src/zephyr/behavioral_audit/rollback_bridge.py |  | production | draft |
| src/zephyr/behavioral_audit/scan_mutex.py |  | production | draft | src/zephyr/behavioral_audit/scan_mutex.py |  | production | draft |
| src/zephyr/behavioral_audit/self_check.py |  | production | draft | src/zephyr/behavioral_audit/self_check.py |  | production | draft |
| src/zephyr/behavioral_audit/self_test_verifier.py |  | production | draft | src/zephyr/behavioral_audit/self_test_verifier.py |  | production | draft |
| src/zephyr/behavioral_audit/suppression_learner.py |  | production | draft | src/zephyr/behavioral_audit/suppression_learner.py |  | production | draft |
| src/zephyr/behavioral_audit/symlink_checker.py |  | production | draft | src/zephyr/behavioral_audit/symlink_checker.py |  | production | draft |
| src/zephyr/behavioral_audit/system_topology.py |  | production | draft | src/zephyr/behavioral_audit/system_topology.py |  | production | draft |
| src/zephyr/behavioral_audit/tamper_proof_audit.py |  | production | draft | src/zephyr/behavioral_audit/tamper_proof_audit.py |  | production | draft |
| src/zephyr/behavioral_audit/test_fixture_checker.py |  | production | draft | src/zephyr/behavioral_audit/test_fixture_checker.py |  | production | draft |
| src/zephyr/behavioral_audit/trend_analyzer.py |  | production | draft | src/zephyr/behavioral_audit/trend_analyzer.py |  | production | draft |

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
    subgraph D_BEHAVIORAL_AUDIT["D-BEHAVIORAL_AUDIT 行为审计"]
        src_zephyr_behavioral_audit_absence_manager_py["src/zephyr/behavioral_audit/absence_manager.py production"]
        src_zephyr_behavioral_audit_ai_construction_detectors_py["src/zephyr/behavioral_audit/ai_construction_det... production"]
        src_zephyr_behavioral_audit_ai_context_injector_py["src/zephyr/behavioral_audit/ai_context_injector.py production"]
        src_zephyr_behavioral_audit_architecture_contracts_py["src/zephyr/behavioral_audit/architecture_contra... production"]
        src_zephyr_behavioral_audit_architecture_principles_py["src/zephyr/behavioral_audit/architecture_princi... production"]
        src_zephyr_behavioral_audit_backcompat_checker_py["src/zephyr/behavioral_audit/backcompat_checker.py production"]
        src_zephyr_behavioral_audit_baseline_manager_py["src/zephyr/behavioral_audit/baseline_manager.py production"]
        src_zephyr_behavioral_audit_baseline_poisoning_guard_py["src/zephyr/behavioral_audit/baseline_poisoning_... production"]
        src_zephyr_behavioral_audit_benchmark_integrity_py["src/zephyr/behavioral_audit/benchmark_integrity.py production"]
        src_zephyr_behavioral_audit_brain_integration_py["src/zephyr/behavioral_audit/brain_integration.py production"]
        src_zephyr_behavioral_audit_canary_controller_py["src/zephyr/behavioral_audit/canary_controller.py production"]
        src_zephyr_behavioral_audit_cascade_detector_py["src/zephyr/behavioral_audit/cascade_detector.py production"]
        src_zephyr_behavioral_audit_chaos_injector_py["src/zephyr/behavioral_audit/chaos_injector.py production"]
        src_zephyr_behavioral_audit_code_review_ai_py["src/zephyr/behavioral_audit/code_review_ai.py production"]
        src_zephyr_behavioral_audit_config_consistency_py["src/zephyr/behavioral_audit/config_consistency.py production"]
        src_zephyr_behavioral_audit_contract_drift_detector_py["src/zephyr/behavioral_audit/contract_drift_dete... production"]
        src_zephyr_behavioral_audit_correlation_engine_py["src/zephyr/behavioral_audit/correlation_engine.py production"]
        src_zephyr_behavioral_audit_credibility_engine_py["src/zephyr/behavioral_audit/credibility_engine.py production"]
        src_zephyr_behavioral_audit_cross_env_consistency_py["src/zephyr/behavioral_audit/cross_env_consisten... production"]
        src_zephyr_behavioral_audit_cross_module_score_py["src/zephyr/behavioral_audit/cross_module_score.py production"]
        src_zephyr_behavioral_audit_dashboard_py["src/zephyr/behavioral_audit/dashboard.py production"]
        src_zephyr_behavioral_audit_data_classification_py["src/zephyr/behavioral_audit/data_classification.py production"]
        src_zephyr_behavioral_audit_data_lifecycle_py["src/zephyr/behavioral_audit/data_lifecycle.py production"]
        src_zephyr_behavioral_audit_data_source_reliability_py["src/zephyr/behavioral_audit/data_source_reliabi... production"]
        src_zephyr_behavioral_audit_dependency_manager_py["src/zephyr/behavioral_audit/dependency_manager.py production"]
        src_zephyr_behavioral_audit_detector_dispatcher_py["src/zephyr/behavioral_audit/detector_dispatcher.py production"]
        src_zephyr_behavioral_audit_drift_cron_scheduler_py["src/zephyr/behavioral_audit/drift_cron_schedule... production"]
        src_zephyr_behavioral_audit_drift_engine_py["src/zephyr/behavioral_audit/drift_engine.py production"]
        src_zephyr_behavioral_audit_drift_hotfix_bypass_py["src/zephyr/behavioral_audit/drift_hotfix_bypass.py production"]
        src_zephyr_behavioral_audit_drift_infrastructure_py["src/zephyr/behavioral_audit/drift_infrastructur... production"]
    end
    src_zephyr_behavioral_audit_chaos_injector_py -->|import_depends| src_zephyr_behavioral_audit_drift_engine_py
    src_zephyr_behavioral_audit_drift_cron_scheduler_py -->|import_depends| src_zephyr_behavioral_audit_drift_engine_py
    src_zephyr_behavioral_audit_drift_engine_py -->|import_depends| src_zephyr_behavioral_audit_drift_infrastructure_py
    D_INTEGRATION["D-INTEGRATION prototype"]
    src_zephyr_behavioral_audit_brain_integration_py -.->|import_depends| D_INTEGRATION
    D_SHARED["D-SHARED production"]
    src_zephyr_behavioral_audit_drift_cron_scheduler_py -->|import_depends| D_SHARED
    D_GOV_AUDIT["D-GOV_AUDIT prototype"]
    src_zephyr_behavioral_audit_drift_engine_py -.->|import_depends| D_GOV_AUDIT
    src_zephyr_behavioral_audit_drift_engine_py -->|import_depends| D_GOV_AUDIT
    src_zephyr_behavioral_audit_drift_hotfix_bypass_py -.->|import_depends| D_INTEGRATION
    D_SECURITY["D-SECURITY prototype"]
    D_SECURITY -.->|import_depends| src_zephyr_behavioral_audit_absence_manager_py
    D_GOVERNANCE["D-GOVERNANCE prototype"]
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_absence_manager_py
    D_SECURITY -.->|import_depends| src_zephyr_behavioral_audit_ai_construction_detectors_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_ai_construction_detectors_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_ai_construction_detectors_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_ai_construction_detectors_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_ai_construction_detectors_py
    D_SECURITY -.->|import_depends| src_zephyr_behavioral_audit_ai_context_injector_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_ai_context_injector_py
    D_SECURITY -.->|import_depends| src_zephyr_behavioral_audit_baseline_poisoning_guard_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_baseline_poisoning_guard_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_behavioral_audit_architecture_principles_py
    D_SECURITY -.->|import_depends| src_zephyr_behavioral_audit_baseline_manager_py
    D_GOV_DRIFT["D-GOV_DRIFT prototype"]
    D_GOV_DRIFT -.->|test_depends| src_zephyr_behavioral_audit_baseline_manager_py
    D_GOV_DRIFT -.->|test_depends| src_zephyr_behavioral_audit_baseline_manager_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_behavioral_audit_absence_manager_py,src_zephyr_behavioral_audit_ai_construction_detectors_py,src_zephyr_behavioral_audit_ai_context_injector_py,src_zephyr_behavioral_audit_architecture_contracts_py,src_zephyr_behavioral_audit_architecture_principles_py,src_zephyr_behavioral_audit_backcompat_checker_py,src_zephyr_behavioral_audit_baseline_manager_py,src_zephyr_behavioral_audit_baseline_poisoning_guard_py,src_zephyr_behavioral_audit_benchmark_integrity_py,src_zephyr_behavioral_audit_brain_integration_py,src_zephyr_behavioral_audit_canary_controller_py,src_zephyr_behavioral_audit_cascade_detector_py,src_zephyr_behavioral_audit_chaos_injector_py,src_zephyr_behavioral_audit_code_review_ai_py,src_zephyr_behavioral_audit_config_consistency_py,src_zephyr_behavioral_audit_contract_drift_detector_py,src_zephyr_behavioral_audit_correlation_engine_py,src_zephyr_behavioral_audit_credibility_engine_py,src_zephyr_behavioral_audit_cross_env_consistency_py,src_zephyr_behavioral_audit_cross_module_score_py,src_zephyr_behavioral_audit_dashboard_py,src_zephyr_behavioral_audit_data_classification_py,src_zephyr_behavioral_audit_data_lifecycle_py,src_zephyr_behavioral_audit_data_source_reliability_py,src_zephyr_behavioral_audit_dependency_manager_py,src_zephyr_behavioral_audit_detector_dispatcher_py,src_zephyr_behavioral_audit_drift_cron_scheduler_py,src_zephyr_behavioral_audit_drift_engine_py,src_zephyr_behavioral_audit_drift_hotfix_bypass_py,src_zephyr_behavioral_audit_drift_infrastructure_py production
    class D_SHARED external_prod
    class D_INTEGRATION,D_GOV_AUDIT,D_SECURITY,D_GOVERNANCE,D_GOV_DRIFT external_design
```

> (依赖图最多显示前 30 个节点，共 60 个)

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 | 依赖数 | 依赖类型 | Target Domain | Count | Type |
|--------|:---:|---------|---------------|:---:|------|
| D-INTEGRATION | 3 | import_depends | D-INTEGRATION | 3 | import_depends |
| D-GOV_AUDIT | 2 | import_depends | D-GOV_AUDIT | 2 | import_depends |
| D-GOVERNANCE | 2 | import_depends | D-GOVERNANCE | 2 | import_depends |
| D-SHARED | 1 | import_depends | D-SHARED | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 | 依赖数 | 依赖类型 | Source Domain | Count | Type |
|------|:---:|---------|---------------|:---:|------|
| D-GOVERNANCE | 90 | test_depends,import_depends | D-GOVERNANCE | 90 | test_depends,import_depends |
| D-SECURITY | 51 | import_depends | D-SECURITY | 51 | import_depends |
| D-GOV_DRIFT | 11 | test_depends,import_depends | D-GOV_DRIFT | 11 | test_depends,import_depends |
| D-OPS | 3 | import_depends,runtime | D-OPS | 3 | import_depends,runtime |
| D-GOV_AUDIT | 2 | import_depends | D-GOV_AUDIT | 2 | import_depends |
| D-TRADING | 1 | import_depends | D-TRADING | 1 | import_depends |
| D-INFRA_RUNTIME | 1 | import_depends | D-INFRA_RUNTIME | 1 | import_depends |
| D-GOV_RULE | 1 | import_depends | D-GOV_RULE | 1 | import_depends |

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
