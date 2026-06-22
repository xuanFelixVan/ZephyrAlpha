# [A_module] module_id=MOD-GOV_zero_residue_check | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.invariants.zero_residue_check
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path


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
        if severity == "error":
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
            project_root = Path(__file__).resolve().parents[5]
        self._root = project_root
        self._scripts_dir = project_root / "scripts" / "governance"

    def scan(self) -> ResidueReport:
        report = ResidueReport()

        # 并行运行5个子脚本（RULE-SEVEN: 强制 ThreadPoolExecutor）
        scan_jobs = [
            self._scan_temp_files,
            self._scan_residual_files,
            self._scan_ruins_references,
            self._scan_orphan_py,
            self._scan_orphan_docs,
        ]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fn) for fn in scan_jobs]
            for future in as_completed(futures):
                for rule_id, message, severity, file_rel in future.result():
                    report.add(rule_id, message, severity, file_rel)

        return report

    def _run_script(self, script_rel: str) -> tuple[int, str, str]:
        script_path = self._scripts_dir / script_rel
        if not script_path.exists():
            return (1, "", f"Script not found: {script_path}")
        try:
            # 设置 PYTHONDONTWRITEBYTECODE=1 防止子脚本 import 模块时生成 __pycache__
            # （-B 参数只影响主脚本，不影响 import 的模块）
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            proc = subprocess.run(
                [sys.executable, "-B", str(script_path)],
                capture_output=True,
                text=True,
                cwd=str(self._root),
                env=env,
                timeout=30,
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
            if (stripped.startswith("[") and "]" in stripped[:6]) or len(stripped) > 5:
                issues.append(stripped)
        return issues

    def _scan_temp_files(self) -> list[tuple[str, str, str, str]]:
        code, out, err = self._run_script("d1_structure/detect_temp_files.py")
        return [("ZR-001", issue, "warning", "") for issue in self._parse_findings(code, err)]

    def _scan_residual_files(self) -> list[tuple[str, str, str, str]]:
        code, out, err = self._run_script("d1_structure/detect_residual_files.py")
        return [("ZR-006", issue, "warning", "") for issue in self._parse_findings(code, err)]

    def _scan_ruins_references(self) -> list[tuple[str, str, str, str]]:
        code, out, err = self._run_script("d4_paths/detect_ruins_references.py")
        return [("ZR-005", issue, "warning", "") for issue in self._parse_findings(code, err)]

    def _scan_orphan_py(self) -> list[tuple[str, str, str, str]]:
        code, out, err = self._run_script("d1_structure/detect_orphan_py.py")
        return [("ZR-003", issue, "warning", "") for issue in self._parse_findings(code, err)]

    def _scan_orphan_docs(self) -> list[tuple[str, str, str, str]]:
        code, out, err = self._run_script("d9_knowledge/detect_orphan_documents.py")
        return [("ZR-004", issue, "warning", "") for issue in self._parse_findings(code, err)]
