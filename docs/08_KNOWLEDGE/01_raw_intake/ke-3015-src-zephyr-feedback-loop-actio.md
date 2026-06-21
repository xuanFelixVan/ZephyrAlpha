---
module_id: KE-2915
status: active
title: src/zephyr/feedback-loop/action_protocols.py (FLE 侧定义)
category: module_blueprint
---

# src/zephyr/feedback-loop/action_protocols.py (FLE 侧定义)

src/zephyr/feedback-loop/action_protocols.py (FLE 侧定义)

from typing import Protocol

class ContextAdjustActionProtocol(Protocol):
    """对应 Context Engine 的 adjust_strategy 接口。"""
    async def adjust_strategy(self, task_id: str, signal: "FeedbackSignal") -> "AdjustResult": ...

class OrchestratorControlActionProtocol(Protocol):
    """对应 Orchestrator 的控制动作。"""
    async def pause_task_kind(self, task_kind: str, ttl_minutes: int, reason: str) -> None: ...
    async def quarantine_agent(self, agent_id: str, ttl_minutes: int, reason: str) -> None: ...

class VMSControlActionProtocol(Protocol):
    """对应 VMS 的临时降权检索。"""
    async def quarantine_collection(self, collection: str, ttl_minutes: int, reason: str) -> None: ...

class LSGControlActionProtocol(Protocol):
    """对应 LSG 的严格度调整。"""
    async def bump_strictness(self, delta: float, ttl_minutes: int, reason: str) -> None: ...
```
