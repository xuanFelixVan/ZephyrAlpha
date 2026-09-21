"""relations 纯函数层测试（零 DB 依赖；BFS 用假连接桩）。"""

from __future__ import annotations

from typing import Any

from zephyr.library.relations import (
    paths_from_assets,
    relations_tree,
    render_relations,
)


def test_paths_from_assets_maps_file_and_mod_ids() -> None:
    """FILE:/MOD: 身份证转路径；未知前缀忽略；保序去重。"""
    rows = [
        {"asset_id": "FILE:src/zephyr/library/lookup.py"},
        {"asset_id": "MOD:src.zephyr.library.librarian"},
        {"asset_id": "PG:depgraph.lib_assets"},
        {"asset_id": "FILE:src/zephyr/library/lookup.py"},
    ]
    paths = paths_from_assets(rows)
    assert paths == [
        "src/zephyr/library/lookup.py",
        "src/zephyr/library/librarian.py",
    ]


def test_render_relations_contains_sections() -> None:
    """渲染含四段结构且含种子行。"""
    text = render_relations(
        "kline_1min",
        [{"asset_id": "FILE:a.py", "kind": "file", "status": "active", "title": "t"}],
        [{"path": "b.py", "node_type": "module", "labels": ["→import"]}],
        {"文档馆关联": [{"asset_id": "DOC:d.md", "kind": "doc", "title": "dd"}]},
        2,
    )
    assert "种子资产 ×1" in text
    assert "代码关联" in text
    assert "b.py" in text
    assert "文档馆关联" in text
    assert "DOC:d.md" in text


class _FakeCur:
    """最小游标桩：按 SQL 片段路由（列描述+行集）。"""

    def __init__(self, routes: dict[str, tuple[list[str], list[Any]]]) -> None:
        self._routes = routes
        self.description: list[Any] = []
        self._rows: list[Any] = []

    def execute(self, sql: str, params: Any = None) -> None:
        for key, (cols, rows) in self._routes.items():
            if key in sql:
                self.description = [(c,) for c in cols]
                self._rows = rows
                return
        self.description = []
        self._rows = []

    def fetchall(self) -> list[Any]:
        return self._rows

    def close(self) -> None:
        pass

    def __enter__(self) -> _FakeCur:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class _FakeConn:
    """最小连接桩。"""

    def __init__(self, routes: dict[str, tuple[list[str], list[Any]]]) -> None:
        self._routes = routes

    def cursor(self) -> _FakeCur:
        return _FakeCur(self._routes)

    def close(self) -> None:
        pass


def test_relations_tree_bfs_and_cap_via_stub() -> None:
    """BFS 一跳展开+馆归类走通（假连接桩，零真库）。"""
    routes = {
        "FROM lib_assets": (
            ["asset_id", "kind", "home", "status", "title", "built_at"],
            [("FILE:src/x/a.py", "file", "file:src/x/a.py", "active", "seed", "")],
        ),
        "FROM nodes WHERE path": (
            ["node_id", "path", "node_type", "build_status"],
            [(1, "src/x/a.py", "module", "production")],
        ),
        "e.dep_type, n.path AS other_path": (
            ["other_id", "dep_type", "other_path"],
            [(2, "import", "src/x/b.py"), (3, "data", "src/x/c.py")],
        ),
    }
    conn = _FakeConn(routes)
    text, seeds = relations_tree(conn, "a.py", depth=1)
    assert seeds == 1
    assert "src/x/b.py" in text
    assert "import" in text


def test_relations_tree_no_seed_returns_zero() -> None:
    """无种子返回 0 且文本带提示。"""
    conn = _FakeConn({})
    text, seeds = relations_tree(conn, "no-such-thing-xyz", depth=2)
    assert seeds == 0
    assert "no seed assets" in text
