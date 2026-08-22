"""LlmPremarketAnalysis (MOD-PLAN-007) 施工验证测试（92号清单 §8.6 / 44号 §9.14 M3-⑨）。

全 mock（ch_client/llm_client 注入，离线可跑）：
- 打包器 PIT 铁律①：cutoff 后数据点拒绝入包（CH 行日期越界 / 注入契约 ts 越界）+ rejected 留痕；
  cutoff 前注入准入；自定义 asof_cutoff 生效
- 七族载荷正确性：指数（涨跌幅/振幅/成交额 vs 20 日均量）/ 情绪（涨跌家数/炸板率/封板率/
  昨日涨停今表现/M1 分注入）/ 板块（领涨领跌 Top5/资金净额 Top5/5 状态注入）/ 衍生（IF/IM
  基差+PCR/IV Rank 注入）/ 外盘（SPX/NDX 隔夜+BS-005）/ 资金（两融Δ/主力净流入/大宗折溢价/
  龙虎榜注入）/ 日历（昨日命中+今日预告）
- input_hash 稳定性（同输入同 hash，built_at/rejected 不进哈希）与敏感性（单字段变化→hash 变）
- 输出契约 schema：缺字段拒收 / 概率和偏离 1 超容差拒收 / prob 越界 / date 不符 / 回显不一致
- mock llm_client 端到端：v1 单调用 / v2 多空辩论三调用编排（多/空/综合席 prompt 标记断言，
  计量合计）/ 调用异常标 invalid 不炸
- 落库幂等：UNIQUE(trade_date, model_version, prompt_version, input_hash) 同键重跑保首条
- llm_client=None → status=skipped_not_wired 落库留痕不炸
"""

from __future__ import annotations

import datetime
import json
import sqlite3

import pytest

from zephyr.plan_engine.llm_premarket_analysis import (
    PROMPT_VERSION,
    STATUS_INVALID,
    STATUS_SKIPPED_NOT_WIRED,
    STATUS_SUCCESS,
    LlmPremarketConfig,
    PremarketInjections,
    build_premarket_package,
    build_user_prompt,
    ensure_llm_daily_analysis_table,
    parse_llm_output,
    run_llm_analysis,
)
from zephyr.signal_ashare.futures_basis_monitor import FuturesBasisSnapshot, FuturesBasisSymbol
from zephyr.signal_ashare.lhb_premium_analyzer import LhbPremiumResult
from zephyr.signal_ashare.market_sentiment_analyzer import MarketSentimentResult
from zephyr.signal_ashare.option_sentiment import OptionSentimentResult
from zephyr.signal_ashare.sector_divergence import SectorDivergenceResult

TRADE_DATE = "2026-08-24"  # 周一
T1 = "2026-08-21"  # T-1（周五）
T2 = "2026-08-20"  # T-2


# ══════════════════════════════════════════════════════════════
# mock CH 数据构造（路由式假客户端：按 SQL 标记分派 TSV）
# ══════════════════════════════════════════════════════════════


def _tsv(rows: list[tuple]) -> str:
    return "\n".join("\t".join(str(c) for c in row) for row in rows)


def _index_tsv() -> str:
    """四指数 22 日行（000001：T-1 收 3860/高 3880/低 3840/额 5000，历史收 3840→3800 额 4000）。"""
    days = [T1, T2] + [f"2026-08-{d:02d}" for d in range(19, 0, -1)] + ["2026-07-31"]
    rows: list[tuple] = []
    for sym, name in (("000001", "上证指数"), ("399001", "深证成指"), ("399006", "创业板指"), ("000688", "科创50")):
        for i, d in enumerate(days):
            if sym == "000001":
                close = {0: 3860.0, 1: 3840.0}.get(i, 3800.0)
                high, low = (3880.0, 3840.0) if i == 0 else (close + 10.0, close - 10.0)
                amt = 5000.0 if i == 0 else 4000.0
            else:
                close, high, low, amt = 1000.0, 1010.0, 990.0, 2000.0
            rows.append((sym, name, d, close, high, low, close, amt, 100))
    return _tsv(rows)


