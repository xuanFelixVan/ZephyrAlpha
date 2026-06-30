---
doc_type: architecture_view
title: D_SHARED 共享服务架构文档
version: "1.0"
status: active
date: 2026-07-01
owner: auto-generator
ttl: permanent
---

# 20_d_shared / 共享服务

> **文档作用 / Purpose**: 展示 共享服务（D_SHARED）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-01 01:52:16
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 20 | Number | 20 |
| 域ID | D_SHARED | Domain ID | D_SHARED |
| 域名称 | 共享服务 | Domain Name | 共享服务 |
| 层级 | L1_foundation | Layer | L1_foundation |
| 模块数 | 255 | Module Count | 255 |
| 域内依赖 | 165 | Internal Dependencies | 165 |
| 跨域入边 | 248 | Cross-domain Incoming | 248 |
| 跨域出边 | 18 | Cross-domain Outgoing | 18 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 188 | Prototype Modules | 188 |
| 生产态模块 | 67 | Production Modules | 67 |
| 容量 | 94/150 (正常) | Capacity | 94/150 (正常) |
| 描述 | 事件总线(event_bus) | Description | 事件总线(event_bus) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 9 页 / Page 1 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_integration_shared_api_03_api_index_py["src/zephyr/integration/shared/api_03/api_index.py prototype"]
        src_zephyr_shared_init_py["src/zephyr/shared/__init__.py production"]
        src_zephyr_shared_version_py["src/zephyr/shared/__version__.py prototype"]
        src_zephyr_shared_cross_layer_init_py["src/zephyr/shared/_cross_layer/__init__.py prototype"]
        src_zephyr_shared_cross_layer_ml_experiment_pipeline_py["src/zephyr/shared/_cross_layer/ml_experiment_pi... prototype"]
        src_zephyr_shared_adaptation_init_py["src/zephyr/shared/adaptation/__init__.py production"]
        src_zephyr_shared_adaptation_execution_tuner_py["src/zephyr/shared/adaptation/execution_tuner.py prototype"]
        src_zephyr_shared_adaptation_prompt_version_manager_py["src/zephyr/shared/adaptation/prompt_version_man... prototype"]
        src_zephyr_shared_adaptive_sampler_py["src/zephyr/shared/adaptive_sampler.py production"]
        src_zephyr_shared_ai_audit_guard_py["src/zephyr/shared/ai_audit_guard.py production"]
        src_zephyr_shared_ai_understandability_constraint_py["src/zephyr/shared/ai_understandability_constrai... production"]
        src_zephyr_shared_alert_escalation_py["src/zephyr/shared/alert_escalation.py production"]
        src_zephyr_shared_alert_manager_py["src/zephyr/shared/alert_manager.py production"]
        src_zephyr_shared_alert_precision_tracker_py["src/zephyr/shared/alert_precision_tracker.py production"]
        src_zephyr_shared_api_init_py["src/zephyr/shared/api/__init__.py prototype"]
        src_zephyr_shared_api_api_client_py["src/zephyr/shared/api/api_client.py prototype"]
        src_zephyr_shared_api_api_index_py["src/zephyr/shared/api/api_index.py prototype"]
        src_zephyr_shared_api_dos_launcher_py["src/zephyr/shared/api/dos_launcher.py prototype"]
        src_zephyr_shared_api_client_py["src/zephyr/shared/api_client.py prototype"]
        src_zephyr_shared_blueprint_code_auditor_py["src/zephyr/shared/blueprint_code_auditor.py production"]
        src_zephyr_shared_blueprint_decomposer_py["src/zephyr/shared/blueprint_decomposer.py prototype"]
        src_zephyr_shared_blueprint_scorer_py["src/zephyr/shared/blueprint_scorer.py prototype"]
        src_zephyr_shared_budget_aware_prompt_py["src/zephyr/shared/budget_aware_prompt.py production"]
        src_zephyr_shared_cache_py["src/zephyr/shared/cache.py prototype"]
        src_zephyr_shared_capability_py["src/zephyr/shared/capability.py prototype"]
        src_zephyr_shared_capacity_calibrator_py["src/zephyr/shared/capacity_calibrator.py production"]
        src_zephyr_shared_capacity_digital_twin_py["src/zephyr/shared/capacity_digital_twin.py production"]
        src_zephyr_shared_capacity_fingerprint_py["src/zephyr/shared/capacity_fingerprint.py production"]
        src_zephyr_shared_capacity_runbook_generator_py["src/zephyr/shared/capacity_runbook_generator.py production"]
        src_zephyr_shared_code_economy_analyzer_py["src/zephyr/shared/code_economy_analyzer.py production"]
    end
    src_zephyr_integration_shared_api_03_api_index_py -.->|import_depends| src_zephyr_shared_api_api_index_py
    src_zephyr_shared_blueprint_decomposer_py -.->|import_depends| src_zephyr_shared_init_py
    src_zephyr_shared_api_client_py -.->|import_depends| src_zephyr_shared_api_api_client_py
    src_zephyr_shared_blueprint_scorer_py -.->|config_depends| src_zephyr_shared_init_py
    src_zephyr_shared_adaptation_prompt_version_manager_py -.->|config_depends| src_zephyr_shared_adaptation_execution_tuner_py
    src_zephyr_shared_api_init_py -.->|config_depends| src_zephyr_shared_api_dos_launcher_py
    D_INTEGRATION["D_INTEGRATION production"]
    src_zephyr_shared_blueprint_decomposer_py -.->|import_depends| D_INTEGRATION
    src_zephyr_shared_blueprint_decomposer_py -.->|import_depends| D_INTEGRATION
    D_ML_TRAIN["D_ML_TRAIN prototype"]
    src_zephyr_shared_cross_layer_ml_experiment_pipeline_py -.->|import_depends| D_ML_TRAIN
    src_zephyr_shared_cross_layer_ml_experiment_pipeline_py -.->|import_depends| D_ML_TRAIN
    D_SIMULATION["D_SIMULATION prototype"]
    src_zephyr_shared_cross_layer_ml_experiment_pipeline_py -.->|import_depends| D_SIMULATION
    D_CROSS_ASSET["D_CROSS_ASSET production"]
    D_CROSS_ASSET -.->|import_depends| src_zephyr_shared_cross_layer_ml_experiment_pipeline_py
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_init_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_init_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_init_py
    D_GOVERNANCE -->|import_depends| src_zephyr_shared_blueprint_code_auditor_py
    D_GOV_DOCS["D_GOV_DOCS prototype"]
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_init_py
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_init_py
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_init_py
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT production"]
    D_GOV_ENFORCEMENT -->|import_depends| src_zephyr_shared_blueprint_code_auditor_py
    D_GOV_ENFORCEMENT -->|import_depends| src_zephyr_shared_code_economy_analyzer_py
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_init_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_init_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_init_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_init_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_alert_manager_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_init_py,src_zephyr_shared_adaptation_init_py,src_zephyr_shared_adaptive_sampler_py,src_zephyr_shared_ai_audit_guard_py,src_zephyr_shared_ai_understandability_constraint_py,src_zephyr_shared_alert_escalation_py,src_zephyr_shared_alert_manager_py,src_zephyr_shared_alert_precision_tracker_py,src_zephyr_shared_blueprint_code_auditor_py,src_zephyr_shared_budget_aware_prompt_py,src_zephyr_shared_capacity_calibrator_py,src_zephyr_shared_capacity_digital_twin_py,src_zephyr_shared_capacity_fingerprint_py,src_zephyr_shared_capacity_runbook_generator_py,src_zephyr_shared_code_economy_analyzer_py production
    class src_zephyr_integration_shared_api_03_api_index_py,src_zephyr_shared_version_py,src_zephyr_shared_cross_layer_init_py,src_zephyr_shared_cross_layer_ml_experiment_pipeline_py,src_zephyr_shared_adaptation_execution_tuner_py,src_zephyr_shared_adaptation_prompt_version_manager_py,src_zephyr_shared_api_init_py,src_zephyr_shared_api_api_client_py,src_zephyr_shared_api_api_index_py,src_zephyr_shared_api_dos_launcher_py,src_zephyr_shared_api_client_py,src_zephyr_shared_blueprint_decomposer_py,src_zephyr_shared_blueprint_scorer_py,src_zephyr_shared_cache_py,src_zephyr_shared_capability_py design
    class D_INTEGRATION,D_CROSS_ASSET,D_GOV_ENFORCEMENT,D_INFRA_RUNTIME external_prod
    class D_ML_TRAIN,D_SIMULATION,D_GOVERNANCE,D_GOV_DOCS external_design
```

### 第 2 页 / 共 9 页 / Page 2 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_combinatorial_gate_py["src/zephyr/shared/combinatorial_gate.py production"]
        src_zephyr_shared_compensation_init_py["src/zephyr/shared/compensation/__init__.py production"]
        src_zephyr_shared_config_init_py["src/zephyr/shared/config/__init__.py ❌ ARCH-038 已删除"]
        src_zephyr_shared_config_loader_py["src/zephyr/shared/config/loader.py ❌ ARCH-038 已删除"]
        src_zephyr_shared_constants_py["src/zephyr/shared/constants.py prototype"]
        src_zephyr_shared_content_fingerprint_py["src/zephyr/shared/content_fingerprint.py prototype"]
        src_zephyr_shared_context_engine_py["src/zephyr/shared/context_engine.py prototype"]
        src_zephyr_shared_contract_bus_py["src/zephyr/shared/contract_bus.py prototype"]
        src_zephyr_shared_contract_tester_py["src/zephyr/shared/contract_tester.py prototype"]
        src_zephyr_shared_contracts_init_py["src/zephyr/shared/contracts/__init__.py prototype"]
        src_zephyr_shared_contracts_backpressure_init_py["src/zephyr/shared/contracts/backpressure/__init... prototype"]
        src_zephyr_shared_contracts_backpressure_types_py["src/zephyr/shared/contracts/backpressure/_types.py prototype"]
        src_zephyr_shared_contracts_backpressure_pause_py["src/zephyr/shared/contracts/backpressure/pause.py prototype"]
        src_zephyr_shared_contracts_backpressure_resume_py["src/zephyr/shared/contracts/backpressure/resume.py prototype"]
        src_zephyr_shared_contracts_backpressure_throttle_py["src/zephyr/shared/contracts/backpressure/thrott... prototype"]
        src_zephyr_shared_contracts_core_init_py["src/zephyr/shared/contracts/core/__init__.py prototype"]
        src_zephyr_shared_contracts_core_base_event_py["src/zephyr/shared/contracts/core/base_event.py prototype"]
        src_zephyr_shared_contracts_core_enforcer_py["src/zephyr/shared/contracts/core/enforcer.py prototype"]
        src_zephyr_shared_contracts_core_factories_py["src/zephyr/shared/contracts/core/factories.py prototype"]
        src_zephyr_shared_contracts_core_gate_types_py["src/zephyr/shared/contracts/core/gate_types.py prototype"]
        src_zephyr_shared_contracts_core_registry_py["src/zephyr/shared/contracts/core/registry.py prototype"]
        src_zephyr_shared_contracts_core_runtime_plane_tag_py["src/zephyr/shared/contracts/core/runtime_plane_... prototype"]
        src_zephyr_shared_contracts_core_system_configuration_py["src/zephyr/shared/contracts/core/system_configu... prototype"]
        src_zephyr_shared_contracts_core_telemetry_emitter_py["src/zephyr/shared/contracts/core/telemetry_emit... production"]
        src_zephyr_shared_contracts_core_timestamp_py["src/zephyr/shared/contracts/core/timestamp.py prototype"]
        src_zephyr_shared_contracts_core_trace_context_py["src/zephyr/shared/contracts/core/trace_context.py prototype"]
        src_zephyr_shared_contracts_errors_init_py["src/zephyr/shared/contracts/errors/__init__.py prototype"]
        src_zephyr_shared_contracts_errors_contract_violation_error_py["src/zephyr/shared/contracts/errors/contract_vio... prototype"]
        src_zephyr_shared_contracts_errors_data_quality_error_py["src/zephyr/shared/contracts/errors/data_quality... prototype"]
        src_zephyr_shared_contracts_errors_execution_rejection_error_py["src/zephyr/shared/contracts/errors/execution_re... prototype"]
    end
    src_zephyr_shared_contract_bus_py -.->|import_depends| src_zephyr_shared_contracts_errors_contract_violation_error_py
    src_zephyr_shared_config_init_py -.->|import_depends| src_zephyr_shared_config_loader_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_backpressure_init_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_enforcer_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_registry_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_factories_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_system_configuration_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_telemetry_emitter_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_runtime_plane_tag_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_timestamp_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_core_trace_context_py
    src_zephyr_shared_contracts_init_py -.->|import_depends| src_zephyr_shared_contracts_errors_init_py
    src_zephyr_shared_contracts_backpressure_resume_py -.->|import_depends| src_zephyr_shared_contracts_backpressure_types_py
    src_zephyr_shared_contracts_backpressure_pause_py -.->|import_depends| src_zephyr_shared_contracts_backpressure_types_py
    src_zephyr_shared_contracts_backpressure_throttle_py -.->|import_depends| src_zephyr_shared_contracts_backpressure_types_py
    src_zephyr_shared_contracts_backpressure_types_py -.->|import_depends| src_zephyr_shared_contracts_core_trace_context_py
    src_zephyr_shared_contracts_core_init_py -.->|import_depends| src_zephyr_shared_contracts_core_base_event_py
    src_zephyr_shared_contracts_core_init_py -.->|import_depends| src_zephyr_shared_contracts_core_gate_types_py
    src_zephyr_shared_contracts_errors_contract_violation_error_py -.->|import_depends| src_zephyr_shared_contracts_core_trace_context_py
    src_zephyr_shared_contracts_errors_data_quality_error_py -.->|import_depends| src_zephyr_shared_contracts_core_trace_context_py
    src_zephyr_shared_contracts_errors_execution_rejection_error_py -.->|config_depends| src_zephyr_shared_contracts_errors_init_py
    src_zephyr_shared_contracts_errors_init_py -.->|import_depends| src_zephyr_shared_contracts_errors_contract_violation_error_py
    src_zephyr_shared_contracts_errors_init_py -.->|import_depends| src_zephyr_shared_contracts_errors_data_quality_error_py
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_errors_data_quality_error_py
    D_GOVERNANCE -->|import_depends| src_zephyr_shared_combinatorial_gate_py
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT production"]
    D_GOV_ENFORCEMENT -->|import_depends| src_zephyr_shared_combinatorial_gate_py
    D_GOV_ENFORCEMENT -.->|import_depends| src_zephyr_shared_contracts_core_enforcer_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_core_factories_py
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    D_INFRA_RUNTIME -.->|import_depends| src_zephyr_shared_config_loader_py
    D_INFRA_A2A["D_INFRA_A2A production"]
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_contracts_core_trace_context_py
    D_INFRA_TELEMETRY["D_INFRA_TELEMETRY production"]
    D_INFRA_TELEMETRY -.->|import_depends| src_zephyr_shared_contracts_core_timestamp_py
    D_TRADING["D_TRADING production"]
    D_TRADING -.->|import_depends| src_zephyr_shared_contracts_core_system_configuration_py
    D_TRADING -.->|import_depends| src_zephyr_shared_contracts_core_telemetry_emitter_py
    D_TRADING -.->|import_depends| src_zephyr_shared_contracts_core_registry_py
    D_TRADING -.->|import_depends| src_zephyr_shared_contracts_core_factories_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_combinatorial_gate_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_combinatorial_gate_py,src_zephyr_shared_compensation_init_py,src_zephyr_shared_contracts_core_telemetry_emitter_py production
    class src_zephyr_shared_config_init_py,src_zephyr_shared_config_loader_py,src_zephyr_shared_constants_py,src_zephyr_shared_content_fingerprint_py,src_zephyr_shared_context_engine_py,src_zephyr_shared_contract_bus_py,src_zephyr_shared_contract_tester_py,src_zephyr_shared_contracts_init_py,src_zephyr_shared_contracts_backpressure_init_py,src_zephyr_shared_contracts_backpressure_types_py,src_zephyr_shared_contracts_backpressure_pause_py,src_zephyr_shared_contracts_backpressure_resume_py,src_zephyr_shared_contracts_backpressure_throttle_py,src_zephyr_shared_contracts_core_init_py,src_zephyr_shared_contracts_core_base_event_py,src_zephyr_shared_contracts_core_enforcer_py,src_zephyr_shared_contracts_core_factories_py,src_zephyr_shared_contracts_core_gate_types_py,src_zephyr_shared_contracts_core_registry_py,src_zephyr_shared_contracts_core_runtime_plane_tag_py,src_zephyr_shared_contracts_core_system_configuration_py,src_zephyr_shared_contracts_core_timestamp_py,src_zephyr_shared_contracts_core_trace_context_py,src_zephyr_shared_contracts_errors_init_py,src_zephyr_shared_contracts_errors_contract_violation_error_py,src_zephyr_shared_contracts_errors_data_quality_error_py,src_zephyr_shared_contracts_errors_execution_rejection_error_py design
    class D_GOV_ENFORCEMENT,D_INFRA_RUNTIME,D_INFRA_A2A,D_INFRA_TELEMETRY,D_TRADING external_prod
    class D_GOVERNANCE external_design
```

