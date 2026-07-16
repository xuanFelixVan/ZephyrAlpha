---
module_id: MOD-MASTER_BLUEPRINT
submodule_paths_scope: all-modules
title: "Master Blueprint Index 蓝图 — 集成闭环总蓝图索引·指向3个拆分蓝图"
doc_type: blueprint
status: Active
version: "1.3.1"
layer: L1_foundation
layer_name: cross_layer
blueprint_level: domain
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
ttl: permanent
last_updated: "2026-05-15"
last_verified: "2026-05-15"
construction_progress: partially_implemented
actual_disk_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\"
template_for: blueprint
generation: 2
functional_domain: infrastructure
parent_module: "SYS-MASTER-001"
belongs_to: "SYS-MASTER-001"
rule_form: structural
scope: global
stability: stable
verifiability: manual
priority: P0
runtime_plane: cold
summary: "集成闭环总蓝图索引文件。本文件仅保留索引和导航信息。"
codification_level: L1
codification_at: "2026-05-15"
depends_on:
  - target: "MOD-MASTER-002"
    at: "全篇"
    why: "基线蓝图——v0.9.2 现存设计"
  - target: "MOD-MASTER-003"
    at: "全篇"
    why: "容量设计蓝图——v1.1.0 升级章"
  - target: "MOD-MASTER-001"
    at: "全篇"
    why: "Agent Spec接口蓝图——§十五CBAC+Skill路由"
references:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_baseline.md"
    section: "全篇"
    why: "基线蓝图"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_capacity.md"
    section: "全篇"
    why: "容量蓝图"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master_blueprint\\blueprint_agent_spec.md"
    section: "全篇"
    why: "Agent Spec蓝图"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\templates\\blueprint-template.md"
    section: "全篇"
    why: "蓝图模板v3.5/v3.6"
  - path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\trae_030_doc_numbering_metadata.yaml"
    section: "全篇"
    why: "压缩工作流标准"
tags:
  - master-blueprint
  - index
  - cross-layer
  - integration
responsibility_domain: 
build_status: deprecated
design_maturity: design
---

# Master Blueprint Index 蓝图 — 集成闭环总蓝图索引·指向3个拆分蓝图

> module_id: MOD-MASTER_BLUEPRINT | version: 1.3.1 | status: active | layer: cross_layer | blueprint_level: domain
> actual_disk_path: D:\ZephyrAlpha\docs\03_modules\_master_blueprint\ | generation: 2 | construction_progress: partially_implemented

## 概述

本文件是 MOD-MASTER_BLUEPRINT 集成闭环总蓝图的索引导航文件。核心职责：提供 3 个拆分蓝图的路径导航、阅读顺序指引。新 AI session 应按场景按需读取对应的拆分蓝图——而非本索引文件。上游依赖 SYS-MASTER-001，下游被 3 个拆分蓝图消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

## 模板章节映射表

> 本文件为索引导航文件，模板必需章节由 3 个拆分蓝图覆盖。
> **v3.6 变更**：§7 备选方案已删除（由 §18 决策记录"选项"列覆盖）；§15 后果已删除（正面与 §1 重复，负面合并到 §14 风险"类型"列）。

| 模板必需章节 | 覆盖蓝图 | 对应章节 |
|------------|---------|---------|
| §1-§6 设计 | MOD-MASTER-002 | §零~§十四 + §十六~§三十七 |
| §0 代码对齐 | MOD-MASTER-002 | §零 |
| §8-§14 设计 | MOD-MASTER-002 | §十六~§三十七 |
| §16-§18 施工 | MOD-MASTER-002 | §十六~§三十七 |
| §17 容量升级 | MOD-MASTER-003 | §-1/§-2 |
| §18 决策记录（含原§7备选项） | MOD-MASTER-002 | §三十七 |
| 治理信息 | MOD-MASTER-002 | 末尾 |
| §7 备选方案 | 已删除→§18决策记录覆盖 | v3.6删除 |
| §15 后果 | 已删除→正面在§1，负面在§14 | v3.6删除 |

## 拆分蓝图导航

