# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.submodule_sync
# [DOMAIN] D_INFRA_RECOVERY
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
# [A_module] module_id=MOD-INF_submodule_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Submodule Sync — Submodule/Monorepo 多仓库同步回滚。

依据：
    蓝图 MOD-INF-021 §6.12 B75 + §9 exit code 16
    任务卡 TASK-INF-0251

功能：
    - 检测 git submodule / Monorepo layout
    - 逐 submodule 回滚 + 更新主仓库引用
    - 引用不同步 → exit code 16 (SUBMODULE_OUT_OF_SYNC)
    - 多仓库版本视为单一单元回滚
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXIT_SUBMODULE_OUT_OF_SYNC = 16


@dataclass
class SubmoduleInfo:
    path: str
    url: str
    current_sha: str
    target_sha: str = ""
    synced: bool = False


@dataclass
class MonorepoModule:
    path: str
    package_name: str
    is_submodule: bool = False


@dataclass
class SyncResult:
    success: bool
    submodules_processed: int
    submodules_synced: int
    out_of_sync: list[str]
    errors: list[str] = field(default_factory=list)
    exit_code: int = 0


class SubmoduleSync:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def detect_layout(self) -> str:
        if (self._project_root / ".gitmodules").exists():
            return "submodule"

        src_dir = self._project_root / "src"
        if src_dir.exists():
            subdirs = [d for d in src_dir.iterdir() if d.is_dir()]
            if len(subdirs) > 1:
                return "monorepo"

        return "single_repo"

    def list_submodules(self) -> list[SubmoduleInfo]:
        submodules: list[SubmoduleInfo] = []
        gitmodules_path = self._project_root / ".gitmodules"

        if not gitmodules_path.exists():
            return submodules

        try:
            output = subprocess.run(
                ["git", "submodule", "status"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in output.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.strip().split()
                if len(parts) >= 2:
                    current_sha = parts[0].lstrip(" +-")
                    path = parts[1]
                    submodules.append(
                        SubmoduleInfo(
                            path=path,
                            url=self._get_submodule_url(path),
                            current_sha=current_sha,
                        )
                    )
        except (subprocess.TimeoutExpired, Exception):
            pass

        return submodules

    def get_submodule_shas(self) -> dict[str, str]:
        sha_map: dict[str, str] = {}
        try:
            output = subprocess.run(
                ["git", "submodule", "foreach", "--quiet", "echo $path $sha1"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in output.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    sha_map[parts[0]] = parts[1]
        except (subprocess.TimeoutExpired, Exception):
            pass
        return sha_map

    def sync_submodule(self, submodule_path: str, target_sha: str) -> bool:
        sub_path = self._project_root / submodule_path
        if not sub_path.exists():
            return False

        try:
            subprocess.run(
                ["git", "-C", str(sub_path), "checkout", target_sha],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=30,
            )

            subprocess.run(
                ["git", "add", submodule_path],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )

            return True
        except (subprocess.TimeoutExpired, Exception):
            return False

    def sync_all_submodules(self, target_sha: str) -> SyncResult:
        submodules = self.list_submodules()
        synced_count = 0
        out_of_sync: list[str] = []
        errors: list[str] = []

        for sm in submodules:
            sm.target_sha = target_sha
            if self.sync_submodule(sm.path, target_sha):
                sm.synced = True
                synced_count += 1
            else:
                out_of_sync.append(sm.path)

        self._verify_submodule_references(submodules, errors)

        exit_code = 0
        if out_of_sync:
            exit_code = EXIT_SUBMODULE_OUT_OF_SYNC

        return SyncResult(
            success=len(out_of_sync) == 0,
            submodules_processed=len(submodules),
            submodules_synced=synced_count,
            out_of_sync=out_of_sync,
            errors=errors,
            exit_code=exit_code,
        )

    def rollback_submodules_consistent(
        self,
        main_commit_sha: str,
        submodule_target_shas: dict[str, str],
    ) -> SyncResult:
        synced_count = 0
        out_of_sync: list[str] = []
        errors: list[str] = []

        for path, target_sha in submodule_target_shas.items():
            if self.sync_submodule(path, target_sha):
                synced_count += 1
            else:
                out_of_sync.append(path)

        exit_code = EXIT_SUBMODULE_OUT_OF_SYNC if out_of_sync else 0

        return SyncResult(
            success=len(out_of_sync) == 0,
            submodules_processed=len(submodule_target_shas),
            submodules_synced=synced_count,
            out_of_sync=out_of_sync,
            errors=errors,
            exit_code=exit_code,
        )

    def detect_monorepo_modules(self) -> list[MonorepoModule]:
        modules: list[MonorepoModule] = []
        src_dir = self._project_root / "src"

        if not src_dir.exists():
            return modules

        for d in src_dir.iterdir():
            if d.is_dir():
                setup_py = d / "setup.py"
                pyproject = d / "pyproject.toml"
                if setup_py.exists() or pyproject.exists():
                    modules.append(
                        MonorepoModule(
                            path=str(d.relative_to(self._project_root)),
                            package_name=d.name,
                        )
                    )

        return modules

    def _get_submodule_url(self, path: str) -> str:
        try:
            output = subprocess.run(
                ["git", "config", "--file", ".gitmodules", f"submodule.{path}.url"],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return output.stdout.strip()
        except (subprocess.TimeoutExpired, Exception):
            return ""

    def _verify_submodule_references(
        self,
        submodules: list[SubmoduleInfo],
        errors: list[str],
    ) -> None:
        for sm in submodules:
            if not sm.synced:
                errors.append(
                    f"SUBMODULE_OUT_OF_SYNC: {sm.path} (current={sm.current_sha[:8]}, target={sm.target_sha[:8]})"
                )

    def generate_sync_report(self, result: SyncResult) -> dict[str, Any]:
        return {
            "report_id": f"SUBMODULE-SYNC-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "success": result.success,
            "submodules_processed": result.submodules_processed,
            "submodules_synced": result.submodules_synced,
            "out_of_sync": result.out_of_sync,
            "errors": result.errors,
            "exit_code": result.exit_code,
            "project_root": str(self._project_root),
        }
