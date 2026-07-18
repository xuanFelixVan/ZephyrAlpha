---
module_id: VIEW-04PRINC-DATA
title: Data Architecture Principles / 数据架构原则
doc_type: architecture_view
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-05-DATA-ARCH
related_rationale:
- R36
related_open_questions: []
tags:
- data-architecture
- pit
- lineage
- survivorship
- master-data
- data-quality
- feature-store
- retention
summary: 数据架构永恒原则——PIT 红线、Survivorship Bias 防御、血缘三层、MDM 三件套、质量门禁五类断言、保留与归档、三维分类。派生数据（19 实体清单、字段级 schema）由 05_dataflow_architecture/data_inventory.md 自动生成。
date: '2026-07-19'
ttl: permanent
---

# Data Architecture Principles / 数据架构原则

> 本文档从 `target_architecture/data_architecture.md`（已删除）提取永恒指导原则。
> 派生数据（实体清单、字段级 schema、血缘图）由以下机制自动生成：
> - `scripts/governance/d5_architecture/generators/generate_data_inventory.py` → `05_dataflow_architecture/data_inventory.md`
> - `scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py` → 跨域数据流图
> - 字段级 schema 真源在 `03_modules/_domain_data/`（D_DATA_ENG 域）

## 1. 本原则的定位

数据架构原则回答"系统里**业务数据对象**如何被正确处理"的**永恒约束**——独立于具体存储技术、字段 schema、调度工具选型。这些原则在任何技术栈下都成立，是量化系统的红线。

**主要读者**：量化研究员（理解 PIT/Survivorship 不会被回测撒谎）、数据工程师（落 schema 与 lineage 注册）、风控/合规（理解数据可信链）、AI 架构师（理解 factor → signal → order 的端到端血缘）。

## 2. Point-in-Time (PIT) 红线

> **PIT 是量化系统的红线**：任何因子值、信号、回测结果都必须能回答"在过去某一时刻 T，使用当时**确实可获得**的数据，会算出什么"。违反 PIT = 回测撒谎 = 实盘必亏。

### 2.1 三个核心字段（强制 schema）

凡 PIT 敏感（🔴 高）的实体，schema 中**必须**含：

| 字段 | 含义 | 业界对位 |
|------|------|---------|
| `asof_date` / `valid_time` | 数据所描述的"业务时间"（事件本身发生的时刻） | TimescaleDB / SQL:2011 valid time |
| `ts_ingest` / `transaction_time` | 数据**实际进入系统**的时间 | SQL:2011 transaction time / bitemporal |
| `vendor_release_ts` | 外部 vendor 把这条数据**对外发布**的时间（财报口径关键） | Bloomberg PIT / FactSet PIT |

**铁律**：任意因子计算 / 回测查询，**只能用 `vendor_release_ts ≤ T` 且 `ts_ingest ≤ T`** 的数据。`asof_date` 仅用作语义对齐，不做过滤条件。

### 2.2 PIT 违反的三种典型场景与防御

| 场景 | 例子 | 防御 |
|------|------|------|
| **Look-ahead bias / 前视偏差** | 用今天收盘价做今天开盘的决策 | factor 必须显式声明 `asof_offset`（如"昨日收盘后可知"） + fitness function `test_no_lookahead_bias.py` 在 CI 强制扫描 |
| **Restated data / 财报修订** | Q1 财报 4/30 公布，6/15 修订；回测 5/15 用了 6/15 修订版 | 财务实体存 bitemporal，查询走 `vendor_release_ts ≤ T` |
| **Index rebalance / 指数成分调整** | 沪深 300 半年调整，回测 2024 年 Q1 不能用 Q3 后调进的成分股 | `IndexConstituent` 必须 bitemporal；查询用 PIT API |

### 2.3 PIT 查询的四条实现路径（架构原则）

1. **bitemporal 表** —— OLTP 主数据用 valid_time + transaction_time 双时间戳建模
2. **append-only event log** —— 事件实体（Tick/Fill/Signal）天然 PIT，永不修改
3. **PIT-safe view layer** —— 因子计算前必须经过统一的 `pit_view(entity, asof=T)` 函数封装（具体实现归 D_DATA_ENG 域）
4. **CI fitness function** —— `test_no_lookahead_bias.py` 在 PR 阶段扫描所有因子代码，禁止任何 `df.loc[df.date <= today]` 之外的时间过滤模式

> **原则边界**：本文档只定义"原则与契约"；具体 SQL/代码归 D_DATA_ENG / D_FACTOR 域、`scripts/fitness_functions/`。

