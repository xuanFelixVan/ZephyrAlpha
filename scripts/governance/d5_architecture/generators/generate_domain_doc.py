# [BLUEPRINT] MOD-GOV_GENERATE_DOMAIN_DOC
# [MODULE]# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_doc
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""G2+G10 合并：从 depgraph (PostgreSQL) nodes+edges 表生成指定域的 MD 文档

包含：
- 域内依赖图（内嵌 Mermaid，分页显示，节点含成熟度+中英文名+大白话+文件路径）
- 跨域依赖（出边/入边聚合）
- 架构分层视图（ASCII art 分层可视化）
- 依赖关系图（ASCII art 按 dep_type 分组）

治本合并：消除 generate_domain_architecture_diagram.py 的 4 个 DB 查询函数逐字重复 +
修复 arch_diagram 孤儿状态（原 reconciler 不调用它，53 个 _architecture.md 已过时）。
合并后由 GATE-DOMAIN-DOC reconciler 统一维护，ASCII art 也会随 depgraph (PostgreSQL) 变更自动刷新。

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/_working/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_domain_doc
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);输出到02_domain_architecture_docs/
[MODIFY-GUARD] 修改需通过DM200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看02_domain_architecture_docs/{编号}_{domain}.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1;域不存在→exit 2
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# 治本（2026-07-04）：DB_DISPLAY_NAME 前移到 __manifest__ 之前，避免 f-string 求值时 NameError。
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _common import cleanup_stale_files, DB_DISPLAY_NAME  # noqa: E402

__manifest__ = f"""
args: []
description: G2+G10 合并：从 {DB_DISPLAY_NAME} nodes+edges 表生成指定域的 MD 文档
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import ast
import os
import re
from datetime import datetime

import yaml

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, PgConnExecuteWrapper  # 治本 #ARCH-TOOL-HEALTH-V1：PgConnExecuteWrapper 用于类型注解（8 处使用）

from domain_name_mapping import get_domain_name_zh, get_domain_name_zh_strict, get_domain_name_en, get_layer_name_bilingual, get_domain_desc_zh  # noqa: E402
from _shared.module_translation_loader import get_module_translation, get_module_name_bilingual, get_module_desc_bilingual, get_module_plain  # noqa: E402 — 模块级翻译真源（#ARCH-SSOT-GLOSSARY-MERGE-001 补齐模块级缺口）
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # Bug 6 fix: L1370 uses but not imported
from zoomable_html import emit_zoomable_html, HTML_SUBDIR  # noqa: E402 — 可缩放 HTML 联动生成（md→_zoomable_html/ 子文件夹同步，reconciler 刷新 md 即刷新 HTML）

OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "02_domain_architecture_docs"

# 本地 HTTP 文档服务器基址（用于生成可缩放 HTML 的浏览器跳转链接）
# 原理：Trae/VS Code 预览面板对 file:/// 和相对路径链接会在编辑器内打开源码，
# 只有 http:// 链接会交给外部浏览器渲染。因此需要本地起一个 http server 服务仓库根目录：
#   python -m http.server 8765 --bind 127.0.0.1   （在仓库根目录执行）
# 启动脚本：scripts/serve_docs_http.bat（双击即可，gitignore 为 dev-local 工具）。端口变更时同步修改此处。
# 注意：.html 文件本身已 gitignore（dev-local 衍生产物），故链接仅在生成端开发机可用，这是预期行为。
_DOC_HTTP_BASE = "http://localhost:8765"

# 层级排序：编号按此顺序分组分配（build_numbering_map 按 LAYER_ORDER 给域编号）
LAYER_ORDER = ["L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"]  # noqa: gate-vocab  显示排序用，含历史遗留 L1_platform（layer_vocabulary v2.0.0 已移除，保留仅为兼容旧域文档分组）


def _is_ghost(path: str, design_maturity: str = "") -> bool:
    """检查节点路径是否为 ghost（path 非空但磁盘上不存在）。

    第一性原理治本：即使不手动 deprecate，生成器也自动过滤幽灵文件，
    防止架构文档引用已删除的文件。铁律保障：新 AI 不需要知道要跑 deprecate。

    重要例外：设计态节点（design_maturity='design'）代码未写、文件不存在是正常的
    （build_status=planned），不应视为 ghost——否则设计态模块全部被过滤，设计态图永远为空。
    """
    if design_maturity == "design":
        return False
    return bool(path) and not (REPO_ROOT / path).exists()


def _extract_docstring_first_line(path: str) -> str:
    """从 Python 文件提取 docstring 首行作为功能简介。

    用 ast 模块安全解析，非 .py 文件或无 docstring 返回空字符串。
    跳过治理标记首行（[A_module]、[BLUEPRINT]、[MODULE] 等），取第一个有意义行。
    截断到 80 字符。
    """
    if not path or not path.endswith('.py'):
        return ""
    abs_path = REPO_ROOT / path
    if not abs_path.exists():
        return ""
    try:
        content = abs_path.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        if docstring:
            lines = docstring.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 跳过治理标记行（[A_module]、[BLUEPRINT]、[MODULE] 等）
                if line.startswith('[A_') or line.startswith('[BLUEPRINT') or line.startswith('[MODULE'):
                    continue
                return _truncate(line, 80)
            return ""
    except Exception:  # noqa: BLE001 — 单个 Python 文件读取/AST 解析失败（语法错误/编码异常/IO）时返回空简介继续生成文档，尽力而为语义
        pass
    return ""


def _extract_yaml_description(path: str) -> str:
    """从 YAML 文件提取 description 字段作为功能简介（ARCH-052）。

    用于聚合节点展开的 items——门禁 yaml/脚本配置等。
    """
    if not path or not path.endswith(('.yaml', '.yml')):
        return ""
    abs_path = REPO_ROOT / path
    if not abs_path.exists():
        return ""
    try:
        data = yaml.safe_load(abs_path.read_text(encoding='utf-8', errors='replace'))
        if isinstance(data, dict):
            desc = (data.get('description', '') or '').strip()
            if desc:
                # 取第一行，截断到 80 字符
                first_line = desc.split('\n')[0].strip()
                return _truncate(first_line, 80)
    except Exception:  # noqa: BLE001 — 单个 YAML 读取/解析失败（YAMLError/IO）时返回空简介继续生成文档，尽力而为语义
        pass
    return ""


# ---------------------------------------------------------------------------
# 中英文双显映射表 + 节点标签辅助函数（L180-194 修复：视图显示中文功能简介）
# ---------------------------------------------------------------------------

# 成熟度中英文映射（design_maturity 字段值 → 中文/英文双显）
MATURITY_DISPLAY = {
    "production": "生产态 / production",
    "design": "设计态 / design",
    "unknown": "未知 / unknown",
    "": "未知 / unknown",
}

# 依赖类型中英文映射（dep_type 字段值 → 中文/英文双显）
DEP_TYPE_DISPLAY = {
    "import_depends": "导入依赖 / import_depends",
    "test_depends": "测试依赖 / test_depends",
    "contract_depends": "契约依赖 / contract_depends",
    "event_depends": "事件依赖 / event_depends",
    "unknown": "未知 / unknown",
    "": "未知 / unknown",
}


def _maturity_display(maturity: str) -> str:
    """成熟度值转中英文双显。"""
    return MATURITY_DISPLAY.get(maturity, f"{maturity} / {maturity}")


def _dep_type_display(dep_type: str) -> str:
    """依赖类型值转中英文双显。"""
    return DEP_TYPE_DISPLAY.get(dep_type, f"{dep_type} / {dep_type}")


def _dep_types_display(dep_types_str: str) -> str:
    """逗号分隔的 dep_types 字符串转中英文双显（STRING_AGG 产物解析）。"""
    if not dep_types_str:
        return "—"
    parts = [p.strip() for p in dep_types_str.split(",") if p.strip()]
    return ", ".join(_dep_type_display(p) for p in parts) if parts else "—"


def _node_short_name(n: dict) -> str:
    """从节点数据提取短名称（父目录/文件名，便于区分同名文件如 __init__.py）。"""
    path = n.get("path") or ""
    # 优先用 path（结构化路径），取最后两段：父目录/文件名
    if path:
        parts = path.rsplit("/", 2)
        if len(parts) >= 2:
            return f"{parts[-2]}/{parts[-1]}"
        return parts[-1]
    node_name = n.get("node_name") or ""
    if node_name:
        return node_name.rsplit("/", 1)[-1]
    return f"node_{n.get('node_id', '?')}"


def _node_desc_zh(n: dict) -> str:
    """从节点数据提取功能简介（优先 DB description，回退到文件 docstring/yaml description）。

    get_domain_nodes 不 SELECT description 字段（多为空），因此主要依赖
    _extract_docstring_first_line 从 Python 文件 docstring 提取首行——
    与模块清单表格的 desc_display 保持同一真源，避免多真源不一致。
    """
    # 1. 优先使用 DB description 字段（如已 SELECT）
    desc = (n.get("description") or "").strip()
    if desc:
        return _truncate(desc.split("\n")[0].strip(), 50)
    # 2. 回退到 Python 文件 docstring 首行 / YAML description
    path = n.get("path") or ""
    if not path:
        return ""
    doc_desc = _extract_docstring_first_line(path)
    if doc_desc:
        return _truncate(doc_desc, 80)
    if path.endswith(('.yaml', '.yml')):
        yaml_desc = _extract_yaml_description(path)
        if yaml_desc:
            return _truncate(yaml_desc, 80)
    return ""


def _node_bilingual_name(n: dict) -> str:
    """返回节点双语名称（中文在前 / English）。

    优先查模块翻译真源（module_translation_registry.yaml）；
    未登记时回退到 docstring 首行（单语，可能是中文或英文）；
    都无则返回空串。

    Returns:
        ``"中文名 / English"`` / ``"中文名"`` / ``"English"`` / ``""``
    """
    path = n.get("path") or ""
    if path:
        bi = get_module_name_bilingual(path)
        if bi:
            return bi
    # fallback: docstring 首行（单语）
    return _node_desc_zh(n)


def _node_bilingual_desc(n: dict) -> str:
    """返回节点双语功能简介（中文在前 / English）。

    优先查模块翻译真源；未登记时回退到 docstring 首行（单语）；
    都无则返回空串。

    Returns:
        ``"中文简介 / English"`` / ``"中文简介"`` / ``"English"`` / ``""``
    """
    path = n.get("path") or ""
    if path:
        bi = get_module_desc_bilingual(path)
        if bi:
            return bi
    # fallback: docstring 首行（单语）
    return _node_desc_zh(n)


def _wrap_label_text(text: str, max_units: int = 48) -> str:
    """将长节点标签文本按显示宽度预折行（Mermaid 节点内显示用）。

    治本（2026-08-01）：Mermaid 先按标签行数测量节点框宽高，若依赖 HTML 渲染层
    CSS max-width 二次折行，渲染行数 > 测量行数 → 框高不够、文字被上下裁剪。
    必须在生成端用 <br/> 显式预折行，使测量行数 = 渲染行数。

    折行规则：显示宽度（CJK=2/ASCII=1）超 max_units 断行（48 ≈ 24 个汉字）；
    优先在空格/下划线之后、左括号/斜杠之前软断（保持英文词完整），否则硬断。
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


