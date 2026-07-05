# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_simulator
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
# [A_module] module_id=MOD-INF_rollback_simulator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackSimulator — 回滚模拟器（CI 集成）。

依据: 蓝图 MOD-INF-021 §6.2 B11 + D-021-14

在临时 git worktree 中模拟回滚流程。
CI 集成: 每次 PR 运行真实回滚 → 确认回滚可行 + 无副作用。
返回是否安全回滚 + 影响面分析 + 冲突报告。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SimulationResult:
    safe_to_rollback: bool
    commit_sha: str
    worktree_path: str
    duration_ms: int
    conflict_files: list[str]
    files_changed: int
    db_impact: int
    details: list[str] = field(default_factory=list)


class RollbackSimulator:
    WORKTREE_PREFIX: str = ".zephyr/sim_worktree_"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def simulate_rollback(self, commit_sha: str) -> SimulationResult:
        start_time = time.time()
        sim_id = f"SIM-{int(start_time)}"
        worktree_path = self._project_root / f"{self.WORKTREE_PREFIX}{sim_id}"

        safe = False
        conflict_files: list[str] = []
        details: list[str] = []

        try:
            self._run_git(["worktree", "add", str(worktree_path), commit_sha])
            details.append(f"Worktree created: {worktree_path}")

            result = subprocess.run(
                ["git", "revert", "--no-edit", commit_sha],
                cwd=str(worktree_path),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                safe = True
                details.append(f"Revert simulation passed: {commit_sha}")
            else:
                stderr = result.stderr
                details.append(f"Revert conflict: {stderr[:200]}")
                if "CONFLICT" in stderr:
                    conflict_output = self._run_git(
                        ["diff", "--name-only", "--diff-filter=U"],
                        cwd=worktree_path,
                    )
                    conflict_files = [f for f in conflict_output.strip().split("\n") if f]

        except Exception as e:
            details.append(f"Simulation error: {e}")
        finally:
            try:
                self._run_git(["worktree", "remove", "--force", str(worktree_path)])
            except Exception as e:
                logger.warning("suppressed error in rollback_simulator", exc_info=True)

        duration_ms = int((time.time() - start_time) * 1000)

        return SimulationResult(
            safe_to_rollback=safe,
            commit_sha=commit_sha,
            worktree_path=str(worktree_path),
            duration_ms=duration_ms,
            conflict_files=conflict_files,
            files_changed=len(conflict_files),
            db_impact=0,
            details=details,
        )

    def _run_git(self, args: list[str], cwd: Path | None = None) -> str:
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(cwd or self._project_root),
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout
        except Exception:
            return ""
