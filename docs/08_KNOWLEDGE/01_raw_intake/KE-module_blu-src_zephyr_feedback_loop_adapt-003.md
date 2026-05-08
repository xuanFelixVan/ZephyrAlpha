---
module_id: KE-module_blu-src_zephyr_feedback_loop_adapt-003
title: src/zephyr/feedback_loop/adapters/context_engine.py
category: module_blueprint
---

# src/zephyr/feedback_loop/adapters/context_engine.py

src/zephyr/feedback_loop/adapters/context_engine.py

class CEAdjustAdapter:
    """FLE 侧 Anomaly → CE 侧 FeedbackSignal 的适配器。"""

    def __init__(self, ce: ContextEngineProtocol) -> None:
        self._ce = ce

    async def adjust_strategy(self, task_id: str, signal_fle: "FLESignal") -> AdjustResult:
        # 把 FLE 内部 anomaly kind 映射到 CE 的 FeedbackSignal.anomaly_type
        signal_ce = FeedbackSignal(
            task_id=task_id,
            anomaly_type=_map_anomaly_kind(signal_fle.anomaly_kind),
            confidence=min(1.0, signal_fle.deviation_sigma / 3.0),
            suggested_action=_map_action(signal_fle.suggested_action),
            target_slot=signal_fle.payload.get("slot"),
            adjustment_magnitude=signal_fle.payload.get("delta", 0.1),
            observed_at=signal_fle.last_observed_at,
        )
        return await self._ce.adjust_strategy(task_id, signal_ce)
```
