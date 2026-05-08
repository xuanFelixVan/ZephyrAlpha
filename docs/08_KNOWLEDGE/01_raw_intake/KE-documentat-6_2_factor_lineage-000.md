---
module_id: KE-documentat-6_2_factor_lineage-000
title: 6.2 Factor Lineage 端到端示例
category: documentation
---

# 6.2 Factor Lineage 端到端示例

6.2 Factor Lineage 端到端示例

```
原始 Tick (vendor=tushare, ts_ingest=2025-01-15 09:30:00.123)
   ↓ aggregate (job=tick_to_bar_1m, version=v3.2.1, run_id=...)
Bar 1m
   ↓ aggregate (job=bar_1m_to_eod, version=v2.0.0, run_id=...)
Bar EOD
   ↓ adjust (job=corporate_action_replay, version=v1.4.0, run_id=...)
AdjustedBar EOD
   ↓ compute (factor=momentum_20d, code_sha=abc123, run_id=...)
FactorValue(factor=mom_20d, symbol=600519, asof=2025-01-15, lineage_root=lin_xxx)
   ↓ aggregate
FeatureSet(asof=2025-01-15)
   ↓ predict (strategy=alpha_001, model_version=v1.2.3, run_id=...)
Signal
   ↓ optimize (portfolio=p001, optimizer_version=v2.1.0)
TargetPosition → Order → Fill → Position → PnL
```

每一条 → 在 lineage store 落一条 edge，含：`upstream_id` / `downstream_id` / `transform_job_id` / `code_sha` / `run_id` / `ts`。
