# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_domain_doc
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
- 模块清单（按 architecture_layer 分组）
- 域内依赖图（内嵌 Mermaid，分页显示）
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

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from domain_name_mapping import get_domain_name_zh, get_domain_name_en, get_layer_name_bilingual
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "02_domain_architecture_docs"

# ARCH-052: 聚合节点类型——配置对象集（门禁/脚本/测试/规则文件）用 1 个聚合节点代表
# 图视图只显示聚合节点本身；清单视图展开 registry.yaml 列出内部 items
AGGREGATE_NODE_TYPES = {
    "gate_rule_set",           # 门禁规则集（D_GOV_ENFORCEMENT）
    "script_collection",       # 脚本集（D_GOV_SCRIPTS）
    "test_suite",              # 测试集（D_AUDITTEST）
    "strategy_collection",     # 策略集（D_TRADING）
    "rule_registry_collection",  # 规则注册表集（D_GOVERNANCE）
}

# 层级排序：编号按此顺序分组分配
LAYER_ORDER = ["L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"]

# 层级中文显示名映射（合并自 generate_domain_architecture_diagram.py）
LAYER_DISPLAY = {
    "L0_infrastructure": "L0 基础设施层 / Infrastructure Layer",
    "L1_foundation": "L1 基础层 / Foundation Layer",
    "L1_platform": "L1 平台层 / Platform Layer",
    "L2_domain": "L2 领域层 / Domain Layer",
    "L3_application": "L3 应用层 / Application Layer",
}

# ASCII box 内部宽度（合并自 generate_domain_architecture_diagram.py）
BOX_WIDTH = 64


def _is_ghost(path: str) -> bool:
    """检查节点路径是否为 ghost（path 非空但磁盘上不存在）。

    第一性原理治本：即使不手动 deprecate，生成器也自动过滤幽灵文件，
    防止架构文档引用已删除的文件。铁律保障：新 AI 不需要知道要跑 deprecate。
    """
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
    except Exception:
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
    except Exception:
        pass
    return ""


def _load_registry_items(registry_path: str) -> list[dict]:
    """加载 registry.yaml 的 items 列表（ARCH-052 聚合节点展开用）。

    registry_path 是聚合节点的 path 字段（SSoT 指针），指向 registry.yaml 文件。
    返回 items 列表，每个 item 含 file/description 等字段。
    """
    if not registry_path:
        return []
    abs_path = REPO_ROOT / registry_path
    if not abs_path.exists() or not abs_path.suffix in ('.yaml', '.yml'):
        return []
    try:
        data = yaml.safe_load(abs_path.read_text(encoding='utf-8', errors='replace'))
        if isinstance(data, dict):
            items = data.get('items', []) or []
            return items if isinstance(items, list) else []
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# 中英文双显映射表 + 节点标签辅助函数（L180-194 修复：视图显示中文功能简介）
# ---------------------------------------------------------------------------

# 成熟度中英文映射（design_maturity 字段值 → 中文/英文双显）
MATURITY_DISPLAY = {
    "production": "生产态 / production",
    "design": "设计态 / design",
    "prototype": "原型态 / prototype",
    "unknown": "未知 / unknown",
    "": "未知 / unknown",
}

