# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_governance.environment_manager
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.ops_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: name 参数
#   fields: 参数 name，类型注解 Environment
#   code: environment_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: current 参数
#   fields: 参数 current，类型注解 Environment
#   code: environment_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: target 参数
#   fields: 参数 target，类型注解 Environment
#   code: environment_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_env
#   name_en: get_env
#   intro: get_env(name) 源码 L139-L140
#   desc: 源码 L139-L140
#   inputs: name
#   outputs: EnvConfig | None
# - id: A2
#   name_zh: ② switch_env
#   name_en: switch_env
#   intro: switch_env(current, target) 源码 L143-L146
#   desc: 源码 L143-L146
#   inputs: current target
#   outputs: EnvConfig | None
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: EnvConfig | None
#   name_en: EnvConfig | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Final

from pydantic import BaseModel, Field

from zephyr.shared.security.secrets import get_secret_or_default


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


ENVIRONMENTS: Final[dict[Environment, EnvConfig]] = {
    Environment.DEV: EnvConfig(
        name=Environment.DEV,
        host="127.0.0.1",
        env_file=".env.dev",
        env_vars={"LOG_LEVEL": "DEBUG", "API_MODE": "sandbox"},
        db_conn=get_secret_or_default("DEV_DB_CONN", "sqlite:///dev.db"),
        broker_conn=get_secret_or_default("DEV_BROKER_CONN", "paper://localhost:4002"),
    ),
    Environment.STAGE: EnvConfig(
        name=Environment.STAGE,
        host="120.26.x.x",
        env_file=".env.stage",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "staging"},
        db_conn=get_secret_or_default("STAGE_DB_CONN", "postgresql://stage"),
        broker_conn=get_secret_or_default("STAGE_BROKER_CONN", "paper://stage:4002"),
    ),
    Environment.UAT: EnvConfig(
        name=Environment.UAT,
        host="uat.internal",
        env_file=".env.uat",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "uat"},
        db_conn=get_secret_or_default("UAT_DB_CONN", "postgresql://uat"),
        broker_conn=get_secret_or_default("UAT_BROKER_CONN", "paper://uat:4002"),
    ),
    Environment.PAPER: EnvConfig(
        name=Environment.PAPER,
        host="paper.internal",
        env_file=".env.paper",
        env_vars={"LOG_LEVEL": "INFO", "API_MODE": "paper"},
        db_conn=get_secret_or_default("PAPER_DB_CONN", "postgresql://paper"),
        broker_conn=get_secret_or_default("PAPER_BROKER_CONN", "paper://paper-gw:4001"),
    ),
    Environment.LIVE: EnvConfig(
        name=Environment.LIVE,
        host="live.internal",
        env_file=".env.live",
        env_vars={"LOG_LEVEL": "WARNING", "API_MODE": "production"},
        db_conn=get_secret_or_default("LIVE_DB_CONN", "postgresql://live"),
        broker_conn=get_secret_or_default("LIVE_BROKER_CONN", "live://ib-gateway:4001"),
    ),
}


def get_env(name: Environment) -> EnvConfig | None:
    return ENVIRONMENTS.get(name)


def switch_env(current: Environment, target: Environment) -> EnvConfig | None:
    if target is Environment.LIVE:
        return ENVIRONMENTS.get(Environment.LIVE)
    return ENVIRONMENTS.get(target)
