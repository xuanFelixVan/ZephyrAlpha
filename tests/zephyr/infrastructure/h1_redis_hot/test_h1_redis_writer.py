# [TTL] task_bound
# [TESTS] zephyr.infrastructure.h1_redis_hot.h1_redis_writer
"""H1RedisWriter 单元测试——验证因子截面批量写入 + updated_at 时戳（CP-02 治本）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

from unittest.mock import MagicMock

import pytest

from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import feature_updated_at_field
from zephyr.infrastructure.h1_redis_hot.h1_redis_writer import (
    H1RedisWriter,
    H1WriteBatchFailed,
)


class TestWriteFactorCrossSection:
    """因子截面写入 + updated_at 时戳。"""

    def test_writes_factors_and_updated_at(self):
        """写入因子字段 + _updated_at 时戳（CP-02 过期检测）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe
        mock_pipe.execute.return_value = []

        writer = H1RedisWriter(mock_conn)
        cs = {"000001.SZ": {"momentum_20d": 0.0234, "close": 12.50}}
        count = writer.write_factor_cross_section(cs)

        assert count == 1
        mock_conn.pipeline.assert_called_once_with(transaction=False)
        mock_pipe.hset.assert_called_once()
        # 校验 mapping 含 _updated_at + 因子字段
        _, kwargs = mock_pipe.hset.call_args
        mapping = kwargs["mapping"]
        assert feature_updated_at_field() in mapping
        assert "momentum_20d:v1" in mapping
        assert "close:v1" in mapping

    def test_updated_at_is_epoch_float_string(self):
        """_updated_at 值是 epoch 秒的字符串（float() 可解析，消费者做差值）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe

        writer = H1RedisWriter(mock_conn)
        writer.write_factor_cross_section({"000001.SZ": {"close": 1.0}})

        _, kwargs = mock_pipe.hset.call_args
        updated_at_str = kwargs["mapping"][feature_updated_at_field()]
        ts = float(updated_at_str)  # 不抛异常
        # 近期时间戳（>2024年）
        assert ts > 1.7e9

    def test_empty_cross_section_returns_zero(self):
        """空截面 → 返回 0，不建 pipeline。"""
        mock_conn = MagicMock()
        writer = H1RedisWriter(mock_conn)
        assert writer.write_factor_cross_section({}) == 0
        mock_conn.pipeline.assert_not_called()

    def test_skips_symbol_with_empty_factors(self):
        """空 factor dict 的 symbol 被跳过（不写其 key）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe
        mock_pipe.execute.return_value = []

        writer = H1RedisWriter(mock_conn)
        writer.write_factor_cross_section({
            "000001.SZ": {},  # 空 → 跳过
            "600000.SH": {"close": 8.0},
        })

        assert mock_pipe.hset.call_count == 1

    def test_pipeline_failure_raises_h1writebatchfailed(self):
        """pipe.execute() 抛异常 → H1WriteBatchFailed。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe
        mock_pipe.execute.side_effect = RuntimeError("Redis down")

        writer = H1RedisWriter(mock_conn)
        with pytest.raises(H1WriteBatchFailed):
            writer.write_factor_cross_section({"000001.SZ": {"close": 1.0}})

    def test_multiple_symbols_share_same_updated_at(self):
        """同一批截面所有 symbol 共享同一 updated_at 时戳（3秒周期一致性）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe

        writer = H1RedisWriter(mock_conn)
        writer.write_factor_cross_section({
            "000001.SZ": {"close": 1.0},
            "600000.SH": {"close": 2.0},
        })

        calls = mock_pipe.hset.call_args_list
        assert len(calls) == 2
        ts1 = calls[0].kwargs["mapping"][feature_updated_at_field()]
        ts2 = calls[1].kwargs["mapping"][feature_updated_at_field()]
        assert ts1 == ts2  # 同批一致

    def test_factor_version_in_field_name(self):
        """自定义 factor_version 出现在 Field 名中（窄表 DD-P3-01）。"""
        mock_conn = MagicMock()
        mock_pipe = MagicMock()
        mock_conn.pipeline.return_value = mock_pipe

        writer = H1RedisWriter(mock_conn)
        writer.write_factor_cross_section(
            {"000001.SZ": {"close": 1.0}},
            factor_version="v2",
        )

        _, kwargs = mock_pipe.hset.call_args
        assert "close:v2" in kwargs["mapping"]
