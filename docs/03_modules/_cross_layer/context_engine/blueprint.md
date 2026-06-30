---
module_id: MOD-CONTEXT_ENGINE
submodule_path: src/zephyr/intelligence/context_management
title: Context Engine 集成蓝图 — Core Pipeline + Governance & Operations 双蓝图索引
doc_type: blueprint
template_for: blueprint
status: Draft
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: 2026-05-07
updated: 2026-05-19
valid_from: 2026-05-07
ttl: permanent
construction_progress: design_only
actual_disk_path: src/zephyr/intelligence/context_management/
belongs_to: MOD-MASTER_BLUEPRINT
parent_module:
generation: 1
functional_domain: intelligence
last_verified: 2026-05-19
last_updated: 2026-05-19
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: Context Engine 集成索引蓝图——拆分为 Core Pipeline (MOD-INF-008A, 40文件) + Governance & Operations (MOD-INF-008B, 47文件)。87个 .py 文件全部已实现。
tags: [context-engine, ce, context-injection, rag, token-budget, build-compress-validate-inject, infrastructure, capacity-planning, governance, operations]
priority: P0
runtime_plane: hot
depends_on:
- {target: architecture_model/layers/b_context_engine.yaml", at: "全篇", why: "CE YAML SSoT——本蓝图真源"}
child_modules:
---

# Context Engine 集成蓝图 — Core Pipeline + Governance & Operations 双蓝图索引

> module_id: MOD-CONTEXT_ENGINE | version: 1.0.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/orchestration/context_management/ | generation: 1 | construction_progress: completed
> child_modules: MOD-INF-008A (Core Pipeline, 40文件) | MOD-INF-008B (Governance & Operations, 47文件)
> 蓝图+施工图模板：[TPL-BLUEPRINT-001](file:///D:/ZephyrAlpha/docs/03_modules/template-registry.yaml)

## 概述

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-CONTEXT_ENGINE`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

### §0.1 代码文件清单

> 本蓝图为集成索引，代码文件清单见子蓝图：MOD-INF-008A（Core Pipeline, 40文件）、MOD-INF-008B（Governance & Operations, 47文件）

本蓝图是 Context Engine 的集成索引。MOD-CONTEXT_ENGINE 已拆分为两个职责单一的子蓝图，87 个 .py 文件全部已实现（含 assembly/management/parsing/support 5 子包 + config/2 yaml）。

| 子蓝图 | 功能域 | 文件数 | 蓝图路径 |
|--------|------|:---:|------|
| **MOD-INF-008A** | Core Pipeline — build→compress→validate→inject 四阶段流水线 + Token预算三级管控 + VMS 4C检索桥接 + LSG安全审查 + MCP Agentic Pull接口 | 40 | [sub-blueprints/MOD-INF-008A-blueprint.md](sub-blueprints/MOD-INF-008A-blueprint.md) |
| **MOD-INF-008B** | Governance & Operations — 健康评分(ContextHealthScore) + 生命周期(ContextEvictor/ContextRotModel/SessionLearner) + 安全防护(AdversarialRobustness/PoisoningMonitor) + 熔断监控(KillSwitch/OTel/SelfDiagnosis) + 运维支撑 | 47 | [sub-blueprints/MOD-INF-008B-blueprint.md](sub-blueprints/MOD-INF-008B-blueprint.md) |

canonical SSoT 为 [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_context_engine.yaml)，代码落位 `src/zephyr/orchestration/context_management/`。

---

## 子蓝图文件清单分发

### Core Pipeline (MOD-INF-008A — 40 文件)

**assembly 子包 (4):** context_assembler.py, context_injector.py, context_pipeline.py, \_\_init\_\_.py
**parsing 子包 (3):** intent_keyword_mapper.py, intent_parser.py, \_\_init\_\_.py
**support 子包 (5):** architecture_context_loader.py, doc_compressor.py, prompt_registry.py, system_snapshot.py, \_\_init\_\_.py
**根级 (28):** context_assembler.py, context_budget_tracker.py, context_injector.py, context_pipeline.py, context_rule_registry.py, doc_compressor.py, intent_keyword_mapper.py, intent_parser.py, pattern_library.py, prompt_registry.py, system_snapshot.py, pipeline_orchestrator.py, vector_bridge.py, context_budget.py, token_budget.py, complexity_budget.py, budget_forecaster.py, atomic_injector.py, diff_injector.py, progressive_disclosure_injector.py, contextual_fetch_api.py, mcp_adapter.py, ce_bootstrap.py, cold_start_booster.py, mode_manager.py, context_model_strategy.py, dispatch_table.py, dependency_tracker.py, architecture_context_loader.py

> 详细描述、§0 对齐矩阵、契约、约束、施工指引 → [MOD-INF-008A 蓝图](sub-blueprints/MOD-INF-008A-blueprint.md)

### Governance & Operations (MOD-INF-008B — 47 文件)

**management 子包 (4):** context_budget_tracker.py, context_evictor.py, context_rot_model.py, \_\_init\_\_.py
**根级 (43):** ContextHealthScore.py, \_\_init\_\_.py, adversarial_robustness.py, alignment_scorer.py, architecture_context_loader.py, cache_invalidation.py, ce_explain_cli.py, ce_playground_v2.py, ce_vibe_shortcuts.py, checkpoint_manager.py, citation_walker.py, config_safety_guard.py, context_debt_score.py, context_evaluator.py, context_evictor.py, context_outcome_tracker.py, context_playground.py, context_rot_model.py, context_value_attribution.py, curation_loop.py, diversity_constraint.py, domain_decay_config.py, embedding_version_lock.py, fallback_staleness_gate.py, fragmentation_index.py, host_resource_governor.py, integrity_check.py, kill_switch.py, knowledge_distiller.py, list_ce_files.py, lsg_pattern_tracker.py, memory_bank.py, otel_instrumentation.py, poisoning_monitor.py, position_optimizer.py, rational.py, self_diagnosis.py, sensitivity_classifier.py, session_learner.py, shadow_canary.py, solo_dev_safety_net.py, staleness_manager.py, verify_paths.py

> 详细描述、§0 对齐矩阵、安全管道、熔断机制 → [MOD-INF-008B 蓝图](sub-blueprints/MOD-INF-008B-blueprint.md)

---

## 跨模块契约

| CT-* | 涉及系统 | 方向 | 说明 |
|------|---------|------|------|
| CT-ORC-CE-001 | Orc→CE | → | Orc 在任务启动时→CE.build(task_card, session_id) |
| CT-CE-VMS-001 | CE→VMS | → | CE.build()→VMS.search()→4C 检索 |
| CT-CE-LSG-001 | CE→LSG | → | CE.validate()→LSG 三层审查→PASS/FAIL |

## 依赖关系

| 依赖模块 | 依赖类型 | 依赖内容 | 蓝图路径 |
|---------|---------|---------|---------|
| MOD-INF-011 VMS | 必须 | 知识检索 | `docs/03_modules/_domain-infra_ops/vector-memory/blueprint.md` |
| MOD-TASK_SYSTEM Task System | 必须 | 任务状态 | `docs/03_modules/_cross_layer/task-system/blueprint.md` |
| MOD-LLM_SECURITY LSG | 必须 | 安全校验 | `docs/03_modules/_cross_layer/llm-security/blueprint.md` |
| MOD-KB-001 | 必须 | 知识库检索源 | `docs/03_modules/_domain-infra_ops/knowledge-base/blueprint.md` |
| MOD-INF-035 AutoRuntime Core | 可选 | 运行时调度 | `docs/03_modules/_cross_layer/auto-runtime-core/blueprint.md` |

## 消费者注册表

| 消费者 | 消费方式 | 契约 |
|--------|---------|------|
| MOD-MASTER_BLUEPRINT (Orchestrator) | 调用 CE.build() | CT-ORC-CE-001 |
| MOD-INF-011 (VMS) | 被 CE 检索 | CT-CE-VMS-001 |
| MOD-LLM_SECURITY (LSG) | 被 CE 调用审查 | CT-CE-LSG-001 |
| AI Agent (via MCP) | 调用 /ce:fetch | DD113 |

## 项目中已有类似功能

| 模块 | 覆盖范围 | 与 CE 的区别 |
|------|---------|-------------|
| MOD-TASK_SYSTEM (Orchestrator) | Agent session 管理 | Orc 管理 Agent 生命周期；CE 管理上下文内容 |
| MOD-INF-011 (VMS) | 向量存储与检索 | VMS 是存储层；CE 是消费层 |
| MOD-LLM_SECURITY (LSG) | 安全审查 | LSG 是安全门；CE 是上下文管道 |
| MOD-KB-001 (知识库) | KE CRUD | KB 是数据源；CE 是数据消费者 |

## 集成目标

| # | 集成目标 | 对接模块 | 接口 | 状态 |
|---|---------|---------|------|:---:|
| 1 | Orchestrator 消费 CE 输出 | MOD-TASK_SYSTEM | CE→Orc 优先级协议 | ✅ 已实现 |
| 2 | VMS 知识检索 | MOD-INF-011 | build 阶段查询 | ✅ 已实现 |
| 3 | LSG 安全审查 | MOD-LLM_SECURITY | validate 阶段审查 | ✅ 已实现 |

## 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 集成蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context-engine\blueprint.md` | 本文件 |
| 008A 子蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context-engine\sub-blueprints\MOD-INF-008A-blueprint.md` | Core Pipeline |
| 008B 子蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context-engine\sub-blueprints\MOD-INF-008B-blueprint.md` | Governance & Operations |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\context-engine\` | 87 个 .py 文件 |
| 测试代码 | `D:\ZephyrAlpha\tests\context-engine\` | CE 测试用例 |

## 必备链接

| 资源 | 路径 |
|------|------|
| CE YAML SSoT | [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_context_engine.yaml) |
| 代码落位 | `src/zephyr/context-engine/` |
| 总蓝图 | [MASTER-001](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md) |
| VMS 蓝图 | MOD-INF-011 |
| LSG 蓝图 | MOD-LLM_SECURITY |
| Orchestrator 蓝图 | MOD-TASK_SYSTEM |
| 知识库蓝图 | MOD-KB-001 |
| 蓝图注册表 | [blueprint_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) |

---

## ⚠️ Vibe Coding 蓝图编写铁律（委托到子蓝图）

| # | 铁律 | 委托 |
|---|------|------|
| 1 | 代码文件 MUST 标注 `[BLUEPRINT] MOD-CONTEXT_ENGINE \| 本蓝图 §N` | → 008A/008B §0 |
| 2 | 代码文件 MUST 标注 `[INVARIANTS]` 不变量 | → 008A §5 |
| 3 | 蓝图 §4 文件清单 ↔ 代码 `[BLUEPRINT]` 字段 MUST 双向对齐 | → 008A/008B §0 |

## 变更同步规则

| 修改此文件 | MUST 同步更新 |
|-----------|-------------|
| 子蓝图文件清单 | 对应 §0 代码文件清单 |
| child_modules | blueprint_registry.yaml |
| frontmatter version | blueprint_registry.yaml |
| 契约变更 | 对应 CT-* 契约文件 + 子蓝图 §4 |

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 上下文引擎——9文件骨架+assembler+injector已实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/orchestration/context_management/adversarial_robustness.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/alignment_scorer.py` | ✅ 已实现 | |
| `src/zephyr/context-engine/architecture-context.json` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/architecture_context_loader.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/assembly/context_assembler.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/assembly/context_injector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/assembly/context_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/atomic_injector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/budget_forecaster.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/cache_invalidation.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/ce_bootstrap.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/ce_explain_cli.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/ce_playground_v2.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/ce_vibe_shortcuts.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/checkpoint_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/citation_walker.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/cold_start_booster.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/complexity_budget.py` | ✅ 已实现 | |
| `src/zephyr/context-engine/config/compression_policy.yaml` | ✅ 已实现 | |
| `src/zephyr/context-engine/config/context-rules.yaml` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/config_safety_guard.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_assembler.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_budget.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_budget_tracker.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_debt_score.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_evaluator.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_evictor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_health_score.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_injector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_model_strategy.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_outcome_tracker.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_pipeline.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_playground.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_rot_model.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_rule_registry.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/context_value_attribution.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/contextual_fetch_api.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/curation_loop.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/dependency_tracker.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/diff_injector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/dispatch_table.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/diversity_constraint.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/doc_compressor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/domain_decay_config.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/embedding_version_lock.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/fallback_staleness_gate.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/fragmentation_index.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/host_resource_governor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/integrity_check.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/intent_keyword_mapper.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/intent_parser.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/kill_switch.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/knowledge_distiller.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/list_ce_files.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/lsg_pattern_tracker.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/management/context_budget_tracker.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/management/context_evictor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/management/context_rot_model.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/mcp_adapter.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/memory_bank.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/mode_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/otel_instrumentation.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/parsing/intent_keyword_mapper.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/parsing/intent_parser.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/pattern_library.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/pipeline_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/poisoning_monitor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/position_optimizer.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/progressive_disclosure_injector.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/prompt_registry.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/rational.py` | ✅ 已实现 | |
| `src/zephyr/context-engine/risk-register.yaml` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/self_diagnosis.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/sensitivity_classifier.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/session_learner.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/shadow_canary.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/solo_dev_safety_net.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/staleness_manager.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/support/architecture_context_loader.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/support/doc_compressor.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/support/prompt_registry.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/support/system_snapshot.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/system_snapshot.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/token_budget.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/vector_bridge.py` | ✅ 已实现 | |
| `src/zephyr/orchestration/context_management/verify_paths.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_context_injector.py` | ✅ 已实现 | |
| `tests/unit/test_doc_compressor.py` | ✅ 已实现 | |
| `tests/unit/test_prompt_registry.py` | ✅ 已实现 | |
| `tests/unit/test_intent_parser.py` | ✅ 已实现 | |
| `tests/unit/test_intent_keyword_mapper.py` | ✅ 已实现 | |
| `tests/unit/test_pattern_library.py` | ✅ 已实现 | |
| `tests/unit/test_system_snapshot.py` | ✅ 已实现 | |

### 1.3 配置文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `config/context_rules.yaml` | ✅ 已实现 | |
| `config/compression_policy.yaml` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-05-19 | 1.0.0 | 拆分为 MOD-INF-008A (Core Pipeline, 40文件) + MOD-INF-008B (Governance & Operations, 47文件)。原 1085 行详细内容分发到子蓝图，本文件改为集成索引。 |
| 2026-05-14 | v3.3 | 蓝图模板 v3.5 重构（历史版本） |
| 2026-05-13 | L1 | 规格化（历史版本） |
| 2026-05-07 | 0.8.0 | 第十七轮零债务对齐（历史版本） |
