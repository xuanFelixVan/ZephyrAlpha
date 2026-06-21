---
module_id: KE-2926
status: active
title: src/zephyr/orchestrator/feedback_sink.py
category: module_blueprint
---

# src/zephyr/orchestrator/feedback_sink.py

src/zephyr/orchestrator/feedback_sink.py

from typing import Protocol

class FeedbackSinkProtocol(Protocol):
    """Orchestrator 只知道这个 Protocol，不 import FLE 具体实现。"""
    async def record_task_metrics(self, metrics: TaskMetrics) -> None: ...
    async def record_hallucination_event(self, event: HallucinationEvent) -> None: ...
