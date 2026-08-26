# [BLUEPRINT] MOD-OPS-002 | docs/03_modules/_domain_infrastructure/incident_responder/blueprint.md
# [MODULE] zephyr.infrastructure.system_telemetry.incident_responder
# [DOMAIN] D_OPS
# [DEPENDENCIES] ops_incident_aggregate（OpsIncident/IncidentSeverity 复用）；时钟/处置 handler/升级回调全注入
# [CONSUMERS] 运行时装配批（事件类型策略表绑定 / 升级路由接告警 / 效果统计入面板）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分级词表闭合(P0|P1|P2); 策略表按事件类型闭合（未注册事件类型 Fail-Closed）; 单次处置耗时超 timeout_seconds 判 TIMEOUT 不重试; 失败按 max_attempts 重试；超时/失败必触发升级回调（注入才发）; 处置结果全部回写效果统计; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure/incident_responder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] IncidentResponderError(占位 ZA-OPS-UNREGISTERED-INCIDENT-RESPONDER)——非法分级/空事件类型/非可调用handler/未注册事件类型/非法规则/非法incident时抛
# [TESTS] tests/infrastructure/system_telemetry/test_incident_responder.py
# [A_module] module_id=MOD-OPS-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""IncidentResponder — 事件响应器（MOD-OPS-002）。

B9-11645（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-OPS-002，B9 OPS-03）：
AIOps Detect-Diagnose-Remediate-Learn 闭环——事件分级（P0~P2 词表）+
自动处置策略表（事件类型 → 处置动作 handler 注入）+ 升级规则（超时/失败
升级，注入时钟判超时）+ 处置结果回写学习（结果登记 + 策略效果统计）。

查重分工（蓝图 §0）：ops_incident_aggregate=事件生命周期聚合（本件复用其
OpsIncident/IncidentSeverity 类型，不重建状态机）；本件只做处置执行与学
习统计；处置动作副作用全部经注入 handler，纯内存确定性，同输入必同输出。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

from zephyr.infrastructure.system_telemetry.ops_incident_aggregate import (
    IncidentSeverity,
    OpsIncident,
)

_log = logging.getLogger(__name__)

__all__: Final = [
    "EscalationRule",
    "IncidentResponder",
    "IncidentResponderError",
    "PolicyEffectiveness",
    "RemediationOutcome",
    "ResponseRecord",
]


class IncidentResponderError(Exception):
    """事件响应器输入/规则非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-OPS-UNREGISTERED-INCIDENT-RESPONDER。
    """


class RemediationOutcome(str, Enum):
    """处置结果。"""

    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class EscalationRule:
    """升级规则（按分级配置：重试上限 + 单次超时秒数，frozen）。"""

    max_attempts: int
    timeout_seconds: float


@dataclass(frozen=True)
class ResponseRecord:
    """处置记录（回写学习载体，frozen）。"""

    incident_id: str
    event_type: str
    outcome: RemediationOutcome
    attempts: int
    escalated: bool
    elapsed_seconds: float
    started_at: datetime.datetime
    finished_at: datetime.datetime


@dataclass(frozen=True)
class PolicyEffectiveness:
    """策略效果统计（按事件类型聚合，frozen）。"""

    event_type: str
    responds: int
    attempts: int
    successes: int
    failures: int
    timeouts: int
    escalations: int
    success_rate: float


