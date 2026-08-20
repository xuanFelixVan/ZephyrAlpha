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
# [ERROR_CONTRACT] PermissionError(晋级时降级姿态非NORMAL);ValueError(GateThresholds配置越界)
# [TESTS] tests/governance/trading/test_paper_live_transition.py
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

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Final

from pydantic import BaseModel, Field

from zephyr.governance.lifecycle_governance.rollback_state_machine import RollbackState


class TransitionPhase(str, Enum):
    PARALLEL = "PARALLEL"
    SHADOW = "SHADOW"
    GRAY_RAMP = "GRAY_RAMP"


@dataclass(frozen=True)
class GateThresholds:
    """迁移门禁阈值/观察期/灰度顺序配置(不可变, 53号§6 校准配置化落地)

    机制初始值未经实盘校准(53号 §6 待裁定"门禁阈值校准"行)——首批策略迁移
    各阶段数据累积后, 通过构造新 GateThresholds 实例校准, 禁止改码内字面量。
    默认值与既有 PHASE_SPECS key_gates/duration_days 逐字一致(不破坏既有行为)。

    Attributes:
        parallel_min_days: PARALLEL 机制最小天数(默认30)
        shadow_min_days: SHADOW 机制最小天数(默认14)
        gray_ramp_min_days: GRAY_RAMP 机制最小天数(默认30)
        signal_match_min: 信号一致性下限(默认0.999)
        slippage_diff_max_bp: 滑点偏差上限(默认1.0bp)
        fill_rate_min: 成交率下限(默认0.99)
        shadow_pnl_correlation_min: 影子PnL相关下限(默认0.95)
        settlement_match_min: 结算一致率下限(默认1.0)
        latency_max_ms: 执行时延上限(默认100ms)
        ramp_drawdown_max: 每级 ramp 回撤上限(默认0.01)
        ramp_daily_loss_max: 每级 ramp 日亏损上限(默认0.03)
        ramp_steps: 灰度放大顺序(默认1%→5%→20%→50%→100%, 严格递增且末级=100)
        observation_min_months: 保守观察期(默认6月, 53号§3.3)
        min_trades_floor: 交易笔数统计地板(默认30笔, 53号§3.3)
    """

    parallel_min_days: int = 30
    shadow_min_days: int = 14
    gray_ramp_min_days: int = 30
    signal_match_min: float = 0.999
    slippage_diff_max_bp: float = 1.0
    fill_rate_min: float = 0.99
    shadow_pnl_correlation_min: float = 0.95
    settlement_match_min: float = 1.0
    latency_max_ms: float = 100.0
    ramp_drawdown_max: float = 0.01
    ramp_daily_loss_max: float = 0.03
    ramp_steps: tuple[float, ...] = (1.0, 5.0, 20.0, 50.0, 100.0)
    observation_min_months: int = 6
    min_trades_floor: int = 30

    def __post_init__(self) -> None:
        if min(self.parallel_min_days, self.shadow_min_days, self.gray_ramp_min_days) <= 0:
            raise ValueError("各阶段机制最小天数必须>0")
        if not 0 < self.signal_match_min <= 1:
            raise ValueError(f"signal_match_min必须在(0,1], got {self.signal_match_min}")
        if self.slippage_diff_max_bp <= 0:
            raise ValueError(f"slippage_diff_max_bp必须>0, got {self.slippage_diff_max_bp}")
        if not 0 < self.fill_rate_min <= 1:
            raise ValueError(f"fill_rate_min必须在(0,1], got {self.fill_rate_min}")
        if not 0 < self.shadow_pnl_correlation_min <= 1:
            raise ValueError(f"shadow_pnl_correlation_min必须在(0,1], got {self.shadow_pnl_correlation_min}")
        if not 0 < self.settlement_match_min <= 1:
            raise ValueError(f"settlement_match_min必须在(0,1], got {self.settlement_match_min}")
        if self.latency_max_ms <= 0:
            raise ValueError(f"latency_max_ms必须>0, got {self.latency_max_ms}")
        if not 0 < self.ramp_drawdown_max < 1:
            raise ValueError(f"ramp_drawdown_max必须在(0,1), got {self.ramp_drawdown_max}")
        if not 0 < self.ramp_daily_loss_max < 1:
            raise ValueError(f"ramp_daily_loss_max必须在(0,1), got {self.ramp_daily_loss_max}")
        steps = tuple(self.ramp_steps)
        if not steps or any(s <= 0 for s in steps):
            raise ValueError(f"ramp_steps必须全非空正数, got {steps}")
        if any(b <= a for a, b in zip(steps, steps[1:])):
            raise ValueError(f"ramp_steps必须严格递增(灰度顺序不可乱), got {steps}")
        if steps[-1] != 100.0:
            raise ValueError(f"ramp_steps末级必须=100(全量), got {steps[-1]}")
        if self.observation_min_months <= 0:
            raise ValueError(f"observation_min_months必须>0, got {self.observation_min_months}")
        if self.min_trades_floor <= 0:
            raise ValueError(f"min_trades_floor必须>0, got {self.min_trades_floor}")


