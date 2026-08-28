---
ttl: permanent
---

# PIT 接线调研报告：财报数据修订处理与回测正确性

- **调研日期**: 2026-08-02
- **触发**: 用户疑问"数据可以更正，实时检测到更正跟着更正就好了，为什么要 PIT 冻结历史版本？"
- **调研范围**: 项目代码 + 蓝图文档 + 专业机构实践 + 量化社区共识
- **关联项**: P0-5 PIT 推进、§8 改期项、#ARCH-CH-021

---

## 1. 用户核心疑问

> "数据可以更正的呀？比如我用现在回测用了这个数据，过了两天它更正了，那我也跟着更正就好了嘛？我实时可以检测到这个更正的情况。能不能两份数据都查看呢？"

这个疑问包含两个独立的问题：

**问题 A**：为什么要用 PIT 冻结历史版本？不能实时检测修订、跟着更新吗？
**问题 B**：能不能同时保留原始版本和修订版本，两个都能查？

---

## 2. 第一性原理：回测的本质

### 2.1 回测是什么

回测是在回答一个问题：**"如果我在历史时点 T 运行这个策略，会发生什么？"**

这个问题的核心约束是：**"with the information available at the time"**（当时能获得的信息）。

—— StockFit Engineering, "Point-in-Time Data: Essential for Backtesting Accuracy"

### 2.2 回测 vs 实盘的信息不对称

| | 实盘交易 | 回测 |
|---|---|---|
| **你站在** | 当前时点 T_now | 模拟历史时点 T_past，但实际站在 T_future |
| **能看到的数据** | T_now 之前已公告的所有版本 | 应该只能看到 T_past 之前已公告的版本 |
| **修订处理** | 检测到修订 → 更新 → 用最新值 ✅ | 不能用 T_past 之后的修订（那是未来信息）❌ |
| **数据需求** | 最新、最准确的版本 | T_past 时点能看到的版本（PIT） |

**关键洞察**：实盘和回测的数据需求是**相反的**：
- 实盘：用最新版本（修订后的）
- 回测：用时点版本（修订前的原始版本）

### 2.3 用户的"实时修订跟踪"方案为什么对回测不成立

用户的方案是：用最新数据做回测，如果数据被修订了，检测到修订，更新回测数据。

**问题在于**：在回测时点 T_past，你不可能"检测到"T_past 之后才发生的修订。这就像穿越回 2020 年，却带着 2024 年的财报修订数据——你在用 2024 年才知道的信息做 2020 年的决策。

**具体例子**（真实案例，来自 StockFit）：
- Plug Power 2018 财年净亏损：原始报告 $78.1M（2019年3月公告）
- 2021年5月修订为 $85.7M（两年后才公告）
- 如果你在回测 2019-2020 年策略时用了 $85.7M（修订值），你就在用 2021 年才知道的信息
- 回测结果会虚高——策略看起来"知道"了某些它不可能知道的东西

### 2.4 "两份数据都保留"——这正是专业做法

用户问"能不能两份数据都查看"——**可以，而且这就是专业机构的做法**。

> "The fix is not to throw away the restatement. The fix is to keep both values, each tagged with the filing that carried it, so the backtest can ask: what was the value as of this date?"
>
> —— StockFit Engineering

专业系统的做法是：
1. **保留所有版本**（原始 + 修订 + 再修订...）
2. **回测时**：查 PIT，取历史时点能看到的版本
3. **实盘时**：查最新版本
4. **分析时**：对比原始 vs 修订，研究修订影响

---

## 3. 专业机构实践

### 3.1 TEJ（台湾经济日报，专业数据供应商）

TEJ Point-in-Time Audited Financial Database 的做法：
- 每个数据点带**公告时间戳**（announcement timestamp）
- **完整版本保留**（full version retention）——所有修订版本都保留
- "Only after that exact timestamp would the corrected figure take effect"（修正值只在公告时间戳之后生效）
- 案例：TRANS-SUN 2025 Q2 财报修正，TEJ 数据库保留完整版本历史

### 3.2 StockFit（SEC 数据 API 供应商）

