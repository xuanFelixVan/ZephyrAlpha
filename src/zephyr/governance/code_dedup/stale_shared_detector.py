# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.stale_shared_detector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/drift/test_stale_shared_detector.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_stale_shared_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""过时共享函数检测器 — 无caller × 30天 → STALE标记."""

from datetime import UTC, datetime


class StaleSharedDetector:
    """过时共享函数检测."""

    _STALE_AGE_DAYS: int = 30

    def detect(self, functions_with_callers: list[dict]) -> list[str]:
        """无caller × 30天未使用 → STALE."""
        now = datetime.now(UTC)
        stale: list[str] = []

        for func_info in functions_with_callers:
            if func_info.get("caller_count", 0) > 0:
                continue

            last_used = func_info.get("last_used_at", "")
            if not last_used:
                stale.append(func_info["name"])
                continue

            try:
                used_date = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
            except ValueError:
                continue

            if (now - used_date.replace(tzinfo=UTC)).days >= self._STALE_AGE_DAYS:
                stale.append(func_info["name"])

        return stale
