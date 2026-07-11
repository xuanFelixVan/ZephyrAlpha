# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.diff_detector
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/drift/test_diff_detector.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_diff_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Stage 0: Git diff 变更检测器 — 函数粒度增量.

职责：
  - 运行 `git diff --name-only --cached` 检测暂存区变更
  - 运行 `git diff --name-only` 检测工作区变更
  - 过滤出 .py 文件
  - AST 解析变更文件,提取新增/变更的函数（函数粒度而非文件粒度）
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChangedFunction:
    file: str
    name: str
    lineno: int
    end_lineno: int
    source: str = ""


@dataclass
class DiffResult:
    changed_files: list[str] = field(default_factory=list)
    changed_functions: list[ChangedFunction] = field(default_factory=list)
    staged_files: list[str] = field(default_factory=list)
    unstaged_files: list[str] = field(default_factory=list)


class DiffDetector:
    """Git diff 变更检测——函数粒度增量."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()

    # ── 公共 API ──────────────────────────────────────────────

    def detect(self) -> DiffResult:
        """检测所有变更——暂存区 + 工作区 -> 函数粒度."""
        staged = self._git_diff_files(cached=True)
        unstaged = self._git_diff_files(cached=False)
        all_files = sorted(set(staged + unstaged))

        py_files = [f for f in all_files if f.endswith(".py")]

        functions: list[ChangedFunction] = []
        for rel_path in py_files:
            abs_path = self._repo_root / rel_path
            if abs_path.exists():
                funcs = self._extract_functions(abs_path)
                for fn in funcs:
                    fn.file = rel_path
                    functions.append(fn)

        return DiffResult(
            changed_files=py_files,
            changed_functions=functions,
            staged_files=staged,
            unstaged_files=unstaged,
        )

    def detect_changed_files(self) -> list[str]:
        """仅返回变更的 .py 文件列表."""
        result = self.detect()
        return result.changed_files

    def detect_changed_functions(self) -> list[ChangedFunction]:
        """仅返回变更的函数列表."""
        result = self.detect()
        return result.changed_functions

    # ── 内部方法 ─────────────────────────────────────────────

    def _git_diff_files(self, cached: bool = False) -> list[str]:
        args = ["git", "diff", "--name-only"]
        if cached:
            args.append("--cached")
        try:
            output = subprocess.check_output(
                args,
                cwd=str(self._repo_root),
                encoding="utf-8",
                errors="replace",
            )
            return [line.strip() for line in output.splitlines() if line.strip()]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    @staticmethod
    def _extract_functions(file_path: Path) -> list[ChangedFunction]:
        """AST 解析——提取文件中所有顶层函数和方法."""
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError:
            return []

        functions: list[ChangedFunction] = []

        class _FunctionVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                end = node.end_lineno or node.lineno
                functions.append(
                    ChangedFunction(
                        file="",
                        name=node.name,
                        lineno=node.lineno,
                        end_lineno=end,
                        source=ast.get_source_segment(source, node) or "",
                    )
                )
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                end = node.end_lineno or node.lineno
                functions.append(
                    ChangedFunction(
                        file="",
                        name=node.name,
                        lineno=node.lineno,
                        end_lineno=end,
                        source=ast.get_source_segment(source, node) or "",
                    )
                )
                self.generic_visit(node)

        _FunctionVisitor().visit(tree)
        return functions
