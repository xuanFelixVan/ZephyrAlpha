---
doc_type: domain_architecture_diagram
title: D-AUTONOMY_CORE 自治核心架构图
version: "1.0"
status: active
date: 2026-06-24
owner: auto-generator
ttl: permanent
---

# 09_d_autonomy_core / 自治核心 架构图

> **文档作用 / Purpose**: 以ASCII art可视化展示自治核心（D-AUTONOMY_CORE）功能域的模块分层架构和依赖关系。

> 本文档由 generate_domain_architecture_diagram.py 从 depgraph.db 自动生成
> 最后更新 / Last Updated: 2026-06-24 23:57:37
> 数据源 / Data Source: depgraph.db nodes表 + edges表

## 架构全景图 / Architecture Overview

> 按 architecture_layer 分层显示 自治核心（D-AUTONOMY_CORE）的模块分布。共 654 个模块 / 654 modules。

```

┌──────────────────────────────────────────────────────────────────┐
│            L1 基础层 / Foundation Layer (175 modules)            │
├──────────────────────────────────────────────────────────────────┤
│   src/zephyr/autonomy_core/__init__.py  [production]             │
│   src/zephyr/autonomy_core/__init___from_orches.py  [prototype]  │
│   src/zephyr/autonomy_core/__main__.py  [prototype]              │
│   src/zephyr/autonomy_core/_extensions/__init__.py  [scaffold... │
│   src/zephyr/autonomy_core/_infrastructure.py  [prototype]       │
│   src/zephyr/autonomy_core/_injection.py  [prototype]            │
│   src/zephyr/autonomy_core/_pipeline.py  [prototype]             │
│   src/zephyr/autonomy_core/_safety.py  [prototype]               │
│   src/zephyr/autonomy_core/adversarial_robustness.py  [protot... │
│   src/zephyr/autonomy_core/agent_observability.py  [prototype]   │
│   src/zephyr/autonomy_core/alignment_scorer.py  [prototype]      │
│   src/zephyr/autonomy_core/all_skill_modules.py  [prototype]     │
│   src/zephyr/autonomy_core/api/__init__.py  [scaffold_placeho... │
│   src/zephyr/autonomy_core/architecture_context_loader.py  [p... │
│   src/zephyr/autonomy_core/assembly/__init__.py  [prototype]     │
│   src/zephyr/autonomy_core/assembly/context_assembler.py  [pr... │
│   src/zephyr/autonomy_core/assembly/context_injector.py  [pro... │
│   src/zephyr/autonomy_core/assembly/context_pipeline.py  [pro... │
│   ...还有 157 个模块 / 157 more modules                          │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               L2 领域层 / Domain Layer (2 modules)               │
├──────────────────────────────────────────────────────────────────┤
│   ChromaDB Runtime Validator  [design]                           │
│   Memory Provenance Enforcer  [design]                           │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│               未分类 / Unclassified (477 modules)                │
├──────────────────────────────────────────────────────────────────┤
│   11 Agents Full MVP 11个Agent全部MVP实现  [design]              │
│   8-Collection Unified Schema Manager 8大Collection统一Schema... │
│   A2A Check A2A检查  [design]                                    │
│   A2A Check Gateway A2A检查网关  [design]                        │
│   A2A Check Gateway Policy Engine A2A检查网关策略引擎  [design]  │
│   A2A Check Non-Bypassable A2A检查不可绕过  [design]             │
│   A2A Check Protocol A2A检查协议  [design]                       │
│   A2A Communication Agent间通信  [design]                        │
│   A2A Protocol A2A协议  [design]                                 │
│   ABAC策略 ABAC Policy  [design]                                 │
│   AGENTICAITA AGENTICAITA框架  [design]                          │
│   AI 人工智能  [design]                                          │
│   AI 治理执行者角色  [design]                                    │
│   AISI 2026报告  [design]                                        │
│   AI自主执行率阈值 AI Autonomous Execution Rate Threshold  [d... │
│   AI自治行为审计 AI Autonomous Behavior Audit  [design]          │
│   AI自治运维是闭环而非开环 Closed-Loop Autonomy  [design]        │
│   AI自治运维闭环 AI自治运维  [design]                            │
│   ...还有 459 个模块 / 459 more modules                          │
└──────────────────────────────────────────────────────────────────┘

```

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 654 个模块 / 654 modules）。

