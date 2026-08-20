# -*- coding: utf-8 -*-
"""边界单测：停牌处理（GAP-010）

测试盘中临停/跨日停牌/复牌场景。
"""

from zephyr.ex_core.trading_halt_resolver import (
    HaltInfo,
    HaltStatus,
    HaltType,
    TradingHaltResolver,
)


class TestSuspension:
    """停牌边界测试。"""

    def test_intraday_halt_skip_order(self):
        """盘中临停票从当日目标移除不报单；持仓票保留不动等复牌。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            HaltInfo(
                symbol="600000.SH",
                is_halted=True,
                halt_type=HaltType.INTRADAY_PRICE_LIMIT,
                is_cross_day=False,
            ),
        )

        # 下单前检查：盘中临停 → 从目标移除（不报单）
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.HALTED_REMOVE_FROM_TARGET

        # 调仓过滤：从目标权重移除，不释放预占（盘中临停 10 分钟即复牌）
        filtered, actions = resolver.filter_target_weights({"600000.SH": 0.1, "000001.SZ": 0.2})
        assert "600000.SH" not in filtered
        assert filtered["000001.SZ"] == 0.2
        halt_action = next(a for a in actions if a.symbol == "600000.SH")
        assert halt_action.remove_from_target is True
        assert halt_action.release_prepaid is False

        # 持仓票盘中临停：保留不动等复牌
        assert resolver.check_position_halt("600000.SH") is HaltStatus.HALTED_KEEP_POSITION

    def test_cross_day_halt_release_preoccupation(self):
        """跨日停牌票释放资金预占额度，且幂等不重复释放。"""
        resolver = TradingHaltResolver()
        resolver.update_halt_status(
            "600000.SH",
            HaltInfo(
                symbol="600000.SH",
                is_halted=True,
                halt_type=HaltType.CROSS_DAY_REVIEW,
                is_cross_day=True,
            ),
        )

        # 持仓票跨日停牌：从目标移除 + 首次释放预占
        filtered, actions = resolver.filter_target_weights(
            {"600000.SH": 0.1},
            held_symbols={"600000.SH"},
        )
        assert "600000.SH" not in filtered
        action = next(a for a in actions if a.symbol == "600000.SH")
        assert action.status is HaltStatus.HALTED_RELEASE_PREPAID
        assert action.release_prepaid is True

        # 再次过滤：不重复释放（幂等——防止同一预占被释放两次）
        _, actions2 = resolver.filter_target_weights(
            {"600000.SH": 0.1},
            held_symbols={"600000.SH"},
        )
        action2 = next(a for a in actions2 if a.symbol == "600000.SH")
        assert action2.release_prepaid is False

        # 下单前检查：跨日停牌 → 释放预占决策
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.HALTED_RELEASE_PREPAID

    def test_resume_reevaluate(self):
        """复牌后标记 RESUMED_REEVALUATE 重新评估，清理后恢复正常。"""
        resolver = TradingHaltResolver()
        # 先跨日停牌并释放预占
        resolver.update_halt_status(
            "600000.SH",
            HaltInfo(
                symbol="600000.SH",
                is_halted=True,
                halt_type=HaltType.CROSS_DAY_REVIEW,
                is_cross_day=True,
            ),
        )
        resolver.filter_target_weights({"600000.SH": 0.1}, held_symbols={"600000.SH"})

        # 复牌（is_halted=False）
        resolver.update_halt_status(
            "600000.SH",
            HaltInfo(
                symbol="600000.SH",
                is_halted=False,
                halt_type=HaltType.CROSS_DAY_REVIEW,
            ),
        )
        filtered, actions = resolver.filter_target_weights({"600000.SH": 0.1})
        # 复牌票保留在目标中，但标记重新评估（复牌可能跌停，需策略层重估权重）
        assert filtered["600000.SH"] == 0.1
        resume_action = next(a for a in actions if a.symbol == "600000.SH")
        assert resume_action.status is HaltStatus.RESUMED_REEVALUATE

        # 清理复牌记录后：预占释放台账同步清除，恢复正常决策
        assert resolver.clear_resumed() == ["600000.SH"]
        assert resolver.check_order_allowed("600000.SH") is HaltStatus.NORMAL