## 3. Survivorship Bias 防御原则

> **核心问题**：用今天还活着的股票池回测过去 10 年，会高估收益（已退市的失败股票被自动排除）。

### 3.1 三类需要处理的"消失/变化"

| 类型 | 例子 | 处理原则 |
|------|------|---------|
| **退市 / Delisting** | 长航油运退市、瑞幸退市 | `Security.delisting_date` + `status='delisted'`，查询时按 PIT 包含 |
| **合并 / Merger** | 中国南车 + 中国北车 → 中国中车 | 旧 symbol 在 `delisting_date` 后映射到新 symbol，保留 mapping 表 |
| **指数成分调整** | 沪深 300 季度调仓 | `IndexConstituent` bitemporal，PIT 查询返回当时成分 |

### 3.2 反幸存者偏差的查询契约

凡构建历史投资域（universe），**必须**经过统一接口：

```text
universe = build_universe(
    asof=T,                     # PIT 时点
    exchange='SSE,SZSE',
    include_delisted=True,      # 默认 True；False 必须在 KB 决策记录中说明理由
    index_filter=('CSI300', T)  # PIT 指数成分过滤
)
```

**禁止**直接 `SELECT * FROM security WHERE status = 'active'`——这是幸存者偏差的最常见入口。`scripts/fitness_functions/test_no_survivorship_bias.py` 应扫描此类反模式。

### 3.3 退市股票的数据保留

| 数据 | 退市后保留期 | 理由 |
|------|------------|------|
| `Security` 主数据 | **永久** | PIT 查询必备 |
| `Bar` / `Tick`（退市前） | **永久** | 回测必备 |
| 退市后的"幽灵价格"（清算价 / 0） | 不补造 | 用 `status` 字段表达更准确 |

### 3.4 与 PIT 的关系

PIT 是"时间维度真实"，Survivorship 是"对象维度真实"——两者**正交且必须同时成立**。任何回测的 universe 构造必须**两条都过**才算可信。

## 4. Data Lineage 三层原则

> **目标**：从任何一条 PnL 出现异常，能在分钟级反向追溯到具体的 Tick / vendor / 计算代码版本。

### 4.1 血缘三层

| 层级 | 内容 | 真源 |
|------|------|------|
| **Schema lineage** | 字段级映射：`PnL.realized` ← `Fill.price * Fill.qty` ← ... | `03_modules/_domain_data/`（D_DATA_ENG 域）|
| **Pipeline lineage** | 任务级 DAG：`compute_factor_X` 依赖 `load_bar_eod`、`load_corporate_action` | 调度器元数据（Airflow / Dagster）→ OpenLineage |
| **Instance lineage** | 实例级：`FactorValue(factor=mom_20, symbol=600519, asof=2025-01-15)` 追溯到 `Bar(...)` 实例集合 | 每个派生实体的 `lineage_root` 字段 |

### 4.2 血缘标准与工具对位

| 业界标准 / 工具 | 在本项目中的位置 |
|----------------|----------------|
| **OpenLineage** | 血缘事件交换格式（推荐采纳的接口标准） |
| **Marquez / DataHub** | 血缘存储与可视化（具体选型归 04-TA） |
| **MLflow** | 模型训练血缘（归 D_ML_TRAIN 域）|

> **原则边界**：本文档定义"必须有 lineage_root"、"必须实现 OpenLineage 接口"；**不**做工具选型。

### 4.3 血缘的 fitness function 契约

`scripts/fitness_functions/test_lineage_completeness.py` 应保证：
- 任何派生实体（FactorValue / Signal / PnL / RiskMetric）创建时必填 `lineage_root`
- 任何 lineage_root 必须能解析出至少一条上游边
- 任何代码层 commit 不允许引入"无血缘的派生实体"

## 5. Master Data Management (MDM) 三件套

> **MDM 三件套**：证券主数据 / 交易日历 / Corporate Action。这三者一旦错，下游全错；必须**单点维护、版本化、bitemporal**。

### 5.1 三件套责任原则

| 主数据 | Steward | bitemporal | 校验门禁 |
|--------|---------|----------|---------|
| `Security` / `Instrument` | 数据工程师 | ✅ 必须 | symbol 唯一性 + ISIN 校验 + delisting_date 不可回溯修改 |
| `TradingCalendar` | 数据工程师 | ❌ 不需要（可直接覆盖未来） | 与 vendor 三家以上交叉验证 |
| `CorporateAction` | 数据工程师 + 策略研究员复核 | ✅ 必须 | 比例合理性（送转不超 1:10）+ 修订必须留旧版 |

