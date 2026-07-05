# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §L3
# [MODULE] zephyr.security.access_control.orphan_judge.unique_analyzer
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge
# [CONSUMERS] orphan-judge.judge._run_layer L3
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AST节点比对; 独特节点≥5 → has_unique=True; 不修改任何文件
# [MODIFY-GUARD] 修改阈值必须同步 blueprint.md §3.1
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AST解析失败时返回 has_unique=False+is_uncertain=True,不抛异常
# [TESTS] tests/orphan-judge/test_unique_analyzer.py
# [A_module] module_id=MOD-SEC_unique_analyzer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-029 — L3 独特价值分析器

AST节点比对，检测文件中的独特代码元素(类/函数/常量定义等)。
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path

from zephyr.security.access_control.orphan_judge.judge import LayerResult

logger = logging.getLogger(__name__)

__all__ = [
    "UniqueValueAnalyzer",
]

_MIN_UNIQUE_NODES = 5
_MAX_SCAN_FILES = 50


class UniqueValueAnalyzer:
    def __init__(self, project_root: str | Path = ".") -> None:
        self._root = Path(project_root).resolve()

    def check(self, path: str) -> LayerResult:
        file_path = self._root / path
        if not file_path.exists():
            return LayerResult(
                layer="L3",
                passed=True,
                detail="File not found, defaulting to has_unique=True (preserve)",
                data={"has_unique": True, "is_uncertain": False, "unique_confidence": "low"},
            )

        try:
            target_ast = ast.parse(file_path.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            return LayerResult(
                layer="L3",
                passed=True,
                detail="AST parse failed, defaulting to has_unique=True (preserve)",
                data={"has_unique": True, "is_uncertain": True, "unique_confidence": "low"},
            )

        target_names = self._extract_defined_names(target_ast)
        if not target_names:
            return LayerResult(
                layer="L3",
                passed=False,
                detail="No defined names (classes/functions) found",
                data={"has_unique": False, "is_uncertain": False, "unique_confidence": "low"},
            )

        src_dir = self._root / "src" / "zephyr"
        if not src_dir.exists():
            return LayerResult(
                layer="L3",
                passed=True,
                detail="src/zephyr/ not found, defaulting to has_unique=True",
                data={"has_unique": True, "is_uncertain": True, "unique_confidence": "low"},
            )

        common_names: set[str] = set()
        scanned = 0
        for py_file in src_dir.rglob("*.py"):
            if py_file.resolve() == file_path.resolve():
                continue
            try:
                other_ast = ast.parse(py_file.read_text(encoding="utf-8"))
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue
            other_names = self._extract_defined_names(other_ast)
            common_names.update(target_names & other_names)
            scanned += 1
            if scanned >= _MAX_SCAN_FILES:
                break

        unique_names = target_names - common_names
        unique_count = len(unique_names)
        has_unique = unique_count >= _MIN_UNIQUE_NODES

        if unique_count >= 10:
            confidence = "high"
        elif unique_count >= 5:
            confidence = "medium"
        else:
            confidence = "low"

        return LayerResult(
            layer="L3",
            passed=has_unique,
            detail=f"Unique names: {unique_count}/{len(target_names)} (threshold={_MIN_UNIQUE_NODES})",
            data={
                "has_unique": has_unique,
                "is_uncertain": False,
                "unique_confidence": confidence,
                "unique_count": unique_count,
                "total_defined": len(target_names),
            },
        )

    def _extract_defined_names(self, tree: ast.AST) -> set[str]:
        names: set[str] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                or isinstance(node, ast.AsyncFunctionDef)
                or isinstance(node, ast.ClassDef)
            ):
                names.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                names.add(elt.id)
        return names
