---
doc_type: architecture_view
title: 决策流图 数据驱动轨（Data-Driven Track）
version: "1.0"
status: active
date: 2026-08-02
owner: auto-generator
ttl: permanent
---

# 决策流图 · 数据驱动轨（Data-Driven Track）

> 生成时间: 2026-08-02T22:07:21
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | Track 2

**track_id**: `data_driven` | **优先级**: 2 | **激活条件**: 模型驱动轨信号不足时补充

端到端 DL 信号：原始数据→自动特征→买卖信号→密度预测PDF→AI信号融合→AI级决策信号


## 统计

| Layer 数 | 决策节点数 | 域内边数 | 跨轨边数 |
|----------|-----------|----------|----------|
| 0 | 0 | 0 | 0 |

## Layer 骨架图（三视图）

> 本轨无决策节点，骨架图省略。Layer 清单见下方表格。

## 功能域文件（L2A/L3 拆分）

> （本轨无功能域文件——决策节点未按域拆分）

## Layer 清单

| layer_id / 层ID | 名称 / name | 英文名 / name_en | 所属轨 / track | 蓝图(module_id) | 蓝图名 / bp | 代码引用 / ref | 功能简述 / desc | 决策频率 / freq | maturity / 成熟度 | build_status / 构建状态 |
|----------|------|--------|--------|-----------------|--------------|----------|----------|----------|--------|--------------|

## 跨轨边

> （无跨轨边）