### 5.2 主数据的"三禁三必"

| 禁止 | 必须 |
|------|------|
| 禁止任何业务模块**绕过 MDM 直接读 vendor** | 必须经过 D_MKT_DATA `connectors/`（ACL）+ MDM 服务 |
| 禁止 `UPDATE security SET delisting_date=...`（破坏 bitemporal） | 必须 INSERT 新版本 + 旧版本标记 superseded |
| 禁止前端/AI 直接发起主数据修改 | 必须走"修改提案 → Steward 复核 → 双人签字 → 落库"流程 |

## 6. Data Quality Gates 五类断言

> **设计原则**：数据质量不是"运行时偶尔扫描一下"，而是"任何数据写入 / 任何代码合入都必须先过断言"。对齐 Great Expectations / Soda Core 业界规范。

### 6.1 五类标准断言

| 类别 | 断言示例 | 触发时机 |
|------|---------|---------|
| **Schema** | 字段类型 / 必填 / 取值域（enum） | ingest 时（fail-fast）+ CI |
| **Range** | `0 < price < 10000`、`volume ≥ 0`、`abs(daily_return) < 0.5`（非异常停牌） | ingest 时 + 每日报表 |
| **Null / Completeness** | 关键字段缺失率 < 0.01% | 每日 ETL 后 |
| **Freshness** | `max(ts_ingest)` 与当前时间差 < SLA | 调度器健康检查 |
| **Distribution Drift** | 因子值分布与近 60 日基线 PSI < 0.2 | 每日因子计算后 |

### 6.2 门禁触发与失败处理

| 严重级 | 触发动作 | 处理 |
|--------|---------|------|
| 🔴 Fatal（schema 违反 / 重复主键） | 阻塞 ingest，告警 | 修数据源或修代码，**不绕过** |
| 🟠 Critical（range 越界 / freshness 严重超时） | 数据隔离到 quarantine，下游消费方收到 stale 标记 | Steward 24h 内裁决 |
| 🟡 Warning（drift / 缺失率小幅升高） | 告警 + dashboard | 进入 backlog 排查 |

### 6.3 业界工具映射原则

| 业界工具 | 本项目用途 |
|---------|----------|
| **Great Expectations** | 适合 batch 断言（EOD bar / 因子值） |
| **Soda Core** | 适合 SQL-first 团队，与 dbt 集成好 |
| **自研 fitness functions** | PIT / Survivorship / Lineage 这三类**业界工具不覆盖**的量化专属断言，必须自研 |

> **原则边界**：本文档给"**断言契约清单**"；具体 Python/SQL 代码落 `scripts/fitness_functions/`、`src/zephyr/data/quality_gate/`。

## 7. Data Retention & Archival 原则

### 7.1 保留策略原则矩阵

| 数据类别 | 热层保留 | 温层保留 | 冷层保留 | 删除？ |
|------|---------|---------|---------|--------|
| Tick / OrderBookSnapshot | 30 天 | 1 年 | 永久（对象存储） | 否 |
| Bar (intraday) | 90 天 | 3 年 | 永久 | 否 |
| Bar (EOD) | 永久（温层） | — | — | 否 |
| FactorValue（活跃因子） | 永久（温层） | — | — | 否 |
| FactorValue（退役因子） | — | 1 年 | 永久 | 否 |
| Order / Fill | 1 年（热） | 7 年（温） | 永久（冷） | 否（合规） |
| Position / PnL | 永久 | — | — | 否 |
| RiskMetric（实时） | 1 年 | 3 年 | 永久 | 否 |
| 临时回测产物 | 30 天 | — | — | **是**（自动清理） |

### 7.2 归档三原则

- **触发**：调度器按数据 `ts` 字段超过阈值时，移动到冷层，元数据登记到 archive index
- **可恢复性**：冷层数据必须可在 24h 内重建为温层可查（重测、合规调阅）
- **不可变性**：归档数据走 WORM（Write Once Read Many）存储，对应合规留痕要求

### 7.3 监管驱动的保留要求

具体监管条款映射归 D_COMPLIANCE 域。本原则只声明"Order/Fill 必须保留 7 年（中国/美国证监会通用要求）"，具体条款引用待合规域激活。

## 8. Data Classification 三维分类