# 构建状态中英文映射（build_status 字段值 → 中文/英文双显）
BUILD_STATUS_DISPLAY = {
    "generated": "已生成 / generated",
    "handwritten": "手写 / handwritten",
    "deprecated": "已废弃 / deprecated",
    "": "—",
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


def _build_status_display(status: str) -> str:
    """构建状态值转中英文双显。"""
    return BUILD_STATUS_DISPLAY.get(status, f"{status} / {status}")


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
    """从节点数据提取短名称（文件名，不含路径）。"""
    node_name = n.get("node_name") or ""
    if node_name:
        return node_name.rsplit("/", 1)[-1]
    path = n.get("path") or ""
    if path:
        return path.rsplit("/", 1)[-1]
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
        return _truncate(doc_desc, 50)
    if path.endswith(('.yaml', '.yml')):
        yaml_desc = _extract_yaml_description(path)
        if yaml_desc:
            return _truncate(yaml_desc, 50)
    return ""


def _node_mermaid_label(n: dict) -> str:
    """生成 Mermaid 节点标签（中文功能简介在前+成熟度中英文）。

    格式参考 decision_index.md：(状态中英文) 中文名<br/>文件: 文件名
    """
    desc_zh = _node_desc_zh(n)
    maturity = _maturity_display(n.get("design_maturity") or "unknown")
    short_name = _node_short_name(n)

    if desc_zh:
        return f"({maturity}) {desc_zh}<br/>文件: {short_name}"
    else:
        return f"({maturity}) {short_name}"


def _node_ascii_label(n: dict) -> str:
    """生成 ASCII 视图节点标签（中文功能简介在前+成熟度中英文，单行）。"""
    desc_zh = _node_desc_zh(n)
    maturity = _maturity_display(n.get("design_maturity") or "unknown")
    short_name = _node_short_name(n)

    if desc_zh:
        return f"{desc_zh} [{maturity}]"
    else:
        return f"{short_name} [{maturity}]"


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
        "n.node_type, "
        "(SELECT COUNT(*) FROM edges WHERE to_node_id=n.node_id) AS in_degree, "
        "(SELECT COUNT(*) FROM edges WHERE from_node_id=n.node_id) AS out_degree, "
        "n.architecture_layer, n.file_path "
        "FROM nodes n WHERE n.domain_id=%s AND n.build_status != 'deprecated' ORDER BY n.path",
        (domain_id,),
    )
    rows = []
    for r in cur.fetchall():
        # node_type='database' 是手工维护的持久基础设施节点（裁定#2026-0701），
        # path 是 SSoT 指针（→ infrastructure_registry.yaml INFRA-DB-xxx），不是 ghost
        if r.get("node_type") == "database":
            pass
        elif _is_ghost(r["path"] or ""):
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
        if _is_ghost(r["from_path"] or "") or _is_ghost(r["to_path"] or ""):
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
        if _is_ghost(r["from_path"] or "") or _is_ghost(r["to_path"] or ""):
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
        if _is_ghost(r["from_path"] or "") or _is_ghost(r["to_path"] or ""):
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


def generate_internal_mermaid(
    domain_id: str,
    domain_name: str,
    nodes: list[dict],
    edges: list[dict],
    outgoing: list[dict],
    incoming: list[dict],
) -> str:
    """生成内嵌 Mermaid 依赖图代码（单页，节点子集由调用方传入）。

    - graph TD 格式
    - subgraph 包裹本域模块
    - 实线箭头 --> = 运营态依赖（from和to都是production）
    - 虚线箭头 -.-> = 设计态依赖（任一方非production）
    - 跨域入边和出边用 external 节点表示
    - nodes 参数即当前页的节点子集，由调用方分页传入
    """
    displayed_node_ids = {n["node_id"] for n in nodes}

    lines = ["graph TD"]

    # subgraph 包裹本域模块
    subgraph_id = sanitize_node_id(domain_id)
    safe_domain_name = _sanitize_subgraph_label(domain_name)
    lines.append(f'    subgraph {subgraph_id}["{domain_id} {safe_domain_name}"]')

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

        label = _sanitize_mermaid_label(_node_mermaid_label(n))
        lines.append(f'        {mermaid_id}["{label}"]')
    lines.append("    end")

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
        ext_label = _sanitize_mermaid_label(ext_domain)
        ext_maturity = _maturity_display(maturity)
        lines.append(f'    {ext_id}["({ext_maturity}) {ext_label}"]')
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

    # classDef 样式（所有都加 color:#000 确保黑字）
    lines.append("    classDef production fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000")
    lines.append("    classDef design fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000,stroke-dasharray: 5 5")
    lines.append("    classDef external_prod fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px,color:#000")
    lines.append(
        "    classDef external_design fill:#fce4ec,stroke:#880e4f,stroke-width:1px,color:#000,stroke-dasharray: 5 5"
    )

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


def _pad_to_width(s: str, width: int) -> str:
    """按显示宽度右填充空格到指定宽度。"""
    current = _display_width(s)
    if current >= width:
        return s
    return s + " " * (width - current)


def _truncate(text: str, max_len: int = 40) -> str:
    """截断文本到指定显示宽度，超出则加'...'。"""
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
    return result + "..."


def _layer_sort_key(layer: str) -> tuple[int, str]:
    """层级排序键：LAYER_ORDER 优先，其余按字母序，空值最后。"""
    if layer in LAYER_ORDER:
        return (LAYER_ORDER.index(layer), layer)
    elif layer:
        return (len(LAYER_ORDER), layer)
    else:
        return (len(LAYER_ORDER) + 1, "")


