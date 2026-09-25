# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.venue_dual_run
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator (import_ruler/ruler_available);
#                zephyr.intelligence.model_profiling.dual_run (OBJ_M 双跑执行器+三把尺统计，SSOT 引用不复制)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (claim_exam 注册表项)
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] OBJ_M 三把尺引用不重建（DESIGN §2.1 模型行：MCE 考试/同任务双跑 McNemar-Wilcoxon/成本审计）；
#              考纲 freeze 真源=config/dual_run_criteria.yaml（freeze_hash 经考尺件，本件只转调）；
#              裁判异厂异档约束由调用方保证（dual_run 原契约，本件不放宽）；
#              调不到考尺=fail-closed 拒考；A 档统计判据（alpha/效应量线读常量层，检验计算在考尺）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.1（模型行）；判据细节真源=
#                docs/_working/ai_layer_vision/OBJ_M_models/DESIGN.md §4
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 考尺 import 失败→VenueUnavailable；未知 op→ValueError；判据文件残缺→
#                  考尺侧 CriteriaError 原样上抛（不吞不包装，保留 OBJ_M 语义）
# [TESTS] tests/ai_layer/comparator/test_venues.py（criteria freeze_hash 同源/run_pair 转调/
#         mcnemar+wilcoxon 转调/fail-closed）
# [TTL] permanent
"""venue_dual_run — 模型考场适配器：OBJ_M 同任务双跑执行器的薄封装。

制式（DESIGN §2.1）：同任务双跑（五层×20 分层抽样，McNemar 二元/Wilcoxon 连续）+成本审计
（时段加权单价）。判据真源：考纲=config/dual_run_criteria.yaml（load_criteria+freeze_hash），
显著性/效应量线=config/comparison_policy.yaml significance 节（L4 常量层）。

本件零考尺逻辑：统计检验（mcnemar_p/wilcoxon_signed_rank_p）、逐样本记账（run_pair）、
判据冻结（freeze_hash）全部转调 ``zephyr.intelligence.model_profiling.dual_run``。
"""

from __future__ import annotations

import functools

from typing import Any, Final, Mapping

from zephyr.ai_layer.comparator import import_ruler, make_available_probe, ruler_available

__all__: Final = ["RULER_MODULES", "VENUE_ID", "available", "criteria", "run"]

VENUE_ID: Final = "venue_dual_run"
RULER_MODULES: Final = ("zephyr.intelligence.model_profiling.dual_run",)


# FUNCTION-DUP 治本（2026-09-24 st-ailayer-final-20260924）：available 与兄弟考场同体，partial 绑定唯一实现 ruler_available
available = make_available_probe(RULER_MODULES, globals())


def criteria() -> dict[str, Any]:
    """考纲快照+冻结哈希（OBJ_M C5 freeze_rule 同款，冻进 experiment 卡的考卷指纹）。"""
    dr = import_ruler(RULER_MODULES[0])
    loaded = dr.load_criteria()
    return {
        "venue": VENUE_ID,
        "criteria_path": str(dr.DEFAULT_CRITERIA_PATH),
        "criteria": loaded,
        "freeze_hash": dr.freeze_hash(loaded),
    }


def run(payload: Mapping[str, Any]) -> dict[str, Any]:
    """转调考尺（op 分派；fn/samples/judge 由调用方注入，本件零 LLM 依赖同考尺契约）。

    ops::

        run_pair   {challenger_fn, champion_fn, samples, judge_fn} → run_pair 逐样本记账
        mcnemar    {b: int, c: int} → mcnemar_p（二元判据 p 值）
        wilcoxon   {diffs: [float]} → wilcoxon_signed_rank_p（连续判据 p 值）
    """
    op = str(payload.get("op") or "")
    dr = import_ruler(RULER_MODULES[0])
    if op == "run_pair":
        records = dr.run_pair(
            payload["challenger_fn"],
            payload["champion_fn"],
            payload["samples"],
            payload["judge_fn"],
        )
        return {"venue": VENUE_ID, "op": op, "records": records}
    if op == "mcnemar":
        return {"venue": VENUE_ID, "op": op, "p": dr.mcnemar_p(int(payload["b"]), int(payload["c"]))}
    if op == "wilcoxon":
        return {"venue": VENUE_ID, "op": op, "p": dr.wilcoxon_signed_rank_p(list(payload["diffs"]))}
    raise ValueError(f"venue_dual_run unknown_op:{op}")
