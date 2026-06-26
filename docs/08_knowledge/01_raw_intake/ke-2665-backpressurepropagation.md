---
module_id: KE-2570
status: active
title: BackpressurePropagation（背压传导）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# BackpressurePropagation（背压传导）

BackpressurePropagation（背压传导）

```python
@dataclass
class BackpressureSignal:
    """背压信号——从 EventBus 向上游传播"""
    source_module: str         # 哪个模块慢
    queue_usage_pct: float     # 队列使用率 (0.0-1.0)
    severity: str              # "warning" (>80%) | "critical" (>95%)
    affected_upstream: list[str]  # 受影响的上有模块ID

class BackpressurePropagator:
    """背压传导——不是单向减速，而是链式减速"""
    _thresholds: dict = {
        "warning": 0.80,   # 80% → 发 WARNING 信号→上游模块限速到 50%
        "critical": 0.95,  # 95% → 发 CRITICAL 信号→上游模块暂停写入
    }

    async def propagate(self, signal: BackpressureSignal) -> None:
        """根据队列使用率→计算减速因子→通知上游模块"""
        for upstream_id in signal.affected_upstream:
            throttle_factor = self._calc_throttle(signal.queue_usage_pct)
            await EventBus.publish(BackpressureEvent(
                target_module=upstream_id,
                throttle_factor=throttle_factor
            ))
```
