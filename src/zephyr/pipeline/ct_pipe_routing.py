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

from zephyr.core.models import TaskCard
from zephyr.pipeline.models import PipelineRouteDecision
from zephyr.shared.schemas import BASE_CONFIG

__all__ = [
    "CtPipeRoutingHints",
    "PipelineRoutingInputsError",
    "ct_pipe_hints_from_task_card",
    "modules_slice_from_node",
    "resolve_ct_pipe_orc001",
]

_CT_PIPE_TAG_PREFIX = "ct_pipe."

# 蓝图决策树隐含的低层路由（foundation layers）
_FOUNDATION_LAYERS = frozenset({"L00", "L01", "L10"})

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

    raw_layer = (getattr(task, "target_layer", None) or "").strip() or tag_kv.get("layer") or tag_kv.get(
        "target_layer", ""
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
        node = "M3" if pri == "P0" else "M4"
        return _make_decision(node, f"CT-PIPE: AUDIT + priority={pri} → {node}")

    if tt in ("DOC_WRITE", "REFACTOR"):
        if not lyr:
            raise PipelineRoutingInputsError(
                f"CT-PIPE: task_type={tt} 需要 target_layer（字段或 ct_pipe.layer=）"
            )
        node = "M5" if lyr in _FOUNDATION_LAYERS else "M6"
        return _make_decision(node, f"CT-PIPE: {tt} + target_layer={lyr} → {node}")

    if tt in ("AUTO_FIX", "AUTOFIX"):
        return _make_decision("M11", f"CT-PIPE: task_type={tt} → M11")

    raise PipelineRoutingInputsError(f"CT-PIPE: 未支持的 task_type={tt!r}")
