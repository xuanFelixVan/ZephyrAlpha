---
doc_type: architecture_view
title: 数据流图（dataflowgraph）索引
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 数据流图（dataflowgraph）索引

> 生成时间: 2026-08-03T21:21:09
> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表（ARCH-051）
> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）

## 这是什么？大白话讲数据流图

这份"数据流图索引"背后是一张**数据流图（dataflowgraph）**。在往下看清单之前，先用大白话讲清楚它是什么、有什么用、为什么要看。

### 一、数据流是什么意思？

一个作业把数据"吃进来、加工、吐出去"，吐出来的又被下一个作业吃掉，这条流向就叫**数据流**。
比如：`下载行情`作业把日线写进库 → `算因子`作业读这些日线算出因子 → `回测`作业读这些因子做回测。数据就这样一路流下去。

把项目里所有这种"数据从哪流到哪"的关系记下来，就是**数据流**。

### 二、数据流图是什么？

把项目里**所有数据**（叫 Dataset）和**所有作业**（叫 Job）当成点，把"谁产出谁、谁消费谁"当成连线，画成一张大网，就是数据流图。

- 它不是一张图片，是存在数据库（`depgraph`）里的一张表
- 两个基本元件：**Dataset**（数据集，被加工的数据）和 **Job**（作业，加工数据的动作）
- 连线方向：Job 产出 → Dataset → 被另一个 Job 消费 → 再产出新 Dataset……

### 三、数据流图有什么用？它和依赖图啥关系？

这个项目有三张正交的全景图，各管一摊：

| 全景图 | 管什么 | 举个例子 |
|---|---|---|
| 依赖图 depgraph | 模块**谁依赖谁**（静态） | 因子模块 import 了数据模块 |
| **数据流图 dataflowgraph** | **数据从哪流到哪**（动态） | 行情数据 → 因子 → 回测 |
| 决策流图 decisiongraph | 决策怎么产生（动态） | 信号 → 风控 → 下单 |

**为什么要看数据流图**：看数据血缘（某数据被谁产出、又被谁消费）、找断点（该产出的作业没产出）、排查"数据从哪来"（回测用的因子是哪个作业算的）。

**一句话**：依赖图管"模块关系"，数据流图管"数据流向"——一个看代码结构，一个看数据走向。

### 四、这份索引主要看什么？

1. **有多少数据流** —— 看"统计"表里的 Job / Dataset 数量
2. **数据流长啥样** —— 点进 [dataflow_panorama.md](dataflow_panorama.md) 看全项目数据流全景图（运营态+设计态）
3. **按域拆分的数据流** —— 下面表格按功能域列出每个域的数据流文档

> 运营态 = 实际在跑的数据流；设计态 = 还在图纸上没动工的数据流。

---

## 统计

| 类型 | 运营态 (production) | 设计态 (design) | 合计 |
|------|:---:|:---:|:---:|
| Dataset | 25 | 51 | 76 |
| Job | 24 | 51 | 75 |
| Edge | 39 | 51 | 90 |

## 数据流全景（运营态 + 设计态）

> 75 个作业 / 76 个数据集 / 90 条边（含设计态 51 jobs / 51 datasets）

- [dataflow_panorama.md](dataflow_panorama.md) — 全项目数据流全景图（运营态+设计态）+ Dataset/Job 清单
- [可缩放 HTML 版](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/dataflow_panorama.html) — 浏览器打开可 Ctrl+滚轮缩放

## 数据流（按域拆分，含三视图）

> 75 个作业 / 76 个数据集 / 90 条边，按功能域拆分（每个域文档含三视图：全景图 → 运营态的图 → 设计态的图）：

| 文件 | 功能域 | Job 数 | Dataset 数 | 可缩放 HTML |
|------|--------|:---:|:---:|:---:|
| [d_factor_ashare.md](d_factor_ashare.md) | 因子域-A股因子计算 | 14 | 14 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_factor_ashare.html) |
| [d_factor_analysis.md](d_factor_analysis.md) | 因子域-因子分析 | 12 | 12 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_factor_analysis.html) |
| [d_factor_barra_mine.md](d_factor_barra_mine.md) | 因子域-Barra风险模型与因子挖掘 | 6 | 6 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_factor_barra_mine.html) |
| [d_backtest.md](d_backtest.md) | 回测域-回测服务 | 13 | 13 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_backtest.html) |
| [d_data.md](d_data.md) | 数据域-数据采集管理 | 5 | 5 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_data.html) |
| [d_data_eng.md](d_data_eng.md) | 数据工程域-数据工程服务 | 5 | 5 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_data_eng.html) |
| [d_ex_pf_core.md](d_ex_pf_core.md) | 执行核心+组合核心域 | 10 | 11 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_ex_pf_core.html) |
| [d_others.md](d_others.md) | 其他域-ML训练+风控+交易 | 5 | 5 | [HTML](http://localhost:8765/docs/02_enterprise_architecture/05_dataflow_architecture/_zoomable_html/d_others.html) |

## 概述

数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖）
- dataflowgraph 表达"数据从哪流到哪"（数据流向）
- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联

> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。

