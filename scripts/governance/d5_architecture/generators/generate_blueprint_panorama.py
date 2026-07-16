#!/usr/bin/env python
# [BLUEPRINT] MOD-GOV-029 | docs/03_modules/_domain_governance/panorama_alignment_engine/blueprint.md | §FP-panorama-gen
# [MODULE] scripts.governance.d5_architecture.generators.generate_blueprint_panorama
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.persistence.dataflowgraph_schema (get_dataflowgraph_pg_connection); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); d5_architecture.panorama_common (weighted_domain_vote, min_maturity)
# [CONSUMERS] CI自动触发;人工审查蓝图 §0.6;sync_panorama_module 后续可调用
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读PG(零写入);只写蓝图 §0.6 章节(不动 frontmatter/不动其他章节);输出幂等(相同输入→相同输出);depgraph无此模块→跳过;蓝图不存在→跳过;§0.6 不存在则插入,存在则替换
# [MODIFY-GUARD] generate_for_module/generate_all 为对外入口;SQL 常量集中在模块级 _SQL_*;§0.6 块边界由 _S06_BLOCK_RE 定义(修改需同步模板)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph不可达→exit 1;depgraph无此模块→exit 3(跳过);蓝图不存在→exit 0(标记缺失跳过);DB异常→exit 4
# [TESTS] tests/governance/test_generate_blueprint_panorama.py
# [TTL] permanent
# [ARCH-REF] #ARCH-053 #ARCH-056 #ARCH-MM-001
# 真源说明：本生成器从 depgraph / dataflowgraph / decisiongraph (PostgreSQL) 读取三图节点，
# 从 docs/03_modules/ 下的蓝图文件 frontmatter 采集第四张图（blueprint），
# 生成 §0.6 四图对齐视图（四图位置表 + 四核心字段对比表）并写入蓝图文件。
# 详见 AGENTS.md §真源分类（11.0.2）+ ARCH-053 / ARCH-056 裁定 + 蓝图模板 v2.1.0 §0.6。
"""G-panorama-gen: 蓝图 §0.6 四图对齐视图生成器（ARCH-053 + ARCH-056 + 模板 v2.1.0）

依据：蓝图模板 v2.1.0 §0.6 格式定义；ARCH-053 裁定（2026-07-06）；ARCH-056 四图升级（2026-07-09）

功能：
  - 从 depgraph.nodes 读取模块核心字段（build_status, domain_id, file_count）—— 加权投票聚合
  - 从 dataflow_datasets + dataflow_jobs 读取模块的数据流节点计数
  - 从 decision_nodes + decision_layers 读取模块的决策节点计数
  - 从蓝图文件 frontmatter 采集第四张图字段（module_id, responsibility_domain, build_status）
  - 生成 §0.6 四图对齐视图（两个表格）并写入蓝图文件
  - 幂等：多次运行同一模块结果相同（不会重复插入 §0.6）

定位：写入型生成器（只写蓝图 §0.6 章节，不动 frontmatter / 不动其他章节）。
depgraph 是架构数据真源（SSoT），蓝图是派生视图，冲突时以 depgraph 为准。

用法
----
    python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-INF-039
    python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py --all
    python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py --all --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
_SRC_DIR = _REPO_ROOT / "src"
for _p in (str(_REPO_ROOT), str(_SRC_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, str(_p))

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    get_dataflowgraph_pg_connection,
)
from zephyr.governance.persistence.decisiongraph_schema import (  # noqa: E402
    get_decisiongraph_pg_connection,
)

try:
    from d5_architecture.panorama_common import (
        min_maturity as _min_mat,
        weighted_domain_vote,
    )
except ImportError:
    import sys as _sys
    _pc_path = str(Path(__file__).resolve().parents[1])  # d5_architecture/
    if _pc_path not in _sys.path:
        _sys.path.insert(0, _pc_path)
    from panorama_common import (  # noqa: E402
        min_maturity as _min_mat,
        weighted_domain_vote,
    )


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 蓝图扫描根目录（与 blueprint_frontmatter_reconciler._BP_SCAN_ROOT 一致）
_BP_SCAN_ROOT = _REPO_ROOT / "docs" / "03_modules"

# 跳过的文件名（非模块蓝图文件，与 align_panoramas._BP_SKIP_NAMES 一致）
_BP_SKIP_NAMES = {"index.md"}

# frontmatter 正则（与 blueprint_frontmatter_reconciler._FRONTMATTER_RE 一致）
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# §0.6 块边界正则：匹配从 "### §0.6" 或 "## §0.6" 头到下一个 "---" 分隔线或 "## " 标题
# 使用非贪婪匹配 + 前瞻，确保只匹配 §0.6 内容（不含闭合的 "---"）
# 不含前导 \n：避免替换时引入多余换行，保证幂等性（insert 与 replace 产生相同结构）
_S06_BLOCK_RE = re.compile(
    r"(#{2,3} §0\.6[^\n]*\n).*?(?=\n---\s*\n|\n## [^#]|\Z)",
    re.DOTALL,
)

# §0.1 表格行正则：匹配 "| N | ..." 格式的数据行（N 为行号）
_S01_TABLE_ROW_RE = re.compile(r"^\|\s*\d+\s*\|", re.MULTILINE)


# ---------------------------------------------------------------------------
# SQL 常量（SQL 集中化，§5.160.2）
# ---------------------------------------------------------------------------
# 注意：不使用 LIMIT 1 — 同一 blueprint_id 可有多行（跨域模块），
# _fetch_depgraph_module 在 Python 中用加权投票聚合，
# 与 align_panoramas._fetch_depgraph_nodes 聚合策略一致。
_SQL_QUERY_DEPGRAPH_MODULE = (
    "SELECT blueprint_id, path, design_maturity, build_status, domain_id "
    "FROM nodes WHERE blueprint_id = %s "
    "ORDER BY (path IS NULL), path"
)
_SQL_COUNT_DEPGRAPH_FILES = (
    "SELECT COUNT(*) FROM nodes WHERE blueprint_id = %s"
)
_SQL_COUNT_DATAFLOW_DATASETS = (
    "SELECT COUNT(*) FROM dataflow_datasets WHERE module_id = %s"
)
_SQL_COUNT_DATAFLOW_JOBS = (
    "SELECT COUNT(*) FROM dataflow_jobs WHERE module_id = %s"
)
_SQL_DATAFLOW_STATUS = (
    "SELECT design_maturity, build_status FROM dataflow_jobs "
    "WHERE module_id = %s AND design_maturity IS NOT NULL "
    "ORDER BY (design_maturity = 'design') DESC LIMIT 1"
)
_SQL_COUNT_DECISION_NODES = (
    "SELECT COUNT(*) FROM decision_nodes WHERE module_id = %s"
)
_SQL_COUNT_DECISION_LAYERS = (
    "SELECT COUNT(*) FROM decision_layers WHERE module_id = %s"
)
_SQL_DECISION_STATUS = (
    "SELECT design_maturity, build_status FROM decision_nodes "
    "WHERE module_id = %s AND design_maturity IS NOT NULL "
    "ORDER BY (design_maturity = 'design') DESC LIMIT 1"
)
_SQL_QUERY_ALL_MODULES = (
    "SELECT DISTINCT blueprint_id FROM nodes "
    "WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"
)


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass
class DepgraphModuleInfo:
    """depgraph 中模块的聚合信息（加权投票聚合，与 align_panoramas 一致）。"""

    module_id: str
    domain_id: str  # 加权投票值（可能为空）
    design_maturity: str  # min_maturity（最 design 的状态）
    build_status: str  # 第一个非空
    file_count: int  # nodes 表中此 blueprint_id 的行数


@dataclass
class DataflowModuleInfo:
    """dataflow 中模块的节点计数。"""

    dataset_count: int
    job_count: int
    design_maturity: str  # 代表性状态（最 design 优先）
    build_status: str


@dataclass
class DecisionModuleInfo:
    """decision 中模块的节点计数。"""

    node_count: int
    layer_count: int
    design_maturity: str
    build_status: str


@dataclass
class BlueprintFrontmatter:
    """蓝图文件 frontmatter 采集结果。"""

    module_id: str
    responsibility_domain: str
    design_maturity: str
    build_status: str
    construction_progress: str
    status: str  # frontmatter.status（Active/Draft 等）
    file_path: Path
    content: str


@dataclass
class ModulePanorama:
    """单模块四图全景数据。"""

    module_id: str
    depgraph: DepgraphModuleInfo | None
    dataflow: DataflowModuleInfo | None
    decision: DecisionModuleInfo | None
    blueprint: BlueprintFrontmatter | None


# ---------------------------------------------------------------------------
# 数据采集：depgraph
# ---------------------------------------------------------------------------


def _fetch_depgraph_module(module_id: str) -> DepgraphModuleInfo | None:
    """从 depgraph.nodes 查询模块核心字段（加权投票聚合）。

    聚合策略与 align_panoramas._fetch_depgraph_nodes 一致：
    - domain_id: 加权投票（测试文件降权，平局字母序）
    - design_maturity: 取最 design 的状态（design < prototype < production）
    - build_status: 取第一个非空
    - file_count: COUNT(*) 所有行
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_QUERY_DEPGRAPH_MODULE, (module_id,))
            rows = cur.fetchall()
            if not rows:
                return None
            cur.execute(_SQL_COUNT_DEPGRAPH_FILES, (module_id,))
            count_row = cur.fetchone()
            file_count = (
                count_row[0] if count_row else len(rows)
            )
    finally:
        conn.close()

    maturities: list[str] = []
    build_status = ""
    for row in rows:
        if isinstance(row, dict):
            dm = row.get("design_maturity")
            bs = row.get("build_status")
        else:
            dm = row[2] if len(row) > 2 else None
            bs = row[3] if len(row) > 3 else None
        if dm:
            maturities.append(dm)
        if not build_status and bs:
            build_status = bs

    domain_id = weighted_domain_vote(rows)
    design_maturity = _min_mat(maturities) if maturities else ""
    return DepgraphModuleInfo(
        module_id=module_id,
        domain_id=domain_id or "",
        design_maturity=design_maturity or "",
        build_status=build_status or "",
        file_count=file_count,
    )


