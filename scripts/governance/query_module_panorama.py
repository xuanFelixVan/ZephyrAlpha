#!/usr/bin/env python
# [BLUEPRINT] MOD-D5-ARCH-TOOLS | docs/03_modules/d5_architecture/blueprint.md | §query_tools
# [MODULE] scripts.governance.query_module_panorama
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.persistence.dataflowgraph_schema (get_dataflowgraph_pg_connection); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection)
# [CONSUMERS] (manual CLI)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读查询（不写DB）；depgraph.nodes 文件级 GROUP BY blueprint_id 得到蓝图级模块表
# [MODIFY-GUARD] (none)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] module_id 不存在时 exit 3；DB 异常时 exit 4
# [TESTS] (none yet)
# [TTL] permanent
"""query_module_panorama.py — 模块全景查询入口（四图模块对齐 Step 5）

输入 module_id（MOD-XXX），输出该模块在三图（depgraph/dataflow/decision）的所有记录，
以及蓝图 frontmatter、文件清单、能力索引。

--all 模式输出全项目蓝图级模块表（从 depgraph.nodes GROUP BY blueprint_id）。

这是用户要的"全项目模块表"——一个查询入口，不是一张静态表。

Usage::

    # 查询单个模块
    python scripts/governance/query_module_panorama.py MOD-FACTOR_ENGINE

    # 输出全项目模块表
    python scripts/governance/query_module_panorama.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# 确保项目根在 sys.path 中
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.governance.persistence.dataflowgraph_schema import (
    get_dataflowgraph_pg_connection,
)
from zephyr.governance.persistence.decisiongraph_schema import (
    get_decisiongraph_pg_connection,
)


def _query_depgraph_nodes(module_id: str) -> list[dict]:
    """查询 depgraph.nodes 中属于该 module_id 的所有文件级节点。"""
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT path, node_type, domain_id, design_maturity, build_status,
                       entry_point, public_api, blueprint_path
                FROM nodes
                WHERE blueprint_id = %s
                ORDER BY path
                """,
                (module_id,),
            )
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def _query_depgraph_metadata(module_id: str) -> dict | None:
    """查询 nodes_metadata 中该 module_id 的模块级元数据（取第一条）。"""
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT nm.path, nm.module_name_cn, nm.module_name_en,
                       nm.description_cn, nm.description_en, nm.tags, nm.last_updated
                FROM nodes_metadata nm
                JOIN nodes n ON nm.path = n.path
                WHERE n.blueprint_id = %s
                LIMIT 1
                """,
                (module_id,),
            )
            cols = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            return dict(zip(cols, row)) if row else None
    finally:
        conn.close()


def _query_dataflow_entities(module_id: str) -> list[dict]:
    """查询 dataflow_datasets + dataflow_jobs 中属于该 module_id 的实体。"""
    conn = get_dataflowgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            # datasets
            cur.execute(
                """
                SELECT entity_name, entity_type, scope, domain_id, physical_type
                FROM dataflow_datasets
                WHERE module_id = %s
                ORDER BY entity_name
                """,
                (module_id,),
            )
            cols = [desc[0] for desc in cur.description]
            datasets = [dict(zip(cols, row)) for row in cur.fetchall()]

            # jobs
            cur.execute(
                """
                SELECT job_name, entity_type, scope, source_code_ref, trigger_type
                FROM dataflow_jobs
                WHERE module_id = %s
                ORDER BY job_name
                """,
                (module_id,),
            )
            cols = [desc[0] for desc in cur.description]
            jobs = [dict(zip(cols, row)) for row in cur.fetchall()]

            return datasets + jobs
    finally:
        conn.close()


def _query_decision_nodes(module_id: str) -> list[dict]:
    """查询 decision_nodes + decision_layers 中属于该 module_id 的节点。"""
    conn = get_decisiongraph_pg_connection()
    try:
        with conn.cursor() as cur:
            # decision_nodes
            cur.execute(
                """
                SELECT decision_name, layer_id, node_type, design_maturity, build_status
                FROM decision_nodes
                WHERE module_id = %s
                ORDER BY decision_name
                """,
                (module_id,),
            )
            cols = [desc[0] for desc in cur.description]
            nodes = [dict(zip(cols, row)) for row in cur.fetchall()]

            # decision_layers
            cur.execute(
                """
                SELECT layer_name, layer_id, design_maturity, build_status
                FROM decision_layers
                WHERE module_id = %s
                ORDER BY layer_name
                """,
                (module_id,),
            )
            cols = [desc[0] for desc in cur.description]
            layers = [dict(zip(cols, row)) for row in cur.fetchall()]

            return layers + nodes
    finally:
        conn.close()


def _query_all_modules() -> list[dict]:
    """全项目蓝图级模块表：GROUP BY blueprint_id。"""
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    blueprint_id,
                    MIN(domain_id) AS domain_id,
                    COUNT(*) AS file_count,
                    MIN(design_maturity) AS design_maturity,
                    MIN(build_status) AS build_status,
                    MIN(blueprint_path) AS blueprint_path,
                    bool_or(entry_point) AS has_entry_point
                FROM nodes
                WHERE blueprint_id IS NOT NULL
                  AND blueprint_id != ''
                  AND blueprint_id_invalid = 0
                GROUP BY blueprint_id
                ORDER BY blueprint_id
                """
            )
            cols = [desc[0] for desc in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def _print_single_module(module_id: str) -> int:
    """打印单个模块的全景信息。返回 exit code。"""
    # 1. depgraph 文件清单
    dep_nodes = _query_depgraph_nodes(module_id)
    if not dep_nodes:
        print(f"ERROR: module_id '{module_id}' 在 depgraph.nodes 中不存在", file=sys.stderr)
        return 3

    # 2. 模块级元数据
    metadata = _query_depgraph_metadata(module_id)

    # 3. dataflow 实体
    dataflow_entities = _query_dataflow_entities(module_id)

    # 4. decision 节点
    decision_nodes = _query_decision_nodes(module_id)

    # 打印
    print(f"{'=' * 60}")
    print(f"模块：{module_id}")
    if metadata:
        if metadata.get("module_name_cn"):
            print(f"中文名：{metadata['module_name_cn']}")
        if metadata.get("module_name_en"):
            print(f"英文名：{metadata['module_name_en']}")
        if metadata.get("description_cn"):
            print(f"简介(中)：{metadata['description_cn']}")
        if metadata.get("description_en"):
            print(f"简介(英)：{metadata['description_en']}")
    else:
        print("（无模块级元数据，使用 --update-module-metadata 补充）")

    first = dep_nodes[0]
    print(f"域：{first.get('domain_id', '(未设置)')}")
    print(f"蓝图路径：{first.get('blueprint_path', '(未设置)')}")
    print(f"状态：design_maturity={first.get('design_maturity', '?')}, build_status={first.get('build_status', '?')}")

    print(f"\n文件清单（{len(dep_nodes)}个）：")
    for node in dep_nodes:
        entry_marker = " [入口]" if node.get("entry_point") else ""
        public_api = node.get("public_api", "")
        api_info = f" (public_api: {public_api})" if public_api else ""
        print(f"  {entry_marker} {node['path']}{api_info}")

    print(f"\nDataflow实体（{len(dataflow_entities)}个）：")
    if dataflow_entities:
        for ent in dataflow_entities:
            etype = ent.get("entity_type", "?")
            name = ent.get("entity_name") or ent.get("job_name", "?")
            print(f"  - {etype}: {name}")
    else:
        print("  （无）")

    print(f"\nDecision节点（{len(decision_nodes)}个）：")
    if decision_nodes:
        for dn in decision_nodes:
            name = dn.get("decision_name") or dn.get("layer_name", "?")
            print(f"  - {name}")
    else:
        print("  （无）")

    print(f"{'=' * 60}")
    return 0


def _print_all_modules() -> int:
    """打印全项目蓝图级模块表。"""
    modules = _query_all_modules()
    print(f"全项目蓝图级模块表（{len(modules)}个）：")
    print(f"{'-' * 100}")
    print(f"{'blueprint_id':<30s} {'domain_id':<20s} {'files':>5s} {'design_maturity':<15s} {'build_status':<12s} {'entry':>5s}")
    print(f"{'-' * 100}")
    for m in modules:
        bp = m.get("blueprint_id", "")
        dom = m.get("domain_id", "")
        files = m.get("file_count", 0)
        dm = m.get("design_maturity", "")
        bs = m.get("build_status", "")
        entry = "Y" if m.get("has_entry_point") else ""
        print(f"{bp:<30s} {dom:<20s} {files:>5d} {dm:<15s} {bs:<12s} {entry:>5s}")
    print(f"{'-' * 100}")
    print(f"总计：{len(modules)} 个蓝图级模块")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="模块全景查询入口（四图模块对齐 Step 5）"
    )
    parser.add_argument(
        "module_id",
        nargs="?",
        help="模块ID（MOD-XXX），查询该模块在三图的所有记录",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="输出全项目蓝图级模块表（GROUP BY blueprint_id）",
    )
    args = parser.parse_args()

    if args.all:
        return _print_all_modules()

    if not args.module_id:
        parser.print_help()
        print("\nERROR: 必须指定 module_id 或 --all", file=sys.stderr)
        return 3

    return _print_single_module(args.module_id)


if __name__ == "__main__":
    sys.exit(main())
