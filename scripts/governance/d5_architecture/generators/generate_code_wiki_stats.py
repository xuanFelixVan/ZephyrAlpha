# [BLUEPRINT] MOD-D_GOV_SCRIPTS | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance.d5_architecture.generators.generate_code_wiki_stats
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] depgraph (PostgreSQL); pyproject.toml; architecture_model/*.yaml; scripts/governance/d*/ 目录扫描; src/zephyr/gov_enforcement/commit_gates/ 扫描; governance.db (SQLite)
# [CONSUMERS] docs/02_enterprise_architecture/04_architecture_principles_decisions/README.md;project_handbook/01_overview.md;02_repository_and_modules.md;03_data_layer.md;04_data_sources.md;05_trading_domains.md;06_governance_and_infra.md;07_dependencies.md
# [STARTUP] event_driven  # 由 generate_project_depgraph.py 刷新钩子触发（main 末尾 post_depgraph_refresh_hook）
# [MATURITY] production
# [INVARIANTS] 只更新 AUTO-START/END 标记块内内容；手工区不动；输出幂等；双语格式（中文 / English）；多目标文件并行刷新
# [MODIFY-GUARD] AUTO 标记块名与 project_handbook/*.md 中标记保持一致
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph 不存在→exit 1；目标文档不存在→exit 1；标记块缺失→跳过该块并 warning；单块采集失败→跳过并 warning（不阻断其他块）
# [TESTS]
# [A_module] module_id=MOD-D_GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: consumers-accuracy  # project_handbook/*.md 是文档路径非模块路径
# noqa: m11-perm-manual-legitimate  生成器由全景图刷新钩子触发(subprocess, 经 process_pool.run_subprocess_hidden)
"""Code Wiki 统计数据生成器（半自动维护机制）。

[BLUEPRINT] VIEW-CODE-WIKI | docs/02_enterprise_architecture/04_architecture_principles_decisions/project_handbook/
[MODULE] scripts.governance.d5_architecture.generators.generate_code_wiki_stats
[INVARIANTS] 只更新 AUTO-START/END 标记块内内容；手工区不动；输出幂等；双语格式；多目标文件
[CONSUMERS] README.md + project_handbook/01_overview.md ~ 07_dependencies.md（12 个 AUTO 块）
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph 不存在→exit 1；目标文档不存在→exit 1；标记块缺失→跳过并 warning；单块采集失败→跳过
[DOMAIN] D_GOV_SCRIPTS

本生成器从多个数据源（depgraph DB / pyproject.toml / architecture_model YAML / 文件系统扫描 /
governance.db SQLite / commit_gates 目录）拉取统计数据，更新 04_architecture_principles_decisions 下
8 个文档（README.md + 7 个 project_handbook）中的 12 个 AUTO 标记块内嵌内容，不触碰手工区。

支持的 AUTO 块（块名必须与 project_handbook/*.md 中标记一致）：
- directory_tree           : src/zephyr/ + scripts/governance/ 目录树骨架（01_overview.md，注释列手工维护，生成器跳过）
- dependency_stats         : depgraph DB 节点/边/域统计（01_overview.md）
- external_deps            : pyproject.toml [project.dependencies] 表（01_overview.md）
- module_counts            : module_id_registry.yaml 注册数 + 包/目录计数（02_repository_and_modules.md）
- py_file_total            : src/zephyr + scripts/governance + tests .py 文件计数（02_repository_and_modules.md）
- table_counts             : table_registry 内存加载按数据库分组（03_data_layer.md）
- task_counts              : data_sources_registry.yaml 数据源清单（04_data_sources.md）
- domain_list              : depgraph domains 表 + nodes 按域聚合（05_trading_domains.md）
- gate_counts              : commit_gates 目录门禁 .py 计数（06_governance_and_infra.md）
- governance_script_counts : 12 维度审计脚本数表（06_governance_and_infra.md）
- edge_stats               : depgraph edges 按 dep_type/跨域聚合（07_dependencies.md）

调用方式：
    python -m scripts.governance.d5_architecture.generators.generate_code_wiki_stats
    python scripts/governance/d5_architecture/generators/generate_code_wiki_stats.py
    python scripts/governance/d5_architecture/generators/generate_code_wiki_stats.py --block dependency_stats

外部钩子（供 generate_project_depgraph.py 成功后调用）：
    from generate_code_wiki_stats import post_depgraph_refresh_hook
    post_depgraph_refresh_hook()  # 非阻断，内部捕获所有异常
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G-WIKI: 自动同步 04 下 8 文件 12 个 AUTO 标记块的统计数据'
dimensions:
- D5
priority: P2
timeout_seconds: 90
warn_only: false
"""