def _sector_kline_tsv() -> str:
    """板块 T-1/T-2 收盘（880004 +3% / 880007 +2% / 880002 +1% / 880006 +0.5% / 880005 -2% / 880003 -5%）。"""
    base = {
        "880002": (1000.0, 1010.0),
        "880003": (1000.0, 950.0),
        "880004": (1000.0, 1030.0),
        "880005": (1000.0, 980.0),
        "880006": (1000.0, 1005.0),
        "880007": (1000.0, 1020.0),
    }
    rows = [(code, T2, c2) for code, (c2, _c1) in base.items()]
    rows += [(code, T1, c1) for code, (_c2, c1) in base.items()]
    return _tsv(rows)


def _make_ch(
    *,
    prev_dates: str | None = None,
    index: str | None = None,
    breadth: str | None = None,
    limit_stats: str | None = None,
    limit_up_symbols: str | None = None,
    next_perf: str | None = None,
    sector_names: str | None = None,
    sector_kline: str | None = None,
    money_flow_day: str | None = None,
    constituents: str | None = None,
    us_index: str | None = None,
    margin: str | None = None,
    money_flow_agg: str | None = None,
    block_trade: str | None = None,
    calendar: str | None = None,
):
    """路由式假 CH 客户端（None=用默认夹具；空串=该通道无数据）。"""
    data = {
        "prev_dates": prev_dates if prev_dates is not None else _tsv([(T1,), (T2,)]),
        "index": index if index is not None else _index_tsv(),
        "breadth": breadth if breadth is not None else _tsv([("3000", "1800", "200")]),
        "limit_stats": limit_stats if limit_stats is not None else _tsv([("45", "60", "12")]),
        "limit_up_symbols": limit_up_symbols
        if limit_up_symbols is not None
        else _tsv([("600000.SH",), ("000001.SZ",)]),
        "next_perf": next_perf if next_perf is not None else _tsv([("600000.SH", "5.0"), ("000001.SZ", "-2.0")]),
        "sector_names": sector_names
        if sector_names is not None
        else _tsv([("880002", "半导体"), ("880003", "医药"), ("880004", "券商")]),
        "sector_kline": sector_kline if sector_kline is not None else _sector_kline_tsv(),
        "money_flow_day": money_flow_day
        if money_flow_day is not None
        else _tsv([("600000.SH", "20000"), ("000001.SZ", "50000")]),
        "constituents": constituents
        if constituents is not None
        else _tsv([("880004", "600000.SH"), ("880004", "000001.SZ")]),
        "us_index": us_index
        if us_index is not None
        else _tsv([(T1, "SPX", "6500"), (T2, "SPX", "6450"), (T1, "IXIC", "21000"), (T2, "IXIC", "20800")]),
        "margin": margin if margin is not None else _tsv([(T1, "150"), (T2, "120"), ("2026-08-19", "100")]),
        "money_flow_agg": money_flow_agg if money_flow_agg is not None else _tsv([(T1, "-800000", "-0.35")]),
        "block_trade": block_trade if block_trade is not None else _tsv([(T1, "-0.062")]),
        "calendar": calendar
        if calendar is not None
        else _tsv([(T1, "futures_delivery"), (TRADE_DATE, "option_expiry")]),
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
        raise AssertionError(f"未路由的 SQL: {sql[:120]}")

    return _ch


# ══════════════════════════════════════════════════════════════
# 注入契约构造（真实 dataclass，MOD-SIG-025/057/058/059/060 输出）
# ══════════════════════════════════════════════════════════════


def _futures_snapshot(ts: str) -> FuturesBasisSnapshot:
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

    return FuturesBasisSnapshot(
        ts=ts,
        trade_date=T1,
        per_symbol={"IF": _sym("IF", -0.002), "IM": _sym("IM", -0.008)},
        delivery_week=False,
    )


def _option_sentiment(date: str = T1) -> OptionSentimentResult:
    return OptionSentimentResult(
        date=date, pcr=0.85, pcr_percentile=0.6, iv_rank=0.45, skew_norm=0.08, skew_extreme=False
    )


def _sector_divergence(date: str = T1) -> SectorDivergenceResult:
    return SectorDivergenceResult(
        date=date,
        rotation_state="ROTATION",
        siphon_z=0.8,
        siphon_flag=False,
        rotation_velocity=3.2,
        velocity_percentile=0.4,
        fan_market_flag=False,
        top_risk_flag=False,
    )


def _sentiment_result(ts: datetime.datetime) -> MarketSentimentResult:
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


def _lhb_result(date: str = T1) -> LhbPremiumResult:
    return LhbPremiumResult(
        date=date,
        high_open_candidates=["600000.SH"],
        low_open_risks=["000001.SZ"],
        fanhe_watchlist=["300750.SZ"],
    )


def _full_injected() -> PremarketInjections:
    return PremarketInjections(
        sentiment_result=_sentiment_result(datetime.datetime(2026, 8, 21, 15, 0)),
        sector_divergence=_sector_divergence(),
        futures_snapshot=_futures_snapshot(f"{T1} 15:00:00"),
        option_sentiment=_option_sentiment(),
        lhb_result=_lhb_result(),
        bs005_triggered=False,
    )


def _valid_llm_json(trade_date: str = TRADE_DATE, **overrides) -> str:
    obj = {
        "date": trade_date,
        "scenarios": {
            "gap_up": {"prob": 0.25, "key_levels": ["上证 3860"], "action_boundary": "高开不追仓"},
            "flat": {"prob": 0.50, "key_levels": ["上证 3840"], "action_boundary": "按昨夜边界执行"},
            "gap_down": {"prob": 0.25, "key_levels": ["上证 3800"], "action_boundary": "企稳前禁新开仓"},
        },
        "risk_points": ["外围波动"],
        "watch_sectors": ["券商"],
        "confidence_note": "数据齐",
    }
    obj.update(overrides)
    return json.dumps(obj, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════
# 打包器：七族载荷正确性
# ══════════════════════════════════════════════════════════════


def test_package_seven_families_payload():
    pkg = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), injected=_full_injected())
    assert pkg.trade_date == TRADE_DATE
    assert pkg.asof_cutoff == f"{TRADE_DATE} 08:00:00"
    assert set(pkg.families) == {"index", "sentiment", "sector", "derivatives", "overseas", "capital", "calendar"}
    assert pkg.rejected == []

    # 指数族：涨跌幅/振幅/成交额 vs 20 日均量
    idx0 = next(i for i in pkg.families["index"]["items"] if i["symbol"] == "000001")
    assert idx0["date"] == T1
    assert idx0["pct_change"] == pytest.approx((3860 - 3840) / 3840)
    assert idx0["amplitude"] == pytest.approx((3880 - 3840) / 3840)
    assert idx0["turnover_vs_20d"] == pytest.approx(5000 / 4000)

    # 情绪族：涨跌家数/涨跌停/炸板率/封板率/昨日涨停今表现/M1 注入
    s = pkg.families["sentiment"]
    assert (s["advance_count"], s["decline_count"], s["flat_count"]) == (3000, 1800, 200)
    assert s["limit_up_count"] == 45 and s["limit_down_count"] == 12 and s["attempted_up_count"] == 60
    assert s["seal_rate"] == pytest.approx(0.75)
    assert s["break_rate"] == pytest.approx(0.25)
    assert s["yesterday_limit_up_perf"]["count"] == 2
    assert s["yesterday_limit_up_perf"]["avg_pct_change"] == pytest.approx(1.5)
    assert s["m1_overall_score"] == 58.0 and s["m1_phase"] == "主升"

    # 板块族：领涨领跌 Top5/资金净额 Top5/5 状态注入
    sec = pkg.families["sector"]
    assert [g["sector_code"] for g in sec["top_gainers"][:3]] == ["880004", "880007", "880002"]
    assert sec["top_gainers"][0]["name"] == "券商"
    assert [l["sector_code"] for l in sec["top_losers"][:2]] == ["880003", "880005"]
    assert sec["sector_money_flow_top"][0]["sector_code"] == "880004"
    assert sec["sector_money_flow_top"][0]["net_inflow_yi"] == pytest.approx(7.0)  # 70000万→7亿
    assert sec["rotation_state"] == "ROTATION" and sec["siphon_z"] == 0.8
    assert sec["velocity_percentile"] == 0.4 and sec["fan_market_flag"] is False

    # 衍生族：IF/IM 基差+贴水速率 + 期权 PCR/IV Rank
    d = pkg.families["derivatives"]
    assert d["if_basis_rate"] == -0.002 and d["im_basis_rate"] == -0.008
    assert d["if_basis_vel_30m"] == -0.0005
    assert d["option_pcr"] == 0.85 and d["option_iv_rank"] == 0.45
    assert d["futures_delivery_week"] is False

    # 外盘族：SPX/NDX 隔夜 + BS-005 注入 + 缺口占位
    o = pkg.families["overseas"]
    assert o["spx"]["pct_change"] == pytest.approx((6500 - 6450) / 6450)
    assert o["ndx"]["pct_change"] == pytest.approx((21000 - 20800) / 20800)
    assert o["bs005_triggered"] is False
    assert o["a50_night"] is None and o["es_nq_intraday"] is None

    # 资金族：两融Δ/主力净流入/大宗折溢价/龙虎榜注入
    c = pkg.families["capital"]
    assert c["margin"]["net_buy"] == 150.0
    assert c["margin"]["delta_vs_prev"] == pytest.approx(30.0)
    assert c["margin"]["avg_20d"] == pytest.approx(110.0)
    assert c["main_force"]["net_inflow"] == -800000.0
    assert c["block_trade"]["premium_rate"] == pytest.approx(-0.062)
    assert c["lhb"]["high_open_candidates"] == ["600000.SH"]

    # 日历族：昨日命中 + 今日预告
    cal = pkg.families["calendar"]
    assert [e["event_type"] for e in cal["yesterday_hits"]] == ["futures_delivery"]
    assert [e["event_type"] for e in cal["today_preview"]] == ["option_expiry"]

    # 全包 JSON 可序列化
    json.dumps(pkg.to_dict(), ensure_ascii=False)


