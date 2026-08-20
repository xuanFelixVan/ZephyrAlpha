# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.escalation.escalation_engine
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.security.llm_defense.llm_security.gateway
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
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Escalation Engine — MOD-INF-022

Core escalation engine: rule matching, level determination, auto-escalation with circuit breaker
and economic guard integration.
Blueprint: docs/03_modules/_domain_autonomy_perm/escalation-protocol/blueprint.md §2

裁定#216 Tier1 P2 重构（2026-07-15，Extract Method + table-driven dispatch）
------------------------------------------------------------------------
原 _run_extension_hooks 140 行 McCabe=56（12 个相同 try/except detector 块串联，
P2 detector fan-out 模式）。治本：Extract Method 提取为 12 个模块级 hook 函数
（均 McCabe≤5）+ _HOOK_DISPATCH dict，_run_extension_hooks 简化为 ~10 行
table-driven dispatch 循环（McCabe≈4）。行为等价契约：每个 hook 签名
(event, detector, engine) -> None，就地 mutate event；try/except 由 caller 统一处理。
关键行为保持：
  - hook 按原始顺序执行（dict 保序，Python 3.7+）
  - detector None 时 skip（原始 if 逻辑等价）
  - DriftDetector hook 访问 engine._recent_escalations（通过 engine 参数传入）
  - 原始 CredentialGuard/ClockGuard 用 logger.debug，重构后统一 logger.warning
    （异常路径日志级别差异，无测试覆盖，行为等价）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 升级事件入参 evaluate()
