# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_deduplication
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_ct_deduplication | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class DeduplicationHandler(CheckTypeHandler):
    name = "deduplication"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []
        try:
            import importlib

            _scanner_mod = importlib.import_module("zephyr.governance.scanner")
            _exit_mod = importlib.import_module("zephyr.governance.code_dedup.exit_codes")
            Scanner = _scanner_mod.Scanner
            ExitCode = _exit_mod.ExitCode

            scan_mode = params.get("scan_mode", "incremental")
            fail_on_severity = params.get("fail_on_severity", "high")

            scanner = Scanner()
            if scan_mode == "incremental":
                _diff_mod = importlib.import_module("zephyr.governance.code_dedup.diff_detector")
                DiffDetector = _diff_mod.DiffDetector
                detector = DiffDetector()
                changed_files = detector.detect()
                if changed_files:
                    scanner.scan_files(changed_files)
            else:
                from pathlib import Path

                root = Path(str(project_root)) if project_root else Path(".")
                py_files = [str(f) for f in root.glob("src/zephyr/**/*.py")]
                if py_files:
                    scanner.scan_files(py_files[:500])

            duplicates = scanner.find_duplicates()

            severity_map = {"critical": "P0", "high": "P0", "medium": "P1", "low": "P2"}
            fail_level = {"critical": 0, "high": 1, "medium": 2, "low": 3}

            for group in duplicates:
                sev = _classify_severity(group)
                if fail_level.get(sev, 3) <= fail_level.get(fail_on_severity, 1):
                    violations.append(
                        dict(
                            message=f"Dedup: {group.group_id} similarity={group.similarity:.2f} severity={sev} members={len(group.members)}",
                            severity=severity_map.get(sev, "P2"),
                            check_id=getattr(check, "id", "DD-CHK-INCREMENTAL"),
                        )
                    )

        except Exception as exc:
            violations.append(
                dict(
                    message=f"Deduplication scan failed: {exc}",
                    severity="P2",
                    check_id=getattr(check, "id", "DD-CHK-INCREMENTAL"),
                )
            )
        return violations


def _classify_severity(group: Any) -> str:
    if group.similarity >= 0.95:
        return "critical"
    if group.similarity >= 0.85:
        return "high"
    if group.similarity >= 0.70:
        return "medium"
    return "low"
