"""冷归档占位 — 批量归档批次 ID 生成（Phase 1）"""

from __future__ import annotations

import uuid


def next_archive_batch_id(prefix: str = "arc") -> str:
    """生成归档批次标识符。"""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
