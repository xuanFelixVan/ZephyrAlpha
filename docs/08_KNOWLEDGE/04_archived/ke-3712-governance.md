---
module_id: KE-3565
title: 3.2 四条核心接口
category: governance
---

# 3.2 四条核心接口

3.2 四条核心接口

> **📊 D2-B 闭环接口图**：见 [`diagrams/governance_d2b_loop.mmd`](diagrams/governance_d2b_loop.mmd)

| 接口 | 触发时机 | 协议 | 当前状态 |
|---|---|---|---|
| **① Policy→Factory** | Policy 规则新增/变更（git commit） | policy_compiler：Markdown/YAML → 检查器配置 | 手动（Sprint 10/11 自动化） |
| **② Factory→Runtime** | git commit / CI push / 交易执行 / AI 决策 | pre-commit hook / GitHub Actions / 函数调用 | L3 三件套就位（Sprint 9） |
| **③ Runtime→Audit** | 每次检查器执行后 | append-only 写入 `policy_decision_ledger.jsonl`（OQ-063 §4.3 28 字段） | Sprint 10 |
| **④ Audit→Policy** | 定期（周/月）+ 事件驱动 | `feedback_to_policy.py` 聚合 → PR 提案 | Sprint 10/11 |
