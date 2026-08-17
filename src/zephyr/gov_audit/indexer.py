# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.gov_audit.indexer
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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# 治本（裁定#18 G5）：本文件原为桩实现——__init__(index_dir) + build_index/lookup/
# add_entry/persist/cold_start_cache，与测试契约 (db_path/events_path + rebuild/
# query_stats + IndexResult{status,events_scanned,events_indexed,new_entries,errors})
# 完全不符。现重写为 SQLite 索引器，rebuild 从 events_path 读 JSONL 写入 db_path，
# query_stats 聚合查询；保留旧 ABC 方法（build_index/lookup/cold_start_cache）满足
# contracts.AuditIndexer 抽象基类，向后兼容。
import json
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from zephyr.gov_audit.contracts import AuditIndexer as AuditIndexerABC  # noqa: I001 — ABC 契约
from zephyr.shared.io.paths import REPO_ROOT  # 路径真源（SSoT）
from zephyr.shared.io.serialization import dumps
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["AuditIndexer", "IndexResult"]

# 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。
DEFAULT_INDEX_DIR: Final[Any] = REPO_ROOT / "data" / "audit_cache"
INDEX_FILE: Final[str] = "audit_index.json"

# audit_events 表列名（按顺序，用于 INSERT）
_EVENT_COLUMNS: Final[tuple[str, ...]] = (
    "entry_id",
    "event_type",
    "timestamp",
    "lamport",
    "agent_id",
    "session_id",
    "target_path",
    "operation",
    "status",
    "provenance",
    "entry_hash",
    "prev_entry_hash",
    "merkle_batch_id",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_events (
    entry_id TEXT PRIMARY KEY,
    event_type TEXT,
    timestamp TEXT,
    lamport INTEGER,
    agent_id TEXT,
    session_id TEXT,
    target_path TEXT,
    operation TEXT,
    status TEXT,
    provenance TEXT,
    entry_hash TEXT,
    prev_entry_hash TEXT,
    merkle_batch_id TEXT
);
"""

# SQL 集中化常量（裁定#18 G5 + NO-BARE-SQL gate §5.160.2）
# 所有 SQL 字面量提取到模块级常量，禁止在方法内使用裸 SQL。
# 注意：不能用 : Final[str] 类型注解——_extract_sql_constant_lines 只识别
# ast.Assign 节点，AnnAssign 不被豁免会触发 gate 误报。用普通赋值。
_SQL_INSERT_EVENT = (
    f"INSERT OR IGNORE INTO audit_events ({','.join(_EVENT_COLUMNS)}) "
    f"VALUES ({','.join('?' for _ in _EVENT_COLUMNS)})"
)
_SQL_COUNT_TOTAL = "SELECT COUNT(*) FROM audit_events"
_SQL_BY_TYPE = (
    "SELECT event_type, COUNT(*) FROM audit_events "
    "WHERE event_type IS NOT NULL GROUP BY event_type"
)
_SQL_BY_AGENT = (
    "SELECT agent_id, COUNT(*) FROM audit_events "
    "WHERE agent_id IS NOT NULL GROUP BY agent_id"
)


@dataclass
class IndexResult:
    """索引重建结果——治本（裁定#18 G5）：对齐 test_audit_indexer.py 契约。

    字段：status("ok"/"no_data")、events_scanned、events_indexed、new_entries、errors。
    """

    status: str = ""
    events_scanned: int = 0
    events_indexed: int = 0
    new_entries: int = 0
    errors: list[str] = field(default_factory=list)

    def model_dump(self) -> dict[str, Any]:
        """Pydantic-compatible dump -- 对齐 test_indexer.py."""
        return {
            "status": self.status,
            "events_scanned": self.events_scanned,
            "events_indexed": self.events_indexed,
            "new_entries": self.new_entries,
            "errors": list(self.errors),
        }


class AuditIndexer(AuditIndexerABC):
    """审计事件索引器——治本（裁定#18 G5）：对齐 test_audit_indexer.py 契约。

    旧桩 __init__(index_dir) + build_index/lookup/add_entry/persist/cold_start_cache，
    与测试契约 (db_path/events_path + rebuild/query_stats) 完全不符。现重写为
    SQLite 索引器，保留旧 ABC 方法满足 contracts.AuditIndexer 抽象基类。

    构造：AuditIndexer(db_path=None, events_path=None)，默认
    _db_path=Path("audit_index.db")、_events_path=Path("events.jsonl")。
    旧 AuditIndexer(index_dir=...) 调用仍兼容（index_dir 派生 db_path）。
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        events_path: str | Path | None = None,
        index_dir: str | Path | None = None,
    ) -> None:
        # 向后兼容：旧 index_dir 调用 → 派生 db_path
        if index_dir is not None and db_path is None:
            db_path = Path(index_dir) / "audit_index.db"
        self._db_path: Path = Path(db_path) if db_path else Path("audit_index.db")
        self._events_path: Path = Path(events_path) if events_path else Path("events.jsonl")
        # 旧 ABC API 状态
        self._index_dir: Path = self._db_path.parent
        self._index_path: Path = self._index_dir / INDEX_FILE
        self._index: dict[str, Any] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def db_path(self) -> Path:
        """只读：db_path（Stage 4 公共化）。"""
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        """写入：db_path（Stage 4 公共化）。"""
        self._db_path = value

    @property
    def events_path(self) -> Path:
        """只读：events_path（Stage 4 公共化）。"""
        return self._events_path

    @events_path.setter
    def events_path(self, value):
        """写入：events_path（Stage 4 公共化）。"""
        self._events_path = value


    # ------------------------------------------------------------------
    # 新 API（裁定#18 G5）：rebuild + query_stats
    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))
        conn.executescript(_SCHEMA)
        return conn

    def rebuild(self) -> IndexResult:
        """从 events_path 读取 JSONL 事件，写入 SQLite 索引。

        Returns:
            IndexResult：status="no_data"（文件不存在/空）或 "ok"（成功）。
            events_scanned=读取事件数；events_indexed=有效事件数（含 entry_id）；
            new_entries=本次新插入数（去重）；errors=缺 entry_id 等错误。
        """
        result = IndexResult()
        if not self._events_path.exists():
            result.status = "no_data"
            return result
        try:
            content = self._events_path.read_text(encoding="utf-8")
        except OSError:
            result.status = "no_data"
            return result
        if not content.strip():
            result.status = "no_data"
            return result

        events: list[dict[str, Any]] = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                result.errors.append(f"JSON parse error: {exc}")
        result.events_scanned = len(events)
        if not events:
            result.status = "no_data"
            return result

        conn = self._connect()
        try:
            new_count = 0
            indexed = 0
            for ev in events:
                entry_id = ev.get("entry_id")
                if not entry_id:
                    result.errors.append(
                        f"Missing entry_id in event: {ev.get('event_type', '?')}"
                    )
                    continue
                values = tuple(ev.get(col) for col in _EVENT_COLUMNS)
                cur = conn.execute(_SQL_INSERT_EVENT, values)
                if cur.rowcount > 0:
                    new_count += 1
                indexed += 1
            conn.commit()
            result.status = "ok"
            result.events_indexed = indexed
            result.new_entries = new_count
        except sqlite3.Error as exc:
            result.errors.append(f"DB error: {exc}")
            result.status = "ok"
        finally:
            conn.close()
        return result

    def query_stats(self) -> dict[str, Any]:
        """查询索引统计：total/by_event_type/by_agent。

        db 不存在或查询失败 → 返回空统计 {"total":0,"by_event_type":{},"by_agent":{}}。
        """
        empty: dict[str, Any] = {"total": 0, "by_event_type": {}, "by_agent": {}}
        if not self._db_path.exists():
            return empty
        try:
            conn = self._connect()
        except sqlite3.Error:
            return empty
        try:
            total = conn.execute(_SQL_COUNT_TOTAL).fetchone()[0]
            by_type = {
                row[0]: row[1]
                for row in conn.execute(_SQL_BY_TYPE)
            }
            by_agent = {
                row[0]: row[1]
                for row in conn.execute(_SQL_BY_AGENT)
            }
            return {"total": total, "by_event_type": by_type, "by_agent": by_agent}
        except sqlite3.Error:
            return empty
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # 旧 ABC API（向后兼容，满足 contracts.AuditIndexer 抽象基类）
    # ------------------------------------------------------------------
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
            except Exception:  # noqa: BLE001 — broad exception catch
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
            self._index["built_at"] = now_utc().isoformat()
            self._index_path.write_text(
                dumps(self._index, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return True
        except Exception as exc:  # noqa: BLE001 — broad exception catch
            logger.error("Failed to persist index: %s", exc, exc_info=True)
            return False

    def cold_start_cache(self) -> dict[str, Any]:
        return {
            "total_dimensions": len(self._index.get("by_dimension", {})),
            "total_entries": self._index.get("total_entries", 0),
            "severity_distribution": self._index.get("by_severity", {}),
        }
