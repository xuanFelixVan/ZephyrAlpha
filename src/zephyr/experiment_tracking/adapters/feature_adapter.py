# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M4
# [MODULE] zephyr.experiment_tracking.adapters.feature_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker (get_tracker); pandas 仅 TYPE_CHECKING（运行时鸭子类型）
# [CONSUMERS] regime 特征构建入口（track 时 lazy import 调用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 特征矩阵 DataFrame → 实验跟踪 run（schema/缺失率/快照 artifact）；tracker 降级 no-op 不抛；空 DataFrame 仍记录（metrics=0）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 失败→stderr warning 不抛（不崩特征业务）；run_id 返回（NullBackend 返回 "null-run"）
# [TESTS] tests/experiment_tracking/test_component_adapters.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
# [ALGO_FLOW]
# I1: features(特征矩阵 DataFrame 鸭子类型: columns/shape/isna/index) + builder_info(构建参数,可选) + lineage(上游 run_id,可选)
# F1: _extract_metrics(行数/列数/整体缺失率/日期范围)
# F2: _log_schema_artifact(列名 schema CSV + 前 snapshot_rows 行快照 CSV)
# F3: track_feature_build(start_run(component=feature-build) → log_* → run_id)
# O1: run_id（NullBackend="null-run"）
# [/ALGO_FLOW]
"""L_INFRA_TELEMETRY — regime_feature_builder 特征矩阵 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。

把一次特征构建产出（DataFrame）翻译为一个实验跟踪 run：特征矩阵 schema + 缺失率 +
快照 artifact（50 号 §3 ⑥ 接入要求）。运行时全鸭子类型（不 import regime 域）。

依据: 50_backtest_observability_workplan §3 ⑥
Version: 0.1.0
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

from zephyr.experiment_tracking.experiment_tracker import get_tracker

if TYPE_CHECKING:  # 仅静态类型检查
    import pandas as pd

__all__: Final = ["track_feature_build"]

_COMPONENT = "feature-build"


def track_feature_build(
    features: "pd.DataFrame",
    *,
    builder_info: dict[str, Any] | None = None,
    snapshot_rows: int = 20,
    lineage: dict[str, str] | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把一次特征矩阵构建记录为一个实验跟踪 run。

    Args:
        features: 特征矩阵（DataFrame 鸭子类型，读 columns/shape/isna/index）。
        builder_info: 构建参数（可选，写入 params，如 start/end/数据源表）。
        snapshot_rows: 快照 artifact 保留前 N 行（0=不加快照）。
        lineage: 上游零件 run_id 映射，写入 tags 串联全链路。
        extra_tags: 额外 tags（可选）。

    Returns:
        run_id（NullBackend 返回 "null-run"）。
    """
    tracker = get_tracker()
    n_rows, n_cols = (int(features.shape[0]), int(features.shape[1])) if features.shape else (0, 0)
    total_cells = n_rows * n_cols
    nan_cells = int(features.isna().sum().sum()) if total_cells else 0
    missing_rate = nan_cells / total_cells if total_cells else 0.0

    tags: dict[str, str] = {"component": _COMPONENT}
    if lineage:
        tags.update({f"lineage_{k}": str(v) for k, v in lineage.items()})
    if extra_tags:
        tags.update({k: str(v) for k, v in extra_tags.items()})

    params: dict[str, Any] = dict(builder_info or {})
    params["n_features"] = n_cols
    if n_rows and hasattr(features.index, "min"):
        params["index_min"] = str(features.index.min())
        params["index_max"] = str(features.index.max())

    metrics: dict[str, float] = {
        "rows": float(n_rows),
        "cols": float(n_cols),
        "missing_rate": float(missing_rate),
    }

    run_name = f"feature_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        run.log_params(params)
        run.log_metrics(metrics)
        # schema artifact：列名清单 CSV（特征矩阵 schema 登记，50 号 §3 ⑥）
        schema_csv = "\n".join(["column"] + [str(c) for c in features.columns]).encode("utf-8")
        run.log_artifact_bytes(schema_csv, "feature_schema.csv", artifact_path="schema")
        if snapshot_rows > 0 and n_rows:
            snap_csv = features.head(snapshot_rows).to_csv(index=True).encode("utf-8")
            run.log_artifact_bytes(snap_csv, "feature_snapshot.csv", artifact_path="snapshot")
    return run.run_id
