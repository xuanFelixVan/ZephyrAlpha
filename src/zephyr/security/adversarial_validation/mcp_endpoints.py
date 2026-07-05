# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §10.2 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.mcp_endpoints
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.validator; zephyr.security.adversarial_validation.scenario_loader; zephyr.security.adversarial_validation.models; zephyr.security.adversarial_validation.convergence_checker
# [CONSUMERS] MCP Server; external AI Agents
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 4 MCP Tools: run_adversarial / list_scenarios / get_report / check_convergence; all return JSON-serializable dicts
# [MODIFY-GUARD] Adding tool MUST register in get_tools() and implement handler; tool schema per MCP Tool protocol
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] McpEndpointError on tool execution failure
# [TESTS] tests/red_blue/test_mcp_endpoints.py
# [A_module] module_id=MOD-SEC_mcp_endpoints | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from zephyr.security.adversarial_validation.convergence_checker import ConvergenceChecker
from zephyr.security.adversarial_validation.models import AttackTier, BlastRadiusLevel, RedBlueReport
from zephyr.security.adversarial_validation.scenario_loader import ScenarioLoader
from zephyr.security.adversarial_validation.validator import RedBlueValidator

logger = logging.getLogger(__name__)

__all__: list[str] = ["MCPEndpoints", "McpEndpointError", "McpTool"]


class McpEndpointError(RuntimeError):
    pass


@dataclass
class McpTool:
    name: str
    description: str
    input_schema: dict = field(default_factory=dict)


class MCPEndpoints:
    def __init__(self) -> None:
        self._convergence = ConvergenceChecker()

    def get_tools(self) -> list[McpTool]:
        return [
            McpTool(
                name="run_adversarial",
                description="Run a red-blue adversarial validation session",
                input_schema={
                    "type": "object",
                    "properties": {
                        "tier": {"type": "string", "enum": ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]},
                        "blast_radius": {"type": "string", "enum": ["FILE", "MODULE", "CROSS_MODULE", "SYSTEM"]},
                    },
                },
            ),
            McpTool(
                name="list_scenarios",
                description="List all registered adversarial attack scenarios",
            ),
            McpTool(
                name="get_report",
                description="Get the latest adversarial testing report",
            ),
            McpTool(
                name="check_convergence",
                description="Check if adversarial defense has converged",
            ),
        ]

    def handle(self, tool_name: str, arguments: dict | None = None) -> dict:
        args = arguments or {}
        try:
            if tool_name == "run_adversarial":
                return self._run_adversarial(args)
            elif tool_name == "list_scenarios":
                return self._list_scenarios(args)
            elif tool_name == "get_report":
                return self._get_report(args)
            elif tool_name == "check_convergence":
                return self._check_convergence(args)
            else:
                raise McpEndpointError(f"Unknown tool: {tool_name}")
        except Exception as e:
            logger.exception("mcp_tool_error tool=%s", tool_name)
            raise McpEndpointError(f"Tool '{tool_name}' failed: {e}") from e

    def _run_adversarial(self, args: dict) -> dict:
        validator = RedBlueValidator()
        tier = None
        if args.get("tier"):
            tier = AttackTier.from_label(args["tier"])
        radius = BlastRadiusLevel(args.get("blast_radius", "FILE"))

        report: RedBlueReport = validator.run_adversarial_session(
            session_name="mcp-session",
            tier=tier,
            blast_radius=radius,
        )
        return report.model_dump()

    def _list_scenarios(self, args: dict) -> dict:
        loader = ScenarioLoader()
        loader.load()
        scenarios = loader.list_active()
        return {
            "total": len(scenarios),
            "tier_counts": {t.value: c for t, c in loader.tier_counts().items()},
            "scenarios": [
                {"id": s.scenario_id, "name": s.name, "tier": s.tier.value, "severity": s.severity.value}
                for s in scenarios
            ],
        }

    def _get_report(self, args: dict) -> dict:
        validator = RedBlueValidator()
        report = validator.run_adversarial_session(
            session_name="mcp-report",
            tier=AttackTier.TIER_1,
        )
        return {
            "session_id": report.session_id,
            "total": report.total,
            "blocked": report.blocked,
            "bypassed": report.bypassed,
            "blocked_rate": report.blocked_rate,
            "duration_ms": report.duration_ms,
            "scenario_count": len(report.scenarios),
        }

    def _check_convergence(self, args: dict) -> dict:
        result = self._convergence.check_convergence(phase="mcp")
        return result.model_dump()
