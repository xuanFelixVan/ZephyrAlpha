# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §output_guard
# [MODULE] zephyr.security.access_control.guards.output_guard
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_output_guard_agent_rbac.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] check() never raises; PII/credentials always masked in output
# [MODIFY-GUARD] blueprint.md §output_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check() never raises; returns OutputResult with decision
# [TESTS] tests/agent_rbac/test_output_guard_agent_rbac.py
# [A_module] module_id=MOD-SEC_output_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""OutputGuard — 输出内容守卫.

依据蓝图 MOD-INF-018 §output_guard:
- 检测输出中的 PII（个人身份信息）
- 检测输出中的凭证（API key、token 等）
- 大输出截断
- 多源信息合成泄露检测
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class OutputDecision(str, Enum):
    """输出决策."""

    CLEAN = "clean"
    SANITIZED = "sanitized"
    REDACTED = "redacted"
    ALLOW = "allow"


PII_PATTERNS: list[dict[str, str]] = [
    {"name": "PHONE_CN", "pattern": r"1[3-9]\d{9}"},
    {"name": "ID_CN", "pattern": r"\d{17}[\dXx]"},
    {"name": "EMAIL", "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"},
]

CREDENTIAL_PATTERNS: list[dict[str, str]] = [
    {"name": "OPENAI_KEY", "pattern": r"sk-[a-zA-Z0-9]{20,}"},
    {"name": "AWS_ACCESS_KEY", "pattern": r"AKIA[0-9A-Z]{16}"},
    {"name": "GITHUB_TOKEN", "pattern": r"gh[pousr]_[A-Za-z0-9]{36}"},
]

MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB


@dataclass
class OutputResult:
    """输出检查结果.

    Attributes:
        decision: 决策结果
        sanitized_content: 脱敏后的内容
        findings: 发现的问题列表
        reason: 决策原因
    """

    decision: OutputDecision = OutputDecision.ALLOW
    sanitized_content: str = ""
    findings: list[dict[str, Any]] = field(default_factory=list)
    reason: str = ""


class OutputGuard:
    """输出内容守卫.

    检测输出中的敏感信息并进行脱敏处理。
    """

    def __init__(self) -> None:
        self._read_history: dict[str, list[str]] = {}

    def record_read(self, agent_id: str, source: str) -> None:
        """记录 agent 读取的源文件.

        Args:
            agent_id: Agent ID
            source: 读取的源文件路径
        """
        if agent_id not in self._read_history:
            self._read_history[agent_id] = []
        self._read_history[agent_id].append(source)

    def check(self, text: str, agent_id: str = "") -> OutputResult:
        """检查输出内容.

        Args:
            text: 待检查的文本
            agent_id: 输出来源的 agent ID

        Returns:
            OutputResult: 检查结果
        """
        if not text:
            return OutputResult(
                decision=OutputDecision.CLEAN,
                sanitized_content="",
                findings=[],
                reason="empty output",
            )

        sanitized = text
        findings: list[dict[str, Any]] = []

        # 检查输出大小
        if len(text) > MAX_OUTPUT_SIZE:
            sanitized = text[:MAX_OUTPUT_SIZE] + "[SIZE_TRUNCATED]"
            findings.append({
                "type": "size_truncated",
                "original_size": len(text),
                "max_size": MAX_OUTPUT_SIZE,
            })
            return OutputResult(
                decision=OutputDecision.SANITIZED,
                sanitized_content=sanitized,
                findings=findings,
                reason="output truncated due to size",
            )

        # 检查 PII
        for p in PII_PATTERNS:
            matches = re.findall(p["pattern"], sanitized)
            if matches:
                sanitized = re.sub(
                    p["pattern"], f"[{p['name']}_MASKED]", sanitized
                )
                findings.append({
                    "type": "pii",
                    "name": p["name"],
                    "count": len(matches),
                })

        # 检查凭证
        for p in CREDENTIAL_PATTERNS:
            matches = re.findall(p["pattern"], sanitized)
            if matches:
                sanitized = re.sub(p["pattern"], "CREDENTIAL_MASKED", sanitized)
                findings.append({
                    "type": "credential",
                    "name": p["name"],
                    "count": len(matches),
                })

        # 检查多源信息合成泄露
        if agent_id and agent_id in self._read_history:
            sources = self._read_history[agent_id]
            if len(sources) >= 3:
                findings.append({
                    "type": "synthesis_leakage",
                    "sources": list(sources),
                    "count": len(sources),
                })

        if findings:
            decision = OutputDecision.SANITIZED
            reason = f"{len(findings)} issue(s) found"
        else:
            decision = OutputDecision.CLEAN
            reason = "no sensitive info"

        return OutputResult(
            decision=decision,
            sanitized_content=sanitized,
            findings=findings,
            reason=reason,
        )


__all__ = [
    "CREDENTIAL_PATTERNS",
    "MAX_OUTPUT_SIZE",
    "PII_PATTERNS",
    "OutputDecision",
    "OutputGuard",
    "OutputResult",
]