def test_package_empty_ch_degrades_not_raises():
    pkg = build_premarket_package(TRADE_DATE, ch_client=lambda sql: "")
    assert pkg.families["index"]["status"] == "degraded:no_data"
    assert pkg.families["sentiment"]["status"] == "degraded:no_prev_date"
    assert pkg.families["derivatives"]["status"] == "not_injected"
    assert pkg.families["calendar"]["status"] == "degraded:no_data"
    assert len(pkg.input_hash) == 64


def test_package_ch_channel_exception_degrades():
    def _boom(sql: str) -> str:
        raise RuntimeError("ch down")

    pkg = build_premarket_package(TRADE_DATE, ch_client=_boom, injected=_full_injected())
    assert pkg.families["index"]["status"] == "degraded:no_data"
    # 注入族不依赖 CH，仍准入
    assert pkg.families["derivatives"]["if_basis_rate"] == -0.002
    assert pkg.families["sentiment"]["m1_overall_score"] == 58.0


# ══════════════════════════════════════════════════════════════
# 打包器：PIT 铁律①（cutoff 后数据拒绝入包 + rejected 留痕）
# ══════════════════════════════════════════════════════════════


def test_pit_ch_row_after_cutoff_rejected():
    """CH 行日期 ≥ trade_date（SQL 护栏穿透的兜底）：拒入 + rejected 留痕，序列用合规行计算。"""
    us = _tsv([(TRADE_DATE, "SPX", "6600"), (T1, "SPX", "6500"), (T2, "SPX", "6450")])
    pkg = build_premarket_package(TRADE_DATE, ch_client=_make_ch(us_index=us))
    # 越界行（T 日美股收盘，北京 T+1 凌晨才可见）被拒，SPX 仍按 T-1/T-2 计算
    assert pkg.families["overseas"]["spx"]["pct_change"] == pytest.approx((6500 - 6450) / 6450)
    assert pkg.families["overseas"]["spx"]["date"] == T1
    hits = [r for r in pkg.rejected if r["family"] == "overseas" and r["asof"] == TRADE_DATE]
    assert len(hits) == 1 and "trade_date" in hits[0]["reason"]


