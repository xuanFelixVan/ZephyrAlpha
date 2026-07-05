# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.api.dos_launcher
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-SHR_dos_launcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Self

"""
DOSLauncher: load and execute DOS directive files
==================================================
Task ID : T-2-27 (C53)
safety_level : L
Depends : none

Loads DOS directive files from the directives directory and supports
directive chain composition (e.g. "325+344+999").

Directive 源文件位于 `resources/DOS/directives/`。
运行时可通过环境变量 `ZEPHYR_DOS_DIRECTIVE_DIR` 显式覆盖。

Each directive file has a frontmatter with:
  - directive_id: numeric string (e.g. "325")
  - domain: D0-D9
  - title: descriptive name
  - safety_level: L/M/H

Output: DOSResult with directives_loaded, execution_log, compliance.
"""


import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.io.paths import REPO_ROOT

__all__ = [
    "DOSLauncher",
    "DOSResult",
    "DirectiveInfo",
]


# ---------------------------------------------------------------------------
# 默认 directive 目录解析
# ---------------------------------------------------------------------------
# 解析优先级：
#   1. 环境变量 ZEPHYR_DOS_DIRECTIVE_DIR（显式配置，优先）
#   2. resources/DOS/directives（项目内约定路径）
# ---------------------------------------------------------------------------
def _resolve_default_directive_dir() -> Path:
    env = os.environ.get("ZEPHYR_DOS_DIRECTIVE_DIR")
    if env:
        return Path(env).expanduser().resolve()

    project_root = REPO_ROOT
    in_tree = project_root / "resources" / "DOS" / "directives"
    return in_tree


_DIRECTIVE_DIR = _resolve_default_directive_dir()

_CHAIN_SEPARATOR = "+"

_FM_OPEN = re.compile(r"^---\s*$")
_FM_CLOSE = re.compile(r"^---\s*$")
_FM_FIELD = re.compile(r"^(\w+)\s*:\s*(.+)$")


class DirectiveInfo(BaseModel):
    model_config = BASE_CONFIG

    directive_id: str = Field(min_length=1)
    title: str = Field(default="")
    domain: str = Field(default="")
    safety_level: str = Field(default="L")
    file_path: str = Field(default="")
    content: str = Field(default="")


class DOSResult(BaseModel):
    model_config = BASE_CONFIG

    directives_loaded: list[str] = Field(default_factory=list)
    execution_log: str = Field(default="")
    compliance: bool = Field(default=True)
    chain: str = Field(default="")
    errors: list[str] = Field(default_factory=list)


def _parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or not _FM_OPEN.match(lines[0]):
        return {}
    result: dict[str, str] = {}
    in_fm = False
    for i, line in enumerate(lines):
        if i == 0:
            in_fm = True
            continue
        if _FM_CLOSE.match(line):
            break
        if in_fm:
            m = _FM_FIELD.match(line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip().strip("'\"")
                result[key] = val
    return result


def _parse_body(text: str) -> str:
    lines = text.splitlines()
    if not lines or not _FM_OPEN.match(lines[0]):
        return text
    found_close = False
    body_start = 0
    for i, line in enumerate(lines):
        if i > 0 and _FM_CLOSE.match(line):
            found_close = True
            body_start = i + 1
            break
    if not found_close:
        return ""
    return "\n".join(lines[body_start:]).strip()


class DOSLauncher:
    """Load and execute DOS directive files.

    Parameters
    ----------
    directive_dir : Path | None
        Directory containing directive .md files.
        Defaults to :data:`_DIRECTIVE_DIR`（由 :func:`_resolve_default_directive_dir` 计算）。
    """

    def __init__(
        self,
        directive_dir: Path | None = None,
    ) -> None:
        self._directive_dir = directive_dir or _DIRECTIVE_DIR
        self._cache: dict[str, DirectiveInfo] = {}

    def load_directive(self, directive_id: str) -> DirectiveInfo | None:
        if directive_id in self._cache:
            return self._cache[directive_id]

        if not self._directive_dir.exists():
            return None

        for md_file in self._directive_dir.rglob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = _parse_frontmatter(text)
            if fm.get("directive_id") == directive_id:
                body = _parse_body(text)
                info = DirectiveInfo(
                    directive_id=directive_id,
                    title=fm.get("title", ""),
                    domain=fm.get("domain", ""),
                    safety_level=fm.get("safety_level", "L"),
                    file_path=str(md_file),
                    content=body,
                )
                self._cache[directive_id] = info
                return info

        return None

    def load_chain(self, chain: str) -> DOSResult:
        directive_ids = [d.strip() for d in chain.split(_CHAIN_SEPARATOR) if d.strip()]

        if not directive_ids:
            return DOSResult(
                directives_loaded=[],
                execution_log="Empty chain",
                compliance=False,
                chain=chain,
                errors=["No directive IDs in chain"],
            )

        loaded: list[str] = []
        log_parts: list[str] = []
        errors: list[str] = []
        all_compliant = True

        for did in directive_ids:
            info = self.load_directive(did)
            if info is None:
                errors.append(f"Directive {did} not found")
                log_parts.append(f"[MISS] {did}: not found")
                all_compliant = False
            else:
                loaded.append(did)
                log_parts.append(f"[OK] {did}: {info.title} (domain={info.domain})")

        execution_log = "\n".join(log_parts)

        return DOSResult(
            directives_loaded=loaded,
            execution_log=execution_log,
            compliance=all_compliant,
            chain=chain,
            errors=errors,
        )

    def list_available_directives(self) -> list[DirectiveInfo]:
        if not self._directive_dir.exists():
            return []

        results: list[DirectiveInfo] = []
        for md_file in sorted(self._directive_dir.rglob("*.md")):
            try:
                text = md_file.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = _parse_frontmatter(text)
            did = fm.get("directive_id", "")
            if did:
                body = _parse_body(text)
                results.append(
                    DirectiveInfo(
                        directive_id=did,
                        title=fm.get("title", ""),
                        domain=fm.get("domain", ""),
                        safety_level=fm.get("safety_level", "L"),
                        file_path=str(md_file),
                        content=body,
                    )
                )
        return results

    @property
    def directive_dir(self) -> Path:
        return self._directive_dir

    def clear_cache(self) -> None:
        self._cache.clear()
