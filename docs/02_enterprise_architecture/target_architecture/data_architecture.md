---
module_id: VIEW-05-DATA-ARCH
title: Target Architecture — Data Architecture / 目标架构：数据架构
doc_type: architecture_view
status: Active
version: 1.0.2
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale: R36
related_open_questions: []
tags:
- data-architecture
- togaf
- pit
- lineage
- survivorship
- master-data
- data-quality
- feature-store
summary: TOGAF Data Architecture 视图（DA View）。回答系统中"业务数据对象有哪些、如何分类、如何避免未来数据泄露（PIT）、如何处理退市股票（Survivorship
  Bias）、如何追踪因子血缘、如何治理证券主数据 / 交易日历 / Corporate Action、如何在 CI 中执行数据质量门禁、如何归档"。本视图独立于
  02-IA（IA 讲 docs/ 抽屉的"信息资产组织"，DA 讲业务"数据对象"），与 03-AA / 04-TA 通过明确边界关系图衔接。v1.0.0 为新建版本（非从
  IA 迁移而来——经查 02-IA v1.1.0 全文不含业务数据对象，DA 此前一直缺位，详见 R36）。
date: '2026-07-04'
ttl: permanent
---

# Target Architecture — Data Architecture
# 目标架构：数据架构（DA View）

---

## 1. Purpose of this view / 本视图的用途

The Data Architecture view answers questions about the **business data objects** flowing through the system, independent of how those objects are stored, indexed, or rendered as documents.

数据架构视图回答关于"系统里**业务数据对象**"的全部问题，**独立于**这些对象具体如何存储、索引、或被渲染成文档：

- 系统里到底有哪些核心数据实体？（Data Entity Catalog / 数据实体清单）
- 数据按 冷/温/热 × 批/流 × 内/外 三维如何分类？（Data Classification / 数据分类）
- 如何确保任意时点回看的因子值"当时确实可知"？（Point-in-Time / PIT）
- 退市、停牌、合并、分拆的股票如何在历史数据里正确表达？（Survivorship Bias / 幸存者偏差）
- 一个因子值出问题时，如何反向追溯到原始 tick？（Factor Lineage / 因子血缘）
- 证券基础信息、交易所日历、Corporate Action 由谁负责单点维护？（Master Data Management）
- 数据质量在 CI 流水线中由哪些断言保护？（Data Quality Gates）
- 不同热度数据保留多久？归档到哪里？（Retention & Archival）
- 本视图与 IA / AA / TA 边界在哪？（§10）

> **本视图主要读者**：量化研究员（理解 PIT/Survivorship 不会被回测撒谎）、数据工程师（落 schema 与 lineage 注册）、风控/合规（理解数据可信链）、AI 架构师（理解 factor → signal → order 的端到端血缘）。

---

## 2. Data Entity Catalog / 数据实体清单

> 本节列出系统终态全部**核心数据实体**（Core Data Entities），共 19 条。每条给出：实体名（保留英文）、所属域、生命周期状态机、PIT 敏感度、典型存储介质（仅作 hint，真源在 04-TA），与上下游主要关系。
>
> **粒度原则**：DA 只列 entity 与关键字段族，不列字段级 schema（字段级 schema 真源在 [`03_modules/_domain_data/`](../../03_modules/_domain_data/)，由 D_DATA_ENG 域注册）。

### 2.1 Market Data 域（行情数据）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E01 | `Tick` | 单笔成交/盘口快照（symbol, ts_exchange, ts_ingest, price, volume, side, bid/ask 五档） | append-only，永不修改 | 🔴 高 | 列存 / 时序库 |
| E02 | `Bar` | OHLCV 聚合（symbol, frequency=1m/5m/1d, ts_open, ts_close, open, high, low, close, volume, vwap） | append-only；当日 bar 在收盘前可滚动更新 | 🔴 高 | 时序库 |
| E03 | `OrderBookSnapshot` | L2 深度快照（symbol, ts, levels[10]） | append-only | 🔴 高 | 时序库 / 对象存储 |
| E04 | `CorporateAction` | 分红 / 拆股 / 配股 / 合并事件（symbol, ex_date, action_type, ratio, cash_amount） | 主数据，可修订（修订必须留痕） | 🔴 高（影响复权） | OLTP + 历史快照 |