def test_pit_injected_futures_ts_after_cutoff_rejected():
    """注入期指快照 ts > cutoff（如 T 日 09:30 盘中值）：整块拒入，族字段 None。"""
    inj = PremarketInjections(futures_snapshot=_futures_snapshot(f"{TRADE_DATE} 09:30:00"))
    pkg = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), injected=inj)
    d = pkg.families["derivatives"]
    assert d["if_basis_rate"] is None and d["im_basis_rate"] is None
    assert d["status"] == "degraded:pit_rejected"
    hits = [r for r in pkg.rejected if r["family"] == "derivatives" and r["field"] == "futures_snapshot"]
    assert len(hits) == 1 and "cutoff" in hits[0]["reason"]


def test_pit_injected_date_precision_same_day_rejected():
    """日频精度注入（期权/龙虎榜/板块分歧度）date == trade_date：T 日数据 08:00 不可得 → 拒入。"""
    inj = PremarketInjections(
        option_sentiment=_option_sentiment(date=TRADE_DATE),
        lhb_result=_lhb_result(date=TRADE_DATE),
        sector_divergence=_sector_divergence(date=TRADE_DATE),
    )
    pkg = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), injected=inj)
    assert pkg.families["derivatives"]["option_pcr"] is None
    assert pkg.families["capital"]["lhb"] is None
    assert pkg.families["sector"]["rotation_state"] is None
    rejected_fields = {(r["family"], r["field"]) for r in pkg.rejected}
    assert ("derivatives", "option_sentiment") in rejected_fields
    assert ("capital", "lhb_result") in rejected_fields
    assert ("sector", "sector_divergence") in rejected_fields


