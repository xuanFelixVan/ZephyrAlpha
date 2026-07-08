# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.dream_cycle
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_dream_cycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DreamCycle — 知识固化引擎
==========================
蓝图: ARC-0001 §4.2 (三阶)
借鉴: Claude Code Dream Cycle + Tulving 记忆分类
归档->提取->遗忘->索引->commit
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)


class DreamReport(BaseModel):
    model_config = BASE_CONFIG
    archived_files: int = 0
    extracted_patterns: int = 0
    forgotten_items: int = 0
    indexed_entries: int = 0
    committed: bool = False
    timestamp: str = Field(default_factory=lambda: now_utc().isoformat())


class DreamCycle:
    """知识固化引擎——从情节记忆到语义记忆的转化。

    借鉴:
      - Claude Code Dream Cycle: 归档->提取->遗忘->索引->commit
      - Tulving 记忆分类: episodic vs semantic
    """

    def __init__(self, archive_dir: Path, audit_log_dir: Path | None = None) -> None:
        self._archive_dir = Path(archive_dir)
        self._audit_log_dir = audit_log_dir
        self._episodic_dir = self._archive_dir / "episodic"
        self._semantic_dir = self._archive_dir / "semantic"
        self._forgotten_log = self._archive_dir / "forgotten.log"

    def trigger_archival(self) -> DreamReport:
        report = DreamReport()

        self._episodic_dir.mkdir(parents=True, exist_ok=True)
        self._semantic_dir.mkdir(parents=True, exist_ok=True)

        if self._audit_log_dir and self._audit_log_dir.exists():
            report.archived_files = self._archive_audit_logs()

        report.extracted_patterns = self._extract_patterns()
        report.forgotten_items = self._forget()
        report.indexed_entries = self._index_semantic()
        report.committed = False

        return report

    def needs_archival(self) -> bool:
        if self._audit_log_dir and self._audit_log_dir.exists():
            today = now_utc().strftime("%Y-%m-%d")
            today_file = self._audit_log_dir / f"ai_audit_{today}.jsonl"
            if today_file.exists():
                episodic_today = self._episodic_dir / today
                if not episodic_today.exists():
                    return True
        return False

    def query_episodic(self, date_str: str) -> list[dict[str, Any]]:
        path = self._episodic_dir / date_str
        if not path.exists():
            return []
        results: list[dict[str, Any]] = []
        for f in path.glob("*.jsonl"):
            # 5.169 修复：用 context manager 防止文件句柄泄漏
            with f.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return results

    def query_semantic(self, tags: list[str]) -> list[dict[str, Any]]:
        index_file = self._semantic_dir / "index.json"
        if not index_file.exists():
            return []
        try:
            data = json.loads(index_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("query_semantic: failed to load semantic index (%s: %s)", type(e).__name__, e)
            return []
        tag_set = set(t.lower() for t in tags)
        return [e for e in data if tag_set & set(t.lower() for t in e.get("tags", []))]

    def _archive_audit_logs(self) -> int:
        if not self._audit_log_dir or not self._audit_log_dir.exists():
            return 0
        count = 0
        today = now_utc().strftime("%Y-%m-%d")
        target = self._episodic_dir / today
        target.mkdir(parents=True, exist_ok=True)
        for f in self._audit_log_dir.glob("ai_audit_*.jsonl"):
            date_part = f.stem.replace("ai_audit_", "")
            if date_part != today:
                dest = target / f.name
                shutil.copy2(f, dest)
                count += 1
        return count

    def _extract_patterns(self) -> int:
        return 0

    def _forget(self) -> int:
        self._forgotten_log.parent.mkdir(parents=True, exist_ok=True)
        if not self._forgotten_log.exists():
            self._forgotten_log.write_text(
                f"# Forgotten Log — {now_utc().isoformat()}\n# Retain lessons, forget noise.\n",
                encoding="utf-8",
            )
        return 0

    def _index_semantic(self) -> int:
        index_file = self._semantic_dir / "index.json"
        self._semantic_dir.mkdir(parents=True, exist_ok=True)
        if not index_file.exists():
            index_file.write_text("[]", encoding="utf-8")
        return 0
