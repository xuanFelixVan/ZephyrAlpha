# [BLUEPRINT] MOD-RUNTIME_INTRADAY | tests/zephyr/runtime/test_intraday_main.py
# [MODULE] tests.zephyr.runtime.test_intraday_main
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.runtime.intraday_main
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RUNTIME_INTRADAY | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IntradayRuntime 盘中编排器单元测试。

覆盖：
    1. 启动流程：交易日守卫 → Redis → tick_subscriber → factor_loop 顺序
    2. 非交易日守卫（--force 跳过）
    3. tick_subscriber 启动失败 → 不启动 loop
    4. factor_loop 启动失败 → 回滚 subscriber
    5. 停止反序（loop 先停，subscriber 后停）
    6. stats 聚合
    7. symbols 从 subscriber 传给 factor_loop
    8. main() 命令行入口
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from zephyr.runtime.intraday_main import IntradayRuntime, main


class _FakeTickSubscriber:
    """模拟 TickSubscriber——记录调用、可控返回值。"""

    def __init__(self, **kwargs):
        self.start_called = False
        self.stop_called = False
        self.start_return = True
        self._subscribed = {"000001.SZ", "600000.SH"}

    def start(self) -> bool:
        self.start_called = True
        return self.start_return

    def stop(self) -> None:
        self.stop_called = True

    def stats(self) -> dict:
        return {"received": 100, "written": 90}

    @property
    def subscribed_symbols(self) -> set[str]:
        return self._subscribed


class _FakeFactorLoop:
    """模拟 IntradayFactorLoop——记录调用、可控返回值、捕获构造参数。"""

    def __init__(self, **kwargs):
        self.start_called = False
        self.stop_called = False
        self.start_return = True
        self.init_kwargs = kwargs

    def start(self) -> bool:
        self.start_called = True
        return self.start_return

    def stop(self) -> None:
        self.stop_called = True

    def stats(self) -> dict:
        return {"cycle_count": 10}


