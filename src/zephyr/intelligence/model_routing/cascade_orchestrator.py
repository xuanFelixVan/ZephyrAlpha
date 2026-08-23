# [BLUEPRINT] MOD-MODEL_ROUTER_ORCH | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/11_evidence_skill_router.md | §3.3/§4.3
# [MODULE] zephyr.intelligence.model_routing.cascade_orchestrator
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.capability_passport(CapabilityPassport/TamperError/QuickProfile); zephyr.intelligence.model_profiling.job_matcher(JobMatcher); zephyr.intelligence.model_profiling.task_model_learner(ModelTaskMatrix); zephyr.governance.intelligence_governance.model_router(ModelRouter/RoutingDecision/TaskComplexity 只消费不改); zephyr.governance.ops_governance.budget_models(ModelTier); zephyr.shared.io.paths(REPO_ROOT)
# [CONSUMERS] 待统筹接线（06号文 Phase 2 dispatch 链 + AutoRuntime）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只做消费与串联（三基座 CapabilityPassport/JobMatcher/task_model_learner + MOD-INF-024 ModelRouter 内部结构零改动）; L1 验签失败=拒绝（伪造/篡改护照不进入候选）; required 硬门不满足不进入 L2; 级联降级链逐段留痕（每段故障=降级产物+告警，不中断路由返回）; 风控类任务必须外部 API 不可降级（HB-09，故障注入也不落本地/规则引擎）; 路由规则落配置（config/model_routing_policy.yaml，配置变更不改代码）; 可变容器 typing.Final 禁重新赋值
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CascadeRoutingError(ZA-IT-0012)：策略文件缺失/损坏/缺段 fail-closed; 三基座/ModelRouter 运行期异常不抛 -> 级联降级（degraded_stages+alerts 留痕）
# [TESTS] tests/intelligence/model_routing/test_cascade_orchestrator.py
# [A_module] module_id=MOD-MODEL_ROUTER_ORCH | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
cascade_orchestrator — 模型路由级联编排层（11号文 §3.3/§4.3，P1-1~P1-5）
================================================================================

一次路由决策串成三段级联（编排层只做消费与串联，不改三个基座内部结构）：

- **L1 能力门**：消费 CapabilityPassport（verify=True 验签），岗位 required 硬门 +
  safe_capabilities 交集过滤候选模型。伪造/篡改护照验签失败被拒；
  全部候选无护照 -> 本段降级（不过滤+告警），由下游静态映射兜底。
- **L2 任务适配排序**：融合 JobMatcher match_score 与 task_model_learner
  composite_score（权重配置化）；样本=0 -> 静态映射兜底（task_model_learner 先例）。
- **L3 成本/层级路由**：复用 MOD-INF-024 ModelRouter（源文件零改动）做 API 侧
  tier×perf-aware 终裁；本地优先、API 兜底；时段限制（附表 B）与风控不可降级
  （附表 C / HB-09）在此硬执行。

级联降级链：任一段异常 -> degraded_stages 记录 + alerts 告警 + 静态映射/兜底返回，
不中断路由返回。风控类任务（non_degradable）任一段故障仍落外部 API。
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.governance.intelligence_governance.model_router import ModelRouter, TaskComplexity
from zephyr.governance.ops_governance.budget_models import ModelTier
from zephyr.intelligence.model_profiling.capability_passport import (
    CapabilityPassport,
    QuickProfile,
    TamperError,
)
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "CascadeDecision",
    "CascadeOrchestrator",
    "CascadeRoutingError",
    "DEFAULT_POLICY_PATH",
]

_log = logging.getLogger(__name__)

DEFAULT_POLICY_PATH: Final[Path] = REPO_ROOT / "config" / "model_routing_policy.yaml"

# 策略文件必需顶层段（缺段=fail-closed，防半配置静默路由）
_POLICY_REQUIRED_SECTIONS: Final[tuple[str, ...]] = (
    "fusion",
    "local_providers",
    "api_providers",
    "risk_api_default",
    "rule_engine_provider",
    "task_routes",
    "period_rules",
    "task_job_map",
    "static_mapping",
)