### 2.2 Reference & Master Data 域（参考与主数据）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E05 | `Security` / `Instrument` | 证券主数据（symbol, isin, exchange, sector, industry, listing_date, delisting_date, status, currency） | 主数据，**必须保留历史版本**（退市后保留） | 🔴 高（survivorship 关键） | OLTP + bitemporal 表 |
| E06 | `TradingCalendar` | 交易日历（exchange, date, is_trading, half_day, session_open, session_close） | 主数据，按月维护 | 🟡 中 | OLTP |
| E07 | `IndexConstituent` | 指数成分（index_code, symbol, weight, effective_date, end_date） | 主数据，**bitemporal**（必须 PIT 查询） | 🔴 高 | OLTP + bitemporal 表 |

### 2.3 Research & Factor 域（研究与因子）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E08 | `Factor` | 因子定义（factor_id, name, formula_ref, frequency, asof_offset, lineage_root） | 注册即不可变（变更=新版本） | — | OLTP（registry） |
| E09 | `FactorValue` | 因子取值（factor_id, symbol, asof_date, ts_calc, value, status） | append-only；**必须含 asof_date 与 ts_calc** | 🔴 高（PIT 红线） | 列存 / 特征仓 |
| E10 | `FeatureSet` | 特征集（feature_set_id, factor_ids[], asof_date, lineage_root） | append-only；快照式 | 🔴 高 | 特征仓 / 对象存储 |

### 2.4 Signal & Strategy 域（信号与策略）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E11 | `Signal` | 策略输出信号（strategy_id, symbol, ts, signal_type, magnitude, lineage_root） | append-only | 🔴 高 | 时序库 |
| E12 | `TargetPosition` | 目标持仓（portfolio_id, symbol, target_weight, ts_decision, lineage_root） | append-only | 🟡 中 | OLTP |

### 2.5 Execution & Position 域（执行与持仓）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E13 | `Order` | 委托（client_order_id, symbol, side, qty, type, ts_create, parent_order_id?） | 状态机：`new → routed → partial → filled / cancelled / rejected` | 🟢 低（事件流） | OLTP + 事件流 |
| E14 | `Fill` / `Execution` | 成交回报（exec_id, order_id, ts_exec, qty, price, venue, fee） | append-only | 🟢 低 | OLTP + 事件流 |
| E15 | `Position` | 持仓快照（account_id, symbol, qty, avg_cost, ts_snapshot） | bitemporal（valid_time + transaction_time） | 🟡 中 | OLTP |
| E16 | `Portfolio` | 组合定义（portfolio_id, name, base_currency, capital, mandate） | 主数据 | — | OLTP |

### 2.6 Risk & PnL 域（风险与盈亏）

| # | Entity | 描述 / 字段族 | 生命周期 | PIT 敏感 | 典型存储 hint |
|---|--------|--------------|---------|---------|---------------|
| E17 | `RiskMetric` | 风险指标（portfolio_id, metric_name=VaR/Beta/Exposure/..., ts, value, scenario_id?） | append-only | 🟡 中 | 时序库 |
| E18 | `PnL` | 盈亏（portfolio_id, ts, realized, unrealized, fees, by_book, lineage_root） | append-only；T+1 修订需保留旧版本 | 🟡 中 | OLTP |
| E19 | `Benchmark` | 基准（benchmark_id, type, components[], ts） | 主数据 | — | OLTP |

> **PIT 敏感度图例**：🔴 高 = 任何错误都会让回测/归因撒谎；🟡 中 = 错误可被对账发现；🟢 低 = 事件流自然带时间。

### 2.7 实体上下游关系（一句话叙事）

