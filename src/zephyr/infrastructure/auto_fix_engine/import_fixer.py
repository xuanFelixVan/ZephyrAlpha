# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.import_fixer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只修复可确定正确路径的import;不确定则跳过
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml import_fixer段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportFixError
# [TESTS] tests/auto-fix-engine/test_import_fixer.py
# [A_module] module_id=MOD-INF_import_fixer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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


def _is_scan_excluded(py_file: Path) -> bool:
    s = str(py_file)
    return "site-packages" in s or ".venv" in s


def _check_import_from_node(
    node: ast.ImportFrom, src_root: Path, py_file: Path
) -> dict[str, Any] | None:
    if not node.module or not node.module.startswith("zephyr."):
        return None
    parts = node.module.split(".")
    if len(parts) < 2:
        return None
    pkg_path = src_root / Path(*parts[:-1]) if len(parts) > 2 else src_root / parts[0]
    init_file = pkg_path / "__init__.py"
    if init_file.exists() or (src_root / Path(*parts)).exists():
        return None
    return {
        "file": str(py_file),
        "line": node.lineno,
        "module": node.module,
        "type": "broken_import",
    }


def _check_import_node(
    node: ast.Import, src_root: Path, py_file: Path
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for alias in node.names:
        if not alias.name.startswith("zephyr."):
            continue
        parts = alias.name.split(".")
        mod_path = src_root / Path(*parts) / "__init__.py"
        if mod_path.exists():
            continue
        mod_path2 = src_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
        if mod_path2.exists():
            continue
        findings.append(
            {
                "file": str(py_file),
                "line": node.lineno,
                "module": alias.name,
                "type": "broken_import",
            }
        )
    return findings


def _scan_file_imports(py_file: Path, src_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    try:
        content = py_file.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                finding = _check_import_from_node(node, src_root, py_file)
                if finding:
                    findings.append(finding)
            elif isinstance(node, ast.Import):
                findings.extend(_check_import_node(node, src_root, py_file))
    except Exception:
        pass
    return findings


class ImportFixer(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="import_fixer",
            action_type="import_fix",
            level=FixLevel.L1_RULE,
            dimension="DIM-CODE-001",
            description="修复损坏 import",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        src_root = REPO_ROOT / "src"  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        for py_file in REPO_ROOT.rglob("*.py"):
            if _is_scan_excluded(py_file):
                continue
            findings.extend(_scan_file_imports(py_file, src_root))
        return findings

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
            repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            src_root = repo_root / "src"
            fixes: list[str] = []
            lines = content.split("\n")
            new_lines: list[str] = []
            for line in lines:
                stripped = line.strip()
                fixed_line = line
                from_match = re.match(r"^(\s*)from\s+(zephyr[\.\w]*)\s+import", stripped)
                if from_match:
                    indent = from_match.group(1)
                    module = from_match.group(2)
                    corrected = self._try_fix_module(module, src_root)
                    if corrected and corrected != module:
                        fixed_line = line.replace(f"from {module}", f"from {corrected}")
                        fixes.append(f"{module} -> {corrected}")
                import_match = re.match(r"^(\s*)import\s+(zephyr[\.\w]*)", stripped)
                if import_match and not from_match:
                    module = import_match.group(2)
                    corrected = self._try_fix_module(module, src_root)
                    if corrected and corrected != module:
                        fixed_line = line.replace(f"import {module}", f"import {corrected}")
                        fixes.append(f"{module} -> {corrected}")
                new_lines.append(fixed_line)
            content = "\n".join(new_lines)
            if content != original:
                action.before = original
                action.after = content
                action.metadata["fixes"] = fixes
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
                action.metadata["note"] = "No broken imports found"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def _try_fix_module(self, module: str, src_root: Path) -> str | None:
        parts = module.split(".")
        if len(parts) < 2:
            return None
        candidates: list[str] = []
        for i in range(len(parts), 1, -1):
            prefix = ".".join(parts[:i])
            suffix = parts[i:] if i < len(parts) else []
            pkg_path = src_root / Path(*parts[:i])
            if (pkg_path / "__init__.py").exists() or (
                src_root / Path(*parts[: i - 1]) / f"{parts[i - 1]}.py"
            ).exists():
                if not suffix:
                    candidates.append(prefix)
                else:
                    candidates.append(prefix)
                break
        if not candidates:
            for i in range(len(parts) - 1, 1, -1):
                prefix = ".".join(parts[:i])
                pkg_path = src_root / Path(*parts[:i])
                if (pkg_path / "__init__.py").exists():
                    candidates.append(prefix)
                    break
        return candidates[0] if candidates else None

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="import_fix", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            compile(content, target, "exec")
            return ValidationResult(valid=True, check_name="import_fix", evidence="Syntax check passed")
        except SyntaxError as exc:
            return ValidationResult(valid=False, check_name="import_fix", evidence="", error=f"Syntax error: {exc}")

    def rollback(self, target: str) -> bool:
        return False
