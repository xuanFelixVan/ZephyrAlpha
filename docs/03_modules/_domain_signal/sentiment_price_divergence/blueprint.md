---
blueprint_id: MOD-SIG-101
module_name: sentiment_price_divergence
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-101 sentiment_price_divergence 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B10-01371（模块16 情绪-价格背离指数模型
> Sentiment-Price Divergence Index，裁定=做 P1）+ 候选注册表 CAND-TESTB-016。
> 代码：`src/zephyr/signal_ashare/sentiment_price_divergence.py`

## 0. 定位

场内对账（查重铁律⑤分工在案）：
- sector_divergence（MOD-SIG-060）= 板块间分歧度与轮动速度（横截面板块生态）；
- multi_indicator_divergence（MOD-SIG-095）= RSI/MACD/CVD 技术指标峰谷背离
  （纯价格-指标对位，语义正交裁定 P1W02 fragment 在案）；
- **情绪-价格背离指数 SDI=ΔSentiment_z−ΔPrice_z 无实现**（深挖批 min_build_spec
  明示：核心类 SentimentPriceDivergence，输入情绪指数与价格 z 分差，输出 SDI 值
  +背离方向+置信度）。本模块落地，情绪指数序列由 MOD-SIG-025
  market_sentiment_analyzer 产出注入（鸭子类型，不 import）。

## 1. 接口

```python
@dataclass(frozen=True) class SentimentPriceDivergenceConfig  # 窗/滞后/阈值（构造即校验）
@dataclass(frozen=True) class DivergenceReading               # 单点读数（SDI/方向/置信度）
class SentimentPriceDivergence:
    def compute(self, sentiment_scores, prices) -> DivergenceReading   # 最新读数
    def scan(self, sentiment_scores, prices) -> list[DivergenceReading]  # 背离事件表
```

- **z 分差**：z_s =（情绪 − 滚动窗均值）/窗总体标准差（默认窗 60）；z_p 同口径；
  窗零方差 → z=0 + notes（恒定窗无信息，不伪造背离）。
- **SDI = ΔSentiment_z − ΔPrice_z**，Δ = 当前 z − lag 根前 z（默认 lag=5）。
- **方向**：SDI ≥ +threshold（默认 1.0）→ bullish（情绪改善显著快于价格，正向背离）；
  ≤ −threshold → bearish（情绪恶化显著快于价格，负向背离）；其间 → none。
- **置信度** = min(|SDI| / confidence_scale, 1.0)（scale 默认 2.0），direction=none 时
  置信度照算（幅度读数）但 divergence=False。
- **scan**：自首个可算根起逐根计算，仅收 direction≠none 的背离事件（带 bar_index）。

## 2. 纪律

- 序列等长/≥z_window+delta_lag/有限值/价格>0 校验；非法 → ValueError（fail-closed）。
- 配置构造即校验：z_window≥10、delta_lag≥1、threshold>0、confidence_scale>0。
- PIT：z/Δ 全部滚动窗前视；scan 逐根前视无未来信息。
- frozen dataclass asdict JSON 可序列化；纯内存统计不直连 DB、不荐股。

## 3. 依赖

- import：标准库（math/statistics/dataclasses）——无 zephyr 内部 import 边。
- 上游注入：market_sentiment_analyzer（MOD-SIG-025）情绪指数序列、指数/个股价格
  （D_DATA 装配层）；下游候选：情绪页背离告警、买入侧背离过滤装配层。
