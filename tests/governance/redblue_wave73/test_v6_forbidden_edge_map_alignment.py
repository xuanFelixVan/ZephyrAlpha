# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v6_forbidden_edge_map_alignment
# [DOMAIN] D_GOV_CODE_QUALITY
"""wave7.3 V6 绕禁止边：MAP-ALIGNMENT 面的悬空边/禁止边语义在案记录。

在案发现（不虚报为已拦）：battle_map 对齐判定 evaluate_battle_map_report 将
悬空边（dangling_edges，含"禁用边仍被引用"形态）归入 **soft**（warn-only），
hard 面只有违规孤儿环节/缺失叙事——即提交面禁用边可无感通过（warn 留痕）。
防线前移事实：写入端 apply_battle_map.op_add_anchor 强制 target 存在性校验
（2026-09-15 裁定，见 battle_map_alignment_gate 模块 docstring"幽灵锚点降级裁定"）。
本用例固化该分级现状：若未来把悬空边升 hard，此测试红=升级生效信号。
"""

from __future__ import annotations

from types import SimpleNamespace

from zephyr.gov_enforcement.commit_gates.battle_map_alignment_gate import evaluate_battle_map_report


def test_dangling_edge_is_soft_currently__documented_finding():
    report = SimpleNamespace(
        ghost_anchors=[],
        orphan_steps=[],
        missing_narratives=[],
        domain_drifts=[],
        dangling_edges=[{"from": "STEP-A", "to": "STEP-GONE", "map": "depgraph"}],
        parent_child_issues=[],
        orphan_modules=[],
    )
    hard, soft = evaluate_battle_map_report(report)
    assert hard == [], "悬空边已升 hard——V6 在案发现过时，请更新记录"
    assert any("悬空边" in s for s in soft), "悬空边未进 soft 列表——warn 留痕面失灵"


def test_orphan_step_and_missing_narrative_stay_hard():
    """对照：hard 面两判据（违规孤儿环节/缺失叙事）仍在——面未整体失守。"""
    report = SimpleNamespace(
        ghost_anchors=[],
        orphan_steps=[{"step_id": "S-ORPHAN"}],
        missing_narratives=[{"step_id": "S-NONARR"}],
        domain_drifts=[],
        dangling_edges=[],
        parent_child_issues=[],
        orphan_modules=[],
    )
    hard, soft = evaluate_battle_map_report(report)
    assert len(hard) == 2
    assert any("孤儿环节" in h for h in hard) and any("缺失叙事" in h for h in hard)
    assert soft == []
