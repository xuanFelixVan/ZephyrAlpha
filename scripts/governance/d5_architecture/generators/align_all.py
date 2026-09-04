# [BLUEPRINT] MOD-GOV-ALIGN-ALL | docs/03_modules/_domain_governance/panorama_alignment_engine/align_all_blueprint.md | §main
# [MODULE] scripts.governance.d5_architecture.generators.align_all
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.generators.align_panoramas (run_alignment); scripts.governance.align_battle_map (run_alignment); _shared.constants (EXIT_*)
# [CONSUMERS] CI自动触发;人工审查五图对齐总览;施工前对齐验证（AGENTS.md RULE-DEPGRAPH 第三件事）
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
# [ARCH-REF] #ARCH-ALIGN-UNIFIED-001 #ARCH-053 #ARCH-056
# [CREATION-TOKEN] ARCH-ALIGN-UNIFIED-001
"""G-align-all: 六图对齐执行入口（ARCH-ALIGN-UNIFIED-001，2026-09-04 六图升级）

依据：trae_080_panorama_alignment.yaml v1.1.0（五图对齐铁律）;
      ARCH-053/056（全景对齐机制）; battle_map_positioning.md §八（与全景图对齐体系的关系）;
      2026-09-04 六图升级（Owner 裁定：+frontend_map 第六图，check_frontend_map 复用接入）

功能：
  一站式六图对齐验证——调 align_panoramas.run_alignment 查图 1-4（module_id 轴）+
  调 align_battle_map.run_alignment 查图 5（step_id 轴）+
  调 check_frontend_map.run_checks 查图 6（feature_id 轴），产出总览报告。

六图定义：
  图 1-4（module_id 轴）：depgraph / dataflowgraph / decisiongraph / blueprint.md
  图 5  （step_id 轴）  ：battle_map（通过 anchors 与图 1-4 双向校验）
  图 6  （feature_id 轴）：frontend_map（真源 web/frontend_map.yaml，R0-R3 校验）

强制力分层：
  硬问题（exit 1）：domain_mismatches（图 1-4 域不一致）/ ghost_anchors（图 5 幽灵锚点）/
                    frontend_map fail（图 6 悬空/重复）
  软问题（exit 0 + warn）：orphans / state_drifts / design_only_in_one /
                          orphan_steps / missing_narratives / dangling_edges /
                          domain_drifts / parent_child_issues / orphan_modules / frontend_map warns

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
description: 'G-align-all: 五图对齐执行入口（ARCH-ALIGN-UNIFIED-001）'
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

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402
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
from align_panoramas import (  # noqa: E402  # noqa: import-integrity  sys.path 动态加载的本地模块
    run_alignment as run_panorama_alignment,
)

# 默认输出路径
_DEFAULT_OVERVIEW = (
    _REPO_ROOT / "docs" / "02_enterprise_architecture" / "03_governance_reports" / "panorama_alignment_overview.md"
)


def _build_overview(
    pano: PanoramaAlignmentReport,
    bm: BattleMapAlignmentReport,
    generated_at: str,
    fm_fails: list[str],
    fm_warns: list[str],
    fm_total: int,
) -> str:
    """构建六图对齐总览 Markdown（2026-09-04 六图升级：+frontend_map）。"""
    lines: list[str] = []
    lines.append("# 六图对齐总览 (Six-Panorama Alignment Overview)")
    lines.append("")
    lines.append(f"> 生成时间: {generated_at}")
    lines.append("> 对齐轴: module_id（图 1-4）+ step_id（图 5）+ feature_id（图 6）")
    lines.append("> 六图: depgraph / dataflowgraph / decisiongraph / blueprint.md / battle_map / frontend_map")
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

    # === 汇总裁定 ===
    lines.append("## 四、汇总裁定")
    lines.append("")

    hard_issues = len(pano.domain_mismatches) + len(bm.ghost_anchors) + len(fm_fails)
    soft_issues = (
        pano.issues_total
        - len(pano.domain_mismatches)
        + bm.issues_total
        - len(bm.ghost_anchors)
        + len(fm_warns)
    )

    if hard_issues > 0:
        lines.append(f"❌ **硬阻断**: {hard_issues} 个硬问题须修复后才能施工")
        lines.append(f"   - 全景域不一致: {len(pano.domain_mismatches)}")
        lines.append(f"   - 作战地图幽灵锚点: {len(bm.ghost_anchors)}")
        lines.append(f"   - frontend_map fail: {len(fm_fails)}")
    else:
        lines.append("✅ **硬问题清零**: domain_mismatches=0, ghost_anchors=0, frontend_map fail=0")

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
    print("五图对齐总览（ARCH-ALIGN-UNIFIED-001）")
    print("=" * 60)
    print()
    print("[1/2] 全景对齐（module_id 轴，图 1-4）...")
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
    print("[2/3] 作战地图对齐（step_id 轴，图 5）...")
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
    print("[3/3] 第六图 frontend_map 对齐（feature_id 轴，2026-09-04 六图升级）...")
    try:
        fm_fails, fm_warns, fm_total = run_frontend_map_checks()
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR
    print(f"  OK: 功能点={fm_total}（backend_ref 全类型化）")
    print(f"  问题: fail={len(fm_fails)}, warn={len(fm_warns)}")
    for x in fm_fails:
        print(f"    FAIL: {x}")

    hard_issues = len(pano.domain_mismatches) + len(bm.ghost_anchors) + len(fm_fails)
    print()
    print("-" * 60)
    if hard_issues > 0:
        print(
            f"❌ 硬阻断: {hard_issues} 个硬问题"
            f"（域不一致={len(pano.domain_mismatches)}, "
            f"幽灵锚点={len(bm.ghost_anchors)}, "
            f"frontend_map fail={len(fm_fails)}）"
        )
        print("   须修复后才能施工！")
    else:
        print("✅ 硬问题清零: domain_mismatches=0, ghost_anchors=0, frontend_map fail=0")

    soft_issues = (
        pano.issues_total
        - len(pano.domain_mismatches)
        + bm.issues_total
        - len(bm.ghost_anchors)
        + len(fm_warns)
    )
    if soft_issues > 0:
        print(f"⚠️ 软问题: {soft_issues} 个 warn 级问题（君子协定，不阻断）")
    else:
        print("✅ 软问题清零")

    # --- 写总览报告 ---
    if not args.no_report:
        from datetime import datetime, timezone

        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        overview = _build_overview(pano, bm, generated_at, fm_fails, fm_warns, fm_total)
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
