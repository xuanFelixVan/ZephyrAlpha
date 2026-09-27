# [TTL] permanent
"""successor_of 墓碑去向接线测试（S5 图书馆接线）：SQL 面+馆员写入面+lookup CLI 展示面。

零 DB 依赖：fake conn/cursor 记录参数，CLI 走 monkeypatch lookup_assets。
"""

from __future__ import annotations

import pytest

from zephyr.library import lookup as lookup_mod
from zephyr.library.ledger_schema import (
    _SQL_ENSURE_ASSETS,
    _SQL_LOOKUP,
    _SQL_LOOKUP_COMPOSED,
    _SQL_MARK_DECEASED,
)
from zephyr.library.librarian import Librarian
from zephyr.library.lookup import _successor_display, _tombstone_tail

# ---------------------------------------------------------------- SQL 常量面


def test_ensure_assets_contains_successor_of_column() -> None:
    """CREATE TABLE 常量与迁移后老库同列对齐（增枝五步先例②第 5 步）。"""
    assert "successor_of text," in _SQL_ENSURE_ASSETS


def test_lookup_selects_tombstone_columns() -> None:
    """两条查询基座都必须带 disposition_authority + successor_of（墓碑显示供数）。"""
    for sql in (_SQL_LOOKUP, _SQL_LOOKUP_COMPOSED):
        assert "disposition_authority, successor_of" in sql


def test_mark_deceased_sets_successor_of() -> None:
    """死亡登记 SQL：SET 三参（authority/successor_of/asset_id）。"""
    assert "disposition_authority = %s, successor_of = %s" in _SQL_MARK_DECEASED
    assert _SQL_MARK_DECEASED.count("%s") == 3


# ---------------------------------------------------------------- 馆员写入面


class _RecordingCur:
    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def __enter__(self) -> _RecordingCur:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def execute(self, sql: object, *args: object) -> None:
        self.calls.append((sql, args))

    def fetchone(self) -> tuple:
        return (1,)


class _RecordingConn:
    def __init__(self) -> None:
        self.cur = _RecordingCur()

    def cursor(self) -> _RecordingCur:
        return self.cur

    def commit(self) -> None:
        pass


def _delete_params(fields: dict) -> tuple:
    conn = _RecordingConn()
    Librarian(conn).act(  # type: ignore[arg-type]
        "delete", "FILE:docs/old.md", actor="t", authority="裁定#NNN", fields=fields
    )
    sql, args = conn.cur.calls[-1]
    assert sql == _SQL_MARK_DECEASED
    return args[0]  # execute(sql, params) 形态：单参元组


def test_act_delete_passes_successor_of() -> None:
    """delete 携带后继指针：参数序 (authority, successor_of, asset_id)。"""
    params = _delete_params({"successor_of": "FILE:docs/new.md"})
    assert params == ("裁定#NNN", "FILE:docs/new.md", "FILE:docs/old.md")


def test_act_delete_successor_default_none_means_unevaluated() -> None:
    """delete 缺省 successor_of=None=未评估（历史存量兼容态），禁 or 串误转空串。"""
    params = _delete_params({})
    assert params == ("裁定#NNN", None, "FILE:docs/old.md")


def test_act_delete_empty_successor_means_no_successor() -> None:
    """显式空串=确认无后继（两态纪律，08 §6）。"""
    params = _delete_params({"successor_of": ""})
    assert params == ("裁定#NNN", "", "FILE:docs/old.md")


# ---------------------------------------------------------------- 展示面纯函数


def test_successor_display_states() -> None:
    """四态渲染：后继指针/确认无后继/未评估有墓志/未评估无墓志。"""
    assert _successor_display({"successor_of": "MOD:a.py"}) == "MOD:a.py"
    assert _successor_display({"successor_of": ""}) == "(无后继)"
    authority = "裁" * 60
    shown = _successor_display({"successor_of": None, "disposition_authority": authority})
    assert shown.startswith("去向未评估｜墓志:")
    assert len(shown) < len(authority)  # 墓志截前 40 字
    assert _successor_display({"successor_of": None, "disposition_authority": ""}) == "去向未评估"
    # 旧形态行（键全缺）不抛异常
    assert _successor_display({}) == "去向未评估"


def test_tombstone_tail_only_for_deceased() -> None:
    """尾巴只挂 deceased 行；active/archived 行恒空。"""
    dead = {"status": "deceased", "successor_of": "MOD:b.py"}
    assert _tombstone_tail(dead).endswith("-> MOD:b.py")
    assert _tombstone_tail({"status": "active"}) == ""
    assert _tombstone_tail({"status": "archived"}) == ""


# ---------------------------------------------------------------- CLI 面


def _cli_rows(status: str, successor: object, authority: str = "裁定#1") -> list[dict]:
    return [
        {
            "asset_id": "FILE:docs/old.md",
            "kind": "file",
            "status": status,
            "home": "docs/old.md",
            "title": None,
            "built_at": None,
            "disposition_authority": authority,
            "successor_of": successor,
        }
    ]


def _run_main(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], rows: list[dict]) -> int:
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: rows)
    return lookup_mod.main(["old.md", "--no-alias"])


def test_cli_deceased_with_successor_prints_moved_card(monkeypatch, capsys) -> None:
    """全结果无 active 有 deceased：行尾去向 + moved 墓碑卡。"""
    code = _run_main(monkeypatch, capsys, _cli_rows("deceased", "FILE:docs/new.md"))
    out = capsys.readouterr().out
    assert code == 0
    assert "-> FILE:docs/new.md" in out
    assert "(moved: FILE:docs/old.md -> FILE:docs/new.md)" in out


def test_cli_deceased_without_successor_shows_no_successor(monkeypatch, capsys) -> None:
    """空串=确认无后继：显示 (无后继)，仍出墓碑卡。"""
    code = _run_main(monkeypatch, capsys, _cli_rows("deceased", ""))
    out = capsys.readouterr().out
    assert "-> (无后继)" in out
    assert "(moved: FILE:docs/old.md -> (无后继))" in out


def test_cli_deceased_unevaluated_shows_authority_inscription(monkeypatch, capsys) -> None:
    """NULL=未评估：退显 disposition_authority 墓志。"""
    code = _run_main(monkeypatch, capsys, _cli_rows("deceased", None, authority="批文：准予注销迁移"))
    out = capsys.readouterr().out
    assert "去向未评估｜墓志:批文：准予注销迁移" in out


def test_cli_active_hits_no_moved_card(monkeypatch, capsys) -> None:
    """有 active 命中：不出墓碑卡（正常在编结果）。"""
    code = _run_main(monkeypatch, capsys, _cli_rows("active", None))
    out = capsys.readouterr().out
    assert "(moved:" not in out
    assert "->" not in out
    assert code == 0


def test_cli_no_rows_exit_1(monkeypatch, capsys) -> None:
    """零命中：维持 (no results) 退出码 1。"""
    code = _run_main(monkeypatch, capsys, [])
    out = capsys.readouterr().out
    assert "(no results" in out
    assert code == 1
