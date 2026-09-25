# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_comparator
# [MODULE] zephyr.ai_layer.comparator.venue_tool_bench
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.comparator (ruler_available/VenueUnavailable/import_ruler)
# [CONSUMERS] zephyr.ai_layer.comparator.executor (claim_exam 注册表项)
# [STARTUP] event_driven
# [MATURITY] new
# [INVARIANTS] OBJ_T 基准任务集引用不重建（DESIGN §2.1 工具行：OBJ_T 卡待深挖，L4 先锁制式）；
#              考尺未建成→available()=False→claim_exam 拒考（fail-closed 是本件当前的**正常态**，
#              不是故障）；制式锁定：同基准任务集版本双跑（同工具族新 vs 老），判成功率/速度/成本，
#              小样本按 Tier B 诚实条款（未决不硬判）；删除类工具专项红线归 OBJ_S（本件不接）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L4_compare/DESIGN.md §2.1（工具行）；考尺建成后将
#                RULER_MODULES 指向 OBJ_T 目录真源（改一处常量即可，制式不变）
# [STABILITY] new
# [SAFETY] L
# [ALGO_FLOW] external: docs/03_modules/_domain_ai_layer/algo_flow/venue_tool_bench.yaml
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 考尺未建成→available()=False + run() VenueUnavailable（拒考，DESIGN C4 验收
#                  标准的既定路径）；未知 op→ValueError
# [TESTS] tests/ai_layer/comparator/test_venues.py（未建成=available False+run 拒考/
#         op 白名单/RULER_MODULES 指针存在性）
# [TTL] permanent
"""venue_tool_bench — 工具考场适配器：OBJ_T 基准任务集的薄封装（考尺未建，先锁制式）。

制式（DESIGN §2.1，锁定待 OBJ_T 落地）：同基准任务集**版本号**双跑（同工具族新 vs 老），
判成功率/速度/成本；工具-模型配对实验借用 OBJ_M dual_run 执行器（venue_dual_run 承接）；
小样本按 §2.4 B 档诚实条款（效应量+CI 全宽+未决不硬判）。

现状：OBJ_T 基准任务集目录未建成（vision README §3.5 OBJ_T-#2 治理立案保留中）——
本件把"拒考"作为一等公民：available() 探测 OBJ_T 真源模块，缺席即拒考，
绝不本地造考卷（D-L4-01：L4 不自建考尺）。
"""

from __future__ import annotations

import functools

from typing import Any, Final, Mapping

from zephyr.ai_layer.comparator import import_ruler, make_available_probe, ruler_available

__all__: Final = ["RULER_MODULES", "VENUE_ID", "available", "criteria", "run"]

VENUE_ID: Final = "venue_tool_bench"
# OBJ_T 基准任务集真源指针（接线批 2026-09-24 指向 OBJ_T 真源 zephyr.ai_layer.tools.suite；
# 缺席=拒考，fail-closed 不变——考尺真身缺席时 available()=False 行为与指针错位期一致）
RULER_MODULES: Final = ("zephyr.ai_layer.tools.suite",)


# FUNCTION-DUP 治本（2026-09-24 st-ailayer-final-20260924）：available 与兄弟考场同体，partial 绑定唯一实现 ruler_available
available = make_available_probe(RULER_MODULES, globals())


def criteria() -> dict[str, Any]:
    """考卷快照（基准任务集版本+陷阱题构成）——考尺建成前调不到=VenueUnavailable。"""
    bench = import_ruler(RULER_MODULES[0])
    return dict(bench.suite_criteria())


def run(payload: Mapping[str, Any]) -> dict[str, Any]:
    """转调考尺（op 分派；考尺建成前任何 op 都拒考）。

    ops（制式锁定，OBJ_T 落地后生效）::

        suite_run  {tool_ref, suite_version} → 同版本双跑记账（成功率/速度/成本）
    """
    op = str(payload.get("op") or "")
    if op != "suite_run":
        raise ValueError(f"venue_tool_bench unknown_op:{op}")
    bench = import_ruler(RULER_MODULES[0])
    return dict(bench.suite_run(dict(payload)))
