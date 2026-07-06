---
module_id: ARCH-VIEW-005
title: "数据流架构（dataflowgraph）"
doc_type: architecture_view
status: active
version: 1.0.0
date: '2026-07-06'
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 数据流架构（dataflowgraph）

> **本目录是数据流图的入口索引**。自动生成的 Mermaid 图表 + Markdown 文档位于 `generated/dataflows/`。
> 三图正交声明见 [AGENTS.md §11](../../../AGENTS.md)。

## 概述

数据流图（dataflowgraph）是与依赖图（depgraph）、决策流图（decisiongraph）正交的第二维度全景图。

| 全景图 | 维度 | 表达 | 文档位置 |
|--------|------|------|----------|
| depgraph | 模块依赖 | "谁依赖谁"（静态） | `02_domain_architecture_docs/` + `generated/domains/` |
| **dataflowgraph** | **数据流** | **"数据从哪流到哪"（动态）** | **`generated/dataflows/`** |
| decisiongraph | 决策流 | "决策如何产生"（动态） | `06_decision_architecture/` + `generated/decisions/` |

三图通过 `module_id` / `source_code_ref` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）。

## 自动生成文档（generated/dataflows/）

> **禁止手工编辑**——以下文档由 `generate_dataflow_diagram.py` 从 PostgreSQL `dataflow_*` 表自动生成。
> 真源：`dataflow_graph_registry.yaml`（YAML 真源）→ `dataflow_*` 表（DB 缓存）→ 本目录（派生文档）。

| 文档 | 内容 |
|------|------|
| [dataflow_index.md](../generated/dataflows/dataflow_index.md) | 索引（统计 + Dataset/Job 清单） |
| [dataflow_overview.mmd](../generated/dataflows/dataflow_overview.mmd) | 全景图（所有 Dataset/Job） |
| [dataflow_production.mmd](../generated/dataflows/dataflow_production.mmd) | 生产数据流图（scope=production） |
| [dataflow_backtest.mmd](../generated/dataflows/dataflow_backtest.mmd) | 回测内部数据流图（scope=backtest_internal） |

## 生成器

- **脚本**：[`scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py`](../../../scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py)
- **触发**：手动运行 / GitCommitGateway post-commit reconciler 自动触发
- **数据源**：PostgreSQL `dataflow_datasets` / `dataflow_jobs` / `dataflow_edges` 表（ARCH-051）
- **用法**：`python scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py`

## 程序化访问

- **只读查询**：`extract_dataflowgraph.py`（CLI）或 `DataflowGraphReader`（Python）
- **写入设计态**：`apply_dataflowgraph.py`（pg_advisory_lock=424243）
- **YAML→DB 同步**：`sync_yaml_to_depgraph.py`（dataflow_graph_registry.yaml → dataflow_* 表）
