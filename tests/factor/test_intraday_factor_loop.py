# [BLUEPRINT] MOD-L02-001 | tests/factor/test_intraday_factor_loop.py
# [MODULE] tests.factor.test_intraday_factor_loop
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.core.intraday_factor_loop
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
# [A_module] module_id=MOD-L02-001 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IntradayFactorLoop 单元测试——盘中3秒因子调度循环。

覆盖：
    1. _parse_tick_hash 转换（Redis Hash → DataFrame 行）
    2. read_ticks_to_dataframe PIPELINE 批量读 + DataFrame 构造
    3. tick_cycle 执行流程（DagExecutor.execute 参数验证）
    4. start/stop 线程生命周期
    5. 错误降级（Redis 故障 / 空 tick / DAG 构建失败）
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from zephyr.factor.core.intraday_factor_loop import (
    IntradayFactorLoop,
    _parse_tick_hash,
)

# ── _parse_tick_hash 测试 ──


class TestParseTickHash:
    """Redis tick Hash → DataFrame 行字典转换。"""

    def test_full_tick(self):
        tick_hash = {"price": "12.5", "volume": "100000", "amount": "1250000.0"}
        result = _parse_tick_hash(tick_hash)
        assert result is not None
        assert result["close"] == pytest.approx(12.5)
        assert result["volume"] == 100000
        assert result["amount"] == pytest.approx(1250000.0)

    def test_empty_hash(self):
        assert _parse_tick_hash({}) is None

    def test_missing_price(self):
        tick_hash = {"volume": "100", "amount": "1000"}
        assert _parse_tick_hash(tick_hash) is None

    def test_invalid_values(self):
        tick_hash = {"price": "not_a_number", "volume": "100"}
        assert _parse_tick_hash(tick_hash) is None

    def test_zero_defaults(self):
        tick_hash = {"price": "12.5"}
        result = _parse_tick_hash(tick_hash)
        assert result is not None
        assert result["volume"] == 0
        assert result["amount"] == 0.0


# ── read_ticks_to_dataframe 测试 ──


class TestReadTicksToDataFrame:
    """PIPELINE 批量读 Redis tick → DataFrame。"""

    def test_normal_read(self):
        """正常读取 → DataFrame 含 close/volume/amount。"""
        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [
            {"price": "12.5", "volume": "100", "amount": "1250.0"},
            {"price": "8.32", "volume": "200", "amount": "1664.0"},
        ]
        mock_redis.pipeline.return_value = mock_pipe

        loop = IntradayFactorLoop(mock_redis, ["000001.SZ", "600000.SH"])
        df = loop.read_ticks_to_dataframe()

        assert not df.empty
        assert len(df) == 2
        assert "close" in df.columns
        assert df.loc["000001.SZ", "close"] == pytest.approx(12.5)
        assert df.loc["600000.SH", "close"] == pytest.approx(8.32)

    def test_empty_symbols(self):
        """空标的列表 → 空 DataFrame。"""
        mock_redis = MagicMock()
        loop = IntradayFactorLoop(mock_redis, [])
        df = loop.read_ticks_to_dataframe()
        assert df.empty

    def test_redis_failure(self):
        """Redis 故障 → 空 DataFrame（降级）。"""
        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.side_effect = ConnectionError("Redis down")
        mock_redis.pipeline.return_value = mock_pipe

        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"])
        df = loop.read_ticks_to_dataframe()
        assert df.empty

    def test_partial_empty_ticks(self):
        """部分 symbol 无 tick → 只返回有数据的 symbol。"""
        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [
            {"price": "12.5", "volume": "100", "amount": "1250.0"},
            {},  # 无 tick 数据
        ]
        mock_redis.pipeline.return_value = mock_pipe

        loop = IntradayFactorLoop(mock_redis, ["000001.SZ", "600000.SH"])
        df = loop.read_ticks_to_dataframe()
        assert len(df) == 1
        assert "000001.SZ" in df.index

    def test_uses_pipeline(self):
        """验证使用 PIPELINE（非逐条 HGETALL）。"""
        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [{"price": "1.0", "volume": "1", "amount": "1"}]
        mock_redis.pipeline.return_value = mock_pipe

        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"])
        loop.read_ticks_to_dataframe()

        mock_redis.pipeline.assert_called_once_with(transaction=False)
        assert mock_pipe.hgetall.call_count == 1  # 1 symbol = 1 HGETALL in pipeline


# ── tick_cycle 测试 ──