### 第 3 页 / 共 9 页 / Page 3 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_contracts_errors_factor_computation_error_py["src/zephyr/shared/contracts/errors/factor_compu... prototype"]
        src_zephyr_shared_contracts_errors_risk_limit_violation_error_py["src/zephyr/shared/contracts/errors/risk_limit_v... prototype"]
        src_zephyr_shared_contracts_errors_signal_degradation_warning_py["src/zephyr/shared/contracts/errors/signal_degra... prototype"]
        src_zephyr_shared_contracts_escalation_init_py["src/zephyr/shared/contracts/escalation/__init__.py prototype"]
        src_zephyr_shared_contracts_escalation_budget_alert_py["src/zephyr/shared/contracts/escalation/budget_a... production"]
        src_zephyr_shared_contracts_execution_init_py["src/zephyr/shared/contracts/execution/__init__.py prototype"]
        src_zephyr_shared_contracts_execution_capital_allocation_result_py["src/zephyr/shared/contracts/execution/capital_a... prototype"]
        src_zephyr_shared_contracts_execution_execution_report_py["src/zephyr/shared/contracts/execution/execution... prototype"]
        src_zephyr_shared_contracts_execution_fill_py["src/zephyr/shared/contracts/execution/fill.py prototype"]
        src_zephyr_shared_contracts_execution_model_serving_request_py["src/zephyr/shared/contracts/execution/model_ser... prototype"]
        src_zephyr_shared_contracts_execution_order_py["src/zephyr/shared/contracts/execution/order.py prototype"]
        src_zephyr_shared_contracts_experiment_init_py["src/zephyr/shared/contracts/experiment/__init__.py prototype"]
        src_zephyr_shared_contracts_experiment_experiment_result_py["src/zephyr/shared/contracts/experiment/experime... prototype"]
        src_zephyr_shared_contracts_experiment_model_serving_response_py["src/zephyr/shared/contracts/experiment/model_se... prototype"]
        src_zephyr_shared_contracts_external_init_py["src/zephyr/shared/contracts/external/__init__.py prototype"]
        src_zephyr_shared_contracts_external_ext_001_py["src/zephyr/shared/contracts/external/ext_001.py prototype"]
        src_zephyr_shared_contracts_external_ext_002_py["src/zephyr/shared/contracts/external/ext_002.py prototype"]
        src_zephyr_shared_contracts_external_ext_003_py["src/zephyr/shared/contracts/external/ext_003.py prototype"]
        src_zephyr_shared_contracts_external_ext_004_py["src/zephyr/shared/contracts/external/ext_004.py prototype"]
        src_zephyr_shared_contracts_identity_init_py["src/zephyr/shared/contracts/identity/__init__.py prototype"]
        src_zephyr_shared_contracts_identity_agent_identity_py["src/zephyr/shared/contracts/identity/agent_iden... prototype"]
        src_zephyr_shared_contracts_identity_permission_py["src/zephyr/shared/contracts/identity/permission.py prototype"]
        src_zephyr_shared_contracts_llm_gateway_protocol_py["src/zephyr/shared/contracts/llm_gateway_protoco... prototype"]
        src_zephyr_shared_contracts_market_init_py["src/zephyr/shared/contracts/market/__init__.py prototype"]
        src_zephyr_shared_contracts_market_factor_monitor_report_py["src/zephyr/shared/contracts/market/factor_monit... production"]
        src_zephyr_shared_contracts_market_factor_signal_py["src/zephyr/shared/contracts/market/factor_signa... prototype"]
        src_zephyr_shared_contracts_market_instrument_py["src/zephyr/shared/contracts/market/instrument.py prototype"]
        src_zephyr_shared_contracts_market_macro_factor_signal_py["src/zephyr/shared/contracts/market/macro_factor... prototype"]
        src_zephyr_shared_contracts_market_market_data_py["src/zephyr/shared/contracts/market/market_data.py prototype"]
        src_zephyr_shared_contracts_market_synthesized_signal_py["src/zephyr/shared/contracts/market/synthesized_... prototype"]
    end
    src_zephyr_shared_contracts_escalation_init_py -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    src_zephyr_shared_contracts_execution_fill_py -.->|config_depends| src_zephyr_shared_contracts_execution_init_py
    src_zephyr_shared_contracts_execution_execution_report_py -.->|config_depends| src_zephyr_shared_contracts_execution_init_py
    src_zephyr_shared_contracts_execution_capital_allocation_result_py -.->|config_depends| src_zephyr_shared_contracts_execution_init_py
    src_zephyr_shared_contracts_execution_model_serving_request_py -.->|config_depends| src_zephyr_shared_contracts_execution_init_py
    src_zephyr_shared_contracts_execution_order_py -.->|config_depends| src_zephyr_shared_contracts_execution_init_py
    src_zephyr_shared_contracts_experiment_init_py -.->|config_depends| src_zephyr_shared_contracts_experiment_experiment_result_py
    src_zephyr_shared_contracts_external_init_py -.->|config_depends| src_zephyr_shared_contracts_external_ext_001_py
    src_zephyr_shared_contracts_identity_init_py -.->|import_depends| src_zephyr_shared_contracts_identity_agent_identity_py
    src_zephyr_shared_contracts_identity_init_py -.->|import_depends| src_zephyr_shared_contracts_identity_permission_py
    src_zephyr_shared_contracts_market_init_py -.->|import_depends| src_zephyr_shared_contracts_market_factor_monitor_report_py
    src_zephyr_shared_contracts_market_init_py -.->|import_depends| src_zephyr_shared_contracts_market_instrument_py
    src_zephyr_shared_contracts_market_init_py -.->|import_depends| src_zephyr_shared_contracts_market_macro_factor_signal_py
    src_zephyr_shared_contracts_market_init_py -.->|import_depends| src_zephyr_shared_contracts_market_market_data_py
    src_zephyr_shared_contracts_market_init_py -.->|import_depends| src_zephyr_shared_contracts_market_factor_signal_py
    src_zephyr_shared_contracts_market_init_py -.->|import_depends| src_zephyr_shared_contracts_market_synthesized_signal_py
    D_FACTOR["D_FACTOR production"]
    D_FACTOR -.->|import_depends| src_zephyr_shared_contracts_errors_factor_computation_error_py
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    D_OPS["D_OPS prototype"]
    D_OPS -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_experiment_experiment_result_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_escalation_budget_alert_py
    D_INFRA_RECOVERY["D_INFRA_RECOVERY production"]
    D_INFRA_RECOVERY -.->|import_depends| src_zephyr_shared_contracts_llm_gateway_protocol_py
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    D_INFRA_RUNTIME -.->|import_depends| src_zephyr_shared_contracts_llm_gateway_protocol_py
    D_INFRA_RECOVERY -.->|import_depends| src_zephyr_shared_contracts_identity_agent_identity_py
    D_INTEGRATION["D_INTEGRATION prototype"]
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_contracts_llm_gateway_protocol_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_identity_agent_identity_py
    D_INTELLIGENCE["D_INTELLIGENCE production"]
    D_INTELLIGENCE -.->|import_depends| src_zephyr_shared_contracts_experiment_model_serving_response_py
    D_ML_TRAIN["D_ML_TRAIN prototype"]
    D_ML_TRAIN -.->|import_depends| src_zephyr_shared_contracts_experiment_model_serving_response_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_contracts_escalation_budget_alert_py,src_zephyr_shared_contracts_market_factor_monitor_report_py production
    class src_zephyr_shared_contracts_errors_factor_computation_error_py,src_zephyr_shared_contracts_errors_risk_limit_violation_error_py,src_zephyr_shared_contracts_errors_signal_degradation_warning_py,src_zephyr_shared_contracts_escalation_init_py,src_zephyr_shared_contracts_execution_init_py,src_zephyr_shared_contracts_execution_capital_allocation_result_py,src_zephyr_shared_contracts_execution_execution_report_py,src_zephyr_shared_contracts_execution_fill_py,src_zephyr_shared_contracts_execution_model_serving_request_py,src_zephyr_shared_contracts_execution_order_py,src_zephyr_shared_contracts_experiment_init_py,src_zephyr_shared_contracts_experiment_experiment_result_py,src_zephyr_shared_contracts_experiment_model_serving_response_py,src_zephyr_shared_contracts_external_init_py,src_zephyr_shared_contracts_external_ext_001_py,src_zephyr_shared_contracts_external_ext_002_py,src_zephyr_shared_contracts_external_ext_003_py,src_zephyr_shared_contracts_external_ext_004_py,src_zephyr_shared_contracts_identity_init_py,src_zephyr_shared_contracts_identity_agent_identity_py,src_zephyr_shared_contracts_identity_permission_py,src_zephyr_shared_contracts_llm_gateway_protocol_py,src_zephyr_shared_contracts_market_init_py,src_zephyr_shared_contracts_market_factor_signal_py,src_zephyr_shared_contracts_market_instrument_py,src_zephyr_shared_contracts_market_macro_factor_signal_py,src_zephyr_shared_contracts_market_market_data_py,src_zephyr_shared_contracts_market_synthesized_signal_py design
    class D_FACTOR,D_INFRA_RECOVERY,D_INFRA_RUNTIME,D_INTELLIGENCE external_prod
    class D_GOVERNANCE,D_OPS,D_INTEGRATION,D_ML_TRAIN external_design
