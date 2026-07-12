---
module_id: MOD-ARCH-BIZDB
submodule_path: docs/03_modules/_cross_layer/database
title: "业务数据库顶层架构设计书 — 回测引擎数据仓库 + 实盘分析数据中台（ClickHouse目标 / SQLite事务 / Neo4j图谱）"
doc_type: blueprint
status: Active
version: "1.0.0"
layer: L1_foundation
blueprint_level: architecture
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260701-arch
date: "2026-07-01"
valid_from: "2026-07-01"
ttl: permanent
rule_form: structural
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
scope: global
stability: evolving
verifiability: design_review
construction_progress: design_phase
codification_level: L1
generation: 1
functional_domain: data
summary: "业务数据库顶层架构母蓝图——从第一性原理推导的分库方案：治理数据库(已有，governance.db+depgraph，不动) + 业务数据库(新建，C1~C4 ClickHouse仓库 + G2 Neo4j图谱 + L4 SQLite事务 + 内存工作台)。第一驱动力=回测性能(时光机重演) + 实盘实时分析(不拉垮)。按引擎+生命周期分库，69个数据品类插拔式管理(YAML注册表+DDL-as-Code+CTR契约+CategoryManager发现)。回测采用模式③混合(批量预加载内存+时间步重演)，规避ClickHouse JOIN弱项。能造现在就造(硬性边界二元判定)，硬边界品类(Level-2/卫星/Barra)enabled=false预留接口。本母蓝图指导C1~C4/G2/L4各子施工蓝图。"
tags: [business-database, clickhouse, sqlite, neo4j, backtest, realtime, category-registry, ddl-as-code, data-contract, pluggable, architecture-design, master-blueprint]
priority: P1
runtime_plane: warm
child_modules:
  - {module_id: "C1-MARKET-CH", title: "C1 market_clickhouse 行情仓库施工蓝图", status: "Pending", construction_progress: "not_started", path: "sub_blueprints/c1_market_clickhouse.md"}
  - {module_id: "C2-INDICATOR-CH", title: "C2 indicator_clickhouse 指标与因子仓库施工蓝图", status: "Pending", construction_progress: "not_started", path: "sub_blueprints/c2_indicator_clickhouse.md"}
  - {module_id: "C3-NEWS-CH", title: "C3 news_clickhouse 新闻与宏观仓库施工蓝图", status: "Pending", construction_progress: "not_started", path: "sub_blueprints/c3_news_clickhouse.md"}
  - {module_id: "C4-BACKTEST-CH", title: "C4 backtest_clickhouse 回测结果仓库施工蓝图", status: "Pending", construction_progress: "not_started", path: "sub_blueprints/c4_backtest_clickhouse.md"}
  - {module_id: "G2-KNOWLEDGE-NEO4J", title: "G2 knowledge_graph Neo4j知识图谱施工蓝图", status: "Pending", construction_progress: "not_started", path: "sub_blueprints/g2_knowledge_graph_neo4j.md"}
  - {module_id: "L4-TRADING-SQLITE", title: "L4 trading.db SQLite交易事务施工蓝图", status: "Pending", construction_progress: "not_started", path: "sub_blueprints/l4_trading_sqlite.md"}
depends_on:
  - {target: "SH-DB-001", at: "§三库职责划分", why: "现有三库(governance.db+depgraph+market.duckdb)为本架构基线，market.duckdb将重构"}
  - {target: "数据架构.md", at: "§1~§17", why: "数据品类清单/SLA/L0→L1流水线/CTR契约体系的设计输入"}
  - {target: "依赖图/02-D-DATA-数据域.md", at: "§1", why: "D-DATA-03 Storage 模块定义+数据目录结构"}
references:
  - {id: "PS-STD-001", at: "§2~§7", why: "frontmatter字段合法值"}
  - {id: "PS-STD-005", at: "§6", why: "蓝图归属与引用链——belongs_to字段定义"}
  - {id: "DD-07-01", at: "数据架构.md §7.5", why: "DuckDB→ClickHouse升级门禁决策(本架构提前触发)"}
  - {id: "DD-P3-01", at: "数据架构.md §3.2", why: "因子值窄表7列Schema决策(本架构采纳)"}
  - {id: "DD-P6-01", at: "数据架构.md §6.4", why: "图谱存储NetworkX→Neo4j修正(551K关系超舒适区)"}
  - {id: "ARCH-BIZDB-DISCUSSION", at: "docs/_working/业务数据库架构_讨论记录.md", why: "11章推导过程记录，本母蓝图的完整输入"}
responsibility_domain: 
build_status: planned
design_maturity: design
---

# 业务数据库顶层架构设计书 — 回测引擎数据仓库 + 实盘分析数据中台

