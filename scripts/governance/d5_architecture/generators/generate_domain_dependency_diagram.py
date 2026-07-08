# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_dependency_diagram
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""G3: 从 depgraph (PostgreSQL) edges 表生成指定域的全景依赖图(.mmd Mermaid格式)

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_dependency_diagram
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到generated/domains/
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/domains/{domain}_dependency.mmd
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1;域不存在→exit 2
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# 治本（2026-07-04）：DB_DISPLAY_NAME 前移到 __manifest__ 之前，避免 f-string 求值时 NameError。
# _common.py 与本文件同目录（generators/），CLI 运行时 sys.path[0]=本目录，可直接 import。
from _common import cleanup_stale_files, DB_DISPLAY_NAME  # noqa: E402

__manifest__ = f"""
args: []
description: 'G3: 从 {DB_DISPLAY_NAME} edges 表生成指定域的全景依赖图(.mmd Mermaid格式)'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from domain_name_mapping import get_domain_name_zh
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "generated" / "domains"


def sanitize_node_id(path: str) -> str:
    """将路径转换为合法的 Mermaid 节点ID。"""
    # 替换非法字符
    safe = path.replace("/", "_").replace("\\", "_").replace(".", "_").replace("-", "_")
    safe = safe.replace(" ", "_").replace(":", "_").replace("(", "").replace(")", "")
    safe = safe.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
    # 截断过长的ID
    if len(safe) > 60:
        safe = safe[:30] + "___" + safe[-27:]
    return safe


def shorten_path(path: str, max_len: int = 40) -> str:
    """缩短路径用于显示。"""
    if len(path) <= max_len:
        return path
    return "..." + path[-(max_len - 3) :]


def _is_ghost(path: str) -> bool:
    """检查节点路径是否为 ghost（path 非空但磁盘上不存在）。

    第一性原理治本：即使不手动 deprecate，生成器也自动过滤幽灵文件，
    防止架构文档引用已删除的文件。铁律保障：新 AI 不需要知道要跑 deprecate。
    """
    return bool(path) and not (REPO_ROOT / path).exists()


def get_domain_nodes(conn: PgConnExecuteWrapper, domain_id: str) -> list[dict]:
    """查询指定域的所有节点（排除 deprecated 和 ghost 节点）。"""
    cur = conn.execute(
        "SELECT node_id, path, design_maturity FROM nodes WHERE domain_id=%s AND build_status != 'deprecated' ORDER BY path",
        (domain_id,),
    )
    return [
        {"node_id": r["node_id"], "path": r["path"] or "", "design_maturity": r["design_maturity"] or ""}
        for r in cur.fetchall()
        if not _is_ghost(r["path"] or "")
    ]


def get_domain_edges(conn: PgConnExecuteWrapper, domain_id: str) -> list[dict]:
    """查询涉及指定域的所有边（域内+跨域，排除 deprecated 和 ghost 节点的边）。"""
    cur = conn.execute(
        """SELECT e.from_node_id, n1.path AS from_path, n1.domain_id AS from_domain,
                  e.to_node_id, n2.path AS to_path, n2.domain_id AS to_domain,
                  e.dep_type, e.coupling_strength
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE (n1.domain_id=%s OR n2.domain_id=%s)
             AND n1.build_status != 'deprecated'
             AND n2.build_status != 'deprecated'
           ORDER BY e.edge_id""",
        (domain_id, domain_id),
    )
    return [
        {
            "from_id": r["from_node_id"],
            "from_path": r["from_path"] or "",
            "from_domain": r["from_domain"] or "",
            "to_id": r["to_node_id"],
            "to_path": r["to_path"] or "",
            "to_domain": r["to_domain"] or "",
            "dep_type": r["dep_type"] or "",
            "coupling": r["coupling_strength"] or "",
        }
        for r in cur.fetchall()
        if not _is_ghost(r["from_path"] or "") and not _is_ghost(r["to_path"] or "")
    ]


def generate_dependency_diagram(domain_id: str, conn: PgConnExecuteWrapper) -> str:
    """生成域全景依赖图(.mmd)。"""
    # 验证域存在
    cur = conn.execute("SELECT domain_name FROM domains WHERE domain_id=%s", (domain_id,))
    row = cur.fetchone()
    if not row:
        print(f"ERROR: 域 '{domain_id}' 不存在", file=sys.stderr)
        return ""
    domain_name = get_domain_name_zh(domain_id, row["domain_name"] or domain_id)

    nodes = get_domain_nodes(conn, domain_id)
    edges = get_domain_edges(conn, domain_id)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_domain = domain_id.replace("-", "_")

    lines = []
    lines.append(f"%% {domain_id} 域全景依赖图")
    lines.append(f"%% 生成时间: {now}")
    lines.append(f"%% 数据源: {DB_DISPLAY_NAME} nodes表 + edges表")
    lines.append(f"%% 模块数: {len(nodes)}, 依赖边数: {len(edges)}")
    lines.append("")
    lines.append("graph TD")
    lines.append("")

    # 域内模块（限制数量避免图表过大）
    MAX_NODES = 100
    lines.append(f"    %% 域内模块（最多显示 {MAX_NODES} 个）")
    lines.append(f"    subgraph {safe_domain}[{domain_name}]")

    # 构建 node_id -> path 映射
    node_map = {n["node_id"]: n for n in nodes}
    displayed_node_ids = set()

    for n in nodes[:MAX_NODES]:
        node_id_safe = sanitize_node_id(n["path"])
        short_path = shorten_path(n["path"])
        maturity_tag = f"[{n['design_maturity']}]" if n["design_maturity"] else ""
        lines.append(f'        {node_id_safe}["{short_path} {maturity_tag}"]')
        displayed_node_ids.add(n["node_id"])

    if len(nodes) > MAX_NODES:
        lines.append(f"        %% ... 还有 {len(nodes) - MAX_NODES} 个模块未显示")
    lines.append("    end")
    lines.append("")

    # 分类边：域内边和跨域边
    internal_edges = []
    incoming_cross = []  # 跨域入边（其他域 -> 本域）
    outgoing_cross = []  # 跨域出边（本域 -> 其他域）

    for e in edges:
        if e["from_domain"] == domain_id and e["to_domain"] == domain_id:
            internal_edges.append(e)
        elif e["to_domain"] == domain_id:
            incoming_cross.append(e)
        elif e["from_domain"] == domain_id:
            outgoing_cross.append(e)

    # 域内依赖（限制数量）
    MAX_INTERNAL = 80
    lines.append(f"    %% 域内依赖（最多显示 {MAX_INTERNAL} 条）")
    for e in internal_edges[:MAX_INTERNAL]:
        from_safe = sanitize_node_id(e["from_path"])
        to_safe = sanitize_node_id(e["to_path"])
        dep_label = e["dep_type"] or "dep"
        lines.append(f"    {from_safe} -->|{dep_label}| {to_safe}")
    if len(internal_edges) > MAX_INTERNAL:
        lines.append(f"    %% ... 还有 {len(internal_edges) - MAX_INTERNAL} 条域内依赖未显示")
    lines.append("")

    # 跨域入边（其他域 -> 本域）
    MAX_CROSS = 30
    lines.append(f"    %% 跨域依赖（入）- 最多显示 {MAX_CROSS} 条")
    # 按源域分组
    incoming_by_domain: dict[str, list] = {}
    for e in incoming_cross:
        incoming_by_domain.setdefault(e["from_domain"], []).append(e)

    for src_domain, src_edges in sorted(incoming_by_domain.items()):
        src_safe = src_domain.replace("-", "_")
        lines.append(f"    %% {src_domain} -> {domain_id} ({len(src_edges)} 条)")
        for e in src_edges[:MAX_CROSS]:
            from_safe = sanitize_node_id(e["from_path"])
            to_safe = sanitize_node_id(e["to_path"])
            dep_label = e["dep_type"] or "dep"
            # 只显示目标节点（本域节点），源节点用域ID表示
            lines.append(f"    {src_safe}[{src_domain}] -->|{dep_label}| {to_safe}")
    lines.append("")

    # 跨域出边（本域 -> 其他域）
    lines.append(f"    %% 跨域依赖（出）- 最多显示 {MAX_CROSS} 条")
    outgoing_by_domain: dict[str, list] = {}
    for e in outgoing_cross:
        outgoing_by_domain.setdefault(e["to_domain"], []).append(e)

    for tgt_domain, tgt_edges in sorted(outgoing_by_domain.items()):
        tgt_safe = tgt_domain.replace("-", "_")
        lines.append(f"    %% {domain_id} -> {tgt_domain} ({len(tgt_edges)} 条)")
        for e in tgt_edges[:MAX_CROSS]:
            from_safe = sanitize_node_id(e["from_path"])
            to_safe = tgt_safe
            dep_label = e["dep_type"] or "dep"
            lines.append(f"    {from_safe} -->|{dep_label}| {to_safe}[{tgt_domain}]")
    lines.append("")

    # 统计
    lines.append("    %% 统计")
    lines.append(f"    %% 域内依赖: {len(internal_edges)} 条")
    lines.append(f"    %% 跨域入边: {len(incoming_cross)} 条")
    lines.append(f"    %% 跨域出边: {len(outgoing_cross)} 条")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """入口：生成域全景依赖图。"""
    parser = argparse.ArgumentParser(description="G3: 生成域全景依赖图(.mmd)")
    parser.add_argument("domain_id", type=str, nargs="?", default=None, help="域ID (如 D_TRADING)。--all 模式下可省略")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--all", action="store_true", help="生成所有域的依赖图")
    args = parser.parse_args()

    if not args.all and not args.domain_id:
        parser.error("domain_id 是必填参数（除非使用 --all）")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        if args.all:
            cur = conn.execute("SELECT domain_id FROM domains ORDER BY domain_id")
            domain_ids = [r["domain_id"] for r in cur.fetchall()]
            success = 0
            for did in domain_ids:
                content = generate_dependency_diagram(did, conn)
                if content:
                    safe_name = did.replace("-", "_").lower()
                    out_path = output_dir / f"{safe_name}_dependency.mmd"
                    out_path.write_text(content, encoding="utf-8")
                    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
                    success += 1
            print(f"\n共生成 {success}/{len(domain_ids)} 个域依赖图")
            # 清理孤儿 .mmd 文件（治本：解决只增不删，参考 generate_domain_doc.py）
            expected_basenames = {f"{did.replace('-', '_').lower()}_dependency.mmd" for did in domain_ids}
            deleted_mmd = cleanup_stale_files(
                output_dir, expected_basenames, r'^[a-z0-9_]+_dependency\.mmd$'
            )
            if deleted_mmd:
                print(f"[CLEANUP] 删除 {len(deleted_mmd)} 个残留 .mmd: {deleted_mmd}")
        else:
            content = generate_dependency_diagram(args.domain_id, conn)
            if not content:
                sys.exit(2)
            safe_name = args.domain_id.replace("-", "_").lower()
            out_path = output_dir / f"{safe_name}_dependency.mmd"
            out_path.write_text(content, encoding="utf-8")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
