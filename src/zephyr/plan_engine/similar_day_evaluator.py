# [BLUEPRINT] MOD-PLAN-016 | 待统筹登记（44号 §9.3 纪律开关 + 92号 §8.7 M4-④）
# [MODULE] zephyr.plan_engine.similar_day_evaluator
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.reporting.prediction_log_writer(query_predictions); zephyr.plan_engine.brier_calibration(brier_score); zephyr.signal_ashare.similar_day_inference(STRONG_LABEL/FLAT_LABEL/WEAK_LABEL)
# [CONSUMERS] similar_day_inference（walkforward_hit_rate 回填）; G04 参数校准流程（评审建议）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只读 prediction_log（经 query_predictions 公共 API，零裸 SQL）；walk-forward 滚动窗口（预测日 < 评估日，防前视）；命中率 <55% → 建议停用；零样本 → 建议启用（默认安全）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/44_premarket_intraday_decision_upgrade.md §9.3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入校验 fail-closed（ValueError）；query_predictions 的 sqlite3.Error 透传；零样本不抛（返回默认建议）
# [TESTS] tests/plan_engine/test_similar_day_evaluator.py
# [A_module] module_id=MOD-PLAN-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-PLAN-016 — 相似日 KNN 尾盘推演 walk-forward 命中率评估器（44号 §9.3 纪律开关落地）。

设计真源：44号 §9.3（walk-forward 验证命中率 <55% → 自动停用）+ 92号 §8.7
（M4-④ 日志→参数校准反馈闭环）。本模块消费 prediction_log 中
module="plan_engine.scenario_planner" 的 scenario_plan 预测行与 outcome 回写行，
按滚动窗口计算命中率时序与 Brier 校准，输出启用/停用建议。

口径（写清）：
- 预测行：prediction_type="scenario_plan"，payload 含 final_scenario/confidence_scale；
- 真值行：prediction_type="outcome"，payload 含 hit:bool / actual_scenario /
  trend_source； hit=True 表示预测 final_scenario == actual_scenario；
- walk-forward：对每个评估日，仅用 trade_date < 评估日的样本计算命中率
  （防前视偏差，对齐 44号 §9.3 "滚动窗口" 语义）；
- Brier 校准：confidence_scale 作为预测概率代理（1.0=确认，0.5=降信），
  hit:bool 作为 0/1 真值；样本 <3 → brier=None；
- 建议判定：窗口命中率 < hit_rate_floor（默认 0.55）且样本 ≥ min_samples
  → 建议停用（enabled=False）；样本不足 → 建议启用（默认安全，不阻塞新模块）。

与 brier_calibration（MOD-PLAN-010）的分工：MOD-PLAN-010 是通用校准报告器
（W0/W6 消费），本模块是 similar_day_inference 专用纪律开关评估器
（44号 §9.3 命中率阈值 + walk-forward 时序输出）。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final

from zephyr.plan_engine.brier_calibration import brier_score
from zephyr.reporting.prediction_log_writer import query_predictions
from zephyr.signal_ashare.similar_day_inference import (
    FLAT_LABEL,
    STRONG_LABEL,
    WEAK_LABEL,
)

__all__: Final = [
    "SimilarDayEvalConfig",
    "SimilarDayEvalReport",
    "evaluate_similar_day_hit_rate",
]

# 预测/真值族常量（prediction_log 单一账本）
_PREDICTION_TYPE_PLAN: Final = "scenario_plan"
_PREDICTION_TYPE_OUTCOME: Final = "outcome"
_MODULE_LOG_NAME: Final = "plan_engine.scenario_planner"

# 默认配置（44号 §9.3 纪律）
DEFAULT_HIT_RATE_FLOOR: Final = 0.55
DEFAULT_WINDOW_DAYS: Final = 60
DEFAULT_MIN_SAMPLES: Final = 10  # 骨架期样本量守卫（<30 由 calibration_monitor 兜底，此处更宽）
_QUERY_LIMIT: Final = 10000


