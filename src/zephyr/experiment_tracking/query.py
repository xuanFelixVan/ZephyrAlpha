# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.query
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.config (load_config); zephyr.experiment_tracking.models (RunSummary/RunDetail); mlflow (lazy); pandas (lazy)
# [CONSUMERS] zephyr.frontend.dashboard ; AI/人查询
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] list_runs/get_run/compare_runs 屏蔽 mlflow vs JSON 双源；查询失败返回空不抛
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询失败→返回空列表/None + warning 不抛
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪查询接口（屏蔽 MLflow vs 降级 JSON 差异）。

list_runs / get_run 对外统一返回 RunSummary / RunDetail，底层按 mlflow 是否可用自动选
MLflow search_runs 或扫 fallback JSON 目录。Panel/AI/脚本只消费统一模型，不感知双源。

依据: backtest_observability_mlflow_plan.md M1 query.py 设计
Version: 0.1.0
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Optional

from zephyr.experiment_tracking.config import ExperimentTrackingConfig, load_config
from zephyr.experiment_tracking.models import RunDetail, RunSummary

# lazy import mlflow——与 experiment_tracker 同策略
try:  # pragma: no cover - 环境依赖
    import mlflow  # type: ignore[import-not-found]

    _MLFLOW_AVAILABLE = True
except ImportError:  # pragma: no cover
    mlflow = None  # type: ignore[assignment]
    _MLFLOW_AVAILABLE = False

_logger = logging.getLogger(__name__)

__all__: Final = ["list_runs", "get_run", "compare_runs"]


def _exp_name(component: str, prefix: str) -> str:
    """component → experiment 名（与 _MLflowBackend._exp_name 一致）。"""
    return f"{prefix}{component}"


def _parse_dt(s: Optional[str]) -> Optional[datetime]:
    """解析 ISO 字符串为 datetime（失败返回 None）。"""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _from_ms(ms: Optional[int]) -> Optional[datetime]:
    """毫秒时间戳 → datetime（失败返回 None）。"""
    if ms is None:
        return None
    try:
        return datetime.fromtimestamp(ms / 1000.0)
    except (ValueError, OSError):
        return None


def _row_to_summary(row: Any, component: str) -> RunSummary:
    """mlflow RunData row → RunSummary。"""
    data = row.data
    return RunSummary(
        run_id=row.info.run_id,
        component=component,
        run_name=row.info.run_name or "",
        status=row.info.status or "",
        start_time=_from_ms(row.info.start_time),
        end_time=_from_ms(row.info.end_time),
        tags=dict(data.tags) if data and data.tags else {},
        metrics=dict(data.metrics) if data and data.metrics else {},
        artifact_uris=[],
    )


def _list_runs_mlflow(
    component: Optional[str],
    max_results: int,
    cfg: ExperimentTrackingConfig,
) -> list[RunSummary]:
    """mlflow 可用时：search_runs 查询。"""
    import pandas as pd  # mlflow search 依赖 pandas

    client = mlflow.tracking.MlflowClient(tracking_uri=cfg.tracking_uri)  # type: ignore[union-attr]
    if component is None:
        experiments = client.search_experiments()
        runs: list[Any] = []
        for exp in experiments:
            if exp.name.startswith(cfg.experiment_prefix):
                runs.extend(client.search_runs([exp.experiment_id], max_results=max_results))
    else:
        exp_name = _exp_name(component, cfg.experiment_prefix)
        exp = client.get_experiment_by_name(exp_name)
        if exp is None:
            return []
        runs = client.search_runs([exp.experiment_id], max_results=max_results)
    comp = component or ""
    return [_row_to_summary(r, comp or r.info.run_name.split("_")[0]) for r in runs]


def _meta_to_summary(meta: dict[str, Any], component: str) -> RunSummary:
    """fallback run_meta.json dict → RunSummary。"""
    return RunSummary(
        run_id=meta.get("run_id", ""),
        component=meta.get("component", component),
        run_name=meta.get("run_name", ""),
        status=meta.get("status", ""),
        start_time=_parse_dt(meta.get("start_time")),
        end_time=_parse_dt(meta.get("end_time")),
        tags=dict(meta.get("tags", {})),
        metrics={k: float(v) for k, v in meta.get("metrics", {}).items()},
        artifact_uris=[a.get("local_path", "") for a in meta.get("artifacts", [])],
    )


def _load_meta(meta_path: Path) -> Optional[dict[str, Any]]:
    """读取 run_meta.json（失败返回 None）。"""
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        _logger.warning("query _load_meta 失败(跳过 %s): %s", meta_path, exc)
        return None


