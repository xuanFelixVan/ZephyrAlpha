---
doc_type: domain_architecture_diagram
title: D-INTEGRATION 管线路由架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 11_d_integration / 管线路由 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示管线路由（D-INTEGRATION）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 21:40:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 管线路由（D-INTEGRATION）的模块分布。共 706 个模块 / 706 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (304 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/integration/__init__.py  [production]               │
│   src/zephyr/integration/__init___from_orches.py  [prototype]    │
│   src/zephyr/integration/_extensions/__init__.py  [scaffold_p... │
│   src/zephyr/integration/api/__init__.py  [scaffold_placeholder] │
│   src/zephyr/integration/backpressure_manager.py  [prototype]    │
│   src/zephyr/integration/backpressure_types.py  [prototype]      │
│   src/zephyr/integration/behavioral_admission/__init__.py  [p... │
│   src/zephyr/integration/behavioral_admission/admission_respo... │
│   src/zephyr/integration/budget_enforcer/__init__.py  [protot... │
│   src/zephyr/integration/budget_enforcer/degradation_spiral_d... │
│   src/zephyr/integration/circuit_breaker_manager.py  [prototype] │
│   src/zephyr/integration/contracts/__init__.py  [prototype]      │
│   src/zephyr/integration/contracts/experiment_result.py  [pro... │
│   src/zephyr/integration/contracts/model_serving_response.py ... │
│   src/zephyr/integration/core/__init__.py  [scaffold_placehol... │
│   src/zephyr/integration/cost_tracker.py  [prototype]            │
│   src/zephyr/integration/ct_pipe_routing.py  [prototype]         │
│   src/zephyr/integration/dead_letter_queue.py  [prototype]       │
│   ...还有 286 个模块 / 286 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (402 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   6-Month Data Retention 6个月数据保留  [design]                 │
│   A2A + MCP Dual Protocol A2A+MCP双协议  [design]                │
│   A2A MCP Hybrid Orchestration A2A+MCP混合编排  [design]         │
│   A2A Message Encryption A2A消息加密  [design]                   │
│   A2A Protocol Bridge A2A协议桥接  [design]                      │
│   A2A Protocol Handler A2A协议处理器  [design]                   │
│   A2A Protocol Integration A2A协议集成  [design]                 │
│   A2AProtocolBridge A2A协议桥  [design]                          │
│   ACL Anti-Corruption Layer ACL防腐层  [design]                  │
│   AI Gateway AI网关  [design]                                    │
│   AI Security Boundary Execution Layer AI安全边界执行层  [des... │
│   AI Track AI轨  [design]                                        │
│   API Fuzz Testing API模糊测试  [design]                         │
│   API Gateway API网关  [design]                                  │
│   API Gateway Design API网关设计  [design]                       │
│   API Gateway Four Layer Architecture API网关四层架构  [design]  │
│   API Gateway Layer API网关层  [design]                          │
│   API Gateway Unified Entry API网关统一入口  [design]            │
│   ...还有 384 个模块 / 384 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 706 个模块 / 706 modules）。

### L1 基础层 / Foundation Layer (304 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/integration/__init__.py | src/zephyr/integration/__init__.py | production | draft |
| 2 | src/zephyr/integration/__init___from_orches.py | src/zephyr/integration/__init___from_... | prototype | draft |
| 3 | src/zephyr/integration/_extensions/__init__.py | src/zephyr/integration/_extensions/__... | scaffold_placeholder | orphan |
| 4 | src/zephyr/integration/api/__init__.py | src/zephyr/integration/api/__init__.py | scaffold_placeholder | orphan |
| 5 | src/zephyr/integration/backpressure_manager.py | src/zephyr/integration/backpressure_m... | prototype | draft |
| 6 | src/zephyr/integration/backpressure_types.py | src/zephyr/integration/backpressure_t... | prototype | draft |
| 7 | src/zephyr/integration/behavioral_admission/__init__.py | src/zephyr/integration/behavioral_adm... | prototype | draft |
| 8 | src/zephyr/integration/behavioral_admission/admission_res... | src/zephyr/integration/behavioral_adm... | production | draft |
| 9 | src/zephyr/integration/budget_enforcer/__init__.py | src/zephyr/integration/budget_enforce... | prototype | draft |
| 10 | src/zephyr/integration/budget_enforcer/degradation_spiral... | src/zephyr/integration/budget_enforce... | prototype | draft |
| 11 | src/zephyr/integration/circuit_breaker_manager.py | src/zephyr/integration/circuit_breake... | prototype | draft |
| 12 | src/zephyr/integration/contracts/__init__.py | src/zephyr/integration/contracts/__in... | prototype | draft |
| 13 | src/zephyr/integration/contracts/experiment_result.py | src/zephyr/integration/contracts/expe... | prototype | draft |
| 14 | src/zephyr/integration/contracts/model_serving_response.py | src/zephyr/integration/contracts/mode... | prototype | draft |
| 15 | src/zephyr/integration/core/__init__.py | src/zephyr/integration/core/__init__.py | scaffold_placeholder | orphan |
| 16 | src/zephyr/integration/cost_tracker.py | src/zephyr/integration/cost_tracker.py | prototype | draft |
| 17 | src/zephyr/integration/ct_pipe_routing.py | src/zephyr/integration/ct_pipe_routin... | prototype | draft |
| 18 | src/zephyr/integration/dead_letter_queue.py | src/zephyr/integration/dead_letter_qu... | prototype | draft |
| 19 | src/zephyr/integration/infrastructure/__init__.py | src/zephyr/integration/infrastructure... | scaffold_placeholder | orphan |
| 20 | src/zephyr/integration/layer1_discovery/__init__.py | src/zephyr/integration/layer1_discove... | prototype | draft |
| 21 | src/zephyr/integration/layer1_discovery/a2a_registry.py | src/zephyr/integration/layer1_discove... | prototype | draft |
| 22 | src/zephyr/integration/layer1_discovery/agent_card.py | src/zephyr/integration/layer1_discove... | prototype | draft |
| 23 | src/zephyr/integration/layer1_discovery/identity_verifier.py | src/zephyr/integration/layer1_discove... | prototype | draft |
| 24 | src/zephyr/integration/layer2_communication/__init__.py | src/zephyr/integration/layer2_communi... | prototype | draft |
| 25 | src/zephyr/integration/layer2_communication/a2a_schemas.py | src/zephyr/integration/layer2_communi... | prototype | draft |
| 26 | src/zephyr/integration/layer2_communication/a2a_state.py | src/zephyr/integration/layer2_communi... | prototype | draft |
| 27 | src/zephyr/integration/layer2_communication/context_packa... | src/zephyr/integration/layer2_communi... | prototype | draft |
| 28 | src/zephyr/integration/layer2_communication/handoff_manag... | src/zephyr/integration/layer2_communi... | prototype | draft |
| 29 | src/zephyr/integration/layer2_communication/message_route... | src/zephyr/integration/layer2_communi... | prototype | draft |
| 30 | src/zephyr/integration/layer2_communication/push_notifier.py | src/zephyr/integration/layer2_communi... | prototype | draft |
| 31 | src/zephyr/integration/layer2_communication/streaming.py | src/zephyr/integration/layer2_communi... | prototype | draft |
| 32 | src/zephyr/integration/layer2_communication/trigger_monit... | src/zephyr/integration/layer2_communi... | prototype | draft |
| 33 | src/zephyr/integration/layer3_coordination/__init__.py | src/zephyr/integration/layer3_coordin... | prototype | draft |
| 34 | src/zephyr/integration/layer_consumer_registry.py | src/zephyr/integration/layer_consumer... | prototype | draft |
| 35 | src/zephyr/integration/layer_router.py | src/zephyr/integration/layer_router.py | prototype | draft |
| 36 | src/zephyr/integration/llm_bridge.py | src/zephyr/integration/llm_bridge.py | prototype | draft |
| 37 | src/zephyr/integration/llm_gateway.py | src/zephyr/integration/llm_gateway.py | prototype | draft |
| 38 | src/zephyr/integration/local_model/__init__.py | src/zephyr/integration/local_model/__... | prototype | draft |
| 39 | src/zephyr/integration/local_model/cache_layer.py | src/zephyr/integration/local_model/ca... | prototype | draft |
| 40 | src/zephyr/integration/local_model/embedding_router.py | src/zephyr/integration/local_model/em... | production | draft |
| 41 | src/zephyr/integration/local_model/local_model_scheduler.py | src/zephyr/integration/local_model/lo... | prototype | draft |
| 42 | src/zephyr/integration/local_model/ollama_chat.py | src/zephyr/integration/local_model/ol... | prototype | draft |
| 43 | src/zephyr/integration/local_model/ollama_embedding.py | src/zephyr/integration/local_model/ol... | prototype | draft |
| 44 | src/zephyr/integration/mcp/__init__.py | src/zephyr/integration/mcp/__init__.py | prototype | draft |
| 45 | src/zephyr/integration/mcp/_base_server.py | src/zephyr/integration/mcp/_base_serv... | prototype | draft |
| 46 | src/zephyr/integration/mcp/audit_logger.py | src/zephyr/integration/mcp/audit_logg... | prototype | draft |
| 47 | src/zephyr/integration/mcp/blueprint_search_server.py | src/zephyr/integration/mcp/blueprint_... | prototype | draft |
| 48 | src/zephyr/integration/mcp/doc_guard_server.py | src/zephyr/integration/mcp/doc_guard_... | prototype | draft |
| 49 | src/zephyr/integration/mcp/error_codes.py | src/zephyr/integration/mcp/error_code... | prototype | draft |
| 50 | src/zephyr/integration/mcp/gate_engine_server.py | src/zephyr/integration/mcp/gate_engin... | prototype | draft |
| 51 | src/zephyr/integration/mcp/gateway_server.py | src/zephyr/integration/mcp/gateway_se... | prototype | draft |
| 52 | src/zephyr/integration/mcp/handoff_auto_loader.py | src/zephyr/integration/mcp/handoff_au... | prototype | draft |
| 53 | src/zephyr/integration/mcp/knowledge_base_server.py | src/zephyr/integration/mcp/knowledge_... | prototype | draft |
| 54 | src/zephyr/integration/mcp/prompt_provider.py | src/zephyr/integration/mcp/prompt_pro... | prototype | draft |
| 55 | src/zephyr/integration/mcp/rate_limiter.py | src/zephyr/integration/mcp/rate_limit... | prototype | draft |
| 56 | src/zephyr/integration/mcp/resource_provider.py | src/zephyr/integration/mcp/resource_p... | prototype | draft |
| 57 | src/zephyr/integration/mcp/sandbox_server.py | src/zephyr/integration/mcp/sandbox_se... | prototype | draft |
| 58 | src/zephyr/integration/mcp/sentinel_server.py | src/zephyr/integration/mcp/sentinel_s... | prototype | draft |
| 59 | src/zephyr/integration/mcp/task_manager_server.py | src/zephyr/integration/mcp/task_manag... | prototype | draft |
| 60 | src/zephyr/integration/mcp/telemetry_server.py | src/zephyr/integration/mcp/telemetry_... | prototype | draft |
| 61 | src/zephyr/integration/mcp/tool_contracts.yaml | src/zephyr/integration/mcp/tool_contr... | production | orphan |
| 62 | src/zephyr/integration/mcp/vector_memory_server.py | src/zephyr/integration/mcp/vector_mem... | prototype | draft |
| 63 | src/zephyr/integration/mcp_server.py | src/zephyr/integration/mcp_server.py | prototype | draft |
| 64 | src/zephyr/integration/model_profiler/__init__.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 65 | src/zephyr/integration/model_profiler/benchmark_suite.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 66 | src/zephyr/integration/model_profiler/capability_passport.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 67 | src/zephyr/integration/model_profiler/cli.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 68 | src/zephyr/integration/model_profiler/deepseek_v4_chat.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 69 | src/zephyr/integration/model_profiler/exam_orchestrator.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 70 | src/zephyr/integration/model_profiler/exam_test_cases.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 71 | src/zephyr/integration/model_profiler/model_discovery.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 72 | src/zephyr/integration/model_profiler/profiler.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 73 | src/zephyr/integration/model_profiler/results_writer.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 74 | src/zephyr/integration/model_profiler/task_model_learner.py | src/zephyr/integration/model_profiler... | prototype | draft |
| 75 | src/zephyr/integration/model_router.py | src/zephyr/integration/model_router.py | prototype | draft |
| 76 | src/zephyr/integration/models.py | src/zephyr/integration/models.py | prototype | draft |
| 77 | src/zephyr/integration/models/__init__.py | src/zephyr/integration/models/__init_... | prototype | orphan |
| 78 | src/zephyr/integration/pipeline_agent_bridge.py | src/zephyr/integration/pipeline_agent... | prototype | draft |
| 79 | src/zephyr/integration/pipeline_lock.py | src/zephyr/integration/pipeline_lock.py | prototype | draft |
| 80 | src/zephyr/integration/pipeline_orchestrator.py | src/zephyr/integration/pipeline_orche... | prototype | draft |
| 81 | src/zephyr/integration/pipeline_roadmap.py | src/zephyr/integration/pipeline_roadm... | prototype | draft |
| 82 | src/zephyr/integration/ports.py | src/zephyr/integration/ports.py | prototype | draft |
| 83 | src/zephyr/integration/preemption_manager.py | src/zephyr/integration/preemption_man... | prototype | draft |
| 84 | src/zephyr/integration/routing_plugins.py | src/zephyr/integration/routing_plugin... | prototype | draft |
| 85 | src/zephyr/integration/services/__init__.py | src/zephyr/integration/services/__ini... | scaffold_placeholder | orphan |
| 86 | src/zephyr/integration/shared/api_03/__init__.py | src/zephyr/integration/shared/api_03/... | prototype | draft |
| 87 | src/zephyr/integration/shared/api_03/api_client.py | src/zephyr/integration/shared/api_03/... | prototype | draft |
| 88 | src/zephyr/integration/shared/api_03/api_index.py | src/zephyr/integration/shared/api_03/... | prototype | draft |
| 89 | src/zephyr/integration/shared/api_03/dos_launcher.py | src/zephyr/integration/shared/api_03/... | production | draft |
| 90 | src/zephyr/integration/shared/contracts/errors/__init__.py | src/zephyr/integration/shared/contrac... | prototype | draft |
| 91 | src/zephyr/integration/shared/contracts/errors/contract_v... | src/zephyr/integration/shared/contrac... | prototype | draft |
| 92 | src/zephyr/integration/shared/contracts/errors/data_quali... | src/zephyr/integration/shared/contrac... | prototype | draft |
| 93 | src/zephyr/integration/shared/contracts/errors/execution_... | src/zephyr/integration/shared/contrac... | prototype | draft |
| 94 | src/zephyr/integration/shared/contracts/errors/factor_com... | src/zephyr/integration/shared/contrac... | prototype | draft |
| 95 | src/zephyr/integration/shared/contracts/errors/risk_limit... | src/zephyr/integration/shared/contrac... | prototype | draft |
| 96 | src/zephyr/integration/shared/contracts/errors/signal_deg... | src/zephyr/integration/shared/contrac... | production | draft |
| 97 | src/zephyr/integration/shared/events/__init__.py | src/zephyr/integration/shared/events/... | prototype | draft |
| 98 | src/zephyr/integration/shared/events/dlq.py | src/zephyr/integration/shared/events/... | prototype | draft |
| 99 | src/zephyr/integration/shared/events/dlq_bridge.py | src/zephyr/integration/shared/events/... | prototype | draft |
| 100 | src/zephyr/integration/shared/events/event_bus_upgrade.py | src/zephyr/integration/shared/events/... | prototype | draft |
| 101 | src/zephyr/integration/shared/events/event_schemas.py | src/zephyr/integration/shared/events/... | prototype | draft |
| 102 | src/zephyr/integration/shared/events/upgrade_strategy.py | src/zephyr/integration/shared/events/... | production | draft |
| 103 | src/zephyr/integration/shared/schema/__init__.py | src/zephyr/integration/shared/schema/... | prototype | draft |
| 104 | src/zephyr/integration/shared/schema/base_config.py | src/zephyr/integration/shared/schema/... | production | draft |
| 105 | src/zephyr/integration/shared/schema/execution_model.py | src/zephyr/integration/shared/schema/... | production | draft |
| 106 | src/zephyr/integration/shared/schema/schema_registry.py | src/zephyr/integration/shared/schema/... | production | draft |
| 107 | src/zephyr/integration/shared/schema/schemas.py | src/zephyr/integration/shared/schema/... | production | draft |
| 108 | src/zephyr/integration/shared/schema/severity_types.py | src/zephyr/integration/shared/schema/... | production | draft |
| 109 | src/zephyr/integration/shared_08/__init__.py | src/zephyr/integration/shared_08/__in... | prototype | draft |
| 110 | src/zephyr/integration/shared_08/__version__.py | src/zephyr/integration/shared_08/__ve... | production | draft |
| 111 | src/zephyr/integration/shared_08/_contracts.py | src/zephyr/integration/shared_08/_con... | prototype | draft |
| 112 | src/zephyr/integration/shared_08/_infrastructure.py | src/zephyr/integration/shared_08/_inf... | prototype | draft |
| 113 | src/zephyr/integration/shared_08/_observability.py | src/zephyr/integration/shared_08/_obs... | prototype | draft |
| 114 | src/zephyr/integration/shared_08/_patterns.py | src/zephyr/integration/shared_08/_pat... | prototype | draft |
| 115 | src/zephyr/integration/shared_08/_version_and_types.py | src/zephyr/integration/shared_08/_ver... | prototype | draft |
| 116 | src/zephyr/integration/shared_08/agent_identity_impl.py | src/zephyr/integration/shared_08/agen... | prototype | draft |
| 117 | src/zephyr/integration/shared_08/api_client.py | src/zephyr/integration/shared_08/api_... | prototype | draft |
| 118 | src/zephyr/integration/shared_08/api_index.py | src/zephyr/integration/shared_08/api_... | prototype | draft |
| 119 | src/zephyr/integration/shared_08/blueprint_scorer.py | src/zephyr/integration/shared_08/blue... | prototype | draft |
| 120 | src/zephyr/integration/shared_08/cache.py | src/zephyr/integration/shared_08/cach... | prototype | draft |
| 121 | src/zephyr/integration/shared_08/capability.py | src/zephyr/integration/shared_08/capa... | prototype | draft |
| 122 | src/zephyr/integration/shared_08/constants.py | src/zephyr/integration/shared_08/cons... | prototype | draft |
| 123 | src/zephyr/integration/shared_08/content_fingerprint.py | src/zephyr/integration/shared_08/cont... | production | draft |
| 124 | src/zephyr/integration/shared_08/context.py | src/zephyr/integration/shared_08/cont... | production | draft |
| 125 | src/zephyr/integration/shared_08/contract_bus.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 126 | src/zephyr/integration/shared_08/contract_enforcer.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 127 | src/zephyr/integration/shared_08/contract_tester.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 128 | src/zephyr/integration/shared_08/contract_versions.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 129 | src/zephyr/integration/shared_08/contracts/__init__.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 130 | src/zephyr/integration/shared_08/contracts/approval_types.py | src/zephyr/integration/shared_08/cont... | production | draft |
| 131 | src/zephyr/integration/shared_08/contracts/backpressure/_... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 132 | src/zephyr/integration/shared_08/contracts/backpressure/p... | src/zephyr/integration/shared_08/cont... | production | draft |
| 133 | src/zephyr/integration/shared_08/contracts/backpressure/r... | src/zephyr/integration/shared_08/cont... | production | draft |
| 134 | src/zephyr/integration/shared_08/contracts/backpressure/t... | src/zephyr/integration/shared_08/cont... | production | draft |
| 135 | src/zephyr/integration/shared_08/contracts/capital_alloca... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 136 | src/zephyr/integration/shared_08/contracts/compliance_rul... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 137 | src/zephyr/integration/shared_08/contracts/core/__init__.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 138 | src/zephyr/integration/shared_08/contracts/core/base_even... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 139 | src/zephyr/integration/shared_08/contracts/core/enforcer.py | src/zephyr/integration/shared_08/cont... | production | draft |
| 140 | src/zephyr/integration/shared_08/contracts/core/gate_type... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 141 | src/zephyr/integration/shared_08/contracts/core/registry.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 142 | src/zephyr/integration/shared_08/contracts/core/runtime_p... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 143 | src/zephyr/integration/shared_08/contracts/core/system_co... | src/zephyr/integration/shared_08/cont... | production | draft |
| 144 | src/zephyr/integration/shared_08/contracts/core/telemetry... | src/zephyr/integration/shared_08/cont... | production | draft |
| 145 | src/zephyr/integration/shared_08/contracts/core/timestamp.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 146 | src/zephyr/integration/shared_08/contracts/core/trace_con... | src/zephyr/integration/shared_08/cont... | production | draft |
| 147 | src/zephyr/integration/shared_08/contracts/escalation/__i... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 148 | src/zephyr/integration/shared_08/contracts/escalation/bud... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 149 | src/zephyr/integration/shared_08/contracts/execution_repo... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 150 | src/zephyr/integration/shared_08/contracts/experiment/__i... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 151 | src/zephyr/integration/shared_08/contracts/experiment/exp... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 152 | src/zephyr/integration/shared_08/contracts/experiment/mod... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 153 | src/zephyr/integration/shared_08/contracts/experiment_res... | src/zephyr/integration/shared_08/cont... | production | draft |
| 154 | src/zephyr/integration/shared_08/contracts/external/__ini... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 155 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 156 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 157 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 158 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 159 | src/zephyr/integration/shared_08/contracts/factor_monitor... | src/zephyr/integration/shared_08/cont... | production | draft |
| 160 | src/zephyr/integration/shared_08/contracts/factor_signal.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 161 | src/zephyr/integration/shared_08/contracts/fill.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 162 | src/zephyr/integration/shared_08/contracts/gate/__init__.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 163 | src/zephyr/integration/shared_08/contracts/gate/gate_resu... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 164 | src/zephyr/integration/shared_08/contracts/identity/__ini... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 165 | src/zephyr/integration/shared_08/contracts/identity/agent... | src/zephyr/integration/shared_08/cont... | production | draft |
| 166 | src/zephyr/integration/shared_08/contracts/identity/permi... | src/zephyr/integration/shared_08/cont... | production | draft |
| 167 | src/zephyr/integration/shared_08/contracts/macro_factor_s... | src/zephyr/integration/shared_08/cont... | production | draft |
| 168 | src/zephyr/integration/shared_08/contracts/market_data.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 169 | src/zephyr/integration/shared_08/contracts/model_serving_... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 170 | src/zephyr/integration/shared_08/contracts/model_serving_... | src/zephyr/integration/shared_08/cont... | production | draft |
| 171 | src/zephyr/integration/shared_08/contracts/order.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 172 | src/zephyr/integration/shared_08/contracts/performance_at... | src/zephyr/integration/shared_08/cont... | production | draft |
| 173 | src/zephyr/integration/shared_08/contracts/position.py | src/zephyr/integration/shared_08/cont... | production | draft |
| 174 | src/zephyr/integration/shared_08/contracts/protocols.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 175 | src/zephyr/integration/shared_08/contracts/risk_dashboard... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 176 | src/zephyr/integration/shared_08/contracts/risk_limits.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 177 | src/zephyr/integration/shared_08/contracts/risk_metrics.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 178 | src/zephyr/integration/shared_08/contracts/rollback_types.py | src/zephyr/integration/shared_08/cont... | production | draft |
| 179 | src/zephyr/integration/shared_08/contracts/runtime_types.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 180 | src/zephyr/integration/shared_08/contracts/security/__ini... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 181 | src/zephyr/integration/shared_08/contracts/security/secur... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 182 | src/zephyr/integration/shared_08/contracts/strategy_lifec... | src/zephyr/integration/shared_08/cont... | production | draft |
| 183 | src/zephyr/integration/shared_08/contracts/synthesized_si... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 184 | src/zephyr/integration/shared_08/contracts/sys_master_com... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 185 | src/zephyr/integration/shared_08/contracts/system_configu... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 186 | src/zephyr/integration/shared_08/contracts/telemetry_emit... | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 187 | src/zephyr/integration/shared_08/contracts/trace_context.py | src/zephyr/integration/shared_08/cont... | prototype | draft |
| 188 | src/zephyr/integration/shared_08/deprecation.py | src/zephyr/integration/shared_08/depr... | production | draft |
| 189 | src/zephyr/integration/shared_08/diff_utils.py | src/zephyr/integration/shared_08/diff... | production | draft |
| 190 | src/zephyr/integration/shared_08/durable_execution.py | src/zephyr/integration/shared_08/dura... | production | draft |
| 191 | src/zephyr/integration/shared_08/env.py | src/zephyr/integration/shared_08/env.py | prototype | draft |
| 192 | src/zephyr/integration/shared_08/errors.py | src/zephyr/integration/shared_08/erro... | production | draft |
| 193 | src/zephyr/integration/shared_08/evals.py | src/zephyr/integration/shared_08/eval... | production | draft |
| 194 | src/zephyr/integration/shared_08/event_bus.py | src/zephyr/integration/shared_08/even... | production | stable |
| 195 | src/zephyr/integration/shared_08/file_utils.py | src/zephyr/integration/shared_08/file... | production | draft |
| 196 | src/zephyr/integration/shared_08/flags.py | src/zephyr/integration/shared_08/flag... | production | draft |
| 197 | src/zephyr/integration/shared_08/foundation/__init__.py | src/zephyr/integration/shared_08/foun... | production | draft |
| 198 | src/zephyr/integration/shared_08/foundation/constants.py | src/zephyr/integration/shared_08/foun... | prototype | draft |
| 199 | src/zephyr/integration/shared_08/foundation/deprecation.py | src/zephyr/integration/shared_08/foun... | prototype | draft |
| 200 | src/zephyr/integration/shared_08/foundation/env.py | src/zephyr/integration/shared_08/foun... | prototype | draft |

> (仅显示前 200 个模块，共 304 个)

### 未分类 / Unclassified (402 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-INTEGRATION/6-Month Data Retention 6个月数据保留 | 6-Month Data Retention 6个月数据保留 | design | design_only |
| 2 | D-INTEGRATION/A2A + MCP Dual Protocol A2A+MCP双协议 | A2A + MCP Dual Protocol A2A+MCP双协议 | design | design_only |
| 3 | D-INTEGRATION/A2A MCP Hybrid Orchestration A2A+MCP混合编排 | A2A MCP Hybrid Orchestration A2A+MCP... | design | design_only |
| 4 | D-INTEGRATION/A2A Message Encryption A2A消息加密 | A2A Message Encryption A2A消息加密 | design | design_only |
| 5 | D-INTEGRATION/A2A Protocol Bridge A2A协议桥接 | A2A Protocol Bridge A2A协议桥接 | design | design_only |
| 6 | D-INTEGRATION/A2A Protocol Handler A2A协议处理器 | A2A Protocol Handler A2A协议处理器 | design | design_only |
| 7 | D-INTEGRATION/A2A Protocol Integration A2A协议集成 | A2A Protocol Integration A2A协议集成 | design | design_only |
| 8 | D-INTEGRATION/A2AProtocolBridge A2A协议桥 | A2AProtocolBridge A2A协议桥 | design | design_only |
| 9 | D-INTEGRATION/ACL Anti-Corruption Layer ACL防腐层 | ACL Anti-Corruption Layer ACL防腐层 | design | design_only |
| 10 | D-INTEGRATION/AI Gateway AI网关 | AI Gateway AI网关 | design | design_only |
| 11 | D-INTEGRATION/AI Security Boundary Execution Layer AI安全... | AI Security Boundary Execution Layer ... | design | design_only |
| 12 | D-INTEGRATION/AI Track AI轨 | AI Track AI轨 | design | design_only |
| 13 | D-INTEGRATION/API Fuzz Testing API模糊测试 | API Fuzz Testing API模糊测试 | design | design_only |
| 14 | D-INTEGRATION/API Gateway API网关 | API Gateway API网关 | design | design_only |
| 15 | D-INTEGRATION/API Gateway Design API网关设计 | API Gateway Design API网关设计 | design | design_only |
| 16 | D-INTEGRATION/API Gateway Four Layer Architecture API网关... | API Gateway Four Layer Architecture A... | design | design_only |
| 17 | D-INTEGRATION/API Gateway Layer API网关层 | API Gateway Layer API网关层 | design | design_only |
| 18 | D-INTEGRATION/API Gateway Unified Entry API网关统一入口 | API Gateway Unified Entry API网关统一... | design | design_only |
| 19 | D-INTEGRATION/API Key 90-Day Auto Rotation API密钥90天自... | API Key 90-Day Auto Rotation API密钥9... | design | design_only |
| 20 | D-INTEGRATION/API Key 90-Day Rotation API密钥90天轮换 | API Key 90-Day Rotation API密钥90天轮换 | design | design_only |
| 21 | D-INTEGRATION/API Key Encrypted Storage API密钥加密存储 | API Key Encrypted Storage API密钥加密... | design | design_only |
| 22 | D-INTEGRATION/API Lifecycle API生命周期 | API Lifecycle API生命周期 | design | design_only |
| 23 | D-INTEGRATION/API Record Replay VCR API录制回放 | API Record Replay VCR API录制回放 | design | design_only |
| 24 | D-INTEGRATION/API Routing Service Discovery API路由与服务... | API Routing Service Discovery API路由... | design | design_only |
| 25 | D-INTEGRATION/API Version Hard Constraint API版本管理硬约束 | API Version Hard Constraint API版本管... | design | design_only |
| 26 | D-INTEGRATION/API Version Mismatch Reject API版本不匹配拒绝 | API Version Mismatch Reject API版本不... | design | design_only |
| 27 | D-INTEGRATION/APIDocumentation API文档 | APIDocumentation API文档 | design | design_only |
| 28 | D-INTEGRATION/APIGatewayRequestRouted API网关请求路由 | APIGatewayRequestRouted API网关请求路由 | design | design_only |
| 29 | D-INTEGRATION/Adapter Auto-Discovery 适配器自动发现 | Adapter Auto-Discovery 适配器自动发现 | design | design_only |
| 30 | D-INTEGRATION/Adapter Baseline Snapshot 适配器基线快照 | Adapter Baseline Snapshot 适配器基线快照 | design | design_only |
| 31 | D-INTEGRATION/Adapter Manager 适配器管理器 | Adapter Manager 适配器管理器 | design | design_only |
| 32 | D-INTEGRATION/Additive Change 非破坏性变更 | Additive Change 非破坏性变更 | design | design_only |
| 33 | D-INTEGRATION/Agent Card Discovery Agent Card发现机制 | Agent Card Discovery Agent Card发现机制 | design | design_only |
| 34 | D-INTEGRATION/AgentAction Agent动作事件 | AgentAction Agent动作事件 | design | design_only |
| 35 | D-INTEGRATION/AkShare Crawler AkShare爬虫 | AkShare Crawler AkShare爬虫 | design | design_only |
| 36 | D-INTEGRATION/AkShare HTTP Crawler 另类数据源 | AkShare HTTP Crawler 另类数据源 | design | design_only |
| 37 | D-INTEGRATION/Architecture Governance Integration 架构治... | Architecture Governance Integration ... | design | design_only |
| 38 | D-INTEGRATION/Architecture as Code Integration 架构即代码... | Architecture as Code Integration 架构... | design | design_only |
| 39 | D-INTEGRATION/Artifact Exchange Artifact交换 | Artifact Exchange Artifact交换 | design | design_only |
| 40 | D-INTEGRATION/Asynchronous Messaging 异步消息 | Asynchronous Messaging 异步消息 | design | design_only |
| 41 | D-INTEGRATION/Audit Layer 审计层 | Audit Layer 审计层 | design | design_only |
| 42 | D-INTEGRATION/Audit Log Required 审计日志必须 | Audit Log Required 审计日志必须 | design | design_only |
| 43 | D-INTEGRATION/Authentication Layer 认证层 | Authentication Layer 认证层 | design | design_only |
| 44 | D-INTEGRATION/Auto Integration Registry 自动集成注册表 | Auto Integration Registry 自动集成注册表 | design | design_only |
| 45 | D-INTEGRATION/Auto-Scaling Integration 自动扩缩集成 | Auto-Scaling Integration 自动扩缩集成 | design | design_only |
| 46 | D-INTEGRATION/AutoScaling 自动扩缩容 | AutoScaling 自动扩缩容 | design | design_only |
| 47 | D-INTEGRATION/Backpressure Contract 001 背压契约001 | Backpressure Contract 001 背压契约001 | design | design_only |
| 48 | D-INTEGRATION/Backpressure Contract 002 背压契约002 | Backpressure Contract 002 背压契约002 | design | design_only |
| 49 | D-INTEGRATION/Backpressure Contract 003 背压契约003 | Backpressure Contract 003 背压契约003 | design | design_only |
| 50 | D-INTEGRATION/BackpressureManager 背压管理器 | BackpressureManager 背压管理器 | design | design_only |
| 51 | D-INTEGRATION/Baseline Snapshot Persistence 基线快照持久化 | Baseline Snapshot Persistence 基线快... | design | design_only |
| 52 | D-INTEGRATION/Batch Import 批量导入 | Batch Import 批量导入 | design | design_only |
| 53 | D-INTEGRATION/Behavioral Admission Integration 行为准入门... | Behavioral Admission Integration 行为... | design | design_only |
| 54 | D-INTEGRATION/Blueprint-Architecture Bidirectional Mappin... | Blueprint-Architecture Bidirectional ... | design | design_only |
| 55 | D-INTEGRATION/Breaking Change 破坏性变更 | Breaking Change 破坏性变更 | design | design_only |
| 56 | D-INTEGRATION/Bulkhead Isolation Pool 舱壁隔离池 | Bulkhead Isolation Pool 舱壁隔离池 | design | design_only |
| 57 | D-INTEGRATION/Bulkhead Isolation 舱壁隔离 | Bulkhead Isolation 舱壁隔离 | design | design_only |
| 58 | D-INTEGRATION/CI/CDIntegration CI/CD集成 | CI/CDIntegration CI/CD集成 | design | design_only |
| 59 | D-INTEGRATION/CLOSED 正常状态 | CLOSED 正常状态 | design | design_only |
| 60 | D-INTEGRATION/CQRS Separation CQRS分离 | CQRS Separation CQRS分离 | design | design_only |
| 61 | D-INTEGRATION/Capital Flow Behavior Analysis 资金行为分析 | Capital Flow Behavior Analysis 资金行... | design | design_only |
| 62 | D-INTEGRATION/Chaos Engineering Environment 混沌工程环境选择 | Chaos Engineering Environment 混沌工... | design | design_only |
| 63 | D-INTEGRATION/Circuit Breaker + Bulkhead 熔断器+舱壁隔离 | Circuit Breaker + Bulkhead 熔断器+舱... | design | design_only |
| 64 | D-INTEGRATION/Circuit Breaker Layer 熔断层 | Circuit Breaker Layer 熔断层 | design | design_only |
| 65 | D-INTEGRATION/Circuit Breaker Matrix 熔断器矩阵 | Circuit Breaker Matrix 熔断器矩阵 | design | design_only |
| 66 | D-INTEGRATION/Circuit Breaker State Export 熔断器状态导出 | Circuit Breaker State Export 熔断器状... | design | design_only |
| 67 | D-INTEGRATION/Circuit Breaker State 熔断器状态 | Circuit Breaker State 熔断器状态 | design | design_only |
| 68 | D-INTEGRATION/Claude API 克劳德API | Claude API 克劳德API | design | design_only |
| 69 | D-INTEGRATION/Client MCP客户端 | Client MCP客户端 | design | design_only |
| 70 | D-INTEGRATION/Closed Loop Manual Approval 闭环优化人工审批 | Closed Loop Manual Approval 闭环优化... | design | design_only |
| 71 | D-INTEGRATION/Closed State Retry Closed状态重试 | Closed State Retry Closed状态重试 | design | design_only |
| 72 | D-INTEGRATION/Cloud Backup Desensitization 云端冷备脱敏 | Cloud Backup Desensitization 云端冷备... | design | design_only |
| 73 | D-INTEGRATION/Compliance Gateway Embedded 合规网关嵌入 | Compliance Gateway Embedded 合规网关嵌入 | design | design_only |
| 74 | D-INTEGRATION/Compliance Gateway Layer 合规网关层 | Compliance Gateway Layer 合规网关层 | design | design_only |
| 75 | D-INTEGRATION/Compliance Policy Integration 合规策略集成 | Compliance Policy Integration 合规策... | design | design_only |
| 76 | D-INTEGRATION/Component Reuse Manager 组件复用管理器 | Component Reuse Manager 组件复用管理器 | design | design_only |
| 77 | D-INTEGRATION/Config Git Versioning 配置Git版本化 | Config Git Versioning 配置Git版本化 | design | design_only |
| 78 | D-INTEGRATION/ConfigChanged 配置变更 | ConfigChanged 配置变更 | design | design_only |
| 79 | D-INTEGRATION/Consumer-Driven Contract Testing 消费者驱动... | Consumer-Driven Contract Testing 消费... | design | design_only |
| 80 | D-INTEGRATION/Contract Baseline Update 契约基线更新 | Contract Baseline Update 契约基线更新 | design | design_only |
| 81 | D-INTEGRATION/Contract Drift 契约漂移 | Contract Drift 契约漂移 | design | design_only |
| 82 | D-INTEGRATION/Contract Layer 契约层 | Contract Layer 契约层 | design | design_only |
| 83 | D-INTEGRATION/Contract Registry Version Query 契约注册表... | Contract Registry Version Query 契约... | design | design_only |
| 84 | D-INTEGRATION/Contract Registry 契约注册表 | Contract Registry 契约注册表 | design | design_only |
| 85 | D-INTEGRATION/Contract Test Block Deploy 契约测试阻断部署 | Contract Test Block Deploy 契约测试阻... | design | design_only |
| 86 | D-INTEGRATION/Contract Test Coverage 契约测试覆盖 | Contract Test Coverage 契约测试覆盖 | design | design_only |
| 87 | D-INTEGRATION/Contract Test Deploy Block 契约测试阻断部署 | Contract Test Deploy Block 契约测试阻... | design | design_only |
| 88 | D-INTEGRATION/ContractFrozen 契约冻结 | ContractFrozen 契约冻结 | design | design_only |
| 89 | D-INTEGRATION/ContractVersionManager 契约版本管理器 | ContractVersionManager 契约版本管理器 | design | design_only |
| 90 | D-INTEGRATION/ContractViolated 契约违反事件 | ContractViolated 契约违反事件 | design | design_only |
| 91 | D-INTEGRATION/ContractViolationError 契约违反错误 | ContractViolationError 契约违反错误 | design | design_only |
| 92 | D-INTEGRATION/Cost-Aware LLM Routing 成本感知LLM路由 | Cost-Aware LLM Routing 成本感知LLM路由 | design | design_only |
| 93 | D-INTEGRATION/Cross-Market Data Integrator 跨市场数据集成器 | Cross-Market Data Integrator 跨市场数... | design | design_only |
| 94 | D-INTEGRATION/D-INT-36 ArchitectureAsCode 架构即代码 | D-INT-36 ArchitectureAsCode 架构即代码 | design | design_only |
| 95 | D-INTEGRATION/D-INTEGRATION 集成 | D-INTEGRATION 集成 | design | design_only |
| 96 | D-INTEGRATION/Daily Mode 日频模式 | Daily Mode 日频模式 | design | design_only |
| 97 | D-INTEGRATION/Data Consistency Guarantee 数据一致性保证 | Data Consistency Guarantee 数据一致性... | design | design_only |
| 98 | D-INTEGRATION/Data Desensitization 数据脱敏 | Data Desensitization 数据脱敏 | design | design_only |
| 99 | D-INTEGRATION/Data Fetch Pool 数据拉取池 | Data Fetch Pool 数据拉取池 | design | design_only |
| 100 | D-INTEGRATION/Data Format Transformer 数据格式转换器 | Data Format Transformer 数据格式转换器 | design | design_only |
| 101 | D-INTEGRATION/Data Freshness Grading 数据新鲜度分级 | Data Freshness Grading 数据新鲜度分级 | design | design_only |
| 102 | D-INTEGRATION/Data Source Failure Degradation 数据源故障降级 | Data Source Failure Degradation 数据... | design | design_only |
| 103 | D-INTEGRATION/Data Source Manager 数据源管理器 | Data Source Manager 数据源管理器 | design | design_only |
| 104 | D-INTEGRATION/Data Source Router 数据源路由 | Data Source Router 数据源路由 | design | design_only |
| 105 | D-INTEGRATION/Data Track 数据轨 | Data Track 数据轨 | design | design_only |
| 106 | D-INTEGRATION/DataSourceConnectorRegistry 数据源连接器注... | DataSourceConnectorRegistry 数据源连... | design | design_only |
| 107 | D-INTEGRATION/DeepSeek V4 Pro API 深度求索API | DeepSeek V4 Pro API 深度求索API | design | design_only |
| 108 | D-INTEGRATION/DepMap Integration DepMap集成 | DepMap Integration DepMap集成 | design | design_only |
| 109 | D-INTEGRATION/Dependency Semantics Integration 依赖语义集成 | Dependency Semantics Integration 依赖... | design | design_only |
| 110 | D-INTEGRATION/Deprecating Change Deprecating变更 | Deprecating Change Deprecating变更 | design | design_only |
| 111 | D-INTEGRATION/Desensitization Layer 脱敏层 | Desensitization Layer 脱敏层 | design | design_only |
| 112 | D-INTEGRATION/Disaster Recovery State Reconstructability ... | Disaster Recovery State Reconstructab... | design | design_only |
| 113 | D-INTEGRATION/Distributed Tracing OTel 分布式追踪OTel | Distributed Tracing OTel 分布式追踪OTel | design | design_only |
| 114 | D-INTEGRATION/DistributedTracePropagator 分布式追踪传播器 | DistributedTracePropagator 分布式追踪... | design | design_only |
| 115 | D-INTEGRATION/Dual Version Transition 双版本过渡期 | Dual Version Transition 双版本过渡期 | design | design_only |
| 116 | D-INTEGRATION/E-0119 前端域→集成域依赖 | E-0119 前端域→集成域依赖 | design | design_only |
| 117 | D-INTEGRATION/Email System 邮件系统 | Email System 邮件系统 | design | design_only |
| 118 | D-INTEGRATION/Error Budget 误差预算 | Error Budget 误差预算 | design | design_only |
| 119 | D-INTEGRATION/Event Bus Manager 事件总线 | Event Bus Manager 事件总线 | design | design_only |
| 120 | D-INTEGRATION/Event Sourcing 事件驱动+Event Sourcing | Event Sourcing 事件驱动+Event Sourcing | design | design_only |
| 121 | D-INTEGRATION/Event-Driven 事件驱动 | Event-Driven 事件驱动 | design | design_only |
| 122 | D-INTEGRATION/EventBusManager 事件总线管理器 | EventBusManager 事件总线管理器 | design | design_only |
| 123 | D-INTEGRATION/EventRoutingFailed 事件路由失败事件 | EventRoutingFailed 事件路由失败事件 | design | design_only |
| 124 | D-INTEGRATION/External API Metrics 外部API调用指标 | External API Metrics 外部API调用指标 | design | design_only |
| 125 | D-INTEGRATION/External API No Position Data 外部API禁止传... | External API No Position Data 外部API... | design | design_only |
| 126 | D-INTEGRATION/External API Response Validation 外部API响... | External API Response Validation 外部... | design | design_only |
| 127 | D-INTEGRATION/External API Unified Gateway 外部API统一网关 | External API Unified Gateway 外部API... | design | design_only |
| 128 | D-INTEGRATION/External System Adapter 外部系统适配器 | External System Adapter 外部系统适配器 | design | design_only |
| 129 | D-INTEGRATION/External System Connector 外部系统连接器 | External System Connector 外部系统连接器 | design | design_only |
| 130 | D-INTEGRATION/External System Interaction Matrix 外部系统... | External System Interaction Matrix 外... | design | design_only |
| 131 | D-INTEGRATION/External System Isolation 外部系统故障隔离 | External System Isolation 外部系统故... | design | design_only |
| 132 | D-INTEGRATION/External System Layer 外部系统层 | External System Layer 外部系统层 | design | design_only |
| 133 | D-INTEGRATION/ExternalAPIAccess 外部API访问 | ExternalAPIAccess 外部API访问 | design | design_only |
| 134 | D-INTEGRATION/ExternalAPIEndpoint 外部API端点 | ExternalAPIEndpoint 外部API端点 | design | design_only |
| 135 | D-INTEGRATION/Factor Calculation MCP Server 因子计算MCP服... | Factor Calculation MCP Server 因子计... | design | design_only |
| 136 | D-INTEGRATION/Fault Injection Test 故障注入测试 | Fault Injection Test 故障注入测试 | design | design_only |
| 137 | D-INTEGRATION/Feature Flag Progressive Integration 功能开... | Feature Flag Progressive Integration ... | design | design_only |
| 138 | D-INTEGRATION/FeatureFlagManager 功能开关管理器 | FeatureFlagManager 功能开关管理器 | design | design_only |
| 139 | D-INTEGRATION/Four-Level Rate Limiting 四级限流架构 | Four-Level Rate Limiting 四级限流架构 | design | design_only |
| 140 | D-INTEGRATION/Full Contract Test on Change 变更触发全量契... | Full Contract Test on Change 变更触发... | design | design_only |
| 141 | D-INTEGRATION/Full Sync After Recovery 灾备恢复全量同步 | Full Sync After Recovery 灾备恢复全量... | design | design_only |
| 142 | D-INTEGRATION/Git Local Repository Git本地仓库 | Git Local Repository Git本地仓库 | design | design_only |
| 143 | D-INTEGRATION/Google A2A Protocol Google A2A协议 | Google A2A Protocol Google A2A协议 | design | design_only |
| 144 | D-INTEGRATION/HALF_OPEN 半开试探状态 | HALF_OPEN 半开试探状态 | design | design_only |
| 145 | D-INTEGRATION/Host MCP主机进程 | Host MCP主机进程 | design | design_only |
| 146 | D-INTEGRATION/IA-02 iFind个人版数据字段覆盖度假设 | IA-02 iFind个人版数据字段覆盖度假设 | design | design_only |
| 147 | D-INTEGRATION/IA-03 iFind QPS上限维持20假设 | IA-03 iFind QPS上限维持20假设 | design | design_only |
| 148 | D-INTEGRATION/IA-04 RTX 3090显存24GB足够假设 | IA-04 RTX 3090显存24GB足够假设 | design | design_only |
| 149 | D-INTEGRATION/IA-05 外部LLM API服务商持续运营假设 | IA-05 外部LLM API服务商持续运营假设 | design | design_only |
| 150 | D-INTEGRATION/IA-06 微信Webhook接口不发生破坏性变更假设 | IA-06 微信Webhook接口不发生破坏性变更... | design | design_only |
| 151 | D-INTEGRATION/IA-07 Windows操作系统兼容性维持假设 | IA-07 Windows操作系统兼容性维持假设 | design | design_only |
| 152 | D-INTEGRATION/IA-08 家用网络30Mbps带宽足够假设 | IA-08 家用网络30Mbps带宽足够假设 | design | design_only |
| 153 | D-INTEGRATION/IA-09 MCP 2026-07-28规范无重大破坏性变更假设 | IA-09 MCP 2026-07-28规范无重大破坏性... | design | design_only |
| 154 | D-INTEGRATION/IA-10 AkShare反爬策略不升级到完全封禁假设 | IA-10 AkShare反爬策略不升级到完全封禁... | design | design_only |
| 155 | D-INTEGRATION/IA-11 证监会CN-003程序化交易细则不发生重大... | IA-11 证监会CN-003程序化交易细则不发... | design | design_only |
| 156 | D-INTEGRATION/IA-12 Google A2A协议规范不发生破坏性变更假设 | IA-12 Google A2A协议规范不发生破坏性... | design | design_only |
| 157 | D-INTEGRATION/IA-13 GitHub私有仓库持续可用且免费额度足够假设 | IA-13 GitHub私有仓库持续可用且免费额... | design | design_only |
| 158 | D-INTEGRATION/Idempotency Key Required 幂等Key必须 | Idempotency Key Required 幂等Key必须 | design | design_only |
| 159 | D-INTEGRATION/Idempotency Key Value Object 幂等Key值对象 | Idempotency Key Value Object 幂等Key... | design | design_only |
| 160 | D-INTEGRATION/Idempotency Key 幂等Key | Idempotency Key 幂等Key | design | design_only |
| 161 | D-INTEGRATION/IdempotencyKeyInterceptor 幂等Key拦截器 | IdempotencyKeyInterceptor 幂等Key拦截器 | design | design_only |
| 162 | D-INTEGRATION/IdempotencyKeyMissing 幂等Key缺失 | IdempotencyKeyMissing 幂等Key缺失 | design | design_only |
| 163 | D-INTEGRATION/Independent Integration Architecture 独立集... | Independent Integration Architecture ... | design | design_only |
| 164 | D-INTEGRATION/Integration Capacity Planning 集成容量规划... | Integration Capacity Planning 集成容... | design | design_only |
| 165 | D-INTEGRATION/Integration Closed Loop Optimization 集成闭... | Integration Closed Loop Optimization ... | design | design_only |
| 166 | D-INTEGRATION/Integration Closed Loop Optimization 集成闭... | Integration Closed Loop Optimization ... | design | design_only |
| 167 | D-INTEGRATION/Integration Compliance Governance 集成合规治理 | Integration Compliance Governance 集... | design | design_only |
| 168 | D-INTEGRATION/Integration Config Damage 集成配置损坏 | Integration Config Damage 集成配置损坏 | design | design_only |
| 169 | D-INTEGRATION/Integration Config GitOps 集成配置GitOps | Integration Config GitOps 集成配置GitOps | design | design_only |
| 170 | D-INTEGRATION/Integration Config Manager 集成配置管理器 | Integration Config Manager 集成配置管... | design | design_only |
| 171 | D-INTEGRATION/Integration Contract 集成契约 | Integration Contract 集成契约 | design | design_only |
| 172 | D-INTEGRATION/Integration Disaster Recovery 集成层灾备 | Integration Disaster Recovery 集成层灾备 | design | design_only |
| 173 | D-INTEGRATION/Integration Legacy Issue Decision 集成遗留... | Integration Legacy Issue Decision 集... | design | design_only |
| 174 | D-INTEGRATION/Integration Observability 集成可观测性 | Integration Observability 集成可观测性 | design | design_only |
| 175 | D-INTEGRATION/Integration Security Defense 集成安全纵深 | Integration Security Defense 集成安全... | design | design_only |
| 176 | D-INTEGRATION/Integration Smoke Test 集成冒烟测试 | Integration Smoke Test 集成冒烟测试 | design | design_only |
| 177 | D-INTEGRATION/Integration Style 集成风格 | Integration Style 集成风格 | design | design_only |
| 178 | D-INTEGRATION/Integration Test Framework 集成测试框架 | Integration Test Framework 集成测试框架 | design | design_only |
| 179 | D-INTEGRATION/Integration Test Strategy 集成测试策略 | Integration Test Strategy 集成测试策略 | design | design_only |
| 180 | D-INTEGRATION/IntegrationHealthMonitor 集成健康监控 | IntegrationHealthMonitor 集成健康监控 | design | design_only |
| 181 | D-INTEGRATION/IntegrationTester 集成测试器 | IntegrationTester 集成测试器 | design | design_only |
| 182 | D-INTEGRATION/Interface Contract Governance 接口契约治理 | Interface Contract Governance 接口契... | design | design_only |
| 183 | D-INTEGRATION/Internal Consumer Layer 内部消费层 | Internal Consumer Layer 内部消费层 | design | design_only |
| 184 | D-INTEGRATION/Isolation Layer 隔离层 | Isolation Layer 隔离层 | design | design_only |
| 185 | D-INTEGRATION/Isolation Manager 隔离管理器 | Isolation Manager 隔离管理器 | design | design_only |
| 186 | D-INTEGRATION/Isolation Policy Bypass Prevent 隔离策略不... | Isolation Policy Bypass Prevent 隔离... | design | design_only |
| 187 | D-INTEGRATION/Isolation Strategy 隔离策略 | Isolation Strategy 隔离策略 | design | design_only |
| 188 | D-INTEGRATION/KS-L4 Reduced Operation KS-L4降额运行1天 | KS-L4 Reduced Operation KS-L4降额运行1天 | design | design_only |
| 189 | D-INTEGRATION/Key 90-Day Rotation 密钥90天轮换 | Key 90-Day Rotation 密钥90天轮换 | design | design_only |
| 190 | D-INTEGRATION/Kill-Switch Four-Level Cascade Kill-Switch... | Kill-Switch Four-Level Cascade Kill-S... | design | design_only |
| 191 | D-INTEGRATION/Kill-Switch 紧急停机机制 | Kill-Switch 紧急停机机制 | design | design_only |
| 192 | D-INTEGRATION/Knowledge Graph MCP Server 知识图谱MCP服务器 | Knowledge Graph MCP Server 知识图谱MC... | design | design_only |
| 193 | D-INTEGRATION/L0 Normal L0正常 | L0 Normal L0正常 | design | design_only |
| 194 | D-INTEGRATION/L00 Data Source Blueprint L00数据源蓝图 | L00 Data Source Blueprint L00数据源蓝图 | design | design_only |
| 195 | D-INTEGRATION/L1 Contract Layer L1契约层 | L1 Contract Layer L1契约层 | design | design_only |
| 196 | D-INTEGRATION/L1 Mild Degradation L1轻度降级 | L1 Mild Degradation L1轻度降级 | design | design_only |
| 197 | D-INTEGRATION/L2 Mock Layer L2模拟层 | L2 Mock Layer L2模拟层 | design | design_only |
| 198 | D-INTEGRATION/L2 Moderate Degradation L2中度降级 | L2 Moderate Degradation L2中度降级 | design | design_only |
| 199 | D-INTEGRATION/L3 Real Layer L3真实层 | L3 Real Layer L3真实层 | design | design_only |
| 200 | D-INTEGRATION/L3 Severe Degradation L3重度降级 | L3 Severe Degradation L3重度降级 | design | design_only |

> (仅显示前 200 个模块，共 402 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 730 条 / 730 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 730 条 / 730 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 527 条 / edges                               │
│   [config_depends]: 78 条 / edges                                │
│   [contract]: 70 条 / edges                                      │
│   [runtime]: 30 条 / edges                                       │
│   [event]: 21 条 / edges                                         │
│   [data]: 4 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (527 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   backpressure_types.py → trace_context.py                       │
│   circuit_breaker_manager.py → __init__.py                       │
│   backpressure_manager.py → __init__.py                          │
│   cost_tracker.py → __init__.py                                  │
│   ct_pipe_routing.py → __init__.py                               │
│   ct_pipe_routing.py → schemas.py                                │
│   dead_letter_queue.py → __init__.py                             │
│   models.py → schemas.py                                         │
│   layer_consumer_registry.py → __init__.py                       │
│   pipeline_agent_bridge.py → __init__.py                         │
│   pipeline_orchestrator.py → __init__.py                         │
│   pipeline_orchestrator.py → embedding_router.py                 │
│   pipeline_orchestrator.py → local_model_scheduler.py            │
│   pipeline_orchestrator.py → protocols.py                        │
│   preemption_manager.py → __init__.py                            │
│   routing_plugins.py → __init__.py                               │
│   model_serving_response.py → model_serving_response.py          │
│   experiment_result.py → experiment_result.py                    │
│   __init__.py → a2a_registry.py                                  │
│   __init__.py → identity_verifier.py                             │
│   __init__.py → a2a_state.py                                     │
│   __init__.py → message_router.py                                │
│   __init__.py → a2a_schemas.py                                   │
│   __init__.py → handoff_manager.py                               │
│   __init__.py → trigger_monitor.py                               │
│   __init__.py → push_notifier.py                                 │
│   __init__.py → streaming.py                                     │
│   embedding_router.py → ollama_embedding.py                      │
│   local_model_scheduler.py → embedding_router.py                 │
│   local_model_scheduler.py → ollama_chat.py                      │
│   local_model_scheduler.py → resource_optimization_eng...        │
│   blueprint_search_server.py → _base_server.py                   │
│   __init__.py → cache_layer.py                                   │
│   __init__.py → embedding_router.py                              │
│   __init__.py → ollama_chat.py                                   │
│   __init__.py → local_model_scheduler.py                         │
│   __init__.py → ollama_embedding.py                              │
│   doc_guard_server.py → _base_server.py                          │
│   gateway_server.py → blueprint_search_server.py                 │
│   gateway_server.py → audit_logger.py                            │
│   gateway_server.py → error_codes.py                             │
│   gateway_server.py → doc_guard_server.py                        │
│   gateway_server.py → gate_engine_server.py                      │
│   gateway_server.py → knowledge_base_server.py                   │
│   gateway_server.py → rate_limiter.py                            │
│   gateway_server.py → sentinel_server.py                         │
│   gateway_server.py → task_manager_server.py                     │
│   gateway_server.py → telemetry_server.py                        │
│   gateway_server.py → _base_server.py                            │
│   ...还有 478 条 / 478 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (78 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (70 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (30 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (21 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (4 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 730 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `11_d_integration_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
