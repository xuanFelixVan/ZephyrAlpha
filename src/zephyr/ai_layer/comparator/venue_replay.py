# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.venue_replay
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator (import_ruler/ruler_available);
#                zephyr.governance.standards_governance.rule_replay (OBJ_R 重放器+P1-P4，SSOT 引用不复制)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (claim_exam 注册表项)
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] OBJ_R 历史重放器复用不重建（DESIGN §2.1 门禁参数行）；本件只做两件增补：
#              ①criteria() 把 P1-P4 判据快照交给调用方冻进 experiment 卡（预注册时序机检）；
#              ②run() 把重放结果聚合回统一裁定卡载荷；判据 SSOT=rule_replay 模块常量；
#              调不到考尺=fail-closed 拒考；B' 档确定性对照（非统计推断，禁报 p 值）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.1（门禁参数行）；判据细节真源=
#                docs/_working/ai_layer_vision/OBJ_R_rules_standards/DESIGN.md §②-E
# [STABILITY] new
# [SAFETY] L
# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/venue_replay.yaml
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 考尺 import 失败→VenueUnavailable；未知 op→ValueError；
#                  request 非 ReplayRequest 实例→TypeError（契约在考尺侧，不复制不放宽）
# [TESTS] tests/ai_layer/comparator/test_venues.py（criteria 快照=rule_replay 常量同源/
#         未知 op/request 契约/fail-closed）
# [TTL] permanent
"""venue_replay — 门禁参数/成本线重放考场适配器：OBJ_R 重放器的薄封装（B' 档确定性对照）。

制式（DESIGN §2.1）：新阈值 vs 现行常量对历史提交集重放（内存 stub gateway，first-parent diff
纯函数对照），判据=P1-P4（放走=0/误拦≤2%/Jaccard≥0.98·0.95）。本件零考尺逻辑——判据常量、
抽样、diff 对照全在 ``zephyr.governance.standards_governance.rule_replay``。

成本线重放（降档规则 vs 现行规则对 usage_records）为同构重放（OBJ_R 重放器同构换数据底表），
考尺建成前经本件同 op 形态接入，调不到=拒考。
"""

from __future__ import annotations

import functools

from pathlib import Path
from typing import Any, Final, Mapping

from zephyr.ai_layer.comparator import import_ruler, make_available_probe, ruler_available

__all__: Final = ["RULER_MODULES", "VENUE_ID", "available", "criteria", "run"]

VENUE_ID: Final = "venue_replay"
RULER_MODULES: Final = ("zephyr.governance.standards_governance.rule_replay",)


# FUNCTION-DUP 治本（2026-09-24 st-ailayer-final-20260924）：available 与兄弟考场同体，partial 绑定唯一实现 ruler_available
available = make_available_probe(RULER_MODULES, globals())


def criteria() -> dict[str, Any]:
    """P1-P4 判据快照（SSOT=rule_replay 模块常量，逐值直读不复制）——冻进 experiment 卡。"""
    rr = import_ruler(RULER_MODULES[0])
    return {
        "venue": VENUE_ID,
        "P1_pass_leak_allowed": rr.P1_PASS_LEAK_ALLOWED,
        "P2_new_block_rate": rr.P2_NEW_BLOCK_RATE,
        "P3_jaccard_global": rr.P3_JACCARD_GLOBAL,
        "P3_jaccard_per_gate": rr.P3_JACCARD_PER_GATE,
        "error_rate_unreliable": rr.ERROR_RATE_UNRELIABLE,
        "inference": "deterministic_replay_no_p_value",
    }


def run(payload: Mapping[str, Any]) -> dict[str, Any]:
    """转调考尺（op 分派）。

    ops::

        replay     {request: rule_replay.ReplayRequest 实例}
                   → run_replay + summarize（聚合回统一裁定卡载荷）
        summarize  {report_path: str} → summarize(report.jsonl)
    """
    op = str(payload.get("op") or "")
    rr = import_ruler(RULER_MODULES[0])
    if op == "replay":
        request = payload["request"]
        if not isinstance(request, rr.ReplayRequest):
            raise TypeError(f"venue_replay 需要 ReplayRequest 实例，得:{type(request).__name__}")
        report_path = rr.run_replay(request)
        return {
            "venue": VENUE_ID,
            "op": op,
            "report_path": str(report_path),
            "summary": rr.summarize(report_path),
        }
    if op == "summarize":
        return {
            "venue": VENUE_ID,
            "op": op,
            "summary": rr.summarize(Path(str(payload["report_path"]))),
        }
    raise ValueError(f"venue_replay unknown_op:{op}")
