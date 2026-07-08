---
doc_type: architecture_view
title: D_SECURITY_LLM LLM防御架构文档
version: "1.0"
status: active
date: 2026-07-09
owner: auto-generator
ttl: permanent
---

# 18_d_security_llm / llm_defense / LLM防御 / LLM Defense

> **功能简介 / Overview**: LLM 防御，负责 LLM 安全防护、Prompt 注入防御和输出过滤

> **文档作用 / Purpose**: 展示 LLM防御（D_SECURITY_LLM）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 最后更新: 2026-07-09 05:45:35
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 18 | Number | 18 |
| 域ID | D_SECURITY_LLM | Domain ID | D_SECURITY_LLM |
| 域名称 | LLM防御 | Domain Name | LLM Defense |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 44 | Module Count | 44 |
| 域内依赖 | 47 | Internal Dependencies | 47 |
| 跨域入边 | 57 | Cross-domain Incoming | 57 |
| 跨域出边 | 19 | Cross-domain Outgoing | 19 |
| 设计态模块 | 0 | Design Modules | 0 |
| 原型态模块 | 11 | Prototype Modules | 11 |
| 生产态模块 | 33 | Production Modules | 33 |
| 容量 | 33/150 (正常) | Capacity | 33/150 (正常) |
| 描述 | L0供应链安全(模型验证/依赖扫描) | Description | L0供应链安全(模型验证/依赖扫描) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 44 个模块 / 44 modules）。