def _make_box(title: str, content_lines: list[str], width: int = BOX_WIDTH) -> list[str]:
    """生成ASCII box（带标题行和内容行）。

    结构:
    ┌──────┐
    │ title │  (居中)
    ├──────┤
    │ line │  (左对齐)
    └──────┘
    """
    inner = width
    top = "┌" + "─" * (inner + 2) + "┐"
    bottom = "└" + "─" * (inner + 2) + "┘"
    separator = "├" + "─" * (inner + 2) + "┤"

    lines = [top]
    # 标题行（居中）
    title_w = _display_width(title)
    if title_w >= inner:
        title_padded = _truncate(title, inner)
    else:
        left_pad = (inner - title_w) // 2
        title_padded = " " * left_pad + title
    lines.append(f"│ {_pad_to_width(title_padded, inner)} │")

    if content_lines:
        lines.append(separator)
        for line in content_lines:
            line_trunc = _truncate(line, inner)
            lines.append(f"│ {_pad_to_width(line_trunc, inner)} │")

    lines.append(bottom)
    return lines


def _arrow_down(width: int = BOX_WIDTH) -> list[str]:
    """生成向下箭头（层间连接）。"""
    center = width // 2 + 2  # +2 for "│ " prefix offset
    return [" " * center + "│", " " * center + "▼"]


def _display_edge_name(name: str, path: str, max_len: int = 28) -> str:
    """生成依赖边的节点显示名：优先 node_name，否则用 path 的 basename。"""
    if name:
        return _truncate(name, max_len)
    if path:
        # 用 basename 提高可读性（如 auto_dispatcher.py 而非完整路径）
        base = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        return _truncate(base, max_len)
    return "?"


# ---------------------------------------------------------------------------
# ASCII art 章节生成函数（合并自 generate_domain_architecture_diagram.py）
# ---------------------------------------------------------------------------


def generate_ascii_architecture_overview(
    domain_id: str, domain_name: str, nodes: list[dict]
) -> str:
    """生成ASCII架构分层视图（按 architecture_layer 分层显示）。

    - 按 architecture_layer 分组节点
    - 每层一个ASCII box，最多显示20个模块（超过显示前18个+"...还有N个"）
    - 层与层之间用箭头连接
    """
    # 按 architecture_layer 分组
    layer_groups: dict[str, list[dict]] = {}
    for n in nodes:
        layer = n["architecture_layer"] or ""
        layer_groups.setdefault(layer, []).append(n)

    # 排序层级
    sorted_layers = sorted(layer_groups.keys(), key=_layer_sort_key)

    if not sorted_layers:
        return "（无模块 / No modules）\n"

    lines: list[str] = []
    lines.append("```")
    lines.append("")

    for idx, layer in enumerate(sorted_layers):
        layer_nodes = layer_groups[layer]
        display_name = LAYER_DISPLAY.get(layer, layer) if layer else "未分类 / Unclassified"
        count = len(layer_nodes)

        # 最多显示20个模块（前18 + "...还有N个"）
        MAX_PER_LAYER = 20
        if count <= MAX_PER_LAYER:
            shown = layer_nodes
            more_count = 0
        else:
            shown = layer_nodes[: MAX_PER_LAYER - 2]
            more_count = count - (MAX_PER_LAYER - 2)

        # 构建内容行：每行一个模块标签（中文功能简介在前+成熟度中英文）
        content = []
        for n in shown:
            content.append(f"  {_node_ascii_label(n)}")

        if more_count > 0:
            content.append(f"  ...还有 {more_count} 个模块 / {more_count} more modules")

        title = f"{display_name} ({count} modules)"
        box_lines = _make_box(title, content)

        # 层间箭头
        if idx > 0:
            lines.extend(_arrow_down())

        lines.extend(box_lines)

    lines.append("")
    lines.append("```")
    return "\n".join(lines)


