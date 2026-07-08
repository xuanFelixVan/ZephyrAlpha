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
# [TTL] permanent
"""G1: 从 depgraph (PostgreSQL) arch_directory_tree 表 + 文件系统生成 docs/02_enterprise_architecture/ 目录树(中英文)输出到 generated/

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.4
[MODULE] scripts.governance.d5_architecture.generators.generate_path_tree
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL)+文件系统;输出到01_global_architecture_diagram/目录;全项目概览(过滤噪声目录)
[MODIFY-GUARD] 修改需通过DM-200910任务卡或后续维护任务卡
[CONSUMERS] CI自动触发;人工查看full_project_tree_zh.md+full_project_tree_en.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1;查询失败→exit 2
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

# 治本（2026-07-04）：DB_DISPLAY_NAME 前移到 __manifest__ 之前，避免 f-string 求值时 NameError。
# _common.py 与本文件同目录（generators/），CLI 运行时 sys.path[0]=本目录，可直接 import。
from _common import DB_DISPLAY_NAME  # noqa: E402

__manifest__ = f"""
args: []
description: 'G1: 从 {DB_DISPLAY_NAME} arch_directory_tree 表 + 文件系统生成 docs/02_enterprise_architecture/
  目录树(中英文)输出到 generated/'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import functools
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

PROJECT_ROOT = REPO_ROOT
OUTPUT_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "01_global_architecture_diagram"
TARGET_SUBTREE = "docs/02_enterprise_architecture"

# 生成文件的 frontmatter（GATE-15 TTL 校验要求：.md 文件必须有 ttl 字段）
# doc_type=architecture_view 真源：doc_type_vocabulary.yaml
_FRONTMATTER = (
    "---\n"
    "doc_type: architecture_view\n"
    "ttl: permanent\n"
    "module_id: MOD-GOV-generate_path_tree\n"
    "---\n\n"
)

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


