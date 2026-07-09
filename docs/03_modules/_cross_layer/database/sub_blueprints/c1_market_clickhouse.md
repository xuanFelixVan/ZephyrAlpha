---
module_id: MOD-C1-MARKETCH
submodule_path: data/databases/c1_market_clickhouse
title: "C1 market_clickhouse 行情仓库施工蓝图"
doc_type: blueprint
status: Active
version: "1.0.1"
layer: L2_domain
layer_name: market_warehouse
functional_domain: data
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260701-c1
valid_from: "2026-07-01"
date: "2026-07-01"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "data/databases/c1_market_clickhouse/"
belongs_to: "ARCH-BIZDB-001"
parent_module: "ARCH-BIZDB-001"
codification_level: L1
last_updated: "2026-07-05"
generation: 1
rule_form: structural
scope: module
stability: evolving
verifiability: design_review
references:
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\business_data_architecture.md"
    section: "§5.2 C1 / §6 插拔机制 / §7 回测调度 / §8 硬边界"
    why: "业务数据库母蓝图——C1的上游设计真源"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\blueprint.md"
    section: "§4 接口契约"
    why: "数据源接入层——C1的数据来源（D_DATA）"
depends_on:
  - target: ARCH-BIZDB-001
    at: "§5.2/§6/§7/§8"
    why: "母蓝图定义C1的8张表/插拔机制/回测调度/硬边界"
  - target: MOD-L00-001
    at: "§4"
    why: "数据源接入层为C1提供原料数据（当前OHLCV，多品类扩展后覆盖8张表）"
  - target: MOD-INF-012A
    at: "§10"
    why: "ClickHouse基础设施部署依赖"
tags: [clickhouse, market-data, warehouse, c1, backtest, replay, preload, ddl-as-code, category-registry, sub-blueprint]
priority: P1
runtime_plane: warm
---

# C1 market_clickhouse 行情仓库施工蓝图

## 概述

C1 market_clickhouse 是业务数据库仓库层的**行情仓库**，存储 L1 标准化行情数据。它是回测引擎和实盘分析的**数据底座**——回测时从 C1 批量加载到内存重演（母蓝图 §7 模式③：批量预加载内存 + 时间步重演），实盘时 C1 提供实时行情查询。

本蓝图是母蓝图 ARCH-BIZDB-001 的子蓝图之一，承接母蓝图 §5.2 定义的 C1 行情仓库 8 张表，将其细化到字段级 DDL，并对接母蓝图 §6 插拔式品类管理、§7 回测调度策略、§8 硬性边界清单。

**8 张表**（母蓝图 §5.2 已定义，本蓝图细化到字段级 DDL）：

| # | 表名 | 品类 | 性质 | calc_mode | category_id |
|---|------|------|------|:---------:|-------------|
| 1 | tick_data | A股3秒Tick | 原料 | replay | market_tick |
| 2 | daily_kline | 日线OHLCV | 成品(聚合) | preload | market_daily_kline |
| 3 | auction_snapshot | 集合竞价快照 | 原料 | preload | market_auction |
| 4 | index_quote | 指数行情 | 原料 | replay | market_index |
| 5 | option_iv_surface | 期权IV曲面 | 原料(衍生) | preload | market_option_iv |
| 6 | futures_position | 期货持仓 | 原料(衍生) | preload | market_futures_position |
| 7 | futures_term_structure | 期货期限结构 | 原料(衍生) | preload | market_futures_term |
| 8 | convertible_bond_iv | 可转债隐含波动率 | 成品(算) | preload | market_cb_iv |

> **本蓝图是设计书**：描述目标态。ClickHouse 已于 2026-07-01 部署（INFRA-DB-006），c1_market 数据库及 daily_kline 表已建。`construction_progress: partially_implemented`（部分表已建，其余待 DDL-as-Code 施工）。

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属 SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单 SSoT**：`python scripts/governance/extract_depgraph.py --modules C1-MARKET-CH`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | schemas/categories/market_tick.py | §4.1 | tick_data 表 DDL-as-Code | 待建 |
| 2 | schemas/categories/market_daily_kline.py | §4.2 | daily_kline 表 DDL-as-Code | 待建 |
| 3 | schemas/categories/market_auction.py | §4.3 | auction_snapshot 表 DDL-as-Code | 待建 |
| 4 | schemas/categories/market_index.py | §4.4 | index_quote 表 DDL-as-Code | 待建 |
| 5 | schemas/categories/market_option_iv.py | §4.5 | option_iv_surface 表 DDL-as-Code | 待建 |
| 6 | schemas/categories/market_futures_position.py | §4.6 | futures_position 表 DDL-as-Code | 待建 |
| 7 | schemas/categories/market_futures_term.py | §4.7 | futures_term_structure 表 DDL-as-Code | 待建 |
| 8 | schemas/categories/market_cb_iv.py | §4.8 | convertible_bond_iv 表 DDL-as-Code | 待建 |
| 9 | c1_market_writer.py | §4.9 | C1 行情仓库写入接口 | 待建 |
| 10 | c1_market_reader.py | §4.10 | C1 行情仓库查询接口 | 待建 |
| 11 | c1_backtest_loader.py | §4.11 | C1 回测数据加载器 | 待建 |
| 12 | apply_schema.py | §16 步骤2 | DDL 自动建表执行器 | 待建 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → §0.1 部分已建(daily_kline)/部分待建 | 逐文件核对 | ☐ |
| 蓝图描述的表名/字段 = DDL-as-Code 文件中的表名/字段 | `grep "CREATE TABLE" schemas/categories/market_*.py` | ☐ |
| 8 张表 calc_mode 全部标注 | `grep "calc_mode" business_data_categories.yaml` | ☐ |
| 8 张表 category_id 全部注册 | `grep "category_id" business_data_categories.yaml` | ☐ |
| actual_disk_path = §10 产出物路径 | 路径比对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (本版) | 无代码（设计态） | 全部 12 文件 | partially_implemented（ClickHouse 已部署，daily_kline 表已建，其余 7 张表待 DDL-as-Code 施工） |

---

## §1 设计背景与目标

### §1.1 背景

ZephyrAlpha 业务数据库母蓝图（ARCH-BIZDB-001 §5.2）定义了 **C1 market_clickhouse 行情仓库**的 8 张表（tick_data / daily_kline / auction_snapshot / index_quote / option_iv_surface / futures_position / futures_term_structure / convertible_bond_iv），覆盖 A 股 3 秒 Tick、日线 OHLCV、集合竞价、指数、期权 IV、期货持仓、期货期限结构、可转债 IV 共 8 个行情品类。

母蓝图 §6 要求**品类插拔式管理**（4 层机制：品类注册表 → DDL-as-Code → CTR 契约 → CategoryManager 发现）；母蓝图 §7 要求回测采用**模式③混合调度**（批量预加载内存 + 时间步重演），并要求每个品类标注 **calc_mode**（replay/preload/hybrid）；母蓝图 §7.1 要求**分层加载**（热层 tick 常驻内存 / 温层日线按时间窗）；母蓝图 §8 要求硬边界品类（港股/美股/期货多市场数据）以 `enabled=false` 预留接口，`market_type` 字段预留但不摄取。

本子蓝图将母蓝图 §5.2 的 8 张表**细化到字段级 DDL**，定义写入/查询/回测加载三类接口，并给出 ClickHouse 引擎策略、分区策略、排序键、TTL 策略。

### §1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 8 张表字段级 DDL | 母蓝图 §5.2 表级定义细化到字段级 |
| 2 | ✅ 包含 | ClickHouse 引擎/分区/排序键/TTL 策略 | 回测性能 + 分区裁剪 + 数据生命周期 |
| 3 | ✅ 包含 | 写入接口 C1MarketWriter | 对接 D_DATA 数据源接入层（CTR-001~008） |
| 4 | ✅ 包含 | 查询接口 C1MarketReader | 实盘实时行情查询 |
| 5 | ✅ 包含 | 回测加载接口 C1BacktestLoader | 对接母蓝图 §7 回测调度（热层/温层分层加载） |
| 6 | ✅ 包含 | calc_mode 标注 | 8 张表标注 replay/preload（母蓝图 §7.5） |
| 7 | ✅ 包含 | category_id 注册 | 8 个品类注册到品类注册表（母蓝图 §6 第1层） |
| 8 | ✅ 包含 | market_type 硬边界预留 | 港股/美股/期货字段预留 enabled=false（母蓝图 §8.2） |
| 9 | ❌ 排除 | 数据源摄取实现 | MOD-L00-001 数据源接入层负责 |
| 10 | ❌ 排除 | 因子计算 | C2 indicator_clickhouse 负责 |
| 11 | ❌ 排除 | ClickHouse 部署运维 | MOD-INF-012A 基础设施层负责 |
| 12 | ❌ 排除 | 回测引擎调度逻辑 | 回测引擎模块负责（C1 仅提供 load 接口） |

