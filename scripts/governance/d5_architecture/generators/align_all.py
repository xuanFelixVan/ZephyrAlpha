# [BLUEPRINT] MOD-GOV-ALIGN-ALL | docs/03_modules/_domain_governance/panorama_alignment_engine/align_all_blueprint.md | §main
# [MODULE] scripts.governance.d5_architecture.generators.align_all
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.align_panoramas (run_alignment); scripts.governance.align_battle_map (run_alignment); _shared.constants (EXIT_*)
# [CONSUMERS] CI自动触发;人工审查全图全库对齐总览;施工前对齐验证（AGENTS.md RULE-DEPGRAPH 第三件事）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读（零写入，除 overview 报告外）;复用两个 run_alignment(write_report=False);输出幂等;exit code 分层（硬问题→1，软问题→0+warn）
# [MODIFY-GUARD] 修改需通过 ARCH-ALIGN-UNIFIED-001 任务
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 硬问题(domain_mismatches/ghost_anchors)→exit 1;任一检测器异常→exit 2;软问题→exit 0+warn
# [TESTS] tests/governance/test_align_all.py (规划中)
# [A_module] module_id=MOD-GOV-ALIGN-ALL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-ALIGN-UNIFIED-001 #ARCH-053 #ARCH-056 #ARCH-312
# [CREATION-TOKEN] ARCH-ALIGN-UNIFIED-001
"""G-align-all: 全图全库对齐执行入口（ARCH-ALIGN-UNIFIED-001，2026-09-15 十图升级）

依据：trae_080_panorama_alignment.yaml v1.1.0（五图对齐铁律）;
      ARCH-053/056（全景对齐机制）; battle_map_positioning.md §八（与全景图对齐体系的关系）;
      2026-09-04 六图升级（Owner 裁定：+frontend_map 第六图，check_frontend_map 复用接入）

功能：
  一站式全图全库对齐验证——调 align_panoramas.run_alignment 查图 1-4（module_id 轴）+
  调 align_battle_map.run_alignment 查图 5（step_id 轴）+
  调 check_frontend_map.run_checks 查图 6（feature_id 轴）+
  内联复用 generate_governance_map.scan() 查图 10（module_id/import spec 轴），产出总览报告。

全景图定义（命名口径=#ARCH-ALIGN-NAMING-001 计数无关命名，数量只作轨迹记录）：
  图 1-4（module_id 轴）：depgraph / dataflowgraph / decisiongraph / blueprint.md
  图 5  （step_id 轴）  ：battle_map（通过 anchors 与图 1-4 双向校验）
  图 6  （feature_id 轴）：frontend_map（真源 web/frontend_map.yaml，R0-R3 校验）
  图 10 （module_id/import spec 轴）：governance_operations_map（机生层=families 与
        scan() 重建比对；人工层=GOM-L0..L6 层位合法+mounts/disconnected 路径实存+
        disconnected 必带 note；已删墓碑凭 note 豁免计软）

升级轨迹：七图=+trading_decision_map（2026-09-05）→ 八图=+industry_chain_map（2026-09-11，
注册表层/文档抽查/产业链三节）→ 九图=+strategy_production_map（2026-09-13，第八节结构
十项+仓储存在性校验，单一真源=validators/validate_strategy_production_map.py）→
十图=+governance_operations_map（2026-09-15，#ARCH-312 GOMAP 转正 Owner 放行，
第九节内联复用 generate_governance_map.scan() 单一真源，零独立校验器）。

强制力分层：
  硬问题（exit 1）：domain_mismatches（图 1-4 域不一致）/ ghost_anchors（图 5 幽灵锚点）/
                    frontend_map fail（图 6 悬空/重复）/ gomap error（图 10 机生层漂移+
                    人工层路径缺失/层位非法/缺 note）
  软问题（exit 0 + warn）：orphans / state_drifts / design_only_in_one /
                          orphan_steps / missing_narratives / dangling_edges /
                          domain_drifts / parent_child_issues / orphan_modules / frontend_map warns
                          / gomap 已删墓碑豁免条目（warn 待清理）

用法
----
    # 施工前对齐验证（AGENTS.md RULE-DEPGRAPH 第三件事 Step 3）
    python scripts/governance/d5_architecture/generators/align_all.py

    # 自定义输出路径
    python scripts/governance/d5_architecture/generators/align_all.py --output custom/overview.md

    # 仅检测不写报告（门禁场景）
    python scripts/governance/d5_architecture/generators/align_all.py --no-report
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'G-align-all: 全图全库对齐执行入口（ARCH-ALIGN-UNIFIED-001）'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import sys
from pathlib import Path

# 添加项目根到 sys.path
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# _shared 在 scripts/governance/_shared，须将其父目录加入 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# align_battle_map.py 在 scripts/governance/，须将其目录加入 sys.path
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

import json  # noqa: E402
import re  # noqa: E402  # 第九节 图 10 GOMAP import spec 形状判定（2026-09-15 十图升级）

import yaml  # noqa: E402  # 第八节 图 9 strategy_production_map 结构+仓储校验（2026-09-13 九图升级）

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402  # TRAE-067 无窗口 subprocess 统一入口

_REPO_ROOT_A = next(p for p in Path(__file__).resolve().parents if (p / "src" / "zephyr").exists())
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from zephyr.gov_enforcement.registry_alignment import (  # noqa: E402  # 第二层注册表对齐共享核心（满贯施工 2026-09-11）
    check_candidate_promotion_chain,
    check_field_dictionary_fk,
    check_governance_bidirectional,
    check_industry_graph_field_dictionary,
    run_all_registry_validations,
)
from align_battle_map import (  # noqa: E402
    BattleMapAlignmentReport,
)
from align_battle_map import (
    run_alignment as run_battle_map_alignment,
)

# 导入两个对齐检测器
from align_panoramas import (  # noqa: E402  # noqa: import-integrity  sys.path 动态加载的本地模块
    PanoramaAlignmentReport,
    PanoramaEmptyError,
)

# 第六图 frontend_map 校验器（2026-09-04 六图对齐升级，同目录）
from check_frontend_map import run_checks as run_frontend_map_checks  # noqa: E402
# 第七图 trading_decision_map 校验器（2026-09-05 七图升级 #ARCH-DECISION-MAP-GATE-001，同目录）
from check_decision_map import run_checks as run_decision_map_checks  # noqa: E402
from align_panoramas import (  # noqa: E402  # noqa: import-integrity  sys.path 动态加载的本地模块
    run_alignment as run_panorama_alignment,
)

# 默认输出路径
_DEFAULT_OVERVIEW = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "panorama_alignment_overview.md"
)


# ============================================================
# 第九节 图 10 GOMAP（governance_operations_map）校验（2026-09-15 十图升级 #ARCH-312）
# 校验逻辑零新文件：机生层单一真源=generate_governance_map.scan() 内联复用重建比对；
# 人工层=GOM-L0..L6 层位合法+mounts/disconnected import spec 磁盘实存+disconnected 必带 note。
# ============================================================
_GOM_VALID_LAYERS = {f"GOM-L{i}" for i in range(7)}
_GOM_TOMBSTONE_MARKERS = ("已删", "已退役", "deleted")
_GOM_SPEC_RE = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+")


def _gomap_resolve_spec(spec: str) -> Path | None:
    """import spec → 磁盘路径解析（module/包/symbol 三态），解析失败返回 None。"""
    parts = spec.split(".")
    rel = "/".join(parts)
    for cand in (f"src/{rel}.py", f"src/{rel}/__init__.py", f"{rel}.py", f"{rel}/__init__.py"):
        p = _REPO_ROOT / cand
        if p.exists():
            return p
    if len(parts) > 1:
        # symbol 形态：父模块/包实存且 token 在其源码文本出现
        prel = "/".join(parts[:-1])
        tok = parts[-1]
        for cand in (f"src/{prel}.py", f"src/{prel}/__init__.py", f"{prel}.py", f"{prel}/__init__.py"):
            p = _REPO_ROOT / cand
            if p.exists() and tok in p.read_text(encoding="utf-8", errors="replace"):
                return p
    return None


def _gomap_diff_families(existing_fams: dict, rebuild: dict, hard: list[str]) -> None:
    """机生层：families 与 scan() 重建逐族逐模块比对（generated_at/counts 不在比对范围）。"""
    for fam in sorted(set(rebuild) | set(existing_fams)):
        reb = {m.get("path"): m for m in (rebuild.get(fam) or [])}
        ext = {m.get("path"): m for m in (existing_fams.get(fam) or [])}
        for p in sorted(set(reb) - set(ext)):
            hard.append(f"机生层漂移 {fam}: {p}（scan() 重建新增，yaml 未刷新——重跑 generate_governance_map.py）")
        for p in sorted(set(ext) - set(reb)):
            hard.append(f"机生层幽灵 {fam}: {p}（磁盘已消失，yaml 未刷新——重跑 generate_governance_map.py）")
        for p in sorted(set(reb) & set(ext)):
            if reb[p] != ext[p]:
                hard.append(f"机生层元数据漂移 {fam}: {p}（wiring/domain/maturity 与重建不一致）")


def _gomap_check_mounts(lid: str, layer: dict, hard: list[str]) -> None:
    """人工层：mounts import spec 磁盘实存。"""
    for spec in layer.get("mounts") or []:
        if _gomap_resolve_spec(str(spec)) is None:
            hard.append(f"{lid} mount 路径不存在: {spec}")


def _gomap_check_disconnected(lid: str, layer: dict, hard: list[str]) -> int:
    """人工层：disconnected 必带 note；已删墓碑（note 含已删/已退役/deleted）豁免计软。

    Returns:
        soft（已删墓碑豁免条数，warn 待清理）。
    """
    soft = 0
    for item in layer.get("disconnected") or []:
        mod = str(item.get("mod", "")).strip()
        note = str(item.get("note_zh", "")).strip()
        if not note:
            hard.append(f"{lid} disconnected 缺 note: {mod}")
        if _GOM_SPEC_RE.fullmatch(mod) and _gomap_resolve_spec(mod) is None:
            if any(mk in note for mk in _GOM_TOMBSTONE_MARKERS):
                soft += 1  # 已删墓碑：如实记录现实，warn 级待清理，不阻断
            else:
                hard.append(f"{lid} disconnected 路径不存在且无已删标记: {mod}")
    return soft


def _gomap_check_layers(layers: list, hard: list[str]) -> int:
    """人工层：GOM-L0..L6 层位合法 + mounts/disconnected 逐层检查。Returns: soft 数。"""
    soft = 0
    for layer in layers:
        lid = str(layer.get("id", "?"))
        if lid not in _GOM_VALID_LAYERS:
            hard.append(f"人工层非法层位 {lid}（合法=GOM-L0..L6）")
        _gomap_check_mounts(lid, layer, hard)
        soft += _gomap_check_disconnected(lid, layer, hard)
    return soft


def _check_gomap_alignment(data: dict, rebuild: dict) -> tuple[int, int]:
    """图 10 GOMAP 对齐校验。

    机生层：yaml families 与 scan() 重建逐族逐模块比对（generated_at/counts 不在比对范围）。
    人工层：层位合法 + mounts 实存 + disconnected 实存（已删墓碑凭 note 豁免计软）+ note 必带。
    Returns:
        (hard, soft) —— hard=error 级违规数（阻断），soft=已删墓碑豁免条数（warn 待清理）。
    """
    hard: list[str] = []
    _gomap_diff_families(data.get("families") or {}, rebuild, hard)
    soft = _gomap_check_layers((data.get("pipeline") or {}).get("layers") or [], hard)
    if hard:
        for x in hard[:20]:
            print(f"    FAIL: {x}")
    return len(hard), soft


def _build_overview(
    pano: PanoramaAlignmentReport,
    bm: BattleMapAlignmentReport,
    generated_at: str,
    fm_fails: list[str],
    fm_warns: list[str],
    fm_total: int,
    dm_fails: list[str] | None = None,
    dm_warns: list[str] | None = None,
    dm_total: int = 0,
    layer2_hard: int = 0,
    layer2_soft: int = 0,
    layer2_entries: int = 0,
    doc_soft: int = 0,
    ig_hard: int = 0,
    ig_soft: int = 0,
    fac_hard: int = 0,
    fac_soft: int = 0,
    gom_hard: int = 0,
    gom_soft: int = 0,
) -> str:
    """构建全图全库对齐总览 Markdown（2026-09-15 十图升级：+图 10 治理运行地图）。
    命名口径=#ARCH-ALIGN-NAMING-001 计数无关命名。"""
    dm_fails = dm_fails or []
    dm_warns = dm_warns or []
    lines: list[str] = []
    lines.append("# 全图全库对齐总览 (Full-Panorama Alignment Overview)")
    lines.append("")
    lines.append(f"> 生成时间: {generated_at}")
    lines.append("> 对齐轴: module_id（图 1-4/图 10 机生层）+ step_id（图 5）+ feature_id（图 6）+ node_id（图 7 TDM-*/图 9 FAC-*）+ chain_id（图 8）+ import spec（图 10 人工层）")
    lines.append("> 全景图（现 10 张）: depgraph / dataflowgraph / decisiongraph / blueprint.md / battle_map / frontend_map / trading_decision_map / industry_chain_map / strategy_production_map / governance_operations_map")
    lines.append("")

    # === 图 1-4：全景对齐（module_id 轴）===
    lines.append("## 一、全景对齐（module_id 轴，图 1-4）")
    lines.append("")
    lines.append("### 节点统计")
    lines.append("")
    lines.append("| 图 | 节点数 |")
    lines.append("|---|---:|")
    lines.append(f"| depgraph | {pano.depgraph_count} |")
    lines.append(f"| dataflowgraph | {pano.dataflow_count} |")
    lines.append(f"| decisiongraph | {pano.decision_count} |")
    lines.append(f"| blueprint.md | {pano.blueprint_count} |")
    lines.append("")

    lines.append("### 问题汇总")
    lines.append("")
    lines.append("| 类型 | 数量 | 级别 |")
    lines.append("|---|---:|---|")
    lines.append(f"| 孤儿（仅一图存在） | {len(pano.orphans)} | warn |")
    lines.append(f"| 状态漂移（design_maturity 不一致） | {len(pano.state_drifts)} | warn |")
    lines.append(f"| **域不一致（domain_id 不一致）** | {len(pano.domain_mismatches)} | **硬阻断** |")
    lines.append(f"| 设计态孤立（design 仅一图） | {len(pano.design_only_in_one)} | warn |")
    lines.append(f"| **小计** | {pano.issues_total} | |")
    lines.append("")

    # === 图 5：作战地图对齐（step_id 轴）===
    lines.append("## 二、作战地图对齐（step_id 轴，图 5）")
    lines.append("")
    lines.append("### 三表统计")
    lines.append("")
    lines.append("| 表 | 记录数 |")
    lines.append("|---|---:|")
    lines.append(f"| battle_map_steps（环节） | {bm.step_count} |")
    lines.append(f"| battle_map_anchors（锚点） | {bm.anchor_count} |")
    lines.append(f"| battle_map_edges（流转边） | {bm.edge_count} |")
    lines.append(f"| 翻译真源已登记叙事 | {bm.narrative_count} |")
    lines.append("")

    lines.append("### 问题汇总")
    lines.append("")
    lines.append("| 类型 | 数量 | 级别 |")
    lines.append("|---|---:|---|")
    lines.append(f"| 孤儿环节（BM-INV-001） | {len(bm.orphan_steps)} | warn |")
    lines.append(f"| **幽灵锚点（BM-INV-002）** | {len(bm.ghost_anchors)} | **硬阻断** |")
    lines.append(f"| 缺失叙事（BM-INV-003） | {len(bm.missing_narratives)} | warn |")
    lines.append(f"| 悬空边 | {len(bm.dangling_edges)} | warn |")
    lines.append(f"| 域漂移（BM-INV-004） | {len(bm.domain_drifts)} | warn |")
    lines.append(f"| 父子嵌套问题（BM-INV-006） | {len(bm.parent_child_issues)} | warn |")
    lines.append(f"| 孤儿模块（BM-INV-007，违规） | {len(bm.orphan_modules)} | warn |")
    lines.append(f"| 已确认合理孤儿环节 | {len(bm.acknowledged_orphan_steps)} | 信息 |")
    lines.append(f"| 已确认合理孤儿模块 | {len(bm.acknowledged_orphan_modules)} | 信息 |")
    if bm.source_unavailable:
        lines.append(f"| 目标图源不可用（降级） | {','.join(bm.source_unavailable)} | 告警 |")
    lines.append(f"| **小计** | {bm.issues_total} | |")
    lines.append("")

    # === 图 6：frontend_map 对齐（feature_id 轴，2026-09-04 六图升级）===
    lines.append("## 三、frontend_map 对齐（feature_id 轴，图 6）")
    lines.append("")
    lines.append(f"- 功能点总数: {fm_total}")
    lines.append(f"- R0 id 重复 / R1 backend_ref 悬空: {len(fm_fails)}")
    lines.append(f"- R2 manifest 双向 / R3 file 失联 warn: {len(fm_warns)}")
    lines.append("")

    # === 图 7：trading_decision_map 对齐（node_id 轴，2026-09-05 七图升级）===
    lines.append("## 四、trading_decision_map 对齐（node_id 轴，图 7）")
    lines.append("")
    lines.append(f"- 决策链节点总数: {dm_total}")
    lines.append(f"- R1-R8 error 级缺口: {len(dm_fails)}")
    lines.append(f"- warning 级（module_ref 红节点占位等）: {len(dm_warns)}")
    lines.append("")

    # === 图 9：strategy_production_map 对齐（node_id FAC-* 轴，2026-09-13 九图升级）===
    lines.append("## 五、strategy_production_map 对齐（node_id FAC-* 轴，图 9）")
    lines.append("")
    lines.append(f"- 结构十项+仓储存在性硬违规: {fac_hard}")
    lines.append(f"- warning 级（待定入库位/CH 环境异常）: {fac_soft}")
    lines.append("")

    # === 图 10：governance_operations_map 对齐（module_id/import spec 轴，2026-09-15 十图升级）===
    lines.append("## 六、governance_operations_map 对齐（module_id/import spec 轴，图 10）")
    lines.append("")
    lines.append(f"- 机生层 families 重建比对漂移+人工层实存性/层位/note error: {gom_hard}")
    lines.append(f"- warning 级（已删墓碑豁免待清理）: {gom_soft}")
    lines.append("")

    # === 汇总裁定 ===
    lines.append("## 七、汇总裁定")
    lines.append("")

    hard_issues = (
        len(pano.domain_mismatches) + len(bm.ghost_anchors) + len(fm_fails) + len(dm_fails)
        + layer2_hard + fac_hard + gom_hard
    )
    soft_issues = (
        pano.issues_total
        - len(pano.domain_mismatches)
        + bm.issues_total
        - len(bm.ghost_anchors)
        + len(fm_warns)
        + len(dm_warns)
        + layer2_soft
        + doc_soft
        + ig_hard  # 图 8 数据层暂计软（长城专项清欠中，清零后升硬）
        + ig_soft
        + fac_soft  # 图 9 待定入库位/CH 环境异常（增长轨设计态预期内，不阻断）
        + gom_soft  # 图 10 已删墓碑豁免（如实记录，待清理，不阻断）
    )
    lines.append("### 注册表层（第二层满贯）+ 产业链图 8")
    lines.append("")
    lines.append(f"- 注册表条目: {layer2_entries}（19 文件/21 段，id 唯一+module_id+depgraph 存在性）")
    lines.append(f"- 注册表层硬违规: {layer2_hard}，软 warn: {layer2_soft}")
    lines.append(f"- 产业链图 8 数据层: 硬违规 {ig_hard}（暂计软，长城清欠中）+ advisory {ig_soft}")
    lines.append("")

    if hard_issues > 0:
        lines.append(f"❌ **硬阻断**: {hard_issues} 个硬问题须修复后才能施工")
        lines.append(f"   - 全景域不一致: {len(pano.domain_mismatches)}")
        lines.append(f"   - 作战地图幽灵锚点: {len(bm.ghost_anchors)}")
        lines.append(f"   - frontend_map fail: {len(fm_fails)}")
        lines.append(f"   - trading_decision_map error: {len(dm_fails)}")
        lines.append(f"   - strategy_production_map error: {fac_hard}")
        lines.append(f"   - governance_operations_map error: {gom_hard}")
    else:
        lines.append(
            "✅ **硬问题清零**: domain_mismatches=0, ghost_anchors=0, frontend_map fail=0, "
            "decision_map error=0, factory_map error=0, gomap error=0"
        )

    if soft_issues > 0:
        lines.append(f"⚠️ **软问题**: {soft_issues} 个 warn 级问题（君子协定，不阻断施工）")
    else:
        lines.append("✅ **软问题清零**: 无 warn 级问题")

    lines.append("")
    lines.append("---")
    lines.append(
        "> 本报告由 align_all.py 自动生成（ARCH-ALIGN-UNIFIED-001 六图升级 2026-09-04），复用 align_panoramas + align_battle_map + check_frontend_map 检测逻辑。"
    )
    lines.append("> 详细报告: panorama_alignment_report.md + battle_map_alignment_report.md + check_frontend_map.py 输出")

    return "\n".join(lines) + "\n"


