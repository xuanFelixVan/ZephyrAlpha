# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §vibe_coding_guard
# [MODULE] zephyr.security.access_control.guards.vibe_coding_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_vibe_coding.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] clean code never flagged; dangerous patterns always detected
# [MODIFY-GUARD] blueprint.md §vibe_coding_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] scan never raises; returns VibeCodingAudit
# [TESTS] tests/agent_rbac/test_vibe_coding.py
# [A_module] module_id=MOD-SEC_vibe_coding_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""VibeCodingGuard — Vibe Coding 攻击面检测.

依据蓝图 MOD-INF-018 §vibe_coding_guard:
- 检测代码中的危险模式（HACK/FIXME/bypass/allow_all 等）
- 检测权限绕过模式
- 评估风险分数
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


VIBE_CODING_PATTERNS: list[dict[str, str]] = [
    {"name": "HACK_COMMENT", "pattern": r"#\s*HACK", "risk": "0.5"},
    {"name": "FIXME_BYPASS", "pattern": r"#\s*FIXME.*bypass", "risk": "0.5"},
    {"name": "ALLOW_ALL", "pattern": r"allow_all\s*=\s*True", "risk": "0.8"},
    {"name": "DISABLE_SECURITY", "pattern": r"disable_security|security\s*=\s*False", "risk": "0.8"},
    {"name": "BYPASS_AUTH", "pattern": r"bypass_auth|skip_auth|no_auth", "risk": "0.8"},
    {"name": "EVAL_EXEC", "pattern": r"\beval\s*\(|\bexec\s*\(", "risk": "0.6"},
    {"name": "SUBPROCESS_SHELL", "pattern": r"subprocess.*shell\s*=\s*True", "risk": "0.7"},
    {"name": "OS_SYSTEM", "pattern": r"os\.system\s*\(", "risk": "0.7"},
    {"name": "PICKLE_LOAD", "pattern": r"pickle\.loads?\s*\(", "risk": "0.6"},
    {"name": "YAML_UNSAFE", "pattern": r"yaml\.load\s*\([^)]*\)\s*$", "risk": "0.5"},
]


@dataclass
class VibeCodingAudit:
    """Vibe Coding 审计结果.

    Attributes:
        detected: 检测到的模式列表（每项为 dict 含 name/risk）
        risk_score: 风险分数
        filename: 文件名
    """

    detected: list[dict[str, str]] = field(default_factory=list)
    risk_score: float = 0.0
    filename: str = ""


class VibeCodingGuard:
    """Vibe Coding 攻击面检测器."""

    def __init__(self) -> None:
        self._patterns = [
            {**p, "compiled": re.compile(p["pattern"], re.IGNORECASE)}
            for p in VIBE_CODING_PATTERNS
        ]

    def scan(self, filename: str, content: str) -> VibeCodingAudit:
        """扫描文件内容检测 Vibe Coding 危险模式.

        Args:
            filename: 文件名
            content: 文件内容

        Returns:
            VibeCodingAudit 包含检测结果和风险分数
        """
        detected: list[dict[str, str]] = []
        risk_score = 0.0

        for p in self._patterns:
            if p["compiled"].search(content):
                detected.append({"name": p["name"], "risk": p["risk"]})
                risk_score += float(p["risk"])

        return VibeCodingAudit(
            detected=detected,
            risk_score=risk_score,
            filename=filename,
        )


__all__ = [
    "VIBE_CODING_PATTERNS",
    "VibeCodingAudit",
    "VibeCodingGuard",
]
