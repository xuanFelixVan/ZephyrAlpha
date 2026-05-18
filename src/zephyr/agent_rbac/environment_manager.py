# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md
# [MODULE] zephyr.agent_rbac
# [INVARIANTS] 七层纵深防御+六横切面Runtime RBAC
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md;src/zephyr/agent_rbac/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-020;MOD-INF-027
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PermissionError;ValueError;RuntimeError
# [TESTS] tests/test_agent_rbac/
from __future__ import annotations

from enum import Enum
from typing import Optional

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
        db_conn="sqlite:///dev.db",
        broker_conn="paper://localhost:4002",
    ),
    Environment.STAGE: EnvConfig(
        name=Environment.STAGE,
        host="120.26.x.x",
        env_file=".env.stage",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "staging"},
        db_conn="postgresql://stage",
        broker_conn="paper://stage:4002",
    ),
    Environment.UAT: EnvConfig(
        name=Environment.UAT,
        host="uat.internal",
        env_file=".env.uat",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "uat"},
        db_conn="postgresql://uat",
        broker_conn="paper://uat:4002",
    ),
    Environment.PAPER: EnvConfig(
        name=Environment.PAPER,
        host="paper.internal",
        env_file=".env.paper",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "paper"},
        db_conn="postgresql://paper",
        broker_conn="paper://paper-gw:4001",
    ),
    Environment.LIVE: EnvConfig(
        name=Environment.LIVE,
        host="live.internal",
        env_file=".env.live",
        env_vars={"LOG_LEVEL": "WARNING", "API_MODE": "production"},
        db_conn="postgresql://live",
        broker_conn="live://ib-gateway:4001",
    ),
}


def get_env(name: Environment) -> Optional[EnvConfig]:
    return ENVIRONMENTS.get(name)


def switch_env(current: Environment, target: Environment) -> Optional[EnvConfig]:
    if target == Environment.LIVE:
        return ENVIRONMENTS.get(Environment.LIVE)
    return ENVIRONMENTS.get(target)
