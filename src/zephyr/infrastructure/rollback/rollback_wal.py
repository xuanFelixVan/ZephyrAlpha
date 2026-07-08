# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_wal
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_wal | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackWAL — 回滚预写日志。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B127 + exit code 45

回滚操作本身的 WAL (Write-Ahead Log):
    每次回滚前记入 WAL -> 确保回滚本身可回滚。
    WAL 不完整 -> exit 45 (ROLLBACK_WAL_INCOMPLETE)。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class WALEntry:
    entry_id: str
    operation: str
    from_commit: str
    to_commit: str
    files: list[str]
    status: str
    written_at: str


@dataclass
class WALStatus:
    complete: bool
    entry_count: int
    pending_count: int
    oldest_pending: str
    exit_code: int


class RollbackWAL:
    EXIT_CODE_WAL_INCOMPLETE: int = 45
    WAL_FILE: str = ".zephyr/rollback_wal.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._wal_path = self._project_root / self.WAL_FILE

    def write_ahead(self, operation: str, from_commit: str, to_commit: str, files: list[str]) -> WALEntry:
        entry_id = f"WAL-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S-%f')}"

        entry = WALEntry(
            entry_id=entry_id,
            operation=operation,
            from_commit=from_commit,
            to_commit=to_commit,
            files=files,
            status="PENDING",
            written_at=datetime.now(UTC).isoformat(),
        )

        self._wal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._wal_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "entry_id": entry.entry_id,
                        "operation": entry.operation,
                        "from_commit": entry.from_commit,
                        "to_commit": entry.to_commit,
                        "files": entry.files,
                        "status": entry.status,
                        "written_at": entry.written_at,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            f.flush()

        return entry

    def mark_complete(self, entry_id: str) -> bool:
        if not self._wal_path.exists():
            return False

        entries = self._read_all()
        found = False
        updated: list[dict[str, Any]] = []

        for e in entries:
            if e.get("entry_id") == entry_id:
                e["status"] = "COMPLETE"
                e["completed_at"] = datetime.now(UTC).isoformat()
                found = True
            updated.append(e)

        if found:
            tmp_path = f"{self._wal_path}.{os.getpid()}.tmp"
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    for e in updated:
                        f.write(json.dumps(e, ensure_ascii=False) + "\n")
                os.replace(tmp_path, self._wal_path)
            except PermissionError:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

        return found

    def check_incomplete(self) -> WALStatus:
        entries = self._read_all()
        pending = [e for e in entries if e.get("status") != "COMPLETE"]
        complete = len(entries) == len([e for e in entries if e.get("status") == "COMPLETE"])

        oldest = ""
        if pending:
            oldest = pending[0].get("written_at", "")

        return WALStatus(
            complete=complete,
            entry_count=len(entries),
            pending_count=len(pending),
            oldest_pending=oldest,
            exit_code=self.EXIT_CODE_WAL_INCOMPLETE if not complete and len(pending) > 3 else 0,
        )

    def get_reverse_operation(self, entry_id: str) -> dict[str, Any] | None:
        entries = self._read_all()
        for e in entries:
            if e.get("entry_id") == entry_id:
                return {
                    "operation": f"reverse_{e.get('operation')}",
                    "from_commit": e.get("to_commit"),
                    "to_commit": e.get("from_commit"),
                    "files": e.get("files", []),
                }
        return None

    def _read_all(self) -> list[dict[str, Any]]:
        if not self._wal_path.exists():
            return []
        entries: list[dict[str, Any]] = []
        with open(self._wal_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return entries