```
Tick / OrderBookSnapshot → (聚合) → Bar
       Bar + Security + CorporateAction → (PIT 复权) → AdjustedBar (虚拟视图)
              AdjustedBar + IndexConstituent → (因子计算 asof) → FactorValue
                     FactorValue → FeatureSet → (策略) → Signal
                                                Signal → TargetPosition
                                                       → Order(CTR-004) → Fill(CTR-005) → Position(CTR-006)
                                                                          → PnL / RiskMetric
```

> **与跨层数据契约的对齐**：上述 `Order`/`Fill`/`Position` 分别对应 P0 跨层数据契约 **CTR-004** (Order, mutable)、**CTR-005** (Fill, frozen)、**CTR-006** (PositionSnapshot, frozen)。
> 契约真源：`architecture_model/contracts/cross_layer_contracts.yaml`。

每一条 → 都对应 §6 的一条**血缘边**（lineage edge），有 `lineage_root` 字段在实体里显式登记。

---

## 3. Data Classification / 数据分类（三维）

按"温度 × 节奏 × 来源"三维分类，每个数据实体在三轴各占一格，用于驱动存储选型（04-TA）、备份策略（§9）、访问控制（06-Security）。

### 3.1 三轴定义

| 轴 | 取值 | 判定规则 |
|----|------|---------|
| **温度** | 热（Hot） / 温（Warm） / 冷（Cold） | 热 = 实时读写，分钟级访问；温 = 当日/近期，分钟到小时；冷 = 历史，按需重载 |
| **节奏** | 流（Stream） / 批（Batch） | 流 = 持续到达，无明确边界；批 = 周期性快照或夜间任务 |
| **来源** | 外（External） / 内（Internal） / 派生（Derived） | 外 = 外部 vendor；内 = 系统自产事件；派生 = 由其他实体计算得出 |

### 3.2 分类矩阵（按实体）

| Entity | 温度 | 节奏 | 来源 |
|--------|-----|-----|------|
| Tick / OrderBookSnapshot | 热 | 流 | 外 |
| Bar (intraday) | 热 | 流 | 派生 |
| Bar (EOD) | 温 | 批 | 派生 |
| Security / TradingCalendar / Benchmark | 温 | 批 | 外 |
| IndexConstituent | 温 | 批 | 外（bitemporal） |
| CorporateAction | 温 | 批 | 外 |
| FactorValue / FeatureSet | 温 | 批（夜间）/ 流（日内因子） | 派生 |
| Signal / TargetPosition | 热 | 流 | 派生 |
| Order / Fill | 热 | 流 | 内 |
| Position | 温 | 批（快照）/ 流（实时增量） | 派生 |
| PnL / RiskMetric | 温 | 批 | 派生 |
| 历史 Tick (>2y) | 冷 | 批 | 外 |
| 退役模型的 FactorValue | 冷 | 批 | 派生 |

### 3.3 分类驱动的设计后果

| 分类组合 | 必备能力 | 落到哪个视图 |
|---------|---------|-------------|
| 热 × 流 × 内/外 | 低延迟 ingest、背压控制、at-least-once | 03-AA D_MKT_DATA / 04-TA 流处理选型 |
| 温 × 批 × 派生 | 幂等重算、checkpoint、版本号 | 03-AA D_FACTOR/D_ASHARE_SIGNAL、04-TA 调度器 |
| 冷 × 批 × * | 列存归档、按需重载、生命周期策略 | §9 + 04-TA 对象存储 |

---

## 4. Point-in-Time (PIT) Architecture / PIT 数据架构

> **PIT 是量化系统的红线**：任何因子值、信号、回测结果都必须能回答"在过去某一时刻 T，使用当时**确实可获得**的数据，会算出什么"。违反 PIT = 回测撒谎 = 实盘必亏。

### 4.1 PIT 三个核心字段（强制 schema）

凡 PIT 敏感（🔴 高）的实体，schema 中**必须**含：

