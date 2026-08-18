#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV_DEFERRED_EDGES | docs/_working/2026-07-28-three_systems_upgrade_plan.md | §8
# [MODULE] scripts.governance.add_deferred_design_edges
# [DOMAIN] D_GOV_SCRIPTS
# [STARTUP] manual
# [MATURITY] production
# [SAFETY] L
# [A_module] module_id=MOD-GOV_DEFERRED_EDGES | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
为暂缓模块添加设计态依赖边（dep_maturity='design'）。

约束：add_design_edge 要求双端 design_maturity='design'。
  - 设计态边只能连接两个设计态节点（暂缓→暂缓）
  - 暂缓→生产的依赖是隐式的，等代码写好后扫描器自动创建 active 边

边的方向：from(消费者) → to(提供者)，即 from 依赖 to。
"""
from __future__ import annotations

__manifest__ = """
args: []
description: 为暂缓模块添加设计态依赖边（dep_maturity='design'）。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src"), str(_REPO_ROOT / "scripts" / "governance")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import apply_depgraph

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection, release_depgraph_pg_connection

# ============================================================
# 设计态依赖边定义
# ============================================================
# 格式: (from_path, to_path, dep_type, coupling, api_contract_refs, event_ref, data_transfer_description)
# 方向: from(消费者) → to(提供者)

DESIGN_EDGES = [
    # --- 因子域：Barra 风险模型链 ---
    # D-FACTOR-11 暴露计算器 → D-FACTOR-06 Barra风险模型
    ("src/zephyr/factor/barra/exposure_calculator/",
     "src/zephyr/factor/barra/risk_model/",
     "import", "critical", "CTR-002", "",
     "Barra风格因子→因子暴露计算"),
    # D-FACTOR-24 风险预算分配器 → D-FACTOR-11 暴露计算器
    ("src/zephyr/factor/barra/risk_budget_allocator/",
     "src/zephyr/factor/barra/exposure_calculator/",
     "import", "critical", "CTR-002", "",
     "因子暴露→风险预算分配"),
    # D-FACTOR-24 风险预算分配器 → D-FACTOR-06 Barra风险模型
    ("src/zephyr/factor/barra/risk_budget_allocator/",
     "src/zephyr/factor/barra/risk_model/",
     "import", "medium", "CTR-002", "",
     "Barra因子→风险预算约束"),
    # D-FACTOR-10 换手率分析器 → D-FACTOR-09 相关性分析器
    ("src/zephyr/factor/analysis/turnover_analyzer/",
     "src/zephyr/factor/analysis/correlation_analyzer/",
     "import", "medium", "", "",
     "相关性矩阵→换手率分析输入"),

    # --- 数据工程域：流处理链 ---
    # D-DATA-ENG-06 流处理引擎 → D-DATA-04 实时行情推送管理器
    ("src/zephyr/data_eng/services/stream_processing/",
     "src/zephyr/data/realtime_push_manager/",
     "import", "critical", "", "",
     "实时行情流→流处理引擎输入"),
    # D-DATA-ENG-09 训练数据管理器 → D-DATA-ENG-03 特征存储
    ("src/zephyr/data_eng/services/training_data_manager/",
     "src/zephyr/data/feature_store/",
     "import", "critical", "", "",
     "特征存储PIT查询→训练数据构建"),
    # D-DATA-ENG-18 合成数据生成器 → D-DATA-ENG-09 训练数据管理器
    ("src/zephyr/data_eng/services/synthetic_data/",
     "src/zephyr/data_eng/services/training_data_manager/",
     "import", "medium", "", "",
     "训练数据→合成数据增强"),
    # D-DATA-ENG-07 漂移感知调度器 → D-DATA-ENG-16 数据画像
    ("src/zephyr/data_eng/services/drift_aware_scheduler/",
     "src/zephyr/data_eng/services/data_profiling/",
     "import", "medium", "", "",
     "数据画像统计→漂移检测输入"),
    # D-DATA-ENG-12 数据湖管理器 → D-DATA-ENG-13 数据压缩归档
    ("src/zephyr/data_eng/services/data_lake_manager/",
     "src/zephyr/data_eng/services/data_compression/",
     "import", "medium", "", "",
     "冷数据→压缩归档"),
    # D-DATA-ENG-14 Schema演进管理器 → D-DATA-ENG-17 数据目录同步
    ("src/zephyr/data_eng/services/schema_evolution/",
     "src/zephyr/data_eng/services/data_catalog/",
     "import", "medium", "", "",
     "Schema变更→数据目录同步"),

    # --- 回测域：辅助模块链 ---
    # BT-23 异常诊断器 → BT-22 数据质量检查器
    ("src/zephyr/backtest/services/anomaly_diagnoser.py",
     "src/zephyr/backtest/services/data_quality_checker.py",
     "import", "medium", "", "",
     "数据质量报告→异常诊断输入"),
    # BT-24 结果对比器 → BT-20 缓存管理器
    ("src/zephyr/backtest/services/result_comparator.py",
     "src/zephyr/backtest/services/cache_manager.py",
     "import", "medium", "", "",
     "缓存回测结果→多次结果对比"),
    # BT-21 参数分析器 → BT-20 缓存管理器
    ("src/zephyr/backtest/services/param_analyzer.py",
     "src/zephyr/backtest/services/cache_manager.py",
     "import", "medium", "", "",
     "缓存参数网格结果→参数显著性分析"),
]


