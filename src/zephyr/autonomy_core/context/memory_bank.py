# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.memory_bank
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
memory_bank.py — AI 读写结构化持久上下文 (DD: memory_bank, TASK-014 beta c)
==========================================================================
6 个结构化 .md 文件, AI 可读写, 作为跨 session 的持久上下文存储。
"""

from __future__ import annotations

from typing import Final
from datetime import UTC, timezone, datetime
from pathlib import Path

UTC: Final[timezone] = UTC

BANK_FILES: Final[list] = [
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
        bank.write_section("decision_log", " "Approved: use ONNX int8")
        decisions = bank.read_file("decision_log")
    """

    def __init__(self, root_dir: str | Path = ".ce_memory") -> None:
        self._root = Path(root_dir)
        self._root.mkdir(parents=True, exist_ok=True)
        for fname in BANK_FILES:
            fp = self._root / fname
            if not fp.exists():
                fp.write_text(f"# {fname.replace('.md', '').replace('_', ' ').title()}\n\n", encoding="utf-8")

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
            raise ValueError(f"Invalid bank file. Must be one of {BANK_FILES}")

    @property
    def root_dir(self) -> Path:
        return self._root


def _resolve_filename(filename: str) -> str:
    return filename if filename.endswith(".md") else f"{filename}.md"
