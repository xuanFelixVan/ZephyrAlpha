# [A_module] module_id=MOD-INF_modules | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
"""
ZephyrAlpha 容量保障体系 — 模块包
包含盲点审计（§21-§25）补充的所有模块 (M-28~M-46)。
"""

from zephyr.shared.alert_manager import Alert, AlertManager, AlertSeverity
from zephyr.shared.alert_precision_tracker import AlertPrecisionTracker, PrecisionMetrics
from zephyr.shared.dual_channel_alert import Channel, DualAlert, DualChannelAlert
from zephyr.shared.error_budget_tracker import BudgetStatus, ErrorBudgetTracker
from zephyr.shared.heartbeat_server import HeartbeatServer, HeartbeatStatus
from zephyr.shared.longevity_monitor import LongevityMonitor, LongevityReport
from zephyr.shared.slo_review_assistant import SloReview, SloReviewAssistant
from zephyr.shared.task_heartbeat import TaskHeartbeat, TaskPulse
from zephyr.shared.ttl_cleanup_engine import CleanupResult, TtlCleanupEngine, TtlEntry

from . import (
    ai_skill_monitor,
    capacity_testing_harness,
    cliff_detector,
    cold_start_estimator,
    config_reload_semantic,
    context_budget_guard,
    degradation_spiral_detector,
    dr_drill_scheduler,
    graceful_shutdown,
    hawthorne_blind,
    multi_model_vendor_risk,
    observer_effect_compensator,
    owner_health_monitor,
    per_task_token_budget,
    startup_guard,
    sunk_cost_intervention,
    time_partitioned_slo,
    token_value_attribution,
    trace_capacity_injector,
    winfs_defense,
)

__all__ = [
    "ai_skill_monitor",
    "capacity_testing_harness",
    "cliff_detector",
    "cold_start_estimator",
    "config_reload_semantic",
    "context_budget_guard",
    "degradation_spiral_detector",
    "dr_drill_scheduler",
    "graceful_shutdown",
    "hawthorne_blind",
    "multi_model_vendor_risk",
    "observer_effect_compensator",
    "owner_health_monitor",
    "per_task_token_budget",
    "startup_guard",
    "sunk_cost_intervention",
    "time_partitioned_slo",
    "token_value_attribution",
    "trace_capacity_injector",
    "winfs_defense",
]

version = "2.6.0"
module_id = "MOD-INF-001"
