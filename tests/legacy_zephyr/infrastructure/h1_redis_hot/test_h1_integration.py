"""H1 Redis 集成适配器单元测试——D-FACTOR/SIGNAL/RISK ←→ H1 接口验证。

测试范围：
    - dag_report_to_cross_section(): DagExecutionReport.results → {symbol: {factor: value}} 转换
    - write_dag_results_to_h1(): 转换 + 写入（mock Redis）
    - create_h1_factor_sink(): 回调工厂
    - create_h1_reader(): Reader 工厂

不测试实际 Redis 连接（E2E 联调已在 scripts/backup/test_h1_writer_reader_projectors.py 覆盖）。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from zephyr.infrastructure.h1_redis_hot.h1_integration import (
    create_h1_factor_sink,
    create_h1_reader,
    dag_report_to_cross_section,
    write_dag_results_to_h1,
)


@dataclass
class _MockFactorResult:
    """模拟 FactorExecutionResult（duck-typing 兼容）。"""

    factor_id: str
    success: bool
    series: pd.Series | None
    error: str = ""


class TestDagReportToCrossSection:
    """测试 dag_report_to_cross_section 转换逻辑。"""

    def test_basic_conversion(self):
        """正常情况：多个因子 × 多个标的 → 截面字典。"""
        results = {
            "momentum_20d": _MockFactorResult(
                factor_id="momentum_20d",
                success=True,
                series=pd.Series({"000001.SZ": 0.0234, "600000.SH": -0.0156}),
            ),
            "close": _MockFactorResult(
                factor_id="close",
                success=True,
                series=pd.Series({"000001.SZ": 12.50, "600000.SH": 8.32}),
            ),
        }
        cs = dag_report_to_cross_section(results)
        assert "000001.SZ" in cs
        assert "600000.SH" in cs
        assert cs["000001.SZ"]["momentum_20d"] == pytest.approx(0.0234)
        assert cs["000001.SZ"]["close"] == pytest.approx(12.50)
        assert cs["600000.SH"]["momentum_20d"] == pytest.approx(-0.0156)

    def test_skip_failed_factors(self):
        """失败因子（success=False）被跳过。"""
        results = {
            "good_factor": _MockFactorResult(
                factor_id="good_factor",
                success=True,
                series=pd.Series({"000001.SZ": 0.5}),
            ),
            "bad_factor": _MockFactorResult(
                factor_id="bad_factor",
                success=False,
                series=None,
                error="compute error",
            ),
        }
        cs = dag_report_to_cross_section(results)
        assert "000001.SZ" in cs
        assert "good_factor" in cs["000001.SZ"]
        assert "bad_factor" not in cs["000001.SZ"]

    def test_skip_nan_values(self):
        """NaN 值被跳过。"""
        results = {
            "factor_with_nan": _MockFactorResult(
                factor_id="factor_with_nan",
                success=True,
                series=pd.Series({"000001.SZ": 0.5, "600000.SH": float("nan")}),
            ),
        }
        cs = dag_report_to_cross_section(results)
        assert "000001.SZ" in cs
        assert "600000.SH" not in cs  # NaN 被跳过

    def test_skip_none_series(self):
        """series=None 的因子被跳过。"""
        results = {
            "null_factor": _MockFactorResult(
                factor_id="null_factor",
                success=True,
                series=None,
            ),
        }
        cs = dag_report_to_cross_section(results)
        assert cs == {}

    def test_empty_results(self):
        """空 results 字典 → 空截面。"""
        cs = dag_report_to_cross_section({})
        assert cs == {}


class TestWriteDagResultsToH1:
    """测试 write_dag_results_to_h1 便捷函数。"""

    def test_writes_to_redis(self):
        """正常写入——mock H1RedisWriter。"""
        results = {
            "momentum": _MockFactorResult(
                factor_id="momentum",
                success=True,
                series=pd.Series({"000001.SZ": 0.5}),
            ),
        }
        mock_conn = MagicMock()
        with patch("zephyr.infrastructure.h1_redis_hot.h1_redis_writer.H1RedisWriter") as MockWriter:
            mock_writer = MockWriter.return_value
            mock_writer.write_factor_cross_section.return_value = 1
            written = write_dag_results_to_h1(results, mock_conn)
            assert written == 1
            mock_writer.write_factor_cross_section.assert_called_once()

    def test_empty_results_returns_zero(self):
        """空 results → 返回 0，不调用 Writer。"""
        mock_conn = MagicMock()
        with patch("zephyr.infrastructure.h1_redis_hot.h1_redis_writer.H1RedisWriter") as MockWriter:
            written = write_dag_results_to_h1({}, mock_conn)
            assert written == 0
            MockWriter.return_value.write_factor_cross_section.assert_not_called()

    def test_write_failure_returns_zero(self):
        """Writer 抛异常 → 降级返回 0（不 re-raise）。"""
        results = {
            "momentum": _MockFactorResult(
                factor_id="momentum",
                success=True,
                series=pd.Series({"000001.SZ": 0.5}),
            ),
        }
        mock_conn = MagicMock()
        with patch("zephyr.infrastructure.h1_redis_hot.h1_redis_writer.H1RedisWriter") as MockWriter:
            MockWriter.return_value.write_factor_cross_section.side_effect = RuntimeError("Redis connection refused")
            written = write_dag_results_to_h1(results, mock_conn)
            assert written == 0  # 降级返回 0


class TestCreateH1FactorSink:
    """测试 create_h1_factor_sink 回调工厂。"""

    def test_returns_callable(self):
        """工厂返回可调用对象。"""
        mock_conn = MagicMock()
        sink = create_h1_factor_sink(mock_conn)
        assert callable(sink)

    def test_sink_writes_results(self):
        """回调被调用时写入 H1。"""
        results = {
            "momentum": _MockFactorResult(
                factor_id="momentum",
                success=True,
                series=pd.Series({"000001.SZ": 0.5}),
            ),
        }
        mock_conn = MagicMock()
        with patch("zephyr.infrastructure.h1_redis_hot.h1_redis_writer.H1RedisWriter") as MockWriter:
            MockWriter.return_value.write_factor_cross_section.return_value = 1
            sink = create_h1_factor_sink(mock_conn)
            sink(results)  # 不应抛异常
            MockWriter.return_value.write_factor_cross_section.assert_called_once()

    def test_sink_swallows_errors(self):
        """回调内部异常不传播（DagExecutor 依赖此行为）。"""
        results = {
            "momentum": _MockFactorResult(
                factor_id="momentum",
                success=True,
                series=pd.Series({"000001.SZ": 0.5}),
            ),
        }
        mock_conn = MagicMock()
        with patch("zephyr.infrastructure.h1_redis_hot.h1_redis_writer.H1RedisWriter") as MockWriter:
            MockWriter.return_value.write_factor_cross_section.side_effect = RuntimeError("Redis down")
            sink = create_h1_factor_sink(mock_conn)
            # 不应抛异常——write_dag_results_to_h1 内部已降级
            sink(results)


class TestCreateH1Reader:
    """测试 create_h1_reader 工厂。"""

    def test_returns_reader(self):
        """工厂返回 H1RedisReader 实例。"""
        mock_conn = MagicMock()
        reader = create_h1_reader(mock_conn)
        # 验证返回的对象有 H1RedisReader 的方法
        assert hasattr(reader, "get_online_features")
        assert hasattr(reader, "get_position")
