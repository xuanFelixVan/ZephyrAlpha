---
module_id: MOD-GOV-SYNC-PANORAMA
title: "四图模块对齐引擎蓝图 — depgraph/dataflow/decision/blueprint 四图对齐"
doc_type: blueprint
status: Active
version: "1.1.0"
layer: L1_foundation
layer_name: cross_layer
functional_domain: governance
responsibility_domain: 
build_status: generated
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.2
valid_from: 2026-07-09
actual_disk_path: "scripts/governance/sync_panorama_module.py; scripts/governance/d5_architecture/generators/align_panoramas.py; scripts/governance/d5_architecture/syncers/blueprint_frontmatter_reconciler.py"
ttl: permanent
construction_progress: partially_implemented
date: "2026-07-10"
tags:
  - panorama-alignment
  - four-way-alignment
  - module-sync
  - depgraph
  - dataflowgraph
  - decisiongraph
  - blueprint-reconciler
  - majority-vote-aggregation
summary: >
  四图模块对齐引擎——depgraph/dataflowgraph/decisiongraph/blueprint.md 四图模块对齐。
  4 核心字段（module_id/domain_id/design_maturity/build_status）跨四图同步。
  单模块同步+全量同步+transition 触发+blueprint 缺失标记+多数投票聚合。
design_maturity: prototype
---

# 四图模块对齐引擎蓝图 — depgraph/dataflow/decision/blueprint 四图对齐

> module_id: MOD-GOV-SYNC-PANORAMA | version: 1.1.0 | status: Active
> actual_disk_path: sync_panorama_module.py + align_panoramas.py + blueprint_frontmatter_reconciler.py

## 概述

本蓝图描述 ZephyrAlpha 的**四图模块对齐引擎**——它解决了架构图中模块在不同图之间名称/编号/域/状态不一致的问题。

核心能力：当用户在 depgraph（依赖图）中添加一个设计态模块后，引擎自动将该模块同步到另外三张图（dataflowgraph 数据流图 / decisiongraph 决策图 / blueprint.md 蓝图文档），使同一个模块在四张图中都能找到、位置对齐、四个核心字段一模一样。

**用户场景**：对某个架构图输入添加了一堆设计态模块 → 这些模块自动在四个架构图写入、显示、对齐位置、名字、编号等一模一样 → 一个同样的模块，在四个架构图都能找到位置。

---

## §1 对齐的图与字段

### 1.1 四张图

| # | 图 | 存储 | 表/位置 | 说明 |
|---|---|------|---------|------|
| 1 | depgraph（依赖图） | PostgreSQL | `nodes` / `edges` / `domains` | **真源**——模块定义的源头，blueprint_id 作为 module_id 对齐 key |
| 2 | dataflowgraph（数据流图） | PostgreSQL | `dataflow_jobs` / `dataflow_datasets` / `dataflow_edges` | 数据流作业，job_name=module_id 对齐 |
| 3 | decisiongraph（决策图） | PostgreSQL | `decision_layers` / `decision_nodes` | 决策层，layer_id=module_id 对齐 |
| 4 | blueprint.md（蓝图文档） | 文件系统 | `docs/03_modules/*.md` frontmatter | YAML frontmatter 中的 module_id 对齐 |

### 1.2 四个核心字段

四张图通过这 4 个字段保持模块对齐——任何一个字段不一致即为"对齐问题"。

| # | 字段 | depgraph 列 | dataflow 列 | decision 列 | blueprint frontmatter key | 说明 |
|---|------|------------|------------|------------|--------------------------|------|
| 1 | module_id | `blueprint_id` | `job_name` | `layer_id` | `module_id` | 模块唯一标识，四图对齐的主键 |
| 2 | domain_id | `domain_id` | `domain_id` | `domain_id` | `responsibility_domain` | 责任域（如 D_TRADING / D_GOVERNANCE） |
| 3 | design_maturity | `design_maturity` | `design_maturity` | `design_maturity` | `design_maturity` | 设计成熟度：design < prototype < production |
| 4 | build_status | `build_status` | `build_status` | `build_status` | `build_status` | 构建状态：planned / generated / ... |