StockFit 的做法：
- 每个财务数据点携带两个信息：**filing date**（公告日）和 **original value**（首次报告值）
- 服务端 AS OF 查询：传入 `as_of` 日期，API 自动过滤 `filing_date <= as_of`
- 三类问题：**Restatements**（修订→前视偏差）、**Reporting lag**（报告滞后）、**Survivorship bias**（幸存者偏差）

### 3.3 Portfolio123（量化回测平台）

Portfolio123 的做法：
- 保留 2-3 个版本的快照（preliminary data snapshot until filing complete）
- 修订处理：在修订公告日之前看到旧数据，之后看到新数据
- "Between the period end date and the restatement date, you'll see the older data, and after the restatement date, you'll see the newer data"

### 3.4 量化社区共识

> "回测时用了修订后的值——这就是用了未来才会被知道的更准确数字——相当于偷看了几个月后的修订结果。点位时态（point-in-time，PIT）数据库的存在就是为了防止这件事。"
>
> —— quant67.com, "回测陷阱：前视偏差、过拟合、数据窥视"

量化社区的共识：**PIT 是回测可信性的基石，不是可选项**。

---

## 4. 项目现状审计

### 4.1 已有的 PIT 基础设施

| 组件 | 状态 | 说明 |
|---|---|---|
| ClickHouse ReplacingMergeTree | ✅ production | `ORDER BY (symbol, report_period, announce_date)` — 所有版本保留 |
| pit_query.py（数据层） | ✅ production（本 session 升级） | AS OF JOIN + embargo + survivorship，47 测试全绿 |
| pit_manager.py（回测层） | ✅ production | as_of_join + apply_embargo + pit_consistency_test + check_survivorship_bias |
| 蓝图 §5.1 PIT铁律 | ✅ 零容忍 | "违反→fail_backtest直接失败退出" |

### 4.2 缺口

| 组件 | 状态 | 缺口 |
|---|---|---|
| data_handler.py | ❌ 未接 pit_query | `from_clickhouse()` 只查 OHLCV（`SELECT date, symbol, open, high, low, close, volume`），不查财务数据 |
| value_factor.py | ❌ 硬编码默认值 | `earnings_per_share = kwargs.get("earnings_per_share", 5.0)` — 用默认值 5.0，没查真实财务数据 |
| 回测引擎 | ❌ 无财务数据流 | vectorized_engine / event_driven_engine 只消费 OHLCV bar，不消费财务数据 |

### 4.3 ClickHouse 版本保留机制确认

balance_sheet 表 DDL（schemas/categories/fundamental_balance_sheet.py）：
```
ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(report_period)
ORDER BY (symbol, report_period, announce_date)
```

**关键**：ORDER BY 包含 announce_date，不同公告日的版本不会被 ReplacingMergeTree 合并。
所以 ClickHouse **已经保留了所有版本**——原始公告 + 修正公告都在，pit_query 的 `LIMIT 1 BY` 可以精确取到查询时点可见的最新版本。

---

## 5. 裁定结果

### 5.1 裁定 A：PIT 是回测的硬约束，不可妥协

**依据**：
- 蓝图 §5.1 明确标注"零容忍，违反→fail_backtest直接失败退出"
- 专业机构（TEJ/StockFit/Portfolio123）全部使用 PIT
- 量化社区共识：PIT 是回测可信性基石
- 用户的"实时修订跟踪"方案适用于实盘，不适用于回测

### 5.2 裁定 B：两份数据都保留（用户建议正确）

**依据**：
- ClickHouse ReplacingMergeTree 已保留所有版本（无需额外建设）
- pit_query.py 查 PIT 版本（回测用）
- ch_reader 查最新版本（实盘用）
- 用户建议"两份数据都查看"与专业机构做法完全一致

### 5.3 裁定 C：data_handler 接线是 AI 可独立完成的基础设施

**依据**：
- pit_query.py 已 production，接口稳定
- data_handler.py 已有 PITManager 集成（用于 post-hoc 检查）
- 接线工作是"调用 pit_query 查财务数据 → 喂给回测引擎"，不涉及策略决策
- embargo_days 用 pit_manager 默认值 5 天（蓝图 P0-13 规定）

### 5.4 裁定 D：embargo_days 不需要用户给策略

