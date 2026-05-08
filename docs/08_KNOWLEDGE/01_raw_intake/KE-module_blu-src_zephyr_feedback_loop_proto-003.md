---
module_id: KE-module_blu-src_zephyr_feedback_loop_proto-003
title: src/zephyr/feedback_loop/protocol.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/feedback_loop/protocol.py (experimental 产出)

src/zephyr/feedback_loop/protocol.py (experimental 产出)

from typing import Protocol

class FeedbackLoopProtocol(Protocol):
    # Sink：接收指标
    async def record_metric(self, metric: Metric) -> None: ...
    async def record_batch(self, metrics: list[Metric]) -> BatchRecordResult: ...

    # Analyze：查询基线 / 异常
    async def get_baseline(self, metric_name: str, window: str = "7d") -> Baseline: ...
    async def detect_anomalies(self, since: datetime | None = None) -> list[Anomaly]: ...

    # Dispatch：触发动作
    async def dispatch_action(self, anomaly: Anomaly) -> ActionResult: ...
    async def list_pending_actions(self) -> list[PendingAction]: ...
    async def acknowledge_action_outcome(self, action_id: str, outcome: ActionOutcome) -> None: ...

    # Query
    async def query_timeseries(self, metric_name: str, since: datetime, until: datetime) -> list[Metric]: ...
    async def stats(self) -> FLEStats: ...

class InProcessFeedbackLoop:
    """SQLite 时间序列 + 规则引擎。"""

class DistributedFeedbackLoop:
    """beta+：InfluxDB + 分布式分析器。"""
```

| Phase | 实施形态 | 运行方式 | 触发升级条件 |
|:-:|---------|---------|-------------|
| **experimental** | **`InProcessFeedbackLoop`（SQLite + 移动平均）** | 进程内异步 | - |
| beta | `DistributedFeedbackLoop`（InfluxDB + SPC 算法） | HTTP 服务 | 数据点 > 100 万 或 误报率 > 20% |
| stable | 强化学习 Evolve | RL Agent | beta 数据充足后 |

**所有 API 均为 `async`**。进程内锁 `asyncio.Lock`，跨进程锁 `filelock.FileLock`。**严禁 `threading.Lock`**。

---
