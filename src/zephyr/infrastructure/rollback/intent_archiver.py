# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.intent_archiver
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
# [A_module] module_id=MOD-INF_intent_archiver | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
IntentArchiver — 意图存档保护。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B129 + exit code 46

回滚前保存原始操作意图 (why was this done?) 的不可变记录。
意图存档不可被 GC 清理 → 若检测到清理意图存档 → exit 46 (INTENT_ARCHIVE_PRUNE)。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class IntentRecord:
    intent_id: str
    operation_id: str
    intent_text: str
    author: str
    archived_at: str
    content_hash: str


@dataclass
class IntentArchiveStatus:
    total_entries: int
    integrity_pass: bool
    pruned_count: int
    exit_code: int


class IntentArchiver:
    EXIT_CODE_INTENT_PRUNE: int = 46
    ARCHIVE_DIR: str = ".zephyr/intent_archive"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._archive_dir = self._project_root / self.ARCHIVE_DIR
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._archive_dir / "manifest.jsonl"

    def archive(self, operation_id: str, intent_text: str, author: str = "") -> IntentRecord:
        now = datetime.now(UTC)
        intent_id = f"INTENT-{now.strftime('%Y%m%d-%H%M%S-%f')}"

        content_hash = hashlib.sha256(intent_text.encode()).hexdigest()

        record = IntentRecord(
            intent_id=intent_id,
            operation_id=operation_id,
            intent_text=intent_text,
            author=author,
            archived_at=now.isoformat(),
            content_hash=content_hash,
        )

        intent_file = self._archive_dir / f"{intent_id}.txt"
        intent_file.write_text(
            f"# Intent Archive\n"
            f"intent_id: {intent_id}\n"
            f"operation_id: {operation_id}\n"
            f"author: {author}\n"
            f"archived_at: {now.isoformat()}\n"
            f"content_hash: {content_hash}\n"
            f"---\n"
            f"{intent_text}\n",
            encoding="utf-8",
        )

        with open(self._manifest_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "intent_id": record.intent_id,
                        "operation_id": record.operation_id,
                        "author": record.author,
                        "archived_at": record.archived_at,
                        "content_hash": record.content_hash,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            f.flush()

        return record

    def verify_integrity(self) -> IntentArchiveStatus:
        if not self._manifest_path.exists():
            return IntentArchiveStatus(total_entries=0, integrity_pass=True, pruned_count=0, exit_code=0)

        total_entries = 0
        pruned_count = 0
        missing_files = 0

        try:
            with open(self._manifest_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        intent_id = entry.get("intent_id", "")
                        intent_file = self._archive_dir / f"{intent_id}.txt"
                        total_entries += 1
                        if not intent_file.exists():
                            missing_files += 1
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass

        integrity_pass = missing_files == 0
        exit_code = self.EXIT_CODE_INTENT_PRUNE if not integrity_pass else 0

        return IntentArchiveStatus(
            total_entries=total_entries,
            integrity_pass=integrity_pass,
            pruned_count=missing_files,
            exit_code=exit_code,
        )

    def get_intent(self, operation_id: str) -> str | None:
        if not self._manifest_path.exists():
            return None

        try:
            with open(self._manifest_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("operation_id") == operation_id:
                            intent_id = entry.get("intent_id", "")
                            intent_file = self._archive_dir / f"{intent_id}.txt"
                            if intent_file.exists():
                                content = intent_file.read_text(encoding="utf-8")
                                parts = content.split("---\n", 1)
                                return parts[1].strip() if len(parts) > 1 else content
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        return None
