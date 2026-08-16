# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.paper_live_transition
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.__init__; zephyr.governance.lifecycle_governance.rollback_state_machine
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] TransitionPhase order: PARALLEL→SHADOW→GRAY_RAMP;valid_transition only sequential;晋级前置当前降级姿态须为NORMAL(#ARCH-QUANT-003两机唯一耦合点)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PermissionError(晋级时降级姿态非NORMAL)
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""三阶段迁移门禁（PARALLEL/SHADOW/GRAY_RAMP）+ 晋级前置降级姿态校验。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 阶段晋级请求
#   fields: from_phase/to_phase（TransitionPhase 枚举）
#   code: valid_transition(from_phase, to_phase)
# - id: I2
#   name: 当前降级姿态
#   fields: RollbackState 五态（NORMAL/THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING）
#   code: check_promotion_allowed(posture)
# 层: 算法
# - id: A1
#   name_zh: ① 不可跳级校验
#   name_en: valid_transition sequential check
#   intro: 只允许顺序 next（to_idx == from_idx + 1），不可跳 Phase
#   desc: PHASE_ORDER 索引差判定；get_next_phase 返回顺序下一阶或 None
#   inputs: I1
#   outputs: bool / 下一 Phase
#   invariant: TransitionPhase order 恒为 PARALLEL→SHADOW→GRAY_RAMP
# - id: A2
#   name_zh: ② 晋级前置降级姿态校验
#   name_en: check_promotion_allowed posture gate
#   intro: 当前降级姿态非 NORMAL → PermissionError 拒绝晋级（两机唯一耦合点，#ARCH-QUANT-003）
#   desc: posture != RollbackState.NORMAL → raise PermissionError；姿态读取走 rollback_state_machine.load_persisted_state（fail-closed）
#   inputs: I2
#   outputs: None（通过）/ PermissionError（拒绝）
#   invariant: 降级中（THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING）禁止晋级
# 层: 输出
# - id: O1
#   name_zh: 晋级裁决与迁移状态
#   name_en: promotion verdict + TransitionState
#   intro: 晋级通过后经 get_next_phase 推进并持久化 TransitionState（审计凭证）
#   downstream: 53 号 memo §3.6 晋级仪式（首批策略进 SHADOW 阶段接线）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# A1 --> O1
# A2 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Final

from pydantic import BaseModel, Field

from zephyr.governance.lifecycle_governance.rollback_state_machine import RollbackState


class TransitionPhase(str, Enum):
    PARALLEL = "PARALLEL"
    SHADOW = "SHADOW"
    GRAY_RAMP = "GRAY_RAMP"


class PhaseSpec(BaseModel):
    phase: TransitionPhase
    name: str
    duration_days: int
    description: str
    key_gates: list[str] = Field(default_factory=list)


PHASE_SPECS: Final[dict[TransitionPhase, PhaseSpec]] = {
    TransitionPhase.PARALLEL: PhaseSpec(
        phase=TransitionPhase.PARALLEL,
        name="并行运行",
        duration_days=30,
        description="Paper与Live并行运行30天，比较所有信号与执行质量",
        key_gates=["paper_live_signal_match >= 99.9%", "slippage_diff < 1bp", "fill_rate >= 99%"],
    ),
    TransitionPhase.SHADOW: PhaseSpec(
        phase=TransitionPhase.SHADOW,
        name="影子账户",
        duration_days=14,
        description="以小额真实资金运行影子账户，验证执行链路与结算",
        key_gates=["shadow_pnl_correlation >= 0.95", "settlement_match 100%", "latency < 100ms"],
    ),
    TransitionPhase.GRAY_RAMP: PhaseSpec(
        phase=TransitionPhase.GRAY_RAMP,
        name="灰度上线",
        duration_days=30,
        description="逐级放大(1%->5%->20%->50%->100%)至全量",
        key_gates=["drawdown < 1% per ramp step", "no circuit_breaker triggers", "daily_loss < 3%"],
    ),
}

PHASE_ORDER: Final[dict[TransitionPhase, int]] = {
    TransitionPhase.PARALLEL: 0,
    TransitionPhase.SHADOW: 1,
    TransitionPhase.GRAY_RAMP: 2,
}


def get_phase_spec(phase: TransitionPhase) -> PhaseSpec | None:
    return PHASE_SPECS.get(phase)


def valid_transition(from_phase: TransitionPhase, to_phase: TransitionPhase) -> bool:
    """检查是否可跳Phase——不可跳, 只允许顺序next。"""
    from_idx = PHASE_ORDER.get(from_phase, -1)
    to_idx = PHASE_ORDER.get(to_phase, -1)
    return to_idx == from_idx + 1


def get_next_phase(current: TransitionPhase) -> TransitionPhase | None:
    phases = list(TransitionPhase)
    idx = phases.index(current) if current in phases else -1
    if idx + 1 < len(phases):
        return phases[idx + 1]
    return None


def check_promotion_allowed(posture: RollbackState) -> None:
    """阶段晋级前置校验：当前降级姿态须为 NORMAL。

    #ARCH-QUANT-003 裁定两机唯一耦合点（53 号 §3.6 晋级条件）：降级中
    （THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING）禁止晋级；其余时间两机独立。
    姿态读取走 rollback_state_machine.load_persisted_state（fail-closed——
    读取失败按 SOFT_HALT 处理即禁止晋级，停错代价 < 放错代价）。

    Raises:
        PermissionError: 降级姿态非 NORMAL，禁止晋级。
    """
    if posture != RollbackState.NORMAL:
        raise PermissionError(
            f"降级姿态={posture.value}，禁止晋级（须 NORMAL；"
            f"#ARCH-QUANT-003 两机唯一耦合点，53 号 §3.6）"
        )


class TransitionState(BaseModel):
    current_phase: TransitionPhase
    started_at: str
    completed_at: str | None = None
    ramping_percentage: float = 0.0

    @property
    def elapsed_days(self) -> float:
        started = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        return (now - started).total_seconds() / 86400.0

    def ramp_up(self, step_percent: float) -> float:
        self.ramping_percentage = min(100.0, self.ramping_percentage + step_percent)
        return self.ramping_percentage


def create_transition_state() -> TransitionState:
    return TransitionState(
        current_phase=TransitionPhase.PARALLEL,
        started_at=datetime.now(UTC).isoformat(),
        ramping_percentage=0.0,
    )
