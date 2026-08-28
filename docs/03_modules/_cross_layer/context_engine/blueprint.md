---
module_id: MOD-CONTEXT_ENGINE
submodule_path: src/zephyr/autonomy_core/context
title: Context Engine 集成蓝图 — 上下文引擎集成索引
doc_type: blueprint
template_for: blueprint
status: Active
version: 1.2.6
layer: L1_foundation
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: 2026-05-07
updated: 2026-08-22
valid_from: 2026-05-07
ttl: permanent
actual_disk_path: src/zephyr/autonomy_core/context/
belongs_to: MOD-MASTER_BLUEPRINT
parent_module:
generation: 1
functional_domain: intelligence
last_verified: 2026-08-22
last_updated: 2026-08-22
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
summary: Context Engine 集成索引蓝图——上下文注入管道(build→compress→validate→inject)+Token预算管控。代码位于 src/zephyr/autonomy_core/context/（39个.py文件，38模块+__init__.py），四段管道已实现（inject段API就绪、生产数据源待接线，见 07_context_engine_build.md Phase 1）。
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

> module_id: MOD-CONTEXT_ENGINE | version: 1.2.0 | status: Active | layer: cross_layer
> actual_disk_path: src/zephyr/autonomy_core/context/ | generation: 1 | construction_progress: completed（inject 段 API 就绪、生产数据源待接线——07 号文 Phase 1 补缺项）
> 蓝图+施工图模板：[TPL-BLUEPRINT-001](file:///D:/ZephyrAlpha/docs/03_modules/template_registry.yaml)

## 概述

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-CONTEXT_ENGINE`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

Context Engine 是 ZephyrAlpha 的上下文注入管道，负责 build→compress→validate→inject 四阶段流水线 + Token 预算管控。代码位于 `src/zephyr/autonomy_core/context/`（39 个 .py 文件：38 个模块 + `__init__.py`，平铺无子包；2026-08-22 实测总行数 4586）。

四段现状（07 号文 §2.1 实测）：build/compress/validate 三段生产可用（Assembler 装配+DocCompressor 压缩+G3 门禁），inject 段三模式 API 就绪但生产返回空 InjectedContext（数据源未接线）；组合根 `context_pipeline.run_context_four_stage()` 显式编排四段。

canonical SSoT 为 [b_context_engine.yaml](file:///D:/ZephyrAlpha/architecture_model/layers/b_context_engine.yaml)，代码落位 `src/zephyr/autonomy_core/context/`。

---

## 跨模块契约

| CT-* | 涉及系统 | 方向 | 说明 |
|------|---------|------|------|
| CT-ORC-CE-001 | Orc→CE | → | Orc 在任务启动时→CE.build(task_card, session_id) |
| CT-CE-VMS-001 | CE→VMS | → | CE.build()→VMS.search()→4C 检索 |
| CT-CE-LSG-001 | CE→LSG | → | CE.validate()→LSG 三层审查→PASS/FAIL |

## 依赖关系

> **2026-08-22 depgraph 真源对齐（#255⑤ / #ARCH-164 尾巴）**：以 PG depgraph 实测 import 边为准——CE 出边 26 条：MOD-INF-016×10、内部×6、MOD-INF-001×6、MOD-INF-002×2、MOD-SHARED-001×1、MOD-LLM_SECURITY×1。

| 依赖模块 | 依赖类型 | 依赖内容 | 蓝图路径 |
|---------|---------|---------|---------|
| MOD-INF-001 capacity_assurance | 必须 | token 预算（token_budget×5 文件）+熔断（kill_switch×1）——depgraph 实测 6 边 | `docs/03_modules/_domain_infrastructure_operations/capacity_assurance/index.md` |
| MOD-LLM_SECURITY LSG | 必须 | 安全校验（context_injector→gateway 实测 1 边） | `docs/03_modules/_cross_layer/large_language_model_security/blueprint.md` |
| MOD-INF-011 VMS | 必须（协议注入） | 知识检索——vector_bridge 依赖 VMSSearchProtocol 而非具体实现，depgraph 无 import 边属**正确反映**（CT-CE-VMS-001） | `docs/03_modules/_domain_knowledge/vector_memory/blueprint.md` |
| MOD-TASK_SYSTEM Task System | 事件驱动（无 import 边） | 任务状态——接口形态=boot 触发注册+EventBus 订阅（07 文 Q2 部分成立）；boot_hooks 接线缺口归 Q2 Owner 裁定项 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` |
| MOD-INF-035 AutoRuntime Core | 可选（无 import 边） | 运行时调度——代码实测无 import 对应，同归 07 文 Q2 裁定语境 | `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md` |

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
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\autonomy_core\context\` | 39 个 .py 文件 |
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

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> **2026-08-22 过滤器治本闭环注记（#255⑤）**：生成器 SQL 过滤器已由 `generated` 单值扩为 `generated/testing/stable` 三态（生命周期推进后代码仍在盘），本表重跑幂等覆盖——§1.1 源码 1 行→39 行全量派生（38 stable+1 generated），行数为 `(Get-Content).Count` 实测口径见 §2。

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/autonomy_core/context/__init__.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/autonomy/test_checkpoint_manager.py` | ✅ 已实现 | |
| `tests/autonomy/test_complexity_budget.py` | ✅ 已实现 | |
| `tests/autonomy/test_context_pipeline_red_blue.py` | ✅ 已实现 | |
| `tests/autonomy/test_integrity_check.py` | ✅ 已实现 | |
| `tests/autonomy/test_lsg_pattern_tracker.py` | ✅ 已实现 | |
| `tests/autonomy/test_shadow_canary.py` | ✅ 已实现 | |
| `tests/autonomy/test_solo_dev_safety_net.py` | ✅ 已实现 | |
| `tests/autonomy/test_staleness_manager.py` | ✅ 已实现 | |
| `tests/autonomy/test_vector_bridge.py` | ✅ 已实现 | |
| `tests/autonomy/test_verify_paths.py` | ✅ 已实现 | |
| `tests/ce/test_ce_bootstrap.py` | ✅ 已实现 | |
| `tests/ce/test_ce_explain_cli.py` | ✅ 已实现 | |
| `tests/ce/test_ce_playground_v2.py` | ✅ 已实现 | |
| `tests/ce/test_ce_vibe_shortcuts.py` | ✅ 已实现 | |
| `tests/cold/test_cold_start_booster.py` | ✅ 已实现 | |
| `tests/config/test_config_safety_guard.py` | ✅ 已实现 | |
| `tests/context/test_context_budget_tracker.py` | ✅ 已实现 | |
| `tests/context/test_context_debt_score.py` | ✅ 已实现 | |
| `tests/context/test_context_engine_pipeline.py` | ✅ 已实现 | |
| `tests/context/test_context_health_score.py` | ✅ 已实现 | |
| `tests/context/test_context_model_strategy.py` | ✅ 已实现 | |
| `tests/context/test_context_pipeline_auto.py` | ✅ 已实现 | |

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

## 2. 维护优先级分类（P0-3 实证，2026-08-22）

> 依据 07_context_engine_build.md §4 Phase 0：**只标不删**——核心=四段管道主链必需；辅助=支撑件（有生产/脚本消费者）；候选废弃=无生产消费者（仅测试消费）的陈旧件，物理删除待 07 号文 §6 Q5 Owner 裁定。
> 消费者证据：2026-08-22 全仓 import 扫描（src/scripts/tests 三域）；接线状态指是否被四段组合根/自动化层 import。

### 2.1 核心子集（15）——四段管道主链必需，优先维护

| 文件 | 管道位 | 接线/消费者证据 |
|------|-------|----------------|
| `context_pipeline.py` | 组合根 | ← context_pipeline_auto；→ assembler/injector/rule_registry |
| `context_assembler.py` | build/compress/validate | ← context_pipeline；→ rule_registry + DocCompressor(shared) + token_budget(infra) |
| `context_injector.py` | inject | ← context_pipeline + `prompt_registry.py`（src 消费）；→ token_budget(infra) |
| `context_budget.py` | 预算 | 仅测试消费；四段预算语义核心（截断策略 SSoT），未直接接线 |
| `context_budget_tracker.py` | 预算 | `system_snapshot.py` 版本钉引用；三级阈值告警，未直接接线 |
| `context_evictor.py` | compress 辅助 | 仅测试消费；条目级逐出（与 DocCompressor 内容级压缩互补），未直接接线 |
| `vector_bridge.py` | build 检索桥 | ← `feedback_loop/scheduler.py` + `orchestrator/execution/memory_writer.py`（2 src 消费）；VMSSearchProtocol 协议注入 |
| `context_pipeline_auto.py` | 自动化层 | → kill_switch(infra) + EventBus；[CONSUMERS] 声称 boot_hooks 实测未接线（07 号文 Q2 登记） |
| `memory_bank.py` | 持久上下文 | 仅测试消费；6 个结构化 .md 跨 session 持久层 |
| `context_rule_registry.py` | 规则注入 | ← context_assembler + context_pipeline + `gov_code_quality/code_dedup/integration_hub.py`（1 src 消费） |
| `integrity_check.py` | validate 辅助 | 仅测试消费；注入后完整性校验，未直接接线 |
| `checkpoint_manager.py` | inject 辅助 | 仅测试消费；Inject 前快照，未直接接线 |
| `atomic_injector.py` | inject 辅助 | 仅测试消费；原子注入（temp-file + os.replace），未直接接线 |
| `ce_bootstrap.py` | 自举 | 仅测试消费；CE_MVP/FUNCTIONAL/FULL_CE 三级自举入口 |
| `__init__.py` | 包入口 | 38 模块 `__all__` 导出（无初始化逻辑） |

### 2.2 辅助（1）——有非测试消费者，保留维护

| 文件 | 消费者证据 |
|------|-----------|
| `shadow_canary.py` | ← `scripts/ops/shadow_canary_deploy.py`（运维脚本真实 import）+ 测试 |

### 2.3 候选废弃（23）——无生产消费者（仅各自测试消费），只标不删，待 Q5 裁定

| 类别 | 文件 |
|------|------|
| 治理辅助 | context_rot_model、context_evaluator、curation_loop、fallback_staleness_gate、context_outcome_tracker、context_debt_score、context_model_strategy、mode_manager、diversity_constraint、staleness_manager、position_optimizer、domain_decay_config、diff_injector、context_value_attribution、context_health_score、complexity_budget、cold_start_booster |
| 工具/CLI | ce_file_lister、ce_explain_cli、ce_vibe_shortcuts |
| 工具/实验 | context_playground、ce_playground_v2 |
| 接口骨架 | contextual_fetch_api（硬编码返回，07 号文 Phase 3 登记升级为真实查询） |

> 注：上述 23 个文件均有对应测试且测试全绿（见 §1.2），"候选废弃"指标记维护优先级最低、不再扩展新功能；物理删除需 07 号文 §6 Q5 Owner 裁定后另行施工。

---

## 变更记录

| 日期 | 版本 | 变更摘要 |
|------|------|---------|
| 2026-08-22 | 1.2.0 | P0 对齐收口（07 号文 §4 Phase 0 / 18 号清单 w3-07）：文件清单 22→39（§1.1 全量重写，含行数与职责）；construction_progress partially_implemented→completed（inject 段 API 就绪待接线限定）；frontmatter build_status planned→stable、design_maturity design→production（与 depgraph 38 个 stable 文件节点 + 38 个 [MATURITY] production 代码头一致）；§1.2 测试地址簿 21→68（全仓 import 扫描实证口径）；新增 §2 维护优先级分类（核心 15 / 辅助 1 / 候选废弃 23，只标不删）；§1.1 补 depgraph generated/stable 过滤器结构性低报的手工对齐注记；测试基线 956 用例全绿（含 test_ce_kill_switch 陈旧导入路径修复激活 16 例） |
| 2026-07-02 | 1.1.0 | 修正蓝图漂移：actual_disk_path 统一为 autonomy_core/context/，删除不存在的子蓝图 MOD-INF-008A/008B 引用，§1 文件清单从 86 个错误路径重写为 22 个实际文件，construction_progress 统一为 partially_implemented，修复 YAML 语法错误 |
| 2026-05-19 | 1.0.0 | 拆分为 MOD-INF-008A (Core Pipeline, 40文件) + MOD-INF-008B (Governance & Operations, 47文件)。原 1085 行详细内容分发到子蓝图，本文件改为集成索引。 |
| 2026-05-14 | v3.3 | 蓝图模板 v3.5 重构（历史版本） |
| 2026-05-13 | L1 | 规格化（历史版本） |
| 2026-05-07 | 0.8.0 | 第十七轮零债务对齐（历史版本） |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CONTEXT_ENGINE`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CONTEXT_ENGINE` 的 63 个 file 节点 | design | `extract_depgraph.py --modules MOD-CONTEXT_ENGINE` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
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
