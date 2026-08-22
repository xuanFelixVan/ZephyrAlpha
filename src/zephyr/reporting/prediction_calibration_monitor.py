# [BLUEPRINT] MOD-RPT-029 | 待统筹登记（92号清单 §8.7 M4-④ 日志→参数校准反馈闭环骨架）
# [MODULE] zephyr.reporting.prediction_calibration_monitor
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.prediction_log_writer(log_prediction/query_predictions 消费); zephyr.shared.io.paths(MAIN_REPO_ROOT 锚 .runtime 运行时区)
# [CONSUMERS] G04 参数校准流程（评审建议工单消费方——人审）; CAND-SELL-001 同族触发器族（规划）; 55号 周/月复盘编排（规划）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只出"评审建议"——本模块永不自治修改任何参数（调参动作恒人审/G04 流程）; 评估/落盘异常 fail-open（不触发+TriggerVerdict.reason='error'+logging 留痕，绝不阻断调用方）; 输入/config/stats 校验 fail-closed（ValueError）; 不写任何注册表 yaml（experiment_registry 联动=输出工单文本落 .runtime/ 运行时区）; DB 访问仅经 prediction_log_writer 公共 API（append-only，本模块零裸 SQL）; 样本量守卫：样本<30（默认可配）恒不触发
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（module/config/stats/outcome_payload 非法 fail-closed）; compute_hit_rate_stats/record_outcome 的 sqlite3.Error 透传（evaluate_calibration_trigger 内统一收敛 fail-open 不外抛）
# [TESTS] tests/reporting/test_prediction_calibration_monitor.py
# [A_module] module_id=MOD-RPT-029 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

prediction_calibration_monitor — 日志→参数校准反馈闭环骨架（92号清单 §8.7 M4-④）

设计真源：44号备忘 §12.1 M4-④（"AI 通过日志调参"——实验结果→参数调整的
登记与触发；experiment_registry 联动：预测命中率/边界修正胜率→参数校准评审；
G04 校准/CAND-SELL-001 同族触发器）+ 92号清单 §8.7（数据期需命中率积累，
本批=统计器+触发器骨架+样本量守卫 <30 不触发）。
机构对标：MLflow experiment tracking 反馈环 / WFA 滚动校准触发器（52号）。

四项裁定（写清）
----------------
裁定一·真值回写落点：``record_outcome`` 写 **prediction_log 本表**
（prediction_type='outcome' 族），不建姊妹表——单一账本可回查可验证，
复用 92号 §7.13 幂等键/DDL 真源/查询 API，不新建第二真源
（对齐 44号 §12.2 "全部已有主，不新建第二真源"纪律）。

裁定二·命中判定归回写方：本模块只聚合不判定。``record_outcome`` 要求
outcome_payload 含 ``hit: bool``（事后真值评估结果，fail-closed 校验）——
判定口径（如边界修正胜率=修正方向 vs 次日实际走势是否一致）由生产侧
回写管道持有，统计器不内嵌任何业务判定逻辑（骨架期保持口径无关）。

裁定三·experiment_registry 联动形态：**不写注册表 yaml**（human_gated
注册表纪律）——触发时输出"参数校准评审建议工单" markdown 文本落
``.runtime/calibration_review/`` 运行时区（锚 MAIN_REPO_ROOT，governance
观测数据同先例），供 G04 流程人审消费；同模块同日同统计内容重写=覆盖
同日工单（runtime 幂等，非审计载体——审计载体=prediction_log 触发事件行）。

裁定四·失败方向分层：输入/config 校验 fail-closed（ValueError，house 惯例）；
评估与落盘异常 fail-open——``evaluate_calibration_trigger`` 永不外抛运行时
异常，收敛为 TriggerVerdict(triggered=False, reason='error') + logging 留痕；
触发事件落盘失败不翻转判定（verdict 仍 triggered=True，evidence 记
persistence_error）——本模块只出建议，判定与留痕解耦，绝不自动改参。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Final

from zephyr.reporting.prediction_log_writer import log_prediction, query_predictions
from zephyr.shared.io.paths import MAIN_REPO_ROOT

