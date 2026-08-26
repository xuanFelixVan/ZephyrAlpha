# [BLUEPRINT] MOD-TRADING-012 | docs/03_modules/_domain_trading/eod_processor/blueprint.md
# [MODULE] zephyr.trading.eod_processor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.post_settlement_pipeline(MOD-TRADING-003); zephyr.shared.foundation.errors
# [CONSUMERS] 调度层(data scheduler APScheduler / trading work_dag，build_eod_job_spec 注册入口，与 post_settlement_pipeline 同 15:30 窗口)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] Decimal-only金额; EodPosition/EodReport/EodJobSpec frozen不可变; 价格/风险真源探针注入(未接线不臆造); 未定价持仓市价与盈亏按0计并如实披露; 探针异常收敛状态字段不逃逸调度器; alert_sink/audit_sink异常吞没不阻断主链; 函数级注册不挂生产APScheduler任务
# [MODIFY-GUARD] docs/03_modules/_domain_trading/eod_processor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidEodInputError(ZA-TR-0023)
# [TESTS] tests/trading/test_eod_processor.py
# [A_module] module_id=MOD-TRADING-012 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: trade_date + positions(EodPosition) + cash
# I2: price_probe/risk_reassess_fn/expected_nav/nav_tolerance(注入)
# A1: 价格快照(逐symbol取日终价; 异常/非正→unpriced按0计如实披露)
# A2: NAV/P&L(mv=Σqty×price; nav=cash+mv; pnl=Σ(price−cost)×qty; |nav−expected|>tol→DRIFT)
# A3: 风险重估(委托回调; 异常→ERROR+alert; 未注入→SKIPPED)
# O1: EodReport(frozen)
# 边:
# I1 --> A1
# I1 --> A2
# I2 --> A1
# I2 --> A2
# I2 --> A3
# A1 --> A2
# A1 --> O1
# A2 --> O1
# A3 --> O1
# [/ALGO_FLOW]
"""D-TRADING-04 EOD Processor — 日终处理器 (MOD-TRADING-012, CAND-TRD-005, B10-02208)。

每个交易日收盘后（15:30 链）执行日终三步：
  ① 收盘价格快照：逐持仓 symbol 经注入 price_probe 取日终价，缺失/异常如实披露
     （unpriced 按 0 计，绝不臆造价格）；
  ② NAV/P&L 确认：NAV=cash+Σ(qty×eod_price)，未实现盈亏=Σ((eod−cost)×qty)；
     注入 expected_nav 时容差比对 → CONFIRMED/DRIFT（严格大于才 DRIFT）；
  ③ 日终风险重估：委托既有 risk 件回调（生产接线 MOD-RK-20 族），异常落状态
     不逃逸调度器（对齐 post_settlement_pipeline 口径）。

canonical 声明：本模块为 "D-TRADING-04 EOD Processor 日终处理器" 唯一真源；
W-P1-23 同名候选 CAND-TRD-007（B14-04718）后到时应归并本件（本波先建先登）。
铸号备注：初铸 MOD-TRADING-010 与 W-P1-23 并行会话 settlement_record_aggregate
撞号，本方退让改铸 MOD-TRADING-012（depgraph 节点 10631552 已改号）。

SSoT: docs/03_modules/_domain_trading/eod_processor/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.trading.post_settlement_pipeline import POST_SETTLEMENT_CRON

_logger = logging.getLogger(__name__)

__all__: Final = [
    "EodJobSpec",
    "EodPosition",
    "EodReport",
    "InvalidEodInputError",
    "build_eod_job_spec",
    "run_eod_processor",
]

#: NAV 确认默认容差（元，C 类可调）
DEFAULT_NAV_TOLERANCE: Final = Decimal("1.00")


class InvalidEodInputError(ZephyrBaseError):
    """日终处理输入非法——空结算日/非 Decimal 金额/负成本价等（Fail-Closed，占位未登码）。"""

    error_code = "ZA-TR-0023"


def _require_decimal(name: str, value: Decimal, *, allow_negative: bool = False) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise InvalidEodInputError(f"{name} 必须为有限 Decimal: {value!r}")
    if not allow_negative and value < 0:
        raise InvalidEodInputError(f"{name} 必须 ≥0: {value}")
    return value


@dataclass(frozen=True)
class EodPosition:
    """日终持仓快照输入（frozen；Decimal-only）。"""

    symbol: str
    quantity: Decimal
    avg_cost: Decimal

    def __post_init__(self) -> None:
        if not self.symbol or not self.symbol.strip():
            raise InvalidEodInputError("symbol 不能为空")
        _require_decimal("quantity", self.quantity, allow_negative=True)
        _require_decimal("avg_cost", self.avg_cost)


@dataclass(frozen=True)
class EodJobSpec:
    """日终任务调度规格（声明式；调度层据此注册，本模块不实际挂生产任务）。"""

    job_id: str
    cron_expression: str
    trading_day_only: bool
    entrypoint: str
    description: str
    schema_version: str = "1.0"


@dataclass(frozen=True)
class EodReport:
    """一次日终处理结果（frozen）。"""

    trade_date: str
    nav: Decimal
    cash: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    priced_symbols: tuple[str, ...]
    unpriced_symbols: tuple[str, ...]
    snapshot_status: str  # OK / INCOMPLETE / ERROR
    nav_status: str  # CONFIRMED / DRIFT / SKIPPED
    risk_status: str  # OK / ERROR / SKIPPED
    errors: tuple[str, ...] = field(default_factory=tuple)
    captured_at: datetime | None = None
    schema_version: str = "1.0"


def build_eod_job_spec() -> EodJobSpec:
    """日终 15:30 任务规格（与 post_settlement_pipeline 同窗口串联，调度层注册）。"""
    return EodJobSpec(
        job_id="eod_processor_daily",
        cron_expression=POST_SETTLEMENT_CRON,
        trading_day_only=True,
        entrypoint="zephyr.trading.eod_processor.run_eod_processor",
        description="日终处理（D-TRADING-04）：收盘价格快照+NAV/P&L确认+风险重估（MOD-TRADING-012，挂 15:30 盘后链）",
    )


def run_eod_processor(
    trade_date: str,
    *,
    positions: Iterable[EodPosition] = (),
    cash: Decimal = Decimal("0"),
    price_probe: Callable[[str], Decimal] | None = None,
    risk_reassess_fn: Callable[[str, Decimal], object] | None = None,
    expected_nav: Decimal | None = None,
    nav_tolerance: Decimal = DEFAULT_NAV_TOLERANCE,
    alert_sink: Callable[[str, str], None] | None = None,
    audit_sink: Callable[[str], None] | None = None,
    clock: Callable[[], datetime] | None = None,
) -> EodReport:
    """日终处理执行入口（价格快照 → NAV/P&L 确认 → 风险重估）。

    Args:
        trade_date: 结算日（YYYY-MM-DD）。
        positions: 日终持仓（EodPosition 可迭代）。
        cash: 日终现金（Decimal，允许负值=融资口径）。
        price_probe: 日终价探针（symbol→Decimal）；None=快照 ERROR（不臆造）。
        risk_reassess_fn: 风险重估回调（trade_date, nav）；None=SKIPPED。
        expected_nav: 期望 NAV 基准；None=NAV 确认 SKIPPED。
        nav_tolerance: NAV 容差（严格大于才 DRIFT）。
        alert_sink: 告警出口 callable(trade_date, message)；None=仅日志。
        audit_sink: 审计出口 callable(message)；None=仅日志。
        clock: 时钟（默认 UTC now）；测试注入固定时钟保确定性。
    """
    if not trade_date or not trade_date.strip():
        raise InvalidEodInputError("trade_date 不能为空（YYYY-MM-DD）")
    _require_decimal("cash", cash, allow_negative=True)
    _require_decimal("nav_tolerance", nav_tolerance)
    if expected_nav is not None:
        _require_decimal("expected_nav", expected_nav, allow_negative=True)
    captured_at = (clock or (lambda: datetime.now(UTC)))()
    pos_list = list(positions)
    errors: list[str] = []

    def _alert(message: str) -> None:
        _logger.error("EOD 告警: date=%s %s", trade_date, message)
        if alert_sink is not None:
            try:
                alert_sink(trade_date, message)
            except Exception:  # noqa: BLE001 — 告警出口失败不阻断主链路
                _logger.exception("alert_sink 调用失败（已吞没，不阻断）: date=%s", trade_date)

    def _audit(message: str) -> None:
        _logger.info("EOD 审计: date=%s %s", trade_date, message)
        if audit_sink is not None:
            try:
                audit_sink(message)
            except Exception:  # noqa: BLE001 — 审计出口失败不阻断主链路
                _logger.exception("audit_sink 调用失败（已吞没，不阻断）: date=%s", trade_date)

    # ── 步骤 1：收盘价格快照 ──
    priced: list[str] = []
    unpriced: list[str] = []
    prices: dict[str, Decimal] = {}
    if price_probe is None and pos_list:
        errors.append("price_probe 未接线（Fail-Closed：不臆造价格）")
    for pos in pos_list:
        price: Decimal | None = None
        if price_probe is not None:
            try:
                candidate = price_probe(pos.symbol)
                if isinstance(candidate, Decimal) and candidate.is_finite() and candidate > 0:
                    price = candidate
            except Exception as exc:  # noqa: BLE001 — 探针异常收敛为该 symbol 未定价
                _logger.warning("EOD 取价异常: date=%s symbol=%s error=%r", trade_date, pos.symbol, exc)
        if price is None:
            unpriced.append(pos.symbol)
        else:
            priced.append(pos.symbol)
            prices[pos.symbol] = price
    if not pos_list:
        snapshot_status = "OK"
    elif not unpriced:
        snapshot_status = "OK"
    elif priced:
        snapshot_status = "INCOMPLETE"
    else:
        snapshot_status = "ERROR"
    if unpriced:
        _alert(f"日终价缺失（按 0 计并如实披露）: symbols={unpriced}")

    # ── 步骤 2：NAV/P&L 确认 ──
    market_value = Decimal("0")
    unrealized_pnl = Decimal("0")
    for pos in pos_list:
        price = prices.get(pos.symbol)
        if price is None:
            continue  # 未定价按 0 计（已在 unpriced 披露）
        market_value += pos.quantity * price
        unrealized_pnl += (price - pos.avg_cost) * pos.quantity
    nav = cash + market_value
    if expected_nav is None:
        nav_status = "SKIPPED"
    elif abs(nav - expected_nav) > nav_tolerance:
        nav_status = "DRIFT"
        gap = nav - expected_nav
        _alert(f"NAV 确认不一致：nav={nav} expected={expected_nav} gap={gap} tol={nav_tolerance}")
        _audit(f"EOD_NAV_DRIFT date={trade_date} nav={nav} expected={expected_nav} gap={gap}")
    else:
        nav_status = "CONFIRMED"

    # ── 步骤 3：日终风险重估（委托既有 risk 件） ──
    if risk_reassess_fn is None:
        risk_status = "SKIPPED"
    else:
        try:
            risk_reassess_fn(trade_date, nav)
            risk_status = "OK"
        except Exception as exc:  # noqa: BLE001 — 盘后任务异常不逃逸调度器
            risk_status = "ERROR"
            errors.append(f"risk_reassess_fn 异常: {exc!r}")
            _alert(f"日终风险重估步骤异常：{exc!r}")

    return EodReport(
        trade_date=trade_date,
        nav=nav,
        cash=cash,
        market_value=market_value,
        unrealized_pnl=unrealized_pnl,
        priced_symbols=tuple(priced),
        unpriced_symbols=tuple(unpriced),
        snapshot_status=snapshot_status,
        nav_status=nav_status,
        risk_status=risk_status,
        errors=tuple(errors),
        captured_at=captured_at,
    )


#: 包门面再导出别名（scaffold 注册约定：__init__ 以 EodProcessor 类名引用本模块入口）
EodProcessor = run_eod_processor
