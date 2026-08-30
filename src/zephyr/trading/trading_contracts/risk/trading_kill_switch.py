# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.trading.trading_contracts.risk.trading_kill_switch
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.trading_contracts.risk.__init__
# [CONSUMERS] MOD-INF-022 ; MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 交易风险熔断器;五级KillSwitch;Pydantic数据模型
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md;src/zephyr/rollback/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError;RuntimeError
# [TESTS] tests/test_rollback/
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# SRC-0041: Copy file -- keep independent implementation, pending future review
#   shared/kill_switch.py is now the unified export SSoT; this file exported
#   as GovernanceKillSwitch alias from shared.
#   Migrated from governance/ to rollback/ on 2026-05-14.
#
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: level 参数
#   fields: 参数 level，类型注解 KillSwitchLevel
#   code: trading_kill_switch.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: condition 参数
#   fields: 参数 condition，类型注解 str
#   code: trading_kill_switch.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: evaluator 参数
#   fields: 参数 evaluator，类型注解 Callable[[str], bool]
#   code: trading_kill_switch.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_switch
#   name_en: get_switch
#   intro: get_switch(level) 源码 L177-L178
#   desc: 源码 L177-L178
#   inputs: level
#   outputs: KillSwitch | None
# - id: A2
#   name_zh: ② trigger
#   name_en: trigger
#   intro: trigger(level) 源码 L181-L186
#   desc: 源码 L181-L186
#   inputs: level
#   outputs: bool
# - id: A3
#   name_zh: ③ reset
#   name_en: reset
#   intro: reset(level) 源码 L189-L194
#   desc: 源码 L189-L194
#   inputs: level
#   outputs: bool
# - id: A4
#   name_zh: ④ active_switches
#   name_en: active_switches
#   intro: active_switches() 源码 L197-L198
#   desc: 源码 L197-L198
#   inputs: 无参数
#   outputs: list[KillSwitch]
# - id: A5
#   name_zh: ⑤ evaluate
#   name_en: evaluate
#   intro: evaluate(condition, evaluator) 源码 L201-L214
#   desc: 源码 L201-L214
#   inputs: condition evaluator
#   outputs: list[KillSwitch]
#   （注：A5 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: KillSwitch | None
#   name_en: KillSwitch | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-022 ; MOD-INF-020
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-022 ; MOD-INF-020
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from typing import Final

logger = logging.getLogger(__name__)

from collections.abc import Callable
from enum import Enum

from pydantic import BaseModel


class KillSwitchLevel(str, Enum):
    POSITION_LIMIT = "POSITION_LIMIT"
    DAILY_LOSS = "DAILY_LOSS"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    SECOND_LEVEL = "SECOND_LEVEL"
    API_TIMEOUT = "API_TIMEOUT"


# class-name-alias: trading-risk Pydantic kill-switch model (5-level POSITION_LIMIT/DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT); name shadows canonical zephyr.security.access_control.kill_switch.KillSwitch (MOD-SEC_kill_switch) but is a trading-domain data model, not the system-level breaker. Distinct domain (D_TRADING).
class KillSwitch(BaseModel):
    level: KillSwitchLevel
    label: str
    trigger_condition: str
    action: str
    cooldown_seconds: int = 0
    auto_reenable: bool = False
    active: bool = False


KILL_SWITCHES: Final[dict[KillSwitchLevel, KillSwitch]] = {
    KillSwitchLevel.POSITION_LIMIT: KillSwitch(
        level=KillSwitchLevel.POSITION_LIMIT,
        label="位置超限 -> reduce_only",
        trigger_condition="position > max_position_limit",
        action="REDUCE_ONLY: 禁止开仓, 允许平仓",
        cooldown_seconds=300,
        auto_reenable=True,
    ),
    KillSwitchLevel.DAILY_LOSS: KillSwitch(
        level=KillSwitchLevel.DAILY_LOSS,
        label="日亏>3% -> cancel all + disable new",
        trigger_condition="daily_pnl < -0.03 * aum",
        action="CANCEL_ALL + DISABLE_NEW: 撤销所有挂单, 禁止新单",
        cooldown_seconds=86400,
        auto_reenable=False,
    ),
    KillSwitchLevel.CIRCUIT_BREAKER: KillSwitch(
        level=KillSwitchLevel.CIRCUIT_BREAKER,
        label="断路器 -> disconnect",
        trigger_condition="consecutive_rejections >= 5 OR price_deviation > 5%",
        action="DISCONNECT: 断开Broker连接",
        cooldown_seconds=600,
        auto_reenable=False,
    ),
    KillSwitchLevel.SECOND_LEVEL: KillSwitch(
        level=KillSwitchLevel.SECOND_LEVEL,
        label="秒级熔断 -> full shutdown",
        trigger_condition="latency > 1000ms OR fill_rate < 50%",
        action="FULL_SHUTDOWN: 全系统暂停",
        cooldown_seconds=300,
        auto_reenable=False,
    ),
    KillSwitchLevel.API_TIMEOUT: KillSwitch(
        level=KillSwitchLevel.API_TIMEOUT,
        label="API超时 -> auto kill",
        trigger_condition="broker_api_timeout > 10s OR heartbeat_miss >= 3",
        action="AUTO_KILL: 自动终止当前Session",
        cooldown_seconds=120,
        auto_reenable=True,
    ),
}


def get_switch(level: KillSwitchLevel) -> KillSwitch | None:
    return KILL_SWITCHES.get(level)


def trigger(level: KillSwitchLevel) -> bool:
    ks = KILL_SWITCHES.get(level)
    if ks is None:
        return False
    ks.active = True
    return True


def reset(level: KillSwitchLevel) -> bool:
    ks = KILL_SWITCHES.get(level)
    if ks is None:
        return False
    ks.active = False
    return True


def active_switches() -> list[KillSwitch]:
    return [ks for ks in KILL_SWITCHES.values() if ks.active]


def evaluate(
    condition: str,
    evaluator: Callable[[str], bool],
) -> list[KillSwitch]:
    triggered: list[KillSwitch] = []
    for _level, ks in KILL_SWITCHES.items():
        if not ks.active:
            try:
                if evaluator(ks.trigger_condition):
                    ks.active = True
                    triggered.append(ks)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in trading_kill_switch", exc_info=True)
    return triggered
