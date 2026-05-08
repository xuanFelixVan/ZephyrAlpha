---
module_id: KE-governance-api-000
title: ✅ 正确：仅导出公开 API
category: governance
---

# ✅ 正确：仅导出公开 API

✅ 正确：仅导出公开 API
from zephyr.alpha.market_data_pipeline import MarketDataPipeline
from zephyr.alpha.market_data_pipeline import TickNormalizer

__all__ = ["MarketDataPipeline", "TickNormalizer"]
