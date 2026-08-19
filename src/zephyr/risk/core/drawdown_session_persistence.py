# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.15/§3.18/§6.12
# [MODULE] zephyr.risk.core.drawdown_session_persistence
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.state_store; zephyr.risk.stop_loss(import-only); zephyr.risk.core.drawdown_state_machine
# [CONSUMERS] RiskOrchestrator(§6.5 接线位); 盘前启动序列/盘后日终批
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 盘前=§3.15四阶段顺序不可调换(先Ghost核对→再状态机→后基线校准→末健康检查); 盘后=§3.15加载逆序(先存被依赖项); 审计门控失败不持久化(mark AUDIT_FAILED_SKIP); 全成功才标DRAWDOWN_COMPLETE(原子提交点,部分失败次日冷启动默认NORMAL); peak单调非减(max()保证); nav_history滚动252日窗口; 状态损坏抛StateCorruptError不静默兜底
# [MODIFY-GUARD] tests/risk/test_drawdown_session_persistence.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSessionPersistInputError(ZA-RK-0062)
# [TESTS] tests/risk/test_drawdown_session_persistence.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: JsonStateStore(6命名空间: peak_nav/nav_history/entry_var/attribution/strategy_state/persistable)
# I2: 盘前输入(broker_holdings+strategy_state+kill_switch_state+health_check探针)
# I3: 盘后输入(closing_nav+state_machine+var_95+attribution_result+strategy_holdings+audit门控)
# F1: premarket_initialization(Ghost核对→状态机恢复/冷启动→peak+nav_history基线(不足30日保守50%cap)→健康检查→entry_var/prev_attribution)
# F2: postmarket_persist(审计门控→终态nav→peak max→状态机→nav_history append/trim→entry_var→归因→策略持仓→标COMPLETE)
# A1: 低层存取原语对(save/load peak_nav·entry_var·attribution·strategy_state + append/trim nav_history + mark/load persistable)
# O1: PremarketResult(status READY/REFUSED+状态机+基线) / PostmarketResult(status PERSISTED/SKIPPED+peak对)
# [/ALGO_FLOW]
"""D_RISK — 盘前初始化 + 盘后持久化配对编排（35 号 memo §3.15/§3.18/§6.12 施工）。

痛点（§3.15/§3.18 代码差距）：无 state_store 持久化配对——peak NAV/状态机态/
recovery_step/nav_history/entry_var 重启即丢失；盘前"加载"无源可载；
盘后无原子提交点（部分持久化成功产生不一致快照）。

本模块落地：
  - 6 个命名空间的低层存取原语对（save/load 配对，JsonStateStore 原子写）。
  - premarket_initialization（§3.15 四阶段，顺序不可调换）：
    ① Ghost 持仓核对（冷启动 strategy_state=None → broker 有持仓全视为 Ghost）
    ② DrawdownStateMachine 恢复（None=冷启动默认 NORMAL，保守不假设 RECOVERY）
    ③ 基线校准（peak NAV 单调非减 / nav_history 窗口，不足 30 日保守 cap 50%）
    ④ 执行通道健康检查（探针注入，不健康 → RefuseStart）
  - postmarket_persist（§3.18，§3.15 加载逆序）：
    审计门控 → 终态净值 → peak → 状态机 → nav_history → entry_var → 归因
    → 策略持仓 → mark_persistable(DRAWDOWN_COMPLETE) 原子提交点。
    审计失败 → 标 AUDIT_FAILED_SKIP 直接返回（宁可丢状态不可存错误状态）。

SSoT: 35_drawdown_protocol_impl §3.15/§3.18 + §6.12（P0 配对施工项）
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Final, Mapping, Sequence

from zephyr.risk.core.drawdown_state_machine import DrawdownStateMachine
from zephyr.risk.stop_loss import detect_ghost_positions
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.state_store import JsonStateStore

__all__: Final = [
    "InvalidSessionPersistInputError",
    "PremarketResult",
    "PostmarketResult",
    "PEAK_NAV_NAMESPACE",
    "NAV_HISTORY_NAMESPACE",
    "ENTRY_VAR_NAMESPACE",
    "ATTRIBUTION_NAMESPACE",
    "STRATEGY_STATE_NAMESPACE",
    "PERSISTABLE_NAMESPACE",
    "STATUS_DRAWDOWN_COMPLETE",
    "STATUS_AUDIT_FAILED_SKIP",
    "MIN_NAV_HISTORY",
    "NAV_HISTORY_WINDOW",
    "save_peak_nav",
    "load_peak_nav",
    "append_nav_history",
    "load_nav_history",
    "save_entry_var",
    "load_entry_var",
    "save_attribution_result",
    "load_attribution_result",
    "save_strategy_state",
    "load_strategy_state",
    "mark_persistable",
    "load_persistable_status",
    "premarket_initialization",
    "postmarket_persist",
]

_logger = logging.getLogger(__name__)

# ── 命名空间常量（§3.15/§3.18 配对契约）──
PEAK_NAV_NAMESPACE: Final = "drawdown_peak_nav"
NAV_HISTORY_NAMESPACE: Final = "drawdown_nav_history"
ENTRY_VAR_NAMESPACE: Final = "drawdown_entry_var"
ATTRIBUTION_NAMESPACE: Final = "drawdown_attribution_result"
STRATEGY_STATE_NAMESPACE: Final = "drawdown_strategy_state"
PERSISTABLE_NAMESPACE: Final = "drawdown_persistable"

#: 原子提交点状态（§3.18 阶段 5 两阶段标记之回撤层标记）
STATUS_DRAWDOWN_COMPLETE: Final = "DRAWDOWN_COMPLETE"
STATUS_AUDIT_FAILED_SKIP: Final = "AUDIT_FAILED_SKIP"

#: 最小回撤计算窗口（§3.15：对齐 36 号 §2.3 var_calculator min_history=30）
MIN_NAV_HISTORY: Final = 30
#: nav_history 滚动窗口（§3.18 阶段 4 trim 252 日）
NAV_HISTORY_WINDOW: Final = 252


class InvalidSessionPersistInputError(ZephyrBaseError):
    """盘前/盘后编排输入非法（净值非正/窗口非法/载荷畸形）。"""

    error_code = "ZA-RK-0062"


# ── 结果数据模型 ──


@dataclass(frozen=True)
class PremarketResult:
    """盘前初始化结果（§3.15 InitializationResult）。

    Attributes:
        status: "READY"=可启动 / "REFUSED"=拒绝启动（Ghost 检出或通道不健康）
        refuse_reason: 拒绝原因（READY 时 None）
        ghosts: Ghost 持仓列表 [(symbol, position_info, ghost_type)]
        state_machine: 恢复/新建的状态机（REFUSED 时 None）
        restored_state: "cold_start_default_NORMAL" 或 "restored_<STATE>"
        kill_switch_still_closed: 持久化态为 KILL（盘前保持禁开仓，待人工复位）
        peak_nav: 持久化 peak（None=无记录）
        nav_history: 滚动窗口净值序列（旧→新）
        insufficient_history: nav_history 不足 MIN_NAV_HISTORY（保守冷启动标记）
        conservative_position_cap: 历史不足时的保守仓位上限（0.5；否则 None）
        entry_var: 前日盘前 VaR_95 快照（None=首次/未持久化）
        prev_attribution: 前日归因结果（None=正常降级）
    """

    status: str
    refuse_reason: str | None = None
    ghosts: list[tuple[str, dict, str]] = field(default_factory=list)
    state_machine: DrawdownStateMachine | None = None
    restored_state: str = "cold_start_default_NORMAL"
    kill_switch_still_closed: bool = False
    peak_nav: float | None = None
    nav_history: tuple[float, ...] = ()
    insufficient_history: bool = False
    conservative_position_cap: float | None = None
    entry_var: float | None = None
    prev_attribution: dict[str, Any] | None = None


@dataclass(frozen=True)
class PostmarketResult:
    """盘后持久化结果（§3.18）。

    Attributes:
        status: "PERSISTED"=已标 DRAWDOWN_COMPLETE / "SKIPPED_AUDIT_FAILED"=审计门控跳过
        closing_nav: 终态净值
        old_peak / new_peak: peak 更新对（new_peak ≥ old_peak，单调非减）
        is_new_high: 当日是否创新高
        persistable_status: 实际写入的提交标记
    """

    status: str
    closing_nav: float
    old_peak: float | None
    new_peak: float
    is_new_high: bool
    persistable_status: str


# ── 低层存取原语对（save/load 配对）──


def save_peak_nav(store: JsonStateStore, peak_nav: float) -> None:
    """保存 peak NAV（调用方须以 max(old, closing) 保证单调非减）。"""
    if peak_nav <= 0:
        raise InvalidSessionPersistInputError(f"peak_nav 须为正, got {peak_nav}")
    store.save(PEAK_NAV_NAMESPACE, {"peak_nav": peak_nav})


def load_peak_nav(store: JsonStateStore) -> float | None:
    """加载 peak NAV。None=无记录（fresh boot）。"""
    data = store.load(PEAK_NAV_NAMESPACE)
    if data is None:
        return None
    return float(data["peak_nav"])


def append_nav_history(
    store: JsonStateStore,
    trade_date: date,
    nav: float,
    *,
    window: int = NAV_HISTORY_WINDOW,
) -> int:
    """追加当日净值并 trim 滚动窗口（同日重复调用=更新当日，幂等）。

    Returns: trim 后的窗口长度。
    """
    if nav <= 0:
        raise InvalidSessionPersistInputError(f"nav 须为正, got {nav}")
    if window < 1:
        raise InvalidSessionPersistInputError(f"window 须 >= 1, got {window}")
    history = _load_nav_history_records(store)
    iso = trade_date.isoformat()
    if history and history[-1].get("date") == iso:
        history[-1] = {"date": iso, "nav": nav}
    else:
        history.append({"date": iso, "nav": nav})
    history = history[-window:]
    store.save(NAV_HISTORY_NAMESPACE, {"history": history})
    return len(history)


def load_nav_history(store: JsonStateStore) -> tuple[float, ...]:
    """加载 nav_history（旧→新）。空 tuple=无记录。"""
    return tuple(float(r["nav"]) for r in _load_nav_history_records(store))


def save_entry_var(store: JsonStateStore, trade_date: date, var_95: float) -> None:
    """保存当日盘前 VaR_95 快照（§3.18 阶段 4b，供次日 §3.15 加载 + §3.16 归因）。"""
    if var_95 < 0:
        raise InvalidSessionPersistInputError(f"var_95 须 >= 0, got {var_95}")
    store.save(ENTRY_VAR_NAMESPACE, {"date": trade_date.isoformat(), "var_95": var_95})


def load_entry_var(store: JsonStateStore) -> float | None:
    """加载最近一次 entry_var。None=首次/未持久化（§3.15 正常降级跳过）。"""
    data = store.load(ENTRY_VAR_NAMESPACE)
    if data is None:
        return None
    return float(data["var_95"])


def save_attribution_result(
    store: JsonStateStore, trade_date: date, attribution: Mapping[str, Any]
) -> None:
    """保存归因结果（§3.18 阶段 4c，供次日盘前加载参考）。"""
    store.save(
        ATTRIBUTION_NAMESPACE,
        {"date": trade_date.isoformat(), "result": dict(attribution)},
    )


def load_attribution_result(store: JsonStateStore) -> dict[str, Any] | None:
    """加载最近一次归因结果。None=正常降级。"""
    data = store.load(ATTRIBUTION_NAMESPACE)
    if data is None:
        return None
    result = data.get("result")
    return dict(result) if isinstance(result, Mapping) else None


def save_strategy_state(
    store: JsonStateStore, trade_date: date, holdings: Mapping[str, Any]
) -> None:
    """保存策略目标持仓快照（§3.18 阶段 4d，次日 Ghost 检测基准）。"""
    store.save(
        STRATEGY_STATE_NAMESPACE,
        {"date": trade_date.isoformat(), "holdings": dict(holdings)},
    )


def load_strategy_state(store: JsonStateStore) -> dict[str, Any] | None:
    """加载策略持仓快照。None=冷启动/首次（§3.15 冷启动守卫数据源）。"""
    data = store.load(STRATEGY_STATE_NAMESPACE)
    if data is None:
        return None
    holdings = data.get("holdings")
    return dict(holdings) if isinstance(holdings, Mapping) else None


def mark_persistable(store: JsonStateStore, trade_date: date, status: str) -> None:
    """原子提交点标记（§3.18 阶段 5）：全成功才标 DRAWDOWN_COMPLETE。"""
    if status not in (STATUS_DRAWDOWN_COMPLETE, STATUS_AUDIT_FAILED_SKIP):
        raise InvalidSessionPersistInputError(f"非法 persistable 状态: {status!r}")
    store.save(PERSISTABLE_NAMESPACE, {"date": trade_date.isoformat(), "status": status})


def load_persistable_status(store: JsonStateStore) -> str | None:
    """加载提交标记。None=上次未正常持久化（§3.15 据此冷启动默认 NORMAL）。"""
    data = store.load(PERSISTABLE_NAMESPACE)
    if data is None:
        return None
    status = data.get("status")
    return str(status) if status is not None else None


def _load_nav_history_records(store: JsonStateStore) -> list[dict[str, Any]]:
    data = store.load(NAV_HISTORY_NAMESPACE)
    if data is None:
        return []
    history = data.get("history", [])
    if not isinstance(history, list):
        raise InvalidSessionPersistInputError("nav_history 载荷非 list")
    return [dict(r) for r in history]


# ── 编排：盘前初始化（§3.15 四阶段）──


def premarket_initialization(
    store: JsonStateStore,
    *,
    broker_holdings: Mapping[str, dict] | None = None,
    strategy_state: Mapping[str, Any] | None = None,
    kill_switch_state: str = "OPEN",
    state_machine: DrawdownStateMachine | None = None,
    min_history: int = MIN_NAV_HISTORY,
    conservative_cap: float = 0.50,
    health_check: Callable[[], bool] | None = None,
) -> PremarketResult:
    """盘前初始化：Ghost 核对 → 状态机恢复 → 基线校准 → 健康检查。

    顺序不可调换（§3.15）：先核对持仓（防 Ghost），再加载状态机
    （防基于错误持仓恢复），最后校准基线与健康检查。

    Args:
        store: Crash-only 状态存储（6 命名空间真源）
        broker_holdings: 实盘真实持仓 {symbol: {"qty": ...}}（None=按空仓处理）
        strategy_state: 策略侧持仓状态 {symbol: "OPEN"/"CLOSED"}；
            None=冷启动守卫——broker 有持仓全部视为 Ghost（来源不明）
        kill_switch_state: Kill Switch 状态（Ghost 检测情况 2 输入）
        state_machine: 注入的状态机实例（None=本函数以 store 新建）
        min_history: 最小回撤计算窗口（默认 30，对齐 36 号 §2.3）
        conservative_cap: 历史不足时的保守仓位上限（默认 0.50）
        health_check: 执行通道健康探针（None=跳过；返回 False → RefuseStart）

    Returns:
        PremarketResult（status="READY" 可启动 / "REFUSED" 拒绝启动）

    Raises:
        StateCorruptError: 任一持久化记录损坏——fail-closed，调用方拒绝启动。
    """
    # ── 阶段 1 broker 持仓核对（防 Ghost Position，§3.5.1）──
    holdings = dict(broker_holdings or {})
    if strategy_state is None:
        # 冷启动守卫：无策略记录却有持仓 → 来源不明，全部视为 Ghost
        ghosts = [
            (sym, dict(info), "unknown_to_strategy")
            for sym, info in holdings.items()
            if isinstance(info, Mapping) and info.get("qty", 0) != 0
        ]
    else:
        ghosts = detect_ghost_positions(holdings, dict(strategy_state), kill_switch_state)
    if ghosts:
        _logger.critical("PREMARKET_GHOST_DETECTED ghosts=%s", [g[0] for g in ghosts])
        return PremarketResult(
            status="REFUSED",
            refuse_reason="存在 Ghost Position，拒绝启动，需人工清零持仓",
            ghosts=ghosts,
        )

    # ── 阶段 2 加载 DrawdownStateMachine 持久化状态（§3.11 转换守卫记忆）──
    machine = state_machine if state_machine is not None else DrawdownStateMachine(store)
    restored = machine.load_or_none()
    if restored is None:
        restored_state = "cold_start_default_NORMAL"  # 保守：不假设上次在 RECOVERY
    else:
        restored_state = f"restored_{restored.current.value}"
    _logger.info("PREMARKET_STATE_RECOVERY %s", restored_state)
    # Kill Switch 终态校验：上次收盘 == KILL → 盘前保持禁开仓（人工复位才能解除）
    kill_switch_still_closed = machine.kill_switch_closed
    if kill_switch_still_closed:
        _logger.warning("PREMARKET_KILL_SWITCH_CLOSED 盘前禁开仓，等待人工复位")

    # ── 阶段 3 基线校准（peak NAV / nav_history / entry_var）──
    peak_nav = load_peak_nav(store)  # peak 单调非减（§3.8），从持久化加载
    nav_history = load_nav_history(store)
    insufficient = len(nav_history) < min_history
    if insufficient:
        # 历史不足 → 保守冷启动（§3.15）：强制 conservative cap + 审计标记
        _logger.warning(
            "COLD_START_INSUFFICIENT_HISTORY available=%d required=%d cap=%.2f",
            len(nav_history), min_history, conservative_cap,
        )
    entry_var = load_entry_var(store)
    prev_attribution = load_attribution_result(store)

    # ── 阶段 4 执行通道健康检查（§3.5.1 L1：避免触发时才发现连接断）──
    if health_check is not None and not health_check():
        _logger.critical("PREMARKET_HEALTH_CHECK_FAILED 执行通道不健康，拒绝启动")
        return PremarketResult(
            status="REFUSED",
            refuse_reason="执行通道不健康（broker 连接异常），拒绝启动",
            state_machine=machine,
            restored_state=restored_state,
            kill_switch_still_closed=kill_switch_still_closed,
            peak_nav=peak_nav,
            nav_history=nav_history,
            insufficient_history=insufficient,
            conservative_position_cap=conservative_cap if insufficient else None,
            entry_var=entry_var,
            prev_attribution=prev_attribution,
        )

    return PremarketResult(
        status="READY",
        state_machine=machine,
        restored_state=restored_state,
        kill_switch_still_closed=kill_switch_still_closed,
        peak_nav=peak_nav,
        nav_history=nav_history,
        insufficient_history=insufficient,
        conservative_position_cap=conservative_cap if insufficient else None,
        entry_var=entry_var,
        prev_attribution=prev_attribution,
    )


# ── 编排：盘后持久化（§3.18，§3.15 加载逆序）──


def postmarket_persist(
    store: JsonStateStore,
    *,
    trade_date: date,
    closing_nav: float,
    state_machine: DrawdownStateMachine | None = None,
    var_95: float | None = None,
    attribution_result: Mapping[str, Any] | None = None,
    strategy_holdings: Mapping[str, Any] | None = None,
    audit_passed: bool = True,
    audit_failure_reason: str | None = None,
    nav_window: int = NAV_HISTORY_WINDOW,
) -> PostmarketResult:
    """盘后持久化：审计门控 → 终态净值 → peak → 状态机 → nav_history →
    entry_var → 归因 → 策略持仓 → 标记可加载（原子提交点）。

    原子性：全部成功才标 DRAWDOWN_COMPLETE；任一环节异常向上传播且不标记，
    次日 §3.15 视为"上次未正常持久化"冷启动默认 NORMAL（宁丢状态不存错状态）。

    Args:
        store: Crash-only 状态存储
        trade_date: 交易日
        closing_nav: 终态净值（含已实现；A 股 T+1 未实现按收盘 Mark 归零）
        state_machine: 当日状态机（None=跳过阶段 3）
        var_95: 当日盘前 VaR_95 快照（None=跳过阶段 4b）
        attribution_result: §3.16 归因结果 dict（None=跳过阶段 4c）
        strategy_holdings: 目标持仓快照（None=跳过阶段 4d）
        audit_passed: §3.10 daily_auditor.audit() 门控（False=不持久化）
        audit_failure_reason: 审计失败原因（留痕）
        nav_window: nav_history 滚动窗口（默认 252）

    Returns:
        PostmarketResult
    """
    # ── 阶段 0 审计门控（§3.18：宁可丢状态不可存错误状态）──
    if not audit_passed:
        _logger.warning(
            "POSTMARKET_PERSIST_SKIPPED date=%s reason=%s",
            trade_date, audit_failure_reason,
        )
        mark_persistable(store, trade_date, STATUS_AUDIT_FAILED_SKIP)
        peak = load_peak_nav(store)
        return PostmarketResult(
            status="SKIPPED_AUDIT_FAILED",
            closing_nav=closing_nav,
            old_peak=peak,
            new_peak=peak if peak is not None else closing_nav,
            is_new_high=False,
            persistable_status=STATUS_AUDIT_FAILED_SKIP,
        )

    if closing_nav <= 0:
        raise InvalidSessionPersistInputError(f"closing_nav 须为正, got {closing_nav}")

    # ── 阶段 1+2 终态净值 → peak NAV（§3.8 单调非减由 max() 保证）──
    old_peak = load_peak_nav(store)
    new_peak = max(old_peak, closing_nav) if old_peak is not None else closing_nav
    save_peak_nav(store, new_peak)
    is_new_high = old_peak is None or new_peak > old_peak
    _logger.info(
        "POSTMARKET_PEAK_UPDATE old=%s new=%s is_new_high=%s",
        old_peak, new_peak, is_new_high,
    )

    # ── 阶段 3 状态机快照（§3.11 5 态 + recovery_step + kill_switch）──
    if state_machine is not None:
        state_machine.persist()

    # ── 阶段 4 nav_history 滚动窗口（追加当日 + trim，§3.15 restore 需完整窗口）──
    append_nav_history(store, trade_date, closing_nav, window=nav_window)

    # ── 阶段 4b entry VaR（供次日 §3.15 加载 + §3.16 风险恶化判断）──
    if var_95 is not None:
        save_entry_var(store, trade_date, var_95)

    # ── 阶段 4c 归因结果持久化（§3.16 save/load 闭环）──
    if attribution_result is not None:
        save_attribution_result(store, trade_date, attribution_result)

    # ── 阶段 4d 策略持仓快照（次日 Ghost 检测基准）──
    if strategy_holdings is not None:
        save_strategy_state(store, trade_date, strategy_holdings)

    # ── 阶段 5 标记可加载（原子提交点：全部成功后唯一提交动作）──
    mark_persistable(store, trade_date, STATUS_DRAWDOWN_COMPLETE)
    _logger.info(
        "POSTMARKET_PERSIST date=%s closing_nav=%s peak=%s",
        trade_date, closing_nav, new_peak,
    )
    return PostmarketResult(
        status="PERSISTED",
        closing_nav=closing_nav,
        old_peak=old_peak,
        new_peak=new_peak,
        is_new_high=is_new_high,
        persistable_status=STATUS_DRAWDOWN_COMPLETE,
    )
