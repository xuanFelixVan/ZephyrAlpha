# [BLUEPRINT] MOD-GOV_DATAFLOW_DIAGRAM | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §dataflowgraph
# [MODULE] scripts.governance.d5_architecture.generators.generate_dataflow_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.dataflowgraph_schema; _common (DB_DISPLAY_NAME)
# [CONSUMERS] CI自动触发;人工查看generated/dataflows/
# [STARTUP] manual
# [MATURITY] production
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
# 治本：_shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
# （原代码只加项目根，_shared 不在项目根下导致 ModuleNotFoundError）
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    get_dataflowgraph_pg_connection,
    init_dataflow_db,
)
from _shared.yaml_utils import load_vocabulary_values  # noqa: E402  词表合法值加载 SSoT（D-D-05）
from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR
# 术语翻译真源（SSoT：terminology_glossary.yaml，禁止硬编码中文字典）
from _shared.terminology_loader import get_flat_map

# maturity 合法值真源是 maturity_vocabulary.yaml，禁止代码硬编码字面量集合。
# strict=False 容错：词表缺失时返回空 set，校验逻辑回退（warn-only，不崩溃）。
_MATURITY_VALUES: set[str] = load_vocabulary_values("maturity_vocabulary.yaml", strict=False)

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture"


# 治本（2026-07-31）：在数据流图索引头部加大白话解释，让入口索引对非架构读者也友好。
# 覆盖：数据流是什么、数据流图是什么、有什么用、和依赖图啥关系、这份索引看什么。
# 风格对齐 generate_domain_index.py 的 _PLAIN_LANGUAGE_INTRO。
_DATAFLOW_PLAIN_LANGUAGE_INTRO = """\
## 这是什么？大白话讲数据流图

这份"数据流图索引"背后是一张**数据流图（dataflowgraph）**。在往下看清单之前，先用大白话讲清楚它是什么、有什么用、为什么要看。

### 一、数据流是什么意思？

一个作业把数据"吃进来、加工、吐出去"，吐出来的又被下一个作业吃掉，这条流向就叫**数据流**。
比如：`下载行情`作业把日线写进库 → `算因子`作业读这些日线算出因子 → `回测`作业读这些因子做回测。数据就这样一路流下去。

把项目里所有这种"数据从哪流到哪"的关系记下来，就是**数据流**。

### 二、数据流图是什么？

把项目里**所有数据**（叫 Dataset）和**所有作业**（叫 Job）当成点，把"谁产出谁、谁消费谁"当成连线，画成一张大网，就是数据流图。

- 它不是一张图片，是存在数据库（`depgraph`）里的一张表
- 两个基本元件：**Dataset**（数据集，被加工的数据）和 **Job**（作业，加工数据的动作）
- 连线方向：Job 产出 → Dataset → 被另一个 Job 消费 → 再产出新 Dataset……

### 三、数据流图有什么用？它和依赖图啥关系？

这个项目有三张正交的全景图，各管一摊：

| 全景图 | 管什么 | 举个例子 |
|---|---|---|
| 依赖图 depgraph | 模块**谁依赖谁**（静态） | 因子模块 import 了数据模块 |
| **数据流图 dataflowgraph** | **数据从哪流到哪**（动态） | 行情数据 → 因子 → 回测 |
| 决策流图 decisiongraph | 决策怎么产生（动态） | 信号 → 风控 → 下单 |

**为什么要看数据流图**：看数据血缘（某数据被谁产出、又被谁消费）、找断点（该产出的作业没产出）、排查"数据从哪来"（回测用的因子是哪个作业算的）。

**一句话**：依赖图管"模块关系"，数据流图管"数据流向"——一个看代码结构，一个看数据走向。

### 四、这份索引主要看什么？

1. **有多少数据流** —— 看"统计"表里的 Job / Dataset 数量
2. **数据流长啥样** —— 点进 [dataflow_production.md](dataflow_production.md) 看运营态全景图
3. **按域拆分的数据流** —— 下面表格按功能域列出每个域的数据流文档

> 运营态 = 实际在跑的数据流；设计态 = 还在图纸上没动工的数据流。

---
"""


