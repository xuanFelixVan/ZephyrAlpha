---
module_id: MOD-CONTEXT_ENGINE
submodule_path: src/zephyr/autonomy_core/context
title: Context Engine 集成蓝图 — 上下文引擎集成索引
doc_type: blueprint
template_for: blueprint
status: Active
version: 1.1.0
layer: L1_foundation
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: 2026-05-07
updated: 2026-07-02
valid_from: 2026-05-07
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: src/zephyr/autonomy_core/context/
belongs_to: MOD-MASTER_BLUEPRINT
parent_module:
generation: 1
functional_domain: intelligence
last_verified: 2026-07-02
last_updated: 2026-07-02
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: Context Engine 集成索引蓝图——上下文注入管道(build→compress→validate→inject)+Token预算管控。代码位于 src/zephyr/autonomy_core/context/（22个.py文件），部分实现。
tags: [context_engine, ce, context-injection, rag, token-budget, build-compress-validate-inject, infrastructure, governance, operations]
priority: P0
runtime_plane: hot
depends_on:
- {target: "architecture_model/layers/b_context_engine.yaml", at: "全篇", why: "CE YAML SSoT——本蓝图真源"}
child_modules:
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Context Engine 集成蓝图 — 上下文引擎集成索引

> module_id: MOD-CONTEXT_ENGINE | version: 1.1.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/autonomy_core/context/ | generation: 1 | construction_progress: partially_implemented
> 蓝图+施工图模板：[TPL-BLUEPRINT-001](file:///D:/ZephyrAlpha/docs/03_modules/template_registry.yaml)

## 概述

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-CONTEXT_ENGINE`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

Context Engine 是 ZephyrAlpha 的上下文注入管道，负责 build→compress→validate→inject 四阶段流水线 + Token 预算管控。代码位于 `src/zephyr/autonomy_core/context/`（22 个 .py 文件，平铺无子包）。

canonical SSoT 为 [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_context_engine.yaml)，代码落位 `src/zephyr/autonomy_core/context/`。

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
| MOD-INF-011 VMS | 必须 | 知识检索 | `docs/03_modules/_domain_knowledge/vector_memory/blueprint.md` |
| MOD-TASK_SYSTEM Task System | 必须 | 任务状态 | `docs/03_modules/_cross_layer/task_system/blueprint.md` |
| MOD-LLM_SECURITY LSG | 必须 | 安全校验 | `docs/03_modules/_cross_layer/large_language_model_security/blueprint.md` |
| MOD-KB-001 | 必须 | 知识库检索源 | `docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md` |
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
| 集成蓝图 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\context_engine\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\autonomy_core\context\` | 22 个 .py 文件 |
| 测试代码 | `D:\ZephyrAlpha\tests\context\` | CE 测试用例 |

## 必备链接

| 资源 | 路径 |
|------|------|
| CE YAML SSoT | [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_context_engine.yaml) |
| 代码落位 | `src/zephyr/autonomy_core/context/` |
| 总蓝图 | [MASTER-001](file:///D:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint.md) |
| VMS 蓝图 | MOD-INF-011 |
| LSG 蓝图 | MOD-LLM_SECURITY |
| Orchestrator 蓝图 | MOD-TASK_SYSTEM |
| 知识库蓝图 | MOD-KB-001 |
| 蓝图注册表 | [blueprint_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 说明 |
|---|------|------|
| 1 | 代码文件 MUST 标注 `[BLUEPRINT] MOD-CONTEXT_ENGINE \| docs/03_modules/_cross_layer/context_engine/blueprint.md \| §N` | 防幻觉锚点 |
| 2 | 代码文件 MUST 标注 `[INVARIANTS]` 不变量 | 契约约束 |
| 3 | 蓝图 §1 文件清单 ↔ 代码 `[BLUEPRINT]` 字段 MUST 双向对齐 | 三方对齐 |

## 变更同步规则

| 修改此文件 | MUST 同步更新 |
|-----------|-------------|
| §1 代码文件清单 | blueprint_registry.yaml（via sync_registry_from_blueprints.py）|
| frontmatter version | blueprint_registry.yaml |
| 契约变更 | 对应 CT-* 契约文件 |

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/autonomy_core/context/__init__.py` | ✅ 已实现 | 模块导出 |
| `src/zephyr/autonomy_core/context/ce_bootstrap.py` | ✅ 已实现 | CE 启动 |
| `src/zephyr/autonomy_core/context/ce_explain_cli.py` | ✅ 已实现 | CE CLI |
| `src/zephyr/autonomy_core/context/ce_playground_v2.py` | ✅ 已实现 | CE Playground |
| `src/zephyr/autonomy_core/context/ce_vibe_shortcuts.py` | ✅ 已实现 | CE 快捷方式 |
| `src/zephyr/autonomy_core/context/context_assembler.py` | ✅ 已实现 | 上下文组装 |
| `src/zephyr/autonomy_core/context/context_budget.py` | ✅ 已实现 | Token 预算 |
| `src/zephyr/autonomy_core/context/context_budget_tracker.py` | ✅ 已实现 | 预算追踪 |
| `src/zephyr/autonomy_core/context/context_debt_score.py` | ✅ 已实现 | 债务评分 |
| `src/zephyr/autonomy_core/context/context_evaluator.py` | ✅ 已实现 | 上下文评估 |
| `src/zephyr/autonomy_core/context/context_evictor.py` | ✅ 已实现 | 上下文驱逐 |
| `src/zephyr/autonomy_core/context/context_health_score.py` | ✅ 已实现 | 健康评分 |
| `src/zephyr/autonomy_core/context/context_injector.py` | ✅ 已实现 | 上下文注入 |
| `src/zephyr/autonomy_core/context/context_model_strategy.py` | ✅ 已实现 | 模型策略 |
| `src/zephyr/autonomy_core/context/context_outcome_tracker.py` | ✅ 已实现 | 结果追踪 |
| `src/zephyr/autonomy_core/context/context_pipeline.py` | ✅ 已实现 | Core Pipeline |
| `src/zephyr/autonomy_core/context/context_pipeline_auto.py` | ✅ 已实现 | 自动管道 |
| `src/zephyr/autonomy_core/context/context_playground.py` | ✅ 已实现 | Playground |
| `src/zephyr/autonomy_core/context/context_rot_model.py` | ✅ 已实现 | Rot 模型 |
| `src/zephyr/autonomy_core/context/context_rule_registry.py` | ✅ 已实现 | 规则注册 |
| `src/zephyr/autonomy_core/context/context_value_attribution.py` | ✅ 已实现 | 价值归因 |

### 1.2 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下

---

## 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-07-02 | 1.1.0 | 修正蓝图漂移：actual_disk_path 统一为 autonomy_core/context/，删除不存在的子蓝图 MOD-INF-008A/008B 引用，§1 文件清单从 86 个错误路径重写为 22 个实际文件，construction_progress 统一为 partially_implemented，修复 YAML 语法错误 |
| 2026-05-19 | 1.0.0 | 拆分为 MOD-INF-008A (Core Pipeline, 40文件) + MOD-INF-008B (Governance & Operations, 47文件)。原 1085 行详细内容分发到子蓝图，本文件改为集成索引。 |
| 2026-05-14 | v3.3 | 蓝图模板 v3.5 重构（历史版本） |
| 2026-05-13 | L1 | 规格化（历史版本） |
| 2026-05-07 | 0.8.0 | 第十七轮零债务对齐（历史版本） |

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CONTEXT_ENGINE`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CONTEXT_ENGINE` 的 63 个 file 节点 | design | `extract_depgraph.py --modules MOD-CONTEXT_ENGINE` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CONTEXT_ENGINE | MOD-CONTEXT_ENGINE | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | planned | ✅ |
| file_count | 63 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
