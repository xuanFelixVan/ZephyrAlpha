---
module_id: KE-1807
status: active
title: 2.229 Data Freshness-Weighted Confidence - data_freshness_weighting.py (🆕 v0.21.
category: module_blueprint
---

# 2.229 Data Freshness-Weighted Confidence - data_freshness_weighting.py (🆕 v0.21.

2.229 Data Freshness-Weighted Confidence - data_freshness_weighting.py (🆕 v0.21.0 - 盲点278 — 指标年龄对其信任度的动态折扣)

**致命问题**：FLE同时消费实时metrics（<1s龄）和批次metrics（>10min龄）——但从不对不同年龄的metrics做置信度折扣。一个10min前的"CPU=80%"和一个1s前的"order_rate=500/s"在FLE的诊断中等权。但在交易系统中，10min前的数据是上辈子——价格已变、position已变、风险暴露已变。FLE应该显式地对过时数据进行置信度折扣。
**对标**：Google Spanner TrueTime Confidence Intervals + Financial Time Series Staleness Discounting + Bloomberg REAL-TIME Flag

```python
@dataclass
class FreshnessWeightedMetric:
    raw_value: float
    raw_age_sec: float
    source: str             # "REAL_TIME_STREAM"|"BATCH_ETL"|"EXTERNAL_API"
    confidence_discount: float  # 0=完全信任, 1=完全不信
    effective_value: float      # raw_value * (1 - discount) + baseline * discount

class DataFreshnessWeighting:
    SOURCE_MAX_AGE: dict[str, float] = {
        "REAL_TIME_STREAM": 5,    # 5s
        "BATCH_ETL": 600,          # 10min
        "EXTERNAL_API": 300,       # 5min
    }
    HALF_LIFE_FACTOR: float = 2.0  # 超过max_age后每halflife折扣翻倍

    async def weight_metric_by_freshness(self,
                                           metric: Metric) -> FreshnessWeightedMetric:
        max_age = self.SOURCE_MAX_AGE.get(metric.source, 300)
        if metric.age_sec <= max_age:
            confidence_discount = 0.0  # 新鲜数据完全可信
        else:
            # Exponential decay: older = less trusted
            half_lives = (metric.age_sec - max_age) / max_age
            confidence_discount = min(0.95, 1.0 - (0.5 ** half_lives))
        # 若置信度折扣>0.5→标记为"stale"并通知FLE的diagnose对此数据降权
        if confidence_discount > 0.50:
            stale_weight = 1.0 - confidence_discount
            effective = metric.value * stale_weight + self._get_baseline(metric.name) * (1 - stale_weight)
            if confidence_discount > 0.80:
                self.FLE.notify_owner("METRIC_CRITICALLY_STALE",
                    f"Metric {metric.name} age={metric.age_sec:.0f}s, "
                    f"discount={confidence_discount:.0%}. "
                    f"Source {metric.source} max_age={max_age}s. "
                    f"FLE is using baseline instead of stale raw value.")
        else:
            effective = metric.value
        return FreshnessWeightedMetric(raw_value=metric.value, raw_age_sec=metric.age_sec,
            source=metric.source, confidence_discount=confidence_discount,
            effective_value=effective)
```