| 字段 | 含义 | 业界对位 |
|------|------|---------|
| `asof_date` / `valid_time` | 数据所描述的"业务时间"（事件本身发生的时刻） | TimescaleDB / SQL:2011 valid time |
| `ts_ingest` / `transaction_time` | 数据**实际进入系统**的时间 | SQL:2011 transaction time / bitemporal |
| `vendor_release_ts` | 外部 vendor 把这条数据**对外发布**的时间（财报口径关键） | Bloomberg PIT / FactSet PIT |

**铁律**：任意因子计算 / 回测查询，**只能用 `vendor_release_ts ≤ T` 且 `ts_ingest ≤ T`** 的数据。`asof_date` 仅用作语义对齐，不做过滤条件。

### 4.2 PIT 违反的三种典型场景与防御

| 场景 | 例子 | 防御 |
|------|------|------|
| **Look-ahead bias / 前视偏差** | 用今天收盘价做今天开盘的决策 | factor 必须显式声明 `asof_offset`（如"昨日收盘后可知"） + fitness function `test_no_lookahead_bias.py` 在 CI 强制扫描 |
| **Restated data / 财报修订** | Q1 财报 4/30 公布，6/15 修订；回测 5/15 用了 6/15 修订版 | 财务实体存 bitemporal，查询走 `vendor_release_ts ≤ T` |
| **Index rebalance / 指数成分调整** | 沪深 300 半年调整，回测 2024 年 Q1 不能用 Q3 后调进的成分股 | `IndexConstituent` 必须 bitemporal；查询用 PIT API |

### 4.3 PIT 查询的实现路径（架构原则，非具体技术）

1. **bitemporal 表** —— OLTP 主数据用 valid_time + transaction_time 双时间戳建模
2. **append-only event log** —— 事件实体（Tick/Fill/Signal）天然 PIT，永不修改
3. **PIT-safe view layer** —— 因子计算前必须经过统一的 `pit_view(entity, asof=T)` 函数封装（具体实现归 D_DATA_ENG 域）
4. **CI fitness function** —— `test_no_lookahead_bias.py` 在 PR 阶段扫描所有因子代码，禁止任何 `df.loc[df.date <= today]` 之外的时间过滤模式

> **DA 视图只定义"原则与契约"**，具体 SQL/代码归 D_DATA_ENG / D_FACTOR 域、`scripts/fitness_functions/`。

---

## 5. Survivorship Bias 处理框架 / 幸存者偏差处理

> **核心问题**：用今天还活着的股票池回测过去 10 年，会高估收益（已退市的失败股票被自动排除）。专业机构对此有标准做法，本节给出 ZephyrAlpha 的处理框架。

### 5.1 三类需要处理的"消失/变化"

| 类型 | 例子 | DA 处理 |
|------|------|---------|
| **退市 / Delisting** | 长航油运退市、瑞幸 KB 决策记录 退市 | `Security.delisting_date` + `status='delisted'`，查询时按 PIT 包含 |
| **合并 / Merger** | 中国南车 + 中国北车 → 中国中车 | 旧 symbol 在 `delisting_date` 后映射到新 symbol，保留 mapping 表 |
| **指数成分调整** | 沪深 300 季度调仓 | `IndexConstituent` bitemporal，PIT 查询返回当时成分 |

### 5.2 反幸存者偏差的查询契约

凡构建历史投资域（universe），**必须**经过统一接口：

```text
universe = build_universe(
    asof=T,                     # PIT 时点
    exchange='SSE,SZSE',
    include_delisted=True,      # 默认 True；False 必须在 KB 决策记录 中说明理由
    index_filter=('CSI300', T)  # PIT 指数成分过滤
)
```

**禁止**直接 `SELECT * FROM security WHERE status = 'active'`——这是幸存者偏差的最常见入口。`scripts/fitness_functions/` 应有 `test_no_survivorship_bias.py` 扫描代码中此类反模式。

### 5.3 退市股票的数据保留

