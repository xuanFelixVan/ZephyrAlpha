# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
"""查馆入口等价回归（R4 import 面削薄，st-fms-tc-20260927 常驻组①）。

零真库：连接被替换为假件，只锁"同关键词→同行集同顺序"这条契约。
改前/改后 A/B 实测（HEAD 树 vs 工作树，同一探针脚本，2026-09-27）：
`python -m zephyr.library.lookup` 的 5 条腿（主查询/别名展开/--feeds/空结果/
commit-guide）stdout 与退出码 **逐字节相同**；假连接探针的 JSON 报告除 import
计时一项外亦逐字相同。此处把该结论固化为常驻断言，防后续惰性化悄悄改变
合并顺序/转义/借还语义。
"""

from __future__ import annotations

import pytest

import zephyr.governance.depgraph_schema as depgraph_schema
from zephyr.library import lookup as lookup_mod
from zephyr.library.ledger_cache import LEDGER_PROJECTION_COLUMNS

#: 假库每词固定回 3 行（i=1,2 active / i=3 deceased），用于暴露任何顺序/去重扰动。
_ROWS_PER_TERM = 3


def _unescape_pattern(param: object) -> str:
    """还原 Librarian.lookup 的 LIKE 转义（与 `\\`→`\\\\`、`%`→`\\%`、`_`→`\\_` 逆序）。"""
    text = str(param)
    if text.startswith("%"):
        text = text[1:]
    if text.endswith("%"):
        text = text[:-1]
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            out.append(text[i + 1])
            i += 2
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _expected_ids(terms: list[str], limit: int) -> list[str]:
    """独立陈述"逐深度轮转合并"契约：同深度上原词优先，展开词不被长尾挤掉。"""
    merged: list[str] = []
    for depth in range(1, _ROWS_PER_TERM + 1):
        for term in terms:
            asset_id = f"{term}#{depth}"
            if asset_id not in merged:
                merged.append(asset_id)
    return merged[:limit]


def _make_row(term: str, i: int) -> dict[str, object]:
    row: dict[str, object] = dict.fromkeys(LEDGER_PROJECTION_COLUMNS, "")
    row.update(
        {
            "asset_id": f"{term}#{i}",
            "kind": "file",
            "status": "active" if i != 3 else "deceased",
            "home": f"docs/{term}/{i}",
            "title": f"title {term} {i}",
            "owner_domain": "D_DATA",
            "tags": ["ch", "行情"] if i == 2 else ["ch"],
            "successor_of": None if i == 3 else "",
            "disposition_authority": "裁定#410" if i == 3 else None,
        }
    )
    return row


class _FakeCursor:
    def __init__(self, sink: list[tuple[str, tuple]]) -> None:
        self._sink = sink
        self.description: list[tuple] = []
        self._rows: list[tuple] = []

    def __enter__(self) -> _FakeCursor:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False

    def execute(self, sql: str, params: tuple = ()) -> None:
        self._sink.append((sql, tuple(params)))
        # --feeds 腿的 SQL 只带 limit（关键词在 Python 侧过滤），行形如供数反查投影
        if params and isinstance(params[0], int):
            self.description = [(col,) for col in ("asset_id", "kind", "home", "status", "title", "consumers")]
            self._rows = [(f"feeds#{i}", "table", f"data/{i}", "active", f"title {i}", ["lookup"]) for i in range(1, 4)]
            return
        term = _unescape_pattern(params[0]) if params else ""
        self.description = [(col,) for col in LEDGER_PROJECTION_COLUMNS]
        self._rows = [
            tuple(_make_row(term, i)[col] for col in LEDGER_PROJECTION_COLUMNS) for i in range(1, _ROWS_PER_TERM + 1)
        ]

    def fetchall(self) -> list[tuple]:
        return list(self._rows)


class _FakeConn:
    """只允许"借还"，任何 close() 即测试失败（连接弃池反模式）。"""

    def __init__(self, sink: list[tuple[str, tuple]]) -> None:
        self._sink = sink

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self._sink)

    def commit(self) -> None:
        return None

    def close(self) -> None:
        raise AssertionError("池化连接被 close 而非 release 归还")


class _PoolDownError(RuntimeError):
    """替身异常：语义等同 psycopg2 PoolError/OperationalError（取不到连接）。"""


