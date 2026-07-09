#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV-SYNC-PANORAMA | docs/_working/2026-07-09-panorama_module_sync_engine.md | §Phase2
# [MODULE] scripts.governance.sync_panorama_module
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.persistence.dataflowgraph_schema (get_dataflowgraph_pg_connection); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection)
# [CONSUMERS] generate_project_depgraph.py; apply_depgraph.py; GitCommitGateway
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 单向派生（depgraph→dataflow/decision/blueprint）;占位记录用 entity_type='module_placeholder' / track='placeholder'
# [MODIFY-GUARD] sync_module_panorama/sync_all_panorama 为对外入口；SQL 常量集中在模块级 _SQL_*；占位记录策略不可改（entity_type/track 值为契约）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph无此模块→exit 3;DB异常→exit 4
# [TESTS] tests/governance/test_sync_panorama_module.py
# [TTL] permanent
# [ARCH-REF] #ARCH-056
"""sync_panorama_module.py — 四图模块同步引擎（ARCH-056）

从 depgraph.nodes 读取模块核心字段，单向派生到：
  1. dataflow_jobs（占位记录，entity_type='module_placeholder'）
  2. decision_layers（占位记录，layer_id=module_id, track='placeholder'）
  3. blueprint.md frontmatter（如蓝图存在，由 blueprint_frontmatter_reconciler 处理）

核心字段（4个）：module_id / domain_id / design_maturity / build_status

用法:
    python scripts/governance/sync_panorama_module.py MOD-XXX
    python scripts/governance/sync_panorama_module.py --all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC_DIR = _REPO_ROOT / "src"
_GOV_DIR = _REPO_ROOT / "scripts" / "governance"
for _p in (str(_REPO_ROOT), str(_SRC_DIR), str(_GOV_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.persistence.dataflowgraph_schema import get_dataflowgraph_pg_connection  # noqa: E402
from zephyr.governance.persistence.decisiongraph_schema import get_decisiongraph_pg_connection  # noqa: E402

# ---------------------------------------------------------------------------
# SQL 常量（SQL 集中化，§5.160.2）
# ---------------------------------------------------------------------------
# 注意：不使用 LIMIT 1 — 同一 blueprint_id 可有多行（跨域模块），
# _query_depgraph_module 在 Python 中用多数投票聚合，
# 与 align_panoramas._fetch_depgraph_nodes 聚合策略一致。
_SQL_QUERY_MODULE = (
    "SELECT blueprint_id, domain_id, design_maturity, build_status, path "
    "FROM nodes WHERE blueprint_id = %s AND blueprint_id <> '' "
    "ORDER BY (path IS NULL), path"
)

# design_maturity 排序：design < prototype < production（与 align_panoramas._maturity_rank 一致）
_MATURITY_RANK = {"design": 0, "prototype": 1, "production": 2}
_SQL_QUERY_ALL_MODULES = (
    "SELECT DISTINCT blueprint_id "
    "FROM nodes "
    "WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"
)
_SQL_CHECK_DATAFLOW_JOB = (
    "SELECT entity_type "
    "FROM dataflow_jobs WHERE job_name = %s"
)
_SQL_UPDATE_DATAFLOW_JOB = (
    "UPDATE dataflow_jobs "
    "SET domain_id=%s, design_maturity=%s, build_status=%s, "
    "module_id=%s WHERE job_name=%s"
)
_SQL_UPSERT_DATAFLOW_PLACEHOLDER = (
    "INSERT "
    "INTO dataflow_jobs (job_name, entity_type, module_id, domain_id, "
    "design_maturity, build_status, trigger_type) "
    "VALUES (%s, 'module_placeholder', %s, %s, %s, %s, NULL) "
    "ON CONFLICT (job_name) DO UPDATE SET "
    "entity_type='module_placeholder', module_id=EXCLUDED.module_id, "
    "domain_id=EXCLUDED.domain_id, design_maturity=EXCLUDED.design_maturity, "
    "build_status=EXCLUDED.build_status"
)
_SQL_CHECK_DECISION_LAYER = (
    "SELECT track "
    "FROM decision_layers WHERE layer_id = %s"
)
_SQL_UPDATE_DECISION_LAYER = (
    "UPDATE decision_layers "
    "SET domain_id=%s, design_maturity=%s, "
    "build_status=%s, module_id=%s WHERE layer_id=%s"
)
_SQL_UPSERT_DECISION_PLACEHOLDER = (
    "INSERT "
    "INTO decision_layers (layer_id, layer_name, layer_name_en, track, "
    "module_id, domain_id, design_maturity, build_status) "
    "VALUES (%s, %s, %s, 'placeholder', %s, %s, %s, %s) "
    "ON CONFLICT (layer_id) DO UPDATE SET "
    "module_id=EXCLUDED.module_id, domain_id=EXCLUDED.domain_id, "
    "design_maturity=EXCLUDED.design_maturity, build_status=EXCLUDED.build_status"
)


def _query_depgraph_module(conn, module_id: str) -> dict | None:
    """从 depgraph.nodes 查询单个模块的核心字段（多数投票聚合）。

    depgraph.nodes 中同一 blueprint_id 可有多行（跨域模块的正常现象）。
    聚合策略与 align_panoramas._fetch_depgraph_nodes 一致：
    - domain_id: 多数投票（Counter.most_common）
    - design_maturity: 取最 design 的状态（design < prototype < production）
    - build_status: 取第一个非空
    - path: 取第一个非空（ORDER BY 保证非空优先）
    """
    from collections import Counter

    with conn.cursor() as cur:
        cur.execute(_SQL_QUERY_MODULE, (module_id,))
        rows = cur.fetchall()
    if not rows:
        return None
    domains: list[str] = []
    maturities: list[str] = []
    build_status = ""
    path = ""
    for row in rows:
        if isinstance(row, dict):
            dom = row.get("domain_id")
            dm = row.get("design_maturity")
            bs = row.get("build_status")
            p = row.get("path")
        else:
            dom = row[1] if len(row) > 1 else None
            dm = row[2] if len(row) > 2 else None
            bs = row[3] if len(row) > 3 else None
            p = row[4] if len(row) > 4 else None
        if dom:
            domains.append(dom)
        if dm:
            maturities.append(dm)
        if not build_status and bs:
            build_status = bs
        if not path and p:
            path = p
    domain_id = Counter(domains).most_common(1)[0][0] if domains else ""
    design_maturity = (
        min(maturities, key=lambda v: _MATURITY_RANK.get(v, 99)) if maturities else ""
    )
    return {
        "module_id": module_id,
        "domain_id": domain_id,
        "design_maturity": design_maturity,
        "build_status": build_status,
        "path": path,
    }


def _sync_to_dataflow(conn, module: dict) -> int:
    """同步到 dataflow_jobs 占位记录。

    占位策略：entity_type='module_placeholder', job_name=module_id。
    如已存在非占位记录（entity_type!='module_placeholder'），更新核心字段但不改 entity_type。
    """
    mid = module["module_id"]
    with conn.cursor() as cur:
        cur.execute(_SQL_CHECK_DATAFLOW_JOB, (mid,))
        existing = cur.fetchone()
        if existing is not None:
            existing_type = existing.get("entity_type") if isinstance(existing, dict) else existing[0]
            if existing_type != "module_placeholder":
                cur.execute(
                    _SQL_UPDATE_DATAFLOW_JOB,
                    (module["domain_id"], module["design_maturity"],
                     module["build_status"], mid, mid),
                )
                return 0
        cur.execute(
            _SQL_UPSERT_DATAFLOW_PLACEHOLDER,
            (mid, mid, module["domain_id"], module["design_maturity"],
             module["build_status"]),
        )
        return 0


def _sync_to_decision(conn, module: dict) -> int:
    """同步到 decision_layers 占位记录。

    占位策略：layer_id=module_id, track='placeholder'。
    如已存在非占位 layer（track!='placeholder'），更新核心字段但不改 track。
    """
    mid = module["module_id"]
    with conn.cursor() as cur:
        cur.execute(_SQL_CHECK_DECISION_LAYER, (mid,))
        existing = cur.fetchone()
        if existing is not None:
            existing_track = existing.get("track") if isinstance(existing, dict) else existing[0]
            if existing_track != "placeholder":
                cur.execute(
                    _SQL_UPDATE_DECISION_LAYER,
                    (module["domain_id"], module["design_maturity"],
                     module["build_status"], mid, mid),
                )
                return 0
        cur.execute(
            _SQL_UPSERT_DECISION_PLACEHOLDER,
            (mid, mid, mid, mid, module["domain_id"],
             module["design_maturity"], module["build_status"]),
        )
        return 0


def sync_module_panorama(module_id: str) -> int:
    """同步单个模块的四图核心字段。

    Returns: 0=成功, 3=模块不存在, 4=DB异常
    """
    depgraph_conn = get_depgraph_pg_connection()
    try:
        module = _query_depgraph_module(depgraph_conn, module_id)
        if not module:
            print(f"[ERROR] 模块 {module_id} 在 depgraph 中不存在", file=sys.stderr)
            return 3
    finally:
        depgraph_conn.close()

    dataflow_conn = get_dataflowgraph_pg_connection(allow_design_delete=True)
    try:
        _sync_to_dataflow(dataflow_conn, module)
    finally:
        dataflow_conn.close()

    decision_conn = get_decisiongraph_pg_connection(allow_design_delete=True)
    try:
        _sync_to_decision(decision_conn, module)
    finally:
        decision_conn.close()

    # 蓝图 frontmatter 对齐（如蓝图存在）
    try:
        from d5_architecture.syncers.blueprint_frontmatter_reconciler import (
            reconcile_blueprint_frontmatter,
        )
        reconcile_blueprint_frontmatter(module_id)
    except Exception as e:
        print(f"[WARN] 蓝图 frontmatter 对齐失败（不阻断）: {e}", file=sys.stderr)

    return 0


def sync_all_panorama() -> int:
    """同步所有有 blueprint_id 的模块。"""
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_QUERY_ALL_MODULES)
            modules = [row["blueprint_id"] if isinstance(row, dict) else row[0]
                       for row in cur.fetchall()]
    finally:
        conn.close()

    failed = 0
    for mid in modules:
        rc = sync_module_panorama(mid)
        if rc != 0:
            print(f"[WARN] 同步 {mid} 失败 (rc={rc})", file=sys.stderr)
            failed += 1
    print(f"[OK] 同步完成：{len(modules)} 个模块，{failed} 个失败")
    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="四图模块同步引擎（ARCH-056）")
    parser.add_argument("module_id", nargs="?", help="要同步的模块 ID（MOD-XXX）")
    parser.add_argument("--all", action="store_true", help="同步所有模块")
    args = parser.parse_args()

    if args.all:
        return sync_all_panorama()
    if args.module_id:
        return sync_module_panorama(args.module_id)
    parser.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())
