---
doc_type: domain_architecture_diagram
title: D-INFRA_RUNTIME 运行时集成架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 02_d_infra_runtime / 运行时集成 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示运行时集成（D-INFRA_RUNTIME）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:01:56
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 运行时集成（D-INFRA_RUNTIME）的模块分布。共 727 个模块 / 727 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│         L0 基础设施层 / Infrastructure Layer (3 modules)         │
├──────────────────────────────────────────────────────────────────┤
│   Backup Manager(架构版)  [design]                               │
│   数据源可用性SLA追踪器  [design]                                │
│   配置管理器  [design]                                           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (415 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/__init__.py  [production]                           │
│   src/zephyr/autonomy_core/pipeline_orchestrator.py  [product... │
│   src/zephyr/infrastructure/__init__.py  [production]            │
│   src/zephyr/infrastructure/__init___from_infra.py  [production] │
│   src/zephyr/infrastructure/_base_server.py  [production]        │
│   src/zephyr/infrastructure/_extensions/__init__.py  [scaffol... │
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
│   ...还有 397 个模块 / 397 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (309 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   A-Share Diffusion Model Data Augmentation A股扩散模型数据增... │
│   AB Test Dependency Mapper AB测试依赖映射器  [design]           │
│   API Documentation Synchronizer API文档同步器  [design]         │
│   API Version Compatibility Detector API版本兼容检测器  [design] │
│   API Version Manager API版本管理器  [design]                    │
│   Alert Escalation Strategy Engine 告警升级策略引擎  [design]    │
│   Alert Silence Manager 告警静默管理器  [design]                 │
│   Alternative Data Source Expansion 另类数据源扩展  [design]     │
│   App 包装器  [design]                                           │
│   Application State Snapshotter 应用状态快照器  [design]         │
│   Architecture Compliance Checker 架构合规检查器  [design]       │
│   Architecture Evolution Planner 架构演进规划器  [design]        │
│   Architecture Recommendation Engine 架构推荐引擎  [design]      │
│   Automated Code Reviewer 自动代码审查器  [design]               │
│   Bandwidth Optimizer 带宽优化  [design]                         │
│   Base 基础  [design]                                            │
│   Batch Data Processor 批量数据处理器  [design]                  │
│   Blue-Green Dependency Mapper 蓝绿依赖映射器  [design]          │
│   ...还有 291 个模块 / 291 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 727 个模块 / 727 modules）。

### L0 基础设施层 / Infrastructure Layer (3 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 运维基础设施域/D-INFRA-03 | Backup Manager(架构版) | design | design_only |
| 2 | 运维基础设施域/D-INFRA-321 | 数据源可用性SLA追踪器 | design | design_only |
| 3 | 运行时基础设施域-配置管理/D-INFRA-06 | 配置管理器 | design | design_only |

### L1 基础层 / Foundation Layer (415 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/__init__.py | src/zephyr/__init__.py | production | draft |
| 2 | src/zephyr/autonomy_core/pipeline_orchestrator.py | src/zephyr/autonomy_core/pipeline_orc... | production | draft |
| 3 | src/zephyr/infrastructure/__init__.py | src/zephyr/infrastructure/__init__.py | production | draft |
| 4 | src/zephyr/infrastructure/__init___from_infra.py | src/zephyr/infrastructure/__init___fr... | production | draft |
| 5 | src/zephyr/infrastructure/_base_server.py | src/zephyr/infrastructure/_base_serve... | production | draft |
| 6 | src/zephyr/infrastructure/_extensions/__init__.py | src/zephyr/infrastructure/_extensions... | scaffold_placeholder | orphan |
| 7 | src/zephyr/infrastructure/a2a_protocol/__init__.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 8 | src/zephyr/infrastructure/a2a_protocol/a2a_card_registry.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 9 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/_... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 10 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/a... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 11 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/a... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 12 | src/zephyr/infrastructure/a2a_protocol/layer1_discovery/i... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 13 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 14 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 15 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 16 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 17 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 18 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 19 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 20 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 21 | src/zephyr/infrastructure/a2a_protocol/layer2_communicati... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 22 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 23 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 24 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 25 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 26 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 27 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 28 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 29 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 30 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 31 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 32 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 33 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 34 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 35 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 36 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 37 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 38 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 39 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 40 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 41 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 42 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 43 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 44 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 45 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 46 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 47 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 48 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 49 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 50 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 51 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 52 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 53 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 54 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 55 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 56 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 57 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 58 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 59 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 60 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 61 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 62 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 63 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 64 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 65 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 66 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 67 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 68 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 69 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 70 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 71 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 72 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 73 | src/zephyr/infrastructure/a2a_protocol/layer3_coordinatio... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 74 | src/zephyr/infrastructure/a2a_protocol/legacy_auditor.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 75 | src/zephyr/infrastructure/a2a_protocol/legacy_protocol.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 76 | src/zephyr/infrastructure/a2a_protocol/local_first_arch.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 77 | src/zephyr/infrastructure/a2a_protocol/market_data_pipeli... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 78 | src/zephyr/infrastructure/a2a_protocol/migration_strategy.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 79 | src/zephyr/infrastructure/a2a_protocol/multi_agent.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 80 | src/zephyr/infrastructure/a2a_protocol/multi_model_consen... | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 81 | src/zephyr/infrastructure/a2a_protocol/offline_autonomy.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 82 | src/zephyr/infrastructure/a2a_protocol/offline_resilience.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 83 | src/zephyr/infrastructure/a2a_protocol/phase_hold.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 84 | src/zephyr/infrastructure/a2a_protocol/prompt_lifecycle.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 85 | src/zephyr/infrastructure/a2a_protocol/realtime_streaming.py | src/zephyr/infrastructure/a2a_protoco... | production | draft |
| 86 | src/zephyr/infrastructure/adaptation/__init__.py | src/zephyr/infrastructure/adaptation/... | production | draft |
| 87 | src/zephyr/infrastructure/api/__init__.py | src/zephyr/infrastructure/api/__init_... | scaffold_placeholder | orphan |
| 88 | src/zephyr/infrastructure/asset_inventory/__init__.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 89 | src/zephyr/infrastructure/asset_inventory/__main__.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 90 | src/zephyr/infrastructure/asset_inventory/classifier.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 91 | src/zephyr/infrastructure/asset_inventory/dashboard.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 92 | src/zephyr/infrastructure/asset_inventory/dependency.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 93 | src/zephyr/infrastructure/asset_inventory/index_generator.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 94 | src/zephyr/infrastructure/asset_inventory/lifecycle.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 95 | src/zephyr/infrastructure/asset_inventory/mcp_server.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 96 | src/zephyr/infrastructure/asset_inventory/metadata.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 97 | src/zephyr/infrastructure/asset_inventory/models.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 98 | src/zephyr/infrastructure/asset_inventory/reconciler.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 99 | src/zephyr/infrastructure/asset_inventory/registry_adapte... | src/zephyr/infrastructure/asset_inven... | production | draft |
| 100 | src/zephyr/infrastructure/asset_inventory/scanner.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 101 | src/zephyr/infrastructure/asset_inventory/telemetry.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 102 | src/zephyr/infrastructure/asset_inventory/trust_anchor.py | src/zephyr/infrastructure/asset_inven... | production | draft |
| 103 | src/zephyr/infrastructure/audit_logger.py | src/zephyr/infrastructure/audit_logge... | production | draft |
| 104 | src/zephyr/infrastructure/auto_diagnostics.py | src/zephyr/infrastructure/auto_diagno... | production | draft |
| 105 | src/zephyr/infrastructure/auto_fix_engine/__init__.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 106 | src/zephyr/infrastructure/auto_fix_engine/__main__.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 107 | src/zephyr/infrastructure/auto_fix_engine/alignment_synce... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 108 | src/zephyr/infrastructure/auto_fix_engine/all_completer.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 109 | src/zephyr/infrastructure/auto_fix_engine/batch_fixer.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 110 | src/zephyr/infrastructure/auto_fix_engine/compliance_audi... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 111 | src/zephyr/infrastructure/auto_fix_engine/config_fixer.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 112 | src/zephyr/infrastructure/auto_fix_engine/dedup_extractor.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 113 | src/zephyr/infrastructure/auto_fix_engine/dep_version_fix... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 114 | src/zephyr/infrastructure/auto_fix_engine/drift_fixer.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 115 | src/zephyr/infrastructure/auto_fix_engine/engine.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 116 | src/zephyr/infrastructure/auto_fix_engine/escalation_brid... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 117 | src/zephyr/infrastructure/auto_fix_engine/event_hooks.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 118 | src/zephyr/infrastructure/auto_fix_engine/fix_budget.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 119 | src/zephyr/infrastructure/auto_fix_engine/fix_diff.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 120 | src/zephyr/infrastructure/auto_fix_engine/fix_health_chec... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 121 | src/zephyr/infrastructure/auto_fix_engine/fix_pattern_min... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 122 | src/zephyr/infrastructure/auto_fix_engine/fix_reliability.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 123 | src/zephyr/infrastructure/auto_fix_engine/fix_report.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 124 | src/zephyr/infrastructure/auto_fix_engine/fix_safety.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 125 | src/zephyr/infrastructure/auto_fix_engine/fix_scheduler.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 126 | src/zephyr/infrastructure/auto_fix_engine/import_fixer.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 127 | src/zephyr/infrastructure/auto_fix_engine/interrupt_guard.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 128 | src/zephyr/infrastructure/auto_fix_engine/llm_fix_adapter.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 129 | src/zephyr/infrastructure/auto_fix_engine/models.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 130 | src/zephyr/infrastructure/auto_fix_engine/scaffold_regist... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 131 | src/zephyr/infrastructure/auto_fix_engine/self_heal_agent.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 132 | src/zephyr/infrastructure/auto_fix_engine/shadow_workspac... | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 133 | src/zephyr/infrastructure/auto_fix_engine/state_machine.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 134 | src/zephyr/infrastructure/auto_fix_engine/zombie_cleaner.py | src/zephyr/infrastructure/auto_fix_en... | production | draft |
| 135 | src/zephyr/infrastructure/blueprint_code_sync.py | src/zephyr/infrastructure/blueprint_c... | production | draft |
| 136 | src/zephyr/infrastructure/blueprint_search_server.py | src/zephyr/infrastructure/blueprint_s... | production | draft |
| 137 | src/zephyr/infrastructure/capacity_assurance/__init__.py | src/zephyr/infrastructure/capacity_as... | production | draft |
| 138 | src/zephyr/infrastructure/capacity_assurance/contracts/__... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 139 | src/zephyr/infrastructure/capacity_assurance/contracts/ba... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 140 | src/zephyr/infrastructure/capacity_assurance/contracts/ba... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 141 | src/zephyr/infrastructure/capacity_assurance/contracts/co... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 142 | src/zephyr/infrastructure/capacity_assurance/cross_module... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 143 | src/zephyr/infrastructure/capacity_assurance/modules/__in... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 144 | src/zephyr/infrastructure/capacity_assurance/modules/ai_s... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 145 | src/zephyr/infrastructure/capacity_assurance/modules/capa... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 146 | src/zephyr/infrastructure/capacity_assurance/modules/clif... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 147 | src/zephyr/infrastructure/capacity_assurance/modules/cold... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 148 | src/zephyr/infrastructure/capacity_assurance/modules/conf... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 149 | src/zephyr/infrastructure/capacity_assurance/modules/cont... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 150 | src/zephyr/infrastructure/capacity_assurance/modules/degr... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 151 | src/zephyr/infrastructure/capacity_assurance/modules/dr_d... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 152 | src/zephyr/infrastructure/capacity_assurance/modules/grac... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 153 | src/zephyr/infrastructure/capacity_assurance/modules/hawt... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 154 | src/zephyr/infrastructure/capacity_assurance/modules/mult... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 155 | src/zephyr/infrastructure/capacity_assurance/modules/obse... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 156 | src/zephyr/infrastructure/capacity_assurance/modules/owne... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 157 | src/zephyr/infrastructure/capacity_assurance/modules/per_... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 158 | src/zephyr/infrastructure/capacity_assurance/modules/star... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 159 | src/zephyr/infrastructure/capacity_assurance/modules/sunk... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 160 | src/zephyr/infrastructure/capacity_assurance/modules/time... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 161 | src/zephyr/infrastructure/capacity_assurance/modules/toke... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 162 | src/zephyr/infrastructure/capacity_assurance/modules/trac... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 163 | src/zephyr/infrastructure/capacity_assurance/modules/winf... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 164 | src/zephyr/infrastructure/capacity_assurance/risk_mitigat... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 165 | src/zephyr/infrastructure/capacity_assurance/schema.py | src/zephyr/infrastructure/capacity_as... | production | draft |
| 166 | src/zephyr/infrastructure/capacity_assurance/sli_instrume... | src/zephyr/infrastructure/capacity_as... | production | draft |
| 167 | src/zephyr/infrastructure/capacity_assurance/tech_stack.py | src/zephyr/infrastructure/capacity_as... | production | draft |
| 168 | src/zephyr/infrastructure/compensation/__init__.py | src/zephyr/infrastructure/compensatio... | production | draft |
| 169 | src/zephyr/infrastructure/config/__init__.py | src/zephyr/infrastructure/config/__in... | production | draft |
| 170 | src/zephyr/infrastructure/config/shared/config/__init__.py | src/zephyr/infrastructure/config/shar... | production | draft |
| 171 | src/zephyr/infrastructure/config/shared/config/loader.py | src/zephyr/infrastructure/config/shar... | production | draft |
| 172 | src/zephyr/infrastructure/config_validator.py | src/zephyr/infrastructure/config_vali... | production | draft |
| 173 | src/zephyr/infrastructure/contract_tester.py | src/zephyr/infrastructure/contract_te... | production | draft |
| 174 | src/zephyr/infrastructure/core/__init__.py | src/zephyr/infrastructure/core/__init... | scaffold_placeholder | orphan |
| 175 | src/zephyr/infrastructure/cost_tracker.py | src/zephyr/infrastructure/cost_tracke... | production | draft |
| 176 | src/zephyr/infrastructure/dashboard/__init__.py | src/zephyr/infrastructure/dashboard/_... | production | orphan |
| 177 | src/zephyr/infrastructure/dashboard/components/__init__.py | src/zephyr/infrastructure/dashboard/c... | production | orphan |
| 178 | src/zephyr/infrastructure/db/__init__.py | src/zephyr/infrastructure/db/__init__.py | production | draft |
| 179 | src/zephyr/infrastructure/db/atomic_transaction_manager.py | src/zephyr/infrastructure/db/atomic_t... | production | draft |
| 180 | src/zephyr/infrastructure/db/audit_schema.py | src/zephyr/infrastructure/db/audit_sc... | production | draft |
| 181 | src/zephyr/infrastructure/db/base_repo.py | src/zephyr/infrastructure/db/base_rep... | production | draft |
| 182 | src/zephyr/infrastructure/db/circuit_breaker_repo.py | src/zephyr/infrastructure/db/circuit_... | production | draft |
| 183 | src/zephyr/infrastructure/db/circuit_breaker_types.py | src/zephyr/infrastructure/db/circuit_... | production | draft |
| 184 | src/zephyr/infrastructure/db/database_manager.py | src/zephyr/infrastructure/db/database... | production | draft |
| 185 | src/zephyr/infrastructure/db/gate_repo.py | src/zephyr/infrastructure/db/gate_rep... | production | draft |
| 186 | src/zephyr/infrastructure/db/olap_engine.py | src/zephyr/infrastructure/db/olap_eng... | production | draft |
| 187 | src/zephyr/infrastructure/db/query.py | src/zephyr/infrastructure/db/query.py | production | draft |
| 188 | src/zephyr/infrastructure/db/query_metrics.py | src/zephyr/infrastructure/db/query_me... | production | draft |
| 189 | src/zephyr/infrastructure/db/sqlite_schema.py | src/zephyr/infrastructure/db/sqlite_s... | production | draft |
| 190 | src/zephyr/infrastructure/db/task_repo.py | src/zephyr/infrastructure/db/task_rep... | production | draft |
| 191 | src/zephyr/infrastructure/db/transition.py | src/zephyr/infrastructure/db/transiti... | production | draft |
| 192 | src/zephyr/infrastructure/dependency/__init__.py | src/zephyr/infrastructure/dependency/... | production | draft |
| 193 | src/zephyr/infrastructure/doc_guard_server.py | src/zephyr/infrastructure/doc_guard_s... | production | draft |
| 194 | src/zephyr/infrastructure/draft/__init__.py | src/zephyr/infrastructure/draft/__ini... | production | draft |
| 195 | src/zephyr/infrastructure/dry_run_simulator.py | src/zephyr/infrastructure/dry_run_sim... | production | draft |
| 196 | src/zephyr/infrastructure/error_codes.py | src/zephyr/infrastructure/error_codes.py | production | draft |
| 197 | src/zephyr/infrastructure/event_bus_upgrade.py | src/zephyr/infrastructure/event_bus_u... | production | draft |
| 198 | src/zephyr/infrastructure/event_store.py | src/zephyr/infrastructure/event_store.py | production | draft |
| 199 | src/zephyr/infrastructure/events/__init__.py | src/zephyr/infrastructure/events/__in... | production | draft |
| 200 | src/zephyr/infrastructure/events/event_store.py | src/zephyr/infrastructure/events/even... | production | draft |

> (仅显示前 200 个模块，共 415 个)

### 未分类 / Unclassified (309 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-INFRA-RUNTIME/A-Share Diffusion Model Data Augmentation... | A-Share Diffusion Model Data Augmenta... | design | design_only |
| 2 | D-INFRA-RUNTIME/AB Test Dependency Mapper AB测试依赖映射器 | AB Test Dependency Mapper AB测试依赖... | design | design_only |
| 3 | D-INFRA-RUNTIME/API Documentation Synchronizer API文档同步器 | API Documentation Synchronizer API文... | design | design_only |
| 4 | D-INFRA-RUNTIME/API Version Compatibility Detector API版... | API Version Compatibility Detector AP... | design | design_only |
| 5 | D-INFRA-RUNTIME/API Version Manager API版本管理器 | API Version Manager API版本管理器 | design | design_only |
| 6 | D-INFRA-RUNTIME/Alert Escalation Strategy Engine 告警升级... | Alert Escalation Strategy Engine 告警... | design | design_only |
| 7 | D-INFRA-RUNTIME/Alert Silence Manager 告警静默管理器 | Alert Silence Manager 告警静默管理器 | design | design_only |
| 8 | D-INFRA-RUNTIME/Alternative Data Source Expansion 另类数... | Alternative Data Source Expansion 另... | design | design_only |
| 9 | D-INFRA-RUNTIME/App 包装器 | App 包装器 | design | design_only |
| 10 | D-INFRA-RUNTIME/Application State Snapshotter 应用状态快照器 | Application State Snapshotter 应用状... | design | design_only |
| 11 | D-INFRA-RUNTIME/Architecture Compliance Checker 架构合规... | Architecture Compliance Checker 架构... | design | design_only |
| 12 | D-INFRA-RUNTIME/Architecture Evolution Planner 架构演进规... | Architecture Evolution Planner 架构演... | design | design_only |
| 13 | D-INFRA-RUNTIME/Architecture Recommendation Engine 架构推... | Architecture Recommendation Engine 架... | design | design_only |
| 14 | D-INFRA-RUNTIME/Automated Code Reviewer 自动代码审查器 | Automated Code Reviewer 自动代码审查器 | design | design_only |
| 15 | D-INFRA-RUNTIME/Bandwidth Optimizer 带宽优化 | Bandwidth Optimizer 带宽优化 | design | design_only |
| 16 | D-INFRA-RUNTIME/Base 基础 | Base 基础 | design | design_only |
| 17 | D-INFRA-RUNTIME/Batch Data Processor 批量数据处理器 | Batch Data Processor 批量数据处理器 | design | design_only |
| 18 | D-INFRA-RUNTIME/Blue-Green Dependency Mapper 蓝绿依赖映射器 | Blue-Green Dependency Mapper 蓝绿依赖... | design | design_only |
| 19 | D-INFRA-RUNTIME/Blueprint Code Sync 蓝图代码同步 | Blueprint Code Sync 蓝图代码同步 | design | design_only |
| 20 | D-INFRA-RUNTIME/CPU Core Allocation Manager CPU核心分配管... | CPU Core Allocation Manager CPU核心分... | design | design_only |
| 21 | D-INFRA-RUNTIME/Cache Data Preloader 缓存数据预加载器 | Cache Data Preloader 缓存数据预加载器 | design | design_only |
| 22 | D-INFRA-RUNTIME/Cache Warmup Manager 缓存预热管理器 | Cache Warmup Manager 缓存预热管理器 | design | design_only |
| 23 | D-INFRA-RUNTIME/Canary Dependency Mapper 金丝雀依赖映射器 | Canary Dependency Mapper 金丝雀依赖映... | design | design_only |
| 24 | D-INFRA-RUNTIME/Capacity Alert 容量告警 | Capacity Alert 容量告警 | design | design_only |
| 25 | D-INFRA-RUNTIME/CapacityThresholdBreached 容量阈值突破事件 | CapacityThresholdBreached 容量阈值突... | design | design_only |
| 26 | D-INFRA-RUNTIME/Causal ML 深度补充 因果ML深度补充 | Causal ML 深度补充 因果ML深度补充 | design | design_only |
| 27 | D-INFRA-RUNTIME/ChromaDB Vector Database ChromaDB向量数据库 | ChromaDB Vector Database ChromaDB向量... | design | design_only |
| 28 | D-INFRA-RUNTIME/Circular Dependency Detector 循环依赖检测器 | Circular Dependency Detector 循环依赖... | design | design_only |
| 29 | D-INFRA-RUNTIME/ClickHouse Database ClickHouse数据库 | ClickHouse Database ClickHouse数据库 | design | design_only |
| 30 | D-INFRA-RUNTIME/Clock Sync Service 时钟同步服务 | Clock Sync Service 时钟同步服务 | design | design_only |
| 31 | D-INFRA-RUNTIME/Code Change Impact Analyzer 代码变更影响... | Code Change Impact Analyzer 代码变更... | design | design_only |
| 32 | D-INFRA-RUNTIME/Code Complexity Analyzer 代码复杂度分析器 | Code Complexity Analyzer 代码复杂度分... | design | design_only |
| 33 | D-INFRA-RUNTIME/Code Duplication Detector 代码重复检测器 | Code Duplication Detector 代码重复检测器 | design | design_only |
| 34 | D-INFRA-RUNTIME/Code Security Static Analyzer 代码安全静... | Code Security Static Analyzer 代码安... | design | design_only |
| 35 | D-INFRA-RUNTIME/Code Standard Enforcer 代码规范强制执行器 | Code Standard Enforcer 代码规范强制执... | design | design_only |
| 36 | D-INFRA-RUNTIME/Code Structure Visualizer 代码结构可视化器 | Code Structure Visualizer 代码结构可... | design | design_only |
| 37 | D-INFRA-RUNTIME/Code Template Engine 代码模板引擎 | Code Template Engine 代码模板引擎 | design | design_only |
| 38 | D-INFRA-RUNTIME/Cold Start Optimizer 冷启动优化器 | Cold Start Optimizer 冷启动优化器 | design | design_only |
| 39 | D-INFRA-RUNTIME/Cold Storage 冷存储 | Cold Storage 冷存储 | design | design_only |
| 40 | D-INFRA-RUNTIME/Cold平面 冷平面 | Cold平面 冷平面 | design | design_only |
| 41 | D-INFRA-RUNTIME/Communication Protocol Adapter 通信协议适... | Communication Protocol Adapter 通信协... | design | design_only |
| 42 | D-INFRA-RUNTIME/ConfigManager 配置管理器 | ConfigManager 配置管理器 | design | design_only |
| 43 | D-INFRA-RUNTIME/Configuration Change Notifier 配置变更通知器 | Configuration Change Notifier 配置变... | design | design_only |
| 44 | D-INFRA-RUNTIME/Configuration Code Generator 配置代码生成器 | Configuration Code Generator 配置代码... | design | design_only |
| 45 | D-INFRA-RUNTIME/Configuration Dependency Mapper 配置依赖... | Configuration Dependency Mapper 配置... | design | design_only |
| 46 | D-INFRA-RUNTIME/Configuration Diff Detector 配置差异检测器 | Configuration Diff Detector 配置差异... | design | design_only |
| 47 | D-INFRA-RUNTIME/Configuration Encryption Manager 配置加密... | Configuration Encryption Manager 配置... | design | design_only |
| 48 | D-INFRA-RUNTIME/Configuration Hot Update Engine 配置热更... | Configuration Hot Update Engine 配置... | design | design_only |
| 49 | D-INFRA-RUNTIME/Configuration Manager 配置管理器 | Configuration Manager 配置管理器 | design | design_only |
| 50 | D-INFRA-RUNTIME/Configuration Merge Engine 配置合并引擎 | Configuration Merge Engine 配置合并引擎 | design | design_only |
| 51 | D-INFRA-RUNTIME/Configuration Validation Engine 配置校验引擎 | Configuration Validation Engine 配置... | design | design_only |
| 52 | D-INFRA-RUNTIME/Configuration Version Management & Rollba... | Configuration Version Management & Ro... | design | design_only |
| 53 | D-INFRA-RUNTIME/Conformal Prediction 共形预测 | Conformal Prediction 共形预测 | design | design_only |
| 54 | D-INFRA-RUNTIME/Connection Pool Manager 连接池管理器 | Connection Pool Manager 连接池管理器 | design | design_only |
| 55 | D-INFRA-RUNTIME/Container Image Cache Manager 容器镜像缓... | Container Image Cache Manager 容器镜... | design | design_only |
| 56 | D-INFRA-RUNTIME/Container Orchestrator 容器编排器 | Container Orchestrator 容器编排器 | design | design_only |
| 57 | D-INFRA-RUNTIME/Container Resource Isolator 容器资源隔离器 | Container Resource Isolator 容器资源... | design | design_only |
| 58 | D-INFRA-RUNTIME/Continuous Improvement Engine 持续改进引擎 | Continuous Improvement Engine 持续改... | design | design_only |
| 59 | D-INFRA-RUNTIME/Conversation Context Compressor 对话上下... | Conversation Context Compressor 对话... | design | design_only |
| 60 | D-INFRA-RUNTIME/Cross-Module Interface Registry 跨模块接... | Cross-Module Interface Registry 跨模... | design | design_only |
| 61 | D-INFRA-RUNTIME/Cross-Origin Resource Sharing Manager 跨... | Cross-Origin Resource Sharing Manager... | design | design_only |
| 62 | D-INFRA-RUNTIME/Cross-Phase State Propagator 跨阶段状态传... | Cross-Phase State Propagator 跨阶段状... | design | design_only |
| 63 | D-INFRA-RUNTIME/Cybersecurity Shield 网络安全防护组件 | Cybersecurity Shield 网络安全防护组件 | design | design_only |
| 64 | D-INFRA-RUNTIME/D-INFRA | D-INFRA | design | design_only |
| 65 | D-INFRA-RUNTIME/D-INFRA-RUNTIME | D-INFRA-RUNTIME | design | design_only |
| 66 | D-INFRA-RUNTIME/DAO Layer Code Generator DAO层代码生成器 | DAO Layer Code Generator DAO层代码生成器 | design | design_only |
| 67 | D-INFRA-RUNTIME/Data Aggregation View Manager 数据聚合视... | Data Aggregation View Manager 数据聚... | design | design_only |
| 68 | D-INFRA-RUNTIME/Data Buffer Pool Manager 数据缓冲池管理器 | Data Buffer Pool Manager 数据缓冲池管... | design | design_only |
| 69 | D-INFRA-RUNTIME/Data Compression Manager 数据压缩管理器 | Data Compression Manager 数据压缩管理器 | design | design_only |
| 70 | D-INFRA-RUNTIME/Data Format Version Coordinator 数据格式... | Data Format Version Coordinator 数据... | design | design_only |
| 71 | D-INFRA-RUNTIME/Data Migration Script Generator 数据迁移... | Data Migration Script Generator 数据... | design | design_only |
| 72 | D-INFRA-RUNTIME/Data Model Generator 数据模型生成器 | Data Model Generator 数据模型生成器 | design | design_only |
| 73 | D-INFRA-RUNTIME/Data Source Star Rating Dynamic Updater ... | Data Source Star Rating Dynamic Updat... | design | design_only |
| 74 | D-INFRA-RUNTIME/Data Sovereignty Manager 数据主权管理器 | Data Sovereignty Manager 数据主权管理器 | design | design_only |
| 75 | D-INFRA-RUNTIME/Data Transfer Validator 数据传输校验器 | Data Transfer Validator 数据传输校验器 | design | design_only |
| 76 | D-INFRA-RUNTIME/Data Transformation Performance Optimizer... | Data Transformation Performance Optim... | design | design_only |
| 77 | D-INFRA-RUNTIME/Data Transformation Pipeline Orchestrator... | Data Transformation Pipeline Orchestr... | design | design_only |
| 78 | D-INFRA-RUNTIME/Database Layer 数据库层 | Database Layer 数据库层 | design | design_only |
| 79 | D-INFRA-RUNTIME/Database Schema Synchronizer 数据库Schema... | Database Schema Synchronizer 数据库Sc... | design | design_only |
| 80 | D-INFRA-RUNTIME/DegradationTriggered 降级触发事件 | DegradationTriggered 降级触发事件 | design | design_only |
| 81 | D-INFRA-RUNTIME/Deliverable Version Tracker 交付物版本追踪器 | Deliverable Version Tracker 交付物版... | design | design_only |
| 82 | D-INFRA-RUNTIME/Dependency Conflict Resolver 依赖冲突解决器 | Dependency Conflict Resolver 依赖冲突... | design | design_only |
| 83 | D-INFRA-RUNTIME/Dependency Graph Visualization Renderer ... | Dependency Graph Visualization Render... | design | design_only |
| 84 | D-INFRA-RUNTIME/Dependency Security Vulnerability Scanner... | Dependency Security Vulnerability Sca... | design | design_only |
| 85 | D-INFRA-RUNTIME/Dependency Upgrade Compatibility Checker ... | Dependency Upgrade Compatibility Chec... | design | design_only |
| 86 | D-INFRA-RUNTIME/Dependency Version Lock Manager 依赖版本... | Dependency Version Lock Manager 依赖... | design | design_only |
| 87 | D-INFRA-RUNTIME/Dependency Visualizer 依赖可视化器 | Dependency Visualizer 依赖可视化器 | design | design_only |
| 88 | D-INFRA-RUNTIME/Deployment Topology Manager 部署拓扑管理器 | Deployment Topology Manager 部署拓扑... | design | design_only |
| 89 | D-INFRA-RUNTIME/Development Plan Visualizer 开发计划可视化器 | Development Plan Visualizer 开发计划... | design | design_only |
| 90 | D-INFRA-RUNTIME/Distributed Lock Manager 分布式锁管理器 | Distributed Lock Manager 分布式锁管理器 | design | design_only |
| 91 | D-INFRA-RUNTIME/Document Link Validator 文档链接验证器 | Document Link Validator 文档链接验证器 | design | design_only |
| 92 | D-INFRA-RUNTIME/Document Search Indexer 文档搜索索引器 | Document Search Indexer 文档搜索索引器 | design | design_only |
| 93 | D-INFRA-RUNTIME/Document Template Engine 文档模板引擎 | Document Template Engine 文档模板引擎 | design | design_only |
| 94 | D-INFRA-RUNTIME/Document Version Manager 文档版本管理器 | Document Version Manager 文档版本管理器 | design | design_only |
| 95 | D-INFRA-RUNTIME/Domain-Driven Design Validator 领域驱动设... | Domain-Driven Design Validator 领域驱... | design | design_only |
| 96 | D-INFRA-RUNTIME/DuckDB Database DuckDB数据库 | DuckDB Database DuckDB数据库 | design | design_only |
| 97 | D-INFRA-RUNTIME/Elastic Scaling Manager 弹性伸缩管理器 | Elastic Scaling Manager 弹性伸缩管理器 | design | design_only |
| 98 | D-INFRA-RUNTIME/Endpoint Response Format Validator 端点响... | Endpoint Response Format Validator 端... | design | design_only |
| 99 | D-INFRA-RUNTIME/Environment Configuration Layering Manage... | Environment Configuration Layering Ma... | design | design_only |
| 100 | D-INFRA-RUNTIME/Environment Manager 环境管理 | Environment Manager 环境管理 | design | design_only |
| 101 | D-INFRA-RUNTIME/Environment Variable Manager 环境变量管理器 | Environment Variable Manager 环境变量... | design | design_only |
| 102 | D-INFRA-RUNTIME/Error Handling Code Generator 错误处理代... | Error Handling Code Generator 错误处... | design | design_only |
| 103 | D-INFRA-RUNTIME/EventBus 事件总线 | EventBus 事件总线 | design | design_only |
| 104 | D-INFRA-RUNTIME/EventStoreDB Event Store EventStoreDB事件... | EventStoreDB Event Store EventStoreDB... | design | design_only |
| 105 | D-INFRA-RUNTIME/Experiment and Resilience Testing 实验与... | Experiment and Resilience Testing 实... | design | design_only |
| 106 | D-INFRA-RUNTIME/FAISS Vector Search FAISS向量检索 | FAISS Vector Search FAISS向量检索 | design | design_only |
| 107 | D-INFRA-RUNTIME/Factor Warmup Manager 因子预热管理器 | Factor Warmup Manager 因子预热管理器 | design | design_only |
| 108 | D-INFRA-RUNTIME/Failover Coordinator 故障转移协调器 | Failover Coordinator 故障转移协调器 | design | design_only |
| 109 | D-INFRA-RUNTIME/Faiss GPU Vector Search Faiss GPU向量搜索 | Faiss GPU Vector Search Faiss GPU向量... | design | design_only |
| 110 | D-INFRA-RUNTIME/Feature Drift & Concept Drift Detection ... | Feature Drift & Concept Drift Detecti... | design | design_only |
| 111 | D-INFRA-RUNTIME/Feature Lifecycle Manager 功能生命周期管理器 | Feature Lifecycle Manager 功能生命周... | design | design_only |
| 112 | D-INFRA-RUNTIME/Field Mapping Converter 字段映射转换器 | Field Mapping Converter 字段映射转换器 | design | design_only |
| 113 | D-INFRA-RUNTIME/Financial Time Series Data Augmentation ... | Financial Time Series Data Augmentati... | design | design_only |
| 114 | D-INFRA-RUNTIME/GPU Compute Pipeline Manager GPU计算管线... | GPU Compute Pipeline Manager GPU计算... | design | design_only |
| 115 | D-INFRA-RUNTIME/GPU Inference Training Dynamic Allocator ... | GPU Inference Training Dynamic Alloca... | design | design_only |
| 116 | D-INFRA-RUNTIME/GPU Kernel Launch Optimizer GPU内核启动优... | GPU Kernel Launch Optimizer GPU内核启... | design | design_only |
| 117 | D-INFRA-RUNTIME/GPU MPS多进程并发 GPU Multi-Process Service | GPU MPS多进程并发 GPU Multi-Process S... | design | design_only |
| 118 | D-INFRA-RUNTIME/GPU Memory Transfer Optimizer GPU内存传输... | GPU Memory Transfer Optimizer GPU内存... | design | design_only |
| 119 | D-INFRA-RUNTIME/GPU Programming Abstraction Layer GPU编程... | GPU Programming Abstraction Layer GPU... | design | design_only |
| 120 | D-INFRA-RUNTIME/GPU Resource Monitor GPU资源监控器 | GPU Resource Monitor GPU资源监控器 | design | design_only |
| 121 | D-INFRA-RUNTIME/GPU Scheduler GPU调度器 | GPU Scheduler GPU调度器 | design | design_only |
| 122 | D-INFRA-RUNTIME/GPUOOMDetected GPU OOM检测事件 | GPUOOMDetected GPU OOM检测事件 | design | design_only |
| 123 | D-INFRA-RUNTIME/GPU调度上岗+热交换 GPU调度 | GPU调度上岗+热交换 GPU调度 | design | design_only |
| 124 | D-INFRA-RUNTIME/GPU调度层 GPU调度 | GPU调度层 GPU调度 | design | design_only |
| 125 | D-INFRA-RUNTIME/Global Dependency Graph Calculator 全局依... | Global Dependency Graph Calculator 全... | design | design_only |
| 126 | D-INFRA-RUNTIME/Governance Adapter 治理适配器 | Governance Adapter 治理适配器 | design | design_only |
| 127 | D-INFRA-RUNTIME/Governance Protocol 治理协议 | Governance Protocol 治理协议 | design | design_only |
| 128 | D-INFRA-RUNTIME/Graceful Shutdown Coordinator 优雅关闭协调器 | Graceful Shutdown Coordinator 优雅关... | design | design_only |
| 129 | D-INFRA-RUNTIME/Graph Neural Network for Stock Relations ... | Graph Neural Network for Stock Relati... | design | design_only |
| 130 | D-INFRA-RUNTIME/Hardware Accelerator 硬件加速器 | Hardware Accelerator 硬件加速器 | design | design_only |
| 131 | D-INFRA-RUNTIME/High Performance HA Framework 高性能高可... | High Performance HA Framework 高性能... | design | design_only |
| 132 | D-INFRA-RUNTIME/Hot Storage 热存储 | Hot Storage 热存储 | design | design_only |
| 133 | D-INFRA-RUNTIME/Hot↔Warm必须通过IPC协议通信 Hot-Warm IPC... | Hot↔Warm必须通过IPC协议通信 Hot-Warm... | design | design_only |
| 134 | D-INFRA-RUNTIME/Hot平面 热平面 | Hot平面 热平面 | design | design_only |
| 135 | D-INFRA-RUNTIME/Inference Engine Warmer 推理引擎预热器 | Inference Engine Warmer 推理引擎预热器 | design | design_only |
| 136 | D-INFRA-RUNTIME/Infrastructure Status 基础设施状态 | Infrastructure Status 基础设施状态 | design | design_only |
| 137 | D-INFRA-RUNTIME/Infrastructure Topology Visualizer 基础设... | Infrastructure Topology Visualizer 基... | design | design_only |
| 138 | D-INFRA-RUNTIME/InfrastructureAlert 基础设施告警 | InfrastructureAlert 基础设施告警 | design | design_only |
| 139 | D-INFRA-RUNTIME/InfrastructureNode 基础设施节点 | InfrastructureNode 基础设施节点 | design | design_only |
| 140 | D-INFRA-RUNTIME/Inter-Layer Data Format Converter & Valid... | Inter-Layer Data Format Converter & V... | design | design_only |
| 141 | D-INFRA-RUNTIME/Inter-Module Communication Protocol Manag... | Inter-Module Communication Protocol M... | design | design_only |
| 142 | D-INFRA-RUNTIME/Inter-Process Communication Manager 进程... | Inter-Process Communication Manager ... | design | design_only |
| 143 | D-INFRA-RUNTIME/Interface Mock Generator 接口Mock生成器 | Interface Mock Generator 接口Mock生成器 | design | design_only |
| 144 | D-INFRA-RUNTIME/Iteration Cycle Tracker 迭代周期追踪器 | Iteration Cycle Tracker 迭代周期追踪器 | design | design_only |
| 145 | D-INFRA-RUNTIME/Kafka Message Queue Kafka消息队列 | Kafka Message Queue Kafka消息队列 | design | design_only |
| 146 | D-INFRA-RUNTIME/Knowledge Base Data Sovereignty 知识库数... | Knowledge Base Data Sovereignty 知识... | design | design_only |
| 147 | D-INFRA-RUNTIME/Knowledge Base Indexer 知识库索引器 | Knowledge Base Indexer 知识库索引器 | design | design_only |
| 148 | D-INFRA-RUNTIME/LLM Agent for Fundamental Analysis 大语言... | LLM Agent for Fundamental Analysis 大... | design | design_only |
| 149 | D-INFRA-RUNTIME/Learning System Bridge Declaration 学习系... | Learning System Bridge Declaration 学... | design | design_only |
| 150 | D-INFRA-RUNTIME/Live Data to Research Domain Feedback Cha... | Live Data to Research Domain Feedback... | design | design_only |
| 151 | D-INFRA-RUNTIME/Load Balancing Strategy Engine 负载均衡策... | Load Balancing Strategy Engine 负载均... | design | design_only |
| 152 | D-INFRA-RUNTIME/Local First Architecture 本地优先架构 | Local First Architecture 本地优先架构 | design | design_only |
| 153 | D-INFRA-RUNTIME/MCP Sentinel System Monitor MCP哨兵系统监... | MCP Sentinel System Monitor MCP哨兵系... | design | design_only |
| 154 | D-INFRA-RUNTIME/Mamba/SSM State Space Model Mamba/SSM状态... | Mamba/SSM State Space Model Mamba/SSM... | design | design_only |
| 155 | D-INFRA-RUNTIME/Market Microstructure Deep Modeling 市场... | Market Microstructure Deep Modeling ... | design | design_only |
| 156 | D-INFRA-RUNTIME/Message Queue Manager 消息队列管理器 | Message Queue Manager 消息队列管理器 | design | design_only |
| 157 | D-INFRA-RUNTIME/Message Queue 消息队列 | Message Queue 消息队列 | design | design_only |
| 158 | D-INFRA-RUNTIME/Metric Anomaly Detector 指标异常检测器 | Metric Anomaly Detector 指标异常检测器 | design | design_only |
| 159 | D-INFRA-RUNTIME/Milestone Dependency Validator 里程碑依赖... | Milestone Dependency Validator 里程碑... | design | design_only |
| 160 | D-INFRA-RUNTIME/MinIO Object Storage MinIO对象存储 | MinIO Object Storage MinIO对象存储 | design | design_only |
| 161 | D-INFRA-RUNTIME/Model Registry & Experiment Management 模... | Model Registry & Experiment Managemen... | design | design_only |
| 162 | D-INFRA-RUNTIME/Model Warmup Manager 模型预热管理器 | Model Warmup Manager 模型预热管理器 | design | design_only |
| 163 | D-INFRA-RUNTIME/Module Configuration Aggregator 模块配置... | Module Configuration Aggregator 模块... | design | design_only |
| 164 | D-INFRA-RUNTIME/Module Dependency Injector 模块依赖注入器 | Module Dependency Injector 模块依赖注... | design | design_only |
| 165 | D-INFRA-RUNTIME/Module Documentation Indexer 模块文档索引器 | Module Documentation Indexer 模块文档... | design | design_only |
| 166 | D-INFRA-RUNTIME/Module Exception Boundary Manager 模块异... | Module Exception Boundary Manager 模... | design | design_only |
| 167 | D-INFRA-RUNTIME/Module Feature Toggle Manager 模块功能开... | Module Feature Toggle Manager 模块功... | design | design_only |
| 168 | D-INFRA-RUNTIME/Module Health Checker 模块健康检查器 | Module Health Checker 模块健康检查器 | design | design_only |
| 169 | D-INFRA-RUNTIME/Module Hot Update Manager 模块热更新管理器 | Module Hot Update Manager 模块热更新... | design | design_only |
| 170 | D-INFRA-RUNTIME/Module Interface Contract Manager 模块接... | Module Interface Contract Manager 模... | design | design_only |
| 171 | D-INFRA-RUNTIME/Module Lifecycle Manager 模块生命周期管理器 | Module Lifecycle Manager 模块生命周期... | design | design_only |
| 172 | D-INFRA-RUNTIME/Module Log Aggregator 模块日志聚合器 | Module Log Aggregator 模块日志聚合器 | design | design_only |
| 173 | D-INFRA-RUNTIME/Module Metrics Collector 模块度量采集器 | Module Metrics Collector 模块度量采集器 | design | design_only |
| 174 | D-INFRA-RUNTIME/Module Performance Profiler 模块性能分析器 | Module Performance Profiler 模块性能... | design | design_only |
| 175 | D-INFRA-RUNTIME/Module Registry 模块注册中心 | Module Registry 模块注册中心 | design | design_only |
| 176 | D-INFRA-RUNTIME/Module Sandbox Isolator 模块沙箱隔离器 | Module Sandbox Isolator 模块沙箱隔离器 | design | design_only |
| 177 | D-INFRA-RUNTIME/Module Test Runner 模块测试运行器 | Module Test Runner 模块测试运行器 | design | design_only |
| 178 | D-INFRA-RUNTIME/Module Version Dependency Resolver 模块版... | Module Version Dependency Resolver 模... | design | design_only |
| 179 | D-INFRA-RUNTIME/Monitoring Dashboard Process 监控面板进程 | Monitoring Dashboard Process 监控面板... | design | design_only |
| 180 | D-INFRA-RUNTIME/Monitoring Data Aggregator 监控数据聚合器 | Monitoring Data Aggregator 监控数据聚... | design | design_only |
| 181 | D-INFRA-RUNTIME/Multi-Device State Coordinator 多端状态协... | Multi-Device State Coordinator 多端状... | design | design_only |
| 182 | D-INFRA-RUNTIME/Multi-Modal Input Router 多模态输入路由 | Multi-Modal Input Router 多模态输入路由 | design | design_only |
| 183 | D-INFRA-RUNTIME/Multi-Process Isolation & Runtime Archite... | Multi-Process Isolation & Runtime Arc... | design | design_only |
| 184 | D-INFRA-RUNTIME/Multi-Protocol Network Adapter 多协议网络... | Multi-Protocol Network Adapter 多协议... | design | design_only |
| 185 | D-INFRA-RUNTIME/Multi-Region Collaboration Manager 多区域... | Multi-Region Collaboration Manager 多... | design | design_only |
| 186 | D-INFRA-RUNTIME/NAS Storage NAS存储 | NAS Storage NAS存储 | design | design_only |
| 187 | D-INFRA-RUNTIME/NSSM+自研Supervisor 进程守护层 | NSSM+自研Supervisor 进程守护层 | design | design_only |
| 188 | D-INFRA-RUNTIME/NSSM注册Windows服务 NSSM Windows Service | NSSM注册Windows服务 NSSM Windows Service | design | design_only |
| 189 | D-INFRA-RUNTIME/Network Policy Manager 网络策略管理器 | Network Policy Manager 网络策略管理器 | design | design_only |
| 190 | D-INFRA-RUNTIME/Node Return Type Contractor 节点返回值类... | Node Return Type Contractor 节点返回... | design | design_only |
| 191 | D-INFRA-RUNTIME/P3 Process Specification P3进程规格 | P3 Process Specification P3进程规格 | design | design_only |
| 192 | D-INFRA-RUNTIME/Package Dependency Graph Generator 包依赖... | Package Dependency Graph Generator 包... | design | design_only |
| 193 | D-INFRA-RUNTIME/Panel Layout Engine 面板布局引擎 | Panel Layout Engine 面板布局引擎 | design | design_only |
| 194 | D-INFRA-RUNTIME/Parquet Columnar Storage Parquet列式存储 | Parquet Columnar Storage Parquet列式存储 | design | design_only |
| 195 | D-INFRA-RUNTIME/Parquet Parquet列式存储格式 | Parquet Parquet列式存储格式 | design | design_only |
| 196 | D-INFRA-RUNTIME/Path Resolver 路径解析 | Path Resolver 路径解析 | design | design_only |
| 197 | D-INFRA-RUNTIME/Phase Retrospective Analyzer 阶段回顾分析器 | Phase Retrospective Analyzer 阶段回顾... | design | design_only |
| 198 | D-INFRA-RUNTIME/Phase Synchronization Coordinator 阶段同... | Phase Synchronization Coordinator 阶... | design | design_only |
| 199 | D-INFRA-RUNTIME/Plugin System Manager 插件系统管理器 | Plugin System Manager 插件系统管理器 | design | design_only |
| 200 | D-INFRA-RUNTIME/Policy Conflict Auto Detector 策略冲突自... | Policy Conflict Auto Detector 策略冲... | design | design_only |

> (仅显示前 200 个模块，共 309 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 674 条 / 674 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 674 条 / 674 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 529 条 / edges                               │
│   [config_depends]: 112 条 / edges                               │
│   [event]: 14 条 / edges                                         │
│   [contract]: 7 条 / edges                                       │
│   [data]: 7 条 / edges                                           │
│   [runtime]: 5 条 / edges                                        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (529 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   blueprint_search_server.py → __init__.py                       │
│   doc_guard_server.py → __init__.py                              │
│   gateway_server.py → __init__.py                                │
│   knowledge_base_server.py → __init__.py                         │
│   gate_engine_server.py → __init__.py                            │
│   sentinel_server.py → __init__.py                               │
│   vector_memory_server.py → __init__.py                          │
│   sandbox_server.py → __init__.py                                │
│   warm_hot_gate.py → __init__.py                                 │
│   a2a_card_registry.py → a2a_registry.py                         │
│   _base_server.py → __init__.py                                  │
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
│   a2a_red_team.py → __init__.py                                  │
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
│   __init__.py → __init__.py                                      │
│   _intelligence.py → a2a_blame_attribution.py                    │
│   _intelligence.py → a2a_behavior_fingerprint.py                 │
│   _intelligence.py → a2a_collusion_detector.py                   │
│   _intelligence.py → a2a_causal_trace.py                         │
│   _intelligence.py → a2a_cross_agent_semantic_...                │
│   _intelligence.py → a2a_knowledge_distill.py                    │
│   _intelligence.py → a2a_latent_comm.py                          │
│   ...还有 480 条 / 480 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (112 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (14 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (7 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 674 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `02_d_infra_runtime_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