| 蓝图文件 | module_id | 版本 | 内容 |
|---------|-----------|------|------|
| [blueprint_baseline.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_baseline.md) | MOD-MASTER-002 | v0.9.2 | §零~§十四+§十六~§三十七（12系统拓扑+63条CT-*契约+共享Schema+全局状态传播+容量预算+施工Phase+Anti-Patterns+设计决策+集成测试+风险+治理） |
| [blueprint_capacity.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_capacity.md) | MOD-MASTER-003 | v1.1.0 | §-1/§-2（容量升级：二次审计12缺口+10个升级章） |
| [blueprint_agent_spec.md](file:///d:/ZephyrAlpha/docs/03_modules/_master_blueprint/blueprint_agent_spec.md) | MOD-MASTER-001 | v1.1.0 | §十五（CBAC能力访问控制矩阵+违规响应+离线更新+编排器特权+Skill路由） |

## 12 个集成系统

# | 系统 | 模块蓝图 | 关键 CT-* |
|---|------|:---:|------|
1 | Agent Orchestrator | MOD-TASK_SYSTEM | CT-ORC-SCRIPT, CT-ORC-CE, CT-ORC-VMS, CT-ORC-GATE, CT-ORC-DB |
2 | Script System | MOD-INF-005 | CT-ORC-SCRIPT, CT-SCRIPT-KB, CT-SCRIPT-GATE |
3 | Knowledge Base | MOD-KB-001 | CT-SCRIPT-KB, CT-KB-VMS |
4 | Gate Engine | MOD-GATE_ENGINE | CT-ORC-GATE, CT-SCRIPT-GATE |
5 | Context Engine | MOD-CONTEXT_ENGINE | CT-ORC-CE, CT-CE-VMS, CT-CE-LSG |
6 | Task Pipeline | MOD-INF-009 | CT-PIPE-ORC |
7 | Feedback Loop Engine | MOD-FEEDBACK_LOOP | CT-FLE-ORC, CT-FLE-DB, CT-TELE-FLE |
8 | Vector Memory Service | MOD-INF-011 | CT-ORC-VMS, CT-CE-VMS, CT-KB-VMS |
9 | Database | MOD-DATABASE | CT-FLE-DB, CT-ORC-DB |
10 | MCP Servers | MOD-INF-013 | — |
11 | LLM Security Gateway | MOD-LLM_SECURITY | CT-CE-LSG |
12 | System Telemetry | MOD-INF-015 | CT-TELE-FLE |

## 阅读顺序

| 场景 | 阅读路径 |
|------|---------|
| 新 AI session 冷启动 | baseline §零（分派表）→ baseline §二（契约总表 ai_read_only_hint） |
| 容量升级施工 | capacity §-2（缺口清单）→ capacity §-1（升级章）→ baseline（对照现有设计） |
| Agent/Skill 开发 | agent-spec §十五（CBAC矩阵）→ baseline §二（契约定义） |
| 跨系统集成开发 | baseline §一（系统拓扑）→ baseline §二（契约总表）→ 按需读具体 CT-* |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径 | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | construction_progress 必须与代码实际状态一致 | 重复造轮子或跳过施工 |
| 6 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4） | 双源漂移 |

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-MASTER_BLUEPRINT`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案等临时内容一旦执行完毕即从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责不清 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

| STEP | 操作 | 判定标准 |
|:---:|------|---------|
| 1 | 识别职责域 | 该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？ |
| 2a | 职责相同→原地升级 | 服务对象相同 + 变更频率同步 + 依赖关系重叠 → 在 §17 容量升级附录中增量记录 |
| 2b | 职责不同→拆分独立蓝图 | 满足任一：a)独立 module_id 前缀 b)独立 Phase 路线图 c)独立依赖图（交集<50%）d)内容>100行且无直接数据流 → 创建子蓝图，本蓝图 §10 引用 |
| 3 | 拆分后验证 | 子蓝图 MUST 有独立 frontmatter + 概述 + §0~§18；belongs_to = 本蓝图 module_id；本蓝图 §10 新增引用；blueprint_registry.yaml 同步更新 |

### 本蓝图拆分状态

本蓝图已执行拆分：3 个子蓝图（BASELINE/CAPACITY/AGENT-SPEC），拆分依据见拆分蓝图导航表。

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。索引文件为纯导航型，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则 |
| 2 | 目录结构标准 | GOV-DOC-002 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/013 |
| 4 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 5 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 6 | 基线蓝图 | MOD-MASTER-002 | v0.9.2 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` | 现存设计 |
| 7 | 容量蓝图 | MOD-MASTER-003 | v1.1.0 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_capacity.md` | 升级设计 |
| 8 | Agent Spec蓝图 | MOD-MASTER-001 | v1.1.0 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_agent_spec.md` | CBAC+Skill |

---

## 项目中已有类似功能

| # | 已有模块 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|---------|------------|----------|-------------|
| 1 | SYS-MASTER-001 | `D:\ZephyrAlpha\docs\03_modules\_system_master\blueprint.md` | 系统拓扑 | SYS-MASTER 定义"谁有什么"，本蓝图定义"之间怎么连" |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 索引文件 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint.md` | 修改 | 本文件 |
| 2 | 基线蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_baseline.md` | 读取 | 子蓝图 |
| 3 | 容量蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_capacity.md` | 读取 | 子蓝图 |
| 4 | Agent Spec蓝图 | `D:\ZephyrAlpha\docs\03_modules\_master_blueprint\blueprint_agent_spec.md` | 读取 | 子蓝图 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 总蓝图不产生代码，仅定义集成契约

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 集成闭环总蓝图索引 | **本文档** | — |
| 12系统拓扑+契约 | **MOD-MASTER-002** | — |
| 容量升级设计 | **MOD-MASTER-003** | — |
| CBAC+Skill路由 | **MOD-MASTER_BLUEPRINT** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-MASTER-002 | 索引导航 |
| Tier 1 | MOD-MASTER-003 | 索引导航 |
| Tier 1 | MOD-MASTER_BLUEPRINT | 索引导航 |
| Tier 2 | SYS-MASTER-001 | 子蓝图引用 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 拆分蓝图路径变更 | 更新导航表 | 更新 blueprint_registry.yaml |
| 新增拆分蓝图 | 更新导航表+阅读顺序 | 更新 blueprint_registry.yaml |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 拆分蓝图路径变更 | 需 Owner 审批 |
| 新增拆分蓝图 | 需 Owner 审批 |
| 阅读顺序调整 | AI 可自主修改 |

### 负向责任

| # | 本蓝图不涉及 | 由谁负责 |
|---|-------------|---------|
| 1 | 12 系统集成契约定义 | MOD-MASTER-002 负责 |
| 2 | 容量升级设计 | MOD-MASTER-003 负责 |
| 3 | CBAC 矩阵定义 | MOD-MASTER_BLUEPRINT 负责 |

### 触发条件

| 场景 | AI 应读取本蓝图 |
|------|---------------|
| 首次进入 MOD-MASTER_BLUEPRINT 体系 | 读本索引了解 3 个拆分蓝图的关系 |
| 不确定该读哪个拆分蓝图 | 看拆分蓝图导航 + 阅读顺序 |

### 导航路径

| 步骤 | 操作 |
|:---:|------|
| 1 | 读本索引 → 了解 3 个拆分蓝图定位 |
| 2 | 按场景选读拆分蓝图：集成开发→baseline, 容量升级→capacity, Skill开发→agent-spec |
| 3 | 如需跨蓝图细节 → 回到本索引查 cross-reference |

### 漂移防护

| 修改本文件 | 必须同步更新 |
|-----------|------------|
| 拆分蓝图路径变更 | 本索引导航表 + blueprint_registry.yaml |
| 新增拆分蓝图 | 本索引全部导航表 + blueprint_registry.yaml |
| 拆分蓝图内容重排 | 本索引阅读顺序 + 模板章节映射表 |

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-MASTER_BLUEPRINT`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-MASTER_BLUEPRINT` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-MASTER_BLUEPRINT` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-MASTER_BLUEPRINT | MOD-MASTER_BLUEPRINT | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | deprecated | deprecated | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
