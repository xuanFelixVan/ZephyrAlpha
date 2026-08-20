# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] tests/ex_core/test_trading_halt_resolver.py
# [TTL] task_bound
# 对应: src/zephyr/ex_core/trading_halt_resolver.py
# 覆盖: gap 14 临时停牌处理（盘中临停/跨日停牌/复牌/目标过滤/预占释放）
"""TradingHaltResolver 单元测试（40_execution_broker §决策⑮ gap 14）。"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.ex_core.trading_halt_resolver import (
    HaltAction,
    HaltInfo,
    HaltStatus,
    HaltType,
    TradingHaltResolver,
)


def _make_halt_info(
    symbol: str = "600000.SH",
    is_halted: bool = True,
    halt_type: HaltType = HaltType.INTRADAY_PRICE_LIMIT,
    is_cross_day: bool = False,
    can_place_order: bool = False,
    can_cancel_order: bool = False,
) -> HaltInfo:
    return HaltInfo(
        symbol=symbol,
        is_halted=is_halted,
        halt_type=halt_type,
        halt_start=datetime(2026, 8, 10, 10, 30, tzinfo=timezone.utc),
        expected_resume=None,
        is_cross_day=is_cross_day,
        can_place_order=can_place_order,
        can_cancel_order=can_cancel_order,
    )


# ───────────────────────── 状态查询 ─────────────────────────


class TestStatusQuery:
    """停牌状态查询。"""

    def test_normal_when_no_info(self):
        """未登记的 symbol → NORMAL。"""
        resolver = TradingHaltResolver()
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.NORMAL
        assert resolver.is_halted("600000.SH") is False

    def test_normal_when_not_halted(self):
        """登记但未停牌 → NORMAL。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status("600000.SH", _make_halt_info(is_halted=False))
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.NORMAL
        assert resolver.is_halted("600000.SH") is False

    def test_intraday_halt_remove_from_target(self):
        """盘中临停 → HALTED_REMOVE_FROM_TARGET。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                halt_type=HaltType.INTRADAY_PRICE_LIMIT,
                is_cross_day=False,
            ),
        )
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.HALTED_REMOVE_FROM_TARGET

    def test_cross_day_halt_release_prepaid(self):
        """跨日停牌 → HALTED_RELEASE_PREPAID。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                halt_type=HaltType.CROSS_DAY_REVIEW,
                is_cross_day=True,
            ),
        )
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.HALTED_RELEASE_PREPAID

    def test_halted_symbols_list(self):
        """halted_symbols 返回所有停牌票。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status("600000.SH", _make_halt_info(symbol="600000.SH"))
        resolver.update_halt_status("000001.SZ", _make_halt_info(symbol="000001.SZ"))
        resolver.update_halt_status("300001.SZ", _make_halt_info(symbol="300001.SZ", is_halted=False))

        halted = resolver.halted_symbols()
        assert set(halted) == {"600000.SH", "000001.SZ"}

    def test_cross_day_halted_symbols(self):
        """cross_day_halted_symbols 只返回跨日停牌票。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=True,
            ),
        )
        resolver.update_halt_status(
            "000001.SZ",
            _make_halt_info(
                symbol="000001.SZ",
                is_cross_day=False,
            ),
        )

        cross_day = resolver.cross_day_halted_symbols()
        assert cross_day == ["600000.SH"]


# ───────────────────────── 目标过滤 ─────────────────────────


