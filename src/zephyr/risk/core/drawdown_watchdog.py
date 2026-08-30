# [BLUEPRINT] MOD-RK-011 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.5.1/§6.11
# [MODULE] zephyr.risk.core.drawdown_watchdog
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.risk.stop_loss(import-only: detect_ghost_positions 复用,不改)
# [CONSUMERS] 独立看门狗进程(外部调度器驱动 poll_once) ; RiskOrchestrator(§6.5 接线位) ; stop_loss.execute_kill_switch_liquidation(L1 执行消费 force_liquidate_symbols)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不一致即强平(ghosts 非空→force_liquidate_symbols=ghost 标的+halt_new_orders=True); 轮询失败 fail-closed(POLL_FAILED→halt_new_orders=True 但不盲强平,人工介入); kill_switch CLOSED 且有持仓→全量强平(Ghost 情况2); strategy_state None=冷启动守卫(broker 有持仓全部视为 Ghost,来源不明); 本模块只裁决不执行(执行归 L1,进程分离归部署)
# [MODIFY-GUARD] tests/risk/test_drawdown_watchdog.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidWatchdogInputError(ZA-RK-0074)
# [TESTS] tests/risk/test_drawdown_watchdog.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: broker_holdings {symbol: {qty}}(轮询实盘真实持仓; None=轮询失败)
# I2: strategy_state {symbol: "OPEN"/"CLOSED"}(策略侧持仓状态; None=冷启动守卫)
# I3: kill_switch_state "OPEN"/"CLOSED"(DefaultRiskValidator 状态, L3 轮询核对对象)
# F1: poll_once(fail-closed 轮询失败判定 → detect_ghost_positions 一致性核对 → 裁决强平清单)
# O1: WatchdogVerdict(status/ghosts/force_liquidate_symbols/halt_new_orders/reason)
# [/ALGO_FLOW]
"""
D_RISK — L3 看门狗一致性裁决（35 号 memo §6.11 施工，§3.5.1 四层架构 L3 落地）。

痛点（§3.5.1 四层防御表 L3 行）：
  L1 代码层平仓链路 + L2 broker 端止损仍可能留下 Ghost Position（平仓指令
  发出但未成交/部分成交/连接中断，nexusfi Breukelen 2022 实证 14 手 ES
  无主暴露）。L3 看门狗是独立于策略进程的第三道兜底：定时轮询 broker
  持仓 vs 策略状态一致性，不一致即裁决强平清单。

本模块落地（L3 裁决核心，进程分离属部署层——由外部调度器独立进程驱动）：
  - poll_once：单轮一致性裁决。复用 stop_loss.detect_ghost_positions
    双类型检测（strategy_closed_but_broker_holds /
    kill_switch_closed_but_position_remains），复用 §3.15 冷启动守卫
    （strategy_state=None 时 broker 持仓全部视为来源不明 Ghost）。
  - 裁决语义（§3.5.1 "不一致即强平" + Tidball "fail closed" 双重锚定）：
    * ghosts 非空 → force_liquidate_symbols=ghost 标的（去重）+
      halt_new_orders=True（先锁增量再清存量）；
    * 轮询失败（broker_holdings=None）→ POLL_FAILED：halt_new_orders=True
      但 force_liquidate_symbols=空——监控不可用默认停新仓（halt），
      绝不基于缺失数据盲目强平，人工介入；
    * kill_switch CLOSED 且 broker 仍有持仓 → 全量强平残余（Ghost 情况 2）。
  - 边界：本模块只裁决不执行——强平执行归 L1 execute_kill_switch_liquidation，
    独立进程/Task Scheduler 驱动归部署层（Unfireable 四属性之进程分离，
    §6.31 远期参考）；不读写任何持久化状态（无状态纯裁决）。

SSoT: 35_drawdown_protocol_impl §3.5.1/§6.11

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: broker_holdings 参数
#   fields: 参数 broker_holdings，类型注解 Mapping[str, Mapping[str, Any]] | None
#   code: drawdown_watchdog.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: strategy_state 参数
#   fields: 参数 strategy_state，类型注解 Mapping[str, str] | None
#   code: drawdown_watchdog.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: kill_switch_state 参数
#   fields: 参数 kill_switch_state，类型注解 str
#   code: drawdown_watchdog.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① poll_once
#   name_en: poll_once
#   intro: L3 单轮一致性裁决（外部独立进程定时调用，§3.5.1 看门狗层）。
#   desc: L3 单轮一致性裁决（外部独立进程定时调用，§3.5.1 看门狗层）。 Args: broker_holdings: 实盘真实持仓 {symbol: {"qty": ...}}；…；源码 L143-L209
#   inputs: broker_holdings strategy_state kill_switch_state
#   outputs: WatchdogVerdict
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: WatchdogVerdict
#   name_en: WatchdogVerdict
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 独立看门狗进程(外部调度器驱动 poll_once) ; RiskOrchestrator(§6.5 接线位) ; stop_loss.execute_kil…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from zephyr.risk.stop_loss import detect_ghost_positions
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidWatchdogInputError",
    "WatchdogVerdict",
    "WATCHDOG_STATUS_CONSISTENT",
    "WATCHDOG_STATUS_GHOST_DETECTED",
    "WATCHDOG_STATUS_POLL_FAILED",
    "poll_once",
]

_logger = logging.getLogger(__name__)

#: 裁决状态（WatchdogVerdict.status 合法值）
WATCHDOG_STATUS_CONSISTENT: Final = "CONSISTENT"
WATCHDOG_STATUS_GHOST_DETECTED: Final = "GHOST_DETECTED"
WATCHDOG_STATUS_POLL_FAILED: Final = "POLL_FAILED"

_VALID_KILL_SWITCH_STATES: Final = frozenset({"OPEN", "CLOSED"})


class InvalidWatchdogInputError(ZephyrBaseError):
    """L3 看门狗输入非法（kill_switch_state 越界/持仓载荷畸形等）。"""

    error_code = "ZA-RK-0074"


@dataclass(frozen=True)
class WatchdogVerdict:
    """L3 单轮裁决（§3.5.1 L3：不一致即强平的决策输出）。

    Attributes:
        status: CONSISTENT=一致 / GHOST_DETECTED=检出幽灵持仓 /
            POLL_FAILED=轮询失败（fail-closed）
        ghosts: Ghost 持仓列表 [(symbol, position_info, ghost_type)]
        force_liquidate_symbols: 裁决强平标的（ghost 标的去重，输入顺序）；
            POLL_FAILED 时恒为空（不基于缺失数据盲动）
        halt_new_orders: 是否锁定新开仓（GHOST_DETECTED/POLL_FAILED 均 True）
        reason: 人类可读裁决说明（审计留痕）
    """

    status: str
    ghosts: tuple[tuple[str, dict, str], ...] = field(default_factory=tuple)
    force_liquidate_symbols: tuple[str, ...] = field(default_factory=tuple)
    halt_new_orders: bool = False
    reason: str = ""


def poll_once(
    broker_holdings: Mapping[str, Mapping[str, Any]] | None,
    strategy_state: Mapping[str, str] | None,
    kill_switch_state: str = "OPEN",
) -> WatchdogVerdict:
    """L3 单轮一致性裁决（外部独立进程定时调用，§3.5.1 看门狗层）。

    Args:
        broker_holdings: 实盘真实持仓 {symbol: {"qty": ...}}；
            None=轮询失败（broker 连接异常，fail-closed）
        strategy_state: 策略侧持仓状态 {symbol: "OPEN"/"CLOSED"}；
            None=冷启动守卫（broker 有持仓全部视为来源不明 Ghost）
        kill_switch_state: Kill Switch 状态 "OPEN"/"CLOSED"
            （DefaultRiskValidator 状态，L3 轮询核对对象）

    Returns:
        WatchdogVerdict（调用方：force_liquidate_symbols 交 L1 执行强平，
        halt_new_orders 交 validate_order 锁新开仓）

    Raises:
        InvalidWatchdogInputError: kill_switch_state 越界 / 持仓载荷非 Mapping
    """
    if kill_switch_state not in _VALID_KILL_SWITCH_STATES:
        raise InvalidWatchdogInputError(f"kill_switch_state 须为 OPEN/CLOSED, got {kill_switch_state!r}")

    # ── fail-closed：轮询失败 → 锁新开仓 + 人工介入，但不盲强平 ──
    if broker_holdings is None:
        _logger.critical("WATCHDOG_POLL_FAILED broker 持仓轮询失败, fail-closed 锁新开仓")
        return WatchdogVerdict(
            status=WATCHDOG_STATUS_POLL_FAILED,
            halt_new_orders=True,
            reason="broker 持仓轮询失败（监控不可用默认 halt）——锁定新开仓，人工介入核对，不基于缺失数据强平",
        )

    for sym, pos in broker_holdings.items():
        if not isinstance(pos, Mapping):
            raise InvalidWatchdogInputError(f"{sym} 持仓信息须为 Mapping, got {type(pos).__name__}")

    # ── 一致性核对（Ghost 检测，复用 L1 已施工双类型检测 + §3.15 冷启动守卫）──
    if strategy_state is None:
        ghosts = [
            (sym, dict(pos), "unknown_to_strategy") for sym, pos in broker_holdings.items() if pos.get("qty", 0) != 0
        ]
    else:
        ghosts = detect_ghost_positions(dict(broker_holdings), dict(strategy_state), kill_switch_state)

    if not ghosts:
        _logger.info("WATCHDOG_CONSISTENT holdings=%d kill_switch=%s", len(broker_holdings), kill_switch_state)
        return WatchdogVerdict(
            status=WATCHDOG_STATUS_CONSISTENT,
            reason="持仓与策略状态一致",
        )

    # ── 不一致即强平：ghost 标的去重 + 锁新开仓（先锁增量再清存量）──
    force_liquidate = tuple(dict.fromkeys(g[0] for g in ghosts))
    _logger.critical(
        "WATCHDOG_GHOST_DETECTED symbols=%s types=%s",
        list(force_liquidate),
        [g[2] for g in ghosts],
    )
    return WatchdogVerdict(
        status=WATCHDOG_STATUS_GHOST_DETECTED,
        ghosts=tuple(ghosts),
        force_liquidate_symbols=force_liquidate,
        halt_new_orders=True,
        reason=f"检出 Ghost Position {len(ghosts)} 项（{', '.join(force_liquidate)}），裁决强平 + 锁定新开仓（§3.5.1 L3）",
    )
