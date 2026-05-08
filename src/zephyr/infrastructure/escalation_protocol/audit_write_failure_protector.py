"""Audit Write Failure Protector — v0.13.0 审计写入失败保护器。

委托 zephyr.audit_trail.writer.AuditWriter 内置的写入失败保护机制。
AuditWriter.write() 内部已实现连续5次失败后自动进入 readonly 模式。
"""
from __future__ import annotations

from zephyr.audit_trail.writer import AuditWriter


class AuditWriteProtector:
    """审计写入失败保护器——委托 AuditWriter 内置保护。"""

    def __init__(self, writer: AuditWriter | None = None):
        self._writer = writer

    def _ensure_writer(self) -> AuditWriter | None:
        if self._writer is None:
            try:
                self._writer = AuditWriter()
            except Exception:
                pass
        return self._writer

    def record_failure(self) -> None:
        w = self._ensure_writer()
        if w is not None:
            w._write_failures += 1
            if w._write_failures >= w._max_write_failures:
                w._readonly = True

    def can_write(self) -> bool:
        w = self._ensure_writer()
        if w is not None:
            return not w._readonly
        return True

    def reset(self) -> None:
        w = self._ensure_writer()
        if w is not None:
            w._write_failures = 0
            w._readonly = False
