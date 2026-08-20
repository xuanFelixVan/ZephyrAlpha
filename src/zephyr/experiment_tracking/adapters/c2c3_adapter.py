# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M4
# [MODULE] zephyr.experiment_tracking.adapters.c2c3_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker (get_tracker); typing.TYPE_CHECKING (backtest 类型仅静态检查，运行时鸭子类型——破 backtest↔experiment_tracking 循环)
# [CONSUMERS] C2/C3 验证入口（track 时 lazy import 调用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] C2ProtectionReport/C3AttributionReport → 实验跟踪 run（params/metrics/tags）；tracker 降级 no-op 不抛；lineage tags 串联上游 run_id
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 失败→stderr warning 不抛（不崩验证业务）；run_id 返回（NullBackend 返回 "null-run"）
# [TESTS] tests/experiment_tracking/test_component_adapters.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
# [ALGO_FLOW]
# I1: C2ProtectionReport(events/mean_improvement/min_improvement/skipped/passed) 或 C3AttributionReport(states/total_avoided/defensive_share/bull_mean_shrinkage/passed)（鸭子类型）
# I2: lineage(上游 run_id 映射,如 c1_run_id) + extra_tags
# F1: track_c2_result(per-event 改善指标 + passed → run) / track_c3_result(per-state 归因 + passed → run)
# O1: run_id（NullBackend="null-run"）
# [/ALGO_FLOW]
"""L_INFRA_TELEMETRY — C2/C3 验证器结果 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。

50 号 §2.2 原定时 C2/C3「未建，建时即接入」——实证 2026-08-20 两验证器已落码
（``c2_extreme_event_protection.evaluate_extreme_event_protection`` /
``c3_throttle_attribution.attribute_throttle``，纯分析函数 + frozen report）。
本 adapter 把两报告翻译为实验跟踪 run，运行时全鸭子类型（TYPE_CHECKING 隔离）。

依据: 50_backtest_observability_workplan §3 ⑥
Version: 0.1.0
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final

from zephyr.experiment_tracking.experiment_tracker import get_tracker

if TYPE_CHECKING:  # 仅静态类型检查，运行时不 import backtest（破循环）
    from zephyr.backtest.regime_validation.c2_extreme_event_protection import (
        C2ProtectionReport,
    )
    from zephyr.backtest.regime_validation.c3_throttle_attribution import (
        C3AttributionReport,
    )

__all__: Final = ["track_c2_result", "track_c3_result"]

_COMPONENT = "c2c3-validation"


def _base_tags(kind: str, passed: bool, lineage: dict[str, str] | None, extra: dict[str, str] | None) -> dict[str, str]:
    tags: dict[str, str] = {"component": _COMPONENT, "kind": kind, "passed": str(passed)}
    if lineage:
        tags.update({f"lineage_{k}": str(v) for k, v in lineage.items()})
    if extra:
        tags.update({k: str(v) for k, v in extra.items()})
    return tags


def track_c2_result(
    report: "C2ProtectionReport",
    *,
    lineage: dict[str, str] | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把 C2 极端事件保护报告记录为一个实验跟踪 run（鸭子类型，只读 report 属性）。"""
    tracker = get_tracker()
    tags = _base_tags("c2", report.passed, lineage, extra_tags)
    metrics: dict[str, float] = {
        "mean_improvement": float(report.mean_improvement),
        "min_improvement": float(report.min_improvement),
        "n_events": float(len(report.events)),
        "n_skipped": float(len(report.skipped)),
        "passed": 1.0 if report.passed else 0.0,
    }
    for e in report.events:
        key = str(e.name).lower().replace(" ", "_")
        metrics[f"{key}_improvement"] = float(e.improvement)
        metrics[f"{key}_dd_baseline"] = float(e.dd_baseline)
        metrics[f"{key}_dd_experiment"] = float(e.dd_experiment)

    run_name = f"c2_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        run.log_params({"n_events": len(report.events), "skipped": list(map(str, report.skipped))})
        run.log_metrics(metrics)
        run.log_artifact_bytes(report.summary.encode("utf-8"), "c2_summary.md", artifact_path="report")
    return run.run_id


def track_c3_result(
    report: "C3AttributionReport",
    *,
    lineage: dict[str, str] | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把 C3 节流归因报告记录为一个实验跟踪 run（鸭子类型，只读 report 属性）。"""
    tracker = get_tracker()
    tags = _base_tags("c3", report.passed, lineage, extra_tags)
    metrics: dict[str, float] = {
        "total_days": float(report.total_days),
        "total_avoided": float(report.total_avoided),
        "defensive_share": float(report.defensive_share),
        "bull_mean_shrinkage": float(report.bull_mean_shrinkage)
        if report.bull_mean_shrinkage is not None
        else float("nan"),
        "passed": 1.0 if report.passed else 0.0,
    }
    for s in report.states:
        key = str(s.state).lower().replace(" ", "_")
        metrics[f"{key}_avoided_return"] = float(s.avoided_return)
        metrics[f"{key}_contribution_share"] = float(s.contribution_share)
        metrics[f"{key}_mean_shrinkage"] = float(s.mean_shrinkage)

    run_name = f"c3_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        run.log_params({"n_states": len(report.states), "total_days": report.total_days})
        run.log_metrics(metrics)
        run.log_artifact_bytes(report.summary.encode("utf-8"), "c3_summary.md", artifact_path="report")
    return run.run_id
