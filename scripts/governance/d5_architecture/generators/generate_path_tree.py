# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_path_tree
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""G1: 从 depgraph.db arch_directory_tree 表 + 文件系统生成 docs/02_enterprise_architecture/ 目录树(中英文)输出到 generated/

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_path_tree
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph.db+文件系统;输出到generated/目录;仅展示 docs/02_enterprise_architecture/ 子树
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看generated/path_tree_zh.md+path_tree_en.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1;查询失败→exit 2
[TESTS] tests/test_dm200910_generators.py
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

DEPGRAPH_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
PROJECT_ROOT = Path("D:/ZephyrAlpha")
OUTPUT_DIR = Path("D:/ZephyrAlpha/docs/02_enterprise_architecture/01_global_architecture_diagram")
TARGET_SUBTREE = "docs/02_enterprise_architecture"

# 全项目顶级目录及中文描述
TOP_LEVEL_DIRS_ZH = {
    "src": "源代码",
    "scripts": "脚本",
    "tests": "测试",
    "docs": "文档",
    "config": "配置",
    "data": "数据",
}

# 全项目模式下需要跳过的目录（噪声/缓存/构建产物）
SKIP_DIRS_FULL = {
    "__pycache__", ".git", ".ailocks", ".audit_cache", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox", ".venv", "venv",
    ".idea", ".vs", ".eggs", "cache", "telemetry", ".trae",
}


def build_tree_rows(conn: sqlite3.Connection, scope: str = "arch") -> list[dict]:
    """从 arch_directory_tree 表查询目录记录，按 path 排序。

    scope='arch': 仅 docs/02_enterprise_architecture 下的目录
    scope='full': 全项目所有目录（过滤噪声目录）
    """
    if scope == "full":
        cur = conn.execute(
            "SELECT path, parent_path, path_type, domain_id, build_status, design_maturity "
            "FROM arch_directory_tree "
            "WHERE path NOT LIKE '%/' "
            "ORDER BY path",
        )
    else:
        cur = conn.execute(
            "SELECT path, parent_path, path_type, domain_id, build_status, design_maturity "
            "FROM arch_directory_tree "
            "WHERE (path = ? OR path LIKE ?) AND path NOT LIKE '%/' "
            "ORDER BY path",
            (TARGET_SUBTREE, TARGET_SUBTREE + "/%"),
        )
    rows = []
    for r in cur.fetchall():
        path = r[0] or ""
        # 全项目模式下过滤噪声目录
        if scope == "full":
            parts = path.split("/")
            if any(p in SKIP_DIRS_FULL for p in parts):
                continue
        rows.append(
            {
                "path": path,
                "parent_path": r[1] or "",
                "path_type": r[2] or "",
                "domain_id": r[3] or "",
                "build_status": r[4] or "",
                "design_maturity": r[5] or "",
            }
        )
    return rows


def build_tree_structure(rows: list[dict], scope: str = "arch") -> dict:
    """将扁平记录列表构建为嵌套树结构，并从文件系统补充缺失的目录。

    返回: {path: {"children": set(), "domain_id": str, "data": dict}}
    """
    tree: dict[str, dict] = {}
    for row in rows:
        path = row["path"]
        if not path:
            continue
        # 过滤文件系统上不存在的目录（数据库可能有陈旧条目）
        if not (PROJECT_ROOT / path).is_dir():
            continue
        tree[path] = {
            "children": set(),
            "domain_id": row["domain_id"],
            "data": row,
        }
    # 从文件系统补充数据库中缺失的目录
    if scope == "full":
        # 全项目模式：补充所有顶级目录
        for top_dir in TOP_LEVEL_DIRS_ZH:
            if (PROJECT_ROOT / top_dir).is_dir():
                _supplement_from_filesystem(tree, top_dir)
    else:
        _supplement_from_filesystem(tree, TARGET_SUBTREE)
    # 建立 parent->children 关系
    for path, node in tree.items():
        parent = node["data"]["parent_path"]
        if parent and parent in tree:
            tree[parent]["children"].add(path)
    return tree


