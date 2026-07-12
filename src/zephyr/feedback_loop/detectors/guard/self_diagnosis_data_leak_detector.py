# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.self_diagnosis_data_leak_detector
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_self_diagnosis_data_leak_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R530: SelfDiagnosisDataLeakDetector
自诊断报告敏感数据泄漏扫描 — API Key/PII/内部路径 防护
"""

import re
from dataclasses import dataclass, field


@dataclass
class SelfDiagnosisDataLeakDetector:
    sensitive_patterns: list[tuple[str, str, str]] = field(
        default_factory=lambda: [
            (r"[A-Za-z0-9_-]{20,}:[A-Za-z0-9+/=]{32,}", "api_key_pattern", "high"),
            (r"sk-[A-Za-z0-9]{32,}", "openai_key", "critical"),
            (r"AIza[0-9A-Za-z_-]{35}", "google_api_key", "critical"),
            (r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", "uuid_pattern", "low"),
            (r"(?:postgres|mysql|mongodb)://[^@\s]+@", "database_url", "critical"),
            (r'encryption_key\s*=\s*["\']([^"\']+)["\']', "encryption_key", "critical"),
            (r'(?:private_key|secret_key|api_secret)\s*=\s*["\']([^"\']+)["\']', "secret_assignment", "critical"),
            (r'D:\\\\ZephyrAlpha\\\\[^\s"]+', "internal_path", "medium"),
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "email", "medium"),
        ]
    )
    findings: list[dict] = field(default_factory=list)

    def scan(self, text: str, source: str = "diagnostic_report") -> dict:
        self.findings = []
        for pattern, pattern_name, severity in self.sensitive_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                snippet = text[max(0, match.start() - 10) : match.end() + 10]
                masked_snippet = snippet[:10] + "***" + snippet[-10:] if len(snippet) > 25 else snippet[:6] + "***"
                self.findings.append(
                    {
                        "pattern": pattern_name,
                        "severity": severity,
                        "source": source,
                        "snippet": masked_snippet,
                        "position": match.start(),
                    }
                )

        critical_count = sum(1 for f in self.findings if f["severity"] == "critical")
        high_count = sum(1 for f in self.findings if f["severity"] == "high")

        status = "clean"
        if critical_count > 0:
            status = "critical_leak"
        elif high_count > 0:
            status = "high_risk"
        elif self.findings:
            status = "low_risk"

        return {
            "status": status,
            "findings_count": len(self.findings),
            "critical_findings": critical_count,
            "high_findings": high_count,
            "findings": self.findings[:20],
        }

    def sanitize(self, text: str) -> str:
        sanitized = text
        for pattern, _, _ in self.sensitive_patterns:
            sanitized = re.sub(pattern, lambda m: m.group(0)[:8] + "***[REDACTED]", sanitized, flags=re.IGNORECASE)
        return sanitized
