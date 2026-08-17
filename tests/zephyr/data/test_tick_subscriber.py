# [BLUEPRINT] MOD-L00-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TESTS] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [TTL] task_bound
"""tick_subscriber 单元测试（含 Phase C: WalWriter + 批量出队 + 无锁计数）。"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import json
import logging
import queue
import threading
import time
from datetime import datetime
from decimal import Decimal
from logging.handlers import RotatingFileHandler
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psutil
import pytest

import zephyr.data.tick_subscriber as ts_module
from zephyr.data.tick_subscriber import TickSubscriber, tick_to_row, infer_market_type


def _conn(status, lip, lport, rip, rport, pid):
    """构造类 psutil.sconn 的测试桩（status/laddr/raddr/pid）。"""
    return SimpleNamespace(
        status=status,
        laddr=SimpleNamespace(ip=lip, port=lport) if lip is not None else None,
        raddr=SimpleNamespace(ip=rip, port=rport) if rip is not None else None,
        pid=pid,
    )


def _proc_with_exe(exe_path):
    """构造类 psutil.Process 的测试桩（仅 .exe()）。"""
    return SimpleNamespace(exe=lambda: exe_path)


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
        # timestamp（时区相关，仅校验非空）
        assert row[1] is not None
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
    """构造最小可测试 TickSubscriber 实例（Stage 4：用真实 __init__ 构造）。

    __init__ 所有参数可选且不导入 xtdata（延迟到 start()），故可直接 TickSubscriber()。
    仅 running 需测试覆写（__init__ 设 False，测试默认 True）。
    """
    from zephyr.data.tick_subscriber import TickSubscriber
    sub = TickSubscriber()
    sub.running = True
    return sub


class TestTickSubscriber:
    def test_callback_puts_to_queue(self):
        """QMT callback 把 tick 放入队列（list[dict] 格式，subscribe_quote 实际回调）"""
        sub = _make_sub()
        # QMT subscribe_quote 回调: tick_data 是 list[dict]
        datas = {"000001.SZ": [{"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}]}
        sub.on_tick(datas)

        assert not sub.tick_queue.empty()
        symbol, tick = sub.tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert tick["lastPrice"] == 10.5
        assert sub.received == 1  # 无锁计数

    def test_callback_handles_dict_format(self):
        """dict 格式 tick 向后兼容（subscribe_whole_quote 快照）"""
        sub = _make_sub()
        datas = {"000001.SZ": {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}}
        sub.on_tick(datas)

        assert not sub.tick_queue.empty()
        symbol, tick = sub.tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert tick["lastPrice"] == 10.5
        assert sub.received == 1

    def test_callback_handles_multi_tick_list(self):
        """list 包含多个 tick 时全部入队"""
        sub = _make_sub()
        datas = {"000001.SZ": [
            {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050},
            {"time": 1720838406000, "lastPrice": 10.6, "volume": 200, "amount": 2120},
        ]}
        sub.on_tick(datas)

        assert sub.tick_queue.qsize() == 2
        assert sub.received == 2

    def test_drain_batch_single_tick(self):
        """drain_batch 取一条 tick 交给 WalWriter（Phase C: 替代 _flush_once）"""
        sub = _make_sub()
        sub.writer = MagicMock()
        sub.writer.add.return_value = True

        sub.tick_queue.put(("000001.SZ", {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}))

        n = sub.drain_batch(timeout=0.1)
        assert n == 1
        assert sub.writer.add.called
        assert sub.written == 1

    def test_drain_batch_batch_output(self):
        """drain_batch 批量出队多个 tick，构造单个 FetchResult 交给 WalWriter（Phase C 核心改进）"""
        sub = _make_sub()
        sub.writer = MagicMock()
        sub.writer.add.return_value = True

        # 放入 3 条 tick
        for i in range(3):
            sub.tick_queue.put(("000001.SZ", {
                "time": 1720838403000 + i * 1000,
                "lastPrice": 10.5 + i,
                "volume": 100,
                "amount": 1050,
            }))

        n = sub.drain_batch(max_n=500, timeout=0.1)
        assert n == 3
        assert sub.written == 3
        # writer.add 只被调用一次（批量构造单个多行 FetchResult）
        assert sub.writer.add.call_count == 1

    def test_drain_batch_empty_returns_zero(self):
        """空队列 drain_batch 返回 0"""
        sub = _make_sub()
        sub.writer = MagicMock()
        n = sub.drain_batch(timeout=0.05)
        assert n == 0
        assert not sub.writer.add.called

    def test_drain_batch_writer_failure_counts_errors(self):
        """WalWriter.add 失败时 errors 递增"""
        sub = _make_sub()
        sub.writer = MagicMock()
        sub.writer.add.return_value = False  # 写入失败

        sub.tick_queue.put(("000001.SZ", {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}))
        n = sub.drain_batch(timeout=0.1)
        assert n == 0
        assert sub.errors == 1

    def test_stats_returns_all_fields(self):
        """stats() 返回 received/written/errors/queue_size（无锁快照）"""
        sub = _make_sub()
        sub.received = 10
        sub.written = 8
        sub.errors = 2
        sub.tick_queue.put(("s", {}))
        sub.tick_queue.put(("s", {}))

        stats = sub.stats()
        assert stats == {"received": 10, "written": 8, "errors": 2, "queue_size": 2}

    def test_stop_sets_running_false(self):
        """stop() 设置 running=False"""
        sub = _make_sub()
        sub.running = True
        sub.stop()
        assert sub.running is False


class TestWarmupLogic:
    """P0-2: 预热逻辑测试——订阅完成 + 首个 tick 收到 = ready"""

    def test_event_initially_not_set(self):
        """first_tick_received 初始未设置"""
        sub = _make_sub()
        assert not sub.first_tick_received.is_set()

    def test_first_tick_sets_event(self):
        """首个 tick 成功入队后 first_tick_received 被 set"""
        sub = _make_sub()
        datas = {"000001.SZ": [{"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}]}
        sub.on_tick(datas)
        assert sub.first_tick_received.is_set()

    def test_event_set_only_once(self):
        """Event 已 set 后后续 tick 不重复加锁（is_set 短路）"""
        sub = _make_sub()
        sub.first_tick_received.set()
        datas = {"000001.SZ": [{"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}]}
        sub.on_tick(datas)
        # 仍为 set，无异常
        assert sub.first_tick_received.is_set()
        assert sub.received == 1

    def test_event_not_set_when_not_running(self):
        """running=False 时 on_tick 不处理 tick，Event 不 set"""
        sub = _make_sub()
        sub.running = False
        datas = {"000001.SZ": [{"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}]}
        sub.on_tick(datas)
        assert not sub.first_tick_received.is_set()
        assert sub.received == 0

    def test_wait_returns_immediately_when_already_set(self):
        """Event 已 set 时 wait(timeout) 立即返回 True"""
        sub = _make_sub()
        sub.first_tick_received.set()
        assert sub.first_tick_received.wait(timeout=0.01) is True

    def test_wait_times_out_when_not_set(self):
        """Event 未 set 时 wait(timeout) 超时返回 False"""
        sub = _make_sub()
        assert sub.first_tick_received.wait(timeout=0.05) is False


class TestBackupTickSource:
    """P1-3: 备源 tick 回调 + data_source 标记"""

    def test_backup_tick_tags_data_source(self):
        """on_backup_tick 在 tick dict 中标记 _data_source='tdx_backup'"""
        sub = _make_sub()
        tick = {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}
        sub.on_backup_tick("000001.SZ", tick)
        symbol, queued_tick = sub.tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert queued_tick["_data_source"] == "tdx_backup"
        assert sub.received == 1

    def test_backup_tick_not_processed_when_not_running(self):
        """running=False 时 on_backup_tick 不入队"""
        sub = _make_sub()
        sub.running = False
        tick = {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}
        sub.on_backup_tick("000001.SZ", tick)
        assert sub.tick_queue.empty()
        assert sub.received == 0

    def test_drain_batch_extracts_backup_data_source(self):
        """drain_batch 从 tick dict 提取 _data_source 并传给 tick_to_row"""
        sub = _make_sub()
        sub.writer = MagicMock()
        sub.writer.add.return_value = True

        tick = {
            "time": 1720838403000,
            "lastPrice": 10.5,
            "volume": 100,
            "amount": 1050,
            "_data_source": "tdx_backup",
        }
        sub.tick_queue.put(("000001.SZ", tick))
        n = sub.drain_batch(timeout=0.1)
        assert n == 1
        # 验证 FetchResult 中 data_source 列为 tdx_backup
        result = sub.writer.add.call_args[0][0]
        # columns 列表中 data_source 的索引
        ds_idx = result.columns.index("data_source")
        assert result.rows[0][ds_idx] == "tdx_backup"

    def test_tick_to_row_with_custom_data_source(self):
        """tick_to_row 接受 data_source 参数"""
        tick = {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}
        row = tick_to_row("000001.SZ", tick, data_source="tdx_backup")
        assert row is not None
        # data_source 在 index 9（15字段: 0-14, data_source=9）
        assert row[9] == "tdx_backup"

    def test_tick_to_row_default_data_source(self):
        """tick_to_row 默认 data_source='miniqmt'"""
        tick = {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}
        row = tick_to_row("000001.SZ", tick)
        assert row is not None
        assert row[9] == "miniqmt"


class TestMain:
    @pytest.fixture(autouse=True)
    def _isolate_run_log(self, tmp_path, monkeypatch):
        """隔离 main() 日志落盘（#ARCH-DATA-017 裁定B 配套治本）：
        main() 无条件给 root logger 挂 RotatingFileHandler（生产 run log 路径）且不摘除——
        不隔离则同进程后续测试的 WARNING+ 日志泄漏进生产 tmp/tick_subscriber_run.log
        （2026-08-15 实证：TestQmtInstanceGuard 6 条假"QMT 实例辨识"ERROR 混入生产日志，
        干扰 D 项订阅失效取证）。修复：patch 路径到 tmp_path + 测试后摘除并 close handler。
        """
        monkeypatch.setattr(ts_module, "_RUN_LOG_PATH", tmp_path / "tick_subscriber_run.log")
        root = logging.getLogger()
        before = list(root.handlers)
        yield
        for h in list(root.handlers):
            if h not in before:
                root.removeHandler(h)
                h.close()

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


class _OldXtdata:
    """模拟旧版 xtquant：只有 subscribe_quote/unsubscribe_quote，无批量 API。

    注：unsubscribe_quote 签名为 (int seq)，此处模拟旧版逐只退订接口（已被实测
    证明签名错误、从未真正退订——治本 stop() 不再调用它）。
    """

    def __init__(self):
        self.subscribed: list[str] = []
        self.unsubscribe_quote_calls: list = []

    def subscribe_quote(self, stock_code, period="tick", callback=None):
        self.subscribed.append(stock_code)

    def unsubscribe_quote(self, seq, callback=None):
        self.unsubscribe_quote_calls.append(seq)


class TestSubscribeAllSymbols:
    """_subscribe_all_symbols 批量订阅逻辑（治本 2026-08-03：28分钟卡死→批量订阅）。"""

    def test_uses_subscribe_whole_quote_batch(self):
        """优先用 subscribe_whole_quote 批量订阅（vs 逐只 subscribe_quote）。"""
        sub = _make_sub()
        mock_xtdata = MagicMock()
        # subscribe_whole_quote 返回成功订阅的 stock_code 列表
        mock_xtdata.subscribe_whole_quote.return_value = ["000001.SZ", "600000.SH"]
        sub._xtdata = mock_xtdata  # type: ignore[attr-defined]

        count = sub._subscribe_all_symbols(["000001.SZ", "600000.SH"])

        assert count == 2
        assert "000001.SZ" in sub.subscribed_symbols
        assert "600000.SH" in sub.subscribed_symbols
        mock_xtdata.subscribe_whole_quote.assert_called_once()
        # 不应回退到逐只
        mock_xtdata.subscribe_quote.assert_not_called()

    def test_batch_size_1000_chunks(self):
        """2500 只标的 → 3 批（1000+1000+500），3 次 subscribe_whole_quote 调用。"""
        sub = _make_sub()
        mock_xtdata = MagicMock()
        mock_xtdata.subscribe_whole_quote.return_value = []  # 返回空 → best-effort 全标
        sub._xtdata = mock_xtdata

        symbols = [f"{i:06d}.SZ" for i in range(2500)]
        sub._subscribe_all_symbols(symbols)

        assert mock_xtdata.subscribe_whole_quote.call_count == 3
        assert len(sub.subscribed_symbols) == 2500

    def test_fallback_to_per_symbol_when_no_batch_api(self):
        """无 subscribe_whole_quote（旧版 xtquant）→ 回退逐只 subscribe_quote。"""
        sub = _make_sub()
        old_xtdata = _OldXtdata()  # 无 subscribe_whole_quote 属性
        sub._xtdata = old_xtdata  # type: ignore[attr-defined]

        count = sub._subscribe_all_symbols(["000001.SZ", "600000.SH"])

        assert count == 2
        assert old_xtdata.subscribed == ["000001.SZ", "600000.SH"]

    def test_empty_symbols_returns_zero(self):
        """空标的列表 → 直接返回 0，不调用任何订阅 API。"""
        sub = _make_sub()
        mock_xtdata = MagicMock()
        sub._xtdata = mock_xtdata

        count = sub._subscribe_all_symbols([])

        assert count == 0
        mock_xtdata.subscribe_whole_quote.assert_not_called()

    def test_batch_failure_continues(self):
        """某批订阅抛异常 → 记录错误继续后续批次（不中断）。"""
        sub = _make_sub()
        mock_xtdata = MagicMock()
        mock_xtdata.subscribe_whole_quote.side_effect = [
            RuntimeError("batch 1 timeout"),  # 第1批失败
            ["600000.SH"],  # 第2批成功
        ]
        sub._xtdata = mock_xtdata

        # 2 批（每批 1000）
        symbols = [f"{i:06d}.SZ" for i in range(1500)]
        sub._subscribe_all_symbols(symbols)

        # 第1批失败不中断，第2批仍被调用
        assert mock_xtdata.subscribe_whole_quote.call_count == 2
        # 第2批成功标的进入订阅集
        assert "600000.SH" in sub.subscribed_symbols

    def test_stop_uses_unsubscribe_whole_quote(self):
        """stop() 用 unsubscribe_whole_quote 批量取消（与订阅对齐）。"""
        sub = _make_sub()
        mock_xtdata = MagicMock()
        sub._xtdata = mock_xtdata
        sub._subscribed.update(["000001.SZ", "600000.SH"])

        sub.stop()

        mock_xtdata.unsubscribe_whole_quote.assert_called_once()
        # 不应调用签名错误的逐只 unsubscribe_quote
        mock_xtdata.unsubscribe_quote.assert_not_called()

    def test_stop_handles_missing_batch_unsubscribe(self):
        """无 unsubscribe_whole_quote（实测本版本）→ stop() 不崩溃、不调签名错误的
        unsubscribe_quote(symbol, callback=...)（治本：消除假退订）。

        订阅随进程退出由 xtquant 自动释放（daemon 生命周期保证）。
        """
        sub = _make_sub()
        old_xtdata = _OldXtdata()  # 无 unsubscribe_whole_quote 属性
        sub._xtdata = old_xtdata
        sub._subscribed.update(["000001.SZ", "600000.SH"])

        # stop() 不应抛异常
        sub.stop()

        # 不应调用签名错误的 unsubscribe_quote（治本：消除假退订）
        assert old_xtdata.unsubscribe_quote_calls == []


class TestQmtInstanceGuard:
    """启动守卫：辨识 xtdata 实际连接的 QMT 实例（治本 #ARCH-QMT-ENV-DISAMBIG-001）。

    主路径 TCP 对端进程辨识（ground truth），兜底 get_data_dir() 字符串匹配。
    两终端都 LISTEN 58610 时靠"已建立连接配对"唯一锁定真正服务的数据进程。
    """

    # ------------------------------------------------------------------
    # 路径分类工具
    # ------------------------------------------------------------------
    def test_classify_sim_path(self):
        """exe/datadir 含"模拟" → sim。"""
        assert TickSubscriber._classify_qmt_path(
            r"E:\国金QMT交易端模拟\bin.x64\miniquote.exe"
        ) == "sim"

    def test_classify_live_path(self):
        """exe/datadir 含"证券"且无"模拟" → live。"""
        assert TickSubscriber._classify_qmt_path(
            r"E:\国金证券QMT交易端\bin.x64\miniquote.exe"
        ) == "live"

    def test_classify_sim_priority_when_both_present(self):
        """路径同时含"模拟"和"证券" → 优先 sim（"模拟"后缀更具体）。"""
        assert TickSubscriber._classify_qmt_path(r"E:\证券模拟\x") == "sim"

    def test_classify_unknown_path(self):
        """路径既无"模拟"也无"证券" → unknown。"""
        assert TickSubscriber._classify_qmt_path(r"D:\other\bin\app.exe") == "unknown"

    # ------------------------------------------------------------------
    # TCP 主路径
    # ------------------------------------------------------------------
    def test_tcp_identifies_sim_peer(self, monkeypatch):
        """本进程连到模拟盘 miniquote（对端 exe 含"模拟"）→ sim。"""
        my_pid = os.getpid()
        conns = [
            # 本进程侧：ephemeral 41001 → 58610
            _conn("ESTABLISHED", "127.0.0.1", 41001, "127.0.0.1", 58610, my_pid),
            # 对端（模拟盘 miniquote）侧：58610 → 41001
            _conn("ESTABLISHED", "127.0.0.1", 58610, "127.0.0.1", 41001, 47052),
        ]
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": conns)
        monkeypatch.setattr(
            psutil, "Process",
            lambda pid: _proc_with_exe(r"E:\国金QMT交易端模拟\bin.x64\miniquote.exe"),
        )
        sub = _make_sub()
        sub._xtdata = MagicMock()  # 探活不会触发（首次扫描即命中）

        env = sub._verify_qmt_instance()

        assert env == "sim"

    def test_tcp_identifies_live_peer(self, monkeypatch):
        """本进程连到实盘 miniquote（对端 exe 含"证券"）→ live。"""
        my_pid = os.getpid()
        conns = [
            _conn("ESTABLISHED", "127.0.0.1", 41002, "127.0.0.1", 58610, my_pid),
            _conn("ESTABLISHED", "127.0.0.1", 58610, "127.0.0.1", 41002, 52744),
        ]
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": conns)
        monkeypatch.setattr(
            psutil, "Process",
            lambda pid: _proc_with_exe(r"E:\国金证券QMT交易端\bin.x64\miniquote.exe"),
        )
        sub = _make_sub()
        sub._xtdata = MagicMock()

        env = sub._verify_qmt_instance()

        assert env == "live"

    def test_tcp_disambiguates_two_listeners_on_same_port(self, monkeypatch):
        """两终端都 LISTEN 58610 时，靠 ESTABLISHED 配对锁定真正服务的进程。

        场景复现实测拓扑：sim miniquote(pid 47052) 与 live miniquote(pid 52744)
        都 LISTEN 0.0.0.0:58610，但 OS 只把本进程的连接路由给 live(52744)。
        若按 LISTEN 端口匹配会二义；按 ESTABLISHED 配对唯一锁定 52744→live。
        """
        my_pid = os.getpid()
        conns = [
            # 本进程侧：ephemeral 41682 → 58610
            _conn("ESTABLISHED", "127.0.0.1", 41682, "127.0.0.1", 58610, my_pid),
            # 实盘 miniquote 是真正服务端：58610 ↔ 41682
            _conn("ESTABLISHED", "127.0.0.1", 58610, "127.0.0.1", 41682, 52744),
            # 模拟盘 miniquote 也 LISTEN 58610（干扰项，但无匹配 ESTABLISHED）
            _conn("LISTEN", "0.0.0.0", 58610, None, None, 47052),
            # 模拟盘内部 IPC（与自己的 XtMiniQmt），不应被误判为 xtdata 对端
            _conn("ESTABLISHED", "127.0.0.1", 58342, "127.0.0.1", 3772, 47052),
        ]
        exe_map = {
            52744: r"E:\国金证券QMT交易端\bin.x64\miniquote.exe",   # live
            47052: r"E:\国金QMT交易端模拟\bin.x64\miniquote.exe",   # sim
        }
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": conns)
        monkeypatch.setattr(psutil, "Process", lambda pid: _proc_with_exe(exe_map[pid]))
        sub = _make_sub()
        sub._xtdata = MagicMock()

        env = sub._verify_qmt_instance()

        # 必须锁定真正服务端 52744(live)，而非 LISTEN 同端口的 47052(sim)
        assert env == "live"

    def test_tcp_no_peer_falls_back_to_datadir(self, monkeypatch):
        """无 TCP 对端连接（psutil 未发现）→ 回退 get_data_dir 字符串匹配。"""
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": [])
        sub = _make_sub()
        mock_xtdata = MagicMock()
        mock_xtdata.get_data_dir.return_value = (
            r"E:\国金QMT交易端模拟\userdata_mini\datadir"
        )
        sub._xtdata = mock_xtdata

        env = sub._verify_qmt_instance()

        assert env == "sim"
        # 探活触发一次（首次扫描无连接→探活→再扫仍无→走兜底）
        mock_xtdata.get_market_data_ex.assert_called()

    def test_tcp_peer_not_qmt_path_falls_back_to_datadir(self, monkeypatch):
        """对端进程 exe 非 QMT 路径（无模拟/证券）→ TCP 无果，回退 get_data_dir。"""
        my_pid = os.getpid()
        conns = [
            _conn("ESTABLISHED", "127.0.0.1", 41003, "127.0.0.1", 58610, my_pid),
            _conn("ESTABLISHED", "127.0.0.1", 58610, "127.0.0.1", 41003, 9999),
        ]
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": conns)
        monkeypatch.setattr(
            psutil, "Process", lambda pid: _proc_with_exe(r"C:\Windows\System32\other.exe"),
        )
        sub = _make_sub()
        mock_xtdata = MagicMock()
        mock_xtdata.get_data_dir.return_value = r"E:\国金证券QMT交易端\datadir"
        sub._xtdata = mock_xtdata

        env = sub._verify_qmt_instance()

        assert env == "live"

    # ------------------------------------------------------------------
    # datadir 兜底路径（TCP 无果时的分类）
    # ------------------------------------------------------------------
    def test_datadir_sim(self, monkeypatch):
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": [])
        sub = _make_sub()
        sub._xtdata = MagicMock()
        sub._xtdata.get_data_dir.return_value = (
            r"E:\国金QMT交易端模拟\userdata_mini\datadir"
        )

        assert sub._verify_qmt_instance() == "sim"

    def test_datadir_live(self, monkeypatch):
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": [])
        sub = _make_sub()
        sub._xtdata = MagicMock()
        sub._xtdata.get_data_dir.return_value = (
            r"E:\国金证券QMT交易端\userdata_mini\datadir"
        )

        assert sub._verify_qmt_instance() == "live"

    def test_datadir_unknown(self, monkeypatch):
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": [])
        sub = _make_sub()
        sub._xtdata = MagicMock()
        sub._xtdata.get_data_dir.return_value = r"D:\其他路径\datadir"

        assert sub._verify_qmt_instance() == "unknown"

    def test_datadir_failure_returns_unknown(self, monkeypatch):
        """TCP 无果且 get_data_dir 抛异常 → 不崩溃，返回 unknown。"""
        monkeypatch.setattr(psutil, "net_connections", lambda kind="inet": [])
        sub = _make_sub()
        sub._xtdata = MagicMock()
        sub._xtdata.get_data_dir.side_effect = RuntimeError("not connected")

        assert sub._verify_qmt_instance() == "unknown"


# ── #ARCH-DATA-017 裁定B/C/E 专项（2026-08-15 AI-TICK-001 补登记入库）──
# 3b7eae39f8 commit 自报的 16 项 python 单测为临时探针未入库，本批为持久化版本。

# 业务心跳 JSON 契约字段（deadman_switch.ps1 / start_tick_subscriber.ps1 消费面）
_BIZ_HB_CONTRACT_KEYS = {
    "ts", "pid", "started_ts", "last_tick_ts", "last_tick_age_s",
    "today_rows", "received", "written", "errors", "subscribed",
    "resub_count", "is_trading_day", "universe_retry_count",
}


class _FakeDt(datetime):
    """固定当前时刻的 datetime 替身（模块级 monkeypatch 用）。"""
    _fixed = None

    @classmethod
    def now(cls, tz=None):
        return cls._fixed


def _patch_now(monkeypatch, dt):
    """把 ts_module.datetime 钉到固定时刻。"""
    _FakeDt._fixed = dt
    monkeypatch.setattr(ts_module, "datetime", _FakeDt)


class TestBizHeartbeat:
    """裁定C：业务心跳 JSON——业务活性（last_tick_ts/today_rows）与进程活性正交。"""

    def test_payload_contract_fields(self, tmp_path, monkeypatch):
        """心跳 JSON 字段集=ps1 消费契约；原子写无 .tmp 残留。"""
        hb = tmp_path / "tick_subscriber_biz.heartbeat"
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", hb)
        sub = _make_sub()
        sub._started_ts = time.time() - 60
        sub.on_tick({"000001.SZ": {"time": 1720838403000}})
        sub.written = 10
        sub._write_biz_heartbeat()  # 首帧锚定日界基准（base=10）
        sub.written = 52  # 当日净落 42 行

        sub._write_biz_heartbeat()

        payload = json.loads(hb.read_text(encoding="utf-8"))
        assert set(payload) == _BIZ_HB_CONTRACT_KEYS
        assert payload["pid"] == os.getpid()
        assert payload["last_tick_ts"] is not None
        assert payload["last_tick_age_s"] is not None and payload["last_tick_age_s"] >= 0
        assert payload["today_rows"] == 42
        assert payload["subscribed"] == 0
        assert payload["resub_count"] == 0
        assert payload["is_trading_day"] is not None
        assert not hb.with_suffix(".tmp").exists()  # tmp→os.replace 原子写无残留

    def test_first_frame_last_tick_null(self, tmp_path, monkeypatch):
        """启动首帧（从未收到 tick）：last_tick_ts/last_tick_age_s 为 None，
        ps1 锚点走 max(started_ts, 当日09:30) 宽限路径——契约要求字段存在且为 null。"""
        hb = tmp_path / "tick_subscriber_biz.heartbeat"
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", hb)
        sub = _make_sub()
        sub._started_ts = time.time()

        sub._write_biz_heartbeat()

        payload = json.loads(hb.read_text(encoding="utf-8"))
        assert payload["last_tick_ts"] is None
        assert payload["last_tick_age_s"] is None
        assert payload["started_ts"] is not None
        assert payload["today_rows"] == 0

    def test_day_rollover_resets_today_rows(self, tmp_path, monkeypatch):
        """日界翻转：today_rows 以当日零点 written 为基准（日增量口径）。"""
        hb = tmp_path / "tick_subscriber_biz.heartbeat"
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", hb)
        sub = _make_sub()
        sub._hb_day = datetime(2026, 8, 14).date()  # 昨日锚
        sub._written = 100

        sub._write_biz_heartbeat()

        payload = json.loads(hb.read_text(encoding="utf-8"))
        assert sub._hb_day == datetime.now().date()
        assert sub._hb_day_base_written == 100
        assert payload["today_rows"] == 0

    def test_primary_and_backup_tick_both_update_last_tick(self):
        """主源/备源 tick 均刷新 last_tick_ts（备源活性同样算业务存活）。"""
        sub = _make_sub()
        assert sub._last_tick_ts == 0.0
        sub.on_tick({"000001.SZ": {"time": 1720838403000}})
        t1 = sub._last_tick_ts
        assert t1 > 0
        sub.on_backup_tick("000001.SZ", {"time": 1720838403000})
        assert sub._last_tick_ts >= t1

    def test_write_failure_non_fatal(self, tmp_path, monkeypatch):
        """心跳写出失败不阻断采集主流程（warning 吞没）。"""
        hb = tmp_path / "tick_subscriber_biz.heartbeat"
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", hb)
        monkeypatch.setattr(ts_module.os, "replace", MagicMock(side_effect=OSError("disk full")))
        sub = _make_sub()
        sub._write_biz_heartbeat()  # 不抛异常即通过


class TestTradingDayFlag:
    """裁定C：is_trading_day 由业务侧 xtdata 日历判定（fallback weekday 近似）。"""

    def test_xtdata_calendar_hit(self, monkeypatch):
        _patch_now(monkeypatch, datetime(2026, 8, 17, 10, 0))  # 周一
        day0_ms = int(datetime(2026, 8, 17).timestamp() * 1000)
        sub = _make_sub()
        sub._xtdata = SimpleNamespace(get_trading_dates=lambda mkt: [day0_ms])
        sub._refresh_trading_day_flag()
        assert sub._is_trading_day is True

    def test_xtdata_calendar_miss(self, monkeypatch):
        """日历真实但当日不在其中（节假日）→ False，不误报。"""
        _patch_now(monkeypatch, datetime(2026, 10, 1, 10, 0))  # 国庆假期
        other_ms = int(datetime(2026, 10, 9).timestamp() * 1000)
        sub = _make_sub()
        sub._xtdata = SimpleNamespace(get_trading_dates=lambda mkt: [other_ms])
        sub._refresh_trading_day_flag()
        assert sub._is_trading_day is False

    def test_xtdata_none_fallback_weekday(self, monkeypatch):
        """xtdata 未挂载 → weekday 近似（周一=True）。"""
        _patch_now(monkeypatch, datetime(2026, 8, 17, 10, 0))
        sub = _make_sub()
        sub._xtdata = None
        sub._refresh_trading_day_flag()
        assert sub._is_trading_day is True

    def test_xtdata_none_fallback_weekend(self, monkeypatch):
        """xtdata 未挂载 → weekday 近似（周六=False）。"""
        _patch_now(monkeypatch, datetime(2026, 8, 15, 10, 0))
        sub = _make_sub()
        sub._xtdata = None
        sub._refresh_trading_day_flag()
        assert sub._is_trading_day is False

    def test_xtdata_error_fallback_weekday(self, monkeypatch):
        """日历接口异常 → fallback weekday，不崩溃。"""
        _patch_now(monkeypatch, datetime(2026, 8, 15, 10, 0))  # 周六
        sub = _make_sub()
        sub._xtdata = SimpleNamespace(
            get_trading_dates=MagicMock(side_effect=RuntimeError("qmt down"))
        )
        sub._refresh_trading_day_flag()
        assert sub._is_trading_day is False


class TestMarketOpenNow:
    """裁定C：盘中窗口判定（09:30-15:00 且交易日）——告警/重订阅只在盘中生效。"""

    def test_intraday_returns_true(self, monkeypatch):
        _patch_now(monkeypatch, datetime(2026, 8, 17, 10, 0))
        sub = _make_sub()
        sub._is_trading_day = True
        assert sub._is_market_open_now() is True

    def test_preopen_returns_false(self, monkeypatch):
        _patch_now(monkeypatch, datetime(2026, 8, 17, 9, 29))
        sub = _make_sub()
        sub._is_trading_day = True
        assert sub._is_market_open_now() is False

    def test_after_close_returns_false(self, monkeypatch):
        _patch_now(monkeypatch, datetime(2026, 8, 17, 15, 1))
        sub = _make_sub()
        sub._is_trading_day = True
        assert sub._is_market_open_now() is False

    def test_non_trading_day_returns_false(self, monkeypatch):
        _patch_now(monkeypatch, datetime(2026, 8, 17, 10, 0))
        sub = _make_sub()
        sub._is_trading_day = False
        assert sub._is_market_open_now() is False


class _WatchdogXtdata:
    """看门狗测试用 xtdata 桩：捕获批量订阅回调并计数。"""

    def __init__(self):
        self.callback = None
        self.subscribe_calls = 0

    def subscribe_whole_quote(self, codes, callback=None):
        self.subscribe_calls += 1
        self.callback = callback
        return list(codes)

    def get_trading_dates(self, market):
        day0 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return [int(day0.timestamp() * 1000)]


class TestBizWatchdog:
    """裁定E：盘中无 tick 周期重订阅（治本预热后永久静默）；非盘中不重订阅。"""

    def _patch_fast_loop(self, monkeypatch, tmp_path):
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", tmp_path / "biz.heartbeat")
        monkeypatch.setattr(ts_module, "_BIZ_RESUB_AFTER_S", 0.2)
        monkeypatch.setattr(ts_module, "_BIZ_WATCHDOG_LOOP_S", 0.02)

    def test_stale_intraday_triggers_resubscribe(self, tmp_path, monkeypatch):
        """盘中 last_tick 过期 → 清订阅+重订阅；喂 tick 后判恢复退出。"""
        self._patch_fast_loop(monkeypatch, tmp_path)
        fake = _WatchdogXtdata()
        sub = _make_sub()
        sub._xtdata = fake
        sub._symbols_resolved = ["000001.SZ"]
        sub._subscribed = {"000001.SZ"}
        sub._last_tick_ts = time.time() - 100  # 盘中过期态
        sub._is_market_open_now = lambda: True

        t = threading.Thread(target=sub._biz_watchdog_loop, daemon=True)
        t.start()
        deadline = time.time() + 5
        while sub._resub_count < 1 and time.time() < deadline:
            time.sleep(0.02)
        assert sub._resub_count >= 1
        assert fake.subscribe_calls >= 1
        # 重订阅后重等首 tick（30s wait）——喂 tick 立即释放并判恢复
        fake.callback({"000001.SZ": {"time": int(time.time() * 1000)}})
        sub.running = False
        t.join(timeout=3)
        assert not t.is_alive()
        assert time.time() - sub._last_tick_ts < 5

    def test_off_hours_no_resubscribe(self, tmp_path, monkeypatch):
        """非盘中（收盘/周末/节假日）：只写心跳不重订阅。"""
        self._patch_fast_loop(monkeypatch, tmp_path)
        fake = _WatchdogXtdata()
        sub = _make_sub()
        sub._xtdata = fake
        sub._symbols_resolved = ["000001.SZ"]
        sub._last_tick_ts = time.time() - 100  # 即使过期也不重订阅
        sub._is_market_open_now = lambda: False

        t = threading.Thread(target=sub._biz_watchdog_loop, daemon=True)
        t.start()
        time.sleep(0.2)
        sub.running = False
        t.join(timeout=3)
        assert sub._resub_count == 0
        assert fake.subscribe_calls == 0
        # 心跳仍在持续写出
        assert (tmp_path / "biz.heartbeat").exists()


class _UniverseRetryXtdata(_WatchdogXtdata):
    """#117 测试桩：板块标的可配置（空列表模拟启动时 QMT 离线解析全失败）。"""

    def __init__(self, sector_symbols=None):
        super().__init__()
        self._sector_symbols = list(sector_symbols) if sector_symbols is not None else ["000001.SZ"]
        self.resolve_calls = 0

    def get_stock_list_in_sector(self, sector):
        self.resolve_calls += 1
        return list(self._sector_symbols)


