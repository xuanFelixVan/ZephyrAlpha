# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §10.2 + §16 Phase 2c
# [MODULE] zephyr.security.adversarial_validation.mcp_endpoints
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.validator; zephyr.security.adversarial_validation.scenario_loader; zephyr.security.adversarial_validation.models; zephyr.security.adversarial_validation.convergence_checker
# [CONSUMERS] MCP Server; external AI Agents
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 4 MCP Tools: run_adversarial / list_scenarios / get_report / check_convergence; all return JSON-serializable dicts
# [MODIFY-GUARD] Adding tool MUST register in get_tools() and implement handler; tool schema per MCP Tool protocol
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] McpEndpointError on tool execution failure
# [TESTS] tests/red_blue/test_mcp_endpoints.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: mcp_endpoints.py
# 层: 算法
# - id: A1
#   name_zh: ① MCPEndpoints
#   name_en: MCPEndpoints
#   intro: class MCPEndpoints 源码 L80-L173
#   desc: 公共方法（定义序）: get_tools, handle；源码 L80-L173
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: MCPEndpoints
#   downstream: MCP Server; external AI Agents
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
    error_code = "ZA-SC-0003"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.exception("mcp_tool_error tool=%s", tool_name, exc_info=True)
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