| 数据 | 退市后保留期 | 理由 |
|------|------------|------|
| `Security` 主数据 | **永久** | PIT 查询必备 |
| `Bar` / `Tick`（退市前） | **永久** | 回测必备 |
| 退市后的"幽灵价格"（清算价 / 0） | 不补造 | 用 `status` 字段表达更准确 |

### 5.4 与 PIT 的关系

PIT 是"时间维度真实"，Survivorship 是"对象维度真实"——两者**正交且必须同时成立**。任何回测的 universe 构造必须**两条都过**才算可信。

---

## 6. Data Lineage / 数据血缘

> **目标**：从任何一条 PnL 出现异常，能在分钟级反向追溯到具体的 Tick / vendor / 计算代码版本。

### 6.1 血缘的三层

| 层级 | 内容 | 真源 |
|------|------|------|
| **Schema lineage** | 字段级映射：`PnL.realized` ← `Fill.price * Fill.qty` ← ... | [`03_modules/_domain_data/`](../../03_modules/_domain_data/)（D_DATA_ENG 域）|
| **Pipeline lineage** | 任务级 DAG：`compute_factor_X` 依赖 `load_bar_eod`、`load_corporate_action` | 调度器元数据（Airflow / Dagster）→ OpenLineage |
| **Instance lineage** | 实例级：`FactorValue(factor=mom_20, symbol=600519, asof=2025-01-15)` 追溯到 `Bar(...)` 实例集合 | 每个派生实体的 `lineage_root` 字段 |

### 6.2 Factor Lineage 端到端示例

```
原始 Tick (vendor=tushare, ts_ingest=2025-01-15 09:30:00.123)
   ↓ aggregate (job=tick_to_bar_1m, version=v3.2.1, run_id=...)
Bar 1m
   ↓ aggregate (job=bar_1m_to_eod, version=v2.0.0, run_id=...)
Bar EOD
   ↓ adjust (job=corporate_action_replay, version=v1.4.0, run_id=...)
AdjustedBar EOD
   ↓ compute (factor=momentum_20d, code_sha=abc123, run_id=...)
FactorValue(factor=mom_20d, symbol=600519, asof=2025-01-15, lineage_root=lin_xxx)
   ↓ aggregate
FeatureSet(asof=2025-01-15)
   ↓ predict (strategy=alpha_001, model_version=v1.2.3, run_id=...)
Signal
   ↓ optimize (portfolio=p001, optimizer_version=v2.1.0)
TargetPosition → Order → Fill → Position → PnL
```

每一条 → 在 lineage store 落一条 edge，含：`upstream_id` / `downstream_id` / `transform_job_id` / `code_sha` / `run_id` / `ts`。

### 6.3 血缘标准与工具对位

| 业界标准 / 工具 | 在本项目中的位置 |
|----------------|----------------|
| **OpenLineage** | 血缘事件交换格式（DA 推荐采纳的接口标准） |
| **Marquez / DataHub** | 血缘存储与可视化（具体选型归 04-TA） |
| **MLflow** | 模型训练血缘（归 D_ML_TRAIN 域）|

> **DA 视图责任**：定义"必须有 lineage_root"、"必须实现 OpenLineage 接口"；**不**做工具选型（归 04-TA）。

### 6.4 血缘的 fitness function

`scripts/fitness_functions/test_lineage_completeness.py`（规划中）应保证：
- 任何派生实体（FactorValue / Signal / PnL / RiskMetric）创建时必填 `lineage_root`
- 任何 lineage_root 必须能解析出至少一条上游边
- 任何代码层 commit 不允许引入"无血缘的派生实体"

---

## 7. Master Data Management / 主数据管理

> **MDM 三件套**：证券主数据 / 交易日历 / Corporate Action。这三者一旦错，下游全错；必须**单点维护、版本化、bitemporal**。

### 7.1 三件套责任矩阵

