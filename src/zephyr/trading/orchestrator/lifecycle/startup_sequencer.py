from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.lifecycle.startup_sequencer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_startup_sequencer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
冷启动序列器（Startup Sequencer — CT-STARTUP-001）

依据：MOD-MASTER-002 蓝图 §十六
5层启动顺序 + 120s全局超时。
"""

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel


class StartupLayer(str, Enum):
    L1_DATABASE = "L1_database"
    L2_VMS = "L2_vector_memory"
    L3_FLE = "L3_feedback_loop"
    L4_CORE_SERVICES = "L4_core_services"
    L5_TELEMETRY = "L5_telemetry"


STARTUP_ORDER: Final[tuple[StartupLayer, ...]] = (
    StartupLayer.L1_DATABASE,
    StartupLayer.L2_VMS,
    StartupLayer.L3_FLE,
    StartupLayer.L4_CORE_SERVICES,
    StartupLayer.L5_TELEMETRY,
)

STARTUP_COMPONENTS: Final[dict[StartupLayer, list[str]]] = {
    StartupLayer.L1_DATABASE: ["database"],
    StartupLayer.L2_VMS: ["vector-memory"],
    StartupLayer.L3_FLE: ["feedback-loop"],
    StartupLayer.L4_CORE_SERVICES: [
        "orchestrator",
        "script_system",
        "knowledge_base",
        "context-engine",
        "gate_engine",
        "pipeline",
        "llm-security",
        "mcp_servers",
    ],
    StartupLayer.L5_TELEMETRY: ["system-telemetry"],
}

GLOBAL_TIMEOUT_S: Final[float] = 120.0


class StartupState(BaseModel):
    layer: StartupLayer
    status: str = "pending"
    started_at: datetime | None = None
    completed_at: datetime | None = None


class StartupSequencer:
    def __init__(self):
        self._states: dict[StartupLayer, StartupState] = {}
        self._init_states()

    def _init_states(self) -> None:
        for layer in STARTUP_ORDER:
            self._states[layer] = StartupState(layer=layer)

    def get_order(self) -> list[str]:
        return [l.value for l in STARTUP_ORDER]

    def get_layer_components(self, layer: StartupLayer) -> list[str]:
        return STARTUP_COMPONENTS.get(layer, [])

    def start_layer(self, layer: StartupLayer) -> bool:
        idx = STARTUP_ORDER.index(layer)
        if idx > 0:
            prev = STARTUP_ORDER[idx - 1]
            prev_state = self._states[prev]
            if prev_state.status != "completed":
                return False

        state = self._states[layer]
        state.status = "running"
        state.started_at = datetime.now(UTC)
        return True

    def complete_layer(self, layer: StartupLayer) -> None:
        state = self._states[layer]
        state.status = "completed"
        state.completed_at = datetime.now(UTC)
