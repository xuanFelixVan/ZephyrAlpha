# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.ct_security_artifact_scan

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

SecurityArtifactScanHandler — SecurityArtifactScanHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""



from __future__ import annotations





from typing import Any





from zephyr.gates.check_types.check_type_registry import CheckTypeHandler, register_check_type


from zephyr.gates.task_types import Task








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


                    from zephyr.l10_compliance.artifact_scanner import ArtifactScanner


                    scanner = ArtifactScanner()


                    scanner._RULES = []


                    scan_paths = list(params.get("scan_paths", []))


                    for sp in scan_paths:


                        path = project_root / sp if not str(sp).startswith(str(project_root)) else __import__("pathlib").Path(sp)


                        if not path.exists():


                            continue


                        if path.is_file():


                            report = scanner.scan_file(path)


                            if not report.is_clean:


                                for f in report.findings:


                                    violations.append({"message": f"{report.target}:L{f.line_number}: {f.message}", "severity": f.severity})


                        else:


                            py_files = list(path.rglob("*.py"))


                            for report in scanner.scan_files(py_files):


                                if not report.is_clean:


                                    for f in report.findings:


                                        violations.append({"message": f"{report.target}:L{f.line_number}: {f.message}", "severity": f.severity})


                except Exception as exc:


                    violations.append({"message": f"Security artifact scan failed: {exc}", "severity": "P2"})


                return violations


