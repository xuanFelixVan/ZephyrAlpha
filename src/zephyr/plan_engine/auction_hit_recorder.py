# [BLUEPRINT] MOD-PLAN-015 | 待统筹登记（缺口总账 GAP-F-08 + 45号作战手册 §4 W3）
# [MODULE] zephyr.plan_engine.auction_hit_recorder
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.scenario_plan_recorder（determine_actual_scenario 命中判定口径复用，MOD-PLAN-008）; zephyr.plan_engine.scenario_planner（AuctionVerification 竞价三细节透传，MOD-PLAN-005）; zephyr.reporting.prediction_log_writer（log_prediction/query_predictions）; zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（表名解析）
# [CONSUMERS] 作战室 W3 观察哨（当前命中格点亮）; W0 昨日预案验证; 复盘页预案回看; （候选：W2 矩阵格高亮联动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 盘中 10:00 判定时点语义（phase=intraday_1000，开盘桶×30分钟走势桶→9格）；命中判定口径恒与 MOD-PLAN-008 一致（determine_actual_scenario 复用不重写）；D3 fake_ratio>0.6→direction_void 红色留痕（竞价方向信号作废）；append-only 仅 INSERT 经 prediction_log_writer 公共 API 零裸 SQL 写库；幂等保首条；落库/查询/CH 异常 fail-open 不阻塞盘中主流程；输入校验 fail-closed；错误消息不含 session_id
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-08 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（trade_date/config 非法 fail-closed）；CH/落库异常 fail-open（status=skipped:*/error:* 留痕不外抛）
# [TESTS] tests/plan_engine/test_auction_hit_recorder.py
# [A_module] module_id=MOD-PLAN-015 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""AuctionHitRecorder — 竞价命中分支判定持久化 (MOD-PLAN-015)

缺口总账 GAP-F-08 落码：盘中实时判定"实际命中哪格"+落库，供作战室 W3 观察哨
（当前命中格点亮）/W0 昨日预案验证/复盘页预案回看消费。

与 MOD-PLAN-008（scenario_plan_recorder.writeback_outcome）的边界：
    - 008=盘后日频 outcome 回写（prediction 维三维归因/Brier 校准真源）；
    - 本模块=盘中 10:00 实时命中判定（phase="intraday_1000"），竞价三细节
      （D1 偏离/D2 量比/D3 撤单）随命中格一并落库——W3 观察哨"9:25 二次匹配
      + 9:30-10:00 观察→命中格点亮"的持久化载体。命中判定口径（开盘桶 ±2%
      ×走势桶 30 分钟 VWAP ±0.1%）复用 008 determine_actual_scenario，零分叉。

数据底座（GAP-F-D2 2026-08-23 实测）：auction_snapshot 31,261 行/6 交易日、
auction_book 144.5 万行/13 交易日，9:15-9:25 窗口覆盖在库（9:20 分界前后
均有快照，D3 撤单识别可行）——本模块按真实数据源施工；竞价三细节计算归
MOD-PLAN-005（本模块经 AuctionVerification 注入透传，不重复计算）。

不做什么：不重算竞价三细节（MOD-PLAN-005 职责）/不做方向点预测/不参与
         集合竞价下单（40号决策⑧）/不写 execution/pnl 维度。

依据: 缺口总账 GAP-F-08；45_warroom_playbook §4 W3；44号 §9.11
SSoT: depgraph MOD-PLAN-015（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: trade_date + kline_index(开盘桶) + kline_etf_1min(走势桶) + AuctionVerification(注入透传) + scenario_plan 预测行
# 特征: open_pct(指数开盘偏离) / trend_pct(30分钟 VWAP 偏离或日线代理) / fake_ratio(D3)
# 算法: 开盘桶×走势桶 → 9 格命中格（008 口径复用）→ hit=命中格==预案格 → auction_hit 族落库
# 输出: prediction_log auction_hit 族行 + AuctionHitVerdict（status/hit/actual_scenario/direction_void/row_id）
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.plan_engine.scenario_plan_recorder import (
    OPEN_THRESHOLD,
    TREND_TOLERANCE,
    determine_actual_scenario,
)
from zephyr.plan_engine.scenario_planner import AuctionVerification
from zephyr.reporting.prediction_log_writer import (
    log_prediction,
    query_predictions,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "MODULE_LOG_NAME",
    "PREDICTION_TYPE_AUCTION_HIT",
    "AuctionHitConfig",
    "AuctionHitVerdict",
    "record_auction_hit",
]

# ── prediction_log 落库口径常量 ──

