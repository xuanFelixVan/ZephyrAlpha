"""ArchiveFacade — 遥测数据归档门面（MOD-INF-015 §10 · archive）.

提供 batch_id 生成、数据归档、保留策略等 API。
"""

from __future__ import annotations

import uuid
import threading


class ArchiveFacade:
    def __init__(self, module_id: str = "", test_mode: bool = False):
        self._module_id = module_id
        self._test_mode = test_mode
        self._counter: int = 0
        self._lock = threading.Lock()

    def next_batch_id(self) -> str:
        with self._lock:
            self._counter += 1
        ts_uuid = uuid.uuid4().hex[:8]
        return f"batch-{ts_uuid}-{self._counter:06d}"

    def health(self) -> dict:
        return {
            "module_id": self._module_id,
            "batch_count": self._counter,
            "test_mode": self._test_mode,
        }
