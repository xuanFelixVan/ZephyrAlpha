"""阶段二（92号清单 §9 波6）盘前/盘中新模块跨模块端到端集成测试。

真实调用链（非单测堆砌），全合成数据 + mock CH + tmp SQLite，不触生产 CH/DB、不触网络：

- 链 A 盘中情绪→边界修正→落库：合成分钟快照序列（BreadthTimeSeries）→
  MOD-SIG-025 analyze_breadth_acceleration 出加速度 → analyze 出综合分 →
  boundary_revision_engine.evaluate_boundary_revision（14:00/14:45 两槽，InMemoryJsonStateStore
  跨调用防抖）→ 断言降档修正 → prediction_log（tmp 库）plan_revision 事件可读回。
- 链 B 盘前全链：mock CH（外盘/两融/资金/大宗/日历全合成）→
  overnight_boundary_reviser.compute_overnight_revision 出 final_shift →
  scenario_planner.compute_scenario_plan（auction_book 合成序列）出三情景+竞价验证 →
  llm_premarket_analysis.build_premarket_package（PIT cutoff 越界注入拒收断言）→
  mock llm_client（合规 JSON）→ run_llm_analysis → llm_daily_analysis（tmp 库）
  success 行落库 + input_hash 一致 + 幂等重跑保首条。
- 链 C 期指基差→M2 降档：合成期货/现货序列（贴水急扩超 1.5σ）→
  futures_basis_monitor.compute_futures_basis 出 discount_alert → 喂 boundary_revision_engine
  IM 贴水触发源（两个合成 ts 快照满足防抖 ≥15min）→ 断言降档触发 + 留痕落库。
- 链 D 板块观测链：合成板块/成分/个股数据 → sector_divergence.compute_sector_divergence
  出 5 状态+速度计+标定 → sector_leader.identify_sector_leaders 出四档 →
  mainline_candidates.compute_mainline_candidates 出榜 → sector_report_builder 编排
  （同一复合 mock CH 各源）→ 断言报告结构完整（Top10/状态/梯队/主线键齐）。
- 链 E 校准闭环：tmp 库 prediction_log 播种 30 条预测+outcome 真值（命中率 0.4）→
  prediction_calibration_monitor.compute_hit_rate_stats → evaluate_calibration_trigger →
  断言触发评审工单（命中率<0.55 且样本≥30）+ calibration_trigger 事件落库。
- 链 F 快照采集→回路：合成全市场 tick → market_breadth_collector.aggregate_market_ticks
  聚合 → build_insert_row 列序契约 → 回读行装配 → intraday_sentiment_loop.run_once
  （mock CH+tmp prediction_log）→ 断言快照行结构+time_series 装配+情绪分落库。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from zephyr.data.intraday_sentiment_loop import run_once
from zephyr.data.market_breadth_collector import (
    INSERT_COLUMN_NAMES,
    aggregate_market_ticks,
    build_insert_row,
)
from zephyr.data.sector_report_builder import build_sector_report, report_to_dict
from zephyr.plan_engine.boundary_revision_engine import (
    TRIGGER_IM_BASIS_DISCOUNT,
    TRIGGER_SENTIMENT_BREADTH,
    InMemoryJsonStateStore,
    evaluate_boundary_revision,
)
from zephyr.plan_engine.llm_premarket_analysis import (
    DEFAULT_MODEL_VERSION,
    PROMPT_VERSION,
    STATUS_SUCCESS,
    PremarketInjections,
    build_premarket_package,
    run_llm_analysis,
)
from zephyr.plan_engine.overnight_boundary_reviser import compute_overnight_revision
from zephyr.plan_engine.scenario_planner import compute_scenario_plan
from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary
from zephyr.reporting.prediction_calibration_monitor import (
    compute_hit_rate_stats,
    evaluate_calibration_trigger,
    record_outcome,
)
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
    query_predictions,
)
from zephyr.signal_ashare.futures_basis_monitor import (
    DEFAULT_PRODUCTS,
    FuturesBasisConfig,
    FuturesBasisSnapshot,
    FuturesBasisSymbol,
    compute_futures_basis,
)
from zephyr.signal_ashare.lhb_premium_analyzer import LhbPremiumResult
from zephyr.signal_ashare.mainline_candidates import compute_mainline_candidates
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
from zephyr.signal_ashare.option_sentiment import OptionSentimentResult
from zephyr.signal_ashare.sector_divergence import (
    SectorDivergenceResult,
    compute_sector_divergence,
)
from zephyr.signal_ashare.sector_leader import identify_sector_leaders


def _tsv(rows: list[tuple]) -> str:
    """行列表 → TSV（ch_reader.query 返回形态，与 plan_engine 单测同款）。"""
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


# ══════════════════════════════════════════════════════════════
# 链 A：盘中情绪 → 边界修正 → prediction_log 落库
# ══════════════════════════════════════════════════════════════

_DATE_A = "2026-08-21"  # 周五


def _chain_a_time_series() -> BreadthTimeSeries:
    """21 分钟快照（13:40→14:00）：上涨家数续降 + 涨停家数续减（lu_net_rate_5m<0）。"""
    base = datetime(2026, 8, 21, 13, 40)
    snaps = []
    for i in range(21):
        adv = 900 - 5 * i
        dec = 4000 + 5 * i
        lu = 12 - i // 2
        snaps.append(
            BreadthSnapshot(
                timestamp=base + timedelta(minutes=i),
                advancing_count=adv,
                declining_count=dec,
                limit_up_count=lu,
                sealed_limit_up_count=lu,
                attempted_limit_up_count=lu + 2,
            )
        )
    return BreadthTimeSeries(snapshots=tuple(snaps), total_count=5000)


def test_chain_a_intraday_sentiment_to_boundary_revision(tmp_path):
    ts = _chain_a_time_series()
    analyzer = MarketSentimentAnalyzer()

    # ① 加速度三件套（MOD-SIG-025 M1-①）
    accel = analyzer.analyze_breadth_acceleration(ts, index_change_pct=-1.8)
    assert accel is not None
    assert accel.breadth_vel_5m == pytest.approx((800 - 825) / 5000)
    assert accel.breadth_acc_15m is not None  # n=21 > 5+15 二阶窗口
    assert accel.lu_net_rate_5m is not None and accel.lu_net_rate_5m < 0
    assert accel.deteriorating is False  # 指数同步下跌，非"指数红个股跌"恶化形态

    # ② 综合情绪分（末快照：普跌+恐慌蔓延 → <35 降档线）
    sentiment = analyzer.analyze(
        MarketSentimentInput(
            timestamp=datetime(2026, 8, 21, 14, 0),
            breadth=MarketBreadthData(advancing_count=800, declining_count=4100, flat_count=100, total_count=5000),
            limit_data=LimitUpDownData(
                limit_up_count=2,
                limit_down_count=45,
                near_limit_up_count=3,
                sealed_limit_up_count=2,
                attempted_limit_up_count=4,
            ),
            index_performance=IndexPerformanceData(index_name="上证指数", index_change_pct=-1.8),
            time_series=ts,
        )
    )
    assert 0.0 <= sentiment.overall_score <= 100.0
    assert sentiment.overall_score < 35.0  # 降档触发腿① 条件一
    assert sentiment.breadth_acceleration is not None

    # ③ 边界修正引擎（14:00 首现防抖 → 14:45 确认降档；state_store 跨调用累积）
    store = InMemoryJsonStateStore()
    db = tmp_path / "gov_e2e_a.db"
    rev1 = evaluate_boundary_revision(
        _DATE_A,
        "14:00",
        sentiment=sentiment,
        state_store=store,
        eval_time="14:00",
        log_db_path=db,
    )
    assert rev1.revision_applied is False
    assert TRIGGER_SENTIMENT_BREADTH in rev1.pending_triggers
    assert rev1.debounce_proof[TRIGGER_SENTIMENT_BREADTH]["confirmed"] is False

    rev2 = evaluate_boundary_revision(
        _DATE_A,
        "14:45",
        sentiment=sentiment,
        state_store=store,
        eval_time="14:45",
        log_db_path=db,
    )
    assert rev2.revision_applied is True
    assert rev2.direction == "DOWNGRADE"
    assert rev2.original_tier == "NORMAL" and rev2.revised_tier == "CONSERVATIVE"
    assert rev2.triggers == [TRIGGER_SENTIMENT_BREADTH]
    assert rev2.position_cap_scale == pytest.approx(0.5)
    assert rev2.no_add_price_shift == pytest.approx(-0.5)
    assert rev2.logged is True
    # 30m 字段未落地 → 5m 口径代理留痕（跨模块契约对齐点）
    assert rev2.trace["trigger_details"][TRIGGER_SENTIMENT_BREADTH]["rate_proxy_5m"] is True
    assert rev2.is_effective_on(_DATE_A) is True
    assert rev2.is_effective_on("2026-08-24") is False  # 修正仅当日有效

    # ④ plan_revision 事件落 prediction_log（tmp 库）可读回
    rows = query_predictions(trade_date=_DATE_A, prediction_type="plan_revision", db_path=db)
    assert len(rows) == 1
    assert rows[0]["module"] == "plan_engine.boundary_revision_engine"
    payload = json.loads(rows[0]["payload_json"])
    assert payload["revised_tier"] == "CONSERVATIVE"
    assert payload["direction"] == "DOWNGRADE"
    assert payload["triggers"] == [TRIGGER_SENTIMENT_BREADTH]


# ══════════════════════════════════════════════════════════════
# 链 B：盘前全链（隔夜修正 → 三情景+竞价验证 → LLM 打包/分析/落库）
# ══════════════════════════════════════════════════════════════

_DATE_B = "2026-08-24"  # 周一
_T1 = "2026-08-21"  # T-1（周五）
_T2 = "2026-08-20"  # T-2


def _z_series_tsv(latest: float, hist_lo: float, hist_hi: float, n: int = 20) -> str:
    """21 行日序列（DESC）：latest + n 个历史点（hist_lo/hist_hi 交替，std>0）。"""
    base = date(2026, 8, 21)
    rows = [(base, latest)]
    for i in range(1, n + 1):
        rows.append((base - timedelta(days=i), hist_lo if i % 2 else hist_hi))
    return _tsv(rows)


def _ch_b_overnight():
    """隔夜修正 mock CH：外盘双序列暴跌 + 资金面同向确认 + 日历空表 fail-open。"""
    us_index = _tsv(
        [
            (_T1, "SPX", 6240.0),
            (_T2, "SPX", 6500.0),  # ret_SPX=-4%
            (_T1, "IXIC", 20370.0),
            (_T2, "IXIC", 21000.0),  # ret_NDX=-3%
        ]
    )
    margin = _z_series_tsv(10.0, 100.0, 120.0)  # z=-10（与 gap 同向）
    mf = _z_series_tsv(0.1, 1.0, 1.2)  # z=-10
    bt = _z_series_tsv(-0.05, 0.01, -0.01)  # z=-5

    def _ch(sql: str) -> str:
        if "us_index" in sql:
            return us_index
        if "margin_trading" in sql:
            return margin
        if "money_flow" in sql:
            return mf
        if "block_trade" in sql:
            return bt
        if "calendar_event" in sql:
            return ""
        return ""

    return _ch


def _ch_b_auction():
    """竞价 mock CH：低开 -2.5% + 放量 1.6× + 撤单比 0.04（真实低开确认）。"""
    snapshot = _tsv(
        [
            ("600000.SH", "600000.SH", 9.75, 10.0, 1000, 97500),
            ("000001.SZ", "000001.SZ", 19.5, 20.0, 600, 58500),
        ]
    )
    history = _tsv(
        [
            (d, sym, 500.0)
            for d in ("2026-08-21", "2026-08-20", "2026-08-19", "2026-08-18", "2026-08-17")
            for sym in ("600000.SH", "000001.SZ")
        ]
    )
    series = _tsv([("600000.SH", 5000, 4800, 3, 2), ("000001.SZ", 3000, 2900, 3, 2)])
    limit_up = _tsv([("600000.SH",)])

    def _ch(sql: str) -> str:
        if "stk_limit" in sql:
            return limit_up
        if "auction_book" in sql:
            if "maxIf(" in sql:
                return series
            if "GROUP BY trade_date, symbol" in sql:
                return history
            return snapshot
        return ""

    return _ch


def _ch_b_llm():
    """LLM 打包器 mock CH：七族日频全合成（路由口径对齐 test_llm_premarket_analysis）。"""
    days = [_T1, _T2] + [f"2026-08-{d:02d}" for d in range(19, 0, -1)] + ["2026-07-31"]
    index_rows: list[tuple] = []
    for sym, name in (("000001", "上证指数"), ("399001", "深证成指"), ("399006", "创业板指"), ("000688", "科创50")):
        for i, d in enumerate(days):
            if sym == "000001":
                close = {0: 3860.0, 1: 3840.0}.get(i, 3800.0)
                high, low = (3880.0, 3840.0) if i == 0 else (close + 10.0, close - 10.0)
                amt = 5000.0 if i == 0 else 4000.0
            else:
                close, high, low, amt = 1000.0, 1010.0, 990.0, 2000.0
            index_rows.append((sym, name, d, close, high, low, close, amt, 100))
    sector_kline = _tsv(
        [
            (c, _T2, c2)
            for c, (c2, _c1) in {
                "880002": (1000.0, 1010.0),
                "880003": (1000.0, 950.0),
                "880004": (1000.0, 1030.0),
                "880005": (1000.0, 980.0),
                "880006": (1000.0, 1005.0),
                "880007": (1000.0, 1020.0),
            }.items()
        ]
        + [
            (c, _T1, c1)
            for c, (_c2, c1) in {
                "880002": (1000.0, 1010.0),
                "880003": (1000.0, 950.0),
                "880004": (1000.0, 1030.0),
                "880005": (1000.0, 980.0),
                "880006": (1000.0, 1005.0),
                "880007": (1000.0, 1020.0),
            }.items()
        ]
    )
    data = {
        "prev_dates": _tsv([(_T1,), (_T2,)]),
        "index": _tsv(index_rows),
        "breadth": _tsv([("3000", "1800", "200")]),
        "limit_stats": _tsv([("45", "60", "12")]),
        "limit_up_symbols": _tsv([("600000.SH",), ("000001.SZ",)]),
        "next_perf": _tsv([("600000.SH", "5.0"), ("000001.SZ", "-2.0")]),
        "sector_names": _tsv([("880002", "半导体"), ("880003", "医药"), ("880004", "券商")]),
        "sector_kline": sector_kline,
        "money_flow_day": _tsv([("600000.SH", "20000"), ("000001.SZ", "50000")]),
        "constituents": _tsv([("880004", "600000.SH"), ("880004", "000001.SZ")]),
        "us_index": _tsv([(_T1, "SPX", "6240"), (_T2, "SPX", "6500"), (_T1, "IXIC", "20370"), (_T2, "IXIC", "21000")]),
        "margin": _z_series_tsv(10.0, 100.0, 120.0),
        "money_flow_agg": _tsv([(_T1, "-800000", "-0.35")]),
        "block_trade": _tsv([(_T1, "-0.062")]),
        "calendar": _tsv([(_T1, "futures_delivery"), (_DATE_B, "option_expiry")]),
    }

    def _ch(sql: str) -> str:
        if "calendar_event" in sql:
            return data["calendar"]
        if "block_trade" in sql:
            return data["block_trade"]
        if "margin_trading" in sql:
            return data["margin"]
        if "us_index" in sql:
            return data["us_index"]
        if "kline_sector_880" in sql:
            return data["sector_kline"]
        if "sector_meta" in sql:
            return data["sector_names"]
        if "sector_constituent" in sql:
            return data["constituents"]
        if "main_net_inflow_pct" in sql:
            return data["money_flow_agg"]
        if "money_flow" in sql:
            return data["money_flow_day"]
        if "countIf(toFloat64(close)" in sql:
            return data["limit_stats"]
        if "stk_limit" in sql:
            return data["limit_up_symbols"]
        if "SELECT DISTINCT trade_date" in sql:
            return data["prev_dates"]
        if "countIf(toFloat64(pct_change)" in sql:
            return data["breadth"]
        if "pct_change FROM" in sql:
            return data["next_perf"]
        if "kline_index" in sql:
            return data["index"]
        return ""

    return _ch


def _sentiment_injection(ts: datetime) -> MarketSentimentResult:
    return MarketSentimentResult(
        timestamp=ts,
        breadth_status="均衡",
        breadth_score=50.0,
        limit_zeal_status="正常",
        limit_score=55.0,
        profit_effect_status="中",
        profit_effect_score=52.0,
        next_day_risk_status="中风险",
        next_day_risk_score=48.0,
        morale_status="正常",
        morale_score=50.0,
        seal_rate_status="中",
        seal_rate=0.75,
        yesterday_lu_status="中",
        overall_score=58.0,
        sentiment_phase="主升",
    )


def _futures_injection(ts: str) -> FuturesBasisSnapshot:
    def _sym(product: str, rate: float) -> FuturesBasisSymbol:
        return FuturesBasisSymbol(
            product=product,
            spot_name="现货",
            basis_rate=rate,
            basis_vel_30m=-0.0005,
            vel_source="intraday_30m",
            discount_alert=False,
            confirm_flag=True,
            signal_weight=1.0,
            futures_price=3900.0,
            spot_price=3908.0,
            futures_leg="futures_kline_qmt",
            spot_leg="index_quote_intraday",
            sigma_20d=0.01,
            position_surge_pct=None,
            sensitivity="注解",
            degraded=False,
        )

    return FuturesBasisSnapshot(ts=ts, trade_date=_T1, per_symbol={"IF": _sym("IF", -0.002), "IM": _sym("IM", -0.008)})


def _premarket_injections(sentiment_ts: datetime) -> PremarketInjections:
    return PremarketInjections(
        sentiment_result=_sentiment_injection(sentiment_ts),
        sector_divergence=SectorDivergenceResult(
            date=_T1,
            rotation_state="HEALTHY_MAINLINE",
            siphon_z=0.8,
            rotation_velocity=3.2,
            velocity_percentile=0.4,
        ),
        futures_snapshot=_futures_injection(f"{_T1} 15:00:00"),
        option_sentiment=OptionSentimentResult(
            date=_T1, pcr=0.85, pcr_percentile=0.6, iv_rank=0.45, skew_norm=0.08, skew_extreme=False
        ),
        lhb_result=LhbPremiumResult(
            date=_T1,
            high_open_candidates=["600000.SH"],
            low_open_risks=["000001.SZ"],
            fanhe_watchlist=["300750.SZ"],
        ),
        bs005_triggered=False,
    )


def _llm_ok(prompt: str) -> str:
    """合规 JSON 应答（三情景概率和=1，date=交易日）。"""
    assert "盘前数据包" in prompt  # prompt 组装链路断言（数据包注入）
    return json.dumps(
        {
            "date": _DATE_B,
            "scenarios": {
                "gap_up": {"prob": 0.20, "key_levels": ["上证 3860"], "action_boundary": "高开不追仓"},
                "flat": {"prob": 0.55, "key_levels": ["上证 3840"], "action_boundary": "按昨夜边界执行"},
                "gap_down": {"prob": 0.25, "key_levels": ["上证 3800"], "action_boundary": "企稳前禁新开仓"},
            },
            "risk_points": ["外围隔夜暴跌传导"],
            "watch_sectors": ["券商"],
            "confidence_note": "外盘缺口已计入，数据齐",
        },
        ensure_ascii=False,
    )


def test_chain_b_premarket_full_chain(tmp_path):
    # ── 段 1：隔夜边界修正（MOD-PLAN-004，三通道合成）──
    rev = compute_overnight_revision(_DATE_B, ch_client=_ch_b_overnight())
    assert rev.gap_adj == pytest.approx(0.2 * -0.04 + 0.3 * -0.03)  # -1.7%
    assert rev.final_shift == -1.0  # |gap|≥1.5% → -1 档；资金面同向确认不否决
    assert rev.fund_score is not None and rev.fund_score < 0
    assert any("确认" in r for r in rev.reasons)
    assert rev.event_flags["calendar_status"] == "empty_or_failed"  # 日历空表 fail-open

    # ── 段 2：三情景+竞价验证（MOD-PLAN-005，revision 跨模块注入）──
    boundary = TomorrowBoundary(
        symbol="600000.SH",
        box_upper=11.0,
        box_lower=9.5,
        max_add_position=0.30,
        no_add_price=10.8,
        must_exit_price=11.0,
        breakout_confirm="放量站稳10分钟",
        computed_at=None,
    )
    plan = compute_scenario_plan(_DATE_B, ch_client=_ch_b_auction(), revision=rev, boundary=boundary)
    assert plan.trace["channels"]["overnight_revision"] == "injected"
    assert len(plan.three_scenarios) == 3
    assert [s.name for s in plan.three_scenarios] == ["HIGH_OPEN", "FLAT_OPEN", "LOW_OPEN"]
    assert all(s.stance == "CONSERVATIVE" for s in plan.three_scenarios)
    assert all(s.max_add_position == pytest.approx(0.30 * 0.5) for s in plan.three_scenarios)
    av = plan.auction_verification
    assert av is not None and av.status == "ok"
    assert av.direction == "DOWN" and av.direction_consistent is True  # 与 gap_adj 同向
    assert av.confirmed is True and av.direction_void is False
    assert plan.final_scenario == "LOW_OPEN_REAL_DOWN"
    assert plan.confidence_scale == pytest.approx(1.0)

    # ── 段 3：LLM 盘前数据包（MOD-PLAN-007 打包器，PIT cutoff 双护栏）──
    pkg = build_premarket_package(
        _DATE_B, ch_client=_ch_b_llm(), injected=_premarket_injections(datetime(2026, 8, 21, 15, 0))
    )
    assert pkg.trade_date == _DATE_B
    assert pkg.asof_cutoff == f"{_DATE_B} 08:00:00"
    assert set(pkg.families) == {"index", "sentiment", "sector", "derivatives", "overseas", "capital", "calendar"}
    assert pkg.rejected == []  # 全部注入 T-1 可见 → 准入
    assert pkg.families["sentiment"]["m1_overall_score"] == pytest.approx(58.0)
    assert pkg.families["derivatives"]["im_basis_rate"] == pytest.approx(-0.008)
    assert pkg.families["overseas"]["spx"]["pct_change"] == pytest.approx(-0.04)
    assert pkg.input_hash

    # PIT 铁律①：cutoff（08:00）后数据点拒绝入包 + rejected 留痕
    pkg_late = build_premarket_package(
        _DATE_B, ch_client=_ch_b_llm(), injected=_premarket_injections(datetime(2026, 8, 24, 9, 30))
    )
    assert any(r["family"] == "sentiment" and r["field"] == "m1_result" for r in pkg_late.rejected)
    assert pkg_late.families["sentiment"]["m1_overall_score"] is None
    assert pkg_late.families["sentiment"]["status"] == "degraded:pit_rejected"

    # ── 段 4：mock llm_client → run_llm_analysis → llm_daily_analysis 落库 ──
    db = tmp_path / "gov_e2e_b.db"
    result = run_llm_analysis(
        _DATE_B,
        llm_client=_llm_ok,
        ch_client=_ch_b_llm(),
        db_path=db,
        injected=_premarket_injections(datetime(2026, 8, 21, 15, 0)),
    )
    assert result.status == STATUS_SUCCESS
    assert result.db_logged is True and result.row_id > 0
    assert result.analysis is not None
    assert abs(sum(s.prob for s in result.analysis.scenarios.values()) - 1.0) <= 0.02
    assert result.input_hash == result.package.input_hash == pkg.input_hash  # 同源校验锚一致

    conn = sqlite3.connect(str(db))
    try:
        rows = conn.execute(
            "SELECT status, input_hash, model_version, prompt_version, output_json "
            "FROM llm_daily_analysis WHERE trade_date = ?",
            (_DATE_B,),
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 1
    status, input_hash, model_version, prompt_version, output_json = rows[0]
    assert status == STATUS_SUCCESS
    assert input_hash == result.input_hash
    assert model_version == DEFAULT_MODEL_VERSION  # 铁律② 冻结入库
    assert prompt_version == PROMPT_VERSION  # 铁律③ v1 单调用版本串
    assert "gap_up" in json.loads(output_json)["analysis"]["scenarios"]

    # 幂等：同输入重跑 → 同键跳过保首条（仍 1 行，row_id 复用）
    result2 = run_llm_analysis(
        _DATE_B,
        llm_client=_llm_ok,
        ch_client=_ch_b_llm(),
        db_path=db,
        injected=_premarket_injections(datetime(2026, 8, 21, 15, 0)),
    )
    assert result2.status == STATUS_SUCCESS and result2.row_id == result.row_id
    conn = sqlite3.connect(str(db))
    try:
        n = conn.execute("SELECT count(*) FROM llm_daily_analysis WHERE trade_date = ?", (_DATE_B,)).fetchone()[0]
    finally:
        conn.close()
    assert n == 1


# ══════════════════════════════════════════════════════════════
# 链 C：期指基差贴水急扩 → M2 降档
# ══════════════════════════════════════════════════════════════

_DATE_C = "2026-08-18"  # 周二


class _FuturesFakeCH:
    """鸭子类型 ch_client（clickhouse-driver execute(sql, params) 形态）。"""

    def __init__(self, spot_quote, fut_qmt, fut_daily, spot_daily, position):
        self._spot_quote = spot_quote
        self._fut_qmt = fut_qmt
        self._fut_daily = fut_daily
        self._spot_daily = spot_daily
        self._position = position

    def execute(self, sql, params=None):
        if "index_quote" in sql:
            return list(self._spot_quote)
        if "futures_kline_qmt" in sql:
            return list(self._fut_qmt)
        if "kline_futures" in sql:
            return list(self._fut_daily)
        if "kline_index" in sql:
            return list(self._spot_daily)
        if "futures_position" in sql:
            return list(self._position)
        if "calendar_event" in sql:
            return []
        return []


def _im_discount_client() -> _FuturesFakeCH:
    """IM 贴水急扩场景：常态小幅贴水波动（σ 小），今日期货盘中暴跌 → 基差 -1.5%。"""
    days: list[date] = []
    cur = date(2026, 8, 17)
    while len(days) < 21:
        if cur.weekday() < 5:
            days.append(cur)
        cur -= timedelta(days=1)
    days = sorted(days)
    spot_base = 7000.0
    fut_base = spot_base * 0.9985
    return _FuturesFakeCH(
        spot_quote=[("2026-08-18 13:59:57", spot_base)],
        fut_qmt=[("IM2609.CFFEX", spot_base * 0.985, 8000)],  # 盘中暴跌 → basis=-1.5%
        fut_daily=[(d, "IM2608", fut_base + (i % 3) * 0.5, 1000 + i) for i, d in enumerate(days)],
        spot_daily=[(d, spot_base) for d in days],
        position=[(days[-1], "IM2608", 10000, 9000)] * 6,
    )


def test_chain_c_futures_basis_to_downgrade(tmp_path):
    cfg = FuturesBasisConfig(products=(DEFAULT_PRODUCTS[2],))  # IM 单品种
    snap1 = compute_futures_basis(ts=f"{_DATE_C} 14:00:00", ch_client=_im_discount_client(), config=cfg)
    assert snap1.degraded is False
    im = snap1.per_symbol["IM"]
    assert im.discount_alert is True
    assert im.sigma_20d is not None and im.sigma_20d > 0
    assert im.basis_vel_30m < -1.5 * im.sigma_20d  # 贴水急扩超 1.5σ（M2 触发源④ 口径）

    # 14:45 复算快照（同一合成世界，第二个 ts —— 防抖时间序列）
    snap2 = compute_futures_basis(ts=f"{_DATE_C} 14:45:00", ch_client=_im_discount_client(), config=cfg)
    assert snap2.per_symbol["IM"].discount_alert is True

    store = InMemoryJsonStateStore()
    db = tmp_path / "gov_e2e_c.db"
    rev1 = evaluate_boundary_revision(
        _DATE_C,
        "14:00",
        futures_basis=snap1,
        state_store=store,
        eval_time="14:00",
        log_db_path=db,
    )
    assert rev1.revision_applied is False
    assert TRIGGER_IM_BASIS_DISCOUNT in rev1.pending_triggers  # 首现登记，防抖未满

    rev2 = evaluate_boundary_revision(
        _DATE_C,
        "14:45",
        futures_basis=snap2,
        state_store=store,
        eval_time="14:45",
        log_db_path=db,
    )
    assert rev2.revision_applied is True
    assert rev2.direction == "DOWNGRADE" and rev2.revised_tier == "CONSERVATIVE"
    assert rev2.triggers == [TRIGGER_IM_BASIS_DISCOUNT]
    assert rev2.debounce_proof[TRIGGER_IM_BASIS_DISCOUNT]["elapsed_min"] == 45
    assert rev2.logged is True
    rows = query_predictions(trade_date=_DATE_C, prediction_type="plan_revision", db_path=db)
    assert len(rows) == 1
    assert json.loads(rows[0]["payload_json"])["triggers"] == [TRIGGER_IM_BASIS_DISCOUNT]


# ══════════════════════════════════════════════════════════════
# 链 D：板块观测链（分歧度 → 龙头四档 → 主线榜 → 报告编排）
# ══════════════════════════════════════════════════════════════

_D0 = date(2026, 5, 4)
_N_D = 66  # 速度计分位窗最小样本 60 + lag 5 → ≥66 天
_DAYS_D = [_D0 + timedelta(days=i) for i in range(_N_D)]
_END_D = _DAYS_D[-1]
_MKT = "880001.SH"
_S880 = [f"8805{i:02d}.SH" for i in range(1, 9)]


def _closes_const(n: int, daily: float, start: float = 100.0) -> list[float]:
    out = [start]
    for _ in range(1, n):
        out.append(out[-1] * (1 + daily))
    return out


def _closes_accel(n: int, base: float, accel: float, start: float = 100.0) -> list[float]:
    out = [start]
    for i in range(1, n):
        out.append(out[-1] * (1 + base + accel * i))
    return out


def _closes_shuffle(base: float, si: int, up: bool, start: float = 100.0) -> list[float]:
    """非领涨板块收盘序列：历史段日收益在 base 上叠加 (i+si)%3 振荡（排名逐日洗牌，
    速度计分位窗有变异）；末 6 日固定 base（今日速度=0，分位低，非电风扇）。"""
    out = [start]
    for i in range(1, _N_D):
        r = base if i >= _N_D - 6 else base + (0.002 * ((i + si) % 3) if up else -0.002 * ((i + si) % 3))
        out.append(out[-1] * (1 + r))
    return out


# 板块宇宙：880501 每日加速领涨（贯穿全窗主线），其余板块历史段排名洗牌/末段定序；
# 成交额轻波动（HHI 低分散）
_SECTOR_CLOSES = {
    _MKT: [100.0] * _N_D,
    "880501.SH": _closes_accel(_N_D, 0.03, 0.0003),
    "880502.SH": _closes_shuffle(0.002, 1, True),
    "880503.SH": _closes_shuffle(0.001, 2, True),
    "880504.SH": _closes_shuffle(0.0005, 3, True),
    "880505.SH": _closes_shuffle(-0.001, 4, False),
    "880506.SH": _closes_shuffle(-0.002, 5, False),
    "880507.SH": _closes_shuffle(-0.003, 6, False),
    "880508.SH": _closes_shuffle(-0.004, 7, False),
}
_SECTOR_AMOUNTS = {code: [10.0 + ((i + si) % 3) for i in range(_N_D)] for si, code in enumerate([_MKT] + _S880)}

# 个股宇宙（板块归属 / 趋势起点 / 日步长 / 末日涨幅% / 末尾连板封板天数 / 当日成交额）
# 注：成交额与板块 K 线 amount 同量级（~10）——881xxx 合成板块成交额=成分合计，
# 量级悬殊会把 mainline 宇宙的 HHI 顶高、5 状态误判集中（板块合成口径跨模块契约点）。
_STOCK_SPECS = {
    "STK_C1.SH": ("880501.SH", 10.0, 0.05, 10.0, 3, 5.0),  # 3 连板龙头
    "STK_C2.SH": ("880501.SH", 10.0, 0.08, 1.5, 0, 10.0),  # 大成交额中军
    "STK_A1.SH": ("881386.SH", 10.0, 0.03, 10.0, 2, 5.0),  # 2 连板龙头（防御族板块）
    "STK_A2.SH": ("881386.SH", 10.0, 0.04, 1.0, 0, 8.0),  # 中军
    "STK_A3.SH": ("881386.SH", 13.0, -0.05, 2.0, 0, 1.0),  # 红盘跟风
    "STK_B1.SH": ("881394.SH", 13.0, -0.03, -3.0, 0, 5.0),  # 无特征 neutral
    "STK_B2.SH": ("881394.SH", 12.0, -0.04, -1.0, 0, 4.0),  # neutral
    "STK_D1.SH": ("880502.SH", 10.0, 0.0, 0.5, 0, 15.0),  # 无龙头板块跟风
}
_SECTOR_NAMES = {"881386.SH": "银行", "881394.SH": "券商", "880501.SH": "机器人", "880502.SH": "磷化工"}


def _stock_master(sym: str) -> tuple[list[float], list[float]]:
    """单股收盘/日涨幅%序列（末尾 sealed_tail 日每日 +10% 封板；末日涨幅=today_pct）。"""
    _sector, start, step, today_pct, sealed_tail, _amt = _STOCK_SPECS[sym]
    closes = [start + step * i for i in range(_N_D)]
    if sealed_tail > 0:
        for j in range(_N_D - sealed_tail, _N_D):
            closes[j] = closes[j - 1] * 1.10
    else:
        closes[-1] = closes[-2] * (1.0 + today_pct / 100.0)
    pcts = [0.0] + [(closes[i] / closes[i - 1] - 1.0) * 100.0 for i in range(1, _N_D)]
    return closes, pcts


class _SectorWorldCH:
    """板块观测链复合 mock CH：同一合成世界喂四个模块（按 SQL 列形/表名路由）。"""

    def __init__(self) -> None:
        self._sector_rows = [
            (code, d, _SECTOR_CLOSES[code][i], _SECTOR_AMOUNTS[code][i])
            for code in [_MKT] + _S880
            for i, d in enumerate(_DAYS_D)
        ]
        self._cons2 = [(sector, sym) for sym, (sector, *_r) in _STOCK_SPECS.items()]
        self._cons3 = [(sector, _SECTOR_NAMES[sector], sym) for sym, (sector, *_r) in _STOCK_SPECS.items()]
        self._meta = [("881386", "银行"), ("881394", "券商")]
        self._rows7: list[tuple] = []  # divergence 个股 K 线（high/low/close/turnover/pct）
        self._rows_leader: list[tuple] = []  # leader 个股 K 线（close/amount/turnover）
        self._rows_pct: list[tuple] = []  # mainline/report 个股 K 线（close/amount/pct）
        self._stk3: list[tuple] = []  # leader 涨跌停价窗（sym/date/limit_up）
        self._stk2: list[tuple] = []  # divergence/report 当日涨跌停价（sym/limit_up）
        for sym in _STOCK_SPECS:
            closes, pcts = _stock_master(sym)
            amt_today = _STOCK_SPECS[sym][5]
            sealed_from = _N_D - _STOCK_SPECS[sym][4]
            for i, d in enumerate(_DAYS_D):
                c = closes[i]
                self._rows7.append((sym, d, c * 1.01, c * 0.99, c, 1.0, pcts[i]))
                self._rows_leader.append((sym, d, c, amt_today if i == _N_D - 1 else amt_today * 0.5, 3.0))
                self._rows_pct.append((sym, d, c, amt_today, pcts[i]))
                limit = c if i >= sealed_from else c * 1.1
                self._stk3.append((sym, d, limit))
            self._stk2.append((sym, closes[-1] if _STOCK_SPECS[sym][4] > 0 else closes[-1] * 1.1))
        self._mf_today = [(sym, 1e4, 5e3, 2e3, 0.0, 0.0) for sym in _STOCK_SPECS]
        self._mf_window = [
            (d, sym, 1e3 if (i + si) % 2 == 0 else -1e3)
            for i, d in enumerate(_DAYS_D[-10:])
            for si, sym in enumerate(_STOCK_SPECS)
        ]
        self._limit_rows = [
            ("STK_C1.SH", _DAYS_D[-2], "涨停"),
            ("STK_C1.SH", _DAYS_D[-1], "涨停"),
            ("STK_A1.SH", _DAYS_D[-1], "涨停"),
        ]
        self._snapshot = [
            (
                "880501.SH",
                _SECTOR_CLOSES["880501.SH"][-1],
                _SECTOR_CLOSES["880501.SH"][-2],
                500.0,
                20.0,
                11.0,
                9.0,
                _END_D,
            ),
            (
                "880502.SH",
                _SECTOR_CLOSES["880502.SH"][-1],
                _SECTOR_CLOSES["880502.SH"][-2],
                490.0,
                30.0,
                15.0,
                15.0,
                _END_D,
            ),
            (
                "880503.SH",
                _SECTOR_CLOSES["880503.SH"][-1],
                _SECTOR_CLOSES["880503.SH"][-2],
                480.0,
                10.0,
                6.0,
                4.0,
                _END_D,
            ),
        ]
        self._breadth = [(_DAYS_D[-2], 40, 100), (_DAYS_D[-1], 60, 100)]

    def execute(self, sql, params=None):
        if "sector_snapshot" in sql:
            return list(self._snapshot)
        if "sector_meta" in sql:
            return list(self._meta)
        if "sector_constituent" in sql:
            return list(self._cons3) if "sector_name" in sql else list(self._cons2)
        if "dragon_tiger_seat" in sql:
            return []
        if "limit_up_down" in sql:
            return list(self._limit_rows)
        if "stk_limit" in sql:
            return list(self._stk3) if "trade_date, limit_up" in sql else list(self._stk2)
        if "money_flow" in sql:
            return list(self._mf_today) if "super_large" in sql else list(self._mf_window)
        if "kline_sector_880" in sql:
            if "max(trade_date)" in sql:
                return [(_END_D,)]
            return list(self._sector_rows)
        if "kline_daily" in sql:
            if "countIf(pct_change" in sql:
                return list(self._breadth)
            if "max(trade_date)" in sql:
                return [(_END_D,)]
            if "high, low" in sql:
                return list(self._rows7)
            if "turnover" in sql:
                return list(self._rows_leader)
            return list(self._rows_pct)
        return []


def test_chain_d_sector_observation_chain():
    broker = _SectorWorldCH()

    # ── 环 1：板块分歧度（5 状态+速度计+SEC-03 标定+rs 雷达）──
    div = compute_sector_divergence(_END_D, ch_client=broker)
    assert div.degraded is False
    assert div.rotation_state == "HEALTHY_MAINLINE"
    assert div.top_risk_flag is False
    assert div.lead_streak is not None and div.lead_streak >= 3
    assert div.rotation_velocity == pytest.approx(0.0)  # 末 6 日排名定序 → 今日速度 0
    assert div.velocity_percentile is not None and div.velocity_percentile < 0.75  # 66 日窗 ≥60 且非电风扇
    assert div.fan_market_flag is False and div.no_mainline_flag is False
    assert div.state_conditional_stats  # SEC-03 标定出统计
    assert div.current_state_summary and "当前状态=" in div.current_state_summary
    assert div.rs_ratio is not None and div.rs_z is not None  # 族相对强度雷达（真实标签 yaml）

    # ── 环 2：龙头四档（连板高度 × 成交额 × 涨幅推导）──
    board = identify_sector_leaders(trade_date=_END_D, ch_client=broker)
    assert board.degraded is False
    assert board.n_stocks == len(_STOCK_SPECS)
    groups = {g.sector_code: g for g in board.sectors}
    g501 = groups["880501.SH"]
    assert g501.leader is not None and g501.leader.symbol == "STK_C1.SH"
    assert g501.leader.consec_limit == 3
    assert [b.symbol for b in g501.backbones] == ["STK_C2.SH"]
    g381 = groups["881386.SH"]
    assert g381.leader is not None and g381.leader.symbol == "STK_A1.SH"
    assert g381.leader.consec_limit == 2
    g502 = groups["880502.SH"]
    assert g502.leader is None and g502.annotation is not None and "无龙头板块" in g502.annotation

    # ── 环 3：主线候选榜（HEALTHY_MAINLINE 领涨+q3 前排+RRG）──
    ml = compute_mainline_candidates(trade_date=_END_D, ch_client=broker)
    assert ml.degraded is False
    assert ml.rotation_state == "HEALTHY_MAINLINE"
    assert ml.leader_code == "880501.SH"
    assert ml.no_mainline_flag is False
    assert ml.candidates
    assert "880501.SH" in {c.sector_code for c in ml.candidates}

    # ── 环 4：盘后报告编排（MOD-L00-009，内嵌 SEC-05 主线）──
    report = build_sector_report(_END_D, ch_client=broker)
    assert report.degraded is False
    assert report.top_sectors and report.top_sectors[0].sector_code == "880501.SH"
    assert report.top_sectors[0].rank == 1
    assert report.rotation_state == "HEALTHY_MAINLINE"
    assert report.limit_ladder is not None
    assert report.limit_ladder.total_limit_up == 2  # C1（二板）+A1（首板）
    assert report.limit_ladder.max_streak == 2
    assert report.mainline is not None and report.mainline.candidates  # 主线键嵌入
    assert {"top_ladder", "money_flow", "rotation_state", "limit_ladder", "siphon", "mainline"} <= set(
        report.availability
    )
    payload = report_to_dict(report)
    json.dumps(payload, ensure_ascii=False)  # JSON 可序列化契约
    assert payload["mainline"]["candidates"]


# ══════════════════════════════════════════════════════════════
# 链 E：校准闭环（prediction_log 播种 → 命中率统计 → 触发评审）
# ══════════════════════════════════════════════════════════════


def test_chain_e_calibration_closed_loop(tmp_path):
    db = tmp_path / "gov_e2e_e.db"
    ensure_prediction_log_table(db)
    module = "plan_engine.boundary_revision_engine"
    today = date.today()
    start = today - timedelta(days=29)  # 30 个连续自然日（全在 60 日默认窗内）

    for i in range(30):
        d = (start + timedelta(days=i)).isoformat()
        log_prediction(
            trade_date=d,
            module=module,
            prediction_type="plan_revision",
            payload={"day": d, "revised_tier": "CONSERVATIVE", "direction": "DOWNGRADE"},
            asof_ts=f"{d}T14:45:00+08:00",
            db_path=db,
        )
        record_outcome(
            d,
            module,
            {"hit": (i % 5) < 2, "note": f"e2e-{i}"},  # 12/30 = 命中率 0.4
            asof_ts=f"{d}T18:00:00+08:00",
            db_path=db,
        )

    stats = compute_hit_rate_stats(module, db_path=db)
    assert stats.prediction_count == 30
    assert stats.sample_size == 30
    assert stats.hit_rate == pytest.approx(0.4)
    assert stats.trend == "stable"

    work_dir = tmp_path / "calibration_review"
    verdict = evaluate_calibration_trigger(module, stats=stats, db_path=db, runtime_dir=work_dir)
    assert verdict.triggered is True  # 命中率 0.4 < 0.55 且样本 30 ≥ 30
    assert verdict.reason == "below_threshold"
    assert "G04" in verdict.suggested_action
    assert Path(verdict.evidence["work_order_path"]).is_file()
    assert work_dir.exists()

    trig_rows = query_predictions(module=module, prediction_type="calibration_trigger", db_path=db)
    assert len(trig_rows) == 1
    trig_payload = json.loads(trig_rows[0]["payload_json"])
    assert trig_payload["reason"] == "below_threshold"
    assert trig_payload["hit_rate"] == pytest.approx(0.4)
    assert trig_payload["sample_size"] == 30


# ══════════════════════════════════════════════════════════════
# 链 F：快照采集 → 盘中情绪回路 → 落库
# ══════════════════════════════════════════════════════════════

_TD_F = date(2026, 8, 21)


def _tick(last: float, pre: float, *, high=None, amount=1e8, ask_p=None, ask_v=None) -> dict:
    """合成一条 get_full_tick tick dict（键名=provider 实证口径）。"""
    return {
        "lastPrice": last,
        "lastClose": pre,
        "high": high if high is not None else last,
        "amount": amount,
        "askPrice": ask_p if ask_p is not None else [last, 0, 0, 0, 0],
        "askVol": ask_v if ask_v is not None else [100, 0, 0, 0, 0],
    }


def _minute_ticks(m: int) -> dict:
    """第 m 分钟全市场 tick：上涨 59+m / 下跌 40-m / 平 5；3 只主板封板 + 1 只 ST 涨停未封 + 2 无效。"""
    ticks: dict[str, dict] = {}
    for i in range(55 + m):
        ticks[f"600{i:03d}.SH"] = _tick(10.10, 10.00)  # 涨
    for i in range(55 + m, 95):
        ticks[f"600{i:03d}.SH"] = _tick(9.90, 10.00)  # 跌
    for i in range(95, 100):
        ticks[f"600{i:03d}.SH"] = _tick(10.00, 10.00)  # 平
    for k in range(3):
        ticks[f"6001{k:02d}.SH"] = _tick(11.00, 10.00, ask_p=[0.0], ask_v=[0])  # 主板涨停且卖一无量=封住
    ticks["600199.SH"] = _tick(10.50, 10.00, ask_p=[10.50], ask_v=[100])  # ST 5% 涨停但有卖单=未封
    ticks["600200.SH"] = {"lastPrice": 0.0, "lastClose": 10.0}  # 无效（最新价≤0）
    ticks["600201.SH"] = {"lastPrice": 10.1}  # 无效（缺昨收）
    return ticks


class _LoopFakeCH:
    """盘中回路 mock CH（breadth 回读行/sector_snapshot/index 两腿）。"""

    def __init__(self, breadth_rows, sector_rows):
        self._breadth = breadth_rows
        self._sector = sector_rows

    def execute(self, sql, params=None):
        if "market_breadth_snapshot" in sql:
            return list(self._breadth)
        if "sector_snapshot" in sql:
            return list(self._sector)
        if "index_quote" in sql:
            return [(3950.0, datetime(2026, 8, 21, 9, 36))]
        if "kline_index" in sql:
            return [(3900.0,)]
        return []


def test_chain_f_breadth_collect_to_loop(tmp_path):
    # ── 环 1：全市场 tick 聚合（MOD-DATA-062 纯函数）──
    aggs = []
    for m in range(6):
        agg = aggregate_market_ticks(_minute_ticks(m), {"600199"}, trade_date=_TD_F)
        assert agg.total_count == 104
        assert agg.advancing == 59 + m
        assert agg.declining == 40 - m
        assert agg.flat == 5
        assert agg.limit_up == 4  # 3 主板 + 1 ST
        assert agg.sealed == 3  # ST 有卖单未封
        assert agg.attempted == 4
        assert agg.limit_down == 0
        assert agg.n_skipped == 2
        assert agg.total_amount == pytest.approx(104 * 1e8)
        aggs.append(agg)

    # ── 环 2：落库行契约（build_insert_row 列序=schemas INSERT_COLUMNS 真源）──
    readback_rows: list[tuple] = []
    for m, agg in enumerate(aggs):
        ts_dt = datetime(2026, 8, 21, 9, 31 + m)
        row13 = build_insert_row(agg, "2026-08-21", ts_dt.strftime("%Y-%m-%d %H:%M:%S"))
        assert len(row13) == len(INSERT_COLUMN_NAMES) == 13
        assert row13[2] == 59 + m and row13[5] == 4  # advancing / limit_up 列位
        # 模拟 CH 写后回读：INSERT 列序 → SQL_BREADTH_LATEST_DAY 查询列序
        readback_rows.append(
            (ts_dt, row13[2], row13[3], row13[4], row13[5], row13[6], row13[7], row13[8], row13[9], row13[10], row13[0])
        )

    # ── 环 3：盘中情绪回路单拍（MOD-DATA-063，time_series 装配+SEC-02 挂接+落库）──
    sector_rows = [
        ("880301.SH", datetime(2026, 8, 21, 9, 35), 100.0, 99.0, 1e6, 10, 5, 0, 0, 0.5, 100.0, "sector", _TD_F),
        ("880301.SH", datetime(2026, 8, 21, 9, 36), 101.0, 99.0, 2e6, 12, 4, 0, 0, 0.8, 100.5, "sector", _TD_F),
    ]
    db = tmp_path / "gov_e2e_f.db"
    ensure_prediction_log_table(db)
    result = run_once(ch_client=_LoopFakeCH(readback_rows, sector_rows), db_path=str(db))

    assert result.degraded is False
    assert result.trade_date == "2026-08-21"
    assert result.n_snapshots == 6
    assert result.total_count == 104
    assert result.sentiment is not None
    assert 0.0 <= result.sentiment.overall_score <= 100.0
    accel = result.sentiment.breadth_acceleration
    assert accel is not None  # time_series 装配激活 M1-①
    assert accel.breadth_vel_5m == pytest.approx((64 - 59) / 104)
    assert result.sector_board is not None and result.sector_board.n_sectors == 1
    assert result.prediction_log_id is not None and result.prediction_log_id > 0

    rows = query_predictions(trade_date="2026-08-21", module="zephyr.data.intraday_sentiment_loop", db_path=str(db))
    assert len(rows) == 1
    assert rows[0]["prediction_type"] == "sentiment_score"
    payload = json.loads(rows[0]["payload_json"])
    assert payload["time_series_minutes"] == 6
    assert payload["snapshot"]["advancing"] == 64
    assert payload["snapshot"]["limit_up"] == 4
    assert payload["snapshot"]["sealed"] == 3
    assert "sector_board" in payload  # SEC-02 榜面摘要注解同载体
