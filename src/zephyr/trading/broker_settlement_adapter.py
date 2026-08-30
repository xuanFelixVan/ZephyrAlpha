# [BLUEPRINT] MOD-TRADING-005 | docs/03_modules/_domain_trading/broker_settlement_adapter/blueprint.md
# [MODULE] zephyr.trading.broker_settlement_adapter
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.trading.settlement_reconciliation
# [CONSUMERS] zephyr.trading.recon_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配对键口径唯一真源(symbol+组内时间序); 适配纯转换不修改source状态; Decimal全程
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/trading/test_broker_settlement_adapter.py
# [A_module] module_id=MOD-TRADING-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_TRADING — 券商侧对账适配器（适配层 B，56号文 §2 G4）

把 QMT 模拟盘盘后查询结果（G3 query_trades_today 产出的 Fill 列表）适配成
SettlementReconciler 期望的 BrokerSettlementRecord 列表（字段对齐 L1 交易级对账输入）。

设计真源: docs/.../design_memos/56_backtest_vs_sim_reconciliation_plan.md §2（适配层 B）
口径铁律: 对账比对以**数量与成交价为主键**，佣金/税费仅作参考列（56号文 §3/§4 R1）。

配对键口径（两侧唯一真源，G5 回测侧适配器复用本模块函数）
----------------------------------------------------------
回测 trade_log 与实盘成交回报之间不存在可互认的券商 ID（回测无 traded_id），
故 L1 配对采用**业务主键**：``{symbol}|{seq:03d}`` —— 同标的组内按成交时间
升序的流水号（从 1 开始）。两侧适配器各自独立生成，同信号同窗口（56号文 §1
不变量 I1/I3）下两侧笔序一致即逐笔对上：

- 配对成功 + 成交价超容差 → A 类滑点（56号文 §3）
- 配对成功 + 实盘数量 < 回测数量 → B 类部分成交
- 一侧整笔缺失（键不配对）→ C 类拒单/缺失

已知近似：同标的同日多笔且两侧笔序错位（如实盘拆单）时可能错配，
由 56号文 C4（笔数差 ≤5%）与人工复核兜底。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: broker_settlement_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: seq 参数
#   fields: 参数 seq，类型注解 int
#   code: broker_settlement_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: fills 参数
#   fields: 参数 fills，类型注解 list[Fill]
#   code: broker_settlement_adapter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: trade_date 参数
#   fields: 参数 trade_date，类型注解 str
#   code: broker_settlement_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① BrokerTradeSource
#   name_en: BrokerTradeSource
#   intro: 券商盘后成交查询源协议（鸭子类型，MiniQmtBroker 已满足）。
#   desc: 券商盘后成交查询源协议（鸭子类型，MiniQmtBroker 已满足）。；公共方法（定义序）: query_trades_today；源码 L129-L132
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② make_business_pair_key
#   name_en: make_business_pair_key
#   intro: 生成 L1 对账业务配对键（两侧唯一口径真源）。
#   desc: 生成 L1 对账业务配对键（两侧唯一口径真源）。 Args: symbol: 标的代码 seq: 同标的组内按成交时间升序的流水号（从 1 开始） Returns: 配对键，形如…；源码 L135-L147
#   inputs: symbol seq
#   outputs: str
# - id: A3
#   name_zh: ③ fills_to_broker_records
#   name_en: fills_to_broker_records
#   intro: 券商成交 Fill 列表 → BrokerSettlementRecord 列表（适配层 B 主函数）。
#   desc: 券商成交 Fill 列表 → BrokerSettlementRecord 列表（适配层 B 主函数）。 字段映射（对齐 SettlementReconciler 期望）： tr…；源码 L150-L193
#   inputs: fills trade_date
#   outputs: list[BrokerSettlementRecord]
# - id: A4
#   name_zh: ④ fetch_broker_settlement_records
#   name_en: fetch_broker_settlement_records
#   intro: 编排：broker.query_trades_today() → BrokerSettlementRecord 列表。
#   desc: 编排：broker.query_trades_today() → BrokerSettlementRecord 列表。 盘后场景一次性拉取（56号文 §5 15:30 收盘后步骤…；源码 L196-L206
#   inputs: broker trade_date
#   outputs: list[BrokerSettlementRecord]
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.trading.recon_runner
# - id: O2
#   name_zh: list[BrokerSettlementRecord]
#   name_en: list[BrokerSettlementRecord]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.trading.recon_runner
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from typing import Final, Protocol