def _node_mermaid_label(n: dict) -> str:
    """生成 Mermaid 节点标签：中文在前（名+简介+受限），英文在后（名+简介），状态最后。

    显示策略（2026-08-01 第四轮治本：中英分排，解决末行裁剪问题）：
    - **中文部分（前面）**：中文名 → 中文简介(大白话) → ⛔受限原因(设计态)
    - **英文部分（后面）**：英文名 → 英文简介
    - **末尾**：文件路径 → 成熟度状态（颜色已区分运营态/设计态，放最后不碍阅读）
    - 中文名称：真源 name_zh 优先 → docstring 首行兜底 → 文件名兜底
    - 中文简介：真源 plain_zh 优先 → desc_zh 兜底 → 名称来自真源时用 docstring 兜底
    - 英文名称/简介：真源 name_en/desc_en（可能为空，为空则整段不输出）
    - ⛔ 受限原因：设计态节点 gate_reason 非空时追加（紧跟中文简介，说明"为什么没施工"）
    - 所有行经 _wrap_label_text 预折行（<br/> 显式断行），防 CSS 二次折行致框高不足
    """
    maturity = _maturity_display(n.get("design_maturity") or "unknown")
    short_name = _node_short_name(n)
    path = n.get("path") or ""
    desc = _node_desc_zh(n)
    # 拆分取中英文名和简介（翻译真源独立字段）
    trans = get_module_translation(path) if path else None
    name_zh = (trans.get("name_zh", "") if trans else "").strip()
    name_en = (trans.get("name_en", "") if trans else "").strip()
    desc_zh = (trans.get("desc_zh", "") if trans else "").strip()
    desc_en = (trans.get("desc_en", "") if trans else "").strip()
    plain = get_module_plain(path) if path else ""

    # 中文名称：name_zh > docstring > 文件名
    cn_name = name_zh or desc or short_name
    # 中文简介（多级回退，确保每个节点都有大白话）：
    # 1. plain_zh（真源大白话）——若与 name_zh 完全相同则视为"复述"跳过
    # 2. desc_zh（真源技术简介）——若与 name_zh/cn_name 相同也跳过
    # 3. docstring 首行——若与 cn_name 不同则用作兜底简介
    # 4. 以上都与名字相同 → 留空（名字行已含功能描述，不需重复显示）
    cn_intro = ""
    for candidate in (plain, desc_zh, desc):
        if candidate and candidate != name_zh and candidate != cn_name:
            cn_intro = candidate
            break
    # __init__.py 特殊兜底：翻译注册表中 90 个 __init__.py 填了同样的通用描述
    # （"数据的包入口，把这一层的子模块归到一起..."），用完整包路径区分各包
    if path.endswith("__init__.py") and cn_intro and "包入口" in cn_intro and "统一管理" in cn_intro:
        pkg_parent = Path(path).parent
        pkg_parts = pkg_parent.parts
        pkg_short = "/".join(pkg_parts[-2:]) if len(pkg_parts) >= 2 else pkg_parent.name
        cn_intro = f"{pkg_short} 包入口，管理该层子模块的统一加载和懒导入"

    gate_reason = (n.get("gate_reason") or "").strip()
    is_design = (n.get("design_maturity") or "") == "design"

    # 去重辅助：候选与已显示内容完全相同，或候选是已显示内容的子串（候选更短/相等）
    # 则跳过。候选更长（含额外信息）时不跳过——如 plain_zh="名字。功能描述" 比 name_zh 长。
    # （翻译注册表 8314 条中大量 name_en/desc_zh/desc_en 填了同样的 docstring，
    #  不去重会导致节点标签同一行内容重复 2-3 遍）
    def _is_dup(candidate: str, shown: list[str]) -> bool:
        c = candidate.lower().strip()
        if not c:
            return True
        for s in shown:
            sl = s.lower().strip()
            if not sl:
                continue
            if c == sl or c in sl:
                return True
        return False

    parts: list[str] = []
    shown: list[str] = []  # 已显示的文本（用于去重判断）
    # ── 中文部分（前面）──
    parts.append(cn_name)
    shown.append(cn_name)
    if cn_intro and not _is_dup(cn_intro, shown):
        parts.append(cn_intro)
        shown.append(cn_intro)
    if gate_reason and is_design:
        parts.append(f"⛔ {gate_reason}")
    # ── 英文部分（后面）——与已显示内容重复则跳过 ──
    if name_en and not _is_dup(name_en, shown):
        parts.append(name_en)
        shown.append(name_en)
    if desc_en and not _is_dup(desc_en, shown):
        parts.append(desc_en)
        shown.append(desc_en)
    # ── 末尾：文件路径 + 成熟度（颜色已区分，放最后）──
    parts.append(f"文件: {short_name}")
    parts.append(f"({maturity})")
    return "<br/>".join(_wrap_label_text(p) for p in parts)


