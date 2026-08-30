# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.execution_report
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.execution_report(CTR-P1-007); zephyr.ex_core.execution_engine(ExecutionEngineRunRecord); zephyr.shared.contracts.order; zephyr.shared.foundation.errors
# [CONSUMERS] D_REPORTING(TCA/归因数据流上游, BM-REC-02-B); 调用方(执行完成事件驱动产出)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 产出物=CTR-P1-007 frozen契约; 滑点口径=40号§2.4 DECISION决策价基准(买入正滑点=不利); intended_price=order.limit_price; 函数级产出(不改 ExecutionEngine 生产路径); 输入不一致(order_id不匹配/量非正)Fail-Closed拒绝
# [MODIFY-GUARD] 40_execution_broker.md §2.4; execution_core blueprint GAP-L06-003
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidExecutionReportInputError(ZA-EX-0012)
# [TESTS] tests/ex_core/test_execution_report.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: Order(委托单, 含 side/limit_price/quantity/idempotency_key) + ExecutionEngineRunRecord(引擎聚合快照: filled_quantity/avg_fill_price/commission/venue/algo_type/起止时间)
# F1: build_execution_report(order, run_record)——组装 CTR-P1-007 ExecutionReport(frozen codegen 契约)
# F2: 滑点计算——signed_slippage_bps: BUY=(avg_fill-intended)/intended×1e4; SELL=(intended-avg_fill)/intended×1e4(正=不利成本); intended=0 退化 0.0
# F3: vwap_price=avg_fill_price(单券商 MVP 口径: 成交量加权均价即成交均价)
# O1: ExecutionReport(CTR-P1-007) -> D_REPORTING(TCA/归因消费)
# [/ALGO_FLOW]
"""
D_EX_CORE — CTR-P1-007 ExecutionReport 产出逻辑（GAP-L06-003 P0）。

execution_core blueprint GAP-L06-003（P0：无 ExecutionReport → D_REPORTING 需要
执行报告）；battle_map BM-REC-02-B"暂不可建"标注的残余阻塞（54 号 §7 开放问题：
契约 codegen 已落盘但产出逻辑未施工）。本模块为函数级产出：把执行引擎内部聚合
快照（ExecutionEngineRunRecord）+ 委托单（Order）组装为 CTR-P1-007 frozen 契约，
供 TCA / 归因数据流消费。

滑点口径（40 号 §2.4 DECISION 决策价基准）：以 order.limit_price 为决策基准，
带方向符号——正滑点=不利成本（买贵/卖贱），负滑点=有利。BUY 正差为不利，
SELL 负差为不利。

工程裁定：函数级产出，不改 ExecutionEngine 生产路径（产出接线由执行完成事件
驱动方调用本函数）；vwap_price 取 avg_fill_price（单券商 MVP，多券商汇聚
口径随 GAP-L06-002 富途/IB 适配器重评）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: order 参数
#   fields: 参数 order，类型注解 Order
#   code: execution_report.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: run_record 参数
#   fields: 参数 run_record，类型注解 ExecutionEngineRunRecord
#   code: execution_report.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_execution_report
#   name_en: build_execution_report
#   intro: 组装 CTR-P1-007 ExecutionReport（GAP-L06-003 产出逻辑）。
#   desc: 组装 CTR-P1-007 ExecutionReport（GAP-L06-003 产出逻辑）。 Args: order: 委托单（side/limit_price/quanti…；源码 L102-L160
#   inputs: order run_record
#   outputs: ExecutionReport
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ExecutionReport
#   name_en: ExecutionReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: D_REPORTING(TCA/归因数据流上游, BM-REC-02-B); 调用方(执行完成事件驱动产出)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from zephyr.ex_core.execution_engine import ExecutionEngineRunRecord
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError


class InvalidExecutionReportInputError(ZephyrBaseError):
    """ExecutionReport 产出输入非法——order_id 不匹配/量非正/价为负等。"""

    error_code = "ZA-EX-0012"


def _signed_slippage_bps(side: OrderSide, intended_price: Decimal, avg_fill_price: Decimal) -> float:
    """带方向符号滑点（bps，正=不利成本）。intended≤0 退化 0.0（无基准不判定）。"""
    if intended_price <= 0:
        return 0.0
    if side is OrderSide.SELL:
        raw = (intended_price - avg_fill_price) / intended_price
    else:  # BUY（及未知方向保守按 BUY 口径：成交价高于基准=不利）
        raw = (avg_fill_price - intended_price) / intended_price
    return float(raw * Decimal("10000"))


def build_execution_report(
    order: Order,
    run_record: ExecutionEngineRunRecord,
) -> ExecutionReport:
    """组装 CTR-P1-007 ExecutionReport（GAP-L06-003 产出逻辑）。

    Args:
        order: 委托单（side/limit_price/quantity/idempotency_key 来源）。
        run_record: 执行引擎聚合快照（filled_quantity/avg_fill_price/commission/
            venue/algo_type/起止时间来源）。

    Returns:
        ExecutionReport（CTR-P1-007 frozen 契约，TCA/归因数据流上游）。

    Raises:
        InvalidExecutionReportInputError: order_id 不匹配 / intended_quantity 非正 /
            filled_quantity 为负 / avg_fill_price 为负。
    """
    if order.order_id != run_record.order_id:
        raise InvalidExecutionReportInputError(
            "order 与 run_record 的 order_id 不匹配",
            details={"order_id": order.order_id, "run_record_order_id": run_record.order_id},
        )
    intended_qty = int(run_record.total_quantity)
    actual_qty = int(run_record.filled_quantity)
    if intended_qty <= 0:
        raise InvalidExecutionReportInputError(
            "intended_quantity 必须为正",
            details={"total_quantity": str(run_record.total_quantity)},
        )
    if actual_qty < 0:
        raise InvalidExecutionReportInputError(
            "filled_quantity 不能为负",
            details={"filled_quantity": str(run_record.filled_quantity)},
        )
    intended_price = run_record.target_price
    avg_fill_price = run_record.avg_fill_price
    if intended_price < 0 or avg_fill_price < 0:
        raise InvalidExecutionReportInputError(
            "价格不能为负",
            details={"target_price": str(intended_price), "avg_fill_price": str(avg_fill_price)},
        )

    return ExecutionReport(
        actual_quantity=actual_qty,
        broker_id=run_record.venue,
        commission=run_record.commission,
        direction=order.side.value if hasattr(order.side, "value") else str(order.side),
        execution_end=run_record.end_time.isoformat(),
        execution_start=run_record.start_time.isoformat(),
        idempotency_key=order.idempotency_key,
        intended_price=intended_price,
        intended_quantity=intended_qty,
        order_id=order.order_id,
        slippage_bps=_signed_slippage_bps(order.side, intended_price, avg_fill_price),
        symbol=order.symbol,
        vwap_price=avg_fill_price,
        algo_type=run_record.algo_type or "NONE",
    )


__all__ = [
    "InvalidExecutionReportInputError",
    "build_execution_report",
]