# ---------------------------------------------------------------------------
# 数据采集：dataflow
# ---------------------------------------------------------------------------


def _fetch_dataflow_module(module_id: str) -> DataflowModuleInfo | None:
    """从 dataflow_datasets + dataflow_jobs 查询模块的数据流节点计数。"""
    conn = get_dataflowgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_COUNT_DATAFLOW_DATASETS, (module_id,))
            ds_row = cur.fetchone()
            dataset_count = ds_row[0] if ds_row else 0

            cur.execute(_SQL_COUNT_DATAFLOW_JOBS, (module_id,))
            job_row = cur.fetchone()
            job_count = job_row[0] if job_row else 0

            design_maturity = ""
            build_status = ""
            if job_count > 0:
                cur.execute(_SQL_DATAFLOW_STATUS, (module_id,))
                status_row = cur.fetchone()
                if status_row:
                    if isinstance(status_row, dict):
                        design_maturity = status_row.get("design_maturity") or ""
                        build_status = status_row.get("build_status") or ""
                    else:
                        design_maturity = status_row[0] if len(status_row) > 0 else ""
                        build_status = status_row[1] if len(status_row) > 1 else ""
    finally:
        conn.close()

    if dataset_count == 0 and job_count == 0:
        return None
    return DataflowModuleInfo(
        dataset_count=dataset_count,
        job_count=job_count,
        design_maturity=design_maturity,
        build_status=build_status,
    )


