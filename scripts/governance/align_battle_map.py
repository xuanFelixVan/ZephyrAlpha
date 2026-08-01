# [BLUEPRINT] MOD-GOV_ALIGN_BATTLE_MAP | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/battle_map_panorama.md | §8.3
# [MODULE] scripts.governance.align_battle_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.battle_map_reader (BattleMapReader); zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.governance.persistence.dataflowgraph_schema (get_dataflowgraph_pg_connection); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection); scripts.governance._shared.module_translation_loader (all_battle_map_step_ids, preload_battle_map_steps); scripts.governance._shared.constants (EXIT_*)
# [CONSUMERS] CI自动触发;人工审查作战地图对齐报告
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读PG（零写入）;只读YAML/文件系统（零写入）;输出幂等(相同输入→相同输出);输出到generated/battle_map_alignment_report.md
# [MODIFY-GUARD] 修改需通过 battle_map_panorama.md §8.3 任务或后续维护任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] battle_map 表不存在→exit 2;findings→exit 1(EXIT_FINDINGS);无 findings→exit 0(EXIT_PASS)
# [TESTS] tests/test_align_battle_map.py (规划中)
# [TTL] permanent
# [ARCH-REF] battle_map_panorama.md §七 §八
# 真源说明：本检测器从 battle_map_* 三表（PostgreSQL）读取环节/锚点/流转边，
# 从翻译真源 module_translation_registry.yaml §battle_map_steps 段读取环节叙事，
# 从 depgraph/dataflowgraph/decisiongraph/candidate/blueprint 读取锚点目标合法 id，
# 生成作战地图对齐报告（孤儿环节/幽灵锚点/缺失叙事/悬空边）。
# 详见 battle_map_panorama.md §8.3 + §7.4（BM-INV-001~003）。
"""G-battle-map-align: 作战地图对齐检测器（battle_map_panorama.md §8.3）

依据：battle_map_panorama.md V0.2.0 §八（与全景图对齐体系的关系）+ §七（双向查找机制）

功能：
  - 从 battle_map_steps / battle_map_anchors / battle_map_edges 读取作战地图三表（DB 真源）
  - 从翻译真源 module_translation_registry.yaml §battle_map_steps 段读取环节叙事
  - 从 depgraph/dataflowgraph/decisiongraph/candidate/blueprint 读取锚点目标合法 id
  - 检测四类问题：
      (1) 孤儿环节（BM-INV-001）：环节无任何锚点 = 悬空决策 = 幻觉风险
      (2) 幽灵锚点（BM-INV-002）：anchor.target_id 在 target_graph 对应图/仓库找不到
      (3) 缺失叙事（BM-INV-003）：DB 环节在翻译真源 battle_map_steps 段无对应叙事
      (4) 悬空边：edge.from_step_id / to_step_id 指向不存在的环节
  - 输出 MD 报告到 docs/02_enterprise_architecture/generated/battle_map_alignment_report.md

定位：只读检测器（君子协定告警，不做自动修复，不硬阻断 commit），由人工或后续工具根据报告处理。
与 align_panoramas.py 正交：align_panoramas 管 module_id 轴（四图模块一致性），
本工具管 step_id 轴（作战环节落地性）。互不干扰。

用法
----
    python scripts/governance/align_battle_map.py
    python scripts/governance/align_battle_map.py --output custom/path.md
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 添加项目根到 sys.path
# 本文件在 scripts/governance/，repo root = 含 scripts/ 和 src/ 的目录（marker 法保健壮）
_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = next(p for p in _THIS_FILE.parents if (p / "scripts").is_dir() and (p / "src").is_dir())
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# _shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR  # noqa: E402
from _shared.module_translation_loader import (  # noqa: E402
    all_battle_map_step_ids,
    preload_battle_map_steps,
)
from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402

try:
    from _common import DB_DISPLAY_NAME  # noqa: E402
except ImportError:
    DB_DISPLAY_NAME = "PostgreSQL depgraph"

# 候选池 YAML 真源（target_graph=candidate 的合法 id 来源）
_CANDIDATE_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry"
    / "catalogs" / "candidate_module_registry.yaml"
)

# blueprint 扫描根（target_graph=blueprint 的合法 id 来源）
_BP_SCAN_ROOT = _REPO_ROOT / "docs" / "03_modules"

# 默认报告输出路径
_DEFAULT_REPORT = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "generated"
    / "battle_map_alignment_report.md"
)


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass
class BattleMapAlignmentReport:
    """作战地图对齐检测报告。"""

    generated_at: str = ""
    db_name: str = DB_DISPLAY_NAME
    # 三表统计
    step_count: int = 0
    anchor_count: int = 0
    edge_count: int = 0
    narrative_count: int = 0  # 翻译真源已登记环节叙事数
    # 四类问题
    orphan_steps: list[dict] = field(default_factory=list)  # BM-INV-001 孤儿环节
    ghost_anchors: list[dict] = field(default_factory=list)  # BM-INV-002 幽灵锚点
    missing_narratives: list[dict] = field(default_factory=list)  # BM-INV-003 缺失叙事
    dangling_edges: list[dict] = field(default_factory=list)  # 悬空边
    # 降级告警（目标图源不可用时记录，非对齐问题）
    source_unavailable: list[str] = field(default_factory=list)
    # 汇总
    issues_total: int = 0

    def to_markdown(self) -> str:
        """渲染为 Markdown 报告。"""
        lines: list[str] = []
        lines.append("# 作战地图对齐报告 (Battle Map Alignment Report)")
        lines.append("")
        lines.append(f"- 生成时间: {self.generated_at}")
        lines.append(f"- 数据源: {self.db_name}")
        lines.append(f"- 三表统计: steps={self.step_count} / "
                     f"anchors={self.anchor_count} / edges={self.edge_count} / "
                     f"叙事真源={self.narrative_count}")
        lines.append(f"- 问题总数: {self.issues_total}")
        lines.append("  - 孤儿环节（BM-INV-001，无锚点=悬空决策）: {}".format(len(self.orphan_steps)))
        lines.append("  - 幽灵锚点（BM-INV-002，target_id 找不到）: {}".format(len(self.ghost_anchors)))
        lines.append("  - 缺失叙事（BM-INV-003，翻译真源无环节）: {}".format(len(self.missing_narratives)))
        lines.append("  - 悬空边（edge 指向不存在环节）: {}".format(len(self.dangling_edges)))
        if self.source_unavailable:
            lines.append("")
            lines.append("> ⚠ 目标图源不可用（已跳过该图 BM-INV-002 校验）: "
                         + ", ".join(self.source_unavailable))
        lines.append("")

        # 1. 孤儿环节
        lines.append("## 1. 孤儿环节（BM-INV-001：环节无锚点 = 悬空决策）")
        lines.append("")
        lines.append("> 君子协定：每个 battle_map_steps 必须至少有一个 battle_map_anchors。"
                     "无锚点环节 = 没有模块承载 = AI 写决策时凭记忆推断 = 幻觉风险。")
        lines.append("")
        if not self.orphan_steps:
            lines.append("> ✅ 无孤儿环节，所有环节均已挂载锚点。")
        else:
            lines.append("| step_id | 环节名 | 阶段 | 设计成熟度 |")
            lines.append("|---|---|---|---|")
            for s in self.orphan_steps:
                lines.append(
                    f"| {s['step_id']} | {s.get('step_name', '—')} | "
                    f"{s.get('flow_stage', '—')} | {s.get('design_maturity', '—')} |"
                )
        lines.append("")

        # 2. 幽灵锚点
        lines.append("## 2. 幽灵锚点（BM-INV-002：target_id 在目标图找不到）")
        lines.append("")
        lines.append("> 君子协定：anchor.target_id 必须能在 target_graph 对应的图/仓库里找到。"
                     "找不到 = 幽灵锚点 = 指向不存在的模块/候选/蓝图。")
        lines.append("")
        if not self.ghost_anchors:
            lines.append("> ✅ 无幽灵锚点（或锚点表为空，无对象校验）。")
        else:
            lines.append("| anchor_id | step_id | target_graph | target_id | 角色 |")
            lines.append("|---|---|---|---|---|")
            for a in self.ghost_anchors:
                lines.append(
                    f"| {a.get('anchor_id', '—')} | {a.get('step_id', '—')} | "
                    f"{a.get('target_graph', '—')} | {a.get('target_id', '—')} | "
                    f"{a.get('target_role', '—')} |"
                )
        lines.append("")

        # 3. 缺失叙事
        lines.append("## 3. 缺失叙事（BM-INV-003：翻译真源无对应环节）")
        lines.append("")
        lines.append("> 君子协定：DB 每个环节必须在翻译真源 `battle_map_steps` 段有叙事"
                     "（name_zh/plain_zh/mechanism_zh/indicators_zh）。缺失 = 生成器降级到 DB step_name。")
        lines.append("")
        if not self.missing_narratives:
            lines.append("> ✅ 无缺失叙事，所有环节在翻译真源均已登记。")
        else:
            lines.append("| step_id | 环节名 | 阶段 |")
            lines.append("|---|---|---|")
            for s in self.missing_narratives:
                lines.append(
                    f"| {s['step_id']} | {s.get('step_name', '—')} | "
                    f"{s.get('flow_stage', '—')} |"
                )
        lines.append("")

        # 4. 悬空边
        lines.append("## 4. 悬空边（edge 指向不存在的环节）")
        lines.append("")
        if not self.dangling_edges:
            lines.append("> ✅ 无悬空边，所有流转边两端均为合法环节。")
        else:
            lines.append("| edge_id | from_step_id | to_step_id | edge_type | 缺失端 |")
            lines.append("|---|---|---|---|---|")
            for e in self.dangling_edges:
                lines.append(
                    f"| {e.get('edge_id', '—')} | {e.get('from_step_id', '—')} | "
                    f"{e.get('to_step_id', '—')} | {e.get('edge_type', '—')} | "
                    f"{e.get('missing_end', '—')} |"
                )
        lines.append("")

        # 处置建议
        lines.append("## 5. 处置建议")
        lines.append("")
        lines.append("- 孤儿环节：用 `apply_battle_map.py --add-anchor` 为环节挂载承载模块/候选/蓝图"
                     "（草图 §12 迁移第二批「锚点」）")
        lines.append("- 幽灵锚点：修正 target_id 指向真实存在的模块/候选，或删除该锚点")
        lines.append("- 缺失叙事：在 `module_translation_registry.yaml` §battle_map_steps 段补齐环节叙事"
                     "（name_zh/plain_zh/mechanism_zh/indicators_zh）")
        lines.append("- 悬空边：修正 edge 的 from/to step_id，或删除孤立边")
        lines.append("")
        lines.append("> 域漂移检查（环节 flow_stage vs 锚点目标模块 domain）待后续补 flow_stage→domain "
                     "映射表后实现（battle_map_panorama.md §8.3 第三项）。")
        lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 锚点目标合法 id 采集（BM-INV-002）
# ---------------------------------------------------------------------------


def _valid_ids_depgraph() -> tuple[set[str], bool]:
    """采集 depgraph 合法 target_id（blueprint_id ∪ path，宽松匹配防误报）。

    Returns:
        (valid_ids, available) — available=False 表示源不可用（跳过校验）
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
        valid: set[str] = set()
        conn = get_depgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT blueprint_id, path FROM nodes "
                    "WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''"
                )
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row))
                    bp = r.get("blueprint_id")
                    path = r.get("path")
                    if bp:
                        valid.add(str(bp))
                    if path:
                        valid.add(str(path))
        finally:
            conn.close()
        return valid, True
    except Exception:
        return set(), False


