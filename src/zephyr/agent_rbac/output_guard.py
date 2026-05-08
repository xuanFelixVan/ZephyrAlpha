"""
L5 Output Guard — 输出护栏 (PII脱敏/凭证检测/截断/合成泄漏检测)

MOD-INF-018 §2.8  D-018-10

PII脱敏含中文身份证18位/手机号11位/统一社会信用代码18位 (B107).
Synthesis Leakage Detection — 跨读链合成输出检测.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class OutputDecision(str, Enum):
    CLEAN = "CLEAN"
    SANITIZED = "SANITIZED"
    TRUNCATED = "TRUNCATED"
    BLOCKED = "BLOCKED"


PII_PATTERNS: list[tuple[str, str, str]] = [
    (r"\b1[3-9]\d{9}\b", "PHONE_CN", "Mobile number"),
    (r"\b[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b", "ID_CN", "Chinese ID"),
    (r"\b[0-9A-Z]{18}\b", "CREDIT_CODE_CN", "Unified Social Credit Code"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "EMAIL", "Email address"),
]
MSG = "msg"

CREDENTIAL_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)sk-[A-Za-z0-9]{32,}", "OpenAI API Key"),
    (r"(?i)AIza[0-9A-Za-z\-_]{35}", "Google API Key"),
    (r"(?i)AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"(?i)eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+", "JWT Token"),
    (r"(?i)ghp_[A-Za-z0-9]{36}", "GitHub Token"),
    (r"\b[a-f0-9]{40}\b", "Potential API Key"),
]

MAX_OUTPUT_SIZE = 1024 * 1024


@dataclass
class OutputResult:
    decision: OutputDecision = OutputDecision.CLEAN
    sanitized_content: str = ""
    findings: list[str] = field(default_factory=list)
    truncated_original_size: int = 0


class OutputGuard:
    def __init__(self) -> None:
        self._read_sources: dict[str, list[str]] = {}
        self._synthesis_threshold = 3

    def check(self, content: str, agent_id: str = "") -> OutputResult:
        findings: list[str] = []
        sanitized = content

        for pattern, label, desc in PII_PATTERNS:
            matches = re.findall(pattern, sanitized)
            if matches:
                findings.append(f"PII {label} ({desc}): {len(matches)} instance(s)")
                sanitized = re.sub(pattern, f"[{label}]", sanitized)

        for pattern, desc in CREDENTIAL_PATTERNS:
            matches = re.findall(pattern, sanitized)
            if matches:
                findings.append(f"Credential ({desc}): {len(matches)} instance(s)")
                sanitized = re.sub(pattern, "[CREDENTIAL_MASKED]", sanitized)

        decision = OutputDecision.SANITIZED if findings else OutputDecision.CLEAN

        if len(content.encode("utf-8")) > MAX_OUTPUT_SIZE:
            truncate_point = MAX_OUTPUT_SIZE
            sanitized = sanitized.encode("utf-8")[:truncate_point].decode("utf-8", errors="replace")
            sanitized += "\n\n[SIZE_TRUNCATED]"
            if decision == OutputDecision.CLEAN:
                decision = OutputDecision.TRUNCATED
            findings.append(f"Output truncated: {len(content.encode('utf-8'))} > {MAX_OUTPUT_SIZE}")

        synthesis = self._check_synthesis_leakage(agent_id, content)
        if synthesis:
            findings.append(synthesis)
            if decision == OutputDecision.CLEAN:
                decision = OutputDecision.SANITIZED

        return OutputResult(
            decision=decision,
            sanitized_content=sanitized,
            findings=findings,
            truncated_original_size=len(content.encode("utf-8")) if decision == OutputDecision.TRUNCATED else 0,
        )

    def record_read(self, agent_id: str, source: str) -> None:
        sources = self._read_sources.setdefault(agent_id, [])
        sources.append(source)
        if len(sources) > 100:
            self._read_sources[agent_id] = sources[-100:]

    def _check_synthesis_leakage(self, agent_id: str, output: str) -> Optional[str]:
        sources = self._read_sources.get(agent_id, [])
        if len(sources) < self._synthesis_threshold:
            return None
        unique_sources = list(set(sources))
        if len(unique_sources) >= self._synthesis_threshold:
            return f"Synthesis leakage risk: agent read from {len(unique_sources)} sources before generating output"
        return None

    def reset_agent(self, agent_id: str) -> None:
        self._read_sources.pop(agent_id, None)