def build_tree_rows(conn: PgConnExecuteWrapper, scope: str = "arch") -> list[dict]:
    """从 arch_directory_tree 表查询目录记录，按 path 排序。

    scope='arch': 仅 docs/02_enterprise_architecture 下的目录
    scope='full': 全项目所有目录（过滤噪声目录）
    """
    if scope == "full":
        cur = conn.execute(
            "SELECT path, parent_path, path_type, domain_id, build_status, design_maturity "
            "FROM arch_directory_tree "
            "WHERE path NOT LIKE '%%/' "
            "ORDER BY path",
        )
    else:
        cur = conn.execute(
            "SELECT path, parent_path, path_type, domain_id, build_status, design_maturity "
            "FROM arch_directory_tree "
            "WHERE (path = %s OR path LIKE %s) AND path NOT LIKE '%%/' "
            "ORDER BY path",
            (TARGET_SUBTREE, TARGET_SUBTREE + "/%"),
        )
    rows = []
    for r in cur.fetchall():
        path = r["path"] or ""
        # 全项目模式下过滤噪声目录
        if scope == "full":
            parts = path.split("/")
            if any(p in SKIP_DIRS_FULL for p in parts):
                continue
        rows.append(
            {
                "path": path,
                "parent_path": r["parent_path"] or "",
                "path_type": r["path_type"] or "",
                "domain_id": r["domain_id"] or "",
                "build_status": r["build_status"] or "",
                "design_maturity": r["design_maturity"] or "",
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
# depth 0=根, 1=00_overview_entry等, 2=architecture_model, 3=architecture_model/contracts(不展开)
# 最大显示深度（相对于根目录）
# arch 模式: depth 0=根, 1=00_overview_entry等, 2=architecture_model, 3=contracts(不展开)
# full 模式: depth 0=顶级(src/scripts等), 1=二级, 2=三级(不展开)
MAX_DISPLAY_DEPTH_ARCH = 3
MAX_DISPLAY_DEPTH_FULL = 2


def get_dir_description(dir_name: str, lang: str) -> str:
    """获取目录功能描述。"""
    if lang == "zh":
        return DIR_DESCRIPTIONS_ZH.get(dir_name, "")
    return DIR_DESCRIPTIONS_EN.get(dir_name, "")


@functools.lru_cache(maxsize=None)
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


# 文件折叠阈值：超过此数量的目录只显示统计，不逐个列出文件名
COLLAPSE_THRESHOLD = 200  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 路径树折叠阈值，脚本专用
# 同类文件折叠的最小数量（低于此数即使同类也不折叠，保留明细）
SAME_PATTERN_MIN = 15
# 临时文件扩展名（无独立查看价值）
_TMP_EXTS = {".tmp", ".bak", ".cache", ".temp", ".swp"}
# data/ 下的数据文件扩展名（自动生成的同类数据）
_DATA_EXTS = {".json", ".jsonl", ".csv", ".log"}
# 文件名数字归一化模式（用于检测时间戳/序号命名）
_DIGIT_PATTERN = re.compile(r"\d+")


def _normalize_filename(name: str) -> str:
    """将文件名中的数字替换为 #，用于检测同类命名模式。"""
    return _DIGIT_PATTERN.sub("#", name)


def _majority_same_pattern(files: list[str], threshold: float = 0.6) -> bool:
    """检测 > threshold 的文件名归一化后共享相同模板（时间戳/序号命名同类文件）。

    例：benchmark_20260522.jsonl 与 benchmark_20260523.jsonl 归一化后均为 benchmark_#.jsonl。
    """
    if not files:
        return False
    patterns = [_normalize_filename(f) for f in files]
    counter = Counter(patterns)
    most_common_count = counter.most_common(1)[0][1]
    return most_common_count / len(files) > threshold


def _is_data_dir(dir_path: str, files: list[str], threshold: float = 0.7) -> bool:
    """判断 data/ 下的同类数据文件目录（> threshold 同扩展名，>= 20 个）。

    data/ 下的 .json/.jsonl/.csv/.log 文件通常是自动生成的同类数据，无独立查看价值。
    排除 .db（数据库文件有独立意义）和 .yaml（配置/skill 文件有独立意义）。
    """
    if not dir_path.startswith("data/"):
        return False
    if len(files) < 20:
        return False
    exts = [Path(f).suffix.lower() for f in files]
    ext_counter = Counter(exts)
    most_common_ext, most_common_count = ext_counter.most_common(1)[0]
    return most_common_count / len(files) > threshold and most_common_ext in _DATA_EXTS


def _majority_tmp_files(files: list[str], threshold: float = 0.6) -> bool:
    """检测 > threshold 的文件是临时文件（.tmp/.bak 等）。"""
    if not files:
        return False
    tmp_count = sum(1 for f in files if Path(f).suffix.lower() in _TMP_EXTS)
    return tmp_count / len(files) > threshold


def _should_collapse_files(dir_path: str, files: list[str]) -> bool:
    """判断目录下的文件是否应折叠（只显示数量统计，不逐个列出）。

    判定标准（任一满足即折叠）：
    1. __pycache__ 目录 → 总是折叠（.pyc 缓存文件无独立意义）
    2. 文件数量 > COLLAPSE_THRESHOLD → 折叠（大量同类数据文件）
    3. 文件数 >= SAME_PATTERN_MIN 且多数文件名归一化后共享模板 → 折叠（时间戳/序号命名）
    4. data/ 下同类数据文件（> 70% 同扩展名，>= 20 个）→ 折叠（自动生成数据）
    5. 文件数 >= SAME_PATTERN_MIN 且多数是临时文件 → 折叠（.tmp/.bak 无独立意义）
    """
    if not files:
        return False
    dir_name = dir_path.rsplit("/", 1)[-1] if "/" in dir_path else dir_path
    if dir_name == "__pycache__":
        return True
    if len(files) > COLLAPSE_THRESHOLD:
        return True
    if len(files) >= SAME_PATTERN_MIN and _majority_same_pattern(files):
        return True
    if _is_data_dir(dir_path, files):
        return True
    if len(files) >= SAME_PATTERN_MIN and _majority_tmp_files(files):
        return True
    return False


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
    "full_project_tree_en.md": "路径树(英文)",
    "full_project_tree_zh.md": "路径树(中文)",
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
    # 以下文件随 target_architecture/ 删除（2026-07-01），描述保留供历史参考
    "application_architecture.md": "应用架构",
    "architecture_endgame_locked.md": "架构终态锁定",
    "architecture_principles.md": "架构原则",
    "business_architecture.md": "业务架构",
    "data_architecture.md": "数据架构",
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
    "dependency_path_panorama.md": "依赖路径全景图",
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
    "full_project_tree_en.md": "Path tree (English)",
    "full_project_tree_zh.md": "Path tree (Chinese)",
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


def _extract_file_brief(file_path: Path) -> str:
    """从文件内容提取功能简介（docstring 第一行 / title 字段 / 标题）。

    返回空字符串表示未提取到。最多返回100字符。
    """
    suffix = file_path.suffix.lower()
    if suffix not in (".py", ".yaml", ".yml", ".md"):
        return ""
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            content = f.read(4096)
    except OSError:
        return ""

    if suffix == ".py":
        # 提取 docstring 第一行（""" 或 '''）
        m = re.search(r'"""(.+?)"""', content, re.DOTALL)
        if not m:
            m = re.search(r"'''(.+?)'''", content, re.DOTALL)
        if m:
            first_line = m.group(1).strip().split("\n")[0].strip()
            # 去掉模块ID引用（如 "（MOD-INF-013 §5.3）"）
            first_line = re.sub(r"（[^）]*MOD-[^）]*）", "", first_line).strip()
            if first_line:
                return first_line[:100]

    elif suffix in (".yaml", ".yml"):
        # 提取 title: 字段
        m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        if m:
            return m.group(1).strip()[:100]

    elif suffix == ".md":
        # 优先 frontmatter title
        m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
        if m:
            return m.group(1).strip()[:100]
        # 回退到第一个 # 标题
        m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if m:
            return m.group(1).strip()[:100]

    return ""


def get_file_description(filename: str, lang: str, file_path: str = "") -> str:
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

    # 从文件内容提取功能简介（docstring / title / 标题）
    if file_path:
        brief = _extract_file_brief(Path(file_path))
        if brief:
            return brief

    # 通用后缀推断（回退）
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


def render_tree(tree: dict, root_path: str, prefix: str, lines: list[str], lang: str, depth: int = 0, scope: str = "arch") -> None:
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
    _render_children(tree, root_path, prefix, lines, lang, depth, scope)


def _render_children(tree: dict, parent_path: str, prefix: str, lines: list[str], lang: str, depth: int, scope: str = "arch") -> None:
    """渲染子节点（子目录在前，文件在后），深度超过限制时不展开子目录。"""
    if parent_path not in tree:
        return
    max_depth = MAX_DISPLAY_DEPTH_FULL if scope == "full" else MAX_DISPLAY_DEPTH_ARCH
    node = tree[parent_path]
    child_dirs = sorted(node["children"], key=lambda c: _sort_children_key(c, parent_path))
    files = get_dir_files(parent_path)

    # 判断是否折叠文件列表（大量同类数据文件只显示统计）
    if _should_collapse_files(parent_path, files):
        file_summary = get_file_summary(files, lang)
        if lang == "zh":
            collapse_line = f"[文件列表已折叠] {file_summary}"
        else:
            collapse_line = f"[file list collapsed] {file_summary}"
        all_items: list[tuple[str, bool]] = [(d, True) for d in child_dirs] + [
            (collapse_line, False)
        ]
    else:
        files_display = _limit_files(files, lang)
        all_items = [(d, True) for d in child_dirs] + [
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
            # 深度控制：超过max_depth不展开子目录
            if depth < max_depth:
                _render_children(tree, item, child_prefix, lines, lang, depth + 1, scope)
        else:
            # 折叠行直接输出，不添加文件描述
            if item.startswith("["):
                lines.append(f"{prefix}{connector}{item}")
            else:
                # 文件名后添加中文功能描述
                full_path = str(PROJECT_ROOT / parent_path / item)
                file_desc = get_file_description(item, lang, full_path)
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


def generate_path_tree(lang: str, conn: PgConnExecuteWrapper, scope: str = "arch") -> str:
    """生成路径树内容。

    lang: 'zh' 或 'en'
    scope: 'arch'（仅架构文档目录）或 'full'（全项目概览）
    """
    rows = build_tree_rows(conn, scope)
    tree = build_tree_structure(rows, scope)
    roots = find_roots(tree)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if scope == "full":
        if lang == "zh":
            header = f"""# ZephyrAlpha 全项目目录树 / Full Project Directory Tree

> **文档作用**: 以树状结构展示全项目的所有顶级目录及子目录，用于快速定位代码/脚本/文档/配置/数据。
> 本文档由 generate_path_tree.py 从 {DB_DISPLAY_NAME} + 文件系统自动生成 / Auto-generated by generate_path_tree.py from {DB_DISPLAY_NAME} + filesystem
> 最后更新: {now} / Last updated: {now}
> 数据源: {DB_DISPLAY_NAME} arch_directory_tree 表（目录）+ 文件系统扫描（文件）/ Data source: {DB_DISPLAY_NAME} arch_directory_tree (dirs) + filesystem scan (files)
> 显示深度: 顶级目录展开2层，深层目录不展开 / Display depth: top-level dirs expand 2 levels, deep dirs collapsed

## 全项目目录树 / Full Project Directory Tree

"""
            stats_title = "## 统计 / Statistics"
            total_dirs_label = "总目录数 / Total directories"
            total_files_label = "总文件数 / Total files"
            total_domains_label = "涉及域数 / Domains involved"
        else:
            header = f"""# ZephyrAlpha Full Project Directory Tree / 全项目目录树

> **Purpose**: Display all top-level directories and subdirectories of the entire project in a tree structure for quick location of code/scripts/docs/config/data.
> Auto-generated by generate_path_tree.py from {DB_DISPLAY_NAME} + filesystem / 本文档由 generate_path_tree.py 从 {DB_DISPLAY_NAME} + 文件系统自动生成
> Last updated: {now} / 最后更新: {now}
> Data source: {DB_DISPLAY_NAME} arch_directory_tree (dirs) + filesystem scan (files) / 数据源: {DB_DISPLAY_NAME} arch_directory_tree（目录）+ 文件系统扫描（文件）
> Display depth: top-level dirs expand 2 levels / 显示深度: 顶级目录展开2层

## Full Project Directory Tree / 全项目目录树

"""
            stats_title = "## Statistics / 统计"
            total_dirs_label = "Total directories / 总目录数"
            total_files_label = "Total files / 总文件数"
            total_domains_label = "Domains involved / 涉及域数"
    else:
        if lang == "zh":
            header = f"""# ZephyrAlpha 架构文档目录树 / Architecture Docs Directory Tree

> **文档作用**: 以树状结构展示 docs/02_enterprise_architecture/ 目录下的所有子目录、文件及所属功能域，用于快速定位架构文档。
> 本文档由 generate_path_tree.py 从 {DB_DISPLAY_NAME} + 文件系统自动生成 / Auto-generated by generate_path_tree.py from {DB_DISPLAY_NAME} + filesystem
> 最后更新: {now} / Last updated: {now}
> 数据源: {DB_DISPLAY_NAME} arch_directory_tree 表（目录）+ 文件系统扫描（文件）/ Data source: {DB_DISPLAY_NAME} arch_directory_tree (dirs) + filesystem scan (files)

## 架构文档目录树 / Architecture Docs Directory Tree

"""
            stats_title = "## 统计 / Statistics"
            total_dirs_label = "总目录数 / Total directories"
            total_files_label = "总文件数 / Total files"
            total_domains_label = "涉及域数 / Domains involved"
        else:
            header = f"""# ZephyrAlpha Architecture Docs Directory Tree / 架构文档目录树

> **Purpose**: Display all subdirectories, files and their functional domains under docs/02_enterprise_architecture/ in a tree structure for quick architecture document location.
> Auto-generated by generate_path_tree.py from {DB_DISPLAY_NAME} + filesystem / 本文档由 generate_path_tree.py 从 {DB_DISPLAY_NAME} + 文件系统自动生成
> Last updated: {now} / 最后更新: {now}
> Data source: {DB_DISPLAY_NAME} arch_directory_tree (dirs) + filesystem scan (files) / 数据源: {DB_DISPLAY_NAME} arch_directory_tree（目录）+ 文件系统扫描（文件）

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
        render_tree(tree, root, "", lines, lang, scope=scope)
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
    """入口：生成中英文物理路径树(全项目)。"""
    parser = argparse.ArgumentParser(description="G1: 生成项目物理路径树(中英文)")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--lang", type=str, choices=["zh", "en", "both"], default="both", help="生成语言")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    zh_name = "full_project_tree_zh.md"
    en_name = "full_project_tree_en.md"

    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        if args.lang in ("zh", "both"):
            content = _FRONTMATTER + generate_path_tree("zh", conn, "full")
            out_path = output_dir / zh_name
            out_path.write_text(content, encoding="utf-8")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")

        if args.lang in ("en", "both"):
            content = _FRONTMATTER + generate_path_tree("en", conn, "full")
            out_path = output_dir / en_name
            out_path.write_text(content, encoding="utf-8")
            print(f"[OK] 生成 {out_path} ({len(content)} 字符)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
