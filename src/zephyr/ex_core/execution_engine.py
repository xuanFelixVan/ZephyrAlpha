# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.execution_engine
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager; zephyr.governance.adapters.risk_validation_bridge; zephyr.trading.trading_contracts.execution.order; zephyr.ex_sor.core.algo_trading_engine; zephyr.ex_sor.core.market_context_provider; zephyr.shared.contracts.enums.order_enums
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
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: ex_core
# category: execution_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_EXECUTION_CORE — Execution Engine

交易执行引擎。负责订单执行、算法单（TWAP/VWAP）、经纪商智能路由（SOR）。

CTR 契约：
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE
  生产者 — CTR-005 (Fill) -> D_REPORTING
  生产者 — CTR-006 (PositionSnapshot) -> D_RISK, D_REPORTING, D_ML_TRAIN
  生产者 — CTR-ERR-005 (ExecutionRejectionError) -> D_PORTFOLIO_CORE, D_REPORTING
  生产者 — CTR-P1-007 (ExecutionReport，定义见 shared.contracts) -> D_REPORTING

说明：本模块内 ``ExecutionEngineRunRecord`` 为引擎内部聚合快照，非 CTR-P1-007；
跨层传输的 ExecutionReport 须使用 ``zephyr.shared.contracts.execution_report``。

SSoT: cross_layer_contracts.yaml -> CTR-004 + CTR-005 + CTR-006 + CTR-P1-007

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 委托订单 Order + 算法选择 algo + broker_id
#   fields: order_id/symbol/side/quantity/limit_price + AlgoType(MARKET/TWAP/VWAP/ICEBERG)
#   code: execute_order(order, algo, broker_id) (execution_engine.py)
# 层: 算法
# - id: A1
#   name_zh: ① 盘前风控校验
#   name_en: risk_validator.validate_order
#   intro: HALT 级违规则拒单（ValueError），通过才进入执行分支
#   desc: target_weight=qty/1e6 估算 → RiskValidationPort → HALT 即抛
#   inputs: I1
#   outputs: 放行或拒单
#   invariant: 风控先于执行
# - id: A2
#   name_zh: ② 算法分发执行
#   name_en: _execute_twap/_execute_vwap/_execute_iceberg/_execute_market
#   intro: 按算法类型分发；G7 注入（algo_engine+market_ctx_provider）时走切片路径
#   desc: _can_use_algo→_execute_sliced(generate_plan→逐片子订单create+submit)；未注入回退整笔提交（向后兼容）
#   inputs: I1 A1
#   outputs: 子订单/整单提交
#   invariant: 切片委托 ex_sor AlgoTradingEngine（不重复实现算法）
# - id: A3
#   name_zh: ③ 执行记录
#   name_en: _record_run
#   intro: 聚合成交结果写 _reports（ExecutionEngineRunRecord 引擎内部快照）
#   desc: 填充总量/成交/均价/状态/venue，供 get_engine_run_record 查询
#   inputs: A2
#   outputs: ExecutionEngineRunRecord
# 层: 输出
# - id: O1
#   name_zh: 券商订单号 broker_order_id
#   name_en: broker_order_id（切片路径=首个子订单）
#   intro: 提交成功返回券商订单号；母子订单关联记 algo_orders 供审计
#   downstream: OrderManager / BrokerInterface（miniqmt/simulation）
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.adapters.risk_validation_bridge import (
    RiskValidationPort,
)
from zephyr.shared.contracts.enums.order_enums import OrderType
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.risk_limits import RiskLimits

if TYPE_CHECKING:
    # 懒加载运行时导入 (见 _execute_sliced / _build_algo_params), 避免 ex_core 模块加载
    # 依赖 ClickHouse/Redis 连接链; 同时打破 ex_core→ex_sor 的加载期耦合。
    from zephyr.ex_sor.core.algo_trading_engine import AlgoTradingEngine as SorAlgoTradingEngine
    from zephyr.ex_sor.core.market_context_provider import MarketContextProvider

_logger = logging.getLogger(__name__)


