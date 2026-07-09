# [BLUEPRINT] MOD-GOV-ALIGN-PANORAMAS | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §panorama-alignment
# [MODULE] scripts.governance.d5_architecture.generators.align_panoramas
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema; zephyr.governance.persistence.dataflowgraph_schema; zephyr.governance.persistence.decisiongraph_schema; _common (DB_DISPLAY_NAME)
# [CONSUMERS] CI自动触发;人工审查四图对齐报告
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 只读PG（零写入）;只读blueprint.md文件（零写入）;输出幂等(相同输入→相同输出);输出到generated/panorama_alignment_report.md
# [MODIFY-GUARD] 修改需通过ARCH-053任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] depgraph不存在→exit 1;三图任一为空→exit 2(blueprint图不参与此检查)
# [TESTS] tests/test_align_panoramas.py
# [TTL] permanent
# [ARCH-REF] #ARCH-053 #ARCH-056
# 真源说明：本检测器从 depgraph / dataflowgraph / decisiongraph (PostgreSQL) 读取三图节点，
# 并从 docs/03_modules/ 下的 blueprint.md / 模块文件 frontmatter 采集第四张图（blueprint），
# 生成四图对齐报告（孤儿/状态漂移/域不一致/设计态孤立）。
# 详见 AGENTS.md §真源分类（11.0.2）+ ARCH-053 / ARCH-056 裁定。
"""G-panorama-align: 四图对齐检测器（ARCH-053 + ARCH-056 四图升级）

依据：ARCH-053 裁定（2026-07-06）；ARCH-056 四图升级（2026-07-09）

功能：
  - 从 depgraph.nodes / dataflow_datasets+jobs / decision_nodes+layers 读取三图节点（DB 真源）
  - 从 docs/03_modules/ 下的 blueprint.md / 模块文件 frontmatter 采集第四张图节点（blueprint）
  - 用 module_id 作为对齐 key（depgraph 用 blueprint_id 派生，dataflow/decision 用 module_id，
    blueprint 用 frontmatter.module_id）
  - 检测四类问题：
      (1) 孤儿：仅在一图存在的 module_id（其它三图无对应记录）
      (2) 状态漂移：同一 module_id 在不同图 design_maturity 不一致
      (3) 域不一致：同一 module_id 在不同图 domain_id 不一致
      (4) 设计态孤立：design 状态仅出现在一图，其它三图无对应
  - 输出 MD 报告到 docs/02_enterprise_architecture/generated/panorama_alignment_report.md

定位：只读检测器（不做自动修复），由人工或后续工具根据报告处理。

用法
----
    python scripts/governance/d5_architecture/generators/align_panoramas.py
    python scripts/governance/d5_architecture/generators/align_panoramas.py --output custom/path.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.governance.persistence.dataflowgraph_schema import (  # noqa: E402
    get_dataflowgraph_pg_connection,
)
from zephyr.governance.persistence.decisiongraph_schema import (  # noqa: E402
    get_decisiongraph_pg_connection,
)

try:
    from d5_architecture.panorama_common import weighted_domain_vote, min_maturity as _min_mat
except ImportError:
    import sys as _sys
    _pc_path = str(Path(__file__).resolve().parents[1])  # d5_architecture/
    if _pc_path not in _sys.path:
        _sys.path.insert(0, _pc_path)
    from panorama_common import weighted_domain_vote, min_maturity as _min_mat


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


class PanoramaEmptyError(RuntimeError):
    """三图（depgraph/dataflow/decision）任一为空时抛出（ERROR_CONTRACT exit 2）。

    blueprint 图不参与此检查（blueprint 文件可能尚未生成）。
    """


@dataclass
class PanoramaNode:
    """四图任一节点视图（统一字段供对齐检测）。"""

    module_id: str
    graph: str  # "depgraph" | "dataflow" | "decision" | "blueprint"
    entity_name: str
    design_maturity: str | None
    build_status: str | None
    domain_id: str | None


@dataclass
class PanoramaAlignmentReport:
    """四图对齐检测报告。"""

    generated_at: str = ""
    db_name: str = DB_DISPLAY_NAME
    # 四图统计
    depgraph_count: int = 0
    dataflow_count: int = 0
    decision_count: int = 0
    blueprint_count: int = 0
    # 四类问题
    orphans: list[dict] = field(default_factory=list)  # 仅在一图
    state_drifts: list[dict] = field(default_factory=list)  # design_maturity 不一致
    domain_mismatches: list[dict] = field(default_factory=list)  # domain_id 不一致
    design_only_in_one: list[dict] = field(default_factory=list)  # design 仅一图
    # 汇总
    issues_total: int = 0

    def to_markdown(self) -> str:
        """渲染为 Markdown 报告。"""
        lines: list[str] = []
        lines.append("# 四图对齐报告 (Panorama Alignment Report)")
        lines.append("")
        lines.append(f"- 生成时间: {self.generated_at}")
        lines.append(f"- 数据源: {self.db_name}")
        lines.append(f"- 四图节点数: depgraph={self.depgraph_count} / "
                     f"dataflow={self.dataflow_count} / decision={self.decision_count} / "
                     f"blueprint={self.blueprint_count}")
        lines.append(f"- 问题总数: {self.issues_total}")
        lines.append("  - 孤儿（仅一图）: {}".format(len(self.orphans)))
        lines.append("  - 状态漂移（blueprint 缺 design_maturity）: {}".format(len(self.state_drifts)))
        lines.append("  - 域不一致（domain_id 不一致）: {}".format(len(self.domain_mismatches)))
        lines.append("  - 设计态孤立（design 仅一图）: {}".format(len(self.design_only_in_one)))
        lines.append("")

        # 孤儿
        lines.append("## 1. 孤儿节点（仅一图存在）")
        lines.append("")
        if not self.orphans:
            lines.append("> 无孤儿节点，四图在 module_id 维度对齐。")
        else:
            lines.append("| module_id | graph | entity_name |")
            lines.append("|---|---|---|")
            for o in self.orphans[:200]:  # 最多展示 200 行
                lines.append(f"| {o['module_id']} | {o['graph']} | {o['entity_name']} |")
            if len(self.orphans) > 200:
                lines.append(f"... 共 {len(self.orphans)} 行（仅展示前 200 行）")
        lines.append("")

        # 状态漂移
        lines.append("## 2. 状态漂移（blueprint 缺 design_maturity 字段）")
        lines.append("")
        if not self.state_drifts:
            lines.append("> 无状态漂移。")
        else:
            lines.append("| module_id | depgraph | dataflow | decision | blueprint |")
            lines.append("|---|---|---|---|---|")
            for d in self.state_drifts:
                lines.append(f"| {d['module_id']} | {d['depgraph']} | {d['dataflow']} | "
                             f"{d['decision']} | {d['blueprint']} |")
        lines.append("")

        # 域不一致
        lines.append("## 3. 域不一致（domain_id 不一致）")
        lines.append("")
        if not self.domain_mismatches:
            lines.append("> 无域不一致。")
        else:
            lines.append("| module_id | depgraph | dataflow | decision | blueprint |")
            lines.append("|---|---|---|---|---|")
            for d in self.domain_mismatches:
                lines.append(f"| {d['module_id']} | {d['depgraph']} | {d['dataflow']} | "
                             f"{d['decision']} | {d['blueprint']} |")
        lines.append("")

        # 设计态孤立
        lines.append("## 4. 设计态孤立（design 仅一图）")
        lines.append("")
        if not self.design_only_in_one:
            lines.append("> 无设计态孤立。")
        else:
            lines.append("| module_id | graph | entity_name |")
            lines.append("|---|---|---|")
            for d in self.design_only_in_one[:200]:
                lines.append(f"| {d['module_id']} | {d['graph']} | {d['entity_name']} |")
            if len(self.design_only_in_one) > 200:
                lines.append(f"... 共 {len(self.design_only_in_one)} 行（仅展示前 200 行）")
        lines.append("")

        # 处置建议
        lines.append("## 5. 处置建议")
        lines.append("")
        lines.append("- 孤儿节点：决定是否需在另三图登记对应 module_id，或在一图删除")
        lines.append("- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）")
        lines.append("- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）")
        lines.append("- 设计态孤立：评估设计态是否需要同步到另三图")
        lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 数据采集
# ---------------------------------------------------------------------------


def _fetch_depgraph_nodes(conn) -> list[PanoramaNode]:
    """从 depgraph.nodes 读取（blueprint_id 作为 module_id 对齐 key）。

    聚合：depgraph.nodes 中同一 blueprint_id 可有多行（不同文件路径实例），
    每行可能有不同的 domain_id/design_maturity（跨域模块的正常现象）。
    每个 blueprint_id 聚合所有行，避免单行取值不稳定导致对齐误报：
    - domain_id: 多数投票（Counter.most_common），取代表性域
    - design_maturity: 取最 design 的状态（design < prototype < production），
      与 _detect_state_drifts 聚合策略一致
    - build_status: 取第一个非空
    - entity_name: 取第一个非空 path（path 非空优先，ORDER BY 保证）
    """
    grouped: dict[str, list[dict]] = {}
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT blueprint_id, path, design_maturity, build_status, domain_id
            FROM nodes
            WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''
            ORDER BY blueprint_id, (path IS NULL), path
            """
        )
        for row in cur.fetchall():
            if isinstance(row, dict):
                bp = row.get("blueprint_id")
                path = row.get("path")
                dm = row.get("design_maturity")
                bs = row.get("build_status")
                dom = row.get("domain_id")
            else:
                # tuple 兼容
                bp = row[0] if len(row) > 0 else None
                path = row[1] if len(row) > 1 else None
                dm = row[2] if len(row) > 2 else None
                bs = row[3] if len(row) > 3 else None
                dom = row[4] if len(row) > 4 else None
            if not bp:
                continue
            grouped.setdefault(bp, []).append({
                "path": path,
                "design_maturity": dm,
                "build_status": bs,
                "domain_id": dom,
            })

    nodes: list[PanoramaNode] = []
    for bp, rows in grouped.items():
        # domain_id: 加权域投票（测试文件降权，平局字母序）
        domain_id = weighted_domain_vote(rows) or None
        # design_maturity: 取最 design（min rank）
        maturities = [r["design_maturity"] for r in rows if r["design_maturity"]]
        design_maturity = _min_mat(maturities) or None
        # build_status: 取第一个非空
        build_status = next((r["build_status"] for r in rows if r["build_status"]), None)
        # entity_name: 取第一个非空 path
        entity_name = next((r["path"] for r in rows if r["path"]), bp)

        nodes.append(PanoramaNode(
            module_id=bp,
            graph="depgraph",
            entity_name=entity_name,
            design_maturity=design_maturity,
            build_status=build_status,
            domain_id=domain_id,
        ))
    return nodes


