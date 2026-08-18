---
ttl: permanent
doc_type: architecture_view
title: 数据层架构 / Data Layer
owner: ZephyrAlpha-Owner
language: zh
---

# 03 · 数据层架构

> 大白话项目现状。数据库角色分工 + Hot/Warm/Cold 三层 + AUTO 表计数 + 外链数据清单。

## 1. 数据库角色分工矩阵

| 数据库 | 引擎 | 角色 | 真源性质 |
|--------|------|------|---------|
| **depgraph** | PostgreSQL 16 | 架构真源（依赖/路径全景图，双态设计+运营） | 架构数据真源，`apply_depgraph.py`/`generate_project_depgraph.py` 直接写 |
| **业务库** | ClickHouse 26.x | Hot 层业务行情/基本面仓库（MergeTree） | 由数据集成器写入 |
| **governance.db** | SQLite (WAL) | 治理运行时（任务系统/审计/事件存储） | `TaskRepository` 唯一真源 |
| **Warm 层** | DuckDB + Parquet | 中频历史数据 | 派生 |
| **向量库** | ChromaDB | 知识库向量 | 派生 |

> **SSoT 铁律**：规则数据真源 = YAML（`architecture_model/`）→ `sync_yaml_to_depgraph.py` 单向同步到 depgraph DB；架构数据真源 = PostgreSQL depgraph，`apply_*.py` 直接写，**禁止反向 DB→YAML**。

## 2. 统一连接入口

`DatabaseService`（MOD-INF-002）封装各引擎连接，ClickHouse 读写分层（D_DATA 域）：TCP:9000 查询 + HTTP:8123 写入 + 本地落盘回退。所有持久化通过 `shared.io.sqlite_factory` + `paths.DB_PATH`（governance.db）。depgraph 用 `DepgraphSchema._SelfHealingPool` 自愈连接池。

## 3. Hot/Warm/Cold 三层存储架构

| 层 | 职责 | 存储 | 场景 |
|----|------|------|------|
| Hot | 高频实时数据 | ClickHouse MergeTree + 常驻内存 | tick_data / index_quote |
| Warm | 中频历史数据 | DuckDB + Parquet | daily_kline 等 |
| Cold | 长期归档（7 年合规） | Parquet | 合规归档 |

> 三平面定义与跨平面通信铁律由 `architecture_model/cross_cutting/invariants.yaml`（INV-010/011/012/018-020）强制执行。

## 4. 表计数

<!-- AUTO-START:table_counts -->
<!-- 数据源：table_registry 内存加载 | 最后同步：2026-08-17 -->

| 数据库 / Database | 表数 / Tables |
|------|------|
| `c0_meta` | 1 |
| `c1_market` | 94 |
| `c3_fundamental` | 23 |
| **合计 / Total** | **118** |
<!-- AUTO-END:table_counts -->

## 5. 外部权威源（全量表清单与逐表 schema）

| 权威源 | 内容 | 路径 |
|--------|------|------|
| 数据清单 | 全量表清单 + 字段 + 分类 | `docs/02_enterprise_architecture/05_dataflow_architecture/data_inventory.md`（`generate_data_inventory.py`） |
| 数据采集流 | L0→L1 标准化管线 | `docs/02_enterprise_architecture/05_dataflow_architecture/data_acquisition_flow.md` |
| 数据流图 | 端到端数据流 | `docs/02_enterprise_architecture/05_dataflow_architecture/` |

> 数据架构红线（PIT/反幸存者偏差）由 fitness functions 强制执行（`scripts/arch_guard/fitness_functions/check_pit_compliance.py` + `check_survivorship_bias.py`）；runtime 血缘见 #ARCH-DATA-LINEAGE-001。
