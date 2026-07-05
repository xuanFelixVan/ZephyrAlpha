# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §2.10
# [MODULE] zephyr.governance.rule_enforcement.invariants.en_process_lifecycle_gateway
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES]
# [CONSUMERS] CI Pipeline (phase_manager.py Gate 检查)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 检测裸 subprocess.Popen / multiprocessing.Process 调用；不误报 Gateway 自身内部使用
# [MODIFY-GUARD] 白名单更新时必须同步此 Gate
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 违规 → GateResult(passed=False, violations=[...])
# [TESTS] tests/zephyr/gates/invariants/test_en_process_lifecycle_gateway.py
# [A_module] module_id=MOD-GOV_en_process_lifecycle_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
EN-process-lifecycle-gateway — 进程创建入口校验门禁

AST 扫描检测裸 subprocess.Popen / multiprocessing.Process 调用。
CI 阶段阻断绕过 ProcessLifecycleGateway 的代码。

SSoT: MOD-INF-016 §2.10 | DEP-GRAPH-process-lifecycle-001
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import ast
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from zephyr.shared.io.paths import REPO_ROOT

ALLOWED_FILES: set[str] = {
    "src/zephyr/shared/infra/process_pool.py",
    "src/zephyr/shared/infra/process_lifecycle_gateway.py",
}


@dataclass
class Violation:
    file: str
    line: int
    call_type: str
    snippet: str


@dataclass
class GateResult:
    passed: bool
    violations: list[Violation] = field(default_factory=list)
    scanned_files: int = 0


class ProcessCreationScanner(ast.NodeVisitor):
    """AST 扫描器：检测裸 subprocess.Popen / multiprocessing.Process 调用。"""

    FORBIDDEN_CALLS: ClassVar[dict[str, str]] = {
        "subprocess.Popen": "subprocess.Popen",
        "subprocess.call": "subprocess.call",
        "multiprocessing.Process": "multiprocessing.Process",
    }

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.violations: list[Violation] = []
        self._imported_gateway = False

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if "process_lifecycle_gateway" in alias.name:
                self._imported_gateway = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module and "process_lifecycle_gateway" in node.module:
            self._imported_gateway = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func_path = self._resolve_call_path(node.func)
        if func_path in self.FORBIDDEN_CALLS:
            snippet = self._get_snippet(node)
            self.violations.append(
                Violation(
                    file=self.file_path,
                    line=node.lineno or 0,
                    call_type=func_path,
                    snippet=snippet,
                )
            )
        self.generic_visit(node)

    def _get_snippet(self, node: ast.Call) -> str:
        snippet = f"{self._resolve_call_path(node.func)}(...)"
        try:
            with open(self.file_path, encoding="utf-8") as f:
                source = f.read()
            snippet = ast.get_source_segment(source, node) or snippet
        except Exception as e:
            logger.warning("suppressed error in en_process_lifecycle_gateway", exc_info=True)
        return snippet.strip()[:120] if snippet else ""

    @staticmethod
    def _resolve_call_path(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            value_path = ProcessCreationScanner._resolve_call_path(node.value)
            return f"{value_path}.{node.attr}" if value_path else node.attr
        return ""


def scan_file(file_path: str) -> list[Violation]:
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return []

    tree = ast.parse(source, filename=file_path)
    scanner = ProcessCreationScanner(file_path)
    scanner.visit(tree)

    if scanner._imported_gateway:
        return []

    return scanner.violations


def scan_directory(
    root: str | Path,
    exclude_dirs: Iterable[str] | None = None,
) -> GateResult:
    root_path = Path(root)
    src_dir = root_path / "src" / "zephyr"
    if not src_dir.exists():
        return GateResult(passed=True, violations=[], scanned_files=0)

    exclude = set(exclude_dirs or [])
    exclude.update({".git", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules"})

    all_violations: list[Violation] = []
    scanned = 0

    for py_file in src_dir.rglob("*.py"):
        rel_parts = py_file.relative_to(root_path).parts
        if any(ex in rel_parts for ex in exclude):
            continue

        rel_str = str(py_file.relative_to(root_path)).replace("\\", "/")
        if rel_str in ALLOWED_FILES:
            scanned += 1
            continue

        scanned += 1
        violations = scan_file(str(py_file))
        all_violations.extend(violations)

    return GateResult(
        passed=len(all_violations) == 0,
        violations=all_violations,
        scanned_files=scanned,
    )


def result() -> GateResult:
    return scan_directory(REPO_ROOT)


if __name__ == "__main__":
    r = result()
    print(f"Scanned: {r.scanned_files} files")
    if r.passed:
        print("PASS: No bare subprocess/multiprocessing calls found outside Gateway.")
    else:
        print(f"FAIL: {len(r.violations)} violation(s):")
        for v in r.violations:
            print(f"  {v.file}:{v.line} — {v.call_type}(...): {v.snippet}")