class TestBizWatchdogEmptyUniverse:
    """#117（2026-08-17 实盘实证）：启动时 QMT 离线致 0 标的——看门狗盘中周期重试
    universe 解析+订阅（指数退避+留痕）；非盘中不重试。"""

    def _patch_fast_retry(self, monkeypatch, tmp_path):
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", tmp_path / "biz.heartbeat")
        monkeypatch.setattr(ts_module, "_BIZ_WATCHDOG_LOOP_S", 0.02)
        monkeypatch.setattr(ts_module, "_BIZ_UNIVERSE_RETRY_BASE_S", 0.05)
        monkeypatch.setattr(ts_module, "_BIZ_UNIVERSE_RETRY_MAX_S", 0.20)

    def test_empty_symbols_intraday_retries_universe_resolution(self, tmp_path, monkeypatch):
        """盘中 0 标的 → 重试 universe 解析成功 → 订阅 → 喂 tick 判恢复并重置退避。"""
        self._patch_fast_retry(monkeypatch, tmp_path)
        fake = _UniverseRetryXtdata(["000001.SZ"])
        sub = _make_sub()
        sub._xtdata = fake
        sub._symbols_resolved = []  # 启动时解析全失败（#117 边缘）
        sub._last_tick_ts = 0.0     # 从未收到 tick
        sub._is_market_open_now = lambda: True

        t = threading.Thread(target=sub._biz_watchdog_loop, daemon=True)
        t.start()
        deadline = time.time() + 5
        while not sub._symbols_resolved and time.time() < deadline:
            time.sleep(0.02)
        assert sub._symbols_resolved == ["000001.SZ"]
        assert fake.resolve_calls >= 1
        assert fake.subscribe_calls >= 1
        assert "000001.SZ" in sub._subscribed
        # 喂 tick 释放重等首 tick → 判恢复并重置退避计时（retry_count 累计留痕不重置）
        fake.callback({"000001.SZ": {"time": int(time.time() * 1000)}})
        deadline = time.time() + 3
        while sub._universe_retry_next_ts != 0.0 and time.time() < deadline:
            time.sleep(0.02)
        assert sub._universe_retry_next_ts == 0.0
        assert sub._universe_retry_count >= 1
        # 留痕：等下一轮心跳写出（loop 0.02s）后读取，再停线程
        deadline = time.time() + 3
        while time.time() < deadline:
            payload = json.loads((tmp_path / "biz.heartbeat").read_text(encoding="utf-8"))
            if payload["universe_retry_count"] >= 1:
                break
            time.sleep(0.02)
        assert payload["universe_retry_count"] >= 1
        sub.running = False
        t.join(timeout=3)
        assert not t.is_alive()

    def test_empty_symbols_resolution_failure_backoff(self, tmp_path, monkeypatch):
        """重解析持续 0 只（QMT 未恢复）→ 指数退避：窗口内不重复尝试、不触发订阅。"""
        self._patch_fast_retry(monkeypatch, tmp_path)
        fake = _UniverseRetryXtdata([])  # 解析持续失败
        sub = _make_sub()
        sub._xtdata = fake
        sub._symbols_resolved = []
        sub._is_market_open_now = lambda: True

        t = threading.Thread(target=sub._biz_watchdog_loop, daemon=True)
        t.start()
        deadline = time.time() + 3
        while sub._universe_retry_count < 2 and time.time() < deadline:
            time.sleep(0.02)
        first_two = sub._universe_retry_count
        assert first_two >= 2
        # 第 2 次失败后 backoff=0.10s（base 0.05×2）：短窗内不应立刻第 3 次
        time.sleep(0.04)
        assert sub._universe_retry_count <= first_two + 1
        sub.running = False
        t.join(timeout=3)
        assert fake.subscribe_calls == 0  # 解析失败不触发订阅
        assert sub._symbols_resolved == []

    def test_empty_symbols_off_hours_no_retry(self, tmp_path, monkeypatch):
        """非盘中 0 标的不重试（无 tick 推送属正常，留盘中自愈）。"""
        self._patch_fast_retry(monkeypatch, tmp_path)
        fake = _UniverseRetryXtdata(["000001.SZ"])
        sub = _make_sub()
        sub._xtdata = fake
        sub._symbols_resolved = []
        sub._is_market_open_now = lambda: False

        t = threading.Thread(target=sub._biz_watchdog_loop, daemon=True)
        t.start()
        time.sleep(0.2)
        sub.running = False
        t.join(timeout=3)
        assert sub._universe_retry_count == 0
        assert fake.resolve_calls == 0
        assert fake.subscribe_calls == 0
        # 心跳仍在持续写出（含留痕键）
        assert (tmp_path / "biz.heartbeat").exists()


