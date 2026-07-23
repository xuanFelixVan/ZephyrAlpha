---
module_id: AUDIT-DB-SCHEMA-REVIEW
title: "业务数据库 Schema 逐表深度审查"
doc_type: audit_report
rule_form: data
status: active
version: 1.0.0
date: 2026-07-23
owner: ZephyrAlpha-Owner
ttl: permanent
language: zh
created_by: agent
---

# 业务数据库 Schema 逐表深度审查（audit_01_schema_review）

> **审查员**：库表设计审查（只读审查，未修改任何文件）
> **审查日期**：2026-07-22
> **审查范围**：业务数据库（**仅回测用途**，实盘交易后续再开发）—— ClickHouse `c0_meta` / `c1_market` / `c3_fundamental` 三库共 **101 张表**（实测）
> **审查方法**：① ClickHouse **只读实测**（`system.tables` / `system.columns` / `SHOW CREATE TABLE`，CH 版本 `26.6.1.1193`，服务器时区 `Etc/UTC`）；② DDL-as-Code 真源文件静态审查（`schemas/categories/market_*.py` 10 个）；③ 部署脚本 / 品类注册表 / 蓝图三方交叉比对。治理域（SQLite/PostgreSQL depgraph/event_store 等）不属于本次"业务回测数据库"范围，未纳入。
> **实测声明**：本次 **已成功只读连接 ClickHouse 实测**，所有引擎/排序键/分区键/列级结论均为实测值，非推断。

---

## 目录

