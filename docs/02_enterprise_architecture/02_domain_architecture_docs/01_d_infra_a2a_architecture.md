---
doc_type: architecture_view
title: D-INFRA_A2A a2a_communication架构图
version: "1.0"
status: active
date: 2026-06-27
owner: auto-generator
ttl: permanent
---

# 01_d_infra_a2a / a2a_communication 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示a2a_communication（D-INFRA_A2A）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-27 02:42:10
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 a2a_communication（D-INFRA_A2A）的模块分布。共 101 个模块 / 101 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (101 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/infrastructure/a2a_protocol/__init__.py  [produc... │
│   src/zephyr/infrastructure/a2a_protocol/a2a_card_registry.py... │
│   src/zephyr/infrastructure/a2a_protocol/layer1_discovery/__i... │
│   src/zephyr/infrastructure/a2a_protocol/layer1_discovery/a2a... │
│   src/zephyr/infrastructure/a2a_protocol/layer1_discovery/age... │
│   src/zephyr/infrastructure/a2a_protocol/layer1_discovery/ide... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer2_communication... │
│   src/zephyr/infrastructure/a2a_protocol/layer3_coordination/... │
│   src/zephyr/infrastructure/a2a_protocol/layer3_coordination/... │
│   src/zephyr/infrastructure/a2a_protocol/layer3_coordination/... │
│   ...还有 83 个模块 / 83 more modules                            │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 101 个模块 / 101 modules）。

### L1 基础层 / Foundation Layer (101 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/infrastructure/a2a_protocol/__init__.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 2 | src/zephyr/infrastructure/a2a_protocol/a2a_card_registry.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 3 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/_... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 4 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/a... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 5 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/a... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 6 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/i... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 7 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 8 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 9 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 10 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 11 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 12 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 13 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 14 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 15 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 16 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 17 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 18 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 19 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 20 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 21 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 22 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 23 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 24 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 25 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 26 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 27 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 28 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 29 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 30 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 31 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 32 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 33 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 34 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 35 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 36 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 37 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 38 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 39 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 40 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 41 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 42 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 43 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 44 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 45 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 46 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 47 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 48 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 49 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 50 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 51 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 52 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 53 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 54 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 55 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 56 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 57 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 58 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 59 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 60 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 61 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 62 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 63 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 64 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 65 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 66 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 67 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 68 | src/zephyr/infrastructure/a2a_protocol/legacy_auditor.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 69 | src/zephyr/infrastructure/a2a_protocol/legacy_protocol.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 70 | src/zephyr/infrastructure/a2a_protocol/local_first_arch.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 71 | src/zephyr/infrastructure/a2a_protocol/market_data_pipeli... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 72 | src/zephyr/infrastructure/a2a_protocol/migration_strategy.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 73 | src/zephyr/infrastructure/a2a_protocol/multi_agent.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 74 | src/zephyr/infrastructure/a2a_protocol/multi_model_consen... | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 75 | src/zephyr/infrastructure/a2a_protocol/offline_autonomy.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 76 | src/zephyr/infrastructure/a2a_protocol/offline_resilience.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 77 | src/zephyr/infrastructure/a2a_protocol/phase_hold.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 78 | src/zephyr/infrastructure/a2a_protocol/prompt_lifecycle.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 79 | src/zephyr/infrastructure/a2a_protocol/realtime_streaming.py | src/zephyr/infrastructure/a2a_protoco... | production | generated |
| 80 | src/zephyr/infrastructure/events/__init__.py | src/zephyr/infrastructure/events/__in... | production | generated |
| 81 | src/zephyr/infrastructure/events/event_store.py | src/zephyr/infrastructure/events/even... | production | generated |
| 82 | src/zephyr/infrastructure/pipeline/__init__.py | src/zephyr/infrastructure/pipeline/__... | production | generated |
| 83 | src/zephyr/infrastructure/pipeline/backpressure_manager.py | src/zephyr/infrastructure/pipeline/ba... | production | generated |
| 84 | src/zephyr/infrastructure/pipeline/backpressure_types.py | src/zephyr/infrastructure/pipeline/ba... | production | generated |
| 85 | src/zephyr/infrastructure/pipeline/circuit_breaker_manage... | src/zephyr/infrastructure/pipeline/ci... | production | generated |
| 86 | src/zephyr/infrastructure/pipeline/cost_tracker.py | src/zephyr/infrastructure/pipeline/co... | production | generated |
| 87 | src/zephyr/infrastructure/pipeline/ct_pipe_routing.py | src/zephyr/infrastructure/pipeline/ct... | production | generated |
| 88 | src/zephyr/infrastructure/pipeline/dead_letter_queue.py | src/zephyr/infrastructure/pipeline/de... | production | generated |
| 89 | src/zephyr/infrastructure/pipeline/layer_consumer_registr... | src/zephyr/infrastructure/pipeline/la... | production | generated |
| 90 | src/zephyr/infrastructure/pipeline/layer_router.py | src/zephyr/infrastructure/pipeline/la... | production | generated |
| 91 | src/zephyr/infrastructure/pipeline/llm_gateway.py | src/zephyr/infrastructure/pipeline/ll... | production | generated |
| 92 | src/zephyr/infrastructure/pipeline/model_router.py | src/zephyr/infrastructure/pipeline/mo... | production | generated |
| 93 | src/zephyr/infrastructure/pipeline/models.py | src/zephyr/infrastructure/pipeline/mo... | production | generated |
| 94 | src/zephyr/infrastructure/pipeline/pipeline_agent_bridge.py | src/zephyr/infrastructure/pipeline/pi... | production | generated |
| 95 | src/zephyr/infrastructure/pipeline/pipeline_lock.py | src/zephyr/infrastructure/pipeline/pi... | production | generated |
| 96 | src/zephyr/infrastructure/pipeline/pipeline_roadmap.py | src/zephyr/infrastructure/pipeline/pi... | production | generated |
| 97 | src/zephyr/infrastructure/pipeline/preemption_manager.py | src/zephyr/infrastructure/pipeline/pr... | production | generated |
| 98 | src/zephyr/infrastructure/pipeline/routing_plugins.py | src/zephyr/infrastructure/pipeline/ro... | production | generated |
| 99 | src/zephyr/infrastructure/queue/__init__.py | src/zephyr/infrastructure/queue/__ini... | production | generated |
| 100 | src/zephyr/infrastructure/queue/task_queue.py | src/zephyr/infrastructure/queue/task_... | production | generated |
| 101 | src/zephyr/infrastructure/queue/task_scheduler.py | src/zephyr/infrastructure/queue/task_... | production | generated |

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 73 条 / 73 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│       依赖关系图 / Dependency Graph (共 73 条 / 73 edges)        │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 2                               │
│   [import_depends]: 50 条 / edges                                │
│   [config_depends]: 23 条 / edges                                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                 [import_depends] (50 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   a2a_card_registry.py → a2a_registry.py                         │
│   __init__.py → __init__.py                                      │
│   __init__.py → __init__.py                                      │
│   a2a_registry.py → agent_card.py                                │
│   __init__.py → agent_card.py                                    │
│   __init__.py → a2a_registry.py                                  │
│   __init__.py → identity_verifier.py                             │
│   message_router.py → a2a_schemas.py                             │
│   __init__.py → context_package.py                               │
│   __init__.py → a2a_schemas.py                                   │
│   __init__.py → a2a_state.py                                     │
│   __init__.py → handoff_manager.py                               │
│   __init__.py → message_router.py                                │
│   __init__.py → push_notifier.py                                 │
│   __init__.py → streaming.py                                     │
│   __init__.py → trigger_monitor.py                               │
│   supervisor.py → a2a_state.py                                   │
│   _core_coordination.py → cascade_guard.py                       │
│   _core_coordination.py → conflict_detector.py                   │
│   _core_coordination.py → arbitrator.py                          │
│   _core_coordination.py → construction_verifier.py               │
│   _core_coordination.py → semantic_diff.py                       │
│   _core_coordination.py → livelock_detector.py                   │
│   _core_coordination.py → deadlock_guard.py                      │
│   _core_coordination.py → supervisor.py                          │
│   _consensus.py → a2a_debate.py                                  │
│   _consensus.py → a2a_negotiation.py                             │
│   _consensus.py → a2a_saga.py                                    │
│   _consensus.py → a2a_voting.py                                  │
│   _consensus.py → a2a_work_steal.py                              │
│   _intelligence.py → a2a_blame_attribution.py                    │
│   _intelligence.py → a2a_behavior_fingerprint.py                 │
│   _intelligence.py → a2a_collusion_detector.py                   │
│   _intelligence.py → a2a_causal_trace.py                         │
│   _intelligence.py → a2a_cross_agent_semantic_...                │
│   _intelligence.py → a2a_knowledge_distill.py                    │
│   _intelligence.py → a2a_latent_comm.py                          │
│   _security_and_economics.py → a2a_anomaly_detector.py           │
│   _security_and_economics.py → a2a_economics.py                  │
│   _security_and_economics.py → a2a_forgetting.py                 │
│   _security_and_economics.py → a2a_delegation_chain.py           │
│   _security_and_economics.py → a2a_idle_guard.py                 │
│   _security_and_economics.py → a2a_idempotency.py                │
│   _security_and_economics.py → a2a_red_team.py                   │
│   _security_and_economics.py → a2a_temporal_admission.py         │
│   _security_and_economics.py → a2a_security.py                   │
│   _security_and_economics.py → session_smuggling_defense.py      │
│   __init__.py → event_store.py                                   │
│   __init__.py → llm_gateway.py                                   │
│   __init__.py → task_scheduler.py                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (23 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 73 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `01_d_infra_a2a_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
