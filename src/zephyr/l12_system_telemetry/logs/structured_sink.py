"""L12 · logs/structured_sink — 结构化日志管道。

蓝图 §5: structlog 配置 + JSONL 写入 + trace_id 注入 + ring buffer + RULE-ONE 原子写入。
"""

from __future__ import annotations

import json
import logging
import os
import threading
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

_DEFAULT_LOG_DIR: Path = Path("data/telemetry/prod/logs")
_BUFFER_MAX: int = 500
_FLUSH_INTERVAL_SECONDS: float = 5.0
_MAX_FILE_BYTES: int = 10 * 1024 * 1024

_log_buffer: deque[dict[str, Any]] = deque()
_buffer_lock: threading.Lock = threading.Lock()
_flush_timer: threading.Timer | None = None


def configure(
    log_dir: Path | None = None,
    buffer_size: int | None = None,
    max_file_bytes: int | None = None,
) -> None:
    global _DEFAULT_LOG_DIR, _BUFFER_MAX, _MAX_FILE_BYTES
    if log_dir is not None:
        _DEFAULT_LOG_DIR = log_dir
    if buffer_size is not None:
        _BUFFER_MAX = buffer_size
    if max_file_bytes is not None:
        _MAX_FILE_BYTES = max_file_bytes


def _inject_trace_context(record: dict[str, Any]) -> None:
    try:
        from zephyr.l12_system_telemetry.traces.span_stub import _current_span
        span = _current_span()
        if span is not None:
            record.setdefault("trace_id", span.context.trace_id)
            record.setdefault("span_id", span.context.span_id)
    except Exception:
        pass


def append_jsonl_record(
    record: dict[str, Any],
    labels: dict[str, Any] | None = None,
) -> bool:
    ts = datetime.now(UTC).isoformat()
    entry: dict[str, Any] = {
        "ts": ts,
    }
    if labels:
        entry["labels"] = labels
    entry.update(record)

    _inject_trace_context(entry)

    with _buffer_lock:
        _log_buffer.append(entry)
        overflow = len(_log_buffer) > _BUFFER_MAX

    if overflow:
        flush()

    return True


def log_record_stub(
    level: str,
    message: str,
    **labels: Any,
) -> dict[str, Any]:
    entry = {
        "ts": datetime.now(UTC).isoformat(),
        "level": level,
        "message": message,
        "labels": labels,
    }
    _inject_trace_context(entry)
    return entry


def flush() -> int:
    with _buffer_lock:
        if not _log_buffer:
            return 0
        batch = list(_log_buffer)
        _log_buffer.clear()

    target = _resolve_target_path()
    _write_batch_atomic(target, batch)
    return len(batch)


def _resolve_target_path() -> Path:
    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    return _DEFAULT_LOG_DIR / f"telemetry_{date_str}.jsonl"


def _write_batch_atomic(target: Path, batch: list[dict[str, Any]]) -> None:
    tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = "\n".join(
            json.dumps(entry, default=str, ensure_ascii=False) for entry in batch
        ) + "\n"

        existing = ""
        if target.exists() and target.stat().st_size < _MAX_FILE_BYTES:
            existing = target.read_text(encoding="utf-8")

        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(existing + lines)

        os.replace(tmp, target)
    except (OSError, PermissionError):
        try:
            os.remove(tmp)
        except OSError:
            pass
        _logger.debug("structured_sink atomic write failed: %s", target, exc_info=True)


def panic_flush() -> int:
    return flush()


def buffer_depth() -> int:
    with _buffer_lock:
        return len(_log_buffer)
