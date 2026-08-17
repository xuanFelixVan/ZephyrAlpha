# [BLUEPRINT] MOD-TRADING-003 | docs/03_modules/_domain_trading/settlement_reconciliation/blueprint.md
# [MODULE] zephyr.trading.settlement_reconciliation
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting; zephyr.governance
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only金额/数量比较; BrokerSettlementRecord/SettlementDrift/ReconciliationResult/SettlementReport frozen不可变; reconcile纯读不修改source状态; on_discrepancy异常不阻断对账; report_hash=SHA-256(canonical_json)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSettlementInputError(ZA-TR-0003)
# [TESTS] tests/trading/test_settlement_reconciliation.py
# [A_module] module_id=MOD-TRADING-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_TRADING — Settlement & Reconciliation Engine (结算对账器)

盘后交易级对账基础设施。每日 15:30 后自动比对系统交易记录(来自 D-EX-CORE
的 Fill)与券商结算单(BrokerSettlementRecord), 逐笔检测价格/数量/佣金差异及
缺失记录, 产出结算报告并触发差异告警。

与 D-EX-CORE-56 持仓对账器互补:
  - EX-56: 持仓级对账(盘中5分钟, 比对 position quantity, 差异→冻结交易)
  - TRADING-003: 交易级对账(盘后15:30, 比对 trade price/qty/commission, 差异→告警+报告)

产出 E-TR-01 SettlementCompleted / E-TR-02 ReconciliationCompleted 事件
(阶段1用回调模式, 阶段2接入事件总线)。

设计真源: D:/临时工作区/依赖图/18-D-TRADING-交易运营域.md §1 D-TRADING-02
蓝图: docs/03_modules/_domain_trading/settlement_reconciliation/blueprint.md

属 A 类基础设施(确定性比对 + 容差检测), 纯消费层不修改 source 状态。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 系统侧交易记录 system_fills（list[Fill]，来自 D-EX-CORE）
#   fields: broker_fill_id(优先配对键)/order_id(回退)/symbol/fill_price/filled_quantity/commission
#   code: reconcile(system_fills) L203
# - id: I2
#   name: 券商结算单 broker_records（list[BrokerSettlementRecord]）
#   fields: trade_id/order_id/symbol/settlement_price/settlement_quantity/commission/settlement_date
#   code: BrokerSettlementRecord L94
# - id: I3
#   name: 对账容差配置 ReconciliationConfig（C类可调参数）
#   fields: price_tolerance=0.01元 / quantity_tolerance=0(数量必须精确) / commission_tolerance=0.01元
#   code: ReconciliationConfig L78
# 层: 算法
# - id: A1
#   name_zh: ① 配对索引构建
#   name_en: reconcile 索引段
#   intro: 系统侧按 broker_fill_id 优先 order_id 回退建键，券商侧按 trade_id/order_id 建键
#   desc: 两侧各建 dict 索引；券商记录结算日期与对账日期不一致仅告警不剔除
#   inputs: I1 I2
#   outputs: system_by_id + broker_by_id
# - id: A2
#   name_zh: ② 逐字段容差比较
#   name_en: _compare_fields
#   intro: 配对成功的逐笔比对价格/数量/佣金，超容差记差异
#   desc: diff=system-broker；|diff|>tolerance → PRICE/QUANTITY/COMMISSION_MISMATCH；数量容差=0 必须精确
#   inputs: A1 I3
#   outputs: SettlementDrift 列表（MISMATCH 类）
# - id: A3
#   name_zh: ③ 缺失记录检测
#   name_en: reconcile 缺失检测段
#   intro: 系统有券商无、券商有系统无，分别记两种缺失差异
#   desc: 未配对系统Fill→MISSING_IN_BROKER；未配对券商记录→MISSING_IN_SYSTEM
#   inputs: A1
#   outputs: SettlementDrift 列表（MISSING 类）
# - id: A4
#   name_zh: ④ 差异告警回调
#   name_en: on_discrepancy trigger
#   intro: 有差异时触发告警回调，回调异常只记日志不阻断对账
#   desc: matched=(drifts为空)；False 时调 on_discrepancy(result)，异常 catch+log
#   inputs: A2 A3
#   outputs: E-TR-02 差异告警（阶段1回调模式）
# - id: A5
#   name_zh: ⑤ 结算报告生成（含哈希指纹）
#   name_en: generate_report
#   intro: 把对账结果打包成不可变报告，SHA-256 指纹防篡改
#   desc: canonical_json(sorted keys)+SHA-256→report_hash；report_id=SR-+uuid12位
#   inputs: A2 A3
#   outputs: SettlementReport
#   invariant: report_hash=SHA-256(canonical_json)
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconciliationResult
#   name_en: ReconciliationResult
#   intro: matched 标志+差异元组+两侧笔数/成功配对笔数，frozen 不可变
#   invariant: reconcile 纯读不修改 source 状态
#   downstream: generate_report（A5）；on_discrepancy 告警
# - id: O2
#   name_zh: 结算报告 SettlementReport（E-TR-01/E-TR-02 事件）
#   name_en: SettlementReport
#   intro: 含哈希指纹的盘后结算报告，供报表与治理域归档审计
#   downstream: zephyr.reporting；zephyr.governance
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I3 --> A2
# A1 --> A3
# A2 --> A4
# A3 --> A4
# A2 --> A5
# A3 --> A5
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A5 --> O2
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Callable

