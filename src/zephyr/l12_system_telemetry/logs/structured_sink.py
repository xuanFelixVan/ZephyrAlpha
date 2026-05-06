"""结构化日志 — JSONL 追加（Phase 1）

写入失败时静默跳过，不阻塞业务线程。
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)


def append_jsonl_record(target_file: Path, record: dict[str, Any]) -> bool:
    """向 JSONL 文件追加一行记录；成功返回 True。"""
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, default=str, ensure_ascii=False)
        with target_file.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return True
    except OSError:
        _logger.debug("structured_sink append failed: %s", target_file, exc_info=True)
        return False


def log_record_stub(level: str, message: str, **labels: Any) -> dict[str, Any]:
    """构造标准化结构化日志 dict（便于单测与下游聚合）。"""
    return {
        "ts": datetime.now(UTC).isoformat(),
        "level": level,
        "message": message,
        "labels": labels,
    }
