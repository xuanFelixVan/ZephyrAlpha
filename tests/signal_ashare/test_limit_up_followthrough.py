# [BLUEPRINT] MOD-SIG-078 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-19 行）
# [MODULE] tests.signal_ashare.test_limit_up_followthrough
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.limit_up_followthrough
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网（ch_client 鸭子类型 SQL 子串路由）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=昨涨停今表现/炸板率统计逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-SIG-078_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-SIG-078 昨日涨停今表现+炸板率统计 单元测试（GAP-F-19，合成数据不触库）。

覆盖：封板池/炸板池分组统计（均值/中位/正负占比/最大最小）、双端榜、
市场炸板率（attempted-sealed 口径 + attempted=0 守卫）、超额收益（注入指数涨幅）、
空池降级、单腿查询异常独立降级、裸码/canonical 归一、日期校验 fail-closed、
主入口降级链、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from zephyr.signal_ashare.limit_up_followthrough import (
    FollowthroughConfig,
    PoolStock,
    compute_followthrough_stats,
    run_limit_up_followthrough,
)

# ------------------------------------------------------------------
# 合成数据
# ------------------------------------------------------------------

SEALED = [
    PoolStock(symbol="600001", name="封板A", y_close=10.0),
    PoolStock(symbol="600002", name="封板B", y_close=20.0),
    PoolStock(symbol="000001", name="封板C", y_close=15.0),
]
BROKEN = [
    PoolStock(symbol="300001", name="炸板D", y_close=30.0),
    PoolStock(symbol="300002", name="炸板E", y_close=25.0),
]
TODAY = {
    "600001": 5.0,
    "600002": -2.0,
    "000001": 3.0,
    "300001": -6.0,
    # 300002 今日缺数据 → 跳过留痕
}


def _cfg(**kw) -> FollowthroughConfig:
    return FollowthroughConfig(**kw)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def test_stats_two_pools_basic() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=BROKEN,
        today_pct=TODAY,
        breadth_attempted=40,
        breadth_sealed=30,
        config=_cfg(),
    )
    assert rep.degraded is False
    # 封板池 3 只有效
    assert rep.sealed.count == 3
    assert rep.sealed.avg_pct == pytest.approx((5.0 - 2.0 + 3.0) / 3)
    assert rep.sealed.median_pct == pytest.approx(3.0)
    assert rep.sealed.positive_ratio == pytest.approx(0.6667)
    assert rep.sealed.max_pct == pytest.approx(5.0)
    assert rep.sealed.min_pct == pytest.approx(-2.0)
    # 炸板池 1 只有效（300002 缺今日数据跳过）
    assert rep.broken.count == 1
    assert rep.broken.avg_pct == pytest.approx(-6.0)
    assert any("300002" in n for n in rep.notes)


def test_market_broken_rate() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=[],
        today_pct=TODAY,
        breadth_attempted=40,
        breadth_sealed=30,
        config=_cfg(),
    )
    # (40-30)/40 = 25%
    assert rep.market_broken_rate == pytest.approx(0.25)
    assert rep.market_attempted == 40
    assert rep.market_sealed == 30


def test_market_broken_rate_zero_attempted_guard() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=[],
        today_pct=TODAY,
        breadth_attempted=0,
        breadth_sealed=0,
        config=_cfg(),
    )
    assert rep.market_broken_rate is None
    assert any("曾涨停为 0" in n for n in rep.notes)


def test_breadth_missing_degrades_leg_not_all() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=BROKEN,
        today_pct=TODAY,
        breadth_attempted=None,
        breadth_sealed=None,
        config=_cfg(),
    )
    assert rep.market_broken_rate is None
    assert rep.sealed.count == 3  # 主池不受影响
    assert any("市场宽度" in n for n in rep.notes)


def test_excess_vs_index() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=BROKEN,
        today_pct=TODAY,
        breadth_attempted=40,
        breadth_sealed=30,
        config=_cfg(index_pct_change=1.0),
    )
    assert rep.excess_avg_pct == pytest.approx(rep.sealed.avg_pct - 1.0)


