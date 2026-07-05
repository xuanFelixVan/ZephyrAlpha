---
doc_type: architecture_view
title: D_SECURITY_LLM llm_defense架构文档
version: "1.0"
status: active
date: 2026-07-06
owner: auto-generator
ttl: permanent
---

# 18_d_security_llm / llm_defense

> **文档作用 / Purpose**: 展示 llm_defense（D_SECURITY_LLM）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-06 05:46:45
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 18 | Number | 18 |
| 域ID | D_SECURITY_LLM | Domain ID | D_SECURITY_LLM |
| 域名称 | llm_defense | Domain Name | llm_defense |
| 层级 | L1_foundation | Layer | L1_foundation |
| 模块数 | 44 | Module Count | 44 |
| 域内依赖 | 47 | Internal Dependencies | 47 |
| 跨域入边 | 53 | Cross-domain Incoming | 53 |
| 跨域出边 | 19 | Cross-domain Outgoing | 19 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 11 | Prototype Modules | 11 |
| 生产态模块 | 33 | Production Modules | 33 |
| 容量 | 33/150 (正常) | Capacity | 33/150 (正常) |
| 描述 | L0供应链安全(模型验证/依赖扫描) | Description | L0供应链安全(模型验证/依赖扫描) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，还在设计中）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）

### 第 1 页 / 共 2 页 / Page 1 of 2

```mermaid
graph TD
    subgraph D_SECURITY_LLM["D_SECURITY_LLM llm_defense"]
        src_zephyr_security_llm_defense_init_py["src/zephyr/security/llm_defense/__init__.py prototype"]
        src_zephyr_security_llm_defense_llm_security_init_py["src/zephyr/security/llm_defense/llm_security/__... prototype"]
        src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py["src/zephyr/security/llm_defense/llm_security/ad... production"]
        src_zephyr_security_llm_defense_llm_security_alignment_scorer_py["src/zephyr/security/llm_defense/llm_security/al... production"]
        src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py["src/zephyr/security/llm_defense/llm_security/be... production"]
        src_zephyr_security_llm_defense_llm_security_dashboard_init_py["src/zephyr/security/llm_defense/llm_security/da... prototype"]
        src_zephyr_security_llm_defense_llm_security_dashboard_app_py["src/zephyr/security/llm_defense/llm_security/da... prototype"]
        src_zephyr_security_llm_defense_llm_security_gateway_py["src/zephyr/security/llm_defense/llm_security/ga... production"]
        src_zephyr_security_llm_defense_llm_security_input_sanitizer_py["src/zephyr/security/llm_defense/llm_security/in... production"]
        src_zephyr_security_llm_defense_llm_security_layers_init_py["src/zephyr/security/llm_defense/llm_security/la... prototype"]
        src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l1_input_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l3_output_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py["src/zephyr/security/llm_defense/llm_security/la... prototype"]
        src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py["src/zephyr/security/llm_defense/llm_security/la... prototype"]
        src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py["src/zephyr/security/llm_defense/llm_security/la... production"]
        src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py["src/zephyr/security/llm_defense/llm_security/ls... production"]
        src_zephyr_security_llm_defense_llm_security_patterns_init_py["src/zephyr/security/llm_defense/llm_security/pa... prototype"]
        src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py["src/zephyr/security/llm_defense/llm_security/pa... production"]
        src_zephyr_security_llm_defense_llm_security_patterns_secrets_py["src/zephyr/security/llm_defense/llm_security/pa... production"]
        src_zephyr_security_llm_defense_llm_security_payloads_init_py["src/zephyr/security/llm_defense/llm_security/pa... prototype"]
        src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml["src/zephyr/security/llm_defense/llm_security/pa... production"]
        src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml["src/zephyr/security/llm_defense/llm_security/pa... production"]
        src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml["src/zephyr/security/llm_defense/llm_security/pa... production"]
        src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml["src/zephyr/security/llm_defense/llm_security/pa... production"]
    end
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_patterns_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_init_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_init_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_init_py -.->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_dashboard_init_py -.->|config_depends| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py -.->|config_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py -.->|config_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml -.->|config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml -.->|config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml -.->|config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml -.->|config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    D_SHARED["D_SHARED production"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|import_depends| D_SHARED
    D_GOVERNANCE["D_GOVERNANCE production"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|import_depends| D_GOVERNANCE
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py -->|import_depends| D_SHARED
    D_AUTONOMY_CORE["D_AUTONOMY_CORE production"]
    D_AUTONOMY_CORE -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_GOVERNANCE -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION["D_INTEGRATION production"]
    D_INTEGRATION -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION_GATEWAY["D_INTEGRATION_GATEWAY prototype"]
    D_INTEGRATION_GATEWAY -.->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING["D_TRADING production"]
    D_TRADING -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING -->|import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_TRADING -->|import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING -.->|import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_GOVERNANCE -.->|import_depends| src_zephyr_security_llm_defense_llm_security_init_py
    D_AUDITTEST["D_AUDITTEST prototype"]
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_alignment_scorer_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py,src_zephyr_security_llm_defense_llm_security_alignment_scorer_py,src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py,src_zephyr_security_llm_defense_llm_security_gateway_py,src_zephyr_security_llm_defense_llm_security_input_sanitizer_py,src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py,src_zephyr_security_llm_defense_llm_security_layers_l1_input_py,src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_layers_l3_output_py,src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py,src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py,src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py,src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py,src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py,src_zephyr_security_llm_defense_llm_security_patterns_secrets_py,src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml,src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml,src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml,src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml production
    class src_zephyr_security_llm_defense_init_py,src_zephyr_security_llm_defense_llm_security_init_py,src_zephyr_security_llm_defense_llm_security_dashboard_init_py,src_zephyr_security_llm_defense_llm_security_dashboard_app_py,src_zephyr_security_llm_defense_llm_security_layers_init_py,src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py,src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py,src_zephyr_security_llm_defense_llm_security_patterns_init_py,src_zephyr_security_llm_defense_llm_security_payloads_init_py design
    class D_SHARED,D_GOVERNANCE,D_AUTONOMY_CORE,D_INTEGRATION,D_TRADING external_prod
    class D_INTEGRATION_GATEWAY,D_AUDITTEST external_design
```

