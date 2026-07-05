# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_security_artifact_scan
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.check_types.check_type_registry; zephyr.governance.rule_enforcement.task_types
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_ct_security_artifact_scan | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

SecurityArtifactScanHandler — SecurityArtifactScanHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class SecurityArtifactScanHandler(CheckTypeHandler):
    name = "security_artifact_scan"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations = []

        try:
            import importlib

            _mod = importlib.import_module("zephyr.governance.drift_detection.artifact_scanner")
            ArtifactScanner = _mod.ArtifactScanner

            scanner = ArtifactScanner()

            scanner._RULES = []

            scan_paths = list(params.get("scan_paths", []))

            for sp in scan_paths:
                path = (
                    project_root / sp if not str(sp).startswith(str(project_root)) else __import__("pathlib").Path(sp)
                )

                if not path.exists():
                    continue

                if path.is_file():
                    report = scanner.scan_file(path)

                    if not report.is_clean:
                        for f in report.findings:
                            violations.append(
                                {"message": f"{report.target}:L{f.line_number}: {f.message}", "severity": f.severity}
                            )

                else:
                    py_files = list(path.rglob("*.py"))

                    for report in scanner.scan_files(py_files):
                        if not report.is_clean:
                            for f in report.findings:
                                violations.append(
                                    {
                                        "message": f"{report.target}:L{f.line_number}: {f.message}",
                                        "severity": f.severity,
                                    }
                                )

        except Exception as exc:
            violations.append({"message": f"Security artifact scan failed: {exc}", "severity": "P2"})

        return violations