```

### 第 4 页 / 共 9 页 / Page 4 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_contracts_orchestration_protocol_py["src/zephyr/shared/contracts/orchestration_proto... prototype"]
        src_zephyr_shared_contracts_portfolio_init_py["src/zephyr/shared/contracts/portfolio/__init__.py prototype"]
        src_zephyr_shared_contracts_portfolio_money_py["src/zephyr/shared/contracts/portfolio/money.py production"]
        src_zephyr_shared_contracts_portfolio_performance_attribution_report_py["src/zephyr/shared/contracts/portfolio/performan... prototype"]
        src_zephyr_shared_contracts_portfolio_position_py["src/zephyr/shared/contracts/portfolio/position.py prototype"]
        src_zephyr_shared_contracts_portfolio_strategy_lifecycle_event_py["src/zephyr/shared/contracts/portfolio/strategy_... prototype"]
        src_zephyr_shared_contracts_risk_init_py["src/zephyr/shared/contracts/risk/__init__.py prototype"]
        src_zephyr_shared_contracts_risk_compliance_rule_py["src/zephyr/shared/contracts/risk/compliance_rul... prototype"]
        src_zephyr_shared_contracts_risk_risk_dashboard_snapshot_py["src/zephyr/shared/contracts/risk/risk_dashboard... production"]
        src_zephyr_shared_contracts_risk_risk_limits_py["src/zephyr/shared/contracts/risk/risk_limits.py prototype"]
        src_zephyr_shared_contracts_risk_risk_metrics_py["src/zephyr/shared/contracts/risk/risk_metrics.py production"]
        src_zephyr_shared_contracts_risk_risk_validator_protocol_py["src/zephyr/shared/contracts/risk/risk_validator... prototype"]
        src_zephyr_shared_contracts_security_init_py["src/zephyr/shared/contracts/security/__init__.py prototype"]
        src_zephyr_shared_contracts_security_security_decision_py["src/zephyr/shared/contracts/security/security_d... prototype"]
        src_zephyr_shared_contracts_skill_protocol_py["src/zephyr/shared/contracts/skill_protocol.py prototype"]
        src_zephyr_shared_contracts_task_repository_protocol_py["src/zephyr/shared/contracts/task_repository_pro... prototype"]
        src_zephyr_shared_core_integrity_guard_py["src/zephyr/shared/core_integrity_guard.py production"]
        src_zephyr_shared_cost_estimator_py["src/zephyr/shared/cost_estimator.py production"]
        src_zephyr_shared_degradation_chain_py["src/zephyr/shared/degradation_chain.py production"]
        src_zephyr_shared_dependency_init_py["src/zephyr/shared/dependency/__init__.py production"]
        src_zephyr_shared_dependency_capacity_guard_py["src/zephyr/shared/dependency_capacity_guard.py production"]
        src_zephyr_shared_deprecation_py["src/zephyr/shared/deprecation.py prototype"]
        src_zephyr_shared_diff_utils_py["src/zephyr/shared/diff_utils.py prototype"]
        src_zephyr_shared_draft_init_py["src/zephyr/shared/draft/__init__.py production"]
        src_zephyr_shared_dual_channel_alert_py["src/zephyr/shared/dual_channel_alert.py production"]
        src_zephyr_shared_env_py["src/zephyr/shared/env.py prototype"]
        src_zephyr_shared_error_budget_tracker_py["src/zephyr/shared/error_budget_tracker.py production"]
        src_zephyr_shared_errors_py["src/zephyr/shared/errors.py prototype"]
        src_zephyr_shared_event_bus_py["src/zephyr/shared/event_bus.py production"]
        src_zephyr_shared_event_bus_py_1["src/zephyr/shared/event_bus.py production"]
    end
    src_zephyr_shared_contracts_portfolio_init_py -.->|import_depends| src_zephyr_shared_contracts_portfolio_position_py
    src_zephyr_shared_contracts_security_init_py -.->|import_depends| src_zephyr_shared_contracts_security_security_decision_py
    src_zephyr_shared_contracts_risk_init_py -.->|import_depends| src_zephyr_shared_contracts_risk_risk_limits_py
    src_zephyr_shared_contracts_risk_init_py -.->|import_depends| src_zephyr_shared_contracts_risk_compliance_rule_py
    src_zephyr_shared_contracts_risk_init_py -.->|import_depends| src_zephyr_shared_contracts_risk_risk_dashboard_snapshot_py
    src_zephyr_shared_contracts_risk_init_py -.->|import_depends| src_zephyr_shared_contracts_risk_risk_metrics_py
    src_zephyr_shared_contracts_risk_init_py -.->|import_depends| src_zephyr_shared_contracts_risk_risk_validator_protocol_py
    D_AUTONOMY_CORE["D_AUTONOMY_CORE prototype"]
    D_AUTONOMY_CORE -.->|import_depends| src_zephyr_shared_contracts_security_init_py
    D_FRONTEND["D_FRONTEND production"]
    D_FRONTEND -.->|import_depends| src_zephyr_shared_contracts_task_repository_protocol_py
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_portfolio_performance_attribution_report_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_task_repository_protocol_py
    D_GOVERNANCE -->|import_depends| src_zephyr_shared_core_integrity_guard_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_skill_protocol_py
    D_GOV_AUDIT["D_GOV_AUDIT prototype"]
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_contracts_task_repository_protocol_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_contracts_security_security_decision_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_contracts_task_repository_protocol_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_contracts_task_repository_protocol_py
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT production"]
    D_GOV_ENFORCEMENT -->|import_depends| src_zephyr_shared_core_integrity_guard_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_portfolio_strategy_lifecycle_event_py
    D_INFRA_OPS["D_INFRA_OPS prototype"]
    D_INFRA_OPS -.->|import_depends| src_zephyr_shared_contracts_task_repository_protocol_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_contracts_skill_protocol_py
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_dual_channel_alert_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_contracts_portfolio_money_py,src_zephyr_shared_contracts_risk_risk_dashboard_snapshot_py,src_zephyr_shared_contracts_risk_risk_metrics_py,src_zephyr_shared_core_integrity_guard_py,src_zephyr_shared_cost_estimator_py,src_zephyr_shared_degradation_chain_py,src_zephyr_shared_dependency_init_py,src_zephyr_shared_dependency_capacity_guard_py,src_zephyr_shared_draft_init_py,src_zephyr_shared_dual_channel_alert_py,src_zephyr_shared_error_budget_tracker_py,src_zephyr_shared_event_bus_py,src_zephyr_shared_event_bus_py_1 production
    class src_zephyr_shared_contracts_orchestration_protocol_py,src_zephyr_shared_contracts_portfolio_init_py,src_zephyr_shared_contracts_portfolio_performance_attribution_report_py,src_zephyr_shared_contracts_portfolio_position_py,src_zephyr_shared_contracts_portfolio_strategy_lifecycle_event_py,src_zephyr_shared_contracts_risk_init_py,src_zephyr_shared_contracts_risk_compliance_rule_py,src_zephyr_shared_contracts_risk_risk_limits_py,src_zephyr_shared_contracts_risk_risk_validator_protocol_py,src_zephyr_shared_contracts_security_init_py,src_zephyr_shared_contracts_security_security_decision_py,src_zephyr_shared_contracts_skill_protocol_py,src_zephyr_shared_contracts_task_repository_protocol_py,src_zephyr_shared_deprecation_py,src_zephyr_shared_diff_utils_py,src_zephyr_shared_env_py,src_zephyr_shared_errors_py design
    class D_FRONTEND,D_GOV_ENFORCEMENT,D_INFRA_RUNTIME external_prod
    class D_AUTONOMY_CORE,D_GOVERNANCE,D_GOV_AUDIT,D_INFRA_OPS external_design
```

### 第 5 页 / 共 9 页 / Page 5 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_events_init_py["src/zephyr/shared/events/__init__.py prototype"]
        src_zephyr_shared_events_dlq_py["src/zephyr/shared/events/dlq.py prototype"]
        src_zephyr_shared_events_dlq_bridge_py["src/zephyr/shared/events/dlq_bridge.py prototype"]
        src_zephyr_shared_events_event_bus_py["src/zephyr/shared/events/event_bus.py production"]
        src_zephyr_shared_events_event_bus_upgrade_py["src/zephyr/shared/events/event_bus_upgrade.py production"]
        src_zephyr_shared_events_event_reactor_py["src/zephyr/shared/events/event_reactor.py prototype"]
        src_zephyr_shared_events_event_schemas_py["src/zephyr/shared/events/event_schemas.py prototype"]
        src_zephyr_shared_events_hook_dispatcher_py["src/zephyr/shared/events/hook_dispatcher.py prototype"]
        src_zephyr_shared_events_upgrade_strategy_py["src/zephyr/shared/events/upgrade_strategy.py prototype"]
        src_zephyr_shared_fault_isolator_py["src/zephyr/shared/fault_isolator.py production"]
        src_zephyr_shared_file_utils_py["src/zephyr/shared/file_utils.py prototype"]
        src_zephyr_shared_flags_py["src/zephyr/shared/flags.py prototype"]
        src_zephyr_shared_foundation_init_py["src/zephyr/shared/foundation/__init__.py prototype"]
        src_zephyr_shared_foundation_constants_py["src/zephyr/shared/foundation/constants.py prototype"]
        src_zephyr_shared_foundation_deprecation_py["src/zephyr/shared/foundation/deprecation.py prototype"]
        src_zephyr_shared_foundation_env_py["src/zephyr/shared/foundation/env.py prototype"]
        src_zephyr_shared_foundation_errors_py["src/zephyr/shared/foundation/errors.py prototype"]
        src_zephyr_shared_foundation_flags_py["src/zephyr/shared/foundation/flags.py prototype"]
        src_zephyr_shared_foundation_types_py["src/zephyr/shared/foundation/types.py prototype"]
        src_zephyr_shared_frontmatter_utils_py["src/zephyr/shared/frontmatter_utils.py prototype"]
        src_zephyr_shared_health_py["src/zephyr/shared/health.py production"]
        src_zephyr_shared_healthcheck_service_py["src/zephyr/shared/healthcheck_service.py production"]
        src_zephyr_shared_heartbeat_server_py["src/zephyr/shared/heartbeat_server.py production"]
        src_zephyr_shared_idempotency_py["src/zephyr/shared/idempotency.py prototype"]
        src_zephyr_shared_infra_init_py["src/zephyr/shared/infra/__init__.py prototype"]
        src_zephyr_shared_infra_cache_py["src/zephyr/shared/infra/cache.py prototype"]
        src_zephyr_shared_infra_idempotency_py["src/zephyr/shared/infra/idempotency.py prototype"]
        src_zephyr_shared_infra_limiter_py["src/zephyr/shared/infra/limiter.py prototype"]
        src_zephyr_shared_infra_lock_py["src/zephyr/shared/infra/lock.py prototype"]
        src_zephyr_shared_infra_observer_py["src/zephyr/shared/infra/observer.py prototype"]
    end
    src_zephyr_shared_flags_py -.->|import_depends| src_zephyr_shared_foundation_flags_py
    src_zephyr_shared_idempotency_py -.->|import_depends| src_zephyr_shared_infra_idempotency_py
    src_zephyr_shared_events_dlq_bridge_py -.->|import_depends| src_zephyr_shared_events_dlq_py
    src_zephyr_shared_events_dlq_py -.->|import_depends| src_zephyr_shared_infra_observer_py
    src_zephyr_shared_events_event_schemas_py -.->|import_depends| src_zephyr_shared_infra_observer_py
    src_zephyr_shared_events_init_py -.->|import_depends| src_zephyr_shared_events_dlq_bridge_py
    src_zephyr_shared_foundation_constants_py -.->|import_depends| src_zephyr_shared_infra_observer_py
    src_zephyr_shared_foundation_flags_py -.->|import_depends| src_zephyr_shared_foundation_errors_py
    src_zephyr_shared_infra_idempotency_py -.->|import_depends| src_zephyr_shared_foundation_errors_py
    src_zephyr_shared_infra_cache_py -.->|import_depends| src_zephyr_shared_foundation_errors_py
    src_zephyr_shared_infra_lock_py -.->|import_depends| src_zephyr_shared_foundation_errors_py
    src_zephyr_shared_infra_limiter_py -.->|import_depends| src_zephyr_shared_foundation_errors_py
    src_zephyr_shared_foundation_init_py -.->|config_depends| src_zephyr_shared_foundation_constants_py
    src_zephyr_shared_infra_init_py -.->|import_depends| src_zephyr_shared_infra_cache_py
    D_OPS["D_OPS prototype"]
    src_zephyr_shared_health_py -.->|import_depends| D_OPS
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    src_zephyr_shared_healthcheck_service_py -->|import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE["D_GOVERNANCE production"]
    src_zephyr_shared_foundation_constants_py -.->|import_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["D_AUTONOMY_CORE prototype"]
    D_AUTONOMY_CORE -.->|import_depends| src_zephyr_shared_events_event_schemas_py
    D_AUTONOMY_CORE -.->|import_depends| src_zephyr_shared_infra_cache_py
    D_GOV_AUDIT["D_GOV_AUDIT prototype"]
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_infra_observer_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_infra_observer_py
    D_INFRA_RUNTIME -.->|import_depends| src_zephyr_shared_events_upgrade_strategy_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_heartbeat_server_py
    D_INFRA_A2A["D_INFRA_A2A production"]
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_events_dlq_bridge_py
    D_INFRA_RUNTIME -.->|import_depends| src_zephyr_shared_infra_observer_py
    D_TRADING["D_TRADING prototype"]
    D_TRADING -.->|import_depends| src_zephyr_shared_events_event_bus_upgrade_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_fault_isolator_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_events_event_bus_upgrade_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_heartbeat_server_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_events_event_bus_py,src_zephyr_shared_events_event_bus_upgrade_py,src_zephyr_shared_fault_isolator_py,src_zephyr_shared_health_py,src_zephyr_shared_healthcheck_service_py,src_zephyr_shared_heartbeat_server_py production
    class src_zephyr_shared_events_init_py,src_zephyr_shared_events_dlq_py,src_zephyr_shared_events_dlq_bridge_py,src_zephyr_shared_events_event_reactor_py,src_zephyr_shared_events_event_schemas_py,src_zephyr_shared_events_hook_dispatcher_py,src_zephyr_shared_events_upgrade_strategy_py,src_zephyr_shared_file_utils_py,src_zephyr_shared_flags_py,src_zephyr_shared_foundation_init_py,src_zephyr_shared_foundation_constants_py,src_zephyr_shared_foundation_deprecation_py,src_zephyr_shared_foundation_env_py,src_zephyr_shared_foundation_errors_py,src_zephyr_shared_foundation_flags_py,src_zephyr_shared_foundation_types_py,src_zephyr_shared_frontmatter_utils_py,src_zephyr_shared_idempotency_py,src_zephyr_shared_infra_init_py,src_zephyr_shared_infra_cache_py,src_zephyr_shared_infra_idempotency_py,src_zephyr_shared_infra_limiter_py,src_zephyr_shared_infra_lock_py,src_zephyr_shared_infra_observer_py design
    class D_INFRA_RUNTIME,D_GOVERNANCE,D_INFRA_A2A external_prod
    class D_OPS,D_AUTONOMY_CORE,D_GOV_AUDIT,D_TRADING external_design
