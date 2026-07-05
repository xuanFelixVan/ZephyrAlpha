# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.scaffold_registrar
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-026(asset-inventory);MOD-INF-029(orphan-judge)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只注册不删除;注册到manifest/registry/__init__.py
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml scaffold_registrar段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScaffoldRegistrationError
# [TESTS] tests/auto-fix-engine/test_scaffold_registrar.py
# [A_module] module_id=MOD-INF_scaffold_registrar | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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


class ScaffoldRegistrar(BaseFixer):

    def __init__(self) -> None:
        super().__init__(
            fixer_id="scaffold_registrar",
            action_type="scaffold_registration",
            level=FixLevel.L1_RULE,
            dimension="DIM-TYPE-002",
            description="孤儿文件注册到 manifest/registry",
        )

    def scan(self) -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        manifest_path = repo_root / "scripts" / "script-manifest.yaml"
        registered_scripts: set[str] = set()
        if manifest_path.exists():
            try:
                import yaml

                data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                if data and "scripts" in data:
                    for entry in data["scripts"]:
                        if isinstance(entry, dict) and "path" in entry:
                            registered_scripts.add(entry["path"])
            except Exception as e:
                logger.debug("suppressed error in scaffold_registrar", exc_info=True)
        for script in (repo_root / "scripts").rglob("*.py"):
            if script.name.startswith("_"):
                continue
            rel = str(script.relative_to(repo_root)).replace("\\", "/")
            if rel not in registered_scripts:
                findings.append({"file": str(script), "relative_path": rel, "type": "unregistered_script"})
        for py_file in (repo_root / "src" / "zephyr").rglob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            if py_file.name == "__init__.py":
                continue
            pkg_dir = py_file.parent
            init_file = pkg_dir / "__init__.py"
            if init_file.exists():
                try:
                    content = init_file.read_text(encoding="utf-8")
                    module_name = py_file.stem
                    if module_name not in content:
                        findings.append(
                            {"file": str(py_file), "init_file": str(init_file), "type": "unregistered_module"}
                        )
                except Exception as e:
                    logger.warning("suppressed error in scaffold_registrar", exc_info=True)
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
            if target.startswith("scripts"):
                action.metadata["registration_type"] = "script_manifest"
                if not dry_run:
                    self._register_script(target)
                action.status = FixStatus.COMPLETED
            elif target.startswith("src/zephyr") and target.endswith(".py"):
                action.metadata["registration_type"] = "__init__.py"
                if not dry_run:
                    self._register_module(target)
                action.status = FixStatus.COMPLETED
            else:
                action.status = FixStatus.FAILED
                action.metadata["error"] = "Unknown registration target type"
        except Exception as exc:
            action.status = FixStatus.FAILED
            action.metadata["error"] = str(exc)
        return action

    def _register_script(self, target: str) -> None:
        repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
        manifest_path = repo_root / "scripts" / "script-manifest.yaml"
        try:
            import yaml

            data: dict[str, Any] = {"scripts": []}
            if manifest_path.exists():
                content = manifest_path.read_text(encoding="utf-8")
                data = yaml.safe_load(content) or {"scripts": []}
            rel = target.replace("\\", "/")
            existing_paths = [s.get("path", "") for s in data.get("scripts", []) if isinstance(s, dict)]
            if rel not in existing_paths:
                data.setdefault("scripts", []).append(
                    {
                        "path": rel,
                        "name": Path(target).stem,
                        "registered_by": "auto-fix-engine",
                    }
                )
                tmp_path = f"{manifest_path}.{os.getpid()}.tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
                os.replace(tmp_path, str(manifest_path))
        except Exception as exc:
            logger.error("Failed to register script %s: %s", target, exc)
            raise

    def _register_module(self, target: str) -> None:
        target_path = Path(target)
        init_file = target_path.parent / "__init__.py"
        module_name = target_path.stem
        if not init_file.exists():
            return
        try:
            content = init_file.read_text(encoding="utf-8")
            if module_name in content:
                return
            if "__all__" in content:
                all_match = re.search(r"__all__\s*=\s*\[([^\]]*)\]", content)
                if all_match:
                    existing = all_match.group(1).strip()
                    new_all = f'__all__ = [{existing}, "{module_name}"]' if existing else f'__all__ = ["{module_name}"]'
                    content = content.replace(all_match.group(0), new_all)
            import_line = f"from .{module_name} import *  # noqa: F401,F403\n"
            lines = content.split("\n")
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(("import ", "from ")):
                    insert_idx = i + 1
            lines.insert(insert_idx, import_line.rstrip())
            content = "\n".join(lines)
            tmp_path = f"{init_file}.{os.getpid()}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, str(init_file))
        except Exception as exc:
            logger.error("Failed to register module %s: %s", target, exc)
            raise

    def validate(self, target: str) -> ValidationResult:
        target_path = Path(target)
        if not target_path.exists():
            return ValidationResult(
                valid=False, check_name="scaffold_registration", evidence="", error="Target not found"
            )
        if target.startswith("scripts"):
            repo_root = REPO_ROOT  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            manifest_path = repo_root / "scripts" / "script-manifest.yaml"
            if not manifest_path.exists():
                return ValidationResult(
                    valid=False, check_name="scaffold_registration", evidence="", error="Manifest not found"
                )
            try:
                import yaml

                data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                rel = target.replace("\\", "/")
                paths = [s.get("path", "") for s in data.get("scripts", []) if isinstance(s, dict)]
                if rel in paths:
                    return ValidationResult(
                        valid=True, check_name="scaffold_registration", evidence="Registered in manifest"
                    )
                return ValidationResult(
                    valid=False, check_name="scaffold_registration", evidence="", error="Not found in manifest"
                )
            except Exception as exc:
                return ValidationResult(valid=False, check_name="scaffold_registration", evidence="", error=str(exc))
        return ValidationResult(
            valid=True, check_name="scaffold_registration", evidence="Validation skipped for module type"
        )

    def rollback(self, target: str) -> bool:
        return False
