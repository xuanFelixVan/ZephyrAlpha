---
module_id: KE-2355
status: active
title: 6.1 EMA（指数移动平均）
category: module_blueprint
---

# 6.1 EMA（指数移动平均）

6.1 EMA（指数移动平均）

```
EMA_t = α · value_t + (1-α) · EMA_{t-1}
其中 α ∈ [0.1, 0.3]（experimental 默认 0.2）
```

新值偏离 EMA 超过 `k·stddev`（experimental 默认 k=2）即标记 `spike`/`drop`。
