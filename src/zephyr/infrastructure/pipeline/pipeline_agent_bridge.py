# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.pipeline_agent_bridge
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
# [A_module] module_id=MOD-INF_pipeline_agent_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Pipeline -> Agent Bridge — 双编排器桥接层
=========================================
真源：MOD-INF-009 第四轮审计 B34+B36
对标：K8s Scheduler -> kubelet 的 Pod->Container 映射

PipelineOrchestrator 路由任务到 M1-M11 节点，
AgentOrchestrator 将任务委派给 6 种 Agent 角色。
此桥接负责将 PipelineResult -> AgentOrchestrator.orchestrate()。

M->Role 映射（B36）:
  M1(parse)          -> ARCHITECT
  M2(assemble)       -> ARCHITECT
  M3(generate)       -> IMPLEMENTER
  M4(validate)       -> REVIEWER
  M5(package)        -> OPERATOR
  M6(diff)           -> REVIEWER
  M7(deep_review)    -> REVIEWER
  M8(compliance)     -> GOVERNOR
  M9(risk)           -> GOVERNOR
  M10(report)        -> REVIEWER
  M11(gating)        -> GOVERNOR

使用:
    from zephyr.infrastructure.pipeline.pipeline_agent_bridge import PipelineAgentBridge
    bridge = PipelineAgentBridge(agent_orchestrator)
    orchestration_results = bridge.bridge(pipeline_result)
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

from zephyr.infrastructure.pipeline.models import M_MODULE_SPECS, ModuleResult, PipelineResult

_mod = importlib.import_module("zephyr.orchestrator.agent_orchestrator")
AgentOrchestrator = _mod.AgentOrchestrator
AgentRole = _mod.AgentRole
OrchestrationResult = _mod.OrchestrationResult
RoutingStrategy = _mod.RoutingStrategy

__all__ = [
    "M_TO_ROLE",
    "PipelineAgentBridge",
    "domain_for_pipeline",
    "role_for_module",
]

_logger = logging.getLogger(__name__)

M_TO_ROLE: dict[str, str] = {
    "M1": "architect",
    "M2": "architect",
    "M3": "implementer",
    "M4": "reviewer",
    "M5": "operator",
    "M6": "reviewer",
    "M7": "reviewer",
    "M8": "governor",
    "M9": "governor",
    "M10": "reviewer",
    "M11": "governor",
}

_ROLE_TO_DOMAIN: dict[str, str] = {
    "architect": "D0",
    "implementer": "D1",
    "reviewer": "D2",
    "governor": "D3",
    "researcher": "D4",
    "operator": "D5",
}

_PIPELINE_TO_DOMAIN: dict[str, str] = {
    "A": "D1",
    "B": "D2",
    "C": "D3",
}


def role_for_module(module_id: str) -> str:
    """返回 Mx 节点绑定的 Agent Role 名。"""
    return M_TO_ROLE.get(module_id, "implementer")


def domain_for_pipeline(pipeline: str) -> str:
    """返回管线对应的域 D0-D9。"""
    return _PIPELINE_TO_DOMAIN.get(pipeline.upper(), "D1")


def _build_directive_chain(module_id: str) -> str:
    """从 module_id 构建 MCP directive 链。"""
    spec = M_MODULE_SPECS.get(module_id, {})
    role = spec.get("role", "")
    directives: list[str] = []

    if module_id == "M1":
        directives = ["blueprint_lookup", "parse", "plan"]
    elif module_id == "M2":
        directives = ["context_assembly", "context_validate"]
    elif module_id == "M3":
        directives = ["code_generate", "doc_generate"]
    elif module_id == "M4":
        directives = ["format_validate", "lint"]
    elif module_id == "M5":
        directives = ["package", "artifact_collect"]
    elif module_id == "M6":
        directives = ["diff_detect", "baseline_compare"]
    elif module_id == "M7":
        directives = ["deep_review", "logic_audit", "compliance_check"]
    elif module_id == "M8":
        directives = ["standard_compliance", "ps_gov_adr_check"]
    elif module_id == "M9":
        directives = ["risk_assessment", "owasp_top10"]
    elif module_id == "M10":
        directives = ["audit_report", "finding_format"]
    elif module_id == "M11":
        directives = ["gating_decision", "g5_g6_verify"]

    return "+".join(directives) if directives else "default"


