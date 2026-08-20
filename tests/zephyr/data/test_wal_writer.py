# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""wal_writer 单测（P0-1 Phase A）。

测试内容：
- 段落盘（行数阈值 / 时间阈值 / 手动 flush / 空段）
- 列过滤（有交集过滤 / CH 不可用 fallback）
- add 边界（result.error / 空 rows）
- 背压（warning 不阻断 / critical 阻断）
- drain 回灌（线程启动后自动回灌积压）
- 崩溃恢复（实例1落盘→replay_batch 回灌）
- 生命周期（start 幂等 / stop flush 残留 / stop join 线程）

不依赖真实 ClickHouse；用 tmp_path 隔离 data/local_fallback/。
"""

import json
import time
from decimal import Decimal
from unittest.mock import patch

import pytest

from src.zephyr.data import local_replay, wal_writer
from src.zephyr.data.provider_base import FetchResult
from src.zephyr.data.wal_writer import WalWriter


def _make_result(rows, columns=None, table="c1_market.tick_data", error=None):
    """构造测试用 FetchResult。"""
    cols = columns or ["trade_date", "symbol", "price"]
    return FetchResult(
        table=table,
        columns=cols,
        rows=rows,
        last_key="2026-07-22",
        elapsed_sec=0.01,
        error=error,
    )


def _setup_fallback_dir(tmp_path, monkeypatch):
    """隔离 local_replay 目录到 tmp_path。"""
    monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
    monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")


def _mock_table_cols(cols):
    """返回 mock get_insertable_columns_set 的 patcher（避免查真实 CH）。"""
    return patch(
        "src.zephyr.data.ch_writer.get_insertable_columns_set",
        return_value=set(cols),
    )


class TestSegmentFlush:
    """段落盘测试。"""

    def test_flush_by_rows(self, tmp_path, monkeypatch):
        """行数达阈值→自动落盘。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=3)
            w.add(_make_result([("d1", "s1", Decimal("1")), ("d1", "s2", Decimal("2"))]))
            assert w.pending_rows == 2  # 未达阈值
            w.add(_make_result([("d1", "s3", Decimal("3"))]))
            assert w.pending_rows == 0  # 达3行→自动落盘
            assert w.segment_count == 1
            assert w.total_segmented == 3

    def test_flush_by_time(self, tmp_path, monkeypatch):
        """时间达阈值→自动落盘。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=100, segment_max_seconds=0.3)
            w.add(_make_result([("d1", "s1", Decimal("1"))]))
            assert w.pending_rows == 1
            time.sleep(0.4)
            w.add(_make_result([("d1", "s2", Decimal("2"))]))
            # 第二次 add 时检测到超时→落盘（含两行）
            assert w.pending_rows == 0
            assert w.segment_count == 1
            assert w.total_segmented == 2

    def test_flush_empty(self, tmp_path, monkeypatch):
        """空段 flush→返回 True，不落盘。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date"]):
            w = WalWriter("c1_market.tick_data")
            assert w.flush() is True
            assert w.segment_count == 0

    def test_manual_flush_residual(self, tmp_path, monkeypatch):
        """未达阈值→手动 flush 强制落盘。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=100)
            w.add(_make_result([("d1", "s1", Decimal("1"))]))
            assert w.pending_rows == 1
            assert w.flush() is True
            assert w.pending_rows == 0
            assert w.segment_count == 1
            assert w.total_segmented == 1


class TestColumnFilter:
    """列过滤测试。"""

    def test_column_filter(self, tmp_path, monkeypatch):
        """result.columns 与表列有交集→过滤多余列。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        # 表只有 2 列，result 有 3 列→过滤掉 extra
        with _mock_table_cols(["trade_date", "symbol"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=2)
            r = _make_result(
                [("d1", "s1", Decimal("99"))],
                columns=["trade_date", "symbol", "extra"],
            )
            assert w.add(r) is True
            assert w.flush() is True
            assert w.total_segmented == 1

    def test_no_table_cols_fallback(self, tmp_path, monkeypatch):
        """CH 不可用（表列空）→不固化列，保留全部行。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(set()):  # 空集合模拟 CH 不可用
            w = WalWriter("c1_market.tick_data", segment_max_rows=2)
            r = _make_result([("d1", "s1", Decimal("1"))])
            assert w.add(r) is True
            assert w.flush() is True
            assert w.total_segmented == 1


class TestAddEdgeCases:
    """add 边界条件。"""

    def test_error_result(self, tmp_path, monkeypatch):
        """result.error→返回 False。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date"]):
            w = WalWriter("c1_market.tick_data")
            r = _make_result([("d1",)], error="boom")
            assert w.add(r) is False
            assert w.total_added == 0

    def test_empty_rows(self, tmp_path, monkeypatch):
        """空 rows→返回 True，不入段。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date"]):
            w = WalWriter("c1_market.tick_data")
            r = _make_result([])
            assert w.add(r) is True
            assert w.pending_rows == 0


class TestBackpressure:
    """背压测试（调小 wal_dir_max_bytes 避免写大文件）。"""

    def test_warning_not_blocked(self, tmp_path, monkeypatch):
        """70% 容量→warning 但不阻断写入。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        # 写 800 字节，上限 1000 → 80% > 70% warning
        (tmp_path / "junk.bin").write_bytes(b"x" * 800)
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=100, wal_dir_max_bytes=1000)
            r = _make_result([("d1", "s1", Decimal("1"))])
            assert w.add(r) is True  # warning 不阻断
            assert w.pending_rows == 1

    def test_critical_blocked(self, tmp_path, monkeypatch):
        """90% 容量→critical 阻断写入。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        # 写 950 字节，上限 1000 → 95% > 90% critical
        (tmp_path / "junk.bin").write_bytes(b"x" * 950)
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=100, wal_dir_max_bytes=1000)
            r = _make_result([("d1", "s1", Decimal("1"))])
            assert w.add(r) is False  # critical 阻断
            assert w.total_added == 0


class TestDrainAndRecovery:
    """drain + 崩溃恢复测试。"""

    def test_drain_replays_backlog(self, tmp_path, monkeypatch):
        """drain 线程启动后自动回灌积压文件。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        # 用 save_fallback 预置积压文件（确保路径格式与 replay_batch 一致）
        local_replay.save_fallback("c1_market.tick_data", None, b"d1\ts1\t1.0\n")
        assert local_replay.has_backlog()
        # 读取落盘的 tsv 文件路径（用于后续验证删除）
        entries = local_replay.read_manifest()
        tsv_path = tmp_path / entries[0]["file"]

        # 缩短 drain 间隔加速测试
        monkeypatch.setattr(wal_writer, "_DRAIN_IDLE_INTERVAL", 0.1)
        monkeypatch.setattr(wal_writer, "_DRAIN_FAST_INTERVAL", 0.05)

        with (
            _mock_table_cols(["trade_date", "symbol", "price"]),
            patch("src.zephyr.data.ch_writer.get_insert_columns", return_value="(trade_date, symbol, price)"),
            patch("src.zephyr.data.ch_writer.write_tsv", return_value=True),
        ):
            w = WalWriter("c1_market.tick_data")
            w.start()
            time.sleep(1.0)  # 等 drain 线程处理
            w.stop()
            # 验证文件被回灌删除 + manifest 清空（#ARCH-CH-023 Phase 3 bug 已修复）
            assert not tsv_path.exists()
            assert not local_replay.has_backlog()

    def test_crash_recovery(self, tmp_path, monkeypatch):
        """崩溃恢复：实例1落盘段文件→replay_batch 回灌。

        模拟进程崩溃（不启动 drain），段文件已持久化，
        重启后 replay_batch 能回灌。
        """
        _setup_fallback_dir(tmp_path, monkeypatch)
        # 实例1：写入段文件并落盘（不启动 drain = 模拟崩溃）
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w1 = WalWriter("c1_market.tick_data", segment_max_rows=100)
            w1.add(_make_result([("d1", "s1", Decimal("1")), ("d1", "s2", Decimal("2"))]))
            w1.flush()
            assert w1.segment_count == 1
            # 不调 stop()，不启动 drain → 模拟崩溃

        # 验证段文件已持久化
        manifest = tmp_path / "_manifest.jsonl"
        assert manifest.exists()
        entries = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(entries) == 1
        assert entries[0]["rows"] == 2
        tsv_path = tmp_path / entries[0]["file"]

        # 实例2：replay_batch 回灌（模拟重启后 drain）
        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=True):
            result = local_replay.replay_batch()
        assert result["replayed"] == 1  # 回灌成功
        assert result["remaining"] == 0  # 无残留（#ARCH-CH-023 Phase 3 bug 已修复）
        assert not tsv_path.exists()  # 文件已被回灌删除
        assert not manifest.exists()  # manifest 清空（无剩余条目）

    def test_stop_flushes_residual(self, tmp_path, monkeypatch):
        """stop 时 flush 残留段。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        with _mock_table_cols(["trade_date", "symbol", "price"]):
            w = WalWriter("c1_market.tick_data", segment_max_rows=100)
            w.add(_make_result([("d1", "s1", Decimal("1"))]))
            assert w.pending_rows == 1
            w.stop()
            assert w.pending_rows == 0
            assert w.segment_count == 1


class TestLifecycle:
    """生命周期测试。"""

    def test_start_idempotent(self, tmp_path, monkeypatch):
        """重复 start 不创建多个线程。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        monkeypatch.setattr(wal_writer, "_DRAIN_IDLE_INTERVAL", 0.1)
        with _mock_table_cols(["trade_date"]):
            w = WalWriter("c1_market.tick_data")
            w.start()
            t1 = w.drain_thread
            w.start()  # 重复 start
            assert w.drain_thread is t1  # 同一线程
            w.stop()

    def test_stop_joins_thread(self, tmp_path, monkeypatch):
        """stop 后线程退出。"""
        _setup_fallback_dir(tmp_path, monkeypatch)
        monkeypatch.setattr(wal_writer, "_DRAIN_IDLE_INTERVAL", 0.1)
        with _mock_table_cols(["trade_date"]):
            w = WalWriter("c1_market.tick_data")
            w.start()
            assert w.drain_thread is not None
            assert w.drain_thread.is_alive()
            w.stop()
            assert w.drain_thread is None