### §1.3 术语

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| C1 market_clickhouse | 行情仓库，存 L1 标准化行情数据 | — | 业务数据库仓库层之一 |
| replay | 回测时逐笔实时重算，保证回测=实盘（母蓝图 §7.5） | preload | replay 用于 tick/index 等高频原料 |
| preload | 回测时预加载到内存，性能优先（母蓝图 §7.5） | replay | preload 用于日线/指标等可预计算成品 |
| 热层/温层 | 回测分层加载策略（母蓝图 §7.1） | 冷层 | C1 无冷层（冷层属 C3 新闻/宏观仓库） |
| calc_mode | 品类回测计算模式（母蓝图 §7.5） | — | replay/preload/hybrid 三值 |
| category_id | 品类标识（母蓝图 §6 第1层注册表） | — | C1 的 8 个品类唯一标识 |
| DDL-as-Code | 表结构用 Python 类定义（母蓝图 §6 第2层） | — | 版本可控、AI 可生成 |
| 分区裁剪 | ClickHouse 按分区键跳过无关分区 | — | 提升查询性能 |
| 母蓝图 | 业务数据库顶层架构设计书 ARCH-BIZDB-001 | — | C1 的上游设计真源 |

### §1.4 约束

| 约束 | 影响 |
|------|------|
| ClickHouse 已部署（INFRA-DB-006，2026-07-01 上线，WSL2 Ubuntu） | C1 施工前置阻塞已解除，DDL 可直接执行 |
| 当前数据源(D_DATA)只支持 OHLCV（daily_kline 表） | 其他 7 张表需 D_DATA 步骤3 多品类扩展 |
| 回测内存预算 64G（母蓝图 §7.1） | tick_data 必须分层加载，不能全量载入 |
| 8 张表 calc_mode 必须标注（母蓝图 §7.5） | 回测引擎按 calc_mode 决定处理方式 |
| 硬边界品类(港股/美股/期货多市场) market_type 预留但不摄取 | 字段设计预留，enabled=false |
| ClickHouse 无 AS OF JOIN（母蓝图 §7.3） | 多频率时间对齐在内存工作台完成 |

### §1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 | 设计+施工 | 审批权限 |
| 母蓝图 ARCH-BIZDB-001 | 8张表定义/插拔机制/调度策略上游对齐 | 设计 | C1 为其仓库层子蓝图 |
| MOD-L00-001 数据源接入层 | 原料数据供给（CTR-001~008） | 施工 | C1 的数据来源 |
| MOD-INF-012A 基础设施 | ClickHouse 部署 | 施工前置 | C1 施工前置条件 |
| 回测引擎 | C1BacktestLoader 接口 | 消费 | 分层加载 + calc_mode 调度 |
| 实盘引擎 | C1MarketReader 接口 | 消费 | 实时行情查询 |

### §1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| ClickHouse 部署 | 已部署（INFRA-DB-006，2026-07-01 上线） | INFRA-DB-006 ClickHouse 部署 | 部分表已建 | P0 |
| 8 张表 DDL | 无 | 8 个 schemas/categories/market_*.py | 待编写 DDL-as-Code | P0 |
| 数据源覆盖 | OHLCV（daily_kline 1张） | 8张表全覆盖 | 需 D_DATA 步骤3 多品类扩展 | P0 |
| 写入接口 | 无 | C1MarketWriter | 待实现 | P1 |
| 回测加载接口 | 无 | C1BacktestLoader（热层/温层） | 待实现 | P1 |
| 品类注册表 | 无 | 8 条品类注册记录 | 待注册（母蓝图 §6 第1层） | P1 |

### §1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 日线行情回测 | 回测引擎启动 | C1BacktestLoader.load_warm_layer → daily_kline 预加载到内存 | DataFrame dict |
| Tick 回测 | 回测引擎启动 | C1BacktestLoader.load_hot_layer → tick_data 常驻内存逐笔回放 | DataFrame dict |
| 实盘行情查询 | 实盘引擎请求 | C1MarketReader.query_latest → ClickHouse 实时查询 | DataFrame |
| 日线写入 | D_DATA 摄取完成 | C1MarketWriter.upsert_daily_kline → ClickHouse 批量写入 | 写入行数 |
| 范围查询 | 分析模块请求 | C1MarketReader.query_range → 分区裁剪查询 | DataFrame |
| 硬边界品类预留 | 港股/美股注册 | market_type 字段预留，enabled=false | 预留接口（不摄取） |

---

## §2 模块边界

### §2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 8 张表 DDL 设计 | 字段级 Schema + 引擎/分区/排序键/TTL（母蓝图 §6 第2层） | 本模块 |
| 2 | ✅ 包含 | 行情数据写入 | C1MarketWriter 对接 D_DATA CTR-001~008 契约 | 本模块 |
| 3 | ✅ 包含 | 行情数据查询 | C1MarketReader 范围查询/最新查询（分区裁剪） | 本模块 |
| 4 | ✅ 包含 | 回测数据加载 | C1BacktestLoader 热层/温层分层加载（母蓝图 §7.1） | 本模块 |
| 5 | ✅ 包含 | calc_mode 标注 | 8 张表标注 replay/preload（母蓝图 §7.5） | 本模块 |
| 6 | ✅ 包含 | category_id 注册 | 8 个品类注册到品类注册表（母蓝图 §6 第1层） | 本模块 |
| 7 | ✅ 包含 | market_type 硬边界预留 | 港股/美股/期货字段预留 enabled=false（母蓝图 §8.2） | 本模块 |
| 8 | ❌ 排除 | 数据源摄取 | D_DATA 数据源接入层负责 | MOD-L00-001 |
| 9 | ❌ 排除 | 因子计算 | C2 indicator_clickhouse 负责 | C2 |
| 10 | ❌ 排除 | ClickHouse 部署运维 | 基础设施层负责 | MOD-INF-012A |
| 11 | ❌ 排除 | 回测引擎调度 | 回测引擎模块负责（C1 仅提供 load 接口） | 回测引擎 |
| 12 | ❌ 排除 | 新闻/宏观数据 | C3 news_clickhouse 负责 | C3 |

### §2.2 排除项

| # | 排除项 | 原因 | 归属模块 |
|---|--------|------|---------|
| 1 | 数据源 API 调用 | 数据摄取是 D_DATA 职责 | MOD-L00-001 |
| 2 | 因子值存储 | 因子属指标仓库 | C2-INDICATOR-CH |
| 3 | 回测结果存储 | 回测产出属回测结果仓库 | C4-BACKTEST-CH |
| 4 | 交易事务 | 事务层 | L4-TRADING-SQLITE |

---

## §3 架构设计

### §3.1 组件架构

> 对接母蓝图 §6 插拔式品类管理 4 层机制：第1层品类注册表 → 第2层 DDL-as-Code → 第3层 CTR 契约 → 第4层 CategoryManager 发现与路由。

