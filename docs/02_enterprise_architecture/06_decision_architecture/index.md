---
module_id: ARCH-VIEW-006
title: "决策流架构（decisiongraph）"
doc_type: architecture_view
status: active
version: 2.0.0
date: '2026-07-06'
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 决策流架构（decisiongraph）

> **本目录是决策流图的入口索引**。自动生成的 Mermaid 图表 + Markdown 文档位于 `generated/decisions/`。
> 三图正交声明见 [AGENTS.md §11](../../../AGENTS.md)。

## 概述

决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图，管理 L0-L6 交易决策链。

| 全景图 | 维度 | 表达 | 文档位置 |
|--------|------|------|----------|
| depgraph | 模块依赖 | "谁依赖谁"（静态） | `02_domain_architecture_docs/` + `generated/domains/` |
| dataflowgraph | 数据流 | "数据从哪流到哪"（动态） | `05_dataflow_architecture/` + `generated/dataflows/` |
| **decisiongraph** | **决策流** | **"决策如何产生"（动态）** | **`06_decision_architecture/` + `generated/decisions/`** |

三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）。

## 自动生成文档（generated/decisions/）

> **禁止手工编辑**——以下文档由 `generate_decision_diagram.py` 从 PostgreSQL `decision_*` 表 + `decision_graph_model.yaml` 自动生成。
> 真源：`decision_graph_model.yaml`（YAML 真源）→ `decision_*` 表（DB 缓存）→ 本目录（派生文档）。

| 文档 | 内容 |
|------|------|
| [decision_index.md](../generated/decisions/decision_index.md) | 索引（统计 + Track/Layer/Node/Edge 清单） |
| [decision_overview.mmd](../generated/decisions/decision_overview.mmd) | 全景图（L0-L6 层级 + 四轨并行） |
| [decision_layers.mmd](../generated/decisions/decision_layers.mmd) | 层级详情图（10 层卡片 + 频率/状态） |
| [decision_invariants.mmd](../generated/decisions/decision_invariants.mmd) | 不变量图（6 节点类型 + 5 承重墙不变量） |

## 生成器

- **脚本**：[`scripts/governance/d5_architecture/generators/generate_decision_diagram.py`](../../../scripts/governance/d5_architecture/generators/generate_decision_diagram.py)
- **触发**：手动运行（`python scripts/governance/d5_architecture/generators/generate_decision_diagram.py`）
- **数据源**：PostgreSQL `decision_tracks` / `decision_layers` / `decision_nodes` / `decision_edges` 表 + `decision_graph_model.yaml`（invariants 真源）
- **输出**：`docs/02_enterprise_architecture/generated/decisions/`（4 份文档）

## 四轨架构（Four Tracks）

| 轨 | 名称 | 优先级 | 激活条件 |
|----|------|--------|----------|
| model_driven | 模型驱动轨 | 1 | 正常运行时 |
| data_driven | 数据驱动轨 | 2 | 模型驱动轨信号不足时补充 |
| human_override | 人工指令轨 | 3 | 人工干预时 |
| emergency | 应急保命轨 | 4 | 所有模型/策略/信号失效时 |

## L0-L6 决策层

| 层 | 名称 | 所属轨 | 频率 | 状态 |
|----|------|--------|------|------|
| L0 | 数据接入与预处理层 | model_driven | tick | stable |
| L1 | 因子计算层 | model_driven | daily | stable |
| L2A | 信号层 | model_driven | daily | planned |
| L2B | 主力行为层 | model_driven | daily | planned |
| L2C | 市场状态与大盘预测层 | model_driven | daily | planned |
| L2D | 知识图谱与因果推演层 | model_driven | daily | planned |
| L3 | 策略组合层 | model_driven | daily | planned |
| L4 | 风控层 | model_driven | realtime | stable |
| L5 | 学习层 | model_driven | weekly | planned |
| L6 | 自评估层 | model_driven | weekly | planned |

## 五条承重墙不变量

| 编号 | 不变量 | 强制点 |
|------|--------|--------|
| DEC-INV-001 | 风控一票否决：order 节点必有 risk_check→order 的 approving 边 | 应用层 finalize 校验 |
| DEC-INV-002 | 信号仓位分离：signal 不能直接连 order | DB 触发器硬阻断 |
| DEC-INV-003 | DAG 无环 | 应用层 Tarjan SCC |
| DEC-INV-004 | 时间单调性：edges.valid_since ≥ from_node.created_at | DB CHECK |
| DEC-INV-005 | evidence_hash 必填 | DB NOT NULL |

## 程序化访问

- **只读查询**：[`extract_decisiongraph.py`](../../../scripts/governance/extract_decisiongraph.py)（CLI）或 `DecisionGraphReader`（Python）
- **写入设计态**：[`apply_decisiongraph.py`](../../../scripts/governance/apply_decisiongraph.py)（pg_advisory_lock=424244）
- **YAML→DB 同步**：[`generate_decision_graph.py`](../../../scripts/governance/generate_decision_graph.py)（tracks/layers 同步）
- **回测落图**：`backtest_result_to_decision_node()`（BacktestResult → L5 学习层节点）
