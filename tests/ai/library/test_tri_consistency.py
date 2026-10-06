# [TTL] permanent
"""三层一致性检查器测试（S5）：账↔视图↔盘断言面纯函数 + run_tri_check 编排（fake conn）。

零 DB 依赖；馆页 fixture 用真实 _write_page 产出（格式真源），INDEX 手拼同格式。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from scripts.governance.generators import check_library_tri_consistency as tri
from scripts.governance.generators.generate_library_index import _DISPLAY_CAP, _write_page


def _db_rows() -> list[dict[str, Any]]:
    """合成总账行：code 馆 2 module + 1 file、data 馆 1 table（_SQL_ALL 同序按 kind, home）。"""
    return [
        {"asset_id": "FILE:src/a.py", "kind": "file", "home": "src/a.py", "status": "active"},
        {"asset_id": "MOD:src/b.py", "kind": "module", "home": "src/b.py", "status": "active"},
        {"asset_id": "MOD:src/c.py", "kind": "module", "home": "src/c.py", "status": "active"},
        {"asset_id": "TBL:ch.k", "kind": "table", "home": "ch.k", "status": "active"},
    ]


def _write_view(
    library_dir: Path,
    db_rows: list[dict[str, Any]],
    *,
    only: tuple[str, ...] | None = None,
) -> dict[str, int]:
    """按生成器同款写出七馆页+INDEX（一致态基准；only=故意漏写若干馆页的降级 fixture）。"""
    library_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for name, title, _p in tri._HALLS:
        rows = [r for r in db_rows if tri._classify(r["kind"], r["home"]) == name]
        counts[name] = len(rows)
        if only is not None and name not in only:
            continue
        _write_page(library_dir / f"{name}.md", f"DOC:docs/library/{name}.md", title, rows, len(rows))
    lines = [
        "---",
        'asset_id: "DOC:docs/library/INDEX.md"',
        'ttl: "permanent"',
        'doc_type: "index"',
        "---",
        "",
        f"- 在编资产总数：{len(db_rows)}（deceased 除外）",
        "- 查询总口：`python -m zephyr.library.lookup <关键词>`",
        "",
        "| 馆 | 页 | 在编数 |",
        "|---|---|---|",
    ]
    for name, title, _p in tri._HALLS:
        lines.append(f"| {title} | [{name}.md]({name}.md) | {counts[name]} |")
    (library_dir / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return counts


# ---------------------------------------------------------------- 解析面


def test_parse_index_extracts_total_and_halls() -> None:
    rows = _db_rows()
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        lib = Path(td)
        _write_view(lib, rows)
        parsed = tri.parse_index((lib / "INDEX.md").read_text(encoding="utf-8"))
    assert parsed["total"] == 4
    assert parsed["halls"]["code"] == 3
    assert parsed["halls"]["data"] == 1


def test_parse_page_extracts_counts_and_rows() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        lib = Path(td)
        _write_view(lib, _db_rows())
        page = tri.parse_page((lib / "code.md").read_text(encoding="utf-8"))
    assert page["listed"] == 3
    assert page["total"] == 3
    assert ("FILE:src/a.py", "file", "active", "src/a.py") in page["rows"]
    assert all(r[0] != "asset_id" for r in page["rows"])  # 表头不入数据行


def test_parse_page_missing_declarations_return_none() -> None:
    page = tri.parse_page("# 只有标题\n")
    assert page["listed"] is None
    assert page["total"] is None
    assert page["rows"] == []


# ---------------------------------------------------------------- 账↔视图


def test_consistent_view_zero_findings(tmp_path: Path) -> None:
    _write_view(tmp_path, _db_rows())
    assert tri.check_ledger_vs_view(_db_rows(), tmp_path) == []


def test_index_total_drift_detected(tmp_path: Path) -> None:
    _write_view(tmp_path, _db_rows())
    index = tmp_path / "INDEX.md"
    index.write_text(index.read_text(encoding="utf-8").replace("在编资产总数：4", "在编资产总数：99"), encoding="utf-8")
    findings = tri.check_ledger_vs_view(_db_rows(), tmp_path)
    assert any("INDEX 在编总数 99 != 总账 4" in f for f in findings)


def test_index_hall_count_drift_detected(tmp_path: Path) -> None:
    _write_view(tmp_path, _db_rows())
    index = tmp_path / "INDEX.md"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            "| 代码馆 | [code.md](code.md) | 3 |", "| 代码馆 | [code.md](code.md) | 30 |"
        ),
        encoding="utf-8",
    )
    findings = tri.check_ledger_vs_view(_db_rows(), tmp_path)
    assert any("代码馆 在编数 30 != 总账 3" in f for f in findings)


def test_page_declared_listed_vs_actual_rows_catches_count_bug(tmp_path: Path) -> None:
    """S4 计数失真断言：声明 999 vs 表格 3 行必报（修复后恒一致）。"""
    rows = _db_rows()
    _write_view(tmp_path, rows)
    page = tmp_path / "code.md"
    text = page.read_text(encoding="utf-8").replace("条目数（本页列出）：3", "条目数（本页列出）：999")
    page.write_text(text, encoding="utf-8", newline="\n")
    findings = tri.check_ledger_vs_view(rows, tmp_path)
    assert any("'本页列出'声明 999 != 表格实际 3 行" in f for f in findings)


def test_page_row_drift_reports_first_diff(tmp_path: Path) -> None:
    rows = _db_rows()
    _write_view(tmp_path, rows)
    page = tmp_path / "code.md"
    text = page.read_text(encoding="utf-8").replace("| src/a.py |", "| src/moved.py |")
    page.write_text(text, encoding="utf-8", newline="\n")
    findings = tri.check_ledger_vs_view(rows, tmp_path)
    assert any("code.md 表格与总账逐行复核不一致" in f and "首个差异行号 0" in f for f in findings)


def test_page_missing_untouched_halls_reported(tmp_path: Path) -> None:
    """故意漏写五馆页：缺失必须逐页报（生成器七页全写，缺页=视图残缺）。"""
    _write_view(tmp_path, _db_rows(), only=("code", "data"))
    findings = tri.check_ledger_vs_view(_db_rows(), tmp_path)
    missing = [f for f in findings if "馆页" in f and "不可读" in f]
    assert len(missing) == 5  # doc/rule/gate/pipeline/backup


def test_hall_overflow_page_still_consistent(tmp_path: Path) -> None:
    """超上限馆：页截 _DISPLAY_CAP 行，账侧按同口径前 N 行复核=一致。"""
    rows = [
        {"asset_id": f"MOD:src/m{i}.py", "kind": "module", "home": f"src/m{i}.py", "status": "active"}
        for i in range(_DISPLAY_CAP + 50)
    ]
    _write_view(tmp_path, rows)
    assert tri.check_ledger_vs_view(rows, tmp_path) == []


# ---------------------------------------------------------------- 视图↔盘


def test_view_vs_disk_reports_missing_homes(tmp_path: Path) -> None:
    rows = _db_rows()
    _write_view(tmp_path, rows)
    # 盘上只造 2 个文件，其余 home 必报缺失
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "src" / "a.py").write_text("x", encoding="utf-8")
    (tmp_path / "ch.k").write_text("x", encoding="utf-8")
    findings = tri.check_view_vs_disk(tmp_path, tmp_path)
    missing = [f for f in findings if "盘面缺文件" in f]
    assert missing
    assert all("src/a.py" not in f and "ch.k" not in f for f in missing)


# ---------------------------------------------------------------- 编排面（fake conn）


class _FakeCur:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows
        self.description = [(c,) for c in ("asset_id", "kind", "home", "status")]

    def __enter__(self) -> _FakeCur:
        return self

    def __exit__(self, *args: object) -> bool:
        return False

    def execute(self, *args: object, **kwargs: object) -> None:
        pass

    def fetchall(self) -> list[tuple]:
        return [tuple(r[c] for c in ("asset_id", "kind", "home", "status")) for r in self._rows]


class _FakeConn:
    def __init__(self, rows: list[tuple]) -> None:
        self._rows = rows

    def cursor(self) -> _FakeCur:
        return _FakeCur(self._rows)

    def close(self) -> None:
        pass


def test_run_tri_check_pass_writes_report_to_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rows = _db_rows()
    _write_view(tmp_path / "docs" / "library", rows)
    (tmp_path / "src").mkdir()
    for r in rows:
        p = tmp_path / r["home"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
    monkeypatch.setattr(tri, "get_depgraph_pg_connection", lambda *a, **k: _FakeConn(rows))
    code, findings, stats = tri.run_tri_check(tmp_path, skip_regen=True)
    assert code == 0
    assert findings == []
    assert stats["ledger_rows"] == 4
    report = tmp_path / "docs" / "_working" / "ultimate_library" / "TRI_CONSISTENCY.md"
    assert report.exists()
    assert "三层一致：零断言失败" in report.read_text(encoding="utf-8")


def test_run_tri_check_findings_exit_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_view(tmp_path / "docs" / "library", _db_rows())  # 盘上无资产文件→盘断言必报
    monkeypatch.setattr(tri, "get_depgraph_pg_connection", lambda *a, **k: _FakeConn(_db_rows()))
    code, findings, _stats = tri.run_tri_check(tmp_path, skip_regen=True)
    assert code == 1
    assert findings


def test_run_tri_check_db_down_exit_2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom() -> object:
        raise RuntimeError("connection refused")

    monkeypatch.setattr(tri, "get_depgraph_pg_connection", lambda *a, **k: _boom())
    code, findings, _stats = tri.run_tri_check(tmp_path, skip_regen=True)
    assert code == 2
    assert any("总账不可达" in f for f in findings)
