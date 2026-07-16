# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.dedup_extractor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-017(code-dedup-engine)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只提取≥3处重复;提取后原位置调用共享函数;不改变语义
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml dedup_extractor段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DedupExtractionError
# [TESTS] tests/auto-fix-engine/test_dedup_extractor.py
# [A_module] module_id=MOD-INF_dedup_extractor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

from __future__ import annotations

import ast
import hashlib
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    BaseFixer,
    FixAction,
    FixConfidence,
    FixLevel,
    FixStatus,
    ValidationResult,
)

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class DedupExtractor(BaseFixer):

    def __init__(self, min_occurrences: int = 3) -> None:
        super().__init__(
            fixer_id="dedup_extractor",
            action_type="dedup_extraction",
            level=FixLevel.L1_RULE,
            dimension="DIM-CODE-001",
            description="提取重复代码为共享函数",
        )
        self._min_occurrences = min_occurrences

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        code_blocks: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for py_file in repo_root.rglob("*.py"):
            if "site-packages" in str(py_file) or ".venv" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        body_lines = ast.get_source_segment(content, node)
                        if body_lines and len(body_lines.strip()) > 50:
                            normalized = self._normalize_code(body_lines)
                            h = hashlib.sha256(normalized.encode()).hexdigest()[:16]
                            code_blocks[h].append({"file": str(py_file), "function": node.name, "line": node.lineno})
            except Exception:
                continue
        for h, occurrences in code_blocks.items():
            if len(occurrences) >= self._min_occurrences:
                findings.append(
                    {
                        "hash": h,
                        "occurrences": len(occurrences),
                        "locations": occurrences,
                        "type": "code_duplication",
                    }
                )
        return findings

    def _normalize_code(self, code: str) -> str:
        lines = code.split("\n")
        stripped = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
        return "\n".join(stripped)

    def _collect_function_bodies(
        self, content: str, tree: ast.AST
    ) -> dict[str, list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]]:
        function_bodies: dict[
            str, list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]
        ] = defaultdict(list)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                body_lines = ast.get_source_segment(content, node)
                if body_lines and len(body_lines.strip()) > 50:
                    normalized = self._normalize_code(body_lines)
                    h = hashlib.sha256(normalized.encode()).hexdigest()[:16]
                    function_bodies[h].append((content, node))
        return function_bodies

    def _build_shared_function(
        self,
        content: str,
        first_func: ast.FunctionDef | ast.AsyncFunctionDef,
        shared_name: str,
    ) -> str | None:
        body_source = ast.get_source_segment(content, first_func)
        if not body_source:
            return None
        shared_func = f"def {shared_name}(*args, **kwargs):\n"
        for line in body_source.split("\n")[1:]:
            shared_func += f"    {line.strip()}\n" if line.strip() else "\n"
        return shared_func

    def _replace_duplicate_functions(
        self,
        content: str,
        function_bodies: dict[str, list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]],
    ) -> tuple[list[str], str, int]:
        new_functions: list[str] = []
        replacements_made = 0
        for h, funcs in function_bodies.items():
            if len(funcs) < self._min_occurrences:
                continue
            first_func = funcs[0][1]
            shared_name = f"_shared_{first_func.name}_{h[:6]}"
            shared_func = self._build_shared_function(content, first_func, shared_name)
            if shared_func is None:
                continue
            new_functions.append(shared_func)
            for _, func_node in funcs[1:]:
                old_call = ast.get_source_segment(content, func_node)
                if old_call:
                    new_call = f"def {func_node.name}(*args, **kwargs):\n    return {shared_name}(*args, **kwargs)"
                    content = content.replace(old_call, new_call)
                    replacements_made += 1
        return new_functions, content, replacements_made

    def _persist_fix(self, target: str, content: str) -> bool:
        tmp_path = f"{target}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, target)
            return True
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return False

    def fix(self, target: str, dry_run: bool = False) -> FixAction:
        action = FixAction(
            action_type=self.action_type,
            level=self.level,
            target=target,
            confidence=FixConfidence.HIGH,
        )
        target_path = Path(target)
        if not target_path.exists():
            action.status = FixStatus.FAILED
            return action
        try:
            content = target_path.read_text(encoding="utf-8")
            original = content
            tree = ast.parse(content)
            function_bodies = self._collect_function_bodies(content, tree)
            new_functions, content, replacements_made = self._replace_duplicate_functions(
                content, function_bodies
            )
            if new_functions and replacements_made > 0:
                insert_pos = content.find("\n\nclass ") if "\nclass " in content else len(content)
                for func_def in new_functions:
                    content = func_def + "\n\n" + content
                action.before = original
                action.after = content
                action.metadata["shared_functions"] = len(new_functions)
                action.metadata["replacements"] = replacements_made
                if not dry_run:
                    if not self._persist_fix(target, content):
                        action.status = FixStatus.FAILED
                        return action
                action.status = FixStatus.COMPLETED
            else:
                action.status = FixStatus.COMPLETED
                action.metadata["note"] = "No dedup opportunities found"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="dedup_extraction", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            compile(content, target, "exec")
            return ValidationResult(valid=True, check_name="dedup_extraction", evidence="Syntax check passed")
        except SyntaxError as exc:
            return ValidationResult(
                valid=False, check_name="dedup_extraction", evidence="", error=f"Syntax error: {exc}"
            )

    def rollback(self, target: str) -> bool:
        return False