> **字段名差异**：blueprint frontmatter 用 `responsibility_domain`（语义命名），其他三图用 `domain_id`（技术命名）。引擎自动映射。

---

## §2 对齐机制

### 2.1 同步引擎（sync_panorama_module.py）

引擎以 depgraph 为真源，将模块的 4 个核心字段同步到另外三图。

| 命令 | 作用 | 触发场景 |
|------|------|---------|
| `python scripts/governance/sync_panorama_module.py <MODULE_ID>` | 同步单个模块 | 新增模块后手动触发 |
| `python scripts/governance/sync_panorama_module.py --all` | 同步所有模块 | 全量对齐校准 / 定期维护 |

**单模块同步流程**（`sync_module_panorama(module_id)`）：

```
1. 从 depgraph.nodes 读取模块的 4 核心字段（多数投票聚合，见 §3）
2. 同步到 dataflow_jobs（_sync_to_dataflow）
   - 如已存在非占位记录 → 更新核心字段
   - 如不存在 → 插入占位记录（entity_type='module_placeholder'）
3. 同步到 decision_layers（_sync_to_decision）
   - 如已存在非占位 layer → 更新核心字段
   - 如不存在 → 插入占位记录（track='placeholder'）
4. 同步到 blueprint.md（reconcile_blueprint_frontmatter）
   - 如 blueprint_path 有值 → 更新该文件的 frontmatter
   - 如 blueprint_path 为空 → 使用命名约定 docs/03_modules/<module_id>.md 查找
   - 文件不存在 → 标记缺失跳过（不创建文件，输出 warning）
```

### 2.2 transition 自动触发

状态转换（transition）完成后自动触发四图同步——模块状态变更时无需手动同步。

### 2.3 blueprint 对齐（blueprint_frontmatter_reconciler.py）

| 场景 | 行为 |
|------|------|
| blueprint_path 有值且文件存在 | 更新 frontmatter 的 4 核心字段 |
| blueprint_path 有值但无 .md 扩展名 | 自动补 .md（DCR-005 合规） |
| blueprint_path 为空 | 使用命名约定 `docs/03_modules/<module_id>.md` 查找 |
| 命名约定文件不存在 | **标记缺失跳过**（不创建文件，输出 warning） |
| 命名约定文件已存在 | 更新 frontmatter（不覆盖正文） |

---

## §3 聚合策略（多数投票）

### 3.1 为什么需要聚合

depgraph.nodes 中同一个 `blueprint_id` 可有多行——这是**跨域模块的正常现象**。例如 MOD-INF-002（基础设施模块）有 79 行，分布在 8 个域（D_GOVERNANCE 22 行 / D_INFRA_RUNTIME 20 行 / D_AUDITTEST 17 行 / ...）。

如果用 `LIMIT 1` 取第一行，domain_id 取值不稳定（取决于 SQL 返回顺序），会导致四图域不一致误报。

### 3.2 聚合规则

三个组件（`_query_depgraph_module` / `_query_module_bp` / `_fetch_depgraph_nodes`）使用**完全一致**的聚合策略：

| 字段 | 聚合策略 | 理由 |
|------|---------|------|
| domain_id | **多数投票**（`Counter.most_common`） | 取代表性域，避免单行取值不稳定 |
| design_maturity | **取最 design 状态**（min rank：design=0 < prototype=1 < production=2） | 与 `_detect_state_drifts` 聚合策略一致，保守取最不成熟状态 |
| build_status | **取第一个非空**（ORDER BY 保证非空优先） | build_status 通常单值 |
| blueprint_path/path | **取第一个非空**（`ORDER BY (path IS NULL), path`） | 有路径的行更可能是模块主节点 |

### 3.3 一致性保证

三个组件共享同一套聚合规则，确保：
- 同步引擎写入的值 = 对齐检测读取的值
- 不会因聚合策略不一致而产生虚假的"域不一致"告警

---

## §4 对齐验证（align_panoramas.py）

### 4.1 对齐报告

```bash
python scripts/governance/d5_architecture/generators/align_panoramas.py
```

输出：`docs/02_enterprise_architecture/generated/panorama_alignment_report.md`

报告检测 4 类对齐问题：

