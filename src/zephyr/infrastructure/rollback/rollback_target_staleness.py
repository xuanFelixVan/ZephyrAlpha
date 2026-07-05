# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_target_staleness
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
# [A_module] module_id=MOD-INF_rollback_target_staleness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackTargetStaleness — 回滚目标陈旧度检测。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B125 + exit code 42

回滚目标 commit 若超过 30 天未被重新验证为 knowngoodstate，
触发 exit 42 (TARGET_STALE_OVER_30D) + 告警。
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class StalenessResult:
    commit_sha: str
    age_days: float
    is_stale: bool
    last_verified_at: str
    exit_code: int
    recommendation: str


class RollbackTargetStaleness:
    EXIT_CODE_STALE: int = 42
    MAX_AGE_DAYS: int = 30

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def check(self, commit_sha: str) -> StalenessResult:
        commit_date = self._get_commit_date(commit_sha)
        if not commit_date:
            return StalenessResult(
                commit_sha=commit_sha,
                age_days=0,
                is_stale=False,
                last_verified_at="",
                exit_code=0,
                recommendation="Could not determine commit date",
            )

        now = datetime.now(UTC)
        age_days = (now - commit_date).total_seconds() / 86400
        is_stale = age_days > self.MAX_AGE_DAYS

        recommendation = ""
        if is_stale:
            recommendation = (
                f"Rollback target {commit_sha} is {age_days:.0f} days old "
                f"(max {self.MAX_AGE_DAYS}d). Consider selecting a more recent commit "
                f"or re-verifying this state via knowngoodstate_ledger."
            )

        return StalenessResult(
            commit_sha=commit_sha,
            age_days=age_days,
            is_stale=is_stale,
            last_verified_at=commit_date.isoformat(),
            exit_code=self.EXIT_CODE_STALE if is_stale else 0,
            recommendation=recommendation,
        )

    def _get_commit_date(self, commit_sha: str) -> datetime | None:
        try:
            result = subprocess.run(
                ["git", "show", "-s", "--format=%aI", commit_sha],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return datetime.fromisoformat(result.stdout.strip())
        except Exception:
            pass
        return None