### L1 基础层 / Foundation Layer (175 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/autonomy_core/__init__.py | src/zephyr/autonomy_core/__init__.py | production | draft |
| 2 | src/zephyr/autonomy_core/__init___from_orches.py | src/zephyr/autonomy_core/__init___fro... | prototype | draft |
| 3 | src/zephyr/autonomy_core/__main__.py | src/zephyr/autonomy_core/__main__.py | prototype | draft |
| 4 | src/zephyr/autonomy_core/_extensions/__init__.py | src/zephyr/autonomy_core/_extensions/... | scaffold_placeholder | orphan |
| 5 | src/zephyr/autonomy_core/_infrastructure.py | src/zephyr/autonomy_core/_infrastruct... | prototype | draft |
| 6 | src/zephyr/autonomy_core/_injection.py | src/zephyr/autonomy_core/_injection.py | prototype | draft |
| 7 | src/zephyr/autonomy_core/_pipeline.py | src/zephyr/autonomy_core/_pipeline.py | prototype | draft |
| 8 | src/zephyr/autonomy_core/_safety.py | src/zephyr/autonomy_core/_safety.py | prototype | draft |
| 9 | src/zephyr/autonomy_core/adversarial_robustness.py | src/zephyr/autonomy_core/adversarial_... | prototype | draft |
| 10 | src/zephyr/autonomy_core/agent_observability.py | src/zephyr/autonomy_core/agent_observ... | prototype | draft |
| 11 | src/zephyr/autonomy_core/alignment_scorer.py | src/zephyr/autonomy_core/alignment_sc... | prototype | draft |
| 12 | src/zephyr/autonomy_core/all_skill_modules.py | src/zephyr/autonomy_core/all_skill_mo... | prototype | draft |
| 13 | src/zephyr/autonomy_core/api/__init__.py | src/zephyr/autonomy_core/api/__init__.py | scaffold_placeholder | orphan |
| 14 | src/zephyr/autonomy_core/architecture_context_loader.py | src/zephyr/autonomy_core/architecture... | prototype | draft |
| 15 | src/zephyr/autonomy_core/assembly/__init__.py | src/zephyr/autonomy_core/assembly/__i... | prototype | draft |
| 16 | src/zephyr/autonomy_core/assembly/context_assembler.py | src/zephyr/autonomy_core/assembly/con... | prototype | draft |
| 17 | src/zephyr/autonomy_core/assembly/context_injector.py | src/zephyr/autonomy_core/assembly/con... | prototype | draft |
| 18 | src/zephyr/autonomy_core/assembly/context_pipeline.py | src/zephyr/autonomy_core/assembly/con... | prototype | draft |
| 19 | src/zephyr/autonomy_core/atomic_injector.py | src/zephyr/autonomy_core/atomic_injec... | prototype | draft |
| 20 | src/zephyr/autonomy_core/budget_forecaster.py | src/zephyr/autonomy_core/budget_forec... | prototype | draft |
| 21 | src/zephyr/autonomy_core/cache_invalidation.py | src/zephyr/autonomy_core/cache_invali... | prototype | draft |
| 22 | src/zephyr/autonomy_core/ce_bootstrap.py | src/zephyr/autonomy_core/ce_bootstrap.py | prototype | draft |
| 23 | src/zephyr/autonomy_core/ce_explain_cli.py | src/zephyr/autonomy_core/ce_explain_c... | prototype | draft |
| 24 | src/zephyr/autonomy_core/ce_playground_v2.py | src/zephyr/autonomy_core/ce_playgroun... | prototype | draft |
| 25 | src/zephyr/autonomy_core/ce_vibe_shortcuts.py | src/zephyr/autonomy_core/ce_vibe_shor... | prototype | draft |
| 26 | src/zephyr/autonomy_core/checkpoint_manager.py | src/zephyr/autonomy_core/checkpoint_m... | prototype | draft |
| 27 | src/zephyr/autonomy_core/citation_walker.py | src/zephyr/autonomy_core/citation_wal... | prototype | draft |
| 28 | src/zephyr/autonomy_core/cold_start_booster.py | src/zephyr/autonomy_core/cold_start_b... | prototype | draft |
| 29 | src/zephyr/autonomy_core/complexity_budget.py | src/zephyr/autonomy_core/complexity_b... | prototype | draft |
| 30 | src/zephyr/autonomy_core/config_safety_guard.py | src/zephyr/autonomy_core/config_safet... | prototype | draft |
| 31 | src/zephyr/autonomy_core/context_assembler.py | src/zephyr/autonomy_core/context_asse... | prototype | draft |
| 32 | src/zephyr/autonomy_core/context_budget.py | src/zephyr/autonomy_core/context_budg... | prototype | draft |
| 33 | src/zephyr/autonomy_core/context_budget_tracker.py | src/zephyr/autonomy_core/context_budg... | prototype | draft |
| 34 | src/zephyr/autonomy_core/context_debt_score.py | src/zephyr/autonomy_core/context_debt... | prototype | draft |
| 35 | src/zephyr/autonomy_core/context_evaluator.py | src/zephyr/autonomy_core/context_eval... | prototype | draft |
| 36 | src/zephyr/autonomy_core/context_evictor.py | src/zephyr/autonomy_core/context_evic... | prototype | draft |
| 37 | src/zephyr/autonomy_core/context_health_score.py | src/zephyr/autonomy_core/context_heal... | prototype | draft |
| 38 | src/zephyr/autonomy_core/context_injector.py | src/zephyr/autonomy_core/context_inje... | prototype | draft |
| 39 | src/zephyr/autonomy_core/context_model_strategy.py | src/zephyr/autonomy_core/context_mode... | prototype | draft |
| 40 | src/zephyr/autonomy_core/context_optimizer.py | src/zephyr/autonomy_core/context_opti... | prototype | draft |
| 41 | src/zephyr/autonomy_core/context_outcome_tracker.py | src/zephyr/autonomy_core/context_outc... | prototype | draft |
| 42 | src/zephyr/autonomy_core/context_pipeline.py | src/zephyr/autonomy_core/context_pipe... | prototype | draft |
| 43 | src/zephyr/autonomy_core/context_playground.py | src/zephyr/autonomy_core/context_play... | prototype | draft |
| 44 | src/zephyr/autonomy_core/context_rot_model.py | src/zephyr/autonomy_core/context_rot_... | prototype | draft |
| 45 | src/zephyr/autonomy_core/context_rule_registry.py | src/zephyr/autonomy_core/context_rule... | prototype | draft |
| 46 | src/zephyr/autonomy_core/context_value_attribution.py | src/zephyr/autonomy_core/context_valu... | prototype | draft |
| 47 | src/zephyr/autonomy_core/contextual_fetch_api.py | src/zephyr/autonomy_core/contextual_f... | prototype | draft |
| 48 | src/zephyr/autonomy_core/core/__init__.py | src/zephyr/autonomy_core/core/__init_... | scaffold_placeholder | orphan |
| 49 | src/zephyr/autonomy_core/curation_loop.py | src/zephyr/autonomy_core/curation_loo... | prototype | draft |
| 50 | src/zephyr/autonomy_core/dependency_tracker.py | src/zephyr/autonomy_core/dependency_t... | prototype | draft |
| 51 | src/zephyr/autonomy_core/diff_injector.py | src/zephyr/autonomy_core/diff_injecto... | prototype | draft |
| 52 | src/zephyr/autonomy_core/dispatch_table.py | src/zephyr/autonomy_core/dispatch_tab... | prototype | draft |
| 53 | src/zephyr/autonomy_core/diversity_constraint.py | src/zephyr/autonomy_core/diversity_co... | prototype | draft |
| 54 | src/zephyr/autonomy_core/doc_compressor.py | src/zephyr/autonomy_core/doc_compress... | prototype | draft |
| 55 | src/zephyr/autonomy_core/domain_decay_config.py | src/zephyr/autonomy_core/domain_decay... | prototype | draft |
| 56 | src/zephyr/autonomy_core/embedding_version_lock.py | src/zephyr/autonomy_core/embedding_ve... | prototype | draft |
| 57 | src/zephyr/autonomy_core/engine.py | src/zephyr/autonomy_core/engine.py | prototype | draft |
| 58 | src/zephyr/autonomy_core/fallback_staleness_gate.py | src/zephyr/autonomy_core/fallback_sta... | prototype | draft |
| 59 | src/zephyr/autonomy_core/file_autoregister.py | src/zephyr/autonomy_core/file_autoreg... | prototype | draft |
| 60 | src/zephyr/autonomy_core/file_autorregister.py | src/zephyr/autonomy_core/file_autorre... | prototype | draft |
| 61 | src/zephyr/autonomy_core/fragmentation_index.py | src/zephyr/autonomy_core/fragmentatio... | prototype | draft |
| 62 | src/zephyr/autonomy_core/host_resource_governor.py | src/zephyr/autonomy_core/host_resourc... | prototype | draft |
| 63 | src/zephyr/autonomy_core/ide_watcher.py | src/zephyr/autonomy_core/ide_watcher.py | prototype | draft |
| 64 | src/zephyr/autonomy_core/infrastructure/__init__.py | src/zephyr/autonomy_core/infrastructu... | scaffold_placeholder | orphan |
| 65 | src/zephyr/autonomy_core/integration/__init__.py | src/zephyr/autonomy_core/integration/... | prototype | draft |
| 66 | src/zephyr/autonomy_core/integration/pipeline_bridge.py | src/zephyr/autonomy_core/integration/... | prototype | draft |
| 67 | src/zephyr/autonomy_core/integrity_check.py | src/zephyr/autonomy_core/integrity_ch... | prototype | draft |
| 68 | src/zephyr/autonomy_core/intent_keyword_mapper.py | src/zephyr/autonomy_core/intent_keywo... | prototype | draft |
| 69 | src/zephyr/autonomy_core/intent_parser.py | src/zephyr/autonomy_core/intent_parse... | prototype | draft |
| 70 | src/zephyr/autonomy_core/kill_switch.py | src/zephyr/autonomy_core/kill_switch.py | prototype | draft |
| 71 | src/zephyr/autonomy_core/knowledge_distiller.py | src/zephyr/autonomy_core/knowledge_di... | prototype | draft |
| 72 | src/zephyr/autonomy_core/list_ce_files.py | src/zephyr/autonomy_core/list_ce_file... | prototype | draft |
| 73 | src/zephyr/autonomy_core/llm_gateway.py | src/zephyr/autonomy_core/llm_gateway.py | prototype | draft |
| 74 | src/zephyr/autonomy_core/lsg_pattern_tracker.py | src/zephyr/autonomy_core/lsg_pattern_... | prototype | draft |
| 75 | src/zephyr/autonomy_core/management/__init__.py | src/zephyr/autonomy_core/management/_... | prototype | draft |
| 76 | src/zephyr/autonomy_core/management/context_budget_tracke... | src/zephyr/autonomy_core/management/c... | prototype | draft |
| 77 | src/zephyr/autonomy_core/management/context_evictor.py | src/zephyr/autonomy_core/management/c... | prototype | draft |
| 78 | src/zephyr/autonomy_core/management/context_rot_model.py | src/zephyr/autonomy_core/management/c... | prototype | draft |
| 79 | src/zephyr/autonomy_core/mcp_adapter.py | src/zephyr/autonomy_core/mcp_adapter.py | prototype | draft |
| 80 | src/zephyr/autonomy_core/memory_bank.py | src/zephyr/autonomy_core/memory_bank.py | prototype | draft |
| 81 | src/zephyr/autonomy_core/mode_manager.py | src/zephyr/autonomy_core/mode_manager.py | prototype | draft |
| 82 | src/zephyr/autonomy_core/models/__init__.py | src/zephyr/autonomy_core/models/__ini... | scaffold_placeholder | orphan |
| 83 | src/zephyr/autonomy_core/otel_instrumentation.py | src/zephyr/autonomy_core/otel_instrum... | prototype | draft |
| 84 | src/zephyr/autonomy_core/parsing/__init__.py | src/zephyr/autonomy_core/parsing/__in... | prototype | draft |
| 85 | src/zephyr/autonomy_core/parsing/intent_keyword_mapper.py | src/zephyr/autonomy_core/parsing/inte... | prototype | draft |
| 86 | src/zephyr/autonomy_core/parsing/intent_parser.py | src/zephyr/autonomy_core/parsing/inte... | prototype | draft |
| 87 | src/zephyr/autonomy_core/pattern_library.py | src/zephyr/autonomy_core/pattern_libr... | prototype | draft |
| 88 | src/zephyr/autonomy_core/phase_planner.py | src/zephyr/autonomy_core/phase_planne... | prototype | draft |
| 89 | src/zephyr/autonomy_core/pipeline_orchestrator.py | src/zephyr/autonomy_core/pipeline_orc... | prototype | draft |
| 90 | src/zephyr/autonomy_core/poisoning_monitor.py | src/zephyr/autonomy_core/poisoning_mo... | prototype | draft |
| 91 | src/zephyr/autonomy_core/position_optimizer.py | src/zephyr/autonomy_core/position_opt... | prototype | draft |
| 92 | src/zephyr/autonomy_core/progressive_disclosure_injector.py | src/zephyr/autonomy_core/progressive_... | prototype | draft |
| 93 | src/zephyr/autonomy_core/prompt_registry.py | src/zephyr/autonomy_core/prompt_regis... | prototype | draft |
| 94 | src/zephyr/autonomy_core/rational.py | src/zephyr/autonomy_core/rational.py | prototype | draft |
| 95 | src/zephyr/autonomy_core/registry.py | src/zephyr/autonomy_core/registry.py | prototype | draft |
| 96 | src/zephyr/autonomy_core/security_filter.py | src/zephyr/autonomy_core/security_fil... | prototype | draft |
| 97 | src/zephyr/autonomy_core/self_diagnosis.py | src/zephyr/autonomy_core/self_diagnos... | prototype | draft |
| 98 | src/zephyr/autonomy_core/self_evolution_fidelity_gate.py | src/zephyr/autonomy_core/self_evoluti... | prototype | draft |
| 99 | src/zephyr/autonomy_core/sensitivity_classifier.py | src/zephyr/autonomy_core/sensitivity_... | prototype | draft |
| 100 | src/zephyr/autonomy_core/services/__init__.py | src/zephyr/autonomy_core/services/__i... | scaffold_placeholder | orphan |
| 101 | src/zephyr/autonomy_core/session_learner.py | src/zephyr/autonomy_core/session_lear... | prototype | draft |
| 102 | src/zephyr/autonomy_core/shadow_canary.py | src/zephyr/autonomy_core/shadow_canar... | prototype | draft |
| 103 | src/zephyr/autonomy_core/skill_attention.py | src/zephyr/autonomy_core/skill_attent... | prototype | draft |
| 104 | src/zephyr/autonomy_core/skill_breakage_checker.py | src/zephyr/autonomy_core/skill_breaka... | prototype | draft |
| 105 | src/zephyr/autonomy_core/skill_cache_provider.py | src/zephyr/autonomy_core/skill_cache_... | prototype | draft |
| 106 | src/zephyr/autonomy_core/skill_calibration.py | src/zephyr/autonomy_core/skill_calibr... | prototype | draft |
| 107 | src/zephyr/autonomy_core/skill_canary.py | src/zephyr/autonomy_core/skill_canary.py | prototype | draft |
| 108 | src/zephyr/autonomy_core/skill_cognitive_preservation.py | src/zephyr/autonomy_core/skill_cognit... | prototype | draft |
| 109 | src/zephyr/autonomy_core/skill_compliance.py | src/zephyr/autonomy_core/skill_compli... | prototype | draft |
| 110 | src/zephyr/autonomy_core/skill_consensus.py | src/zephyr/autonomy_core/skill_consen... | prototype | draft |
| 111 | src/zephyr/autonomy_core/skill_constructor.py | src/zephyr/autonomy_core/skill_constr... | prototype | draft |
| 112 | src/zephyr/autonomy_core/skill_context_isolation.py | src/zephyr/autonomy_core/skill_contex... | prototype | draft |
| 113 | src/zephyr/autonomy_core/skill_contract.py | src/zephyr/autonomy_core/skill_contra... | prototype | draft |
| 114 | src/zephyr/autonomy_core/skill_cross_model.py | src/zephyr/autonomy_core/skill_cross_... | prototype | draft |
| 115 | src/zephyr/autonomy_core/skill_di.py | src/zephyr/autonomy_core/skill_di.py | prototype | draft |
| 116 | src/zephyr/autonomy_core/skill_discovery.py | src/zephyr/autonomy_core/skill_discov... | prototype | draft |
| 117 | src/zephyr/autonomy_core/skill_durable.py | src/zephyr/autonomy_core/skill_durabl... | prototype | draft |
| 118 | src/zephyr/autonomy_core/skill_economics.py | src/zephyr/autonomy_core/skill_econom... | prototype | draft |
| 119 | src/zephyr/autonomy_core/skill_efficacy_calibrator.py | src/zephyr/autonomy_core/skill_effica... | prototype | draft |
| 120 | src/zephyr/autonomy_core/skill_evaluator.py | src/zephyr/autonomy_core/skill_evalua... | prototype | draft |
| 121 | src/zephyr/autonomy_core/skill_executor.py | src/zephyr/autonomy_core/skill_execut... | prototype | draft |
| 122 | src/zephyr/autonomy_core/skill_explain.py | src/zephyr/autonomy_core/skill_explai... | prototype | draft |
| 123 | src/zephyr/autonomy_core/skill_factory.py | src/zephyr/autonomy_core/skill_factor... | prototype | draft |
| 124 | src/zephyr/autonomy_core/skill_feature_flags.py | src/zephyr/autonomy_core/skill_featur... | prototype | draft |
| 125 | src/zephyr/autonomy_core/skill_feedback.py | src/zephyr/autonomy_core/skill_feedba... | prototype | draft |
| 126 | src/zephyr/autonomy_core/skill_freshness.py | src/zephyr/autonomy_core/skill_freshn... | prototype | draft |
| 127 | src/zephyr/autonomy_core/skill_freshness_ext.py | src/zephyr/autonomy_core/skill_freshn... | prototype | draft |
| 128 | src/zephyr/autonomy_core/skill_gitops.py | src/zephyr/autonomy_core/skill_gitops.py | prototype | draft |
| 129 | src/zephyr/autonomy_core/skill_guardrails.py | src/zephyr/autonomy_core/skill_guardr... | prototype | draft |
| 130 | src/zephyr/autonomy_core/skill_idempotency.py | src/zephyr/autonomy_core/skill_idempo... | prototype | draft |
| 131 | src/zephyr/autonomy_core/skill_kill_switch.py | src/zephyr/autonomy_core/skill_kill_s... | prototype | draft |
| 132 | src/zephyr/autonomy_core/skill_knowledge_base.py | src/zephyr/autonomy_core/skill_knowle... | prototype | draft |
| 133 | src/zephyr/autonomy_core/skill_kya.py | src/zephyr/autonomy_core/skill_kya.py | prototype | draft |
| 134 | src/zephyr/autonomy_core/skill_learning.py | src/zephyr/autonomy_core/skill_learni... | prototype | draft |
| 135 | src/zephyr/autonomy_core/skill_lifecycle.py | src/zephyr/autonomy_core/skill_lifecy... | prototype | draft |
| 136 | src/zephyr/autonomy_core/skill_lineage.py | src/zephyr/autonomy_core/skill_lineag... | prototype | draft |
| 137 | src/zephyr/autonomy_core/skill_loader.py | src/zephyr/autonomy_core/skill_loader.py | prototype | draft |
| 138 | src/zephyr/autonomy_core/skill_locking.py | src/zephyr/autonomy_core/skill_lockin... | prototype | draft |
| 139 | src/zephyr/autonomy_core/skill_model.py | src/zephyr/autonomy_core/skill_model.py | prototype | draft |
| 140 | src/zephyr/autonomy_core/skill_model_evolution.py | src/zephyr/autonomy_core/skill_model_... | prototype | draft |
| 141 | src/zephyr/autonomy_core/skill_observability.py | src/zephyr/autonomy_core/skill_observ... | prototype | draft |
| 142 | src/zephyr/autonomy_core/skill_ontology.py | src/zephyr/autonomy_core/skill_ontolo... | prototype | draft |
| 143 | src/zephyr/autonomy_core/skill_postmortem.py | src/zephyr/autonomy_core/skill_postmo... | prototype | draft |
| 144 | src/zephyr/autonomy_core/skill_prompt_cache.py | src/zephyr/autonomy_core/skill_prompt... | prototype | draft |
| 145 | src/zephyr/autonomy_core/skill_prompt_opt.py | src/zephyr/autonomy_core/skill_prompt... | prototype | draft |
| 146 | src/zephyr/autonomy_core/skill_registry.py | src/zephyr/autonomy_core/skill_regist... | prototype | draft |
| 147 | src/zephyr/autonomy_core/skill_resilience.py | src/zephyr/autonomy_core/skill_resili... | prototype | draft |
| 148 | src/zephyr/autonomy_core/skill_risk_mitigator.py | src/zephyr/autonomy_core/skill_risk_m... | prototype | draft |
| 149 | src/zephyr/autonomy_core/skill_router.py | src/zephyr/autonomy_core/skill_router.py | prototype | draft |
| 150 | src/zephyr/autonomy_core/skill_sandbox.py | src/zephyr/autonomy_core/skill_sandbo... | prototype | draft |
| 151 | src/zephyr/autonomy_core/skill_schema_registry.py | src/zephyr/autonomy_core/skill_schema... | prototype | draft |
| 152 | src/zephyr/autonomy_core/skill_security.py | src/zephyr/autonomy_core/skill_securi... | prototype | draft |
| 153 | src/zephyr/autonomy_core/skill_shadow.py | src/zephyr/autonomy_core/skill_shadow.py | prototype | draft |
| 154 | src/zephyr/autonomy_core/skill_silent_failure.py | src/zephyr/autonomy_core/skill_silent... | prototype | draft |
| 155 | src/zephyr/autonomy_core/skill_team_optimizer.py | src/zephyr/autonomy_core/skill_team_o... | prototype | draft |
| 156 | src/zephyr/autonomy_core/skill_telemetry.py | src/zephyr/autonomy_core/skill_teleme... | prototype | draft |
| 157 | src/zephyr/autonomy_core/skill_temperature.py | src/zephyr/autonomy_core/skill_temper... | prototype | draft |
| 158 | src/zephyr/autonomy_core/skill_tokenomics.py | src/zephyr/autonomy_core/skill_tokeno... | prototype | draft |
| 159 | src/zephyr/autonomy_core/skill_translator.py | src/zephyr/autonomy_core/skill_transl... | prototype | draft |
| 160 | src/zephyr/autonomy_core/skill_workflow.py | src/zephyr/autonomy_core/skill_workfl... | prototype | draft |
| 161 | src/zephyr/autonomy_core/solo_dev_safety_net.py | src/zephyr/autonomy_core/solo_dev_saf... | prototype | draft |
| 162 | src/zephyr/autonomy_core/staleness_manager.py | src/zephyr/autonomy_core/staleness_ma... | prototype | draft |
| 163 | src/zephyr/autonomy_core/support/__init__.py | src/zephyr/autonomy_core/support/__in... | prototype | draft |
| 164 | src/zephyr/autonomy_core/support/architecture_context_loa... | src/zephyr/autonomy_core/support/arch... | prototype | draft |
| 165 | src/zephyr/autonomy_core/support/doc_compressor.py | src/zephyr/autonomy_core/support/doc_... | prototype | draft |
| 166 | src/zephyr/autonomy_core/support/prompt_registry.py | src/zephyr/autonomy_core/support/prom... | prototype | draft |
| 167 | src/zephyr/autonomy_core/support/system_snapshot.py | src/zephyr/autonomy_core/support/syst... | prototype | draft |
| 168 | src/zephyr/autonomy_core/system_snapshot.py | src/zephyr/autonomy_core/system_snaps... | prototype | draft |
| 169 | src/zephyr/autonomy_core/task_context_builder.py | src/zephyr/autonomy_core/task_context... | prototype | draft |
| 170 | src/zephyr/autonomy_core/token_budget.py | src/zephyr/autonomy_core/token_budget.py | prototype | draft |
| 171 | src/zephyr/autonomy_core/trigger_router.py | src/zephyr/autonomy_core/trigger_rout... | prototype | draft |
| 172 | src/zephyr/autonomy_core/vector_bridge.py | src/zephyr/autonomy_core/vector_bridg... | prototype | draft |
| 173 | src/zephyr/autonomy_core/vector_writer.py | src/zephyr/autonomy_core/vector_write... | prototype | draft |
| 174 | src/zephyr/autonomy_core/verify_paths.py | src/zephyr/autonomy_core/verify_paths.py | prototype | draft |
| 175 | src/zephyr/autonomy_core/vibe_coding_quality_gate.py | src/zephyr/autonomy_core/vibe_coding_... | prototype | draft |