# ============================================================
# 中文术语映射（英文 → 中文）
# ============================================================
# 真源：terminology_glossary.yaml（SSoT，经 _shared.terminology_loader 加载）。
# 新增 Dataset/Job 时，在 terminology_glossary.yaml 的对应类别补 en/zh 条目即可，
# 无需改本生成器代码。未映射的英文将原样显示（不附加中文）。
# 显式列出 dataflow 消费的类别，合并为扁平 _ZH_MAP（_zh(en) 按 key 查无 category 参数）。
# edge_type 类别含 produces/consumed by（dataflow 用）+ 6 个 decision 专用边类型
# （dataflow 不查，无害）；保留共享类别以与 decision 生成器对齐。
_DATAFLOW_CATEGORIES = [
    "entity_name",        # Dataset/Job 实体名
    "domain_id_display",  # D_XXX 图示显示名（含 D_SIGNAL 等遗留域）
    "scope",              # production / backtest_internal
    "build_status",       # design / generated
    "maturity",           # design / production（design_maturity 值）
    "pit_policy",         # strict / loose / none
    "trigger_type",      # event_driven / scheduled / manual / stream
    "edge_type",          # produces / consumed by（+ 6 个 decision 边类型，不查无害）
]
_ZH_MAP: dict[str, str] = get_flat_map(_DATAFLOW_CATEGORIES)


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


def _extract_zh_label(summary: str | None, max_len: int = 60) -> str:
    """从 format_summary/description 提取中文标签，完整保留括号说明。

    设计态 Dataset/Job 名称（如 factor.ashare_alpha87）未收录于
    terminology_glossary.yaml，``_zh`` 查无映射时回退到本函数：取完整功能
    简述，括号内说明用 ``<br/>`` 换行显示在第二行，保证节点标签信息完整
    （不再切断丢弃括号内容）。运营态节点优先用 glossary 短名（如
    "回测.模拟成交"），不走本回退。
    """
    if not summary:
        return ""
    s = summary.strip()
    # 把括号内说明换行显示，保留完整信息（不再切断丢弃括号内容）
    for sep in ("（", "("):
        if sep in s:
            head = s.split(sep, 1)[0].strip()
            rest = s[s.index(sep) + 1:]
            for close in ("）", ")"):
                if close in rest:
                    rest = rest.split(close, 1)[0].strip()
                    break
            if head and rest:
                s = f"{head}<br/>（{rest}）"
            elif head:
                s = head
            break
    if len(s) > max_len:
        s = s[:max_len] + "…"
    return s


