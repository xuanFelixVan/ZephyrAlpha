# [BLUEPRINT] MOD-PLAN-008 | 待统筹登记（45号 §4 W0/W6 + 缺口总账 GAP-F-07①）
# [MODULE] zephyr.plan_engine.scenario_plan_recorder
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.scenario_planner(ScenarioPlan/compute_scenario_plan/SHIFT_STANCE); zephyr.reporting.prediction_log_writer(log_prediction/query_predictions/ensure_prediction_log_table); zephyr.reporting.prediction_calibration_monitor(record_outcome); zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（表名解析）
# [CONSUMERS] 盘前管线（预案落库 compute_and_record_scenario_plan）; W0/W6 复盘（writeback_scenario_outcome 回写）; MOD-PLAN-009 三维归因统计（outcome payload 契约消费）; MOD-PLAN-010 Brier 校准（predicted_confidence×hit 消费）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] append-only 仅 INSERT（经 prediction_log_writer 公共 API，零裸 SQL 写库）; 命中判定口径归本模块（44号 §12.1 M4-④ 裁定二：回写方持有判定口径）; actual 情景恒∈SCENARIO_LIST（与 MOD-PLAN-002 语义对齐）; 落库/回写失败 fail-open 不阻塞主流程; 输入校验 fail-closed; 错误消息不含 session_id
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（输入非法 fail-closed）; 落库/查询/CH 异常 fail-open（record 返回 -1 / writeback 返回 verdict.status=error:* 留痕，不外抛）
# [TESTS] tests/plan_engine/test_scenario_plan_recorder.py
# [A_module] module_id=MOD-PLAN-008 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

ScenarioPlanRecorder — 预案 prediction_log 落库与实际 outcome 回写 (MOD-PLAN-008)

45号作战手册 §4 W0/W6 + 缺口总账 GAP-F-07① 落码：接通 MOD-PLAN-005 ScenarioPlan
"预测 → 实际 outcome" 闭环链路（scenario_planner 头部 CONSUMERS 标注"后续波次接"
的落库通道，本模块=该通道载体；scenario_planner 计算核保持纯计算零改动）。

两段链路：
    - 预测落库：ScenarioPlan.to_dict() → prediction_log（module=
      "plan_engine.scenario_planner"，prediction_type="scenario_plan"）——幂等
      （UNIQUE(trade_date, module, prediction_type, input_hash)，同计划重跑保首条）。
    - 实际回写：次日盘后取实际行情判定"实际命中哪格"→ record_outcome 写
      outcome 族（prediction_type="outcome"），payload 携 W0 三维归因/Brier
      校准消费契约字段（hit/dimension/scenario/actual_scenario/signal_source/
      predicted_confidence/trend_source/...）。

命中判定口径（裁定二·回写方持有，写清）：
    - 开盘桶：上证指数（kline_index，默认 000001.SH 可配）今日开盘价 vs 昨日收盘
      → open_pct ≥+2% HIGH / ≤-2% LOW / 其余 FLAT（与 MOD-PLAN-002 ±2% 对齐）。
    - 走势桶：开盘后 30 分钟（9:30-10:00）——首选 300ETF（kline_etf_1min，默认
      510300.SH 可配，ETF 替代真实指数与 MOD-PLAN-004/007 同口径）分钟线
      VWAP 判定：末根收盘价 vs 窗口 VWAP 偏离超 ±trend_tolerance（默认 0.1%）
      → 高走/低走，否则平走；分钟数据缺失且 allow_daily_proxy → 日线代理
      (close-open)/open，trend_source="daily_proxy" 留痕（校准统计可按此过滤）；
      代理禁用 → 跳过回写（skipped:no_trend_data，不污染校准样本）。
    - 9 格映射：HIGH×高走=HIGH_OPEN_REAL_UP / HIGH×低走=HIGH_OPEN_FAKE_UP /
      HIGH×平走=HIGH_OPEN_WASH（LOW/FLAT 同理，恒∈SCENARIO_LIST）。
    - hit = (actual_scenario == 预测 final_scenario)。

不做什么：不改 scenario_planner 计算核（稳定节点零破坏）/不做方向点预测/
         不判定执行与盈亏维度（execution/pnl 维度由执行链模块回写，本模块只写
         dimension="prediction"）。

