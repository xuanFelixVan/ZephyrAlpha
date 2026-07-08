---
doc_type: architecture_view
title: D_TRADING 交易运营架构文档
version: "1.0"
status: active
date: 2026-07-09
owner: auto-generator
ttl: permanent
---

# 50_d_trading / 交易运营 / 交易运营 / Trading Operations

> **功能简介 / Overview**: 交易运营与盘口管理

> **文档作用 / Purpose**: 展示 交易运营（D_TRADING）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-09 01:10:32
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 50 | Number | 50 |
| 域ID | D_TRADING | Domain ID | D_TRADING |
| 域名称 | 交易运营 | Domain Name | Trading Operations |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 464 | Module Count | 464 |
| 域内依赖 | 435 | Internal Dependencies | 435 |
| 跨域入边 | 735 | Cross-domain Incoming | 735 |
| 跨域出边 | 198 | Cross-domain Outgoing | 198 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 201 | Prototype Modules | 201 |
| 生产态模块 | 263 | Production Modules | 263 |
| 容量 | 280/150 (超容) | Capacity | 280/150 (超容) |
| 描述 | 交易会话、交易接口、交易日志、交易复盘。交易运营中枢。合规检查由D-GOV_ENFORCEMENT门禁层执行。 | Description | 交易会话、交易接口、交易日志、交易复盘。交易运营中枢。合规检查由D-GOV_ENFORCEMENT门禁层执行。 |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 16 页 / Page 1 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_main_py["(原型态 / prototype) __main__.py"]
        src_zephyr_trading_extensions_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_action_dispatcher_py["(生产态 / production) action_dispatcher.py"]
        src_zephyr_trading_admission_controller_py["(生产态 / production) admission_controller.py"]
        src_zephyr_trading_ai_audit_logger_py["(生产态 / production) ai_audit_logger.py"]
        src_zephyr_trading_api_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_auto_dispatcher_py["(原型态 / prototype) auto_dispatcher.py"]
        src_zephyr_trading_auto_integrator_py["(生产态 / production) auto_integrator.py"]
        src_zephyr_trading_auto_runtime_core_py["(生产态 / production) auto_runtime_core.py"]
        src_zephyr_trading_auto_task_generator_py["(生产态 / production) auto_task_generator.py"]
        src_zephyr_trading_boot_hooks_py["(生产态 / production) boot_hooks.py"]
        src_zephyr_trading_capability_card_py["(生产态 / production) capability_card.py"]
        src_zephyr_trading_capability_registry_py["(生产态 / production) capability_registry.py"]
        src_zephyr_trading_capability_sync_py["(生产态 / production) capability_sync.py"]
        src_zephyr_trading_core_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_dream_cycle_py["(生产态 / production) dream_cycle.py"]
        src_zephyr_trading_feedback_loop_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_feedback_loop_gen_inherited_py["(生产态 / production) _gen_inherited.py"]
        src_zephyr_trading_feedback_loop_actors_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_feedback_loop_actors_action_selector_py["(生产态 / production) action_selector.py"]
        src_zephyr_trading_feedback_loop_actors_agent_lifecycle_py["(生产态 / production) agent_lifecycle.py"]
        src_zephyr_trading_feedback_loop_actors_api_version_contract_py["(生产态 / production) api_version_contract.py"]
        src_zephyr_trading_feedback_loop_actors_global_action_scheduler_py["(生产态 / production) global_action_scheduler.py"]
        src_zephyr_trading_feedback_loop_actors_incident_priority_triage_automator_py["(生产态 / production) incident_priority_triage_automator.py"]
        src_zephyr_trading_feedback_loop_actors_intent_driven_ops_py["(生产态 / production) intent_driven_ops.py"]
        src_zephyr_trading_feedback_loop_actors_multi_agent_orchestrator_py["(生产态 / production) multi_agent_orchestrator.py"]
        src_zephyr_trading_feedback_loop_actors_notification_personalizer_py["(生产态 / production) notification_personalizer.py"]
        src_zephyr_trading_feedback_loop_actors_owner_absence_escalation_py["(生产态 / production) owner_absence_escalation.py"]
        src_zephyr_trading_feedback_loop_actors_saga_compensator_py["(原型态 / prototype) saga_compensator.py"]
    end
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_auto_integrator_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_boot_hooks_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_ai_audit_logger_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_sync_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_dream_cycle_py
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_init_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_capability_sync_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    src_zephyr_trading_capability_registry_py -->|导入依赖 / import_depends| src_zephyr_trading_capability_card_py
    src_zephyr_trading_main_py -.->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_api_version_contract_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_action_selector_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_incident_priority_triage_automator_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_global_action_scheduler_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_agent_lifecycle_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_owner_absence_escalation_py
    src_zephyr_trading_feedback_loop_actors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_saga_compensator_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_intent_driven_ops_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_notification_personalizer_py
    src_zephyr_trading_feedback_loop_actors_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_actors_multi_agent_orchestrator_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_action_dispatcher_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_action_dispatcher_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_auto_integrator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_auto_dispatcher_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_auto_runtime_core_py -.->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_auto_runtime_core_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_auto_runtime_core_py -.->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_auto_runtime_core_py -.->|导入依赖 / import_depends| D_INTEGRATION
    D_INTELLIGENCE["[原型态 / prototype] D_INTELLIGENCE"]
    src_zephyr_trading_auto_runtime_core_py -.->|导入依赖 / import_depends| D_INTELLIGENCE
    src_zephyr_trading_auto_runtime_core_py -.->|导入依赖 / import_depends| D_INTELLIGENCE
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_init_py
    D_SECURITY["[原型态 / prototype] D_SECURITY"]
    D_SECURITY -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_init_py
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_trading_capability_registry_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_auto_runtime_core_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_auto_task_generator_py
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_action_dispatcher_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_actors_action_selector_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_actors_agent_lifecycle_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_auto_runtime_core_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_boot_hooks_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_ai_audit_logger_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_auto_integrator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_capability_card_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_capability_registry_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_auto_runtime_core_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_init_py,src_zephyr_trading_action_dispatcher_py,src_zephyr_trading_admission_controller_py,src_zephyr_trading_ai_audit_logger_py,src_zephyr_trading_auto_integrator_py,src_zephyr_trading_auto_runtime_core_py,src_zephyr_trading_auto_task_generator_py,src_zephyr_trading_boot_hooks_py,src_zephyr_trading_capability_card_py,src_zephyr_trading_capability_registry_py,src_zephyr_trading_capability_sync_py,src_zephyr_trading_dream_cycle_py,src_zephyr_trading_feedback_loop_init_py,src_zephyr_trading_feedback_loop_gen_inherited_py,src_zephyr_trading_feedback_loop_actors_init_py,src_zephyr_trading_feedback_loop_actors_action_selector_py,src_zephyr_trading_feedback_loop_actors_agent_lifecycle_py,src_zephyr_trading_feedback_loop_actors_api_version_contract_py,src_zephyr_trading_feedback_loop_actors_global_action_scheduler_py,src_zephyr_trading_feedback_loop_actors_incident_priority_triage_automator_py,src_zephyr_trading_feedback_loop_actors_intent_driven_ops_py,src_zephyr_trading_feedback_loop_actors_multi_agent_orchestrator_py,src_zephyr_trading_feedback_loop_actors_notification_personalizer_py,src_zephyr_trading_feedback_loop_actors_owner_absence_escalation_py production
    class src_zephyr_trading_main_py,src_zephyr_trading_extensions_init_py,src_zephyr_trading_api_init_py,src_zephyr_trading_auto_dispatcher_py,src_zephyr_trading_core_init_py,src_zephyr_trading_feedback_loop_actors_saga_compensator_py design
    class D_SHARED,D_GOVERNANCE,D_INTEGRATION external_prod
    class D_INTELLIGENCE,D_SECURITY,D_AUDITTEST external_design
```

### 第 2 页 / 共 16 页 / Page 2 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_actors_secondary_alert_channel_py["(生产态 / production) secondary_alert_channel.py"]
        src_zephyr_trading_feedback_loop_alert_dispatcher_py["(原型态 / prototype) alert_dispatcher.py"]
        src_zephyr_trading_feedback_loop_auto_evolution_py["(生产态 / production) auto_evolution.py"]
        src_zephyr_trading_feedback_loop_backpressure_bridge_py["(生产态 / production) backpressure_bridge.py"]
        src_zephyr_trading_feedback_loop_collectors_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_collectors_calendar_adapter_py["(生产态 / production) calendar_adapter.py"]
        src_zephyr_trading_feedback_loop_collectors_config_timeline_py["(生产态 / production) config_timeline.py"]
        src_zephyr_trading_feedback_loop_collectors_data_quality_validator_py["(生产态 / production) data_quality_validator.py"]
        src_zephyr_trading_feedback_loop_collectors_feedback_collector_py["(原型态 / prototype) feedback_collector.py"]
        src_zephyr_trading_feedback_loop_collectors_financial_stratification_py["(生产态 / production) financial_stratification.py"]
        src_zephyr_trading_feedback_loop_collectors_kb_provenance_py["(生产态 / production) kb_provenance.py"]
        src_zephyr_trading_feedback_loop_collectors_knowledge_capture_py["(生产态 / production) knowledge_capture.py"]
        src_zephyr_trading_feedback_loop_collectors_knowledge_freshness_py["(生产态 / production) knowledge_freshness.py"]
        src_zephyr_trading_feedback_loop_collectors_knowledge_injection_py["(生产态 / production) knowledge_injection.py"]
        src_zephyr_trading_feedback_loop_collectors_knowledge_packaging_py["(生产态 / production) knowledge_packaging.py"]
        src_zephyr_trading_feedback_loop_collectors_known_unknown_registry_py["(生产态 / production) known_unknown_registry.py"]
        src_zephyr_trading_feedback_loop_collectors_llm_cost_accounting_py["(生产态 / production) llm_cost_accounting.py"]
        src_zephyr_trading_feedback_loop_collectors_market_calendar_py["(生产态 / production) market_calendar.py"]
        src_zephyr_trading_feedback_loop_collectors_market_event_integrator_py["(生产态 / production) market_event_integrator.py"]
        src_zephyr_trading_feedback_loop_collectors_metrics_collector_py["(原型态 / prototype) metrics_collector.py"]
        src_zephyr_trading_feedback_loop_collectors_notification_feedback_py["(生产态 / production) notification_feedback.py"]
        src_zephyr_trading_feedback_loop_collectors_schema_evolution_py["(生产态 / production) schema_evolution.py"]
        src_zephyr_trading_feedback_loop_collectors_schema_migration_py["(生产态 / production) schema_migration.py"]
        src_zephyr_trading_feedback_loop_collectors_temporal_event_store_py["(生产态 / production) temporal_event_store.py"]
        src_zephyr_trading_feedback_loop_collectors_token_finops_py["(生产态 / production) token_finops.py"]
        src_zephyr_trading_feedback_loop_config_py["(生产态 / production) config.py"]
        src_zephyr_trading_feedback_loop_core_py["(原型态 / prototype) core.py"]
        src_zephyr_trading_feedback_loop_db_bridge_py["(生产态 / production) db_bridge.py"]
        src_zephyr_trading_feedback_loop_db_writer_py["(原型态 / prototype) db_writer.py"]
        src_zephyr_trading_feedback_loop_decision_engine_py["(生产态 / production) decision_engine.py"]
    end
    src_zephyr_trading_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_alert_dispatcher_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_calendar_adapter_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_config_timeline_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_feedback_collector_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_kb_provenance_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_financial_stratification_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_knowledge_injection_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_knowledge_freshness_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_knowledge_capture_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_llm_cost_accounting_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_market_calendar_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_data_quality_validator_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_knowledge_packaging_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_known_unknown_registry_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_market_event_integrator_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_notification_feedback_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_schema_migration_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_temporal_event_store_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_metrics_collector_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_schema_evolution_py
    src_zephyr_trading_feedback_loop_collectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_collectors_token_finops_py
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_feedback_loop_alert_dispatcher_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    src_zephyr_trading_feedback_loop_backpressure_bridge_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_trading_feedback_loop_db_bridge_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_feedback_loop_core_py -.->|导入依赖 / import_depends| D_INTEGRATION
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_feedback_loop_core_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_feedback_loop_core_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_TELEMETRY["[原型态 / prototype] D_INFRA_TELEMETRY"]
    src_zephyr_trading_feedback_loop_db_writer_py -.->|导入依赖 / import_depends| D_INFRA_TELEMETRY
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_auto_evolution_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_db_bridge_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_decision_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_collectors_schema_evolution_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_backpressure_bridge_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_auto_evolution_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_collectors_calendar_adapter_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_config_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_collectors_config_timeline_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_db_bridge_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_collectors_data_quality_validator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_decision_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_collectors_financial_stratification_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_collectors_kb_provenance_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_backpressure_bridge_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_actors_secondary_alert_channel_py,src_zephyr_trading_feedback_loop_auto_evolution_py,src_zephyr_trading_feedback_loop_backpressure_bridge_py,src_zephyr_trading_feedback_loop_collectors_calendar_adapter_py,src_zephyr_trading_feedback_loop_collectors_config_timeline_py,src_zephyr_trading_feedback_loop_collectors_data_quality_validator_py,src_zephyr_trading_feedback_loop_collectors_financial_stratification_py,src_zephyr_trading_feedback_loop_collectors_kb_provenance_py,src_zephyr_trading_feedback_loop_collectors_knowledge_capture_py,src_zephyr_trading_feedback_loop_collectors_knowledge_freshness_py,src_zephyr_trading_feedback_loop_collectors_knowledge_injection_py,src_zephyr_trading_feedback_loop_collectors_knowledge_packaging_py,src_zephyr_trading_feedback_loop_collectors_known_unknown_registry_py,src_zephyr_trading_feedback_loop_collectors_llm_cost_accounting_py,src_zephyr_trading_feedback_loop_collectors_market_calendar_py,src_zephyr_trading_feedback_loop_collectors_market_event_integrator_py,src_zephyr_trading_feedback_loop_collectors_notification_feedback_py,src_zephyr_trading_feedback_loop_collectors_schema_evolution_py,src_zephyr_trading_feedback_loop_collectors_schema_migration_py,src_zephyr_trading_feedback_loop_collectors_temporal_event_store_py,src_zephyr_trading_feedback_loop_collectors_token_finops_py,src_zephyr_trading_feedback_loop_config_py,src_zephyr_trading_feedback_loop_db_bridge_py,src_zephyr_trading_feedback_loop_decision_engine_py production
    class src_zephyr_trading_feedback_loop_alert_dispatcher_py,src_zephyr_trading_feedback_loop_collectors_init_py,src_zephyr_trading_feedback_loop_collectors_feedback_collector_py,src_zephyr_trading_feedback_loop_collectors_metrics_collector_py,src_zephyr_trading_feedback_loop_core_py,src_zephyr_trading_feedback_loop_db_writer_py design
    class D_GOVERNANCE,D_INFRA_RUNTIME,D_INTEGRATION,D_SHARED external_prod
    class D_INFRA_TELEMETRY,D_AUDITTEST external_design
```

