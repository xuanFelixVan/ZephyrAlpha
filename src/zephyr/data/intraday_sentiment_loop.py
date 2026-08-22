# [BLUEPRINT] MOD-DATA-063 | 待统筹登记（blueprint 未建，真源=44号备忘 §2 M1-④ 行 + 92号清单 §8.2）
# [MODULE] zephyr.data.intraday_sentiment_loop
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.sector_intraday_aggregator（SEC-02 挂接）; zephyr.signal_ashare.market_sentiment_analyzer（MOD-SIG-025）; zephyr.reporting.prediction_log_writer（M4-②）; zephyr.data.ch_writer（默认客户端延迟加载，可注入旁路）; c1_market.market_breadth_snapshot / index_quote / kline_index / sector_snapshot（只读）
# [CONSUMERS] （常驻节拍交 APScheduler/P0-5 日循环 SOP 调度族挂接，本模块不注册任务——波5 交付单拍函数）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 单拍形态：只提供 run_once() 单拍函数，禁止 while True/常驻循环（PERM-TRIGGER 门禁纪律——永久驻留循环必须有界或由调度器节拍）；fail-open：任一 I/O 边界（快照读/指数读/prediction_log 写/SEC-02 聚合）单次失败 → errors 留痕不抛不炸调度；PIT（只读 ≤ 当前时点最新交易日快照）；快照缺失>2min 不外推（MOD-SIG-025 侧纪律）；输出容器 frozen dataclass（含 datetime 字段不直接 JSON 序列化；prediction_log payload 经写入器 canonical 序列化，datetime/Decimal 放行）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/92_phase2_business_construction_order.md §8.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 客户端不可用/查询异常→degraded=True+errors 留痕返回（不抛）；无当日快照→跳过情绪分析与落库、SEC-02 仍聚合（载体职责）；prediction_log 写入异常→errors 留痕返回
# [TESTS] tests/zephyr/data/test_intraday_sentiment_loop.py
# [A_module] module_id=MOD-DATA-063 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
r"""MOD-DATA-063 — M1-④ 盘中情绪实时调度回路（92号清单 §8.2，44号备忘 §2 M1-④ 行）。

单拍链路（run_once 一次执行）：
    读 c1_market.market_breadth_snapshot 最新交易日全部分钟快照
    → 装配 MarketSentimentInput.time_series（M1-① 波3 已施工的输入契约
      BreadthTimeSeries/BreadthSnapshot，本模块是其首个生产侧装配方）
    → 调 MOD-SIG-025 MarketSentimentAnalyzer.analyze（M1 增量特征组随 analyze 内链
      自动消费 time_series；指数涨跌幅经 index_quote×kline_index 两腿推导，
      失败降级 0.0+留痕）
    → 结果经 prediction_log_writer.log_prediction 落 governance.db prediction_log
      （波4 已建表，module=本模块路径，prediction_type="sentiment_score"，
      asof_ts=最新快照 ts——PIT 口径）
    → SEC-02 挂接同载体：sector_intraday_aggregator.load_latest_snapshots +
      aggregate_sector_intraday(previous_board=调用方逐轮持有的上轮榜) 一并聚合，
      榜面摘要随 payload 注解留痕并挂入返回值。

有界形态纪律（PERM-TRIGGER）：
    本模块**只做单拍**——常驻节拍交给 APScheduler 任务族，禁止在本模块写
    while True/自旋循环。挂接点=调度器节拍每拍调 run_once()，previous_board
    由调用方逐轮持有（SEC-02 新开板对照基线契约）。

与 P0-5 日循环 SOP 的对接注记：
    本回路属**盘中调度族**（intraday 9:30-15:00 分钟级），在日循环 SOP 中的位置=
    盘中段的情绪观测支线——盘前段（MOD-PLAN-002 边界加载）之后、尾盘段
    （MOD-PLAN-003 14:45 决策）之前持续供给情绪分与加速度特征；采集腿
    market_breadth_snapshot_minute 任务挂 L2 intraday_minute 族（tasks.yaml），
    本回路节拍随 P0-5 SOP 盘中段编排注册（对接点注记于此，注册动作不在本工单）。
    盘中族与日循环的硬时点（14:00/14:45 边界修正评估，M2 施工面）经
    prediction_log 共享载体解耦——本回路只写观测，不直接驱动交易动作。

fail-open 纪律：单次失败留痕（errors/nodes）不炸调度；全链路任一环节缺数据
按 degraded=True 返回结构化结果（观测可用性由消费方判定）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final

from zephyr.data.sector_intraday_aggregator import (
    SectorIntradayBoard,
    aggregate_sector_intraday,
    load_latest_snapshots,
)
from zephyr.data.table_registry import get_registry as _get_table_registry
from zephyr.reporting.prediction_log_writer import log_prediction
from zephyr.signal_ashare.market_sentiment_analyzer import (
    BreadthSnapshot,
    BreadthTimeSeries,
    IndexPerformanceData,
    LimitUpDownData,
    MarketBreadthData,
    MarketSentimentAnalyzer,
    MarketSentimentInput,
    MarketSentimentResult,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "IntradayLoopResult",
    "rows_to_time_series",
    "run_once",
]

# 表名真源：market_breadth_snapshot 尚未登记 business_data_categories.yaml
# （92号工单纪律不写其他注册表 yaml，补登=统筹批后续项，补登后迁移 table_registry 真源）
_TBL_BREADTH: Final = "c1_market.market_breadth_snapshot"
_TBL_INDEX_QUOTE: Final = _get_table_registry().table("market_index_quote")
_TBL_KLINE_INDEX: Final = _get_table_registry().table("market_index_kline")

# SQL 集中化（NO-BARE-SQL gate 豁免 SQL_ 前缀；f-string 仅表名真源插值，日期参数化占位）
# 最新交易日全部分钟快照（FINAL 去重——同分钟重跑幂等替换在合并前可能双行并存）
SQL_BREADTH_LATEST_DAY: Final = f"""
SELECT ts, advancing, declining, flat, limit_up, limit_down, sealed, attempted,
       total_count, total_amount, trade_date
