# [BLUEPRINT] MOD-SIG-080 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-16 行）
# [MODULE] tests.signal_ashare.test_counter_trend_board
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.counter_trend_board
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=逆势榜四卡逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-080_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-080 逆势榜 4 卡 单元测试（GAP-F-16，合成分钟序列不触库）。

覆盖：主下跌段识别（峰→谷）、四卡口径（逆势上涨/下跌段资金流入/率先反弹/最抗跌）、
资金腿未供给降级、无有效下跌段全卡降级、板块缺分钟覆盖留痕、日期非法 fail-closed、
JSON 可序列化、主入口降级链。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.counter_trend_board import (
    CounterTrendConfig,
    build_counter_trend_board,
    run_counter_trend_board,
)

D = "2026-08-21"


def _mk_index(prices: list[float]) -> list[tuple[str, float]]:
    # 09:30 起逐分钟
    out = []
    hh, mm = 9, 30
    for p in prices:
        out.append((f"{D} {hh:02d}:{mm:02d}", p))
        mm += 1
        if mm >= 60:
            hh, mm = hh + 1, 0
    return out


def _mk_sector(closes: list[float]) -> list[tuple[str, float]]:
    return _mk_index(closes)


def _cfg(**kw) -> CounterTrendConfig:
    return CounterTrendConfig(**kw)


# 指数：平开后 09:32 见顶 102 → 09:36 谷底 99 → 反弹
INDEX = _mk_index([100.0, 101.0, 102.0, 101.0, 100.0, 99.5, 99.0, 99.5, 100.5, 101.5])
# 板块 A：下跌段逆势上涨（指数 102→99 段它横盘偏强）
SECT_A = _mk_sector([100.0, 100.5, 101.0, 101.2, 101.3, 101.4, 101.5, 101.8, 102.2, 102.6])
# 板块 B：跟跌且更弱（最抗跌榜应排 A 之后），谷后横移不反弹
SECT_B = _mk_sector([100.0, 100.2, 100.5, 99.0, 97.5, 96.0, 94.5, 94.4, 94.3, 94.4])
# 板块 C：跟跌但谷后率先反弹（09:37 起快速收复）
SECT_C = _mk_sector([100.0, 100.1, 100.2, 99.5, 98.5, 97.5, 96.5, 97.2, 98.5, 100.0])


def _board(**kw):
    return build_counter_trend_board(
        index_series=INDEX,
        sector_series={"880001": SECT_A, "880002": SECT_B, "880003": SECT_C},
        fund_flow=kw.pop("fund_flow", None),
        config=_cfg(**kw),
    )


# ------------------------------------------------------------------
# 下跌段识别
# ------------------------------------------------------------------


def test_down_segment_identified() -> None:
    board = _board()
    assert board.degraded is False
    assert board.down_start_ts == f"{D} 09:32"  # 峰 102
    assert board.down_end_ts == f"{D} 09:36"    # 谷 99
    assert board.index_down_pct == pytest.approx((99.0 / 102.0 - 1.0) * 100.0, abs=1e-3)


def test_no_down_segment_all_cards_degraded() -> None:
    up_only = _mk_index([100.0, 101.0, 102.0, 103.0, 104.0])
    board = build_counter_trend_board(
        index_series=up_only, sector_series={"880001": SECT_A}, fund_flow=None, config=_cfg()
    )
    assert board.degraded is True
    assert all(c.degraded for c in board.cards)
    assert any("无有效下跌段" in n for n in board.notes)


def test_too_few_minutes_degraded() -> None:
    board = build_counter_trend_board(
        index_series=_mk_index([100.0, 101.0]), sector_series={"880001": SECT_A},
        fund_flow=None, config=_cfg(),
    )
    assert board.degraded is True


# ------------------------------------------------------------------
# 卡 1：逆势上涨
# ------------------------------------------------------------------


