# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.implementations.default_risk_validator
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.risk_manager; zephyr.risk.risk_validator; zephyr.shared.state_store
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] kill switch 状态记录损坏按已熔断处理(Fail-Closed); reset 持久化失败不解除熔断
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StateCorruptError→fail-closed置位(不向上抛)
# [TESTS] tests/risk/test_kill_switch_state_persistence.py
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_RISK — Default Risk Validator

风险校验器具体实现。Pre-trade 订单校验 + 全组合风控状态校验。

CTR 契约：
  消费者 — CTR-003 (RiskLimits) ← 本层
  消费者 — CTR-006 (PositionSnapshot) ← D_EXECUTION_CORE
  生产者 — CTR-ERR-004 (RiskLimitViolationError) -> D_PORTFOLIO_CORE, D_EXECUTION_CORE

SSoT: cross_layer_contracts.yaml -> CTR-ERR-004 + CTR-003
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final

from zephyr.risk.risk_manager import (
    RiskLimits,
)
from zephyr.risk.risk_validator import (
    RiskValidator,
    ViolatedConstraint,
    ViolationDetail,
)
from zephyr.shared.state_store import (
    JsonStateStore,
    StateCorruptError,
    StateStoreError,
)

_logger = logging.getLogger(__name__)

__validator_id__ = "default-risk-validator"

# Kill Switch 持久化命名空间（单一仲裁点：stop_loss 兼容层与本类共用同一状态记录）
KILL_SWITCH_STATE_NAMESPACE = "kill_switch"

# 幽灵持仓类型枚举（detect_ghost_positions 第三种判定，裁定书 §二）
GHOST_STRATEGY_CLOSED = "strategy_closed_but_broker_holds"
GHOST_KILL_SWITCH_ACTIVE = "kill_switch_active_but_position_remains"
GHOST_UNKNOWN_TO_STRATEGY = "unknown_to_strategy"


def load_kill_switch_record(store: JsonStateStore) -> dict | None:
    """读取 Kill Switch 持久化状态记录（三分语义委托给 JsonStateStore.load）。

    Returns:
        None: 无记录（fresh boot，从未触发）。
        dict: 状态记录（含 active/triggered_at/reason/event_id 等字段）。

    Raises:
        StateCorruptError: 记录损坏——消费方必须 fail-closed。
    """
    return store.load(KILL_SWITCH_STATE_NAMESPACE)


def persist_trigger_record(
    store: JsonStateStore,
    *,
    event_id: str,
    reason: str = "",
    scope: str = "all",
    source: str = "default_risk_validator",
) -> dict:
    """持久化熔断触发记录（含触发时间+reason+event_id，Qwen P0-3①）。"""
    record = {
        "active": True,
        "event_id": event_id,
        "reason": reason,
        "scope": scope,
        "source": source,
        "triggered_at": datetime.now(UTC).isoformat(),
    }
    store.save(KILL_SWITCH_STATE_NAMESPACE, record)
    return record


def persist_reset_record(
    store: JsonStateStore,
    *,
    confirmed_by: str,
    override_reason: str = "",
    source: str = "default_risk_validator",
) -> dict:
    """持久化熔断解除记录。"""
    record = {
        "active": False,
        "confirmed_by": confirmed_by,
        "override_reason": override_reason,
        "source": source,
        "reset_at": datetime.now(UTC).isoformat(),
    }
    store.save(KILL_SWITCH_STATE_NAMESPACE, record)
    return record


