---
doc_type: audit_report
title: 候选模块清单 — D_SIGLEGACY
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_SIGLEGACY 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **1** 条（原有 1 + harvest 0）。

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-SIGLEGACY-001 | D_SIGLEGACY 多策略引擎 | (已解决)多策略编排已由 D_PF_CORE PC-01 承担 | D_SIGLEGACY | 否决（rejected） | 一问通过 | P2 | — | 2027-07-31 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 一问通过（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-SIGLEGACY-001 | D_SIGLEGACY 多策略引擎 | (已解决)多策略编排已由 D_PF_CORE PC-01 承担 | D_SIGLEGACY | rejected,确认死域。除非D_PF_CORE多策略出现重大缺口,否则不再评估 | 已由 D_PF_CORE MOD-L05-001 承担 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2027-07-31 | yearly | CAND-SIGLEGACY-001 | D_SIGLEGACY 多策略引擎 | D_SIGLEGACY | 否决（rejected） | rejected,确认死域。除非D_PF_CORE多策略出现重大缺口,否则不再评估 |
