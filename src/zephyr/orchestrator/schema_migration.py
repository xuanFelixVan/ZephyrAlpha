"""数据库 Schema 演化契约（CT-SCHEMA-MIGRATE）——向后兼容迁移+回滚脚本。"""

from __future__ import annotations

class SchemaMigration:
    def __init__(self):
        self._version: int = 1
        self._history: list[dict] = []

    def current_version(self) -> int:
        return self._version

    def migrate(self, to_version: int) -> bool:
        if to_version <= self._version:
            return False
        self._history.append({"from": self._version, "to": to_version})
        self._version = to_version
        return True

    def rollback(self, target_version: int) -> bool:
        if target_version >= self._version:
            return False
        self._version = target_version
        return True
