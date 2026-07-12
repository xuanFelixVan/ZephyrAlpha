# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.scheduler_health
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS] zephyr.feedback_loop.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] HealthReporter.report() returns dict with all 20 health keys
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_scheduler_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from dataclasses import dataclass, field
from typing import Any

from zephyr.feedback_loop.detectors.diminishing_returns_detector import DiminishingReturnsDetector
from zephyr.feedback_loop.detectors.guard_cascade_detector import GuardCascadeDetector
from zephyr.feedback_loop.detectors.guard_oscillation_detector import GuardOscillationDetector
from zephyr.feedback_loop.diagnosers.cold_start_conservative_mode import ColdStartConservativeMode
from zephyr.feedback_loop.diagnosers.context_window_pressure_manager import ContextWindowPressureManager
from zephyr.feedback_loop.diagnosers.cross_guard_conflict_detector import CrossGuardConflictDetector
from zephyr.feedback_loop.diagnosers.cross_session_consistency_validator import CrossSessionConsistencyValidator
from zephyr.feedback_loop.diagnosers.data_volume_growth_monitor import DataVolumeGrowthMonitor
from zephyr.feedback_loop.diagnosers.e2e_integration_health import E2EIntegrationHealth
from zephyr.feedback_loop.diagnosers.fle_dogfood_monitor import FLEDogfoodMonitor
from zephyr.feedback_loop.diagnosers.guard_self_consistency_auditor import GuardSelfConsistencyAuditor
from zephyr.feedback_loop.diagnosers.knowledge_bus_factor_monitor import KnowledgeBusFactorMonitor
from zephyr.feedback_loop.diagnosers.numerical_stability_guard import NumericalStabilityGuard
from zephyr.feedback_loop.diagnosers.self_bottleneck_detector import SelfBottleneckDetector
from zephyr.feedback_loop.diagnosers.statistical_hygiene_auditor import StatisticalHygieneAuditor
from zephyr.feedback_loop.diagnosers.system_entropy_monitor import SystemEntropyMonitor
from zephyr.feedback_loop.evolution.self_modification_rate_limiter import SelfModificationRateLimiter
from zephyr.feedback_loop.forensic.guard_complexity_budget import GuardComplexityBudget
from zephyr.feedback_loop.resilience.graceful_degradation_planner import GracefulDegradationPlanner
from zephyr.feedback_loop.resilience.self_api_throttle_defense import SelfAPIThrottleDefense


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
