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
