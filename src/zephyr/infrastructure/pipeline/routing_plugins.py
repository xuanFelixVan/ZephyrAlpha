# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.routing_plugins
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_routing_plugins | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Pipeline Routing Plugin System — K8s Scheduling Framework 对标
=============================================================
真源：MOD-INF-009 §3 路由决策树 + K8s Scheduler Plugin Architecture
关联：GOV-AI-002 v2.0.0 模型路由策略

插件生命周期：
  Filter 阶段 → 淘汰不合格节点（Predicates）
  Score 阶段  → 给剩余节点打分（Priorities）
  Bind 阶段   → 选最高分 + 生成 PipelineRouteDecision

使用：
    from zephyr.infrastructure.pipeline.routing_plugins import PipelineRouter, DEFAULT_PLUGINS
    router = PipelineRouter()
    decision = router.route(hints)

扩展（AI 自治）：
    from zephyr.infrastructure.pipeline.routing_plugins import RoutingPlugin, RoutingContext
    class MyPlugin(RoutingPlugin):
        name = "my_filter"
        phase = "filter"
        priority = 60
        def apply(self, ctx: RoutingContext) -> None: ...
    router = PipelineRouter([MyPlugin(), *DEFAULT_PLUGINS])
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from zephyr.infrastructure.pipeline.ct_pipe_routing import CtPipeRoutingHints, _make_decision
from zephyr.infrastructure.pipeline.models import M_MODULE_SPECS, M_MODULES, PipelineRouteDecision

__all__ = [
    "DEFAULT_PLUGINS",
    "ComplexityFilter",
    "CostScorer",
    "NoEligibleNodeError",
    "PipelineAffinityScorer",
    "PipelineRouter",
    "PriorityScorer",
    "RoutingContext",
    "RoutingPlugin",
    "TaskTypeFilter",
]

# 对齐 SSoT: blueprint_baseline.md §CT-PIPE-ORC-001 + target_layer_vocabulary.yaml v1.0.0
# foundation_domains（D_MKT_DATA/D_INFRA_OPS/D_GOV_ENFORCEMENT → M5）
_FOUNDATION_LAYERS = frozenset({"D_MKT_DATA", "D_INFRA_OPS", "D_GOV_ENFORCEMENT"})

_NODE_TASK_TYPE_MAP: dict[str, frozenset[str]] = {
    "M1": frozenset({"MODEL_BUILD"}),
    "M2": frozenset({"MODEL_BUILD", "DOC_WRITE", "REFACTOR", "OPS"}),
    "M3": frozenset({"AUDIT"}),
    "M4": frozenset({"AUDIT"}),
    "M5": frozenset({"DOC_WRITE", "REFACTOR"}),
    "M6": frozenset({"DOC_WRITE", "REFACTOR", "AUDIT"}),
    "M7": frozenset({"DOC_WRITE", "REFACTOR", "AUDIT"}),
    "M8": frozenset({"DOC_WRITE", "REFACTOR", "AUDIT"}),
    "M9": frozenset({"DOC_WRITE", "REFACTOR", "AUDIT"}),
    "M10": frozenset({"DOC_WRITE", "REFACTOR", "AUDIT"}),
    "M11": frozenset({"AUTO_FIX", "AUTOFIX"}),
}

_NODE_COMPLEXITY_MAP: dict[str, frozenset[str]] = {
    "M1": frozenset({"HIGH", "H", "COMPLEX"}),
}

_MODEL_COST_MAP: dict[str, float] = {
    "deepseek": 2.61,
    "glm": 0.0,
    "claude": 15.0,
}


class RoutingContext:
    """插件间共享的可变路由上下文。

    Filter 阶段：插件从 `candidates` 中移除不合格节点。
    Score 阶段：插件向 `scores` 累加分数。
    """

    def __init__(self, hints: CtPipeRoutingHints) -> None:
        self.hints = hints
        self.candidates: list[str] = list(M_MODULES)
        self.scores: dict[str, float] = {m: 0.0 for m in M_MODULES}
        self.rejections: dict[str, str] = {}


