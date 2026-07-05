# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.ct_restructuring_safety
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
# [A_module] module_id=MOD-GOV_ct_restructuring_safety | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

RestructuringSafetyHandler — RestructuringSafetyHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""


"""CheckType: restructuring_safety — GOV-ENG-002 代码重组安全检查


=============================================================


自动执行 GOV-ENG-002 §3 强制安全协议的 Post-merge Verify：





1. 旧 import 路径零残留：grep 全项目搜索旧路径，确认零结果


2. class/function 列表完整性：对比合并前后的 class/function 列表





参数（通过 check.params 传入）：


  - old_import_path: str — 旧 import 路径（如 "zephyr.data.telemetry"）


  - canonical_path: str — 真源路径（如 "zephyr.observability.telemetry"）


  - expected_classes: list[str] — 合并前 class 列表（用于完整性验证）


"""


import ast
import re
from pathlib import Path
from typing import Any

from zephyr.governance.rule_enforcement.check_types.check_type_registry import CheckTypeHandler, register_check_type
from zephyr.governance.rule_enforcement.task_types import Task


@register_check_type
class RestructuringSafetyHandler(CheckTypeHandler):
    name = "restructuring_safety"

    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []

        old_path = str(params.get("old_import_path", ""))

        canonical_path = str(params.get("canonical_path", ""))

        expected_classes = list(params.get("expected_classes", []))

        if old_path:
            residual = self._check_import_residual(old_path, project_root)

            for file_path, line_no, line_content in residual:
                violations.append(
                    {
                        "message": f"旧 import 残留: {file_path}:{line_no}: {line_content.strip()}",
                        "severity": "P0",
                        "detail": f"GOV-ENG-002 §3.3 #1: 旧路径 '{old_path}' 必须零残留",
                    }
                )

        if canonical_path and expected_classes:
            missing = self._check_class_completeness(canonical_path, expected_classes, project_root)

            for cls_name in missing:
                violations.append(
                    {
                        "message": f"class 缺失: {cls_name} 不在 {canonical_path} 中",
                        "severity": "P0",
                        "detail": "GOV-ENG-002 §3.3 #2: 合并后 class 列表必须完整",
                    }
                )

        if not old_path and not canonical_path:
            violations.append(
                {
                    "message": "restructuring_safety check 缺少 old_import_path 或 canonical_path 参数",
                    "severity": "P2",
                }
            )

        return violations

    def _check_import_residual(self, old_path: str, project_root: Any) -> list[tuple[str, int, str]]:
        root = Path(project_root) if not isinstance(project_root, Path) else project_root

        src_root = root / "src"

        if not src_root.exists():
            src_root = root

        results: list[tuple[str, int, str]] = []

        pattern_from = re.compile(rf"^\s*from\s+{re.escape(old_path)}\b", re.MULTILINE)

        pattern_import = re.compile(rf"^\s*import\s+{re.escape(old_path)}\b", re.MULTILINE)

        for py_file in src_root.rglob("*.py"):
            try:
                text = py_file.read_text(encoding="utf-8")

            except (UnicodeDecodeError, PermissionError):
                continue

            rel = str(py_file.relative_to(root))

            if "/test_" in rel or "\\test_" in rel:
                continue

            for i, line in enumerate(text.splitlines(), 1):
                if pattern_from.match(line) or pattern_import.match(line):
                    results.append((rel, i, line))

        return results

    def _check_class_completeness(
        self,
        canonical_path: str,
        expected_classes: list[str],
        project_root: Any,
    ) -> list[str]:
        root = Path(project_root) if not isinstance(project_root, Path) else project_root

        parts = canonical_path.split(".")

        if parts[0] == "zephyr":
            parts = parts[1:]

        py_file = root / "src" / "zephyr" / "/".join(parts[0:-1]) / (parts[-1] + ".py")

        if not py_file.exists():
            py_file = root / "src" / "zephyr" / "/".join(parts) / "__init__.py"

        if not py_file.exists():
            return expected_classes

        try:
            source = py_file.read_text(encoding="utf-8")

            tree = ast.parse(source)

        except (SyntaxError, UnicodeDecodeError):
            return expected_classes

        actual_classes = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                actual_classes.add(node.name)

        missing = [cls for cls in expected_classes if cls not in actual_classes]

        return missing
