# [BLUEPRINT] MOD-LIB-005 | docs/03_modules/_domain_library/blueprint.md | §5
# [MODULE] zephyr.library.relations
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.librarian; zephyr.library.ledger_schema (derive_asset_id); zephyr.governance.depgraph_schema (get_depgraph_pg_connection)
# [CONSUMERS] CLI (python -m zephyr.library.relations); tests/library/test_relations.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读（depgraph nodes/edges + lib_assets 读查询）；全部 SQL 模块级常量（NO-BARE-SQL）；展开有界（visited 上限防全图爆炸）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DB 异常原样上抛；CLI 无种子返回 1
# [TESTS] tests/library/test_relations.py
# [A_module] module_id=MOD-LIB-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""relations.py — 图书馆关系树一键查询（MOD-LIB-005，W+1 Owner 点名第一项）。

从功能关键词定位种子资产，经 depgraph nodes/edges 有界 BFS 展开全部关联，
按馆归类输出树：代码（dep 边）/文档（docs 资产）/数据表/管线与任务。

Usage::

    python -m zephyr.library.relations kline_1min [depth]
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/relations.yaml
"""

from __future__ import annotations

import sys
from typing import Any, Final

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.library.librarian import Librarian, PgConnection

__all__ = ["paths_from_assets", "relations_tree", "render_relations"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_SQL_NODES_BY_PATH: Final[str] = """
SELECT node_id, path, node_type, build_status
FROM nodes WHERE path = ANY(%s) LIMIT %s
"""
_SQL_EDGES_OUT: Final[str] = """
SELECT e.to_node_id AS other_id, e.dep_type, n.path AS other_path
FROM edges e JOIN nodes n ON n.node_id = e.to_node_id
WHERE e.from_node_id = ANY(%s) LIMIT %s
"""
_SQL_EDGES_IN: Final[str] = """
SELECT e.from_node_id AS other_id, e.dep_type, n.path AS other_path
FROM edges e JOIN nodes n ON n.node_id = e.from_node_id
WHERE e.to_node_id = ANY(%s) LIMIT %s
"""
_SQL_ASSETS_BY_IDS: Final[str] = """
SELECT asset_id, kind, home, status, title
FROM lib_assets WHERE asset_id = ANY(%s) LIMIT %s
"""

_DEPTH_DEFAULT: Final[int] = 2
_DEPTH_MAX: Final[int] = 5
_VISITED_CAP: Final[int] = 400
_EDGE_LIMIT: Final[int] = 4000
_ASSET_LIMIT: Final[int] = 2000
_SEED_PATH_CAP: Final[int] = 8
_SEED_FETCH: Final[int] = 200
_SECTION_CODE: Final[str] = "代码关联（depgraph 边）"
_SECTION_DOC: Final[str] = "文档馆关联"
_SECTION_DATA: Final[str] = "数据馆关联"
_SECTION_PIPE: Final[str] = "管线/任务关联"


def _seed_sort_key(row: dict[str, Any]) -> tuple[int, int]:
    """种子相关性排序键（确定性）：代码/注册表/文档优先，同优先级短 ID 精确匹配在前。"""
    kind = str(row.get("kind", ""))
    asset_id = str(row.get("asset_id", ""))
    if kind in ("module",) or (kind == "file" and asset_id.startswith(("FILE:src/", "FILE:scripts/"))):
        priority = 0
    elif kind in ("table", "registry", "doc", "pipeline_node"):
        priority = 1
    else:
        priority = 2
    return (priority, len(asset_id))


def paths_from_assets(rows: list[dict[str, Any]]) -> list[str]:
    """从资产行提取仓库路径种子（FILE:/MOD: 两种身份证；其余忽略）。

    Args:
        rows: lib_assets 行字典列表。

    Returns:
        去重后的仓库相对路径列表（保序）。
    """
    out: list[str] = []
    seen: set[str] = set()
    for row in rows:
        asset_id = str(row.get("asset_id", ""))
        path = ""
        if asset_id.startswith("FILE:"):
            path = asset_id[len("FILE:") :]
        elif asset_id.startswith("MOD:"):
            mod = asset_id[len("MOD:") :]
            if mod.startswith("src."):
                path = mod.replace(".", "/") + ".py"
        if path and path not in seen:
            seen.add(path)
            out.append(path)
    return out


def _expand_edges(conn: PgConnection, node_ids: list[int]) -> dict[str, list[str]]:
    """一跳双向展开：返回 {邻居路径: [边标签, ...]}（含方向标注）。"""
    if not node_ids:
        return {}
    found: dict[str, list[str]] = {}
    with conn.cursor() as cur:
        for sql, label in (
            (_SQL_EDGES_OUT, "→"),
            (_SQL_EDGES_IN, "←"),
        ):
            cur.execute(sql, (list(node_ids), _EDGE_LIMIT))
            for other_id, dep_type, other_path in cur.fetchall():
                if not other_path:
                    continue
                found.setdefault(str(other_path), []).append(f"{label}{dep_type}")
    return found


def _hall_rows(conn: PgConnection, asset_ids: list[str]) -> dict[str, list[dict[str, Any]]]:
    """按馆归类资产行（代码之外的 doc/table/registry/pipeline/task 等）。"""
    if not asset_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(_SQL_ASSETS_BY_IDS, (list(asset_ids), _ASSET_LIMIT))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]
    halls: dict[str, list[dict[str, Any]]] = {
        _SECTION_DOC: [],
        _SECTION_DATA: [],
        _SECTION_PIPE: [],
    }
    for row in rows:
        kind = str(row.get("kind", ""))
        asset_id = str(row.get("asset_id", ""))
        if kind in ("doc",):
            halls[_SECTION_DOC].append(row)
        elif kind in ("table",):
            halls[_SECTION_DATA].append(row)
        elif kind in ("pipeline_node", "task", "mcp_tool", "backup", "registry"):
            halls[_SECTION_PIPE].append(row)
        elif asset_id.startswith(("DOC:", "FILE:docs/")):
            halls[_SECTION_DOC].append(row)
    return halls


def render_relations(
    keyword: str,
    seeds: list[dict[str, Any]],
    code_rows: list[dict[str, Any]],
    halls: dict[str, list[dict[str, Any]]],
    depth_used: int,
) -> str:
    """渲染关系树文本（纯函数，零 IO）。"""
    lines: list[str] = [f"关系树: {keyword!r}（展开深度={depth_used}）"]
    lines.append(f"├─ 种子资产 ×{len(seeds)}")
    for row in seeds[:20]:
        lines.append(
            f"│  ├─ {row.get('asset_id', '')} [{row.get('kind', '')}] {row.get('status') or ''} {row.get('title') or ''}".rstrip()
        )
    lines.append(f"├─ {_SECTION_CODE} ×{len(code_rows)}")
    for row in code_rows[:60]:
        labels = ",".join(row.get("labels", []))
        lines.append(f"│  ├─ {row.get('path', '')} [{row.get('node_type', '')}] {labels}".rstrip())
    for section in (_SECTION_DOC, _SECTION_DATA, _SECTION_PIPE):
        rows = halls.get(section, [])
        lines.append(f"├─ {section} ×{len(rows)}")
        for row in rows[:40]:
            lines.append(f"│  ├─ {row.get('asset_id', '')} [{row.get('kind', '')}] {row.get('title') or ''}".rstrip())
    lines.append("└─ （树完；只读视图，真源=depgraph+lib_assets）")
    return "\n".join(lines)


def _bfs_expand(
    conn: PgConnection, seed_paths: list[str], depth: int
) -> tuple[set[str], dict[str, list[str]], dict[str, dict[str, Any]], int]:
    """有界 BFS：沿 depgraph 边展开邻接路径。

    Args:
        conn: PG 连接（只读）。
        seed_paths: 种子路径。
        depth: 展开深度。

    Returns:
        (visited_paths, labels_by_path, path_meta, depth_used)。
    """
    with conn.cursor() as cur:
        cur.execute(_SQL_NODES_BY_PATH, (list(seed_paths), _VISITED_CAP))
        node_rows = cur.fetchall()
    node_id_by_path = {str(row[1]): int(row[0]) for row in node_rows}
    path_meta = {str(row[1]): {"node_type": row[2], "build_status": row[3]} for row in node_rows}

    visited_paths: set[str] = set(seed_paths)
    frontier_paths = list(seed_paths)
    labels_by_path: dict[str, list[str]] = {}
    depth_used = 0
    for _ in range(depth):
        depth_used += 1
        node_ids = [node_id_by_path[p] for p in frontier_paths if p in node_id_by_path]
        if not node_ids or len(visited_paths) >= _VISITED_CAP:
            break
        neighbors = _expand_edges(conn, node_ids)
        next_frontier: list[str] = []
        for npath, nlabels in neighbors.items():
            cur_labels = labels_by_path.setdefault(npath, [])
            for lab in nlabels:
                if lab not in cur_labels:
                    cur_labels.append(lab)
            if npath not in visited_paths:
                visited_paths.add(npath)
                next_frontier.append(npath)
                if len(visited_paths) >= _VISITED_CAP:
                    break
        frontier_paths = next_frontier
        if not frontier_paths:
            break
    return visited_paths, labels_by_path, path_meta, depth_used


def _merge_seed_rows(halls: dict[str, list[dict[str, Any]]], ranked: list[dict[str, Any]]) -> None:
    """种子资产按馆归类并入 halls（原地，去重）。"""
    for row in ranked:
        kind = str(row.get("kind", ""))
        section = ""
        if kind == "table":
            section = _SECTION_DATA
        elif kind in ("doc",) or str(row.get("asset_id", "")).startswith(("DOC:", "FILE:docs/")):
            section = _SECTION_DOC
        elif kind in ("pipeline_node", "task", "mcp_tool", "backup", "registry"):
            section = _SECTION_PIPE
        if section:
            known = {str(r.get("asset_id")) for r in halls.get(section, [])}
            if str(row.get("asset_id", "")) not in known:
                halls.setdefault(section, []).append(row)


def relations_tree(conn: PgConnection, keyword: str, depth: int = _DEPTH_DEFAULT) -> tuple[str, int]:
    """主流程：种子定位→depgraph 有界 BFS→馆归类→渲染。

    Args:
        conn: PG 连接（depgraph 库，只读使用）。
        keyword: 功能关键词。
        depth: BFS 展开深度（1..5）。

    Returns:
        (树文本, 命中种子数)。
    """
    depth = max(1, min(int(depth), _DEPTH_MAX))
    librarian = Librarian(conn)
    seeds = librarian.lookup(keyword, limit=_SEED_FETCH)
    if not seeds:
        return (f"(no seed assets for {keyword!r})", 0)

    ranked = sorted(seeds, key=_seed_sort_key)
    seed_paths = paths_from_assets(ranked)[:_SEED_PATH_CAP]
    visited_paths, labels_by_path, path_meta, depth_used = _bfs_expand(conn, seed_paths, depth)

    code_rows: list[dict[str, Any]] = []
    for path in sorted(labels_by_path):
        meta = path_meta.get(path, {})
        code_rows.append(
            {
                "path": path,
                "node_type": meta.get("node_type", ""),
                "labels": labels_by_path[path],
            }
        )

    reached_ids = [f"FILE:{p}" for p in visited_paths]
    halls = _hall_rows(conn, reached_ids)
    _merge_seed_rows(halls, ranked)
    text = render_relations(keyword, ranked, code_rows, halls, depth_used)
    return (text, len(seeds))


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：python -m zephyr.library.relations <keyword> [depth]。

    Args:
        argv: 命令行参数（默认 sys.argv[1:]）。

    Returns:
        退出码：0=有种子，1=无种子或用法错误。
    """
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("usage: python -m zephyr.library.relations <keyword> [depth]")
        return 1
    depth = _DEPTH_DEFAULT
    if len(args) > 1:
        try:
            depth = int(args[1])
        except ValueError:
            print(f"invalid depth: {args[1]!r}")
            return 1
    conn = get_depgraph_pg_connection()
    try:
        text, seeds = relations_tree(conn, args[0], depth=depth)
    finally:
        conn.close()
    print(text)
    return 0 if seeds else 1


if __name__ == "__main__":
    raise SystemExit(main())