class TestMainRunLog:
    """裁定B：main() RotatingFileHandler 落盘（治本 guard 未重定向 stdout/stderr 吞没）。"""

    def test_main_attaches_run_log(self, tmp_path, monkeypatch):
        run_log = tmp_path / "tick_subscriber_run.log"
        monkeypatch.setattr(ts_module, "_RUN_LOG_PATH", run_log)
        sub_instance = MagicMock()
        sub_instance.start.return_value = False
        monkeypatch.setattr(ts_module, "TickSubscriber", lambda *a, **kw: sub_instance)
        root = logging.getLogger()
        before = list(root.handlers)
        old_level = root.level
        root.setLevel(logging.INFO)  # pytest 下 basicConfig 为 no-op，需显式放行 INFO
        try:
            assert ts_module.main() == 1
            content = run_log.read_text(encoding="utf-8")
            assert "日志落盘" in content
            assert "启动失败" in content
            assert any(
                isinstance(h, RotatingFileHandler) for h in root.handlers if h not in before
            )
        finally:
            root.setLevel(old_level)
            for h in list(root.handlers):
                if h not in before:
                    root.removeHandler(h)
                    h.close()


class _FakeLinkXtdata:
    """盘中联调用 xtdata 桩：探活通过/板块列表/批量订阅捕获回调/日历含当日。"""

    def __init__(self, symbols):
        self._symbols = symbols
        self.callback = None
        self.subscribe_calls = 0
        self.unsub_calls = 0

    def get_stock_list_in_sector(self, sector):
        return list(self._symbols) if sector == "沪深A股" else []

    def get_market_data_ex(self, fields, codes, period="1m", count=1):
        return {c: [1] for c in codes}

    def subscribe_whole_quote(self, codes, callback=None):
        self.subscribe_calls += 1
        self.callback = callback
        return list(codes)

    def unsubscribe_whole_quote(self, codes):
        self.unsub_calls += 1
        return 1

    def get_trading_dates(self, market):
        day0 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return [int(day0.timestamp() * 1000)]

    def get_data_dir(self):
        return r"D:\模拟QMT\userdata_mini\datadir"


