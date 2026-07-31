---
doc_type: architecture_view
title: D_AUTONOMY_CORE 自治核心架构文档
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 10_d_autonomy_core / 自治核心 / Autonomy Core

> **功能简介 / Overview**: 自治核心，负责 AI 自治决策、目标分解和执行编排

> **文档作用 / Purpose**: 展示 自治核心（D_AUTONOMY_CORE）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。

> 本文档由 generate_domain_doc.py 从 depgraph (PostgreSQL) 自动生成
> 数据源: depgraph (PostgreSQL) nodes表 + edges表

## 域基本信息 / Domain Overview

| 字段 | 值 | Field | Value |
|------|------|-------|-------|
| 编号 | 10 | Number | 10 |
| 域ID | D_AUTONOMY_CORE | Domain ID | D_AUTONOMY_CORE |
| 域名称 | 自治核心 | Domain Name | Autonomy Core |
| 层级 | L1 基础平台层 | Layer | L1 Foundation |
| 模块数 | 130 | Module Count | 130 |
| 域内依赖 | 43 | Internal Dependencies | 43 |
| 跨域入边 | 11 | Cross-domain Incoming | 11 |
| 跨域出边 | 59 | Cross-domain Outgoing | 59 |
| 设计态模块 | 0 | Design Modules | 0 |
| 生产态模块 | 130 | Production Modules | 130 |
| 容量 | 130/150 (正常) | Capacity | 130/150 (正常) |
| 描述 | Skill渐进披露(L0永久/L1触发/L2组合/L3按需) | Description | Skill渐进披露(L0永久/L1触发/L2组合/L3按需) |

## 模块分层清单 / Module Layered List

> 按 architecture_layer 分组的模块清单（共 130 个模块 / 130 modules）。

### L1 基础层 / Foundation Layer (130 modules)

