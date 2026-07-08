# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.instruction_bloat_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-RES_instruction_bloat_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""InstructionBloatDetector — 指令膨胀检测
=============================================
蓝图 §2.18 · 检测 AGENTS.md/system_prompt 等指令文件膨胀

三级告警
--------
  oversized   -> instruction_token_count > session_budget × 0.25
  growing     -> growth_rate_weekly > 20%
  dominance   -> per_turn_instruction_overhead > productive_tokens
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

_DEFAULT_TARGETS = [
    "AGENTS.md",
    "CLAUDE.md",
    ".trae/rules/project_rules.md",
    "config/budget_policy.yaml",
]

_DEFAULT_BLUEPRINT_PATTERNS = [
    "docs/03_modules/**/blueprint.md",
]


class BloatLevel(Enum):
    NORMAL = auto()
    OVERSIZED = auto()
    GROWING = auto()
    DOMINANCE = auto()


@dataclass
class InstructionMetrics:
    target_path: str
    token_count: int = 0
    byte_count: int = 0
    growth_rate_weekly: float = 0.0
    per_turn_overhead: float = 0.0
    level: BloatLevel = BloatLevel.NORMAL
    message: str = ""
    last_measured: float = field(default_factory=time.time)


@dataclass
class BloatAlert:
    target_path: str
    level: BloatLevel
    message: str
    token_count: int = 0
    estimated_savings: int = 0


@dataclass
class CompactSuggestion:
    target_path: str
    current_tokens: int
    suggestion: str
    unused_sections: list[str] = field(default_factory=list)
    estimated_savings: int = 0


class InstructionBloatDetector:
    def __init__(
        self,
        targets: list[str] | None = None,
        session_budget: float = 1_000_000.0,
        history_path: str = "data/budget-enforcer/instruction_bloat_history.json",
    ) -> None:
        self._targets = targets or _DEFAULT_TARGETS
        self._session_budget = session_budget
        self._history_path = Path(history_path)
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: dict[str, list[dict[str, Any]]] = self._load_history()
        self._lock = threading.Lock()

    def scan(self, project_root: str = ".") -> list[InstructionMetrics]:
        root = Path(project_root)
        results: list[InstructionMetrics] = []
        with self._lock:
            for target in self._targets:
                target_path = root / target
                metrics = self._measure_target(target, target_path)
                results.append(metrics)
            for bp_pattern in _DEFAULT_BLUEPRINT_PATTERNS:
                for bp_path in root.glob(bp_pattern):
                    metrics = self._measure_target(bp_path.name, bp_path, is_blueprint=True)
                    results.append(metrics)
        return results

    def _measure_target(self, name: str, path: Path, is_blueprint: bool = False) -> InstructionMetrics:
        if not path.exists():
            return InstructionMetrics(target_path=name, level=BloatLevel.NORMAL, message="file not found")

        content = path.read_text(encoding="utf-8", errors="replace")
        if is_blueprint:
            lines = content.split("\n")
            section_end = 0
            for i, line in enumerate(lines):
                if line.startswith("## ") and section_end > 0:
                    break
                if line.startswith("## "):
                    section_end = i
            if section_end > 0:
                content = "\n".join(lines[:section_end])

        token_count = len(content) // 4
        byte_count = len(content.encode("utf-8"))
        growth_rate = self._compute_growth_rate(name, token_count)
        per_turn_overhead = token_count / max(self._session_budget, 1.0)

        level = BloatLevel.NORMAL
        message = ""

        if token_count > self._session_budget * 0.25:
            level = BloatLevel.OVERSIZED
            message = f"指令过大 — {token_count} tokens 占预算 {per_turn_overhead:.1%}"
        elif growth_rate > 0.20:
            level = BloatLevel.GROWING
            message = f"指令膨胀 — 周增长率 {growth_rate:.1%}"
        elif per_turn_overhead > 0.5:
            level = BloatLevel.DOMINANCE
            message = f"指令主导 — 每轮 {token_count} tokens 超过产出 tokens"

        self._record_measurement(name, token_count, byte_count)

        return InstructionMetrics(
            target_path=name,
            token_count=token_count,
            byte_count=byte_count,
            growth_rate_weekly=growth_rate,
            per_turn_overhead=per_turn_overhead,
            level=level,
            message=message,
        )

    def _compute_growth_rate(self, name: str, current_tokens: int) -> float:
        records = self._history.get(name, [])
        if len(records) < 2:
            return 0.0
        week_ago = time.time() - 7 * 86400
        old_records = [r for r in records if r.get("timestamp", 0) < week_ago]
        if not old_records:
            recent = records[0]
            return (current_tokens - recent.get("token_count", current_tokens)) / max(recent.get("token_count", 1), 1)
        baseline = old_records[-1].get("token_count", current_tokens)
        return (current_tokens - baseline) / max(baseline, 1)

    def _record_measurement(self, name: str, token_count: int, byte_count: int) -> None:
        if name not in self._history:
            self._history[name] = []
        self._history[name].append(
            {
                "timestamp": time.time(),
                "token_count": token_count,
                "byte_count": byte_count,
            }
        )
        if len(self._history[name]) > 100:
            self._history[name] = self._history[name][-50:]
        self._save_history()

    def suggest_compact(self, project_root: str = ".") -> list[CompactSuggestion]:
        root = Path(project_root)
        suggestions: list[CompactSuggestion] = []
        for target in self._targets:
            target_path = root / target
            if not target_path.exists():
                continue
            content = target_path.read_text(encoding="utf-8", errors="replace")
            lines = content.split("\n")
            unused: list[str] = []
            current_tokens = len(content) // 4
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("# ") or stripped.startswith("## "):
                    section_header = stripped
                    section_lines = 0
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip().startswith("# ") or lines[j].strip().startswith("## "):
                            break
                        section_lines += 1
                    if section_lines > 20:
                        unused.append(f"{section_header} ({section_lines} lines)")
            if unused:
                savings = current_tokens // 4
                suggestions.append(
                    CompactSuggestion(
                        target_path=target,
                        current_tokens=current_tokens,
                        suggestion=f"检测到 {len(unused)} 个大段落，建议审查是否仍在使用",
                        unused_sections=unused,
                        estimated_savings=savings,
                    )
                )
        return suggestions

    def _load_history(self) -> dict[str, list[dict[str, Any]]]:
        if self._history_path.exists():
            try:
                return json.loads(self._history_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_history(self) -> None:
        tmp_path = f"{self._history_path}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, str(self._history_path))
        except (PermissionError, OSError):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def summary(self) -> dict[str, Any]:
        return {
            "targets_monitored": len(self._targets),
            "history_entries": sum(len(v) for v in self._history.values()),
            "session_budget": self._session_budget,
        }


__all__ = [
    "BloatLevel",
    "CompactSuggestion",
    "InstructionBloatDetector",
    "InstructionMetrics",
]
