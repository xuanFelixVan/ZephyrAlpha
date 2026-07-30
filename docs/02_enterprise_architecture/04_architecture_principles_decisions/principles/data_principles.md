---
module_id: VIEW-04PRINC-DATA
title: Data Architecture Principles / 数据架构原则
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
language: zh
created_by: agent
valid_from: 2026-07-30
superseded_by: null
supersedes: VIEW-05-DATA-ARCH
tags:
- data-architecture
- pit
- survivorship
- lineage
- quant-redline
summary: 数据架构永恒红线精简版。仅保留两条量化真红线（PIT + 反幸存者偏差）及 Lineage 极简契约。MDM/质量门/保留分级/三维分类等已由 data_entity_catalog.yaml schema + fitness_functions/ 代码落地，本文档是它们的"解释书"，不再重复。
date: '2026-07-30'
ttl: permanent
---

# 数据架构原则（Data Architecture Principles）

> 精简版 v2.0（2026-07-30）：保留 PIT + Survivorship 两条量化真红线及 Lineage 极简契约。删除 MDM 三件套（已在 schema）、质量门五类断言（已在 `scripts/fitness_functions/`）、保留分级（已在 `technology_landscape.yaml`）、三维分类（已派生）。
> 派生数据真源：概念实体清单 → `architecture_model/data/data_entity_catalog.yaml`；物理表清单 → `generate_data_inventory.py` 自动生成；字段级 schema → `03_modules/_domain_data/`。

---

## §1 Point-in-Time (PIT) 红线

> **PIT 是量化系统的红线**：任何因子值、信号、回测结果都必须能回答"在过去某一时刻 T，使用当时**确实可获得**的数据，会算出什么"。违反 PIT = 回测撒谎 = 实盘必亏。

### 1.1 三个核心字段（强制 schema）

凡 PIT 敏感（🔴 高）的实体，schema 中**必须**含：

| 字段 | 含义 |
|------|------|
| `asof_date` / `valid_time` | 数据所描述的"业务时间"（事件本身发生的时刻） |
| `ts_ingest` / `transaction_time` | 数据**实际进入系统**的时间 |
| `vendor_release_ts` | 外部 vendor 把这条数据**对外发布**的时间（财报口径关键） |

**铁律**：任意因子计算 / 回测查询，**只能用 `vendor_release_ts ≤ T` 且 `ts_ingest ≤ T`** 的数据。`asof_date` 仅用作语义对齐，不做过滤条件。

### 1.2 PIT 违反的三种典型场景与防御

| 场景 | 例子 | 防御 |
|------|------|------|
| **Look-ahead bias / 前视偏差** | 用今天收盘价做今天开盘的决策 | factor 必须显式声明 `asof_offset` + CI fitness function 强制扫描 |
| **Restated data / 财报修订** | Q1 财报 4/30 公布，6/15 修订；回测 5/15 用了 6/15 修订版 | 财务实体存 bitemporal，查询走 `vendor_release_ts ≤ T` |
| **Index rebalance / 指数成分调整** | 沪深 300 半年调整，回测 Q1 不能用 Q3 后调进的成分股 | `IndexConstituent` 必须 bitemporal；查询用 PIT API |

### 1.3 PIT 查询的四条实现路径

1. **bitemporal 表** —— OLTP 主数据用 valid_time + transaction_time 双时间戳建模
2. **append-only event log** —— 事件实体（Tick/Fill/Signal）天然 PIT，永不修改
3. **PIT-safe view layer** —— 因子计算前必须经过统一的 `pit_view(entity, asof=T)` 函数封装
4. **CI fitness function** —— PR 阶段扫描所有因子代码，禁止任何 `df.loc[df.date <= today]` 之外的时间过滤模式

> 具体实现归 D_DATA_ENG / D_FACTOR 域、`scripts/fitness_functions/`。

---

## §2 Survivorship Bias 防御原则

> **核心问题**：用今天还活着的股票池回测过去 10 年，会高估收益（已退市的失败股票被自动排除）。

### 2.1 三类需要处理的"消失/变化"

| 类型 | 例子 | 处理原则 |
|------|------|---------|
| **退市 / Delisting** | 长航油运退市、瑞幸退市 | `Security.delisting_date` + `status='delisted'`，查询时按 PIT 包含 |
| **合并 / Merger** | 中国南车 + 中国北车 → 中国中车 | 旧 symbol 在 `delisting_date` 后映射到新 symbol，保留 mapping 表 |
| **指数成分调整** | 沪深 300 季度调仓 | `IndexConstituent` bitemporal，PIT 查询返回当时成分 |

### 2.2 反幸存者偏差的查询契约

凡构建历史投资域（universe），**必须**经过统一接口：

```text
universe = build_universe(
    asof=T,                     # PIT 时点
    exchange='SSE,SZSE',
    include_delisted=True,      # 默认 True；False 必须在 KB 决策记录中说明理由
    index_filter=('CSI300', T)  # PIT 指数成分过滤
)
```

**禁止**直接 `SELECT * FROM security WHERE status = 'active'`——这是幸存者偏差的最常见入口。CI fitness function 应扫描此类反模式。

### 2.3 与 PIT 的关系

PIT 是"时间维度真实"，Survivorship 是"对象维度真实"——两者**正交且必须同时成立**。任何回测的 universe 构造必须**两条都过**才算可信。

---

## §3 Data Lineage 极简契约（永恒）

**目标**：从任何一条 PnL 出现异常，能在分钟级反向追溯到具体的 Tick / vendor / 计算代码版本。

- 任何派生实体（FactorValue / Signal / PnL / RiskMetric）创建时必填 `lineage_root`
- 任何 `lineage_root` 必须能解析出至少一条上游边
- 任何代码层 commit 不允许引入"无血缘的派生实体"

> 具体实现（Schema/Pipeline/Instance 三层）归 D_DATA_ENG 域 + `scripts/fitness_functions/`。

---

> **文档维护原则**：本文档只保留两条量化真红线及 Lineage 契约的解释。MDM/质量门/保留/分类等可派生内容已由 YAML schema 与 fitness function 代码落地。
