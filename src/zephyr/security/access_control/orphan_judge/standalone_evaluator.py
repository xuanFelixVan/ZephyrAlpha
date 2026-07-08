# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §L4
# [MODULE] zephyr.security.access_control.orphan_judge.standalone_evaluator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS] orphan-judge.judge._run_layer L4
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 六指标加权评分; score≥0.5 -> has_value=True; 不修改任何文件
# [MODIFY-GUARD] 修改评分权重必须同步 blueprint.md §3.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件不可读时返回 has_value=False+is_uncertain=True,不抛异常
# [TESTS] tests/orphan-judge/test_standalone_evaluator.py
# [A_module] module_id=MOD-SEC_standalone_evaluator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-029 — L4 独立价值评估器

六指标加权评分: 文件大小(15%) + 代码行数(20%) + 定义数(20%)
+ 文档注释(10%) + 测试存在(10%) + 导入复杂度(25%)
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from zephyr.security.access_control.orphan_judge.judge import LayerResult

logger = logging.getLogger(__name__)

__all__ = [
    "StandaloneEvaluator",
]

_INDICATOR_WEIGHTS = {
    "file_size": 0.15,
    "code_lines": 0.20,
    "definition_count": 0.20,
    "docstring_ratio": 0.10,
    "test_exists": 0.10,
    "import_depth": 0.25,
}
_VALUE_THRESHOLD = 0.5
_SIZE_KB_THRESHOLD = 50
_MIN_LINES = 20
_MIN_DEFS = 3
_MAX_IMPORTS = 15


class StandaloneEvaluator:
    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()

    def check(self, path: str) -> LayerResult:
        file_path = self._root / path
        if not file_path.exists():
            return LayerResult(
                layer="L4",
                passed=False,
                detail="File not found, defaulting to no value",
                data={"has_value": False, "is_uncertain": True, "value_confidence": "low"},
            )

        try:
            content = file_path.read_text(encoding="utf-8")
            size_kb = file_path.stat().st_size / 1024.0
        except (OSError, UnicodeDecodeError):
            return LayerResult(
                layer="L4",
                passed=False,
                detail="File unreadable, defaulting to no value",
                data={"has_value": False, "is_uncertain": True, "value_confidence": "low"},
            )

        lines = [l for l in content.split("\n") if l.strip()]
        code_lines = len(lines)
        size_score = min(size_kb / _SIZE_KB_THRESHOLD, 1.0)
        lines_score = min(code_lines / (_MIN_LINES * 10), 1.0)

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return LayerResult(
                layer="L4",
                passed=False,
                detail="Syntax error in file",
                data={"has_value": False, "is_uncertain": False, "value_confidence": "low"},
            )

        def_count = 0
        imports_count = 0
        has_docstring = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                def_count += 1
                if ast.get_docstring(node):
                    has_docstring = True
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports_count += 1

        def_score = min(def_count / _MIN_DEFS, 1.0)
        doc_score = 1.0 if has_docstring else 0.0
        import_score = min(imports_count / _MAX_IMPORTS, 1.0)

        has_test = self._check_test_exists(file_path)
        test_score = 1.0 if has_test else 0.0

        indicators = {
            "file_size_kb": size_kb,
            "code_lines": code_lines,
            "definition_count": def_count,
            "has_docstring": has_docstring,
            "test_exists": has_test,
            "import_count": imports_count,
        }

        score = (
            size_score * _INDICATOR_WEIGHTS["file_size"]
            + lines_score * _INDICATOR_WEIGHTS["code_lines"]
            + def_score * _INDICATOR_WEIGHTS["definition_count"]
            + doc_score * _INDICATOR_WEIGHTS["docstring_ratio"]
            + test_score * _INDICATOR_WEIGHTS["test_exists"]
            + import_score * _INDICATOR_WEIGHTS["import_depth"]
        )

        has_value = score >= _VALUE_THRESHOLD
        if score >= 0.7:
            confidence = "high"
        elif score >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        return LayerResult(
            layer="L4",
            passed=has_value,
            detail=f"Value score: {score:.2f} (threshold={_VALUE_THRESHOLD})",
            data={
                "has_value": has_value,
                "is_uncertain": False,
                "value_confidence": confidence,
                "score": score,
                "indicators": indicators,
            },
        )

    def _check_test_exists(self, file_path: Path) -> bool:
        stem = file_path.stem
        test_name = f"test_{stem}.py"
        tests_dir = self._root / "tests"
        if not tests_dir.exists():
            return False
        for test_file in tests_dir.rglob("*.py"):
            if test_file.name == test_name:
                return True
            try:
                content = test_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if stem in content:
                return True
        return False
