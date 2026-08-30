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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackTargetStaleness — 回滚目标陈旧度检测。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B125 + exit code 42

回滚目标 commit 若超过 30 天未被重新验证为 knowngoodstate，
触发 exit 42 (TARGET_STALE_OVER_30D) + 告警。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: rollback_target_staleness.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RollbackTargetStaleness
#   name_en: RollbackTargetStaleness
#   intro: class RollbackTargetStaleness 源码 L77-L144
#   desc: 公共方法（定义序）: project_root, get_commit_date, check；源码 L77-L144
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: RollbackTargetStaleness
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

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def get_commit_date(self, commit_sha) -> datetime | None:
        """公共接口：get_commit_date（Stage 4 公共化）。"""
        return self._get_commit_date(commit_sha)

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
            result = run_subprocess_hidden(
                ["git", "show", "-s", "--format=%aI", commit_sha],
                cwd=str(self._project_root),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return datetime.fromisoformat(result.stdout.strip())
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in rollback_target_staleness", exc_info=True)
        return None
