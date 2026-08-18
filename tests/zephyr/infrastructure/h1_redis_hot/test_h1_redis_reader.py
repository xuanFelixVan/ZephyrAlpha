# [TTL] task_bound
# [TESTS] zephyr.infrastructure.h1_redis_hot.h1_redis_reader
"""H1RedisReader 单元测试——验证 get_online_features + get_feature_updated_at（CP-02 治本）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

from unittest.mock import MagicMock

import pytest

from zephyr.infrastructure.h1_redis_hot.h1_redis_reader import (
    H1RedisReader,
    H1RedisUnavailable,
)


class TestGetOnlineFeatures:
    """因子截面读取。"""

    def test_reads_factors(self):
        mock_conn = MagicMock()
        mock_conn.hmget.return_value = ["0.0234", "12.50"]

        reader = H1RedisReader(mock_conn)
        result = reader.get_online_features("000001.SZ", ["momentum_20d", "close"])

        assert result == {"momentum_20d": pytest.approx(0.0234), "close": pytest.approx(12.50)}

    def test_skips_missing_factors(self):
        mock_conn = MagicMock()
        mock_conn.hmget.return_value = [None, "12.50"]  # 第一个缺失

        reader = H1RedisReader(mock_conn)
        result = reader.get_online_features("000001.SZ", ["missing", "close"])

        assert "missing" not in result
        assert result["close"] == pytest.approx(12.50)

    def test_redis_failure_raises_h1redisunavailable(self):
        """Redis 操作失败 → H1RedisUnavailable（调用方触发 CP-02 降级）。"""
        mock_conn = MagicMock()
        mock_conn.hmget.side_effect = RuntimeError("Redis timeout")

        reader = H1RedisReader(mock_conn)
        with pytest.raises(H1RedisUnavailable):
            reader.get_online_features("000001.SZ", ["close"])


class TestGetFeatureUpdatedAt:
    """updated_at 时戳读取（CP-02 时效判定核心）。"""

    def test_returns_epoch_float(self):
        """正常读取 → 返回 epoch 秒 float。"""
        mock_conn = MagicMock()
        mock_conn.hget.return_value = "1785725958.123"

        reader = H1RedisReader(mock_conn)
        ts = reader.get_feature_updated_at("000001.SZ")

        assert ts == pytest.approx(1785725958.123)

    def test_returns_none_when_missing(self):
        """无 _updated_at 字段 → None（数据未写入）。"""
        mock_conn = MagicMock()
        mock_conn.hget.return_value = None

        reader = H1RedisReader(mock_conn)
        assert reader.get_feature_updated_at("000001.SZ") is None

    def test_returns_none_when_empty(self):
        """空字符串 → None。"""
        mock_conn = MagicMock()
        mock_conn.hget.return_value = ""

        reader = H1RedisReader(mock_conn)
        assert reader.get_feature_updated_at("000001.SZ") is None

    def test_returns_none_on_invalid_value(self):
        """非数字字符串 → None（_parse_float 容错）。"""
        mock_conn = MagicMock()
        mock_conn.hget.return_value = "not-a-number"

        reader = H1RedisReader(mock_conn)
        assert reader.get_feature_updated_at("000001.SZ") is None

    def test_redis_failure_raises_h1redisunavailable(self):
        """Redis 操作失败 → H1RedisUnavailable。"""
        mock_conn = MagicMock()
        mock_conn.hget.side_effect = RuntimeError("Redis timeout")

        reader = H1RedisReader(mock_conn)
        with pytest.raises(H1RedisUnavailable):
            reader.get_feature_updated_at("000001.SZ")

    def test_uses_correct_field_name(self):
        """验证读取 _updated_at 字段（与 Writer 写入对齐——字段名一致是治本关键）。"""
        from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import (
            feature_updated_at_field,
        )

        mock_conn = MagicMock()
        mock_conn.hget.return_value = None

        reader = H1RedisReader(mock_conn)
        reader.get_feature_updated_at("000001.SZ")

        # 校验 hget 的第二个位置参数是 _updated_at（与 Writer 写入字段对齐）
        args = mock_conn.hget.call_args.args
        assert args[1] == feature_updated_at_field()
