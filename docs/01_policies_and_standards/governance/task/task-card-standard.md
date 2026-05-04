---
module_id: GOV-TASK-001
title: "任务卡操作指南"
doc_type: standard
status: active
version: "3.0.0"
layer: cross_layer
area: governance
priority: P0
author_agent: Trae
approver: ZephyrAlpha-Owner
classification: public
evolution_policy: rewritable
ai_autonomy: immutable_core
rule_form: declarative
date: "2026-05-01"
scope: global
owner: ZephyrAlpha-Owner
stability: stable
ttl: permanent
verifiability: manual
tags: [task, governance, guide]
language: zh
created_by: human_plus_agent
depends_on:
  - target: PS-STD-001
    at: "§7"
    why: "metadata-registry.md §7 定义了任务卡全部 28 个字段和 task_id 格式的权威规则"
summary: "任务卡的操作指南——正文结构规范、路径与依赖速查、门禁快速参考。字段定义以 metadata-registry.md §7 为准。v3.0.0：拆分——§3 字段定义全部归入 registry，本文件降格为操作指南。"
related:
  - GOV-AI-008
  - GOV-TASK-004
  - GOV-TASK-005
---

# 任务卡操作指南

> **字段定义以 [metadata-registry.md §7](../../meta/metadata-registry.md) 为唯一真源，本文件不重复定义。**
>
> 本文档是操作指南，告诉 AI "拿到一个任务卡该怎么填、怎么验收"。

## 1. 定位

本标准是任务卡的**操作指南**。管三件事：
- 任务卡正文怎么写（§3 正文结构——"读→做→产→检"四步）
- 路径和依赖怎么填（§4~§5 速查）
- 创建前和完成后要检查什么（§7 门禁速查）

## 2. 适用范围

所有新建任务卡，无论存储形式（SQLite 数据库或 Markdown 文件）。

## 3. 正文结构

每张任务卡的正文必须包含以下章节，按顺序。

### 3.1 目标

1-3 句话说清楚：**为什么做、做什么、关键约束**。

✅ 正确示例：
> 为 SQLite 任务仓库添加 CRUD 操作（INSERT/SELECT/UPDATE/DELETE）。本任务是 beta 数据层核心，后续 3 个任务依赖此产出。

### 3.2 触发条件

列出开始本任务前必须满足的前置条件：

```
- {前置任务 task_id} 已通过（前置）
- {蓝图/规则} 已落地（已满足）
```

### 3.3 执行步骤——"读→做→产→检"

必须按以下四步写：

| 步骤 | 怎么写 |
|------|--------|
| **读** | 列出本任务需要读取的所有文件（绝对路径），与 `files_in_scope` 对应 |
| **做** | 具体的操作步骤，按时间顺序写 |
| **产** | 列出本任务产出的所有文件（绝对路径），与 `deliverables` 对应 |
| **检** | 自检方法——运行什么命令、检查什么结果 |

### 3.4 验收标准

用表格列出量化指标：

| # | 指标 | 目标 |
|---|------|------|
| 1 | {指标名} | {可量化的目标值} |

**共享度量标签**（建议使用，便于统一验收语言）：

| 标签 | 含义 | 示例目标 |
|------|------|---------|
| `coverage` | 测试覆盖率 | `≥ 80%` |
| `build` | 构建通过 | `0 errors` |
| `lint` | 代码规范 | `0 errors, 0 warnings` |
| `files` | 文件完整性 | `deliverables 全部存在 + UTF-8` |
| `diff` | diff 范围 | `仅修改 files_in_scope` |

### 3.5 风险与缓解

| 风险 | 缓解 |
|------|------|
| {风险描述} | {缓解措施} |

## 4. 路径规范速查

> 字段定义见 [metadata-registry.md §7.4](../../meta/metadata-registry.md)