### 第 3 页 / 共 16 页 / Page 3 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_detectors_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_anomaly_clustering_py["(原型态 / prototype) anomaly_clustering.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_anomaly_detector_py["(原型态 / prototype) anomaly_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_emergent_behavior_detector_py["(原型态 / prototype) emergent_behavior_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_flapping_detector_py["(原型态 / prototype) flapping_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_heisenbug_detector_py["(原型态 / prototype) heisenbug_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_infinite_loop_detector_py["(原型态 / prototype) infinite_loop_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py["(原型态 / prototype) intermittent_failure_pattern.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_log_anomaly_py["(原型态 / prototype) log_anomaly.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_silent_corruption_detector_py["(原型态 / prototype) silent_corruption_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py["(原型态 / prototype) synthetic_anomaly_generator.py"]
        src_zephyr_trading_feedback_loop_detectors_anomaly_temporal_pattern_py["(原型态 / prototype) temporal_pattern.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py["(原型态 / prototype) action_efficacy_decay_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_action_interaction_detector_py["(原型态 / prototype) action_interaction_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py["(原型态 / prototype) action_side_effect_cumulative_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py["(原型态 / prototype) agent_trajectory_anomaly_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_cross_signal_validator_py["(原型态 / prototype) cross_signal_validator.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_cross_system_correlator_py["(原型态 / prototype) cross_system_correlator.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_decision_provenance_py["(原型态 / prototype) decision_provenance.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_dependency_freshness_monitor_py["(原型态 / prototype) dependency_freshness_monitor.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_ensemble_detector_py["(原型态 / prototype) ensemble_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_external_health_py["(原型态 / prototype) external_health.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_external_validation_checkpoint_py["(原型态 / prototype) external_validation_checkpoint.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_fle_performance_regression_detector_py["(原型态 / prototype) fle_performance_regression_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_multi_signal_correlator_py["(原型态 / prototype) multi_signal_correlator.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_rumor_noise_filter_py["(原型态 / prototype) rumor_noise_filter.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_trace_causal_bridge_py["(原型态 / prototype) trace_causal_bridge.py"]
        src_zephyr_trading_feedback_loop_detectors_correlation_traffic_replay_validator_py["(原型态 / prototype) traffic_replay_validator.py"]
    end
    src_zephyr_trading_feedback_loop_detectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_flapping_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_heisenbug_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_anomaly_clustering_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_emergent_behavior_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_log_anomaly_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_infinite_loop_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_temporal_pattern_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_anomaly_silent_corruption_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_anomaly_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_cross_system_correlator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_action_interaction_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_dependency_freshness_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_cross_signal_validator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_decision_provenance_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_ensemble_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_external_health_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_fle_performance_regression_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_trace_causal_bridge_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_external_validation_checkpoint_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_multi_signal_correlator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_rumor_noise_filter_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    src_zephyr_trading_feedback_loop_detectors_correlation_traffic_replay_validator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_correlation_init_py
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_detectors_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_detectors_init_py production
    class src_zephyr_trading_feedback_loop_detectors_anomaly_init_py,src_zephyr_trading_feedback_loop_detectors_anomaly_anomaly_clustering_py,src_zephyr_trading_feedback_loop_detectors_anomaly_anomaly_detector_py,src_zephyr_trading_feedback_loop_detectors_anomaly_emergent_behavior_detector_py,src_zephyr_trading_feedback_loop_detectors_anomaly_flapping_detector_py,src_zephyr_trading_feedback_loop_detectors_anomaly_heisenbug_detector_py,src_zephyr_trading_feedback_loop_detectors_anomaly_infinite_loop_detector_py,src_zephyr_trading_feedback_loop_detectors_anomaly_intermittent_failure_pattern_py,src_zephyr_trading_feedback_loop_detectors_anomaly_log_anomaly_py,src_zephyr_trading_feedback_loop_detectors_anomaly_silent_corruption_detector_py,src_zephyr_trading_feedback_loop_detectors_anomaly_synthetic_anomaly_generator_py,src_zephyr_trading_feedback_loop_detectors_anomaly_temporal_pattern_py,src_zephyr_trading_feedback_loop_detectors_correlation_init_py,src_zephyr_trading_feedback_loop_detectors_correlation_action_efficacy_decay_detector_py,src_zephyr_trading_feedback_loop_detectors_correlation_action_interaction_detector_py,src_zephyr_trading_feedback_loop_detectors_correlation_action_side_effect_cumulative_detector_py,src_zephyr_trading_feedback_loop_detectors_correlation_agent_trajectory_anomaly_detector_py,src_zephyr_trading_feedback_loop_detectors_correlation_cross_signal_validator_py,src_zephyr_trading_feedback_loop_detectors_correlation_cross_system_correlator_py,src_zephyr_trading_feedback_loop_detectors_correlation_decision_provenance_py,src_zephyr_trading_feedback_loop_detectors_correlation_dependency_freshness_monitor_py,src_zephyr_trading_feedback_loop_detectors_correlation_ensemble_detector_py,src_zephyr_trading_feedback_loop_detectors_correlation_external_health_py,src_zephyr_trading_feedback_loop_detectors_correlation_external_validation_checkpoint_py,src_zephyr_trading_feedback_loop_detectors_correlation_fle_performance_regression_detector_py,src_zephyr_trading_feedback_loop_detectors_correlation_multi_signal_correlator_py,src_zephyr_trading_feedback_loop_detectors_correlation_rumor_noise_filter_py,src_zephyr_trading_feedback_loop_detectors_correlation_trace_causal_bridge_py,src_zephyr_trading_feedback_loop_detectors_correlation_traffic_replay_validator_py design
    class D_AUDITTEST external_design
```

### 第 4 页 / 共 16 页 / Page 4 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_detectors_drift_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_concept_drift_py["(原型态 / prototype) concept_drift.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_config_drift_py["(原型态 / prototype) config_drift.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_context_window_contamination_detector_py["(原型态 / prototype) context_window_contamination_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_diminishing_returns_detector_py["(原型态 / prototype) diminishing_returns_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_ensemble_drift_py["(原型态 / prototype) ensemble_drift.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_gradual_poisoning_detector_py["(原型态 / prototype) gradual_poisoning_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_drift_trend_cycle_separator_py["(原型态 / prototype) trend_cycle_separator.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_alert_desensitization_curve_py["(原型态 / prototype) alert_desensitization_curve.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_guard_cascade_detector_py["(原型态 / prototype) guard_cascade_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_guard_oscillation_detector_py["(原型态 / prototype) guard_oscillation_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_placebo_action_detector_py["(原型态 / prototype) placebo_action_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_positive_feedback_defense_py["(原型态 / prototype) positive_feedback_defense.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py["(原型态 / prototype) recursive_diagnosis_trust_evaluator.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_self_audit_py["(原型态 / prototype) self_audit.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py["(原型态 / prototype) self_diagnosis_data_leak_detector.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_self_ha_py["(原型态 / prototype) self_ha.py"]
        src_zephyr_trading_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py["(原型态 / prototype) temporal_coherence_of_self_model.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_autoscale_remediation_py["(原型态 / prototype) autoscale_remediation.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_blast_radius_py["(原型态 / prototype) blast_radius.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_blast_radius_budget_py["(原型态 / prototype) blast_radius_budget.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_capacity_forecast_py["(原型态 / prototype) capacity_forecast.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_chaos_engineering_py["(原型态 / prototype) chaos_engineering.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_ebpf_monitor_py["(原型态 / prototype) ebpf_monitor.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_flag_lifecycle_py["(原型态 / prototype) flag_lifecycle.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_maintenance_coordinator_py["(原型态 / prototype) maintenance_coordinator.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_metric_cardinality_guard_py["(原型态 / prototype) metric_cardinality_guard.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_openfeature_py["(原型态 / prototype) openfeature.py"]
    end
    src_zephyr_trading_feedback_loop_detectors_drift_config_drift_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_drift_gradual_poisoning_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_drift_ensemble_drift_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_drift_diminishing_returns_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_drift_concept_drift_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_positive_feedback_defense_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_drift_trend_cycle_separator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_drift_context_window_contamination_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_drift_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_alert_desensitization_curve_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_guard_cascade_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_placebo_action_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_guard_oscillation_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_self_audit_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_self_ha_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_blast_radius_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_autoscale_remediation_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_guard_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_blast_radius_budget_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_chaos_engineering_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_capacity_forecast_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_maintenance_coordinator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_ebpf_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_flag_lifecycle_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_metric_cardinality_guard_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    src_zephyr_trading_feedback_loop_detectors_reliability_openfeature_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_detectors_reliability_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_detectors_drift_init_py,src_zephyr_trading_feedback_loop_detectors_drift_concept_drift_py,src_zephyr_trading_feedback_loop_detectors_drift_config_drift_py,src_zephyr_trading_feedback_loop_detectors_drift_context_window_contamination_detector_py,src_zephyr_trading_feedback_loop_detectors_drift_diminishing_returns_detector_py,src_zephyr_trading_feedback_loop_detectors_drift_ensemble_drift_py,src_zephyr_trading_feedback_loop_detectors_drift_gradual_poisoning_detector_py,src_zephyr_trading_feedback_loop_detectors_drift_trend_cycle_separator_py,src_zephyr_trading_feedback_loop_detectors_guard_init_py,src_zephyr_trading_feedback_loop_detectors_guard_alert_desensitization_curve_py,src_zephyr_trading_feedback_loop_detectors_guard_guard_cascade_detector_py,src_zephyr_trading_feedback_loop_detectors_guard_guard_oscillation_detector_py,src_zephyr_trading_feedback_loop_detectors_guard_placebo_action_detector_py,src_zephyr_trading_feedback_loop_detectors_guard_positive_feedback_defense_py,src_zephyr_trading_feedback_loop_detectors_guard_recursive_diagnosis_trust_evaluator_py,src_zephyr_trading_feedback_loop_detectors_guard_self_audit_py,src_zephyr_trading_feedback_loop_detectors_guard_self_diagnosis_data_leak_detector_py,src_zephyr_trading_feedback_loop_detectors_guard_self_ha_py,src_zephyr_trading_feedback_loop_detectors_guard_temporal_coherence_of_self_model_py,src_zephyr_trading_feedback_loop_detectors_reliability_init_py,src_zephyr_trading_feedback_loop_detectors_reliability_autoscale_remediation_py,src_zephyr_trading_feedback_loop_detectors_reliability_blast_radius_py,src_zephyr_trading_feedback_loop_detectors_reliability_blast_radius_budget_py,src_zephyr_trading_feedback_loop_detectors_reliability_capacity_forecast_py,src_zephyr_trading_feedback_loop_detectors_reliability_chaos_engineering_py,src_zephyr_trading_feedback_loop_detectors_reliability_ebpf_monitor_py,src_zephyr_trading_feedback_loop_detectors_reliability_flag_lifecycle_py,src_zephyr_trading_feedback_loop_detectors_reliability_maintenance_coordinator_py,src_zephyr_trading_feedback_loop_detectors_reliability_metric_cardinality_guard_py,src_zephyr_trading_feedback_loop_detectors_reliability_openfeature_py design
```

### 第 5 页 / 共 16 页 / Page 5 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_detectors_reliability_otel_adapter_py["(原型态 / prototype) otel_adapter.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_regulatory_audit_py["(原型态 / prototype) regulatory_audit.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_resolution_tracker_py["(原型态 / prototype) resolution_tracker.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_runbook_executor_py["(原型态 / prototype) runbook_executor.py"]
        src_zephyr_trading_feedback_loop_detectors_reliability_version_migrator_py["(原型态 / prototype) version_migrator.py"]
        src_zephyr_trading_feedback_loop_diagnosers_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py["(原型态 / prototype) adaptive_param_tuning.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_cognitive_load_py["(原型态 / prototype) cognitive_load.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py["(原型态 / prototype) cognitive_load_budget.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_collaborative_learning_py["(原型态 / prototype) collaborative_learning.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_confidence_decomposer_py["(原型态 / prototype) confidence_decomposer.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_gamification_py["(原型态 / prototype) gamification.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py["(原型态 / prototype) meta_guard_latency_budget.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_socratic_questions_py["(原型态 / prototype) socratic_questions.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_tone_adapter_py["(原型态 / prototype) tone_adapter.py"]
        src_zephyr_trading_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py["(原型态 / prototype) tone_adapter_v2.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py["(原型态 / prototype) auto_diagnosis.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py["(原型态 / prototype) causal_inference_engine.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_counterfactual_py["(原型态 / prototype) counterfactual.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py["(原型态 / prototype) diagnosis_engine.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py["(原型态 / prototype) diagnosis_kpi.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_impact_predictor_py["(原型态 / prototype) impact_predictor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py["(原型态 / prototype) incident_knowledge_injector.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py["(原型态 / prototype) interactive_diagnosis.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py["(原型态 / prototype) knowledge_bus_factor_monitor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_knowledge_market_py["(原型态 / prototype) knowledge_market.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_mtti_tracker_py["(原型态 / prototype) mtti_tracker.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py["(原型态 / prototype) nonstationary_effectiveness.py"]
    end
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_gamification_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_confidence_decomposer_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_cognitive_load_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_collaborative_learning_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_socratic_questions_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_tone_adapter_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_counterfactual_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_knowledge_market_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_impact_predictor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_mtti_tracker_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    src_zephyr_trading_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_diagnosers_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_diagnosers_init_py production
    class src_zephyr_trading_feedback_loop_detectors_reliability_otel_adapter_py,src_zephyr_trading_feedback_loop_detectors_reliability_regulatory_audit_py,src_zephyr_trading_feedback_loop_detectors_reliability_resolution_tracker_py,src_zephyr_trading_feedback_loop_detectors_reliability_runbook_executor_py,src_zephyr_trading_feedback_loop_detectors_reliability_version_migrator_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_init_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_adaptive_param_tuning_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_cognitive_load_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_cognitive_load_budget_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_collaborative_learning_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_confidence_decomposer_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_gamification_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_meta_guard_latency_budget_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_socratic_questions_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_tone_adapter_py,src_zephyr_trading_feedback_loop_diagnosers_cognitive_tone_adapter_v2_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_init_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_auto_diagnosis_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_causal_inference_engine_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_counterfactual_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_diagnosis_engine_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_diagnosis_kpi_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_impact_predictor_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_incident_knowledge_injector_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_interactive_diagnosis_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_knowledge_bus_factor_monitor_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_knowledge_market_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_mtti_tracker_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_nonstationary_effectiveness_py design
    class D_AUDITTEST external_design
```

### 第 6 页 / 共 16 页 / Page 6 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py["(原型态 / prototype) statistical_hygiene_auditor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py["(原型态 / prototype) vertical_self_assessment.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_action_composition_health_monitor_py["(原型态 / prototype) action_composition_health_monitor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_dr_resilience_metrics_py["(原型态 / prototype) dr_resilience_metrics.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_e2e_integration_health_py["(原型态 / prototype) e2e_integration_health.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_fle_dogfood_monitor_py["(原型态 / prototype) fle_dogfood_monitor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_fle_self_slo_metrics_py["(原型态 / prototype) fle_self_slo_metrics.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_global_health_map_py["(原型态 / prototype) global_health_map.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_memory_self_check_py["(原型态 / prototype) memory_self_check.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_model_health_py["(原型态 / prototype) model_health.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_self_benchmark_py["(原型态 / prototype) self_benchmark.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_self_bottleneck_detector_py["(原型态 / prototype) self_bottleneck_detector.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_self_health_monitor_py["(原型态 / prototype) self_health_monitor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_health_self_llm_observability_py["(原型态 / prototype) self_llm_observability.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_amplification_guard_py["(原型态 / prototype) amplification_guard.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_api_dependency_metrics_py["(原型态 / prototype) api_dependency_metrics.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_burn_rate_alerter_py["(原型态 / prototype) burn_rate_alerter.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_burnout_alarm_py["(原型态 / prototype) burnout_alarm.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_capacity_aware_repair_py["(原型态 / prototype) capacity_aware_repair.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py["(原型态 / prototype) cold_start_conservative_mode.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_context_truncation_py["(原型态 / prototype) context_truncation.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py["(原型态 / prototype) context_window_pressure_manager.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py["(原型态 / prototype) cross_guard_conflict_detector.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py["(原型态 / prototype) cross_session_consistency_validator.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py["(原型态 / prototype) data_volume_growth_monitor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py["(原型态 / prototype) feedback_delay_compensator.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py["(原型态 / prototype) guard_interaction_topology_mapper.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py["(原型态 / prototype) guard_self_consistency_auditor.py"]
    end
    src_zephyr_trading_feedback_loop_diagnosers_health_dr_resilience_metrics_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_e2e_integration_health_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_action_composition_health_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_fle_self_slo_metrics_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_fle_dogfood_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_global_health_map_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_model_health_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_self_benchmark_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_self_llm_observability_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_self_bottleneck_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_memory_self_check_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_health_self_health_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_health_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_api_dependency_metrics_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_burnout_alarm_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_burn_rate_alerter_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_capacity_aware_repair_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_amplification_guard_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_context_truncation_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    src_zephyr_trading_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py -.->|config_depends / config_depends| src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_diagnosers_diagnosis_statistical_hygiene_auditor_py,src_zephyr_trading_feedback_loop_diagnosers_diagnosis_vertical_self_assessment_py,src_zephyr_trading_feedback_loop_diagnosers_health_init_py,src_zephyr_trading_feedback_loop_diagnosers_health_action_composition_health_monitor_py,src_zephyr_trading_feedback_loop_diagnosers_health_dr_resilience_metrics_py,src_zephyr_trading_feedback_loop_diagnosers_health_e2e_integration_health_py,src_zephyr_trading_feedback_loop_diagnosers_health_fle_dogfood_monitor_py,src_zephyr_trading_feedback_loop_diagnosers_health_fle_self_slo_metrics_py,src_zephyr_trading_feedback_loop_diagnosers_health_global_health_map_py,src_zephyr_trading_feedback_loop_diagnosers_health_memory_self_check_py,src_zephyr_trading_feedback_loop_diagnosers_health_model_health_py,src_zephyr_trading_feedback_loop_diagnosers_health_self_benchmark_py,src_zephyr_trading_feedback_loop_diagnosers_health_self_bottleneck_detector_py,src_zephyr_trading_feedback_loop_diagnosers_health_self_health_monitor_py,src_zephyr_trading_feedback_loop_diagnosers_health_self_llm_observability_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_init_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_amplification_guard_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_api_dependency_metrics_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_burn_rate_alerter_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_burnout_alarm_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_capacity_aware_repair_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_cold_start_conservative_mode_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_context_truncation_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_context_window_pressure_manager_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_cross_guard_conflict_detector_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_cross_session_consistency_validator_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_data_volume_growth_monitor_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_feedback_delay_compensator_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_guard_interaction_topology_mapper_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_guard_self_consistency_auditor_py design
```

### 第 7 页 / 共 16 页 / Page 7 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py["(原型态 / prototype) human_anomaly_flood_detector.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_latency_slo_py["(原型态 / prototype) latency_slo.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_llm_provider_integrity_py["(原型态 / prototype) llm_provider_integrity.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_llm_quality_regression_py["(原型态 / prototype) llm_quality_regression.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_model_rotation_py["(原型态 / prototype) model_rotation.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_model_rotation_v2_py["(原型态 / prototype) model_rotation_v2.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py["(原型态 / prototype) model_version_semantic_drift.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_numerical_stability_guard_py["(原型态 / prototype) numerical_stability_guard.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_operational_seasonality_py["(原型态 / prototype) operational_seasonality.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_prompt_fingerprint_py["(原型态 / prototype) prompt_fingerprint.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_prompt_sanitizer_py["(原型态 / prototype) prompt_sanitizer.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_recovery_time_stats_py["(原型态 / prototype) recovery_time_stats.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py["(原型态 / prototype) regime_gain_scheduling.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_retirement_planner_py["(原型态 / prototype) retirement_planner.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py["(原型态 / prototype) slo_capacity_metrics.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_system_entropy_monitor_py["(原型态 / prototype) system_entropy_monitor.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py["(原型态 / prototype) temporal_integrity_guard.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py["(原型态 / prototype) timezone_semantic_reasoner.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_toil_quantification_py["(原型态 / prototype) toil_quantification.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_value_added_baseline_py["(原型态 / prototype) value_added_baseline.py"]
        src_zephyr_trading_feedback_loop_diagnosers_reliability_zombie_fle_detector_py["(原型态 / prototype) zombie_fle_detector.py"]
        src_zephyr_trading_feedback_loop_docs_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_feedback_loop_docs_cold_start_manual_py["(生产态 / production) cold_start_manual.py"]
        src_zephyr_trading_feedback_loop_error_budget_py["(生产态 / production) error_budget.py"]
        src_zephyr_trading_feedback_loop_eval_harness_py["(生产态 / production) eval_harness.py"]
        src_zephyr_trading_feedback_loop_evolution_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_evolution_auto_reward_py["(生产态 / production) auto_reward.py"]
        src_zephyr_trading_feedback_loop_evolution_conformal_prediction_py["(生产态 / production) conformal_prediction.py"]
        src_zephyr_trading_feedback_loop_evolution_cross_gen_validation_py["(生产态 / production) cross_gen_validation.py"]
        src_zephyr_trading_feedback_loop_evolution_dynamic_threshold_py["(生产态 / production) dynamic_threshold.py"]
    end
    src_zephyr_trading_feedback_loop_docs_init_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_docs_cold_start_manual_py
    src_zephyr_trading_feedback_loop_evolution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_evolution_auto_reward_py
    src_zephyr_trading_feedback_loop_evolution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_evolution_dynamic_threshold_py
    src_zephyr_trading_feedback_loop_evolution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_evolution_conformal_prediction_py
    src_zephyr_trading_feedback_loop_evolution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_evolution_cross_gen_validation_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_feedback_loop_diagnosers_reliability_operational_seasonality_py -.->|导入依赖 / import_depends| D_SHARED
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_auto_reward_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_error_budget_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_cross_gen_validation_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_eval_harness_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_error_budget_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_conformal_prediction_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_docs_init_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_docs_cold_start_manual_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_dynamic_threshold_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_eval_harness_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_auto_reward_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_conformal_prediction_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_dynamic_threshold_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_error_budget_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_docs_init_py,src_zephyr_trading_feedback_loop_docs_cold_start_manual_py,src_zephyr_trading_feedback_loop_error_budget_py,src_zephyr_trading_feedback_loop_eval_harness_py,src_zephyr_trading_feedback_loop_evolution_auto_reward_py,src_zephyr_trading_feedback_loop_evolution_conformal_prediction_py,src_zephyr_trading_feedback_loop_evolution_cross_gen_validation_py,src_zephyr_trading_feedback_loop_evolution_dynamic_threshold_py production
    class src_zephyr_trading_feedback_loop_diagnosers_reliability_human_anomaly_flood_detector_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_latency_slo_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_llm_provider_integrity_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_llm_quality_regression_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_model_rotation_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_model_rotation_v2_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_model_version_semantic_drift_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_numerical_stability_guard_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_operational_seasonality_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_prompt_fingerprint_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_prompt_sanitizer_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_recovery_time_stats_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_regime_gain_scheduling_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_retirement_planner_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_slo_capacity_metrics_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_system_entropy_monitor_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_temporal_integrity_guard_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_timezone_semantic_reasoner_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_toil_quantification_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_value_added_baseline_py,src_zephyr_trading_feedback_loop_diagnosers_reliability_zombie_fle_detector_py,src_zephyr_trading_feedback_loop_evolution_init_py design
    class D_SHARED external_prod
    class D_AUDITTEST external_design
```

### 第 8 页 / 共 16 页 / Page 8 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_evolution_ewc_kb_review_py["(生产态 / production) ewc_kb_review.py"]
        src_zephyr_trading_feedback_loop_evolution_failure_replay_py["(生产态 / production) failure_replay.py"]
        src_zephyr_trading_feedback_loop_evolution_graduated_activation_protocol_py["(生产态 / production) graduated_activation_protocol.py"]
        src_zephyr_trading_feedback_loop_evolution_hypernetwork_py["(生产态 / production) hypernetwork.py"]
        src_zephyr_trading_feedback_loop_evolution_knowledge_distillation_py["(生产态 / production) knowledge_distillation.py"]
        src_zephyr_trading_feedback_loop_evolution_online_feature_importance_py["(生产态 / production) online_feature_importance.py"]
        src_zephyr_trading_feedback_loop_evolution_prompt_factory_governance_py["(生产态 / production) prompt_factory_governance.py"]
        src_zephyr_trading_feedback_loop_evolution_prompt_optimization_regression_detector_py["(生产态 / production) prompt_optimization_regression_detector.py"]
        src_zephyr_trading_feedback_loop_evolution_prompt_self_optimization_loop_py["(生产态 / production) prompt_self_optimization_loop.py"]
        src_zephyr_trading_feedback_loop_evolution_self_modification_rate_limiter_py["(生产态 / production) self_modification_rate_limiter.py"]
        src_zephyr_trading_feedback_loop_evolution_self_reflection_py["(生产态 / production) self_reflection.py"]
        src_zephyr_trading_feedback_loop_evolution_self_upgrade_canary_py["(生产态 / production) self_upgrade_canary.py"]
        src_zephyr_trading_feedback_loop_evolution_semantic_intent_preservation_guard_py["(生产态 / production) semantic_intent_preservation_guard.py"]
        src_zephyr_trading_feedback_loop_evolution_teacher_transfer_py["(生产态 / production) teacher_transfer.py"]
        src_zephyr_trading_feedback_loop_evolution_training_data_gov_py["(生产态 / production) training_data_gov.py"]
        src_zephyr_trading_feedback_loop_evolution_engine_py["(生产态 / production) evolution_engine.py"]
        src_zephyr_trading_feedback_loop_exceptions_py["(生产态 / production) exceptions.py"]
        src_zephyr_trading_feedback_loop_feedback_collector_py["(生产态 / production) feedback_collector.py"]
        src_zephyr_trading_feedback_loop_fitness_functions_py["(生产态 / production) fitness_functions.py"]
        src_zephyr_trading_feedback_loop_forensic_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_forensic_architectural_sod_py["(生产态 / production) architectural_sod.py"]
        src_zephyr_trading_feedback_loop_forensic_automated_rca_postmortem_generator_py["(生产态 / production) automated_rca_postmortem_generator.py"]
        src_zephyr_trading_feedback_loop_forensic_boot_integrity_attestation_py["(生产态 / production) boot_integrity_attestation.py"]
        src_zephyr_trading_feedback_loop_forensic_crypto_bootstrap_py["(生产态 / production) crypto_bootstrap.py"]
        src_zephyr_trading_feedback_loop_forensic_deterministic_replay_py["(生产态 / production) deterministic_replay.py"]
        src_zephyr_trading_feedback_loop_forensic_external_verifier_py["(生产态 / production) external_verifier.py"]
        src_zephyr_trading_feedback_loop_forensic_fle_upgrade_safety_validator_py["(生产态 / production) fle_upgrade_safety_validator.py"]
        src_zephyr_trading_feedback_loop_forensic_guard_complexity_budget_py["(生产态 / production) guard_complexity_budget.py"]
        src_zephyr_trading_feedback_loop_forensic_guard_configuration_drift_monitor_py["(生产态 / production) guard_configuration_drift_monitor.py"]
        src_zephyr_trading_feedback_loop_forensic_interrupt_coherence_validator_py["(生产态 / production) interrupt_coherence_validator.py"]
    end
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_architectural_sod_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_automated_rca_postmortem_generator_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_deterministic_replay_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_crypto_bootstrap_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_boot_integrity_attestation_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_guard_complexity_budget_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_fle_upgrade_safety_validator_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_external_verifier_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_guard_configuration_drift_monitor_py
    src_zephyr_trading_feedback_loop_forensic_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_forensic_interrupt_coherence_validator_py
    D_SHARED["[原型态 / prototype] D_SHARED"]
    src_zephyr_trading_feedback_loop_evolution_engine_py -.->|导入依赖 / import_depends| D_SHARED
    D_SECURITY_LLM["[生产态 / production] D_SECURITY_LLM"]
    src_zephyr_trading_feedback_loop_evolution_engine_py -->|导入依赖 / import_depends| D_SECURITY_LLM
    src_zephyr_trading_feedback_loop_fitness_functions_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_feedback_loop_feedback_collector_py -->|导入依赖 / import_depends| D_SHARED
    D_FRONTEND["[生产态 / production] D_FRONTEND"]
    D_FRONTEND -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_fitness_functions_py
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_crypto_bootstrap_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_deterministic_replay_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_external_verifier_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_feedback_collector_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_exceptions_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_fitness_functions_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_evolution_self_modification_rate_limiter_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_feedback_collector_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_automated_rca_postmortem_generator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_architectural_sod_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_evolution_ewc_kb_review_py,src_zephyr_trading_feedback_loop_evolution_failure_replay_py,src_zephyr_trading_feedback_loop_evolution_graduated_activation_protocol_py,src_zephyr_trading_feedback_loop_evolution_hypernetwork_py,src_zephyr_trading_feedback_loop_evolution_knowledge_distillation_py,src_zephyr_trading_feedback_loop_evolution_online_feature_importance_py,src_zephyr_trading_feedback_loop_evolution_prompt_factory_governance_py,src_zephyr_trading_feedback_loop_evolution_prompt_optimization_regression_detector_py,src_zephyr_trading_feedback_loop_evolution_prompt_self_optimization_loop_py,src_zephyr_trading_feedback_loop_evolution_self_modification_rate_limiter_py,src_zephyr_trading_feedback_loop_evolution_self_reflection_py,src_zephyr_trading_feedback_loop_evolution_self_upgrade_canary_py,src_zephyr_trading_feedback_loop_evolution_semantic_intent_preservation_guard_py,src_zephyr_trading_feedback_loop_evolution_teacher_transfer_py,src_zephyr_trading_feedback_loop_evolution_training_data_gov_py,src_zephyr_trading_feedback_loop_evolution_engine_py,src_zephyr_trading_feedback_loop_exceptions_py,src_zephyr_trading_feedback_loop_feedback_collector_py,src_zephyr_trading_feedback_loop_fitness_functions_py,src_zephyr_trading_feedback_loop_forensic_architectural_sod_py,src_zephyr_trading_feedback_loop_forensic_automated_rca_postmortem_generator_py,src_zephyr_trading_feedback_loop_forensic_boot_integrity_attestation_py,src_zephyr_trading_feedback_loop_forensic_crypto_bootstrap_py,src_zephyr_trading_feedback_loop_forensic_deterministic_replay_py,src_zephyr_trading_feedback_loop_forensic_external_verifier_py,src_zephyr_trading_feedback_loop_forensic_fle_upgrade_safety_validator_py,src_zephyr_trading_feedback_loop_forensic_guard_complexity_budget_py,src_zephyr_trading_feedback_loop_forensic_guard_configuration_drift_monitor_py,src_zephyr_trading_feedback_loop_forensic_interrupt_coherence_validator_py production
    class src_zephyr_trading_feedback_loop_forensic_init_py design
    class D_SECURITY_LLM,D_INTEGRATION,D_FRONTEND external_prod
    class D_SHARED,D_AUDITTEST external_design
```

### 第 9 页 / 共 16 页 / Page 9 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py["(生产态 / production) knowledge_injection_pre_flight_verifier.py"]
        src_zephyr_trading_feedback_loop_forensic_point_in_time_reconstructor_py["(生产态 / production) point_in_time_reconstructor.py"]
        src_zephyr_trading_feedback_loop_forensic_self_modification_audit_py["(生产态 / production) self_modification_audit.py"]
        src_zephyr_trading_feedback_loop_forensic_serialization_format_tracker_py["(生产态 / production) serialization_format_tracker.py"]
        src_zephyr_trading_feedback_loop_forensic_state_migration_validator_py["(生产态 / production) state_migration_validator.py"]
        src_zephyr_trading_feedback_loop_forensic_sub_agent_collusion_py["(生产态 / production) sub_agent_collusion.py"]
        src_zephyr_trading_feedback_loop_forensic_toctou_guard_py["(原型态 / prototype) toctou_guard.py"]
        src_zephyr_trading_feedback_loop_forensic_worm_write_integrity_py["(生产态 / production) worm_write_integrity.py"]
        src_zephyr_trading_feedback_loop_gates_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_gates_governance_gates_py["(原型态 / prototype) _governance_gates.py"]
        src_zephyr_trading_feedback_loop_gates_operational_gates_py["(原型态 / prototype) _operational_gates.py"]
        src_zephyr_trading_feedback_loop_gates_safety_gates_py["(原型态 / prototype) _safety_gates.py"]
        src_zephyr_trading_feedback_loop_gates_security_gates_py["(原型态 / prototype) _security_gates.py"]
        src_zephyr_trading_feedback_loop_gates_action_reversibility_py["(生产态 / production) action_reversibility.py"]
        src_zephyr_trading_feedback_loop_gates_adversarial_validation_py["(原型态 / prototype) adversarial_validation.py"]
        src_zephyr_trading_feedback_loop_gates_autonomy_credit_py["(生产态 / production) autonomy_credit.py"]
        src_zephyr_trading_feedback_loop_gates_autonomy_maturity_py["(生产态 / production) autonomy_maturity.py"]
        src_zephyr_trading_feedback_loop_gates_blueprint_code_reconciler_py["(生产态 / production) blueprint_code_reconciler.py"]
        src_zephyr_trading_feedback_loop_gates_blueprint_validator_py["(生产态 / production) blueprint_validator.py"]
        src_zephyr_trading_feedback_loop_gates_checkpoint_manager_py["(生产态 / production) checkpoint_manager.py"]
        src_zephyr_trading_feedback_loop_gates_ci_cd_pre_scanner_py["(生产态 / production) ci_cd_pre_scanner.py"]
        src_zephyr_trading_feedback_loop_gates_concurrent_change_deconfliction_py["(生产态 / production) concurrent_change_deconfliction.py"]
        src_zephyr_trading_feedback_loop_gates_config_complexity_budget_py["(生产态 / production) config_complexity_budget.py"]
        src_zephyr_trading_feedback_loop_gates_config_governance_py["(生产态 / production) config_governance.py"]
        src_zephyr_trading_feedback_loop_gates_conflict_arbitration_py["(生产态 / production) conflict_arbitration.py"]
        src_zephyr_trading_feedback_loop_gates_cve_scanner_py["(生产态 / production) cve_scanner.py"]
        src_zephyr_trading_feedback_loop_gates_data_quality_gate_py["(生产态 / production) data_quality_gate.py"]
        src_zephyr_trading_feedback_loop_gates_db_integrity_py["(生产态 / production) db_integrity.py"]
        src_zephyr_trading_feedback_loop_gates_deployment_suppression_py["(生产态 / production) deployment_suppression.py"]
        src_zephyr_trading_feedback_loop_gates_dynamic_llm_cost_router_py["(生产态 / production) dynamic_llm_cost_router.py"]
    end
    src_zephyr_trading_feedback_loop_gates_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_gates_operational_gates_py
    src_zephyr_trading_feedback_loop_gates_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_gates_safety_gates_py
    src_zephyr_trading_feedback_loop_gates_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_gates_governance_gates_py
    src_zephyr_trading_feedback_loop_gates_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_gates_security_gates_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_feedback_loop_forensic_self_modification_audit_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["[原型态 / prototype] D_SECURITY"]
    src_zephyr_trading_feedback_loop_gates_adversarial_validation_py -.->|导入依赖 / import_depends| D_SECURITY
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_action_reversibility_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_point_in_time_reconstructor_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_serialization_format_tracker_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_forensic_sub_agent_collusion_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_autonomy_credit_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_autonomy_maturity_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_blueprint_code_reconciler_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_blueprint_validator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_config_complexity_budget_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_config_governance_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_data_quality_gate_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_db_integrity_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_action_reversibility_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_autonomy_credit_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_blueprint_code_reconciler_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_forensic_knowledge_injection_pre_flight_verifier_py,src_zephyr_trading_feedback_loop_forensic_point_in_time_reconstructor_py,src_zephyr_trading_feedback_loop_forensic_self_modification_audit_py,src_zephyr_trading_feedback_loop_forensic_serialization_format_tracker_py,src_zephyr_trading_feedback_loop_forensic_state_migration_validator_py,src_zephyr_trading_feedback_loop_forensic_sub_agent_collusion_py,src_zephyr_trading_feedback_loop_forensic_worm_write_integrity_py,src_zephyr_trading_feedback_loop_gates_action_reversibility_py,src_zephyr_trading_feedback_loop_gates_autonomy_credit_py,src_zephyr_trading_feedback_loop_gates_autonomy_maturity_py,src_zephyr_trading_feedback_loop_gates_blueprint_code_reconciler_py,src_zephyr_trading_feedback_loop_gates_blueprint_validator_py,src_zephyr_trading_feedback_loop_gates_checkpoint_manager_py,src_zephyr_trading_feedback_loop_gates_ci_cd_pre_scanner_py,src_zephyr_trading_feedback_loop_gates_concurrent_change_deconfliction_py,src_zephyr_trading_feedback_loop_gates_config_complexity_budget_py,src_zephyr_trading_feedback_loop_gates_config_governance_py,src_zephyr_trading_feedback_loop_gates_conflict_arbitration_py,src_zephyr_trading_feedback_loop_gates_cve_scanner_py,src_zephyr_trading_feedback_loop_gates_data_quality_gate_py,src_zephyr_trading_feedback_loop_gates_db_integrity_py,src_zephyr_trading_feedback_loop_gates_deployment_suppression_py,src_zephyr_trading_feedback_loop_gates_dynamic_llm_cost_router_py production
    class src_zephyr_trading_feedback_loop_forensic_toctou_guard_py,src_zephyr_trading_feedback_loop_gates_init_py,src_zephyr_trading_feedback_loop_gates_governance_gates_py,src_zephyr_trading_feedback_loop_gates_operational_gates_py,src_zephyr_trading_feedback_loop_gates_safety_gates_py,src_zephyr_trading_feedback_loop_gates_security_gates_py,src_zephyr_trading_feedback_loop_gates_adversarial_validation_py design
    class D_SHARED external_prod
    class D_SECURITY,D_AUDITTEST external_design
```

### 第 10 页 / 共 16 页 / Page 10 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_gates_emergency_takeover_py["(生产态 / production) emergency_takeover.py"]
        src_zephyr_trading_feedback_loop_gates_federated_security_py["(生产态 / production) federated_security.py"]
        src_zephyr_trading_feedback_loop_gates_flag_lifecycle_manager_py["(生产态 / production) flag_lifecycle_manager.py"]
        src_zephyr_trading_feedback_loop_gates_license_compliance_py["(生产态 / production) license_compliance.py"]
        src_zephyr_trading_feedback_loop_gates_llm_cost_router_py["(生产态 / production) llm_cost_router.py"]
        src_zephyr_trading_feedback_loop_gates_merkle_audit_root_py["(生产态 / production) merkle_audit_root.py"]
        src_zephyr_trading_feedback_loop_gates_meta_performance_gate_py["(生产态 / production) meta_performance_gate.py"]
        src_zephyr_trading_feedback_loop_gates_parameterized_safety_gate_py["(生产态 / production) parameterized_safety_gate.py"]
        src_zephyr_trading_feedback_loop_gates_safety_gate_l1_l27_py["(生产态 / production) safety_gate_l1_l27.py"]
        src_zephyr_trading_feedback_loop_gates_scope_creep_monitor_py["(生产态 / production) scope_creep_monitor.py"]
        src_zephyr_trading_feedback_loop_generator_py["(生产态 / production) generator.py"]
        src_zephyr_trading_feedback_loop_metrics_collector_py["(生产态 / production) metrics_collector.py"]
        src_zephyr_trading_feedback_loop_protocols_py["(生产态 / production) protocols.py"]
        src_zephyr_trading_feedback_loop_resilience_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_resilience_config_hot_reload_guard_py["(生产态 / production) config_hot_reload_guard.py"]
        src_zephyr_trading_feedback_loop_resilience_deadman_switch_py["(生产态 / production) deadman_switch.py"]
        src_zephyr_trading_feedback_loop_resilience_dr_automation_py["(生产态 / production) dr_automation.py"]
        src_zephyr_trading_feedback_loop_resilience_graceful_degradation_planner_py["(生产态 / production) graceful_degradation_planner.py"]
        src_zephyr_trading_feedback_loop_resilience_multi_instance_coord_py["(生产态 / production) multi_instance_coord.py"]
        src_zephyr_trading_feedback_loop_resilience_oscillation_damping_py["(生产态 / production) oscillation_damping.py"]
        src_zephyr_trading_feedback_loop_resilience_resource_starvation_aware_py["(生产态 / production) resource_starvation_aware.py"]
        src_zephyr_trading_feedback_loop_resilience_self_api_throttle_defense_py["(生产态 / production) self_api_throttle_defense.py"]
        src_zephyr_trading_feedback_loop_resilience_split_brain_quorum_py["(生产态 / production) split_brain_quorum.py"]
        src_zephyr_trading_feedback_loop_scheduler_py["(生产态 / production) scheduler.py"]
        src_zephyr_trading_feedback_loop_scheduler_act_py["(生产态 / production) scheduler_act.py"]
        src_zephyr_trading_feedback_loop_scheduler_collect_detect_py["(生产态 / production) scheduler_collect_detect.py"]
        src_zephyr_trading_feedback_loop_scheduler_health_py["(生产态 / production) scheduler_health.py"]
        src_zephyr_trading_feedback_loop_scheduler_safety_py["(生产态 / production) scheduler_safety.py"]
        src_zephyr_trading_feedback_loop_security_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_security_agent_skill_guard_py["(生产态 / production) agent_skill_guard.py"]
    end
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_scheduler_collect_detect_py
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_scheduler_act_py
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_scheduler_health_py
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_scheduler_safety_py
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_protocols_py
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_trading_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_trading_feedback_loop_scheduler_health_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_trading_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_gates_safety_gate_l1_l27_py
    src_zephyr_trading_feedback_loop_scheduler_safety_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_config_hot_reload_guard_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_dr_automation_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_deadman_switch_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_graceful_degradation_planner_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_resource_starvation_aware_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_oscillation_damping_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_multi_instance_coord_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_split_brain_quorum_py
    src_zephyr_trading_feedback_loop_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_resilience_self_api_throttle_defense_py
    src_zephyr_trading_feedback_loop_security_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_security_agent_skill_guard_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_feedback_loop_scheduler_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INFRA_TELEMETRY["[原型态 / prototype] D_INFRA_TELEMETRY"]
    src_zephyr_trading_feedback_loop_scheduler_py -.->|导入依赖 / import_depends| D_INFRA_TELEMETRY
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_feedback_loop_scheduler_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_feedback_loop_metrics_collector_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_feedback_loop_metrics_collector_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_INFRA_RECOVERY
    src_zephyr_trading_feedback_loop_scheduler_act_py -->|导入依赖 / import_depends| D_SHARED
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_security_agent_skill_guard_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_scheduler_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_resilience_config_hot_reload_guard_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_metrics_collector_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_protocols_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_emergency_takeover_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_federated_security_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_gates_flag_lifecycle_manager_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_generator_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_gates_emergency_takeover_py,src_zephyr_trading_feedback_loop_gates_federated_security_py,src_zephyr_trading_feedback_loop_gates_flag_lifecycle_manager_py,src_zephyr_trading_feedback_loop_gates_license_compliance_py,src_zephyr_trading_feedback_loop_gates_llm_cost_router_py,src_zephyr_trading_feedback_loop_gates_merkle_audit_root_py,src_zephyr_trading_feedback_loop_gates_meta_performance_gate_py,src_zephyr_trading_feedback_loop_gates_parameterized_safety_gate_py,src_zephyr_trading_feedback_loop_gates_safety_gate_l1_l27_py,src_zephyr_trading_feedback_loop_gates_scope_creep_monitor_py,src_zephyr_trading_feedback_loop_generator_py,src_zephyr_trading_feedback_loop_metrics_collector_py,src_zephyr_trading_feedback_loop_protocols_py,src_zephyr_trading_feedback_loop_resilience_config_hot_reload_guard_py,src_zephyr_trading_feedback_loop_resilience_deadman_switch_py,src_zephyr_trading_feedback_loop_resilience_dr_automation_py,src_zephyr_trading_feedback_loop_resilience_graceful_degradation_planner_py,src_zephyr_trading_feedback_loop_resilience_multi_instance_coord_py,src_zephyr_trading_feedback_loop_resilience_oscillation_damping_py,src_zephyr_trading_feedback_loop_resilience_resource_starvation_aware_py,src_zephyr_trading_feedback_loop_resilience_self_api_throttle_defense_py,src_zephyr_trading_feedback_loop_resilience_split_brain_quorum_py,src_zephyr_trading_feedback_loop_scheduler_py,src_zephyr_trading_feedback_loop_scheduler_act_py,src_zephyr_trading_feedback_loop_scheduler_collect_detect_py,src_zephyr_trading_feedback_loop_scheduler_health_py,src_zephyr_trading_feedback_loop_scheduler_safety_py,src_zephyr_trading_feedback_loop_security_agent_skill_guard_py production
    class src_zephyr_trading_feedback_loop_resilience_init_py,src_zephyr_trading_feedback_loop_security_init_py design
    class D_SHARED,D_GOVERNANCE,D_INFRA_RUNTIME,D_AUTONOMY_CORE,D_INTEGRATION,D_INFRA_RECOVERY external_prod
    class D_INFRA_TELEMETRY,D_AUDITTEST external_design
```

### 第 11 页 / 共 16 页 / Page 11 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_security_dep_cve_correlator_py["(生产态 / production) dep_cve_correlator.py"]
        src_zephyr_trading_feedback_loop_security_metric_prompt_scanner_py["(生产态 / production) metric_prompt_scanner.py"]
        src_zephyr_trading_feedback_loop_security_remote_attestation_py["(生产态 / production) remote_attestation.py"]
        src_zephyr_trading_feedback_loop_security_secret_rotation_py["(生产态 / production) secret_rotation.py"]
        src_zephyr_trading_feedback_loop_security_wireheading_prevention_py["(生产态 / production) wireheading_prevention.py"]
        src_zephyr_trading_feedback_loop_self_diagnosis_py["(生产态 / production) self_diagnosis.py"]
        src_zephyr_trading_feedback_loop_session_learner_py["(生产态 / production) session_learner.py"]
        src_zephyr_trading_feedback_loop_slo_manager_py["(生产态 / production) slo_manager.py"]
        src_zephyr_trading_feedback_loop_template_py["(生产态 / production) template.py"]
        src_zephyr_trading_feedback_loop_tests_e2e_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_tests_e2e_integration_test_pipeline_py["(生产态 / production) integration_test_pipeline.py"]
        src_zephyr_trading_feedback_loop_validator_py["(生产态 / production) validator.py"]
        src_zephyr_trading_feedback_loop_verifiers_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_feedback_loop_verifiers_ab_test_py["(生产态 / production) ab_test.py"]
        src_zephyr_trading_feedback_loop_verifiers_action_explainability_py["(生产态 / production) action_explainability.py"]
        src_zephyr_trading_feedback_loop_verifiers_ai_comment_veracity_py["(生产态 / production) ai_comment_veracity.py"]
        src_zephyr_trading_feedback_loop_verifiers_attack_simulator_py["(生产态 / production) attack_simulator.py"]
        src_zephyr_trading_feedback_loop_verifiers_auto_rollback_py["(生产态 / production) auto_rollback.py"]
        src_zephyr_trading_feedback_loop_verifiers_build_reproducibility_verifier_py["(生产态 / production) build_reproducibility_verifier.py"]
        src_zephyr_trading_feedback_loop_verifiers_canary_repair_py["(生产态 / production) canary_repair.py"]
        src_zephyr_trading_feedback_loop_verifiers_cascading_rollback_analyzer_py["(生产态 / production) cascading_rollback_analyzer.py"]
        src_zephyr_trading_feedback_loop_verifiers_cross_blueprint_contract_drift_py["(生产态 / production) cross_blueprint_contract_drift.py"]
        src_zephyr_trading_feedback_loop_verifiers_cross_module_integration_py["(生产态 / production) cross_module_integration.py"]
        src_zephyr_trading_feedback_loop_verifiers_cross_session_knowledge_integrity_py["(生产态 / production) cross_session_knowledge_integrity.py"]
        src_zephyr_trading_feedback_loop_verifiers_digital_twin_sandbox_py["(生产态 / production) digital_twin_sandbox.py"]
        src_zephyr_trading_feedback_loop_verifiers_dry_run_sandbox_py["(生产态 / production) dry_run_sandbox.py"]
        src_zephyr_trading_feedback_loop_verifiers_federated_protocol_py["(生产态 / production) federated_protocol.py"]
        src_zephyr_trading_feedback_loop_verifiers_golden_test_external_py["(生产态 / production) golden_test_external.py"]
        src_zephyr_trading_feedback_loop_verifiers_no_llm_degradation_py["(生产态 / production) no_llm_degradation.py"]
        src_zephyr_trading_feedback_loop_verifiers_pre_flight_simulator_py["(生产态 / production) pre_flight_simulator.py"]
    end
    src_zephyr_trading_feedback_loop_validator_py -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_template_py
    src_zephyr_trading_feedback_loop_tests_e2e_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_tests_e2e_integration_test_pipeline_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_ab_test_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_action_explainability_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_auto_rollback_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_ai_comment_veracity_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_build_reproducibility_verifier_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_attack_simulator_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_canary_repair_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_cascading_rollback_analyzer_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_digital_twin_sandbox_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_cross_session_knowledge_integrity_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_cross_module_integration_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_dry_run_sandbox_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_golden_test_external_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_cross_blueprint_contract_drift_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_no_llm_degradation_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_federated_protocol_py
    src_zephyr_trading_feedback_loop_verifiers_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_verifiers_pre_flight_simulator_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_feedback_loop_security_secret_rotation_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["[原型态 / prototype] D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -.->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_security_secret_rotation_py
    D_SHARED -->|导入依赖 / import_depends| src_zephyr_trading_feedback_loop_security_secret_rotation_py
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_action_explainability_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_ai_comment_veracity_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_ab_test_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_build_reproducibility_verifier_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_build_reproducibility_verifier_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_pre_flight_simulator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_auto_rollback_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_canary_repair_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_cross_blueprint_contract_drift_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_cross_module_integration_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_cross_session_knowledge_integrity_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_validator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_template_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_security_dep_cve_correlator_py,src_zephyr_trading_feedback_loop_security_metric_prompt_scanner_py,src_zephyr_trading_feedback_loop_security_remote_attestation_py,src_zephyr_trading_feedback_loop_security_secret_rotation_py,src_zephyr_trading_feedback_loop_security_wireheading_prevention_py,src_zephyr_trading_feedback_loop_self_diagnosis_py,src_zephyr_trading_feedback_loop_session_learner_py,src_zephyr_trading_feedback_loop_slo_manager_py,src_zephyr_trading_feedback_loop_template_py,src_zephyr_trading_feedback_loop_tests_e2e_integration_test_pipeline_py,src_zephyr_trading_feedback_loop_validator_py,src_zephyr_trading_feedback_loop_verifiers_ab_test_py,src_zephyr_trading_feedback_loop_verifiers_action_explainability_py,src_zephyr_trading_feedback_loop_verifiers_ai_comment_veracity_py,src_zephyr_trading_feedback_loop_verifiers_attack_simulator_py,src_zephyr_trading_feedback_loop_verifiers_auto_rollback_py,src_zephyr_trading_feedback_loop_verifiers_build_reproducibility_verifier_py,src_zephyr_trading_feedback_loop_verifiers_canary_repair_py,src_zephyr_trading_feedback_loop_verifiers_cascading_rollback_analyzer_py,src_zephyr_trading_feedback_loop_verifiers_cross_blueprint_contract_drift_py,src_zephyr_trading_feedback_loop_verifiers_cross_module_integration_py,src_zephyr_trading_feedback_loop_verifiers_cross_session_knowledge_integrity_py,src_zephyr_trading_feedback_loop_verifiers_digital_twin_sandbox_py,src_zephyr_trading_feedback_loop_verifiers_dry_run_sandbox_py,src_zephyr_trading_feedback_loop_verifiers_federated_protocol_py,src_zephyr_trading_feedback_loop_verifiers_golden_test_external_py,src_zephyr_trading_feedback_loop_verifiers_no_llm_degradation_py,src_zephyr_trading_feedback_loop_verifiers_pre_flight_simulator_py production
    class src_zephyr_trading_feedback_loop_tests_e2e_init_py,src_zephyr_trading_feedback_loop_verifiers_init_py design
    class D_SHARED external_prod
    class D_INFRA_RUNTIME,D_AUDITTEST external_design
```

### 第 12 页 / 共 16 页 / Page 12 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_feedback_loop_verifiers_preventive_repair_py["(生产态 / production) preventive_repair.py"]
        src_zephyr_trading_feedback_loop_verifiers_rollback_integrity_py["(生产态 / production) rollback_integrity.py"]
        src_zephyr_trading_feedback_loop_verifiers_sim2real_calibration_py["(生产态 / production) sim2real_calibration.py"]
        src_zephyr_trading_feedback_loop_verifiers_stochastic_diagnosis_verifier_py["(生产态 / production) stochastic_diagnosis_verifier.py"]
        src_zephyr_trading_feedback_loop_verifiers_toctou_revalidation_py["(生产态 / production) toctou_revalidation.py"]
        src_zephyr_trading_feedback_loop_verifiers_verification_engine_py["(生产态 / production) verification_engine.py"]
        src_zephyr_trading_finalizer_py["(生产态 / production) finalizer.py"]
        src_zephyr_trading_gpu_consensus_scheduler_py["(生产态 / production) gpu_consensus_scheduler.py"]
        src_zephyr_trading_gpu_monitor_py["(原型态 / prototype) gpu_monitor.py"]
        src_zephyr_trading_health_monitor_py["(生产态 / production) health_monitor.py"]
        src_zephyr_trading_ide_health_daemon_py["(生产态 / production) ide_health_daemon.py"]
        src_zephyr_trading_infrastructure_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_integration_registry_py["(生产态 / production) integration_registry.py"]
        src_zephyr_trading_lifecycle_manager_py["(生产态 / production) lifecycle_manager.py"]
        src_zephyr_trading_models_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_module_onboarding_scanner_py["(生产态 / production) module_onboarding_scanner.py"]
        src_zephyr_trading_night_shift_queue_py["(生产态 / production) night_shift_queue.py"]
        src_zephyr_trading_orchestrator_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_orchestrator_agent_health_monitor_py["(生产态 / production) agent_health_monitor.py"]
        src_zephyr_trading_orchestrator_agent_orchestrator_py["(生产态 / production) agent_orchestrator.py"]
        src_zephyr_trading_orchestrator_contracts_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_contracts_alert_handler_py["(原型态 / prototype) alert_handler.py"]
        src_zephyr_trading_orchestrator_contracts_construction_guide_py["(生产态 / production) construction_guide.py"]
        src_zephyr_trading_orchestrator_contracts_contract_registry_py["(生产态 / production) contract_registry.py"]
        src_zephyr_trading_orchestrator_contracts_contract_router_py["(生产态 / production) contract_router.py"]
        src_zephyr_trading_orchestrator_contracts_design_decisions_py["(生产态 / production) design_decisions.py"]
        src_zephyr_trading_orchestrator_contracts_finding_bridge_py["(生产态 / production) finding_bridge.py"]
        src_zephyr_trading_orchestrator_contracts_prompt_version_py["(生产态 / production) prompt_version.py"]
        src_zephyr_trading_orchestrator_core_init_py["(生产态 / production) __init__.py"]
        src_zephyr_trading_orchestrator_core_agent_orchestrator_py["(原型态 / prototype) agent_orchestrator.py"]
    end
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_finalizer_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_health_monitor_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_integration_registry_py
    src_zephyr_trading_lifecycle_manager_py -->|导入依赖 / import_depends| src_zephyr_trading_night_shift_queue_py
    src_zephyr_trading_orchestrator_agent_health_monitor_py -->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_agent_orchestrator_py
    src_zephyr_trading_orchestrator_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_contracts_alert_handler_py
    src_zephyr_trading_orchestrator_contracts_contract_router_py -->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_contracts_contract_registry_py
    src_zephyr_trading_orchestrator_contracts_init_py -.->|config_depends / config_depends| src_zephyr_trading_orchestrator_contracts_construction_guide_py
    D_OPS["[生产态 / production] D_OPS"]
    src_zephyr_trading_finalizer_py -->|导入依赖 / import_depends| D_OPS
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    src_zephyr_trading_finalizer_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_OPS
    src_zephyr_trading_health_monitor_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_ide_health_daemon_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_integration_registry_py -->|导入依赖 / import_depends| D_INTEGRATION
    D_SECURITY["[生产态 / production] D_SECURITY"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_trading_module_onboarding_scanner_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_ide_health_daemon_py
    D_GOV_SCRIPTS["[原型态 / prototype] D_GOV_SCRIPTS"]
    D_GOV_SCRIPTS -.->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_contracts_contract_registry_py
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_agent_health_monitor_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_agent_orchestrator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_agent_orchestrator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_preventive_repair_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_sim2real_calibration_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_toctou_revalidation_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_feedback_loop_verifiers_verification_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_module_onboarding_scanner_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_health_monitor_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_contracts_contract_registry_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_contracts_contract_router_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_contracts_contract_registry_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_feedback_loop_verifiers_preventive_repair_py,src_zephyr_trading_feedback_loop_verifiers_rollback_integrity_py,src_zephyr_trading_feedback_loop_verifiers_sim2real_calibration_py,src_zephyr_trading_feedback_loop_verifiers_stochastic_diagnosis_verifier_py,src_zephyr_trading_feedback_loop_verifiers_toctou_revalidation_py,src_zephyr_trading_feedback_loop_verifiers_verification_engine_py,src_zephyr_trading_finalizer_py,src_zephyr_trading_gpu_consensus_scheduler_py,src_zephyr_trading_health_monitor_py,src_zephyr_trading_ide_health_daemon_py,src_zephyr_trading_integration_registry_py,src_zephyr_trading_lifecycle_manager_py,src_zephyr_trading_module_onboarding_scanner_py,src_zephyr_trading_night_shift_queue_py,src_zephyr_trading_orchestrator_init_py,src_zephyr_trading_orchestrator_agent_health_monitor_py,src_zephyr_trading_orchestrator_agent_orchestrator_py,src_zephyr_trading_orchestrator_contracts_construction_guide_py,src_zephyr_trading_orchestrator_contracts_contract_registry_py,src_zephyr_trading_orchestrator_contracts_contract_router_py,src_zephyr_trading_orchestrator_contracts_design_decisions_py,src_zephyr_trading_orchestrator_contracts_finding_bridge_py,src_zephyr_trading_orchestrator_contracts_prompt_version_py,src_zephyr_trading_orchestrator_core_init_py production
    class src_zephyr_trading_gpu_monitor_py,src_zephyr_trading_infrastructure_init_py,src_zephyr_trading_models_init_py,src_zephyr_trading_orchestrator_contracts_init_py,src_zephyr_trading_orchestrator_contracts_alert_handler_py,src_zephyr_trading_orchestrator_core_agent_orchestrator_py design
    class D_OPS,D_INFRA_RUNTIME,D_SHARED,D_INTEGRATION,D_GOVERNANCE,D_SECURITY external_prod
    class D_GOV_SCRIPTS,D_AUDITTEST external_design
```

### 第 13 页 / 共 16 页 / Page 13 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_orchestrator_core_task_queue_py["(原型态 / prototype) task_queue.py"]
        src_zephyr_trading_orchestrator_deferred_queue_py["(生产态 / production) deferred_queue.py"]
        src_zephyr_trading_orchestrator_execution_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_execution_batch_orchestrator_py["(生产态 / production) batch_orchestrator.py"]
        src_zephyr_trading_orchestrator_execution_context_bridge_py["(原型态 / prototype) context_bridge.py"]
        src_zephyr_trading_orchestrator_execution_data_lifecycle_py["(生产态 / production) data_lifecycle.py"]
        src_zephyr_trading_orchestrator_execution_dispatch_table_py["(生产态 / production) dispatch_table.py"]
        src_zephyr_trading_orchestrator_execution_dlq_manager_py["(生产态 / production) dlq_manager.py"]
        src_zephyr_trading_orchestrator_execution_memory_writer_py["(原型态 / prototype) memory_writer.py"]
        src_zephyr_trading_orchestrator_execution_phase_executor_py["(生产态 / production) phase_executor.py"]
        src_zephyr_trading_orchestrator_execution_reconciliation_loop_py["(生产态 / production) reconciliation_loop.py"]
        src_zephyr_trading_orchestrator_execution_script_runner_py["(原型态 / prototype) script_runner.py"]
        src_zephyr_trading_orchestrator_execution_task_context_builder_py["(原型态 / prototype) task_context_builder.py"]
        src_zephyr_trading_orchestrator_execution_trigger_router_py["(生产态 / production) trigger_router.py"]
        src_zephyr_trading_orchestrator_execution_wave_generator_py["(生产态 / production) wave_generator.py"]
        src_zephyr_trading_orchestrator_failure_matcher_py["(生产态 / production) failure_matcher.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_bulkhead_manager_py["(生产态 / production) bulkhead_manager.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_canary_manager_py["(生产态 / production) canary_manager.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_chaos_engine_py["(生产态 / production) chaos_engine.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_chaos_hooks_py["(生产态 / production) chaos_hooks.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_degrade_cascade_py["(生产态 / production) degrade_cascade.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_disk_guard_py["(生产态 / production) disk_guard.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_fault_types_py["(生产态 / production) fault_types.py"]
        src_zephyr_trading_orchestrator_fault_tolerance_network_partition_py["(生产态 / production) network_partition.py"]
        src_zephyr_trading_orchestrator_file_task_mapper_py["(生产态 / production) file_task_mapper.py"]
        src_zephyr_trading_orchestrator_governance_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_governance_autonomy_guard_py["(生产态 / production) autonomy_guard.py"]
        src_zephyr_trading_orchestrator_governance_capacity_budget_py["(生产态 / production) capacity_budget.py"]
        src_zephyr_trading_orchestrator_governance_dependency_lock_py["(生产态 / production) dependency_lock.py"]
    end
    src_zephyr_trading_orchestrator_execution_context_bridge_py -.->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_execution_task_context_builder_py
    src_zephyr_trading_orchestrator_execution_init_py -.->|config_depends / config_depends| src_zephyr_trading_orchestrator_execution_batch_orchestrator_py
    src_zephyr_trading_orchestrator_fault_tolerance_chaos_hooks_py -->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_fault_tolerance_chaos_engine_py
    src_zephyr_trading_orchestrator_fault_tolerance_chaos_hooks_py -->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_fault_tolerance_fault_types_py
    src_zephyr_trading_orchestrator_fault_tolerance_init_py -.->|config_depends / config_depends| src_zephyr_trading_orchestrator_fault_tolerance_bulkhead_manager_py
    src_zephyr_trading_orchestrator_governance_init_py -.->|config_depends / config_depends| src_zephyr_trading_orchestrator_governance_capacity_budget_py
    D_SHARED["[原型态 / prototype] D_SHARED"]
    src_zephyr_trading_orchestrator_deferred_queue_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_deferred_queue_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_orchestrator_failure_matcher_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_orchestrator_file_task_mapper_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_file_task_mapper_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_file_task_mapper_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_core_task_queue_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_execution_batch_orchestrator_py -.->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["[原型态 / prototype] D_INTEGRATION"]
    src_zephyr_trading_orchestrator_execution_context_bridge_py -.->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_orchestrator_execution_memory_writer_py -.->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    src_zephyr_trading_orchestrator_execution_memory_writer_py -.->|导入依赖 / import_depends| D_AUTONOMY_CORE
    src_zephyr_trading_orchestrator_execution_memory_writer_py -.->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_orchestrator_execution_wave_generator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_execution_wave_generator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_execution_task_context_builder_py -.->|导入依赖 / import_depends| D_INTEGRATION
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_autonomy_guard_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_execution_dispatch_table_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_fault_tolerance_canary_manager_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_capacity_budget_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_fault_tolerance_chaos_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_fault_tolerance_chaos_hooks_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_fault_tolerance_chaos_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_fault_tolerance_chaos_engine_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_dependency_lock_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_file_task_mapper_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_deferred_queue_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_execution_data_lifecycle_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_failure_matcher_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_execution_wave_generator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_execution_trigger_router_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_orchestrator_deferred_queue_py,src_zephyr_trading_orchestrator_execution_batch_orchestrator_py,src_zephyr_trading_orchestrator_execution_data_lifecycle_py,src_zephyr_trading_orchestrator_execution_dispatch_table_py,src_zephyr_trading_orchestrator_execution_dlq_manager_py,src_zephyr_trading_orchestrator_execution_phase_executor_py,src_zephyr_trading_orchestrator_execution_reconciliation_loop_py,src_zephyr_trading_orchestrator_execution_trigger_router_py,src_zephyr_trading_orchestrator_execution_wave_generator_py,src_zephyr_trading_orchestrator_failure_matcher_py,src_zephyr_trading_orchestrator_fault_tolerance_bulkhead_manager_py,src_zephyr_trading_orchestrator_fault_tolerance_canary_manager_py,src_zephyr_trading_orchestrator_fault_tolerance_chaos_engine_py,src_zephyr_trading_orchestrator_fault_tolerance_chaos_hooks_py,src_zephyr_trading_orchestrator_fault_tolerance_degrade_cascade_py,src_zephyr_trading_orchestrator_fault_tolerance_disk_guard_py,src_zephyr_trading_orchestrator_fault_tolerance_fault_types_py,src_zephyr_trading_orchestrator_fault_tolerance_network_partition_py,src_zephyr_trading_orchestrator_file_task_mapper_py,src_zephyr_trading_orchestrator_governance_autonomy_guard_py,src_zephyr_trading_orchestrator_governance_capacity_budget_py,src_zephyr_trading_orchestrator_governance_dependency_lock_py production
    class src_zephyr_trading_orchestrator_core_task_queue_py,src_zephyr_trading_orchestrator_execution_init_py,src_zephyr_trading_orchestrator_execution_context_bridge_py,src_zephyr_trading_orchestrator_execution_memory_writer_py,src_zephyr_trading_orchestrator_execution_script_runner_py,src_zephyr_trading_orchestrator_execution_task_context_builder_py,src_zephyr_trading_orchestrator_fault_tolerance_init_py,src_zephyr_trading_orchestrator_governance_init_py design
    class D_GOVERNANCE,D_AUTONOMY_CORE external_prod
    class D_SHARED,D_INTEGRATION,D_AUDITTEST external_design
```

### 第 14 页 / 共 16 页 / Page 14 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_orchestrator_governance_feature_flag_py["(生产态 / production) feature_flag.py"]
        src_zephyr_trading_orchestrator_governance_model_registry_py["(生产态 / production) model_registry.py"]
        src_zephyr_trading_orchestrator_governance_path_index_py["(生产态 / production) path_index.py"]
        src_zephyr_trading_orchestrator_governance_risk_registry_py["(生产态 / production) risk_registry.py"]
        src_zephyr_trading_orchestrator_governance_schema_migration_py["(生产态 / production) schema_migration.py"]
        src_zephyr_trading_orchestrator_governance_version_manifest_py["(生产态 / production) version_manifest.py"]
        src_zephyr_trading_orchestrator_hallucination_detector_py["(生产态 / production) hallucination_detector.py"]
        src_zephyr_trading_orchestrator_lifecycle_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_lifecycle_housekeeping_py["(生产态 / production) housekeeping.py"]
        src_zephyr_trading_orchestrator_lifecycle_incident_postmortem_py["(生产态 / production) incident_postmortem.py"]
        src_zephyr_trading_orchestrator_lifecycle_rolling_upgrade_py["(生产态 / production) rolling_upgrade.py"]
        src_zephyr_trading_orchestrator_lifecycle_session_conflict_py["(生产态 / production) session_conflict.py"]
        src_zephyr_trading_orchestrator_lifecycle_session_manager_py["(生产态 / production) session_manager.py"]
        src_zephyr_trading_orchestrator_lifecycle_startup_sequencer_py["(生产态 / production) startup_sequencer.py"]
        src_zephyr_trading_orchestrator_lifecycle_state_propagation_py["(生产态 / production) state_propagation.py"]
        src_zephyr_trading_orchestrator_lifecycle_state_synchronizer_py["(生产态 / production) state_synchronizer.py"]
        src_zephyr_trading_orchestrator_lifecycle_system_transfer_py["(生产态 / production) system_transfer.py"]
        src_zephyr_trading_orchestrator_lifecycle_teardown_manager_py["(生产态 / production) teardown_manager.py"]
        src_zephyr_trading_orchestrator_quality_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_quality_agent_quality_py["(生产态 / production) agent_quality.py"]
        src_zephyr_trading_orchestrator_quality_benchmark_runner_py["(生产态 / production) benchmark_runner.py"]
        src_zephyr_trading_orchestrator_quality_blind_spot_closure_py["(生产态 / production) blind_spot_closure.py"]
        src_zephyr_trading_orchestrator_quality_blueprint_scorer_py["(生产态 / production) blueprint_scorer.py"]
        src_zephyr_trading_orchestrator_quality_ke_quality_py["(生产态 / production) ke_quality.py"]
        src_zephyr_trading_orchestrator_quality_knowledge_freshness_py["(生产态 / production) knowledge_freshness.py"]
        src_zephyr_trading_orchestrator_quality_lean_scanner_py["(生产态 / production) lean_scanner.py"]
        src_zephyr_trading_orchestrator_quality_stability_guard_py["(生产态 / production) stability_guard.py"]
        src_zephyr_trading_orchestrator_resilience_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_orchestrator_resilience_failure_matcher_py["(生产态 / production) failure_matcher.py"]
        src_zephyr_trading_orchestrator_rollback_manager_py["(生产态 / production) rollback_manager.py"]
    end
    src_zephyr_trading_orchestrator_lifecycle_init_py -.->|config_depends / config_depends| src_zephyr_trading_orchestrator_lifecycle_housekeeping_py
    src_zephyr_trading_orchestrator_quality_init_py -.->|config_depends / config_depends| src_zephyr_trading_orchestrator_quality_agent_quality_py
    src_zephyr_trading_orchestrator_resilience_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_orchestrator_resilience_failure_matcher_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_orchestrator_rollback_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_rollback_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_rollback_manager_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_orchestrator_hallucination_detector_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_orchestrator_hallucination_detector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_lifecycle_session_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_lifecycle_session_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_lifecycle_state_synchronizer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_lifecycle_state_synchronizer_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_orchestrator_lifecycle_state_synchronizer_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_orchestrator_resilience_failure_matcher_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_AUDITTEST["[原型态 / prototype] D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_quality_agent_quality_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_quality_blueprint_scorer_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_quality_ke_quality_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_quality_knowledge_freshness_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_rollback_manager_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_model_registry_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_hallucination_detector_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_path_index_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_risk_registry_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_lifecycle_session_conflict_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_lifecycle_session_manager_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_quality_blind_spot_closure_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_quality_benchmark_runner_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_governance_feature_flag_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_trading_orchestrator_lifecycle_housekeeping_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_orchestrator_governance_feature_flag_py,src_zephyr_trading_orchestrator_governance_model_registry_py,src_zephyr_trading_orchestrator_governance_path_index_py,src_zephyr_trading_orchestrator_governance_risk_registry_py,src_zephyr_trading_orchestrator_governance_schema_migration_py,src_zephyr_trading_orchestrator_governance_version_manifest_py,src_zephyr_trading_orchestrator_hallucination_detector_py,src_zephyr_trading_orchestrator_lifecycle_housekeeping_py,src_zephyr_trading_orchestrator_lifecycle_incident_postmortem_py,src_zephyr_trading_orchestrator_lifecycle_rolling_upgrade_py,src_zephyr_trading_orchestrator_lifecycle_session_conflict_py,src_zephyr_trading_orchestrator_lifecycle_session_manager_py,src_zephyr_trading_orchestrator_lifecycle_startup_sequencer_py,src_zephyr_trading_orchestrator_lifecycle_state_propagation_py,src_zephyr_trading_orchestrator_lifecycle_state_synchronizer_py,src_zephyr_trading_orchestrator_lifecycle_system_transfer_py,src_zephyr_trading_orchestrator_lifecycle_teardown_manager_py,src_zephyr_trading_orchestrator_quality_agent_quality_py,src_zephyr_trading_orchestrator_quality_benchmark_runner_py,src_zephyr_trading_orchestrator_quality_blind_spot_closure_py,src_zephyr_trading_orchestrator_quality_blueprint_scorer_py,src_zephyr_trading_orchestrator_quality_ke_quality_py,src_zephyr_trading_orchestrator_quality_knowledge_freshness_py,src_zephyr_trading_orchestrator_quality_lean_scanner_py,src_zephyr_trading_orchestrator_quality_stability_guard_py,src_zephyr_trading_orchestrator_resilience_failure_matcher_py,src_zephyr_trading_orchestrator_rollback_manager_py production
    class src_zephyr_trading_orchestrator_lifecycle_init_py,src_zephyr_trading_orchestrator_quality_init_py,src_zephyr_trading_orchestrator_resilience_init_py design
    class D_SHARED,D_INTEGRATION,D_GOVERNANCE external_prod
    class D_AUDITTEST external_design
```

### 第 15 页 / 共 16 页 / Page 15 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_orchestrator_task_queue_py["(生产态 / production) task_queue.py"]
        src_zephyr_trading_orphan_detector_py["(原型态 / prototype) orphan_detector.py"]
        src_zephyr_trading_ports_py["(原型态 / prototype) ports.py"]
        src_zephyr_trading_protection_index_py["(生产态 / production) protection_index.py"]
        src_zephyr_trading_resource_optimization_py["(生产态 / production) resource_optimization.py"]
        src_zephyr_trading_runtime_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_runtime_config_py["(生产态 / production) runtime_config.py"]
        src_zephyr_trading_services_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_speed_baseline_checker_py["(原型态 / prototype) speed_baseline_checker.py"]
        src_zephyr_trading_staging_area_py["(生产态 / production) staging_area.py"]
        src_zephyr_trading_status_dashboard_py["(生产态 / production) status_dashboard.py"]
        src_zephyr_trading_stop_gate_py["(生产态 / production) stop_gate.py"]
        src_zephyr_trading_task_gate_py["(生产态 / production) task_gate.py"]
        src_zephyr_trading_trading_contracts_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_trading_contracts_execution_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py["(生产态 / production) capital_allocation_result.py"]
        src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py["(原型态 / prototype) execution_rejection_error.py"]
        src_zephyr_trading_trading_contracts_execution_execution_report_py["(生产态 / production) execution_report.py"]
        src_zephyr_trading_trading_contracts_execution_fill_py["(生产态 / production) fill.py"]
        src_zephyr_trading_trading_contracts_execution_model_serving_request_py["(生产态 / production) model_serving_request.py"]
        src_zephyr_trading_trading_contracts_execution_order_py["(生产态 / production) order.py"]
        src_zephyr_trading_trading_contracts_execution_position_py["(生产态 / production) position.py"]
        src_zephyr_trading_trading_contracts_factories_py["(原型态 / prototype) factories.py"]
        src_zephyr_trading_trading_contracts_market_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_trading_contracts_market_factor_monitor_report_py["(原型态 / prototype) factor_monitor_report.py"]
        src_zephyr_trading_trading_contracts_market_factor_signal_py["(生产态 / production) factor_signal.py"]
        src_zephyr_trading_trading_contracts_market_instrument_py["(原型态 / prototype) instrument.py"]
        src_zephyr_trading_trading_contracts_market_macro_factor_signal_py["(原型态 / prototype) macro_factor_signal.py"]
        src_zephyr_trading_trading_contracts_market_market_data_py["(生产态 / production) market_data.py"]
        src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py["(原型态 / prototype) signal_degradation_warning.py"]
    end
    src_zephyr_trading_status_dashboard_py -.->|导入依赖 / import_depends| src_zephyr_trading_orphan_detector_py
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_factor_signal_py
    src_zephyr_trading_trading_contracts_factories_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_fill_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_execution_report_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_factor_signal_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_factor_monitor_report_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_instrument_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_macro_factor_signal_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_market_data_py
    src_zephyr_trading_trading_contracts_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_fill_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_execution_report_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_model_serving_request_py
    src_zephyr_trading_trading_contracts_execution_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    src_zephyr_trading_trading_contracts_market_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_factor_signal_py
    src_zephyr_trading_trading_contracts_market_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_factor_monitor_report_py
    src_zephyr_trading_trading_contracts_market_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_instrument_py
    src_zephyr_trading_trading_contracts_market_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_macro_factor_signal_py
    src_zephyr_trading_trading_contracts_market_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_market_data_py
    src_zephyr_trading_trading_contracts_market_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_resource_optimization_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_trading_speed_baseline_checker_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_runtime_config_py -->|导入依赖 / import_depends| D_SHARED
    D_EX_CORE["[生产态 / production] D_EX_CORE"]
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_fill_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_fill_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    D_EX_CORE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    D_EX_CORE -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    D_FRONTEND["[生产态 / production] D_FRONTEND"]
    D_FRONTEND -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_fill_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_fill_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_order_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_position_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_factories_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_orchestrator_task_queue_py,src_zephyr_trading_protection_index_py,src_zephyr_trading_resource_optimization_py,src_zephyr_trading_runtime_config_py,src_zephyr_trading_staging_area_py,src_zephyr_trading_status_dashboard_py,src_zephyr_trading_stop_gate_py,src_zephyr_trading_task_gate_py,src_zephyr_trading_trading_contracts_execution_capital_allocation_result_py,src_zephyr_trading_trading_contracts_execution_execution_report_py,src_zephyr_trading_trading_contracts_execution_fill_py,src_zephyr_trading_trading_contracts_execution_model_serving_request_py,src_zephyr_trading_trading_contracts_execution_order_py,src_zephyr_trading_trading_contracts_execution_position_py,src_zephyr_trading_trading_contracts_market_factor_signal_py,src_zephyr_trading_trading_contracts_market_market_data_py production
    class src_zephyr_trading_orphan_detector_py,src_zephyr_trading_ports_py,src_zephyr_trading_runtime_init_py,src_zephyr_trading_services_init_py,src_zephyr_trading_speed_baseline_checker_py,src_zephyr_trading_trading_contracts_init_py,src_zephyr_trading_trading_contracts_execution_init_py,src_zephyr_trading_trading_contracts_execution_execution_rejection_error_py,src_zephyr_trading_trading_contracts_factories_py,src_zephyr_trading_trading_contracts_market_init_py,src_zephyr_trading_trading_contracts_market_factor_monitor_report_py,src_zephyr_trading_trading_contracts_market_instrument_py,src_zephyr_trading_trading_contracts_market_macro_factor_signal_py,src_zephyr_trading_trading_contracts_market_signal_degradation_warning_py design
    class D_SHARED,D_INFRA_RUNTIME,D_GOVERNANCE,D_EX_CORE,D_FRONTEND external_prod
```

### 第 16 页 / 共 16 页 / Page 16 of 16

```mermaid
graph TD
    subgraph D_TRADING["D_TRADING 交易运营"]
        src_zephyr_trading_trading_contracts_market_synthesized_signal_py["(生产态 / production) synthesized_signal.py"]
        src_zephyr_trading_trading_contracts_portfolio_contracts_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_trading_contracts_risk_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_trading_trading_contracts_risk_compliance_rule_py["(原型态 / prototype) compliance_rule.py"]
        src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py["(生产态 / production) risk_dashboard_snapshot.py"]
        src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py["(生产态 / production) risk_limit_violation_error.py"]
        src_zephyr_trading_trading_contracts_risk_risk_limits_py["(原型态 / prototype) risk_limits.py"]
        src_zephyr_trading_trading_contracts_risk_risk_metrics_py["(生产态 / production) risk_metrics.py"]
        src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py["(生产态 / production) risk_validator_protocol.py"]
        src_zephyr_trading_verdict_engine_py["(生产态 / production) verdict_engine.py"]
        src_zephyr_trading_windows_service_py["(原型态 / prototype) windows_service.py"]
        src_zephyr_trading_work_dag_py["(生产态 / production) work_dag.py"]
        src_zephyr_trading_work_orchestrator_py["(生产态 / production) work_orchestrator.py"]
        src_zephyr_trading_zombie_scanner_py["(原型态 / prototype) zombie_scanner.py"]
    end
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| src_zephyr_trading_work_dag_py
    src_zephyr_trading_trading_contracts_risk_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limits_py
    src_zephyr_trading_trading_contracts_risk_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    src_zephyr_trading_trading_contracts_risk_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    src_zephyr_trading_trading_contracts_risk_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py
    src_zephyr_trading_trading_contracts_risk_init_py -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    src_zephyr_trading_verdict_engine_py -->|导入依赖 / import_depends| D_GOVERNANCE
    D_SHARED["[生产态 / production] D_SHARED"]
    src_zephyr_trading_zombie_scanner_py -.->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    src_zephyr_trading_work_dag_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_work_orchestrator_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_ENFORCEMENT["[原型态 / prototype] D_GOV_ENFORCEMENT"]
    src_zephyr_trading_trading_contracts_risk_init_py -.->|导入依赖 / import_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_synthesized_signal_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limits_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_market_synthesized_signal_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limits_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_compliance_rule_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_metrics_py
    D_RISK["[生产态 / production] D_RISK"]
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py
    D_RISK -->|导入依赖 / import_depends| src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_trading_trading_contracts_market_synthesized_signal_py,src_zephyr_trading_trading_contracts_risk_risk_dashboard_snapshot_py,src_zephyr_trading_trading_contracts_risk_risk_limit_violation_error_py,src_zephyr_trading_trading_contracts_risk_risk_metrics_py,src_zephyr_trading_trading_contracts_risk_risk_validator_protocol_py,src_zephyr_trading_verdict_engine_py,src_zephyr_trading_work_dag_py,src_zephyr_trading_work_orchestrator_py production
    class src_zephyr_trading_trading_contracts_portfolio_contracts_init_py,src_zephyr_trading_trading_contracts_risk_init_py,src_zephyr_trading_trading_contracts_risk_compliance_rule_py,src_zephyr_trading_trading_contracts_risk_risk_limits_py,src_zephyr_trading_windows_service_py,src_zephyr_trading_zombie_scanner_py design
    class D_GOVERNANCE,D_SHARED,D_INTEGRATION,D_RISK external_prod
    class D_GOV_ENFORCEMENT external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_SHARED | 95 | 导入依赖 / import_depends |
| D_GOVERNANCE | 26 | 导入依赖 / import_depends |
| D_INTEGRATION | 26 | 导入依赖 / import_depends |
| D_INFRA_RUNTIME | 18 | 导入依赖 / import_depends |
| D_SECURITY | 6 | 导入依赖 / import_depends |
| D_GOV_ENFORCEMENT | 5 | 导入依赖 / import_depends |
| D_INTELLIGENCE | 5 | 导入依赖 / import_depends |
| D_AUTONOMY_CORE | 4 | 导入依赖 / import_depends |
| D_SECURITY_LLM | 4 | 导入依赖 / import_depends |
| D_OPS | 3 | 导入依赖 / import_depends |
| D_INFRA_TELEMETRY | 3 | 导入依赖 / import_depends |
| D_INFRA_RECOVERY | 2 | 导入依赖 / import_depends |
| D_INFRA_A2A | 1 | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_AUDITTEST | 639 | 测试依赖 / test_depends |
| D_GOVERNANCE | 51 | 导入依赖 / import_depends |
| D_FUNDAMENTAL_SIGNAL | 14 | 导入依赖 / import_depends |
| D_REPORTING | 6 | 导入依赖 / import_depends |
| D_EX_CORE | 6 | 导入依赖 / import_depends |
| D_RISK | 3 | 导入依赖 / import_depends |
| D_SECURITY | 3 | 导入依赖 / import_depends |
| D_SIGQC | 2 | 导入依赖 / import_depends |
| D_FRONTEND | 2 | 导入依赖 / import_depends |
| D_GOV_SCRIPTS | 2 | 导入依赖 / import_depends |
| D_ML_TRAIN | 2 | 导入依赖 / import_depends |
| D_SHARED | 2 | 导入依赖 / import_depends |
| D_INTELLIGENCE | 1 | 导入依赖 / import_depends |
| D_INFRA_RUNTIME | 1 | 导入依赖 / import_depends |
| D_PF_CORE | 1 | 导入依赖 / import_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 交易运营（D_TRADING）的模块分布。共 464 个模块 / 464 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│     L2 领域层 / Domain Layer（共 464 个模块 / 464 modules）      │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py [生产态 / production]                              │
│   __main__.py [原型态 / prototype]                               │
│   __init__.py [原型态 / prototype]                               │
│   action_dispatcher.py [生产态 / production]                     │
│   admission_controller.py [生产态 / production]                  │
│   ai_audit_logger.py [生产态 / production]                       │
│   __init__.py [原型态 / prototype]                               │
│   auto_dispatcher.py [原型态 / prototype]                        │
│   auto_integrator.py [生产态 / production]                       │
│   auto_runtime_core.py [生产态 / production]                     │
│   auto_task_generator.py [生产态 / production]                   │
│   boot_hooks.py [生产态 / production]                            │
│   capability_card.py [生产态 / production]                       │
│   capability_registry.py [生产态 / production]                   │
│   capability_sync.py [生产态 / production]                       │
│   __init__.py [原型态 / prototype]                               │
│   dream_cycle.py [生产态 / production]                           │
│   __init__.py [生产态 / production]                              │
│   ...还有 446 个模块 / 446 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 464 个模块 / 464 modules）。

### L2 领域层 / Domain Layer (464 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 功能简介 / Description | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|---------|:---:|:---:|
| 1 | src/zephyr/trading/__init__.py | src/zephyr/trading/__init__.py |  | production | generated |
| 2 | src/zephyr/trading/__main__.py | src/zephyr/trading/__main__.py | python -m zephyr.trading — AutoRuntime Core 入口 | prototype | generated |
| 3 | src/zephyr/trading/_extensions/__init__.py | src/zephyr/trading/_extensions/__init... |  | prototype | generated |
| 4 | src/zephyr/trading/action_dispatcher.py | src/zephyr/trading/action_dispatcher.py | ActionDispatcher --- 大脑的"手" v2.0 (Phase 2) | production | generated |
| 5 | src/zephyr/trading/admission_controller.py | src/zephyr/trading/admission_controll... |  | production | generated |
| 6 | src/zephyr/trading/ai_audit_logger.py | src/zephyr/trading/ai_audit_logger.py | AiAuditLogger — AI 行为审计日志 | production | generated |
| 7 | src/zephyr/trading/api/__init__.py | src/zephyr/trading/api/__init__.py |  | prototype | generated |
| 8 | src/zephyr/trading/auto_dispatcher.py | src/zephyr/trading/auto_dispatcher.py | AutoDispatcher — 守护进程内的轻量 PipelineDispatcher | prototype | generated |
| 9 | src/zephyr/trading/auto_integrator.py | src/zephyr/trading/auto_integrator.py | AutoIntegrator — 自动接入器 | production | generated |
| 10 | src/zephyr/trading/auto_runtime_core.py | src/zephyr/trading/auto_runtime_core.py | AutoRuntimeCore — 三层运行时运营中心（系统大脑） | production | generated |
| 11 | src/zephyr/trading/auto_task_generator.py | src/zephyr/trading/auto_task_generato... | AutoTaskGenerator — 自动任务生成器 | production | generated |
| 12 | src/zephyr/trading/boot_hooks.py | src/zephyr/trading/boot_hooks.py |  | production | generated |
| 13 | src/zephyr/trading/capability_card.py | src/zephyr/trading/capability_card.py | CapabilityCard — 能力卡片数据模型 | production | generated |
| 14 | src/zephyr/trading/capability_registry.py | src/zephyr/trading/capability_registr... | CapabilityRegistry — 能力注册中心 | production | generated |
| 15 | src/zephyr/trading/capability_sync.py | src/zephyr/trading/capability_sync.py |  | production | generated |
| 16 | src/zephyr/trading/core/__init__.py | src/zephyr/trading/core/__init__.py |  | prototype | generated |
| 17 | src/zephyr/trading/dream_cycle.py | src/zephyr/trading/dream_cycle.py | DreamCycle — 知识固化引擎 | production | generated |
| 18 | src/zephyr/trading/feedback_loop/__init__.py | src/zephyr/trading/feedback_loop/__in... | Feedback Loop Engine — MOD-FEEDBACK_LOOP. | production | generated |
| 19 | src/zephyr/trading/feedback_loop/_gen_inherited.py | src/zephyr/trading/feedback_loop/_gen... |  | production | generated |
| 20 | src/zephyr/trading/feedback_loop/actors/__init__.py | src/zephyr/trading/feedback_loop/acto... | feedback-loop.actors — auto-generated package init. | production | generated |
| 21 | src/zephyr/trading/feedback_loop/actors/action_selector.py | src/zephyr/trading/feedback_loop/acto... |  | production | generated |
| 22 | src/zephyr/trading/feedback_loop/actors/agent_lifecycle.py | src/zephyr/trading/feedback_loop/acto... | Agent Lifecycle Manager — v0.12.0 R159c | production | generated |
| 23 | src/zephyr/trading/feedback_loop/actors/api_version_contr... | src/zephyr/trading/feedback_loop/acto... | API Version Contract — v0.14.0 R188 | production | generated |
| 24 | src/zephyr/trading/feedback_loop/actors/global_action_sch... | src/zephyr/trading/feedback_loop/acto... | Global Action Scheduler — v0.16.0 R226 | production | generated |
| 25 | src/zephyr/trading/feedback_loop/actors/incident_priority... | src/zephyr/trading/feedback_loop/acto... | Incident Priority Triage Automator — v0.37.0 R463 | production | generated |
| 26 | src/zephyr/trading/feedback_loop/actors/intent_driven_ops.py | src/zephyr/trading/feedback_loop/acto... | Intent-Driven Ops — v0.12.0 R159 | production | generated |
| 27 | src/zephyr/trading/feedback_loop/actors/multi_agent_orche... | src/zephyr/trading/feedback_loop/acto... | Multi-Agent Orchestrator — v0.12.0 R159b | production | generated |
| 28 | src/zephyr/trading/feedback_loop/actors/notification_pers... | src/zephyr/trading/feedback_loop/acto... | Notification Personalizer — v0.6.0 R67 | production | generated |
| 29 | src/zephyr/trading/feedback_loop/actors/owner_absence_esc... | src/zephyr/trading/feedback_loop/acto... | Owner Absence Escalation — v0.37.0 R462 | production | generated |
| 30 | src/zephyr/trading/feedback_loop/actors/saga_compensator.py | src/zephyr/trading/feedback_loop/acto... | Saga Compensator — v0.3.0 R19b | prototype | generated |
| 31 | src/zephyr/trading/feedback_loop/actors/secondary_alert_c... | src/zephyr/trading/feedback_loop/acto... | Secondary Alert Channel — v0.37.0 R461 | production | generated |
| 32 | src/zephyr/trading/feedback_loop/alert_dispatcher.py | src/zephyr/trading/feedback_loop/aler... | FLE->Orc 告警分派器 — dispatch() 生产者 | prototype | generated |
| 33 | src/zephyr/trading/feedback_loop/auto_evolution.py | src/zephyr/trading/feedback_loop/auto... |  | production | generated |
| 34 | src/zephyr/trading/feedback_loop/backpressure_bridge.py | src/zephyr/trading/feedback_loop/back... | FLE -> Pipeline 背压桥接（CTR-BP-001~003） | production | generated |
| 35 | src/zephyr/trading/feedback_loop/collectors/__init__.py | src/zephyr/trading/feedback_loop/coll... | feedback-loop.collectors — auto-generated package init. | prototype | generated |
| 36 | src/zephyr/trading/feedback_loop/collectors/calendar_adap... | src/zephyr/trading/feedback_loop/coll... | Calendar Adapter — v0.8.0 R102b | production | generated |
| 37 | src/zephyr/trading/feedback_loop/collectors/config_timeli... | src/zephyr/trading/feedback_loop/coll... | Config Timeline — v0.8.0 R99 | production | generated |
| 38 | src/zephyr/trading/feedback_loop/collectors/data_quality_... | src/zephyr/trading/feedback_loop/coll... | Data Quality Validator — v0.9.0 R110 | production | generated |
| 39 | src/zephyr/trading/feedback_loop/collectors/feedback_coll... | src/zephyr/trading/feedback_loop/coll... |  | prototype | generated |
| 40 | src/zephyr/trading/feedback_loop/collectors/financial_str... | src/zephyr/trading/feedback_loop/coll... | Financial Stratification — v0.5.0 R50 | production | generated |
| 41 | src/zephyr/trading/feedback_loop/collectors/kb_provenance.py | src/zephyr/trading/feedback_loop/coll... | KB Provenance — v0.10.0 R136 | production | generated |
| 42 | src/zephyr/trading/feedback_loop/collectors/knowledge_cap... | src/zephyr/trading/feedback_loop/coll... | Knowledge Capture — v0.4.0 R30 | production | generated |
| 43 | src/zephyr/trading/feedback_loop/collectors/knowledge_fre... | src/zephyr/trading/feedback_loop/coll... | Knowledge Freshness — v0.5.0 R47 | production | generated |
| 44 | src/zephyr/trading/feedback_loop/collectors/knowledge_inj... | src/zephyr/trading/feedback_loop/coll... | Knowledge Injection — v0.8.0 R102 | production | generated |
| 45 | src/zephyr/trading/feedback_loop/collectors/knowledge_pac... | src/zephyr/trading/feedback_loop/coll... | Knowledge Packaging — v0.9.0 R123 | production | generated |
| 46 | src/zephyr/trading/feedback_loop/collectors/known_unknown... | src/zephyr/trading/feedback_loop/coll... | Known-Unknown Registry — v0.16.0 R229 | production | generated |
| 47 | src/zephyr/trading/feedback_loop/collectors/llm_cost_acco... | src/zephyr/trading/feedback_loop/coll... | LLM Cost Accounting — v0.4.0 R35 | production | generated |
| 48 | src/zephyr/trading/feedback_loop/collectors/market_calend... | src/zephyr/trading/feedback_loop/coll... | Market Calendar — v0.5.0 R48 | production | generated |
| 49 | src/zephyr/trading/feedback_loop/collectors/market_event_... | src/zephyr/trading/feedback_loop/coll... | Market Event Integrator — v0.14.0 R197 | production | generated |
| 50 | src/zephyr/trading/feedback_loop/collectors/metrics_colle... | src/zephyr/trading/feedback_loop/coll... |  | prototype | generated |
| 51 | src/zephyr/trading/feedback_loop/collectors/notification_... | src/zephyr/trading/feedback_loop/coll... | Notification Feedback — v0.9.0 R118 | production | generated |
| 52 | src/zephyr/trading/feedback_loop/collectors/schema_evolut... | src/zephyr/trading/feedback_loop/coll... | Schema Evolution — v0.9.0 R111 | production | generated |
| 53 | src/zephyr/trading/feedback_loop/collectors/schema_migrat... | src/zephyr/trading/feedback_loop/coll... | Schema Migration — v0.14.0 R190 | production | generated |
| 54 | src/zephyr/trading/feedback_loop/collectors/temporal_even... | src/zephyr/trading/feedback_loop/coll... | Temporal Event Store — v0.3.0 R9 | production | generated |
| 55 | src/zephyr/trading/feedback_loop/collectors/token_finops.py | src/zephyr/trading/feedback_loop/coll... | Token FinOps — v0.12.0 R162 | production | generated |
| 56 | src/zephyr/trading/feedback_loop/config.py | src/zephyr/trading/feedback_loop/conf... |  | production | generated |
| 57 | src/zephyr/trading/feedback_loop/core.py | src/zephyr/trading/feedback_loop/core.py | FeedbackLoop core — 反馈闭环核心类。 | prototype | generated |
| 58 | src/zephyr/trading/feedback_loop/db_bridge.py | src/zephyr/trading/feedback_loop/db_b... | FLE DB契约适配器 — 通过规范zephyr.governance.sqlite_schema连接写入fle_metrics | production | generated |
| 59 | src/zephyr/trading/feedback_loop/db_writer.py | src/zephyr/trading/feedback_loop/db_w... | FLE 持久化写入器 — 写 metrics/alerts/dispatch_log 到 SQLite | prototype | generated |
| 60 | src/zephyr/trading/feedback_loop/decision_engine.py | src/zephyr/trading/feedback_loop/deci... | Feedback Loop Decision Engine | production | generated |
| 61 | src/zephyr/trading/feedback_loop/detectors/__init__.py | src/zephyr/trading/feedback_loop/dete... | feedback-loop.detectors — GOV-DOC-018: 60个叶子模块拆分为5个逻辑子包(anomaly... | production | generated |
| 62 | src/zephyr/trading/feedback_loop/detectors/anomaly/__init... | src/zephyr/trading/feedback_loop/dete... |  | prototype | generated |
| 63 | src/zephyr/trading/feedback_loop/detectors/anomaly/anomal... | src/zephyr/trading/feedback_loop/dete... | Anomaly Clustering — v0.9.0 R119 | prototype | generated |
| 64 | src/zephyr/trading/feedback_loop/detectors/anomaly/anomal... | src/zephyr/trading/feedback_loop/dete... |  | prototype | generated |
| 65 | src/zephyr/trading/feedback_loop/detectors/anomaly/emerge... | src/zephyr/trading/feedback_loop/dete... | Emergent Behavior Detector — v0.38.0 R473 | prototype | generated |
| 66 | src/zephyr/trading/feedback_loop/detectors/anomaly/flappi... | src/zephyr/trading/feedback_loop/dete... | Flapping Detector — v0.40.0 R494 | prototype | generated |
| 67 | src/zephyr/trading/feedback_loop/detectors/anomaly/heisen... | src/zephyr/trading/feedback_loop/dete... | Heisenbug Detector — v0.38.0 R470 | prototype | generated |
| 68 | src/zephyr/trading/feedback_loop/detectors/anomaly/infini... | src/zephyr/trading/feedback_loop/dete... | Infinite Loop Detector — v0.15.0 R219 | prototype | generated |
| 69 | src/zephyr/trading/feedback_loop/detectors/anomaly/interm... | src/zephyr/trading/feedback_loop/dete... | Intermittent Failure Pattern Detector — v0.40.0 R501 | prototype | generated |
| 70 | src/zephyr/trading/feedback_loop/detectors/anomaly/log_an... | src/zephyr/trading/feedback_loop/dete... | Log Anomaly Detector — v0.6.0 R61 | prototype | generated |
| 71 | src/zephyr/trading/feedback_loop/detectors/anomaly/silent... | src/zephyr/trading/feedback_loop/dete... | Silent Corruption Detector — v0.40.0 R499 | prototype | generated |
| 72 | src/zephyr/trading/feedback_loop/detectors/anomaly/synthe... | src/zephyr/trading/feedback_loop/dete... | Synthetic Anomaly Generator — v0.9.0 R112 | prototype | generated |
| 73 | src/zephyr/trading/feedback_loop/detectors/anomaly/tempor... | src/zephyr/trading/feedback_loop/dete... | Temporal Pattern Detector — v0.12.0 R164 | prototype | generated |
| 74 | src/zephyr/trading/feedback_loop/detectors/correlation/__... | src/zephyr/trading/feedback_loop/dete... |  | prototype | generated |
| 75 | src/zephyr/trading/feedback_loop/detectors/correlation/ac... | src/zephyr/trading/feedback_loop/dete... | R507: ActionEfficacyDecayDetector | prototype | generated |
| 76 | src/zephyr/trading/feedback_loop/detectors/correlation/ac... | src/zephyr/trading/feedback_loop/dete... | Action Interaction Detector — v0.38.0 R472 | prototype | generated |
| 77 | src/zephyr/trading/feedback_loop/detectors/correlation/ac... | src/zephyr/trading/feedback_loop/dete... | R526: ActionSideEffectCumulativeDetector | prototype | generated |
| 78 | src/zephyr/trading/feedback_loop/detectors/correlation/ag... | src/zephyr/trading/feedback_loop/dete... | R503: AgentTrajectoryAnomalyDetector | prototype | generated |
| 79 | src/zephyr/trading/feedback_loop/detectors/correlation/cr... | src/zephyr/trading/feedback_loop/dete... | Cross-Signal Validator — v0.6.0 R63 | prototype | generated |
| 80 | src/zephyr/trading/feedback_loop/detectors/correlation/cr... | src/zephyr/trading/feedback_loop/dete... | Cross-System Correlator — v0.13.0 R185 | prototype | generated |
| 81 | src/zephyr/trading/feedback_loop/detectors/correlation/de... | src/zephyr/trading/feedback_loop/dete... | Decision Provenance — v0.12.0 R166 | prototype | generated |
| 82 | src/zephyr/trading/feedback_loop/detectors/correlation/de... | src/zephyr/trading/feedback_loop/dete... | Dependency Freshness Monitor — v0.38.0 R474 | prototype | generated |
| 83 | src/zephyr/trading/feedback_loop/detectors/correlation/en... | src/zephyr/trading/feedback_loop/dete... | Ensemble Detector — v0.4.0 R21 | prototype | generated |
| 84 | src/zephyr/trading/feedback_loop/detectors/correlation/ex... | src/zephyr/trading/feedback_loop/dete... | External Health Monitor — v0.14.0 R193 | prototype | generated |
| 85 | src/zephyr/trading/feedback_loop/detectors/correlation/ex... | src/zephyr/trading/feedback_loop/dete... | R524: ExternalValidationCheckpoint | prototype | generated |
| 86 | src/zephyr/trading/feedback_loop/detectors/correlation/fl... | src/zephyr/trading/feedback_loop/dete... | R532: FLEPerformanceRegressionDetector | prototype | generated |
| 87 | src/zephyr/trading/feedback_loop/detectors/correlation/mu... | src/zephyr/trading/feedback_loop/dete... | Multi-Signal Correlator — v0.4.0 R22 | prototype | generated |
| 88 | src/zephyr/trading/feedback_loop/detectors/correlation/ru... | src/zephyr/trading/feedback_loop/dete... | Rumor Noise Filter — v0.37.0 R460 | prototype | generated |
| 89 | src/zephyr/trading/feedback_loop/detectors/correlation/tr... | src/zephyr/trading/feedback_loop/dete... | Trace Causal Bridge — v0.6.0 R62 | prototype | generated |
| 90 | src/zephyr/trading/feedback_loop/detectors/correlation/tr... | src/zephyr/trading/feedback_loop/dete... | Traffic Replay Validator — v0.14.0 R202 | prototype | generated |
| 91 | src/zephyr/trading/feedback_loop/detectors/drift/__init__.py | src/zephyr/trading/feedback_loop/dete... |  | prototype | generated |
| 92 | src/zephyr/trading/feedback_loop/detectors/drift/concept_... | src/zephyr/trading/feedback_loop/dete... | Concept Drift Detector — v0.5.0 R42 | prototype | generated |
| 93 | src/zephyr/trading/feedback_loop/detectors/drift/config_d... | src/zephyr/trading/feedback_loop/dete... | Config Drift Detector — v0.13.0 R182 | prototype | generated |
| 94 | src/zephyr/trading/feedback_loop/detectors/drift/context_... | src/zephyr/trading/feedback_loop/dete... | Context Window Contamination Detector — v0.38.0 R471 | prototype | generated |
| 95 | src/zephyr/trading/feedback_loop/detectors/drift/diminish... | src/zephyr/trading/feedback_loop/dete... | R528: DiminishingReturnsDetector | prototype | generated |
| 96 | src/zephyr/trading/feedback_loop/detectors/drift/ensemble... | src/zephyr/trading/feedback_loop/dete... | Ensemble Drift — v0.5.0 R43 | prototype | generated |
| 97 | src/zephyr/trading/feedback_loop/detectors/drift/gradual_... | src/zephyr/trading/feedback_loop/dete... | Gradual Poisoning Detector — v0.15.0 R210 | prototype | generated |
| 98 | src/zephyr/trading/feedback_loop/detectors/drift/trend_cy... | src/zephyr/trading/feedback_loop/dete... | Trend-Cycle Separator — v0.9.0 R113 | prototype | generated |
| 99 | src/zephyr/trading/feedback_loop/detectors/guard/__init__.py | src/zephyr/trading/feedback_loop/dete... |  | prototype | generated |
| 100 | src/zephyr/trading/feedback_loop/detectors/guard/alert_de... | src/zephyr/trading/feedback_loop/dete... | Alert Desensitization Curve — v0.37.0 R492 | prototype | generated |
| 101 | src/zephyr/trading/feedback_loop/detectors/guard/guard_ca... | src/zephyr/trading/feedback_loop/dete... | R520: GuardCascadeDetector | prototype | generated |
| 102 | src/zephyr/trading/feedback_loop/detectors/guard/guard_os... | src/zephyr/trading/feedback_loop/dete... | R519: GuardOscillationDetector | prototype | generated |
| 103 | src/zephyr/trading/feedback_loop/detectors/guard/placebo_... | src/zephyr/trading/feedback_loop/dete... | R508: PlaceboActionDetector | prototype | generated |
| 104 | src/zephyr/trading/feedback_loop/detectors/guard/positive... | src/zephyr/trading/feedback_loop/dete... | Positive Feedback Defense — v0.4.0 R28 | prototype | generated |
| 105 | src/zephyr/trading/feedback_loop/detectors/guard/recursiv... | src/zephyr/trading/feedback_loop/dete... | R517: RecursiveDiagnosisTrustEvaluator | prototype | generated |
| 106 | src/zephyr/trading/feedback_loop/detectors/guard/self_aud... | src/zephyr/trading/feedback_loop/dete... | Self Audit — v0.13.0 R183 | prototype | generated |
| 107 | src/zephyr/trading/feedback_loop/detectors/guard/self_dia... | src/zephyr/trading/feedback_loop/dete... | R530: SelfDiagnosisDataLeakDetector | prototype | generated |
| 108 | src/zephyr/trading/feedback_loop/detectors/guard/self_ha.py | src/zephyr/trading/feedback_loop/dete... | Self HA — v0.13.0 R173 | prototype | generated |
| 109 | src/zephyr/trading/feedback_loop/detectors/guard/temporal... | src/zephyr/trading/feedback_loop/dete... | R525: TemporalCoherenceOfSelfModel | prototype | generated |
| 110 | src/zephyr/trading/feedback_loop/detectors/reliability/__... | src/zephyr/trading/feedback_loop/dete... |  | prototype | generated |
| 111 | src/zephyr/trading/feedback_loop/detectors/reliability/au... | src/zephyr/trading/feedback_loop/dete... | Autoscale Remediation — v0.13.0 R174 | prototype | generated |
| 112 | src/zephyr/trading/feedback_loop/detectors/reliability/bl... | src/zephyr/trading/feedback_loop/dete... | Blast Radius Detector — v0.12.0 R167 | prototype | generated |
| 113 | src/zephyr/trading/feedback_loop/detectors/reliability/bl... | src/zephyr/trading/feedback_loop/dete... | Blast Radius Budget — v0.13.0 R178 | prototype | generated |
| 114 | src/zephyr/trading/feedback_loop/detectors/reliability/ca... | src/zephyr/trading/feedback_loop/dete... | Capacity Forecast — v0.13.0 R186b | prototype | generated |
| 115 | src/zephyr/trading/feedback_loop/detectors/reliability/ch... | src/zephyr/trading/feedback_loop/dete... | Chaos Engineering — v0.13.0 R172 | prototype | generated |
| 116 | src/zephyr/trading/feedback_loop/detectors/reliability/eb... | src/zephyr/trading/feedback_loop/dete... | eBPF Monitor — v0.6.0 R64 | prototype | generated |
| 117 | src/zephyr/trading/feedback_loop/detectors/reliability/fl... | src/zephyr/trading/feedback_loop/dete... | Flag Lifecycle Detector — v0.13.0 R180 | prototype | generated |
| 118 | src/zephyr/trading/feedback_loop/detectors/reliability/ma... | src/zephyr/trading/feedback_loop/dete... | Maintenance Coordinator — v0.12.0 R168 | prototype | generated |
| 119 | src/zephyr/trading/feedback_loop/detectors/reliability/me... | src/zephyr/trading/feedback_loop/dete... | Metric Cardinality Guard — v0.40.0 R495 | prototype | generated |
| 120 | src/zephyr/trading/feedback_loop/detectors/reliability/op... | src/zephyr/trading/feedback_loop/dete... | OpenFeature Integration — v0.13.0 R181 | prototype | generated |
| 121 | src/zephyr/trading/feedback_loop/detectors/reliability/ot... | src/zephyr/trading/feedback_loop/dete... | OTel Adapter — v0.12.0 R170 | prototype | generated |
| 122 | src/zephyr/trading/feedback_loop/detectors/reliability/re... | src/zephyr/trading/feedback_loop/dete... | Regulatory Audit Detector — v0.13.0 R184 | prototype | generated |
| 123 | src/zephyr/trading/feedback_loop/detectors/reliability/re... | src/zephyr/trading/feedback_loop/dete... | Resolution Tracker — v0.12.0 R165 | prototype | generated |
| 124 | src/zephyr/trading/feedback_loop/detectors/reliability/ru... | src/zephyr/trading/feedback_loop/dete... | Runbook Executor — v0.13.0 R186a | prototype | generated |
| 125 | src/zephyr/trading/feedback_loop/detectors/reliability/ve... | src/zephyr/trading/feedback_loop/dete... | Version Migrator — v0.12.0 R169 | prototype | generated |
| 126 | src/zephyr/trading/feedback_loop/diagnosers/__init__.py | src/zephyr/trading/feedback_loop/diag... | feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分为4个逻辑子包(cognit... | production | generated |
| 127 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/__i... | src/zephyr/trading/feedback_loop/diag... |  | prototype | generated |
| 128 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/ada... | src/zephyr/trading/feedback_loop/diag... | Adaptive Parameter Tuning — v0.37.0 R452 | prototype | generated |
| 129 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/cog... | src/zephyr/trading/feedback_loop/diag... | Cognitive Load Estimator — v0.6.0 R68 | prototype | generated |
| 130 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/cog... | src/zephyr/trading/feedback_loop/diag... | Cognitive Load Budget — v0.16.0 R223 | prototype | generated |
| 131 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/col... | src/zephyr/trading/feedback_loop/diag... | Collaborative Learning — v0.7.0 R82 | prototype | generated |
| 132 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/con... | src/zephyr/trading/feedback_loop/diag... | Confidence Decomposer — v0.7.0 R83 | prototype | generated |
| 133 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/gam... | src/zephyr/trading/feedback_loop/diag... | Gamification — v0.8.0 R101 | prototype | generated |
| 134 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/met... | src/zephyr/trading/feedback_loop/diag... | R516: MetaGuardLatencyBudget | prototype | generated |
| 135 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/soc... | src/zephyr/trading/feedback_loop/diag... | Socratic Questions — v0.7.0 R81 | prototype | generated |
| 136 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/ton... | src/zephyr/trading/feedback_loop/diag... | Tone Adapter — v0.9.0 R127 | prototype | generated |
| 137 | src/zephyr/trading/feedback_loop/diagnosers/cognitive/ton... | src/zephyr/trading/feedback_loop/diag... | Tone Adapter v2 — v0.10.0 R141 | prototype | generated |
| 138 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/__i... | src/zephyr/trading/feedback_loop/diag... |  | prototype | generated |
| 139 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/aut... | src/zephyr/trading/feedback_loop/diag... | Auto Diagnosis — v0.3.0 R16 | prototype | generated |
| 140 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/cau... | src/zephyr/trading/feedback_loop/diag... | Causal Inference Engine — v0.3.0 R5-R7 | prototype | generated |
| 141 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/cou... | src/zephyr/trading/feedback_loop/diag... | Counterfactual Engine — v0.6.0 R60 | prototype | generated |
| 142 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/dia... | src/zephyr/trading/feedback_loop/diag... |  | prototype | generated |
| 143 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/dia... | src/zephyr/trading/feedback_loop/diag... | Diagnosis KPI — v0.9.0 R116 | prototype | generated |
| 144 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/imp... | src/zephyr/trading/feedback_loop/diag... | Impact Predictor — v0.9.0 R121 | prototype | generated |
| 145 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/inc... | src/zephyr/trading/feedback_loop/diag... | R504: IncidentKnowledgeInjector | prototype | generated |
| 146 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/int... | src/zephyr/trading/feedback_loop/diag... | Interactive Diagnosis — v0.7.0 R80 | prototype | generated |
| 147 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/kno... | src/zephyr/trading/feedback_loop/diag... | Knowledge Bus Factor Monitor — v0.38.0 R481 | prototype | generated |
| 148 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/kno... | src/zephyr/trading/feedback_loop/diag... | Knowledge Market — v0.9.0 R126 | prototype | generated |
| 149 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/mtt... | src/zephyr/trading/feedback_loop/diag... | MTTI Tracker — v0.16.0 R221 | prototype | generated |
| 150 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/non... | src/zephyr/trading/feedback_loop/diag... | Nonstationary Effectiveness — v0.37.0 R455 | prototype | generated |
| 151 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/sta... | src/zephyr/trading/feedback_loop/diag... | Statistical Hygiene Auditor — v0.38.0 R476 | prototype | generated |
| 152 | src/zephyr/trading/feedback_loop/diagnosers/diagnosis/ver... | src/zephyr/trading/feedback_loop/diag... | Vertical Self Assessment — v0.10.0 R137 | prototype | generated |
| 153 | src/zephyr/trading/feedback_loop/diagnosers/health/__init... | src/zephyr/trading/feedback_loop/diag... |  | prototype | generated |
| 154 | src/zephyr/trading/feedback_loop/diagnosers/health/action... | src/zephyr/trading/feedback_loop/diag... | R511: ActionCompositionHealthMonitor | prototype | generated |
| 155 | src/zephyr/trading/feedback_loop/diagnosers/health/dr_res... | src/zephyr/trading/feedback_loop/diag... | DR Resilience Metrics — v0.17.0+ R231-R236 | prototype | generated |
| 156 | src/zephyr/trading/feedback_loop/diagnosers/health/e2e_in... | src/zephyr/trading/feedback_loop/diag... | E2E Integration Health Monitor — v0.39.0 R489 | prototype | generated |
| 157 | src/zephyr/trading/feedback_loop/diagnosers/health/fle_do... | src/zephyr/trading/feedback_loop/diag... | FLE Dogfood Monitor — v0.38.0 R480 | prototype | generated |
| 158 | src/zephyr/trading/feedback_loop/diagnosers/health/fle_se... | src/zephyr/trading/feedback_loop/diag... | FLE Self SLO Metrics — v0.17.0+ R249-R254 | prototype | generated |
| 159 | src/zephyr/trading/feedback_loop/diagnosers/health/global... | src/zephyr/trading/feedback_loop/diag... | Global Health Map — v0.8.0 R103 | prototype | generated |
| 160 | src/zephyr/trading/feedback_loop/diagnosers/health/memory... | src/zephyr/trading/feedback_loop/diag... | Memory Self Check — v0.8.0 R105 | prototype | generated |
| 161 | src/zephyr/trading/feedback_loop/diagnosers/health/model_... | src/zephyr/trading/feedback_loop/diag... | Model Health Monitor — v0.5.0 R40 | prototype | generated |
| 162 | src/zephyr/trading/feedback_loop/diagnosers/health/self_b... | src/zephyr/trading/feedback_loop/diag... | Self Benchmark — v0.9.0 R115 | prototype | generated |
| 163 | src/zephyr/trading/feedback_loop/diagnosers/health/self_b... | src/zephyr/trading/feedback_loop/diag... | Self-Bottleneck Detector — v0.38.0 R479 | prototype | generated |
| 164 | src/zephyr/trading/feedback_loop/diagnosers/health/self_h... | src/zephyr/trading/feedback_loop/diag... | Self Health Monitor — v0.4.0 R29 | prototype | generated |
| 165 | src/zephyr/trading/feedback_loop/diagnosers/health/self_l... | src/zephyr/trading/feedback_loop/diag... | Self LLM Observability — v0.12.0 R160 | prototype | generated |
| 166 | src/zephyr/trading/feedback_loop/diagnosers/reliability/_... | src/zephyr/trading/feedback_loop/diag... |  | prototype | generated |
| 167 | src/zephyr/trading/feedback_loop/diagnosers/reliability/a... | src/zephyr/trading/feedback_loop/diag... | Amplification Guard — v0.10.0 R134 | prototype | generated |
| 168 | src/zephyr/trading/feedback_loop/diagnosers/reliability/a... | src/zephyr/trading/feedback_loop/diag... | API Dependency Metrics — v0.17.0+ R237-R242 | prototype | generated |
| 169 | src/zephyr/trading/feedback_loop/diagnosers/reliability/b... | src/zephyr/trading/feedback_loop/diag... | Burn Rate Alerter — v0.14.0 R200 | prototype | generated |
| 170 | src/zephyr/trading/feedback_loop/diagnosers/reliability/b... | src/zephyr/trading/feedback_loop/diag... | Burnout Alarm — v0.8.0 R100 | prototype | generated |
| 171 | src/zephyr/trading/feedback_loop/diagnosers/reliability/c... | src/zephyr/trading/feedback_loop/diag... | Capacity Aware Repair — v0.9.0 R120 | prototype | generated |
| 172 | src/zephyr/trading/feedback_loop/diagnosers/reliability/c... | src/zephyr/trading/feedback_loop/diag... | R509: ColdStartConservativeMode | prototype | generated |
| 173 | src/zephyr/trading/feedback_loop/diagnosers/reliability/c... | src/zephyr/trading/feedback_loop/diag... | Context Truncation Detector — v0.9.0 R122 | prototype | generated |
| 174 | src/zephyr/trading/feedback_loop/diagnosers/reliability/c... | src/zephyr/trading/feedback_loop/diag... | R506: ContextWindowPressureManager | prototype | generated |
| 175 | src/zephyr/trading/feedback_loop/diagnosers/reliability/c... | src/zephyr/trading/feedback_loop/diag... | R513: CrossGuardConflictDetector | prototype | generated |
| 176 | src/zephyr/trading/feedback_loop/diagnosers/reliability/c... | src/zephyr/trading/feedback_loop/diag... | R510: CrossSessionConsistencyValidator | prototype | generated |
| 177 | src/zephyr/trading/feedback_loop/diagnosers/reliability/d... | src/zephyr/trading/feedback_loop/diag... | Data Volume Growth Monitor — v0.39.0 R492 | prototype | generated |
| 178 | src/zephyr/trading/feedback_loop/diagnosers/reliability/f... | src/zephyr/trading/feedback_loop/diag... | Feedback Delay Compensator — v0.38.0 R477 | prototype | generated |
| 179 | src/zephyr/trading/feedback_loop/diagnosers/reliability/g... | src/zephyr/trading/feedback_loop/diag... | R518: GuardInteractionTopologyMapper | prototype | generated |
| 180 | src/zephyr/trading/feedback_loop/diagnosers/reliability/g... | src/zephyr/trading/feedback_loop/diag... | R512: GuardSelfConsistencyAuditor | prototype | generated |
| 181 | src/zephyr/trading/feedback_loop/diagnosers/reliability/h... | src/zephyr/trading/feedback_loop/diag... | Human Anomaly Flood Detector — v0.40.0 R500 | prototype | generated |
| 182 | src/zephyr/trading/feedback_loop/diagnosers/reliability/l... | src/zephyr/trading/feedback_loop/diag... | Latency SLO Monitor — v0.14.0 R192 | prototype | generated |
| 183 | src/zephyr/trading/feedback_loop/diagnosers/reliability/l... | src/zephyr/trading/feedback_loop/diag... | LLM Provider Integrity — v0.15.0 R217 | prototype | generated |
| 184 | src/zephyr/trading/feedback_loop/diagnosers/reliability/l... | src/zephyr/trading/feedback_loop/diag... | LLM Quality Regression — v0.12.0 R161 | prototype | generated |
| 185 | src/zephyr/trading/feedback_loop/diagnosers/reliability/m... | src/zephyr/trading/feedback_loop/diag... | Model Rotation — v0.9.0 R125 | prototype | generated |
| 186 | src/zephyr/trading/feedback_loop/diagnosers/reliability/m... | src/zephyr/trading/feedback_loop/diag... | Model Rotation v2 — v0.10.0 R140 | prototype | generated |
| 187 | src/zephyr/trading/feedback_loop/diagnosers/reliability/m... | src/zephyr/trading/feedback_loop/diag... | Model Version Semantic Drift Monitor — v0.39.0 R493 | prototype | generated |
| 188 | src/zephyr/trading/feedback_loop/diagnosers/reliability/n... | src/zephyr/trading/feedback_loop/diag... | Numerical Stability Guard — v0.38.0 R475 | prototype | generated |
| 189 | src/zephyr/trading/feedback_loop/diagnosers/reliability/o... | src/zephyr/trading/feedback_loop/diag... | Operational Seasonality — v0.16.0 R228 | prototype | generated |
| 190 | src/zephyr/trading/feedback_loop/diagnosers/reliability/p... | src/zephyr/trading/feedback_loop/diag... | Prompt Fingerprint — v0.3.0 R14 | prototype | generated |
| 191 | src/zephyr/trading/feedback_loop/diagnosers/reliability/p... | src/zephyr/trading/feedback_loop/diag... | Prompt Sanitizer — v0.10.0 R133 | prototype | generated |
| 192 | src/zephyr/trading/feedback_loop/diagnosers/reliability/r... | src/zephyr/trading/feedback_loop/diag... | Recovery Time Statistics — v0.37.0 R454 | prototype | generated |
| 193 | src/zephyr/trading/feedback_loop/diagnosers/reliability/r... | src/zephyr/trading/feedback_loop/diag... | Regime Gain Scheduling — v0.37.0 R453 | prototype | generated |
| 194 | src/zephyr/trading/feedback_loop/diagnosers/reliability/r... | src/zephyr/trading/feedback_loop/diag... | Retirement Planner — v0.10.0 R139 | prototype | generated |
| 195 | src/zephyr/trading/feedback_loop/diagnosers/reliability/s... | src/zephyr/trading/feedback_loop/diag... | SLO Capacity Metrics — v0.17.0+ R243-R248 | prototype | generated |
| 196 | src/zephyr/trading/feedback_loop/diagnosers/reliability/s... | src/zephyr/trading/feedback_loop/diag... | R527: SystemEntropyMonitor | prototype | generated |
| 197 | src/zephyr/trading/feedback_loop/diagnosers/reliability/t... | src/zephyr/trading/feedback_loop/diag... | Temporal Integrity Guard — v0.38.0 R478 | prototype | generated |
| 198 | src/zephyr/trading/feedback_loop/diagnosers/reliability/t... | src/zephyr/trading/feedback_loop/diag... | Timezone Semantic Reasoner — v0.37.0 R456 | prototype | generated |
| 199 | src/zephyr/trading/feedback_loop/diagnosers/reliability/t... | src/zephyr/trading/feedback_loop/diag... | Toil Quantification — v0.37.0 R457 | prototype | generated |
| 200 | src/zephyr/trading/feedback_loop/diagnosers/reliability/v... | src/zephyr/trading/feedback_loop/diag... | Value Added Baseline — v0.10.0 R138 | prototype | generated |

> (仅显示前 200 个模块，共 464 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 435 条 / 435 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 435 条 / 435 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 302 条 / edges                               │
│   [config_depends]: 133 条 / edges                               │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│          [导入依赖 / import_depends]（302 条 / edges）           │
├──────────────────────────────────────────────────────────────────┤
│   auto_integrator.py → capability_card.py                        │
│   auto_integrator.py → capability_registry.py                    │
│   auto_integrator.py → module_onboarding_scanner.py              │
│   auto_dispatcher.py → task_queue.py                             │
│   auto_dispatcher.py → context_bridge.py                         │
│   auto_dispatcher.py → script_runner.py                          │
│   auto_runtime_core.py → auto_integrator.py                      │
│   auto_runtime_core.py → boot_hooks.py                           │
│   auto_runtime_core.py → ai_audit_logger.py                      │
│   auto_runtime_core.py → capability_sync.py                      │
│   auto_runtime_core.py → capability_registry.py                  │
│   auto_runtime_core.py → finalizer.py                            │
│   auto_runtime_core.py → dream_cycle.py                          │
│   auto_runtime_core.py → health_monitor.py                       │
│   auto_runtime_core.py → integration_registry.py                 │
│   auto_runtime_core.py → night_shift_queue.py                    │
│   auto_runtime_core.py → module_onboarding_scanner.py            │
│   auto_runtime_core.py → orphan_detector.py                      │
│   auto_runtime_core.py → resource_optimization.py                │
│   auto_runtime_core.py → lifecycle_manager.py                    │
│   auto_runtime_core.py → runtime_config.py                       │
│   auto_runtime_core.py → status_dashboard.py                     │
│   auto_runtime_core.py → stop_gate.py                            │
│   auto_runtime_core.py → work_dag.py                             │
│   auto_runtime_core.py → work_orchestrator.py                    │
│   auto_runtime_core.py → scheduler.py                            │
│   auto_runtime_core.py → __init__.py                             │
│   boot_hooks.py → finalizer.py                                   │
│   boot_hooks.py → ide_health_daemon.py                           │
│   boot_hooks.py → memory_writer.py                               │
│   capability_sync.py → capability_card.py                        │
│   capability_sync.py → capability_registry.py                    │
│   capability_registry.py → capability_card.py                    │
│   gpu_consensus_scheduler.py → verdict_engine.py                 │
│   health_monitor.py → resource_optimization.py                   │
│   module_onboarding_scanner.py → capability_registry.py          │
│   orphan_detector.py → capability_registry.py                    │
│   orphan_detector.py → module_onboarding_scanner.py              │
│   resource_optimization.py → gpu_monitor.py                      │
│   resource_optimization.py → ide_health_daemon.py                │
│   lifecycle_manager.py → ai_audit_logger.py                      │
│   lifecycle_manager.py → capability_registry.py                  │
│   lifecycle_manager.py → finalizer.py                            │
│   lifecycle_manager.py → dream_cycle.py                          │
│   lifecycle_manager.py → health_monitor.py                       │
│   lifecycle_manager.py → integration_registry.py                 │
│   lifecycle_manager.py → night_shift_queue.py                    │
│   lifecycle_manager.py → runtime_config.py                       │
│   lifecycle_manager.py → stop_gate.py                            │
│   ...还有 253 条 / 253 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends / config_depends]** (133 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 435 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[生产态 / production]`=已上线 / `[设计态 / design]`=设计中 / `[原型态 / prototype]`=原型 / `[未知 / unknown]`=未知
