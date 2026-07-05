# [BLUEPRINT] SRC-058 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.environment_manager
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
# [A_module] module_id=MOD-GOV_environment_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import os
from enum import Enum

from pydantic import BaseModel, Field


class Environment(str, Enum):
    DEV = "DEV"
    STAGE = "STAGE"
    UAT = "UAT"
    PAPER = "PAPER"
    LIVE = "LIVE"


class EnvConfig(BaseModel):
    name: Environment
    host: str
    env_file: str
    env_vars: dict[str, str] = Field(default_factory=dict)
    db_conn: str = ""
    broker_conn: str = ""


ENVIRONMENTS: dict[Environment, EnvConfig] = {
    Environment.DEV: EnvConfig(
        name=Environment.DEV,
        host="127.0.0.1",
        env_file=".env.dev",
        env_vars={"LOG_LEVEL": "DEBUG", "API_MODE": "sandbox"},
        db_conn=os.getenv("DEV_DB_CONN", "sqlite:///dev.db"),
        broker_conn=os.getenv("DEV_BROKER_CONN", "paper://localhost:4002"),
    ),
    Environment.STAGE: EnvConfig(
        name=Environment.STAGE,
        host="120.26.x.x",
        env_file=".env.stage",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "staging"},
        db_conn=os.getenv("STAGE_DB_CONN", "postgresql://stage"),
        broker_conn=os.getenv("STAGE_BROKER_CONN", "paper://stage:4002"),
    ),
    Environment.UAT: EnvConfig(
        name=Environment.UAT,
        host="uat.internal",
        env_file=".env.uat",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "uat"},
        db_conn=os.getenv("UAT_DB_CONN", "postgresql://uat"),
        broker_conn=os.getenv("UAT_BROKER_CONN", "paper://uat:4002"),
    ),
    Environment.PAPER: EnvConfig(
        name=Environment.PAPER,
        host="paper.internal",
        env_file=".env.paper",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "paper"},
        db_conn=os.getenv("PAPER_DB_CONN", "postgresql://paper"),
        broker_conn=os.getenv("PAPER_BROKER_CONN", "paper://paper-gw:4001"),
    ),
    Environment.LIVE: EnvConfig(
        name=Environment.LIVE,
        host="live.internal",
        env_file=".env.live",
        env_vars={"LOG_LEVEL": "WARNING", "API_MODE": "production"},
        db_conn=os.getenv("LIVE_DB_CONN", "postgresql://live"),
        broker_conn=os.getenv("LIVE_BROKER_CONN", "live://ib-gateway:4001"),
    ),
}


def get_env(name: Environment) -> EnvConfig | None:
    return ENVIRONMENTS.get(name)


def switch_env(current: Environment, target: Environment) -> EnvConfig | None:
    if target is Environment.LIVE:
        return ENVIRONMENTS.get(Environment.LIVE)
    return ENVIRONMENTS.get(target)
