# [BLUEPRINT] MOD-L00-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psutil

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
