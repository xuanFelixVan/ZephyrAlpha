# noqa: m02-manual-trigger  M02豁免: 本文件是运维一次性维护工具（注册表机生/对账探测），由操作者按需手动触发，非常驻服务不涉事件订阅；参数经 argparse 显式传入禁交互输入
# noqa: m11-perm-manual-legitimate  M11豁免: 同上，manual=合法运维姿势（campaign 工具族，生成器产物 chain_registry.yaml 才是常驻消费面），非自动触发缺失
# [BLUEPRINT] MOD-GOV-CHAINREG | docs/03_modules/MOD-GOV-CHAINREG.md | §
# [MODULE] scripts.governance.generate_chain_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection 只读); pathlib/datetime/argparse (stdlib)
# [CONSUMERS] scripts.governance.reconcile_chain_refs (值域对账读 chain_registry.yaml); zephyr.trading.decision_map (_XREF_SPECS chain_refs 轴 R45 校验)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读 PG（read_only 连接，零 UPDATE/DELETE）; 生成物禁手改（本文件=唯一合法再生成入口）; 覆盖判据复用 w4_1 triage canonical（禁重画），落盘前与独立 canonical SQL 交叉自校验不一致即拒写
# [MODIFY-GUARD] 输出 schema 变更须同步 decision_map.py _XREF_SPECS chain_refs 轴与 tests（chain_registry.yaml 消费方）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 覆盖数与 canonical 口径不一致→exit 2 拒写（fail-closed）；PG 不可达→异常向上抛
# [TESTS] tests/trading/test_decision_map.py::TestChainRefAxis（值域存在性/容量/未知 id 拒收）
# [TTL] permanent
# [ARCH-REF] #TDMAP-001
# [CREATION-TOKEN] chain-registry-generator-generate-chain-registry-20260922
"""chain_registry.yaml 生成器（st-tdm20-20260923 W4）。

从 PG depgraph 库 ig_chain 族机生传导链注册表（TDM chain_refs 交叉轴的值域真源）。
生成物禁手改：本文件是唯一合法再生成入口；判据复用 final3 W4-1 triage canonical
（583/873=链内存在至少 1 条链内传导边的链，禁重画另立口径）。

用法：
  python scripts/governance/generate_chain_registry.py            # 全量生成
  python scripts/governance/generate_chain_registry.py --dry-run  # 只读统计不写盘
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from zephyr.shared.utils.time_utils import now_utc

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSoT 符号唯一来源

OUTPUT = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "chain_registry.yaml"

# w4_1_conduction_triage.md §1 canonical 口径：被覆盖链=链内存在至少 1 条传导边
_COVERED_SQL = """
SELECT count(DISTINCT a.chain_id) FROM ig_node a
JOIN ig_edge e ON e.from_node = a.node_id
JOIN ig_node b ON b.node_id = e.to_node AND b.chain_id = a.chain_id
"""

_CHAINS_SQL = """
SELECT c.chain_id, c.name, c.category, c.status,
       count(DISTINCT n.node_id) AS node_count,
       count(DISTINCT e.edge_id) AS edge_count,
       (bool_or(e.edge_id IS NOT NULL)) AS covered
FROM ig_chain c
LEFT JOIN ig_node n ON n.chain_id = c.chain_id
LEFT JOIN ig_edge e ON e.from_node = n.node_id
GROUP BY c.chain_id, c.name, c.category, c.status
ORDER BY c.chain_id
"""

HEADER = """\
# ============================================================================
# 传导链注册表（chain_refs 交叉轴值域真源）——生成器产物，禁止手编
# generated_by: scripts/governance/generate_chain_registry.py（唯一合法再生成入口）
# 真源: PG depgraph 库 ig_chain/ig_node/ig_edge（DDL=scripts/industry_graph/apply_industry_graph_ddl.py）
# 覆盖判据: final3 W4-1 triage canonical——链内存在≥1条链内传导边（禁重画另立口径）
# 消费: src/zephyr/trading/decision_map.py _XREF_SPECS chain_refs 轴（R45 存在性校验）
# {banner}
# ============================================================================
"""


def _get_conn(read_only: bool = True):
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection(read_only=read_only)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="只读统计不写盘")
    args = ap.parse_args()

    conn = _get_conn(read_only=True)
    try:
        with conn.cursor() as cur:
            cur.execute(_CHAINS_SQL)
            rows = cur.fetchall()
            cur.execute(_COVERED_SQL)
            covered_canonical = cur.fetchone()[0]
    finally:
        conn.close()

    cols = ["chain_id", "name", "category", "status", "node_count", "edge_count", "covered"]
    chains = [dict(zip(cols, r, strict=True)) for r in rows]
    covered = sum(1 for c in chains if c["covered"])
    total = len(chains)
    print(f"[scan] ig_chain total={total} covered(in-chain-edge)={covered}")
    print(f"[scan] canonical SQL covered={covered_canonical}（两口径须一致，不一致=查 SQL 漂移）")
    if covered != covered_canonical:
        print("[ERROR] 覆盖数与 canonical 口径不一致，拒写", file=sys.stderr)
        return 2

    now = now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [HEADER.format(banner=f"generated_at: {now} (UTC)")]
    lines += [
        "module_id: MOD-GOV-CHAINREG",
        "ttl: permanent",
        "schema_version: '1.0'",
        "registry_id: REG-CHAIN-001",
        "name: Chain Registry",
        "name_zh: 传导链注册表",
        "description: >-",
        "  TDM chain_refs 交叉轴值域真源（机生自 PG ig_chain 族）。行=传导链身份，",
        "  只登记身份与规模读数，不复制图谱内容（图谱本体真源=ig_* 表）；",
        "  covered=链内存在至少1条传导边（w4_1 triage canonical 判据）。",
        "owner: st-tdm20-20260923",
        "tier: L",
        "status: active",
        "version: '1.0'",
        f"created: '{now[:10]}'",
        f"last_updated: '{now[:10]}'",
        "related_arch: [TDMAP-001, REG-DATAFLOW-001]",
        "unique_key: chain_id",
        "",
        "chains:",
    ]
    for c in chains:
        name = str(c["name"]).replace('"', "'")
        cat = str(c["category"] or "").replace('"', "'")
        lines.append(
            '- {chain_id: "%s", name: "%s", category: "%s", status: %s, node_count: %d, edge_count: %d, covered: %s}'
            % (c["chain_id"], name, cat, c["status"], c["node_count"], c["edge_count"],
               "true" if c["covered"] else "false")
        )
    if args.dry_run:
        print(f"[dry-run] would write {OUTPUT} ({total} chains)")
        return 0
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"[emit] {OUTPUT} ({total} chains)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
