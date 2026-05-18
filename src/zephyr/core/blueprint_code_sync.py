# [BLUEPRINT] MOD-INF-002 | 03_modules/l01_infrastructure/runtime-integration/blueprint.md | §

# [MODULE] zephyr.core.blueprint_code_sync

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Blueprint-Code Sync — 蓝图-代码索引同步验证。

依据：
    蓝图 MOD-INF-006 §6.4.2 + v0.6.0
    任务卡 TASK-INF-0111 (Part 2/2)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class SyncEntry:
    blueprint_path: str
    code_path: str
    status: str
    last_synced: str = ""


@dataclass
class SyncReport:
    total_entries: int
    synced: int
    missing: int
    stale: int
    entries: list[SyncEntry]
    timestamp_utc: str


class BlueprintCodeSync:

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._registry_path = self._project_root / "docs" / "03_modules" / "blueprint-registry.yaml"

    def verify_sync(self) -> SyncReport:
        entries = self._collect_entries()

        synced = 0
        missing = 0
        stale = 0

        for entry in entries:
            code_full = self._project_root / entry.code_path
            blueprint_full = self._project_root / entry.blueprint_path

            if not code_full.exists():
                entry.status = "MISSING"
                missing += 1
            elif not blueprint_full.exists():
                entry.status = "STALE"
                stale += 1
            else:
                entry.status = "SYNCED"
                synced += 1

        return SyncReport(
            total_entries=len(entries),
            synced=synced,
            missing=missing,
            stale=stale,
            entries=entries,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
        )

    def validate_task_card(self, task_card: dict[str, Any]) -> tuple[bool, str]:
        downstream = task_card.get("downstream_outputs", [])
        for output in downstream:
            path_str = output.get("path", "")
            if not (self._project_root / path_str).exists():
                return False, f"Blueprint-code sync failed: {path_str} not found"

        return True, "Blueprint-code sync verified"

    def _collect_entries(self) -> list[SyncEntry]:
        entries: list[SyncEntry] = []

        task_dir = self._project_root / "docs" / "03_modules" / "l01_infrastructure" / "task-system"
        changes_dir = task_dir / "changes" / "MOD-INF-006"

        if not changes_dir.exists():
            return entries

        for card_file in sorted(changes_dir.glob("TASK-INF-*.md")):
            task_id = card_file.stem
            entries.append(SyncEntry(
                blueprint_path=str(card_file.relative_to(self._project_root)),
                code_path=f"src/zephyr/core/",
                status="PENDING",
                last_synced="",
            ))

        return entries
