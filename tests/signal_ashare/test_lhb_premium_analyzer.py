"""MOD-SIG-057 龙虎榜盘后溢价分析器 单元测试（44号备忘录 §9.7 四规则）"""

import json
import sys
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare import lhb_premium_analyzer as mod
from zephyr.signal_ashare.lhb_premium_analyzer import (
    LhbPremiumResult,
    compute_lhb_premium,
)

TRADE_DATE = date(2026, 8, 18)


class _FakeCH:
    """鸭子类型 ch_client：按 SQL 路由返回合成行（不触库）。"""

    def __init__(self, seat_rows=None, summary_rows=None, history_rows=None, exc=None):
        self._seats = seat_rows or []
        self._summary = summary_rows or []
        self._history = history_rows or []
        self._exc = exc

    def execute(self, sql, params=None):
        if self._exc is not None:
            raise self._exc
        if "seat_name IN" in sql:
            return list(self._history)
        if "dragon_tiger_seat" in sql:
            return list(self._seats)
        return list(self._summary)


def _seat(
    symbol: str,
    seat_name: str,
    buy: float,
    sell: float,
    buy_rank=None,
    sell_rank=None,
    provider_type: str = "broker",
    reason: str = "日涨幅偏离值达7%",
) -> tuple:
    """合成 dragon_tiger_seat 行（列序对齐模块 SQL）。"""
    return (symbol, seat_name, buy, sell, buy - sell, buy_rank, sell_rank, provider_type, reason)


def _summary(symbol: str, net_buy: float, buy: float, sell: float, reason: str = "日涨幅偏离值达7%") -> tuple:
    """合成 dragon_tiger 汇总行（列序对齐模块 SQL）。"""
    return (symbol, net_buy, buy, sell, reason)


# ---------- 规则① 高开候选 ----------


