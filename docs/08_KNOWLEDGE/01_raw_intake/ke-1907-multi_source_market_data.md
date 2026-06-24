---
module_id: KE-1816
status: active
title: 2.235 Multi-Source Market Data Divergence Detector - market_data_divergence.py (
category: module_blueprint
---

# 2.235 Multi-Source Market Data Divergence Detector - market_data_divergence.py (

2.235 Multi-Source Market Data Divergence Detector - market_data_divergence.py (🆕 v0.22.0 - 盲点284 — 多源市场数据的隐性分歧)

**致命问题**：FLE订阅多个市场数据源（Bloomberg、Reuters、Binance、Coinbase等）。当两个源对同一资产的报价出现系统性偏差（如Bloomberg延迟2s显示BTC=64500而Binance实时显示64502→2bp的价差对高频系统是巨大的）→FLE的regime_detector和anomaly_detector基于"公认"价格运行→但从未交叉验证不同源之间的分歧程度。在金融系统中，数据源分歧往往是市场微观结构变化或数据管道故障的前兆信号。
**对标**：Bloomberg Data Quality Framework + Refinitiv DataScope Select + CoinMarketCap Data Transparency + SEC Market Data Infrastructure Rules

```python
@dataclass
class CrossSourceDivergence:
    symbol: str
    sources_compared: list[str]  # ["BLOOMBERG", "REUTERS", "BINANCE_API"]
    price_difference_bps: float  # 最大价差（basis points）
    timestamp_diff_sec: float    # 时间戳偏差
    divergence_trend: str        # "STABLE"|"WIDENING"|"OSCILLATING"
    suspected_cause: str         # "SOURCE_LATENCY"|"MICROSTRUCTURE_CHANGE"|"PIPELINE_CORRUPTION"

class MultiSourceDivergenceDetector:
    MAX_ACCEPTABLE_BPS: float = 5.0      # 5bps=0.05%
    TREND_WINDOW_SAMPLES: int = 100

    async def detect_cross_source_divergence(self) -> list[CrossSourceDivergence]:
        active_symbols = await self._get_active_trading_symbols()
        divergences = []
        for symbol in active_symbols:
            sources = await self._get_available_sources(symbol)
            if len(sources) < 2:
                continue
            prices = await asyncio.gather(*[
                self._fetch_price(symbol, src) for src in sources
            ])
            valid = [(s, p) for s, p in zip(sources, prices) if p is not None]
            if len(valid) < 2:
                continue
            max_price = max(p for _, p in valid)
            min_price = min(p for _, p in valid)
            if min_price <= 0:
                continue
            bps = (max_price - min_price) / min_price * 10000
            if bps > self.MAX_ACCEPTABLE_BPS:
                trend = await self._compute_divergence_trend(symbol, bps)
                worst_src, worst_p = max(valid, key=lambda x: abs(x[1] - sum(p for _,p in valid)/len(valid)))
                divergences.append(CrossSourceDivergence(
                    symbol=symbol,
                    sources_compared=[s for s, _ in valid],
                    price_difference_bps=bps,
                    timestamp_diff_sec=max(abs((max(valid,key=lambda x:x[1])[1]/p-1)*10) for _,p in valid),
                    divergence_trend=trend,
                    suspected_cause="SOURCE_LATENCY" if trend == "STABLE"
                        else "MICROSTRUCTURE_CHANGE" if trend == "WIDENING"
                        else "PIPELINE_CORRUPTION"))
                self.FLE.notify_owner("MARKET_DATA_DIVERGENCE",
                    f"{symbol}: {bps:.1f}bps divergence across {len(valid)} sources "
                    f"({worst_src}: {worst_p:.2f}). Trend: {trend}. "
                    f"FLE will EXCLUDE outlier source from diagnosis until divergence resolves.")
                await self._exclude_divergent_source(symb
