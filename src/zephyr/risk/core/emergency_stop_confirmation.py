# [BLUEPRINT] MOD-RK-36 | docs/03_modules/_domain_risk/emergency_stop_confirmation/blueprint.md
# [MODULE] zephyr.risk.core.emergency_stop_confirmation
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.intelligence.venra_double_lock_anchor(MOD-INF-049); zephyr.shared.foundation.errors
# [CONSUMERS] 编排层(紧急停止/强平执行前门禁); D_GOV_AUDIT(确认留痕消费); MOD-INF-016 trading_kill_switch(放行后执行体)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 动作白名单仅EMERGENCY_STOP/FORCED_LIQUIDATION; 提案人/确认人均须在授权名册(Fail-Closed); 两名不同操作人approve才confirmed放行; 任一reject即rejected终态; 留痕=理由+payload哈希入MOD-INF-049锚定链(只追加可离线校验); 空理由/未授权/未知提案不放行
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EmergencyStopConfirmationError; VenraDoubleLockError(透传)
# [TESTS] tests/risk/core/test_emergency_stop_confirmation.py
# [A_module] module_id=MOD-RK-36 | layer=module | stability=evolving | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""Emergency Stop Confirmation — 紧急停止安全确认 (MOD-RK-36, CAND-RSK-039 / D-RISK-115)

kill switch 本体（MOD-INF-016）已建；本模块补齐**紧急操作二次确认与不可篡改
留痕**缺口：紧急停止（EMERGENCY_STOP）与强制平仓（FORCED_LIQUIDATION）类高危
操作，必须两名不同授权操作人双锁确认才放行，全程留痕入哈希链可离线校验。

复用优先：双锁与锚定链唯一机制真源 = MOD-INF-049 VenraDoubleLockAnchor（本模块
不重造），其上只加风险域应用层语义：

  1. 动作白名单：仅 EMERGENCY_STOP / FORCED_LIQUIDATION 可提案；
  2. 身份核验：提案人/确认人均须在授权名册（构造注入，空名册 Fail-Closed 全拒）；
  3. 放行语义：confirmed → released=True（编排层方可执行），rejected/pending 不放行；
  4. 留痕导出：audit_trail() 把锚定记录展开为含 action_type/operator/reason/
     payload_hash/lockers/decision 的明文台账（payload 明文不出域，仅哈希入链），
     verify_audit_trail() 委托锚定链离线校验（D_GOV_AUDIT 消费）。

纪律：本模块只做确认门禁与留痕，不执行任何停止/平仓动作（执行归编排层+
MOD-INF-016）；与 scripts/deadman_switch.ps1 的联动演练留 Owner 窗口。
依据: blueprint.md（MOD-RK-36）§3 核心规则；蓝图 MOD-INF-001 §30.1.5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 紧急操作提案
#   fields: action_type(白名单枚举) + operator(授权名册内) + reason(非空) + payload(操作参数,仅哈希入链)
#   code: propose() 参数
# - id: I2
#   name: 确认动作
#   fields: request_id + actor(授权名册内,与已锁人不同) + approve
#   code: confirm() 参数
# - id: I3
#   name: 授权名册
#   fields: authorized_operators(构造注入 frozenset, 空=Fail-Closed)
#   code: EmergencyStopConfirmation.__init__
# 层: 算法
# - id: A1
#   name_zh: ① 白名单+身份核验
#   name_en: _check_operator
#   intro: 非白名单动作/空operator/不在名册 → EmergencyStopConfirmationError
# - id: A2
#   name_zh: ② 双锁确认委托
#   name_en: confirm
#   intro: MOD-INF-049 propose/lock; 两不同actor approve→confirmed(released), 任一reject→rejected
# - id: A3
#   name_zh: ③ 留痕导出台账化
#   name_en: audit_trail
#   intro: 锚定记录展开为 action_type/operator/reason/payload_hash/lockers/decision 明文台账
# 层: 输出
# - id: O1
#   name: EmergencyActionRequest
#   fields: request_id/action_type/operator/reason/payload_hash
# - id: O2
#   name: ConfirmationVerdict
#   fields: decision(pending/confirmed/rejected) + released(仅confirmed=True)
# 边:
# I1 --> A1
# I3 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> O1
# A2 --> O2
# A2 --> A3
# [/ALGO_FLOW]
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.intelligence.venra_double_lock_anchor import VenraDoubleLockAnchor
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ConfirmationVerdict",
    "EmergencyActionRequest",
    "EmergencyActionType",
    "EmergencyStopConfirmation",
    "EmergencyStopConfirmationError",
]


class EmergencyStopConfirmationError(ZephyrBaseError):
    """紧急停止安全确认非法（白名单外动作/未授权操作人/空理由，Fail-Closed）。"""