依据: 45_warroom_playbook §4 W0/W6 + §5；44号 §12.1 M4-②/M4-④；92号 §7.13/§8.7
SSoT: depgraph MOD-PLAN-008（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: ScenarioPlan（预测落库）/ trade_date + kline_index + kline_etf_1min（回写）
# 特征: open_pct（指数开盘偏离）/ trend_pct（30 分钟 VWAP 偏离或日线代理）
# 算法: 开盘桶×走势桶 → 9 格实际情景 → hit 判定 → outcome 族回写
# 输出: prediction_log scenario_plan/outcome 两族行 + ScenarioOutcomeVerdict

"""

from __future__ import annotations

import datetime
import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.plan_engine.scenario_planner import ScenarioPlan, compute_scenario_plan
from zephyr.reporting.prediction_calibration_monitor import record_outcome
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
    query_predictions,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "DIMENSION_PREDICTION",
    "MODULE_LOG_NAME",
    "PREDICTION_TYPE_SCENARIO_PLAN",
    "SIGNAL_SOURCE",
    "ScenarioOutcomeVerdict",
    "ScenarioPlanRecorder",
    "ScenarioRecorderConfig",
    "compute_and_record_scenario_plan",
    "determine_actual_scenario",
    "record_scenario_plan",
    "writeback_scenario_outcome",
]

# ── prediction_log 落库口径常量 ──

MODULE_LOG_NAME: Final = "plan_engine.scenario_planner"  # prediction_log.module（=产出模块口径，供 W0 回查）
PREDICTION_TYPE_SCENARIO_PLAN: Final = "scenario_plan"  # 预测族（44号 §12.1 M4-② 四族之一）
SIGNAL_SOURCE: Final = "MOD-PLAN-005.scenario_planner"  # 信号源标识（三维归因"信号源"维取值）

# ── outcome payload 契约字段（MOD-PLAN-009/010 消费真源）──

DIMENSION_PREDICTION: Final = "prediction"  # 三维归因"维度"取值：预测命中（execution/pnl 由执行链回写）

# ── 判定口径默认值（45号 §4 W2/W0 口径）──

OPEN_THRESHOLD: Final = 0.02  # 高/低开判定 ±2%（与 MOD-PLAN-002 对齐）
TREND_TOLERANCE: Final = 0.001  # 平走容忍带 ±0.1%（末收 vs 窗口 VWAP）
INDEX_SYMBOL: Final = "000001.SH"  # 开盘桶判定指数（上证指数）
TREND_PROXY_SYMBOL: Final = "510300.SH"  # 30 分钟走势判定代理（300ETF，分钟线）
TREND_WINDOW_START: Final = "09:30"  # 走势判定窗口开始
TREND_WINDOW_END: Final = "10:00"  # 走势判定窗口结束（开盘后 30 分钟）

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 scenario_planner 同约定）
# 指数日线近两日（open_pct=今日 open vs 昨日 close）
_SQL_INDEX_TWO_DAY: Final = (
    "SELECT trade_date, toFloat64(open) AS o, toFloat64(close) AS c "
    "FROM {table} FINAL WHERE symbol_canonical = '{symbol}' "
    "AND trade_date <= toDate('{trade_date}') ORDER BY trade_date DESC LIMIT 2"
)
# ETF 分钟窗口聚合（30 分钟 VWAP + 末根收盘；VWAP=sum(amount)/sum(volume)）
_SQL_ETF_MINUTE_AGG: Final = (
    "SELECT sum(toFloat64(amount)) AS amt_sum, sum(toFloat64(volume)) AS vol_sum, "
    "argMax(toFloat64(close), trade_time) AS last_close, count() AS n "
    "FROM {table} FINAL WHERE trade_date = toDate('{trade_date}') "
    "AND symbol_canonical = '{symbol}' "
    "AND trade_time >= toDateTime64('{trade_date} {win_start}:00', 3, 'Asia/Shanghai') "
    "AND trade_time < toDateTime64('{trade_date} {win_end}:00', 3, 'Asia/Shanghai')"
)


def _parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """把 ch_reader.query 返回的 TSV 字符串解析成行列表（ncols 不足跳过该行）。"""
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        vals = line.rstrip("\r").split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def _safe_float(v: Any) -> float | None:
    """安全转 float；失败/NaN/Inf 返回 None（区别于 0.0，供降级判定）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _validate_trade_date(trade_date: object) -> str:
    """交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    if not isinstance(trade_date, str):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
    try:
        datetime.date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    return trade_date


def determine_actual_scenario(
    open_pct: float,
    trend_pct: float,
    *,
    open_threshold: float = OPEN_THRESHOLD,
    trend_tolerance: float = TREND_TOLERANCE,
) -> str:
    """实际命中情景判定（纯函数）：开盘桶 × 走势桶 → 9 情景之一。

    开盘桶：open_pct ≥ +open_threshold → HIGH；≤ -open_threshold → LOW；其余 FLAT。
    走势桶：|trend_pct| ≤ trend_tolerance → 平走（WASH）；>0 → 高走；<0 → 低走。
    映射：HIGH×高走=HIGH_OPEN_REAL_UP / HIGH×低走=HIGH_OPEN_FAKE_UP /
    HIGH×平走=HIGH_OPEN_WASH（LOW/FLAT 同理），返回值恒∈SCENARIO_LIST。

    Args:
        open_pct: 实际开盘涨幅（(今开-昨收)/昨收，指数口径）。
        trend_pct: 开盘后 30 分钟走势偏离（末收 vs 窗口 VWAP，或日线代理）。
        open_threshold: 高/低开阈值（默认 +2%，与 MOD-PLAN-002 对齐）。
        trend_tolerance: 平走容忍带（默认 ±0.1%）。

    Returns:
        实际命中情景（SCENARIO_LIST 成员）。

    Raises:
        ValueError: open_pct/trend_pct 非有限实数，或阈值配置非法（fail-closed）。
    """
    open_f = _safe_float(open_pct)
    trend_f = _safe_float(trend_pct)
    if open_f is None:
        raise ValueError(f"open_pct 非法（须有限实数）: {open_pct!r}")
    if trend_f is None:
        raise ValueError(f"trend_pct 非法（须有限实数）: {trend_pct!r}")
    th = _safe_float(open_threshold)
    tol = _safe_float(trend_tolerance)
    if th is None or th <= 0:
        raise ValueError(f"open_threshold 非法（须正实数）: {open_threshold!r}")
    if tol is None or tol < 0:
        raise ValueError(f"trend_tolerance 非法（须非负实数）: {trend_tolerance!r}")

    if open_f >= th:
        open_bucket = "HIGH"
    elif open_f <= -th:
        open_bucket = "LOW"
    else:
        open_bucket = "FLAT"

    if trend_f > tol:
        trend_bucket = "UP"
    elif trend_f < -tol:
        trend_bucket = "DOWN"
    else:
        trend_bucket = "WASH"

    scenario = {
        ("HIGH", "UP"): "HIGH_OPEN_REAL_UP",
        ("HIGH", "DOWN"): "HIGH_OPEN_FAKE_UP",
        ("HIGH", "WASH"): "HIGH_OPEN_WASH",
        ("LOW", "UP"): "LOW_OPEN_FAKE_DOWN",
        ("LOW", "DOWN"): "LOW_OPEN_REAL_DOWN",
        ("LOW", "WASH"): "LOW_OPEN_WASH",
        ("FLAT", "UP"): "FLAT_OPEN_REAL_UP",
        ("FLAT", "DOWN"): "FLAT_OPEN_REAL_DOWN",
        ("FLAT", "WASH"): "FLAT_OPEN_WASH",
    }[(open_bucket, trend_bucket)]
    if scenario not in SCENARIO_LIST:  # 防御性兜底（映射表已穷举 9 格）
        raise ValueError(f"实际情景映射越界（不在 SCENARIO_LIST）: {scenario!r}")
    return scenario


# ── 配置契约 ──


@dataclass(frozen=True)
class ScenarioRecorderConfig:
    """落库/回写配置（默认值=45号 §4 W2/W0 设计口径）。"""

    open_threshold: float = OPEN_THRESHOLD  # 高/低开判定阈值
    trend_tolerance: float = TREND_TOLERANCE  # 平走容忍带
    index_symbol: str = INDEX_SYMBOL  # 开盘桶判定指数
    trend_proxy_symbol: str = TREND_PROXY_SYMBOL  # 30 分钟走势判定代理标的
    trend_window_start: str = TREND_WINDOW_START  # 走势窗口开始
    trend_window_end: str = TREND_WINDOW_END  # 走势窗口结束
    allow_daily_proxy: bool = True  # 分钟数据缺失时允许日线代理（trend_source 留痕）

    def __post_init__(self) -> None:
        if _safe_float(self.open_threshold) is None or self.open_threshold <= 0:
            raise ValueError(f"open_threshold 非法（须正实数）: {self.open_threshold!r}")
        if _safe_float(self.trend_tolerance) is None or self.trend_tolerance < 0:
            raise ValueError(f"trend_tolerance 非法（须非负实数）: {self.trend_tolerance!r}")
        for name in ("index_symbol", "trend_proxy_symbol", "trend_window_start", "trend_window_end"):
            v = getattr(self, name)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f"{name} 非法（须非空字符串）: {v!r}")


DEFAULT_CONFIG: Final = ScenarioRecorderConfig()


# ── 输出契约 ──


@dataclass(frozen=True)
class ScenarioOutcomeVerdict:
    """实际 outcome 回写结论（writeback_scenario_outcome 返回，JSON 可序列化）。"""

    trade_date: str
    status: str  # ok / skipped:no_prediction / skipped:no_open_data / skipped:no_trend_data / error:*
    hit: bool | None  # 命中判定（None=未判定）
    predicted_scenario: str | None  # 预测 final_scenario
    actual_scenario: str | None  # 实际命中情景（SCENARIO_LIST 成员）
    open_pct: float | None  # 实际开盘涨幅
    trend_pct: float | None  # 30 分钟走势偏离（或日线代理）
    trend_source: str | None  # kline_etf_1min / daily_proxy / None
    outcome_row_id: int | None  # outcome 落库行 id（None=未落库）
    detail: dict[str, Any] = field(default_factory=dict)  # 留痕（指数/代理标的/样本数等）

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        return {
            "trade_date": self.trade_date,
            "status": self.status,
            "hit": self.hit,
            "predicted_scenario": self.predicted_scenario,
            "actual_scenario": self.actual_scenario,
            "open_pct": self.open_pct,
            "trend_pct": self.trend_pct,
            "trend_source": self.trend_source,
            "outcome_row_id": self.outcome_row_id,
            "detail": dict(self.detail),
        }


# ── 落库与回写器 ──


class ScenarioPlanRecorder:
    """预案落库+实际 outcome 回写器（MOD-PLAN-008）。

    CH 数据经 ch_client 注入（测试 mock/离线）；未注入走项目默认 CH 通道
    （zephyr.data.ch_reader.query）。库路径经 db_path 注入（None=DB_PATH SSoT，
    测试注入临时库，与 prediction_log_writer 同款隔离先例）。
    """

    def __init__(
        self,
        ch_client: Callable[[str], str] | None = None,
        db_path: str | Path | None = None,
        config: ScenarioRecorderConfig | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._ch = ch_client
        self._db_path = db_path

    # ── 基础设施 ──────────────────────────────────────────────────────────

    @staticmethod
    def _table(category_id: str, fallback: str) -> str:
        """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
        try:
            from zephyr.data.table_registry import get_registry

            return get_registry().table(category_id)
        except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
            log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
            return fallback

    def _query(self, sql: str, channel: str) -> str:
        """执行 CH 查询；异常→返回空串+warning 留痕（fail-open，由调用方判降级）。"""
        try:
            if self._ch is not None:
                return self._ch(sql)
            from zephyr.data import ch_reader

            return ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open：单通道异常不炸整体
            log.warning("通道 %s 查询异常，降级跳过: %s", channel, exc)
            return ""

    # ── 预测落库 ──────────────────────────────────────────────────────────

    def record_plan(self, plan: ScenarioPlan, asof_ts: str | None = None) -> int:
        """ScenarioPlan → prediction_log（scenario_plan 族，幂等保首条）。

        Args:
            plan: MOD-PLAN-005 产出（须 ScenarioPlan 实例，fail-closed）。
            asof_ts: 预测生效时点 ISO8601；None=落库当前 UTC。

        Returns:
            行 id（同计划重复写=已存在行 id）；落库异常 fail-open 返回 -1。

        Raises:
            ValueError: plan 非 ScenarioPlan（fail-closed）。
        """
        if not isinstance(plan, ScenarioPlan):
            raise ValueError(f"plan 非法（须 ScenarioPlan）: {type(plan).__name__}")
        try:
            return log_prediction(
                trade_date=plan.date,
                module=MODULE_LOG_NAME,
                prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
                payload=plan.to_dict(),
                asof_ts=asof_ts,
                db_path=self._db_path,
            )
        except Exception as exc:  # noqa: BLE001 — fail-open：落库失败不阻塞预案主流程
            log.warning("scenario_plan 落库失败 fail-open（date=%s）: %s: %s", plan.date, type(exc).__name__, exc)
            return -1

    # ── 实际 outcome 回写 ─────────────────────────────────────────────────

    def _load_open_pct(self, trade_date: str) -> tuple[float | None, dict[str, Any]]:
        """实际开盘涨幅：指数今日 open vs 昨日 close（kline_index 近两日）。"""
        table = self._table("market_kline_index", "c1_market.kline_index")
        tsv = self._query(
            _SQL_INDEX_TWO_DAY.format(
                table=table, symbol=self._config.index_symbol, trade_date=trade_date,
            ),
            "kline_index",
        )
        rows = _parse_tsv(tsv, 3)
        detail: dict[str, Any] = {"index_symbol": self._config.index_symbol, "rows": len(rows)}
        if len(rows) < 2:
            return None, detail
        today_open = _safe_float(rows[0][1])
        prev_close = _safe_float(rows[1][2])
        if today_open is None or prev_close is None or prev_close <= 0 or today_open <= 0:
            return None, detail
        return (today_open - prev_close) / prev_close, detail

    def _load_trend_pct(self, trade_date: str) -> tuple[float | None, str | None, dict[str, Any]]:
        """30 分钟走势偏离：ETF 分钟窗口末收 vs VWAP；缺数据按配置走日线代理。

        返回 (trend_pct, trend_source, detail)；trend_source ∈
        kline_etf_1min / daily_proxy / None（None=双路皆缺，调用方跳过回写）。
        """
        cfg = self._config
        table = self._table("market_kline_etf_1min", "c1_market.kline_etf_1min")
        tsv = self._query(
            _SQL_ETF_MINUTE_AGG.format(
                table=table,
                symbol=cfg.trend_proxy_symbol,
                trade_date=trade_date,
                win_start=cfg.trend_window_start,
                win_end=cfg.trend_window_end,
            ),
            "kline_etf_1min",
        )
        rows = _parse_tsv(tsv, 4)
        detail: dict[str, Any] = {"trend_proxy_symbol": cfg.trend_proxy_symbol}
        if rows:
            amt_sum = _safe_float(rows[0][0])
            vol_sum = _safe_float(rows[0][1])
            last_close = _safe_float(rows[0][2])
            n = _safe_float(rows[0][3])
            detail["minute_bars"] = n
            if amt_sum and vol_sum and vol_sum > 0 and last_close and last_close > 0:
                vwap = amt_sum / vol_sum
                detail["vwap"] = round(vwap, 6)
                return (last_close - vwap) / vwap, "kline_etf_1min", detail
        if not cfg.allow_daily_proxy:
            return None, None, detail
        # 日线代理：(close-open)/open 全日走势代理 30 分钟走势（留痕可过滤）
        table_idx = self._table("market_kline_index", "c1_market.kline_index")
        tsv_idx = self._query(
            _SQL_INDEX_TWO_DAY.format(
                table=table_idx, symbol=cfg.index_symbol, trade_date=trade_date,
            ),
            "kline_index_proxy",
        )
        rows_idx = _parse_tsv(tsv_idx, 3)
        if not rows_idx:
            return None, None, detail
        today_open = _safe_float(rows_idx[0][1])
        today_close = _safe_float(rows_idx[0][2])
        if today_open is None or today_close is None or today_open <= 0 or today_close <= 0:
            return None, None, detail
        detail["proxy_note"] = "分钟数据缺失，(close-open)/open 日线代理"
        return (today_close - today_open) / today_open, "daily_proxy", detail

    def writeback_outcome(self, trade_date: str, asof_ts: str | None = None) -> ScenarioOutcomeVerdict:
        """实际 outcome 回写：判定实际命中格 → outcome 族落库（fail-open）。

        链路：读当日 scenario_plan 预测行（最新一条）→ 实际开盘/走势判定 →
        hit=(actual==predicted) → record_outcome（payload 携三维归因/Brier
        消费契约字段）。任一数据缺失→对应 skipped:* 状态，不写库不抛异常。

        Args:
            trade_date: 被回写预测所属交易日（非法即拒，fail-closed）。
            asof_ts: 评估时点 ISO8601；None=落库当前 UTC。

        Returns:
            ScenarioOutcomeVerdict（status/hit/actual_scenario/落库行 id 留痕）。

        Raises:
            ValueError: trade_date 非法（fail-closed，仅此一类外抛）。
        """
        v_date = _validate_trade_date(trade_date)
        cfg = self._config

        try:
            rows = query_predictions(
                trade_date=v_date,
                module=MODULE_LOG_NAME,
                prediction_type=PREDICTION_TYPE_SCENARIO_PLAN,
                limit=1,
                db_path=self._db_path,
            )
        except Exception as exc:  # noqa: BLE001 — fail-open：查询异常（如表缺失）不炸主流程
            log.warning("预测行查询异常 fail-open（date=%s）: %s: %s", v_date, type(exc).__name__, exc)
            return ScenarioOutcomeVerdict(
                trade_date=v_date,
                status=f"error:query:{type(exc).__name__}",
                hit=None,
                predicted_scenario=None,
                actual_scenario=None,
                open_pct=None,
                trend_pct=None,
                trend_source=None,
                outcome_row_id=None,
            )
        if not rows:
            return ScenarioOutcomeVerdict(
                trade_date=v_date,
                status="skipped:no_prediction",
                hit=None,
                predicted_scenario=None,
                actual_scenario=None,
                open_pct=None,
                trend_pct=None,
                trend_source=None,
                outcome_row_id=None,
            )

        try:
            payload = json.loads(rows[0]["payload_json"])
        except Exception as exc:  # noqa: BLE001 — fail-open：预测行不可解析=数据质量留痕
            log.warning("预测行 payload 解析失败 fail-open（date=%s）: %s", v_date, exc)
            return ScenarioOutcomeVerdict(
                trade_date=v_date,
                status=f"error:payload_parse:{type(exc).__name__}",
                hit=None,
                predicted_scenario=None,
                actual_scenario=None,
                open_pct=None,
                trend_pct=None,
                trend_source=None,
                outcome_row_id=None,
            )
        predicted = payload.get("final_scenario") if isinstance(payload, dict) else None
        predicted = predicted if isinstance(predicted, str) and predicted in SCENARIO_LIST else None
        confidence = payload.get("confidence_scale") if isinstance(payload, dict) else None
        confidence_f = _safe_float(confidence)

        open_pct, open_detail = self._load_open_pct(v_date)
        if open_pct is None:
            return ScenarioOutcomeVerdict(
                trade_date=v_date,
                status="skipped:no_open_data",
                hit=None,
                predicted_scenario=predicted,
                actual_scenario=None,
                open_pct=None,
                trend_pct=None,
                trend_source=None,
                outcome_row_id=None,
                detail=open_detail,
            )

        trend_pct, trend_source, trend_detail = self._load_trend_pct(v_date)
        if trend_pct is None or trend_source is None:
            return ScenarioOutcomeVerdict(
                trade_date=v_date,
                status="skipped:no_trend_data",
                hit=None,
                predicted_scenario=predicted,
                actual_scenario=None,
                open_pct=open_pct,
                trend_pct=None,
                trend_source=None,
                outcome_row_id=None,
                detail={**open_detail, **trend_detail},
            )

        actual = determine_actual_scenario(
            open_pct,
            trend_pct,
            open_threshold=cfg.open_threshold,
            trend_tolerance=cfg.trend_tolerance,
        )
        hit = predicted is not None and actual == predicted

        try:
            row_id: int | None = record_outcome(
                trade_date=v_date,
                module=MODULE_LOG_NAME,
                outcome_payload={
                    "hit": hit,
                    "dimension": DIMENSION_PREDICTION,
                    "scenario": predicted,
                    "actual_scenario": actual,
                    "open_pct": round(open_pct, 6),
                    "trend_pct": round(trend_pct, 6),
                    "trend_source": trend_source,
                    "predicted_confidence": confidence_f,
                    "signal_source": SIGNAL_SOURCE,
                },
                asof_ts=asof_ts,
                db_path=self._db_path,
            )
        except Exception as exc:  # noqa: BLE001 — fail-open：回写落库失败不炸主流程
            log.warning("outcome 回写落库失败 fail-open（date=%s）: %s: %s", v_date, type(exc).__name__, exc)
            return ScenarioOutcomeVerdict(
                trade_date=v_date,
                status=f"error:outcome_write:{type(exc).__name__}",
                hit=hit,
                predicted_scenario=predicted,
                actual_scenario=actual,
                open_pct=open_pct,
                trend_pct=trend_pct,
                trend_source=trend_source,
                outcome_row_id=None,
                detail={**open_detail, **trend_detail},
            )

        return ScenarioOutcomeVerdict(
            trade_date=v_date,
            status="ok",
            hit=hit,
            predicted_scenario=predicted,
            actual_scenario=actual,
            open_pct=open_pct,
            trend_pct=trend_pct,
            trend_source=trend_source,
            outcome_row_id=row_id,
            detail={**open_detail, **trend_detail},
        )


