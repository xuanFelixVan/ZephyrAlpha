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
# [A_module] module_id=MOD-GOV_DATAFLOW_DIAGRAM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

__manifest__ = """
args: []
description: 'G-dataflow: 从 dataflowgraph (PostgreSQL) 生成数据流图 Markdown 文档（内嵌 Mermaid）'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


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
# 治本（2026-08-01 模板 V1.2 升级）：脚本自身目录加入 sys.path，使 `from zoomable_html import`
# 在 importlib 加载（tests/test_generate_dataflow_diagram.py）下也能解析——
# 仅作为 script 运行时 sys.path[0] 自动是脚本目录，但 importlib 不会加。
_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

try:
    from _common import DB_DISPLAY_NAME, idempotent_timestamp  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

from _shared.constants import DOC_HTTP_BASE, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS

# 术语翻译真源（SSoT：terminology_glossary.yaml，禁止硬编码中文字典）
from _shared.terminology_loader import get_flat_map
from _shared.yaml_utils import load_vocabulary_values  # noqa: E402  词表合法值加载 SSoT（D-D-05）

# 域中文名真源（#ARCH-SSOT-GLOSSARY-MERGE-001）：functional_domain_registry.yaml 经 domain_name_mapping 加载
from domain_name_mapping import (  # noqa: E402
    get_domain_desc_zh,
    get_domain_name_en,
    get_domain_name_zh,
    get_domain_name_zh_strict,
)

# 可缩放 HTML 联动生成（模板 V1.2 §9.1 #1：MD+HTML 双产物，md 刷新即 HTML 刷新）
from zoomable_html import HTML_SUBDIR, emit_zoomable_html  # noqa: E402

from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    get_dataflowgraph_pg_connection,
    init_dataflow_db,
)

# maturity 合法值真源是 maturity_vocabulary.yaml，禁止代码硬编码字面量集合。
# strict=False 容错：词表缺失时返回空 set，校验逻辑回退（warn-only，不崩溃）。
_MATURITY_VALUES: set[str] = load_vocabulary_values("maturity_vocabulary.yaml", strict=False)

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "05_dataflow_architecture"


# ============================================================
# 模板 V1.2 对齐：Mermaid 主题/样式/折行/转义/拓扑分层/HTML 链接
# （真源：visualization_view_template.md V1.2；函数复制自 generate_domain_doc.py）
# ============================================================

# 本地 HTTP 文档服务器基址（模板 §14：HTML 跳转链接必须 http:// 绝对路径）
# 启动：python -m http.server 8765 --bind 127.0.0.1 （仓库根目录执行）
# 真源：_shared.constants.DOC_HTTP_BASE（MOD-INF-005 SSoT），不再此处硬编码。
_DOC_HTTP_BASE = DOC_HTTP_BASE
# HTML 集中子文件夹相对于仓库根的 posix 路径（用于拼 http 链接）
_HTML_REL_POSIX = (OUTPUT_DIR.relative_to(_REPO_ROOT) / HTML_SUBDIR).as_posix()

# Mermaid 灰色主题头（模板 §4.1，含 clusterBkg transparent §13 前向兼容）
_MERMAID_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {"
    "'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', "
    "'primaryBorderColor': '#666666', 'lineColor': '#666666', "
    "'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'clusterBkg': 'transparent', 'clusterBorder': 'transparent', "
    "'fontSize': '14px'}}}%%"
)

# 4 类 classDef（模板 §4.7：production/design/external_prod/external_design）
_CLASSDEF_PRODUCTION = "classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000"
_CLASSDEF_DESIGN = "classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5"
_CLASSDEF_EXTERNAL_PROD = "classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000"
_CLASSDEF_EXTERNAL_DESIGN = (
    "classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5"
)

# 成熟度中英文双显（模板 §7.3：design_maturity 值 → 全称）
_MATURITY_DISPLAY = {
    "production": "生产态 / production",
    "design": "设计态 / design",
    "unknown": "未知 / unknown",
    "": "未知 / unknown",
}


def _maturity_display(maturity: str | None) -> str:
    """成熟度值转中英文全称（如 'production' → '生产态 / production'）。"""
    return _MATURITY_DISPLAY.get(maturity or "", f"{maturity} / {maturity}")


def _wrap_label_text(text: str, max_units: int = 48) -> str:
    """将长节点标签文本按显示宽度预折行（Mermaid 节点内显示用）。

    治本（模板 §4.10 铁律）：Mermaid 先按标签行数测量节点框宽高，若依赖 HTML 渲染层
    CSS max-width 二次折行，渲染行数 > 测量行数 → 框高不够、文字被上下裁剪。
    必须在生成端用 <br/> 显式预折行，使测量行数 = 渲染行数。
    原样复制自 generate_domain_doc.py:282（模板 §4.10 指示原样复制，不跨模块 import）。
    """
    if not text:
        return ""
    lines: list[str] = []
    remaining = text.strip()
    while remaining:
        width = 0
        cut = 0
        soft = -1
        for i, ch in enumerate(remaining):
            u = 2 if ord(ch) > 0x2E7F else 1
            if width + u > max_units:
                break
            width += u
            cut = i + 1
            if ch in " _":
                soft = i + 1
            elif ch in "（(/":
                soft = i if i > 0 else -1
        if cut >= len(remaining):
            lines.append(remaining)
            break
        if soft >= 8:
            cut = soft
        line = remaining[:cut].rstrip()
        if line:
            lines.append(line)
        remaining = remaining[cut:].lstrip(" ")
    return "<br/>".join(lines)


def _sanitize_mermaid_label(text: str) -> str:
    r"""清理 Mermaid 标签特殊字符（模板 §4.9：[\]"｜）。原样复制自 generate_domain_doc.py:763。"""
    if not text:
        return ""
    return text.replace("[", "(").replace("]", ")").replace('"', "'").replace("|", "/")


def _html_link_for(md_stem: str) -> str:
    """生成 _zoomable_html/{md_stem}.html 的 http 绝对跳转链接（模板 §14）。

    md_stem 为不含扩展名的 md 文件名（如 'd_factor_ashare'）。
    """
    return f"{_DOC_HTTP_BASE}/{_HTML_REL_POSIX}/{md_stem}.html"


def _short_path(source_ref: str) -> str:
    """源码引用路径取最后两段（父目录/文件名），如 src/zephyr/data/ingest.py → data/ingest.py。"""
    if not source_ref:
        return "-"
    parts = source_ref.rsplit("/", 2)
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return parts[-1]