| # | 规则 |
|---|------|
| 1 | 必须使用绝对路径（如 `D:\ZephyrAlpha\src\...`），禁止相对路径 |
| 2 | 必须列出所有相关文件——AI 不会猜，漏一个就可能找不到 |
| 3 | 路径必须指向 `D:\ZephyrAlpha\` |
| 4 | `deliverables` 与 `files_in_scope` 不能完全重叠（除非原地修改） |

## 5. 依赖验真速查

> 字段定义见 [metadata-registry.md §7.5](../../meta/metadata-registry.md)

| 场景 | 行为 |
|------|------|
| depends_on 所有 task_id 均存在且终态 | ✅ 允许开始 |
| depends_on 中有 task_id 不存在 | ❌ G0 阻止创建 |
| depends_on 中有 task_id 非终态 | ⚠️ 可创建，状态自动 = PENDING |
| depends_on = `[]` 或字段缺失 | ✅ 无前置约束 |

## 6. 废弃字段速查

> 完整清单见 [metadata-registry.md §7.11](../../meta/metadata-registry.md)

| 废弃字段 | 替代方案 |
|---------|---------|
| `predecessor` | → `depends_on` |
| `model_preference` | → `execution_model` |
| `ai_autonomy`（任务卡中） | 由 `classification` + `safety_level` 推导 |
| `owner` | 系统默认 |
| `version` / `layer`（任务卡中） | 由 git / `namespace` 推导 |
| `est_hours` / `created` | → `estimate_hours` / `created_at` |

## 7. 门禁快速参考

> 本节为快速参考。权威定义以 [task-lifecycle-standard.md](../../governance/task/task-lifecycle-standard.md)（治理规则）、[task-card-kms/blueprint.md](../../../03_modules/l01_infrastructure/task-card-kms/blueprint.md) §5.3（门禁细则）和 [task-closure-standard.md](../../governance/task/task-closure-standard.md)（关闭验证）为准。

### 7.1 G0 创建门禁（创建任务卡前检查）

1. 必填字段完整性——对照 [metadata-registry.md §7 字段总表](../../meta/metadata-registry.md) 中标记为"必填"的字段
2. task_id 格式符合 `{NAMESPACE}-{SEQ}`
3. files_in_scope 中的路径必须物理存在
4. execution_model 必须是合法枚举值
5. depends_on 中的 task_id 必须在系统中已存在（若引用外部任务）

### 7.2 G5 完成门禁（关闭任务卡前检查）

1. deliverables 中所有文件物理存在
2. 无残留临时文件（`.backup` / `.tmp` / `temp_*`）
3. 验收标准全部达标——逐项对照 §3.4 验证
4. 文件编码 UTF-8，换行符 LF

## 8. 完整示例

```yaml
task_id: SRC-042
title: 实现 SQLite 任务仓库 CRUD + 10 状态机
phase: implement
status: PENDING
priority: P1
execution_model: claude-sonnet-4.6
model_rationale: Sonnet 擅长结构化代码编写且便宜，本任务涉及 3 个文件修改，无需 Opus 架构推理
safety_level: M
classification: public
evolution_policy: rewritable
estimate_hours: 2.5
files_in_scope:
  - D:\ZephyrAlpha\src\zephyr\schemas.py
  - D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py
  - D:\ZephyrAlpha\src\zephyr\db\task_repo.py
  - D:\ZephyrAlpha\src\zephyr\cli\task_cli.py
deliverables:
  - D:\ZephyrAlpha\src\zephyr\db\sqlite_schema.py
  - D:\ZephyrAlpha\src\zephyr\db\task_repo.py
  - D:\ZephyrAlpha\tests\test_task_repo.py
depends_on:
  - SRC-041
acceptance:
  - "CRUD 全覆盖（INSERT/SELECT/UPDATE/DELETE）"
  - "10 状态机转换全部实现"
tags:
  -
  - datalayer
  - origin:#17

# 正文

## 目标
为 SQLite 任务仓库添加完整 CRUD 操作和 10 状态机实现。这是 beta 数据层核心组件，后续任务依赖此产出。

## 触发条件
- SRC-041（SQLite 基础框架搭建）已通过

## 执行步骤

### 读
- `schemas.py`（TaskCard & TaskNamespace 模型 + TaskStatus 枚举）
- `sqlite_schema.py`（当前表结构）
- `task_repo.py`（当前仓库实现）
- `cli/task_cli.py`（CLI 接口定义）

### 做
1. 扩展 `sqlite_schema.py`——添加 tasks 表完整 DDL（28 字段 + 索引）
2. 实现 `task_repo.py` INSERT/SELECT/UPDATE/DELETE + 状态机转换
3. 编写 `test_task_repo.py`——测试 CRUD + 10 状态流转 + 边界条件
4. 更新 `task_cli.py`——命令参数适配新 schema

### 产
- `sqlite_schema.py`（tasks 表 DDL）
- `task_repo.py`（CRUD + 状态机）
- `tests/test_task_repo.py`（全覆盖测试）

### 检
```bash
pytest tests/test_task_repo.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | coverage | 60%+（数据库层最小要求） |
| 2 | lint | 0 errors, 0 warnings |
| 3 | files | deliverables 全部存在 + UTF-8 |
| 4 | diff | 仅修改 files_in_scope |
```

## 9. 与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| [metadata-registry.md §7](../../meta/metadata-registry.md) | 任务卡字段定义的唯一真源（28 字段 + task_id 格式） |
| [task-card-kms/blueprint.md §5.3](../../../03_modules/l01_infrastructure/task-card-kms/blueprint.md) | G0-G6 门禁的详细检查项 |
| [task-lifecycle-standard.md](../../governance/task/task-lifecycle-standard.md) | 治理规则：取消权限 + 优先级裁决 + 升级治理 |
| [task-closure-standard.md](../../governance/task/task-closure-standard.md) | 关闭验证的完整流程 |
| [handoff-protocol.md](../../governance/ai/handoff-protocol.md) | 任务交接时状态变更协议 |

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 3.0.0 | 2026-05-01 | **拆分**：§3 字段定义（原名 §3.1~§3.10）全部归入 metadata-registry.md §7；§5 命名空间归入 registry §9.3+§7.10；§6 状态机归入 registry §4.2。本文件降格为操作指南（正文结构 + 速查 + 门禁 + 示例） |
| 2.0.0 | 2026-04-29 | #12 裁定后重写——task_id 格式升级、字段定义调整为 vl-04 标准、模型论证判据标准化 |
| 1.0.0 | — | 初始版本 |