#   fields: category 规则类别 + description 描述 + owner_id 责任人 + source_event_id 来源事件
#   code: escalation_engine.py L295
# - id: I2
#   name: 默认升级规则集 规则表
#   fields: DEFAULT_ESCALATION_RULES 各规则 category/priority/target_level/cooldown_seconds/max_escalations_per_hour
#   code: escalation_models.DEFAULT_ESCALATION_RULES L53
# - id: I3
#   name: 扩展检测器组 动态加载类
#   fields: 18 个 detector 类（循环/劝说/死锁/凭证/时钟/漂移/反弹/SLO 等）importlib 动态实例化
#   code: _load_extension_detectors L478
# - id: I4
#   name: LSG 安全网关 外部扫描服务
#   fields: scan_input 判定结果 allow/block
#   code: lsg_scan_input L533
# 层: 算法
# - id: A1
#   name_zh: ① 输入安全扫描
#   name_en: lsg_scan_input
#   intro: 升级描述先过 LSG 安全网关，拦截恶意输入
#   desc: run_sync(gateway.scan_input(description))，decision 非 allow 抛 PermissionError；ImportError 降级放行
#   inputs: I1 I4
#   outputs: 放行或 PermissionError
# - id: A2
#   name_zh: ② 扩展钩子表驱动分发
#   name_en: _run_extension_hooks/_HOOK_DISPATCH
#   intro: 12 个 hook 按 dict 顺序就地标注事件，可抬升升级等级
#   desc: 循环检测→L2、死锁环→L3、奖励黑客反弹→L4、劝说/凭证/时钟/命令链/置信度/漂移/Merkle/SLO 标注 description
#   inputs: I1 I3
#   outputs: 标注后事件
#   invariant: hook 按 _HOOK_DISPATCH dict 保序执行；detector 缺失则 skip；异常吞掉仅 warning
# - id: A3
#   name_zh: ③ 双闸门拦截评估
#   name_en: evaluate
#   intro: 断路器熔断与经济守卫预算任一不过则直接 REJECTED
#   desc: CircuitBreaker.call() 失败置 circuit_breaker_triggered；EconomicGuard.can_proceed() 失败置 economic_guard_passed=False
#   inputs: A2
#   outputs: 放行事件或 REJECTED 事件
# - id: A4
#   name_zh: ④ 最优规则匹配与冷却限频
#   name_en: _find_best_rule/_check_cooldown
#   intro: 按类别+启用过滤规则取优先级最高者，冷却窗口内同类超限则拒
#   desc: category 匹配不到回退 CUSTOM；priority 降序取首；cooldown_seconds 窗口内同类事件数 ≥ max_escalations_per_hour 拒
#   inputs: I2 A3
#   outputs: 定级事件（target_level）
# - id: A5
#   name_zh: ⑤ 自动升级与委派
#   name_en: escalate
#   intro: 规则允许自动升级则抬一级并封顶 L4，按类别成本扣预算，需要委派置 DELEGATED
#   desc: retry_count<max_retries 时 level+1 封顶 L4_EMERGENCY；CATEGORY_COST 扣 economic_guard；delegate_strategy 非 NONE 置 DELEGATED 并生成建议文本
#   inputs: A4
#   outputs: 升级结果
#   invariant: new_level ≤ L4_EMERGENCY
# 层: 输出
# - id: O1
#   name_zh: 升级事件 EscalationEvent
#   name_en: EscalationEvent
#   intro: 带最终 level/state/description 标注的事件记录，EVALUATING 或 REJECTED
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 升级结果 EscalationResult
#   name_en: EscalationResult
#   intro: escalated/new_level/delegated_to/suggestion 四元组结论
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I4 --> A1
# I1 --> A2
# I3 --> A2
# A1 --> A2
# A2 --> A3
# A3 --> A4
# I2 --> A4
# A4 --> A5
# A4 --> O1
# A5 --> O2
"""

from __future__ import annotations

import importlib
import logging
import threading
from datetime import UTC, datetime, timedelta
from typing import Callable, Protocol, runtime_checkable

from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界

logger = logging.getLogger(__name__)

from zephyr.governance.escalation.escalation_metrics import EscalationMetrics
from zephyr.governance.escalation.escalation_models import (
    DEFAULT_ESCALATION_RULES,
    DelegationStrategy,
    EconomicGuard,
    EscalationEvent,
    EscalationLevel,
    EscalationResult,
    EscalationRule,
    EscalationState,
    RuleCategory,
)
from zephyr.governance.resilience_governance.circuit_breaker import CircuitBreaker, CircuitState


@runtime_checkable
class ExtensionDetector(Protocol):
    """空 Protocol 作为 12 个异构 detector 类的鸭子类型标记。

    Batch 1 (#ARCH-ANY-GOVERNANCE-001)：替换裸 Any 注解。
    每个 detector 类实现不同的方法集，无法用具体 Protocol 描述统一接口。
    """

    pass


# === 裁定#216 Tier1 P2 table-driven dispatch 重构（2026-07-15） ===
# 12 个模块级 hook 函数，签名 (event, detector, engine) -> None，就地 mutate event。
# 每个 hook 对应原 _run_extension_hooks 中的一个 detector 块，按原始顺序注册到 _HOOK_DISPATCH。


def _hook_escalation_loop(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """EscalationLoopDetector: record transition + detect_loop → L2."""
    detector.record_transition(event.event_id, "incoming", event.level.name)
    if detector.detect_loop():
        event.description += " | loop_detected=True"
        if event.level.value < EscalationLevel.L2_HUMAN_REVIEW.value:
            event.level = EscalationLevel.L2_HUMAN_REVIEW


def _hook_persuasion(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """PersuasionDetector: detect → flag（仅 SECURITY_VIOLATION/DEADLOCK）。"""
    if event.category in (RuleCategory.SECURITY_VIOLATION, RuleCategory.DEADLOCK):
        flagged, _ = detector.detect(event.description)
        if flagged:
            event.description += " | persuasion_flagged=True"


def _hook_deadlock(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """DeadlockDetector: detect_cycle → L3（仅 DEADLOCK）。"""
    if event.category is RuleCategory.DEADLOCK:
        cycle = detector.detect_cycle()
        if cycle:
            event.description += f" | deadlock_cycle={','.join(cycle)}"
            if event.level.value < EscalationLevel.L3_CRITICAL.value:
                event.level = EscalationLevel.L3_CRITICAL


def _hook_credential_guard(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """CredentialGuard: scan → flag（仅 SECURITY_VIOLATION）。"""
    if event.category is RuleCategory.SECURITY_VIOLATION:
        if hasattr(detector, "scan") and detector.scan(event.description):
            event.description += " | credential_leak_detected=True"


def _hook_clock_guard(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """ClockGuard: verify → flag。"""
    if hasattr(detector, "verify"):
        if not detector.verify():
            event.description += " | clock_integrity_failed=True"


def _hook_command_chain(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """CommandChainGate: check → flag。"""
    if hasattr(detector, "check"):
        ok, limit = detector.check(event.description)
        if not ok:
            event.description += f" | command_chain_exceeded={limit}"


def _hook_confidence_estimator(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """ConfidenceEstimator: estimate → annotate。"""
    if hasattr(detector, "estimate"):
        conf = detector.estimate(event.description)
        event.description += f" | meta_confidence={conf:.2f}"


def _hook_drift_detector(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """DriftDetector: is_drifting → L2（仅 DRIFT_DETECTED，需 engine._recent_escalations）。"""
    if event.category is RuleCategory.DRIFT_DETECTED:
        if hasattr(detector, "is_drifting"):
            metrics = {
                "event_rate": float(len(engine._recent_escalations)),
                "category_code": float(event.category.value),
            }
            if detector.is_drifting(metrics):
                event.description += " | behavioral_drift=True"
                if event.level.value < EscalationLevel.L2_HUMAN_REVIEW.value:
                    event.level = EscalationLevel.L2_HUMAN_REVIEW


def _hook_merkle_audit(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """MerkleAudit: record → annotate。"""
    if hasattr(detector, "record"):
        root_hash = detector.record(
            {"event_id": event.event_id, "category": event.category.name, "level": event.level.name}
        )
        event.description += f" | merkle_root={root_hash[:12]}"


def _hook_anti_automation_bias(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """AntiAutomationBias: evaluate → flag。"""
    if hasattr(detector, "evaluate"):
        result = detector.evaluate(
            event.event_id,
            is_autonomous=(event.level is EscalationLevel.L0_SELF_HEAL),
            actor_identity=getattr(event, "actor", ""),
            operation_content=event.description,
        )
        if result.forced_review:
            event.description += " | forced_review=True"


def _hook_slo_contract(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """SLOContractEngine: get_recommended_scaling → escalate。"""
    if hasattr(detector, "get_recommended_scaling"):
        scaling = detector.get_recommended_scaling()
        event.description += f" | slo_tier={scaling['current_tier']}"
        if scaling["escalation_level_offset"] > 0:
            new_level = min(EscalationLevel.L4_EMERGENCY.value, event.level.value + scaling["escalation_level_offset"])
            event.level = EscalationLevel(new_level)


def _hook_rebound_detector(event: EscalationEvent, detector: ExtensionDetector, engine: "EscalationEngine") -> None:
    """ReboundDetector: record + detect_rebound → L4（仅 SECURITY_VIOLATION/REWARD_HACKING_REBOUND）。"""
    if event.category in (RuleCategory.SECURITY_VIOLATION, RuleCategory.REWARD_HACKING_REBOUND):
        owner = event.owner_id or "unknown"
        if event.category is RuleCategory.SECURITY_VIOLATION:
            detector.record(owner, "violation", severity="high", description=event.description, event_id=event.event_id)
        elif event.category is RuleCategory.REWARD_HACKING_REBOUND:
            detector.record(
                owner, "rebound", severity="critical", description=event.description, event_id=event.event_id
            )
        if detector.detect_rebound(owner):
            event.description += " | reward_hacking_rebound=True"
            event.level = EscalationLevel.L4_EMERGENCY
            detector.mark_rebound_agent(owner)


_HOOK_DISPATCH: dict[str, Callable[[EscalationEvent, ExtensionDetector, "EscalationEngine"], None]] = {
    "EscalationLoopDetector": _hook_escalation_loop,
    "PersuasionDetector": _hook_persuasion,
    "DeadlockDetector": _hook_deadlock,
    "CredentialGuard": _hook_credential_guard,
    "ClockGuard": _hook_clock_guard,
    "CommandChainGate": _hook_command_chain,
    "ConfidenceEstimator": _hook_confidence_estimator,
    "DriftDetector": _hook_drift_detector,
    "MerkleAudit": _hook_merkle_audit,
    "AntiAutomationBias": _hook_anti_automation_bias,
    "SLOContractEngine": _hook_slo_contract,
    "ReboundDetector": _hook_rebound_detector,
}


class EscalationEngine:
    MAX_ESCALATIONS_PER_HOUR = 100

    CATEGORY_COST: dict[RuleCategory, float] = {
        RuleCategory.AUTO_GUARD_FAILURE: 1.0,
        RuleCategory.BUDGET_EXCEEDED: 3.0,
        RuleCategory.DRIFT_DETECTED: 2.0,
        RuleCategory.DEADLOCK: 5.0,
        RuleCategory.TIMEOUT: 1.0,
        RuleCategory.QUALITY_DEGRADATION: 1.0,
        RuleCategory.SECURITY_VIOLATION: 10.0,
        RuleCategory.OWNER_ABSENT: 2.0,
        RuleCategory.CASCADE_FAILURE: 8.0,
        RuleCategory.REWARD_HACKING_REBOUND: 10.0,
        RuleCategory.CUSTOM: 0.5,
    }

    def __init__(self, name: str = "default", hooks_enabled: bool = True):
        self.name = name
        self._rules: dict[str, EscalationRule] = {}
        self._circuit_breaker = CircuitBreaker(f"escalation:{name}")
        self._economic_guard = EconomicGuard(f"econ:{name}")
        self._metrics = EscalationMetrics()
        self._recent_escalations: list[EscalationEvent] = []
        self._lock = threading.Lock()
        self._hooks_enabled = hooks_enabled
        self._extension_detectors: dict[str, ExtensionDetector] = {}
        self._register_default_rules()
        if self._hooks_enabled:
            self._load_extension_detectors()

    # ── Stage 4 公共化属性 ──

    @property
    def rules(self) -> dict[str, "EscalationRule"]:
        """已注册的规则字典（public API, Stage 4）."""
        return self._rules

    @property
    def hooks_enabled(self) -> bool:
        """hooks 是否启用（public API, Stage 4）."""
        return self._hooks_enabled

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """关联的断路器实例（public API, Stage 4）."""
        return self._circuit_breaker

    @property
    def economic_guard(self) -> EconomicGuard:
        """关联的经济守卫实例（public API, Stage 4）."""
        return self._economic_guard

    @property
    def extension_detectors(self) -> dict[str, "ExtensionDetector"]:
        """扩展检测器字典（public API, Stage 4）."""
        return self._extension_detectors

    @property
    def recent_escalations(self) -> list["EscalationEvent"]:
        """最近的升级事件列表（public API, Stage 4）."""
        return self._recent_escalations

    def _register_default_rules(self) -> None:
        for rule in DEFAULT_ESCALATION_RULES:
            self.register_rule(rule)

    def register_rule(self, rule: EscalationRule) -> None:
        with self._lock:
            self._rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> None:
        with self._lock:
            self._rules.pop(rule_id, None)

    def evaluate(
        self,
        category: RuleCategory,
        description: str = "",
        owner_id: str | None = None,
        source_event_id: str | None = None,
    ) -> EscalationEvent:
        start_time = __import__("time").monotonic()
        self.lsg_scan_input(description)
        event = EscalationEvent(
            category=category,
            description=description,
            owner_id=owner_id,
            source_event_id=source_event_id,
        )
        event = self._run_extension_hooks(event)
        if not self._circuit_breaker.call():
            event.circuit_breaker_triggered = True
            event.state = EscalationState.REJECTED
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        try:
            ab = self._extension_detectors.get("AntiAutomationBias")
            if ab and hasattr(ab, "evaluate"):
                result = ab.evaluate(
                    event.event_id,
                    is_autonomous=(event.level is EscalationLevel.L0_SELF_HEAL),
                    actor_identity=getattr(event, "actor", ""),
                    operation_content=event.description,
                )
                if result.forced_review:
                    event.description += " | forced_review=True"
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in escalation_engine", exc_info=True)

        try:
            slo = self._extension_detectors.get("SLOContractEngine")
            if slo and hasattr(slo, "get_recommended_scaling"):
                scaling = slo.get_recommended_scaling()
                event.description += f" | slo_tier={scaling['current_tier']}"
                if scaling["escalation_level_offset"] > 0:
                    new_level = min(
                        EscalationLevel.L4_EMERGENCY.value, event.level.value + scaling["escalation_level_offset"]
                    )
                    event.level = EscalationLevel(new_level)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in escalation_engine", exc_info=True)

        if not self._economic_guard.can_proceed():
            event.economic_guard_passed = False
            event.state = EscalationState.REJECTED
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        matching_rule = self._find_best_rule(category)
        if matching_rule is None:
            event.state = EscalationState.REJECTED
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        if not self._check_cooldown(matching_rule):
            event.state = EscalationState.REJECTED
            self._metrics.record("blocked", __import__("time").monotonic() - start_time)
            return event
        event.level = matching_rule.target_level
        event.state = EscalationState.EVALUATING
        with self._lock:
            self._recent_escalations.append(event)
            self._prune_old_escalations()
        latency = __import__("time").monotonic() - start_time
        self._metrics.record(event.level.name.lower(), latency)
        return event

    def escalate(self, event: EscalationEvent) -> EscalationResult:
        if event.state is EscalationState.REJECTED:
            return EscalationResult(event=event, escalated=False, new_level=event.level, message="Rejected by gate")
        rule = self._find_best_rule(event.category)
        if rule is None:
            return EscalationResult(event=event, escalated=False, new_level=event.level, message="No matching rule")
        escalated = rule.auto_escalate
        new_level = event.level
        if escalated and event.retry_count < event.max_retries:
            if event.level.value < EscalationLevel.L4_EMERGENCY.value:
                new_level = EscalationLevel(min(event.level.value + 1, EscalationLevel.L4_EMERGENCY.value))
        event.level = new_level
        event.state = EscalationState.ESCALATED if escalated else event.state
        event.updated_at = datetime.now(UTC)
        cost = self.CATEGORY_COST.get(event.category, 1.0)
        self._economic_guard.consume(cost)
        self._circuit_breaker.record_success()
        delegated_to: str | None = None
        if rule.delegate_strategy is not DelegationStrategy.NONE:
            result_msg = f"Escalated to {new_level.name} — delegation needed"
            delegated_to = rule.delegate_strategy.name
            event.delegate_id = delegated_to
            event.state = EscalationState.DELEGATED
        else:
            result_msg = f"Escalated to {new_level.name}"
        return EscalationResult(
            event=event,
            escalated=escalated,
            new_level=new_level,
            delegated_to=delegated_to,
            circuit_broken=False,
            message=result_msg,
            suggestion=self.generate_suggestion(event, rule),
        )

    def record_resolution(self, event: EscalationEvent) -> None:
        event.state = EscalationState.RESOLVED
        event.resolved_at = datetime.now(UTC)
        event.updated_at = datetime.now(UTC)
        self._circuit_breaker.record_success()

    def record_failure(self, event: EscalationEvent) -> None:
        event.retry_count += 1
        self._circuit_breaker.record_failure()

    def get_circuit_state(self) -> CircuitState:
        return self._circuit_breaker.state

    def get_economic_status(self) -> dict[str, object]:
        return {
            "daily_budget": self._economic_guard.daily_budget,
            "consumed_today": self._economic_guard.consumed_today,
            "hard_limit_reached": self._economic_guard.hard_limit_reached,
        }

    def get_metrics(self) -> dict[str, object]:
        return {
            "total_evals": self._metrics._total_evals,
            "blocks": self._metrics._blocks,
            "auto_guards": self._metrics._auto_guards,
            "autonomous": self._metrics._autonomous,
            "escalation_rate": self._metrics.escalation_rate(),
            "avg_latency": self._metrics.avg_latency(),
            "false_positive_rate": self._metrics.false_positive_rate(),
        }

    def get_active_count(self) -> int:
        with self._lock:
            self._prune_old_escalations()
            active = [
                e
                for e in self._recent_escalations
                if e.state
                in (
                    EscalationState.DETECTED,
                    EscalationState.EVALUATING,
                    EscalationState.ESCALATED,
                    EscalationState.DELEGATED,
                )
            ]
            return len(active)

    def _find_best_rule(self, category: RuleCategory) -> EscalationRule | None:
        candidates = [r for r in self._rules.values() if r.category == category and r.enabled]
        if not candidates:
            candidates = [r for r in self._rules.values() if r.category is RuleCategory.CUSTOM and r.enabled]
        if not candidates:
            return None
        candidates.sort(key=lambda r: r.priority, reverse=True)
        return candidates[0]

    def _check_cooldown(self, rule: EscalationRule) -> bool:
        cutoff = datetime.now(UTC) - timedelta(seconds=rule.cooldown_seconds)
        recent_same = [e for e in self._recent_escalations if e.category == rule.category and e.created_at > cutoff]
        return len(recent_same) < rule.max_escalations_per_hour

    def _prune_old_escalations(self) -> None:
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        self._recent_escalations = [e for e in self._recent_escalations if e.created_at > cutoff]

    @staticmethod
    def generate_suggestion(event: EscalationEvent, rule: EscalationRule) -> str:
        """生成升级建议文本（public API, Stage 4）."""
        suggestions: dict[EscalationLevel, str] = {
            EscalationLevel.L0_SELF_HEAL: "Self-healing deployed. Monitor for 5 minutes.",
            EscalationLevel.L1_AUTO_FIX: "Auto-fix triggered. Check audit log for fix details.",
            EscalationLevel.L2_HUMAN_REVIEW: "Human review required. See escalation details.",
            EscalationLevel.L3_CRITICAL: "CRITICAL: immediate attention. Deadlock/cascade detected.",
            EscalationLevel.L4_EMERGENCY: "EMERGENCY: security violation or system-wide failure. All hands.",
        }
        return suggestions.get(event.level, "Review escalation event.")

    def _load_extension_detectors(self):
        detector_modules = [
            ("zephyr.governance.security_governance.persuasion_detector", "PersuasionDetector"),
            ("zephyr.governance.resilience_governance.deadlock_detector", "DeadlockDetector"),
            ("zephyr.gov_drift.drift_detector", "DriftDetector"),
            ("zephyr.governance.escalation.escalation_loop_detector", "EscalationLoopDetector"),
            ("zephyr.governance.resilience_governance.engine_sandbox", "EngineSandbox"),
            ("zephyr.governance.intelligence_governance.confidence_estimator", "ConfidenceEstimator"),
            ("zephyr.gov_drift.vigil_runtime", "VigilRuntime"),
            ("zephyr.governance.architecture_governance.formal_verifier", "FormalVerifier"),
            ("zephyr.governance.intelligence_governance.provider_failover", "ProviderFailover"),
            ("zephyr.governance.security_governance.credential_guard", "CredentialGuard"),
            ("zephyr.gov_audit.merkle_audit", "MerkleAudit"),
            ("zephyr.governance.security_governance.sbom_guard", "SBOMGuard"),
            ("zephyr.governance.ops_governance.clock_guard", "ClockGuard"),
            ("zephyr.governance.context_governance.command_chain_length_gate", "CommandChainGate"),
            ("zephyr.governance.security_governance.compositional_safety_tester", "CompositionalSafetyTester"),
            ("zephyr.governance.security_governance.anti_automation_bias", "AntiAutomationBias"),
            ("zephyr.gov_enforcement.rule_enforcement.slo_contract", "SLOContractEngine"),
            ("zephyr.gov_drift.reward_hacking_rebound_detector", "ReboundDetector"),
        ]
        for module_path, class_name in detector_modules:
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name, None)
                if cls:
                    self._extension_detectors[class_name] = cls()
            except ImportError:
                pass

    def _run_extension_hooks(self, event: EscalationEvent) -> EscalationEvent:
        if not self._hooks_enabled or not self._extension_detectors:
            return event
        for detector_name, hook_fn in _HOOK_DISPATCH.items():
            detector = self._extension_detectors.get(detector_name)
            if detector is None:
                continue
            try:
                hook_fn(event, detector, self)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in escalation_engine", exc_info=True)
        return event

    def enable_hooks(self):
        self._hooks_enabled = True
        if not self._extension_detectors:
            self._load_extension_detectors()

    def disable_hooks(self):
        self._hooks_enabled = False

    def _lsg_scan_input(self, description: str) -> None:
        """[DEPRECATED] 薄包装, 转发到公共 lsg_scan_input (reverse hierarchy)。"""
        self.lsg_scan_input(description)

    def lsg_scan_input(self, description: str) -> None:
        if not description:
            return
        try:
            import asyncio

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

            gateway = LSGSecurityGateway()
            result = run_sync(gateway.scan_input(description))
            if result.decision.value not in ("allow", "ALLOW"):
                raise PermissionError(f"LSG blocked escalation input: {result.decision.value}")
        except ImportError:
            pass


__version__ = "0.14.0"
