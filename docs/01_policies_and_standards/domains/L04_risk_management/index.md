---
classification: confidential
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
layer: L04
merged_from: README.md + index.md
module_id: DOM-L04-000
status: active
title: L04 风控管理层域层入口
---

# L04 — 风控管理层（Risk Management）

> 负责交易风险的量化约束与自动化执行——仓位限额、止损规则、敞口管理。本域是 ZephyrAlpha 的风险防线。

## 责任声明（Single Responsibility）

本目录只存放：**L04 风控层 — 风险限额策略/止损配置**。

## 文件清单

| 文件 | 说明 |
|------|------|

## 管什么（In Scope）

- 仓位限额（单品种上限、总敞口上限、杠杆倍率）
- 止损规则（固定止损、追踪止损、时间止损）
- 风控触发动作（硬止损→平仓 / 软止损→告警+人工审批）
- 例外审批流程

## 不管什么（Out of Scope）

- 市场风险建模（VaR/CVaR）→ 属于研究层
- 合规性审查 → `../../governance/compliance/`
- 盘后风控绩效归因 → L07 盘后分析层

## 依赖关系

| 方向 | 域层 | 关系 | 传输内容 |
|------|------|------|---------|
| 上游 | L00 数据源层 | 输入 | 持仓/保证金/账户数据 |
| 上游 | L02 因子层 | 输入 | 因子信号 |
| 下游 | L06 交易执行 | 输出 | 风控指令（止损触发/仓位限制） |
| 下游 | L07 盘后分析 | 输出 | 风控事件日志 |

## 本域文件

| 文件 | 类型 | 说明 |
|------|------|------|
| [governance/risk-limits-policy.md](governance/risk-limits-policy.md) | 治理规则 | 仓位/止损/敞口限制——限额类型、计算方法、触发动作、例外审批 |
| [operational/stop-loss-config-runbook.md](operational/stop-loss-config-runbook.md) | 操作手册 | 配置止损规则的完整操作步骤——参数验证、回测确认、上线监控 |

## 引用的跨域规则

- [audit-trail-policy.md](../../governance/compliance/audit-trail-policy.md) — 风控决策审计追踪
- [data-quality-policy.md](../../governance/data/data-quality-policy.md) — 风控输入数据质量

## 排除规则（不应放入本目录的内容）

- ❌ 全局规则 → `01_policies_and_standards/governance/`

## 父级目录

- 父级：[domains](../../domains/index.md)
