# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.quality.blueprint_scorer
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS] zephyr.orchestrator.trigger_router; zephyr.shared.utils.blueprint_scorer (re-export); zephyr.shared.blueprint_scorer (re-export)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_blueprint_scorer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BlueprintScorer — 蓝图路由统一打分逻辑

此模块提供 blueprint_routing.yaml 路由表的统一评分函数，
供 trigger_router.handle_blueprint_lookup_stub 和
mcp.BlueprintSearchServer._find_relevant_blueprint 共用。

SSoT: config/blueprint_routing.yaml routes
KBG:  路由）+
"""

from __future__ import annotations

import fnmatch
from typing import Any


def score_blueprint_route(
    route: dict[str, Any],
    path_patterns: list[str] | None = None,
    task_keywords: list[str] | None = None,
    task_text: str = "",
) -> int:
    """对单条 route 计算匹配分数。

    两级匹配：
    1. path_patterns（高权重）：glob 匹配文件路径 -> +10/命中
    2. task_keywords（中权重）：关键词匹配
       - 整词出现在 task_text 中 -> +5
       - 子串匹配 task_keywords 中任一 -> +2

    参数
    ----
    route : 单条路由条目（来自 blueprint_routing.yaml routes[]）
    path_patterns : 当前改动的文件路径列表（可选）
    task_keywords : 任务关键字列表（可选）
    task_text : 任务自然语言描述全文

    返回
    ----
    整型分数，0 表示无匹配
    """
    score = 0

    route_patterns = route.get("path_patterns", []) or []

    if path_patterns:
        for pp in path_patterns:
            for rp in route_patterns:
                if fnmatch.fnmatch(pp, rp):
                    score += 10
                    break

    route_keywords = route.get("task_keywords", []) or []

    if task_keywords or task_text:
        task_lower = task_text.lower()
        kw_lower = [k.lower() for k in (task_keywords or [])]
        for rk in route_keywords:
            rk_lower = rk.lower()
            if rk_lower in task_lower:
                score += 5
                continue
            for k in kw_lower:
                if rk_lower in k or k in rk_lower:
                    score += 2
                    break

    return score


def score_and_rank_routes(
    routes: list[dict[str, Any]],
    path_patterns: list[str] | None = None,
    task_keywords: list[str] | None = None,
    task_text: str = "",
    *,
    skip_disabled: bool = True,
) -> list[tuple[int, int, dict[str, Any]]]:
    """对所有 routes 打分并排序。

    参数
    ----
    routes : 路由条目列表
    path_patterns, task_keywords, task_text : 匹配输入
    skip_disabled : 是否跳过 enabled!=True 的路由

    返回
    ----
    [(score, priority, route), ...] 按 score 降序 -> priority 降序排列
    """
    scored: list[tuple[int, int, dict[str, Any]]] = []

    for route in routes:
        if skip_disabled and not route.get("enabled", True):
            continue

        score = score_blueprint_route(route, path_patterns, task_keywords, task_text)

        if score > 0:
            priority = route.get("priority", 50)
            scored.append((score, priority, route))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return scored
