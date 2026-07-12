# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.task_completion_gate
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.infrastructure.lifecycle.task_lifecycle_manager
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_task_completion_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TaskCompletionGate: scan for residual files outside files_in_scope
===================================================================
Task ID : T-2-25 (C52)
safety_level : L

Detects residual files that should not exist in a target directory:
  - temp_* patterns
  - *.backup patterns
  - *-v2.* versioned file patterns
  - __pycache__/ directories
  - *.pyc compiled files

Output: list of residual files with suggested disposition (delete/move/keep)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Disposition(str, Enum):
    DELETE = "delete"
    MOVE = "move"
    KEEP = "keep"


class ResidualType(str, Enum):
    TEMP = "temp_file"
    BACKUP = "backup_file"
    VERSIONED = "versioned_file"
    PYCACHE = "pycache_dir"
    PYC = "compiled_pyc"


_RESIDUAL_PATTERNS: list[tuple[ResidualType, re.Pattern[str]]] = [
    (ResidualType.TEMP, re.compile(r"^temp_")),
    (ResidualType.BACKUP, re.compile(r"\.backup$")),
    (ResidualType.VERSIONED, re.compile(r"-v\d+\.")),
    (ResidualType.PYCACHE, re.compile(r"^__pycache__$")),
    (ResidualType.PYC, re.compile(r"\.pyc$")),
]

_DISPOSITION_MAP: dict[ResidualType, Disposition] = {
    ResidualType.TEMP: Disposition.DELETE,
    ResidualType.BACKUP: Disposition.DELETE,
    ResidualType.VERSIONED: Disposition.DELETE,
    ResidualType.PYCACHE: Disposition.DELETE,
    ResidualType.PYC: Disposition.DELETE,
}


@dataclass
class ResidualFile:
    path: Path
    rel_path: str
    residual_type: ResidualType
    disposition: Disposition
    reason: str