# ── 主入口 ──


def record_scenario_plan(
    plan: ScenarioPlan,
    asof_ts: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    """预案落库主入口（MOD-PLAN-008）：ScenarioPlan → prediction_log。

    Returns:
        行 id（幂等保首条）；落库异常 fail-open 返回 -1。

    Raises:
        ValueError: plan 非 ScenarioPlan（fail-closed）。
    """
    return ScenarioPlanRecorder(db_path=db_path).record_plan(plan, asof_ts=asof_ts)


def writeback_scenario_outcome(
    trade_date: str,
    ch_client: Callable[[str], str] | None = None,
    db_path: str | Path | None = None,
    config: ScenarioRecorderConfig | None = None,
    asof_ts: str | None = None,
) -> ScenarioOutcomeVerdict:
    """实际 outcome 回写主入口（MOD-PLAN-008）。

    Args:
        trade_date: 被回写预测所属交易日（非法即拒，fail-closed）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        config: 判定口径配置（None=45号设计默认值）。
        asof_ts: 评估时点 ISO8601；None=落库当前 UTC。

    Returns:
        ScenarioOutcomeVerdict（任何数据/通道异常降级为对应 status，不外抛）。
    """
    return ScenarioPlanRecorder(ch_client=ch_client, db_path=db_path, config=config).writeback_outcome(
        trade_date, asof_ts=asof_ts,
    )


def compute_and_record_scenario_plan(
    trade_date: str | datetime.date,
    ch_client: Callable[[str], str] | None = None,
    db_path: str | Path | None = None,
    asof_ts: str | None = None,
    **compute_kwargs: Any,
) -> tuple[ScenarioPlan, int]:
    """组合主入口：MOD-PLAN-005 计算 + 本模块落库（scenario_planner 零改动接通）。

    Args:
        trade_date: 交易日（ISO 字符串或 date）。
        ch_client: CH 查询客户端（compute 与本模块共用注入，测试 mock/离线）。
        db_path: 库路径；None=DB_PATH SSoT。
        asof_ts: 预测生效时点 ISO8601；None=落库当前 UTC。
        **compute_kwargs: 透传 compute_scenario_plan（config/revision/boundary）。

    Returns:
        (ScenarioPlan, prediction_log 行 id)；落库失败行 id=-1（plan 仍返回）。
    """
    plan = compute_scenario_plan(trade_date, ch_client=ch_client, **compute_kwargs)
    row_id = ScenarioPlanRecorder(ch_client=ch_client, db_path=db_path).record_plan(plan, asof_ts=asof_ts)
    return plan, row_id