def _fetch_dataflow_nodes(conn) -> list[PanoramaNode]:
    """从 dataflow_datasets + dataflow_jobs 读取（module_id 作为对齐 key）。

    ARCH-053 修复（2026-07-09）：对齐 key 从 entity_name/job_name 改为 module_id 字段，
    与 depgraph（blueprint_id）和 decision（module_id）统一。
    module_id 为空的实体跳过（无对应 depgraph 模块，不参与对齐）。
    """
    nodes: list[PanoramaNode] = []
    with conn.cursor() as cur:
        # datasets
        cur.execute(
            """
            SELECT entity_name, module_id, design_maturity, build_status, domain_id
            FROM dataflow_datasets
            WHERE module_id IS NOT NULL AND module_id <> ''
            """
        )
        for row in cur.fetchall():
            if isinstance(row, dict):
                name = row.get("entity_name")
                mid = row.get("module_id")
                dm = row.get("design_maturity")
                bs = row.get("build_status")
                dom = row.get("domain_id")
            else:
                name = row[0] if len(row) > 0 else None
                mid = row[1] if len(row) > 1 else None
                dm = row[2] if len(row) > 2 else None
                bs = row[3] if len(row) > 3 else None
                dom = row[4] if len(row) > 4 else None
            if not mid:
                continue
            nodes.append(PanoramaNode(
                module_id=mid,
                graph="dataflow",
                entity_name=name or mid,
                design_maturity=dm,
                build_status=bs,
                domain_id=dom,
            ))
        # jobs
        cur.execute(
            """
            SELECT job_name, module_id, design_maturity, build_status, NULL AS domain_id
            FROM dataflow_jobs
            WHERE module_id IS NOT NULL AND module_id <> ''
            """
        )
        for row in cur.fetchall():
            if isinstance(row, dict):
                name = row.get("job_name")
                mid = row.get("module_id")
                dm = row.get("design_maturity")
                bs = row.get("build_status")
                dom = row.get("domain_id")
            else:
                name = row[0] if len(row) > 0 else None
                mid = row[1] if len(row) > 1 else None
                dm = row[2] if len(row) > 2 else None
                bs = row[3] if len(row) > 3 else None
                dom = row[4] if len(row) > 4 else None
            if not mid:
                continue
            nodes.append(PanoramaNode(
                module_id=mid,
                graph="dataflow",
                entity_name=name or mid,
                design_maturity=dm,
                build_status=bs,
                domain_id=dom,
            ))
    return nodes


