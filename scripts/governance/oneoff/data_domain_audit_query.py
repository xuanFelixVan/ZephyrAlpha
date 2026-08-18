# [BLUEPRINT] SH-GOV-001 | scripts/governance/oneoff/
# [MODULE] scripts.governance.oneoff.data_domain_audit_query
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] oneoff
# [INVARIANTS] 数据域 DB 现状只读查询（Phase 2）；不写 DB
# [MODIFY-GUARD] none
# [STABILITY] ephemeral
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 执行成功->退出码0; depgraph不可达->退出码2
# [TESTS] python scripts/governance/oneoff/data_domain_audit_query.py
# [TTL] task_bound
"""数据域设计态排查 - DB 现状查询（Phase 2，只读不写）。

查询场内 depgraph DB 中所有数据相关域的现状：
  domains / nodes / edges / contracts / domain_dependencies

输出：
  - stdout：表 schema + 摘要统计
  - 文件：完整明细（data_domain_audit_report_db.md）
"""
from __future__ import annotations

__manifest__ = """
args: []
description: 数据域设计态排查 - DB 现状查询（Phase 2，只读不写）。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

# 让脚本能 import zephyr.*
_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

DATA_DOMAINS = [
    "D_DATA",
    "D_MKT_DATA",
    "D_DATA_ENG",
    "D_DATA_GOV",
    "D_DATA_SEC",
    "D_ALT_DATA",
]

REPORT_FILE = Path(__file__).resolve().parent / "data_domain_audit_report_db.md"

# ============================================================
# SQL 集中化（NO-BARE-SQL 门禁，§5.160.2）
# ============================================================
SQL_SCHEMA_COLUMNS = (
    "SELECT column_name, data_type FROM information_schema.columns "
    "WHERE table_name = %s ORDER BY ordinal_position"
)
SQL_DOMAINS_ALL = "SELECT * FROM domains ORDER BY domain_id"
SQL_NODE_STATS = (
    "SELECT domain_id, design_maturity, build_status, COUNT(*) AS n "
    "FROM nodes WHERE domain_id = ANY(%s) "
    "GROUP BY domain_id, design_maturity, build_status "
    "ORDER BY domain_id, design_maturity, build_status"
)
SQL_NODE_DETAILS = (
    "SELECT path, domain_id, subdomain_id, design_maturity, build_status, "
    "gate_reason, architecture_layer, node_type, node_name, "
    "blueprint_id, belongs_to FROM nodes "
    "WHERE domain_id = ANY(%s) ORDER BY domain_id, path"
)
SQL_EDGE_STATS_TOTAL = (
    "SELECT COUNT(*) AS total, "
    "SUM(CASE WHEN nf.domain_id = ANY(%s) AND nt.domain_id = ANY(%s) THEN 1 ELSE 0 END) AS intra, "
    "SUM(CASE WHEN nf.domain_id = ANY(%s) OR nt.domain_id = ANY(%s) THEN 1 ELSE 0 END) AS touched "
    "FROM edges e JOIN nodes nf ON e.from_node_id = nf.node_id "
    "JOIN nodes nt ON e.to_node_id = nt.node_id"
)
SQL_EDGE_STATS_GROUPED = (
    "SELECT nf.domain_id AS from_dom, nt.domain_id AS to_dom, "
    "e.dep_type, e.dep_maturity, e.cross_domain, COUNT(*) AS n "
    "FROM edges e JOIN nodes nf ON e.from_node_id = nf.node_id "
    "JOIN nodes nt ON e.to_node_id = nt.node_id "
    "WHERE nf.domain_id = ANY(%s) OR nt.domain_id = ANY(%s) "
    "GROUP BY nf.domain_id, nt.domain_id, e.dep_type, e.dep_maturity, e.cross_domain "
    "ORDER BY nf.domain_id, nt.domain_id, e.dep_type"
)
SQL_EDGE_DETAILS = (
    "SELECT nf.path AS from_path, nt.path AS to_path, "
    "nf.domain_id AS from_dom, nt.domain_id AS to_dom, "
    "e.dep_type, e.dep_maturity, e.cross_domain, e.used_symbol "
    "FROM edges e JOIN nodes nf ON e.from_node_id = nf.node_id "
    "JOIN nodes nt ON e.to_node_id = nt.node_id "
    "WHERE nf.domain_id = ANY(%s) OR nt.domain_id = ANY(%s) "
    "ORDER BY nf.domain_id, nt.domain_id, nf.path"
)
SQL_CONTRACTS = (
    "SELECT contract_id, name, provider_domain, consumer_domain, "
    "contract_type, fulfillment_status, version, target_phase, gap "
    "FROM contracts "
    "WHERE provider_domain = ANY(%s) OR consumer_domain = ANY(%s) "
    "ORDER BY provider_domain, contract_id"
)
SQL_DOMAIN_DEPS = (
    "SELECT from_domain, to_domain, edge_count, edge_types, constraint_type "
    "FROM domain_dependencies "
    "WHERE from_domain = ANY(%s) OR to_domain = ANY(%s) "
    "ORDER BY from_domain, to_domain"
)


def _rows(cur):
    """_rows implementation."""
    return [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    lines: list[str] = []

    def out(s: str = "") -> None:
        """out implementation."""
        lines.append(s)
        print(s)

    # ── 0. 相关表 schema ──────────────────────────────────────────
    out("=" * 90)
    out("0. 相关表 schema（nodes / edges / domains / contracts / domain_dependencies）")
    out("=" * 90)
    for tbl in ["nodes", "edges", "domains", "contracts", "domain_dependencies"]:
        cur.execute(SQL_SCHEMA_COLUMNS, (tbl,))
        out(f"\n[{tbl}]")
        for r in cur.fetchall():
            out(f"  {r[0]:32s} {r[1]}")

    # ── 1. domains 全表 ──────────────────────────────────────────
    out("\n" + "=" * 90)
    out("1. domains 全表")
    out("=" * 90)
    cur.execute(SQL_DOMAINS_ALL)
    cols = [c[0] for c in cur.description]
    out(" | ".join(cols))
    for r in cur.fetchall():
        out(" | ".join("" if x is None else str(x) for x in r))

    # ── 2. 数据相关域节点统计 ────────────────────────────────────
    out("\n" + "=" * 90)
    out("2. 数据相关域节点统计（domain_id × design_maturity × build_status）")
    out("=" * 90)
    cur.execute(SQL_NODE_STATS, (DATA_DOMAINS,))
    out("domain_id | design_maturity | build_status | n")
    for r in cur.fetchall():
        out(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")

    # ── 3. 数据相关域节点明细 ────────────────────────────────────
    out("\n" + "=" * 90)
    out("3. 数据相关域节点明细（写入报告文件）")
    out("=" * 90)
    cur.execute(SQL_NODE_DETAILS, (DATA_DOMAINS,))
    node_rows = _rows(cur)
    out(f"共 {len(node_rows)} 个节点，明细见报告文件 §3")

    # ── 4. 数据相关域边统计 + 明细 ───────────────────────────────
    out("\n" + "=" * 90)
    out("4. 数据相关域边统计")
    out("=" * 90)
    cur.execute(
        SQL_EDGE_STATS_TOTAL,
        (DATA_DOMAINS, DATA_DOMAINS, DATA_DOMAINS, DATA_DOMAINS),
    )
    r = cur.fetchone()
    out(f"涉及数据域的边总数={r[0]} | 域内边={r[1]} | 触及数据域的边={r[2]}")

    cur.execute(SQL_EDGE_STATS_GROUPED, (DATA_DOMAINS, DATA_DOMAINS))
    out("from_dom | to_dom | dep_type | dep_maturity | cross_domain | n")
    edge_stat = cur.fetchall()
    for r in edge_stat:
        out(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

    cur.execute(SQL_EDGE_DETAILS, (DATA_DOMAINS, DATA_DOMAINS))
    edge_rows = _rows(cur)
    out(f"边明细 {len(edge_rows)} 条，见报告文件 §4")

    # ── 5. 数据相关域契约 ────────────────────────────────────────
    out("\n" + "=" * 90)
    out("5. 数据相关域契约（provider_domain 或 consumer_domain 命中数据域）")
    out("=" * 90)
    cur.execute(SQL_CONTRACTS, (DATA_DOMAINS, DATA_DOMAINS))
    contract_rows = _rows(cur)
    out(f"共 {len(contract_rows)} 个契约：")
    out("contract_id | name | provider | consumer | type | fulfillment | version | phase | gap")
    for r in contract_rows:
        out(
            f"{r['contract_id']} | {r.get('name')} | {r['provider_domain']} | "
            f"{r['consumer_domain']} | {r['contract_type']} | {r['fulfillment_status']} | "
            f"{r.get('version')} | {r.get('target_phase')} | {r.get('gap')}"
        )

    # ── 6. domain_dependencies 中数据域记录 ─────────────────────
    out("\n" + "=" * 90)
    out("6. domain_dependencies 中数据域记录")
    out("=" * 90)
    cur.execute(SQL_DOMAIN_DEPS, (DATA_DOMAINS, DATA_DOMAINS))
    dd_rows = _rows(cur)
    out("from_domain | to_domain | edge_count | edge_types | constraint_type")
    for r in dd_rows:
        out(
            f"{r['from_domain']} | {r['to_domain']} | {r.get('edge_count')} | "
            f"{r.get('edge_types')} | {r.get('constraint_type')}"
        )

    conn.close()

    # ── 写完整明细到报告文件 ─────────────────────────────────────
    with REPORT_FILE.open("w", encoding="utf-8") as f:
        f.write("# 数据域 DB 现状完整明细报告\n\n")
        f.write("## §3 节点明细（{} 个）\n\n".format(len(node_rows)))
        f.write(
            "| path | domain_id | subdomain_id | design_maturity | build_status | "
            "gate_reason | layer | node_type | node_name | blueprint_id | belongs_to |\n"
        )
        f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in node_rows:
            f.write(
                f"| {r['path']} | {r['domain_id']} | {r.get('subdomain_id')} | "
                f"{r.get('design_maturity')} | {r.get('build_status')} | "
                f"{r.get('gate_reason')} | {r.get('architecture_layer')} | "
                f"{r.get('node_type')} | {r.get('node_name')} | "
                f"{r.get('blueprint_id')} | {r.get('belongs_to')} |\n"
            )

        f.write("\n## §4 边明细（{} 条）\n\n".format(len(edge_rows)))
        f.write(
            "| from_path | to_path | from_dom | to_dom | dep_type | "
            "dep_maturity | cross_domain | used_symbol |\n"
        )
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in edge_rows:
            f.write(
                f"| {r['from_path']} | {r['to_path']} | {r['from_dom']} | {r['to_dom']} | "
                f"{r['dep_type']} | {r.get('dep_maturity')} | {r.get('cross_domain')} | "
                f"{r.get('used_symbol')} |\n"
            )

    print(f"\n[完整明细已写入] {REPORT_FILE}")


if __name__ == "__main__":
    main()
