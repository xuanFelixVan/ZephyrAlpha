# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.config_fixer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-023(drift-detector)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配置为SSoT;只修复合并冲突标记和格式问题;不改变配置语义
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml config_fixer段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConfigFixError
# [TESTS] tests/auto-fix-engine/test_config_fixer.py
# [A_module] module_id=MOD-INF_config_fixer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

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


class ConfigFixer(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="config_fixer",
            action_type="config_fix",
            level=FixLevel.L1_RULE,
            dimension="DIM-DRIFT-001",
            description="修复配置与契约不一致",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        for config_file in repo_root.rglob("*.yaml"):
            if ".ailocks" in str(config_file) or "node_modules" in str(config_file):
                continue
            try:
                content = config_file.read_text(encoding="utf-8")
                if "<<<<<<< " in content or "=======" in content or ">>>>>>> " in content:
                    findings.append(
                        {
                            "file": str(config_file),
                            "type": "merge_conflict_markers",
                        }
                    )
                tab_lines = [
                    i + 1
                    for i, line in enumerate(content.splitlines())
                    if "\t" in line and not line.strip().startswith("#")
                ]
                if tab_lines:
                    findings.append(
                        {
                            "file": str(config_file),
                            "lines": tab_lines[:10],
                            "type": "tab_indentation",
                        }
                    )
                trailing_ws = [
                    i + 1 for i, line in enumerate(content.splitlines()) if line.rstrip() != line and line.strip()
                ]
                if len(trailing_ws) > 5:
                    findings.append(
                        {
                            "file": str(config_file),
                            "count": len(trailing_ws),
                            "type": "trailing_whitespace",
                        }
                    )
            except Exception:
                continue
        return findings

    def fix(self, target: str, dry_run: bool = False) -> FixAction:
        action = FixAction(
            action_type=self.action_type,
            level=self.level,
            target=target,
            confidence=FixConfidence.MEDIUM,
        )
        target_path = Path(target)
        if not target_path.exists():
            action.status = FixStatus.FAILED
            action.metadata["error"] = "Target not found"
            return action
        try:
            content = target_path.read_text(encoding="utf-8")
            original = content
            fixes: list[str] = []
            content = self._fix_merge_conflicts(content, fixes)
            content = self._fix_tabs(content, fixes)
            content = self._fix_trailing_whitespace(content, fixes)
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
                action.metadata["note"] = "No config issues found"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def _fix_merge_conflicts(self, content: str, fixes: list[str]) -> str:
        if "<<<<<<< " not in content:
            return content
        pattern = re.compile(
            r"<<<<<<< .+?\n(.*?)=======\n(.*?)>>>>>>> .+?\n",
            re.DOTALL,
        )
        count = 0

        def _resolve(match: re.Match) -> str:
            nonlocal count
            ours = match.group(1)
            theirs = match.group(2)
            count += 1
            if len(ours.strip()) >= len(theirs.strip()):
                fixes.append(f"Merge conflict {count}: kept ours")
                return ours
            fixes.append(f"Merge conflict {count}: kept theirs")
            return theirs

        content = pattern.sub(_resolve, content)
        return content

    def _fix_tabs(self, content: str, fixes: list[str]) -> str:
        lines = content.split("\n")
        fixed = 0
        new_lines: list[str] = []
        for line in lines:
            if "\t" in line and not line.strip().startswith("#"):
                new_line = line.replace("\t", "    ")
                if new_line != line:
                    fixed += 1
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        if fixed > 0:
            fixes.append(f"Fixed {fixed} tab-indented lines")
        return "\n".join(new_lines)

    def _fix_trailing_whitespace(self, content: str, fixes: list[str]) -> str:
        lines = content.split("\n")
        fixed = 0
        new_lines: list[str] = []
        for line in lines:
            if line.rstrip() != line and line.strip():
                new_lines.append(line.rstrip())
                fixed += 1
            else:
                new_lines.append(line)
        if fixed > 0:
            fixes.append(f"Fixed {fixed} trailing whitespace lines")
        return "\n".join(new_lines)

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="config_fix", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            if "<<<<<<< " in content:
                return ValidationResult(
                    valid=False,
                    check_name="config_fix",
                    evidence="Merge conflict markers present",
                    error="Unresolved merge conflicts",
                )
            try:
                import yaml

                yaml.safe_load(content)
            except yaml.YAMLError as exc:
                return ValidationResult(
                    valid=False, check_name="config_fix", evidence="", error=f"YAML parse error: {exc}"
                )
            return ValidationResult(valid=True, check_name="config_fix", evidence="YAML valid, no merge conflicts")
        except Exception as exc:
            return ValidationResult(valid=False, check_name="config_fix", evidence="", error=str(exc))

    def rollback(self, target: str) -> bool:
        return False