def _query_node_id(path: str) -> int | None:
    """查询节点的 node_id 和 design_maturity。"""
    conn = get_depgraph_pg_connection(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT node_id, design_maturity FROM nodes WHERE path = %s LIMIT 1", (path,))
        row = cur.fetchone()
        return (row[0], row[1]) if row else None
    finally:
        release_depgraph_pg_connection(conn)


def main():
    """Entry point: parse args, run logic, return exit code."""
    print("=" * 70)
    print(f"添加 {len(DESIGN_EDGES)} 条设计态依赖边 (dep_maturity='design')")
    print("=" * 70)

    added = 0
    skipped = 0
    failed = 0

    for i, (from_path, to_path, dep_type, coupling, contract, event, data_desc) in enumerate(DESIGN_EDGES, 1):
        print(f"\n  [{i}/{len(DESIGN_EDGES)}] {from_path} → {to_path}")

        # 查询双端 node_id 和 design_maturity
        from_info = _query_node_id(from_path)
        to_info = _query_node_id(to_path)

        if not from_info:
            print(f"    [SKIP] from_node 不存在: {from_path}")
            skipped += 1
            continue
        if not to_info:
            print(f"    [SKIP] to_node 不存在: {to_path}")
            skipped += 1
            continue

        from_id, from_mat = from_info
        to_id, to_mat = to_info

        if from_mat != "design":
            print(f"    [SKIP] from_node design_maturity={from_mat}（应为design）")
            skipped += 1
            continue
        if to_mat != "design":
            print(f"    [SKIP] to_node design_maturity={to_mat}（应为design）")
            skipped += 1
            continue

        print(f"    from: node_id={from_id} (design) → to: node_id={to_id} (design)")

        # 调用 add_design_edge
        edge_id = apply_depgraph.add_design_edge(
            from_node_id=from_id,
            to_node_id=to_id,
            dep_type=dep_type,
            coupling_strength=coupling,
            api_contract_refs=contract,
            event_ref=event,
            data_transfer_description=data_desc,
        )

        if edge_id > 0:
            print(f"    [OK] edge_id={edge_id}")
            added += 1
        else:
            print(f"    [FAIL] add_design_edge 返回 {edge_id}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"完成: 新增={added}  跳过={skipped}  失败={failed}")
    print("=" * 70)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
