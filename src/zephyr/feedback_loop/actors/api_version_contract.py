# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.api_version_contract
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""API Version Contract — v0.14.0 R188

Blindspot: API version contracts invisible to consuming agents; sunset dates unenforced.
Risk: R188 — Agent calls deprecated API version; silent failure or wrong behavior.

Mitigation: Agent-readable API version contracts with sunset date enforcement.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: API 版本契约 + 调用时刻
#   fields: APIVersionContract（api_name/version/sunset_date）+ now_utc()
#   code: 契约 dataclass 与状态判定入口
# 层: 算法
# - id: A1
#   name_zh: 版本生命周期判定
#   name_en: version_lifecycle_verdict
#   intro: 按 sunset_date 与当前时间判定 ACTIVE/DEPRECATED/SUNSET，阻断过期版本调用
#   code: 状态判定逻辑（VersionStatus）
# 层: 输出
# - id: O1
#   name_zh: 版本可用性裁决
#   name_en: version_verdict
#   intro: Agent 可读的版本状态（SUNSET 即拒用）
#   downstream: 调用方 Agent / feedback_loop actors
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from zephyr.shared.utils.time_utils import now_utc


class VersionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    SUNSET = "SUNSET"


@dataclass
class APIVersionContract:
    api_name: str
    version: str
    sunset_date: str
    replacement_version: str = ""
    status: VersionStatus = VersionStatus.ACTIVE
    deprecation_notice_days: int = 90

    def check_sunset(self, today: str | None = None) -> bool:
        if today is None:
            today = now_utc().strftime("%Y-%m-%d")
        sunset = datetime.strptime(self.sunset_date, "%Y-%m-%d")
        now = datetime.strptime(today, "%Y-%m-%d")
        return now >= sunset

    def days_until_sunset(self) -> int:
        sunset = datetime.strptime(self.sunset_date, "%Y-%m-%d").replace(tzinfo=UTC)
        return (sunset - now_utc()).days
