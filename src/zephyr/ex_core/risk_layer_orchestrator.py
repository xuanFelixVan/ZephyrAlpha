# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.risk_layer_orchestrator
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.position.core.drawdown_controller; zephyr.risk.core.drawdown_tracker; zephyr.risk.core.var_calculator; zephyr.risk.core.tail_risk_monitor; zephyr.risk.stop_loss; zephyr.ex_core.position_reconciler; zephyr.ex_core.position_tracker.tracker; zephyr.trading.trading_contracts.broker_interface; zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums
# [CONSUMERS] zephyr.ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 重建完成前禁止下单(Fail-Closed); 熔断单一仲裁点(重复触发不重复清算); 清算以券商实时持仓为准; 样本不足降级标记degraded不阻断; 只编排不重造(回撤/VaR/尾部计算全委托既有模块)
# [MODIFY-GUARD] docs/_working/reviews/2026-08-16-dual-review-adjudication.md §六 (#ARCH-100)
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_risk_layer_orchestrator.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: nav(盘中净值, cash+持仓市值) + positions(券商持仓快照) + today_fills(当日成交)
# I2: DrawdownController/VaRCalculator/TailRiskMonitor/DrawdownTracker(既有风控组件实例)
# I3: broker(券商接口, 启动恢复查询+清算执行) + reconciler(持仓对账器)
# F1: recover_from_broker(以券商持仓为准重建账本, 重建完成前 is_trading_allowed=False)
# F2: evaluate_intraday(净值→回撤追踪→收益序列→VaR/ES→DrawdownController.evaluate→position_cap)
# A1: _engage_kill_switch(单一仲裁点: EMERGENCY/尾部极值/BS-007→trigger_kill_switch+清算)
# A2: start/stop_reconcile_loop(盘中定时对账, 蓝图MOD-EX-056阶段2规划位, 默认300s)
# O1: RiskLayerSnapshot(position_cap/allow_new_position/degraded) + RecoveryResult + 清算报告
# [/ALGO_FLOW]
"""D_EX_CORE — 风控层运行时编排器（Risk Layer Orchestrator）

双轮审查裁定书 §六 P0 风控接线批（#ARCH-100，AI-RWIRE-001 施工）：
35 回撤 / 36 VaR-ES / 37 流动性模块 + KillSwitch + PositionReconciler 模块全写完、
测试全绿但生产链路零实例化（"消防栓装了没接水管"）。本模块是把组合级风控层
接进 TradingSession 运行时的唯一编排点，只编排不重造——回撤/VaR/尾部/对账计算
全部委托既有已验证模块。

四条接线链：
  1. 盘前/盘中评估：evaluate_intraday(nav) → DrawdownTracker.update → 收益序列
     → VaRCalculator.calculate + TailRiskMonitor.assess → DrawdownController.evaluate
     → position_cap / allow_new_position 供 TradingSession 缩放目标权重
  2. EMERGENCY 监听链：DrawdownTracker.on_drawdown_alerted 注册监听，EMERGENCY
     → _engage_kill_switch（单一仲裁点）→ kill_switch_owner.trigger_kill_switch()
     （状态层，RRESIL 内部持久化接口不变）+ stop_loss.trigger_kill_switch（事件层）
     + execute_kill_switch_liquidation（以券商实时持仓为准，15 笔/秒限频）
     ——尾部风险 EMERGENCY 与 BS-007(kill_switch_advised) 同口仲裁
  3. 盘中对账：PositionReconciler 定时调度（蓝图 MOD-EX-056 阶段2规划位，
     默认 300s），冻结标的经 is_symbol_frozen 供 TradingSession 下单前硬拦
  4. 启动恢复：recover_from_broker 以券商持仓+当日成交全量重建 PositionTracker
     （消费 AI-RRESIL-001 交付的 rebuild_from_broker 接口），重建完成前
     is_trading_allowed=False（Fail-Closed 闸门，禁止空仓错觉下重复建仓）

边界（并发会话 AI-RRESIL-001）：DefaultRiskValidator / fill_handler /
PositionTracker 内部实现归 RRESIL，本模块只做调用点接入。
"""

from __future__ import annotations

import logging
import threading
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final, Protocol

import numpy as np