class EmergencyActionType(str, Enum):
    """紧急操作白名单。"""

    EMERGENCY_STOP = "EMERGENCY_STOP"  # 紧急停止（全部交易活动 halt）
    FORCED_LIQUIDATION = "FORCED_LIQUIDATION"  # 强制平仓


@dataclass(frozen=True)
class EmergencyActionRequest:
    """紧急操作提案凭据。"""

    request_id: str
    action_type: EmergencyActionType
    operator: str
    reason: str
    payload_hash: str


@dataclass(frozen=True)
class ConfirmationVerdict:
    """一次确认动作后的裁定。"""

    decision: str  # "pending" | "confirmed" | "rejected"
    released: bool  # 仅 confirmed → True（编排层放行凭据）


class EmergencyStopConfirmation:
    """紧急停止/强平双锁二次确认门禁（MOD-INF-049 风险域应用层封装）。"""

    def __init__(self, *, authorized_operators: frozenset[str]) -> None:
        roster = frozenset(str(op) for op in authorized_operators if str(op).strip())
        if not roster:
            raise EmergencyStopConfirmationError("授权名册为空（Fail-Closed：无授权操作人即全拒）")
        self._roster: Final = roster
        self._anchor = VenraDoubleLockAnchor()
        self._seq = itertools.count(1)
        self._meta: dict[
            str, tuple[EmergencyActionType, str, str, str]
        ] = {}  # request_id → (action_type, operator, reason, payload_hash)

    # ── 提案 ─────────────────────────────────────────────────────────

    def propose(
        self,
        action_type: EmergencyActionType,
        *,
        operator: str,
        reason: str,
        payload: object = None,
    ) -> EmergencyActionRequest:
        """登记紧急操作提案（白名单+身份核验，Fail-Closed）。

        Raises:
            EmergencyStopConfirmationError: 动作非白名单/操作人未授权/理由为空
            VenraDoubleLockError: request_id 冲突（理论上自增不撞，透传防御）
        """
        if not isinstance(action_type, EmergencyActionType):
            raise EmergencyStopConfirmationError(f"动作非白名单枚举: {action_type!r}")
        self._check_operator(operator)
        if not reason or not str(reason).strip():
            raise EmergencyStopConfirmationError("紧急操作理由不得为空（留痕强制）")

        request_id = f"EMG-{action_type.value}-{next(self._seq):06d}"
        change = self._anchor.propose(
            request_id,
            target=action_type.value,
            payload={"reason": reason, "payload": payload},
            proposer=operator,
        )
        self._meta[request_id] = (action_type, operator, reason, change.payload_hash)
        return EmergencyActionRequest(
            request_id=request_id,
            action_type=action_type,
            operator=operator,
            reason=reason,
            payload_hash=change.payload_hash,
        )

    # ── 双锁确认 ─────────────────────────────────────────────────────

    def confirm(self, request_id: str, *, actor: str, approve: bool) -> ConfirmationVerdict:
        """对提案加锁确认。两名不同授权操作人 approve → confirmed 放行。

        Raises:
            EmergencyStopConfirmationError: 确认人未授权
            VenraDoubleLockError: 未知提案/同人重复/终态后操作（MOD-INF-049 透传）
        """
        self._check_operator(actor)
        decision = self._anchor.lock(request_id, actor=actor, approve=approve)
        return ConfirmationVerdict(decision=decision, released=decision == "confirmed")

    def is_released(self, request_id: str) -> bool:
        """提案是否已 confirmed 放行。"""
        return self._anchor.is_confirmed(request_id)

    # ── 留痕导出 ─────────────────────────────────────────────────────

    def audit_trail(self) -> list[dict]:
        """确认留痕台账（终态记录全量，payload 明文不出域仅哈希）。"""
        trail: list[dict] = []
        for rec in self._anchor.anchor_chain():
            action_type, operator, reason, payload_hash = self._meta.get(
                rec.change_id, (EmergencyActionType.EMERGENCY_STOP, "", "", "")
            )
            trail.append(
                {
                    "seq": rec.seq,
                    "request_id": rec.change_id,
                    "action_type": action_type.value,
                    "operator": operator,
                    "reason": reason,
                    "payload_hash": payload_hash,
                    "lockers": rec.lockers,
                    "decision": rec.decision,
                    "prev_hash": rec.prev_hash,
                    "record_hash": rec.record_hash,
                }
            )
        return trail

    def verify_audit_trail(self) -> bool:
        """离线校验留痕哈希链完整性（任一记录被篡改即 False）。"""
        return self._anchor.verify_chain()

    # ── 内部 ─────────────────────────────────────────────────────────

    def _check_operator(self, operator: str) -> None:
        if not operator or not str(operator).strip():
            raise EmergencyStopConfirmationError("操作人不得为空（身份核验 Fail-Closed）")
        if operator not in self._roster:
            raise EmergencyStopConfirmationError(f"操作人 {operator!r} 不在授权名册（Fail-Closed 拒绝）")