def _fetch_decision_nodes(conn) -> list[PanoramaNode]:
    """从 decision_nodes + decision_layers 读取（module_id 作为对齐 key）。"""
    nodes: list[PanoramaNode] = []
    with conn.cursor() as cur:
        # decision_nodes（module_id 可能为空，过滤掉）
        cur.execute(
            """
            SELECT module_id, path, design_maturity, build_status, NULL AS domain_id
            FROM decision_nodes
            WHERE module_id IS NOT NULL AND module_id <> ''
            """
        )
        for row in cur.fetchall():
            if isinstance(row, dict):
                mid = row.get("module_id")
                path = row.get("path")
                dm = row.get("design_maturity")
                bs = row.get("build_status")
                dom = row.get("domain_id")
            else:
                mid = row[0] if len(row) > 0 else None
                path = row[1] if len(row) > 1 else None
                dm = row[2] if len(row) > 2 else None
                bs = row[3] if len(row) > 3 else None
                dom = row[4] if len(row) > 4 else None
            if not mid:
                continue
            nodes.append(PanoramaNode(
                module_id=mid,
                graph="decision",
                entity_name=path or mid,
                design_maturity=dm,
                build_status=bs,
                domain_id=dom,
            ))
        # decision_layers（module_id 可能为空，过滤掉）
        cur.execute(
            """
            SELECT module_id, layer_id, design_maturity, build_status, NULL AS domain_id
            FROM decision_layers
            WHERE module_id IS NOT NULL AND module_id <> ''
            """
        )
        for row in cur.fetchall():
            if isinstance(row, dict):
                mid = row.get("module_id")
                layer_id = row.get("layer_id")
                dm = row.get("design_maturity")
                bs = row.get("build_status")
                dom = row.get("domain_id")
            else:
                mid = row[0] if len(row) > 0 else None
                layer_id = row[1] if len(row) > 1 else None
                dm = row[2] if len(row) > 2 else None
                bs = row[3] if len(row) > 3 else None
                dom = row[4] if len(row) > 4 else None
            if not mid:
                continue
            nodes.append(PanoramaNode(
                module_id=mid,
                graph="decision",
                entity_name=f"layer:{layer_id}" if layer_id else mid,
                design_maturity=dm,
                build_status=bs,
                domain_id=dom,
            ))
    return nodes


