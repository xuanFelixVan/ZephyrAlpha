# [A_module] module_id=MOD-UNK_diagnosers | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.ops.diagnosers
# [INVARIANTS] __all__列表不变; 公开API不变
# [MODIFY-GUARD] 新增子模块须同步更新_SUBMODULES和__all__
# [CONSUMERS] zephyr.integration.runtime_core.feedback_loop; diagnosers子包消费者
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
"""feedback-loop.diagnosers — DW-242: 71个子模块拆分为4个逻辑子模块。"""
import importlib

from zephyr.ops.diagnosers._health import _SUBMODULES as _HEALTH_SUBS
from zephyr.ops.diagnosers._cognitive import _SUBMODULES as _COGNITIVE_SUBS
from zephyr.ops.diagnosers._diagnosis import _SUBMODULES as _DIAGNOSIS_SUBS
from zephyr.ops.diagnosers._reliability import _SUBMODULES as _RELIABILITY_SUBS

_SUBMODULES = _HEALTH_SUBS + _COGNITIVE_SUBS + _DIAGNOSIS_SUBS + _RELIABILITY_SUBS


def __getattr__(name):
    if name in _SUBMODULES:
        mod = importlib.import_module(f"zephyr.ops.diagnosers.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'action_composition_health_monitor',
    'adaptive_param_tuning',
    'amplification_guard',
    'api_dependency_metrics',
    'auto_diagnosis',
    'burn_rate_alerter',
    'burnout_alarm',
    'capacity_aware_repair',
    'causal_inference_engine',
    'cognitive_load',
    'cognitive_load_budget',
    'cold_start_conservative_mode',
    'collaborative_learning',
    'confidence_decomposer',
    'context_truncation',
    'context_window_pressure_manager',
    'counterfactual',
    'cross_guard_conflict_detector',
    'cross_session_consistency_validator',
    'data_volume_growth_monitor',
    'diagnosis_engine',
    'diagnosis_kpi',
    'dr_resilience_metrics',
    'e2e_integration_health',
    'feedback_delay_compensator',
    'fle_dogfood_monitor',
    'fle_self_slo_metrics',
    'gamification',
    'global_health_map',
    'guard_interaction_topology_mapper',
    'guard_self_consistency_auditor',
    'human_anomaly_flood_detector',
    'impact_predictor',
    'incident_knowledge_injector',
    'interactive_diagnosis',
    'knowledge_bus_factor_monitor',
    'knowledge_market',
    'latency_slo',
    'llm_provider_integrity',
    'llm_quality_regression',
    'memory_self_check',
    'meta_guard_latency_budget',
    'model_health',
    'model_rotation',
    'model_rotation_v2',
    'model_version_semantic_drift',
    'mtti_tracker',
    'nonstationary_effectiveness',
    'numerical_stability_guard',
    'operational_seasonality',
    'prompt_fingerprint',
    'prompt_sanitizer',
    'recovery_time_stats',
    'regime_gain_scheduling',
    'retirement_planner',
    'self_benchmark',
    'self_bottleneck_detector',
    'self_health_monitor',
    'self_llm_observability',
    'slo_capacity_metrics',
    'socratic_questions',
    'statistical_hygiene_auditor',
    'system_entropy_monitor',
    'temporal_integrity_guard',
    'timezone_semantic_reasoner',
    'toil_quantification',
    'tone_adapter',
    'tone_adapter_v2',
    'value_added_baseline',
    'vertical_self_assessment',
    'zombie_fle_detector',
    "_cognitive",
    "_diagnosis",
    "_health",
    "_reliability",
]