class DefaultRiskValidator(RiskValidator):
    """默认风险校验器——Pre-trade + Portfolio 校验"""

    __validator_id__ = __validator_id__

    def __init__(
        self,
        kill_switch_active: bool = False,
        state_store: JsonStateStore | None = None,
    ):
        """初始化风险校验器。

        Args:
            kill_switch_active: 初始熔断状态（无持久化记录时的默认值）。
            state_store: Crash-only 状态外部化存储（#ARCH-QUANT-002）。
                提供时启动加载持久化的 kill switch 状态：
                - 无记录（fresh boot）→ 使用 kill_switch_active 默认值；
                - 有记录 → 以记录为准（触发后杀进程重启，熔断状态仍在）；
                - 记录损坏（StateCorruptError）→ Fail-Closed 按已熔断处理。
                None=纯内存模式（既有行为，不持久化）。
        """
        self._state_store = state_store
        self._violation_history: list[ViolationDetail] = []

        if state_store is None:
            self._kill_switch_active = kill_switch_active
            return

        try:
            record = load_kill_switch_record(state_store)
        except StateCorruptError as exc:
            # Fail-Closed：状态读不到按已熔断处理（Qwen P0-3①）
            _logger.critical(
                "KILL_SWITCH_STATE_CORRUPT fail-closed validator=%s error=%s",
                self.__validator_id__,
                exc,
            )
            self._kill_switch_active = True
            return

        if record is None:
            self._kill_switch_active = kill_switch_active
        else:
            self._kill_switch_active = bool(record.get("active", False))
            if self._kill_switch_active:
                _logger.warning(
                    "KILL_SWITCH_STATE_RESTORED validator=%s event_id=%s triggered_at=%s reason=%s",
                    self.__validator_id__,
                    record.get("event_id"),
                    record.get("triggered_at"),
                    record.get("reason"),
                )

    def validate_order(
        self,
        symbol: str,
        target_weight: float,
        current_holdings: dict[str, float],
        limits: RiskLimits,
    ) -> list[ViolationDetail]:
        """对单笔订单做 pre-trade 风控校验。

        校验项：
        1. Kill Switch 激活时拒绝全部新订单（HALT）
        2. 单仓权重是否超限（HALT）
        3. 下单后总权重是否超限（HALT）

        Args:
            symbol: 标的代码
            target_weight: 目标权重（正=买入，负=卖出）
            current_holdings: 当前持仓权重字典
            limits: 风险限额配置

        Returns:
            违规列表，空列表表示通过
        """
        violations: list[ViolationDetail] = []

        if self._kill_switch_active:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.DRAWDOWN_TRIGGER,
                    description="Kill switch 已激活，拒绝所有新订单",
                    limit_value=0.0,
                    actual_value=target_weight,
                    severity="HALT",
                )
            )
            self._violation_history.extend(violations)
            return violations

        # 5.145 审查修复：limits: Any -> RiskLimits，消除 dict 双模式（死代码）
        override_limit = (limits.symbol_overrides or {}).get(symbol)
        effective_single = override_limit if override_limit is not None else limits.max_single_position

        if abs(target_weight) > effective_single:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.POSITION_LIMIT,
                    description=f"单仓权重超限: {symbol} target={target_weight:.4f} limit={effective_single:.4f}",
                    limit_value=effective_single,
                    actual_value=abs(target_weight),
                    severity="HALT",
                )
            )

        post_trade_weight = Decimal(str(current_holdings.get(symbol, 0.0))) + Decimal(str(target_weight))
        if abs(post_trade_weight) > effective_single * 1.05:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.POSITION_LIMIT,
                    description=f"下单后总权重超限: {symbol} post_trade={post_trade_weight:.4f}",
                    limit_value=effective_single,
                    actual_value=abs(post_trade_weight),
                    severity="HALT",
                )
            )

        self._violation_history.extend(violations)
        return violations

    def validate_portfolio(
        self,
        holdings: dict[str, float],
        market_values: dict[str, float],
        total_nav: Decimal,
        limits: RiskLimits,
    ) -> list[ViolationDetail]:
        """对全组合做风控状态校验。

        校验项：
        1. 各标的持仓是否超单仓限额（HALT）
        2. 总杠杆是否超限（HALT）

        注（治本 2026-08-17）：组合回撤检查不在此快照接口内——
        (holdings, market_values, total_nav) 单点快照数学上无法计算峰谷回撤
        （需要峰值状态），此前 "1 - Σmarket_values/total_nav" 的实现把现金拖累
        误计为回撤（满仓永不触发、持现金即误报 HALT），属错误的第二决策点。
        回撤真源 = drawdown_tracker（MOD-RK-011，峰值追踪+三级阈值）+
        drawdown_controller（MOD-POS-008）；熔断仲裁 = 本类 kill_switch 状态。

        Args:
            holdings: symbol → weight 字典
            market_values: symbol → market_value 字典
            total_nav: 组合总净值
            limits: 风险限额配置

        Returns:
            违规列表，空列表表示通过
        """
        violations: list[ViolationDetail] = []

        # 5.145 审查修复：limits: Any -> RiskLimits，消除 dict 双模式（死代码）
        max_single = limits.max_single_position
        max_leverage = limits.max_gross_leverage

        for symbol, weight in holdings.items():
            if abs(weight) > max_single:
                violations.append(
                    ViolationDetail(
                        constraint=ViolatedConstraint.POSITION_LIMIT,
                        description=f"持仓超限: {symbol} weight={weight:.4f} limit={max_single:.4f}",
                        limit_value=max_single,
                        actual_value=abs(weight),
                        severity="HALT",
                    )
                )

        gross_leverage = sum(abs(w) for w in holdings.values())
        if gross_leverage > max_leverage:
            violations.append(
                ViolationDetail(
                    constraint=ViolatedConstraint.LEVERAGE_LIMIT,
                    description=f"总杠杆超限: {gross_leverage:.4f} > {max_leverage:.4f}",
                    limit_value=max_leverage,
                    actual_value=gross_leverage,
                    severity="HALT",
                )
            )

        self._violation_history.extend(violations)
        return violations

    def trigger_kill_switch(
        self,
        reason: str = "",
        event_id: str | None = None,
        scope: str = "all",
    ) -> None:
        """手动触发 kill switch（资金级熔断事件）。

        状态置位先行（绝不让 I/O 延迟熔断），随后持久化（配置了 state_store 时）：
        持久化失败仅 CRITICAL 告警，内存态保持熔断（当前进程防护不失效）。

        Args:
            reason: 触发原因（如 "drawdown > 25%"）。
            event_id: 幂等事件 ID（None=自动生成 uuid4）；与清算链路贯穿使用。
            scope: 执行范围（"all"/"position"/"order"）。
        """
        event_id = event_id or str(uuid.uuid4())
        _logger.critical(
            "KILL_SWITCH_ACTIVATED validator=%s event_id=%s reason=%s scope=%s",
            self.__validator_id__,
            event_id,
            reason,
            scope,
        )
        self._kill_switch_active = True

        if self._state_store is not None:
            try:
                persist_trigger_record(
                    self._state_store,
                    event_id=event_id,
                    reason=reason,
                    scope=scope,
                )
            except StateStoreError as exc:
                _logger.critical(
                    "KILL_SWITCH_PERSIST_FAIL validator=%s event_id=%s error=%s "
                    "(内存态保持熔断; 重启后可能丢失, 需人工核查)",
                    self.__validator_id__,
                    event_id,
                    exc,
                )

    def reset_kill_switch(self, confirmation: dict | None = None) -> None:
        """重置 kill switch（需人工确认后调用）。

        配置了 state_store 时先持久化解除记录，持久化失败则保持熔断
        （Fail-Closed：宁可保持熔断也不留"内存已解、重启恢复熔断"的不一致窗口）。

        Args:
            confirmation: 确认信息字典，必须包含：
                - confirmed_by: 确认人
                - holdings_verified_zero: 持仓已清零确认（True/False）
        """
        confirmed_by = "unknown"
        override_reason = ""
        if confirmation is not None:
            confirmed_by = confirmation.get("confirmed_by", "unknown")
            override_reason = confirmation.get("override_reason", "")
            holdings_verified_zero = confirmation.get("holdings_verified_zero", False)
            if not holdings_verified_zero:
                _logger.warning(
                    "KILL_SWITCH_RESET_GHOST_RISK confirmed_by=%s holdings_not_verified_zero",
                    confirmed_by,
                )
            _logger.warning(
                "KILL_SWITCH_RESET confirmed_by=%s holdings_verified_zero=%s",
                confirmed_by,
                holdings_verified_zero,
            )
        else:
            _logger.warning("KILL_SWITCH_RESET no confirmation provided")

        if self._state_store is not None:
            try:
                persist_reset_record(
                    self._state_store,
                    confirmed_by=confirmed_by,
                    override_reason=override_reason,
                )
            except StateStoreError as exc:
                _logger.critical(
                    "KILL_SWITCH_RESET_PERSIST_FAIL fail-closed保持熔断 validator=%s error=%s",
                    self.__validator_id__,
                    exc,
                )
                return

        self._kill_switch_active = False

    def detect_ghost_positions(
        self,
        broker_holdings: dict[str, dict],
        strategy_state: dict[str, str],
    ) -> list[tuple[str, dict, str]]:
        """检测 Ghost Position（策略认为已平仓但 broker 仍持有的幽灵持仓）。

        三种 Ghost 情况：
        1. 策略侧某标的 CLOSED 但 broker 仍有该标的持仓
        2. Kill Switch 已激活但 broker 仍有任意持仓
        3. 策略侧无该标的任何记录（None）但 broker 仍有持仓
           （人工建仓/其他通道建仓/crash 后策略状态丢失，裁定书 §二补登）

        Args:
            broker_holdings: symbol → position_info 字典，broker 端实际持仓
                position_info 需包含 "qty" 字段
            strategy_state: symbol → "OPEN"/"CLOSED" 字典，策略侧持仓状态

        Returns:
            ghost_positions 列表，每项为 (symbol, position_info, ghost_type) 元组
        """
        ghosts: list[tuple[str, dict, str]] = []

        # 情况 1+3：策略侧 CLOSED / 无记录，但 broker 有持仓
        for sym, pos in broker_holdings.items():
            qty = pos.get("qty", 0)
            if qty == 0:
                continue
            state = strategy_state.get(sym)
            if state == "CLOSED":
                ghosts.append((sym, pos, GHOST_STRATEGY_CLOSED))
            elif state is None:
                ghosts.append((sym, pos, GHOST_UNKNOWN_TO_STRATEGY))

        # 情况 2：Kill Switch 已激活但 broker 仍有任意持仓
        if self._kill_switch_active:
            for sym, pos in broker_holdings.items():
                qty = pos.get("qty", 0)
                if qty != 0:
                    # 避免重复（情况 1/3 已记录的标的不重复添加）
                    if not any(g[0] == sym for g in ghosts):
                        ghosts.append((sym, pos, GHOST_KILL_SWITCH_ACTIVE))

        return ghosts

    @property
    def kill_switch_active(self) -> bool:
        return self._kill_switch_active


__all__: Final = [
    "DefaultRiskValidator",
    "GHOST_KILL_SWITCH_ACTIVE",
    "GHOST_STRATEGY_CLOSED",
    "GHOST_UNKNOWN_TO_STRATEGY",
    "KILL_SWITCH_STATE_NAMESPACE",
    "load_kill_switch_record",
    "persist_reset_record",
    "persist_trigger_record",
]
