# [TESTS] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [TTL] task_bound
"""tick_subscriber 单元测试（含 Phase C: WalWriter + 批量出队 + 无锁计数）。"""
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
        """正常 tick dict 转换为15字段 tuple（P0-1: 新增 recorded_time）"""
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
        assert len(row) == 15
        # trade_date
        assert row[0] is not None
        # timestamp
        assert row[1] == "2024-07-13 10:00:03"
        # recorded_time (P0-1 新增，格式校验)
        assert row[2] is not None
        assert isinstance(row[2], str)
        # symbol
        assert row[3] == "000001"
        # market_type
        assert row[4] == "stock"
        # price
        assert row[5] == Decimal("10.5")
        # volume
        assert row[6] == 1000
        # direction
        assert row[8] == "中性盘"
        # data_source
        assert row[9] == "miniqmt"
        # bid_price (1档)
        assert row[10] == Decimal("10.49")
        # ask_price (1档)
        assert row[11] == Decimal("10.5")
        # quality_flag
        assert row[14] == 1

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
        assert row[10] is None  # bid_price
        assert row[11] is None  # ask_price
        assert row[12] is None  # bid_volume
        assert row[13] is None  # ask_volume

    def test_etf_market_type(self):
        tick = {"time": 1720838403000, "lastPrice": 3.5, "volume": 100, "amount": 350}
        row = tick_to_row("159915.SZ", tick)
        assert row[4] == "etf"

    def test_index_market_type(self):
        tick = {"time": 1720838403000, "lastPrice": 3000, "volume": 0, "amount": 0}
        row = tick_to_row("000300.SH", tick)
        assert row[4] == "index"


class TestInferMarketType:
    def test_sh_stock(self):
        assert infer_market_type("600000.SH") == "stock"

    def test_sz_stock(self):
        assert infer_market_type("000001.SZ") == "stock"

    def test_star(self):
        assert infer_market_type("688001.SH") == "stock"

    def test_etf(self):
        assert infer_market_type("159915.SZ") == "etf"

    def test_etf_sh_51_prefix(self):
        assert infer_market_type("510300.SH") == "etf"

    def test_lof_sz_16_prefix(self):
        assert infer_market_type("161725.SZ") == "lof"

    def test_lof_sz_18_prefix(self):
        assert infer_market_type("184801.SZ") == "lof"

    def test_lof_sh_501_prefix(self):
        assert infer_market_type("501000.SH") == "lof"

    def test_cb_sz_12_prefix(self):
        assert infer_market_type("113001.SZ") == "cb"

    def test_cb_sz_11_prefix(self):
        assert infer_market_type("110064.SZ") == "cb"

    def test_index_sh(self):
        assert infer_market_type("000300.SH") == "index"

    def test_index_sz(self):
        assert infer_market_type("399001.SZ") == "index"

    def test_index_880(self):
        assert infer_market_type("880001.SH") == "index"

    def test_bj(self):
        assert infer_market_type("430047.BJ") == "stock_bj"


def _make_sub():
    """构造最小可测试 TickSubscriber 实例（绕过 __init__ 的 xtdata 依赖）。"""
    from zephyr.data.tick_subscriber import TickSubscriber
    sub = TickSubscriber.__new__(TickSubscriber)
    sub._tick_queue = queue.Queue()
    sub._running = True
    sub._received = 0
    sub._written = 0
    sub._errors = 0
    sub._writer = None
    sub._flush_thread = None
    sub._xtdata = None
    sub._subscribed = set()
    sub._heartbeat = None  # P2-8: 心跳集成——_make_sub 须与 __init__ 属性集对齐
    return sub


class TestTickSubscriber:
    def test_callback_puts_to_queue(self):
        """QMT callback 把 tick 放入队列（list[dict] 格式，subscribe_quote 实际回调）"""
        sub = _make_sub()
        # QMT subscribe_quote 回调: tick_data 是 list[dict]
        datas = {"000001.SZ": [{"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}]}
        sub._on_tick(datas)

        assert not sub._tick_queue.empty()
        symbol, tick = sub._tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert tick["lastPrice"] == 10.5
        assert sub._received == 1  # 无锁计数

    def test_callback_handles_dict_format(self):
        """dict 格式 tick 向后兼容（subscribe_whole_quote 快照）"""
        sub = _make_sub()
        datas = {"000001.SZ": {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}}
        sub._on_tick(datas)

        assert not sub._tick_queue.empty()
        symbol, tick = sub._tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert tick["lastPrice"] == 10.5
        assert sub._received == 1

    def test_callback_handles_multi_tick_list(self):
        """list 包含多个 tick 时全部入队"""
        sub = _make_sub()
        datas = {"000001.SZ": [
            {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050},
            {"time": 1720838406000, "lastPrice": 10.6, "volume": 200, "amount": 2120},
        ]}
        sub._on_tick(datas)

        assert sub._tick_queue.qsize() == 2
        assert sub._received == 2

    def test_drain_batch_single_tick(self):
        """_drain_batch 取一条 tick 交给 WalWriter（Phase C: 替代 _flush_once）"""
        sub = _make_sub()
        sub._writer = MagicMock()
        sub._writer.add.return_value = True

        sub._tick_queue.put(("000001.SZ", {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}))

        n = sub._drain_batch(timeout=0.1)
        assert n == 1
        assert sub._writer.add.called
        assert sub._written == 1

    def test_drain_batch_batch_output(self):
        """_drain_batch 批量出队多个 tick，构造单个 FetchResult 交给 WalWriter（Phase C 核心改进）"""
        sub = _make_sub()
        sub._writer = MagicMock()
        sub._writer.add.return_value = True

        # 放入 3 条 tick
        for i in range(3):
            sub._tick_queue.put(("000001.SZ", {
                "time": 1720838403000 + i * 1000,
                "lastPrice": 10.5 + i,
                "volume": 100,
                "amount": 1050,
            }))

        n = sub._drain_batch(max_n=500, timeout=0.1)
        assert n == 3
        assert sub._written == 3
        # writer.add 只被调用一次（批量构造单个多行 FetchResult）
        assert sub._writer.add.call_count == 1

    def test_drain_batch_empty_returns_zero(self):
        """空队列 _drain_batch 返回 0"""
        sub = _make_sub()
        sub._writer = MagicMock()
        n = sub._drain_batch(timeout=0.05)
        assert n == 0
        assert not sub._writer.add.called

    def test_drain_batch_writer_failure_counts_errors(self):
        """WalWriter.add 失败时 errors 递增"""
        sub = _make_sub()
        sub._writer = MagicMock()
        sub._writer.add.return_value = False  # 写入失败

        sub._tick_queue.put(("000001.SZ", {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}))
        n = sub._drain_batch(timeout=0.1)
        assert n == 0
        assert sub._errors == 1

    def test_stats_returns_all_fields(self):
        """stats() 返回 received/written/errors/queue_size（无锁快照）"""
        sub = _make_sub()
        sub._received = 10
        sub._written = 8
        sub._errors = 2
        sub._tick_queue.put(("s", {}))
        sub._tick_queue.put(("s", {}))

        stats = sub.stats()
        assert stats == {"received": 10, "written": 8, "errors": 2, "queue_size": 2}

    def test_stop_sets_running_false(self):
        """stop() 设置 _running=False"""
        sub = _make_sub()
        sub._running = True
        sub.stop()
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
