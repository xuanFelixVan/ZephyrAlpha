# [BLUEPRINT] MOD-EXE-AGENTS | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/14_execution_layer.md | §4-S1.1
# [MODULE] zephyr.autonomy_core.agents._s11_wiring
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.agents._run_store ; zephyr.intelligence.model_routing.cascade_orchestrator（11号文，只消费 route 签名）; zephyr.autonomy_core.module_factory.knowledge_classifier + module_mapper（13号文，只消费）; zephyr.intelligence.reflexion.reflctrl_gate + roles + reflection_schema（12号文，只消费）
# [CONSUMERS] zephyr.autonomy_core.agents.algorithm_agent_entry ; self_iteration_agent_entry（懒加载薄委派）; tests/autonomy/test_execution_layer_s11_wiring.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只做消费与串联（11/12/13号文模块源文件零改动）；全部真源经注入缝传入（默认 None 由入口走既有行为，reflection_review 无既有行为故默认缝=真闸门+合成三角色+真 ReflectionStore 落 runtime 下）；产出 100% human_gated 落盘；工单载荷非法 fail-closed 产 error 留痕不抛
# [MODIFY-GUARD] Owner approval required; 变更须同步 14号文 §4-S1.1 验收口径
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 模块映射载荷非法（pydantic/ModuleMapperError）→ status=error 裁决留痕不抛；ReflectionRequest 非法 layer/level → ValueError 上抛（fail-closed 先于落盘）；反思闸门拒绝 → denied_by_reflctrl 留痕不反思
# [TESTS] tests/autonomy/test_execution_layer_s11_wiring.py
# [A_module] module_id=MOD-EXE-AGENTS | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""S1.1 接口接线件（14号文 §4-S1.1）：四入口消费 11/12/13号文正式接口的适配层.

- route_experiment_model：算法实验工单 → 11号文 CascadeOrchestrator.route 裁决
  "实验该用哪个模型"（task_type/complexity/period/required_capabilities 从工单映射，
  complexity 字符串→TaskComplexity 枚举非法归 MODERATE，对齐 runtime_assembly 先例）。
- map_module_generation：新模块生成类工单 → 13号文 ModuleMapper.map_knowledge
  四选一裁决（new_entry/variant_of/reject_duplicate/combination）留痕进产出。
- run_reflection_review：迭代评审工单 → 12号文 ReflCtrlGate.decide 频率闸门先行
  （拒则 denied 留痕不反思），放行才走 run_three_role_flow/L1 反思，ReflectionRecord
  落 ReflectionStore（默认落 <runtime>/reflections/，闸门留痕落 <runtime>/reflctrl/）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

from zephyr.autonomy_core.agents._run_store import AgentRunStore
from zephyr.autonomy_core.module_factory.knowledge_classifier import (
    ClassificationPayload,
    ClassificationResult,
    KnowledgeItem,
)
from zephyr.autonomy_core.module_factory.module_mapper import ModuleMapperError
from zephyr.governance.intelligence_governance.model_router import TaskComplexity
from zephyr.intelligence.reflexion.reflctrl_gate import ReflCtrlGate, ReflectionRequest
from zephyr.intelligence.reflexion.reflection_schema import ReflectionStore
from zephyr.intelligence.reflexion.roles import (
    L1SelfReflection,
    RubricEvaluator,
    SyntheticActor,
    TaskSpec,
    run_three_role_flow,
)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
_COMPLEXITY: Final[dict[str, TaskComplexity]] = {
    c.value: c for c in (TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX)
}


