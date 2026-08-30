# [BLUEPRINT] MOD-AU-013 | docs/03_modules/_domain_autonomy_core/ai_ops_autonomy_card/blueprint.md
# [MODULE] zephyr.autonomy_core.ai_ops_autonomy_card
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 运行时装配批（7类检测源事件接入 / process_supervisor 修复执行体 / 健康度回读装配 / D_GOV_AUDIT 运维审计落账）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] evaluate/evaluate_post_repair 判定纯函数无IO; 运维事件与卡配置非法 Fail-Closed; B-014/015/016 禁区硬编码（交易时段命中必 ESCALATE_HUMAN，卡级别不可抬升绕过）; 不可逆策略或无 restore 快照必人工（TNR）; 策略分级超卡分级必人工; 修复/回滚仅产信号（执行委托 process_supervisor 等存量）; 回调/sink 异常不阻断判定; 决策与执行双审计记录
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_core/ai_ops_autonomy_card/blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidOpsIncidentError; InvalidAutonomyCardConfigError
# [TESTS] tests/autonomy/test_ai_ops_autonomy_card.py
# [A_module] module_id=MOD-AU-013 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""



AiOpsAutonomyCard — C-008 AI 自治运维能力卡片 (MOD-AU-013)

B14-04565（AUD-DRAFT-001-DIGEST P1 波 W-P1-12，A9 §3.5 / A1§12.2 迁移）：
自监控→自诊断→自修复→自保障（Learn）四阶段闭环的**运维自治判定核心**——
7 类检测源事件 → 四路诊断（规则/关联/LLM/因果）→ AUT-001~008 修复策略库
（A-L1~L4 分级）→ TNR 可撤销修复（restore 快照 + 恶化自动回滚）→ 故障模式
库 Learn（未知动作 OBSERVE + learn_candidate 审计）。

禁区硬编码（跨模块约束，卡级别抬升也不可绕过）：交易时段命中
B-014（禁AI自动重启核心进程）/B-015（禁AI自动升级依赖库）/
B-016（禁AI自动清理未归档交易日志审计）动作 → 必 ESCALATE_HUMAN。

查重分工（W-P1-12 探查结论，均不复制）：
- capability_card（MOD-INF-035）：能力卡数据模型（pydantic schema 族），
  本卡为其业务实例的判定核心；
- autonomy_level_registry（MOD-AU-005）：Agent 角色四级自治（L0~L3），
  本卡 A-L1~L4 为**运维动作**分级，对齐不复制；
- self_diagnosis（MOD-FEEDBACK_LOOP）：策略/信号层自诊断（诊断路委托面）；
- auto_fix_engine（infrastructure）：开发侧代码自愈，不管交易运行时；
- process_supervisor（MOD-INF-066）：进程守护执行体（repair_sink 委托）；
- health_monitor（trading）：健康监控散件（检测源之一）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: grade 参数
#   fields: 参数 grade（无注解）
#   code: ai_ops_autonomy_card.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: repair_sink 参数
#   fields: 参数 repair_sink（无注解）
#   code: ai_ops_autonomy_card.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: rollback_trigger 参数
#   fields: 参数 rollback_trigger（无注解）
#   code: ai_ops_autonomy_card.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: audit_sink 参数
#   fields: 参数 audit_sink（无注解）
#   code: ai_ops_autonomy_card.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AiOpsAutonomyCard
#   name_en: AiOpsAutonomyCard
#   intro: C-008 AI 自治运维能力卡片（判定纯函数 + 信号回调委托）。
#   desc: C-008 AI 自治运维能力卡片（判定纯函数 + 信号回调委托）。 Args: grade: 卡当前自治分级（默认 A_L2；禁区硬编码不受其抬升影响）。 repair_sin…；公共方法（定义序）: grade,…
#   inputs: grade repair_sink rollback_trigger audit_sink
#   outputs: 返回值
#   （注：A1 之后另有 10 个公共定义未列入（含 10 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（11 定义）
#   name_en: public defs
#   intro: AiOpsAutonomyCard
#   downstream: 运行时装配批（7类检测源事件接入 / process_supervisor 修复执行体 / 健康度回读装配 / D_GOV_AUDIT 运维审计落账）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "CAPABILITY_CARD",
    "FORBIDDEN_ZONES",
    "REPAIR_STRATEGIES",
    "AiOpsAutonomyCard",
    "AutonomyGrade",
    "DetectorSource",
    "DiagnosisRoute",
    "ForbiddenZone",
    "InvalidAutonomyCardConfigError",
    "InvalidOpsIncidentError",
    "OpsIncident",
    "RemediateAction",
    "RemediateVerdict",
    "RepairStrategy",
]