def test_card_counter_rally() -> None:
    board = _board()
    card = next(c for c in board.cards if c.card == "counter_rally")
    assert card.degraded is False
    codes = [i.sector_code for i in card.items]
    assert "880001" in codes  # 下跌段累计 +0.49%（101→101.5）
    assert "880002" not in codes  # 大跌不入选
    assert card.items[0].metric_value > 0


# ------------------------------------------------------------------
# 卡 2：下跌段资金流入
# ------------------------------------------------------------------


def test_card_fund_inflow() -> None:
    board = _board(fund_flow={"880001": 5_000.0, "880002": -3_000.0, "880003": 800.0})
    card = next(c for c in board.cards if c.card == "fund_inflow")
    assert card.degraded is False
    assert [i.sector_code for i in card.items] == ["880001", "880003"]


def test_card_fund_inflow_missing_degraded() -> None:
    board = _board(fund_flow=None)
    card = next(c for c in board.cards if c.card == "fund_inflow")
    assert card.degraded is True
    assert "资金流" in card.note


# ------------------------------------------------------------------
# 卡 3：率先反弹
# ------------------------------------------------------------------


def test_card_first_rebound() -> None:
    board = _board()
    card = next(c for c in board.cards if c.card == "first_rebound")
    assert card.degraded is False
    codes = [i.sector_code for i in card.items]
    assert codes == ["880003", "880001"]  # C 谷后 1 分钟过阈值最快，A 2 分钟次之
    assert "880002" not in codes  # 不反弹
    # 分钟数越小越靠前
    minutes = [i.metric_value for i in card.items]
    assert minutes == sorted(minutes)


def test_card_first_rebound_trough_at_end_degraded() -> None:
    # 谷底=最后一分钟 → 无反弹观察窗
    idx = _mk_index([100.0, 102.0, 101.0, 100.0, 99.0])
    board = build_counter_trend_board(
        index_series=idx, sector_series={"880001": SECT_A[:5]}, fund_flow=None, config=_cfg()
    )
    card = next(c for c in board.cards if c.card == "first_rebound")
    assert card.degraded is True


# ------------------------------------------------------------------
# 卡 4：最抗跌
# ------------------------------------------------------------------


def test_card_most_resilient() -> None:
    board = _board()
    card = next(c for c in board.cards if c.card == "most_resilient")
    assert card.degraded is False
    codes = [i.sector_code for i in card.items]
    assert codes[0] == "880001"  # 下跌段最大回撤最小
    assert codes.index("880003") < codes.index("880002")  # C 比 B 抗跌
    # metric=回撤%（≤0），越接近 0 越抗跌
    assert card.items[0].metric_value >= card.items[-1].metric_value


def test_top_n_caps_items() -> None:
    board = _board(top_n=2)
    for card in board.cards:
        assert len(card.items) <= 2


def test_sector_names_attached() -> None:
    board = build_counter_trend_board(
        index_series=INDEX, sector_series={"880001": SECT_A}, fund_flow=None,
        config=_cfg(sector_names={"880001": "半导体"}),
    )
    card = next(c for c in board.cards if c.card == "counter_rally")
    assert card.items[0].sector_name == "半导体"


def test_json_serializable() -> None:
    board = _board(fund_flow={"880001": 5.0})
    json.dumps(asdict(board), ensure_ascii=False)


# ------------------------------------------------------------------
# 主入口（注入序列；客户端腿降级）
# ------------------------------------------------------------------


def test_run_with_injected_series() -> None:
    board = run_counter_trend_board(
        trade_date=D, ch_client=None,
        index_series=INDEX, sector_series={"880001": SECT_A}, config=_cfg(),
    )
    assert board.date == D
    assert board.degraded is False


def test_run_invalid_date_fail_closed() -> None:
    with pytest.raises(ValueError, match="trade_date"):
        run_counter_trend_board(
            trade_date="2026-13-01", ch_client=None,
            index_series=INDEX, sector_series={}, config=_cfg(),
        )


def test_run_no_client_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "zephyr.signal_ashare.counter_trend_board._default_client", lambda: None
    )
    board = run_counter_trend_board(trade_date=D, ch_client=None, config=_cfg())
    assert board.degraded is True
