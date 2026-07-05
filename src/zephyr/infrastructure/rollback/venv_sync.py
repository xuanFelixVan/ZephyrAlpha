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
# [A_module] module_id=MOD-INF_venv_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
VenvSync — venv/conda 版本同步保障。

依据: 蓝图 MOD-INF-021 §6.12 B68

回滚不仅恢复代码，同时 pip install -r requirements.txt（冻结版本）。
pip freeze 保存回滚前后的依赖快照用于差异审计。
--no-deps-sync 跳过（快速探索模式）。
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


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
            subprocess.run(
                ["pip", "install", "-r", str(self._req_path)],
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )
            details.append("pip install -r requirements.txt: SUCCESS")
        except subprocess.CalledProcessError as e:
            details.append(f"pip install failed: {e.stderr[:200]}")
        except Exception as e:
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
            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout.strip()
        except Exception:
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