class IncidentResponder:
    """事件响应器（策略表 + 升级规则 + 效果学习）。"""

    #: 默认升级规则（分级未显式配置时使用）
    DEFAULT_RULE: Final = EscalationRule(max_attempts=1, timeout_seconds=60.0)

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        policies: Mapping[str, Callable[[OpsIncident], bool]] | None = None,
        rules: Mapping[IncidentSeverity, EscalationRule] | None = None,
        escalation_sink: Callable[[OpsIncident, str], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._policies: dict[str, Callable[[OpsIncident], bool]] = {}
        for event_type, handler in (policies or {}).items():
            self.register_policy(event_type, handler)
        self._rules: dict[IncidentSeverity, EscalationRule] = {}
        for severity, rule in (rules or {}).items():
            if not isinstance(severity, IncidentSeverity):
                raise IncidentResponderError(f"非法规则分级: {severity!r}")
            self._validate_rule(rule)
            self._rules[severity] = rule
        self._escalation_sink = escalation_sink
        self._records: list[ResponseRecord] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_rule(rule: EscalationRule) -> None:
        if rule.max_attempts < 1:
            raise IncidentResponderError(f"max_attempts 须 ≥1: {rule.max_attempts}")
        if rule.timeout_seconds <= 0:
            raise IncidentResponderError(
                f"timeout_seconds 须 >0: {rule.timeout_seconds}"
            )

    def _rule_for(self, severity: IncidentSeverity) -> EscalationRule:
        return self._rules.get(severity, self.DEFAULT_RULE)

    # ── 分级 ─────────────────────────────────────────────────────────────

    @staticmethod
    def classify(raw: object) -> IncidentSeverity:
        """分级解析：IncidentSeverity 原样返回；字符串按词表严格匹配。"""
        if isinstance(raw, IncidentSeverity):
            return raw
        if isinstance(raw, str):
            try:
                return IncidentSeverity(raw)
            except ValueError:
                pass
        raise IncidentResponderError(f"非法分级: {raw!r}（词表 P0|P1|P2）")

    # ── 策略表 ───────────────────────────────────────────────────────────

    def register_policy(
        self, event_type: str, handler: Callable[[OpsIncident], bool]
    ) -> None:
        """登记自动处置策略：事件类型 → 处置 handler（注入，返回 True=成功）。"""
        if not event_type:
            raise IncidentResponderError("event_type 为空")
        if not callable(handler):
            raise IncidentResponderError(f"handler 非可调用: {handler!r}")
        self._policies[event_type] = handler

    # ── 处置执行 ─────────────────────────────────────────────────────────

    def respond(self, incident: OpsIncident, event_type: str) -> ResponseRecord:
        """处置：按策略表执行 handler；超时判 TIMEOUT 不重试；失败按规则重试；
        超时/失败触发升级回调；结果回写学习。"""
        if not isinstance(incident, OpsIncident):
            raise IncidentResponderError(f"非法 incident: {type(incident)!r}")
        if not event_type:
            raise IncidentResponderError("event_type 为空")
        handler = self._policies.get(event_type)
        if handler is None:
            raise IncidentResponderError(
                f"未注册事件类型: {event_type!r}（策略表闭合，Fail-Closed）"
            )
        rule = self._rule_for(incident.severity)
        started_at = self._clock()
        elapsed = 0.0
        attempts = 0
        outcome = RemediationOutcome.FAILED
        for _ in range(rule.max_attempts):
            attempts += 1
            t0 = self._clock()
            try:
                ok = bool(handler(incident))
            except Exception:  # noqa: BLE001 — handler 异常按失败处理不抛
                _log.exception("处置 handler 异常: %s/%s", incident.incident_id, event_type)
                ok = False
            t1 = self._clock()
            elapsed += max(0.0, (t1 - t0).total_seconds())
            if (t1 - t0).total_seconds() > rule.timeout_seconds:
                outcome = RemediationOutcome.TIMEOUT
                break
            if ok:
                outcome = RemediationOutcome.SUCCESS
                break
        finished_at = self._clock()

        escalated = False
        if outcome is not RemediationOutcome.SUCCESS and self._escalation_sink is not None:
            reason = (
                f"处置{outcome.value}: incident {incident.incident_id} "
                f"event_type {event_type} attempts {attempts}"
            )
            try:
                self._escalation_sink(incident, reason)
                escalated = True
            except Exception:  # noqa: BLE001 — 升级回调失败不阻断（蓝图 §1）
                _log.exception("escalation_sink 升级失败: %s", incident.incident_id)

        record = ResponseRecord(
            incident_id=incident.incident_id,
            event_type=event_type,
            outcome=outcome,
            attempts=attempts,
            escalated=escalated,
            elapsed_seconds=round(elapsed, 6),
            started_at=started_at,
            finished_at=finished_at,
        )
        self._records.append(record)
        _log.info(
            "处置完成: %s/%s → %s (attempts=%d, escalated=%s)",
            incident.incident_id, event_type, outcome.value, attempts, escalated,
        )
        return record

    # ── 学习（效果统计） ─────────────────────────────────────────────────

    def policy_effectiveness(self, event_type: str) -> PolicyEffectiveness:
        """单事件类型效果统计（无记录 → Fail-Closed）。"""
        rows = [r for r in self._records if r.event_type == event_type]
        if not rows:
            raise IncidentResponderError(f"无处置记录: {event_type!r}")
        successes = sum(1 for r in rows if r.outcome is RemediationOutcome.SUCCESS)
        return PolicyEffectiveness(
            event_type=event_type,
            responds=len(rows),
            attempts=sum(r.attempts for r in rows),
            successes=successes,
            failures=sum(1 for r in rows if r.outcome is RemediationOutcome.FAILED),
            timeouts=sum(1 for r in rows if r.outcome is RemediationOutcome.TIMEOUT),
            escalations=sum(1 for r in rows if r.escalated),
            success_rate=round(successes / len(rows), 6),
        )

    def effectiveness_table(self) -> list[PolicyEffectiveness]:
        """全策略效果表（按 event_type 确定性排序）。"""
        return [
            self.policy_effectiveness(et)
            for et in sorted({r.event_type for r in self._records})
        ]

    def records(self) -> list[ResponseRecord]:
        """全量处置记录（按处置发生顺序，确定性）。"""
        return list(self._records)
