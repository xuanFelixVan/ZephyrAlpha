"""Backward-compatibility shim — still imports from local span_stub for legacy API (SRC-0035).

For new code, use: from zephyr.l12_system_telemetry.traces import ...
"""

from zephyr.telemetry.traces.span_stub import noop_span

__all__ = ["noop_span", "span_stub"]
