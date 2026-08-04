---
doc_type: audit_report
title: 候选模块清单 — D_GOV_RULE
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_GOV_RULE 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **1** 条（原有 1 + harvest 0）。

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 一问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-PC-001 | Policy Compiler / 策略编译器 | 策略规则到检查器代码的翻译需自动化,避免手工编写检查器 | D_GOV_RULE | 否决（rejected） | 一问通过 | P2 | 规则数量爆炸且频繁变更,人工编写检查器成本高 等2条 | 2027-07-31 |

## 按一问卡点分组（为什么没开发）

> 一问标准（裁定 2026-08-04）：仅 q1 已实现/重复。q1「是」即不进 depgraph 设计态，登记在候选库。原 q2/q3/q4 灰度已废。

### 一问通过（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-PC-001 | Policy Compiler / 策略编译器 | 策略规则到检查器代码的翻译需自动化,避免手工编写检查器 | D_GOV_RULE | rejected,q4 AI替代。除非 TRAE AI 翻译能力显著退化,否则不再评估 | 依赖 TRAE AI 运行时做规则→检查器翻译。代价:无固化产物,但 AI 翻译足够可靠 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过一问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2027-07-31 | yearly | CAND-PC-001 | Policy Compiler / 策略编译器 | D_GOV_RULE | 否决（rejected） | rejected,q4 AI替代。除非 TRAE AI 翻译能力显著退化,否则不再评估 |
