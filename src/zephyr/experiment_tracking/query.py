# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md
# [MODULE] zephyr.experiment_tracking.query
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.config (load_config); zephyr.experiment_tracking.models (RunSummary/RunDetail)
# [CONSUMERS] zephyr.frontend.dashboard ; AI/人查询
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] list_runs/get_run/compare_runs/download_artifact 统一 JSON 源；查询失败返回空不抛
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询失败→返回空列表/None + warning 不抛
# [TESTS] tests/experiment_tracking/test_experiment_tracker.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — 实验跟踪查询接口（统一本地 JSON 源，MLflow 已退役）。

list_runs / get_run 扫 fallback JSON 目录返回 RunSummary / RunDetail；
download_artifact 按 run 目录路径规则读 artifact bytes（nav CSV / report MD）。
Panel/AI/脚本只消费统一模型。

依据: 51_panel_experiment_history_mlflow_retirement.md 工作流 A2/B1
Version: 0.2.0（MLflow 退役，单一 JSON 源 + download_artifact）
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Optional

from zephyr.experiment_tracking.config import ExperimentTrackingConfig, load_config
from zephyr.experiment_tracking.models import RunDetail, RunSummary

_logger = logging.getLogger(__name__)

__all__: Final = ["list_runs", "get_run", "compare_runs", "download_artifact", "download_artifact_text"]


def _parse_dt(s: str | None) -> datetime | None:
    """解析 ISO 字符串为 datetime（失败返回 None）。"""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _parse_passed(metrics: dict[str, Any], tags: dict[str, Any]) -> bool | None:
    """从 metrics/tags 解析 C1 passed（metrics.passed=1.0/0.0 优先，tags.passed 字符串兜底）。

    修复预存 bug：RunSummary.passed 为必填位（无默认值），旧构造未传 → TypeError
    被 list_runs/get_run try/except 吞掉，fallback 查询静默返空。
    """
    v = metrics.get("passed")
    if v is not None:
        try:
            return bool(float(v))
        except (TypeError, ValueError):
            pass
    t = tags.get("passed")
    if isinstance(t, str) and t in ("True", "False"):
        return t == "True"
    return None


def _meta_to_summary(meta: dict[str, Any], component: str) -> RunSummary:
    """fallback run_meta.json dict → RunSummary。"""
    metrics = {k: float(v) for k, v in meta.get("metrics", {}).items()}
    tags = dict(meta.get("tags", {}))
    return RunSummary(
        run_id=meta.get("run_id", ""),
        component=meta.get("component", component),
        run_name=meta.get("run_name", ""),
        status=meta.get("status", ""),
        start_time=_parse_dt(meta.get("start_time")),
        end_time=_parse_dt(meta.get("end_time")),
        passed=_parse_passed(metrics, tags),
        tags=tags,
        metrics=metrics,
        artifact_uris=[
            # 防御：旧版 fallback meta 的 artifacts 为 list[str]（2026-08-07 前写入）
            a if isinstance(a, str) else (a.get("local_path") or a.get("filename", ""))
            for a in meta.get("artifacts", [])
        ],
    )


def _load_meta(meta_path: Path) -> dict[str, Any] | None:
    """读取 run_meta.json（失败返回 None）。"""
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        _logger.warning("query _load_meta 失败(跳过 %s): %s", meta_path, exc)
        return None


def _list_runs_fallback(
    component: str | None,
    cfg: ExperimentTrackingConfig,
) -> list[RunSummary]:
    """扫 fallback_dir JSON 目录。"""
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


def _get_run_fallback(
    run_id: str,
    component: str | None,
    cfg: ExperimentTrackingConfig,
) -> RunDetail | None:
    """扫 fallback_dir 找 run_meta.json。

    artifact_paths 契约（dict[str, str]，与 models.py 声明一致）：
    {artifact名: 本地绝对路径}——local_path 类 artifact 直接取 local_path；
    bytes 类 artifact（log_artifact_bytes 落盘）按 run 目录重建绝对路径
    {run_dir}/{artifact_path}/{filename}，信息零丢失。
    治本留痕：旧版曾赋 list[dict] 并注释"models.py 声明为预存类型 bug"——
    实测唯一消费者 strategy_deviation_monitor.load_backtest_returns_from_experiment
    按 dict 调 .items()，list 形状使其 broad-except 静默降级 None
    （回测-实盘偏差监控基准供给桥失效）。本实现按声明归一，契约三方对齐。
    """
    base = cfg.fallback_dir
    if not base.exists():
        return None
    comps = [component] if component else [p.name for p in base.iterdir() if p.is_dir()]
    for comp in comps:
        run_dir = base / comp / run_id
        meta_path = run_dir / "run_meta.json"
        if meta_path.exists():
            meta = _load_meta(meta_path)
            if meta is None:
                return None
            metrics = {k: float(v) for k, v in meta.get("metrics", {}).items()}
            tags = dict(meta.get("tags", {}))
            return RunDetail(
                run_id=meta.get("run_id", run_id),
                component=meta.get("component", comp),
                run_name=meta.get("run_name", ""),
                status=meta.get("status", ""),
                start_time=_parse_dt(meta.get("start_time")),
                end_time=_parse_dt(meta.get("end_time")),
                passed=_parse_passed(metrics, tags),
                tags=tags,
                metrics=metrics,
                params=dict(meta.get("params", {})),
                artifact_paths=_build_artifact_paths(meta.get("artifacts", []), run_dir),
            )
    return None