def test_pit_injected_sentiment_before_cutoff_admitted():
    """M1 情绪分 timestamp = T-1 15:00（收盘后）≤ cutoff → 准入；T 日 09:00 → 拒入。"""
    ok = build_premarket_package(
        TRADE_DATE,
        ch_client=_make_ch(),
        injected=PremarketInjections(sentiment_result=_sentiment_result(datetime.datetime(2026, 8, 21, 15, 0))),
    )
    assert ok.families["sentiment"]["m1_overall_score"] == 58.0
    assert ok.rejected == []

    bad = build_premarket_package(
        TRADE_DATE,
        ch_client=_make_ch(),
        injected=PremarketInjections(sentiment_result=_sentiment_result(datetime.datetime(2026, 8, 24, 9, 0))),
    )
    assert bad.families["sentiment"]["m1_overall_score"] is None
    assert any(r["family"] == "sentiment" for r in bad.rejected)


def test_pit_custom_asof_cutoff():
    """自定义 cutoff 生效：08:00→07:00 收紧后，07:30 的注入被拒。"""
    snap = _futures_snapshot(f"{TRADE_DATE} 07:30:00")
    ok = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), injected=PremarketInjections(futures_snapshot=snap))
    assert ok.families["derivatives"]["if_basis_rate"] == -0.002
    tight = build_premarket_package(
        TRADE_DATE,
        ch_client=_make_ch(),
        asof_cutoff=f"{TRADE_DATE} 07:00:00",
        injected=PremarketInjections(futures_snapshot=snap),
    )
    assert tight.families["derivatives"]["if_basis_rate"] is None
    assert tight.asof_cutoff == f"{TRADE_DATE} 07:00:00"


def test_calendar_event_after_trade_date_rejected():
    """日历族上限：event_date > trade_date 拒入留痕（今日预告不超今日）。"""
    cal = _tsv([(T1, "futures_delivery"), (TRADE_DATE, "option_expiry"), ("2026-08-25", "fomc_meeting")])
    pkg = build_premarket_package(TRADE_DATE, ch_client=_make_ch(calendar=cal))
    assert [e["event_type"] for e in pkg.families["calendar"]["today_preview"]] == ["option_expiry"]
    assert any(r["family"] == "calendar" and r["asof"] == "2026-08-25" for r in pkg.rejected)


def test_invalid_trade_date_raises():
    with pytest.raises(ValueError):
        build_premarket_package("2026-13-40", ch_client=_make_ch())
    with pytest.raises(ValueError):
        build_premarket_package(TRADE_DATE, ch_client=_make_ch(), asof_cutoff="not-a-ts")


# ══════════════════════════════════════════════════════════════
# input_hash 稳定性与敏感性（铁律④）
# ══════════════════════════════════════════════════════════════