@dataclass(frozen=True)
class SimilarDayEvalConfig:
    """相似日评估配置（frozen 容器）。"""

    hit_rate_floor: float = DEFAULT_HIT_RATE_FLOOR  # 命中率阈值 <55% → 停用
    window_days: int = DEFAULT_WINDOW_DAYS           # 滚动窗口天数（自然日）
    min_samples: int = DEFAULT_MIN_SAMPLES           # 样本量守卫下限
    module: str = _MODULE_LOG_NAME                   # prediction_log.module 过滤

    def __post_init__(self) -> None:
        if isinstance(self.hit_rate_floor, bool) or not isinstance(
            self.hit_rate_floor, (int, float)
        ) or not 0.0 < float(self.hit_rate_floor) < 1.0:
            raise ValueError(f"hit_rate_floor 非法（须 0<t<1）: {self.hit_rate_floor!r}")
        if isinstance(self.window_days, bool) or not isinstance(self.window_days, int) or self.window_days < 1:
            raise ValueError(f"window_days 非法（须正整数）: {self.window_days!r}")
        if isinstance(self.min_samples, bool) or not isinstance(self.min_samples, int) or self.min_samples < 1:
            raise ValueError(f"min_samples 非法（须正整数）: {self.min_samples!r}")


@dataclass(frozen=True)
class HitRatePoint:
    """walk-forward 命中率时序单点。"""

    eval_date: str          # 评估日（该日收盘后评估）
    window_start: str       # 窗口起点（含）
    window_end: str         # 窗口终点（含，= eval_date）
    sample_size: int        # 窗口内有效样本数
    hit_count: int          # 命中数
    hit_rate: float | None  # 命中率（sample_size=0 → None）
    brier: float | None     # Brier 评分（sample_size<3 → None）
    suggested_enabled: bool  # 建议启用/停用
    reason: str             # 判定原因


@dataclass(frozen=True)
class SimilarDayEvalReport:
    """相似日 walk-forward 评估报告（JSON 可序列化）。"""

    module: str
    eval_date: str
    config: dict[str, Any]
    series: tuple[HitRatePoint, ...]   # 按 eval_date 升序
    latest: HitRatePoint | None        # 最新评估点（series 为空 → None）
    suggested_enabled: bool            # 综合建议（= latest.suggested_enabled）
    walkforward_hit_rate: float | None  # 最新命中率（供 SimilarDayConfig 回填）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return {
            "module": self.module,
            "eval_date": self.eval_date,
            "config": self.config,
            "series": [asdict(p) for p in self.series],
            "latest": asdict(self.latest) if self.latest is not None else None,
            "suggested_enabled": self.suggested_enabled,
            "walkforward_hit_rate": self.walkforward_hit_rate,
        }