from zephyr.shared.contracts.fill import Fill
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"


class InvalidSettlementInputError(ZephyrBaseError):
    """结算对账输入非法——空结算日期/负价格/负数量等。"""

    error_code = "ZA-TR-0003"


# ── 枚举 ──


class DriftType(str, Enum):
    """结算差异类型——5种。"""

    PRICE_MISMATCH = "price_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    COMMISSION_MISMATCH = "commission_mismatch"
    MISSING_IN_SYSTEM = "missing_in_system"
    MISSING_IN_BROKER = "missing_in_broker"


# ── 容差配置 (C 类可调参数) ──


@dataclass(frozen=True)
class ReconciliationConfig:
    """对账容差配置——全部可调参数, 非硬编码。

    A股交易数量必须精确匹配(quantity_tolerance=0), 价格/佣金允许微小差异
    (券商系统精度差异)。
    """

    price_tolerance: Decimal = Decimal("0.01")  # 0.01元
    quantity_tolerance: Decimal = Decimal("0")  # 0股(必须精确)
    commission_tolerance: Decimal = Decimal("0.01")  # 0.01元


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class BrokerSettlementRecord:
    """券商结算单单笔记录——来自券商盘后结算单, 不可变。

    trade_id 对应 Fill.broker_fill_id (优先配对键);
    order_id 为回退配对键 (当 broker_fill_id 缺失时)。
    """

    trade_id: str
    order_id: str
    symbol: str
    settlement_price: Decimal
    settlement_quantity: Decimal
    commission: Decimal
    settlement_date: str  # YYYY-MM-DD


@dataclass(frozen=True)
class SettlementDrift:
    """单笔结算差异记录——不可变。

    对于 MISSING_IN_SYSTEM: system_value=None, broker_value=券商记录值
    对于 MISSING_IN_BROKER: system_value=系统Fill值, broker_value=None
    对于 *_MISMATCH:        两端都有值, diff=system_value-broker_value
    """

    trade_id: str
    symbol: str
    drift_type: DriftType
    system_value: Decimal | None
    broker_value: Decimal | None
    diff: Decimal | None


@dataclass(frozen=True)
class ReconciliationResult:
    """一次对账的结果——不可变。

    Attributes:
        timestamp: 对账时刻
        settlement_date: 结算日期(YYYY-MM-DD)
        matched: True=无差异(drifts 为空)
        drifts: 差异项元组(空 tuple = 一致)
        total_system_trades: 系统侧交易笔数
        total_broker_trades: 券商侧交易笔数
        matched_trades: 成功配对且无差异的交易笔数
    """

    timestamp: datetime
    settlement_date: str
    matched: bool
    drifts: tuple[SettlementDrift, ...]
    total_system_trades: int
    total_broker_trades: int
    matched_trades: int


@dataclass(frozen=True)
class SettlementReport:
    """结算报告——含对账结果和哈希指纹的不可变记录。

    report_hash = SHA-256(canonical_json(content)), 用于防篡改校验。
    """

    report_id: str
    settlement_date: str
    portfolio_id: str
    generated_at: datetime
    result: ReconciliationResult
    report_hash: str
    schema_version: str = _SCHEMA_VERSION


