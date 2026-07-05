# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.boot_cron_jobs
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.rule_enforcement.task_completion_gate; zephyr.shared.event_bus; zephyr.autonomy_core.__init__; zephyr.governance.__init__
# [CONSUMERS] zephyr.trading.auto_runtime_core
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] register_boot_cron_jobs is idempotent
# [DEPRECATED] 定时调度已废除（2026-06-26裁定）：CircadianScheduler 已彻底移除。
# 本函数仅保留事件订阅（bus.subscribe）作为事件驱动入口，不再接收 circadian_scheduler 参数。
# 审计/治理任务改由 pre-commit GATE（commit事件）和 boot_hooks（状态变更事件）触发。
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns None; logs warning on failure; never raises
# [TESTS]
# [A_module] module_id=MOD-ORC_boot_cron_jobs | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.trading.work_orchestrator import WorkOrchestrator

logger = logging.getLogger(__name__)


def register_boot_cron_jobs(
    work_orchestrator: WorkOrchestrator,
    project_root: Path,
) -> None:
    # 定时调度已废除（2026-06-26裁定）：CircadianScheduler 已移除。
    # 仅保留事件订阅（bus.subscribe）作为事件驱动入口。
    try:
        from zephyr.shared.events.event_bus import bus

        def _on_freshness_critical(payload: dict) -> None:
            try:
                from zephyr.autonomy_core.skills.skill_freshness_ext import auto_deprecate_skill
                from zephyr.autonomy_core.skills.skill_lifecycle import SkillLifecycle

                sl = SkillLifecycle()
                for item in payload.get("criticals", []):
                    skill_id = item.get("skill_id", "")
                    score = item.get("freshness_score", 0.0)
                    if skill_id:
                        auto_deprecate_skill(sl, skill_id, score, reason="freshness_critical_auto")
            except Exception:
                pass

        bus.subscribe("skill.freshness_critical", _on_freshness_critical)
    except Exception as e:
        logger.warning("Failed to register boot cron event subscriptions: %s", e)
