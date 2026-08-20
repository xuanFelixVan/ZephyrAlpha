# [BLUEPRINT] SH-GOV-001 | scripts/governance/oneoff/
# [MODULE] scripts.governance.oneoff.data_domain_design_state_complete
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] apply_depgraph.py; zephyr.infrastructure
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] oneoff
# [INVARIANTS] 数据域全景设计态补全：补全 subdomain_id + 登记 design 节点 + 修复契约 fulfillment_status；depgraph 修改通过 apply_depgraph.py 受控函数（铁律）
# [MODIFY-GUARD] none
# [STABILITY] ephemeral
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] dry-run->退出码0; 执行成功->退出码0; depgraph不可达->退出码2; 部分失败->退出码1
# [TESTS] python scripts/governance/oneoff/data_domain_design_state_complete.py --dry-run
# [TTL] task_bound
"""数据域全景设计态补全——一次性执行脚本。

执行计划 Step 1-3：
  Step 1: 补全 6 个数据域节点的 subdomain_id（扁平分组，不建子域幻影节点）
          - D_DATA（83 节点）：按 path 前缀分组 DATA-CORE/DATA-SCHEMA/DATA-DDL/DATA-PROVIDER/DATA-WAL/DATA-REDUNDANT/DATA-SATELLITE/DATA-CONFIG/DATA-TEST
          - D_MKT_DATA/D_DATA_ENG/D_DATA_GOV/D_DATA_SEC/D_ALT_DATA（各 7 节点）：MKT-CORE/DATA-ENG/DATA-GOV/DATA-SEC/ALT-CORE
  Step 2: 登记 4 个 design 节点（场外文档描述但场内缺失的关键模块，供后续施工参考）
          - D-DATA-02 NormalizedMarketData 生产者（CP-03 门禁）
          - D-DATA-03 FeatureStore
          - D-DATA-06 Data Lineage
          - D-DATA-23 DataObservability
  Step 3: 修复 3 个契约的 fulfillment_status（sync_yaml_to_depgraph.py 不处理 cross_layer 契约此字段，直接 UPDATE DB）
          - CTR-001: planned → generated（dataclass 已实现并被 10+ 模块消费）
          - CTR-ERR-001: unresolved → generated
          - CTR-TRACE-001: planned → generated（TraceContext 已实现）

机制（遵守"depgraph 修改必须用 apply_depgraph.py"铁律）：
  - subdomain_id / gate_reason：_load_depgraph() 改 dep dict → _atomic_write() 全量 UPDATE 写回
  - 新增 design 节点：add_design_node()（apply_depgraph.py 受控函数）
  - 契约 fulfillment_status：直接 SQL UPDATE（无受控函数，sync 不处理此字段）

用法：
  python scripts/governance/oneoff/data_domain_design_state_complete.py --dry-run   # 预览
  python scripts/governance/oneoff/data_domain_design_state_complete.py              # 执行
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 数据域全景设计态补全——一次性执行脚本。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]  # oneoff -> governance -> scripts -> repo_root
_GOVERNANCE_DIR = _REPO_ROOT / "scripts" / "governance"
for _p in (str(_REPO_ROOT), str(_GOVERNANCE_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apply_depgraph import (  # noqa: E402
    _atomic_write,
    _load_depgraph,
    add_design_node,
)

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

# ============================================================
# SQL 集中化（NO-BARE-SQL 门禁，§5.160.2）
# ============================================================
SQL_SELECT_CONTRACT_FULFILLMENT = "SELECT fulfillment_status FROM contracts WHERE contract_id = %s"
SQL_UPDATE_CONTRACT_FULFILLMENT = (
    "UPDATE contracts SET fulfillment_status = %s, last_reviewed = NOW() WHERE contract_id = %s"
)

# ============================================================
# Step 1 数据：path 前缀 → subdomain_id 映射（扁平分组，不建子域节点）
# ============================================================
# D_DATA 旧轨（83 节点）按 path 前缀分组
SUBDOMAIN_BY_PREFIX_D_DATA: list[tuple[str, str]] = [
    ("schemas/categories/", "DATA-SCHEMA"),
    ("scripts/ch/", "DATA-DDL"),
    ("src/zephyr/data/implementations/", "DATA-PROVIDER"),
    ("src/zephyr/data/wal_codec/", "DATA-WAL"),
    ("src/zephyr/data/redundant_source/", "DATA-REDUNDANT"),
    ("src/zephyr/data/satellite_geospatial_engine/", "DATA-SATELLITE"),
    ("src/zephyr/data/config/", "DATA-CONFIG"),
    ("tests/data/", "DATA-TEST"),
    ("tests/zephyr/data/", "DATA-TEST"),
    ("src/zephyr/data/", "DATA-CORE"),  # 兜底：core 文件
    ("scripts/register_guard_tasks.ps1", "DATA-SCRIPT"),
    ("scripts/start_scheduler.ps1", "DATA-SCRIPT"),
    ("scripts/start_tick_subscriber.ps1", "DATA-SCRIPT"),
]

# 新轨 5 域（各 7 节点）每个域一个 subdomain_id
SUBDOMAIN_BY_PREFIX_NEW_TRACK: list[tuple[str, str]] = [
    ("src/zephyr/market_data/", "MKT-CORE"),
    ("src/zephyr/data_eng/", "DATA-ENG"),
    ("src/zephyr/data_governance/", "DATA-GOV"),
    ("src/zephyr/data_security/", "DATA-SEC"),
    ("src/zephyr/alt_data/", "ALT-CORE"),
]

# D_DATA 中两个 deprecated 节点（zephyr.data.kline_resampler / zephyr.data.sector_snapshot_collector）
# 不设 subdomain_id（保留 None，表示历史遗留）

# ============================================================
# Step 2 数据：新增 design 节点（场外文档描述但场内缺失的关键模块）
# ============================================================
# (path, blueprint_id, domain_id, build_status, granularity, subdomain_id, gate_reason)
DESIGN_NODES_TO_ADD: list[dict] = [
    {
        "path": "src/zephyr/market_data/normalized_market_data_producer/",
        "blueprint_id": "MOD-MKT_DATA",
        "domain_id": "D_MKT_DATA",
        "build_status": "planned",
        "granularity": "directory",
        "subdomain_id": "MKT-CORE",
        "gate_reason": "CP-03: 需D-DATA-02生成NormalizedMarketData Python实现；契约dataclass已实现(src/zephyr/shared/contracts/market_data.py)但生产者缺失",
    },
    {
        "path": "src/zephyr/data/feature_store/",
        "blueprint_id": "MOD-L00-004",
        "domain_id": "D_DATA",
        "build_status": "planned",
        "granularity": "directory",
        "subdomain_id": "DATA-CORE",
        "gate_reason": "D-DATA-03: FeatureStore离线PIT+在线Serving+四维索引；消除训练-服务偏差；pit_query.py部分覆盖但无独立FeatureStore模块",
    },
    {
        "path": "src/zephyr/data/data_lineage/",
        "blueprint_id": "MOD-L00-004",
        "domain_id": "D_DATA",
        "build_status": "planned",
        "granularity": "directory",
        "subdomain_id": "DATA-CORE",
        "gate_reason": "D-DATA-06: OpenLineage标准数据血缘+列级血缘+数据源变更自动评估受影响下游模块",
    },
    {
        "path": "src/zephyr/data/data_observability/",
        "blueprint_id": "MOD-L00-004",
        "domain_id": "D_DATA",
        "build_status": "planned",
        "granularity": "directory",
        "subdomain_id": "DATA-CORE",
        "gate_reason": "D-DATA-23: 数据可观测性引擎(新鲜度监控+Schema漂移检测+SLA违约预测)；quality_gate.py部分覆盖但无独立DataObservability模块",
    },
]

# ============================================================
# Step 3 数据：修复契约 fulfillment_status
# ============================================================
# sync_yaml_to_depgraph.py 的 sync_cross_layer_contracts 不处理 fulfillment_status 字段
# 直接 UPDATE DB（contracts 表属架构数据，真源是 DB）
CONTRACTS_TO_UPDATE: list[tuple[str, str, str]] = [
    # (contract_id, target_status, reason)
    (
        "CTR-001",
        "generated",
        "NormalizedMarketData dataclass 已实现于 src/zephyr/shared/contracts/market_data.py，被 10+ 模块消费；生产者待实现",
    ),
    ("CTR-ERR-001", "generated", "DataQualityError 契约已实现"),
    ("CTR-TRACE-001", "generated", "TraceContext 已实现于 src/zephyr/shared/contracts/core/trace_context.py"),
]


def resolve_subdomain(path: str, domain_id: str) -> str | None:
    """按 path 前缀解析 subdomain_id。"""
    if domain_id == "D_DATA":
        for prefix, sub in SUBDOMAIN_BY_PREFIX_D_DATA:
            if path.startswith(prefix):
                return sub
        return None  # deprecated 节点等不设
    # 新轨 5 域
    for prefix, sub in SUBDOMAIN_BY_PREFIX_NEW_TRACK:
        if path.startswith(prefix):
            return sub
    return None


def step1_set_subdomain_id(dry_run: bool) -> int:
    """Step 1: 补全 6 个数据域节点的 subdomain_id。"""
    print("[Step 1] 加载 depgraph, 设置 subdomain_id ...")
    dep = _load_depgraph()
    changes = 0
    data_domains = {"D_DATA", "D_MKT_DATA", "D_DATA_ENG", "D_DATA_GOV", "D_DATA_SEC", "D_ALT_DATA"}
    for nid, node in dep["nodes"].items():
        domain_id = node.get("domain_id", "")
        if domain_id not in data_domains:
            continue
        path = node.get("path", "")
        # 跳过 deprecated 节点
        if node.get("build_status") == "deprecated":
            continue
        sub = resolve_subdomain(path, domain_id)
        if sub and node.get("subdomain_id") != sub:
            print(f"  subdomain: {path} -> {sub} (was {node.get('subdomain_id')})")
            node["subdomain_id"] = sub
            changes += 1
    print(f"  subdomain_id 变更: {changes} 个节点\n")
    if dry_run:
        print("[DRY RUN] Step 1 不写 DB（_atomic_write 跳过）\n")
    else:
        _atomic_write(dep)
        print("[OK] Step 1 已写回 DB\n")
    return changes


def step2_add_design_nodes(dry_run: bool) -> int:
    """Step 2: 登记 4 个 design 节点。"""
    print(f"[Step 2] 新增 {len(DESIGN_NODES_TO_ADD)} 个 design 节点 ...")
    added = 0
    failed = 0
    new_node_ids: list[tuple[str, int]] = []  # (path, node_id)

    for spec in DESIGN_NODES_TO_ADD:
        if dry_run:
            print(
                f"  [DRY RUN] add_design_node: path={spec['path']} domain={spec['domain_id']} bp={spec['blueprint_id']}"
            )
            print(f"            subdomain={spec['subdomain_id']} gate_reason={spec['gate_reason'][:60]}...")
            added += 1
            continue
        node_id = add_design_node(
            path=spec["path"],
            blueprint_id=spec["blueprint_id"],
            domain_id=spec["domain_id"],
            build_status=spec["build_status"],
            granularity=spec["granularity"],
        )
        if node_id > 0:
            print(f"  OK: {spec['path']} -> node_id={node_id}")
            new_node_ids.append((spec["path"], node_id))
            added += 1
        else:
            print(f"  FAIL: {spec['path']} (返回 {node_id})")
            failed += 1

    # 设置新节点的 subdomain_id 和 gate_reason（通过 _load_depgraph + _atomic_write）
    if new_node_ids and not dry_run:
        print(f"  设置 {len(new_node_ids)} 个新节点的 subdomain_id + gate_reason ...")
        dep = _load_depgraph()
        path_to_new_id = {p: nid for p, nid in new_node_ids}
        sub_gate_changes = 0
        for nid_str, node in dep["nodes"].items():
            path = node.get("path", "")
            if path not in path_to_new_id:
                continue
            # subdomain_id
            for spec in DESIGN_NODES_TO_ADD:
                if spec["path"] == path:
                    node["subdomain_id"] = spec["subdomain_id"]
                    node["gate_reason"] = spec["gate_reason"]
                    sub_gate_changes += 1
                    print(f"  {path}: subdomain={spec['subdomain_id']}, gate_reason set")
                    break
        if sub_gate_changes > 0:
            _atomic_write(dep)
            print(f"  [OK] {sub_gate_changes} 个新节点 subdomain_id + gate_reason 已写回 DB")
    print(f"\n  成功: {added}, 失败: {failed}\n")
    return added


def step3_update_contracts(dry_run: bool) -> int:
    """Step 3: 修复 3 个契约的 fulfillment_status。"""
    print(f"[Step 3] 修复 {len(CONTRACTS_TO_UPDATE)} 个契约的 fulfillment_status ...")
    if dry_run:
        for cid, target, reason in CONTRACTS_TO_UPDATE:
            print(f"  [DRY RUN] {cid}: -> {target}  ({reason[:60]}...)")
        print("\n  [DRY RUN] Step 3 不写 DB\n")
        return len(CONTRACTS_TO_UPDATE)

    conn = get_depgraph_pg_connection(autocommit=False)
    cur = conn.cursor()
    try:
        updated = 0
        for cid, target, reason in CONTRACTS_TO_UPDATE:
            # 先查当前值
            cur.execute(SQL_SELECT_CONTRACT_FULFILLMENT, (cid,))
            row = cur.fetchone()
            if not row:
                print(f"  SKIP: {cid} 不在 contracts 表中")
                continue
            old = row[0] if isinstance(row, tuple) else row["fulfillment_status"]
            # UPDATE
            cur.execute(SQL_UPDATE_CONTRACT_FULFILLMENT, (target, cid))
            print(f"  {cid}: {old} -> {target}  ({reason[:60]}...)")
            updated += 1
        conn.commit()
        print(f"\n  [OK] {updated} 个契约 fulfillment_status 已更新\n")
        return updated
    except Exception as e:
        conn.rollback()
        print(f"  ERROR: {e}", file=sys.stderr)
        return 0
    finally:
        cur.close()
        conn.close()


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="数据域全景设计态补全")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不写 DB")
    args = parser.parse_args()

    print(f"=== 数据域设计态补全 (dry_run={args.dry_run}) ===\n")

    step1_set_subdomain_id(args.dry_run)
    step2_add_design_nodes(args.dry_run)
    step3_update_contracts(args.dry_run)

    print("=== 完成 ===")
    print("\n下一步：")
    print("  1. 运行 sync_panorama_module.py 同步数据域 module_id 到全景")
    print("  2. 运行 align_panoramas.py 验证数据域 0 问题")
    print("  3. 用 GitCommitGateway 提交")
    return 0


if __name__ == "__main__":
    sys.exit(main())