FROM {_TBL_BREADTH} FINAL
WHERE trade_date = (SELECT max(trade_date) FROM {_TBL_BREADTH})
ORDER BY ts
"""

# 上证指数盘中最新价（index_quote L1 盘中轮询；symbol 带后缀口径实证 000001.SH）
SQL_INDEX_LATEST_PRICE: Final = f"""
SELECT price, timestamp FROM {_TBL_INDEX_QUOTE} FINAL
WHERE symbol = '{{index_symbol}}' AND trade_date <= '{{trade_date}}'
ORDER BY timestamp DESC LIMIT 1
"""

# 上证指数最近可得昨收（kline_index 裸码口径实证 000001；严格 < 当日取昨收腿）
SQL_INDEX_PREV_CLOSE: Final = f"""
SELECT close FROM {_TBL_KLINE_INDEX} FINAL
WHERE symbol = '{{index_bare}}' AND trade_date < '{{trade_date}}'
ORDER BY trade_date DESC LIMIT 1
"""

_INDEX_SYMBOL: Final = "000001.SH"  # 上证指数（index_quote 后缀口径实证 2026-08-22）
_INDEX_BARE: Final = "000001"  # kline_index 裸码口径实证 2026-08-22
_INDEX_NAME: Final = "上证指数"

#: SQL_BREADTH_LATEST_DAY 返回列序（rows_to_time_series 输入 dict 键）
_BREADTH_ROW_KEYS: Final = (
    "ts",
    "advancing",
    "declining",
    "flat",
    "limit_up",
    "limit_down",
    "sealed",
    "attempted",
    "total_count",
    "total_amount",
    "trade_date",
)

#: prediction_log 写入标识（M4-② 四族之一：M1 情绪分）
_MODULE_ID: Final = "zephyr.data.intraday_sentiment_loop"
_PREDICTION_TYPE: Final = "sentiment_score"


@dataclass(frozen=True, slots=True)
class IntradayLoopResult:
    """run_once 单拍输出（frozen，asdict JSON 可序列化）。"""

    asof: str  # 最新快照时间戳 ISO；无快照 → ""
    trade_date: str = ""  # 数据日 YYYY-MM-DD
    n_snapshots: int = 0  # 当日已落库分钟快照数
    total_count: int = 0  # 最新快照全市场标的数
    sentiment: MarketSentimentResult | None = None  # MOD-SIG-025 输出（无快照 → None）
    prediction_log_id: int | None = None  # prediction_log 行 id（写失败/跳过 → None）
    sector_board: SectorIntradayBoard | None = None  # SEC-02 聚合榜（挂接同载体）
    degraded: bool = False  # 任一环节降级（客户端缺失/查询空/写失败）
    errors: tuple[str, ...] = ()  # fail-open 留痕（单次失败不炸调度）
    notes: tuple[str, ...] = ()  # 口径/降级注解


def _as_dt(v: object) -> datetime | None:
    """时间戳归一（datetime 原样；date 升 midnight；str 按 ISO 解析；非法 → None 由调用方跳过）。"""
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            return None
    return None


def _to_float(v: object, default: float = 0.0) -> float:
    """安全转 float（Decimal/int/str 兼容；None/空串/非法 → default）。"""
    if v is None or v == "":
        return default
    try:
        return float(v)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


def _to_int(v: object, default: int = 0) -> int:
    """安全转 int（None/非法 → default）。"""
    if v is None or v == "":
        return default
    try:
        return int(float(v))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


def rows_to_time_series(rows: list[dict[str, Any]]) -> tuple[BreadthTimeSeries, str] | None:
    """快照行序列 → MarketSentimentInput.time_series 契约装配（纯函数，无 I/O）。

    Args:
        rows: list[dict]，键=_BREADTH_ROW_KEYS（ts/advancing/declining/limit_up/
            sealed/attempted/total_count/trade_date；limit_down/flat/total_amount
            不参与 time_series 但同属行契约）。

    Returns:
        (BreadthTimeSeries, trade_date)；空序列/全部缺 ts → None（调用方降级）。
        快照按 ts 升序重排；total_count 取最新行（全市场家数当日不变）。
    """
    timed: list[tuple[datetime, dict[str, Any]]] = []
    for rec in rows:
        ts = _as_dt(rec.get("ts"))
        if ts is not None:
            timed.append((ts, rec))
    if not timed:
        return None
    timed.sort(key=lambda x: x[0])

    snapshots = tuple(
        BreadthSnapshot(
            timestamp=ts,
            advancing_count=_to_int(rec.get("advancing")),
            declining_count=_to_int(rec.get("declining")),
            limit_up_count=_to_int(rec.get("limit_up")),
            sealed_limit_up_count=_to_int(rec.get("sealed")),
            attempted_limit_up_count=_to_int(rec.get("attempted")),
        )
        for ts, rec in timed
    )
    latest_td = str(timed[-1][1].get("trade_date") or "")
    return (
        BreadthTimeSeries(
            snapshots=snapshots,
            total_count=_to_int(timed[-1][1].get("total_count")),
            zscore_stats=None,  # 20 日滚动统计=数据期积累后供给（44号 §9.1 消费方预计算口径）
        ),
        latest_td,
    )


def _load_index_change_pct(client: Any, trade_date: str) -> tuple[float | None, str | None]:
    """上证指数盘中涨跌幅（%）：index_quote 最新价 × kline_index 昨收两腿推导（fail-open）。

    Returns:
        (pct, error_note)；任一侧失败 → (None, 留痕串)，调用方降级 0.0+notes。
    """
    try:
        rows = client.execute(
            SQL_INDEX_LATEST_PRICE.format(index_symbol=_INDEX_SYMBOL, trade_date=trade_date)
        )
    except Exception as e:  # noqa: BLE001 — fail-open
        return None, f"index_quote 最新价查询失败: {e!r}"
    if not rows:
        return None, "index_quote 无盘中价（非交易时段/采集未起）"
    live = _to_float(rows[0][0], 0.0)
    if live <= 0:
        return None, f"index_quote 最新价非法: {rows[0][0]!r}"

    try:
        prev_rows = client.execute(
            SQL_INDEX_PREV_CLOSE.format(index_bare=_INDEX_BARE, trade_date=trade_date)
        )
    except Exception as e:  # noqa: BLE001 — fail-open
        return None, f"kline_index 昨收查询失败: {e!r}"
    if not prev_rows:
        return None, "kline_index 无昨收腿"
    prev_close = _to_float(prev_rows[0][0], 0.0)
    if prev_close <= 0:
        return None, f"kline_index 昨收非法: {prev_rows[0][0]!r}"
    return (live - prev_close) / prev_close * 100.0, None


def _build_sentiment_payload(
    result: MarketSentimentResult,
    *,
    n_snapshots: int,
    latest_row: dict[str, Any],
    sector_board: SectorIntradayBoard | None,
) -> dict[str, Any]:
    """情绪分析结果 → prediction_log payload（canonical JSON 可序列化；含 SEC-02 榜面摘要注解）。"""
    accel = result.breadth_acceleration
    payload: dict[str, Any] = {
        "overall_score": result.overall_score,
        "sentiment_phase": result.sentiment_phase,
        "breadth_status": result.breadth_status,
        "breadth_score": result.breadth_score,
        "limit_zeal_status": result.limit_zeal_status,
        "limit_score": result.limit_score,
        "seal_rate": result.seal_rate,
        "seal_rate_status": result.seal_rate_status,
        "next_day_risk_status": result.next_day_risk_status,
        "next_day_risk_score": result.next_day_risk_score,
        "time_series_minutes": n_snapshots,
        "snapshot": {
            "advancing": _to_int(latest_row.get("advancing")),
            "declining": _to_int(latest_row.get("declining")),
            "flat": _to_int(latest_row.get("flat")),
            "limit_up": _to_int(latest_row.get("limit_up")),
            "limit_down": _to_int(latest_row.get("limit_down")),
            "sealed": _to_int(latest_row.get("sealed")),
            "attempted": _to_int(latest_row.get("attempted")),
            "total_amount": _to_float(latest_row.get("total_amount")),
        },
        "breadth_acceleration": (
            {
                "breadth_vel_5m": accel.breadth_vel_5m,
                "breadth_acc_15m": accel.breadth_acc_15m,
                "lu_net_rate_5m": accel.lu_net_rate_5m,
                "break_rate_5m": accel.break_rate_5m,
                "repairing": accel.repairing,
                "deteriorating": accel.deteriorating,
            }
            if accel is not None
            else None
        ),
        "distortion_flag": result.distortion.distortion_flag if result.distortion is not None else None,
    }
    if sector_board is not None:
        # SEC-02 榜面摘要注解（观测留痕；新开板对照基线=调用方逐轮持有的上轮榜）
        payload["sector_board"] = {
            "asof": sector_board.asof,
            "n_sectors": sector_board.n_sectors,
            "degraded": sector_board.degraded,
            "breadth_total_up": sector_board.breadth.total_up,
            "breadth_total_down": sector_board.breadth.total_down,
            "new_open_boards": list(sector_board.new_open_boards),
        }
    return payload


def _default_client() -> Any | None:
    """延迟加载默认 CH 客户端（不可用时返回 None，由调用方转降级）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        log.warning("ch_writer 默认客户端不可用", exc_info=True)
        return None


