# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §3.1
# [MODULE] zephyr.trading.verdict_engine
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.governance.audit_trail.models
# [CONSUMERS] MOD-INF-027(audit-orchestrator);MOD-INF-031(auto-fix-engine);zephyr.trading.admission_controller
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] VerdictLevel三态判定不可扩展；GraduatedLevel升级矩阵由protection_level+gate+violations联合决定
# [MODIFY-GUARD] docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md;src/zephyr/behavioral-admission/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] evaluate: PermissionCheckTimeout→Verdict(RED); evaluate_batch: partial_failure→individual RED
# [TESTS] tests/test_behavioral_audit/test_verdict_engine.py
# [A_module] module_id=MOD-ORC_verdict_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum, IntEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

try:
    from zephyr.governance.audit_trail.models import AuditEntryV1, AuditEventType

    _HAS_AUDIT_ENTRY = True
except ImportError as e:
    logger.warning(
        "verdict_engine: audit_trail import failed, audit features disabled (%s: %s)",
        type(e).__name__,
        e,
    )
    _HAS_AUDIT_ENTRY = False
    AuditEntryV1 = None
    AuditEventType = None


class AuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_type: str = ""
    agent_id: str = ""
    session_id: str = ""
    target_path: str = ""
    operation: str = ""
    is_human: bool = False
    is_cross_module: bool = False
    protection_level: str = "normal"
    gate_passed: bool = False
    trust_score: float = 50.0
    violation_count: int = 0
    timestamp: str = ""


class VerdictLevel(str, Enum):
    PASS = "PASS"
    YELLOW = "YELLOW"
    RED = "RED"


class ProtectionLevel(str, Enum):
    anchor = "anchor"
    protected = "protected"
    normal = "normal"
    public = "public"


class GraduatedLevel(IntEnum):
    L0 = 0
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6


class ActorInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = ""
    is_human: bool = False
    trust_score: float = 50.0
    violation_count: int = 0


class OperationInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: str = ""
    target_path: str = ""
    is_cross_module: bool = False
    protection_level: ProtectionLevel = ProtectionLevel.normal


class AuthCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gate_passed: bool = False
    gate_id: str = ""
    check_duration_ms: float = 0.0
    error: str = ""


class ResponseInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: VerdictLevel = VerdictLevel.PASS
    graduated_level: GraduatedLevel = GraduatedLevel.L0
    reason: str = ""
    requires_consensus: bool = False
    latency_ms: float = 0.0