```

### 第 6 页 / 共 9 页 / Page 6 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_infra_outbox_py["src/zephyr/shared/infra/outbox.py prototype"]
        src_zephyr_shared_infra_process_lifecycle_gateway_py["src/zephyr/shared/infra/process_lifecycle_gatew... production"]
        src_zephyr_shared_infra_process_pool_py["src/zephyr/shared/infra/process_pool.py prototype"]
        src_zephyr_shared_infra_06_init_py["src/zephyr/shared/infra_06/__init__.py production"]
        src_zephyr_shared_infra_06_idempotency_py["src/zephyr/shared/infra_06/idempotency.py prototype"]
        src_zephyr_shared_infra_06_limiter_py["src/zephyr/shared/infra_06/limiter.py prototype"]
        src_zephyr_shared_infra_06_lock_py["src/zephyr/shared/infra_06/lock.py prototype"]
        src_zephyr_shared_infra_06_observer_py["src/zephyr/shared/infra_06/observer.py prototype"]
        src_zephyr_shared_infra_06_outbox_py["src/zephyr/shared/infra_06/outbox.py prototype"]
        src_zephyr_shared_io_init_py["src/zephyr/shared/io/__init__.py prototype"]
        src_zephyr_shared_io_content_fingerprint_py["src/zephyr/shared/io/content_fingerprint.py prototype"]
        src_zephyr_shared_io_file_utils_py["src/zephyr/shared/io/file_utils.py prototype"]
        src_zephyr_shared_io_frontmatter_utils_py["src/zephyr/shared/io/frontmatter_utils.py prototype"]
        src_zephyr_shared_io_io_cache_py["src/zephyr/shared/io/io_cache.py prototype"]
        src_zephyr_shared_io_paths_py["src/zephyr/shared/io/paths.py prototype"]
        src_zephyr_shared_io_serialization_py["src/zephyr/shared/io/serialization.py prototype"]
        src_zephyr_shared_io_streaming_reader_py["src/zephyr/shared/io/streaming_reader.py prototype"]
        src_zephyr_shared_knowledge_init_py["src/zephyr/shared/knowledge/__init__.py production"]
        src_zephyr_shared_knowledge_ke_linker_py["src/zephyr/shared/knowledge/ke_linker.py prototype"]
        src_zephyr_shared_knowledge_ke_structurer_py["src/zephyr/shared/knowledge/ke_structurer.py prototype"]
        src_zephyr_shared_knowledge_kms_interface_py["src/zephyr/shared/knowledge/kms_interface.py prototype"]
        src_zephyr_shared_lifecycle_scope_guard_py["src/zephyr/shared/lifecycle/scope_guard.py production"]
        src_zephyr_shared_lifecycle_task_lifecycle_manager_py["src/zephyr/shared/lifecycle/task_lifecycle_mana... production"]
        src_zephyr_shared_limiter_py["src/zephyr/shared/limiter.py prototype"]
        src_zephyr_shared_lock_py["src/zephyr/shared/lock.py prototype"]
        src_zephyr_shared_logging_py["src/zephyr/shared/logging.py prototype"]
        src_zephyr_shared_longevity_monitor_py["src/zephyr/shared/longevity_monitor.py production"]
        src_zephyr_shared_maintenance_init_py["src/zephyr/shared/maintenance/__init__.py production"]
        src_zephyr_shared_maintenance_autonomy_monitor_py["src/zephyr/shared/maintenance/autonomy_monitor.py production"]
        src_zephyr_shared_maintenance_dogfooding_py["src/zephyr/shared/maintenance/dogfooding.py prototype"]
    end
    src_zephyr_shared_infra_process_lifecycle_gateway_py -.->|import_depends| src_zephyr_shared_infra_process_pool_py
    src_zephyr_shared_io_init_py -.->|config_depends| src_zephyr_shared_io_content_fingerprint_py
    src_zephyr_shared_knowledge_ke_linker_py -.->|config_depends| src_zephyr_shared_knowledge_ke_structurer_py
    src_zephyr_shared_knowledge_kms_interface_py -.->|config_depends| src_zephyr_shared_knowledge_ke_linker_py
    D_OPS["D_OPS prototype"]
    src_zephyr_shared_logging_py -.->|import_depends| D_OPS
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    src_zephyr_shared_infra_process_lifecycle_gateway_py -->|import_depends| D_INFRA_RUNTIME
    src_zephyr_shared_infra_process_pool_py -.->|import_depends| D_INFRA_RUNTIME
    src_zephyr_shared_io_io_cache_py -.->|import_depends| D_INFRA_RUNTIME
    D_GOV_AUDIT["D_GOV_AUDIT prototype"]
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_io_paths_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_io_paths_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_io_streaming_reader_py
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT production"]
    D_GOV_ENFORCEMENT -.->|import_depends| src_zephyr_shared_io_io_cache_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_longevity_monitor_py
    D_INFRA_RUNTIME -->|import_depends| src_zephyr_shared_infra_process_lifecycle_gateway_py
    D_INTEGRATION["D_INTEGRATION prototype"]
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_io_paths_py
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_io_paths_py
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_io_paths_py
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_io_paths_py
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_longevity_monitor_py
    D_GOVERNANCE -.->|test_depends| src_zephyr_shared_infra_process_lifecycle_gateway_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_infra_process_lifecycle_gateway_py,src_zephyr_shared_infra_06_init_py,src_zephyr_shared_knowledge_init_py,src_zephyr_shared_lifecycle_scope_guard_py,src_zephyr_shared_lifecycle_task_lifecycle_manager_py,src_zephyr_shared_longevity_monitor_py,src_zephyr_shared_maintenance_init_py,src_zephyr_shared_maintenance_autonomy_monitor_py production
    class src_zephyr_shared_infra_outbox_py,src_zephyr_shared_infra_process_pool_py,src_zephyr_shared_infra_06_idempotency_py,src_zephyr_shared_infra_06_limiter_py,src_zephyr_shared_infra_06_lock_py,src_zephyr_shared_infra_06_observer_py,src_zephyr_shared_infra_06_outbox_py,src_zephyr_shared_io_init_py,src_zephyr_shared_io_content_fingerprint_py,src_zephyr_shared_io_file_utils_py,src_zephyr_shared_io_frontmatter_utils_py,src_zephyr_shared_io_io_cache_py,src_zephyr_shared_io_paths_py,src_zephyr_shared_io_serialization_py,src_zephyr_shared_io_streaming_reader_py,src_zephyr_shared_knowledge_ke_linker_py,src_zephyr_shared_knowledge_ke_structurer_py,src_zephyr_shared_knowledge_kms_interface_py,src_zephyr_shared_limiter_py,src_zephyr_shared_lock_py,src_zephyr_shared_logging_py,src_zephyr_shared_maintenance_dogfooding_py design
    class D_INFRA_RUNTIME,D_GOV_ENFORCEMENT external_prod
    class D_OPS,D_GOV_AUDIT,D_INTEGRATION,D_GOVERNANCE external_design
```

### 第 7 页 / 共 9 页 / Page 7 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_maintenance_handbook_py["src/zephyr/shared/maintenance/handbook.py prototype"]
        src_zephyr_shared_maintenance_zero_config_py["src/zephyr/shared/maintenance/zero_config.py prototype"]
        src_zephyr_shared_metrics_py["src/zephyr/shared/metrics.py production"]
        src_zephyr_shared_migration_py["src/zephyr/shared/migration.py prototype"]
        src_zephyr_shared_model_capacity_probe_py["src/zephyr/shared/model_capacity_probe.py production"]
        src_zephyr_shared_models_py["src/zephyr/shared/models.py prototype"]
        src_zephyr_shared_module_birth_registry_py["src/zephyr/shared/module_birth_registry.py production"]
        src_zephyr_shared_observability_02_init_py["src/zephyr/shared/observability_02/__init__.py production"]
        src_zephyr_shared_observability_02_health_py["src/zephyr/shared/observability_02/health.py production"]
        src_zephyr_shared_observability_02_health_discovery_py["src/zephyr/shared/observability_02/health_disco... production"]
        src_zephyr_shared_observability_02_logging_py["src/zephyr/shared/observability_02/logging.py prototype"]
        src_zephyr_shared_observability_02_metrics_py["src/zephyr/shared/observability_02/metrics.py production"]
        src_zephyr_shared_observability_02_tracing_py["src/zephyr/shared/observability_02/tracing.py prototype"]
        src_zephyr_shared_observer_py["src/zephyr/shared/observer.py prototype"]
        src_zephyr_shared_outbox_py["src/zephyr/shared/outbox.py prototype"]
        src_zephyr_shared_owner_trust_gauge_py["src/zephyr/shared/owner_trust_gauge.py production"]
        src_zephyr_shared_pagination_py["src/zephyr/shared/pagination.py prototype"]
        src_zephyr_shared_ports_py["src/zephyr/shared/ports.py prototype"]
        src_zephyr_shared_protocols_init_py["src/zephyr/shared/protocols/__init__.py prototype"]
        src_zephyr_shared_protocols_a2a_init_py["src/zephyr/shared/protocols/a2a/__init__.py prototype"]
        src_zephyr_shared_protocols_a2a_a2a_coordination_py["src/zephyr/shared/protocols/a2a/a2a_coordinatio... prototype"]
        src_zephyr_shared_protocols_a2a_a2a_protocol_py["src/zephyr/shared/protocols/a2a/a2a_protocol.py prototype"]
        src_zephyr_shared_protocols_a2a_a2a_registry_py["src/zephyr/shared/protocols/a2a/a2a_registry.py prototype"]
        src_zephyr_shared_protocols_a2a_a2a_schemas_py["src/zephyr/shared/protocols/a2a/a2a_schemas.py prototype"]
        src_zephyr_shared_protocols_a2a_layer3_coordination_init_py["src/zephyr/shared/protocols/a2a/layer3_coordina... prototype"]
        src_zephyr_shared_queue_init_py["src/zephyr/shared/queue/__init__.py production"]
        src_zephyr_shared_queue_task_scheduler_py["src/zephyr/shared/queue/task_scheduler.py production"]
        src_zephyr_shared_reasoning_spans_py["src/zephyr/shared/reasoning_spans.py production"]
        src_zephyr_shared_registry_py["src/zephyr/shared/registry.py prototype"]
        src_zephyr_shared_reliability_init_py["src/zephyr/shared/reliability/__init__.py production"]
    end
    src_zephyr_shared_maintenance_handbook_py -.->|config_depends| src_zephyr_shared_maintenance_zero_config_py
    src_zephyr_shared_observability_02_health_discovery_py -->|config_depends| src_zephyr_shared_observability_02_health_py
    src_zephyr_shared_observability_02_tracing_py -.->|import_depends| src_zephyr_shared_observability_02_logging_py
    src_zephyr_shared_protocols_init_py -.->|import_depends| src_zephyr_shared_protocols_a2a_init_py
    src_zephyr_shared_protocols_a2a_init_py -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_registry_py
    src_zephyr_shared_protocols_a2a_init_py -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_protocol_py
    src_zephyr_shared_protocols_a2a_init_py -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_schemas_py
    src_zephyr_shared_protocols_a2a_init_py -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_coordination_py
    src_zephyr_shared_protocols_a2a_layer3_coordination_init_py -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_coordination_py
    D_OPS["D_OPS prototype"]
    src_zephyr_shared_metrics_py -.->|import_depends| D_OPS
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    src_zephyr_shared_protocols_a2a_init_py -.->|import_depends| D_GOVERNANCE
    src_zephyr_shared_protocols_a2a_layer3_coordination_init_py -.->|import_depends| D_GOVERNANCE
    D_GOVERNANCE -->|import_depends| src_zephyr_shared_module_birth_registry_py
    D_INFRA_RUNTIME["D_INFRA_RUNTIME production"]
    D_INFRA_RUNTIME -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_protocol_py
    D_INFRA_A2A["D_INFRA_A2A production"]
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_protocol_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_coordination_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_init_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_protocol_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_registry_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_registry_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_schemas_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_schemas_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_schemas_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_schemas_py
    D_INFRA_A2A -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_schemas_py
    D_INTEGRATION["D_INTEGRATION prototype"]
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_protocols_a2a_layer3_coordination_init_py
    D_INTEGRATION -.->|import_depends| src_zephyr_shared_protocols_a2a_a2a_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_metrics_py,src_zephyr_shared_model_capacity_probe_py,src_zephyr_shared_module_birth_registry_py,src_zephyr_shared_observability_02_init_py,src_zephyr_shared_observability_02_health_py,src_zephyr_shared_observability_02_health_discovery_py,src_zephyr_shared_observability_02_metrics_py,src_zephyr_shared_owner_trust_gauge_py,src_zephyr_shared_queue_init_py,src_zephyr_shared_queue_task_scheduler_py,src_zephyr_shared_reasoning_spans_py,src_zephyr_shared_reliability_init_py production
    class src_zephyr_shared_maintenance_handbook_py,src_zephyr_shared_maintenance_zero_config_py,src_zephyr_shared_migration_py,src_zephyr_shared_models_py,src_zephyr_shared_observability_02_logging_py,src_zephyr_shared_observability_02_tracing_py,src_zephyr_shared_observer_py,src_zephyr_shared_outbox_py,src_zephyr_shared_pagination_py,src_zephyr_shared_ports_py,src_zephyr_shared_protocols_init_py,src_zephyr_shared_protocols_a2a_init_py,src_zephyr_shared_protocols_a2a_a2a_coordination_py,src_zephyr_shared_protocols_a2a_a2a_protocol_py,src_zephyr_shared_protocols_a2a_a2a_registry_py,src_zephyr_shared_protocols_a2a_a2a_schemas_py,src_zephyr_shared_protocols_a2a_layer3_coordination_init_py,src_zephyr_shared_registry_py design
    class D_INFRA_RUNTIME,D_INFRA_A2A external_prod
    class D_OPS,D_GOVERNANCE,D_INTEGRATION external_design