def generate_module_layered_list(nodes: list[dict]) -> str:
    """生成模块分层清单表格（按 architecture_layer 分组，中英文表头）。"""
    # 按 architecture_layer 分组
    layer_groups: dict[str, list[dict]] = {}
    for n in nodes:
        layer = n["architecture_layer"] or ""
        layer_groups.setdefault(layer, []).append(n)

    sorted_layers = sorted(layer_groups.keys(), key=_layer_sort_key)

    if not sorted_layers:
        return "（无模块 / No modules）\n"

    lines: list[str] = []

    MAX_PER_LAYER = 200
    for layer in sorted_layers:
        layer_nodes = layer_nodes_all = layer_groups[layer]
        display_name = LAYER_DISPLAY.get(layer, layer) if layer else "未分类 / Unclassified"

        lines.append(f"### {display_name} ({len(layer_nodes_all)} modules)")
        lines.append("")

        shown = layer_nodes_all[:MAX_PER_LAYER]
        lines.append(
            "| # | 模块路径 / Module Path | 模块名称 / Module Name | "
            "功能简介 / Description | 成熟度 / Maturity | 构建状态 / Build Status |"
        )
        lines.append("|:--:|---------|---------|---------|:---:|:---:|")

        for i, n in enumerate(shown, 1):
            path_display = _truncate(n["path"] or "", 60)
            name_display = _truncate(n["node_name"] or n["path"] or "", 40)
            node_type = n.get("node_type", "")

            # ARCH-052: 聚合节点——显示自身一行 + 展开 registry.yaml 列出内部 items
            if node_type in AGGREGATE_NODE_TYPES:
                registry_path = n["path"] or ""
                registry_data = _load_registry_items(registry_path)
                # 聚合节点本身一行
                # 从 registry.yaml 取 collection_name 作为 description
                collection_desc = ""
                try:
                    abs_reg = REPO_ROOT / registry_path
                    if abs_reg.exists():
                        reg_data = yaml.safe_load(abs_reg.read_text(encoding='utf-8', errors='replace'))
                        if isinstance(reg_data, dict):
                            collection_desc = reg_data.get("collection_name", "") or ""
                            items_count = len(registry_data)
                            collection_desc = f"[聚合节点 / Aggregated] {collection_desc} ({items_count} items)"
                except Exception:
                    pass
                lines.append(
                    f"| {i} | {path_display} | {name_display} | "
                    f"{collection_desc} | {_maturity_display(n['design_maturity'])} | {_build_status_display(n['build_status'])} |"
                )
                # 展开内部 items（最多显示前 100 个，避免表格过长）
                MAX_ITEMS = 100
                for j, item in enumerate(registry_data[:MAX_ITEMS], 1):
                    item_file = item.get("file", "") or ""
                    item_desc = (item.get("description", "") or "").strip().split('\n')[0].strip()
                    item_desc = _truncate(item_desc, 80)
                    item_path_display = _truncate(f"  ↳ {item_file}", 60)
                    item_name_display = _truncate(item.get("gate_id", "") or item.get("title", "") or "", 40)
                    lines.append(
                        f"| ↳{j} | {item_path_display} | {item_name_display} | "
                        f"{item_desc} | - | - |"
                    )
                if len(registry_data) > MAX_ITEMS:
                    lines.append(f"| | | | > (仅显示前 {MAX_ITEMS} 个 items，共 {len(registry_data)} 个) | | |")
            else:
                # 普通节点——保持原逻辑（docstring 提取）
                # 对 .yaml 文件也尝试提取 description（ARCH-052 增强）
                desc_display = _extract_docstring_first_line(n["path"] or "")
                if not desc_display and n["path"] and n["path"].endswith(('.yaml', '.yml')):
                    desc_display = _extract_yaml_description(n["path"])
                lines.append(
                    f"| {i} | {path_display} | {name_display} | "
                    f"{desc_display} | {_maturity_display(n['design_maturity'])} | {_build_status_display(n['build_status'])} |"
                )

        if len(layer_nodes_all) > MAX_PER_LAYER:
            lines.append(f"\n> (仅显示前 {MAX_PER_LAYER} 个模块，共 {len(layer_nodes_all)} 个)")
        lines.append("")

    return "\n".join(lines)