> module_id: MOD-ARCH-BIZDB | version: 1.0.0 | status: Active | layer: cross_layer | blueprint_level: architecture
> 本文档为**母蓝图**，指导 C1~C4 / G2 / L4 各子施工蓝图。表级细化，不到字段级（字段级见各子蓝图 DDL-as-Code）。
> **推导过程完整记录**：[业务数据库架构_讨论记录.md](file:///D:/ZephyrAlpha/docs/_working/业务数据库架构_讨论记录.md)（11章）

## 概述

### 定位

本文档是 ZephyrAlpha 业务数据库的**顶层架构设计书**（母蓝图）。区别于现有 [database/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md)（market.duckdb 单库施工蓝图），本母蓝图定义业务数据库的**分库原则、引擎选型、品类全景、插拔机制、调度策略**，指导后续各库的施工蓝图。

### 核心理念（一句话）

> **业务数据库 = "回测引擎的数据仓库" + "实盘分析的数据中台"**
> 仓库只管存和批量出货，工作台（内存）管计算。ClickHouse 当仓库，SQLite 管事务，Neo4j 管图谱，PostgreSQL 管架构真源。

### 第一驱动力

```
回测性能（第一优先级）
  └─ 回测速度 ↑ → 策略自我迭代效率 ↑ → 赚钱能力 ↑

实盘实时分析（第二优先级，并重）
  └─ 实盘不拉垮，tick→信号≤15秒

两者共用同一套计算引擎，数据源不同（历史批量 vs 实时流）。
回测真实性 = 实盘真实性。
```

### 输入材料

| 材料 | 性质 | 贡献 |
|------|------|------|
| [数据架构.md](file:///D:/ZephyrAlpha/docs/_working/research_notes/架构图/数据架构.md) | 数据架构设计书 | 品类清单(60+)/SLA/L0→L1流水线/CTR契约/因子窄表Schema |
| [依赖图/](file:///D:/ZephyrAlpha/docs/_working/research_notes/依赖图) | 模块依赖规划书 | 30个业务域的数据存储需求/D-DATA-03 Storage |
| [database/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md) | 现有三库施工蓝图 | 三库职责划分验证/DatabaseService统一入口 |

---

## §1 第一性原理推导

### §1.1 为什么要分库（数据本质三类）

数据库选型应由"数据本质特征"决定，而非由"业务域归属"决定。数据本质有三类（互斥不可合并）：

| 数据本质 | 特征 | 最优引擎 | 类比 |
|---------|------|---------|------|
| 关系事务型 | 高频小事务、ACID、状态机CHECK约束 | SQLite | 保险柜（小而稳） |
| 时序分析型 | 海量存储、列式压缩、快速扫描、按时间归档 | ClickHouse | 录像带库（量大、按时间查） |
| 图遍历型 | 复杂关系查询、MVCC并发、图遍历 | PostgreSQL / Neo4j | 地图册（查关系用） |

**结论**：三种数据住在同一个库 = 三种需求互相打架（事务锁 vs 快速扫描）。必须分家。

### §1.2 现有三库第一性原理判断：合理

| # | 库 | 引擎 | 职责 | 判断 |
|---|---|------|------|------|
| 1 | governance.db | SQLite | 治理运行时 | ✅ 保持（保险柜） |
| 2 | depgraph | PostgreSQL | 架构静态真源 | ✅ 保持（地图册） |
| 3 | market.duckdb | DuckDB | 业务时序（8表） | ⚠️ 重构（升级ClickHouse，按品类拆分） |

**market.duckdb 重构理由**：AUM即将>200万（用户称"100万马上超200万"），DuckDB进入Pushing区间；用户授权可重构/删除，按新设计重建。

### §1.3 回测的本质（决定仓库设计）

```
❌ 错误理解：回测 = 从DB查历史数据，一条条SQL查
   → 数据库要支持复杂JOIN和点查 → ClickHouse弱项暴露 → 慢

✅ 正确理解：回测 = 时光机重演——把历史数据"倒进内存"，在内存里重演
   → 数据库只负责"快速把数据倒出来"（批量扫描） → ClickHouse强项发挥 → 快
   → 时间对齐/JOIN/计算都在内存做，规避ClickHouse JOIN弱项
```

回测的本质是"在历史数据上重放交易决策"。实盘怎么算，回测就怎么算（新闻分析/因子计算/信号生成都要复现）。区别只在：数据是历史的，可调的是"影响的数值权重"（策略参数）。

---

## §2 顶层架构全景

### §2.1 架构全景图

```
┌─────────────────────────────────────────────────────────────────────┐
│              ZephyrAlpha 业务数据库顶层架构                            │
│                                                                     │
│  ┌─ 治理数据库（已有，不动）──────────────────────────────────────┐  │
│  │  governance.db (SQLite)   治理运行时（TaskCard/事件/门禁）       │  │
│  │  depgraph (PostgreSQL 16) 架构静态真源（nodes/edges/domains）    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─ 业务数据库（新建，本母蓝图范围）──────────────────────────────┐  │
│  │                                                                │  │
│  │  ┌─ 仓库层 ClickHouse（回测+实盘分析的数据底座）──────────────┐ │  │
│  │  │  C1 market_clickhouse   行情录像带                         │ │  │
│  │  │  C2 indicator_clickhouse 指标与因子仓库                     │ │  │
│  │  │  C3 news_clickhouse     新闻与宏观仓库                     │ │  │
│  │  │  C4 backtest_clickhouse  回测结果仓库                      │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌─ 事务层 SQLite（交易执行的保险柜）─────────────────────────┐ │  │
│  │  │  L4 trading.db  orders/positions/risk_snapshots             │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌─ 图谱层 Neo4j（知识图谱持久化）────────────────────────────┐ │  │
│  │  │  G2 knowledge_graph  公司/产业/供应链/因果链/地缘           │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  │                                                                │  │
│  │  ┌─ 工作台 内存（回测重演+实时计算，64G）────────────────────┐ │  │
│  │  │  回测：从C1~C3批量加载→内存重演→结果写C4                 │ │  │
│  │  │  实盘：实时tick进内存→实时算指标/信号                     │ │  │
│  │  │  共用同一套计算引擎（回测真实性=实盘真实性）              │ │  │
│  │  └──────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─ 能造现在就造（硬性边界外，立即建）────────────────────────────┐  │
│  │  H1 redis_hot       实盘热缓存（64G内存够）                    │  │
│  │  E1 event_store     事件溯源（Parquet+CQRS）                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─ 硬性边界不能造（enabled=false预留接口）────────────────────────┐  │
│  │  Level-2逐笔（资金硬边界 $10K+/年）                             │  │
│  │  多市场数据（数据源硬边界，需采购）                            │  │
│  │  卫星图像/信用卡/AIS/Barra（资金/合规硬边界）                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### §2.2 与现有三库的关系

| 现有三库 | 在新架构中的位置 | 变化 |
|---------|----------------|------|
| governance.db (SQLite) | 治理数据库（保持） | 不变 |
| depgraph (PostgreSQL) | 治理数据库（保持） | 不变 |
| market.duckdb (DuckDB) | 重构为 C1~C4 (ClickHouse) + L4 (SQLite) | **核心变化**：8表按品类拆分，DuckDB→ClickHouse |

---

## §3 分库原则（第一性原理推导）

| 原则 | 内容 | 理由 |
|------|------|------|
| **P1 引擎适配** | 按数据本质特征选引擎，不按业务域选 | 时序用ClickHouse、关系用SQLite、图用Neo4j，引擎能力不可替代 |
| **P2 同引擎内分库** | 同一引擎内按"数据生命周期+品类"分库 | 单库膨胀控制 + 备份策略差异（行情vs回测留存期不同） |
| **P3 跨引擎不分库** | 不同引擎不因"同一域"强行合并 | D-DATA的tick(ClickHouse)和reference(SQLite)各归各位 |
| **P4 元数据集中** | 所有库的元数据/契约/血缘集中在治理层 | 单一真源，避免元数据散落 |
| **P5 能造现在就造** | 硬性边界外的全建，不等需求门禁 | 避免"等需要了再改"的技术债 |
| **P6 统一入口** | DatabaseService 扩展为多库路由 | AI只需记一个类，引擎差异封装在内部 |

### §3.1 门禁逻辑（重要修正）

```
❌ 废弃逻辑：需求门禁触发演进
   "等AUM>200万再造" "等实盘再造Redis" "等需要了再造"
   → 后面改非常麻烦，技术债累积

✅ 采用逻辑：硬性边界二元判定
   能造 → 现在就造（按最好需求）
   不能造 → 一定是硬性边界（CPU/内存/资金/数据源采购）
   不认"需求门禁"，只认"物理硬边界"
```

---

## §4 引擎选型决策

### §4.1 引擎选型表

| 数据本质 | 选型引擎 | 理由 | 替代方案（不采用原因） |
|---------|---------|------|---------------------|
| 时序分析型 | **ClickHouse** | 列式压缩、MergeTree、高速扫描、分区裁剪 | DuckDB（AUM>200万进入Pushing区间，避免二次迁移） |
| 关系事务型 | **SQLite** | 嵌入式零部署、ACID、状态机CHECK约束 | PostgreSQL（governance已用，trading事务量单人SQLite够） |
| 图遍历型 | **Neo4j** | 551K关系超NetworkX舒适区，社区版免费 | NetworkX（内存扛不住551K关系） |
| 架构真源 | **PostgreSQL**（已有） | MVCC、递归CTE、28表关系查询 | 不变 |
| 向量检索 | **ChromaDB+Faiss**（部分部署） | RAG/Embedding检索 | 不变 |
| 热缓存 | **Redis**（能造现在造） | 实盘<5ms推理 | — |

### §4.2 ClickHouse 的弱项与规避

| ClickHouse弱项 | 规避方式 |
|---------------|---------|
| 无 AS OF JOIN | 内存时间网格对齐（§7.3） |
| JOIN性能差 | 批量预加载到内存，内存里JOIN |
| 不适合高频小事务 | orders/positions用SQLite（L4） |
| 不适合强一致查询 | positions当前持仓用SQLite |

**结论**：模式③（批量预加载+内存重演）下，ClickHouse所有弱项都被规避，只发挥强项（列式扫描+分区裁剪）。

---

## §5 数据品类全景与库映射

### §5.1 品类总览（69个品类）

> 来源：数据架构.md §1~§6（60个）+ 盲点排查补充（9个）。详见 [品类注册表](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/business_data_categories.yaml)（待建，真源）。

| 品类大类 | 数量 | 性质 | 归属库 |
|---------|:---:|------|--------|
| 行情数据 | 5+5=10 | 原料(固定) | C1 market_clickhouse |
| 基本面数据 | 10 | 原料(固定) | C3 news_clickhouse |
| 另类数据 | 10 | 原料+成品 | C3 news_clickhouse |
| 宏观与跨市场 | 11 | 原料(固定) | C3 news_clickhouse |
| 因子值 | 5大类 | 成品(可预计算) | C2 indicator_clickhouse |
| 技术指标 | 1组 | 成品(可预计算) | C2 indicator_clickhouse |
| 图形识别 | 6类 | 成品(统一引擎输出) | C2 indicator_clickhouse |
| 信号历史 | 1 | 成品(策略算) | C2 indicator_clickhouse |
| 主力行为 | 1 | 成品(模型算) | C2 indicator_clickhouse |
| 板块强度 | 1 | 成品(聚合算) | C2 indicator_clickhouse |
| 知识图谱 | 5类 | 图遍历 | G2 knowledge_graph(Neo4j) |
| 回测结果 | 2 | 成品(回测产出) | C4 backtest_clickhouse |
| 交易事务 | 3 | 事务(实时写) | L4 trading.db(SQLite) |
| **补充品类** | 9 | 见§5.3 | 分散归属 |

### §5.2 品类→库精确映射（表级）

#### C1 market_clickhouse（行情仓库，存L1标准化数据）

| 表名 | 品类 | 性质 | 频率 | 数据源 |
|------|------|------|:----:|--------|
| tick_data | A股3秒Tick | 原料 | 3秒 | miniQMT |
| daily_kline | 日线OHLCV | 成品(聚合) | 日频 | miniQMT/iFind |
| auction_snapshot | 集合竞价快照 | 原料 | 9:15-9:25 | miniQMT |
| index_quote | 指数行情 | 原料 | 3秒 | miniQMT |
| option_iv_surface | 期权IV曲面 | 原料(衍生) | 日频 | iFind/AkShare |
| futures_position | 期货持仓 | 原料(衍生) | 日频 | CZCE/DCE |
| futures_term_structure | 期货期限结构 | 原料(衍生) | 日频 | 交易所 |
| convertible_bond_iv | 可转债隐含波动率 | 成品(算) | 日频 | iFind |

> market_type 字段预留（港股/美股/期货，硬边界后填）

#### C2 indicator_clickhouse（指标与因子仓库）

| 表名 | 品类 | 性质 | Schema | 说明 |
|------|------|------|--------|------|
| factor_values | 因子值（量价/基本面/另类/风险） | 成品 | **窄表7列** | 见§5.4 |
| technical_indicator | 技术指标(MA/MACD/KDJ/RSI/ATR/OBV/VWAP) | 成品 | 宽表 | 数值型 |
| pattern_recognition | 图形识别输出 | 成品 | 宽表 | 类型+置信度+关键点位+方向+胜率+时间级别 |
| signal_history | 信号历史 | 成品 | 窄表 | 策略产出 |
| main_force_behavior | 主力行为模拟 | 成品 | 宽表 | 龙虎榜/大宗/融资融券衍生 |
| sector_strength | 板块强度/热度 | 成品 | 宽表 | 聚合算 |
| risk_model_output | 风险模型(VaR/相关性/波动率曲面) | 成品 | 宽表 | 自算 |

#### C3 news_clickhouse（新闻与宏观仓库）

| 表名 | 品类 | 性质 | 数据源 |
|------|------|------|--------|
| news_raw | 新闻快讯/公告/研报原文 | 原料 | tushare/iFind |
| news_impact | LLM影响值 | 成品(可重算) | LLM计算 |
| macro_data | 中美宏观/FOMC/VIX/外汇/国债/商品 | 原料 | iFind |
| sentiment_data | 舆情/情绪面板/社媒情绪 | 原料+成品 | iFind/tushare/爬虫 |
| financial_data | 财报/股东/调研 | 原料 | iFind |
| credit_spread | 信用利差 | 原料 | 公开数据 |
| analyst_consensus | 分析师一致预期 | 原料 | iFind |
| government_data | 政府公开数据(统计/海关) | 原料 | 统计局/海关 |

#### C4 backtest_clickhouse（回测结果仓库）

| 表名 | 品类 | 性质 |
|------|------|------|
| backtest_results | 回测统计 | 成品(回测产出) |
| backtest_trades | 回测成交 | 成品(回测产出) |

#### G2 knowledge_graph（Neo4j，知识图谱）

| 图谱类型 | 实体数 | 关系数 | 数据源 |
|---------|:------:|:------:|--------|
| 公司图谱 | ~10,000 | ~50,000 | iFind |
| 产业图谱 | 238,000 | 551,000 | iFind |
| 供应链图谱 | ~5,000 | ~20,000 | iFind/年报 |
| 宏观因果链 | ~500 | ~2,000 | iFind+LLM |
| 地缘政治图谱 | ~200 | ~1,000 | 新闻+LLM |

#### L4 trading.db（SQLite，交易事务）

| 表名 | 品类 | 性质 | 理由 |
|------|------|------|------|
| orders | 订单 | 事务(逐笔写) | ClickHouse不适合高频写入 |
| positions | 持仓 | 事务(强一致) | ClickHouse最终一致性不够 |
| risk_snapshots | 风险快照 | 事务 | 实时风控需强一致 |

### §5.3 补充的9个品类（盲点排查）

| # | 新品类 | 归属库 | 性质 | 数据源 |
|---|--------|--------|------|--------|
| 1 | 期权IV曲面 | C1 | 原料(衍生) | iFind/AkShare |
| 2 | 期货持仓 | C1 | 原料(衍生) | CZCE/DCE公开 |
| 3 | 期货期限结构 | C1 | 原料(衍生) | 交易所公开 |
| 4 | 信用利差 | C3 | 原料 | 公开数据 |
| 5 | 可转债隐含波动率 | C1 | 成品(算) | iFind |
| 6 | 社交媒体情绪 | C3 | 成品(NLP) | tushare/爬虫 |
| 7 | 分析师一致预期 | C3 | 原料 | iFind |
| 8 | 政府公开数据 | C3 | 原料 | 统计局/海关 |
| 9 | 风险模型输出 | C2 | 成品(自算) | 自算 |

### §5.4 因子值窄表7列Schema（采纳数据架构.md §3.2）

```
trade_date | symbol | factor_name | factor_value | factor_version | computed_at | quality_flag
```

**窄表好处**：新增因子不改变表结构。宽表通过 ClickHouse PIVOT 按需生成。

### §5.5 硬边界品类（enabled=false预留接口）

| 品类 | 硬边界类型 | 预留方式 |
|------|----------|---------|
| Level-2逐笔成交 | 资金($10K+/年) | 注册表enabled=false |
| Level-2逐笔委托 | 资金 | 注册表enabled=false |
| 卫星图像 | 资金($50K+/年) | 注册表enabled=false |
| 信用卡消费数据 | 合规 | 注册表enabled=false |
| AIS海运数据 | 资金 | 注册表enabled=false |
| Barra因子收益率 | 资金 | 注册表enabled=false，自建风险因子替代 |
| 财报电话会议纪要 | 服务 | 注册表enabled=false |

---

## §6 插拔式品类管理（4层机制）

### §6.1 核心理念

```
传统做法：每加一个品类，改代码、改表、改查询、改回测引擎
   → 牵一发动全身，扩展成本高

插拔做法：品类 = 一个"标准件"，注册即可用
   → 新品类 = 写一个schema文件 + 注册一条记录
   → 引擎自动发现、自动可用
   → 类似USB：插上就能用，拔了不影响其他
```

### §6.2 4层机制

```
┌─ 第1层：品类注册表（Category Registry）─────────────────┐
│  文件：business_data_categories.yaml（唯一真源）         │
│  每个品类一条记录：                                       │
│    category_id / name / engine / table / schema_file    │
│    data_type(原料/成品/事务) / lifecycle / sla_level     │
│    enabled(能造/硬边界) / hard_constraint / calc_mode     │
│  新增品类 = 加一条YAML记录（不改代码）                    │
└──────────────────────────────────────────────────────────┘
                          ↓
┌─ 第2层：DDL-as-Code（Schema即代码）──────────────────────┐
│  每个品类一个schema文件：schemas/categories/xxx.py       │
│  用Python类定义表结构                                    │
│  新品类 = 写一个schema.py文件                            │
│  执行apply_schema.py自动建表                             │
└──────────────────────────────────────────────────────────┘
                          ↓
┌─ 第3层：数据契约（Data Contract CTR-XXX）─────────────────┐
│  每个品类定义一个契约：                                   │
│    输入Schema / 输出Schema / 质量门禁 / SLA              │
│  新品类接入 = 定义CTR-XXX契约 + 实现采集器               │
└──────────────────────────────────────────────────────────┘
                          ↓
┌─ 第4层：品类发现与路由（CategoryManager）────────────────┐
│  一个CategoryManager类，启动时扫描注册表                 │
│  自动发现所有enabled品类                                 │
│  回测引擎/实盘引擎按category_id请求数据                 │
│  DatabaseService按engine字段路由到对应库                 │
│  新品类注册后，引擎自动可用（零代码改动）                 │
└──────────────────────────────────────────────────────────┘
```

### §6.3 插拔流程示例

```
新增"卫星停车场图像"品类（硬边界，预留接口）：
Step1: business_data_categories.yaml加一条
  category_id: SAT_PARKING / engine: parquet / enabled: false
  hard_constraint: "资金硬边界$50K+/年"
Step2: 写 schemas/categories/sat_parking.py
Step3: 定义 CTR-XXX 契约
Step4: 完成 → CategoryManager自动发现(不加载) → 未来enabled=true即启用
```

### §6.4 与项目现有机制对接（向内收原则）

| 机制 | 复用现有能力 | 说明 |
|------|------------|------|
| 品类注册表 | 扩展 capability_canonical_file_registry.yaml 机制 | 同YAML注册表模式 |
| DDL-as-Code | 复用 DDL-as-Code 模式（见 c1_market 母蓝图） | 已有DDL-as-Code先例 |
| 数据契约 | 复用 CTR-001~008 契约体系 | 数据架构.md §16已定义 |
| 品类发现 | 复用 CapabilityLookup 类 | 已有发现机制 |
| 门禁 | 复用 GitCommitGateway + create_guard.py | 已有门禁 |

**关键**：不新建"品类管理系统"，扩展现有注册表+契约+发现机制。符合"向内收"原则。

### §6.5 关键设计原则

| 原则 | 内容 | 理由 |
|------|------|------|
| 注册表唯一真源 | business_data_categories.yaml | 对齐YAML铁律 |
| DDL-as-Code | 表结构用Python定义 | 版本可控、AI可生成 |
| engine字段路由 | 品类指定engine，DatabaseService路由 | 新引擎可插入 |
| enabled二元开关 | 每品类true/false | 硬边界品类预留接口不启用 |
| 契约保证质量 | 每品类有CTR契约 | 品类间质量一致 |
| 零代码扩展 | 新品类只加注册+schema | 插拔核心 |

---

## §7 回测/实时计算调度策略

> 品类增加（60→69）后，库结构/引擎不变，但调度策略需补充。本章定义5个优化方案。

### §7.1 风险1：内存预算 → 分层加载

```
不再"全量加载"，改为"按需分层加载"：
├─ 热数据（常驻内存）：tick + 因子值 + 当前持仓
├─ 温数据（按时间窗加载）：技术指标 + 图形识别（回测时间段内）
├─ 冷数据（按需点查）：新闻原文 + 宏观（事件驱动，按时间点取）
└─ 结果：内存占用从63G降到~30G，留出计算空间
```

**内存评估（64G）**：

| 数据类型 | 单标的1年 | 100标的1年 | 分层后占用 |
|---------|:--------:|:---------:|:---------:|
| 3秒tick | ~480MB | ~48GB | 热层常驻 |
| 因子值(64因子) | ~50MB | ~5GB | 热层常驻 |
| 日线 | ~2MB | ~200MB | 温层 |
| 新闻原文 | — | ~1GB | 冷层按需 |

### §7.2 风险2：加载时间 → 并行加载

```
69张表不再串行查询，改并行：
├─ ClickHouse支持并发查询
├─ Python用asyncio/threading并行加载
├─ 按品类分组并行（行情组/因子组/新闻组同时加载）
└─ 结果：加载时间从69×T降到~5×T（按组分批并行）
```

### §7.3 风险3：多频率时间对齐 → 统一时间网格

```
定义"回测时间网格"（基于最小频率）：
├─ 网格步长 = 3秒（tick频率）
├─ 高频数据（tick/指数）：按网格点取值
├─ 低频数据（日线/因子）：AS OF取最近值（内存里实现）
├─ 事件数据（新闻/宏观）：注入到对应时间点
└─ 结果：统一网格对齐，规避ClickHouse无AS OF JOIN问题（内存里做）
```

### §7.4 风险4：实时计算调度 → 优先级队列

```
复用数据架构.md的P0/P1/P2三级SLA：
├─ P0（3秒内必须算完）：tick→因子→信号→决策→风控→执行
├─ P1（盘后算）：日线/基本面/因子历史
├─ P2（可延后）：图谱/研报/归档
└─ 实时引擎按优先级调度，P0抢占资源
```

### §7.5 风险5：回测真实性 → 品类计算模式标注

```
每个品类在注册表标注 calc_mode：
├─ mode=replay（回测时实时重算，保证=实盘）
│   如：信号生成、策略决策、权重调整
├─ mode=preload（回测时用预计算值，性能优先）
│   如：技术指标(KDJ/MACD)、图形识别、因子值
├─ mode=hybrid（预计算+回测时微调）
│   如：新闻影响值（原料预计算，权重回测调）
└─ 回测引擎按calc_mode决定每个品类怎么处理
```

### §7.6 回测 vs 实时计算（两者并重）

| 维度 | 回测 | 实时计算 |
|------|------|---------|
| 目标 | 迭代效率 | 实盘不拉垮 |
| 数据来源 | 仓库层批量加载 | 实时接入+热缓存 |
| 计算位置 | 内存工作台 | 内存工作台 |
| 延迟要求 | 越快越好 | <15秒（tick→信号） |
| 共享 | **同一套计算逻辑** | **同一套计算逻辑** |

**关键**：回测和实盘共用同一套计算引擎，数据源不同（历史批量vs实时流）。回测真实性=实盘真实性。

---

## §8 能造/硬性边界清单

### §8.1 能造现在就造（硬性边界外）

| # | 库/组件 | 引擎 | 理由 |
|---|---------|------|------|
| 1 | C1~C4 仓库层 | ClickHouse | AUM即将>200万，直接上目标引擎 |
| 2 | L4 trading.db | SQLite | 事务层，单机够用 |
| 3 | G2 knowledge_graph | Neo4j | 551K关系，社区版免费 |
| 4 | H1 redis_hot | Redis | 64G内存够，实盘热缓存 |
| 5 | E1 event_store | Parquet+CQRS | 事件溯源，实盘支撑 |

### §8.2 硬性边界不能造（enabled=false预留）

| # | 品类 | 硬边界类型 | 说明 |
|---|------|----------|------|
| 1 | Level-2逐笔成交/委托 | 资金($10K+/年) | 券商额外权限 |
| 2 | 多市场数据(港股/期货) | 数据源(需采购) | 待资金/账户满2年 |
| 3 | 卫星图像 | 资金($50K+/年) | 机构级数据 |
| 4 | 信用卡消费数据 | 合规 | 个人隐私 |
| 5 | AIS海运数据 | 资金 | 机构级数据 |
| 6 | Barra因子收益率 | 资金 | 自建风险因子替代 |
| 7 | 财报电话会议纪要 | 服务 | 需买Bloomberg服务 |

---

## §9 新闻数据分层设计（原料/成品）

### §9.1 新闻数据流

```
新闻原文(原料) ──清洗──→ 结构化新闻 ──LLM计算──→ 影响值(成品)
     ↓                                    ↓
 存C3 news_clickhouse           存C3 news_clickhouse
   news_raw表                    news_impact表
```

### §9.2 原料 vs 成品

| 层 | 内容 | 存储 | 回测时 |
|---|------|------|--------|
| 原料层 | 新闻原文、时间、来源 | C3 news_raw（固定） | 批量加载到内存 |
| 成品层 | LLM算出的影响值+权重 | C3 news_impact（可重算） | calc_mode=hybrid，权重可调 |

**关键**：成品层不是"一个固定值"，而是"一套可重算的LLM调用"。回测时改变策略参数 = 改变LLM的prompt/权重 = 重新算影响值。原料不变，成品可变。

---

## §10 图形识别统一引擎

> 采纳数据架构.md §58 决策：1个统一引擎替代20+独立图形识别模块。

### §10.1 图形模式库（6类）

| 图形类别 | 具体图形 | 关键点位 |
|----------|---------|---------|
| 反转图形 | 头肩顶/底、双顶/底(W顶/底)、三重顶/底、圆弧顶/底 | 颈线位、突破点 |
| 持续图形 | 三角形（对称/上升/下降）、旗形、矩形、楔形 | 突破方向、目标位 |
| 趋势图形 | 上升趋势线、下降趋势线、通道线 | 趋势线触点、通道上下轨 |
| 支撑阻力 | 水平支撑/阻力、整数关口、前高/前低 | 支撑位、阻力位 |
| 缠论图形 | 笔、线段、中枢、背驰 | 中枢区间、三类买卖点 |
| 波浪图形 | 推动浪(5浪)、调整浪(3浪)、延长浪 | 浪的起点/终点 |

### §10.2 统一识别算法

| 算法 | 适用场景 |
|------|---------|
| DTW (Dynamic Time Warping) | 任意图形匹配 |
| CNN分类 | 固定类别图形识别 |
| Transformer | 时序图形识别 |
| 规则引擎 | 简单图形（支撑阻力/趋势线） |

### §10.3 输出格式（pattern_recognition表）

| 字段 | 说明 |
|------|------|
| 图形类型 | 头肩顶/双底/三角形/... |
| 置信度 | 0-1，DTW距离/CNN概率 |
| 关键点位 | 颈线位/突破点/目标位 |
| 预测方向 | 看涨/看跌/中性 |
| 历史胜率 | 该图形的历史预测胜率 |
| 时间级别 | 5min/15min/30min/60min/日线/周线 |

---

## §11 演进路径

> 基于用户"能造现在就造"逻辑，不再分阶段门禁，只分"现在建"和"硬边界后建"。

### §11.1 现在建（立即施工）

| # | 库/组件 | 引擎 | 施工蓝图 |
|---|---------|------|---------|
| 1 | C1 market_clickhouse | ClickHouse | sub_blueprints/c1_market_clickhouse.md |
| 2 | C2 indicator_clickhouse | ClickHouse | sub_blueprints/c2_indicator_clickhouse.md |
| 3 | C3 news_clickhouse | ClickHouse | sub_blueprints/c3_news_clickhouse.md |
| 4 | C4 backtest_clickhouse | ClickHouse | sub_blueprints/c4_backtest_clickhouse.md |
| 5 | G2 knowledge_graph | Neo4j | sub_blueprints/g2_knowledge_graph_neo4j.md |
| 6 | L4 trading.db | SQLite | sub_blueprints/l4_trading_sqlite.md |
| 7 | H1 redis_hot | Redis | sub_blueprints/h1_redis_hot.md |
| 8 | E1 event_store | Parquet+CQRS | sub_blueprints/e1_event_store.md |
| 9 | 品类注册表 | YAML | business_data_categories.yaml |

### §11.2 硬边界后建（enabled=false预留）

| # | 品类 | 触发条件（硬边界解除） |
|---|------|---------------------|
| 1 | Level-2逐笔 | 资金到位（$10K+/年） |
| 2 | 多市场数据 | 数据源采购/账户满2年 |
| 3 | 卫星图像 | 资金到位（$50K+/年） |
| 4 | Barra因子 | 资金到位（或自建风险因子成熟） |

---

## §12 与专业机构对标

| 维度 | 专业机构 | 本方案 | 对齐情况 |
|------|---------|--------|---------|
| 时序引擎 | ClickHouse/Kafka | ClickHouse | ✅ 对齐 |
| 事务引擎 | PostgreSQL | SQLite | 🟡 单机限制，单人够用 |
| 回测架构 | 内存重演 | 内存重演 | ✅ 对齐（业界主流） |
| 新闻处理 | NLP预处理+实时算 | 原料/成品分层 | ✅ 对齐 |
| 多市场 | 多库分市场 | 单库字段标记 | 🟡 灵活但容量需监控 |
| 图形识别 | 统一引擎 | 统一引擎(DTW/CNN) | ✅ 对齐 |
| 知识图谱 | Neo4j | Neo4j | ✅ 对齐 |
| 品类管理 | 定制化 | YAML注册表+插拔 | ✅ 对齐（个人场景更轻量） |
| AI开发 | 人类施工 | AI读蓝图施工 | ⚠️ 需蓝图无歧义（已约束） |

**结论**：个人量化场景下可达专业机构水准，核心差距在单机容量（ClickHouse单机TB级，足够长远）。

---

## §13 100% AI开发的特殊约束

> AI是"听话的施工队"但不会"猜"。本母蓝图及子蓝图必须满足以下约束。

| 约束 | 要求 | 落实方式 |
|------|------|---------|
| 无歧义 | 每个决策二选一/三选一，明确指定 | 本母蓝图所有决策已明确 |
| 约束明确 | 每个库写清引擎选择理由、禁止项 | §4 引擎选型 + §8 能造/硬边界 |
| 可自动施工 | DDL能被AI执行 | DDL-as-Code（§6.2第2层） |
| 真源唯一 | 每个库真源只在一个地方 | 品类注册表YAML唯一真源 |
| 门禁触发明确 | 硬边界品类写清触发条件 | §8.2 硬边界清单 |
| 插拔扩展 | 新品类零代码改动 | §6 插拔式4层机制 |

---

## §14 子蓝图索引

| 子蓝图 | 路径 | 状态 | 细化程度 |
|--------|------|:----:|---------|
| D_DATA datasource_core（上游） | ../_domain_data/blueprint.md | 🔄重建中(v4.0.0) | 接口契约 |
| C1 market_clickhouse | sub_blueprints/c1_market_clickhouse.md | ⬜待建 | 字段级DDL |
| C2 indicator_clickhouse | sub_blueprints/c2_indicator_clickhouse.md | ⬜待建 | 字段级DDL |
| C3 news_clickhouse | sub_blueprints/c3_news_clickhouse.md | ⬜待建 | 字段级DDL |
| C4 backtest_clickhouse | sub_blueprints/c4_backtest_clickhouse.md | ⬜待建 | 字段级DDL |
| G2 knowledge_graph(Neo4j) | sub_blueprints/g2_knowledge_graph_neo4j.md | ⬜待建 | 字段级DDL |
| L4 trading.db(SQLite) | sub_blueprints/l4_trading_sqlite.md | ⬜待建 | 字段级DDL |
| H1 redis_hot | sub_blueprints/h1_redis_hot.md | ⬜待建 | 字段级DDL |
| E1 event_store | sub_blueprints/e1_event_store.md | ⬜待建 | 字段级DDL |
| 品类注册表 | business_data_categories.yaml | ⬜待建 | YAML真源 |

---

## §15 待办与下一步

1. **创建品类注册表** business_data_categories.yaml（69品类+9补充=78条记录）
2. **起草各子施工蓝图**（C1~C4/G2/L4/H1/E1，字段级DDL-as-Code）
3. **market.duckdb 迁移**：8表数据迁移到C1~C4+L4
4. **CategoryManager 实现**：扩展现有 CapabilityLookup
5. **回测引擎设计**：基于§7调度策略，与业务数据库协同设计

---

> **本文档为母蓝图，表级细化。字段级DDL见各子施工蓝图。**
> **推导过程完整记录**：[业务数据库架构_讨论记录.md](file:///D:/ZephyrAlpha/docs/_working/业务数据库架构_讨论记录.md)（11章）