__all__: Final = [
    "CalibrationConfig",
    "CalibrationStats",
    "TriggerVerdict",
    "compute_hit_rate_stats",
    "evaluate_calibration_trigger",
    "record_outcome",
]

logger = logging.getLogger(__name__)

# ── prediction_type 族常量（prediction_log 单一账本内的本模块类型段）──
OUTCOME_PREDICTION_TYPE: Final = "outcome"  # 事后真值回写族（裁定一）
TRIGGER_PREDICTION_TYPE: Final = "calibration_trigger"  # 校准评审触发事件族

# ── 触发判定 reason 词表（TriggerVerdict.reason 取值闭集）──
REASON_INSUFFICIENT_DATA: Final = "insufficient_data"  # 样本量守卫：不足不触发
REASON_BELOW_THRESHOLD: Final = "below_threshold"  # 命中率低于阈值：触发评审
REASON_HOLD: Final = "hold"  # 命中率达标：维持现状
REASON_ERROR: Final = "error"  # fail-open 收敛：评估/落盘异常

# ── 统计口径常量 ──
_STATS_QUERY_LIMIT: Final = 10000  # 窗口内单模块行数上限（骨架期远大于实际量级）
_TREND_EPSILON: Final = 0.05  # 趋势判定容忍带：|近段-前段|≤5pp 记 stable
_WORK_ORDER_SUBDIR: Final = ".runtime/calibration_review"  # 工单落盘运行时区（裁定三）
_MODULE_SAFE_RE: Final = re.compile(r"[^0-9A-Za-z_-]+")


@dataclass(frozen=True)
class CalibrationConfig:
    """触发器配置（config 化；默认值=92号 §8.7 工单口径）。

    Attributes:
        hit_rate_threshold: 命中率阈值——窗口命中率低于此值且样本达标即触发
            "参数校准评审"建议（默认 0.55，对齐 44号 M3 注解栏 55% 口径族）。
        min_samples: 样本量守卫下限——窗口内已评估样本不足此数恒不触发
            （默认 30，92号 §8.7 工单口径）。
        window_days: 统计窗口天数（默认 60，含当日的自然日窗口）。

    Raises:
        ValueError: 任一字段非法（fail-closed：阈值须 0<t<1 实数，
            min_samples/window_days 须正整数）。
    """

    hit_rate_threshold: float = 0.55
    min_samples: int = 30
    window_days: int = 60

    def __post_init__(self) -> None:
        t = self.hit_rate_threshold
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not 0.0 < float(t) < 1.0:
            raise ValueError(f"hit_rate_threshold 非法（须 0<t<1 实数）: {t!r}")
        if isinstance(self.min_samples, bool) or not isinstance(self.min_samples, int) or self.min_samples < 1:
            raise ValueError(f"min_samples 非法（须正整数）: {self.min_samples!r}")
        if isinstance(self.window_days, bool) or not isinstance(self.window_days, int) or self.window_days < 1:
            raise ValueError(f"window_days 非法（须正整数）: {self.window_days!r}")


@dataclass(frozen=True)
class CalibrationStats:
    """某模块窗口期预测命中率统计快照（统计器输出，纯数据不判定）。

    Attributes:
        module: 统计对象模块标识。
        window_days: 窗口天数；window_start/window_end 为闭区间端点（YYYY-MM-DD）。
        prediction_count: 窗口内预测行数（剔除 outcome/calibration_trigger 族）。
        sample_size: 已评估样本量=窗口内且能匹配当日预测行的 outcome 数。
        hit_count: 其中 hit=True 数。
        hit_rate: 命中率（hit_count/sample_size）；sample_size=0 时为 None。
        recent_hit_rate/previous_hit_rate: 样本按 trade_date 升序对半分，
            近段/前段命中率（样本<2 时均为 None）。
        trend: 窗口趋势——improving/stable/worsening/insufficient_data
            （近段-前段 >±_TREND_EPSILON 判定，样本<2 记 insufficient_data）。
        orphan_outcome_count: 无当日预测行匹配的 outcome 数（数据质量观察量，
            不计入样本）。
        invalid_outcome_count: payload 不可解析或缺 hit:bool 的 outcome 数
            （不计入样本；经 record_outcome 写入的行恒不落入此桶）。
    """

    module: str
    window_days: int
    window_start: str
    window_end: str
    prediction_count: int
    sample_size: int
    hit_count: int
    hit_rate: float | None
    recent_hit_rate: float | None
    previous_hit_rate: float | None
    trend: str
    orphan_outcome_count: int = 0
    invalid_outcome_count: int = 0