### L2 领域层 / Domain Layer (2 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | 自治-向量库验证/D-AUTONOMY-125 | ChromaDB Runtime Validator | design | design_only |
| 2 | 自治-记忆溯源/D-AUTONOMY-73 | Memory Provenance Enforcer | design | design_only |

### 未分类 / Unclassified (477 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name | 成熟度 / Maturity | 构建状态 / Build Status |
|:--:|---------|---------|:---:|:---:|
| 1 | D-AUTONOMY-CORE/11 Agents Full MVP 11个Agent全部MVP实现 | 11 Agents Full MVP 11个Agent全部MVP实现 | design | design_only |
| 2 | D-AUTONOMY-CORE/8-Collection Unified Schema Manager 8大Co... | 8-Collection Unified Schema Manager 8... | design | design_only |
| 3 | D-AUTONOMY-CORE/A2A Check A2A检查 | A2A Check A2A检查 | design | design_only |
| 4 | D-AUTONOMY-CORE/A2A Check Gateway A2A检查网关 | A2A Check Gateway A2A检查网关 | design | design_only |
| 5 | D-AUTONOMY-CORE/A2A Check Gateway Policy Engine A2A检查网... | A2A Check Gateway Policy Engine A2A检... | design | design_only |
| 6 | D-AUTONOMY-CORE/A2A Check Non-Bypassable A2A检查不可绕过 | A2A Check Non-Bypassable A2A检查不可绕过 | design | design_only |
| 7 | D-AUTONOMY-CORE/A2A Check Protocol A2A检查协议 | A2A Check Protocol A2A检查协议 | design | design_only |
| 8 | D-AUTONOMY-CORE/A2A Communication Agent间通信 | A2A Communication Agent间通信 | design | design_only |
| 9 | D-AUTONOMY-CORE/A2A Protocol A2A协议 | A2A Protocol A2A协议 | design | design_only |
| 10 | D-AUTONOMY-CORE/ABAC策略 ABAC Policy | ABAC策略 ABAC Policy | design | design_only |
| 11 | D-AUTONOMY-CORE/AGENTICAITA AGENTICAITA框架 | AGENTICAITA AGENTICAITA框架 | design | design_only |
| 12 | D-AUTONOMY-CORE/AI 人工智能 | AI 人工智能 | design | design_only |
| 13 | D-AUTONOMY-CORE/AI 治理执行者角色 | AI 治理执行者角色 | design | design_only |
| 14 | D-AUTONOMY-CORE/AISI 2026报告 | AISI 2026报告 | design | design_only |
| 15 | D-AUTONOMY-CORE/AI自主执行率阈值 AI Autonomous Execution ... | AI自主执行率阈值 AI Autonomous Execut... | design | design_only |
| 16 | D-AUTONOMY-CORE/AI自治行为审计 AI Autonomous Behavior Audit | AI自治行为审计 AI Autonomous Behavior... | design | design_only |
| 17 | D-AUTONOMY-CORE/AI自治运维是闭环而非开环 Closed-Loop Auto... | AI自治运维是闭环而非开环 Closed-Loop ... | design | design_only |
| 18 | D-AUTONOMY-CORE/AI自治运维闭环 AI自治运维 | AI自治运维闭环 AI自治运维 | design | design_only |
| 19 | D-AUTONOMY-CORE/AI自治进化与闭环优化 | AI自治进化与闭环优化 | design | design_only |
| 20 | D-AUTONOMY-CORE/API LLM | API LLM | design | design_only |
| 21 | D-AUTONOMY-CORE/ARA Adaptive Risk Architecture ARA自适应... | ARA Adaptive Risk Architecture ARA自... | design | design_only |
| 22 | D-AUTONOMY-CORE/ARA自适应风险架构 ARA Adaptive Risk Archi... | ARA自适应风险架构 ARA Adaptive Risk A... | design | design_only |
| 23 | D-AUTONOMY-CORE/ARS双轨结算模型 ARS Dual-track Settlement... | ARS双轨结算模型 ARS Dual-track Settle... | design | design_only |
| 24 | D-AUTONOMY-CORE/AWQ 4-bit Quantization AWQ 4-bit量化 | AWQ 4-bit Quantization AWQ 4-bit量化 | design | design_only |
| 25 | D-AUTONOMY-CORE/AWS Agentic AI安全范围矩阵 AWS Agentic AI... | AWS Agentic AI安全范围矩阵 AWS Agenti... | design | design_only |
| 26 | D-AUTONOMY-CORE/AWS Resilient AI Agents AWS弹性AI Agent | AWS Resilient AI Agents AWS弹性AI Agent | design | design_only |
| 27 | D-AUTONOMY-CORE/Actor Actor执行器 | Actor Actor执行器 | design | design_only |
| 28 | D-AUTONOMY-CORE/Actor 执行器 | Actor 执行器 | design | design_only |
| 29 | D-AUTONOMY-CORE/Actor-Evaluator-SelfReflection Actor-Eval... | Actor-Evaluator-SelfReflection Actor-... | design | design_only |
| 30 | D-AUTONOMY-CORE/Adaptive Z-Score Trigger Engine 自适应Z分... | Adaptive Z-Score Trigger Engine 自适... | design | design_only |
| 31 | D-AUTONOMY-CORE/Agent Architecture Position Agent架构在全... | Agent Architecture Position Agent架构... | design | design_only |
| 32 | D-AUTONOMY-CORE/Agent Architecture Unified Source Agent架... | Agent Architecture Unified Source Age... | design | design_only |
| 33 | D-AUTONOMY-CORE/Agent Audit Trail Agent审计链 | Agent Audit Trail Agent审计链 | design | design_only |
| 34 | D-AUTONOMY-CORE/Agent Autonomy Boundary Agent自治边界 | Agent Autonomy Boundary Agent自治边界 | design | design_only |
| 35 | D-AUTONOMY-CORE/Agent Budget Enforcer Agent预算执行器 | Agent Budget Enforcer Agent预算执行器 | design | design_only |
| 36 | D-AUTONOMY-CORE/Agent Card Registry Agent Card注册表 | Agent Card Registry Agent Card注册表 | design | design_only |
| 37 | D-AUTONOMY-CORE/Agent Challenge 代理挑战 | Agent Challenge 代理挑战 | design | design_only |
| 38 | D-AUTONOMY-CORE/Agent Cold Start Agent冷启动与技能注册 | Agent Cold Start Agent冷启动与技能注册 | design | design_only |
| 39 | D-AUTONOMY-CORE/Agent Cold Start Skill Registration Agent... | Agent Cold Start Skill Registration A... | design | design_only |
| 40 | D-AUTONOMY-CORE/Agent Collaboration Flow Panorama Agent协... | Agent Collaboration Flow Panorama Age... | design | design_only |
| 41 | D-AUTONOMY-CORE/Agent Command Chain Agent分层指挥链 | Agent Command Chain Agent分层指挥链 | design | design_only |
| 42 | D-AUTONOMY-CORE/Agent Communication Protocol Agent间通信协议 | Agent Communication Protocol Agent间... | design | design_only |
| 43 | D-AUTONOMY-CORE/Agent Communication Security Agent通信安全 | Agent Communication Security Agent通... | design | design_only |
| 44 | D-AUTONOMY-CORE/Agent Coordination Agent协调 | Agent Coordination Agent协调 | design | design_only |
| 45 | D-AUTONOMY-CORE/Agent Dispatch Agent调度分发 | Agent Dispatch Agent调度分发 | design | design_only |
| 46 | D-AUTONOMY-CORE/Agent Drift Guard Agent漂移守卫 | Agent Drift Guard Agent漂移守卫 | design | design_only |
| 47 | D-AUTONOMY-CORE/Agent Drift量化检查器 Agent Drift Quantit... | Agent Drift量化检查器 Agent Drift Qua... | design | design_only |
| 48 | D-AUTONOMY-CORE/Agent Error Recovery Agent错误恢复与优雅降级 | Agent Error Recovery Agent错误恢复与... | design | design_only |
| 49 | D-AUTONOMY-CORE/Agent Escalation Engine Agent升级引擎 | Agent Escalation Engine Agent升级引擎 | design | design_only |
| 50 | D-AUTONOMY-CORE/Agent Four Level Autonomy Model Agent四级... | Agent Four Level Autonomy Model Agent... | design | design_only |
| 51 | D-AUTONOMY-CORE/Agent Identity Manager Agent身份管理器 | Agent Identity Manager Agent身份管理器 | design | design_only |
| 52 | D-AUTONOMY-CORE/Agent Kill Switch Agent紧急制动 | Agent Kill Switch Agent紧急制动 | design | design_only |
| 53 | D-AUTONOMY-CORE/Agent Legacy Issue Decision Agent遗留问题... | Agent Legacy Issue Decision Agent遗留... | design | design_only |
| 54 | D-AUTONOMY-CORE/Agent Memory Agent记忆 | Agent Memory Agent记忆 | design | design_only |
| 55 | D-AUTONOMY-CORE/Agent Memory Architecture Agent记忆架构 | Agent Memory Architecture Agent记忆架构 | design | design_only |
| 56 | D-AUTONOMY-CORE/Agent Memory Vector Retrieval RAG Agent记... | Agent Memory Vector Retrieval RAG Age... | design | design_only |
| 57 | D-AUTONOMY-CORE/Agent Observability Agent可观测性 | Agent Observability Agent可观测性 | design | design_only |
| 58 | D-AUTONOMY-CORE/Agent Permission Guard Agent权限守卫 | Agent Permission Guard Agent权限守卫 | design | design_only |
| 59 | D-AUTONOMY-CORE/Agent Process Crash Agent进程崩溃 | Agent Process Crash Agent进程崩溃 | design | design_only |
| 60 | D-AUTONOMY-CORE/Agent Registry Agent注册表 | Agent Registry Agent注册表 | design | design_only |
| 61 | D-AUTONOMY-CORE/Agent Resource Manager Agent资源管理器 | Agent Resource Manager Agent资源管理器 | design | design_only |
| 62 | D-AUTONOMY-CORE/Agent Spec Agent规格 | Agent Spec Agent规格 | design | design_only |
| 63 | D-AUTONOMY-CORE/Agent Stability Index ASI 索引 | Agent Stability Index ASI 索引 | design | design_only |
| 64 | D-AUTONOMY-CORE/Agent State Agent状态检查点 | Agent State Agent状态检查点 | design | design_only |
| 65 | D-AUTONOMY-CORE/Agent State Manager Agent状态管理器 | Agent State Manager Agent状态管理器 | design | design_only |
| 66 | D-AUTONOMY-CORE/Agent Test Chaos Engineering Agent测试与... | Agent Test Chaos Engineering Agent测... | design | design_only |
| 67 | D-AUTONOMY-CORE/Agent Testing Chaos Engineering Agent测试... | Agent Testing Chaos Engineering Agent... | design | design_only |
| 68 | D-AUTONOMY-CORE/Agent Three Layer Command Chain Agent三层... | Agent Three Layer Command Chain Agent... | design | design_only |
| 69 | D-AUTONOMY-CORE/Agent Upgrade Safety Mode Agent升级安全模式 | Agent Upgrade Safety Mode Agent升级安... | design | design_only |
| 70 | D-AUTONOMY-CORE/Agent Version Management Agent版本管理策略 | Agent Version Management Agent版本管... | design | design_only |
| 71 | D-AUTONOMY-CORE/Agent-R Agent-R实时反思 | Agent-R Agent-R实时反思 | design | design_only |
| 72 | D-AUTONOMY-CORE/AgentCard Agent技能卡 | AgentCard Agent技能卡 | design | design_only |
| 73 | D-AUTONOMY-CORE/Agentic Financial Market Model AFMM 模型 | Agentic Financial Market Model AFMM 模型 | design | design_only |
| 74 | D-AUTONOMY-CORE/Agent串谋检测 Agent Collusion Detection | Agent串谋检测 Agent Collusion Detection | design | design_only |
| 75 | D-AUTONOMY-CORE/Agent可观测性 | Agent可观测性 | design | design_only |
| 76 | D-AUTONOMY-CORE/Agent安全约束 | Agent安全约束 | design | design_only |
| 77 | D-AUTONOMY-CORE/Agent架构安全约束 | Agent架构安全约束 | design | design_only |
| 78 | D-AUTONOMY-CORE/Agent漏洞全景与防御升级 Agent Vulnerabili... | Agent漏洞全景与防御升级 Agent Vulnera... | design | design_only |
| 79 | D-AUTONOMY-CORE/Agent行为约束 | Agent行为约束 | design | design_only |
| 80 | D-AUTONOMY-CORE/Agent身份注册与认证 Agent Identity Regist... | Agent身份注册与认证 Agent Identity Re... | design | design_only |
| 81 | D-AUTONOMY-CORE/Agent轮换策略 Agent Rotation Strategy | Agent轮换策略 Agent Rotation Strategy | design | design_only |
| 82 | D-AUTONOMY-CORE/Agent间信任利用攻击 Inter-agent Trust Exp... | Agent间信任利用攻击 Inter-agent Trust... | design | design_only |
| 83 | D-AUTONOMY-CORE/Agent间通信协议 | Agent间通信协议 | design | design_only |
| 84 | D-AUTONOMY-CORE/Anthropic Agent Skills Anthropic Agent技... | Anthropic Agent Skills Anthropic Agen... | design | design_only |
| 85 | D-AUTONOMY-CORE/Architecture Component to Domain Mapping ... | Architecture Component to Domain Mapp... | design | design_only |
| 86 | D-AUTONOMY-CORE/Architecture Diagram Relations 与其他架构... | Architecture Diagram Relations 与其他... | design | design_only |
| 87 | D-AUTONOMY-CORE/Assurance Gap Manager 保障缺口管理器 | Assurance Gap Manager 保障缺口管理器 | design | design_only |
| 88 | D-AUTONOMY-CORE/Async Reflection 反思为异步执行 | Async Reflection 反思为异步执行 | design | design_only |
| 89 | D-AUTONOMY-CORE/Audit Trail 审计追踪 | Audit Trail 审计追踪 | design | design_only |
| 90 | D-AUTONOMY-CORE/AuditLogger 审计日志器 | AuditLogger 审计日志器 | design | design_only |
| 91 | D-AUTONOMY-CORE/AuditTrace Interface 审计追踪接口 | AuditTrace Interface 审计追踪接口 | design | design_only |
| 92 | D-AUTONOMY-CORE/Auto-Fix Engine 自动修复引擎 | Auto-Fix Engine 自动修复引擎 | design | design_only |
| 93 | D-AUTONOMY-CORE/AutoGen 2.0 | AutoGen 2.0 | design | design_only |
| 94 | D-AUTONOMY-CORE/Automated Operations Execution 自动化运维... | Automated Operations Execution 自动化... | design | design_only |
| 95 | D-AUTONOMY-CORE/AutonomousExecutionRateDegraded 自主执行... | AutonomousExecutionRateDegraded 自主... | design | design_only |
| 96 | D-AUTONOMY-CORE/Autonomy Boundary Enforcer 自治边界执行器 | Autonomy Boundary Enforcer 自治边界执... | design | design_only |
| 97 | D-AUTONOMY-CORE/Autonomy Circuit Breaker 自治熔断条件 | Autonomy Circuit Breaker 自治熔断条件 | design | design_only |
| 98 | D-AUTONOMY-CORE/Autonomy Maturity Grading 自治成熟度分级 | Autonomy Maturity Grading 自治成熟度分级 | design | design_only |
| 99 | D-AUTONOMY-CORE/Autonomy Passport 自治护照 | Autonomy Passport 自治护照 | design | design_only |
| 100 | D-AUTONOMY-CORE/Autopilot 自动驾驶 | Autopilot 自动驾驶 | design | design_only |
| 101 | D-AUTONOMY-CORE/BEST-Route BEST-Route路由 | BEST-Route BEST-Route路由 | design | design_only |
| 102 | D-AUTONOMY-CORE/Backtest Execution 回测执行 | Backtest Execution 回测执行 | design | design_only |
| 103 | D-AUTONOMY-CORE/Benchmark Analysis 对标分析 | Benchmark Analysis 对标分析 | design | design_only |
| 104 | D-AUTONOMY-CORE/BlackSwanDetected 黑天鹅检测 | BlackSwanDetected 黑天鹅检测 | design | design_only |
| 105 | D-AUTONOMY-CORE/Bootstrap Superadmin 超级管理员引导 | Bootstrap Superadmin 超级管理员引导 | design | design_only |
| 106 | D-AUTONOMY-CORE/Bounded Autonomy Level Manager 有界自治等... | Bounded Autonomy Level Manager 有界自... | design | design_only |
| 107 | D-AUTONOMY-CORE/Budget Enforcer 预算执行器 | Budget Enforcer 预算执行器 | design | design_only |
| 108 | D-AUTONOMY-CORE/Budget Management 预算管理 | Budget Management 预算管理 | design | design_only |
| 109 | D-AUTONOMY-CORE/BudgetExceeded 预算超限 | BudgetExceeded 预算超限 | design | design_only |
| 110 | D-AUTONOMY-CORE/CSCR CSCR路由 | CSCR CSCR路由 | design | design_only |
| 111 | D-AUTONOMY-CORE/CTR-P1-014 ExperimentResult CTR-P1-014实... | CTR-P1-014 ExperimentResult CTR-P1-01... | design | design_only |
| 112 | D-AUTONOMY-CORE/CTR-TRACE-001 AuditTrace 审计追踪 | CTR-TRACE-001 AuditTrace 审计追踪 | design | design_only |
| 113 | D-AUTONOMY-CORE/CapabilityCard 能力卡片 | CapabilityCard 能力卡片 | design | design_only |
| 114 | D-AUTONOMY-CORE/Causal LLM Routing 因果LLM路由 | Causal LLM Routing 因果LLM路由 | design | design_only |
| 115 | D-AUTONOMY-CORE/Chaos Engineering Experiment Library 混沌... | Chaos Engineering Experiment Library ... | design | design_only |
| 116 | D-AUTONOMY-CORE/Cheng Adaptive LLM Multi-Agent Cheng自适... | Cheng Adaptive LLM Multi-Agent Cheng... | design | design_only |
| 117 | D-AUTONOMY-CORE/ChromaDB Runtime Validator ChromaDB运行验... | ChromaDB Runtime Validator ChromaDB运... | design | design_only |
| 118 | D-AUTONOMY-CORE/Circuit Breaker 熔断器 | Circuit Breaker 熔断器 | design | design_only |
| 119 | D-AUTONOMY-CORE/Claude Claude模型 | Claude Claude模型 | design | design_only |
| 120 | D-AUTONOMY-CORE/Cold Start 6-Step 冷启动6步流程 | Cold Start 6-Step 冷启动6步流程 | design | design_only |
| 121 | D-AUTONOMY-CORE/Cold Start Process 冷启动流程 | Cold Start Process 冷启动流程 | design | design_only |
| 122 | D-AUTONOMY-CORE/Cold Start Requires Skill Registration Ag... | Cold Start Requires Skill Registratio... | design | design_only |
| 123 | D-AUTONOMY-CORE/Cold Start Skill Registration 冷启动与技... | Cold Start Skill Registration 冷启动... | design | design_only |
| 124 | D-AUTONOMY-CORE/Command Flow 指令流 | Command Flow 指令流 | design | design_only |
| 125 | D-AUTONOMY-CORE/Command Priority 指令优先级 | Command Priority 指令优先级 | design | design_only |
| 126 | D-AUTONOMY-CORE/Compliance Check 合规检查 | Compliance Check 合规检查 | design | design_only |
| 127 | D-AUTONOMY-CORE/Config Update 配置更新 | Config Update 配置更新 | design | design_only |
| 128 | D-AUTONOMY-CORE/Conflict & Contradiction Matrix 冲突与矛... | Conflict & Contradiction Matrix 冲突... | design | design_only |
| 129 | D-AUTONOMY-CORE/Conflict Resolution 冲突解决 | Conflict Resolution 冲突解决 | design | design_only |
| 130 | D-AUTONOMY-CORE/ContestTrade ContestTrade框架 | ContestTrade ContestTrade框架 | design | design_only |
| 131 | D-AUTONOMY-CORE/Context Engine 上下文引擎 | Context Engine 上下文引擎 | design | design_only |
| 132 | D-AUTONOMY-CORE/Context Manager 上下文管理 | Context Manager 上下文管理 | design | design_only |
| 133 | D-AUTONOMY-CORE/Context Recycling 上下文回收 | Context Recycling 上下文回收 | design | design_only |
| 134 | D-AUTONOMY-CORE/CoreReadOnlyState 核心只读状态 | CoreReadOnlyState 核心只读状态 | design | design_only |
| 135 | D-AUTONOMY-CORE/Cost Control 成本控制 | Cost Control 成本控制 | design | design_only |
| 136 | D-AUTONOMY-CORE/Cost Controller 成本控制器 | Cost Controller 成本控制器 | design | design_only |
| 137 | D-AUTONOMY-CORE/Cost Governance 成本治理 | Cost Governance 成本治理 | design | design_only |
| 138 | D-AUTONOMY-CORE/Cost-Aware Routing 成本感知路由 | Cost-Aware Routing 成本感知路由 | design | design_only |
| 139 | D-AUTONOMY-CORE/CrewAI | CrewAI | design | design_only |
| 140 | D-AUTONOMY-CORE/Cross-Layer Interaction Matrix 跨层交互矩阵 | Cross-Layer Interaction Matrix 跨层交... | design | design_only |
| 141 | D-AUTONOMY-CORE/Cross-Layer Interaction Rules 跨层交互规则 | Cross-Layer Interaction Rules 跨层交... | design | design_only |
| 142 | D-AUTONOMY-CORE/CrowdnessWarning 拥挤度告警 | CrowdnessWarning 拥挤度告警 | design | design_only |
| 143 | D-AUTONOMY-CORE/D-AUT | D-AUT | design | design_only |
| 144 | D-AUTONOMY-CORE/D-AUT-CORE 核心 | D-AUT-CORE 核心 | design | design_only |
| 145 | D-AUTONOMY-CORE/D-AUTONOMY | D-AUTONOMY | design | design_only |
| 146 | D-AUTONOMY-CORE/D-AUTONOMY-CORE 核心 | D-AUTONOMY-CORE 核心 | design | design_only |
| 147 | D-AUTONOMY-CORE/Data Quality Check 数据质量检查 | Data Quality Check 数据质量检查 | design | design_only |
| 148 | D-AUTONOMY-CORE/Data Quality Self-Management 数据质量自管理 | Data Quality Self-Management 数据质量... | design | design_only |
| 149 | D-AUTONOMY-CORE/Decision Checkpoint 决策前快照检查点 | Decision Checkpoint 决策前快照检查点 | design | design_only |
| 150 | D-AUTONOMY-CORE/DecisionTraceBroken 决策溯源断链 | DecisionTraceBroken 决策溯源断链 | design | design_only |
| 151 | D-AUTONOMY-CORE/DeepSeek V4 Pro DeepSeek V4 Pro模型 | DeepSeek V4 Pro DeepSeek V4 Pro模型 | design | design_only |
| 152 | D-AUTONOMY-CORE/DeepSeek-7B DeepSeek-7B模型 | DeepSeek-7B DeepSeek-7B模型 | design | design_only |
| 153 | D-AUTONOMY-CORE/Degradation Strategy Matrix 降级策略矩阵 | Degradation Strategy Matrix 降级策略矩阵 | design | design_only |
| 154 | D-AUTONOMY-CORE/Detect 异常检测 | Detect 异常检测 | design | design_only |
| 155 | D-AUTONOMY-CORE/Diagnose 根因分析 | Diagnose 根因分析 | design | design_only |
| 156 | D-AUTONOMY-CORE/Drift Detection 漂移检测 | Drift Detection 漂移检测 | design | design_only |
| 157 | D-AUTONOMY-CORE/Drift Detector 漂移检测器 | Drift Detector 漂移检测器 | design | design_only |
| 158 | D-AUTONOMY-CORE/Dual Channel Scheduler Decision 双通道调... | Dual Channel Scheduler Decision 双通... | design | design_only |
| 159 | D-AUTONOMY-CORE/Episodic Memory 情景记忆 | Episodic Memory 情景记忆 | design | design_only |
| 160 | D-AUTONOMY-CORE/Error Classification Recovery Strategy 错... | Error Classification Recovery Strateg... | design | design_only |
| 161 | D-AUTONOMY-CORE/Error Recovery 优雅降级 错误恢复与优雅降级 | Error Recovery 优雅降级 错误恢复与优... | design | design_only |
| 162 | D-AUTONOMY-CORE/Error Recovery 错误恢复 | Error Recovery 错误恢复 | design | design_only |
| 163 | D-AUTONOMY-CORE/Escalation Engine 升级引擎 | Escalation Engine 升级引擎 | design | design_only |
| 164 | D-AUTONOMY-CORE/EscalationTriggered 升级触发 | EscalationTriggered 升级触发 | design | design_only |
| 165 | D-AUTONOMY-CORE/Evaluator Evaluator评估器 | Evaluator Evaluator评估器 | design | design_only |
| 166 | D-AUTONOMY-CORE/Evaluator 评估器 | Evaluator 评估器 | design | design_only |
| 167 | D-AUTONOMY-CORE/Evolution Agent 进化Agent | Evolution Agent 进化Agent | design | design_only |
| 168 | D-AUTONOMY-CORE/Execution Bus 执行层消息总线 | Execution Bus 执行层消息总线 | design | design_only |
| 169 | D-AUTONOMY-CORE/Execution Layer Agents 执行层Agent组 | Execution Layer Agents 执行层Agent组 | design | design_only |
| 170 | D-AUTONOMY-CORE/Execution Traces Collection Manager 执行... | Execution Traces Collection Manager ... | design | design_only |
| 171 | D-AUTONOMY-CORE/ExperimentAnomaly 实验异常检测 | ExperimentAnomaly 实验异常检测 | design | design_only |
| 172 | D-AUTONOMY-CORE/FAISS FAISS向量检索引擎 | FAISS FAISS向量检索引擎 | design | design_only |
| 173 | D-AUTONOMY-CORE/FCA Mills Review自治光谱 | FCA Mills Review自治光谱 | design | design_only |
| 174 | D-AUTONOMY-CORE/FSM Verifier FSM验证器 | FSM Verifier FSM验证器 | design | design_only |
| 175 | D-AUTONOMY-CORE/Factor Computation 因子计算 | Factor Computation 因子计算 | design | design_only |
| 176 | D-AUTONOMY-CORE/Feature Store Dependency Drift Detector ... | Feature Store Dependency Drift Detect... | design | design_only |
| 177 | D-AUTONOMY-CORE/Fee Track 费用轨道 | Fee Track 费用轨道 | design | design_only |
| 178 | D-AUTONOMY-CORE/Feedback Flow 反馈流 | Feedback Flow 反馈流 | design | design_only |
| 179 | D-AUTONOMY-CORE/Five-Stage Memory Pipeline 五阶段记忆流水线 | Five-Stage Memory Pipeline 五阶段记忆... | design | design_only |
| 180 | D-AUTONOMY-CORE/Four Track Decision Path Agent Responsibi... | Four Track Decision Path Agent Respon... | design | design_only |
| 181 | D-AUTONOMY-CORE/Four-Layer Memory Model 四层记忆模型 | Four-Layer Memory Model 四层记忆模型 | design | design_only |
| 182 | D-AUTONOMY-CORE/Four-Layer Versioning 四层版本化 | Four-Layer Versioning 四层版本化 | design | design_only |
| 183 | D-AUTONOMY-CORE/Four-Layer Versioning 四层版本化分类法 | Four-Layer Versioning 四层版本化分类法 | design | design_only |
| 184 | D-AUTONOMY-CORE/Functional Domain List 功能域清单 | Functional Domain List 功能域清单 | design | design_only |
| 185 | D-AUTONOMY-CORE/GATE-GA 守护智能体汇总 | GATE-GA 守护智能体汇总 | design | design_only |
| 186 | D-AUTONOMY-CORE/GATE-GA-01 多Agent架构 | GATE-GA-01 多Agent架构 | design | design_only |
| 187 | D-AUTONOMY-CORE/GATE-GA-02 监控盲区 | GATE-GA-02 监控盲区 | design | design_only |
| 188 | D-AUTONOMY-CORE/GATE-GA-03 独立运行环境 | GATE-GA-03 独立运行环境 | design | design_only |
| 189 | D-AUTONOMY-CORE/GATE-SZP Szpruch运行时治理汇总 | GATE-SZP Szpruch运行时治理汇总 | design | design_only |
| 190 | D-AUTONOMY-CORE/GATE-SZP-01 日内高频 | GATE-SZP-01 日内高频 | design | design_only |
| 191 | D-AUTONOMY-CORE/GATE-SZP-02 多Agent工作流 | GATE-SZP-02 多Agent工作流 | design | design_only |
| 192 | D-AUTONOMY-CORE/GATE-SZP-03 轨迹漂移盲区 | GATE-SZP-03 轨迹漂移盲区 | design | design_only |
| 193 | D-AUTONOMY-CORE/GATE-TRUST Agent间信任防护汇总 | GATE-TRUST Agent间信任防护汇总 | design | design_only |
| 194 | D-AUTONOMY-CORE/GATE-TRUST-01 多Agent通信 | GATE-TRUST-01 多Agent通信 | design | design_only |
| 195 | D-AUTONOMY-CORE/GATE-TRUST-02 Agent间协议 | GATE-TRUST-02 Agent间协议 | design | design_only |
| 196 | D-AUTONOMY-CORE/GATE-TRUST-03 Meta-Governance 治理 | GATE-TRUST-03 Meta-Governance 治理 | design | design_only |
| 197 | D-AUTONOMY-CORE/GD-02 AI自治边界分三级 | GD-02 AI自治边界分三级 | design | design_only |
| 198 | D-AUTONOMY-CORE/GLM-5.1 GLM-5.1模型 | GLM-5.1 GLM-5.1模型 | design | design_only |
| 199 | D-AUTONOMY-CORE/GPU Management GPU管理 | GPU Management GPU管理 | design | design_only |
| 200 | D-AUTONOMY-CORE/GPU Memory Insufficient GPU显存不足 | GPU Memory Insufficient GPU显存不足 | design | design_only |

