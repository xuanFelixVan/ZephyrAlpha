# [A_test] module_id: MOD-TEST-CH-STRICT-READ | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] W-180 | docs/_working/final_delivery_campaign/workorders_data_exam_factory.md（C134 处方：strict 抛错契约） | §
# [MODULE] tests.data.test_ch_reader_strict
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.ch_writer; stdlib(http.client)
# [CONSUMERS] CI pytest
# [STARTUP] test_only
# [MATURITY] testing
# [TTL] permanent
# [INVARIANTS] W-180.1 严格读通道契约尺（全 fake，零网络/零真实 CH/零生产写入）：
#   1. query_strict 只读白名单（非 SELECT/WITH/SHOW/DESCRIBE/EXPLAIN 直接抛 contract 错，不触传输层）；
#   2. 双链路全失败必抛 ClickHouseQueryError（attempts 逐路径可溯源），"查询失败"与"真 0 行"两态可分；
#   3. count_strict：形状异常/非整数必抛，[(0,)]＝确证空表返回 0；引擎探测失败必抛；
#   4. 存量静默契约不回退：ch_reader.query()/count() 失败仍返回 ""/0（存量 12+ 消费者零迁移）。
"""W-180.1 CH 严格读通道契约测试（query_strict/count_strict/inject_final_strict/query_rows）。"""

from __future__ import annotations

import http.client

import pytest

from zephyr.data import ch_reader, ch_writer
from zephyr.data.ch_reader import ClickHouseQueryError

# ============== ch_writer.parse_tsv_rows ==============


class TestParseTsvRows:
    def test_empty_and_whitespace(self):
        assert ch_writer.parse_tsv_rows("") == []
        assert ch_writer.parse_tsv_rows("   \n") == []

    def test_tsv_to_tuples(self):
        assert ch_writer.parse_tsv_rows("1\t2\n3\t4") == [("1", "2"), ("3", "4")]


# ============== ch_writer.query_strict ==============


class _FakeTcpClient:
    def __init__(self, rows=None, exc: Exception | None = None):
        self._rows = rows or []
        self._exc = exc
        self.calls: list[str] = []

    def execute(self, sql, settings=None):
        self.calls.append(sql)
        if self._exc is not None:
            raise self._exc
        return [tuple(r) for r in self._rows]


class _FakeResp:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body

    def read(self) -> bytes:
        return self._body


class _FakeConn:
    def __init__(self, status: int, body: bytes):
        self._status = status
        self._body = body
        self.closed = False

    def request(self, method, path, headers=None):
        pass

    def getresponse(self) -> _FakeResp:
        return _FakeResp(self._status, self._body)

    def close(self):
        self.closed = True


class TestQueryStrictContract:
    def test_readonly_guard_raises_before_transport(self, monkeypatch):
        """非只读语句直接抛 contract 错，且不触碰任何传输层。"""
        touched = []
        monkeypatch.setattr(ch_writer, "get_client", lambda: touched.append("tcp"))
        monkeypatch.setattr(ch_writer, "get_http_host", lambda: touched.append("http"))
        with pytest.raises(ClickHouseQueryError) as ei:
            ch_writer.query_strict("INSERT INTO t VALUES (1)")
        assert ei.value.attempts[0][0] == "contract"
        assert touched == []

    def test_tcp_success(self, monkeypatch):
        fake = _FakeTcpClient(rows=[(1, "a"), (3, "b")])
        monkeypatch.setattr(ch_writer, "get_client", lambda: fake)
        monkeypatch.setattr(ch_writer, "get_http_host", lambda: "")
        rows = ch_writer.query_strict("SELECT x, y FROM t")
        assert rows == [(1, "a"), (3, "b")]
        assert ch_writer.last_transport() == "tcp"

    def test_dual_path_failure_raises_with_attempts(self, monkeypatch):
        """TCP/HTTP 双链路全失败 → 必抛（禁降级空值），attempts 双路径可溯源。"""
        monkeypatch.setattr(ch_writer, "get_client", lambda: None)
        monkeypatch.setattr(ch_writer, "get_http_host", lambda: "")
        with pytest.raises(ClickHouseQueryError) as ei:
            ch_writer.query_strict("SELECT 1")
        paths = [a[0] for a in ei.value.attempts]
        assert "tcp" in paths and "http" in paths
        assert "SELECT 1" in str(ei.value)

    def test_http_fallback_success_after_tcp_failure(self, monkeypatch):
        """TCP 挂 → HTTP 200 兜底；行集经 parse_tsv_rows。"""
        fake = _FakeTcpClient(exc=RuntimeError("tcp down"))
        invalidated = []
        monkeypatch.setattr(ch_writer, "get_client", lambda: fake)
        monkeypatch.setattr(ch_writer, "_invalidate_tcp_client", lambda reason="": invalidated.append(reason))
        monkeypatch.setattr(ch_writer, "get_http_host", lambda: "fake-host")
        monkeypatch.setattr(http.client, "HTTPConnection", lambda host, port, timeout: _FakeConn(200, b"5\t6\n"))
        rows = ch_writer.query_strict("SELECT a, b FROM t")
        assert rows == [("5", "6")]
        assert ch_writer.last_transport() == "http"
        assert invalidated, "TCP 失败必须触发自愈失效钩子"

    def test_http_500_raises(self, monkeypatch):
        noted = []
        monkeypatch.setattr(ch_writer, "get_client", lambda: None)
        monkeypatch.setattr(ch_writer, "get_http_host", lambda: "fake-host")
        monkeypatch.setattr(ch_writer, "_note_http_failure", lambda reason="": noted.append(reason))
        monkeypatch.setattr(http.client, "HTTPConnection", lambda host, port, timeout: _FakeConn(503, b"boom"))
        with pytest.raises(ClickHouseQueryError):
            ch_writer.query_strict("SELECT 1")
        assert noted, "5xx 必须记链路自愈观测"

    def test_write_statement_rejected_even_lowercase(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "get_client", lambda: None)
        with pytest.raises(ClickHouseQueryError):
            ch_writer.query_strict("  alter table t drop partition 202401")


