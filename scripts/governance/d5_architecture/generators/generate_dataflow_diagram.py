# [BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §dataflowgraph
# [MODULE] scripts.governance.d5_architecture.generators.generate_dataflow_diagram
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.dataflowgraph_schema; _common (DB_DISPLAY_NAME)
# [CONSUMERS] CI自动触发;人工查看generated/dataflows/
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 输出幂等(相同输入→相同输出);只读dataflowgraph;输出到generated/dataflows/
# [MODIFY-GUARD] 修改需通过ARCH-051任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] dataflowgraph不存在→exit 1;无数据→exit 2
# [TESTS] tests/test_generate_dataflow_diagram.py
# [TTL] permanent
# [ARCH-REF] #ARCH-051
"""G-dataflow: 从 dataflowgraph (PostgreSQL) 生成数据流图(.mmd Mermaid格式 + .md 文档)

依据：ARCH-051 裁定（2026-07-06）

功能：
  - 从 dataflow_datasets / dataflow_jobs / dataflow_edges 表读取数据流图
  - 生成 Mermaid 图表（flowchart LR）
  - 区分 production / backtest_internal scope（不同颜色）
  - 输出到 docs/02_enterprise_architecture/generated/dataflows/

输出文件：
  - dataflow_overview.mmd          全景图（所有 Dataset/Job）
  - dataflow_production.mmd         生产数据流图（scope=production）
  - dataflow_backtest.mmd           回测内部数据流图（scope=backtest_internal）
  - dataflow_index.md               索引文档（含统计+图嵌入）

用法
----
    python scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py
    python scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py --scope production
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    get_dataflowgraph_pg_connection,
    init_dataflow_db,
)

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "generated" / "dataflows"


def _fetch_dataflow_data(conn) -> tuple[list[dict], list[dict], list[dict]]:
    """从 PG 读取 datasets/jobs/edges。"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT dataset_id, entity_name, scope, contract_ref, physical_type,
                   produced_by_job, domain_id, design_maturity, build_status, pit_policy
            FROM dataflow_datasets
            ORDER BY scope, entity_name
        """)
        datasets = [
            {
                "id": r[0], "name": r[1], "scope": r[2], "contract": r[3],
                "physical_type": r[4], "produced_by": r[5], "domain": r[6],
                "maturity": r[7], "build": r[8], "pit": r[9],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT job_id, job_name, scope, source_code_ref, trigger_type,
                   run_context, design_maturity, build_status
            FROM dataflow_jobs
            ORDER BY scope, job_name
        """)
        jobs = [
            {
                "id": r[0], "name": r[1], "scope": r[2], "source": r[3],
                "trigger": r[4], "context": r[5], "maturity": r[6], "build": r[7],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT from_entity_id, to_entity_id, from_entity_type, to_entity_type, edge_type
            FROM dataflow_edges
        """)
        edges = [
            {"from_id": r[0], "to_id": r[1], "from_type": r[2], "to_type": r[3], "type": r[4]}
            for r in cur.fetchall()
        ]

    return datasets, jobs, edges


def _gen_mermaid(
    datasets: list[dict], jobs: list[dict], edges: list[dict], scope_filter: str | None = None
) -> tuple[str, int, int, int]:
    """生成 Mermaid flowchart LR 图表。

    :param scope_filter: None=全部, 'production'=仅生产, 'backtest_internal'=仅回测
    :return: (mmd_text, ds_count, job_count, edge_count) —— 计数均为 scope_filter 过滤后实数
    """
    lines = ["flowchart LR"]

    # 过滤
    if scope_filter:
        ds_list = [d for d in datasets if d["scope"] == scope_filter]
        job_list = [j for j in jobs if j["scope"] == scope_filter]
    else:
        ds_list = datasets
        job_list = jobs

    ds_ids = {d["id"] for d in ds_list}
    job_ids = {j["id"] for j in job_list}

    # Dataset 节点（矩形）
    for d in ds_list:
        label = d["name"]
        if d["contract"]:
            label += f"<br/>CTR: {d['contract']}"
        if d["domain"]:
            label += f"<br/>[{d['domain']}]"
        scope_class = "dsProd" if d["scope"] == "production" else "dsBacktest"
        lines.append(f'    DS{d["id"]}["{label}"]:::{scope_class}')

    # Job 节点（圆角矩形）
    for j in job_list:
        label = j["name"]
        if j["trigger"]:
            label += f"<br/>trigger: {j['trigger']}"
        scope_class = "jobProd" if j["scope"] == "production" else "jobBacktest"
        lines.append(f'    JOB{j["id"]}("{label}"):::{scope_class}')

    # Edges
    edge_count = 0
    for e in edges:
        if e["from_type"] == "job" and e["to_type"] == "dataset":
            if e["from_id"] in job_ids and e["to_id"] in ds_ids:
                lines.append(f'    JOB{e["from_id"]} -->|produces| DS{e["to_id"]}')
                edge_count += 1
        elif e["from_type"] == "dataset" and e["to_type"] == "job":
            if e["from_id"] in ds_ids and e["to_id"] in job_ids:
                lines.append(f'    DS{e["from_id"]} -->|consumed by| JOB{e["to_id"]}')
                edge_count += 1

    # 样式定义
    lines.append("")
    lines.append("    classDef dsProd fill:#e1f5fe,stroke:#01579b,stroke-width:2px")
    lines.append("    classDef dsBacktest fill:#fff3e0,stroke:#e65100,stroke-width:2px")
    lines.append("    classDef jobProd fill:#f1f8e9,stroke:#33691e,stroke-width:2px")
    lines.append("    classDef jobBacktest fill:#fce4ec,stroke:#880e4f,stroke-width:2px")

    return "\n".join(lines) + "\n", len(ds_list), len(job_list), edge_count


def _gen_index_md(datasets: list[dict], jobs: list[dict], edges: list[dict]) -> str:
    """生成索引文档（frontmatter + 内嵌 Mermaid 图 + 统计 + 清单）。

    单 MD 文件可看全部（图 + 清单），符合 02_domain_architecture_docs/ 风格。
    .mmd 文件仍单独输出，供 Mermaid CLI/VSCode 单独预览。
    """
    prod_ds = sum(1 for d in datasets if d["scope"] == "production")
    bt_ds = sum(1 for d in datasets if d["scope"] == "backtest_internal")
    prod_job = sum(1 for j in jobs if j["scope"] == "production")
    bt_job = sum(1 for j in jobs if j["scope"] == "backtest_internal")
    now = datetime.now().isoformat(timespec="seconds")

    lines = []
    # frontmatter（G1 门禁要求：doc_type, title, version, status, date, owner, ttl）
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 数据流图（dataflowgraph）索引")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split('T')[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")

    lines.append("# 数据流图（dataflowgraph）索引")
    lines.append("")
    lines.append(f"> 生成时间: {now}")
    lines.append(f"> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表（ARCH-051）")
    lines.append(f"> 数据库: {DB_DISPLAY_NAME}")
    lines.append(f"> 生成器: `generate_dataflow_diagram.py`（Mermaid 图内嵌在本文档中，IDE 可直接渲染）")
    lines.append("")

    # 概述
    lines.append("## 概述")
    lines.append("")
    lines.append("数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。")
    lines.append('- depgraph 表达"谁依赖谁"（模块依赖）')
    lines.append('- dataflowgraph 表达"数据从哪流到哪"（数据流向）')
    lines.append("- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联")
    lines.append("")

    # 统计
    lines.append("## 统计")
    lines.append("")
    lines.append("| 类型 | 生产 (production) | 回测内部 (backtest_internal) | 合计 |")
    lines.append("|------|-------------------|------------------------------|------|")
    lines.append(f"| Dataset | {prod_ds} | {bt_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_job} | {bt_job} | {len(jobs)} |")
    lines.append(f"| Edge | - | - | {len(edges)} |")
    lines.append("")

    # 内嵌 Mermaid 图
    lines.append("## Mermaid 图表")
    lines.append("")
    lines.append("> 图表内嵌在本文档中，IDE 可直接渲染显示。")
    lines.append(">")
    lines.append("> **图例说明**：")
    lines.append("> - **dsProd**（蓝色底）/ **jobProd**（绿色底）= 生产 scope")
    lines.append("> - **dsBacktest**（橙色底）/ **jobBacktest**（粉色底）= 回测内部 scope")
    lines.append("")

    # 全景图
    lines.append("### 全景图")
    lines.append("")
    mmd_overview, _, _, _ = _gen_mermaid(datasets, jobs, edges, scope_filter=None)
    lines.append("```mermaid")
    lines.append(mmd_overview.rstrip())
    lines.append("```")
    lines.append("")

    # 生产数据流图
    lines.append("### 生产数据流图（scope=production）")
    lines.append("")
    mmd_prod, _, _, _ = _gen_mermaid(datasets, jobs, edges, scope_filter="production")
    lines.append("```mermaid")
    lines.append(mmd_prod.rstrip())
    lines.append("```")
    lines.append("")

    # 回测内部数据流图
    lines.append("### 回测内部数据流图（scope=backtest_internal）")
    lines.append("")
    mmd_bt, _, _, _ = _gen_mermaid(datasets, jobs, edges, scope_filter="backtest_internal")
    lines.append("```mermaid")
    lines.append(mmd_bt.rstrip())
    lines.append("```")
    lines.append("")

    # .mmd 文件链接（保留，供 Mermaid CLI/VSCode 单独预览）
    lines.append("> 纯 Mermaid 文件（.mmd）也可直接打开渲染：")
    lines.append("> - [dataflow_overview.mmd](dataflow_overview.mmd)")
    lines.append("> - [dataflow_production.mmd](dataflow_production.mmd)")
    lines.append("> - [dataflow_backtest.mmd](dataflow_backtest.mmd)")
    lines.append("")

    # Dataset 清单
    lines.append("## Dataset 清单")
    lines.append("")
    lines.append("| ID | entity_name | scope | contract_ref | domain | pit_policy | build_status |")
    lines.append("|----|-------------|-------|--------------|--------|------------|--------------|")
    for d in datasets:
        lines.append(
            f"| DS-{d['id']:03d} | {d['name']} | {d['scope']} | "
            f"{d['contract'] or '-'} | {d['domain'] or '-'} | {d['pit']} | {d['build']} |"
        )

    lines.append("")
    lines.append("## Job 清单")
    lines.append("")
    lines.append("| ID | job_name | scope | source_code_ref | trigger_type | run_context | build_status |")
    lines.append("|----|----------|-------|-----------------|--------------|-------------|--------------|")
    for j in jobs:
        lines.append(
            f"| JOB-{j['id']:03d} | {j['name']} | {j['scope']} | "
            f"{j['source'] or '-'} | {j['trigger'] or '-'} | {j['context'] or '-'} | {j['build']} |"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 dataflowgraph (PostgreSQL) 生成数据流图（Mermaid + Markdown）",
    )
    parser.add_argument("--scope", choices=["production", "backtest_internal"], help="仅生成指定 scope 的图表")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args()

    # 验证 dataflowgraph schema
    try:
        init_dataflow_db()
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    conn = get_dataflowgraph_pg_connection()
    try:
        datasets, jobs, edges = _fetch_dataflow_data(conn)
    finally:
        conn.close()

    if not datasets and not jobs:
        print("[WARN] dataflowgraph 表为空，请先运行 sync_yaml_to_depgraph.py 同步 dataflow_graph_registry.yaml")
        return 2

    # 创建输出目录
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 生成图表
    scopes = [args.scope] if args.scope else [None, "production", "backtest_internal"]
    filenames = {None: "dataflow_overview", "production": "dataflow_production", "backtest_internal": "dataflow_backtest"}

    for scope in scopes:
        mmd, ds_count, job_count, edge_count = _gen_mermaid(datasets, jobs, edges, scope_filter=scope)
        fname = filenames[scope] + ".mmd"
        (out_dir / fname).write_text(mmd, encoding="utf-8")
        print(f"[OK] 生成 {fname} ({ds_count} datasets, {job_count} jobs, {edge_count} edges)")

    # 生成索引文档
    if not args.scope:
        md = _gen_index_md(datasets, jobs, edges)
        (out_dir / "dataflow_index.md").write_text(md, encoding="utf-8")
        print(f"[OK] 生成 dataflow_index.md")

    print(f"\n输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