def route_experiment_model(ticket: dict[str, Any], cascade_router: Any) -> dict[str, Any]:
    """实验工单 → cascade 模型选择裁决留痕（无候选不调路由，标 skipped）."""
    task_type = str(ticket.get("model_task_type") or ticket.get("experiment_type") or "model_evaluation")
    candidates = [str(c) for c in (ticket.get("model_candidates") or []) if str(c).strip()]
    if not candidates:
        return {"kind": "model_routing_decision", "status": "skipped_no_candidates",
                "task_type": task_type, "note": "工单未给 model_candidates，不调级联（空候选 fail-closed）"}
    complexity = _COMPLEXITY.get(str(ticket.get("complexity") or "moderate").lower(),
                                 TaskComplexity.MODERATE)
    decision = cascade_router.route(
        task_type,
        candidates,
        complexity=complexity,
        period=str(ticket["period"]) if ticket.get("period") else None,
        required_capabilities=[str(x) for x in ticket["required_capabilities"]]
        if ticket.get("required_capabilities") else None,
    )
    payload = decision.to_dict() if hasattr(decision, "to_dict") else dict(decision)
    return {"kind": "model_routing_decision", "status": "routed", "task_type": task_type,
            "candidates": candidates, "decision": payload}


def map_module_generation(ticket: dict[str, Any], module_mapper: Any) -> dict[str, Any]:
    """新模块生成工单 → ModuleMapper 四选一裁决留痕（载荷非法 fail-closed 不抛）."""
    try:
        knowledge = ticket.get("knowledge") or {}
        item = KnowledgeItem(
            knowledge_id=str(knowledge.get("knowledge_id") or ticket.get("ticket_id") or ""),
            title=str(knowledge.get("title") or ""),
            content=str(knowledge.get("content") or ""),
            source_ref=str(knowledge.get("source_ref") or ""),
        )
        payload = ClassificationPayload(**(ticket.get("classification") or {}))
        classification = ClassificationResult(
            verdict="classified", knowledge_id=item.knowledge_id, classification=payload,
        )
        spec = module_mapper.map_knowledge(item, classification,
                                           schema_plan=ticket.get("schema_plan"))
    except (ValueError, TypeError, AttributeError, ModuleMapperError) as exc:
        return {"kind": "module_mapping_spec", "status": "error", "verdict": "error",
                "rationale": f"工单载荷非法/映射失败（fail-closed）: {type(exc).__name__}: {exc}",
                "human_gate_required": True}
    return {
        "kind": "module_mapping_spec", "status": "mapped",
        "verdict": str(spec.verdict), "target_registry": str(spec.target_registry),
        "rationale": str(spec.rationale), "retrieval_channel": str(spec.retrieval_channel),
        "degraded": bool(spec.degraded),
        "candidates": [{"entry_id": c.entry_id, "registry": c.registry,
                        "score": c.score, "retired": c.retired} for c in spec.candidates],
        "draft_notes": [str(n) for n in spec.draft_notes],
        "human_gate_required": bool(spec.human_gate_required),
    }


def _default_flow(task: TaskSpec) -> Any:
    return run_three_role_flow(task, SyntheticActor(), RubricEvaluator(), L1SelfReflection())


def _reflection_request(ticket: dict[str, Any], ticket_id: str) -> ReflectionRequest:
    """工单字段 → ReflectionRequest（非法 layer/level 由 schema 层 ValueError fail-closed）."""
    return ReflectionRequest(
        task_id=str(ticket.get("task_id") or ticket_id),
        layer=str(ticket.get("layer") or "execution"),
        requested_level=str(ticket.get("requested_level") or "L1"),
        deviation_pct=float(ticket.get("deviation_pct") or 0.0),
        risk_vetoed=bool(ticket.get("risk_vetoed") or False),
        outcome=str(ticket.get("outcome") or ""),
        signal_sigma_deviation=float(ticket.get("signal_sigma_deviation") or 0.0),
        slippage_ratio=float(ticket.get("slippage_ratio") or 0.0),
        risk_param_deviation_pct=float(ticket.get("risk_param_deviation_pct") or 0.0),
        regime_transition_prob_pct=float(ticket.get("regime_transition_prob_pct") or 0.0),
        regime_triggered=bool(ticket.get("regime_triggered") or False),
        eval_confidence=float(ticket.get("eval_confidence", 1.0)),
        similar_task_count=int(ticket.get("similar_task_count") or 0),
        excellent_streak=int(ticket.get("excellent_streak") or 0),
        normal_streak=int(ticket.get("normal_streak") or 0),
        severity=str(ticket.get("severity") or ""),
        reflection_round=int(ticket.get("reflection_round") or 0),
        estimated_tokens=int(ticket.get("estimated_tokens") or 0),
    )


