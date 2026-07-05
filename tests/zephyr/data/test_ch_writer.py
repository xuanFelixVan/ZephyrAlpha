"""ch_writer 单测（MOD-L00-004 阶段2）。

测试内容：
- tsv_escape（纯函数）
- write_tsv（mock _wsl_ch）
- write_result（mock _wsl_ch + FetchResult）
- delete_where（mock _wsl_ch）
- query（mock _wsl_ch）
- _get_insert_columns（mock query）

不依赖真实 WSL/clickhouse-client，用 unittest.mock.patch 替换 _wsl_ch。
"""
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from src.zephyr.data.ch_writer import (
    tsv_escape,
    write_tsv,
    write_result,
    delete_where,
    query,
    _get_insert_columns,
)
from src.zephyr.data.provider_base import FetchResult


class TestTsvEscape:
    """tsv_escape 纯函数测试。"""

    def test_none(self):
        assert tsv_escape(None) == "\\N"

    def test_nan(self):
        assert tsv_escape(float("nan")) == "\\N"

    def test_int(self):
        assert tsv_escape(42) == "42"

    def test_float(self):
        assert tsv_escape(3.14) == "3.14"

    def test_string(self):
        assert tsv_escape("hello") == "hello"

    def test_string_with_tab(self):
        """制表符替换为空格。"""
        assert tsv_escape("a\tb") == "a b"

    def test_string_with_newline(self):
        """换行符替换为空格。"""
        assert tsv_escape("a\nb") == "a b"

    def test_string_with_backslash(self):
        """反斜杠转义。"""
        assert tsv_escape("a\\b") == "a\\\\b"

    def test_empty_string(self):
        assert tsv_escape("") == ""

    def test_bool_true(self):
        assert tsv_escape(True) == "True"


class TestQuery:
    """query 函数测试（mock _wsl_ch）。"""

    def test_query_success(self):
        """成功查询返回 stdout。"""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = b"col1\tcol2\n"
        mock_proc.stderr = b""
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc):
            result = query("SELECT 1")
        assert result == "col1\tcol2\n"

    def test_query_failure(self):
        """查询失败返回空字符串。"""
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = b""
        mock_proc.stderr = b"Table not found"
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc):
            result = query("SELECT * FROM nonexistent")
        assert result == ""

    def test_query_timeout(self):
        """超时返回空字符串。"""
        with patch(
            "src.zephyr.data.ch_writer._wsl_ch",
            side_effect=subprocess.TimeoutExpired(cmd="wsl", timeout=1),
        ):
            result = query("SELECT 1")
        assert result == ""


class TestWriteTsv:
    """write_tsv 函数测试（mock _wsl_ch）。"""

    def test_write_success(self):
        """成功写入返回 True。"""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = b""
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc) as mock_ch:
            ok = write_tsv("c1_market.kline_daily", "(col1, col2)", b"v1\tv2\n")
        assert ok is True
        mock_ch.assert_called_once()
        # 验证 SQL 包含表名和列
        args = mock_ch.call_args[0][0]  # 第一个位置参数是 args list
        assert any("c1_market.kline_daily" in a for a in args)

    def test_write_empty_data(self):
        """空数据返回 False。"""
        with patch("src.zephyr.data.ch_writer._wsl_ch") as mock_ch:
            ok = write_tsv("c1_market.kline_daily", "(col1)", b"")
        assert ok is False
        mock_ch.assert_not_called()

    def test_write_failure(self):
        """写入失败返回 False。"""
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = b"Too many parts"
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc):
            ok = write_tsv("c1_market.kline_daily", "(col1)", b"v1\n")
        assert ok is False

    def test_write_timeout(self):
        """超时返回 False。"""
        with patch(
            "src.zephyr.data.ch_writer._wsl_ch",
            side_effect=subprocess.TimeoutExpired(cmd="wsl", timeout=1),
        ):
            ok = write_tsv("c1_market.kline_daily", "(col1)", b"v1\n")
        assert ok is False

    def test_write_auto_columns(self):
        """columns=None 时自动查询列清单。"""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = b""
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc) as mock_ch:
            with patch("src.zephyr.data.ch_writer._get_insert_columns", return_value="(a, b)"):
                ok = write_tsv("c1_market.kline_daily", None, b"v1\tv2\n")
        assert ok is True


