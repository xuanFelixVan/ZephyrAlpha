# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.text_to_finding_adapter
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.finding_model; zephyr.integration.shared.schema.base_config
# [CONSUMERS] pipeline_runner.py; run_all.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] TextToFindingAdapter is the sole bridge between text-output scripts and AuditFinding; it MUST handle all 15 common output patterns
# [MODIFY-GUARD] Pattern additions require run_all.py compatibility verification
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] parse() never raises; individual line parse failures are silently skipped
# [TESTS] tests/test_audit_full_pipeline_e2e.py
# [A_module] module_id=MOD-GOV_text_to_finding_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import re
from datetime import UTC, datetime

from pydantic import BaseModel

from zephyr.governance.audit_trail.finding_model import (
    AuditFinding,
    BlastRadius,
    FindingDimension,
    FindingSeverity,
    FindingTarget,
    RecommendationBlock,
    RemediationAction,
    RemediationPriority,
    generate_finding_id,
)
from zephyr.integration.shared.schema.base_config import BASE_CONFIG


class ParsedLine(BaseModel):
    model_config = BASE_CONFIG
    severity: FindingSeverity = FindingSeverity.MEDIUM
    file_path: str = ""
    line_range: str = ""
    description: str = ""
    dimension: str = "D5"


class TextToFindingAdapter:
    _SEVERITY_MAP: dict[str, FindingSeverity] = {
        "P0": FindingSeverity.CRITICAL,
        "P1": FindingSeverity.HIGH,
        "P2": FindingSeverity.MEDIUM,
        "P3": FindingSeverity.LOW,
        "CRITICAL": FindingSeverity.CRITICAL,
        "HIGH": FindingSeverity.HIGH,
        "MEDIUM": FindingSeverity.MEDIUM,
        "LOW": FindingSeverity.LOW,
        "INFO": FindingSeverity.INFO,
    }

    _PRIORITY_MAP: dict[str, RemediationPriority] = {
        "P0": RemediationPriority.P0,
        "P1": RemediationPriority.P1,
        "P2": RemediationPriority.P2,
        "P3": RemediationPriority.P3,
        "CRITICAL": RemediationPriority.P0,
        "HIGH": RemediationPriority.P1,
        "MEDIUM": RemediationPriority.P2,
        "LOW": RemediationPriority.P3,
        "INFO": RemediationPriority.P3,
    }

    _COUNT_SEVERITY_MAP: dict[str, str] = {
        "error": "HIGH",
        "errors": "HIGH",
        "failure": "HIGH",
        "failures": "HIGH",
        "violation": "HIGH",
        "violations": "HIGH",
        "warning": "MEDIUM",
        "warnings": "MEDIUM",
        "issue": "LOW",
        "issues": "LOW",
        "problem": "LOW",
        "problems": "LOW",
    }

    _SEVERITY_TAG_RE = re.compile(r"^\s*\[(P[0-3])\]\s*(.*)")
    _ERROR_RE = re.compile(r"^\s*(?:ERROR|VIOLATION)\s*[:：]\s*(.*)", re.IGNORECASE)
    _CROSS_RE = re.compile(r"^\s*❌\s*(.*)")
    _FAIL_RE = re.compile(r"^\s*FAIL\s*[:：]?\s*(.*)", re.IGNORECASE)
    _WARNING_RE = re.compile(r"^\s*(?:WARNING|WARN)\s*[:：]\s*(.*)", re.IGNORECASE)
    _SEVERITY_WORD_TAG_RE = re.compile(r"^\s*\[(CRITICAL|HIGH|MEDIUM|LOW)\]\s+(.+)$")
    _FAILED_EXCEPTION_RE = re.compile(r"^\s*(FAILED|EXCEPTION|FATAL|CRITICAL_ERROR):\s+(.+)$")
    _COUNT_STAT_RE = re.compile(
        r"^\s*(\d+)\s+(errors?|warnings?|issues?|problems?|violations?|failures?)\s+(found|detected|identified|reported)?",
        re.IGNORECASE,
    )
    _FILE_LINE_RE = re.compile(r"^\s*([^\s:]+\.py):(\d+):?\s+(.+)$")
    _UNICODE_MARK_RE = re.compile(r"^\s*[✗✘⚠]\s+(.+)$")
    _INDENT_ITEM_RE = re.compile(r"^\s{2,}[-*]\s+(.+)$")
    _YAML_KEY_RE = re.compile(r"^\s+[\w_-]+:\s+(.+\.py.+)$")
    _CONTINUATION_RE = re.compile(r"^\s{2,}(\S.*)$")
    _FILE_PATH_RE = re.compile(
        r"((?:src|tests|scripts|docs|config|schemas)[/\\][\w/\\._-]+\.\w+)(?::(\d+))?",
        re.IGNORECASE,
    )
    _SKIP_PATTERNS = [
        re.compile(r"^\s*$"),
        re.compile(r"^\s*={3,}"),
        re.compile(r"^\s*-{3,}"),
        re.compile(r"^\s*Scanned\s+\d+"),
        re.compile(r"^\s*\d+\s+(?:files?|scripts?|modules?)"),
        re.compile(r"^\s*(?:PASS|OK|✅|✓|✔|All checks passed|Done|Complete|passed|success)", re.IGNORECASE),
        re.compile(r"^\s*\[GATE-"),
        re.compile(r"^\s*(?:Summary|Total|Result)", re.IGNORECASE),
    ]

    def parse(self, text: str, dimension: str = "D5", script_name: str = "") -> list[AuditFinding]:
        findings: list[AuditFinding] = []
        prev_finding: AuditFinding | None = None
        for line in text.splitlines():
            parsed = self._parse_line(line)
            if parsed is None:
                if prev_finding is not None:
                    cont_m = self._CONTINUATION_RE.match(line)
                    if cont_m:
                        appended = prev_finding.description + " " + cont_m.group(1).strip()
                        prev_finding.description = appended[:500]
                        continue
                    prev_finding = None
                continue
            priority_tag = ""
            for tag, sev in self._SEVERITY_MAP.items():
                if parsed.severity == sev:
                    priority_tag = tag
                    break
            if not priority_tag:
                priority_tag = "P2"
            finding = AuditFinding(
                finding_id=generate_finding_id(dimension, parsed.description[:100]),
                dimension=dimension,
                severity=parsed.severity,
                category=f"{FindingDimension(dimension).label} — {script_name}" if script_name else dimension,
                target=FindingTarget(file_path=parsed.file_path, line_range=parsed.line_range),
                description=parsed.description[:500],
                evidence=line.strip()[:500],
                impact={"blast_radius": BlastRadius.file},
                remediation={
                    "action": RemediationAction.FIX,
                    "priority": self._PRIORITY_MAP.get(priority_tag, RemediationPriority.P2),
                },
                lifecycle={"status": "OPEN"},
                traceability={"related_kb": [], "related_ke": [], "related_finding": []},
                timestamp=datetime.now(UTC).isoformat(),
                recommendation_block=RecommendationBlock(),
            )
            findings.append(finding)
            prev_finding = finding
        return findings

    def _parse_line(self, line: str) -> ParsedLine | None:
        for skip_re in self._SKIP_PATTERNS:
            if skip_re.match(line):
                return None

        m = self._SEVERITY_TAG_RE.match(line)
        if m:
            return self._build_parsed(m.group(1), m.group(2), line)

        m = self._ERROR_RE.match(line)
        if m:
            return self._build_parsed("P1", m.group(1), line)

        m = self._CROSS_RE.match(line)
        if m:
            return self._build_parsed("P1", m.group(1), line)

        m = self._FAIL_RE.match(line)
        if m:
            return self._build_parsed("P2", m.group(1), line)

        m = self._WARNING_RE.match(line)
        if m:
            return self._build_parsed("P3", m.group(1), line)

        m = self._SEVERITY_WORD_TAG_RE.match(line)
        if m:
            return self._build_parsed(m.group(1), m.group(2), line)

        m = self._FAILED_EXCEPTION_RE.match(line)
        if m:
            keyword = m.group(1).upper()
            if keyword in ("FATAL", "CRITICAL_ERROR"):
                priority = "CRITICAL"
            else:
                priority = "HIGH"
            return self._build_parsed(priority, m.group(2), line)

        m = self._COUNT_STAT_RE.match(line)
        if m:
            count_type = m.group(2).lower()
            priority = self._COUNT_SEVERITY_MAP.get(count_type, "LOW")
            return self._build_parsed(priority, line.strip(), line)

        m = self._FILE_LINE_RE.match(line)
        if m:
            return self._build_parsed(
                "MEDIUM",
                m.group(3),
                line,
                file_path_override=m.group(1).replace("\\", "/"),
                line_range_override=m.group(2),
            )

        m = self._UNICODE_MARK_RE.match(line)
        if m:
            mark_char = line.lstrip()[0]
            if mark_char in ("✗", "✘"):
                priority = "HIGH"
            else:
                priority = "LOW"
            return self._build_parsed(priority, m.group(1), line)

        m = self._INDENT_ITEM_RE.match(line)
        if m:
            content = m.group(1)
            if ".py" in content:
                return self._build_parsed("LOW", content, line)
            return None

        m = self._YAML_KEY_RE.match(line)
        if m:
            return self._build_parsed("MEDIUM", m.group(1), line)

        if ".py" in line:
            return self._build_parsed("INFO", line.strip(), line)

        return None

    def _build_parsed(
        self,
        priority: str,
        content: str,
        original_line: str,
        file_path_override: str = "",
        line_range_override: str = "",
    ) -> ParsedLine:
        file_path = file_path_override
        line_range = line_range_override
        if not file_path:
            fm = self._FILE_PATH_RE.search(content) or self._FILE_PATH_RE.search(original_line)
            if fm:
                file_path = fm.group(1).replace("\\", "/")
                if not line_range and fm.group(2):
                    line_range = fm.group(2)
        description = content.strip() if content.strip() else original_line.strip()
        return ParsedLine(
            severity=self._SEVERITY_MAP.get(priority, FindingSeverity.MEDIUM),
            file_path=file_path,
            line_range=line_range,
            description=description[:500],
        )
