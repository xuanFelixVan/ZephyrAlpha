# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.memory_bank

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
memory_bank.py — AI 读写结构化持久上下文 (DD: memory_bank, TASK-014 beta c)
==========================================================================
6 个结构化 .md 文件, AI 可读写, 作为跨 session 的持久上下文存储。
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc

BANK_FILES = [
    "project_brief.md",
    "product_context.md",
    "system_patterns.md",
    "active_context.md",
    "progress_tracker.md",
    "decision_log.md",
]


class MemoryBank:
    """AI 读写 6 类结构化持久上下文 (DD: memory_bank)。

    Using::

        bank = MemoryBank(root_dir=".memory")
        bank.write_section("decision_log", "ADR-0023", "Approved: use ONNX int8")
        decisions = bank.read_file("decision_log")
    """

    def __init__(self, root_dir: str | Path = ".ce_memory") -> None:
        self._root = Path(root_dir)
        self._root.mkdir(parents=True, exist_ok=True)
        for fname in BANK_FILES:
            fp = self._root / fname
            if not fp.exists():
                fp.write_text(f"# {fname.replace('.md','').replace('_',' ').title()}\n\n", encoding="utf-8")

    def read_file(self, filename: str) -> str:
        self._validate_filename(filename)
        return (self._root / _resolve_filename(filename)).read_text(encoding="utf-8")

    def write_section(self, filename: str, heading: str, content: str) -> None:
        self._validate_filename(filename)
        fp = self._root / _resolve_filename(filename)
        existing = fp.read_text(encoding="utf-8") if fp.exists() else ""
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        entry = f"\n## {heading}\n\n> Updated: {timestamp}\n\n{content}\n"
        fp.write_text(existing + entry, encoding="utf-8")

    def list_all(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for fname in BANK_FILES:
            fp = self._root / fname
            if fp.exists():
                key = fname.replace(".md", "")
                result[key] = fp.stat().st_size
        return result

    def export_json(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for fname in BANK_FILES:
            fp = self._root / fname
            if fp.exists():
                key = fname.replace(".md", "")
                result[key] = fp.read_text(encoding="utf-8")
        return result

    @staticmethod
    def _validate_filename(filename: str) -> None:
        basename = filename if filename.endswith(".md") else f"{filename}.md"
        if basename not in BANK_FILES:
            raise ValueError(f"Invalid bank file: {filename}. Must be one of {BANK_FILES}")

    @property
    def root_dir(self) -> Path:
        return self._root


def _resolve_filename(filename: str) -> str:
    return filename if filename.endswith(".md") else f"{filename}.md"
