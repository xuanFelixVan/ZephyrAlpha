# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
"""读侧"盘上存在性"标注回归（st-libstale-20261013，纯视图面）。

锁定的契约：①只有 file/doc/module 三类参与判读，命名空间型 home（含冒号非盘符）恒
unknown=不判（防误杀）；②missing 行只加尾标，行内容与传入 dict 逐字节不变（纯视图、
零账本写，且不污染世代缓存行）；③``--hide-missing`` 才剔除，缺省零行为变化；④盘符绝对
路径按自身存在性判，不拼仓根；⑤footer 计数与剔除后行数一致。

判别力自证：本册含"表类不得被误判消失"与"幽灵必须被标出"两条反向用例——把
_ON_DISK_JUDGED_KINDS 或谓词写反都会有一支红。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from zephyr.library import lookup as lookup_mod
from zephyr.library.lookup import _MISSING_ON_DISK_MARKER, _annotate_on_disk, _on_disk_state


def _row(asset_id: str, kind: str, home: str) -> dict[str, Any]:
    return {"asset_id": asset_id, "kind": kind, "status": "active", "home": home}


def test_ghost_relative_path_is_missing(tmp_path: Path) -> None:
    """仓内相对路径不存在=missing（本次落地要防的正是这一类）。"""
    assert _on_disk_state("tests/data/backup/test_stage3_vault_mtime_and_verdict.py", "file", tmp_path) == "missing"


def test_present_file_is_not_marked(tmp_path: Path) -> None:
    """盘上存在件必须 present——反向自证：谓词写反或根拼错即此支红。"""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "real_module.py").write_text("x = 1\n", encoding="utf-8")
    assert _on_disk_state("src/real_module.py", "file", tmp_path) == "present"


def test_namespace_home_is_never_judged(tmp_path: Path) -> None:
    """命名空间型 asset（计划任务/CH 表）无仓内路径概念，恒 unknown=不判。"""
    assert _on_disk_state("schtasks:\\ZephyrAlpha-BackupShadow", "task", tmp_path) == "unknown"
    assert _on_disk_state("TBL:ch:market_kline_daily", "table", tmp_path) == "unknown"
    # 表类即便 home 长得像路径也不判（kind 不在白名单）——防把"账本没这个概念"读成消失
    assert _on_disk_state("some/table-ish/name", "table", tmp_path) == "unknown"


def test_kind_outside_whitelist_is_unknown(tmp_path: Path) -> None:
    """判读面按 kind 白名单收窄：registry/infra 等一律 unknown。"""
    assert _on_disk_state("config/nope.yaml", "registry", tmp_path) == "unknown"


def test_drive_absolute_path_judged_by_itself(tmp_path: Path) -> None:
    """盘符绝对路径（仓外资产面）按自身存在性判，绝不拼到仓根下。"""
    drive = tmp_path.drive  # 形如 "C:"（POSIX 下为空 → 本支不适用）
    if not drive:
        pytest.skip("drive-letter form is Windows-only")
    assert _on_disk_state(f"{drive}\\__definitely_absent__/x.py", "file", tmp_path) == "missing"
    real = tmp_path / "outside.py"
    real.write_text("x = 1\n", encoding="utf-8")
    assert _on_disk_state(str(real), "file", tmp_path) == "present"


def test_missing_rows_have_no_backslash_drive_false_positive(tmp_path: Path) -> None:
    """反斜杠仓内相对路径同样要能判（Windows 书写形态不得退化成 unknown 而漏标）。"""
    assert _on_disk_state("docs\\nope\\gone.md", "doc", tmp_path) == "missing"


def test_annotate_keeps_rows_and_counts_missing(tmp_path: Path) -> None:
    """缺省不剔除：行全保留 + missing 计数正确；行 dict 逐字节不变（纯视图）。"""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "here.md").write_text("x\n", encoding="utf-8")
    rows = [_row("DOC:docs/here.md", "doc", "docs/here.md"), _row("DOC:docs/gone.md", "doc", "docs/gone.md")]
    snapshot = [dict(r) for r in rows]
    judged, missing = _annotate_on_disk(rows, hide_missing=False, root=tmp_path)
    assert [r["asset_id"] for r, _ in judged] == ["DOC:docs/here.md", "DOC:docs/gone.md"]
    assert [s for _, s in judged] == ["present", "missing"]
    assert missing == 1
    assert rows == snapshot  # 零突变：不往缓存行里塞键


def test_annotate_hide_missing_filters(tmp_path: Path) -> None:
    """--hide-missing 才剔除，且计数仍按判读全量报。"""
    rows = [_row("FILE:src/a.py", "file", "src/a.py"), _row("FILE:src/gone.py", "file", "src/gone.py")]
    judged, missing = _annotate_on_disk(rows, hide_missing=True, root=tmp_path)
    assert judged == []
    assert missing == 2  # 两根都不在 tmp 根下

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    judged, missing = _annotate_on_disk(rows, hide_missing=True, root=tmp_path)
    assert [r["asset_id"] for r, _ in judged] == ["FILE:src/a.py"]
    assert missing == 1


def test_state_source_index_marks_ghosts_but_keeps_has_semantics(monkeypatch, tmp_path: Path) -> None:
    """state 源①：幽灵行带尾标，但 has 仍为 True（账本证据语义本批不改，属方案③）。"""
    rows = [
        {"asset_id": "FILE:src/a.py", "kind": "file", "status": "active", "home": "src/a.py", "title": "甲"},
        {"asset_id": "FILE:src/gone.py", "kind": "file", "status": "active", "home": "src/gone.py", "title": "乙"},
    ]
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [dict(r) for r in rows])
    monkeypatch.setattr(lookup_mod, "_on_disk_root", lambda: tmp_path)

    lines, has = lookup_mod._state_source_index("anything")
    assert has is True
    assert len(lines) == 2
    assert _MISSING_ON_DISK_MARKER not in lines[0]
    assert lines[1].endswith(_MISSING_ON_DISK_MARKER)


def test_cli_main_face_marks_ghost_and_prints_footer(monkeypatch, capsys, tmp_path: Path) -> None:
    """CLI 主查询面：幽灵行带尾标 + footer 计数；存在件无尾标。"""
    ghost = _row("FILE:tests/data/backup/test_stage3_vault_mtime_and_verdict.py", "file", "tests/data/backup/x.py")
    live = _row("FILE:docs/keep.md", "file", "docs/keep.md")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "keep.md").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [dict(ghost), dict(live)])
    monkeypatch.setattr(lookup_mod, "_on_disk_root", lambda: tmp_path)

    rc = lookup_mod.main(["anything", "--no-alias"])
    out = capsys.readouterr().out
    assert rc == 0
    assert ghost["asset_id"] + "\tfile\tactive\ttests/data/backup/x.py" + _MISSING_ON_DISK_MARKER in out
    assert live["asset_id"] + "\tfile\tactive\tdocs/keep.md\n" in out
    assert "# view-only: 1/2 行 home 盘上不存在" in out


def test_cli_hide_missing_drops_ghost_row(monkeypatch, capsys, tmp_path: Path) -> None:
    """--hide-missing 剔除幽灵行；footer 分母仍按判读全量（不是剔除后行数），并报剔除数。"""
    ghost = _row("FILE:src/ghost.py", "file", "src/ghost.py")
    live = _row("FILE:docs/keep.md", "file", "docs/keep.md")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "keep.md").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [dict(ghost), dict(live)])
    monkeypatch.setattr(lookup_mod, "_on_disk_root", lambda: tmp_path)

    rc = lookup_mod.main(["anything", "--hide-missing", "--no-alias"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "FILE:src/ghost.py" not in out
    assert live["asset_id"] in out
    assert "# view-only: 1/2 行 home 盘上不存在｜已剔除 1 行" in out


def test_cli_hide_missing_all_hidden_returns_no_result(monkeypatch, capsys, tmp_path: Path) -> None:
    """全被剔除时退回既有"无结果"语义（rc=1），不输出半截表。"""
    ghost = _row("FILE:src/ghost.py", "file", "src/ghost.py")
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [dict(ghost)])
    monkeypatch.setattr(lookup_mod, "_on_disk_root", lambda: tmp_path)

    rc = lookup_mod.main(["anything", "--hide-missing", "--no-alias"])
    out = capsys.readouterr().out
    assert rc == 1
    assert out.startswith("(no results for")
