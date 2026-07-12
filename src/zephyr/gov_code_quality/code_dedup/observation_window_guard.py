# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.observation_window_guard
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/resilience/test_observation_window_guard.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_observation_window_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""提取后稳定观察期守护 — 对标SDP 14天观察."""

from datetime import UTC, datetime


class ObservationWindowGuard:
    """14天稳定观察期."""

    _WINDOW_DAYS: int = 14

    def check(self, extraction_date: str) -> tuple[bool, int, str]:
        """检查提取是否已过14天观察期."""
        try:
            dt = datetime.fromisoformat(extraction_date.replace("Z", "+00:00"))
        except ValueError:
            return False, 0, "invalid_date"

        age = (datetime.now(UTC) - dt.replace(tzinfo=UTC)).days
        if age >= self._WINDOW_DAYS:
            return True, age, f"观察期通过：{age}天/14天"
        return False, age, f"观察期进行中：{age}天/14天，剩余{self._WINDOW_DAYS - age}天"
