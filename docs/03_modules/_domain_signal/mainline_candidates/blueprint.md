---
blueprint_id: MOD-SIG-061
module_name: mainline_candidates
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-SIG-061 mainline_candidates 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：92号清单 §7.8 + 架构审查报告 §11.5 SEC-05 + 22号板块轮动 spec §3.1⑧⑨④。
> 代码：`src/zephyr/signal_ashare/mainline_candidates.py`

## 0. 定位

主线候选榜——最可能成主线的板块 Top3-5，盘后出榜（T 日收盘后批量，T+1 开盘可消费）。四维判定全部 import 消费既有模块（不重复造）：① HEALTHY_MAINLINE 判定（sector_rotation_state 5 状态）；② lead_streak 连续领涨天数；③ q3 动量前排（sector_momentum，3 日累计涨跌幅截面分位 ≥0.80）；④ RRG 改善/领先象限（sector_rrg，JdK DualEma 10/26 + whipsaw 连续 2 日确认）。

## 1. 接口

```python
def compute_mainline_candidates(
    trade_date: str | date | datetime | None = None,  # None=kline_sector_880 最新数据日（PIT 数据日口径）
    ch_client: Any | None = None,                     # None=延迟取 ch_writer.get_client，不可得→degraded
    config: MainlineCandidatesConfig | None = None,   # None=22号 spec + 44号 §9.13 + 数据实证默认口径
) -> MainlineCandidatesResult
```

只读四表：kline_sector_880 / sector_constituent（SCD-2 时点过滤）/ kline_daily / sector_meta（板块名称真源）。

## 2. 输出契约

`MainlineCandidatesResult`（frozen dataclass，asdict JSON 可序列化）：date/rotation_state/watch_score/leader_code/leader_name/lead_streak/no_mainline_flag + `candidates: list[MainlineCandidate]` + annotations/degraded/notes。

`MainlineCandidate`：sector_code/sector_name/score/reasons（中文理由标签链，消费方直读）/lead_streak/q3_percentile ∈ [0,1]/rrg_quadrant（LEADING/IMPROVING/WEAKENING/LAGGING）。

评分（规则层 if-else，无 ML，可审计）：健康主线领涨 +3 / 连续领涨≥2 日 +2 / 当日涨幅居首 +1 / q3 前排 +1 / RRG 领先或改善象限 +1；score≥2 入榜，按 (score, q3 分位, 代码) 排序取 top_k（默认 5）。无主线混沌（lead_streak<2，22号 §2.3/44号 §9.13 口径）→空榜+注解，不强行出榜。

## 3. 不变量（头注 INVARIANTS 原文）

- 不预测纪律：只出候选榜+理由标签，不出方向/点位
- 候选数 ∈ [0, top_k]；q3 分位 ∈ [0,1]
- 无主线混沌（连续领涨<2 日）→空榜+注解
- PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）
- 各数据维度独立降级互不累及
- frozen dataclass asdict JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→对应维度降级 notes 留痕不抛；板块全集为空/当日无收益截面→degraded=True；trade_date 格式非法→ValueError（fail-closed）；单板块 K 线不足 62 日→该板块 rrg_quadrant=None 不炸整体
- 板块 K 线历史自 2026-06 起采（~52 交易日）：RRG 最小 62 日数据积累期常态降级（设计内行为）
- 板块名称：sector_meta SCD 版本取 argMax(trade_date) 最新；sector_constituent 回显名过滤；880xxx 概念板无中文名→代码直出（采集层缺口，非本模块职责）
- 881xxx 行业板无 K 线→成分股等权 pct_change 合成价格指数（cumprod），与 880xxx 同管线下游

## 5. 边界（不做）

- 消费方：zephyr.data.sector_report_builder（SEC-01 板块盘后全景报告器主线候选维度）；远期 IDX-02 Dashboard 板块页 D-06
- 不出方向/点位；不接交易

## 6. 测试

tests/signal_ashare/test_mainline_candidates.py