def _valid_ids_dataflowgraph() -> tuple[set[str], bool]:
    """采集 dataflowgraph 合法 target_id（entity_name ∪ job_name ∪ module_id）。"""
    try:
        from zephyr.governance.persistence.dataflowgraph_schema import (
            get_dataflowgraph_pg_connection,
        )
        valid: set[str] = set()
        conn = get_dataflowgraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT entity_name, module_id FROM dataflow_datasets")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row))
                    for k in ("entity_name", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
                cur.execute("SELECT job_name, module_id FROM dataflow_jobs")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row))
                    for k in ("job_name", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
        finally:
            conn.close()
        return valid, True
    except Exception:
        return set(), False


def _valid_ids_decisiongraph() -> tuple[set[str], bool]:
    """采集 decisiongraph 合法 target_id（path ∪ module_id ∪ layer_id）。"""
    try:
        from zephyr.governance.persistence.decisiongraph_schema import (
            get_decisiongraph_pg_connection,
        )
        valid: set[str] = set()
        conn = get_decisiongraph_pg_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT path, module_id FROM decision_nodes")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row))
                    for k in ("path", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
                cur.execute("SELECT layer_id, module_id FROM decision_layers")
                cols = [d[0] for d in cur.description]
                for row in cur.fetchall():
                    r = dict(zip(cols, row))
                    for k in ("layer_id", "module_id"):
                        v = r.get(k)
                        if v:
                            valid.add(str(v))
        finally:
            conn.close()
        return valid, True
    except Exception:
        return set(), False


def _valid_ids_candidate() -> tuple[set[str], bool]:
    """采集候选池合法 target_id（candidate_module_registry.yaml 条目 id）。"""
    try:
        import yaml  # type: ignore[import-untyped]
        if not _CANDIDATE_YAML.exists():
            return set(), False
        data = yaml.safe_load(_CANDIDATE_YAML.read_text(encoding="utf-8")) or {}
        valid: set[str] = set()
        # 兼容多种 schema：顶层 list / entries / candidates / modules
        entries: list = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            for key in ("entries", "candidates", "modules", "items"):
                v = data.get(key)
                if isinstance(v, list):
                    entries = v
                    break
        for e in entries:
            if not isinstance(e, dict):
                continue
            for k in ("id", "candidate_id", "module_id"):
                v = e.get(k)
                if v:
                    valid.add(str(v))
        return valid, True
    except Exception:
        return set(), False


def _valid_ids_blueprint() -> tuple[set[str], bool]:
    """采集蓝图合法 target_id（docs/03_modules/ frontmatter module_id）。"""
    try:
        import re
        if not _BP_SCAN_ROOT.exists():
            return set(), False
        fm_re = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
        valid: set[str] = set()
        for fpath in _BP_SCAN_ROOT.rglob("*"):
            if not fpath.is_file() or fpath.name in {"index.md"}:
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            m = fm_re.match(content)
            if not m:
                continue
            for line in m.group(1).split("\n"):
                if ":" not in line:
                    continue
                key, _, val = line.partition(":")
                if key.strip() in ("module_id", "id"):
                    v = val.strip().strip('"').strip("'")
                    if v and not v.startswith("[") and not v.startswith("{"):
                        valid.add(v)
        return valid, True
    except Exception:
        return set(), False


# target_graph → 采集器
_GRAPH_COLLECTORS = {
    "depgraph": _valid_ids_depgraph,
    "dataflowgraph": _valid_ids_dataflowgraph,
    "decisiongraph": _valid_ids_decisiongraph,
    "candidate": _valid_ids_candidate,
    "blueprint": _valid_ids_blueprint,
}


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def run_alignment(
    output_path: Path | None = None,
    *,
    write_report: bool = True,
) -> BattleMapAlignmentReport:
    """运行作战地图对齐检测，生成报告。

    Args:
        output_path: 报告输出路径。None 时使用默认路径
            docs/02_enterprise_architecture/generated/battle_map_alignment_report.md
        write_report: True 写入文件（默认）；False 仅返回 report 不写文件
    """
    if output_path is None:
        output_path = _DEFAULT_REPORT

    # 预加载翻译真源
    preload_battle_map_steps()

    reader = BattleMapReader()
    try:
        steps = reader.get_all_steps()
        anchors = reader.get_all_anchors()
        edges = reader.get_all_edges()
        orphan_steps = reader.find_steps_without_anchors()
    finally:
        reader.close()

    # BM-INV-002 幽灵锚点：按 target_graph 分组校验
    ghost_anchors: list[dict] = []
    source_unavailable: list[str] = []
    graphs_present = {a["target_graph"] for a in anchors if a.get("target_graph")}
    reader2 = BattleMapReader()
    try:
        for graph in sorted(graphs_present):
            collector = _GRAPH_COLLECTORS.get(graph)
            if collector is None:
                # 未知 target_graph：所有该图锚点都是幽灵（target_graph 本身非法）
                ghost_anchors.extend(
                    {**a, "reason": f"unknown_target_graph:{graph}"}
                    for a in reader2.get_all_anchors()
                    if a.get("target_graph") == graph
                )
                continue
            valid_ids, available = collector()
            if not available:
                source_unavailable.append(graph)
                continue
            orphans = reader2.find_orphan_anchors_by_graph(graph, valid_ids)
            ghost_anchors.extend({**a, "reason": "target_id_not_found"} for a in orphans)
    finally:
        reader2.close()

    # BM-INV-003 缺失叙事：DB step_id 不在翻译真源
    narrative_ids = set(all_battle_map_step_ids())
    missing_narratives = [s for s in steps if s["step_id"] not in narrative_ids]

    # 悬空边：from/to 指向不存在的环节
    step_ids = {s["step_id"] for s in steps}
    dangling_edges: list[dict] = []
    for e in edges:
        miss = []
        if e.get("from_step_id") not in step_ids:
            miss.append("from")
        if e.get("to_step_id") not in step_ids:
            miss.append("to")
        if miss:
            dangling_edges.append({**e, "missing_end": "/".join(miss)})

    report = BattleMapAlignmentReport(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        step_count=len(steps),
        anchor_count=len(anchors),
        edge_count=len(edges),
        narrative_count=len(narrative_ids),
        orphan_steps=orphan_steps,
        ghost_anchors=ghost_anchors,
        missing_narratives=missing_narratives,
        dangling_edges=dangling_edges,
        source_unavailable=source_unavailable,
        issues_total=(
            len(orphan_steps) + len(ghost_anchors)
            + len(missing_narratives) + len(dangling_edges)
        ),
    )

    if write_report:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report.to_markdown(), encoding="utf-8")
        print(f"OK: 作战地图对齐报告已写入 {output_path}")
        print(f"    问题总数: {report.issues_total} "
              f"(孤儿环节={len(orphan_steps)}, 幽灵锚点={len(ghost_anchors)}, "
              f"缺失叙事={len(missing_narratives)}, 悬空边={len(dangling_edges)})")
        if source_unavailable:
            print(f"    ⚠ 目标图源不可用（跳过校验）: {', '.join(source_unavailable)}")

    return report


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="作战地图对齐检测器（battle_map_panorama.md §8.3，君子协定）"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="报告输出路径（默认 docs/02_enterprise_architecture/generated/battle_map_alignment_report.md）",
    )
    args = parser.parse_args()

    try:
        report = run_alignment(output_path=args.output)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR
    # 君子协定：有 findings 返回 EXIT_FINDINGS（调用方决定是否阻断），无 findings 返回 EXIT_PASS
    return EXIT_FINDINGS if report.issues_total > 0 else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
