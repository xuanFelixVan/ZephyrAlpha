# [BLUEPRINT] SRC-064 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.startup_shutdown
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.__init__
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
# [A_module] module_id=MOD-GOV_startup_shutdown | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class StartupPhase(str, Enum):
    P1_SECRETS_DB = "P1_SECRETS_DB"
    P2_CONTEXT_GATE = "P2_CONTEXT_GATE"
    P3_MARKET_DATA = "P3_MARKET_DATA"
    P4_FACTOR_SIGNAL = "P4_FACTOR_SIGNAL"
    P5_OMS_RISK = "P5_OMS_RISK"
    P6_DASHBOARD_TELEMETRY = "P6_DASHBOARD_TELEMETRY"


class PhaseState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    HEALTHY = "HEALTHY"
    FAILED = "FAILED"


class StartupPhaseDef(BaseModel):
    phase: StartupPhase
    label: str
    depends_on: list[StartupPhase] = Field(default_factory=list)
    health_check: str = ""
    timeout_seconds: int = 30
    state: PhaseState = PhaseState.PENDING

    @property
    def is_ready(self) -> bool:
        return all(
            STARTUP_DAG.get(dep) is not None and STARTUP_DAG[dep].state is PhaseState.HEALTHY for dep in self.depends_on
        )


STARTUP_DAG: dict[StartupPhase, StartupPhaseDef] = {
    StartupPhase.P1_SECRETS_DB: StartupPhaseDef(
        phase=StartupPhase.P1_SECRETS_DB,
        label="Secrets + Database",
        depends_on=[],
        health_check="check_secrets_db",
        timeout_seconds=30,
    ),
    StartupPhase.P2_CONTEXT_GATE: StartupPhaseDef(
        phase=StartupPhase.P2_CONTEXT_GATE,
        label="Context + Gate",
        depends_on=[StartupPhase.P1_SECRETS_DB],
        health_check="check_context_gate",
        timeout_seconds=15,
    ),
    StartupPhase.P3_MARKET_DATA: StartupPhaseDef(
        phase=StartupPhase.P3_MARKET_DATA,
        label="Market Data",
        depends_on=[StartupPhase.P2_CONTEXT_GATE],
        health_check="check_market_data",
        timeout_seconds=20,
    ),
    StartupPhase.P4_FACTOR_SIGNAL: StartupPhaseDef(
        phase=StartupPhase.P4_FACTOR_SIGNAL,
        label="Factor + Signal",
        depends_on=[StartupPhase.P3_MARKET_DATA],
        health_check="check_factor_signal",
        timeout_seconds=20,
    ),
    StartupPhase.P5_OMS_RISK: StartupPhaseDef(
        phase=StartupPhase.P5_OMS_RISK,
        label="OMS + Risk",
        depends_on=[StartupPhase.P4_FACTOR_SIGNAL],
        health_check="check_oms_risk",
        timeout_seconds=20,
    ),
    StartupPhase.P6_DASHBOARD_TELEMETRY: StartupPhaseDef(
        phase=StartupPhase.P6_DASHBOARD_TELEMETRY,
        label="Dashboard + Telemetry",
        depends_on=[StartupPhase.P5_OMS_RISK],
        health_check="check_dashboard_telemetry",
        timeout_seconds=15,
    ),
}

SHUTDOWN_SEQUENCE: list[StartupPhase] = list(reversed(list(StartupPhase)))


class StartupOrchestrator:
    def __init__(self, health_check_fn: Callable[[str], bool]) -> None:
        self._health_check = health_check_fn

    def run(self) -> bool:
        for phase in StartupPhase:
            pdef = STARTUP_DAG[phase]
            if not pdef.is_ready:
                logger.warning("StartupPhase %s 未就绪——上游不健康", phase.value)
                return False
            pdef.state = PhaseState.RUNNING
            logger.info("启动 %s: %s", phase.value, pdef.label)
            ok = self._health_check(pdef.health_check)
            time.sleep(0.1)
            if ok:
                pdef.state = PhaseState.HEALTHY
                logger.info("  %s: HEALTHY", phase.value)
            else:
                pdef.state = PhaseState.FAILED
                logger.error("  %s: FAILED", phase.value)
                return False
        return True


class ShutdownOrchestrator:
    def __init__(self, shutdown_fn: Callable[[StartupPhase], bool]) -> None:
        self._shutdown = shutdown_fn

    def run(self) -> bool:
        for phase in SHUTDOWN_SEQUENCE:
            pdef = STARTUP_DAG[phase]
            logger.info("停机 %s: %s", phase.value, pdef.label)
            ok = self._shutdown(phase)
            if ok:
                pdef.state = PhaseState.PENDING
                logger.info("  %s: 已停机", phase.value)
            else:
                logger.error("  %s: 停机失败", phase.value)
                return False
        return True


def get_phase_def(phase: StartupPhase) -> StartupPhaseDef | None:
    return STARTUP_DAG.get(phase)


def startup_ordered_phases() -> list[StartupPhase]:
    return list(StartupPhase)


def shutdown_ordered_phases() -> list[StartupPhase]:
    return list(SHUTDOWN_SEQUENCE)
