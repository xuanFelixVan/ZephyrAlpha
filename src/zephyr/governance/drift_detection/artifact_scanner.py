# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.drift_detection.artifact_scanner
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/compliance/artifact_scanner.py; tests/governance/security/test_artifact_scanner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_artifact_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODEGEN:ARTIFACT-SCAN ====
"""
ArtifactScanner — SSRF / Path Traversal / Credential / Token 防御扫描器

独立于 SecurityGateway 的 artifact 级安全扫描器，适用于：
  - 代码审查门禁（CI/CD pipeline）
  - 文件变更前置检查
  - 模型输出 artifact 审计

检测类别：
  S-01 SSRF URL 模式
  S-02 Path Traversal 模式
  S-03 Hardcoded 凭据
  S-04 Token / API Key 泄漏
  S-05 敏感文件路径引用
  S-06 命令注入模式

SSoT: cross_layer_contracts.yaml v3.0
Phase F — LLM 安全门禁落地
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class ArtifactFinding:
    rule_id: str
    category: str
    severity: str
    message: str
    file_path: str = ""
    line_number: int = 0
    snippet: str = ""


@dataclass
class ScanReport:
    target: str
    findings: list[ArtifactFinding] = field(default_factory=list)
    summary: str = ""

    @property
    def is_clean(self) -> bool:
        return len(self.findings) == 0

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")


class ArtifactScanner:
    """多类别 artifact 安全扫描器

    使用方式：
        scanner = ArtifactScanner()
        report = scanner.scan_file(Path("src/pipeline/worker.py"))
        report = scanner.scan_content("some content...", label="pipeline_worker.py")
    """

    _RULES: ClassVar[list[dict]] = [
        # ─── S-01: SSRF ───
        {
            "rule_id": "S-01-SSRF-IP",
            "category": "ssrf",
            "severity": "error",
            "pattern": re.compile(
                r"https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:\/\S*)?",
                re.IGNORECASE,
            ),
            "message": "SSRF risk: raw IP address URL — may target internal services",
        },
        {
            "rule_id": "S-01-SSRF-LOCALHOST",
            "category": "ssrf",
            "severity": "error",
            "pattern": re.compile(
                r"https?://(?:localhost|127\.\d{1,3}\.\d{1,3}\.\d{1,3}|0\.0\.0\.0)",
                re.IGNORECASE,
            ),
            "message": "SSRF risk: localhost URL — may bypass network boundaries",
        },
        {
            "rule_id": "S-01-SSRF-METADATA",
            "category": "ssrf",
            "severity": "error",
            "pattern": re.compile(
                r"(?:169\.254\.169\.254|metadata\.google\.internal" r"|instance-data\.ec2\.\w+?\.amazonaws\.com)",
                re.IGNORECASE,
            ),
            "message": "SSRF risk: cloud metadata endpoint access",
        },
        # ─── S-02: Path Traversal ───
        {
            "rule_id": "S-02-PATH-TRAVERSAL",
            "category": "path_traversal",
            "severity": "error",
            "pattern": re.compile(
                r"(?:\.\.(?:/|\\)){2,}(?:etc|var|root|Windows|System32|boot|dev|proc)",
                re.IGNORECASE,
            ),
            "message": "Path traversal: references protected system directory",
        },
        {
            "rule_id": "S-02-PATH-ABSOLUTE",
            "category": "path_traversal",
            "severity": "warning",
            "pattern": re.compile(
                r"(?:^|[\s\"'`])(?:[A-Za-z]:\\|/(?:etc|var|tmp|home|root|opt)/)(?:\S+)",
            ),
            "message": "Absolute filesystem path reference — review for path traversal risk",
        },
        # ─── S-03: Credentials ───
        {
            "rule_id": "S-03-CRED-HARDCODED",
            "category": "credential",
            "severity": "error",
            "pattern": re.compile(
                r"""(?:
                    (?:api[_-]?key|apikey|secret[_-]?key|private[_-]?key
                    |access[_-]?key|auth[_-]?token|bearer[_-]?token)\s*[:=]\s*
                    [\"'][A-Za-z0-9+/=_-]{16,}[\"']
                    |
                    (?:password|passwd|pwd)\s*[:=]\s*[\"'][^\"'\s]{6,}[\"']
                )""",
                re.IGNORECASE | re.VERBOSE,
            ),
            "message": "Hardcoded credential or secret key detected",
        },
        # ─── S-04: Token Leak ───
        {
            "rule_id": "S-04-TOKEN-GITHUB",
            "category": "token_leak",
            "severity": "error",
            "pattern": re.compile(
                r"gh[ps]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}",
            ),
            "message": "GitHub personal access token pattern detected",
        },
        {
            "rule_id": "S-04-TOKEN-OPENAI",
            "category": "token_leak",
            "severity": "error",
            "pattern": re.compile(
                r"sk-(?:proj-)?[A-Za-z0-9]{32,}",
            ),
            "message": "OpenAI API key pattern detected",
        },
        {
            "rule_id": "S-04-TOKEN-JWT",
            "category": "token_leak",
            "severity": "warning",
            "pattern": re.compile(
                r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}",
            ),
            "message": "JWT token pattern detected — may be expired but should not be logged",
        },
        # ─── S-05: Sensitive Files ───
        {
            "rule_id": "S-05-FILE-ENV",
            "category": "sensitive_file",
            "severity": "warning",
            "pattern": re.compile(
                r"(?:\.env(?:\.[a-z]+)?|credentials\.(?:json|yaml|yml|ini)" r"|\.aws/credentials|\.ssh/id_|\.netrc)",
                re.IGNORECASE,
            ),
            "message": "Reference to sensitive configuration file",
        },
        # ─── S-06: Command Injection ───
        {
            "rule_id": "S-06-CMD-INJECT",
            "category": "command_injection",
            "severity": "error",
            "pattern": re.compile(
                r"(?:os\.system|subprocess\.(?:run|Popen|call|check_output)"
                r"|exec\s*\(|eval\s*\()\s*\(\s*(?:f[\"']|[\"'].*\{)",
                re.IGNORECASE,
            ),
            "message": "Command injection risk: dynamic subprocess/eval with format string",
        },
    ]

    _CONFIG_RULES: ClassVar[list[dict]] = [
        {
            "rule_id": "S-07-CONFIG-SECRET",
            "category": "config_secret",
            "severity": "error",
            "pattern": re.compile(
                r"""(?:password|passwd|pwd|secret|token)\s*[:=]\s*["']?[^\s"']{6,}""",
                re.IGNORECASE,
            ),
            "message": "Hardcoded secret in configuration file",
        },
    ]

    _NOTEBOOK_RULES: ClassVar[list[dict]] = [
        {
            "rule_id": "S-08-NB-SYSTEM",
            "category": "notebook_risk",
            "severity": "error",
            "pattern": re.compile(
                r"os\.system|subprocess\.(?:run|Popen|call|check_output)",
            ),
            "message": "Dangerous system call in notebook cell",
        },
        {
            "rule_id": "S-08-NB-PIP",
            "category": "notebook_risk",
            "severity": "warning",
            "pattern": re.compile(r"!\s*pip\s+install"),
            "message": "Inline pip install in notebook — should use requirements.txt",
        },
    ]

    def scan_content(self, content: str, label: str = "<content>") -> ScanReport:
        findings: list[ArtifactFinding] = []
        lines = content.split("\n")

        for rule in self._RULES:
            for i, line in enumerate(lines, start=1):
                for m in rule["pattern"].finditer(line):
                    findings.append(
                        ArtifactFinding(
                            rule_id=rule["rule_id"],
                            category=rule["category"],
                            severity=rule["severity"],
                            message=rule["message"],
                            file_path=label,
                            line_number=i,
                            snippet=m.group(0)[:150],
                        )
                    )

        error_count = sum(1 for f in findings if f.severity == "error")
        warn_count = sum(1 for f in findings if f.severity == "warning")

        summary = (
            f"[CLEAN] {label}" if not findings else f"[FOUND] {label}: {error_count} errors, {warn_count} warnings"
        )

        return ScanReport(target=label, findings=findings, summary=summary)

    def _scan_with_rules(self, content: str, label: str, rules: list[dict]) -> ScanReport:
        findings: list[ArtifactFinding] = []
        lines = content.split("\n")
        for rule in rules:
            for i, line in enumerate(lines, start=1):
                for m in rule["pattern"].finditer(line):
                    findings.append(
                        ArtifactFinding(
                            rule_id=rule["rule_id"],
                            category=rule["category"],
                            severity=rule["severity"],
                            message=rule["message"],
                            file_path=label,
                            line_number=i,
                            snippet=m.group(0)[:150],
                        )
                    )
        error_count = sum(1 for f in findings if f.severity == "error")
        warn_count = sum(1 for f in findings if f.severity == "warning")
        summary = (
            f"[CLEAN] {label}" if not findings else f"[FOUND] {label}: {error_count} errors, {warn_count} warnings"
        )
        return ScanReport(target=label, findings=findings, summary=summary)

    def scan_file(self, file_path: Path) -> ScanReport:
        if not file_path.exists():
            return ScanReport(target=str(file_path), summary=f"[MISSING] {file_path}")
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return ScanReport(target=str(file_path), summary=f"[BINARY] {file_path}")
        base_report = self.scan_content(content, label=str(file_path))
        suffix = file_path.suffix.lower()
        extra_rules: list[dict] = []
        if suffix in (".yaml", ".yml"):
            extra_rules = self._CONFIG_RULES
        elif suffix == ".ipynb":
            extra_rules = self._NOTEBOOK_RULES
        if extra_rules:
            extra_report = self._scan_with_rules(content, str(file_path), extra_rules)
            combined_findings = base_report.findings + extra_report.findings
            error_count = sum(1 for f in combined_findings if f.severity == "error")
            warn_count = sum(1 for f in combined_findings if f.severity == "warning")
            summary = (
                f"[CLEAN] {file_path}"
                if not combined_findings
                else f"[FOUND] {file_path}: {error_count} errors, {warn_count} warnings"
            )
            return ScanReport(target=str(file_path), findings=combined_findings, summary=summary)
        return base_report

    def scan_directory(self, directory: Path) -> list[ScanReport]:
        reports: list[ScanReport] = []
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                reports.append(self.scan_file(file_path))
        return reports

    def scan_files(self, paths: list[Path]) -> list[ScanReport]:
        return [self.scan_file(p) for p in paths]


__all__ = [
    "ArtifactFinding",
    "ArtifactScanner",
    "ScanReport",
]

# ==== END CODEGEN:ARTIFACT-SCAN ====