| 问题类型 | 含义 | 严重性 |
|---------|------|--------|
| 孤儿（仅一图存在） | 模块只在一张图出现，其他三图缺失 | warn-only |
| 状态漂移（design_maturity 不一致） | 同一模块在不同图 design_maturity 不同 | warn-only |
| 域不一致（domain_id 不一致） | 同一模块在不同图 domain_id 不同 | 三图内部不一致→阻断；blueprint-only→warn |
| 设计态孤立（design 仅一图） | design_maturity=design 的模块仅一张图有 | warn-only |

### 4.2 GATE-PANORAMA-ALIGNMENT 阻断策略

| 情形 | 处理 |
|------|------|
| depgraph/dataflow/decision 三图中 ≥2 个不同的非空 domain | **硬阻断**（gate 阻断提交） |
| 仅 blueprint 与三图不一致 | warn-only（不阻断） |

### 4.3 当前对齐状态（2026-07-09）

```
四图节点数: depgraph=140 / dataflow=165 / decision=296 / blueprint=220
问题总数: 35（修复前 64，-45%）
  - 域不一致: 37 → 9（-76%，剩余为平局/非标准 domain 历史数据）
  - 状态漂移: 7 → 2（-71%）
  - 孤儿: 23（历史蓝图文件，不在 depgraph 登记）
  - 设计态孤立: 1
```

---

## §5 对齐清单（会扩张）

### 5.1 清单真源

对齐清单的**真源是 depgraph.nodes 中的 `blueprint_id`**。清单会随 depgraph 的扩张自动扩张——新增模块自动进入对齐范围，无需手动维护清单。

### 5.2 新增模块的完整工作流

```
# 1. 在 depgraph 添加设计态模块（真源）
python scripts/governance/apply_depgraph.py --add-module MOD-NEW-001 \
    --domain D_TRADING --maturity design --status planned

# 2. 同步到四图（自动写入 dataflow/decision）
python scripts/governance/sync_panorama_module.py MOD-NEW-001

# 3. 验证对齐（生成报告）
python scripts/governance/d5_architecture/generators/align_panoramas.py
```

执行后：
- `dataflow_jobs` 表新增一行（job_name=MOD-NEW-001, entity_type='module_placeholder'）
- `decision_layers` 表新增一行（layer_id=MOD-NEW-001, track='placeholder'）
- `docs/03_modules/MOD-NEW-001.md` 如已存在则更新 frontmatter（不存在则标记缺失跳过，需手动创建蓝图）
- 三图对齐率保持 100%（dataflow/decision 自动写入占位记录）

### 5.3 清单扩张的自动化保证

| 扩张场景 | 自动化机制 |
|---------|-----------|
| 新增模块 | sync_panorama_module.py 自动写入 dataflow/decision 两图 |
| 模块状态变更 | transition 自动触发同步 |
| 全量校准 | sync --all 重新同步所有模块 |
| 对齐检测 | align_panoramas.py 生成报告 + gate 阻断 |

---

## §6 三图如何对齐（dataflow/decision/blueprint）

### 6.1 dataflowgraph 对齐

| 项 | 说明 |
|---|------|
| 目标表 | `dataflow_jobs` |
| 对齐 key | `job_name` = module_id |
| 占位策略 | 如不存在 → 插入 `entity_type='module_placeholder'` 的占位记录 |
| 已有记录 | 如已存在非占位记录（entity_type != 'module_placeholder'）→ 仅更新 4 核心字段，不改 entity_type |
| 特殊 | jobs 查询用 `NULL AS domain_id`，jobs 不参与 domain 对齐检测 |

### 6.2 decisiongraph 对齐

| 项 | 说明 |
|---|------|
| 目标表 | `decision_layers` |
| 对齐 key | `layer_id` = module_id |
| 占位策略 | 如不存在 → 插入 `track='placeholder'` 的占位记录 |
| 已有记录 | 如已存在非占位 layer（track != 'placeholder'）→ 仅更新 4 核心字段，不改 track |

### 6.3 blueprint.md 对齐