按"温度 × 节奏 × 来源"三维分类，每个数据实体在三轴各占一格，用于驱动存储选型（04-TA）、备份策略（§7）、访问控制（06-Security）。

### 8.1 三轴定义

| 轴 | 取值 | 判定规则 |
|----|------|---------|
| **温度** | 热（Hot） / 温（Warm） / 冷（Cold） | 热 = 实时读写，分钟级访问；温 = 当日/近期，分钟到小时；冷 = 历史，按需重载 |
| **节奏** | 流（Stream） / 批（Batch） | 流 = 持续到达，无明确边界；批 = 周期性快照或夜间任务 |
| **来源** | 外（External） / 内（Internal） / 派生（Derived） | 外 = 外部 vendor；内 = 系统自产事件；派生 = 由其他实体计算得出 |

### 8.2 分类驱动的设计后果

| 分类组合 | 必备能力 | 落到哪个视图 |
|---------|---------|-------------|
| 热 × 流 × 内/外 | 低延迟 ingest、背压控制、at-least-once | 03-AA D_MKT_DATA / 04-TA 流处理选型 |
| 温 × 批 × 派生 | 幂等重算、checkpoint、版本号 | 03-AA D_FACTOR/D_ASHARE_SIGNAL、04-TA 调度器 |
| 冷 × 批 × * | 列存归档、按需重载、生命周期策略 | §7 + 04-TA 对象存储 |

## 9. 与其他视图的边界

### 9.1 边界四象限

| 视图 | 关心 | 不关心 | 与 DA 的接口 |
|------|------|-------|-------------|
| **02-IA** Information Architecture | `docs/` 顶级目录、文档生命周期、frontmatter schema | 业务数据对象 | **零重叠**——IA 是"文档抽屉"，DA 是"业务实体"，两者完全正交 |
| **03-AA** Application Architecture | 域 src/、模块边界、ACL、扩展点 | 数据实体的字段定义 | DA 的实体被 AA 的域处理：D_MKT_DATA 落 Tick/Bar、D_FACTOR 算 FactorValue、D_EX_CORE 产 Order/Fill、D_TRADING 算 PnL/RiskMetric |
| **04-TA** Technology Architecture | 时序库选型、对象存储选型、调度器选型 | 数据实体本身有什么字段 | DA 给出"温度 × 节奏"分类，TA 据此选具体技术栈（DA 不指定 PostgreSQL 还是 ClickHouse） |
| **D_SECURITY** 安全域 | 字段级访问控制、PII 脱敏 | 数据怎么计算 | DA 给出 `classification` 标签，Security 据此设权限 |
| **D_DATA_ENG** 数据工程域 | 字段级 schema、SQL DDL、具体调度脚本 | 跨域数据原则 | DA 是"原则与契约"，D_DATA_ENG 是"schema 真源与执行" |

### 9.2 一句话区分 DA vs IA

> **02-IA**："系统里有哪些**文档抽屉**？文档怎么流转？" — 治理 `docs/` 这个仓库本身。
>
> **05-DA**（本文）："系统里有哪些**业务数据**？数据怎么流转？" — 治理交易系统真正处理的对象。
>
> 类比：IA 管"图书馆有哪些书架"，DA 管"账本上记了哪些资金往来"。

### 9.3 DA 不做什么（防止越界）

| DA 不做的事 | 归属视图 |
|------------|---------|
| 字段级 schema DDL | D_DATA_ENG 域 |
| 选具体存储产品（TimescaleDB vs ClickHouse vs DuckDB） | 04-TA |
| 因子计算的具体算法 | D_FACTOR / D_RESEARCH 域 |
| 监管条款映射 | D_COMPLIANCE 域 |
| 加密 / 脱敏算法 | D_SECURITY 域 |
| AI 自治的数据血缘自动发现 | D_AUTONOMY_CORE 域（未来） |

## 10. 与其他原则文档的关系

| 其他文档 | 关系 |
|---|---|
| `architecture_principles.md` | 本文是总纲 §4 核心架构决策的数据架构子原则 |
| `capability_maturity_principles.md` | 数据域（D_MKT_DATA/D_FACTOR/D_DATA_ENG 等）的成熟度评估遵循该文定义 |
| `05_dataflow_architecture/data_inventory.md` | 自动生成的实体清单（派生数据），实体定义遵循本文 PIT/lineage/MDM 原则 |
| `03_modules/_domain_data/` | 字段级 schema 真源（D_DATA_ENG 域物化点），遵循本文 PIT/质量门禁原则 |