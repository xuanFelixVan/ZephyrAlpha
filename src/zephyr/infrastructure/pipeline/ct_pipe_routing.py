# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.ct_pipe_routing
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.models; zephyr.infrastructure.__init__; zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INF_ct_pipe_routing | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
CT-PIPE-ORC-001 — TaskCard → 管线入口节点路由
============================================
真源：`docs/03_modules/_master-blueprint/blueprint.md` §2.7 CT-PIPE-ORC-001

与 ``config/blueprint_routing.yaml`` 的边界：本模块输出 **Mx 入口决策**（CT-PIPE-ORC-001）；
**blueprint_routing** 仅为关键词/路径→蓝图文档索引（MOD-INF-009，供选读与 ``blueprint_search``），
**不参与** ``resolve_ct_pipe_orc001`` 的节点解析。

激活条件（满足其一即可）：
  - `TaskCard.pipeline_task_type` 非空；或
  - `tags` 中含 `ct_pipe.task_type=<TYPE>`（大小写不敏感 TYPE 值）。

可选补充（字段或等价 tag，`ct_pipe.*`）：
  - `target_layer` / `ct_pipe.layer=` / `ct_pipe.target_layer=`
  - `estimated_complexity` / `ct_pipe.complexity=`
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from zephyr.infrastructure.pipeline.models import (
    AFFINITY_CONSTRAINTS,
    M_MODULE_SPECS,
    AffinityWeight,
    PipelineRouteDecision,
)
from zephyr.shared.schema.schemas import BASE_CONFIG, Priority
from zephyr.shared.foundation.models import TaskCard

__all__ = [
    "CtPipeRoutingHints",
    "PipelineRoutingInputsError",
    "ct_pipe_hints_from_task_card",
    "enforce_affinity",
    "modules_slice_from_node",
    "resolve_ct_pipe_orc001",
]

_CT_PIPE_TAG_PREFIX = "ct_pipe."

# 蓝图决策树隐含的低层路由（foundation domains）— 对齐 SSoT: blueprint_baseline.md §CT-PIPE-ORC-001
# + target_layer_vocabulary.yaml v1.0.0 foundation_domains
# target_layer ∈ {D_MKT_DATA, D_INFRA_OPS, D_GOV_ENFORCEMENT} → M5；其余域 → M6
_FOUNDATION_LAYERS = frozenset({"D_MKT_DATA", "D_INFRA_OPS", "D_GOV_ENFORCEMENT"})

# node_id → (execution_model, sandbox_profile, gate_profile) — 对齐契约 YAML 枚举语义
_NODE_PROFILE: dict[str, tuple[str, str, str]] = {
    "M1": ("deepseek", "full", "full_g0_g7"),
    "M2": ("deepseek", "standard", "pre_commit_only"),
    "M3": ("deepseek", "audit", "post_exec_only"),
    "M4": ("deepseek", "audit", "post_exec_only"),
    "M5": ("glm", "full", "pre_commit_only"),
    "M6": ("deepseek", "standard", "full_g0_g7"),
    "M7": ("glm", "audit", "full_g0_g7"),
    "M8": ("deepseek", "audit", "full_g0_g7"),
    "M9": ("deepseek", "audit", "full_g0_g7"),
    "M10": ("deepseek", "audit", "post_exec_only"),
    "M11": ("deepseek", "restricted", "post_exec_only"),
}

_ORDER_A: tuple[str, ...] = ("M1", "M2", "M3", "M4", "M5")
_ORDER_B: tuple[str, ...] = ("M6", "M7", "M8", "M9", "M10", "M11")


class CtPipeRoutingHints(BaseModel):
    """CT-PIPE-ORC-001 路由输入（已从 TaskCard / tags 归一化）。"""

    model_config = BASE_CONFIG

    task_type: str = Field(min_length=1, description="MODEL_BUILD | AUDIT | DOC_WRITE | REFACTOR | OPS 等")
    priority_value: str = Field(default="P2", pattern=r"^P[0-3]$")
    target_layer: str | None = None
    estimated_complexity: str | None = None


class PipelineRoutingInputsError(ValueError):
    """CT-PIPE 路由输入不足以唯一决策时抛出（如 DOC_WRITE 缺 target_layer）。"""