import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import PgConnExecuteWrapper, get_depgraph_pg_connection  # noqa: E402
from _shared.constants import EXIT_FINDINGS
from _common import DB_DISPLAY_NAME  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402
# 治本（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase A3，2026-07-31）：移除内联
# DB_DISPLAY_NAME 定义——原注释谎称"避免 import _common 触发 IMPORT-INTEGRITY
# worktree 误报"，实证 18 个 sibling generators 均成功 from _common import
# DB_DISPLAY_NAME，该借口不成立（陈旧 worktree 兼容代码已无必要）。

# ============================================================
# 目标文档（半自动维护：生成器只更新 AUTO 标记块内内容）
# ============================================================

# 04_architecture_principles_decisions 根目录（README.md 与 project_handbook/ 的公共父）
_BASE_DIR = (
    REPO_ROOT
    / "docs"
    / "02_enterprise_architecture"
    / "04_architecture_principles_decisions"
)

# 目标文件 → 该文件中需刷新的 AUTO 块名清单（路径相对 _BASE_DIR，顺序即刷新顺序）
_TARGETS: dict[str, list[str]] = {
    "README.md": ["project_snapshot"],
    "project_handbook/01_overview.md": ["directory_tree", "dependency_stats", "external_deps"],
    "project_handbook/02_repository_and_modules.md": ["module_counts", "py_file_total"],
    "project_handbook/03_data_layer.md": ["table_counts"],
    "project_handbook/04_data_sources.md": ["task_counts"],
    "project_handbook/05_trading_domains.md": ["domain_list"],
    "project_handbook/06_governance_and_infra.md": ["gate_counts", "governance_script_counts"],
    "project_handbook/07_dependencies.md": ["edge_stats"],
}

# ============================================================
# SQL 集中化（NO-BARE-SQL 门禁要求：SQL 提取到模块级常量）
# ============================================================

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
# 域清单（含节点聚合）；domain_name/layer_id 若不存在则降级（见 collect_domain_list）
SQL_DOMAIN_LIST_FULL = (
    "SELECT d.domain_id, d.domain_name, d.layer_id, "
    "COUNT(n.node_id) AS node_cnt "
    "FROM domains d "
    "LEFT JOIN nodes n ON n.domain_id = d.domain_id "
    "GROUP BY d.domain_id, d.domain_name, d.layer_id "
    "ORDER BY node_cnt DESC, d.domain_id"
)
SQL_DOMAIN_LIST_FALLBACK = (
    "SELECT d.domain_id, COUNT(n.node_id) AS node_cnt "
    "FROM domains d "
    "LEFT JOIN nodes n ON n.domain_id = d.domain_id "
    "GROUP BY d.domain_id "
    "ORDER BY node_cnt DESC, d.domain_id"
)
# 边按 dep_type 聚合
SQL_EDGES_BY_TYPE = (
    "SELECT dep_type, COUNT(*) AS cnt "
    "FROM edges "
    "WHERE dep_type IS NOT NULL AND dep_type != '' "
    "GROUP BY dep_type "
    "ORDER BY cnt DESC"
)
# 跨域边计数（两端节点 domain_id 不同）
SQL_CROSS_DOMAIN_EDGES = (
    "SELECT COUNT(*) AS cnt FROM edges e "
    "JOIN nodes nf ON nf.node_id = e.from_node_id "
    "JOIN nodes nt ON nt.node_id = e.to_node_id "
    "WHERE nf.domain_id IS NOT NULL AND nt.domain_id IS NOT NULL "
    "AND nf.domain_id != nt.domain_id"
)