def test_input_hash_stable_across_runs():
    p1 = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), injected=_full_injected())
    p2 = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), injected=_full_injected())
    assert p1.input_hash == p2.input_hash
    assert p1.families == p2.families
    assert len(p1.input_hash) == 64  # SHA-256 hex


def test_input_hash_sensitive_to_data_change():
    p1 = build_premarket_package(TRADE_DATE, ch_client=_make_ch())
    changed = _make_ch(us_index=_tsv([(T1, "SPX", "6501"), (T2, "SPX", "6450")]))
    p2 = build_premarket_package(TRADE_DATE, ch_client=changed)
    assert p1.input_hash != p2.input_hash


def test_input_hash_sensitive_to_cutoff_change():
    p1 = build_premarket_package(TRADE_DATE, ch_client=_make_ch())
    p2 = build_premarket_package(TRADE_DATE, ch_client=_make_ch(), asof_cutoff=f"{TRADE_DATE} 07:00:00")
    assert p1.input_hash != p2.input_hash


# ══════════════════════════════════════════════════════════════
# 输出契约 schema 校验（拒收不炸）
# ══════════════════════════════════════════════════════════════

_PARSE_KW = dict(trade_date=TRADE_DATE, input_hash="h" * 64, model_version="m", prompt_version="pm-v1.0.0")


def test_parse_valid_output():
    analysis, errors = parse_llm_output(_valid_llm_json(), **_PARSE_KW)
    assert errors == []
    assert analysis is not None
    assert analysis.date == TRADE_DATE
    assert analysis.scenarios["gap_up"].prob == 0.25
    assert analysis.scenarios["flat"].key_levels == ["上证 3840"]
    assert analysis.risk_points == ["外围波动"]
    json.dumps(analysis.to_dict(), ensure_ascii=False)


def test_parse_tolerates_markdown_fence():
    analysis, errors = parse_llm_output(f"```json\n{_valid_llm_json()}\n```", **_PARSE_KW)
    assert errors == [] and analysis is not None


def test_parse_missing_field_rejected():
    obj = json.loads(_valid_llm_json())
    del obj["watch_sectors"]
    analysis, errors = parse_llm_output(json.dumps(obj, ensure_ascii=False), **_PARSE_KW)
    assert analysis is None
    assert any("watch_sectors" in e for e in errors)


def test_parse_prob_sum_out_of_tolerance_rejected():
    obj = json.loads(_valid_llm_json())
    obj["scenarios"]["gap_down"]["prob"] = 0.05  # 和=0.80，超 ±0.02
    analysis, errors = parse_llm_output(json.dumps(obj, ensure_ascii=False), **_PARSE_KW)
    assert analysis is None
    assert any("概率和" in e for e in errors)


def test_parse_prob_sum_within_tolerance_accepted():
    obj = json.loads(_valid_llm_json())
    obj["scenarios"]["gap_down"]["prob"] = 0.26  # 和=1.01，容差内
    analysis, errors = parse_llm_output(json.dumps(obj, ensure_ascii=False), **_PARSE_KW)
    assert errors == [] and analysis is not None


def test_parse_prob_out_of_range_rejected():
    obj = json.loads(_valid_llm_json())
    obj["scenarios"]["flat"]["prob"] = 1.5
    analysis, errors = parse_llm_output(json.dumps(obj, ensure_ascii=False), **_PARSE_KW)
    assert analysis is None
    assert any("越界" in e for e in errors)


def test_parse_date_mismatch_rejected():
    analysis, errors = parse_llm_output(_valid_llm_json(trade_date=T1), **_PARSE_KW)
    assert analysis is None
    assert any("date" in e for e in errors)


def test_parse_echoed_identity_mismatch_rejected():
    """LLM 回显的 input_hash 与运行值不一致 → 拒收（铁律④ 防张冠李戴）。"""
    analysis, errors = parse_llm_output(_valid_llm_json(input_hash="0" * 64), **_PARSE_KW)
    assert analysis is None
    assert any("input_hash" in e for e in errors)