MODULE_LOG_NAME: Final = "plan_engine.auction_hit_recorder"  # prediction_log.module（本模块口径）
PREDICTION_TYPE_AUCTION_HIT: Final = "auction_hit"  # 盘中命中族（W3/W0/复盘页消费键）
PHASE_INTRADAY: Final = "intraday_1000"  # 判定时点语义（10:00 纪律线，走势窗闭环）

# ── 判定口径默认值（与 MOD-PLAN-008 同源常量复用）──

FAKE_RATIO_VOID: Final = 0.6  # D3 虚假申报作废阈值（44号 §9.11，>0.6 严格大于）
INDEX_SYMBOL: Final = "000001.SH"  # 开盘桶判定指数（上证指数）
TREND_PROXY_SYMBOL: Final = "510300.SH"  # 30 分钟走势判定代理（300ETF）
TREND_WINDOW_START: Final = "09:30"
TREND_WINDOW_END: Final = "10:00"

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 scenario_plan_recorder 同约定同口径）
_SQL_INDEX_TWO_DAY: Final = (
    "SELECT trade_date, toFloat64(open) AS o, toFloat64(close) AS c "
    "FROM {table} FINAL WHERE symbol_canonical = '{symbol}' "
    "AND trade_date <= toDate('{trade_date}') ORDER BY trade_date DESC LIMIT 2"
)
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
    """安全转 float；失败返回 None（供降级判定）。"""
    if v is None:
        return None
    try:
        import math

        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _validate_trade_date(trade_date: object) -> str:
    """交易日校验：YYYY-MM-DD 且为真实日期（fail-closed）。"""
    import re

    if not isinstance(trade_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", trade_date):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
    try:
        datetime.date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    return trade_date


# ── 配置与输出契约 ──


@dataclass(frozen=True)
class AuctionHitConfig:
    """盘中命中判定配置（默认值=44/45号设计口径，与 008 同参）。"""

    open_threshold: float = OPEN_THRESHOLD  # 高/低开判定阈值 ±2%
    trend_tolerance: float = TREND_TOLERANCE  # 平走容忍带 ±0.1%
    fake_ratio_void: float = FAKE_RATIO_VOID  # D3 作废阈值
    index_symbol: str = INDEX_SYMBOL
    trend_proxy_symbol: str = TREND_PROXY_SYMBOL
    trend_window_start: str = TREND_WINDOW_START
    trend_window_end: str = TREND_WINDOW_END
    allow_daily_proxy: bool = True  # 分钟缺失时日线代理（trend_source 留痕可过滤）

    def __post_init__(self) -> None:
        if _safe_float(self.open_threshold) is None or self.open_threshold <= 0:
            raise ValueError(f"open_threshold 非法（须正实数）: {self.open_threshold!r}")
        if _safe_float(self.trend_tolerance) is None or self.trend_tolerance < 0:
            raise ValueError(f"trend_tolerance 非法（须非负实数）: {self.trend_tolerance!r}")
        if _safe_float(self.fake_ratio_void) is None or not (0.0 < self.fake_ratio_void < 1.0):
            raise ValueError(f"fake_ratio_void 非法（须 ∈ (0,1)）: {self.fake_ratio_void!r}")


@dataclass(frozen=True)
class AuctionHitVerdict:
    """盘中命中判定结论（record_auction_hit 返回，JSON 可序列化）。"""

    trade_date: str
    status: str  # ok / skipped:no_open_data / skipped:no_trend_data / error:*
    actual_scenario: str | None  # 盘中命中格（SCENARIO_LIST 语义）
    hit: bool | None  # 命中格==预案 final_scenario（无预案行 → None）
    matched_plan_scenario: str | None  # 当日预案 final_scenario（None=无预案行）
    open_pct: float | None
    trend_pct: float | None
    trend_source: str | None  # kline_etf_1min / daily_proxy / None
    direction_void: bool  # D3 fake_ratio>阈值 → 竞价方向信号作废（红色留痕）
    row_id: int | None  # 落库行 id（None=未落库）
    annotations: list[str] = field(default_factory=list)
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典。"""
        from dataclasses import asdict

        return asdict(self)


# ── 数据加载（CH 注入/mocked；口径与 008 一致）──


def _table(category_id: str, fallback: str) -> str:
    """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
    try:
        from zephyr.data.table_registry import get_registry

        return get_registry().table(category_id)
    except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
        log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
        return fallback


def _query(ch: Callable[[str], str] | None, sql: str, channel: str) -> str:
    """执行 CH 查询；异常→返回空串+warning 留痕（fail-open，由调用方判降级）。"""
    try:
        if ch is not None:
            return ch(sql)
        from zephyr.data import ch_reader

        return ch_reader.query(sql)
    except Exception as exc:  # noqa: BLE001 — fail-open：单通道异常不炸整体
        log.warning("通道 %s 查询异常，降级跳过: %s", channel, exc)
        return ""


def _load_open_pct(ch: Callable[[str], str] | None, trade_date: str, cfg: AuctionHitConfig) -> float | None:
    """实际开盘涨幅：指数今日 open vs 昨日 close（kline_index 近两日，008 同口径）。"""
    table = _table("market_kline_index", "c1_market.kline_index")
    tsv = _query(
        ch,
        _SQL_INDEX_TWO_DAY.format(table=table, symbol=cfg.index_symbol, trade_date=trade_date),
        "kline_index",
    )
    rows = _parse_tsv(tsv, 3)
    if len(rows) < 2:
        return None
    today_open = _safe_float(rows[0][1])
    prev_close = _safe_float(rows[1][2])
    if today_open is None or prev_close is None or prev_close <= 0 or today_open <= 0:
        return None
    return (today_open - prev_close) / prev_close


def _load_trend_pct(
    ch: Callable[[str], str] | None,
    trade_date: str,
    cfg: AuctionHitConfig,
) -> tuple[float | None, str | None]:
    """30 分钟走势偏离：ETF 分钟窗末收 vs VWAP；缺数据按配置走日线代理（008 同口径）。

    Returns:
        (trend_pct, trend_source)；trend_source ∈ kline_etf_1min / daily_proxy / None。
    """
    table = _table("market_kline_etf_1min", "c1_market.kline_etf_1min")
    tsv = _query(
        ch,
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
    if rows:
        amt_sum = _safe_float(rows[0][0])
        vol_sum = _safe_float(rows[0][1])
        last_close = _safe_float(rows[0][2])
        if amt_sum and vol_sum and vol_sum > 0 and last_close and last_close > 0:
            vwap = amt_sum / vol_sum
            return (last_close - vwap) / vwap, "kline_etf_1min"
    if not cfg.allow_daily_proxy:
        return None, None
    table_idx = _table("market_kline_index", "c1_market.kline_index")
    tsv_idx = _query(
        ch,
        _SQL_INDEX_TWO_DAY.format(table=table_idx, symbol=cfg.index_symbol, trade_date=trade_date),
        "kline_index_proxy",
    )
    rows_idx = _parse_tsv(tsv_idx, 3)
    if not rows_idx:
        return None, None
    today_open = _safe_float(rows_idx[0][1])
    today_close = _safe_float(rows_idx[0][2])
    if today_open is None or today_close is None or today_open <= 0 or today_close <= 0:
        return None, None
    return (today_close - today_open) / today_open, "daily_proxy"


def _auction_payload(auction: AuctionVerification | None) -> dict[str, Any] | None:
    """竞价三细节透传 payload（MOD-PLAN-005 产出，本模块不重算）。"""
    if auction is None:
        return None
    return {
        "deviation": auction.deviation,
        "volume_ratio": auction.volume_ratio,
        "fake_ratio": auction.fake_ratio,
        "yesterday_limit_premium": auction.yesterday_limit_premium,
        "direction": auction.direction,
        "direction_consistent": auction.direction_consistent,
        "confirmed": auction.confirmed,
        "status": auction.status,
    }


# ── 主入口 ──


def record_auction_hit(
    trade_date: str,
    ch_client: Callable[[str], str] | None = None,
    db_path: str | Path | None = None,
    auction: AuctionVerification | None = None,
    config: AuctionHitConfig | None = None,
    asof_ts: str | None = None,
) -> AuctionHitVerdict:
    """盘中命中分支判定+落库主入口（MOD-PLAN-015，10:00 判定时点语义）。

    链路：实际开盘/走势判定（008 口径复用）→ 9 格命中格 → 读当日 scenario_plan
    预测行算 hit → auction_hit 族落库（prediction_log，幂等保首条，payload 携
    phase/命中格/开盘走势/竞价三细节透传/direction_void 契约字段）。任一数据
    缺失→对应 skipped:* 状态，不写库不抛异常。

    Args:
        trade_date: 交易日（非法即拒，fail-closed）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道。
        db_path: 库路径；None=DB_PATH SSoT（测试注入临时库）。
        auction: MOD-PLAN-005 竞价三细节产出（注入透传；None=竞价段未执行）。
        config: 判定口径配置（None=设计默认值）。
        asof_ts: 判定时点 ISO8601；None=落库当前 UTC。

    Returns:
        AuctionHitVerdict（任何数据/通道异常降级为对应 status，不外抛）。

    Raises:
        ValueError: trade_date 非法（fail-closed，仅此一类外抛）。
    """
    v_date = _validate_trade_date(trade_date)
    cfg = config or AuctionHitConfig()

    def _skip(status: str, **kw: Any) -> AuctionHitVerdict:
        return AuctionHitVerdict(
            trade_date=v_date,
            status=status,
            actual_scenario=kw.get("actual_scenario"),
            hit=kw.get("hit"),
            matched_plan_scenario=kw.get("matched_plan_scenario"),
            open_pct=kw.get("open_pct"),
            trend_pct=kw.get("trend_pct"),
            trend_source=kw.get("trend_source"),
            direction_void=kw.get("direction_void", False),
            row_id=None,
            annotations=kw.get("annotations", []),
            detail=kw.get("detail", {}),
        )

    open_pct = _load_open_pct(ch_client, v_date, cfg)
    if open_pct is None:
        return _skip("skipped:no_open_data", detail={"index_symbol": cfg.index_symbol})

    trend_pct, trend_source = _load_trend_pct(ch_client, v_date, cfg)
    if trend_pct is None or trend_source is None:
        return _skip(
            "skipped:no_trend_data",
            open_pct=open_pct,
            detail={"trend_proxy_symbol": cfg.trend_proxy_symbol},
        )

    actual = determine_actual_scenario(
        open_pct,
        trend_pct,
        open_threshold=cfg.open_threshold,
        trend_tolerance=cfg.trend_tolerance,
    )

    # 当日预案行（hit 判定基准；无预案行 → hit=None 仍落库，W3 只看命中格）
    matched: str | None = None
    try:
        rows = query_predictions(
            trade_date=v_date,
            module="plan_engine.scenario_planner",
            prediction_type="scenario_plan",
            limit=1,
            db_path=db_path,
        )
        if rows:
            import json

            payload = json.loads(rows[0]["payload_json"])
            fs = payload.get("final_scenario") if isinstance(payload, dict) else None
            matched = fs if isinstance(fs, str) else None
    except Exception as exc:  # noqa: BLE001 — fail-open：预案行查询异常不阻塞命中落库
        log.warning("预案行查询异常 fail-open（date=%s）: %s: %s", v_date, type(exc).__name__, exc)
    hit = None if matched is None else (actual == matched)

    direction_void = bool(
        auction is not None
        and auction.fake_ratio is not None
        and auction.fake_ratio > cfg.fake_ratio_void
    )
    annotations: list[str] = [f"盘中命中格={actual}（{PHASE_INTRADAY} 判定）"]
    if direction_void:
        annotations.append(
            f"D3 撤单比 fake_ratio={auction.fake_ratio:.2f}>{cfg.fake_ratio_void}（虚假申报），"
            "竞价方向信号作废（红色警示，进攻方案应已被 W4 风控否决）"
        )
    if trend_source == "daily_proxy":
        annotations.append("分钟数据缺失，走势桶日线代理留痕（校准统计可按 trend_source 过滤）")

    row_id: int | None = None
    try:
        row_id = log_prediction(
            trade_date=v_date,
            module=MODULE_LOG_NAME,
            prediction_type=PREDICTION_TYPE_AUCTION_HIT,
            payload={
                "phase": PHASE_INTRADAY,
                "actual_scenario": actual,
                "hit": hit,
                "matched_plan_scenario": matched,
                "open_pct": round(open_pct, 6),
                "trend_pct": round(trend_pct, 6),
                "trend_source": trend_source,
                "auction": _auction_payload(auction),
                "direction_void": direction_void,
            },
            asof_ts=asof_ts,
            db_path=db_path,
        )
        if row_id < 0:
            raise RuntimeError(f"log_prediction 返回 {row_id}")
    except Exception as exc:  # noqa: BLE001 — fail-open：落库失败不阻塞盘中主流程
        log.warning("auction_hit 落库失败 fail-open（date=%s）: %s: %s", v_date, type(exc).__name__, exc)
        return _skip(
            f"error:persist:{type(exc).__name__}",
            actual_scenario=actual,
            hit=hit,
            matched_plan_scenario=matched,
            open_pct=open_pct,
            trend_pct=trend_pct,
            trend_source=trend_source,
            direction_void=direction_void,
            annotations=annotations,
        )

    return AuctionHitVerdict(
        trade_date=v_date,
        status="ok",
        actual_scenario=actual,
        hit=hit,
        matched_plan_scenario=matched,
        open_pct=open_pct,
        trend_pct=trend_pct,
        trend_source=trend_source,
        direction_void=direction_void,
        row_id=row_id,
        annotations=annotations,
        detail={"index_symbol": cfg.index_symbol, "trend_proxy_symbol": cfg.trend_proxy_symbol},
    )
