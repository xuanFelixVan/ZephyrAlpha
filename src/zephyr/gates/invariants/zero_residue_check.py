# [BLUEPRINT] MOD-INF-007 | 03_modules/_cross_layer/gate-engine/blueprint.md | §

# [MODULE] zephyr.gates.invariants.zero_residue_check

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ResidueFinding:
    rule_id: str
    message: str
    severity: str
    file_rel: str


@dataclass
class ResidueReport:
    is_clean: bool = True
    findings: list[ResidueFinding] = field(default_factory=list)

    def add(self, rule_id: str, message: str, severity: str, file_rel: str = "") -> None:
        self.is_clean = False
        self.findings.append(
            ResidueFinding(
                rule_id=rule_id,
                message=message,
                severity=severity,
                file_rel=file_rel,
            )
        )


class ZeroResidueScanner:
    def __init__(self, project_root: Path | None = None) -> None:
        if project_root is None:
            project_root = Path(__file__).resolve().parents[4]
        self._root = project_root
        self._scripts_dir = project_root / "scripts" / "governance"

    def scan(self) -> ResidueReport:
        report = ResidueReport()

        self._scan_temp_files(report)
        self._scan_residual_files(report)
        self._scan_ruins_references(report)
        self._scan_orphan_py(report)
        self._scan_orphan_docs(report)

        return report

    def _run_script(self, script_rel: str) -> tuple[int, str, str]:
        script_path = self._scripts_dir / script_rel
        if not script_path.exists():
            return (1, "", f"Script not found: {script_path}")
        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=str(self._root),
                timeout=120,
            )
            return (proc.returncode, proc.stdout, proc.stderr)
        except subprocess.TimeoutExpired:
            return (1, "", "Script timed out")
        except Exception as exc:
            return (1, "", str(exc))

    def _parse_findings(self, exit_code: int, stderr: str) -> list[str]:
        if exit_code == 0:
            return []
        issues: list[str] = []
        for line in stderr.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("===") or stripped.startswith("---"):
                continue
            if "[TEMP-FILES]" in stripped or "[RESIDUAL]" in stripped or "[RUINS-SCAN]" in stripped:
                continue
            if "[ORPHAN-PY]" in stripped or "[ORPHAN-DOC]" in stripped:
                continue
            if "Scanned " in stripped and " files" in stripped:
                continue
            if stripped.startswith("[") and "]" in stripped[:6]:
                issues.append(stripped)
            elif len(stripped) > 5:
                issues.append(stripped)
        return issues

    def _scan_temp_files(self, report: ResidueReport) -> None:
        code, out, err = self._run_script("d1_structure/detect_temp_files.py")
        for issue in self._parse_findings(code, err):
            report.add("ZR-001", issue, "error")

    def _scan_residual_files(self, report: ResidueReport) -> None:
        code, out, err = self._run_script("d1_structure/detect_residual_files.py")
        for issue in self._parse_findings(code, err):
            report.add("ZR-006", issue, "warning")

    def _scan_ruins_references(self, report: ResidueReport) -> None:
        code, out, err = self._run_script("d4_paths/detect_ruins_references.py")
        for issue in self._parse_findings(code, err):
            report.add("ZR-005", issue, "error")

    def _scan_orphan_py(self, report: ResidueReport) -> None:
        code, out, err = self._run_script("d1_structure/detect_orphan_py.py")
        for issue in self._parse_findings(code, err):
            report.add("ZR-003", issue, "warning")

    def _scan_orphan_docs(self, report: ResidueReport) -> None:
        code, out, err = self._run_script("d9_knowledge/detect_orphan_documents.py")
        for issue in self._parse_findings(code, err):
            report.add("ZR-004", issue, "warning")
