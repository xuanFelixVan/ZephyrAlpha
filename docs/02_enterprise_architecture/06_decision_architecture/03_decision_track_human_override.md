---
doc_type: architecture_view
title: 决策流图 人工指令轨（Human Override Track）
version: "1.0"
status: active
date: 2026-07-31
owner: auto-generator
ttl: permanent
---

# 决策流图 · 人工指令轨（Human Override Track）

> 生成时间: 2026-07-31T17:21:51
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | Track 3

**track_id**: `human_override` | **优先级**: 3 | **激活条件**: 人工干预时

人工买入/卖出/调仓指令 + 人工风控干预 + 人工参数覆盖 + 指令审计链


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

