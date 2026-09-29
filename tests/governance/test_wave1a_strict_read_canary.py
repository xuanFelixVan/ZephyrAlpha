# [TTL] task_bound
# [STARTUP] test_only: pytest 收集，无运行期常驻
# [CONSUMERS] CI/本地 pytest; docs/_working/total_command_closeout/wave1a/dead_store_triage.md §4 红证锚
"""红证一：CH 严格读接口失败必抛（人为注入"query 抛错"，尺必须红）。

三条契约：
1. 双链路不可用 ⇒ `query_rows()` / `count_strict()` **必抛** `ClickHouseQueryError`
   （把 raise 删掉本测试即红——W-180.1 出口判据"红证=去掉 raise 必红"）；
2. 同刻同条件下**存量** `ch_reader.query()` 返回 `""` ⇒ 证明"失败"与"真空"在旧通道不可分
   （本仓在册病："静默失败被读成无数据→深度幻觉"）；
3. `parse_tsv_rows` 与 `splitlines()+split('\\t')` 对拍（TSV 解析形状）。

测试禁写生产路径：全部走 monkeypatch + tmp_path，不触任何真实 CH/DB。
"""

from __future__ import annotations

import pytest

from zephyr.data import ch_reader, ch_writer


def _kill_transports(monkeypatch):
    """注入"传输层全灭"：TCP client 不可用 + HTTP host 不可用。"""
    monkeypatch.setattr(ch_writer, "get_client", lambda *a, **k: None)
    monkeypatch.setattr(ch_writer, "get_http_host", lambda *a, **k: "")
    monkeypatch.setattr(ch_writer, "_invalidate_tcp_client", lambda *a, **k: None)
    monkeypatch.setattr(ch_writer, "_invalidate_http_host", lambda *a, **k: None)
    monkeypatch.setattr(ch_writer, "_note_http_failure", lambda *a, **k: None)


class _FakeClient:
    def __init__(self, rows, error=None):
        self._rows = rows
        self._error = error

    def execute(self, sql, settings=None):
        if self._error is not None:
            raise self._error
        return self._rows


def test_query_rows_raises_when_both_transports_down(monkeypatch):
    _kill_transports(monkeypatch)
    with pytest.raises(ch_writer.ClickHouseQueryError) as ei:
        ch_reader.query_rows("SELECT name FROM system.tables")
    kinds = {a[0] for a in ei.value.attempts}
    assert {"tcp", "http"} <= kinds, f"必须记录两条传输路径的失败原因，实得 {ei.value.attempts}"


def test_count_strict_raises_when_both_transports_down(monkeypatch):
    _kill_transports(monkeypatch)
    monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: False)
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_reader.count_strict("c1_market.kline_daily")


def test_legacy_query_is_the_fail_silent_baseline(monkeypatch):
    """在册病基线：同一失败条件下旧通道返回 ''（不抛）⇒ 严格通道存在的理由。"""
    _kill_transports(monkeypatch)
    monkeypatch.setattr(
        ch_writer,
        "log",
        type("L", (), {"error": staticmethod(lambda *a, **k: None), "warning": staticmethod(lambda *a, **k: None)}),
    )
    assert ch_reader.query("SELECT name FROM system.tables") == ""  # 旧行为，禁改
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_reader.query_rows("SELECT name FROM system.tables")


def test_count_strict_distinguishes_real_zero_from_failure(monkeypatch):
    """真空 0 行＝返回 int 0；查询失败＝抛。两态必须可分（W-180.3 复测的前提）。"""
    monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: False)
    monkeypatch.setattr(ch_writer, "get_http_host", lambda *a, **k: "")
    monkeypatch.setattr(ch_writer, "_invalidate_http_host", lambda *a, **k: None)
    monkeypatch.setattr(ch_writer, "_invalidate_tcp_client", lambda *a, **k: None)
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([(0,)]))
    assert ch_reader.count_strict("c1_market.empty_table") == 0
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([], error=RuntimeError("boom")))
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_reader.count_strict("c1_market.kline_daily")


def test_count_strict_rejects_bad_shape(monkeypatch):
    """count 返回非 1x1 或非整数＝契约破坏，必须抛（禁 int() 失败退化成 0）。"""
    monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: True)
    monkeypatch.setattr(ch_writer, "get_http_host", lambda *a, **k: "")
    monkeypatch.setattr(ch_writer, "_invalidate_tcp_client", lambda *a, **k: None)
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([("not-a-number",)]))
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_reader.count_strict("c1_market.kline_daily")


def test_query_rows_returns_row_tuples_on_tcp_path(monkeypatch):
    monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: False)
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([("a", 1), ("b", 2)]))
    rows = ch_reader.query_rows("SELECT name, v FROM c1_market.t")
    assert rows == [("a", 1), ("b", 2)]
    assert ch_writer.last_transport() == "tcp"


def test_query_rows_genuinely_empty_returns_empty_list(monkeypatch):
    monkeypatch.setattr(ch_writer, "is_replacing_engine", lambda t: False)
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([]))
    assert ch_reader.query_rows("SELECT name FROM c1_market.t WHERE 0") == []


def test_engine_probe_failure_raises_instead_of_skipping_final(monkeypatch):
    """FINAL 缺失会让 ReplacingMergeTree 计数虚高 ⇒ 严格版引擎探测失败必须抛。"""

    def _boom(_t):
        raise RuntimeError("engine probe down")

    monkeypatch.setattr(ch_writer, "is_replacing_engine", _boom)
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([("x",)]))
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_reader.query_rows("SELECT count() FROM c1_market.kline_daily")
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_reader.count_strict("c1_market.kline_daily")


def test_query_strict_refuses_non_readonly_sql(monkeypatch):
    """判据通道禁写：非只读语句直接抛（硬禁"对 CH 做任何写操作"的结构性兜底）。"""
    monkeypatch.setattr(ch_writer, "get_client", lambda: _FakeClient([("x",)]))
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_writer.query_strict("DROP TABLE c1_market.kline_daily")
    with pytest.raises(ch_writer.ClickHouseQueryError):
        ch_writer.query_strict("INSERT INTO c1_market.t FORMAT TSV")


@pytest.mark.parametrize(
    "text",
    [
        "a\tb\nc\td\n",
        "单列\n第二行\n",
        "含空字段\t\ty\n",
        "",
        "\n\n",
    ],
)
def test_parse_tsv_rows_matches_manual_split(text):
    """TSV 解析与 splitlines()+split('\\t') 对拍（W-180.1 出口判据）。"""
    expected = [tuple(ln.split("\t")) for ln in text.splitlines() if ln != ""]
    assert ch_writer.parse_tsv_rows(text) == expected