# blueprint frontmatter 解析（与 blueprint_frontmatter_reconciler.py 一致风格）
_BP_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# blueprint 文件扫描根目录
_BP_SCAN_ROOT = _REPO_ROOT / "docs" / "03_modules"

# 跳过的文件名（非模块蓝图文件）
_BP_SKIP_NAMES = {"index.md"}

# exempt_list 配置文件（历史归档豁免，Task 8 创建）
_EXEMPT_LIST_PATH = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    / "panorama_exempt_list.yaml"
)


def _load_exempt_list() -> set[str]:
    """加载 exempt_list 配置（历史归档豁免）。文件不存在时返回空集合。"""
    if not _EXEMPT_LIST_PATH.exists():
        return set()
    try:
        import yaml
        data = yaml.safe_load(_EXEMPT_LIST_PATH.read_text(encoding="utf-8"))
        ids = data.get("exempt_module_ids", []) if data else []
        return {str(i) for i in ids if i}
    except Exception:
        return set()


def _parse_simple_frontmatter(content: str) -> dict[str, str]:
    """解析 YAML frontmatter 为扁平 dict（简单实现，跳过嵌套字段）。

    跳过以 [ 或 { 开头的值（列表/字典），只提取标量字段。
    """
    match = _BP_FRONTMATTER_RE.match(content)
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


