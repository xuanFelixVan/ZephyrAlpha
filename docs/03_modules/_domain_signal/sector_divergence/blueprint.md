---
blueprint_id: MOD-SIG-060
module_name: sector_divergence
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

# MOD-SIG-060 sector_divergence 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘录 §9.13 + §9.2 通道 c；92号清单 §7.4+§7.10 合并施工；架构审查报告 §11.5 SEC-03 同一工件裁定。M1-⑩ + M1-②c。
> 代码：`src/zephyr/signal_ashare/sector_divergence.py`

## 0. 定位

板块分歧度与轮动速度计 + SEC-03 概率标定器（四件套）：a) 消费接入既有 22 号模块（5 状态分类/虹吸态，import 不重复造）；b) 电风扇速度计（国泰海通 2026-08 口径）；c) 个股分歧度（24号口径通用化）；d) SEC-03 概率标定器（5 状态×后续 3/5 日涨跌历史条件频率，滚动 250 交易日窗，可审计可复算不做伪精确点概率）。合并施工 M1-②c 板块属性标签雷达（config/sector_attribute_labels.yaml 为族标签真源）。

## 1. 接口

```python
def compute_sector_divergence(
    trade_date: str | date | datetime | None = None,  # None=kline_sector_880 最新数据日（PIT 数据日口径）
    ch_client: Any | None = None,                     # None=延迟取 ch_writer.get_client，不可得→degraded
    config: SectorDivergenceConfig | None = None,     # None=44号 §9.13/§9.2 + 数据实证默认口径
) -> SectorDivergenceResult
```

只读六表：kline_sector_880 / sector_constituent（SCD-2 时点过滤）/ money_flow / kline_daily / stk_limit / dragon_tiger_seat；yaml 真源两件：sector_attribute_labels.yaml（族标签）+ seat_registry.yaml（一线游资席位身份）。

## 2. 输出契约

`SectorDivergenceResult`（frozen dataclass，asdict JSON 可序列化）：

- `rotation_state`（5 状态）/ `watch_score` / `top_risk_flag`（CONSENSUS_CLIMAX/DISTRIBUTION_RISK→见顶风险标记，M2 降档触发）
- `siphon_z` / `siphon_flag`（z>1.5σ 虹吸态）/ `rotation_velocity` / `velocity_percentile`（>75 分位=电风扇行情）/ `fan_market_flag` / `top3_overlap`（<20%=一日游生态）/ `no_mainline_flag`（lead_streak<2 且速度计>75 分位=无主线混沌）/ `siphon_chaos_flag`（虹吸×电风扇共振）
- 个股分歧度：divergence = 0.4·z(换手突增) + 0.3·上影占比 + 0.2·炸板标记 + 0.1·龙虎榜买卖对打；截面 >80 分位→stock_watchlist 例外清单（禁新开仓注解，只清单不方向）
- SEC-03 标定输出："当前状态=X；该状态历史后续 3 日下跌>2% 频率=Y%（样本 N=Z）"；单状态样本 <30→sufficient=False
- M1-②c 族相对强度：rs_ratio=mean_ret(进攻族)−mean_ret(防御族)；rs_z<−1 且指数红→避险抱团注解；rs_z>+1 且上涨家数改善→真情绪好注解

## 3. 不变量（头注 INVARIANTS 原文）

- 不预测纪律：只出状态+风险清单+历史条件频率，不出方向/点位（个股分歧≠必然下跌，44号原文）
- velocity_percentile ∈ [0,1]；top3_overlap ∈ [0,1]
- 各维度独立降级互不累及
- PIT（全部数据 ≤ trade_date，成分股 SCD-2 时点过滤）
- frozen dataclass asdict JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→对应维度降级 notes 留痕不抛；主数据（kline_sector_880）缺失/异常→degraded=True；trade_date 格式非法→ValueError（fail-closed）；板块族标签 yaml 缺失/解析失败→rs 维度降级不抛
- 板块 K 线历史仅 ~52 交易日（2026-06 起采）：速度计 250 分位窗/标定器 250 窗数据积累期常态降级（min_periods 守卫+insufficient 标注），属设计内行为
- 881xxx 纯行业板无板块 K 线→族收益经成分股等权聚合（kline_daily.pct_change）计算，yaml evidence 逐条留痕
- 炸板判定=盘中触涨停价（0.005 网格容差）且收盘未封（limit_up_down 无炸板池采集口径裁定）

## 5. 边界（不做）

- MVP 阶段无消费方（候选：M2 边界修正降档触发 §9.5、MOD-SIG-025 情绪注解、SEC-01 板块盘后报告器、M3-⑨ LLM 板块族输入、prediction_log 落库）
- 不出方向/点位；不做伪精确点概率

## 6. 测试

tests/signal_ashare/test_sector_divergence.py
