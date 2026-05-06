"""分布式追踪占位 — 后续对齐 OpenTelemetry（Phase 1）"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def noop_span(operation_name: str) -> Iterator[None]:
    """空操作的 span 上下文管理器，用于在未接入 OTEL 前保持调用形状。"""
    _ = operation_name
    yield None