def test_high_open_candidate_exactly_two_strong_seats() -> None:
    """净买率>5% 且机构+一线游资恰好 2 席（≥2 正边界）→ 高开候选，系数 1.0。"""
    client = _FakeCH(
        summary_rows=[_summary("300750", 60e6, 300e6, 240e6)],  # 净买率 60/540=11.1%
        seat_rows=[
            _seat("300750", "机构专用", 30e6, 1e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "章盟主", 21e6, 1e6, buy_rank=2),
        ],  # 买方合计 51e6，买一占比 58.8%<60%（非独食）
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.degraded is False
    assert result.date == "2026-08-18"
    assert result.high_open_candidates == ["300750"]
    premium = result.premiums["300750"]
    assert premium.premium_factor == pytest.approx(1.0)
    assert "high_open_candidate" in premium.tags
    assert premium.reasons


def test_exact_5pct_ratio_not_candidate() -> None:
    """净买率恰好 5%（严格 > 边界）→ 不触发高开候选。"""
    client = _FakeCH(
        summary_rows=[_summary("300750", 50e6, 525e6, 475e6)],  # 恰好 5.0%
        seat_rows=[
            _seat("300750", "机构专用", 41e6, 1e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "章盟主", 21e6, 1e6, buy_rank=2),
        ],
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.degraded is False
    assert result.high_open_candidates == []
    assert "300750" not in result.premiums


def test_single_strong_seat_not_candidate() -> None:
    """净买率>5% 但机构/一线游资仅 1 席（<2 负边界）→ 不触发。"""
    client = _FakeCH(
        summary_rows=[_summary("300750", 60e6, 300e6, 240e6)],
        seat_rows=[
            _seat("300750", "机构专用", 41e6, 1e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "某不知名营业部", 21e6, 1e6, buy_rank=2),
        ],
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.high_open_candidates == []
    assert "300750" not in result.premiums


# ---------- 规则② 降权（独食/一日游） ----------


def test_single_seat_dominance_downgrade() -> None:
    """独食型：单一席位买入占比 >60% → 溢价系数 ×0.3。"""
    client = _FakeCH(
        summary_rows=[_summary("300750", 80e6, 200e6, 120e6)],  # 净买率 25%
        seat_rows=[
            _seat("300750", "机构专用", 150e6, 90e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "章盟主", 30e6, 10e6, buy_rank=2),
        ],
    )  # 买方合计 180e6，机构一席独占 83.3%
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.high_open_candidates == ["300750"]
    premium = result.premiums["300750"]
    assert premium.premium_factor == pytest.approx(0.3)
    assert "downgraded_dushi" in premium.tags
    assert any("独食" in r for r in premium.reasons)


def test_one_day_youzi_registry_downgrade() -> None:
    """一日游型（registry 静态标签：宁波桑田路 style=一日游）→ 溢价系数 ×0.3。"""
    client = _FakeCH(
        summary_rows=[_summary("300750", 150e6, 400e6, 250e6)],  # 净买率 23%
        seat_rows=[
            _seat("300750", "机构专用", 60e6, 1e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "章盟主", 50e6, 1e6, buy_rank=2),
            _seat("300750", "宁波桑田路", 40e6, 1e6, buy_rank=3),
        ],
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    premium = result.premiums["300750"]
    assert premium.premium_factor == pytest.approx(0.3)
    assert "downgraded_yiriyou" in premium.tags
    assert any("一日游" in r for r in premium.reasons)


def test_one_day_youzi_dynamic_sell_rate_downgrade() -> None:
    """一日游型（动态口径：未入注册表席位近 20 日隔日卖出率 >70%）→ 溢价系数 ×0.3。"""
    d = lambda day: date(2026, 7, day)  # noqa: E731
    history = []
    # 4 次买入（分散标的防日历串扰），3 次次日现卖 → 隔日卖出率 3/4=75%
    for sym, b_day, n_day, sold in [
        ("300001", date(2026, 7, 20), date(2026, 7, 21), True),
        ("300002", date(2026, 7, 22), date(2026, 7, 23), True),
        ("300003", date(2026, 7, 27), date(2026, 7, 28), True),
        ("300004", date(2026, 8, 3), date(2026, 8, 4), False),
    ]:
        history.append((b_day, sym, "某快进快出营业部", 30e6, 1e6))
        history.append((n_day, sym, "某快进快出营业部", 0.5e6, 25e6 if sold else 0.0))
    client = _FakeCH(
        summary_rows=[_summary("300750", 150e6, 400e6, 250e6)],
        seat_rows=[
            _seat("300750", "机构专用", 60e6, 1e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "章盟主", 50e6, 1e6, buy_rank=2),
            _seat("300750", "某快进快出营业部", 40e6, 1e6, buy_rank=3),
        ],
        history_rows=history,
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    premium = result.premiums["300750"]
    assert premium.premium_factor == pytest.approx(0.3)
    assert "downgraded_yiriyou" in premium.tags
    assert any("隔日卖出率" in r for r in premium.reasons)


# ---------- 规则③ 低开风险 ----------


def test_institution_net_sell_low_open_risk() -> None:
    """机构席位净卖出占比 >5% → 低开风险提示。"""
    client = _FakeCH(
        summary_rows=[_summary("600519", -100e6, 400e6, 500e6, reason="日跌幅偏离值达7%")],
        seat_rows=[
            _seat("600519", "机构专用", 1e6, 90e6, sell_rank=1, provider_type="institution"),
            _seat("600519", "沪股通专用", 1e6, 21e6, sell_rank=2, provider_type="connect"),
            _seat("600519", "某不知名营业部", 30e6, 1e6, buy_rank=1),
        ],
    )  # 机构净卖出 110e6 / 900e6 = 12.2%
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.low_open_risks == ["600519"]
    premium = result.premiums["600519"]
    assert "low_open_risk" in premium.tags
    assert any("低开" in r for r in premium.reasons)
    assert result.high_open_candidates == []


# ---------- 规则④ 反核观察 ----------


def test_fanhe_watchlist_limit_down_known_youzi() -> None:
    """跌停股买一为知名游资（章盟主，registry 龙头连板风格）→ 反核观察名单。"""
    client = _FakeCH(
        summary_rows=[_summary("002594", 30e6, 120e6, 90e6, reason="日收盘价格跌停")],
        seat_rows=[
            _seat("002594", "章盟主", 50e6, 1e6, buy_rank=1, reason="日收盘价格跌停"),
            _seat("002594", "某不知名营业部", 20e6, 1e6, buy_rank=2, reason="日收盘价格跌停"),
        ],
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.fanhe_watchlist == ["002594"]
    premium = result.premiums["002594"]
    assert "fanhe_watch" in premium.tags
    assert any("反核" in r for r in premium.reasons)


def test_limit_down_unknown_buyer_not_fanhe() -> None:
    """跌停股买一为未入注册表营业部（非知名游资）→ 不进反核名单。"""
    client = _FakeCH(
        summary_rows=[_summary("002594", 30e6, 120e6, 90e6, reason="日收盘价格跌停")],
        seat_rows=[
            _seat("002594", "某不知名营业部", 50e6, 1e6, buy_rank=1, reason="日收盘价格跌停"),
        ],
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.fanhe_watchlist == []
    assert "002594" not in result.premiums


# ---------- degraded 契约 ----------


def test_empty_rows_degraded() -> None:
    """无龙虎榜日（当日零行）→ degraded=True 空结果不炸。"""
    result = compute_lhb_premium(TRADE_DATE, ch_client=_FakeCH())
    assert result.degraded is True
    assert result.high_open_candidates == []
    assert result.low_open_risks == []
    assert result.fanhe_watchlist == []
    assert result.premiums == {}
    assert result.notes


def test_query_exception_degraded() -> None:
    """查询异常 → degraded=True 空结果不抛。"""
    client = _FakeCH(exc=RuntimeError("ch boom"))
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert result.degraded is True
    assert result.premiums == {}
    assert any("异常" in n for n in result.notes)


def test_client_unavailable_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    """ch_client 未注入且默认客户端不可得 → degraded=True。"""
    monkeypatch.setattr(mod, "_default_client", lambda: None)
    result = compute_lhb_premium(TRADE_DATE, ch_client=None)
    assert result.degraded is True
    assert result.premiums == {}


# ---------- 输出契约 ----------


def test_result_json_serializable() -> None:
    """LhbPremiumResult dataclass → asdict → JSON 可序列化（prediction_log 预留）。"""
    client = _FakeCH(
        summary_rows=[_summary("300750", 60e6, 300e6, 240e6)],
        seat_rows=[
            _seat("300750", "机构专用", 30e6, 1e6, buy_rank=1, provider_type="institution"),
            _seat("300750", "章盟主", 21e6, 1e6, buy_rank=2),
        ],
    )
    result = compute_lhb_premium(TRADE_DATE, ch_client=client)
    assert isinstance(result, LhbPremiumResult)
    payload = json.dumps(asdict(result), ensure_ascii=False)
    assert "300750" in payload
