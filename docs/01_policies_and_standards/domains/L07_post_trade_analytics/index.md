---
classification: confidential
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
layer: l07_post_trade_analytics
merged_from: README.md + index.md
module_id: DOM-L07-000
status: active
title: L07 盘后分析层域层入口
---

# L07 — 盘后分析层（Post-Trade Analytics）

> 负责盘后报告生成、交易分析与绩效归因。本域将交易数据转化为可决策的分析洞察。

## 责任声明（Single Responsibility）

本目录只存放：**L07 归因分析层 — 盘后报告策略/分析流水线**。

## 文件清单

| 文件 | 说明 |
|------|------|

## 管什么（In Scope）

- 盘后报告产出（日报/周报/月报的类型、时限、质量标准）
- 交易分析（成交质量、滑点评估、冲击成本）
- 绩效归因（因子收益分解、择时/选股贡献拆分）
- 报告分发规则

## 不管什么（Out of Scope）

- 实时风控监控 → L04 风控管理层
- 交易执行优化 → L06 交易执行层
- 原始数据清洗 → L00 数据源层

## 依赖关系

| 方向 | 域层 | 关系 | 传输内容 |
|------|------|------|---------|
| 上游 | L00 数据源层 | 输入 | 交易日志/成交记录 |
| 上游 | L04 风控层 | 输入 | 风控事件日志 |

## 本域文件

| 文件 | 类型 | 说明 |
|------|------|------|
| [governance/post-trade-reporting-policy.md](governance/post-trade-reporting-policy.md) | 治理规则 | 盘后必须产出的报告类型、产出时限、质量标准与分发规则 |
| [operational/analytics-pipeline-runbook.md](operational/analytics-pipeline-runbook.md) | 操作手册 | 运行盘后分析管线的完整操作步骤——数据依赖、异常处理、报告生成 |

## 引用的跨域规则

- [audit-trail-policy.md](../../governance/compliance/audit-trail-policy.md) — 盘后报告审计追溯
- [data-retention-policy.md](../../governance/data/data-retention-policy.md) — 历史分析数据保留

## 排除规则（不应放入本目录的内容）

- ❌ 全局规则 → `01_policies_and_standards/governance/`

## 父级目录

- 父级：[domains](../../domains/index.md)