def _parse_plan_payload(payload_json: str) -> dict[str, Any] | None:
    """scenario_plan payload → dict；非法 → None。"""
    try:
        payload = json.loads(payload_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None
    scenario = payload.get("final_scenario")
    if not isinstance(scenario, str) or not scenario.strip():
        return None
    confidence = payload.get("confidence_scale")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        confidence = None
    return {
        "final_scenario": scenario.strip(),
        "confidence_scale": float(confidence) if confidence is not None else None,
    }


def _parse_outcome_payload(payload_json: str) -> dict[str, Any] | None:
    """outcome payload → dict；非法/缺 hit → None。"""
    try:
        payload = json.loads(payload_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None
    hit = payload.get("hit")
    if not isinstance(hit, bool):
        return None
    actual = payload.get("actual_scenario")
    return {
        "hit": hit,
        "actual_scenario": actual if isinstance(actual, str) else None,
        "trend_source": payload.get("trend_source"),
    }


def _evaluate_single_window(
    samples: list[tuple[str, bool, float | None]],
    eval_date: str,
    config: SimilarDayEvalConfig,
) -> HitRatePoint:
    """单窗口评估（纯函数）。"""
    n = len(samples)
    hit_count = sum(1 for _, h, _ in samples if h)
    hit_rate = hit_count / n if n > 0 else None

    # Brier 校准（confidence_scale 作为概率代理，hit 作为 0/1）
    brier_pairs = [
        (conf, 1.0 if hit else 0.0)
        for _, hit, conf in samples
        if conf is not None
    ]
    brier: float | None = None
    if len(brier_pairs) >= 3:
        try:
            brier = brier_score(brier_pairs)
        except ValueError:
            brier = None

    # 判定
    if n < config.min_samples:
        suggested = True
        reason = f"样本不足 n={n} < {config.min_samples}，默认启用（不阻塞）"
    elif hit_rate is not None and hit_rate < config.hit_rate_floor:
        suggested = False
        reason = f"命中率 {hit_rate:.2%} < {config.hit_rate_floor:.0%}，建议停用（44号 §9.3 纪律）"
    else:
        suggested = True
        reason = f"命中率 {hit_rate:.2%} ≥ {config.hit_rate_floor:.0%}，维持启用"

    window_start = (
        date.fromisoformat(eval_date) - timedelta(days=config.window_days - 1)
    ).isoformat()
    return HitRatePoint(
        eval_date=eval_date,
        window_start=window_start,
        window_end=eval_date,
        sample_size=n,
        hit_count=hit_count,
        hit_rate=hit_rate,
        brier=brier,
        suggested_enabled=suggested,
        reason=reason,
    )


def _parse_eval_date(eval_date: str | date | None) -> date:
    """解析评估基准日（fail-closed）。"""
    if eval_date is None:
        return date.today()
    if isinstance(eval_date, str):
        try:
            return date.fromisoformat(eval_date)
        except ValueError as exc:
            raise ValueError(f"eval_date 非法（须 YYYY-MM-DD）: {eval_date!r}") from exc
    return eval_date


def _load_prediction_rows(
    cfg: SimilarDayEvalConfig,
    db_path: str | Path | None,
) -> tuple[list[dict], list[dict]]:
    """读取 prediction_log 预测行与真值行。"""
    plan_rows = query_predictions(
        module=cfg.module,
        prediction_type=_PREDICTION_TYPE_PLAN,
        limit=_QUERY_LIMIT,
        db_path=db_path,
    )
    outcome_rows = query_predictions(
        module=cfg.module,
        prediction_type=_PREDICTION_TYPE_OUTCOME,
        limit=_QUERY_LIMIT,
        db_path=db_path,
    )
    return plan_rows, outcome_rows


def _build_samples(
    plan_rows: list[dict],
    outcome_rows: list[dict],
) -> list[tuple[str, bool, float | None]]:
    """装配 (trade_date, hit, confidence) 样本列表（按日期升序）。"""
    plans: dict[str, dict[str, Any]] = {}
    for row in plan_rows:
        parsed = _parse_plan_payload(row["payload_json"])
        if parsed is not None:
            plans[row["trade_date"]] = parsed

    samples: list[tuple[str, bool, float | None]] = []
    for row in outcome_rows:
        parsed = _parse_outcome_payload(row["payload_json"])
        if parsed is None:
            continue
        td = row["trade_date"]
        plan = plans.get(td)
        conf = plan["confidence_scale"] if plan is not None else None
        samples.append((td, parsed["hit"], conf))

    samples.sort(key=lambda s: s[0])
    return samples


def _walk_forward_series(
    samples: list[tuple[str, bool, float | None]],
    eval_d: date,
    cfg: SimilarDayEvalConfig,
) -> list[HitRatePoint]:
    """walk-forward 滚动窗口评估（防前视）。"""
    series: list[HitRatePoint] = []
    if not samples:
        return series

    unique_dates = sorted({s[0] for s in samples})
    for d in unique_dates:
        if d >= eval_d.isoformat():
            continue  # 防前视：只用 < eval_date 的样本
        window_samples = [s for s in samples if s[0] <= d]
        series.append(_evaluate_single_window(window_samples, d, cfg))
    return series


def evaluate_similar_day_hit_rate(
    eval_date: str | date | None = None,
    *,
    config: SimilarDayEvalConfig | None = None,
    db_path: str | Path | None = None,
) -> SimilarDayEvalReport:
    """相似日 walk-forward 命中率评估主入口。

    Args:
        eval_date: 评估基准日（None=今日）；walk-forward 仅用 < eval_date 的样本。
        config: 评估配置（None=默认）。
        db_path: prediction_log 库路径；None=DB_PATH SSoT（测试注入临时库）。

    Returns:
        SimilarDayEvalReport（含命中率时序 + 建议启用/停用）。

    Raises:
        ValueError: eval_date/config 非法（fail-closed）。
        sqlite3.Error: 库级异常透传。
    """
    cfg = config or SimilarDayEvalConfig()
    eval_d = _parse_eval_date(eval_date)

    plan_rows, outcome_rows = _load_prediction_rows(cfg, db_path)
    samples = _build_samples(plan_rows, outcome_rows)
    series = _walk_forward_series(samples, eval_d, cfg)

    # 最新点 = 窗口终点 < eval_date 的最后一个评估日
    latest = series[-1] if series else None

    # 综合建议：最新点启用建议；无样本 → 默认启用（零数据不阻塞）
    suggested_enabled = latest.suggested_enabled if latest is not None else True
    walkforward_hit_rate = latest.hit_rate if latest is not None else None

    return SimilarDayEvalReport(
        module=cfg.module,
        eval_date=eval_d.isoformat(),
        config={
            "hit_rate_floor": cfg.hit_rate_floor,
            "window_days": cfg.window_days,
            "min_samples": cfg.min_samples,
        },
        series=tuple(series),
        latest=latest,
        suggested_enabled=suggested_enabled,
        walkforward_hit_rate=walkforward_hit_rate,
    )
