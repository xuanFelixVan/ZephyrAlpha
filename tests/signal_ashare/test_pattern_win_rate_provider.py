# [BLUEPRINT] MOD-SIG-145 | tests/signal_ashare/test_pattern_win_rate_provider.py
# [MODULE] tests.signal_ashare.test_pattern_win_rate_provider
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 注入式 fake client，禁触 CH
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->测试失败
# [TESTS] pytest tests/signal_ashare/test_pattern_win_rate_provider.py
# [TTL] permanent
"""pattern_win_rate_provider 单测（W3）——None 语义三途（查无/low_sample/NULL）+baseline。"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider import (
    PatternWinRateProvider,
    engine_win_rate_callable,
)


class _FakeClient:
    def __init__(self, rows):
        self._rows = rows
        self.last_sql = ""
        self.last_params = {}

    def execute(self, sql, params=None):
        self.last_sql = sql
        self.last_params = params or {}
        return self._rows


def _provider(rows) -> PatternWinRateProvider:
    return PatternWinRateProvider(client=_FakeClient(rows))


def test_get_returns_rate():
    p = _provider([(500, 0.72, 0)])
    assert p.get("双顶@746", direction="向下", fwd_window=10) == 0.72
    assert p._ensure_client().last_params["p"] == "双顶@746"  # noqa: SLF001
    assert "FINAL" in p._ensure_client().last_sql  # noqa: SLF001


def test_get_none_semantics_three_ways():
    assert _provider([]).get("x") is None  # 查无
    assert _provider([(10, 0.9, 1)]).get("x") is None  # low_sample
    assert _provider([(500, None, 0)]).get("x") is None  # 中性 NULL


def test_get_baseline_uses_marker_id():
    p = _provider([(583517, 0.641, 0)])
    assert p.get_baseline(direction="向下") == 0.641
    assert p._ensure_client().last_params["p"] == "__baseline__"  # noqa: SLF001


def test_without_client_raises(monkeypatch):
    monkeypatch.setattr("zephyr.data.ch_writer.get_client", lambda: None)
    p = PatternWinRateProvider(client=None)
    with pytest.raises(RuntimeError, match="clickhouse-driver"):
        p.get("x")


# ── 引擎 wrapper（name-only 契约）─────────────────────────────


def test_engine_callable_maps_name_to_direction():
    captured = {}

    class _Spy(PatternWinRateProvider):
        def get(self, pattern_id, *, timeframe="day", direction="向上", fwd_window=10, regime_tag=""):
            captured = (pattern_id, direction, fwd_window, regime_tag)
            return 0.75

    rates = engine_win_rate_callable(_Spy(), fwd_window=10)
    assert rates("双底") == 0.75  # 双底→向上 查询命中
    assert rates("未知形态名") is None  # 封闭集外→None（无统计路径）


def test_engine_callable_none_for_ambiguous_names():
    rates = engine_win_rate_callable(PatternWinRateProvider(client=_FakeClient([])))
    assert rates("缠论中枢") is None  # 方向随事件变化，name-only 契约下不猜
