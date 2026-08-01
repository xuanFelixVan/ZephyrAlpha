---
doc_type: audit_report
title: 候选模块清单 — D_BACKTEST
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_BACKTEST 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **3** 条（原有 2 + harvest 1）。
> harvest 去重四态: likely_implemented=1

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-4121 | Backtest Pipeline Process 回测管线进程 | A1迁移概念级进程P1 V1-V6验证Walk-Forward策略A/B淘汰可重启 | D_BACKTEST | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-BT-001 | Backtest v2.0 Auxiliary Modules / 回测v2.0辅助模块 | 回测的四个辅助工具：批量调度、衰减监控、自动报告、结果缓存。现在回测是手动单策略，等要批量跑、自动出报告时再开发。 | D_BACKTEST | 延后（deferred） | q2 无需求驱动 | P2 | 回测需批量调度多策略(当前单策略) 等4条 | 2027-07-31 |
| CAND-WFO-001 | Walk-Forward Optimizer / 滚动前进优化器 | 回测调参时用一段历史调、下一段验证，像考试一样滚动检验，防止参数只在历史上好看、实盘就拉胯。等真出现过拟合再说。 | D_BACKTEST | 延后（deferred） | q2 无需求驱动 | P2 | 实盘策略表现与回测显著背离(过拟合迹象) 等3条 | 2027-01-31 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### q2 无需求驱动（2 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-BT-001 | Backtest v2.0 Auxiliary Modules / 回测v2.0辅助模块 | 回测的四个辅助工具：批量调度、衰减监控、自动报告、结果缓存。现在回测是手动单策略，等要批量跑、自动出报告时再开发。 | D_BACKTEST | 首次登记,待回测需批量调度/自动报告时重新评估 | 当前手动单策略回测。代价:无批量调度/自动报告/衰减监控 |
| CAND-WFO-001 | Walk-Forward Optimizer / 滚动前进优化器 | 回测调参时用一段历史调、下一段验证，像考试一样滚动检验，防止参数只在历史上好看、实盘就拉胯。等真出现过拟合再说。 | D_BACKTEST | 首次登记,待实盘出现过拟合迹象或 D_BACKTEST Phase2 启动时重新评估 | 靠 D_BACKTEST 基础回测 + 人工参数审查。代价:过拟合风险不可量化 |

### 待评估（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-4121 | Backtest Pipeline Process 回测管线进程 | A1迁移概念级进程P1 V1-V6验证Walk-Forward策略A/B淘汰可重启 | D_BACKTEST | harvest待评估（likely_implemented） |  |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-HARVEST-4121 | Backtest Pipeline Process 回测管线进程 | D_BACKTEST | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2027-01-31 | half_yearly | CAND-WFO-001 | Walk-Forward Optimizer / 滚动前进优化器 | D_BACKTEST | 延后（deferred） | 首次登记,待实盘出现过拟合迹象或 D_BACKTEST Phase2 启动时重新评估 |
| 2027-07-31 | yearly | CAND-BT-001 | Backtest v2.0 Auxiliary Modules / 回测v2.0辅助模块 | D_BACKTEST | 延后（deferred） | 首次登记,待回测需批量调度/自动报告时重新评估 |