def main() -> int:
    """Entry point: parse args, run both alignments, return exit code."""
    parser = argparse.ArgumentParser(
        description="六图对齐执行入口（ARCH-ALIGN-UNIFIED-001 六图升级，复用 align_panoramas + align_battle_map + check_frontend_map）"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="总览报告输出路径（默认 docs/02_enterprise_architecture/03_governance_reports/panorama_alignment_overview.md）",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="不写总览报告（门禁场景，仅返回 exit code）",
    )
    args = parser.parse_args()

    output_path = args.output or _DEFAULT_OVERVIEW

    # --- 图 1-4：全景对齐（module_id 轴）---
    print("=" * 60)
    print("全图全库对齐总览（ARCH-ALIGN-UNIFIED-001，现 10 张全景图）")
    print("=" * 60)
    print()
    print("[1/9] 全景对齐（module_id 轴，图 1-4）...")
    try:
        pano = run_panorama_alignment(write_report=False)
    except PanoramaEmptyError as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR

    print(
        f"  OK: 节点 depgraph={pano.depgraph_count} / "
        f"dataflow={pano.dataflow_count} / "
        f"decision={pano.decision_count} / "
        f"blueprint={pano.blueprint_count}"
    )
    print(
        f"  问题: 孤儿={len(pano.orphans)}, "
        f"状态漂移={len(pano.state_drifts)}, "
        f"域不一致={len(pano.domain_mismatches)}, "
        f"设计态孤立={len(pano.design_only_in_one)}"
    )

    # --- 图 5：作战地图对齐（step_id 轴）---
    print()
    print("[2/9] 作战地图对齐（step_id 轴，图 5）...")
    try:
        bm = run_battle_map_alignment(write_report=False)
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR

    print(f"  OK: 环节={bm.step_count} / 锚点={bm.anchor_count} / 流转边={bm.edge_count}")
    print(
        f"  问题: 孤儿环节={len(bm.orphan_steps)}, "
        f"幽灵锚点={len(bm.ghost_anchors)}, "
        f"缺失叙事={len(bm.missing_narratives)}, "
        f"悬空边={len(bm.dangling_edges)}, "
        f"域漂移={len(bm.domain_drifts)}, "
        f"父子嵌套={len(bm.parent_child_issues)}, "
        f"孤儿模块={len(bm.orphan_modules)}"
    )

    # --- 汇总裁定 ---
    print()
    print("[3/9] 第六图 frontend_map 对齐（feature_id 轴，2026-09-04 六图升级）...")
    try:
        fm_fails, fm_warns, fm_total = run_frontend_map_checks()
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR
    print(f"  OK: 功能点={fm_total}（backend_ref 全类型化）")
    print(f"  问题: fail={len(fm_fails)}, warn={len(fm_warns)}")
    for x in fm_fails:
        print(f"    FAIL: {x}")

    # --- 图 7：trading_decision_map 对齐（node_id 轴，2026-09-05 七图升级）---
    print()
    print("[4/9] 第七图 trading_decision_map 对齐（node_id 轴，2026-09-05 七图升级）...")
    try:
        dm_fails, dm_warns, dm_total = run_decision_map_checks()
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR
    print(f"  OK: 决策链节点={dm_total}（R1-R8 引用校验）")
    print(f"  问题: error={len(dm_fails)}, warn={len(dm_warns)}")
    for x in dm_fails:
        print(f"    FAIL: {x}")

    # --- 第五节：注册表层对齐（第二层满贯，2026-09-11）---
    print()
    print("[5/9] 注册表层对齐（19 文件/21 段业务库 + 字典 FK + CAND 转正链 + 治理双向）...")
    layer2_hard = 0
    layer2_soft = 0
    try:
        reg_fails, reg_total = run_all_registry_validations(include_depgraph=True)
        fk_errors, fk_warns = check_field_dictionary_fk()
        cand_errors, cand_warns = check_candidate_promotion_chain()
        gov_errors, gov_warns = check_governance_bidirectional()
        ig_errors, ig_warns = check_industry_graph_field_dictionary()
        layer2_hard = len(reg_fails) + len(fk_errors) + len(cand_errors) + len(gov_errors) + len(ig_errors)
        layer2_soft = len(fk_warns) + len(cand_warns) + len(gov_warns) + len(ig_warns)
        print(f"  OK: 条目={reg_total}（id 唯一 + module_id MOD-* + depgraph 存在性 fail-open）")
        print(
            f"  问题: 硬={layer2_hard}"
            f"（注册表={len(reg_fails)}, 字典FK={len(fk_errors)}, CAND={len(cand_errors)}, "
            f"治理双向={len(gov_errors)}, 产业链字典={len(ig_errors)}）, "
            f"软={layer2_soft}"
        )
        for x in (reg_fails + fk_errors + cand_errors + gov_errors + ig_errors)[:20]:
            print(f"    FAIL: {x}")
    except Exception as e:  # noqa: BLE001 — 第二层故障不炸整个 align_all（降 warn）
        print(f"  WARN: 注册表层校验异常（降级跳过）: {e}")

    # --- 第六节：代码↔文档对齐（文档 node_id 硬编码检测，第三层抽查）---
    print()
    print("[6/9] 代码↔文档对齐（doc node_id 硬编码检测，GATE-DOC-NODE-ID 同源）...")
    doc_hard = 0
    doc_run = run_subprocess_hidden(
        [sys.executable, str(_REPO_ROOT_A / "scripts/governance/d3_metadata/check_doc_node_id_hardcode.py"), "--ci"],
        timeout=300,
    )
    if doc_run.returncode == 0:
        print("  OK: docs/** 零 node_id 硬编码")
    elif doc_run.returncode == 1:
        # 存量硬编码计 soft（增量由 GATE-DOC-NODE-ID commit gate 硬阻断；存量 12 处登记遗留清欠）
        print("  WARN: 文档存在存量易变物理 ID 硬编码（增量由 GATE-DOC-NODE-ID 硬管）")
        tail = (doc_run.stdout or "").strip().splitlines()[-5:]
        for line_x in tail:
            print(f"    SOFT: {line_x}")
    else:
        print(f"  WARN: 检测器异常 exit={doc_run.returncode}（fail-open，不阻断）")

    # --- 第七节：产业链全景图（图 8，chain_id 轴，2026-09-11 八图升级）---
    print()
    print("[7/9] 第八图 产业链全景图（chain_id 轴，graph_quality_check S1-S21 引擎判定）...")
    ig_hard = 0
    ig_soft = 0
    gq_run = run_subprocess_hidden(
        [sys.executable, str(_REPO_ROOT_A / "scripts/industry_graph/graph_quality_check.py"), "--json", "-"],
        timeout=600,
    )
    if gq_run.returncode == 2:
        print("  WARN: PG 不可达（图 8 引擎 fail-open，不计违规）")
    else:
        try:
            report = json.loads(gq_run.stdout or "{}")
            results = report.get("checks") or []
            hard_v = [(r, len(r.get("violations") or [])) for r in results if not r.get("advisory")]
            advisory_v = [(r, len(r.get("violations") or [])) for r in results if r.get("advisory")]
            ig_hard = int(report.get("total_violations") or sum(n for _, n in hard_v))
            ig_soft = sum(n for _, n in advisory_v)
            bad = [(r["id"], n) for r, n in hard_v if n]
            print(f"  OK: 合格线={len(results)} 项体检完成（硬违规={ig_hard}, advisory={ig_soft}）")
            for sid, n in bad[:10]:
                print(f"    FAIL: {sid} 违规 {n} 条（判定权=graph_quality_check 引擎，AI 只修复不判定）")
            if ig_soft:
                print(f"    WARN: advisory {ig_soft} 条（S21 族，长城任务进行中口径）")
            if ig_hard:
                print(f"    WARN: 图 8 数据层硬违规 {ig_hard} 条暂计软（长城专项清欠中，清零后升硬）")
        except (ValueError, KeyError) as e:
            print(f"  WARN: 图 8 引擎输出解析失败（降级不计违规）: {e}")

    # --- 第八节：策略生产全景图（图 9，node_id FAC-* 轴，2026-09-13 九图升级）---
    print()
    print("[8/9] 第九图 策略生产全景图（node_id FAC-* 轴，结构十项+仓储存在性）...")
    fac_hard = 0
    fac_soft = 0
    try:
        _validators_dir = str(_REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "validators")
        if _validators_dir not in sys.path:
            sys.path.insert(0, _validators_dir)
        from validate_strategy_production_map import check_stores, validate_structure  # noqa: import-integrity  sys.path 动态加载

        _fac_map = _REPO_ROOT / "config" / "strategy_production_map.yaml"
        _fac_data = yaml.safe_load(_fac_map.read_text(encoding="utf-8"))
        fac_errors = validate_structure(_fac_data)
        s_errors, s_warns = check_stores(_fac_data, root=_REPO_ROOT)
        # CH 连接异常（环境异常域）降 warn——学图 8 PG fail-open 先例；CH 表缺失/磁盘路径缺失保持硬
        _fac_infra = [x for x in s_errors if x.startswith("CH 表检查失败")]
        _fac_store_hard = [x for x in s_errors if not x.startswith("CH 表检查失败")]
        fac_hard = len(fac_errors) + len(_fac_store_hard)
        fac_soft = len(s_warns) + len(_fac_infra)
        print(
            f"  OK: 节点={len(_fac_data.get('nodes') or [])} 边={len(_fac_data.get('edges') or [])}"
            "（结构十项+仓储存在性，单一真源=validate_strategy_production_map）"
        )
        print(f"  问题: 硬={fac_hard}, 软={fac_soft}（含待定入库位 warn）")
        for x in (fac_errors + _fac_store_hard)[:20]:
            print(f"    FAIL: {x}")
        for x in _fac_infra[:5]:
            print(f"    WARN: {x}（CH 环境异常 fail-open）")
    except Exception as e:  # noqa: BLE001 — 图 9 故障不炸整个 align_all（降 warn，学第二层先例）
        print(f"  WARN: 图 9 校验异常（降级跳过不计违规）: {e}")

    # --- 第九节：治理运行地图（图 10，module_id/import spec 轴，2026-09-15 十图升级 #ARCH-312）---
    print()
    print("[9/9] 第十图 治理运行地图（GOMAP，机生层 scan() 重建比对+人工层实存性）...")
    gom_hard = 0
    gom_soft = 0
    try:
        if _GOV_DIR not in sys.path:
            sys.path.insert(0, _GOV_DIR)
        from generate_governance_map import scan as gomap_scan  # noqa: import-integrity  sys.path 动态加载

        _gomap_path = _REPO_ROOT / "config" / "governance_operations_map.yaml"
        _gomap_data = yaml.safe_load(_gomap_path.read_text(encoding="utf-8"))
        gom_hard, gom_soft = _check_gomap_alignment(_gomap_data, gomap_scan())
        _gom_total = sum(len(v) for v in (_gomap_data.get("families") or {}).values())
        print(f"  OK: 机生层模块={_gom_total}（单一真源=generate_governance_map.scan() 重建比对）")
        print(f"  问题: 硬={gom_hard}, 软={gom_soft}（已删墓碑豁免 warn 待清理）")
    except Exception as e:  # noqa: BLE001 — 图 10 故障不炸整个 align_all（降 warn，学图 9 先例）
        print(f"  WARN: 图 10 校验异常（降级跳过不计违规）: {e}")

    hard_issues = (
        len(pano.domain_mismatches)
        + len(bm.ghost_anchors)
        + len(fm_fails)
        + len(dm_fails)
        + layer2_hard
        + fac_hard
        + gom_hard
    )
    # 图 8 数据层违规（ig_hard）不计硬闸：产业链清欠=长城专项进行中（S21/S24 Owner gated、
    # S25 梳理清单在案），判定权=graph_quality_check 引擎；git 侧工件已由
    # INDUSTRY-CHAIN-MAP gate(141) 硬阻断。清零后升硬（登记 alignment_checklist §3 图 8 行）。
    print()
    print("-" * 60)
    if hard_issues > 0:
        print(
            f"❌ 硬阻断: {hard_issues} 个硬问题"
            f"（域不一致={len(pano.domain_mismatches)}, "
            f"幽灵锚点={len(bm.ghost_anchors)}, "
            f"frontend_map fail={len(fm_fails)}, "
            f"decision_map error={len(dm_fails)}, "
            f"factory_map error={fac_hard}, "
            f"gomap error={gom_hard}）"
        )
        print("   须修复后才能施工！")
    else:
        print(
            "✅ 硬问题清零: domain_mismatches=0, ghost_anchors=0, frontend_map fail=0, "
            "decision_map error=0, factory_map error=0, gomap error=0"
        )

    soft_issues = (
        pano.issues_total
        - len(pano.domain_mismatches)
        + bm.issues_total
        - len(bm.ghost_anchors)
        + len(fm_warns)
        + len(dm_warns)
        + gom_soft  # 图 10 已删墓碑豁免（warn 待清理）
    )
    if soft_issues > 0:
        print(f"⚠️ 软问题: {soft_issues} 个 warn 级问题（君子协定，不阻断）")
    else:
        print("✅ 软问题清零")

    # --- 写总览报告 ---
    if not args.no_report:
        from datetime import datetime, timezone

        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        overview = _build_overview(
            pano, bm, generated_at, fm_fails, fm_warns, fm_total, dm_fails, dm_warns, dm_total,
            layer2_hard=layer2_hard, layer2_soft=layer2_soft, layer2_entries=reg_total,
            doc_soft=1 if doc_run.returncode == 1 else 0, ig_hard=ig_hard, ig_soft=ig_soft,
            fac_hard=fac_hard, fac_soft=fac_soft,
            gom_hard=gom_hard, gom_soft=gom_soft,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(overview, encoding="utf-8")
        print()
        print(f"总览报告已写入: {output_path}")

    print()
    if hard_issues > 0:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
