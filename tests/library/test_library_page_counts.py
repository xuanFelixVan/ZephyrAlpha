# [TTL] permanent
"""馆页计数口径测试（S5 计数失真修复）："本页列出"=表格实际行数，截断提示活代码。

回归锚点：修复前 L88 报 len(rows)（馆内总数）而表格截 300 行——27,949 声明 vs ~300 实行。
"""

from __future__ import annotations

from pathlib import Path

from scripts.governance.generators.generate_library_index import _DISPLAY_CAP, _write_page


def _rows(n: int) -> list[dict]:
    return [
        {"asset_id": f"FILE:src/f{i}.py", "kind": "file", "status": "active", "home": f"src/f{i}.py"} for i in range(n)
    ]


def _table_row_count(text: str) -> int:
    count = 0
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) == 4 and cells[0] not in ("asset_id", "") and set("".join(cells)) - {"-", ":"}:
            count += 1
    return count


def test_display_cap_constant_shared_with_checker() -> None:
    """展示上限常量在册（tri-checker import 同口径，禁复制字面量）。"""
    assert _DISPLAY_CAP == 300


def test_write_page_large_hall_declares_actual_listed_rows(tmp_path: Path) -> None:
    """馆内超上限：本页列出=300（表格实际行数）≠馆内总数，截断提示出现。"""
    page = tmp_path / "code.md"
    total = 350
    _write_page(page, "DOC:docs/library/code.md", "代码馆", _rows(total), total)
    text = page.read_text(encoding="utf-8")
    assert "条目数（本页列出）：300｜馆内总数：350" in text
    assert _table_row_count(text) == _DISPLAY_CAP
    assert "（仅列前 300 条，共 350 条——全量请走总口查询）" in text


def test_write_page_small_hall_no_truncation_hint(tmp_path: Path) -> None:
    """馆内在上限内：本页列出=馆内总数，无截断提示（提示不再死代码也不再误现）。"""
    page = tmp_path / "code.md"
    _write_page(page, "DOC:docs/library/code.md", "代码馆", _rows(10), 10)
    text = page.read_text(encoding="utf-8")
    assert "条目数（本页列出）：10｜馆内总数：10" in text
    assert _table_row_count(text) == 10
    assert "仅列前" not in text