# AUTO 标记块正则：匹配 <!-- AUTO-START:name -->...<!-- AUTO-END:name --> 之间的内容
_BLOCK_RE_TEMPLATE = r"(<!-- AUTO-START:{name} -->\n)(.*?)(<!-- AUTO-END:{name} -->)"


# ============================================================
# 数据采集函数
# ============================================================


def collect_directory_tree() -> str:
    """块 directory_tree：src/zephyr/ + scripts/governance/ 目录树骨架。

    注释列是手工维护的双语说明，生成器若强行覆盖会破坏人工翻译。
    策略：生成器跳过此块（返回空串表示不更新），由人工维护。

    Returns:
        空字符串（此块由手工维护，生成器不自动覆盖注释列）。
    """
    return ""


def collect_governance_script_counts() -> str:
    """块 governance_script_counts：扫描 scripts/governance/d*/ 目录的 .py 文件数。

    自动生成维度+脚本数表。职责列的中英文翻译是手工维护的（在 _DIMENSION_LABELS 里）。

    Returns:
        Markdown 表格字符串（含表头+数据行）。
    """
    gov_dir = REPO_ROOT / "scripts" / "governance"

    # 维度目录 → 中英文职责描述（手工维护的翻译表）
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
        py_files = [f for f in dim_dir.glob("*.py") if f.name != "__init__.py"]
        count = len(py_files)
        total += count
        zh, en = _DIMENSION_LABELS.get(dim_key, (dim_key, dim_key))
        rows.append(f"| {dim_key} | {zh} / {en} | {count} |")

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

    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记

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