def _split_summary(summary: str | None) -> tuple[str, str]:
    """拆分 format_summary/description 为 (head, detail)。

    head = 第一个全/半角括号前的文本（中文短名/功能名）；
    detail = 括号内说明（去掉括号）。无括号时 head=全文、detail=''。
    用于节点四要素：head 进"双语名称"行，detail 进"大白话"行（避免重复）。
    """
    if not summary:
        return ("", "")
    s = summary.strip()
    for sep in ("（", "("):
        if sep in s:
            head = s.split(sep, 1)[0].strip()
            rest = s[s.index(sep) + 1 :]
            for close in ("）", ")"):
                if close in rest:
                    rest = rest.split(close, 1)[0].strip()
                    break
            return (head, rest)
    return (s, "")


def _ds_node_label(d: dict) -> str:
    """Dataset 节点四要素标签：成熟度全称 + 双语名称 + 大白话 + 契约/域。

    模板 §4.3 四要素适配 dataflow Dataset：①成熟度 ②entity_name/中文短名 ③大白话(字段说明)
    ④契约引用·域。dataflow 表无 gate_reason，故无 ⛔ 行（模板 §7.4：gate_reason 真源在
    depgraph nodes 表，dataflow N/A）。每行过 _wrap_label_text 预折行（§4.10）。
    """
    maturity = _maturity_display(d.get("maturity"))
    name = d.get("name", "")
    summary = d.get("format_summary") or ""
    head, detail = _split_summary(summary)
    zh_short = _zh(name) or head or name  # 中文短名：glossary 优先，回退 summary head
    # 大白话：若 zh_short 来自 head，则大白话用 detail（避免重复）；否则用完整 summary
    if zh_short == head and detail:
        plain = f"（{detail}）"
    elif zh_short == head and not detail:
        plain = ""  # summary 无括号且 head 已用作名称，无额外大白话
    else:
        plain = summary
    parts = [f"({maturity}) {name} / {zh_short}"]
    if plain:
        parts.append(plain)
    contract = d.get("contract") or "-"
    domain_zh = get_domain_name_zh_strict(d.get("domain") or "") or d.get("domain") or "-"
    parts.append(f"契约: {contract} · 域: {domain_zh}")
    return _sanitize_mermaid_label("<br/>".join(_wrap_label_text(p) for p in parts))


def _job_node_label(j: dict) -> str:
    """Job 节点四要素标签：成熟度全称 + 双语名称 + 大白话 + 文件路径。

    模板 §4.3 四要素适配 dataflow Job：①成熟度 ②job_name/中文短名 ③大白话(作业描述)
    ④文件: source_code_ref 父目录/文件名。每行过 _wrap_label_text 预折行（§4.10）。
    """
    maturity = _maturity_display(j.get("maturity"))
    name = j.get("name", "")
    desc = j.get("description") or ""
    head, detail = _split_summary(desc)
    zh_short = _zh(name) or head or name
    if zh_short == head and detail:
        plain = f"（{detail}）"
    elif zh_short == head and not detail:
        plain = ""
    else:
        plain = desc
    parts = [f"({maturity}) {name} / {zh_short}"]
    if plain:
        parts.append(plain)
    parts.append(f"文件: {_short_path(j.get('source') or '')}")
    return _sanitize_mermaid_label("<br/>".join(_wrap_label_text(p) for p in parts))


def _ext_domain_node_label(ext_domain: str, maturity: str) -> str:
    """跨域外部节点标签：成熟度 + 域中英文名 + 域功能简介 + 跨域标识（模板 §4.3 跨域节点）。"""
    maturity_full = _maturity_display(maturity or "unknown")
    name_zh = get_domain_name_zh_strict(ext_domain) or ext_domain
    name_en = get_domain_name_en(ext_domain) or ext_domain
    desc = get_domain_desc_zh(ext_domain) or ""
    if name_en and name_en != ext_domain:
        name_bi = f"{name_zh} / {name_en}"
    else:
        name_bi = f"{ext_domain} {name_zh}" if name_zh != ext_domain else ext_domain
    parts = [f"({maturity_full}) {name_bi}"]
    if desc:
        parts.append(desc)
    parts.append("跨域节点 / cross-domain")
    return _sanitize_mermaid_label("<br/>".join(_wrap_label_text(p) for p in parts))


def _compute_dataflow_topo_layers(ds_list: list[dict], job_list: list[dict], edges: list[dict]) -> dict[str, int]:
    """计算 DS/JOB 节点拓扑层级（Kahn 算法，模板 §4.6 强制竖排分层）。

    返回 {node_id_str: layer}，node_id_str = 'DS{id}' / 'JOB{id}'。
    layer 0 = 入度为 0 的节点；layer(node)=max(layer(前驱))+1；环内节点归 max+1 层。
    仅考虑两端都在当前 ds_list/job_list 内的边。
    """
    node_ids: set[str] = set()
    for d in ds_list:
        node_ids.add(f"DS{d['id']}")
    for j in job_list:
        node_ids.add(f"JOB{j['id']}")

    out_edges: dict[str, list[str]] = {nid: [] for nid in node_ids}
    in_degree: dict[str, int] = {nid: 0 for nid in node_ids}
    for e in edges:
        f, t = "", ""
        if e["from_type"] == "job" and e["to_type"] == "dataset":
            f, t = f"JOB{e['from_id']}", f"DS{e['to_id']}"
        elif e["from_type"] == "dataset" and e["to_type"] == "job":
            f, t = f"DS{e['from_id']}", f"JOB{e['to_id']}"
        if f in node_ids and t in node_ids:
            out_edges[f].append(t)
            in_degree[t] += 1

    layer: dict[str, int] = {}
    queue = [nid for nid in node_ids if in_degree[nid] == 0]
    for nid in queue:
        layer[nid] = 0
    while queue:
        cur = queue.pop(0)
        for nxt in out_edges[cur]:
            in_degree[nxt] -= 1
            layer[nxt] = max(layer.get(nxt, 0), layer[cur] + 1)
            if in_degree[nxt] == 0:
                queue.append(nxt)

    remaining = [nid for nid in node_ids if nid not in layer]
    if remaining:
        max_layer = max(layer.values()) if layer else 0
        for nid in remaining:
            layer[nid] = max_layer + 1
    return layer


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
2. **数据流长啥样** —— 点进 [dataflow_panorama.md](dataflow_panorama.md) 看全项目数据流全景图（运营态+设计态）
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
    "entity_name",  # Dataset/Job 实体名
    "scope",  # production / backtest_internal
    "build_status",  # design / generated
    "maturity",  # design / production（design_maturity 值）
    "pit_policy",  # strict / loose / none
    "trigger_type",  # event_driven / scheduled / manual / stream
    "edge_type",  # produces / consumed by（+ 6 个 decision 边类型，不查无害）
]
_ZH_MAP: dict[str, str] = get_flat_map(_DATAFLOW_CATEGORIES)


