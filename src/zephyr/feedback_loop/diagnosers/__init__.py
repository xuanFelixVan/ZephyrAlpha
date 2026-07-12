# [A_module] module_id=MOD-UNK_diagnosers | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers
# [INVARIANTS] __all__列表不变(公开叶子API不变); 旧路径diagnosers.<leaf>保持可导入(兼容垫片)
# [MODIFY-GUARD] 新增子模块须同步更新对应子包的_SUBMODULES和本文件__all__
# [CONSUMERS] zephyr.integration.runtime_core.feedback_loop; diagnosers子包消费者
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [TTL] permanent
"""feedback-loop.diagnosers — GOV-DOC-018: 71个叶子模块拆分为4个逻辑子包(cognitive/diagnosis/health/reliability)。

兼容垫片：旧导入路径 ``zephyr.trading.feedback_loop.diagnosers.<leaf>`` 继续可用，
实际模块已迁移到 ``zephyr.trading.feedback_loop.diagnosers.<subpkg>.<leaf>``。
``__getattr__`` 处理 ``from diagnosers import <leaf>`` 形式；
``_LeafAliasFinder`` 处理 ``from diagnosers.<leaf> import X`` / ``import diagnosers.<leaf>`` 形式。
"""

import importlib
import importlib.abc
import importlib.util
import sys

from zephyr.feedback_loop.diagnosers.cognitive import _SUBMODULES as _COGNITIVE_SUBS
from zephyr.feedback_loop.diagnosers.diagnosis import _SUBMODULES as _DIAGNOSIS_SUBS
from zephyr.feedback_loop.diagnosers.health import _SUBMODULES as _HEALTH_SUBS
from zephyr.feedback_loop.diagnosers.reliability import _SUBMODULES as _RELIABILITY_SUBS

# 子包 -> 叶子列表（顺序对齐DW-242分类，方便未来AI理解）
_SUBPKG_GROUPS = (
    ("cognitive", _COGNITIVE_SUBS),
    ("diagnosis", _DIAGNOSIS_SUBS),
    ("health", _HEALTH_SUBS),
    ("reliability", _RELIABILITY_SUBS),
)

# 叶子名 -> 所属子包（兼容垫片重定向映射）
_LEAF_TO_SUBPKG = {
    _leaf: _subpkg
    for _subpkg, _subs in _SUBPKG_GROUPS
    for _leaf in _subs
}

_SUBMODULES = _COGNITIVE_SUBS + _DIAGNOSIS_SUBS + _HEALTH_SUBS + _RELIABILITY_SUBS

_PREFIX = "zephyr.trading.feedback_loop.diagnosers."


class _LeafAliasLoader(importlib.abc.Loader):
    """加载器：把旧路径别名模块指向真实子包叶子模块（共享同一模块对象）。"""

    def __init__(self, real_name):
        self._real_name = real_name

    def create_module(self, spec):
        return importlib.import_module(self._real_name)

    def exec_module(self, module):
        # 真实模块在 create_module 中已完成加载与执行；别名模块直接复用，无需重复。
        pass


class _LeafAliasFinder(importlib.abc.MetaPathFinder):
    """兼容垫片finder：拦截 ``diagnosers.<leaf>`` 旧路径，重定向到 ``diagnosers.<subpkg>.<leaf>``。

    仅处理已注册的单段叶子名；不影响真实子包(如 diagnosers.cognitive)的导入。
    """

    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith(_PREFIX):
            return None
        leaf = fullname[len(_PREFIX):]
        if "." in leaf or leaf not in _LEAF_TO_SUBPKG:
            return None
        real_name = f"{_PREFIX}{_LEAF_TO_SUBPKG[leaf]}.{leaf}"
        return importlib.util.spec_from_loader(fullname, _LeafAliasLoader(real_name))


sys.meta_path.append(_LeafAliasFinder())


def __getattr__(name):
    if name in _LEAF_TO_SUBPKG:
        mod = importlib.import_module(
            f"zephyr.trading.feedback_loop.diagnosers.{_LEAF_TO_SUBPKG[name]}.{name}"
        )
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "cognitive",
    "diagnosis",
    "health",
    "reliability",
    "action_composition_health_monitor",
    "adaptive_param_tuning",
    "amplification_guard",
    "api_dependency_metrics",
    "auto_diagnosis",
    "burn_rate_alerter",
    "burnout_alarm",
    "capacity_aware_repair",
    "causal_inference_engine",
    "cognitive_load",
    "cognitive_load_budget",
    "cold_start_conservative_mode",
    "collaborative_learning",
    "confidence_decomposer",
    "context_truncation",
    "context_window_pressure_manager",
    "counterfactual",
    "cross_guard_conflict_detector",
    "cross_session_consistency_validator",
    "data_volume_growth_monitor",
    "diagnosis_engine",
    "diagnosis_kpi",
    "dr_resilience_metrics",
    "e2e_integration_health",
    "feedback_delay_compensator",
    "fle_dogfood_monitor",
    "fle_self_slo_metrics",
    "gamification",
    "global_health_map",
    "guard_interaction_topology_mapper",
    "guard_self_consistency_auditor",
    "human_anomaly_flood_detector",
    "impact_predictor",
    "incident_knowledge_injector",
    "interactive_diagnosis",
    "knowledge_bus_factor_monitor",
    "knowledge_market",
    "latency_slo",
    "llm_provider_integrity",
    "llm_quality_regression",
    "memory_self_check",
    "meta_guard_latency_budget",
    "model_health",
    "model_rotation",
    "model_rotation_v2",
    "model_version_semantic_drift",
    "mtti_tracker",
    "nonstationary_effectiveness",
    "numerical_stability_guard",
    "operational_seasonality",
    "prompt_fingerprint",
    "prompt_sanitizer",
    "recovery_time_stats",
    "regime_gain_scheduling",
    "retirement_planner",
    "self_benchmark",
    "self_bottleneck_detector",
    "self_health_monitor",
    "self_llm_observability",
    "slo_capacity_metrics",
    "socratic_questions",
    "statistical_hygiene_auditor",
    "system_entropy_monitor",
    "temporal_integrity_guard",
    "timezone_semantic_reasoner",
    "toil_quantification",
    "tone_adapter",
    "tone_adapter_v2",
    "value_added_baseline",
    "vertical_self_assessment",
    "zombie_fle_detector",
]