@pytest.fixture
def fake_pg(monkeypatch):  # noqa: ARG001 — pytest fixture 注入
    """把池化借还口换成假件，并强制走"直查真源"腿（缓存旁路）。"""
    executed: list[tuple[str, tuple]] = []
    released: list[bool] = []

    def _get():
        return _FakeConn(executed)

    def _release(conn):  # noqa: ARG001
        released.append(True)

    # 惰性化后的函数内 import 正是从真源模块取属性——这里也是组②的靶面
    monkeypatch.setattr(depgraph_schema, "get_depgraph_pg_connection", _get, raising=True)
    monkeypatch.setattr(depgraph_schema, "release_depgraph_pg_connection", _release, raising=True)
    monkeypatch.setenv("LIBRAM_DIRECT", "1")
    return executed, released


@pytest.mark.parametrize(
    ("query", "kwargs"),
    [
        pytest.param("kline", {"limit": 5}, id="plain"),
        pytest.param(
            "lookup",
            {"limit": 3, "kind": "file", "owner_domain": "D_DATA", "tags": ["ch"], "status": "active"},
            id="t5-five-filters",
        ),
        pytest.param("module", {"limit": 7, "status": "stale"}, id="status-filter"),
        pytest.param("融资融券", {"limit": 4}, id="alias-expansion"),
        pytest.param("backtest", {"limit": 6, "home_prefix": "data/backtest_artifacts/"}, id="backtest-prefix"),
    ],
)
def test_lookup_assets_row_set_and_order_unchanged(fake_pg, query, kwargs) -> None:
    """组①：同关键词→同行集同顺序；一次查询借还各一次（不随词数增加）。"""
    executed, released = fake_pg
    terms = lookup_mod._expand_query(query)
    rows = lookup_mod.lookup_assets(query, **kwargs)
    assert [row["asset_id"] for row in rows] == _expected_ids(terms, kwargs["limit"])
    assert len(executed) == len(terms), "展开词数与 SQL 条数须一致（别名轴未变）"
    assert len(released) == 1, "一条查询只借一次连接、必须归还一次"


def test_sql_text_and_params_pinned(fake_pg) -> None:
    """组①：SQL 文本与参数（转义三列 + limit）逐字钉住，防过滤拼接面漂移。"""
    executed, _ = fake_pg
    lookup_mod.lookup_assets("kline", limit=5)
    sql, params = executed[0]
    assert params == ("%kline%", "%kline%", "%kline%", 5)
    assert "lib_assets" in sql
    assert "ILIKE" in sql


def test_like_escaping_of_reserved_pattern_chars(fake_pg) -> None:
    """组①：`%`/`_`/`\\` 转义口径不变（假库以还原后的词命名行，转义漂移即行集漂移）。"""
    executed, _ = fake_pg
    rows = lookup_mod.lookup_assets("a%b_c", limit=3)
    assert executed[0][1][:3] == ("%a\\%b\\_c%", "%a\\%b\\_c%", "%a\\%b\\_c%")
    assert [row["asset_id"] for row in rows] == ["a%b_c#1", "a%b_c#2", "a%b_c#3"]


def test_feeds_leg_uses_pooled_connection(fake_pg, capsys) -> None:
    """组①：--feeds 腿（第二条惰性 import 落点）查询与借还口径不变。"""
    _executed, released = fake_pg
    assert lookup_mod._run_feeds_query("lookup", 5) == 0
    assert len(released) == 1
    out = capsys.readouterr().out
    assert "feeds#1\ttable\tlookup" in out


def test_commit_guide_leg_touches_no_database(monkeypatch, capsys) -> None:
    """组①：commit-guide: 腿本就不碰 PG——惰性化后仍不得取连接（少借=不变）。"""

    def _boom():
        raise AssertionError("commit-guide 腿不应取连接")

    monkeypatch.setattr(depgraph_schema, "get_depgraph_pg_connection", _boom, raising=True)
    monkeypatch.delenv("LIBRAM_DIRECT", raising=False)
    rc = lookup_mod._query_commit_guide("")
    out = capsys.readouterr().out
    assert rc in (0, 1)
    assert ("commit-guide anchors" in out) or ("playbook missing" in out)