def run_reflection_review(
    ticket: dict[str, Any],
    *,
    role: str,
    runtime_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    refl_gate: Any | None = None,
    flow_runner: Any | None = None,
    reflection_store: Any | None = None,
) -> dict[str, Any]:
    """reflection_review 工单：ReflCtrlGate 闸门 → 三角色/L1 反思 → ReflectionStore.

    注入缝：refl_gate（默认真 ReflCtrlGate，stats 落 <runtime>/reflctrl/）、
    flow_runner（默认合成三角色 run_three_role_flow）、reflection_store
    （默认真 ReflectionStore，落 <runtime>/reflections/）。闸门拒则 denied 留痕不反思。
    """
    ticket_id = str(ticket.get("ticket_id") or "").strip()
    if not ticket_id:
        raise ValueError("reflection_review 工单缺 ticket_id")
    request = _reflection_request(ticket, ticket_id)  # 先校验后落盘（fail-closed 不留半成品）
    root = Path(repo_root) if repo_root else _REPO_ROOT
    runtime_base = Path(runtime_dir) if runtime_dir else root / ".runtime"
    store = AgentRunStore(role, runtime_dir=runtime_base, repo_root=root)
    store.begin(ticket_id, ticket)

    gate = refl_gate or ReflCtrlGate(stats_root=runtime_base / "reflctrl")
    decision = gate.decide(request)
    gate_record = {
        "kind": "reflctrl_gate_decision", "task_id": request.task_id,
        "layer": request.layer, "requested_level": request.requested_level,
        "allowed": bool(decision.allowed),
        "matched_rules": list(decision.matched_rules),
        "granted_levels": list(decision.granted_levels),
        "denied_by": decision.denied_by,
    }
    store.write_output("reflection_gate.json", gate_record, ticket_id)
    if not decision.allowed:
        report = {"kind": "reflection_review", "status": "denied_by_reflctrl",
                  "advice_only": True, "gate": gate_record,
                  "note": "频率闸门拒绝：本次不反思（12号文 §3.4 显式规则外不烧 token）"}
        store.write_output("reflection_review.json", report, ticket_id)
        store.finish(ticket_id, "denied_by_reflctrl", {"denied_by": decision.denied_by})
        return report

    task = TaskSpec(task_id=request.task_id,
                    description=str(ticket.get("task_description") or ticket_id),
                    params=dict(ticket.get("params") or {}))
    trajectory, evaluation, record = (flow_runner or _default_flow)(task)
    refl_store = reflection_store or ReflectionStore(root=runtime_base / "reflections")
    refl_store.append(record)
    record_payload = record.to_dict() if hasattr(record, "to_dict") else dict(record)
    store.write_output("reflection_evaluation.json", {
        "kind": "reflection_evaluation", "task_id": request.task_id,
        "trajectory_succeeded": bool(trajectory.succeeded),
        "score": float(evaluation.score), "dimensions": dict(evaluation.dimensions),
        "defects": list(evaluation.defects),
    }, ticket_id)
    store.write_output("reflection_record.json", {
        "kind": "reflection_record", "store_path": Path(refl_store.path).as_posix(),
        "granted_levels": list(decision.granted_levels), "record": record_payload,
    }, ticket_id)
    report = {"kind": "reflection_review", "status": "completed", "advice_only": True,
              "gate": gate_record, "reflection_id": record_payload.get("reflection_id"),
              "outcome": record_payload.get("outcome")}
    store.write_output("reflection_review.json", report, ticket_id)
    store.finish(ticket_id, "completed", {"granted_levels": list(decision.granted_levels),
                                          "outcome": record_payload.get("outcome")})
    return report


__all__ = ["map_module_generation", "route_experiment_model", "run_reflection_review"]
