---
module_id: KE-1106
status: active
title: ✅ 正确：引用 CTR 契约类型
category: governance
ttl: permanent
---

# ✅ 正确：引用 CTR 契约类型

✅ 正确：引用 CTR 契约类型
from zephyr.shared.contracts.market_data import NormalizedMarketData
from zephyr.shared.contracts.timestamp import Timestamp
from zephyr.shared.contracts.money import Money

def process(tick: NormalizedMarketData) -> FactorSignal:
    ...
```