class AlgoType(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    MARKET = "market"
    TWAP = "twap"
    VWAP = "vwap"
    ICEBERG = "iceberg"


# ex_core.AlgoType → ex_sor.AlgoType 名称映射 (G7 接入, 2026-08-05)
# ex_sor 额外支持 POV/IS/ALT, ex_core 暂只暴露 TWAP/VWAP/ICEBERG (MARKET 走直提交)
_ALGO_TYPE_MAP: dict[AlgoType, str] = {
    AlgoType.TWAP: "TWAP",
    AlgoType.VWAP: "VWAP",
    AlgoType.ICEBERG: "ICEBERG",
}


@dataclass
class ExecutionConfig:
    """执行配置"""

    default_algo: AlgoType = AlgoType.TWAP
    twap_window_minutes: int = 30
    twap_slices: int = 10
    max_slippage_bps: Decimal = Decimal("5")
    participation_rate: float = 0.10
    min_order_qty: Decimal = Decimal("100")
    round_lot: int = 100


@dataclass
class ExecutionEngineRunRecord:
    """引擎内部执行聚合记录（非 CTR-P1-007；契约类型见 shared.contracts.ExecutionReport）。"""

    report_id: str
    order_id: str
    symbol: str
    algo_type: str
    total_quantity: Decimal
    filled_quantity: Decimal
    avg_fill_price: Decimal
    target_price: Decimal
    slippage_bps: Decimal
    commission: Decimal
    start_time: datetime
    end_time: datetime
    status: str
    fills: list[dict] = field(default_factory=list)
    venue: str = "simulation"

    @property
    def fill_rate(self) -> float:
        return float(self.filled_quantity / self.total_quantity) if self.total_quantity > 0 else 0.0


class ExecutionEngine:
    """交易执行引擎——算法单执行 + SOR"""

    def __init__(
        self,
        order_manager: OrderManager,
        risk_validator: RiskValidationPort,
        config: ExecutionConfig | None = None,
        algo_engine: SorAlgoTradingEngine | None = None,
        market_ctx_provider: MarketContextProvider | None = None,
    ):
        """初始化执行引擎。

        Args:
            order_manager: 订单管理器 (创建/提交子订单)
            risk_validator: 风控校验端口
            config: 执行配置 (切片数/窗口/参与率等)
            algo_engine: G7 算法引擎 (MOD-XS-005, 可选)。注入后 _execute_twap/_execute_vwap
                走 generate_plan() 切片路径; 为 None 则回退占位整笔提交 (向后兼容)。
            market_ctx_provider: 市场上下文提供器 (MOD-XS-006, 可选)。与 algo_engine 成对
                注入; 两者均存在才启用切片路径。
        """
        self._order_manager = order_manager
        self._config = config or ExecutionConfig()
        self._risk_validator = risk_validator
        self._algo_engine = algo_engine
        self._market_ctx_provider = market_ctx_provider
        self._algo_orders: dict[str, dict] = {}
        self._reports: dict[str, ExecutionEngineRunRecord] = {}
        self._broker_scores: dict[str, float] = defaultdict(lambda: 1.0)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def algo_orders(self) -> dict[str, dict]:
        """只读：algo_orders（Stage 4 公共化）。"""
        return self._algo_orders

    @algo_orders.setter
    def algo_orders(self, value):
        """写入：algo_orders（Stage 4 公共化）。"""
        self._algo_orders = value

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def broker_scores(self) -> dict[str, float]:
        """只读：broker_scores（Stage 4 公共化）。"""
        return self._broker_scores

    @broker_scores.setter
    def broker_scores(self, value):
        """写入：broker_scores（Stage 4 公共化）。"""
        self._broker_scores = value

    def execute_order(
        self,
        order: Order,
        algo: AlgoType | None = None,
        broker_id: str = "simulation",
    ) -> str:
        """执行单笔订单"""
        algo = algo or self._config.default_algo

        violations = self._risk_validator.validate_order(
            symbol=order.symbol,
            # 5.105.5 修复: 在Decimal域内计算后再转float, 避免大数量Decimal->float精度丢失
            target_weight=float(Decimal(str(order.quantity)) / Decimal("1000000"))
            if not isinstance(order.quantity, Decimal)
            else float(order.quantity / Decimal("1000000")),
            current_holdings={},
            limits=RiskLimits(
                as_of_date=datetime.now(UTC),
                idempotency_key=f"exec-{order.order_id}",
                max_single_position=0.10,
            ),
        )

        halt_violations = [v for v in violations if v.severity == "HALT"]
        if halt_violations:
            _logger.warning("Order rejected by risk: order_id=%s violations=%s", order.order_id, len(halt_violations))
            raise ValueError(f"Order rejected by risk validator: {halt_violations[0].description}")

        if algo is AlgoType.TWAP:
            return self._execute_twap(order, broker_id)
        elif algo is AlgoType.VWAP:
            return self._execute_vwap(order, broker_id)
        elif algo is AlgoType.ICEBERG:
            return self._execute_iceberg(order, broker_id)
        else:
            return self._execute_market(order, broker_id)

    def execute_batch(
        self,
        orders: list[Order],
        algo: AlgoType | None = None,
    ) -> list[str]:
        """批量执行订单列表"""
        broker_order_ids = []
        for order in orders:
            try:
                bid = self.execute_order(order, algo)
                broker_order_ids.append(bid)
            except ValueError as e:
                _logger.error("Order execution rejected: order_id=%s error=%s", order.order_id, e)
        return broker_order_ids

    def get_engine_run_record(self, order_id: str) -> ExecutionEngineRunRecord | None:
        return self._reports.get(order_id)

    def select_broker(self, order: Order) -> str:
        """Smart Order Router (SOR)——选择最优经纪商"""
        scored = sorted(
            self._broker_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        if scored:
            return scored[0][0]
        return "simulation"

    def update_broker_score(self, broker_id: str, fill_quality: float) -> None:
        """更新经纪商评分（基于成交质量）"""
        current = self._broker_scores[broker_id]
        self._broker_scores[broker_id] = current * 0.9 + fill_quality * 0.1

    def _record_run(
        self,
        order: Order,
        algo_type: str,
        broker_order_id: str,
        broker_id: str,
        start_time: datetime,
    ) -> None:
        """填充执行记录（消除死代码：原 _reports 从未写入）

        Args:
            order: 订单
            algo_type: 算法类型（market/twap/vwap）
            broker_order_id: 券商订单号
            broker_id: 经纪商ID
            start_time: 执行开始时间
        """
        target_price = order.limit_price if order.limit_price is not None else Decimal("0")
        self._reports[order.order_id] = ExecutionEngineRunRecord(
            report_id=f"rpt-{broker_order_id}",
            order_id=order.order_id,
            symbol=order.symbol,
            algo_type=algo_type,
            total_quantity=order.quantity,
            filled_quantity=order.filled_quantity or Decimal("0"),
            avg_fill_price=order.avg_fill_price or Decimal("0"),
            target_price=target_price,
            slippage_bps=Decimal("0"),
            commission=Decimal("0"),
            start_time=start_time,
            end_time=datetime.now(UTC),
            status=order.status.value if hasattr(order.status, "value") else str(order.status),
            venue=broker_id,
        )

    def _execute_twap(self, order: Order, broker_id: str) -> str:
        start_time = datetime.now(UTC)
        if self._can_use_algo():
            return self._execute_sliced(order, broker_id, AlgoType.TWAP, start_time)
        # 回退: 占位整笔提交 (向后兼容, algo_engine 未注入时)
        slices = self._config.twap_slices
        broker_order_id = self._order_manager.submit_order(order.order_id, broker_id)

        self._algo_orders[order.order_id] = {
            "algo": "twap",
            "sliced": False,
            "slices": slices,
            "broker_order_ids": [broker_order_id],
            "started_at": start_time,
        }
        self._record_run(order, "twap", broker_order_id, broker_id, start_time)

        return broker_order_id

    def _execute_vwap(self, order: Order, broker_id: str) -> str:
        start_time = datetime.now(UTC)
        if self._can_use_algo():
            return self._execute_sliced(order, broker_id, AlgoType.VWAP, start_time)
        # 回退: 占位整笔提交 (向后兼容, algo_engine 未注入时)
        self._algo_orders[order.order_id] = {
            "algo": "vwap",
            "sliced": False,
            "started_at": start_time,
        }
        broker_order_id = self._order_manager.submit_order(order.order_id, broker_id)
        self._record_run(order, "vwap", broker_order_id, broker_id, start_time)
        return broker_order_id

    def _execute_iceberg(self, order: Order, broker_id: str) -> str:
        start_time = datetime.now(UTC)
        if self._can_use_algo():
            return self._execute_sliced(order, broker_id, AlgoType.ICEBERG, start_time)
        # 回退: 占位整笔提交 (向后兼容, algo_engine 未注入时走 MARKET 路径)
        return self._execute_market(order, broker_id)

    def _execute_market(self, order: Order, broker_id: str) -> str:
        start_time = datetime.now(UTC)
        broker_order_id = self._order_manager.submit_order(order.order_id, broker_id)
        self._record_run(order, "market", broker_order_id, broker_id, start_time)
        return broker_order_id

    # ── G7 智能订单路由接入 (MOD-XS-005 + MOD-XS-006, 2026-08-05 治本) ──

    def _can_use_algo(self) -> bool:
        """是否启用 G7 切片路径——algo_engine 与 market_ctx_provider 成对注入。"""
        return self._algo_engine is not None and self._market_ctx_provider is not None

    def _build_algo_params(self, sor_algo_type: object) -> object:
        """从 ExecutionConfig 构造 AlgoParams (懒加载 ex_sor 类型)。

        - participation_rate 钳制到 §10.1 上限 5% (config 默认 0.10 超限)
        - ICEBERG 用 min_order_qty 作为 display_quantity (AlgoParams 强制要求)
        """
        from zephyr.ex_sor.core.algo_trading_engine import (
            MAX_PARTICIPATION_RATE,
            AlgoParams,
        )

        cfg = self._config
        # §10.1 硬上限 5%: config.participation_rate 可能 > 0.05, 钳制
        pr = min(Decimal(str(cfg.participation_rate)), MAX_PARTICIPATION_RATE)
        if pr <= 0:
            pr = MAX_PARTICIPATION_RATE
        display = cfg.min_order_qty if sor_algo_type.name == "ICEBERG" else None
        return AlgoParams(
            algo_type=sor_algo_type,
            participation_rate=pr,
            time_horizon_minutes=cfg.twap_window_minutes,
            max_slice_count=cfg.twap_slices,
            min_slice_quantity=cfg.min_order_qty,
            display_quantity=display,
        )

    def _execute_sliced(
        self,
        order: Order,
        broker_id: str,
        core_algo: AlgoType,
        start_time: datetime,
    ) -> str:
        """G7 切片执行——generate_plan → 子订单创建/提交 (治本接入)。

        流程:
            1. 映射 AlgoType + 构造 AlgoParams
            2. MarketContextProvider 取真实 MarketContext
            3. AlgoTradingEngine.generate_plan 生成切片方案 (含 §13.1 ADV 上限/守恒校验)
            4. 每个 AlgoSlice → OrderManager.create_order + submit_order (子订单)
            5. 母子订单关联记录到 algo_orders (审计)

        Args:
            order: 母订单 (CTR-004)
            broker_id: 经纪商 ID
            core_algo: ex_core.AlgoType (TWAP/VWAP/ICEBERG)
            start_time: 执行开始时刻

        Returns:
            首个子订单的 broker_order_id (母订单聚合由 algo_orders 跟踪)

        Raises:
            ValueError: generate_plan 失败 (OrderTooLargeError/AlgoError 包装,
                与风控拒绝同走 ValueError 契约, 供上游统一处理)
        """
        from zephyr.ex_sor.core.algo_trading_engine import (
            AlgoError,
            OrderTooLargeError,
        )
        from zephyr.ex_sor.core.algo_trading_engine import (
            AlgoType as SorAlgoType,
        )

        sor_algo_name = _ALGO_TYPE_MAP.get(core_algo)
        if sor_algo_name is None:
            raise ValueError(f"不支持的算法类型: {core_algo}")
        sor_algo_type = SorAlgoType[sor_algo_name]
        params = self._build_algo_params(sor_algo_type)

        ctx = self._market_ctx_provider.get_context(order.symbol)
        try:
            plan = self._algo_engine.generate_plan(order, params, ctx)
        except (AlgoError, OrderTooLargeError) as exc:
            _logger.error(
                "G7 generate_plan 失败 order=%s algo=%s: %s",
                order.order_id,
                sor_algo_name,
                exc,
            )
            raise ValueError(
                f"algo plan generation failed for {sor_algo_name}: {exc}",
            ) from exc

        # 每个切片 → 子订单创建 + 提交 (HB-07 零重试: 单片失败不重试, 记录后继续)
        child_orders: list[dict] = []
        broker_order_ids: list[str] = []
        for sl in plan.slices:
            if sl.quantity <= 0:
                continue
            limit_price = sl.reference_price
            child_order_type = OrderType.LIMIT if limit_price is not None else OrderType.MARKET
            child = self._order_manager.create_order(
                symbol=order.symbol,
                strategy_id=order.strategy_id,
                side=order.side,
                order_type=child_order_type,
                quantity=sl.quantity,
                limit_price=limit_price,
                broker_id=broker_id,
            )
            child_broker_oid = self._order_manager.submit_order(child.order_id, broker_id)
            broker_order_ids.append(child_broker_oid)
            child_orders.append(
                {
                    "child_order_id": child.order_id,
                    "broker_order_id": child_broker_oid,
                    "slice_index": sl.slice_index,
                    "quantity": str(sl.quantity),
                    "price_strategy": sl.price_strategy.value,
                }
            )

        first_broker_oid = broker_order_ids[0] if broker_order_ids else ""
        self._algo_orders[order.order_id] = {
            "algo": core_algo.value,
            "sliced": True,
            "plan": plan.to_dict(),
            "slice_count": len(plan.slices),
            "child_orders": child_orders,
            "broker_order_ids": broker_order_ids,
            "started_at": start_time,
        }
        self._record_run(order, core_algo.value, first_broker_oid, broker_id, start_time)
        _logger.info(
            "G7 切片执行完成: order=%s algo=%s slices=%d child_orders=%d",
            order.order_id,
            sor_algo_name,
            len(plan.slices),
            len(child_orders),
        )
        return first_broker_oid


__all__ = ["AlgoType", "ExecutionConfig", "ExecutionEngine", "ExecutionEngineRunRecord"]