class NoEligibleNodeError(ValueError):
    """所有候选节点均被 Filter 阶段淘汰。"""


class RoutingPlugin(ABC):
    """Pipeline 路由插件基类——对标 K8s Scheduling Framework Plugin。

    子类 MUST 定义：
      - name: ClassVar[str]  —— 插件唯一标识
      - phase: ClassVar[str] —— "filter" | "score"
      - priority: ClassVar[int] —— 执行顺序（越小越先，默认 50）

    Filter 插件：实现 `apply(ctx)` → 从 ctx.candidates 中移除不合格节点。
    Score 插件：实现 `apply(ctx)` → 向 ctx.scores 累加分数。
    """

    name: ClassVar[str]
    phase: ClassVar[str]
    priority: ClassVar[int] = 50

    @abstractmethod
    def apply(self, ctx: RoutingContext) -> None:
        """执行插件逻辑——直接修改 ctx。"""
        ...


class TaskTypeFilter(RoutingPlugin):
    """过滤：节点的 task_type 白名单不匹配 → 淘汰。"""

    name: ClassVar[str] = "task_type_filter"
    phase: ClassVar[str] = "filter"
    priority: ClassVar[int] = 10

    def apply(self, ctx: RoutingContext) -> None:
        tt = ctx.hints.task_type.upper().replace("-", "_")
        kept: list[str] = []
        for node in ctx.candidates:
            allowed = _NODE_TASK_TYPE_MAP.get(node, frozenset())
            if tt in allowed:
                kept.append(node)
            else:
                ctx.rejections[node] = f"task_type={tt} not in {sorted(allowed)}"
        ctx.candidates = kept


class ComplexityFilter(RoutingPlugin):
    """过滤：高复杂度任务只能选支持高复杂度的节点。"""

    name: ClassVar[str] = "complexity_filter"
    phase: ClassVar[str] = "filter"
    priority: ClassVar[int] = 20

    def apply(self, ctx: RoutingContext) -> None:
        comp = (ctx.hints.estimated_complexity or "").upper()
        if comp not in ("HIGH", "H", "COMPLEX"):
            return

        kept: list[str] = []
        for node in ctx.candidates:
            allowed = _NODE_COMPLEXITY_MAP.get(node, frozenset())
            if comp in allowed:
                kept.append(node)
            else:
                ctx.rejections[node] = f"complexity={comp} requires high-capability node"
        ctx.candidates = kept


class LayerFilter(RoutingPlugin):
    """过滤：DOC_WRITE/REFACTOR 按 target_layer 限定节点范围。"""

    name: ClassVar[str] = "layer_filter"
    phase: ClassVar[str] = "filter"
    priority: ClassVar[int] = 15

    def apply(self, ctx: RoutingContext) -> None:
        tt = ctx.hints.task_type.upper().replace("-", "_")
        if tt not in ("DOC_WRITE", "REFACTOR"):
            return

        lyr = (ctx.hints.target_layer or "").upper()
        if not lyr:
            return

        if lyr in _FOUNDATION_LAYERS:
            kept: list[str] = []
            for node in ctx.candidates:
                if node in ("M5",):
                    kept.append(node)
            if kept:
                ctx.candidates = kept

        elif len(ctx.candidates) > 1 and "M5" in ctx.candidates:
            ctx.candidates = [n for n in ctx.candidates if n != "M5"]