from zephyr.ex_core.position_reconciler import PositionReconciler
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.position.core.drawdown_controller import (
    DrawdownController,
    DrawdownInfo,
    DrawdownResponse,
    VarCvarMetrics,
)
from zephyr.risk.core.drawdown_tracker import (
    DrawdownAlertLevel,
    DrawdownAlertedEvent,
    DrawdownTracker,
)
from zephyr.risk.core.tail_risk_monitor import (
    TailRiskAlertLevel,
    TailRiskMonitor,
    TailRiskSnapshot,
)
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.risk.stop_loss import (
    execute_kill_switch_liquidation,
    trigger_kill_switch,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

_logger = logging.getLogger(__name__)

__all__: Final = [
    "RiskLayerConfig",
    "RiskLayerSnapshot",
    "RecoveryResult",
    "KillSwitchStateOwner",
    "RiskLayerOrchestrator",
]


class KillSwitchStateOwner(Protocol):
    """Kill Switch 状态层协议（DefaultRiskValidator 鸭子类型满足）。

    RRESIL 在其内部落地持久化/LIQUIDATING 锁，接口签名不变。
    """

    def trigger_kill_switch(self) -> None: ...


@dataclass(frozen=True)
class RiskLayerConfig:
    """风控层编排配置（C 类可调参数）。

    Attributes:
        reconcile_interval_seconds: 盘中对账间隔秒数（蓝图 MOD-EX-056 阶段2：每 5 分钟）
        nav_history_maxlen: 净值历史窗口长度（收益序列样本上限）
        min_samples_for_var: VaR/尾部评估所需最少收益样本数（不足→降级标记，不阻断）
        liquidation_scope: 清算范围（all=平仓+撤单 / position=仅平仓 / order=仅撤单）
        max_orders_per_second: 清算限频（A 股 2026 程序化交易新规 15 笔/秒）
        today_fills_probe: broker 当日成交查询扩展方法名（可选能力，缺失→空列表降级）
    """

    reconcile_interval_seconds: float = 300.0
    nav_history_maxlen: int = 512
    min_samples_for_var: int = 30
    liquidation_scope: str = "all"
    max_orders_per_second: int = 15
    today_fills_probe: str = "get_today_fills"


@dataclass(frozen=True)
class RiskLayerSnapshot:
    """一次盘中风控评估快照（不可变）。

    Attributes:
        timestamp: 评估时刻
        nav: 当前净值
        drawdown_level: 回撤告警级别（NONE/WARNING/CRITICAL/EMERGENCY）
        drawdown_pct: 当前回撤率（≤0）
        response: DrawdownController 分级响应（样本不足降级时为 None）
        tail_alert: 尾部风险告警级别（降级时为 None）
        var_pct: VaR 占净值比例（降级时为 None）
        es_pct: ES/CVaR 占净值比例（降级时为 None）
        degraded: 是否降级（收益样本不足，VaR/尾部未参与本次评估）
        degrade_reason: 降级原因（未降级为空串）
    """

    timestamp: datetime
    nav: float
    drawdown_level: DrawdownAlertLevel
    drawdown_pct: float
    response: DrawdownResponse | None
    tail_alert: TailRiskAlertLevel | None
    var_pct: float | None
    es_pct: float | None
    degraded: bool
    degrade_reason: str = ""

    @property
    def position_cap(self) -> float:
        """仓位上限系数（无响应=未评估完成，默认 1.0 不加约束）。"""
        return self.response.position_cap if self.response is not None else 1.0

    @property
    def allow_new_position(self) -> bool:
        """是否允许新开仓（无响应=默认允许；橙/红/黑或熔断建议=禁止）。"""
        return self.response.allow_new_position if self.response is not None else True


@dataclass(frozen=True)
class RecoveryResult:
    """启动恢复结果（不可变）。

    Attributes:
        success: 是否重建完成（False=Fail-Closed，禁止下单）
        holdings_count: 重建的持仓标的数
        fills_count: 重放的当日成交笔数
        error: 失败原因（成功为 None）
        completed_at: 完成时刻
    """

    success: bool
    holdings_count: int
    fills_count: int
    error: str | None
    completed_at: datetime


class _LiquidationBrokerAdapter:
    """execute_kill_switch_liquidation 的 broker 适配器。

    清算函数期望 ExecutionBroker 风格接口（place_order/cancel_order），
    本适配器桥接到 BrokerInterface（submit_order/cancel_order）。
    """

    def __init__(self, broker: BrokerInterface, strategy_id: str = "kill_switch") -> None:
        self._broker = broker
        self._strategy_id = strategy_id

    def place_order(self, symbol: str, direction: str, qty: float, order_type: str = "MARKET") -> str:
        """构造市价清算单并提交，返回 broker_order_id。"""
        order = Order(
            order_id=f"ks-{symbol}-{uuid.uuid4().hex[:8]}",
            idempotency_key=f"ks-{symbol}-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            strategy_id=self._strategy_id,
            side=OrderSide.BUY if direction == "BUY" else OrderSide.SELL,
            order_type=OrderType.MARKET if order_type == "MARKET" else OrderType.LIMIT,
            quantity=Decimal(str(qty)),
            created_at=datetime.now(UTC),
        )
        return self._broker.submit_order(order)

    def cancel_order(self, order_id: str) -> bool:
        """按 broker_order_id 撤单。"""
        return self._broker.cancel_order(order_id)


class RiskLayerOrchestrator:
    """风控层运行时编排器——组合级风控接进交易会话的唯一编排点。

    用法::

        orchestrator = RiskLayerOrchestrator(
            drawdown_controller=DrawdownController(),
            drawdown_tracker=DrawdownTracker(initial_net_value=1_000_000.0),
            var_calculator=VaRCalculator(),
            tail_risk_monitor=TailRiskMonitor(),
            broker=broker,
            position_tracker=tracker,
            kill_switch_owner=default_risk_validator,
            reconciler=PositionReconciler(system_source=tracker, broker_source=broker),
            open_orders_provider=lambda: {...},
        )
        session = TradingSession(..., risk_layer=orchestrator)
        session.start()  # 内部先 recover_from_broker，完成前禁止下单

    Thread Safety:
        熔断仲裁标志与最新快照加锁保护；evaluate_intraday（调仓线程）与
        on_drawdown_alerted 监听（同线程内同步发射）/ reconcile 定时线程可并发。
    """

    def __init__(
        self,
        *,
        drawdown_controller: DrawdownController,
        drawdown_tracker: DrawdownTracker,
        var_calculator: VaRCalculator,
        tail_risk_monitor: TailRiskMonitor,
        broker: BrokerInterface,
        position_tracker: PositionTracker | None = None,
        kill_switch_owner: KillSwitchStateOwner | None = None,
        reconciler: PositionReconciler | None = None,
        open_orders_provider: Callable[[], dict[str, dict]] | None = None,
        config: RiskLayerConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._controller = drawdown_controller
        self._tracker = drawdown_tracker
        self._var_calc = var_calculator
        self._tail_monitor = tail_risk_monitor
        self._broker = broker
        self._position_tracker = position_tracker
        self._kill_switch_owner = kill_switch_owner
        self._reconciler = reconciler
        self._open_orders_provider = open_orders_provider
        self._config = config or RiskLayerConfig()
        self._clock = clock or (lambda: datetime.now(UTC))

        self._nav_history: deque[float] = deque(maxlen=self._config.nav_history_maxlen)
        self._lock = threading.Lock()
        self._latest: RiskLayerSnapshot | None = None
        self._recovery_completed = False
        self._kill_switch_engaged = False
        self._kill_switch_report: dict[str, object] | None = None
        self._reconcile_timer: threading.Timer | None = None
        self._reconcile_running = False

        # EMERGENCY 监听链（E-RK-03）：级别变化去抖由 tracker 保证
        self._tracker.on_drawdown_alerted(self._on_drawdown_alerted)

    # ------------------------------------------------------------------
    # 启动恢复编排（Fail-Closed 闸门）
    # ------------------------------------------------------------------

    def recover_from_broker(self) -> RecoveryResult:
        """以券商为准全量重建持仓账本；重建完成前 is_trading_allowed=False。

        流程：query 券商持仓 + 当日成交 → PositionTracker.rebuild_from_broker
        （AI-RRESIL-001 交付接口，签名 rebuild_from_broker(holdings, today_fills)）。
        任何异常 -> success=False，Fail-Closed 保持禁止下单（空仓错觉下重复建仓
        是 Qwen P0-2 实证事故链）。
        """
        now = self._clock()
        try:
            snapshot = self._broker.get_positions()
            holdings = dict(snapshot.holdings)
            today_fills = self._query_today_fills()
            if self._position_tracker is not None:
                self._position_tracker.rebuild_from_broker(holdings, today_fills)
            with self._lock:
                self._recovery_completed = True
                if snapshot.cash is not None:
                    nav = float(snapshot.cash + snapshot.total_market_value)
                    if nav > 0 and not self._nav_history:
                        self._nav_history.append(nav)
            _logger.info(
                "启动恢复完成: holdings=%d today_fills=%d（以券商为准）",
                len(holdings),
                len(today_fills),
            )
            return RecoveryResult(True, len(holdings), len(today_fills), None, now)
        except Exception as exc:  # noqa: BLE001 — Fail-Closed 必须全捕获，恢复失败禁止下单
            _logger.critical(
                "启动恢复失败，Fail-Closed 禁止下单: %s", exc, exc_info=True
            )
            with self._lock:
                self._recovery_completed = False
            return RecoveryResult(False, 0, 0, str(exc), now)

    def _query_today_fills(self) -> list[object]:
        """查询当日成交（broker 可选扩展能力，缺失 -> 空列表降级）。"""
        probe = getattr(self._broker, self._config.today_fills_probe, None)
        if probe is None:
            _logger.warning(
                "broker 无 %s 扩展，当日成交按空列表降级重建", self._config.today_fills_probe
            )
            return []
        result = probe()
        return list(result) if result is not None else []

    @property
    def is_trading_allowed(self) -> bool:
        """是否允许下单（启动恢复完成 且 熔断未触发）。"""
        with self._lock:
            return self._recovery_completed and not self._kill_switch_engaged

    @property
    def recovery_completed(self) -> bool:
        with self._lock:
            return self._recovery_completed

    @property
    def kill_switch_engaged(self) -> bool:
        with self._lock:
            return self._kill_switch_engaged

    # ------------------------------------------------------------------
    # 盘前/盘中风险评估（position_cap 喂仓位上限链）
    # ------------------------------------------------------------------

    def evaluate_intraday(self, nav: float, now: datetime | None = None) -> RiskLayerSnapshot:
        """盘中风控评估：净值 → 回撤追踪 → VaR/ES → 分级响应 → position_cap。

        Args:
            nav: 当前组合净值（cash + 持仓市值，调用方按最新价计算）
            now: 评估时刻（None=取 clock）

        Returns:
            RiskLayerSnapshot（含 position_cap / allow_new_position / degraded）
        """
        if nav <= 0:
            _logger.error("nav 非正，跳过本次风控评估: nav=%s", nav)
            return self._fallback_snapshot(nav, "nav_non_positive")
        now = now or self._clock()

        # 1. 回撤追踪（EMERGENCY 经监听链同步触发熔断，tracker 内部去抖）
        dd_snapshot = self._tracker.update(nav, now=now)
        self._nav_history.append(nav)

        # 2. 收益序列 → VaR/ES（样本不足降级：GREEN 口径 + degraded 标记，不阻断）
        returns = self._returns_series()
        var_pct: float | None = None
        es_pct: float | None = None
        tail_snapshot: TailRiskSnapshot | None = None
        degraded = False
        degrade_reason = ""
        if len(returns) >= self._config.min_samples_for_var:
            try:
                var_result = self._var_calc.calculate(returns, portfolio_value=nav, now=now)
                tail_snapshot = self._tail_monitor.assess(returns, portfolio_value=nav, now=now)
                var_pct = var_result.value_pct
                es_pct = tail_snapshot.expected_shortfall / nav if nav > 0 else None
            except Exception as exc:  # noqa: BLE001 — 评估失效降级，保留回撤链保护
                degraded = True
                degrade_reason = f"var_es_eval_error:{exc}"
                _logger.exception("VaR/尾部评估失效，本次降级（回撤链仍生效）")
        else:
            degraded = True
            degrade_reason = f"insufficient_returns:{len(returns)}<{self._config.min_samples_for_var}"

        # 3. 回撤控制器分级响应（取最严仓位上限）
        response: DrawdownResponse | None = None
        if var_pct is not None and es_pct is not None:
            try:
                response = self._controller.evaluate(
                    drawdown_info=DrawdownInfo(
                        drawdown_pct=dd_snapshot.drawdown,
                        peak_nav=dd_snapshot.peak,
                        current_nav=nav,
                        recovered_pct=self._recovered_pct(dd_snapshot.drawdown, nav, dd_snapshot.peak, dd_snapshot.trough),
                    ),
                    var_cvar=VarCvarMetrics(var_95=var_pct, cvar_95=max(es_pct, var_pct)),
                )
            except Exception as exc:  # noqa: BLE001 — 响应合成失效降级，回撤链仍生效
                degraded = True
                degrade_reason = f"controller_eval_error:{exc}"
                _logger.exception("DrawdownController.evaluate 失效，本次降级（回撤链仍生效）")
            # 尾部极值 / BS-007 -> 同一仲裁点触发熔断
            if tail_snapshot is not None and tail_snapshot.alert_level is TailRiskAlertLevel.EMERGENCY:
                self._engage_kill_switch(f"尾部风险 EMERGENCY: {tail_snapshot.reason}")
            elif response is not None and response.kill_switch_advised:
                self._engage_kill_switch("BS-007 系统性风险: DrawdownController 建议 Kill Switch")

        snapshot = RiskLayerSnapshot(
            timestamp=now,
            nav=nav,
            drawdown_level=dd_snapshot.level,
            drawdown_pct=dd_snapshot.drawdown,
            response=response,
            tail_alert=tail_snapshot.alert_level if tail_snapshot is not None else None,
            var_pct=var_pct,
            es_pct=es_pct,
            degraded=degraded,
            degrade_reason=degrade_reason,
        )
        with self._lock:
            self._latest = snapshot
        return snapshot

    @staticmethod
    def _recovered_pct(drawdown: float, nav: float, peak: float, trough: float) -> float:
        """回撤回补比例（相对最大回撤）：谷底回升进度 0~1。"""
        if drawdown >= 0 or peak <= trough:
            return 0.0
        return max(0.0, min(1.0, (nav - trough) / (peak - trough)))

    def _returns_series(self) -> np.ndarray:
        """净值历史 -> 收益序列（简单收益率）。"""
        navs = list(self._nav_history)
        if len(navs) < 2:
            return np.array([], dtype=float)
        arr = np.asarray(navs, dtype=float)
        prev = arr[:-1]
        prev[prev == 0] = np.nan  # 除零保护（NaN 由下游校验过滤）
        return (arr[1:] - prev) / prev

    def _fallback_snapshot(self, nav: float, reason: str) -> RiskLayerSnapshot:
        """评估无法执行时的兜底快照（不加仓位约束，保留既有行为）。"""
        return RiskLayerSnapshot(
            timestamp=self._clock(),
            nav=nav,
            drawdown_level=self._tracker.last_level,
            drawdown_pct=0.0,
            response=None,
            tail_alert=None,
            var_pct=None,
            es_pct=None,
            degraded=True,
            degrade_reason=reason,
        )

    @property
    def latest_snapshot(self) -> RiskLayerSnapshot | None:
        """最近一次评估快照（未评估=None）。"""
        with self._lock:
            return self._latest

    @property
    def position_cap(self) -> float:
        """当前仓位上限系数（未评估=1.0 不加约束）。"""
        snap = self.latest_snapshot
        return snap.position_cap if snap is not None else 1.0

    @property
    def allow_new_position(self) -> bool:
        """当前是否允许新开仓（未评估=允许）。"""
        snap = self.latest_snapshot
        return snap.allow_new_position if snap is not None else True

    # ------------------------------------------------------------------
    # EMERGENCY 监听链 + 熔断单一仲裁点
    # ------------------------------------------------------------------

    def _on_drawdown_alerted(self, event: DrawdownAlertedEvent) -> None:
        """E-RK-03 监听：EMERGENCY 级（回撤 >15%）触发熔断清算链。"""
        if event.level is DrawdownAlertLevel.EMERGENCY and event.is_escalation:
            self._engage_kill_switch(
                f"回撤 EMERGENCY: drawdown={event.snapshot.drawdown:.2%} "
                f"peak={event.snapshot.peak:.2f} nav={event.snapshot.net_value:.2f}"
            )

    def _engage_kill_switch(self, reason: str) -> dict[str, object]:
        """熔断单一仲裁点：状态层熔断 + 事件记录 + 清算执行（重复触发直接返回首报）。

        触发源（回撤 EMERGENCY / 尾部 EMERGENCY / BS-007）在此互斥——
        裁定书 P1「多 Protocol 无仲裁」随本仲裁点一并解。
        """
        with self._lock:
            if self._kill_switch_engaged and self._kill_switch_report is not None:
                _logger.warning("Kill Switch 已触发，重复仲裁跳过: %s", reason)
                return self._kill_switch_report
            self._kill_switch_engaged = True  # 先置位防重入

        _logger.critical("KILL_SWITCH_ENGAGE reason=%s", reason)

        # 1. 状态层熔断（DefaultRiskValidator 接口不变，持久化归 RRESIL）
        if self._kill_switch_owner is not None:
            try:
                self._kill_switch_owner.trigger_kill_switch()
            except Exception:  # noqa: BLE001 — 状态层故障不阻断清算链
                _logger.exception("kill_switch_owner.trigger_kill_switch 失效（继续清算）")

        # 2. 事件记录层
        event = trigger_kill_switch(reason=reason, scope=self._config.liquidation_scope)

        # 3. 清算执行（以券商实时持仓为准——Qwen P0-3 裁定）
        try:
            positions_snapshot = self._broker.get_positions()
            positions = {
                symbol: float(qty)
                for symbol, qty in positions_snapshot.holdings.items()
                if qty != 0
            }
        except Exception as exc:  # noqa: BLE001 — 持仓查询失效仍需熔断状态生效
            _logger.critical("清算持仓查询失效（熔断状态保持，新单已禁）: %s", exc, exc_info=True)
            positions = {}
        open_orders: dict[str, dict] = {}
        if self._open_orders_provider is not None:
            try:
                open_orders = self._open_orders_provider()
            except Exception:  # noqa: BLE001 — 挂单查询失效降级为仅平仓
                _logger.exception("open_orders_provider 失效（降级为仅平仓）")

        adapter = _LiquidationBrokerAdapter(self._broker)
        report = execute_kill_switch_liquidation(
            adapter,
            positions,
            open_orders,
            scope=self._config.liquidation_scope,
            max_orders_per_second=self._config.max_orders_per_second,
        )
        result: dict[str, object] = {"event": event, "report": report, "reason": reason}
        with self._lock:
            self._kill_switch_report = result
        return result

    # ------------------------------------------------------------------
    # 盘中对账（蓝图 MOD-EX-056 阶段2规划位：每 5 分钟定时调度）
    # ------------------------------------------------------------------

    def start_reconcile_loop(self) -> None:
        """启动盘中定时对账（session 生命周期内，stop 时关闭）。"""
        if self._reconciler is None or self._config.reconcile_interval_seconds <= 0:
            return
        with self._lock:
            if self._reconcile_running:
                return
            self._reconcile_running = True
        self._schedule_reconcile()

    def stop_reconcile_loop(self) -> None:
        """停止盘中定时对账。"""
        with self._lock:
            self._reconcile_running = False
            timer = self._reconcile_timer
            self._reconcile_timer = None
        if timer is not None:
            timer.cancel()

    def run_reconcile_once(self) -> bool:
        """手动执行一次对账（返回是否一致）；冻结集由 reconciler 内部全量重算。"""
        if self._reconciler is None:
            return True
        result = self._reconciler.reconcile()
        return result.matched

    def is_symbol_frozen(self, symbol: str) -> bool:
        """标的是否被对账冻结（未接入对账器=False 不拦）。"""
        return self._reconciler.is_frozen(symbol) if self._reconciler is not None else False

    def _schedule_reconcile(self) -> None:
        with self._lock:
            if not self._reconcile_running:
                return
            self._reconcile_timer = threading.Timer(
                self._config.reconcile_interval_seconds,
                self._reconcile_tick,
            )
            self._reconcile_timer.daemon = True
            self._reconcile_timer.start()

    def _reconcile_tick(self) -> None:
        try:
            self.run_reconcile_once()
        except Exception:  # noqa: BLE001 — 对账故障不阻断交易主循环，下轮重试
            _logger.exception("盘中定时对账失败（下轮重试）")
        self._schedule_reconcile()