| 主数据 | Steward / 责任人 | 输入源 | 频率 | bitemporal | 校验门禁 |
|--------|---------------|-------|------|----------|---------|
| `Security` / `Instrument` | 数据工程师 | tushare / akshare / 交易所官网 | 每日开盘前 | ✅ 必须 | symbol 唯一性 + ISIN 校验 + delisting_date 不可回溯修改 |
| `TradingCalendar` | 数据工程师 | 交易所官网 | 每月末次月历 | ❌ 不需要（可直接覆盖未来） | 与 vendor 三家以上交叉验证 |
| `CorporateAction` | 数据工程师 + 策略研究员复核 | tushare / 交易所公告 | 每日 | ✅ 必须 | 比例合理性（送转不超 1:10）+ 修订必须留旧版 |

### 7.2 主数据的"三禁三必"

| 禁止 | 必须 |
|------|------|
| 禁止任何业务模块**绕过 MDM 直接读 vendor** | 必须经过 D_MKT_DATA `connectors/`（ACL）+ MDM 服务 |
| 禁止 `UPDATE security SET delisting_date=...`（破坏 bitemporal） | 必须 INSERT 新版本 + 旧版本标记 superseded |
| 禁止前端/AI 直接发起主数据修改 | 必须走"修改提案 → Steward 复核 → 双人签字 → 落库"流程（暂时仅限单人 + 双 AI 评审） |

### 7.3 与旧体系 L00-M5 `catalog/` 的关系

旧体系 `construction-plan-l00-data-source.md` 中的 L00-M5 `catalog`（标的、交易所日历、数据源版本与血缘登记）就是 MDM 在代码层的物化点。本视图与旧体系设计**完全兼容**，新增的是"必须 bitemporal"+"必须经 OpenLineage 注册血缘"两条强约束。

---

## 8. Data Quality Gates / 数据质量门禁

> **设计原则**：数据质量不是"运行时偶尔扫描一下"，而是"任何数据写入 / 任何代码合入都必须先过断言"。对齐 Great Expectations / Soda Core 业界规范。

### 8.1 五类标准断言

| 类别 | 断言示例 | 触发时机 |
|------|---------|---------|
| **Schema** | 字段类型 / 必填 / 取值域（enum） | ingest 时（fail-fast）+ CI |
| **Range** | `0 < price < 10000`、`volume ≥ 0`、`abs(daily_return) < 0.5`（非异常停牌） | ingest 时 + 每日报表 |
| **Null / Completeness** | 关键字段缺失率 < 0.01% | 每日 ETL 后 |
| **Freshness** | `max(ts_ingest)` 与当前时间差 < SLA | 调度器健康检查 |
| **Distribution Drift** | 因子值分布与近 60 日基线 PSI < 0.2 | 每日因子计算后 |

### 8.2 门禁触发与失败处理

| 严重级 | 触发动作 | 处理 |
|--------|---------|------|
| 🔴 Fatal（schema 违反 / 重复主键） | 阻塞 ingest，告警 | 修数据源或修代码，**不绕过** |
| 🟠 Critical（range 越界 / freshness 严重超时） | 数据隔离到 quarantine，下游消费方收到 stale 标记 | Steward 24h 内裁决 |
| 🟡 Warning（drift / 缺失率小幅升高） | 告警 + dashboard | 进入 backlog 排查 |

### 8.3 业界工具映射（建议，最终选型归 04-TA）

| 业界工具 | 本项目用途 |
|---------|----------|
| **Great Expectations** | 适合 batch 断言（EOD bar / 因子值） |
| **Soda Core** | 适合 SQL-first 团队，与 dbt 集成好 |
| **自研 fitness functions** | PIT / Survivorship / Lineage 这三类**业界工具不覆盖**的量化专属断言，必须自研（INV-004/INV-016 支撑） |

### 8.4 与 03-AA / scripts/ 的边界

DA 视图给"**断言契约清单**"；具体 Python/SQL 代码落 `scripts/fitness_functions/`、`src/zephyr/data/quality_gate/`。

---

