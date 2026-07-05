---
module_id: MOD-L00-001
title: D-DATA 域索引
doc_type: index
status: Active
layer: L2_domain
date: "2026-06-22"
version: "2.0.0"
ttl: permanent
---

# D-DATA — 数据源域索引

> **架构裁定**：D19/D21 — 14层降级为域属性，D-DATA 为唯一分类。
> **命名规范**：统一下划线（snake_case）。

## 模块清单

| module_id | 模块名 | blueprint | status | construction_progress |
|-----------|--------|-----------|--------|-----------------------|
| MOD-L00-001 | Datasource Core | [blueprint](blueprint.md) | Draft | partially_implemented |
| MOD-L00-002 | 数据源能力地图 | [data_source_capability_map](data_source_capability_map.md) | Active | verified |
| MOD-L00-003 | 数据获取需求清单 | [data_acquisition_plan](data_acquisition_plan.md) | Active | verified |

## 参考文档

| 文档 | 说明 | SSoT 范围 |
|------|------|----------|
| [数据源能力地图](data_source_capability_map.md) | iFind + miniQMT 可获取数据完整清单与获取方法，所有 API 调用方法均已实测验证固化 | 数据源能力唯一真源——"能获取什么+怎么获取" |
| [数据获取需求清单](data_acquisition_plan.md) | 数据库现状对照 + 需补充数据清单（P0/P1/P2/P3优先级）+ 执行计划 | 数据获取需求唯一真源——"需要什么+现状如何+缺什么" |
| [业务数据清单](data_inventory.md) | ClickHouse 80 张业务表实时扫描结果（起止时间/标的数/行数/数据源/新鲜度），生成器 `tmp/generate_data_inventory.py` 可随时刷新 | 业务表数据现状唯一真源——"有什么+新鲜度如何" |

**架构模型真源**：`docs/03_modules/_domain_data/blueprint.md`
**数据源能力真源**：`docs/03_modules/_domain_data/data_source_capability_map.md`
**数据获取需求真源**：`docs/03_modules/_domain_data/data_acquisition_plan.md`
**业务数据现状真源**：`docs/03_modules/_domain_data/data_inventory.md`（派生自 ClickHouse 实时扫描）

## 导航

- [上级目录](../index.md)
- [架构真源](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md)
