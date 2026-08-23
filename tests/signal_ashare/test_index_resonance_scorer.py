# [BLUEPRINT] MOD-SIG-069 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-31 行）
# [MODULE] tests.signal_ashare.test_index_resonance_scorer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.index_resonance_scorer
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=共振评分逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-069_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-069 指数级多指标共振综合评分 单元测试（GAP-F-31，合成数据不触库）。

覆盖：七族投票口径（单边上涨→买入/单边下跌→卖出/震荡→中性）、共振 x/7 计数、
置信度启发式（中性恒 50）、样本不足 degraded 不出伪信号、weight_overrides
白名单/非法键 fail-closed、权重和 0 degraded、加载层假 client（DESC→升序还原）、
PIT 日期非法 fail-closed、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, timedelta

import pytest

from zephyr.signal_ashare.index_resonance_scorer import (
    SIGNAL_BUY,
    SIGNAL_NEUTRAL,
    SIGNAL_SELL,
    DailyBar,
    ResonanceConfig,
    compute_resonance,
    score_index_resonance,
)

D0 = date(2026, 5, 20)


def _bars(closes: list[float], volume: float = 1000.0) -> list[DailyBar]:
    return [
        DailyBar(
            date=(D0 + timedelta(days=i)).isoformat(),
            open=c * 0.999, high=c * 1.002, low=c * 0.998, close=c, volume=volume,
        )
        for i, c in enumerate(closes)
    ]


def _uptrend(n: int = 80) -> list[DailyBar]:
    return _bars([100.0 + i * 0.3 for i in range(n)])


def _downtrend(n: int = 80) -> list[DailyBar]:
    return _bars([124.0 - i * 0.3 for i in range(n)])


def _sideways(n: int = 80) -> list[DailyBar]:
    # 下跌后走平：MACD 收敛转正/KDJ 走平转负/RSI 平/量能缩/均线混合/BOLL 中轨下/趋势平
    # → 加权分落 (-0.2, 0.2) 中性区（逐族口径可复算）
    half = n // 2
    closes = [108.0 - i * 0.2 for i in range(half)] + [100.0] * (n - half)
    return _bars(closes)


# ------------------------------------------------------------------
# 三态信号
# ------------------------------------------------------------------


def test_uptrend_buy_high_resonance():
    result = compute_resonance(_uptrend())
    assert result.signal == SIGNAL_BUY
    assert result.resonance_total == 7
    assert result.resonance_count >= 5  # 除量能（恒量→0）外各族同向
    assert result.score is not None and result.score >= 0.2
    assert 50.0 < result.confidence <= 95.0
    macd = next(f for f in result.family_votes if f.family == "macd")
    assert macd.vote == 1 and macd.weight == pytest.approx(0.18)


def test_downtrend_sell():
    result = compute_resonance(_downtrend())
    assert result.signal == SIGNAL_SELL
    assert result.resonance_count >= 5
    assert result.score is not None and result.score <= -0.2


def test_sideways_neutral_flat_confidence():
    result = compute_resonance(_sideways())
    assert result.signal == SIGNAL_NEUTRAL
    assert result.confidence == 50.0  # 中性恒 50
    # 中性：共振计数=投 0 族数
    assert result.resonance_count == sum(1 for f in result.family_votes if f.vote == 0)


def test_resonance_count_matches_direction():
    result = compute_resonance(_uptrend())
    aligned = sum(1 for f in result.family_votes if f.vote == 1)
    assert result.resonance_count == aligned


def test_volume_family_expanding_up():
    bars = _uptrend()
    # 近 5 日放量 → 量能族 +1
    bumped = [DailyBar(b.date, b.open, b.high, b.low, b.close, b.volume * (3 if i >= 75 else 1))
              for i, b in enumerate(bars)]
    result = compute_resonance(bumped)
    vol = next(f for f in result.family_votes if f.family == "volume")
    assert vol.vote == 1
    assert "放量" in vol.reason


# ------------------------------------------------------------------
# 降级与权重
# ------------------------------------------------------------------


def test_insufficient_bars_degraded():
    result = compute_resonance(_uptrend(30))
    assert result.degraded is True
    assert result.confidence is None and result.score is None
    assert any("样本不足" in n for n in result.notes)


def test_weight_overrides_whitelist():
    cfg = ResonanceConfig(weight_overrides={"rsi": 5.0})
    result = compute_resonance(_uptrend(), cfg)
    assert result.weight_mode == "override"
    rsi = next(f for f in result.family_votes if f.family == "rsi")
    assert rsi.weight == pytest.approx(5.0)


def test_weight_overrides_bad_key_fail_closed():
    with pytest.raises(ValueError):
        compute_resonance(_uptrend(), ResonanceConfig(weight_overrides={"cci": 1.0}))


def test_zero_weight_sum_degraded():
    cfg = ResonanceConfig(weight_overrides={
        "macd": 0.0, "kdj": 0.0, "rsi": 0.0, "volume": 0.0, "ma": 0.0, "boll": 0.0, "trend": 0.0,
    })
    result = compute_resonance(_uptrend(), cfg)
    assert result.degraded is True


def test_bad_threshold_fail_closed():
    with pytest.raises(ValueError):
        compute_resonance(_uptrend(), ResonanceConfig(buy_threshold=1.5))


# ------------------------------------------------------------------
# 主入口（假 client）
# ------------------------------------------------------------------


class _FakeClient:
    def __init__(self, rows):
        self._rows = rows
        self.last_params = None

    def execute(self, sql, params):
        self.last_params = params
        return self._rows


def _rows_desc(bars: list[DailyBar]) -> list[tuple]:
    # kline_index 查询 ORDER BY trade_date DESC 返回形态
    return [
        (b.date, b.open, b.high, b.low, b.close, b.volume) for b in reversed(bars)
    ]


def test_main_entry_fake_client_desc_to_asc():
    client = _FakeClient(_rows_desc(_uptrend()))
    result = score_index_resonance("000001.SH", trade_date=date(2026, 8, 21), ch_client=client)
    assert result.symbol == "000001.SH"
    assert result.signal == SIGNAL_BUY
    assert result.date == _uptrend()[-1].date  # DESC 行已还原升序
    assert client.last_params["trade_date"] == date(2026, 8, 21)


def test_main_entry_no_trade_date_sentinel():
    client = _FakeClient(_rows_desc(_uptrend()))
    result = score_index_resonance("000001.SH", ch_client=client)
    assert client.last_params["trade_date"] == date(2100, 1, 1)  # PIT 上限=不过滤
    assert result.signal == SIGNAL_BUY


def test_main_entry_query_exception_degraded():
    class _Boom:
        def execute(self, sql, params):  # noqa: ARG002
            raise RuntimeError("boom")

    result = score_index_resonance("000001.SH", trade_date=date(2026, 8, 21), ch_client=_Boom())
    assert result.degraded is True
    assert any("查询异常" in n for n in result.notes)


def test_main_entry_bad_date_fail_closed():
    with pytest.raises(ValueError):
        score_index_resonance("000001.SH", trade_date="2026/08/21", ch_client=_FakeClient([]))


def test_result_json_serializable():
    result = compute_resonance(_uptrend())
    json.dumps(asdict(result), ensure_ascii=False)