## 9. Data Retention & Archival / 数据保留与归档

### 9.1 保留策略矩阵

| 数据 | 热层保留 | 温层保留 | 冷层保留 | 删除？ |
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

### 9.2 归档触发与流程

- **触发**：调度器按数据 `ts` 字段超过阈值时，移动到冷层，元数据登记到 archive index
- **可恢复性**：冷层数据必须可在 24h 内重建为温层可查（重测、合规调阅）
- **不可变性**：归档数据走 WORM（Write Once Read Many）存储，对应合规留痕要求

### 9.3 监管驱动的保留要求（占位）

具体监管条款映射归 D_COMPLIANCE 域。本视图只声明"Order/Fill 必须保留 7 年（中国/美国证监会通用要求）"，具体条款引用待合规域激活。

---

## 10. Relationship to Other Views / 与其他视图的边界

> **本节是 DA 视图最重要的一节**——清楚划清边界，DA 才能独立存在而不与其他视图打架。

### 10.1 边界四象限

| 视图 | 关心 | 不关心 | 与 DA 的接口 |
|------|------|-------|-------------|
| **02-IA** Information Architecture | `docs/` 6 顶级目录、文档生命周期、frontmatter schema | 业务数据对象 | **零重叠**——IA 是"文档抽屉"，DA 是"业务实体"，两者完全正交 |
| **03-AA** Application Architecture | 53 域 src/、模块边界、ACL、扩展点 | 数据实体的字段定义 | DA 的实体被 AA 的域处理：D_MKT_DATA 落 Tick/Bar、D_FACTOR 算 FactorValue、D_EX_CORE 产 Order/Fill、D_TRADING 算 PnL/RiskMetric |
| **04-TA** Technology Architecture | 时序库选型、对象存储选型、调度器选型 | 数据实体本身有什么字段 | DA 给出"温度 × 节奏"分类，TA 据此选具体技术栈（DA 不指定 PostgreSQL 还是 ClickHouse） |
| **D_SECURITY** 安全域 | 字段级访问控制、PII 脱敏 | 数据怎么计算 | DA 给出 `classification` 标签，Security 据此设权限 |
| **D_DATA_ENG** 数据工程域 | 字段级 schema、SQL DDL、具体调度脚本 | 跨域数据原则 | DA 是"原则与契约"，D_DATA_ENG 是"schema 真源与执行" |

### 10.2 一句话区分 DA vs IA（防止读者混淆）

> **02-IA**："系统里有哪些**文档抽屉**？文档怎么流转？" — 治理 `docs/` 这个仓库本身。
>
> **05-DA**（本文）："系统里有哪些**业务数据**？数据怎么流转？" — 治理交易系统真正处理的对象。
>
> 类比：IA 管"图书馆有哪些书架"，DA 管"账本上记了哪些资金往来"。

### 10.3 DA 不做什么（防止越界）

| DA 不做的事 | 归属视图 |
|------------|---------|
| 字段级 schema DDL | D_DATA_ENG 域 |
| 选具体存储产品（TimescaleDB vs ClickHouse vs DuckDB） | 04-TA |
| 因子计算的具体算法 | D_FACTOR / D_RESEARCH 域 |
| 监管条款映射 | D_COMPLIANCE 域 |
| 加密 / 脱敏算法 | D_SECURITY 域 |
| AI 自治的数据血缘自动发现 | D_AUTONOMY_CORE 域（未来） |

> **📊 数据流时序图**：
> - [`diagrams/data_flow.mmd`](diagrams/data_flow.mmd) — 跨域核心数据流（D_MKT_DATA→D_FACTOR→D_ASHARE_SIGNAL→D_PF_CORE→D_EX_CORE→D_REPORTING 主链路）
> - [`diagrams/dataflow_terminal.mmd`](diagrams/dataflow_terminal.mmd) — 终端数据流详细时序

---

## 11. 修订记录

> 已删除（git log 是真源）。v1.0.0 于 2026-04-19 新建，详见 git log。