### L1 基础层 / Foundation Layer (44 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/security/llm_defense/__init__.py | __init__.py | 原型态 / prototype |  |
| 2 | src/zephyr/security/llm_defense/llm_security/__init__.py | __init__.py | 原型态 / prototype |  |
| 3 | src/zephyr/security/llm_defense/llm_security/adversarial_... | adversarial_robustness.py — 对抗鲁棒性 (B8, DD... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 4 | src/zephyr/security/llm_defense/llm_security/alignment_sc... | alignment_scorer.py — 对齐评分 (B11, DD85, TAS... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 5 | src/zephyr/security/llm_defense/llm_security/behavior_aud... | behavior_audit_logger.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 6 | src/zephyr/security/llm_defense/llm_security/dashboard/__... | LLM Security Gateway Dashboard Module. | 原型态 / prototype | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 7 | src/zephyr/security/llm_defense/llm_security/dashboard/ap... | LLM Security Gateway - Streamlit Dashboard. | 原型态 / prototype | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 8 | src/zephyr/security/llm_defense/llm_security/gateway.py | gateway.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 9 | src/zephyr/security/llm_defense/llm_security/input_saniti... | InputSanitizer: path whitelist + command whitel... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 10 | src/zephyr/security/llm_defense/llm_security/layers/__ini... | __init__.py | 原型态 / prototype |  |
| 11 | src/zephyr/security/llm_defense/llm_security/layers/l0_su... | l0_supply_chain.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 12 | src/zephyr/security/llm_defense/llm_security/layers/l1_in... | l1_input.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 13 | src/zephyr/security/llm_defense/llm_security/layers/l2_pr... | l2_prompt_protection.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 14 | src/zephyr/security/llm_defense/llm_security/layers/l2a_p... | l2a_process_sandbox.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 15 | src/zephyr/security/llm_defense/llm_security/layers/l3_ou... | l3_output.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 16 | src/zephyr/security/llm_defense/llm_security/layers/l4_ag... | l4_agent.py | 生产态 / production |  |
| 17 | src/zephyr/security/llm_defense/llm_security/layers/l5_re... | l5_resource_protection.py | 生产态 / production |  |
| 18 | src/zephyr/security/llm_defense/llm_security/layers/l6_da... | l6_data_flow.py | 原型态 / prototype | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 19 | src/zephyr/security/llm_defense/llm_security/layers/l6_ob... | L6 Observability Layer — security event loggin... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 20 | src/zephyr/security/llm_defense/llm_security/layers/l8_co... | l8_compliance.py | 原型态 / prototype | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 21 | src/zephyr/security/llm_defense/llm_security/layers/l8_mu... | l8_multi_agent.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 22 | src/zephyr/security/llm_defense/llm_security/lsg_pattern_... | lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 23 | src/zephyr/security/llm_defense/llm_security/patterns/__i... | __init__.py | 原型态 / prototype |  |
| 24 | src/zephyr/security/llm_defense/llm_security/patterns/inj... | injection_patterns.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 25 | src/zephyr/security/llm_defense/llm_security/patterns/sec... | secrets.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 26 | src/zephyr/security/llm_defense/llm_security/payloads/__i... | __init__.py | 原型态 / prototype |  |
| 27 | src/zephyr/security/llm_defense/llm_security/payloads/inj... | 提示词注入攻击载荷库——覆盖直接/间接/跨语言注入 | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 28 | src/zephyr/security/llm_defense/llm_security/payloads/lea... | 提示词泄露探测短语——用于主动扫描模型是否泄露... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 29 | src/zephyr/security/llm_defense/llm_security/payloads/red... | Red Team 攻击载荷库——覆盖 OWASP LLM01-LLM10 ... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 30 | src/zephyr/security/llm_defense/llm_security/payloads/too... | Agent工具调用攻击载荷——覆盖权限提升/参数混淆/... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 31 | src/zephyr/security/llm_defense/llm_security/poisoning_mo... | poisoning_monitor.py — Embed 污染检测 (DD97, T... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 32 | src/zephyr/security/llm_defense/llm_security/process_sand... | L2a ProcessSandbox — subprocess 路径白名单沙箱 | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 33 | src/zephyr/security/llm_defense/llm_security/protocol.py | protocol.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 34 | src/zephyr/security/llm_defense/llm_security/red_team_cor... | LSG 红队语料库种子文件。对标 06-security_archit... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 35 | src/zephyr/security/llm_defense/llm_security/runtime_inte... | runtime_interceptor.py — 运行时 LLM 裸调拦截器... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 36 | src/zephyr/security/llm_defense/llm_security/sandbox/__in... | LSG 代码执行沙箱包。 | 原型态 / prototype | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 37 | src/zephyr/security/llm_defense/llm_security/self_protect... | __init__.py | 原型态 / prototype |  |
| 38 | src/zephyr/security/llm_defense/llm_security/self_protect... | adversarial_mutator.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 39 | src/zephyr/security/llm_defense/llm_security/self_protect... | code_integrity.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 40 | src/zephyr/security/llm_defense/llm_security/self_protect... | isolation.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 41 | src/zephyr/security/llm_defense/llm_security/self_protect... | l7_validation.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 42 | src/zephyr/security/llm_defense/llm_security/self_protect... | red_team_scanner.py | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 43 | src/zephyr/security/llm_defense/llm_security/sensitivity_... | sensitivity_classifier.py — 数据分级 (B9, DD83... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |
| 44 | src/zephyr/security/llm_defense/llm_security/solo_dev_saf... | solo_dev_safety_net.py — 单人无审查安全网 (B15... | 生产态 / production | [MOD-LLM_SECURITY](../../03_modules/_cross_layer/large_language_model_security/blueprint.md) |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分四个视图：合并全景图、运营态子图、设计态子图、原型态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **虚线边框 = 原型态模块**（prototype，代码已写，验证中未稳定上线）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 44 个模块（生产态 33 + 设计态 0 + 原型态 11），标签标注成熟度。

#### 第 1 页 / 共 2 页

```mermaid
graph TD
    subgraph D_SECURITY_LLM["D_SECURITY_LLM LLM防御"]
        src_zephyr_security_llm_defense_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py["(生产态 / production) adversarial_robustness.py — 对抗鲁棒性 (B8, DD...<br/>文件: adversarial_robustness.py"]
        src_zephyr_security_llm_defense_llm_security_alignment_scorer_py["(生产态 / production) alignment_scorer.py — 对齐评分 (B11, DD85, TAS...<br/>文件: alignment_scorer.py"]
        src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py["(生产态 / production) behavior_audit_logger.py"]
        src_zephyr_security_llm_defense_llm_security_dashboard_init_py["(原型态 / prototype) LLM Security Gateway Dashboard Module.<br/>文件: __init__.py"]
        src_zephyr_security_llm_defense_llm_security_dashboard_app_py["(原型态 / prototype) LLM Security Gateway - Streamlit Dashboard.<br/>文件: app.py"]
        src_zephyr_security_llm_defense_llm_security_gateway_py["(生产态 / production) gateway.py"]
        src_zephyr_security_llm_defense_llm_security_input_sanitizer_py["(生产态 / production) InputSanitizer: path whitelist + command whitel...<br/>文件: input_sanitizer.py"]
        src_zephyr_security_llm_defense_llm_security_layers_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py["(生产态 / production) l0_supply_chain.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l1_input_py["(生产态 / production) l1_input.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py["(生产态 / production) l2_prompt_protection.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py["(生产态 / production) l2a_process_sandbox.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l3_output_py["(生产态 / production) l3_output.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py["(生产态 / production) l4_agent.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py["(生产态 / production) l5_resource_protection.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py["(原型态 / prototype) l6_data_flow.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py["(生产态 / production) L6 Observability Layer — security event loggin...<br/>文件: l6_observability.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py["(原型态 / prototype) l8_compliance.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py["(生产态 / production) l8_multi_agent.py"]
        src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py["(生产态 / production) lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20...<br/>文件: lsg_pattern_tracker.py"]
        src_zephyr_security_llm_defense_llm_security_patterns_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py["(生产态 / production) injection_patterns.py"]
        src_zephyr_security_llm_defense_llm_security_patterns_secrets_py["(生产态 / production) secrets.py"]
        src_zephyr_security_llm_defense_llm_security_payloads_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml["(生产态 / production) 提示词注入攻击载荷库——覆盖直接/间接/跨语言注入<br/>文件: injection_payloads.yaml"]
        src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml["(生产态 / production) 提示词泄露探测短语——用于主动扫描模型是否泄露...<br/>文件: leak_probe_phrases.yaml"]
        src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml["(生产态 / production) Red Team 攻击载荷库——覆盖 OWASP LLM01-LLM10 ...<br/>文件: red_team_payloads.yaml"]
        src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml["(生产态 / production) Agent工具调用攻击载荷——覆盖权限提升/参数混淆/...<br/>文件: tool_call_payloads.yaml"]
    end
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_init_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_init_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_init_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_patterns_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_init_py -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE -.->|contract / contract| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION_GATEWAY["(生产态 / production) D_INTEGRATION_GATEWAY"]
    D_INTEGRATION_GATEWAY -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_init_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_alignment_scorer_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py,src_zephyr_security_llm_defense_llm_security_alignment_scorer_py,src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py,src_zephyr_security_llm_defense_llm_security_gateway_py,src_zephyr_security_llm_defense_llm_security_input_sanitizer_py,src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py,src_zephyr_security_llm_defense_llm_security_layers_l1_input_py,src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_layers_l3_output_py,src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py,src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py,src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py,src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py,src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py,src_zephyr_security_llm_defense_llm_security_patterns_secrets_py,src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml,src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml,src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml,src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml production
    class src_zephyr_security_llm_defense_init_py,src_zephyr_security_llm_defense_llm_security_init_py,src_zephyr_security_llm_defense_llm_security_dashboard_init_py,src_zephyr_security_llm_defense_llm_security_dashboard_app_py,src_zephyr_security_llm_defense_llm_security_layers_init_py,src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py,src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py,src_zephyr_security_llm_defense_llm_security_patterns_init_py,src_zephyr_security_llm_defense_llm_security_payloads_init_py design
    class D_SHARED,D_GOVERNANCE,D_AUTONOMY_CORE,D_INTEGRATION,D_INTEGRATION_GATEWAY,D_TRADING external_prod
    class D_AUDITTEST external_design
```

#### 第 2 页 / 共 2 页

```mermaid
graph TD
    subgraph D_SECURITY_LLM["D_SECURITY_LLM LLM防御"]
        src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py["(生产态 / production) poisoning_monitor.py — Embed 污染检测 (DD97, T...<br/>文件: poisoning_monitor.py"]
        src_zephyr_security_llm_defense_llm_security_process_sandbox_py["(生产态 / production) L2a ProcessSandbox — subprocess 路径白名单沙箱<br/>文件: process_sandbox.py"]
        src_zephyr_security_llm_defense_llm_security_protocol_py["(生产态 / production) protocol.py"]
        src_zephyr_security_llm_defense_llm_security_red_team_corpus_yaml["(生产态 / production) LSG 红队语料库种子文件。对标 06-security_archit...<br/>文件: red_team_corpus.yaml"]
        src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py["(生产态 / production) runtime_interceptor.py — 运行时 LLM 裸调拦截器...<br/>文件: runtime_interceptor.py"]
        src_zephyr_security_llm_defense_llm_security_sandbox_init_py["(原型态 / prototype) LSG 代码执行沙箱包。<br/>文件: __init__.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py["(生产态 / production) adversarial_mutator.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py["(生产态 / production) code_integrity.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py["(生产态 / production) isolation.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py["(生产态 / production) l7_validation.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py["(生产态 / production) red_team_scanner.py"]
        src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py["(生产态 / production) sensitivity_classifier.py — 数据分级 (B9, DD83...<br/>文件: sensitivity_classifier.py"]
        src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py["(生产态 / production) solo_dev_safety_net.py — 单人无审查安全网 (B15...<br/>文件: solo_dev_safety_net.py"]
    end
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_protocol_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -.->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION_GATEWAY["(生产态 / production) D_INTEGRATION_GATEWAY"]
    D_INTEGRATION_GATEWAY -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py,src_zephyr_security_llm_defense_llm_security_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_protocol_py,src_zephyr_security_llm_defense_llm_security_red_team_corpus_yaml,src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py,src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py,src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py,src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py,src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py,src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py,src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py,src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py production
    class src_zephyr_security_llm_defense_llm_security_sandbox_init_py,src_zephyr_security_llm_defense_llm_security_self_protection_init_py design
    class D_SHARED,D_GOVERNANCE,D_INTEGRATION_GATEWAY external_prod
    class D_AUDITTEST external_design
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 33 个，26 条域内依赖）。

```mermaid
graph TD
    subgraph D_SECURITY_LLM["D_SECURITY_LLM LLM防御"]
        src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py["(生产态 / production) adversarial_robustness.py — 对抗鲁棒性 (B8, DD...<br/>文件: adversarial_robustness.py"]
        src_zephyr_security_llm_defense_llm_security_alignment_scorer_py["(生产态 / production) alignment_scorer.py — 对齐评分 (B11, DD85, TAS...<br/>文件: alignment_scorer.py"]
        src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py["(生产态 / production) behavior_audit_logger.py"]
        src_zephyr_security_llm_defense_llm_security_gateway_py["(生产态 / production) gateway.py"]
        src_zephyr_security_llm_defense_llm_security_input_sanitizer_py["(生产态 / production) InputSanitizer: path whitelist + command whitel...<br/>文件: input_sanitizer.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py["(生产态 / production) l0_supply_chain.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l1_input_py["(生产态 / production) l1_input.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py["(生产态 / production) l2_prompt_protection.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py["(生产态 / production) l2a_process_sandbox.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l3_output_py["(生产态 / production) l3_output.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py["(生产态 / production) l4_agent.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py["(生产态 / production) l5_resource_protection.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py["(生产态 / production) L6 Observability Layer — security event loggin...<br/>文件: l6_observability.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py["(生产态 / production) l8_multi_agent.py"]
        src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py["(生产态 / production) lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20...<br/>文件: lsg_pattern_tracker.py"]
        src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py["(生产态 / production) injection_patterns.py"]
        src_zephyr_security_llm_defense_llm_security_patterns_secrets_py["(生产态 / production) secrets.py"]
        src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml["(生产态 / production) 提示词注入攻击载荷库——覆盖直接/间接/跨语言注入<br/>文件: injection_payloads.yaml"]
        src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml["(生产态 / production) 提示词泄露探测短语——用于主动扫描模型是否泄露...<br/>文件: leak_probe_phrases.yaml"]
        src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml["(生产态 / production) Red Team 攻击载荷库——覆盖 OWASP LLM01-LLM10 ...<br/>文件: red_team_payloads.yaml"]
        src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml["(生产态 / production) Agent工具调用攻击载荷——覆盖权限提升/参数混淆/...<br/>文件: tool_call_payloads.yaml"]
        src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py["(生产态 / production) poisoning_monitor.py — Embed 污染检测 (DD97, T...<br/>文件: poisoning_monitor.py"]
        src_zephyr_security_llm_defense_llm_security_process_sandbox_py["(生产态 / production) L2a ProcessSandbox — subprocess 路径白名单沙箱<br/>文件: process_sandbox.py"]
        src_zephyr_security_llm_defense_llm_security_protocol_py["(生产态 / production) protocol.py"]
        src_zephyr_security_llm_defense_llm_security_red_team_corpus_yaml["(生产态 / production) LSG 红队语料库种子文件。对标 06-security_archit...<br/>文件: red_team_corpus.yaml"]
        src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py["(生产态 / production) runtime_interceptor.py — 运行时 LLM 裸调拦截器...<br/>文件: runtime_interceptor.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py["(生产态 / production) adversarial_mutator.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py["(生产态 / production) code_integrity.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py["(生产态 / production) isolation.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py["(生产态 / production) l7_validation.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py["(生产态 / production) red_team_scanner.py"]
        src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py["(生产态 / production) sensitivity_classifier.py — 数据分级 (B9, DD83...<br/>文件: sensitivity_classifier.py"]
        src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py["(生产态 / production) solo_dev_safety_net.py — 单人无审查安全网 (B15...<br/>文件: solo_dev_safety_net.py"]
    end
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l1_input_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l3_output_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py
    src_zephyr_security_llm_defense_llm_security_gateway_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(生产态 / production) D_GOVERNANCE"]
    src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py -->|导入依赖 / import_depends| D_GOVERNANCE
    src_zephyr_security_llm_defense_llm_security_process_sandbox_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_protocol_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l1_input_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l3_output_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_patterns_secrets_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py -.->|导入依赖 / import_depends| D_SHARED
    D_AUTONOMY_CORE["(生产态 / production) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_GOVERNANCE -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION_GATEWAY["(生产态 / production) D_INTEGRATION_GATEWAY"]
    D_INTEGRATION_GATEWAY -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_INTEGRATION_GATEWAY -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_protocol_py
    D_TRADING["(生产态 / production) D_TRADING"]
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_TRADING -->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_gateway_py
    D_TRADING -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_input_sanitizer_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_alignment_scorer_py
    D_AUDITTEST -.->|测试依赖 / test_depends| src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py,src_zephyr_security_llm_defense_llm_security_alignment_scorer_py,src_zephyr_security_llm_defense_llm_security_behavior_audit_logger_py,src_zephyr_security_llm_defense_llm_security_gateway_py,src_zephyr_security_llm_defense_llm_security_input_sanitizer_py,src_zephyr_security_llm_defense_llm_security_layers_l0_supply_chain_py,src_zephyr_security_llm_defense_llm_security_layers_l1_input_py,src_zephyr_security_llm_defense_llm_security_layers_l2_prompt_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l2a_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_layers_l3_output_py,src_zephyr_security_llm_defense_llm_security_layers_l4_agent_py,src_zephyr_security_llm_defense_llm_security_layers_l5_resource_protection_py,src_zephyr_security_llm_defense_llm_security_layers_l6_observability_py,src_zephyr_security_llm_defense_llm_security_layers_l8_multi_agent_py,src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py,src_zephyr_security_llm_defense_llm_security_patterns_injection_patterns_py,src_zephyr_security_llm_defense_llm_security_patterns_secrets_py,src_zephyr_security_llm_defense_llm_security_payloads_injection_payloads_yaml,src_zephyr_security_llm_defense_llm_security_payloads_leak_probe_phrases_yaml,src_zephyr_security_llm_defense_llm_security_payloads_red_team_payloads_yaml,src_zephyr_security_llm_defense_llm_security_payloads_tool_call_payloads_yaml,src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py,src_zephyr_security_llm_defense_llm_security_process_sandbox_py,src_zephyr_security_llm_defense_llm_security_protocol_py,src_zephyr_security_llm_defense_llm_security_red_team_corpus_yaml,src_zephyr_security_llm_defense_llm_security_runtime_interceptor_py,src_zephyr_security_llm_defense_llm_security_self_protection_adversarial_mutator_py,src_zephyr_security_llm_defense_llm_security_self_protection_code_integrity_py,src_zephyr_security_llm_defense_llm_security_self_protection_isolation_py,src_zephyr_security_llm_defense_llm_security_self_protection_l7_validation_py,src_zephyr_security_llm_defense_llm_security_self_protection_red_team_scanner_py,src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py,src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py production
    class D_SHARED,D_GOVERNANCE,D_AUTONOMY_CORE,D_INTEGRATION,D_INTEGRATION_GATEWAY,D_TRADING external_prod
    class D_AUDITTEST external_design
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

### 原型态子图（仅 design_maturity=prototype 的模块和依赖）

> 仅展示代码已写、验证中未稳定上线的原型态模块（共 11 个，7 条域内依赖）。

```mermaid
graph TD
    subgraph D_SECURITY_LLM["D_SECURITY_LLM LLM防御"]
        src_zephyr_security_llm_defense_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_dashboard_init_py["(原型态 / prototype) LLM Security Gateway Dashboard Module.<br/>文件: __init__.py"]
        src_zephyr_security_llm_defense_llm_security_dashboard_app_py["(原型态 / prototype) LLM Security Gateway - Streamlit Dashboard.<br/>文件: app.py"]
        src_zephyr_security_llm_defense_llm_security_layers_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py["(原型态 / prototype) l6_data_flow.py"]
        src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py["(原型态 / prototype) l8_compliance.py"]
        src_zephyr_security_llm_defense_llm_security_patterns_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_payloads_init_py["(原型态 / prototype) __init__.py"]
        src_zephyr_security_llm_defense_llm_security_sandbox_init_py["(原型态 / prototype) LSG 代码执行沙箱包。<br/>文件: __init__.py"]
        src_zephyr_security_llm_defense_llm_security_self_protection_init_py["(原型态 / prototype) __init__.py"]
    end
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_payloads_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_patterns_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_self_protection_init_py
    src_zephyr_security_llm_defense_llm_security_dashboard_init_py -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py -.->|config_depends / config_depends| src_zephyr_security_llm_defense_llm_security_layers_init_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_security_llm_defense_llm_security_dashboard_app_py -.->|导入依赖 / import_depends| D_SHARED
    D_GOVERNANCE["(原型态 / prototype) D_GOVERNANCE"]
    D_GOVERNANCE -.->|导入依赖 / import_depends| src_zephyr_security_llm_defense_llm_security_init_py
    D_AUDITTEST["(原型态 / prototype) D_AUDITTEST"]
    D_AUDITTEST -.->|runtime / runtime| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    D_AUTONOMY_CORE["(原型态 / prototype) D_AUTONOMY_CORE"]
    D_AUTONOMY_CORE -.->|runtime / runtime| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    D_GOVERNANCE -.->|contract / contract| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    D_GOVERNANCE -.->|contract / contract| src_zephyr_security_llm_defense_llm_security_dashboard_app_py
    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000
    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5
    class src_zephyr_security_llm_defense_init_py,src_zephyr_security_llm_defense_llm_security_init_py,src_zephyr_security_llm_defense_llm_security_dashboard_init_py,src_zephyr_security_llm_defense_llm_security_dashboard_app_py,src_zephyr_security_llm_defense_llm_security_layers_init_py,src_zephyr_security_llm_defense_llm_security_layers_l6_data_flow_py,src_zephyr_security_llm_defense_llm_security_layers_l8_compliance_py,src_zephyr_security_llm_defense_llm_security_patterns_init_py,src_zephyr_security_llm_defense_llm_security_payloads_init_py,src_zephyr_security_llm_defense_llm_security_sandbox_init_py,src_zephyr_security_llm_defense_llm_security_self_protection_init_py design
    class D_SHARED external_prod
    class D_GOVERNANCE,D_AUDITTEST,D_AUTONOMY_CORE external_design
```

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | behavior_audit_logger.py | → | D_GOVERNANCE 生命周期管理: bridge.py | 导入依赖 / import_depends |
| 2 | isolation.py | → | D_GOVERNANCE 生命周期管理: bridge.py | 导入依赖 / import_depends |
| 3 | behavior_audit_logger.py | → | D_SHARED 共享服务: time_utils.py —— 时间/日期工具（Phase 9 新增 ... | 导入依赖 / import_depends |
| 4 | LLM Security Gateway - Streamlit Dashboard. (ap... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 5 | l0_supply_chain.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 6 | l1_input.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 7 | l2_prompt_protection.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 8 | l2a_process_sandbox.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 9 | l3_output.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 10 | l4_agent.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 11 | l5_resource_protection.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 12 | L6 Observability Layer — security event loggin... | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 13 | l8_multi_agent.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 14 | secrets.py | → | D_SHARED 共享服务: secrets.py —— Secrets 管理抽象（Phase 7 新增 ... | 导入依赖 / import_depends |
| 15 | L2a ProcessSandbox — subprocess 路径白名单沙箱... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 16 | protocol.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 17 | adversarial_mutator.py | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 18 | l7_validation.py | → | D_SHARED 共享服务: security_decision.py | 导入依赖 / import_depends |
| 19 | red_team_scanner.py | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_AUDITTEST 审计测试套件: test_auto_bootstrap.py | → | LLM Security Gateway - Streamlit Dashboard. (ap... | runtime / runtime |
| 2 | D_AUDITTEST 审计测试套件: test_adversarial_robustness.py | → | adversarial_robustness.py — 对抗鲁棒性 (B8, DD... | 测试依赖 / test_depends |
| 3 | D_AUDITTEST 审计测试套件: test_alignment_scorer.py | → | alignment_scorer.py — 对齐评分 (B11, DD85, TAS... | 测试依赖 / test_depends |
| 4 | D_AUDITTEST 审计测试套件: test_lsg_pattern_tracker.py | → | lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20... | 测试依赖 / test_depends |
| 5 | D_AUDITTEST 审计测试套件: test_poisoning_monitor.py | → | poisoning_monitor.py — Embed 污染检测 (DD97, T... | 测试依赖 / test_depends |
| 6 | D_AUDITTEST 审计测试套件: test_sensitivity_classifier.py | → | sensitivity_classifier.py — 数据分级 (B9, DD83... | 测试依赖 / test_depends |
| 7 | D_AUDITTEST 审计测试套件: test_solo_dev_safety_net.py | → | solo_dev_safety_net.py — 单人无审查安全网 (B15... | 测试依赖 / test_depends |
| 8 | D_AUDITTEST 审计测试套件: test_adversarial_mutator.py | → | adversarial_mutator.py | 测试依赖 / test_depends |
| 9 | D_AUDITTEST 审计测试套件: test_behavior_audit_logger.py | → | behavior_audit_logger.py | 测试依赖 / test_depends |
| 10 | D_AUDITTEST 审计测试套件: test_code_integrity.py | → | code_integrity.py | 测试依赖 / test_depends |
| 11 | D_AUDITTEST 审计测试套件: test_db.py | → | InputSanitizer: path whitelist + command whitel... | 测试依赖 / test_depends |
| 12 | D_AUDITTEST 审计测试套件: test_fail_closed.py | → | gateway.py | 测试依赖 / test_depends |
| 13 | D_AUDITTEST 审计测试套件: test_fail_closed.py | → | protocol.py | 测试依赖 / test_depends |
| 14 | D_AUDITTEST 审计测试套件: test_gateway_e2e.py | → | gateway.py | 测试依赖 / test_depends |
| 15 | D_AUDITTEST 审计测试套件: test_injection_patterns.py | → | injection_patterns.py | 测试依赖 / test_depends |
| 16 | D_AUDITTEST 审计测试套件: test_input_sanitizer_llm_security.py | → | InputSanitizer: path whitelist + command whitel... | 测试依赖 / test_depends |
| 17 | D_AUDITTEST 审计测试套件: test_isolation.py | → | isolation.py | 测试依赖 / test_depends |
| 18 | D_AUDITTEST 审计测试套件: test_l0_supply_chain.py | → | l0_supply_chain.py | 测试依赖 / test_depends |
| 19 | D_AUDITTEST 审计测试套件: test_l0_supply_chain.py | → | protocol.py | 测试依赖 / test_depends |
| 20 | D_AUDITTEST 审计测试套件: test_l1_input_defense.py | → | l1_input.py | 测试依赖 / test_depends |
| 21 | D_AUDITTEST 审计测试套件: test_l1_input_defense.py | → | protocol.py | 测试依赖 / test_depends |
| 22 | D_AUDITTEST 审计测试套件: test_l2_prompt_protection.py | → | l2_prompt_protection.py | 测试依赖 / test_depends |
| 23 | D_AUDITTEST 审计测试套件: test_l2_prompt_protection.py | → | protocol.py | 测试依赖 / test_depends |
| 24 | D_AUDITTEST 审计测试套件: test_l2a_process_sandbox.py | → | l2a_process_sandbox.py | 测试依赖 / test_depends |
| 25 | D_AUDITTEST 审计测试套件: test_l3_output_security.py | → | l3_output.py | 测试依赖 / test_depends |
| 26 | D_AUDITTEST 审计测试套件: test_l3_output_security.py | → | protocol.py | 测试依赖 / test_depends |
| 27 | D_AUDITTEST 审计测试套件: test_l4_agent_security.py | → | l4_agent.py | 测试依赖 / test_depends |
| 28 | D_AUDITTEST 审计测试套件: test_l4_agent_security.py | → | protocol.py | 测试依赖 / test_depends |
| 29 | D_AUDITTEST 审计测试套件: test_l5_resource_protection.py | → | l5_resource_protection.py | 测试依赖 / test_depends |
| 30 | D_AUDITTEST 审计测试套件: test_l5_resource_protection.py | → | protocol.py | 测试依赖 / test_depends |
| 31 | D_AUDITTEST 审计测试套件: test_l6_observability.py | → | L6 Observability Layer — security event loggin... | 测试依赖 / test_depends |
| 32 | D_AUDITTEST 审计测试套件: test_l6_observability.py | → | protocol.py | 测试依赖 / test_depends |
| 33 | D_AUDITTEST 审计测试套件: test_l7_red_team.py | → | red_team_scanner.py | 测试依赖 / test_depends |
| 34 | D_AUDITTEST 审计测试套件: test_l7_validation.py | → | l7_validation.py | 测试依赖 / test_depends |
| 35 | D_AUDITTEST 审计测试套件: test_l8_multi_agent.py | → | l8_multi_agent.py | 测试依赖 / test_depends |
| 36 | D_AUDITTEST 审计测试套件: test_l8_multi_agent.py | → | protocol.py | 测试依赖 / test_depends |
| 37 | D_AUDITTEST 审计测试套件: test_process_sandbox_llm_security.py | → | L2a ProcessSandbox — subprocess 路径白名单沙箱... | 测试依赖 / test_depends |
| 38 | D_AUDITTEST 审计测试套件: test_runtime_interceptor.py — 运行时 LLM 裸调.... | → | gateway.py | 测试依赖 / test_depends |
| 39 | D_AUDITTEST 审计测试套件: test_runtime_interceptor.py — 运行时 LLM 裸调.... | → | protocol.py | 测试依赖 / test_depends |
| 40 | D_AUDITTEST 审计测试套件: test_runtime_interceptor.py — 运行时 LLM 裸调.... | → | runtime_interceptor.py — 运行时 LLM 裸调拦截器... | 测试依赖 / test_depends |
| 41 | D_AUDITTEST 审计测试套件: test_secrets.py | → | secrets.py | 测试依赖 / test_depends |
| 42 | D_AUTONOMY_CORE 自治核心: ContextInjector: retrieve and inject relevant k... | → | gateway.py | 导入依赖 / import_depends |
| 43 | D_AUTONOMY_CORE 自治核心: file_autoregister.py | → | LLM Security Gateway - Streamlit Dashboard. (ap... | runtime / runtime |
| 44 | D_GOVERNANCE 生命周期管理: blueprint.md | → | LLM Security Gateway - Streamlit Dashboard. (ap... | contract / contract |
| 45 | D_GOVERNANCE 生命周期管理: blueprint.md | → | LLM Security Gateway - Streamlit Dashboard. (ap... | contract / contract |
| 46 | D_GOVERNANCE 生命周期管理: C-track 端到端演示 —— 全流水线一次性运行 (dem... | → | __init__.py | 导入依赖 / import_depends |
| 47 | D_GOVERNANCE 生命周期管理: Escalation Engine — MOD-INF-022 (escalation_en... | → | gateway.py | 导入依赖 / import_depends |
| 48 | D_GOVERNANCE 生命周期管理: Delegation Engine — MOD-INF-022 (delegation_en... | → | gateway.py | 导入依赖 / import_depends |
| 49 | D_GOVERNANCE 生命周期管理: DefaultSecurityGateway — SecurityGateway 三层.... | → | gateway.py | 导入依赖 / import_depends |
| 50 | D_GOVERNANCE 生命周期管理: DefaultSecurityGateway — SecurityGateway 三层.... | → | InputSanitizer: path whitelist + command whitel... | 导入依赖 / import_depends |
| 51 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | gateway.py | 导入依赖 / import_depends |
| 52 | D_INTEGRATION_GATEWAY 集成网关: MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | → | gateway.py | 导入依赖 / import_depends |
| 53 | D_INTEGRATION_GATEWAY 集成网关: MCP Gateway 集中式治理节点（MOD-INF-013 §12 Ph... | → | protocol.py | 导入依赖 / import_depends |
| 54 | D_TRADING 交易运营: evolution_engine.py | → | gateway.py | 导入依赖 / import_depends |
| 55 | D_TRADING 交易运营: AgentOrchestrator · 多角色 Agent 路由、工具链.... | → | gateway.py | 导入依赖 / import_depends |
| 56 | D_TRADING 交易运营: AgentOrchestrator · 多角色 Agent 路由、工具链.... | → | InputSanitizer: path whitelist + command whitel... | 导入依赖 / import_depends |
| 57 | D_TRADING 交易运营: agent_orchestrator.py | → | InputSanitizer: path whitelist + command whitel... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 7 个外部域直接连接（出边 19 条 + 入边 57 条 = 76 条）。只显示直接连接的域，不展开具体节点。

```mermaid
graph LR
    D_SECURITY_LLM["D_SECURITY_LLM<br/>LLM防御"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_GOVERNANCE["D_GOVERNANCE<br/>生命周期管理"]
    D_AUDITTEST["D_AUDITTEST<br/>审计测试套件"]
    D_TRADING["D_TRADING<br/>交易运营"]
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_INTEGRATION_GATEWAY["D_INTEGRATION_GATEWAY<br/>集成网关"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_SECURITY_LLM -->|17条 导入依赖 / import_depends| D_SHARED
    D_SECURITY_LLM -->|2条 导入依赖 / import_depends| D_GOVERNANCE
    D_AUDITTEST -->|41条 runtime / runtime, 测试依赖 / test_depends| D_SECURITY_LLM
    D_GOVERNANCE -->|7条 contract / contract, 导入依赖 / import_depends| D_SECURITY_LLM
    D_TRADING -->|4条 导入依赖 / import_depends| D_SECURITY_LLM
    D_AUTONOMY_CORE -->|2条 导入依赖 / import_depends, runtime / runtime| D_SECURITY_LLM
    D_INTEGRATION_GATEWAY -->|2条 导入依赖 / import_depends| D_SECURITY_LLM
    D_INTEGRATION -->|1条 导入依赖 / import_depends| D_SECURITY_LLM
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
