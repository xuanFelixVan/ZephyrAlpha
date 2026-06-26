---
module_id: KE-585
status: active
title: 8.2 本视图的保障机制
category: documentation
ttl: permanent
---

# 8.2 本视图的保障机制

8.2 本视图的保障机制

**机制一：跨平面契约统一**

`shared/contracts/` 承载以下**跨平面统一契约**（所有平面必须同契约）：

| 契约 | Cold Path 实现 | Warm Path 实现 | Hot Path 实现（T1 后）|
|---|---|---|---|
| `MarketImpactModel` | 真实成交历史回归系数 | 同 Cold 参数 | C++ 硬编码同参数 |
| `WeightPortfolio` | DataFrame-based | asyncio dataclass | C++ struct（同 schema）|
| `OrderBook` | Parquet snapshot | Redis in-memory | Shared Memory |
| `FillEvent` | Parquet record | Kafka message | Aeron message（同 schema）|
| `Timestamp` | pandas Timestamp (nanosecond) | datetime + tz | int64 nanosecond epoch |

**所有平面共享 `shared/contracts/` canonical schema**，不允许任何平面独立发明 schema。

**机制二：Champion-Challenger Shadow Validation**

L13 `experiment_pipeline/shadow/` 强制所有 Cold → Warm 模型更新先跑 **Shadow Trading**（Warm Path 并行运行新旧模型，无真实资金）≥ N 天后再晋级到 Hot Path。

**机制三：三平面共享 `risk/`**

风控 `shared/contracts/RiskConstraint` 在 Cold 回测 / Warm 实盘 / Hot 拦截三处必须**使用同一参数文件**（`config/risk_params.yaml`），避免三平面参数漂移。
