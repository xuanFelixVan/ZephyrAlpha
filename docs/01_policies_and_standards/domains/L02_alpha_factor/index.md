---
classification: confidential
date: '2026-05-04'
doc_type: index
generated: '2026-05-02'
layer: L02
merged_from: README.md + index.md
module_id: DOM-L02-IDX
status: active
version: "1.0.1"
title: L02 Alpha 因子层域层入口
---

# L02 — Alpha 因子层（Alpha Factor）

> 负责 Alpha 因子的质量门禁、上线流程与生命周期管理。本域确保所有进入生产环境的因子满足最低质量标准。

## 责任声明（Single Responsibility）

本目录只存放：**L02 因子层 — 因子质量门禁/因子上线流程**。

## 文件清单

| 文件 | 说明 |
|------|------|

## 管什么（In Scope）

- 因子质量门禁（最小夏普比率、最大回撤、IC 阈值、衰减检测）
- 因子上线流程（回测验证、灰度发布、监控配置）
- 因子生命周期管理（激活→衰减检测→退役）

## 不管什么（Out of Scope）

- 因子信号的生成与计算 → `../../domains/L03_signal_generation/`
- 因子组合与权重优化 → `../../domains/L05_portfolio_construction/`
- 因子数据的底层存储 → `../../governance/data/`

## 依赖关系

| 方向 | 域层 | 关系 | 传输内容 |
|------|------|------|---------|
| 上游 | L00 数据源层 | 输入 | 标准化行情/交易数据 |
| 下游 | L04 风控层 | 输出 | 因子信号 |
| 下游 | L05 组合构建 | 输出 | 有效因子集 + 因子表现指标 |

## 本域文件

| 文件 | 类型 | 说明 |
|------|------|------|
| [governance/factor-quality-policy.md](governance/factor-quality-policy.md) | 治理规则 | 因子必须满足的质量标准——最小夏普比率、最大回撤、IC 阈值、衰减检测 |
| [operational/factor-onboarding-runbook.md](operational/factor-onboarding-runbook.md) | 操作手册 | 上线新因子的完整操作步骤——回测验证、灰度发布、监控配置 |

## 引用的跨域规则

- [data-quality-policy.md](../../governance/data/data-quality-policy.md) — 数据质量标准
- [data-lineage-policy.md](../../governance/data/data-lineage-policy.md) — 因子计算数据血缘

## 排除规则（不应放入本目录的内容）

- ❌ 全局规则 → `01_policies_and_standards/governance/`

## 父级目录

- 父级：[domains](../../domains/index.md)
