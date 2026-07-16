"""ch_writer 单测（MOD-L00-004 阶段2，Hyper-V 迁移后修订 2026-07-16）。

测试内容：
- tsv_escape（纯函数）
- write_tsv（mock _http_insert）
- write_result（mock _http_insert + FetchResult）
- delete_where（mock _get_client + _get_http_host）
- query（mock _get_client + _get_http_host）
- _get_insert_columns（mock query）

不依赖真实 ClickHouse，用 unittest.mock.patch 替换 TCP/HTTP 传输层。
"""
from unittest.mock import patch, MagicMock

import pytest

from src.zephyr.data.ch_writer import (
    tsv_escape,
    write_tsv,
    write_tsv_outcome,
    WriteDisposition,
    write_result,
    delete_where,
    query,
    _get_insert_columns,
    get_table_engine,
    is_replacing_engine,
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
    """query 函数测试（二级传输：clickhouse-driver TCP + HTTP fallback）。"""

    def setup_method(self):
        """每个测试前重置客户端单例。"""
        import src.zephyr.data.ch_writer as cw
        cw._ch_client = None
        cw._ch_http_host = None

    def test_query_select_success(self):
        """SELECT 查询通过 clickhouse-driver 返回 TSV 格式。"""
        mock_client = MagicMock()
        mock_client.execute.return_value = [("col1", "col2")]
        with patch("src.zephyr.data.ch_writer._get_client", return_value=mock_client):
            result = query("SELECT 1")
        assert result == "col1\tcol2\n"

    def test_query_describe_success(self):
        """DESCRIBE TABLE 查询通过 clickhouse-driver 返回 TSV。"""
        mock_client = MagicMock()
        mock_client.execute.return_value = [
            ("code", "String", "", "", "", "", ""),
            ("date", "Date", "DEFAULT", "today()", "", "", ""),
        ]
        with patch("src.zephyr.data.ch_writer._get_client", return_value=mock_client):
            result = query("DESCRIBE TABLE c1_market.kline_daily")
        assert "code\tString" in result
        assert "date\tDate" in result

    def test_query_ddl_returns_empty(self):
        """DDL 语句（TRUNCATE/ALTER）返回空字符串。"""
        mock_client = MagicMock()
        mock_client.execute.return_value = []
        with patch("src.zephyr.data.ch_writer._get_client", return_value=mock_client):
            result = query("TRUNCATE TABLE c1_market.test")
        assert result == ""

    def test_query_select_empty_result(self):
        """SELECT 返回空结果时返回空字符串。"""
        mock_client = MagicMock()
        mock_client.execute.return_value = []
        with patch("src.zephyr.data.ch_writer._get_client", return_value=mock_client):
            result = query("SELECT 1 WHERE 0")
        assert result == ""

    def test_query_driver_fails_fallback_http(self):
        """clickhouse-driver 不可用时（返回 None）降级到 HTTP API。"""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"fallback_result\n"
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp
        with patch("src.zephyr.data.ch_writer._get_client", return_value=None):
            with patch("src.zephyr.data.ch_writer._get_http_host", return_value="172.24.30.100"):
                with patch("http.client.HTTPConnection", return_value=mock_conn):
                    result = query("SELECT 1")
        assert result == "fallback_result\n"

    def test_query_driver_exception_fallback_http(self):
        """clickhouse-driver execute 异常时降级到 HTTP API。"""
        mock_client = MagicMock()
        mock_client.execute.side_effect = Exception("query failed")
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b"fallback_result\n"
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp
        with patch("src.zephyr.data.ch_writer._get_client", return_value=mock_client):
            with patch("src.zephyr.data.ch_writer._get_http_host", return_value="172.24.30.100"):
                with patch("http.client.HTTPConnection", return_value=mock_conn):
                    result = query("SELECT 1")
        assert result == "fallback_result\n"

    def test_query_both_fail_returns_empty(self):
        """driver 不可用且 HTTP 也不可用时返回空字符串。"""
        with patch("src.zephyr.data.ch_writer._get_client", return_value=None):
            with patch("src.zephyr.data.ch_writer._get_http_host", return_value=""):
                result = query("SELECT 1")
        assert result == ""


class TestWriteTsv:
    """write_tsv 函数测试（mock _http_insert）。"""

    def test_write_success(self):
        """成功写入返回 True。"""
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=True) as mock_http:
            ok = write_tsv("c1_market.kline_daily", "(col1, col2)", b"v1\tv2\n")
        assert ok is True
        mock_http.assert_called_once()

    def test_write_empty_data(self):
        """空数据返回 False。"""
        with patch("src.zephyr.data.ch_writer._http_insert") as mock_http:
            ok = write_tsv("c1_market.kline_daily", "(col1)", b"")
        assert ok is False
        mock_http.assert_not_called()

    def test_write_failure_http_local_fallback(self):
        """HTTP 失败后本地落盘也成功，write_tsv 返回 False（非 CH 已提交）。"""
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=False):
            with patch("zephyr.data.local_replay.save_fallback", return_value=True):
                ok = write_tsv("c1_market.kline_daily", "(col1)", b"v1\n")
        assert ok is False  # 本地落盘不等于 CH 已提交

    def test_write_outcome_local_fallback_is_not_ch_commit(self):
        """本地落盘成功必须可区分于 ClickHouse 已提交。"""
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=False):
            with patch("zephyr.data.local_replay.save_fallback", return_value=True):
                outcome = write_tsv_outcome("c1_market.kline_daily", "(col1)", b"v1\n")
        assert outcome.disposition is WriteDisposition.LOCAL_DURABLE
        assert outcome.is_ch_committed is False

    def test_write_outcome_ch_committed(self):
        """HTTP 成功时 outcome 为 CH_COMMITTED。"""
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=True):
            outcome = write_tsv_outcome("c1_market.kline_daily", "(col1)", b"v1\n")
        assert outcome.disposition is WriteDisposition.CH_COMMITTED
        assert outcome.is_ch_committed is True

    def test_write_auto_columns(self):
        """columns=None 时自动查询列清单。"""
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=True) as mock_http:
            with patch("src.zephyr.data.ch_writer._get_insert_columns", return_value="(a, b)"):
                ok = write_tsv("c1_market.kline_daily", None, b"v1\tv2\n")
        assert ok is True