@dataclass(frozen=True)
class TriggerVerdict:
    """触发器判定结论（本模块唯一输出——只出评审建议，不自治改参）。

    Attributes:
        module: 评估对象模块标识。
        triggered: True=触发"参数校准评审"建议（reason=below_threshold）。
        reason: 判定原因，取 REASON_* 词表闭集。
        suggested_action: 触发时的评审建议文本（供 G04 流程人审消费）；
            未触发/异常时为空串。
        evidence: 证据快照 dict（统计字段+阈值/守卫口径+落盘结果留痕）。
        evaluated_at: 评估时点 UTC ISO8601。
    """

    module: str
    triggered: bool
    reason: str
    suggested_action: str
    evidence: dict = field(default_factory=dict)
    evaluated_at: str = ""


def _validate_non_empty_str(value: object, field_name: str) -> str:
    """非空字符串字段校验（module，fail-closed）。"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 非法（须非空字符串）: {value!r}")
    return value.strip()


def _default_work_order_dir() -> Path:
    """工单默认落盘目录：MAIN_REPO_ROOT/.runtime/calibration_review（运行时区）。"""
    return MAIN_REPO_ROOT / _WORK_ORDER_SUBDIR


def record_outcome(
    trade_date: str,
    module: str,
    outcome_payload: object,
    asof_ts: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    """事后真值回写（裁定一/二）：写 prediction_log 本表 outcome 族。

    Args:
        trade_date: 被评估预测所属交易日 "YYYY-MM-DD"（非法即拒）。
        module: 产出模块标识（非空字符串，须与被评估预测行同 module）。
        outcome_payload: 真值载荷——**必须 dict 且含 ``hit: bool``**
            （命中判定结果，由回写方口径产出；本模块不判定只聚合）。
            其余键自由（如 actual_direction/revision_direction/note），
            须 JSON 可序列化。
        asof_ts: 评估时点 ISO8601；None=落库当前 UTC。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。

    Returns:
        行 id（幂等语义同 log_prediction：同日同模块同内容重复写=跳过保首条）。

    Raises:
        ValueError: outcome_payload 非 dict / 缺 hit 键 / hit 非 bool，
            或 trade_date/module 非法（fail-closed）。
        sqlite3.Error: 库级异常透传（表缺失先调 ensure_prediction_log_table）。
    """
    if not isinstance(outcome_payload, dict):
        raise ValueError(f"outcome_payload 非法（须 dict 且含 hit: bool）: {type(outcome_payload).__name__}")
    hit = outcome_payload.get("hit")
    if not isinstance(hit, bool):
        raise ValueError(f"outcome_payload.hit 非法（须 bool 命中判定）: {hit!r}")
    return log_prediction(
        trade_date=trade_date,
        module=module,
        prediction_type=OUTCOME_PREDICTION_TYPE,
        payload=outcome_payload,
        asof_ts=asof_ts,
        db_path=db_path,
    )


def compute_hit_rate_stats(
    module: str,
    window_days: int = 60,
    db_path: str | Path | None = None,
) -> CalibrationStats:
    """统计器：从 prediction_log 读某模块窗口期预测序列，算命中率/样本量/趋势。

    口径（裁定二）：样本=窗口内 outcome 行且当日存在该模块预测行（剔除
    outcome/calibration_trigger 族自身，防自引用计数）；命中=outcome payload
    的 hit: bool；趋势=样本按 trade_date 升序对半分后近段-前段命中率差
    （±5pp 容忍带记 stable，样本<2 记 insufficient_data）。

    Args:
        module: 统计对象模块标识（非空字符串）。
        window_days: 统计窗口天数（正整数；含当日的自然日闭区间）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。

    Returns:
        CalibrationStats 快照（sample_size=0 时 hit_rate=None）。

    Raises:
        ValueError: module/window_days 非法（fail-closed）。
        sqlite3.Error: 库级异常透传。
    """
    v_module = _validate_non_empty_str(module, "module")
    if isinstance(window_days, bool) or not isinstance(window_days, int) or window_days < 1:
        raise ValueError(f"window_days 非法（须正整数）: {window_days!r}")

    today = date.today()
    window_start = (today - timedelta(days=window_days - 1)).isoformat()
    window_end = today.isoformat()

    rows = query_predictions(module=v_module, limit=_STATS_QUERY_LIMIT, db_path=db_path)
    in_window = [r for r in rows if window_start <= r["trade_date"] <= window_end]
    predictions = [
        r for r in in_window
        if r["prediction_type"] not in (OUTCOME_PREDICTION_TYPE, TRIGGER_PREDICTION_TYPE)
    ]
    outcomes = [r for r in in_window if r["prediction_type"] == OUTCOME_PREDICTION_TYPE]
    prediction_dates = {r["trade_date"] for r in predictions}

    samples: list[tuple[str, bool]] = []
    orphan_count = 0
    invalid_count = 0
    for row in outcomes:
        try:
            payload = json.loads(row["payload_json"])
        except (json.JSONDecodeError, TypeError):
            invalid_count += 1
            continue
        hit = payload.get("hit") if isinstance(payload, dict) else None
        if not isinstance(hit, bool):
            invalid_count += 1
            continue
        if row["trade_date"] not in prediction_dates:
            orphan_count += 1
            continue
        samples.append((row["trade_date"], hit))

    samples.sort(key=lambda s: s[0])
    sample_size = len(samples)
    hit_count = sum(1 for _, hit in samples if hit)
    hit_rate = (hit_count / sample_size) if sample_size > 0 else None

    recent_rate: float | None = None
    previous_rate: float | None = None
    if sample_size < 2:
        trend = "insufficient_data"
    else:
        mid = sample_size // 2
        previous_rate = sum(1 for _, h in samples[:mid] if h) / mid
        recent_rate = sum(1 for _, h in samples[mid:] if h) / (sample_size - mid)
        diff = recent_rate - previous_rate
        if diff > _TREND_EPSILON:
            trend = "improving"
        elif diff < -_TREND_EPSILON:
            trend = "worsening"
        else:
            trend = "stable"

    return CalibrationStats(
        module=v_module,
        window_days=window_days,
        window_start=window_start,
        window_end=window_end,
        prediction_count=len(predictions),
        sample_size=sample_size,
        hit_count=hit_count,
        hit_rate=hit_rate,
        recent_hit_rate=recent_rate,
        previous_hit_rate=previous_rate,
        trend=trend,
        orphan_outcome_count=orphan_count,
        invalid_outcome_count=invalid_count,
    )


def _stats_evidence(stats: CalibrationStats, config: CalibrationConfig) -> dict:
    """统计快照 → verdict evidence dict（含阈值/守卫口径留痕）。"""
    return {
        "module": stats.module,
        "window_start": stats.window_start,
        "window_end": stats.window_end,
        "window_days": stats.window_days,
        "prediction_count": stats.prediction_count,
        "sample_size": stats.sample_size,
        "hit_count": stats.hit_count,
        "hit_rate": stats.hit_rate,
        "recent_hit_rate": stats.recent_hit_rate,
        "previous_hit_rate": stats.previous_hit_rate,
        "trend": stats.trend,
        "orphan_outcome_count": stats.orphan_outcome_count,
        "invalid_outcome_count": stats.invalid_outcome_count,
        "hit_rate_threshold": config.hit_rate_threshold,
        "min_samples": config.min_samples,
    }


def _build_suggested_action(stats: CalibrationStats, config: CalibrationConfig) -> str:
    """评审建议文本（只出建议——调参动作恒人审/G04 流程，本模块不改参）。"""
    assert stats.hit_rate is not None  # 调用方保证 sample_size>=min_samples>=1
    return (
        f"提请 G04 参数校准评审（人审）：模块 {stats.module} 近 {stats.window_days} 日窗口 "
        f"（{stats.window_start}~{stats.window_end}）预测命中率 {stats.hit_rate:.2%} "
        f"低于阈值 {float(config.hit_rate_threshold):.2%}（样本 {stats.sample_size}，"
        f"趋势 {stats.trend}）——建议按 G04 校准流程评审该模块参数"
        f"（CAND-SELL-001 同族触发器形态）；本模块只出评审建议，不自治改参。"
    )


def _write_review_work_order(
    stats: CalibrationStats,
    config: CalibrationConfig,
    evaluated_at: str,
    runtime_dir: str | Path | None,
) -> Path:
    """评审建议工单落盘（裁定三）：.runtime/calibration_review/ 运行时区 markdown。

    同模块同日重写=覆盖（runtime 幂等，非审计载体）；目录不存在自动建。
    """
    out_dir = Path(runtime_dir) if runtime_dir is not None else _default_work_order_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    module_safe = _MODULE_SAFE_RE.sub("_", stats.module)
    out_path = out_dir / f"{evaluated_at[:10]}_{module_safe}_calibration_review.md"
    assert stats.hit_rate is not None
    recent = f"{stats.recent_hit_rate:.2%}" if stats.recent_hit_rate is not None else "N/A"
    previous = f"{stats.previous_hit_rate:.2%}" if stats.previous_hit_rate is not None else "N/A"
    text = (
        f"# 参数校准评审建议工单（G04 流程人审消费）\n\n"
        f"- 生成时点（UTC）：{evaluated_at}\n"
        f"- 模块：{stats.module}\n"
        f"- 统计窗口：{stats.window_start} ~ {stats.window_end}（{stats.window_days} 日）\n"
        f"- 样本量：{stats.sample_size}（守卫下限 {config.min_samples}）\n"
        f"- 命中率：{stats.hit_rate:.2%}（阈值 {float(config.hit_rate_threshold):.2%}）\n"
        f"- 窗口趋势：{stats.trend}（近段 {recent} vs 前段 {previous}）\n"
        f"- 触发原因：{REASON_BELOW_THRESHOLD}（命中率低于阈值）\n\n"
        f"## 建议动作\n\n"
        f"{_build_suggested_action(stats, config)}\n\n"
        f"## 纪律声明\n\n"
        f"本工单仅为评审建议——参数调整动作永远走人审/G04 流程，"
        f"产出模块（prediction_calibration_monitor）永不自治修改任何参数。\n"
        f"真源：92号清单 §8.7 M4-④（44号备忘 §12.1）。\n"
    )
    out_path.write_text(text, encoding="utf-8")
    return out_path


def evaluate_calibration_trigger(
    module: str,
    stats: CalibrationStats | None = None,
    config: CalibrationConfig | None = None,
    db_path: str | Path | None = None,
    runtime_dir: str | Path | None = None,
) -> TriggerVerdict:
    """触发器：样本量守卫+阈值规则 → 参数校准评审建议（fail-open，不改参）。

    规则（92号 §8.7）：样本量 < min_samples（默认 30）→ 不触发
    （insufficient_data）；样本达标且命中率 < hit_rate_threshold（默认 0.55）
    → 触发"参数校准评审"事件（below_threshold）；命中率 ≥ 阈值 → hold。
    触发时事件经 log_prediction 写 prediction_log（calibration_trigger 族）
    + 评审建议工单落 .runtime/calibration_review/（裁定三，不写注册表 yaml）。

    失败方向（裁定四）：评估/落盘异常一律 fail-open——本函数永不外抛运行时
    异常；评估异常收敛为 triggered=False/reason='error'，落盘异常不翻转判定
    （evidence 记 persistence_error/work_order_error）+ logging 留痕。

    Args:
        module: 评估对象模块标识（非空字符串，fail-closed）。
        stats: 预计算统计快照（None=现算，走 compute_hit_rate_stats）；
            给定则须 CalibrationStats（fail-closed）。
        config: 触发器配置（None=默认 CalibrationConfig()）；给定则须
            CalibrationConfig（fail-closed）。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        runtime_dir: 工单落盘目录；None=MAIN_REPO_ROOT/.runtime/calibration_review。

    Returns:
        TriggerVerdict（triggered/reason/suggested_action/evidence/evaluated_at）。

    Raises:
        ValueError: module/config/stats 类型非法（fail-closed，仅此一类外抛）。
    """
    v_module = _validate_non_empty_str(module, "module")
    cfg = config if config is not None else CalibrationConfig()
    if not isinstance(cfg, CalibrationConfig):
        raise ValueError(f"config 非法（须 CalibrationConfig 或 None）: {type(cfg).__name__}")
    if stats is not None and not isinstance(stats, CalibrationStats):
        raise ValueError(f"stats 非法（须 CalibrationStats 或 None）: {type(stats).__name__}")
    evaluated_at = datetime.now(UTC).isoformat()

    try:
        st = stats if stats is not None else compute_hit_rate_stats(
            v_module, window_days=cfg.window_days, db_path=db_path,
        )
    except Exception as exc:  # noqa: BLE001 — fail-open：统计异常=不触发+留痕，绝不阻断调用方
        logger.warning("calibration 统计异常 fail-open（module=%s）: %s: %s", v_module, type(exc).__name__, exc)
        return TriggerVerdict(
            module=v_module,
            triggered=False,
            reason=REASON_ERROR,
            suggested_action="",
            evidence={"error": f"{type(exc).__name__}: {exc}"},
            evaluated_at=evaluated_at,
        )

    evidence = _stats_evidence(st, cfg)
    if st.sample_size < cfg.min_samples or st.hit_rate is None:
        return TriggerVerdict(
            module=v_module,
            triggered=False,
            reason=REASON_INSUFFICIENT_DATA,
            suggested_action="",
            evidence=evidence,
            evaluated_at=evaluated_at,
        )
    if st.hit_rate >= float(cfg.hit_rate_threshold):
        return TriggerVerdict(
            module=v_module,
            triggered=False,
            reason=REASON_HOLD,
            suggested_action="",
            evidence=evidence,
            evaluated_at=evaluated_at,
        )

    # 触发：命中率低于阈值且样本达标——出评审建议（只建议不改参）
    suggested = _build_suggested_action(st, cfg)
    try:
        evidence["persisted_row_id"] = log_prediction(
            trade_date=evaluated_at[:10],
            module=v_module,
            prediction_type=TRIGGER_PREDICTION_TYPE,
            payload={
                "reason": REASON_BELOW_THRESHOLD,
                "hit_rate": st.hit_rate,
                "sample_size": st.sample_size,
                "window_start": st.window_start,
                "window_end": st.window_end,
                "threshold": float(cfg.hit_rate_threshold),
                "trend": st.trend,
                "suggested_action": suggested,
            },
            db_path=db_path,
        )
    except Exception as exc:  # noqa: BLE001 — fail-open：落盘失败不翻转判定，留痕证据
        logger.warning("calibration 触发事件落盘失败 fail-open（module=%s）: %s: %s", v_module, type(exc).__name__, exc)
        evidence["persistence_error"] = f"{type(exc).__name__}: {exc}"
    try:
        evidence["work_order_path"] = str(_write_review_work_order(st, cfg, evaluated_at, runtime_dir))
    except Exception as exc:  # noqa: BLE001 — fail-open：工单落盘失败不翻转判定，留痕证据
        logger.warning("calibration 评审工单落盘失败 fail-open（module=%s）: %s: %s", v_module, type(exc).__name__, exc)
        evidence["work_order_error"] = f"{type(exc).__name__}: {exc}"

    return TriggerVerdict(
        module=v_module,
        triggered=True,
        reason=REASON_BELOW_THRESHOLD,
        suggested_action=suggested,
        evidence=evidence,
        evaluated_at=evaluated_at,
    )