def _bilingual_label_from_path(path: str, max_len: int = 60) -> str:
    """从模块路径构建跨域表格用的双语标签（中文名 / English (short_name)）。

    优先用模块翻译真源的双语名称；未登记回退到 docstring 首行；都无则仅 short_name。
    格式：``"中文名 / English (dir/file.py)"``，截断到 max_len。

    用于跨域依赖表格的源/目标模块列——只传 path 即可，无需完整节点 dict。
    """
    if not path:
        return ""
    # 优先双语名称（_node_bilingual_name 内部已封装 docstring 降级）
    name_bi = get_module_name_bilingual(path)
    short = _node_short_name({"path": path})
    if name_bi and short:
        label = f"{name_bi} ({short})"
    elif name_bi:
        label = name_bi
    else:
        # 真源未登记且无双语名称：回退到 docstring 首行（单语）
        desc = _node_desc_zh({"path": path, "description": ""})
        label = f"{desc} ({short})" if desc and short else (desc or short or "")
    return _truncate(label, max_len)


# ---------------------------------------------------------------------------
# 数据库查询函数
# ---------------------------------------------------------------------------


def get_domain_info(conn: PgConnExecuteWrapper, domain_id: str) -> dict | None:
    """查询域基本信息。"""
    cur = conn.execute(
        "SELECT domain_id, domain_name, current_modules, max_modules, production_nodes, layer_id, description "
        "FROM domains WHERE domain_id=%s",
        (domain_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "domain_id": row["domain_id"],
        "domain_name": row["domain_name"] or "",
        "current_modules": row["current_modules"] or 0,
        "max_modules": row["max_modules"] or 150,
        "production_nodes": row["production_nodes"] or 0,
        "layer_id": row["layer_id"] or "",
        "description": row["description"] or "",
    }


def get_domain_nodes(conn: PgConnExecuteWrapper, domain_id: str) -> list[dict]:
    """查询指定域的所有节点（排除 deprecated 已废弃节点）。"""
    cur = conn.execute(
        "SELECT n.node_id, n.path, n.blueprint_id, n.design_maturity, n.build_status, n.node_name, "
        "n.node_type, n.gate_reason, "
        "(SELECT COUNT(*) FROM edges WHERE to_node_id=n.node_id) AS in_degree, "
        "(SELECT COUNT(*) FROM edges WHERE from_node_id=n.node_id) AS out_degree, "
        "n.architecture_layer, n.file_path "
        "FROM nodes n WHERE n.domain_id=%s AND n.build_status != 'deprecated' ORDER BY n.path",
        (domain_id,),
    )
    rows = []
    for r in cur.fetchall():
        # node_type='database' 是手工维护的持久基础设施节点（裁定#218），
        # path 是 SSoT 指针（→ infrastructure_registry.yaml INFRA-DB-xxx），不是 ghost
        if r.get("node_type") == "database":
            pass
        elif _is_ghost(r["path"] or "", r["design_maturity"] or ""):
            continue
        rows.append(
            {
                "node_id": r["node_id"],
                "path": r["path"] or "",
                "blueprint_id": r["blueprint_id"] or "",
                "design_maturity": r["design_maturity"] or "",
                "build_status": r["build_status"] or "",
                "node_name": r["node_name"] or "",
                "in_degree": r["in_degree"] or 0,
                "out_degree": r["out_degree"] or 0,
                "architecture_layer": r["architecture_layer"] or "",
                "node_type": r["node_type"] or "",
                "file_path": r["file_path"] or "",
                "gate_reason": r["gate_reason"] or "",
            }
        )
    return rows


def get_domain_edges(conn: PgConnExecuteWrapper, domain_id: str) -> list[dict]:
    """查询域内依赖边（from_node 和 to_node 都在本域，排除 deprecated 节点的边）。

    返回每条边的两端节点路径、名称、设计成熟度，供 Mermaid 图和 ASCII 依赖图使用。
    """
    cur = conn.execute(
        """SELECT e.from_node_id, e.to_node_id, e.dep_type, e.dep_maturity,
                  n1.path AS from_path, n2.path AS to_path,
                  n1.design_maturity AS from_maturity, n2.design_maturity AS to_maturity,
                  n1.node_name AS from_name, n2.node_name AS to_name
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=%s AND n2.domain_id=%s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
           ORDER BY e.from_node_id, e.to_node_id""",
        (domain_id, domain_id),
    )
    edges = []
    for r in cur.fetchall():
        if _is_ghost(r["from_path"] or "", r["from_maturity"] or "") or _is_ghost(r["to_path"] or "", r["to_maturity"] or ""):
            continue
        edges.append(
            {
                "from_node_id": r["from_node_id"],
                "to_node_id": r["to_node_id"],
                "dep_type": r["dep_type"] or "",
                "dep_maturity": r["dep_maturity"] or "",
                "from_path": r["from_path"] or "",
                "to_path": r["to_path"] or "",
                "from_maturity": r["from_maturity"] or "",
                "to_maturity": r["to_maturity"] or "",
                "from_name": r["from_name"] or "",
                "to_name": r["to_name"] or "",
            }
        )
    return edges


def get_cross_domain_deps(conn: PgConnExecuteWrapper, domain_id: str) -> tuple[list[dict], list[dict]]:
    """查询跨域依赖（聚合统计，排除 deprecated 节点的边）。

    返回: (本域依赖的其他域列表, 依赖本域的其他域列表)
    """
    # 本域依赖的其他域（出边：from_node 在本域，to_node 在其他域）
    cur = conn.execute(
        """SELECT n2.domain_id as target_domain, COUNT(*) as cnt,
                  STRING_AGG(DISTINCT e.dep_type, ',') as dep_types
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=%s AND n2.domain_id != %s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
           GROUP BY n2.domain_id
           ORDER BY cnt DESC""",
        (domain_id, domain_id),
    )
    outgoing = []
    for r in cur.fetchall():
        outgoing.append({"target_domain": r["target_domain"], "count": r["cnt"], "dep_types": r["dep_types"] or ""})

    # 依赖本域的其他域（入边：from_node 在其他域，to_node 在本域）
    cur = conn.execute(
        """SELECT n1.domain_id as source_domain, COUNT(*) as cnt,
                  STRING_AGG(DISTINCT e.dep_type, ',') as dep_types
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n2.domain_id=%s AND n1.domain_id != %s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
           GROUP BY n1.domain_id
           ORDER BY cnt DESC""",
        (domain_id, domain_id),
    )
    incoming = []
    for r in cur.fetchall():
        incoming.append({"source_domain": r["source_domain"], "count": r["cnt"], "dep_types": r["dep_types"] or ""})

    return outgoing, incoming


def get_cross_domain_deps_detail(conn: PgConnExecuteWrapper, domain_id: str) -> tuple[list[dict], list[dict]]:
    """查询跨域依赖的详细信息（每条边的源模块→目标模块），排除 deprecated 节点的边。

    返回: (出边明细列表, 入边明细列表)，每条含:
    - from_path, to_path (模块路径)
    - from_domain, to_domain
    - dep_type
    用于明细表格展示具体哪个模块依赖哪个模块。
    """
    # 出边明细：from_node 在本域，to_node 在外部域
    cur = conn.execute(
        """SELECT e.dep_type, n1.path AS from_path, n2.path AS to_path,
                  n1.domain_id AS from_domain, n2.domain_id AS to_domain,
                  n1.design_maturity AS from_maturity, n2.design_maturity AS to_maturity
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=%s AND n2.domain_id != %s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
           ORDER BY n2.domain_id, n1.path, n2.path""",
        (domain_id, domain_id),
    )
    outgoing_detail = []
    for r in cur.fetchall():
        if _is_ghost(r["from_path"] or "", r["from_maturity"] or "") or _is_ghost(r["to_path"] or "", r["to_maturity"] or ""):
            continue
        outgoing_detail.append({
            "from_path": r["from_path"] or "",
            "to_path": r["to_path"] or "",
            "from_domain": r["from_domain"] or "",
            "to_domain": r["to_domain"] or "",
            "dep_type": r["dep_type"] or "",
        })

    # 入边明细：from_node 在外部域，to_node 在本域
    cur = conn.execute(
        """SELECT e.dep_type, n1.path AS from_path, n2.path AS to_path,
                  n1.domain_id AS from_domain, n2.domain_id AS to_domain,
                  n1.design_maturity AS from_maturity, n2.design_maturity AS to_maturity
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n2.domain_id=%s AND n1.domain_id != %s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
           ORDER BY n1.domain_id, n1.path, n2.path""",
        (domain_id, domain_id),
    )
    incoming_detail = []
    for r in cur.fetchall():
        if _is_ghost(r["from_path"] or "", r["from_maturity"] or "") or _is_ghost(r["to_path"] or "", r["to_maturity"] or ""):
            continue
        incoming_detail.append({
            "from_path": r["from_path"] or "",
            "to_path": r["to_path"] or "",
            "from_domain": r["from_domain"] or "",
            "to_domain": r["to_domain"] or "",
            "dep_type": r["dep_type"] or "",
        })

    return outgoing_detail, incoming_detail


def generate_cross_domain_mermaid(
    domain_id: str,
    domain_name: str,
    outgoing_agg: list[dict],
    incoming_agg: list[dict],
) -> str:
    """生成跨域依赖 Mermaid 图（只显示直接连接的外部域，不显示具体节点）。

    - 本域作为中心节点
    - 出边（本域 → 外部域）：实线箭头，标注依赖数和类型
    - 入边（外部域 → 本域）：实线箭头，标注依赖数和类型
    - 只显示直接连接的域，不展开具体节点
    - 外部域节点显示中英文域名
    """
    lines = [_MERMAID_GRAY_THEME, "graph LR"]

    # 本域节点
    self_id = sanitize_node_id(domain_id)
    safe_name = _sanitize_subgraph_label(domain_name)
    lines.append(f'    {self_id}["{domain_id}<br/>{safe_name}"]')

    # 收集所有外部域（去重），显示中英文
    external_domains: dict[str, str] = {}  # domain_id -> mermaid_id
    for d in outgoing_agg:
        ext = d["target_domain"]
        if ext not in external_domains:
            ext_id = sanitize_node_id(ext)
            ext_name_zh = get_domain_name_zh_strict(ext)
            label = f"{ext}<br/>{ext_name_zh}" if ext_name_zh else ext
            external_domains[ext] = ext_id
            lines.append(f'    {ext_id}["{label}"]')
    for d in incoming_agg:
        ext = d["source_domain"]
        if ext not in external_domains:
            ext_id = sanitize_node_id(ext)
            ext_name_zh = get_domain_name_zh_strict(ext)
            label = f"{ext}<br/>{ext_name_zh}" if ext_name_zh else ext
            external_domains[ext] = ext_id
            lines.append(f'    {ext_id}["{label}"]')

    # 出边：本域 → 外部域
    for d in outgoing_agg:
        ext_id = external_domains.get(d["target_domain"])
        if ext_id:
            dep_label = _dep_types_display(d["dep_types"])
            lines.append(f"    {self_id} -->|{d['count']}条 {dep_label}| {ext_id}")

    # 入边：外部域 → 本域
    for d in incoming_agg:
        ext_id = external_domains.get(d["source_domain"])
        if ext_id:
            dep_label = _dep_types_display(d["dep_types"])
            lines.append(f"    {ext_id} -->|{d['count']}条 {dep_label}| {self_id}")

    return "\n".join(lines)


def get_cross_domain_edges_detail(
    conn: PgConnExecuteWrapper, domain_id: str, internal_node_ids: list[int]
) -> tuple[list[dict], list[dict]]:
    """查询跨域边的详细信息（涉及指定内部节点的，排除 deprecated 节点的边），供 Mermaid 图绘制外部节点和边。

    返回: (出边列表, 入边列表)，每条含 from_path/to_path/成熟度/外部域ID。
    """
    outgoing_edges: list[dict] = []
    incoming_edges: list[dict] = []
    if not internal_node_ids:
        return outgoing_edges, incoming_edges

    placeholders = ",".join(["%s"] * len(internal_node_ids))
    params_out = [domain_id, domain_id] + list(internal_node_ids)

    # 出边：from 内部节点 → 外部节点
    cur = conn.execute(
        f"""SELECT e.dep_type, n1.path AS from_path, n2.path AS to_path,
                  n1.design_maturity AS from_maturity, n2.design_maturity AS to_maturity,
                  n1.node_name AS from_name, n2.node_name AS to_name,
                  n2.domain_id AS ext_domain
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n1.domain_id=%s AND n2.domain_id != %s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
             AND e.from_node_id IN ({placeholders})
           LIMIT 15""",
        params_out,
    )
    for r in cur.fetchall():
        if _is_ghost(r["from_path"] or "", r["from_maturity"] or "") or _is_ghost(r["to_path"] or "", r["to_maturity"] or ""):
            continue
        outgoing_edges.append(
            {
                "dep_type": r["dep_type"] or "",
                "from_path": r["from_path"] or "",
                "to_path": r["to_path"] or "",
                "from_maturity": r["from_maturity"] or "",
                "to_maturity": r["to_maturity"] or "",
                "from_name": r["from_name"] or "",
                "to_name": r["to_name"] or "",
                "ext_domain": r["ext_domain"] or "",
            }
        )

    # 入边：from 外部节点 → 内部节点
    cur = conn.execute(
        f"""SELECT e.dep_type, n1.path AS from_path, n2.path AS to_path,
                  n1.design_maturity AS from_maturity, n2.design_maturity AS to_maturity,
                  n1.node_name AS from_name, n2.node_name AS to_name,
                  n1.domain_id AS ext_domain
           FROM edges e
           JOIN nodes n1 ON e.from_node_id = n1.node_id
           JOIN nodes n2 ON e.to_node_id = n2.node_id
           WHERE n2.domain_id=%s AND n1.domain_id != %s
             AND n1.build_status != 'deprecated' AND n2.build_status != 'deprecated'
             AND e.to_node_id IN ({placeholders})
           LIMIT 15""",
        params_out,
    )
    for r in cur.fetchall():
        if _is_ghost(r["from_path"] or "", r["from_maturity"] or "") or _is_ghost(r["to_path"] or "", r["to_maturity"] or ""):
            continue
        incoming_edges.append(
            {
                "dep_type": r["dep_type"] or "",
                "from_path": r["from_path"] or "",
                "to_path": r["to_path"] or "",
                "from_maturity": r["from_maturity"] or "",
                "to_maturity": r["to_maturity"] or "",
                "from_name": r["from_name"] or "",
                "to_name": r["to_name"] or "",
                "ext_domain": r["ext_domain"] or "",
            }
        )

    return outgoing_edges, incoming_edges


def build_numbering_map(conn: PgConnExecuteWrapper) -> dict[str, int]:
    """构建域编号映射：按 layer_id 分组排序，生成 {domain_id: number} 映射。

    层级顺序: L0_infrastructure(01-02) → L1_foundation(03-08) → L1_platform(09-15) → L2_domain(16-53)
    """
    cur = conn.execute("SELECT domain_id, layer_id FROM domains")
    domains = [(r["domain_id"], r["layer_id"] or "") for r in cur.fetchall()]

    def _sort_key(item: tuple[str, str]) -> tuple[int, str]:
        """_sort_key implementation."""
        layer = item[1]
        layer_idx = LAYER_ORDER.index(layer) if layer in LAYER_ORDER else len(LAYER_ORDER)
        return (layer_idx, item[0])

    domains.sort(key=_sort_key)
    return {did: idx + 1 for idx, (did, _) in enumerate(domains)}


# ---------------------------------------------------------------------------
# Mermaid 辅助函数
# ---------------------------------------------------------------------------


def sanitize_node_id(path: str) -> str:
    """将文件路径转为合法的 Mermaid 节点ID（只保留字母数字下划线）。"""
    if not path:
        return "node"
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", path)
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")
    return sanitized or "node"


def _sanitize_mermaid_label(text: str) -> str:
    """清理 Mermaid 标签中的特殊字符（方括号/引号/管道符）。"""
    if not text:
        return ""
    return text.replace("[", "(").replace("]", ")").replace('"', "'").replace("|", "/")


def _sanitize_subgraph_label(text: str) -> str:
    """清理 subgraph 标签（额外移除斜杠）。"""
    return _sanitize_mermaid_label(text).replace("/", "_")


def _compute_topo_layers(nodes: list[dict], edges: list[dict]) -> dict[int, int]:
    """计算节点拓扑层级（用于强制竖排分层）。

    返回 {node_id: layer}。layer 0 = 当前页内入度为 0 的节点；
    layer(node) = max(layer(前驱)) + 1（Kahn 算法）。环内节点（Kahn 未覆盖）
    统一分配 max_layer+1；孤立节点（无入无出）归 layer 0。
    仅考虑两端都在当前页 nodes 列表内的边。
    """
    node_ids = {n["node_id"] for n in nodes}
    out_edges: dict[int, list[int]] = {nid: [] for nid in node_ids}
    in_degree: dict[int, int] = {nid: 0 for nid in node_ids}
    for e in edges:
        f, t = e["from_node_id"], e["to_node_id"]
        if f in node_ids and t in node_ids:
            out_edges[f].append(t)
            in_degree[t] += 1

    layer: dict[int, int] = {}
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

    # 环内剩余节点（Kahn 未覆盖）—— 拓扑排序无法破环，统一放最大层 +1
    remaining = [nid for nid in node_ids if nid not in layer]
    if remaining:
        max_layer = max(layer.values()) if layer else 0
        for nid in remaining:
            layer[nid] = max_layer + 1

    return layer


# Mermaid 灰色主题（对齐 decision_index.md / 09_decision_l2a_research.md 风格）
_MERMAID_GRAY_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {"
    "'primaryColor': '#eaeaea', 'primaryTextColor': '#333333', "
    "'primaryBorderColor': '#666666', 'lineColor': '#666666', "
    "'secondaryColor': '#eaeaea', 'tertiaryColor': '#eaeaea', 'fontSize': '14px'"
    "}}}%%"
)

# 状态色（对齐 dataflow 图 d_ex_pf_core.md 风格，用颜色增强运营态/设计态区分）：
# 🟦 蓝色 = 运营态（已实现）/ 🟧 橙色虚线 = 设计态（未实现）
_CLASSDEF_PRODUCTION = "classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000"
_CLASSDEF_DESIGN = "classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5"
_CLASSDEF_EXTERNAL_PROD = "classDef external_prod fill:#e8f4fd,stroke:#0277bd,stroke-width:1px,color:#000"
_CLASSDEF_EXTERNAL_DESIGN = "classDef external_design fill:#fff8e7,stroke:#ef6c00,stroke-width:1px,color:#000,stroke-dasharray: 5 5"


def generate_internal_mermaid(
    domain_id: str,
    domain_name: str,
    nodes: list[dict],
    edges: list[dict],
    outgoing: list[dict],
    incoming: list[dict],
) -> str:
    """生成内嵌 Mermaid 依赖图代码（单页，节点子集由调用方传入）。

    风格对齐 decision_index.md / 09_decision_l2a_research.md：
    - flowchart TD + 灰色 init 主题（primaryColor #eaeaea / lineColor #666666 / fontSize 14px）
    - 拓扑分层强制竖排：Kahn 算法计算层级，同层节点用不可见边 ~~~ 横向串联强制同 rank，
      层间靠依赖边纵向连接，整体从上到下分层流动（每层一行）
    - 去掉 subgraph 域边界框（subgraph 让 dagre 在框内横向铺开，是竖向效果差元凶）
    - 保留 production/design/external 状态色，但降为与灰主题协调的低饱和配色
    - 实线箭头 --> = 运营态依赖（from和to都是production），虚线箭头 -.-> = 非运营态依赖
    - 跨域入边和出边用 external 节点表示；nodes 参数即当前页的节点子集
    """
    displayed_node_ids = {n["node_id"] for n in nodes}

    lines = [_MERMAID_GRAY_THEME, "flowchart TD"]

    # 节点定义 + 构建 path→mermaid_id 映射
    node_id_map: dict[int, str] = {}
    path_to_mermaid: dict[str, str] = {}
    used_ids: set[str] = set()
    for n in nodes:
        mermaid_id = sanitize_node_id(n["path"] or n["node_name"] or f"node{n['node_id']}")
        base_id = mermaid_id
        counter = 1
        while mermaid_id in used_ids:
            mermaid_id = f"{base_id}_{counter}"
            counter += 1
        used_ids.add(mermaid_id)
        node_id_map[n["node_id"]] = mermaid_id
        if n["path"]:
            path_to_mermaid[n["path"]] = mermaid_id

    # 拓扑分层 + 按层级分组声明节点（强制竖排：每层一行，层间纵向流动）
    layers = _compute_topo_layers(nodes, edges)
    layer_groups: dict[int, list[dict]] = {}
    for n in nodes:
        layer_groups.setdefault(layers.get(n["node_id"], 0), []).append(n)

    for layer_idx in sorted(layer_groups.keys()):
        group = layer_groups[layer_idx]
        for n in group:
            mermaid_id = node_id_map[n["node_id"]]
            label = _sanitize_mermaid_label(_node_mermaid_label(n))
            lines.append(f'    {mermaid_id}["{label}"]')
        # 同层节点用不可见边 ~~~ 横向串联，强制 dagre 同 rank（每层一行）
        if len(group) > 1:
            ids = [node_id_map[n["node_id"]] for n in group]
            for i in range(len(ids) - 1):
                lines.append(f"    {ids[i]} ~~~ {ids[i + 1]}")

    # 域内依赖边
    for e in edges:
        if e["from_node_id"] in displayed_node_ids and e["to_node_id"] in displayed_node_ids:
            from_id = node_id_map.get(e["from_node_id"], sanitize_node_id(e["from_path"]))
            to_id = node_id_map.get(e["to_node_id"], sanitize_node_id(e["to_path"]))
            if e["from_maturity"] == "production" and e["to_maturity"] == "production":
                arrow = "-->"
            else:
                arrow = "-.->"
            dep_label = _sanitize_mermaid_label(_dep_type_display(e["dep_type"])) or "dep"
            lines.append(f"    {from_id} {arrow}|{dep_label}| {to_id}")

    # 跨域外部节点
    external_nodes: dict[str, tuple[str, str]] = {}  # ext_domain -> (mermaid_id, maturity)

    def _get_or_create_external(ext_domain: str, maturity: str) -> str:
        """跨域节点代表"另一个域"（非单个模块），标签同样塞入完整信息。

        与域内节点 _node_mermaid_label 对齐（2026-08-01 第四轮：中英分排）：
        中文在前（域中文名+简介）→ 英文在后（域英文名）→ 跨域节点标识 → 成熟度最后。
        域信息取自 domain_name_mapping（中文名 DB 优先 / 英文名+简介硬编码真源）。
        """
        if ext_domain in external_nodes:
            return external_nodes[ext_domain][0]
        ext_id = sanitize_node_id(ext_domain)
        base = ext_id
        idx = 1
        while ext_id in used_ids:
            ext_id = f"{base}_{idx}"
            idx += 1
        used_ids.add(ext_id)
        external_nodes[ext_domain] = (ext_id, maturity)
        ext_maturity = _maturity_display(maturity)
        ext_name_zh = get_domain_name_zh_strict(ext_domain)
        ext_name_en = get_domain_name_en(ext_domain)
        ext_desc = get_domain_desc_zh(ext_domain)
        # ── 中文部分（前面）──
        parts = [ext_name_zh or ext_domain]
        if ext_desc:
            parts.append(ext_desc)
        # ── 英文部分（后面）──
        if ext_name_en and ext_name_en != ext_domain:
            parts.append(ext_name_en)
        # ── 末尾：跨域节点标识 + 成熟度（颜色已区分，放最后）──
        parts.append("跨域节点 / cross-domain")
        parts.append(f"({ext_maturity})")
        ext_label = _sanitize_mermaid_label("<br/>".join(_wrap_label_text(p) for p in parts))
        lines.append(f'    {ext_id}["{ext_label}"]')
        return ext_id

    # 跨域出边
    for e in outgoing:
        from_mermaid = path_to_mermaid.get(e["from_path"])
        if not from_mermaid:
            continue
        ext_id = _get_or_create_external(e["ext_domain"], e["to_maturity"] or "unknown")
        if e["from_maturity"] == "production" and e["to_maturity"] == "production":
            arrow = "-->"
        else:
            arrow = "-.->"
        dep_label = _sanitize_mermaid_label(_dep_type_display(e["dep_type"])) or "dep"
        lines.append(f"    {from_mermaid} {arrow}|{dep_label}| {ext_id}")

    # 跨域入边
    for e in incoming:
        to_mermaid = path_to_mermaid.get(e["to_path"])
        if not to_mermaid:
            continue
        ext_id = _get_or_create_external(e["ext_domain"], e["from_maturity"] or "unknown")
        if e["from_maturity"] == "production" and e["to_maturity"] == "production":
            arrow = "-->"
        else:
            arrow = "-.->"
        dep_label = _sanitize_mermaid_label(_dep_type_display(e["dep_type"])) or "dep"
        lines.append(f"    {ext_id} {arrow}|{dep_label}| {to_mermaid}")

    # classDef 样式（灰主题协调的低饱和状态色）
    lines.append(f"    {_CLASSDEF_PRODUCTION}")
    lines.append(f"    {_CLASSDEF_DESIGN}")
    lines.append(f"    {_CLASSDEF_EXTERNAL_PROD}")
    lines.append(f"    {_CLASSDEF_EXTERNAL_DESIGN}")

    # 应用样式到内部节点
    prod_nodes = []
    design_nodes = []
    for n in nodes:
        mermaid_id = node_id_map[n["node_id"]]
        if n["design_maturity"] == "production":
            prod_nodes.append(mermaid_id)
        else:
            design_nodes.append(mermaid_id)
    if prod_nodes:
        lines.append(f"    class {','.join(prod_nodes)} production")
    if design_nodes:
        lines.append(f"    class {','.join(design_nodes)} design")

    # 应用样式到外部节点
    ext_prod = []
    ext_design = []
    for ext_domain, (ext_id, maturity) in external_nodes.items():
        if maturity == "production":
            ext_prod.append(ext_id)
        else:
            ext_design.append(ext_id)
    if ext_prod:
        lines.append(f"    class {','.join(ext_prod)} external_prod")
    if ext_design:
        lines.append(f"    class {','.join(ext_design)} external_design")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# ASCII art 辅助函数（合并自 generate_domain_architecture_diagram.py）
# ---------------------------------------------------------------------------


def _display_width(s: str) -> int:
    """计算字符串显示宽度（CJK字符算2，其余算1）。"""
    width = 0
    for ch in s:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF
            or 0x3000 <= code <= 0x303F
            or 0xFF00 <= code <= 0xFFEF
            or 0x2E80 <= code <= 0x2EFF
            or 0x3400 <= code <= 0x4DBF
        ):
            width += 2
        else:
            width += 1
    return width