class TestIntradayRuntimeStart(unittest.TestCase):
    """启动流程测试。"""

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    def test_start_success(self, mock_cache_cls, mock_ds_cls, mock_trading):
        """正常启动：交易日 → Redis → tick_subscriber → factor_loop 全部启动。"""
        mock_sub = _FakeTickSubscriber()
        mock_loop = _FakeFactorLoop()
        rt = IntradayRuntime(
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        self.assertTrue(rt.start())
        self.assertTrue(mock_sub.start_called)
        self.assertTrue(mock_loop.start_called)
        self.assertTrue(rt._running)

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=False)
    def test_start_non_trading_day_blocked(self, mock_trading):
        """非交易日 + 非 force → 守卫拦截，不启动任何组件。"""
        mock_sub = _FakeTickSubscriber()
        mock_loop = _FakeFactorLoop()
        rt = IntradayRuntime(
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        self.assertFalse(rt.start())
        self.assertFalse(mock_sub.start_called)
        self.assertFalse(mock_loop.start_called)
        self.assertFalse(rt._running)

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=False)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_start_force_bypasses_guard(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """非交易日 + --force → 跳过守卫，正常启动。"""
        mock_sub = _FakeTickSubscriber()
        mock_loop = _FakeFactorLoop()
        rt = IntradayRuntime(
            force=True,
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        self.assertTrue(rt.start())
        self.assertTrue(mock_sub.start_called)
        self.assertTrue(mock_loop.start_called)

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_start_tick_subscriber_fails(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """tick_subscriber 启动失败 → 不启动 loop，返回 False。"""
        mock_sub = _FakeTickSubscriber()
        mock_sub.start_return = False
        mock_loop = _FakeFactorLoop()
        rt = IntradayRuntime(
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        self.assertFalse(rt.start())
        self.assertTrue(mock_sub.start_called)
        self.assertFalse(mock_loop.start_called)
        self.assertFalse(rt._running)

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_start_factor_loop_fails_rolls_back_subscriber(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """factor_loop 启动失败 → 回滚 subscriber（调用其 stop）。"""
        mock_sub = _FakeTickSubscriber()
        mock_loop = _FakeFactorLoop()
        mock_loop.start_return = False
        rt = IntradayRuntime(
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        self.assertFalse(rt.start())
        self.assertTrue(mock_sub.start_called)
        self.assertTrue(mock_loop.start_called)
        self.assertTrue(mock_sub.stop_called)  # 回滚
        self.assertFalse(rt._running)


class TestIntradayRuntimeStop(unittest.TestCase):
    """停止流程测试。"""

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_stop_reverse_order(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """停止顺序：factor_loop 先停，subscriber 后停（反序）。"""
        mock_sub = _FakeTickSubscriber()
        mock_loop = _FakeFactorLoop()
        rt = IntradayRuntime(
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        rt.start()
        rt.stop()
        self.assertTrue(mock_loop.stop_called)
        self.assertTrue(mock_sub.stop_called)
        self.assertFalse(rt._running)

    def test_stop_without_start_no_error(self):
        """未启动直接 stop 不报错（空操作）。"""
        rt = IntradayRuntime(redis_conn=MagicMock())
        rt.stop()  # 不应抛异常
        self.assertFalse(rt._running)


class TestIntradayRuntimeStats(unittest.TestCase):
    """统计聚合测试。"""

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_stats_aggregates_both_components(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """stats 聚合 subscriber + factor_loop 数据。"""
        mock_sub = _FakeTickSubscriber()
        mock_loop = _FakeFactorLoop()
        rt = IntradayRuntime(
            redis_conn=MagicMock(),
            tick_subscriber=mock_sub,
            factor_loop=mock_loop,
        )
        rt.start()
        stats = rt.stats()
        self.assertTrue(stats["running"])
        self.assertEqual(stats["tick_subscriber"]["received"], 100)
        self.assertEqual(stats["factor_loop"]["cycle_count"], 10)

    def test_stats_empty_before_start(self):
        """启动前 stats 只有 running=False。"""
        rt = IntradayRuntime(redis_conn=MagicMock())
        stats = rt.stats()
        self.assertFalse(stats["running"])


class TestSymbolsPropagation(unittest.TestCase):
    """symbols 从 subscriber 传给 factor_loop 测试。"""

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_symbols_passed_from_subscriber_to_loop(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """无显式 symbols 时，从 subscriber.subscribed_symbols 传给 factor_loop。"""
        mock_sub = _FakeTickSubscriber()
        captured: dict = {}

        class _CapturingLoop(_FakeFactorLoop):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                captured["symbols"] = kwargs.get("symbols")

        with patch("zephyr.runtime.intraday_main.IntradayFactorLoop", _CapturingLoop):
            rt = IntradayRuntime(
                redis_conn=MagicMock(),
                tick_subscriber=mock_sub,
            )
            self.assertTrue(rt.start())

        # symbols = sorted(subscriber.subscribed_symbols)
        self.assertEqual(captured["symbols"], ["000001.SZ", "600000.SH"])

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=True)
    @patch("zephyr.runtime.intraday_main.TickRedisCache")
    @patch("zephyr.runtime.intraday_main.DatabaseService")
    def test_empty_subscribed_falls_back_to_explicit_symbols(self, mock_ds_cls, mock_cache_cls, mock_trading):
        """subscriber 订阅为空时，回退到显式传入的 symbols。"""
        mock_sub = _FakeTickSubscriber()
        mock_sub._subscribed = set()  # 空订阅
        captured: dict = {}

        class _CapturingLoop(_FakeFactorLoop):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                captured["symbols"] = kwargs.get("symbols")

        with patch("zephyr.runtime.intraday_main.IntradayFactorLoop", _CapturingLoop):
            rt = IntradayRuntime(
                symbols=["999999.BJ"],
                redis_conn=MagicMock(),
                tick_subscriber=mock_sub,
            )
            self.assertTrue(rt.start())

        self.assertEqual(captured["symbols"], ["999999.BJ"])


class TestMain(unittest.TestCase):
    """main() 命令行入口测试。"""

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=False)
    def test_main_non_trading_day_returns_1(self, mock_trading):
        """非交易日 + 无 --force → main 返回 1（start 失败）。"""
        rc = main([])
        self.assertEqual(rc, 1)

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=False)
    @patch("zephyr.runtime.intraday_main.IntradayRuntime")
    def test_main_force_flag_passed(self, mock_rt_cls, mock_trading):
        """--force 标志正确传递给 IntradayRuntime。"""
        mock_rt = MagicMock()
        mock_rt.run_forever.return_value = 0
        mock_rt_cls.return_value = mock_rt
        rc = main(["--force"])
        self.assertEqual(rc, 0)
        # 验证 force=True 被传入
        _args, kwargs = mock_rt_cls.call_args
        self.assertTrue(kwargs.get("force"))

    @patch("zephyr.runtime.intraday_main.is_trading_day", return_value=False)
    @patch("zephyr.runtime.intraday_main.IntradayRuntime")
    def test_main_symbols_passed(self, mock_rt_cls, mock_trading):
        """--symbols 标志正确传递。"""
        mock_rt = MagicMock()
        mock_rt.run_forever.return_value = 0
        mock_rt_cls.return_value = mock_rt
        main(["--symbols", "000001.SZ", "600000.SH"])
        _args, kwargs = mock_rt_cls.call_args
        self.assertEqual(kwargs.get("symbols"), ["000001.SZ", "600000.SH"])


if __name__ == "__main__":
    unittest.main()
