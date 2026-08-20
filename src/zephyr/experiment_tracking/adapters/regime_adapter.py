# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M4
# [MODULE] zephyr.experiment_tracking.adapters.regime_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker (get_tracker); typing.TYPE_CHECKING (regime 类型仅静态检查，运行时鸭子类型——破 regime↔experiment_tracking 循环)
# [CONSUMERS] regime 验证/运行入口（track 时 lazy import 调用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] RegimeProbabilities/ShrinkageResult → 实验跟踪 run（params/metrics/tags）；tracker 降级时 no-op 不抛；lineage tags 串联上游 run_id
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 失败→stderr warning 不抛（不崩 regime 业务）；run_id 返回（NullBackend 返回 "null-run"）
# [TESTS] tests/experiment_tracking/test_component_adapters.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
# [ALGO_FLOW]
# I1: probabilities(RegimeProbabilities 鸭子类型: probabilities/dominant_regime/dominant_frequency/confidence) + shrinkage(ShrinkageResult: value/confidence_signal/risk_signal/shrinkage_enabled)
# I2: feature_stats(输入特征统计,可选) + model_params(HMM 超参,可选) + lineage(上游 run_id 映射,可选)
# F1: _extract_metrics(输出状态分布 per-state 概率 + confidence + shrinkage 三值)
# F2: track_regime_detection(start_run(component=regime-detector) → log_params/log_metrics → run_id)
# O1: run_id（NullBackend="null-run"）
# [/ALGO_FLOW]
"""L_INFRA_TELEMETRY — regime_detector 检测结果 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。

把一次 ``RegimeDetector.detect`` 产出（7 态概率分布 + Shrinkage）翻译为一个实验跟踪 run：
输入特征统计 + 输出状态分布 + 模型参数（50 号 §3 ⑥ 接入要求）。运行时全鸭子类型
（TYPE_CHECKING 隔离，不 import regime 域，破包级循环）。

依据: 50_backtest_observability_workplan §3 ⑥
Version: 0.1.0
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

from zephyr.experiment_tracking.experiment_tracker import get_tracker

if TYPE_CHECKING:  # 仅静态类型检查，运行时不 import regime（破循环）
    from zephyr.regime.core.regime_detector import RegimeProbabilities, ShrinkageResult

__all__: Final = ["track_regime_detection"]

_COMPONENT = "regime-detector"


def track_regime_detection(
    probabilities: "RegimeProbabilities",
    shrinkage: "ShrinkageResult | None" = None,
    *,
    feature_stats: dict[str, Any] | None = None,
    model_params: dict[str, Any] | None = None,
    lineage: dict[str, str] | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把一次 regime 检测产出记录为一个实验跟踪 run。

    Args:
        probabilities: 7 态概率分布（鸭子类型，读 probabilities/dominant_regime/
            dominant_frequency/confidence）。
        shrinkage: Shrinkage 结果（可选；None 时跳过 shrinkage 指标）。
        feature_stats: 输入特征统计（可选，写入 params，如特征数/缺失率/日期范围）。
        model_params: HMM 模型超参（可选，写入 params）。
        lineage: 上游零件 run_id 映射（如 {"feature_run_id": ...}），写入 tags 串联全链路。
        extra_tags: 额外 tags（可选）。

    Returns:
        run_id（NullBackend 返回 "null-run"）。
    """
    tracker = get_tracker()
    tags: dict[str, str] = {
        "component": _COMPONENT,
        "dominant_regime": str(probabilities.dominant_regime),
    }
    if shrinkage is not None:
        tags["shrinkage_enabled"] = str(shrinkage.shrinkage_enabled)
    if lineage:
        tags.update({f"lineage_{k}": str(v) for k, v in lineage.items()})
    if extra_tags:
        tags.update({k: str(v) for k, v in extra_tags.items()})

    params: dict[str, Any] = dict(model_params or {})
    if feature_stats:
        params.update({f"feature_{k}": v for k, v in feature_stats.items()})

    metrics: dict[str, float] = {
        "confidence": float(probabilities.confidence),
        "dominant_frequency": float(probabilities.dominant_frequency),
    }
    for state, p in probabilities.probabilities.items():
        metrics[f"prob_{state}"] = float(p)
    if shrinkage is not None:
        metrics["shrinkage_value"] = float(shrinkage.value)
        metrics["confidence_signal"] = float(shrinkage.confidence_signal)
        metrics["risk_signal"] = float(shrinkage.risk_signal)

    run_name = f"regime_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        if params:
            run.log_params(params)
        run.log_metrics(metrics)
    return run.run_id
