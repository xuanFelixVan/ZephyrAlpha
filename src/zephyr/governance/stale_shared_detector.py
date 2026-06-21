# [A_module] module_id=MOD-UNK_stale_shared_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md

# [MODULE] zephyr.testing.code_dedup.stale_shared_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""过时共享函数检测器 — 无caller × 30天 → STALE标记."""

from datetime import datetime, timezone, timedelta
from pathlib import Path

class StaleSharedDetector:
    """过时共享函数检测."""

    _STALE_AGE_DAYS: int = 30

    def detect(self, functions_with_callers: list[dict]) -> list[str]:
        """无caller × 30天未使用 → STALE."""
        now = datetime.now(timezone.utc)
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

            if (now - used_date.replace(tzinfo=timezone.utc)).days >= self._STALE_AGE_DAYS:
                stale.append(func_info["name"])

        return stale