- [1. 总览：库表清单与 DDL 真源体系](#1-总览库表清单与-ddl-真源体系)
- [2. 逐表审查](#2-逐表审查)
  - [2.1 tick_data（#ARCH-CH-020 事故现状核实）](#21-tick_dataarch-ch-020-事故现状核实)
  - [2.2 kline_daily](#22-kline_daily)
  - [2.3 分钟 K 线族（15 张：stock/etf/lof × 1/5/15/30/60min）](#23-分钟-k-线族15-张)
  - [2.4 其他 K 线族（hfq/weekly/monthly/hk/us/futures/cb/index/sector）](#24-其他-k-线族12-张)
  - [2.5 auction_snapshot 与 auction_book](#25-auction_snapshot-与-auction_book)
  - [2.6 sector_snapshot](#26-sector_snapshot)
  - [2.7 index_quote](#27-index_quote)
  - [2.8 option_iv_surface / convertible_bond_iv / futures_position / futures_term_structure](#28-衍生品类四张ddl-as-code表)
  - [2.9 事件/资金类表（money_flow/margin_trading/dragon_tiger 等 11 张）](#29-事件资金类表)
  - [2.10 元数据表（stock_list/trade_calendar/etf_list 等 16 张）](#210-元数据表)
  - [2.11 c3_fundamental 23 张基本面表](#211-c3_fundamental-23-张基本面表)
  - [2.12 c0_meta.fetch_perf](#212-c0_metafetch_perf)
- [3. 横向专题](#3-横向专题)
- [4. 问题清单（P0/P1/P2 分级）](#4-问题清单p0p1p2-分级)
- [5. 改进方向](#5-改进方向)

---

## 1. 总览：库表清单与 DDL 真源体系

### 1.1 实测库表规模

| 库 | 实测表数 | 注册表条目数 | 差异 |
|---|---:|---:|---|
| `c0_meta` | 1 | 1 | 无 |
| `c1_market` | 77 | 81 | 4 条注册但未建表（`margin_trading_qmt` / `dragon_tiger_qmt` / `block_trade_qmt` 为 QMT 占位，`l2_tick` 为预留；均有注释说明，属有意设计） |
| `c3_fundamental` | 23 | 23 | 无 |

数据来源：`system.tables` 实测（2026-07-22）× `docs/03_modules/_cross_layer/database/business_data_categories.yaml` 逐条比对。77 张实测 C1 表 **全部在注册表登记**，无黑表。

⚠️ 注册表文件头注释已过时：`business_data_categories.yaml` L9-10 自述 "C1: 76条 / C3: 21条"，实测为 **81 条 / 23 条**。

### 1.2 DDL 真源体系盘点

| 真源层级 | 覆盖表数 | 位置 |
|---|---:|---|
| DDL-as-Code（声明的唯一真源） | **10 / 101** | `schemas/categories/market_{tick,kline_daily,auction,auction_book,index,option_iv,futures_position,futures_term,cb_iv,sector_snapshot}.py` |
| 部署脚本内嵌 fallback | 4 | `scripts/ch/apply_market_tables_ddl.py` L57-L199（仅部署 tick_data / kline_daily / auction_book / sector_snapshot 4 张） |
| 无代码侧真源（仅存在于 CH 实例） | **87** | 分钟 K 线族、港股/美股/期货 K 线、事件类、c3 全部 23 张等 |

关键结构性事实：

- 蓝图 8 表中的 `auction_snapshot` / `index_quote` / `option_iv_surface` / `futures_position` / `futures_term_structure` / `convertible_bond_iv` **有 schema 文件但无任何部署脚本引用**——`apply_market_tables_ddl.py` 的 `_ALL_DDL`（L202-L207）只含 4 张；蓝图规划的统一执行器 `apply_schema.py` 在蓝图 §0.1 自标 "待建"（`docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md` L106）。这 6 张表在 CH 中实际存在（推测为手工建表），schema 文件与实际表的一致性无工具链保证。
- `scripts/migration/` 下 3 个脚本（`governance_root_split.py` / `dm314_infra_ops_split.py` / `dm311_autonomy_core_split.py`）均为代码目录治理迁移，与业务库 schema 无关。
- `src/zephyr/data/ch_config.py` 是连接配置单真源（裁定 #ARCH-CH-017/#ARCH-CH-019），不含表定义；fail-closed 设计良好。
- `src/zephyr/data/sector_snapshot_collector.py` L69-L73 主路径从 schema 文件导入 DDL，但保留了一份内联 fallback DDL（L73 起）——双写风险仍在（fallback 与真源漂移时无校验）。

---

## 2. 逐表审查

### 2.1 tick_data（#ARCH-CH-020 事故现状核实）

**真源**：`schemas/categories/market_tick.py`（DDL L41-L63）；**实测** `SHOW CREATE TABLE c1_market.tick_data`（2026-07-22）。

| 维度 | 现状 | 评价 |
|---|---|---|
| 引擎 | `ReplacingMergeTree`（无版本列） | ✅ 设计决策已在真源 L28-L30 记录，且是 #ARCH-CH-009 的已登记例外（蓝图 §4.1，c1_market_clickhouse.md L366-L368） |
| 排序键 | `(market_type, symbol, trade_date, timestamp, price)` | ✅ **#ARCH-CH-020 根因已修复**：实际表排序键含 `price`，同时间戳不同价位成交不会被合并。实测表级 COMMENT 亦标注 `'历史3秒Tick分笔成交(ORDER BY含price,ARCH-CH-020修复)'`。AGENTS.md RULE-DATA-OPS（L103-L114）记载的事故（ORDER BY 4 字段不含 price → AI 误判"重复"→ REPLACE PARTITION 删 21 个月数据）对应的结构根因已消除 |
| 分区键 | `toYYYYMM(trade_date)` 月级 | ✅ 93 亿行规模下日级分区会爆炸（真源 L25-L27 有论证）；实测当前 **143.2 亿行**（`system.parts` 求和，2026-07-22），月级分区仍然合理。⚠️ 真源 L26 的 "93 亿行" 数字已过时 |
| 价格类型 | `price Decimal(18,4)` | ✅ 正确选择（非 Float64），A 股价格 4 位小数足够 |
| 时间戳精度 | `timestamp DateTime`（秒级） | ⚠️ 3 秒粒度行情够用，但列注释自承"3秒粒度"——若未来接入逐笔委托/L2（注册表 `l2_tick` 已预留），秒级精度必然不够，需 DateTime64。当前可接受 |
| 成交量 | `volume UInt64` | ✅ |
| 去重语义 | 5 字段全同才合并 | ✅ 正确（真源 L24） |
| 辅助索引 | 实测表有 `INDEX idx_ts timestamp TYPE minmax GRANULARITY 1`，**真源文件没有** | ⚠️ **真源漂移**：索引与表级 COMMENT 均为后加，未回写 `market_tick.py`。下次若用真源重建表将静默丢失该索引 |
| 字段默认值 | 真源 `direction LowCardinality(String) DEFAULT ''`（L51），实测表 `direction` **无 DEFAULT** | ⚠️ 真源与实际表漂移（INSERT 缺列时行为不同） |
| 血缘字段 | `data_source LowCardinality(String) DEFAULT 'bdpan'` | ⚠️ 有 data_source 但 **无 ingest_ts**（虽是登记例外，但无写入时间意味着无法回答"这行数据何时入库"，审计能力受限）；无 `ingest_batch_id` 类批次血缘 |
| 时区 | `timestamp DateTime` 无时区标记；CH 服务器为 Etc/UTC | ⚠️ 行情时间是北京时间还是 UTC 只能靠约定，类型层面无保障（详见 §3.4） |
| market_type 覆盖 | 注册表宣称 8 种品种（L225），实测 2026-07 以来仅 `stock` 一种有新数据（127,205,897 行） | ⚠️ 8 种 market_type 名实不符（其余 7 类为历史存量或空） |

**评分：⚠️** —— 事故根因修复到位、核心键设计正确，但真源漂移（索引/默认值）与血缘字段缺失需要治理。

---

### 2.2 kline_daily

**真源**：`schemas/categories/market_kline_daily.py`（DDL L35-L59）；**实测** `SHOW CREATE TABLE c1_market.kline_daily`。

| 维度 | 现状 | 评价 |
|---|---|---|
| 引擎/排序键/分区 | `ReplacingMergeTree` / `(symbol, trade_date)` / `toYYYYMM(trade_date)` | ✅ 日频表标准设计，与实际表一致 |
| **amount 类型** | 真源 `Decimal(18,2)`（L45），实测 **`Float64`** | ❌ **真源与实际表类型漂移**：成交额用 Float64 有精度风险（大额成交额浮点误差），且同一字段两处定义矛盾 |
| **market_type 默认值** | 真源 `DEFAULT 'A_share'`（L51），实测 `DEFAULT 'stock'` | ⚠️ 枚举值域不统一：`'A_share'`（schema/auction_snapshot）vs `'stock'`（实际 kline_daily/tick_data 实际值）vs `'sector/mkt_index'`（sector_snapshot）——三套词汇 |
| **data_source 默认值** | 真源无 DEFAULT（L52），实测 `DEFAULT 'bdpan_qfq'` | ⚠️ 漂移；且 `'bdpan_qfq'` 把"前复权"语义编码进数据源名，属隐式约定 |
| **复权设计** | 本表存**前复权**成品（注册表 L41-L55 明示"前复权"）；`adj_factor Decimal(18,8)` 列存在；另有独立 `adj_factor` 表 | ⚠️ **原始未复权 OHLC 没有独立表**——只存 qfq（本表）+ hfq（kline_daily_hfq）两份冗余成品。若复权因子源数据修正，两份成品都需重算；回测若需要"原始价 + 自选复权时点"无法支持（详见 §3.5） |
| 派生列冗余 | `amplitude/pct_change/change/turnover` 4 列均为可由 OHLCV 派生的值 | ⚠️ 反范式冗余（真源 L46-L49），数据源直采值与本地重算值可能不一致，无校验机制 |
| 血缘 | 有 data_source / quality_flag，无 ingest_ts | ⚠️ 同 tick_data |
| 列注释 | 真源全部有 COMMENT，实测表 **全部无列注释** | ⚠️ 漂移（建表时未带 COMMENT 或被重建过） |

**评分：❌** —— amount 类型漂移是实质风险；真源与实际表三处漂移说明该表未经 `apply_schema.py` 类工具校验重建过。

---

### 2.3 分钟 K 线族（15 张）

`kline_{1,5,15,30,60}min` / `kline_etf_{1,5,15,30,60}min` / `kline_lof_{1,5,15,30,60}min`。**无 DDL-as-Code 真源**（注册表对应条目 `schema_file: null`），实测 `SHOW CREATE TABLE`。

实测规模（2026-07-22）：`kline_1min` 38.7 亿行、`kline_5min` 9.8 亿行、`kline_etf_1min` 3.6 亿行。

| 维度 | 现状 | 评价 |
|---|---|---|
| 引擎 | 全部 `ReplacingMergeTree`（无版本列） | ⚠️ 直接 INSERT 幂等依赖排序键全等，无 ingest_ts 版本列时重复下载不同来源的同 bar 数据保留哪条不确定 |
| 排序键 | `(symbol, trade_time)` | ✅ 正确 |
| 分区键 | 股票 5 张：`toYYYYMM(trade_time)`；ETF/LOF 10 张：`toYYYYMM(trade_date)` | ⚠️ **同族表分区键基准列不一致**（trade_time vs trade_date），查询写法不能统一 |
| **OHLC 精度不统一** | `kline_1min`：`Decimal(18,4)`；`kline_5min`：**`Decimal(18,6)`** | ⚠️ 同族同语义字段精度两制，跨表 UNION 需显式转换 |
| **volume 类型不统一** | `kline_1min`：`UInt64`；`kline_5min`：**`Int64`** | ⚠️ 有符号/无符号混用（`hk_kline` 也是 Int64） |
| **列集不统一** | `kline_1min` 有 `trade_date` + `pct_change` + `amplitude`；`kline_5min` **无 trade_date**、无派生列 | ⚠️ 同族表列集不齐，`kline_1min` 有 trade_date 而分区键却用 trade_time（冗余列未物尽其用） |
| **幂等键错配** | `src/zephyr/data/config/tasks.yaml`：`kline_1min` `date_col: trade_date`（L253），`kline_5min` `date_col: trade_time`（L265）；而 `kline_1min` 分区键是 `trade_time` | ⚠️ scheduler.py L1048-L1054 的"写前 DELETE"路径（仅 MergeTree 表触发）若按 `trade_date` DELETE 则**无法分区裁剪**（分区键是 trade_time），将全表扫描。当前因引擎是 ReplacingMergeTree 走直接 INSERT 不触发，属潜伏风险 |
| data_source 类型 | `kline_1min`：`LowCardinality(String)`；`kline_5min`：**`String`** | ⚠️ 低基数枚举未统一用 LowCardinality |
| 血缘 | 全部无 ingest_ts、无 quality_flag（实测 15 张均缺） | ⚠️ 分钟级数据无质量标记，坏 bar 无法标记 |

**评分：⚠️** —— 功能可用且规模最大的一批表（合计 55+ 亿行），但族内 schema 各自为政，是典型的"多次施工无统一模板"痕迹。

---

### 2.4 其他 K 线族（12 张）

`kline_daily_hfq` / `kline_weekly(_hfq)` / `kline_monthly(_hfq)` / `kline_hk_daily` / `hk_kline` / `kline_us_daily` / `kline_futures` / `futures_kline_qmt` / `kline_cb` / `kline_index` / `kline_sector` / `kline_sector_880` / `kline_sector_intraday` / `us_index`。

| 表 | 关键观察 | 评分 |
|---|---|---|
| `kline_daily_hfq` | 后复权日线；**无 market_type / quality_flag / adj_factor 列**（后复权表不需要 adj_factor 合理，但缺 quality_flag 与主表不一致）；amount 同主表 Float64 | ⚠️ |
| `kline_hk_daily` vs `hk_kline` | **功能重叠双表**（注册表 L713-L714 自承）：主表 2015 起含 name 列，补充表 2024 起、`volume Int64`、无 name。港股硬边界本应 `enabled=false` 预留（蓝图 §8.2），实际已摄取——与"当前仅 A 股"的硬边界声明存在偏差 | ⚠️ |
| `kline_futures` vs `futures_kline_qmt` | **功能重叠双表**（注册表 L643-L645 自承），主表 311 万行 vs QMT 新表 1170 行。`kline_futures` 排序键 `(symbol, period, trade_date)` 含 period 列区分日/周/月，设计合理 | ⚠️ |
| `kline_index` | **少数落实 #ARCH-CH-009 的表**：`ReplacingMergeTree(ingest_ts)` 带版本列 ✅ | ✅ |
| `kline_sector` / `kline_sector_880` / `kline_sector_intraday` | 三张板块 K 线分别来自 tdx/ifind、tqcenter、mootdx，排序键分别为 `(code, trade_date)` / `(period, sector_code, timestamp)` / `(code, period, trade_date)`——**板块代码列名三制**（code / sector_code / code） | ⚠️ |
| `kline_us_daily` / `us_index` | 美股数据已摄取（注册表 L2 级）；同样与硬边界声明有偏差；**无 currency 字段**（美元/港币价格与人民币价格同构存储，币种语义缺失，详见 §3.5） | ⚠️ |
| `kline_weekly/monthly(_hfq)` | 周/月 K 线为直采成品而非由日线聚合——数据量小可接受，但与 kline_daily 存在双真源风险（同一周线的 close 应与对应周五日线 close 一致，无校验） | ⚠️ |

**族评分：⚠️** —— 功能重叠表有注释自承是加分项，但字段命名/类型三制、币种缺失是结构性短板。

---

### 2.5 auction_snapshot 与 auction_book

| 维度 | auction_snapshot（真源 `market_auction.py`） | auction_book（真源 `market_auction_book.py`） |
|---|---|---|
| 定位 | 集合竞价快照（9:15-9:25），preload | 集合竞价五档簿，**注册表 `enabled: false` 预留**（business_data_categories.yaml L1331-L1345） |
| 排序键 | `(symbol, trade_date)` —— **同一股票同一交易日只保留一条** | `(symbol, trade_date, timestamp)` —— 支持竞价过程多快照 |
| 评分 | ⚠️ | ⚠️ |

关键问题：

- **功能重叠与语义冲突**：`auction_snapshot` 排序键 `(symbol, trade_date)` 意味着设计上"每日一股一价"（最终撮合价），而 `auction_book` 保留竞价过程全序列。两表并存合理，但 auction_snapshot 若要存 9:15-9:25 多次快照会被 ReplacingMergeTree 合并掉——`auction_time` 列存在却不在排序键中，**若写入方误以为可存多快照将静默丢数据**。⚠️
- **auction_book 名实不符**：注册表标 `enabled: false` 预留，但表已建且 `apply_market_tables_ddl.py` 把它列入正式部署清单（L206），`sector_snapshot_collector` 同级的 miniqmt_provider 也是其 CONSUMER（market_auction_book.py L5）——预留表已被事实启用，注册表状态过时。⚠️
- 五档簿用 20 个平铺列（bid_price1-5/ask_price1-5/bid_volume1-5/ask_volume1-5）而非 `Array` 嵌套——对 ClickHouse 是务实选择（列式查询友好）✅；但固定 5 档无法扩展 10 档行情。⚠️
- 两表均无 quality_flag（auction_book）/无 ingest_ts（两表）。⚠️

---

### 2.6 sector_snapshot

**真源**：`schemas/categories/market_sector_snapshot.py`；**实测**一致（列级对齐 ✅）。

| 维度 | 现状 | 评价 |
|---|---|---|
| 引擎迁移 | MergeTree → ReplacingMergeTree 治本（2026-07-22，真源 L19-L27） | ✅ 消除了写前 DELETE 的 mutations 累积 |
| 排序键 | `(sector_code, timestamp)` | ✅ 高频快照正确 |
| **calc_mode 双真源冲突** | 真源 `CALC_MODE = "streaming"`（L67），注册表 `calc_mode: replay`（business_data_categories.yaml L979） | ⚠️ 两处真源矛盾 |
| **采集频率口径** | 注册表 `frequency: 18秒`（L980），真源注释 "30秒轮询+99只推送"（L21-L22） | ⚠️ 口径不一致 |
| 字段命名 | `zangsu`（涨速，拼音）、`up_home`/`down_home`（上涨/下跌家数，中式英语）、`before_5min_now` | ⚠️ 命名规范性差，对外不可读 |
| 血缘 | 有 `fetched_at`（采集时间）+ `data_source` ✅；但**无 quality_flag**；`fetched_at` 真源注释 `采集时间(UTC)`（L56）而实测表注释仅 `采集时间`——UTC 标注在漂移中丢失 | ⚠️ |
| 成交量语义 | `volume` 真源注释 `成交量(板块恒为0)`（L47）——恒零列保留占存储 | ⚠️ 可裁剪 |

**评分：⚠️** —— 引擎治理到位，但双真源冲突与命名规范是明显短板。

---

### 2.7 index_quote

**真源**：`schemas/categories/market_index.py`。

| 维度 | 现状 | 评价 |
|---|---|---|
| 分区键 | **`toYYYYMMDD(trade_date)` 日级分区**（L42） | ❌ **与 tick_data 月级分区的论证自相矛盾**：同为 3 秒频 replay 表，tick_data 真源明确论证"日级分区在 93 亿行规模下分区数过多（>8000）"（market_tick.py L25-L27），index_quote 却用日级分区。指数标的少（注册表 index_list 732 个），数据量小于 tick，但长期累积后日分区数无上限增长，蓝图 §6.1 自设告警 `c1_partition_count > 365分区/表`（c1_market_clickhouse.md L914）会被该表触发 |
| 生命周期矛盾 | 注册表 `lifecycle: hot_90d`（L601），蓝图 INV-RET-003 铁律声明 index_quote **无 TTL 永久保留**（c1_market_clickhouse.md L516、L866） | ❌ 两处真源直接冲突（实际表无 TTL，按蓝图执行中，但注册表标注错误会误导后续治理操作——若有人按注册表执行 90 天清理将重演 #ARCH-CH-020 类事故） |
| 与 tick_data(market_type='index') 重叠 | 注册表 L520-L528 用注释区分二者 | ⚠️ 同一指数 3 秒数据存两处（index_quote 与 tick_data 的 index 类型），存储双份 |
| 血缘 | 有 quality_flag，无 ingest_ts | ⚠️ |

**评分：❌** —— 分区策略与 tick_data 的既定论证矛盾，且 lifecycle 真源冲突有实质风险。

---

### 2.8 衍生品类四张 DDL-as-Code 表

`option_iv_surface` / `convertible_bond_iv` / `futures_position` / `futures_term_structure`。

| 表 | 观察 | 评分 |
|---|---|---|
| `option_iv_surface` | 排序键 `(underlying, trade_date, strike, expiry)` 合理；IV/Greeks 用 `Decimal(18,6)` 精度恰当 ✅；**`option_type` 不在排序键中**——同一标的同日同行权价同到期日的 call 与 put 会互相覆盖！⚠️ 严重设计缺陷 | ❌ |
| `convertible_bond_iv` | 排序键 `(symbol, trade_date)` 标准；希腊字母默认值 `DEFAULT 0` 会把"未计算"与"真零值"混淆（Delta=0 与缺失无法区分），应用 Nullable | ⚠️ |
| `futures_position` | 排序键 `(symbol, trade_date)`；`exchange` 已有 LowCardinality ✅ | ✅ |
| `futures_term_structure` | `basis` 注释 "基差(近月-次月)"（L38）——**基差常规定义为现货-期货**，此处自定义为近月-次月价差，术语误用会误导因子开发 | ⚠️ |

四张表共性：schema 文件齐备但**无部署链路**（见 §1.2），实际表与真源是否一致无工具保证；均无 ingest_ts。

---

### 2.9 事件/资金类表

`money_flow` / `margin_trading` / `dragon_tiger` / `block_trade` / `block_trade_detail` / `limit_up_down` / `st_stock_list` / `stock_indicator` / `daily_valuation` / `hk_connect_flow` / `macro_data`。

| 观察 | 评价 |
|---|---|
| 全部 `ReplacingMergeTree` + 月分区 ✅ | ✅ |
| 排序键两制：`(trade_date, symbol)`（dragon_tiger/block_trade/limit_up_down 等 6 张）vs `(symbol, trade_date)`（money_flow/daily_valuation 等）——蓝图 §4.0 明确"排序键 symbol 前缀（回测主要查单只股票历史数据）"（c1_market_clickhouse.md L354），trade_date 前缀的 6 张偏离设计原则，回测按 symbol 取数时无法利用排序键前缀裁剪 | ⚠️ |
| 11 张全部无 quality_flag（实测）；9 张无 ingest_ts | ⚠️ |
| QMT 占位 3 表（margin_trading_qmt 等）注册但未建表，注册表注释自承由 AKShare 覆盖（L1114-L1115，裁定 #ARCH-CH-024 Phase 5）——登记规范 ✅，但"注册了表却不存在"对全量校验工具是噪声 | ⚠️ |

**族评分：⚠️**

---

### 2.10 元数据表

`stock_list` / `trade_calendar` / `etf_list` / `etf_benchmark` / `lof_list` / `convertible_bond_list` / `index_list` / `index_constituent` / `index_weight` / `hk_stock_list` / `hk_trade_calendar` / `concept_board(_constituent)` / `concept_sector` / `sector_meta` / `sector_list` / `industry_class` / `market_index_meta` / `sector_constituent`。

| 观察 | 评价 |
|---|---|
| 全部为 `ReplacingMergeTree`（元数据表用 Replacing 合理——同一实体属性更新覆盖旧值）✅ | ✅ |
| **11 张无分区键**（stock_list/trade_calendar/etf_list 等，实测 partition_key 为空）——元数据表体量小，可接受 | ✅ |
| **11 张无 data_source、16 张无 quality_flag**（实测 §3.6）；无 `updated_at`/`valid_from` 列——`stock_list` 这类缓变维表**无法回答"该记录是哪天的状态"**，回测到 2023 年时拿到的仍是当前列表（含当时未上市股票），存在**前视偏差（look-ahead bias）通道** | ❌ |
| `stock_list` 有 `currency` 列 ✅ 但行情表无对应币种列 | ⚠️ |
| `1970-01-01` 作"未发生"语义空值（注册表 L15 统一声明）——用哨兵值代替 NULL，回测过滤时极易踩坑（如 `delist_date > '2020-01-01'` 会把 1970 哨兵当作已退市） | ⚠️ 已在注册表显式声明，属可接受但有风险的约定 |
| 命名多义自承（"index"一词 8 种含义，注册表 L520-L528 有完整消歧注释） | ✅ 注释消歧是好实践 |

**族评分：⚠️** —— 最大问题是缓变维表无时点版本，对回测真实性是结构性威胁。

---

### 2.11 c3_fundamental 23 张基本面表

| 观察 | 评价 |
|---|---|
| **8 张裸 `MergeTree`**（实测）：`analyst_forecast` / `disclosure_plan` / `equity_pledge_detail` / `industry_class_suppl` / `restricted_shares` / `rights_issue` / `share_change` / `share_unlock` | ❌ **违反裁定 #ARCH-CH-002**（"全部 ReplacingMergeTree"，c1_market_clickhouse.md §4.0 L337）。这些表走 scheduler.py L1048-L1054 的"写前 DELETE"幂等路径，正是蓝图自己论证过的 mutations 累积反模式（§4.0 L339："5204 次 ALTER DELETE mutation = 双倍 data parts"） |
| 15 张 `ReplacingMergeTree` 中，`balance_sheet` / `news_data` 等已落实 `ingest_ts` 版本列 ✅（实测 `ReplacingMergeTree(ingest_ts)`） | ✅ #ARCH-CH-009 在 c3 部分落实 |
| `balance_sheet` 等报表：排序键 `(symbol, report_period, announce_date)` 含公告日——**支持 point-in-time 查询**（避免使用未公告数据），这是基本面表最关键的正确性设计 ✅ | ✅ |
| 财务金额用 `Nullable(Float64)`（balance_sheet 实测）——财报大额数值浮点精度风险 + Nullable 合理但全列 Nullable 稍滥 | ⚠️ |
| `news_data`：含 `sentiment_score Decimal(4,3)`（-1 到 1 用 3 位小数合理）✅、`related_symbols Array(String)` ✅、`raw_data` 原始 JSON 备份 ✅（血缘可追溯）；`crawl_time` + `ingest_ts` 双时间戳 ✅。全库血缘最完整的表 | ✅ |
| `dividend` 分区键 `toYYYYMM(dividend_year)`——按"分红年度"分区而非公告日，跨年查询公告事件时分区裁剪失效 | ⚠️ |

**族评分：⚠️**（8 张裸 MergeTree 拉低整体；point-in-time 设计与 news_data 血缘是亮点）

---

### 2.12 c0_meta.fetch_perf

单表，`ReplacingMergeTree(recorded_at)` 带版本列 ✅，列注释完整 ✅，排序键 `(source, capability, test_date)` 合理 ✅。**评分：✅** —— 全库设计与文档一致性最好的表（MOD-L00-004 自产自用）。

---

## 3. 横向专题

### 3.1 #ARCH-CH-020 现状核实（重点任务项）

- **事故根因（ORDER BY 不含 price）已修复** ✅：实测 `tick_data` 排序键为 5 字段含 price，与真源 `market_tick.py` L61 一致；表级 COMMENT 显式标注修复来源。
- **残留风险**：①真源文件未包含实测表的 `idx_ts` minmax 索引与表级 COMMENT（重建即丢失）；②AGENTS.md RULE-DATA-OPS 的三步验证纪律（L105-L111）是流程约束，结构上仍无防呆——若未来有人按真源重建表，5 字段排序键保留但索引丢失，性能回退无告警。

### 3.2 #ARCH-CH-009 版本列落实率：17/101

裁定要求"所有 ReplacingMergeTree 表新增 `ingest_ts` 作 version 列"（c1_market_clickhouse.md L342-L347）。实测：

- 带版本列：**17 张**（c0 全部 1 张；c1 仅 `adj_factor` / `kline_index` 2 张；c3 约 14 张如 balance_sheet/news_data）
- 无版本列：**84 张**（含全部 10 张 DDL-as-Code 真源表——**真源本身未落实裁定**，schema 文件自述"蓝图内部矛盾，待 #ARCH-CH-009 后续裁定统一修正"，如 market_kline_daily.py L24-L28）

即裁定、蓝图、真源、实例四层互相等待，无人闭环。无版本列的 ReplacingMergeTree 在"同键不同内容重写"场景（数据源修正历史数据）下，合并保留哪一行**不确定**（取决于 part 合并顺序），这对回测可复现性是实质威胁。

### 3.3 引擎合规

- c1_market 77 张全部 ReplacingMergeTree ✅
- c3_fundamental 23 张中 8 张裸 MergeTree ❌（清单见 §2.11）
- `apply_market_tables_ddl.py` 的 `_EXPECTED_ENGINES`（L210-L215）只验证 4 张表，verify() 对"未在选型矩阵中"的表仅打印 ⚠️ 不报错（L269-L273）——引擎合规无全库门禁。

### 3.4 时间戳与时区

- 全部时间列 `DateTime`（秒级），无 `DateTime64`——3 秒粒度够用，但 L2/逐笔预留表（l2_tick）与未来实盘必然需要毫秒。⚠️
- CH 服务器时区 `Etc/UTC`（实测 `SELECT timezone()`），`DateTime` 类型不带时区；行情时间（北京时间）、采集时间（fetched_at 注释自称 UTC）、`now()` 默认值（UTC）三类时间同构存储无类型级区分。**一旦写入端按本地时间写入而读取端按 UTC 解读（或反之），将产生 8 小时系统性偏移**，且 schema 层面无任何防线。⚠️
- `trade_date`（Date）与 `trade_time/timestamp`（DateTime）冗余双列在部分表共存（kline_1min）部分表没有（kline_5min），口径不统一。

### 3.5 复权 / 币种 / 单位

- **复权**：kline_daily 存前复权成品（`data_source='bdpan_qfq'`），原始价无独立表；`adj_factor` 有独立表（含 ingest_ts ✅）但其 `adj_factor` 列是 **Float64**，与 kline_daily 内嵌 `adj_factor Decimal(18,8)` **同名字段两类型**。用 Float64 因子回算原始价会累积浮点误差。⚠️
- **币种**：行情表无 `currency` 列；港股/美股 K 线已实际摄取，与 A 股同构存储，回测跨市场拼接时币种只能靠 symbol 后缀推断。⚠️
- **单位**：auction_book 的 volume 注释"手"、tick_data 注释"股"（market_auction_book.py L42 vs market_tick.py L49）——跨表单位不统一且无 unit 字段，因子误用风险。⚠️

### 3.6 血缘与质量字段

实测全库统计（`system.columns`，2026-07-22）：

- 缺 `ingest_ts`：**84 张**（含全部分钟 K 线、tick_data、sector_snapshot）
- 缺 `quality_flag`：**64 张**
- 缺 `data_source`/`source`：**11 张**（全部为元数据表，含 stock_list/trade_calendar）
- 无 `ingest_batch_id` / 源文件哈希 / 采集任务 ID 类批次级血缘——RULE-DATA-OPS 事故后无法回答"这批数据是哪次任务写入的"，误删后的精确恢复只能靠分区+时间范围粗粒度回灌。

### 3.7 注册表治理

- ✅ 77 张实测 C1 表全部登记，无黑表；功能重叠表有注释自承；"index"多义有消歧。
- ⚠️ 头部统计过时（76→81 / 21→23）；`auction_book` enabled 状态过时；`index_quote` lifecycle 与蓝图铁律冲突；`sector_snapshot` calc_mode/frequency 与 schema 真源冲突。

---

## 4. 问题清单（P0/P1/P2 分级）

### P0（影响回测正确性/可能丢数据，须立即处理）

| # | 问题 | 证据 |
|---|---|---|
| P0-1 | `option_iv_surface` 排序键缺 `option_type`：同标的同日同行权价同到期日的 call/put 互相覆盖，**静默丢一半数据** | `schemas/categories/market_option_iv.py` L48（实测排序键同样无 option_type） |
| P0-2 | `index_quote` lifecycle 真源冲突：注册表 `hot_90d` vs 蓝图 INV-RET-003"无 TTL 永久保留"——按错误真源执行清理即重演 #ARCH-CH-020 类数据删除事故 | `business_data_categories.yaml` L601 vs `c1_market_clickhouse.md` L516/L866 |
| P0-3 | 元数据缓变维表（stock_list 等 18 张）无时点版本字段：回测取全量当前状态 → **前视偏差**（用含未来新股的股票池回测历史） | §2.10 实测（无 valid_from/updated_at 列） |
| P0-4 | 8 张 c3 表裸 MergeTree 违反 #ARCH-CH-002，走写前 DELETE 路径（mutations 累积 + DELETE 不可回滚） | 实测 engine 清单（§2.11）；scheduler.py L1048-L1054 |

### P1（真源漂移/一致性问题，应在下个治理周期处理）

| # | 问题 | 证据 |
|---|---|---|
| P1-1 | #ARCH-CH-009 版本列落实率仅 17/101；10 个 DDL-as-Code 真源文件**全部未含 ingest_ts**，裁定-真源-实例四层断链 | §3.2 |
| P1-2 | `kline_daily` 真源与实际表三处漂移：amount 类型（Decimal(18,2)→Float64）、market_type 默认值（'A_share'→'stock'）、data_source 默认值（无→'bdpan_qfq'） | `market_kline_daily.py` L45/L51/L52 vs 实测 SHOW CREATE |
| P1-3 | `tick_data` 真源缺实测表的 `idx_ts` 索引、表级 COMMENT、direction 默认值——重建即回退 | `market_tick.py` L41-L63 vs 实测 |
| P1-4 | 分钟 K 线族内 schema 不统一：OHLC 精度（18,4 vs 18,6）、volume 符号性（UInt64 vs Int64）、列集（trade_date 有无）、分区基准列（trade_time vs trade_date）、幂等键与分区键错配（kline_1min） | §2.3 实测；tasks.yaml L253/L265 |
| P1-5 | 6 张事件表排序键 `(trade_date, symbol)` 违反蓝图"symbol 前缀"设计原则，回测按股取数无法前缀裁剪 | §2.9 实测；c1_market_clickhouse.md L354 |
| P1-6 | `index_quote` 日级分区与 tick_data 月级分区论证矛盾，分区数无上限 | `market_index.py` L42 vs `market_tick.py` L25-L27 |
| P1-7 | 87/101 张表无 DDL-as-Code 真源（含全部 c3、全部分钟 K 线），蓝图 8 表中 6 张有真源无部署链路（apply_schema.py 待建） | §1.2；c1_market_clickhouse.md L106 |
| P1-8 | `auction_snapshot` 排序键 `(symbol, trade_date)` 不含 `auction_time`，多快照写入被静默合并 | `market_auction.py` L44 |

### P2（规范性/可维护性问题，可排期改进）

| # | 问题 | 证据 |
|---|---|---|
| P2-1 | 时区无类型级防线：全库 DateTime 无时区，业务时间（北京）/采集时间（UTC）/now() 混存，8 小时偏移风险无 schema 防线 | §3.4 |
| P2-2 | 枚举词汇三制：market_type 取值 'A_share'/'stock'/'sector/mkt_index' 并存 | §2.2/§2.6 |
| P2-3 | 字段命名不规范：`zangsu`（拼音）、`up_home/down_home`、`before_5min_now`；板块代码列名三制（code/sector_code） | `market_sector_snapshot.py` L50-L54；§2.4 |
| P2-4 | 复权体系缺原始价层：只存 qfq/hfq 双成品，adj_factor 表因子列 Float64 与 kline_daily 内嵌 Decimal(18,8) 不一致 | §3.5 |
| P2-5 | 币种/单位语义缺失：行情表无 currency；volume 单位"股/手"跨表不一 | §3.5 |
| P2-6 | 血缘字段缺口：64 张缺 quality_flag、11 张缺 data_source、全库无批次级血缘（batch_id/源哈希） | §3.6 |
| P2-7 | 注册表元信息过时：头部计数（76/21→81/23）、auction_book enabled 状态、sector_snapshot calc_mode（streaming vs replay）与 frequency（18秒 vs 30秒） | business_data_categories.yaml L9-L10/L1331/L979-L980 |
| P2-8 | 双写 fallback：`sector_snapshot_collector.py` L73 起内联 DDL fallback 与真源漂移无校验；`apply_market_tables_ddl.py` L56-L79 同样保留内联 fallback | 两文件源码 |
| P2-9 | Greeks 默认值 `DEFAULT 0` 混淆"未计算"与"真零值"（应为 Nullable） | `market_cb_iv.py` L36-L39 |
| P2-10 | `futures_term_structure.basis` 术语误用（基差≠近月-次月价差） | `market_futures_term.py` L38 |
| P2-11 | 哨兵值 `1970-01-01` 代替 NULL 作"未发生"语义，回测过滤易踩坑（已声明但仍有风险） | business_data_categories.yaml L15 |
| P2-12 | 文档数字过时：tick_data "93 亿行"（实测 143.2 亿） | market_tick.py L26 vs 实测 |

---

## 5. 改进方向

1. **补齐真源覆盖（治 P1-7）**：把 `apply_schema.py` 从"待建"变为现实——以 10 个现有 schema 文件为模板，为其余 87 张表（优先 15 张分钟 K 线 + 8 张裸 MergeTree c3 表）生成 DDL-as-Code 文件；`apply_market_tables_ddl.py` 的 `_ALL_DDL` 改为全量扫描 `schemas/categories/`，消除"4 张部署/6 张孤儿"现状。
2. **建立"真源 ↔ 实例"漂移检测门禁（治 P1-1/P1-2/P1-3）**：定时比对 `SHOW CREATE TABLE` 与 schema 文件（列、类型、默认值、索引、引擎参数），漂移即告警。当前 verify() 只查引擎且对未知表放行（apply_market_tables_ddl.py L269-L273），需升级为全字段比对 + 全库覆盖。
3. **闭环 #ARCH-CH-009（治 P1-1）**：二选一明确裁定——要么全库补 `ingest_ts` 版本列（含回写 10 个 schema 真源），要么正式废弃该裁定并修订蓝图 §4.0。当前"四层互相等待"状态比任何一个单选都差。
4. **修排序键硬伤（治 P0-1/P1-8/P1-5）**：`option_iv_surface` 排序键补 `option_type`；`auction_snapshot` 补 `auction_time`（或文档明示"每日一条"约束并由写入端保证）；6 张事件表统一为 symbol 前缀。涉及历史数据重排的表需按 RULE-DATA-OPS 三步验证执行。
5. **消除 P0 数据安全隐患（治 P0-2/P0-3/P0-4）**：修正 `index_quote` 注册表 lifecycle 为 permanent；元数据表增加 `valid_from`（或至少 `updated_at`）列并在回测加载层加"as-of 回测截止日"过滤；8 张裸 MergeTree 迁移 ReplacingMergeTree。
6. **分钟 K 线族归一化（治 P1-4）**：定族模板（统一 OHLC 精度、volume UInt64、trade_date 冗余列、分区基准列、LowCardinality data_source），生成 DDL-as-Code 后逐表重建；同步修正 tasks.yaml 幂等键与分区键对齐。
7. **时区与语义字段（治 P2-1/P2-5）**：写入层统一"业务时间=Asia/Shanghai 墙钟、采集时间=UTC"并在 schema 注释强制标注；新增表引入 `currency`（LowCardinality 默认 'CNY'）与 volume 单位约定；`market_type` 枚举值收敛为一套受控词汇表（写入前校验）。
8. **血缘增强（治 P2-6）**：新增/重建表统一含 `data_source` / `quality_flag` / `ingest_ts` / `ingest_batch_id` 四件套；注册表文件头计数改为自动生成为宜（手工维护已证明会过时）。

---

> **审查局限声明**：① 行数/分区统计基于 `system.parts`（active），为审查时点快照；② 未对每张表逐列核对 101×N 全列矩阵（重点表已逐一 `SHOW CREATE` 核对，族内同构表按抽样+`system.columns` 聚合统计）；③ 写入端代码（scheduler/collector/provider）仅审查与 schema 直接相关的幂等路径，未做全链路数据正确性验证；④ PostgreSQL/SQLite 治理域库表不在本次"业务回测数据库"范围内。