```

### 第 8 页 / 共 9 页 / Page 8 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_reliability_context_guard_py["src/zephyr/shared/reliability/context_guard.py production"]
        src_zephyr_shared_reliability_diff_planner_py["src/zephyr/shared/reliability/diff_planner.py prototype"]
        src_zephyr_shared_reliability_retry_handler_py["src/zephyr/shared/reliability/retry_handler.py prototype"]
        src_zephyr_shared_resilience_init_py["src/zephyr/shared/resilience/__init__.py prototype"]
        src_zephyr_shared_resilience_circuit_breaker_py["src/zephyr/shared/resilience/circuit_breaker.py prototype"]
        src_zephyr_shared_resilience_fallback_py["src/zephyr/shared/resilience/fallback.py prototype"]
        src_zephyr_shared_resilience_retry_py["src/zephyr/shared/resilience/retry.py prototype"]
        src_zephyr_shared_sandbox_executor_py["src/zephyr/shared/sandbox_executor.py production"]
        src_zephyr_shared_schema_init_py["src/zephyr/shared/schema/__init__.py prototype"]
        src_zephyr_shared_schema_base_config_py["src/zephyr/shared/schema/base_config.py prototype"]
        src_zephyr_shared_schema_schema_registry_py["src/zephyr/shared/schema/schema_registry.py prototype"]
        src_zephyr_shared_schema_schemas_py["src/zephyr/shared/schema/schemas.py prototype"]
        src_zephyr_shared_schema_severity_types_py["src/zephyr/shared/schema/severity_types.py prototype"]
        src_zephyr_shared_schema_registry_py["src/zephyr/shared/schema_registry.py prototype"]
        src_zephyr_shared_schemas_py["src/zephyr/shared/schemas.py prototype"]
        src_zephyr_shared_secrets_py["src/zephyr/shared/secrets.py prototype"]
        src_zephyr_shared_security_init_py["src/zephyr/shared/security/__init__.py prototype"]
        src_zephyr_shared_security_capability_py["src/zephyr/shared/security/capability.py prototype"]
        src_zephyr_shared_security_secrets_py["src/zephyr/shared/security/secrets.py prototype"]
        src_zephyr_shared_security_ssot_guard_py["src/zephyr/shared/security/ssot_guard.py prototype"]
        src_zephyr_shared_serialization_py["src/zephyr/shared/serialization.py prototype"]
        src_zephyr_shared_session_init_py["src/zephyr/shared/session/__init__.py production"]
        src_zephyr_shared_session_session_boundary_py["src/zephyr/shared/session/session_boundary.py prototype"]
        src_zephyr_shared_session_audit_py["src/zephyr/shared/session_audit.py prototype"]
        src_zephyr_shared_session_continuity_py["src/zephyr/shared/session_continuity.py prototype"]
        src_zephyr_shared_slo_review_assistant_py["src/zephyr/shared/slo_review_assistant.py production"]
        src_zephyr_shared_ssot_guard_py["src/zephyr/shared/ssot_guard.py prototype"]
        src_zephyr_shared_state_machine_py["src/zephyr/shared/state_machine.py prototype"]
        src_zephyr_shared_task_heartbeat_py["src/zephyr/shared/task_heartbeat.py production"]
        src_zephyr_shared_task_types_py["src/zephyr/shared/task_types.py prototype"]
    end
    src_zephyr_shared_schema_registry_py -.->|import_depends| src_zephyr_shared_schema_schema_registry_py
    src_zephyr_shared_schemas_py -.->|import_depends| src_zephyr_shared_schema_schemas_py
    src_zephyr_shared_secrets_py -.->|import_depends| src_zephyr_shared_security_secrets_py
    src_zephyr_shared_ssot_guard_py -.->|import_depends| src_zephyr_shared_security_ssot_guard_py
    src_zephyr_shared_reliability_diff_planner_py -.->|config_depends| src_zephyr_shared_reliability_retry_handler_py
    src_zephyr_shared_schema_schemas_py -.->|import_depends| src_zephyr_shared_schema_severity_types_py
    src_zephyr_shared_schema_schemas_py -.->|import_depends| src_zephyr_shared_schema_base_config_py
    src_zephyr_shared_resilience_init_py -.->|config_depends| src_zephyr_shared_resilience_fallback_py
    src_zephyr_shared_schema_init_py -.->|config_depends| src_zephyr_shared_schema_severity_types_py
    src_zephyr_shared_security_init_py -.->|config_depends| src_zephyr_shared_security_secrets_py
    D_GOV_AUDIT["D_GOV_AUDIT production"]
    src_zephyr_shared_session_audit_py -.->|import_depends| D_GOV_AUDIT
    D_GOVERNANCE["D_GOVERNANCE prototype"]
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_task_types_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_resilience_fallback_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_shared_state_machine_py
    D_GOV_DOCS["D_GOV_DOCS prototype"]
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_schema_schemas_py
    D_GOV_DOCS -.->|import_depends| src_zephyr_shared_security_capability_py
    D_GOV_ENFORCEMENT["D_GOV_ENFORCEMENT production"]
    D_GOV_ENFORCEMENT -->|import_depends| src_zephyr_shared_slo_review_assistant_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_reliability_context_guard_py,src_zephyr_shared_sandbox_executor_py,src_zephyr_shared_session_init_py,src_zephyr_shared_slo_review_assistant_py,src_zephyr_shared_task_heartbeat_py production
    class src_zephyr_shared_reliability_diff_planner_py,src_zephyr_shared_reliability_retry_handler_py,src_zephyr_shared_resilience_init_py,src_zephyr_shared_resilience_circuit_breaker_py,src_zephyr_shared_resilience_fallback_py,src_zephyr_shared_resilience_retry_py,src_zephyr_shared_schema_init_py,src_zephyr_shared_schema_base_config_py,src_zephyr_shared_schema_schema_registry_py,src_zephyr_shared_schema_schemas_py,src_zephyr_shared_schema_severity_types_py,src_zephyr_shared_schema_registry_py,src_zephyr_shared_schemas_py,src_zephyr_shared_secrets_py,src_zephyr_shared_security_init_py,src_zephyr_shared_security_capability_py,src_zephyr_shared_security_secrets_py,src_zephyr_shared_security_ssot_guard_py,src_zephyr_shared_serialization_py,src_zephyr_shared_session_session_boundary_py,src_zephyr_shared_session_audit_py,src_zephyr_shared_session_continuity_py,src_zephyr_shared_ssot_guard_py,src_zephyr_shared_state_machine_py,src_zephyr_shared_task_types_py design
    class D_GOV_AUDIT,D_GOV_ENFORCEMENT external_prod
    class D_GOVERNANCE,D_GOV_DOCS external_design
```

### 第 9 页 / 共 9 页 / Page 9 of 9