# ── 结算对账器主类 ──


class SettlementReconciler:
    """结算对账器 (D-TRADING-02)——盘后交易级对账。

    比对系统交易记录(Fill)与券商结算单(BrokerSettlementRecord),
    按 trade_id/order_id 配对后逐字段(价格/数量/佣金)容差比较,
    检测缺失记录, 产出 ReconciliationResult + SettlementReport。

    Usage:
        reconciler = SettlementReconciler(
            config=ReconciliationConfig(),
            on_discrepancy=lambda r: alert_service.send(r),
        )

        result = reconciler.reconcile(system_fills, broker_records, "2026-08-01")
        if not result.matched:
            # result.drifts ...

        report = reconciler.generate_report(result, portfolio_id="PF-001")

    Thread Safety:
        无共享可变状态(config/on_discrepancy 均不可变), reconcile() 线程安全。
    """

    def __init__(
        self,
        config: ReconciliationConfig | None = None,
        on_discrepancy: Callable[[ReconciliationResult], None] | None = None,
    ) -> None:
        self._config = config if config is not None else ReconciliationConfig()
        self._on_discrepancy = on_discrepancy

    def reconcile(
        self,
        system_fills: list[Fill],
        broker_records: list[BrokerSettlementRecord],
        settlement_date: str,
    ) -> ReconciliationResult:
        """执行一次对账：配对+逐字段比较+缺失检测, 返回结果。

        - 按 broker_fill_id(优先)/order_id(回退) 建立配对索引
        - 配对后逐字段容差比较(price/quantity/commission)
        - 未配对的系统Fill → MISSING_IN_BROKER
        - 未配对的券商记录 → MISSING_IN_SYSTEM
        - matched=False 时触发 on_discrepancy 回调(异常被 catch+log, 不阻断)
        """
        if not settlement_date:
            raise InvalidSettlementInputError(
                "settlement_date 不能为空",
                details={"settlement_date": settlement_date},
            )

        # ── 构建系统侧索引: trade_id → Fill ──
        system_by_id: dict[str, Fill] = {}
        for fill in system_fills:
            key = fill.broker_fill_id if fill.broker_fill_id else fill.order_id
            system_by_id[key] = fill

        # ── 构建券商侧索引: trade_id → BrokerSettlementRecord ──
        broker_by_id: dict[str, BrokerSettlementRecord] = {}
        for rec in broker_records:
            # 验证结算日期一致
            if rec.settlement_date != settlement_date:
                _logger.warning(
                    "券商记录结算日期不匹配: trade_id=%s record_date=%s expected=%s",
                    rec.trade_id,
                    rec.settlement_date,
                    settlement_date,
                )
            key = rec.trade_id if rec.trade_id else rec.order_id
            broker_by_id[key] = rec

        # ── 配对 + 逐字段比较 ──
        drifts: list[SettlementDrift] = []
        matched_count = 0
        paired_keys: set[str] = set()

        for key, fill in system_by_id.items():
            broker_rec = broker_by_id.get(key)
            if broker_rec is None:
                # 系统有但券商无
                drifts.append(
                    SettlementDrift(
                        trade_id=key,
                        symbol=fill.symbol,
                        drift_type=DriftType.MISSING_IN_BROKER,
                        system_value=fill.fill_price,
                        broker_value=None,
                        diff=None,
                    )
                )
                continue

            paired_keys.add(key)
            fill_drifts = self._compare_fields(fill, broker_rec)
            if fill_drifts:
                drifts.extend(fill_drifts)
            else:
                matched_count += 1

        # 券商有但系统无
        for key, rec in broker_by_id.items():
            if key not in paired_keys and key not in system_by_id:
                drifts.append(
                    SettlementDrift(
                        trade_id=key,
                        symbol=rec.symbol,
                        drift_type=DriftType.MISSING_IN_SYSTEM,
                        system_value=None,
                        broker_value=rec.settlement_price,
                        diff=None,
                    )
                )

        result = ReconciliationResult(
            timestamp=datetime.now(UTC),
            settlement_date=settlement_date,
            matched=len(drifts) == 0,
            drifts=tuple(drifts),
            total_system_trades=len(system_by_id),
            total_broker_trades=len(broker_by_id),
            matched_trades=matched_count,
        )

        if not result.matched:
            _logger.warning(
                "结算对账发现差异: date=%s drifts=%d system_trades=%d broker_trades=%d matched=%d",
                settlement_date,
                len(drifts),
                result.total_system_trades,
                result.total_broker_trades,
                matched_count,
            )
            if self._on_discrepancy is not None:
                try:
                    self._on_discrepancy(result)
                except Exception:  # noqa: BLE001 — 告警通道故障不阻断对账主流程
                    _logger.exception("on_discrepancy 回调异常（已忽略，不影响对账结果）")

        return result

    def generate_report(
        self,
        result: ReconciliationResult,
        portfolio_id: str,
    ) -> SettlementReport:
        """从对账结果生成结算报告（含哈希指纹）。

        report_hash = SHA-256(canonical_json(report_content))
        """
        # 构建哈希内容（canonical JSON: sorted keys, 无空格）
        drifts_summary = [
            {
                "trade_id": d.trade_id,
                "symbol": d.symbol,
                "drift_type": d.drift_type.value,
                "system_value": str(d.system_value) if d.system_value is not None else None,
                "broker_value": str(d.broker_value) if d.broker_value is not None else None,
                "diff": str(d.diff) if d.diff is not None else None,
            }
            for d in result.drifts
        ]
        hash_content = {
            "settlement_date": result.settlement_date,
            "portfolio_id": portfolio_id,
            "total_system_trades": result.total_system_trades,
            "total_broker_trades": result.total_broker_trades,
            "matched_trades": result.matched_trades,
            "drift_count": len(result.drifts),
            "drifts_summary": drifts_summary,
            "matched": result.matched,
        }
        canonical = json.dumps(hash_content, sort_keys=True, ensure_ascii=False)
        report_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        report = SettlementReport(
            report_id=f"SR-{uuid.uuid4().hex[:12]}",
            settlement_date=result.settlement_date,
            portfolio_id=portfolio_id,
            generated_at=datetime.now(UTC),
            result=result,
            report_hash=report_hash,
        )

        _logger.info(
            "结算报告生成: report_id=%s date=%s portfolio=%s matched=%s drifts=%d hash=%s",
            report.report_id,
            report.settlement_date,
            portfolio_id,
            result.matched,
            len(result.drifts),
            report_hash[:16],
        )
        return report

    # ── 内部方法 ──

    def _compare_fields(self, fill: Fill, rec: BrokerSettlementRecord) -> list[SettlementDrift]:
        """逐字段比较单笔配对交易, 返回差异列表(空=无差异)。"""
        drifts: list[SettlementDrift] = []
        cfg = self._config
        trade_id = rec.trade_id if rec.trade_id else rec.order_id
        symbol = fill.symbol

        # 价格差异
        price_diff = fill.fill_price - rec.settlement_price
        if abs(price_diff) > cfg.price_tolerance:
            drifts.append(
                SettlementDrift(
                    trade_id=trade_id,
                    symbol=symbol,
                    drift_type=DriftType.PRICE_MISMATCH,
                    system_value=fill.fill_price,
                    broker_value=rec.settlement_price,
                    diff=price_diff,
                )
            )

        # 数量差异
        qty_diff = fill.filled_quantity - rec.settlement_quantity
        if abs(qty_diff) > cfg.quantity_tolerance:
            drifts.append(
                SettlementDrift(
                    trade_id=trade_id,
                    symbol=symbol,
                    drift_type=DriftType.QUANTITY_MISMATCH,
                    system_value=fill.filled_quantity,
                    broker_value=rec.settlement_quantity,
                    diff=qty_diff,
                )
            )

        # 佣金差异
        comm_diff = fill.commission - rec.commission
        if abs(comm_diff) > cfg.commission_tolerance:
            drifts.append(
                SettlementDrift(
                    trade_id=trade_id,
                    symbol=symbol,
                    drift_type=DriftType.COMMISSION_MISMATCH,
                    system_value=fill.commission,
                    broker_value=rec.commission,
                    diff=comm_diff,
                )
            )

        return drifts


__all__ = [
    "BrokerSettlementRecord",
    "DriftType",
    "InvalidSettlementInputError",
    "ReconciliationConfig",
    "ReconciliationResult",
    "SettlementDrift",
    "SettlementReconciler",
    "SettlementReport",
]
