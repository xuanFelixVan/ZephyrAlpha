"""
Finalizer — 优雅清理器
========================
蓝图: ARC-0001 §4.4 (六阶)
借鉴: K8s Finalizer + OwnerReference
"""

from __future__ import annotations

from typing import Callable


class Finalizer:
    """优雅清理器——关闭前完成所有必要持久化。"""

    def __init__(self) -> None:
        self._cleanup_fns: list[tuple[str, Callable[[], None]]] = []

    def register(self, resource_type: str, cleanup_fn: Callable[[], None]) -> None:
        self._cleanup_fns.append((resource_type, cleanup_fn))

    def run(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for resource_type, fn in self._cleanup_fns:
            try:
                fn()
                results[resource_type] = True
            except Exception:
                results[resource_type] = False
        return results