| # | 模块路径 / Module Path | 模块名称 / Module Name (功能简介 / Description) | 成熟度 / Maturity | 蓝图 / Blueprint |
|:--:|---------|---------|:---:|:---:|
| 1 | src/zephyr/autonomy_core/__main__.py | agent-spec MOD-INF-019 CLI — 蓝图->Skill 升级... | 生产态 / production |  |
| 2 | src/zephyr/autonomy_core/agent_observability.py | MOD-INF-019: Agent Spec — Agent Observability | 生产态 / production |  |
| 3 | src/zephyr/autonomy_core/all_skill_modules.py | MOD-INF-019: Agent Spec — All Skill Modules | 生产态 / production |  |
| 4 | src/zephyr/autonomy_core/context/atomic_injector.py | atomic_injector.py — 原子注入 (DD101, TASK-019) | 生产态 / production |  |
| 5 | src/zephyr/autonomy_core/context/ce_bootstrap.py | ce_bootstrap.py — CE 自举架构 (B1, DD75, TASK-... | 生产态 / production |  |
| 6 | src/zephyr/autonomy_core/context/ce_explain_cli.py | ce_explain_cli.py — KE inclusion rationale 解... | 生产态 / production |  |
| 7 | src/zephyr/autonomy_core/context/ce_file_lister.py | list_ce_files.py — CE 文件清单生成器 | 生产态 / production |  |
| 8 | src/zephyr/autonomy_core/context/ce_playground_v2.py | ce_playground_v2.py — V2 Playground with full ... | 生产态 / production |  |
| 9 | src/zephyr/autonomy_core/context/ce_vibe_shortcuts.py | ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (T... | 生产态 / production |  |
| 10 | src/zephyr/autonomy_core/context/checkpoint_manager.py | checkpoint_manager.py — Inject 前快照 (DD100, ... | 生产态 / production |  |
| 11 | src/zephyr/autonomy_core/context/cold_start_booster.py | cold_start_booster.py — 冷启动 (DD107, TASK-019) | 生产态 / production |  |
| 12 | src/zephyr/autonomy_core/context/complexity_budget.py | complexity_budget.py — Token 预算复杂度因子 (D... | 生产态 / production |  |
| 13 | src/zephyr/autonomy_core/context/context_assembler.py | ContextAssembler — 上下文装配、校验、影子留档 | 生产态 / production |  |
| 14 | src/zephyr/autonomy_core/context/context_budget.py | TruncationStrategy — TruncationStrategy | 生产态 / production |  |
| 15 | src/zephyr/autonomy_core/context/context_budget_tracker.py | ContextBudgetTracker: token budget management w... | 生产态 / production |  |
| 16 | src/zephyr/autonomy_core/context/context_debt_score.py | context_debt_score.py — 上下文债务评分 (B19, D... | 生产态 / production |  |
| 17 | src/zephyr/autonomy_core/context/context_evaluator.py | context_evaluator.py — AI 引用率评估 (TASK-014... | 生产态 / production |  |
| 18 | src/zephyr/autonomy_core/context/context_evictor.py | context_evictor.py — 三维逐出器 (DD9, TASK-014... | 生产态 / production |  |
| 19 | src/zephyr/autonomy_core/context/context_health_score.py | ContextHealthScore.py — 统一健康分 (B6, DD80, ... | 生产态 / production |  |
| 20 | src/zephyr/autonomy_core/context/context_injector.py | ContextInjector: retrieve and inject relevant k... | 生产态 / production |  |
| 21 | src/zephyr/autonomy_core/context/context_model_strategy.py | context_model_strategy.py — 模型选择策略 (DD11... | 生产态 / production |  |
| 22 | src/zephyr/autonomy_core/context/context_outcome_tracker.py | context_outcome_tracker.py — 因果链追踪 (B14, ... | 生产态 / production |  |
| 23 | src/zephyr/autonomy_core/context/context_pipeline.py | context_pipeline — Context Engine **四段流水线... | 生产态 / production |  |
| 24 | src/zephyr/autonomy_core/context/context_pipeline_auto.py | context_pipeline_auto.py — ContextPipeline 三... | 生产态 / production |  |
| 25 | src/zephyr/autonomy_core/context/context_playground.py | context_playground.py — 上下文沙箱 dry-run (B5... | 生产态 / production |  |
| 26 | src/zephyr/autonomy_core/context/context_rot_model.py | context_rot_model.py — Context Rot 注意力衰减... | 生产态 / production |  |
| 27 | src/zephyr/autonomy_core/context/context_rule_registry.py | context_rule_registry.py | 生产态 / production |  |
| 28 | src/zephyr/autonomy_core/context/context_value_attributio... | context_value_attribution.py — KE 级 ROI 归因 ... | 生产态 / production |  |
| 29 | src/zephyr/autonomy_core/context/contextual_fetch_api.py | contextual_fetch_api.py — HTTP FE 对外 API (DD... | 生产态 / production |  |
| 30 | src/zephyr/autonomy_core/context/curation_loop.py | curation_loop.py — Per-Turn Curation 策展 (DD1... | 生产态 / production |  |
| 31 | src/zephyr/autonomy_core/context/diff_injector.py | diff_injector.py — 增量注入 (DD98, TASK-019) | 生产态 / production |  |
| 32 | src/zephyr/autonomy_core/context/diversity_constraint.py | diversity_constraint.py — 多样性约束 (DD119, T... | 生产态 / production |  |
| 33 | src/zephyr/autonomy_core/context/domain_decay_config.py | domain_decay_config.py — 每领域半衰期 (DD105, ... | 生产态 / production |  |
| 34 | src/zephyr/autonomy_core/context/fallback_staleness_gate.py | fallback_staleness_gate.py — 兜底层自腐检测 (B... | 生产态 / production |  |
| 35 | src/zephyr/autonomy_core/context/integrity_check.py | integrity_check.py — 注入后完整性 (DD106, TASK... | 生产态 / production |  |
| 36 | src/zephyr/autonomy_core/context/memory_bank.py | memory_bank.py — AI 读写结构化持久上下文 (DD: ... | 生产态 / production |  |
| 37 | src/zephyr/autonomy_core/context/mode_manager.py | mode_manager.py — 模式管理器 (DD102, TASK-019) | 生产态 / production |  |
| 38 | src/zephyr/autonomy_core/context/position_optimizer.py | position_optimizer.py — 位置优化 (DD104, TASK-019) | 生产态 / production |  |
| 39 | src/zephyr/autonomy_core/context/shadow_canary.py | shadow_canary.py — 金丝雀部署 (B4, DD78, TASK-... | 生产态 / production |  |
| 40 | src/zephyr/autonomy_core/context/staleness_manager.py | staleness_manager.py — 全局过期检测 (DD112, TA... | 生产态 / production |  |
| 41 | src/zephyr/autonomy_core/context/vector_bridge.py | VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE... | 生产态 / production |  |
| 42 | src/zephyr/autonomy_core/file_autoregister.py | file_autoregister.py | 生产态 / production |  |
| 43 | src/zephyr/autonomy_core/ide_watcher.py | MOD-INF-019: Agent Spec — IDE Watcher | 生产态 / production |  |
| 44 | src/zephyr/autonomy_core/integration/pipeline_bridge.py | PipelineSkillBridge — Agent Spec -> Pipeline ... | 生产态 / production |  |
| 45 | src/zephyr/autonomy_core/phase_planner.py | MOD-INF-019: Agent Spec — Phase Planner | 生产态 / production |  |
| 46 | src/zephyr/autonomy_core/progressive_disclosure_injector.py | progressive_disclosure_injector.py — 渐进式披... | 生产态 / production |  |
| 47 | src/zephyr/autonomy_core/prompt_registry.py | PromptRegistry: YAML-driven Prompt 模板注册表 | 生产态 / production |  |
| 48 | src/zephyr/autonomy_core/self_evolution_fidelity_gate.py | MOD-INF-019: Agent Spec — Self Evolution Fidel... | 生产态 / production |  |
| 49 | src/zephyr/autonomy_core/skill_rbac_registry.py | G-CT-003: Agent Spec -> RBAC capability check. | 生产态 / production |  |
| 50 | src/zephyr/autonomy_core/skills/skill_attention.py | MOD-INF-019: Agent Spec — Skill Attention Mana... | 生产态 / production |  |
| 51 | src/zephyr/autonomy_core/skills/skill_breakage_checker.py | MOD-INF-019: Agent Spec — Skill Breakage Checker | 生产态 / production |  |
| 52 | src/zephyr/autonomy_core/skills/skill_cache_provider.py | MOD-INF-019: Agent Spec — Skill Cache Provider | 生产态 / production |  |
| 53 | src/zephyr/autonomy_core/skills/skill_calibration.py | MOD-INF-019: Agent Spec — Skill Calibration | 生产态 / production |  |
| 54 | src/zephyr/autonomy_core/skills/skill_canary.py | MOD-INF-019: Agent Spec — Skill Canary | 生产态 / production |  |
| 55 | src/zephyr/autonomy_core/skills/skill_cognitive_preservat... | MOD-INF-019: Agent Spec — Skill Cognitive Pres... | 生产态 / production |  |
| 56 | src/zephyr/autonomy_core/skills/skill_compliance.py | MOD-INF-019: Agent Spec — Skill Compliance | 生产态 / production |  |
| 57 | src/zephyr/autonomy_core/skills/skill_consensus.py | MOD-INF-019: Agent Spec — Skill Consensus | 生产态 / production |  |
| 58 | src/zephyr/autonomy_core/skills/skill_constructor.py | MOD-INF-019: Agent Spec — Skill Constructor | 生产态 / production |  |
| 59 | src/zephyr/autonomy_core/skills/skill_context_isolation.py | MOD-INF-019: Agent Spec — Context Isolation | 生产态 / production |  |
| 60 | src/zephyr/autonomy_core/skills/skill_contract.py | MOD-INF-019: Agent Spec — Skill Contract | 生产态 / production |  |
| 61 | src/zephyr/autonomy_core/skills/skill_cross_model.py | MOD-INF-019: Agent Spec — Skill Cross-Model | 生产态 / production |  |
| 62 | src/zephyr/autonomy_core/skills/skill_di.py | MOD-INF-019: Agent Spec — Skill Dependency Inj... | 生产态 / production |  |
| 63 | src/zephyr/autonomy_core/skills/skill_discovery.py | MOD-INF-019: Agent Spec — Skill Discovery | 生产态 / production |  |
| 64 | src/zephyr/autonomy_core/skills/skill_durable.py | MOD-INF-019: Agent Spec — Durable Execution | 生产态 / production |  |
| 65 | src/zephyr/autonomy_core/skills/skill_economics.py | MOD-INF-019: Agent Spec — Skill Economics | 生产态 / production |  |
| 66 | src/zephyr/autonomy_core/skills/skill_efficacy_calibrator.py | MOD-INF-019: Agent Spec — Skill Efficacy Calib... | 生产态 / production |  |
| 67 | src/zephyr/autonomy_core/skills/skill_evaluator.py | MOD-INF-019: Agent Spec — Skill Evaluator | 生产态 / production |  |
| 68 | src/zephyr/autonomy_core/skills/skill_executor.py | skill_executor.py | 生产态 / production |  |
| 69 | src/zephyr/autonomy_core/skills/skill_explain.py | MOD-INF-019: Agent Spec — XAI Explainable Skil... | 生产态 / production |  |
| 70 | src/zephyr/autonomy_core/skills/skill_factory.py | skill_factory.py | 生产态 / production |  |
| 71 | src/zephyr/autonomy_core/skills/skill_feature_flags.py | MOD-INF-019: Agent Spec — Skill Feature Flags | 生产态 / production |  |
| 72 | src/zephyr/autonomy_core/skills/skill_feedback.py | MOD-INF-019: Agent Spec — Skill Feedback Loop | 生产态 / production |  |
| 73 | src/zephyr/autonomy_core/skills/skill_freshness.py | MOD-INF-019: Agent Spec — Skill Freshness Decay | 生产态 / production |  |
| 74 | src/zephyr/autonomy_core/skills/skill_freshness_ext.py | MOD-INF-019: Agent Spec — Skill Freshness Exte... | 生产态 / production |  |
| 75 | src/zephyr/autonomy_core/skills/skill_gitops.py | MOD-INF-019: Agent Spec — Skill GitOps | 生产态 / production |  |
| 76 | src/zephyr/autonomy_core/skills/skill_guardrails.py | MOD-INF-019: Agent Spec — Skill Guardrails | 生产态 / production |  |
| 77 | src/zephyr/autonomy_core/skills/skill_idempotency.py | MOD-INF-019: Agent Spec — Skill Idempotency | 生产态 / production |  |
| 78 | src/zephyr/autonomy_core/skills/skill_kill_switch.py | MOD-INF-019: Agent Spec — Skill Kill Switch | 生产态 / production |  |
| 79 | src/zephyr/autonomy_core/skills/skill_kya.py | MOD-INF-019: Agent Spec — Skill KYA | 生产态 / production |  |
| 80 | src/zephyr/autonomy_core/skills/skill_learning.py | MOD-INF-019: Agent Spec — Skill Self-Learning ... | 生产态 / production |  |
| 81 | src/zephyr/autonomy_core/skills/skill_lifecycle.py | MOD-INF-019: Agent Spec — Skill Lifecycle | 生产态 / production |  |
| 82 | src/zephyr/autonomy_core/skills/skill_lineage.py | MOD-INF-019: Agent Spec — Skill Lineage | 生产态 / production |  |
| 83 | src/zephyr/autonomy_core/skills/skill_loader.py | skill_loader.py | 生产态 / production |  |
| 84 | src/zephyr/autonomy_core/skills/skill_locking.py | MOD-INF-019: Agent Spec — Skill Locking (Produ... | 生产态 / production |  |
| 85 | src/zephyr/autonomy_core/skills/skill_model.py | skill_model.py | 生产态 / production |  |
| 86 | src/zephyr/autonomy_core/skills/skill_model_evolution.py | MOD-INF-019: Agent Spec — Skill Model Evolution | 生产态 / production |  |
| 87 | src/zephyr/autonomy_core/skills/skill_observability.py | MOD-INF-019: Agent Spec — Skill Observability | 生产态 / production |  |
| 88 | src/zephyr/autonomy_core/skills/skill_ontology.py | MOD-INF-019: Agent Spec — Skill Ontology | 生产态 / production |  |
| 89 | src/zephyr/autonomy_core/skills/skill_postmortem.py | MOD-INF-019: Agent Spec — Skill Postmortem (追... | 生产态 / production |  |
| 90 | src/zephyr/autonomy_core/skills/skill_prompt_cache.py | MOD-INF-019: Agent Spec — Skill Prompt Cache | 生产态 / production |  |
| 91 | src/zephyr/autonomy_core/skills/skill_prompt_opt.py | MOD-INF-019: Agent Spec — Skill Prompt Optimizer | 生产态 / production |  |
| 92 | src/zephyr/autonomy_core/skills/skill_registry.py | skill-registry.py —— Skill 注册基座（Phase 14... | 生产态 / production |  |
| 93 | src/zephyr/autonomy_core/skills/skill_resilience.py | MOD-INF-019: Agent Spec — Skill Resilience | 生产态 / production |  |
| 94 | src/zephyr/autonomy_core/skills/skill_risk_mitigator.py | MOD-INF-019: Agent Spec — Skill Risk Mitigator | 生产态 / production |  |
| 95 | src/zephyr/autonomy_core/skills/skill_router.py | skill_router.py | 生产态 / production |  |
| 96 | src/zephyr/autonomy_core/skills/skill_sandbox.py | MOD-INF-019: Agent Spec — Skill Sandbox | 生产态 / production |  |
| 97 | src/zephyr/autonomy_core/skills/skill_schema_registry.py | MOD-INF-019: Agent Spec — Skill Schema Registry | 生产态 / production |  |
| 98 | src/zephyr/autonomy_core/skills/skill_security.py | MOD-INF-019: Agent Spec — Skill Security | 生产态 / production |  |
| 99 | src/zephyr/autonomy_core/skills/skill_shadow.py | MOD-INF-019: Agent Spec — Skill Shadow Deployment | 生产态 / production |  |
| 100 | src/zephyr/autonomy_core/skills/skill_silent_failure.py | MOD-INF-019: Agent Spec — Silent Failure Detector | 生产态 / production |  |
| 101 | src/zephyr/autonomy_core/skills/skill_team_optimizer.py | MOD-INF-019: Agent Spec — Skill Team Optimizer | 生产态 / production |  |
| 102 | src/zephyr/autonomy_core/skills/skill_telemetry.py | MOD-INF-019: Agent Spec — Skill Telemetry | 生产态 / production |  |
| 103 | src/zephyr/autonomy_core/skills/skill_temperature.py | MOD-INF-019: Agent Spec — Skill Temperature | 生产态 / production |  |
| 104 | src/zephyr/autonomy_core/skills/skill_tokenomics.py | MOD-INF-019: Agent Spec — Skill Tokenomics | 生产态 / production |  |
| 105 | src/zephyr/autonomy_core/skills/skill_translator.py | MOD-INF-019: Agent Spec — Skill Translator | 生产态 / production |  |
| 106 | src/zephyr/autonomy_core/skills/skill_workflow.py | MOD-INF-019: Agent Spec — Skill Workflow Orche... | 生产态 / production |  |
| 107 | src/zephyr/autonomy_core/spec_engine.py | MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski... | 生产态 / production |  |
| 108 | src/zephyr/autonomy_core/trigger_router.py | trigger_router.py | 生产态 / production |  |
| 109 | src/zephyr/autonomy_core/vibe_coding_quality_gate.py | VibeCodingQualityGate — 代码质量门禁（stub, te... | 生产态 / production |  |
| 110 | src/zephyr/governance/persistence/intent_keyword_mapper.py | IntentKeywordMapper - Stage 1 of three-stage in... | 生产态 / production |  |
| 111 | src/zephyr/governance/persistence/intent_parser.py | IntentParser · 意图三阶段级联解析器（V-09） | 生产态 / production |  |
| 112 | src/zephyr/infrastructure/system_snapshot.py | SystemSnapshotter — M1 系统状态镜像（CL-017 RI... | 生产态 / production |  |
| 113 | src/zephyr/infrastructure/system_telemetry/otel_instrumen... | otel_instrumentation.py — 全链路 OTel (B12, DD... | 生产态 / production |  |
| 114 | src/zephyr/integration/vector_memory/vector_writer.py | CE 向量写入器 — vectorize_and_store() 生产者 | 生产态 / production |  |
| 115 | src/zephyr/security/llm_defense/llm_security/adversarial_... | adversarial_robustness.py — 对抗鲁棒性 (B8, DD... | 生产态 / production |  |
| 116 | src/zephyr/security/llm_defense/llm_security/alignment_sc... | alignment_scorer.py — 对齐评分 (B11, DD85, TAS... | 生产态 / production |  |
| 117 | src/zephyr/security/llm_defense/llm_security/lsg_pattern_... | lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20... | 生产态 / production |  |
| 118 | src/zephyr/security/llm_defense/llm_security/poisoning_mo... | poisoning_monitor.py — Embed 污染检测 (DD97, T... | 生产态 / production |  |
| 119 | src/zephyr/security/llm_defense/llm_security/sensitivity_... | sensitivity_classifier.py — 数据分级 (B9, DD83... | 生产态 / production |  |
| 120 | src/zephyr/security/llm_defense/llm_security/solo_dev_saf... | solo_dev_safety_net.py — 单人无审查安全网 (B15... | 生产态 / production |  |
| 121 | src/zephyr/shared/ai_guards/config_safety_guard.py | config_safety_guard.py — 配置自毁防护 (B16, DD... | 生产态 / production |  |
| 122 | src/zephyr/shared/blueprint_tools/architecture_context_lo... | architecture_context_loader — 加载 ``generate_... | 生产态 / production |  |
| 123 | src/zephyr/shared/dependency/dependency_tracker.py | dependency_tracker.py — 依赖追踪 (DD116, TASK-020) | 生产态 / production |  |
| 124 | src/zephyr/shared/io/cache_invalidation.py | cache_invalidation.py — 缓存一致性 (DD113, TAS... | 生产态 / production |  |
| 125 | src/zephyr/shared/io/doc_compressor.py | DocCompressor — 文档压缩服务（CL-018 RI 扩展模式） | 生产态 / production |  |
| 126 | src/zephyr/shared/utils/verify_paths.py | verify_paths.py — 代码路径索引验证 (TASK-012) | 生产态 / production |  |
| 127 | tests/automation/test_auto_runtime_e2e.py | F1 AutoRuntimeCore 非mock端到端集成测试 | 生产态 / production |  |
| 128 | tests/f_lifecycle/test_f1_event_trigger.py | F1 事件触发启动测试 | 生产态 / production |  |
| 129 | tests/trading/extreme/test_f14_pipeline_extreme.py | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 | 生产态 / production |  |
| 130 | tests/trading/extreme/test_f1_extreme.py | F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试 | 生产态 / production |  |

## 域内依赖图 / Internal Dependency Diagram

> 依赖图内嵌在本文档中，IDE 可直接渲染显示。参考 decision_index.md 设计，分三个视图：合并全景图、运营态子图、设计态子图（按 design_maturity 实际值拆分）。
>
> **图例说明 / Legend**：
> - **实线边框 = 运营态模块**（production，已上线运行）
> - **虚线边框 = 设计态模块**（design，蓝图阶段，代码未写）
> - **实线箭头 = 运营态依赖**（已生效的依赖关系）
> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）

### 合并全景图（全部模块，标签标注成熟度）

> 展示全部 130 个模块（生产态 130 + 设计态 0），标签标注成熟度。

#### 第 1 页 / 共 5 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_autonomy_core_main_py["(生产态 / production) agent-spec MOD-INF-019 CLI — 蓝图->Skill 升级...<br/>文件: __main__.py"]
    src_zephyr_autonomy_core_agent_observability_py["(生产态 / production) MOD-INF-019: Agent Spec — Agent Observability<br/>文件: agent_observability.py"]
    src_zephyr_autonomy_core_all_skill_modules_py["(生产态 / production) MOD-INF-019: Agent Spec — All Skill Modules<br/>文件: all_skill_modules.py"]
    src_zephyr_autonomy_core_context_atomic_injector_py["(生产态 / production) atomic_injector.py — 原子注入 (DD101, TASK-019)<br/>文件: atomic_injector.py"]
    src_zephyr_autonomy_core_context_ce_bootstrap_py["(生产态 / production) ce_bootstrap.py — CE 自举架构 (B1, DD75, TASK-...<br/>文件: ce_bootstrap.py"]
    src_zephyr_autonomy_core_context_ce_explain_cli_py["(生产态 / production) ce_explain_cli.py — KE inclusion rationale 解...<br/>文件: ce_explain_cli.py"]
    src_zephyr_autonomy_core_context_ce_file_lister_py["(生产态 / production) list_ce_files.py — CE 文件清单生成器<br/>文件: ce_file_lister.py"]
    src_zephyr_autonomy_core_context_ce_playground_v2_py["(生产态 / production) ce_playground_v2.py — V2 Playground with full ...<br/>文件: ce_playground_v2.py"]
    src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py["(生产态 / production) ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (T...<br/>文件: ce_vibe_shortcuts.py"]
    src_zephyr_autonomy_core_context_checkpoint_manager_py["(生产态 / production) checkpoint_manager.py — Inject 前快照 (DD100, ...<br/>文件: checkpoint_manager.py"]
    src_zephyr_autonomy_core_context_cold_start_booster_py["(生产态 / production) cold_start_booster.py — 冷启动 (DD107, TASK-019)<br/>文件: cold_start_booster.py"]
    src_zephyr_autonomy_core_context_complexity_budget_py["(生产态 / production) complexity_budget.py — Token 预算复杂度因子 (D...<br/>文件: complexity_budget.py"]
    src_zephyr_autonomy_core_context_context_budget_py["(生产态 / production) TruncationStrategy — TruncationStrategy<br/>文件: context_budget.py"]
    src_zephyr_autonomy_core_context_context_budget_tracker_py["(生产态 / production) ContextBudgetTracker: token budget management w...<br/>文件: context_budget_tracker.py"]
    src_zephyr_autonomy_core_context_context_debt_score_py["(生产态 / production) context_debt_score.py — 上下文债务评分 (B19, D...<br/>文件: context_debt_score.py"]
    src_zephyr_autonomy_core_context_context_evaluator_py["(生产态 / production) context_evaluator.py — AI 引用率评估 (TASK-014...<br/>文件: context_evaluator.py"]
    src_zephyr_autonomy_core_context_context_evictor_py["(生产态 / production) context_evictor.py — 三维逐出器 (DD9, TASK-014...<br/>文件: context_evictor.py"]
    src_zephyr_autonomy_core_context_context_health_score_py["(生产态 / production) ContextHealthScore.py — 统一健康分 (B6, DD80, ...<br/>文件: context_health_score.py"]
    src_zephyr_autonomy_core_context_context_model_strategy_py["(生产态 / production) context_model_strategy.py — 模型选择策略 (DD11...<br/>文件: context_model_strategy.py"]
    src_zephyr_autonomy_core_context_context_outcome_tracker_py["(生产态 / production) context_outcome_tracker.py — 因果链追踪 (B14, ...<br/>文件: context_outcome_tracker.py"]
    src_zephyr_autonomy_core_context_context_pipeline_auto_py["(生产态 / production) context_pipeline_auto.py — ContextPipeline 三...<br/>文件: context_pipeline_auto.py"]
    src_zephyr_autonomy_core_context_context_playground_py["(生产态 / production) context_playground.py — 上下文沙箱 dry-run (B5...<br/>文件: context_playground.py"]
    src_zephyr_autonomy_core_context_context_rot_model_py["(生产态 / production) context_rot_model.py — Context Rot 注意力衰减...<br/>文件: context_rot_model.py"]
    src_zephyr_autonomy_core_context_context_value_attribution_py["(生产态 / production) context_value_attribution.py — KE 级 ROI 归因 ...<br/>文件: context_value_attribution.py"]
    src_zephyr_autonomy_core_context_contextual_fetch_api_py["(生产态 / production) contextual_fetch_api.py — HTTP FE 对外 API (DD...<br/>文件: contextual_fetch_api.py"]
    src_zephyr_autonomy_core_context_curation_loop_py["(生产态 / production) curation_loop.py — Per-Turn Curation 策展 (DD1...<br/>文件: curation_loop.py"]
    src_zephyr_autonomy_core_main_py ~~~ src_zephyr_autonomy_core_agent_observability_py
    src_zephyr_autonomy_core_agent_observability_py ~~~ src_zephyr_autonomy_core_all_skill_modules_py
    src_zephyr_autonomy_core_all_skill_modules_py ~~~ src_zephyr_autonomy_core_context_atomic_injector_py
    src_zephyr_autonomy_core_context_atomic_injector_py ~~~ src_zephyr_autonomy_core_context_ce_bootstrap_py
    src_zephyr_autonomy_core_context_ce_bootstrap_py ~~~ src_zephyr_autonomy_core_context_ce_explain_cli_py
    src_zephyr_autonomy_core_context_ce_explain_cli_py ~~~ src_zephyr_autonomy_core_context_ce_file_lister_py
    src_zephyr_autonomy_core_context_ce_file_lister_py ~~~ src_zephyr_autonomy_core_context_ce_playground_v2_py
    src_zephyr_autonomy_core_context_ce_playground_v2_py ~~~ src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py
    src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py ~~~ src_zephyr_autonomy_core_context_checkpoint_manager_py
    src_zephyr_autonomy_core_context_checkpoint_manager_py ~~~ src_zephyr_autonomy_core_context_cold_start_booster_py
    src_zephyr_autonomy_core_context_cold_start_booster_py ~~~ src_zephyr_autonomy_core_context_complexity_budget_py
    src_zephyr_autonomy_core_context_complexity_budget_py ~~~ src_zephyr_autonomy_core_context_context_budget_py
    src_zephyr_autonomy_core_context_context_budget_py ~~~ src_zephyr_autonomy_core_context_context_budget_tracker_py
    src_zephyr_autonomy_core_context_context_budget_tracker_py ~~~ src_zephyr_autonomy_core_context_context_debt_score_py
    src_zephyr_autonomy_core_context_context_debt_score_py ~~~ src_zephyr_autonomy_core_context_context_evaluator_py
    src_zephyr_autonomy_core_context_context_evaluator_py ~~~ src_zephyr_autonomy_core_context_context_evictor_py
    src_zephyr_autonomy_core_context_context_evictor_py ~~~ src_zephyr_autonomy_core_context_context_health_score_py
    src_zephyr_autonomy_core_context_context_health_score_py ~~~ src_zephyr_autonomy_core_context_context_model_strategy_py
    src_zephyr_autonomy_core_context_context_model_strategy_py ~~~ src_zephyr_autonomy_core_context_context_outcome_tracker_py
    src_zephyr_autonomy_core_context_context_outcome_tracker_py ~~~ src_zephyr_autonomy_core_context_context_pipeline_auto_py
    src_zephyr_autonomy_core_context_context_pipeline_auto_py ~~~ src_zephyr_autonomy_core_context_context_playground_py
    src_zephyr_autonomy_core_context_context_playground_py ~~~ src_zephyr_autonomy_core_context_context_rot_model_py
    src_zephyr_autonomy_core_context_context_rot_model_py ~~~ src_zephyr_autonomy_core_context_context_value_attribution_py
    src_zephyr_autonomy_core_context_context_value_attribution_py ~~~ src_zephyr_autonomy_core_context_contextual_fetch_api_py
    src_zephyr_autonomy_core_context_contextual_fetch_api_py ~~~ src_zephyr_autonomy_core_context_curation_loop_py
    src_zephyr_autonomy_core_context_context_pipeline_py["(生产态 / production) context_pipeline — Context Engine **四段流水线...<br/>文件: context_pipeline.py"]
    src_zephyr_autonomy_core_context_context_assembler_py["(生产态 / production) ContextAssembler — 上下文装配、校验、影子留档<br/>文件: context_assembler.py"]
    src_zephyr_autonomy_core_context_context_injector_py["(生产态 / production) ContextInjector: retrieve and inject relevant k...<br/>文件: context_injector.py"]
    src_zephyr_autonomy_core_context_context_assembler_py ~~~ src_zephyr_autonomy_core_context_context_injector_py
    src_zephyr_autonomy_core_context_context_rule_registry_py["(生产态 / production) context_rule_registry.py"]
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_rule_registry_py
    src_zephyr_autonomy_core_context_context_pipeline_auto_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_pipeline_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_assembler_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_injector_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_rule_registry_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_context_injector_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_context_budget_tracker_py -->|导入依赖 / import_depends| D_SHARED
    D_ORCHESTRATOR["(生产态 / production) D_ORCHESTRATOR"]
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| D_ORCHESTRATOR
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_autonomy_core_context_context_budget_tracker_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_autonomy_core_context_context_budget_tracker_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_checkpoint_manager_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_context_pipeline_auto_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| D_SHARED
    D_SECURITY["(生产态 / production) D_SECURITY"]
    src_zephyr_autonomy_core_context_context_injector_py -->|导入依赖 / import_depends| D_SECURITY
    src_zephyr_autonomy_core_context_context_pipeline_auto_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_autonomy_core_context_context_budget_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_rule_registry_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_autonomy_core_main_py,src_zephyr_autonomy_core_agent_observability_py,src_zephyr_autonomy_core_all_skill_modules_py,src_zephyr_autonomy_core_context_atomic_injector_py,src_zephyr_autonomy_core_context_ce_bootstrap_py,src_zephyr_autonomy_core_context_ce_explain_cli_py,src_zephyr_autonomy_core_context_ce_file_lister_py,src_zephyr_autonomy_core_context_ce_playground_v2_py,src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py,src_zephyr_autonomy_core_context_checkpoint_manager_py,src_zephyr_autonomy_core_context_cold_start_booster_py,src_zephyr_autonomy_core_context_complexity_budget_py,src_zephyr_autonomy_core_context_context_assembler_py,src_zephyr_autonomy_core_context_context_budget_py,src_zephyr_autonomy_core_context_context_budget_tracker_py,src_zephyr_autonomy_core_context_context_debt_score_py,src_zephyr_autonomy_core_context_context_evaluator_py,src_zephyr_autonomy_core_context_context_evictor_py,src_zephyr_autonomy_core_context_context_health_score_py,src_zephyr_autonomy_core_context_context_injector_py,src_zephyr_autonomy_core_context_context_model_strategy_py,src_zephyr_autonomy_core_context_context_outcome_tracker_py,src_zephyr_autonomy_core_context_context_pipeline_py,src_zephyr_autonomy_core_context_context_pipeline_auto_py,src_zephyr_autonomy_core_context_context_playground_py,src_zephyr_autonomy_core_context_context_rot_model_py,src_zephyr_autonomy_core_context_context_rule_registry_py,src_zephyr_autonomy_core_context_context_value_attribution_py,src_zephyr_autonomy_core_context_contextual_fetch_api_py,src_zephyr_autonomy_core_context_curation_loop_py production
    class D_SHARED,D_ORCHESTRATOR,D_INFRA_RUNTIME,D_SECURITY,D_GOV_CODE_QUALITY external_prod
```

#### 第 2 页 / 共 5 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_autonomy_core_context_diff_injector_py["(生产态 / production) diff_injector.py — 增量注入 (DD98, TASK-019)<br/>文件: diff_injector.py"]
    src_zephyr_autonomy_core_context_diversity_constraint_py["(生产态 / production) diversity_constraint.py — 多样性约束 (DD119, T...<br/>文件: diversity_constraint.py"]
    src_zephyr_autonomy_core_context_domain_decay_config_py["(生产态 / production) domain_decay_config.py — 每领域半衰期 (DD105, ...<br/>文件: domain_decay_config.py"]
    src_zephyr_autonomy_core_context_fallback_staleness_gate_py["(生产态 / production) fallback_staleness_gate.py — 兜底层自腐检测 (B...<br/>文件: fallback_staleness_gate.py"]
    src_zephyr_autonomy_core_context_integrity_check_py["(生产态 / production) integrity_check.py — 注入后完整性 (DD106, TASK...<br/>文件: integrity_check.py"]
    src_zephyr_autonomy_core_context_memory_bank_py["(生产态 / production) memory_bank.py — AI 读写结构化持久上下文 (DD: ...<br/>文件: memory_bank.py"]
    src_zephyr_autonomy_core_context_mode_manager_py["(生产态 / production) mode_manager.py — 模式管理器 (DD102, TASK-019)<br/>文件: mode_manager.py"]
    src_zephyr_autonomy_core_context_position_optimizer_py["(生产态 / production) position_optimizer.py — 位置优化 (DD104, TASK-019)<br/>文件: position_optimizer.py"]
    src_zephyr_autonomy_core_context_shadow_canary_py["(生产态 / production) shadow_canary.py — 金丝雀部署 (B4, DD78, TASK-...<br/>文件: shadow_canary.py"]
    src_zephyr_autonomy_core_context_staleness_manager_py["(生产态 / production) staleness_manager.py — 全局过期检测 (DD112, TA...<br/>文件: staleness_manager.py"]
    src_zephyr_autonomy_core_context_vector_bridge_py["(生产态 / production) VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE...<br/>文件: vector_bridge.py"]
    src_zephyr_autonomy_core_file_autoregister_py["(生产态 / production) file_autoregister.py"]
    src_zephyr_autonomy_core_ide_watcher_py["(生产态 / production) MOD-INF-019: Agent Spec — IDE Watcher<br/>文件: ide_watcher.py"]
    src_zephyr_autonomy_core_integration_pipeline_bridge_py["(生产态 / production) PipelineSkillBridge — Agent Spec -> Pipeline ...<br/>文件: pipeline_bridge.py"]
    src_zephyr_autonomy_core_phase_planner_py["(生产态 / production) MOD-INF-019: Agent Spec — Phase Planner<br/>文件: phase_planner.py"]
    src_zephyr_autonomy_core_progressive_disclosure_injector_py["(生产态 / production) progressive_disclosure_injector.py — 渐进式披...<br/>文件: progressive_disclosure_injector.py"]
    src_zephyr_autonomy_core_prompt_registry_py["(生产态 / production) PromptRegistry: YAML-driven Prompt 模板注册表<br/>文件: prompt_registry.py"]
    src_zephyr_autonomy_core_self_evolution_fidelity_gate_py["(生产态 / production) MOD-INF-019: Agent Spec — Self Evolution Fidel...<br/>文件: self_evolution_fidelity_gate.py"]
    src_zephyr_autonomy_core_skill_rbac_registry_py["(生产态 / production) G-CT-003: Agent Spec -> RBAC capability check.<br/>文件: skill_rbac_registry.py"]
    src_zephyr_autonomy_core_skills_skill_attention_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Attention Mana...<br/>文件: skill_attention.py"]
    src_zephyr_autonomy_core_skills_skill_breakage_checker_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Breakage Checker<br/>文件: skill_breakage_checker.py"]
    src_zephyr_autonomy_core_skills_skill_cache_provider_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Cache Provider<br/>文件: skill_cache_provider.py"]
    src_zephyr_autonomy_core_skills_skill_calibration_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Calibration<br/>文件: skill_calibration.py"]
    src_zephyr_autonomy_core_skills_skill_canary_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Canary<br/>文件: skill_canary.py"]
    src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Cognitive Pres...<br/>文件: skill_cognitive_preservation.py"]
    src_zephyr_autonomy_core_skills_skill_compliance_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Compliance<br/>文件: skill_compliance.py"]
    src_zephyr_autonomy_core_skills_skill_consensus_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Consensus<br/>文件: skill_consensus.py"]
    src_zephyr_autonomy_core_skills_skill_constructor_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Constructor<br/>文件: skill_constructor.py"]
    src_zephyr_autonomy_core_skills_skill_context_isolation_py["(生产态 / production) MOD-INF-019: Agent Spec — Context Isolation<br/>文件: skill_context_isolation.py"]
    src_zephyr_autonomy_core_skills_skill_contract_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Contract<br/>文件: skill_contract.py"]
    src_zephyr_autonomy_core_context_diff_injector_py ~~~ src_zephyr_autonomy_core_context_diversity_constraint_py
    src_zephyr_autonomy_core_context_diversity_constraint_py ~~~ src_zephyr_autonomy_core_context_domain_decay_config_py
    src_zephyr_autonomy_core_context_domain_decay_config_py ~~~ src_zephyr_autonomy_core_context_fallback_staleness_gate_py
    src_zephyr_autonomy_core_context_fallback_staleness_gate_py ~~~ src_zephyr_autonomy_core_context_integrity_check_py
    src_zephyr_autonomy_core_context_integrity_check_py ~~~ src_zephyr_autonomy_core_context_memory_bank_py
    src_zephyr_autonomy_core_context_memory_bank_py ~~~ src_zephyr_autonomy_core_context_mode_manager_py
    src_zephyr_autonomy_core_context_mode_manager_py ~~~ src_zephyr_autonomy_core_context_position_optimizer_py
    src_zephyr_autonomy_core_context_position_optimizer_py ~~~ src_zephyr_autonomy_core_context_shadow_canary_py
    src_zephyr_autonomy_core_context_shadow_canary_py ~~~ src_zephyr_autonomy_core_context_staleness_manager_py
    src_zephyr_autonomy_core_context_staleness_manager_py ~~~ src_zephyr_autonomy_core_context_vector_bridge_py
    src_zephyr_autonomy_core_context_vector_bridge_py ~~~ src_zephyr_autonomy_core_file_autoregister_py
    src_zephyr_autonomy_core_file_autoregister_py ~~~ src_zephyr_autonomy_core_ide_watcher_py
    src_zephyr_autonomy_core_ide_watcher_py ~~~ src_zephyr_autonomy_core_integration_pipeline_bridge_py
    src_zephyr_autonomy_core_integration_pipeline_bridge_py ~~~ src_zephyr_autonomy_core_phase_planner_py
    src_zephyr_autonomy_core_phase_planner_py ~~~ src_zephyr_autonomy_core_progressive_disclosure_injector_py
    src_zephyr_autonomy_core_progressive_disclosure_injector_py ~~~ src_zephyr_autonomy_core_prompt_registry_py
    src_zephyr_autonomy_core_prompt_registry_py ~~~ src_zephyr_autonomy_core_self_evolution_fidelity_gate_py
    src_zephyr_autonomy_core_self_evolution_fidelity_gate_py ~~~ src_zephyr_autonomy_core_skill_rbac_registry_py
    src_zephyr_autonomy_core_skill_rbac_registry_py ~~~ src_zephyr_autonomy_core_skills_skill_attention_py
    src_zephyr_autonomy_core_skills_skill_attention_py ~~~ src_zephyr_autonomy_core_skills_skill_breakage_checker_py
    src_zephyr_autonomy_core_skills_skill_breakage_checker_py ~~~ src_zephyr_autonomy_core_skills_skill_cache_provider_py
    src_zephyr_autonomy_core_skills_skill_cache_provider_py ~~~ src_zephyr_autonomy_core_skills_skill_calibration_py
    src_zephyr_autonomy_core_skills_skill_calibration_py ~~~ src_zephyr_autonomy_core_skills_skill_canary_py
    src_zephyr_autonomy_core_skills_skill_canary_py ~~~ src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py
    src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py ~~~ src_zephyr_autonomy_core_skills_skill_compliance_py
    src_zephyr_autonomy_core_skills_skill_compliance_py ~~~ src_zephyr_autonomy_core_skills_skill_consensus_py
    src_zephyr_autonomy_core_skills_skill_consensus_py ~~~ src_zephyr_autonomy_core_skills_skill_constructor_py
    src_zephyr_autonomy_core_skills_skill_constructor_py ~~~ src_zephyr_autonomy_core_skills_skill_context_isolation_py
    src_zephyr_autonomy_core_skills_skill_context_isolation_py ~~~ src_zephyr_autonomy_core_skills_skill_contract_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    src_zephyr_autonomy_core_prompt_registry_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_autonomy_core_prompt_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_prompt_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_file_autoregister_py -->|导入依赖 / import_depends| D_SHARED
    D_ORCHESTRATOR["(生产态 / production) D_ORCHESTRATOR"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_vector_bridge_py
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_vector_bridge_py
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_autonomy_core_integration_pipeline_bridge_py
    D_SECURITY["(生产态 / production) D_SECURITY"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skill_rbac_registry_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_autonomy_core_context_diff_injector_py,src_zephyr_autonomy_core_context_diversity_constraint_py,src_zephyr_autonomy_core_context_domain_decay_config_py,src_zephyr_autonomy_core_context_fallback_staleness_gate_py,src_zephyr_autonomy_core_context_integrity_check_py,src_zephyr_autonomy_core_context_memory_bank_py,src_zephyr_autonomy_core_context_mode_manager_py,src_zephyr_autonomy_core_context_position_optimizer_py,src_zephyr_autonomy_core_context_shadow_canary_py,src_zephyr_autonomy_core_context_staleness_manager_py,src_zephyr_autonomy_core_context_vector_bridge_py,src_zephyr_autonomy_core_file_autoregister_py,src_zephyr_autonomy_core_ide_watcher_py,src_zephyr_autonomy_core_integration_pipeline_bridge_py,src_zephyr_autonomy_core_phase_planner_py,src_zephyr_autonomy_core_progressive_disclosure_injector_py,src_zephyr_autonomy_core_prompt_registry_py,src_zephyr_autonomy_core_self_evolution_fidelity_gate_py,src_zephyr_autonomy_core_skill_rbac_registry_py,src_zephyr_autonomy_core_skills_skill_attention_py,src_zephyr_autonomy_core_skills_skill_breakage_checker_py,src_zephyr_autonomy_core_skills_skill_cache_provider_py,src_zephyr_autonomy_core_skills_skill_calibration_py,src_zephyr_autonomy_core_skills_skill_canary_py,src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py,src_zephyr_autonomy_core_skills_skill_compliance_py,src_zephyr_autonomy_core_skills_skill_consensus_py,src_zephyr_autonomy_core_skills_skill_constructor_py,src_zephyr_autonomy_core_skills_skill_context_isolation_py,src_zephyr_autonomy_core_skills_skill_contract_py production
    class D_INFRA_RUNTIME,D_SHARED,D_ORCHESTRATOR,D_FEEDBACK_LOOP,D_INTEGRATION,D_SECURITY external_prod
```

#### 第 3 页 / 共 5 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_autonomy_core_skills_skill_cross_model_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Cross-Model<br/>文件: skill_cross_model.py"]
    src_zephyr_autonomy_core_skills_skill_di_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Dependency Inj...<br/>文件: skill_di.py"]
    src_zephyr_autonomy_core_skills_skill_discovery_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Discovery<br/>文件: skill_discovery.py"]
    src_zephyr_autonomy_core_skills_skill_durable_py["(生产态 / production) MOD-INF-019: Agent Spec — Durable Execution<br/>文件: skill_durable.py"]
    src_zephyr_autonomy_core_skills_skill_economics_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Economics<br/>文件: skill_economics.py"]
    src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Efficacy Calib...<br/>文件: skill_efficacy_calibrator.py"]
    src_zephyr_autonomy_core_skills_skill_executor_py["(生产态 / production) skill_executor.py"]
    src_zephyr_autonomy_core_skills_skill_explain_py["(生产态 / production) MOD-INF-019: Agent Spec — XAI Explainable Skil...<br/>文件: skill_explain.py"]
    src_zephyr_autonomy_core_skills_skill_feature_flags_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Feature Flags<br/>文件: skill_feature_flags.py"]
    src_zephyr_autonomy_core_skills_skill_feedback_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Feedback Loop<br/>文件: skill_feedback.py"]
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Freshness Exte...<br/>文件: skill_freshness_ext.py"]
    src_zephyr_autonomy_core_skills_skill_gitops_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill GitOps<br/>文件: skill_gitops.py"]
    src_zephyr_autonomy_core_skills_skill_guardrails_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Guardrails<br/>文件: skill_guardrails.py"]
    src_zephyr_autonomy_core_skills_skill_idempotency_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Idempotency<br/>文件: skill_idempotency.py"]
    src_zephyr_autonomy_core_skills_skill_kya_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill KYA<br/>文件: skill_kya.py"]
    src_zephyr_autonomy_core_skills_skill_learning_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Self-Learning ...<br/>文件: skill_learning.py"]
    src_zephyr_autonomy_core_skills_skill_lineage_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Lineage<br/>文件: skill_lineage.py"]
    src_zephyr_autonomy_core_skills_skill_locking_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Locking (Produ...<br/>文件: skill_locking.py"]
    src_zephyr_autonomy_core_skills_skill_observability_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Observability<br/>文件: skill_observability.py"]
    src_zephyr_autonomy_core_skills_skill_ontology_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Ontology<br/>文件: skill_ontology.py"]
    src_zephyr_autonomy_core_skills_skill_postmortem_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Postmortem (追...<br/>文件: skill_postmortem.py"]
    src_zephyr_autonomy_core_skills_skill_prompt_cache_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Prompt Cache<br/>文件: skill_prompt_cache.py"]
    src_zephyr_autonomy_core_skills_skill_cross_model_py ~~~ src_zephyr_autonomy_core_skills_skill_di_py
    src_zephyr_autonomy_core_skills_skill_di_py ~~~ src_zephyr_autonomy_core_skills_skill_discovery_py
    src_zephyr_autonomy_core_skills_skill_discovery_py ~~~ src_zephyr_autonomy_core_skills_skill_durable_py
    src_zephyr_autonomy_core_skills_skill_durable_py ~~~ src_zephyr_autonomy_core_skills_skill_economics_py
    src_zephyr_autonomy_core_skills_skill_economics_py ~~~ src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py
    src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py ~~~ src_zephyr_autonomy_core_skills_skill_executor_py
    src_zephyr_autonomy_core_skills_skill_executor_py ~~~ src_zephyr_autonomy_core_skills_skill_explain_py
    src_zephyr_autonomy_core_skills_skill_explain_py ~~~ src_zephyr_autonomy_core_skills_skill_feature_flags_py
    src_zephyr_autonomy_core_skills_skill_feature_flags_py ~~~ src_zephyr_autonomy_core_skills_skill_feedback_py
    src_zephyr_autonomy_core_skills_skill_feedback_py ~~~ src_zephyr_autonomy_core_skills_skill_freshness_ext_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py ~~~ src_zephyr_autonomy_core_skills_skill_gitops_py
    src_zephyr_autonomy_core_skills_skill_gitops_py ~~~ src_zephyr_autonomy_core_skills_skill_guardrails_py
    src_zephyr_autonomy_core_skills_skill_guardrails_py ~~~ src_zephyr_autonomy_core_skills_skill_idempotency_py
    src_zephyr_autonomy_core_skills_skill_idempotency_py ~~~ src_zephyr_autonomy_core_skills_skill_kya_py
    src_zephyr_autonomy_core_skills_skill_kya_py ~~~ src_zephyr_autonomy_core_skills_skill_learning_py
    src_zephyr_autonomy_core_skills_skill_learning_py ~~~ src_zephyr_autonomy_core_skills_skill_lineage_py
    src_zephyr_autonomy_core_skills_skill_lineage_py ~~~ src_zephyr_autonomy_core_skills_skill_locking_py
    src_zephyr_autonomy_core_skills_skill_locking_py ~~~ src_zephyr_autonomy_core_skills_skill_observability_py
    src_zephyr_autonomy_core_skills_skill_observability_py ~~~ src_zephyr_autonomy_core_skills_skill_ontology_py
    src_zephyr_autonomy_core_skills_skill_ontology_py ~~~ src_zephyr_autonomy_core_skills_skill_postmortem_py
    src_zephyr_autonomy_core_skills_skill_postmortem_py ~~~ src_zephyr_autonomy_core_skills_skill_prompt_cache_py
    src_zephyr_autonomy_core_skills_skill_evaluator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Evaluator<br/>文件: skill_evaluator.py"]
    src_zephyr_autonomy_core_skills_skill_factory_py["(生产态 / production) skill_factory.py"]
    src_zephyr_autonomy_core_skills_skill_kill_switch_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Kill Switch<br/>文件: skill_kill_switch.py"]
    src_zephyr_autonomy_core_skills_skill_lifecycle_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Lifecycle<br/>文件: skill_lifecycle.py"]
    src_zephyr_autonomy_core_skills_skill_model_evolution_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Model Evolution<br/>文件: skill_model_evolution.py"]
    src_zephyr_autonomy_core_skills_skill_evaluator_py ~~~ src_zephyr_autonomy_core_skills_skill_factory_py
    src_zephyr_autonomy_core_skills_skill_factory_py ~~~ src_zephyr_autonomy_core_skills_skill_kill_switch_py
    src_zephyr_autonomy_core_skills_skill_kill_switch_py ~~~ src_zephyr_autonomy_core_skills_skill_lifecycle_py
    src_zephyr_autonomy_core_skills_skill_lifecycle_py ~~~ src_zephyr_autonomy_core_skills_skill_model_evolution_py
    src_zephyr_autonomy_core_skills_skill_freshness_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Freshness Decay<br/>文件: skill_freshness.py"]
    src_zephyr_autonomy_core_skills_skill_loader_py["(生产态 / production) skill_loader.py"]
    src_zephyr_autonomy_core_skills_skill_model_py["(生产态 / production) skill_model.py"]
    src_zephyr_autonomy_core_skills_skill_freshness_py ~~~ src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_loader_py ~~~ src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_discovery_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_factory_py
    src_zephyr_autonomy_core_skills_skill_discovery_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_explain_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_evaluator_py
    src_zephyr_autonomy_core_skills_skill_explain_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_evolution_py
    src_zephyr_autonomy_core_skills_skill_evaluator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_evaluator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_executor_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_feedback_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_feedback_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_kill_switch_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_lifecycle_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_kill_switch_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_lifecycle_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_kya_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_postmortem_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    src_zephyr_autonomy_core_skills_skill_executor_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_GOV_RULE["(生产态 / production) D_GOV_RULE"]
    src_zephyr_autonomy_core_skills_skill_executor_py -->|导入依赖 / import_depends| D_GOV_RULE
    src_zephyr_autonomy_core_skills_skill_feedback_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_skills_skill_factory_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_autonomy_core_skills_skill_executor_py -->|导入依赖 / import_depends| D_INTEGRATION
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_ext_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_feedback_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_lifecycle_py
    D_GOV_REPAIR["(生产态 / production) D_GOV_REPAIR"]
    D_GOV_REPAIR -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_executor_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_autonomy_core_skills_skill_cross_model_py,src_zephyr_autonomy_core_skills_skill_di_py,src_zephyr_autonomy_core_skills_skill_discovery_py,src_zephyr_autonomy_core_skills_skill_durable_py,src_zephyr_autonomy_core_skills_skill_economics_py,src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py,src_zephyr_autonomy_core_skills_skill_evaluator_py,src_zephyr_autonomy_core_skills_skill_executor_py,src_zephyr_autonomy_core_skills_skill_explain_py,src_zephyr_autonomy_core_skills_skill_factory_py,src_zephyr_autonomy_core_skills_skill_feature_flags_py,src_zephyr_autonomy_core_skills_skill_feedback_py,src_zephyr_autonomy_core_skills_skill_freshness_py,src_zephyr_autonomy_core_skills_skill_freshness_ext_py,src_zephyr_autonomy_core_skills_skill_gitops_py,src_zephyr_autonomy_core_skills_skill_guardrails_py,src_zephyr_autonomy_core_skills_skill_idempotency_py,src_zephyr_autonomy_core_skills_skill_kill_switch_py,src_zephyr_autonomy_core_skills_skill_kya_py,src_zephyr_autonomy_core_skills_skill_learning_py,src_zephyr_autonomy_core_skills_skill_lifecycle_py,src_zephyr_autonomy_core_skills_skill_lineage_py,src_zephyr_autonomy_core_skills_skill_loader_py,src_zephyr_autonomy_core_skills_skill_locking_py,src_zephyr_autonomy_core_skills_skill_model_py,src_zephyr_autonomy_core_skills_skill_model_evolution_py,src_zephyr_autonomy_core_skills_skill_observability_py,src_zephyr_autonomy_core_skills_skill_ontology_py,src_zephyr_autonomy_core_skills_skill_postmortem_py,src_zephyr_autonomy_core_skills_skill_prompt_cache_py production
    class D_SHARED,D_GOV_AUDIT,D_GOV_RULE,D_INTEGRATION,D_INFRA_RUNTIME,D_GOV_REPAIR external_prod
```

#### 第 4 页 / 共 5 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_autonomy_core_skills_skill_prompt_opt_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Prompt Optimizer<br/>文件: skill_prompt_opt.py"]
    src_zephyr_autonomy_core_skills_skill_registry_py["(生产态 / production) skill-registry.py —— Skill 注册基座（Phase 14...<br/>文件: skill_registry.py"]
    src_zephyr_autonomy_core_skills_skill_resilience_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Resilience<br/>文件: skill_resilience.py"]
    src_zephyr_autonomy_core_skills_skill_risk_mitigator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Risk Mitigator<br/>文件: skill_risk_mitigator.py"]
    src_zephyr_autonomy_core_skills_skill_router_py["(生产态 / production) skill_router.py"]
    src_zephyr_autonomy_core_skills_skill_sandbox_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Sandbox<br/>文件: skill_sandbox.py"]
    src_zephyr_autonomy_core_skills_skill_schema_registry_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Schema Registry<br/>文件: skill_schema_registry.py"]
    src_zephyr_autonomy_core_skills_skill_security_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Security<br/>文件: skill_security.py"]
    src_zephyr_autonomy_core_skills_skill_shadow_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Shadow Deployment<br/>文件: skill_shadow.py"]
    src_zephyr_autonomy_core_skills_skill_silent_failure_py["(生产态 / production) MOD-INF-019: Agent Spec — Silent Failure Detector<br/>文件: skill_silent_failure.py"]
    src_zephyr_autonomy_core_skills_skill_team_optimizer_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Team Optimizer<br/>文件: skill_team_optimizer.py"]
    src_zephyr_autonomy_core_skills_skill_telemetry_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Telemetry<br/>文件: skill_telemetry.py"]
    src_zephyr_autonomy_core_skills_skill_temperature_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Temperature<br/>文件: skill_temperature.py"]
    src_zephyr_autonomy_core_skills_skill_tokenomics_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Tokenomics<br/>文件: skill_tokenomics.py"]
    src_zephyr_autonomy_core_skills_skill_translator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Translator<br/>文件: skill_translator.py"]
    src_zephyr_autonomy_core_skills_skill_workflow_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Workflow Orche...<br/>文件: skill_workflow.py"]
    src_zephyr_autonomy_core_spec_engine_py["(生产态 / production) MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski...<br/>文件: spec_engine.py"]
    src_zephyr_autonomy_core_vibe_coding_quality_gate_py["(生产态 / production) VibeCodingQualityGate — 代码质量门禁（stub, te...<br/>文件: vibe_coding_quality_gate.py"]
    src_zephyr_governance_persistence_intent_parser_py["(生产态 / production) IntentParser · 意图三阶段级联解析器（V-09）<br/>文件: intent_parser.py"]
    src_zephyr_infrastructure_system_snapshot_py["(生产态 / production) SystemSnapshotter — M1 系统状态镜像（CL-017 RI...<br/>文件: system_snapshot.py"]
    src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py["(生产态 / production) otel_instrumentation.py — 全链路 OTel (B12, DD...<br/>文件: otel_instrumentation.py"]
    src_zephyr_integration_vector_memory_vector_writer_py["(生产态 / production) CE 向量写入器 — vectorize_and_store() 生产者<br/>文件: vector_writer.py"]
    src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py["(生产态 / production) adversarial_robustness.py — 对抗鲁棒性 (B8, DD...<br/>文件: adversarial_robustness.py"]
    src_zephyr_security_llm_defense_llm_security_alignment_scorer_py["(生产态 / production) alignment_scorer.py — 对齐评分 (B11, DD85, TAS...<br/>文件: alignment_scorer.py"]
    src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py["(生产态 / production) lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20...<br/>文件: lsg_pattern_tracker.py"]
    src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py["(生产态 / production) poisoning_monitor.py — Embed 污染检测 (DD97, T...<br/>文件: poisoning_monitor.py"]
    src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py["(生产态 / production) sensitivity_classifier.py — 数据分级 (B9, DD83...<br/>文件: sensitivity_classifier.py"]
    src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py["(生产态 / production) solo_dev_safety_net.py — 单人无审查安全网 (B15...<br/>文件: solo_dev_safety_net.py"]
    src_zephyr_autonomy_core_skills_skill_prompt_opt_py ~~~ src_zephyr_autonomy_core_skills_skill_registry_py
    src_zephyr_autonomy_core_skills_skill_registry_py ~~~ src_zephyr_autonomy_core_skills_skill_resilience_py
    src_zephyr_autonomy_core_skills_skill_resilience_py ~~~ src_zephyr_autonomy_core_skills_skill_risk_mitigator_py
    src_zephyr_autonomy_core_skills_skill_risk_mitigator_py ~~~ src_zephyr_autonomy_core_skills_skill_router_py
    src_zephyr_autonomy_core_skills_skill_router_py ~~~ src_zephyr_autonomy_core_skills_skill_sandbox_py
    src_zephyr_autonomy_core_skills_skill_sandbox_py ~~~ src_zephyr_autonomy_core_skills_skill_schema_registry_py
    src_zephyr_autonomy_core_skills_skill_schema_registry_py ~~~ src_zephyr_autonomy_core_skills_skill_security_py
    src_zephyr_autonomy_core_skills_skill_security_py ~~~ src_zephyr_autonomy_core_skills_skill_shadow_py
    src_zephyr_autonomy_core_skills_skill_shadow_py ~~~ src_zephyr_autonomy_core_skills_skill_silent_failure_py
    src_zephyr_autonomy_core_skills_skill_silent_failure_py ~~~ src_zephyr_autonomy_core_skills_skill_team_optimizer_py
    src_zephyr_autonomy_core_skills_skill_team_optimizer_py ~~~ src_zephyr_autonomy_core_skills_skill_telemetry_py
    src_zephyr_autonomy_core_skills_skill_telemetry_py ~~~ src_zephyr_autonomy_core_skills_skill_temperature_py
    src_zephyr_autonomy_core_skills_skill_temperature_py ~~~ src_zephyr_autonomy_core_skills_skill_tokenomics_py
    src_zephyr_autonomy_core_skills_skill_tokenomics_py ~~~ src_zephyr_autonomy_core_skills_skill_translator_py
    src_zephyr_autonomy_core_skills_skill_translator_py ~~~ src_zephyr_autonomy_core_skills_skill_workflow_py
    src_zephyr_autonomy_core_skills_skill_workflow_py ~~~ src_zephyr_autonomy_core_spec_engine_py
    src_zephyr_autonomy_core_spec_engine_py ~~~ src_zephyr_autonomy_core_vibe_coding_quality_gate_py
    src_zephyr_autonomy_core_vibe_coding_quality_gate_py ~~~ src_zephyr_governance_persistence_intent_parser_py
    src_zephyr_governance_persistence_intent_parser_py ~~~ src_zephyr_infrastructure_system_snapshot_py
    src_zephyr_infrastructure_system_snapshot_py ~~~ src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py
    src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py ~~~ src_zephyr_integration_vector_memory_vector_writer_py
    src_zephyr_integration_vector_memory_vector_writer_py ~~~ src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py
    src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py ~~~ src_zephyr_security_llm_defense_llm_security_alignment_scorer_py
    src_zephyr_security_llm_defense_llm_security_alignment_scorer_py ~~~ src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py
    src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py ~~~ src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py
    src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py ~~~ src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py
    src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py ~~~ src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py
    src_zephyr_autonomy_core_trigger_router_py["(生产态 / production) trigger_router.py"]
    src_zephyr_governance_persistence_intent_keyword_mapper_py["(生产态 / production) IntentKeywordMapper - Stage 1 of three-stage in...<br/>文件: intent_keyword_mapper.py"]
    src_zephyr_autonomy_core_trigger_router_py ~~~ src_zephyr_governance_persistence_intent_keyword_mapper_py
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_trigger_router_py
    src_zephyr_governance_persistence_intent_parser_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_intent_keyword_mapper_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_infrastructure_system_snapshot_py -->|导入依赖 / import_depends| D_SHARED
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_governance_persistence_intent_keyword_mapper_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_skills_skill_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_skills_skill_router_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_autonomy_core_skills_skill_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_skills_skill_registry_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_integration_vector_memory_vector_writer_py -->|导入依赖 / import_depends| D_INTEGRATION
    src_zephyr_governance_persistence_intent_parser_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_system_snapshot_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    src_zephyr_autonomy_core_skills_skill_sandbox_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_ORCHESTRATOR["(生产态 / production) D_ORCHESTRATOR"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vector_writer_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_governance_persistence_intent_keyword_mapper_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_autonomy_core_skills_skill_prompt_opt_py,src_zephyr_autonomy_core_skills_skill_registry_py,src_zephyr_autonomy_core_skills_skill_resilience_py,src_zephyr_autonomy_core_skills_skill_risk_mitigator_py,src_zephyr_autonomy_core_skills_skill_router_py,src_zephyr_autonomy_core_skills_skill_sandbox_py,src_zephyr_autonomy_core_skills_skill_schema_registry_py,src_zephyr_autonomy_core_skills_skill_security_py,src_zephyr_autonomy_core_skills_skill_shadow_py,src_zephyr_autonomy_core_skills_skill_silent_failure_py,src_zephyr_autonomy_core_skills_skill_team_optimizer_py,src_zephyr_autonomy_core_skills_skill_telemetry_py,src_zephyr_autonomy_core_skills_skill_temperature_py,src_zephyr_autonomy_core_skills_skill_tokenomics_py,src_zephyr_autonomy_core_skills_skill_translator_py,src_zephyr_autonomy_core_skills_skill_workflow_py,src_zephyr_autonomy_core_spec_engine_py,src_zephyr_autonomy_core_trigger_router_py,src_zephyr_autonomy_core_vibe_coding_quality_gate_py,src_zephyr_governance_persistence_intent_keyword_mapper_py,src_zephyr_governance_persistence_intent_parser_py,src_zephyr_infrastructure_system_snapshot_py,src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py,src_zephyr_integration_vector_memory_vector_writer_py,src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py,src_zephyr_security_llm_defense_llm_security_alignment_scorer_py,src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py,src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py,src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py,src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py production
    class D_SHARED,D_INTEGRATION,D_GOV_AUDIT,D_ORCHESTRATOR external_prod
```

#### 第 5 页 / 共 5 页

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_shared_ai_guards_config_safety_guard_py["(生产态 / production) config_safety_guard.py — 配置自毁防护 (B16, DD...<br/>文件: config_safety_guard.py"]
    src_zephyr_shared_blueprint_tools_architecture_context_loader_py["(生产态 / production) architecture_context_loader — 加载 ``generate_...<br/>文件: architecture_context_loader.py"]
    src_zephyr_shared_dependency_dependency_tracker_py["(生产态 / production) dependency_tracker.py — 依赖追踪 (DD116, TASK-020)<br/>文件: dependency_tracker.py"]
    src_zephyr_shared_io_cache_invalidation_py["(生产态 / production) cache_invalidation.py — 缓存一致性 (DD113, TAS...<br/>文件: cache_invalidation.py"]
    src_zephyr_shared_io_doc_compressor_py["(生产态 / production) DocCompressor — 文档压缩服务（CL-018 RI 扩展模式）<br/>文件: doc_compressor.py"]
    src_zephyr_shared_utils_verify_paths_py["(生产态 / production) verify_paths.py — 代码路径索引验证 (TASK-012)<br/>文件: verify_paths.py"]
    tests_automation_test_auto_runtime_e2e_py["(生产态 / production) F1 AutoRuntimeCore 非mock端到端集成测试<br/>文件: test_auto_runtime_e2e.py"]
    tests_f_lifecycle_test_f1_event_trigger_py["(生产态 / production) F1 事件触发启动测试<br/>文件: test_f1_event_trigger.py"]
    tests_trading_extreme_test_f14_pipeline_extreme_py["(生产态 / production) F14 管线编排/反馈环 — 红蓝对抗端到端极端测试<br/>文件: test_f14_pipeline_extreme.py"]
    tests_trading_extreme_test_f1_extreme_py["(生产态 / production) F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试<br/>文件: test_f1_extreme.py"]
    src_zephyr_shared_ai_guards_config_safety_guard_py ~~~ src_zephyr_shared_blueprint_tools_architecture_context_loader_py
    src_zephyr_shared_blueprint_tools_architecture_context_loader_py ~~~ src_zephyr_shared_dependency_dependency_tracker_py
    src_zephyr_shared_dependency_dependency_tracker_py ~~~ src_zephyr_shared_io_cache_invalidation_py
    src_zephyr_shared_io_cache_invalidation_py ~~~ src_zephyr_shared_io_doc_compressor_py
    src_zephyr_shared_io_doc_compressor_py ~~~ src_zephyr_shared_utils_verify_paths_py
    src_zephyr_shared_utils_verify_paths_py ~~~ tests_automation_test_auto_runtime_e2e_py
    tests_automation_test_auto_runtime_e2e_py ~~~ tests_f_lifecycle_test_f1_event_trigger_py
    tests_f_lifecycle_test_f1_event_trigger_py ~~~ tests_trading_extreme_test_f14_pipeline_extreme_py
    tests_trading_extreme_test_f14_pipeline_extreme_py ~~~ tests_trading_extreme_test_f1_extreme_py
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f1_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_shared_io_doc_compressor_py -->|导入依赖 / import_depends| D_SHARED
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_FEEDBACK_LOOP
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f1_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f1_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f1_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_shared_ai_guards_config_safety_guard_py,src_zephyr_shared_blueprint_tools_architecture_context_loader_py,src_zephyr_shared_dependency_dependency_tracker_py,src_zephyr_shared_io_cache_invalidation_py,src_zephyr_shared_io_doc_compressor_py,src_zephyr_shared_utils_verify_paths_py,tests_automation_test_auto_runtime_e2e_py,tests_f_lifecycle_test_f1_event_trigger_py,tests_trading_extreme_test_f14_pipeline_extreme_py,tests_trading_extreme_test_f1_extreme_py production
    class D_INFRA_RUNTIME,D_SHARED,D_FEEDBACK_LOOP external_prod
```

### 运营态子图（仅 design_maturity=production 的模块和依赖）

> 仅展示已上线运行的模块（共 130 个，43 条域内依赖）。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
flowchart TD
    src_zephyr_autonomy_core_main_py["(生产态 / production) agent-spec MOD-INF-019 CLI — 蓝图->Skill 升级...<br/>文件: __main__.py"]
    src_zephyr_autonomy_core_agent_observability_py["(生产态 / production) MOD-INF-019: Agent Spec — Agent Observability<br/>文件: agent_observability.py"]
    src_zephyr_autonomy_core_all_skill_modules_py["(生产态 / production) MOD-INF-019: Agent Spec — All Skill Modules<br/>文件: all_skill_modules.py"]
    src_zephyr_autonomy_core_context_atomic_injector_py["(生产态 / production) atomic_injector.py — 原子注入 (DD101, TASK-019)<br/>文件: atomic_injector.py"]
    src_zephyr_autonomy_core_context_ce_bootstrap_py["(生产态 / production) ce_bootstrap.py — CE 自举架构 (B1, DD75, TASK-...<br/>文件: ce_bootstrap.py"]
    src_zephyr_autonomy_core_context_ce_explain_cli_py["(生产态 / production) ce_explain_cli.py — KE inclusion rationale 解...<br/>文件: ce_explain_cli.py"]
    src_zephyr_autonomy_core_context_ce_file_lister_py["(生产态 / production) list_ce_files.py — CE 文件清单生成器<br/>文件: ce_file_lister.py"]
    src_zephyr_autonomy_core_context_ce_playground_v2_py["(生产态 / production) ce_playground_v2.py — V2 Playground with full ...<br/>文件: ce_playground_v2.py"]
    src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py["(生产态 / production) ce_vibe_shortcuts.py — Vibe/Strict 模式切换 (T...<br/>文件: ce_vibe_shortcuts.py"]
    src_zephyr_autonomy_core_context_checkpoint_manager_py["(生产态 / production) checkpoint_manager.py — Inject 前快照 (DD100, ...<br/>文件: checkpoint_manager.py"]
    src_zephyr_autonomy_core_context_cold_start_booster_py["(生产态 / production) cold_start_booster.py — 冷启动 (DD107, TASK-019)<br/>文件: cold_start_booster.py"]
    src_zephyr_autonomy_core_context_complexity_budget_py["(生产态 / production) complexity_budget.py — Token 预算复杂度因子 (D...<br/>文件: complexity_budget.py"]
    src_zephyr_autonomy_core_context_context_budget_py["(生产态 / production) TruncationStrategy — TruncationStrategy<br/>文件: context_budget.py"]
    src_zephyr_autonomy_core_context_context_budget_tracker_py["(生产态 / production) ContextBudgetTracker: token budget management w...<br/>文件: context_budget_tracker.py"]
    src_zephyr_autonomy_core_context_context_debt_score_py["(生产态 / production) context_debt_score.py — 上下文债务评分 (B19, D...<br/>文件: context_debt_score.py"]
    src_zephyr_autonomy_core_context_context_evaluator_py["(生产态 / production) context_evaluator.py — AI 引用率评估 (TASK-014...<br/>文件: context_evaluator.py"]
    src_zephyr_autonomy_core_context_context_evictor_py["(生产态 / production) context_evictor.py — 三维逐出器 (DD9, TASK-014...<br/>文件: context_evictor.py"]
    src_zephyr_autonomy_core_context_context_health_score_py["(生产态 / production) ContextHealthScore.py — 统一健康分 (B6, DD80, ...<br/>文件: context_health_score.py"]
    src_zephyr_autonomy_core_context_context_model_strategy_py["(生产态 / production) context_model_strategy.py — 模型选择策略 (DD11...<br/>文件: context_model_strategy.py"]
    src_zephyr_autonomy_core_context_context_outcome_tracker_py["(生产态 / production) context_outcome_tracker.py — 因果链追踪 (B14, ...<br/>文件: context_outcome_tracker.py"]
    src_zephyr_autonomy_core_context_context_pipeline_auto_py["(生产态 / production) context_pipeline_auto.py — ContextPipeline 三...<br/>文件: context_pipeline_auto.py"]
    src_zephyr_autonomy_core_context_context_playground_py["(生产态 / production) context_playground.py — 上下文沙箱 dry-run (B5...<br/>文件: context_playground.py"]
    src_zephyr_autonomy_core_context_context_rot_model_py["(生产态 / production) context_rot_model.py — Context Rot 注意力衰减...<br/>文件: context_rot_model.py"]
    src_zephyr_autonomy_core_context_context_value_attribution_py["(生产态 / production) context_value_attribution.py — KE 级 ROI 归因 ...<br/>文件: context_value_attribution.py"]
    src_zephyr_autonomy_core_context_contextual_fetch_api_py["(生产态 / production) contextual_fetch_api.py — HTTP FE 对外 API (DD...<br/>文件: contextual_fetch_api.py"]
    src_zephyr_autonomy_core_context_curation_loop_py["(生产态 / production) curation_loop.py — Per-Turn Curation 策展 (DD1...<br/>文件: curation_loop.py"]
    src_zephyr_autonomy_core_context_diff_injector_py["(生产态 / production) diff_injector.py — 增量注入 (DD98, TASK-019)<br/>文件: diff_injector.py"]
    src_zephyr_autonomy_core_context_diversity_constraint_py["(生产态 / production) diversity_constraint.py — 多样性约束 (DD119, T...<br/>文件: diversity_constraint.py"]
    src_zephyr_autonomy_core_context_domain_decay_config_py["(生产态 / production) domain_decay_config.py — 每领域半衰期 (DD105, ...<br/>文件: domain_decay_config.py"]
    src_zephyr_autonomy_core_context_fallback_staleness_gate_py["(生产态 / production) fallback_staleness_gate.py — 兜底层自腐检测 (B...<br/>文件: fallback_staleness_gate.py"]
    src_zephyr_autonomy_core_context_integrity_check_py["(生产态 / production) integrity_check.py — 注入后完整性 (DD106, TASK...<br/>文件: integrity_check.py"]
    src_zephyr_autonomy_core_context_memory_bank_py["(生产态 / production) memory_bank.py — AI 读写结构化持久上下文 (DD: ...<br/>文件: memory_bank.py"]
    src_zephyr_autonomy_core_context_mode_manager_py["(生产态 / production) mode_manager.py — 模式管理器 (DD102, TASK-019)<br/>文件: mode_manager.py"]
    src_zephyr_autonomy_core_context_position_optimizer_py["(生产态 / production) position_optimizer.py — 位置优化 (DD104, TASK-019)<br/>文件: position_optimizer.py"]
    src_zephyr_autonomy_core_context_shadow_canary_py["(生产态 / production) shadow_canary.py — 金丝雀部署 (B4, DD78, TASK-...<br/>文件: shadow_canary.py"]
    src_zephyr_autonomy_core_context_staleness_manager_py["(生产态 / production) staleness_manager.py — 全局过期检测 (DD112, TA...<br/>文件: staleness_manager.py"]
    src_zephyr_autonomy_core_context_vector_bridge_py["(生产态 / production) VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE...<br/>文件: vector_bridge.py"]
    src_zephyr_autonomy_core_file_autoregister_py["(生产态 / production) file_autoregister.py"]
    src_zephyr_autonomy_core_ide_watcher_py["(生产态 / production) MOD-INF-019: Agent Spec — IDE Watcher<br/>文件: ide_watcher.py"]
    src_zephyr_autonomy_core_integration_pipeline_bridge_py["(生产态 / production) PipelineSkillBridge — Agent Spec -> Pipeline ...<br/>文件: pipeline_bridge.py"]
    src_zephyr_autonomy_core_phase_planner_py["(生产态 / production) MOD-INF-019: Agent Spec — Phase Planner<br/>文件: phase_planner.py"]
    src_zephyr_autonomy_core_progressive_disclosure_injector_py["(生产态 / production) progressive_disclosure_injector.py — 渐进式披...<br/>文件: progressive_disclosure_injector.py"]
    src_zephyr_autonomy_core_prompt_registry_py["(生产态 / production) PromptRegistry: YAML-driven Prompt 模板注册表<br/>文件: prompt_registry.py"]
    src_zephyr_autonomy_core_self_evolution_fidelity_gate_py["(生产态 / production) MOD-INF-019: Agent Spec — Self Evolution Fidel...<br/>文件: self_evolution_fidelity_gate.py"]
    src_zephyr_autonomy_core_skill_rbac_registry_py["(生产态 / production) G-CT-003: Agent Spec -> RBAC capability check.<br/>文件: skill_rbac_registry.py"]
    src_zephyr_autonomy_core_skills_skill_attention_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Attention Mana...<br/>文件: skill_attention.py"]
    src_zephyr_autonomy_core_skills_skill_breakage_checker_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Breakage Checker<br/>文件: skill_breakage_checker.py"]
    src_zephyr_autonomy_core_skills_skill_cache_provider_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Cache Provider<br/>文件: skill_cache_provider.py"]
    src_zephyr_autonomy_core_skills_skill_calibration_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Calibration<br/>文件: skill_calibration.py"]
    src_zephyr_autonomy_core_skills_skill_canary_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Canary<br/>文件: skill_canary.py"]
    src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Cognitive Pres...<br/>文件: skill_cognitive_preservation.py"]
    src_zephyr_autonomy_core_skills_skill_compliance_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Compliance<br/>文件: skill_compliance.py"]
    src_zephyr_autonomy_core_skills_skill_consensus_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Consensus<br/>文件: skill_consensus.py"]
    src_zephyr_autonomy_core_skills_skill_constructor_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Constructor<br/>文件: skill_constructor.py"]
    src_zephyr_autonomy_core_skills_skill_context_isolation_py["(生产态 / production) MOD-INF-019: Agent Spec — Context Isolation<br/>文件: skill_context_isolation.py"]
    src_zephyr_autonomy_core_skills_skill_contract_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Contract<br/>文件: skill_contract.py"]
    src_zephyr_autonomy_core_skills_skill_cross_model_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Cross-Model<br/>文件: skill_cross_model.py"]
    src_zephyr_autonomy_core_skills_skill_di_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Dependency Inj...<br/>文件: skill_di.py"]
    src_zephyr_autonomy_core_skills_skill_discovery_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Discovery<br/>文件: skill_discovery.py"]
    src_zephyr_autonomy_core_skills_skill_durable_py["(生产态 / production) MOD-INF-019: Agent Spec — Durable Execution<br/>文件: skill_durable.py"]
    src_zephyr_autonomy_core_skills_skill_economics_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Economics<br/>文件: skill_economics.py"]
    src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Efficacy Calib...<br/>文件: skill_efficacy_calibrator.py"]
    src_zephyr_autonomy_core_skills_skill_executor_py["(生产态 / production) skill_executor.py"]
    src_zephyr_autonomy_core_skills_skill_explain_py["(生产态 / production) MOD-INF-019: Agent Spec — XAI Explainable Skil...<br/>文件: skill_explain.py"]
    src_zephyr_autonomy_core_skills_skill_feature_flags_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Feature Flags<br/>文件: skill_feature_flags.py"]
    src_zephyr_autonomy_core_skills_skill_feedback_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Feedback Loop<br/>文件: skill_feedback.py"]
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Freshness Exte...<br/>文件: skill_freshness_ext.py"]
    src_zephyr_autonomy_core_skills_skill_gitops_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill GitOps<br/>文件: skill_gitops.py"]
    src_zephyr_autonomy_core_skills_skill_guardrails_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Guardrails<br/>文件: skill_guardrails.py"]
    src_zephyr_autonomy_core_skills_skill_idempotency_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Idempotency<br/>文件: skill_idempotency.py"]
    src_zephyr_autonomy_core_skills_skill_kya_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill KYA<br/>文件: skill_kya.py"]
    src_zephyr_autonomy_core_skills_skill_learning_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Self-Learning ...<br/>文件: skill_learning.py"]
    src_zephyr_autonomy_core_skills_skill_lineage_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Lineage<br/>文件: skill_lineage.py"]
    src_zephyr_autonomy_core_skills_skill_locking_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Locking (Produ...<br/>文件: skill_locking.py"]
    src_zephyr_autonomy_core_skills_skill_observability_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Observability<br/>文件: skill_observability.py"]
    src_zephyr_autonomy_core_skills_skill_ontology_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Ontology<br/>文件: skill_ontology.py"]
    src_zephyr_autonomy_core_skills_skill_postmortem_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Postmortem (追...<br/>文件: skill_postmortem.py"]
    src_zephyr_autonomy_core_skills_skill_prompt_cache_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Prompt Cache<br/>文件: skill_prompt_cache.py"]
    src_zephyr_autonomy_core_skills_skill_prompt_opt_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Prompt Optimizer<br/>文件: skill_prompt_opt.py"]
    src_zephyr_autonomy_core_skills_skill_resilience_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Resilience<br/>文件: skill_resilience.py"]
    src_zephyr_autonomy_core_skills_skill_risk_mitigator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Risk Mitigator<br/>文件: skill_risk_mitigator.py"]
    src_zephyr_autonomy_core_skills_skill_router_py["(生产态 / production) skill_router.py"]
    src_zephyr_autonomy_core_skills_skill_sandbox_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Sandbox<br/>文件: skill_sandbox.py"]
    src_zephyr_autonomy_core_skills_skill_schema_registry_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Schema Registry<br/>文件: skill_schema_registry.py"]
    src_zephyr_autonomy_core_skills_skill_security_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Security<br/>文件: skill_security.py"]
    src_zephyr_autonomy_core_skills_skill_shadow_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Shadow Deployment<br/>文件: skill_shadow.py"]
    src_zephyr_autonomy_core_skills_skill_silent_failure_py["(生产态 / production) MOD-INF-019: Agent Spec — Silent Failure Detector<br/>文件: skill_silent_failure.py"]
    src_zephyr_autonomy_core_skills_skill_team_optimizer_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Team Optimizer<br/>文件: skill_team_optimizer.py"]
    src_zephyr_autonomy_core_skills_skill_telemetry_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Telemetry<br/>文件: skill_telemetry.py"]
    src_zephyr_autonomy_core_skills_skill_temperature_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Temperature<br/>文件: skill_temperature.py"]
    src_zephyr_autonomy_core_skills_skill_tokenomics_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Tokenomics<br/>文件: skill_tokenomics.py"]
    src_zephyr_autonomy_core_skills_skill_translator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Translator<br/>文件: skill_translator.py"]
    src_zephyr_autonomy_core_skills_skill_workflow_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Workflow Orche...<br/>文件: skill_workflow.py"]
    src_zephyr_autonomy_core_spec_engine_py["(生产态 / production) MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski...<br/>文件: spec_engine.py"]
    src_zephyr_autonomy_core_vibe_coding_quality_gate_py["(生产态 / production) VibeCodingQualityGate — 代码质量门禁（stub, te...<br/>文件: vibe_coding_quality_gate.py"]
    src_zephyr_governance_persistence_intent_parser_py["(生产态 / production) IntentParser · 意图三阶段级联解析器（V-09）<br/>文件: intent_parser.py"]
    src_zephyr_infrastructure_system_snapshot_py["(生产态 / production) SystemSnapshotter — M1 系统状态镜像（CL-017 RI...<br/>文件: system_snapshot.py"]
    src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py["(生产态 / production) otel_instrumentation.py — 全链路 OTel (B12, DD...<br/>文件: otel_instrumentation.py"]
    src_zephyr_integration_vector_memory_vector_writer_py["(生产态 / production) CE 向量写入器 — vectorize_and_store() 生产者<br/>文件: vector_writer.py"]
    src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py["(生产态 / production) adversarial_robustness.py — 对抗鲁棒性 (B8, DD...<br/>文件: adversarial_robustness.py"]
    src_zephyr_security_llm_defense_llm_security_alignment_scorer_py["(生产态 / production) alignment_scorer.py — 对齐评分 (B11, DD85, TAS...<br/>文件: alignment_scorer.py"]
    src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py["(生产态 / production) lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20...<br/>文件: lsg_pattern_tracker.py"]
    src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py["(生产态 / production) poisoning_monitor.py — Embed 污染检测 (DD97, T...<br/>文件: poisoning_monitor.py"]
    src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py["(生产态 / production) sensitivity_classifier.py — 数据分级 (B9, DD83...<br/>文件: sensitivity_classifier.py"]
    src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py["(生产态 / production) solo_dev_safety_net.py — 单人无审查安全网 (B15...<br/>文件: solo_dev_safety_net.py"]
    src_zephyr_shared_ai_guards_config_safety_guard_py["(生产态 / production) config_safety_guard.py — 配置自毁防护 (B16, DD...<br/>文件: config_safety_guard.py"]
    src_zephyr_shared_dependency_dependency_tracker_py["(生产态 / production) dependency_tracker.py — 依赖追踪 (DD116, TASK-020)<br/>文件: dependency_tracker.py"]
    src_zephyr_shared_io_cache_invalidation_py["(生产态 / production) cache_invalidation.py — 缓存一致性 (DD113, TAS...<br/>文件: cache_invalidation.py"]
    src_zephyr_shared_utils_verify_paths_py["(生产态 / production) verify_paths.py — 代码路径索引验证 (TASK-012)<br/>文件: verify_paths.py"]
    tests_automation_test_auto_runtime_e2e_py["(生产态 / production) F1 AutoRuntimeCore 非mock端到端集成测试<br/>文件: test_auto_runtime_e2e.py"]
    tests_f_lifecycle_test_f1_event_trigger_py["(生产态 / production) F1 事件触发启动测试<br/>文件: test_f1_event_trigger.py"]
    tests_trading_extreme_test_f14_pipeline_extreme_py["(生产态 / production) F14 管线编排/反馈环 — 红蓝对抗端到端极端测试<br/>文件: test_f14_pipeline_extreme.py"]
    tests_trading_extreme_test_f1_extreme_py["(生产态 / production) F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测试<br/>文件: test_f1_extreme.py"]
    src_zephyr_autonomy_core_main_py ~~~ src_zephyr_autonomy_core_agent_observability_py
    src_zephyr_autonomy_core_agent_observability_py ~~~ src_zephyr_autonomy_core_all_skill_modules_py
    src_zephyr_autonomy_core_all_skill_modules_py ~~~ src_zephyr_autonomy_core_context_atomic_injector_py
    src_zephyr_autonomy_core_context_atomic_injector_py ~~~ src_zephyr_autonomy_core_context_ce_bootstrap_py
    src_zephyr_autonomy_core_context_ce_bootstrap_py ~~~ src_zephyr_autonomy_core_context_ce_explain_cli_py
    src_zephyr_autonomy_core_context_ce_explain_cli_py ~~~ src_zephyr_autonomy_core_context_ce_file_lister_py
    src_zephyr_autonomy_core_context_ce_file_lister_py ~~~ src_zephyr_autonomy_core_context_ce_playground_v2_py
    src_zephyr_autonomy_core_context_ce_playground_v2_py ~~~ src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py
    src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py ~~~ src_zephyr_autonomy_core_context_checkpoint_manager_py
    src_zephyr_autonomy_core_context_checkpoint_manager_py ~~~ src_zephyr_autonomy_core_context_cold_start_booster_py
    src_zephyr_autonomy_core_context_cold_start_booster_py ~~~ src_zephyr_autonomy_core_context_complexity_budget_py
    src_zephyr_autonomy_core_context_complexity_budget_py ~~~ src_zephyr_autonomy_core_context_context_budget_py
    src_zephyr_autonomy_core_context_context_budget_py ~~~ src_zephyr_autonomy_core_context_context_budget_tracker_py
    src_zephyr_autonomy_core_context_context_budget_tracker_py ~~~ src_zephyr_autonomy_core_context_context_debt_score_py
    src_zephyr_autonomy_core_context_context_debt_score_py ~~~ src_zephyr_autonomy_core_context_context_evaluator_py
    src_zephyr_autonomy_core_context_context_evaluator_py ~~~ src_zephyr_autonomy_core_context_context_evictor_py
    src_zephyr_autonomy_core_context_context_evictor_py ~~~ src_zephyr_autonomy_core_context_context_health_score_py
    src_zephyr_autonomy_core_context_context_health_score_py ~~~ src_zephyr_autonomy_core_context_context_model_strategy_py
    src_zephyr_autonomy_core_context_context_model_strategy_py ~~~ src_zephyr_autonomy_core_context_context_outcome_tracker_py
    src_zephyr_autonomy_core_context_context_outcome_tracker_py ~~~ src_zephyr_autonomy_core_context_context_pipeline_auto_py
    src_zephyr_autonomy_core_context_context_pipeline_auto_py ~~~ src_zephyr_autonomy_core_context_context_playground_py
    src_zephyr_autonomy_core_context_context_playground_py ~~~ src_zephyr_autonomy_core_context_context_rot_model_py
    src_zephyr_autonomy_core_context_context_rot_model_py ~~~ src_zephyr_autonomy_core_context_context_value_attribution_py
    src_zephyr_autonomy_core_context_context_value_attribution_py ~~~ src_zephyr_autonomy_core_context_contextual_fetch_api_py
    src_zephyr_autonomy_core_context_contextual_fetch_api_py ~~~ src_zephyr_autonomy_core_context_curation_loop_py
    src_zephyr_autonomy_core_context_curation_loop_py ~~~ src_zephyr_autonomy_core_context_diff_injector_py
    src_zephyr_autonomy_core_context_diff_injector_py ~~~ src_zephyr_autonomy_core_context_diversity_constraint_py
    src_zephyr_autonomy_core_context_diversity_constraint_py ~~~ src_zephyr_autonomy_core_context_domain_decay_config_py
    src_zephyr_autonomy_core_context_domain_decay_config_py ~~~ src_zephyr_autonomy_core_context_fallback_staleness_gate_py
    src_zephyr_autonomy_core_context_fallback_staleness_gate_py ~~~ src_zephyr_autonomy_core_context_integrity_check_py
    src_zephyr_autonomy_core_context_integrity_check_py ~~~ src_zephyr_autonomy_core_context_memory_bank_py
    src_zephyr_autonomy_core_context_memory_bank_py ~~~ src_zephyr_autonomy_core_context_mode_manager_py
    src_zephyr_autonomy_core_context_mode_manager_py ~~~ src_zephyr_autonomy_core_context_position_optimizer_py
    src_zephyr_autonomy_core_context_position_optimizer_py ~~~ src_zephyr_autonomy_core_context_shadow_canary_py
    src_zephyr_autonomy_core_context_shadow_canary_py ~~~ src_zephyr_autonomy_core_context_staleness_manager_py
    src_zephyr_autonomy_core_context_staleness_manager_py ~~~ src_zephyr_autonomy_core_context_vector_bridge_py
    src_zephyr_autonomy_core_context_vector_bridge_py ~~~ src_zephyr_autonomy_core_file_autoregister_py
    src_zephyr_autonomy_core_file_autoregister_py ~~~ src_zephyr_autonomy_core_ide_watcher_py
    src_zephyr_autonomy_core_ide_watcher_py ~~~ src_zephyr_autonomy_core_integration_pipeline_bridge_py
    src_zephyr_autonomy_core_integration_pipeline_bridge_py ~~~ src_zephyr_autonomy_core_phase_planner_py
    src_zephyr_autonomy_core_phase_planner_py ~~~ src_zephyr_autonomy_core_progressive_disclosure_injector_py
    src_zephyr_autonomy_core_progressive_disclosure_injector_py ~~~ src_zephyr_autonomy_core_prompt_registry_py
    src_zephyr_autonomy_core_prompt_registry_py ~~~ src_zephyr_autonomy_core_self_evolution_fidelity_gate_py
    src_zephyr_autonomy_core_self_evolution_fidelity_gate_py ~~~ src_zephyr_autonomy_core_skill_rbac_registry_py
    src_zephyr_autonomy_core_skill_rbac_registry_py ~~~ src_zephyr_autonomy_core_skills_skill_attention_py
    src_zephyr_autonomy_core_skills_skill_attention_py ~~~ src_zephyr_autonomy_core_skills_skill_breakage_checker_py
    src_zephyr_autonomy_core_skills_skill_breakage_checker_py ~~~ src_zephyr_autonomy_core_skills_skill_cache_provider_py
    src_zephyr_autonomy_core_skills_skill_cache_provider_py ~~~ src_zephyr_autonomy_core_skills_skill_calibration_py
    src_zephyr_autonomy_core_skills_skill_calibration_py ~~~ src_zephyr_autonomy_core_skills_skill_canary_py
    src_zephyr_autonomy_core_skills_skill_canary_py ~~~ src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py
    src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py ~~~ src_zephyr_autonomy_core_skills_skill_compliance_py
    src_zephyr_autonomy_core_skills_skill_compliance_py ~~~ src_zephyr_autonomy_core_skills_skill_consensus_py
    src_zephyr_autonomy_core_skills_skill_consensus_py ~~~ src_zephyr_autonomy_core_skills_skill_constructor_py
    src_zephyr_autonomy_core_skills_skill_constructor_py ~~~ src_zephyr_autonomy_core_skills_skill_context_isolation_py
    src_zephyr_autonomy_core_skills_skill_context_isolation_py ~~~ src_zephyr_autonomy_core_skills_skill_contract_py
    src_zephyr_autonomy_core_skills_skill_contract_py ~~~ src_zephyr_autonomy_core_skills_skill_cross_model_py
    src_zephyr_autonomy_core_skills_skill_cross_model_py ~~~ src_zephyr_autonomy_core_skills_skill_di_py
    src_zephyr_autonomy_core_skills_skill_di_py ~~~ src_zephyr_autonomy_core_skills_skill_discovery_py
    src_zephyr_autonomy_core_skills_skill_discovery_py ~~~ src_zephyr_autonomy_core_skills_skill_durable_py
    src_zephyr_autonomy_core_skills_skill_durable_py ~~~ src_zephyr_autonomy_core_skills_skill_economics_py
    src_zephyr_autonomy_core_skills_skill_economics_py ~~~ src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py
    src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py ~~~ src_zephyr_autonomy_core_skills_skill_executor_py
    src_zephyr_autonomy_core_skills_skill_executor_py ~~~ src_zephyr_autonomy_core_skills_skill_explain_py
    src_zephyr_autonomy_core_skills_skill_explain_py ~~~ src_zephyr_autonomy_core_skills_skill_feature_flags_py
    src_zephyr_autonomy_core_skills_skill_feature_flags_py ~~~ src_zephyr_autonomy_core_skills_skill_feedback_py
    src_zephyr_autonomy_core_skills_skill_feedback_py ~~~ src_zephyr_autonomy_core_skills_skill_freshness_ext_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py ~~~ src_zephyr_autonomy_core_skills_skill_gitops_py
    src_zephyr_autonomy_core_skills_skill_gitops_py ~~~ src_zephyr_autonomy_core_skills_skill_guardrails_py
    src_zephyr_autonomy_core_skills_skill_guardrails_py ~~~ src_zephyr_autonomy_core_skills_skill_idempotency_py
    src_zephyr_autonomy_core_skills_skill_idempotency_py ~~~ src_zephyr_autonomy_core_skills_skill_kya_py
    src_zephyr_autonomy_core_skills_skill_kya_py ~~~ src_zephyr_autonomy_core_skills_skill_learning_py
    src_zephyr_autonomy_core_skills_skill_learning_py ~~~ src_zephyr_autonomy_core_skills_skill_lineage_py
    src_zephyr_autonomy_core_skills_skill_lineage_py ~~~ src_zephyr_autonomy_core_skills_skill_locking_py
    src_zephyr_autonomy_core_skills_skill_locking_py ~~~ src_zephyr_autonomy_core_skills_skill_observability_py
    src_zephyr_autonomy_core_skills_skill_observability_py ~~~ src_zephyr_autonomy_core_skills_skill_ontology_py
    src_zephyr_autonomy_core_skills_skill_ontology_py ~~~ src_zephyr_autonomy_core_skills_skill_postmortem_py
    src_zephyr_autonomy_core_skills_skill_postmortem_py ~~~ src_zephyr_autonomy_core_skills_skill_prompt_cache_py
    src_zephyr_autonomy_core_skills_skill_prompt_cache_py ~~~ src_zephyr_autonomy_core_skills_skill_prompt_opt_py
    src_zephyr_autonomy_core_skills_skill_prompt_opt_py ~~~ src_zephyr_autonomy_core_skills_skill_resilience_py
    src_zephyr_autonomy_core_skills_skill_resilience_py ~~~ src_zephyr_autonomy_core_skills_skill_risk_mitigator_py
    src_zephyr_autonomy_core_skills_skill_risk_mitigator_py ~~~ src_zephyr_autonomy_core_skills_skill_router_py
    src_zephyr_autonomy_core_skills_skill_router_py ~~~ src_zephyr_autonomy_core_skills_skill_sandbox_py
    src_zephyr_autonomy_core_skills_skill_sandbox_py ~~~ src_zephyr_autonomy_core_skills_skill_schema_registry_py
    src_zephyr_autonomy_core_skills_skill_schema_registry_py ~~~ src_zephyr_autonomy_core_skills_skill_security_py
    src_zephyr_autonomy_core_skills_skill_security_py ~~~ src_zephyr_autonomy_core_skills_skill_shadow_py
    src_zephyr_autonomy_core_skills_skill_shadow_py ~~~ src_zephyr_autonomy_core_skills_skill_silent_failure_py
    src_zephyr_autonomy_core_skills_skill_silent_failure_py ~~~ src_zephyr_autonomy_core_skills_skill_team_optimizer_py
    src_zephyr_autonomy_core_skills_skill_team_optimizer_py ~~~ src_zephyr_autonomy_core_skills_skill_telemetry_py
    src_zephyr_autonomy_core_skills_skill_telemetry_py ~~~ src_zephyr_autonomy_core_skills_skill_temperature_py
    src_zephyr_autonomy_core_skills_skill_temperature_py ~~~ src_zephyr_autonomy_core_skills_skill_tokenomics_py
    src_zephyr_autonomy_core_skills_skill_tokenomics_py ~~~ src_zephyr_autonomy_core_skills_skill_translator_py
    src_zephyr_autonomy_core_skills_skill_translator_py ~~~ src_zephyr_autonomy_core_skills_skill_workflow_py
    src_zephyr_autonomy_core_skills_skill_workflow_py ~~~ src_zephyr_autonomy_core_spec_engine_py
    src_zephyr_autonomy_core_spec_engine_py ~~~ src_zephyr_autonomy_core_vibe_coding_quality_gate_py
    src_zephyr_autonomy_core_vibe_coding_quality_gate_py ~~~ src_zephyr_governance_persistence_intent_parser_py
    src_zephyr_governance_persistence_intent_parser_py ~~~ src_zephyr_infrastructure_system_snapshot_py
    src_zephyr_infrastructure_system_snapshot_py ~~~ src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py
    src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py ~~~ src_zephyr_integration_vector_memory_vector_writer_py
    src_zephyr_integration_vector_memory_vector_writer_py ~~~ src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py
    src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py ~~~ src_zephyr_security_llm_defense_llm_security_alignment_scorer_py
    src_zephyr_security_llm_defense_llm_security_alignment_scorer_py ~~~ src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py
    src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py ~~~ src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py
    src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py ~~~ src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py
    src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py ~~~ src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py
    src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py ~~~ src_zephyr_shared_ai_guards_config_safety_guard_py
    src_zephyr_shared_ai_guards_config_safety_guard_py ~~~ src_zephyr_shared_dependency_dependency_tracker_py
    src_zephyr_shared_dependency_dependency_tracker_py ~~~ src_zephyr_shared_io_cache_invalidation_py
    src_zephyr_shared_io_cache_invalidation_py ~~~ src_zephyr_shared_utils_verify_paths_py
    src_zephyr_shared_utils_verify_paths_py ~~~ tests_automation_test_auto_runtime_e2e_py
    tests_automation_test_auto_runtime_e2e_py ~~~ tests_f_lifecycle_test_f1_event_trigger_py
    tests_f_lifecycle_test_f1_event_trigger_py ~~~ tests_trading_extreme_test_f14_pipeline_extreme_py
    tests_trading_extreme_test_f14_pipeline_extreme_py ~~~ tests_trading_extreme_test_f1_extreme_py
    src_zephyr_autonomy_core_context_context_pipeline_py["(生产态 / production) context_pipeline — Context Engine **四段流水线...<br/>文件: context_pipeline.py"]
    src_zephyr_autonomy_core_skills_skill_evaluator_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Evaluator<br/>文件: skill_evaluator.py"]
    src_zephyr_autonomy_core_skills_skill_factory_py["(生产态 / production) skill_factory.py"]
    src_zephyr_autonomy_core_skills_skill_kill_switch_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Kill Switch<br/>文件: skill_kill_switch.py"]
    src_zephyr_autonomy_core_skills_skill_lifecycle_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Lifecycle<br/>文件: skill_lifecycle.py"]
    src_zephyr_autonomy_core_skills_skill_model_evolution_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Model Evolution<br/>文件: skill_model_evolution.py"]
    src_zephyr_autonomy_core_skills_skill_registry_py["(生产态 / production) skill-registry.py —— Skill 注册基座（Phase 14...<br/>文件: skill_registry.py"]
    src_zephyr_autonomy_core_trigger_router_py["(生产态 / production) trigger_router.py"]
    src_zephyr_governance_persistence_intent_keyword_mapper_py["(生产态 / production) IntentKeywordMapper - Stage 1 of three-stage in...<br/>文件: intent_keyword_mapper.py"]
    src_zephyr_autonomy_core_context_context_pipeline_py ~~~ src_zephyr_autonomy_core_skills_skill_evaluator_py
    src_zephyr_autonomy_core_skills_skill_evaluator_py ~~~ src_zephyr_autonomy_core_skills_skill_factory_py
    src_zephyr_autonomy_core_skills_skill_factory_py ~~~ src_zephyr_autonomy_core_skills_skill_kill_switch_py
    src_zephyr_autonomy_core_skills_skill_kill_switch_py ~~~ src_zephyr_autonomy_core_skills_skill_lifecycle_py
    src_zephyr_autonomy_core_skills_skill_lifecycle_py ~~~ src_zephyr_autonomy_core_skills_skill_model_evolution_py
    src_zephyr_autonomy_core_skills_skill_model_evolution_py ~~~ src_zephyr_autonomy_core_skills_skill_registry_py
    src_zephyr_autonomy_core_skills_skill_registry_py ~~~ src_zephyr_autonomy_core_trigger_router_py
    src_zephyr_autonomy_core_trigger_router_py ~~~ src_zephyr_governance_persistence_intent_keyword_mapper_py
    src_zephyr_autonomy_core_context_context_assembler_py["(生产态 / production) ContextAssembler — 上下文装配、校验、影子留档<br/>文件: context_assembler.py"]
    src_zephyr_autonomy_core_context_context_injector_py["(生产态 / production) ContextInjector: retrieve and inject relevant k...<br/>文件: context_injector.py"]
    src_zephyr_autonomy_core_skills_skill_freshness_py["(生产态 / production) MOD-INF-019: Agent Spec — Skill Freshness Decay<br/>文件: skill_freshness.py"]
    src_zephyr_autonomy_core_skills_skill_loader_py["(生产态 / production) skill_loader.py"]
    src_zephyr_autonomy_core_skills_skill_model_py["(生产态 / production) skill_model.py"]
    src_zephyr_shared_blueprint_tools_architecture_context_loader_py["(生产态 / production) architecture_context_loader — 加载 ``generate_...<br/>文件: architecture_context_loader.py"]
    src_zephyr_autonomy_core_context_context_assembler_py ~~~ src_zephyr_autonomy_core_context_context_injector_py
    src_zephyr_autonomy_core_context_context_injector_py ~~~ src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_freshness_py ~~~ src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_loader_py ~~~ src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_model_py ~~~ src_zephyr_shared_blueprint_tools_architecture_context_loader_py
    src_zephyr_autonomy_core_context_context_rule_registry_py["(生产态 / production) context_rule_registry.py"]
    src_zephyr_shared_io_doc_compressor_py["(生产态 / production) DocCompressor — 文档压缩服务（CL-018 RI 扩展模式）<br/>文件: doc_compressor.py"]
    src_zephyr_autonomy_core_context_context_rule_registry_py ~~~ src_zephyr_shared_io_doc_compressor_py
    src_zephyr_autonomy_core_prompt_registry_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_injector_py
    src_zephyr_autonomy_core_prompt_registry_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_registry_py
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_trigger_router_py
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_factory_py
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_main_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_main_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_context_context_budget_tracker_py -->|导入依赖 / import_depends| src_zephyr_shared_io_doc_compressor_py
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_rule_registry_py
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| src_zephyr_shared_io_doc_compressor_py
    src_zephyr_autonomy_core_context_context_pipeline_auto_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_pipeline_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_assembler_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_injector_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_rule_registry_py
    src_zephyr_autonomy_core_context_context_pipeline_py -->|导入依赖 / import_depends| src_zephyr_shared_blueprint_tools_architecture_context_loader_py
    src_zephyr_autonomy_core_integration_pipeline_bridge_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_trigger_router_py
    src_zephyr_autonomy_core_integration_pipeline_bridge_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_consensus_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_contract_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_constructor_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_discovery_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_factory_py
    src_zephyr_autonomy_core_skills_skill_discovery_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_explain_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_evaluator_py
    src_zephyr_autonomy_core_skills_skill_explain_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_evolution_py
    src_zephyr_autonomy_core_skills_skill_evaluator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_evaluator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_executor_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_feedback_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_feedback_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_kill_switch_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_lifecycle_py
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_kill_switch_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_lifecycle_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_model_py
    src_zephyr_autonomy_core_skills_skill_kya_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_prompt_opt_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_postmortem_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_shadow_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_py
    src_zephyr_autonomy_core_skills_skill_workflow_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_autonomy_core_skills_skill_translator_py -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_loader_py
    src_zephyr_governance_persistence_intent_parser_py -->|导入依赖 / import_depends| src_zephyr_governance_persistence_intent_keyword_mapper_py
    D_SHARED["(生产态 / production) D_SHARED"]
    src_zephyr_autonomy_core_skills_skill_freshness_ext_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_infrastructure_system_snapshot_py -->|导入依赖 / import_depends| D_SHARED
    src_zephyr_autonomy_core_context_context_assembler_py -->|导入依赖 / import_depends| D_SHARED
    D_GOV_AUDIT["(生产态 / production) D_GOV_AUDIT"]
    src_zephyr_autonomy_core_skills_skill_executor_py -->|导入依赖 / import_depends| D_GOV_AUDIT
    D_INFRA_RUNTIME["(生产态 / production) D_INFRA_RUNTIME"]
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    src_zephyr_autonomy_core_prompt_registry_py -->|导入依赖 / import_depends| D_INFRA_RUNTIME
    D_INTEGRATION["(生产态 / production) D_INTEGRATION"]
    src_zephyr_autonomy_core_spec_engine_py -->|导入依赖 / import_depends| D_INTEGRATION
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f1_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_automation_test_auto_runtime_e2e_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    tests_trading_extreme_test_f14_pipeline_extreme_py -->|测试依赖 / test_depends| D_INFRA_RUNTIME
    src_zephyr_governance_persistence_intent_keyword_mapper_py -->|导入依赖 / import_depends| D_SHARED
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_freshness_ext_py
    D_ORCHESTRATOR["(生产态 / production) D_ORCHESTRATOR"]
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_vector_bridge_py
    D_FEEDBACK_LOOP["(生产态 / production) D_FEEDBACK_LOOP"]
    D_FEEDBACK_LOOP -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_vector_bridge_py
    D_ORCHESTRATOR -->|导入依赖 / import_depends| src_zephyr_integration_vector_memory_vector_writer_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_feedback_py
    D_INFRA_RUNTIME -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_lifecycle_py
    D_GOV_CODE_QUALITY["(生产态 / production) D_GOV_CODE_QUALITY"]
    D_GOV_CODE_QUALITY -->|导入依赖 / import_depends| src_zephyr_autonomy_core_context_context_rule_registry_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_governance_persistence_intent_keyword_mapper_py
    D_INTEGRATION -->|导入依赖 / import_depends| src_zephyr_autonomy_core_integration_pipeline_bridge_py
    D_SECURITY["(生产态 / production) D_SECURITY"]
    D_SECURITY -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skill_rbac_registry_py
    D_GOV_REPAIR["(生产态 / production) D_GOV_REPAIR"]
    D_GOV_REPAIR -->|导入依赖 / import_depends| src_zephyr_autonomy_core_skills_skill_executor_py
    classDef production fill:#e8edf2,stroke:#0277bd,stroke-width:2px,color:#1a1a1a
    classDef design fill:#f0ebe3,stroke:#bf360c,stroke-width:2px,color:#1a1a1a,stroke-dasharray: 5 5
    classDef external_prod fill:#e8efe9,stroke:#1b5e20,stroke-width:1px,color:#1a1a1a
    classDef external_design fill:#efe5ea,stroke:#880e4f,stroke-width:1px,color:#1a1a1a,stroke-dasharray: 5 5
    class src_zephyr_autonomy_core_main_py,src_zephyr_autonomy_core_agent_observability_py,src_zephyr_autonomy_core_all_skill_modules_py,src_zephyr_autonomy_core_context_atomic_injector_py,src_zephyr_autonomy_core_context_ce_bootstrap_py,src_zephyr_autonomy_core_context_ce_explain_cli_py,src_zephyr_autonomy_core_context_ce_file_lister_py,src_zephyr_autonomy_core_context_ce_playground_v2_py,src_zephyr_autonomy_core_context_ce_vibe_shortcuts_py,src_zephyr_autonomy_core_context_checkpoint_manager_py,src_zephyr_autonomy_core_context_cold_start_booster_py,src_zephyr_autonomy_core_context_complexity_budget_py,src_zephyr_autonomy_core_context_context_assembler_py,src_zephyr_autonomy_core_context_context_budget_py,src_zephyr_autonomy_core_context_context_budget_tracker_py,src_zephyr_autonomy_core_context_context_debt_score_py,src_zephyr_autonomy_core_context_context_evaluator_py,src_zephyr_autonomy_core_context_context_evictor_py,src_zephyr_autonomy_core_context_context_health_score_py,src_zephyr_autonomy_core_context_context_injector_py,src_zephyr_autonomy_core_context_context_model_strategy_py,src_zephyr_autonomy_core_context_context_outcome_tracker_py,src_zephyr_autonomy_core_context_context_pipeline_py,src_zephyr_autonomy_core_context_context_pipeline_auto_py,src_zephyr_autonomy_core_context_context_playground_py,src_zephyr_autonomy_core_context_context_rot_model_py,src_zephyr_autonomy_core_context_context_rule_registry_py,src_zephyr_autonomy_core_context_context_value_attribution_py,src_zephyr_autonomy_core_context_contextual_fetch_api_py,src_zephyr_autonomy_core_context_curation_loop_py,src_zephyr_autonomy_core_context_diff_injector_py,src_zephyr_autonomy_core_context_diversity_constraint_py,src_zephyr_autonomy_core_context_domain_decay_config_py,src_zephyr_autonomy_core_context_fallback_staleness_gate_py,src_zephyr_autonomy_core_context_integrity_check_py,src_zephyr_autonomy_core_context_memory_bank_py,src_zephyr_autonomy_core_context_mode_manager_py,src_zephyr_autonomy_core_context_position_optimizer_py,src_zephyr_autonomy_core_context_shadow_canary_py,src_zephyr_autonomy_core_context_staleness_manager_py,src_zephyr_autonomy_core_context_vector_bridge_py,src_zephyr_autonomy_core_file_autoregister_py,src_zephyr_autonomy_core_ide_watcher_py,src_zephyr_autonomy_core_integration_pipeline_bridge_py,src_zephyr_autonomy_core_phase_planner_py,src_zephyr_autonomy_core_progressive_disclosure_injector_py,src_zephyr_autonomy_core_prompt_registry_py,src_zephyr_autonomy_core_self_evolution_fidelity_gate_py,src_zephyr_autonomy_core_skill_rbac_registry_py,src_zephyr_autonomy_core_skills_skill_attention_py,src_zephyr_autonomy_core_skills_skill_breakage_checker_py,src_zephyr_autonomy_core_skills_skill_cache_provider_py,src_zephyr_autonomy_core_skills_skill_calibration_py,src_zephyr_autonomy_core_skills_skill_canary_py,src_zephyr_autonomy_core_skills_skill_cognitive_preservation_py,src_zephyr_autonomy_core_skills_skill_compliance_py,src_zephyr_autonomy_core_skills_skill_consensus_py,src_zephyr_autonomy_core_skills_skill_constructor_py,src_zephyr_autonomy_core_skills_skill_context_isolation_py,src_zephyr_autonomy_core_skills_skill_contract_py,src_zephyr_autonomy_core_skills_skill_cross_model_py,src_zephyr_autonomy_core_skills_skill_di_py,src_zephyr_autonomy_core_skills_skill_discovery_py,src_zephyr_autonomy_core_skills_skill_durable_py,src_zephyr_autonomy_core_skills_skill_economics_py,src_zephyr_autonomy_core_skills_skill_efficacy_calibrator_py,src_zephyr_autonomy_core_skills_skill_evaluator_py,src_zephyr_autonomy_core_skills_skill_executor_py,src_zephyr_autonomy_core_skills_skill_explain_py,src_zephyr_autonomy_core_skills_skill_factory_py,src_zephyr_autonomy_core_skills_skill_feature_flags_py,src_zephyr_autonomy_core_skills_skill_feedback_py,src_zephyr_autonomy_core_skills_skill_freshness_py,src_zephyr_autonomy_core_skills_skill_freshness_ext_py,src_zephyr_autonomy_core_skills_skill_gitops_py,src_zephyr_autonomy_core_skills_skill_guardrails_py,src_zephyr_autonomy_core_skills_skill_idempotency_py,src_zephyr_autonomy_core_skills_skill_kill_switch_py,src_zephyr_autonomy_core_skills_skill_kya_py,src_zephyr_autonomy_core_skills_skill_learning_py,src_zephyr_autonomy_core_skills_skill_lifecycle_py,src_zephyr_autonomy_core_skills_skill_lineage_py,src_zephyr_autonomy_core_skills_skill_loader_py,src_zephyr_autonomy_core_skills_skill_locking_py,src_zephyr_autonomy_core_skills_skill_model_py,src_zephyr_autonomy_core_skills_skill_model_evolution_py,src_zephyr_autonomy_core_skills_skill_observability_py,src_zephyr_autonomy_core_skills_skill_ontology_py,src_zephyr_autonomy_core_skills_skill_postmortem_py,src_zephyr_autonomy_core_skills_skill_prompt_cache_py,src_zephyr_autonomy_core_skills_skill_prompt_opt_py,src_zephyr_autonomy_core_skills_skill_registry_py,src_zephyr_autonomy_core_skills_skill_resilience_py,src_zephyr_autonomy_core_skills_skill_risk_mitigator_py,src_zephyr_autonomy_core_skills_skill_router_py,src_zephyr_autonomy_core_skills_skill_sandbox_py,src_zephyr_autonomy_core_skills_skill_schema_registry_py,src_zephyr_autonomy_core_skills_skill_security_py,src_zephyr_autonomy_core_skills_skill_shadow_py,src_zephyr_autonomy_core_skills_skill_silent_failure_py,src_zephyr_autonomy_core_skills_skill_team_optimizer_py,src_zephyr_autonomy_core_skills_skill_telemetry_py,src_zephyr_autonomy_core_skills_skill_temperature_py,src_zephyr_autonomy_core_skills_skill_tokenomics_py,src_zephyr_autonomy_core_skills_skill_translator_py,src_zephyr_autonomy_core_skills_skill_workflow_py,src_zephyr_autonomy_core_spec_engine_py,src_zephyr_autonomy_core_trigger_router_py,src_zephyr_autonomy_core_vibe_coding_quality_gate_py,src_zephyr_governance_persistence_intent_keyword_mapper_py,src_zephyr_governance_persistence_intent_parser_py,src_zephyr_infrastructure_system_snapshot_py,src_zephyr_infrastructure_system_telemetry_otel_instrumentation_py,src_zephyr_integration_vector_memory_vector_writer_py,src_zephyr_security_llm_defense_llm_security_adversarial_robustness_py,src_zephyr_security_llm_defense_llm_security_alignment_scorer_py,src_zephyr_security_llm_defense_llm_security_lsg_pattern_tracker_py,src_zephyr_security_llm_defense_llm_security_poisoning_monitor_py,src_zephyr_security_llm_defense_llm_security_sensitivity_classifier_py,src_zephyr_security_llm_defense_llm_security_solo_dev_safety_net_py,src_zephyr_shared_ai_guards_config_safety_guard_py,src_zephyr_shared_blueprint_tools_architecture_context_loader_py,src_zephyr_shared_dependency_dependency_tracker_py,src_zephyr_shared_io_cache_invalidation_py,src_zephyr_shared_io_doc_compressor_py,src_zephyr_shared_utils_verify_paths_py,tests_automation_test_auto_runtime_e2e_py,tests_f_lifecycle_test_f1_event_trigger_py,tests_trading_extreme_test_f14_pipeline_extreme_py,tests_trading_extreme_test_f1_extreme_py production
    class D_SHARED,D_GOV_AUDIT,D_INFRA_RUNTIME,D_INTEGRATION,D_ORCHESTRATOR,D_FEEDBACK_LOOP,D_GOV_CODE_QUALITY,D_SECURITY,D_GOV_REPAIR external_prod
```

### 设计态子图（仅 design_maturity=design 的模块和依赖）

> 仅展示蓝图阶段、代码未写的设计态模块（共 0 个，0 条域内依赖）。

> （无设计态模块 / No design modules）

## 跨域依赖 / Cross-domain Dependencies

### 本域依赖的其他域（出边）/ Depends On

| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | D_FEEDBACK_LOOP 反馈循环引擎: Error Budget 状态机——monthly budget + burn_ra... | 测试依赖 / test_depends |
| 2 | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose... | 测试依赖 / test_depends |
| 3 | skill_executor.py | → | D_GOV_AUDIT 审计追踪: writer.py | 导入依赖 / import_depends |
| 4 | MOD-INF-019: Agent Spec — Skill Sandbox (skill... | → | D_GOV_AUDIT 审计追踪: bridge.py | 导入依赖 / import_depends |
| 5 | MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski... | → | D_GOV_AUDIT 审计追踪: writer.py | 导入依赖 / import_depends |
| 6 | skill_executor.py | → | D_GOV_RULE 规则治理: GateEngine — KMS G1-G6 + Orc G0/G7 + 交易 G10-... | 导入依赖 / import_depends |
| 7 | ContextAssembler — 上下文装配、校验、影子留档 ... | → | D_INFRA_RUNTIME 运行时集成: token_budget.py — Token 估算工具 SSoT (token_b... | 导入依赖 / import_depends |
| 8 | TruncationStrategy — TruncationStrategy (conte... | → | D_INFRA_RUNTIME 运行时集成: token_budget.py — Token 估算工具 SSoT (token_b... | 导入依赖 / import_depends |
| 9 | ContextBudgetTracker: token budget management w... | → | D_INFRA_RUNTIME 运行时集成: token_budget.py — Token 估算工具 SSoT (token_b... | 导入依赖 / import_depends |
| 10 | ContextInjector: retrieve and inject relevant k... | → | D_INFRA_RUNTIME 运行时集成: token_budget.py — Token 估算工具 SSoT (token_b... | 导入依赖 / import_depends |
| 11 | context_pipeline — Context Engine **四段流水线... | → | D_INFRA_RUNTIME 运行时集成: token_budget.py — Token 估算工具 SSoT (token_b... | 导入依赖 / import_depends |
| 12 | context_pipeline_auto.py — ContextPipeline 三.... | → | D_INFRA_RUNTIME 运行时集成: kill_switch.py -- safety circuit breaker (DD110... | 导入依赖 / import_depends |
| 13 | PromptRegistry: YAML-driven Prompt 模板注册表 (... | → | D_INFRA_RUNTIME 运行时集成: token_budget.py — Token 估算工具 SSoT (token_b... | 导入依赖 / import_depends |
| 14 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: AutoRuntimeCore — 三层运行时运营中心（系统大脑... | 测试依赖 / test_depends |
| 15 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: CapabilityRegistry — 能力注册中心 (capability_... | 测试依赖 / test_depends |
| 16 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: DreamCycle — 知识固化引擎 (dream_cycle.py) | 测试依赖 / test_depends |
| 17 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: HealthMonitor — 健康监控 + 自愈 (health_monito... | 测试依赖 / test_depends |
| 18 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: runtime_config.py | 测试依赖 / test_depends |
| 19 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: WorkDAG + WorkItem — 工作编排数据模型 (work_da... | 测试依赖 / test_depends |
| 20 | F1 AutoRuntimeCore 非mock端到端集成测试 (test_a... | → | D_INFRA_RUNTIME 运行时集成: work_orchestrator.py | 测试依赖 / test_depends |
| 21 | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | D_INFRA_RUNTIME 运行时集成: Pipeline — Backpressure Manager (backpressure_... | 测试依赖 / test_depends |
| 22 | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | D_INFRA_RUNTIME 运行时集成: backpressure_types.py - Pipeline backpressure s... | 测试依赖 / test_depends |
| 23 | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | D_INFRA_RUNTIME 运行时集成: DeadLetterQueue — 死信队列 (dead_letter_queue.py) | 测试依赖 / test_depends |
| 24 | F14 管线编排/反馈环 — 红蓝对抗端到端极端测试 (... | → | D_INFRA_RUNTIME 运行时集成: Pipeline 数据模型 (models.py) | 测试依赖 / test_depends |
| 25 | F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测... | → | D_INFRA_RUNTIME 运行时集成: DreamCycle — 知识固化引擎 (dream_cycle.py) | 测试依赖 / test_depends |
| 26 | F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测... | → | D_INFRA_RUNTIME 运行时集成: HealthMonitor — 健康监控 + 自愈 (health_monito... | 测试依赖 / test_depends |
| 27 | F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测... | → | D_INFRA_RUNTIME 运行时集成: WorkDAG + WorkItem — 工作编排数据模型 (work_da... | 测试依赖 / test_depends |
| 28 | F1 自动驾驶/运行时大脑 — 红蓝对抗端到端极端测... | → | D_INFRA_RUNTIME 运行时集成: work_orchestrator.py | 测试依赖 / test_depends |
| 29 | skill_executor.py | → | D_INTEGRATION 管线路由: Structural Protocol interfaces for cross-module... | 导入依赖 / import_depends |
| 30 | skill_router.py | → | D_INTEGRATION 管线路由: EmbeddingRouter — MOD-INF-011 双嵌入维度路由 (... | 导入依赖 / import_depends |
| 31 | MOD-INF-019: Agent Spec — SpecEngine 蓝图->Ski... | → | D_INTEGRATION 管线路由: Structural Protocol interfaces for cross-module... | 导入依赖 / import_depends |
| 32 | CE 向量写入器 — vectorize_and_store() 生产者 (... | → | D_INTEGRATION 管线路由: VMS 上下文注入器 — ingest_context() 消费者 (co... | 导入依赖 / import_depends |
| 33 | ContextAssembler — 上下文装配、校验、影子留档 ... | → | D_ORCHESTRATOR 代理编排器: contracts — orchestrator contracts subpackage.... | 导入依赖 / import_depends |
| 34 | ContextInjector: retrieve and inject relevant k... | → | D_SECURITY 对抗验证: gateway.py | 导入依赖 / import_depends |
| 35 | checkpoint_manager.py — Inject 前快照 (DD100, ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 36 | ContextAssembler — 上下文装配、校验、影子留档 ... | → | D_SHARED 共享服务: ports — D-DATA 服务的 Protocol 定义 (ports.py) | 导入依赖 / import_depends |
| 37 | ContextAssembler — 上下文装配、校验、影子留档 ... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 38 | ContextBudgetTracker: token budget management w... | → | D_SHARED 共享服务: Zero-dependency Observer pattern (subscribe/emi... | 导入依赖 / import_depends |
| 39 | ContextBudgetTracker: token budget management w... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 40 | ContextInjector: retrieve and inject relevant k... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 41 | ContextInjector: retrieve and inject relevant k... | → | D_SHARED 共享服务: async_utils.py — async/sync 边界桥接（5.12.8 .... | 导入依赖 / import_depends |
| 42 | context_pipeline — Context Engine **四段流水线... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 43 | context_pipeline_auto.py — ContextPipeline 三.... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 44 | file_autoregister.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 45 | PromptRegistry: YAML-driven Prompt 模板注册表 (... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 46 | PromptRegistry: YAML-driven Prompt 模板注册表 (... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 47 | skill_factory.py | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 48 | MOD-INF-019: Agent Spec — Skill Feedback Loop ... | → | D_SHARED 共享服务: serialization.py —— 统一序列化/反序列化基础设... | 导入依赖 / import_depends |
| 49 | MOD-INF-019: Agent Spec — Skill Freshness Exte... | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 导入依赖 / import_depends |
| 50 | skill-registry.py —— Skill 注册基座（Phase 14... | → | D_SHARED 共享服务: constants.py —— 共享枚举 & 常量集中 re-export... | 导入依赖 / import_depends |
| 51 | skill-registry.py —— Skill 注册基座（Phase 14... | → | D_SHARED 共享服务: yaml_utils.py — vocabulary YAML 加载公共工具（... | 导入依赖 / import_depends |
| 52 | skill-registry.py —— Skill 注册基座（Phase 14... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 53 | IntentKeywordMapper - Stage 1 of three-stage in... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 54 | IntentParser · 意图三阶段级联解析器（V-09） (i... | → | D_SHARED 共享服务: schemas.py | 导入依赖 / import_depends |
| 55 | SystemSnapshotter — M1 系统状态镜像（CL-017 RI... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 56 | SystemSnapshotter — M1 系统状态镜像（CL-017 RI... | → | D_SHARED 共享服务: SQLite 连接工厂真源（SSoT） (sqlite_factory.py) | 导入依赖 / import_depends |
| 57 | DocCompressor — 文档压缩服务（CL-018 RI 扩展模... | → | D_SHARED 共享服务: paths.py — 项目路径常量 SSoT（Single Source of... | 导入依赖 / import_depends |
| 58 | DocCompressor — 文档压缩服务（CL-018 RI 扩展模... | → | D_SHARED 共享服务: CBAC 能力检查器 (Capability-Based Access Contro... | 导入依赖 / import_depends |
| 59 | F1 事件触发启动测试 (test_f1_event_trigger.py) | → | D_SHARED 共享服务: EventBus — 事件总线（带背压控制）(M-07) (event... | 测试依赖 / test_depends |

### 依赖本域的其他域（入边）/ Depended By

| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |
|:--:|---------|:--:|---------|---------|
| 1 | D_FEEDBACK_LOOP 反馈循环引擎: FLE 全链路调度器 —— collect->detect->diagnose... | → | VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE... | 导入依赖 / import_depends |
| 2 | D_GOV_CODE_QUALITY 代码质量治理: 集成协调器 — 24集成+19更新+16GitHub整合. (inte... | → | context_rule_registry.py | 导入依赖 / import_depends |
| 3 | D_GOV_REPAIR 治理修复: budget_enforcement.py | → | skill_executor.py | 导入依赖 / import_depends |
| 4 | D_INFRA_RUNTIME 运行时集成: boot_hooks.py | → | MOD-INF-019: Agent Spec — Skill Freshness Exte... | 导入依赖 / import_depends |
| 5 | D_INFRA_RUNTIME 运行时集成: boot_hooks.py | → | MOD-INF-019: Agent Spec — Skill Lifecycle (ski... | 导入依赖 / import_depends |
| 6 | D_INTEGRATION 管线路由: SentinelServer: 意图路由哨兵 MCP Server (sentin... | → | IntentKeywordMapper - Stage 1 of three-stage in... | 导入依赖 / import_depends |
| 7 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | PipelineSkillBridge — Agent Spec -> Pipeline .... | 导入依赖 / import_depends |
| 8 | D_INTEGRATION 管线路由: PipelineOrchestrator — M1-M11 管线协调器 (pipe... | → | MOD-INF-019: Agent Spec — Skill Feedback Loop ... | 导入依赖 / import_depends |
| 9 | D_ORCHESTRATOR 代理编排器: Orc->CE 上下文桥接 — request_context() 生产者 ... | → | CE 向量写入器 — vectorize_and_store() 生产者 (... | 导入依赖 / import_depends |
| 10 | D_ORCHESTRATOR 代理编排器: Orc->VMS 记忆写入器 (memory_writer.py) | → | VectorBridge — CE↔VMS 检索桥接 (Connect CT-CE... | 导入依赖 / import_depends |
| 11 | D_SECURITY 对抗验证: Agent capability scope verification — 拒绝受限... | → | G-CT-003: Agent Spec -> RBAC capability check. ... | 导入依赖 / import_depends |

### 跨域依赖图 / Cross-domain Dependency Diagram

> 本域与 10 个外部域直接连接（出边 59 条 + 入边 11 条 = 70 条）。只显示直接连接的域，不展开具体节点。

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', 'primaryBorderColor': '#666666', 'lineColor': '#666666', 'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'}}}%%
graph LR
    D_AUTONOMY_CORE["D_AUTONOMY_CORE<br/>自治核心"]
    D_SHARED["D_SHARED<br/>共享服务"]
    D_INFRA_RUNTIME["D_INFRA_RUNTIME<br/>运行时集成"]
    D_INTEGRATION["D_INTEGRATION<br/>管线路由"]
    D_GOV_AUDIT["D_GOV_AUDIT<br/>审计追踪"]
    D_FEEDBACK_LOOP["D_FEEDBACK_LOOP<br/>反馈循环引擎"]
    D_GOV_RULE["D_GOV_RULE<br/>规则治理"]
    D_ORCHESTRATOR["D_ORCHESTRATOR<br/>代理编排器"]
    D_SECURITY["D_SECURITY<br/>对抗验证"]
    D_GOV_CODE_QUALITY["D_GOV_CODE_QUALITY<br/>代码质量治理"]
    D_GOV_REPAIR["D_GOV_REPAIR<br/>治理修复"]
    D_AUTONOMY_CORE -->|25条 导入依赖 / import_depends, 测试依赖 / test_depends| D_SHARED
    D_AUTONOMY_CORE -->|22条 导入依赖 / import_depends, 测试依赖 / test_depends| D_INFRA_RUNTIME
    D_AUTONOMY_CORE -->|4条 导入依赖 / import_depends| D_INTEGRATION
    D_AUTONOMY_CORE -->|3条 导入依赖 / import_depends| D_GOV_AUDIT
    D_AUTONOMY_CORE -->|2条 测试依赖 / test_depends| D_FEEDBACK_LOOP
    D_AUTONOMY_CORE -->|1条 导入依赖 / import_depends| D_GOV_RULE
    D_AUTONOMY_CORE -->|1条 导入依赖 / import_depends| D_ORCHESTRATOR
    D_AUTONOMY_CORE -->|1条 导入依赖 / import_depends| D_SECURITY
    D_INTEGRATION -->|3条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_INFRA_RUNTIME -->|2条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_ORCHESTRATOR -->|2条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_FEEDBACK_LOOP -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOV_CODE_QUALITY -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_SECURITY -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
    D_GOV_REPAIR -->|1条 导入依赖 / import_depends| D_AUTONOMY_CORE
```

## 说明 / Notes

- **数据源 / Data Source**: `depgraph (PostgreSQL)` 的 `nodes`、`edges`、`domains` 表
- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）
- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新
- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`
- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / `[unknown]`=未知