from zephyr.shared.contracts.fill import Fill
from zephyr.trading.settlement_reconciliation import BrokerSettlementRecord

_logger = logging.getLogger(__name__)

__all__: Final = [
    "BrokerTradeSource",
    "fetch_broker_settlement_records",
    "fills_to_broker_records",
    "make_business_pair_key",
]


class BrokerTradeSource(Protocol):
    """券商盘后成交查询源协议（鸭子类型，MiniQmtBroker 已满足）。"""

    def query_trades_today(self, trade_date: str | None = None) -> list[Fill]: ...


def make_business_pair_key(symbol: str, seq: int) -> str:
    """生成 L1 对账业务配对键（两侧唯一口径真源）。

    Args:
        symbol: 标的代码
        seq: 同标的组内按成交时间升序的流水号（从 1 开始）

    Returns:
        配对键，形如 "600000.SH|001"。系统侧写入 Fill.order_id
        （broker_fill_id 为空时的回退配对键），券商侧写入
        BrokerSettlementRecord.trade_id（优先配对键）。
    """
    return f"{symbol}|{seq:03d}"


def fills_to_broker_records(
    fills: list[Fill],
    trade_date: str,
) -> list[BrokerSettlementRecord]:
    """券商成交 Fill 列表 → BrokerSettlementRecord 列表（适配层 B 主函数）。

    字段映射（对齐 SettlementReconciler 期望）：
      trade_id            ← make_business_pair_key(symbol, 组内时间序)（业务主键）
      order_id            ← Fill.order_id（券商原始订单号，保留参考）
      symbol              ← Fill.symbol
      settlement_price    ← Fill.fill_price
      settlement_quantity ← Fill.filled_quantity
      commission          ← Fill.commission（参考列，不参与判定，56号文 C9）
      settlement_date     ← trade_date（YYYY-MM-DD）

    Args:
        fills: G3 query_trades_today 产出的当日成交（任意顺序，内部重排）
        trade_date: 结算日 "YYYY-MM-DD"
    """
    sorted_fills = sorted(fills, key=lambda f: f.fill_timestamp)
    seq_by_symbol: dict[str, int] = {}
    records: list[BrokerSettlementRecord] = []
    for fill in sorted_fills:
        seq = seq_by_symbol.get(fill.symbol, 0) + 1
        seq_by_symbol[fill.symbol] = seq
        records.append(
            BrokerSettlementRecord(
                trade_id=make_business_pair_key(fill.symbol, seq),
                order_id=fill.order_id,
                symbol=fill.symbol,
                settlement_price=fill.fill_price,
                settlement_quantity=fill.filled_quantity,
                commission=fill.commission,
                settlement_date=trade_date,
            )
        )
    _logger.info(
        "券商侧适配: trade_date=%s fills=%d records=%d symbols=%d",
        trade_date,
        len(fills),
        len(records),
        len(seq_by_symbol),
    )
    return records


def fetch_broker_settlement_records(
    broker: BrokerTradeSource,
    trade_date: str,
) -> list[BrokerSettlementRecord]:
    """编排：broker.query_trades_today() → BrokerSettlementRecord 列表。

    盘后场景一次性拉取（56号文 §5 15:30 收盘后步骤①）。
    broker 鸭子类型——生产为 MiniQmtBroker，测试注入 mock，不连真 QMT。
    """
    fills = broker.query_trades_today(trade_date)
    return fills_to_broker_records(fills, trade_date)
