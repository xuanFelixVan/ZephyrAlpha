"""
Re-export wrapper — canonical implementation at zephyr.l01_infrastructure.warm_hot_gate.

TD-SHARED-001: 发散副本统一为 re-export wrapper，消除代码漂移。
"""
from zephyr.l01_infrastructure.warm_hot_gate import *  # noqa: F401,F403
from zephyr.l01_infrastructure.warm_hot_gate import WarmHotGate, GateCheckResult  # noqa: F401
