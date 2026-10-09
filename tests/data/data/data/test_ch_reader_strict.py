# [A_test] module_id: MOD-TEST-CH-STRICT-READ-TEST_CH_READER_STRICT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
        def engine(table):
            if probe_exc is not None:
                raise probe_exc
            return "ReplacingMergeTree" if replacing else "MergeTree"

        monkeypatch.setattr(ch_writer, "get_table_engine", engine)

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
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda t: (_ for _ in ()).throw(AssertionError("不应探测")))
        sql = "SELECT count() FROM t FINAL"
        assert ch_reader.inject_final_strict(sql) == sql

    def test_system_table_no_probe(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda t: (_ for _ in ()).throw(AssertionError("不应探测")))
        sql = "SELECT partition FROM system.parts WHERE active = 1"
        assert ch_reader.inject_final_strict(sql) == sql

    def test_replacing_table_injected(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda t: "ReplacingMergeTree")
        out = ch_reader.inject_final_strict("SELECT count() FROM c1_market.kline_daily")
        assert out == "SELECT count() FROM c1_market.kline_daily FINAL"

    def test_probe_failure_raises(self, monkeypatch):
        def boom(table):
            raise RuntimeError("probe down")

        monkeypatch.setattr(ch_writer, "get_table_engine", boom)
        with pytest.raises(ClickHouseQueryError):
            ch_reader.inject_final_strict("SELECT count() FROM c1_market.kline_daily")


class TestQueryRows:
    def test_passthrough_with_strict_final(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda t: "ReplacingMergeTree")
        seen = {}

        def fake_query_strict(sql, timeout=600):
            seen["sql"] = sql
            return [("a", "b")]

        monkeypatch.setattr(ch_writer, "query_strict", fake_query_strict)
        assert ch_reader.query_rows("SELECT s, v FROM t") == [("a", "b")]
        assert "FROM t FINAL" in seen["sql"]

    def test_query_rows_table_wiring(self, monkeypatch):
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda t: "MergeTree")
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


# ============== P0 治本（2026-10-09）：引擎探测失败禁污染进程级缓存 ==============


class TestEngineProbePoisoning:
    """红证：探针失败后 FINAL 注入必须仍生效，或显式报红——两者都不满足即本类必红。

    病根：`get_table_engine()` 旧实现无条件写缓存，把失败得到的 "" 当权威值缓存，
    一次瞬态故障（如 system.* 内省整片失败）⇒ 该进程永久认为"引擎未知"，
    且 `is_replacing_engine()` 对"未知"与"确证非 Replacing"都给 False，
    连严格通道 `_final_suffix_strict()` 一起静默跳过 FINAL。
    """

    _T = "c1_market.technical_indicator"

    @pytest.fixture(autouse=True)
    def _clean_cache(self):
        ch_writer.table_engine_cache.pop(self._T, None)
        ch_writer.engine_probe_failures.pop(self._T, None)
        yield
        ch_writer.table_engine_cache.pop(self._T, None)
        ch_writer.engine_probe_failures.pop(self._T, None)

    def test_probe_failure_is_not_cached(self, monkeypatch):
        """失败（空返回）绝不写权威缓存——否则污染终身。"""
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=600: "")
        assert ch_writer.get_table_engine(self._T) == ""
        assert self._T not in ch_writer.table_engine_cache, "失败被缓存＝P0 复发"
        assert ch_writer.engine_probe_failures.get(self._T) == 1

    def test_probe_self_heals_after_transient_failure(self, monkeypatch):
        """瞬态故障后恢复：下一次调用必须重新探测并正常注入 FINAL。"""
        seq = iter(["", "", "ReplacingMergeTree"])
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=600: next(seq))
        assert ch_writer.get_table_engine(self._T) == ""
        sql = f"SELECT c FROM {self._T} WHERE 1"
        assert "FINAL" not in ch_reader.inject_final(sql)  # 未知时保守不注入
        out = ch_reader.inject_final(sql)
        assert "FINAL" in out, "自愈后注入必须恢复，否则红"
        assert f"FROM {self._T} FINAL" in out

    def test_strict_raises_on_unknown_engine(self, monkeypatch):
        """严格通道：未知＝抛，不得当成"非 Replacing"安静放行。"""
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=600: "")
        with pytest.raises(ClickHouseQueryError):
            ch_reader.inject_final_strict(f"SELECT c FROM {self._T}")

    def test_inject_final_warns_loudly_on_unknown_engine(self, monkeypatch, caplog):
        """非严格通道：不注入可以，但必须留下可 grep 的响亮告警（不得静默）。"""
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=600: "")
        # 钉到具体 logger：依赖 root 级别在跨文件顺序下会被先导入的模块配置影响
        caplog.set_level("WARNING", logger="zephyr.data.ch_reader")
        caplog.set_level("WARNING", logger="zephyr.data.ch_writer")
        with caplog.at_level("WARNING"):
            ch_reader.inject_final(f"SELECT c FROM {self._T}")
        msgs = [r.getMessage() for r in caplog.records]
        assert any("GATE-P0-ENGINE-PROBE" in m for m in msgs), "降级未报警＝静默假绿"
        assert self._T in ch_writer.engine_probe_failures, "失败未计入可观测面"

    def test_known_non_replacing_engine_still_not_injected(self, monkeypatch):
        """反向不误伤：确证 MergeTree（非 Replacing）⇒ 不注入且不报未知。"""
        monkeypatch.setattr(ch_writer, "query", lambda sql, timeout=600: "MergeTree")
        out = ch_reader.inject_final(f"SELECT c FROM {self._T}")
        assert "FINAL" not in out
        assert self._T not in ch_writer.engine_probe_failures