def test_parse_non_json_rejected():
    analysis, errors = parse_llm_output("今天大概率高开，没有JSON", **_PARSE_KW)
    assert analysis is None
    assert any("json_extract_failed" in e for e in errors)


# ══════════════════════════════════════════════════════════════
# mock llm_client 端到端（v1 单调用 / v2 三调用编排）+ 落库幂等
# ══════════════════════════════════════════════════════════════


def _read_rows(db_path) -> list[sqlite3.Row]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM llm_daily_analysis ORDER BY id").fetchall()
    finally:
        conn.close()


def test_run_v1_success_end_to_end(tmp_path):
    db = tmp_path / "governance.db"
    calls: list[str] = []

    def _client(prompt: str):
        calls.append(prompt)
        return {"text": _valid_llm_json(), "tokens_in": 12000, "tokens_out": 1500, "cost_yuan": 0.05}

    res = run_llm_analysis(TRADE_DATE, llm_client=_client, ch_client=_make_ch(), db_path=db)
    assert res.status == STATUS_SUCCESS
    assert res.analysis is not None and res.analysis.date == TRADE_DATE
    assert res.tokens_in == 12000 and res.tokens_out == 1500
    assert res.cost_yuan == pytest.approx(0.05)
    assert res.latency_ms is not None and res.latency_ms >= 0
    assert res.db_logged and res.row_id > 0
    assert res.errors == []
    # v1 单调用；prompt 含系统纪律+数据包
    assert len(calls) == 1
    assert "盘前分析员" in calls[0] and TRADE_DATE in calls[0] and "kline" not in calls[0]
    assert '"index"' in calls[0]  # 数据包七族注入
    # 版本冻结入库（铁律②③④）
    assert res.prompt_version == PROMPT_VERSION
    row = _read_rows(db)[0]
    assert row["status"] == STATUS_SUCCESS
    assert row["prompt_version"] == PROMPT_VERSION
    assert row["input_hash"] == res.input_hash
    out = json.loads(row["output_json"])
    assert out["mode"] == "v1" and out["analysis"]["scenarios"]["flat"]["prob"] == 0.5


def test_run_v2_debate_three_calls(tmp_path):
    db = tmp_path / "governance.db"
    calls: list[str] = []

    def _client(prompt: str):
        calls.append(prompt)
        if "多头角色" in prompt:
            return {"text": "多头陈词：两融放量", "tokens_in": 100, "tokens_out": 50, "cost_yuan": 0.01}
        if "空头角色" in prompt:
            return {"text": "空头陈词：炸板率高", "tokens_in": 100, "tokens_out": 50, "cost_yuan": 0.01}
        return {"text": _valid_llm_json(), "tokens_in": 300, "tokens_out": 200, "cost_yuan": 0.03}

    cfg = LlmPremarketConfig(debate_mode=True)
    res = run_llm_analysis(TRADE_DATE, llm_client=_client, ch_client=_make_ch(), config=cfg, db_path=db)
    assert res.status == STATUS_SUCCESS
    assert res.debate_mode is True
    # 三调用编排：多头→空头→综合席；综合席 prompt 含双方陈词+数据包
    assert len(calls) == 3
    assert "多头角色" in calls[0] and "空头角色" in calls[1]
    assert "综合席" in calls[2] and "多头陈词：两融放量" in calls[2] and "空头陈词：炸板率高" in calls[2]
    # 计量合计
    assert res.tokens_in == 500 and res.tokens_out == 300
    assert res.cost_yuan == pytest.approx(0.05)
    # 有效版本带 +debate 后缀（铁律③ 模板集分离）
    assert res.prompt_version == f"{PROMPT_VERSION}+debate"
    out = json.loads(_read_rows(db)[0]["output_json"])
    assert out["mode"] == "v2_debate"
    assert out["debate"]["bull"] == "多头陈词：两融放量"


def test_run_invalid_output_persisted_not_raised(tmp_path):
    db = tmp_path / "governance.db"

    def _client(prompt: str):
        return "我认为明天涨"  # 非 JSON

    res = run_llm_analysis(TRADE_DATE, llm_client=_client, ch_client=_make_ch(), db_path=db)
    assert res.status == STATUS_INVALID
    assert res.analysis is None
    assert res.db_logged  # 拒收也落库留痕
    row = _read_rows(db)[0]
    assert row["status"] == STATUS_INVALID
    assert "json_extract_failed" in row["error"]
    assert "我认为明天涨" in json.loads(row["output_json"])["raw_output"]