> (仅显示前 200 个模块，共 477 个)

## 依赖关系图 / Dependency Graph

> 域内模块依赖关系（共 644 条 / 644 edges）。按依赖类型分组，使用 → 表示方向。

```

┌──────────────────────────────────────────────────────────────────┐
│      依赖关系图 / Dependency Graph (共 644 条 / 644 edges)       │
├──────────────────────────────────────────────────────────────────┤
│   依赖类型数 / Dependency Types: 6                               │
│   [import_depends]: 446 条 / edges                               │
│   [config_depends]: 136 条 / edges                               │
│   [contract]: 22 条 / edges                                      │
│   [runtime]: 19 条 / edges                                       │
│   [event]: 16 条 / edges                                         │
│   [data]: 5 条 / edges                                           │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                [import_depends] (446 条 / edges)                 │
├──────────────────────────────────────────────────────────────────┤
│   context_assembler.py → __init__.py                             │
│   context_budget_tracker.py → __init__.py                        │
│   context_budget.py → __init__.py                                │
│   context_pipeline.py → __init__.py                              │
│   context_injector.py → __init__.py                              │
│   engine.py → __init__.py                                        │
│   intent_parser.py → __init__.py                                 │
│   pipeline_orchestrator.py → __init__.py                         │
│   prompt_registry.py → __init__.py                               │
│   skill_constructor.py → __init__.py                             │
│   skill_consensus.py → __init__.py                               │
│   skill_contract.py → __init__.py                                │
│   skill_discovery.py → __init__.py                               │
│   skill_evaluator.py → __init__.py                               │
│   skill_executor.py → __init__.py                                │
│   skill_efficacy_calibrator.py → __init__.py                     │
│   skill_explain.py → __init__.py                                 │
│   skill_factory.py → __init__.py                                 │
│   skill_feedback.py → __init__.py                                │
│   skill_freshness_ext.py → __init__.py                           │
│   skill_kill_switch.py → __init__.py                             │
│   skill_kya.py → __init__.py                                     │
│   skill_lifecycle.py → __init__.py                               │
│   skill_postmortem.py → __init__.py                              │
│   skill_prompt_opt.py → __init__.py                              │
│   skill_shadow.py → __init__.py                                  │
│   skill_workflow.py → __init__.py                                │
│   skill_translator.py → __init__.py                              │
│   _pipeline.py → __init__.py                                     │
│   __main__.py → __init__.py                                      │
│   context_assembler.py → __init__.py                             │
│   __init___from_orches.py → __init__.py                          │
│   context_injector.py → __init__.py                              │
│   context_pipeline.py → __init__.py                              │
│   pipeline_bridge.py → __init__.py                               │
│   context_budget_tracker.py → __init__.py                        │
│   __init__.py → context_rot_model.py                             │
│   __init__.py → context_evictor.py                               │
│   intent_parser.py → __init__.py                                 │
│   prompt_registry.py → __init__.py                               │
│   Main Force Capital Behavi... → Reflection Frequency Cont...    │
│   Market Maker Behavior Pat... → 多重故障叠加修复策略 Stra...    │
│   Data Quality Self-Managem... → Skill Discovery & Matchin...    │
│   Meta-Level Iteration 元级... → L1-L5 Test Levels L1-L5测...    │
│   基础设施自优化 Base → Conflict & Contradiction ...             │
│   质量保障自驱动 Quality As... → 漂移自适应 Drift Adaptation     │
│   Gate Engine 门禁引擎 → A2A Protocol A2A协议                    │
│   A2A Protocol A2A协议 → Local Model 本地模型                    │
│   Local Model 本地模型 → Permission Guard 权限守卫               │
│   ...还有 397 条 / 397 more edges                                │
└──────────────────────────────────────────────────────────────────┘

**[config_depends]** (136 条 / edges) — 已达显示上限，省略 / limit reached

**[contract]** (22 条 / edges) — 已达显示上限，省略 / limit reached

**[runtime]** (19 条 / edges) — 已达显示上限，省略 / limit reached

**[event]** (16 条 / edges) — 已达显示上限，省略 / limit reached

**[data]** (5 条 / edges) — 已达显示上限，省略 / limit reached

> (最多显示前 50 条依赖边，共 644 条)

```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph.db` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_architecture_diagram.py`
- **维护方式 / Maintenance**: 自动生成，depgraph.db 变更时 CI 自动刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}_architecture.md`，如 `09_d_autonomy_core_architecture.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[prototype]`=原型 / `[unknown]`=未知