def _truncate(text: str, max_len: int = 40) -> str:
    """截断文本到指定显示宽度，超出则加'...'。保护 #ARCH-XXX 引用不被截断。"""
    if not text:
        return ""
    if _display_width(text) <= max_len:
        return text
    # 按显示宽度截断
    result = ""
    w = 0
    for ch in text:
        cw = 2 if ord(ch) > 0x7F else 1
        if w + cw > max_len - 3:
            break
        result += ch
        w += cw
    # 保护 #ARCH-XXX 引用：截断点落在引用中间时回退到引用之前
    m = re.search(r'#ARCH-[A-Z0-9-]*$', result)
    if m:
        full = re.match(r'#ARCH-[A-Z0-9-]+', text[m.start():])
        if full and full.group() != m.group():
            result = result[:m.start()].rstrip()
    # 保护 裁定#NNN 引用：截断点落在裁定编号中间时回退到编号之前（避免裁定编号被截断成不完整片段误触发 RULING_ATOMICITY 门禁）
    m2 = re.search(r'裁定#\d*$', result)
    if m2:
        full2 = re.match(r'裁定#\d+', text[m2.start():])
        if full2 and full2.group() != m2.group():
            result = result[:m2.start()].rstrip('（( \t　')
    return result + "..."


# ---------------------------------------------------------------------------
# 原子写入（合并自 generate_domain_architecture_diagram.py）
# ---------------------------------------------------------------------------