def test_run_llm_client_exception_marks_invalid(tmp_path):
    db = tmp_path / "governance.db"

    def _client(prompt: str):
        raise RuntimeError("api timeout")

    res = run_llm_analysis(TRADE_DATE, llm_client=_client, ch_client=_make_ch(), db_path=db)
    assert res.status == STATUS_INVALID
    assert any("llm_call_failed" in e for e in res.errors)
    assert _read_rows(db)[0]["status"] == STATUS_INVALID


def test_run_str_return_client_supported(tmp_path):
    db = tmp_path / "governance.db"
    res = run_llm_analysis(TRADE_DATE, llm_client=lambda prompt: _valid_llm_json(), ch_client=_make_ch(), db_path=db)
    assert res.status == STATUS_SUCCESS
    assert res.tokens_in is None and res.cost_yuan is None


def test_persist_idempotent_same_key(tmp_path):
    """幂等：UNIQUE(trade_date, model_version, prompt_version, input_hash) 同键重跑保首条。"""
    db = tmp_path / "governance.db"

    def _client(prompt: str):
        return _valid_llm_json()

    r1 = run_llm_analysis(TRADE_DATE, llm_client=_client, ch_client=_make_ch(), db_path=db)
    r2 = run_llm_analysis(TRADE_DATE, llm_client=_client, ch_client=_make_ch(), db_path=db)
    assert r1.status == r2.status == STATUS_SUCCESS
    assert r1.input_hash == r2.input_hash
    assert r2.row_id == r1.row_id  # 同键返已存在行 id
    rows = _read_rows(db)
    assert len(rows) == 1  # 保首条不覆写


def test_persist_debate_and_v1_same_input_both_kept(tmp_path):
    """v1/v2 模板集版本串分离：同输入两模式不互撞幂等键。"""
    db = tmp_path / "governance.db"
    r1 = run_llm_analysis(TRADE_DATE, llm_client=lambda p: _valid_llm_json(), ch_client=_make_ch(), db_path=db)
    r2 = run_llm_analysis(
        TRADE_DATE,
        llm_client=lambda p: _valid_llm_json(),
        ch_client=_make_ch(),
        config=LlmPremarketConfig(debate_mode=True),
        db_path=db,
    )
    assert r1.prompt_version != r2.prompt_version
    assert len(_read_rows(db)) == 2


# ══════════════════════════════════════════════════════════════
# llm_client=None → skipped_not_wired 落库留痕不炸
# ══════════════════════════════════════════════════════════════


def test_run_not_wired_skipped(tmp_path):
    db = tmp_path / "governance.db"
    res = run_llm_analysis(TRADE_DATE, llm_client=None, ch_client=_make_ch(), db_path=db)
    assert res.status == STATUS_SKIPPED_NOT_WIRED
    assert res.analysis is None
    assert res.db_logged and res.row_id > 0
    row = _read_rows(db)[0]
    assert row["status"] == STATUS_SKIPPED_NOT_WIRED
    assert row["output_json"] == ""
    assert row["error"] is None
    assert row["input_hash"] == res.input_hash  # 数据包哈希仍留痕（PIT 可复现锚）


def test_ensure_table_idempotent(tmp_path):
    db = tmp_path / "sub" / "governance.db"
    p1 = ensure_llm_daily_analysis_table(db)
    p2 = ensure_llm_daily_analysis_table(db)
    assert p1 == p2 == db
    assert _read_rows(db) == []


def test_build_user_prompt_contains_package_and_pit_note():
    pkg = build_premarket_package(TRADE_DATE, ch_client=_make_ch())
    prompt = build_user_prompt(pkg)
    assert pkg.asof_cutoff in prompt and "PIT" in prompt
    assert '"sentiment"' in prompt
    debate_prompt = build_user_prompt(pkg, debate_transcripts={"bull": "多", "bear": "空"})
    assert "【多头陈词】\n多" in debate_prompt and "【空头陈词】\n空" in debate_prompt
