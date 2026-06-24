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


def build_tree_rows(conn: sqlite3.Connection) -> list[dict]:
    """从 arch_directory_tree 表查询 docs/02_enterprise_architecture 下的目录记录，按 path 排序。

    过滤掉带尾斜杠的设计态噪声条目（path 以 '/' 结尾且 parent_path 为空）。
    """
    cur = conn.execute(
        "SELECT path, parent_path, path_type, domain_id, build_status, design_maturity "
        "FROM arch_directory_tree "
        "WHERE (path = ? OR path LIKE ?) AND path NOT LIKE '%/' "
        "ORDER BY path",
        (TARGET_SUBTREE, TARGET_SUBTREE + "/%"),
    )
    rows = []
    for r in cur.fetchall():
        rows.append(
            {
                "path": r[0] or "",
                "parent_path": r[1] or "",
                "path_type": r[2] or "",
                "domain_id": r[3] or "",
                "build_status": r[4] or "",
                "design_maturity": r[5] or "",
            }
        )
    return rows


def build_tree_structure(rows: list[dict]) -> dict:
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
    # 从文件系统补充数据库中缺失的目录（如 generated/）
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
    """限制文件显示数量：超过10个则显示前8个并追加省略提示。"""
    if len(files) <= 10:
        return list(files)
    displayed = list(files[:8])
    remaining = len(files) - 8
    if lang == "zh":
        displayed.append(f"...还有{remaining}个")
    else:
        displayed.append(f"...{remaining} more")
    return displayed


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
            lines.append(f"{prefix}{connector}{item}")


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

    return "\n".join(lines)


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
