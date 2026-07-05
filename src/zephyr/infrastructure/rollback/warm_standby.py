# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.warm_standby
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
# [A_module] module_id=MOD-INF_warm_standby | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
WarmStandby — 温备热切（git worktree 副本维护）。

依据: 蓝图 MOD-INF-021 §6.12 B61 + D-021-15

维护 git worktree 温备副本 → Agent 在回滚期间切换到读备副本。
RTO 从 ~2s 降低到 <100ms（worktree 切换 + 指针替换）。
后台异步完成回滚验证后更新温备 → exit code 14。
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import subprocess
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class StandbyState:
    standby_commit: str
    standby_path: str
    last_verified_at: str
    is_active: bool
    is_stale: bool


@dataclass
class CutoverResult:
    success: bool
    previous_commit: str
    target_commit: str
    rto_ms: int
    exit_code: int
    details: list[str] = field(default_factory=list)


class WarmStandby:
    STANDBY_DIR: str = ".zephyr/warm_standby"
    STANDBY_STATE_FILE: str = ".zephyr/warm_standby_state.json"
    EXIT_CODE_CUTOVER: int = 14

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._standby_dir = self._project_root / self.STANDBY_DIR
        self._state_path = self._project_root / self.STANDBY_STATE_FILE

    def initialize(self, commit_sha: str) -> bool:
        if self._standby_dir.exists():
            return True

        try:
            subprocess.run(
                ["git", "worktree", "add", str(self._standby_dir), commit_sha],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=15,
                check=True,
            )

            state = {
                "standby_commit": commit_sha,
                "standby_path": str(self._standby_dir),
                "last_verified_at": datetime.now(UTC).isoformat(),
                "is_active": True,
                "is_stale": False,
            }
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

            return True
        except Exception:
            return False

    def cutover(self, target_commit: str) -> CutoverResult:
        start = time.time()

        if not self._state_path.exists():
            return CutoverResult(
                success=False,
                previous_commit="",
                target_commit=target_commit,
                rto_ms=0,
                exit_code=self.EXIT_CODE_CUTOVER,
                details=["No warm standby initialized"],
            )

        state = self._read_state()
        if not state:
            return CutoverResult(
                success=False,
                previous_commit="",
                target_commit=target_commit,
                rto_ms=0,
                exit_code=self.EXIT_CODE_CUTOVER,
                details=["Failed to read standby state"],
            )

        previous_commit = state.standby_commit

        try:
            self._run_git(["checkout", target_commit], cwd=self._standby_dir)
        except Exception as e:
            return CutoverResult(
                success=False,
                previous_commit=previous_commit,
                target_commit=target_commit,
                rto_ms=0,
                exit_code=self.EXIT_CODE_CUTOVER,
                details=[str(e)],
            )

        state.standby_commit = target_commit
        state.last_verified_at = datetime.now(UTC).isoformat()
        state.is_stale = False
        self._save_state(state)

        rto_ms = int((time.time() - start) * 1000)

        return CutoverResult(
            success=True,
            previous_commit=previous_commit,
            target_commit=target_commit,
            rto_ms=rto_ms,
            exit_code=0,
            details=[f"Cutover completed in {rto_ms}ms"],
        )

    def rotate(self, new_commit: str) -> bool:
        try:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(self._standby_dir)],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=10,
            )
        except Exception as e:
            logger.warning("suppressed error in warm_standby", exc_info=True)

        return self.initialize(new_commit)

    def verify_integrity(self) -> bool:
        if not self._standby_dir.exists():
            return False
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self._standby_dir),
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_state(self) -> StandbyState | None:
        return self._read_state()

    def _read_state(self) -> StandbyState | None:
        if not self._state_path.exists():
            return None
        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            return StandbyState(**data)
        except (json.JSONDecodeError, TypeError):
            return None

    def _save_state(self, state: StandbyState) -> None:
        data = {
            "standby_commit": state.standby_commit,
            "standby_path": state.standby_path,
            "last_verified_at": state.last_verified_at,
            "is_active": state.is_active,
            "is_stale": state.is_stale,
        }
        self._state_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _run_git(self, args: list[str], cwd: Path | None = None) -> str:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd or self._project_root),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout
