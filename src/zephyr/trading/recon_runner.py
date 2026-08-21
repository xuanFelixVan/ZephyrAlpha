# [BLUEPRINT] MOD-TRADING-007 | docs/03_modules/_domain_trading/recon_runner/blueprint.md
# [MODULE] zephyr.trading.recon_runner
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.backtest.io.result_repository; zephyr.ex_core.position_reconciler; zephyr.risk.core.daily_auditor; zephyr.shared.contracts.fill; zephyr.shared.contracts.position; zephyr.shared.io.paths; zephyr.trading.backtest_fills_adapter; zephyr.trading.broker_settlement_adapter; zephyr.trading.settlement_reconciliation
# [CONSUMERS] 57号文日循环SOP（人工/后续调度触发）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只消费不改既有引擎逻辑(SettlementReconciler/PositionReconciler/DailyAuditor); 差异写库append-only仅INSERT; SQL参数化+常量(NO-BARE-SQL); db_path默认None走DB_PATH SSoT(测试注入临时库); C类当日告警清单必出; 费用差仅参考不归类(56号文C9)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ArtifactNotFoundError(透传); broker查询异常透传
# [TESTS] tests/trading/test_recon_runner.py
# [A_module] module_id=MOD-TRADING-007 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_TRADING — 回测 vs 模拟盘日终对账编排器（56号文 §2 G7，testing 封顶=宪章 B-007）

串 L1（SettlementReconciler 交易级）+ L2（PositionReconciler 持仓级双源比对语义）
+ L3（DailyAuditor PnL 口径，0.1% 容差）三层 diff → 归因三分类（56号文 §3）
→ 差异写 reconciliation_differences 表（governance.db，append-only）
→ 返回结构化结果（含 C 类清单供当日告警，56号文 §6 C10 闭环首查项）。

设计真源: docs/.../design_memos/56_backtest_vs_sim_reconciliation_plan.md
触发方式: 57号文日循环 SOP §5「15:30 收盘后」人工/后续调度触发（本模块不挂调度）。

调用示例（SOP 用）::

    from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker
    from zephyr.trading.recon_runner import run_daily_reconciliation

    broker = MiniQmtBroker(path=..., account_id=...)  # config/.env.qmt 读取
    broker.connect()
    result = run_daily_reconciliation(
        trade_date="2026-08-21",
        run_id="bt-e8405c0f",          # 当日同信号回测跑批 run_id
        broker=broker,
    )
    for item in result.c_class_items:  # C 类当日告警
        alert(item)
    print(result.to_dict())

口径说明
--------
- **配对键**：数量与成交价为主键（56号文口径铁律），业务配对键口径真源
  = broker_settlement_adapter.make_business_pair_key（两侧同款）。
- **费用差**：COMMISSION_MISMATCH 仅写库作参考列，归 REFERENCE_FEE 不参与
  A/B/C 三分类（56号文 C9；费率统一已于 #ARCH-134 裁定，费用列仍不判定）。
- **L2 持仓**：基准侧由回测 trade_log 重放推导（G5），实盘侧取同一
  get_positions() 快照（避免两次查询快照不一致），复用 PositionReconciler
  双源比对语义（零容差，56号文 C7）。
- **L3 PnL**：expected=回测当日净值差（equity_curve 末-初），realized=模拟盘
  当日 PnL 代理（期末持仓市值 − 当日净买入现金流，**隐含期初空仓假设**——
  P0-5 日循环模拟盘每日 fresh 开仓场景成立；若模拟盘滚动持仓，L3 仅作
  参考层，MISMATCH 走人工复核，56号文 C8 处置链）。复用
  daily_auditor.PnLReconciliation 结果类型与 |gap_pct|≤0.001 容差口径。
  equity_curve 缺失时 L3=SKIPPED（l3_result=None）。
- **落库**：reconciliation_differences（#234 已建表），recon_layer=
  trade/position/cash；L1 全量 drifts（含费用参考列）+ L2 持仓差 +
  L3 MISMATCH；append-only 仅 INSERT，参数化+SQL 常量（NO-BARE-SQL 门禁）。
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Final, Protocol

from zephyr.backtest.io.result_repository import get_artifact
from zephyr.ex_core.position_reconciler import PositionReconciler, ReconcileResult
from zephyr.risk.core.daily_auditor import PnLReconciliation, ReconciliationStatus
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.io.paths import DB_PATH
from zephyr.trading.backtest_fills_adapter import (
    replay_positions_from_trade_log,
    trades_to_fills,
)
from zephyr.trading.broker_settlement_adapter import fills_to_broker_records
from zephyr.trading.settlement_reconciliation import (
    DriftType,
    ReconciliationResult,
    SettlementReconciler,
)

_logger = logging.getLogger(__name__)

__all__: Final = [
    "AttributionClass",
    "AttributionItem",
    "ReconBrokerSource",
    "ReconDailyResult",
    "run_daily_reconciliation",
]

# L3 PnL 容差——对齐 DailyAuditor AuditConfig.pnl_tolerance 默认 0.001（56号文 C8）
_PNL_GAP_TOLERANCE: Final[float] = 0.001

# L3 写库时的组合级 symbol 占位（reconciliation_differences.symbol NOT NULL）
_PORTFOLIO_SYMBOL: Final = "__PORTFOLIO__"

# L2/L3 drift_type 取值（表列注释列举 L1 DriftType 5 类；position/cash 层类型值
# 由本模块定义，recon_layer 列区分层级——表设计预留三层口径）
_DRIFT_TYPE_POSITION_QTY: Final = "position_qty_mismatch"
_DRIFT_TYPE_PNL_GAP: Final = "pnl_gap_mismatch"

# SQL 常量（NO-BARE-SQL 门禁；append-only 仅 INSERT，参数化防注入）
_SQL_INSERT_DIFFERENCE: Final = (
    "INSERT INTO reconciliation_differences "
    "(trade_date, recon_layer, trade_id, symbol, drift_type, "
    "system_value, broker_value, diff, detected_at, schema_version) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SCHEMA_VERSION: Final = "1.0"


class ReconBrokerSource(Protocol):
    """对账实盘侧数据源协议（鸭子类型，MiniQmtBroker 已满足；测试注入 mock）。"""

    def query_trades_today(self, trade_date: str | None = None) -> list[Fill]: ...

    def get_positions(self) -> PositionSnapshot: ...


class AttributionClass(str, Enum):
    """偏差归因三分类 + 费用参考列（56号文 §3）。VALUE 即异常登记口径字符串。"""

    A_SLIPPAGE = "A_slippage"  # 数量一致、成交价偏差超容差
    B_PARTIAL_FILL = "B_partial_fill"  # 实盘数量 ≠ 回测数量（典型=实盘<回测）
    C_REJECT_MISSING = "C_reject_missing"  # 整笔缺失（拒单/断线漏单）
    REFERENCE_FEE = "reference_fee"  # 费用差——仅参考列，不归类（56号文 C9）


@dataclass(frozen=True)
class AttributionItem:
    """单笔 L1 差异的归因记录（不可变）。"""

    category: AttributionClass
    trade_id: str
    symbol: str
    drift_type: str
    system_value: Decimal | None
    broker_value: Decimal | None
    diff: Decimal | None
    detail: str


@dataclass(frozen=True)
class ReconDailyResult:
    """一次日终对账的结构化结果（不可变）。

    c_class_items 为当日告警清单（56号文 §3：C 类当日即告警）；
    db_error 非 None 表示落库失败（对账结果本身仍有效，需人工补登记）。
    """

    trade_date: str
    run_id: str
    l1_result: ReconciliationResult
    l2_result: ReconcileResult
    l3_result: PnLReconciliation | None
    attributions: tuple[AttributionItem, ...]
    c_class_items: tuple[AttributionItem, ...]
    rows_written: int
    db_path: str
    db_error: str | None = None

    def to_dict(self) -> dict:
        """SOP 打印/落 tracker 用的 JSON 快照。"""
        return {
            "trade_date": self.trade_date,
            "run_id": self.run_id,
            "l1_matched": self.l1_result.matched,
            "l1_drifts": len(self.l1_result.drifts),
            "l1_system_trades": self.l1_result.total_system_trades,
            "l1_broker_trades": self.l1_result.total_broker_trades,
            "l2_matched": self.l2_result.matched,
            "l2_drift_symbols": sorted(d.symbol for d in self.l2_result.drifts),
            "l3_status": self.l3_result.status.value if self.l3_result else "SKIPPED",
            "l3_gap_pct": self.l3_result.gap_pct if self.l3_result else None,
            "attribution_counts": {
                cls.value: sum(1 for a in self.attributions if a.category is cls)
                for cls in AttributionClass
            },
            "c_class_items": [
                {"trade_id": a.trade_id, "symbol": a.symbol, "detail": a.detail}
                for a in self.c_class_items
            ],
            "rows_written": self.rows_written,
            "db_error": self.db_error,
        }


class _StaticPositionSource:
    """静态持仓源——把 {symbol: qty} 包装成 PositionSource 协议对象。

    L2 复用 PositionReconciler 双源比对语义（56号文 §2）；实盘侧包同一
    get_positions() 快照，避免二次 QMT 查询导致快照不一致。
    """

    def __init__(self, holdings: dict[str, Decimal]) -> None:
        self._holdings = dict(holdings)

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            idempotency_key=f"recon-static-{id(self)}",
            portfolio_id="recon",
            holdings=dict(self._holdings),
        )


def _classify_l1_drifts(l1: ReconciliationResult) -> tuple[AttributionItem, ...]:
    """L1 drifts → 归因三分类（56号文 §3 判定特征映射）。"""
    items: list[AttributionItem] = []
    for d in l1.drifts:
        if d.drift_type is DriftType.PRICE_MISMATCH:
            items.append(
                AttributionItem(
                    category=AttributionClass.A_SLIPPAGE,
                    trade_id=d.trade_id,
                    symbol=d.symbol,
                    drift_type=d.drift_type.value,
                    system_value=d.system_value,
                    broker_value=d.broker_value,
                    diff=d.diff,
                    detail="A 滑点：数量一致、成交价偏差超容差（回测价 %.4f vs 实盘价 %.4f）"
                    % (d.system_value, d.broker_value),
                )
            )
        elif d.drift_type is DriftType.QUANTITY_MISMATCH:
            direction = "实盘<回测（部分成交）" if (d.diff or 0) > 0 else "实盘>回测（超额成交）"
            items.append(
                AttributionItem(
                    category=AttributionClass.B_PARTIAL_FILL,
                    trade_id=d.trade_id,
                    symbol=d.symbol,
                    drift_type=d.drift_type.value,
                    system_value=d.system_value,
                    broker_value=d.broker_value,
                    diff=d.diff,
                    detail=f"B 部分成交：数量不一致（{direction}，回测 {d.system_value} vs 实盘 {d.broker_value}）",
                )
            )
        elif d.drift_type is DriftType.COMMISSION_MISMATCH:
            # 费用差仅参考列不归类（56号文 C9 / §4 R1）
            items.append(
                AttributionItem(
                    category=AttributionClass.REFERENCE_FEE,
                    trade_id=d.trade_id,
                    symbol=d.symbol,
                    drift_type=d.drift_type.value,
                    system_value=d.system_value,
                    broker_value=d.broker_value,
                    diff=d.diff,
                    detail="费用差（参考列，不参与 A/B/C 判定，56号文 C9）",
                )
            )
        else:  # MISSING_IN_BROKER / MISSING_IN_SYSTEM → C 类当日告警
            side = (
                "回测有实盘无（疑拒单/断线漏单）"
                if d.drift_type is DriftType.MISSING_IN_BROKER
                else "实盘有回测无（疑多报/口径错位）"
            )
            items.append(
                AttributionItem(
                    category=AttributionClass.C_REJECT_MISSING,
                    trade_id=d.trade_id,
                    symbol=d.symbol,
                    drift_type=d.drift_type.value,
                    system_value=d.system_value,
                    broker_value=d.broker_value,
                    diff=d.diff,
                    detail=f"C 拒单/缺失：整笔缺失（{side}）——当日即告警",
                )
            )
    return tuple(items)


def _compute_l3_pnl(
    equity_curve: list[dict],
    broker_fills: list[Fill],
    broker_snapshot: PositionSnapshot,
) -> PnLReconciliation | None:
    """L3 PnL 对账（回测期望 vs 模拟盘实现，DailyAuditor 口径 0.1% 容差）。

    口径见模块头「L3 PnL」段；equity_curve 为空返回 None（SKIPPED）。
    """
    if not equity_curve:
        _logger.warning("L3 跳过：回测 artifact 缺 equity_curve（I4 产物不完整）")
        return None
    bt_pnl = float(equity_curve[-1]["equity"]) - float(equity_curve[0]["equity"])
    # 模拟盘当日 PnL 代理：期末持仓市值 − 当日净买入现金流（隐含期初空仓假设）
    trade_cash = sum(float(f.filled_quantity * f.fill_price) for f in broker_fills)
    sim_pnl = float(broker_snapshot.total_market_value) - trade_cash
    nav = float(broker_snapshot.cash + broker_snapshot.total_market_value)
    gap = bt_pnl - sim_pnl
    gap_pct = gap / abs(nav) if abs(nav) > 0 else 0.0
    status = (
        ReconciliationStatus.MATCH
        if abs(gap_pct) <= _PNL_GAP_TOLERANCE
        else ReconciliationStatus.MISMATCH
    )
    # 费用合计仅报告用（56号文 C9：费用不参与 gap 判定）
    total_cost = sum(float(f.commission) for f in broker_fills)
    return PnLReconciliation(
        expected_pnl=bt_pnl,
        realized_pnl=sim_pnl,
        unrealized_pnl=0.0,
        total_pnl=sim_pnl,
        gap=gap,
        gap_pct=gap_pct,
        status=status,
        total_cost=total_cost,
    )


def _persist_differences(
    db_path: Path,
    trade_date: str,
    l1: ReconciliationResult,
    l2: ReconcileResult,
    l3: PnLReconciliation | None,
) -> int:
    """差异写 reconciliation_differences 表（append-only，仅 INSERT，参数化）。

    Returns:
        写入行数。
    """
    detected_at = datetime.now(UTC).isoformat()
    rows: list[tuple] = []
    # L1 交易级（含 COMMISSION_MISMATCH 参考列——记录不判定，56号文 C9）
    for d in l1.drifts:
        rows.append(
            (
                trade_date,
                "trade",
                d.trade_id,
                d.symbol,
                d.drift_type.value,
                str(d.system_value) if d.system_value is not None else None,
                str(d.broker_value) if d.broker_value is not None else None,
                str(d.diff) if d.diff is not None else None,
                detected_at,
                _SCHEMA_VERSION,
            )
        )
    # L2 持仓级
    for d in l2.drifts:
        rows.append(
            (
                trade_date,
                "position",
                None,
                d.symbol,
                _DRIFT_TYPE_POSITION_QTY,
                str(d.system_qty),
                str(d.broker_qty),
                str(d.diff),
                detected_at,
                _SCHEMA_VERSION,
            )
        )
    # L3 PnL 级（仅 MISMATCH 落库；MATCH 即 56号文 C8 通过）
    if l3 is not None and l3.status is ReconciliationStatus.MISMATCH:
        rows.append(
            (
                trade_date,
                "cash",
                None,
                _PORTFOLIO_SYMBOL,
                _DRIFT_TYPE_PNL_GAP,
                repr(l3.expected_pnl),
                repr(l3.realized_pnl),
                repr(l3.gap),
                detected_at,
                _SCHEMA_VERSION,
            )
        )
    if not rows:
        return 0
    conn = sqlite3.connect(str(db_path))
    try:
        with conn:  # 事务：全部成功才提交
            conn.executemany(_SQL_INSERT_DIFFERENCE, rows)
    finally:
        conn.close()
    return len(rows)


def run_daily_reconciliation(
    trade_date: str,
    run_id: str,
    broker: ReconBrokerSource,
    db_path: str | Path | None = None,
    storage_path: str | Path | None = None,
) -> ReconDailyResult:
    """执行一次「回测 vs 模拟盘」日终对账（56号文 §5 15:30 步骤③④）。

    流程：回测产物+实盘查询 → L1 交易级 diff → L2 持仓级 diff → L3 PnL 级
    → 归因三分类 → 差异落库 → 结构化结果（C 类清单当日告警）。

    Args:
        trade_date: 交易日 "YYYY-MM-DD"
        run_id: 当日同信号回测跑批 run_id（data/backtest_artifacts/{run_id}.json）
        broker: 实盘侧数据源（生产=MiniQmtBroker，已 connect；测试=mock）
        db_path: governance.db 路径；None=DB_PATH SSoT（paths.py）。
            测试注入临时库（trend_analyzer db_path setter 同款隔离先例）。
        storage_path: 回测产物目录；None=默认 data/backtest_artifacts/。

    Returns:
        ReconDailyResult（含 C 类当日告警清单）。

    Raises:
        ArtifactNotFoundError: run_id 产物缺失（I4 不变量破坏，56号文 C3）。
        MiniQmtBrokerError: 实盘查询失败（56号文 C1：记 C 类并 SKIP 由 SOP 处置）。
    """
    _logger.info("日终对账开始: trade_date=%s run_id=%s", trade_date, run_id)

    # ── 输入准备 ──
    artifact = get_artifact(run_id, storage_path=Path(storage_path) if storage_path else None)
    system_fills = trades_to_fills(artifact.trade_log, artifact.strategy_id, run_id)
    system_positions = replay_positions_from_trade_log(artifact.trade_log)
    broker_fills = broker.query_trades_today(trade_date)
    broker_records = fills_to_broker_records(broker_fills, trade_date)
    broker_snapshot = broker.get_positions()

    # ── L1 交易级（SettlementReconciler，容差=ReconciliationConfig 默认）──
    l1 = SettlementReconciler().reconcile(system_fills, broker_records, trade_date)

    # ── L2 持仓级（PositionReconciler 双源比对语义，零容差，56号文 C7）──
    l2 = PositionReconciler(
        system_source=_StaticPositionSource(system_positions),
        broker_source=_StaticPositionSource(broker_snapshot.holdings),
        tolerance=Decimal("0"),
    ).reconcile()

    # ── L3 PnL 级（DailyAuditor PnLReconciliation 口径，0.1% 容差，56号文 C8）──
    l3 = _compute_l3_pnl(artifact.equity_curve, broker_fills, broker_snapshot)

    # ── 归因三分类（56号文 §3）──
    attributions = _classify_l1_drifts(l1)
    c_class_items = tuple(a for a in attributions if a.category is AttributionClass.C_REJECT_MISSING)

    # ── 差异落库（append-only；失败不丢对账结果，db_error 显性标记）──
    resolved_db = Path(db_path) if db_path is not None else DB_PATH
    rows_written = 0
    db_error: str | None = None
    try:
        rows_written = _persist_differences(resolved_db, trade_date, l1, l2, l3)
    except (sqlite3.Error, OSError) as exc:
        db_error = f"{type(exc).__name__}: {exc}"
        _logger.exception("reconciliation_differences 落库失败: %s", db_error)

    result = ReconDailyResult(
        trade_date=trade_date,
        run_id=run_id,
        l1_result=l1,
        l2_result=l2,
        l3_result=l3,
        attributions=attributions,
        c_class_items=c_class_items,
        rows_written=rows_written,
        db_path=str(resolved_db),
        db_error=db_error,
    )
    _logger.info(
        "日终对账完成: trade_date=%s l1_matched=%s l2_matched=%s l3=%s 归因 A=%d B=%d C=%d 费用参考=%d 落库=%d 行",
        trade_date,
        l1.matched,
        l2.matched,
        l3.status.value if l3 else "SKIPPED",
        sum(1 for a in attributions if a.category is AttributionClass.A_SLIPPAGE),
        sum(1 for a in attributions if a.category is AttributionClass.B_PARTIAL_FILL),
        len(c_class_items),
        sum(1 for a in attributions if a.category is AttributionClass.REFERENCE_FEE),
        rows_written,
    )
    return result