**依据**：
- 蓝图 P0-13 已规定 Embargo 期 + pit_consistency_test 偏差>1% 告警
- pit_manager.py 默认 `embargo_days=5`（DEFAULT_EMBARGO_DAYS = 5）
- 这是回测工程标准参数，不是策略参数

---

## 6. 治本施工方案

### 6.1 施工目标

在 data_handler.py 中新增财务数据加载能力，通过 pit_query.py 做 PIT 正确查询，使回测引擎能消费 PIT 正确的财务因子数据。

### 6.2 施工范围

```
pit_query.py (数据层, 已 production)
       ↓ as_of / as_of_panel / as_of_latest / survivorship_universe
data_handler.py (回测层, 新增 from_clickhouse_fundamental 方法)
       ↓ 财务数据 DataFrame
vectorized_engine / event_driven_engine (回测引擎, 消费财务数据)
       ↓ 因子计算
value_factor.py (因子, 替换硬编码 earnings_per_share=5.0)
```

### 6.3 施工步骤

**Step 1: data_handler.py 新增 `from_clickhouse_fundamental` 方法**
- 使用 pit_query.FinancialPITQuery 查询财务数据
- 支持 as_of_panel（多标的批量查询）
- 返回 PIT 正确的财务 DataFrame

**Step 2: data_handler.py 新增财务数据 bar 推送**
- 在 `get_bar(date)` 中合并 OHLCV + 该时点可见的最新财务数据
- 按 PIT 规则：只推送 announce_date <= date 的最新版本

**Step 3: value_factor.py 替换硬编码**
- `earnings_per_share` 从 bar 数据中读取（而非默认 5.0）
- 计算 PE = price / earnings_per_share（PIT 正确）

**Step 4: 测试**
- 新增 `test_data_handler_pit.py`：验证财务数据 PIT 正确性
- 测试用例：原始公告 + 修订公告，验证回测时点只看到原始版本

### 6.4 不做的事

- ❌ 不修改 pit_query.py（已 production，不动）
- ❌ 不修改 pit_manager.py（已 production，不动）
- ❌ 不改 ClickHouse 表结构（ReplacingMergeTree 已保留所有版本）
- ❌ 不引入新的数据供应商（用现有 c3_fundamental 数据）

---

## 7. 对用户疑问的最终回答

| 用户疑问 | 回答 |
|---|---|
| 为什么要 PIT？不能实时修订跟踪？ | **实盘可以，回测不行**。回测是模拟过去，不能用未来才知道的修订数据。用了 = 前视偏差 = 回测虚高 = 实盘必然达不到回测预期。 |
| 能不能两份数据都查看？ | **可以，而且这就是专业做法**。ClickHouse 已经保留所有版本。回测查 PIT 版本，实盘查最新版本，分析时对比两者。 |
| 需要我给策略吗？ | **不需要**。embargo_days=5 是蓝图标准参数，PIT 接线是纯基础设施。AI 可以独立完成。 |

---

## 参考来源

1. TEJ Point-in-Time Audited Financial Database – https://www.tejwin.com/en/insight/tej-point-in-time-audited-financial-database/
2. StockFit Engineering – Point-in-Time Data: Essential for Backtesting Accuracy – https://developer.stockfit.io/blog/point-in-time-data-backtesting
3. quant67 – 回测陷阱：前视偏差、过拟合、数据窥视 – https://quant67.com/post/quant/20-backtest-pitfalls/20-backtest-pitfalls.html
4. Portfolio123 – How is restated data handled to prevent look-ahead bias – https://community.portfolio123.com/t/how-is-restated-data-handled-in-p123-to-prevent-look-ahead-bias/72044
5. TradevoData – Point-in-Time Fundamentals Data: What It Is, Why It Matters – https://dev.to/tradevodata/point-in-time-fundamentals-data-what-it-is-why-it-matters-and-how-to-choose-a70
6. 项目蓝图 §5.1 PIT铁律 – docs/03_modules/_domain_backtest/blueprint.md
7. pit_query.py – src/zephyr/data/pit_query.py（47 测试全绿，production）
8. pit_manager.py – src/zephyr/backtest/core/pit_manager.py（production）
9. balance_sheet DDL – schemas/categories/fundamental_balance_sheet.py（ReplacingMergeTree 保留所有版本）
