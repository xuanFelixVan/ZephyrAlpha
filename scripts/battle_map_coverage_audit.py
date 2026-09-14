# [BLUEPRINT] MOD-SCRIPT-battle_map_coverage_audit | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md
# [MODULE] scripts.battle_map_coverage_audit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.registry_alignment（REGISTRY_SPECS 单一真源）；depgraph PG 只读
# [CONSUMERS] battle_map 治理（孤儿锚点回填裁定的证据源）；对齐巡检
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 宇宙口径=BUSINESS-REGISTRY gate 同源（REGISTRY_SPECS 19 文件/21 段，防双真源）；PG 只读；只盘点不写入（回填仍走 apply_battle_map --add-anchor 正门）；fail-open 对齐 gate 惯例（PG 异常=报告标注不误报）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(注册表目录缺失)
# [TESTS] 无（只读盘点件，输出即证据；逻辑=集合差，回归由 BUSINESS-REGISTRY gate 测试族间接覆盖）
# [A_module] module_id=MOD-SCRIPT-battle_map_coverage_audit | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""battle_map 锚点覆盖率盘点器（BM-INV-007 孤儿模块反向检测的机械化落地）。

口径：业务资产库（REGISTRY_SPECS 21 段）全部条目的 module_id 宇宙，对
battle_map_anchors(target_graph='depgraph') 求差集=孤儿模块清单。
用途：回填裁定的证据源（gate 管增量，本件管存量与漂移复测）。
用法：python scripts/battle_map_coverage_audit.py [--json]
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[1]
_CATALOGS = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"


def collect_universe() -> dict[str, set[str]]:
    """按库收集 module_id 宇宙（同 gate 真源 REGISTRY_SPECS）。"""
    from zephyr.gov_enforcement.registry_alignment import REGISTRY_SPECS

    if not _CATALOGS.exists():
        raise RuntimeError(f"注册表目录缺失: {_CATALOGS}")
    universe: dict[str, set[str]] = defaultdict(set)
    for spec in REGISTRY_SPECS:
        path = _CATALOGS / spec.filename
        if not path.exists():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for entry in data.get(spec.section) or []:
            if isinstance(entry, dict):
                mid = entry.get("module_id")
                if mid:
                    universe[spec.display].add(mid)
    return dict(universe)


def anchored_module_ids() -> set[str] | None:
    """PG 锚点已覆盖的 depgraph 目标集；PG 异常返回 None（fail-open）。"""
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(read_only=True)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT target_id FROM battle_map_anchors WHERE target_graph='depgraph'")
                return {r[0] for r in cur.fetchall()}
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001 — fail-open 对齐 gate 惯例
        print(f"WARN PG 不可用，锚点侧按未知处理: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="battle_map 锚点覆盖率盘点")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    universe = collect_universe()
    all_mids = set().union(*universe.values()) if universe else set()
    anchored = anchored_module_ids()
    report: dict = {
        "universe_modules": len(all_mids),
        "anchored_modules": len(anchored) if anchored is not None else None,
        "pg_available": anchored is not None,
        "per_registry": {},
    }
    missing_by_registry: dict[str, list[str]] = {}
    if anchored is not None:
        orphans = all_mids - anchored
        report["orphan_modules"] = len(orphans)
        report["coverage_pct"] = round(100.0 * (len(all_mids) - len(orphans)) / max(len(all_mids), 1), 2)
        for display, mids in universe.items():
            miss = sorted(mids - anchored)
            report["per_registry"][display] = {"modules": len(mids), "missing": len(miss)}
            if miss:
                missing_by_registry[display] = miss
        report["missing_detail"] = missing_by_registry

    if args.json:
        import json

        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(f"宇宙模块数: {report['universe_modules']}")
        print(f"锚点已覆盖: {report.get('anchored_modules')}")
        print(f"孤儿数: {report.get('orphan_modules')}  覆盖率: {report.get('coverage_pct')}%")
        for display, miss in missing_by_registry.items():
            print(f"[{display}] 缺 {len(miss)}: {', '.join(miss[:8])}{' ...' if len(miss) > 8 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