class PriorityScorer(RoutingPlugin):
    """打分：任务优先级越高 → 高分节点获得的加成越多。

    P0 AUDIT → M3(opus级审计) 得高分；P2 MODEL_BUILD → M2(标准) 得高分。
    """

    name: ClassVar[str] = "priority_scorer"
    phase: ClassVar[str] = "score"
    priority: ClassVar[int] = 10

    def apply(self, ctx: RoutingContext) -> None:
        pri = ctx.hints.priority_value.upper()
        tt = ctx.hints.task_type.upper().replace("-", "_")
        pri_weights = {"P0": 40, "P1": 25, "P2": 10, "P3": 0}

        for node in ctx.candidates:
            weight = pri_weights.get(pri, 10)
            if tt == "AUDIT" and pri == "P0" and node == "M3":
                ctx.scores[node] += weight + 30
            elif tt == "MODEL_BUILD" and node == "M2":
                ctx.scores[node] += weight
            elif node == "M6":
                ctx.scores[node] += weight * 0.5


class PipelineAffinityScorer(RoutingPlugin):
    """打分：A区任务偏好A区节点，B区任务偏好B区节点。"""

    name: ClassVar[str] = "pipeline_affinity_scorer"
    phase: ClassVar[str] = "score"
    priority: ClassVar[int] = 20

    def apply(self, ctx: RoutingContext) -> None:
        tt = ctx.hints.task_type.upper().replace("-", "_")
        a_tasks = frozenset({"MODEL_BUILD", "OPS"})
        b_entry_tasks = frozenset({"AUDIT", "DOC_WRITE", "REFACTOR"})

        for node in ctx.candidates:
            spec = M_MODULE_SPECS.get(node, {})
            pipeline = spec.get("pipeline", "")
            if tt in a_tasks and pipeline == "A":
                ctx.scores[node] += 15
            elif tt in b_entry_tasks and pipeline == "B":
                ctx.scores[node] += 10


class CostScorer(RoutingPlugin):
    """打分：便宜模型得分更高——同等条件下优先选 DeepSeek/GLM。

    不阻断高成本节点，仅降低其排序。
    """

    name: ClassVar[str] = "cost_scorer"
    phase: ClassVar[str] = "score"
    priority: ClassVar[int] = 30

    def apply(self, ctx: RoutingContext) -> None:
        for node in ctx.candidates:
            spec = M_MODULE_SPECS.get(node, {})
            model = spec.get("model", "unknown")
            cost = _MODEL_COST_MAP.get(model, 5.0)
            ctx.scores[node] += max(0, 20 - cost * 2)


DEFAULT_PLUGINS: list[RoutingPlugin] = [
    TaskTypeFilter(),
    ComplexityFilter(),
    LayerFilter(),
    PriorityScorer(),
    PipelineAffinityScorer(),
    CostScorer(),
]


class PipelineRouter:
    """Pipeline 路由引擎——Filter→Score→Bind 三阶段。

    Parameters
    ----------
    plugins : list[RoutingPlugin] | None
        插件列表。None 时使用 DEFAULT_PLUGINS。
    """

    def __init__(self, plugins: list[RoutingPlugin] | None = None) -> None:
        all_plugins = plugins if plugins is not None else DEFAULT_PLUGINS
        sorted_plugins = sorted(all_plugins, key=lambda p: p.priority)
        self._filters = [p for p in sorted_plugins if p.phase == "filter"]
        self._scorers = [p for p in sorted_plugins if p.phase == "score"]

    def route(self, hints: CtPipeRoutingHints) -> PipelineRouteDecision:
        ctx = RoutingContext(hints)

        for f in self._filters:
            f.apply(ctx)
            if not ctx.candidates:
                rejections = "; ".join(f"{n}:{r}" for n, r in sorted(ctx.rejections.items()))
                raise NoEligibleNodeError(f"No eligible node for task_type={hints.task_type}: {rejections}")

        for s in self._scorers:
            s.apply(ctx)

        scored = [(ctx.scores[n], n) for n in ctx.candidates]
        scored.sort(reverse=True)
        best_score, best_node = scored[0]

        detail = ", ".join(f"{n}={ctx.scores[n]:.0f}" for _, n in scored[:3])
        return _make_decision(
            best_node,
            f"Filter→{len(ctx.candidates)} nodes; Score→{best_node}={best_score:.0f} [{detail}]",
        )