# ============== ch_reader 严格族（引擎探测/形状契约） ==============


class TestCountStrict:
    def _probe(self, monkeypatch, replacing=True, probe_exc: Exception | None = None):
        def probe(table):
            if probe_exc is not None:
                raise probe_exc
            return replacing

        monkeypatch.setattr(ch_writer, "is_replacing_engine", probe)

    def test_success_with_final_and_where(self, monkeypatch):
        self._probe(monkeypatch, replacing=True)
        seen = {}

        def fake_query_strict(sql, timeout=30):
            seen["sql"] = sql
            return [(7,)]

        monkeypatch.setattr(ch_writer, "query_strict", fake_query_strict)
        assert ch_reader.count_strict("c1_market.kline_daily", where="trade_date = '2026-09-29'") == 7
        assert "FROM c1_market.kline_daily FINAL" in seen["sql"]
        assert "WHERE trade_date = '2026-09-29'" in seen["sql"]

    def test_true_zero_is_confirmed_empty(self, monkeypatch):
        """[(0,)]＝确证空表返回 0（与"失败"两态可分，这正是 W-180 的核心契约）。"""
        self._probe(monkeypatch, replacing=False)
        monkeypatch.setattr(ch_writer, "query_strict", lambda sql, timeout=30: [(0,)])
        assert ch_reader.count_strict("c1_market.tick_data") == 0

    def test_empty_shape_raises(self, monkeypatch):
        self._probe(monkeypatch, replacing=False)
        monkeypatch.setattr(ch_writer, "query_strict", lambda sql, timeout=30: [])
        with pytest.raises(ClickHouseQueryError, match="1x1"):
            ch_reader.count_strict("c1_market.tick_data")

    def test_non_integer_raises(self, monkeypatch):
        self._probe(monkeypatch, replacing=False)
        monkeypatch.setattr(ch_writer, "query_strict", lambda sql, timeout=30: [("oops",)])
        with pytest.raises(ClickHouseQueryError, match="非整数"):
            ch_reader.count_strict("c1_market.tick_data")

    def test_engine_probe_failure_raises(self, monkeypatch):
        """引擎探测失败必抛（FINAL 缺失会让 ReplacingMergeTree 计数虚高，禁静默降级）。"""
        self._probe(monkeypatch, probe_exc=RuntimeError("probe down"))
        with pytest.raises(ClickHouseQueryError, match="engine_probe"):
            ch_reader.count_strict("c1_market.kline_daily")


class TestInjectFinalStrict:
    def test_existing_final_no_probe(self, monkeypatch):
        monkeypatch.setattr(
            ch_writer, "is_replacing_engine", lambda t: (_ for _ in ()).throw(AssertionError("不应探测"))
        )
        sql = "SELECT count() FROM t FINAL"
        assert ch_reader.inject_final_strict(sql) == sql

    def test_system_table_no_probe(self, monkeypatch):
        monkeypatch.setattr(
            ch_writer, "is_replacing_engine", lambda t: (_ for _ in ()).throw(AssertionError("不应探测"))
        )
        sql = "SELECT partition FROM system.parts WHERE active = 1"
        assert ch_reader.inject_final_strict(sql) == sql

    def test_replacing_table_injected(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: True)
        out = ch_reader.inject_final_strict("SELECT count() FROM c1_market.kline_daily")
        assert out == "SELECT count() FROM c1_market.kline_daily FINAL"

    def test_probe_failure_raises(self, monkeypatch):
        def boom(table):
            raise RuntimeError("probe down")

        monkeypatch.setattr(ch_writer, "is_replacing_engine", boom)
        with pytest.raises(ClickHouseQueryError):
            ch_reader.inject_final_strict("SELECT count() FROM c1_market.kline_daily")


class TestQueryRows:
    def test_passthrough_with_strict_final(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: True)
        seen = {}

        def fake_query_strict(sql, timeout=600):
            seen["sql"] = sql
            return [("a", "b")]

        monkeypatch.setattr(ch_writer, "query_strict", fake_query_strict)
        assert ch_reader.query_rows("SELECT s, v FROM t") == [("a", "b")]
        assert "FROM t FINAL" in seen["sql"]

    def test_query_rows_table_wiring(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: False)
        seen = {}

        def fake_query_strict(sql, timeout=600):
            seen["sql"] = sql
            return [(1,)]

        monkeypatch.setattr(ch_writer, "query_strict", fake_query_strict)
        assert ch_reader.query_rows_table("t", columns="x", where="x > 0", order_by="x", limit=5) == [(1,)]
        assert "SELECT x FROM t" in seen["sql"]
        assert "WHERE x > 0" in seen["sql"] and "ORDER BY x" in seen["sql"] and "LIMIT 5" in seen["sql"]


# ============== 存量静默契约不回退（内收红线） ==============


class TestLegacySilentContractUnchanged:
    def test_legacy_query_returns_empty_string_on_failure(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=600: "")
        assert ch_reader.query("SELECT 1") == ""

    def test_legacy_count_returns_zero_on_failure(self, monkeypatch):
        """存量 count() 失败仍返回 0（fail-silent）——判据类读数禁用由 docstring 红线约束。"""
        monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: False)
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=30: "")
        assert ch_reader.count("c1_market.tick_data") == 0

    def test_exception_type_shared_between_modules(self):
        assert ch_reader.ClickHouseQueryError is ch_writer.ClickHouseQueryError
