# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.generators.generate_navigation_index
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
"""G10: 自动生成架构文档库导航总览

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.10
[MODULE] scripts.governance.d5_architecture.generators.generate_navigation_index
[INVARIANTS] 输出幂等(相同输入→相同输出);只读depgraph (PostgreSQL);扫描实际文件
[MODIFY-GUARD] 修改需通过任务卡
[CONSUMERS] 人工查看 00_overview_entry/架构文档库总览.md
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph (PostgreSQL)不存在→exit 1
[TESTS]
[DOMAIN] D_GOVERNANCE
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G10: 自动生成架构文档库导航总览'
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

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402

from domain_name_mapping import get_domain_name_zh
from _common import DB_DISPLAY_NAME
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

BASE_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture"
OUTPUT_DIR = BASE_DIR / "00_overview_entry"

# 层级中文名映射
LAYER_NAME_ZH = {
    "L0_infrastructure": "基础设施层",
    "L1_foundation": "基础层",
    "L1_platform": "平台层",
    "L2_domain": "业务域层",
}


def scan_directory(dir_path: Path) -> list[str]:
    """扫描目录下的所有文件，返回文件名列表。"""
    if not dir_path.exists():
        return []
    return sorted([f.name for f in dir_path.iterdir() if f.is_file() and not f.name.startswith(".")])


def get_db_stats(conn: PgConnExecuteWrapper) -> dict:
    """从 depgraph (PostgreSQL) 获取统计数据。"""
    stats = {}

    # 域总数
    cur = conn.execute("SELECT COUNT(*) AS cnt FROM domains")
    stats["domain_count"] = cur.fetchone()["cnt"]

    # 节点总数
    cur = conn.execute("SELECT COUNT(*) AS cnt FROM nodes")
    stats["node_count"] = cur.fetchone()["cnt"]

    # 边总数
    cur = conn.execute("SELECT COUNT(*) AS cnt FROM edges")
    stats["edge_count"] = cur.fetchone()["cnt"]

    # 按层分组获取域
    cur = conn.execute(
        """SELECT layer_id, domain_id, domain_name
           FROM domains
           WHERE layer_id IS NOT NULL AND layer_id != ''
           ORDER BY layer_id, domain_id"""
    )
    all_domains = cur.fetchall()

    # 按层分组
    layer_domains: dict[str, list[tuple[str, str]]] = {}
    for r in all_domains:
        layer_id = r["layer_id"]
        domain_id = r["domain_id"]
        domain_name = r["domain_name"]
        if layer_id not in layer_domains:
            layer_domains[layer_id] = []
        layer_domains[layer_id].append((domain_id, get_domain_name_zh(domain_id, domain_name or domain_id)))

    stats["layer_domains"] = layer_domains

    # 未分层的域
    cur = conn.execute(
        """SELECT domain_id, domain_name
           FROM domains
           WHERE layer_id IS NULL OR layer_id = ''
           ORDER BY domain_id"""
    )
    stats["unassigned_domains"] = [(r["domain_id"], get_domain_name_zh(r["domain_id"], r["domain_name"] or r["domain_id"])) for r in cur.fetchall()]

    return stats


def generate_navigation(stats: dict, global_files: list, domain_files: list, report_files: list) -> str:
    """生成导航文档。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append("# 架构文档库总览")
    lines.append("")
    lines.append("> 这是你查看 ZephyrAlpha 架构的入口。从这里出发，你能找到所有架构相关的文档和图。")
    lines.append(">")
    lines.append(
        f"> **核心原则**：这个文档库是给人看的，不是给机器看的。机器看全景图数据库（{DB_DISPLAY_NAME}），人看这里。所以一切都是以人怎么方便、怎么看得直白为准。"
    )
    lines.append(">")
    lines.append(
        f"> **自动生成**：本文件由 `generate_navigation_index.py` 自动生成，每次全景图更新后自动刷新。最后更新：{now}"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # 文档库结构
    lines.append("## 文档库结构")
    lines.append("")
    lines.append("| 文件夹 | 是什么 | 谁维护 | 什么时候变 |")
    lines.append("|--------|--------|--------|-----------|")
    lines.append("| `00_overview_entry/` | 你现在看的这个文件，整个文档库的导航地图 | 自动生成 | 全景图更新时 |")
    lines.append(
        f"| `01_global_architecture_diagram/` | 全局视图（路径树、跨域矩阵、集成拓扑图），共 {len(global_files)} 个文件 | 自动生成 | 全景图更新时 |"
    )
    lines.append(
        f"| `02_domain_architecture_docs/` | 每个功能域的详细文档和依赖图，共 {len(domain_files)} 个文件 | 自动生成 | 全景图更新时 |"
    )
    lines.append(
        f"| `03_governance_reports/` | 容量报告、约束违规报告、设计态vs运营态报告，共 {len(report_files)} 个文件 | 自动生成 | 全景图更新时 |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # 怎么看
    lines.append("## 怎么看（按场景导航）")
    lines.append("")

    # 快速了解系统
    lines.append("### 想快速了解系统")
    lines.append("")
    lines.append("1. 看本文件了解文档库结构")
    lines.append("2. 看 `01_global_architecture_diagram/full_project_tree_zh.md` 了解项目物理结构（文件怎么组织的）")
    lines.append("3. 看 `01_global_architecture_diagram/integration_topology.md` 了解43个域之间怎么互相依赖")
    lines.append("4. 看 `01_global_architecture_diagram/cross_domain_matrix.md` 了解域间依赖的详细数据")
    lines.append("")

    # 了解某个功能域
    lines.append("### 想了解某个功能域")
    lines.append("")
    lines.append("1. 去 `02_domain_architecture_docs/` 找到对应域的文档（如 `53_d_trading.md`）")
    lines.append("2. 看域文档了解这个域有哪些模块、每个模块干什么")
    lines.append("3. 看域文档内嵌的 Mermaid 依赖图了解这个域内部怎么依赖、跟其他域怎么依赖")
    lines.append("4. 看 `02_domain_architecture_docs/domain_index.md` 了解所有域的清单")
    lines.append("")

    # 看系统健康度
    lines.append("### 想看系统健康度")
    lines.append("")
    lines.append("1. 看 `03_governance_reports/capacity_report.md` 了解各域模块数（有没有超标）")
    lines.append("2. 看 `03_governance_reports/constraint_violations.md` 了解有哪些违规")
    lines.append("3. 看 `03_governance_reports/design_vs_production.md` 了解设计态到运营态的迁移进度")
    lines.append("")

    lines.append("---")
    lines.append("")

    # 数据从哪来
    lines.append("## 数据从哪来")
    lines.append("")
    lines.append("**所有文档都是自动生成的**：")
    lines.append(f"- 数据源：{DB_DISPLAY_NAME} 数据库（全景图数据库）")
    lines.append("- 全景图是唯一真源")
    lines.append("- 架构图是全景图的派生物")
    lines.append("- 禁止手工修改自动生成的文档")
    lines.append("- 生成器位于：`scripts/governance/d5_architecture/generators/`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 功能域速览
    lines.append("## 功能域速览")
    lines.append("")
    lines.append("> 完整列表见 `02_domain_architecture_docs/domain_index.md`")
    lines.append("")
    lines.append("| 层级 | 域数量 | 代表域 |")
    lines.append("|------|:---:|--------|")

    for layer_id, domains in stats["layer_domains"].items():
        layer_name = LAYER_NAME_ZH.get(layer_id, layer_id)
        count = len(domains)
        # 取前3个域作为代表
        rep_domains = domains[:3]
        rep_str = "、".join([f"{did}（{name}）" for did, name in rep_domains])
        if count > 3:
            rep_str += " 等"
        lines.append(f"| {layer_name} | {count} | {rep_str} |")

    # 未分层的域
    if stats["unassigned_domains"]:
        count = len(stats["unassigned_domains"])
        rep_domains = stats["unassigned_domains"][:3]
        rep_str = "、".join([f"{did}（{name}）" for did, name in rep_domains])
        if count > 3:
            rep_str += " 等"
        lines.append(f"| 未分层 | {count} | {rep_str} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 修订记录
    lines.append("## 修订记录")
    lines.append("")
    lines.append("| 日期 | 说明 |")
    lines.append("|------|------|")
    lines.append(f"| {now} | 自动生成 |")

    return "\n".join(lines)


def main() -> None:
    """入口：生成导航总览。"""
    parser = argparse.ArgumentParser(description="G10: 自动生成架构文档库导航总览")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR), help="输出目录")
    parser.add_argument("--output-name", type=str, default="navigation_index.md", help="输出文件名")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 扫描实际文件
    global_files = scan_directory(BASE_DIR / "01_global_architecture_diagram")
    domain_files = scan_directory(BASE_DIR / "02_domain_architecture_docs")
    report_files = scan_directory(BASE_DIR / "03_governance_reports")

    # 获取统计数据
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        stats = get_db_stats(conn)
    finally:
        conn.close()

    # 生成导航文档
    content = generate_navigation(stats, global_files, domain_files, report_files)
    out_path = output_dir / args.output_name
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] 生成 {out_path} ({len(content)} 字符)")


if __name__ == "__main__":
    main()
