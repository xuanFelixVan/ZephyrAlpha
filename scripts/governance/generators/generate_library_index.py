# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] scripts.governance.generators.generate_library_index
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.registry; zephyr.governance.depgraph_schema
# [CONSUMERS] generator_registry.yaml（E 包登记）；AI 冷启动链（AGENTS.md→docs/library）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读总账→生成七馆页+INDEX；产出自带索书号 frontmatter（asset_id）；页面=生成视图非真源
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 总账不可达即非零退出（不产半页）
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_library_index.py — 七馆页+INDEX 生成器（馆页=构建产物，dbt 同源模式）。

Usage::

    python scripts/governance/generators/generate_library_index.py
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/generators/generate_library_index.yaml
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.library.librarian import Librarian

__all__ = ["generate"]

_OUT_DIR: Final[Path] = Path("docs/library")

_SQL_ALL = (
    "SELECT asset_id, kind, home, status, title, fingerprint_sha256, built_at"
    " FROM lib_assets WHERE status NOT IN ('deceased','archived') ORDER BY kind, home"
)

_HALLS: Final[tuple[tuple[str, str, Any], ...]] = (
    ("code", "代码馆", lambda kind, home: kind == "module" or kind == "file"),
    ("data", "数据馆", lambda kind, home: kind == "table"),
    ("doc", "文档馆", lambda kind, home: kind == "doc"),
    ("rule", "制度馆", lambda kind, home: kind == "registry" or "/rules/" in home),
    ("gate", "闸门馆", lambda kind, home: "gov_enforcement" in home or ".pre-commit" in home),
    (
        "pipeline",
        "管线馆",
        lambda kind, home: kind in ("task", "pipeline_node", "mcp_tool") or "tasks" in home,
    ),
    ("backup", "基建与备份馆", lambda kind, home: kind in ("backup", "infra")),
)

_HALL_ASSET_IDS: Final[dict[str, str]] = {
    "code": "DOC:docs/library/code.md",
    "data": "DOC:docs/library/data.md",
    "doc": "DOC:docs/library/doc.md",
    "rule": "DOC:docs/library/rule.md",
    "gate": "DOC:docs/library/gate.md",
    "pipeline": "DOC:docs/library/pipeline.md",
    "backup": "DOC:docs/library/backup.md",
}


def _classify(kind: str, home: str) -> str:
    """按七馆谓词归类（先命中先得；缺省归代码馆）。"""
    for hall, _title, predicate in _HALLS:
        if hall != "code" and predicate(kind, home):
            return hall
    return "code"


def _write_page(path: Path, asset_id: str, title: str, rows: list[dict[str, Any]], total: int) -> None:
    """写单馆页（自带索书号 frontmatter）。"""
    lines = [
        "---",
        f'asset_id: "{asset_id}"',
        'ttl: "permanent"',
        'doc_type: "index"',
        "---",
        "",
        f"# {title}（生成视图，构建于总账 lib_assets；真源在资产本体）",
        "",
        f"- 条目数（本页列出）：{len(rows)}｜馆内总数：{total}",
        "- 索书号使用法：本页 asset_id 即本页身份；查任意资产用 `python -m zephyr.library.lookup <关键词>`",
        "",
        "| asset_id | kind | status | home |",
        "|---|---|---|---|",
    ]
    for row in rows[:300]:
        lines.append(f"| {row['asset_id']} | {row['kind']} | {row['status']} | {row['home']} |")
    if total > len(rows):
        lines.append(f"\n（仅列前 {len(rows)} 条，共 {total} 条——全量请走总口查询）")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def generate() -> dict[str, int]:
    """从总账生成七馆页+INDEX。

    Returns:
        各馆条目统计。
    """
    conn = get_depgraph_pg_connection()
    try:
        librarian = Librarian(conn)
        with conn.cursor() as cur:
            cur.execute(_SQL_ALL)
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
        halls: dict[str, list[dict[str, Any]]] = {name: [] for name, _t, _p in _HALLS}
        for row in rows:
            halls[_classify(row["kind"], row["home"])].append(row)
        _OUT_DIR.mkdir(parents=True, exist_ok=True)
        stats: dict[str, int] = {}
        for name, title, _predicate in _HALLS:
            items = halls[name]
            stats[name] = len(items)
            _write_page(_OUT_DIR / f"{name}.md", _HALL_ASSET_IDS[name], title, items, len(items))
        index_lines = [
            "---",
            'asset_id: "DOC:docs/library/INDEX.md"',
            'ttl: "permanent"',
            'doc_type: "index"',
            "---",
            "",
            "# 终极图书馆 INDEX（L1 总目，生成视图）",
            "",
            f"- 在编资产总数：{len(rows)}（deceased 除外）",
            "- 查询总口：`python -m zephyr.library.lookup <关键词>`",
            "- 冷启动链：AGENTS.md → 本页 → 七馆页 → 资产本体",
            "",
            "| 馆 | 页 | 在编数 |",
            "|---|---|---|",
        ]
        for name, title, _predicate in _HALLS:
            index_lines.append(f"| {title} | [{name}.md]({name}.md) | {stats[name]} |")
        (_OUT_DIR / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8", newline="\n")
        librarian.act(
            "audit",
            "DOC:docs/library/INDEX.md",
            actor="generate_library_index",
            detail={"stats": stats, "total": len(rows)},
        )
        for name, asset_id in _HALL_ASSET_IDS.items():
            home = f"docs/library/{name}.md"
            librarian.act(
                "register",
                asset_id,
                actor="generate_library_index",
                fields={"kind": "doc", "home": home, "title": f"{name}.md", "tags": ["library_page"]},
            )

    finally:
        conn.close()
    return stats


def main() -> int:
    """CLI 入口。"""
    stats = generate()
    print("library pages generated:", dict(Counter(stats)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