```mermaid
graph TD
    subgraph D_SHARED["D_SHARED 共享服务"]
        src_zephyr_shared_testing_py["src/zephyr/shared/testing.py prototype"]
        src_zephyr_shared_time_utils_py["src/zephyr/shared/time_utils.py prototype"]
        src_zephyr_shared_tracing_py["src/zephyr/shared/tracing.py prototype"]
        src_zephyr_shared_ttl_cleanup_engine_py["src/zephyr/shared/ttl_cleanup_engine.py production"]
        src_zephyr_shared_types_py["src/zephyr/shared/types.py prototype"]
        src_zephyr_shared_utils_init_py["src/zephyr/shared/utils/__init__.py prototype"]
        src_zephyr_shared_utils_context_py["src/zephyr/shared/utils/context.py prototype"]
        src_zephyr_shared_utils_db_utils_py["src/zephyr/shared/utils/db_utils.py prototype"]
        src_zephyr_shared_utils_diff_utils_py["src/zephyr/shared/utils/diff_utils.py prototype"]
        src_zephyr_shared_utils_migration_py["src/zephyr/shared/utils/migration.py prototype"]
        src_zephyr_shared_utils_pagination_py["src/zephyr/shared/utils/pagination.py prototype"]
        src_zephyr_shared_utils_testing_py["src/zephyr/shared/utils/testing.py prototype"]
        src_zephyr_shared_utils_time_utils_py["src/zephyr/shared/utils/time_utils.py prototype"]
        src_zephyr_shared_vibe_experiment_tracker_py["src/zephyr/shared/vibe_experiment_tracker.py production"]
        src_zephyr_shared_zephyr_logger_py["src/zephyr/shared/zephyr_logger.py production"]
    end
    src_zephyr_shared_testing_py -.->|import_depends| src_zephyr_shared_utils_testing_py
    src_zephyr_shared_time_utils_py -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    src_zephyr_shared_utils_init_py -.->|import_depends| src_zephyr_shared_utils_context_py
    D_OPS["D_OPS prototype"]
    src_zephyr_shared_zephyr_logger_py -.->|import_depends| D_OPS
    src_zephyr_shared_tracing_py -.->|import_depends| D_OPS
    D_GOV_AUDIT["D_GOV_AUDIT prototype"]
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_db_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_db_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_db_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_db_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_db_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_db_utils_py
    D_GOV_AUDIT -.->|import_depends| src_zephyr_shared_utils_time_utils_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_shared_ttl_cleanup_engine_py,src_zephyr_shared_vibe_experiment_tracker_py,src_zephyr_shared_zephyr_logger_py production
    class src_zephyr_shared_testing_py,src_zephyr_shared_time_utils_py,src_zephyr_shared_tracing_py,src_zephyr_shared_types_py,src_zephyr_shared_utils_init_py,src_zephyr_shared_utils_context_py,src_zephyr_shared_utils_db_utils_py,src_zephyr_shared_utils_diff_utils_py,src_zephyr_shared_utils_migration_py,src_zephyr_shared_utils_pagination_py,src_zephyr_shared_utils_testing_py,src_zephyr_shared_utils_time_utils_py design
    class D_OPS,D_GOV_AUDIT external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_OPS | 5 | import_depends |
| D_INFRA_RUNTIME | 4 | import_depends |
| D_GOVERNANCE | 3 | import_depends |
| D_INTEGRATION | 2 | import_depends |
| D_ML_TRAIN | 2 | import_depends |
| D_GOV_AUDIT | 1 | import_depends |
| D_SIMULATION | 1 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_GOVERNANCE | 73 | import_depends,test_depends |
| D_GOV_AUDIT | 33 | import_depends |
| D_TRADING | 31 | contract,import_depends |
| D_INTEGRATION | 29 | import_depends |
| D_INFRA_RUNTIME | 21 | import_depends |
| D_INFRA_A2A | 16 | import_depends |
| D_GOV_DOCS | 8 | import_depends |
| D_GOV_ENFORCEMENT | 7 | import_depends |
| D_OPS | 6 | import_depends |
| D_INFRA_RECOVERY | 4 | import_depends |
| D_SECURITY | 4 | import_depends |
| D_AUTONOMY_CORE | 3 | import_depends |
| D_INFRA_TELEMETRY | 2 | import_depends |
| D_ML_TRAIN | 2 | import_depends |
| D_PF_ALLOC | 2 | contract,import_depends |
| D_INTELLIGENCE | 1 | import_depends |
| D_GOV_SCRIPTS | 1 | import_depends |
| D_FACTOR | 1 | import_depends |
| D_INFRA_OPS | 1 | import_depends |
| D_RISK | 1 | import_depends |
| D_CROSS_ASSET | 1 | import_depends |
| D_FRONTEND | 1 | import_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 共享服务（D_SHARED）的模块分布。共 255 个模块 / 255 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│        L0 基础设施层 / Infrastructure Layer (67 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/shared/contracts/__init__.py  [prototype]           │
│   src/zephyr/shared/contracts/backpressure/__init__.py  [prot... │
│   src/zephyr/shared/contracts/backpressure/_types.py  [protot... │
│   src/zephyr/shared/contracts/backpressure/pause.py  [prototype] │
│   src/zephyr/shared/contracts/backpressure/resume.py  [protot... │
│   src/zephyr/shared/contracts/backpressure/throttle.py  [prot... │
│   src/zephyr/shared/contracts/core/__init__.py  [prototype]      │
│   src/zephyr/shared/contracts/core/base_event.py  [prototype]    │
│   src/zephyr/shared/contracts/core/enforcer.py  [prototype]      │
│   src/zephyr/shared/contracts/core/factories.py  [prototype]     │
│   src/zephyr/shared/contracts/core/gate_types.py  [prototype]    │
│   src/zephyr/shared/contracts/core/registry.py  [prototype]      │
│   src/zephyr/shared/contracts/core/runtime_plane_tag.py  [pro... │
│   src/zephyr/shared/contracts/core/system_configuration.py  [... │
│   src/zephyr/shared/contracts/core/telemetry_emitter.py  [pro... │
│   src/zephyr/shared/contracts/core/timestamp.py  [prototype]     │
│   src/zephyr/shared/contracts/core/trace_context.py  [prototype] │
│   src/zephyr/shared/contracts/errors/__init__.py  [prototype]    │
│   ...还有 49 个模块 / 49 more modules                            │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (173 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/integration/shared/api_03/api_index.py  [prototype] │
│   src/zephyr/shared/__init__.py  [production]                    │
│   src/zephyr/shared/__version__.py  [prototype]                  │
│   src/zephyr/shared/_cross_layer/__init__.py  [prototype]        │
│   src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py  [... │
│   src/zephyr/shared/adaptation/execution_tuner.py  [prototype]   │
│   src/zephyr/shared/adaptation/prompt_version_manager.py  [pr... │
│   src/zephyr/shared/adaptive_sampler.py  [production]            │
│   src/zephyr/shared/ai_audit_guard.py  [production]              │
│   src/zephyr/shared/ai_understandability_constraint.py  [prod... │
│   src/zephyr/shared/alert_escalation.py  [production]            │
│   src/zephyr/shared/alert_manager.py  [production]               │
│   src/zephyr/shared/alert_precision_tracker.py  [production]     │
│   src/zephyr/shared/api/__init__.py  [prototype]                 │
│   src/zephyr/shared/api/api_client.py  [prototype]               │
│   src/zephyr/shared/api/api_index.py  [prototype]                │
│   src/zephyr/shared/api/dos_launcher.py  [prototype]             │
│   src/zephyr/shared/api_client.py  [prototype]                   │
│   ...还有 155 个模块 / 155 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (15 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/shared/adaptation/__init__.py  [production]         │
│   src/zephyr/shared/compensation/__init__.py  [production]       │
│   src/zephyr/shared/dependency/__init__.py  [production]         │
│   src/zephyr/shared/draft/__init__.py  [production]              │
│   src/zephyr/shared/infra_06/__init__.py  [production]           │
│   src/zephyr/shared/knowledge/__init__.py  [production]          │
│   src/zephyr/shared/lifecycle/scope_guard.py  [production]       │
│   src/zephyr/shared/lifecycle/task_lifecycle_manager.py  [pro... │
│   src/zephyr/shared/maintenance/__init__.py  [production]        │
│   src/zephyr/shared/observability_02/__init__.py  [production]   │
│   src/zephyr/shared/queue/__init__.py  [production]              │
│   src/zephyr/shared/queue/task_scheduler.py  [production]        │
│   src/zephyr/shared/reliability/__init__.py  [production]        │
│   src/zephyr/shared/reliability/context_guard.py  [production]   │
│   src/zephyr/shared/session/__init__.py  [production]            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 255 个模块 / 255 modules）。

### L0 基础设施层 / Infrastructure Layer (67 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/shared/contracts/__init__.py | src/zephyr/shared/contracts/__init__.py | prototype | generated |
| 2 | src/zephyr/shared/contracts/backpressure/__init__.py | src/zephyr/shared/contracts/backpress... | prototype | generated |
| 3 | src/zephyr/shared/contracts/backpressure/_types.py | src/zephyr/shared/contracts/backpress... | prototype | generated |
| 4 | src/zephyr/shared/contracts/backpressure/pause.py | src/zephyr/shared/contracts/backpress... | prototype | generated |
| 5 | src/zephyr/shared/contracts/backpressure/resume.py | src/zephyr/shared/contracts/backpress... | prototype | generated |
| 6 | src/zephyr/shared/contracts/backpressure/throttle.py | src/zephyr/shared/contracts/backpress... | prototype | generated |
| 7 | src/zephyr/shared/contracts/core/__init__.py | src/zephyr/shared/contracts/core/__in... | prototype | generated |
| 8 | src/zephyr/shared/contracts/core/base_event.py | src/zephyr/shared/contracts/core/base... | prototype | generated |
| 9 | src/zephyr/shared/contracts/core/enforcer.py | src/zephyr/shared/contracts/core/enfo... | prototype | generated |
| 10 | src/zephyr/shared/contracts/core/factories.py | src/zephyr/shared/contracts/core/fact... | prototype | generated |
| 11 | src/zephyr/shared/contracts/core/gate_types.py | src/zephyr/shared/contracts/core/gate... | prototype | generated |
| 12 | src/zephyr/shared/contracts/core/registry.py | src/zephyr/shared/contracts/core/regi... | prototype | generated |
| 13 | src/zephyr/shared/contracts/core/runtime_plane_tag.py | src/zephyr/shared/contracts/core/runt... | prototype | generated |
| 14 | src/zephyr/shared/contracts/core/system_configuration.py | src/zephyr/shared/contracts/core/syst... | prototype | generated |
| 15 | src/zephyr/shared/contracts/core/telemetry_emitter.py | src/zephyr/shared/contracts/core/tele... | production | stable |
| 16 | src/zephyr/shared/contracts/core/timestamp.py | src/zephyr/shared/contracts/core/time... | prototype | generated |
| 17 | src/zephyr/shared/contracts/core/trace_context.py | src/zephyr/shared/contracts/core/trac... | prototype | generated |
| 18 | src/zephyr/shared/contracts/errors/__init__.py | src/zephyr/shared/contracts/errors/__... | prototype | generated |
| 19 | src/zephyr/shared/contracts/errors/contract_violation_err... | src/zephyr/shared/contracts/errors/co... | prototype | generated |
| 20 | src/zephyr/shared/contracts/errors/data_quality_error.py | src/zephyr/shared/contracts/errors/da... | prototype | generated |
| 21 | src/zephyr/shared/contracts/errors/execution_rejection_er... | src/zephyr/shared/contracts/errors/ex... | prototype | generated |
| 22 | src/zephyr/shared/contracts/errors/factor_computation_err... | src/zephyr/shared/contracts/errors/fa... | prototype | generated |
| 23 | src/zephyr/shared/contracts/errors/risk_limit_violation_e... | src/zephyr/shared/contracts/errors/ri... | prototype | generated |
| 24 | src/zephyr/shared/contracts/errors/signal_degradation_war... | src/zephyr/shared/contracts/errors/si... | prototype | generated |
| 25 | src/zephyr/shared/contracts/escalation/__init__.py | src/zephyr/shared/contracts/escalatio... | prototype | generated |
| 26 | src/zephyr/shared/contracts/escalation/budget_alert.py | src/zephyr/shared/contracts/escalatio... | production | generated |
| 27 | src/zephyr/shared/contracts/execution/__init__.py | src/zephyr/shared/contracts/execution... | prototype | generated |
| 28 | src/zephyr/shared/contracts/execution/capital_allocation_... | src/zephyr/shared/contracts/execution... | prototype | generated |
| 29 | src/zephyr/shared/contracts/execution/execution_report.py | src/zephyr/shared/contracts/execution... | prototype | generated |
| 30 | src/zephyr/shared/contracts/execution/fill.py | src/zephyr/shared/contracts/execution... | prototype | generated |
| 31 | src/zephyr/shared/contracts/execution/model_serving_reque... | src/zephyr/shared/contracts/execution... | prototype | generated |
| 32 | src/zephyr/shared/contracts/execution/order.py | src/zephyr/shared/contracts/execution... | prototype | generated |
| 33 | src/zephyr/shared/contracts/experiment/__init__.py | src/zephyr/shared/contracts/experimen... | prototype | generated |
| 34 | src/zephyr/shared/contracts/experiment/experiment_result.py | src/zephyr/shared/contracts/experimen... | prototype | generated |
| 35 | src/zephyr/shared/contracts/experiment/model_serving_resp... | src/zephyr/shared/contracts/experimen... | prototype | generated |
| 36 | src/zephyr/shared/contracts/external/__init__.py | src/zephyr/shared/contracts/external/... | prototype | generated |
| 37 | src/zephyr/shared/contracts/external/ext_001.py | src/zephyr/shared/contracts/external/... | prototype | generated |
| 38 | src/zephyr/shared/contracts/external/ext_002.py | src/zephyr/shared/contracts/external/... | prototype | generated |
| 39 | src/zephyr/shared/contracts/external/ext_003.py | src/zephyr/shared/contracts/external/... | prototype | generated |
| 40 | src/zephyr/shared/contracts/external/ext_004.py | src/zephyr/shared/contracts/external/... | prototype | generated |
| 41 | src/zephyr/shared/contracts/identity/__init__.py | src/zephyr/shared/contracts/identity/... | prototype | generated |
| 42 | src/zephyr/shared/contracts/identity/agent_identity.py | src/zephyr/shared/contracts/identity/... | prototype | generated |
| 43 | src/zephyr/shared/contracts/identity/permission.py | src/zephyr/shared/contracts/identity/... | prototype | generated |
| 44 | src/zephyr/shared/contracts/llm_gateway_protocol.py | src/zephyr/shared/contracts/llm_gatew... | prototype | generated |
| 45 | src/zephyr/shared/contracts/market/__init__.py | src/zephyr/shared/contracts/market/__... | prototype | generated |
| 46 | src/zephyr/shared/contracts/market/factor_monitor_report.py | src/zephyr/shared/contracts/market/fa... | production | stable |
| 47 | src/zephyr/shared/contracts/market/factor_signal.py | src/zephyr/shared/contracts/market/fa... | prototype | generated |
| 48 | src/zephyr/shared/contracts/market/instrument.py | src/zephyr/shared/contracts/market/in... | prototype | generated |
| 49 | src/zephyr/shared/contracts/market/macro_factor_signal.py | src/zephyr/shared/contracts/market/ma... | prototype | generated |
| 50 | src/zephyr/shared/contracts/market/market_data.py | src/zephyr/shared/contracts/market/ma... | prototype | generated |
| 51 | src/zephyr/shared/contracts/market/synthesized_signal.py | src/zephyr/shared/contracts/market/sy... | prototype | generated |
| 52 | src/zephyr/shared/contracts/orchestration_protocol.py | src/zephyr/shared/contracts/orchestra... | prototype | generated |
| 53 | src/zephyr/shared/contracts/portfolio/__init__.py | src/zephyr/shared/contracts/portfolio... | prototype | generated |
| 54 | src/zephyr/shared/contracts/portfolio/money.py | src/zephyr/shared/contracts/portfolio... | production | generated |
| 55 | src/zephyr/shared/contracts/portfolio/performance_attribu... | src/zephyr/shared/contracts/portfolio... | prototype | generated |
| 56 | src/zephyr/shared/contracts/portfolio/position.py | src/zephyr/shared/contracts/portfolio... | prototype | generated |
| 57 | src/zephyr/shared/contracts/portfolio/strategy_lifecycle_... | src/zephyr/shared/contracts/portfolio... | prototype | generated |
| 58 | src/zephyr/shared/contracts/risk/__init__.py | src/zephyr/shared/contracts/risk/__in... | prototype | generated |
| 59 | src/zephyr/shared/contracts/risk/compliance_rule.py | src/zephyr/shared/contracts/risk/comp... | prototype | generated |
| 60 | src/zephyr/shared/contracts/risk/risk_dashboard_snapshot.py | src/zephyr/shared/contracts/risk/risk... | production | stable |
| 61 | src/zephyr/shared/contracts/risk/risk_limits.py | src/zephyr/shared/contracts/risk/risk... | prototype | generated |
| 62 | src/zephyr/shared/contracts/risk/risk_metrics.py | src/zephyr/shared/contracts/risk/risk... | production | stable |
| 63 | src/zephyr/shared/contracts/risk/risk_validator_protocol.py | src/zephyr/shared/contracts/risk/risk... | prototype | generated |
| 64 | src/zephyr/shared/contracts/security/__init__.py | src/zephyr/shared/contracts/security/... | prototype | generated |
| 65 | src/zephyr/shared/contracts/security/security_decision.py | src/zephyr/shared/contracts/security/... | prototype | generated |
| 66 | src/zephyr/shared/contracts/skill_protocol.py | src/zephyr/shared/contracts/skill_pro... | prototype | generated |
| 67 | src/zephyr/shared/contracts/task_repository_protocol.py | src/zephyr/shared/contracts/task_repo... | prototype | generated |

### L1 基础层 / Foundation Layer (173 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/integration/shared/api_03/api_index.py | src/zephyr/integration/shared/api_03/... | prototype | generated |
| 2 | src/zephyr/shared/__init__.py | src/zephyr/shared/__init__.py | production | generated |
| 3 | src/zephyr/shared/__version__.py | src/zephyr/shared/__version__.py | prototype | generated |
| 4 | src/zephyr/shared/_cross_layer/__init__.py | src/zephyr/shared/_cross_layer/__init... | prototype | generated |
| 5 | src/zephyr/shared/_cross_layer/ml_experiment_pipeline.py | src/zephyr/shared/_cross_layer/ml_exp... | prototype | generated |
| 6 | src/zephyr/shared/adaptation/execution_tuner.py | src/zephyr/shared/adaptation/executio... | prototype | generated |
| 7 | src/zephyr/shared/adaptation/prompt_version_manager.py | src/zephyr/shared/adaptation/prompt_v... | prototype | generated |
| 8 | src/zephyr/shared/adaptive_sampler.py | src/zephyr/shared/adaptive_sampler.py | production | generated |
| 9 | src/zephyr/shared/ai_audit_guard.py | src/zephyr/shared/ai_audit_guard.py | production | generated |
| 10 | src/zephyr/shared/ai_understandability_constraint.py | src/zephyr/shared/ai_understandabilit... | production | generated |
| 11 | src/zephyr/shared/alert_escalation.py | src/zephyr/shared/alert_escalation.py | production | generated |
| 12 | src/zephyr/shared/alert_manager.py | src/zephyr/shared/alert_manager.py | production | generated |
| 13 | src/zephyr/shared/alert_precision_tracker.py | src/zephyr/shared/alert_precision_tra... | production | generated |
| 14 | src/zephyr/shared/api/__init__.py | src/zephyr/shared/api/__init__.py | prototype | generated |
| 15 | src/zephyr/shared/api/api_client.py | src/zephyr/shared/api/api_client.py | prototype | generated |
| 16 | src/zephyr/shared/api/api_index.py | src/zephyr/shared/api/api_index.py | prototype | generated |
| 17 | src/zephyr/shared/api/dos_launcher.py | src/zephyr/shared/api/dos_launcher.py | prototype | generated |
| 18 | src/zephyr/shared/api_client.py | src/zephyr/shared/api_client.py | prototype | generated |
| 19 | src/zephyr/shared/blueprint_code_auditor.py | src/zephyr/shared/blueprint_code_audi... | production | generated |
| 20 | src/zephyr/shared/blueprint_decomposer.py | src/zephyr/shared/blueprint_decompose... | prototype | generated |
| 21 | src/zephyr/shared/blueprint_scorer.py | src/zephyr/shared/blueprint_scorer.py | prototype | generated |
| 22 | src/zephyr/shared/budget_aware_prompt.py | src/zephyr/shared/budget_aware_prompt.py | production | generated |
| 23 | src/zephyr/shared/cache.py | src/zephyr/shared/cache.py | prototype | generated |
| 24 | src/zephyr/shared/capability.py | src/zephyr/shared/capability.py | prototype | generated |
| 25 | src/zephyr/shared/capacity_calibrator.py | src/zephyr/shared/capacity_calibrator.py | production | generated |
| 26 | src/zephyr/shared/capacity_digital_twin.py | src/zephyr/shared/capacity_digital_tw... | production | generated |
| 27 | src/zephyr/shared/capacity_fingerprint.py | src/zephyr/shared/capacity_fingerprin... | production | generated |
| 28 | src/zephyr/shared/capacity_runbook_generator.py | src/zephyr/shared/capacity_runbook_ge... | production | generated |
| 29 | src/zephyr/shared/code_economy_analyzer.py | src/zephyr/shared/code_economy_analyz... | production | generated |
| 30 | src/zephyr/shared/combinatorial_gate.py | src/zephyr/shared/combinatorial_gate.py | production | generated |
| 31 | ~~src/zephyr/shared/config/__init__.py~~ | ❌ ARCH-038 已删除 | prototype | generated |
| 32 | ~~src/zephyr/shared/config/loader.py~~ | ❌ ARCH-038 已删除（虚假统一空壳，0消费者） | prototype | generated |
| 33 | src/zephyr/shared/constants.py | src/zephyr/shared/constants.py | prototype | generated |
| 34 | src/zephyr/shared/content_fingerprint.py | src/zephyr/shared/content_fingerprint.py | prototype | generated |
| 35 | src/zephyr/shared/context_engine.py | src/zephyr/shared/context_engine.py | prototype | generated |
| 36 | src/zephyr/shared/contract_bus.py | src/zephyr/shared/contract_bus.py | prototype | generated |
| 37 | src/zephyr/shared/contract_tester.py | src/zephyr/shared/contract_tester.py | prototype | generated |
| 38 | src/zephyr/shared/core_integrity_guard.py | src/zephyr/shared/core_integrity_guar... | production | generated |
| 39 | src/zephyr/shared/cost_estimator.py | src/zephyr/shared/cost_estimator.py | production | generated |
| 40 | src/zephyr/shared/degradation_chain.py | src/zephyr/shared/degradation_chain.py | production | generated |
| 41 | src/zephyr/shared/dependency_capacity_guard.py | src/zephyr/shared/dependency_capacity... | production | generated |
| 42 | src/zephyr/shared/deprecation.py | src/zephyr/shared/deprecation.py | prototype | generated |
| 43 | src/zephyr/shared/diff_utils.py | src/zephyr/shared/diff_utils.py | prototype | generated |
| 44 | src/zephyr/shared/dual_channel_alert.py | src/zephyr/shared/dual_channel_alert.py | production | generated |
| 45 | src/zephyr/shared/env.py | src/zephyr/shared/env.py | prototype | generated |
| 46 | src/zephyr/shared/error_budget_tracker.py | src/zephyr/shared/error_budget_tracke... | production | generated |
| 47 | src/zephyr/shared/errors.py | src/zephyr/shared/errors.py | prototype | generated |
| 48 | src/zephyr/shared/event_bus.py | src/zephyr/shared/event_bus.py | production | stable |
| 49 | src/zephyr/shared/event_bus.py | src/zephyr/shared/event_bus.py | production | generated |
| 50 | src/zephyr/shared/events/__init__.py | src/zephyr/shared/events/__init__.py | prototype | generated |
| 51 | src/zephyr/shared/events/dlq.py | src/zephyr/shared/events/dlq.py | prototype | generated |
| 52 | src/zephyr/shared/events/dlq_bridge.py | src/zephyr/shared/events/dlq_bridge.py | prototype | generated |
| 53 | src/zephyr/shared/events/event_bus.py | src/zephyr/shared/events/event_bus.py | production | stable |
| 54 | src/zephyr/shared/events/event_bus_upgrade.py | src/zephyr/shared/events/event_bus_up... | production | generated |
| 55 | src/zephyr/shared/events/event_reactor.py | src/zephyr/shared/events/event_reacto... | prototype | generated |
| 56 | src/zephyr/shared/events/event_schemas.py | src/zephyr/shared/events/event_schema... | prototype | generated |
| 57 | src/zephyr/shared/events/hook_dispatcher.py | src/zephyr/shared/events/hook_dispatc... | prototype | generated |
| 58 | src/zephyr/shared/events/upgrade_strategy.py | src/zephyr/shared/events/upgrade_stra... | prototype | generated |
| 59 | src/zephyr/shared/fault_isolator.py | src/zephyr/shared/fault_isolator.py | production | generated |
| 60 | src/zephyr/shared/file_utils.py | src/zephyr/shared/file_utils.py | prototype | generated |
| 61 | src/zephyr/shared/flags.py | src/zephyr/shared/flags.py | prototype | generated |
| 62 | src/zephyr/shared/foundation/__init__.py | src/zephyr/shared/foundation/__init__.py | prototype | generated |
| 63 | src/zephyr/shared/foundation/constants.py | src/zephyr/shared/foundation/constant... | prototype | generated |
| 64 | src/zephyr/shared/foundation/deprecation.py | src/zephyr/shared/foundation/deprecat... | prototype | generated |
| 65 | src/zephyr/shared/foundation/env.py | src/zephyr/shared/foundation/env.py | prototype | generated |
| 66 | src/zephyr/shared/foundation/errors.py | src/zephyr/shared/foundation/errors.py | prototype | generated |
| 67 | src/zephyr/shared/foundation/flags.py | src/zephyr/shared/foundation/flags.py | prototype | generated |
| 68 | src/zephyr/shared/foundation/types.py | src/zephyr/shared/foundation/types.py | prototype | generated |
| 69 | src/zephyr/shared/frontmatter_utils.py | src/zephyr/shared/frontmatter_utils.py | prototype | generated |
| 70 | src/zephyr/shared/health.py | src/zephyr/shared/health.py | production | stable |
| 71 | src/zephyr/shared/healthcheck_service.py | src/zephyr/shared/healthcheck_service.py | production | stable |
| 72 | src/zephyr/shared/heartbeat_server.py | src/zephyr/shared/heartbeat_server.py | production | generated |
| 73 | src/zephyr/shared/idempotency.py | src/zephyr/shared/idempotency.py | prototype | generated |
| 74 | src/zephyr/shared/infra/__init__.py | src/zephyr/shared/infra/__init__.py | prototype | generated |
| 75 | src/zephyr/shared/infra/cache.py | src/zephyr/shared/infra/cache.py | prototype | generated |
| 76 | src/zephyr/shared/infra/idempotency.py | src/zephyr/shared/infra/idempotency.py | prototype | generated |
| 77 | src/zephyr/shared/infra/limiter.py | src/zephyr/shared/infra/limiter.py | prototype | generated |
| 78 | src/zephyr/shared/infra/lock.py | src/zephyr/shared/infra/lock.py | prototype | generated |
| 79 | src/zephyr/shared/infra/observer.py | src/zephyr/shared/infra/observer.py | prototype | generated |
| 80 | src/zephyr/shared/infra/outbox.py | src/zephyr/shared/infra/outbox.py | prototype | generated |
| 81 | src/zephyr/shared/infra/process_lifecycle_gateway.py | src/zephyr/shared/infra/process_lifec... | production | generated |
| 82 | src/zephyr/shared/infra/process_pool.py | src/zephyr/shared/infra/process_pool.py | prototype | generated |
| 83 | src/zephyr/shared/infra_06/idempotency.py | src/zephyr/shared/infra_06/idempotenc... | prototype | generated |
| 84 | src/zephyr/shared/infra_06/limiter.py | src/zephyr/shared/infra_06/limiter.py | prototype | generated |
| 85 | src/zephyr/shared/infra_06/lock.py | src/zephyr/shared/infra_06/lock.py | prototype | generated |
| 86 | src/zephyr/shared/infra_06/observer.py | src/zephyr/shared/infra_06/observer.py | prototype | generated |
| 87 | src/zephyr/shared/infra_06/outbox.py | src/zephyr/shared/infra_06/outbox.py | prototype | generated |
| 88 | src/zephyr/shared/io/__init__.py | src/zephyr/shared/io/__init__.py | prototype | generated |
| 89 | src/zephyr/shared/io/content_fingerprint.py | src/zephyr/shared/io/content_fingerpr... | prototype | generated |
| 90 | src/zephyr/shared/io/file_utils.py | src/zephyr/shared/io/file_utils.py | prototype | generated |
| 91 | src/zephyr/shared/io/frontmatter_utils.py | src/zephyr/shared/io/frontmatter_util... | prototype | generated |
| 92 | src/zephyr/shared/io/io_cache.py | src/zephyr/shared/io/io_cache.py | prototype | generated |
| 93 | src/zephyr/shared/io/paths.py | src/zephyr/shared/io/paths.py | prototype | generated |
| 94 | src/zephyr/shared/io/serialization.py | src/zephyr/shared/io/serialization.py | prototype | generated |
| 95 | src/zephyr/shared/io/streaming_reader.py | src/zephyr/shared/io/streaming_reader.py | prototype | generated |
| 96 | src/zephyr/shared/knowledge/ke_linker.py | src/zephyr/shared/knowledge/ke_linker.py | prototype | generated |
| 97 | src/zephyr/shared/knowledge/ke_structurer.py | src/zephyr/shared/knowledge/ke_struct... | prototype | generated |
| 98 | src/zephyr/shared/knowledge/kms_interface.py | src/zephyr/shared/knowledge/kms_inter... | prototype | generated |
| 99 | src/zephyr/shared/limiter.py | src/zephyr/shared/limiter.py | prototype | generated |
| 100 | src/zephyr/shared/lock.py | src/zephyr/shared/lock.py | prototype | generated |
| 101 | src/zephyr/shared/logging.py | src/zephyr/shared/logging.py | prototype | generated |
| 102 | src/zephyr/shared/longevity_monitor.py | src/zephyr/shared/longevity_monitor.py | production | generated |
| 103 | src/zephyr/shared/maintenance/autonomy_monitor.py | src/zephyr/shared/maintenance/autonom... | production | stable |
| 104 | src/zephyr/shared/maintenance/dogfooding.py | src/zephyr/shared/maintenance/dogfood... | prototype | generated |
| 105 | src/zephyr/shared/maintenance/handbook.py | src/zephyr/shared/maintenance/handboo... | prototype | generated |
| 106 | src/zephyr/shared/maintenance/zero_config.py | src/zephyr/shared/maintenance/zero_co... | prototype | generated |
| 107 | src/zephyr/shared/metrics.py | src/zephyr/shared/metrics.py | production | stable |
| 108 | src/zephyr/shared/migration.py | src/zephyr/shared/migration.py | prototype | generated |
| 109 | src/zephyr/shared/model_capacity_probe.py | src/zephyr/shared/model_capacity_prob... | production | generated |
| 110 | src/zephyr/shared/models.py | src/zephyr/shared/models.py | prototype | generated |
| 111 | src/zephyr/shared/module_birth_registry.py | src/zephyr/shared/module_birth_regist... | production | generated |
| 112 | src/zephyr/shared/observability_02/health.py | src/zephyr/shared/observability_02/he... | production | stable |
| 113 | src/zephyr/shared/observability_02/health_discovery.py | src/zephyr/shared/observability_02/he... | production | stable |
| 114 | src/zephyr/shared/observability_02/logging.py | src/zephyr/shared/observability_02/lo... | prototype | generated |
| 115 | src/zephyr/shared/observability_02/metrics.py | src/zephyr/shared/observability_02/me... | production | stable |
| 116 | src/zephyr/shared/observability_02/tracing.py | src/zephyr/shared/observability_02/tr... | prototype | generated |
| 117 | src/zephyr/shared/observer.py | src/zephyr/shared/observer.py | prototype | generated |
| 118 | src/zephyr/shared/outbox.py | src/zephyr/shared/outbox.py | prototype | generated |
| 119 | src/zephyr/shared/owner_trust_gauge.py | src/zephyr/shared/owner_trust_gauge.py | production | generated |
| 120 | src/zephyr/shared/pagination.py | src/zephyr/shared/pagination.py | prototype | generated |
| 121 | src/zephyr/shared/ports.py | src/zephyr/shared/ports.py | prototype | generated |
| 122 | src/zephyr/shared/protocols/__init__.py | src/zephyr/shared/protocols/__init__.py | prototype | generated |
| 123 | src/zephyr/shared/protocols/a2a/__init__.py | src/zephyr/shared/protocols/a2a/__ini... | prototype | generated |
| 124 | src/zephyr/shared/protocols/a2a/a2a_coordination.py | src/zephyr/shared/protocols/a2a/a2a_c... | prototype | generated |
| 125 | src/zephyr/shared/protocols/a2a/a2a_protocol.py | src/zephyr/shared/protocols/a2a/a2a_p... | prototype | generated |
| 126 | src/zephyr/shared/protocols/a2a/a2a_registry.py | src/zephyr/shared/protocols/a2a/a2a_r... | prototype | generated |
| 127 | src/zephyr/shared/protocols/a2a/a2a_schemas.py | src/zephyr/shared/protocols/a2a/a2a_s... | prototype | generated |
| 128 | src/zephyr/shared/protocols/a2a/layer3_coordination/__ini... | src/zephyr/shared/protocols/a2a/layer... | prototype | generated |
| 129 | src/zephyr/shared/reasoning_spans.py | src/zephyr/shared/reasoning_spans.py | production | generated |
| 130 | src/zephyr/shared/registry.py | src/zephyr/shared/registry.py | prototype | generated |
| 131 | src/zephyr/shared/reliability/diff_planner.py | src/zephyr/shared/reliability/diff_pl... | prototype | generated |
| 132 | src/zephyr/shared/reliability/retry_handler.py | src/zephyr/shared/reliability/retry_h... | prototype | generated |
| 133 | src/zephyr/shared/resilience/__init__.py | src/zephyr/shared/resilience/__init__.py | prototype | generated |
| 134 | src/zephyr/shared/resilience/circuit_breaker.py | src/zephyr/shared/resilience/circuit_... | prototype | generated |
| 135 | src/zephyr/shared/resilience/fallback.py | src/zephyr/shared/resilience/fallback.py | prototype | generated |
| 136 | src/zephyr/shared/resilience/retry.py | src/zephyr/shared/resilience/retry.py | prototype | generated |
| 137 | src/zephyr/shared/sandbox_executor.py | src/zephyr/shared/sandbox_executor.py | production | generated |
| 138 | src/zephyr/shared/schema/__init__.py | src/zephyr/shared/schema/__init__.py | prototype | generated |
| 139 | src/zephyr/shared/schema/base_config.py | src/zephyr/shared/schema/base_config.py | prototype | generated |
| 140 | src/zephyr/shared/schema/schema_registry.py | src/zephyr/shared/schema/schema_regis... | prototype | generated |
| 141 | src/zephyr/shared/schema/schemas.py | src/zephyr/shared/schema/schemas.py | prototype | generated |
| 142 | src/zephyr/shared/schema/severity_types.py | src/zephyr/shared/schema/severity_typ... | prototype | generated |
| 143 | src/zephyr/shared/schema_registry.py | src/zephyr/shared/schema_registry.py | prototype | generated |
| 144 | src/zephyr/shared/schemas.py | src/zephyr/shared/schemas.py | prototype | generated |
| 145 | src/zephyr/shared/secrets.py | src/zephyr/shared/secrets.py | prototype | generated |
| 146 | src/zephyr/shared/security/__init__.py | src/zephyr/shared/security/__init__.py | prototype | generated |
| 147 | src/zephyr/shared/security/capability.py | src/zephyr/shared/security/capability.py | prototype | generated |
| 148 | src/zephyr/shared/security/secrets.py | src/zephyr/shared/security/secrets.py | prototype | generated |
| 149 | src/zephyr/shared/security/ssot_guard.py | src/zephyr/shared/security/ssot_guard.py | prototype | generated |
| 150 | src/zephyr/shared/serialization.py | src/zephyr/shared/serialization.py | prototype | generated |
| 151 | src/zephyr/shared/session/session_boundary.py | src/zephyr/shared/session/session_bou... | prototype | generated |
| 152 | src/zephyr/shared/session_audit.py | src/zephyr/shared/session_audit.py | prototype | generated |
| 153 | src/zephyr/shared/session_continuity.py | src/zephyr/shared/session_continuity.py | prototype | generated |
| 154 | src/zephyr/shared/slo_review_assistant.py | src/zephyr/shared/slo_review_assistan... | production | generated |
| 155 | src/zephyr/shared/ssot_guard.py | src/zephyr/shared/ssot_guard.py | prototype | generated |
| 156 | src/zephyr/shared/state_machine.py | src/zephyr/shared/state_machine.py | prototype | generated |
| 157 | src/zephyr/shared/task_heartbeat.py | src/zephyr/shared/task_heartbeat.py | production | generated |
| 158 | src/zephyr/shared/task_types.py | src/zephyr/shared/task_types.py | prototype | generated |
| 159 | src/zephyr/shared/testing.py | src/zephyr/shared/testing.py | prototype | generated |
| 160 | src/zephyr/shared/time_utils.py | src/zephyr/shared/time_utils.py | prototype | generated |
| 161 | src/zephyr/shared/tracing.py | src/zephyr/shared/tracing.py | prototype | generated |
| 162 | src/zephyr/shared/ttl_cleanup_engine.py | src/zephyr/shared/ttl_cleanup_engine.py | production | generated |
| 163 | src/zephyr/shared/types.py | src/zephyr/shared/types.py | prototype | generated |
| 164 | src/zephyr/shared/utils/__init__.py | src/zephyr/shared/utils/__init__.py | prototype | generated |
| 165 | src/zephyr/shared/utils/context.py | src/zephyr/shared/utils/context.py | prototype | generated |
| 166 | src/zephyr/shared/utils/db_utils.py | src/zephyr/shared/utils/db_utils.py | prototype | generated |
| 167 | src/zephyr/shared/utils/diff_utils.py | src/zephyr/shared/utils/diff_utils.py | prototype | generated |
| 168 | src/zephyr/shared/utils/migration.py | src/zephyr/shared/utils/migration.py | prototype | generated |
| 169 | src/zephyr/shared/utils/pagination.py | src/zephyr/shared/utils/pagination.py | prototype | generated |
| 170 | src/zephyr/shared/utils/testing.py | src/zephyr/shared/utils/testing.py | prototype | generated |
| 171 | src/zephyr/shared/utils/time_utils.py | src/zephyr/shared/utils/time_utils.py | prototype | generated |
| 172 | src/zephyr/shared/vibe_experiment_tracker.py | src/zephyr/shared/vibe_experiment_tra... | production | generated |
| 173 | src/zephyr/shared/zephyr_logger.py | src/zephyr/shared/zephyr_logger.py | production | generated |

### 未分类 / Unclassified (15 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/shared/adaptation/__init__.py | src/zephyr/shared/adaptation/__init__.py | production | generated |
| 2 | src/zephyr/shared/compensation/__init__.py | src/zephyr/shared/compensation/__init... | production | generated |
| 3 | src/zephyr/shared/dependency/__init__.py | src/zephyr/shared/dependency/__init__.py | production | generated |
| 4 | src/zephyr/shared/draft/__init__.py | src/zephyr/shared/draft/__init__.py | production | generated |
| 5 | src/zephyr/shared/infra_06/__init__.py | src/zephyr/shared/infra_06/__init__.py | production | generated |
| 6 | src/zephyr/shared/knowledge/__init__.py | src/zephyr/shared/knowledge/__init__.py | production | generated |
| 7 | src/zephyr/shared/lifecycle/scope_guard.py | src/zephyr/shared/lifecycle/scope_gua... | production | generated |
| 8 | src/zephyr/shared/lifecycle/task_lifecycle_manager.py | src/zephyr/shared/lifecycle/task_life... | production | generated |
| 9 | src/zephyr/shared/maintenance/__init__.py | src/zephyr/shared/maintenance/__init_... | production | generated |
| 10 | src/zephyr/shared/observability_02/__init__.py | src/zephyr/shared/observability_02/__... | production | generated |
| 11 | src/zephyr/shared/queue/__init__.py | src/zephyr/shared/queue/__init__.py | production | generated |
| 12 | src/zephyr/shared/queue/task_scheduler.py | src/zephyr/shared/queue/task_schedule... | production | generated |
| 13 | src/zephyr/shared/reliability/__init__.py | src/zephyr/shared/reliability/__init_... | production | generated |
| 14 | src/zephyr/shared/reliability/context_guard.py | src/zephyr/shared/reliability/context... | production | generated |
| 15 | src/zephyr/shared/session/__init__.py | src/zephyr/shared/session/__init__.py | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 165 条 / 165 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 165 条 / 165 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 137 条 / edges                               │
│   [config_depends]: 28 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (137 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   api_index.py → api_index.py                                    │
│   blueprint_decomposer.py → __init__.py                          │
│   api_client.py → api_client.py                                  │
│   capability.py → capability.py                                  │
│   cache.py → cache.py                                            │
│   constants.py → constants.py                                    │
│   content_fingerprint.py → content_fingerprint.py                │
│   contract_bus.py → contract_violation_error.py                  │
│   errors.py → errors.py                                          │
│   diff_utils.py → diff_utils.py                                  │
│   event_bus.py → contract_bus.py                                 │
│   env.py → env.py                                                │
│   deprecation.py → deprecation.py                                │
│   flags.py → flags.py                                            │
│   frontmatter_utils.py → frontmatter_utils.py                    │
│   file_utils.py → file_utils.py                                  │
│   idempotency.py → idempotency.py                                │
│   limiter.py → limiter.py                                        │
│   lock.py → lock.py                                              │
│   migration.py → migration.py                                    │
│   observer.py → observer.py                                      │
│   outbox.py → outbox.py                                          │
│   pagination.py → pagination.py                                  │
│   ports.py → task_repository_protocol.py                         │
│   schema_registry.py → schema_registry.py                        │
│   schemas.py → schemas.py                                        │
│   serialization.py → serialization.py                            │
│   secrets.py → secrets.py                                        │
│   session_continuity.py → __init__.py                            │
│   ssot_guard.py → ssot_guard.py                                  │
│   state_machine.py → errors.py                                   │
│   testing.py → testing.py                                        │
│   time_utils.py → time_utils.py                                  │
│   types.py → types.py                                            │
│   dos_launcher.py → schemas.py                                   │
│   api_client.py → errors.py                                      │
│   api_client.py → serialization.py                               │
│   api_client.py → retry.py                                       │
│   api_client.py → circuit_breaker.py                             │
│   loader.py → errors.py                                          │
│   __init__.py → __init__.py                                      │
│   __init__.py → loader.py                                        │
│   __init__.py → skill_protocol.py                                │
│   __init__.py → orchestration_protocol.py                        │
│   __init__.py → task_repository_protocol.py                      │
│   __init__.py → llm_gateway_protocol.py                          │
│   __init__.py → __init__.py                                      │
│   __init__.py → enforcer.py                                      │
│   __init__.py → registry.py                                      │
│   ...还有 88 条 / 88 more edges                                  │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (28 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 165 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
