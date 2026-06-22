# [A_module] module_id=MOD-UNK_scheduler_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.scheduler_health
# [INVARIANTS] HealthReporter.report() returns dict with all 20 health keys
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.observability.feedback_loop.scheduler
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
from dataclasses import dataclass, field
from typing import Any

from zephyr.ops.detectors.diminishing_returns_detector import DiminishingReturnsDetector
from zephyr.ops.detectors.guard_cascade_detector import GuardCascadeDetector
from zephyr.ops.detectors.guard_oscillation_detector import GuardOscillationDetector
from zephyr.ops.diagnosers.cold_start_conservative_mode import ColdStartConservativeMode
from zephyr.ops.diagnosers.context_window_pressure_manager import ContextWindowPressureManager
from zephyr.ops.diagnosers.cross_guard_conflict_detector import CrossGuardConflictDetector
from zephyr.ops.diagnosers.cross_session_consistency_validator import CrossSessionConsistencyValidator
from zephyr.ops.diagnosers.data_volume_growth_monitor import DataVolumeGrowthMonitor
from zephyr.ops.diagnosers.e2e_integration_health import E2EIntegrationHealth
from zephyr.ops.diagnosers.fle_dogfood_monitor import FLEDogfoodMonitor
from zephyr.ops.diagnosers.guard_self_consistency_auditor import GuardSelfConsistencyAuditor
from zephyr.ops.diagnosers.knowledge_bus_factor_monitor import KnowledgeBusFactorMonitor
from zephyr.ops.diagnosers.numerical_stability_guard import NumericalStabilityGuard
from zephyr.ops.diagnosers.self_bottleneck_detector import SelfBottleneckDetector
from zephyr.ops.diagnosers.statistical_hygiene_auditor import StatisticalHygieneAuditor
from zephyr.ops.diagnosers.system_entropy_monitor import SystemEntropyMonitor
from zephyr.ops.evolution.self_modification_rate_limiter import SelfModificationRateLimiter
from zephyr.ops.forensic.guard_complexity_budget import GuardComplexityBudget
from zephyr.ops.resilience.graceful_degradation_planner import GracefulDegradationPlanner
from zephyr.ops.resilience.self_api_throttle_defense import SelfAPIThrottleDefense


@dataclass
class HealthReporter:
    dogfood_monitor: FLEDogfoodMonitor = field(default_factory=FLEDogfoodMonitor)
    bottleneck_detector: SelfBottleneckDetector = field(default_factory=SelfBottleneckDetector)
    degradation_planner: GracefulDegradationPlanner = field(default_factory=GracefulDegradationPlanner)
    throttle_defense: SelfAPIThrottleDefense = field(default_factory=SelfAPIThrottleDefense)
    bus_factor_monitor: KnowledgeBusFactorMonitor = field(default_factory=KnowledgeBusFactorMonitor)
    e2e_health: E2EIntegrationHealth = field(default_factory=E2EIntegrationHealth)
    volume_monitor: DataVolumeGrowthMonitor = field(default_factory=DataVolumeGrowthMonitor)
    numerical_guard: NumericalStabilityGuard = field(default_factory=NumericalStabilityGuard)
    stats_hygiene: StatisticalHygieneAuditor = field(default_factory=StatisticalHygieneAuditor)
    guard_consistency: GuardSelfConsistencyAuditor = field(default_factory=GuardSelfConsistencyAuditor)
    guard_conflict: CrossGuardConflictDetector = field(default_factory=CrossGuardConflictDetector)
    guard_oscillation: GuardOscillationDetector = field(default_factory=GuardOscillationDetector)
    cascade_detector: GuardCascadeDetector = field(default_factory=GuardCascadeDetector)
    mod_rate_limiter: SelfModificationRateLimiter = field(default_factory=SelfModificationRateLimiter)
    entropy_monitor: SystemEntropyMonitor = field(default_factory=SystemEntropyMonitor)
    diminishing_returns: DiminishingReturnsDetector = field(default_factory=DiminishingReturnsDetector)
    complexity_budget: GuardComplexityBudget = field(default_factory=GuardComplexityBudget)
    cold_start: ColdStartConservativeMode = field(default_factory=ColdStartConservativeMode)
    context_pressure: ContextWindowPressureManager = field(default_factory=ContextWindowPressureManager)
    session_consistency: CrossSessionConsistencyValidator = field(default_factory=CrossSessionConsistencyValidator)

    def report(self) -> dict[str, Any]:
        return {
            "dogfood": self.dogfood_monitor.self_check(),
            "bottleneck": self.bottleneck_detector.detect_bottleneck(),
            "degradation": self.degradation_planner.current_level.value,
            "throttle": self.throttle_defense.get_throttle_status(),
            "bus_factor": self.bus_factor_monitor.overall_bus_factor_score(),
            "e2e": self.e2e_health.overall_integration_score(),
            "storage": self.volume_monitor.overall_storage_health(),
            "numerical": {k: round(v, 3) for k, v in self.numerical_guard.health_scores.items()},
            "hygiene": self.stats_hygiene.overall_hygiene_score(),
            "L2_guard_consistency": self.guard_consistency.audit_consistency(),
            "L2_guard_conflicts": self.guard_conflict.detect_conflicts(),
            "L2_guard_oscillation": self.guard_oscillation.detect_oscillations(),
            "L3_cascade": self.cascade_detector.detect_cascade(),
            "L3_mod_rate_limiter": self.mod_rate_limiter.get_status(),
            "L3_entropy": self.entropy_monitor.analyze_trend(),
            "L4_diminishing_returns": self.diminishing_returns.analyze_diminishing_returns(),
            "L4_complexity_budget": self.complexity_budget.get_complexity_report(),
            "cold_start": self.cold_start.status_report(),
            "context_pressure": self.context_pressure.check_pressure(),
            "session_consistency": self.session_consistency.detect_jumps(),
        }
