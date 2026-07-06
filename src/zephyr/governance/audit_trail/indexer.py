# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.governance.audit_trail.indexer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.query; pipeline_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 索引必须支持增量更新; 全量重建不丢数据
# [MODIFY-GUARD] 索引格式变更必须同步 cold_start.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 索引构建失败返回None
# [TESTS] tests/audit-orchestrator/test_indexer.py
# [A_module] module_id=MOD-GOV_indexer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import json
import logging
from pathlib import Path
from typing import Any

from zephyr.governance.audit_trail.contracts import AuditIndexer as AuditIndexerABC  # 5.104.14 修复: 继承ABC契约
from zephyr.shared.utils.time_utils import now_utc
from typing import Final

logger = logging.getLogger(__name__)

__all__ = ["AuditIndexer"]

DEFAULT_INDEX_DIR: Final[Any] = Path("data/audit_cache")
INDEX_FILE: Final[str] = "audit_index.json"


class AuditIndexer(AuditIndexerABC):  # 5.104.14 修复: 继承ABC契约
    def __init__(self, index_dir: Path | None = None) -> None:
        self._index_dir = Path(index_dir or DEFAULT_INDEX_DIR)
        self._index_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._index_dir / INDEX_FILE
        self._index: dict[str, Any] = {}

    def build_index(self, force: bool = False) -> dict[str, Any]:
        if not force and self._index:
            return {"status": "cached", "entries": len(self._index)}

        self._index = {
            "built_at": "",
            "total_entries": 0,
            "by_dimension": {},
            "by_severity": {},
            "by_type": {},
        }

        if self._index_path.exists():
            try:
                cached = json.loads(self._index_path.read_text(encoding="utf-8"))
                self._index = cached
            except Exception:
                logger.warning("Corrupted index cache, rebuilding", exc_info=True)

        self._index["built_at"] = self._index.get("built_at", "")
        return {"status": "rebuilt", "entries": self._index.get("total_entries", 0)}

    def lookup(self, key: str) -> dict[str, Any] | None:
        if not self._index:
            self.build_index()
        by_dim = self._index.get("by_dimension", {})
        return by_dim.get(key)

    def add_entry(self, dim_id: str, severity: str, audit_type: str, count: int = 1) -> None:
        by_dim = self._index.setdefault("by_dimension", {})
        by_dim[dim_id] = by_dim.get(dim_id, 0) + count

        by_sev = self._index.setdefault("by_severity", {})
        by_sev[severity] = by_sev.get(severity, 0) + count

        by_type = self._index.setdefault("by_type", {})
        by_type[audit_type] = by_type.get(audit_type, 0) + count

        self._index["total_entries"] = self._index.get("total_entries", 0) + count

    def persist(self) -> bool:
        try:
            from datetime import datetime

            self._index["built_at"] = now_utc().isoformat()
            self._index_path.write_text(
                json.dumps(self._index, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            return True
        except Exception as exc:
            logger.error("Failed to persist index: %s", exc, exc_info=True)
            return False

    def cold_start_cache(self) -> dict[str, Any]:
        return {
            "total_dimensions": len(self._index.get("by_dimension", {})),
            "total_entries": self._index.get("total_entries", 0),
            "severity_distribution": self._index.get("by_severity", {}),
        }


class IndexResult:
    def __init__(self, index_id="", entries_indexed=0, timestamp=None, errors=None):
        self.index_id = index_id
        self.entries_indexed = entries_indexed
        self.timestamp = timestamp
        self.errors = errors or []