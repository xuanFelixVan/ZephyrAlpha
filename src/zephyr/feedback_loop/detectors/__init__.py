# [DOMAIN] D_FEEDBACK_LOOP
# [A_module] module_id=MOD-UNK_detectors | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors
# [INVARIANTS] __all__列表不变(公开叶子API不变); 旧路径detectors.<leaf>保持可导入(兼容垫片)
# [MODIFY-GUARD] 新增子模块须同步更新对应子包的_SUBMODULES和本文件__all__
# [CONSUMERS] zephyr.integration.runtime_core.feedback_loop; detectors子包消费者
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AttributeError: 模块无此属性
# [TESTS] tests/test_feedback_loop_imports.py
# [TTL] permanent
"""feedback-loop.detectors — GOV-DOC-018: 60个叶子模块拆分为5个逻辑子包(anomaly/correlation/drift/guard/reliability)。

兼容垫片：旧导入路径 ``zephyr.feedback_loop.detectors.<leaf>`` 继续可用，
实际模块已迁移到 ``zephyr.feedback_loop.detectors.<subpkg>.<leaf>``。
``__getattr__`` 处理 ``from detectors import <leaf>`` 形式；
``_LeafAliasFinder`` 处理 ``from detectors.<leaf> import X`` / ``import detectors.<leaf>`` 形式。
"""

import importlib
import importlib.abc
import importlib.util
import sys

from zephyr.feedback_loop.detectors.anomaly import _SUBMODULES as _ANOMALY_SUBS
from zephyr.feedback_loop.detectors.correlation import _SUBMODULES as _CORRELATION_SUBS
from zephyr.feedback_loop.detectors.drift import _SUBMODULES as _DRIFT_SUBS
from zephyr.feedback_loop.detectors.guard import _SUBMODULES as _GUARD_SUBS
from zephyr.feedback_loop.detectors.reliability import _SUBMODULES as _RELIABILITY_SUBS

# 子包 -> 叶子列表（顺序对齐DW-244分类，方便未来AI理解）
_SUBPKG_GROUPS = (
    ("anomaly", _ANOMALY_SUBS),
    ("correlation", _CORRELATION_SUBS),
    ("drift", _DRIFT_SUBS),
    ("guard", _GUARD_SUBS),
    ("reliability", _RELIABILITY_SUBS),
)

# 叶子名 -> 所属子包（兼容垫片重定向映射）
_LEAF_TO_SUBPKG = {
    _leaf: _subpkg
    for _subpkg, _subs in _SUBPKG_GROUPS
    for _leaf in _subs
}

_SUBMODULES = _ANOMALY_SUBS + _DRIFT_SUBS + _GUARD_SUBS + _RELIABILITY_SUBS + _CORRELATION_SUBS

_PREFIX = "zephyr.feedback_loop.detectors."


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
    """兼容垫片finder：拦截 ``detectors.<leaf>`` 旧路径，重定向到 ``detectors.<subpkg>.<leaf>``。

    仅处理已注册的单段叶子名；不影响真实子包(如 detectors.anomaly)的导入。
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
            f"zephyr.feedback_loop.detectors.{_LEAF_TO_SUBPKG[name]}.{name}"
        )
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "anomaly",
    "correlation",
    "drift",
    "guard",
    "reliability",
    "action_efficacy_decay_detector",
    "action_interaction_detector",
    "action_side_effect_cumulative_detector",
    "agent_trajectory_anomaly_detector",
    "alert_desensitization_curve",
    "anomaly_clustering",
    "anomaly_detector",
    "autoscale_remediation",
    "blast_radius",
    "blast_radius_budget",
    "capacity_forecast",
    "chaos_engineering",
    "concept_drift",
    "config_drift",
    "context_window_contamination_detector",
    "cross_signal_validator",
    "cross_system_correlator",
    "decision_provenance",
    "dependency_freshness_monitor",
    "diminishing_returns_detector",
    "ebpf_monitor",
    "emergent_behavior_detector",
    "ensemble_detector",
    "ensemble_drift",
    "external_health",
    "external_validation_checkpoint",
    "flag_lifecycle",
    "flapping_detector",
    "fle_performance_regression_detector",
    "gradual_poisoning_detector",
    "guard_cascade_detector",
    "guard_oscillation_detector",
    "heisenbug_detector",
    "infinite_loop_detector",
    "intermittent_failure_pattern",
    "log_anomaly",
    "maintenance_coordinator",
    "metric_cardinality_guard",
    "multi_signal_correlator",
    "openfeature",
    "otel_adapter",
    "placebo_action_detector",
    "positive_feedback_defense",
    "recursive_diagnosis_trust_evaluator",
    "regulatory_audit",
    "resolution_tracker",
    "rumor_noise_filter",
    "runbook_executor",
    "self_audit",
    "self_diagnosis_data_leak_detector",
    "self_ha",
    "silent_corruption_detector",
    "synthetic_anomaly_generator",
    "temporal_coherence_of_self_model",
    "temporal_pattern",
    "trace_causal_bridge",
    "traffic_replay_validator",
    "trend_cycle_separator",
    "version_migrator",
]