class EvidenceChain(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor: ActorInfo = Field(default_factory=ActorInfo)
    operation: OperationInfo = Field(default_factory=OperationInfo)
    auth_check: AuthCheckResult = Field(default_factory=AuthCheckResult)
    response: ResponseInfo = Field(default_factory=ResponseInfo)


class MultiModelResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_id: str = ""
    verdict: VerdictLevel = VerdictLevel.PASS
    confidence: float = 0.0
    reasoning: str = ""
    latency_ms: float = 0.0


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict_level: VerdictLevel = VerdictLevel.PASS
    graduated_level: GraduatedLevel = GraduatedLevel.L0
    protection_level: ProtectionLevel = ProtectionLevel.normal
    gate_passed: bool = False
    requires_consensus: bool = False
    evidence: EvidenceChain = Field(default_factory=EvidenceChain)
    multi_model_results: list[MultiModelResult] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
    reason: str = ""


_YELLOW_TRUST_THRESHOLD: float = 30.0
_YELLOW_VIOLATION_THRESHOLD: int = 3


class VerdictEngine:
    def __init__(
        self,
        protection_index: Any = None,
        gpu_scheduler: Any = None,
        verdict_timeout_s: float = 10.0,
    ) -> None:
        self._protection_index = protection_index
        self._gpu_scheduler = gpu_scheduler
        self._verdict_timeout_s = verdict_timeout_s
        self._eval_count: int = 0
        self._red_count: int = 0
        self._yellow_count: int = 0
        self._pass_count: int = 0

    async def evaluate(self, event: Any) -> Verdict:
        start = time.monotonic()
        self._eval_count += 1

        if _HAS_AUDIT_ENTRY and isinstance(event, AuditEntryV1):
            actor = ActorInfo(
                agent_id=event.agent_id,
                is_human=False,
                trust_score=event.trust_score if event.trust_score is not None else 50.0,
                violation_count=0,
            )
            prot_level_str = getattr(event, "permission_level", "normal") or "normal"
            try:
                prot_level = ProtectionLevel(prot_level_str)
            except ValueError:
                prot_level = ProtectionLevel.normal
            operation = OperationInfo(
                operation=event.operation,
                target_path=event.target_path,
                is_cross_module=getattr(event, "indirect_operation", False),
                protection_level=prot_level,
            )
            gate_passed = bool(getattr(event, "guard_checks_passed", []))
            violation_count = 0
        elif isinstance(event, AuditEvent):
            actor = ActorInfo(
                agent_id=event.agent_id,
                is_human=event.is_human,
                trust_score=event.trust_score,
                violation_count=event.violation_count,
            )
            try:
                prot_level = ProtectionLevel(event.protection_level)
            except ValueError:
                prot_level = ProtectionLevel.normal
            operation = OperationInfo(
                operation=event.operation,
                target_path=event.target_path,
                is_cross_module=event.is_cross_module,
                protection_level=prot_level,
            )
            gate_passed = event.gate_passed
            violation_count = event.violation_count
        elif isinstance(event, dict):
            actor = ActorInfo(
                agent_id=event.get("agent_id", ""),
                is_human=event.get("is_human", False),
                trust_score=event.get("trust-score", 50.0),
                violation_count=event.get("violation_count", 0),
            )
            try:
                prot_level = ProtectionLevel(event.get("protection_level", "normal"))
            except ValueError:
                prot_level = ProtectionLevel.normal
            operation = OperationInfo(
                operation=event.get("operation", ""),
                target_path=event.get("target_path", ""),
                is_cross_module=event.get("is_cross_module", False),
                protection_level=prot_level,
            )
            gate_passed = event.get("gate_passed", False)
            violation_count = event.get("violation_count", 0)
        else:
            self._red_count += 1
            return Verdict(
                verdict_level=VerdictLevel.RED,
                graduated_level=GraduatedLevel.L6,
                reason="unknown_event_type",
            )

        if self._protection_index is not None and operation.target_path:
            try:
                resolved_level = self._protection_index.query(operation.target_path)
                if resolved_level is not None:
                    operation = OperationInfo(
                        operation=operation.operation,
                        target_path=operation.target_path,
                        is_cross_module=operation.is_cross_module,
                        protection_level=resolved_level,
                    )
                    prot_level = resolved_level
            except Exception as e:
                # 5.151.3 修复: protection_level 是安全判决关键输入, 失败后静默吞没并继续走决策树
                # 存在安全风险。记录 warning 使查询失败可见 (不阻断决策, 但留审计痕迹)
                logger.warning("verdict_engine: protection_index.query failed for %s: %s", operation.target_path, e)

        verdict_level, reason = self._apply_decision_tree(actor, operation, gate_passed, violation_count)

        graduated = self.resolve_graduated_level(verdict_level, prot_level, gate_passed, violation_count)
        needs_consensus = self.should_trigger_consensus(verdict_level, prot_level)

        latency = (time.monotonic() - start) * 1000.0

        if verdict_level is VerdictLevel.RED:
            self._red_count += 1
        elif verdict_level is VerdictLevel.YELLOW:
            self._yellow_count += 1
        else:
            self._pass_count += 1

        auth_check = AuthCheckResult(
            gate_passed=gate_passed,
            check_duration_ms=latency,
        )
        response = ResponseInfo(
            verdict=verdict_level,
            graduated_level=graduated,
            reason=reason,
            requires_consensus=needs_consensus,
            latency_ms=latency,
        )
        evidence = EvidenceChain(
            actor=actor,
            operation=operation,
            auth_check=auth_check,
            response=response,
        )

        return Verdict(
            verdict_level=verdict_level,
            graduated_level=graduated,
            protection_level=prot_level,
            gate_passed=gate_passed,
            requires_consensus=needs_consensus,
            evidence=evidence,
            reason=reason,
        )

    def _apply_decision_tree(
        self,
        actor: ActorInfo,
        operation: OperationInfo,
        gate_passed: bool,
        violation_count: int,
    ) -> tuple[VerdictLevel, str]:
        if actor.is_human:
            return VerdictLevel.PASS, "human_actor_auto_pass"

        if operation.is_cross_module:
            return VerdictLevel.RED, "cross_module_blocked"

        if operation.protection_level is ProtectionLevel.anchor:
            return VerdictLevel.RED, "ai_on_anchor_blocked"

        if operation.protection_level is ProtectionLevel.protected:
            if not gate_passed:
                return VerdictLevel.RED, "ai_on_protected_no_gate"
            return VerdictLevel.PASS, "ai_on_protected_gate_passed"

        if operation.protection_level is ProtectionLevel.normal:
            if actor.trust_score < _YELLOW_TRUST_THRESHOLD:
                return VerdictLevel.YELLOW, "low_trust_score"
            if violation_count >= _YELLOW_VIOLATION_THRESHOLD:
                return VerdictLevel.YELLOW, "high_violation_count"
            return VerdictLevel.PASS, "ai_on_normal"

        return VerdictLevel.PASS, "ai_on_public"

    async def evaluate_batch(self, events: list[Any]) -> list[Verdict]:
        if not events:
            return []

        loop = asyncio.get_running_loop()

        async def _eval_one(evt: Any) -> Verdict:
            try:
                return await asyncio.wait_for(
                    self.evaluate(evt),
                    timeout=self._verdict_timeout_s,
                )
            except TimeoutError:
                self._red_count += 1
                return Verdict(
                    verdict_level=VerdictLevel.RED,
                    graduated_level=GraduatedLevel.L6,
                    reason="evaluate_timeout",
                )
            except Exception as exc:
                self._red_count += 1
                return Verdict(
                    verdict_level=VerdictLevel.RED,
                    graduated_level=GraduatedLevel.L6,
                    reason=f"evaluate_error:{exc}",
                )

        tasks = [_eval_one(evt) for evt in events]
        results = await asyncio.gather(*tasks)
        return list(results)

    def resolve_graduated_level(
        self,
        verdict_level: VerdictLevel,
        protection_level: ProtectionLevel,
        gate_passed: bool,
        session_violation_count: int,
    ) -> GraduatedLevel:
        if verdict_level is VerdictLevel.PASS:
            if protection_level is ProtectionLevel.public:
                return GraduatedLevel.L0
            if protection_level is ProtectionLevel.normal:
                return GraduatedLevel.L1
            if protection_level is ProtectionLevel.protected and gate_passed:
                return GraduatedLevel.L2
            return GraduatedLevel.L3

        if verdict_level is VerdictLevel.YELLOW:
            if session_violation_count >= 5:
                return GraduatedLevel.L5
            if session_violation_count >= 3:
                return GraduatedLevel.L4
            return GraduatedLevel.L3

        if verdict_level is VerdictLevel.RED:
            if protection_level is ProtectionLevel.anchor:
                return GraduatedLevel.L6
            if protection_level is ProtectionLevel.protected:
                return GraduatedLevel.L5
            return GraduatedLevel.L4

        return GraduatedLevel.L3

    def should_trigger_consensus(
        self,
        verdict_level: VerdictLevel,
        protection_level: ProtectionLevel,
    ) -> bool:
        if verdict_level is VerdictLevel.RED and protection_level in (
            ProtectionLevel.anchor,
            ProtectionLevel.protected,
        ):
            return True
        if verdict_level is VerdictLevel.YELLOW and protection_level is ProtectionLevel.anchor:
            return True
        return False

    def health_check(self) -> dict[str, Any]:
        # 5.55.4 修复：根据 red_rate 阈值返回降级状态（原硬编码 "healthy"）
        red_rate = round(self._red_count / max(self._eval_count, 1), 4)
        if red_rate >= 0.5:
            status = "unhealthy"
        elif red_rate >= 0.2:
            status = "degraded"
        else:
            status = "healthy"
        return {
            "status": status,
            "total_evaluations": self._eval_count,
            "red_count": self._red_count,
            "yellow_count": self._yellow_count,
            "pass_count": self._pass_count,
            "red_rate": red_rate,
            "has_protection_index": self._protection_index is not None,
            "has_gpu_scheduler": self._gpu_scheduler is not None,
            "verdict_timeout_s": self._verdict_timeout_s,
        }