# ---------------------------------------------------------------------------
# 数据采集：decision
# ---------------------------------------------------------------------------


def _fetch_decision_module(module_id: str) -> DecisionModuleInfo | None:
    """从 decision_nodes + decision_layers 查询模块的决策节点计数。"""
    conn = get_decisiongraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_COUNT_DECISION_NODES, (module_id,))
            node_row = cur.fetchone()
            node_count = node_row[0] if node_row else 0

            cur.execute(_SQL_COUNT_DECISION_LAYERS, (module_id,))
            layer_row = cur.fetchone()
            layer_count = layer_row[0] if layer_row else 0

            design_maturity = ""
            build_status = ""
            if node_count > 0:
                cur.execute(_SQL_DECISION_STATUS, (module_id,))
                status_row = cur.fetchone()
                if status_row:
                    if isinstance(status_row, dict):
                        design_maturity = status_row.get("design_maturity") or ""
                        build_status = status_row.get("build_status") or ""
                    else:
                        design_maturity = status_row[0] if len(status_row) > 0 else ""
                        build_status = status_row[1] if len(status_row) > 1 else ""
    finally:
        conn.close()

    if node_count == 0 and layer_count == 0:
        return None
    return DecisionModuleInfo(
        node_count=node_count,
        layer_count=layer_count,
        design_maturity=design_maturity,
        build_status=build_status,
    )


