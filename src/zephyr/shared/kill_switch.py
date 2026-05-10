"""
kill_switch - SSoT unified export (SRC-0041)

From 4 independent implementations consolidated to shared/ source of truth:
  - rollback/kill_switch       -> KillSwitchManager (L1/L2/L3 three-level manager)
  - agent_rbac/kill_switch     -> AgentKillSwitch (L0 global circuit breaker)
  - context_engine/kill_switch -> ContextKillSwitch (per-session error counter)
  - governance/kill_switch     -> GovernanceKillSwitch (trading risk circuit breaker)

Blueprint: MOD-INF-021 S6.2 B46 + SRC-0041 kill_switch x5 -> shared SSoT
"""

# -- Rollback: KillSwitchManager (L1/L2/L3 three-level Kill Switch manager) --
# -- Agent RBAC: L0 global circuit breaker (>=13 triggers, NORMAL/TRIPPED/COOLDOWN) --
from zephyr.agent_rbac.kill_switch import (  # noqa: F401
    KillSwitch as AgentKillSwitch,
)

# -- Context Engine: per-session error count circuit breaker (DD110) --
from zephyr.context_engine.kill_switch import (  # noqa: F401
    FuseState,
)

# -- Governance: trading risk circuit breaker (POSITION_LIMIT/DAILY_LOSS/...) --
from zephyr.governance.kill_switch import (  # noqa: F401
    KILL_SWITCHES,
    active_switches,
    evaluate,
    get_switch,
    reset,
    trigger,
)
from zephyr.rollback.kill_switch import (  # noqa: F401
    KillLevel,
    KillSwitchEntry,
    KillSwitchManager,
    KillSwitchStatus,
)
