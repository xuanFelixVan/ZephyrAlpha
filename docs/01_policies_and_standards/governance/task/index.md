---
module_id: GOV-TASK-000
title: "任务系统架构总览"
doc_type: index
status: active
version: "2.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: immutable_core
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "ZephyrAlpha 任务系统的全链路架构总览。声明任务系统的分层架构（schema→治理→施工→协议→代码）、各层的负责文件及跨层交叉引用。新 AI session 理解任务体系时，应首先读取本文件。v2.2.0：bootstrap-plans/ 废除，施工内容迁入 03_modules/l01_infrastructure/task-card-kms/blueprint.md，CP-TASK-CARD-KMS-001→MOD-INF-003。"
tags: [index, task, governance, navigation, architecture, construction-plan]
rule_form: declarative
depends_on:
  - target: PS-STD-001
    at: "§5.8 + §7"
    why: "metadata-registry.md 定义了 GOV-TASK 模块 ID 分配规则 + 任务卡字段 schema"
ai_autonomy: immutable_core
---

# 任务系统架构总览

> **module_id**: GOV-TASK-000 | **version**: 2.2.0 | **status**: active

---

## §1 任务系统的分层架构

ZephyrAlpha 的任务系统横跨 5 层：

```
┌──────────────────────────────────────────────────┐
│ 第 1 层：Schema（字段定义）                         │
│   meta/metadata-registry.md §7                    │
│   30 个任务卡字段的完整定义 + task_id 格式 + 枚举值     │
├──────────────────────────────────────────────────┤
│ 第 2 层：治理规则（怎么管）                           │
│   governance/task/   ← 你现在看的这个目录             │
│   ├── task-card-standard.md   操作指南：怎么写任务卡    │
│   ├── task-lifecycle-standard.md  治理规则：权限/优先级 │
│   └── task-closure-standard.md  关闭验证：残留清扫    │
├──────────────────────────────────────────────────┤
│ 第 3 层：施工计划（怎么做）                          │
│   03_modules/l01_infrastructure/                  │
│   └── task-card-kms/blueprint.md §5.2-§5.5       │
│       状态机实现 + G0-G6 门禁 + 超时升级 + 消费者      │
├──────────────────────────────────────────────────┤
│ 第 4 层：治理协议（跨域交叉）                          │
│   governance/ai/handoff-protocol.md               │
├──────────────────────────────────────────────────┤
│ 第 5 层：代码实现                                     │
│   src/zephyr/schemas.py (TaskCard 模型)             │
│   src/zephyr/db/task_repo.py (CRUD)                │
│   src/zephyr/gates/task_completion_gate.py (G5)    │
│   src/zephyr/mcp/task_manager_server.py             │
└──────────────────────────────────────────────────┘
```

---

## §2 本目录的责任（governance/task/）

`governance/task/` 是 ZephyrAlpha 的**任务治理中心**。这里管的是"任务卡怎么写、怎么被治理、怎么关闭"相关的规则。

**正向责任**（本目录管的事）：
1. 任务卡的正文结构规范（如何写"读→做→产→检"四步）
2. 任务生命周期的治理规则（谁有权取消/改优先级、P0 通胀保护、升级治理）
3. 任务关闭的验证标准和残留清扫

**负向责任**（本目录不管的事，去对应位置找）：
- 任务卡字段的权威定义 → `meta/metadata-registry.md` §7
- 状态机实现、门禁检查逻辑、超时检测代码 → `03_modules/l01_infrastructure/task-card-kms/blueprint.md` §5.2-§5.5
- Session 交接协议 → `governance/ai/handoff-protocol.md`

---

## §3 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [task-card-standard.md](../../governance/task/task-card-standard.md) | GOV-TASK-001 | 操作指南：正文结构 + 路径依赖速查 + 门禁参考 + 示例 |
| [task-lifecycle-standard.md](../../governance/task/task-lifecycle-standard.md) | GOV-TASK-004 | 治理规则：取消权限 + 优先级裁决 + P0 通胀保护 + 升级治理 |
| [task-closure-standard.md](../../governance/task/task-closure-standard.md) | GOV-TASK-005 | 关闭验证 5 项检查 + 残留文件清扫 |

**跨层文件**（不在本目录，但属于任务系统）：

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [task-card-kms/blueprint.md](../../../03_modules/l01_infrastructure/task-card-kms/blueprint.md) | MOD-INF-003 | 蓝图+施工：状态机实现 + G0-G6 门禁 + 超时升级 + 消费者 |

---

## §4 跨层依赖关系

```
metadata-registry.md §7 (PS-STD-001)
    │ 字段 schema（唯一真源）
    ▼
GOV-TASK-001 (task-card-standard)     ← 操作指南，管"怎么写"
    │
    ├── GOV-TASK-004 (lifecycle)      ← 治理规则，管"权限/优先级/升级"
    │       └── GOV-TASK-005 (closure) ← 关闭验证，管"怎么收尾"
    │
    ├── MOD-INF-003                   ← 蓝图+施工，管"怎么实现"
    │       （状态机 + G0-G6 + 超时升级 + 消费者）
    │
    ├── GOV-AI-008 (handoff)          ← Session 交接（在 ai/）
    │        关联：交接时更新任务状态
```

---

## §5 对 AI 的使用指引

每个新 AI session 理解任务体系时，按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解任务系统的五层架构
2. **再读 metadata-registry.md §7**——理解"每个字段叫什么、有什么约束"
3. **再读 task-card-standard.md**——理解"怎么填一张任务卡"
4. **按需读取** lifecycle（治理规则）/ closure（关闭验证）/ task-card-kms/blueprint.md §5.2-§5.5（施工实现）/ handoff（交接协议）

所有 governance/task/ 下文件均标记 `ai_autonomy: immutable_core`——AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

---

## §6 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.2.0 | 2026-05-02 | **bootstrap-plans 废除**：施工内容全部迁入 03_modules/l01_infrastructure/task-card-kms/blueprint.md §5.2-§5.5；CP-TASK-CARD-KMS-001→MOD-INF-003；所有交叉引用更新 |
| 2.1.0 | 2026-05-01 | **施工层拆分**：lifecycle-standard（GOV-TASK-004）施工内容迁移至 construction-plan-task-card-and-kms.md §2.5-§2.8。体系从 4 层升级为 5 层（新增"施工计划"层）。lifecycle-standard 精简为纯治理文件 |
| 2.0.0 | 2026-05-01 | **A 方案重整**：handoff-protocol.md → governance/ai/（GOV-AI-008）；drafts-audits-arbitration-protocol.md 废除。本文件从"目录索引"升级为"任务系统架构总览" |
| 1.0.0 | 2026-05-01 | 初始版本（目录索引） |
