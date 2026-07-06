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
| MOD-L00-002 | 数据源操作手册 | [data_source_operation_manual](data_source_operation_manual.md) | Active | verified |
| MOD-L00-003 | 数据获取需求清单 | [data_acquisition_plan](data_acquisition_plan.md) | Active | verified |
| MOD-L00-004 | 数据源集成器 | [data_source_integrator_blueprint](data_source_integrator_blueprint.md) | Active | in_progress |

## 参考文档

| 文档 | 说明 | SSoT 范围 |
|------|------|----------|
| [数据源操作手册](data_source_operation_manual.md) | iFind + miniQMT 可获取数据完整清单与获取方法，所有 API 调用方法均已实测验证固化 | 数据源能力唯一真源——"能获取什么+怎么获取" |
| [数据获取需求清单](data_acquisition_plan.md) | 数据库现状对照 + 需补充数据清单（P0/P1/P2/P3优先级）+ 执行计划 | 数据获取需求唯一真源——"需要什么+现状如何+缺什么" |
| [业务数据清单](data_inventory.md) | ClickHouse 80 张业务表实时扫描结果（起止时间/标的数/行数/数据源/新鲜度），生成器 `tmp/generate_data_inventory.py` 可随时刷新 | 业务表数据现状唯一真源——"有什么+新鲜度如何" |
| [实盘数据清单](realtime_data_inventory.md) | 35 项实盘交易实时数据能力索引（数据源/延迟/限流/稳定性/读取速度），生成器 `tmp/generate_realtime_inventory.py` | 实盘数据能力唯一真源——"实盘能拿什么+多快" |
| 数据获取能力矩阵 | 78 项数据需求 4 态分类（稳定获取/手动触发/待接入/无法获取），生成器 `tmp/generate_acquisition_matrix.py` 阶段4 重新生成 | 数据缺口与自动化短板唯一真源——"哪些能自动/哪些拿不到" |

**架构模型真源**：`docs/03_modules/_domain_data/blueprint.md`（Provider 抽象部分已移交 MOD-L00-004）
**数据源集成器真源**：`docs/03_modules/_domain_data/data_source_integrator_blueprint.md`（Provider 抽象 + 调度编排 + 策略注册表）
**数据源能力真源**：`docs/03_modules/_domain_data/data_source_operation_manual.md`
**数据获取需求真源**：`docs/03_modules/_domain_data/data_acquisition_plan.md`
**业务数据现状真源**：`docs/03_modules/_domain_data/data_inventory.md`（派生自 ClickHouse 实时扫描）
**数据缺口现状真源**：`tmp/generate_acquisition_matrix.py` 输出（阶段4 重新生成，输出到 `docs/03_modules/_domain_data/data_acquisition_matrix.md`）

## 导航

- [上级目录](../index.md)
- [架构真源](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md)