def _fetch_blueprint_nodes(scan_root: Path | None = None) -> list[PanoramaNode]:
    """从 docs/03_modules/ 下的蓝图文件 frontmatter 采集节点（ARCH-056 第四张图）。

    扫描策略：递归遍历 scan_root，对每个文件尝试解析 YAML frontmatter，
    提取 module_id 字段（缺失则跳过）。

    兼容两种布局：
      1. docs/03_modules/<MODULE_ID>.md（由 blueprint_frontmatter_reconciler 自动创建）
      2. docs/03_modules/<path>/blueprint.md（人工维护的蓝图）

    字段映射：
      module_id        ← frontmatter.module_id
      responsibility_domain → domain_id
      design_maturity  ← frontmatter.design_maturity
      build_status     ← frontmatter.build_status
      entity_name      ← 文件相对路径
    """
    root = scan_root if scan_root is not None else _BP_SCAN_ROOT
    nodes: list[PanoramaNode] = []
    if not root.exists():
        return nodes

    for fpath in root.rglob("*"):
        if not fpath.is_file() or fpath.name in _BP_SKIP_NAMES:
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = _parse_simple_frontmatter(content)
        mid = fm.get("module_id")
        if not mid:
            continue  # 无 module_id 不参与对齐
        try:
            rel = str(fpath.relative_to(root)).replace("\\", "/")
        except ValueError:
            rel = str(fpath)
        nodes.append(PanoramaNode(
            module_id=mid,
            graph="blueprint",
            entity_name=rel,
            design_maturity=fm.get("design_maturity") or None,
            build_status=fm.get("build_status") or None,
            domain_id=fm.get("responsibility_domain") or None,
        ))
    return nodes


# ---------------------------------------------------------------------------
# 对齐检测
# ---------------------------------------------------------------------------


def _group_by_module_id(all_nodes: list[PanoramaNode]) -> dict[str, list[PanoramaNode]]:
    """按 module_id 分组。"""
    grouped: dict[str, list[PanoramaNode]] = defaultdict(list)
    for n in all_nodes:
        grouped[n.module_id].append(n)
    return grouped


def _detect_orphans(all_nodes: list[PanoramaNode],
                    exempt_list: set[str] | None = None) -> list[dict]:
    """孤儿：仅在一图存在的 module_id。

    exempt_list 中的 module_id 跳过检测（历史归档豁免）。
    """
    exempt = exempt_list or set()
    grouped = _group_by_module_id(all_nodes)
    orphans: list[dict] = []
    for mid, nodes in grouped.items():
        if mid in exempt:
            continue
        graphs = {n.graph for n in nodes}
        if len(graphs) == 1:
            g = next(iter(graphs))
            for n in nodes:
                orphans.append({
                    "module_id": mid,
                    "graph": g,
                    "entity_name": n.entity_name,
                })
    # 按图分组后按 module_id 排序
    orphans.sort(key=lambda x: (x["graph"], x["module_id"]))
    return orphans