class TestFilterTargetWeights:
    """目标权重过滤。"""

    def test_normal_target_preserved(self):
        """正常票保留在目标中。"""
        resolver = TradingHaltResolver()
        targets = {"600000.SH": 0.1, "000001.SZ": 0.2}

        filtered, actions = resolver.filter_target_weights(targets)

        assert filtered == targets
        assert actions == []

    def test_intraday_halt_removed_from_target(self):
        """盘中临停票从目标移除。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=False,
            ),
        )
        targets = {"600000.SH": 0.1, "000001.SZ": 0.2}

        filtered, actions = resolver.filter_target_weights(targets)

        assert "600000.SH" not in filtered
        assert "000001.SZ" in filtered
        assert len(actions) == 1
        assert actions[0].remove_from_target is True
        assert actions[0].release_prepaid is False

    def test_cross_day_halt_removed_and_release_prepaid_for_held(self):
        """持仓票跨日停牌 → 移除目标 + 释放预占。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=True,
            ),
        )
        targets = {"600000.SH": 0.1, "000001.SZ": 0.2}

        filtered, actions = resolver.filter_target_weights(
            targets,
            held_symbols={"600000.SH"},
        )

        assert "600000.SH" not in filtered
        assert len(actions) == 1
        assert actions[0].release_prepaid is True
        assert actions[0].remove_from_target is True

    def test_cross_day_halt_no_release_for_non_held(self):
        """非持仓票跨日停牌 → 移除目标但不释放预占（无持仓可释放）。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=True,
            ),
        )
        targets = {"600000.SH": 0.1}

        filtered, actions = resolver.filter_target_weights(
            targets,
            held_symbols=set(),  # 不持仓
        )

        assert "600000.SH" not in filtered
        assert actions[0].release_prepaid is False

    def test_prepaid_released_only_once(self):
        """同一票跨日停牌，预占只释放一次（幂等）。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=True,
            ),
        )
        targets = {"600000.SH": 0.1}

        # 第一次过滤：释放预占
        _, actions1 = resolver.filter_target_weights(targets, held_symbols={"600000.SH"})
        assert actions1[0].release_prepaid is True

        # 第二次过滤：不再释放（已释放过）
        _, actions2 = resolver.filter_target_weights(targets, held_symbols={"600000.SH"})
        assert actions2[0].release_prepaid is False


# ───────────────────────── 持仓停牌 ─────────────────────────


class TestPositionHalt:
    """持仓票停牌处理。"""

    def test_intraday_keep_position(self):
        """持仓票盘中临停 → HALTED_KEEP_POSITION（不动）。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=False,
            ),
        )
        assert resolver.check_position_halt("600000.SH") is HaltStatus.HALTED_KEEP_POSITION

    def test_cross_day_release_prepaid(self):
        """持仓票跨日停牌 → HALTED_RELEASE_PREPAID。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=True,
            ),
        )
        assert resolver.check_position_halt("600000.SH") is HaltStatus.HALTED_RELEASE_PREPAID

    def test_normal_position(self):
        """未停牌 → NORMAL。"""
        resolver = TradingHaltResolver()
        assert resolver.check_position_halt("600000.SH") is HaltStatus.NORMAL


# ───────────────────────── 复牌清理 ─────────────────────────


class TestClearResumed:
    """复牌清理。"""

    def test_clear_resumed_returns_resumed_symbols(self):
        """clear_resumed 返回已复牌的 symbol。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_halted=True,
            ),
        )
        resolver.update_halt_status(
            "000001.SZ",
            _make_halt_info(
                symbol="000001.SZ",
                is_halted=False,  # 已复牌
            ),
        )

        resumed = resolver.clear_resumed()
        assert "000001.SZ" in resumed
        assert "600000.SH" not in resumed
        assert resolver.is_halted("000001.SZ") is False

    def test_resumed_after_prepaid_release_reevaluate(self):
        """跨日停牌释放预占后复牌 → 标记 RESUMED_REEVALUATE。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_cross_day=True,
            ),
        )
        targets = {"600000.SH": 0.1}
        # 第一次：跨日停牌释放预占
        resolver.filter_target_weights(targets, held_symbols={"600000.SH"})

        # 复牌
        resolver.update_halt_status(
            "600000.SH",
            _make_halt_info(
                symbol="600000.SH",
                is_halted=False,
            ),
        )

        # 第二次：应标记重新评估
        filtered, actions = resolver.filter_target_weights(targets, held_symbols={"600000.SH"})
        assert "600000.SH" in filtered  # 保留在目标
        assert any(a.status is HaltStatus.RESUMED_REEVALUATE for a in actions)