class TestLegacyCountLoudWarning:
    """⑤-b（批复 b+c 第①步）：存量 count()/query_table() 引擎未知时"语义不变、报警必响"。

    与旧行为的**唯一**差别是告警与失败计数——返回值、FINAL 注入决策都不动，
    存量消费者零迁移（判据类的迁移动作在⑤-c 普查之后逐批做，不在本步大爆炸）。
    """

    _T = "c9_probe.legacy_contract"

    @pytest.fixture(autouse=True)
    def _isolate_failures(self):
        snapshot = dict(ch_writer.engine_probe_failures)
        yield
        ch_writer.engine_probe_failures.clear()
        ch_writer.engine_probe_failures.update(snapshot)

    @classmethod
    def _guard(cls):
        if not hasattr(ch_reader, "_note_unknown_engine"):
            pytest.skip("ch_reader 的⑤-b 响亮化未落地（源袋先行），落地后本组用例自动生效")

    def _probe_fails(self, monkeypatch, reply):
        seen: list[str] = []
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda table: "")

        def fake_query(sql, timeout=600):
            seen.append(sql)
            return reply

        monkeypatch.setattr(ch_writer, "query", fake_query)
        return seen

    def test_count_contract_unchanged_but_loud(self, monkeypatch, caplog):
        self._guard()
        seen = self._probe_fails(monkeypatch, "42\n")
        caplog.set_level("WARNING", logger="zephyr.data.ch_reader")
        assert ch_reader.count(self._T) == 42  # 返回值语义不变
        assert "FINAL" not in seen[0], "未知引擎却注入 FINAL＝行为被改动"
        assert any("GATE-P0-ENGINE-PROBE" in r.getMessage() for r in caplog.records), "降级静默＝假绿"
        assert ch_writer.engine_probe_failures[self._T] == 1

    def test_query_table_contract_unchanged_but_loud(self, monkeypatch, caplog):
        self._guard()
        seen = self._probe_fails(monkeypatch, "a\tb\n")
        caplog.set_level("WARNING", logger="zephyr.data.ch_reader")
        assert ch_reader.query_table(self._T) == "a\tb\n"
        assert "FINAL" not in seen[0]
        assert any(
            "GATE-P0-ENGINE-PROBE" in r.getMessage() and "query_table()" in r.getMessage() for r in caplog.records
        )
        assert ch_writer.engine_probe_failures[self._T] == 1

    def test_failure_count_accumulates_across_calls(self, monkeypatch):
        self._guard()
        self._probe_fails(monkeypatch, "42\n")
        ch_reader.count(self._T)
        ch_reader.count(self._T)
        assert ch_writer.engine_probe_failures[self._T] == 2, "失败计数不累计＝可观测面失真"

    def test_known_replacing_engine_injects_final_and_stays_quiet(self, monkeypatch, caplog):
        """阴性腿：引擎确证 Replacing 时不得报警——否则这道告警会把正常路径也淹掉。"""
        self._guard()
        seen: list[str] = []
        monkeypatch.setattr(ch_writer, "get_table_engine", lambda table: "ReplacingMergeTree")

        def fake_query(sql, timeout=600):
            seen.append(sql)
            return "7\n"

        monkeypatch.setattr(ch_writer, "query", fake_query)
        caplog.set_level("WARNING", logger="zephyr.data.ch_reader")
        assert ch_reader.count(self._T) == 7
        assert " FINAL" in seen[0]
        assert not [r for r in caplog.records if "GATE-P0-ENGINE-PROBE" in r.getMessage()]
        assert self._T not in ch_writer.engine_probe_failures