def _detect_state_drifts(all_nodes: list[PanoramaNode]) -> list[dict]:
    """状态漂移：blueprint 缺 design_maturity 字段（ARCH-056 修正后新语义）。

    四图 design_maturity 维度差异不再报告（各图评估维度不同是正常的）。
    仅检测 blueprint 图中 design_maturity 字段缺失的情况。
    """
    grouped = _group_by_module_id(all_nodes)
    drifts: list[dict] = []
    for mid, nodes in grouped.items():
        graphs = {n.graph for n in nodes}
        if "blueprint" not in graphs:
            continue  # 无 blueprint 节点，不检测
        bp_nodes = [n for n in nodes if n.graph == "blueprint"]
        for n in bp_nodes:
            if not n.design_maturity:
                drifts.append({
                    "module_id": mid,
                    "depgraph": next((x.design_maturity or "-" for x in nodes if x.graph == "depgraph"), "-"),
                    "dataflow": next((x.design_maturity or "-" for x in nodes if x.graph == "dataflow"), "-"),
                    "decision": next((x.design_maturity or "-" for x in nodes if x.graph == "decision"), "-"),
                    "blueprint": "-",
                    "issue": "missing_design_maturity",
                })
                break  # 一个 blueprint 节点缺字段就够了
    drifts.sort(key=lambda x: x["module_id"])
    return drifts


def _detect_domain_mismatches(all_nodes: list[PanoramaNode]) -> list[dict]:
    """域不一致：dataflow/decision 与 blueprint 域不一致（ARCH-056 修正后新语义）。

    depgraph 与 blueprint 域不一致不报告（depgraph 是路径投票值，blueprint 是逻辑真源）。
    仅检测 dataflow/decision 与 blueprint 不一致的情况。
    """
    grouped = _group_by_module_id(all_nodes)
    mismatches: list[dict] = []
    for mid, nodes in grouped.items():
        graphs = {n.graph for n in nodes}
        if "blueprint" not in graphs:
            continue  # 无 blueprint 节点，无法比较
        bp_domain = next((n.domain_id for n in nodes if n.graph == "blueprint" and n.domain_id), None)
        if not bp_domain:
            continue  # blueprint 无 domain_id，无法比较
        per_graph: dict[str, str] = {}
        for n in nodes:
            if n.graph in ("dataflow", "decision") and n.domain_id:
                per_graph[n.graph] = n.domain_id
        mismatched = {g: d for g, d in per_graph.items() if d != bp_domain}
        if mismatched:
            mismatches.append({
                "module_id": mid,
                "depgraph": "-",
                "dataflow": mismatched.get("dataflow", "-"),
                "decision": mismatched.get("decision", "-"),
                "blueprint": bp_domain,
            })
    mismatches.sort(key=lambda x: x["module_id"])
    return mismatches


