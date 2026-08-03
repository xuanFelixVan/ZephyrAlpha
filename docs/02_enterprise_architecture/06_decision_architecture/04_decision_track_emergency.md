---
doc_type: architecture_view
title: 决策流图 应急保命轨（Emergency Track）
version: "1.0"
status: active
date: 2026-08-03
owner: auto-generator
ttl: permanent
---

# 决策流图 · 应急保命轨（Emergency Track）

> 生成时间: 2026-08-03T19:13:48
> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）
> 数据库: depgraph (PostgreSQL)
> 导航: [返回主索引 decision_index.md](decision_index.md) | Track 4

**track_id**: `emergency` | **优先级**: 4 | **激活条件**: 所有模型/策略/信号失效时

全系统降级到最简规则：L2失效→硬编码均线 / L3失效→固定比例仓位 / L4失效→硬编码10%上限 / 数据断流→仅执行卖出


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