def run_once(
    ch_client: Any | None = None,
    *,
    db_path: str | None = None,
    previous_board: SectorIntradayBoard | None = None,
    analyzer: MarketSentimentAnalyzer | None = None,
    sector_window_minutes: int = 5,
) -> IntradayLoopResult:
    """M1-④ 盘中情绪回路单拍执行（有界形态——常驻节拍交 APScheduler/P0-5 盘中族，本函数不含循环）。

    Args:
        ch_client: clickhouse-driver 鸭子类型（execute(sql) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client()，不可得 → degraded 返回（不抛）。
        db_path: prediction_log 库路径；None=DB_PATH SSoT（测试注入临时库）。
        previous_board: 上一轮 SEC-02 榜（新开板对照基线；首轮 None → 空清单留痕）。
        analyzer: MOD-SIG-025 实例（None=默认构造；测试可注入配置变体）。
        sector_window_minutes: SEC-02 回看窗口分钟数（默认 5，覆盖 ≥2 个 30s 轮询周期）。

    Returns:
        IntradayLoopResult；任一环节失败 → errors 留痕 + degraded，不抛（fail-open）。
    """
    errors: list[str] = []
    notes: list[str] = []

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        return IntradayLoopResult(
            asof="",
            degraded=True,
            errors=("ch_client 未注入且默认客户端不可用",),
        )

    # ---- SEC-02 挂接同载体（独立环节：快照缺失时仍聚合，载体职责）----
    sector_board: SectorIntradayBoard | None = None
    try:
        sector_snaps = load_latest_snapshots(ch_client=client, minutes=sector_window_minutes)
        sector_board = aggregate_sector_intraday(sector_snaps, previous_board=previous_board)
    except Exception as e:  # noqa: BLE001 — fail-open
        errors.append(f"SEC-02 板块聚合失败: {e!r}")

    # ---- 读最新交易日分钟快照 ----
    try:
        raw = client.execute(SQL_BREADTH_LATEST_DAY)
    except Exception as e:  # noqa: BLE001 — fail-open
        errors.append(f"market_breadth_snapshot 查询失败: {e!r}")
        return IntradayLoopResult(asof="", degraded=True, errors=tuple(errors), sector_board=sector_board)
    rows = [dict(zip(_BREADTH_ROW_KEYS, r, strict=True)) for r in raw]
    assembled = rows_to_time_series(rows)
    if assembled is None:
        notes.append("当日 market_breadth_snapshot 无快照（采集未起/非交易日），跳过情绪分析")
        return IntradayLoopResult(
            asof="", degraded=True, errors=tuple(errors), notes=tuple(notes), sector_board=sector_board
        )
    time_series, trade_date = assembled
    latest_row = rows[-1]
    latest_ts = _as_dt(latest_row.get("ts"))
    asof = latest_ts.isoformat() if latest_ts is not None else ""

    # ---- 指数涨跌幅（M1-② 恶化中信号 + 维度④ 输入；失败降级 0.0 留痕）----
    index_pct, index_err = _load_index_change_pct(client, trade_date)
    if index_pct is None:
        notes.append(f"指数涨跌幅不可得降级 0.0：{index_err}")
        index_pct = 0.0

    # ---- 装配 MarketSentimentInput（M1-① time_series 契约生产侧）----
    total_count = time_series.total_count
    latest_amount = _to_float(latest_row.get("total_amount"))
    input_data = MarketSentimentInput(
        timestamp=latest_ts or datetime.now(),
        breadth=MarketBreadthData(
            advancing_count=_to_int(latest_row.get("advancing")),
            declining_count=_to_int(latest_row.get("declining")),
            flat_count=_to_int(latest_row.get("flat")),
            total_count=total_count,
        ),
        limit_data=LimitUpDownData(
            limit_up_count=_to_int(latest_row.get("limit_up")),
            limit_down_count=_to_int(latest_row.get("limit_down")),
            near_limit_up_count=0,  # 口径留痕：接近涨停(涨幅>9%)计数不在快照表层（44号 §9.1 未列入 s_t）
            sealed_limit_up_count=_to_int(latest_row.get("sealed")),
            attempted_limit_up_count=_to_int(latest_row.get("attempted")),
        ),
        index_performance=IndexPerformanceData(index_name=_INDEX_NAME, index_change_pct=index_pct),
        market_turnover=latest_amount / 1e8,  # 元 → 亿（MarketSentimentInput 口径）
        time_series=time_series,
    )

    # ---- 调 MOD-SIG-025（M1 增量特征组随 analyze 内链消费 time_series）----
    engine = analyzer or MarketSentimentAnalyzer()
    try:
        sentiment = engine.analyze(input_data)
    except Exception as e:  # noqa: BLE001 — fail-open
        errors.append(f"MOD-SIG-025 分析失败: {e!r}")
        return IntradayLoopResult(
            asof=asof,
            trade_date=trade_date,
            n_snapshots=len(time_series.snapshots),
            total_count=total_count,
            sector_board=sector_board,
            degraded=True,
            errors=tuple(errors),
            notes=tuple(notes),
        )

    # ---- 落 prediction_log（M4-② 统一载体；写失败留痕不炸）----
    prediction_id: int | None = None
    try:
        prediction_id = log_prediction(
            trade_date=trade_date,
            module=_MODULE_ID,
            prediction_type=_PREDICTION_TYPE,
            payload=_build_sentiment_payload(
                sentiment,
                n_snapshots=len(time_series.snapshots),
                latest_row=latest_row,
                sector_board=sector_board,
            ),
            asof_ts=asof or None,
            db_path=db_path,
        )
    except Exception as e:  # noqa: BLE001 — fail-open
        errors.append(f"prediction_log 写入失败: {e!r}")

    log.info(
        "intraday_sentiment_loop 单拍完成: %s %s score=%.1f phase=%s minutes=%d sectors=%d errors=%d",
        trade_date,
        asof,
        sentiment.overall_score,
        sentiment.sentiment_phase,
        len(time_series.snapshots),
        sector_board.n_sectors if sector_board is not None else 0,
        len(errors),
    )
    return IntradayLoopResult(
        asof=asof,
        trade_date=trade_date,
        n_snapshots=len(time_series.snapshots),
        total_count=total_count,
        sentiment=sentiment,
        prediction_log_id=prediction_id,
        sector_board=sector_board,
        degraded=bool(errors),
        errors=tuple(errors),
        notes=tuple(notes),
    )
