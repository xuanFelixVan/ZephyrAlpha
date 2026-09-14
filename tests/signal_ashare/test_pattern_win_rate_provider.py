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


# ── W-C2：Wilson 下界口径（消费班方案 v1.0 挖矿 M1） ─────────────────────────


def test_wilson_lower_bound_known_value():
    """n=100 p=0.62 的 Wilson 95% LB≈0.522（教科书值带内）。"""
    from zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider import (
        _wilson_lower_bound,
    )

    lb = _wilson_lower_bound(0.62, 100)
    assert 0.51 <= lb <= 0.53
    assert lb < 0.62  # LB 恒 ≤ raw


def test_wilson_monotone_in_sample_size():
    """样本越大 LB 越贴近 raw；n=0 零信任。"""
    from zephyr.signal_ashare.strategy_signal.pattern_win_rate_provider import (
        _wilson_lower_bound,
    )

    assert _wilson_lower_bound(0.62, 1000) > _wilson_lower_bound(0.62, 100)
    assert _wilson_lower_bound(0.62, 0) == 0.0


def test_get_conservative_wilson_and_none_paths():
    """保守口径：有统计=Wilson LB；low_sample/查无/NULL→None。"""
    p = _provider([(500, 0.72, 0)])
    lb = p.get_conservative("双顶@746", direction="向下", fwd_window=10)
    assert lb is not None and 0.66 <= lb <= 0.72
    p2 = _provider([(8, 0.9, 1)])
    assert p2.get_conservative("x") is None  # low_sample
    p3 = _provider([])
    assert p3.get_conservative("x") is None  # 查无
    p4 = _provider([(100, None, 0)])
    assert p4.get_conservative("x") is None  # NULL


def test_get_detail_returns_full_row():
    """get_detail 原样返回行字段（审计快照用），查无=None。"""
    p = _provider([(500, 0.72, 0)])
    d = p.get_detail("双顶@746", direction="向下", fwd_window=10)
    assert d == {"n_events": 500, "hit_rate": 0.72, "low_sample": 0}
    assert _provider([]).get_detail("不存在") is None  # 查无（fake 按行集应答）
