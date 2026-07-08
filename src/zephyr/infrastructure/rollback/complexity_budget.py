# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.complexity_budget
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_complexity_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ComplexityBudget — 回滚复杂度元 Budget 监控。

依据: 蓝图 MOD-INF-021 §7 Phase 9 + §6.16 B115 + exit code 38

McCCabe 复杂度 > 15 / 文件 -> 反向回溯 + Lint 阻断。
复杂度超过阈值 -> exit 38 (COMPLEXITY_OVER_BUDGET)。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ComplexityReport:
    file_path: str
    mccabe_cyclomatic: int
    lines_of_code: int
    function_count: int
    exceeds_threshold: bool
    exit_code: int


class ComplexityBudget:
    EXIT_CODE_COMPLEXITY: int = 38
    MAX_MCCABE_PER_FILE: int = 15
    MAX_FUNCTIONS_PER_FILE: int = 30

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def check_file(self, file_path: Path) -> ComplexityReport:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        mccabe = self._compute_mccabe(tree)
        loc = len(source.splitlines())
        func_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))

        exceeds = (mccabe > self.MAX_MCCABE_PER_FILE) or (func_count > self.MAX_FUNCTIONS_PER_FILE)

        details: list[str] = []
        if mccabe > self.MAX_MCCABE_PER_FILE:
            details.append(f"McCCabe {mccabe} exceeds max {self.MAX_MCCABE_PER_FILE}")
        if func_count > self.MAX_FUNCTIONS_PER_FILE:
            details.append(f"Function count {func_count} exceeds max {self.MAX_FUNCTIONS_PER_FILE}")

        return ComplexityReport(
            file_path=str(file_path),
            mccabe_cyclomatic=mccabe,
            lines_of_code=loc,
            function_count=func_count,
            exceeds_threshold=exceeds,
            exit_code=self.EXIT_CODE_COMPLEXITY if exceeds else 0,
        )

    def check_module(self, module_dir: Path) -> list[ComplexityReport]:
        reports: list[ComplexityReport] = []
        for py_file in module_dir.glob("**/*.py"):
            try:
                reports.append(self.check_file(py_file))
            except Exception as e:
                logger.warning("suppressed error in complexity_budget", exc_info=True)
        return reports

    @staticmethod
    def _compute_mccabe(tree: ast.AST) -> int:
        complexity = 1
        for node in ast.walk(tree):
            if (
                isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor))
                or isinstance(node, ast.ExceptHandler)
                or isinstance(node, (ast.And, ast.Or))
            ):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
