# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.quality.quality_monitor
# [DOMAIN] D_INFRA_RUNTIME
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
# [A_module] module_id=MOD-INF_quality_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Quality Monitor — 生成代码质量门禁。

依据：
    蓝图 MOD-TASK_SYSTEM §6.9 + v0.6.0
    任务卡 TASK-INF-0114
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class QualityMetric:
    name: str
    value: float
    threshold: float
    passed: bool


@dataclass
class CodeQualityReport:
    file_path: str
    overall_score: float
    metrics: list[QualityMetric]
    issues: list[str]
    passed: bool


class QualityMonitor:
    MAX_LINE_LENGTH = 150
    MAX_FUNCTION_LENGTH = 200
    MIN_DOCSTRING_COVERAGE = 0.5

    def analyze_file(self, file_path: str, project_root: Path | None = None) -> CodeQualityReport:
        root = project_root or Path.cwd()
        full_path = root / file_path

        if not full_path.exists():
            return CodeQualityReport(
                file_path=file_path,
                overall_score=0.0,
                metrics=[],
                issues=["File not found"],
                passed=False,
            )

        content = full_path.read_text(encoding="utf-8")

        metrics: list[QualityMetric] = []
        issues: list[str] = []

        metrics.append(self._check_line_length(content, issues))
        metrics.append(self._check_imports(content, issues))

        try:
            tree = ast.parse(content)
            metrics.append(self._check_function_length(tree, issues))
            metrics.append(self._check_docstrings(tree, issues))
            metrics.append(self._check_naming(content, issues))
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")

        passed = all(m.passed for m in metrics)
        overall = sum(m.value for m in metrics) / max(len(metrics), 1)

        return CodeQualityReport(
            file_path=file_path,
            overall_score=round(overall, 2),
            metrics=metrics,
            issues=issues,
            passed=passed,
        )

    def validate_python_file(self, file_path: str, project_root: Path | None = None) -> tuple[bool, CodeQualityReport]:
        report = self.analyze_file(file_path, project_root)
        return report.passed, report

    def _check_line_length(self, content: str, issues: list[str]) -> QualityMetric:
        long_lines = 0
        total = 0
        for line in content.split("\n"):
            total += 1
            if len(line) > self.MAX_LINE_LENGTH:
                long_lines += 1

        ratio = long_lines / max(total, 1)
        passed = ratio < 0.1

        if long_lines > 0:
            issues.append(f"{long_lines} lines exceed {self.MAX_LINE_LENGTH} chars")

        return QualityMetric(
            name="line_length",
            value=round(ratio, 3),
            threshold=0.1,
            passed=passed,
        )

    def _check_imports(self, content: str, issues: list[str]) -> QualityMetric:
        wildcard_imports = len(re.findall(r"from\s+[\w.]+\s+import\s+\*", content))
        passed = wildcard_imports == 0

        if wildcard_imports > 0:
            issues.append(f"{wildcard_imports} wildcard import(s) detected")

        return QualityMetric(
            name="imports",
            value=0.0 if wildcard_imports == 0 else 1.0,
            threshold=0.0,
            passed=passed,
        )

    def _check_function_length(self, tree: ast.AST, issues: list[str]) -> QualityMetric:
        long_funcs = 0
        total = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                total += 1
                if node.end_lineno and node.lineno:
                    length = node.end_lineno - node.lineno
                    if length > self.MAX_FUNCTION_LENGTH:
                        long_funcs += 1
                        issues.append(f"Function {node.name} is {length} lines")

        ratio = long_funcs / max(total, 1)
        passed = ratio < 0.1

        return QualityMetric(
            name="function_length",
            value=round(ratio, 3),
            threshold=0.1,
            passed=passed,
        )

    def _check_docstrings(self, tree: ast.AST, issues: list[str]) -> QualityMetric:
        with_docstring = 0
        total = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                total += 1
                if ast.get_docstring(node):
                    with_docstring += 1

        ratio = with_docstring / max(total, 1)
        passed = ratio >= self.MIN_DOCSTRING_COVERAGE

        if not passed:
            issues.append(f"Docstring coverage: {ratio:.0%} < {self.MIN_DOCSTRING_COVERAGE:.0%}")

        return QualityMetric(
            name="docstrings",
            value=round(ratio, 3),
            threshold=self.MIN_DOCSTRING_COVERAGE,
            passed=passed,
        )

    def _check_naming(self, content: str, issues: list[str]) -> QualityMetric:
        snake_violations = len(re.findall(r"def\s+[a-z]+[A-Z]", content))
        passed = snake_violations == 0

        if snake_violations > 0:
            issues.append(f"{snake_violations} function(s) not snake_case")

        return QualityMetric(
            name="naming",
            value=0.0 if passed else 1.0,
            threshold=0.0,
            passed=passed,
        )