| 项 | 说明 |
|---|------|
| 目标位置 | `docs/03_modules/<module_id>.md`（命名约定）或 blueprint_path 指定的路径 |
| 对齐 key | frontmatter 中的 `module_id` |
| 文件不存在 | 标记缺失跳过（不创建文件，输出 warning） |
| 文件已存在 | 更新 frontmatter 的 4 字段，不覆盖正文内容 |
| frontmatter 不存在 | 跳过（不强制添加） |
| 字段映射 | `responsibility_domain` ↔ `domain_id`（自动映射） |

---

## §7 代码文件清单

| # | 文件 | 路径 | 职责 |
|---|------|------|------|
| 1 | sync_panorama_module.py | `scripts/governance/sync_panorama_module.py` | 同步引擎——单模块/全量同步四图核心字段 |
| 2 | align_panoramas.py | `scripts/governance/d5_architecture/generators/align_panoramas.py` | 对齐检测——生成 panorama_alignment_report.md |
| 3 | blueprint_frontmatter_reconciler.py | `scripts/governance/d5_architecture/syncers/blueprint_frontmatter_reconciler.py` | blueprint 对齐——更新 blueprint.md frontmatter（缺失则标记跳过） |

---

## §8 已知限制

| # | 限制 | 根因 | 影响 | 解决方向 |
|---|------|------|------|---------|
| 1 | 平局 domain 不稳定 | 多数投票在平局时取第一个（如 D_AUDITTEST(2) vs D_GOV_SCRIPTS(2)） | 9 个模块域不一致 | 增加 tie-breaking 规则（如按域优先级） |
| 2 | 非标准 domain 值 | 部分 blueprint 用了非标准值（如 `auto_runtime_core` / `agent_orchestrator`） | 2 个模块域不一致 | 清理 blueprint frontmatter，统一用 D_ 前缀标准值 |
| 3 | 历史孤儿蓝图 | 17 个历史蓝图文件（master/cross_layer）不在 depgraph 登记 | 对齐报告显示孤儿 | 决定是否在 depgraph 登记或删除孤儿蓝图 |
| 4 | blueprint 缺失不自动创建 | reconciler 在文件不存在时标记缺失跳过（不创建文件） | 模块无蓝图文件时 blueprint 图缺失该模块 | 手动创建蓝图后更新 depgraph 的 blueprint_path 指向正式蓝图路径 |

---

## §9 决策记录

| # | 决策 | 选项 | 选中 | 依据 |
|---|------|------|------|------|
| 1 | 四图对齐 key | module_id / blueprint_id / path | module_id（depgraph 的 blueprint_id） | 跨图唯一标识，已在 depgraph 使用 |
| 2 | 聚合策略 | LIMIT 1 / 多数投票 | 多数投票 | 跨域模块多行，LIMIT 1 取值不稳定 |
| 3 | blueprint_path 为空时 | 跳过 / 自动创建 | 标记缺失跳过（不创建文件） | 避免自动生成大量空蓝图；blueprint 图对齐依赖手动创建蓝图 |
| 4 | dataflow/decision 占位策略 | 不创建 / 创建占位记录 | 创建占位记录（module_placeholder / placeholder） | 确保三图都有该模块节点 |
| 5 | GATE 阻断范围 | 四图全阻断 / 三图阻断 | 三图内部不一致阻断，blueprint-only warn | blueprint 数据质量较低，warn-only 避免过度阻断 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| 四图 | depgraph + dataflowgraph + decisiongraph + blueprint.md | 全景图 | 全景图是更广的概念（含 44 个全景图），四图是模块对齐的 4 张图 |
| 对齐 | 同一 module_id 在四图中的 4 核心字段一致 | 同步 | 同步是动作，对齐是结果 |
| 多数投票 | 同一 blueprint_id 多行的 domain_id 取出现次数最多的值 | 平均/第一行 | 平均无意义（domain 是枚举），第一行不稳定 |
| 占位记录 | dataflow/decision 中 entity_type='module_placeholder' / track='placeholder' 的记录 | 正式记录 | 占位记录仅含 4 核心字段，正式记录有完整业务字段 |
| 孤儿模块 | 仅在一张图存在的模块 | 漂移模块 | 孤儿是缺失，漂移是字段不一致 |
