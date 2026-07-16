# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.gateway
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.protocol; zephyr.security.llm_defense.llm_security.layers.l0_supply_chain; zephyr.security.llm_defense.llm_security.layers.l1_input; zephyr.security.llm_defense.llm_security.layers.l2_prompt_protection; zephyr.security.llm_defense.llm_security.layers.l2a_process_sandbox; zephyr.security.llm_defense.llm_security.layers.l3_output; zephyr.security.llm_defense.llm_security.layers.l4_agent; zephyr.security.llm_defense.llm_security.layers.l5_resource_protection; zephyr.security.llm_defense.llm_security.layers.l6_observability; zephyr.security.llm_defense.llm_security.self_protection.l7_validation; zephyr.security.llm_defense.llm_security.layers.l8_multi_agent
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=human_gated
# [TTL] permanent

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from zephyr.security.llm_defense.llm_security.layers.l0_supply_chain import SupplyChainGuard
from zephyr.security.llm_defense.llm_security.layers.l1_input import InputDefenseLayer
from zephyr.security.llm_defense.llm_security.layers.l2_prompt_protection import PromptProtectionLayer
from zephyr.security.llm_defense.llm_security.layers.l2a_process_sandbox import ProcessSandboxLayer
from zephyr.security.llm_defense.llm_security.layers.l3_output import OutputSecurityLayer
from zephyr.security.llm_defense.llm_security.layers.l4_agent import AgentSecurityLayer
from zephyr.security.llm_defense.llm_security.layers.l5_resource_protection import ResourceProtectionLayer
from zephyr.security.llm_defense.llm_security.layers.l6_observability import ObservabilityLayer
from zephyr.security.llm_defense.llm_security.layers.l8_multi_agent import MultiAgentSecurityLayer
from zephyr.security.llm_defense.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)
from zephyr.security.llm_defense.llm_security.runtime_interceptor import grant_allowance as _grant_runtime_allowance
from zephyr.security.llm_defense.llm_security.self_protection.l7_validation import ValidationLayer


class ScanMode(str, Enum):
    FULL = "full"
    INPUT_ONLY = "input_only"
    OUTPUT_ONLY = "output_only"
    AGENT_ONLY = "agent_only"


@dataclass
class ScanResult:
    decision: SecurityDecision
    mode: ScanMode
    layers_evaluated: int
    layers_passed: int
    layers_denied: int
    layers_flagged: int
    total_score: float
    elapsed_ms: float
    layer_results: dict[str, SecurityResult] = field(default_factory=dict)
    blocked_by: str = ""
    sanitized_input: str = ""
    sanitized_output: str = ""


def _classify_layer_decision(name, result, fail_open_layers):
    if result.decision is SecurityDecision.DENY:
        if name not in fail_open_layers:
            return ("deny", True, SecurityDecision.DENY)
        return ("deny", False, None)
    elif result.decision is SecurityDecision.BLOCK:
        if name not in fail_open_layers:
            return ("deny", True, SecurityDecision.BLOCK)
        return ("deny", False, None)
    elif result.decision is SecurityDecision.FLAG:
        return ("flag", False, None)
    else:
        return ("pass", False, None)


def _maybe_grant_runtime_allowance(final_decision, mode, request_id):
    # 运行时 Gate 放行令牌：仅对“预调用”扫描（输入/全量/Agent 动作）且 ALLOW 时颁发。
    # scan_output（OUTPUT_ONLY）不颁发——输出扫描发生在 LLM 调用之后，不应放行后续裸调。
    # 令牌 TTL 30s，使合法的“LSG 扫描通过 -> 发起 LLM 调用”链路畅通（见 runtime_interceptor）。
    if final_decision is SecurityDecision.ALLOW and mode in (
        ScanMode.INPUT_ONLY,
        ScanMode.FULL,
        ScanMode.AGENT_ONLY,
    ):
        try:
            _grant_runtime_allowance(request_id=request_id)
        except Exception:
            # 颁发失败绝不影响 LSG 主流程——最坏情况是合法调用被运行时 Gate 拦
            # （此时业务侧会收到 BareLLMCallError，需检查 runtime_interceptor 状态）
            pass


