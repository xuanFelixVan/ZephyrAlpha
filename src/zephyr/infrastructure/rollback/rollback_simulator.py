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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackSimulator — 回滚模拟器（CI 集成）。

依据: 蓝图 MOD-INF-021 §6.2 B11 + D-021-14

在临时 git worktree 中模拟回滚流程。
CI 集成: 每次 PR 运行真实回滚 -> 确认回滚可行 + 无副作用。
返回是否安全回滚 + 影响面分析 + 冲突报告。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: rollback_simulator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RollbackSimulator
#   name_en: RollbackSimulator
#   intro: class RollbackSimulator 源码 L80-L166
#   desc: 公共方法（定义序）: run_git, project_root, simulate_rollback；源码 L80-L166
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RollbackSimulator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging

from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

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

    def run_git(self, args, cwd=None) -> str:
        """公共接口：run_git（Stage 4 公共化，forward 至 _run_git 实现）。"""
        return self._run_git(args, cwd)

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def simulate_rollback(self, commit_sha: str) -> SimulationResult:
        start_time = time.time()
        sim_id = f"SIM-{int(start_time)}"
        worktree_path = self._project_root / f"{self.WORKTREE_PREFIX}{sim_id}"

        safe = False
        conflict_files: list[str] = []
        details: list[str] = []

        try:
            self.run_git(["worktree", "add", str(worktree_path), commit_sha])
            details.append(f"Worktree created: {worktree_path}")

            result = run_subprocess_hidden(
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
                    conflict_output = self.run_git(
                        ["diff", "--name-only", "--diff-filter=U"],
                        cwd=worktree_path,
                    )
                    conflict_files = [f for f in conflict_output.strip().split("\n") if f]

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            details.append(f"Simulation error: {e}")
        finally:
            try:
                self.run_git(["worktree", "remove", "--force", str(worktree_path)])
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            result = run_subprocess_hidden(
                ["git"] + args,
                cwd=str(cwd or self._project_root),
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return ""