| # | 组件 | 职责 | 依赖 | 交互方式 | 母蓝图对接 |
|---|------|------|------|---------|---------|
| 1 | schemas/categories/market_*.py (8个) | 8 张表 DDL-as-Code 定义 | — | Python 类 | §6 第2层 DDL-as-Code |
| 2 | C1MarketWriter | 行情数据批量写入 ClickHouse | ClickHouse Client | 同步批量插入 | §6 第3层 CTR-001~008 Consumer |
| 3 | C1MarketReader | 行情数据查询（范围/最新） | ClickHouse Client | 同步查询 | §7.6 实盘数据来源 |
| 4 | C1BacktestLoader | 回测数据分层加载到内存 | C1MarketReader | 同步批量加载 | §7.1 分层加载 / §7.5 calc_mode |
| 5 | apply_schema.py | DDL 自动建表执行器 | schemas/categories/*.py | 一次性执行 | §6 第2层 DDL 执行 |

### §3.2 数据流

```
数据源(D_DATA) → C1MarketWriter.batch_insert → ClickHouse C1表(8张)
                                                    ↓
回测引擎 ← C1BacktestLoader.load_to_memory ← 分区裁剪查询
实盘引擎 ← C1MarketReader.query_latest ← 实时查询
```

**详细数据流**：

| 流向 | 生产者 | 消费者 | 数据类型 | 传输方式 |
|------|--------|--------|---------|---------|
| 写入 | D_DATA DataSourceBase | C1MarketWriter | CTR-001~008 DataFrame | 函数调用 |
| 存储 | C1MarketWriter | ClickHouse C1 表(8张) | 行情记录 | 批量 INSERT |
| 回测加载 | C1BacktestLoader | 回测引擎内存工作台 | 范围查询结果 | 分层批量加载 |
| 实盘查询 | C1MarketReader | 实盘引擎 | 最新行情 | 实时查询 |

### §3.3 与母蓝图 §6/§7/§8 对接

#### 对接母蓝图 §6 插拔式品类管理（4层机制）

| 层次 | 对接内容 | C1 实现 |
|------|---------|---------|
| 第1层 品类注册表 | business_data_categories.yaml 注册 8 条品类 | category_id: market_tick / market_daily_kline / market_auction / market_index / market_option_iv / market_futures_position / market_futures_term / market_cb_iv |
| 第2层 DDL-as-Code | 8 张表 Schema Python 类 | schemas/categories/market_*.py（本蓝图 §4 定义） |
| 第3层 数据契约 | CTR-001~008 每张表一个契约 | 对接 D_DATA CTR 契约体系 |
| 第4层 品类发现 | CategoryManager 按 category_id 路由到 C1 | DatabaseService 按 engine=clickhouse 路由 |

#### 对接母蓝图 §7 回测调度策略

| 母蓝图章节 | 对接内容 | C1 实现 |
|-----------|---------|---------|
| §7.1 分层加载 | 热层常驻内存 / 温层按时间窗 | C1BacktestLoader.load_hot_layer（tick_data）/ load_warm_layer（daily_kline 等） |
| §7.2 并行加载 | 按品类分组并行加载 | C1BacktestLoader 内部 asyncio/threading 并行 |
| §7.3 时间对齐 | 统一时间网格（3秒步长） | C1 仅提供原始数据，对齐在内存工作台完成 |
| §7.5 calc_mode | replay/preload 标注 | 8 张表 calc_mode 见 §4 各表定义 |
| §7.6 回测vs实盘 | 共用同一套计算逻辑 | C1 同时服务回测（C1BacktestLoader）和实盘（C1MarketReader） |

#### 对接母蓝图 §8 硬性边界清单

| 母蓝图章节 | 对接内容 | C1 实现 |
|-----------|---------|---------|
| §8.2 硬边界品类 | 港股/美股/期货多市场数据 enabled=false | market_type 字段预留 DEFAULT 'A_share'，硬边界品类不摄取 |

---

## §4 接口契约

### §4.0 ClickHouse 引擎策略

| 策略项 | 设计 | 理由 |
|--------|------|------|
| 引擎 | 全部 MergeTree | 数据源唯一（D_DATA），不需要 ReplacingMergeTree 去重 |
| 分区策略 | PARTITION BY toYYYYMMDD(trade_date)（高频表）/ toYYYYMM(trade_date)（日频表） | 按天/月分区，方便分区裁剪和 TTL |
| 排序键 | ORDER BY (symbol, trade_date, timestamp)（高频）/ ORDER BY (symbol, trade_date)（日频） | 回测主要查单只股票历史数据，symbol 前缀 |
| TTL | tick_data/index_quote 保留 90 天后归档 Parquet | 高频数据体积大，超期归档 |
| 数据类型 | Decimal(18,4) 价格 / UInt64 成交量 / LowCardinality(String) 枚举 | ClickHouse 推荐类型 |

### §4.1 tick_data（3秒Tick — replay模式）

```python
# schemas/categories/market_tick.py
# category_id: market_tick
# calc_mode: replay（回测时逐笔回放，保证=实盘）

TICK_DATA_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.tick_data
(
    trade_date   Date           COMMENT '交易日期',
    timestamp    DateTime       COMMENT '时间戳(3秒粒度)',
    symbol       String         COMMENT '证券代码',
    price        Decimal(18,4)  COMMENT '成交价',
    volume       UInt64         COMMENT '成交量(股)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    bid_price    Decimal(18,4)  COMMENT '买一价',
    ask_price    Decimal(18,4)  COMMENT '卖一价',
    bid_volume   UInt64         COMMENT '买一量',
    ask_volume   UInt64         COMMENT '卖一量',
    market_type  LowCardinality(String) DEFAULT 'A_share' COMMENT '市场类型(预留港股/美股/期货)',
    data_source  LowCardinality(String)  COMMENT '数据来源(miniQMT等)',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    INDEX idx_ts timestamp TYPE minmax GRANULARITY 1
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(trade_date)
ORDER BY (symbol, trade_date, timestamp)
TTL trade_date + INTERVAL 90 DAY
COMMENT 'A股3秒Tick行情(原料,replay)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | tick_data |
| 品类 | A股3秒Tick |
| 性质 | 原料 |
| 频率 | 3秒 |
| 数据源 | miniQMT |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMMDD(trade_date) |
| 排序键 | ORDER BY (symbol, trade_date, timestamp) |
| 索引 | INDEX idx_ts timestamp TYPE minmax GRANULARITY 1 |
| TTL | trade_date + INTERVAL 90 DAY（超期归档 Parquet） |
| calc_mode | **replay**（回测时逐笔回放，保证=实盘） |
| category_id | **market_tick** |

### §4.2 daily_kline（日线OHLCV — preload模式）

```python
# schemas/categories/market_daily_kline.py
# category_id: market_daily_kline
# calc_mode: preload（回测时预加载到内存）

DAILY_KLINE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.daily_kline
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '证券代码',
    open         Decimal(18,4)  COMMENT '开盘价',
    high         Decimal(18,4)  COMMENT '最高价',
    low          Decimal(18,4)  COMMENT '最低价',
    close        Decimal(18,4)  COMMENT '收盘价',
    volume       UInt64         COMMENT '成交量(股)',
    amount       Decimal(18,2)  COMMENT '成交额(元)',
    amplitude    Decimal(18,4)  DEFAULT 0 COMMENT '振幅(%，AkShare提供)',
    pct_change   Decimal(18,4)  DEFAULT 0 COMMENT '涨跌幅(%，AkShare提供)',
    change       Decimal(18,4)  DEFAULT 0 COMMENT '涨跌额(元，AkShare提供)',
    turnover     Decimal(18,4)  DEFAULT 0 COMMENT '换手率(%，AkShare提供)',
    adj_factor   Decimal(18,8)  DEFAULT 1 COMMENT '复权因子',
    market_type  LowCardinality(String) DEFAULT 'A_share' COMMENT '市场类型(预留港股/美股/期货)',
    data_source  LowCardinality(String)  COMMENT '数据来源(AkShare/miniQMT/iFind)',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
COMMENT '日线OHLCV(成品聚合,preload)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | daily_kline |
| 品类 | 日线OHLCV |
| 性质 | 成品(聚合) |
| 频率 | 日频 |
| 数据源 | miniQMT/iFind |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMM(trade_date)（日线按月分区） |
| 排序键 | ORDER BY (symbol, trade_date) |
| TTL | 无（日线永久保留） |
| calc_mode | **preload**（回测时预加载到内存） |
| category_id | **market_daily_kline** |
| 说明 | 对接 D_DATA DataSourceBase.fetch_historical 输出 CTR-001 |

### §4.3 auction_snapshot（集合竞价快照 — preload模式）

```python
# schemas/categories/market_auction.py
# category_id: market_auction
# calc_mode: preload

AUCTION_SNAPSHOT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.auction_snapshot
(
    trade_date      Date           COMMENT '交易日期',
    auction_time    DateTime       COMMENT '集合竞价时间(9:15-9:25)',
    symbol          String         COMMENT '证券代码',
    auction_price   Decimal(18,4)  COMMENT '集合竞价价格',
    auction_volume  UInt64         COMMENT '集合竞价成交量',
    auction_amount  Decimal(18,2)  COMMENT '集合竞价成交额',
    market_type     LowCardinality(String) DEFAULT 'A_share' COMMENT '市场类型(预留)',
    data_source     LowCardinality(String)  COMMENT '数据来源(miniQMT)',
    quality_flag    UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
COMMENT '集合竞价快照(原料,preload)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | auction_snapshot |
| 品类 | 集合竞价快照 |
| 性质 | 原料 |
| 频率 | 9:15-9:25 |
| 数据源 | miniQMT |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMM(trade_date) |
| 排序键 | ORDER BY (symbol, trade_date) |
| calc_mode | **preload** |
| category_id | **market_auction** |

### §4.4 index_quote（指数行情 — replay模式）

```python
# schemas/categories/market_index.py
# category_id: market_index
# calc_mode: replay

INDEX_QUOTE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.index_quote
(
    trade_date   Date           COMMENT '交易日期',
    timestamp    DateTime       COMMENT '时间戳(3秒粒度)',
    symbol       String         COMMENT '指数代码(如000001.SH)',
    price        Decimal(18,4)  COMMENT '指数点位',
    volume       UInt64         COMMENT '成交量',
    amount       Decimal(18,2)  COMMENT '成交额',
    data_source  LowCardinality(String)  COMMENT '数据来源(miniQMT)',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = MergeTree
PARTITION BY toYYYYMMDD(trade_date)
ORDER BY (symbol, trade_date, timestamp)
TTL trade_date + INTERVAL 90 DAY
COMMENT '指数行情(原料,replay)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | index_quote |
| 品类 | 指数行情 |
| 性质 | 原料 |
| 频率 | 3秒 |
| 数据源 | miniQMT |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMMDD(trade_date) |
| 排序键 | ORDER BY (symbol, trade_date, timestamp) |
| TTL | trade_date + INTERVAL 90 DAY |
| calc_mode | **replay** |
| category_id | **market_index** |

### §4.5 option_iv_surface（期权IV曲面 — preload模式）

```python
# schemas/categories/market_option_iv.py
# category_id: market_option_iv
# calc_mode: preload

OPTION_IV_SURFACE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.option_iv_surface
(
    trade_date   Date           COMMENT '交易日期',
    symbol       String         COMMENT '期权代码',
    underlying   String         COMMENT '标的代码',
    strike       Decimal(18,4)  COMMENT '行权价',
    expiry       Date           COMMENT '到期日',
    iv           Decimal(18,6)  COMMENT '隐含波动率',
    option_type  LowCardinality(String)  COMMENT '期权类型(call/put)',
    delta        Decimal(18,6)  DEFAULT 0 COMMENT 'Delta',
    gamma        Decimal(18,6)  DEFAULT 0 COMMENT 'Gamma',
    theta        Decimal(18,6)  DEFAULT 0 COMMENT 'Theta',
    vega         Decimal(18,6)  DEFAULT 0 COMMENT 'Vega',
    data_source  LowCardinality(String)  COMMENT '数据来源(iFind/AkShare)',
    quality_flag UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (underlying, trade_date, strike, expiry)
COMMENT '期权IV曲面(原料衍生,preload)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | option_iv_surface |
| 品类 | 期权IV曲面 |
| 性质 | 原料(衍生) |
| 频率 | 日频 |
| 数据源 | iFind/AkShare |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMM(trade_date) |
| 排序键 | ORDER BY (underlying, trade_date, strike, expiry) |
| calc_mode | **preload** |
| category_id | **market_option_iv** |

### §4.6 futures_position（期货持仓 — preload模式）

```python
# schemas/categories/market_futures_position.py
# category_id: market_futures_position
# calc_mode: preload

FUTURES_POSITION_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.futures_position
(
    trade_date     Date           COMMENT '交易日期',
    symbol         String         COMMENT '合约代码',
    long_position  UInt64         COMMENT '多头持仓量',
    short_position UInt64         COMMENT '空头持仓量',
    long_volume    UInt64         COMMENT '多头成交量',
    short_volume   UInt64         COMMENT '空头成交量',
    exchange       LowCardinality(String)  COMMENT '交易所(CZCE/DCE/SHFE/CFFEX)',
    data_source    LowCardinality(String)  COMMENT '数据来源(CZCE/DCE)',
    quality_flag   UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
COMMENT '期货持仓(原料衍生,preload)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | futures_position |
| 品类 | 期货持仓 |
| 性质 | 原料(衍生) |
| 频率 | 日频 |
| 数据源 | CZCE/DCE |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMM(trade_date) |
| 排序键 | ORDER BY (symbol, trade_date) |
| calc_mode | **preload** |
| category_id | **market_futures_position** |

### §4.7 futures_term_structure（期货期限结构 — preload模式）

```python
# schemas/categories/market_futures_term.py
# category_id: market_futures_term
# calc_mode: preload

FUTURES_TERM_STRUCTURE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.futures_term_structure
(
    trade_date     Date           COMMENT '交易日期',
    symbol         String         COMMENT '品种代码',
    front_contract String         COMMENT '近月合约',
    next_contract  String         COMMENT '次月合约',
    front_price    Decimal(18,4)  COMMENT '近月价格',
    next_price     Decimal(18,4)  COMMENT '次月价格',
    basis          Decimal(18,4)  COMMENT '基差(近月-次月)',
    data_source    LowCardinality(String)  COMMENT '数据来源(交易所)',
    quality_flag   UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
COMMENT '期货期限结构(原料衍生,preload)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | futures_term_structure |
| 品类 | 期货期限结构 |
| 性质 | 原料(衍生) |
| 频率 | 日频 |
| 数据源 | 交易所 |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMM(trade_date) |
| 排序键 | ORDER BY (symbol, trade_date) |
| calc_mode | **preload** |
| category_id | **market_futures_term** |

### §4.8 convertible_bond_iv（可转债隐含波动率 — preload模式）

```python
# schemas/categories/market_cb_iv.py
# category_id: market_cb_iv
# calc_mode: preload

CONVERTIBLE_BOND_IV_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.convertible_bond_iv
(
    trade_date          Date           COMMENT '交易日期',
    symbol              String         COMMENT '转债代码',
    underlying          String         COMMENT '正股代码',
    iv                  Decimal(18,6)  COMMENT '隐含波动率',
    delta               Decimal(18,6)  DEFAULT 0 COMMENT 'Delta',
    gamma               Decimal(18,6)  DEFAULT 0 COMMENT 'Gamma',
    theta               Decimal(18,6)  DEFAULT 0 COMMENT 'Theta',
    vega                Decimal(18,6)  DEFAULT 0 COMMENT 'Vega',
    conversion_premium  Decimal(18,6)  COMMENT '转股溢价率',
    data_source         LowCardinality(String)  COMMENT '数据来源(iFind)',
    quality_flag        UInt8          DEFAULT 1  COMMENT '质量标记'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
COMMENT '可转债隐含波动率(成品算,preload)'
"""
```

| 属性 | 值 |
|------|-----|
| 表名 | convertible_bond_iv |
| 品类 | 可转债隐含波动率 |
| 性质 | 成品(算) |
| 频率 | 日频 |
| 数据源 | iFind |
| 引擎 | MergeTree |
| 分区 | PARTITION BY toYYYYMM(trade_date) |
| 排序键 | ORDER BY (symbol, trade_date) |
| calc_mode | **preload** |
| category_id | **market_cb_iv** |

### §4.9 写入接口

> 对接 D_DATA 数据源接入层（MOD-L00-001 §4 接口契约）的 CTR-001~008 输出。

```python
class C1MarketWriter:
    """C1 行情仓库写入接口——对接 D_DATA 数据源接入层 CTR-001~008 契约"""

    def __init__(self, clickhouse_client):
        """
        初始化写入器

        Args:
            clickhouse_client: ClickHouse 客户端连接
        """
        ...

    def batch_insert(self, table_name: str, records: list[dict]) -> int:
        """
        批量写入行情数据

        Args:
            table_name: C1 表名（tick_data/daily_kline/...共8张）
            records: 行情记录列表（dict 格式，字段对齐 DDL）

        Returns:
            写入行数

        Raises:
            ClickHouseException: 写入失败
        """
        ...

    def upsert_daily_kline(self, df: pd.DataFrame) -> int:
        """
        日线 OHLCV 写入（对接 D_DATA DataSourceBase.fetch_historical 输出 CTR-001）

        Args:
            df: OHLCV DataFrame（trade_date/symbol/open/high/low/close/volume/amount/adj_factor）

        Returns:
            写入行数

        Note:
            MergeTree 不支持 UPSERT，采用"先删后插"模式（按 symbol+trade_date 删除后批量插入）
        """
        ...
```

### §4.10 查询接口

```python
class C1MarketReader:
    """C1 行情仓库查询接口——实盘实时行情查询"""

    def __init__(self, clickhouse_client):
        """初始化查询器"""
        ...

    def query_range(self, table_name: str, symbol: str,
                    start: datetime, end: datetime) -> pd.DataFrame:
        """
        范围查询（分区裁剪）

        Args:
            table_name: C1 表名
            symbol: 证券代码
            start: 开始时间
            end: 结束时间

        Returns:
            查询结果 DataFrame（利用 PARTITION BY 分区裁剪加速）
        """
        ...

    def query_latest(self, table_name: str, symbol: str) -> pd.DataFrame:
        """
        查最新一条行情

        Args:
            table_name: C1 表名
            symbol: 证券代码

        Returns:
            最新行情 DataFrame（利用 ORDER BY 排序键取最后一条）
        """
        ...
```

### §4.11 回测加载接口

> 对接母蓝图 ARCH-BIZDB-001 §7 回测调度策略。

```python
class C1BacktestLoader:
    """C1 回测数据加载器——对接母蓝图 §7 回测调度策略"""

    def __init__(self, clickhouse_client):
        """初始化回测加载器"""
        ...

    def load_to_memory(self, symbols: list[str], start: datetime, end: datetime,
                       calc_mode: str = "preload") -> dict[str, pd.DataFrame]:
        """
        按 calc_mode 加载到内存（母蓝图 §7.5）

        Args:
            symbols: 证券代码列表
            start: 回测开始时间
            end: 回测结束时间
            calc_mode: 计算模式
                - replay: tick_data/index_quote 逐笔加载（母蓝图 §7.5 mode=replay）
                - preload: daily_kline 等全量加载（母蓝图 §7.5 mode=preload）

        Returns:
            {symbol: DataFrame} 字典
        """
        ...

    def load_hot_layer(self, symbols: list[str]) -> dict:
        """
        热层加载（母蓝图 §7.1：tick + 因子常驻内存）

        加载内容: tick_data（3秒Tick）常驻内存
        内存占用: ~480MB/标的/年（母蓝图 §7.1 内存评估）

        Args:
            symbols: 证券代码列表

        Returns:
            {symbol: tick DataFrame} 字典
        """
        ...

    def load_warm_layer(self, symbols: list[str], start: datetime,
                        end: datetime) -> dict:
        """
        温层加载（母蓝图 §7.1：日线/指标按时间窗）

        加载内容: daily_kline + auction_snapshot + 其他 preload 表
        内存占用: ~2MB/标的/年（日线，母蓝图 §7.1 内存评估）

        Args:
            symbols: 证券代码列表
            start: 时间窗开始
            end: 时间窗结束

        Returns:
            {symbol: {table_name: DataFrame}} 字典
        """
        ...
```

### §4.12 契约版本表

| 契约ID | 对应表 | Producer | Consumer | 版本 | 状态 |
|--------|--------|----------|----------|------|:----:|
| CTR-001 | daily_kline | D_DATA DataSourceBase | C1MarketWriter | 1.0.0 | 待实现 |
| CTR-002 | tick_data | D_DATA (miniQMT) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |
| CTR-003 | auction_snapshot | D_DATA (miniQMT) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |
| CTR-004 | index_quote | D_DATA (miniQMT) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |
| CTR-005 | option_iv_surface | D_DATA (iFind/AkShare) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |
| CTR-006 | futures_position | D_DATA (CZCE/DCE) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |
| CTR-007 | futures_term_structure | D_DATA (交易所) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |
| CTR-008 | convertible_bond_iv | D_DATA (iFind) | C1MarketWriter | 1.0.0 | 待D_DATA扩展 |

---

## §5 约束条件

### §5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 全部表使用 MergeTree 引擎 | 数据源唯一，不需要 ReplacingMergeTree 去重 |
| 2 | 高频表按天分区 / 日频表按月分区 | PARTITION BY toYYYYMMDD / toYYYYMM |
| 3 | 排序键 symbol 前缀 | 回测主要查单只股票历史数据 |
| 4 | 8 张表 calc_mode 必须标注 | replay/preload（母蓝图 §7.5） |
| 5 | 8 张表 category_id 必须注册 | 母蓝图 §6 第1层 |
| 6 | market_type 字段预留硬边界品类 | 港股/美股/期货 DEFAULT 'A_share'，enabled=false（母蓝图 §8.2） |
| 7 | tick_data/index_quote TTL 90天 | 高频数据超期归档 Parquet |
| 8 | daily_kline 永久保留 | 日线数据不 TTL |
| 9 | DDL-as-Code 格式 | Python 类定义表结构（母蓝图 §6 第2层） |
| 10 | ClickHouse 已部署（2026-07-01），前置阻塞已解除 | INFRA-DB-006 已上线 |

### §5.2 容量估算

> 参考母蓝图 §7.1 内存评估（64G 预算）。

| 维度 | 单标的1年 | 100标的1年 | 分层后占用 | 分层归属 |
|------|:--------:|:---------:|:---------:|:--------:|
| tick_data（3秒tick） | ~480MB | ~48GB | 热层常驻 | 热层 |
| daily_kline（日线） | ~2MB | ~200MB | 温层按时间窗 | 温层 |
| index_quote（指数3秒） | ~480MB | ~48GB | 热层常驻 | 热层 |
| auction_snapshot（日频） | ~2KB | ~200KB | 温层 | 温层 |
| option_iv_surface（日频） | ~50KB | ~5MB | 温层 | 温层 |
| futures_position（日频） | ~10KB | ~1MB | 温层 | 温层 |
| futures_term_structure（日频） | ~10KB | ~1MB | 温层 | 温层 |
| convertible_bond_iv（日频） | ~10KB | ~1MB | 温层 | 温层 |

### §5.3 迁移/废弃方案

| # | 迁移项 | 来源 | 目标 | 状态 |
|---|--------|------|------|:----:|
| 1 | market.duckdb → ClickHouse | INFRA-DB-005 (已废弃,2026-07-05删除) | C1 market_clickhouse | daily_kline 已迁移至 ClickHouse；market.duckdb 残留文件已于 2026-07-05 删除（524KB，无有价值数据） |
| 2 | DDL 迁移 | c1_market_schema.py（待建，DDL-as-Code 模式） | schemas/categories/c1_market_*.py | 待编写 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | ClickHouse 连接失败 | 连接超时 | 重试 + 告警 | 写入/查询不可用 |
| 2 | 批量写入失败 | ClickHouseException | 记录失败批次 + 重试 | 数据延迟 |
| 3 | 分区裁剪失效 | 查询计划分析 | 检查 WHERE 条件含 trade_date | 查询性能下降 |
| 4 | TTL 归档失败 | 归档任务日志 | 重试归档 + 保留原数据 | 磁盘占用增长 |
| 5 | DDL 执行失败 | apply_schema.py 报错 | 检查表已存在 + 字段冲突 | 建表阻塞 |
| 6 | 数据质量标记 quality_flag=0 | 写入前校验 | 标记后写入 + 告警 | 下游收到异常标记数据 |

### §6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| c1_insert_total | Counter | 自动埋点 | — | — |
| c1_insert_error_total | Counter | 自动埋点 | >5%错误率 | P1 |
| c1_query_latency_seconds | Histogram | 计时 | P95>5s | P2 |
| c1_backtest_load_seconds | Histogram | 计时 | P95>60s | P1 |
| c1_partition_count | Gauge | 元数据查询 | >365分区/表 | P2 |
| c1_disk_usage_bytes | Gauge | 系统监控 | >80%磁盘 | P1 |

### §6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| ClickHouse | 无（C1 是数据底座） | 全部行情写入/查询/回测加载 | 回测降级为 MemoryProvider 合成数据（仅测试） | ClickHouse 恢复 |
| C1BacktestLoader 热层 | 温层加载 | tick 逐笔回放 | 回测仅用日线 preload | tick_data 数据补齐 |
| C1MarketReader | 无降级 | 实盘查询 | 实盘引擎降级为缓存最后行情 | ClickHouse 恢复 |

---

## §7 安全考量

| # | 安全项 | 措施 | 依据 |
|---|--------|------|------|
| 1 | ClickHouse 凭证 | 环境变量存储，禁止硬编码 | 防幻觉十八条 |
| 2 | 数据库网络访问 | ClickHouse 仅监听内网，禁止公网暴露 | 基础设施安全 |
| 3 | 写入权限控制 | C1MarketWriter 独立账户，仅 INSERT 权限 | 最小权限原则 |
| 4 | 查询权限控制 | C1MarketReader 独立账户，仅 SELECT 权限 | 最小权限原则 |
| 5 | DDL 权限控制 | apply_schema.py 独立管理员账户，仅初始化时使用 | 最小权限原则 |
| 6 | 数据分类 | classification: confidential（行情数据机密） | frontmatter |
| 7 | 审计日志 | 所有写入/查询操作记录审计日志 | 合规要求 |
| 8 | 备份策略 | ClickHouse 数据定期备份到对象存储 | 灾难恢复 |

---

## §8 测试策略

### §8.1 测试分层

| 层次 | 测试类型 | 覆盖范围 | 工具 | 状态 |
|------|---------|---------|------|:----:|
| 单元测试 | DDL 正确性 | 8 张表 DDL 语法校验 | pytest + clickhouse-test | 待实现 |
| 单元测试 | 写入接口 | C1MarketWriter.batch_insert / upsert_daily_kline | pytest | 待实现 |
| 单元测试 | 查询接口 | C1MarketReader.query_range / query_latest | pytest | 待实现 |
| 集成测试 | 回测加载 | C1BacktestLoader 热层/温层加载 | pytest + testcontainers | 待实现 |
| 集成测试 | D_DATA 对接 | CTR-001~008 写入 C1 全链路 | pytest | 待实现 |
| 性能测试 | 分区裁剪 | 范围查询分区裁剪效果 | benchmark | 待实现 |
| 性能测试 | 回测加载延迟 | 100标的1年数据加载时间 | benchmark | 待实现 |

### §8.2 验收测试用例

| # | 用例 | 输入 | 期望输出 | 验证点 |
|---|------|------|---------|--------|
| 1 | daily_kline 写入 | OHLCV DataFrame(100行) | 写入100行 | 数据完整 |
| 2 | daily_kline 范围查询 | symbol=000001, 2026-01-01~2026-06-30 | DataFrame | 分区裁剪生效 |
| 3 | tick_data 热层加载 | symbols=[000001], 全量 | DataFrame dict | 内存占用<500MB |
| 4 | daily_kline 温层加载 | symbols=[000001], 1年 | DataFrame dict | 加载时间<10s |
| 5 | DDL 建表 | apply_schema.py | 8张表创建成功 | 表结构正确 |
| 6 | TTL 归档 | 91天前 tick_data | 归档 Parquet | 原数据删除 |

---

## §9 依赖关系

### §9.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| ARCH-BIZDB-001 母蓝图 | 必须 | 8张表定义/插拔机制/回测调度/硬边界 | §5.2/§6/§7/§8 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\business_data_architecture.md` |
| MOD-L00-001 数据源接入层 | 必须 | 原料数据供给（CTR-001~008） | §4 | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` |
| MOD-INF-012A 基础设施 | 必须(前置) | ClickHouse 部署 | §10 | 基础设施蓝图 |

### §9.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §9.1 依赖声明 ↔ dependency_path_panorama.md | 蓝图声明的每个依赖在依赖图中有对应条目 | 待对齐 | 人工核对 |
| 2 | §10 产出物路径 ↔ 依赖图 C1-MARKET-CH | 路径一致 | 待对齐 | 人工核对 |
| 3 | 8张表 ↔ 母蓝图 §5.2 C1 表清单 | 表名/品类/性质一致 | 已对齐 | 逐表核对 |

### §9.3 内部依赖图

**执行顺序依赖**：

```
INFRA-DB-006 ClickHouse部署 → apply_schema.py 建表 → C1MarketWriter 写入接口 → C1MarketReader 查询接口 → C1BacktestLoader 回测加载
```

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| D_DATA DataSourceBase | C1MarketWriter | CTR-001~008 DataFrame | 函数调用 |
| C1MarketWriter | ClickHouse C1 表(8张) | 行情记录 | 批量 INSERT |
| ClickHouse C1 表 | C1MarketReader | 查询结果 | SQL 查询 |
| ClickHouse C1 表 | C1BacktestLoader | 范围数据 | 分层批量加载 |
| C1BacktestLoader | 回测引擎内存工作台 | DataFrame dict | 内存传递 |

### §9.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | DDL 自动建表 | 是 | 8张表一键创建 | apply_schema.py | 无 | 全缺 | 手动/CI | ClickHouse部署后 |
| 2 | 依赖对齐自动验证 | 否 | 人工核对即可 | — | — | — | — | — |
| 3 | 施工步骤完成度自动检测 | 是 | 验证代码可导入 | pytest | pytest | 无 | CI pipeline | 代码提交时 |

---

## §10 产出物存放目录

> §10 产出物路径 MUST 与依赖图 §5 path_mappings 一致。

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\c1_market_clickhouse.md` | 本文件 |
| DDL-as-Code | `D:\ZephyrAlpha\data\databases\c1_market_clickhouse\schemas\categories\market_*.py` | 8张表 Schema |
| 写入接口 | `D:\ZephyrAlpha\data\databases\c1_market_clickhouse\c1_market_writer.py` | C1MarketWriter |
| 查询接口 | `D:\ZephyrAlpha\data\databases\c1_market_clickhouse\c1_market_reader.py` | C1MarketReader |
| 回测加载 | `D:\ZephyrAlpha\data\databases\c1_market_clickhouse\c1_backtest_loader.py` | C1BacktestLoader |
| 建表执行器 | `D:\ZephyrAlpha\data\databases\c1_market_clickhouse\apply_schema.py` | DDL 自动建表 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\data\databases\c1_market_clickhouse\` | 测试用例 |

---

## §11 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| 回测引擎 | C1BacktestLoader 接口 | load_to_memory / load_hot_layer / load_warm_layer | 回测引擎可加载行情数据 |
| 实盘引擎 | C1MarketReader 接口 | query_latest | 实盘引擎可查询最新行情 |
| D_DATA 数据源接入层 | C1MarketWriter 接口 | batch_insert / upsert_daily_kline | D_DATA CTR-001~008 可写入 C1 |
| 母蓝图 §6 品类注册表 | business_data_categories.yaml | 8条品类注册记录 | CategoryManager 可发现 C1 品类 |
| 母蓝图 §6 CategoryManager | engine=clickhouse 路由 | DatabaseService 路由 | 按 category_id 路由到 C1 |
| MOD-INF-012A 基础设施 | ClickHouse 部署 | INFRA-DB-006 | ClickHouse 可连接 |

---

## §12 需要更新

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | C1-MARKET-CH 注册 | 新建子蓝图 |
| 2 | 母蓝图子模块状态 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\business_data_architecture.md` | child_modules C1 状态更新 | 施工进度变更 |
| 3 | 品类注册表 | `D:\ZephyrAlpha\data\databases\business_data_categories.yaml` | 8条品类注册 | 母蓝图 §6 第1层 |
| 4 | 基础设施注册表 | `D:\ZephyrAlpha\docs\...\infrastructure_registry.yaml` | INFRA-DB-006 注册 | ClickHouse 新建 |
| 5 | sub_blueprints/index.md | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\index.md` | C1 蓝图索引 | 新建子蓝图 |

---

## §13 附录

### §13.1 8张表属性汇总

| # | 表名 | 性质 | 频率 | 数据源 | 引擎 | 分区 | 排序键 | TTL | calc_mode | category_id |
|---|------|------|:----:|--------|------|------|--------|:---:|:---------:|-------------|
| 1 | tick_data | 原料 | 3秒 | miniQMT | MergeTree | toYYYYMMDD | symbol,trade_date,timestamp | 90天 | replay | market_tick |
| 2 | daily_kline | 成品(聚合) | 日频 | miniQMT/iFind | MergeTree | toYYYYMM | symbol,trade_date | 无 | preload | market_daily_kline |
| 3 | auction_snapshot | 原料 | 9:15-9:25 | miniQMT | MergeTree | toYYYYMM | symbol,trade_date | 无 | preload | market_auction |
| 4 | index_quote | 原料 | 3秒 | miniQMT | MergeTree | toYYYYMMDD | symbol,trade_date,timestamp | 90天 | replay | market_index |
| 5 | option_iv_surface | 原料(衍生) | 日频 | iFind/AkShare | MergeTree | toYYYYMM | underlying,trade_date,strike,expiry | 无 | preload | market_option_iv |
| 6 | futures_position | 原料(衍生) | 日频 | CZCE/DCE | MergeTree | toYYYYMM | symbol,trade_date | 无 | preload | market_futures_position |
| 7 | futures_term_structure | 原料(衍生) | 日频 | 交易所 | MergeTree | toYYYYMM | symbol,trade_date | 无 | preload | market_futures_term |
| 8 | convertible_bond_iv | 成品(算) | 日频 | iFind | MergeTree | toYYYYMM | symbol,trade_date | 无 | preload | market_cb_iv |

### §13.2 品类注册表条目模板

> 母蓝图 §6 第1层：business_data_categories.yaml 每个品类一条记录。

```yaml
# business_data_categories.yaml C1 行情仓库品类注册示例
- category_id: market_tick
  name: "A股3秒Tick"
  engine: clickhouse
  database: c1_market
  table: tick_data
  schema_file: schemas/categories/market_tick.py
  data_type: 原料
  lifecycle: hot_warm  # 热层90天+归档
  sla_level: P0
  enabled: true
  hard_constraint: ""
  calc_mode: replay
  contract: CTR-002

- category_id: market_daily_kline
  name: "日线OHLCV"
  engine: clickhouse
  database: c1_market
  table: daily_kline
  schema_file: schemas/categories/market_daily_kline.py
  data_type: 成品
  lifecycle: permanent  # 永久保留
  sla_level: P0
  enabled: true
  hard_constraint: ""
  calc_mode: preload
  contract: CTR-001
```

### §13.3 硬边界品类预留示例

> 母蓝图 §8.2：硬边界品类 enabled=false 预留接口。

```yaml
# 硬边界品类预留（不摄取）
- category_id: market_hk_stock
  name: "港股行情"
  engine: clickhouse
  database: c1_market
  table: tick_data  # 复用 tick_data 表，market_type='HK'
  data_type: 原料
  enabled: false  # 硬边界
  hard_constraint: "数据源需采购(待资金/账户满2年)"
  calc_mode: replay

- category_id: market_us_stock
  name: "美股行情"
  engine: clickhouse
  database: c1_market
  table: tick_data  # 复用 tick_data 表，market_type='US'
  data_type: 原料
  enabled: false  # 硬边界
  hard_constraint: "数据源需采购"
  calc_mode: replay
```

---

## §14 已知风险

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | ClickHouse 已部署，C1 施工前置阻塞已解除 | 高 | 全部代码待建 | DDL-as-Code 设计就绪，可直接执行建表 | 风险 |
| 2 | D_DATA 仅支持 OHLCV，7张表无数据源 | 高 | 7张表空置 | 待 D_DATA 步骤3 多品类扩展 | 风险 |
| 3 | tick_data 内存占用过大（100标的48GB） | 中 | 回测内存溢出 | 热层分层加载 + 限制标的数量 | 风险 |
| 4 | ClickHouse 无 AS OF JOIN | 中 | 多频率时间对齐困难 | 内存工作台完成对齐（母蓝图 §7.3） | 风险 |
| 5 | MergeTree 不支持 UPSERT | — | 中 | daily_kline 先删后插模式 | 负面后果 |
| 6 | TTL 归档 Parquet 需额外存储 | — | 低 | 对象存储归档 | 负面后果 |
| 7 | ClickHouse 部署需新建 INFRA-DB-006 | — | 中 | Docker 部署，对接 MOD-INF-012A | 负面后果 |

---

## §15 验收清单

| # | 验收项 | 验收标准 | 验证方法 | 状态 |
|---|--------|---------|---------|:----:|
| 1 | 8张表 DDL 设计完成 | 字段级 Schema + 引擎/分区/排序键/TTL | 逐表核对 §4.1~§4.8 | ☐ |
| 2 | 8张表 calc_mode 全部标注 | replay/preload | 核对 §13.1 汇总表 | ☐ |
| 3 | 8张表 category_id 全部定义 | market_tick ~ market_cb_iv | 核对 §13.1 汇总表 | ☐ |
| 4 | market_type 硬边界预留 | 港股/美股/期货字段预留 | 核对 tick_data/daily_kline DDL | ☐ |
| 5 | 写入接口设计完成 | C1MarketWriter 3个方法 | 核对 §4.9 | ☐ |
| 6 | 查询接口设计完成 | C1MarketReader 2个方法 | 核对 §4.10 | ☐ |
| 7 | 回测加载接口设计完成 | C1BacktestLoader 3个方法 | 核对 §4.11 | ☐ |
| 8 | 对接母蓝图 §6 插拔机制 | 4层机制全部对接 | 核对 §3.3 | ☐ |
| 9 | 对接母蓝图 §7 回测调度 | 分层加载/calc_mode/回测vs实盘 | 核对 §3.3 | ☐ |
| 10 | 对接母蓝图 §8 硬边界 | market_type 预留 | 核对 §3.3 + §13.3 | ☐ |
| 11 | §0.1 代码清单标记"待建" | 12文件全部待建 | 核对 §0.1 | ☐ |
| 12 | construction_progress = partially_implemented | frontmatter | 核对文件头 | ☐ |
| 13 | 契约版本表完整 | CTR-001~008 | 核对 §4.12 | ☐ |
| 14 | 施工指引 5步骤 | 步骤1~5 | 核对 §16 | ☐ |

---

## §16 施工指引

> 🚧 C1 market_clickhouse 施工指引——对接母蓝图 ARCH-BIZDB-001。ClickHouse 已部署（2026-07-01），前置阻塞已解除，DDL 可直接执行。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取母蓝图 §5.2/§6/§7/§8 关键章节 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且标记"待建" | 逐项核对 | ☐ |
| 4 | 理解 ClickHouse 已部署，前置阻塞已解除 | 确认 DDL 可直接执行 | ☐ |

### §16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 5 个步骤 |
| 施工模式 | 设计先行 + 基础设施就绪后实施 |
| 核心风险 | D_DATA 仅支持 OHLCV（ClickHouse 已部署 2026-07-01） |
| 目标 generation | 1 |
| Spiral 归属 | Spiral 2：仓库层建设（ClickHouse 部署后） |

### §16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | ClickHouse 部署（INFRA-DB-006） | hard | 已部署（2026-07-01） | ✅ |
| 2 | D_DATA 数据源接入层（OHLCV） | hard | 已实现（CTR-001） | ✅（部分） |
| 3 | 母蓝图品类注册表设计 | soft | 设计完成 | ✅ |
| 4 | D_DATA 多品类扩展（7张表数据源） | soft | 待施工 | ❌ |

### §16.3 实施步骤

#### 步骤 1：部署 ClickHouse（基础设施，Docker）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §5 约束条件 / §9 依赖关系 |
| 产出位置 | Docker 部署 + infrastructure_registry.yaml 注册 |
| 验收标准 | ClickHouse 可连接，c1_market 数据库可创建 |
| 验证命令 | `clickhouse-client --query "SELECT 1"` |
| 状态 | ✅ 已部署（2026-07-01 上线） |
| G7 检查项 | 基础设施就绪，下游 DDL 可执行 |

```
→ 注册 INFRA-DB-006 到 infrastructure_registry.yaml
→ 当前状态：已部署（2026-07-01 上线，INFRA-DB-006）
```

#### 步骤 2：执行 DDL 建表（8张表）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1~§4.8 八张表 DDL |
| 产出位置 | `data/databases/c1_market_clickhouse/schemas/categories/market_*.py` + `apply_schema.py` |
| 验收标准 | 8张表创建成功，字段/引擎/分区/排序键/TTL 正确 |
| 验证命令 | `python apply_schema.py && clickhouse-client --query "SHOW TABLES FROM c1_market"` |
| 状态 | ❌ 待步骤1完成 |
| G7 检查项 | DDL-as-Code 文件可执行，表结构与蓝图一致 |

```
→ 编写 schemas/categories/market_*.py（DDL-as-Code，8个文件）
→ 执行 apply_schema.py 自动建表
→ 当前状态：待步骤1完成
```

#### 步骤 3：实现写入接口（C1MarketWriter）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.9 写入接口 |
| 产出位置 | `data/databases/c1_market_clickhouse/c1_market_writer.py` |
| 验收标准 | batch_insert / upsert_daily_kline 可用 |
| 验证命令 | `python -c "from data.databases.c1_market_clickhouse.c1_market_writer import C1MarketWriter"` |
| 状态 | ❌ 待步骤2完成 |
| G7 检查项 | 上游 D_DATA CTR-001 可对接，下游 ClickHouse 可写入 |

```
→ 先实现 daily_kline 表的写入（对接 D_DATA OHLCV 输出 CTR-001）
→ 其他 7 张表写入接口待 D_DATA 步骤3 多品类扩展
```

#### 步骤 4：实现回测加载接口（C1BacktestLoader）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.11 回测加载接口 |
| 产出位置 | `data/databases/c1_market_clickhouse/c1_backtest_loader.py` |
| 验收标准 | load_to_memory / load_hot_layer / load_warm_layer 可用 |
| 验证命令 | `python -c "from data.databases.c1_market_clickhouse.c1_backtest_loader import C1BacktestLoader"` |
| 状态 | ❌ 待步骤3完成 |
| G7 检查项 | 对接母蓝图 §7.1 分层加载 / §7.5 calc_mode |

```
→ 先实现 preload 模式（daily_kline 预加载到温层）
→ replay 模式（tick_data 逐笔回放）待 D_DATA 多品类扩展
```

#### 步骤 5：品类注册表注册（母蓝图 §6 第1层）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §3.3 对接母蓝图 §6 / §13.2 品类注册模板 |
| 产出位置 | `data/databases/business_data_categories.yaml` |
| 验收标准 | 8条品类注册记录，category_id/calc_mode/enabled 正确 |
| 验证命令 | `grep "category_id" business_data_categories.yaml` |
| 状态 | ❌ 待步骤2完成 |
| G7 检查项 | CategoryManager 可发现 C1 品类，按 engine=clickhouse 路由 |

```
→ business_data_categories.yaml 加 8 条品类记录
→ 硬边界品类(港股/美股/期货) enabled=false 预留（母蓝图 §8.2）
```

### §16.4 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同 symbol 并发写入 | 无检测 | MergeTree 追加写 | 后到者追加 |
| 回测加载与实盘查询并发 | 无冲突 | ClickHouse MVCC | 读不阻塞写 |
| 多 AI Session 同时修改 DDL | 锁检测 | RULE-ZERO 文件锁 | FIFO |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| ClickHouse 节点数 | 1（已部署，WSL2 Ubuntu） | infrastructure_registry.yaml |
| C1 表数量 | 0（待建） | SHOW TABLES |
| 日写入记录 | 0 | 日志统计 |
| 回测加载延迟 | — | benchmark |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-C1-001 | ClickHouse 已部署，GAP 已解除 | Docker 部署 INFRA-DB-006 | P0 | C1施工前置 | v1.0.0 | 已解除 |
| GAP-C1-002 | D_DATA 仅支持 OHLCV | D_DATA 步骤3 多品类扩展 | P0 | 7张表无数据源 | v1.1.0 | 待施工 |
| GAP-C1-003 | tick_data 内存占用大 | 热层分层加载 + 标的数量限制 | P1 | 100标的48GB | v1.0.0 | 设计完成 |
| GAP-C1-004 | TTL 归档无存储 | 对象存储(Parquet归档) | P2 | 90天数据到期 | v1.1.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 初始设计 | 8张表 DDL + 3类接口设计 | ❌（设计态） |
| v1.1.0 | 1 | 基础设施就绪 | ClickHouse部署 + DDL执行 + daily_kline写入 | ⚠️ |
| v1.2.0 | 1 | 多品类扩展 | 7张表写入 + replay模式 | ⚠️ |

### §17.4 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ClickHouse 部署 | GAP-C1-001 | Docker compose | Phase 1 | 待施工 |
| 8张表 DDL | GAP-C1-001 | schemas/categories/market_*.py | Phase 2 | 待施工 |
| C1MarketWriter | GAP-C1-001 | c1_market_writer.py | Phase 3 | 待施工 |
| C1MarketReader | GAP-C1-001 | c1_market_reader.py | Phase 3 | 待施工 |
| C1BacktestLoader | GAP-C1-001 | c1_backtest_loader.py | Phase 4 | 待施工 |
| 7张表数据源 | GAP-C1-002 | D_DATA 多品类扩展 | Phase 5 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-C1-01 | 全部表使用 MergeTree 引擎 | MergeTree/ReplacingMergeTree | MergeTree | 数据源唯一(D_DATA)，不需要去重 | 2026-07-01 |
| 2 | D-C1-02 | 高频表按天分区/日频表按月分区 | 统一按天/混合 | 混合 | 高频表分区裁剪+日频表减少分区数 | 2026-07-01 |
| 3 | D-C1-03 | 排序键 symbol 前缀 | symbol前缀/时间前缀 | symbol前缀 | 回测主要查单只股票历史数据 | 2026-07-01 |
| 4 | D-C1-04 | tick_data/index_quote TTL 90天 | 永久保留/TTL归档 | TTL 90天 | 高频数据体积大，超期归档Parquet | 2026-07-01 |
| 5 | D-C1-05 | daily_kline 永久保留 | TTL/永久 | 永久 | 日线数据体积小且高频查询 | 2026-07-01 |
| 6 | D-C1-06 | calc_mode 二值(replay/preload) | 三值含hybrid/二值 | 二值 | C1行情数据无hybrid需求 | 2026-07-01 |
| 7 | D-C1-07 | market_type 字段预留硬边界品类 | 不预留/预留字段 | 预留字段 | 对接母蓝图 §8.2 硬边界 | 2026-07-01 |
| 8 | D-C1-08 | daily_kline 先删后插(非UPSERT) | ReplacingMergeTree/先删后插 | 先删后插 | MergeTree不支持UPSERT | 2026-07-01 |
| 9 | D-C1-09 | 回测分层加载(热层/温层) | 全量加载/分层 | 分层 | 对接母蓝图 §7.1 内存预算64G | 2026-07-01 |
| 10 | D-C1-10 | ClickHouse 新建 INFRA-DB-006 | 复用duckdb/新建ClickHouse | 新建ClickHouse | 母蓝图 §8.1 直接上目标引擎 | 2026-07-01 |

### 变更记录

### v1.0.1 (2026-07-05) 状态同步修复
- construction_progress: not_started → partially_implemented（ClickHouse 已于 2026-07-01 部署）
- 解除所有"ClickHouse 未部署"前置阻塞描述
- market.duckdb 迁移描述修正：残留文件已于 2026-07-05 删除（524KB，无有价值数据）
- §13.2 模板 database 字段修正：c1_market_clickhouse → c1_market（与 DDL 一致）
- #ARCH-048 关联：Redis/EventStore 架构哲学切换裁决

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| C1 market_clickhouse | 行情仓库，存 L1 标准化行情数据 | — | 业务数据库仓库层之一 |
| MergeTree | ClickHouse 引擎，追加写不去重 | ReplacingMergeTree | C1 数据源唯一不需要去重 |
| replay | 回测时逐笔实时重算（母蓝图 §7.5） | preload | replay 用于 tick/index 高频原料 |
| preload | 回测时预加载到内存（母蓝图 §7.5） | replay | preload 用于日线/指标等成品 |
| 热层/温层 | 回测分层加载（母蓝图 §7.1） | 冷层 | C1 无冷层（冷层属 C3） |
| calc_mode | 品类回测计算模式（母蓝图 §7.5） | — | replay/preload/hybrid |
| category_id | 品类标识（母蓝图 §6 第1层） | — | C1 的 8 个品类唯一标识 |
| DDL-as-Code | 表结构 Python 类定义（母蓝图 §6 第2层） | — | 版本可控、AI 可生成 |
| 分区裁剪 | ClickHouse 按分区键跳过无关分区 | — | 提升查询性能 |
| market_type | 市场类型字段，预留硬边界品类 | — | DEFAULT 'A_share'，港股/美股 enabled=false |
| 母蓝图 | 业务数据库顶层架构设计书 ARCH-BIZDB-001 | — | C1 的上游设计真源 |
| INFRA-DB-006 | ClickHouse 基础设施（新建） | INFRA-DB-005(已删除duckdb) | C1 施工前置条件 |