@dataclass
class GateReport:
    scan_dir: str = ""
    total_scanned: int = 0
    residual_count: int = 0
    residuals: list[ResidualFile] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.residual_count == 0

    @property
    def by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.residuals:
            key = r.residual_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    @property
    def by_disposition(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in self.residuals:
            key = r.disposition.value
            counts[key] = counts.get(key, 0) + 1
        return counts


class GateLevel(str, Enum):
    """G0-G7 门禁级别——从蓝图 MOD-TASK_SYSTEM §3.2.1"""

    G0 = "G0"
    G7 = "G7"
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"
    G4 = "G4"
    G5 = "G5"
    G6 = "G6"


@dataclass
class G7CheckResult:
    gate_id: str = "G7"
    passed: bool = False
    violations: list[str] = field(default_factory=list)
    checked_fields: list[str] = field(default_factory=list)


class G7CompletenessGate:
    """G7 完整度门禁——验证任务卡防漂移字段是否完整填充

    Checks:
      1. upstream_files 非空 + 路径格式
      2. downstream_outputs 非空 + 路径格式
      3. rollback_instructions 非空
      4. applicable_rules 非空
      5. context_assembly_manifest 非空
      6. allowed_touch / forbidden_touch 非空
    """

    REQUIRED_FIELDS = [
        "upstream_files",
        "downstream_outputs",
        "rollback_instructions",
        "applicable_rules",
        "context_assembly_manifest",
        "allowed_touch",
        "forbidden_touch",
    ]

    def check(self, task_card: dict) -> G7CheckResult:
        result = G7CheckResult(checked_fields=list(self.REQUIRED_FIELDS))
        violations: list[str] = []

        for field in self.REQUIRED_FIELDS:
            value = task_card.get(field)
            if value is None:
                violations.append(f"MISSING: {field}")
                continue
            if isinstance(value, (list, dict)) and len(value) == 0:
                violations.append(f"EMPTY: {field}")
                continue
            if isinstance(value, str) and len(value.strip()) < 20:
                violations.append(f"TOO_SHORT: {field}")

        result.violations = violations
        result.passed = len(violations) == 0
        return result

    def format_result(self, result: G7CheckResult) -> str:
        lines = [
            "G7 Completeness Gate Report",
            f"Passed: {'YES' if result.passed else 'NO'}",
            f"Checked fields: {len(result.checked_fields)}",
        ]
        if result.violations:
            lines.append("Violations:")
            for v in result.violations:
                lines.append(f"  - {v}")
        return "\n".join(lines)


class TaskCompletionGate:
    """Scan a directory for residual files not in files_in_scope.

    Parameters
    ----------
    scan_dir : Path
        Directory to scan recursively.
    files_in_scope : set[str] | None
        Set of relative paths that are expected. If None, only pattern-based
        detection is used.
    extra_patterns : list[tuple[ResidualType, re.Pattern[str]]] | None
        Additional residual patterns to detect.
    """

    def __init__(
        self,
        scan_dir: Path,
        files_in_scope: set[str] | None = None,
        extra_patterns: list[tuple[ResidualType, re.Pattern[str]]] | None = None,
    ) -> None:
        self._scan_dir = scan_dir
        self._files_in_scope = files_in_scope
        self._patterns = list(_RESIDUAL_PATTERNS)
        if extra_patterns:
            self._patterns.extend(extra_patterns)

    def scan(self) -> GateReport:
        report = GateReport(scan_dir=str(self._scan_dir))

        if not self._scan_dir.exists():
            return report

        for path in self._scan_dir.rglob("*"):
            report.total_scanned += 1
            name = path.name

            for rtype, pattern in self._patterns:
                if pattern.search(name):
                    try:
                        rel = path.relative_to(self._scan_dir).as_posix()
                    except ValueError:
                        rel = str(path)
                    disposition = _DISPOSITION_MAP.get(rtype, Disposition.KEEP)
                    report.residuals.append(
                        ResidualFile(
                            path=path,
                            rel_path=rel,
                            residual_type=rtype,
                            disposition=disposition,
                            reason=f"Matches pattern '{pattern.pattern}' for type {rtype.value}",
                        )
                    )
                    report.residual_count += 1
                    break

        if self._files_in_scope is not None:
            for path in self._scan_dir.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    rel = path.relative_to(self._scan_dir).as_posix()
                except ValueError:
                    continue
                if rel not in self._files_in_scope:
                    already = any(r.rel_path == rel for r in report.residuals)
                    if not already:
                        report.residuals.append(
                            ResidualFile(
                                path=path,
                                rel_path=rel,
                                residual_type=ResidualType.TEMP,
                                disposition=Disposition.MOVE,
                                reason=f"File not in files_in_scope: {rel}",
                            )
                        )
                        report.residual_count += 1

        return report

    def format_report(self, report: GateReport) -> str:
        lines: list[str] = [
            "Task Completion Gate Report",
            f"Scan dir: {report.scan_dir}",
            f"Total scanned: {report.total_scanned}",
            f"Residual files: {report.residual_count}",
            f"Passed: {'YES' if report.passed else 'NO'}",
            "",
        ]
        if report.residuals:
            lines.append(f"{'Type':<15} {'Disposition':<12} {'Path'}")
            lines.append("-" * 60)
            for r in report.residuals:
                lines.append(f"{r.residual_type.value:<15} {r.disposition.value:<12} {r.rel_path}")
        return "\n".join(lines)


def g7_check_delegate(task_card: dict) -> G7CheckResult:
    """G7 委托层 — 桥接 TaskLifecycleManager.gate_g7_output()。
    TASK-INF-0131: 确保两个 G7 实现路径一致且互补。
    """
    try:
        from zephyr.infrastructure.lifecycle.task_lifecycle_manager import TaskLifecycleManager

        manager = TaskLifecycleManager()
        result = manager.gate_g7_output(task_card)
        return G7CheckResult(
            gate_id="G7",
            passed=result.passed,
            violations=[result.details] if not result.passed else [],
            checked_fields=[
                "upstream_files",
                "downstream_outputs",
                "rollback_instructions",
                "context_assembly_manifest",
                "allowed_touch",
                "forbidden_touch",
            ],
        )
    except ImportError:
        gate = G7CompletenessGate()
        return gate.check(task_card)