def _supplement_from_filesystem(tree: dict, root_rel_path: str) -> None:
    """从文件系统扫描补充数据库中缺失的目录（递归）。"""
    fs_root = PROJECT_ROOT / root_rel_path
    if not fs_root.is_dir():
        return
    for entry in sorted(fs_root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        rel_path = f"{root_rel_path}/{entry.name}"
        if rel_path not in tree:
            tree[rel_path] = {
                "children": set(),
                "domain_id": "",
                "data": {
                    "path": rel_path,
                    "parent_path": root_rel_path,
                    "path_type": "directory",
                    "domain_id": "",
                    "build_status": "",
                    "design_maturity": "",
                },
            }
        _supplement_from_filesystem(tree, rel_path)


# docs/02_enterprise_architecture 直接子目录的指定排序顺序
_ARCH_SUBDIR_ORDER = [
    "00_overview_entry",
    "01_global_architecture_diagram",
    "02_domain_architecture_docs",
    "03_governance_reports",
    "04_architecture_principles_decisions",
    "generated",
    "_archive",
    "archive",
    "sample",
    "target_architecture",
]


def _sort_children_key(child_path: str, parent_path: str) -> tuple:
    """生成子节点排序键。

    docs/02_enterprise_architecture 下的直接子目录按指定编号顺序排列，
    其他目录按字母顺序排列。
    """
    if parent_path and child_path.startswith(parent_path + "/"):
        child_name = child_path[len(parent_path) + 1:]
    else:
        child_name = child_path.rsplit("/", 1)[-1] if "/" in child_path else child_path

    if parent_path == "docs/02_enterprise_architecture":
        if child_name in _ARCH_SUBDIR_ORDER:
            return (0, _ARCH_SUBDIR_ORDER.index(child_name), child_name)
        return (1, 0, child_name)

    return (0, 0, child_name)


# 目录功能描述（中英文）——参考 path_tree_sample.md 格式
DIR_DESCRIPTIONS_ZH = {
    "00_overview_entry": "总览入口：导航索引",
    "01_global_architecture_diagram": "全局架构图：路径树/能力热图/跨域矩阵",
    "02_domain_architecture_docs": "域架构文档：各功能域详细设计",
    "03_governance_reports": "治理报告：容量/约束/设计态对比",
    "04_architecture_principles_decisions": "架构原则与决策：设计规范",
    "_archive": "临时归档：待处理的旧文档",
    "archive": "正式归档：历史文档",
    "sample": "样板文件：文档格式参考",
    "generated": "自动生成产物：依赖图等",
    "domains": "域依赖图：各功能域Mermaid图",
    "target_architecture": "目标架构：架构设计文档",
    "architecture_model": "架构模型：契约/事件/分层模型",
    "diagrams": "架构图：Mermaid图表",
    "contracts": "契约：跨层契约定义",
    "cross_cutting": "横切关注点：能力热图/不变量",
    "domain": "领域模型：DDD模型",
    "events": "事件：领域事件定义",
    "layers": "分层：架构分层定义",
    "technology": "技术：技术栈选型",
}

DIR_DESCRIPTIONS_EN = {
    "00_overview_entry": "Overview entry: navigation index",
    "01_global_architecture_diagram": "Global architecture: path tree/heatmap/matrix",
    "02_domain_architecture_docs": "Domain architecture docs: per-domain design",
    "03_governance_reports": "Governance reports: capacity/constraints/design-vs-prod",
    "04_architecture_principles_decisions": "Architecture principles & decisions",
    "_archive": "Temporary archive: pending old docs",
    "archive": "Formal archive: historical docs",
    "sample": "Sample files: format reference",
    "generated": "Generated artifacts: dependency graphs",
    "domains": "Domain dependency graphs: Mermaid per domain",
    "target_architecture": "Target architecture: design documents",
    "architecture_model": "Architecture model: contracts/events/layers",
    "diagrams": "Diagrams: Mermaid charts",
    "contracts": "Contracts: cross-layer definitions",
    "cross_cutting": "Cross-cutting: heatmap/invariants",
    "domain": "Domain model: DDD model",
    "events": "Events: domain event definitions",
    "layers": "Layers: architecture layer definitions",
    "technology": "Technology: tech stack selection",
}

# 最大显示深度（相对于 docs/02_enterprise_architecture）
# depth 0=根, 1=00_overview_entry等, 2=target_architecture/architecture_model, 3=architecture_model/contracts(不展开)
MAX_DISPLAY_DEPTH = 3


def get_dir_description(dir_name: str, lang: str) -> str:
    """获取目录功能描述。"""
    if lang == "zh":
        return DIR_DESCRIPTIONS_ZH.get(dir_name, "")
    return DIR_DESCRIPTIONS_EN.get(dir_name, "")


def get_dir_files(dir_rel_path: str) -> list[str]:
    """从文件系统读取目录下的直接文件（非递归），返回排序后的文件名列表。

    隐藏文件（以 . 开头）被排除。
    """
    fs_path = PROJECT_ROOT / dir_rel_path
    if not fs_path.is_dir():
        return []
    files = [f.name for f in fs_path.iterdir() if f.is_file() and not f.name.startswith(".")]
    return sorted(files)


def get_file_summary(files: list[str], lang: str) -> str:
    """统计文件类型，返回摘要字符串。

    格式: (包含N个文件: .ext1(count1), .ext2(count2))
    最多显示前5种文件类型，按数量降序排列。无文件时返回空字符串。
    """
    if not files:
        return ""
    ext_counter: Counter = Counter()
    for f in files:
        ext = Path(f).suffix.lower() if Path(f).suffix else "(无扩展名)"
        ext_counter[ext] += 1
    sorted_exts = sorted(ext_counter.items(), key=lambda x: (-x[1], x[0]))[:5]
    parts = [f"{ext}({cnt})" for ext, cnt in sorted_exts]
    detail = ", ".join(parts)
    if lang == "zh":
        return f"(包含{len(files)}个文件: {detail})"
    return f"({len(files)} files: {detail})"


def _limit_files(files: list[str], lang: str) -> list[str]:
    """显示所有文件，不截断。"""
    return list(files)


# 文件名 → 中文功能描述映射
FILE_DESC_ZH = {
    # 通用文件
    "index.md": "索引",
    "readme.md": "说明",
    "navigation_index.md": "导航索引",
    ".gitkeep": "占位文件",
    # 01_global_architecture_diagram
    "capability_heatmap.md": "能力热图",
    "cross_domain_matrix.md": "跨域矩阵",
    "integration_topology.md": "集成拓扑",
    "path_tree_en.md": "路径树(英文)",
    "path_tree_zh.md": "路径树(中文)",
    "runtime_plane_mapping.md": "运行时平面映射",
    # 03_governance_reports
    "capacity_report.md": "容量报告",
    "constraint_violations.md": "约束违规",
    "design_vs_production.md": "设计态vs运营态",
    "orphan_cleanup_audit.md": "孤儿清理审计",
    "_update_audit_doc.py": "审计文档更新脚本",
    # sample
    "00_overview_entry_sample.md": "总览入口样板",
    "04_architecture_principles_decisions_sample.md": "架构原则样板",
    "05_manual_architecture_views_sample.md": "手工架构图样板",
    "16_d_trading_sample.md": "交易域样板",
    "6_手工架构图_样板.mmd": "手工架构图样板",
    "integration_topology_sample.md": "集成拓扑样板",
    "path_tree_sample.md": "路径树样板",
    # target_architecture 根目录文件
    "application_architecture.md": "应用架构",
    "architecture_endgame_locked.md": "架构终态锁定",
    "architecture_principles.md": "架构原则",
    "business_architecture.md": "业务架构",
    "data_architecture.md": "数据架构",
    "dimension_audit_matrix.md": "维度审计矩阵",
    "frontend_architecture.md": "前端架构",
    "governance_architecture.md": "治理架构",
    "information_architecture.md": "信息架构",
    "integration_architecture.md": "集成架构",
    "operations_architecture.md": "运营架构",
    "overview.md": "概览",
    "revision_history.md": "修订历史",
    "runtime_planes.md": "运行时平面",
    "security_architecture.md": "安全架构",
    "technology_architecture.md": "技术架构",
    "session_carryover_schema.md": "会话延续Schema",
    "ai_team_mode_full_config.md": "AI团队模式配置",
    "architecture_diagram_construction_plan.md": "架构图施工计划",
    "architecture_upgrade_discussion.md": "架构升级讨论",
    "contract_dedup_analysis.md": "契约去重分析",
    "contract_dedup_integration_analysis.md": "契约去重集成分析",
    "core_function_dependency_design.md": "核心功能依赖设计",
    "dependency_architecture_panorama.md": "依赖架构全景",
    "migration_registry.yaml": "迁移注册表",
    "phase_d_ai_prompts.md": "Phase D AI提示词",
    "phase_d_full_test_construction_plan.md": "Phase D全量测试施工计划",
    "ssot_authority_map.md": "SSoT权威映射",
    "t18_implementation_plan.md": "T18实施计划",
    # architecture_model
    "module_id_registry.yaml": "模块ID注册表",
    "ddd_model.yaml": "DDD领域模型",
    "domain_events.yaml": "领域事件",
    "consumer_registry.yaml": "消费者注册表",
    "cross_layer_contracts.yaml": "跨层契约",
    "invariants.yaml": "不变量",
    "runtime_planes.yaml": "运行时平面配置",
    "capability_heatmap.yaml": "能力热图配置",
    "technology_landscape.yaml": "技术全景",
    "vibe_coding_infrastructure_tech_stack.yaml": "Vibe Coding技术栈",
    # _archive
    "architecture_decisions_pending.md": "待定架构决策",
    "phase4b_cleanup_construction_plan.md": "Phase4b清理施工计划",
}

# 文件名 → 英文功能描述映射
FILE_DESC_EN = {
    "index.md": "Index",
    "readme.md": "README",
    "navigation_index.md": "Navigation index",
    ".gitkeep": "Placeholder",
    "capability_heatmap.md": "Capability heatmap",
    "cross_domain_matrix.md": "Cross-domain matrix",
    "integration_topology.md": "Integration topology",
    "path_tree_en.md": "Path tree (English)",
    "path_tree_zh.md": "Path tree (Chinese)",
    "runtime_plane_mapping.md": "Runtime plane mapping",
    "capacity_report.md": "Capacity report",
    "constraint_violations.md": "Constraint violations",
    "design_vs_production.md": "Design vs production",
    "orphan_cleanup_audit.md": "Orphan cleanup audit",
    "_update_audit_doc.py": "Audit doc update script",
    "application_architecture.md": "Application architecture",
    "architecture_endgame_locked.md": "Architecture endgame locked",
    "architecture_principles.md": "Architecture principles",
    "business_architecture.md": "Business architecture",
    "data_architecture.md": "Data architecture",
    "dimension_audit_matrix.md": "Dimension audit matrix",
    "frontend_architecture.md": "Frontend architecture",
    "governance_architecture.md": "Governance architecture",
    "information_architecture.md": "Information architecture",
    "integration_architecture.md": "Integration architecture",
    "operations_architecture.md": "Operations architecture",
    "overview.md": "Overview",
    "revision_history.md": "Revision history",
    "runtime_planes.md": "Runtime planes",
    "security_architecture.md": "Security architecture",
    "technology_architecture.md": "Technology architecture",
    "session_carryover_schema.md": "Session carryover schema",
    "module_id_registry.yaml": "Module ID registry",
    "ddd_model.yaml": "DDD domain model",
    "domain_events.yaml": "Domain events",
    "consumer_registry.yaml": "Consumer registry",
    "cross_layer_contracts.yaml": "Cross-layer contracts",
    "invariants.yaml": "Invariants",
    "runtime_planes.yaml": "Runtime planes config",
    "capability_heatmap.yaml": "Capability heatmap config",
    "technology_landscape.yaml": "Technology landscape",
    "vibe_coding_infrastructure_tech_stack.yaml": "Vibe Coding tech stack",
}


def get_file_description(filename: str, lang: str) -> str:
    """获取文件的中文/英文功能描述。

    对于域文档（如 01_d_infra_ops.md），自动从域名映射表生成中文。
    对于其他文件，从 FILE_DESC_ZH/EN 映射表获取。
    """
    # 先查固定映射表
    if lang == "zh":
        desc = FILE_DESC_ZH.get(filename, "")
    else:
        desc = FILE_DESC_EN.get(filename, "")
    if desc:
        return desc

    # 域文档自动生成：01_d_infra_ops.md → 基础设施运维
    import re
    # 先匹配 _architecture.md 后缀（避免贪婪匹配吞掉域名）
    m = re.match(r"^\d+_d_([a-z_]+?)_architecture\.md$", filename)
    if m:
        domain_key = "D-" + m.group(1).upper()
        try:
            from domain_name_mapping import get_domain_name_zh
            domain_zh = get_domain_name_zh(domain_key, "")
            if domain_zh:
                return f"{domain_zh}架构图" if lang == "zh" else f"{domain_zh} architecture"
        except ImportError:
            pass

    # 再匹配普通域文档 .md
    m = re.match(r"^\d+_d_([a-z_]+)\.md$", filename)
    if m:
        domain_key = "D-" + m.group(1).upper()
        try:
            from domain_name_mapping import get_domain_name_zh
            domain_zh = get_domain_name_zh(domain_key, "")
            if domain_zh:
                return domain_zh if lang == "zh" else domain_zh
        except ImportError:
            pass

    # 域依赖图：d_infra_ops_dependency.mmd
    m = re.match(r"^d_([a-z_]+)_dependency\.mmd$", filename)
    if m:
        domain_key = "D-" + m.group(1).upper()
        try:
            from domain_name_mapping import get_domain_name_zh
            domain_zh = get_domain_name_zh(domain_key, "")
            if domain_zh:
                return f"{domain_zh}依赖图" if lang == "zh" else f"{domain_zh} dependency"
        except ImportError:
            pass

    # domain_index.md
    if filename == "domain_index.md":
        return "域索引" if lang == "zh" else "Domain index"

    # 通用后缀推断
    if filename.endswith("_sample.md"):
        base = filename.replace("_sample.md", "")
        return f"{base}样板" if lang == "zh" else f"{base} sample"
    if filename.endswith(".mmd"):
        base = filename.replace(".mmd", "")
        return f"{base}图" if lang == "zh" else f"{base} diagram"
    if filename.endswith(".yaml"):
        base = filename.replace(".yaml", "")
        return f"{base}配置" if lang == "zh" else f"{base} config"
    if filename.endswith(".py"):
        base = filename.replace(".py", "")
        return f"{base}脚本" if lang == "zh" else f"{base} script"

    return ""


def render_tree(tree: dict, root_path: str, prefix: str, lines: list[str], lang: str, depth: int = 0) -> None:
    """递归渲染树状图（显示目录+描述+文件统计，不显示冗余域标签）。"""
    if root_path not in tree:
        return

    dir_name = root_path.rsplit("/", 1)[-1] if "/" in root_path else root_path
    desc = get_dir_description(dir_name, lang)
    files = get_dir_files(root_path)
    file_summary = get_file_summary(files, lang)

    desc_tag = f"  — {desc}" if desc else ""
    summary_tag = f"  {file_summary}" if file_summary else ""
    lines.append(f"{prefix}{dir_name}/{desc_tag}{summary_tag}")
    _render_children(tree, root_path, prefix, lines, lang, depth)


def _render_children(tree: dict, parent_path: str, prefix: str, lines: list[str], lang: str, depth: int) -> None:
    """渲染子节点（子目录在前，文件在后），深度超过MAX_DISPLAY_DEPTH时不展开子目录。"""
    if parent_path not in tree:
        return
    node = tree[parent_path]
    child_dirs = sorted(node["children"], key=lambda c: _sort_children_key(c, parent_path))
    files = get_dir_files(parent_path)
    files_display = _limit_files(files, lang)

    all_items: list[tuple[str, bool]] = [(d, True) for d in child_dirs] + [
        (f, False) for f in files_display
    ]
    total = len(all_items)

    for i, (item, is_dir) in enumerate(all_items):
        is_last = i == total - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")

        if is_dir and item in tree:
            child_name = item.rsplit("/", 1)[-1] if "/" in item else item
            child_desc = get_dir_description(child_name, lang)
            child_files = get_dir_files(item)
            child_summary = get_file_summary(child_files, lang)
            desc_tag = f"  — {child_desc}" if child_desc else ""
            summary_tag = f"  {child_summary}" if child_summary else ""
            lines.append(f"{prefix}{connector}{child_name}/{desc_tag}{summary_tag}")
            # 深度控制：超过MAX_DISPLAY_DEPTH不展开子目录
            if depth < MAX_DISPLAY_DEPTH:
                _render_children(tree, item, child_prefix, lines, lang, depth + 1)
        else:
            # 文件名后添加中文功能描述
            file_desc = get_file_description(item, lang)
            desc_tag = f"  — {file_desc}" if file_desc else ""
            lines.append(f"{prefix}{connector}{item}{desc_tag}")


def find_roots(tree: dict) -> list[str]:
    """找到所有根节点（没有父节点或父节点不在树中的节点）。"""
    roots = []
    for path, node in tree.items():
        parent = node["data"]["parent_path"]
        if not parent or parent not in tree:
            roots.append(path)
    return sorted(roots)


def generate_path_tree(lang: str, conn: sqlite3.Connection) -> str:
    """生成路径树内容。

    lang: 'zh' 或 'en'
    """
    rows = build_tree_rows(conn)
    tree = build_tree_structure(rows)
    roots = find_roots(tree)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if lang == "zh":
        header = f"""# ZephyrAlpha 架构文档目录树 / Architecture Docs Directory Tree

> **文档作用**: 以树状结构展示 docs/02_enterprise_architecture/ 目录下的所有子目录、文件及所属功能域，用于快速定位架构文档。
> 本文档由 generate_path_tree.py 从 depgraph.db + 文件系统自动生成 / Auto-generated by generate_path_tree.py from depgraph.db + filesystem
> 最后更新: {now} / Last updated: {now}
> 数据源: depgraph.db arch_directory_tree 表（目录）+ 文件系统扫描（文件）/ Data source: depgraph.db arch_directory_tree (dirs) + filesystem scan (files)

## 架构文档目录树 / Architecture Docs Directory Tree

"""
        stats_title = "## 统计 / Statistics"
        total_dirs_label = "总目录数 / Total directories"
        total_files_label = "总文件数 / Total files"
        total_domains_label = "涉及域数 / Domains involved"
    else:
        header = f"""# ZephyrAlpha Architecture Docs Directory Tree / 架构文档目录树

> **Purpose**: Display all subdirectories, files and their functional domains under docs/02_enterprise_architecture/ in a tree structure for quick architecture document location.
> Auto-generated by generate_path_tree.py from depgraph.db + filesystem / 本文档由 generate_path_tree.py 从 depgraph.db + 文件系统自动生成
> Last updated: {now} / 最后更新: {now}
> Data source: depgraph.db arch_directory_tree (dirs) + filesystem scan (files) / 数据源: depgraph.db arch_directory_tree（目录）+ 文件系统扫描（文件）

## Architecture Docs Directory Tree / 架构文档目录树

"""
        stats_title = "## Statistics / 统计"
        total_dirs_label = "Total directories / 总目录数"
        total_files_label = "Total files / 总文件数"
        total_domains_label = "Domains involved / 涉及域数"

    lines = [header.rstrip()]

    # 树形图平铺在文档中（不用代码块），每行末尾加两个空格实现硬换行
    # 前导空格用 &nbsp; 替代，防止 Markdown 压缩缩进
    for root in roots:
        render_tree(tree, root, "", lines, lang)
        lines.append("")

    # 统计
    domains_involved = set()
    for row in rows:
        if row["domain_id"]:
            domains_involved.add(row["domain_id"])

    lines.append(stats_title)
    total_files = sum(len(get_dir_files(row["path"])) for row in rows)
    lines.append(f"- {total_dirs_label}: {len(rows)}")
    lines.append(f"- {total_files_label}: {total_files}")
    lines.append(f"- {total_domains_label}: {len(domains_involved)}")
    lines.append("")

    # 后处理：每行末尾加两个空格（硬换行），前导空格用 &nbsp; 替代
    processed_lines = []
    for line in lines:
        if line and not line.startswith("#") and not line.startswith(">") and not line.startswith("-"):
            # 替换前导空格为 &nbsp;（保留树形缩进）
            stripped = line.lstrip(" ")
            leading_spaces = len(line) - len(stripped)
            if leading_spaces > 0:
                line = "&nbsp;" * leading_spaces + stripped
            # 末尾加两个空格（硬换行）
            line = line + "  "
        processed_lines.append(line)

    return "\n".join(processed_lines)


def main() -> None:
    """入口：生成中英文物理路径树。"""
    parser = argparse.ArgumentParser(description="G1: 生成项目物理路径树(中英文)")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--lang", type=str, choices=["zh", "en", "both"], default="both", help="生成语言")
    args = parser.parse_args()

    if not DEPGRAPH_DB.exists():
        print(f"ERROR: depgraph.db 不存在: {DEPGRAPH_DB}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DEPGRAPH_DB))
    try:
        if args.lang in ("zh", "both"):
            content = generate_path_tree("zh", conn)
            out_path = output_dir / "path_tree_zh.md"
            out_path.write_text(content, encoding="utf-8")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")

        if args.lang in ("en", "both"):
            content = generate_path_tree("en", conn)
            out_path = output_dir / "path_tree_en.md"
            out_path.write_text(content, encoding="utf-8")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