class PipelineAgentBridge:
    """Pipeline -> Agent 编排器桥接。

    Parameters
    ----------
    agent_orchestrator : AgentOrchestrator
        已构造的 AgentOrchestrator 实例。
    """

    def __init__(self, agent_orchestrator: AgentOrchestrator) -> None:
        self._agent_orc = agent_orchestrator

    @property
    def agent_orchestrator(self) -> AgentOrchestrator:
        return self._agent_orc

    def bridge(
        self,
        pipeline_result: PipelineResult,
        *,
        task_context: dict[str, Any] | None = None,
        token_budget: int | None = None,
    ) -> dict[str, Any]:
        """将 PipelineResult 中每个模块的执行结果桥接到 AgentOrchestrator。

        对每个 ModuleResult:
          1. 解析 M->Role 映射
          2. 构建 directive chain
          3. 调用 agent_orc.orchestrate()
          4. 收集 OrchestrationResult

        Returns
        -------
        dict
            {
                "pipeline_task_id": str,
                "pipeline_result": PipelineResult,
                "module_bridges": [
                    {
                        "module_id": str,
                        "role": str,
                        "domain": str,
                        "directive_chain": str,
                        "orchestration": OrchestrationResult | None,
                    },
                    ...
                ],
            }
        """
        bridge_results: list[dict[str, Any]] = []

        for mr in pipeline_result.modules_executed:
            role_name = role_for_module(mr.module_id)
            domain = domain_for_pipeline(mr.pipeline)
            directive_chain = _build_directive_chain(mr.module_id)

            _mod = importlib.import_module("zephyr.orchestrator.agent_orchestrator")
            AgentRole = _mod.AgentRole

            required = AgentRole(role_name.upper()) if role_name.upper() in AgentRole.__members__ else None

            orch_result: Any = None
            try:
                orch_result = self._agent_orc.orchestrate(
                    domain=domain,
                    directive_chain=directive_chain,
                    claim=str(mr.output.get("summary", "")),
                    context=task_context or {},
                    strategy="capability_match",
                    required_role=required,
                    token_used=mr.tokens_used,
                    token_budget=token_budget,
                    task_id=f"{pipeline_result.task_id}:{mr.module_id}",
                )
            except Exception:
                _logger.exception(
                    "PipelineAgentBridge: orchestrate failed for %s/%s",
                    pipeline_result.task_id,
                    mr.module_id,
                )

            bridge_results.append(
                {
                    "module_id": mr.module_id,
                    "role": role_name,
                    "domain": domain,
                    "directive_chain": directive_chain,
                    "orchestration": orch_result,
                }
            )

        return {
            "pipeline_task_id": pipeline_result.task_id,
            "pipeline_result": pipeline_result,
            "module_bridges": bridge_results,
        }

    def bridge_module(
        self,
        module_result: ModuleResult,
        *,
        task_context: dict[str, Any] | None = None,
        token_budget: int | None = None,
        task_id_prefix: str = "",
    ) -> object:
        role_name = role_for_module(module_result.module_id)
        domain = domain_for_pipeline(module_result.pipeline)
        directive_chain = _build_directive_chain(module_result.module_id)

        _mod = importlib.import_module("zephyr.orchestrator.agent_orchestrator")
        AgentRole = _mod.AgentRole

        required = AgentRole(role_name.upper()) if role_name.upper() in AgentRole.__members__ else None

        task_id = f"{task_id_prefix}:{module_result.module_id}" if task_id_prefix else module_result.module_id

        return self._agent_orc.orchestrate(
            domain=domain,
            directive_chain=directive_chain,
            claim=str(module_result.output.get("summary", "")),
            context=task_context or {},
            strategy="capability_match",
            required_role=required,
            token_used=module_result.tokens_used,
            token_budget=token_budget,
            task_id=task_id,
        )
