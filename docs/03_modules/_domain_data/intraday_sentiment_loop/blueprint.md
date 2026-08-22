---
blueprint_id: MOD-DATA-063
module_name: intraday_sentiment_loop
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

# MOD-DATA-063 intraday_sentiment_loop 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘 §2 M1-④ 行 + 92号清单 §8.2。
> 代码：`src/zephyr/data/intraday_sentiment_loop.py`

## 0. 定位

M1-④ 盘中情绪实时调度回路——单拍链路（run_once 一次执行）：读 market_breadth_snapshot 最新交易日全部分钟快照 → 装配 MarketSentimentInput.time_series（M1-① 波3 输入契约的首个生产侧装配方）→ 调 MOD-SIG-025 MarketSentimentAnalyzer.analyze → 结果经 prediction_log_writer 落 governance.db（prediction_type="sentiment_score"，asof_ts=最新快照 ts，PIT 口径）→ SEC-02 挂接同载体（sector_intraday_aggregator 一并聚合，榜面摘要随 payload 注解留痕）。

## 1. 接口

```python
def run_once(
    ch_client: Any | None = None,                   # None=延迟取 ch_writer.get_client()，不可得→degraded 不抛
    *, db_path: str | None = None,                  # prediction_log 库路径；None=DB_PATH SSoT
    previous_board: SectorIntradayBoard | None = None,  # SEC-02 新开板对照基线（调用方逐轮持有）
    analyzer: MarketSentimentAnalyzer | None = None,
    sector_window_minutes: int = 5,
) -> IntradayLoopResult

def rows_to_time_series(rows) -> BreadthTimeSeries   # 快照行 → MOD-SIG-025 输入契约装配
```

**有界形态纪律（PERM-TRIGGER）**：本模块只做单拍——常驻节拍交 APScheduler/P0-5 日循环 SOP 盘中族，禁止 while True/自旋循环。盘中硬时点（14:00/14:45 M2 边界修正评估）经 prediction_log 共享载体解耦——本回路只写观测，不直接驱动交易动作。

## 2. 输出契约

`IntradayLoopResult`（frozen dataclass，asdict JSON 可序列化）：asof（最新快照时间戳 ISO，无快照→""）/trade_date/n_snapshots/total_count + sentiment（MOD-SIG-025 输出，无快照→None）+ prediction_log_id（写失败/跳过→None）+ sector_board（SEC-02 聚合榜）+ degraded/errors（fail-open 留痕）/notes。

- 指数涨跌幅经 index_quote×kline_index 两腿推导，失败降级 0.0+留痕
- prediction_log payload 经写入器 canonical 序列化（datetime/Decimal 放行）

## 3. 不变量（头注 INVARIANTS 原文）

- 单拍形态：只提供 run_once() 单拍函数，禁止 while True/常驻循环（PERM-TRIGGER 门禁纪律）
- fail-open：任一 I/O 边界（快照读/指数读/prediction_log 写/SEC-02 聚合）单次失败→errors 留痕不抛不炸调度
- PIT（只读 ≤ 当前时点最新交易日快照）
- 快照缺失>2min 不外推（MOD-SIG-025 侧纪律）
- 输出容器 frozen dataclass（含 datetime 字段不直接 JSON 序列化；prediction_log payload 经写入器 canonical 序列化）

## 4. 降级行为

- ERROR_CONTRACT：CH 客户端不可用/查询异常→degraded=True+errors 留痕返回（不抛）；无当日快照→跳过情绪分析与落库、SEC-02 仍聚合（载体职责）；prediction_log 写入异常→errors 留痕返回
- 全链路任一环节缺数据按 degraded=True 返回结构化结果（观测可用性由消费方判定）

## 5. 边界（不做）

- 常驻节拍交 APScheduler/P0-5 日循环 SOP 调度族挂接，本模块不注册任务（波5 交付单拍函数）
- 只写观测，不直接驱动交易动作；market_breadth_snapshot 尚未登记 business_data_categories.yaml（92号工单纪律不写其他注册表 yaml，补登=统筹批后续项）

## 6. 测试

tests/zephyr/data/test_intraday_sentiment_loop.py
