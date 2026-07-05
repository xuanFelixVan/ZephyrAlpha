# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.zombie_cleaner
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-026(asset-inventory)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只清理指向不存在文件的引用;不删除文件本身
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml zombie_cleaner段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ZombieCleanError
# [TESTS] tests/auto-fix-engine/test_zombie_cleaner.py
# [A_module] module_id=MOD-INF_zombie_cleaner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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


class ZombieCleaner(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="zombie_cleaner",
            action_type="zombie_cleanup",
            level=FixLevel.L1_RULE,
            dimension="DIM-PATH-001",
            description="清理指向不存在文件的引用",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        for yaml_file in repo_root.rglob("*.yaml"):
            try:
                content = yaml_file.read_text(encoding="utf-8")
                path_refs = re.findall(
                    r'(?:path|file|src|location)\s*[:=]\s*["\']?([^\s"\'\]]+\.(?:py|yaml|json|md))["\']?', content
                )
                for ref in path_refs:
                    if not (repo_root / ref).exists() and not Path(ref).is_absolute():
                        findings.append({"file": str(yaml_file), "reference": ref, "type": "zombie_reference"})
            except Exception:
                continue
        for py_file in repo_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                path_refs = re.findall(r'["\']([A-Za-z0-9_/\\]+\.(?:py|yaml|json))["\']', content)
                for ref in path_refs:
                    clean_ref = ref.replace("\\", "/")
                    if not (repo_root / clean_ref).exists() and not Path(clean_ref).is_absolute():
                        if "site-packages" not in clean_ref and "lib/python" not in clean_ref:
                            findings.append({"file": str(py_file), "reference": clean_ref, "type": "zombie_import"})
            except Exception:
                continue
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
            action.metadata["error"] = "Target file not found"
            return action
        try:
            content = target_path.read_text(encoding="utf-8")
            original = content
            repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            if target.endswith(".yaml"):
                path_refs = re.findall(
                    r'(?:path|file|src|location)\s*[:=]\s*["\']?([^\s"\'\]]+\.(?:py|yaml|json|md))["\']?', content
                )
                for ref in path_refs:
                    if not (repo_root / ref).exists() and not Path(ref).is_absolute():
                        lines = content.split("\n")
                        new_lines = [l for l in lines if ref not in l]
                        content = "\n".join(new_lines)
            elif target.endswith(".py"):
                path_refs = re.findall(r'["\']([A-Za-z0-9_/\\]+\.(?:py|yaml|json))["\']', content)
                for ref in path_refs:
                    clean_ref = ref.replace("\\", "/")
                    if not (repo_root / clean_ref).exists() and not Path(ref).is_absolute():
                        if "site-packages" not in clean_ref and "lib/python" not in clean_ref:
                            lines = content.split("\n")
                            new_lines = [l for l in lines if ref not in l]
                            content = "\n".join(new_lines)
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
                action.metadata["note"] = "No zombie references found"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(valid=False, check_name="zombie_clean", evidence="", error="Target not found")
        try:
            content = target_path.read_text(encoding="utf-8")
            repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            remaining_zombies: list[str] = []
            path_refs = re.findall(r'["\']([A-Za-z0-9_/\\]+\.(?:py|yaml|json))["\']', content)
            for ref in path_refs:
                clean_ref = ref.replace("\\", "/")
                if not (repo_root / clean_ref).exists() and not Path(ref).is_absolute():
                    if "site-packages" not in clean_ref and "lib/python" not in clean_ref:
                        remaining_zombies.append(ref)
            if remaining_zombies:
                return ValidationResult(
                    valid=False,
                    check_name="zombie_clean",
                    evidence=f"Remaining zombies: {remaining_zombies}",
                    error="Zombie references still present",
                )
            return ValidationResult(valid=True, check_name="zombie_clean", evidence="No zombie references found")
        except Exception as exc:
            return ValidationResult(valid=False, check_name="zombie_clean", evidence="", error=str(exc))

    def rollback(self, target: str) -> bool:
        return False