# ---------------------------------------------------------------------------
# 数据采集：blueprint（文件扫描）
# ---------------------------------------------------------------------------


def _parse_simple_frontmatter(content: str) -> dict[str, str]:
    """解析 YAML frontmatter 为扁平 dict（简单实现，跳过嵌套字段）。

    与 align_panoramas._parse_simple_frontmatter 一致。
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}
    fm: dict[str, str] = {}
    for line in match.group(1).split("\n"):
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        v = val.strip().strip('"').strip("'")
        if v and not v.startswith("[") and not v.startswith("{"):
            fm[key.strip()] = v
    return fm


def _find_blueprint_by_scan(module_id: str) -> Path | None:
    """扫描 docs/03_modules/ 下所有文件，通过 frontmatter.module_id 匹配。

    与 blueprint_frontmatter_reconciler._find_blueprint_by_scan 扫描策略一致。
    返回第一个匹配的文件（一个 module_id 通常只有一个蓝图文件）。
    """
    if not _BP_SCAN_ROOT.exists():
        return None
    for fpath in _BP_SCAN_ROOT.rglob("*"):
        if not fpath.is_file() or fpath.name in _BP_SKIP_NAMES:
            continue
        if fpath.suffix != ".md":
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        match = _FRONTMATTER_RE.match(content)
        if not match:
            continue
        for line in match.group(1).split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                if key.strip() == "module_id":
                    v = val.strip().strip('"').strip("'")
                    if v == module_id:
                        return fpath
                    break  # 找到 module_id 行，无论是否匹配都跳过此文件
    return None


def _fetch_blueprint(module_id: str) -> BlueprintFrontmatter | None:
    """从蓝图文件 frontmatter 采集第四张图字段。

    扫描策略与 blueprint_frontmatter_reconciler._find_blueprint_by_scan 一致。
    """
    bp_path = _find_blueprint_by_scan(module_id)
    if bp_path is None:
        return None
    try:
        content = bp_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    fm = _parse_simple_frontmatter(content)
    return BlueprintFrontmatter(
        module_id=fm.get("module_id", ""),
        responsibility_domain=fm.get("responsibility_domain", ""),
        design_maturity=fm.get("design_maturity", ""),
        build_status=fm.get("build_status", ""),
        construction_progress=fm.get("construction_progress", ""),
        status=fm.get("status", ""),
        file_path=bp_path,
        content=content,
    )


def _count_s01_files(content: str) -> int | None:
    """统计 §0.1 代码文件清单表格的数据行数。

    §0.1 表格格式：`| # | 文件名 | ...`，数据行以 `| <数字> |` 开头。
    找不到 §0.1 章节时返回 None（显示为 N/A）。
    """
    # 定位 §0.1 章节
    s01_start = re.search(r"^#{2,3} §0\.1[^\n]*\n", content, re.MULTILINE)
    if not s01_start:
        return None
    # §0.1 结束于下一个同级或更高级标题（## 或 ### §0.2 / §1 等）
    rest = content[s01_start.end():]
    s01_end = re.search(r"\n#{2,3} (?:§0\.[2-9]|§[1-9])", rest)
    s01_body = rest[: s01_end.start()] if s01_end else rest
    rows = _S01_TABLE_ROW_RE.findall(s01_body)
    return len(rows) if rows else None


# ---------------------------------------------------------------------------
# §0.6 内容生成
# ---------------------------------------------------------------------------


def _status_mark(a: str, b: str) -> str:
    """比较两个值是否一致，返回 ✅ 或 ❌。空值视为 N/A（不报冲突）。"""
    if not a and not b:
        return "✅"
    if not a or not b:
        return "—"
    return "✅" if a.strip().lower() == b.strip().lower() else "❌"


def _depgraph_status_str(info: DepgraphModuleInfo) -> str:
    """depgraph 行的状态列：design_maturity（production/design/prototype）。"""
    return info.design_maturity or "N/A"


def _dataflow_status_str(info: DataflowModuleInfo) -> str:
    """dataflow 行的状态列。"""
    if info.design_maturity == "design":
        return "planned"
    return "active" if info.job_count > 0 else "planned"


def _decision_status_str(info: DecisionModuleInfo) -> str:
    """decision 行的状态列：design_maturity。"""
    return info.design_maturity or "N/A"


def _blueprint_status_str(bp: BlueprintFrontmatter) -> str:
    """blueprint 行的状态列：frontmatter.status（Active/Draft）。"""
    s = bp.status.strip()
    if not s:
        return "Draft" if bp.construction_progress == "not_started" else "Active"
    return s


def _render_position_table(pan: ModulePanorama) -> str:
    """渲染四图位置表。"""
    mid = pan.module_id
    lines: list[str] = []
    lines.append("#### 四图位置")
    lines.append("")
    lines.append("| 图 | 位置 | 状态 | 链接 |")
    lines.append("|----|------|------|------|")

    # depgraph
    if pan.depgraph:
        dg_pos = f"`blueprint_id={mid}` 的 {pan.depgraph.file_count} 个 file 节点"
        dg_status = _depgraph_status_str(pan.depgraph)
    else:
        dg_pos = "（无节点）"
        dg_status = "N/A"
    lines.append(
        f"| 依赖图 (depgraph) | {dg_pos} | {dg_status} | "
        f"`extract_depgraph.py --modules {mid}` |"
    )

    # dataflow
    if pan.dataflow:
        df_pos = (
            f"{pan.dataflow.dataset_count} 个 Dataset / "
            f"{pan.dataflow.job_count} 个 Job"
        )
        df_status = _dataflow_status_str(pan.dataflow)
    else:
        df_pos = "（无节点）"
        df_status = "N/A"
    lines.append(
        f"| 数据流图 (dataflow) | {df_pos} | {df_status} | "
        f"`apply_dataflowgraph.py --list-datasets` |"
    )

    # decision
    if pan.decision:
        dc_pos = (
            f"{pan.decision.node_count} 个决策节点 / "
            f"{pan.decision.layer_count} 个决策层"
        )
        dc_status = _decision_status_str(pan.decision)
    else:
        dc_pos = "（无节点）"
        dc_status = "N/A"
    lines.append(
        f"| 决策架构图 (decision) | {dc_pos} | {dc_status} | "
        f"`generate_decision_diagram.py` |"
    )

    # blueprint
    if pan.blueprint:
        bp_status = _blueprint_status_str(pan.blueprint)
    else:
        bp_status = "N/A"
    lines.append("| 蓝图 (blueprint) | 本文件 | {} | — |".format(bp_status))

    return "\n".join(lines)


def _compute_field_consistency(
    dg: DepgraphModuleInfo | None, bp: BlueprintFrontmatter | None
) -> tuple[str, str, str]:
    """计算 file_count 字段的（depgraph 值, 蓝图值, 一致性标记）。

    file_count 是四核心字段中唯一需要数值相等比对（非字符串归一）的字段，
    且蓝图值需从 §0.1 代码文件清单表格派生——逻辑较重，独立函数以降低
    _render_core_fields_table 的圈复杂度（NO-HIGH-COMPLEXITY gate，阈值 15）。
    """
    dg_fc = f"{dg.file_count} 文件" if dg else "N/A"
    s01_count: int | None = None
    if bp:
        s01_count = _count_s01_files(bp.content)
        bp_fc = f"{s01_count} 文件（§0.1）" if s01_count is not None else "N/A"
    else:
        bp_fc = "N/A"
    if dg and s01_count is not None:
        fc_mark = "✅" if dg.file_count == s01_count else "❌"
    else:
        fc_mark = "—"
    return dg_fc, bp_fc, fc_mark


def _render_core_fields_table(pan: ModulePanorama) -> str:
    """渲染四核心字段对比表。"""
    lines: list[str] = []
    lines.append("#### 四核心字段")
    lines.append("")
    lines.append("| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |")
    lines.append("|------|-------------------|--------------------------|:-------:|")

    dg = pan.depgraph
    bp = pan.blueprint

    # module_id
    dg_mid = pan.module_id
    bp_mid = bp.module_id if bp else ""
    lines.append(
        f"| module_id | {dg_mid} | {bp_mid or 'N/A'} | {_status_mark(dg_mid, bp_mid)} |"
    )

    # domain_id
    dg_dom = dg.domain_id if dg else ""
    bp_dom = bp.responsibility_domain if bp else ""
    lines.append(
        f"| domain_id | {dg_dom or 'N/A'} | {bp_dom or 'N/A'} | "
        f"{_status_mark(dg_dom, bp_dom)} |"
    )

    # build_status
    dg_bs = dg.build_status if dg else ""
    bp_bs = bp.build_status if bp else ""
    lines.append(
        f"| build_status | {dg_bs or 'N/A'} | {bp_bs or 'N/A'} | "
        f"{_status_mark(dg_bs, bp_bs)} |"
    )

    # file_count（数值比对 + §0.1 派生，独立函数处理）
    dg_fc, bp_fc, fc_mark = _compute_field_consistency(dg, bp)
    lines.append(f"| file_count | {dg_fc} | {bp_fc} | {fc_mark} |")

    return "\n".join(lines)


def _generate_s06_section(pan: ModulePanorama) -> str:
    """生成完整的 §0.6 章节内容（不含闭合的 --- 分隔线）。

    返回值以 "### §0.6 四图对齐视图" 开头，以 "> 冲突时..." 结尾。
    """
    mid = pan.module_id
    lines: list[str] = []
    lines.append("### §0.6 四图对齐视图")
    lines.append("")
    lines.append(
        "<!-- AUTOGEN: source=depgraph+dataflow+decision, "
        "generator=generate_blueprint_panorama.py, "
        "reconciler=sync_panorama_module.py -->"
    )
    lines.append("")
    lines.append(
        "> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。"
    )
    lines.append(
        f"> 生成命令：`python scripts/governance/d5_architecture/generators/"
        f"generate_blueprint_panorama.py {mid}`"
    )
    lines.append("")
    lines.append(_render_position_table(pan))
    lines.append("")
    lines.append(_render_core_fields_table(pan))
    lines.append("")
    lines.append(
        "> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 蓝图文件更新（幂等：替换或插入 §0.6）
# ---------------------------------------------------------------------------


def _replace_or_insert_s06(content: str, new_s06: str) -> str:
    """替换现有 §0.6 块或在 §1 前插入新的 §0.6 块。

    幂等性保证（insert 与 replace 产生相同结构）：
    - 如 §0.6 已存在：用 new_s06 替换旧内容（从 §0.6 标题到下一个 --- 或 ## 标题之前）
      替换后结构：`...<前置内容>\\n<new_s06>\\n\\n---\\n...` 或 `...\\n<new_s06>\\n\\n## §1...`
    - 如 §0.6 不存在：在 §1 前插入 new_s06 + 闭合 --- 分隔线
      插入后结构：`...<前置内容>\\n<new_s06>\\n\\n---\\n\\n## §1...`

    两种路径产生相同的最终结构，因此多次运行结果一致（幂等）。

    Args:
        content: 蓝图文件原始内容
        new_s06: 新的 §0.6 块内容（以 "### §0.6" 开头，不含闭合 ---，不含尾随 \\n）

    Returns:
        更新后的蓝图文件内容
    """
    # 尝试匹配现有 §0.6 块（regex 不含前导 \n，match 从 "### §0.6" 开始）
    match = _S06_BLOCK_RE.search(content)
    if match:
        # 替换现有 §0.6 块：new_s06 + "\n"（补回 .*? 消耗的尾随 \n）
        # match 从 "### §0.6" 到 "\n---" 之前（含一个尾随 \n）
        # 替换为 new_s06 + "\n"，保持与 insert 路径相同的结构
        replacement = new_s06 + "\n"
        return content[: match.start()] + replacement + content[match.end():]

    # §0.6 不存在，需要在 §1 前插入
    # 定位 §1 标题（## §1），regex 不含前导 \n，start() 指向 "##" 首字符
    s1_match = re.search(r"## §1[^\n]*\n", content)
    if not s1_match:
        # 无 §1 标题，追加到文件末尾（无闭合 ---，因无后续章节需要分隔）
        return content.rstrip() + "\n\n" + new_s06 + "\n"

    # 在 §1 前插入 new_s06 + 闭合 --- 分隔线
    # 插入后：<前置内容>\n<new_s06>\n\n---\n\n## §1...
    insertion = new_s06 + "\n\n---\n\n"
    return content[: s1_match.start()] + insertion + content[s1_match.start():]


def _update_blueprint_file(
    bp: BlueprintFrontmatter, new_s06: str, *, dry_run: bool
) -> bool:
    """更新蓝图文件的 §0.6 章节。

    Returns:
        True 如果文件被更新（或 dry_run 模式下本应更新）
    """
    new_content = _replace_or_insert_s06(bp.content, new_s06)
    if new_content == bp.content:
        # 内容无变化（§0.6 已是最新）
        return False
    if not dry_run:
        bp.file_path.write_text(new_content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def _collect_panorama(module_id: str) -> ModulePanorama:
    """采集单模块的四图全景数据。"""
    depgraph_info = _fetch_depgraph_module(module_id)
    dataflow_info = _fetch_dataflow_module(module_id)
    decision_info = _fetch_decision_module(module_id)
    blueprint_info = _fetch_blueprint(module_id)
    return ModulePanorama(
        module_id=module_id,
        depgraph=depgraph_info,
        dataflow=dataflow_info,
        decision=decision_info,
        blueprint=blueprint_info,
    )


def generate_for_module(module_id: str, *, dry_run: bool = False) -> int:
    """生成单个模块的 §0.6 四图对齐视图并写入蓝图。

    Returns: 0=成功/跳过, 1=DB异常, 3=depgraph无此模块
    """
    try:
        panorama = _collect_panorama(module_id)
    except Exception as exc:
        print(f"[ERROR] 采集 {module_id} 数据失败: {exc}", file=sys.stderr)
        return 1

    # depgraph 无此模块 → 跳过（ERROR_CONTRACT exit 3 语义，但此处返回 3 不退出）
    if panorama.depgraph is None:
        print(
            f"[SKIP] {module_id}: 不在 depgraph 中，跳过 §0.6 生成",
            file=sys.stderr,
        )
        return 3

    # 蓝图不存在 → 跳过
    if panorama.blueprint is None:
        print(
            f"[SKIP] {module_id}: 蓝图文件未找到（frontmatter.module_id 无匹配），跳过",
            file=sys.stderr,
        )
        return 0

    new_s06 = _generate_s06_section(panorama)
    updated = _update_blueprint_file(
        panorama.blueprint, new_s06, dry_run=dry_run
    )

    action = "DRY-RUN" if dry_run else "OK"
    if updated:
        print(
            f"[{action}] {module_id}: §0.6 已{'写入' if not dry_run else '预览'} "
            f"{panorama.blueprint.file_path}"
        )
    else:
        print(f"[OK] {module_id}: §0.6 已是最新，无需更新")
    return 0


def generate_all(*, dry_run: bool = False) -> int:
    """生成所有 depgraph 中有 blueprint_id 的模块的 §0.6。

    Returns: 0=全部成功, 1=有失败
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(_SQL_QUERY_ALL_MODULES)
            rows = cur.fetchall()
        modules = [
            row["blueprint_id"] if isinstance(row, dict) else row[0]
            for row in rows
        ]
    finally:
        conn.close()

    print(f"[INFO] 共 {len(modules)} 个模块待处理")
    succeeded = 0
    skipped_depgraph = 0
    skipped_blueprint = 0
    failed = 0
    for mid in modules:
        rc = generate_for_module(mid, dry_run=dry_run)
        if rc == 0:
            succeeded += 1
        elif rc == 3:
            skipped_depgraph += 1
        else:
            failed += 1
    print(
        f"[INFO] 处理完成：成功={succeeded}, "
        f"跳过(depgraph无)={skipped_depgraph}, "
        f"失败={failed}（共 {len(modules)} 个）"
    )
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="蓝图 §0.6 四图对齐视图生成器（ARCH-053 + ARCH-056 + 模板 v2.1.0）"
    )
    parser.add_argument(
        "module_id",
        nargs="?",
        help="要生成 §0.6 的模块 ID（MOD-XXX）",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="生成所有 depgraph 中有 blueprint_id 的模块",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印预览，不写入文件",
    )
    args = parser.parse_args()

    if args.all:
        return generate_all(dry_run=args.dry_run)
    if args.module_id:
        return generate_for_module(args.module_id, dry_run=args.dry_run)
    parser.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())