def _tags_to_kv(tags: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in tags:
        t = raw.strip()
        if not t.startswith(_CT_PIPE_TAG_PREFIX):
            continue
        rest = t[len(_CT_PIPE_TAG_PREFIX) :]
        if "=" not in rest:
            continue
        k, _, v = rest.partition("=")
        key = k.strip().lower().replace("-", "_")
        out[key] = v.strip()
    return out


def ct_pipe_hints_from_task_card(task: TaskCard) -> CtPipeRoutingHints | None:
    """若未激活 CT-PIPE 路由则返回 None（走整链 M1 或 M6 入口的既有行为）。"""
    tag_kv = _tags_to_kv(list(task.tags))

    raw_type = (getattr(task, "pipeline_task_type", None) or "").strip()
    if not raw_type:
        raw_type = tag_kv.get("task_type", "").strip()
    if not raw_type:
        return None

    task_type = raw_type.upper().replace("-", "_")

    raw_layer = (
        (getattr(task, "target_layer", None) or "").strip() or tag_kv.get("layer") or tag_kv.get("target_layer", "")
    )
    target_layer = raw_layer.strip().upper() or None

    raw_comp = (
        (getattr(task, "estimated_complexity", None) or "").strip()
        or tag_kv.get("complexity", "").strip()
        or tag_kv.get("estimated_complexity", "").strip()
    )
    est_comp = raw_comp.upper() or None
    if not est_comp and task_type == "MODEL_BUILD" and getattr(task, "estimated_tokens", 0) >= 6000:
        est_comp = "HIGH"

    return CtPipeRoutingHints(
        task_type=task_type,
        priority_value=task.priority.value,
        target_layer=target_layer,
        estimated_complexity=est_comp,
    )


def modules_slice_from_node(node_id: str) -> tuple[Literal["A", "B"], list[str]]:
    """从入口模块起执行到该区末端（含入口）。"""
    if node_id in _ORDER_A:
        i = _ORDER_A.index(node_id)
        return "A", list(_ORDER_A[i:])
    if node_id in _ORDER_B:
        i = _ORDER_B.index(node_id)
        return "B", list(_ORDER_B[i:])
    raise ValueError(f"unknown pipeline node_id: {node_id!r}")


def _make_decision(node_id: str, rationale: str) -> PipelineRouteDecision:
    em, sb, gp = _NODE_PROFILE[node_id]
    return PipelineRouteDecision(
        node_id=node_id,
        execution_model=em,
        sandbox_profile=sb,
        gate_profile=gp,
        rationale=rationale,
    )


def resolve_ct_pipe_orc001(hints: CtPipeRoutingHints) -> PipelineRouteDecision:
    """实现 CT-PIPE-ORC-001 decision_tree（+ 契约提示中的 OPS→M2）。"""
    tt = hints.task_type.upper().replace("-", "_")
    pri = hints.priority_value.upper()
    lyr = (hints.target_layer or "").upper() or None
    comp = (hints.estimated_complexity or "").upper() or None

    if tt == "OPS":
        return _make_decision("M2", "CT-PIPE: task_type=OPS → M2")

    if tt == "MODEL_BUILD":
        is_high = comp in ("HIGH", "H", "COMPLEX")
        node = "M1" if is_high else "M2"
        return _make_decision(
            node,
            f"CT-PIPE: MODEL_BUILD + complexity={comp or 'DEFAULT_LOW'} → {node}",
        )

    if tt == "AUDIT":
        node = "M3" if pri == Priority.P0.value else "M4"
        return _make_decision(node, f"CT-PIPE: AUDIT + priority={pri} → {node}")

    if tt in ("DOC_WRITE", "REFACTOR"):
        if not lyr:
            raise PipelineRoutingInputsError(f"CT-PIPE: task_type={tt} 需要 target_layer（字段或 ct_pipe.layer=）")
        node = "M5" if lyr in _FOUNDATION_LAYERS else "M6"
        return _make_decision(node, f"CT-PIPE: {tt} + target_layer={lyr} → {node}")

    if tt in ("AUTO_FIX", "AUTOFIX"):
        return _make_decision("M11", f"CT-PIPE: task_type={tt} → M11")

    raise PipelineRoutingInputsError(f"CT-PIPE: 未支持的 task_type={tt!r}")


def enforce_affinity(
    decision: PipelineRouteDecision,
    active_nodes: dict[str, str] | None = None,
) -> list[str]:
    """校验 affinity 约束——违反 HARD 约束返回 ABORT 信息。

    遍历 AFFINITY_CONSTRAINTS，对当前决策和已激活节点进行约束检查：
      - model 约束：检查 node_a 和 node_b 的模型是否冲突
      - sandbox 约束：检查沙箱要求
      - pipeline 约束：检查管线流向

    Returns:
        警告/错误信息列表——HARD 违规以 "ABORT:" 前缀标记
    """
    warnings: list[str] = []
    active = active_nodes or {}

    for constraint in AFFINITY_CONSTRAINTS:
        if constraint.constraint_type == "model":
            node_a_model = active.get(constraint.node_a, M_MODULE_SPECS.get(constraint.node_a, {}).get("model", ""))
            if constraint.node_b:
                node_b_model = active.get(constraint.node_b, M_MODULE_SPECS.get(constraint.node_b, {}).get("model", ""))
                if node_a_model and node_b_model and node_a_model == node_b_model:
                    msg = f"ABORT: {constraint.description} ({constraint.node_a}={node_a_model}, {constraint.node_b}={node_b_model})"
                    warnings.append(msg)
                elif node_a_model and node_b_model and node_a_model != node_b_model:
                    pass
                elif constraint.weight is AffinityWeight.SOFT:
                    warnings.append(f"WARN: {constraint.description} (insufficient model info)")
            else:
                if constraint.weight is AffinityWeight.SOFT:
                    warnings.append(f"WARN: {constraint.description}")
        elif constraint.constraint_type == "sandbox":
            if constraint.node_a.startswith("M") and decision.node_id in ("M1", "M2", "M3", "M4"):
                if decision.sandbox_profile not in ("full", "standard"):
                    msg = f"ABORT: {constraint.description} (current={decision.sandbox_profile})"
                    warnings.append(msg)
        elif constraint.constraint_type == "pipeline":
            if decision.node_id not in ("M5", "M6"):
                warnings.append(f"WARN: {constraint.description} — A区→B区穿越需经M5/M6")

    return warnings