class TestWriteResult:
    """write_result 函数测试（mock _wsl_ch）。"""

    def test_write_result_success(self):
        """成功写入 FetchResult。"""
        result = FetchResult(
            table="c1_market.kline_daily",
            columns=["code", "date", "close"],
            rows=[("000001", "2026-07-05", 10.5), ("000002", "2026-07-05", 20.3)],
            last_key="2026-07-05",
            elapsed_sec=1.0,
        )
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = b""
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc) as mock_ch:
            ok = write_result(result)
        assert ok is True
        # 验证 TSV 数据正确构造
        call_args = mock_ch.call_args
        stdin_data = call_args[1]["stdin_bytes"]  # keyword arg
        assert b"000001\t2026-07-05\t10.5" in stdin_data
        assert b"000002\t2026-07-05\t20.3" in stdin_data

    def test_write_result_with_error(self):
        """FetchResult.error 非 None 时跳过。"""
        result = FetchResult(
            table="c1_market.kline_daily",
            columns=["code"],
            rows=[],
            last_key="",
            elapsed_sec=0,
            error="连接超时",
        )
        with patch("src.zephyr.data.ch_writer._wsl_ch") as mock_ch:
            ok = write_result(result)
        assert ok is False
        mock_ch.assert_not_called()

    def test_write_result_empty_rows(self):
        """无数据行返回 True（跳过但视为成功）。"""
        result = FetchResult(
            table="c1_market.kline_daily",
            columns=["code"],
            rows=[],
            last_key="2026-07-05",
            elapsed_sec=0,
        )
        with patch("src.zephyr.data.ch_writer._wsl_ch") as mock_ch:
            ok = write_result(result)
        assert ok is True
        mock_ch.assert_not_called()

    def test_write_result_none_values(self):
        """None 值转 \\N。"""
        result = FetchResult(
            table="c1_market.test",
            columns=["a", "b"],
            rows=[(None, 1)],
            last_key="",
            elapsed_sec=0,
        )
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = b""
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc) as mock_ch:
            ok = write_result(result)
        assert ok is True
        stdin_data = mock_ch.call_args[1]["stdin_bytes"]
        assert b"\\N\t1" in stdin_data


class TestDeleteWhere:
    """delete_where 函数测试（mock _wsl_ch）。"""

    def test_delete_success(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = b""
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc) as mock_ch:
            ok = delete_where("c1_market.kline_daily", "date = '2026-07-05'")
        assert ok is True
        args = mock_ch.call_args[0][0]
        assert any("ALTER TABLE" in a and "DELETE" in a for a in args)

    def test_delete_failure(self):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = b"Unknown table"
        with patch("src.zephyr.data.ch_writer._wsl_ch", return_value=mock_proc):
            ok = delete_where("nonexistent", "1=1")
        assert ok is False


class TestGetInsertColumns:
    """_get_insert_columns 函数测试（mock query）。"""

    def test_with_default_columns(self):
        """含 DEFAULT 列时应排除。"""
        describe_output = "code\tString\t\ndate\tDate\tDEFAULT\ttoday()\nclose\tFloat64\t\n"
        with patch("src.zephyr.data.ch_writer.query", return_value=describe_output):
            cols = _get_insert_columns("c1_market.kline_daily")
        assert "code" in cols
        assert "close" in cols
        assert "date" not in cols  # DEFAULT 列排除

    def test_empty_describe(self):
        """DESCRIBE 返回空时返回 *。"""
        with patch("src.zephyr.data.ch_writer.query", return_value=""):
            cols = _get_insert_columns("nonexistent")
        assert cols == "*"
