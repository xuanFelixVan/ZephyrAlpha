# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.vibe_coding_guard

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Vibe Coding攻击面——检测AI辅助生成代码中隐藏的权限后门/注入/逻辑绕过."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VibeCodingAudit(BaseModel):
    file_path: str
    lines_total: int = 0
    ai_generated_lines: int = 0
    detected: list[str] = Field(default_factory=list)
    risk_score: float = 0.0


VIBE_CODING_PATTERNS = [
    "# TODO: remove this bypass",
    "if debug_mode",
    "# bypass permission check",
    "allow_all = True",
    "check_permission = lambda _: True",
    "is_admin = True  # for testing",
    "override = True",
    "# HACK:",
    "# FIXME: remove before deploy",
]


class VibeCodingGuard:
    def scan(self, file_path: str, content: str) -> VibeCodingAudit:
        lines = content.splitlines()
        detected = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for pattern in VIBE_CODING_PATTERNS:
                if pattern.lower() in line_lower:
                    detected.append(f"L{i+1}: {pattern}")
                    break

        risk = min(100.0, len(detected) * 15.0 + (0 if len(detected) < 3 else 25.0))

        return VibeCodingAudit(
            file_path=file_path,
            lines_total=len(lines),
            ai_generated_lines=len([l for l in lines if l.strip().startswith("#")]),
            detected=detected,
            risk_score=risk,
        )