_VALID_SEVERITIES: Final[frozenset[str]] = frozenset({"P1", "P2", "P3"})


class InvalidOpsIncidentError(ZephyrBaseError):
    """运维事件非法（Fail-Closed：脏事件不参与判定）。"""


class InvalidAutonomyCardConfigError(ZephyrBaseError):
    """自治运维卡配置非法。"""


class DetectorSource(str, Enum):
    """7 类检测源（A1§12.2）。"""

    PROCESS_HEALTH = "process_health"
    METRIC_ANOMALY = "metric_anomaly"
    LOG_ERROR = "log_error"
    DLQ_BACKLOG = "dlq_backlog"
    LATENCY_SLO = "latency_slo"
    DATA_STALENESS = "data_staleness"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class DiagnosisRoute(str, Enum):
    """四路诊断。"""

    RULE = "rule"
    CORRELATION = "correlation"
    LLM = "llm"
    CAUSAL = "causal"


class AutonomyGrade(IntEnum):
    """运维动作自治分级（A-L1~L4）。"""

    A_L1 = 1  # 观察建议
    A_L2 = 2  # 可逆修复自动
    A_L3 = 3  # 受限自动
    A_L4 = 4  # 全权自动（仍受禁区硬编码约束）


class ForbiddenZone(str, Enum):
    """跨模块禁区（硬编码，不可配置）。"""

    B_014 = "B-014"  # 禁AI自动重启交易时段核心进程
    B_015 = "B-015"  # 禁AI自动升级交易时段依赖库
    B_016 = "B-016"  # 禁AI自动清理未归档交易日志审计


#: 禁区 → 动作标签集（硬编码；交易时段命中必 ESCALATE_HUMAN）
FORBIDDEN_ZONES: Final[dict[ForbiddenZone, tuple[str, ...]]] = {
    ForbiddenZone.B_014: ("restart_core_process", "kill_core_process"),
    ForbiddenZone.B_015: ("upgrade_dependency",),
    ForbiddenZone.B_016: ("purge_unarchived_logs", "delete_unarchived_audit"),
}


class RemediateVerdict(str, Enum):
    """修复裁决。"""

    EXECUTE_REPAIR = "execute_repair"  # 分级达标 + TNR 满足 → 自动修复（信号）
    ESCALATE_HUMAN = "escalate_human"  # 禁区/超分级/TNR 不满足 → 人工
    ROLLBACK = "rollback"  # 修复后健康度恶化 → 自动回滚（信号）
    OBSERVE = "observe"  # 未知动作观察 + Learn / 修复后稳定


@dataclass(frozen=True)
class RepairStrategy:
    """修复策略（frozen；AUT-001~008 策略库条目）。"""

    strategy_id: str
    name: str
    grade: AutonomyGrade
    reversible: bool
    action_tags: tuple[str, ...]


