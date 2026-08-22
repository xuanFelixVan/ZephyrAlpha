---
blueprint_id: MOD-SIG-059
module_name: option_sentiment
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

# MOD-SIG-059 option_sentiment 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘录 §9.9（华泰 2026-03 机构范式），M1-⑨ 情绪注解维度⑨。
> 代码：`src/zephyr/signal_ashare/option_sentiment.py`

## 0. 定位

期权情绪三件套——A 股单边做多市场衍生品"少而精"只取 PCR+IV 两指标最有效，加 Skew 尾部偏度作机构行为佐证，合成"情绪注解维度⑨"（候选消费方 MOD-SIG-025 综合分，权重 ≤0.10 纪律由下游控制）。主标的=300ETF 期权（510300.SH），50ETF/500ETF/科创同算法可经 config.underlying 扩展。

## 1. 接口

```python
def compute_option_sentiment(
    trade_date: str | date | datetime | None = None,  # None=主标的 iv_surface 最新数据日（PIT 数据日口径）
    ch_client: Any | None = None,                     # None=延迟取 ch_writer.get_client，不可得→degraded
    config: OptionSentimentConfig | None = None,      # None=44号 §9.9 + 2026-08-22 数据实证默认口径
) -> OptionSentimentResult
```

只读四表：option_iv_surface / option_kline / option_greeks / calendar_event。

## 2. 输出契约

`OptionSentimentResult`（frozen dataclass，asdict JSON 可序列化）：

- F1 `pcr` / `pcr_basis` / `pcr_percentile`：成交量 PCR=Σ认沽 volume/Σ认购 volume（无任何表含 open_interest 持仓列→实证降级成交量口径留痕；OI 回填后自动切持仓口径）；分位 <20%=过度乐观反向风险，>80%=恐慌过度底部区（pcr_min_periods=20 守卫）
- F2 `iv_rank` / `iv_jump_flag`：平值 IV 分位（最近月 strike≈中位数选约，atm_basis="strike_median" 留痕；min_periods=60 守卫）；IV 单日跳升 >+3σ→避险急增
- F3 `skew_norm` / `skew_extreme` / `divergence_warning`：skew=IV(25Δ沽)−IV(25Δ购) 经 greeks.delta 选约（|delta∓0.25| 最近者）JOIN iv_surface 取 IV；归一 skew>90% 分位=极端左偏；PCR 低分位×Skew 极端背离=多空分歧最大警示
- `composite_score ∈ [-1,1]`（可用子分均值，缺项不累及）+ `annotation` 中文注解文本链（维度⑨直接可消费）
- `m1_threshold_scale`：期权到期日（calendar_event index_option_expiry 当日）=0.8（防伽马挤压假情绪），否则 1.0

## 3. 不变量（头注 INVARIANTS 原文）

- m1_threshold_scale ∈ {1.0, 0.8}
- pcr_basis ∈ {"volume", "open_interest"}（当前实证恒为 "volume"）
- 无数据/查询异常/客户端不可用 MUST 返回 degraded=True 空结果不炸
- 各字段独立降级互不累及
- iv_surface.delta 全 0 实证不可用，禁止以该列选约

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→degraded=True 不抛；trade_date 格式非法→ValueError（fail-closed）
- 分位窗样本不足（pcr<20 / iv_rank<60 / skew<10 守卫）→对应字段 None 降级
- iv_surface data_source 08-14 切换（miniqmt 4 到期月→akshare_sina 仅最近月）→统一限定"最近月"跨源一致口径
- option_greeks option_type 空串→由 delta 符号推断（>0=call，<0=put）
- calendar_event 查询失败→fail-open m1_threshold_scale=1.0 留痕

## 5. 边界（不做）

- MVP 阶段无消费方（候选：MOD-SIG-025 情绪注解维度⑨ 经输入契约注入，权重≤0.10；M1 阈值缩放因子消费方）
- 本模块只出分数与注解文本，权重由下游控制

## 6. 测试

tests/signal_ashare/test_option_sentiment.py