def test_empty_sealed_pool_degraded() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=[],
        broken_pool=[],
        today_pct=TODAY,
        breadth_attempted=40,
        breadth_sealed=30,
        config=_cfg(),
    )
    assert rep.degraded is True
    assert rep.sealed.count == 0


def test_top_gainers_losers() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=BROKEN,
        today_pct=TODAY,
        breadth_attempted=40,
        breadth_sealed=30,
        config=_cfg(top_n=2),
    )
    assert [d.symbol for d in rep.top_gainers] == ["600001", "000001"]
    assert [d.symbol for d in rep.top_losers] == ["300001", "600002"]
    assert rep.top_gainers[0].pool == "sealed"
    assert rep.top_losers[0].pool == "broken"


def test_canonical_symbol_normalized_to_bare() -> None:
    sealed = [PoolStock(symbol="600001.SH", name="封板A", y_close=10.0)]
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=sealed,
        broken_pool=[],
        today_pct={"600001": 5.0},
        breadth_attempted=10,
        breadth_sealed=8,
        config=_cfg(),
    )
    assert rep.sealed.count == 1
    assert rep.sealed.avg_pct == pytest.approx(5.0)


def test_invalid_date_fail_closed() -> None:
    with pytest.raises(ValueError, match="trade_date"):
        compute_followthrough_stats(
            trade_date="2026-13-01",
            prev_trade_date="2026-08-20",
            sealed_pool=SEALED,
            broken_pool=[],
            today_pct=TODAY,
            breadth_attempted=1,
            breadth_sealed=1,
            config=_cfg(),
        )
    with pytest.raises(ValueError, match="prev_trade_date"):
        compute_followthrough_stats(
            trade_date="2026-08-21",
            prev_trade_date="bad",
            sealed_pool=SEALED,
            broken_pool=[],
            today_pct=TODAY,
            breadth_attempted=1,
            breadth_sealed=1,
            config=_cfg(),
        )


def test_json_serializable() -> None:
    rep = compute_followthrough_stats(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        sealed_pool=SEALED,
        broken_pool=BROKEN,
        today_pct=TODAY,
        breadth_attempted=40,
        breadth_sealed=30,
        config=_cfg(),
    )
    json.dumps(asdict(rep), ensure_ascii=False)


# ------------------------------------------------------------------
# 主入口（假 ch_client，SQL 子串路由）
# ------------------------------------------------------------------


class _FakeClient:
    """SQL 子串路由假 client。"""

    def execute(self, sql, params=None):
        if "limit_up_down" in sql:
            return [("600001", "封板A", 10.0), ("600002", "封板B", 20.0)]
        if "stk_limit" in sql:
            return [("300001.SZ", 33.0, 30.0, 33.0)]  # 高=涨停价 收<涨停价 → 炸板
        if "market_breadth_snapshot" in sql:
            return [(50, 40, 0)]  # attempted, sealed, degraded
        if "kline_daily" in sql:
            return [("600001.SH", 5.0), ("600002.SH", -2.0), ("300001.SZ", -6.0)]
        raise AssertionError(f"未路由 SQL: {sql}")


def test_run_main_entry_with_fake_client() -> None:
    rep = run_limit_up_followthrough(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        ch_client=_FakeClient(),
        config=_cfg(),
    )
    assert rep.degraded is False
    assert rep.sealed.count == 2
    assert rep.broken.count == 1
    assert rep.market_broken_rate == pytest.approx(0.2)


def test_run_leg_failure_degrades_independently() -> None:
    class _BadClient(_FakeClient):
        def execute(self, sql, params=None):
            if "market_breadth_snapshot" in sql:
                raise RuntimeError("boom")
            return super().execute(sql, params)

    rep = run_limit_up_followthrough(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        ch_client=_BadClient(),
        config=_cfg(),
    )
    assert rep.market_broken_rate is None
    assert rep.sealed.count == 2
    assert any("market_breadth_snapshot" in n or "宽度" in n for n in rep.notes)


def test_run_no_client_degraded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("zephyr.signal_ashare.limit_up_followthrough._default_client", lambda: None)
    rep = run_limit_up_followthrough(
        trade_date="2026-08-21",
        prev_trade_date="2026-08-20",
        ch_client=None,
        config=_cfg(),
        _allow_no_client=True,
    )
    assert rep.degraded is True
