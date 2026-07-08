---
doc_type: architecture_view
title: D_AUDITTEST 审计测试套件架构文档
version: "1.0"
status: active
date: 2026-07-09
owner: auto-generator
ttl: permanent
---

# 21_d_audittest / audit_test_suite / 审计测试套件 / Audit Test Suite

> **功能简介 / Overview**: 审计测试套件与用例管理

> **文档作用 / Purpose**: 展示 审计测试套件（D_AUDITTEST）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-09 01:10:27
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 21 | Number | 21 |
| 域ID | D_AUDITTEST | Domain ID | D_AUDITTEST |
| 域名称 | 审计测试套件 | Domain Name | Audit Test Suite |
| 层级 | L2 业务域层 | Layer | L2 Domain |
| 模块数 | 1677 | Module Count | 1677 |
| 域内依赖 | 10 | Internal Dependencies | 10 |
| 跨域入边 | 0 | Cross-domain Incoming | 0 |
| 跨域出边 | 2235 | Cross-domain Outgoing | 2235 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 1628 | Prototype Modules | 1628 |
| 生产态模块 | 49 | Production Modules | 49 |
| 容量 | 49/150 (正常) | Capacity | 49/150 (正常) |
| 描述 | 审计单元测试(unit) | Description | 审计单元测试(unit) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 56 页 / Page 1 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        docs_01_policies_and_standards_registry_catalogs_test_suite_registry_yaml["(生产态 / production)  Test Suite — ARCH-052 聚合节点 production"]
        tests_a2a_test_a2a_anomaly_detector_py["(原型态 / prototype) test_a2a_anomaly_detector.py"]
        tests_a2a_test_a2a_behavior_fingerprint_py["(原型态 / prototype) test_a2a_behavior_fingerprint.py"]
        tests_a2a_test_a2a_blame_attribution_py["(原型态 / prototype) test_a2a_blame_attribution.py"]
        tests_a2a_test_a2a_carbon_py["(原型态 / prototype) test_a2a_carbon.py"]
        tests_a2a_test_a2a_card_registry_py["(原型态 / prototype) test_a2a_card_registry.py"]
        tests_a2a_test_a2a_causal_trace_py["(原型态 / prototype) test_a2a_causal_trace.py"]
        tests_a2a_test_a2a_check_py["(原型态 / prototype) test_a2a_check.py"]
        tests_a2a_test_a2a_checkpoint_py["(原型态 / prototype) test_a2a_checkpoint.py"]
        tests_a2a_test_a2a_collusion_detector_py["(原型态 / prototype) test_a2a_collusion_detector.py"]
        tests_a2a_test_a2a_consent_py["(原型态 / prototype) test_a2a_consent.py"]
        tests_a2a_test_a2a_constitutional_py["(原型态 / prototype) test_a2a_constitutional.py"]
        tests_a2a_test_a2a_context_rot_py["(原型态 / prototype) test_a2a_context_rot.py"]
        tests_a2a_test_a2a_cross_agent_semantic_flow_py["(原型态 / prototype) test_a2a_cross_agent_semantic_flow.py"]
        tests_a2a_test_a2a_dashboard_py["(原型态 / prototype) test_a2a_dashboard.py"]
        tests_a2a_test_a2a_debate_py["(原型态 / prototype) test_a2a_debate.py"]
        tests_a2a_test_a2a_delegation_chain_py["(原型态 / prototype) test_a2a_delegation_chain.py"]
        tests_a2a_test_a2a_economics_py["(原型态 / prototype) test_a2a_economics.py"]
        tests_a2a_test_a2a_failure_py["(原型态 / prototype) test_a2a_failure.py"]
        tests_a2a_test_a2a_forgetting_py["(原型态 / prototype) test_a2a_forgetting.py"]
        tests_a2a_test_a2a_formal_verification_py["(原型态 / prototype) test_a2a_formal_verification.py"]
        tests_a2a_test_a2a_frame_negotiation_py["(原型态 / prototype) test_a2a_frame_negotiation.py"]
        tests_a2a_test_a2a_governance_py["(原型态 / prototype) test_a2a_governance.py"]
        tests_a2a_test_a2a_governance_adapter_py["(原型态 / prototype) test_a2a_governance_adapter.py"]
        tests_a2a_test_a2a_hardware_router_py["(原型态 / prototype) test_a2a_hardware_router.py"]
        tests_a2a_test_a2a_hibernate_py["(原型态 / prototype) test_a2a_hibernate.py"]
        tests_a2a_test_a2a_idempotency_py["(原型态 / prototype) test_a2a_idempotency.py"]
        tests_a2a_test_a2a_idle_guard_py["(原型态 / prototype) test_a2a_idle_guard.py"]
        tests_a2a_test_a2a_immune_py["(原型态 / prototype) test_a2a_immune.py"]
        tests_a2a_test_a2a_knowledge_distill_py["(原型态 / prototype) test_a2a_knowledge_distill.py"]
    end
    D_INFRA_A2A["[生产态 / production] D_INFRA_A2A"]
    tests_a2a_test_a2a_card_registry_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_card_registry_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_card_registry_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_a2a_test_a2a_check_py -.->|测试依赖 / test_depends| D_SECURITY
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_a2a_test_a2a_failure_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_a2a_test_a2a_governance_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_governance_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_governance_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class docs_01_policies_and_standards_registry_catalogs_test_suite_registry_yaml production
    class tests_a2a_test_a2a_anomaly_detector_py,tests_a2a_test_a2a_behavior_fingerprint_py,tests_a2a_test_a2a_blame_attribution_py,tests_a2a_test_a2a_carbon_py,tests_a2a_test_a2a_card_registry_py,tests_a2a_test_a2a_causal_trace_py,tests_a2a_test_a2a_check_py,tests_a2a_test_a2a_checkpoint_py,tests_a2a_test_a2a_collusion_detector_py,tests_a2a_test_a2a_consent_py,tests_a2a_test_a2a_constitutional_py,tests_a2a_test_a2a_context_rot_py,tests_a2a_test_a2a_cross_agent_semantic_flow_py,tests_a2a_test_a2a_dashboard_py,tests_a2a_test_a2a_debate_py,tests_a2a_test_a2a_delegation_chain_py,tests_a2a_test_a2a_economics_py,tests_a2a_test_a2a_failure_py,tests_a2a_test_a2a_forgetting_py,tests_a2a_test_a2a_formal_verification_py,tests_a2a_test_a2a_frame_negotiation_py,tests_a2a_test_a2a_governance_py,tests_a2a_test_a2a_governance_adapter_py,tests_a2a_test_a2a_hardware_router_py,tests_a2a_test_a2a_hibernate_py,tests_a2a_test_a2a_idempotency_py,tests_a2a_test_a2a_idle_guard_py,tests_a2a_test_a2a_immune_py,tests_a2a_test_a2a_knowledge_distill_py design
    class D_INFRA_A2A,D_SECURITY,D_GOVERNANCE external_prod
```

### 第 2 页 / 共 56 页 / Page 2 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_a2a_test_a2a_latent_comm_py["(原型态 / prototype) test_a2a_latent_comm.py"]
        tests_a2a_test_a2a_layer1_discovery_py["(原型态 / prototype) test_a2a_layer1_discovery.py"]
        tests_a2a_test_a2a_metrics_py["(原型态 / prototype) test_a2a_metrics.py"]
        tests_a2a_test_a2a_negotiation_py["(原型态 / prototype) test_a2a_negotiation.py"]
        tests_a2a_test_a2a_protocol_gateway_py["(原型态 / prototype) test_a2a_protocol_gateway.py"]
        tests_a2a_test_a2a_protocol_security_py["(原型态 / prototype) test_a2a_protocol_security.py"]
        tests_a2a_test_a2a_red_team_py["(原型态 / prototype) test_a2a_red_team.py"]
        tests_a2a_test_a2a_saga_py["(原型态 / prototype) test_a2a_saga.py"]
        tests_a2a_test_a2a_schemas_py["(原型态 / prototype) test_a2a_schemas.py"]
        tests_a2a_test_a2a_security_py["(原型态 / prototype) test_a2a_security.py"]
        tests_a2a_test_a2a_state_py["(原型态 / prototype) test_a2a_state.py"]
        tests_a2a_test_a2a_temporal_admission_py["(原型态 / prototype) test_a2a_temporal_admission.py"]
        tests_a2a_test_a2a_tracing_py["(原型态 / prototype) test_a2a_tracing.py"]
        tests_a2a_test_a2a_vector_reputation_py["(原型态 / prototype) test_a2a_vector_reputation.py"]
        tests_a2a_test_a2a_voting_py["(原型态 / prototype) test_a2a_voting.py"]
        tests_a2a_test_a2a_work_steal_py["(原型态 / prototype) test_a2a_work_steal.py"]
        tests_a2a_test_construction_verifier_py["(原型态 / prototype) test_construction_verifier.py"]
        tests_a2a_test_mcp_py["(原型态 / prototype) test_mcp.py"]
        tests_a2a_test_spec_sync_py["(原型态 / prototype) test_spec_sync.py"]
        tests_action_test_action_composition_health_monitor_py["(原型态 / prototype) test_action_composition_health_monitor.py"]
        tests_action_test_action_dispatcher_py["(原型态 / prototype) test_action_dispatcher.py"]
        tests_action_test_action_efficacy_decay_detector_py["(原型态 / prototype) test_action_efficacy_decay_detector.py"]
        tests_action_test_action_explainability_py["(原型态 / prototype) test_action_explainability.py"]
        tests_action_test_action_history_py["(原型态 / prototype) test_action_history.py"]
        tests_action_test_action_interaction_detector_py["(原型态 / prototype) test_action_interaction_detector.py"]
        tests_action_test_action_reversibility_py["(原型态 / prototype) test_action_reversibility.py"]
        tests_action_test_action_selector_py["(原型态 / prototype) test_action_selector.py"]
        tests_action_test_action_side_effect_cumulative_detector_py["(原型态 / prototype) test_action_side_effect_cumulative_detector.py"]
        tests_agent_test_agent_cooldown_py["(原型态 / prototype) test_agent_cooldown.py"]
        tests_agent_test_agent_creation_policy_py["(原型态 / prototype) test_agent_creation_policy.py"]
    end
    D_INFRA_A2A["[生产态 / production] D_INFRA_A2A"]
    tests_a2a_test_a2a_saga_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_negotiation_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_layer1_discovery_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_layer1_discovery_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_layer1_discovery_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_schemas_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_state_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_a2a_test_a2a_work_steal_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_action_test_action_dispatcher_py -.->|测试依赖 / test_depends| D_TRADING
    tests_action_test_action_composition_health_monitor_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_action_test_action_history_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_a2a_test_a2a_voting_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_action_test_action_explainability_py -.->|测试依赖 / test_depends| D_TRADING
    tests_action_test_action_efficacy_decay_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_action_test_action_interaction_detector_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_a2a_test_a2a_latent_comm_py,tests_a2a_test_a2a_layer1_discovery_py,tests_a2a_test_a2a_metrics_py,tests_a2a_test_a2a_negotiation_py,tests_a2a_test_a2a_protocol_gateway_py,tests_a2a_test_a2a_protocol_security_py,tests_a2a_test_a2a_red_team_py,tests_a2a_test_a2a_saga_py,tests_a2a_test_a2a_schemas_py,tests_a2a_test_a2a_security_py,tests_a2a_test_a2a_state_py,tests_a2a_test_a2a_temporal_admission_py,tests_a2a_test_a2a_tracing_py,tests_a2a_test_a2a_vector_reputation_py,tests_a2a_test_a2a_voting_py,tests_a2a_test_a2a_work_steal_py,tests_a2a_test_construction_verifier_py,tests_a2a_test_mcp_py,tests_a2a_test_spec_sync_py,tests_action_test_action_composition_health_monitor_py,tests_action_test_action_dispatcher_py,tests_action_test_action_efficacy_decay_detector_py,tests_action_test_action_explainability_py,tests_action_test_action_history_py,tests_action_test_action_interaction_detector_py,tests_action_test_action_reversibility_py,tests_action_test_action_selector_py,tests_action_test_action_side_effect_cumulative_detector_py,tests_agent_test_agent_cooldown_py,tests_agent_test_agent_creation_policy_py design
    class D_INFRA_A2A,D_TRADING,D_GOVERNANCE external_prod
```

### 第 3 页 / 共 56 页 / Page 3 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_agent_test_agent_health_monitor_root_py["(原型态 / prototype) test_agent_health_monitor_root.py"]
        tests_agent_test_agent_lifecycle_py["(原型态 / prototype) test_agent_lifecycle.py"]
        tests_agent_test_agent_observability_py["(原型态 / prototype) test_agent_observability.py"]
        tests_agent_test_agent_orchestrator_root_py["(原型态 / prototype) test_agent_orchestrator_root.py"]
        tests_agent_test_agent_quality_py["(原型态 / prototype) test_agent_quality.py"]
        tests_agent_test_agent_signer_py["(原型态 / prototype) test_agent_signer.py"]
        tests_agent_test_agent_skill_guard_py["(原型态 / prototype) test_agent_skill_guard.py"]
        tests_agent_test_agent_spec_main_py["(原型态 / prototype) test_agent_spec_main.py"]
        tests_agent_test_agent_spec_registry_py["(原型态 / prototype) test_agent_spec_registry.py"]
        tests_agent_test_agent_trajectory_anomaly_detector_py["(原型态 / prototype) test_agent_trajectory_anomaly_detector.py"]
        tests_agent_rbac_conftest_py["(原型态 / prototype) conftest.py"]
        tests_agent_rbac_test_abac_guard_agent_rbac_py["(原型态 / prototype) test_abac_guard_agent_rbac.py"]
        tests_agent_rbac_test_adversarial_agent_rbac_py["(原型态 / prototype) test_adversarial_agent_rbac.py"]
        tests_agent_rbac_test_adversarial_resilience_py["(原型态 / prototype) test_adversarial_resilience.py"]
        tests_agent_rbac_test_cross_model_consistency_py["(原型态 / prototype) test_cross_model_consistency.py"]
        tests_agent_rbac_test_crosscut_d_py["(原型态 / prototype) test_crosscut_d.py"]
        tests_agent_rbac_test_cybersec_2026_py["(原型态 / prototype) test_cybersec_2026.py"]
        tests_agent_rbac_test_decision_explainer_agent_rbac_py["(原型态 / prototype) test_decision_explainer_agent_rbac.py"]
        tests_agent_rbac_test_decisions_py["(原型态 / prototype) test_decisions.py"]
        tests_agent_rbac_test_derive_rbac_py["(原型态 / prototype) test_derive_rbac.py"]
        tests_agent_rbac_test_dry_run_agent_rbac_py["(原型态 / prototype) test_dry_run_agent_rbac.py"]
        tests_agent_rbac_test_engine_degradation_agent_rbac_py["(原型态 / prototype) test_engine_degradation_agent_rbac.py"]
        tests_agent_rbac_test_enhanced_security_py["(原型态 / prototype) test_enhanced_security.py"]
        tests_agent_rbac_test_exceptions_agent_rbac_py["(原型态 / prototype) test_exceptions_agent_rbac.py"]
        tests_agent_rbac_test_forensic_a_py["(原型态 / prototype) test_forensic_a.py"]
        tests_agent_rbac_test_forensic_b_py["(原型态 / prototype) test_forensic_b.py"]
        tests_agent_rbac_test_forensic_c_py["(原型态 / prototype) test_forensic_c.py"]
        tests_agent_rbac_test_guard_layers_agent_rbac_py["(原型态 / prototype) test_guard_layers_agent_rbac.py"]
        tests_agent_rbac_test_identity_py["(原型态 / prototype) test_identity.py"]
        tests_agent_rbac_test_immutable_core_agent_rbac_py["(原型态 / prototype) test_immutable_core_agent_rbac.py"]
    end
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_agent_test_agent_observability_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_agent_test_agent_health_monitor_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_health_monitor_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_lifecycle_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_orchestrator_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_spec_main_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_agent_test_agent_signer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_agent_test_agent_quality_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_skill_guard_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_trajectory_anomaly_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_test_agent_spec_registry_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_agent_rbac_test_abac_guard_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_abac_guard_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_crosscut_d_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_crosscut_d_py -.->|测试依赖 / test_depends| D_SECURITY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_agent_test_agent_health_monitor_root_py,tests_agent_test_agent_lifecycle_py,tests_agent_test_agent_observability_py,tests_agent_test_agent_orchestrator_root_py,tests_agent_test_agent_quality_py,tests_agent_test_agent_signer_py,tests_agent_test_agent_skill_guard_py,tests_agent_test_agent_spec_main_py,tests_agent_test_agent_spec_registry_py,tests_agent_test_agent_trajectory_anomaly_detector_py,tests_agent_rbac_conftest_py,tests_agent_rbac_test_abac_guard_agent_rbac_py,tests_agent_rbac_test_adversarial_agent_rbac_py,tests_agent_rbac_test_adversarial_resilience_py,tests_agent_rbac_test_cross_model_consistency_py,tests_agent_rbac_test_crosscut_d_py,tests_agent_rbac_test_cybersec_2026_py,tests_agent_rbac_test_decision_explainer_agent_rbac_py,tests_agent_rbac_test_decisions_py,tests_agent_rbac_test_derive_rbac_py,tests_agent_rbac_test_dry_run_agent_rbac_py,tests_agent_rbac_test_engine_degradation_agent_rbac_py,tests_agent_rbac_test_enhanced_security_py,tests_agent_rbac_test_exceptions_agent_rbac_py,tests_agent_rbac_test_forensic_a_py,tests_agent_rbac_test_forensic_b_py,tests_agent_rbac_test_forensic_c_py,tests_agent_rbac_test_guard_layers_agent_rbac_py,tests_agent_rbac_test_identity_py,tests_agent_rbac_test_immutable_core_agent_rbac_py design
    class D_AUTONOMY_CORE,D_TRADING,D_GOVERNANCE,D_SECURITY external_prod
```

### 第 4 页 / 共 56 页 / Page 4 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_agent_rbac_test_input_guard_agent_rbac_py["(原型态 / prototype) test_input_guard_agent_rbac.py"]
        tests_agent_rbac_test_integration_agent_rbac_py["(原型态 / prototype) test_integration_agent_rbac.py"]
        tests_agent_rbac_test_integration_root_py["(原型态 / prototype) test_integration_root.py"]
        tests_agent_rbac_test_integrity_agent_rbac_py["(原型态 / prototype) test_integrity_agent_rbac.py"]
        tests_agent_rbac_test_intent_binder_agent_rbac_py["(原型态 / prototype) test_intent_binder_agent_rbac.py"]
        tests_agent_rbac_test_kill_switch_agent_rbac_py["(原型态 / prototype) test_kill_switch_agent_rbac.py"]
        tests_agent_rbac_test_novel_attack_py["(原型态 / prototype) test_novel_attack.py"]
        tests_agent_rbac_test_observability_agent_rbac_py["(原型态 / prototype) test_observability_agent_rbac.py"]
        tests_agent_rbac_test_output_guard_agent_rbac_py["(原型态 / prototype) test_output_guard_agent_rbac.py"]
        tests_agent_rbac_test_permission_guard_py["(原型态 / prototype) test_permission_guard.py"]
        tests_agent_rbac_test_permissions_py["(原型态 / prototype) test_permissions.py"]
        tests_agent_rbac_test_post_action_py["(原型态 / prototype) test_post_action.py"]
        tests_agent_rbac_test_rbac_auto_lifecycle_py["(原型态 / prototype) test_rbac_auto_lifecycle.py"]
        tests_agent_rbac_test_rbac_guard_agent_rbac_py["(原型态 / prototype) test_rbac_guard_agent_rbac.py"]
        tests_agent_rbac_test_redteam_adversarial_py["(原型态 / prototype) test_redteam_adversarial.py"]
        tests_agent_rbac_test_risk_mitigation_agent_rbac_py["(原型态 / prototype) test_risk_mitigation_agent_rbac.py"]
        tests_agent_rbac_test_sequence_guard_agent_rbac_py["(原型态 / prototype) test_sequence_guard_agent_rbac.py"]
        tests_agent_rbac_test_session_aware_stash_red_blue_py["(原型态 / prototype) test_session_aware_stash_red_blue.py"]
        tests_agent_rbac_test_toctou_guard_agent_rbac_py["(原型态 / prototype) test_toctou_guard_agent_rbac.py"]
        tests_agent_rbac_test_vibe_coding_py["(原型态 / prototype) test_vibe_coding.py"]
        tests_ai_test_ai_audit_logger_py["(原型态 / prototype) test_ai_audit_logger.py"]
        tests_ai_test_ai_capability_guard_py["(原型态 / prototype) test_ai_capability_guard.py"]
        tests_ai_test_ai_comment_veracity_py["(原型态 / prototype) test_ai_comment_veracity.py"]
        tests_ai_test_ai_construction_detectors_py["(原型态 / prototype) test_ai_construction_detectors.py"]
        tests_ai_test_ai_context_injector_py["(原型态 / prototype) test_ai_context_injector.py"]
        tests_asset_inventory_test_asset_inventory_py["(原型态 / prototype) test_asset_inventory.py"]
        tests_audit_test_ab_test_py["(原型态 / prototype) test_ab_test.py"]
        tests_audit_test_absence_manager_py["(原型态 / prototype) test_absence_manager.py"]
        tests_audit_test_amplification_guard_py["(原型态 / prototype) test_amplification_guard.py"]
        tests_audit_test_api_dependency_metrics_py["(原型态 / prototype) test_api_dependency_metrics.py"]
    end
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_agent_rbac_test_input_guard_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_integration_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_integration_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_integrity_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_integration_root_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_intent_binder_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_output_guard_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_novel_attack_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_novel_attack_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_kill_switch_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_observability_agent_rbac_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_rbac_auto_lifecycle_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_agent_rbac_test_rbac_auto_lifecycle_py -.->|测试依赖 / test_depends| D_SECURITY
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_agent_rbac_test_rbac_auto_lifecycle_py -.->|测试依赖 / test_depends| D_TRADING
    tests_agent_rbac_test_rbac_auto_lifecycle_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_agent_rbac_test_input_guard_agent_rbac_py,tests_agent_rbac_test_integration_agent_rbac_py,tests_agent_rbac_test_integration_root_py,tests_agent_rbac_test_integrity_agent_rbac_py,tests_agent_rbac_test_intent_binder_agent_rbac_py,tests_agent_rbac_test_kill_switch_agent_rbac_py,tests_agent_rbac_test_novel_attack_py,tests_agent_rbac_test_observability_agent_rbac_py,tests_agent_rbac_test_output_guard_agent_rbac_py,tests_agent_rbac_test_permission_guard_py,tests_agent_rbac_test_permissions_py,tests_agent_rbac_test_post_action_py,tests_agent_rbac_test_rbac_auto_lifecycle_py,tests_agent_rbac_test_rbac_guard_agent_rbac_py,tests_agent_rbac_test_redteam_adversarial_py,tests_agent_rbac_test_risk_mitigation_agent_rbac_py,tests_agent_rbac_test_sequence_guard_agent_rbac_py,tests_agent_rbac_test_session_aware_stash_red_blue_py,tests_agent_rbac_test_toctou_guard_agent_rbac_py,tests_agent_rbac_test_vibe_coding_py,tests_ai_test_ai_audit_logger_py,tests_ai_test_ai_capability_guard_py,tests_ai_test_ai_comment_veracity_py,tests_ai_test_ai_construction_detectors_py,tests_ai_test_ai_context_injector_py,tests_asset_inventory_test_asset_inventory_py,tests_audit_test_ab_test_py,tests_audit_test_absence_manager_py,tests_audit_test_amplification_guard_py,tests_audit_test_api_dependency_metrics_py design
    class D_SECURITY,D_TRADING external_prod
```

### 第 5 页 / 共 56 页 / Page 5 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_audit_test_architecture_contracts_py["(原型态 / prototype) test_architecture_contracts.py"]
        tests_audit_test_architecture_principles_py["(原型态 / prototype) test_architecture_principles.py"]
        tests_audit_test_audit_anomaly_py["(原型态 / prototype) test_audit_anomaly.py"]
        tests_audit_test_audit_api_lifecycle_py["(原型态 / prototype) test_audit_api_lifecycle.py"]
        tests_audit_test_audit_bridge_py["(原型态 / prototype) test_audit_bridge.py"]
        tests_audit_test_audit_chain_verifier_py["(原型态 / prototype) test_audit_chain_verifier.py"]
        tests_audit_test_audit_cli_py["(原型态 / prototype) test_audit_cli.py"]
        tests_audit_test_audit_contracts_py["(原型态 / prototype) test_audit_contracts.py"]
        tests_audit_test_audit_dim_d1_d4_e2e_py["(原型态 / prototype) test_audit_dim_d1_d4_e2e.py"]
        tests_audit_test_audit_dim_d5_d8_e2e_py["(原型态 / prototype) test_audit_dim_d5_d8_e2e.py"]
        tests_audit_test_audit_dim_d9_d12_e2e_py["(原型态 / prototype) test_audit_dim_d9_d12_e2e.py"]
        tests_audit_test_audit_financial_compliance_py["(原型态 / prototype) test_audit_financial_compliance.py"]
        tests_audit_test_audit_full_closure_e2e_py["(原型态 / prototype) test_audit_full_closure_e2e.py"]
        tests_audit_test_audit_full_pipeline_e2e_py["(原型态 / prototype) test_audit_full_pipeline_e2e.py"]
        tests_audit_test_audit_incremental_review_py["(原型态 / prototype) test_audit_incremental_review.py"]
        tests_audit_test_audit_indexer_py["(原型态 / prototype) test_audit_indexer.py"]
        tests_audit_test_audit_integrity_py["(原型态 / prototype) test_audit_integrity.py"]
        tests_audit_test_audit_log_guard_py["(原型态 / prototype) test_audit_log_guard.py"]
        tests_audit_test_audit_models_py["(原型态 / prototype) test_audit_models.py"]
        tests_audit_test_audit_observability_dashboard_py["(原型态 / prototype) test_audit_observability_dashboard.py"]
        tests_audit_test_audit_orchestrator_e2e_py["(原型态 / prototype) test_audit_orchestrator_e2e.py"]
        tests_audit_test_audit_orphan_judge_e2e_py["(原型态 / prototype) test_audit_orphan_judge_e2e.py"]
        tests_audit_test_audit_provenance_tracker_py["(原型态 / prototype) test_audit_provenance_tracker.py"]
        tests_audit_test_audit_red_blue_e2e_py["(原型态 / prototype) test_audit_red_blue_e2e.py"]
        tests_audit_test_audit_registry_gate_e2e_py["(原型态 / prototype) test_audit_registry_gate_e2e.py"]
        tests_audit_test_audit_self_healer_e2e_py["(原型态 / prototype) test_audit_self_healer_e2e.py"]
        tests_audit_test_audit_spec_auditor_py["(原型态 / prototype) test_audit_spec_auditor.py"]
        tests_audit_test_audit_supply_chain_security_py["(原型态 / prototype) test_audit_supply_chain_security.py"]
        tests_audit_test_audit_write_failure_protector_py["(原型态 / prototype) test_audit_write_failure_protector.py"]
        tests_audit_test_backcompat_checker_py["(原型态 / prototype) test_backcompat_checker.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_audit_test_audit_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_cli_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_api_lifecycle_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_anomaly_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_audit_test_audit_chain_verifier_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_audit_test_audit_chain_verifier_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_audit_test_audit_dim_d9_d12_e2e_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_contracts_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_dim_d5_d8_e2e_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_dim_d1_d4_e2e_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_audit_test_audit_log_guard_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_audit_test_audit_incremental_review_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_models_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_indexer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_audit_integrity_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_audit_test_architecture_contracts_py,tests_audit_test_architecture_principles_py,tests_audit_test_audit_anomaly_py,tests_audit_test_audit_api_lifecycle_py,tests_audit_test_audit_bridge_py,tests_audit_test_audit_chain_verifier_py,tests_audit_test_audit_cli_py,tests_audit_test_audit_contracts_py,tests_audit_test_audit_dim_d1_d4_e2e_py,tests_audit_test_audit_dim_d5_d8_e2e_py,tests_audit_test_audit_dim_d9_d12_e2e_py,tests_audit_test_audit_financial_compliance_py,tests_audit_test_audit_full_closure_e2e_py,tests_audit_test_audit_full_pipeline_e2e_py,tests_audit_test_audit_incremental_review_py,tests_audit_test_audit_indexer_py,tests_audit_test_audit_integrity_py,tests_audit_test_audit_log_guard_py,tests_audit_test_audit_models_py,tests_audit_test_audit_observability_dashboard_py,tests_audit_test_audit_orchestrator_e2e_py,tests_audit_test_audit_orphan_judge_e2e_py,tests_audit_test_audit_provenance_tracker_py,tests_audit_test_audit_red_blue_e2e_py,tests_audit_test_audit_registry_gate_e2e_py,tests_audit_test_audit_self_healer_e2e_py,tests_audit_test_audit_spec_auditor_py,tests_audit_test_audit_supply_chain_security_py,tests_audit_test_audit_write_failure_protector_py,tests_audit_test_backcompat_checker_py design
    class D_GOVERNANCE,D_GOV_ENFORCEMENT,D_SECURITY external_prod
```

### 第 6 页 / 共 56 页 / Page 6 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_audit_test_baseline_manager_py["(原型态 / prototype) test_baseline_manager.py"]
        tests_audit_test_baseline_poisoning_guard_py["(原型态 / prototype) test_baseline_poisoning_guard.py"]
        tests_audit_test_benchmark_integrity_py["(原型态 / prototype) test_benchmark_integrity.py"]
        tests_audit_test_brain_integration_root_py["(原型态 / prototype) test_brain_integration_root.py"]
        tests_audit_test_build_reproducibility_verifier_py["(原型态 / prototype) test_build_reproducibility_verifier.py"]
        tests_audit_test_build_reproducibility_verifier_v2_py["(原型态 / prototype) test_build_reproducibility_verifier_v2.py"]
        tests_audit_test_burn_rate_alerter_py["(原型态 / prototype) test_burn_rate_alerter.py"]
        tests_audit_test_burnout_alarm_py["(原型态 / prototype) test_burnout_alarm.py"]
        tests_audit_test_cascade_detector_py["(原型态 / prototype) test_cascade_detector.py"]
        tests_audit_test_causal_inference_engine_py["(原型态 / prototype) test_causal_inference_engine.py"]
        tests_audit_test_code_review_ai_py["(原型态 / prototype) test_code_review_ai.py"]
        tests_audit_test_cognitive_load_budget_py["(原型态 / prototype) test_cognitive_load_budget.py"]
        tests_audit_test_correlation_engine_py["(原型态 / prototype) test_correlation_engine.py"]
        tests_audit_test_credibility_engine_py["(原型态 / prototype) test_credibility_engine.py"]
        tests_audit_test_crypto_bootstrap_py["(原型态 / prototype) test_crypto_bootstrap.py"]
        tests_audit_test_detector_dispatcher_py["(原型态 / prototype) test_detector_dispatcher.py"]
        tests_audit_test_deterministic_replay_py["(原型态 / prototype) test_deterministic_replay.py"]
        tests_audit_test_diagnosis_kpi_py["(原型态 / prototype) test_diagnosis_kpi.py"]
        tests_audit_test_emergent_behavior_detector_py["(原型态 / prototype) test_emergent_behavior_detector.py"]
        tests_audit_test_events_ba_py["(原型态 / prototype) test_events_ba.py"]
        tests_audit_test_forensics_engine_py["(原型态 / prototype) test_forensics_engine.py"]
        tests_audit_test_gitignore_auditor_py["(原型态 / prototype) test_gitignore_auditor.py"]
        tests_audit_test_global_health_map_py["(原型态 / prototype) test_global_health_map.py"]
        tests_audit_test_handoff_manager_py["(原型态 / prototype) test_handoff_manager.py"]
        tests_audit_test_headless_scanner_py["(原型态 / prototype) test_headless_scanner.py"]
        tests_audit_test_human_anomaly_flood_detector_py["(原型态 / prototype) test_human_anomaly_flood_detector.py"]
        tests_audit_test_incremental_scanner_py["(原型态 / prototype) test_incremental_scanner.py"]
        tests_audit_test_interactive_diagnosis_py["(原型态 / prototype) test_interactive_diagnosis.py"]
        tests_audit_test_intermittent_failure_pattern_py["(原型态 / prototype) test_intermittent_failure_pattern.py"]
        tests_audit_test_latency_slo_py["(原型态 / prototype) test_latency_slo.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_audit_test_baseline_manager_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_benchmark_integrity_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_brain_integration_root_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_baseline_poisoning_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_audit_test_build_reproducibility_verifier_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_burn_rate_alerter_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_build_reproducibility_verifier_v2_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_cognitive_load_budget_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_causal_inference_engine_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_burnout_alarm_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_cascade_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_correlation_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_credibility_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_crypto_bootstrap_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_emergent_behavior_detector_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_audit_test_baseline_manager_py,tests_audit_test_baseline_poisoning_guard_py,tests_audit_test_benchmark_integrity_py,tests_audit_test_brain_integration_root_py,tests_audit_test_build_reproducibility_verifier_py,tests_audit_test_build_reproducibility_verifier_v2_py,tests_audit_test_burn_rate_alerter_py,tests_audit_test_burnout_alarm_py,tests_audit_test_cascade_detector_py,tests_audit_test_causal_inference_engine_py,tests_audit_test_code_review_ai_py,tests_audit_test_cognitive_load_budget_py,tests_audit_test_correlation_engine_py,tests_audit_test_credibility_engine_py,tests_audit_test_crypto_bootstrap_py,tests_audit_test_detector_dispatcher_py,tests_audit_test_deterministic_replay_py,tests_audit_test_diagnosis_kpi_py,tests_audit_test_emergent_behavior_detector_py,tests_audit_test_events_ba_py,tests_audit_test_forensics_engine_py,tests_audit_test_gitignore_auditor_py,tests_audit_test_global_health_map_py,tests_audit_test_handoff_manager_py,tests_audit_test_headless_scanner_py,tests_audit_test_human_anomaly_flood_detector_py,tests_audit_test_incremental_scanner_py,tests_audit_test_interactive_diagnosis_py,tests_audit_test_intermittent_failure_pattern_py,tests_audit_test_latency_slo_py design
    class D_GOVERNANCE,D_TRADING external_prod
```

### 第 7 页 / 共 56 页 / Page 7 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_audit_test_ml_engineering_py["(原型态 / prototype) test_ml_engineering.py"]
        tests_audit_test_mtti_tracker_py["(原型态 / prototype) test_mtti_tracker.py"]
        tests_audit_test_naming_magic_checker_py["(原型态 / prototype) test_naming_magic_checker.py"]
        tests_audit_test_orphan_scanner_py["(原型态 / prototype) test_orphan_scanner.py"]
        tests_audit_test_performance_baseline_py["(原型态 / prototype) test_performance_baseline.py"]
        tests_audit_test_point_in_time_reconstructor_py["(原型态 / prototype) test_point_in_time_reconstructor.py"]
        tests_audit_test_pre_flight_simulator_py["(原型态 / prototype) test_pre_flight_simulator.py"]
        tests_audit_test_preventive_repair_py["(原型态 / prototype) test_preventive_repair.py"]
        tests_audit_test_python_compat_py["(原型态 / prototype) test_python_compat.py"]
        tests_audit_test_regime_detector_py["(原型态 / prototype) test_regime_detector.py"]
        tests_audit_test_regime_gain_scheduling_py["(原型态 / prototype) test_regime_gain_scheduling.py"]
        tests_audit_test_roi_engine_py["(原型态 / prototype) test_roi_engine.py"]
        tests_audit_test_scan_mutex_py["(原型态 / prototype) test_scan_mutex.py"]
        tests_audit_test_serialization_format_tracker_py["(原型态 / prototype) test_serialization_format_tracker.py"]
        tests_audit_test_sim2real_calibration_py["(原型态 / prototype) test_sim2real_calibration.py"]
        tests_audit_test_socratic_questions_py["(原型态 / prototype) test_socratic_questions.py"]
        tests_audit_test_state_machine_py["(原型态 / prototype) test_state_machine.py"]
        tests_audit_test_statistical_hygiene_auditor_py["(原型态 / prototype) test_statistical_hygiene_auditor.py"]
        tests_audit_test_sub_agent_collusion_py["(原型态 / prototype) test_sub_agent_collusion.py"]
        tests_audit_test_suppression_learner_py["(原型态 / prototype) test_suppression_learner.py"]
        tests_audit_test_symlink_checker_py["(原型态 / prototype) test_symlink_checker.py"]
        tests_audit_test_tamper_proof_audit_py["(原型态 / prototype) test_tamper_proof_audit.py"]
        tests_audit_test_test_fixture_checker_py["(原型态 / prototype) test_test_fixture_checker.py"]
        tests_audit_test_toctou_revalidation_py["(原型态 / prototype) test_toctou_revalidation.py"]
        tests_audit_test_toil_quantification_py["(原型态 / prototype) test_toil_quantification.py"]
        tests_audit_test_tone_adapter_py["(原型态 / prototype) test_tone_adapter.py"]
        tests_audit_test_tone_adapter_v2_py["(原型态 / prototype) test_tone_adapter_v2.py"]
        tests_audit_test_traffic_replay_validator_py["(原型态 / prototype) test_traffic_replay_validator.py"]
        tests_audit_test_trend_analyzer_py["(原型态 / prototype) test_trend_analyzer.py"]
        tests_audit_test_value_added_baseline_py["(原型态 / prototype) test_value_added_baseline.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_audit_test_mtti_tracker_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_audit_test_ml_engineering_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_orphan_scanner_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_performance_baseline_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_point_in_time_reconstructor_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_preventive_repair_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_naming_magic_checker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_pre_flight_simulator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_python_compat_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_roi_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_regime_gain_scheduling_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_serialization_format_tracker_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_scan_mutex_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_scan_mutex_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_audit_test_regime_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_audit_test_ml_engineering_py,tests_audit_test_mtti_tracker_py,tests_audit_test_naming_magic_checker_py,tests_audit_test_orphan_scanner_py,tests_audit_test_performance_baseline_py,tests_audit_test_point_in_time_reconstructor_py,tests_audit_test_pre_flight_simulator_py,tests_audit_test_preventive_repair_py,tests_audit_test_python_compat_py,tests_audit_test_regime_detector_py,tests_audit_test_regime_gain_scheduling_py,tests_audit_test_roi_engine_py,tests_audit_test_scan_mutex_py,tests_audit_test_serialization_format_tracker_py,tests_audit_test_sim2real_calibration_py,tests_audit_test_socratic_questions_py,tests_audit_test_state_machine_py,tests_audit_test_statistical_hygiene_auditor_py,tests_audit_test_sub_agent_collusion_py,tests_audit_test_suppression_learner_py,tests_audit_test_symlink_checker_py,tests_audit_test_tamper_proof_audit_py,tests_audit_test_test_fixture_checker_py,tests_audit_test_toctou_revalidation_py,tests_audit_test_toil_quantification_py,tests_audit_test_tone_adapter_py,tests_audit_test_tone_adapter_v2_py,tests_audit_test_traffic_replay_validator_py,tests_audit_test_trend_analyzer_py,tests_audit_test_value_added_baseline_py design
    class D_TRADING,D_GOVERNANCE external_prod
```

### 第 8 页 / 共 56 页 / Page 8 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_audit_test_verification_engine_py["(原型态 / prototype) test_verification_engine.py"]
        tests_audit_test_zombie_fle_detector_py["(原型态 / prototype) test_zombie_fle_detector.py"]
        tests_automation_test_auto_bootstrap_py["(原型态 / prototype) test_auto_bootstrap.py"]
        tests_automation_test_auto_diagnosis_py["(原型态 / prototype) test_auto_diagnosis.py"]
        tests_automation_test_auto_diagnostics_py["(原型态 / prototype) test_auto_diagnostics.py"]
        tests_automation_test_auto_evolution_root_py["(原型态 / prototype) test_auto_evolution_root.py"]
        tests_automation_test_auto_fix_autopilot_py["(原型态 / prototype) test_auto_fix_autopilot.py"]
        tests_automation_test_auto_fix_engine_py["(原型态 / prototype) test_auto_fix_engine.py"]
        tests_automation_test_auto_fix_phase_manager_py["(原型态 / prototype) test_auto_fix_phase_manager.py"]
        tests_automation_test_auto_fix_red_blue_py["(原型态 / prototype) test_auto_fix_red_blue.py"]
        tests_automation_test_auto_fixer_py["(原型态 / prototype) test_auto_fixer.py"]
        tests_automation_test_auto_integrator_py["(原型态 / prototype) test_auto_integrator.py"]
        tests_automation_test_auto_maintenance_py["(原型态 / prototype) test_auto_maintenance.py"]
        tests_automation_test_auto_reward_py["(原型态 / prototype) test_auto_reward.py"]
        tests_automation_test_auto_rollback_py["(原型态 / prototype) test_auto_rollback.py"]
        tests_automation_test_auto_rollback_trigger_py["(原型态 / prototype) test_auto_rollback_trigger.py"]
        tests_automation_test_auto_runtime_core_py["(原型态 / prototype) test_auto_runtime_core.py"]
        tests_automation_test_auto_runtime_e2e_py["(原型态 / prototype) test_auto_runtime_e2e.py"]
        tests_automation_test_auto_runtime_fle_integration_py["(原型态 / prototype) test_auto_runtime_fle_integration.py"]
        tests_automation_test_auto_split_py["(原型态 / prototype) test_auto_split.py"]
        tests_automation_test_auto_task_generator_py["(原型态 / prototype) test_auto_task_generator.py"]
        tests_automation_test_auto_test_generator_py["(原型态 / prototype) test_auto_test_generator.py"]
        tests_autonomy_test_adversarial_robustness_py["(原型态 / prototype) test_adversarial_robustness.py"]
        tests_autonomy_test_alignment_scorer_py["(原型态 / prototype) test_alignment_scorer.py"]
        tests_autonomy_test_all_skill_modules_py["(原型态 / prototype) test_all_skill_modules.py"]
        tests_autonomy_test_architecture_context_loader_py["(原型态 / prototype) test_architecture_context_loader.py"]
        tests_autonomy_test_assembly_context_assembler_py["(原型态 / prototype) test_assembly_context_assembler.py"]
        tests_autonomy_test_assembly_context_injector_py["(原型态 / prototype) test_assembly_context_injector.py"]
        tests_autonomy_test_assembly_context_pipeline_py["(原型态 / prototype) test_assembly_context_pipeline.py"]
        tests_autonomy_test_atomic_injector_py["(原型态 / prototype) test_atomic_injector.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_audit_test_verification_engine_py -.->|测试依赖 / test_depends| D_TRADING
    tests_audit_test_zombie_fle_detector_py -.->|测试依赖 / test_depends| D_TRADING
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_automation_test_auto_diagnostics_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_evolution_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_automation_test_auto_evolution_root_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_automation_test_auto_fixer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_automation_test_auto_integrator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_automation_test_auto_integrator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_automation_test_auto_integrator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_automation_test_auto_integrator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_automation_test_auto_diagnosis_py -.->|测试依赖 / test_depends| D_TRADING
    tests_automation_test_auto_fix_red_blue_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_fix_red_blue_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_fix_red_blue_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_fix_red_blue_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_audit_test_verification_engine_py,tests_audit_test_zombie_fle_detector_py,tests_automation_test_auto_bootstrap_py,tests_automation_test_auto_diagnosis_py,tests_automation_test_auto_diagnostics_py,tests_automation_test_auto_evolution_root_py,tests_automation_test_auto_fix_autopilot_py,tests_automation_test_auto_fix_engine_py,tests_automation_test_auto_fix_phase_manager_py,tests_automation_test_auto_fix_red_blue_py,tests_automation_test_auto_fixer_py,tests_automation_test_auto_integrator_py,tests_automation_test_auto_maintenance_py,tests_automation_test_auto_reward_py,tests_automation_test_auto_rollback_py,tests_automation_test_auto_rollback_trigger_py,tests_automation_test_auto_runtime_core_py,tests_automation_test_auto_runtime_e2e_py,tests_automation_test_auto_runtime_fle_integration_py,tests_automation_test_auto_split_py,tests_automation_test_auto_task_generator_py,tests_automation_test_auto_test_generator_py,tests_autonomy_test_adversarial_robustness_py,tests_autonomy_test_alignment_scorer_py,tests_autonomy_test_all_skill_modules_py,tests_autonomy_test_architecture_context_loader_py,tests_autonomy_test_assembly_context_assembler_py,tests_autonomy_test_assembly_context_injector_py,tests_autonomy_test_assembly_context_pipeline_py,tests_autonomy_test_atomic_injector_py design
    class D_TRADING,D_INFRA_RUNTIME,D_GOVERNANCE external_prod
```

### 第 9 页 / 共 56 页 / Page 9 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_autonomy_test_autonomy_credit_py["(原型态 / prototype) test_autonomy_credit.py"]
        tests_autonomy_test_autonomy_dashboard_py["(原型态 / prototype) test_autonomy_dashboard.py"]
        tests_autonomy_test_autonomy_guard_py["(原型态 / prototype) test_autonomy_guard.py"]
        tests_autonomy_test_autonomy_maturity_py["(原型态 / prototype) test_autonomy_maturity.py"]
        tests_autonomy_test_autonomy_regressor_py["(原型态 / prototype) test_autonomy_regressor.py"]
        tests_autonomy_test_behavioral_auditor_main_py["(原型态 / prototype) test_behavioral_auditor_main.py"]
        tests_autonomy_test_cache_invalidation_py["(原型态 / prototype) test_cache_invalidation.py"]
        tests_autonomy_test_checkpoint_manager_py["(原型态 / prototype) test_checkpoint_manager.py"]
        tests_autonomy_test_citation_walker_py["(原型态 / prototype) test_citation_walker.py"]
        tests_autonomy_test_complexity_budget_py["(原型态 / prototype) test_complexity_budget.py"]
        tests_autonomy_test_context_pipeline_red_blue_py["(原型态 / prototype) test_context_pipeline_red_blue.py"]
        tests_autonomy_test_contextual_fetch_api_py["(原型态 / prototype) test_contextual_fetch_api.py"]
        tests_autonomy_test_curation_loop_root_py["(原型态 / prototype) test_curation_loop_root.py"]
        tests_autonomy_test_diff_injector_py["(原型态 / prototype) test_diff_injector.py"]
        tests_autonomy_test_dispatch_table_root_py["(原型态 / prototype) test_dispatch_table_root.py"]
        tests_autonomy_test_diversity_constraint_py["(原型态 / prototype) test_diversity_constraint.py"]
        tests_autonomy_test_doc_compressor_root_py["(原型态 / prototype) test_doc_compressor_root.py"]
        tests_autonomy_test_domain_decay_config_py["(原型态 / prototype) test_domain_decay_config.py"]
        tests_autonomy_test_embedding_version_lock_py["(原型态 / prototype) test_embedding_version_lock.py"]
        tests_autonomy_test_fallback_staleness_gate_py["(原型态 / prototype) test_fallback_staleness_gate.py"]
        tests_autonomy_test_fragmentation_index_py["(原型态 / prototype) test_fragmentation_index.py"]
        tests_autonomy_test_host_resource_governor_py["(原型态 / prototype) test_host_resource_governor.py"]
        tests_autonomy_test_ide_watcher_py["(原型态 / prototype) test_ide_watcher.py"]
        tests_autonomy_test_integrity_check_py["(原型态 / prototype) test_integrity_check.py"]
        tests_autonomy_test_list_ce_files_py["(原型态 / prototype) test_list_ce_files.py"]
        tests_autonomy_test_lsg_pattern_tracker_py["(原型态 / prototype) test_lsg_pattern_tracker.py"]
        tests_autonomy_test_mgmt_context_budget_tracker_py["(原型态 / prototype) test_mgmt_context_budget_tracker.py"]
        tests_autonomy_test_mgmt_context_evictor_py["(原型态 / prototype) test_mgmt_context_evictor.py"]
        tests_autonomy_test_mgmt_context_rot_model_py["(原型态 / prototype) test_mgmt_context_rot_model.py"]
        tests_autonomy_test_mode_manager_py["(原型态 / prototype) test_mode_manager.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_autonomy_test_autonomy_credit_py -.->|测试依赖 / test_depends| D_TRADING
    tests_autonomy_test_autonomy_guard_py -.->|测试依赖 / test_depends| D_TRADING
    tests_autonomy_test_autonomy_maturity_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_autonomy_test_autonomy_regressor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_autonomy_test_behavioral_auditor_main_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_autonomy_test_cache_invalidation_py -.->|测试依赖 / test_depends| D_SHARED
    tests_autonomy_test_citation_walker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_autonomy_test_complexity_budget_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_curation_loop_root_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_checkpoint_manager_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_diversity_constraint_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_dispatch_table_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_autonomy_test_diff_injector_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_contextual_fetch_api_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_context_pipeline_red_blue_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_autonomy_test_autonomy_credit_py,tests_autonomy_test_autonomy_dashboard_py,tests_autonomy_test_autonomy_guard_py,tests_autonomy_test_autonomy_maturity_py,tests_autonomy_test_autonomy_regressor_py,tests_autonomy_test_behavioral_auditor_main_py,tests_autonomy_test_cache_invalidation_py,tests_autonomy_test_checkpoint_manager_py,tests_autonomy_test_citation_walker_py,tests_autonomy_test_complexity_budget_py,tests_autonomy_test_context_pipeline_red_blue_py,tests_autonomy_test_contextual_fetch_api_py,tests_autonomy_test_curation_loop_root_py,tests_autonomy_test_diff_injector_py,tests_autonomy_test_dispatch_table_root_py,tests_autonomy_test_diversity_constraint_py,tests_autonomy_test_doc_compressor_root_py,tests_autonomy_test_domain_decay_config_py,tests_autonomy_test_embedding_version_lock_py,tests_autonomy_test_fallback_staleness_gate_py,tests_autonomy_test_fragmentation_index_py,tests_autonomy_test_host_resource_governor_py,tests_autonomy_test_ide_watcher_py,tests_autonomy_test_integrity_check_py,tests_autonomy_test_list_ce_files_py,tests_autonomy_test_lsg_pattern_tracker_py,tests_autonomy_test_mgmt_context_budget_tracker_py,tests_autonomy_test_mgmt_context_evictor_py,tests_autonomy_test_mgmt_context_rot_model_py,tests_autonomy_test_mode_manager_py design
    class D_TRADING,D_GOVERNANCE,D_AUTONOMY_CORE,D_SHARED external_prod
```

### 第 10 页 / 共 56 页 / Page 10 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_autonomy_test_otel_instrumentation_py["(原型态 / prototype) test_otel_instrumentation.py"]
        tests_autonomy_test_parsing_intent_keyword_mapper_py["(原型态 / prototype) test_parsing_intent_keyword_mapper.py"]
        tests_autonomy_test_parsing_intent_parser_py["(原型态 / prototype) test_parsing_intent_parser.py"]
        tests_autonomy_test_pattern_library_root_py["(原型态 / prototype) test_pattern_library_root.py"]
        tests_autonomy_test_poisoning_monitor_py["(原型态 / prototype) test_poisoning_monitor.py"]
        tests_autonomy_test_position_optimizer_py["(原型态 / prototype) test_position_optimizer.py"]
        tests_autonomy_test_progressive_disclosure_injector_py["(原型态 / prototype) test_progressive_disclosure_injector.py"]
        tests_autonomy_test_rational_py["(原型态 / prototype) test_rational.py"]
        tests_autonomy_test_registry_py["(原型态 / prototype) test_registry.py"]
        tests_autonomy_test_sensitivity_classifier_py["(原型态 / prototype) test_sensitivity_classifier.py"]
        tests_autonomy_test_shadow_canary_py["(原型态 / prototype) test_shadow_canary.py"]
        tests_autonomy_test_solo_dev_safety_net_py["(原型态 / prototype) test_solo_dev_safety_net.py"]
        tests_autonomy_test_staleness_manager_py["(原型态 / prototype) test_staleness_manager.py"]
        tests_autonomy_test_support_architecture_context_loader_py["(原型态 / prototype) test_support_architecture_context_loader.py"]
        tests_autonomy_test_support_doc_compressor_py["(原型态 / prototype) test_support_doc_compressor.py"]
        tests_autonomy_test_support_prompt_registry_py["(原型态 / prototype) test_support_prompt_registry.py"]
        tests_autonomy_test_support_system_snapshot_py["(原型态 / prototype) test_support_system_snapshot.py"]
        tests_autonomy_test_system_snapshot_root_py["(原型态 / prototype) test_system_snapshot_root.py"]
        tests_autonomy_test_token_budget_root_py["(原型态 / prototype) test_token_budget_root.py"]
        tests_autonomy_test_trigger_router_root_py["(原型态 / prototype) test_trigger_router_root.py"]
        tests_autonomy_test_vector_bridge_py["(原型态 / prototype) test_vector_bridge.py"]
        tests_autonomy_test_verify_paths_py["(原型态 / prototype) test_verify_paths.py"]
        tests_ba_test_ba_canary_controller_py["(原型态 / prototype) test_ba_canary_controller.py"]
        tests_ba_test_ba_chaos_injector_py["(原型态 / prototype) test_ba_chaos_injector.py"]
        tests_ba_test_ba_dashboard_py["(原型态 / prototype) test_ba_dashboard.py"]
        tests_ba_test_ba_data_lifecycle_py["(原型态 / prototype) test_ba_data_lifecycle.py"]
        tests_ba_test_ba_dependency_manager_py["(原型态 / prototype) test_ba_dependency_manager.py"]
        tests_ba_test_ba_events_py["(原型态 / prototype) test_ba_events.py"]
        tests_ba_test_ba_handoff_manager_py["(原型态 / prototype) test_ba_handoff_manager.py"]
        tests_ba_test_ba_integration_test_runner_py["(原型态 / prototype) test_ba_integration_test_runner.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_autonomy_test_parsing_intent_keyword_mapper_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_autonomy_test_parsing_intent_parser_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_autonomy_test_parsing_intent_parser_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_TELEMETRY["[生产态 / production] D_INFRA_TELEMETRY"]
    tests_autonomy_test_otel_instrumentation_py -.->|测试依赖 / test_depends| D_INFRA_TELEMETRY
    tests_autonomy_test_pattern_library_root_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_autonomy_test_progressive_disclosure_injector_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_rational_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY_LLM["[生产态 / production] D_SECURITY_LLM"]
    tests_autonomy_test_poisoning_monitor_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_autonomy_test_position_optimizer_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_registry_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_shadow_canary_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_autonomy_test_solo_dev_safety_net_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_autonomy_test_sensitivity_classifier_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_autonomy_test_staleness_manager_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_autonomy_test_support_system_snapshot_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_autonomy_test_otel_instrumentation_py,tests_autonomy_test_parsing_intent_keyword_mapper_py,tests_autonomy_test_parsing_intent_parser_py,tests_autonomy_test_pattern_library_root_py,tests_autonomy_test_poisoning_monitor_py,tests_autonomy_test_position_optimizer_py,tests_autonomy_test_progressive_disclosure_injector_py,tests_autonomy_test_rational_py,tests_autonomy_test_registry_py,tests_autonomy_test_sensitivity_classifier_py,tests_autonomy_test_shadow_canary_py,tests_autonomy_test_solo_dev_safety_net_py,tests_autonomy_test_staleness_manager_py,tests_autonomy_test_support_architecture_context_loader_py,tests_autonomy_test_support_doc_compressor_py,tests_autonomy_test_support_prompt_registry_py,tests_autonomy_test_support_system_snapshot_py,tests_autonomy_test_system_snapshot_root_py,tests_autonomy_test_token_budget_root_py,tests_autonomy_test_trigger_router_root_py,tests_autonomy_test_vector_bridge_py,tests_autonomy_test_verify_paths_py,tests_ba_test_ba_canary_controller_py,tests_ba_test_ba_chaos_injector_py,tests_ba_test_ba_dashboard_py,tests_ba_test_ba_data_lifecycle_py,tests_ba_test_ba_dependency_manager_py,tests_ba_test_ba_events_py,tests_ba_test_ba_handoff_manager_py,tests_ba_test_ba_integration_test_runner_py design
    class D_GOVERNANCE,D_INFRA_TELEMETRY,D_AUTONOMY_CORE,D_SECURITY_LLM,D_INFRA_RUNTIME external_prod
```

### 第 11 页 / 共 56 页 / Page 11 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_ba_test_ba_main_py["(原型态 / prototype) test_ba_main.py"]
        tests_ba_test_ba_state_machine_py["(原型态 / prototype) test_ba_state_machine.py"]
        tests_blueprint_test_blueprint_bloat_monitor_py["(原型态 / prototype) test_blueprint_bloat_monitor.py"]
        tests_blueprint_test_blueprint_code_consistency_py["(原型态 / prototype) test_blueprint_code_consistency.py"]
        tests_blueprint_test_blueprint_code_reconciler_py["(原型态 / prototype) test_blueprint_code_reconciler.py"]
        tests_blueprint_test_blueprint_fidelity_py["(原型态 / prototype) test_blueprint_fidelity.py"]
        tests_blueprint_test_blueprint_metrics_py["(原型态 / prototype) test_blueprint_metrics.py"]
        tests_blueprint_test_blueprint_reconciler_py["(原型态 / prototype) test_blueprint_reconciler.py"]
        tests_blueprint_test_blueprint_scorer_py["(原型态 / prototype) test_blueprint_scorer.py"]
        tests_blueprint_test_blueprint_validator_py["(原型态 / prototype) test_blueprint_validator.py"]
        tests_blueprint_test_gen_inherited_py["(原型态 / prototype) test_gen_inherited.py"]
        tests_bridges_test_bridges_anomaly_py["(原型态 / prototype) test_bridges_anomaly.py"]
        tests_bridges_test_bridges_contracts_py["(原型态 / prototype) test_bridges_contracts.py"]
        tests_bridges_test_bridges_delegation_bridge_py["(原型态 / prototype) test_bridges_delegation_bridge.py"]
        tests_bridges_test_bridges_drift_bridge_py["(原型态 / prototype) test_bridges_drift_bridge.py"]
        tests_bridges_test_bridges_feedback_bridge_py["(原型态 / prototype) test_bridges_feedback_bridge.py"]
        tests_bridges_test_bridges_spec_auditor_py["(原型态 / prototype) test_bridges_spec_auditor.py"]
        tests_bridges_test_bridges_tiered_storage_bridge_py["(原型态 / prototype) test_bridges_tiered_storage_bridge.py"]
        tests_bridges_test_bridges_trust_bridge_py["(原型态 / prototype) test_bridges_trust_bridge.py"]
        tests_budget_test_budget_enforcer_rbac_bridge_py["(原型态 / prototype) test_budget_enforcer_rbac_bridge.py"]
        tests_budget_test_budget_engine_root_py["(原型态 / prototype) test_budget_engine_root.py"]
        tests_budget_test_budget_event_driven_py["(原型态 / prototype) test_budget_event_driven.py"]
        tests_budget_test_budget_forecaster_py["(原型态 / prototype) test_budget_forecaster.py"]
        tests_budget_test_budget_handler_py["(原型态 / prototype) test_budget_handler.py"]
        tests_budget_test_budget_lifecycle_e2e_py["(原型态 / prototype) test_budget_lifecycle_e2e.py"]
        tests_budget_test_budget_models_py["(原型态 / prototype) test_budget_models.py"]
        tests_budget_test_budget_profile_manager_py["(原型态 / prototype) test_budget_profile_manager.py"]
        tests_budget_test_budget_shutdown_py["(原型态 / prototype) test_budget_shutdown.py"]
        tests_budget_test_budget_telemetry_bridge_py["(原型态 / prototype) test_budget_telemetry_bridge.py"]
        tests_budget_test_budget_tracker_py["(原型态 / prototype) test_budget_tracker.py"]
    end
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_ba_test_ba_main_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_blueprint_test_blueprint_bloat_monitor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_blueprint_test_blueprint_fidelity_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_blueprint_test_blueprint_code_consistency_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_blueprint_test_blueprint_code_reconciler_py -.->|测试依赖 / test_depends| D_TRADING
    tests_ba_test_ba_state_machine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_ba_test_ba_state_machine_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_blueprint_test_blueprint_reconciler_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_blueprint_test_blueprint_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_blueprint_test_gen_inherited_py -.->|测试依赖 / test_depends| D_TRADING
    tests_blueprint_test_blueprint_scorer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_bridges_test_bridges_delegation_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_bridges_test_bridges_drift_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_bridges_test_bridges_anomaly_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_bridges_test_bridges_spec_auditor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_ba_test_ba_main_py,tests_ba_test_ba_state_machine_py,tests_blueprint_test_blueprint_bloat_monitor_py,tests_blueprint_test_blueprint_code_consistency_py,tests_blueprint_test_blueprint_code_reconciler_py,tests_blueprint_test_blueprint_fidelity_py,tests_blueprint_test_blueprint_metrics_py,tests_blueprint_test_blueprint_reconciler_py,tests_blueprint_test_blueprint_scorer_py,tests_blueprint_test_blueprint_validator_py,tests_blueprint_test_gen_inherited_py,tests_bridges_test_bridges_anomaly_py,tests_bridges_test_bridges_contracts_py,tests_bridges_test_bridges_delegation_bridge_py,tests_bridges_test_bridges_drift_bridge_py,tests_bridges_test_bridges_feedback_bridge_py,tests_bridges_test_bridges_spec_auditor_py,tests_bridges_test_bridges_tiered_storage_bridge_py,tests_bridges_test_bridges_trust_bridge_py,tests_budget_test_budget_enforcer_rbac_bridge_py,tests_budget_test_budget_engine_root_py,tests_budget_test_budget_event_driven_py,tests_budget_test_budget_forecaster_py,tests_budget_test_budget_handler_py,tests_budget_test_budget_lifecycle_e2e_py,tests_budget_test_budget_models_py,tests_budget_test_budget_profile_manager_py,tests_budget_test_budget_shutdown_py,tests_budget_test_budget_telemetry_bridge_py,tests_budget_test_budget_tracker_py design
    class D_AUTONOMY_CORE,D_GOVERNANCE,D_SECURITY,D_TRADING,D_INFRA_RUNTIME external_prod
```

### 第 12 页 / 共 56 页 / Page 12 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_budget_test_error_budget_py["(原型态 / prototype) test_error_budget.py"]
        tests_canary_test_canary_controller_py["(原型态 / prototype) test_canary_controller.py"]
        tests_canary_test_canary_manager_py["(原型态 / prototype) test_canary_manager.py"]
        tests_canary_test_canary_register_py["(原型态 / prototype) test_canary_register.py"]
        tests_canary_test_canary_repair_py["(原型态 / prototype) test_canary_repair.py"]
        tests_canary_test_canary_rollout_manager_py["(原型态 / prototype) test_canary_rollout_manager.py"]
        tests_capability_test_capability_card_py["(原型态 / prototype) test_capability_card.py"]
        tests_capability_test_capability_check_py["(原型态 / prototype) test_capability_check.py"]
        tests_capability_test_capability_lookup_py["(原型态 / prototype) test_capability_lookup.py"]
        tests_capability_test_capability_overlap_gate_py["(原型态 / prototype) test_capability_overlap_gate.py"]
        tests_capability_test_capability_passport_py["(原型态 / prototype) test_capability_passport.py"]
        tests_capability_test_capability_registry_py["(原型态 / prototype) test_capability_registry.py"]
        tests_capability_test_capability_sync_py["(原型态 / prototype) test_capability_sync.py"]
        tests_capacity_test_batch1_infra_py["(原型态 / prototype) test_batch1_infra.py"]
        tests_capacity_test_batch2_governance_py["(原型态 / prototype) test_batch2_governance.py"]
        tests_capacity_test_batch3_integration_py["(原型态 / prototype) test_batch3_integration.py"]
        tests_capacity_test_capacity_assurance_py["(原型态 / prototype) test_capacity_assurance.py"]
        tests_capacity_test_capacity_aware_repair_py["(原型态 / prototype) test_capacity_aware_repair.py"]
        tests_capacity_test_capacity_budget_root_py["(原型态 / prototype) test_capacity_budget_root.py"]
        tests_capacity_test_capacity_forecast_py["(原型态 / prototype) test_capacity_forecast.py"]
        tests_capacity_test_tech_stack_py["(原型态 / prototype) test_tech_stack.py"]
        tests_ce_test_ce_bootstrap_py["(原型态 / prototype) test_ce_bootstrap.py"]
        tests_ce_test_ce_cache_invalidation_py["(原型态 / prototype) test_ce_cache_invalidation.py"]
        tests_ce_test_ce_explain_cli_py["(原型态 / prototype) test_ce_explain_cli.py"]
        tests_ce_test_ce_integrity_check_py["(原型态 / prototype) test_ce_integrity_check.py"]
        tests_ce_test_ce_kill_switch_py["(原型态 / prototype) test_ce_kill_switch.py"]
        tests_ce_test_ce_playground_v2_py["(原型态 / prototype) test_ce_playground_v2.py"]
        tests_ce_test_ce_vibe_shortcuts_py["(原型态 / prototype) test_ce_vibe_shortcuts.py"]
        tests_chaos_test_chaos_engine_py["(原型态 / prototype) test_chaos_engine.py"]
        tests_chaos_test_chaos_engine_ops_py["(原型态 / prototype) test_chaos_engine_ops.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_canary_test_canary_controller_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_budget_test_error_budget_py -.->|测试依赖 / test_depends| D_TRADING
    tests_canary_test_canary_manager_py -.->|测试依赖 / test_depends| D_TRADING
    tests_canary_test_canary_repair_py -.->|测试依赖 / test_depends| D_TRADING
    tests_canary_test_canary_register_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_canary_test_canary_rollout_manager_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_capability_test_capability_card_py -.->|测试依赖 / test_depends| D_TRADING
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_capability_test_capability_check_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_capability_test_capability_check_py -.->|测试依赖 / test_depends| D_SECURITY
    D_INTELLIGENCE["[生产态 / production] D_INTELLIGENCE"]
    tests_capability_test_capability_passport_py -.->|测试依赖 / test_depends| D_INTELLIGENCE
    tests_capability_test_capability_lookup_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_capability_test_capability_registry_py -.->|测试依赖 / test_depends| D_TRADING
    tests_capability_test_capability_registry_py -.->|测试依赖 / test_depends| D_TRADING
    tests_capability_test_capability_overlap_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_capability_test_capability_overlap_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_budget_test_error_budget_py,tests_canary_test_canary_controller_py,tests_canary_test_canary_manager_py,tests_canary_test_canary_register_py,tests_canary_test_canary_repair_py,tests_canary_test_canary_rollout_manager_py,tests_capability_test_capability_card_py,tests_capability_test_capability_check_py,tests_capability_test_capability_lookup_py,tests_capability_test_capability_overlap_gate_py,tests_capability_test_capability_passport_py,tests_capability_test_capability_registry_py,tests_capability_test_capability_sync_py,tests_capacity_test_batch1_infra_py,tests_capacity_test_batch2_governance_py,tests_capacity_test_batch3_integration_py,tests_capacity_test_capacity_assurance_py,tests_capacity_test_capacity_aware_repair_py,tests_capacity_test_capacity_budget_root_py,tests_capacity_test_capacity_forecast_py,tests_capacity_test_tech_stack_py,tests_ce_test_ce_bootstrap_py,tests_ce_test_ce_cache_invalidation_py,tests_ce_test_ce_explain_cli_py,tests_ce_test_ce_integrity_check_py,tests_ce_test_ce_kill_switch_py,tests_ce_test_ce_playground_v2_py,tests_ce_test_ce_vibe_shortcuts_py,tests_chaos_test_chaos_engine_py,tests_chaos_test_chaos_engine_ops_py design
    class D_GOVERNANCE,D_TRADING,D_SECURITY,D_AUTONOMY_CORE,D_INTELLIGENCE external_prod
```

### 第 13 页 / 共 56 页 / Page 13 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_chaos_test_chaos_engineering_py["(原型态 / prototype) test_chaos_engineering.py"]
        tests_chaos_test_chaos_hooks_py["(原型态 / prototype) test_chaos_hooks.py"]
        tests_chaos_test_chaos_injector_py["(原型态 / prototype) test_chaos_injector.py"]
        tests_cold_test_cold_start_py["(原型态 / prototype) test_cold_start.py"]
        tests_cold_test_cold_start_booster_py["(原型态 / prototype) test_cold_start_booster.py"]
        tests_cold_test_cold_start_conservative_mode_py["(原型态 / prototype) test_cold_start_conservative_mode.py"]
        tests_cold_test_cold_start_lock_py["(原型态 / prototype) test_cold_start_lock.py"]
        tests_cold_test_cold_stub_py["(原型态 / prototype) test_cold_stub.py"]
        tests_config_test_config_complexity_budget_py["(原型态 / prototype) test_config_complexity_budget.py"]
        tests_config_test_config_consistency_py["(原型态 / prototype) test_config_consistency.py"]
        tests_config_test_config_drift_py["(原型态 / prototype) test_config_drift.py"]
        tests_config_test_config_fixer_py["(原型态 / prototype) test_config_fixer.py"]
        tests_config_test_config_governance_py["(原型态 / prototype) test_config_governance.py"]
        tests_config_test_config_hot_reload_guard_py["(原型态 / prototype) test_config_hot_reload_guard.py"]
        tests_config_test_config_root_py["(原型态 / prototype) test_config_root.py"]
        tests_config_test_config_safety_guard_py["(原型态 / prototype) test_config_safety_guard.py"]
        tests_config_test_config_scanner_py["(原型态 / prototype) test_config_scanner.py"]
        tests_config_test_config_validator_py["(原型态 / prototype) test_config_validator.py"]
        tests_context_test_context_assembler_root_py["(原型态 / prototype) test_context_assembler_root.py"]
        tests_context_test_context_budget_root_py["(原型态 / prototype) test_context_budget_root.py"]
        tests_context_test_context_budget_tracker_py["(原型态 / prototype) test_context_budget_tracker.py"]
        tests_context_test_context_debt_score_py["(原型态 / prototype) test_context_debt_score.py"]
        tests_context_test_context_drift_detector_py["(原型态 / prototype) test_context_drift_detector.py"]
        tests_context_test_context_evaluator_root_py["(原型态 / prototype) test_context_evaluator_root.py"]
        tests_context_test_context_evictor_root_py["(原型态 / prototype) test_context_evictor_root.py"]
        tests_context_test_context_health_score_py["(原型态 / prototype) test_context_health_score.py"]
        tests_context_test_context_injector_root_py["(原型态 / prototype) test_context_injector_root.py"]
        tests_context_test_context_manager_py["(原型态 / prototype) test_context_manager.py"]
        tests_context_test_context_model_strategy_py["(原型态 / prototype) test_context_model_strategy.py"]
        tests_context_test_context_outcome_tracker_py["(原型态 / prototype) test_context_outcome_tracker.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_chaos_test_chaos_engineering_py -.->|测试依赖 / test_depends| D_TRADING
    tests_chaos_test_chaos_hooks_py -.->|测试依赖 / test_depends| D_TRADING
    tests_chaos_test_chaos_hooks_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_chaos_test_chaos_injector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_cold_test_cold_start_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_cold_test_cold_start_lock_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_cold_test_cold_start_lock_py -.->|测试依赖 / test_depends| D_SECURITY
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_cold_test_cold_start_booster_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_config_test_config_drift_py -.->|测试依赖 / test_depends| D_TRADING
    tests_config_test_config_consistency_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_cold_test_cold_start_conservative_mode_py -.->|测试依赖 / test_depends| D_TRADING
    tests_config_test_config_complexity_budget_py -.->|测试依赖 / test_depends| D_TRADING
    tests_config_test_config_hot_reload_guard_py -.->|测试依赖 / test_depends| D_TRADING
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_config_test_config_safety_guard_py -.->|测试依赖 / test_depends| D_SHARED
    tests_config_test_config_governance_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_chaos_test_chaos_engineering_py,tests_chaos_test_chaos_hooks_py,tests_chaos_test_chaos_injector_py,tests_cold_test_cold_start_py,tests_cold_test_cold_start_booster_py,tests_cold_test_cold_start_conservative_mode_py,tests_cold_test_cold_start_lock_py,tests_cold_test_cold_stub_py,tests_config_test_config_complexity_budget_py,tests_config_test_config_consistency_py,tests_config_test_config_drift_py,tests_config_test_config_fixer_py,tests_config_test_config_governance_py,tests_config_test_config_hot_reload_guard_py,tests_config_test_config_root_py,tests_config_test_config_safety_guard_py,tests_config_test_config_scanner_py,tests_config_test_config_validator_py,tests_context_test_context_assembler_root_py,tests_context_test_context_budget_root_py,tests_context_test_context_budget_tracker_py,tests_context_test_context_debt_score_py,tests_context_test_context_drift_detector_py,tests_context_test_context_evaluator_root_py,tests_context_test_context_evictor_root_py,tests_context_test_context_health_score_py,tests_context_test_context_injector_root_py,tests_context_test_context_manager_py,tests_context_test_context_model_strategy_py,tests_context_test_context_outcome_tracker_py design
    class D_TRADING,D_GOVERNANCE,D_SECURITY,D_AUTONOMY_CORE,D_SHARED external_prod
```

### 第 14 页 / 共 56 页 / Page 14 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_context_test_context_package_py["(原型态 / prototype) test_context_package.py"]
        tests_context_test_context_pipeline_auto_py["(原型态 / prototype) test_context_pipeline_auto.py"]
        tests_context_test_context_pipeline_root_py["(原型态 / prototype) test_context_pipeline_root.py"]
        tests_context_test_context_playground_py["(原型态 / prototype) test_context_playground.py"]
        tests_context_test_context_rot_model_root_py["(原型态 / prototype) test_context_rot_model_root.py"]
        tests_context_test_context_rule_registry_root_py["(原型态 / prototype) test_context_rule_registry_root.py"]
        tests_context_test_context_rule_registry_unit_py["(原型态 / prototype) test_context_rule_registry_unit.py"]
        tests_context_test_context_switch_governor_py["(原型态 / prototype) test_context_switch_governor.py"]
        tests_context_test_context_truncation_py["(原型态 / prototype) test_context_truncation.py"]
        tests_context_test_context_value_attribution_py["(原型态 / prototype) test_context_value_attribution.py"]
        tests_context_test_context_waste_detector_py["(原型态 / prototype) test_context_waste_detector.py"]
        tests_context_test_context_window_contamination_detector_py["(原型态 / prototype) test_context_window_contamination_detector.py"]
        tests_context_test_context_window_pressure_manager_py["(原型态 / prototype) test_context_window_pressure_manager.py"]
        tests_contracts_meta_init_py["(原型态 / prototype) __init__.py"]
        tests_contracts_test_abac_guard_root_py["(原型态 / prototype) test_abac_guard_root.py"]
        tests_contracts_test_alerts_bridge_py["(原型态 / prototype) test_alerts_bridge.py"]
        tests_contracts_test_api_version_contract_py["(原型态 / prototype) test_api_version_contract.py"]
        tests_contracts_test_contract_bus_py["(原型态 / prototype) test_contract_bus.py"]
        tests_contracts_test_contract_consistency_checker_py["(原型态 / prototype) test_contract_consistency_checker.py"]
        tests_contracts_test_contract_drift_detector_py["(原型态 / prototype) test_contract_drift_detector.py"]
        tests_contracts_test_contract_metrics_root_py["(原型态 / prototype) test_contract_metrics_root.py"]
        tests_contracts_test_contract_registry_root_py["(原型态 / prototype) test_contract_registry_root.py"]
        tests_contracts_test_contract_router_root_py["(原型态 / prototype) test_contract_router_root.py"]
        tests_contracts_test_contract_tester_py["(原型态 / prototype) test_contract_tester.py"]
        tests_contracts_test_contract_verifier_py["(原型态 / prototype) test_contract_verifier.py"]
        tests_contracts_test_ct_audit_findings_resolved_py["(原型态 / prototype) test_ct_audit_findings_resolved.py"]
        tests_contracts_test_ct_blueprint_read_check_py["(原型态 / prototype) test_ct_blueprint_read_check.py"]
        tests_contracts_test_ct_circuit_breaker_py["(原型态 / prototype) test_ct_circuit_breaker.py"]
        tests_contracts_test_ct_circular_dependency_scan_py["(原型态 / prototype) test_ct_circular_dependency_scan.py"]
        tests_contracts_test_ct_classification_py["(原型态 / prototype) test_ct_classification.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_context_test_context_package_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_context_test_context_pipeline_auto_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_context_test_context_pipeline_auto_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_context_test_context_pipeline_auto_py -.->|测试依赖 / test_depends| D_SHARED
    tests_context_test_context_pipeline_root_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_pipeline_root_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_rot_model_root_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_playground_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_rule_registry_root_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_rule_registry_unit_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_switch_governor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_context_test_context_window_pressure_manager_py -.->|测试依赖 / test_depends| D_TRADING
    tests_context_test_context_value_attribution_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_context_test_context_truncation_py -.->|测试依赖 / test_depends| D_TRADING
    tests_context_test_context_window_contamination_detector_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_context_test_context_package_py,tests_context_test_context_pipeline_auto_py,tests_context_test_context_pipeline_root_py,tests_context_test_context_playground_py,tests_context_test_context_rot_model_root_py,tests_context_test_context_rule_registry_root_py,tests_context_test_context_rule_registry_unit_py,tests_context_test_context_switch_governor_py,tests_context_test_context_truncation_py,tests_context_test_context_value_attribution_py,tests_context_test_context_waste_detector_py,tests_context_test_context_window_contamination_detector_py,tests_context_test_context_window_pressure_manager_py,tests_contracts_meta_init_py,tests_contracts_test_abac_guard_root_py,tests_contracts_test_alerts_bridge_py,tests_contracts_test_api_version_contract_py,tests_contracts_test_contract_bus_py,tests_contracts_test_contract_consistency_checker_py,tests_contracts_test_contract_drift_detector_py,tests_contracts_test_contract_metrics_root_py,tests_contracts_test_contract_registry_root_py,tests_contracts_test_contract_router_root_py,tests_contracts_test_contract_tester_py,tests_contracts_test_contract_verifier_py,tests_contracts_test_ct_audit_findings_resolved_py,tests_contracts_test_ct_blueprint_read_check_py,tests_contracts_test_ct_circuit_breaker_py,tests_contracts_test_ct_circular_dependency_scan_py,tests_contracts_test_ct_classification_py design
    class D_GOVERNANCE,D_AUTONOMY_CORE,D_INFRA_RUNTIME,D_SHARED,D_TRADING external_prod
```

### 第 15 页 / 共 56 页 / Page 15 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_contracts_test_ct_content_length_py["(原型态 / prototype) test_ct_content_length.py"]
        tests_contracts_test_ct_content_quality_py["(原型态 / prototype) test_ct_content_quality.py"]
        tests_contracts_test_ct_contract_compatibility_check_py["(原型态 / prototype) test_ct_contract_compatibility_check.py"]
        tests_contracts_test_ct_deduplication_py["(原型态 / prototype) test_ct_deduplication.py"]
        tests_contracts_test_ct_drift_budget_py["(原型态 / prototype) test_ct_drift_budget.py"]
        tests_contracts_test_ct_encoding_py["(原型态 / prototype) test_ct_encoding.py"]
        tests_contracts_test_ct_enforcement_mode_check_py["(原型态 / prototype) test_ct_enforcement_mode_check.py"]
        tests_contracts_test_ct_field_presence_py["(原型态 / prototype) test_ct_field_presence.py"]
        tests_contracts_test_ct_file_extension_py["(原型态 / prototype) test_ct_file_extension.py"]
        tests_contracts_test_ct_fle_gate_py["(原型态 / prototype) test_ct_fle_gate.py"]
        tests_contracts_test_ct_frontmatter_py["(原型态 / prototype) test_ct_frontmatter.py"]
        tests_contracts_test_ct_leverage_limit_py["(原型态 / prototype) test_ct_leverage_limit.py"]
        tests_contracts_test_ct_line_ending_py["(原型态 / prototype) test_ct_line_ending.py"]
        tests_contracts_test_ct_manual_approval_py["(原型态 / prototype) test_ct_manual_approval.py"]
        tests_contracts_test_ct_path_blacklist_py["(原型态 / prototype) test_ct_path_blacklist.py"]
        tests_contracts_test_ct_path_routing_py["(原型态 / prototype) test_ct_path_routing.py"]
        tests_contracts_test_ct_path_whitelist_py["(原型态 / prototype) test_ct_path_whitelist.py"]
        tests_contracts_test_ct_pipe_routing_root_py["(原型态 / prototype) test_ct_pipe_routing_root.py"]
        tests_contracts_test_ct_position_limit_py["(原型态 / prototype) test_ct_position_limit.py"]
        tests_contracts_test_ct_reference_check_py["(原型态 / prototype) test_ct_reference_check.py"]
        tests_contracts_test_ct_regex_pattern_py["(原型态 / prototype) test_ct_regex_pattern.py"]
        tests_contracts_test_ct_restructuring_safety_py["(原型态 / prototype) test_ct_restructuring_safety.py"]
        tests_contracts_test_ct_rollback_exit_code_py["(原型态 / prototype) test_ct_rollback_exit_code.py"]
        tests_contracts_test_ct_score_threshold_py["(原型态 / prototype) test_ct_score_threshold.py"]
        tests_contracts_test_ct_security_artifact_scan_py["(原型态 / prototype) test_ct_security_artifact_scan.py"]
        tests_contracts_test_ct_strategy_correlation_py["(原型态 / prototype) test_ct_strategy_correlation.py"]
        tests_contracts_test_ct_temporal_py["(原型态 / prototype) test_ct_temporal.py"]
        tests_contracts_test_ct_zero_residue_check_py["(原型态 / prototype) test_ct_zero_residue_check.py"]
        tests_contracts_test_rbac_guard_root_py["(原型态 / prototype) test_rbac_guard_root.py"]
        tests_cross_test_cross_agent_conflict_detector_py["(原型态 / prototype) test_cross_agent_conflict_detector.py"]
    end
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_contracts_test_ct_deduplication_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_deduplication_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    tests_contracts_test_ct_deduplication_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_contracts_test_ct_content_quality_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_content_quality_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_content_quality_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_contracts_test_ct_field_presence_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_field_presence_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_field_presence_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_contracts_test_ct_drift_budget_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_drift_budget_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_drift_budget_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_contracts_test_ct_enforcement_mode_check_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_enforcement_mode_check_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_contracts_test_ct_enforcement_mode_check_py -.->|测试依赖 / test_depends| D_INTEGRATION
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_contracts_test_ct_content_length_py,tests_contracts_test_ct_content_quality_py,tests_contracts_test_ct_contract_compatibility_check_py,tests_contracts_test_ct_deduplication_py,tests_contracts_test_ct_drift_budget_py,tests_contracts_test_ct_encoding_py,tests_contracts_test_ct_enforcement_mode_check_py,tests_contracts_test_ct_field_presence_py,tests_contracts_test_ct_file_extension_py,tests_contracts_test_ct_fle_gate_py,tests_contracts_test_ct_frontmatter_py,tests_contracts_test_ct_leverage_limit_py,tests_contracts_test_ct_line_ending_py,tests_contracts_test_ct_manual_approval_py,tests_contracts_test_ct_path_blacklist_py,tests_contracts_test_ct_path_routing_py,tests_contracts_test_ct_path_whitelist_py,tests_contracts_test_ct_pipe_routing_root_py,tests_contracts_test_ct_position_limit_py,tests_contracts_test_ct_reference_check_py,tests_contracts_test_ct_regex_pattern_py,tests_contracts_test_ct_restructuring_safety_py,tests_contracts_test_ct_rollback_exit_code_py,tests_contracts_test_ct_score_threshold_py,tests_contracts_test_ct_security_artifact_scan_py,tests_contracts_test_ct_strategy_correlation_py,tests_contracts_test_ct_temporal_py,tests_contracts_test_ct_zero_residue_check_py,tests_contracts_test_rbac_guard_root_py,tests_cross_test_cross_agent_conflict_detector_py design
    class D_GOV_ENFORCEMENT,D_INTEGRATION external_prod
```

### 第 16 页 / 共 56 页 / Page 16 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_cross_test_cross_assistant_adapter_py["(原型态 / prototype) test_cross_assistant_adapter.py"]
        tests_cross_test_cross_blueprint_contract_drift_py["(原型态 / prototype) test_cross_blueprint_contract_drift.py"]
        tests_cross_test_cross_boundary_detector_py["(原型态 / prototype) test_cross_boundary_detector.py"]
        tests_cross_test_cross_cutting_py["(原型态 / prototype) test_cross_cutting.py"]
        tests_cross_test_cross_env_consistency_py["(原型态 / prototype) test_cross_env_consistency.py"]
        tests_cross_test_cross_gen_validation_py["(原型态 / prototype) test_cross_gen_validation.py"]
        tests_cross_test_cross_guard_conflict_detector_py["(原型态 / prototype) test_cross_guard_conflict_detector.py"]
        tests_cross_test_cross_layer_py["(原型态 / prototype) test_cross_layer.py"]
        tests_cross_test_cross_module_integration_root_py["(原型态 / prototype) test_cross_module_integration_root.py"]
        tests_cross_test_cross_module_score_py["(原型态 / prototype) test_cross_module_score.py"]
        tests_cross_test_cross_platform_shell_py["(原型态 / prototype) test_cross_platform_shell.py"]
        tests_cross_test_cross_session_consistency_validator_py["(原型态 / prototype) test_cross_session_consistency_validator.py"]
        tests_cross_test_cross_session_correlator_py["(原型态 / prototype) test_cross_session_correlator.py"]
        tests_cross_test_cross_session_detector_py["(原型态 / prototype) test_cross_session_detector.py"]
        tests_cross_test_cross_session_knowledge_integrity_py["(原型态 / prototype) test_cross_session_knowledge_integrity.py"]
        tests_cross_test_cross_signal_validator_py["(原型态 / prototype) test_cross_signal_validator.py"]
        tests_cross_test_cross_system_correlator_py["(原型态 / prototype) test_cross_system_correlator.py"]
        tests_data_test_data_lifecycle_py["(原型态 / prototype) test_data_lifecycle.py"]
        tests_data_test_data_pipeline_guard_py["(原型态 / prototype) test_data_pipeline_guard.py"]
        tests_data_test_data_quality_gate_py["(原型态 / prototype) test_data_quality_gate.py"]
        tests_data_test_data_source_reliability_py["(原型态 / prototype) test_data_source_reliability.py"]
        tests_data_test_data_volume_growth_monitor_py["(原型态 / prototype) test_data_volume_growth_monitor.py"]
        tests_db_test_db_auto_ops_py["(原型态 / prototype) test_db_auto_ops.py"]
        tests_db_test_db_bridge_py["(原型态 / prototype) test_db_bridge.py"]
        tests_db_test_db_integration_py["(原型态 / prototype) test_db_integration.py"]
        tests_db_test_db_integrity_py["(原型态 / prototype) test_db_integrity.py"]
        tests_db_test_db_query_py["(原型态 / prototype) test_db_query.py"]
        tests_db_test_db_red_blue_py["(原型态 / prototype) test_db_red_blue.py"]
        tests_db_test_db_transition_py["(原型态 / prototype) test_db_transition.py"]
        tests_db_test_dm400_stale_task_fix_py["(原型态 / prototype) test_dm400_stale_task_fix.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_cross_test_cross_boundary_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_cross_test_cross_blueprint_contract_drift_py -.->|测试依赖 / test_depends| D_TRADING
    tests_cross_test_cross_assistant_adapter_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_cross_test_cross_module_integration_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_cross_test_cross_gen_validation_py -.->|测试依赖 / test_depends| D_TRADING
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_cross_test_cross_platform_shell_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_cross_test_cross_cutting_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_cross_test_cross_module_score_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_cross_test_cross_guard_conflict_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_cross_test_cross_session_consistency_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_cross_test_cross_session_detector_py -.->|测试依赖 / test_depends| D_SECURITY
    D_INTELLIGENCE["[生产态 / production] D_INTELLIGENCE"]
    tests_cross_test_cross_layer_py -.->|测试依赖 / test_depends| D_INTELLIGENCE
    D_SIMULATION["[生产态 / production] D_SIMULATION"]
    tests_cross_test_cross_layer_py -.->|测试依赖 / test_depends| D_SIMULATION
    D_FUNDAMENTAL_SIGNAL["[生产态 / production] D_FUNDAMENTAL_SIGNAL"]
    tests_cross_test_cross_layer_py -.->|测试依赖 / test_depends| D_FUNDAMENTAL_SIGNAL
    tests_cross_test_cross_system_correlator_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_cross_test_cross_assistant_adapter_py,tests_cross_test_cross_blueprint_contract_drift_py,tests_cross_test_cross_boundary_detector_py,tests_cross_test_cross_cutting_py,tests_cross_test_cross_env_consistency_py,tests_cross_test_cross_gen_validation_py,tests_cross_test_cross_guard_conflict_detector_py,tests_cross_test_cross_layer_py,tests_cross_test_cross_module_integration_root_py,tests_cross_test_cross_module_score_py,tests_cross_test_cross_platform_shell_py,tests_cross_test_cross_session_consistency_validator_py,tests_cross_test_cross_session_correlator_py,tests_cross_test_cross_session_detector_py,tests_cross_test_cross_session_knowledge_integrity_py,tests_cross_test_cross_signal_validator_py,tests_cross_test_cross_system_correlator_py,tests_data_test_data_lifecycle_py,tests_data_test_data_pipeline_guard_py,tests_data_test_data_quality_gate_py,tests_data_test_data_source_reliability_py,tests_data_test_data_volume_growth_monitor_py,tests_db_test_db_auto_ops_py,tests_db_test_db_bridge_py,tests_db_test_db_integration_py,tests_db_test_db_integrity_py,tests_db_test_db_query_py,tests_db_test_db_red_blue_py,tests_db_test_db_transition_py,tests_db_test_dm400_stale_task_fix_py design
    class D_GOVERNANCE,D_TRADING,D_INFRA_RECOVERY,D_SECURITY,D_INTELLIGENCE,D_SIMULATION,D_FUNDAMENTAL_SIGNAL external_prod
```

### 第 17 页 / 共 56 页 / Page 17 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_decision_test_decision_auditor_py["(原型态 / prototype) test_decision_auditor.py"]
        tests_decision_test_decision_engine_py["(原型态 / prototype) test_decision_engine.py"]
        tests_decision_test_decision_explainer_root_py["(原型态 / prototype) test_decision_explainer_root.py"]
        tests_decision_test_decision_provenance_py["(原型态 / prototype) test_decision_provenance.py"]
        tests_decision_test_decision_registry_py["(原型态 / prototype) test_decision_registry.py"]
        tests_dependency_test_dependency_auditor_py["(原型态 / prototype) test_dependency_auditor.py"]
        tests_dependency_test_dependency_freshness_monitor_py["(原型态 / prototype) test_dependency_freshness_monitor.py"]
        tests_dependency_test_dependency_lock_py["(原型态 / prototype) test_dependency_lock.py"]
        tests_dependency_test_dependency_manager_py["(原型态 / prototype) test_dependency_manager.py"]
        tests_dependency_test_dependency_root_py["(原型态 / prototype) test_dependency_root.py"]
        tests_dependency_test_dependency_tracker_py["(原型态 / prototype) test_dependency_tracker.py"]
        tests_drift_test_concept_drift_py["(原型态 / prototype) test_concept_drift.py"]
        tests_drift_test_drift_bridge_py["(原型态 / prototype) test_drift_bridge.py"]
        tests_drift_test_drift_detector_ee_py["(原型态 / prototype) test_drift_detector_ee.py"]
        tests_drift_test_drift_detector_gate_py["(原型态 / prototype) test_drift_detector_gate.py"]
        tests_drift_test_drift_engine_py["(原型态 / prototype) test_drift_engine.py"]
        tests_drift_test_drift_fix_py["(原型态 / prototype) test_drift_fix.py"]
        tests_drift_test_drift_fixer_py["(原型态 / prototype) test_drift_fixer.py"]
        tests_drift_test_drift_hotfix_bypass_py["(原型态 / prototype) test_drift_hotfix_bypass.py"]
        tests_drift_test_drift_infrastructure_py["(原型态 / prototype) test_drift_infrastructure.py"]
        tests_drift_test_drift_models_py["(原型态 / prototype) test_drift_models.py"]
        tests_drift_test_drift_result_types_py["(原型态 / prototype) test_drift_result_types.py"]
        tests_drift_test_drift_training_py["(原型态 / prototype) test_drift_training.py"]
        tests_drift_test_schema_evolution_root_py["(原型态 / prototype) test_schema_evolution_root.py"]
        tests_drift_test_version_migrator_py["(原型态 / prototype) test_version_migrator.py"]
        tests_e_test_e_circuit_breaker_py["(原型态 / prototype) test_e_circuit_breaker.py"]
        tests_e_test_e_clock_guard_py["(原型态 / prototype) test_e_clock_guard.py"]
        tests_e_test_e_confidence_estimator_py["(原型态 / prototype) test_e_confidence_estimator.py"]
        tests_e_test_e_consequence_manager_py["(原型态 / prototype) test_e_consequence_manager.py"]
        tests_e_test_e_context_package_py["(原型态 / prototype) test_e_context_package.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_decision_test_decision_auditor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_decision_test_decision_registry_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_decision_test_decision_explainer_root_py -.->|测试依赖 / test_depends| D_SECURITY
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_decision_test_decision_provenance_py -.->|测试依赖 / test_depends| D_TRADING
    tests_dependency_test_dependency_auditor_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_decision_test_decision_engine_py -.->|测试依赖 / test_depends| D_TRADING
    tests_decision_test_decision_engine_py -.->|测试依赖 / test_depends| D_TRADING
    tests_dependency_test_dependency_lock_py -.->|测试依赖 / test_depends| D_TRADING
    tests_dependency_test_dependency_freshness_monitor_py -.->|测试依赖 / test_depends| D_TRADING
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_dependency_test_dependency_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_dependency_test_dependency_tracker_py -.->|测试依赖 / test_depends| D_SHARED
    tests_drift_test_drift_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_drift_test_concept_drift_py -.->|测试依赖 / test_depends| D_TRADING
    tests_drift_test_drift_detector_ee_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_drift_test_drift_detector_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_decision_test_decision_auditor_py,tests_decision_test_decision_engine_py,tests_decision_test_decision_explainer_root_py,tests_decision_test_decision_provenance_py,tests_decision_test_decision_registry_py,tests_dependency_test_dependency_auditor_py,tests_dependency_test_dependency_freshness_monitor_py,tests_dependency_test_dependency_lock_py,tests_dependency_test_dependency_manager_py,tests_dependency_test_dependency_root_py,tests_dependency_test_dependency_tracker_py,tests_drift_test_concept_drift_py,tests_drift_test_drift_bridge_py,tests_drift_test_drift_detector_ee_py,tests_drift_test_drift_detector_gate_py,tests_drift_test_drift_engine_py,tests_drift_test_drift_fix_py,tests_drift_test_drift_fixer_py,tests_drift_test_drift_hotfix_bypass_py,tests_drift_test_drift_infrastructure_py,tests_drift_test_drift_models_py,tests_drift_test_drift_result_types_py,tests_drift_test_drift_training_py,tests_drift_test_schema_evolution_root_py,tests_drift_test_version_migrator_py,tests_e_test_e_circuit_breaker_py,tests_e_test_e_clock_guard_py,tests_e_test_e_confidence_estimator_py,tests_e_test_e_consequence_manager_py,tests_e_test_e_context_package_py design
    class D_GOVERNANCE,D_SECURITY,D_TRADING,D_INFRA_RUNTIME,D_SHARED external_prod
```

### 第 18 页 / 共 56 页 / Page 18 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_e_test_e_deadlock_detector_py["(原型态 / prototype) test_e_deadlock_detector.py"]
        tests_e_test_e_decision_fatigue_py["(原型态 / prototype) test_e_decision_fatigue.py"]
        tests_e_test_e_error_budget_burst_limiter_py["(原型态 / prototype) test_e_error_budget_burst_limiter.py"]
        tests_e_test_e_escalation_api_py["(原型态 / prototype) test_e_escalation_api.py"]
        tests_e_test_e_escalation_metrics_py["(原型态 / prototype) test_e_escalation_metrics.py"]
        tests_e_test_e_escalation_models_py["(原型态 / prototype) test_e_escalation_models.py"]
        tests_e_test_e_exchange_partition_detector_py["(原型态 / prototype) test_e_exchange_partition_detector.py"]
        tests_e_test_e_flash_crash_guard_py["(原型态 / prototype) test_e_flash_crash_guard.py"]
        tests_e_test_e_forensic_package_py["(原型态 / prototype) test_e_forensic_package.py"]
        tests_e_test_e_gap_analyzer_py["(原型态 / prototype) test_e_gap_analyzer.py"]
        tests_e_test_e_ghost_scan_py["(原型态 / prototype) test_e_ghost_scan.py"]
        tests_e_test_e_gov_a2a_failure_py["(原型态 / prototype) test_e_gov_a2a_failure.py"]
        tests_e_test_e_gov_approval_py["(原型态 / prototype) test_e_gov_approval.py"]
        tests_e_test_e_gov_budget_handler_py["(原型态 / prototype) test_e_gov_budget_handler.py"]
        tests_e_test_e_gov_contracts_py["(原型态 / prototype) test_e_gov_contracts.py"]
        tests_e_test_e_gov_rbac_bridge_py["(原型态 / prototype) test_e_gov_rbac_bridge.py"]
        tests_e_test_e_identity_verifier_py["(原型态 / prototype) test_e_identity_verifier.py"]
        tests_e_test_e_integrity_verifier_py["(原型态 / prototype) test_e_integrity_verifier.py"]
        tests_e_test_e_interrupt_handler_py["(原型态 / prototype) test_e_interrupt_handler.py"]
        tests_e_test_e_merkle_audit_py["(原型态 / prototype) test_e_merkle_audit.py"]
        tests_e_test_e_meta_confidence_py["(原型态 / prototype) test_e_meta_confidence.py"]
        tests_e_test_e_objective_tracker_py["(原型态 / prototype) test_e_objective_tracker.py"]
        tests_e_test_e_position_reconciler_py["(原型态 / prototype) test_e_position_reconciler.py"]
        tests_e_test_e_protocol_state_store_py["(原型态 / prototype) test_e_protocol_state_store.py"]
        tests_e_test_e_reward_hacking_py["(原型态 / prototype) test_e_reward_hacking.py"]
        tests_e_test_e_risk_matrix_py["(原型态 / prototype) test_e_risk_matrix.py"]
        tests_e_test_e_self_test_py["(原型态 / prototype) test_e_self_test.py"]
        tests_e_test_e_self_validator_py["(原型态 / prototype) test_e_self_validator.py"]
        tests_e_test_e_silence_detector_py["(原型态 / prototype) test_e_silence_detector.py"]
        tests_e_test_e_slo_contract_py["(原型态 / prototype) test_e_slo_contract.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_e_test_e_deadlock_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_escalation_metrics_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_error_budget_burst_limiter_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_escalation_api_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_escalation_models_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_exchange_partition_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_flash_crash_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_ghost_scan_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_gov_a2a_failure_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_forensic_package_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_gap_analyzer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_e_test_e_decision_fatigue_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_e_test_e_gov_approval_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_e_test_e_gov_budget_handler_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_e_test_e_gov_budget_handler_py -.->|测试依赖 / test_depends| D_SHARED
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_e_test_e_deadlock_detector_py,tests_e_test_e_decision_fatigue_py,tests_e_test_e_error_budget_burst_limiter_py,tests_e_test_e_escalation_api_py,tests_e_test_e_escalation_metrics_py,tests_e_test_e_escalation_models_py,tests_e_test_e_exchange_partition_detector_py,tests_e_test_e_flash_crash_guard_py,tests_e_test_e_forensic_package_py,tests_e_test_e_gap_analyzer_py,tests_e_test_e_ghost_scan_py,tests_e_test_e_gov_a2a_failure_py,tests_e_test_e_gov_approval_py,tests_e_test_e_gov_budget_handler_py,tests_e_test_e_gov_contracts_py,tests_e_test_e_gov_rbac_bridge_py,tests_e_test_e_identity_verifier_py,tests_e_test_e_integrity_verifier_py,tests_e_test_e_interrupt_handler_py,tests_e_test_e_merkle_audit_py,tests_e_test_e_meta_confidence_py,tests_e_test_e_objective_tracker_py,tests_e_test_e_position_reconciler_py,tests_e_test_e_protocol_state_store_py,tests_e_test_e_reward_hacking_py,tests_e_test_e_risk_matrix_py,tests_e_test_e_self_test_py,tests_e_test_e_self_validator_py,tests_e_test_e_silence_detector_py,tests_e_test_e_slo_contract_py design
    class D_GOVERNANCE,D_GOV_ENFORCEMENT,D_SHARED external_prod
```

### 第 19 页 / 共 56 页 / Page 19 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_e_test_e_strategy_portfolio_py["(原型态 / prototype) test_e_strategy_portfolio.py"]
        tests_e_test_e_strategy_scoper_py["(原型态 / prototype) test_e_strategy_scoper.py"]
        tests_escalation_conftest_py["(原型态 / prototype) conftest.py"]
        tests_escalation_test_escalation_adapter_py["(原型态 / prototype) test_escalation_adapter.py"]
        tests_escalation_test_escalation_api_py["(原型态 / prototype) test_escalation_api.py"]
        tests_escalation_test_escalation_bridge_py["(原型态 / prototype) test_escalation_bridge.py"]
        tests_escalation_test_escalation_contracts_py["(原型态 / prototype) test_escalation_contracts.py"]
        tests_escalation_test_escalation_fatigue_manager_py["(原型态 / prototype) test_escalation_fatigue_manager.py"]
        tests_escalation_test_escalation_gov_a2a_failure_py["(原型态 / prototype) test_escalation_gov_a2a_failure.py"]
        tests_escalation_test_escalation_gov_approval_py["(原型态 / prototype) test_escalation_gov_approval.py"]
        tests_escalation_test_escalation_gov_budget_handler_py["(原型态 / prototype) test_escalation_gov_budget_handler.py"]
        tests_escalation_test_escalation_gov_contracts_py["(原型态 / prototype) test_escalation_gov_contracts.py"]
        tests_escalation_test_escalation_gov_rbac_bridge_py["(原型态 / prototype) test_escalation_gov_rbac_bridge.py"]
        tests_escalation_test_escalation_handler_py["(原型态 / prototype) test_escalation_handler.py"]
        tests_escalation_test_escalation_incident_response_py["(原型态 / prototype) test_escalation_incident_response.py"]
        tests_escalation_test_escalation_loop_detector_py["(原型态 / prototype) test_escalation_loop_detector.py"]
        tests_escalation_test_escalation_metrics_py["(原型态 / prototype) test_escalation_metrics.py"]
        tests_escalation_test_escalation_models_py["(原型态 / prototype) test_escalation_models.py"]
        tests_escalation_test_escalation_smoke_tests_py["(原型态 / prototype) test_escalation_smoke_tests.py"]
        tests_escalation_test_incident_priority_triage_automator_py["(原型态 / prototype) test_incident_priority_triage_automator.py"]
        tests_escalation_test_order_state_escalator_py["(原型态 / prototype) test_order_state_escalator.py"]
        tests_escalation_test_owner_absence_escalation_py["(原型态 / prototype) test_owner_absence_escalation.py"]
        tests_event_test_event_bus_upgrade_py["(原型态 / prototype) test_event_bus_upgrade.py"]
        tests_event_test_event_hook_py["(原型态 / prototype) test_event_hook.py"]
        tests_event_test_event_hooks_py["(原型态 / prototype) test_event_hooks.py"]
        tests_event_test_event_sink_py["(原型态 / prototype) test_event_sink.py"]
        tests_event_test_event_store_py["(原型态 / prototype) test_event_store.py"]
        tests_event_test_event_store_stress_py["(原型态 / prototype) test_event_store_stress.py"]
        tests_external_test_external_health_py["(原型态 / prototype) test_external_health.py"]
        tests_external_test_external_merkle_proof_py["(原型态 / prototype) test_external_merkle_proof.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_e_test_e_strategy_scoper_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_escalation_test_escalation_api_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_escalation_test_escalation_adapter_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_escalation_test_escalation_fatigue_manager_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_escalation_test_escalation_bridge_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_escalation_test_escalation_bridge_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_escalation_test_escalation_gov_approval_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_escalation_test_escalation_gov_budget_handler_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_escalation_test_escalation_gov_budget_handler_py -.->|测试依赖 / test_depends| D_SHARED
    tests_escalation_test_escalation_contracts_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_escalation_test_escalation_contracts_py -.->|测试依赖 / test_depends| D_SHARED
    tests_escalation_test_escalation_gov_a2a_failure_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_escalation_test_escalation_handler_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_escalation_test_escalation_loop_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_escalation_test_escalation_gov_contracts_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_e_test_e_strategy_portfolio_py,tests_e_test_e_strategy_scoper_py,tests_escalation_conftest_py,tests_escalation_test_escalation_adapter_py,tests_escalation_test_escalation_api_py,tests_escalation_test_escalation_bridge_py,tests_escalation_test_escalation_contracts_py,tests_escalation_test_escalation_fatigue_manager_py,tests_escalation_test_escalation_gov_a2a_failure_py,tests_escalation_test_escalation_gov_approval_py,tests_escalation_test_escalation_gov_budget_handler_py,tests_escalation_test_escalation_gov_contracts_py,tests_escalation_test_escalation_gov_rbac_bridge_py,tests_escalation_test_escalation_handler_py,tests_escalation_test_escalation_incident_response_py,tests_escalation_test_escalation_loop_detector_py,tests_escalation_test_escalation_metrics_py,tests_escalation_test_escalation_models_py,tests_escalation_test_escalation_smoke_tests_py,tests_escalation_test_incident_priority_triage_automator_py,tests_escalation_test_order_state_escalator_py,tests_escalation_test_owner_absence_escalation_py,tests_event_test_event_bus_upgrade_py,tests_event_test_event_hook_py,tests_event_test_event_hooks_py,tests_event_test_event_sink_py,tests_event_test_event_store_py,tests_event_test_event_store_stress_py,tests_external_test_external_health_py,tests_external_test_external_merkle_proof_py design
    class D_GOVERNANCE,D_INFRA_RUNTIME,D_GOV_ENFORCEMENT,D_SHARED,D_SECURITY external_prod
```

### 第 20 页 / 共 56 页 / Page 20 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_external_test_external_tool_audit_py["(原型态 / prototype) test_external_tool_audit.py"]
        tests_external_test_external_validation_checkpoint_py["(原型态 / prototype) test_external_validation_checkpoint.py"]
        tests_external_test_external_verifier_py["(原型态 / prototype) test_external_verifier.py"]
        tests_f_lifecycle_test_f10_red_blue_py["(原型态 / prototype) test_f10_red_blue.py"]
        tests_f_lifecycle_test_f18_automation_py["(原型态 / prototype) test_f18_automation.py"]
        tests_f_lifecycle_test_f18_redblue_py["(原型态 / prototype) test_f18_redblue.py"]
        tests_f_lifecycle_test_f1_event_trigger_py["(原型态 / prototype) test_f1_event_trigger.py"]
        tests_f_lifecycle_test_f21_auto_run_py["(原型态 / prototype) test_f21_auto_run.py"]
        tests_f_lifecycle_test_f21_auto_shutdown_py["(原型态 / prototype) test_f21_auto_shutdown.py"]
        tests_f_lifecycle_test_f21_auto_startup_py["(原型态 / prototype) test_f21_auto_startup.py"]
        tests_f_lifecycle_test_f21_event_driven_py["(原型态 / prototype) test_f21_event_driven.py"]
        tests_f_lifecycle_test_f5_auto_shutdown_py["(原型态 / prototype) test_f5_auto_shutdown.py"]
        tests_f_lifecycle_test_f5_auto_startup_py["(原型态 / prototype) test_f5_auto_startup.py"]
        tests_f_lifecycle_test_f5_e2e_lifecycle_py["(原型态 / prototype) test_f5_e2e_lifecycle.py"]
        tests_f_lifecycle_test_f5_event_startup_py["(原型态 / prototype) test_f5_event_startup.py"]
        tests_f_lifecycle_test_f5_red_team_extreme_py["(原型态 / prototype) test_f5_red_team_extreme.py"]
        tests_f_lifecycle_test_flag_lifecycle_py["(原型态 / prototype) test_flag_lifecycle.py"]
        tests_f_lifecycle_test_lifecycle_hooks_py["(原型态 / prototype) test_lifecycle_hooks.py"]
        tests_f_lifecycle_test_openfeature_py["(原型态 / prototype) test_openfeature.py"]
        tests_federated_learning_test_fl_action_reversibility_py["(原型态 / prototype) test_fl_action_reversibility.py"]
        tests_federated_learning_test_fl_action_selector_py["(原型态 / prototype) test_fl_action_selector.py"]
        tests_federated_learning_test_fl_adversarial_validation_py["(原型态 / prototype) test_fl_adversarial_validation.py"]
        tests_federated_learning_test_fl_agent_lifecycle_py["(原型态 / prototype) test_fl_agent_lifecycle.py"]
        tests_federated_learning_test_fl_anomaly_detector_py["(原型态 / prototype) test_fl_anomaly_detector.py"]
        tests_federated_learning_test_fl_api_version_contract_py["(原型态 / prototype) test_fl_api_version_contract.py"]
        tests_federated_learning_test_fl_auto_evolution_py["(原型态 / prototype) test_fl_auto_evolution.py"]
        tests_federated_learning_test_fl_autonomy_credit_py["(原型态 / prototype) test_fl_autonomy_credit.py"]
        tests_federated_learning_test_fl_autonomy_maturity_py["(原型态 / prototype) test_fl_autonomy_maturity.py"]
        tests_federated_learning_test_fl_backpressure_bridge_py["(原型态 / prototype) test_fl_backpressure_bridge.py"]
        tests_federated_learning_test_fl_blueprint_code_reconciler_py["(原型态 / prototype) test_fl_blueprint_code_reconciler.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_external_test_external_verifier_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_api_version_contract_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_federated_learning_test_fl_adversarial_validation_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_federated_learning_test_fl_action_reversibility_py -.->|测试依赖 / test_depends| D_TRADING
    tests_external_test_external_validation_checkpoint_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_autonomy_credit_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_external_test_external_tool_audit_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_federated_learning_test_fl_agent_lifecycle_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_action_selector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_action_selector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_backpressure_bridge_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_backpressure_bridge_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_auto_evolution_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_auto_evolution_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_blueprint_code_reconciler_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_external_test_external_tool_audit_py,tests_external_test_external_validation_checkpoint_py,tests_external_test_external_verifier_py,tests_f_lifecycle_test_f10_red_blue_py,tests_f_lifecycle_test_f18_automation_py,tests_f_lifecycle_test_f18_redblue_py,tests_f_lifecycle_test_f1_event_trigger_py,tests_f_lifecycle_test_f21_auto_run_py,tests_f_lifecycle_test_f21_auto_shutdown_py,tests_f_lifecycle_test_f21_auto_startup_py,tests_f_lifecycle_test_f21_event_driven_py,tests_f_lifecycle_test_f5_auto_shutdown_py,tests_f_lifecycle_test_f5_auto_startup_py,tests_f_lifecycle_test_f5_e2e_lifecycle_py,tests_f_lifecycle_test_f5_event_startup_py,tests_f_lifecycle_test_f5_red_team_extreme_py,tests_f_lifecycle_test_flag_lifecycle_py,tests_f_lifecycle_test_lifecycle_hooks_py,tests_f_lifecycle_test_openfeature_py,tests_federated_learning_test_fl_action_reversibility_py,tests_federated_learning_test_fl_action_selector_py,tests_federated_learning_test_fl_adversarial_validation_py,tests_federated_learning_test_fl_agent_lifecycle_py,tests_federated_learning_test_fl_anomaly_detector_py,tests_federated_learning_test_fl_api_version_contract_py,tests_federated_learning_test_fl_auto_evolution_py,tests_federated_learning_test_fl_autonomy_credit_py,tests_federated_learning_test_fl_autonomy_maturity_py,tests_federated_learning_test_fl_backpressure_bridge_py,tests_federated_learning_test_fl_blueprint_code_reconciler_py design
    class D_TRADING,D_GOV_ENFORCEMENT,D_GOVERNANCE external_prod
```

### 第 21 页 / 共 56 页 / Page 21 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_federated_learning_test_fl_blueprint_validator_py["(原型态 / prototype) test_fl_blueprint_validator.py"]
        tests_federated_learning_test_fl_calendar_adapter_py["(原型态 / prototype) test_fl_calendar_adapter.py"]
        tests_federated_learning_test_fl_checkpoint_manager_py["(原型态 / prototype) test_fl_checkpoint_manager.py"]
        tests_federated_learning_test_fl_ci_cd_pre_scanner_py["(原型态 / prototype) test_fl_ci_cd_pre_scanner.py"]
        tests_federated_learning_test_fl_concurrent_change_deconfliction_py["(原型态 / prototype) test_fl_concurrent_change_deconfliction.py"]
        tests_federated_learning_test_fl_config_py["(原型态 / prototype) test_fl_config.py"]
        tests_federated_learning_test_fl_config_complexity_budget_py["(原型态 / prototype) test_fl_config_complexity_budget.py"]
        tests_federated_learning_test_fl_config_governance_py["(原型态 / prototype) test_fl_config_governance.py"]
        tests_federated_learning_test_fl_config_timeline_py["(原型态 / prototype) test_fl_config_timeline.py"]
        tests_federated_learning_test_fl_conflict_arbitration_py["(原型态 / prototype) test_fl_conflict_arbitration.py"]
        tests_federated_learning_test_fl_cve_scanner_py["(原型态 / prototype) test_fl_cve_scanner.py"]
        tests_federated_learning_test_fl_data_quality_gate_py["(原型态 / prototype) test_fl_data_quality_gate.py"]
        tests_federated_learning_test_fl_data_quality_validator_py["(原型态 / prototype) test_fl_data_quality_validator.py"]
        tests_federated_learning_test_fl_db_bridge_py["(原型态 / prototype) test_fl_db_bridge.py"]
        tests_federated_learning_test_fl_db_integrity_py["(原型态 / prototype) test_fl_db_integrity.py"]
        tests_federated_learning_test_fl_decision_engine_py["(原型态 / prototype) test_fl_decision_engine.py"]
        tests_federated_learning_test_fl_deployment_suppression_py["(原型态 / prototype) test_fl_deployment_suppression.py"]
        tests_federated_learning_test_fl_dynamic_llm_cost_router_py["(原型态 / prototype) test_fl_dynamic_llm_cost_router.py"]
        tests_federated_learning_test_fl_emergency_takeover_py["(原型态 / prototype) test_fl_emergency_takeover.py"]
        tests_federated_learning_test_fl_error_budget_py["(原型态 / prototype) test_fl_error_budget.py"]
        tests_federated_learning_test_fl_eval_harness_py["(原型态 / prototype) test_fl_eval_harness.py"]
        tests_federated_learning_test_fl_evolution_engine_py["(原型态 / prototype) test_fl_evolution_engine.py"]
        tests_federated_learning_test_fl_exceptions_py["(原型态 / prototype) test_fl_exceptions.py"]
        tests_federated_learning_test_fl_federated_security_py["(原型态 / prototype) test_fl_federated_security.py"]
        tests_federated_learning_test_fl_financial_stratification_py["(原型态 / prototype) test_fl_financial_stratification.py"]
        tests_federated_learning_test_fl_fitness_functions_py["(原型态 / prototype) test_fl_fitness_functions.py"]
        tests_federated_learning_test_fl_flag_lifecycle_manager_py["(原型态 / prototype) test_fl_flag_lifecycle_manager.py"]
        tests_federated_learning_test_fl_generator_py["(原型态 / prototype) test_fl_generator.py"]
        tests_federated_learning_test_fl_global_action_scheduler_py["(原型态 / prototype) test_fl_global_action_scheduler.py"]
        tests_federated_learning_test_fl_incident_priority_triage_automator_py["(原型态 / prototype) test_fl_incident_priority_triage_automator.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_federated_learning_test_fl_calendar_adapter_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_checkpoint_manager_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_blueprint_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_ci_cd_pre_scanner_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_config_complexity_budget_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_concurrent_change_deconfliction_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_config_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_config_timeline_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_conflict_arbitration_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_db_integrity_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_data_quality_gate_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_config_governance_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_db_bridge_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_cve_scanner_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_data_quality_validator_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_federated_learning_test_fl_blueprint_validator_py,tests_federated_learning_test_fl_calendar_adapter_py,tests_federated_learning_test_fl_checkpoint_manager_py,tests_federated_learning_test_fl_ci_cd_pre_scanner_py,tests_federated_learning_test_fl_concurrent_change_deconfliction_py,tests_federated_learning_test_fl_config_py,tests_federated_learning_test_fl_config_complexity_budget_py,tests_federated_learning_test_fl_config_governance_py,tests_federated_learning_test_fl_config_timeline_py,tests_federated_learning_test_fl_conflict_arbitration_py,tests_federated_learning_test_fl_cve_scanner_py,tests_federated_learning_test_fl_data_quality_gate_py,tests_federated_learning_test_fl_data_quality_validator_py,tests_federated_learning_test_fl_db_bridge_py,tests_federated_learning_test_fl_db_integrity_py,tests_federated_learning_test_fl_decision_engine_py,tests_federated_learning_test_fl_deployment_suppression_py,tests_federated_learning_test_fl_dynamic_llm_cost_router_py,tests_federated_learning_test_fl_emergency_takeover_py,tests_federated_learning_test_fl_error_budget_py,tests_federated_learning_test_fl_eval_harness_py,tests_federated_learning_test_fl_evolution_engine_py,tests_federated_learning_test_fl_exceptions_py,tests_federated_learning_test_fl_federated_security_py,tests_federated_learning_test_fl_financial_stratification_py,tests_federated_learning_test_fl_fitness_functions_py,tests_federated_learning_test_fl_flag_lifecycle_manager_py,tests_federated_learning_test_fl_generator_py,tests_federated_learning_test_fl_global_action_scheduler_py,tests_federated_learning_test_fl_incident_priority_triage_automator_py design
    class D_TRADING external_prod
```

### 第 22 页 / 共 56 页 / Page 22 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_federated_learning_test_fl_intent_driven_ops_py["(原型态 / prototype) test_fl_intent_driven_ops.py"]
        tests_federated_learning_test_fl_kb_provenance_py["(原型态 / prototype) test_fl_kb_provenance.py"]
        tests_federated_learning_test_fl_license_compliance_py["(原型态 / prototype) test_fl_license_compliance.py"]
        tests_federated_learning_test_fl_llm_cost_router_py["(原型态 / prototype) test_fl_llm_cost_router.py"]
        tests_federated_learning_test_fl_merkle_audit_root_py["(原型态 / prototype) test_fl_merkle_audit_root.py"]
        tests_federated_learning_test_fl_meta_performance_gate_py["(原型态 / prototype) test_fl_meta_performance_gate.py"]
        tests_federated_learning_test_fl_multi_agent_orchestrator_py["(原型态 / prototype) test_fl_multi_agent_orchestrator.py"]
        tests_federated_learning_test_fl_notification_personalizer_py["(原型态 / prototype) test_fl_notification_personalizer.py"]
        tests_federated_learning_test_fl_owner_absence_escalation_py["(原型态 / prototype) test_fl_owner_absence_escalation.py"]
        tests_federated_learning_test_fl_parameterized_safety_gate_py["(原型态 / prototype) test_fl_parameterized_safety_gate.py"]
        tests_federated_learning_test_fl_protocols_py["(原型态 / prototype) test_fl_protocols.py"]
        tests_federated_learning_test_fl_safety_gate_l1_l27_py["(原型态 / prototype) test_fl_safety_gate_l1_l27.py"]
        tests_federated_learning_test_fl_saga_compensator_py["(原型态 / prototype) test_fl_saga_compensator.py"]
        tests_federated_learning_test_fl_scheduler_py["(原型态 / prototype) test_fl_scheduler.py"]
        tests_federated_learning_test_fl_scheduler_act_py["(原型态 / prototype) test_fl_scheduler_act.py"]
        tests_federated_learning_test_fl_scheduler_collect_detect_py["(原型态 / prototype) test_fl_scheduler_collect_detect.py"]
        tests_federated_learning_test_fl_scheduler_health_py["(原型态 / prototype) test_fl_scheduler_health.py"]
        tests_federated_learning_test_fl_scheduler_safety_py["(原型态 / prototype) test_fl_scheduler_safety.py"]
        tests_federated_learning_test_fl_scope_creep_monitor_py["(原型态 / prototype) test_fl_scope_creep_monitor.py"]
        tests_federated_learning_test_fl_slo_manager_py["(原型态 / prototype) test_fl_slo_manager.py"]
        tests_federated_learning_test_fl_template_py["(原型态 / prototype) test_fl_template.py"]
        tests_federated_learning_test_fl_validator_py["(原型态 / prototype) test_fl_validator.py"]
        tests_feedback_test_actors_init_py["(原型态 / prototype) test_actors_init.py"]
        tests_feedback_test_adaptive_param_tuning_py["(原型态 / prototype) test_adaptive_param_tuning.py"]
        tests_feedback_test_alert_desensitization_curve_py["(原型态 / prototype) test_alert_desensitization_curve.py"]
        tests_feedback_test_anomaly_clustering_py["(原型态 / prototype) test_anomaly_clustering.py"]
        tests_feedback_test_architectural_sod_py["(原型态 / prototype) test_architectural_sod.py"]
        tests_feedback_test_automated_rca_postmortem_generator_py["(原型态 / prototype) test_automated_rca_postmortem_generator.py"]
        tests_feedback_test_autoscale_remediation_py["(原型态 / prototype) test_autoscale_remediation.py"]
        tests_feedback_test_backpressure_bridge_root_py["(原型态 / prototype) test_backpressure_bridge_root.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_federated_learning_test_fl_intent_driven_ops_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_kb_provenance_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_license_compliance_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_multi_agent_orchestrator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_llm_cost_router_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_meta_performance_gate_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_owner_absence_escalation_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_merkle_audit_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_parameterized_safety_gate_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_notification_personalizer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_protocols_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_safety_gate_l1_l27_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_scheduler_health_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_scheduler_act_py -.->|测试依赖 / test_depends| D_TRADING
    tests_federated_learning_test_fl_scheduler_act_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_federated_learning_test_fl_intent_driven_ops_py,tests_federated_learning_test_fl_kb_provenance_py,tests_federated_learning_test_fl_license_compliance_py,tests_federated_learning_test_fl_llm_cost_router_py,tests_federated_learning_test_fl_merkle_audit_root_py,tests_federated_learning_test_fl_meta_performance_gate_py,tests_federated_learning_test_fl_multi_agent_orchestrator_py,tests_federated_learning_test_fl_notification_personalizer_py,tests_federated_learning_test_fl_owner_absence_escalation_py,tests_federated_learning_test_fl_parameterized_safety_gate_py,tests_federated_learning_test_fl_protocols_py,tests_federated_learning_test_fl_safety_gate_l1_l27_py,tests_federated_learning_test_fl_saga_compensator_py,tests_federated_learning_test_fl_scheduler_py,tests_federated_learning_test_fl_scheduler_act_py,tests_federated_learning_test_fl_scheduler_collect_detect_py,tests_federated_learning_test_fl_scheduler_health_py,tests_federated_learning_test_fl_scheduler_safety_py,tests_federated_learning_test_fl_scope_creep_monitor_py,tests_federated_learning_test_fl_slo_manager_py,tests_federated_learning_test_fl_template_py,tests_federated_learning_test_fl_validator_py,tests_feedback_test_actors_init_py,tests_feedback_test_adaptive_param_tuning_py,tests_feedback_test_alert_desensitization_curve_py,tests_feedback_test_anomaly_clustering_py,tests_feedback_test_architectural_sod_py,tests_feedback_test_automated_rca_postmortem_generator_py,tests_feedback_test_autoscale_remediation_py,tests_feedback_test_backpressure_bridge_root_py design
    class D_TRADING external_prod
```

### 第 23 页 / 共 56 页 / Page 23 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_feedback_test_blast_radius_budget_py["(原型态 / prototype) test_blast_radius_budget.py"]
        tests_feedback_test_boot_integrity_attestation_py["(原型态 / prototype) test_boot_integrity_attestation.py"]
        tests_feedback_test_cascading_rollback_analyzer_py["(原型态 / prototype) test_cascading_rollback_analyzer.py"]
        tests_feedback_test_cognitive_load_py["(原型态 / prototype) test_cognitive_load.py"]
        tests_feedback_test_collaborative_learning_py["(原型态 / prototype) test_collaborative_learning.py"]
        tests_feedback_test_collectors_py["(原型态 / prototype) test_collectors.py"]
        tests_feedback_test_confidence_decomposer_py["(原型态 / prototype) test_confidence_decomposer.py"]
        tests_feedback_test_config_feedback_loop_py["(原型态 / prototype) test_config_feedback_loop.py"]
        tests_feedback_test_conformal_prediction_py["(原型态 / prototype) test_conformal_prediction.py"]
        tests_feedback_test_counterfactual_py["(原型态 / prototype) test_counterfactual.py"]
        tests_feedback_test_deadman_switch_py["(原型态 / prototype) test_deadman_switch.py"]
        tests_feedback_test_diagnosers_py["(原型态 / prototype) test_diagnosers.py"]
        tests_feedback_test_diagnosis_engine_py["(原型态 / prototype) test_diagnosis_engine.py"]
        tests_feedback_test_digital_twin_sandbox_py["(原型态 / prototype) test_digital_twin_sandbox.py"]
        tests_feedback_test_diminishing_returns_detector_py["(原型态 / prototype) test_diminishing_returns_detector.py"]
        tests_feedback_test_docs_init_py["(原型态 / prototype) test_docs_init.py"]
        tests_feedback_test_dr_automation_py["(原型态 / prototype) test_dr_automation.py"]
        tests_feedback_test_dr_resilience_metrics_py["(原型态 / prototype) test_dr_resilience_metrics.py"]
        tests_feedback_test_dry_run_sandbox_py["(原型态 / prototype) test_dry_run_sandbox.py"]
        tests_feedback_test_dynamic_threshold_py["(原型态 / prototype) test_dynamic_threshold.py"]
        tests_feedback_test_e2e_integration_health_py["(原型态 / prototype) test_e2e_integration_health.py"]
        tests_feedback_test_ebpf_monitor_py["(原型态 / prototype) test_ebpf_monitor.py"]
        tests_feedback_test_ensemble_detector_py["(原型态 / prototype) test_ensemble_detector.py"]
        tests_feedback_test_ensemble_drift_py["(原型态 / prototype) test_ensemble_drift.py"]
        tests_feedback_test_eval_harness_root_py["(原型态 / prototype) test_eval_harness_root.py"]
        tests_feedback_test_evolution_engine_root_py["(原型态 / prototype) test_evolution_engine_root.py"]
        tests_feedback_test_evolution_init_py["(原型态 / prototype) test_evolution_init.py"]
        tests_feedback_test_ewc_kb_review_py["(原型态 / prototype) test_ewc_kb_review.py"]
        tests_feedback_test_exceptions_feedback_loop_py["(原型态 / prototype) test_exceptions_feedback_loop.py"]
        tests_feedback_test_failure_replay_py["(原型态 / prototype) test_failure_replay.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_feedback_test_blast_radius_budget_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_boot_integrity_attestation_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_confidence_decomposer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_cascading_rollback_analyzer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_collectors_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_feedback_test_blast_radius_budget_py,tests_feedback_test_boot_integrity_attestation_py,tests_feedback_test_cascading_rollback_analyzer_py,tests_feedback_test_cognitive_load_py,tests_feedback_test_collaborative_learning_py,tests_feedback_test_collectors_py,tests_feedback_test_confidence_decomposer_py,tests_feedback_test_config_feedback_loop_py,tests_feedback_test_conformal_prediction_py,tests_feedback_test_counterfactual_py,tests_feedback_test_deadman_switch_py,tests_feedback_test_diagnosers_py,tests_feedback_test_diagnosis_engine_py,tests_feedback_test_digital_twin_sandbox_py,tests_feedback_test_diminishing_returns_detector_py,tests_feedback_test_docs_init_py,tests_feedback_test_dr_automation_py,tests_feedback_test_dr_resilience_metrics_py,tests_feedback_test_dry_run_sandbox_py,tests_feedback_test_dynamic_threshold_py,tests_feedback_test_e2e_integration_health_py,tests_feedback_test_ebpf_monitor_py,tests_feedback_test_ensemble_detector_py,tests_feedback_test_ensemble_drift_py,tests_feedback_test_eval_harness_root_py,tests_feedback_test_evolution_engine_root_py,tests_feedback_test_evolution_init_py,tests_feedback_test_ewc_kb_review_py,tests_feedback_test_exceptions_feedback_loop_py,tests_feedback_test_failure_replay_py design
    class D_TRADING external_prod
```

### 第 24 页 / 共 56 页 / Page 24 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_feedback_test_federated_protocol_py["(原型态 / prototype) test_federated_protocol.py"]
        tests_feedback_test_feedback_bridge_py["(原型态 / prototype) test_feedback_bridge.py"]
        tests_feedback_test_feedback_collector_root_py["(原型态 / prototype) test_feedback_collector_root.py"]
        tests_feedback_test_feedback_core_py["(原型态 / prototype) test_feedback_core.py"]
        tests_feedback_test_feedback_delay_compensator_py["(原型态 / prototype) test_feedback_delay_compensator.py"]
        tests_feedback_test_feedback_loop_py["(原型态 / prototype) test_feedback_loop.py"]
        tests_feedback_test_feedback_policy_py["(原型态 / prototype) test_feedback_policy.py"]
        tests_feedback_test_feedback_self_audit_py["(原型态 / prototype) test_feedback_self_audit.py"]
        tests_feedback_test_flapping_detector_py["(原型态 / prototype) test_flapping_detector.py"]
        tests_feedback_test_gamification_py["(原型态 / prototype) test_gamification.py"]
        tests_feedback_test_global_action_scheduler_py["(原型态 / prototype) test_global_action_scheduler.py"]
        tests_feedback_test_golden_test_external_py["(原型态 / prototype) test_golden_test_external.py"]
        tests_feedback_test_gradual_poisoning_detector_py["(原型态 / prototype) test_gradual_poisoning_detector.py"]
        tests_feedback_test_graduated_activation_protocol_py["(原型态 / prototype) test_graduated_activation_protocol.py"]
        tests_feedback_test_heisenbug_detector_py["(原型态 / prototype) test_heisenbug_detector.py"]
        tests_feedback_test_hypernetwork_py["(原型态 / prototype) test_hypernetwork.py"]
        tests_feedback_test_impact_predictor_py["(原型态 / prototype) test_impact_predictor.py"]
        tests_feedback_test_incident_knowledge_injector_py["(原型态 / prototype) test_incident_knowledge_injector.py"]
        tests_feedback_test_infinite_loop_detector_py["(原型态 / prototype) test_infinite_loop_detector.py"]
        tests_feedback_test_interrupt_coherence_validator_py["(原型态 / prototype) test_interrupt_coherence_validator.py"]
        tests_feedback_test_known_unknown_registry_py["(原型态 / prototype) test_known_unknown_registry.py"]
        tests_feedback_test_log_anomaly_py["(原型态 / prototype) test_log_anomaly.py"]
        tests_feedback_test_maintenance_coordinator_py["(原型态 / prototype) test_maintenance_coordinator.py"]
        tests_feedback_test_market_calendar_py["(原型态 / prototype) test_market_calendar.py"]
        tests_feedback_test_market_event_integrator_py["(原型态 / prototype) test_market_event_integrator.py"]
        tests_feedback_test_meta_guard_latency_budget_py["(原型态 / prototype) test_meta_guard_latency_budget.py"]
        tests_feedback_test_metric_cardinality_guard_py["(原型态 / prototype) test_metric_cardinality_guard.py"]
        tests_feedback_test_metrics_collector_py["(原型态 / prototype) test_metrics_collector.py"]
        tests_feedback_test_no_llm_degradation_py["(原型态 / prototype) test_no_llm_degradation.py"]
        tests_feedback_test_nonstationary_effectiveness_py["(原型态 / prototype) test_nonstationary_effectiveness.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_feedback_test_federated_protocol_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_feedback_delay_compensator_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_feedback_test_feedback_policy_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_feedback_collector_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_feedback_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_feedback_core_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_feedback_core_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_feedback_self_audit_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_feedback_test_global_action_scheduler_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_feedback_loop_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_gamification_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_flapping_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_gradual_poisoning_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_hypernetwork_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_golden_test_external_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_feedback_test_federated_protocol_py,tests_feedback_test_feedback_bridge_py,tests_feedback_test_feedback_collector_root_py,tests_feedback_test_feedback_core_py,tests_feedback_test_feedback_delay_compensator_py,tests_feedback_test_feedback_loop_py,tests_feedback_test_feedback_policy_py,tests_feedback_test_feedback_self_audit_py,tests_feedback_test_flapping_detector_py,tests_feedback_test_gamification_py,tests_feedback_test_global_action_scheduler_py,tests_feedback_test_golden_test_external_py,tests_feedback_test_gradual_poisoning_detector_py,tests_feedback_test_graduated_activation_protocol_py,tests_feedback_test_heisenbug_detector_py,tests_feedback_test_hypernetwork_py,tests_feedback_test_impact_predictor_py,tests_feedback_test_incident_knowledge_injector_py,tests_feedback_test_infinite_loop_detector_py,tests_feedback_test_interrupt_coherence_validator_py,tests_feedback_test_known_unknown_registry_py,tests_feedback_test_log_anomaly_py,tests_feedback_test_maintenance_coordinator_py,tests_feedback_test_market_calendar_py,tests_feedback_test_market_event_integrator_py,tests_feedback_test_meta_guard_latency_budget_py,tests_feedback_test_metric_cardinality_guard_py,tests_feedback_test_metrics_collector_py,tests_feedback_test_no_llm_degradation_py,tests_feedback_test_nonstationary_effectiveness_py design
    class D_TRADING,D_GOVERNANCE external_prod
```

### 第 25 页 / 共 56 页 / Page 25 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_feedback_test_notification_feedback_py["(原型态 / prototype) test_notification_feedback.py"]
        tests_feedback_test_notification_personalizer_py["(原型态 / prototype) test_notification_personalizer.py"]
        tests_feedback_test_numerical_stability_guard_py["(原型态 / prototype) test_numerical_stability_guard.py"]
        tests_feedback_test_online_feature_importance_py["(原型态 / prototype) test_online_feature_importance.py"]
        tests_feedback_test_operational_seasonality_py["(原型态 / prototype) test_operational_seasonality.py"]
        tests_feedback_test_oscillation_damping_py["(原型态 / prototype) test_oscillation_damping.py"]
        tests_feedback_test_otel_adapter_py["(原型态 / prototype) test_otel_adapter.py"]
        tests_feedback_test_placebo_action_detector_py["(原型态 / prototype) test_placebo_action_detector.py"]
        tests_feedback_test_positive_feedback_defense_py["(原型态 / prototype) test_positive_feedback_defense.py"]
        tests_feedback_test_protocols_py["(原型态 / prototype) test_protocols.py"]
        tests_feedback_test_recovery_time_stats_py["(原型态 / prototype) test_recovery_time_stats.py"]
        tests_feedback_test_recursive_diagnosis_trust_evaluator_py["(原型态 / prototype) test_recursive_diagnosis_trust_evaluator.py"]
        tests_feedback_test_regulatory_audit_py["(原型态 / prototype) test_regulatory_audit.py"]
        tests_feedback_test_resolution_tracker_py["(原型态 / prototype) test_resolution_tracker.py"]
        tests_feedback_test_retirement_planner_py["(原型态 / prototype) test_retirement_planner.py"]
        tests_feedback_test_rumor_noise_filter_py["(原型态 / prototype) test_rumor_noise_filter.py"]
        tests_feedback_test_runbook_executor_py["(原型态 / prototype) test_runbook_executor.py"]
        tests_feedback_test_scheduler_collect_detect_py["(原型态 / prototype) test_scheduler_collect_detect.py"]
        tests_feedback_test_scheduler_health_py["(原型态 / prototype) test_scheduler_health.py"]
        tests_feedback_test_scheduler_integration_py["(原型态 / prototype) test_scheduler_integration.py"]
        tests_feedback_test_secondary_alert_channel_py["(原型态 / prototype) test_secondary_alert_channel.py"]
        tests_feedback_test_silent_corruption_detector_py["(原型态 / prototype) test_silent_corruption_detector.py"]
        tests_feedback_test_slo_capacity_metrics_py["(原型态 / prototype) test_slo_capacity_metrics.py"]
        tests_feedback_test_slo_manager_root_py["(原型态 / prototype) test_slo_manager_root.py"]
        tests_feedback_test_state_migration_validator_py["(原型态 / prototype) test_state_migration_validator.py"]
        tests_feedback_test_stochastic_diagnosis_verifier_py["(原型态 / prototype) test_stochastic_diagnosis_verifier.py"]
        tests_feedback_test_stochastic_diagnosis_verifier_v2_py["(原型态 / prototype) test_stochastic_diagnosis_verifier_v2.py"]
        tests_feedback_test_synthetic_anomaly_generator_py["(原型态 / prototype) test_synthetic_anomaly_generator.py"]
        tests_feedback_test_system_entropy_monitor_py["(原型态 / prototype) test_system_entropy_monitor.py"]
        tests_feedback_test_teacher_transfer_py["(原型态 / prototype) test_teacher_transfer.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_feedback_test_notification_feedback_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_notification_personalizer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_numerical_stability_guard_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_online_feature_importance_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_positive_feedback_defense_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_placebo_action_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_oscillation_damping_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_operational_seasonality_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_protocols_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_otel_adapter_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_recursive_diagnosis_trust_evaluator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_retirement_planner_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_recovery_time_stats_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_rumor_noise_filter_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_resolution_tracker_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_feedback_test_notification_feedback_py,tests_feedback_test_notification_personalizer_py,tests_feedback_test_numerical_stability_guard_py,tests_feedback_test_online_feature_importance_py,tests_feedback_test_operational_seasonality_py,tests_feedback_test_oscillation_damping_py,tests_feedback_test_otel_adapter_py,tests_feedback_test_placebo_action_detector_py,tests_feedback_test_positive_feedback_defense_py,tests_feedback_test_protocols_py,tests_feedback_test_recovery_time_stats_py,tests_feedback_test_recursive_diagnosis_trust_evaluator_py,tests_feedback_test_regulatory_audit_py,tests_feedback_test_resolution_tracker_py,tests_feedback_test_retirement_planner_py,tests_feedback_test_rumor_noise_filter_py,tests_feedback_test_runbook_executor_py,tests_feedback_test_scheduler_collect_detect_py,tests_feedback_test_scheduler_health_py,tests_feedback_test_scheduler_integration_py,tests_feedback_test_secondary_alert_channel_py,tests_feedback_test_silent_corruption_detector_py,tests_feedback_test_slo_capacity_metrics_py,tests_feedback_test_slo_manager_root_py,tests_feedback_test_state_migration_validator_py,tests_feedback_test_stochastic_diagnosis_verifier_py,tests_feedback_test_stochastic_diagnosis_verifier_v2_py,tests_feedback_test_synthetic_anomaly_generator_py,tests_feedback_test_system_entropy_monitor_py,tests_feedback_test_teacher_transfer_py design
    class D_TRADING external_prod
```

### 第 26 页 / 共 56 页 / Page 26 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_feedback_test_timezone_semantic_reasoner_py["(原型态 / prototype) test_timezone_semantic_reasoner.py"]
        tests_feedback_test_token_finops_py["(原型态 / prototype) test_token_finops.py"]
        tests_feedback_test_training_data_gov_py["(原型态 / prototype) test_training_data_gov.py"]
        tests_feedback_test_trend_cycle_separator_py["(原型态 / prototype) test_trend_cycle_separator.py"]
        tests_feedback_test_validator_py["(原型态 / prototype) test_validator.py"]
        tests_feedback_test_vertical_self_assessment_py["(原型态 / prototype) test_vertical_self_assessment.py"]
        tests_feedback_test_worm_write_integrity_py["(原型态 / prototype) test_worm_write_integrity.py"]
        tests_file_test_file_attr_checker_py["(原型态 / prototype) test_file_attr_checker.py"]
        tests_file_test_file_autoregister_py["(原型态 / prototype) test_file_autoregister.py"]
        tests_file_test_file_creator_py["(原型态 / prototype) test_file_creator.py"]
        tests_file_test_file_task_mapper_root_py["(原型态 / prototype) test_file_task_mapper_root.py"]
        tests_file_test_file_watcher_py["(原型态 / prototype) test_file_watcher.py"]
        tests_fix_test_alignment_syncer_py["(原型态 / prototype) test_alignment_syncer.py"]
        tests_fix_test_all_completer_py["(原型态 / prototype) test_all_completer.py"]
        tests_fix_test_compliance_auditor_py["(原型态 / prototype) test_compliance_auditor.py"]
        tests_fix_test_fix_budget_py["(原型态 / prototype) test_fix_budget.py"]
        tests_fix_test_fix_diff_py["(原型态 / prototype) test_fix_diff.py"]
        tests_fix_test_fix_health_check_py["(原型态 / prototype) test_fix_health_check.py"]
        tests_fix_test_fix_pattern_miner_py["(原型态 / prototype) test_fix_pattern_miner.py"]
        tests_fix_test_fix_reliability_py["(原型态 / prototype) test_fix_reliability.py"]
        tests_fix_test_fix_report_py["(原型态 / prototype) test_fix_report.py"]
        tests_fix_test_fix_safety_py["(原型态 / prototype) test_fix_safety.py"]
        tests_fix_test_fix_scheduler_py["(原型态 / prototype) test_fix_scheduler.py"]
        tests_fix_test_import_fixer_py["(原型态 / prototype) test_import_fixer.py"]
        tests_fixtures_test_commit_target_py["(原型态 / prototype) _test_commit_target.py"]
        tests_fixtures_test_lock_target_py["(原型态 / prototype) _test_lock_target.py"]
        tests_fixtures_test_mixed_target_py["(原型态 / prototype) _test_mixed_target.py"]
        tests_fixtures_test_staging_target_py["(原型态 / prototype) _test_staging_target.py"]
        tests_fixtures_g_trae_003_mock_yaml["(生产态 / production) g_trae_003_mock.yaml"]
        tests_fixtures_g_trae_004_mock_yaml["(生产态 / production) g_trae_004_mock.yaml"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_feedback_test_token_finops_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_timezone_semantic_reasoner_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_training_data_gov_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_vertical_self_assessment_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_worm_write_integrity_py -.->|测试依赖 / test_depends| D_TRADING
    tests_feedback_test_trend_cycle_separator_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_file_test_file_attr_checker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_file_test_file_creator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_file_test_file_task_mapper_root_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_file_test_file_task_mapper_root_py -.->|测试依赖 / test_depends| D_TRADING
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_fix_test_fix_health_check_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_fix_test_fix_health_check_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_file_test_file_watcher_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_fixtures_g_trae_003_mock_yaml,tests_fixtures_g_trae_004_mock_yaml production
    class tests_feedback_test_timezone_semantic_reasoner_py,tests_feedback_test_token_finops_py,tests_feedback_test_training_data_gov_py,tests_feedback_test_trend_cycle_separator_py,tests_feedback_test_validator_py,tests_feedback_test_vertical_self_assessment_py,tests_feedback_test_worm_write_integrity_py,tests_file_test_file_attr_checker_py,tests_file_test_file_autoregister_py,tests_file_test_file_creator_py,tests_file_test_file_task_mapper_root_py,tests_file_test_file_watcher_py,tests_fix_test_alignment_syncer_py,tests_fix_test_all_completer_py,tests_fix_test_compliance_auditor_py,tests_fix_test_fix_budget_py,tests_fix_test_fix_diff_py,tests_fix_test_fix_health_check_py,tests_fix_test_fix_pattern_miner_py,tests_fix_test_fix_reliability_py,tests_fix_test_fix_report_py,tests_fix_test_fix_safety_py,tests_fix_test_fix_scheduler_py,tests_fix_test_import_fixer_py,tests_fixtures_test_commit_target_py,tests_fixtures_test_lock_target_py,tests_fixtures_test_mixed_target_py,tests_fixtures_test_staging_target_py design
    class D_TRADING,D_GOVERNANCE,D_GOV_ENFORCEMENT,D_INFRA_RUNTIME external_prod
```

### 第 27 页 / 共 56 页 / Page 27 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_fixtures_g_trae_006_mock_yaml["(生产态 / production) g_trae_006_mock.yaml"]
        tests_fixtures_g_trae_007_mock_yaml["(生产态 / production) g_trae_007_mock.yaml"]
        tests_fixtures_g_trae_008_mock_yaml["(生产态 / production) g_trae_008_mock.yaml"]
        tests_fixtures_g_trae_009_mock_yaml["(生产态 / production) g_trae_009_mock.yaml"]
        tests_fixtures_g_trae_010_mock_yaml["(生产态 / production) g_trae_010_mock.yaml"]
        tests_fixtures_g_trae_011_mock_yaml["(生产态 / production) g_trae_011_mock.yaml"]
        tests_fixtures_g_trae_012_mock_yaml["(生产态 / production) g_trae_012_mock.yaml"]
        tests_fixtures_g_trae_016_mock_yaml["(生产态 / production) g_trae_016_mock.yaml"]
        tests_fixtures_g_trae_017_mock_yaml["(生产态 / production) g_trae_017_mock.yaml"]
        tests_fixtures_g_trae_018_mock_yaml["(生产态 / production) g_trae_018_mock.yaml"]
        tests_fixtures_g_trae_020_mock_yaml["(生产态 / production) g_trae_020_mock.yaml"]
        tests_fixtures_g_trae_021_mock_yaml["(生产态 / production) g_trae_021_mock.yaml"]
        tests_fixtures_g_trae_022_mock_yaml["(生产态 / production) g_trae_022_mock.yaml"]
        tests_fixtures_g_trae_023_mock_yaml["(生产态 / production) g_trae_023_mock.yaml"]
        tests_fixtures_g_trae_024_mock_yaml["(生产态 / production) g_trae_024_mock.yaml"]
        tests_fixtures_g_trae_025_mock_yaml["(生产态 / production) g_trae_025_mock.yaml"]
        tests_fixtures_g_trae_026_mock_yaml["(生产态 / production) g_trae_026_mock.yaml"]
        tests_fixtures_g_trae_027_mock_yaml["(生产态 / production) g_trae_027_mock.yaml"]
        tests_fixtures_g_trae_028_mock_yaml["(生产态 / production) g_trae_028_mock.yaml"]
        tests_fixtures_g_trae_029_mock_yaml["(生产态 / production) g_trae_029_mock.yaml"]
        tests_fixtures_g_trae_030_mock_yaml["(生产态 / production) g_trae_030_mock.yaml"]
        tests_fixtures_g_trae_031_mock_yaml["(生产态 / production) g_trae_031_mock.yaml"]
        tests_fixtures_g_trae_032_mock_yaml["(生产态 / production) g_trae_032_mock.yaml"]
        tests_fixtures_g_trae_033_mock_yaml["(生产态 / production) g_trae_033_mock.yaml"]
        tests_fixtures_g_trae_034_mock_yaml["(生产态 / production) g_trae_034_mock.yaml"]
        tests_fixtures_g_trae_035_mock_yaml["(生产态 / production) g_trae_035_mock.yaml"]
        tests_fixtures_g_trae_036_mock_yaml["(生产态 / production) g_trae_036_mock.yaml"]
        tests_fixtures_g_trae_037_mock_yaml["(生产态 / production) g_trae_037_mock.yaml"]
        tests_fixtures_g_trae_038_mock_yaml["(生产态 / production) g_trae_038_mock.yaml"]
        tests_fixtures_g_trae_039_mock_yaml["(生产态 / production) g_trae_039_mock.yaml"]
    end
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_fixtures_g_trae_006_mock_yaml,tests_fixtures_g_trae_007_mock_yaml,tests_fixtures_g_trae_008_mock_yaml,tests_fixtures_g_trae_009_mock_yaml,tests_fixtures_g_trae_010_mock_yaml,tests_fixtures_g_trae_011_mock_yaml,tests_fixtures_g_trae_012_mock_yaml,tests_fixtures_g_trae_016_mock_yaml,tests_fixtures_g_trae_017_mock_yaml,tests_fixtures_g_trae_018_mock_yaml,tests_fixtures_g_trae_020_mock_yaml,tests_fixtures_g_trae_021_mock_yaml,tests_fixtures_g_trae_022_mock_yaml,tests_fixtures_g_trae_023_mock_yaml,tests_fixtures_g_trae_024_mock_yaml,tests_fixtures_g_trae_025_mock_yaml,tests_fixtures_g_trae_026_mock_yaml,tests_fixtures_g_trae_027_mock_yaml,tests_fixtures_g_trae_028_mock_yaml,tests_fixtures_g_trae_029_mock_yaml,tests_fixtures_g_trae_030_mock_yaml,tests_fixtures_g_trae_031_mock_yaml,tests_fixtures_g_trae_032_mock_yaml,tests_fixtures_g_trae_033_mock_yaml,tests_fixtures_g_trae_034_mock_yaml,tests_fixtures_g_trae_035_mock_yaml,tests_fixtures_g_trae_036_mock_yaml,tests_fixtures_g_trae_037_mock_yaml,tests_fixtures_g_trae_038_mock_yaml,tests_fixtures_g_trae_039_mock_yaml production
```

### 第 28 页 / 共 56 页 / Page 28 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_fixtures_g_trae_040_mock_yaml["(生产态 / production) g_trae_040_mock.yaml"]
        tests_fixtures_g_trae_041_mock_yaml["(生产态 / production) g_trae_041_mock.yaml"]
        tests_fixtures_g_trae_042_mock_yaml["(生产态 / production) g_trae_042_mock.yaml"]
        tests_fixtures_g_trae_043_mock_yaml["(生产态 / production) g_trae_043_mock.yaml"]
        tests_fixtures_g_trae_044_mock_yaml["(生产态 / production) g_trae_044_mock.yaml"]
        tests_fixtures_g_trae_045_mock_yaml["(生产态 / production) g_trae_045_mock.yaml"]
        tests_fixtures_g_trae_046_mock_yaml["(生产态 / production) g_trae_046_mock.yaml"]
        tests_fixtures_g_trae_047_mock_yaml["(生产态 / production) g_trae_047_mock.yaml"]
        tests_fixtures_g_trae_048_mock_yaml["(生产态 / production) g_trae_048_mock.yaml"]
        tests_fixtures_g_trae_049_mock_yaml["(生产态 / production) g_trae_049_mock.yaml"]
        tests_fixtures_g_trae_050_mock_yaml["(生产态 / production) g_trae_050_mock.yaml"]
        tests_fixtures_g_trae_051_mock_yaml["(生产态 / production) g_trae_051_mock.yaml"]
        tests_fixtures_g_trae_052_mock_yaml["(生产态 / production) g_trae_052_mock.yaml"]
        tests_fixtures_g_trae_053_mock_yaml["(生产态 / production) g_trae_053_mock.yaml"]
        tests_fixtures_g_trae_054_mock_yaml["(生产态 / production) g_trae_054_mock.yaml"]
        tests_fixtures_g_trae_055_mock_yaml["(生产态 / production) g_trae_055_mock.yaml"]
        tests_fixtures_psv_mock_script_py["(原型态 / prototype) psv_mock_script.py"]
        tests_fixtures_psv_mock_script_alt_py["(原型态 / prototype) psv_mock_script_alt.py"]
        tests_fle_test_fle_anomaly_detector_py["(原型态 / prototype) test_fle_anomaly_detector.py"]
        tests_fle_test_fle_chaos_engineering_py["(原型态 / prototype) test_fle_chaos_engineering.py"]
        tests_fle_test_fle_config_py["(原型态 / prototype) test_fle_config.py"]
        tests_fle_test_fle_dogfood_monitor_py["(原型态 / prototype) test_fle_dogfood_monitor.py"]
        tests_fle_test_fle_exceptions_py["(原型态 / prototype) test_fle_exceptions.py"]
        tests_fle_test_fle_feedback_collector_py["(原型态 / prototype) test_fle_feedback_collector.py"]
        tests_fle_test_fle_generator_py["(原型态 / prototype) test_fle_generator.py"]
        tests_fle_test_fle_metrics_collector_py["(原型态 / prototype) test_fle_metrics_collector.py"]
        tests_fle_test_fle_performance_regression_detector_py["(原型态 / prototype) test_fle_performance_regression_detector.py"]
        tests_fle_test_fle_protocols_py["(原型态 / prototype) test_fle_protocols.py"]
        tests_fle_test_fle_regime_detector_py["(原型态 / prototype) test_fle_regime_detector.py"]
        tests_fle_test_fle_self_slo_metrics_py["(原型态 / prototype) test_fle_self_slo_metrics.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_fle_test_fle_dogfood_monitor_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_anomaly_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_anomaly_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_anomaly_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_anomaly_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_chaos_engineering_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_exceptions_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_config_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_feedback_collector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_generator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_metrics_collector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_protocols_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_regime_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_self_slo_metrics_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_performance_regression_detector_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_fixtures_g_trae_040_mock_yaml,tests_fixtures_g_trae_041_mock_yaml,tests_fixtures_g_trae_042_mock_yaml,tests_fixtures_g_trae_043_mock_yaml,tests_fixtures_g_trae_044_mock_yaml,tests_fixtures_g_trae_045_mock_yaml,tests_fixtures_g_trae_046_mock_yaml,tests_fixtures_g_trae_047_mock_yaml,tests_fixtures_g_trae_048_mock_yaml,tests_fixtures_g_trae_049_mock_yaml,tests_fixtures_g_trae_050_mock_yaml,tests_fixtures_g_trae_051_mock_yaml,tests_fixtures_g_trae_052_mock_yaml,tests_fixtures_g_trae_053_mock_yaml,tests_fixtures_g_trae_054_mock_yaml,tests_fixtures_g_trae_055_mock_yaml production
    class tests_fixtures_psv_mock_script_py,tests_fixtures_psv_mock_script_alt_py,tests_fle_test_fle_anomaly_detector_py,tests_fle_test_fle_chaos_engineering_py,tests_fle_test_fle_config_py,tests_fle_test_fle_dogfood_monitor_py,tests_fle_test_fle_exceptions_py,tests_fle_test_fle_feedback_collector_py,tests_fle_test_fle_generator_py,tests_fle_test_fle_metrics_collector_py,tests_fle_test_fle_performance_regression_detector_py,tests_fle_test_fle_protocols_py,tests_fle_test_fle_regime_detector_py,tests_fle_test_fle_self_slo_metrics_py design
    class D_TRADING external_prod
```

### 第 29 页 / 共 56 页 / Page 29 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_fle_test_fle_template_py["(原型态 / prototype) test_fle_template.py"]
        tests_fle_test_fle_upgrade_safety_validator_py["(原型态 / prototype) test_fle_upgrade_safety_validator.py"]
        tests_fle_test_fle_validator_py["(原型态 / prototype) test_fle_validator.py"]
        tests_gate_test_ci_cd_pre_scanner_py["(原型态 / prototype) test_ci_cd_pre_scanner.py"]
        tests_gate_test_circuit_breaker_types_py["(原型态 / prototype) test_circuit_breaker_types.py"]
        tests_gate_test_concurrent_change_deconfliction_py["(原型态 / prototype) test_concurrent_change_deconfliction.py"]
        tests_gate_test_conflict_arbitration_py["(原型态 / prototype) test_conflict_arbitration.py"]
        tests_gate_test_cve_scanner_py["(原型态 / prototype) test_cve_scanner.py"]
        tests_gate_test_deployment_suppression_py["(原型态 / prototype) test_deployment_suppression.py"]
        tests_gate_test_dynamic_llm_cost_router_py["(原型态 / prototype) test_dynamic_llm_cost_router.py"]
        tests_gate_test_emergency_takeover_py["(原型态 / prototype) test_emergency_takeover.py"]
        tests_gate_test_federated_security_py["(原型态 / prototype) test_federated_security.py"]
        tests_gate_test_flag_lifecycle_manager_py["(原型态 / prototype) test_flag_lifecycle_manager.py"]
        tests_gate_test_gate_context_py["(原型态 / prototype) test_gate_context.py"]
        tests_gate_test_gate_health_py["(原型态 / prototype) test_gate_health.py"]
        tests_gate_test_gate_integrity_guard_py["(原型态 / prototype) test_gate_integrity_guard.py"]
        tests_gate_test_gate_override_py["(原型态 / prototype) test_gate_override.py"]
        tests_gate_test_gate_persistence_py["(原型态 / prototype) test_gate_persistence.py"]
        tests_gate_test_gate_pipeline_py["(原型态 / prototype) test_gate_pipeline.py"]
        tests_gate_test_gate_simulator_py["(原型态 / prototype) test_gate_simulator.py"]
        tests_gate_test_gate_types_py["(原型态 / prototype) test_gate_types.py"]
        tests_gate_test_license_compliance_py["(原型态 / prototype) test_license_compliance.py"]
        tests_gate_test_merkle_audit_root_py["(原型态 / prototype) test_merkle_audit_root.py"]
        tests_gate_test_meta_performance_gate_py["(原型态 / prototype) test_meta_performance_gate.py"]
        tests_gate_test_parameterized_safety_gate_py["(原型态 / prototype) test_parameterized_safety_gate.py"]
        tests_gate_test_resilience_circuit_breaker_py["(原型态 / prototype) test_resilience_circuit_breaker.py"]
        tests_gate_test_scope_creep_monitor_py["(原型态 / prototype) test_scope_creep_monitor.py"]
        tests_git_test_git_bisector_py["(原型态 / prototype) test_git_bisector.py"]
        tests_git_test_git_commit_concurrent_py["(原型态 / prototype) test_git_commit_concurrent.py"]
        tests_git_test_git_commit_extreme_py["(原型态 / prototype) test_git_commit_extreme.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_fle_test_fle_template_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_upgrade_safety_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_validator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_fle_test_fle_validator_py -.->|测试依赖 / test_depends| D_TRADING
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_gate_test_circuit_breaker_types_py -.->|测试依赖 / test_depends| D_SHARED
    tests_gate_test_ci_cd_pre_scanner_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_concurrent_change_deconfliction_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_deployment_suppression_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_dynamic_llm_cost_router_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_emergency_takeover_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_cve_scanner_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_federated_security_py -.->|测试依赖 / test_depends| D_TRADING
    tests_gate_test_conflict_arbitration_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_gate_test_gate_context_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_gate_test_gate_integrity_guard_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_fle_test_fle_template_py,tests_fle_test_fle_upgrade_safety_validator_py,tests_fle_test_fle_validator_py,tests_gate_test_ci_cd_pre_scanner_py,tests_gate_test_circuit_breaker_types_py,tests_gate_test_concurrent_change_deconfliction_py,tests_gate_test_conflict_arbitration_py,tests_gate_test_cve_scanner_py,tests_gate_test_deployment_suppression_py,tests_gate_test_dynamic_llm_cost_router_py,tests_gate_test_emergency_takeover_py,tests_gate_test_federated_security_py,tests_gate_test_flag_lifecycle_manager_py,tests_gate_test_gate_context_py,tests_gate_test_gate_health_py,tests_gate_test_gate_integrity_guard_py,tests_gate_test_gate_override_py,tests_gate_test_gate_persistence_py,tests_gate_test_gate_pipeline_py,tests_gate_test_gate_simulator_py,tests_gate_test_gate_types_py,tests_gate_test_license_compliance_py,tests_gate_test_merkle_audit_root_py,tests_gate_test_meta_performance_gate_py,tests_gate_test_parameterized_safety_gate_py,tests_gate_test_resilience_circuit_breaker_py,tests_gate_test_scope_creep_monitor_py,tests_git_test_git_bisector_py,tests_git_test_git_commit_concurrent_py,tests_git_test_git_commit_extreme_py design
    class D_TRADING,D_SHARED,D_GOV_ENFORCEMENT external_prod
```

### 第 30 页 / 共 56 页 / Page 30 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_git_test_git_commit_gateway_py["(原型态 / prototype) test_git_commit_gateway.py"]
        tests_git_test_git_hook_pre_scanner_py["(原型态 / prototype) test_git_hook_pre_scanner.py"]
        tests_git_test_git_infra_snapshot_py["(原型态 / prototype) test_git_infra_snapshot.py"]
        tests_git_test_lock_release_uncommitted_py["(原型态 / prototype) test_lock_release_uncommitted.py"]
        tests_governance_access_control_test_account_isolator_py["(原型态 / prototype) test_account_isolator.py"]
        tests_governance_access_control_test_approval_py["(原型态 / prototype) test_approval.py"]
        tests_governance_access_control_test_credential_guard_py["(原型态 / prototype) test_credential_guard.py"]
        tests_governance_access_control_test_credential_rotation_trigger_py["(原型态 / prototype) test_credential_rotation_trigger.py"]
        tests_governance_access_control_test_rbac_bridge_py["(原型态 / prototype) test_rbac_bridge.py"]
        tests_governance_access_control_test_rbac_bridge_bridge_py["(原型态 / prototype) test_rbac_bridge_bridge.py"]
        tests_governance_access_control_test_secret_rotation_aware_py["(原型态 / prototype) test_secret_rotation_aware.py"]
        tests_governance_adversarial_test_adversarial_tester_py["(原型态 / prototype) test_adversarial_tester.py"]
        tests_governance_adversarial_test_anti_automation_bias_py["(原型态 / prototype) test_anti_automation_bias.py"]
        tests_governance_adversarial_test_compositional_safety_tester_py["(原型态 / prototype) test_compositional_safety_tester.py"]
        tests_governance_adversarial_test_hallucination_guard_py["(原型态 / prototype) test_hallucination_guard.py"]
        tests_governance_adversarial_test_persuasion_detector_py["(原型态 / prototype) test_persuasion_detector.py"]
        tests_governance_adversarial_test_poison_cascade_detector_py["(原型态 / prototype) test_poison_cascade_detector.py"]
        tests_governance_adversarial_test_reward_hacking_rebound_detector_py["(原型态 / prototype) test_reward_hacking_rebound_detector.py"]
        tests_governance_adversarial_test_shadow_verifier_py["(原型态 / prototype) test_shadow_verifier.py"]
        tests_governance_adversarial_test_vibe_security_verify_py["(原型态 / prototype) test_vibe_security_verify.py"]
        tests_governance_adversarial_test_vibe_verify_integration_py["(原型态 / prototype) test_vibe_verify_integration.py"]
        tests_governance_adversarial_test_vigil_runtime_py["(原型态 / prototype) test_vigil_runtime.py"]
        tests_governance_audit_test_alerts_py["(原型态 / prototype) test_alerts.py"]
        tests_governance_audit_test_anomaly_py["(原型态 / prototype) test_anomaly.py"]
        tests_governance_audit_test_auditor_py["(原型态 / prototype) test_auditor.py"]
        tests_governance_audit_test_bridge_py["(原型态 / prototype) test_bridge.py"]
        tests_governance_audit_test_changelog_manager_py["(原型态 / prototype) test_changelog_manager.py"]
        tests_governance_audit_test_code_archaeology_py["(原型态 / prototype) test_code_archaeology.py"]
        tests_governance_audit_test_compliance_map_py["(原型态 / prototype) test_compliance_map.py"]
        tests_governance_audit_test_corporate_actions_py["(原型态 / prototype) test_corporate_actions.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_git_test_git_commit_gateway_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_git_test_git_hook_pre_scanner_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_git_test_git_infra_snapshot_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_access_control_test_credential_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_access_control_test_credential_rotation_trigger_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_access_control_test_rbac_bridge_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_governance_access_control_test_approval_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_access_control_test_rbac_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_access_control_test_account_isolator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_adversarial_test_anti_automation_bias_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_access_control_test_secret_rotation_aware_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_adversarial_test_adversarial_tester_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_adversarial_test_persuasion_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_adversarial_test_reward_hacking_rebound_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_adversarial_test_poison_cascade_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_git_test_git_commit_gateway_py,tests_git_test_git_hook_pre_scanner_py,tests_git_test_git_infra_snapshot_py,tests_git_test_lock_release_uncommitted_py,tests_governance_access_control_test_account_isolator_py,tests_governance_access_control_test_approval_py,tests_governance_access_control_test_credential_guard_py,tests_governance_access_control_test_credential_rotation_trigger_py,tests_governance_access_control_test_rbac_bridge_py,tests_governance_access_control_test_rbac_bridge_bridge_py,tests_governance_access_control_test_secret_rotation_aware_py,tests_governance_adversarial_test_adversarial_tester_py,tests_governance_adversarial_test_anti_automation_bias_py,tests_governance_adversarial_test_compositional_safety_tester_py,tests_governance_adversarial_test_hallucination_guard_py,tests_governance_adversarial_test_persuasion_detector_py,tests_governance_adversarial_test_poison_cascade_detector_py,tests_governance_adversarial_test_reward_hacking_rebound_detector_py,tests_governance_adversarial_test_shadow_verifier_py,tests_governance_adversarial_test_vibe_security_verify_py,tests_governance_adversarial_test_vibe_verify_integration_py,tests_governance_adversarial_test_vigil_runtime_py,tests_governance_audit_test_alerts_py,tests_governance_audit_test_anomaly_py,tests_governance_audit_test_auditor_py,tests_governance_audit_test_bridge_py,tests_governance_audit_test_changelog_manager_py,tests_governance_audit_test_code_archaeology_py,tests_governance_audit_test_compliance_map_py,tests_governance_audit_test_corporate_actions_py design
    class D_GOVERNANCE,D_INFRA_RECOVERY,D_GOV_ENFORCEMENT external_prod
```

### 第 31 页 / 共 56 页 / Page 31 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_audit_test_delegation_auditor_py["(原型态 / prototype) test_delegation_auditor.py"]
        tests_governance_audit_test_delegation_bridge_py["(原型态 / prototype) test_delegation_bridge.py"]
        tests_governance_audit_test_dora_metrics_py["(原型态 / prototype) test_dora_metrics.py"]
        tests_governance_audit_test_evidence_pack_py["(原型态 / prototype) test_evidence_pack.py"]
        tests_governance_audit_test_false_negative_auditor_py["(原型态 / prototype) test_false_negative_auditor.py"]
        tests_governance_audit_test_fifteen_dimension_auditor_py["(原型态 / prototype) test_fifteen_dimension_auditor.py"]
        tests_governance_audit_test_forensic_py["(原型态 / prototype) test_forensic.py"]
        tests_governance_audit_test_forensic_package_py["(原型态 / prototype) test_forensic_package.py"]
        tests_governance_audit_test_gap_analyzer_py["(原型态 / prototype) test_gap_analyzer.py"]
        tests_governance_audit_test_genesis_py["(原型态 / prototype) test_genesis.py"]
        tests_governance_audit_test_glossary_matrix_py["(原型态 / prototype) test_glossary_matrix.py"]
        tests_governance_audit_test_governance_auditor_py["(原型态 / prototype) test_governance_auditor.py"]
        tests_governance_audit_test_indexer_py["(原型态 / prototype) test_indexer.py"]
        tests_governance_audit_test_integrity_root_py["(原型态 / prototype) test_integrity_root.py"]
        tests_governance_audit_test_integrity_verifier_py["(原型态 / prototype) test_integrity_verifier.py"]
        tests_governance_audit_test_log_rotation_py["(原型态 / prototype) test_log_rotation.py"]
        tests_governance_audit_test_merkle_audit_py["(原型态 / prototype) test_merkle_audit.py"]
        tests_governance_audit_test_merkle_hourly_py["(原型态 / prototype) test_merkle_hourly.py"]
        tests_governance_audit_test_orchestrator_py["(原型态 / prototype) test_orchestrator.py"]
        tests_governance_audit_test_privacy_py["(原型态 / prototype) test_privacy.py"]
        tests_governance_audit_test_query_py["(原型态 / prototype) test_query.py"]
        tests_governance_audit_test_replay_engine_py["(原型态 / prototype) test_replay_engine.py"]
        tests_governance_audit_test_retention_py["(原型态 / prototype) test_retention.py"]
        tests_governance_audit_test_sbom_generator_py["(原型态 / prototype) test_sbom_generator.py"]
        tests_governance_audit_test_spec_auditor_py["(原型态 / prototype) test_spec_auditor.py"]
        tests_governance_audit_test_supply_chain_py["(原型态 / prototype) test_supply_chain.py"]
        tests_governance_audit_test_tamper_evident_log_py["(原型态 / prototype) test_tamper_evident_log.py"]
        tests_governance_audit_test_tiered_storage_py["(原型态 / prototype) test_tiered_storage.py"]
        tests_governance_audit_test_tiered_storage_bridge_py["(原型态 / prototype) test_tiered_storage_bridge.py"]
        tests_governance_audit_test_trust_bridge_py["(原型态 / prototype) test_trust_bridge.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_audit_test_delegation_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_false_negative_auditor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_fifteen_dimension_auditor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_delegation_auditor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_evidence_pack_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_dora_metrics_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_governance_audit_test_forensic_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_audit_test_glossary_matrix_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_genesis_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_governance_auditor_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_audit_test_gap_analyzer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_forensic_package_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_integrity_verifier_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_indexer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_integrity_root_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_audit_test_delegation_auditor_py,tests_governance_audit_test_delegation_bridge_py,tests_governance_audit_test_dora_metrics_py,tests_governance_audit_test_evidence_pack_py,tests_governance_audit_test_false_negative_auditor_py,tests_governance_audit_test_fifteen_dimension_auditor_py,tests_governance_audit_test_forensic_py,tests_governance_audit_test_forensic_package_py,tests_governance_audit_test_gap_analyzer_py,tests_governance_audit_test_genesis_py,tests_governance_audit_test_glossary_matrix_py,tests_governance_audit_test_governance_auditor_py,tests_governance_audit_test_indexer_py,tests_governance_audit_test_integrity_root_py,tests_governance_audit_test_integrity_verifier_py,tests_governance_audit_test_log_rotation_py,tests_governance_audit_test_merkle_audit_py,tests_governance_audit_test_merkle_hourly_py,tests_governance_audit_test_orchestrator_py,tests_governance_audit_test_privacy_py,tests_governance_audit_test_query_py,tests_governance_audit_test_replay_engine_py,tests_governance_audit_test_retention_py,tests_governance_audit_test_sbom_generator_py,tests_governance_audit_test_spec_auditor_py,tests_governance_audit_test_supply_chain_py,tests_governance_audit_test_tamper_evident_log_py,tests_governance_audit_test_tiered_storage_py,tests_governance_audit_test_tiered_storage_bridge_py,tests_governance_audit_test_trust_bridge_py design
    class D_GOVERNANCE,D_INFRA_RECOVERY external_prod
```

### 第 32 页 / 共 56 页 / Page 32 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_audit_test_trust_engine_py["(原型态 / prototype) test_trust_engine.py"]
        tests_governance_audit_test_verdict_engine_py["(原型态 / prototype) test_verdict_engine.py"]
        tests_governance_audit_test_wqa_scorer_py["(原型态 / prototype) test_wqa_scorer.py"]
        tests_governance_audit_test_writer_py["(原型态 / prototype) test_writer.py"]
        tests_governance_budget_test_adversarial_extreme_py["(原型态 / prototype) test_adversarial_extreme.py"]
        tests_governance_budget_test_burn_rate_monitor_py["(原型态 / prototype) test_burn_rate_monitor.py"]
        tests_governance_budget_test_conversation_tax_detector_py["(原型态 / prototype) test_conversation_tax_detector.py"]
        tests_governance_budget_test_cost_attributor_py["(原型态 / prototype) test_cost_attributor.py"]
        tests_governance_budget_test_cost_budget_root_py["(原型态 / prototype) test_cost_budget_root.py"]
        tests_governance_budget_test_cost_router_py["(原型态 / prototype) test_cost_router.py"]
        tests_governance_budget_test_debt_projector_py["(原型态 / prototype) test_debt_projector.py"]
        tests_governance_budget_test_degradation_py["(原型态 / prototype) test_degradation.py"]
        tests_governance_budget_test_degradation_manager_py["(原型态 / prototype) test_degradation_manager.py"]
        tests_governance_budget_test_error_budget_burst_limiter_py["(原型态 / prototype) test_error_budget_burst_limiter.py"]
        tests_governance_budget_test_governance_budget_tracker_py["(原型态 / prototype) test_governance_budget_tracker.py"]
        tests_governance_budget_test_pre_flight_gate_py["(原型态 / prototype) test_pre_flight_gate.py"]
        tests_governance_budget_test_roi_calculator_py["(原型态 / prototype) test_roi_calculator.py"]
        tests_governance_budget_test_tco_model_py["(原型态 / prototype) test_tco_model.py"]
        tests_governance_code_dedup_test_atomic_fixer_py["(原型态 / prototype) test_atomic_fixer.py"]
        tests_governance_code_dedup_test_grandfather_manager_py["(原型态 / prototype) test_grandfather_manager.py"]
        tests_governance_code_dedup_test_policy_tree_validator_py["(原型态 / prototype) test_policy_tree_validator.py"]
        tests_governance_code_dedup_test_pre_apply_integrity_gate_py["(原型态 / prototype) test_pre_apply_integrity_gate.py"]
        tests_governance_code_dedup_test_ssot_registrar_py["(原型态 / prototype) test_ssot_registrar.py"]
        tests_governance_code_quality_test_ast_comparator_py["(原型态 / prototype) test_ast_comparator.py"]
        tests_governance_code_quality_test_check_frontmatter_metadata_py["(原型态 / prototype) test_check_frontmatter_metadata.py"]
        tests_governance_code_quality_test_code_analyzer_runner_py["(原型态 / prototype) test_code_analyzer_runner.py"]
        tests_governance_code_quality_test_code_simulator_py["(原型态 / prototype) test_code_simulator.py"]
        tests_governance_code_quality_test_detect_forward_reference_py["(原型态 / prototype) test_detect_forward_reference.py"]
        tests_governance_code_quality_test_formal_verifier_py["(原型态 / prototype) test_formal_verifier.py"]
        tests_governance_code_quality_test_fsm_verifier_py["(原型态 / prototype) test_fsm_verifier.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_governance_audit_test_verdict_engine_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_audit_test_verdict_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_writer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_trust_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_audit_test_wqa_scorer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_adversarial_extreme_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_adversarial_extreme_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_adversarial_extreme_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_adversarial_extreme_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_adversarial_extreme_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_cost_attributor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_cost_attributor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_cost_budget_root_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_conversation_tax_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_budget_test_burn_rate_monitor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_audit_test_trust_engine_py,tests_governance_audit_test_verdict_engine_py,tests_governance_audit_test_wqa_scorer_py,tests_governance_audit_test_writer_py,tests_governance_budget_test_adversarial_extreme_py,tests_governance_budget_test_burn_rate_monitor_py,tests_governance_budget_test_conversation_tax_detector_py,tests_governance_budget_test_cost_attributor_py,tests_governance_budget_test_cost_budget_root_py,tests_governance_budget_test_cost_router_py,tests_governance_budget_test_debt_projector_py,tests_governance_budget_test_degradation_py,tests_governance_budget_test_degradation_manager_py,tests_governance_budget_test_error_budget_burst_limiter_py,tests_governance_budget_test_governance_budget_tracker_py,tests_governance_budget_test_pre_flight_gate_py,tests_governance_budget_test_roi_calculator_py,tests_governance_budget_test_tco_model_py,tests_governance_code_dedup_test_atomic_fixer_py,tests_governance_code_dedup_test_grandfather_manager_py,tests_governance_code_dedup_test_policy_tree_validator_py,tests_governance_code_dedup_test_pre_apply_integrity_gate_py,tests_governance_code_dedup_test_ssot_registrar_py,tests_governance_code_quality_test_ast_comparator_py,tests_governance_code_quality_test_check_frontmatter_metadata_py,tests_governance_code_quality_test_code_analyzer_runner_py,tests_governance_code_quality_test_code_simulator_py,tests_governance_code_quality_test_detect_forward_reference_py,tests_governance_code_quality_test_formal_verifier_py,tests_governance_code_quality_test_fsm_verifier_py design
    class D_TRADING,D_GOVERNANCE external_prod
```

### 第 33 页 / 共 56 页 / Page 33 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_code_quality_test_function_discovery_py["(原型态 / prototype) test_function_discovery.py"]
        tests_governance_code_quality_test_simplicity_auditor_py["(原型态 / prototype) test_simplicity_auditor.py"]
        tests_governance_commit_gates_test_arch_reference_gate_py["(原型态 / prototype) test_arch_reference_gate.py"]
        tests_governance_commit_gates_test_claim_required_gate_py["(原型态 / prototype) test_claim_required_gate.py"]
        tests_governance_commit_gates_test_create_guard_py["(原型态 / prototype) test_create_guard.py"]
        tests_governance_commit_gates_test_dangling_reference_gate_py["(原型态 / prototype) test_dangling_reference_gate.py"]
        tests_governance_commit_gates_test_directory_contract_gate_py["(原型态 / prototype) test_directory_contract_gate.py"]
        tests_governance_commit_gates_test_file_placement_ttl_gate_py["(原型态 / prototype) test_file_placement_ttl_gate.py"]
        tests_governance_commit_gates_test_held_overlap_gate_py["(原型态 / prototype) test_held_overlap_gate.py"]
        tests_governance_commit_gates_test_module_id_consistency_gate_py["(原型态 / prototype) test_module_id_consistency_gate.py"]
        tests_governance_commit_gates_test_msg_exposure_gate_py["(原型态 / prototype) test_msg_exposure_gate.py"]
        tests_governance_commit_gates_test_msg_style_gate_py["(原型态 / prototype) test_msg_style_gate.py"]
        tests_governance_commit_gates_test_r5_digit_suffix_gate_py["(原型态 / prototype) test_r5_digit_suffix_gate.py"]
        tests_governance_commit_gates_test_ssot_redefinition_gate_py["(原型态 / prototype) test_ssot_redefinition_gate.py"]
        tests_governance_commit_gates_test_ttl_gate_py["(原型态 / prototype) test_ttl_gate.py"]
        tests_governance_commit_gates_test_unsafe_dict_spread_gate_py["(原型态 / prototype) test_unsafe_dict_spread_gate.py"]
        tests_governance_compliance_test_compliance_mapper_py["(原型态 / prototype) test_compliance_mapper.py"]
        tests_governance_compliance_test_human_factors_py["(原型态 / prototype) test_human_factors.py"]
        tests_governance_compliance_test_load_bearing_py["(原型态 / prototype) test_load_bearing.py"]
        tests_governance_compliance_test_owner_absent_py["(原型态 / prototype) test_owner_absent.py"]
        tests_governance_compliance_test_quiet_period_monitor_py["(原型态 / prototype) test_quiet_period_monitor.py"]
        tests_governance_compliance_test_right_to_be_forgotten_py["(原型态 / prototype) test_right_to_be_forgotten.py"]
        tests_governance_compliance_test_thematic_clusterer_py["(原型态 / prototype) test_thematic_clusterer.py"]
        tests_governance_context_governance_test_command_chain_length_gate_py["(原型态 / prototype) test_command_chain_length_gate.py"]
        tests_governance_data_layer_test_cache_manager_py["(原型态 / prototype) test_cache_manager.py"]
        tests_governance_data_layer_test_s3_snapshot_lifecycle_py["(原型态 / prototype) test_s3_snapshot_lifecycle.py"]
        tests_governance_data_layer_test_sqlite_dumper_py["(原型态 / prototype) test_sqlite_dumper.py"]
        tests_governance_data_layer_test_sqlite_schema_root_py["(原型态 / prototype) test_sqlite_schema_root.py"]
        tests_governance_data_layer_test_symbol_index_py["(原型态 / prototype) test_symbol_index.py"]
        tests_governance_delegation_test_behavioral_sampler_py["(原型态 / prototype) test_behavioral_sampler.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_code_quality_test_function_discovery_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_code_quality_test_simplicity_auditor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_claim_required_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_claim_required_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_create_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_create_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_arch_reference_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_file_placement_ttl_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_dangling_reference_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_directory_contract_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_directory_contract_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_held_overlap_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_held_overlap_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_msg_exposure_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_commit_gates_test_msg_exposure_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_code_quality_test_function_discovery_py,tests_governance_code_quality_test_simplicity_auditor_py,tests_governance_commit_gates_test_arch_reference_gate_py,tests_governance_commit_gates_test_claim_required_gate_py,tests_governance_commit_gates_test_create_guard_py,tests_governance_commit_gates_test_dangling_reference_gate_py,tests_governance_commit_gates_test_directory_contract_gate_py,tests_governance_commit_gates_test_file_placement_ttl_gate_py,tests_governance_commit_gates_test_held_overlap_gate_py,tests_governance_commit_gates_test_module_id_consistency_gate_py,tests_governance_commit_gates_test_msg_exposure_gate_py,tests_governance_commit_gates_test_msg_style_gate_py,tests_governance_commit_gates_test_r5_digit_suffix_gate_py,tests_governance_commit_gates_test_ssot_redefinition_gate_py,tests_governance_commit_gates_test_ttl_gate_py,tests_governance_commit_gates_test_unsafe_dict_spread_gate_py,tests_governance_compliance_test_compliance_mapper_py,tests_governance_compliance_test_human_factors_py,tests_governance_compliance_test_load_bearing_py,tests_governance_compliance_test_owner_absent_py,tests_governance_compliance_test_quiet_period_monitor_py,tests_governance_compliance_test_right_to_be_forgotten_py,tests_governance_compliance_test_thematic_clusterer_py,tests_governance_context_governance_test_command_chain_length_gate_py,tests_governance_data_layer_test_cache_manager_py,tests_governance_data_layer_test_s3_snapshot_lifecycle_py,tests_governance_data_layer_test_sqlite_dumper_py,tests_governance_data_layer_test_sqlite_schema_root_py,tests_governance_data_layer_test_symbol_index_py,tests_governance_delegation_test_behavioral_sampler_py design
    class D_GOVERNANCE external_prod
```

### 第 34 页 / 共 56 页 / Page 34 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_delegation_test_behavioral_trust_checker_py["(原型态 / prototype) test_behavioral_trust_checker.py"]
        tests_governance_delegation_test_consequence_tracker_py["(原型态 / prototype) test_consequence_tracker.py"]
        tests_governance_delegation_test_continuous_trust_py["(原型态 / prototype) test_continuous_trust.py"]
        tests_governance_delegation_test_delegation_engine_py["(原型态 / prototype) test_delegation_engine.py"]
        tests_governance_delegation_test_parent_child_attributor_py["(原型态 / prototype) test_parent_child_attributor.py"]
        tests_governance_delegation_test_shadow_trust_validator_py["(原型态 / prototype) test_shadow_trust_validator.py"]
        tests_governance_delegation_test_trust_ring_manager_py["(原型态 / prototype) test_trust_ring_manager.py"]
        tests_governance_depgraph_test_depgraph_db_py["(原型态 / prototype) test_depgraph_db.py"]
        tests_governance_depgraph_test_depgraph_generator_design_protection_py["(原型态 / prototype) test_depgraph_generator_design_protection.py"]
        tests_governance_drift_test_dead_module_detector_py["(原型态 / prototype) test_dead_module_detector.py"]
        tests_governance_drift_test_diff_detector_py["(原型态 / prototype) test_diff_detector.py"]
        tests_governance_drift_test_ghost_scan_py["(原型态 / prototype) test_ghost_scan.py"]
        tests_governance_drift_test_governance_drift_fix_py["(原型态 / prototype) test_governance_drift_fix.py"]
        tests_governance_drift_test_micro_clone_detector_py["(原型态 / prototype) test_micro_clone_detector.py"]
        tests_governance_drift_test_stale_shared_detector_py["(原型态 / prototype) test_stale_shared_detector.py"]
        tests_governance_escalation_test_alternative_path_blocker_py["(原型态 / prototype) test_alternative_path_blocker.py"]
        tests_governance_escalation_test_result_types_py["(原型态 / prototype) test_result_types.py"]
        tests_governance_governance_e2e_test_naming_e2e_py["(原型态 / prototype) test_naming_e2e.py"]
        tests_governance_governance_e2e_test_validate_rule_frontmatter_red_blue_py["(原型态 / prototype) test_validate_rule_frontmatter_red_blue.py"]
        tests_governance_governance_misc_test_annotations_py["(原型态 / prototype) test_annotations.py"]
        tests_governance_governance_misc_test_bare_repo_scanner_py["(原型态 / prototype) test_bare_repo_scanner.py"]
        tests_governance_governance_misc_test_governance_result_types_py["(原型态 / prototype) test_governance_result_types.py"]
        tests_governance_governance_misc_test_mock_duplicate_generator_py["(原型态 / prototype) test_mock_duplicate_generator.py"]
        tests_governance_governance_misc_test_question_tracker_py["(原型态 / prototype) test_question_tracker.py"]
        tests_governance_integration_test_api_response_sanitizer_py["(原型态 / prototype) test_api_response_sanitizer.py"]
        tests_governance_integration_test_bandwidth_optimizer_py["(原型态 / prototype) test_bandwidth_optimizer.py"]
        tests_governance_integration_test_contract_py["(原型态 / prototype) test_contract.py"]
        tests_governance_integration_test_integration_hub_py["(原型态 / prototype) test_integration_hub.py"]
        tests_governance_integration_test_integrations_py["(原型态 / prototype) test_integrations.py"]
        tests_governance_integration_test_protocol_self_context_py["(原型态 / prototype) test_protocol_self_context.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_delegation_test_consequence_tracker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_delegation_test_behavioral_trust_checker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_delegation_test_parent_child_attributor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_delegation_test_shadow_trust_validator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_delegation_test_trust_ring_manager_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_delegation_test_delegation_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_delegation_test_delegation_engine_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_depgraph_test_depgraph_db_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_drift_test_ghost_scan_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_drift_test_diff_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_depgraph_test_depgraph_generator_design_protection_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_governance_depgraph_test_depgraph_generator_design_protection_py -.->|测试依赖 / test_depends| D_SHARED
    tests_governance_drift_test_dead_module_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_drift_test_governance_drift_fix_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_drift_test_micro_clone_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_delegation_test_behavioral_trust_checker_py,tests_governance_delegation_test_consequence_tracker_py,tests_governance_delegation_test_continuous_trust_py,tests_governance_delegation_test_delegation_engine_py,tests_governance_delegation_test_parent_child_attributor_py,tests_governance_delegation_test_shadow_trust_validator_py,tests_governance_delegation_test_trust_ring_manager_py,tests_governance_depgraph_test_depgraph_db_py,tests_governance_depgraph_test_depgraph_generator_design_protection_py,tests_governance_drift_test_dead_module_detector_py,tests_governance_drift_test_diff_detector_py,tests_governance_drift_test_ghost_scan_py,tests_governance_drift_test_governance_drift_fix_py,tests_governance_drift_test_micro_clone_detector_py,tests_governance_drift_test_stale_shared_detector_py,tests_governance_escalation_test_alternative_path_blocker_py,tests_governance_escalation_test_result_types_py,tests_governance_governance_e2e_test_naming_e2e_py,tests_governance_governance_e2e_test_validate_rule_frontmatter_red_blue_py,tests_governance_governance_misc_test_annotations_py,tests_governance_governance_misc_test_bare_repo_scanner_py,tests_governance_governance_misc_test_governance_result_types_py,tests_governance_governance_misc_test_mock_duplicate_generator_py,tests_governance_governance_misc_test_question_tracker_py,tests_governance_integration_test_api_response_sanitizer_py,tests_governance_integration_test_bandwidth_optimizer_py,tests_governance_integration_test_contract_py,tests_governance_integration_test_integration_hub_py,tests_governance_integration_test_integrations_py,tests_governance_integration_test_protocol_self_context_py design
    class D_GOVERNANCE,D_SHARED external_prod
```

### 第 35 页 / 共 56 页 / Page 35 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_integration_test_protocol_state_store_py["(原型态 / prototype) test_protocol_state_store.py"]
        tests_governance_integration_test_schema_schema_registry_py["(原型态 / prototype) test_schema_schema_registry.py"]
        tests_governance_integration_test_schema_schemas_py["(原型态 / prototype) test_schema_schemas.py"]
        tests_governance_integration_test_slo_contract_py["(原型态 / prototype) test_slo_contract.py"]
        tests_governance_integration_test_subagent_hook_propagator_py["(原型态 / prototype) test_subagent_hook_propagator.py"]
        tests_governance_integration_test_submodule_sync_py["(原型态 / prototype) test_submodule_sync.py"]
        tests_governance_lifecycle_test_bootstrapping_calibrator_py["(原型态 / prototype) test_bootstrapping_calibrator.py"]
        tests_governance_lifecycle_test_checkpoint_gc_py["(原型态 / prototype) test_checkpoint_gc.py"]
        tests_governance_lifecycle_test_coldstart_manager_py["(原型态 / prototype) test_coldstart_manager.py"]
        tests_governance_lifecycle_test_maintenance_window_adapter_py["(原型态 / prototype) test_maintenance_window_adapter.py"]
        tests_governance_lifecycle_test_post_live_verification_py["(原型态 / prototype) test_post_live_verification.py"]
        tests_governance_lifecycle_test_startup_shutdown_py["(原型态 / prototype) test_startup_shutdown.py"]
        tests_governance_lifecycle_test_startup_shutdown_cli_py["(原型态 / prototype) test_startup_shutdown_cli.py"]
        tests_governance_lifecycle_test_time_sync_py["(原型态 / prototype) test_time_sync.py"]
        tests_governance_lifecycle_test_venv_sync_py["(原型态 / prototype) test_venv_sync.py"]
        tests_governance_observability_test_app_panel_unit_py["(原型态 / prototype) test_app_panel_unit.py"]
        tests_governance_observability_test_confidence_estimator_py["(原型态 / prototype) test_confidence_estimator.py"]
        tests_governance_observability_test_confidence_quantifier_py["(原型态 / prototype) test_confidence_quantifier.py"]
        tests_governance_observability_test_hotspot_tracker_py["(原型态 / prototype) test_hotspot_tracker.py"]
        tests_governance_observability_test_instruction_bloat_detector_py["(原型态 / prototype) test_instruction_bloat_detector.py"]
        tests_governance_observability_test_meta_confidence_py["(原型态 / prototype) test_meta_confidence.py"]
        tests_governance_observability_test_meta_observability_py["(原型态 / prototype) test_meta_observability.py"]
        tests_governance_observability_test_p1_components_unit_py["(原型态 / prototype) test_p1_components_unit.py"]
        tests_governance_observability_test_report_py["(原型态 / prototype) test_report.py"]
        tests_governance_ops_test_clock_guard_py["(原型态 / prototype) test_clock_guard.py"]
        tests_governance_ops_test_daily_ops_py["(原型态 / prototype) test_daily_ops.py"]
        tests_governance_ops_test_env_watcher_py["(原型态 / prototype) test_env_watcher.py"]
        tests_governance_ops_test_exit_codes_py["(原型态 / prototype) test_exit_codes.py"]
        tests_governance_ops_test_health_monitor_py["(原型态 / prototype) test_health_monitor.py"]
        tests_governance_ops_test_runbook_generator_py["(原型态 / prototype) test_runbook_generator.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_integration_test_protocol_state_store_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_governance_integration_test_slo_contract_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    tests_governance_integration_test_schema_schema_registry_py -.->|测试依赖 / test_depends| D_INTEGRATION
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_governance_integration_test_schema_schema_registry_py -.->|测试依赖 / test_depends| D_SHARED
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_governance_integration_test_submodule_sync_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_integration_test_subagent_hook_propagator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_integration_test_schema_schemas_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_governance_integration_test_schema_schemas_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_governance_lifecycle_test_bootstrapping_calibrator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_lifecycle_test_maintenance_window_adapter_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_lifecycle_test_checkpoint_gc_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_governance_lifecycle_test_coldstart_manager_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_lifecycle_test_time_sync_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_FRONTEND["[生产态 / production] D_FRONTEND"]
    tests_governance_observability_test_app_panel_unit_py -.->|测试依赖 / test_depends| D_FRONTEND
    tests_governance_observability_test_app_panel_unit_py -.->|测试依赖 / test_depends| D_FRONTEND
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_integration_test_protocol_state_store_py,tests_governance_integration_test_schema_schema_registry_py,tests_governance_integration_test_schema_schemas_py,tests_governance_integration_test_slo_contract_py,tests_governance_integration_test_subagent_hook_propagator_py,tests_governance_integration_test_submodule_sync_py,tests_governance_lifecycle_test_bootstrapping_calibrator_py,tests_governance_lifecycle_test_checkpoint_gc_py,tests_governance_lifecycle_test_coldstart_manager_py,tests_governance_lifecycle_test_maintenance_window_adapter_py,tests_governance_lifecycle_test_post_live_verification_py,tests_governance_lifecycle_test_startup_shutdown_py,tests_governance_lifecycle_test_startup_shutdown_cli_py,tests_governance_lifecycle_test_time_sync_py,tests_governance_lifecycle_test_venv_sync_py,tests_governance_observability_test_app_panel_unit_py,tests_governance_observability_test_confidence_estimator_py,tests_governance_observability_test_confidence_quantifier_py,tests_governance_observability_test_hotspot_tracker_py,tests_governance_observability_test_instruction_bloat_detector_py,tests_governance_observability_test_meta_confidence_py,tests_governance_observability_test_meta_observability_py,tests_governance_observability_test_p1_components_unit_py,tests_governance_observability_test_report_py,tests_governance_ops_test_clock_guard_py,tests_governance_ops_test_daily_ops_py,tests_governance_ops_test_env_watcher_py,tests_governance_ops_test_exit_codes_py,tests_governance_ops_test_health_monitor_py,tests_governance_ops_test_runbook_generator_py design
    class D_GOVERNANCE,D_GOV_ENFORCEMENT,D_INTEGRATION,D_SHARED,D_INFRA_RECOVERY,D_FRONTEND external_prod
```

### 第 36 页 / 共 56 页 / Page 36 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_ops_test_scheduler_act_py["(原型态 / prototype) test_scheduler_act.py"]
        tests_governance_ops_test_success_validator_py["(原型态 / prototype) test_success_validator.py"]
        tests_governance_ops_test_verifier_py["(原型态 / prototype) test_verifier.py"]
        tests_governance_orchestrator_test_engine_sandbox_py["(原型态 / prototype) test_engine_sandbox.py"]
        tests_governance_orchestrator_test_mvep_orchestrator_py["(原型态 / prototype) test_mvep_orchestrator.py"]
        tests_governance_orchestrator_test_objective_tracker_py["(原型态 / prototype) test_objective_tracker.py"]
        tests_governance_orchestrator_test_prioritizer_py["(原型态 / prototype) test_prioritizer.py"]
        tests_governance_orchestrator_test_think_time_model_py["(原型态 / prototype) test_think_time_model.py"]
        tests_governance_persistence_test_base_repo_py["(原型态 / prototype) test_base_repo.py"]
        tests_governance_resilience_test_deadlock_detector_py["(原型态 / prototype) test_deadlock_detector.py"]
        tests_governance_resilience_test_doom_loop_guard_py["(原型态 / prototype) test_doom_loop_guard.py"]
        tests_governance_resilience_test_fail_mode_manager_py["(原型态 / prototype) test_fail_mode_manager.py"]
        tests_governance_resilience_test_fault_tolerance_py["(原型态 / prototype) test_fault_tolerance.py"]
        tests_governance_resilience_test_flash_crash_guard_py["(原型态 / prototype) test_flash_crash_guard.py"]
        tests_governance_resilience_test_interrupt_handler_py["(原型态 / prototype) test_interrupt_handler.py"]
        tests_governance_resilience_test_knowngoodstate_ledger_py["(原型态 / prototype) test_knowngoodstate_ledger.py"]
        tests_governance_resilience_test_last_resort_watchdog_py["(原型态 / prototype) test_last_resort_watchdog.py"]
        tests_governance_resilience_test_observation_window_guard_py["(原型态 / prototype) test_observation_window_guard.py"]
        tests_governance_resilience_test_policy_sandbox_py["(原型态 / prototype) test_policy_sandbox.py"]
        tests_governance_resilience_test_process_isolator_py["(原型态 / prototype) test_process_isolator.py"]
        tests_governance_resilience_test_provider_failover_py["(原型态 / prototype) test_provider_failover.py"]
        tests_governance_resilience_test_recovery_manifest_writer_py["(原型态 / prototype) test_recovery_manifest_writer.py"]
        tests_governance_resilience_test_silence_detector_py["(原型态 / prototype) test_silence_detector.py"]
        tests_governance_resilience_test_spiral_ews_py["(原型态 / prototype) test_spiral_ews.py"]
        tests_governance_resilience_test_stream_abort_guard_py["(原型态 / prototype) test_stream_abort_guard.py"]
        tests_governance_resilience_test_timeout_guard_py["(原型态 / prototype) test_timeout_guard.py"]
        tests_governance_resilience_test_warm_standby_py["(原型态 / prototype) test_warm_standby.py"]
        tests_governance_resilience_test_witness_isolation_py["(原型态 / prototype) test_witness_isolation.py"]
        tests_governance_rule_bridge_test_commit_gate_registry_py["(原型态 / prototype) test_commit_gate_registry.py"]
        tests_governance_rule_bridge_test_session_worktree_py["(原型态 / prototype) test_session_worktree.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_ops_test_success_validator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_orchestrator_test_objective_tracker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_ops_test_verifier_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_orchestrator_test_think_time_model_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_orchestrator_test_mvep_orchestrator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_orchestrator_test_engine_sandbox_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_orchestrator_test_prioritizer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_governance_persistence_test_base_repo_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_resilience_test_fail_mode_manager_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_resilience_test_doom_loop_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_resilience_test_deadlock_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_resilience_test_deadlock_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_resilience_test_deadlock_detector_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_resilience_test_interrupt_handler_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_governance_resilience_test_knowngoodstate_ledger_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_ops_test_scheduler_act_py,tests_governance_ops_test_success_validator_py,tests_governance_ops_test_verifier_py,tests_governance_orchestrator_test_engine_sandbox_py,tests_governance_orchestrator_test_mvep_orchestrator_py,tests_governance_orchestrator_test_objective_tracker_py,tests_governance_orchestrator_test_prioritizer_py,tests_governance_orchestrator_test_think_time_model_py,tests_governance_persistence_test_base_repo_py,tests_governance_resilience_test_deadlock_detector_py,tests_governance_resilience_test_doom_loop_guard_py,tests_governance_resilience_test_fail_mode_manager_py,tests_governance_resilience_test_fault_tolerance_py,tests_governance_resilience_test_flash_crash_guard_py,tests_governance_resilience_test_interrupt_handler_py,tests_governance_resilience_test_knowngoodstate_ledger_py,tests_governance_resilience_test_last_resort_watchdog_py,tests_governance_resilience_test_observation_window_guard_py,tests_governance_resilience_test_policy_sandbox_py,tests_governance_resilience_test_process_isolator_py,tests_governance_resilience_test_provider_failover_py,tests_governance_resilience_test_recovery_manifest_writer_py,tests_governance_resilience_test_silence_detector_py,tests_governance_resilience_test_spiral_ews_py,tests_governance_resilience_test_stream_abort_guard_py,tests_governance_resilience_test_timeout_guard_py,tests_governance_resilience_test_warm_standby_py,tests_governance_resilience_test_witness_isolation_py,tests_governance_rule_bridge_test_commit_gate_registry_py,tests_governance_rule_bridge_test_session_worktree_py design
    class D_GOVERNANCE,D_GOV_ENFORCEMENT,D_INFRA_RECOVERY external_prod
```

### 第 37 页 / 共 56 页 / Page 37 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_rule_bridge_test_ssot_gate_py["(原型态 / prototype) test_ssot_gate.py"]
        tests_governance_rule_enforcement_check_types_test_check_type_registry_py["(原型态 / prototype) test_check_type_registry.py"]
        tests_governance_rule_enforcement_gate_engine_test_adversarial_gate_integration_py["(原型态 / prototype) test_adversarial_gate_integration.py"]
        tests_governance_rule_enforcement_gate_engine_test_adversarial_validation_py["(原型态 / prototype) test_adversarial_validation.py"]
        tests_governance_rule_enforcement_gate_engine_test_adversarial_validation_gate_py["(原型态 / prototype) test_adversarial_validation_gate.py"]
        tests_governance_rule_enforcement_invariants_test_en_001_circular_dependency_py["(原型态 / prototype) test_en_001_circular_dependency.py"]
        tests_governance_rule_enforcement_invariants_test_en_002_enforcement_validator_py["(原型态 / prototype) test_en_002_enforcement_validator.py"]
        tests_governance_rule_enforcement_invariants_test_en_003_contract_compatibility_py["(原型态 / prototype) test_en_003_contract_compatibility.py"]
        tests_governance_rule_enforcement_invariants_test_en_process_lifecycle_gateway_py["(原型态 / prototype) test_en_process_lifecycle_gateway.py"]
        tests_governance_rule_enforcement_invariants_test_post_doc_review_py["(原型态 / prototype) test_post_doc_review.py"]
        tests_governance_rule_enforcement_invariants_test_zero_residue_check_py["(原型态 / prototype) test_zero_residue_check.py"]
        tests_governance_rule_enforcement_test_adaptive_threshold_py["(原型态 / prototype) test_adaptive_threshold.py"]
        tests_governance_rule_enforcement_test_adversarial_strategies_py["(原型态 / prototype) test_adversarial_strategies.py"]
        tests_governance_rule_enforcement_test_breaking_change_detector_py["(原型态 / prototype) test_breaking_change_detector.py"]
        tests_governance_rule_enforcement_test_end_to_end_walkthrough_py["(原型态 / prototype) test_end_to_end_walkthrough.py"]
        tests_governance_rule_enforcement_test_integration_test_runner_py["(原型态 / prototype) test_integration_test_runner.py"]
        tests_governance_rule_enforcement_test_kiss_enforcer_py["(原型态 / prototype) test_kiss_enforcer.py"]
        tests_governance_rule_enforcement_test_output_quality_gate_py["(原型态 / prototype) test_output_quality_gate.py"]
        tests_governance_rule_enforcement_test_secrets_guard_py["(原型态 / prototype) test_secrets_guard.py"]
        tests_governance_rule_enforcement_test_triple_alignment_py["(原型态 / prototype) test_triple_alignment.py"]
        tests_governance_scripts_governance_test_check_vocab_hardcode_py["(原型态 / prototype) test_check_vocab_hardcode.py"]
        tests_governance_scripts_governance_test_pre_write_gate_py["(原型态 / prototype) test_pre_write_gate.py"]
        tests_governance_security_test_extraction_safety_py["(原型态 / prototype) test_extraction_safety.py"]
        tests_governance_security_test_github_api_guard_py["(原型态 / prototype) test_github_api_guard.py"]
        tests_governance_security_test_governance_a2a_check_py["(原型态 / prototype) test_governance_a2a_check.py"]
        tests_governance_security_test_governance_approver_check_py["(原型态 / prototype) test_governance_approver_check.py"]
        tests_governance_security_test_governance_bootstrap_superadmin_py["(原型态 / prototype) test_governance_bootstrap_superadmin.py"]
        tests_governance_security_test_governance_capability_check_py["(原型态 / prototype) test_governance_capability_check.py"]
        tests_governance_security_test_governance_contracts_py["(原型态 / prototype) test_governance_contracts.py"]
        tests_governance_security_test_hooks_integrity_guard_py["(原型态 / prototype) test_hooks_integrity_guard.py"]
    end
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_governance_rule_enforcement_test_adaptive_threshold_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_test_adversarial_strategies_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_rule_bridge_test_ssot_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_rule_bridge_test_ssot_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_rule_bridge_test_ssot_gate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_GOV_SCRIPTS["[生产态 / production] D_GOV_SCRIPTS"]
    tests_governance_rule_bridge_test_ssot_gate_py -.->|测试依赖 / test_depends| D_GOV_SCRIPTS
    tests_governance_rule_enforcement_test_end_to_end_walkthrough_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_check_types_test_check_type_registry_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_test_breaking_change_detector_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_test_integration_test_runner_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_test_secrets_guard_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_test_output_quality_gate_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_gate_engine_test_adversarial_validation_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_gate_engine_test_adversarial_gate_integration_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_governance_rule_enforcement_gate_engine_test_adversarial_gate_integration_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_rule_bridge_test_ssot_gate_py,tests_governance_rule_enforcement_check_types_test_check_type_registry_py,tests_governance_rule_enforcement_gate_engine_test_adversarial_gate_integration_py,tests_governance_rule_enforcement_gate_engine_test_adversarial_validation_py,tests_governance_rule_enforcement_gate_engine_test_adversarial_validation_gate_py,tests_governance_rule_enforcement_invariants_test_en_001_circular_dependency_py,tests_governance_rule_enforcement_invariants_test_en_002_enforcement_validator_py,tests_governance_rule_enforcement_invariants_test_en_003_contract_compatibility_py,tests_governance_rule_enforcement_invariants_test_en_process_lifecycle_gateway_py,tests_governance_rule_enforcement_invariants_test_post_doc_review_py,tests_governance_rule_enforcement_invariants_test_zero_residue_check_py,tests_governance_rule_enforcement_test_adaptive_threshold_py,tests_governance_rule_enforcement_test_adversarial_strategies_py,tests_governance_rule_enforcement_test_breaking_change_detector_py,tests_governance_rule_enforcement_test_end_to_end_walkthrough_py,tests_governance_rule_enforcement_test_integration_test_runner_py,tests_governance_rule_enforcement_test_kiss_enforcer_py,tests_governance_rule_enforcement_test_output_quality_gate_py,tests_governance_rule_enforcement_test_secrets_guard_py,tests_governance_rule_enforcement_test_triple_alignment_py,tests_governance_scripts_governance_test_check_vocab_hardcode_py,tests_governance_scripts_governance_test_pre_write_gate_py,tests_governance_security_test_extraction_safety_py,tests_governance_security_test_github_api_guard_py,tests_governance_security_test_governance_a2a_check_py,tests_governance_security_test_governance_approver_check_py,tests_governance_security_test_governance_bootstrap_superadmin_py,tests_governance_security_test_governance_capability_check_py,tests_governance_security_test_governance_contracts_py,tests_governance_security_test_hooks_integrity_guard_py design
    class D_GOV_ENFORCEMENT,D_GOVERNANCE,D_GOV_SCRIPTS external_prod
```

### 第 38 页 / 共 56 页 / Page 38 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_governance_security_test_import_surface_tracker_py["(原型态 / prototype) test_import_surface_tracker.py"]
        tests_governance_security_test_ipi_defense_py["(原型态 / prototype) test_ipi_defense.py"]
        tests_governance_security_test_monoculture_guard_py["(原型态 / prototype) test_monoculture_guard.py"]
        tests_governance_security_test_sandbox_enforcer_py["(原型态 / prototype) test_sandbox_enforcer.py"]
        tests_governance_security_test_sbom_guard_py["(原型态 / prototype) test_sbom_guard.py"]
        tests_governance_security_test_security_config_scanner_py["(原型态 / prototype) test_security_config_scanner.py"]
        tests_governance_security_test_sensitivity_sweeper_py["(原型态 / prototype) test_sensitivity_sweeper.py"]
        tests_governance_security_test_signature_matcher_py["(原型态 / prototype) test_signature_matcher.py"]
        tests_governance_security_test_vulnerability_rescanner_py["(原型态 / prototype) test_vulnerability_rescanner.py"]
        tests_governance_shared_test_boot_hooks_unlock_py["(原型态 / prototype) test_boot_hooks_unlock.py"]
        tests_governance_shared_test_finding_py["(原型态 / prototype) test_finding.py"]
        tests_governance_shared_test_governance_db_py["(原型态 / prototype) test_governance_db.py"]
        tests_governance_shared_test_post_sync_validation_py["(原型态 / prototype) test_post_sync_validation.py"]
        tests_governance_shared_test_shared_evolver_py["(原型态 / prototype) test_shared_evolver.py"]
        tests_governance_shared_test_shared_lifecycle_manager_py["(原型态 / prototype) test_shared_lifecycle_manager.py"]
        tests_governance_test_ast_import_rewriter_py["(原型态 / prototype) test_ast_import_rewriter.py"]
        tests_governance_test_rule_patterns_py["(原型态 / prototype) test_rule_patterns.py"]
        tests_governance_trading_test_arbitrage_asymmetry_detector_py["(原型态 / prototype) test_arbitrage_asymmetry_detector.py"]
        tests_governance_trading_test_exchange_partition_detector_py["(原型态 / prototype) test_exchange_partition_detector.py"]
        tests_governance_trading_test_exchange_reg_monitor_py["(原型态 / prototype) test_exchange_reg_monitor.py"]
        tests_governance_trading_test_paper_live_transition_py["(原型态 / prototype) test_paper_live_transition.py"]
        tests_governance_trading_test_pricing_sync_py["(原型态 / prototype) test_pricing_sync.py"]
        tests_governance_trading_test_strategy_scoper_py["(原型态 / prototype) test_strategy_scoper.py"]
        tests_guard_test_guard_cascade_detector_py["(原型态 / prototype) test_guard_cascade_detector.py"]
        tests_guard_test_guard_complexity_budget_py["(原型态 / prototype) test_guard_complexity_budget.py"]
        tests_guard_test_guard_configuration_drift_monitor_py["(原型态 / prototype) test_guard_configuration_drift_monitor.py"]
        tests_guard_test_guard_interaction_topology_mapper_py["(原型态 / prototype) test_guard_interaction_topology_mapper.py"]
        tests_guard_test_guard_layers_root_py["(原型态 / prototype) test_guard_layers_root.py"]
        tests_guard_test_guard_oscillation_detector_py["(原型态 / prototype) test_guard_oscillation_detector.py"]
        tests_guard_test_guard_self_consistency_auditor_py["(原型态 / prototype) test_guard_self_consistency_auditor.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_governance_test_rule_patterns_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_ipi_defense_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_import_surface_tracker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_monoculture_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_signature_matcher_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_security_config_scanner_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_sensitivity_sweeper_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_governance_security_test_sbom_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_governance_security_test_vulnerability_rescanner_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_governance_shared_test_boot_hooks_unlock_py -.->|测试依赖 / test_depends| D_SHARED
    tests_governance_shared_test_boot_hooks_unlock_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    tests_governance_shared_test_boot_hooks_unlock_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_governance_shared_test_boot_hooks_unlock_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_governance_shared_test_governance_db_py -.->|测试依赖 / test_depends| D_SHARED
    tests_governance_shared_test_shared_evolver_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_governance_security_test_import_surface_tracker_py,tests_governance_security_test_ipi_defense_py,tests_governance_security_test_monoculture_guard_py,tests_governance_security_test_sandbox_enforcer_py,tests_governance_security_test_sbom_guard_py,tests_governance_security_test_security_config_scanner_py,tests_governance_security_test_sensitivity_sweeper_py,tests_governance_security_test_signature_matcher_py,tests_governance_security_test_vulnerability_rescanner_py,tests_governance_shared_test_boot_hooks_unlock_py,tests_governance_shared_test_finding_py,tests_governance_shared_test_governance_db_py,tests_governance_shared_test_post_sync_validation_py,tests_governance_shared_test_shared_evolver_py,tests_governance_shared_test_shared_lifecycle_manager_py,tests_governance_test_ast_import_rewriter_py,tests_governance_test_rule_patterns_py,tests_governance_trading_test_arbitrage_asymmetry_detector_py,tests_governance_trading_test_exchange_partition_detector_py,tests_governance_trading_test_exchange_reg_monitor_py,tests_governance_trading_test_paper_live_transition_py,tests_governance_trading_test_pricing_sync_py,tests_governance_trading_test_strategy_scoper_py,tests_guard_test_guard_cascade_detector_py,tests_guard_test_guard_complexity_budget_py,tests_guard_test_guard_configuration_drift_monitor_py,tests_guard_test_guard_interaction_topology_mapper_py,tests_guard_test_guard_layers_root_py,tests_guard_test_guard_oscillation_detector_py,tests_guard_test_guard_self_consistency_auditor_py design
    class D_GOVERNANCE,D_INFRA_RECOVERY,D_SHARED,D_INTEGRATION external_prod
```

### 第 39 页 / 共 56 页 / Page 39 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_infrastructure_test_arbiter_py["(原型态 / prototype) test_arbiter.py"]
        tests_infrastructure_test_arbitrator_py["(原型态 / prototype) test_arbitrator.py"]
        tests_infrastructure_test_audit_rename_completeness_py["(原型态 / prototype) test_audit_rename_completeness.py"]
        tests_infrastructure_test_cascade_guard_py["(原型态 / prototype) test_cascade_guard.py"]
        tests_infrastructure_test_classifier_root_py["(原型态 / prototype) test_classifier_root.py"]
        tests_infrastructure_test_commit_quality_gate_py["(原型态 / prototype) test_commit_quality_gate.py"]
        tests_infrastructure_test_conflict_detector_py["(原型态 / prototype) test_conflict_detector.py"]
        tests_infrastructure_test_cost_tracker_py["(原型态 / prototype) test_cost_tracker.py"]
        tests_infrastructure_test_dashboard_root_py["(原型态 / prototype) test_dashboard_root.py"]
        tests_infrastructure_test_deadlock_guard_py["(原型态 / prototype) test_deadlock_guard.py"]
        tests_infrastructure_test_dry_run_simulator_py["(原型态 / prototype) test_dry_run_simulator.py"]
        tests_infrastructure_test_f18_governance_adversarial_py["(原型态 / prototype) test_f18_governance_adversarial.py"]
        tests_infrastructure_test_finding_task_bridge_py["(原型态 / prototype) test_finding_task_bridge.py"]
        tests_infrastructure_test_forward_fix_runner_py["(原型态 / prototype) test_forward_fix_runner.py"]
        tests_infrastructure_test_graceful_degradation_planner_py["(原型态 / prototype) test_graceful_degradation_planner.py"]
        tests_infrastructure_test_index_generator_root_py["(原型态 / prototype) test_index_generator_root.py"]
        tests_infrastructure_test_infra_cache_py["(原型态 / prototype) test_infra_cache.py"]
        tests_infrastructure_test_infra_idempotency_py["(原型态 / prototype) test_infra_idempotency.py"]
        tests_infrastructure_test_infra_limiter_py["(原型态 / prototype) test_infra_limiter.py"]
        tests_infrastructure_test_infra_lock_py["(原型态 / prototype) test_infra_lock.py"]
        tests_infrastructure_test_infra_observer_py["(原型态 / prototype) test_infra_observer.py"]
        tests_infrastructure_test_infra_outbox_py["(原型态 / prototype) test_infra_outbox.py"]
        tests_infrastructure_test_infrastructure_base_py["(原型态 / prototype) test_infrastructure_base.py"]
        tests_infrastructure_test_kill_switch_sim_py["(原型态 / prototype) test_kill_switch_sim.py"]
        tests_infrastructure_test_lifecycle_root_py["(原型态 / prototype) test_lifecycle_root.py"]
        tests_infrastructure_test_livelock_detector_py["(原型态 / prototype) test_livelock_detector.py"]
        tests_infrastructure_test_mcp_adapter_py["(原型态 / prototype) test_mcp_adapter.py"]
        tests_infrastructure_test_mcp_boot_hooks_integration_py["(原型态 / prototype) test_mcp_boot_hooks_integration.py"]
        tests_infrastructure_test_mcp_full_lifecycle_e2e_py["(原型态 / prototype) test_mcp_full_lifecycle_e2e.py"]
        tests_infrastructure_test_mcp_health_check_recovery_py["(原型态 / prototype) test_mcp_health_check_recovery.py"]
    end
    D_INFRA_A2A["[生产态 / production] D_INFRA_A2A"]
    tests_infrastructure_test_arbiter_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_infrastructure_test_arbitrator_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_infrastructure_test_audit_rename_completeness_py -.->|测试依赖 / test_depends| D_SHARED
    tests_infrastructure_test_cascade_guard_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_infrastructure_test_classifier_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_classifier_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_conflict_detector_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_infrastructure_test_commit_quality_gate_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_infrastructure_test_cost_tracker_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_deadlock_guard_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_infrastructure_test_dashboard_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_dashboard_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_dry_run_simulator_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_f18_governance_adversarial_py -.->|测试依赖 / test_depends| D_SHARED
    tests_infrastructure_test_finding_task_bridge_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_infrastructure_test_arbiter_py,tests_infrastructure_test_arbitrator_py,tests_infrastructure_test_audit_rename_completeness_py,tests_infrastructure_test_cascade_guard_py,tests_infrastructure_test_classifier_root_py,tests_infrastructure_test_commit_quality_gate_py,tests_infrastructure_test_conflict_detector_py,tests_infrastructure_test_cost_tracker_py,tests_infrastructure_test_dashboard_root_py,tests_infrastructure_test_deadlock_guard_py,tests_infrastructure_test_dry_run_simulator_py,tests_infrastructure_test_f18_governance_adversarial_py,tests_infrastructure_test_finding_task_bridge_py,tests_infrastructure_test_forward_fix_runner_py,tests_infrastructure_test_graceful_degradation_planner_py,tests_infrastructure_test_index_generator_root_py,tests_infrastructure_test_infra_cache_py,tests_infrastructure_test_infra_idempotency_py,tests_infrastructure_test_infra_limiter_py,tests_infrastructure_test_infra_lock_py,tests_infrastructure_test_infra_observer_py,tests_infrastructure_test_infra_outbox_py,tests_infrastructure_test_infrastructure_base_py,tests_infrastructure_test_kill_switch_sim_py,tests_infrastructure_test_lifecycle_root_py,tests_infrastructure_test_livelock_detector_py,tests_infrastructure_test_mcp_adapter_py,tests_infrastructure_test_mcp_boot_hooks_integration_py,tests_infrastructure_test_mcp_full_lifecycle_e2e_py,tests_infrastructure_test_mcp_health_check_recovery_py design
    class D_INFRA_A2A,D_SHARED,D_INFRA_RUNTIME,D_INFRA_RECOVERY external_prod
```

### 第 40 页 / 共 56 页 / Page 40 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_infrastructure_test_mcp_idle_timeout_py["(原型态 / prototype) test_mcp_idle_timeout.py"]
        tests_infrastructure_test_mcp_signal_shutdown_py["(原型态 / prototype) test_mcp_signal_shutdown.py"]
        tests_infrastructure_test_message_router_py["(原型态 / prototype) test_message_router.py"]
        tests_infrastructure_test_metadata_py["(原型态 / prototype) test_metadata.py"]
        tests_infrastructure_test_preemption_manager_py["(原型态 / prototype) test_preemption_manager.py"]
        tests_infrastructure_test_push_notifier_py["(原型态 / prototype) test_push_notifier.py"]
        tests_infrastructure_test_pydantic_v2_migrator_py["(原型态 / prototype) test_pydantic_v2_migrator.py"]
        tests_infrastructure_test_reconciler_root_py["(原型态 / prototype) test_reconciler_root.py"]
        tests_infrastructure_test_registry_adapter_root_py["(原型态 / prototype) test_registry_adapter_root.py"]
        tests_infrastructure_test_registry_governance_infrastructure_py["(原型态 / prototype) test_registry_governance_infrastructure.py"]
        tests_infrastructure_test_registry_governance_root_py["(原型态 / prototype) test_registry_governance_root.py"]
        tests_infrastructure_test_scanner_root_py["(原型态 / prototype) test_scanner_root.py"]
        tests_infrastructure_test_span_stub_py["(原型态 / prototype) test_span_stub.py"]
        tests_infrastructure_test_split_brain_quorum_py["(原型态 / prototype) test_split_brain_quorum.py"]
        tests_infrastructure_test_streaming_py["(原型态 / prototype) test_streaming.py"]
        tests_infrastructure_test_supervisor_py["(原型态 / prototype) test_supervisor.py"]
        tests_infrastructure_test_telemetry_py["(原型态 / prototype) test_telemetry.py"]
        tests_infrastructure_test_topology_change_log_py["(原型态 / prototype) test_topology_change_log.py"]
        tests_infrastructure_test_trigger_monitor_py["(原型态 / prototype) test_trigger_monitor.py"]
        tests_infrastructure_test_trust_anchor_root_py["(原型态 / prototype) test_trust_anchor_root.py"]
        tests_infrastructure_test_warm_hot_gate_py["(原型态 / prototype) test_warm_hot_gate.py"]
        tests_intent_test_intent_archiver_py["(原型态 / prototype) test_intent_archiver.py"]
        tests_intent_test_intent_binder_root_py["(原型态 / prototype) test_intent_binder_root.py"]
        tests_intent_test_intent_driven_ops_py["(原型态 / prototype) test_intent_driven_ops.py"]
        tests_intent_test_intent_keyword_mapper_root_py["(原型态 / prototype) test_intent_keyword_mapper_root.py"]
        tests_intent_test_intent_parser_root_py["(原型态 / prototype) test_intent_parser_root.py"]
        tests_io_test_depgraph_schema_py["(原型态 / prototype) test_depgraph_schema.py"]
        tests_io_test_io_content_fingerprint_py["(原型态 / prototype) test_io_content_fingerprint.py"]
        tests_io_test_io_file_utils_py["(原型态 / prototype) test_io_file_utils.py"]
        tests_io_test_io_frontmatter_utils_py["(原型态 / prototype) test_io_frontmatter_utils.py"]
    end
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_infrastructure_test_mcp_idle_timeout_py -.->|测试依赖 / test_depends| D_SHARED
    tests_infrastructure_test_mcp_idle_timeout_py -.->|测试依赖 / test_depends| D_SHARED
    tests_infrastructure_test_mcp_idle_timeout_py -.->|测试依赖 / test_depends| D_SHARED
    D_INFRA_A2A["[生产态 / production] D_INFRA_A2A"]
    tests_infrastructure_test_message_router_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_infrastructure_test_message_router_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_infrastructure_test_mcp_signal_shutdown_py -.->|测试依赖 / test_depends| D_SHARED
    tests_infrastructure_test_mcp_signal_shutdown_py -.->|测试依赖 / test_depends| D_SHARED
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_infrastructure_test_metadata_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_infrastructure_test_preemption_manager_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_infrastructure_test_preemption_manager_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_pydantic_v2_migrator_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_registry_governance_infrastructure_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_push_notifier_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    tests_infrastructure_test_reconciler_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_infrastructure_test_reconciler_root_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_infrastructure_test_mcp_idle_timeout_py,tests_infrastructure_test_mcp_signal_shutdown_py,tests_infrastructure_test_message_router_py,tests_infrastructure_test_metadata_py,tests_infrastructure_test_preemption_manager_py,tests_infrastructure_test_push_notifier_py,tests_infrastructure_test_pydantic_v2_migrator_py,tests_infrastructure_test_reconciler_root_py,tests_infrastructure_test_registry_adapter_root_py,tests_infrastructure_test_registry_governance_infrastructure_py,tests_infrastructure_test_registry_governance_root_py,tests_infrastructure_test_scanner_root_py,tests_infrastructure_test_span_stub_py,tests_infrastructure_test_split_brain_quorum_py,tests_infrastructure_test_streaming_py,tests_infrastructure_test_supervisor_py,tests_infrastructure_test_telemetry_py,tests_infrastructure_test_topology_change_log_py,tests_infrastructure_test_trigger_monitor_py,tests_infrastructure_test_trust_anchor_root_py,tests_infrastructure_test_warm_hot_gate_py,tests_intent_test_intent_archiver_py,tests_intent_test_intent_binder_root_py,tests_intent_test_intent_driven_ops_py,tests_intent_test_intent_keyword_mapper_root_py,tests_intent_test_intent_parser_root_py,tests_io_test_depgraph_schema_py,tests_io_test_io_content_fingerprint_py,tests_io_test_io_file_utils_py,tests_io_test_io_frontmatter_utils_py design
    class D_SHARED,D_INFRA_A2A,D_INFRA_RUNTIME,D_GOV_ENFORCEMENT external_prod
```

### 第 41 页 / 共 56 页 / Page 41 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_io_test_io_paths_py["(原型态 / prototype) test_io_paths.py"]
        tests_io_test_io_serialization_py["(原型态 / prototype) test_io_serialization.py"]
        tests_io_test_mcp_launcher_py["(原型态 / prototype) test_mcp_launcher.py"]
        tests_io_test_mcp_task_claim_py["(原型态 / prototype) test_mcp_task_claim.py"]
        tests_io_test_verify_schema_health_py["(原型态 / prototype) test_verify_schema_health.py"]
        tests_kb_test_kb_activate_py["(原型态 / prototype) test_kb_activate.py"]
        tests_kb_test_kb_analyze_py["(原型态 / prototype) test_kb_analyze.py"]
        tests_kb_test_kb_batch_ingest_py["(原型态 / prototype) test_kb_batch_ingest.py"]
        tests_kb_test_kb_bootstrap_py["(原型态 / prototype) test_kb_bootstrap.py"]
        tests_kb_test_kb_embedding_migrate_py["(原型态 / prototype) test_kb_embedding_migrate.py"]
        tests_kb_test_kb_extract_py["(原型态 / prototype) test_kb_extract.py"]
        tests_kb_test_kb_freeze_py["(原型态 / prototype) test_kb_freeze.py"]
        tests_kb_test_kb_gate_py["(原型态 / prototype) test_kb_gate.py"]
        tests_kb_test_kb_gate_task_py["(原型态 / prototype) test_kb_gate_task.py"]
        tests_kb_test_kb_graph_validator_py["(原型态 / prototype) test_kb_graph_validator.py"]
        tests_kb_test_kb_ingest_py["(原型态 / prototype) test_kb_ingest.py"]
        tests_kb_test_kb_integrity_py["(原型态 / prototype) test_kb_integrity.py"]
        tests_kb_test_kb_migration_embedding_py["(原型态 / prototype) test_kb_migration_embedding.py"]
        tests_kb_test_kb_migration_gate_py["(原型态 / prototype) test_kb_migration_gate.py"]
        tests_kb_test_kb_pipeline_activate_py["(原型态 / prototype) test_kb_pipeline_activate.py"]
        tests_kb_test_kb_reranker_py["(原型态 / prototype) test_kb_reranker.py"]
        tests_kb_test_kb_self_test_py["(原型态 / prototype) test_kb_self_test.py"]
        tests_kb_test_kb_storage_backend_py["(原型态 / prototype) test_kb_storage_backend.py"]
        tests_kb_test_kb_triage_py["(原型态 / prototype) test_kb_triage.py"]
        tests_kb_test_kb_unified_memory_api_py["(原型态 / prototype) test_kb_unified_memory_api.py"]
        tests_kb_test_kb_verify_py["(原型态 / prototype) test_kb_verify.py"]
        tests_kb_test_kb_vms_memory_backend_py["(原型态 / prototype) test_kb_vms_memory_backend.py"]
        tests_kb_test_vector_memory_root_py["(原型态 / prototype) test_vector_memory_root.py"]
        tests_knowledge_engine_test_ke_quality_py["(原型态 / prototype) test_ke_quality.py"]
        tests_knowledge_engine_test_ke_tombstone_py["(原型态 / prototype) test_ke_tombstone.py"]
    end
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_io_test_mcp_launcher_py -.->|测试依赖 / test_depends| D_SHARED
    tests_io_test_io_serialization_py -.->|测试依赖 / test_depends| D_SHARED
    tests_io_test_io_serialization_py -.->|测试依赖 / test_depends| D_SHARED
    tests_io_test_io_paths_py -.->|测试依赖 / test_depends| D_SHARED
    tests_io_test_verify_schema_health_py -.->|测试依赖 / test_depends| D_SHARED
    tests_io_test_mcp_task_claim_py -.->|测试依赖 / test_depends| D_SHARED
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_io_test_mcp_task_claim_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INTEGRATION_GATEWAY["[生产态 / production] D_INTEGRATION_GATEWAY"]
    tests_io_test_mcp_task_claim_py -.->|测试依赖 / test_depends| D_INTEGRATION_GATEWAY
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_kb_test_kb_activate_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_INTELLIGENCE["[生产态 / production] D_INTELLIGENCE"]
    tests_kb_test_kb_activate_py -.->|测试依赖 / test_depends| D_INTELLIGENCE
    tests_kb_test_kb_analyze_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_kb_test_kb_analyze_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_kb_test_kb_bootstrap_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_kb_test_kb_freeze_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_kb_test_kb_embedding_migrate_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_io_test_io_paths_py,tests_io_test_io_serialization_py,tests_io_test_mcp_launcher_py,tests_io_test_mcp_task_claim_py,tests_io_test_verify_schema_health_py,tests_kb_test_kb_activate_py,tests_kb_test_kb_analyze_py,tests_kb_test_kb_batch_ingest_py,tests_kb_test_kb_bootstrap_py,tests_kb_test_kb_embedding_migrate_py,tests_kb_test_kb_extract_py,tests_kb_test_kb_freeze_py,tests_kb_test_kb_gate_py,tests_kb_test_kb_gate_task_py,tests_kb_test_kb_graph_validator_py,tests_kb_test_kb_ingest_py,tests_kb_test_kb_integrity_py,tests_kb_test_kb_migration_embedding_py,tests_kb_test_kb_migration_gate_py,tests_kb_test_kb_pipeline_activate_py,tests_kb_test_kb_reranker_py,tests_kb_test_kb_self_test_py,tests_kb_test_kb_storage_backend_py,tests_kb_test_kb_triage_py,tests_kb_test_kb_unified_memory_api_py,tests_kb_test_kb_verify_py,tests_kb_test_kb_vms_memory_backend_py,tests_kb_test_vector_memory_root_py,tests_knowledge_engine_test_ke_quality_py,tests_knowledge_engine_test_ke_tombstone_py design
    class D_SHARED,D_GOVERNANCE,D_INTEGRATION_GATEWAY,D_GOV_ENFORCEMENT,D_INTELLIGENCE external_prod
```

### 第 42 页 / 共 56 页 / Page 42 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_knowledge_engine_test_knowledge_bus_factor_monitor_py["(原型态 / prototype) test_knowledge_bus_factor_monitor.py"]
        tests_knowledge_engine_test_knowledge_capture_py["(原型态 / prototype) test_knowledge_capture.py"]
        tests_knowledge_engine_test_knowledge_distillation_py["(原型态 / prototype) test_knowledge_distillation.py"]
        tests_knowledge_engine_test_knowledge_distiller_py["(原型态 / prototype) test_knowledge_distiller.py"]
        tests_knowledge_engine_test_knowledge_freshness_py["(原型态 / prototype) test_knowledge_freshness.py"]
        tests_knowledge_engine_test_knowledge_injection_py["(原型态 / prototype) test_knowledge_injection.py"]
        tests_knowledge_engine_test_knowledge_injection_pre_flight_verifier_py["(原型态 / prototype) test_knowledge_injection_pre_flight_verifier.py"]
        tests_knowledge_engine_test_knowledge_market_py["(原型态 / prototype) test_knowledge_market.py"]
        tests_knowledge_engine_test_knowledge_packaging_py["(原型态 / prototype) test_knowledge_packaging.py"]
        tests_llm_security_test_adversarial_mutator_py["(原型态 / prototype) test_adversarial_mutator.py"]
        tests_llm_security_test_batch_fixer_py["(原型态 / prototype) test_batch_fixer.py"]
        tests_llm_security_test_behavior_audit_logger_py["(原型态 / prototype) test_behavior_audit_logger.py"]
        tests_llm_security_test_code_integrity_py["(原型态 / prototype) test_code_integrity.py"]
        tests_llm_security_test_cross_module_integration_llm_security_py["(原型态 / prototype) test_cross_module_integration_llm_security.py"]
        tests_llm_security_test_db_py["(原型态 / prototype) test_db.py"]
        tests_llm_security_test_dedup_extractor_py["(原型态 / prototype) test_dedup_extractor.py"]
        tests_llm_security_test_dep_cve_correlator_py["(原型态 / prototype) test_dep_cve_correlator.py"]
        tests_llm_security_test_dep_version_fixer_py["(原型态 / prototype) test_dep_version_fixer.py"]
        tests_llm_security_test_engine_root_py["(原型态 / prototype) test_engine_root.py"]
        tests_llm_security_test_fail_closed_py["(原型态 / prototype) test_fail_closed.py"]
        tests_llm_security_test_gateway_e2e_py["(原型态 / prototype) test_gateway_e2e.py"]
        tests_llm_security_test_injection_patterns_py["(原型态 / prototype) test_injection_patterns.py"]
        tests_llm_security_test_input_sanitizer_llm_security_py["(原型态 / prototype) test_input_sanitizer_llm_security.py"]
        tests_llm_security_test_interrupt_guard_py["(原型态 / prototype) test_interrupt_guard.py"]
        tests_llm_security_test_isolation_py["(原型态 / prototype) test_isolation.py"]
        tests_llm_security_test_l0_supply_chain_py["(原型态 / prototype) test_l0_supply_chain.py"]
        tests_llm_security_test_l1_input_defense_py["(原型态 / prototype) test_l1_input_defense.py"]
        tests_llm_security_test_l2_prompt_protection_py["(原型态 / prototype) test_l2_prompt_protection.py"]
        tests_llm_security_test_l2a_process_sandbox_py["(原型态 / prototype) test_l2a_process_sandbox.py"]
        tests_llm_security_test_l3_output_security_py["(原型态 / prototype) test_l3_output_security.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_knowledge_engine_test_knowledge_bus_factor_monitor_py -.->|测试依赖 / test_depends| D_TRADING
    tests_knowledge_engine_test_knowledge_capture_py -.->|测试依赖 / test_depends| D_TRADING
    tests_knowledge_engine_test_knowledge_freshness_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_knowledge_engine_test_knowledge_distiller_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_knowledge_engine_test_knowledge_distillation_py -.->|测试依赖 / test_depends| D_TRADING
    tests_knowledge_engine_test_knowledge_injection_pre_flight_verifier_py -.->|测试依赖 / test_depends| D_TRADING
    tests_knowledge_engine_test_knowledge_injection_py -.->|测试依赖 / test_depends| D_TRADING
    tests_knowledge_engine_test_knowledge_packaging_py -.->|测试依赖 / test_depends| D_TRADING
    D_SECURITY_LLM["[生产态 / production] D_SECURITY_LLM"]
    tests_llm_security_test_adversarial_mutator_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_knowledge_engine_test_knowledge_market_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_llm_security_test_db_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    tests_llm_security_test_db_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_llm_security_test_db_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_llm_security_test_db_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_llm_security_test_db_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_knowledge_engine_test_knowledge_bus_factor_monitor_py,tests_knowledge_engine_test_knowledge_capture_py,tests_knowledge_engine_test_knowledge_distillation_py,tests_knowledge_engine_test_knowledge_distiller_py,tests_knowledge_engine_test_knowledge_freshness_py,tests_knowledge_engine_test_knowledge_injection_py,tests_knowledge_engine_test_knowledge_injection_pre_flight_verifier_py,tests_knowledge_engine_test_knowledge_market_py,tests_knowledge_engine_test_knowledge_packaging_py,tests_llm_security_test_adversarial_mutator_py,tests_llm_security_test_batch_fixer_py,tests_llm_security_test_behavior_audit_logger_py,tests_llm_security_test_code_integrity_py,tests_llm_security_test_cross_module_integration_llm_security_py,tests_llm_security_test_db_py,tests_llm_security_test_dedup_extractor_py,tests_llm_security_test_dep_cve_correlator_py,tests_llm_security_test_dep_version_fixer_py,tests_llm_security_test_engine_root_py,tests_llm_security_test_fail_closed_py,tests_llm_security_test_gateway_e2e_py,tests_llm_security_test_injection_patterns_py,tests_llm_security_test_input_sanitizer_llm_security_py,tests_llm_security_test_interrupt_guard_py,tests_llm_security_test_isolation_py,tests_llm_security_test_l0_supply_chain_py,tests_llm_security_test_l1_input_defense_py,tests_llm_security_test_l2_prompt_protection_py,tests_llm_security_test_l2a_process_sandbox_py,tests_llm_security_test_l3_output_security_py design
    class D_TRADING,D_GOVERNANCE,D_SECURITY_LLM,D_GOV_ENFORCEMENT,D_INTEGRATION external_prod
```

### 第 43 页 / 共 56 页 / Page 43 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_llm_security_test_l4_agent_security_py["(原型态 / prototype) test_l4_agent_security.py"]
        tests_llm_security_test_l5_resource_protection_py["(原型态 / prototype) test_l5_resource_protection.py"]
        tests_llm_security_test_l6_observability_py["(原型态 / prototype) test_l6_observability.py"]
        tests_llm_security_test_l7_red_team_py["(原型态 / prototype) test_l7_red_team.py"]
        tests_llm_security_test_l7_validation_py["(原型态 / prototype) test_l7_validation.py"]
        tests_llm_security_test_l8_multi_agent_py["(原型态 / prototype) test_l8_multi_agent.py"]
        tests_llm_security_test_llm_cost_accounting_py["(原型态 / prototype) test_llm_cost_accounting.py"]
        tests_llm_security_test_llm_cost_router_py["(原型态 / prototype) test_llm_cost_router.py"]
        tests_llm_security_test_llm_fix_adapter_py["(原型态 / prototype) test_llm_fix_adapter.py"]
        tests_llm_security_test_llm_gateway_py["(原型态 / prototype) test_llm_gateway.py"]
        tests_llm_security_test_llm_provider_integrity_py["(原型态 / prototype) test_llm_provider_integrity.py"]
        tests_llm_security_test_llm_quality_regression_py["(原型态 / prototype) test_llm_quality_regression.py"]
        tests_llm_security_test_llm_security_py["(原型态 / prototype) test_llm_security.py"]
        tests_llm_security_test_metric_prompt_scanner_py["(原型态 / prototype) test_metric_prompt_scanner.py"]
        tests_llm_security_test_models_root_py["(原型态 / prototype) test_models_root.py"]
        tests_llm_security_test_orphan_detector_py["(原型态 / prototype) test_orphan_detector.py"]
        tests_llm_security_test_process_sandbox_llm_security_py["(原型态 / prototype) test_process_sandbox_llm_security.py"]
        tests_llm_security_test_remote_attestation_py["(原型态 / prototype) test_remote_attestation.py"]
        tests_llm_security_test_runtime_interceptor_py["(原型态 / prototype) test_runtime_interceptor.py"]
        tests_llm_security_test_scaffold_registrar_py["(原型态 / prototype) test_scaffold_registrar.py"]
        tests_llm_security_test_secret_rotation_py["(原型态 / prototype) test_secret_rotation.py"]
        tests_llm_security_test_secrets_py["(原型态 / prototype) test_secrets.py"]
        tests_llm_security_test_security_py["(原型态 / prototype) test_security.py"]
        tests_llm_security_test_security_capability_py["(原型态 / prototype) test_security_capability.py"]
        tests_llm_security_test_security_secrets_py["(原型态 / prototype) test_security_secrets.py"]
        tests_llm_security_test_security_ssot_guard_py["(原型态 / prototype) test_security_ssot_guard.py"]
        tests_llm_security_test_shadow_workspace_py["(原型态 / prototype) test_shadow_workspace.py"]
        tests_llm_security_test_wireheading_prevention_py["(原型态 / prototype) test_wireheading_prevention.py"]
        tests_llm_security_test_zombie_cleaner_py["(原型态 / prototype) test_zombie_cleaner.py"]
        tests_memory_test_memory_bank_root_py["(原型态 / prototype) test_memory_bank_root.py"]
    end
    D_SECURITY_LLM["[生产态 / production] D_SECURITY_LLM"]
    tests_llm_security_test_l5_resource_protection_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_llm_security_test_l5_resource_protection_py -.->|测试依赖 / test_depends| D_SHARED
    tests_llm_security_test_l5_resource_protection_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l4_agent_security_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l4_agent_security_py -.->|测试依赖 / test_depends| D_SHARED
    tests_llm_security_test_l4_agent_security_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l7_red_team_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l8_multi_agent_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l8_multi_agent_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l6_observability_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l6_observability_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l6_observability_py -.->|测试依赖 / test_depends| D_SHARED
    tests_llm_security_test_l7_validation_py -.->|测试依赖 / test_depends| D_SECURITY_LLM
    tests_llm_security_test_l7_validation_py -.->|测试依赖 / test_depends| D_SHARED
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_llm_security_test_llm_cost_accounting_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_llm_security_test_l4_agent_security_py,tests_llm_security_test_l5_resource_protection_py,tests_llm_security_test_l6_observability_py,tests_llm_security_test_l7_red_team_py,tests_llm_security_test_l7_validation_py,tests_llm_security_test_l8_multi_agent_py,tests_llm_security_test_llm_cost_accounting_py,tests_llm_security_test_llm_cost_router_py,tests_llm_security_test_llm_fix_adapter_py,tests_llm_security_test_llm_gateway_py,tests_llm_security_test_llm_provider_integrity_py,tests_llm_security_test_llm_quality_regression_py,tests_llm_security_test_llm_security_py,tests_llm_security_test_metric_prompt_scanner_py,tests_llm_security_test_models_root_py,tests_llm_security_test_orphan_detector_py,tests_llm_security_test_process_sandbox_llm_security_py,tests_llm_security_test_remote_attestation_py,tests_llm_security_test_runtime_interceptor_py,tests_llm_security_test_scaffold_registrar_py,tests_llm_security_test_secret_rotation_py,tests_llm_security_test_secrets_py,tests_llm_security_test_security_py,tests_llm_security_test_security_capability_py,tests_llm_security_test_security_secrets_py,tests_llm_security_test_security_ssot_guard_py,tests_llm_security_test_shadow_workspace_py,tests_llm_security_test_wireheading_prevention_py,tests_llm_security_test_zombie_cleaner_py,tests_memory_test_memory_bank_root_py design
    class D_SECURITY_LLM,D_SHARED,D_TRADING external_prod
```

### 第 44 页 / 共 56 页 / Page 44 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_memory_test_memory_guard_py["(原型态 / prototype) test_memory_guard.py"]
        tests_memory_test_memory_poison_guard_py["(原型态 / prototype) test_memory_poison_guard.py"]
        tests_memory_test_memory_provenance_py["(原型态 / prototype) test_memory_provenance.py"]
        tests_memory_test_memory_provenance_guard_py["(原型态 / prototype) test_memory_provenance_guard.py"]
        tests_memory_test_memory_self_check_py["(原型态 / prototype) test_memory_self_check.py"]
        tests_memory_test_vms_adversarial_hijack_py["(原型态 / prototype) test_vms_adversarial_hijack.py"]
        tests_memory_test_vms_adversarial_injection_py["(原型态 / prototype) test_vms_adversarial_injection.py"]
        tests_memory_test_vms_automation_py["(原型态 / prototype) test_vms_automation.py"]
        tests_memory_test_vms_lifecycle_py["(原型态 / prototype) test_vms_lifecycle.py"]
        tests_model_test_benchmark_suite_py["(原型态 / prototype) test_benchmark_suite.py"]
        tests_model_test_calibrate_model_diff_py["(原型态 / prototype) test_calibrate_model_diff.py"]
        tests_model_test_cli_py["(原型态 / prototype) test_cli.py"]
        tests_model_test_deepseek_v4_chat_py["(原型态 / prototype) test_deepseek_v4_chat.py"]
        tests_model_test_exam_orchestrator_py["(原型态 / prototype) test_exam_orchestrator.py"]
        tests_model_test_exam_test_cases_py["(原型态 / prototype) test_exam_test_cases.py"]
        tests_model_test_job_matcher_py["(原型态 / prototype) test_job_matcher.py"]
        tests_model_test_local_model_py["(原型态 / prototype) test_local_model.py"]
        tests_model_test_model_capability_exam_py["(原型态 / prototype) test_model_capability_exam.py"]
        tests_model_test_model_discovery_py["(原型态 / prototype) test_model_discovery.py"]
        tests_model_test_model_drift_detector_py["(原型态 / prototype) test_model_drift_detector.py"]
        tests_model_test_model_drift_monitor_py["(原型态 / prototype) test_model_drift_monitor.py"]
        tests_model_test_model_health_py["(原型态 / prototype) test_model_health.py"]
        tests_model_test_model_rotation_py["(原型态 / prototype) test_model_rotation.py"]
        tests_model_test_model_rotation_v2_py["(原型态 / prototype) test_model_rotation_v2.py"]
        tests_model_test_model_router_py["(原型态 / prototype) test_model_router.py"]
        tests_model_test_model_version_detector_py["(原型态 / prototype) test_model_version_detector.py"]
        tests_model_test_model_version_semantic_drift_py["(原型态 / prototype) test_model_version_semantic_drift.py"]
        tests_model_test_profiler_py["(原型态 / prototype) test_profiler.py"]
        tests_model_test_provider_data_py["(原型态 / prototype) test_provider_data.py"]
        tests_model_test_results_writer_py["(原型态 / prototype) test_results_writer.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_memory_test_memory_poison_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_memory_test_memory_guard_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_memory_test_memory_provenance_guard_py -.->|测试依赖 / test_depends| D_SECURITY
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_memory_test_memory_self_check_py -.->|测试依赖 / test_depends| D_TRADING
    tests_memory_test_memory_provenance_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    tests_memory_test_vms_automation_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_automation_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_automation_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_automation_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_automation_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_adversarial_injection_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_adversarial_injection_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_adversarial_injection_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_adversarial_injection_py -.->|测试依赖 / test_depends| D_INTEGRATION
    tests_memory_test_vms_adversarial_hijack_py -.->|测试依赖 / test_depends| D_INTEGRATION
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_memory_test_memory_guard_py,tests_memory_test_memory_poison_guard_py,tests_memory_test_memory_provenance_py,tests_memory_test_memory_provenance_guard_py,tests_memory_test_memory_self_check_py,tests_memory_test_vms_adversarial_hijack_py,tests_memory_test_vms_adversarial_injection_py,tests_memory_test_vms_automation_py,tests_memory_test_vms_lifecycle_py,tests_model_test_benchmark_suite_py,tests_model_test_calibrate_model_diff_py,tests_model_test_cli_py,tests_model_test_deepseek_v4_chat_py,tests_model_test_exam_orchestrator_py,tests_model_test_exam_test_cases_py,tests_model_test_job_matcher_py,tests_model_test_local_model_py,tests_model_test_model_capability_exam_py,tests_model_test_model_discovery_py,tests_model_test_model_drift_detector_py,tests_model_test_model_drift_monitor_py,tests_model_test_model_health_py,tests_model_test_model_rotation_py,tests_model_test_model_rotation_v2_py,tests_model_test_model_router_py,tests_model_test_model_version_detector_py,tests_model_test_model_version_semantic_drift_py,tests_model_test_profiler_py,tests_model_test_provider_data_py,tests_model_test_results_writer_py design
    class D_GOVERNANCE,D_SECURITY,D_TRADING,D_INTEGRATION external_prod
```

### 第 45 页 / 共 56 页 / Page 45 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_multi_test_multi_agent_collusion_detector_py["(原型态 / prototype) test_multi_agent_collusion_detector.py"]
        tests_multi_test_multi_agent_orchestrator_py["(原型态 / prototype) test_multi_agent_orchestrator.py"]
        tests_multi_test_multi_agent_root_py["(原型态 / prototype) test_multi_agent_root.py"]
        tests_multi_test_multi_instance_coord_py["(原型态 / prototype) test_multi_instance_coord.py"]
        tests_multi_test_multi_signal_correlator_py["(原型态 / prototype) test_multi_signal_correlator.py"]
        tests_multi_test_multi_turn_intent_analyzer_py["(原型态 / prototype) test_multi_turn_intent_analyzer.py"]
        tests_observability_test_facade_py["(原型态 / prototype) test_facade.py"]
        tests_observability_test_health_aggregator_root_py["(原型态 / prototype) test_health_aggregator_root.py"]
        tests_observability_test_health_probes_root_py["(原型态 / prototype) test_health_probes_root.py"]
        tests_observability_test_observability_health_py["(原型态 / prototype) test_observability_health.py"]
        tests_observability_test_observability_logging_py["(原型态 / prototype) test_observability_logging.py"]
        tests_observability_test_observability_metrics_py["(原型态 / prototype) test_observability_metrics.py"]
        tests_observability_test_observability_root_py["(原型态 / prototype) test_observability_root.py"]
        tests_observability_test_observability_tracing_py["(原型态 / prototype) test_observability_tracing.py"]
        tests_observability_test_structured_sink_py["(原型态 / prototype) test_structured_sink.py"]
        tests_observability_test_trace_bridge_py["(原型态 / prototype) test_trace_bridge.py"]
        tests_observability_test_trace_causal_bridge_py["(原型态 / prototype) test_trace_causal_bridge.py"]
        tests_observability_test_watchdog_py["(原型态 / prototype) test_watchdog.py"]
        tests_orchestrator_test_deferred_queue_py["(原型态 / prototype) test_deferred_queue.py"]
        tests_orchestrator_test_orchestrator_data_lifecycle_py["(原型态 / prototype) test_orchestrator_data_lifecycle.py"]
        tests_orchestrator_test_orchestrator_failure_matcher_py["(原型态 / prototype) test_orchestrator_failure_matcher.py"]
        tests_orchestrator_test_orchestrator_hallucination_detector_py["(原型态 / prototype) test_orchestrator_hallucination_detector.py"]
        tests_orchestrator_test_orchestrator_model_registry_py["(原型态 / prototype) test_orchestrator_model_registry.py"]
        tests_orchestrator_test_orchestrator_rollback_manager_py["(原型态 / prototype) test_orchestrator_rollback_manager.py"]
        tests_orchestrator_test_orchestrator_task_queue_py["(原型态 / prototype) test_orchestrator_task_queue.py"]
        tests_orchestrator_test_orchestrator_trigger_router_py["(原型态 / prototype) test_orchestrator_trigger_router.py"]
        tests_orchestrator_test_orchestrator_wave_generator_py["(原型态 / prototype) test_orchestrator_wave_generator.py"]
        tests_path_test_path_guard_py["(原型态 / prototype) test_path_guard.py"]
        tests_path_test_path_index_py["(原型态 / prototype) test_path_index.py"]
        tests_path_test_path_index_validator_py["(原型态 / prototype) test_path_index_validator.py"]
    end
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_multi_test_multi_agent_collusion_detector_py -.->|测试依赖 / test_depends| D_SECURITY
    D_INFRA_A2A["[生产态 / production] D_INFRA_A2A"]
    tests_multi_test_multi_agent_root_py -.->|测试依赖 / test_depends| D_INFRA_A2A
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_multi_test_multi_turn_intent_analyzer_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_multi_test_multi_instance_coord_py -.->|测试依赖 / test_depends| D_TRADING
    tests_multi_test_multi_agent_orchestrator_py -.->|测试依赖 / test_depends| D_TRADING
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_observability_test_observability_logging_py -.->|测试依赖 / test_depends| D_SHARED
    D_OPS["[生产态 / production] D_OPS"]
    tests_observability_test_observability_metrics_py -.->|测试依赖 / test_depends| D_OPS
    D_INFRA_TELEMETRY["[生产态 / production] D_INFRA_TELEMETRY"]
    tests_observability_test_observability_health_py -.->|测试依赖 / test_depends| D_INFRA_TELEMETRY
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_observability_test_observability_health_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_observability_test_observability_root_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_observability_test_observability_tracing_py -.->|测试依赖 / test_depends| D_SHARED
    tests_observability_test_observability_tracing_py -.->|测试依赖 / test_depends| D_OPS
    tests_multi_test_multi_signal_correlator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_observability_test_trace_causal_bridge_py -.->|测试依赖 / test_depends| D_TRADING
    tests_orchestrator_test_deferred_queue_py -.->|测试依赖 / test_depends| D_SHARED
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_multi_test_multi_agent_collusion_detector_py,tests_multi_test_multi_agent_orchestrator_py,tests_multi_test_multi_agent_root_py,tests_multi_test_multi_instance_coord_py,tests_multi_test_multi_signal_correlator_py,tests_multi_test_multi_turn_intent_analyzer_py,tests_observability_test_facade_py,tests_observability_test_health_aggregator_root_py,tests_observability_test_health_probes_root_py,tests_observability_test_observability_health_py,tests_observability_test_observability_logging_py,tests_observability_test_observability_metrics_py,tests_observability_test_observability_root_py,tests_observability_test_observability_tracing_py,tests_observability_test_structured_sink_py,tests_observability_test_trace_bridge_py,tests_observability_test_trace_causal_bridge_py,tests_observability_test_watchdog_py,tests_orchestrator_test_deferred_queue_py,tests_orchestrator_test_orchestrator_data_lifecycle_py,tests_orchestrator_test_orchestrator_failure_matcher_py,tests_orchestrator_test_orchestrator_hallucination_detector_py,tests_orchestrator_test_orchestrator_model_registry_py,tests_orchestrator_test_orchestrator_rollback_manager_py,tests_orchestrator_test_orchestrator_task_queue_py,tests_orchestrator_test_orchestrator_trigger_router_py,tests_orchestrator_test_orchestrator_wave_generator_py,tests_path_test_path_guard_py,tests_path_test_path_index_py,tests_path_test_path_index_validator_py design
    class D_SECURITY,D_INFRA_A2A,D_GOVERNANCE,D_TRADING,D_SHARED,D_OPS,D_INFRA_TELEMETRY,D_INFRA_RUNTIME external_prod
```

### 第 46 页 / 共 56 页 / Page 46 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_path_test_path_tree_generator_design_protection_py["(原型态 / prototype) test_path_tree_generator_design_protection.py"]
        tests_phase_test_phase_check_registry_py["(原型态 / prototype) test_phase_check_registry.py"]
        tests_phase_test_phase_executor_root_py["(原型态 / prototype) test_phase_executor_root.py"]
        tests_phase_test_phase_hold_py["(原型态 / prototype) test_phase_hold.py"]
        tests_phase_test_phase_manager_py["(原型态 / prototype) test_phase_manager.py"]
        tests_phase_test_phase_planner_py["(原型态 / prototype) test_phase_planner.py"]
        tests_pipeline_conftest_py["(原型态 / prototype) conftest.py"]
        tests_pipeline_test_alpha_signal_pipeline_py["(原型态 / prototype) test_alpha_signal_pipeline.py"]
        tests_pipeline_test_integration_test_pipeline_py["(原型态 / prototype) test_integration_test_pipeline.py"]
        tests_pipeline_test_pipeline_agent_bridge_py["(原型态 / prototype) test_pipeline_agent_bridge.py"]
        tests_pipeline_test_pipeline_bridge_py["(原型态 / prototype) test_pipeline_bridge.py"]
        tests_pipeline_test_pipeline_cost_tracker_py["(原型态 / prototype) test_pipeline_cost_tracker.py"]
        tests_pipeline_test_pipeline_lock_py["(原型态 / prototype) test_pipeline_lock.py"]
        tests_pipeline_test_pipeline_models_py["(原型态 / prototype) test_pipeline_models.py"]
        tests_pipeline_test_pipeline_orchestrator_auto_py["(原型态 / prototype) test_pipeline_orchestrator_auto.py"]
        tests_pipeline_test_pipeline_orchestrator_root_py["(原型态 / prototype) test_pipeline_orchestrator_root.py"]
        tests_pipeline_test_pipeline_roadmap_py["(原型态 / prototype) test_pipeline_roadmap.py"]
        tests_prompt_test_prompt_factory_governance_py["(原型态 / prototype) test_prompt_factory_governance.py"]
        tests_prompt_test_prompt_fingerprint_py["(原型态 / prototype) test_prompt_fingerprint.py"]
        tests_prompt_test_prompt_optimization_regression_detector_py["(原型态 / prototype) test_prompt_optimization_regression_detector.py"]
        tests_prompt_test_prompt_registry_root_py["(原型态 / prototype) test_prompt_registry_root.py"]
        tests_prompt_test_prompt_sanitizer_py["(原型态 / prototype) test_prompt_sanitizer.py"]
        tests_prompt_test_prompt_self_optimization_loop_py["(原型态 / prototype) test_prompt_self_optimization_loop.py"]
        tests_prompt_test_prompt_version_py["(原型态 / prototype) test_prompt_version.py"]
        tests_resource_test_resource_guard_py["(原型态 / prototype) test_resource_guard.py"]
        tests_resource_test_resource_optimization_py["(原型态 / prototype) test_resource_optimization.py"]
        tests_resource_test_resource_starvation_aware_py["(原型态 / prototype) test_resource_starvation_aware.py"]
        tests_risk_test_blast_radius_detector_py["(原型态 / prototype) test_blast_radius_detector.py"]
        tests_risk_test_ml_experiment_pipeline_py["(原型态 / prototype) test_ml_experiment_pipeline.py"]
        tests_risk_test_risk_matrix_py["(原型态 / prototype) test_risk_matrix.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_path_test_path_tree_generator_design_protection_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_path_test_path_tree_generator_design_protection_py -.->|测试依赖 / test_depends| D_SHARED
    D_FUNDAMENTAL_SIGNAL["[生产态 / production] D_FUNDAMENTAL_SIGNAL"]
    tests_pipeline_test_alpha_signal_pipeline_py -.->|测试依赖 / test_depends| D_FUNDAMENTAL_SIGNAL
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_phase_test_phase_planner_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_phase_test_phase_executor_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_pipeline_test_integration_test_pipeline_py -.->|测试依赖 / test_depends| D_TRADING
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_pipeline_test_pipeline_agent_bridge_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_pipeline_test_pipeline_agent_bridge_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_pipeline_test_pipeline_agent_bridge_py -.->|测试依赖 / test_depends| D_TRADING
    tests_pipeline_test_pipeline_lock_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_pipeline_test_pipeline_bridge_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_pipeline_test_pipeline_bridge_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_pipeline_test_pipeline_models_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_pipeline_test_pipeline_orchestrator_auto_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_INTEGRATION["[生产态 / production] D_INTEGRATION"]
    tests_pipeline_test_pipeline_orchestrator_auto_py -.->|测试依赖 / test_depends| D_INTEGRATION
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_path_test_path_tree_generator_design_protection_py,tests_phase_test_phase_check_registry_py,tests_phase_test_phase_executor_root_py,tests_phase_test_phase_hold_py,tests_phase_test_phase_manager_py,tests_phase_test_phase_planner_py,tests_pipeline_conftest_py,tests_pipeline_test_alpha_signal_pipeline_py,tests_pipeline_test_integration_test_pipeline_py,tests_pipeline_test_pipeline_agent_bridge_py,tests_pipeline_test_pipeline_bridge_py,tests_pipeline_test_pipeline_cost_tracker_py,tests_pipeline_test_pipeline_lock_py,tests_pipeline_test_pipeline_models_py,tests_pipeline_test_pipeline_orchestrator_auto_py,tests_pipeline_test_pipeline_orchestrator_root_py,tests_pipeline_test_pipeline_roadmap_py,tests_prompt_test_prompt_factory_governance_py,tests_prompt_test_prompt_fingerprint_py,tests_prompt_test_prompt_optimization_regression_detector_py,tests_prompt_test_prompt_registry_root_py,tests_prompt_test_prompt_sanitizer_py,tests_prompt_test_prompt_self_optimization_loop_py,tests_prompt_test_prompt_version_py,tests_resource_test_resource_guard_py,tests_resource_test_resource_optimization_py,tests_resource_test_resource_starvation_aware_py,tests_risk_test_blast_radius_detector_py,tests_risk_test_ml_experiment_pipeline_py,tests_risk_test_risk_matrix_py design
    class D_GOVERNANCE,D_SHARED,D_FUNDAMENTAL_SIGNAL,D_AUTONOMY_CORE,D_TRADING,D_INFRA_RUNTIME,D_INTEGRATION external_prod
```

### 第 47 页 / 共 56 页 / Page 47 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_risk_test_risk_mitigation_root_py["(原型态 / prototype) test_risk_mitigation_root.py"]
        tests_risk_test_risk_mitigation_tracker_py["(原型态 / prototype) test_risk_mitigation_tracker.py"]
        tests_risk_test_risk_mitigator_py["(原型态 / prototype) test_risk_mitigator.py"]
        tests_risk_test_risk_registry_root_py["(原型态 / prototype) test_risk_registry_root.py"]
        tests_risk_test_risk_ssot_py["(原型态 / prototype) test_risk_ssot.py"]
        tests_rollback_conftest_py["(原型态 / prototype) conftest.py"]
        tests_rollback_test_concurrency_guard_py["(原型态 / prototype) test_concurrency_guard.py"]
        tests_rollback_test_concurrency_guard_red_blue_py["(原型态 / prototype) test_concurrency_guard_red_blue.py"]
        tests_rollback_test_concurrent_mv_guard_py["(原型态 / prototype) test_concurrent_mv_guard.py"]
        tests_rollback_test_position_reconciler_py["(原型态 / prototype) test_position_reconciler.py"]
        tests_rollback_test_rollback_abuse_detector_py["(原型态 / prototype) test_rollback_abuse_detector.py"]
        tests_rollback_test_rollback_audit_nexus_py["(原型态 / prototype) test_rollback_audit_nexus.py"]
        tests_rollback_test_rollback_bootstrap_py["(原型态 / prototype) test_rollback_bootstrap.py"]
        tests_rollback_test_rollback_bridge_py["(原型态 / prototype) test_rollback_bridge.py"]
        tests_rollback_test_rollback_budget_py["(原型态 / prototype) test_rollback_budget.py"]
        tests_rollback_test_rollback_concurrent_extreme_py["(原型态 / prototype) test_rollback_concurrent_extreme.py"]
        tests_rollback_test_rollback_context_restorer_py["(原型态 / prototype) test_rollback_context_restorer.py"]
        tests_rollback_test_rollback_dashboard_py["(原型态 / prototype) test_rollback_dashboard.py"]
        tests_rollback_test_rollback_drill_py["(原型态 / prototype) test_rollback_drill.py"]
        tests_rollback_test_rollback_executor_root_py["(原型态 / prototype) test_rollback_executor_root.py"]
        tests_rollback_test_rollback_integration_py["(原型态 / prototype) test_rollback_integration.py"]
        tests_rollback_test_rollback_integrity_py["(原型态 / prototype) test_rollback_integrity.py"]
        tests_rollback_test_rollback_lock_py["(原型态 / prototype) test_rollback_lock.py"]
        tests_rollback_test_rollback_loop_detector_py["(原型态 / prototype) test_rollback_loop_detector.py"]
        tests_rollback_test_rollback_partial_extreme_py["(原型态 / prototype) test_rollback_partial_extreme.py"]
        tests_rollback_test_rollback_sandbox_py["(原型态 / prototype) test_rollback_sandbox.py"]
        tests_rollback_test_rollback_simulator_py["(原型态 / prototype) test_rollback_simulator.py"]
        tests_rollback_test_rollback_state_machine_py["(原型态 / prototype) test_rollback_state_machine.py"]
        tests_rollback_test_rollback_target_staleness_py["(原型态 / prototype) test_rollback_target_staleness.py"]
        tests_rollback_test_rollback_verifier_root_py["(原型态 / prototype) test_rollback_verifier_root.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_risk_test_risk_mitigation_tracker_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_risk_test_risk_mitigator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_risk_test_risk_registry_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_rollback_test_concurrency_guard_red_blue_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_POSITION["[生产态 / production] D_POSITION"]
    tests_rollback_test_position_reconciler_py -.->|测试依赖 / test_depends| D_POSITION
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_rollback_test_rollback_abuse_detector_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_rollback_test_concurrent_mv_guard_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_rollback_test_rollback_bootstrap_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_rollback_test_rollback_audit_nexus_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_risk_test_risk_ssot_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_risk_test_risk_ssot_py -.->|测试依赖 / test_depends| D_SHARED
    tests_rollback_test_rollback_budget_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_rollback_test_rollback_bridge_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_rollback_test_rollback_concurrent_extreme_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    tests_rollback_test_rollback_concurrent_extreme_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_risk_test_risk_mitigation_root_py,tests_risk_test_risk_mitigation_tracker_py,tests_risk_test_risk_mitigator_py,tests_risk_test_risk_registry_root_py,tests_risk_test_risk_ssot_py,tests_rollback_conftest_py,tests_rollback_test_concurrency_guard_py,tests_rollback_test_concurrency_guard_red_blue_py,tests_rollback_test_concurrent_mv_guard_py,tests_rollback_test_position_reconciler_py,tests_rollback_test_rollback_abuse_detector_py,tests_rollback_test_rollback_audit_nexus_py,tests_rollback_test_rollback_bootstrap_py,tests_rollback_test_rollback_bridge_py,tests_rollback_test_rollback_budget_py,tests_rollback_test_rollback_concurrent_extreme_py,tests_rollback_test_rollback_context_restorer_py,tests_rollback_test_rollback_dashboard_py,tests_rollback_test_rollback_drill_py,tests_rollback_test_rollback_executor_root_py,tests_rollback_test_rollback_integration_py,tests_rollback_test_rollback_integrity_py,tests_rollback_test_rollback_lock_py,tests_rollback_test_rollback_loop_detector_py,tests_rollback_test_rollback_partial_extreme_py,tests_rollback_test_rollback_sandbox_py,tests_rollback_test_rollback_simulator_py,tests_rollback_test_rollback_state_machine_py,tests_rollback_test_rollback_target_staleness_py,tests_rollback_test_rollback_verifier_root_py design
    class D_GOVERNANCE,D_TRADING,D_POSITION,D_INFRA_RECOVERY,D_GOV_ENFORCEMENT,D_SHARED external_prod
```

### 第 48 页 / 共 56 页 / Page 48 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_rollback_test_rollback_wal_py["(原型态 / prototype) test_rollback_wal.py"]
        tests_rule_test_rule_canary_manager_py["(原型态 / prototype) test_rule_canary_manager.py"]
        tests_rule_test_rule_debt_auditor_py["(原型态 / prototype) test_rule_debt_auditor.py"]
        tests_rule_test_rule_e2e_py["(原型态 / prototype) test_rule_e2e.py"]
        tests_rule_test_rule_injection_guard_py["(原型态 / prototype) test_rule_injection_guard.py"]
        tests_rule_test_rule_integration_py["(原型态 / prototype) test_rule_integration.py"]
        tests_rule_test_rule_red_blue_py["(原型态 / prototype) test_rule_red_blue.py"]
        tests_rule_test_rule_shadow_runner_py["(原型态 / prototype) test_rule_shadow_runner.py"]
        tests_safety_test_async_monitor_py["(原型态 / prototype) test_async_monitor.py"]
        tests_safety_test_attack_simulator_py["(原型态 / prototype) test_attack_simulator.py"]
        tests_safety_test_circuit_breaker_py["(原型态 / prototype) test_circuit_breaker.py"]
        tests_safety_test_commit_trigger_py["(原型态 / prototype) test_commit_trigger.py"]
        tests_safety_test_constitution_engine_py["(原型态 / prototype) test_constitution_engine.py"]
        tests_safety_test_defense_runner_py["(原型态 / prototype) test_defense_runner.py"]
        tests_safety_test_event_integration_py["(原型态 / prototype) test_event_integration.py"]
        tests_safety_test_game_day_scheduler_py["(原型态 / prototype) test_game_day_scheduler.py"]
        tests_safety_test_injection_engine_py["(原型态 / prototype) test_injection_engine.py"]
        tests_safety_test_phase_manager_integration_py["(原型态 / prototype) test_phase_manager_integration.py"]
        tests_safety_test_red_blue_validator_py["(原型态 / prototype) test_red_blue_validator.py"]
        tests_safety_test_red_blue_validator_tests_py["(原型态 / prototype) test_red_blue_validator_tests.py"]
        tests_safety_test_safety_brake_py["(原型态 / prototype) test_safety_brake.py"]
        tests_safety_test_safety_gate_l1_l27_py["(原型态 / prototype) test_safety_gate_l1_l27.py"]
        tests_safety_test_scheduler_safety_py["(原型态 / prototype) test_scheduler_safety.py"]
        tests_self_check_test_self_api_throttle_defense_py["(原型态 / prototype) test_self_api_throttle_defense.py"]
        tests_self_check_test_self_audit_py["(原型态 / prototype) test_self_audit.py"]
        tests_self_check_test_self_benchmark_py["(原型态 / prototype) test_self_benchmark.py"]
        tests_self_check_test_self_bottleneck_detector_py["(原型态 / prototype) test_self_bottleneck_detector.py"]
        tests_self_check_test_self_budget_tracker_py["(原型态 / prototype) test_self_budget_tracker.py"]
        tests_self_check_test_self_check_py["(原型态 / prototype) test_self_check.py"]
        tests_self_check_test_self_diagnosis_py["(原型态 / prototype) test_self_diagnosis.py"]
    end
    D_INFRA_RECOVERY["[生产态 / production] D_INFRA_RECOVERY"]
    tests_rollback_test_rollback_wal_py -.->|测试依赖 / test_depends| D_INFRA_RECOVERY
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_rule_test_rule_canary_manager_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_rule_test_rule_injection_guard_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_rule_test_rule_shadow_runner_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_rule_test_rule_e2e_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_rule_test_rule_integration_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_rule_test_rule_integration_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_safety_test_async_monitor_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_rule_test_rule_debt_auditor_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_safety_test_commit_trigger_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_rule_test_rule_red_blue_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_safety_test_attack_simulator_py -.->|测试依赖 / test_depends| D_TRADING
    tests_safety_test_defense_runner_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_safety_test_constitution_engine_py -.->|测试依赖 / test_depends| D_SECURITY
    tests_safety_test_game_day_scheduler_py -.->|测试依赖 / test_depends| D_SECURITY
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_rollback_test_rollback_wal_py,tests_rule_test_rule_canary_manager_py,tests_rule_test_rule_debt_auditor_py,tests_rule_test_rule_e2e_py,tests_rule_test_rule_injection_guard_py,tests_rule_test_rule_integration_py,tests_rule_test_rule_red_blue_py,tests_rule_test_rule_shadow_runner_py,tests_safety_test_async_monitor_py,tests_safety_test_attack_simulator_py,tests_safety_test_circuit_breaker_py,tests_safety_test_commit_trigger_py,tests_safety_test_constitution_engine_py,tests_safety_test_defense_runner_py,tests_safety_test_event_integration_py,tests_safety_test_game_day_scheduler_py,tests_safety_test_injection_engine_py,tests_safety_test_phase_manager_integration_py,tests_safety_test_red_blue_validator_py,tests_safety_test_red_blue_validator_tests_py,tests_safety_test_safety_brake_py,tests_safety_test_safety_gate_l1_l27_py,tests_safety_test_scheduler_safety_py,tests_self_check_test_self_api_throttle_defense_py,tests_self_check_test_self_audit_py,tests_self_check_test_self_benchmark_py,tests_self_check_test_self_bottleneck_detector_py,tests_self_check_test_self_budget_tracker_py,tests_self_check_test_self_check_py,tests_self_check_test_self_diagnosis_py design
    class D_INFRA_RECOVERY,D_GOV_ENFORCEMENT,D_SECURITY,D_GOVERNANCE,D_TRADING external_prod
```

### 第 49 页 / 共 56 页 / Page 49 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_self_check_test_self_diagnosis_data_leak_detector_py["(原型态 / prototype) test_self_diagnosis_data_leak_detector.py"]
        tests_self_check_test_self_evolution_fidelity_gate_py["(原型态 / prototype) test_self_evolution_fidelity_gate.py"]
        tests_self_check_test_self_ha_py["(原型态 / prototype) test_self_ha.py"]
        tests_self_check_test_self_heal_agent_py["(原型态 / prototype) test_self_heal_agent.py"]
        tests_self_check_test_self_health_monitor_py["(原型态 / prototype) test_self_health_monitor.py"]
        tests_self_check_test_self_llm_observability_py["(原型态 / prototype) test_self_llm_observability.py"]
        tests_self_check_test_self_modification_audit_py["(原型态 / prototype) test_self_modification_audit.py"]
        tests_self_check_test_self_modification_rate_limiter_py["(原型态 / prototype) test_self_modification_rate_limiter.py"]
        tests_self_check_test_self_monitor_py["(原型态 / prototype) test_self_monitor.py"]
        tests_self_check_test_self_reflection_py["(原型态 / prototype) test_self_reflection.py"]
        tests_self_check_test_self_scanner_py["(原型态 / prototype) test_self_scanner.py"]
        tests_self_check_test_self_test_py["(原型态 / prototype) test_self_test.py"]
        tests_self_check_test_self_test_verifier_py["(原型态 / prototype) test_self_test_verifier.py"]
        tests_self_check_test_self_upgrade_canary_py["(原型态 / prototype) test_self_upgrade_canary.py"]
        tests_self_check_test_self_validator_py["(原型态 / prototype) test_self_validator.py"]
        tests_semantic_auditor_init_py["(原型态 / prototype) __init__.py"]
        tests_semantic_auditor_test_blast_radius_py["(原型态 / prototype) test_blast_radius.py"]
        tests_semantic_auditor_test_blast_radius_red_team_py["(原型态 / prototype) test_blast_radius_red_team.py"]
        tests_semantic_auditor_test_semantic_auditor_py["(原型态 / prototype) test_semantic_auditor.py"]
        tests_semantic_auditor_test_semantic_cache_py["(原型态 / prototype) test_semantic_cache.py"]
        tests_semantic_auditor_test_semantic_diff_py["(原型态 / prototype) test_semantic_diff.py"]
        tests_semantic_auditor_test_semantic_intent_preservation_guard_py["(原型态 / prototype) test_semantic_intent_preservation_guard.py"]
        tests_semantic_auditor_test_semantic_rollback_tag_py["(原型态 / prototype) test_semantic_rollback_tag.py"]
        tests_semantic_auditor_test_semantic_similar_detector_py["(原型态 / prototype) test_semantic_similar_detector.py"]
        tests_session_test_session_conflict_py["(原型态 / prototype) test_session_conflict.py"]
        tests_session_test_session_learner_py["(原型态 / prototype) test_session_learner.py"]
        tests_session_test_session_lifecycle_py["(原型态 / prototype) test_session_lifecycle.py"]
        tests_session_test_session_manager_py["(原型态 / prototype) test_session_manager.py"]
        tests_session_test_session_smuggling_defense_py["(原型态 / prototype) test_session_smuggling_defense.py"]
        tests_skill_test_skill_attention_py["(原型态 / prototype) test_skill_attention.py"]
    end
    tests_semantic_auditor_test_semantic_diff_py -.->|config_depends / config_depends| tests_semantic_auditor_init_py
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_self_check_test_self_diagnosis_data_leak_detector_py -.->|测试依赖 / test_depends| D_TRADING
    tests_self_check_test_self_ha_py -.->|测试依赖 / test_depends| D_TRADING
    tests_self_check_test_self_modification_rate_limiter_py -.->|测试依赖 / test_depends| D_TRADING
    tests_self_check_test_self_llm_observability_py -.->|测试依赖 / test_depends| D_TRADING
    D_SECURITY["[生产态 / production] D_SECURITY"]
    tests_self_check_test_self_heal_agent_py -.->|测试依赖 / test_depends| D_SECURITY
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_self_check_test_self_monitor_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_self_check_test_self_evolution_fidelity_gate_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_self_check_test_self_health_monitor_py -.->|测试依赖 / test_depends| D_TRADING
    tests_self_check_test_self_reflection_py -.->|测试依赖 / test_depends| D_TRADING
    tests_self_check_test_self_scanner_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_self_check_test_self_test_verifier_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_self_check_test_self_modification_audit_py -.->|测试依赖 / test_depends| D_TRADING
    tests_self_check_test_self_test_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_self_check_test_self_validator_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_self_check_test_self_upgrade_canary_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_self_check_test_self_diagnosis_data_leak_detector_py,tests_self_check_test_self_evolution_fidelity_gate_py,tests_self_check_test_self_ha_py,tests_self_check_test_self_heal_agent_py,tests_self_check_test_self_health_monitor_py,tests_self_check_test_self_llm_observability_py,tests_self_check_test_self_modification_audit_py,tests_self_check_test_self_modification_rate_limiter_py,tests_self_check_test_self_monitor_py,tests_self_check_test_self_reflection_py,tests_self_check_test_self_scanner_py,tests_self_check_test_self_test_py,tests_self_check_test_self_test_verifier_py,tests_self_check_test_self_upgrade_canary_py,tests_self_check_test_self_validator_py,tests_semantic_auditor_init_py,tests_semantic_auditor_test_blast_radius_py,tests_semantic_auditor_test_blast_radius_red_team_py,tests_semantic_auditor_test_semantic_auditor_py,tests_semantic_auditor_test_semantic_cache_py,tests_semantic_auditor_test_semantic_diff_py,tests_semantic_auditor_test_semantic_intent_preservation_guard_py,tests_semantic_auditor_test_semantic_rollback_tag_py,tests_semantic_auditor_test_semantic_similar_detector_py,tests_session_test_session_conflict_py,tests_session_test_session_learner_py,tests_session_test_session_lifecycle_py,tests_session_test_session_manager_py,tests_session_test_session_smuggling_defense_py,tests_skill_test_skill_attention_py design
    class D_TRADING,D_SECURITY,D_GOVERNANCE,D_AUTONOMY_CORE external_prod
```

### 第 50 页 / 共 56 页 / Page 50 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_skill_test_skill_breakage_checker_py["(原型态 / prototype) test_skill_breakage_checker.py"]
        tests_skill_test_skill_cache_provider_py["(原型态 / prototype) test_skill_cache_provider.py"]
        tests_skill_test_skill_calibration_py["(原型态 / prototype) test_skill_calibration.py"]
        tests_skill_test_skill_canary_py["(原型态 / prototype) test_skill_canary.py"]
        tests_skill_test_skill_cognitive_preservation_py["(原型态 / prototype) test_skill_cognitive_preservation.py"]
        tests_skill_test_skill_compliance_py["(原型态 / prototype) test_skill_compliance.py"]
        tests_skill_test_skill_consensus_py["(原型态 / prototype) test_skill_consensus.py"]
        tests_skill_test_skill_constructor_py["(原型态 / prototype) test_skill_constructor.py"]
        tests_skill_test_skill_context_isolation_py["(原型态 / prototype) test_skill_context_isolation.py"]
        tests_skill_test_skill_contract_py["(原型态 / prototype) test_skill_contract.py"]
        tests_skill_test_skill_cross_model_py["(原型态 / prototype) test_skill_cross_model.py"]
        tests_skill_test_skill_di_py["(原型态 / prototype) test_skill_di.py"]
        tests_skill_test_skill_discovery_py["(原型态 / prototype) test_skill_discovery.py"]
        tests_skill_test_skill_durable_py["(原型态 / prototype) test_skill_durable.py"]
        tests_skill_test_skill_economics_py["(原型态 / prototype) test_skill_economics.py"]
        tests_skill_test_skill_efficacy_calibrator_py["(原型态 / prototype) test_skill_efficacy_calibrator.py"]
        tests_skill_test_skill_evaluator_py["(原型态 / prototype) test_skill_evaluator.py"]
        tests_skill_test_skill_executor_py["(原型态 / prototype) test_skill_executor.py"]
        tests_skill_test_skill_explain_py["(原型态 / prototype) test_skill_explain.py"]
        tests_skill_test_skill_factory_py["(原型态 / prototype) test_skill_factory.py"]
        tests_skill_test_skill_feature_flags_py["(原型态 / prototype) test_skill_feature_flags.py"]
        tests_skill_test_skill_feedback_py["(原型态 / prototype) test_skill_feedback.py"]
        tests_skill_test_skill_freshness_py["(原型态 / prototype) test_skill_freshness.py"]
        tests_skill_test_skill_freshness_ext_py["(原型态 / prototype) test_skill_freshness_ext.py"]
        tests_skill_test_skill_gitops_py["(原型态 / prototype) test_skill_gitops.py"]
        tests_skill_test_skill_guardrails_py["(原型态 / prototype) test_skill_guardrails.py"]
        tests_skill_test_skill_idempotency_py["(原型态 / prototype) test_skill_idempotency.py"]
        tests_skill_test_skill_kill_switch_py["(原型态 / prototype) test_skill_kill_switch.py"]
        tests_skill_test_skill_knowledge_base_py["(原型态 / prototype) test_skill_knowledge_base.py"]
        tests_skill_test_skill_kya_py["(原型态 / prototype) test_skill_kya.py"]
    end
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_skill_test_skill_cache_provider_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_cognitive_preservation_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_canary_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_breakage_checker_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_compliance_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_calibration_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_di_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_consensus_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_constructor_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_cross_model_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_contract_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_context_isolation_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_evaluator_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_discovery_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_executor_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_skill_test_skill_breakage_checker_py,tests_skill_test_skill_cache_provider_py,tests_skill_test_skill_calibration_py,tests_skill_test_skill_canary_py,tests_skill_test_skill_cognitive_preservation_py,tests_skill_test_skill_compliance_py,tests_skill_test_skill_consensus_py,tests_skill_test_skill_constructor_py,tests_skill_test_skill_context_isolation_py,tests_skill_test_skill_contract_py,tests_skill_test_skill_cross_model_py,tests_skill_test_skill_di_py,tests_skill_test_skill_discovery_py,tests_skill_test_skill_durable_py,tests_skill_test_skill_economics_py,tests_skill_test_skill_efficacy_calibrator_py,tests_skill_test_skill_evaluator_py,tests_skill_test_skill_executor_py,tests_skill_test_skill_explain_py,tests_skill_test_skill_factory_py,tests_skill_test_skill_feature_flags_py,tests_skill_test_skill_feedback_py,tests_skill_test_skill_freshness_py,tests_skill_test_skill_freshness_ext_py,tests_skill_test_skill_gitops_py,tests_skill_test_skill_guardrails_py,tests_skill_test_skill_idempotency_py,tests_skill_test_skill_kill_switch_py,tests_skill_test_skill_knowledge_base_py,tests_skill_test_skill_kya_py design
    class D_AUTONOMY_CORE external_prod
```

### 第 51 页 / 共 56 页 / Page 51 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_skill_test_skill_learning_py["(原型态 / prototype) test_skill_learning.py"]
        tests_skill_test_skill_lifecycle_py["(原型态 / prototype) test_skill_lifecycle.py"]
        tests_skill_test_skill_lineage_py["(原型态 / prototype) test_skill_lineage.py"]
        tests_skill_test_skill_loader_py["(原型态 / prototype) test_skill_loader.py"]
        tests_skill_test_skill_locking_py["(原型态 / prototype) test_skill_locking.py"]
        tests_skill_test_skill_model_py["(原型态 / prototype) test_skill_model.py"]
        tests_skill_test_skill_model_evolution_py["(原型态 / prototype) test_skill_model_evolution.py"]
        tests_skill_test_skill_observability_py["(原型态 / prototype) test_skill_observability.py"]
        tests_skill_test_skill_ontology_py["(原型态 / prototype) test_skill_ontology.py"]
        tests_skill_test_skill_postmortem_py["(原型态 / prototype) test_skill_postmortem.py"]
        tests_skill_test_skill_prompt_cache_py["(原型态 / prototype) test_skill_prompt_cache.py"]
        tests_skill_test_skill_prompt_opt_py["(原型态 / prototype) test_skill_prompt_opt.py"]
        tests_skill_test_skill_registry_root_py["(原型态 / prototype) test_skill_registry_root.py"]
        tests_skill_test_skill_resilience_py["(原型态 / prototype) test_skill_resilience.py"]
        tests_skill_test_skill_risk_mitigator_py["(原型态 / prototype) test_skill_risk_mitigator.py"]
        tests_skill_test_skill_router_py["(原型态 / prototype) test_skill_router.py"]
        tests_skill_test_skill_sandbox_py["(原型态 / prototype) test_skill_sandbox.py"]
        tests_skill_test_skill_schema_registry_py["(原型态 / prototype) test_skill_schema_registry.py"]
        tests_skill_test_skill_security_py["(原型态 / prototype) test_skill_security.py"]
        tests_skill_test_skill_shadow_py["(原型态 / prototype) test_skill_shadow.py"]
        tests_skill_test_skill_silent_failure_py["(原型态 / prototype) test_skill_silent_failure.py"]
        tests_skill_test_skill_team_optimizer_py["(原型态 / prototype) test_skill_team_optimizer.py"]
        tests_skill_test_skill_telemetry_py["(原型态 / prototype) test_skill_telemetry.py"]
        tests_skill_test_skill_temperature_py["(原型态 / prototype) test_skill_temperature.py"]
        tests_skill_test_skill_tokenomics_py["(原型态 / prototype) test_skill_tokenomics.py"]
        tests_skill_test_skill_translator_py["(原型态 / prototype) test_skill_translator.py"]
        tests_skill_test_skill_workflow_py["(原型态 / prototype) test_skill_workflow.py"]
        tests_task_test_task_gate_py["(原型态 / prototype) test_task_gate.py"]
        tests_task_test_task_model_learner_py["(原型态 / prototype) test_task_model_learner.py"]
        tests_task_test_task_repo_auto_commit_py["(原型态 / prototype) test_task_repo_auto_commit.py"]
    end
    D_AUTONOMY_CORE["[生产态 / production] D_AUTONOMY_CORE"]
    tests_skill_test_skill_lifecycle_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_lifecycle_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_learning_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_model_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_loader_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_lineage_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_postmortem_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_observability_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_prompt_cache_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_ontology_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_locking_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_resilience_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_registry_root_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_prompt_opt_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    tests_skill_test_skill_model_evolution_py -.->|测试依赖 / test_depends| D_AUTONOMY_CORE
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_skill_test_skill_learning_py,tests_skill_test_skill_lifecycle_py,tests_skill_test_skill_lineage_py,tests_skill_test_skill_loader_py,tests_skill_test_skill_locking_py,tests_skill_test_skill_model_py,tests_skill_test_skill_model_evolution_py,tests_skill_test_skill_observability_py,tests_skill_test_skill_ontology_py,tests_skill_test_skill_postmortem_py,tests_skill_test_skill_prompt_cache_py,tests_skill_test_skill_prompt_opt_py,tests_skill_test_skill_registry_root_py,tests_skill_test_skill_resilience_py,tests_skill_test_skill_risk_mitigator_py,tests_skill_test_skill_router_py,tests_skill_test_skill_sandbox_py,tests_skill_test_skill_schema_registry_py,tests_skill_test_skill_security_py,tests_skill_test_skill_shadow_py,tests_skill_test_skill_silent_failure_py,tests_skill_test_skill_team_optimizer_py,tests_skill_test_skill_telemetry_py,tests_skill_test_skill_temperature_py,tests_skill_test_skill_tokenomics_py,tests_skill_test_skill_translator_py,tests_skill_test_skill_workflow_py,tests_task_test_task_gate_py,tests_task_test_task_model_learner_py,tests_task_test_task_repo_auto_commit_py design
    class D_AUTONOMY_CORE external_prod
```

### 第 52 页 / 共 56 页 / Page 52 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_task_test_task_repo_gateway_e2e_py["(原型态 / prototype) test_task_repo_gateway_e2e.py"]
        tests_task_test_task_types_py["(原型态 / prototype) test_task_types.py"]
        tests_temporal_test_temporal_coherence_of_self_model_py["(原型态 / prototype) test_temporal_coherence_of_self_model.py"]
        tests_temporal_test_temporal_context_adapter_py["(原型态 / prototype) test_temporal_context_adapter.py"]
        tests_temporal_test_temporal_drift_tracker_py["(原型态 / prototype) test_temporal_drift_tracker.py"]
        tests_temporal_test_temporal_event_store_py["(原型态 / prototype) test_temporal_event_store.py"]
        tests_temporal_test_temporal_integrity_guard_py["(原型态 / prototype) test_temporal_integrity_guard.py"]
        tests_temporal_test_temporal_pattern_py["(原型态 / prototype) test_temporal_pattern.py"]
        tests_test_apply_decisiongraph_py["(原型态 / prototype) test_apply_decisiongraph.py"]
        tests_test_backtest_decisiongraph_adapter_py["(原型态 / prototype) test_backtest_decisiongraph_adapter.py"]
        tests_test_decision_graph_reader_py["(原型态 / prototype) test_decision_graph_reader.py"]
        tests_test_event_driven_engine_py["(原型态 / prototype) test_event_driven_engine.py"]
        tests_test_extract_decisiongraph_py["(原型态 / prototype) test_extract_decisiongraph.py"]
        tests_test_generate_decision_diagram_py["(原型态 / prototype) test_generate_decision_diagram.py"]
        tests_test_generate_decision_graph_py["(原型态 / prototype) test_generate_decision_graph.py"]
        tests_test_matching_engine_py["(原型态 / prototype) test_matching_engine.py"]
        tests_test_miniqmt_broker_py["(原型态 / prototype) test_miniqmt_broker.py"]
        tests_test_tick_replay_data_handler_py["(原型态 / prototype) test_tick_replay_data_handler.py"]
        tests_trading_test_admission_controller_py["(原型态 / prototype) test_admission_controller.py"]
        tests_trading_test_backpressure_manager_py["(原型态 / prototype) test_backpressure_manager.py"]
        tests_trading_test_backpressure_types_py["(原型态 / prototype) test_backpressure_types.py"]
        tests_trading_test_batch_orchestrator_py["(原型态 / prototype) test_batch_orchestrator.py"]
        tests_trading_test_behavioral_admission_py["(原型态 / prototype) test_behavioral_admission.py"]
        tests_trading_test_benchmark_runner_py["(原型态 / prototype) test_benchmark_runner.py"]
        tests_trading_test_blind_spot_closure_py["(原型态 / prototype) test_blind_spot_closure.py"]
        tests_trading_test_boot_cron_jobs_py["(原型态 / prototype) test_boot_cron_jobs.py"]
        tests_trading_test_boot_hooks_py["(原型态 / prototype) test_boot_hooks.py"]
        tests_trading_test_bulkhead_manager_py["(原型态 / prototype) test_bulkhead_manager.py"]
        tests_trading_test_circuit_breaker_manager_py["(原型态 / prototype) test_circuit_breaker_manager.py"]
        tests_trading_test_conductor_py["(原型态 / prototype) test_conductor.py"]
    end
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_test_extract_decisiongraph_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_BACKTEST["[生产态 / production] D_BACKTEST"]
    tests_test_backtest_decisiongraph_adapter_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_backtest_decisiongraph_adapter_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_event_driven_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_event_driven_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_event_driven_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_event_driven_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_decision_graph_reader_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_test_decision_graph_reader_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    tests_test_miniqmt_broker_py -.->|测试依赖 / test_depends| D_BACKTEST
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_test_miniqmt_broker_py -.->|测试依赖 / test_depends| D_TRADING
    tests_test_matching_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_matching_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_matching_engine_py -.->|测试依赖 / test_depends| D_BACKTEST
    tests_test_tick_replay_data_handler_py -.->|测试依赖 / test_depends| D_BACKTEST
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_task_test_task_repo_gateway_e2e_py,tests_task_test_task_types_py,tests_temporal_test_temporal_coherence_of_self_model_py,tests_temporal_test_temporal_context_adapter_py,tests_temporal_test_temporal_drift_tracker_py,tests_temporal_test_temporal_event_store_py,tests_temporal_test_temporal_integrity_guard_py,tests_temporal_test_temporal_pattern_py,tests_test_apply_decisiongraph_py,tests_test_backtest_decisiongraph_adapter_py,tests_test_decision_graph_reader_py,tests_test_event_driven_engine_py,tests_test_extract_decisiongraph_py,tests_test_generate_decision_diagram_py,tests_test_generate_decision_graph_py,tests_test_matching_engine_py,tests_test_miniqmt_broker_py,tests_test_tick_replay_data_handler_py,tests_trading_test_admission_controller_py,tests_trading_test_backpressure_manager_py,tests_trading_test_backpressure_types_py,tests_trading_test_batch_orchestrator_py,tests_trading_test_behavioral_admission_py,tests_trading_test_benchmark_runner_py,tests_trading_test_blind_spot_closure_py,tests_trading_test_boot_cron_jobs_py,tests_trading_test_boot_hooks_py,tests_trading_test_bulkhead_manager_py,tests_trading_test_circuit_breaker_manager_py,tests_trading_test_conductor_py design
    class D_GOVERNANCE,D_BACKTEST,D_TRADING external_prod
```

### 第 53 页 / 共 56 页 / Page 53 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_trading_test_construction_guide_py["(原型态 / prototype) test_construction_guide.py"]
        tests_trading_test_dead_letter_queue_py["(原型态 / prototype) test_dead_letter_queue.py"]
        tests_trading_test_degrade_cascade_py["(原型态 / prototype) test_degrade_cascade.py"]
        tests_trading_test_design_decisions_root_py["(原型态 / prototype) test_design_decisions_root.py"]
        tests_trading_test_disk_guard_py["(原型态 / prototype) test_disk_guard.py"]
        tests_trading_test_dlq_manager_root_py["(原型态 / prototype) test_dlq_manager_root.py"]
        tests_trading_test_dream_cycle_py["(原型态 / prototype) test_dream_cycle.py"]
        tests_trading_test_f14_pipeline_extreme_py["(原型态 / prototype) test_f14_pipeline_extreme.py"]
        tests_trading_test_f1_extreme_py["(原型态 / prototype) test_f1_extreme.py"]
        tests_trading_test_fault_types_py["(原型态 / prototype) test_fault_types.py"]
        tests_trading_test_feature_flag_py["(原型态 / prototype) test_feature_flag.py"]
        tests_trading_test_finalizer_py["(原型态 / prototype) test_finalizer.py"]
        tests_trading_test_finding_bridge_py["(原型态 / prototype) test_finding_bridge.py"]
        tests_trading_test_gpu_consensus_scheduler_py["(原型态 / prototype) test_gpu_consensus_scheduler.py"]
        tests_trading_test_housekeeping_py["(原型态 / prototype) test_housekeeping.py"]
        tests_trading_test_ide_health_daemon_py["(原型态 / prototype) test_ide_health_daemon.py"]
        tests_trading_test_incident_postmortem_py["(原型态 / prototype) test_incident_postmortem.py"]
        tests_trading_test_integration_registry_py["(原型态 / prototype) test_integration_registry.py"]
        tests_trading_test_lean_scanner_py["(原型态 / prototype) test_lean_scanner.py"]
        tests_trading_test_lifecycle_manager_py["(原型态 / prototype) test_lifecycle_manager.py"]
        tests_trading_test_module_onboarding_scanner_py["(原型态 / prototype) test_module_onboarding_scanner.py"]
        tests_trading_test_network_partition_py["(原型态 / prototype) test_network_partition.py"]
        tests_trading_test_night_shift_queue_py["(原型态 / prototype) test_night_shift_queue.py"]
        tests_trading_test_protection_index_py["(原型态 / prototype) test_protection_index.py"]
        tests_trading_test_reconciliation_loop_py["(原型态 / prototype) test_reconciliation_loop.py"]
        tests_trading_test_rolling_upgrade_py["(原型态 / prototype) test_rolling_upgrade.py"]
        tests_trading_test_routing_plugins_py["(原型态 / prototype) test_routing_plugins.py"]
        tests_trading_test_runtime_config_py["(原型态 / prototype) test_runtime_config.py"]
        tests_trading_test_schema_migration_py["(原型态 / prototype) test_schema_migration.py"]
        tests_trading_test_stability_guard_py["(原型态 / prototype) test_stability_guard.py"]
    end
    D_INFRA_RUNTIME["[生产态 / production] D_INFRA_RUNTIME"]
    tests_trading_test_dead_letter_queue_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_test_dead_letter_queue_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_trading_test_construction_guide_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_degrade_cascade_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_design_decisions_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_disk_guard_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_f14_pipeline_extreme_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_test_f14_pipeline_extreme_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_test_f14_pipeline_extreme_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_test_f14_pipeline_extreme_py -.->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_test_f14_pipeline_extreme_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_f14_pipeline_extreme_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_dlq_manager_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_f1_extreme_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_f1_extreme_py -.->|测试依赖 / test_depends| D_TRADING
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_trading_test_construction_guide_py,tests_trading_test_dead_letter_queue_py,tests_trading_test_degrade_cascade_py,tests_trading_test_design_decisions_root_py,tests_trading_test_disk_guard_py,tests_trading_test_dlq_manager_root_py,tests_trading_test_dream_cycle_py,tests_trading_test_f14_pipeline_extreme_py,tests_trading_test_f1_extreme_py,tests_trading_test_fault_types_py,tests_trading_test_feature_flag_py,tests_trading_test_finalizer_py,tests_trading_test_finding_bridge_py,tests_trading_test_gpu_consensus_scheduler_py,tests_trading_test_housekeeping_py,tests_trading_test_ide_health_daemon_py,tests_trading_test_incident_postmortem_py,tests_trading_test_integration_registry_py,tests_trading_test_lean_scanner_py,tests_trading_test_lifecycle_manager_py,tests_trading_test_module_onboarding_scanner_py,tests_trading_test_network_partition_py,tests_trading_test_night_shift_queue_py,tests_trading_test_protection_index_py,tests_trading_test_reconciliation_loop_py,tests_trading_test_rolling_upgrade_py,tests_trading_test_routing_plugins_py,tests_trading_test_runtime_config_py,tests_trading_test_schema_migration_py,tests_trading_test_stability_guard_py design
    class D_INFRA_RUNTIME,D_TRADING external_prod
```

### 第 54 页 / 共 56 页 / Page 54 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_trading_test_staging_area_py["(原型态 / prototype) test_staging_area.py"]
        tests_trading_test_startup_sequencer_py["(原型态 / prototype) test_startup_sequencer.py"]
        tests_trading_test_state_propagation_root_py["(原型态 / prototype) test_state_propagation_root.py"]
        tests_trading_test_state_synchronizer_root_py["(原型态 / prototype) test_state_synchronizer_root.py"]
        tests_trading_test_status_dashboard_py["(原型态 / prototype) test_status_dashboard.py"]
        tests_trading_test_stop_gate_py["(原型态 / prototype) test_stop_gate.py"]
        tests_trading_test_system_transfer_py["(原型态 / prototype) test_system_transfer.py"]
        tests_trading_test_teardown_manager_py["(原型态 / prototype) test_teardown_manager.py"]
        tests_trading_test_trading_contracts_py["(原型态 / prototype) test_trading_contracts.py"]
        tests_trading_test_trading_kill_switch_py["(原型态 / prototype) test_trading_kill_switch.py"]
        tests_trading_test_trading_session_lifecycle_py["(原型态 / prototype) test_trading_session_lifecycle.py"]
        tests_trading_test_version_manifest_py["(原型态 / prototype) test_version_manifest.py"]
        tests_trading_test_work_dag_py["(原型态 / prototype) test_work_dag.py"]
        tests_trading_test_work_orchestrator_py["(原型态 / prototype) test_work_orchestrator.py"]
        tests_trae_rules_test_g_trae_003_py["(原型态 / prototype) test_g_trae_003.py"]
        tests_trae_rules_test_g_trae_004_py["(原型态 / prototype) test_g_trae_004.py"]
        tests_trae_rules_test_g_trae_006_py["(原型态 / prototype) test_g_trae_006.py"]
        tests_trae_rules_test_g_trae_007_py["(原型态 / prototype) test_g_trae_007.py"]
        tests_trae_rules_test_g_trae_008_py["(原型态 / prototype) test_g_trae_008.py"]
        tests_trae_rules_test_g_trae_009_py["(原型态 / prototype) test_g_trae_009.py"]
        tests_trae_rules_test_g_trae_010_py["(原型态 / prototype) test_g_trae_010.py"]
        tests_trae_rules_test_g_trae_011_py["(原型态 / prototype) test_g_trae_011.py"]
        tests_trae_rules_test_g_trae_012_py["(原型态 / prototype) test_g_trae_012.py"]
        tests_trae_rules_test_g_trae_016_py["(原型态 / prototype) test_g_trae_016.py"]
        tests_trae_rules_test_g_trae_017_py["(原型态 / prototype) test_g_trae_017.py"]
        tests_trae_rules_test_g_trae_018_py["(原型态 / prototype) test_g_trae_018.py"]
        tests_trae_rules_test_g_trae_020_py["(原型态 / prototype) test_g_trae_020.py"]
        tests_trae_rules_test_g_trae_021_py["(原型态 / prototype) test_g_trae_021.py"]
        tests_trae_rules_test_g_trae_022_py["(原型态 / prototype) test_g_trae_022.py"]
        tests_trae_rules_test_g_trae_023_py["(原型态 / prototype) test_g_trae_023.py"]
    end
    D_TRADING["[生产态 / production] D_TRADING"]
    tests_trading_test_startup_sequencer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_staging_area_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_state_synchronizer_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_state_propagation_root_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_system_transfer_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_status_dashboard_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_status_dashboard_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_stop_gate_py -.->|测试依赖 / test_depends| D_TRADING
    D_GOVERNANCE["[生产态 / production] D_GOVERNANCE"]
    tests_trading_test_trading_session_lifecycle_py -.->|测试依赖 / test_depends| D_GOVERNANCE
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_trading_test_trading_session_lifecycle_py -.->|测试依赖 / test_depends| D_SHARED
    tests_trading_test_teardown_manager_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_version_manifest_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trading_test_work_dag_py -.->|测试依赖 / test_depends| D_TRADING
    tests_trae_rules_test_g_trae_003_py -.->|测试依赖 / test_depends| D_SHARED
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_trae_rules_test_g_trae_003_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_trading_test_staging_area_py,tests_trading_test_startup_sequencer_py,tests_trading_test_state_propagation_root_py,tests_trading_test_state_synchronizer_root_py,tests_trading_test_status_dashboard_py,tests_trading_test_stop_gate_py,tests_trading_test_system_transfer_py,tests_trading_test_teardown_manager_py,tests_trading_test_trading_contracts_py,tests_trading_test_trading_kill_switch_py,tests_trading_test_trading_session_lifecycle_py,tests_trading_test_version_manifest_py,tests_trading_test_work_dag_py,tests_trading_test_work_orchestrator_py,tests_trae_rules_test_g_trae_003_py,tests_trae_rules_test_g_trae_004_py,tests_trae_rules_test_g_trae_006_py,tests_trae_rules_test_g_trae_007_py,tests_trae_rules_test_g_trae_008_py,tests_trae_rules_test_g_trae_009_py,tests_trae_rules_test_g_trae_010_py,tests_trae_rules_test_g_trae_011_py,tests_trae_rules_test_g_trae_012_py,tests_trae_rules_test_g_trae_016_py,tests_trae_rules_test_g_trae_017_py,tests_trae_rules_test_g_trae_018_py,tests_trae_rules_test_g_trae_020_py,tests_trae_rules_test_g_trae_021_py,tests_trae_rules_test_g_trae_022_py,tests_trae_rules_test_g_trae_023_py design
    class D_TRADING,D_GOVERNANCE,D_SHARED,D_GOV_ENFORCEMENT external_prod
```

### 第 55 页 / 共 56 页 / Page 55 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_trae_rules_test_g_trae_024_py["(原型态 / prototype) test_g_trae_024.py"]
        tests_trae_rules_test_g_trae_025_py["(原型态 / prototype) test_g_trae_025.py"]
        tests_trae_rules_test_g_trae_026_py["(原型态 / prototype) test_g_trae_026.py"]
        tests_trae_rules_test_g_trae_027_py["(原型态 / prototype) test_g_trae_027.py"]
        tests_trae_rules_test_g_trae_028_py["(原型态 / prototype) test_g_trae_028.py"]
        tests_trae_rules_test_g_trae_029_py["(原型态 / prototype) test_g_trae_029.py"]
        tests_trae_rules_test_g_trae_030_py["(原型态 / prototype) test_g_trae_030.py"]
        tests_trae_rules_test_g_trae_031_py["(原型态 / prototype) test_g_trae_031.py"]
        tests_trae_rules_test_g_trae_032_py["(原型态 / prototype) test_g_trae_032.py"]
        tests_trae_rules_test_g_trae_033_py["(原型态 / prototype) test_g_trae_033.py"]
        tests_trae_rules_test_g_trae_034_py["(原型态 / prototype) test_g_trae_034.py"]
        tests_trae_rules_test_g_trae_035_py["(原型态 / prototype) test_g_trae_035.py"]
        tests_trae_rules_test_g_trae_036_py["(原型态 / prototype) test_g_trae_036.py"]
        tests_trae_rules_test_g_trae_037_py["(原型态 / prototype) test_g_trae_037.py"]
        tests_trae_rules_test_g_trae_038_py["(原型态 / prototype) test_g_trae_038.py"]
        tests_trae_rules_test_g_trae_039_py["(原型态 / prototype) test_g_trae_039.py"]
        tests_trae_rules_test_g_trae_040_py["(原型态 / prototype) test_g_trae_040.py"]
        tests_trae_rules_test_g_trae_041_py["(原型态 / prototype) test_g_trae_041.py"]
        tests_trae_rules_test_g_trae_042_py["(原型态 / prototype) test_g_trae_042.py"]
        tests_trae_rules_test_g_trae_043_py["(原型态 / prototype) test_g_trae_043.py"]
        tests_trae_rules_test_g_trae_044_py["(原型态 / prototype) test_g_trae_044.py"]
        tests_trae_rules_test_g_trae_045_py["(原型态 / prototype) test_g_trae_045.py"]
        tests_trae_rules_test_g_trae_046_py["(原型态 / prototype) test_g_trae_046.py"]
        tests_trae_rules_test_g_trae_047_py["(原型态 / prototype) test_g_trae_047.py"]
        tests_trae_rules_test_g_trae_048_py["(原型态 / prototype) test_g_trae_048.py"]
        tests_trae_rules_test_g_trae_049_py["(原型态 / prototype) test_g_trae_049.py"]
        tests_trae_rules_test_g_trae_050_py["(原型态 / prototype) test_g_trae_050.py"]
        tests_trae_rules_test_g_trae_051_py["(原型态 / prototype) test_g_trae_051.py"]
        tests_trae_rules_test_g_trae_052_py["(原型态 / prototype) test_g_trae_052.py"]
        tests_trae_rules_test_g_trae_053_py["(原型态 / prototype) test_g_trae_053.py"]
    end
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_trae_rules_test_g_trae_025_py -.->|测试依赖 / test_depends| D_SHARED
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_trae_rules_test_g_trae_025_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_025_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_024_py -.->|测试依赖 / test_depends| D_SHARED
    tests_trae_rules_test_g_trae_024_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_024_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_026_py -.->|测试依赖 / test_depends| D_SHARED
    tests_trae_rules_test_g_trae_026_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_026_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_027_py -.->|测试依赖 / test_depends| D_SHARED
    tests_trae_rules_test_g_trae_027_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_027_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_029_py -.->|测试依赖 / test_depends| D_SHARED
    tests_trae_rules_test_g_trae_029_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_029_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_trae_rules_test_g_trae_024_py,tests_trae_rules_test_g_trae_025_py,tests_trae_rules_test_g_trae_026_py,tests_trae_rules_test_g_trae_027_py,tests_trae_rules_test_g_trae_028_py,tests_trae_rules_test_g_trae_029_py,tests_trae_rules_test_g_trae_030_py,tests_trae_rules_test_g_trae_031_py,tests_trae_rules_test_g_trae_032_py,tests_trae_rules_test_g_trae_033_py,tests_trae_rules_test_g_trae_034_py,tests_trae_rules_test_g_trae_035_py,tests_trae_rules_test_g_trae_036_py,tests_trae_rules_test_g_trae_037_py,tests_trae_rules_test_g_trae_038_py,tests_trae_rules_test_g_trae_039_py,tests_trae_rules_test_g_trae_040_py,tests_trae_rules_test_g_trae_041_py,tests_trae_rules_test_g_trae_042_py,tests_trae_rules_test_g_trae_043_py,tests_trae_rules_test_g_trae_044_py,tests_trae_rules_test_g_trae_045_py,tests_trae_rules_test_g_trae_046_py,tests_trae_rules_test_g_trae_047_py,tests_trae_rules_test_g_trae_048_py,tests_trae_rules_test_g_trae_049_py,tests_trae_rules_test_g_trae_050_py,tests_trae_rules_test_g_trae_051_py,tests_trae_rules_test_g_trae_052_py,tests_trae_rules_test_g_trae_053_py design
    class D_SHARED,D_GOV_ENFORCEMENT external_prod
```

### 第 56 页 / 共 56 页 / Page 56 of 56

```mermaid
graph TD
    subgraph D_AUDITTEST["D_AUDITTEST 审计测试套件"]
        tests_trae_rules_test_g_trae_054_py["(原型态 / prototype) test_g_trae_054.py"]
        tests_trae_rules_test_g_trae_055_py["(原型态 / prototype) test_g_trae_055.py"]
        tests_utils_test_foundation_deprecation_py["(原型态 / prototype) test_foundation_deprecation.py"]
        tests_utils_test_foundation_env_py["(原型态 / prototype) test_foundation_env.py"]
        tests_utils_test_foundation_errors_py["(原型态 / prototype) test_foundation_errors.py"]
        tests_utils_test_foundation_flags_py["(原型态 / prototype) test_foundation_flags.py"]
        tests_utils_test_resilience_fallback_py["(原型态 / prototype) test_resilience_fallback.py"]
        tests_utils_test_resilience_retry_py["(原型态 / prototype) test_resilience_retry.py"]
        tests_utils_test_utils_context_py["(原型态 / prototype) test_utils_context.py"]
        tests_utils_test_utils_diff_utils_py["(原型态 / prototype) test_utils_diff_utils.py"]
        tests_utils_test_utils_migration_py["(原型态 / prototype) test_utils_migration.py"]
        tests_utils_test_utils_pagination_py["(原型态 / prototype) test_utils_pagination.py"]
        tests_utils_test_utils_testing_py["(原型态 / prototype) test_utils_testing.py"]
        tests_utils_test_utils_time_utils_py["(原型态 / prototype) test_utils_time_utils.py"]
        tests_utils_test_version_py["(原型态 / prototype) test_version.py"]
        tests_zephyr_data_init_py["(原型态 / prototype) __init__.py"]
        tests_zephyr_data_test_alerter_py["(原型态 / prototype) test_alerter.py"]
        tests_zephyr_data_test_ch_writer_py["(原型态 / prototype) test_ch_writer.py"]
        tests_zephyr_data_test_cli_py["(原型态 / prototype) test_cli.py"]
        tests_zephyr_data_test_metrics_py["(原型态 / prototype) test_metrics.py"]
        tests_zephyr_data_test_policy_registry_py["(原型态 / prototype) test_policy_registry.py"]
        tests_zephyr_data_test_progress_store_py["(原型态 / prototype) test_progress_store.py"]
        tests_zephyr_data_test_provider_base_py["(原型态 / prototype) test_provider_base.py"]
        tests_zephyr_data_test_providers_py["(原型态 / prototype) test_providers.py"]
        tests_zephyr_data_test_providers_stage3_py["(原型态 / prototype) test_providers_stage3.py"]
        tests_zephyr_data_test_scheduler_py["(原型态 / prototype) test_scheduler.py"]
        tests_zephyr_data_test_task_queue_py["(原型态 / prototype) test_task_queue.py"]
    end
    tests_zephyr_data_test_alerter_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_ch_writer_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_policy_registry_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_metrics_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_progress_store_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_providers_stage3_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_providers_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_task_queue_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    tests_zephyr_data_test_provider_base_py -.->|config_depends / config_depends| tests_zephyr_data_init_py
    D_SHARED["[生产态 / production] D_SHARED"]
    tests_trae_rules_test_g_trae_054_py -.->|测试依赖 / test_depends| D_SHARED
    D_GOV_ENFORCEMENT["[生产态 / production] D_GOV_ENFORCEMENT"]
    tests_trae_rules_test_g_trae_054_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_054_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_055_py -.->|测试依赖 / test_depends| D_SHARED
    tests_trae_rules_test_g_trae_055_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_trae_rules_test_g_trae_055_py -.->|测试依赖 / test_depends| D_GOV_ENFORCEMENT
    tests_utils_test_foundation_deprecation_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_foundation_env_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_foundation_errors_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_foundation_flags_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_foundation_flags_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_resilience_fallback_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_resilience_fallback_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_utils_migration_py -.->|测试依赖 / test_depends| D_SHARED
    tests_utils_test_resilience_retry_py -.->|测试依赖 / test_depends| D_SHARED
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class tests_trae_rules_test_g_trae_054_py,tests_trae_rules_test_g_trae_055_py,tests_utils_test_foundation_deprecation_py,tests_utils_test_foundation_env_py,tests_utils_test_foundation_errors_py,tests_utils_test_foundation_flags_py,tests_utils_test_resilience_fallback_py,tests_utils_test_resilience_retry_py,tests_utils_test_utils_context_py,tests_utils_test_utils_diff_utils_py,tests_utils_test_utils_migration_py,tests_utils_test_utils_pagination_py,tests_utils_test_utils_testing_py,tests_utils_test_utils_time_utils_py,tests_utils_test_version_py,tests_zephyr_data_init_py,tests_zephyr_data_test_alerter_py,tests_zephyr_data_test_ch_writer_py,tests_zephyr_data_test_cli_py,tests_zephyr_data_test_metrics_py,tests_zephyr_data_test_policy_registry_py,tests_zephyr_data_test_progress_store_py,tests_zephyr_data_test_provider_base_py,tests_zephyr_data_test_providers_py,tests_zephyr_data_test_providers_stage3_py,tests_zephyr_data_test_scheduler_py,tests_zephyr_data_test_task_queue_py design
    class D_SHARED,D_GOV_ENFORCEMENT external_prod
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_TRADING | 639 | 测试依赖 / test_depends |
| D_GOVERNANCE | 516 | 测试依赖 / test_depends |
| D_GOV_ENFORCEMENT | 221 | 测试依赖 / test_depends |
| D_SHARED | 170 | 测试依赖 / test_depends |
| D_SECURITY | 168 | 测试依赖 / test_depends |
| D_AUTONOMY_CORE | 127 | 测试依赖 / test_depends |
| D_INFRA_RUNTIME | 124 | 测试依赖 / test_depends |
| D_INTEGRATION | 63 | 测试依赖 / test_depends |
| D_INFRA_RECOVERY | 52 | 测试依赖 / test_depends |
| D_SECURITY_LLM | 40 | 测试依赖 / test_depends |
| D_INFRA_A2A | 35 | 测试依赖 / test_depends |
| D_INTELLIGENCE | 31 | 测试依赖 / test_depends |
| D_BACKTEST | 13 | 测试依赖 / test_depends |
| D_FRONTEND | 8 | 测试依赖 / test_depends |
| D_RISK | 6 | 测试依赖 / test_depends |
| D_OPS | 4 | 测试依赖 / test_depends |
| D_EX_CORE | 4 | 测试依赖 / test_depends |
| D_PF_CORE | 2 | 测试依赖 / test_depends |
| D_GOV_SCRIPTS | 2 | 测试依赖 / test_depends |
| D_POSITION | 2 | 测试依赖 / test_depends |
| D_FUNDAMENTAL_SIGNAL | 2 | 测试依赖 / test_depends |
| D_INTEGRATION_GATEWAY | 2 | 测试依赖 / test_depends |
| D_INFRA_TELEMETRY | 2 | 测试依赖 / test_depends |
| D_REPORTING | 1 | 测试依赖 / test_depends |
| D_SIMULATION | 1 | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

无跨域入边依赖 / No cross-domain incoming dependencies

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 审计测试套件（D_AUDITTEST）的模块分布。共 1677 个模块 / 1677 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│     L1 基础层 / Foundation Layer（共 1 个模块 / 1 modules）      │
├──────────────────────────────────────────────────────────────────┤
│    Test Suite — ARCH-052 聚合节点 production [生产态 / produ...  │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│    L2 领域层 / Domain Layer（共 1676 个模块 / 1676 modules）     │
├──────────────────────────────────────────────────────────────────┤
│   test_a2a_anomaly_detector.py [原型态 / prototype]              │
│   test_a2a_behavior_fingerprint.py [原型态 / prototype]          │
│   test_a2a_blame_attribution.py [原型态 / prototype]             │
│   test_a2a_carbon.py [原型态 / prototype]                        │
│   test_a2a_card_registry.py [原型态 / prototype]                 │
│   test_a2a_causal_trace.py [原型态 / prototype]                  │
│   test_a2a_check.py [原型态 / prototype]                         │
│   test_a2a_checkpoint.py [原型态 / prototype]                    │
│   test_a2a_collusion_detector.py [原型态 / prototype]            │
│   test_a2a_consent.py [原型态 / prototype]                       │
│   test_a2a_constitutional.py [原型态 / prototype]                │
│   test_a2a_context_rot.py [原型态 / prototype]                   │
│   test_a2a_cross_agent_semantic_flow.py [原型态 / prototype]     │
│   test_a2a_dashboard.py [原型态 / prototype]                     │
│   test_a2a_debate.py [原型态 / prototype]                        │
│   test_a2a_delegation_chain.py [原型态 / prototype]              │
│   test_a2a_economics.py [原型态 / prototype]                     │
│   test_a2a_failure.py [原型态 / prototype]                       │
│   ...还有 1658 个模块 / 1658 more modules                        │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 1677 个模块 / 1677 modules）。

### L1 基础层 / Foundation Layer (1 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 功能简介 / Description | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|---------|:---:|:---:|
| 1 | docs/01_policies_and_standards/_registry/catalogs/test_su... | 测试集 / Test Suite — ARCH-052 聚合... | [聚合节点 / Aggregated] 测试集 / Test Suite (1715 items) | production | stable |
| ↳1 |   ↳ tests/a2a/test_a2a_anomaly_detector.py |  |  | - | - |
| ↳2 |   ↳ tests/a2a/test_a2a_behavior_fingerprint.py |  |  | - | - |
| ↳3 |   ↳ tests/a2a/test_a2a_blame_attribution.py |  |  | - | - |
| ↳4 |   ↳ tests/a2a/test_a2a_carbon.py |  |  | - | - |
| ↳5 |   ↳ tests/a2a/test_a2a_card_registry.py |  |  | - | - |
| ↳6 |   ↳ tests/a2a/test_a2a_causal_trace.py |  |  | - | - |
| ↳7 |   ↳ tests/a2a/test_a2a_check.py |  |  | - | - |
| ↳8 |   ↳ tests/a2a/test_a2a_checkpoint.py |  |  | - | - |
| ↳9 |   ↳ tests/a2a/test_a2a_collusion_detector.py |  |  | - | - |
| ↳10 |   ↳ tests/a2a/test_a2a_consent.py |  |  | - | - |
| ↳11 |   ↳ tests/a2a/test_a2a_constitutional.py |  |  | - | - |
| ↳12 |   ↳ tests/a2a/test_a2a_context_rot.py |  |  | - | - |
| ↳13 |   ↳ tests/a2a/test_a2a_cross_agent_semantic_flow.py |  |  | - | - |
| ↳14 |   ↳ tests/a2a/test_a2a_dashboard.py |  |  | - | - |
| ↳15 |   ↳ tests/a2a/test_a2a_debate.py |  |  | - | - |
| ↳16 |   ↳ tests/a2a/test_a2a_delegation_chain.py |  |  | - | - |
| ↳17 |   ↳ tests/a2a/test_a2a_economics.py |  |  | - | - |
| ↳18 |   ↳ tests/a2a/test_a2a_failure.py |  |  | - | - |
| ↳19 |   ↳ tests/a2a/test_a2a_forgetting.py |  |  | - | - |
| ↳20 |   ↳ tests/a2a/test_a2a_formal_verification.py |  |  | - | - |
| ↳21 |   ↳ tests/a2a/test_a2a_frame_negotiation.py |  |  | - | - |
| ↳22 |   ↳ tests/a2a/test_a2a_governance.py |  |  | - | - |
| ↳23 |   ↳ tests/a2a/test_a2a_governance_adapter.py |  |  | - | - |
| ↳24 |   ↳ tests/a2a/test_a2a_hardware_router.py |  |  | - | - |
| ↳25 |   ↳ tests/a2a/test_a2a_hibernate.py |  |  | - | - |
| ↳26 |   ↳ tests/a2a/test_a2a_idempotency.py |  |  | - | - |
| ↳27 |   ↳ tests/a2a/test_a2a_idle_guard.py |  |  | - | - |
| ↳28 |   ↳ tests/a2a/test_a2a_immune.py |  |  | - | - |
| ↳29 |   ↳ tests/a2a/test_a2a_knowledge_distill.py |  |  | - | - |
| ↳30 |   ↳ tests/a2a/test_a2a_latent_comm.py |  |  | - | - |
| ↳31 |   ↳ tests/a2a/test_a2a_layer1_discovery.py |  |  | - | - |
| ↳32 |   ↳ tests/a2a/test_a2a_metrics.py |  |  | - | - |
| ↳33 |   ↳ tests/a2a/test_a2a_negotiation.py |  |  | - | - |
| ↳34 |   ↳ tests/a2a/test_a2a_protocol_gateway.py |  |  | - | - |
| ↳35 |   ↳ tests/a2a/test_a2a_protocol_security.py |  |  | - | - |
| ↳36 |   ↳ tests/a2a/test_a2a_red_team.py |  |  | - | - |
| ↳37 |   ↳ tests/a2a/test_a2a_saga.py |  |  | - | - |
| ↳38 |   ↳ tests/a2a/test_a2a_schemas.py |  |  | - | - |
| ↳39 |   ↳ tests/a2a/test_a2a_security.py |  |  | - | - |
| ↳40 |   ↳ tests/a2a/test_a2a_state.py |  |  | - | - |
| ↳41 |   ↳ tests/a2a/test_a2a_temporal_admission.py |  |  | - | - |
| ↳42 |   ↳ tests/a2a/test_a2a_tracing.py |  |  | - | - |
| ↳43 |   ↳ tests/a2a/test_a2a_vector_reputation.py |  |  | - | - |
| ↳44 |   ↳ tests/a2a/test_a2a_voting.py |  |  | - | - |
| ↳45 |   ↳ tests/a2a/test_a2a_work_steal.py |  |  | - | - |
| ↳46 |   ↳ tests/a2a/test_construction_verifier.py |  |  | - | - |
| ↳47 |   ↳ tests/a2a/test_mcp.py |  |  | - | - |
| ↳48 |   ↳ tests/a2a/test_spec_sync.py |  |  | - | - |
| ↳49 |   ↳ tests/action/test_action_composition_health_monitor.py |  |  | - | - |
| ↳50 |   ↳ tests/action/test_action_dispatcher.py |  |  | - | - |
| ↳51 |   ↳ tests/action/test_action_efficacy_decay_detector.py |  |  | - | - |
| ↳52 |   ↳ tests/action/test_action_explainability.py |  |  | - | - |
| ↳53 |   ↳ tests/action/test_action_history.py |  |  | - | - |
| ↳54 |   ↳ tests/action/test_action_interaction_detector.py |  |  | - | - |
| ↳55 |   ↳ tests/action/test_action_reversibility.py |  |  | - | - |
| ↳56 |   ↳ tests/action/test_action_selector.py |  |  | - | - |
| ↳57 |   ↳ tests/action/test_action_side_effect_cumulative_dete... |  |  | - | - |
| ↳58 |   ↳ tests/agent/test_agent_cooldown.py |  |  | - | - |
| ↳59 |   ↳ tests/agent/test_agent_creation_policy.py |  |  | - | - |
| ↳60 |   ↳ tests/agent/test_agent_health_monitor_root.py |  |  | - | - |
| ↳61 |   ↳ tests/agent/test_agent_lifecycle.py |  |  | - | - |
| ↳62 |   ↳ tests/agent/test_agent_observability.py |  |  | - | - |
| ↳63 |   ↳ tests/agent/test_agent_orchestrator_root.py |  |  | - | - |
| ↳64 |   ↳ tests/agent/test_agent_quality.py |  |  | - | - |
| ↳65 |   ↳ tests/agent/test_agent_signer.py |  |  | - | - |
| ↳66 |   ↳ tests/agent/test_agent_skill_guard.py |  |  | - | - |
| ↳67 |   ↳ tests/agent/test_agent_spec_main.py |  |  | - | - |
| ↳68 |   ↳ tests/agent/test_agent_spec_registry.py |  |  | - | - |
| ↳69 |   ↳ tests/agent/test_agent_trajectory_anomaly_detector.py |  |  | - | - |
| ↳70 |   ↳ tests/agent_rbac/conftest.py |  |  | - | - |
| ↳71 |   ↳ tests/agent_rbac/test_abac_guard_agent_rbac.py |  |  | - | - |
| ↳72 |   ↳ tests/agent_rbac/test_adversarial_agent_rbac.py |  |  | - | - |
| ↳73 |   ↳ tests/agent_rbac/test_adversarial_resilience.py |  |  | - | - |
| ↳74 |   ↳ tests/agent_rbac/test_cross_model_consistency.py |  |  | - | - |
| ↳75 |   ↳ tests/agent_rbac/test_crosscut_d.py |  |  | - | - |
| ↳76 |   ↳ tests/agent_rbac/test_cybersec_2026.py |  |  | - | - |
| ↳77 |   ↳ tests/agent_rbac/test_decision_explainer_agent_rbac.py |  |  | - | - |
| ↳78 |   ↳ tests/agent_rbac/test_decisions.py |  |  | - | - |
| ↳79 |   ↳ tests/agent_rbac/test_derive_rbac.py |  |  | - | - |
| ↳80 |   ↳ tests/agent_rbac/test_dry_run_agent_rbac.py |  |  | - | - |
| ↳81 |   ↳ tests/agent_rbac/test_engine_degradation_agent_rbac.py |  |  | - | - |
| ↳82 |   ↳ tests/agent_rbac/test_enhanced_security.py |  |  | - | - |
| ↳83 |   ↳ tests/agent_rbac/test_exceptions_agent_rbac.py |  |  | - | - |
| ↳84 |   ↳ tests/agent_rbac/test_forensic_a.py |  |  | - | - |
| ↳85 |   ↳ tests/agent_rbac/test_forensic_b.py |  |  | - | - |
| ↳86 |   ↳ tests/agent_rbac/test_forensic_c.py |  |  | - | - |
| ↳87 |   ↳ tests/agent_rbac/test_guard_layers_agent_rbac.py |  |  | - | - |
| ↳88 |   ↳ tests/agent_rbac/test_identity.py |  |  | - | - |
| ↳89 |   ↳ tests/agent_rbac/test_immutable_core_agent_rbac.py |  |  | - | - |
| ↳90 |   ↳ tests/agent_rbac/test_input_guard_agent_rbac.py |  |  | - | - |
| ↳91 |   ↳ tests/agent_rbac/test_integration_agent_rbac.py |  |  | - | - |
| ↳92 |   ↳ tests/agent_rbac/test_integration_root.py |  |  | - | - |
| ↳93 |   ↳ tests/agent_rbac/test_integrity_agent_rbac.py |  |  | - | - |
| ↳94 |   ↳ tests/agent_rbac/test_intent_binder_agent_rbac.py |  |  | - | - |
| ↳95 |   ↳ tests/agent_rbac/test_kill_switch_agent_rbac.py |  |  | - | - |
| ↳96 |   ↳ tests/agent_rbac/test_novel_attack.py |  |  | - | - |
| ↳97 |   ↳ tests/agent_rbac/test_observability_agent_rbac.py |  |  | - | - |
| ↳98 |   ↳ tests/agent_rbac/test_output_guard_agent_rbac.py |  |  | - | - |
| ↳99 |   ↳ tests/agent_rbac/test_permission_guard.py |  |  | - | - |
| ↳100 |   ↳ tests/agent_rbac/test_permissions.py |  |  | - | - |
| | | | > (仅显示前 100 个 items，共 1715 个) | | |

### L2 领域层 / Domain Layer (1676 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 功能简介 / Description | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|---------|:---:|:---:|
| 1 | tests/a2a/test_a2a_anomaly_detector.py | tests/a2a/test_a2a_anomaly_detector.py |  | prototype | generated |
| 2 | tests/a2a/test_a2a_behavior_fingerprint.py | tests/a2a/test_a2a_behavior_fingerpri... |  | prototype | generated |
| 3 | tests/a2a/test_a2a_blame_attribution.py | tests/a2a/test_a2a_blame_attribution.py |  | prototype | generated |
| 4 | tests/a2a/test_a2a_carbon.py | tests/a2a/test_a2a_carbon.py |  | prototype | generated |
| 5 | tests/a2a/test_a2a_card_registry.py | tests/a2a/test_a2a_card_registry.py |  | prototype | generated |
| 6 | tests/a2a/test_a2a_causal_trace.py | tests/a2a/test_a2a_causal_trace.py |  | prototype | generated |
| 7 | tests/a2a/test_a2a_check.py | tests/a2a/test_a2a_check.py |  | prototype | generated |
| 8 | tests/a2a/test_a2a_checkpoint.py | tests/a2a/test_a2a_checkpoint.py |  | prototype | generated |
| 9 | tests/a2a/test_a2a_collusion_detector.py | tests/a2a/test_a2a_collusion_detector.py |  | prototype | generated |
| 10 | tests/a2a/test_a2a_consent.py | tests/a2a/test_a2a_consent.py |  | prototype | generated |
| 11 | tests/a2a/test_a2a_constitutional.py | tests/a2a/test_a2a_constitutional.py |  | prototype | generated |
| 12 | tests/a2a/test_a2a_context_rot.py | tests/a2a/test_a2a_context_rot.py |  | prototype | generated |
| 13 | tests/a2a/test_a2a_cross_agent_semantic_flow.py | tests/a2a/test_a2a_cross_agent_semant... |  | prototype | generated |
| 14 | tests/a2a/test_a2a_dashboard.py | tests/a2a/test_a2a_dashboard.py |  | prototype | generated |
| 15 | tests/a2a/test_a2a_debate.py | tests/a2a/test_a2a_debate.py |  | prototype | generated |
| 16 | tests/a2a/test_a2a_delegation_chain.py | tests/a2a/test_a2a_delegation_chain.py |  | prototype | generated |
| 17 | tests/a2a/test_a2a_economics.py | tests/a2a/test_a2a_economics.py |  | prototype | generated |
| 18 | tests/a2a/test_a2a_failure.py | tests/a2a/test_a2a_failure.py |  | prototype | generated |
| 19 | tests/a2a/test_a2a_forgetting.py | tests/a2a/test_a2a_forgetting.py |  | prototype | generated |
| 20 | tests/a2a/test_a2a_formal_verification.py | tests/a2a/test_a2a_formal_verificatio... |  | prototype | generated |
| 21 | tests/a2a/test_a2a_frame_negotiation.py | tests/a2a/test_a2a_frame_negotiation.py |  | prototype | generated |
| 22 | tests/a2a/test_a2a_governance.py | tests/a2a/test_a2a_governance.py |  | prototype | generated |
| 23 | tests/a2a/test_a2a_governance_adapter.py | tests/a2a/test_a2a_governance_adapter.py |  | prototype | generated |
| 24 | tests/a2a/test_a2a_hardware_router.py | tests/a2a/test_a2a_hardware_router.py |  | prototype | generated |
| 25 | tests/a2a/test_a2a_hibernate.py | tests/a2a/test_a2a_hibernate.py |  | prototype | generated |
| 26 | tests/a2a/test_a2a_idempotency.py | tests/a2a/test_a2a_idempotency.py |  | prototype | generated |
| 27 | tests/a2a/test_a2a_idle_guard.py | tests/a2a/test_a2a_idle_guard.py |  | prototype | generated |
| 28 | tests/a2a/test_a2a_immune.py | tests/a2a/test_a2a_immune.py |  | prototype | generated |
| 29 | tests/a2a/test_a2a_knowledge_distill.py | tests/a2a/test_a2a_knowledge_distill.py |  | prototype | generated |
| 30 | tests/a2a/test_a2a_latent_comm.py | tests/a2a/test_a2a_latent_comm.py |  | prototype | generated |
| 31 | tests/a2a/test_a2a_layer1_discovery.py | tests/a2a/test_a2a_layer1_discovery.py |  | prototype | generated |
| 32 | tests/a2a/test_a2a_metrics.py | tests/a2a/test_a2a_metrics.py |  | prototype | generated |
| 33 | tests/a2a/test_a2a_negotiation.py | tests/a2a/test_a2a_negotiation.py |  | prototype | generated |
| 34 | tests/a2a/test_a2a_protocol_gateway.py | tests/a2a/test_a2a_protocol_gateway.py |  | prototype | generated |
| 35 | tests/a2a/test_a2a_protocol_security.py | tests/a2a/test_a2a_protocol_security.py |  | prototype | generated |
| 36 | tests/a2a/test_a2a_red_team.py | tests/a2a/test_a2a_red_team.py |  | prototype | generated |
| 37 | tests/a2a/test_a2a_saga.py | tests/a2a/test_a2a_saga.py |  | prototype | generated |
| 38 | tests/a2a/test_a2a_schemas.py | tests/a2a/test_a2a_schemas.py |  | prototype | generated |
| 39 | tests/a2a/test_a2a_security.py | tests/a2a/test_a2a_security.py |  | prototype | generated |
| 40 | tests/a2a/test_a2a_state.py | tests/a2a/test_a2a_state.py |  | prototype | generated |
| 41 | tests/a2a/test_a2a_temporal_admission.py | tests/a2a/test_a2a_temporal_admission.py |  | prototype | generated |
| 42 | tests/a2a/test_a2a_tracing.py | tests/a2a/test_a2a_tracing.py |  | prototype | generated |
| 43 | tests/a2a/test_a2a_vector_reputation.py | tests/a2a/test_a2a_vector_reputation.py |  | prototype | generated |
| 44 | tests/a2a/test_a2a_voting.py | tests/a2a/test_a2a_voting.py |  | prototype | generated |
| 45 | tests/a2a/test_a2a_work_steal.py | tests/a2a/test_a2a_work_steal.py |  | prototype | generated |
| 46 | tests/a2a/test_construction_verifier.py | tests/a2a/test_construction_verifier.py |  | prototype | generated |
| 47 | tests/a2a/test_mcp.py | tests/a2a/test_mcp.py |  | prototype | generated |
| 48 | tests/a2a/test_spec_sync.py | tests/a2a/test_spec_sync.py |  | prototype | generated |
| 49 | tests/action/test_action_composition_health_monitor.py | tests/action/test_action_composition_... |  | prototype | generated |
| 50 | tests/action/test_action_dispatcher.py | tests/action/test_action_dispatcher.py |  | prototype | generated |
| 51 | tests/action/test_action_efficacy_decay_detector.py | tests/action/test_action_efficacy_dec... |  | prototype | generated |
| 52 | tests/action/test_action_explainability.py | tests/action/test_action_explainabili... |  | prototype | generated |
| 53 | tests/action/test_action_history.py | tests/action/test_action_history.py |  | prototype | generated |
| 54 | tests/action/test_action_interaction_detector.py | tests/action/test_action_interaction_... |  | prototype | generated |
| 55 | tests/action/test_action_reversibility.py | tests/action/test_action_reversibilit... |  | prototype | generated |
| 56 | tests/action/test_action_selector.py | tests/action/test_action_selector.py |  | prototype | generated |
| 57 | tests/action/test_action_side_effect_cumulative_detector.py | tests/action/test_action_side_effect_... |  | prototype | generated |
| 58 | tests/agent/test_agent_cooldown.py | tests/agent/test_agent_cooldown.py |  | prototype | generated |
| 59 | tests/agent/test_agent_creation_policy.py | tests/agent/test_agent_creation_polic... |  | prototype | generated |
| 60 | tests/agent/test_agent_health_monitor_root.py | tests/agent/test_agent_health_monitor... |  | prototype | generated |
| 61 | tests/agent/test_agent_lifecycle.py | tests/agent/test_agent_lifecycle.py |  | prototype | generated |
| 62 | tests/agent/test_agent_observability.py | tests/agent/test_agent_observability.py |  | prototype | generated |
| 63 | tests/agent/test_agent_orchestrator_root.py | tests/agent/test_agent_orchestrator_r... |  | prototype | generated |
| 64 | tests/agent/test_agent_quality.py | tests/agent/test_agent_quality.py |  | prototype | generated |
| 65 | tests/agent/test_agent_signer.py | tests/agent/test_agent_signer.py |  | prototype | generated |
| 66 | tests/agent/test_agent_skill_guard.py | tests/agent/test_agent_skill_guard.py |  | prototype | generated |
| 67 | tests/agent/test_agent_spec_main.py | tests/agent/test_agent_spec_main.py |  | prototype | generated |
| 68 | tests/agent/test_agent_spec_registry.py | tests/agent/test_agent_spec_registry.py |  | prototype | generated |
| 69 | tests/agent/test_agent_trajectory_anomaly_detector.py | tests/agent/test_agent_trajectory_ano... |  | prototype | generated |
| 70 | tests/agent_rbac/conftest.py | tests/agent_rbac/conftest.py | pytest fixtures for agent-rbac tests. | prototype | generated |
| 71 | tests/agent_rbac/test_abac_guard_agent_rbac.py | tests/agent_rbac/test_abac_guard_agen... | 测试 L2 ABACGuard — 五维属性权限判定 | prototype | generated |
| 72 | tests/agent_rbac/test_adversarial_agent_rbac.py | tests/agent_rbac/test_adversarial_age... | MOD-INF-018 test_adversarial.py — 对抗性测试: 权限绕过/伪造/重放. | prototype | generated |
| 73 | tests/agent_rbac/test_adversarial_resilience.py | tests/agent_rbac/test_adversarial_res... |  | prototype | generated |
| 74 | tests/agent_rbac/test_cross_model_consistency.py | tests/agent_rbac/test_cross_model_con... | MOD-INF-018 跨模型一致性测试 — DeepSeek/GLM/Claude 对同权限规则判定一致性 | prototype | generated |
| 75 | tests/agent_rbac/test_crosscut_d.py | tests/agent_rbac/test_crosscut_d.py | 跨切面 D 异常检测 + 蓝图保真 + 原生API守卫 + 内存守卫 测试. | prototype | generated |
| 76 | tests/agent_rbac/test_cybersec_2026.py | tests/agent_rbac/test_cybersec_2026.py | cybersec 2026 独立测试. | prototype | generated |
| 77 | tests/agent_rbac/test_decision_explainer_agent_rbac.py | tests/agent_rbac/test_decision_explai... | 测试 DecisionExplainer — 结构化拒绝原因 | prototype | generated |
| 78 | tests/agent_rbac/test_decisions.py | tests/agent_rbac/test_decisions.py | 决策注册表测试. | prototype | generated |
| 79 | tests/agent_rbac/test_derive_rbac.py | tests/agent_rbac/test_derive_rbac.py | MOD-INF-018 test_derive_rbac.py — RBAC 自动派生测试. | prototype | generated |
| 80 | tests/agent_rbac/test_dry_run_agent_rbac.py | tests/agent_rbac/test_dry_run_agent_r... | 测试 L7 DryRun — 权限模拟与影响分析 | prototype | generated |
| 81 | tests/agent_rbac/test_engine_degradation_agent_rbac.py | tests/agent_rbac/test_engine_degradat... | 测试 L0 EngineDegradation — 权限引擎降级策略 | prototype | generated |
| 82 | tests/agent_rbac/test_enhanced_security.py | tests/agent_rbac/test_enhanced_securi... | 七项增强安全机制整合测试. | prototype | generated |
| 83 | tests/agent_rbac/test_exceptions_agent_rbac.py | tests/agent_rbac/test_exceptions_agen... | 测试 AgentRbac 异常类型 | prototype | generated |
| 84 | tests/agent_rbac/test_forensic_a.py | tests/agent_rbac/test_forensic_a.py | 跨切面 B 取证审计 A 层——genesis/asymmetric/non-repudiation 测试. | prototype | generated |
| 85 | tests/agent_rbac/test_forensic_b.py | tests/agent_rbac/test_forensic_b.py | 跨切面 B 取证审计 B 层——path/shell/rule_injection 守卫测试. | prototype | generated |
| 86 | tests/agent_rbac/test_forensic_c.py | tests/agent_rbac/test_forensic_c.py | 跨切面 B 取证审计 C 层——audit_log/replay/legal_chain/rollback_sandbox/monot... | prototype | generated |
| 87 | tests/agent_rbac/test_guard_layers_agent_rbac.py | tests/agent_rbac/test_guard_layers_ag... | 测试防护层模块 — ColdStartLock, AutoGuard, EscalationHandler | prototype | generated |
| 88 | tests/agent_rbac/test_identity.py | tests/agent_rbac/test_identity.py | 测试 AgentIdentity — 身份模型 | prototype | generated |
| 89 | tests/agent_rbac/test_immutable_core_agent_rbac.py | tests/agent_rbac/test_immutable_core_... | 测试 L0 ImmutableCore — 硬编码不可变保护区 | prototype | generated |
| 90 | tests/agent_rbac/test_input_guard_agent_rbac.py | tests/agent_rbac/test_input_guard_age... | 测试 L3 InputGuard — 参数级护栏 | prototype | generated |
| 91 | tests/agent_rbac/test_integration_agent_rbac.py | tests/agent_rbac/test_integration_age... | 集成 + 契约验证测试. | prototype | generated |
| 92 | tests/agent_rbac/test_integration_root.py | tests/agent_rbac/test_integration_roo... |  | prototype | generated |
| 93 | tests/agent_rbac/test_integrity_agent_rbac.py | tests/agent_rbac/test_integrity_agent... | 完整性自检测试. | prototype | generated |
| 94 | tests/agent_rbac/test_intent_binder_agent_rbac.py | tests/agent_rbac/test_intent_binder_a... | 测试 IntentBinder — 意图绑定与连续验证 | prototype | generated |
| 95 | tests/agent_rbac/test_kill_switch_agent_rbac.py | tests/agent_rbac/test_kill_switch_age... | 测试 L0 KillSwitch — 全局熔断机制 | prototype | generated |
| 96 | tests/agent_rbac/test_novel_attack.py | tests/agent_rbac/test_novel_attack.py | 新攻击 / cybersec 2026 专项测试. | prototype | generated |
| 97 | tests/agent_rbac/test_observability_agent_rbac.py | tests/agent_rbac/test_observability_a... | 测试 L6 Observability — 指标上报与异常检测 | prototype | generated |
| 98 | tests/agent_rbac/test_output_guard_agent_rbac.py | tests/agent_rbac/test_output_guard_ag... | 测试 L5 OutputGuard — 输出护栏 | prototype | generated |
| 99 | tests/agent_rbac/test_permission_guard.py | tests/agent_rbac/test_permission_guar... | 测试 PermissionGuard — 七层统一编排 | prototype | generated |
| 100 | tests/agent_rbac/test_permissions.py | tests/agent_rbac/test_permissions.py | 权限自动化测试——120+攻击向量/跨模型一致性/对抗性测试/边缘用例. | prototype | generated |
| 101 | tests/agent_rbac/test_post_action.py | tests/agent_rbac/test_post_action.py | MOD-INF-018 test_post_action.py — L5 Post-Action Hook 测试. | prototype | generated |
| 102 | tests/agent_rbac/test_rbac_auto_lifecycle.py | tests/agent_rbac/test_rbac_auto_lifec... | RBAC 自动启动/关闭生命周期集成测试. | prototype | generated |
| 103 | tests/agent_rbac/test_rbac_guard_agent_rbac.py | tests/agent_rbac/test_rbac_guard_agen... | 测试 L1 RBACGuard — 三层权限模型 | prototype | generated |
| 104 | tests/agent_rbac/test_redteam_adversarial.py | tests/agent_rbac/test_redteam_adversa... | MOD-INF-018 对抗性红队测试 — 专用 Agent 尝试绕过七层+六横切面 | prototype | generated |
| 105 | tests/agent_rbac/test_risk_mitigation_agent_rbac.py | tests/agent_rbac/test_risk_mitigation... | 风险缓解测试. | prototype | generated |
| 106 | tests/agent_rbac/test_sequence_guard_agent_rbac.py | tests/agent_rbac/test_sequence_guard_... | 测试 L4 SequenceGuard — 操作序列追踪与危险序列阻断 | prototype | generated |
| 107 | tests/agent_rbac/test_session_aware_stash_red_blue.py | tests/agent_rbac/test_session_aware_s... | session 隔离 stash 红蓝对抗极限测试。 | prototype | generated |
| 108 | tests/agent_rbac/test_toctou_guard_agent_rbac.py | tests/agent_rbac/test_toctou_guard_ag... | 测试 TOCTOU Guard — 竞态防护 | prototype | generated |
| 109 | tests/agent_rbac/test_vibe_coding.py | tests/agent_rbac/test_vibe_coding.py | Vibe Coding / Novel Attack / Cybersec 2026 攻击面扩展测试. | prototype | generated |
| 110 | tests/ai/test_ai_audit_logger.py | tests/ai/test_ai_audit_logger.py |  | prototype | generated |
| 111 | tests/ai/test_ai_capability_guard.py | tests/ai/test_ai_capability_guard.py |  | prototype | generated |
| 112 | tests/ai/test_ai_comment_veracity.py | tests/ai/test_ai_comment_veracity.py |  | prototype | generated |
| 113 | tests/ai/test_ai_construction_detectors.py | tests/ai/test_ai_construction_detecto... |  | prototype | generated |
| 114 | tests/ai/test_ai_context_injector.py | tests/ai/test_ai_context_injector.py |  | prototype | generated |
| 115 | tests/asset_inventory/test_asset_inventory.py | tests/asset_inventory/test_asset_inve... |  | prototype | generated |
| 116 | tests/audit/test_ab_test.py | tests/audit/test_ab_test.py |  | prototype | generated |
| 117 | tests/audit/test_absence_manager.py | tests/audit/test_absence_manager.py |  | prototype | generated |
| 118 | tests/audit/test_amplification_guard.py | tests/audit/test_amplification_guard.py |  | prototype | generated |
| 119 | tests/audit/test_api_dependency_metrics.py | tests/audit/test_api_dependency_metri... |  | prototype | generated |
| 120 | tests/audit/test_architecture_contracts.py | tests/audit/test_architecture_contrac... |  | prototype | generated |
| 121 | tests/audit/test_architecture_principles.py | tests/audit/test_architecture_princip... |  | prototype | generated |
| 122 | tests/audit/test_audit_anomaly.py | tests/audit/test_audit_anomaly.py |  | prototype | generated |
| 123 | tests/audit/test_audit_api_lifecycle.py | tests/audit/test_audit_api_lifecycle.py |  | prototype | generated |
| 124 | tests/audit/test_audit_bridge.py | tests/audit/test_audit_bridge.py |  | prototype | generated |
| 125 | tests/audit/test_audit_chain_verifier.py | tests/audit/test_audit_chain_verifier.py |  | prototype | generated |
| 126 | tests/audit/test_audit_cli.py | tests/audit/test_audit_cli.py |  | prototype | generated |
| 127 | tests/audit/test_audit_contracts.py | tests/audit/test_audit_contracts.py |  | prototype | generated |
| 128 | tests/audit/test_audit_dim_d1_d4_e2e.py | tests/audit/test_audit_dim_d1_d4_e2e.py |  | prototype | generated |
| 129 | tests/audit/test_audit_dim_d5_d8_e2e.py | tests/audit/test_audit_dim_d5_d8_e2e.py |  | prototype | generated |
| 130 | tests/audit/test_audit_dim_d9_d12_e2e.py | tests/audit/test_audit_dim_d9_d12_e2e.py |  | prototype | generated |
| 131 | tests/audit/test_audit_financial_compliance.py | tests/audit/test_audit_financial_comp... |  | prototype | generated |
| 132 | tests/audit/test_audit_full_closure_e2e.py | tests/audit/test_audit_full_closure_e... |  | prototype | generated |
| 133 | tests/audit/test_audit_full_pipeline_e2e.py | tests/audit/test_audit_full_pipeline_... |  | prototype | generated |
| 134 | tests/audit/test_audit_incremental_review.py | tests/audit/test_audit_incremental_re... |  | prototype | generated |
| 135 | tests/audit/test_audit_indexer.py | tests/audit/test_audit_indexer.py |  | prototype | generated |
| 136 | tests/audit/test_audit_integrity.py | tests/audit/test_audit_integrity.py |  | prototype | generated |
| 137 | tests/audit/test_audit_log_guard.py | tests/audit/test_audit_log_guard.py |  | prototype | generated |
| 138 | tests/audit/test_audit_models.py | tests/audit/test_audit_models.py |  | prototype | generated |
| 139 | tests/audit/test_audit_observability_dashboard.py | tests/audit/test_audit_observability_... |  | prototype | generated |
| 140 | tests/audit/test_audit_orchestrator_e2e.py | tests/audit/test_audit_orchestrator_e... |  | prototype | generated |
| 141 | tests/audit/test_audit_orphan_judge_e2e.py | tests/audit/test_audit_orphan_judge_e... | [INVARIANTS] E2E tests cover DecisionTable 12-row routing; SafetyFence blocks... | prototype | generated |
| 142 | tests/audit/test_audit_provenance_tracker.py | tests/audit/test_audit_provenance_tra... |  | prototype | generated |
| 143 | tests/audit/test_audit_red_blue_e2e.py | tests/audit/test_audit_red_blue_e2e.py |  | prototype | generated |
| 144 | tests/audit/test_audit_registry_gate_e2e.py | tests/audit/test_audit_registry_gate_... |  | prototype | generated |
| 145 | tests/audit/test_audit_self_healer_e2e.py | tests/audit/test_audit_self_healer_e2... |  | prototype | generated |
| 146 | tests/audit/test_audit_spec_auditor.py | tests/audit/test_audit_spec_auditor.py |  | prototype | generated |
| 147 | tests/audit/test_audit_supply_chain_security.py | tests/audit/test_audit_supply_chain_s... |  | prototype | generated |
| 148 | tests/audit/test_audit_write_failure_protector.py | tests/audit/test_audit_write_failure_... |  | prototype | generated |
| 149 | tests/audit/test_backcompat_checker.py | tests/audit/test_backcompat_checker.py |  | prototype | generated |
| 150 | tests/audit/test_baseline_manager.py | tests/audit/test_baseline_manager.py |  | prototype | generated |
| 151 | tests/audit/test_baseline_poisoning_guard.py | tests/audit/test_baseline_poisoning_g... |  | prototype | generated |
| 152 | tests/audit/test_benchmark_integrity.py | tests/audit/test_benchmark_integrity.py |  | prototype | generated |
| 153 | tests/audit/test_brain_integration_root.py | tests/audit/test_brain_integration_ro... |  | prototype | generated |
| 154 | tests/audit/test_build_reproducibility_verifier.py | tests/audit/test_build_reproducibilit... |  | prototype | generated |
| 155 | tests/audit/test_build_reproducibility_verifier_v2.py | tests/audit/test_build_reproducibilit... |  | prototype | generated |
| 156 | tests/audit/test_burn_rate_alerter.py | tests/audit/test_burn_rate_alerter.py |  | prototype | generated |
| 157 | tests/audit/test_burnout_alarm.py | tests/audit/test_burnout_alarm.py |  | prototype | generated |
| 158 | tests/audit/test_cascade_detector.py | tests/audit/test_cascade_detector.py |  | prototype | generated |
| 159 | tests/audit/test_causal_inference_engine.py | tests/audit/test_causal_inference_eng... |  | prototype | generated |
| 160 | tests/audit/test_code_review_ai.py | tests/audit/test_code_review_ai.py |  | prototype | generated |
| 161 | tests/audit/test_cognitive_load_budget.py | tests/audit/test_cognitive_load_budge... |  | prototype | generated |
| 162 | tests/audit/test_correlation_engine.py | tests/audit/test_correlation_engine.py |  | prototype | generated |
| 163 | tests/audit/test_credibility_engine.py | tests/audit/test_credibility_engine.py |  | prototype | generated |
| 164 | tests/audit/test_crypto_bootstrap.py | tests/audit/test_crypto_bootstrap.py |  | prototype | generated |
| 165 | tests/audit/test_detector_dispatcher.py | tests/audit/test_detector_dispatcher.py |  | prototype | generated |
| 166 | tests/audit/test_deterministic_replay.py | tests/audit/test_deterministic_replay.py |  | prototype | generated |
| 167 | tests/audit/test_diagnosis_kpi.py | tests/audit/test_diagnosis_kpi.py |  | prototype | generated |
| 168 | tests/audit/test_emergent_behavior_detector.py | tests/audit/test_emergent_behavior_de... |  | prototype | generated |
| 169 | tests/audit/test_events_ba.py | tests/audit/test_events_ba.py |  | prototype | generated |
| 170 | tests/audit/test_forensics_engine.py | tests/audit/test_forensics_engine.py |  | prototype | generated |
| 171 | tests/audit/test_gitignore_auditor.py | tests/audit/test_gitignore_auditor.py |  | prototype | generated |
| 172 | tests/audit/test_global_health_map.py | tests/audit/test_global_health_map.py |  | prototype | generated |
| 173 | tests/audit/test_handoff_manager.py | tests/audit/test_handoff_manager.py |  | prototype | generated |
| 174 | tests/audit/test_headless_scanner.py | tests/audit/test_headless_scanner.py |  | prototype | generated |
| 175 | tests/audit/test_human_anomaly_flood_detector.py | tests/audit/test_human_anomaly_flood_... |  | prototype | generated |
| 176 | tests/audit/test_incremental_scanner.py | tests/audit/test_incremental_scanner.py |  | prototype | generated |
| 177 | tests/audit/test_interactive_diagnosis.py | tests/audit/test_interactive_diagnosi... |  | prototype | generated |
| 178 | tests/audit/test_intermittent_failure_pattern.py | tests/audit/test_intermittent_failure... |  | prototype | generated |
| 179 | tests/audit/test_latency_slo.py | tests/audit/test_latency_slo.py |  | prototype | generated |
| 180 | tests/audit/test_ml_engineering.py | tests/audit/test_ml_engineering.py |  | prototype | generated |
| 181 | tests/audit/test_mtti_tracker.py | tests/audit/test_mtti_tracker.py |  | prototype | generated |
| 182 | tests/audit/test_naming_magic_checker.py | tests/audit/test_naming_magic_checker.py |  | prototype | generated |
| 183 | tests/audit/test_orphan_scanner.py | tests/audit/test_orphan_scanner.py |  | prototype | generated |
| 184 | tests/audit/test_performance_baseline.py | tests/audit/test_performance_baseline.py |  | prototype | generated |
| 185 | tests/audit/test_point_in_time_reconstructor.py | tests/audit/test_point_in_time_recons... |  | prototype | generated |
| 186 | tests/audit/test_pre_flight_simulator.py | tests/audit/test_pre_flight_simulator.py |  | prototype | generated |
| 187 | tests/audit/test_preventive_repair.py | tests/audit/test_preventive_repair.py |  | prototype | generated |
| 188 | tests/audit/test_python_compat.py | tests/audit/test_python_compat.py |  | prototype | generated |
| 189 | tests/audit/test_regime_detector.py | tests/audit/test_regime_detector.py |  | prototype | generated |
| 190 | tests/audit/test_regime_gain_scheduling.py | tests/audit/test_regime_gain_scheduli... |  | prototype | generated |
| 191 | tests/audit/test_roi_engine.py | tests/audit/test_roi_engine.py |  | prototype | generated |
| 192 | tests/audit/test_scan_mutex.py | tests/audit/test_scan_mutex.py |  | prototype | generated |
| 193 | tests/audit/test_serialization_format_tracker.py | tests/audit/test_serialization_format... |  | prototype | generated |
| 194 | tests/audit/test_sim2real_calibration.py | tests/audit/test_sim2real_calibration.py |  | prototype | generated |
| 195 | tests/audit/test_socratic_questions.py | tests/audit/test_socratic_questions.py |  | prototype | generated |
| 196 | tests/audit/test_state_machine.py | tests/audit/test_state_machine.py |  | prototype | generated |
| 197 | tests/audit/test_statistical_hygiene_auditor.py | tests/audit/test_statistical_hygiene_... |  | prototype | generated |
| 198 | tests/audit/test_sub_agent_collusion.py | tests/audit/test_sub_agent_collusion.py |  | prototype | generated |
| 199 | tests/audit/test_suppression_learner.py | tests/audit/test_suppression_learner.py |  | prototype | generated |
| 200 | tests/audit/test_symlink_checker.py | tests/audit/test_symlink_checker.py |  | prototype | generated |

> (仅显示前 200 个模块，共 1676 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 10 条 / 10 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 10 条 / 10 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 1                               │
│   [config_depends]: 10 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│        [config_depends / config_depends]（10 条 / edges）        │
├──────────────────────────────────────────────────────────────────┤
│   test_semantic_diff.py → __init__.py                            │
│   test_alerter.py → __init__.py                                  │
│   test_ch_writer.py → __init__.py                                │
│   test_policy_registry.py → __init__.py                          │
│   test_metrics.py → __init__.py                                  │
│   test_progress_store.py → __init__.py                           │
│   test_providers_stage3.py → __init__.py                         │
│   test_providers.py → __init__.py                                │
│   test_task_queue.py → __init__.py                               │
│   test_provider_base.py → __init__.py                            │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[生产态 / production]`=已上线 / `[设计态 / design]`=设计中 / `[原型态 / prototype]`=原型 / `[未知 / unknown]`=未知
