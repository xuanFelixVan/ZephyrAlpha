---
doc_type: domain_architecture_diagram
title: D-INTEGRATION 管线路由架构图
version: "1.0"
status: active
date: 2026-06-25
owner: auto-generator
ttl: permanent
---

# 13_d_integration / 管线路由 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示管线路由（D-INTEGRATION）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-25 18:42:45
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 管线路由（D-INTEGRATION）的模块分布。共 314 个模块 / 314 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (303 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/integration/__init__.py  [production]               │
│   src/zephyr/integration/__init___from_orches.py  [prototype]    │
│   src/zephyr/integration/_extensions/__init__.py  [prototype]    │
│   src/zephyr/integration/api/__init__.py  [prototype]            │
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
│   src/zephyr/integration/core/__init__.py  [prototype]           │
│   src/zephyr/integration/cost_tracker.py  [prototype]            │
│   src/zephyr/integration/ct_pipe_routing.py  [prototype]         │
│   src/zephyr/integration/dead_letter_queue.py  [prototype]       │
│   ...还有 285 个模块 / 285 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                未分类 / Unclassified (11 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   F12-knowledge-base/  [design]                                  │
│   F13-mcp-cluster/  [design]                                     │
│   F14-pipeline/  [design]                                        │
│   src/zephyr/integration/local_model/deepseek_chat.py  [produ... │
│   src/zephyr/integration/pipeline_routing.py  [production]       │
│   tests/integration/test_f3_auto_integration.py  [production]    │
│   tests/integration/test_mcp_boot_hooks_integration.py  [prod... │
│   tests/integration/test_mcp_health_check_cron.py  [production]  │
│   tests/integration/test_mcp_health_check_recovery.py  [produ... │
│   tests/integration/test_mcp_idle_timeout.py  [production]       │
│   tests/integration/test_mcp_signal_shutdown.py  [production]    │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 314 个模块 / 314 modules）。

### L1 基础层 / Foundation Layer (303 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/integration/__init__.py | src/zephyr/integration/__init__.py | production | generated |
| 2 | src/zephyr/integration/__init___from_orches.py | src/zephyr/integration/__init___from_... | prototype | generated |
| 3 | src/zephyr/integration/_extensions/__init__.py | src/zephyr/integration/_extensions/__... | prototype | deprecated |
| 4 | src/zephyr/integration/api/__init__.py | src/zephyr/integration/api/__init__.py | prototype | deprecated |
| 5 | src/zephyr/integration/backpressure_manager.py | src/zephyr/integration/backpressure_m... | prototype | generated |
| 6 | src/zephyr/integration/backpressure_types.py | src/zephyr/integration/backpressure_t... | prototype | generated |
| 7 | src/zephyr/integration/behavioral_admission/__init__.py | src/zephyr/integration/behavioral_adm... | prototype | generated |
| 8 | src/zephyr/integration/behavioral_admission/admission_res... | src/zephyr/integration/behavioral_adm... | production | generated |
| 9 | src/zephyr/integration/budget_enforcer/__init__.py | src/zephyr/integration/budget_enforce... | prototype | generated |
| 10 | src/zephyr/integration/budget_enforcer/degradation_spiral... | src/zephyr/integration/budget_enforce... | prototype | generated |
| 11 | src/zephyr/integration/circuit_breaker_manager.py | src/zephyr/integration/circuit_breake... | prototype | generated |
| 12 | src/zephyr/integration/contracts/__init__.py | src/zephyr/integration/contracts/__in... | prototype | generated |
| 13 | src/zephyr/integration/contracts/experiment_result.py | src/zephyr/integration/contracts/expe... | prototype | generated |
| 14 | src/zephyr/integration/contracts/model_serving_response.py | src/zephyr/integration/contracts/mode... | prototype | generated |
| 15 | src/zephyr/integration/core/__init__.py | src/zephyr/integration/core/__init__.py | prototype | deprecated |
| 16 | src/zephyr/integration/cost_tracker.py | src/zephyr/integration/cost_tracker.py | prototype | generated |
| 17 | src/zephyr/integration/ct_pipe_routing.py | src/zephyr/integration/ct_pipe_routin... | prototype | generated |
| 18 | src/zephyr/integration/dead_letter_queue.py | src/zephyr/integration/dead_letter_qu... | prototype | generated |
| 19 | src/zephyr/integration/infrastructure/__init__.py | src/zephyr/integration/infrastructure... | prototype | deprecated |
| 20 | src/zephyr/integration/layer1_discovery/__init__.py | src/zephyr/integration/layer1_discove... | prototype | generated |
| 21 | src/zephyr/integration/layer1_discovery/a2a_registry.py | src/zephyr/integration/layer1_discove... | prototype | generated |
| 22 | src/zephyr/integration/layer1_discovery/agent_card.py | src/zephyr/integration/layer1_discove... | prototype | generated |
| 23 | src/zephyr/integration/layer1_discovery/identity_verifier.py | src/zephyr/integration/layer1_discove... | prototype | generated |
| 24 | src/zephyr/integration/layer2_communication/__init__.py | src/zephyr/integration/layer2_communi... | prototype | generated |
| 25 | src/zephyr/integration/layer2_communication/a2a_schemas.py | src/zephyr/integration/layer2_communi... | prototype | generated |
| 26 | src/zephyr/integration/layer2_communication/a2a_state.py | src/zephyr/integration/layer2_communi... | prototype | generated |
| 27 | src/zephyr/integration/layer2_communication/context_packa... | src/zephyr/integration/layer2_communi... | prototype | generated |
| 28 | src/zephyr/integration/layer2_communication/handoff_manag... | src/zephyr/integration/layer2_communi... | prototype | generated |
| 29 | src/zephyr/integration/layer2_communication/message_route... | src/zephyr/integration/layer2_communi... | prototype | generated |
| 30 | src/zephyr/integration/layer2_communication/push_notifier.py | src/zephyr/integration/layer2_communi... | prototype | generated |
| 31 | src/zephyr/integration/layer2_communication/streaming.py | src/zephyr/integration/layer2_communi... | prototype | generated |
| 32 | src/zephyr/integration/layer2_communication/trigger_monit... | src/zephyr/integration/layer2_communi... | prototype | generated |
| 33 | src/zephyr/integration/layer3_coordination/__init__.py | src/zephyr/integration/layer3_coordin... | prototype | generated |
| 34 | src/zephyr/integration/layer_consumer_registry.py | src/zephyr/integration/layer_consumer... | prototype | generated |
| 35 | src/zephyr/integration/layer_router.py | src/zephyr/integration/layer_router.py | prototype | generated |
| 36 | src/zephyr/integration/llm_bridge.py | src/zephyr/integration/llm_bridge.py | prototype | generated |
| 37 | src/zephyr/integration/llm_gateway.py | src/zephyr/integration/llm_gateway.py | prototype | generated |
| 38 | src/zephyr/integration/local_model/__init__.py | src/zephyr/integration/local_model/__... | prototype | generated |
| 39 | src/zephyr/integration/local_model/cache_layer.py | src/zephyr/integration/local_model/ca... | prototype | generated |
| 40 | src/zephyr/integration/local_model/embedding_router.py | src/zephyr/integration/local_model/em... | production | generated |
| 41 | src/zephyr/integration/local_model/local_model_scheduler.py | src/zephyr/integration/local_model/lo... | prototype | generated |
| 42 | src/zephyr/integration/local_model/ollama_chat.py | src/zephyr/integration/local_model/ol... | prototype | generated |
| 43 | src/zephyr/integration/local_model/ollama_embedding.py | src/zephyr/integration/local_model/ol... | prototype | generated |
| 44 | src/zephyr/integration/mcp/__init__.py | src/zephyr/integration/mcp/__init__.py | prototype | generated |
| 45 | src/zephyr/integration/mcp/_base_server.py | src/zephyr/integration/mcp/_base_serv... | prototype | generated |
| 46 | src/zephyr/integration/mcp/audit_logger.py | src/zephyr/integration/mcp/audit_logg... | prototype | generated |
| 47 | src/zephyr/integration/mcp/blueprint_search_server.py | src/zephyr/integration/mcp/blueprint_... | prototype | generated |
| 48 | src/zephyr/integration/mcp/doc_guard_server.py | src/zephyr/integration/mcp/doc_guard_... | prototype | generated |
| 49 | src/zephyr/integration/mcp/error_codes.py | src/zephyr/integration/mcp/error_code... | prototype | generated |
| 50 | src/zephyr/integration/mcp/gate_engine_server.py | src/zephyr/integration/mcp/gate_engin... | prototype | generated |
| 51 | src/zephyr/integration/mcp/gateway_server.py | src/zephyr/integration/mcp/gateway_se... | prototype | generated |
| 52 | src/zephyr/integration/mcp/handoff_auto_loader.py | src/zephyr/integration/mcp/handoff_au... | prototype | generated |
| 53 | src/zephyr/integration/mcp/knowledge_base_server.py | src/zephyr/integration/mcp/knowledge_... | prototype | generated |
| 54 | src/zephyr/integration/mcp/prompt_provider.py | src/zephyr/integration/mcp/prompt_pro... | prototype | generated |
| 55 | src/zephyr/integration/mcp/rate_limiter.py | src/zephyr/integration/mcp/rate_limit... | prototype | generated |
| 56 | src/zephyr/integration/mcp/resource_provider.py | src/zephyr/integration/mcp/resource_p... | prototype | generated |
| 57 | src/zephyr/integration/mcp/sandbox_server.py | src/zephyr/integration/mcp/sandbox_se... | prototype | generated |
| 58 | src/zephyr/integration/mcp/sentinel_server.py | src/zephyr/integration/mcp/sentinel_s... | prototype | generated |
| 59 | src/zephyr/integration/mcp/task_manager_server.py | src/zephyr/integration/mcp/task_manag... | prototype | generated |
| 60 | src/zephyr/integration/mcp/telemetry_server.py | src/zephyr/integration/mcp/telemetry_... | prototype | generated |
| 61 | src/zephyr/integration/mcp/tool_contracts.yaml | src/zephyr/integration/mcp/tool_contr... | production | deprecated |
| 62 | src/zephyr/integration/mcp/vector_memory_server.py | src/zephyr/integration/mcp/vector_mem... | prototype | generated |
| 63 | src/zephyr/integration/mcp_server.py | src/zephyr/integration/mcp_server.py | prototype | generated |
| 64 | src/zephyr/integration/model_profiler/__init__.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 65 | src/zephyr/integration/model_profiler/benchmark_suite.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 66 | src/zephyr/integration/model_profiler/capability_passport.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 67 | src/zephyr/integration/model_profiler/cli.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 68 | src/zephyr/integration/model_profiler/deepseek_v4_chat.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 69 | src/zephyr/integration/model_profiler/exam_orchestrator.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 70 | src/zephyr/integration/model_profiler/exam_test_cases.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 71 | src/zephyr/integration/model_profiler/model_discovery.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 72 | src/zephyr/integration/model_profiler/profiler.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 73 | src/zephyr/integration/model_profiler/results_writer.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 74 | src/zephyr/integration/model_profiler/task_model_learner.py | src/zephyr/integration/model_profiler... | prototype | generated |
| 75 | src/zephyr/integration/model_router.py | src/zephyr/integration/model_router.py | prototype | generated |
| 76 | src/zephyr/integration/models.py | src/zephyr/integration/models.py | prototype | generated |
| 77 | src/zephyr/integration/pipeline_agent_bridge.py | src/zephyr/integration/pipeline_agent... | prototype | generated |
| 78 | src/zephyr/integration/pipeline_lock.py | src/zephyr/integration/pipeline_lock.py | prototype | generated |
| 79 | src/zephyr/integration/pipeline_orchestrator.py | src/zephyr/integration/pipeline_orche... | prototype | generated |
| 80 | src/zephyr/integration/pipeline_roadmap.py | src/zephyr/integration/pipeline_roadm... | prototype | generated |
| 81 | src/zephyr/integration/ports.py | src/zephyr/integration/ports.py | prototype | generated |
| 82 | src/zephyr/integration/preemption_manager.py | src/zephyr/integration/preemption_man... | prototype | generated |
| 83 | src/zephyr/integration/routing_plugins.py | src/zephyr/integration/routing_plugin... | prototype | generated |
| 84 | src/zephyr/integration/services/__init__.py | src/zephyr/integration/services/__ini... | prototype | deprecated |
| 85 | src/zephyr/integration/shared/api_03/__init__.py | src/zephyr/integration/shared/api_03/... | prototype | generated |
| 86 | src/zephyr/integration/shared/api_03/api_client.py | src/zephyr/integration/shared/api_03/... | prototype | generated |
| 87 | src/zephyr/integration/shared/api_03/api_index.py | src/zephyr/integration/shared/api_03/... | prototype | generated |
| 88 | src/zephyr/integration/shared/api_03/dos_launcher.py | src/zephyr/integration/shared/api_03/... | production | generated |
| 89 | src/zephyr/integration/shared/contracts/errors/__init__.py | src/zephyr/integration/shared/contrac... | prototype | generated |
| 90 | src/zephyr/integration/shared/contracts/errors/contract_v... | src/zephyr/integration/shared/contrac... | prototype | generated |
| 91 | src/zephyr/integration/shared/contracts/errors/data_quali... | src/zephyr/integration/shared/contrac... | prototype | generated |
| 92 | src/zephyr/integration/shared/contracts/errors/execution_... | src/zephyr/integration/shared/contrac... | prototype | generated |
| 93 | src/zephyr/integration/shared/contracts/errors/factor_com... | src/zephyr/integration/shared/contrac... | prototype | generated |
| 94 | src/zephyr/integration/shared/contracts/errors/risk_limit... | src/zephyr/integration/shared/contrac... | prototype | generated |
| 95 | src/zephyr/integration/shared/contracts/errors/signal_deg... | src/zephyr/integration/shared/contrac... | production | generated |
| 96 | src/zephyr/integration/shared/events/__init__.py | src/zephyr/integration/shared/events/... | prototype | generated |
| 97 | src/zephyr/integration/shared/events/dlq.py | src/zephyr/integration/shared/events/... | prototype | generated |
| 98 | src/zephyr/integration/shared/events/dlq_bridge.py | src/zephyr/integration/shared/events/... | prototype | generated |
| 99 | src/zephyr/integration/shared/events/event_bus_upgrade.py | src/zephyr/integration/shared/events/... | prototype | generated |
| 100 | src/zephyr/integration/shared/events/event_schemas.py | src/zephyr/integration/shared/events/... | prototype | generated |
| 101 | src/zephyr/integration/shared/events/upgrade_strategy.py | src/zephyr/integration/shared/events/... | production | generated |
| 102 | src/zephyr/integration/shared/schema/__init__.py | src/zephyr/integration/shared/schema/... | prototype | generated |
| 103 | src/zephyr/integration/shared/schema/base_config.py | src/zephyr/integration/shared/schema/... | production | generated |
| 104 | src/zephyr/integration/shared/schema/execution_model.py | src/zephyr/integration/shared/schema/... | production | generated |
| 105 | src/zephyr/integration/shared/schema/schema_registry.py | src/zephyr/integration/shared/schema/... | production | generated |
| 106 | src/zephyr/integration/shared/schema/schemas.py | src/zephyr/integration/shared/schema/... | production | generated |
| 107 | src/zephyr/integration/shared/schema/severity_types.py | src/zephyr/integration/shared/schema/... | production | generated |
| 108 | src/zephyr/integration/shared_08/__init__.py | src/zephyr/integration/shared_08/__in... | prototype | generated |
| 109 | src/zephyr/integration/shared_08/__version__.py | src/zephyr/integration/shared_08/__ve... | production | generated |
| 110 | src/zephyr/integration/shared_08/_contracts.py | src/zephyr/integration/shared_08/_con... | prototype | generated |
| 111 | src/zephyr/integration/shared_08/_infrastructure.py | src/zephyr/integration/shared_08/_inf... | prototype | generated |
| 112 | src/zephyr/integration/shared_08/_observability.py | src/zephyr/integration/shared_08/_obs... | prototype | generated |
| 113 | src/zephyr/integration/shared_08/_patterns.py | src/zephyr/integration/shared_08/_pat... | prototype | generated |
| 114 | src/zephyr/integration/shared_08/_version_and_types.py | src/zephyr/integration/shared_08/_ver... | prototype | generated |
| 115 | src/zephyr/integration/shared_08/agent_identity_impl.py | src/zephyr/integration/shared_08/agen... | prototype | generated |
| 116 | src/zephyr/integration/shared_08/api_client.py | src/zephyr/integration/shared_08/api_... | prototype | generated |
| 117 | src/zephyr/integration/shared_08/api_index.py | src/zephyr/integration/shared_08/api_... | prototype | generated |
| 118 | src/zephyr/integration/shared_08/blueprint_scorer.py | src/zephyr/integration/shared_08/blue... | prototype | generated |
| 119 | src/zephyr/integration/shared_08/cache.py | src/zephyr/integration/shared_08/cach... | prototype | generated |
| 120 | src/zephyr/integration/shared_08/capability.py | src/zephyr/integration/shared_08/capa... | prototype | generated |
| 121 | src/zephyr/integration/shared_08/constants.py | src/zephyr/integration/shared_08/cons... | prototype | generated |
| 122 | src/zephyr/integration/shared_08/content_fingerprint.py | src/zephyr/integration/shared_08/cont... | production | generated |
| 123 | src/zephyr/integration/shared_08/context.py | src/zephyr/integration/shared_08/cont... | production | generated |
| 124 | src/zephyr/integration/shared_08/contract_bus.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 125 | src/zephyr/integration/shared_08/contract_enforcer.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 126 | src/zephyr/integration/shared_08/contract_tester.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 127 | src/zephyr/integration/shared_08/contract_versions.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 128 | src/zephyr/integration/shared_08/contracts/__init__.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 129 | src/zephyr/integration/shared_08/contracts/approval_types.py | src/zephyr/integration/shared_08/cont... | production | generated |
| 130 | src/zephyr/integration/shared_08/contracts/backpressure/_... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 131 | src/zephyr/integration/shared_08/contracts/backpressure/p... | src/zephyr/integration/shared_08/cont... | production | generated |
| 132 | src/zephyr/integration/shared_08/contracts/backpressure/r... | src/zephyr/integration/shared_08/cont... | production | generated |
| 133 | src/zephyr/integration/shared_08/contracts/backpressure/t... | src/zephyr/integration/shared_08/cont... | production | generated |
| 134 | src/zephyr/integration/shared_08/contracts/capital_alloca... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 135 | src/zephyr/integration/shared_08/contracts/compliance_rul... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 136 | src/zephyr/integration/shared_08/contracts/core/__init__.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 137 | src/zephyr/integration/shared_08/contracts/core/base_even... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 138 | src/zephyr/integration/shared_08/contracts/core/enforcer.py | src/zephyr/integration/shared_08/cont... | production | generated |
| 139 | src/zephyr/integration/shared_08/contracts/core/gate_type... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 140 | src/zephyr/integration/shared_08/contracts/core/registry.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 141 | src/zephyr/integration/shared_08/contracts/core/runtime_p... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 142 | src/zephyr/integration/shared_08/contracts/core/system_co... | src/zephyr/integration/shared_08/cont... | production | generated |
| 143 | src/zephyr/integration/shared_08/contracts/core/telemetry... | src/zephyr/integration/shared_08/cont... | production | generated |
| 144 | src/zephyr/integration/shared_08/contracts/core/timestamp.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 145 | src/zephyr/integration/shared_08/contracts/core/trace_con... | src/zephyr/integration/shared_08/cont... | production | generated |
| 146 | src/zephyr/integration/shared_08/contracts/escalation/__i... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 147 | src/zephyr/integration/shared_08/contracts/escalation/bud... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 148 | src/zephyr/integration/shared_08/contracts/execution_repo... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 149 | src/zephyr/integration/shared_08/contracts/experiment/__i... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 150 | src/zephyr/integration/shared_08/contracts/experiment/exp... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 151 | src/zephyr/integration/shared_08/contracts/experiment/mod... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 152 | src/zephyr/integration/shared_08/contracts/experiment_res... | src/zephyr/integration/shared_08/cont... | production | generated |
| 153 | src/zephyr/integration/shared_08/contracts/external/__ini... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 154 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 155 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 156 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 157 | src/zephyr/integration/shared_08/contracts/external/ext_0... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 158 | src/zephyr/integration/shared_08/contracts/factor_monitor... | src/zephyr/integration/shared_08/cont... | production | generated |
| 159 | src/zephyr/integration/shared_08/contracts/factor_signal.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 160 | src/zephyr/integration/shared_08/contracts/fill.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 161 | src/zephyr/integration/shared_08/contracts/gate/__init__.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 162 | src/zephyr/integration/shared_08/contracts/gate/gate_resu... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 163 | src/zephyr/integration/shared_08/contracts/identity/__ini... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 164 | src/zephyr/integration/shared_08/contracts/identity/agent... | src/zephyr/integration/shared_08/cont... | production | generated |
| 165 | src/zephyr/integration/shared_08/contracts/identity/permi... | src/zephyr/integration/shared_08/cont... | production | generated |
| 166 | src/zephyr/integration/shared_08/contracts/macro_factor_s... | src/zephyr/integration/shared_08/cont... | production | generated |
| 167 | src/zephyr/integration/shared_08/contracts/market_data.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 168 | src/zephyr/integration/shared_08/contracts/model_serving_... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 169 | src/zephyr/integration/shared_08/contracts/model_serving_... | src/zephyr/integration/shared_08/cont... | production | generated |
| 170 | src/zephyr/integration/shared_08/contracts/order.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 171 | src/zephyr/integration/shared_08/contracts/performance_at... | src/zephyr/integration/shared_08/cont... | production | generated |
| 172 | src/zephyr/integration/shared_08/contracts/position.py | src/zephyr/integration/shared_08/cont... | production | generated |
| 173 | src/zephyr/integration/shared_08/contracts/protocols.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 174 | src/zephyr/integration/shared_08/contracts/risk_dashboard... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 175 | src/zephyr/integration/shared_08/contracts/risk_limits.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 176 | src/zephyr/integration/shared_08/contracts/risk_metrics.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 177 | src/zephyr/integration/shared_08/contracts/rollback_types.py | src/zephyr/integration/shared_08/cont... | production | generated |
| 178 | src/zephyr/integration/shared_08/contracts/runtime_types.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 179 | src/zephyr/integration/shared_08/contracts/security/__ini... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 180 | src/zephyr/integration/shared_08/contracts/security/secur... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 181 | src/zephyr/integration/shared_08/contracts/strategy_lifec... | src/zephyr/integration/shared_08/cont... | production | generated |
| 182 | src/zephyr/integration/shared_08/contracts/synthesized_si... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 183 | src/zephyr/integration/shared_08/contracts/sys_master_com... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 184 | src/zephyr/integration/shared_08/contracts/system_configu... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 185 | src/zephyr/integration/shared_08/contracts/telemetry_emit... | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 186 | src/zephyr/integration/shared_08/contracts/trace_context.py | src/zephyr/integration/shared_08/cont... | prototype | generated |
| 187 | src/zephyr/integration/shared_08/deprecation.py | src/zephyr/integration/shared_08/depr... | production | generated |
| 188 | src/zephyr/integration/shared_08/diff_utils.py | src/zephyr/integration/shared_08/diff... | production | generated |
| 189 | src/zephyr/integration/shared_08/durable_execution.py | src/zephyr/integration/shared_08/dura... | production | generated |
| 190 | src/zephyr/integration/shared_08/env.py | src/zephyr/integration/shared_08/env.py | prototype | generated |
| 191 | src/zephyr/integration/shared_08/errors.py | src/zephyr/integration/shared_08/erro... | production | generated |
| 192 | src/zephyr/integration/shared_08/evals.py | src/zephyr/integration/shared_08/eval... | production | generated |
| 193 | src/zephyr/integration/shared_08/event_bus.py | src/zephyr/integration/shared_08/even... | production | stable |
| 194 | src/zephyr/integration/shared_08/file_utils.py | src/zephyr/integration/shared_08/file... | production | generated |
| 195 | src/zephyr/integration/shared_08/flags.py | src/zephyr/integration/shared_08/flag... | production | generated |
| 196 | src/zephyr/integration/shared_08/foundation/__init__.py | src/zephyr/integration/shared_08/foun... | production | generated |
| 197 | src/zephyr/integration/shared_08/foundation/constants.py | src/zephyr/integration/shared_08/foun... | prototype | generated |
| 198 | src/zephyr/integration/shared_08/foundation/deprecation.py | src/zephyr/integration/shared_08/foun... | prototype | generated |
| 199 | src/zephyr/integration/shared_08/foundation/env.py | src/zephyr/integration/shared_08/foun... | prototype | generated |
| 200 | src/zephyr/integration/shared_08/foundation/errors.py | src/zephyr/integration/shared_08/foun... | prototype | generated |

> (仅显示前 200 个模块，共 303 个)

### 未分类 / Unclassified (11 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | F12-knowledge-base/ | F12-knowledge-base/ | design | stable |
| 2 | F13-mcp-cluster/ | F13-mcp-cluster/ | design | stable |
| 3 | F14-pipeline/ | F14-pipeline/ | design | stable |
| 4 | src/zephyr/integration/local_model/deepseek_chat.py | src/zephyr/integration/local_model/de... | production | generated |
| 5 | src/zephyr/integration/pipeline_routing.py | src/zephyr/integration/pipeline_routi... | production | generated |
| 6 | tests/integration/test_f3_auto_integration.py | tests/integration/test_f3_auto_integr... | production | generated |
| 7 | tests/integration/test_mcp_boot_hooks_integration.py | tests/integration/test_mcp_boot_hooks... | production | generated |
| 8 | tests/integration/test_mcp_health_check_cron.py | tests/integration/test_mcp_health_che... | production | generated |
| 9 | tests/integration/test_mcp_health_check_recovery.py | tests/integration/test_mcp_health_che... | production | generated |
| 10 | tests/integration/test_mcp_idle_timeout.py | tests/integration/test_mcp_idle_timeo... | production | generated |
| 11 | tests/integration/test_mcp_signal_shutdown.py | tests/integration/test_mcp_signal_shu... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 310 条 / 310 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 310 条 / 310 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 3                               │
│   [import_depends]: 276 条 / edges                               │
│   [config_depends]: 33 条 / edges                                │
│   [data]: 1 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (276 条 / edges)                 │
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
│   ...还有 227 条 / 227 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (33 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (1 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 310 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `13_d_integration_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
