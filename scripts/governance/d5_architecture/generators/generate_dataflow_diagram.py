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
"""G-dataflow: 从 dataflowgraph (PostgreSQL) 生成数据流图 Markdown 文档（内嵌 Mermaid）

依据：ARCH-051 裁定（2026-07-06）

功能：
  - 从 dataflow_datasets / dataflow_jobs / dataflow_edges 表读取数据流图
  - 生成 Mermaid 图表（flowchart LR）并内嵌到 Markdown 中
  - 区分 production / backtest_internal scope（不同颜色）
  - 输出到 docs/02_enterprise_architecture/05_dataflow_architecture/

输出文件：
  - dataflow_index.md   单 MD 文档（frontmatter + 内嵌 3 张 Mermaid 图 + 统计表 + Dataset/Job 清单）

风格对齐 02_domain_architecture_docs/（generate_domain_doc.py）：Mermaid 直接内嵌在 MD 中，
不输出独立 .mmd 文件，单文件可看全部（图 + 清单）。

用法
----
    python scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py
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

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture"


# ============================================================
# 中文术语映射（英文 → 中文）
# ============================================================
# 新增 Dataset/Job 时，在此添加对应中文翻译。
# 维护策略：dataflow_graph_registry.yaml 新增节点后，同步在此添加映射。
# 未映射的英文将原样显示（不附加中文）。
_ZH_MAP: dict[str, str] = {
    # --- Dataset entity_name → 中文 ---
    "market_data.tick": "市场数据.Tick行情",
    "market_data.ohlc_bar": "市场数据.OHLC K线",
    "factor.value_factor": "因子.价值因子",
    "factor.momentum_20d": "因子.20日动量",
    "signal.composite": "信号.合成信号",
    "risk.limits": "风险.限额",
    "order.target": "订单.目标订单",
    "fill.executed": "成交.已成交",
    "position.snapshot": "持仓.快照",
    "backtest.result": "回测.结果",
    "backtest.tick_event": "回测.Tick事件",
    "backtest.target_weights": "回测.目标权重",
    "backtest.fills": "回测.模拟成交",
    "backtest.nav_series": "回测.净值序列",
    # --- Job job_name → 中文 ---
    "ingest.ifind_kline": "采集.iFind行情",
    "aggregate.ohlc_bar": "聚合.OHLC K线",
    "compute.value_factor": "计算.价值因子",
    "compute.momentum_20d": "计算.20日动量",
    "synthesize.signal": "合成.信号",
    "check.risk_limits": "检查.风险限额",
    "generate.order": "生成.订单",
    "execute.order": "执行.订单",
    "backtest.replay_ticks": "回测.Tick重放",
    "backtest.run_event_driven": "回测.事件驱动运行",
    "backtest.match_fills": "回测.撮合成交",
    "backtest.update_portfolio": "回测.更新组合",
    "backtest.calc_metrics": "回测.计算指标",
    # --- domain_id → 中文 ---
    "D_MKT_DATA": "市场数据",
    "D_FACTOR": "因子",
    "D_SIGNAL": "信号",
    "D_SIGLEGACY": "信号(legacy)",
    "D_RISK": "风险",
    "D_ORDER": "订单",
    "D_EXECUTION": "执行",
    "D_EX_CORE": "执行核心",
    "D_PORTFOLIO": "持仓",
    "D_PF_CORE": "持仓核心",
    "D_BACKTEST": "回测",
    # --- scope ---
    "production": "生产",
    "backtest_internal": "回测内部",
    # --- build_status / design_maturity ---
    "design": "设计",
    "prototype": "原型",
    "generated": "已生成",
    # --- pit_policy ---
    "strict": "严格",
    "loose": "宽松",
    "none": "无",
    # --- trigger_type ---
    "event_driven": "事件驱动",
    "scheduled": "定时",
    "manual": "手动",
    "stream": "流式",
    # --- edge labels ---
    "produces": "产出",
    "consumed by": "被消费于",
}


def _zh(en: str | None) -> str:
    """英文 → 中文。未映射或 None 返回空串。"""
    if not en:
        return ""
    return _ZH_MAP.get(en, "")


def _en_zh(en: str | None, sep: str = " / ") -> str:
    """英文 + 中文并列（如 'production / 生产'）。无映射或 None 返回原值或 '-'。"""
    if not en:
        return "-"
    zh = _ZH_MAP.get(en, "")
    if zh:
        return f"{en}{sep}{zh}"
    return en


def _fetch_dataflow_data(conn) -> tuple[list[dict], list[dict], list[dict]]:
    """从 PG 读取 datasets/jobs/edges。"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT dataset_id, entity_name, scope, contract_ref, physical_type,
                   produced_by_job, domain_id, design_maturity, build_status, pit_policy,
                   module_id
            FROM dataflow_datasets
            ORDER BY scope, entity_name
        """)
        datasets = [
            {
                "id": r[0], "name": r[1], "scope": r[2], "contract": r[3],
                "physical_type": r[4], "produced_by": r[5], "domain": r[6],
                "maturity": r[7], "build": r[8], "pit": r[9], "module_id": r[10],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT job_id, job_name, scope, source_code_ref, trigger_type,
                   run_context, design_maturity, build_status, module_id
            FROM dataflow_jobs
            ORDER BY scope, job_name
        """)
        jobs = [
            {
                "id": r[0], "name": r[1], "scope": r[2], "source": r[3],
                "trigger": r[4], "context": r[5], "maturity": r[6], "build": r[7],
                "module_id": r[8],
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


def _maturity_tag(maturity: str | None) -> str:
    """design_maturity 标签前缀，如 [design]/[production]/[prototype]。未设置返回空串。"""
    if maturity in ("design", "production", "prototype"):
        return f"[{maturity}]"
    return ""


def _node_class(scope: str, maturity: str | None, is_job: bool) -> str:
    """根据 design_maturity（优先）和 scope 决定节点样式类。

    - design → 紫色（bsDesign）—— 标识设计态（蓝图规划，代码未写）
    - prototype → 橙色（bsProto）—— 标识原型态（验证中）
    - production 或未设置 → 按 scope 着色（运营态）
    """
    if maturity == "design":
        return "jobDesign" if is_job else "dsDesign"
    if maturity == "prototype":
        return "jobProto" if is_job else "dsProto"
    # production 或未设置：使用 scope-based 着色
    if is_job:
        return "jobProd" if scope == "production" else "jobBacktest"
    return "dsProd" if scope == "production" else "dsBacktest"


def _gen_mermaid(
    datasets: list[dict], jobs: list[dict], edges: list[dict],
    scope_filter: str | None = None, maturity_filter: str | None = None,
) -> tuple[str, int, int, int]:
    """生成 Mermaid flowchart LR 图表。

    :param scope_filter: None=全部, 'production'=仅生产, 'backtest_internal'=仅回测
    :param maturity_filter: None=全部, 'production'=仅运营态, 'design'=仅设计态, 'prototype'=仅原型态
    :return: (mmd_text, ds_count, job_count, edge_count) —— 计数均为过滤后实数
    """
    lines = ["flowchart LR"]

    # 过滤（scope + maturity 双维度）
    def _match(item: dict) -> bool:
        if scope_filter and item["scope"] != scope_filter:
            return False
        if maturity_filter and item.get("maturity") != maturity_filter:
            return False
        return True

    ds_list = [d for d in datasets if _match(d)]
    job_list = [j for j in jobs if _match(j)]

    ds_ids = {d["id"] for d in ds_list}
    job_ids = {j["id"] for j in job_list}

    # Dataset 节点（矩形）—— [maturity]标签前缀 + 英文+中文并列
    for d in ds_list:
        tag = _maturity_tag(d.get("maturity"))
        label = f"{tag}{_en_zh(d['name'], sep='<br/>')}"
        if d["contract"]:
            label += f"<br/>CTR: {d['contract']}"
        if d["domain"]:
            label += f"<br/>[{_en_zh(d['domain'])}]"
        # 议题1约束：蓝图仅 production/prototype 态显示（design 态代码未写、蓝图未建）
        mid = d.get("module_id")
        if mid and d.get("maturity") != "design":
            label += f"<br/>蓝图: {mid}"
        node_class = _node_class(d["scope"], d.get("maturity"), is_job=False)
        lines.append(f'    DS{d["id"]}["{label}"]:::{node_class}')

    # Job 节点（圆角矩形）—— [maturity]标签前缀 + 英文+中文并列
    for j in job_list:
        tag = _maturity_tag(j.get("maturity"))
        label = f"{tag}{_en_zh(j['name'], sep='<br/>')}"
        if j["trigger"]:
            label += f"<br/>trigger: {_en_zh(j['trigger'])}"
        # 议题1约束：蓝图仅 production/prototype 态显示（design 态代码未写、蓝图未建）
        mid = j.get("module_id")
        if mid and j.get("maturity") != "design":
            label += f"<br/>蓝图: {mid}"
        node_class = _node_class(j["scope"], j.get("maturity"), is_job=True)
        lines.append(f'    JOB{j["id"]}("{label}"):::{node_class}')

    # Edges —— 边标签英文+中文并列
    edge_count = 0
    for e in edges:
        if e["from_type"] == "job" and e["to_type"] == "dataset":
            if e["from_id"] in job_ids and e["to_id"] in ds_ids:
                lines.append(f'    JOB{e["from_id"]} -->|{_en_zh("produces")}| DS{e["to_id"]}')
                edge_count += 1
        elif e["from_type"] == "dataset" and e["to_type"] == "job":
            if e["from_id"] in ds_ids and e["to_id"] in job_ids:
                lines.append(f'    DS{e["from_id"]} -->|{_en_zh("consumed by")}| JOB{e["to_id"]}')
                edge_count += 1

    # 样式定义（scope-based + design_maturity-based）
    # 填色用 Material Design 100-level（对齐 decision_index.md，50-level 太浅字体看不清）
    # 显式 color 设深色字体，确保各主题下可读
    lines.append("")
    lines.append("    classDef dsProd fill:#bbdefb,stroke:#1565c0,stroke-width:2px,color:#0d47a1")
    lines.append("    classDef dsBacktest fill:#ffe0b2,stroke:#ef6c00,stroke-width:2px,color:#e65100")
    lines.append("    classDef jobProd fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20")
    lines.append("    classDef jobBacktest fill:#ffcdd2,stroke:#c62828,stroke-width:2px,color:#b71c1c")
    # 设计态=紫色（对标 decision_index.md 的 bsPlanned，但用紫色以区分 dataflow 维度）
    lines.append("    classDef dsDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c")
    lines.append("    classDef jobDesign fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px,color:#4a148c")
    # 原型态=黄色（区别于回测橙色）
    lines.append("    classDef dsProto fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#f57f17")
    lines.append("    classDef jobProto fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#f57f17")

    return "\n".join(lines) + "\n", len(ds_list), len(job_list), edge_count


def _gen_index_md(datasets: list[dict], jobs: list[dict], edges: list[dict]) -> str:
    """生成索引文档（frontmatter + 内嵌 Mermaid 图 + 统计 + 清单，英文+中文并列）。

    单 MD 文件可看全部（图 + 清单），符合 02_domain_architecture_docs/ 风格。
    所有英文术语后附加中文翻译（通过 _ZH_MAP 映射，新增节点时需同步更新映射）。
    """
    prod_ds = sum(1 for d in datasets if d["scope"] == "production")
    bt_ds = sum(1 for d in datasets if d["scope"] == "backtest_internal")
    prod_job = sum(1 for j in jobs if j["scope"] == "production")
    bt_job = sum(1 for j in jobs if j["scope"] == "backtest_internal")

    # design_maturity 维度统计（运营态/设计态/原型态）
    prod_m_ds = sum(1 for d in datasets if d.get("maturity") == "production")
    design_ds = sum(1 for d in datasets if d.get("maturity") == "design")
    proto_ds = sum(1 for d in datasets if d.get("maturity") == "prototype")
    prod_m_job = sum(1 for j in jobs if j.get("maturity") == "production")
    design_job = sum(1 for j in jobs if j.get("maturity") == "design")
    proto_job = sum(1 for j in jobs if j.get("maturity") == "prototype")

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
    lines.append("")
    lines.append("## 概述")
    lines.append("")
    lines.append("数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。")
    lines.append('- depgraph 表达"谁依赖谁"（模块依赖）')
    lines.append('- dataflowgraph 表达"数据从哪流到哪"（数据流向）')
    lines.append("- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联")
    lines.append("")
    lines.append("## 统计")
    lines.append("")
    lines.append(f"| 类型 | 生产 (production) | 回测内部 (backtest_internal) | 合计 |")
    lines.append(f"|------|-------------------|------------------------------|------|")
    lines.append(f"| Dataset | {prod_ds} | {bt_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_job} | {bt_job} | {len(jobs)} |")
    lines.append(f"| Edge | - | - | {len(edges)} |")
    lines.append("")
    # design_maturity 维度统计（对标 decision_index.md / depgraph 设计态/运营态机制）
    lines.append("### 设计态 / 运营态统计（design_maturity）")
    lines.append("")
    lines.append(f"| 类型 | 运营态 (production) | 设计态 (design) | 原型态 (prototype) | 合计 |")
    lines.append(f"|------|---------------------|-----------------|---------------------|------|")
    lines.append(f"| Dataset | {prod_m_ds} | {design_ds} | {proto_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_m_job} | {design_job} | {proto_job} | {len(jobs)} |")
    lines.append("")
    lines.append(
        "> **设计态 vs 运营态 / Design vs Production**：`design_maturity` 字段区分——"
        "`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行，"
        "`prototype`=原型验证中。对标 depgraph 的设计态/运营态机制（decision_index.md）。"
    )
    lines.append("")

    # 内嵌 Mermaid 图
    lines.append("## Mermaid 图表")
    lines.append("")
    lines.append("> 图表内嵌在本文档中，IDE 可直接渲染显示。")
    lines.append(">")
    lines.append("> **图例说明 / Legend**：")
    lines.append(">")
    lines.append("> **设计态/原型态优先着色（design_maturity）**：")
    lines.append("> - **紫色** = 设计态节点（design_maturity=design，蓝图规划，代码未写）")
    lines.append("> - **黄色** = 原型态节点（design_maturity=prototype，原型验证中）")
    lines.append(">")
    lines.append("> **运营态按 scope 着色（design_maturity=production）**：")
    lines.append("> - **蓝色矩形** = 生产 Dataset（dsProd）")
    lines.append("> - **橙色矩形** = 回测 Dataset（dsBacktest）")
    lines.append("> - **绿色圆角矩形** = 生产 Job（jobProd）")
    lines.append("> - **粉色圆角矩形** = 回测 Job（jobBacktest）")
    lines.append(">")
    lines.append("> - `JOB -->|produces / 产出| DS` = Job 产出 Dataset")
    lines.append("> - `DS -->|consumed by / 被消费于| JOB` = Job 消费 Dataset")
    lines.append("> - 节点标签前缀 `[design]`/`[production]`/`[prototype]` 标注 design_maturity")
    lines.append("")

    # 全景图（设计态 + 运营态合并，标签标注 [design]/[production]/[prototype]）
    lines.append("### 全景图（设计态 + 运营态合并，标签标注 [design]/[production]/[prototype]）")
    lines.append("")
    mmd_overview, o_ds, o_job, o_edge = _gen_mermaid(datasets, jobs, edges, scope_filter=None)
    lines.append(f"> 节点数: {o_ds} datasets / 数据集, {o_job} jobs / 作业, {o_edge} edges / 边")
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd_overview.rstrip())
    lines.append("```")
    lines.append("")

    # 运营态全景图（仅 design_maturity=production）
    lines.append("### 运营态全景图（仅 design_maturity=production）")
    lines.append("")
    mmd_op, op_ds, op_job, op_edge = _gen_mermaid(
        datasets, jobs, edges, scope_filter=None, maturity_filter="production"
    )
    lines.append(
        f"> 仅展示已实现稳定运行的节点（运营态：{op_ds} datasets / 数据集, "
        f"{op_job} jobs / 作业, {op_edge} edges / 边）。"
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd_op.rstrip())
    lines.append("```")
    lines.append("")

    # 生产数据流图
    lines.append("### 生产数据流图（scope=production）")
    lines.append("")
    mmd_prod, p_ds, p_job, p_edge = _gen_mermaid(datasets, jobs, edges, scope_filter="production")
    lines.append(f"> 节点数: {p_ds} datasets / 数据集, {p_job} jobs / 作业, {p_edge} edges / 边")
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd_prod.rstrip())
    lines.append("```")
    lines.append("")

    # 回测内部数据流图
    lines.append("### 回测内部数据流图（scope=backtest_internal）")
    lines.append("")
    mmd_bt, b_ds, b_job, b_edge = _gen_mermaid(datasets, jobs, edges, scope_filter="backtest_internal")
    lines.append(f"> 节点数: {b_ds} datasets / 数据集, {b_job} jobs / 作业, {b_edge} edges / 边")
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd_bt.rstrip())
    lines.append("```")
    lines.append("")

    # Dataset 清单
    lines.append("## Dataset 清单")
    lines.append("")
    lines.append("| ID | entity_name / 实体名 | scope / 范围 | contract_ref / 契约引用 | domain / 域 | pit_policy / PIT策略 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 |")
    lines.append("|----|----------------------|--------------|---------------------------|------------|------------------|------------------|---------------------------|--------------------|")
    for d in datasets:
        lines.append(
            f"| DS-{d['id']:03d} | {_en_zh(d['name'])} | {_en_zh(d['scope'])} | "
            f"{d['contract'] or '-'} | {_en_zh(d['domain'] or '-')} | {_en_zh(d['pit'])} | {d.get('module_id') or '-'} | {_en_zh(d.get('maturity') or '-')} | {_en_zh(d['build'])} |"
        )

    # Job 清单
    lines.append("")
    lines.append("## Job 清单")
    lines.append("")
    lines.append("| ID | job_name / 作业名 | scope / 范围 | source_code_ref / 源码引用 | trigger_type / 触发类型 | run_context / 运行上下文 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 |")
    lines.append("|----|-------------------|--------------|------------------------------|----------------------------|------------------------------|------------------|---------------------------|--------------------|")
    for j in jobs:
        lines.append(
            f"| JOB-{j['id']:03d} | {_en_zh(j['name'])} | {_en_zh(j['scope'])} | "
            f"{j['source'] or '-'} | {_en_zh(j['trigger'] or '-')} | {_en_zh(j['context'] or '-')} | {j.get('module_id') or '-'} | {_en_zh(j.get('maturity') or '-')} | {_en_zh(j['build'])} |"
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 dataflowgraph (PostgreSQL) 生成数据流图 Markdown 文档（内嵌 Mermaid）",
    )
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

    # 生成单 MD 文档（内嵌 4 张 Mermaid 图 + 统计 + 清单），不再输出独立 .mmd 文件
    md = _gen_index_md(datasets, jobs, edges)
    (out_dir / "dataflow_index.md").write_text(md, encoding="utf-8")
    print(f"[OK] 生成 dataflow_index.md（内嵌 4 张 Mermaid 图 + 统计 + Dataset/Job 清单）")

    print(f"\n输出目录: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
