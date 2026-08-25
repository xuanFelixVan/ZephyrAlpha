---
blueprint_id: MOD-DAT-MTF-FUSION
module_name: multi_timeframe_fusion
domain: D_DATA
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_DATA
path: src/zephyr/data/multi_timeframe_fusion.py
granularity: file
---

# MOD-DAT-MTF-FUSION multi_timeframe_fusion 蓝图（多周期数据融合）

> **module_id**: MOD-DAT-MTF-FUSION | **域**: D_DATA | **优先级**: P1
> **来源**: B13-04249（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，D-DATA-25，§17.1）
> 代码：`src/zephyr/data/multi_timeframe_fusion.py`

## 0. 定位

多时间尺度数据融合：`resample()` 统一接口（1min~1d）——交易日历对齐 +
时间戳归一（bar close 口径）+ 前向填充上限（≤3 根）+ 融合质量评分
（覆盖率/对齐误差）输出 quality_flag。纯 pandas 内存计算，provider 无关。

与既有族分工（查重裁定）：
- MOD-L00-004 kline_resampler（10603322，stable）：880 板块 K线 15m/30m/60m
  **ClickHouse 库内合成**（toStartOfInterval 聚合，板块专用、DB 面向）。
  本模块为**内存态统一重采样接口**（任意标的 K线 DataFrame、1min~1d 全域、
  质量评分面向），不复制其 SQL 合成路径；语义对齐走设计边，不 import。
- B1-00634 dig 已裁定"不做-重复:B13-04249"，其缺口明细并入本模块。

## 1. 判定核心（纯内存，无 IO）

- `resample(bars, source_freq, target_freq, trading_days=None, ffill_limit=3)`：
  未知频率/缺必需列（timestamp/open/high/low/close/volume）/source>target
  粒度倒挂 → ValueError Fail-Closed。
- 频率表：1min/5min/15min/30min/60min/1d（分钟映射+日级特例）。
- 时间戳归一：bar close 口径（右闭右标）；非边界落地的源条计入
  alignment_error_count。
- 交易日历对齐：`trading_days` 注入（可空）；提供时剔除日历外目标桶。
- 前向填充：目标桶缺失按 close ffill，连续填充 ≤ ffill_limit 根，超限
  留 NaN 并计入质量统计。
- 质量评分：coverage_ratio（有效目标桶/应到桶）+ alignment_error_count →
  quality_flag ∈ {good / degraded / poor}（阈值常量可配）。

## 2. 接口

```python
SUPPORTED_FREQS: dict[str, ...] 频率表
@dataclass(frozen=True) FusionQuality: expected_bars/actual_bars/coverage_ratio/alignment_error_count/ffill_used/quality_flag
@dataclass(frozen=True) FusionResult: data(DataFrame)/quality(FusionQuality)
@dataclass(frozen=True) FusionConfig: ffill_limit=3/good_coverage=0.95/degraded_coverage=0.80
class MultiTimeframeFusion(config=None):
    resample(bars, source_freq, target_freq, trading_days=None, ffill_limit=None) -> FusionResult
```

## 3. 不变量

- 纯 pandas 内存计算，零 zephyr import、零 IO。
- OHLC 聚合正确性：open=首/high=max/low=min/close=尾/volume=sum。
- 同输入必同输出（确定性）；ffill 不超过上限，超限留痕入质量评分。

## 4. 依赖

- MOD-L00-004 kline_resampler（设计边：周期合成语义对齐，不 import）

## 5. MVP 边界

- miniqmt_service/mkt_data 消费接线、交易日历真源装配留运行时装配批；
  本模块交付统一 resample 接口 + 时间戳归一 + ffill 上限 + 质量评分核心。
