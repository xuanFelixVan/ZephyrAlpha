# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.pf_core.test_strategy_runner_tick
# [DOMAIN] D_PF_CORE
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_STRATEGY_RUNNER_TICK | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""StrategyRunner.run_tick_backtest 单元测试（路径 A：日频信号 × tick 撮合）。

聚焦 _build_tick_callback 的节奏逻辑——这是路径 A 集成的核心决策点：
  - 调仓日开盘后第一个有效 tick（09:30+）返回当日目标权重
  - 盘前 tick（<09:30）返回空（EDE 层 last_price<=0 守卫亦会跳过）
  - 当日已 fired 后的盘中 tick 返回空（每日只触发一次，避免每 tick 走撮合）
  - 非调仓日（不在 weight_panel.index）返回空
  - 第二交易日开盘再次触发（ffill 权重，EDE 算 delta=0 不下单）
  - 权重为 0 的 symbol 被过滤

时区转换（UTC→北京）由 provider 层治本（见 smoke_test_tick_data 实证），
last_price<=0 守卫由 EDE on_tick 保证，此处不重复测。
端到端验证见 scripts/tests/smoke_test_tick_backtest.py（真实 QMT）。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner


@dataclass
class _FakeEvent:
    """模拟 TickEvent，仅含 callback 依赖的字段。"""

    timestamp: datetime
    symbol: str = "600000.SH"
    tick_data: object = None
    sequence: int = 1


def _make_weight_panel() -> pd.DataFrame:
    """两交易日权重面板：调仓日 0.5，次日 ffill 0.5。"""
    return pd.DataFrame(
        {"600000.SH": [0.5, 0.5]},
        index=pd.DatetimeIndex([pd.Timestamp("2026-07-23"), pd.Timestamp("2026-07-24")], name="date"),
    )


class TestBuildTickCallback:
    """_build_tick_callback 节奏逻辑。"""

    def test_rebalance_day_open_tick_returns_weights(self) -> None:
        """调仓日 09:30 开盘 tick → 返回目标权重。"""
        cb = StrategyRunner._build_tick_callback(_make_weight_panel())
        event = _FakeEvent(timestamp=datetime(2026, 7, 23, 9, 30, 0))
        assert cb(event) == {"600000.SH": 0.5}

    def test_pre_market_tick_returns_empty(self) -> None:
        """盘前 09:20 tick（<09:30）→ 返回空，不触发调仓。"""
        cb = StrategyRunner._build_tick_callback(_make_weight_panel())
        event = _FakeEvent(timestamp=datetime(2026, 7, 23, 9, 20, 0))
        assert cb(event) == {}

    def test_intraday_tick_after_fire_returns_empty(self) -> None:
        """当日开盘已 fired 后，盘中 10:00 tick → 返回空。"""
        cb = StrategyRunner._build_tick_callback(_make_weight_panel())
        open_ev = _FakeEvent(timestamp=datetime(2026, 7, 23, 9, 30, 0))
        intraday_ev = _FakeEvent(timestamp=datetime(2026, 7, 23, 10, 0, 0))
        assert cb(open_ev) == {"600000.SH": 0.5}
        assert cb(intraday_ev) == {}

    def test_non_rebalance_day_returns_empty(self) -> None:
        """不在 weight_panel.index 的日期 → 返回空。"""
        cb = StrategyRunner._build_tick_callback(_make_weight_panel())
        event = _FakeEvent(timestamp=datetime(2026, 7, 25, 9, 30, 0))
        assert cb(event) == {}

    def test_second_day_open_fires_again(self) -> None:
        """第二交易日开盘 → 再次触发（ffill 权重，EDE 算 delta=0 不下单）。"""
        cb = StrategyRunner._build_tick_callback(_make_weight_panel())
        cb(_FakeEvent(timestamp=datetime(2026, 7, 23, 9, 30, 0)))
        event = _FakeEvent(timestamp=datetime(2026, 7, 24, 9, 30, 0))
        assert cb(event) == {"600000.SH": 0.5}

    def test_zero_weight_filtered(self) -> None:
        """权重为 0 的 symbol 被过滤，不出现在返回 dict。"""
        wp = pd.DataFrame(
            {"600000.SH": [0.5], "000001.SZ": [0.0]},
            index=pd.DatetimeIndex([pd.Timestamp("2026-07-23")], name="date"),
        )
        cb = StrategyRunner._build_tick_callback(wp)
        event = _FakeEvent(timestamp=datetime(2026, 7, 23, 9, 30, 0))
        result = cb(event)
        assert "600000.SH" in result
        assert "000001.SZ" not in result

    def test_empty_weight_panel_returns_empty_callback(self) -> None:
        """空 weight_panel → callback 对任何 tick 都返回空。"""
        empty_wp = pd.DataFrame()
        cb = StrategyRunner._build_tick_callback(empty_wp)
        event = _FakeEvent(timestamp=datetime(2026, 7, 23, 9, 30, 0))
        assert cb(event) == {}