def _list_runs_fallback(
    component: Optional[str],
    cfg: ExperimentTrackingConfig,
) -> list[RunSummary]:
    """mlflow 不可用时：扫 fallback_dir JSON 目录。"""
    base = cfg.fallback_dir
    if not base.exists():
        return []
    summaries: list[RunSummary] = []
    comps = [component] if component else [p.name for p in base.iterdir() if p.is_dir()]
    for comp in comps:
        comp_dir = base / comp
        if not comp_dir.is_dir():
            continue
        for run_dir in comp_dir.iterdir():
            if not run_dir.is_dir():
                continue
            meta = _load_meta(run_dir / "run_meta.json")
            if meta is not None:
                summaries.append(_meta_to_summary(meta, comp))
    return summaries


def _get_run_mlflow(
    run_id: str,
    component: Optional[str],
    cfg: ExperimentTrackingConfig,
) -> Optional[RunDetail]:
    """mlflow 可用时：get_run 查详情。"""
    client = mlflow.tracking.MlflowClient(tracking_uri=cfg.tracking_uri)  # type: ignore[union-attr]
    try:
        run = client.get_run(run_id)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("query get_run mlflow 失败(返回 None): %s", exc)
        return None
    data = run.data
    comp = component or run.info.run_name.split("_")[0] if run.info.run_name else ""
    arts: list[str] = []
    try:
        arts = client.list_artifacts(run_id)
        arts = [a.path for a in arts]
    except Exception:  # noqa: BLE001
        pass
    return RunDetail(
        run_id=run.info.run_id,
        component=comp,
        run_name=run.info.run_name or "",
        status=run.info.status or "",
        start_time=_from_ms(run.info.start_time),
        end_time=_from_ms(run.info.end_time),
        tags=dict(data.tags) if data and data.tags else {},
        metrics={k: float(v) for k, v in (data.metrics or {}).items()},
        params=dict(data.params) if data and data.params else {},
        artifact_paths=arts,
    )


def _get_run_fallback(
    run_id: str,
    component: Optional[str],
    cfg: ExperimentTrackingConfig,
) -> Optional[RunDetail]:
    """mlflow 不可用时：扫 fallback_dir 找 run_meta.json。"""
    base = cfg.fallback_dir
    if not base.exists():
        return None
    comps = [component] if component else [p.name for p in base.iterdir() if p.is_dir()]
    for comp in comps:
        meta_path = base / comp / run_id / "run_meta.json"
        if meta_path.exists():
            meta = _load_meta(meta_path)
            if meta is None:
                return None
            return RunDetail(
                run_id=meta.get("run_id", run_id),
                component=meta.get("component", comp),
                run_name=meta.get("run_name", ""),
                status=meta.get("status", ""),
                start_time=_parse_dt(meta.get("start_time")),
                end_time=_parse_dt(meta.get("end_time")),
                tags=dict(meta.get("tags", {})),
                metrics={k: float(v) for k, v in meta.get("metrics", {}).items()},
                params=dict(meta.get("params", {})),
                artifact_paths=[a.get("local_path", "") for a in meta.get("artifacts", [])],
            )
    return None


def list_runs(
    component: Optional[str] = None,
    max_results: int = 100,
    config: Optional[ExperimentTrackingConfig] = None,
) -> list[RunSummary]:
    """列出 runs（统一返回 RunSummary，屏蔽 mlflow vs JSON）。

    Args:
        component: 零件类型过滤（None=所有零件）。
        max_results: 最大返回数。
        config: 配置（None=load_config）。

    Returns:
        RunSummary 列表（查询失败返回空列表不抛）。
    """
    cfg = config or load_config()
    try:
        if _MLFLOW_AVAILABLE and cfg.enable_tracking:
            return _list_runs_mlflow(component, max_results, cfg)
        return _list_runs_fallback(component, cfg)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("list_runs 失败(返回空): %s", exc)
        return []


def get_run(
    run_id: str,
    component: Optional[str] = None,
    config: Optional[ExperimentTrackingConfig] = None,
) -> Optional[RunDetail]:
    """获取单次 run 详情（统一返回 RunDetail，屏蔽 mlflow vs JSON）。

    Args:
        run_id: 运行 ID。
        component: 零件类型（fallback 扫描需要，mlflow 可省）。
        config: 配置。

    Returns:
        RunDetail 或 None（查询失败返回 None 不抛）。
    """
    cfg = config or load_config()
    try:
        if _MLFLOW_AVAILABLE and cfg.enable_tracking:
            return _get_run_mlflow(run_id, component, cfg)
        return _get_run_fallback(run_id, component, cfg)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("get_run 失败(返回 None): %s", exc)
        return None


def compare_runs(
    run_ids: list[str],
    component: Optional[str] = None,
    config: Optional[ExperimentTrackingConfig] = None,
) -> list[RunDetail]:
    """对比多次 run（逐个 get_run，失败的跳过）。

    Args:
        run_ids: 要对比的 run_id 列表。
        component: 零件类型。
        config: 配置。

    Returns:
        RunDetail 列表（查询失败的 run 被跳过，不抛）。
    """
    results: list[RunDetail] = []
    for rid in run_ids:
        detail = get_run(rid, component=component, config=config)
        if detail is not None:
            results.append(detail)
    return results
