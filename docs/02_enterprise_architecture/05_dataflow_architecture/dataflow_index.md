---
doc_type: architecture_view
title: 数据流图（dataflowgraph）索引
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 数据流图（dataflowgraph）索引

> 生成时间: 2026-07-31T13:22:51
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表（ARCH-051）
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

## 统计

| 类型 | 运营态 (production) | 设计态 (design) | 合计 |
|------|:---:|:---:|:---:|
| Dataset | 14 | 62 | 76 |
| Job | 13 | 62 | 75 |
| Edge | 28 | 62 | 90 |

## 运营态数据流（已实现）

> 13 个作业 / 14 个数据集 / 28 条边

- [dataflow_production.md](dataflow_production.md) — 运营态全景图 + Dataset/Job 清单

## 设计态数据流（按域拆分）

> 62 个作业 / 62 个数据集 / 62 条边，按功能域拆分为多个文件：

| 文件 | 功能域 | Job 数 | Dataset 数 |
|------|--------|:---:|:---:|
| [d_factor_ashare.md](d_factor_ashare.md) | 因子域-A股因子计算（设计态） | 14 | 14 |
| [d_factor_analysis.md](d_factor_analysis.md) | 因子域-因子分析（设计态） | 12 | 12 |
| [d_factor_barra_mine.md](d_factor_barra_mine.md) | 因子域-Barra风险模型与因子挖掘（设计态） | 6 | 6 |
| [d_backtest.md](d_backtest.md) | 回测域-回测服务（设计态） | 8 | 8 |
| [d_data.md](d_data.md) | 数据域-数据采集管理（设计态） | 5 | 5 |
| [d_data_eng.md](d_data_eng.md) | 数据工程域-数据工程服务（设计态） | 5 | 5 |
| [d_ex_pf_core.md](d_ex_pf_core.md) | 执行核心+组合核心域（设计态） | 8 | 8 |
| [d_others.md](d_others.md) | 其他域-ML训练+风控+交易（设计态） | 4 | 4 |

## 概述

数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖）
- dataflowgraph 表达"数据从哪流到哪"（数据流向）
- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联

> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。

