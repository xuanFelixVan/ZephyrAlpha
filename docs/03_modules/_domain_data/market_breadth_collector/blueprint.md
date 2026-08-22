---
blueprint_id: MOD-DATA-062
module_name: market_breadth_collector
domain: D_DATA
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-DATA-062 market_breadth_collector 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘 §2 M1-④ 行 + 92号清单 §8.2。
> 代码：`src/zephyr/data/market_breadth_collector.py`

## 0. 定位

全市场分钟级宽度快照采集纯函数——miniqmt 实时全市场快照通道（xtdata.get_stock_list_in_sector("沪深A股") ~5400 只 + get_full_tick 分批 200 只/批）→ 全市场最新价×昨收×板块差异化涨跌停价推导涨跌停计数（44号 §9.1 输入 s_t=(adv,dec,lu,attempted)+total 的直接供给）。涨跌停计数不走 miniqmt 板块统计接口（无该口径实证）。

## 1. 接口

```python
def aggregate_market_ticks(
    ticks: Mapping[str, Mapping[str, Any]],           # 全市场 tick 字典（miniqmt get_full_tick 形态）
    st_codes: frozenset[str] | set[str] | None = None,
    *, trade_date: date | None = None,
) -> BreadthAggregate                                 # 纯函数，无 I/O

def build_insert_row(agg, trade_date, ts, *, data_source="miniqmt", degraded=0) -> tuple
    # 聚合结果 → market_breadth_snapshot INSERT 行（列序=schemas INSERT_COLUMNS 真源，本模块为采集侧列序真源）

def load_current_st_codes(query_fn=None, as_of=None) -> tuple[set[str], bool]
    # 当前有效 ST 集=最近可得（≤查询日）全量快照（PIT 严格）；异常→(空集, False)+log（fail-open）
```

## 2. 输出契约

`BreadthAggregate`（frozen dataclass slots，一行 market_breadth_snapshot 的业务字段）：advancing/declining/flat（最新价 vs 昨收）+ limit_up/limit_down + sealed（涨停且卖一无量=封单形态）+ attempted（日内最高曾触涨停价，含炸板）+ total_count（有效 tick 数）+ total_amount（全市场累计成交额元）+ n_skipped（无效 tick 跳过数）。

计数口径：

- 涨跌停价=昨收×(1±幅度) 四舍五入到分（Decimal ROUND_HALF_UP，交易所口径）；幅度=主板 10%（ST/*ST 5%）/创业板/科创板 20%/北交所 30%——复用 AkshareIngestProvider._limit_pct_of（stk_limit DS-082 同口径，单一真源不另造）
- 新股无涨跌幅限制期/未知板块：_limit_pct_of 返回 None→只计涨跌家数不计涨跌停（近似口径留痕）
- 停牌/无昨收/最新价≤0 tick 跳过不计入 total_count

## 3. 不变量（头注 INVARIANTS 原文）

- 聚合纯函数无 I/O 无副作用（同输入同输出）
- 涨跌停幅度口径与 akshare_provider._limit_pct_of（stk_limit 日频表）同源复用不另造
- 价格比较一律 Decimal 量化到分（ROUND_HALF_UP，交易所口径）
- 无效 tick（缺昨收/最新价≤0）跳过不计入 total_count
- ST 集加载失败→degraded=1 降级不炸（主板 ST 按 10% 近似，涨停计数偏紧留痕）

## 4. 降级行为

- ERROR_CONTRACT：空/全非法 tick 输入→全零 BreadthAggregate+n_skipped 留痕不炸；ST 集加载异常→空集+log（fail-open）；query_fn 异常同上
- fail-open 纪律：本模块所有 I/O 边界（ST 集加载）异常→空集+log.warning 不抛——单次失败留痕不炸调度（调度器 FetchResult error 通道在 miniqmt_provider 侧兜底）
- INSERT 列序漂移由 tests/zephyr/data/test_market_breadth_snapshot.py 对账断言兜底

## 5. 边界（不做）

- 本模块为采集纯函数；消费方=miniqmt_provider（market_breadth_snapshot capability）；调度/写表在 provider 侧

## 6. 测试

tests/zephyr/data/test_market_breadth_snapshot.py
