---
module_id: VIEW-CODE-WIKI-02-DATA-LAYER
title: "02 · 数据库架构全景"
doc_type: architecture_view
rule_form: declarative
status: active
version: 1.0.0
date: 2026-07-23
owner: ZephyrAlpha-Owner
ttl: permanent
language: zh
created_by: agent
---

# 02 · 数据层架构全景（Database Layer）

> **文档性质**：只读架构审查（code wiki），非施工蓝图。
> **生成方式**：静态代码/DDL/配置审查 + **只读实库探测**（2026-07-22，本次会话实测）。
> **实测范围**：ClickHouse（TCP 9000，`settings={'readonly':1}`）、PostgreSQL depgraph（psycopg2 只读 SELECT）、本地 SQLite 文件（`mode=ro` URI）均已连通并取数；未执行任何写入/DDL/破坏性操作。
> **覆盖率声明**：ClickHouse 3 库 101 张表 100% 覆盖（逐表引擎/分区键/排序键/行数实测）；PostgreSQL 46 张表 100% 表名覆盖、核心表列结构覆盖；SQLite governance.db 38 张表 100% 表名覆盖、核心表 DDL 覆盖。

## 目录

- [1. 数据库角色分工矩阵](#1-数据库角色分工矩阵)
- [2. 连接管理与服务化封装](#2-连接管理与服务化封装)
- [3. 数据表清单](#3-数据表清单)
  - [3.1 ClickHouse（业务行情/基本面仓库，101 表实测）](#31-clickhouse业务行情基本面仓库101-表实测)
  - [3.2 PostgreSQL depgraph（架构真源，46 表实测）](#32-postgresql-depgraph架构真源46-表实测)
  - [3.3 SQLite governance.db（治理运行时，38 表实测）](#33-sqlite-governancedb治理运行时38-表实测)
  - [3.4 其他 SQLite / 本地存储文件](#34-其他-sqlite--本地存储文件)
- [4. 读写路径与治理规则](#4-读写路径与治理规则)
- [5. depgraph（PostgreSQL）与业务库的边界](#5-depgraphpostgresql与业务库的边界)
- [6. 已知漂移与风险观察](#6-已知漂移与风险观察)
- [7. 验证方法与证据附录](#7-验证方法与证据附录)

---

## 1. 数据库角色分工矩阵

项目数据库清单真源为 `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`（INFRA-DB 条目）；二库职责划分见 `docs/03_modules/_cross_layer/database/blueprint.md`（SH-DB-001 v4.3.4）；业务库顶层分库设计见 `docs/03_modules/_cross_layer/database/business_data_architecture.md`（MOD-ARCH-BIZDB）。

| # | 数据库 | 引擎 | infra_id | 物理位置/端点 | 角色 | 实测状态 |
|---|--------|------|----------|---------------|------|---------|
| 1 | governance.db | SQLite (WAL) | INFRA-DB-001 | `data/databases/governance.db`（约 40 MB，SSoT 常量 `DB_PATH`，`src/zephyr/shared/io/paths.py:95`） | **治理运行时**：TaskCard 任务状态机、事件流、门禁记录、熔断状态、FLE 指标、审计 | ✅ 连通，38 表，schema v35，tasks 1736 行 |
| 2 | depgraph | PostgreSQL 16 | INFRA-DB-003 | `localhost:5432/depgraph`，配置 `config/.env.postgres` | **架构静态真源**：依赖图 nodes/edges/domains + decisiongraph + dataflowgraph + 各类 registry 缓存表 | ✅ 连通，46 表，schema v19，nodes 5506 / edges 7592 行 |
| 3 | c1_market | ClickHouse 26.6.1 | INFRA-DB-006 | Hyper-V VM `172.24.30.100:9000`(TCP) / `:8123`(HTTP)，配置 `config/.env.clickhouse` | **业务行情仓库**（回测数据底座）：K线/tick/板块/指数/期货/期权/港股/美股 | ✅ 连通，77 表，tick_data 约 143.2 亿行、kline_1min 约 38.7 亿行 |
| 4 | c3_fundamental | ClickHouse（同上实例） | （归入 INFRA-DB-006 注记"已创建 c0_meta/c1_market/c3_fundamental 三库"） | 同上 | **财务基本面仓库**：三大报表/股东/质押/新闻/预测 | ✅ 连通，23 表 |
| 5 | c0_meta | ClickHouse（同上实例） | 同上 | 同上 | **采集元数据**：fetch_perf 采集性能记录 | ✅ 连通，1 表（103 行） |
| 6 | DuckDB OLAP | DuckDB `:memory:` | INFRA-DB-004 | 内存模式 | **已退役**：`olap_engine.py` 于 2026-07-16 退役删除（ARCH-OLAP-RETIRE，`src/zephyr/governance/persistence/__init__.py:6-7`），被 ClickHouse 替代；业务行情 DuckDB Warm 层经 2026-07-13 用户裁定**暂缓开发**（`blueprint.md` §三层冷热架构定位） | ❌ 不存在（仅 commit gate 源码中提及 `duckdb.connect` 字样） |
| 7 | market.duckdb | DuckDB（文件） | 原 INFRA-DB-005 | 已删除 | **已废弃**：2026-07-01 废弃、2026-07-05 物理删除，8 张业务表迁移至 ClickHouse c1_market（`database_service.py:35` 注记） | ❌ 已删除 |
| 8 | Redis | Redis（未部署） | INFRA-CACHE-001 | — | **P2 未来蓝图**：Hot 层 <5ms 盘中推理缓存；`DatabaseService.get_redis_conn()` 抛 `NotImplementedError`（`database_service.py:174-179`），实盘交易启动前不开发 | ❌ 未实现（接口预留） |
| 9 | 向量库 | ChromaDB → FAISS 过渡期 | INFRA-DB-002 | `data/vector_db/` | 向量检索（VMS），非关系型，本文不展开 | 未实测 |
| 10 | 辅助 SQLite | SQLite | （未单独登记 INFRA-DB） | `data/integrator_jobs.db`、`data/integrator_progress.db`、`data/databases/session_continuity.db`、`data/events.db`（EventStore 默认路径） | 数据源调度/进度/会话交接/审计事件 | ✅ 前三个已实测（见 §3.4） |

**分库原则（母蓝图 MOD-ARCH-BIZDB）**：治理库（governance.db + depgraph，不动）与业务库分离；业务库按引擎 + 生命周期分库——ClickHouse 当仓库（C1~C4 规划）、SQLite 管事务（L4 trading.db 规划）、Neo4j 管图谱（G2 规划）、内存工作台管计算。其中 C2 indicator / C4 backtest / G2 Neo4j / L4 trading.db 子蓝图在 `business_data_architecture.md` frontmatter 中登记为 `Pending/not_started`，且 `docs/03_modules/_cross_layer/database/sub_blueprints/` 下目前仅有 `c1_market_clickhouse.md` 与 `index.md`——**除 C1/C3（fundamental）外均未落地**。

**冷热分层定位**（`blueprint.md` §三层冷热架构定位，含 2026-07-13 用户裁定）：

| 层 | 组件 | 状态 |
|----|------|------|
| Hot | Redis | 暂缓，实盘交易启动前开发 |
| Warm | ClickHouse（在用）+ DuckDB/Parquet（暂缓） | ClickHouse 已部署；DuckDB Warm 层暂缓（触发条件：回测排队/CH 明显变慢） |
| Cold | E 盘 Parquet 归档 | 架构预留、暂缓（触发条件：D 盘存储紧张） |

---

## 2. 连接管理与服务化封装

### 2.1 统一入口：DatabaseService（MOD-INF-002）

真源 `src/zephyr/infrastructure/database_service.py`；`src/zephyr/governance/persistence/database_service.py` 已收敛为**纯 re-export**（AI-14 审计 P1 修复，消除双真源，该文件头部 `[MODIFY-GUARD] 禁止修改`）。

| 方法 | 目标 | 关键机制 | 证据 |
|------|------|---------|------|
| `get_governance_conn(read_only=False)` | SQLite governance.db | 双连接机制：读写/只读独立连接；只读连接 `PRAGMA query_only=1`；复用 `sqlite_factory.get_db_connection()` 保证 PRAGMA 基线一致；`_lock` 保护 lazy init | `database_service.py:102-126` |
| `get_depgraph_conn(read_only=False)` | PostgreSQL depgraph | **per-thread 连接**（`threading.local`，因 psycopg2 连接非线程安全，`database_service.py:93-97`）；`cursor_factory=RealDictCursor` 兼容 dict 用法；只读连接 `SET default_transaction_read_only=on`；`_live_pg_conns` 注册表供 `close_all()` 统一关闭 | `database_service.py:128-151` |
| `get_clickhouse_conn()` | ClickHouse c1_market | `clickhouse_driver.Client`，**强制 `settings={'readonly': 1}`**；配置委托 `ch_config.load_ch_config()` | `database_service.py:153-172` |
| `get_redis_conn()` | Redis | 抛 `NotImplementedError`（预留） | `database_service.py:174-179` |
| `health_check()` | 三库 | 逐库 `SELECT 1`，返回 `{"governance","depgraph","clickhouse": bool}` | `database_service.py:181-208` |
| `close_all()` | 全部 | 逐连接独立 try/except（异常隔离）；ClickHouse 显式 `disconnect()` 避免 ResourceWarning | `database_service.py:210-246` |

CRUD 方法（get_task/create_task/get_node 等 9 个）已抽取到 `zephyr.shared.database.database_crud_mixin.DatabaseCRUDMixin`，`DatabaseService` 继承之（`database_service.py:79-85, 248-253`）。

### 2.2 各引擎连接配置真源

- **SQLite**：`zephyr.shared.io.sqlite_factory`（`_PRAGMAS/_apply_pragmas/get_db_connection` 的 canonical 文件，`sqlite_schema.py:425-434` re-export）。PRAGMA 基线（KBG-0030 §4.3）：`journal_mode=WAL, synchronous=NORMAL, foreign_keys=ON, busy_timeout=5000, temp_store=MEMORY, wal_autocheckpoint=4096`（`sqlite_schema.py:46-53`）。
- **PostgreSQL**：唯一入口 `zephyr.governance.depgraph_schema.get_depgraph_pg_connection()`，使用 `psycopg2.pool.ThreadedConnectionPool` 池化（`depgraph_schema.py:94-95`）。配置优先级：**`DATABASE_URL` 环境变量 > `config/.env.postgres`**（§5.34.5，`depgraph_schema.py:122-159`）；必需 5 键（HOST/PORT/DB/USER/PASSWORD）+ 可选 4 键 reader/writer 角色凭证（裁定 #ARCH-DEPGRAPH_ACCESS_CONTROL 分级访问，`depgraph_schema.py:105-119`）；密码走 SecretProvider 真源 `get_secret_from_file`。
- **ClickHouse**：**单真源加载器 `zephyr.data.ch_config`**（裁定 #ARCH-CH-017/#ARCH-CH-019）——`config/.env.clickhouse` 是唯一真源；`os.environ > 文件 > 抛 CHConfigError`（fail-closed，禁止任何硬编码 IP 默认值）；`ensure_ch_env_loaded()` 幂等加载（`ch_config.py:63-96`）；`load_ch_config()` 返回 host/port/http_port/user/password/database（`ch_config.py:99-133`）。

### 2.3 ClickHouse 读写分层（D_DATA 域）

- **写入 `zephyr.data.ch_writer`**（`src/zephyr/data/ch_writer.py`，MATURITY=production）：**二级传输降级架构**——`query/delete_where` 走 clickhouse-driver TCP 9000；`write_tsv` 走 HTTP API 8123 → 本地落盘兜底（`local_replay`，CH 不可达时写本地 TSV 待回灌，裁定 #ARCH-CH-013）。TCP 失败 15s 冷却（`_TCP_COOLDOWN_SEC`，`ch_writer.py:83`）；三把锁分工（`_cache_lock → _connect_lock → _ch_lock` 单向锁序，`ch_writer.py:85-92`）；`WriteOutcome/WriteDisposition` 三态（ch_committed/local_durable/not_durable）**禁止把本地持久化伪装成 CH 已提交**（`ch_writer.py:95-113`）。
- **主动 WAL `zephyr.data.wal_writer`**：数据先落本地 WAL 段文件、后台 drain 线程异步排空到 CH；WAL 容量上限 2GB，70% warning / 90% critical 背压阻断写入（`wal_writer.py:8,17-19,64-65`）。
- **读取 `zephyr.data.ch_reader`**（裁定 #ARCH-CH-007）：统一读取层，对 ReplacingMergeTree 表**自动注入 FINAL 关键字**强制查询时去重（ReplacingMergeTree 去重是异步后台 merge，不加 FINAL 会读到重复行）；`system.*` 表与引擎查询失败时不注入（`ch_reader.py:57-91`）。
- **幂等性策略**（`ch_writer.py` §7.3）：ReplacingMergeTree → 直接 INSERT（后台合并去重）；MergeTree → 写前 `DELETE WHERE`；引擎探测 `get_table_engine()/is_replacing_engine()` 辅助决策（裁定 #ARCH-CH-002）。

---

## 3. 数据表清单

### 3.1 ClickHouse（业务行情/基本面仓库，101 表实测）

**实测口径**：`SELECT database, name, engine, partition_key, sorting_key, total_rows FROM system.tables`（只读，2026-07-22）。注册表真源 `docs/03_modules/_cross_layer/database/business_data_categories.yaml`（品类注册表：category_id/engine/table/schema_file/data_type/lifecycle/sla_level/enabled/calc_mode/data_source，新增品类 = 加 YAML 记录不改代码）。

#### c1_market（77 表，全部 ReplacingMergeTree）

按类别分组；行数为实测 `total_rows`（含未合并重复，仅供参考量级）。

| 表名 | 分区键 | 排序键（ORDER BY） | 行数（实测） | 备注 |
|------|--------|--------------------|-------------:|------|
| **A股 K线** | | | | |
| kline_daily | toYYYYMM(trade_date) | symbol, trade_date | 34,664,504 | 日K前复权；schema SSoT `schemas/categories/market_kline_daily.py` |
| kline_daily_hfq | toYYYYMM(trade_date) | symbol, trade_date | 18,203,140 | 日K后复权 |
| kline_weekly | toYYYYMM(trade_date) | symbol, trade_date | 3,811,726 | |
| kline_weekly_hfq | toYYYYMM(trade_date) | symbol, trade_date | 3,800,031 | |
| kline_monthly | toYYYYMM(trade_date) | symbol, trade_date | 923,176 | |
| kline_monthly_hfq | toYYYYMM(trade_date) | symbol, trade_date | 919,705 | |
| **A股分钟K线**（trade_time 分区） | | | | |
| kline_1min | toYYYYMM(trade_time) | symbol, trade_time | 3,867,233,437 | 全库第二大表 |
| kline_5min | toYYYYMM(trade_time) | symbol, trade_time | 979,419,898 | |
| kline_15min | toYYYYMM(trade_time) | symbol, trade_time | 256,545,404 | |
| kline_30min | toYYYYMM(trade_time) | symbol, trade_time | 127,459,548 | |
| kline_60min | toYYYYMM(trade_time) | symbol, trade_time | 63,974,094 | |
| **逐笔/快照** | | | | |
| tick_data | toYYYYMM(trade_date) | market_type, symbol, trade_date, timestamp, price | 14,324,240,136 | **全库最大表**；8 种 market_type；schema SSoT `schemas/categories/market_tick.py`；排序键含 price（#ARCH-CH-020 事故背景，见 AGENTS.md RULE-DATA-OPS） |
| auction_snapshot | toYYYYMM(trade_date) | symbol, trade_date | 20,805 | 集合竞价快照；`schemas/categories/market_auction.py` |
| auction_book | toYYYYMM(trade_date) | symbol, trade_date, timestamp | 5,201 | 集合竞价簿（注册表标 enabled=false 预留，但表已建且有少量数据）；`schemas/categories/market_auction_book.py` |
| index_quote | toYYYYMMDD(trade_date) | symbol, trade_date, timestamp | 32,883 | 指数 3 秒快照（日级分区，全库唯一）；`schemas/categories/market_index.py` |
| realtime_snapshot | toYYYYMM(snapshot_time) | snapshot_time, symbol | 0 | 预留空表（enabled=false） |
| **ETF/LOF** | | | | |
| kline_etf_1min / 5min / 15min / 30min / 60min | toYYYYMM(trade_date) | symbol, trade_time | 355,310,352 / 68,799,500 / 22,958,101 / 11,463,273 / 5,701,311 | |
| kline_lof_1min / 5min / 15min / 30min / 60min | toYYYYMM(trade_date) | symbol, trade_time | 183,023,614 / 36,435,325 / 12,064,816 / 6,037,413 / 3,035,079 | |
| etf_list | （无分区） | (etf_code) | 1,764 | 元数据 |
| etf_benchmark | （无分区） | (index_code) | 732 | |
| etf_nav | toYYYYMM(trade_date) | trade_date, symbol | 112 | |
| lof_list | （无分区） | (code) | 361 | |
| **可转债** | | | | |
| kline_cb | toYYYYMM(trade_date) | trade_date, symbol | 4,611 | |
| convertible_bond_list | （无分区） | (bond_code) | 1,142 | |
| convertible_bond_iv | toYYYYMM(trade_date) | symbol, trade_date | 260,501 | `schemas/categories/market_cb_iv.py` |
| **指数** | | | | |
| kline_index | toYYYYMM(trade_date) | symbol, trade_date | 3,072,935 | 指数日K |
| index_list | （无分区） | (ts_code) | 2,430 | |
| index_constituent | toYYYYMM(trade_date) | index_code, trade_date | 59,583 | |
| index_weight | toYYYYMM(trade_date) | trade_date, index_code, symbol | 3,700 | |
| market_index_meta | （无分区） | (sector_code) | 50 | 市场宏观指标 |
| us_index | toYYYYMM(trade_date) | symbol, trade_date | 22,460 | |
| **期货/期权** | | | | |
| kline_futures | toYYYYMM(trade_date) | symbol, period, trade_date | 3,138,932 | 主表（period 列区分周期） |
| futures_kline_qmt | toYYYYMM(trade_date) | symbol, trade_date | 1,162 | 与 kline_futures 功能重叠（注册表已标注主从关系） |
| futures_position | toYYYYMM(trade_date) | symbol, trade_date | 492 | `schemas/categories/market_futures_position.py` |
| futures_term_structure | toYYYYMM(trade_date) | symbol, trade_date | 34,119 | `schemas/categories/market_futures_term.py` |
| option_kline | toYYYYMM(trade_date) | trade_date, symbol | 1,079 | |
| option_greeks | toYYYYMM(trade_date) | trade_date, symbol | 8,876 | |
| option_iv_surface | toYYYYMM(trade_date) | underlying, trade_date, strike, expiry | 58,498 | `schemas/categories/market_option_iv.py` |
| **港股/美股** | | | | |
| kline_hk_daily | toYYYYMM(trade_date) | symbol, trade_date | 1,614,661 | 港股主表（2015 起） |
| hk_kline | toYYYYMM(trade_date) | trade_date, symbol | 1,604,167 | 补充源（2024 起，与主表功能重叠） |
| hk_stock_list | （无分区） | (code) | 4,688 | |
| hk_trade_calendar | （无分区） | (cal_date) | 17,167 | |
| hk_connect_flow | toYYYYMM(trade_date) | trade_date, channel | 4,052 | 沪深港通资金流 |
| kline_us_daily | toYYYYMM(trade_date) | symbol, trade_date | 167,195 | |
| **板块/行业** | | | | |
| concept_board | （无分区） | (board_code) | 745 | |
| concept_board_constituent | （无分区） | board_code, symbol | 239,663 | |
| concept_sector | （无分区） | (sector_code) | 388 | |
| sector_meta | （无分区） | sector_code, trade_date | 90 | |
| sector_list | toYYYYMM(trade_date) | sector_name, symbol, trade_date | 15,609 | |
| sector_constituent | toYYYYMM(update_date) | sector_code, stock_code | 84,451 | 880xxx 板块成分（tqcenter） |
| kline_sector | toYYYYMM(trade_date) | code, trade_date | 17,200 | |
| kline_sector_880 | (period, toYYYYMM(trade_date)) | period, sector_code, timestamp | 14,389 | |
| kline_sector_intraday | toYYYYMMDD(trade_date) | code, period, trade_date | 396,592 | 分钟级（日分区） |
| sector_snapshot | toYYYYMM(trade_date) | sector_code, timestamp | **0** | 注册表 enabled=true 但实测 0 行（见 §6）；`schemas/categories/market_sector_snapshot.py` |
| industry_class | （无分区） | (symbol) | 40,602 | 申万/证监会分类 |
| **基本面引用/资金** | | | | |
| adj_factor | toYYYYMM(trade_date) | symbol, trade_date | 21,055,920 | 复权因子 |
| daily_valuation | toYYYYMM(trade_date) | symbol, trade_date | 8,841,897 | PE/PB/股息率 |
| money_flow | toYYYYMM(trade_date) | symbol, trade_date | 621,716 | |
| margin_trading | toYYYYMM(trade_date) | trade_date, symbol | 1,154,636 | |
| dragon_tiger | toYYYYMM(trade_date) | trade_date, symbol | 169,980 | |
| block_trade | toYYYYMM(trade_date) | trade_date, symbol | 163,352 | |
| block_trade_detail | toYYYYMM(trade_date) | trade_date, symbol | 861 | |
| limit_up_down | toYYYYMM(trade_date) | trade_date, symbol | 2,555 | |
| st_stock_list | toYYYYMM(trade_date) | trade_date, symbol | 2,139 | |
| stock_indicator | toYYYYMM(trade_date) | trade_date, symbol | 63,654 | |
| macro_data | toYYYYMM(report_date) | indicator_name, report_date | 285,322 | |
| edb_data | toYYYYMM(report_date) | indicator_code, report_date | 0 | 预留（enabled=false） |
| **元数据** | | | | |
| stock_list | （无分区） | (ts_code) | 5,534 | A股全量列表 |
| trade_calendar | （无分区） | exchange, cal_date | 13,162 | |

**注册表登记但实测不存在的 4 张表**（均为占位/预留）：`margin_trading_qmt`、`dragon_tiger_qmt`、`block_trade_qmt`（QMT 占位，裁定 #ARCH-CH-024 Phase 5 要求占位表也注册）、`l2_tick`（Level2 预留）。实测线上不存在但注册表 `enabled: true` 的 QMT 占位三张属于"注册先行、建表未做"。

**DDL-as-Code**：`schemas/categories/` 下 10 个 schema 文件（market_tick / market_kline_daily / market_auction / market_auction_book / market_index / market_option_iv / market_cb_iv / market_futures_position / market_futures_term / market_sector_snapshot），部署脚本 `scripts/ch/apply_market_tables_ddl.py`（apply + verify，verify 比对 `system.tables` 引擎与选型矩阵，退出码 0/1/2；`apply_market_tables_ddl.py:236-280`）。其余 67 张表无 schema 文件（注册表 `schema_file: null`），DDL 由历史采集脚本/手动建立——**schema_file 覆盖率 10/77 ≈ 13%**。

#### c3_fundamental（23 表）

| 表名 | 引擎 | 分区键 | 排序键 | 行数（实测） |
|------|------|--------|--------|-------------:|
| balance_sheet | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 334,521 |
| income_statement | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 340,959 |
| cashflow_statement | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 610,460 |
| financial_indicator | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 348,149 |
| audit_opinion | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 192,020 |
| earnings_forecast | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 251,164 |
| analyst_forecast | **MergeTree** | toYYYYMM(report_date) | symbol, report_date | 11,232 |
| disclosure_plan | **MergeTree** | toYYYYMM(report_period) | symbol, report_period | 611,252 |
| dividend | ReplacingMergeTree | toYYYYMM(dividend_year) | symbol, dividend_year, announce_date | 115,528 |
| equity_pledge_detail | **MergeTree** | toYYYYMM(announce_date) | symbol, announce_date, shareholder_name | 619,346 |
| equity_pledge_summary | ReplacingMergeTree | toYYYYMM(end_date) | symbol, end_date | 1,723,185 |
| express_report | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, announce_date | 57,313 |
| industry_class_suppl | **MergeTree** | （无分区） | (symbol) | 10,403 |
| main_business | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, business_source | 2,090,862 |
| news_data | ReplacingMergeTree | toYYYYMM(publish_time) | news_id, publish_time | 10,161,482 |
| repurchase | ReplacingMergeTree | toYYYYMM(announce_date) | symbol, announce_date | 5,393 |
| restricted_shares | **MergeTree** | toYYYYMM(unlock_date) | symbol, unlock_date, shareholder_name | 22,786,863 |
| rights_issue | **MergeTree** | toYYYYMM(announce_date) | symbol, announce_date, type | 161,548 |
| share_change | **MergeTree** | toYYYYMM(announce_date) | symbol, announce_date | 337,860 |
| share_unlock | **MergeTree** | toYYYYMM(unlock_date) | symbol, unlock_date | 28,524 |
| shareholder_count | ReplacingMergeTree | toYYYYMM(end_date) | symbol, end_date | 501,972 |
| top10_shareholders | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, shareholder_name | 1,444,792 |
| top10_circulating_shareholders | ReplacingMergeTree | toYYYYMM(report_period) | symbol, report_period, shareholder_name | 2,139,709 |

⚠️ **8 张表为裸 MergeTree**（非 ReplacingMergeTree）：analyst_forecast、disclosure_plan、equity_pledge_detail、industry_class_suppl、restricted_shares、rights_issue、share_change、share_unlock。这些表不受 `ch_reader` FINAL 自动注入保护（`inject_final` 只对 ReplacingMergeTree 注入，`ch_reader.py:85-86`），重跑采集会产生重复行，依赖写前 DELETE 幂等路径。

#### c0_meta（1 表）

| 表名 | 引擎 | 分区键 | 排序键 | 行数 |
|------|------|--------|--------|-----:|
| fetch_perf | ReplacingMergeTree | （无分区） | source, capability, test_date | 103 |

### 3.2 PostgreSQL depgraph（架构真源，46 表实测）

**实测口径**：`information_schema.tables`（schema=public，2026-07-22）。蓝图 `blueprint.md` 记载"28 表"，实测 **46 表**——因 PG 单实例承载了 depgraph + decisiongraph + dataflowgraph + 多类 registry 缓存 + 系统扩展表（见 §5 边界与 §6 漂移）。

**Schema 管理**：Python 真源 `src/zephyr/governance/depgraph_schema.py`（`_DDL_*` 常量做列级 drift 校验；`init_db()` 仅验证不执行 DDL）；**DDL 执行真源为 SQL 文件** `scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql`（+ `03_create_decision_schema.sql` / `03_create_dataflow_schema.sql` / `04_create_roles.sql` 等）；实测 `_schema_version` = v19。变更协议：先改 `_DDL_*`/SQL 文件 → git commit → `apply_depgraph.py` 迁移 → `verify_schema_health.py` 校验；**禁止直连 PG 手动 DDL**（`blueprint.md` §depgraph Schema 变更门禁）。

| 分组 | 表（实测） | 说明 |
|------|-----------|------|
| depgraph 核心 | nodes, edges, nodes_metadata, edges_metadata, domains, domain_dependencies, domain_events, contracts, rule_bindings, arch_constraints, arch_directory_tree, arch_path_mappings, _schema_version | `depgraph_schema.py:247-539`；nodes 5506 行 / edges 7592 行 / domains 63 行 / rule_bindings 73 行（实测） |
| depgraph 扩展/治理 | gates, governance_audit_logs, cross_registry_rules, dep_cycles, dep_import_cycles, nodes_archive_module_lifecycle, domain_mapping, domain_naming_rules, hard_boundaries | gates 为 YAML SSoT 只读表（与 governance.db 的 gate_runs 同名异构，`sqlite_schema.py:145-148` 注记） |
| registry/资产缓存 | registries, infrastructure_components, interface_contracts, config_assets, service_assets, data_source_apis, data_source_assets, model_capabilities, field_vocabularies, derived_identifier_registry, blueprint_links, business_streams | RULE-REGISTRY 体系（31 个 registry 同步缓存，RULE-SSOT：规则数据 YAML→DB 单向同步） |
| decisiongraph | decision_tracks, decision_layers, decision_nodes, decision_edges | `decisiongraph_schema.py`；decision_nodes 214 行（实测）；与 depgraph 共库不同表前缀，写锁 `pg_advisory_lock(424244)`（`blueprint.md` §decisiongraph） |
| dataflowgraph | dataflow_datasets, dataflow_jobs, dataflow_runs, dataflow_edges, dataflow_datasets_metadata, dataflow_jobs_metadata | `dataflowgraph_schema.py`；dataflow_datasets 14 行（实测） |
| 系统扩展 | pg_stat_statements, pg_stat_statements_info | `01_create_extensions.sql` 安装的监控扩展 |

核心表结构（`depgraph_schema.py` 行号）：

- `nodes`（L247-289）：`node_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY`，28 列（domain_id FK→domains、node_type、blueprint_id、build_status、change_policy 等），7 个索引（L542-549）。
- `edges`（L291-324）：`edge_id BIGINT ... IDENTITY PRIMARY KEY`，19 列（from_node_id/to_node_id/dep_type/cross_domain 等）。
- `nodes_metadata`/`edges_metadata`（L326-378）：以 `path` / `(from_path, to_path, dep_type)` 为主键的元数据镜像表。
- `domains`（L380-408）：`domain_id TEXT PRIMARY KEY` + CHECK `domain_id ~ '^D_[A-Z][A-Z0-9_]*$'`（v15，裁定 #ARCH-target_layer_v1.0.0）。
- `contracts` / `rule_bindings` / `arch_constraints` / `arch_directory_tree` / `arch_path_mappings`：L440-528。
- 读侧有只读触发器保护（verify_schema_health.py 4 校验之一，`blueprint.md` §变更门禁）。

### 3.3 SQLite governance.db（治理运行时，38 表实测）

**实测口径**：`data/databases/governance.db`（`mode=ro`，2026-07-22），`_schema_version` = **v35**，tasks 1736 行。DDL 真源 `src/zephyr/governance/persistence/sqlite_schema.py`（`_MIGRATIONS` 版本化迁移链 v1→v35，`init_db()` 幂等）。

| 分组 | 表（实测） | 说明 |
|------|-----------|------|
| 任务系统 | tasks, task_files, task_events, task_snapshots, task_reviews | tasks：10 状态机 + TaskCard 40+ 列（`sqlite_schema.py:76-118` + v2~v30 ALTER 链）；task_events 为 Event Sourcing 事件流（UUID PK + seq/prev_hash 完整性链，v19/v31/v32）+ 部分唯一索引 `idx_te_one_claim_per_task`（v21，原子争抢）；task_snapshots 加速 replay（DW-0005） |
| 事件/门禁 | events, gate_runs, gate_decisions, gates | events：DeferredQueue 事件流（`sqlite_schema.py:124-139`）；gate_runs：门禁运行记录（v15 改名避同名异构）；`gates` 为 v34 测试兼容表（`sqlite_schema.py:951-962`） |
| 熔断/事务 | circuit_breaker_state, tx_idempotency | CBG 三态熔断（L164-178）；ATM 事务幂等去重（L226-236） |
| FLE 反馈环 | fle_metrics, fle_alerts, fle_dispatch_log | CT-FLE-DB-001（v22，L265-317） |
| 审计/漂移/修复 | audit_entries, audit_summary, drift_audit_findings, drift_events, drift_scan_results, integrity_records, judgment_records, rule_enforcement_log, reconcile_execution_log, scan_results | 由治理/审计/自动修复各子系统运行时创建（非 sqlite_schema.py `_MIGRATIONS` 内，属运行时建表，覆盖率说明见下） |
| 成本/用量 | costs, usage_records, fix_budget_consumption | CostTracker / 预算执行 |
| 自动修复 | fix_compliance, fix_idempotency, fix_patterns, fix_records | AutoFixEngine 持久化 |
| 其他 | domains, f5_state, knowledge, ke_tombstones, slow_queries, _schema_version, sqlite_sequence | `domains` 为历史残留（v30 已删 tasks.domain_id FK）；`knowledge`/`ke_tombstones` 为 v34/v35 测试兼容表（KBG 已移除）；slow_queries 慢查询（v7） |

视图（DDL 定义，`sqlite_schema.py:367-422`）：`event_log`（tasks×events JOIN 审计视图）、`v_active_tasks`（活跃任务快照）、`v_recent_sessions`（最近 10 session 统计）。

**覆盖率说明**：38 张实测表中，`sqlite_schema.py` `_MIGRATIONS` 直接覆盖约 18 张（tasks/events/gate_runs/gates/task_files/task_events/task_snapshots/task_reviews/circuit_breaker_state/tx_idempotency/slow_queries/fle_×3/knowledge/ke_tombstones/gate_decisions/_schema_version）；其余约 20 张（audit_*/drift_*/fix_*/costs/usage_records/integrity_records/judgment_records/rule_enforcement_log/reconcile_execution_log/scan_results/domains/f5_state）由各治理子系统模块自建，未纳入统一迁移链——治理上属"分散建表"，是潜在 SSoT 薄弱点（§6）。

### 3.4 其他 SQLite / 本地存储文件

| 文件 | 引擎 | 表 | 角色 | 证据 |
|------|------|----|------|------|
| `data/integrator_progress.db` | SQLite (WAL) | task_progress, task_runs | 数据源集成器断点续传进度（`progress_store.py:8,50`，`check_same_thread=False + threading.Lock` 并发保护） | 实测 2068 KB |
| `data/integrator_jobs.db` | SQLite | apscheduler_jobs | APScheduler 任务持久化 | 实测 36 KB |
| `data/databases/session_continuity.db` | SQLite | handoffs | 会话交接（handoff 协议） | 实测 12 KB |
| `data/events.db`（默认路径） | SQLite (WAL+SHA256) | （EventStore 自建） | 不可篡改审计事件日志（RI-13，`src/zephyr/infrastructure/event_store.py:123-150`） | **本次实测未发现该文件**——EventStore 惰性建库（auto_init），路径为默认值，尚未被触发创建 |
| `data/governance.db`（data/ 根目录） | SQLite | （空） | **0 KB 残留空文件**（真实库在 `data/databases/governance.db`，SSoT `DB_PATH`） | 实测 0 表，建议清理 |
| `data/local_fallback/`、`data/raw/` | TSV/文件 | — | CH 不可达时的本地落盘兜底目录（ch_writer/local_replay 回灌源） | `ch_writer.py` [INVARIANTS] |
| `data/backups/`、`data/warehouse/` | 文件/Parquet | — | governance.db 自动备份（7 天日备 + 4 周末备）/ Parquet 冷归档预留 | `blueprint.md` §产出物 |

---

## 4. 读写路径与治理规则

### 4.1 读写路径总览

```
写入：
  数据源采集(D_DATA) → provider_base.FetchResult → ch_writer.write_result()
      → HTTP 8123 TSV INSERT → ClickHouse c1_market/c3_fundamental
      └─ CH 不可达 → local_replay 本地 TSV 落盘 → 待回灌
      （或）wal_writer：先落 WAL 段文件 → 后台 drain 排空到 CH（容量背压 70%/90%）
  治理写入 → TaskRepository/BaseRepo → DatabaseService.get_governance_conn() → governance.db
  架构写入 → apply_depgraph.py 等 → get_depgraph_pg_connection() → PG depgraph
读取：
  回测/分析 → ch_reader.query()（自动 FINAL 注入）→ ClickHouse（只读）
  治理查询 → DatabaseService.get_governance_conn(read_only=True)（PRAGMA query_only=1）
  架构查询 → DatabaseService.get_depgraph_conn(read_only=True)（default_transaction_read_only=on）
```

### 4.2 治理规则清单（硬约束）

| 规则 | 内容 | 真源 |
|------|------|------|
| 禁止裸连接 | 业务数据库统一走 `DatabaseService`；**禁止裸 `duckdb.connect`**（AGENTS.md 基础设施层表）；业务库查询 MUST 显式 `read_only=True`（project_memory 硬约束，`database_service.py:112-113,137-138`） | AGENTS.md；database_service.py |
| NO-BARE-SQL gate | SQL 常量集中化（`SQL_*`/`_SQL_*` 前缀豁免），commit gate `src/zephyr/gov_enforcement/commit_gates/bare_sql_gate.py` 强制 | bare_sql_gate.py；ch_writer.py:74-77 |
| ClickHouse 只读连接 | `DatabaseService.get_clickhouse_conn()` 强制 `settings={'readonly': 1}` | database_service.py:170 |
| CH 配置 fail-closed | 配置缺失抛 `CHConfigError`，禁止硬编码 localhost/IP 默认值 | ch_config.py:8,99-120 |
| FINAL 自动注入 | ReplacingMergeTree 查询必须经 `ch_reader`（裁定 #ARCH-CH-007/#ARCH-CH-004 教训） | ch_reader.py:17-34 |
| RULE-DATA-OPS | 破坏性 DB 操作（DELETE/REPLACE PARTITION/TRUNCATE/ALTER DELETE/OPTIMIZE FINAL/INSERT GROUP BY+REPLACE）前三步验证：必要性/真实性（全字段 GROUP BY 查重，禁止用排序键近似）/可逆性（无备份禁止执行）；标准化工具 `scripts/governance/data_quality/check_tick_duplication.py` | AGENTS.md RULE-DATA-OPS（#ARCH-CH-020，2026-07-16 误删 21 个月 tick 数据事故治本） |
| RULE-SSOT | **规则数据**（trae_*.yaml/契约/门禁/注册表）真源在 YAML，`sync_yaml_to_depgraph.py` 单向同步到 DB（DB 只读缓存）；**架构数据**（depgraph.nodes/edges、decision_*、dataflow_*）真源在 PG DB，`apply_*.py` 直接写入 | AGENTS.md RULE-SSOT；trae_062 |
| DDL-as-Code | CH 表 DDL 真源在 `schemas/categories/*.py`；depgraph DDL 真源 `depgraph_schema.py` + `migrate_sqlite_to_pg/*.sql`；变更先改代码 → commit → 迁移 → verify；禁止直连手动 DDL | apply_market_tables_ddl.py:8；blueprint.md §变更门禁 |
| depgraph 注册前置 | 新模块施工前 MUST 登记 depgraph 设计态（RULE-DEPGRAPH）；新 .py 文件 commit 时有 NEW-FILE-DEPGRAPH-ENFORCEMENT gate | AGENTS.md RULE-DEPGRAPH |
| 写入诚实性 | `WriteOutcome` 三态禁止把本地落盘伪装成 CH 已提交 | ch_writer.py:95-113 |

---

## 5. depgraph（PostgreSQL）与业务库的边界

**边界原则：depgraph PG 是"关于系统的数据"，ClickHouse/SQLite 业务库是"系统处理的数据"——两者零业务重叠、零同步需求**（`blueprint.md` §二库职责划分："2库职责不重叠，无同步需求"）。

| 维度 | depgraph（PostgreSQL 16） | 业务库（ClickHouse c0/c1/c3 + governance.db） |
|------|--------------------------|-----------------------------------------------|
| 数据性质 | 架构静态真源 + 规则数据只读缓存：代码模块依赖（nodes/edges）、域/契约/规则绑定、decision/dataflow 图、31 个 registry 的 DB 缓存 | 治理运行时状态（tasks/events/gates/FLE/审计）与行情/基本面业务时序 |
| 写入方 | `apply_depgraph.py` / `generate_project_depgraph.py` / `sync_yaml_to_depgraph.py` / `apply_dataflowgraph.py` 等治理脚本 | TaskRepository、ch_writer、采集调度器 |
| 消费方 | commit gates、拓扑校验、蓝图同步、AI 能力反查 | 回测引擎、Dashboard、治理运行时 |
| 连接入口 | `get_depgraph_pg_connection()`（池化，reader/writer 角色分级凭证可选） | `DatabaseService`（SQLite 双连接 + CH readonly=1） |
| 共库例外 | decisiongraph（decision_* 4 表）与 dataflowgraph（dataflow_* 6 表）**与 depgraph 同实例同库**，靠表前缀区分、写锁区分（advisory lock 424242 vs 424244） | — |
| 配置真源 | `config/.env.postgres` / `DATABASE_URL` | `config/.env.clickhouse` / SQLite 文件路径 SSoT（paths.py） |

注意：**governance.db（SQLite）虽属"治理侧"，但与 depgraph PG 不同库**——它是运行时状态（高频小事务、嵌入式零部署），PG 是架构静态真源（复杂关系查询、MVCC 并发）；二库划分决策见 `blueprint.md`（"SQLite→PG 合并代价远大于收益"）。

---

## 6. 已知漂移与风险观察

1. **blueprint.md "depgraph 28 表" vs 实测 46 表**：PG 实例持续吸纳 registry 缓存/decision/dataflow 等新表，蓝图描述滞后（实测 46，含 2 张 pg_stat_statements 系统表）。
2. **business_data_categories.yaml 头注释计数滞后**：注释称"C1 76 条 / C3 21 条"，实测注册条目 C1 = 81（含 4 张占位/预留表）、C3 = 23；且 C1 的 `margin_trading_qmt`/`dragon_tiger_qmt`/`block_trade_qmt` 注册为 `enabled: true` 但**线上表不存在**（裁定 #ARCH-CH-024 Phase 5 的"注册先行"语义与 enabled=true 存在歧义）。
3. **`sector_snapshot` 注册 enabled=true 但实测 0 行**：880xxx 板块快照采集链可能未运行或写入失败，建议核查 `sector_snapshot_collector.py` 运行状态。
4. **c3_fundamental 8 张裸 MergeTree 表**（§3.1）：无 FINAL 自动注入保护，重跑采集有重复行风险，依赖写前 DELETE 纪律；与"#ARCH-CH-002 统一 ReplacingMergeTree"裁定存在口径缝隙。
5. **CH schema 文件覆盖率仅 ~13%**（10/77 表有 `schemas/categories/*.py` SSoT），其余表 DDL 无代码真源，与 DDL-as-Code 目标有差距。
6. **governance.db 38 表中约 20 张游离于 `_MIGRATIONS` 迁移链外**（§3.3），由各子系统运行时自建，schema 演进无版本管控。
7. **`data/governance.db`（data/ 根目录）0 KB 空文件残留**，与真实库 `data/databases/governance.db` 仅目录层级之差，有误连风险，建议清理。
8. **文档漂移**：`blueprint.md` 仍引用 `src/zephyr/infrastructure/db/`（13 个 .py，含 OLAPEngine），但该目录**已不存在**、`olap_engine.py` 已退役删除（ARCH-OLAP-RETIRE）；INFRA-DB-004 注册条目仍 `status: connected` 描述 DuckDB OLAP 挂载，与现实不符。
9. **母蓝图落地率**：MOD-ARCH-BIZDB 规划的 C2 indicator / C4 backtest / G2 Neo4j / L4 trading.db 均未启动；c3_fundamental 已上线但与母蓝图命名（C3=news_clickhouse）不一致——实际 c3 是 fundamental，news_data 表归入 c3_fundamental 库内。

## 7. 验证方法与证据附录

- **实库探测**（2026-07-22，全部只读）：
  - ClickHouse：`clickhouse_driver.Client(host=172.24.30.100, port=9000, settings={'readonly':1})`，`system.tables` 全量拉取（c0_meta 1 + c1_market 77 + c3_fundamental 23 = 101 表）。
  - PostgreSQL：`psycopg2` 读 `config/.env.postgres` 连接 `localhost:5432/depgraph`，`information_schema.tables` + 核心表 `count(*)`。
  - SQLite：`sqlite3.connect("file:...?mode=ro", uri=True)` 枚举 `sqlite_master`。
- **静态审查文件清单**（均为相对仓库根路径）：`src/zephyr/infrastructure/database_service.py`、`src/zephyr/governance/persistence/{sqlite_schema,depgraph_schema 于 governance/,database_service,database_manager,decisiongraph_schema,dataflowgraph_schema}.py`、`src/zephyr/data/{ch_config,ch_writer,ch_reader,wal_writer,progress_store}.py`、`scripts/ch/apply_market_tables_ddl.py`、`schemas/categories/*.py`（10 文件）、`docs/03_modules/_cross_layer/database/{blueprint,business_data_architecture,business_data_categories.yaml}.md/yaml`、`docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md`、`docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml`、`scripts/governance/migrate_sqlite_to_pg/`、`src/zephyr/shared/io/paths.py`。
- **未覆盖/未实测**：ChromaDB/FAISS 向量库（data/vector_db/）、Redis（未部署）、Neo4j（未部署）、各表字段级 DDL（除 schemas/categories 10 表与 governance.db/depgraph 核心表外，c1_market 67 张无 schema 文件表的字段结构未逐表 `DESCRIBE`，如需可后续补充）。
