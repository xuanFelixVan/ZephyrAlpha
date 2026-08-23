# [BLUEPRINT] MOD-REGIME-008 | 待统筹登记（supplement：GAP-F-10 四指数分市场分析组合卡；主号=四指数 regime 面板）
# [MODULE] tests.regime.test_index_market_brief
# [DOMAIN] D_REGIME
# [DEPENDENCIES] zephyr.regime.index_market_brief; zephyr.signal_ashare.next_day_8state_forecast
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网（panel/bars 注入）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=四指数分市场分析组合逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-REGIME-008_brief_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-REGIME-008 supplement 四指数分市场分析 单元测试（GAP-F-10，合成注入）。

覆盖：L14 四指数清单（上证/深成/创业板/科创综指）、regime 腿（panel 注入
按裸码匹配，缺卡降级）、预判腿（MOD-SIG-037 参数化 8 态预测，历史不足降级）、
情绪腿（市场共享注入，四卡同值——"1 引擎×4 代理"语义）、全缺降级、
日期校验 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.regime.index_market_brief import (
    FOUR_INDEX_CODES,
    IndexBriefConfig,
    build_index_market_brief,
)
from zephyr.signal_ashare.next_day_8state_forecast import DailyBar


class _FakeRegimeCard:
    def __init__(self, code: str, dominant: str = "r3", conf: float = 0.62, rank: int | None = 1, degraded: bool = False):
        self.code = code
        self.dominant_regime = dominant
        self.confidence = conf
        self.probabilities = {"r1": 0.1, "r2": 0.1, "r3": 0.62, "r4": 0.18, "r10": 0.0, "r11": 0.0, "r12": 0.0}
        self.rank = rank
        self.degraded = degraded


class _FakePanel:
    def __init__(self, cards, ranking=("000001", "399006")):
        self.cards = tuple(cards)
        self.strength_ranking = ranking
        self.degraded = False


def _bars(n: int = 40, start: float = 100.0, drift: float = 0.3) -> list[DailyBar]:
    out = []
    price = start
    for _ in range(n):
        o = price
        c = price + drift
        out.append(DailyBar(open=o, high=max(o, c) + 0.2, low=min(o, c) - 0.2, close=c))
        price = c
    return out


ALL_BARS = {"000001": _bars(), "399001": _bars(drift=0.2), "399006": _bars(drift=0.4), "000680": _bars(drift=0.1)}


# ------------------------------------------------------------------
# 组合主核
# ------------------------------------------------------------------


def test_four_index_universe() -> None:
    assert FOUR_INDEX_CODES == ("000001", "399001", "399006", "000680")


def test_brief_full_legs() -> None:
    panel = _FakePanel([_FakeRegimeCard("000001"), _FakeRegimeCard("399006", rank=2)])
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=panel, index_bars=ALL_BARS,
        sentiment_label="偏暖", sentiment_score=62.5, config=IndexBriefConfig(),
    )
    assert out.degraded is False
    assert len(out.cards) == 4
    c1 = next(c for c in out.cards if c.code == "000001")
    assert c1.regime_dominant == "r3"
    assert c1.regime_confidence == pytest.approx(0.62)
    assert c1.strength_rank == 1
    assert c1.forecast_top_state  # 8 态预测出
    assert c1.forecast_probs and len(c1.forecast_probs) == 8
    assert abs(sum(c1.forecast_probs.values()) - 1.0) < 1e-6
    assert c1.sentiment_label == "偏暖"
    # 无 panel 卡的指数 regime 腿降级但预判腿仍在
    c2 = next(c for c in out.cards if c.code == "399001")
    assert c2.regime_dominant is None
    assert c2.forecast_top_state
    assert any("regime" in n.lower() or "面板" in n for n in c2.notes)


def test_brief_strength_ranking_passthrough() -> None:
    panel = _FakePanel([_FakeRegimeCard("000001")])
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=panel, index_bars=ALL_BARS, config=IndexBriefConfig()
    )
    assert out.strength_ranking == ("000001", "399006")


def test_forecast_leg_insufficient_history_degraded() -> None:
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=None,
        index_bars={"000001": _bars(n=10)},  # 状态序列长 9 < 30
        config=IndexBriefConfig(),
    )
    c1 = next(c for c in out.cards if c.code == "000001")
    assert c1.forecast_top_state is None
    assert any("历史不足" in n or "不足" in n for n in c1.notes)
    # 其余无 bars 指数亦降级
    assert all(c.degraded for c in out.cards)


def test_panel_none_regime_leg_notes() -> None:
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=None, index_bars=ALL_BARS, config=IndexBriefConfig()
    )
    assert all(c.regime_dominant is None for c in out.cards)
    assert all(c.forecast_top_state for c in out.cards)  # 预判腿独立
    assert out.degraded is False


def test_all_missing_degraded() -> None:
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=None, index_bars=None, config=IndexBriefConfig()
    )
    assert out.degraded is True


def test_invalid_trade_date_fail_closed() -> None:
    with pytest.raises(ValueError, match="trade_date"):
        build_index_market_brief(trade_date="2026-13-01", panel=None, index_bars=ALL_BARS, config=IndexBriefConfig())


def test_sentiment_shared_across_cards() -> None:
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=None, index_bars=ALL_BARS,
        sentiment_label="偏暖", sentiment_score=62.5, config=IndexBriefConfig(),
    )
    assert {c.sentiment_label for c in out.cards} == {"偏暖"}
    assert out.market_sentiment_score == pytest.approx(62.5)


def test_json_serializable() -> None:
    panel = _FakePanel([_FakeRegimeCard("000001")])
    out = build_index_market_brief(
        trade_date="2026-08-21", panel=panel, index_bars=ALL_BARS,
        sentiment_label="偏暖", sentiment_score=62.5, config=IndexBriefConfig(),
    )
    json.dumps(asdict(out), ensure_ascii=False)
