# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.all_completer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-026(asset-inventory)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只添加缺失导出;不删除已有导出;不修改__all__顺序
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml all_completer段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AllCompletionError
# [TESTS] tests/auto-fix-engine/test_all_completer.py
# [A_module] module_id=MOD-INF_all_completer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import ast
import logging
import os
import re
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


class AllCompleter(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="all_completer",
            action_type="all_completion",
            level=FixLevel.L1_RULE,
            dimension="DIM-TYPE-001",
            description="补全 __all__ 缺失导出",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        for init_file in repo_root.rglob("__init__.py"):
            try:
                content = init_file.read_text(encoding="utf-8")
                if "__all__" not in content:
                    public_symbols = self._extract_public_symbols(content)
                    if public_symbols:
                        findings.append({"file": str(init_file), "missing": public_symbols, "type": "missing_all"})
                    continue
                declared = self._parse_all(content)
                actual = self._extract_public_symbols(content)
                missing = [s for s in actual if s not in declared]
                if missing:
                    findings.append({"file": str(init_file), "missing": missing, "type": "incomplete_all"})
            except Exception:
                continue
        return findings

    def _extract_public_symbols(self, content: str) -> list[str]:
        symbols: list[str] = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        symbols.append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            symbols.append(target.id)
        except SyntaxError:
            pass
        return sorted(set(symbols))

    def _parse_all(self, content: str) -> list[str]:
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, ast.List):
                                return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                return [elt.s for elt in node.value.elts if isinstance(elt, ast.Str)]
        except SyntaxError:
            pass
        return []

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
            public_symbols = self._extract_public_symbols(content)
            if not public_symbols:
                action.status = FixStatus.COMPLETED
                action.metadata["note"] = "No public symbols found"
                return action
            if "__all__" in content:
                declared = self._parse_all(content)
                missing = [s for s in public_symbols if s not in declared]
                if not missing:
                    action.status = FixStatus.COMPLETED
                    action.metadata["note"] = "No missing exports"
                    return action
                all_match = re.search(r"__all__\s*=\s*\[([^\]]*)\]", content)
                if all_match:
                    existing = all_match.group(1).strip()
                    new_entries = ", ".join(f'"{s}"' for s in missing)
                    replacement = f"__all__ = [{existing}, {new_entries}]" if existing else f"__all__ = [{new_entries}]"
                    content = content.replace(all_match.group(0), replacement)
            else:
                quoted = [f'"{s}"' for s in public_symbols]
                all_line = f"__all__ = [{', '.join(quoted)}]"
                lines = content.split("\n")
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith(("import ", "from ")):
                        insert_idx = i + 1
                lines.insert(insert_idx, all_line)
                content = "\n".join(lines)
            if content != original:
                action.before = original
                action.after = content
                if not dry_run:
                    tmp_path = f"{target}.{os.getpid()}.tmp"
                    try:
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        os.replace(tmp_path, target)
                    except PermissionError:
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
                        action.status = FixStatus.FAILED
                        return action
                action.status = FixStatus.COMPLETED
            else:
                action.status = FixStatus.COMPLETED
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="all_completion", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            if "__all__" not in content:
                return ValidationResult(
                    valid=False, check_name="all_completion", evidence="No __all__ found", error="__all__ missing"
                )
            declared = self._parse_all(content)
            actual = self._extract_public_symbols(content)
            missing = [s for s in actual if s not in declared]
            if missing:
                return ValidationResult(
                    valid=False, check_name="all_completion", evidence=f"Missing: {missing}", error="Incomplete __all__"
                )
            return ValidationResult(
                valid=True, check_name="all_completion", evidence=f"__all__ has {len(declared)} entries"
            )
        except Exception as exc:
            return ValidationResult(valid=False, check_name="all_completion", evidence="", error=str(exc))

    def rollback(self, target: str) -> bool:
        return False