def _detect_design_only_in_one(all_nodes: list[PanoramaNode]) -> list[dict]:
    """设计态孤立：design 状态仅出现在一图，其它三图无对应。"""
    grouped = _group_by_module_id(all_nodes)
    design_only: list[dict] = []
    for mid, nodes in grouped.items():
        graphs = {n.graph for n in nodes}
        if len(graphs) != 1:
            continue  # 多图存在就不算孤立
        # 检查是否有 design 状态节点
        has_design = any(n.design_maturity == "design" for n in nodes)
        if not has_design:
            continue
        g = next(iter(graphs))
        for n in nodes:
            if n.design_maturity == "design":
                design_only.append({
                    "module_id": mid,
                    "graph": g,
                    "entity_name": n.entity_name,
                })
    design_only.sort(key=lambda x: (x["graph"], x["module_id"]))
    return design_only


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run_alignment(
    output_path: Path | None = None,
    *,
    write_report: bool = True,
) -> PanoramaAlignmentReport:
    """运行四图对齐检测，生成报告。

    Args:
        output_path: 报告输出路径。None 时使用默认路径
            docs/02_enterprise_architecture/generated/panorama_alignment_report.md
        write_report: True 写入文件（默认）；False 仅返回 report 不写文件
            （门禁场景使用，避免污染 docs/）
    """
    if output_path is None:
        output_path = (
            _REPO_ROOT
            / "docs"
            / "02_enterprise_architecture"
            / "generated"
            / "panorama_alignment_report.md"
        )

    # 采集三图节点（DB 真源）
    depgraph_conn = get_depgraph_pg_connection()
    try:
        depgraph_nodes = _fetch_depgraph_nodes(depgraph_conn)
    finally:
        depgraph_conn.close()

    dataflow_conn = get_dataflowgraph_pg_connection()
    try:
        dataflow_nodes = _fetch_dataflow_nodes(dataflow_conn)
    finally:
        dataflow_conn.close()

    decision_conn = get_decisiongraph_pg_connection()
    try:
        decision_nodes = _fetch_decision_nodes(decision_conn)
    finally:
        decision_conn.close()

    # 采集第四张图（blueprint，文件系统真源，ARCH-056）
    blueprint_nodes = _fetch_blueprint_nodes()

    all_nodes = depgraph_nodes + dataflow_nodes + decision_nodes + blueprint_nodes

    # ERROR_CONTRACT: 三图（depgraph/dataflow/decision）任一为空 → exit 2（检测无意义）
    # blueprint 图不参与此检查（blueprint 文件可能尚未生成，属合法状态）
    empty_graphs = []
    if not depgraph_nodes:
        empty_graphs.append("depgraph")
    if not dataflow_nodes:
        empty_graphs.append("dataflow")
    if not decision_nodes:
        empty_graphs.append("decision")
    if empty_graphs:
        raise PanoramaEmptyError(
            f"三图（depgraph/dataflow/decision）任一为空（exit 2）: "
            f"{','.join(empty_graphs)} 无节点；检测无意义"
        )

    # 检测四类问题
    exempt = _load_exempt_list()
    orphans = _detect_orphans(all_nodes, exempt_list=exempt)
    state_drifts = _detect_state_drifts(all_nodes)
    domain_mismatches = _detect_domain_mismatches(all_nodes)
    design_only_in_one = _detect_design_only_in_one(all_nodes)

    report = PanoramaAlignmentReport(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        depgraph_count=len(depgraph_nodes),
        dataflow_count=len(dataflow_nodes),
        decision_count=len(decision_nodes),
        blueprint_count=len(blueprint_nodes),
        orphans=orphans,
        state_drifts=state_drifts,
        domain_mismatches=domain_mismatches,
        design_only_in_one=design_only_in_one,
        issues_total=len(orphans) + len(state_drifts) + len(domain_mismatches) + len(design_only_in_one),
    )

    # 写入文件（门禁场景 write_report=False 跳过）
    if write_report:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report.to_markdown(), encoding="utf-8")
        print(f"OK: 四图对齐报告已写入 {output_path}")
        print(f"    问题总数: {report.issues_total} "
              f"(孤儿={len(orphans)}, 状态漂移={len(state_drifts)}, "
              f"域不一致={len(domain_mismatches)}, 设计态孤立={len(design_only_in_one)})")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="四图对齐检测器（ARCH-053 + ARCH-056）"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="报告输出路径（默认 docs/02_enterprise_architecture/generated/panorama_alignment_report.md）",
    )
    args = parser.parse_args()

    try:
        run_alignment(output_path=args.output)
    except PanoramaEmptyError as e:
        # ERROR_CONTRACT: 三图（depgraph/dataflow/decision）任一为空 → exit 2
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
