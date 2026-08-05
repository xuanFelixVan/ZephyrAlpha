---
doc_type: architecture_view
title: 决策流图（decisiongraph）索引
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 决策流图（decisiongraph）索引

> 生成时间: 2026-08-03T19:13:48
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | 主索引

## 这是什么？大白话讲决策流图

这份"决策流图索引"背后是一张**决策流图（decisiongraph）**。在往下看清单之前，先用大白话讲清楚它是什么、有什么用、为什么要看。

### 一、决策流是什么意思？

一笔交易要一步步做决定：先产生信号 → 再做风控检查 → 再决定买什么买多少 → 再下单 → 最后执行。这条"决策一步步怎么往下走"的链路，就叫**决策流**。

把项目里所有这种"决策怎么产生、怎么往下传"的关系记下来，就是**决策流**。

### 二、决策流图是什么？

把决策链上的**每一步**当成点，把"前一步触发后一步"当成连线，画成一张大网，就是决策流图。

- 它不是一张图片，是存在数据库（`depgraph`）里的一张表
- 四个基本元件：
  - **Track（轨）** —— 决策走哪条道（模型驱动 / 数据驱动 / 人工指令 / 应急保命）
  - **Layer（层）** —— 决策链的第几步（L0 信号 → … → L6 反馈）
  - **Node（节点）** —— 每一步具体做什么的决策点
  - **Edge（边）** —— 上下步之间怎么触发、怎么传

### 三、决策流图有什么用？它和依赖图啥关系？

这个项目有三张正交的全景图，各管一摊：

| 全景图 | 管什么 | 举个例子 |
|---|---|---|
| 依赖图 depgraph | 模块**谁依赖谁**（静态） | 风控模块 import 了因子模块 |
| 数据流图 dataflowgraph | 数据从哪流到哪（动态） | 行情数据 → 因子 → 回测 |
| **决策流图 decisiongraph** | **决策怎么产生**（动态） | 信号 → 风控 → 下单 → 执行 |

**为什么要看决策流图**：看决策链（一笔交易从信号到执行经过哪些步）、找断点（该有的风控检查有没有）、排查"这个决定是谁做的"（某个下单是模型驱动还是人工指令，走哪条轨）。

**一句话**：依赖图管"模块关系"，决策流图管"决策走向"——一个看代码结构，一个看决策逻辑。

### 四、这份索引主要看什么？

1. **决策链有几条轨** —— 看"Track 导航"表，5 条轨各有分工
2. **决策链长啥样** —— 点进各 Track 文档看 Mermaid 图
3. **每一步是什么** —— 看 Layer / Node 清单，知道决策链上每步具体做什么

> 运营态 = 实际代码已实现的决策步；设计态 = 还在图纸上没动工的决策步。

---

## 概述

决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。
- depgraph 表达"谁依赖谁"（模块依赖，静态）
- dataflowgraph 表达"数据从哪流到哪"（数据流向，动态）
- decisiongraph 表达"决策如何产生"（决策流，动态）
- 三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）

> 本索引为纯导航枢纽。各 Track / 功能域 / 辅助图分别独立成文件，避免单文件过大无法阅读。

## 统计

| 类型 | 数量 |
|------|------|
| Track（轨） | 5 |
| Layer（层） | 960 |
| Node（节点） | 213 |
| Edge（边） | 211 |
| 运营态 Layer（design_maturity=production） | 798 |
| 设计态 Layer（design_maturity=design） | 162 |
| 运营态 Node（design_maturity=production） | 0 |
| 设计态 Node（design_maturity=design） | 213 |

> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。对标 depgraph 的设计态/运营态机制。

## Track 导航（按优先级）

| 序号 | track_id | 名称 | 优先级 | Layer 数 | Node 数 | [📄 文档](.) |
|------|----------|------|--------|----------|---------|------|
| 01 | model_driven | 模型驱动轨 | 1 | 10 | 213 | [📄 01_decision_track_model_driven.md](01_decision_track_model_driven.md) |
| 02 | data_driven | 数据驱动轨 | 2 | 0 | 0 | [📄 02_decision_track_data_driven.md](02_decision_track_data_driven.md) |
| 03 | human_override | 人工指令轨 | 3 | 0 | 0 | [📄 03_decision_track_human_override.md](03_decision_track_human_override.md) |
| 04 | emergency | 应急保命轨 | 4 | 0 | 0 | [📄 04_decision_track_emergency.md](04_decision_track_emergency.md) |
| 99 | placeholder | 占位轨 | 99 | 950 | 0 | [📄 99_decision_track_placeholder.md](99_decision_track_placeholder.md) |

## L2A 信号层 · 功能域导航（7 域）

| 序号 | 功能域 | Node 数 | [📄 文档](.) |
|------|--------|---------|------|
| 06 | data | 3 | [📄 06_decision_l2a_data.md](06_decision_l2a_data.md) |
| 07 | factor | 2 | [📄 07_decision_l2a_factor.md](07_decision_l2a_factor.md) |
| 08 | frontend | 6 | [📄 08_decision_l2a_frontend.md](08_decision_l2a_frontend.md) |
| 09 | research | 6 | [📄 09_decision_l2a_research.md](09_decision_l2a_research.md) |
| 10 | sell | 19 | [📄 10_decision_l2a_sell.md](10_decision_l2a_sell.md) |
| 11 | signal | 13 | [📄 11_decision_l2a_signal.md](11_decision_l2a_signal.md) |
| 12 | simulation | 15 | [📄 12_decision_l2a_simulation.md](12_decision_l2a_simulation.md) |

## L3 策略组合层 · 功能域导航（7 域）

| 序号 | 功能域 | Node 数 | [📄 文档](.) |
|------|--------|---------|------|
| 13 | aut_core | 11 | [📄 13_decision_l3_aut_core.md](13_decision_l3_aut_core.md) |
| 14 | ex_core | 9 | [📄 14_decision_l3_ex_core.md](14_decision_l3_ex_core.md) |
| 15 | ex_sor | 5 | [📄 15_decision_l3_ex_sor.md](15_decision_l3_ex_sor.md) |
| 16 | pf_alloc | 6 | [📄 16_decision_l3_pf_alloc.md](16_decision_l3_pf_alloc.md) |
| 17 | pf_core | 12 | [📄 17_decision_l3_pf_core.md](17_decision_l3_pf_core.md) |
| 18 | position | 19 | [📄 18_decision_l3_position.md](18_decision_l3_position.md) |
| 19 | trading | 11 | [📄 19_decision_l3_trading.md](19_decision_l3_trading.md) |

## 辅助图

- [📄 20_decision_layers.md](20_decision_layers.md) — 层级详情图（L0-L6 卡片 + 流向）
- [📄 21_decision_invariants.md](21_decision_invariants.md) — 不变量图（6 节点类型 + 5 承重墙不变量）

## 旧锚点重定向

原单文件 `decision_index.md` 的各 section 已拆分到对应文件，外部 wiki 链接请按下方映射更新：

- `#全景图` / `#运营态全景图` / `#设计态全景图` → 见各 [Track 文件](#track-导航按优先级)
- `#层级详情图` → [20_decision_layers.md](20_decision_layers.md)
- `#不变量图` → [21_decision_invariants.md](21_decision_invariants.md)
- `#track-清单` → 上方 Track 导航表
- `#layer-清单` → 各 Track 文件内的 Layer 清单 section
- `#node-清单` → 各 Track / 功能域文件内的 Node 清单 section
- `#edge-清单` → 各 Track 文件内的 Edge 清单 section

