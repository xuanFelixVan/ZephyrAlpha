"""Backward-compatibility shim — still imports from local cold_stub for legacy API (SRC-0035).

For new code, use: from zephyr.l12_system_telemetry.archive import ...
"""

from zephyr.telemetry.archive.cold_stub import next_archive_batch_id

__all__ = ["cold_stub", "next_archive_batch_id"]