def generate_ascii_dependency_graph(edges: list[dict]) -> str:
    """生成ASCII依赖关系图（按 dep_type 分组显示域内依赖边）。

    - 按 dep_type 分组
    - 最多显示50条依赖边（超过显示前48条+"...还有N条"）
    - 使用 → 表示方向
    """
    if not edges:
        return "（无域内依赖 / No internal dependencies）\n"

    # 按 dep_type 分组
    type_groups: dict[str, list[dict]] = {}
    for e in edges:
        dtype = e["dep_type"] or "unknown"
        type_groups.setdefault(dtype, []).append(e)

    # 排序 dep_type（按数量降序）
    sorted_types = sorted(type_groups.keys(), key=lambda t: -len(type_groups[t]))

    MAX_EDGES = 50
    total = len(edges)

    lines: list[str] = []
    lines.append("```")
    lines.append("")

    # 总览 box
    overview_title = f"依赖关系图 / Dependency Graph (共 {total} 条 / {total} edges)"
    overview_content = [f"  依赖类型数 / Dependency Types: {len(sorted_types)}"]
    for dtype in sorted_types:
        overview_content.append(
            f"  [{dtype}]: {len(type_groups[dtype])} 条 / edges"
        )
    lines.extend(_make_box(overview_title, overview_content))
    lines.append("")

    # 分组详情
    shown_total = 0
    for dtype in sorted_types:
        group_edges = type_groups[dtype]
        remaining = MAX_EDGES - shown_total
        # 剩余空间不足以显示至少1条边时，输出摘要行而非空box
        if remaining <= 1:
            lines.append(f"**[{dtype}]** ({len(group_edges)} 条 / edges) — 已达显示上限，省略 / limit reached")
            lines.append("")
            continue

        if len(group_edges) <= remaining:
            shown = group_edges
            more = 0
        else:
            shown = group_edges[: remaining - 1]
            more = len(group_edges) - (remaining - 1)

        shown_total += len(shown)

        group_title = f"[{_dep_type_display(dtype)}] ({len(group_edges)} 条 / edges)"
        content = []
        for e in shown:
            from_name = _display_edge_name(e["from_name"], e["from_path"])
            to_name = _display_edge_name(e["to_name"], e["to_path"])
            content.append(f"  {from_name} → {to_name}")

        if more > 0:
            content.append(f"  ...还有 {more} 条 / {more} more edges")

        lines.extend(_make_box(group_title, content))
        lines.append("")

    if total > MAX_EDGES:
        lines.append(f"> (最多显示前 {MAX_EDGES} 条依赖边，共 {total} 条)")
        lines.append("")

    lines.append("```")
    return "\n".join(lines)


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

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 统计
    design_count = sum(1 for n in nodes if n["design_maturity"] == "design")
    production_count = sum(1 for n in nodes if n["design_maturity"] == "production")
    prototype_count = sum(1 for n in nodes if n["design_maturity"] == "prototype")
    capacity_status = "正常" if info["production_nodes"] <= info["max_modules"] else "超容"
    total_outgoing = sum(d["count"] for d in outgoing_agg)
    total_incoming = sum(d["count"] for d in incoming_agg)

    domain_name_zh = get_domain_name_zh(domain_id, info["domain_name"])
    domain_name_en = get_domain_name_en(domain_id)

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
    lines.append(f"# {number:02d}_{domain_id.replace('-', '_').lower()} / {domain_name_zh} / {domain_name_en}")
    lines.append("")
    lines.append(f"> **文档作用 / Purpose**: 展示 {domain_name_zh}（{domain_id}）功能域的模块清单、域内依赖关系、跨域依赖关系、架构分层视图，供架构审查和域治理参考。")
    lines.append("")
    lines.append(f"> 本文档由 generate_domain_doc.py 从 {DB_DISPLAY_NAME} 自动生成")
    lines.append(f"> 最后更新: {now}")
    lines.append(f"> 数据源: {DB_DISPLAY_NAME} nodes表 + edges表")
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
    lines.append(f"| 原型态模块 | {prototype_count} | Prototype Modules | {prototype_count} |")
    lines.append(f"| 生产态模块 | {production_count} | Production Modules | {production_count} |")
    lines.append(
        f"| 容量 | {info['production_nodes']}/{info['max_modules']} ({capacity_status}) | "
        f"Capacity | {info['production_nodes']}/{info['max_modules']} ({capacity_status}) |"
    )
    if info["description"]:
        lines.append(f"| 描述 | {info['description']} | Description | {info['description']} |")
    lines.append("")

    # 域内依赖图（内嵌 Mermaid，分页显示全部节点）
    lines.append("## 域内依赖图 / Internal Dependency Diagram")
    lines.append("")
    lines.append("> 依赖图内嵌在本文档中，IDE 可直接渲染显示。每30个节点一组分页显示。")
    lines.append(">")
    lines.append("> **图例说明 / Legend**：")
    lines.append("> - **实线边框 = 运营态模块**（production，已上线运行）")
    lines.append("> - **虚线边框 = 设计态模块**（design，还在设计中）")
    lines.append("> - **实线箭头 = 运营态依赖**（已生效的依赖关系）")
    lines.append("> - **虚线箭头 = 设计态依赖**（计划中的依赖关系）")
    lines.append("")

    PAGE_SIZE = 30
    total_pages = (len(nodes) + PAGE_SIZE - 1) // PAGE_SIZE if nodes else 1
    for page_idx in range(total_pages):
        start = page_idx * PAGE_SIZE
        end = start + PAGE_SIZE
        page_nodes = nodes[start:end]
        page_node_ids = {n["node_id"] for n in page_nodes}
        # 跨域边详情（仅涉及当前页节点）
        page_outgoing, page_incoming = get_cross_domain_edges_detail(conn, domain_id, [n["node_id"] for n in page_nodes])

        if total_pages > 1:
            lines.append(f"### 第 {page_idx + 1} 页 / 共 {total_pages} 页 / Page {page_idx + 1} of {total_pages}")
            lines.append("")

        mermaid_code = generate_internal_mermaid(
            domain_id, domain_name_zh, page_nodes, edges, page_outgoing, page_incoming
        )
        lines.append("```mermaid")
        lines.append(mermaid_code)
        lines.append("```")
        lines.append("")

    # 跨域依赖（中英文对照）
    lines.append("## 跨域依赖 / Cross-domain Dependencies")
    lines.append("")

    # 本域依赖的其他域
    lines.append("### 本域依赖的其他域（出边）/ Depends On")
    lines.append("")
    if outgoing_agg:
        lines.append("| 目标域 / Target Domain | 依赖数 / Count | 依赖类型 / Type |")
        lines.append("|--------|:---:|---------|")
        for d in outgoing_agg:
            lines.append(f"| {d['target_domain']} | {d['count']} | {_dep_types_display(d['dep_types'])} |")
    else:
        lines.append("无跨域出边依赖 / No cross-domain outgoing dependencies")
    lines.append("")

    # 依赖本域的其他域
    lines.append("### 依赖本域的其他域（入边）/ Depended By")
    lines.append("")
    if incoming_agg:
        lines.append("| 源域 / Source Domain | 依赖数 / Count | 依赖类型 / Type |")
        lines.append("|------|:---:|---------|")
        for d in incoming_agg:
            lines.append(f"| {d['source_domain']} | {d['count']} | {_dep_types_display(d['dep_types'])} |")
    else:
        lines.append("无跨域入边依赖 / No cross-domain incoming dependencies")
    lines.append("")

    # 架构分层视图（ASCII art，合并自 generate_domain_architecture_diagram.py）
    lines.append("## 架构分层视图 / Architecture Overview")
    lines.append("")
    lines.append(
        f"> 按 architecture_layer 分层显示 {domain_name_zh}（{domain_id}）的模块分布。"
        f"共 {len(nodes)} 个模块 / {len(nodes)} modules。"
    )
    lines.append("")
    lines.append(generate_ascii_architecture_overview(domain_id, domain_name_zh, nodes))
    lines.append("")

    # 模块分层清单（按 architecture_layer 分组，合并自 generate_domain_architecture_diagram.py）
    lines.append("## 模块分层清单 / Module Layered List")
    lines.append("")
    lines.append(
        f"> 按 architecture_layer 分组的模块清单（共 {len(nodes)} 个模块 / {len(nodes)} modules）。"
    )
    lines.append("")
    lines.append(generate_module_layered_list(nodes))

    # 依赖关系图（ASCII art，合并自 generate_domain_architecture_diagram.py）
    lines.append("## 依赖关系图 / Dependency Graph")
    lines.append("")
    lines.append(
        f"> 域内模块依赖关系（共 {len(edges)} 条 / {len(edges)} edges）。"
        "按依赖类型分组，使用 → 表示方向。"
    )
    lines.append("")
    lines.append(generate_ascii_dependency_graph(edges))
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
        "`[prototype]`=原型 / `[unknown]`=未知"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main() -> None:
    """入口：生成指定域的 MD 文档（含 Mermaid 依赖图 + ASCII art 架构图）。"""
    parser = argparse.ArgumentParser(
        description="G2+G10 合并: 生成域架构文档(含内嵌Mermaid依赖图+ASCII art架构图+分层清单+依赖关系图)"
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

    conn = get_depgraph_pg_connection(autocommit=True)
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
                    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
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
        else:
            # 生成单个域的文档
            number = numbering_map.get(args.domain_id, 0)
            content = generate_domain_doc(args.domain_id, conn, number)
            if not content:
                sys.exit(2)
            safe_name = args.domain_id.replace("-", "_").lower()
            out_path = output_dir / f"{number:02d}_{safe_name}.md"
            _atomic_write(out_path, content)
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
