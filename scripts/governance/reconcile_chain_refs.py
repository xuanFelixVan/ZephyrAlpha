# noqa: m02-manual-trigger  M02豁免: 本文件是运维一次性维护工具（注册表机生/对账探测），由操作者按需手动触发，非常驻服务不涉事件订阅；参数经 argparse 显式传入禁交互输入
# noqa: m11-perm-manual-legitimate  M11豁免: 同上，manual=合法运维姿势（campaign 工具族，生成器产物 chain_registry.yaml 才是常驻消费面），非自动触发缺失
# [BLUEPRINT] MOD-GOV-CHAINRECON | docs/03_modules/MOD-GOV-CHAINRECON.md | §
# [MODULE] scripts.governance.reconcile_chain_refs
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection 只读, --pg 时); yaml; pathlib/datetime/argparse (stdlib)
# [CONSUMERS] docs/_working/tdm20_campaign/04_chain_recon_report.md (--write-report 产物); TDM 治理节点 TDM-E-L9-Z2 (module_ref 锚)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只报不清（零删除/零清理/零改写）; 反向覆盖判据复用 w4_1 triage canonical（covered=链内≥1传导边，禁重画）; PG fail-open（不可达降级为跳过行，不阻断读数）
# [MODIFY-GUARD] 读数口径变更须同步 04 号报告生成段与台账 D-5
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 内部异常向上抛（探测失败≠读数为零，禁静默绿）
# [TESTS] docs/_working/tdm20_campaign/04_chain_recon_report.md（首跑读数在案：8 引用/0 断链/575 未吸收）
# [TTL] permanent
# [ARCH-REF] #TDMAP-001
# [CREATION-TOKEN] chain-refs-reconciler-reconcile-chain-refs-20260922
"""chain_refs 双向对账探测器（st-tdm20-20260923 W4）。

图（trading_decision_map.yaml chain_refs 轴）↔ 库（chain_registry.yaml / PG ig_chain 族）
双向对账首跑。纪律=只报不清：本工具是遗漏探测器读数，不做任何删除/清理/改写。

方向：
  正向（图→库）：TDM 节点 chain_refs 每条必须在 chain_registry 在册（且可 --pg 复核 PG 在库）；
  反向（库→图）：583 条有效链（covered）中被 ≥1 个 TDM 节点引用的覆盖数；未被引用=遗漏读数；
  资产面：TDM 节点挂 chain_refs 的节点数 / 全图节点数（无标记=遗漏探测器读数）。

用法：
  python scripts/governance/reconcile_chain_refs.py                 # 报告打 stdout
  python scripts/governance/reconcile_chain_refs.py --write-report  # 另存战役目录 04 号件
  python scripts/governance/reconcile_chain_refs.py --pg            # 追加 PG 实库复核
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from zephyr.shared.utils.time_utils import now_utc

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSoT 符号唯一来源

MAP_YAML = REPO_ROOT / "config" / "trading_decision_map.yaml"
CHAIN_REGISTRY = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "chain_registry.yaml"
REPORT = REPO_ROOT / "docs" / "_working" / "tdm20_campaign" / "04_chain_recon_report.md"

PG_COVERED_SQL = """
SELECT count(DISTINCT a.chain_id) FROM ig_node a
JOIN ig_edge e ON e.from_node = a.node_id
JOIN ig_node b ON b.node_id = e.to_node AND b.chain_id = a.chain_id
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-report", action="store_true", help="另存 04 号对账报告（战役目录）")
    ap.add_argument("--pg", action="store_true", help="追加 PG 实库复核（只读）")
    args = ap.parse_args()

    dm = yaml.safe_load(MAP_YAML.read_text(encoding="utf-8"))
    reg = yaml.safe_load(CHAIN_REGISTRY.read_text(encoding="utf-8"))
    known = {c["chain_id"]: c for c in reg.get("chains", [])}

    refs: dict[str, list[str]] = {}
    broken: list[tuple[str, str]] = []
    for n in dm.get("nodes", []):
        for cid in n.get("chain_refs") or []:
            refs.setdefault(n["node_id"], []).append(cid)
            if cid not in known:
                broken.append((n["node_id"], cid))

    referenced = {c for lst in refs.values() for c in lst}
    covered = [c for c in known.values() if c.get("covered")]
    uncovered_valid = sorted(set(c["chain_id"] for c in covered) - referenced)
    nodes_total = len(dm.get("nodes", []))

    lines = [
        "---",
        "ttl: task_bound",
        "completes_when: 随 tdm20 战役归档（探测器再跑即刷新本件）",
        "title: chain_refs 双向对账首跑报告（st-tdm20-20260923 W4）",
        "owner: st-tdm20-20260923",
        "session: st-tdm20-20260923",
        "date: 2026-09-23",
        "---",
        "",
        "# chain_refs 双向对账首跑报告（st-tdm20-20260923 W4）",
        "",
        f"> 生成: scripts/governance/reconcile_chain_refs.py @ {now_utc().strftime('%Y-%m-%dT%H:%M:%SZ')}（UTC）",
        "> 纪律=只报不清：本报告是遗漏探测器读数，不做任何删除/清理/改写。",
        "",
        "## 读数",
        "",
        f"- 正向（图→库）：TDM chain_refs 引用合计 **{sum(len(v) for v in refs.values())}** 条，断链 **{len(broken)}** 条（须为 0）",
        f"- 反向（库→图）：有效链（covered，w4_1 triage canonical 口径）**{len(covered)}** / 873；其中被图引用 **{len(referenced & set(c['chain_id'] for c in covered))}** 条，未引用 **{len(uncovered_valid)}** 条（=传导链吸收遗漏读数，只报不清）",
        f"- 资产面：挂 chain_refs 的 TDM 节点 **{len(refs)}** / {nodes_total}（无标记节点数={nodes_total - len(refs)}=资产遗漏探测读数）",
        f"- 值域健康：chain_registry 在册 **{len(known)}** 链（生成器=scripts/governance/generate_chain_registry.py，禁手改）",
    ]
    if args.pg:
        try:
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

            conn = get_depgraph_pg_connection(read_only=True)
            try:
                with conn.cursor() as cur:
                    cur.execute(PG_COVERED_SQL)
                    pg_covered = cur.fetchone()[0]
            finally:
                conn.close()
            lines.append(f"- PG 实库复核：canonical 覆盖数={pg_covered}（与注册表 covered 口径{'一致' if pg_covered == len(covered) else '不一致=查漂移'}）")
        except Exception as e:  # noqa: BLE001 — PG fail-open，探测读数不硬阻断
            lines.append(f"- PG 实库复核：不可达（fail-open 跳过）：{e}")
    if refs:
        lines += ["", "## 节点引用明细", ""]
        for nid, lst in sorted(refs.items()):
            lines.append(f"- {nid}: {len(lst)} 条（{', '.join(lst[:4])}{'…' if len(lst) > 4 else ''}）")
    if broken:
        lines += ["", "## 断链明细（须修复）", ""]
        lines += [f"- {nid} → {cid}（不在 chain_registry）" for nid, cid in broken]

    text = "\n".join(lines) + "\n"
    print(text)
    if args.write_report:
        REPORT.write_text(text, encoding="utf-8", newline="\n")
        print(f"[emit] {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
