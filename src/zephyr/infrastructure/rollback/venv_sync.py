# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.venv_sync
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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [DEPRECATED] legacy trio retirement (audit P2-13 / P2-20).
#   Replacement: no direct replacement; the rollback core path
#   (RollbackExecutor + RollbackVerifier) remains the supported API.
#   Scheduled for removal in a future release.

"""
VenvSync — venv/conda 版本同步保障。

依据: 蓝图 MOD-INF-021 §6.12 B68

回滚不仅恢复代码，同时 pip install -r requirements.txt（冻结版本）。
pip freeze 保存回滚前后的依赖快照用于差异审计。
--no-deps-sync 跳过（快速探索模式）。
"""

from __future__ import annotations

import subprocess
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden

warnings.warn(
    "zephyr.infrastructure.rollback.venv_sync is deprecated (legacy trio "
    "retirement, audit P2-13/P2-20). No direct replacement; use the rollback "
    "core path (RollbackExecutor/RollbackVerifier).",
    DeprecationWarning,
    stacklevel=2,
)


@dataclass
class DepDiff:
    added: list[str]
    removed: list[str]
    changed: list[str]


@dataclass
class VenvSyncResult:
    success: bool
    before_freeze: str
    after_freeze: str
    diff: DepDiff
    details: list[str] = field(default_factory=list)


class VenvSync:
    REQUIREMENTS_FILE: str = "requirements.txt"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._req_path = self._project_root / self.REQUIREMENTS_FILE

    def compute_diff(self, before, after) -> DepDiff:
        """公共接口：compute_diff（Stage 4 公共化）。"""
        return self._compute_diff(before, after)


    @property
    def req_path(self):
        """只读：req_path（Stage 4 公共化）。"""
        return self._req_path

    @req_path.setter
    def req_path(self, value):
        """写入：req_path（Stage 4 公共化）。"""
        self._req_path = value


    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value


    @staticmethod
    @staticmethod
    def parse_freeze(freeze_output) -> dict[str, str]:
        """公共接口：parse_freeze（Stage 4 公共化）。"""
        return __class__._parse_freeze(freeze_output)


    def sync(self, skip_deps: bool = False) -> VenvSyncResult:
        before = self._freeze()
        details: list[str] = []

        if skip_deps:
            return VenvSyncResult(
                success=True,
                before_freeze=before,
                after_freeze=before,
                diff=DepDiff([], [], []),
                details=["Dependency sync skipped (--no-deps-sync)"],
            )

        if not self._req_path.exists():
            return VenvSyncResult(
                success=True,
                before_freeze=before,
                after_freeze=before,
                diff=DepDiff([], [], []),
                details=["No requirements.txt found"],
            )

        try:
            run_subprocess_hidden(
                ["pip", "install", "-r", str(self._req_path)],
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )
            details.append("pip install -r requirements.txt: SUCCESS")
        except subprocess.CalledProcessError as e:
            details.append(f"pip install failed: {e.stderr[:200]}")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            details.append(f"pip install error: {e}")

        after = self._freeze()
        diff = self._compute_diff(before, after)
        details.append(f"Dependency diff: +{len(diff.added)} -{len(diff.removed)} ~{len(diff.changed)}")

        return VenvSyncResult(
            success=True,
            before_freeze=before,
            after_freeze=after,
            diff=diff,
            details=details,
        )

    def _freeze(self) -> str:
        try:
            result = run_subprocess_hidden(
                ["pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout.strip()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return ""

    def _compute_diff(self, before: str, after: str) -> DepDiff:
        before_map = self._parse_freeze(before)
        after_map = self._parse_freeze(after)

        added = [pkg for pkg in after_map if pkg not in before_map]
        removed = [pkg for pkg in before_map if pkg not in after_map]
        changed = [pkg for pkg in before_map if pkg in after_map and before_map[pkg] != after_map[pkg]]

        return DepDiff(added=added, removed=removed, changed=changed)

    @staticmethod
    def _parse_freeze(freeze_output: str) -> dict[str, str]:
        pkgs: dict[str, str] = {}
        for line in freeze_output.splitlines():
            if "==" in line:
                name, version = line.split("==", 1)
                pkgs[name.strip().lower()] = version.strip()
        return pkgs
