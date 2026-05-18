# [BLUEPRINT] MOD-INF-021 | docs/03_modules/l01_infrastructure/rollback-system/blueprint.md
# [MODULE] zephyr.rollback.paper_live_transition
# [INVARIANTS] Git-native回滚;SQLite Dump Checkpoint;自动回滚
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/rollback-system/blueprint.md;src/zephyr/rollback/__init__.py
# [CONSUMERS] MOD-INF-020;MOD-INF-007;MOD-INF-022
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RollbackError;CheckpointError;VerificationError
# [TESTS] tests/test_rollback/

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

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


PHASE_SPECS: dict[TransitionPhase, PhaseSpec] = {
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

PHASE_ORDER: dict[TransitionPhase, int] = {
    TransitionPhase.PARALLEL: 0,
    TransitionPhase.SHADOW: 1,
    TransitionPhase.GRAY_RAMP: 2,
}


def get_phase_spec(phase: TransitionPhase) -> Optional[PhaseSpec]:
    return PHASE_SPECS.get(phase)


def valid_transition(from_phase: TransitionPhase, to_phase: TransitionPhase) -> bool:
    from_idx = PHASE_ORDER.get(from_phase, -1)
    to_idx = PHASE_ORDER.get(to_phase, -1)
    return to_idx == from_idx + 1


def get_next_phase(current: TransitionPhase) -> Optional[TransitionPhase]:
    phases = list(TransitionPhase)
    idx = phases.index(current) if current in phases else -1
    if idx + 1 < len(phases):
        return phases[idx + 1]
    return None


class TransitionState(BaseModel):
    current_phase: TransitionPhase
    started_at: str
    completed_at: Optional[str] = None
    ramping_percentage: float = 0.0

    @property
    def elapsed_days(self) -> float:
        started = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - started).total_seconds() / 86400.0

    def ramp_up(self, step_percent: float) -> float:
        self.ramping_percentage = min(100.0, self.ramping_percentage + step_percent)
        return self.ramping_percentage


def create_transition_state() -> TransitionState:
    return TransitionState(
        current_phase=TransitionPhase.PARALLEL,
        started_at=datetime.now(timezone.utc).isoformat(),
        ramping_percentage=0.0,
    )