class TestWriteResult:
    """write_result 函数测试（mock _http_insert）。"""

    def test_write_result_success(self):
        """成功写入 FetchResult。"""
        result = FetchResult(
            table="c1_market.kline_daily",
            columns=["code", "date", "close"],
            rows=[("000001", "2026-07-05", 10.5), ("000002", "2026-07-05", 20.3)],
            last_key="2026-07-05",
            elapsed_sec=1.0,
        )
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=True) as mock_http:
            ok = write_result(result)
        assert ok is True
        # 验证 TSV 数据正确构造
        call_args = mock_http.call_args
        tsv_bytes = call_args[0][1]  # 第二个位置参数是 tsv_bytes
        assert b"000001\t2026-07-05\t10.5" in tsv_bytes
        assert b"000002\t2026-07-05\t20.3" in tsv_bytes

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
        with patch("src.zephyr.data.ch_writer._http_insert") as mock_http:
            ok = write_result(result)
        assert ok is False
        mock_http.assert_not_called()

    def test_write_result_empty_rows(self):
        """无数据行返回 True（跳过但视为成功）。"""
        result = FetchResult(
            table="c1_market.kline_daily",
            columns=["code"],
            rows=[],
            last_key="2026-07-05",
            elapsed_sec=0,
        )
        with patch("src.zephyr.data.ch_writer._http_insert") as mock_http:
            ok = write_result(result)
        assert ok is True
        mock_http.assert_not_called()

    def test_write_result_none_values(self):
        """None 值转 \\N。"""
        result = FetchResult(
            table="c1_market.test",
            columns=["a", "b"],
            rows=[(None, 1)],
            last_key="",
            elapsed_sec=0,
        )
        with patch("src.zephyr.data.ch_writer._http_insert", return_value=True) as mock_http:
            ok = write_result(result)
        assert ok is True
        tsv_bytes = mock_http.call_args[0][1]
        assert b"\\N\t1" in tsv_bytes