#: AUT-001~008 修复策略库（A1§12.2 迁移；TNR：可逆性为硬属性）
REPAIR_STRATEGIES: Final[tuple[RepairStrategy, ...]] = (
    RepairStrategy("AUT-001", "核心进程守护拉起", AutonomyGrade.A_L2, True, ("restart_core_process",)),
    RepairStrategy("AUT-002", "DLQ 重放", AutonomyGrade.A_L2, True, ("dlq_replay",)),
    RepairStrategy("AUT-003", "缓存失效重建", AutonomyGrade.A_L1, True, ("cache_rebuild",)),
    RepairStrategy("AUT-004", "只读副本切换", AutonomyGrade.A_L3, True, ("readonly_failover",)),
    RepairStrategy("AUT-005", "依赖版本回滚", AutonomyGrade.A_L3, True, ("dependency_rollback",)),
    RepairStrategy("AUT-006", "日志归档迁移", AutonomyGrade.A_L2, True, ("log_archive",)),
    RepairStrategy("AUT-007", "只读 Worker 扩容", AutonomyGrade.A_L3, True, ("scale_readonly_worker",)),
    RepairStrategy("AUT-008", "不可逆 Schema 迁移", AutonomyGrade.A_L4, False, ("schema_migrate",)),
)

#: C-008 能力卡声明（A1§12.2 迁移；B-014/015/016 禁区硬编码）
CAPABILITY_CARD: Final[dict[str, Any]] = {
    "card_id": "C-008",
    "name": "AI自治运维能力卡片",
    "source": "A1§12.2迁移（B14-04565，AUD-DRAFT-001-DIGEST P1 波 W-P1-12）",
    "closed_loop": ["detect", "diagnose", "remediate", "learn"],
    "detector_sources": [s.value for s in DetectorSource],
    "diagnosis_routes": [r.value for r in DiagnosisRoute],
    "repair_strategies": [s.strategy_id for s in REPAIR_STRATEGIES],
    "forbidden_zones": {
        "B-014": "禁AI自动重启交易时段核心进程",
        "B-015": "禁AI自动升级交易时段依赖库",
        "B-016": "禁AI自动清理未归档交易日志审计",
    },
    "tnr": "修复必须携带 restore 快照；修复后健康度恶化自动回滚（TNR 事务性无回归）",
    "boundary": "C-008=运行时保障（不崩溃） vs C-023=性能优化（跑更快）",
}


@dataclass(frozen=True)
class OpsIncident:
    """运维事件（检测源装配注入）。"""

    incident_id: str
    source: DetectorSource
    action_tag: str
    severity: str  # P1/P2/P3
    in_trading_session: bool
    snapshot_ref: str  # restore 快照引用（空=无快照，TNR 不满足）
    diagnosis_route: DiagnosisRoute


@dataclass(frozen=True)
class RemediateAction:
    """修复裁决结果（frozen；含策略/理由/信号达成标记/审计记录）。"""

    verdict: RemediateVerdict
    strategy_id: str
    reason: str
    restore_snapshot_ref: str
    rollback_signaled: bool
    audit_records: tuple[dict[str, Any], ...]


def _validate_incident(incident: OpsIncident) -> tuple[DetectorSource, DiagnosisRoute]:
    """运维事件 Fail-Closed 校验，返回归一化 (source, route)。"""
    if not isinstance(incident.incident_id, str) or not incident.incident_id.strip():
        raise InvalidOpsIncidentError("incident_id 不能为空", details={"incident_id": incident.incident_id})
    try:
        source = (
            incident.source if isinstance(incident.source, DetectorSource) else DetectorSource(str(incident.source))
        )
    except (ValueError, TypeError) as exc:
        raise InvalidOpsIncidentError(
            "source 非法（7 类检测源之外）", details={"source": str(incident.source)}
        ) from exc
    try:
        route = (
            incident.diagnosis_route
            if isinstance(incident.diagnosis_route, DiagnosisRoute)
            else DiagnosisRoute(str(incident.diagnosis_route))
        )
    except (ValueError, TypeError) as exc:
        raise InvalidOpsIncidentError(
            "diagnosis_route 非法（四路诊断之外）",
            details={"diagnosis_route": str(incident.diagnosis_route)},
        ) from exc
    if incident.severity not in _VALID_SEVERITIES:
        raise InvalidOpsIncidentError("severity 非法（仅 P1/P2/P3）", details={"severity": incident.severity})
    if not isinstance(incident.action_tag, str) or not incident.action_tag.strip():
        raise InvalidOpsIncidentError("action_tag 不能为空", details={"action_tag": incident.action_tag})
    return source, route


