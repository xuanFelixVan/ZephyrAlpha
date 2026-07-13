# [TESTS] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [TTL] task_bound
"""tick_subscriber 单元测试。"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import queue
import threading
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from zephyr.data.tick_subscriber import tick_to_row, infer_market_type


class TestTickToRow:
    def test_basic_tick_conversion(self):
        """正常 tick dict 转换为14字段 tuple"""
        tick = {
            "time": 1720838403000,  # 2024-07-13 10:00:03 CST (ms)
            "lastPrice": 10.5,
            "volume": 1000,
            "amount": 10500.0,
            "bidPrice": [10.49, 10.48, 10.47, 10.46, 10.45],
            "askPrice": [10.5, 10.51, 10.52, 10.53, 10.54],
            "bidVol": [500, 200, 100, 50, 50],
            "askVol": [300, 400, 100, 50, 50],
        }
        stock_code = "000001.SZ"
        row = tick_to_row(stock_code, tick)
        assert row is not None
        assert len(row) == 14
        # trade_date
        assert row[0] is not None
        # symbol
        assert row[2] == "000001"
        # market_type
        assert row[3] == "stock"
        # price
        assert row[4] == Decimal("10.5")
        # volume
        assert row[5] == 1000
        # direction
        assert row[7] == "中性盘"
        # data_source
        assert row[8] == "miniqmt"
        # bid_price (1档)
        assert row[9] == Decimal("10.49")
        # ask_price (1档)
        assert row[10] == Decimal("10.5")
        # quality_flag
        assert row[13] == 1

    def test_empty_tick_returns_none(self):
        """空 tick 返回 None"""
        assert tick_to_row("000001.SZ", {}) is None

    def test_missing_bid_ask(self):
        """缺少 bid/ask 时对应字段为 None"""
        tick = {
            "time": 1720838403000,
            "lastPrice": 10.5,
            "volume": 1000,
            "amount": 10500.0,
        }
        row = tick_to_row("600000.SH", tick)
        assert row is not None
        assert row[9] is None   # bid_price
        assert row[10] is None  # ask_price
        assert row[11] is None  # bid_volume
        assert row[12] is None  # ask_volume

    def test_etf_market_type(self):
        tick = {"time": 1720838403000, "lastPrice": 3.5, "volume": 100, "amount": 350}
        row = tick_to_row("159915.SZ", tick)
        assert row[3] == "etf"

    def test_index_market_type(self):
        tick = {"time": 1720838403000, "lastPrice": 3000, "volume": 0, "amount": 0}
        row = tick_to_row("000300.SH", tick)
        assert row[3] == "index"


class TestInferMarketType:
    def test_sh_stock(self):
        assert infer_market_type("600000.SH") == "stock"

    def test_sz_stock(self):
        assert infer_market_type("000001.SZ") == "stock"

    def test_star(self):
        assert infer_market_type("688001.SH") == "stock"

    def test_etf(self):
        assert infer_market_type("159915.SZ") == "etf"

    def test_index_sh(self):
        assert infer_market_type("000300.SH") == "index"

    def test_index_sz(self):
        assert infer_market_type("399001.SZ") == "index"

    def test_bj(self):
        assert infer_market_type("430047.BJ") == "stock_bj"


class TestTickSubscriber:
    def test_callback_puts_to_queue(self):
        """QMT callback 把 tick 放入队列"""
        from zephyr.data.tick_subscriber import TickSubscriber
        sub = TickSubscriber.__new__(TickSubscriber)
        sub._tick_queue = queue.Queue()
        sub._running = True
        sub._stats = {"received": 0, "written": 0, "errors": 0}
        sub._lock = threading.Lock()

        datas = {"000001.SZ": {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}}
        TickSubscriber._on_tick(sub, datas)

        assert not sub._tick_queue.empty()
        symbol, tick = sub._tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert tick["lastPrice"] == 10.5
        assert sub._stats["received"] == 1

    def test_flush_thread_processes_queue(self):
        """flush 线程从队列取数据，调用 BufferedWriter"""
        from zephyr.data.tick_subscriber import TickSubscriber
        sub = TickSubscriber.__new__(TickSubscriber)
        sub._tick_queue = queue.Queue()
        sub._running = True
        sub._stats = {"received": 0, "written": 0, "errors": 0}
        sub._lock = threading.Lock()
        sub._writer = MagicMock()
        sub._writer.add.return_value = True

        # 放入一条 tick
        sub._tick_queue.put(("000001.SZ", {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}))

        # 运行一次 flush 循环（timeout=0.1 取不到就退出）
        sub._flush_once(timeout=0.1)

        # 验证 BufferedWriter.add 被调用
        assert sub._writer.add.called
        assert sub._stats["written"] == 1

    def test_stop_sets_running_false(self):
        """stop() 设置 _running=False"""
        from zephyr.data.tick_subscriber import TickSubscriber
        sub = TickSubscriber.__new__(TickSubscriber)
        sub._running = True
        sub._tick_queue = queue.Queue()
        sub._flush_thread = None
        sub._xtdata = None
        sub._subscribed = set()
        sub._stats = {"received": 0, "written": 0, "errors": 0}
        TickSubscriber.stop(sub)
        assert sub._running is False


class TestMain:
    def test_main_returns_zero_on_keyboard_interrupt(self, monkeypatch):
        """main() 捕获 KeyboardInterrupt 返回 0"""
        import zephyr.data.tick_subscriber as ts_module

        sub_instance = MagicMock()
        sub_instance.start.return_value = True
        sub_instance.stats.return_value = {"received": 0, "written": 0, "errors": 0}

        def fake_sleep(*args):
            raise KeyboardInterrupt()

        monkeypatch.setattr("time.sleep", fake_sleep)
        monkeypatch.setattr(ts_module, "TickSubscriber", lambda *a, **kw: sub_instance)

        exit_code = ts_module.main()
        assert exit_code == 0
        sub_instance.stop.assert_called_once()

    def test_main_returns_one_on_start_failure(self, monkeypatch):
        """start() 失败返回 1"""
        import zephyr.data.tick_subscriber as ts_module

        sub_instance = MagicMock()
        sub_instance.start.return_value = False

        monkeypatch.setattr(ts_module, "TickSubscriber", lambda *a, **kw: sub_instance)

        exit_code = ts_module.main()
        assert exit_code == 1
