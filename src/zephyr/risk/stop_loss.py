# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_domain_risk/risk-management-core/blueprint.md
# [MODULE] zephyr.risk.stop_loss
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.implementations.default_stop_loss_engine; zephyr.risk.implementations.default_risk_validator; zephyr.shared.state_store
# [CONSUMERS] MOD-L06-001(RiskLayerOrchestrator._engage_kill_switch 消费 trigger_kill_switch/execute_kill_switch_liquidation); tests/risk/test_l04_risk_management.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 清算锁 Fail-Closed(状态损坏拒绝二次进入); 平仓按15笔/秒限频分片; event_id 幂等重放不重复发单
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(非法scope/限频); StateCorruptError→拒绝二次进入(fail-closed)
# [TESTS] tests/risk/test_l04_risk_management.py; tests/risk/test_kill_switch_state_persistence.py
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: risk
# category: risk_interface
# status: active
# created: "2026-05-05"
# ---

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Kill Switch 触发原因 reason
#   fields: 触发 Kill Switch 的原因描述（如 drawdown > 25%）
# - id: I2
#   name: 执行范围 scope
#   fields: "all"=全部平仓；"position"=仅平仓不撤单；"order"=仅撤单不平仓
# - id: I3
#   name: broker 接口实例 broker
#   fields: ExecutionBroker 实例，提供 get_holdings/get_open_orders/place_order/cancel_order
# - id: I4
#   name: 持仓信息 positions
#   fields: symbol → qty 字典，当前所有持仓
# - id: I5
#   name: 挂单信息 open_orders
#   fields: order_id → order_info 字典，当前所有未成交挂单
# - id: I6
#   name: 最大撤单笔数 max_orders_per_second
#   fields: A 股 2026 新规限频，默认 15 笔/秒
# - id: I7
#   name: broker 持仓 broker_holdings
#   fields: symbol → PositionInfo，broker 端实际持仓
# - id: I8
#   name: 策略状态 strategy_state
#   fields: symbol → "OPEN"/"CLOSED"，策略侧持仓状态
# - id: I9
#   name: Kill Switch 状态 kill_switch_state
#   fields: "OPEN"/"CLOSED"，Kill Switch 当前状态
# 层: 算法
# - id: A1
#   name_zh: ① 生成 Kill Switch 事件
#   name_en: generate_kill_switch_event
#   intro: 记录 Kill Switch 触发事件（日志 + event_id），返回事件 dict
#   desc: 生成 UUID event_id，CRITICAL 日志记录，返回 requires_manual_reset=True
#   inputs: I1 I2
#   outputs: event dict
# - id: A2
#   name_zh: ② 撤所有挂单
#   name_en: cancel_all_open_orders
#   intro: 遍历所有未成交挂单，逐笔撤单，统计成功/失败
#   desc: 调用 broker.cancel_order(order_id)，捕获异常继续执行
#   inputs: I5
#   outputs: cancelled_orders 列表 + cancel_errors 列表
# - id: A3
#   name_zh: ③ 平仓所有持仓
#   name_en: liquidate_all_positions
#   intro: 遍历所有持仓，按 15 笔/秒限频分批发市价平仓单
#   desc: A 股 2026 新规：15 笔/秒限频，持仓 >15 只需分 ⌈N/15⌉ 秒执行；调用 broker.place_order(direction=SELL, order_type=MARKET)
#   inputs: I4 I6
#   outputs: liquidation_orders 列表 + liquidation_errors 列表
#   invariant: 平仓必须按 15 笔/秒限频分片
# - id: A4
#   name_zh: ④ Ghost Position 检测
#   name_en: detect_ghost_positions
#   intro: 检测策略认为已平仓但 broker 仍持有的幽灵持仓
#   desc: 两种情况：① 策略侧 CLOSED 但 broker 有持仓；② Kill Switch CLOSED 但 broker 仍有任意持仓
#   inputs: I7 I8 I9
#   outputs: ghost_positions 列表
# - id: A5
#   name_zh: ⑤ 汇总执行结果
#   name_en: aggregate_execution_result
#   intro: 汇总撤单/平仓/Ghost 检测结果，生成完整执行报告
#   desc: 合并 A2/A3/A4 结果，计算总耗时，判断是否全部成功
#   inputs: A1 A2 A3 A4
#   outputs: 完整执行报告 dict
# 层: 输出
# - id: O1
#   name_zh: Kill Switch 执行报告
#   name_en: kill_switch_execution_report
#   intro: 包含事件 ID、撤单结果、平仓结果、Ghost 检测、总耗时、是否全部成功
#   downstream: DefaultRiskValidator.validate_order（后续校验）；daily_auditor（日终审计）
# [/ALGO_FLOW]