def _atomic_write(path: Path, content: str) -> None:
    """原子写入文件（tmp文件 + os.replace）。"""
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


# ---------------------------------------------------------------------------
# 主文档生成
# ---------------------------------------------------------------------------


def generate_domain_doc(domain_id: str, conn: PgConnExecuteWrapper, number: int = 0) -> str:
    """生成域文档内容（中英文对照表格 + 内嵌 Mermaid 依赖图 + ASCII art 架构图）。"""
    info = get_domain_info(conn, domain_id)
    if not info:
        print(f"ERROR: 域 '{domain_id}' 不存在", file=sys.stderr)
        return ""

    nodes = get_domain_nodes(conn, domain_id)
    edges = get_domain_edges(conn, domain_id)
    outgoing_agg, incoming_agg = get_cross_domain_deps(conn, domain_id)
    outgoing_detail, incoming_detail = get_cross_domain_deps_detail(conn, domain_id)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 统计
    design_count = sum(1 for n in nodes if n["design_maturity"] == "design")
    production_count = sum(1 for n in nodes if n["design_maturity"] == "production")
    capacity_status = "正常" if info["production_nodes"] <= info["max_modules"] else "超容"
    total_outgoing = sum(d["count"] for d in outgoing_agg)
    total_incoming = sum(d["count"] for d in incoming_agg)

    domain_name_zh = get_domain_name_zh(domain_id, info["domain_name"])
    domain_name_en = get_domain_name_en(domain_id)
    # v2.3（2026-07-19 Step 2.5）：移除 domain_name_zh_hardcoded 变量——v2.1 的"硬编码优先"
    # 逻辑在 v2.2 治本后已无意义（DB 全 63 域 domain_name 已统一为中文，get_domain_name_zh
    # 返回值即权威中文名）。直接用 domain_name_zh 即可。
    domain_desc_zh = get_domain_desc_zh(domain_id)

    lines = []
    # frontmatter（G1 门禁要求：doc_type, title, version, status, date, owner, ttl）
    lines.append("---")
    lines.append("doc_type: architecture_view")
    lines.append(f"title: {domain_id} {domain_name_zh}架构文档")
    lines.append('version: "1.0"')
    lines.append("status: active")
    lines.append(f"date: {now.split()[0]}")
    lines.append("owner: auto-generator")
    lines.append("ttl: permanent")
    lines.append("---")
    lines.append("")
    # 标题中文加"域"后缀（如"规则治理域"），明确标识这是功能域；英文不加（Rule Governance 已含 governance）
    lines.append(f"# {number:02d}_{domain_id.replace('-', '_').lower()} / {domain_name_zh}域 / {domain_name_en}")
    lines.append("")
    if domain_desc_zh:
        lines.append(f"> **功能简介 / Overview**: {domain_desc_zh}")
        lines.append("")
    lines.append(f"> **文档作用 / Purpose**: 展示 {domain_name_zh}（{domain_id}）功能域的域内依赖关系、跨域依赖关系，模块信息（成熟度/中英文名/大白话/文件路径）内嵌于 Mermaid 节点，供架构审查和域治理参考。")
    lines.append("")
    lines.append(f"> 本文档由 generate_domain_doc.py 从 {DB_DISPLAY_NAME} 自动生成")
    # DM-90974 Phase 2: 移除 per-second `最后更新: {now}` body 行——违反"相同 DB 输入→相同输出"幂等 invariant
    # （原 line 1083 每次 --all 都让所有域文档产生纯时间戳 diff → reconciler 噪音 commit）。
    # 生成时间由 git log 提供；frontmatter date 字段保留粗粒度（每日）元数据。
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} nodes表 + edges表")
    lines.append("")
    # HTML 可缩放版本快速跳转链接（IDE MD 预览无法无限放大 Mermaid，HTML 版支持 Ctrl+滚轮缩放+拖动平移）
    # 必须用 http:// 链接：Trae 预览面板对 file:/// 和相对路径链接会在编辑器内打开源码，
    # 只有 http:// 链接会交给外部浏览器渲染。需本地 http server（见 _DOC_HTTP_BASE 注释）。
    # 注意：不要在链接前加 emoji（如 🖼️）——会干扰 markdown 渲染器把 [text](url) 识别为链接。
    safe_name_html = f"{number:02d}_{domain_id.replace('-', '_').lower()}.html"
    try:
        # HTML 集中在 _zoomable_html/ 子文件夹（zoomable_html.emit_zoomable_html 联动生成）
        html_rel = (OUTPUT_DIR / HTML_SUBDIR / safe_name_html).relative_to(REPO_ROOT).as_posix()
        html_url = f"{_DOC_HTTP_BASE}/{html_rel}"
    except ValueError:
        # output-dir 在仓库根之外时降级为相对路径（罕见，仅 --output-dir 手动覆盖时触发）
        html_url = f"{HTML_SUBDIR}/{safe_name_html}"
    lines.append(f"> **[可缩放 HTML 版 / Zoomable HTML]({html_url})** — Ctrl+滚轮缩放 ｜ 双击重置 ｜ Ctrl+Shift+D 切换拖动/选择模式")
    lines.append("")

    # 域基本信息（中英文对照）
    lines.append("## 域基本信息 / Domain Overview")
    lines.append("")
    lines.append("| 字段 | 值 | Field | Value |")
    lines.append("|------|------|-------|-------|")
    lines.append(f"| 编号 | {number:02d} | Number | {number:02d} |")
    lines.append(f"| 域ID | {domain_id} | Domain ID | {domain_id} |")
    lines.append(f"| 域名称 | {domain_name_zh} | Domain Name | {domain_name_en} |")
    layer_zh, layer_en = get_layer_name_bilingual(info['layer_id'])
    lines.append(f"| 层级 | {layer_zh} | Layer | {layer_en} |")
    lines.append(f"| 模块数 | {len(nodes)} | Module Count | {len(nodes)} |")
    lines.append(f"| 域内依赖 | {len(edges)} | Internal Dependencies | {len(edges)} |")
    lines.append(f"| 跨域入边 | {total_incoming} | Cross-domain Incoming | {total_incoming} |")
    lines.append(f"| 跨域出边 | {total_outgoing} | Cross-domain Outgoing | {total_outgoing} |")
    lines.append(f"| 设计态模块 | {design_count} | Design Modules | {design_count} |")
    lines.append(f"| 生产态模块 | {production_count} | Production Modules | {production_count} |")
    lines.append(
        f"| 容量 | {info['production_nodes']}/{info['max_modules']} ({capacity_status}) | "
        f"Capacity | {info['production_nodes']}/{info['max_modules']} ({capacity_status}) |"
    )
    if info["description"]:
        lines.append(f"| 描述 | {info['description']} | Description | {info['description']} |")
    lines.append("")

    # 域内依赖图（内嵌 Mermaid，三视图：全景图 + 运营态图 + 设计态图）
    # 模块信息（成熟度全称+名称+大白话/简介+文件路径）已内嵌于 Mermaid 节点标签。
    # 三视图分区（对齐 HTML 渲染铁律：全景图→运营态的图→设计态的图，每图带小标题，
    # 标注视图类型，禁止分页标注页数）：
    #   全景图（全部模块 + 跨域外部节点）→ 运营态图（仅 production）→ 设计态图（仅 design）
    lines.append("## 域内依赖图 / Internal Dependency Diagram")
    lines.append("")
    lines.append("> 依赖图内嵌在本文档中，IDE 可直接渲染；网页版可 Ctrl+滚轮缩放 + 拖动平移查看细节。")
    lines.append(">")
    lines.append("> **图例说明 / Legend**：")
    lines.append("> - 🟦 **蓝色 = 运营态模块**（production，已上线运行）")
    lines.append("> - 🟧 **橙色虚线 = 设计态模块**（design，蓝图阶段，代码未写）")
    lines.append("> - **实线箭头 = 运营态依赖**（已生效的依赖关系）")
    lines.append("> - **虚线箭头 = 非运营态依赖**（计划中/验证中的依赖关系）")
    lines.append("")

    # 跨域边明细（仅全景图用；运营态/设计态图不显示跨域外部节点，聚焦域内结构）
    all_outgoing, all_incoming = get_cross_domain_edges_detail(conn, domain_id, [n["node_id"] for n in nodes])

    def _emit_internal_view(title: str, hint: str, view_nodes: list[dict], view_outgoing: list[dict], view_incoming: list[dict]) -> None:
        """输出单个域内依赖视图（带小标题；空节点集用占位说明，避免空 mermaid 块）。

        edges 传全集，generate_internal_mermaid 内部按 view_nodes 的 node_id 集自动过滤
        （只画两端都在 view_nodes 内的边），故运营态/设计态图各自只显示同态域内依赖；
        跨 production↔design 的混合边仅在全景图展示。
        """
        lines.append(f"### {title}")
        lines.append("")
        lines.append(f"> {hint}")
        lines.append("")
        if not view_nodes:
            lines.append("> （无模块 / No modules）")
            lines.append("")
            return
        mermaid_code = generate_internal_mermaid(
            domain_id, domain_name_zh, view_nodes, edges, view_outgoing, view_incoming
        )
        lines.append("```mermaid")
        lines.append(mermaid_code)
        lines.append("```")
        lines.append("")

    # 图1：全景图（全部模块 + 跨域外部节点，颜色区分运营态/设计态）
    _emit_internal_view(
        "全景图（全部模块，颜色区分运营态/设计态）",
        f"展示全部 {len(nodes)} 个模块（生产态 {production_count} + 设计态 {design_count}），含跨域依赖外部节点。节点含成熟度+名称+大白话/简介+文件路径。",
        nodes, all_outgoing, all_incoming,
    )

    # 图2：运营态的图（仅 design_maturity=production 的模块和域内依赖）
    prod_nodes = [n for n in nodes if n["design_maturity"] == "production"]
    _emit_internal_view(
        "运营态的图（仅 design_maturity=production 的模块和域内依赖）",
        f"仅展示已上线运行的模块（共 {len(prod_nodes)} 个），不含跨域外部节点。跨域依赖见下方跨域依赖章节。",
        prod_nodes, [], [],
    )

    # 图3：设计态的图（仅 design_maturity=design 的模块和域内依赖）
    design_nodes = [n for n in nodes if n["design_maturity"] == "design"]
    _emit_internal_view(
        "设计态的图（仅 design_maturity=design 的模块和域内依赖）",
        f"仅展示蓝图阶段、代码未写的设计态模块（共 {len(design_nodes)} 个），不含跨域外部节点。",
        design_nodes, [], [],
    )

    # 跨域依赖（中英文对照）
    lines.append("## 跨域依赖 / Cross-domain Dependencies")
    lines.append("")

    # 本域依赖的其他域（出边明细）
    lines.append("### 本域依赖的其他域（出边）/ Depends On")
    lines.append("")
    if outgoing_detail:
        lines.append("| # | 本域模块 / Source Module | → | 外部域-目标模块 / Target Module | 依赖类型 / Type |")
        lines.append("|:--:|---------|:--:|---------|---------|")
        for i, d in enumerate(outgoing_detail, 1):
            src_label = _bilingual_label_from_path(d["from_path"])
            tgt_domain = d["to_domain"]
            tgt_domain_zh = get_domain_name_zh_strict(tgt_domain)
            tgt_domain_label = f"{tgt_domain} {tgt_domain_zh}" if tgt_domain_zh else tgt_domain
            tgt_label = _bilingual_label_from_path(d["to_path"])
            lines.append(f"| {i} | {src_label} | → | {tgt_domain_label}: {tgt_label} | {_dep_type_display(d['dep_type'])} |")
    else:
        lines.append("无跨域出边依赖 / No cross-domain outgoing dependencies")
    lines.append("")

    # 依赖本域的其他域（入边明细）
    lines.append("### 依赖本域的其他域（入边）/ Depended By")
    lines.append("")
    if incoming_detail:
        lines.append("| # | 外部域-源模块 / Source Module | → | 本域模块 / Target Module | 依赖类型 / Type |")
        lines.append("|:--:|---------|:--:|---------|---------|")
        for i, d in enumerate(incoming_detail, 1):
            src_domain = d["from_domain"]
            src_domain_zh = get_domain_name_zh_strict(src_domain)
            src_domain_label = f"{src_domain} {src_domain_zh}" if src_domain_zh else src_domain
            src_label = _bilingual_label_from_path(d["from_path"])
            tgt_label = _bilingual_label_from_path(d["to_path"])
            lines.append(f"| {i} | {src_domain_label}: {src_label} | → | {tgt_label} | {_dep_type_display(d['dep_type'])} |")
    else:
        lines.append("无跨域入边依赖 / No cross-domain incoming dependencies")
    lines.append("")

    # 跨域依赖图（第五视图：本域与直接连接的外部域）
    lines.append("### 跨域依赖图 / Cross-domain Dependency Diagram")
    lines.append("")
    total_cross = total_outgoing + total_incoming
    unique_external = len({d["target_domain"] for d in outgoing_agg} | {d["source_domain"] for d in incoming_agg})
    lines.append(
        f"> 本域与 {unique_external} 个外部域直接连接（出边 {total_outgoing} 条 + 入边 {total_incoming} 条 = {total_cross} 条）。"
        "只显示直接连接的域，不展开具体节点。"
    )
    lines.append("")
    if outgoing_agg or incoming_agg:
        mermaid_code = generate_cross_domain_mermaid(
            domain_id, domain_name_zh, outgoing_agg, incoming_agg
        )
        lines.append("```mermaid")
        lines.append(mermaid_code)
        lines.append("```")
    else:
        lines.append("> （无跨域依赖 / No cross-domain dependencies）")
    lines.append("")

    # 说明
    lines.append("## 说明 / Notes")
    lines.append("")
    lines.append(f"- **数据源 / Data Source**: `{DB_DISPLAY_NAME}` 的 `nodes`、`edges`、`domains` 表")
    lines.append("- **生成器 / Generator**: `generate_domain_doc.py`（G2+G10 合并）")
    lines.append("- **维护方式 / Maintenance**: 自动生成，全景图更新时刷新")
    lines.append("- **文件名规则 / File Naming**: `{编号:02d}_{域ID小写}.md`，如 `16_d_trading.md`")
    lines.append(
        "- **图例说明 / Legend**: `[production]`=已上线 / `[design]`=设计中 / "
        "`[unknown]`=未知"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main() -> None:
    """入口：生成指定域的 MD 文档（含 Mermaid 依赖图 + ASCII art 架构图）。"""
    parser = argparse.ArgumentParser(
        description="G2+G10 合并: 生成域架构文档(含内嵌Mermaid依赖图+跨域依赖图，模块信息内嵌节点)"
    )
    parser.add_argument(
        "domain_id",
        type=str,
        nargs="?",
        default=None,
        help="域ID (如 D_TRADING)。--all 模式下可省略",
    )
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--all", action="store_true", help="生成所有域的文档")
    args = parser.parse_args()

    if not args.all and not args.domain_id:
        parser.error("domain_id 是必填参数（除非使用 --all）")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Bug 8 fix: psycopg2 connection has no .execute() (sqlite3 API); wrapper adds it + DictCursor
    import psycopg2.extras

    class _PgConnSqliteCompat:
        """psycopg2 -> sqlite3 API compat wrapper."""
        def __init__(self, conn):
            """__init__ implementation."""
            self._conn = conn
        def execute(self, sql, params=None):
            """execute implementation."""
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(sql) if params is None else cur.execute(sql, params)
            return cur
        def __getattr__(self, name):
            """__getattr__ implementation."""
            return getattr(self._conn, name)
        def close(self):
            """close implementation."""
            self._conn.close()

    conn = _PgConnSqliteCompat(get_depgraph_pg_connection(autocommit=True))
    try:
        # 构建编号映射（按 layer_id 分组排序）
        numbering_map = build_numbering_map(conn)

        if args.all:
            # 生成所有域的文档
            cur = conn.execute("SELECT domain_id FROM domains ORDER BY domain_id")
            domain_ids = [r["domain_id"] for r in cur.fetchall()]
            success = 0
            for did in domain_ids:
                number = numbering_map.get(did, 0)
                content = generate_domain_doc(did, conn, number)
                if content:
                    safe_name = did.replace("-", "_").lower()
                    out_path = output_dir / f"{number:02d}_{safe_name}.md"
                    _atomic_write(out_path, content)
                    # 联动生成可缩放 HTML 到 _zoomable_html/ 子文件夹（md 刷新即 HTML 刷新）
                    html_path = emit_zoomable_html(out_path, content)
                    html_info = f" +HTML({HTML_SUBDIR}/{html_path.name})" if html_path else ""
                    print(f"[OK] 生成 {out_path} ({len(content)} 字符){html_info}")
                    success += 1
            print(f"\n共生成 {success}/{len(domain_ids)} 个域文档")
            # 治本：清理残留文件（解决只增不删）
            expected_docs = {
                f"{numbering_map.get(did, 0):02d}_{did.replace('-', '_').lower()}.md"
                for did in domain_ids if numbering_map.get(did, 0)
            }
            # 1. 清理非 _architecture 的残留 doc（编号格式不匹配的旧文件）
            deleted_docs = cleanup_stale_files(
                output_dir, expected_docs, r'^\d{2}_d_(?!.*_architecture\.md$)[a-z0-9_]+\.md$'
            )
            if deleted_docs:
                print(f"[CLEANUP] 删除 {len(deleted_docs)} 个残留文档: {deleted_docs}")
            # 2. 清理所有过时的 _architecture.md（合并后不再生成这类文件，治本消除孤儿制品）
            deleted_arch = cleanup_stale_files(
                output_dir, set(), r'^\d{2}_d_[a-z0-9_]+_architecture\.md$'
            )
            if deleted_arch:
                print(f"[CLEANUP] 删除 {len(deleted_arch)} 个过时 _architecture.md 孤儿制品: {deleted_arch}")
            # 3. 清理 _zoomable_html/ 子文件夹中过时的 HTML（域被删除时联动 HTML 不残留）
            expected_html = {name.replace(".md", ".html") for name in expected_docs}
            deleted_html = cleanup_stale_files(
                output_dir / HTML_SUBDIR, expected_html, r'^\d{2}_d_[a-z0-9_]+\.html$'
            )
            if deleted_html:
                print(f"[CLEANUP] 删除 {len(deleted_html)} 个过时 HTML: {deleted_html}")
        else:
            # 生成单个域的文档
            number = numbering_map.get(args.domain_id, 0)
            content = generate_domain_doc(args.domain_id, conn, number)
            if not content:
                sys.exit(EXIT_ERROR)
            safe_name = args.domain_id.replace("-", "_").lower()
            out_path = output_dir / f"{number:02d}_{safe_name}.md"
            _atomic_write(out_path, content)
            # 联动生成可缩放 HTML 到 _zoomable_html/ 子文件夹（md 刷新即 HTML 刷新）
            html_path = emit_zoomable_html(out_path, content)
            html_info = f" +HTML({HTML_SUBDIR}/{html_path.name})" if html_path else ""
            print(f"[OK] 生成 {out_path} ({len(content)} 字符){html_info}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
