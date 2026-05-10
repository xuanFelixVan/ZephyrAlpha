"""Backward-compatibility shim — still imports from local blueprint_metrics (SRC-0035).

For new code, use: from zephyr.l12_system_telemetry.metrics import ...
"""

__all__ = ["blueprint_metrics"]