class TestTickCycle:
    """单次3秒周期执行流程测试。"""

    def _make_loop_with_mocks(self, symbols=None):
        """构造 mock Redis + mock DagExecutor 的 loop。"""
        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [
            {"price": "12.5", "volume": "100", "amount": "1250.0"}
        ]
        mock_redis.pipeline.return_value = mock_pipe

        mock_executor = MagicMock()
        mock_report = MagicMock()
        mock_report.results = {"momentum_20d": MagicMock()}
        mock_report.failed_factors = []
        mock_report.duration_s = 0.05
        mock_executor.execute.return_value = mock_report

        loop = IntradayFactorLoop(
            mock_redis,
            symbols or ["000001.SZ"],
            dag_executor=mock_executor,
        )
        loop._dag = MagicMock()  # 跳过真实 DAG 构建
        loop._sink = MagicMock()
        return loop, mock_executor

    def test_normal_cycle(self):
        """正常周期 → DagExecutor.execute 被调用。"""
        loop, mock_executor = self._make_loop_with_mocks()
        result = loop.tick_cycle()

        assert result > 0
        mock_executor.execute.assert_called_once()
        call_kwargs = mock_executor.execute.call_args
        # 验证传了 dag, data, mode, on_results_callback
        assert call_kwargs[1]["on_results_callback"] is loop._sink
        assert "mode" in call_kwargs[1]

    def test_empty_data_skips(self):
        """无 tick 数据 → 跳过执行。"""
        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_pipe.execute.return_value = [{}]  # 空 tick
        mock_redis.pipeline.return_value = mock_pipe

        mock_executor = MagicMock()
        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"], dag_executor=mock_executor)
        loop._dag = MagicMock()
        loop._sink = MagicMock()

        result = loop.tick_cycle()
        assert result == 0
        mock_executor.execute.assert_not_called()

    def test_executor_failure_does_not_raise(self):
        """DagExecutor 异常 → 不 raise（单周期失败不中断循环）。"""
        loop, mock_executor = self._make_loop_with_mocks()
        mock_executor.execute.side_effect = RuntimeError("compute failed")

        result = loop.tick_cycle()
        assert result == 0  # 不 raise，返回0

    def test_cycle_increments_count(self):
        """周期计数递增。"""
        loop, _ = self._make_loop_with_mocks()
        assert loop._cycle_count == 0
        loop.tick_cycle()
        assert loop._cycle_count == 1
        loop.tick_cycle()
        assert loop._cycle_count == 2


# ── start/stop 生命周期测试 ──


class TestStartStopLifecycle:
    """线程生命周期测试。"""

    def test_start_builds_dag_and_sink(self):
        """start() 构建 DAG + 创建 sink + 启动线程。"""
        mock_redis = MagicMock()
        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"])

        with patch.object(loop, "_build_dag", return_value=True) as mock_build, \
             patch("zephyr.factor.core.intraday_factor_loop.create_h1_factor_sink") as mock_sink:
            mock_sink.return_value = MagicMock()
            # 让循环立即退出（_running=False after first cycle）
            loop._cycle_seconds = 0.01
            original_start = loop.start

            # 用 patch 让 _loop 只跑一次就退出
            with patch.object(loop, "_loop", side_effect=lambda: None):
                ok = loop.start()
                assert ok is True
                mock_build.assert_called_once()
                mock_sink.assert_called_once_with(mock_redis)
                loop.stop()

    def test_start_fails_without_factors(self):
        """DAG 构建失败 → start 返回 False。"""
        mock_redis = MagicMock()
        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"])

        with patch.object(loop, "_build_dag", return_value=False):
            ok = loop.start()
            assert ok is False
            assert loop._thread is None

    def test_double_start(self):
        """重复 start → 第二次返回 True（已在运行）。"""
        mock_redis = MagicMock()
        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"])
        loop._running = True  # 模拟已在运行

        ok = loop.start()
        assert ok is True  # 不报错，直接返回

    def test_stop_joins_thread(self):
        """stop() join 线程。"""
        mock_redis = MagicMock()
        loop = IntradayFactorLoop(mock_redis, ["000001.SZ"])
        loop._running = True
        mock_thread = MagicMock()
        loop._thread = mock_thread

        loop.stop()
        assert loop._running is False
        mock_thread.join.assert_called_once_with(timeout=10)

    def test_stats(self):
        """stats() 返回运行状态。"""
        mock_redis = MagicMock()
        loop = IntradayFactorLoop(mock_redis, ["000001.SZ", "600000.SH"])
        loop._cycle_count = 5
        loop._last_error = "test error"

        stats = loop.stats()
        assert stats["cycle_count"] == 5
        assert stats["symbols"] == 2
        assert stats["last_error"] == "test error"
        assert stats["running"] is False