def _domain_en_zh(en: str | None, sep: str = " / ") -> str:
    """域ID → 英文+中文并列（D_XXX → D_XXX 中文名）。

    真源：functional_domain_registry.yaml（经 domain_name_mapping 加载）。
    替代原 glossary domain_id_display 类别（#ARCH-SSOT-GLOSSARY-MERGE-001）。
    找不到中文时返回原 domain_id（不重复显示）。
    """
    if not en or en == "-":
        return "-"
    zh = get_domain_name_zh_strict(en)
    if zh and zh != en:
        return f"{en}{sep}{zh}"
    return en


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
            rest = s[s.index(sep) + 1 :]
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
                "id": r[0],
                "name": r[1],
                "scope": r[2],
                "contract": r[3],
                "physical_type": r[4],
                "produced_by": r[5],
                "domain": r[6],
                "maturity": r[7],
                "build": r[8],
                "pit": r[9],
                "module_id": r[10],
                "format_summary": r[11],
            }
            for r in cur.fetchall()
        ]

        # ARCH-056：dataflow_jobs 含两类记录——
        #   entity_type='job'（13 个真实数据流作业，yaml 真源同步）
        #   entity_type='module_placeholder'（depgraph 模块占位投影，五图对齐用，非数据流作业）
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
                "id": r[0],
                "name": r[1],
                "scope": r[2],
                "source": r[3],
                "trigger": r[4],
                "context": r[5],
                "maturity": r[6],
                "build": r[7],
                "module_id": r[8],
                "description": r[9],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT from_entity_id, to_entity_id, from_entity_type, to_entity_type, edge_type
            FROM dataflow_edges
        """)
        edges = [
            {"from_id": r[0], "to_id": r[1], "from_type": r[2], "to_type": r[3], "type": r[4]} for r in cur.fetchall()
        ]

    return datasets, jobs, edges


def _edge_arrow(from_maturity: str | None, to_maturity: str | None) -> str:
    """边箭头类型（模板 §4.5）：两端均 production → 实线 ``-->``，其余 → 虚线 ``-.->``。"""
    if from_maturity == "production" and to_maturity == "production":
        return "-->"
    return "-.->"


def _ext_ds_node_label(d: dict) -> str:
    """跨域外部 Dataset 节点标签：四要素 + 跨域标识（模板 §4.3 跨域节点适配 dataflow）。

    在 _ds_node_label 四要素基础上追加「跨域节点 / cross-domain」行，用 external_* 类着色。
    """
    base = _ds_node_label(d)
    cross = _sanitize_mermaid_label(_wrap_label_text("跨域节点 / cross-domain"))
    return f"{base}<br/>{cross}"


def _collect_external_datasets(
    domain_jobs: list[dict],
    domain_datasets: list[dict],
    all_datasets: list[dict],
    edges: list[dict],
) -> list[dict]:
    """找出被本域 Job 消费但不属于本域的 Dataset（全景图跨域外部节点）。

    模板 §3.2 全景图含跨域外部节点；运营态/设计态分图不含。本函数扫描 consumed_by
    边（dataset→job），若 job 在本域、dataset 不在本域 → 该 dataset 为跨域外部节点。
    去重保序返回。
    """
    job_ids = {j["id"] for j in domain_jobs}
    local_ds_ids = {d["id"] for d in domain_datasets}
    ext_ds_ids: list[int] = []
    seen: set[int] = set()
    for e in edges:
        if e["from_type"] == "dataset" and e["to_type"] == "job" and e["to_id"] in job_ids:
            if e["from_id"] not in local_ds_ids and e["from_id"] not in seen:
                ext_ds_ids.append(e["from_id"])
                seen.add(e["from_id"])
    ext_map = {d["id"]: d for d in all_datasets}
    return [ext_map[i] for i in ext_ds_ids if i in ext_map]


def _gen_mermaid(
    datasets: list[dict],
    jobs: list[dict],
    edges: list[dict],
    scope_filter: str | None = None,
    maturity_filter: str | None = None,
    external_ds: list[dict] | None = None,
) -> tuple[str, int, int, int]:
    """生成 Mermaid flowchart（模板 V1.2 全面对齐）。

    模板 V1.2 强制项：①灰色主题头（含 clusterBkg transparent）②flowchart TD 竖排
    ③节点四要素标签（成熟度全称+双语名称+大白话+契约/文件路径）④标签预折行 _wrap_label_text
    ⑤4-class classDef（production/design/external_prod/external_design）始终启用
    ⑥拓扑分层 Kahn + 同层 ~~~ 串联强制竖排 ⑦实虚线箭头（production 间实线，其余虚线）
    ⑧跨域外部节点（external_ds，仅全景图传入，渲染为 external_* 类）。

    :param scope_filter: None=全部, 'production'=仅生产, 'backtest_internal'=仅回测
    :param maturity_filter: None=全部, 'production'=仅运营态, 'design'=仅设计态
    :param external_ds: 跨域外部 Dataset 列表（全景图用，渲染为 external_prod/external_design）
    :return: (mmd_text, ds_count, job_count, edge_count) —— 计数为域内过滤后实数（不含外部节点）
    """
    lines = [_MERMAID_THEME, "flowchart TD"]

    # 过滤（scope + maturity 双维度）
    def _match(item: dict) -> bool:
        """_match implementation."""
        if scope_filter and item["scope"] != scope_filter:
            return False
        if maturity_filter and item.get("maturity") != maturity_filter:
            return False
        return True

    ds_list = [d for d in datasets if _match(d)]
    job_list = [j for j in jobs if _match(j)]

    ds_ids = {d["id"] for d in ds_list}
    job_ids = {j["id"] for j in job_list}

    # maturity 查找表（边箭头判定用）
    ds_mat = {d["id"]: d.get("maturity") for d in ds_list}
    job_mat = {j["id"]: j.get("maturity") for j in job_list}

    # 节点定义（四要素标签 + 预折行，模板 §4.3/§4.10）
    # Dataset 矩形 [""] / Job 圆角 ("") 靠节点语法区分形状（dataflow 语义增强）
    for d in ds_list:
        lines.append(f'    DS{d["id"]}["{_ds_node_label(d)}"]')
    for j in job_list:
        lines.append(f'    JOB{j["id"]}("{_job_node_label(j)}")')

    # 跨域外部节点（模板 §4.3 跨域节点，仅全景图传 external_ds 时渲染）
    ext_ds_ids: set[int] = set()
    if external_ds:
        for d in external_ds:
            ext_ds_ids.add(d["id"])
            lines.append(f'    DS{d["id"]}["{_ext_ds_node_label(d)}"]')

    # 边（实线/虚线 + 中英标签，模板 §4.5）
    edge_count = 0
    for e in edges:
        if e["from_type"] == "job" and e["to_type"] == "dataset":
            # job produces dataset
            if e["from_id"] in job_ids and e["to_id"] in ds_ids:
                arrow = _edge_arrow(job_mat.get(e["from_id"]), ds_mat.get(e["to_id"]))
                lines.append(f"    JOB{e['from_id']} {arrow}|{_en_zh('produces')}| DS{e['to_id']}")
                edge_count += 1
        elif e["from_type"] == "dataset" and e["to_type"] == "job":
            # dataset consumed by job
            if e["from_id"] in ds_ids and e["to_id"] in job_ids:
                arrow = _edge_arrow(ds_mat.get(e["from_id"]), job_mat.get(e["to_id"]))
                lines.append(f"    DS{e['from_id']} {arrow}|{_en_zh('consumed by')}| JOB{e['to_id']}")
                edge_count += 1
            elif e["from_id"] in ext_ds_ids and e["to_id"] in job_ids:
                # 跨域外部 Dataset → 本域 Job（全景图跨域边，虚线）
                lines.append(f"    DS{e['from_id']} -.->|{_en_zh('consumed by')}| JOB{e['to_id']}")

    # 拓扑分层（Kahn，模板 §4.6 强制竖排）：同层节点用 ~~~ 串联强制同 rank
    layers = _compute_dataflow_topo_layers(ds_list, job_list, edges)
    layer_nodes: dict[int, list[str]] = {}
    for nid, lyr in layers.items():
        layer_nodes.setdefault(lyr, []).append(nid)
    for lyr in sorted(layer_nodes):
        nodes = layer_nodes[lyr]
        for i in range(len(nodes) - 1):
            lines.append(f"    {nodes[i]} ~~~ {nodes[i + 1]}")

    # 4-class classDef（模板 §4.7，始终启用）
    lines.append(f"    {_CLASSDEF_PRODUCTION}")
    lines.append(f"    {_CLASSDEF_DESIGN}")
    lines.append(f"    {_CLASSDEF_EXTERNAL_PROD}")
    lines.append(f"    {_CLASSDEF_EXTERNAL_DESIGN}")

    # class 赋值（按 maturity 分组，模板 §4.8）
    prod_nodes: list[str] = []
    design_nodes: list[str] = []
    for d in ds_list:
        (design_nodes if d.get("maturity") == "design" else prod_nodes).append(f"DS{d['id']}")
    for j in job_list:
        (design_nodes if j.get("maturity") == "design" else prod_nodes).append(f"JOB{j['id']}")
    ext_prod: list[str] = []
    ext_design: list[str] = []
    for d in external_ds or []:
        (ext_design if d.get("maturity") == "design" else ext_prod).append(f"DS{d['id']}")

    if prod_nodes:
        lines.append(f"    class {','.join(prod_nodes)} production")
    if design_nodes:
        lines.append(f"    class {','.join(design_nodes)} design")
    if ext_prod:
        lines.append(f"    class {','.join(ext_prod)} external_prod")
    if ext_design:
        lines.append(f"    class {','.join(ext_design)} external_design")

    return "\n".join(lines) + "\n", len(ds_list), len(job_list), edge_count


_LEGEND_BLOCK = """\
> **图例说明 / Legend**：
>
> - 🟦 **蓝色 = 运营态节点**（production，已上线运行）
> - 🟧 **橙色虚线 = 设计态节点**（design，蓝图阶段，代码未写）
> - 🟦更浅蓝 = 跨域外部 Dataset（external_prod/external_design）
> - **实线箭头 ``-->`` = 运营态数据流**（两端均 production）
> - **虚线箭头 ``-.->`` = 非运营态数据流**（含 design、混合）
> - 矩形 = Dataset（数据集）/ 圆角矩形 = Job（作业）
> - ``JOB -->|produces / 产出| DS`` = Job 产出 Dataset
> - ``DS -->|consumed by / 被消费于| JOB`` = Job 消费 Dataset
"""


def _gen_panorama_md(datasets: list[dict], jobs: list[dict], edges: list[dict]) -> str:
    """生成全项目数据流全景文档 dataflow_panorama.md（运营态 + 设计态，模板 V1.2 三视图 + HTML 链接 + 图例 + 清单）。

    治本（2026-08-01）：原 dataflow_production.md 仅含运营态节点，用户要求"一张看完所有东西"，
    故改为全项目全景（运营态 + 设计态），文件名同步改为 dataflow_panorama.md。
    三视图结构天然适配：全景图展示全部（production+design），运营态/设计态分图各聚焦一态。
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

    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源（脚本最近 git commit 时间）
    now = idempotent_timestamp(Path(__file__))
    html_link = _html_link_for("dataflow_panorama")

    lines = []
    # frontmatter（G1 门禁要求：doc_type, title, version, status, date, owner, ttl）
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append("title: 数据流图（dataflowgraph）全景（运营态 + 设计态）")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split('T')[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    lines.append("# 数据流图（dataflowgraph）全景（运营态 + 设计态）")
    lines.append("")
    lines.append(f"> 生成时间: {now}")
    lines.append(
        "> 真源: `dataflow_graph_registry.yaml`（13 个真实 Job/Dataset）→ PostgreSQL `dataflow_*` 表（ARCH-051）"
    )
    lines.append(
        "> 注: `dataflow_jobs` 另含 `entity_type='module_placeholder'` 占位记录（`sync_panorama_module.py` 从 depgraph 模块派生，用于五图对齐 ARCH-056，非数据流作业，本文档不展示）"
    )
    lines.append(f"> 数据库: {DB_DISPLAY_NAME}")
    lines.append(
        "> 生成器: `scripts/governance/d5_architecture/generators/generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）"
    )
    lines.append("")
    # HTML 跳转链接（模板 §14：http:// 绝对路径，IDE 预览面板可点开浏览器渲染）
    lines.append(
        f"> **[可缩放 HTML 版 / Zoomable HTML]({html_link})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"
    )
    lines.append("")

    # 概述
    lines.append("## 概述")
    lines.append("")
    lines.append("数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。")
    lines.append('- depgraph 表达"谁依赖谁"（模块依赖）')
    lines.append('- dataflowgraph 表达"数据从哪流到哪"（数据流向）')
    lines.append("- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联")
    lines.append("")

    # 域基本信息表（模板 §3.1）
    lines.append("## 域基本信息 / Overview")
    lines.append("")
    lines.append("| 字段 | 值 | Field | Value |")
    lines.append("|------|------|-------|-------|")
    lines.append(f"| Dataset 数 | {len(datasets)} | Datasets | {len(datasets)} |")
    lines.append(f"| Job 数 | {len(jobs)} | Jobs | {len(jobs)} |")
    lines.append(f"| Edge 数 | {len(edges)} | Edges | {len(edges)} |")
    lines.append(f"| 运营态 Dataset | {prod_m_ds} | Production Datasets | {prod_m_ds} |")
    lines.append(f"| 设计态 Dataset | {design_ds} | Design Datasets | {design_ds} |")
    lines.append(f"| 运营态 Job | {prod_m_job} | Production Jobs | {prod_m_job} |")
    lines.append(f"| 设计态 Job | {design_job} | Design Jobs | {design_job} |")
    lines.append("")

    # 统计（scope 维度）
    lines.append("## 统计")
    lines.append("")
    lines.append("| 类型 | 生产 (production) | 回测内部 (backtest_internal) | 合计 |")
    lines.append("|------|-------------------|------------------------------|------|")
    lines.append(f"| Dataset | {prod_ds} | {bt_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_job} | {bt_job} | {len(jobs)} |")
    lines.append(f"| Edge | - | - | {len(edges)} |")
    lines.append("")
    # design_maturity 维度统计（对标 decision_index.md / depgraph 设计态/运营态机制）
    lines.append("### 设计态 / 运营态统计（design_maturity）")
    lines.append("")
    lines.append("| 类型 | 运营态 (production) | 设计态 (design) | 合计 |")
    lines.append("|------|---------------------|-----------------|------|")
    lines.append(f"| Dataset | {prod_m_ds} | {design_ds} | {len(datasets)} |")
    lines.append(f"| Job | {prod_m_job} | {design_job} | {len(jobs)} |")
    lines.append("")
    lines.append(
        "> **设计态 vs 运营态 / Design vs Production**：`design_maturity` 字段区分——"
        "`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。"
        "对标 depgraph 的设计态/运营态机制（decision_index.md）。"
    )
    lines.append("")

    # 三视图（模板 §3.2 铁律：全景图 → 运营态的图 → 设计态的图）
    lines.append("## 数据流图")
    lines.append("")
    lines.append(_LEGEND_BLOCK.rstrip())
    lines.append("")

    # ① 全景图（全部节点，颜色区分运营态/设计态）
    lines.append("### 全景图（全部模块，颜色区分运营态/设计态）")
    lines.append("")
    mmd_overview, o_ds, o_job, o_edge = _gen_mermaid(datasets, jobs, edges, scope_filter=None)
    lines.append(
        f"> 展示全部 {o_ds + o_job} 个节点（Dataset {o_ds} + Job {o_job}），含 {o_edge} 条边。颜色区分运营态（蓝）/设计态（橙虚线）。"
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append(mmd_overview.rstrip())
    lines.append("```")
    lines.append("")

    # ② 运营态的图（仅 design_maturity=production）
    lines.append("### 运营态的图（仅 design_maturity=production）")
    lines.append("")
    mmd_op, op_ds, op_job, op_edge = _gen_mermaid(
        datasets, jobs, edges, scope_filter=None, maturity_filter="production"
    )
    if op_ds > 0 or op_job > 0:
        lines.append(
            f"> 仅展示已实现稳定运行的节点（运营态：{op_ds} datasets / 数据集, {op_job} jobs / 作业, {op_edge} edges / 边）。"
        )
        lines.append("")
        lines.append("```mermaid")
        lines.append(mmd_op.rstrip())
        lines.append("```")
    else:
        lines.append("> （无模块 / No modules）")
    lines.append("")

    # ③ 设计态的图（仅 design_maturity=design）
    lines.append("### 设计态的图（仅 design_maturity=design）")
    lines.append("")
    mmd_des, d_ds2, d_job2, d_edge2 = _gen_mermaid(datasets, jobs, edges, scope_filter=None, maturity_filter="design")
    if d_ds2 > 0 or d_job2 > 0:
        lines.append(
            f"> 仅展示蓝图阶段、代码未写的设计态节点（设计态：{d_ds2} datasets / 数据集, {d_job2} jobs / 作业, {d_edge2} edges / 边）。"
        )
        lines.append("")
        lines.append("```mermaid")
        lines.append(mmd_des.rstrip())
        lines.append("```")
    else:
        lines.append("> （无模块 / No modules）")
    lines.append("")

    # scope 附加视图（模板 §9.2 可调整项：按 scope 维度补充）
    lines.append("### 生产数据流图（scope=production，附加视图）")
    lines.append("")
    mmd_prod, p_ds, p_job, p_edge = _gen_mermaid(datasets, jobs, edges, scope_filter="production")
    if p_ds > 0 or p_job > 0:
        lines.append(f"> 节点数: {p_ds} datasets / 数据集, {p_job} jobs / 作业, {p_edge} edges / 边")
        lines.append("")
        lines.append("```mermaid")
        lines.append(mmd_prod.rstrip())
        lines.append("```")
    else:
        lines.append("> （无模块 / No modules）")
    lines.append("")

    lines.append("### 回测内部数据流图（scope=backtest_internal，附加视图）")
    lines.append("")
    mmd_bt, b_ds, b_job, b_edge = _gen_mermaid(datasets, jobs, edges, scope_filter="backtest_internal")
    if b_ds > 0 or b_job > 0:
        lines.append(f"> 节点数: {b_ds} datasets / 数据集, {b_job} jobs / 作业, {b_edge} edges / 边")
        lines.append("")
        lines.append("```mermaid")
        lines.append(mmd_bt.rstrip())
        lines.append("```")
    else:
        lines.append("> （无模块 / No modules）")
    lines.append("")

    # Dataset 清单
    lines.append("## Dataset 清单")
    lines.append("")
    lines.append(
        "| ID | entity_name / 实体名 | scope / 范围 | contract_ref / 契约引用 | domain / 域 | pit_policy / PIT策略 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |"
    )
    lines.append(
        "|----|----------------------|--------------|---------------------------|------------|------------------|------------------|---------------------------|--------------------|----------|"
    )
    for d in datasets:
        fmt = (d.get("format_summary") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| DS-{d['id']:03d} | {_en_zh(d['name'])} | {_en_zh(d['scope'])} | "
            f"{d['contract'] or '-'} | {_domain_en_zh(d['domain'] or '-')} | {_en_zh(d['pit'])} | {d.get('module_id') or '-'} | {_en_zh(d.get('maturity') or '-')} | {_en_zh(d['build'])} | {fmt} |"
        )

    # Job 清单
    lines.append("")
    lines.append("## Job 清单")
    lines.append("")
    lines.append(
        "| ID | job_name / 作业名 | scope / 范围 | source_code_ref / 源码引用 | trigger_type / 触发类型 | run_context / 运行上下文 | module_id / 蓝图 | design_maturity / 设计成熟度 | build_status / 构建状态 | 功能简述 |"
    )
    lines.append(
        "|----|-------------------|--------------|------------------------------|----------------------------|------------------------------|------------------|---------------------------|--------------------|----------|"
    )
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
    {
        "key": "d_factor_ashare",
        "title": "因子域-A股因子计算",
        "domains": {"D_FACTOR"},
        "path_contains": "/ashare/",
        "responsibility": "A股Alpha因子计算——Alpha87/资金流/跨市场/基本面/机构/日内/IRL/市场结构/微观结构/形态/PS流动性/板块/SMC/技术指标等14类截面因子信号",
    },
    {
        "key": "d_factor_analysis",
        "title": "因子域-因子分析",
        "domains": {"D_FACTOR"},
        "path_contains": "/analysis/",
        "responsibility": "因子分析与评估——IC/IR计算评估、衰减监控、相关性去重、归因、优化、分层回测、多因子合成、三级研判、换手率分析",
    },
    {
        "key": "d_factor_barra_mine",
        "title": "因子域-Barra风险模型与因子挖掘",
        "domains": {"D_FACTOR"},
        "path_contains": ("/barra/", "/mine/"),
        "responsibility": "Barra风险模型与因子挖掘——ESG/暴露计算/风险预算/协方差风险模型 + 因果性验证/AI因子挖掘Agent",
    },
    {
        "key": "d_backtest",
        "title": "回测域-回测服务",
        "domains": {"D_BACKTEST"},
        "responsibility": "回测分析服务——异常诊断/数据质量检查/衰减监控/NaN处理/参数分析/报告生成/结果对比/结果部署",
    },
    {
        "key": "d_data",
        "title": "数据域-数据采集管理",
        "domains": {"D_DATA"},
        "responsibility": "数据采集与管理——特征存储/K线重采样/实时推送管理/板块快照采集/Tick数据管理",
    },
    {
        "key": "d_data_eng",
        "title": "数据工程域-数据工程服务",
        "domains": {"D_DATA_ENG"},
        "responsibility": "数据工程服务——数据湖管理/知识清洗/流处理/合成数据生成/训练数据管理",
    },
    {
        "key": "d_ex_pf_core",
        "title": "执行核心+组合核心域",
        "domains": {"D_EX_CORE", "D_PF_CORE"},
        "responsibility": "执行核心+组合核心——审计日志/成交处理/持仓跟踪/实盘组合 + 组合优化/汇总/策略运行/TopN动量策略",
    },
    {
        "key": "d_others",
        "title": "其他域-ML训练+风控+交易",
        "domains": {"D_ML_TRAIN", "D_RISK", "D_TRADING"},
        "responsibility": "ML训练+风控+交易——AI操作员决策/训练流水线 + 回撤跟踪 + PnL计算",
    },
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


def _gen_domain_md(
    grp: dict,
    datasets: list[dict],
    jobs: list[dict],
    edges: list[dict],
    all_datasets: list[dict] | None = None,
) -> str:
    """生成单个域分组的 Markdown 文档（模板 V1.2 三视图 + HTML 链接 + 跨域外部节点 + 清单）。

    治本（2026-08-01 模板 V1.2 升级）：三视图顺序固定为 全景图 → 运营态的图 → 设计态的图
    （模板 §3.2 铁律）；全景图含跨域外部 Dataset 节点（external_ds，由 all_datasets 解析），
    运营态/设计态分图不含跨域节点；顶部加 HTML 跳转链接；空视图用占位说明。

    :param all_datasets: 全量 Dataset（用于解析全景图跨域外部节点）；None 时回退到 datasets
    """
    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源（脚本最近 git commit 时间）
    now = idempotent_timestamp(Path(__file__))
    title = grp["title"]
    key = grp["key"]
    html_link = _html_link_for(key)

    # 跨域外部 Dataset（全景图用）：被本域 Job 消费但不属于本域的 Dataset
    ext_ds = _collect_external_datasets(jobs, datasets, all_datasets or datasets, edges)

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
    lines.append("> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表")
    lines.append("> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）")
    lines.append("")
    # HTML 跳转链接（模板 §14）
    lines.append(
        f"> **[可缩放 HTML 版 / Zoomable HTML]({html_link})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"
    )
    lines.append("")

    # 域职责（对标 06_decision_architecture 的"域职责 / Responsibility"说明）
    responsibility = grp.get("responsibility", "")
    if responsibility:
        lines.append(f"> **域职责 / Responsibility**: {responsibility}")
        lines.append("")

    # 域基本信息表（模板 §3.1）
    prod_m_ds = sum(1 for d in datasets if d.get("maturity") == "production")
    design_ds_n = sum(1 for d in datasets if d.get("maturity") == "design")
    prod_m_job = sum(1 for j in jobs if j.get("maturity") == "production")
    design_job_n = sum(1 for j in jobs if j.get("maturity") == "design")
    lines.append("## 域基本信息 / Overview")
    lines.append("")
    lines.append("| 字段 | 值 | Field | Value |")
    lines.append("|------|------|-------|-------|")
    lines.append(f"| Dataset 数 | {len(datasets)} | Datasets | {len(datasets)} |")
    lines.append(f"| Job 数 | {len(jobs)} | Jobs | {len(jobs)} |")
    lines.append(f"| 运营态 Dataset | {prod_m_ds} | Production Datasets | {prod_m_ds} |")
    lines.append(f"| 设计态 Dataset | {design_ds_n} | Design Datasets | {design_ds_n} |")
    lines.append(f"| 运营态 Job | {prod_m_job} | Production Jobs | {prod_m_job} |")
    lines.append(f"| 设计态 Job | {design_job_n} | Design Jobs | {design_job_n} |")
    if ext_ds:
        lines.append(f"| 跨域外部 Dataset | {len(ext_ds)} | Cross-domain Datasets | {len(ext_ds)} |")
    lines.append("")

    # 数据流图（三视图 + 图例）
    lines.append("## 数据流图")
    lines.append("")
    lines.append(_LEGEND_BLOCK.rstrip())
    lines.append("")

    # ① 全景图（全部模块，颜色区分运营态/设计态，含跨域外部节点）
    lines.append("### 全景图（全部模块，颜色区分运营态/设计态）")
    lines.append("")
    all_mmd, a_ds, a_job, a_edge = _gen_mermaid(
        datasets,
        jobs,
        edges,
        scope_filter=None,
        maturity_filter=None,
        external_ds=ext_ds,
    )
    ext_hint = f"，含 {len(ext_ds)} 个跨域外部 Dataset" if ext_ds else ""
    lines.append(
        f"> 展示全部 {a_ds + a_job} 个节点（Dataset {a_ds} + Job {a_job}），含 {a_edge} 条边{ext_hint}。颜色区分运营态（蓝）/设计态（橙虚线）。"
    )
    lines.append("")
    lines.append("```mermaid")
    lines.append(all_mmd.rstrip())
    lines.append("```")
    lines.append("")

    # ② 运营态的图（仅 design_maturity=production，不含跨域节点）
    lines.append("### 运营态的图（仅 design_maturity=production）")
    lines.append("")
    op_mmd, op_ds, op_job, op_edge = _gen_mermaid(
        datasets,
        jobs,
        edges,
        scope_filter=None,
        maturity_filter="production",
    )
    if op_ds > 0 or op_job > 0:
        lines.append(
            f"> 仅展示已实现稳定运行的节点（运营态：{op_ds} datasets / 数据集, {op_job} jobs / 作业, {op_edge} edges / 边）。"
        )
        lines.append("")
        lines.append("```mermaid")
        lines.append(op_mmd.rstrip())
        lines.append("```")
    else:
        lines.append("> （无模块 / No modules）")
    lines.append("")

    # ③ 设计态的图（仅 design_maturity=design，不含跨域节点）
    lines.append("### 设计态的图（仅 design_maturity=design）")
    lines.append("")
    design_mmd, d_ds, d_job, d_edge = _gen_mermaid(
        datasets,
        jobs,
        edges,
        scope_filter=None,
        maturity_filter="design",
    )
    if d_ds > 0 or d_job > 0:
        lines.append(
            f"> 仅展示蓝图阶段、代码未写的设计态节点（设计态：{d_ds} datasets / 数据集, {d_job} jobs / 作业, {d_edge} edges / 边）。"
        )
        lines.append("")
        lines.append("```mermaid")
        lines.append(design_mmd.rstrip())
        lines.append("```")
    else:
        lines.append("> （无模块 / No modules）")
    lines.append("")

    # Dataset 清单（设计态 + 运营态合并，design_maturity 列区分）
    lines.append("## Dataset 清单")
    lines.append("")
    lines.append(
        "| ID | entity_name / 实体名 | scope / 范围 | domain / 域 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |"
    )
    lines.append(
        "|----|----------------------|--------------|------------|------------------------------|------------------|----------|"
    )
    for d in datasets:
        fmt = (d.get("format_summary") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| DS-{d['id']:03d} | {_en_zh(d['name'])} | {_en_zh(d['scope'])} | "
            f"{_domain_en_zh(d['domain'] or '-')} | {_en_zh(d.get('maturity') or '-')} | "
            f"{d.get('module_id') or '-'} | {fmt} |"
        )

    # Job 清单（设计态 + 运营态合并，design_maturity 列区分）
    lines.append("")
    lines.append("## Job 清单")
    lines.append("")
    lines.append(
        "| ID | job_name / 作业名 | trigger_type / 触发类型 | design_maturity / 设计成熟度 | module_id / 蓝图 | 功能简述 |"
    )
    lines.append(
        "|----|-------------------|----------------------------|------------------------------|------------------|----------|"
    )
    for j in jobs:
        jdesc = (j.get("description") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| JOB-{j['id']:03d} | {_en_zh(j['name'])} | "
            f"{_en_zh(j['trigger'] or '-')} | {_en_zh(j.get('maturity') or '-')} | "
            f"{j.get('module_id') or '-'} | {jdesc} |"
        )

    # 跨域依赖清单（出边：本域 Job 产出的 Dataset 被其他域 Job 消费；入边：外部 Dataset 被本域 Job 消费）
    if ext_ds:
        lines.append("")
        lines.append("## 跨域依赖 / Cross-domain Dependencies")
        lines.append("")
        lines.append("### 依赖本域的外部 Dataset（入边）/ Consumed From")
        lines.append("")
        lines.append("| 外部 Dataset | 域 | 成熟度 | 被本域 Job 消费 |")
        lines.append("|-------------|------|--------|----------------|")
        # 找到消费外部 dataset 的本域 job
        job_map = {j["id"]: j for j in jobs}
        for d in ext_ds:
            consumers = []
            for e in edges:
                if (
                    e["from_type"] == "dataset"
                    and e["from_id"] == d["id"]
                    and e["to_type"] == "job"
                    and e["to_id"] in job_map
                ):
                    consumers.append(job_map[e["to_id"]]["name"])
            lines.append(
                f"| {d['name']} | {_domain_en_zh(d.get('domain') or '-')} | "
                f"{_en_zh(d.get('maturity') or '-')} | {', '.join(consumers) or '-'} |"
            )

    lines.append("")
    lines.append("[← 返回索引](dataflow_index.md)")
    return "\n".join(lines) + "\n"


def _gen_overview_index(
    datasets: list[dict], jobs: list[dict], edges: list[dict], group_counts: dict[str, dict]
) -> str:
    """生成索引文件（概览 + 统计 + 链接到各域文件）。"""
    # 治本（#ARCH-REGEN-NONIDEMPOTENT-001，2026-08-05）：幂等时间源（脚本最近 git commit 时间）
    now = idempotent_timestamp(Path(__file__))
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
    lines.append("> 真源: `dataflow_graph_registry.yaml` → PostgreSQL `dataflow_*` 表（ARCH-051）")
    lines.append("> 生成器: `generate_dataflow_diagram.py`（全文自动生成，禁止手工编辑）")
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

    # 全景链接（运营态 + 设计态，一张图看完所有数据流）
    lines.append("## 数据流全景（运营态 + 设计态）")
    lines.append("")
    lines.append(
        f"> {len(jobs)} 个作业 / {len(datasets)} 个数据集 / {len(edges)} 条边（含设计态 {design_job} jobs / {design_ds} datasets）"
    )
    lines.append("")
    lines.append(
        "- [dataflow_panorama.md](dataflow_panorama.md) — 全项目数据流全景图（运营态+设计态）+ Dataset/Job 清单"
    )
    lines.append(f"- [可缩放 HTML 版]({_html_link_for('dataflow_panorama')}) — 浏览器打开可 Ctrl+滚轮缩放")
    lines.append("")

    # 域文件链接（每个域文档含三视图：全景图→运营态的图→设计态的图）
    lines.append("## 数据流（按域拆分，含三视图）")
    lines.append("")
    lines.append(
        f"> {len(jobs)} 个作业 / {len(datasets)} 个数据集 / {len(edges)} 条边，按功能域拆分（每个域文档含三视图：全景图 → 运营态的图 → 设计态的图）："
    )
    lines.append("")
    lines.append("| 文件 | 功能域 | Job 数 | Dataset 数 | 可缩放 HTML |")
    lines.append("|------|--------|:---:|:---:|:---:|")
    for grp in _DOMAIN_GROUPS:
        gc = group_counts.get(grp["key"], {"jobs": 0, "datasets": 0})
        html_l = f"[HTML]({_html_link_for(grp['key'])})" if gc["jobs"] else "-"
        lines.append(
            f"| [{grp['key']}.md]({grp['key']}.md) | {grp['title']} | {gc['jobs']} | {gc['datasets']} | {html_l} |"
        )
    lines.append("")

    lines.append("## 概述")
    lines.append("")
    lines.append("数据流图（dataflowgraph）是与依赖图（depgraph）正交的第三维度全景图。")
    lines.append('- depgraph 表达"谁依赖谁"（模块依赖）')
    lines.append('- dataflowgraph 表达"数据从哪流到哪"（数据流向）')
    lines.append("- 通过 `Job.source_code_ref` 引用 depgraph 模块 path，建立跨图关联")
    lines.append("")
    lines.append(
        "> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。"
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: parse args, run logic, return exit code.

    生成多文件：
    - dataflow_index.md    — 索引+统计+链接
    - dataflow_panorama.md — 全项目数据流全景图（运营态+设计态）+清单
    - d_factor_ashare.md 等 — 按域拆分（8 个域文件，各含三视图）
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

    # 辅助：写 MD 后联动生成可缩放 HTML（模板 V1.2 §9.1 #1：MD+HTML 双产物）
    def _write_md_and_html(stem: str, md_text: str) -> None:
        """_write_md_and_html implementation."""
        md_path = out_dir / f"{stem}.md"
        md_path.write_text(md_text, encoding="utf-8", newline="\n")
        html_path = emit_zoomable_html(md_path, md_text, out_dir / HTML_SUBDIR)
        if html_path:
            print(f"[OK]   └ _zoomable_html/{stem}.html（可缩放交互版）")

    # 1. 生成全项目数据流全景文件（运营态 + 设计态，一张图看完所有数据流）
    panorama_md = _gen_panorama_md(datasets, jobs, edges)
    _write_md_and_html("dataflow_panorama", panorama_md)
    print(f"[OK] 生成 dataflow_panorama.md（{len(jobs)} jobs / {len(datasets)} datasets，含设计态）")

    # 2. 按域分组所有 Job + Dataset（含设计态+运营态，每个域文档三视图展示）
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
        produced_ds_ids = {e["to_id"] for e in edges if e["from_type"] == "job" and e["from_id"] in job_ids}
        for d in datasets:
            if d["id"] in produced_ds_ids:
                group_datasets[grp_key].append(d)

    # 3. 生成各域文件（模板 V1.2 三视图，传 all_datasets 解析跨域外部节点）
    group_counts = {}
    for grp in _DOMAIN_GROUPS:
        key = grp["key"]
        g_jobs = group_jobs.get(key, [])
        g_ds = group_datasets.get(key, [])
        if not g_jobs:
            continue
        md = _gen_domain_md(grp, g_ds, g_jobs, edges, all_datasets=datasets)
        _write_md_and_html(key, md)
        print(f"[OK] 生成 {key}.md（{len(g_jobs)} jobs / {len(g_ds)} datasets）")
        group_counts[key] = {"jobs": len(g_jobs), "datasets": len(g_ds)}

    # 处理未知域
    if group_jobs.get("d_unknown"):
        g_jobs = group_jobs["d_unknown"]
        g_ds = group_datasets.get("d_unknown", [])
        unk_grp = {"key": "d_unknown", "title": "未分类域"}
        md = _gen_domain_md(unk_grp, g_ds, g_jobs, edges, all_datasets=datasets)
        _write_md_and_html("d_unknown", md)
        print(f"[OK] 生成 d_unknown.md（{len(g_jobs)} jobs）")
        group_counts["d_unknown"] = {"jobs": len(g_jobs), "datasets": len(g_ds)}

    # 4. 生成索引文件（无 Mermaid 块，不生成 HTML）
    index_md = _gen_overview_index(datasets, jobs, edges, group_counts)
    (out_dir / "dataflow_index.md").write_text(index_md, encoding="utf-8", newline="\n")
    print("[OK] 生成 dataflow_index.md（索引+统计+链接）")

    # 5. 清理过时 HTML（域分组变更后旧 HTML 残留，模板 §16 reconciler 回退应对）
    # 治本（2026-08-01）：本目录 _zoomable_html/ 由两个生成器共享——
    # generate_data_acquisition_flow.py 也输出 data_acquisition_flow.html 到此处，
    # 清理时必须保留它，否则交叉运行会互相删 HTML。
    html_dir = out_dir / HTML_SUBDIR
    if html_dir.exists():
        valid_stems = {"dataflow_panorama", "dataflow_index", "data_acquisition_flow"} | set(group_counts.keys())
        for old_html in html_dir.glob("*.html"):
            if old_html.stem not in valid_stems:
                old_html.unlink()
                print(f"[OK] 清理过时 HTML: {old_html.name}")

    print(f"\n输出目录: {out_dir}")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
