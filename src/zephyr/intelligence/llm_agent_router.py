# [BLUEPRINT] MOD-INT-AGENT-ROUTER | docs/03_modules/_domain_intelligence/llm_agent_router/blueprint.md | §0-5
# [MODULE] zephyr.intelligence.llm_agent_router
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors(ZephyrBaseError)
# [CONSUMERS] 运行时装配批（decision_engine 接级联 / cost_ledger 接台账 / audit_sink 接审计链 / period 接交易时段真源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定核心纯内存无IO; 配置非法Fail-Closed; 空候选→RouteDecisionError; 成本判定确定性; 降级=信号语义; 零密钥字段; 仅信号输入无下单语义
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/llm_agent_router/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidRouterConfigError(ZA-IT-0019); RouteDecisionError(ZA-IT-0020)
# [TESTS] tests/intelligence/test_llm_agent_router.py
# [A_module] module_id=MOD-INT-AGENT-ROUTER | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""LlmAgentRouter — LLM Agent 路由门面（MOD-INT-AGENT-ROUTER）。

B11-02458（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§0边界声明/§8）：任务分类
→ 模型选择（委托级联决策引擎）→ 成本控制（日预算门）三级流水线；分时策略；
延迟预算校验留痕；路由审计。

查重裁定：不重建 cascade_orchestrator 级联（已覆盖时段+三阶段），模型选择
段经注入 decision_engine 委托其 route() 语义；与 api_llm_pool 分工：本模块
管路由决策时点日预算判定，池级累计台账仍归池。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_log = logging.getLogger(__name__)

__all__: Final = [
    "AgentRouteDecision",
    "AgentRouterConfig",
    "InvalidRouterConfigError",
    "LlmAgentRouter",
    "RouteAuditRecord",
    "RouteDecisionError",
    "RouteRequest",
    "TaskClassification",
]


class InvalidRouterConfigError(ZephyrBaseError):
    """路由配置非法（Fail-Closed）。"""

    error_code = "ZA-IT-0019"


class RouteDecisionError(ZephyrBaseError):
    """路由决策异常（空候选等）。"""

    error_code = "ZA-IT-0020"


@dataclass(frozen=True)
class TaskClassification:
    """任务分类结果。"""

    task_type: str
    kind: str
    local_pref: bool
    reason: str


@dataclass(frozen=True)
class RouteRequest:
    """路由请求。"""

    task_type: str
    candidates: list[str]
    period: str = "intraday"
    complexity: str = "moderate"
    estimated_cost_usd: float = 0.0


@dataclass(frozen=True)
class AgentRouteDecision:
    """路由决策。"""

    task_type: str
    selected_model: str | None
    provider: str
    source: str
    degraded_to_local: bool
    reasons: tuple[str, ...]
    latency_violations: tuple[str, ...]


@dataclass(frozen=True)
class RouteAuditRecord:
    """路由审计记录。"""

    request_fingerprint: str
    classification: TaskClassification
    decision: AgentRouteDecision
    daily_cost_before: float
    daily_cost_after: float
    period: str
    sink_errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentRouterConfig:
    """路由配置。"""

    daily_budget_usd: float
    period_rules: dict[str, dict[str, Any]]
    latency_budgets_ms: tuple[int, int, int] = (50, 10, 5)

    def __post_init__(self) -> None:
        if self.daily_budget_usd < 0:
            raise InvalidRouterConfigError(f"日预算不能为负: {self.daily_budget_usd}")
        if any(b <= 0 for b in self.latency_budgets_ms):
            raise InvalidRouterConfigError(f"延迟预算须全正: {self.latency_budgets_ms}")


class LlmAgentRouter:
    """LLM Agent 路由判定核心（纯内存，无 IO）。"""

    def __init__(
        self,
        config: AgentRouterConfig,
        decision_engine: Callable[[RouteRequest], dict[str, Any]] | None = None,
        cost_ledger: Callable[[], float] | None = None,
        audit_sink: Callable[[RouteAuditRecord], None] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._config = config
        self._decision_engine = decision_engine
        self._cost_ledger = cost_ledger
        self._audit_sink = audit_sink
        self._clock = clock or (lambda: 0.0)
        self._daily_cost: float = 0.0
        self._today: int = 0

    def _ensure_day(self) -> None:
        today = int(self._clock() // 86400)
        if today != self._today:
            self._today = today
            self._daily_cost = 0.0

    def daily_cost(self) -> float:
        self._ensure_day()
        return self._daily_cost

    def reset_daily(self) -> None:
        self._daily_cost = 0.0

    def classify(self, task_type: str) -> TaskClassification:
        rules = self._config.period_rules.get("task_kinds", {})
        kind = rules.get(task_type, "general")
        local_pref = kind in ("local", "hybrid")
        return TaskClassification(
            task_type=task_type,
            kind=kind,
            local_pref=local_pref,
            reason="rules" if task_type in rules else "default",
        )

    def route(self, request: RouteRequest) -> AgentRouteDecision:
        if not request.candidates:
            raise RouteDecisionError("candidates 为空")
        self._ensure_day()
        t0 = self._clock()
        classification = self.classify(request.task_type)
        t1 = self._clock()
        # Stage2: 模型选择（委托决策引擎）
        decision_data: dict[str, Any] = {}
        if self._decision_engine is not None:
            try:
                decision_data = self._decision_engine(request)
            except Exception as exc:
                _log.warning("decision_engine 异常: %s", exc)
                decision_data = {}
        t2 = self._clock()
        selected = decision_data.get("model")
        provider = decision_data.get("provider", "local")
        # Stage3: 成本控制
        daily_before = self._daily_cost
        cost = request.estimated_cost_usd
        degraded = False
        reasons: list[str] = list(decision_data.get("reasons", []))
        if daily_before + cost > self._config.daily_budget_usd:
            degraded = True
            reasons.append("日预算超限，降级本地")
        if request.period == "intraday" and not classification.local_pref:
            reasons.append("盘中非白名单 kind 强制本地")
        # 分时策略：盘中强制本地候选
        if request.period == "intraday":
            selected = self._pick_local(request.candidates, selected)
            provider = "local"
        self._daily_cost = daily_before + cost
        # 延迟预算校验
        latency_violations: list[str] = []
        stages = (t1 - t0, t2 - t1, self._clock() - t2)
        labels = ("classify", "select", "cost")
        for dur, budget, label in zip(stages, self._config.latency_budgets_ms, labels):
            if dur * 1000 > budget:
                latency_violations.append(f"{label} 超预算 {dur*1000:.2f}ms>{budget}ms")
        decision = AgentRouteDecision(
            task_type=request.task_type,
            selected_model=selected,
            provider=provider,
            source="agent_router",
            degraded_to_local=degraded,
            reasons=tuple(reasons),
            latency_violations=tuple(latency_violations),
        )
        audit = RouteAuditRecord(
            request_fingerprint=f"{request.task_type}:{request.period}",
            classification=classification,
            decision=decision,
            daily_cost_before=daily_before,
            daily_cost_after=self._daily_cost,
            period=request.period,
        )
        if self._audit_sink is not None:
            try:
                self._audit_sink(audit)
            except Exception as exc:
                _log.warning("audit_sink 异常: %s", exc)
        return decision

    def _pick_local(self, candidates: list[str], fallback: str | None) -> str | None:
        for c in candidates:
            if c.startswith("local_") or c.startswith("ollama"):
                return c
        return fallback