### 第 2 页 / 共 2 页 / Page 2 of 2

```mermaid
graph TD
    subgraph D_SECURITY_LLM["D_SECURITY_LLM llm_defense"]
        src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py["src/zephyr/security/llm_defense/llm_security/po... production"]
        src_zephyr_security_llm_defense_llm_security_process_sandbox_py["src/zephyr/security/llm_defense/llm_security/pr... production"]
        src_zephyr_security_llm_defense_llm_security_protocol_py["src/zephyr/security/llm_defense/llm_security/pr... production"]
        src_zephyr_security_llm_defense_llm_security_red_team_corpus_yaml["src/zephyr/security/llm_defense/llm_security/re... production"]
        src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py["src/zephyr/security/llm_defense/llm_security/ru... production"]
        src_zephyr_security_llm_defense_llm_security_sandbox_init_py["src/zephyr/security/llm_defense/llm_security/sa... prototype"]
        src_zephyr_security_llm_defense_llm_security_self_protection_init_py["src/zephyr/security/llm_defense/llm_security/se... prototype"]
        src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py["src/zephyr/security/llm_defense/llm_security/se... production"]
        src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py["src/zephyr/security/llm_defense/llm_security/se... production"]
        src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py["src/zephyr/security/llm_defense/llm_security/se... production"]
        src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py["src/zephyr/security/llm_defense/llm_security/se... production"]
        src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py["src/zephyr/security/llm_defense/llm_security/se... production"]
        src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py["src/zephyr/security/llm_defense/llm_security/se... production"]
        src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py["src/zephyr/security/llm_defense/llm_security/so... production"]
    end
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    D_SHARED["D_SHARED production"]
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_protocol_py -->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py -.->|import_depends| D_SHARED
    D_GOVERNANCE["D_GOVERNANCE production"]
    src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py -->|import_depends| D_GOVERNANCE
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -.->|import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|import_depends| D_SHARED
    D_INTEGRATION_GATEWAY["D_INTEGRATION_GATEWAY prototype"]
    D_INTEGRATION_GATEWAY -.->|import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST["D_AUDITTEST prototype"]
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py,src_zephyr_security_llm_defense_llm_security_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_protocol_py,src_zephyr_security_llm_defense_llm_security_red_team_corpus_yaml,src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py,src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py,src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py,src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py,src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py,src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py,src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py,src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py production
    class src_zephyr_security_llm_defense_llm_security_sandbox_init_py,src_zephyr_security_llm_defense_llm_security_self_protection_init_py design
    class D_SHARED,D_GOVERNANCE external_prod
    class D_INTEGRATION_GATEWAY,D_AUDITTEST external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |
|--------|:---:|---------|
| D_SHARED | 17 | import_depends |
| D_GOVERNANCE | 2 | import_depends |

### 依赖本域的其他域（入边）/ Depended By

| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |
|------|:---:|---------|
| D_AUDITTEST | 40 | test_depends |
| D_GOVERNANCE | 5 | import_depends |
| D_TRADING | 4 | import_depends |
| D_INTEGRATION_GATEWAY | 2 | import_depends |
| D_AUTONOMY_CORE | 1 | import_depends |
| D_INTEGRATION | 1 | import_depends |

## 架构分层视图 / Architecture Overview

> 按 architecture_layer 分层显示 llm_defense（D_SECURITY_LLM）的模块分布。共 44 个模块 / 44 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (44 modules)             │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/security/llm_defense/__init__.py  [prototype]       │
│   src/zephyr/security/llm_defense/llm_security/__init__.py  [... │
│   src/zephyr/security/llm_defense/llm_security/adversarial_ro... │
│   src/zephyr/security/llm_defense/llm_security/alignment_scor... │
│   src/zephyr/security/llm_defense/llm_security/behavior_audit... │
│   src/zephyr/security/llm_defense/llm_security/dashboard/__in... │
│   src/zephyr/security/llm_defense/llm_security/dashboard/app.... │
│   src/zephyr/security/llm_defense/llm_security/gateway.py  [p... │
│   src/zephyr/security/llm_defense/llm_security/input_sanitize... │
│   src/zephyr/security/llm_defense/llm_security/layers/__init_... │
│   src/zephyr/security/llm_defense/llm_security/layers/l0_supp... │
│   src/zephyr/security/llm_defense/llm_security/layers/l1_inpu... │
│   src/zephyr/security/llm_defense/llm_security/layers/l2_prom... │
│   src/zephyr/security/llm_defense/llm_security/layers/l2a_pro... │
│   src/zephyr/security/llm_defense/llm_security/layers/l3_outp... │
│   src/zephyr/security/llm_defense/llm_security/layers/l4_agen... │
│   src/zephyr/security/llm_defense/llm_security/layers/l5_reso... │
│   src/zephyr/security/llm_defense/llm_security/layers/l6_data... │
│   ...还有 26 个模块 / 26 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 44 个模块 / 44 modules）。

### L1 基础层 / Foundation Layer (44 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/security/llm_defense/__init__.py | src/zephyr/security/llm_defense/__ini... | prototype | generated |
| 2 | src/zephyr/security/llm_defense/llm_security/__init__.py | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 3 | src/zephyr/security/llm_defense/llm_security/adversarial_... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 4 | src/zephyr/security/llm_defense/llm_security/alignment_sc... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 5 | src/zephyr/security/llm_defense/llm_security/behavior_aud... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 6 | src/zephyr/security/llm_defense/llm_security/dashboard/__... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 7 | src/zephyr/security/llm_defense/llm_security/dashboard/ap... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 8 | src/zephyr/security/llm_defense/llm_security/gateway.py | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 9 | src/zephyr/security/llm_defense/llm_security/input_saniti... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 10 | src/zephyr/security/llm_defense/llm_security/layers/__ini... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 11 | src/zephyr/security/llm_defense/llm_security/layers/l0_su... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 12 | src/zephyr/security/llm_defense/llm_security/layers/l1_in... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 13 | src/zephyr/security/llm_defense/llm_security/layers/l2_pr... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 14 | src/zephyr/security/llm_defense/llm_security/layers/l2a_p... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 15 | src/zephyr/security/llm_defense/llm_security/layers/l3_ou... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 16 | src/zephyr/security/llm_defense/llm_security/layers/l4_ag... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 17 | src/zephyr/security/llm_defense/llm_security/layers/l5_re... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 18 | src/zephyr/security/llm_defense/llm_security/layers/l6_da... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 19 | src/zephyr/security/llm_defense/llm_security/layers/l6_ob... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 20 | src/zephyr/security/llm_defense/llm_security/layers/l8_co... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 21 | src/zephyr/security/llm_defense/llm_security/layers/l8_mu... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 22 | src/zephyr/security/llm_defense/llm_security/lsg_pattern_... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 23 | src/zephyr/security/llm_defense/llm_security/patterns/__i... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 24 | src/zephyr/security/llm_defense/llm_security/patterns/inj... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 25 | src/zephyr/security/llm_defense/llm_security/patterns/sec... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 26 | src/zephyr/security/llm_defense/llm_security/payloads/__i... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 27 | src/zephyr/security/llm_defense/llm_security/payloads/inj... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 28 | src/zephyr/security/llm_defense/llm_security/payloads/lea... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 29 | src/zephyr/security/llm_defense/llm_security/payloads/red... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 30 | src/zephyr/security/llm_defense/llm_security/payloads/too... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 31 | src/zephyr/security/llm_defense/llm_security/poisoning_mo... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 32 | src/zephyr/security/llm_defense/llm_security/process_sand... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 33 | src/zephyr/security/llm_defense/llm_security/protocol.py | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 34 | src/zephyr/security/llm_defense/llm_security/red_team_cor... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 35 | src/zephyr/security/llm_defense/llm_security/runtime_inte... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 36 | src/zephyr/security/llm_defense/llm_security/sandbox/__in... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 37 | src/zephyr/security/llm_defense/llm_security/self_protect... | src/zephyr/security/llm_defense/llm_s... | prototype | generated |
| 38 | src/zephyr/security/llm_defense/llm_security/self_protect... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 39 | src/zephyr/security/llm_defense/llm_security/self_protect... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 40 | src/zephyr/security/llm_defense/llm_security/self_protect... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 41 | src/zephyr/security/llm_defense/llm_security/self_protect... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 42 | src/zephyr/security/llm_defense/llm_security/self_protect... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 43 | src/zephyr/security/llm_defense/llm_security/sensitivity_... | src/zephyr/security/llm_defense/llm_s... | production | generated |
| 44 | src/zephyr/security/llm_defense/llm_security/solo_dev_saf... | src/zephyr/security/llm_defense/llm_s... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 47 条 / 47 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 47 条 / 47 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 39 条 / edges                                │
│   [config_depends]: 8 条 / edges                                 │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (39 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   gateway.py → protocol.py                                       │
│   gateway.py → runtime_interceptor.py                            │
│   gateway.py → l0_supply_chain.py                                │
│   gateway.py → l1_input.py                                       │
│   gateway.py → l2a_process_sandbox.py                            │
│   gateway.py → l2_prompt_protection.py                           │
│   gateway.py → l3_output.py                                      │
│   gateway.py → l5_resource_protection.py                         │
│   gateway.py → l8_multi_agent.py                                 │
│   gateway.py → l4_agent.py                                       │
│   gateway.py → l6_observability.py                               │
│   gateway.py → l7_validation.py                                  │
│   app.py → behavior_audit_logger.py                              │
│   app.py → input_sanitizer.py                                    │
│   app.py → protocol.py                                           │
│   app.py → __init__.py                                           │
│   app.py → __init__.py                                           │
│   app.py → __init__.py                                           │
│   app.py → __init__.py                                           │
│   __init__.py → behavior_audit_logger.py                         │
│   __init__.py → input_sanitizer.py                               │
│   __init__.py → gateway.py                                       │
│   __init__.py → process_sandbox.py                               │
│   __init__.py → protocol.py                                      │
│   l0_supply_chain.py → protocol.py                               │
│   l1_input.py → protocol.py                                      │
│   l2a_process_sandbox.py → protocol.py                           │
│   l2_prompt_protection.py → protocol.py                          │
│   l3_output.py → protocol.py                                     │
│   l5_resource_protection.py → protocol.py                        │
│   l8_multi_agent.py → protocol.py                                │
│   l4_agent.py → protocol.py                                      │
│   l6_observability.py → protocol.py                              │
│   adversarial_mutator.py → gateway.py                            │
│   red_team_scanner.py → gateway.py                               │
│   red_team_scanner.py → protocol.py                              │
│   red_team_scanner.py → __init__.py                              │
│   l7_validation.py → protocol.py                                 │
│   l7_validation.py → code_integrity.py                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [config_depends] (8 条 / edges)                  │
├──────────────────────────────────────────────────────────────────┤
│   __init__.py → app.py                                           │
│   l6_data_flow.py → __init__.py                                  │
│   l8_compliance.py → __init__.py                                 │
│   red_team_corpus.yaml → __init__.py                             │
│   injection_payloads.yaml → __init__.py                          │
│   leak_probe_phrases.yaml → __init__.py                          │
│   red_team_payloads.yaml → __init__.py                           │
│   tool_call_payloads.yaml → __init__.py                          │
└──────────────────────────────────────────────────────────────────┘

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