def _fetch_dataflow_data(conn) -> tuple[list[dict], list[dict], list[dict]]:
    """从 PG 读取 datasets/jobs/edges。

    读取 Dataset 的 format_summary（功能简述，对标 decision_layers.description）
    和 Job 的 description（作业描述，功能简述），供 Mermaid label + 清单表格渲染。
    """
    with conn.cursor() as cur:
        cur.execute("""
            SELECT dataset_id, entity_name, scope, contract_ref, physical_type,
                   produced_by_job, domain_id, design_maturity, build_status, pit_policy,
                   module_id, format_summary
            FROM dataflow_datasets
            ORDER BY scope, entity_name
        """)
        datasets = [
            {
                "id": r[0], "name": r[1], "scope": r[2], "contract": r[3],
                "physical_type": r[4], "produced_by": r[5], "domain": r[6],
                "maturity": r[7], "build": r[8], "pit": r[9], "module_id": r[10],
                "format_summary": r[11],
            }
            for r in cur.fetchall()
        ]

        # ARCH-056：dataflow_jobs 含两类记录——
        #   entity_type='job'（13 个真实数据流作业，yaml 真源同步）
        #   entity_type='module_placeholder'（depgraph 模块占位投影，四图对齐用，非数据流作业）
        # 本生成器只展示真实数据流作业，占位投影由 sync_panorama_module.py 维护、不画入图。
        cur.execute("""
            SELECT job_id, job_name, scope, source_code_ref, trigger_type,
                   run_context, design_maturity, build_status, module_id, description
            FROM dataflow_jobs
            WHERE entity_type = 'job'
            ORDER BY scope, job_name
        """)
        jobs = [
            {
                "id": r[0], "name": r[1], "scope": r[2], "source": r[3],
                "trigger": r[4], "context": r[5], "maturity": r[6], "build": r[7],
                "module_id": r[8], "description": r[9],
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
    """design_maturity 标签前缀，如 [design]/[production]。未设置返回空串。"""
    if maturity in _MATURITY_VALUES:
        return f"[{maturity}]"
    return ""


def _gen_mermaid(
    datasets: list[dict], jobs: list[dict], edges: list[dict],
    scope_filter: str | None = None, maturity_filter: str | None = None,
    force_vertical: bool = False, color_by_maturity: bool = False,
    direction: str = "TD",
) -> tuple[str, int, int, int]:
    """生成 Mermaid flowchart 图表（对齐 06_decision_architecture 视觉风格）。

    视觉对齐决策流程图：%%{init}%% 配置 base 主题 + primaryColor/secondaryColor/tertiaryColor
    全设 #eaeaea 确保 subgraph 内外节点一致灰色；Dataset 矩形 / Job 圆角矩形靠节点
    语法区分形状。design/production 默认用 [标签] 前缀区分；``color_by_maturity=True``
    时额外用 classDef 着色（合并图一眼区分已造/未造）。

    :param scope_filter: None=全部, 'production'=仅生产, 'backtest_internal'=仅回测
    :param maturity_filter: None=全部, 'production'=仅运营态, 'design'=仅设计态
    :param force_vertical: 设计态域文档仅有 JOB→DS 单向 push 边，mermaid 默认横向铺开；
        为 True 时用 ~~~ 不可见链接将相邻 JOB→DS 对纵向串联，强制竖向高列布局
    :param color_by_maturity: True 时添加 classDef（design=橙虚线 / production=蓝实线），
        用于全景合并图直观区分已造/未造；默认 False 保持纯灰色主题
    :param direction: "TD"=竖向（默认，对齐决策流程图）, "LR"=横向（合并图降高度）
    :return: (mmd_text, ds_count, job_count, edge_count) —— 计数均为过滤后实数
    """
    # 灰色主题（对齐 06_decision_architecture 的 _MERMAID_INIT，默认无 classDef）
    lines = [
        "%%{init: {'theme': 'base', 'themeVariables': {"
        "'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', "
        "'primaryBorderColor': '#666666', 'lineColor': '#666666', "
        "'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
        "'fontSize': '14px'}}}%%",
        f"flowchart {direction}",
    ]

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

    # 节点中文标签优先取 format_summary/description（完整功能简述，含括号说明），
    # 未收录时回退到 terminology_glossary 短名。保证设计态/运营态显示方式一致，
    # 用户能在节点上直接看到功能简述（不只英文名）。
    for d in ds_list:
        tag = _maturity_tag(d.get("maturity"))
        zh = _extract_zh_label(d.get("format_summary")) or _zh(d["name"])
        label = f"{tag}{d['name']}" + (f"<br/>{zh}" if zh else "")
        lines.append(f'    DS{d["id"]}["{label}"]')

    for j in job_list:
        tag = _maturity_tag(j.get("maturity"))
        zh = _extract_zh_label(j.get("description")) or _zh(j["name"])
        label = f"{tag}{j['name']}" + (f"<br/>{zh}" if zh else "")
        lines.append(f'    JOB{j["id"]}("{label}")')

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

    # 强制竖向布局（设计态域文档）：仅有 JOB→DS 单向 push 边时 mermaid 默认横向铺开，
    # 用 ~~~ 不可见链接将前一个 JOB 的产出 DS 串联到下一个 JOB，形成单一纵列
    # （JOB1→DS1~~~JOB2→DS2~~~…），对齐运营态/决策流程图的竖向高列显示。
    # ~~~ 为 Mermaid 不可见链接（9.3+），不影响视觉、不计入 edge_count。
    if force_vertical and len(job_list) > 1:
        job_to_last_ds: dict[int, int] = {}
        for e in edges:
            if e["from_type"] == "job" and e["to_type"] == "dataset":
                if e["from_id"] in job_ids and e["to_id"] in ds_ids:
                    job_to_last_ds[e["from_id"]] = e["to_id"]
        for i in range(len(job_list) - 1):
            cur_job_id = job_list[i]["id"]
            next_job_id = job_list[i + 1]["id"]
            last_ds = job_to_last_ds.get(cur_job_id)
            if last_ds is not None:
                lines.append(f"    DS{last_ds} ~~~ JOB{next_job_id}")
            else:
                lines.append(f"    JOB{cur_job_id} ~~~ JOB{next_job_id}")

    # 全景合并图着色：design=橙色虚线边框（未实现）/ production=蓝色填充（已实现）
    # 仅 color_by_maturity=True 时启用，单独图保持纯灰色主题（对齐决策流程图）。
    if color_by_maturity:
        _append_maturity_classes(lines, ds_list, job_list)

    return "\n".join(lines) + "\n", len(ds_list), len(job_list), edge_count


def _append_maturity_classes(lines: list[str], ds_list: list[dict], job_list: list[dict]) -> None:
    """为合并图追加 design/production classDef + class 赋值（直观区分已造/未造）。

    design: 橙色填充 + 虚线边框（蓝图未实现）
    production: 蓝色填充 + 实线边框（已实现稳定运行）
    """
    design_nodes: list[str] = []
    prod_nodes: list[str] = []
    for d in ds_list:
        nid = f"DS{d['id']}"
        if d.get("maturity") == "design":
            design_nodes.append(nid)
        else:
            prod_nodes.append(nid)
    for j in job_list:
        nid = f"JOB{j['id']}"
        if j.get("maturity") == "design":
            design_nodes.append(nid)
        else:
            prod_nodes.append(nid)
    lines.append(
        "    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,"
        "color:#000,stroke-dasharray: 5 5"
    )
    lines.append(
        "    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000"
    )
    if design_nodes:
        lines.append(f"    class {','.join(design_nodes)} design")
    if prod_nodes:
        lines.append(f"    class {','.join(prod_nodes)} production")


def _gen_production_md(datasets: list[dict], jobs: list[dict], edges: list[dict]) -> str:
    """生成运营态全景文档 dataflow_production.md（frontmatter + 内嵌 Mermaid 图 + 统计 + 清单，英文+中文并列）。

    治本（2026-07-31）：原函数名 _gen_index_md 误导（实际生成 production.md 而非索引），
    重命名为 _gen_production_md 以显化职责，消除 AI 幻觉/漂移温床。
    单 MD 文件可看全部（图 + 清单），符合 02_domain_architecture_docs/ 风格。
    所有英文术语后附加中文翻译（通过 _ZH_MAP 映射，新增节点时需同步更新映射）。
    """
    prod_ds = sum(1 for d in datasets if d["scope"] == "production")
    bt_ds = sum(1 for d in datasets if d["scope"] == "backtest_internal")
    prod_job = sum(1 for j in jobs if j["scope"] == "production")
    bt_job = sum(1 for j in jobs if j["scope"] == "backtest_internal")

    # design_maturity 维度统计（运营态/设计态）
    prod_m_ds = sum(1 for d in datasets if d.get("maturity") == "production")
    design_ds = sum(1 for d in datasets if d.get("maturity") == "design")
    prod_m_job = sum(1 for j in jobs if j.get("maturity") == "production")
    design_job = sum(1 for j in jobs if j.get("maturity") == "design")

    now = datetime.now().isoformat(timespec="seconds")

    lines = []
    # frontmatter（G1 门禁要求：doc_type, title, version, status, date, owner, ttl）
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 数据流图（dataflowgraph）运营态全景")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split('T')[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 数据流图（dataflowgraph）运营态全景")
    lines.append("")
    lines.append(f"> 生成时间: {now}")
    lines.append(f"> 真源: `dataflow_graph_registry.yaml`（13 个真实 Job/Dataset）→ PostgreSQL `dataflow_*` 表（ARCH-051）")
    lines.append(f"> 注: `dataflow_jobs` 另含 `entity_type='module_placeholder'` 占位记录（`sync_panorama_module.py` 从 depgraph 模块派生，用于四图对齐 ARCH-056，非数据流作业，本文档不展示）")
    lines.append(f"> 数据库: {DB_DISPLAY_NAME}")
    lines.append(f"> 生成器: `scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）")
    lines.append("")
    lines.append("## 概述（自动生成 · 生成器: generate_dataflow_diagram.py）")
    lines.append("")
    lines.append("数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。")
    lines.append('- depgraph 表达"谁依赖谁"（模块依赖）')
    lines.append('- dataflowgraph 表达"数据从哪流到哪"（数据流向）')
    lines.append("- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联")
    lines.append("")
    lines.append("## 统计（自动生成 · 生成器: generate_dataflow_diagram.py）")
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
    lines.append(f"| 类型 | 运营态 (production) | 设计态 (design) | 合计 |")
    lines.append(f"|------|---------------------|-----------------|------|")
    lines.append(f"| Dataset | {prod_m_ds} | {design_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_m_job} | {design_job} | {len(jobs)} |")
    lines.append("")
    lines.append(
        "> **设计态 vs 运营态 / Design vs Production**：`design_maturity` 字段区分——"
        "`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。"
        "对标 depgraph 的设计态/运营态机制（decision_index.md）。"
    )
    lines.append("")

    # 内嵌 Mermaid 图
    lines.append("## Mermaid 图表（自动生成 · 生成器: generate_dataflow_diagram.py）")
    lines.append("")
    lines.append("> 图表内嵌在本文档中，IDE 可直接渲染显示。视觉风格对齐 06_decision_architecture（灰色主题 + TD 竖向）。")
    lines.append(">")
    lines.append("> **图例说明 / Legend**：")
    lines.append(">")
    lines.append("> - **灰色矩形** = Dataset（数据集）")
    lines.append("> - **灰色圆角矩形** = Job（作业）")
    lines.append("> - 节点标签前缀 `[design]`/`[production]` 标注 design_maturity")
    lines.append("> - `JOB -->|produces / 产出| DS` = Job 产出 Dataset")
    lines.append("> - `DS -->|consumed by / 被消费于| JOB` = Job 消费 Dataset")
    lines.append("> - 节点 label 仅含名称（2 行）；详细信息（CTR/域/蓝图/功能简述）见下方 Dataset/Job 清单表")
    lines.append("")

    # 全景图（设计态 + 运营态合并，标签标注 [design]/[production]）
    lines.append("### 全景图（设计态 + 运营态合并，标签标注 [design]/[production]）")
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
    lines.append("## Dataset 清单（自动生成 · 生成器: generate_dataflow_diagram.py）")
    lines.append("")
    lines.append("| ID | entity_name / 实体名 | scope / 范围 | contract_ref / 契约引用 | domain / 域 | pit_policy / PIT策略 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |")
    lines.append("|----|----------------------|--------------|---------------------------|------------|------------------|------------------|---------------------------|--------------------|----------|")
    for d in datasets:
        fmt = (d.get("format_summary") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| DS-{d['id']:03d} | {_en_zh(d['name'])} | {_en_zh(d['scope'])} | "
            f"{d['contract'] or '-'} | {_en_zh(d['domain'] or '-')} | {_en_zh(d['pit'])} | {d.get('module_id') or '-'} | {_en_zh(d.get('maturity') or '-')} | {_en_zh(d['build'])} | {fmt} |"
        )

    # Job 清单
    lines.append("")
    lines.append("## Job 清单（自动生成 · 生成器: generate_dataflow_diagram.py）")
    lines.append("")
    lines.append("| ID | job_name / 作业名 | scope / 范围 | source_code_ref / 源码引用 | trigger_type / 触发类型 | run_context / 运行上下文 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |")
    lines.append("|----|-------------------|--------------|------------------------------|----------------------------|------------------------------|------------------|---------------------------|--------------------|----------|")
    for j in jobs:
        jdesc = (j.get("description") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| JOB-{j['id']:03d} | {_en_zh(j['name'])} | {_en_zh(j['scope'])} | "
            f"{j['source'] or '-'} | {_en_zh(j['trigger'] or '-')} | {_en_zh(j['context'] or '-')} | {j.get('module_id') or '-'} | {_en_zh(j.get('maturity') or '-')} | {_en_zh(j['build'])} | {jdesc} |"
        )

    return "\n".join(lines) + "\n"


# ============================================================
# 域分组配置（设计态按域拆分输出）
# ============================================================
# D_FACTOR 模块多（32 个），按子目录拆 3 组；其他域按域或合并小域。
# responsibility 字段对标 06_decision_architecture 的"域职责"说明，简述该域
# 数据流职责，由 _gen_domain_md 渲染到文档头部。
_DOMAIN_GROUPS = [
    {"key": "d_factor_ashare", "title": "因子域-A股因子计算",
     "domains": {"D_FACTOR"}, "path_contains": "/ashare/",
     "responsibility": "A股Alpha因子计算——Alpha87/资金流/跨市场/基本面/机构/日内/IRL/市场结构/微观结构/形态/PS流动性/板块/SMC/技术指标等14类截面因子信号"},
    {"key": "d_factor_analysis", "title": "因子域-因子分析",
     "domains": {"D_FACTOR"}, "path_contains": "/analysis/",
     "responsibility": "因子分析与评估——IC/IR计算评估、衰减监控、相关性去重、归因、优化、分层回测、多因子合成、三级研判、换手率分析"},
    {"key": "d_factor_barra_mine", "title": "因子域-Barra风险模型与因子挖掘",
     "domains": {"D_FACTOR"}, "path_contains": ("/barra/", "/mine/"),
     "responsibility": "Barra风险模型与因子挖掘——ESG/暴露计算/风险预算/协方差风险模型 + 因果性验证/AI因子挖掘Agent"},
    {"key": "d_backtest", "title": "回测域-回测服务",
     "domains": {"D_BACKTEST"},
     "responsibility": "回测分析服务——异常诊断/数据质量检查/衰减监控/NaN处理/参数分析/报告生成/结果对比/结果部署"},
    {"key": "d_data", "title": "数据域-数据采集管理",
     "domains": {"D_DATA"},
     "responsibility": "数据采集与管理——特征存储/K线重采样/实时推送管理/板块快照采集/Tick数据管理"},
    {"key": "d_data_eng", "title": "数据工程域-数据工程服务",
     "domains": {"D_DATA_ENG"},
     "responsibility": "数据工程服务——数据湖管理/知识清洗/流处理/合成数据生成/训练数据管理"},
    {"key": "d_ex_pf_core", "title": "执行核心+组合核心域",
     "domains": {"D_EX_CORE", "D_PF_CORE"},
     "responsibility": "执行核心+组合核心——审计日志/成交处理/持仓跟踪/实盘组合 + 组合优化/汇总/策略运行/TopN动量策略"},
    {"key": "d_others", "title": "其他域-ML训练+风控+交易",
     "domains": {"D_ML_TRAIN", "D_RISK", "D_TRADING"},
     "responsibility": "ML训练+风控+交易——AI操作员决策/训练流水线 + 回撤跟踪 + PnL计算"},
]


def _job_domain_group(job: dict, datasets: list[dict], edges: list[dict]) -> str:
    """确定 Job 所属的域分组 key。通过 Job 产出 Dataset 的 domain_id 反查。"""
    job_id = job["id"]
    job_domain = None
    for e in edges:
        if e["from_type"] == "job" and e["from_id"] == job_id and e["to_type"] == "dataset":
            for d in datasets:
                if d["id"] == e["to_id"]:
                    job_domain = d.get("domain", "")
                    break
            if job_domain:
                break
    if not job_domain:
        return "d_unknown"
    src = job.get("source", "") or ""
    for grp in _DOMAIN_GROUPS:
        if job_domain in grp["domains"]:
            pc = grp.get("path_contains")
            if pc is None:
                return grp["key"]
            if isinstance(pc, str):
                if pc in src:
                    return grp["key"]
            elif isinstance(pc, tuple):
                if any(p in src for p in pc):
                    return grp["key"]
    return "d_unknown"


def _gen_domain_md(grp: dict, datasets: list[dict], jobs: list[dict], edges: list[dict]) -> str:
    """生成单个域分组的 Markdown 文档（frontmatter + 全景合并图 + 设计态/运营态分图 + 清单）。

    每个域文档包含三张数据流图：
      1. 全景合并图：设计态+运营态合并，颜色区分已造（蓝）/未造（橙虚线），LR 横向布局
      2. 设计态图：仅 design_maturity=design 的节点（蓝图规划，代码未写）
      3. 运营态图：仅 design_maturity=production 的节点（已实现稳定运行）
    当某态节点数为 0 时，对应分图区块不渲染（对标 05_d_infra_recovery.md 双图模式）。
    Dataset/Job 清单合并列出该域所有节点，用 design_maturity 列区分两态。
    """
    now = datetime.now().isoformat(timespec="seconds")
    title = grp["title"]

    lines = []
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append(f"title: {title}")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split('T')[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> 生成时间: {now}")
    lines.append(f"> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表")
    lines.append(f"> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）")
    lines.append("")

    # 域职责（对标 06_decision_architecture 的"域职责 / Responsibility"说明）
    responsibility = grp.get("responsibility", "")
    if responsibility:
        lines.append(f"> **域职责 / Responsibility**: {responsibility}")
        lines.append("")

    # 全景合并图（设计态+运营态合并，颜色区分已造/未造，LR 横向布局降低高度）
    all_mmd, a_ds, a_job, a_edge = _gen_mermaid(
        datasets, jobs, edges, scope_filter=None, maturity_filter=None,
        force_vertical=False, color_by_maturity=True, direction="LR",
    )
    if a_ds > 0 or a_job > 0:
        lines.append("## 数据流图（全景：设计态+运营态合并）")
        lines.append("")
        lines.append(f"> 节点数: {a_ds} datasets / 数据集, {a_job} jobs / 作业, {a_edge} edges / 边")
        lines.append(">")
        lines.append("> **图例**：🟦 蓝色 = 运营态（已实现）/ 🟧 橙色虚线 = 设计态（未实现）")
        lines.append("")
        lines.append("```mermaid")
        lines.append(all_mmd.rstrip())
        lines.append("```")
        lines.append("")

    # 设计态数据流图（仅 design_maturity=design，force_vertical 强制竖向高列布局）
    design_mmd, d_ds, d_job, d_edge = _gen_mermaid(
        datasets, jobs, edges, scope_filter=None, maturity_filter="design",
        force_vertical=True,
    )
    if d_ds > 0 or d_job > 0:
        lines.append("## 数据流图（设计态）")
        lines.append("")
        lines.append(f"> 节点数: {d_ds} datasets / 数据集, {d_job} jobs / 作业, {d_edge} edges / 边")
        lines.append("")
        lines.append("```mermaid")
        lines.append(design_mmd.rstrip())
        lines.append("```")
        lines.append("")

    # 运营态数据流图（仅 design_maturity=production，有交叉边用横向布局）
    op_mmd, op_ds, op_job, op_edge = _gen_mermaid(
        datasets, jobs, edges, scope_filter=None, maturity_filter="production",
        force_vertical=False,
    )
    if op_ds > 0 or op_job > 0:
        lines.append("## 数据流图（运营态）")
        lines.append("")
        lines.append(f"> 节点数: {op_ds} datasets / 数据集, {op_job} jobs / 作业, {op_edge} edges / 边")
        lines.append("")
        lines.append("```mermaid")
        lines.append(op_mmd.rstrip())
        lines.append("```")
        lines.append("")

    # Dataset 清单（设计态 + 运营态合并，design_maturity 列区分）
    lines.append("## Dataset 清单")
    lines.append("")
    lines.append("| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |")
    lines.append("|----|----------------------|--------------|------------|------------------------------|------------------|----------|")
    for d in datasets:
        fmt = (d.get("format_summary") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| DS-{d['id']:03d} | {_en_zh(d['name'])} | {_en_zh(d['scope'])} | "
            f"{_en_zh(d['domain'] or '-')} | {_en_zh(d.get('maturity') or '-')} | "
            f"{d.get('module_id') or '-'} | {fmt} |"
        )

    # Job 清单（设计态 + 运营态合并，design_maturity 列区分）
    lines.append("")
    lines.append("## Job 清单")
    lines.append("")
    lines.append("| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |")
    lines.append("|----|-------------------|----------------------------|------------------------------|------------------|----------|")
    for j in jobs:
        jdesc = (j.get("description") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| JOB-{j['id']:03d} | {_en_zh(j['name'])} | "
            f"{_en_zh(j['trigger'] or '-')} | {_en_zh(j.get('maturity') or '-')} | "
            f"{j.get('module_id') or '-'} | {jdesc} |"
        )

    lines.append("")
    lines.append(f"[← 返回索引](dataflow_index.md)")
    return "\n".join(lines) + "\n"


def _gen_overview_index(datasets: list[dict], jobs: list[dict], edges: list[dict],
                        group_counts: dict[str, dict]) -> str:
    """生成索引文件（概览 + 统计 + 链接到各域文件）。"""
    now = datetime.now().isoformat(timespec="seconds")
    prod_ds = sum(1 for d in datasets if d.get("maturity") != "design")
    design_ds = sum(1 for d in datasets if d.get("maturity") == "design")
    prod_job = sum(1 for j in jobs if j.get("maturity") != "design")
    design_job = sum(1 for j in jobs if j.get("maturity") == "design")
    prod_edge = sum(1 for e in edges if e.get("design") != "design")
    design_edge = sum(1 for e in edges if e.get("design") == "design")

    lines = []
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
    lines.append(f"> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）")
    lines.append("")

    # 大白话解释数据流图（治本 2026-07-31）：让入口索引对非架构读者也友好
    lines.extend(_DATAFLOW_PLAIN_LANGUAGE_INTRO.splitlines())
    lines.append("")

    # 统计
    lines.append("## 统计")
    lines.append("")
    lines.append("| 类型 | 运营态 (production) | 设计态 (design) | 合计 |")
    lines.append("|------|:---:|:---:|:---:|")
    lines.append(f"| Dataset | {prod_ds} | {design_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_job} | {design_job} | {len(jobs)} |")
    lines.append(f"| Edge | {prod_edge} | {design_edge} | {len(edges)} |")
    lines.append("")

    # 运营态链接
    lines.append("## 运营态数据流（全景）")
    lines.append("")
    lines.append(f"> {prod_job} 个作业 / {prod_ds} 个数据集 / {prod_edge} 条边")
    lines.append("")
    lines.append("- [dataflow_production.md](dataflow_production.md) — 运营态全景图 + Dataset/Job 清单")
    lines.append("")

    # 域文件链接（每个域文档含设计态+运营态双图，节点数为 0 的态不渲染）
    lines.append("## 数据流（按域拆分，含设计态+运营态双图）")
    lines.append("")
    lines.append(f"> {len(jobs)} 个作业 / {len(datasets)} 个数据集 / {len(edges)} 条边，按功能域拆分（每个域文档含设计态+运营态双图）：")
    lines.append("")
    lines.append("| 文件 | 功能域 | Job 数 | Dataset 数 |")
    lines.append("|------|--------|:---:|:---:|")
    for grp in _DOMAIN_GROUPS:
        gc = group_counts.get(grp["key"], {"jobs": 0, "datasets": 0})
        lines.append(
            f"| [{grp['key']}.md]({grp['key']}.md) | {grp['title']} | {gc['jobs']} | {gc['datasets']} |"
        )
    lines.append("")

    lines.append("## 概述")
    lines.append("")
    lines.append("数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。")
    lines.append('- depgraph 表达"谁依赖谁"（模块依赖）')
    lines.append('- dataflowgraph 表达"数据从哪流到哪"（数据流向）')
    lines.append("- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联")
    lines.append("")
    lines.append("> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: parse args, run logic, return exit code.

    生成多文件：
    - dataflow_index.md     — 索引+统计+链接
    - dataflow_production.md — 运营态全景图+清单
    - d_factor_ashare.md 等  — 设计态按域拆分（8 个域文件）
    """
    parser = argparse.ArgumentParser(
        description="从 dataflowgraph (PostgreSQL) 生成数据流图 Markdown 文档（内嵌 Mermaid）",
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args()

    try:
        init_dataflow_db()
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return EXIT_FINDINGS
    conn = get_dataflowgraph_pg_connection()
    try:
        datasets, jobs, edges = _fetch_dataflow_data(conn)
    finally:
        conn.close()

    if not datasets and not jobs:
        print("[WARN] dataflowgraph 表为空，请先运行 sync_yaml_to_depgraph.py")
        return EXIT_ERROR

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 为 edges 附加 design_maturity 标记（用于统计）
    ds_design = {d["id"] for d in datasets if d.get("maturity") == "design"}
    job_design = {j["id"] for j in jobs if j.get("maturity") == "design"}
    for e in edges:
        if e["from_type"] == "job" and e["from_id"] in job_design:
            e["design"] = "design"
        elif e["from_type"] == "dataset" and e["from_id"] in ds_design:
            e["design"] = "design"
        else:
            e["design"] = "production"

    # 1. 生成运营态文件
    prod_datasets = [d for d in datasets if d.get("maturity") != "design"]
    prod_jobs = [j for j in jobs if j.get("maturity") != "design"]
    prod_md = _gen_production_md(prod_datasets, prod_jobs, edges)
    (out_dir / "dataflow_production.md").write_text(prod_md, encoding="utf-8")
    print(f"[OK] 生成 dataflow_production.md（{len(prod_jobs)} jobs / {len(prod_datasets)} datasets）")

    # 2. 按域分组所有 Job + Dataset（含设计态+运营态，每个域文档双图展示）
    group_jobs: dict[str, list] = {g["key"]: [] for g in _DOMAIN_GROUPS}
    group_jobs["d_unknown"] = []
    for j in jobs:
        grp_key = _job_domain_group(j, datasets, edges)
        group_jobs.setdefault(grp_key, []).append(j)

    # 为每个域分组找对应的 datasets（通过 push edges: job→dataset）
    group_datasets: dict[str, list] = {g["key"]: [] for g in _DOMAIN_GROUPS}
    group_datasets["d_unknown"] = []
    for grp_key, grp_jobs_list in group_jobs.items():
        job_ids = {j["id"] for j in grp_jobs_list}
        produced_ds_ids = {e["to_id"] for e in edges
                           if e["from_type"] == "job" and e["from_id"] in job_ids}
        for d in datasets:
            if d["id"] in produced_ds_ids:
                group_datasets[grp_key].append(d)

    # 3. 生成各域文件（含设计态+运营态双图，节点数为 0 的态不渲染图区块）
    group_counts = {}
    for grp in _DOMAIN_GROUPS:
        key = grp["key"]
        g_jobs = group_jobs.get(key, [])
        g_ds = group_datasets.get(key, [])
        if not g_jobs:
            continue
        md = _gen_domain_md(grp, g_ds, g_jobs, edges)
        (out_dir / f"{key}.md").write_text(md, encoding="utf-8")
        print(f"[OK] 生成 {key}.md（{len(g_jobs)} jobs / {len(g_ds)} datasets）")
        group_counts[key] = {"jobs": len(g_jobs), "datasets": len(g_ds)}

    # 处理未知域
    if group_jobs.get("d_unknown"):
        g_jobs = group_jobs["d_unknown"]
        g_ds = group_datasets.get("d_unknown", [])
        unk_grp = {"key": "d_unknown", "title": "未分类域"}
        md = _gen_domain_md(unk_grp, g_ds, g_jobs, edges)
        (out_dir / "d_unknown.md").write_text(md, encoding="utf-8")
        print(f"[OK] 生成 d_unknown.md（{len(g_jobs)} jobs）")
        group_counts["d_unknown"] = {"jobs": len(g_jobs), "datasets": len(g_ds)}

    # 4. 生成索引文件
    index_md = _gen_overview_index(datasets, jobs, edges, group_counts)
    (out_dir / "dataflow_index.md").write_text(index_md, encoding="utf-8")
    print(f"[OK] 生成 dataflow_index.md（索引+统计+链接）")

    print(f"\n输出目录: {out_dir}")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
