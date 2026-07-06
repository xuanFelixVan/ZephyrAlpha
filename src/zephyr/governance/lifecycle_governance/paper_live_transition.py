# [BLUEPRINT] SRC-049 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.paper_live_transition
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.lifecycle_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_paper_live_transition | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


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
        description="逐级放大(1%→5%→20%→50%→100%)至全量",
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
