---
module_id: KE-module_blu-2_239_rumor_noise-aware_anomal-000
title: 2.239 Rumor/Noise-Aware Anomaly Filtering - rumor_noise_filter.py (🆕 v0.22.0 - 盲
category: module_blueprint
---

# 2.239 Rumor/Noise-Aware Anomaly Filtering - rumor_noise_filter.py (🆕 v0.22.0 - 盲

2.239 Rumor/Noise-Aware Anomaly Filtering - rumor_noise_filter.py (🆕 v0.22.0 - 盲点288 — 市场噪音引起的系统指标波动伪装成系统异常)

**致命问题**：金融市场的系统指标（CPU、memory、网络IO）不仅仅是系统行为，也包括市场行为的印记。当SEC发布一则重要公告→市场交易量瞬间暴增10x→order_router CPU飙升→FLE的anomaly detector触发"CPU_THROTTLE_DETECTED"→DIAGNOSE诊断为资源不足→REPAIR增加更多CPU→但这不是系统问题，是正常的市场事件。FLE在昨夜一个Twitter谣言导致的市场恐慌中扩容了50%的计算资源→成本暴增且无必要。需要区分"系统真的出了故障"vs"市场行为导致的系统指标正常波动"。
**对标**：Bloomberg Terminal Event-Driven Analytics + RavenPack News Sentiment Impact + Refinitiv MarketPsych + SEC EDGAR Real-Time Feed

```python
@dataclass
class MarketNoiseContext:
    concurrent_news_events: list[str]   # "SEC_FILING_AAPL"|"FOMC_MINUTES"|"TWITTER_RUMOR_TSLA"
    social_media_sentiment_surge: float # 0-1 sentiment异常度
    trading_volume_multiple: float      # 当前volume / 正常volume
    volatility_regime_change: bool      # VIX/implied vol 跳变
    event_type: str                     # "REGULATORY"|"EARNINGS"|"MACRO"|"RUMOR"|"NONE"

class RumorNoiseAwareAnomalyFilter:
    ANOMALY_CORRELATION_THRESHOLD: float = 0.75  # 指标异常与market noise的Pearson r

    async def classify_anomaly_context(self,
                                         anomaly: Anomaly,
                                         market_noise: MarketNoiseContext) -> NoiseFilteredAnomaly:
        # 1. Cross-correlate: 此anomaly的时间线与market events有高相关性吗
        correlation_score = await self._compute_event_anomaly_correlation(
            anomaly.metrics_timeline, market_noise.concurrent_news_events)
        # 2. 区分: 系统级异常 vs 市场传导正常
        if correlation_score > self.ANOMALY_CORRELATION_THRESHOLD and market_noise.event_type != "NONE":
            self.FLE.notify_owner("MARKET_NOISE_FILTERED_ANOMALY",
                f"Anomaly on {anomaly.target_system} ({anomaly.metric_name}=>{anomaly.z_score:.1f}σ) "
                f"strongly correlates (r={correlation_score:.2f}) with market event: "
                f"{market_noise.event_type} ({', '.join(market_noise.concurrent_news_events[:3])}). "
                f"Volume multiple: {market_noise.trading_volume_multiple:.1f}x. "
                f"FLE reclassified this as MARKET_CONDUCTION—NOT a system fault. "
                f"Will MONITOR only—no repair action will be taken for {anomaly.target_system}.")
            return NoiseFilteredAnomaly(
                anomaly=anomaly,
                classification="MARKET_CONDUCTION",
                confidence=correlation_score,
                recommended_fle_action="MONITOR_ONLY_NO_REPAIR")
        else:
            return NoiseFilteredAnomaly(
                anomaly=anomaly,
                classification="GENUINE_SYSTEM_ANOMALY",
                confidence=1.0 - correlation_score,
                recommended_fle_action="PROCEED_WITH_DIAGNOSIS")
```
