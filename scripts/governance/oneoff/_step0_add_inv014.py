# [BLUEPRINT] SH-GOV-001 | scripts/governance/oneoff/
# [MODULE] scripts.governance.oneoff._step0_add_inv014
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] apply_depgraph.py
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] oneoff
# [INVARIANTS] 补登记INV-014幸存者偏差铁律到3个关键D_DATA节点gate_reason；depgraph修改通过_load_depgraph+_atomic_write受控函数
# [MODIFY-GUARD] none
# [STABILITY] ephemeral
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] dry-run->退出码0; 执行成功->退出码0; depgraph不可达->退出码2
# [TESTS] python scripts/governance/oneoff/_step0_add_inv014.py --dry-run
# [TTL] task_bound
"""Step 0 补登记：为3个关键D_DATA节点添加INV-014幸存者偏差铁律gate_reason。

INV-014来自场外project-entity-depgraph.yaml：
  category: data_integrity
  statement: Survivorship Bias零容忍：回测数据集必须包含退市/停牌标的
  owner_domain: D-DATA
  violation_action: fail_backtest
  priority: P0
  runtime_plane: cold

目标节点（PIT/质量/完整性——幸存者偏差的核心防线）：
  1. pit_query.py (nid=7062813) — PIT AS OF JOIN必须包含退市标的
  2. quality_gate.py (nid=7062815) — 质量门禁校验退市标的覆盖
  3. integrity_checker.py (nid=7062802) — 完整性校验退市标的存在

用法：
  python scripts/governance/oneoff/_step0_add_inv014.py --dry-run   # 预览
  python scripts/governance/oneoff/_step0_add_inv014.py              # 执行
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_GOVERNANCE_DIR = _REPO_ROOT / "scripts" / "governance"
for _p in (str(_REPO_ROOT), str(_GOVERNANCE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apply_depgraph import _load_depgraph, _atomic_write  # noqa: E402

# ============================================================
# INV-014 gate_reason 文本
# ============================================================
INV_014_GATE = (
    "INV-014: 幸存者偏差零容忍——回测数据集必须包含退市/停牌标的，"
    "PIT AS OF JOIN禁止只查当前存续标的；violation_action=fail_backtest，priority=P0"
)

# ============================================================
# 目标节点：path -> node_id（通过_load_depgraph动态查找）
# ============================================================
TARGET_PATHS = [
    "src/zephyr/data/pit_query.py",
    "src/zephyr/data/quality_gate.py",
    "src/zephyr/data/integrity_checker.py",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="补登记INV-014到D_DATA关键节点")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写DB")
    args = parser.parse_args()

    print(f"=== 补登记INV-014 (dry_run={args.dry_run}) ===\n")

    dep = _load_depgraph()
    nodes = dep.get("nodes", {})

    changes = 0
    for nid, node in nodes.items():
        path = node.get("path", "")
        if path not in TARGET_PATHS:
            continue
        domain = node.get("domain_id", "")
        if domain != "D_DATA":
            print(f"  SKIP: {path} domain={domain} (非D_DATA)")
            continue
        old_gate = node.get("gate_reason") or ""
        if "INV-014" in old_gate:
            print(f"  EXISTS: {path} 已有INV-014 gate_reason")
            continue
        if args.dry_run:
            print(f"  [DRY RUN] {path}")
            print(f"            old_gate: {old_gate[:60] if old_gate else '(empty)'}")
            print(f"            new_gate: {INV_014_GATE[:60]}...")
            changes += 1
        else:
            node["gate_reason"] = INV_014_GATE
            print(f"  OK: {path}")
            print(f"      gate_reason set to INV-014")
            changes += 1

    print(f"\n变更节点数: {changes}")

    if changes > 0 and not args.dry_run:
        _atomic_write(dep)
        print("[OK] 已写回DB")
    elif args.dry_run:
        print("[DRY RUN] 未写DB")

    print("\n下一步：运行 align_panoramas.py 验证四图对齐")
    return 0


if __name__ == "__main__":
    sys.exit(main())
