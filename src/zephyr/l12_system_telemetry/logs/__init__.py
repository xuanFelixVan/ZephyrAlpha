"""L12 · logs — 结构化日志流（structlog + JSONL + trace注入）"""
from zephyr.l12_system_telemetry.logs.structured_sink import (
    append_jsonl_record,
    log_record_stub,
    flush,
    panic_flush,
    buffer_depth,
    configure,
)

__all__ = [
    "append_jsonl_record",
    "log_record_stub",
    "flush",
    "panic_flush",
    "buffer_depth",
    "configure",
    "structured_sink",
]
