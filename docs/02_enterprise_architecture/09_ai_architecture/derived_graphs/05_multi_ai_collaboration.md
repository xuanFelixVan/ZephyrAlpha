---
ttl: permanent
doc_type: architecture_view
title: 多 AI 协作时序图（单 AI 多会话 + 人调度 + 落盘交接）
owner: ZephyrAlpha-Owner
language: zh
status: generated
version: "0.1.0"
date: 2026-08-30
topic: multi_ai_collaboration
scope: 09_ai_architecture/derived_graphs
---

# 05 · 多 AI 协作时序图（单 AI 多会话 + 人调度 + 落盘交接）

> **派生图声明**：本文是**视图不是真源**。生成时间 2026-08-29T23:47Z（本地 2026-08-30 07:47，UTC+8）；生成方式=aiarch 3.9 一次性批生成。若与真源漂移，以真源为准并重生成本文。
>
> **源真源**：[08_multi_ai_concurrency_governance.md](../implementation_plans/08_multi_ai_concurrency_governance.md) §2.3/§3.1/§3.3（约束与协作形态设计）+ 61 号备忘 §2.3/§3.6 裁定（不做 agent 编排系统；AI 间不直接通信，交接靠文档落盘）+ 65 号备忘 §11.2.1（worktree 合并人工裁决）。

```mermaid
sequenceDiagram
    autonumber
    participant O as Owner（人调度）
    participant SA as AI 会话 A（worktree A）
    participant SB as AI 会话 B（worktree B）
    participant D as 落盘交接文档（docs/.runtime 交接件）
    participant Q as 提交队列（串行化）
    participant G as git 安全三层（预防→检测→恢复）

    O->>SA: 派单任务卡 A（物理隔离 worktree）
    O->>SB: 派单任务卡 B（物理隔离 worktree）
    Note over SA,SB: AI 间不直接通信（61 号 §3.6）
    SA->>D: 完工落盘交接（进度/决策/待办）
    SB->>D: 完工落盘交接
    O->>D: 读取交接，裁决下一步
    SA->>Q: 提交入队（串行化）
    SB->>Q: 提交入队
    Q->>G: 门禁校验（AI 施工门禁/漂移检测）
    G-->>O: 违规上报告警
    O->>O: worktree 合并人工显式确认（65 号 §11.2.1）
```

## 既定口径（真源摘录）

- **协作形态**：人调度多会话，**非 agent 自治编排**（61 号 §2.3 已裁定不做 agent 编排系统）；AI 间不直接通信，交接靠文档落盘（61 号 §3.6）。
- **会话隔离**：worktree 物理隔离；merge 必须用户显式确认——物理隔离 + 人工裁决合并正好匹配「人调度」模式，不需要自动合并 agent（08 号文 §3.1）。
- **并发安全**：提交队列串行化机制与冲突解决（08 号文 §3.3）；git 安全预防→检测→恢复三层闭环（§3.2）。
- **人力约束**：1 人全栈 + AI 协作者，无团队（08 号文 §2.3）。