def collect_project_snapshot() -> str:
    """块 project_snapshot：README.md 顶部的 depgraph 关键统计精简快照。

    与 dependency_stats 同源（depgraph PG），但输出更精简，适合 README 顶部速览。

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
        cur = conn.execute(SQL_ORPHAN_NODES)
        orphan_count = cur.fetchone()["cnt"]
        cur = conn.execute(SQL_NODES_BY_STATUS)
        status_rows = cur.fetchall()
    finally:
        conn.close()

    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    # 计算运营态占比
    production_cnt = sum(r["cnt"] for r in status_rows if r["build_status"] in ("stable", "generated"))
    production_pct = round(production_cnt * 100 / node_count, 1) if node_count else 0

    lines: list[str] = [f"<!-- 数据源：{DB_DISPLAY_NAME} | 最后同步：{sync_date} -->", ""]
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    lines.append(f"| 功能域 / Domains | {domain_count} |")
    lines.append(f"| 代码节点 / Nodes | {node_count} |")
    lines.append(f"| 依赖边 / Edges | {edge_count} |")
    lines.append(f"| 孤儿节点 / Orphans | {orphan_count} |")
    lines.append(f"| 运营态占比 / Production ratio | {production_pct}%（stable+generated） |")
    return "\n".join(lines)


def collect_external_deps() -> str:
    """块 external_deps：从 pyproject.toml [project.dependencies] 生成依赖表。

    Returns:
        Markdown 表格字符串。
    """
    pyproject = REPO_ROOT / "pyproject.toml"
    import tomllib

    with open(pyproject, "rb") as f:
        data = tomllib.load(f)
    deps = data.get("project", {}).get("dependencies", [])

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

    rows: list[str] = ["| 依赖 | 用途 |", "|------|------|"]
    for dep in deps:
        stripped = dep.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"^([a-zA-Z0-9_-]+)", stripped)
        if not match:
            continue
        dep_name = match.group(1).lower()
        usage = _DEP_USAGE.get(dep_name, "— / —")
        rows.append(f"| `{stripped}` | {usage} |")
    return "\n".join(rows)


def collect_module_counts() -> str:
    """块 module_counts：module_id_registry.yaml 注册数 + src/zephyr 包/目录计数。

    Returns:
        Markdown 表格字符串。
    """
    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    registry_yaml = REPO_ROOT / "architecture_model" / "module_id_registry.yaml"
    total_registered = "—"
    if registry_yaml.exists():
        text = registry_yaml.read_text(encoding="utf-8")
        m = re.search(r"^total_registered:\s*(\d+)", text, re.MULTILINE)
        if m:
            total_registered = m.group(1)

    src_zephyr = REPO_ROOT / "src" / "zephyr"
    top_packages = [p for p in src_zephyr.iterdir() if p.is_dir() and not p.name.startswith("__")]

    gov_scripts = sum(
        1 for f in (REPO_ROOT / "scripts" / "governance").rglob("*.py") if f.name != "__init__.py"
    )

    lines: list[str] = []
    lines.append(f"<!-- 数据源：module_id_registry.yaml + 文件系统扫描 | 最后同步：{sync_date} -->")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    lines.append(f"| module_id 注册数 / Registered module_ids | {total_registered} |")
    lines.append(f"| src/zephyr 一级子包 / Top-level packages | {len(top_packages)} |")
    lines.append(f"| scripts/governance .py 总数 / Governance scripts | {gov_scripts} |")
    return "\n".join(lines)


def collect_py_file_total() -> str:
    """块 py_file_total：src/zephyr + scripts/governance + tests 的 .py 文件计数。

    Returns:
        Markdown 表格字符串。
    """
    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记

    def _count_py(root: Path) -> int:
        if not root.exists():
            return 0
        return sum(1 for f in root.rglob("*.py") if f.name != "__init__.py")

    src_cnt = _count_py(REPO_ROOT / "src" / "zephyr")
    gov_cnt = _count_py(REPO_ROOT / "scripts" / "governance")
    tests_cnt = _count_py(REPO_ROOT / "tests")
    total = src_cnt + gov_cnt + tests_cnt

    lines: list[str] = []
    lines.append(f"<!-- 数据源：文件系统扫描 | 最后同步：{sync_date} -->")
    lines.append("")
    lines.append("| 目录 | .py 文件数（排除 __init__.py） |")
    lines.append("|------|------|")
    lines.append(f"| `src/zephyr/` | {src_cnt} |")
    lines.append(f"| `scripts/governance/` | {gov_cnt} |")
    lines.append(f"| `tests/` | {tests_cnt} |")
    lines.append(f"| **合计 / Total** | **{total}** |")
    return "\n".join(lines)


def collect_table_counts() -> str:
    """块 table_counts：table_registry 内存加载按数据库分组计数。

    优先调 TableRegistry.get_registry().all_tables()，按 "{database}.{table}" 前缀分组。
    import 或加载失败时降级到直接查 depgraph (PG) + governance.db (SQLite) 的表数。

    Returns:
        Markdown 表格字符串。
    """
    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    lines: list[str] = [f"<!-- 数据源：table_registry 内存加载 | 最后同步：{sync_date} -->", ""]

    by_db: dict[str, int] = {}
    registry_ok = False
    try:
        from zephyr.data.table_registry import get_registry  # noqa: m11-perm-manual-legitimate  只读访问已注册表名

        tables = get_registry().all_tables()
        for fqtn in tables:
            prefix = fqtn.split(".", 1)[0] if "." in fqtn else "(unqualified)"
            by_db[prefix] = by_db.get(prefix, 0) + 1
        registry_ok = True
    except Exception as e:  # noqa: m12-broad-except-legitimate  降级路径，记录原因后用 DB 直查兜底
        lines.append(f"<!-- table_registry 加载失败，降级直查 DB：{e} -->")
        by_db = _count_tables_from_dbs()

    lines.append("| 数据库 / Database | 表数 / Tables |")
    lines.append("|------|------|")
    if by_db:
        for db_name in sorted(by_db):
            lines.append(f"| `{db_name}` | {by_db[db_name]} |")
        lines.append(f"| **合计 / Total** | **{sum(by_db.values())}** |")
    else:
        lines.append("| （无注册表） | — |")

    if not registry_ok:
        lines.append("")
        lines.append(
            "> ⚠️ table_registry 不可用，上表为直查 DB 结果（不含 ClickHouse 业务表，需 CH 连接）。"
        )
    return "\n".join(lines)


def _count_tables_from_dbs() -> dict[str, int]:
    """降级：直接查 depgraph (PG) + governance.db (SQLite) 的用户表数。

    Returns:
        {database_name: table_count} 字典（CH 不可达则不计）。
    """
    result: dict[str, int] = {}
    # depgraph (PostgreSQL) 用户表
    try:
        conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
        try:
            cur = conn.execute(
                "SELECT COUNT(*) AS cnt FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
            )
            result[DB_DISPLAY_NAME] = cur.fetchone()["cnt"]
        finally:
            conn.close()
    except Exception:  # noqa: m12-broad-except-legitimate  降级兜底
        pass
    # governance.db (SQLite)
    try:
        import sqlite3

        from zephyr.shared.io.paths import DB_PATH

        if DB_PATH.exists():
            con = sqlite3.connect(str(DB_PATH))
            try:
                cur = con.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'"
                )
                result["governance.db (SQLite)"] = cur.fetchone()[0]
            finally:
                con.close()
    except Exception:  # noqa: m12-broad-except-legitimate  降级兜底
        pass
    return result


def collect_task_counts() -> str:
    """块 task_counts：data_sources_registry.yaml 数据源清单与计数。

    用 yaml.safe_load 解析（比顺序正则稳健，不受字段顺序影响）。

    Returns:
        Markdown 表格字符串。
    """
    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    registry_yaml = REPO_ROOT / "architecture_model" / "data" / "data_sources_registry.yaml"

    lines: list[str] = [
        f"<!-- 数据源：data_sources_registry.yaml | 最后同步：{sync_date} -->",
        "",
        "| Provider ID | 名称 | 类型 | 状态 |",
        "|-------------|------|------|------|",
    ]
    total = 0
    if registry_yaml.exists():
        import yaml

        with open(registry_yaml, "rb") as f:
            data = yaml.safe_load(f)
        for ds in data.get("data_sources", []):
            ds_id = ds.get("id", "?")
            name = ds.get("name", "—")
            dtype = ds.get("type", "—")
            status = ds.get("status", "—")
            lines.append(f"| `{ds_id}` | {name} | {dtype} | {status} |")
            total += 1
    lines.append(f"| **合计 / Total providers** | | | **{total}** |")
    if total == 0:
        lines.append("> ⚠️ 未解析到数据源，请检查 data_sources_registry.yaml 结构。")
    return "\n".join(lines)


def collect_domain_list() -> str:
    """块 domain_list：depgraph domains 表 + nodes 按域聚合。

    domain_name/layer_id 列若不存在则降级只显示 domain_id + 节点数。

    Returns:
        Markdown 表格字符串。
    """
    conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
    try:
        try:
            cur = conn.execute(SQL_DOMAIN_LIST_FULL)
            rows = cur.fetchall()
            has_extra = True
        except Exception:
            cur = conn.execute(SQL_DOMAIN_LIST_FALLBACK)
            rows = cur.fetchall()
            has_extra = False
    finally:
        conn.close()

    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    lines: list[str] = [f"<!-- 数据源：{DB_DISPLAY_NAME} | 最后同步：{sync_date} -->", ""]
    if has_extra:
        lines.append("| 域 ID | 域名 | 层 | 节点数 |")
        lines.append("|-------|------|----|-------|")
        for r in rows:
            lines.append(
                f"| `{r['domain_id']}` | {r['domain_name'] or '—'} | "
                f"{r['layer_id'] or '—'} | {r['node_cnt']} |"
            )
    else:
        lines.append("| 域 ID | 节点数 |")
        lines.append("|-------|-------|")
        for r in rows:
            lines.append(f"| `{r['domain_id']}` | {r['node_cnt']} |")
    lines.append(f"\n**合计 {len(rows)} 个域**")
    return "\n".join(lines)


def collect_gate_counts() -> str:
    """块 gate_counts：扫描 src/zephyr/gov_enforcement/commit_gates/ 目录门禁 .py 计数。

    Returns:
        Markdown 表格字符串。
    """
    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    gates_dir = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "commit_gates"

    py_count = 0
    if gates_dir.exists():
        py_count = sum(
            1 for f in gates_dir.glob("*.py") if f.name != "__init__.py"
        )

    lines: list[str] = [f"<!-- 数据源：commit_gates 目录扫描 | 最后同步：{sync_date} -->", ""]
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    lines.append(f"| commit_gates 目录 / Directory | `{gates_dir.relative_to(REPO_ROOT)}` |")
    lines.append(f"| 门禁 .py 文件数 / Gate files (excl. __init__) | {py_count} |")
    lines.append("")
    lines.append(
        "> 门禁按 priority 升序执行（AST/diff/路径/命名/依赖/blueprint 格式/depgraph 预登记/能力反查等维度）。"
    )
    return "\n".join(lines)


def collect_edge_stats() -> str:
    """块 edge_stats：depgraph edges 按 dep_type/跨域聚合。

    Returns:
        Markdown 表格字符串。
    """
    conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
    try:
        cur = conn.execute(SQL_EDGES_BY_TYPE)
        type_rows = cur.fetchall()
        cur = conn.execute(SQL_CROSS_DOMAIN_EDGES)
        cross_cnt = cur.fetchone()["cnt"]
        cur = conn.execute(SQL_COUNT_EDGES)
        total_edges = cur.fetchone()["cnt"]
    finally:
        conn.close()

    sync_date = datetime.now(UTC).strftime("%Y-%m-%d")  # noqa: m46-time  生成器输出同步日期标记
    lines: list[str] = [f"<!-- 数据源：{DB_DISPLAY_NAME} | 最后同步：{sync_date} -->", ""]
    lines.append("| dep_type | 边数 / Edges |")
    lines.append("|----------|------|")
    listed = 0
    for r in type_rows:
        lines.append(f"| `{r['dep_type']}` | {r['cnt']} |")
        listed += r["cnt"]
    untyped = total_edges - listed
    if untyped > 0:
        lines.append(f"| （空/未分类） | {untyped} |")
    lines.append(f"| **合计 / Total** | **{total_edges}** |")
    lines.append("")
    lines.append(
        f"**跨域边 / Cross-domain edges：{cross_cnt}** 条"
        f"（两端节点 domain_id 不同的依赖边）。"
    )
    return "\n".join(lines)


# 块名 → 采集函数映射（directory_tree 跳过：注释列手工维护）
_BLOCK_COLLECTORS: dict[str, callable] = {
    "project_snapshot": collect_project_snapshot,
    "dependency_stats": collect_dependency_stats,
    "external_deps": collect_external_deps,
    "module_counts": collect_module_counts,
    "py_file_total": collect_py_file_total,
    "table_counts": collect_table_counts,
    "task_counts": collect_task_counts,
    "domain_list": collect_domain_list,
    "gate_counts": collect_gate_counts,
    "governance_script_counts": collect_governance_script_counts,
    "edge_stats": collect_edge_stats,
    # directory_tree：注释列手工维护，生成器跳过（避免破坏双语注释）
}

_ALL_BLOCK_NAMES = ["directory_tree"] + list(_BLOCK_COLLECTORS.keys())


# ============================================================
# AUTO 块替换引擎
# ============================================================


def replace_block(content: str, block_name: str, new_inner: str) -> tuple[str, bool]:
    """替换 content 中指定 AUTO 块的内嵌内容。

    只替换 START 标记行之后、END 标记行之前的全部内容。标记行本身保留。

    Args:
        content: 目标文档的完整文本。
        block_name: AUTO 块名（如 "dependency_stats"）。
        new_inner: 要写入块内的新内容。

    Returns:
        (更新后的 content, 是否找到了块并替换)
    """
    pattern = _BLOCK_RE_TEMPLATE.format(name=re.escape(block_name))
    regex = re.compile(pattern, re.DOTALL)

    def _replace(match: re.Match) -> str:
        start_line = match.group(1)  # <!-- AUTO-START:name -->\n
        return f"{start_line}{new_inner}\n{match.group(3)}"

    new_content, count = regex.subn(_replace, content, count=1)
    return new_content, count > 0


# ============================================================
# 核心刷新逻辑（main 与外部钩子共用）
# ============================================================


def _refresh_all_targets(
    block_filter: str = "all", handbook_dir: Path | None = None
) -> dict[str, list[str]]:
    """刷新所有目标文件的 AUTO 块。

    Args:
        block_filter: "all" 或指定块名（只更新含该块的文件）。
        handbook_dir: 目标目录（默认用模块级 _HANDBOOK_DIR；CLI 可覆盖）。

    Returns:
        {文件名: [已更新块名...]} 字典。
    """
    base_dir = handbook_dir if handbook_dir is not None else _BASE_DIR
    updated_summary: dict[str, list[str]] = {}
    skipped_summary: dict[str, list[str]] = {}

    for fname, block_names in _TARGETS.items():
        # 块过滤：非 all 时只处理含该块的文件
        if block_filter != "all" and block_filter not in block_names:
            continue

        wiki_path = base_dir / fname
        if not wiki_path.exists():
            print(f"[WARN] 目标文档不存在：{wiki_path}", file=sys.stderr)
            skipped_summary[fname] = ["(文件缺失)"]
            continue

        content = wiki_path.read_text(encoding="utf-8")
        original = content
        file_updated: list[str] = []
        file_skipped: list[str] = []

        for block_name in block_names:
            if block_name == "directory_tree":
                file_skipped.append(f"{block_name}（手工维护双语注释）")
                continue

            collector = _BLOCK_COLLECTORS.get(block_name)
            if collector is None:
                print(f"[WARN] 未知块：{block_name}", file=sys.stderr)
                continue

            try:
                new_inner = collector()
            except Exception as e:
                print(f"[ERROR] 采集块 {block_name} 数据失败：{e}", file=sys.stderr)
                file_skipped.append(f"{block_name}（采集失败）")
                continue

            content, found = replace_block(content, block_name, new_inner)
            if found:
                file_updated.append(block_name)
            else:
                print(f"[WARN] 块 {block_name} 标记未在 {fname} 中找到，跳过", file=sys.stderr)
                file_skipped.append(f"{block_name}（标记缺失）")

        # 幂等写：内容有变化才写回
        if content != original:
            wiki_path.write_text(content, encoding="utf-8")
            print(f"[OK] 更新 {fname}：{', '.join(file_updated)}")
        else:
            print(f"[OK] {fname} 无变化（已幂等）")

        if file_updated:
            updated_summary[fname] = file_updated
        if file_skipped:
            skipped_summary[fname] = file_skipped

    if skipped_summary:
        all_skipped = [f"{fn}:{b}" for fn, bs in skipped_summary.items() for b in bs]
        print(f"[INFO] 跳过块：{', '.join(all_skipped)}")

    return updated_summary


# ============================================================
# 外部钩子入口（供 generate_project_depgraph.py 成功后调用）
# ============================================================


def post_depgraph_refresh_hook() -> None:
    """depgraph 刷新成功后的非阻断钩子：刷新 project_handbook/ 统计块。

    设计为完全非阻断：捕获所有异常仅打印 warning，绝不影响调用方退出码。
    供 generate_project_depgraph.py main() 末尾调用。
    """
    try:
        print("[DEPGRAPH] post-refresh hook: 同步 project_handbook 统计块 ...")
        _refresh_all_targets(block_filter="all")
        print("[DEPGRAPH] post-refresh hook: 完成")
    except Exception as e:  # noqa: m12-broad-except-legitimate  钩子必须非阻断
        print(f"[DEPGRAPH] post-refresh hook skipped (非阻断): {e}", file=sys.stderr)


# ============================================================
# 主入口
# ============================================================


def main() -> None:
    """入口：同步 04 根下 8 文件 12 个 AUTO 块的统计数据。"""
    parser = argparse.ArgumentParser(
        description="G-WIKI: 自动同步 04_architecture_principles_decisions 下 8 文件 12 个 AUTO 标记块的统计数据"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="04_architecture_principles_decisions 根目录路径（默认：内置路径）",
    )
    parser.add_argument(
        "--block",
        type=str,
        choices=["all"] + _ALL_BLOCK_NAMES,
        default="all",
        help="只更新指定块（默认：all）",
    )
    args = parser.parse_args()

    base_dir = Path(args.base_dir) if args.base_dir else None
    if base_dir is not None and not base_dir.exists():
        print(f"[ERROR] 04 目录不存在：{base_dir}", file=sys.stderr)
        sys.exit(EXIT_FINDINGS)

    _refresh_all_targets(block_filter=args.block, handbook_dir=base_dir)


if __name__ == "__main__":
    main()
