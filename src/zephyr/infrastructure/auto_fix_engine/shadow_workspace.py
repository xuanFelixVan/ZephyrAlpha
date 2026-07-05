# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.shadow_workspace
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预演失败MUST阻止应用;沙箱目录MUST在验证后清理
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml shadow_workspace段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ShadowWorkspaceError
# [TESTS] tests/auto-fix-engine/test_shadow_workspace.py
# [A_module] module_id=MOD-INF_shadow_workspace | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixAction, ShadowResult

from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)


class ShadowWorkspace:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        config = config or {}
        self._base_dir: str = config.get("base_dir", os.path.join(tempfile.gettempdir(), "auto_fix_shadow"))
        self._run_pytest: bool = config.get("run_pytest", True)
        self._run_mypy: bool = config.get("run_mypy", True)
        self._run_ruff: bool = config.get("run_ruff", True)
        self._pytest_timeout: int = config.get("pytest_timeout", 120)

    def preflight(self, action: FixAction, project_root: str | None = None) -> ShadowResult:
        shadow_dir = os.path.join(self._base_dir, action.action_id)
        try:
            os.makedirs(shadow_dir, exist_ok=True)
            target_path = Path(action.target)
            if not target_path.exists():
                return ShadowResult(safe_to_apply=False, error="Target not found", shadow_dir=shadow_dir)
            rel_path = target_path.relative_to(project_root or str(REPO_ROOT)) if project_root else target_path.name  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            shadow_file = os.path.join(shadow_dir, str(rel_path))
            os.makedirs(os.path.dirname(shadow_file), exist_ok=True)
            with open(shadow_file, "w", encoding="utf-8") as f:
                f.write(action.after)
            test_result = None
            type_result = None
            lint_result = None
            all_passed = True
            if self._run_pytest and shadow_file.endswith(".py"):
                test_result = self._run_test(shadow_dir, project_root)
                if test_result and not test_result.get("passed", False):
                    all_passed = False
            if self._run_mypy and shadow_file.endswith(".py"):
                type_result = self._run_type_check(shadow_file, project_root)
                if type_result and not type_result.get("passed", False):
                    all_passed = False
            if self._run_ruff and shadow_file.endswith(".py"):
                lint_result = self._run_lint(shadow_file, project_root)
                if lint_result and not lint_result.get("passed", False):
                    all_passed = False
            return ShadowResult(
                safe_to_apply=all_passed,
                test_result=test_result,
                type_result=type_result,
                lint_result=lint_result,
                shadow_dir=shadow_dir,
            )
        except Exception as exc:
            return ShadowResult(safe_to_apply=False, error=str(exc), shadow_dir=shadow_dir)
        finally:
            try:
                shutil.rmtree(shadow_dir, ignore_errors=True)
            except Exception:
                pass

    def _run_test(self, shadow_dir: str, project_root: str | None = None) -> dict[str, Any]:
        try:
            cmd = ["python", "-m", "pytest", "-x", "-q", "--tb=short", shadow_dir]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._pytest_timeout,
                cwd=project_root or str(REPO_ROOT),  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            )
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout[-500:] if result.stdout else "",
                "stderr": result.stderr[-500:] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "pytest timeout"}
        except Exception as exc:
            return {"passed": False, "error": str(exc)}

    def _run_type_check(self, shadow_file: str, project_root: str | None = None) -> dict[str, Any]:
        try:
            cmd = ["python", "-m", "mypy", shadow_file, "--no-error-summary"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_root or str(REPO_ROOT),  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            )
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout[-500:] if result.stdout else "",
            }
        except Exception as exc:
            return {"passed": False, "error": str(exc)}

    def _run_lint(self, shadow_file: str, project_root: str | None = None) -> dict[str, Any]:
        try:
            cmd = ["python", "-m", "ruff", "check", shadow_file]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_root or str(REPO_ROOT),  # 5.12.5 修复：改用 REPO_ROOT 真源（原 os.getcwd() 硬假设cwd是项目根）
            )
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout[-500:] if result.stdout else "",
            }
        except Exception as exc:
            return {"passed": False, "error": str(exc)}