def _feed_ticks(fake_xt, n=5, interval=0.1):
    """后台喂 tick：等订阅回调就位后按 QMT 快照格式推送。"""
    deadline = time.time() + 10
    while fake_xt.callback is None and time.time() < deadline:
        time.sleep(0.02)
    for i in range(n):
        if fake_xt.callback is None:
            return
        fake_xt.callback({"000001.SZ": {
            "time": int(time.time() * 1000),
            "lastPrice": 10.5 + i * 0.01,
            "volume": 100,
            "amount": 1050.0,
            "bidPrice": [10.49],
            "askPrice": [10.51],
            "bidVol": [10],
            "askVol": [10],
        }})
        time.sleep(interval)


class TestIntradayLinkIntegration:
    """联调实证（模拟盘中订阅链路）：start→订阅→tick 流入→WAL 落行→心跳业务字段增长→stop。
    全程 fake xtdata/WalWriter，不触真 QMT/CH，不污染主仓 tmp。"""

    def test_intraday_subscription_link(self, tmp_path, monkeypatch):
        hb = tmp_path / "tick_subscriber_biz.heartbeat"
        monkeypatch.setattr(ts_module, "_BIZ_HEARTBEAT_PATH", hb)
        monkeypatch.setattr(ts_module, "_BIZ_WATCHDOG_LOOP_S", 0.05)
        monkeypatch.setattr(ts_module, "start_metrics_server", lambda *a, **kw: None)
        fake_xt = _FakeLinkXtdata(["000001.SZ"])
        monkeypatch.setitem(sys.modules, "xtquant", SimpleNamespace(xtdata=fake_xt))
        fake_writer = MagicMock()
        fake_writer.add.return_value = True
        monkeypatch.setitem(
            sys.modules, "zephyr.data.wal_writer",
            SimpleNamespace(WalWriter=lambda *a, **kw: fake_writer),
        )

        sub = ts_module.TickSubscriber()
        feeder = threading.Thread(target=_feed_ticks, args=(fake_xt,), daemon=True)
        feeder.start()
        try:
            assert sub.start() is True
            assert fake_xt.subscribe_calls >= 1

            # 轮询心跳：last_tick_ts 出现 且 today_rows 增长（WAL add 成功）
            payload = None
            deadline = time.time() + 10
            while time.time() < deadline:
                if hb.exists():
                    payload = json.loads(hb.read_text(encoding="utf-8"))
                    if payload.get("last_tick_ts") and payload.get("today_rows", 0) >= 1:
                        break
                time.sleep(0.05)

            assert payload is not None, "业务心跳未写出"
            assert set(payload) == _BIZ_HB_CONTRACT_KEYS
            assert payload["last_tick_ts"] is not None
            assert payload["today_rows"] >= 1
            assert payload["received"] >= 1
            assert payload["written"] >= 1
            assert payload["subscribed"] == 1
            assert payload["is_trading_day"] is True
            assert payload["pid"] == os.getpid()
        finally:
            sub.stop()
        assert fake_xt.unsub_calls >= 1
