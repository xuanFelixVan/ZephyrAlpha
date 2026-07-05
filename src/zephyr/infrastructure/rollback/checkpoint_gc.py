# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.checkpoint_gc
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_checkpoint_gc | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CheckpointGC — Checkpoint 垃圾回收。

依据: 蓝图 MOD-INF-021 §6.2 B50

快照保留策略:
    - max 100 个 JSONL dump 文件
    - max 90 天保留期
    - 保留最近 5 个 knowngoodstate 快照（不可清）

周期清理: 每周清理过期快照。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GCResult:
    total_before: int
    total_after: int
    deleted: list[str]
    preserved_known_good: list[str]
    skipped_size: int


class CheckpointGC:
    MAX_SNAPSHOTS: int = 100
    MAX_AGE_DAYS: int = 90
    PRESERVE_KNOWN_GOOD: int = 5
    DUMP_DIR: str = "data/rollback/db_snapshots"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._dump_dir = self._project_root / self.DUMP_DIR

    def collect(self) -> GCResult:
        if not self._dump_dir.exists():
            return GCResult(total_before=0, total_after=0, deleted=[], preserved_known_good=[], skipped_size=0)

        snapshots = sorted(self._dump_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        total_before = len(snapshots)

        known_good_commits = self._get_known_good_commits()
        preserved: set[str] = set(known_good_commits[-self.PRESERVE_KNOWN_GOOD :])

        now = datetime.now(UTC)
        to_delete: list[Path] = []

        for sp in snapshots:
            commit_sha = sp.stem

            if commit_sha in preserved:
                continue

            age_seconds = now.timestamp() - sp.stat().st_mtime
            age_days = age_seconds / 86400

            if age_days > self.MAX_AGE_DAYS or total_before - len(to_delete) > self.MAX_SNAPSHOTS:
                to_delete.append(sp)

        deleted: list[str] = []
        for sp in to_delete:
            try:
                sp.unlink()
                deleted.append(sp.name)
            except Exception as e:
                logger.warning("CheckpointGC.collect: snapshot unlink failed for %s (%s: %s)", sp.name, type(e).__name__, e, exc_info=True)

        total_after = total_before - len(deleted)
        return GCResult(
            total_before=total_before,
            total_after=total_after,
            deleted=deleted,
            preserved_known_good=sorted(preserved),
            skipped_size=total_before - total_after,
        )

    def _get_known_good_commits(self) -> list[str]:
        ledger_path = self._project_root / ".zephyr/knowngoodstate_ledger.jsonl"
        if not ledger_path.exists():
            return []

        commits: list[str] = []
        with open(ledger_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    commits.append(entry["commit_sha"])
                except (json.JSONDecodeError, KeyError):
                    continue

        return commits