def _match_forbidden_zone(action_tag: str) -> ForbiddenZone | None:
    for zone, tags in FORBIDDEN_ZONES.items():
        if action_tag in tags:
            return zone
    return None


def _select_strategy(action_tag: str) -> RepairStrategy | None:
    for strategy in REPAIR_STRATEGIES:
        if action_tag in strategy.action_tags:
            return strategy
    return None


class AiOpsAutonomyCard:
    """C-008 AI 自治运维能力卡片（判定纯函数 + 信号回调委托）。

    Args:
        grade: 卡当前自治分级（默认 A_L2；禁区硬编码不受其抬升影响）。
        repair_sink: 修复执行回调 ``(incident, strategy) -> None``（执行委托
            process_supervisor 等存量；异常不阻断判定）。
        rollback_trigger: 回滚信号回调 ``(incident, strategy) -> None``
            （TNR 恶化自动回滚；异常不阻断判定）。
        audit_sink: 审计记录回调（运维审计委托 D_GOV_AUDIT；异常不阻断）。
    """

    def __init__(
        self,
        grade: AutonomyGrade = AutonomyGrade.A_L2,
        repair_sink: Callable[[OpsIncident, RepairStrategy], None] | None = None,
        rollback_trigger: Callable[[OpsIncident, RepairStrategy | None], None] | None = None,
        audit_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        try:
            self._grade = grade if isinstance(grade, AutonomyGrade) else AutonomyGrade(int(grade))
        except (ValueError, TypeError) as exc:
            raise InvalidAutonomyCardConfigError("grade 非法（仅 A_L1~A_L4）", details={"grade": str(grade)}) from exc
        self._repair_sink = repair_sink
        self._rollback_trigger = rollback_trigger
        self._audit_sink = audit_sink

    @property
    def grade(self) -> AutonomyGrade:
        return self._grade

    @property
    def card(self) -> dict[str, Any]:
        return CAPABILITY_CARD

    def evaluate(self, incident: OpsIncident) -> RemediateAction:
        """修复裁决（纯函数）：禁区 → 策略匹配 → TNR → 分级 → EXECUTE/ESCALATE/OBSERVE。"""
        source, route = _validate_incident(incident)
        strategy = _select_strategy(incident.action_tag)

        # ① 禁区硬编码：交易时段命中必人工（卡级别不可抬升绕过）
        zone = _match_forbidden_zone(incident.action_tag)
        if zone is not None and incident.in_trading_session:
            return self._finalize(
                incident,
                RemediateVerdict.ESCALATE_HUMAN,
                strategy,
                f"禁区 {zone.value} 硬编码（{CAPABILITY_CARD['forbidden_zones'][zone.value]}）："
                "交易时段禁止 AI 自动执行，强制人工",
                extra_audit="escalate",
            )

        # ② 未知动作 → OBSERVE + 故障模式库 Learn 候选
        if strategy is None:
            return self._finalize(
                incident,
                RemediateVerdict.OBSERVE,
                None,
                f"动作 {incident.action_tag} 无匹配修复策略，观察并入故障模式库 Learn 候选",
                extra_audit="learn_candidate",
            )

        # ③ TNR：不可逆策略任何级别必人工
        if not strategy.reversible:
            return self._finalize(
                incident,
                RemediateVerdict.ESCALATE_HUMAN,
                strategy,
                f"策略 {strategy.strategy_id}（{strategy.name}）不可逆，TNR 可撤销修复不满足，任何自治级别均人工",
                extra_audit="escalate",
            )

        # ④ TNR：无 restore 快照不得自动执行
        if not incident.snapshot_ref.strip():
            return self._finalize(
                incident,
                RemediateVerdict.ESCALATE_HUMAN,
                strategy,
                "无 restore 快照引用，TNR 可撤销修复无法保证，转人工",
                extra_audit="escalate",
            )

        # ⑤ 自治分级门禁：策略分级超卡分级 → 人工
        if int(strategy.grade) > int(self._grade):
            return self._finalize(
                incident,
                RemediateVerdict.ESCALATE_HUMAN,
                strategy,
                f"策略 {strategy.strategy_id} 分级 L{int(strategy.grade)} 超卡分级 L{int(self._grade)}，转人工",
                extra_audit="escalate",
            )

        # ⑥ 自动修复（信号；执行委托 repair_sink）
        if self._repair_sink is not None:
            try:
                self._repair_sink(incident, strategy)
            except Exception:  # noqa: BLE001 - 回调异常不阻断判定
                _logger.warning("repair_sink 回调异常（不阻断判定）", exc_info=True)
        return self._finalize(
            incident,
            RemediateVerdict.EXECUTE_REPAIR,
            strategy,
            f"分级达标（L{int(strategy.grade)}≤L{int(self._grade)}）且 TNR 满足"
            f"（快照 {incident.snapshot_ref}），自动修复 {strategy.strategy_id}",
            extra_audit="repair_execute",
        )

    def evaluate_post_repair(self, incident: OpsIncident, health_delta: float) -> RemediateAction:
        """修复后评估（纯函数）：健康度恶化（delta<0）→ ROLLBACK 信号，否则 OBSERVE。"""
        _validate_incident(incident)
        strategy = _select_strategy(incident.action_tag)
        if float(health_delta) < 0.0:
            signaled = False
            if self._rollback_trigger is not None:
                try:
                    self._rollback_trigger(incident, strategy)
                    signaled = True
                except Exception:  # noqa: BLE001 - 回调异常不阻断判定
                    _logger.warning("rollback_trigger 回调异常（不阻断判定）", exc_info=True)
            action = self._finalize(
                incident,
                RemediateVerdict.ROLLBACK,
                strategy,
                f"修复后健康度恶化（delta={float(health_delta)}），TNR 自动回滚",
                extra_audit="rollback",
            )
            # rollback_signaled 如实记录（finalize 默认 False，此处重建）
            return RemediateAction(
                verdict=action.verdict,
                strategy_id=action.strategy_id,
                reason=action.reason,
                restore_snapshot_ref=action.restore_snapshot_ref,
                rollback_signaled=signaled,
                audit_records=action.audit_records,
            )
        return self._finalize(
            incident,
            RemediateVerdict.OBSERVE,
            strategy,
            f"修复后健康度未恶化（delta={float(health_delta)}），巩固观察",
            extra_audit="post_repair_observe",
        )

    def _finalize(
        self,
        incident: OpsIncident,
        verdict: RemediateVerdict,
        strategy: RepairStrategy | None,
        reason: str,
        extra_audit: str,
    ) -> RemediateAction:
        audit_records: list[dict[str, Any]] = [
            {
                "kind": "remediate_decision",
                "incident_id": incident.incident_id,
                "action_tag": incident.action_tag,
                "verdict": verdict.value,
                "strategy_id": strategy.strategy_id if strategy else "",
                "reason": reason,
            },
            {
                "kind": extra_audit,
                "incident_id": incident.incident_id,
                "strategy_id": strategy.strategy_id if strategy else "",
            },
        ]
        if self._audit_sink is not None:
            for audit in audit_records:
                try:
                    self._audit_sink(audit)
                except Exception:  # noqa: BLE001 - sink 异常不阻断判定
                    _logger.warning("audit_sink 回调异常（不阻断判定）", exc_info=True)
        return RemediateAction(
            verdict=verdict,
            strategy_id=strategy.strategy_id if strategy else "",
            reason=reason,
            restore_snapshot_ref=incident.snapshot_ref,
            rollback_signaled=False,
            audit_records=tuple(audit_records),
        )