def _build_artifact_paths(artifacts: list[Any], run_dir: Path) -> dict[str, str]:
    """把 run_meta.json 的 artifacts 列表归一为 {artifact名: 本地绝对路径} dict。

    三种条目形态（FallbackBackend 写入侧对称）：
      - bytes artifact: {"filename", "artifact_path"} → 名="artifact_path/filename"，
        值=run_dir 下重建的落盘绝对路径
      - 本地路径 artifact: {"local_path", "artifact_path"} → 名=artifact_path 或
        local_path 文件名，值=local_path
      -  legacy str（2026-08-07 前写入）：名=值=原字符串
    """
    paths: dict[str, str] = {}
    for a in artifacts:
        if isinstance(a, str):  # legacy list[str] 形态
            paths[a] = a
            continue
        if not isinstance(a, dict):
            continue
        if a.get("local_path"):
            local_path = str(a["local_path"])
            name = a.get("artifact_path") or Path(local_path).name
            paths[str(name)] = local_path
        elif a.get("filename"):
            filename = str(a["filename"])
            artifact_path = a.get("artifact_path")
            name = f"{artifact_path}/{filename}" if artifact_path else filename
            disk = run_dir / str(artifact_path) / filename if artifact_path else run_dir / filename
            paths[name] = str(disk)
    return paths


def list_runs(
    component: str | None = None,
    max_results: int = 100,
    config: ExperimentTrackingConfig | None = None,
) -> list[RunSummary]:
    """列出 runs（统一返回 RunSummary，单一 JSON 源）。

    Args:
        component: 零件类型过滤（None=所有零件）。
        max_results: 最大返回数。
        config: 配置（None=load_config）。

    Returns:
        RunSummary 列表（查询失败返回空列表不抛）。
    """
    cfg = config or load_config()
    try:
        return _list_runs_fallback(component, cfg)[:max_results]
    except Exception as exc:  # noqa: BLE001
        _logger.warning("list_runs 失败(返回空): %s", exc)
        return []


def get_run(
    run_id: str,
    component: str | None = None,
    config: ExperimentTrackingConfig | None = None,
) -> RunDetail | None:
    """获取单次 run 详情（统一返回 RunDetail，单一 JSON 源）。

    Args:
        run_id: 运行 ID。
        component: 零件类型（fallback 扫描需要）。
        config: 配置。

    Returns:
        RunDetail 或 None（查询失败返回 None 不抛）。
    """
    cfg = config or load_config()
    try:
        return _get_run_fallback(run_id, component, cfg)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("get_run 失败(返回 None): %s", exc)
        return None


def compare_runs(
    run_ids: list[str],
    component: str | None = None,
    config: ExperimentTrackingConfig | None = None,
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


def download_artifact(
    run_id: str,
    component: str,
    artifact_path: str | None = None,
    filename: str | None = None,
    config: ExperimentTrackingConfig | None = None,
) -> bytes | None:
    """从 fallback run 目录读 artifact bytes。

    路径规则 = {fallback_dir}/{component}/{run_id}/{artifact_path or ""}/{filename}
    （与 FallbackBackend.log_artifact_bytes 写入侧对称）。

    Args:
        run_id: 运行 ID。
        component: 零件类型。
        artifact_path: 产物子目录（如 "nav" / "report"；None=run 根目录）。
        filename: 产物文件名（如 "nav_curve_baseline.csv"）。
        config: 配置。

    Returns:
        bytes 或 None（不存在/读失败返回 None + warning，不抛——契约一致）。
    """
    if not filename:
        return None
    cfg = config or load_config()
    try:
        path = cfg.fallback_dir / component / run_id
        if artifact_path:
            path = path / artifact_path
        path = path / filename
        if not path.exists():
            _logger.warning("download_artifact 不存在: %s", path)
            return None
        return path.read_bytes()
    except Exception as exc:  # noqa: BLE001
        _logger.warning("download_artifact 失败(返回 None): %s", exc)
        return None


def download_artifact_text(
    run_id: str,
    component: str,
    artifact_path: str | None = None,
    filename: str | None = None,
    config: ExperimentTrackingConfig | None = None,
) -> str | None:
    """download_artifact 薄包装（返回 str 或 None，便于直接读 c1_summary.md）。"""
    data = download_artifact(run_id, component, artifact_path, filename, config)
    if data is None:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        _logger.warning("download_artifact_text 解码失败(返回 None): %s", exc)
        return None
