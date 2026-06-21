# [A_module] module_id=MOD-UNK_detectors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.ops.detectors
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增子模块须同步更新_SUBMODULES和__all__
# [CONSUMERS] zephyr.integration.runtime_core.feedback_loop; detectors子包消费者
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
"""feedback-loop.detectors — DW-244: 60个子模块拆分为5个逻辑子模块。"""
import importlib

from zephyr.ops.detectors._anomaly import _SUBMODULES as _ANOMALY_SUBS
from zephyr.ops.detectors._drift import _SUBMODULES as _DRIFT_SUBS
from zephyr.ops.detectors._guard import _SUBMODULES as _GUARD_SUBS
from zephyr.ops.detectors._reliability import _SUBMODULES as _RELIABILITY_SUBS
from zephyr.ops.detectors._correlation import _SUBMODULES as _CORRELATION_SUBS

_SUBMODULES = _ANOMALY_SUBS + _DRIFT_SUBS + _GUARD_SUBS + _RELIABILITY_SUBS + _CORRELATION_SUBS


def __getattr__(name):
    if name in _SUBMODULES:
        mod = importlib.import_module(f"zephyr.ops.detectors.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'action_efficacy_decay_detector',
    'action_interaction_detector',
    'action_side_effect_cumulative_detector',
    'agent_trajectory_anomaly_detector',
    'alert_desensitization_curve',
    'anomaly_clustering',
    'anomaly_detector',
    'autoscale_remediation',
    'blast_radius',
    'blast_radius_budget',
    'capacity_forecast',
    'chaos_engineering',
    'concept_drift',
    'config_drift',
    'context_window_contamination_detector',
    'cross_signal_validator',
    'cross_system_correlator',
    'decision_provenance',
    'dependency_freshness_monitor',
    'diminishing_returns_detector',
    'ebpf_monitor',
    'emergent_behavior_detector',
    'ensemble_detector',
    'ensemble_drift',
    'external_health',
    'external_validation_checkpoint',
    'flag_lifecycle',
    'flapping_detector',
    'fle_performance_regression_detector',
    'gradual_poisoning_detector',
    'guard_cascade_detector',
    'guard_oscillation_detector',
    'heisenbug_detector',
    'infinite_loop_detector',
    'intermittent_failure_pattern',
    'log_anomaly',
    'maintenance_coordinator',
    'metric_cardinality_guard',
    'multi_signal_correlator',
    'openfeature',
    'otel_adapter',
    'placebo_action_detector',
    'positive_feedback_defense',
    'recursive_diagnosis_trust_evaluator',
    'regime_detector',
    'regulatory_audit',
    'resolution_tracker',
    'rumor_noise_filter',
    'runbook_executor',
    'self_audit',
    'self_diagnosis_data_leak_detector',
    'self_ha',
    'silent_corruption_detector',
    'synthetic_anomaly_generator',
    'temporal_coherence_of_self_model',
    'temporal_pattern',
    'trace_causal_bridge',
    'traffic_replay_validator',
    'trend_cycle_separator',
    'version_migrator',
    "_anomaly",
    "_correlation",
    "_drift",
    "_guard",
    "_reliability",
]
