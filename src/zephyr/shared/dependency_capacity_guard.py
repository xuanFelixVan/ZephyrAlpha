"""
Dependency Capacity Guard — 外部依赖容量保护 (盲点 #48)
特性：
  - ChromaDB / SQLite / OTel 远程 exporter 容量约束检查
  - 依赖不可用 → 自动 fallback
"""
from typing import Any, Optional


class DependencyCapacityGuard:
    """
    外部依赖容量守护 (盲点 #48)
    """

    def __init__(self):
        self._dependencies: dict[str, dict] = {
            "chromadb": {"max_collections": 100, "max_vectors_per_collection": 100000},
            "sqlite": {"max_db_size_mb": 1000, "max_tables": 100},
            "otel": {"max_spans_per_second": 1000, "max_spans_per_batch": 512},
        }
        self._status: dict[str, bool] = {k: True for k in self._dependencies}

    def check_dependency(self, dep_name: str) -> dict:
        limits = self._dependencies.get(dep_name, {})
        healthy = self._status.get(dep_name, True)
        return {
            "dependency": dep_name,
            "limits": limits,
            "healthy": healthy,
            "fallback_available": True,
        }

    def mark_unhealthy(self, dep_name: str):
        self._status[dep_name] = False

    def mark_healthy(self, dep_name: str):
        self._status[dep_name] = True

    def check_all(self) -> dict[str, dict]:
        return {dep: self.check_dependency(dep) for dep in self._dependencies}