class LSGSecurityGateway:
    """LLM Security Gateway — L0-L8 九层纵深防御统一编排入口.

    原则：fail-closed —— 任一层 DENY -> 整体 DENY，LSG 不可用 -> 拒绝所有流量.
    L6/L7 为 pass-through 层（fail-open 降级例外）.

    执行语义：严格顺序链式执行 L0->L1->...->L8，任一非 fail-open 层 DENY/BLOCK
    立即中断后续层的评估。这是纵深防御的核心安全语义，不可并行化。

    用法:
        gw = LSGSecurityGateway()
        result = await gw.scan_input("user prompt text", metadata={...})
        if result.decision is SecurityDecision.DENY:
            # 拒绝该请求
    """

    FAIL_OPEN_LAYERS = {"l6_observability", "l7_validation"}

    def __init__(
        self,
        model_digest_registry: dict[str, str] | None = None,
        rules_file_baselines: dict[str, str] | None = None,
        project_root: str | None = None,
        max_tokens: int = 100000,
        max_cost_cents: float = 500.0,
        hmac_key: bytes | None = None,
        layer_timeout_seconds: float = 10.0,
    ):
        self._layers: dict[str, LLMSecurityProtocol] = {}
        self._layer_timeout_seconds = layer_timeout_seconds
        self._init_layers(
            model_digest_registry=model_digest_registry,
            rules_file_baselines=rules_file_baselines,
            project_root=project_root,
            max_tokens=max_tokens,
            max_cost_cents=max_cost_cents,
            hmac_key=hmac_key,
        )

    def _init_layers(self, **kwargs):
        self._layers["l0_supply_chain"] = SupplyChainGuard(
            model_digest_registry=kwargs.get("model_digest_registry"),
            rules_file_baselines=kwargs.get("rules_file_baselines"),
            project_root=kwargs.get("project_root"),
        )
        self._layers["l1_input"] = InputDefenseLayer()
        self._layers["l2_prompt_protection"] = PromptProtectionLayer()
        self._layers["l2a_process_sandbox"] = ProcessSandboxLayer()
        self._layers["l3_output"] = OutputSecurityLayer()
        self._layers["l4_agent"] = AgentSecurityLayer(
            hmac_key=kwargs.get("hmac_key"),
        )
        self._layers["l5_resource_protection"] = ResourceProtectionLayer(
            max_tokens=kwargs.get("max_tokens", 100000),
            max_cost_cents=kwargs.get("max_cost_cents", 500.0),
        )
        self._layers["l6_observability"] = ObservabilityLayer()
        self._layers["l7_validation"] = ValidationLayer()
        self._layers["l8_multi_agent"] = MultiAgentSecurityLayer(
            hmac_key=kwargs.get("hmac_key"),
        )

    @property
    def layers(self) -> dict[str, LLMSecurityProtocol]:
        return dict(self._layers)

    def get_layer(self, layer_name: str) -> LLMSecurityProtocol | None:
        return self._layers.get(layer_name)

    async def scan_input(
        self,
        text: str,
        source: str = "direct_input",
        metadata: dict[str, Any] | None = None,
        mode: ScanMode = ScanMode.INPUT_ONLY,
    ) -> ScanResult:
        """输入扫描：L0->L1->L2->L5 顺序执行.

        fail-closed: 任一层 DENY -> 整体 DENY.
        """
        meta = metadata or {}
        meta["source"] = source
        ctx = SecurityContext(
            request_id=meta.get("request_id", f"lsg-{int(time.time() * 1000)}"),
            layer_name="gateway",
            raw_input=text,
            metadata=meta,
        )

        input_layer_names = ["l0_supply_chain", "l1_input", "l2_prompt_protection", "l5_resource_protection"]
        return await self._evaluate_chain(ctx, input_layer_names, mode)

    async def scan_output(
        self,
        text: str,
        source: str = "model_output",
        metadata: dict[str, Any] | None = None,
        mode: ScanMode = ScanMode.OUTPUT_ONLY,
    ) -> ScanResult:
        """输出扫描：L3->L6 顺序执行.

        fail-closed: L3 DENY -> 整体 DENY; L6 为 pass-through.
        """
        meta = metadata or {}
        meta["source"] = source
        ctx = SecurityContext(
            request_id=meta.get("request_id", f"lsg-{int(time.time() * 1000)}"),
            layer_name="gateway",
            raw_input=text,
            metadata=meta,
        )

        output_layer_names = ["l3_output", "l6_observability"]
        return await self._evaluate_chain(ctx, output_layer_names, mode)

    async def scan_agent_action(
        self,
        text: str,
        tool_name: str = "",
        tool_params: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        mode: ScanMode = ScanMode.AGENT_ONLY,
    ) -> ScanResult:
        """Agent 动作扫描：L4->L5->L8 顺序执行.

        fail-closed: 任一层 DENY -> 整体 DENY.
        """
        meta = metadata or {}
        meta["tool_name"] = tool_name
        meta["tool_params"] = tool_params or {}
        ctx = SecurityContext(
            request_id=meta.get("request_id", f"lsg-{int(time.time() * 1000)}"),
            layer_name="gateway",
            raw_input=text,
            metadata=meta,
        )

        agent_layer_names = ["l4_agent", "l5_resource_protection", "l8_multi_agent"]
        return await self._evaluate_chain(ctx, agent_layer_names, mode)

    async def full_scan(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> ScanResult:
        """全链路扫描：L0->L1->L2->L2a->L3->L4->L5->L6->L7->L8 顺序执行.

        fail-closed: 任一非 pass-through 层 DENY -> 整体 DENY.
        """
        meta = metadata or {}
        ctx = SecurityContext(
            request_id=meta.get("request_id", f"lsg-{int(time.time() * 1000)}"),
            layer_name="gateway",
            raw_input=text,
            metadata=meta,
        )

        all_layer_names = [
            "l0_supply_chain",
            "l1_input",
            "l2_prompt_protection",
            "l2a_process_sandbox",
            "l3_output",
            "l4_agent",
            "l5_resource_protection",
            "l6_observability",
            "l7_validation",
            "l8_multi_agent",
        ]
        return await self._evaluate_chain(ctx, all_layer_names, ScanMode.FULL)

    async def _evaluate_chain(
        self,
        ctx: SecurityContext,
        layer_names: list[str],
        mode: ScanMode,
    ) -> ScanResult:
        """顺序链式评估——纵深防御核心语义：L0->L1->...->LN 严格顺序执行.

        任一非 fail-open 层 DENY/BLOCK -> 立即中断，不评估后续层.
        每层评估带超时保护，防止单层卡死导致整体阻塞.
        """
        t0 = time.perf_counter()
        layer_results: dict[str, SecurityResult] = {}
        passed = 0
        denied = 0
        flagged = 0
        blocked_by = ""
        final_decision = SecurityDecision.ALLOW
        min_score = 1.0

        for name in layer_names:
            layer = self._layers.get(name)
            if layer is None:
                if name in self.FAIL_OPEN_LAYERS:
                    continue
                layer_results[name] = SecurityResult(
                    decision=SecurityDecision.BLOCK,
                    reason=f"{name} is missing/broken — fail-closed",
                    layer_name=name,
                    score=0.0,
                )
                denied += 1
                final_decision = SecurityDecision.BLOCK
                blocked_by = name
                break

            try:
                result = await asyncio.wait_for(
                    layer.evaluate(ctx),
                    timeout=self._layer_timeout_seconds,
                )
                layer_results[name] = result

                kind, should_break, decision_to_set = _classify_layer_decision(
                    name, result, self.FAIL_OPEN_LAYERS
                )
                if kind == "deny":
                    denied += 1
                elif kind == "flag":
                    flagged += 1
                else:
                    passed += 1
                if decision_to_set is not None:
                    final_decision = decision_to_set
                    blocked_by = name
                if should_break:
                    break

                min_score = min(min_score, result.score)

            except TimeoutError:
                if name in self.FAIL_OPEN_LAYERS:
                    layer_results[name] = SecurityResult(
                        decision=SecurityDecision.ALLOW,
                        reason=f"{name} timed out after {self._layer_timeout_seconds}s but is fail-open",
                        layer_name=name,
                        score=1.0,
                    )
                    passed += 1
                else:
                    layer_results[name] = SecurityResult(
                        decision=SecurityDecision.DENY,
                        reason=f"{name} timed out after {self._layer_timeout_seconds}s — fail-closed",
                        layer_name=name,
                        score=0.0,
                    )
                    denied += 1
                    final_decision = SecurityDecision.DENY
                    blocked_by = name
                    break

            except Exception:
                if name in self.FAIL_OPEN_LAYERS:
                    layer_results[name] = SecurityResult(
                        decision=SecurityDecision.ALLOW,
                        reason=f"{name} raised exception but is fail-open",
                        layer_name=name,
                        score=1.0,
                    )
                    passed += 1
                else:
                    layer_results[name] = SecurityResult(
                        decision=SecurityDecision.DENY,
                        reason=f"{name} raised exception — fail-closed",
                        layer_name=name,
                        score=0.0,
                    )
                    denied += 1
                    final_decision = SecurityDecision.DENY
                    blocked_by = name
                    break

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        scan_result = ScanResult(
            decision=final_decision,
            mode=mode,
            layers_evaluated=len(layer_results),
            layers_passed=passed,
            layers_denied=denied,
            layers_flagged=flagged,
            total_score=round(min_score, 3),
            elapsed_ms=round(elapsed_ms, 3),
            layer_results=layer_results,
            blocked_by=blocked_by,
        )

        _maybe_grant_runtime_allowance(final_decision, mode, ctx.request_id)

        return scan_result

    async def validate_self_integrity(self) -> dict[str, Any]:
        """L7 自检：验证 LSG 自身代码完整性."""
        l7 = self._layers.get("l7_validation")
        if l7 is None:
            return {"integrity": "unknown", "reason": "L7 not available"}

        guard = l7.integrity_guard
        result = guard.verify_all()
        all_passed = (result["tampered"] == 0)
        return {
            "integrity": "ok" if all_passed else "compromised",
            "total": result.get("total", 0),
            "clean": result.get("clean", 0),
            "tampered": result.get("tampered", 0),
        }

    async def trigger_regression(self) -> dict[str, Any]:
        """L7 安全回归测试."""
        l7 = self._layers.get("l7_validation")
        if l7 is None:
            return {"regression": "unavailable"}

        from zephyr.security.llm_defense.llm_security.self_protection.l7_validation import RegressionType

        weekly = l7.trigger_security_regression(RegressionType.WEEKLY, gateway=self)
        return {
            "regression": "completed",
            "total_scenarios": weekly.total_scenarios,
            "passed": weekly.passed,
            "failed": weekly.failed,
            "coverage_pct": weekly.coverage_pct,
        }

    def get_observability_metrics(self) -> dict[str, Any]:
        """L6 仪表板指标."""
        l6 = self._layers.get("l6_observability")
        if l6 is None:
            return {}
        metrics = l6.collect_metrics()
        return metrics.model_dump()
