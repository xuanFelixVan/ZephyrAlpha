# [BLUEPRINT] MOD-D_GOV_SCRIPTS | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d5_architecture.generators.generate_code_wiki_stats
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] depgraph (PostgreSQL); pyproject.toml; scripts/governance/d*/ 目录扫描
# [CONSUMERS] docs/02_enterprise_architecture/04_architecture_principles_decisions/code_wiki.md
# [STARTUP] event_driven  # 由 generate_project_depgraph.py 刷新钩子触发
# [MATURITY] production
# [INVARIANTS] 只更新 AUTO-START/END 标记块内内容；手工区不动；输出幂等；双语格式（中文 / English）
# [MODIFY-GUARD] AUTO 标记块名与 code_wiki.md 中标记保持一致
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph 不存在→exit 1；code_wiki.md 不存在→exit 1；标记块缺失→跳过该块并 warning
# [TESTS]
# [TTL] permanent
# noqa: consumers-accuracy  # code_wiki.md 是文档路径非模块路径
# noqa: m11-perm-manual-legitimate  生成器由全景图刷新钩子触发(subprocess.run)
"""Code Wiki 统计数据生成器（半自动维护机制）。

[BLUEPRINT] VIEW-CODE-WIKI | docs/02_enterprise_architecture/04_architecture_principles_decisions/code_wiki.md
[MODULE] scripts.governance.d5_architecture.generators.generate_code_wiki_stats
[INVARIANTS] 只更新 AUTO-START/END 标记块内内容；手工区不动；输出幂等；双语格式
[CONSUMERS] code_wiki.md（4 个 AUTO 块：directory_tree / governance_script_counts / dependency_stats / external_deps）
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph 不存在→exit 1；code_wiki.md 不存在→exit 1；标记块缺失→跳过该块并 warning
[DOMAIN] D_GOV_SCRIPTS

本生成器从数据源（depgraph DB / pyproject.toml / 文件系统扫描）拉取统计数据，
更新 code_wiki.md 中 4 个 AUTO 标记块的内嵌内容，不触碰手工区。

支持的 AUTO 块（块名必须与 code_wiki.md 中标记一致）：
- directory_tree           : src/zephyr/ + scripts/governance/ 目录树（文件系统扫描）
- governance_script_counts : 12 维度审计脚本数表（scripts/governance/d*/ 扫描）
- dependency_stats         : depgraph DB 节点/边/域统计
- external_deps            : pyproject.toml [project.dependencies] 表

调用方式：
    python -m scripts.governance.d5_architecture.generators.generate_code_wiki_stats
    python scripts/governance/d5_architecture/generators/generate_code_wiki_stats.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G-WIKI: 自动同步 code_wiki.md 中 4 个 AUTO 标记块的统计数据'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402
from _shared.constants import EXIT_FINDINGS
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

# DB_DISPLAY_NAME 内联定义（避免 import _common 触发 IMPORT-INTEGRITY worktree 误报）
# 真源：scripts/governance/d5_architecture/generators/_common.py DB_DISPLAY_NAME
DB_DISPLAY_NAME = "depgraph (PostgreSQL)"

# SQL 集中化（NO-BARE-SQL 门禁要求：SQL 提取到模块级常量）
SQL_COUNT_DOMAINS = "SELECT COUNT(*) AS cnt FROM domains"
SQL_COUNT_NODES = "SELECT COUNT(*) AS cnt FROM nodes"
SQL_COUNT_EDGES = "SELECT COUNT(*) AS cnt FROM edges"
SQL_NODES_BY_STATUS = (
    "SELECT build_status, COUNT(*) AS cnt "
    "FROM nodes "
    "WHERE build_status IS NOT NULL AND build_status != '' "
    "GROUP BY build_status "
    "ORDER BY build_status"
)
SQL_ORPHAN_NODES = (
    "SELECT COUNT(*) AS cnt FROM nodes n "
    "WHERE n.build_status = 'production' "
    "AND NOT EXISTS ("
    "SELECT 1 FROM edges e WHERE e.to_node_id = n.node_id"
    ")"
)

# 目标文档（半自动维护：生成器只更新 AUTO 标记块内内容）
WIKI_PATH = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "04_architecture_principles_decisions"
    / "code_wiki.md"
)

# AUTO 标记块正则：匹配 <!-- AUTO-START:name -->...<!-- AUTO-END:name --> 之间的内容
# 捕获组 1 = 块名，组 2 = 块内现有内容（含 START 行后到 END 行前的全部字符）
_BLOCK_RE_TEMPLATE = r"(<!-- AUTO-START:{name} -->\n)(.*?)(<!-- AUTO-END:{name} -->)"


# ============================================================
# 数据采集：4 个 AUTO 块的数据源
# ============================================================


def collect_directory_tree() -> str:
    """块 directory_tree：扫描 src/zephyr/ 一级目录 + scripts/governance/ 维度目录。

    生成带中英文双语注释的目录树。注释列格式：中文说明 / English。
    注意：注释列是手工维护的（在 code_wiki.md 里），本函数只生成树骨架，
    不覆盖注释——故此块实际"半自动"：树结构自动，注释手工。
    为避免破坏手工注释，本块生成器策略：**不更新此块**，仅在块缺失时初始化。

    Returns:
        空字符串（此块由手工维护，生成器不自动覆盖注释列）。
    """
    # 此块的注释列是手工维护的双语说明，生成器若强行覆盖会破坏人工翻译。
    # 策略：生成器跳过此块，由人工维护。返回 None 表示"不更新"。
    return ""


def collect_governance_script_counts() -> str:
    """块 governance_script_counts：扫描 scripts/governance/d*/ 目录的 .py 文件数。

    自动生成维度+脚本数表。职责列的中英文翻译是手工维护的（在 _DIMENSION_LABELS 里）。

    Returns:
        Markdown 表格字符串（含表头+数据行）。
    """
    gov_dir = REPO_ROOT / "scripts" / "governance"

    # 维度目录 → 中英文职责描述（手工维护的翻译表）
    # 真源：scripts/governance/d*/ 目录实际存在性
    _DIMENSION_LABELS: dict[str, tuple[str, str]] = {
        "d1_structure": ("目录结构验证", "Directory structure"),
        "d2_links": ("断链检测", "Broken link detection"),
        "d3_metadata": ("frontmatter 校验", "Frontmatter validation"),
        "d4_paths": ("路径守卫", "Path guard"),
        "d5_architecture": ("架构合规（最大）", "Architecture compliance (largest)"),
        "d6_security": ("安全扫描", "Security scan"),
        "d7_code_quality": ("去重/AST", "Dedup/AST"),
        "d8_doc_sync": ("文档一致性", "Doc consistency"),
        "d9_knowledge": ("知识库", "Knowledge base"),
        "d10_performance": ("性能基准", "Performance benchmark"),
        "d11_compliance": ("合规检查", "Compliance check"),
        "d12_hallucination": ("幻觉检测", "Hallucination detection"),
    }

    rows: list[str] = []
    rows.append("| 维度 | 职责 | 脚本数 |")
    rows.append("|------|------|--------|")

    total = 0
    for dim_dir in sorted(gov_dir.glob("d*/")):
        if not dim_dir.is_dir():
            continue
        dim_key = dim_dir.name
        # 统计 .py 文件数（排除 __init__.py）
        py_files = [f for f in dim_dir.glob("*.py") if f.name != "__init__.py"]
        count = len(py_files)
        total += count
        zh, en = _DIMENSION_LABELS.get(dim_key, (dim_key, dim_key))
        rows.append(f"| {dim_key} | {zh} / {en} | {count} |")

    # 在表格末尾加合计行（便于人工核对"317 脚本"总数）
    rows.append(f"| **合计** | **Total** | **{total}** |")

    return "\n".join(rows)


def collect_dependency_stats() -> str:
    """块 dependency_stats：从 depgraph DB 拉取节点/边/域统计。

    Returns:
        Markdown 表格字符串。
    """
    conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
    try:
        cur = conn.execute(SQL_COUNT_DOMAINS)
        domain_count = cur.fetchone()["cnt"]

        cur = conn.execute(SQL_COUNT_NODES)
        node_count = cur.fetchone()["cnt"]

        cur = conn.execute(SQL_COUNT_EDGES)
        edge_count = cur.fetchone()["cnt"]

        cur = conn.execute(SQL_NODES_BY_STATUS)
        status_rows = cur.fetchall()

        cur = conn.execute(SQL_ORPHAN_NODES)
        orphan_count = cur.fetchone()["cnt"]
    finally:
        conn.close()

    # datetime.now(UTC) 用于同步日期标记（合法场景：生成器输出时间戳）
    from datetime import UTC
    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记(非业务逻辑时间戳)

    lines: list[str] = []
    lines.append(f"<!-- 数据源：{DB_DISPLAY_NAME} | 最后同步：{sync_date} -->")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    lines.append(f"| 域总数 / Total domains | {domain_count} |")
    lines.append(f"| 节点总数 / Total nodes | {node_count} |")
    lines.append(f"| 依赖边总数 / Total edges | {edge_count} |")
    lines.append(f"| 孤儿节点数 / Orphan nodes | {orphan_count} |")
    lines.append("")
    lines.append("| build_status | 节点数 |")
    lines.append("|--------------|--------|")
    for r in status_rows:
        lines.append(f"| `{r['build_status']}` | {r['cnt']} |")

    return "\n".join(lines)


def collect_external_deps() -> str:
    """块 external_deps：从 pyproject.toml [project.dependencies] 生成依赖表。

    Returns:
        Markdown 表格字符串。
    """
    pyproject = REPO_ROOT / "pyproject.toml"

    # 简单解析 [project.dependencies] 段（避免引入 tomli 依赖）
    # 项目 requires-python >=3.12，标准库 tomllib 可用
    import tomllib

    with open(pyproject, "rb") as f:
        data = tomllib.load(f)

    deps = data.get("project", {}).get("dependencies", [])

    # 用途说明（手工维护的翻译表——常见依赖的中文用途）
    _DEP_USAGE: dict[str, str] = {
        "pydantic": "数据验证 / Data validation",
        "pyyaml": "YAML 配置解析 / YAML config parsing",
        "pandas": "数据处理 / Data processing",
        "psutil": "系统监控 / System monitoring",
        "chromadb": "向量数据库（知识库）/ Vector DB (KB)",
        "mcp": "MCP 协议 / MCP protocol",
        "openai": "LLM 客户端 / LLM client",
        "sentence-transformers": "句向量模型 / Sentence embeddings",
        "structlog": "结构化日志 / Structured logging",
        "pyarrow": "Parquet I/O / Parquet I/O",
        "psycopg2-binary": "PostgreSQL 驱动 / PostgreSQL driver",
        "plotly": "可视化 / Visualization",
        "streamlit": "早期仪表盘 / Legacy dashboard",
        "panel": "仪表盘 / Dashboard",
        "holoviews": "可视化层 / Viz layer",
        "datashader": "大数据渲染 / Large data rendering",
        "hvplot": "Pandas 绘图 / Pandas plotting",
        "plotly_resampler": "时序降采样 / Timeseries downsampling",
        "python-dotenv": "环境变量 / Env vars",
        "apscheduler": "任务调度 / Task scheduling",
        "sqlalchemy": "ORM/JobStore / ORM/JobStore",
        "exchange_calendars": "交易日历 / Trading calendars",
    }

    rows: list[str] = []
    rows.append("| 依赖 | 用途 |")
    rows.append("|------|------|")

    for dep in deps:
        # 解析依赖名（去掉版本约束和注释）
        # 形如 "pydantic>=2.0.0,<3.0.0" 或 "# 注释行" 或 "panel>=1.5.0,<2.0.0"
        stripped = dep.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # 提取依赖名（第一个非字母数字字符前的部分）
        match = re.match(r"^([a-zA-Z0-9_-]+)", stripped)
        if not match:
            continue
        dep_name = match.group(1).lower()
        usage = _DEP_USAGE.get(dep_name, "— / —")
        rows.append(f"| `{stripped}` | {usage} |")

    return "\n".join(rows)


# ============================================================
# AUTO 块替换引擎
# ============================================================


def replace_block(content: str, block_name: str, new_inner: str) -> tuple[str, bool]:
    """替换 content 中指定 AUTO 块的内嵌内容。

    只替换 START 标记行之后、END 标记行之前的全部内容。标记行本身保留。
    保持原文件手工区完全不动。

    Args:
        content: code_wiki.md 的完整文本。
        block_name: AUTO 块名（如 "dependency_stats"）。
        new_inner: 要写入块内的新内容。

    Returns:
        (更新后的 content, 是否找到了块并替换)
    """
    pattern = _BLOCK_RE_TEMPLATE.format(name=re.escape(block_name))
    regex = re.compile(pattern, re.DOTALL)

    def _replace(match: re.Match) -> str:
        """_replace implementation."""
        start_line = match.group(1)  # <!-- AUTO-START:name -->\n
        # new_inner + 确保 END 前有换行
        return f"{start_line}{new_inner}\n{match.group(3)}"

    new_content, count = regex.subn(_replace, content, count=1)
    return new_content, count > 0


# ============================================================
# 主入口
# ============================================================


def main() -> None:
    """入口：同步 code_wiki.md 中 4 个 AUTO 块的统计数据。"""
    parser = argparse.ArgumentParser(
        description="G-WIKI: 自动同步 code_wiki.md 中 4 个 AUTO 标记块的统计数据"
    )
    parser.add_argument(
        "--wiki-path",
        type=str,
        default=str(WIKI_PATH),
        help="code_wiki.md 路径（默认：docs/02_enterprise_architecture/04_architecture_principles_decisions/code_wiki.md）",
    )
    parser.add_argument(
        "--block",
        type=str,
        choices=["all", "directory_tree", "governance_script_counts", "dependency_stats", "external_deps"],
        default="all",
        help="只更新指定块（默认：all）",
    )
    args = parser.parse_args()

    wiki_path = Path(args.wiki_path)
    if not wiki_path.exists():
        print(f"[ERROR] code_wiki.md 不存在：{wiki_path}", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    content = wiki_path.read_text(encoding="utf-8")
    original = content

    # 块名 → 数据采集函数
    block_collectors: dict[str, callable] = {
        "governance_script_counts": collect_governance_script_counts,
        "dependency_stats": collect_dependency_stats,
        "external_deps": collect_external_deps,
        # directory_tree 块：注释列手工维护，生成器跳过（避免破坏双语注释）
        # 如需强制更新，加 --block directory_tree 并实现 collect_directory_tree 的覆盖逻辑
    }

    updated_blocks: list[str] = []
    skipped_blocks: list[str] = []

    blocks_to_update = (
        list(block_collectors.keys()) if args.block == "all" else [args.block]
    )

    for block_name in blocks_to_update:
        if block_name == "directory_tree":
            # 此块注释列手工维护，生成器默认跳过
            skipped_blocks.append(f"{block_name}（手工维护双语注释）")
            continue

        collector = block_collectors.get(block_name)
        if collector is None:
            print(f"[WARN] 未知块：{block_name}", file=sys.stderr)
            continue

        try:
            new_inner = collector()
        except Exception as e:
            print(f"[ERROR] 采集块 {block_name} 数据失败：{e}", file=sys.stderr)
            skipped_blocks.append(f"{block_name}（采集失败）")
            continue

        content, found = replace_block(content, block_name, new_inner)
        if found:
            updated_blocks.append(block_name)
        else:
            print(f"[WARN] 块 {block_name} 标记未在文档中找到，跳过", file=sys.stderr)
            skipped_blocks.append(f"{block_name}（标记缺失）")

    # 幂等写：内容有变化才写回
    if content != original:
        wiki_path.write_text(content, encoding="utf-8")
        print(f"[OK] 更新 {wiki_path.name}：{', '.join(updated_blocks)}")
    else:
        print(f"[OK] {wiki_path.name} 无变化（已幂等）")

    if skipped_blocks:
        print(f"[INFO] 跳过块：{', '.join(skipped_blocks)}")


if __name__ == "__main__":
    main()