#: 默认门禁阈值单真源(PHASE_SPECS duration_days/key_gates 由此派生, 53号§6 校准入口)
DEFAULT_GATE_THRESHOLDS: Final[GateThresholds] = GateThresholds()


def validate_gate_thresholds(thresholds: GateThresholds) -> GateThresholds:
    """校验门禁阈值配置(frozen dataclass 构造期已完成全量校验, 本函数为显式校验入口)

    Args:
        thresholds: 待校验配置

    Returns:
        校验通过的原实例

    Raises:
        TypeError: 非 GateThresholds 实例
    """
    if not isinstance(thresholds, GateThresholds):
        raise TypeError(f"thresholds必须是GateThresholds: {type(thresholds).__name__}")
    return thresholds


class PhaseSpec(BaseModel):
    phase: TransitionPhase
    name: str
    duration_days: int
    description: str
    key_gates: list[str] = Field(default_factory=list)


_T: Final[GateThresholds] = DEFAULT_GATE_THRESHOLDS

PHASE_SPECS: Final[dict[TransitionPhase, PhaseSpec]] = {
    TransitionPhase.PARALLEL: PhaseSpec(
        phase=TransitionPhase.PARALLEL,
        name="并行运行",
        duration_days=_T.parallel_min_days,
        description="Paper与Live并行运行30天，比较所有信号与执行质量",
        key_gates=[
            f"paper_live_signal_match >= {_T.signal_match_min:.1%}",
            f"slippage_diff < {_T.slippage_diff_max_bp:g}bp",
            f"fill_rate >= {_T.fill_rate_min:.0%}",
        ],
    ),
    TransitionPhase.SHADOW: PhaseSpec(
        phase=TransitionPhase.SHADOW,
        name="影子账户",
        duration_days=_T.shadow_min_days,
        description="以小额真实资金运行影子账户，验证执行链路与结算",
        key_gates=[
            f"shadow_pnl_correlation >= {_T.shadow_pnl_correlation_min}",
            f"settlement_match {_T.settlement_match_min:.0%}",
            f"latency < {_T.latency_max_ms:g}ms",
        ],
    ),
    TransitionPhase.GRAY_RAMP: PhaseSpec(
        phase=TransitionPhase.GRAY_RAMP,
        name="灰度上线",
        duration_days=_T.gray_ramp_min_days,
        description="逐级放大(1%->5%->20%->50%->100%)至全量",
        key_gates=[
            f"drawdown < {_T.ramp_drawdown_max:.0%} per ramp step",
            "no circuit_breaker triggers",
            f"daily_loss < {_T.ramp_daily_loss_max:.0%}",
        ],
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
            f"降级姿态={posture.value}，禁止晋级（须 NORMAL；#ARCH-QUANT-003 两机唯一耦合点，53 号 §3.6）"
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
