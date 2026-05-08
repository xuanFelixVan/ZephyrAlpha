"""
KE Structurer — 知识条目结构化提取。

依据：
    蓝图 MOD-INF-006 §6.12.1 + v0.6.0
    任务卡 TASK-INF-0120
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class KEType(str, Enum):
    INSIGHT = "insight"
    PROCEDURE = "procedure"
    PATTERN = "pattern"
    FAILURE = "failure"
    HEURISTIC = "heuristic"


@dataclass
class KnowledgeEntry:
    ke_id: str
    task_id: str
    ke_type: KEType
    content_snippet: str
    source_file: str
    priority: str
    created_at: str
    tags: list[str] = field(default_factory=list)


@dataclass
class KeStructuredOutput:
    entries: list[KnowledgeEntry]
    total: int
    by_type: dict[str, int]
    timestamp_utc: str


class KEStructurer:

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/knowledge")
        self._entries_path = self._data_dir / "ke_entries.jsonl"

    def structure_task_ke(self, task_card: dict[str, Any]) -> list[KnowledgeEntry]:
        entries: list[KnowledgeEntry] = []
        task_id = task_card.get("task_id", "")

        existing_kes = task_card.get("ke_entries", [])
        if existing_kes:
            for ke_data in existing_kes:
                entries.append(KnowledgeEntry(
                    ke_id=ke_data.get("ke_id", f"KE-{task_id}-{len(entries) + 1}"),
                    task_id=task_id,
                    ke_type=KEType(ke_data.get("ke_type", "insight")),
                    content_snippet=ke_data.get("content_snippet", ""),
                    source_file=ke_data.get("source_file", ""),
                    priority=ke_data.get("priority", "P2"),
                    created_at=datetime.now(timezone.utc).isoformat(),
                    tags=ke_data.get("tags", []),
                ))
            return entries

        if task_card.get("description"):
            entries.append(KnowledgeEntry(
                ke_id=f"KE-{task_id}-001",
                task_id=task_id,
                ke_type=KEType.INSIGHT,
                content_snippet=task_card["description"][:500],
                source_file="task_card.md",
                priority=task_card.get("priority", "P2"),
                created_at=datetime.now(timezone.utc).isoformat(),
                tags=["task_description"],
            ))

        return entries

    def save_entries(self, entries: list[KnowledgeEntry]) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)

        for entry in entries:
            ke_line = json.dumps({
                "ke_id": entry.ke_id,
                "task_id": entry.task_id,
                "ke_type": entry.ke_type.value,
                "content_snippet": entry.content_snippet,
                "source_file": entry.source_file,
                "priority": entry.priority,
                "created_at": entry.created_at,
                "tags": entry.tags,
            }, ensure_ascii=False)

            with open(self._entries_path, "a", encoding="utf-8") as f:
                f.write(ke_line + "\n")

    def get_by_type(self, ke_type: KEType) -> list[KnowledgeEntry]:
        entries: list[KnowledgeEntry] = []
        if not self._entries_path.exists():
            return entries

        try:
            for line in self._entries_path.read_text(encoding="utf-8").strip().split("\n"):
                if not line:
                    continue
                data = json.loads(line)
                if data.get("ke_type") == ke_type.value:
                    entries.append(KnowledgeEntry(
                        ke_id=data["ke_id"],
                        task_id=data["task_id"],
                        ke_type=KEType(data["ke_type"]),
                        content_snippet=data.get("content_snippet", ""),
                        source_file=data.get("source_file", ""),
                        priority=data.get("priority", "P2"),
                        created_at=data.get("created_at", ""),
                        tags=data.get("tags", []),
                    ))
        except (json.JSONDecodeError, KeyError):
            pass

        return entries
