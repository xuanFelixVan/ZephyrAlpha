---
module_id: GOV-AI-008
title: Session Handoff Protocol（会话交接协议）
doc_type: protocol
status: active
version: "2.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "AI Session 结束时必须产出的 HandoffPackage 格式规范。定义 8 个必填字段——对标 Agile Standup + ITIL 变更记录 + DevOps On-Call Shift Handoff。v2.0.0：压缩——砍掉实现细节、自评报告、冗余 JSON 克隆品（原 300 行→80 行）。"
note: "2026-05-01 从 governance/task/（GOV-TASK-003）迁入。"
tags: [handoff, protocol, session, governance, ai]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: immutable_core
depends_on:
  - target: PS-STD-001
    at: "§7.2"
    why: "metadata-registry.md 定义的 task_id 格式（{NAMESPACE}-{SEQ}）为本协议的 task_id 引用格式基准"
related_kb_ref: [ADR-0041]
---

# Session Handoff Protocol（会话交接协议）

> 对标：Agile Daily Standup 三问 + ITIL Change Enablement 变更记录 + DevOps Shift Handoff 模板

每个 AI Session 结束时必须生成一份 HandoffPackage（YAML），包含以下 8 个字段。**删任一字段视为非法交接**。

---

## §1 HandoffPackage 8 必填字段

| # | 字段 | 类型 | 说明 | 对标 | 示例 |
|---|------|------|------|------|------|
| 1 | `session_id` | string | Session 唯一标识 | ITIL：变更记录 ID | `session-20260424-001` |
| 2 | `completed_tasks` | string[] | 已完成的 task_id 列表 | Agile："我昨天完成了什么" | `["SRC-010", "ADR-007"]` |
| 3 | `in_progress_tasks` | string[] | 未闭环的任务 ID 列表 | Agile："我正在做什么" | `["SRC-013"]` |
| 4 | `blocked_items` | list[{task_id, reason}] | 阻塞项 + 原因 | Agile："有什么阻塞我" | `{task_id: SRC-018, reason: "依赖 SRC-013"}` |
| 5 | `decisions_made` | list[{topic, decision, rationale}] | 关键决策 + 理由 | Michael Nygard ADR 模式 | `{topic: "选型", decision: "SQLite", rationale: "零依赖"}` |
| 6 | `next_actions` | list[{task_id, priority}] | 下一 session 优先执行 | DevOps："下一步行动" | `{task_id: SRC-013, priority: P0}` |
| 7 | `context_summary` | string | 自然语言摘要（≤500 字） | ITIL：变更摘要 | 本 session 完成了 A、遇到 B 问题、建议下一步做 C |
| 8 | `open_questions` | string[] | 向 Owner 暴露的未解问题 | ITIL：未决风险记录 | `["是否需要 schema 校验？"]` |

### 字段补充说明

**in_progress_tasks** 必须附带离开时的上下文——当前执行到哪个步骤、已完成的部分产出物路径、下一 Session 接手的第一个动作。

**decisions_made** 中的 rationale（理由）是必填项——没有理由的决策在下一个 Session 看来就是独裁，无法被继承或质疑。

**next_actions** 至少 1 项。下一 Session 启动后第一件事应按此表直接开始，而非自行探索该做什么。

---

## §2 文件命名与存放

```
docs/09_audit/HANDOFF/session-YYYYMMDD-NNN.yaml
```

- YYYYMMDD：Session 启动日期
- NNN：当日序号（001 起，三位数字）
- 编码：UTF-8，换行符 LF

---

## §3 YAML 模板（直接复制填写）

```yaml
session_id: session-YYYYMMDD-NNN
completed_tasks:
  - XXX-NNN
in_progress_tasks:
  - task_id: XXX-NNN
    step: 当前执行到哪一步
    partial_deliverables: [部分产出物路径]
    next_step: 接手后第一个动作
blocked_items:
  - task_id: XXX-NNN
    reason: 一句话原因
decisions_made:
  - topic: 主题
    decision: 决策
    rationale: 理由
next_actions:
  - task_id: XXX-NNN
    priority: P0
context_summary: ≤500 字的自然语言摘要
open_questions: []
```

---

## §4 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-05-01 | **压缩**：移除 R-编号体系、Pydantic 实现细节、SessionCarryover JSON（与 YAML 重复）、自评报告、pre-commit 配置示例；保留 8 字段核心规则（对标 Agile/ITIL/DevOps）。从 governance/task/ 迁入 |
| 1.0.0 | 2026-04-27 | 初始版本（300 行，含实现细节和自评报告） |