class CascadeRoutingError(Exception):
    """级联路由错误（策略文件缺失/损坏/缺段 fail-closed）。"""

    error_code = "ZA-IT-0012"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class CascadeDecision:
    """级联路由决策（JSON 可序列化；reason+估成本+降级留痕字段完整，P1-3 验收口径）。"""

    task_type: str
    model_key: str
    provider: str
    tier: str  # ModelTier.value；规则引擎/静态映射兜底="UNTIERED"
    reason: str
    estimated_cost_per_1k: tuple[float, float] = (0.0, 0.0)
    performance_score: float = 0.0
    match_score: float = 0.0
    composite_score: float = 0.0
    source: str = "cascade"  # cascade / static_mapping / rule_engine / risk_locked
    risk_locked: bool = False
    degraded_stages: list[str] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _provider_of(model_key: str, api_providers: frozenset[str], local_providers: frozenset[str]) -> str:
    """候选模型 -> provider：命中 api/local 前缀表即取，否则默认本地 ollama（护照模型为本地 Ollama）。"""
    prefix = model_key.split(":", 1)[0]
    if prefix in api_providers or prefix in local_providers:
        return prefix
    return "ollama"


class CascadeOrchestrator:
    """级联编排器——L1 能力门 -> L2 任务适配排序 -> L3 成本/层级路由。

    全部外部依赖可注入（测试全 fake；生产缺省惰性构造真实基座）：
    passport_loader（默认 CapabilityPassport.load）、profile_loader（默认 QuickProfile.load）、
    job_matcher/learner/model_router（默认 JobMatcher/ModelTaskMatrix/ModelRouter 惰性构造）。
    """

    def __init__(
        self,
        *,
        policy_path: Path | str | None = None,
        passport_loader: Any | None = None,
        profile_loader: Any | None = None,
        job_matcher: Any | None = None,
        learner: Any | None = None,
        model_router: Any | None = None,
    ) -> None:
        self._policy_path = Path(policy_path) if policy_path is not None else DEFAULT_POLICY_PATH
        self._policy = self._load_policy(self._policy_path)
        self._passport_loader = passport_loader or CapabilityPassport.load
        self._profile_loader = profile_loader or QuickProfile.load
        self._job_matcher = job_matcher
        self._learner = learner
        self._model_router = model_router
        self._api_providers: Final = frozenset(self._policy["api_providers"])
        self._local_providers: Final = frozenset(self._policy["local_providers"])

    # ── 策略加载（fail-closed）────────────────────────────

    @staticmethod
    def _load_policy(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise CascadeRoutingError(f"路由策略文件缺失: {path}")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise CascadeRoutingError(f"路由策略 YAML 损坏: {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise CascadeRoutingError(f"路由策略根节点非映射: {path}")
        missing = [s for s in _POLICY_REQUIRED_SECTIONS if s not in data]
        if missing:
            raise CascadeRoutingError(f"路由策略缺段 {missing}: {path}")
        return data

    # ── 基座懒解析 ───────────────────────────────────────

    def _resolve_job_matcher(self) -> Any:
        if self._job_matcher is None:
            from zephyr.intelligence.model_profiling.job_matcher import JobMatcher

            self._job_matcher = JobMatcher()
        return self._job_matcher

    def _resolve_learner(self) -> Any:
        if self._learner is None:
            from zephyr.intelligence.model_profiling.task_model_learner import ModelTaskMatrix

            self._learner = ModelTaskMatrix()
        return self._learner

    def _resolve_model_router(self) -> Any:
        if self._model_router is None:
            self._model_router = ModelRouter()
        return self._model_router

    # ── L1 能力门 ────────────────────────────────────────

    def _l1_filter(
        self,
        candidates: list[str],
        required: list[str],
        alerts: list[str],
    ) -> tuple[list[str], bool]:
        """返回 (通过候选, 本段是否降级)。

        验签失败（TamperError）-> 拒绝+告警（不降级放行）；无护照 -> 排除；
        required 非 safe_capabilities 子集 -> 排除。全部候选均因无护照排除 ->
        本段降级（不过滤，交下游静态映射兜底）。
        """
        passed: list[str] = []
        no_passport_count = 0
        for model_id in candidates:
            try:
                passport = self._passport_loader(model_id, verify=True)
            except TamperError as exc:
                alerts.append(f"L1 护照验签失败被拒: {model_id} ({exc})")
                _log.warning("cascade L1: 护照验签失败被拒 %s: %s", model_id, exc)
                continue
            if passport is None:
                no_passport_count += 1
                continue
            safe = set(passport.recommendations.safe_capabilities)
            if not set(required).issubset(safe):
                alerts.append(f"L1 required 硬门不满足: {model_id} 缺 {sorted(set(required) - safe)}")
                continue
            passed.append(model_id)
        if not passed and no_passport_count == len(candidates):
            alerts.append("L1 全部候选无护照，降级为不过滤（静态映射兜底上游）")
            _log.warning("cascade L1: 无护照可用，降级不过滤")
            return list(candidates), True
        return passed, False

    # ── L2 任务适配排序 ──────────────────────────────────

    def _l2_rank(
        self,
        task_type: str,
        candidates: list[str],
    ) -> tuple[list[str], dict[str, dict[str, float]], str]:
        """返回 (排序后候选, {model: {match, composite, fused}}, source)。

        样本=0（learner 对该任务零样本）-> 静态映射兜底排序（source=static_mapping）；
        否则 match×w_job + composite×w_learn 融合降序（source=fused）。
        """
        snapshot = self._resolve_learner().snapshot().get(task_type, {}) or {}
        total_samples = sum(int(v.get("sample_count", 0)) for v in snapshot.values())

        if total_samples == 0:
            mapping = self._policy["static_mapping"].get(task_type) or self._policy["static_mapping"]["default"]
            mapped = [m for m in mapping if m in candidates]
            rest = [m for m in candidates if m not in mapped]
            ranked = mapped + rest
            scores = {m: {"match": 0.0, "composite": 0.0, "fused": 0.0} for m in ranked}
            return ranked, scores, "static_mapping"

        w_job = float(self._policy["fusion"]["job_match_weight"])
        w_learn = float(self._policy["fusion"]["learner_weight"])
        job_id = self._policy["task_job_map"].get(task_type)

        match_scores: dict[str, float] = {}
        if job_id:
            matcher = self._resolve_job_matcher()
            for m in candidates:
                profile = self._profile_loader(m)
                if profile is None:
                    match_scores[m] = 0.0
                    continue
                rec = next((r for r in matcher.match(profile) if r.job_id == job_id), None)
                match_scores[m] = float(rec.match_score) if rec is not None else 0.0

        scores: dict[str, dict[str, float]] = {}
        for m in candidates:
            entry = snapshot.get(m, {})
            composite = float(entry.get("composite_score", 0.0))
            match = match_scores.get(m, 0.0)
            fused = round(w_job * match + w_learn * composite, 4) if job_id else composite
            scores[m] = {"match": match, "composite": composite, "fused": fused}
        ranked = sorted(candidates, key=lambda m: scores[m]["fused"], reverse=True)
        return ranked, scores, "fused"

    # ── L3 成本/层级路由 ─────────────────────────────────

    def _api_decision(
        self,
        task_type: str,
        complexity: TaskComplexity,
        alerts: list[str],
    ) -> CascadeDecision:
        """API 侧终裁：复用 MOD-INF-024 ModelRouter（只消费不改源文件）。"""
        routing = self._resolve_model_router().route(complexity=complexity)
        return CascadeDecision(
            task_type=task_type,
            model_key=routing.model_key,
            provider=routing.provider,
            tier=routing.tier.value,
            reason=f"api-router:{routing.reason}",
            estimated_cost_per_1k=tuple(routing.estimated_cost_per_1k),
            performance_score=float(routing.performance_score),
            source="cascade",
            alerts=alerts,
        )

    def _static_decision(
        self,
        task_type: str,
        candidates: list[str],
        reason: str,
        alerts: list[str],
        degraded: list[str],
    ) -> CascadeDecision:
        """静态映射兜底（task_model_learner 样本=0 先例同款兜底链末端）。"""
        mapping = self._policy["static_mapping"].get(task_type) or self._policy["static_mapping"]["default"]
        pick = next((m for m in mapping if m in candidates), mapping[0] if mapping else self._policy["default_local_model"])
        return CascadeDecision(
            task_type=task_type,
            model_key=pick,
            provider=_provider_of(pick, self._api_providers, self._local_providers),
            tier="UNTIERED",
            reason=reason,
            source="static_mapping",
            degraded_stages=degraded,
            alerts=alerts,
        )

    def _risk_locked_decision(
        self,
        task_type: str,
        complexity: TaskComplexity,
        reason: str,
        alerts: list[str],
        degraded: list[str],
    ) -> CascadeDecision:
        """风控不可降级出口（HB-09）：任何上游故障仍落外部 API，绝不落本地/规则引擎。"""
        try:
            routing = self._resolve_model_router().route(complexity=complexity)
            model_key, provider = routing.model_key, routing.provider
            api_reason = f"api-router:{routing.reason}"
            perf = float(routing.performance_score)
            est = tuple(routing.estimated_cost_per_1k)
        except Exception as exc:  # noqa: BLE001 — 风控任务 L3 故障也不降级本地：落配置化外部 API 兜底
            _log.warning("cascade L3 风控任务 ModelRouter 异常，落 risk_api_default: %s", exc)
            alerts.append(f"L3 ModelRouter 异常，风控任务落 risk_api_default: {exc}")
            if "L3" not in degraded:
                degraded.append("L3")
            model_key = self._policy["risk_api_default"]
            provider = _provider_of(model_key, self._api_providers, self._local_providers)
            api_reason = "risk-api-default"
            perf = 0.0
            est = (0.0, 0.0)
        return CascadeDecision(
            task_type=task_type,
            model_key=model_key,
            provider=provider,
            tier="UNTIERED",
            reason=f"risk-locked(HB-09 不可降级)|{api_reason}|{reason}",
            estimated_cost_per_1k=est,
            performance_score=perf,
            source="risk_locked",
            risk_locked=True,
            degraded_stages=degraded,
            alerts=alerts,
        )

    # ── 级联主入口 ───────────────────────────────────────

    def route(
        self,
        task_type: str,
        candidates: list[str],
        *,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        period: str | None = None,
        required_capabilities: list[str] | None = None,
    ) -> CascadeDecision:
        """一次级联路由决策（逐段故障注入均有降级产物+告警，不中断返回）。

        task_type 须命中策略 task_routes（未登记任务按默认 local 规格处理并告警）；
        period 命中 period_rules 且 api=restricted 时，非 api_allowed_kinds 任务本地only
        （风控 non_degradable 任务不受时段限制——附表 C 成本规则对风控不适用）。
        """
        if not candidates:
            raise CascadeRoutingError("candidates 为空（级联路由至少需一个候选模型）")
        alerts: list[str] = []
        degraded: list[str] = []

        route_spec = self._policy["task_routes"].get(task_type)
        if route_spec is None:
            alerts.append(f"任务 {task_type} 未登记路由表，按默认 local 规格处理")
            route_spec = {"preferred": "local", "fallbacks": [], "kind": "general", "reason": "unregistered-task"}
        risk_locked = bool(route_spec.get("non_degradable", False))

        # 规则引擎直达（附表 A 第 1 行：确定性规则无 LLM，非降级产物）
        if route_spec["preferred"] == "rule_engine":
            return CascadeDecision(
                task_type=task_type,
                model_key=self._policy["rule_engine_provider"],
                provider=self._policy["rule_engine_provider"],
                tier="UNTIERED",
                reason=f"routing-table:rule-engine|{route_spec['reason']}",
                source="rule_engine",
                alerts=alerts,
            )

        required = list(required_capabilities) if required_capabilities else [task_type]

        # L1 能力门
        try:
            passed, l1_degraded = self._l1_filter(candidates, required, alerts)
            if l1_degraded:
                degraded.append("L1")
        except Exception as exc:  # noqa: BLE001 — 级联降级链：L1 故障不过滤+告警不中断
            _log.warning("cascade L1 异常，降级不过滤: %s", exc)
            alerts.append(f"L1 异常降级不过滤: {type(exc).__name__}: {exc}")
            degraded.append("L1")
            passed = list(candidates)

        if not passed:
            alerts.append("L1 过滤后候选为空")
            if risk_locked:
                return self._risk_locked_decision(
                    task_type, complexity, "L1 候选为空", alerts, degraded
                )
            return self._static_decision(
                task_type, candidates, "L1 候选为空->静态映射兜底", alerts, degraded
            )

        # L2 任务适配排序
        try:
            ranked, scores, l2_source = self._l2_rank(task_type, passed)
        except Exception as exc:  # noqa: BLE001 — 级联降级链：L2 故障按原序+告警不中断
            _log.warning("cascade L2 异常，降级按候选原序: %s", exc)
            alerts.append(f"L2 异常降级按候选原序: {type(exc).__name__}: {exc}")
            degraded.append("L2")
            ranked, scores, l2_source = list(passed), {}, "degraded"

        # L3 成本/层级路由（本地优先 API 兜底 + 时段限制 + 风控不可降级）
        if risk_locked:
            return self._risk_locked_decision(
                task_type, complexity, route_spec["reason"], alerts, degraded
            )

        local_only = False
        if period is not None:
            period_spec = self._policy["period_rules"].get(period)
            if period_spec is None:
                alerts.append(f"时段 {period} 未登记 period_rules，按 api allowed 处理")
            elif period_spec.get("api") == "restricted":
                allowed_kinds = set(period_spec.get("api_allowed_kinds", []))
                if route_spec.get("kind", "general") not in allowed_kinds:
                    local_only = True
                    alerts.append(f"时段 {period} API 受限，{route_spec.get('kind', 'general')} 类任务本地only")

        try:
            local_ranked = [
                m for m in ranked
                if _provider_of(m, self._api_providers, self._local_providers) in self._local_providers
            ]
            modes = ["local"] if local_only else [route_spec["preferred"], *route_spec.get("fallbacks", [])]
            for mode in modes:
                if mode in ("local", "hybrid") and local_ranked:
                    winner = local_ranked[0]
                    score = scores.get(winner, {})
                    return CascadeDecision(
                        task_type=task_type,
                        model_key=winner,
                        provider=_provider_of(winner, self._api_providers, self._local_providers),
                        tier="UNTIERED",
                        reason=(
                            f"local-first|l2:{l2_source}|{route_spec['reason']}"
                            + ("|period-local-only" if local_only else "")
                        ),
                        match_score=float(score.get("match", 0.0)),
                        composite_score=float(score.get("composite", 0.0)),
                        source="cascade" if not local_only else "cascade_period_restricted",
                        degraded_stages=degraded,
                        alerts=alerts,
                    )
                if mode == "hybrid":
                    continue  # hybrid=本地优先 API 兜底：本地落空后顺延后续模式
                if mode in ("api", "api_multi"):
                    decision = self._api_decision(task_type, complexity, alerts)
                    decision.degraded_stages = degraded
                    decision.match_score = float(scores.get(ranked[0], {}).get("match", 0.0)) if ranked else 0.0
                    decision.composite_score = (
                        float(scores.get(ranked[0], {}).get("composite", 0.0)) if ranked else 0.0
                    )
                    return decision
                if mode == "rule_engine":
                    return CascadeDecision(
                        task_type=task_type,
                        model_key=self._policy["rule_engine_provider"],
                        provider=self._policy["rule_engine_provider"],
                        tier="UNTIERED",
                        reason=f"routing-table:rule-engine-fallback|{route_spec['reason']}",
                        source="rule_engine",
                        degraded_stages=degraded,
                        alerts=alerts,
                    )
            # 模式链全部落空（如本地任务但候选全 API 且时段受限）-> 静态映射兜底
            return self._static_decision(
                task_type, ranked, "模式链落空->静态映射兜底", alerts, degraded
            )
        except CascadeRoutingError:
            raise
        except Exception as exc:  # noqa: BLE001 — 级联降级链：L3 故障静态映射+告警不中断
            _log.warning("cascade L3 异常，降级静态映射: %s", exc)
            alerts.append(f"L3 异常降级静态映射: {type(exc).__name__}: {exc}")
            degraded.append("L3")
            return self._static_decision(
                task_type, ranked, f"L3 异常({type(exc).__name__})->静态映射兜底", alerts, degraded
            )