class TestDeleteWhere:
    """delete_where 函数测试（二级传输：clickhouse-driver TCP + HTTP fallback）。"""

    def setup_method(self):
        """每个测试前重置客户端单例。"""
        import src.zephyr.data.ch_writer as cw
        cw._ch_client = None
        cw._ch_http_host = None

    def test_delete_success_via_driver(self):
        """通过 clickhouse-driver 成功删除。"""
        mock_client = MagicMock()
        with patch("src.zephyr.data.ch_writer._get_client", return_value=mock_client) as mock_gc:
            ok = delete_where("c1_market.kline_daily", "date = '2026-07-05'")
        assert ok is True
        mock_client.execute.assert_called_once()

    def test_delete_driver_fails_fallback_http(self):
        """clickhouse-driver 不可用时（返回 None）降级到 HTTP 并成功。"""
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_conn = MagicMock()
        mock_conn.getresponse.return_value = mock_resp
        with patch("src.zephyr.data.ch_writer._get_client", return_value=None):
            with patch("src.zephyr.data.ch_writer._get_http_host", return_value="172.24.30.100"):
                with patch("http.client.HTTPConnection", return_value=mock_conn):
                    ok = delete_where("c1_market.kline_daily", "date = '2026-07-05'")
        assert ok is True

    def test_delete_both_fail_returns_false(self):
        """driver 不可用且 HTTP 也不可用时返回 False。"""
        with patch("src.zephyr.data.ch_writer._get_client", return_value=None):
            with patch("src.zephyr.data.ch_writer._get_http_host", return_value=""):
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


class TestGetTableEngine:
    """get_table_engine / is_replacing_engine 测试（mock query）。"""

    def setup_method(self):
        """每个测试前清空引擎缓存，避免测试间污染。"""
        import src.zephyr.data.ch_writer as cw
        cw._table_engine_cache.clear()

    def test_replacing_engine(self):
        """ReplacingMergeTree 引擎正确识别。"""
        with patch("src.zephyr.data.ch_writer.query", return_value="ReplacingMergeTree\n"):
            engine = get_table_engine("c1_market.adj_factor")
        assert engine == "ReplacingMergeTree"
        assert is_replacing_engine("c1_market.adj_factor") is True

    def test_plain_mergetree(self):
        """MergeTree 引擎识别为非 replacing。"""
        with patch("src.zephyr.data.ch_writer.query", return_value="MergeTree\n"):
            engine = get_table_engine("c1_market.kline_daily")
        assert engine == "MergeTree"
        assert is_replacing_engine("c1_market.kline_daily") is False

    def test_replicated_replacing(self):
        """ReplicatedReplacingMergeTree 也算 replacing 族。"""
        with patch("src.zephyr.data.ch_writer.query", return_value="ReplicatedReplacingMergeTree\n"):
            assert is_replacing_engine("c1_market.replicated_tbl") is True

    def test_engine_cache(self):
        """第二次查询命中缓存，不再次调用 query。"""
        with patch("src.zephyr.data.ch_writer.query", return_value="ReplacingMergeTree\n") as mock_q:
            get_table_engine("c1_market.cached_tbl")
            get_table_engine("c1_market.cached_tbl")
        # query 只被调用一次（缓存命中）
        assert mock_q.call_count == 1

    def test_empty_engine(self):
        """查询失败（空字符串）返回空，is_replacing 返回 False。"""
        with patch("src.zephyr.data.ch_writer.query", return_value=""):
            engine = get_table_engine("nonexistent.table")
        assert engine == ""
        assert is_replacing_engine("nonexistent.table") is False