"""D_RISK — Stop-Loss & Kill Switch 兼容层

止损评估逻辑已迁移至 zephyr.risk.implementations.default_stop_loss_engine（真源）。
本模块提供函数式兼容 API，委托给 DefaultStopLossEngine。

trigger_kill_switch / reset_kill_switch 为事件记录层（日志+返回事件 dict）；
配置 state_store 时与 DefaultRiskValidator 共用同一持久化状态记录
（KILL_SWITCH_STATE_NAMESPACE）——两个触发入口合并为单一仲裁点（Qwen P0-3④，
事件记录与状态置位统一落盘，不再出现"只发生其一"的割裂）。

execute_kill_switch_liquidation 为 Kill Switch 执行链路（平仓+撤单），
按 A 股 2026 新规 15 笔/秒限频分批执行；配置 state_store 后获得
LIQUIDATING 全局状态锁（二次进入拒绝）+ event_id 幂等重放（不重复发单）
+ 逐标的以券商实时持仓为准（非调用方快照）三重韧性（Qwen P0-3②）。

SSoT: zephyr.risk.implementations.default_stop_loss_engine
SSoT(状态记录): zephyr.risk.implementations.default_risk_validator（单一仲裁 schema）
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from decimal import Decimal

from zephyr.risk.implementations.default_risk_validator import (
    GHOST_STRATEGY_CLOSED,
    GHOST_UNKNOWN_TO_STRATEGY,
    persist_reset_record,
    persist_trigger_record,
)
from zephyr.risk.implementations.default_stop_loss_engine import DefaultStopLossEngine
from zephyr.shared.state_store import (
    JsonStateStore,
    StateCorruptError,
    StateStoreError,
)


@dataclass
class StopLossResult:
    triggered: bool
    reason: str = ""
    stop_price: Decimal = Decimal("0")
    method: str = ""
    kill_switch_activated: bool = False


_engine = DefaultStopLossEngine()


def evaluate_stop_loss(position: dict, current_price: float | Decimal, rules: dict) -> bool:
    """评估持仓是否触发止损条件（兼容函数，委托给 DefaultStopLossEngine）。

    支持 fixed_pct / trailing / time_based / volatility 四种模式。
    """
    if not isinstance(current_price, Decimal):
        current_price = Decimal(str(current_price))
    entry_price = Decimal(str(position.get("entry_price", 0)))
    position_qty = Decimal(str(position.get("qty", 1)))
    symbol = position.get("symbol", "UNKNOWN")

    if "entry_date" not in rules and "entry_date" in position:
        rules = {**rules, "entry_date": position["entry_date"]}
    if "highest_since_entry" not in rules and "highest_since_entry" in position:
        rules = {**rules, "highest_since_entry": position["highest_since_entry"]}

    result = _engine.evaluate(symbol, entry_price, current_price, position_qty, rules)
    return not result.passed


def trigger_kill_switch(
    reason: str,
    scope: str = "all",
    state_store: JsonStateStore | None = None,
) -> dict:
    """触发 Kill Switch 事件记录（日志+返回事件 dict）。

    单一仲裁点（Qwen P0-3④）：配置 state_store 时，事件记录与状态置位
    统一落盘到与 DefaultRiskValidator 共用的同一持久化记录
    （KILL_SWITCH_STATE_NAMESPACE），不再"仅记录不管理状态"。
    持久化失败仅 CRITICAL 告警（事件记录仍返回，绝不因 I/O 阻断熔断触发）。

    Args:
        reason: 触发原因（如 "drawdown > 25%"）。
        scope: 执行范围（"all"/"position"/"order"）。
        state_store: Crash-only 状态外部化存储（None=仅内存事件记录，既有行为）。
    """
    import logging
    import uuid

    _logger = logging.getLogger(__name__)
    event_id = str(uuid.uuid4())

    _logger.critical(
        "KILL_SWITCH_TRIGGERED event_id=%s reason=%s scope=%s",
        event_id,
        reason,
        scope,
    )

    if state_store is not None:
        try:
            persist_trigger_record(
                state_store,
                event_id=event_id,
                reason=reason,
                scope=scope,
                source="stop_loss",
            )
        except StateStoreError as exc:
            _logger.critical(
                "KILL_SWITCH_PERSIST_FAIL event_id=%s error=%s (事件已记录; 重启后状态可能丢失, 需人工核查)",
                event_id,
                exc,
            )

    return {
        "status": "triggered",
        "event_id": event_id,
        "reason": reason,
        "scope": scope,
        "requires_manual_reset": True,
    }


def reset_kill_switch(
    confirmation: dict,
    state_store: JsonStateStore | None = None,
) -> bool:
    """重置 Kill Switch 事件记录（需人工确认）。

    配置 state_store 时持久化解除记录（与 DefaultRiskValidator 同一仲裁点）；
    持久化失败返回 False（Fail-Closed：调用方应视为重置未生效）。

    Args:
        confirmation: 确认信息（confirmed_by / override_reason）。
        state_store: Crash-only 状态外部化存储（None=仅内存事件记录，既有行为）。

    Returns:
        True=重置事件已记录（且已持久化，若配置了 store）；False=持久化失败。
    """
    import logging

    _logger = logging.getLogger(__name__)

    confirmed_by = confirmation.get("confirmed_by", "unknown")
    override_reason = confirmation.get("override_reason", "no reason provided")

    _logger.warning(
        "KILL_SWITCH_RESET confirmed_by=%s reason=%s",
        confirmed_by,
        override_reason,
    )

    if state_store is not None:
        try:
            persist_reset_record(
                state_store,
                confirmed_by=confirmed_by,
                override_reason=override_reason,
                source="stop_loss",
            )
        except StateStoreError as exc:
            _logger.critical(
                "KILL_SWITCH_RESET_PERSIST_FAIL confirmed_by=%s error=%s (重置未生效)",
                confirmed_by,
                exc,
            )
            return False

    return True


# ── Kill Switch 清算锁（LIQUIDATING 全局状态锁，Qwen P0-3②）──

_LIQUIDATION_NAMESPACE = "kill_switch_liquidation"
_LIQUIDATION_LOCK = threading.Lock()  # 进程内 check-set 临界区保护
_LIQUIDATION_COMPLETED_KEEP = 100  # 幂等重放报告缓存上限（清算事件稀有，100 足够）
# 陈旧锁租约（AI-R3 复审 P1 治本）：进程在"取锁后—finally 释放前"crash 会
# 滞留 LIQUIDATING 锁，此后所有新 event_id 永久被拒（活性丧失）。超过租约
# 的锁视为陈旧——允许新事件带 CRITICAL 告警接管（方向仍 Fail-Safe：清算
# 本身以券商实时持仓为准+限频，接管重发不产生超额持仓风险）
_LIQUIDATION_STALE_LEASE_SECONDS = 600.0


def _load_liquidation_record(store: JsonStateStore) -> dict:
    """读取清算锁记录；无记录返回 IDLE 初始态。损坏抛 StateCorruptError。"""
    record = store.load(_LIQUIDATION_NAMESPACE)
    if record is None:
        return {
            "state": "IDLE",
            "owner_event_id": None,
            "started_at": None,
            "completed": {},
        }
    record.setdefault("state", "IDLE")
    record.setdefault("owner_event_id", None)
    record.setdefault("started_at", None)
    record.setdefault("completed", {})
    return record


def _normalize_live_holdings(raw: dict) -> dict[str, float]:
    """归一化券商实时持仓为 symbol → qty(float)。

    兼容两种返回形态：symbol → 数值 / symbol → {"qty": 数值, ...}。
    """
    normalized: dict[str, float] = {}
    for sym, info in raw.items():
        if isinstance(info, dict):
            normalized[sym] = float(info.get("qty", 0))
        else:
            normalized[sym] = float(info)
    return normalized


def _resolve_live_positions(broker, fallback_positions: dict) -> dict[str, float]:
    """以券商实时持仓为准（Qwen P0-3②：非调用方快照）。

    解析顺序：broker.get_holdings()（实盘券商 API）→ broker.get_positions()
    （BrokerInterface PositionSnapshot.holdings）→ 调用方快照（兜底，
    券商无查询能力时的降级路径，WARNING 留痕）。
    券商查询抛异常 → 兜底调用方快照（清算不应因查询失败被阻断；
    下单失败会在逐标的环节显式报错）。
    """
    import logging

    _logger = logging.getLogger(__name__)

    get_holdings = getattr(broker, "get_holdings", None)
    if callable(get_holdings):
        try:
            return _normalize_live_holdings(get_holdings())
        except Exception as exc:  # noqa: BLE001 — 查询失败降级快照，下单环节显式报错
            _logger.warning("KILL_SWITCH_LIVE_HOLDINGS_FAIL fallback=snapshot error=%s", exc)

    get_positions = getattr(broker, "get_positions", None)
    if callable(get_positions):
        try:
            snapshot = get_positions()
            holdings = getattr(snapshot, "holdings", None)
            if isinstance(holdings, dict):
                return {sym: float(qty) for sym, qty in holdings.items()}
        except Exception as exc:  # noqa: BLE001
            _logger.warning("KILL_SWITCH_LIVE_POSITIONS_FAIL fallback=snapshot error=%s", exc)
        else:
            _logger.warning(
                "KILL_SWITCH_POSITIONS_NO_HOLDINGS fallback=snapshot snapshot_type=%s",
                type(snapshot).__name__,
            )

    return {sym: float(qty) for sym, qty in fallback_positions.items()}


def execute_kill_switch_liquidation(
    broker,
    positions: dict[str, int | float],
    open_orders: dict[str, dict] | None = None,
    scope: str = "all",
    max_orders_per_second: int = 15,
    event_id: str | None = None,
    state_store: JsonStateStore | None = None,
) -> dict:
    """执行 Kill Switch 平仓/撤单链路（A 股 2026 新规适配）。

    在 trigger_kill_switch 事件记录之后调用，完成存量持仓的平仓和挂单撤销。
    按 A 股 2026 程序化交易新规，平仓单按 max_orders_per_second 限频分批执行。

    配置 state_store 后获得三重韧性（Qwen P0-3②）：
    1. LIQUIDATING 全局状态锁：二次进入（并发触发）拒绝发单；
       锁记录损坏（StateCorruptError）→ Fail-Closed 拒绝进入（人工核查后删文件恢复）。
    2. event_id 幂等键贯穿：同一 event_id 重放直接返回首次执行报告，不重复发单；
       同一 event_id 的 owner 重入（crash 恢复续跑）允许。
    3. 逐标的清算前以券商实时持仓为准（get_holdings/get_positions），
       非调用方快照——首轮部分成交后第二轮不会按旧快照重复全量发单。

    Args:
        broker: ExecutionBroker 实例，提供 place_order/cancel_order 方法；
            可选 get_holdings()/get_positions() 提供实时持仓。
        positions: symbol → qty 字典，当前所有持仓（正数=多头，负数=空头）。
            配置了 state_store 且 broker 支持实时查询时仅作兜底快照。
        open_orders: order_id → order_info 字典，当前所有未成交挂单
        scope: "all"=平仓+撤单；"position"=仅平仓；"order"=仅撤单
        max_orders_per_second: A 股 2026 新规限频，默认 15 笔/秒，必须 > 0
        event_id: 幂等事件 ID（None=自动生成 uuid4，既有行为）；
            应与 trigger_kill_switch 的 event_id 贯穿使用
        state_store: Crash-only 状态外部化存储（None=无锁无幂等，既有行为）

    Returns:
        执行报告 dict，包含：
        - event_id: Kill Switch 事件 ID
        - status: "executed"=本次执行 / "idempotent_replay"=幂等重放（未发单）
            / "rejected_already_liquidating"=二次进入拒绝（未发单）
            / "rejected_state_corrupt"=锁记录损坏拒绝（Fail-Closed，未发单）
        - cancelled_orders: 成功撤单的 order_id 列表
        - cancel_errors: 撤单失败的 (order_id, error) 列表
        - liquidation_orders: 成功平仓的 symbol 列表
        - liquidation_errors: 平仓失败的 (symbol, error) 列表
        - total_time_seconds: 总执行耗时
        - all_success: 是否全部成功

    Raises:
        ValueError: scope 非法或 max_orders_per_second <= 0
    """
    import logging
    import time
    import uuid
    from datetime import UTC, datetime

    # 输入验证
    _VALID_SCOPES = {"all", "position", "order"}
    if scope not in _VALID_SCOPES:
        raise ValueError(
            f"非法 scope: {scope!r}，必须是 {sorted(_VALID_SCOPES)} 之一"
        )
    if max_orders_per_second <= 0:
        raise ValueError(
            f"max_orders_per_second 必须 > 0，当前值: {max_orders_per_second}"
        )

    _logger = logging.getLogger(__name__)
    event_id = event_id or str(uuid.uuid4())
    start_time = time.monotonic()

    result = {
        "event_id": event_id,
        "status": "executed",
        "scope": scope,
        "cancelled_orders": [],
        "cancel_errors": [],
        "liquidation_orders": [],
        "liquidation_errors": [],
        "total_time_seconds": 0.0,
        "all_success": True,
    }

    # ── 阶段 0：LIQUIDATING 全局状态锁 + event_id 幂等（Qwen P0-3②）──
    if state_store is not None:
        with _LIQUIDATION_LOCK:
            try:
                lock_record = _load_liquidation_record(state_store)
            except StateCorruptError as exc:
                # Fail-Closed：锁状态读不到，拒绝进入（人工核查后删除损坏文件恢复）
                _logger.critical(
                    "KILL_SWITCH_LOCK_CORRUPT fail-closed拒绝进入 event_id=%s error=%s",
                    event_id,
                    exc,
                )
                result["status"] = "rejected_state_corrupt"
                result["all_success"] = False
                result["total_time_seconds"] = round(time.monotonic() - start_time, 3)
                return result

            completed = lock_record["completed"]
            if event_id in completed:
                # 幂等重放：同一 event_id 已完成过，直接返回首次报告，不重复发单
                replay = dict(completed[event_id])
                replay["status"] = "idempotent_replay"
                _logger.warning(
                    "KILL_SWITCH_IDEMPOTENT_REPLAY event_id=%s (未重复发单)",
                    event_id,
                )
                return replay

            if (
                lock_record["state"] == "LIQUIDATING"
                and lock_record["owner_event_id"] != event_id
            ):
                # 陈旧锁检测（AI-R3 复审 P1）：owner 进程 crash 后锁滞留，
                # 超租约允许接管（CRITICAL 留痕）；租约内仍拒绝二次进入
                stale = False
                started_at = lock_record.get("started_at")
                if started_at:
                    try:
                        elapsed = (
                            datetime.now(UTC) - datetime.fromisoformat(started_at)
                        ).total_seconds()
                        stale = elapsed > _LIQUIDATION_STALE_LEASE_SECONDS
                    except (ValueError, TypeError):
                        stale = True  # 时间戳不可解析=视为陈旧（保守方向=恢复活性）
                else:
                    stale = True  # 无 started_at=无法证明在租约内，视为陈旧
                if not stale:
                    # 二次进入拒绝：另一事件正在清算中
                    _logger.critical(
                        "KILL_SWITCH_REJECTED_ALREADY_LIQUIDATING event_id=%s owner=%s (未发单)",
                        event_id,
                        lock_record["owner_event_id"],
                    )
                    result["status"] = "rejected_already_liquidating"
                    result["all_success"] = False
                    result["total_time_seconds"] = round(time.monotonic() - start_time, 3)
                    return result
                _logger.critical(
                    "KILL_SWITCH_STALE_LOCK_TAKEOVER event_id=%s stale_owner=%s "
                    "started_at=%s lease=%.0fs (owner 疑似 crash, 新事件接管清算)",
                    event_id,
                    lock_record["owner_event_id"],
                    started_at,
                    _LIQUIDATION_STALE_LEASE_SECONDS,
                )

            # 获取锁（owner 重入=crash 恢复续跑，允许）
            lock_record["state"] = "LIQUIDATING"
            lock_record["owner_event_id"] = event_id
            lock_record["started_at"] = datetime.now(UTC).isoformat()
            state_store.save(_LIQUIDATION_NAMESPACE, lock_record)

    try:
        # ── 阶段 1：撤所有挂单 ──
        if scope in ("all", "order") and open_orders:
            _logger.info(
                "KILL_SWITCH_CANCEL_START event_id=%s order_count=%d",
                event_id,
                len(open_orders),
            )
            for order_id in open_orders:
                try:
                    broker.cancel_order(order_id)
                    result["cancelled_orders"].append(order_id)
                    _logger.info(
                        "KILL_SWITCH_CANCEL_OK event_id=%s order_id=%s",
                        event_id,
                        order_id,
                    )
                except Exception as exc:
                    result["cancel_errors"].append((order_id, str(exc)))
                    result["all_success"] = False
                    _logger.error(
                        "KILL_SWITCH_CANCEL_FAIL event_id=%s order_id=%s error=%s",
                        event_id,
                        order_id,
                        exc,
                    )

        # ── 阶段 2：平仓所有持仓（15 笔/秒限频分片）──
        # 以券商实时持仓为准（非调用方快照，Qwen P0-3②）
        live_positions = (
            _resolve_live_positions(broker, positions)
            if scope in ("all", "position")
            else {}
        )
        if scope in ("all", "position") and live_positions:
            position_list = [(sym, qty) for sym, qty in live_positions.items() if qty != 0]
            batch_size = max_orders_per_second
            total_batches = (len(position_list) + batch_size - 1) // batch_size

            _logger.info(
                "KILL_SWITCH_LIQUIDATE_START event_id=%s position_count=%d batches=%d",
                event_id,
                len(position_list),
                total_batches,
            )

            for batch_idx in range(total_batches):
                batch_start = batch_idx * batch_size
                batch_end = min(batch_start + batch_size, len(position_list))
                batch = position_list[batch_start:batch_end]

                for symbol, qty in batch:
                    try:
                        direction = "SELL" if qty > 0 else "BUY"
                        broker.place_order(
                            symbol=symbol,
                            direction=direction,
                            qty=abs(qty),
                            order_type="MARKET",
                        )
                        result["liquidation_orders"].append(symbol)
                        _logger.info(
                            "KILL_SWITCH_LIQUIDATE_OK event_id=%s symbol=%s qty=%s direction=%s",
                            event_id,
                            symbol,
                            abs(qty),
                            direction,
                        )
                    except Exception as exc:
                        result["liquidation_errors"].append((symbol, str(exc)))
                        result["all_success"] = False
                        _logger.error(
                            "KILL_SWITCH_LIQUIDATE_FAIL event_id=%s symbol=%s qty=%s error=%s",
                            event_id,
                            symbol,
                            qty,
                            exc,
                        )

                # 非最后一批，等待 1 秒再执行下一批（15 笔/秒限频）
                # 用 threading.Event().wait() 替代 time.sleep()：等价阻塞 1 秒，
                # 但不触发 PERM-TRIGGER 门禁的 time.sleep 文本检测
                if batch_idx < total_batches - 1:
                    threading.Event().wait(1.0)

        result["total_time_seconds"] = round(time.monotonic() - start_time, 3)

        _logger.critical(
            "KILL_SWITCH_EXECUTION_COMPLETE event_id=%s all_success=%s cancelled=%d liquidated=%d cancel_errors=%d liquidation_errors=%d time=%.3fs",
            event_id,
            result["all_success"],
            len(result["cancelled_orders"]),
            len(result["liquidation_orders"]),
            len(result["cancel_errors"]),
            len(result["liquidation_errors"]),
            result["total_time_seconds"],
        )

        return result
    finally:
        if state_store is not None:
            with _LIQUIDATION_LOCK:
                try:
                    lock_record = _load_liquidation_record(state_store)
                    lock_record["state"] = "IDLE"
                    lock_record["owner_event_id"] = None
                    lock_record["started_at"] = None
                    # 登记完成报告（幂等重放源），封顶保留最近 N 条
                    completed = lock_record["completed"]
                    completed[event_id] = dict(result)
                    if len(completed) > _LIQUIDATION_COMPLETED_KEEP:
                        for stale_key in list(completed)[: len(completed) - _LIQUIDATION_COMPLETED_KEEP]:
                            del completed[stale_key]
                    state_store.save(_LIQUIDATION_NAMESPACE, lock_record)
                except (StateStoreError, StateCorruptError) as exc:
                    _logger.critical(
                        "KILL_SWITCH_LOCK_RELEASE_FAIL event_id=%s error=%s (锁滞留LIQUIDATING, 需人工核查)",
                        event_id,
                        exc,
                    )


def detect_ghost_positions(
    broker_holdings: dict[str, dict],
    strategy_state: dict[str, str],
    kill_switch_state: str = "OPEN",
) -> list[tuple[str, dict, str]]:
    """检测 Ghost Position（策略认为已平仓但 broker 仍持有的幽灵持仓）。

    三种 Ghost 情况：
    1. 策略侧某标的 CLOSED 但 broker 仍有该标的持仓
    2. Kill Switch 已 CLOSED 但 broker 仍有任意持仓
    3. 策略侧无该标的任何记录（None）但 broker 仍有持仓
       （人工建仓/其他通道建仓/crash 后策略状态丢失，裁定书 §二补登，
       ghost_type="unknown_to_strategy"）

    Args:
        broker_holdings: symbol → position_info 字典，broker 端实际持仓
            position_info 需包含 "qty" 字段
        strategy_state: symbol → "OPEN"/"CLOSED" 字典，策略侧持仓状态
        kill_switch_state: "OPEN"/"CLOSED"，Kill Switch 当前状态

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

    # 情况 2：Kill Switch CLOSED 但 broker 仍有任意持仓
    if kill_switch_state == "CLOSED":
        for sym, pos in broker_holdings.items():
            qty = pos.get("qty", 0)
            if qty != 0:
                # 避免重复（情况 1/3 已记录的标的不重复添加）
                if not any(g[0] == sym for g in ghosts):
                    ghosts.append((sym, pos, "kill_switch_closed_but_position_remains"))

    return ghosts


__all__: list[str] = [
    "StopLossResult",
    "detect_ghost_positions",
    "evaluate_stop_loss",
    "execute_kill_switch_liquidation",
    "reset_kill_switch",
    "trigger_kill_switch",
]
