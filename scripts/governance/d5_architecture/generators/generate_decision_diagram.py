# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.d5_architecture.generators.generate_decision_diagram
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); architecture_model/domain/decision_graph_model.yaml (invariants 真源); _common (cleanup_stale_files, DB_DISPLAY_NAME); _shared.terminology_loader (get_category_map); zoomable_html (emit_zoomable_html, HTML_SUBDIR)
# [CONSUMERS] CI自动触发;人工查看06_decision_architecture/
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 输出幂等(相同输入→相同输出22文件);只读decisiongraph;输出到06_decision_architecture/;序号硬编码稳定
# [MODIFY-GUARD] 修改需通过TRAE-061任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] decisiongraph不存在→exit 1;无tracks/layers→exit 2;域集合漂移→exit 3
# [TESTS] tests/test_generate_decision_diagram.py
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""G-decision: 从 decisiongraph (PostgreSQL) 生成决策流图(.md 文档，Mermaid 内嵌)

依据：TRAE-061 任务（2026-07-06）；拆分重构（2026-07-19）。

功能：
  - 从 decision_tracks / decision_layers / decision_nodes / decision_edges 表读取决策流图
  - 从 decision_graph_model.yaml 读取 invariants 定义（5 条承重墙不变量）
  - 生成 Mermaid 图表并内嵌在 Markdown ```mermaid 代码块中
  - 输出到 docs/02_enterprise_architecture/06_decision_architecture/

输出文件（22 个，治本拆分，对标 02_domain_architecture_docs/ 模式）：
  - decision_index.md              主索引（纯导航，0 个 mermaid）
  - 01..05_decision_track_*.md     5 个 Track 文件（各 3 视图：合并/设计态/运营态）
  - 06..12_decision_l2a_*.md       7 个 L2A 功能域文件
  - 13..19_decision_l3_*.md        7 个 L3 功能域文件
  - 20_decision_layers.md          层级详情图
  - 21_decision_invariants.md      不变量图

用法
----
    python scripts/governance/d5_architecture/generators/generate_decision_diagram.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G-decision: 从 decisiongraph (PostgreSQL) 生成决策流图(.md 文档，Mermaid 内嵌)'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# 治本：_shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# 治本（2026-08-01 模板升级）：zoomable_html.py 与本文件同目录，须将 generators 目录
# 加入 sys.path，使 `from zoomable_html import` 在运行时与 importlib 测试加载下都可用。
_GENERATORS_DIR = str(Path(__file__).resolve().parent)
if _GENERATORS_DIR not in sys.path:
    sys.path.insert(0, _GENERATORS_DIR)

from _shared.constants import DOC_HTTP_BASE, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS

# 术语翻译真源（SSoT：terminology_glossary.yaml，禁止硬编码中文字典）
from _shared.terminology_loader import get_category_map

try:
    from _common import DB_DISPLAY_NAME, cleanup_stale_files  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

    def cleanup_stale_files(output_dir: Path, expected: set[str], pattern: str) -> list[str]:  # noqa: ARG001
        """降级 stub：_common 不可用时不动文件。"""
        return []

# 可缩放 HTML 联动生成（md→_zoomable_html/ 子文件夹同步）。真源：zoomable_html.py。
# 对齐 generate_domain_doc.py 的联动模式（visualization_view_template.md §2/§8.4）。
from zoomable_html import HTML_SUBDIR, emit_zoomable_html  # noqa: E402

from zephyr.governance.persistence.decisiongraph_schema import (  # noqa: E402
    get_decisiongraph_pg_connection,
)

OUTPUT_DIR = _REPO_ROOT / "docs" / "02_enterprise_architecture" / "06_decision_architecture"
_YAML_PATH = _REPO_ROOT / "architecture_model" / "domain" / "decision_graph_model.yaml"


# 治本（2026-07-31）：在决策流图索引头部加大白话解释，让入口索引对非架构读者也友好。
# 覆盖：决策流是什么、决策流图是什么、有什么用、和依赖图啥关系、这份索引看什么。
# 风格对齐 generate_domain_index.py 的 _PLAIN_LANGUAGE_INTRO。
_DECISION_PLAIN_LANGUAGE_INTRO = """\
## 这是什么？大白话讲决策流图

这份"决策流图索引"背后是一张**决策流图（decisiongraph）**。在往下看清单之前，先用大白话讲清楚它是什么、有什么用、为什么要看。

### 一、决策流是什么意思？

一笔交易要一步步做决定：先产生信号 → 再做风控检查 → 再决定买什么买多少 → 再下单 → 最后执行。这条"决策一步步怎么往下走"的链路，就叫**决策流**。

把项目里所有这种"决策怎么产生、怎么往下传"的关系记下来，就是**决策流**。

### 二、决策流图是什么？

把决策链上的**每一步**当成点，把"前一步触发后一步"当成连线，画成一张大网，就是决策流图。

- 它不是一张图片，是存在数据库（`depgraph`）里的一张表
- 四个基本元件：
  - **Track（轨）** —— 决策走哪条道（模型驱动 / 数据驱动 / 人工指令 / 应急保命）
  - **Layer（层）** —— 决策链的第几步（L0 信号 → … → L6 反馈）
  - **Node（节点）** —— 每一步具体做什么的决策点
  - **Edge（边）** —— 上下步之间怎么触发、怎么传

### 三、决策流图有什么用？它和依赖图啥关系？

这个项目有三张正交的全景图，各管一摊：

| 全景图 | 管什么 | 举个例子 |
|---|---|---|
| 依赖图 depgraph | 模块**谁依赖谁**（静态） | 风控模块 import 了因子模块 |
| 数据流图 dataflowgraph | 数据从哪流到哪（动态） | 行情数据 → 因子 → 回测 |
| **决策流图 decisiongraph** | **决策怎么产生**（动态） | 信号 → 风控 → 下单 → 执行 |

**为什么要看决策流图**：看决策链（一笔交易从信号到执行经过哪些步）、找断点（该有的风控检查有没有）、排查"这个决定是谁做的"（某个下单是模型驱动还是人工指令，走哪条轨）。

**一句话**：依赖图管"模块关系"，决策流图管"决策走向"——一个看代码结构，一个看决策逻辑。

### 四、这份索引主要看什么？

1. **决策链有几条轨** —— 看"Track 导航"表，5 条轨各有分工
2. **决策链长啥样** —— 点进各 Track 文档看 Mermaid 图
3. **每一步是什么** —— 看 Layer / Node 清单，知道决策链上每步具体做什么

> 运营态 = 实际代码已实现的决策步；设计态 = 还在图纸上没动工的决策步。

---
"""

# --- 文件编号（硬编码，字母序保证跨重生成稳定） ---
# Track 01-05 按 priority（DB ORDER BY priority）；L2A 06-12 按域名字母序；L3 13-19 按域名字母序
_L2A_DOMAINS_ALPHA = ["data", "factor", "frontend", "research", "sell", "signal", "simulation"]
_L3_DOMAINS_ALPHA = ["aut_core", "ex_core", "ex_sor", "pf_alloc", "pf_core", "position", "trading"]
_L2A_DOMAIN_LAYER = "L2A"
_L3_DOMAIN_LAYER = "L3"
_L2A_SEQ_OFFSET = 6   # 06..12
_L3_SEQ_OFFSET = 13   # 13..19
_LAYERS_FILE_NAME = "20_decision_layers.md"
_INVARIANTS_FILE_NAME = "21_decision_invariants.md"
_STALE_FILE_REGEX = r"^\d{2}_decision_[a-z0-9_]+\.md$"
# 架构层 ID 正则：L0-L6（含 L2A/L2B/L2C/L2D 子层）。decision_layers 表还含
# 模块级条目（MOD-*/CFG-*/INFRA-*/SH-*/SYS-*，约 650 个），层级详情图只画
# L0-L6 架构层——模块详情已在 01-19 per-track/per-domain 文件覆盖，全画会导致
# mermaid 节点数超限（>300）渲染失败。
_ARCH_LAYER_RE = re.compile(r"^L[0-6]")

# --- Mermaid 主题策略（用户 VS Code 1.129.1 实测确认 2026-07-30）---
# 用户在 VS Code Markdown Preview 中实测确认：
#   1. %%{init}%% 主题变量生效——flowchart 节点填充为 #eaeaea 灰色 ✓
#   2. subgraph 内节点使用 secondaryColor 而非 primaryColor——若不设
#      secondaryColor，subgraph 内节点回退白色（_gen_overview_mmd 有 track subgraph）
#   3. clusterBkg/clusterBorder 不被 VS Code mermaid 渲染器识别，已移除
# 故：primaryColor + secondaryColor + tertiaryColor 全设 #eaeaea，保证无论
# 节点是否在 subgraph 内都显示灰色。_gen_layers_mmd/invariants/cross_domain
# 已去掉 subgraph（扁平布局），_gen_overview_mmd 保留 track subgraph（需 secondaryColor）。
# _build_status_color() 保留供测试使用；生成逻辑用文字标注 build_status。
# 治本（2026-08-01 模板升级，2026-08-02 V1.3 增量）：对齐 visualization_view_template.md V1.3。
#   ① 灰色主题头（§4.1）+ clusterBkg/clusterBorder 透明（§13.3：subgraph 容器背景
#      默认浅蓝白，VS Code 渲染器不识别 clusterBkg，但 HTML 端 zoomable_html.py 已用
#      JS `style.fill='transparent'` 后处理 + CSS `.cluster rect` 兜底；此处主题变量
#      透明是第三层防线，无 subgraph 的图零影响）。
#   ② fontSize 14px 是 Mermaid 测量字号；HTML 渲染字号 11px（zoomable_html CSS）< 测量字号，
#      渲染比测量更窄更矮，只可能宽松不可能溢出（§4.10 配套纪律）。
_MERMAID_INIT = (
    "%%{init: {'theme': 'base', 'themeVariables': "
    "{'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', "
    "'primaryBorderColor': '#666666', 'lineColor': '#666666', "
    "'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', "
    "'clusterBkg': 'transparent', 'clusterBorder': 'transparent', "
    "'fontSize': '14px'}}}%%"
)

# classDef 四色（§4.7 铁律，照搬 generate_domain_doc.py:823-826，禁止自创色值）：
# 🟦 蓝色 = 运营态（production，已上线）/ 🟧 橙色虚线 = 设计态（design，蓝图阶段）
# external_* 更浅 + 1px 边框区分跨域节点（§4.7 表）。
_CLASSDEFS = (
    "    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000\n"
    "    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5\n"
    "    classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000\n"
    "    classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5"
)

# 图例说明 block（§3.1 铁律：每个含 mermaid 的文件在首个视图前放一次图例）。
_LEGEND_MD = (
    "> **图例说明 / Legend**：\n"
    "> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）\n"
    "> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）\n"
    "> - **实线箭头 `-->` = 运营态依赖**（两端都 production）\n"
    "> - **虚线箭头 `-.->` = 非运营态依赖**（含 design / 混合）"
)

# 本地 doc HTTP server 前缀（§14 铁律：MD 顶部 HTML 跳转链接必须用 http:// 绝对链接，
# 相对路径 / file:// 会在 IDE 编辑器内打开源码而非浏览器渲染）。
# 真源：_shared.constants.DOC_HTTP_BASE（MOD-INF-005 SSoT），不再此处硬编码。
_DOC_HTTP_BASE = DOC_HTTP_BASE

# 功能域英文→中文映射（双语标题/节点标签用）
# 真源：terminology_glossary.yaml 的 decision_domain_short 类别（经 _shared.terminology_loader 加载）
# 原硬编码字典已提升为 YAML 真源，消除跨生成器重复维护（D_FACTOR→因子 等不再三处各存）
_DOMAIN_NAME_ZH: dict[str, str] = get_category_map("decision_domain_short")

# 边类型英文→中文映射（mermaid 边标签 + 表格用 英文 / 中文 格式，参考 dataflow 风格）
# 真源：terminology_glossary.yaml 的 edge_type 类别（decision + dataflow 共享）
_EDGE_TYPE_ZH: dict[str, str] = get_category_map("edge_type")

# 节点类型英文→中文（Node 清单表用 英文 / 中文）。真源：glossary node_type 类别。
_NODE_TYPE_ZH: dict[str, str] = get_category_map("node_type")
# build_status 英文→中文（表格用 英文 / 中文）。真源：glossary build_status 类别。
_BUILD_STATUS_ZH: dict[str, str] = get_category_map("build_status")
# design_maturity 英文→中文（表格用 英文 / 中文）。真源：glossary maturity 类别。
_MATURITY_ZH: dict[str, str] = get_category_map("maturity")
# 功能域核心职责（domain 文件头部"功能域"行后展示）。真源：glossary domain_responsibility 类别。
_DOMAIN_RESPONSIBILITY_ZH: dict[str, str] = get_category_map("domain_responsibility")


# ---------------------------------------------------------------------------
# 模板 V1.3 标准辅助函数（照搬 generate_domain_doc.py，禁止自创逻辑）
# ---------------------------------------------------------------------------


def _wrap_label_text(text: str, max_units: int = 48) -> str:
    """将长节点标签文本按显示宽度预折行（Mermaid 节点内显示用）。

    治本铁律（visualization_view_template.md §4.10）：Mermaid 先按标签行数测量节点框
    宽高，若依赖 HTML 渲染层 CSS max-width 二次折行，渲染行数 > 测量行数 → 框高不够、
    文字被上下裁剪。必须在生成端用 <br/> 显式预折行，使测量行数 = 渲染行数。

    折行规则：显示宽度（CJK=2/ASCII=1）超 max_units 断行（48 ≈ 24 个汉字）；
    优先在空格/下划线之后、左括号/斜杠之前软断（保持英文词完整），否则硬断。
    原样复制自 generate_domain_doc.py，勿改逻辑（改了会重新踩裁剪坑）。
    """
    if not text:
        return ""
    lines: list[str] = []
    remaining = text.strip()
    while remaining:
        width = 0
        cut = 0
        soft = -1  # 软断点（断在空格/_之后，或（(/之前）
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
        if soft >= 8:  # 软断点至少留 8 单位，避免碎片行
            cut = soft
        line = remaining[:cut].rstrip()
        if line:
            lines.append(line)
        remaining = remaining[cut:].lstrip(" ")
    return "<br/>".join(lines)


def _sanitize_mermaid_label(text: str) -> str:
    """清理 Mermaid 标签中的特殊字符（方括号/引号/管道符）。§4.9。

    `[`→`(` `]`→`)` `"`→`'` `|`→`/`。原样复制自 generate_domain_doc.py。
    """
    if not text:
        return ""
    return text.replace("[", "(").replace("]", ")").replace('"', "'").replace("|", "/")


def _arrow(from_maturity: str | None, to_maturity: str | None) -> str:
    """边箭头：两端都 production 返回 `-->`（实线），否则 `-.->`（虚线）。§4.5。"""
    if from_maturity == "production" and to_maturity == "production":
        return "-->"
    return "-.->"


def _maturity_display(maturity: str | None) -> str:
    """成熟度 → 四要素①显示文本：`(生产态 / production)` / `(设计态 / design)`。§4.3。

    真源 terminology_glossary.yaml 的 maturity 类别映射为短形（生产/设计）；模板 §4.3 要求
    显示长形（生产态/设计态，与 generate_domain_doc.py MATURITY_DISPLAY 一致）。在此追加
    "态"后缀而非改共享词表——避免影响其他读 maturity 短形的消费者。
    """
    if not maturity:
        return "(未知 / unknown)"
    zh = _MATURITY_ZH.get(maturity, maturity)
    if zh and not zh.endswith("态"):
        zh = f"{zh}态"
    return f"({zh} / {maturity})"


def _split_zh_en(name: str | None, name_en: str | None) -> tuple[str, str]:
    """从 decision_name（DB 实测为"中文名 English"合并串）拆出纯中文 + 纯英文。

    DB 真源（Step 0 实测）：decision_name='止盈信号 Take-Profit Signal'，
    decision_name_en='Take-Profit Signal'。直接 `name / name_en` 会英文重复，
    故用 name_en 作后缀从 name 剥离得到纯中文。name_en 为空或非后缀时退化为原 name。

    治本（V1.3 §4.3）：当 name == name_en（DB 实测存在，如两者都为
    "Synthesizer 信号合成+权重分配"），剥离后 zh 为空 → 返回 (name, "") 避免标签
    显示"同名 / 同名"重复（坏类型⑤名称重复）。
    """
    name = (name or "").strip()
    en = (name_en or "").strip()
    if not en:
        return name, ""
    if name == en:
        # name 与 name_en 完全相同 → 仅显示一次，不输出英文（防重复，V1.3 §4.3）
        return name, ""
    if name.endswith(en):
        zh = name[:-len(en)].rstrip(" /-·—:：")
        if zh:
            return zh, en
    return name, en


def _node_label_4el(n: dict) -> str:
    """决策节点四要素标签：①成熟度 ②双语名 ③大白话 ④文件路径。§4.3/§4.11。

    ③大白话真源 = ``facets.plain_zh``（PostgreSQL decision_nodes.facets JSONB）。
    - 有 plain_zh → 显示它（三问法起草，真实非模板）。
    - 无 plain_zh → 诚实占位 ``（大白话待补 / plain_zh pending）``（V1.3 §4.11 禁止
      ``{type_zh}·{name_zh}`` 模板话占位，坏类型①模板话 + ⑤名称重复）。

    ②双语名：_split_zh_en 后若 zh==en 或 en 为空，仅显示一个名字，不输出
    ``zh / en`` 重复（§4.3，治本 V1.3）。

    每段过 _wrap_label_text 预折行后用 <br/> 拼接。
    """
    mat = n.get("maturity")
    zh, en = _split_zh_en(n.get("name"), n.get("name_en"))
    # ③大白话：facets.plain_zh 真源，无则诚实占位（V1.3 §4.11 治本）
    facets = n.get("facets") or {}
    plain_zh = facets.get("plain_zh") if isinstance(facets, dict) else None
    plain = plain_zh or "（大白话待补 / plain_zh pending）"
    path = n.get("path", "") or "-"
    parts = [
        f"{_maturity_display(mat)} {zh} / {en}" if en else f"{_maturity_display(mat)} {zh}",
        plain,
        f"文件: {path}",
    ]
    wrapped = [_wrap_label_text(p) for p in parts if p]
    return _sanitize_mermaid_label("<br/>".join(wrapped))


def _layer_label_4el(l: dict) -> str:
    """层级节点四要素标签：①成熟度 ②双语名(含层ID) ③大白话(desc) ④文件(module_id/source_code_ref)。§4.3。

    治本（V1.3 §4.10）：去掉 _truncate(desc, 40) 硬截断——预折行（_wrap_label_text）
    已处理长度，截断只会丢失信息（坏类型②截断）。改用完整 desc。
    """
    mat = l.get("maturity")
    lid = l.get("id", "") or ""
    zh = l.get("name", "") or ""
    en = l.get("name_en", "") or ""
    desc = (l.get("desc", "") or "").strip().replace("\n", " ")
    ref = l.get("source_code_ref") or l.get("module_id") or "（设计态，暂无代码引用）"
    name_line = f"{lid} {zh} / {en}" if en else f"{lid} {zh}"
    parts = [
        f"{_maturity_display(mat)} {name_line}",
        desc,
        f"文件: {ref}",
    ]
    wrapped = [_wrap_label_text(p) for p in parts if p]
    return _sanitize_mermaid_label("<br/>".join(wrapped))


def _class_apply_lines(prod_ids: list[str], design_ids: list[str],
                       ext_prod_ids: list[str] | None = None,
                       ext_design_ids: list[str] | None = None) -> str:
    """生成 class 应用行（§4.8）：按成熟度分组绑类。任一空组不输出该行。"""
    out: list[str] = []
    if prod_ids:
        out.append(f"    class {','.join(prod_ids)} production")
    if design_ids:
        out.append(f"    class {','.join(design_ids)} design")
    if ext_prod_ids:
        out.append(f"    class {','.join(ext_prod_ids)} external_prod")
    if ext_design_ids:
        out.append(f"    class {','.join(ext_design_ids)} external_design")
    return "\n".join(out)


def _html_link_line(md_stem: str) -> str:
    """构造 MD 顶部 HTML 跳转链接行（§14：http:// 绝对链接）。

    md_stem：MD 文件名去 .md（如 '10_decision_l2a_sell'）。HTML 同名输出到
    _zoomable_html/<stem>.html。
    """
    rel = f"docs/02_enterprise_architecture/06_decision_architecture/{HTML_SUBDIR}/{md_stem}.html"
    return (
        f"> **[可缩放 HTML 版 / Zoomable HTML]({_DOC_HTTP_BASE}/{rel})** "
        f"— Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式"
    )


def _git_commit_timestamp() -> str:
    """获取本生成器脚本最近一次 git commit 时间（ISO 8601 秒精度）。

    幂等时间源：相同 commit → 相同时间戳，避免 datetime.now() 导致输出非确定性。
    git 不可用或文件未入库时返回固定占位符。
    """
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", __file__],
            capture_output=True, text=True, timeout=5,
            cwd=str(_REPO_ROOT),
        )
        if r.returncode == 0 and r.stdout.strip():
            # %cI 输出形如 2026-07-19T13:47:00+08:00，截到秒
            return r.stdout.strip()[:19]
    except Exception:  # noqa: BLE001 — git 不可用时降级
        pass
    return "unknown"


def _parse_facets(raw) -> dict:
    """解析 decision_nodes.facets JSONB 列为 dict。

    psycopg2 对 JSONB 列默认返回 str（未注册 jsonb adapter 时）或 dict（已注册时）。
    本函数兼容两种：str→json.loads，dict/None→原样返回，解析失败→空 dict（降级，
    不让单个坏值阻断整批生成）。V1.3 §4.11：plain_zh 真源在此列。
    """
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return {}
        try:
            parsed = json.loads(s)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def _fetch_decision_data(conn) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """从 PG 读取 tracks/layers/nodes/edges。"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT track_id, track_name, track_name_en, description, priority, activation_condition
            FROM decision_tracks ORDER BY priority
        """)
        tracks = [
            {
                "id": r[0], "name": r[1], "name_en": r[2], "desc": r[3],
                "priority": r[4], "activation": r[5],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT layer_id, layer_name, layer_name_en, track, description,
                   decision_frequency, design_maturity, build_status,
                   module_id, source_code_ref
            FROM decision_layers ORDER BY layer_id
        """)
        layers = [
            {
                "id": r[0], "name": r[1], "name_en": r[2], "track": r[3],
                "desc": r[4], "freq": r[5], "maturity": r[6], "build": r[7],
                "module_id": r[8], "source_code_ref": r[9],
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT node_id, layer_id, node_type, path, module_id, decision_name,
                   decision_name_en, build_status, design_maturity, evidence_hash,
                   source_code_ref, facets
            FROM decision_nodes ORDER BY layer_id, node_id
        """)
        nodes = [
            {
                "id": r[0], "layer_id": r[1], "type": r[2], "path": r[3],
                "module_id": r[4], "name": r[5], "name_en": r[6], "build": r[7],
                "maturity": r[8], "hash": r[9], "source_code_ref": r[10],
                "facets": _parse_facets(r[11]),
            }
            for r in cur.fetchall()
        ]

        cur.execute("""
            SELECT edge_id, from_node_id, to_node_id, edge_type, condition, track
            FROM decision_edges ORDER BY edge_id
        """)
        edges = [
            {
                "id": r[0], "from": r[1], "to": r[2], "type": r[3],
                "condition": r[4], "track": r[5],
            }
            for r in cur.fetchall()
        ]

    return tracks, layers, nodes, edges


def _load_invariants() -> list[dict]:
    """从 YAML 真源读取 invariants 定义（5 条承重墙不变量）。"""
    with open(_YAML_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("invariants", [])


def _resolve_blueprint_names(conn, layers: list[dict]) -> dict[str, str]:
    """从 depgraph 查 module_id→blueprint_name 映射。

    :return: {module_id: blueprint_name}，查不到的 module_id 不包含在映射中
    """
    module_ids = {l.get("module_id") for l in layers if l.get("module_id")}
    if not module_ids:
        return {}
    result: dict[str, str] = {}
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT blueprint_id, node_name
                FROM nodes
                WHERE blueprint_id = ANY(%s)
                  AND node_name IS NOT NULL
                  AND node_name != ''
                """,
                (list(module_ids),),
            )
            for row in cur.fetchall():
                bp_id = row[0] if isinstance(row, (list, tuple)) else row.get("blueprint_id")
                bp_name = row[1] if isinstance(row, (list, tuple)) else row.get("node_name")
                if bp_id and bp_name:
                    result[bp_id] = bp_name
    except Exception:  # noqa: BLE001 — depgraph 查询失败时静默降级为仅展示 module_id
        pass
    return result


def _truncate(text: str, max_len: int = 20) -> str:
    """截断文本到指定长度，超出加省略号。"""
    if not text:
        return ""
    text = text.strip().replace("\n", " ").replace(">", "》")
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"


def _build_status_color(build: str) -> str:
    """build_status → mermaid 颜色类。"""
    return {
        "stable": "bsStable",
        "generated": "bsGenerated",
        "testing": "bsTesting",
        "planned": "bsPlanned",
        "deprecated": "bsDeprecated",
    }.get(build, "bsGenerated")


def _edge_label(edge_type: str) -> str:
    """边类型 → 中英文标签（英文 / 中文），参考 dataflow 的 produces / 产出风格。"""
    zh = _EDGE_TYPE_ZH.get(edge_type)
    if zh:
        return f"{edge_type} / {zh}"
    return edge_type


def _bilingual(value: str | None, zh_map: dict[str, str]) -> str:
    """值 → ``英文 / 中文``（表格单元格用）。无映射返回原值，None/空返回 ``-``。"""
    if not value:
        return "-"
    zh = zh_map.get(value)
    return f"{value} / {zh}" if zh else value


def _maturity_tag(maturity: str | None) -> str:
    """design_maturity → 标注标签（[production]/[design]/空）。"""
    if not maturity:
        return ""
    return f"[{maturity}]"


def _node_domain(path: str) -> str:
    """path 第 2 段（功能域），如 'decision/sell/sell_00' → 'sell'。

    path 不足 2 段返回空串（调用方负责跳过）。
    """
    parts = (path or "").split("/")
    return parts[1] if len(parts) >= 2 else ""


def _filter_overview_inputs(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
    *, maturity: str | None = None,
    track_id: str | None = None, path_prefix: str | None = None,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """全景图输入过滤辅助（复杂度收口，避免 _gen_overview_mmd 超 15）。

    过滤顺序：maturity → track_id → path_prefix（path 第 2 段精确匹配）→ 边端点 → 空 track。
    返回新列表，不修改输入。maturity 取值："production" / "design" / None（不过滤）。
    """
    # maturity 过滤
    if maturity is not None:
        layers = [l for l in layers if l.get("maturity") == maturity]
        layer_ids = {l["id"] for l in layers}
        nodes = [n for n in nodes if n["layer_id"] in layer_ids and n.get("maturity") == maturity]
    # track_id 过滤
    if track_id is not None:
        layers = [l for l in layers if l["track"] == track_id]
        layer_ids = {l["id"] for l in layers}
        nodes = [n for n in nodes if n["layer_id"] in layer_ids]
    # path_prefix 过滤（path 第 2 段精确匹配，不用 startswith 避免 sell/sell_algo 误匹配）
    if path_prefix is not None:
        nodes = [n for n in nodes if _node_domain(n.get("path", "")) == path_prefix]
    # 边端点必须都在过滤后节点集中
    node_ids = {n["id"] for n in nodes}
    edges = [e for e in edges if e["from"] in node_ids and e["to"] in node_ids]
    # tracks 过滤：只保留仍有 layer 的 track
    used_track_ids = {l["track"] for l in layers}
    tracks = [t for t in tracks if t["id"] in used_track_ids]
    return tracks, layers, nodes, edges


def _gen_overview_mmd(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
    production_only: bool = False, design_only: bool = False,
    track_id: str | None = None, path_prefix: str | None = None,
    skeleton_only: bool = False,
) -> tuple[str, int, int, int]:
    """生成全景图：L0-L6 层级 + 节点/边（扁平布局，无 subgraph）。

    Args:
        production_only: True 时仅 design_maturity='production'。
        design_only: True 时仅 design_maturity='design'。与 production_only 互斥。
        track_id: 仅生成该 track（用于 per-Track 文件）。
        path_prefix: 仅生成该 path 第 2 段域的节点（用于 per-domain 文件）。
        skeleton_only: True 时仅画 Layer 节点 + 层间边，跳过决策节点（用于 Track 概览图）。
    """
    # 将 production_only/design_only 转换为 maturity 单参（保持 _gen_overview_mmd 签名不变）
    _maturity = "production" if production_only else ("design" if design_only else None)
    tracks, layers, nodes, edges = _filter_overview_inputs(
        tracks, layers, nodes, edges,
        maturity=_maturity,
        track_id=track_id, path_prefix=path_prefix,
    )

    lines = [_MERMAID_INIT, "flowchart TD"]

    # 扁平布局（不使用 subgraph）——与 _gen_layers_mmd/_gen_invariants_mmd 一致。
    # subgraph 内节点用 secondaryColor 致 primaryColor 不生效（节点白色），去掉后灰色生效。
    # per-track/per-domain 文件经 track_id/path_prefix 过滤后只有 1 个 track，无需分组。
    prod_ids: list[str] = []
    design_ids: list[str] = []
    node_by_id: dict[int, dict] = {n["id"]: n for n in nodes}
    for track in tracks:
        tid = track["id"]
        track_layers = [l for l in layers if l["track"] == tid]
        for layer in track_layers:
            lid = layer["id"]
            safe_lid = lid.replace("-", "_")
            node_id = f"L{safe_lid}"
            # 四要素标签（§4.3）：①成熟度 ②双语名(含层ID) ③大白话(desc) ④文件
            lines.append(f'    {node_id}["{_layer_label_4el(layer)}"]')
            if layer.get("maturity") == "production":
                prod_ids.append(node_id)
            else:
                design_ids.append(node_id)
            if not skeleton_only:
                layer_nodes = [n for n in nodes if n["layer_id"] == lid]
                for n in layer_nodes:
                    nid = f'N{n["id"]}'
                    # 四要素标签（§4.3）：①成熟度 ②双语名 ③大白话 ④文件路径
                    lines.append(f'    {nid}["{_node_label_4el(n)}"]')
                    lines.append(f'    {node_id} --- {nid}')  # 层-节点附着边（无箭头）
                    if n.get("maturity") == "production":
                        prod_ids.append(nid)
                    else:
                        design_ids.append(nid)

    # 层间边（triggering，按 layer 顺序）——箭头按两端成熟度（§4.5）
    layer_ids = [l["id"] for l in layers]
    layer_mat = {l["id"]: l.get("maturity") for l in layers}
    for i in range(len(layer_ids) - 1):
        from_lid = layer_ids[i].replace("-", "_")
        to_lid = layer_ids[i + 1].replace("-", "_")
        arr = _arrow(layer_mat.get(layer_ids[i]), layer_mat.get(layer_ids[i + 1]))
        lines.append(f'    L{from_lid} {arr}|{_edge_label("triggering")}| L{to_lid}')

    # 节点间边（skeleton_only 模式下跳过——无决策节点）——箭头按两端成熟度（§4.5）
    if not skeleton_only:
        for e in edges:
            fn = node_by_id.get(e["from"], {})
            tn = node_by_id.get(e["to"], {})
            arr = _arrow(fn.get("maturity"), tn.get("maturity"))
            lines.append(f'    N{e["from"]} {arr}|{_edge_label(e["type"])}| N{e["to"]}')

    # classDef 四色 + class 应用（§4.7/§4.8 铁律）
    lines.append(_CLASSDEFS)
    class_apply = _class_apply_lines(prod_ids, design_ids)
    if class_apply:
        lines.append(class_apply)

    return "\n".join(lines) + "\n", len(tracks), len(layers), len(edges)


def _gen_layers_mmd(tracks: list[dict], layers: list[dict]) -> str:
    """生成层级详情图：L0-L6 架构层卡片 + 频率/成熟度/状态 + 流向箭头。

    只渲染 L0-L6 架构层（约 10 个节点），过滤 decision_layers 表中的模块级/
    基础设施级条目（MOD-*/CFG-*/INFRA-*/SH-*/SYS-*）——这些详情已在 01-19
    per-track/per-domain 文件覆盖。全量渲染（~660 节点）会导致 mermaid 渲染失败。

    用户实测确认（2026-07-30）：subgraph 内的节点使用 secondaryColor 而非
    primaryColor，导致 %%{init}%% 设的 primaryColor 不生效（节点白色）。
    去掉 subgraph 后 primaryColor 生效（节点灰色）。布局用 TD 竖向（方案 L）。
    """
    layers = [l for l in layers if _ARCH_LAYER_RE.match(l["id"])]
    lines = [_MERMAID_INIT, "flowchart TD"]

    prod_ids: list[str] = []
    design_ids: list[str] = []
    for layer in layers:
        lid = layer["id"].replace("-", "_")
        node_id = f"L{lid}"
        # 四要素标签（§4.3），蓝图/代码/频率详情在同文件 Layer 清单表
        lines.append(f'    {node_id}["{_layer_label_4el(layer)}"]')
        if layer.get("maturity") == "production":
            prod_ids.append(node_id)
        else:
            design_ids.append(node_id)

    layer_ids = [l["id"] for l in layers]
    layer_mat = {l["id"]: l.get("maturity") for l in layers}
    for i in range(len(layer_ids) - 1):
        from_lid = layer_ids[i].replace("-", "_")
        to_lid = layer_ids[i + 1].replace("-", "_")
        arr = _arrow(layer_mat.get(layer_ids[i]), layer_mat.get(layer_ids[i + 1]))
        lines.append(f'    L{from_lid} {arr}|{_edge_label("triggering")}| L{to_lid}')

    # 反馈边（L6 → L1/L5，学习闭环）。节点 ID = "L" + layer_id（与上方定义一致）
    if len(layer_ids) >= 6:
        l1 = f"L{layer_ids[1].replace('-', '_')}" if len(layer_ids) > 1 else None
        l5 = f"L{layer_ids[-2].replace('-', '_')}"  # 倒数第 2 = L5
        l6 = f"L{layer_ids[-1].replace('-', '_')}"  # 最后 = L6
        if l1:
            lines.append(f'    {l6} -.->|{_edge_label("feedback")}| {l1}')
        lines.append(f'    {l6} -.->|{_edge_label("feedback")}| {l5}')

    # classDef 四色 + class 应用（§4.7/§4.8）
    lines.append(_CLASSDEFS)
    class_apply = _class_apply_lines(prod_ids, design_ids)
    if class_apply:
        lines.append(class_apply)

    return "\n".join(lines) + "\n"


def _gen_invariants_mmd(invariants: list[dict]) -> str:
    """生成不变量图：6 节点类型 + 5 不变量标注 + 合法/非法连接。

    不使用 subgraph——subgraph 内节点使用 secondaryColor 而非 primaryColor，
    导致 %%{init}%% 设的 primaryColor 不生效（节点白色）。扁平布局保证灰色。
    """
    lines = [_MERMAID_INIT, "flowchart TD"]

    # 6 节点类型为设计态概念，统一 class design；标签四要素化（成熟度+双语名）并预折行/转义
    node_types = [
        ("signal", "信号节点", "Signal"),
        ("portfolio_target", "仓位目标节点", "Portfolio Target"),
        ("risk_check", "风控节点", "Risk Check"),
        ("order", "订单节点", "Order"),
        ("execution", "执行节点", "Execution"),
        ("feedback", "反馈节点", "Feedback"),
    ]
    nt_ids: list[str] = []
    for nt, zh, en in node_types:
        safe = nt.replace("-", "_")
        nid = f"NT_{safe}"
        nt_ids.append(nid)
        label = _sanitize_mermaid_label(_wrap_label_text(f"{_maturity_display('design')} {zh} / {en}"))
        lines.append(f'    {nid}["{label}"]')

    lines.append(f"    NT_signal -->|{_edge_label('portfolio_target')}| NT_portfolio_target")
    lines.append(f"    NT_portfolio_target -->|{_edge_label('risk_check')}| NT_risk_check")
    lines.append(f"    NT_risk_check -->|{_edge_label('approving')}| NT_order")
    lines.append(f"    NT_order -->|{_edge_label('triggering')}| NT_execution")
    lines.append(f"    NT_execution -.->|{_edge_label('feedback')}| NT_feedback")
    lines.append(f"    NT_feedback -.->|{_edge_label('informing')}| NT_signal")

    lines.append("    NT_signal -.->|禁止| NT_order")
    lines.append("    linkStyle 6 stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5")

    inv_ids: list[str] = []
    for inv in invariants:
        iid = inv["id"]
        safe_iid = iid.replace("-", "_")
        nid = f"INV_{safe_iid}"
        inv_ids.append(nid)
        label = _sanitize_mermaid_label(
            "<br/>".join(_wrap_label_text(p) for p in [iid, inv.get("name", ""), inv.get("name_en", "")] if p)
        )
        lines.append(f'    {nid}(["{label}"])')

    lines.append("    INV_DEC_INV_001 -.- NT_order")
    lines.append("    INV_DEC_INV_002 -.- NT_signal")
    lines.append("    INV_DEC_INV_003 -.- NT_feedback")
    lines.append("    INV_DEC_INV_005 -.- NT_signal")

    # classDef 四色（§4.7）：节点类型/不变量均为设计态概念 → class design
    lines.append(_CLASSDEFS)
    class_apply = _class_apply_lines([], nt_ids + inv_ids)
    if class_apply:
        lines.append(class_apply)

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 文件编号与域索引
# ---------------------------------------------------------------------------


def _track_filename(track: dict) -> str:
    """01_decision_track_<track_id>.md — 序号取自 track['priority']。"""
    seq = track.get("priority") or 0
    safe_tid = track["id"].replace("-", "_")
    return f"{seq:02d}_decision_track_{safe_tid}.md"


def _domain_filename(layer_id: str, domain: str) -> str:
    """NN_decision_<layer_lower>_<domain>.md — NN 由硬编码字母序索引+偏移推得。"""
    if layer_id == _L2A_DOMAIN_LAYER:
        idx = _L2A_DOMAINS_ALPHA.index(domain)
        seq = _L2A_SEQ_OFFSET + idx
    elif layer_id == _L3_DOMAIN_LAYER:
        idx = _L3_DOMAINS_ALPHA.index(domain)
        seq = _L3_SEQ_OFFSET + idx
    else:
        raise ValueError(f"未知 layer_id {layer_id}，仅支持 L2A/L3")
    return f"{seq:02d}_decision_{layer_id.lower()}_{domain}.md"


def _build_domain_index(tracks: list[dict], layers: list[dict], nodes: list[dict]) -> list[dict]:
    """构建 14 个功能域索引（L2A 7 + L3 7）。

    返回 [{track, layer_id, domain, node_count, filename, seq}]，按 seq 升序。
    空域（node_count=0）仍保留以稳定编号。
    """
    track_by_id = {t["id"]: t for t in tracks}
    layer_track = {l["id"]: l["track"] for l in layers}
    index: list[dict] = []
    for domain in _L2A_DOMAINS_ALPHA:
        layer_id = _L2A_DOMAIN_LAYER
        domain_nodes = [n for n in nodes if n["layer_id"] == layer_id and _node_domain(n.get("path", "")) == domain]
        fname = _domain_filename(layer_id, domain)
        seq = _L2A_SEQ_OFFSET + _L2A_DOMAINS_ALPHA.index(domain)
        tid = layer_track.get(layer_id, "")
        index.append({
            "track": track_by_id.get(tid, {"id": tid, "name": tid, "name_en": tid}),
            "layer_id": layer_id, "domain": domain,
            "node_count": len(domain_nodes), "filename": fname, "seq": seq,
        })
    for domain in _L3_DOMAINS_ALPHA:
        layer_id = _L3_DOMAIN_LAYER
        domain_nodes = [n for n in nodes if n["layer_id"] == layer_id and _node_domain(n.get("path", "")) == domain]
        fname = _domain_filename(layer_id, domain)
        seq = _L3_SEQ_OFFSET + _L3_DOMAINS_ALPHA.index(domain)
        tid = layer_track.get(layer_id, "")
        index.append({
            "track": track_by_id.get(tid, {"id": tid, "name": tid, "name_en": tid}),
            "layer_id": layer_id, "domain": domain,
            "node_count": len(domain_nodes), "filename": fname, "seq": seq,
        })
    return index


def _aggregate_cross_domain_edges(
    nodes: list[dict], edges: list[dict], self_domain: str,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """聚合跨域边：返回 (outgoing_agg, incoming_agg, outgoing_detail, incoming_detail)。

    - agg: [{other_domain, count, types:set}]
    - detail: [{from_path, to_path, type, condition}]
    域 = node['path'] 第 2 段；path 不足 2 段的节点跳过并 stderr 警告。
    """
    node_id_to_domain: dict[int, str] = {}
    for n in nodes:
        d = _node_domain(n.get("path", ""))
        if not d:
            print(f"[WARN] 节点 {n.get('id')} path 残缺（{n.get('path')!r}），跳过跨域边聚合", file=sys.stderr)
            continue
        node_id_to_domain[n["id"]] = d

    outgoing_agg_map: dict[str, dict] = {}
    incoming_agg_map: dict[str, dict] = {}
    outgoing_detail: list[dict] = []
    incoming_detail: list[dict] = []

    for e in edges:
        from_d = node_id_to_domain.get(e["from"])
        to_d = node_id_to_domain.get(e["to"])
        if from_d is None or to_d is None:
            continue
        if from_d == self_domain and to_d != self_domain:
            entry = outgoing_agg_map.setdefault(to_d, {"other_domain": to_d, "count": 0, "types": set()})
            entry["count"] += 1
            entry["types"].add(e["type"])
            outgoing_detail.append({"from_path": _node_path(nodes, e["from"]), "to_path": _node_path(nodes, e["to"]), "type": e["type"], "condition": e.get("condition")})
        elif to_d == self_domain and from_d != self_domain:
            entry = incoming_agg_map.setdefault(from_d, {"other_domain": from_d, "count": 0, "types": set()})
            entry["count"] += 1
            entry["types"].add(e["type"])
            incoming_detail.append({"from_path": _node_path(nodes, e["from"]), "to_path": _node_path(nodes, e["to"]), "type": e["type"], "condition": e.get("condition")})

    outgoing_agg = [{"other_domain": v["other_domain"], "count": v["count"], "types": sorted(v["types"])} for v in outgoing_agg_map.values()]
    incoming_agg = [{"other_domain": v["other_domain"], "count": v["count"], "types": sorted(v["types"])} for v in incoming_agg_map.values()]
    return outgoing_agg, incoming_agg, outgoing_detail, incoming_detail


def _node_path(nodes: list[dict], node_id: int) -> str:
    """查 node_id → path（跨域边表格用）。"""
    for n in nodes:
        if n["id"] == node_id:
            return n.get("path", "")
    return ""


def _gen_cross_domain_mermaid(
    self_domain: str, outgoing_agg: list[dict], incoming_agg: list[dict],
) -> str:
    """跨域依赖图：flowchart TD，本域居中，外部域为外围节点，边标计数。

    治本（2026-08-01 模板升级）：对齐 visualization_view_template.md §4.2/§4.3/§4.7。
      ① flowchart LR → flowchart TD（§4.2 铁律：竖排才能看清依赖链路从上层到下层流动）。
      ② SELF/EXT 节点改四要素标签（成熟度+双语名+域职责+跨域标识，§4.3 跨域外部节点）。
      ③ 末尾追加 _CLASSDEFS + class 应用（SELF=design，EXT=external_design）。
    决策流图当前全为设计态，故 SELF/EXT 统一标 design/external_design；未来 production
    节点出现后可按域聚合成熟度细化（已知简化，非阻断）。
    不使用 subgraph——扁平布局保证 primaryColor/状态色生效（§13.3）。
    """
    lines = [_MERMAID_INIT, "flowchart TD"]
    _self_zh = _DOMAIN_NAME_ZH.get(self_domain, self_domain)
    _self_resp = _DOMAIN_RESPONSIBILITY_ZH.get(self_domain, "")
    lines.append(f'    SELF["{_cross_domain_label(self_domain, _self_zh, _self_resp)}"]')
    ext_ids: list[str] = []
    seen: set[str] = set()
    for d in outgoing_agg:
        other = d["other_domain"]
        safe = other.replace("-", "_")
        if other not in seen:
            _other_zh = _DOMAIN_NAME_ZH.get(other, other)
            _other_resp = _DOMAIN_RESPONSIBILITY_ZH.get(other, "")
            lines.append(f'    EXT_{safe}["{_cross_domain_label(other, _other_zh, _other_resp)}"]')
            ext_ids.append(f"EXT_{safe}")
            seen.add(other)
        # 边箭头：SELF=design → 非双 production → 虚线（§4.5）
        lines.append(f'    SELF -.->|出 {d["count"]}| EXT_{safe}')
    for d in incoming_agg:
        other = d["other_domain"]
        safe = other.replace("-", "_")
        if other not in seen:
            _other_zh = _DOMAIN_NAME_ZH.get(other, other)
            _other_resp = _DOMAIN_RESPONSIBILITY_ZH.get(other, "")
            lines.append(f'    EXT_{safe}["{_cross_domain_label(other, _other_zh, _other_resp)}"]')
            ext_ids.append(f"EXT_{safe}")
            seen.add(other)
        lines.append(f'    EXT_{safe} -.->|入 {d["count"]}| SELF')
    # classDef 四色 + class 应用（§4.7/§4.8）：SELF=design，EXT=external_design
    lines.append(_CLASSDEFS)
    class_apply = _class_apply_lines([], ["SELF"], [], ext_ids)
    if class_apply:
        lines.append(class_apply)
    return "\n".join(lines) + "\n"


def _cross_domain_label(domain_en: str, domain_zh: str, responsibility: str) -> str:
    """跨域节点四要素标签：①成熟度(design) ②双语名 ③域职责 ④跨域标识。§4.3 跨域外部节点。

    格式：`(设计态 / design) 域中文 / Domain English<br/>域职责<br/>跨域节点 / cross-domain`。
    每段过 _wrap_label_text 预折行 + _sanitize_mermaid_label 转义。
    """
    parts = [
        f"{_maturity_display('design')} {domain_zh} / {domain_en}",
        responsibility or "（域职责待补）",
        "跨域节点 / cross-domain",
    ]
    wrapped = [_wrap_label_text(p) for p in parts if p]
    return _sanitize_mermaid_label("<br/>".join(wrapped))


def _atomic_write(path: Path, content: str) -> None:
    """原子写入文件（tmp + os.replace）。本地复制自 generate_domain_doc.py L1016-1028，避免跨模块耦合。"""
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def _assert_domain_set_stable(layers: list[dict], nodes: list[dict]) -> None:
    """断言 DB 派生的 L2A/L3 域集合 == 硬编码列表（防 schema drift）。

    不匹配则 exit 3 并打印可操作信息。空 DB（无节点）时跳过断言（允许空库生成空文件）。
    """
    if not nodes:
        return
    l2a_layer = next((l for l in layers if l["id"] == _L2A_DOMAIN_LAYER), None)
    l3_layer = next((l for l in layers if l["id"] == _L3_DOMAIN_LAYER), None)
    db_l2a = {d for d in (_node_domain(n.get("path", "")) for n in nodes if n["layer_id"] == _L2A_DOMAIN_LAYER) if d} if l2a_layer else set()
    db_l3 = {d for d in (_node_domain(n.get("path", "")) for n in nodes if n["layer_id"] == _L3_DOMAIN_LAYER) if d} if l3_layer else set()
    expected_l2a = set(_L2A_DOMAINS_ALPHA)
    expected_l3 = set(_L3_DOMAINS_ALPHA)
    drift_l2a = db_l2a - expected_l2a
    drift_l3 = db_l3 - expected_l3
    if drift_l2a or drift_l3:
        msg = (
            f"[ERROR] decisiongraph 域集合漂移（schema drift）。\n"
            f"  L2A 新增域（未在 _L2A_DOMAINS_ALPHA）: {sorted(drift_l2a)}\n"
            f"  L3 新增域（未在 _L3_DOMAINS_ALPHA）: {sorted(drift_l3)}\n"
            f"  请更新 generate_decision_diagram.py 的 _L2A_DOMAINS_ALPHA / _L3_DOMAINS_ALPHA 后重跑。"
        )
        print(msg, file=sys.stderr)
        sys.exit(3)


# ---------------------------------------------------------------------------
# 文件构建函数
# ---------------------------------------------------------------------------


def _md_header(
    title: str, breadcrumb: str, md_stem: str | None = None,
    with_html_link: bool = True, doc_title: str | None = None,
) -> list[str]:
    """统一的文件头部（frontmatter + 标题 + 真源 + 生成时间 + HTML链接）。

    治本（2026-08-01 模板升级）：对齐 visualization_view_template.md §3.1/§14。
      - md_stem 提供（MD 文件名去 .md）时输出 frontmatter（§3.1 铁律）。
      - with_html_link=True 时在导航行后输出 HTML 跳转链接（§14 绝对 http:// 链接）。
        纯导航/无 mermaid 文件（index、空 track）传 False 跳过（链接指向的 HTML 不会生成）。
    """
    lines: list[str] = []
    if md_stem is not None:
        lines += [
            "---",
            "doc_type: architecture_view",
            f"title: {doc_title or title}",
            'version: "1.0"',
            "status: active",
            f"date: {_git_commit_timestamp()[:10]}",
            "owner: auto-generator",
            "ttl: permanent",
            "---",
            "",
        ]
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> 生成时间: {_git_commit_timestamp()}")
    lines.append("> 真源: `architecture_model/domain/decision_graph_model.yaml` → PostgreSQL `decision_*` 表（TRAE-061）")
    lines.append(f"> 数据库: {DB_DISPLAY_NAME}")
    lines.append(f"> 导航: [返回主索引 decision_index.md](decision_index.md) | {breadcrumb}")
    if md_stem is not None and with_html_link:
        lines.append("")
        lines.append(_html_link_line(md_stem))
    lines.append("")
    return lines


def _layer_table(layers: list[dict]) -> list[str]:
    """Layer 清单表（表头与枚举值中英对照）。"""
    lines = [
        "| layer_id / 层ID | 名称 / name | 英文名 / name_en | 所属轨 / track | 蓝图(module_id) | 蓝图名 / bp | 代码引用 / ref | 功能简述 / desc | 决策频率 / freq | maturity / 成熟度 | build_status / 构建状态 |",
        "|----------|------|--------|--------|-----------------|--------------|----------|----------|----------|--------|--------------|",
    ]
    for l in layers:
        mid = l.get("module_id") or "-"
        bp_name = l.get("blueprint_name") or "-"
        scr = l.get("source_code_ref") or "-"
        desc = (l.get("desc") or "").strip().replace("\n", " ").replace("|", "\\|") or "-"
        lines.append(
            f"| {l['id']} | {l['name']} | {l['name_en']} | {l['track']} | "
            f"{mid} | {bp_name} | {scr} | {desc} | "
            f"{l['freq'] or '-'} | {_bilingual(l['maturity'], _MATURITY_ZH)} | {_bilingual(l['build'], _BUILD_STATUS_ZH)} |"
        )
    return lines


def _node_table(nodes: list[dict]) -> list[str]:
    """Node 清单表（表头与枚举值均中英对照）。"""
    if not nodes:
        return ["> （无节点）"]
    lines = [
        "| node_id / 节点ID | layer / 层 | type / 类型 | name / 名称 | path / 路径 | module_id / 模块 | 代码引用 / ref | maturity / 成熟度 | build_status / 构建状态 |",
        "|---------|-------|------|------|------|-----------|----------|--------|--------------|",
    ]
    for n in nodes:
        nscr = n.get("source_code_ref") or "-"
        lines.append(
            f"| {n['id']} | {n['layer_id']} | {_bilingual(n['type'], _NODE_TYPE_ZH)} | {n['name']} | "
            f"{n['path']} | {n['module_id'] or '-'} | {nscr} | {_bilingual(n.get('maturity'), _MATURITY_ZH)} | {_bilingual(n['build'], _BUILD_STATUS_ZH)} |"
        )
    return lines


def _edge_table(edges: list[dict]) -> list[str]:
    """Edge 清单表（表头与 type 值中英对照）。"""
    if not edges:
        return ["> （无决策因果边）"]
    lines = [
        "| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 | track / 轨 |",
        "|---------|-------|-----|------|-----------|-------|",
    ]
    for e in edges:
        lines.append(
            f"| {e['id']} | {e['from']} | {e['to']} | {_bilingual(e['type'], _EDGE_TYPE_ZH)} | "
            f"{e['condition'] or '-'} | {e['track'] or '-'} |"
        )
    return lines


def _filter_track_data(
    tid: str, layers: list[dict], nodes: list[dict], edges: list[dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """过滤本轨的 Layer/Node/Edge + 跨轨边（Extract Method 降低 _gen_track_file_md 复杂度）。"""
    track_layers = [l for l in layers if l["track"] == tid]
    track_layer_ids = {l["id"] for l in track_layers}
    track_nodes = [n for n in nodes if n["layer_id"] in track_layer_ids]
    track_node_ids = {n["id"] for n in track_nodes}
    track_edges = [e for e in edges if e["from"] in track_node_ids and e["to"] in track_node_ids]
    cross_track_edges = [e for e in edges if (e["from"] in track_node_ids) ^ (e["to"] in track_node_ids)]
    return track_layers, track_nodes, track_edges, cross_track_edges


def _emit_skeleton_view(
    title: str, hint: str,
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
    tid: str, *, production_only: bool = False, design_only: bool = False,
) -> list[str]:
    """输出单个 Layer 骨架视图（带 `###` 小标题；空层集用占位说明，避免空 mermaid 块）。

    治本（2026-08-01 模板升级）：三视图铁律（§3.2）——全景/运营态/设计态各一图。
    skeleton_only=True 仅画 Layer 节点 + 层间边（决策节点详情在功能域文件），避免大轨
    数百节点撑爆单文件。空视图（l_count=0，如全 design 时运营态图）输出占位说明。
    """
    out = [f"### {title}", "", f"> {hint}", ""]
    mmd, _, l_count, _ = _gen_overview_mmd(
        tracks, layers, nodes, edges,
        production_only=production_only, design_only=design_only,
        track_id=tid, skeleton_only=True,
    )
    if l_count == 0:
        out += ["> （无模块 / No modules）", ""]
    else:
        out += ["```mermaid", mmd.rstrip("\n"), "```", ""]
    return out


def _gen_track_views_section(
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict], tid: str,
) -> list[str]:
    """生成 Layer 骨架三视图 + 统计表（概览模式，不画决策节点；Extract Method 降低复杂度）。

    Track 文件改为「概览+导航」角色：仅画 Layer 节点 + 层间边，决策节点详情在各
    功能域文件（L2A/L3）中查看。避免 model_driven 等大轨重复展示数百节点导致文件过长。

    治本（2026-08-01 模板升级）：单骨架图 → 严格三视图（全景/运营态/设计态，§3.2 铁律），
    为未来 production 节点出现后运营态图自动有内容做准备（一次到位，避免反复改造）。

    无决策节点的 track（如 placeholder/human_override/emergency）不画骨架图——
    骨架图是为决策节点提供 Layer 上下文，无节点时画图无意义（placeholder 轨有 645 个
    占位 Layer 但 0 决策节点，画图会产生无用的巨型 mermaid）。
    """
    track_layers, track_nodes, track_edges, cross_track_edges = _filter_track_data(tid, layers, nodes, edges)
    prod_layers = [l for l in track_layers if l.get("maturity") == "production"]
    design_layers = [l for l in track_layers if l.get("maturity") == "design"]

    lines = [
        "## 统计", "",
        "| Layer 数 | 决策节点数 | 域内边数 | 跨轨边数 |",
        "|----------|-----------|----------|----------|",
        f"| {len(track_layers)} | {len(track_nodes)} | {len(track_edges)} | {len(cross_track_edges)} |",
        "",
        "## Layer 骨架图（三视图）",
        "",
    ]

    if not track_nodes:
        # 无决策节点的 track 不画骨架图（骨架图是为决策节点提供上下文，无节点时无意义）
        lines += ["> 本轨无决策节点，骨架图省略。Layer 清单见下方表格。", ""]
        return lines

    # 图例说明（§3.1 铁律：首个 mermaid 视图前放一次）
    lines += [_LEGEND_MD, ""]
    # 三视图（§3.2 铁律：全景图 → 运营态的图 → 设计态的图，顺序固定）
    lines += _emit_skeleton_view(
        "全景图（全部 Layer，颜色区分运营态/设计态）",
        f"展示本轨全部 {len(track_layers)} 个 Layer 骨架（决策节点附着上下文），决策节点详情见各功能域文件。",
        tracks, layers, nodes, edges, tid,
    )
    lines += _emit_skeleton_view(
        "运营态的图（仅 design_maturity=production 的 Layer）",
        f"仅展示已上线运行的 Layer 骨架（共 {len(prod_layers)} 个）。",
        tracks, layers, nodes, edges, tid, production_only=True,
    )
    lines += _emit_skeleton_view(
        "设计态的图（仅 design_maturity=design 的 Layer）",
        f"仅展示蓝图阶段、代码未写的设计态 Layer 骨架（共 {len(design_layers)} 个）。",
        tracks, layers, nodes, edges, tid, design_only=True,
    )
    return lines


def _gen_track_file_md(
    track: dict, tracks: list[dict], layers: list[dict],
    nodes: list[dict], edges: list[dict],
    domain_index: list[dict],
) -> str:
    """Per-Track 文件：Layer 骨架图 + 统计 + 功能域链接 + Layer 清单 + 跨轨边（概览+导航模式）。

    决策节点详情不在此文件展示（避免大轨数百节点导致文件过长），改由各功能域文件
    （L2A/L3）承载。Track 文件聚焦：骨架概览 + 功能域导航 + Layer/跨轨边清单。
    """
    tid = track["id"]
    track_layers, track_nodes, track_edges, cross_track_edges = _filter_track_data(tid, layers, nodes, edges)

    _track_fname = _track_filename(track)
    lines = _md_header(
        f"决策流图 · {track['name']}（{track['name_en']}）",
        f"Track {track.get('priority', '-')}",
        md_stem=_track_fname[:-3],
        # 无决策节点的 track 0 mermaid → 不输出 HTML 链接（指向的 HTML 不会生成）
        with_html_link=bool(track_nodes),
        doc_title=f"决策流图 {track['name']}（{track['name_en']}）",
    )
    lines += [
        f"**track_id**: `{tid}` | **优先级**: {track.get('priority', '-')} | **激活条件**: {track.get('activation') or '-'}",
        "",
        track.get("desc") or "",
        "",
    ]
    lines += _gen_track_views_section(tracks, layers, nodes, edges, tid)

    # 功能域文件链接（突出导航作用，紧跟骨架图之后）
    track_domains = [d for d in domain_index if d["track"]["id"] == tid]
    if track_domains:
        lines += ["## 功能域文件（L2A/L3 拆分）", ""]
        lines += ["| 序号 | 层 | 功能域 | Node 数 | 文档 |", "|------|------|--------|---------|------|"]
        for d in track_domains:
            lines.append(f"| {d['seq']:02d} | {d['layer_id']} | {d['domain']} | {d['node_count']} | [📄 {d['filename']}]({d['filename']}) |")
        lines += [""]
    else:
        lines += ["## 功能域文件（L2A/L3 拆分）", "", "> （本轨无功能域文件——决策节点未按域拆分）", ""]

    lines += ["## Layer 清单", ""] + _layer_table(track_layers) + [""]

    lines += ["## 跨轨边", ""]
    if cross_track_edges:
        lines += [
            "| edge_id / 边ID | from / 起点 | to / 终点 | type / 类型 | condition / 条件 |",
            "|---------|-------|-----|------|-----------|",
        ]
        for e in cross_track_edges:
            lines.append(f"| {e['id']} | {e['from']} | {e['to']} | {_bilingual(e['type'], _EDGE_TYPE_ZH)} | {e['condition'] or '-'} |")
    else:
        lines += ["> （无跨轨边）"]
    lines += [""]

    return "\n".join(lines) + "\n"


def _emit_domain_view(
    title: str, hint: str, view_nodes: list[dict],
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
    *, track_id: str, path_prefix: str,
    production_only: bool = False, design_only: bool = False,
) -> list[str]:
    """输出单个域内依赖视图（带 `###` 小标题；空节点集用占位说明，避免空 mermaid 块）。§3.2。

    治本（2026-08-01 模板升级）：决策节点全 design 时运营态视图输出占位说明（不输出空
    mermaid），未来 production 节点出现后自动有内容。空视图判定基于 view_nodes（域内
    决策节点数），非 layer 数——避免「有 production layer 但本域无 production 节点」时
    误画出空 layer 卡片。
    """
    out = [f"### {title}", "", f"> {hint}", ""]
    if not view_nodes:
        out += ["> （无模块 / No modules）", ""]
        return out
    mmd, _, l_count, e_count = _gen_overview_mmd(
        tracks, layers, nodes, edges,
        production_only=production_only, design_only=design_only,
        track_id=track_id, path_prefix=path_prefix,
    )
    out += [f"> 共 {l_count} 层，{e_count} 边。", "", "```mermaid", mmd.rstrip("\n"), "```", ""]
    return out


def _gen_domain_file_md(
    track: dict, layer_id: str, domain: str,
    tracks: list[dict], layers: list[dict], nodes: list[dict], edges: list[dict],
) -> str:
    """Per-domain 文件：三视图 mermaid + 本域 Node 表 + 出/入边表 + 跨域 mermaid。

    治本（2026-08-01 模板升级）：单「设计态全景图」→ 严格三视图（全景/运营态/设计态，
    §3.2 铁律）+ 图例说明 + frontmatter + HTML 跳转链接。运营态当前 0 production 节点
    → 占位说明；未来 production 节点出现后自动有内容（一次到位，避免反复改造）。
    """
    domain_nodes = [n for n in nodes if n["layer_id"] == layer_id and _node_domain(n.get("path", "")) == domain]
    domain_node_ids = {n["id"] for n in domain_nodes}
    domain_edges = [e for e in edges if e["from"] in domain_node_ids and e["to"] in domain_node_ids]
    outgoing_agg, incoming_agg, outgoing_detail, incoming_detail = _aggregate_cross_domain_edges(nodes, edges, domain)

    prod_domain_nodes = [n for n in domain_nodes if n.get("maturity") == "production"]
    design_domain_nodes = [n for n in domain_nodes if n.get("maturity") == "design"]

    _domain_zh = _DOMAIN_NAME_ZH.get(domain, domain)
    _domain_fname = _domain_filename(layer_id, domain)
    lines = _md_header(
        f"Decision Flow · {layer_id} Functional Domain {domain}（{_domain_zh}）",
        f"{track['name']} → {layer_id} → {domain}",
        md_stem=_domain_fname[:-3],
        # 域无决策节点时 0 mermaid（含跨域）→ 不输出 HTML 链接
        with_html_link=bool(domain_nodes),
        doc_title=f"{domain}（{_domain_zh}）决策流图",
    )
    _responsibility = _DOMAIN_RESPONSIBILITY_ZH.get(domain, "")
    lines += [
        f"**所属轨**: {track['name']}（`{track['id']}`） | **所属层**: {layer_id} | **功能域**: `{domain}`（{_domain_zh}）",
        "",
    ]
    if _responsibility:
        lines += [f"> **域职责 / Responsibility**: {_responsibility}", ""]
    lines += [
        "## 统计",
        "",
        f"- 决策节点数（全部）: {len(domain_nodes)}",
        f"- 运营态节点数（production）: {len(prod_domain_nodes)}",
        f"- 设计态节点数（design）: {len(design_domain_nodes)}",
        f"- 域内边数: {len(domain_edges)}",
        f"- 跨域出边: {sum(d['count'] for d in outgoing_agg)}（{len(outgoing_agg)} 个外部域）",
        f"- 跨域入边: {sum(d['count'] for d in incoming_agg)}（{len(incoming_agg)} 个外部域）",
        "",
        "## 域内依赖图 / Internal Dependency Diagram",
        "",
        _LEGEND_MD,
        "",
    ]
    # 三视图（§3.2 铁律：全景图 → 运营态的图 → 设计态的图，顺序固定）
    lines += _emit_domain_view(
        "全景图（全部模块，颜色区分运营态/设计态）",
        f"展示全部 {len(domain_nodes)} 个决策节点（运营态 {len(prod_domain_nodes)} + 设计态 {len(design_domain_nodes)}），含跨域依赖外部节点。",
        domain_nodes, tracks, layers, nodes, edges,
        track_id=track["id"], path_prefix=domain,
    )
    lines += _emit_domain_view(
        "运营态的图（仅 design_maturity=production 的模块和域内依赖）",
        f"仅展示已上线运行的决策节点（共 {len(prod_domain_nodes)} 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。",
        prod_domain_nodes, tracks, layers, nodes, edges,
        track_id=track["id"], path_prefix=domain, production_only=True,
    )
    lines += _emit_domain_view(
        "设计态的图（仅 design_maturity=design 的模块和域内依赖）",
        f"仅展示蓝图阶段、代码未写的设计态决策节点（共 {len(design_domain_nodes)} 个），不含跨域外部节点。",
        design_domain_nodes, tracks, layers, nodes, edges,
        track_id=track["id"], path_prefix=domain, design_only=True,
    )

    lines += ["## Node 清单", ""]
    lines += _node_table(domain_nodes) + [""]
    lines += ["## Edge 清单（域内）", ""] + _edge_table(domain_edges) + [""]

    # 跨域出边
    lines += ["## 跨域出边（Depends On）", ""]
    if outgoing_detail:
        lines += ["| # | 本域节点 / from | → | 外部域-目标节点 / to | type / 类型 |", "|:--:|---------|:--:|---------|---------|"]
        for i, d in enumerate(outgoing_detail, 1):
            lines.append(f"| {i} | {d['from_path']} | → | {d['to_path']} | {_bilingual(d['type'], _EDGE_TYPE_ZH)} |")
    else:
        lines += ["> （无跨域出边）"]
    lines += [""]

    # 跨域入边
    lines += ["## 跨域入边（Depended By）", ""]
    if incoming_detail:
        lines += ["| # | 外部域-源节点 / from | → | 本域节点 / to | type / 类型 |", "|:--:|---------|:--:|---------|---------|"]
        for i, d in enumerate(incoming_detail, 1):
            lines.append(f"| {i} | {d['from_path']} | → | {d['to_path']} | {_bilingual(d['type'], _EDGE_TYPE_ZH)} |")
    else:
        lines += ["> （无跨域入边）"]
    lines += [""]

    # 跨域 mermaid
    lines += ["## 跨域依赖图（Cross-Domain Dependency Graph）", ""]
    if outgoing_agg or incoming_agg:
        _ext_count = len(outgoing_agg) + len(incoming_agg)
        lines += [
            f"> 本域与 {_ext_count} 个外部域直接连接 / This domain directly connects to {_ext_count} external domain(s).",
            "",
            "```mermaid",
            _gen_cross_domain_mermaid(domain, outgoing_agg, incoming_agg).rstrip("\n"),
            "```",
        ]
    else:
        lines += ["> （无跨域依赖）"]
    lines += [""]

    return "\n".join(lines) + "\n"


def _gen_layers_file_md(tracks: list[dict], layers: list[dict]) -> str:
    """层级详情图独立文件。"""
    mmd = _gen_layers_mmd(tracks, layers)
    lines = _md_header(
        "决策流图 · 层级详情图", "辅助图",
        md_stem=_LAYERS_FILE_NAME[:-3], doc_title="决策流图 层级详情图",
    )
    lines += [
        "L0-L6 层级卡片 + 频率/成熟度/状态 + 流向箭头 + 学习闭环反馈边。",
        "",
        _LEGEND_MD,
        "",
        "```mermaid",
        mmd.rstrip("\n"),
        "```",
        "",
    ]
    return "\n".join(lines) + "\n"


def _gen_invariants_file_md(invariants: list[dict]) -> str:
    """不变量图独立文件。"""
    mmd = _gen_invariants_mmd(invariants)
    lines = _md_header(
        "决策流图 · 不变量图", "辅助图",
        md_stem=_INVARIANTS_FILE_NAME[:-3], doc_title="决策流图 不变量图",
    )
    lines += [
        "6 节点类型 + 5 承重墙不变量 + 合法/非法连接标注。",
        "",
        _LEGEND_MD,
        "",
        "```mermaid",
        mmd.rstrip("\n"),
        "```",
        "",
    ]
    return "\n".join(lines) + "\n"


def _gen_index_md(
    tracks: list[dict],
    layers: list[dict],
    nodes: list[dict],
    edges: list[dict],
    invariants: list[dict] | None = None,
    domain_index: list[dict] | None = None,
) -> str:
    """生成主索引（纯导航，0 个 mermaid）。

    保留概述 + 统计 + Track/L2A/L3 导航表 + 辅助图链接 + 旧锚点重定向。
    """
    invariants = invariants or []
    domain_index = domain_index or []

    prod_layers = [l for l in layers if l.get("maturity") == "production"]
    design_layers = [l for l in layers if l.get("maturity") == "design"]
    prod_nodes = [n for n in nodes if n.get("maturity") == "production"]
    design_nodes = [n for n in nodes if n.get("maturity") == "design"]

    # frontmatter（§3.1）；with_html_link=False：主索引纯导航 0 mermaid，不输出 HTML 链接。
    lines = _md_header(
        "决策流图（decisiongraph）索引", "主索引",
        md_stem="decision_index", with_html_link=False,
        doc_title="决策流图（decisiongraph）索引",
    )
    lines += [
        # 大白话解释决策流图（治本 2026-07-31）：让入口索引对非架构读者也友好
        *_DECISION_PLAIN_LANGUAGE_INTRO.splitlines(),
        "",
        "## 概述",
        "",
        "决策流图（decisiongraph）是与依赖图（depgraph）、数据流图（dataflowgraph）正交的第三维度全景图。",
        '- depgraph 表达"谁依赖谁"（模块依赖，静态）',
        '- dataflowgraph 表达"数据从哪流到哪"（数据流向，动态）',
        '- decisiongraph 表达"决策如何产生"（决策流，动态）',
        "- 三图通过 `module_id` 关联：决策节点 → 实现模块（depgraph）→ 数据流作业（dataflowgraph）",
        "",
        "> 本索引为纯导航枢纽。各 Track / 功能域 / 辅助图分别独立成文件，避免单文件过大无法阅读。",
        "",
        "## 统计",
        "",
        "| 类型 | 数量 |",
        "|------|------|",
        f"| Track（轨） | {len(tracks)} |",
        f"| Layer（层） | {len(layers)} |",
        f"| Node（节点） | {len(nodes)} |",
        f"| Edge（边） | {len(edges)} |",
        f"| 运营态 Layer（design_maturity=production） | {len(prod_layers)} |",
        f"| 设计态 Layer（design_maturity=design） | {len(design_layers)} |",
        f"| 运营态 Node（design_maturity=production） | {len(prod_nodes)} |",
        f"| 设计态 Node（design_maturity=design） | {len(design_nodes)} |",
        "",
        "> **设计态 vs 运营态**：`design_maturity` 字段区分——`design`=蓝图规划（代码未写），`production`=实际代码已实现稳定运行。对标 depgraph 的设计态/运营态机制。",
        "",
        "## Track 导航（按优先级）",
        "",
        "| 序号 | track_id | 名称 | 优先级 | Layer 数 | Node 数 | [📄 文档](.) |",
        "|------|----------|------|--------|----------|---------|------|",
    ]
    for t in tracks:
        t_layers = [l for l in layers if l["track"] == t["id"]]
        t_layer_ids = {l["id"] for l in t_layers}
        t_nodes = [n for n in nodes if n["layer_id"] in t_layer_ids]
        fname = _track_filename(t)
        lines.append(
            f"| {t.get('priority', 0):02d} | {t['id']} | {t['name']} | {t.get('priority', '-')} | "
            f"{len(t_layers)} | {len(t_nodes)} | [📄 {fname}]({fname}) |"
        )

    # L2A 域导航
    l2a_entries = [d for d in domain_index if d["layer_id"] == _L2A_DOMAIN_LAYER]
    lines += [
        "",
        f"## L2A 信号层 · 功能域导航（{len(l2a_entries)} 域）",
        "",
        "| 序号 | 功能域 | Node 数 | [📄 文档](.) |",
        "|------|--------|---------|------|",
    ]
    for d in l2a_entries:
        lines.append(f"| {d['seq']:02d} | {d['domain']} | {d['node_count']} | [📄 {d['filename']}]({d['filename']}) |")

    # L3 域导航
    l3_entries = [d for d in domain_index if d["layer_id"] == _L3_DOMAIN_LAYER]
    lines += [
        "",
        f"## L3 策略组合层 · 功能域导航（{len(l3_entries)} 域）",
        "",
        "| 序号 | 功能域 | Node 数 | [📄 文档](.) |",
        "|------|--------|---------|------|",
    ]
    for d in l3_entries:
        lines.append(f"| {d['seq']:02d} | {d['domain']} | {d['node_count']} | [📄 {d['filename']}]({d['filename']}) |")

    # 辅助图
    lines += [
        "",
        "## 辅助图",
        "",
        f"- [📄 {_LAYERS_FILE_NAME}]({_LAYERS_FILE_NAME}) — 层级详情图（L0-L6 卡片 + 流向）",
        f"- [📄 {_INVARIANTS_FILE_NAME}]({_INVARIANTS_FILE_NAME}) — 不变量图（6 节点类型 + 5 承重墙不变量）",
        "",
        "## 旧锚点重定向",
        "",
        "原单文件 `decision_index.md` 的各 section 已拆分到对应文件，外部 wiki 链接请按下方映射更新：",
        "",
        "- `#全景图` / `#运营态全景图` / `#设计态全景图` → 见各 [Track 文件](#track-导航按优先级)",
        "- `#层级详情图` → [20_decision_layers.md](20_decision_layers.md)",
        "- `#不变量图` → [21_decision_invariants.md](21_decision_invariants.md)",
        "- `#track-清单` → 上方 Track 导航表",
        "- `#layer-清单` → 各 Track 文件内的 Layer 清单 section",
        "- `#node-清单` → 各 Track / 功能域文件内的 Node 清单 section",
        "- `#edge-清单` → 各 Track 文件内的 Edge 清单 section",
        "",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="从 decisiongraph (PostgreSQL) 生成决策流图（Mermaid + Markdown，22 文件）",
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    args = parser.parse_args()

    try:
        conn = get_decisiongraph_pg_connection()
    except Exception as e:
        print(f"[ERROR] decisiongraph 连接失败: {e}", file=sys.stderr)
        return EXIT_FINDINGS
    try:
        tracks, layers, nodes, edges = _fetch_decision_data(conn)
        bp_map = _resolve_blueprint_names(conn, layers)
        for l in layers:
            mid = l.get("module_id")
            if mid and mid in bp_map:
                l["blueprint_name"] = bp_map[mid]
    finally:
        conn.close()

    if not tracks and not layers:
        print("[WARN] decisiongraph 表为空，请先运行 generate_decision_graph.py 同步 decision_graph_model.yaml")
        return EXIT_ERROR
    invariants = _load_invariants()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 写文件前断言域集合稳定（失败 exit 3，不留半成品）
    _assert_domain_set_stable(layers, nodes)

    domain_index = _build_domain_index(tracks, layers, nodes)
    expected_basenames: set[str] = set()
    html_count = 0  # 联动生成的 HTML 文件数

    def _write_md(rel_name: str, content: str) -> None:
        """写 MD + 联动生成可缩放 HTML（无 mermaid 自动跳过）。对齐 generate_domain_doc.py。"""
        nonlocal html_count
        path = out_dir / rel_name
        _atomic_write(path, content)
        html_path = emit_zoomable_html(path, content)
        if html_path:
            html_count += 1

    # 1. 主索引（纯导航，0 mermaid → 不生成 HTML）
    index_md = _gen_index_md(tracks, layers, nodes, edges, invariants, domain_index)
    _write_md("decision_index.md", index_md)

    # 2. Per-Track 文件（01-05）
    for track in tracks:
        fname = _track_filename(track)
        expected_basenames.add(fname)
        _write_md(fname, _gen_track_file_md(track, tracks, layers, nodes, edges, domain_index))

    # 3. Per-domain 文件（06-19）
    for entry in domain_index:
        expected_basenames.add(entry["filename"])
        _write_md(
            entry["filename"],
            _gen_domain_file_md(
                entry["track"], entry["layer_id"], entry["domain"],
                tracks, layers, nodes, edges,
            ),
        )

    # 4. 辅助图（20, 21）
    _write_md(_LAYERS_FILE_NAME, _gen_layers_file_md(tracks, layers))
    _write_md(_INVARIANTS_FILE_NAME, _gen_invariants_file_md(invariants))
    expected_basenames.add(_LAYERS_FILE_NAME)
    expected_basenames.add(_INVARIANTS_FILE_NAME)

    # 5. 清理陈旧 MD 文件
    deleted = cleanup_stale_files(out_dir, expected_basenames, _STALE_FILE_REGEX)
    if deleted:
        print(f"[CLEANUP] 删除 {len(deleted)} 个残留 MD: {deleted}")
    # 6. 清理陈旧 HTML（_zoomable_html/ 子文件夹，域/轨被删时联动 HTML 不残留）
    expected_html = {name[:-3] + ".html" for name in expected_basenames}
    expected_html.add("decision_index.html")  # index 无 mermaid 不会生成，留作占位避免误删
    deleted_html = cleanup_stale_files(
        out_dir / HTML_SUBDIR, expected_html, r"^[a-z0-9_]+\.html$"
    )
    if deleted_html:
        print(f"[CLEANUP] 删除 {len(deleted_html)} 个残留 HTML: {deleted_html}")

    total_files = len(expected_basenames) + 1  # +1 for decision_index.md
    print(
        f"[OK] 生成 {total_files} MD (1 index + {len(tracks)} tracks + "
        f"{len(domain_index)} domains + 2 aux) + {html_count} HTML 到 {out_dir}"
    )
    return EXIT_PASS


# ── Stage 4 公共 API 别名（for testing, thin wrappers） ──
# 模块级私有函数/常量的公共别名，消除测试对 _mod._xxx 的私有访问。
build_status_color = _build_status_color
load_invariants = _load_invariants
gen_overview_mmd = _gen_overview_mmd
gen_layers_mmd = _gen_layers_mmd
gen_invariants_mmd = _gen_invariants_mmd
gen_index_md = _gen_index_md
resolve_blueprint_names = _resolve_blueprint_names
truncate = _truncate
maturity_tag = _maturity_tag
filter_overview_inputs = _filter_overview_inputs
gen_track_file_md = _gen_track_file_md
gen_domain_file_md = _gen_domain_file_md
gen_layers_file_md = _gen_layers_file_md
gen_invariants_file_md = _gen_invariants_file_md
track_filename = _track_filename
domain_filename = _domain_filename
build_domain_index = _build_domain_index
node_domain = _node_domain
fetch_decision_data = _fetch_decision_data
STALE_FILE_REGEX = _STALE_FILE_REGEX
YAML_PATH = _YAML_PATH
# 模板升级新增辅助函数别名（供测试断言四要素/图例/跨域标签/双语拆分）
node_label_4el = _node_label_4el
layer_label_4el = _layer_label_4el
split_zh_en = _split_zh_en
cross_domain_label = _cross_domain_label
gen_cross_domain_mermaid = _gen_cross_domain_mermaid
wrap_label_text = _wrap_label_text
CLASSDEFS = _CLASSDEFS
LEGEND_MD = _LEGEND_MD

if __name__ == "__main__":
    sys.exit(main())
