# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_security
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A 安全内容扫描器 — 六大类威胁检测

对 A2A 消息 payload 进行内容安全扫描:
  1. prompt_injection: 提示词注入 — "ignore previous instructions" / "system:" 前缀劫持
  2. code_execution: 代码执行 — eval/exec/os.system/subprocess 含未审查参数
  3. credential_leak: 凭证泄漏 — api_key/token/password/secrets 暴露
  4. path_traversal: 路径穿越 — "../../etc/passwd" 类攻击
  5. denylist_content: 黑名单内容 — 恶意 URL / XSS / SQL 注入片段
  6. oversized_payload: 超大 payload — 单消息超过 token 预算

输出: A2ASecurityReport — 每个 Message Part 的安全判定
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class SecurityVerdict(str, Enum):
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class ThreatCategory(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    CODE_EXECUTION = "code_execution"
    CREDENTIAL_LEAK = "credential_leak"
    PATH_TRAVERSAL = "path_traversal"
    DENYLIST_CONTENT = "denylist_content"
    OVERSIZED_PAYLOAD = "oversized_payload"


@dataclass
class SecurityFinding:
    category: ThreatCategory
    verdict: SecurityVerdict
    description: str
    line_number: int | None = None
    matched_pattern: str = ""


@dataclass
class A2ASecurityReport:
    agent_id: str
    message_id: str
    findings: list[SecurityFinding] = field(default_factory=list)
    clean: bool = True

    @property
    def blocked(self) -> bool:
        return any(f.verdict is SecurityVerdict.MALICIOUS for f in self.findings)

    @property
    def suspicious_count(self) -> int:
        return sum(1 for f in self.findings if f.verdict is SecurityVerdict.SUSPICIOUS)


_PROMPT_INJECTION_PATTERNS = [
    (
        r"ignore\s+(all\s+)?(previous|prior)\s+(instructions?|prompts?|context)",
        "Prompt injection: 'ignore previous instructions'",
    ),
    (r"(you\s+are|act\s+as|roleplay\s+as)\s+(now|from\s+now\s+on)", "Role override: 'you are now / act as'"),
    (r"^\s*system\s*:\s*", "System prompt hijacking: 'system:' prefix"),
    (r"(forget|disregard|override)\s+(everything|all)\s+(you|above|before)", "Memory override: 'forget everything'"),
]

_CODE_EXEC_PATTERNS = [
    (r"\beval\s*\(.*\)", "eval() call detected"),
    (r"\bexec\s*\(.*\)", "exec() call detected"),
    (r"\bos\.system\s*\(.*\)", "os.system() call detected"),
    (r"\bsubprocess\.(run|Popen|call)\s*\(.*\)", "subprocess call detected"),
    (r"\b__import__\s*\(.*\)", "dynamic __import__() detected"),
]

_CREDENTIAL_PATTERNS = [
    (r"""(?:api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*['"][A-Za-z0-9_\-]{20,}['"]""", "API key/secret exposed"),
    (r"""(?:password|passwd|pwd)\s*[:=]\s*['"][^'"]{4,}['"]""", "Password exposed"),
    (r"""sk-[A-Za-z0-9]{32,}""", "OpenAI-style secret key"),
    (r"""(?:token|auth[_-]?token)\s*[:=]\s*['"][A-Za-z0-9_\-.]{20,}['"]""", "Auth token exposed"),
]

_PATH_TRAVERSAL_PATTERNS = [
    (r"(?:\.\.[/\\]){2,}", "Path traversal: ../../"),
    (r"""(?:/etc/(?:passwd|shadow|hosts))""", "Linux system file access"),
    (r"""C:\\Windows\\System32\\""", "Windows system32 access"),
]

_DENYLIST_PATTERNS = [
    (r"<script[^>]*>.*?</script>", "XSS: <script> tag injection"),
    (r"javascript\s*:", "XSS: javascript: protocol"),
    (r"('|')\s*(OR|AND)\s+('|')\s*=\s*('|')", "SQL injection: ' OR '1'='1'"),
    (r"data\s*:\s*text/html", "HTML data URI injection"),
]


class A2ASecurityScanner:
    """A2A 消息安全扫描器.

    扫描跨 Agent 消息 payload 的六个维度:
      prompt_injection / code_execution / credential_leak /
      path_traversal / denylist_content / oversized_payload
    """

    def __init__(
        self,
        max_payload_bytes: int = 100_000,
        scan_prompt_injection: bool = True,
        scan_code_execution: bool = True,
        scan_credentials: bool = True,
        scan_path_traversal: bool = True,
        scan_denylist: bool = True,
    ):
        self._max_payload_bytes = max_payload_bytes
        self._scan_categories = {
            ThreatCategory.PROMPT_INJECTION: scan_prompt_injection,
            ThreatCategory.CODE_EXECUTION: scan_code_execution,
            ThreatCategory.CREDENTIAL_LEAK: scan_credentials,
            ThreatCategory.PATH_TRAVERSAL: scan_path_traversal,
            ThreatCategory.DENYLIST_CONTENT: scan_denylist,
            ThreatCategory.OVERSIZED_PAYLOAD: True,
        }

    def scan(self, agent_id: str, message_id: str, content: str) -> A2ASecurityReport:
        """扫描消息内容，返回安全报告."""

        if not content.strip():
            return A2ASecurityReport(agent_id=agent_id, message_id=message_id, clean=True)

        findings: list[SecurityFinding] = []

        if len(content.encode("utf-8")) > self._max_payload_bytes:
            findings.append(
                SecurityFinding(
                    category=ThreatCategory.OVERSIZED_PAYLOAD,
                    verdict=SecurityVerdict.SUSPICIOUS,
                    description=f"Payload exceeds max size ({len(content.encode('utf-8'))} > {self._max_payload_bytes})",
                )
            )

        if self._scan_categories[ThreatCategory.PROMPT_INJECTION]:
            findings.extend(self._scan_patterns(content, _PROMPT_INJECTION_PATTERNS, ThreatCategory.PROMPT_INJECTION))

        if self._scan_categories[ThreatCategory.CODE_EXECUTION]:
            findings.extend(self._scan_patterns(content, _CODE_EXEC_PATTERNS, ThreatCategory.CODE_EXECUTION))

        if self._scan_categories[ThreatCategory.CREDENTIAL_LEAK]:
            findings.extend(self._scan_patterns(content, _CREDENTIAL_PATTERNS, ThreatCategory.CREDENTIAL_LEAK))

        if self._scan_categories[ThreatCategory.PATH_TRAVERSAL]:
            findings.extend(self._scan_patterns(content, _PATH_TRAVERSAL_PATTERNS, ThreatCategory.PATH_TRAVERSAL))

        if self._scan_categories[ThreatCategory.DENYLIST_CONTENT]:
            findings.extend(self._scan_patterns(content, _DENYLIST_PATTERNS, ThreatCategory.DENYLIST_CONTENT))

        clean = not any(f.verdict is SecurityVerdict.MALICIOUS for f in findings)

        return A2ASecurityReport(
            agent_id=agent_id,
            message_id=message_id,
            findings=findings,
            clean=clean,
        )

    def _scan_patterns(
        self,
        content: str,
        patterns: list[tuple[str, str]],
        category: ThreatCategory,
    ) -> list[SecurityFinding]:
        findings: list[SecurityFinding] = []
        lines = content.split("\n")

        for pattern_str, description in patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for lineno, line in enumerate(lines, 1):
                match = pattern.search(line)
                if match:
                    findings.append(
                        SecurityFinding(
                            category=category,
                            verdict=SecurityVerdict.MALICIOUS,
                            description=description,
                            line_number=lineno,
                            matched_pattern=pattern_str,
                        )
                    )
                    break

        return findings

    @staticmethod
    def scan_multiple(
        scanner: A2ASecurityScanner,
        messages: list[tuple[str, str, str]],
    ) -> list[A2ASecurityReport]:
        results: list[A2ASecurityReport] = []
        for agent_id, message_id, content in messages:
            results.append(scanner.scan(agent_id, message_id, content))
        return results

    @staticmethod
    def summary(reports: list[A2ASecurityReport]) -> dict:
        total = len(reports)
        blocked = sum(1 for r in reports if r.blocked)
        suspicious = sum(1 for r in reports if r.suspicious_count > 0 and not r.blocked)
        clean = total - blocked - suspicious

        all_findings: dict[str, int] = {}
        for report in reports:
            for f in report.findings:
                key = f.category.value
                all_findings[key] = all_findings.get(key, 0) + 1

        return {
            "total_messages": total,
            "blocked": blocked,
            "suspicious": suspicious,
            "clean": clean,
            "findings_by_category": all_findings,
        }
