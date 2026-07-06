# [BLUEPRINT]
# [MODULE] zephyr.security.access_control.orphan_judge.safety_fence
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_safety_fence | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import re
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

_BLOCKED_STABILITY = {"frozen"}
_BLOCKED_AUTONOMY = {"immutable_core"}
_HEADER_PATTERN_STABILITY = re.compile(r"\[STABILITY\]\s*(\S+)")
_HEADER_PATTERN_AUTONOMY = re.compile(r"\[AI_AUTONOMY\]\s*(\S+)")


class SafetyCheckResult(BaseModel):
    allowed: bool
    reason: str = ""
    blocked_by: list[str] = Field(default_factory=list)


class SafetyFenceError(Exception):
    error_code = "ZA-SC-0034"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class SafetyFence:
    """安全围栏——阻止删除 frozen/immutable_core 文件。

    解析文件头部的 [STABILITY] 和 [AI_AUTONOMY] 标签，
    frozen 或 immutable_core 的文件禁止删除。
    """

    def __init__(self, project_root: str | Path | None = None) -> None:
        if project_root is None:
            self._root = Path.cwd()
        else:
            self._root = Path(project_root).resolve()
        self._cache: dict[str, tuple[str | None, str | None]] = {}

    def is_deletion_allowed(self, path: str | Path) -> bool:
        result = self.check_safety(path, "delete")
        return result.allowed

    def check_safety(self, path: str | Path, action: str = "delete") -> SafetyCheckResult:
        resolved = self._resolve_path(path)
        if not resolved.exists():
            return SafetyCheckResult(
                allowed=False,
                reason=f"File not found: {resolved}",
                blocked_by=["file_not_found"],
            )

        stability, autonomy = self._parse_headers(resolved)
        blockers: list[str] = []

        if action == "delete":
            if stability and stability in _BLOCKED_STABILITY:
                blockers.append(f"STABILITY={stability}")
            if autonomy and autonomy in _BLOCKED_AUTONOMY:
                blockers.append(f"AI_AUTONOMY={autonomy}")

        if blockers:
            reason = f"Deletion blocked by: {', '.join(blockers)}"
            logger.warning("Safety fence blocked %s on %s: %s", action, resolved, reason)
            return SafetyCheckResult(allowed=False, reason=reason, blocked_by=blockers)

        return SafetyCheckResult(allowed=True, reason="", blocked_by=[])

    def _resolve_path(self, path: str | Path) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p.resolve()
        return (self._root / p).resolve()

    def _parse_headers(self, resolved: Path) -> tuple[str | None, str | None]:
        cache_key = str(resolved)
        if cache_key in self._cache:
            return self._cache[cache_key]

        stability: str | None = None
        autonomy: str | None = None

        try:
            content = resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            logger.warning("Cannot read file headers from %s: %s", resolved, exc)
            self._cache[cache_key] = (None, None)
            return (None, None)

        header_section = self._extract_header_section(content)

        stab_match = _HEADER_PATTERN_STABILITY.search(header_section)
        if stab_match:
            stability = stab_match.group(1)

        auto_match = _HEADER_PATTERN_AUTONOMY.search(header_section)
        if auto_match:
            autonomy = auto_match.group(1)

        self._cache[cache_key] = (stability, autonomy)
        return (stability, autonomy)

    def _extract_header_section(self, content: str) -> str:
        end = len(content)
        triple_quote_pos = content.find('"""')
        if triple_quote_pos >= 0:
            second_quote = content.find('"""', triple_quote_pos + 3)
            if second_quote >= 0:
                end = second_quote
            else:
                end = len(content)
        return content[:end]

    def clear_cache(self) -> None:
        self._cache.clear()
