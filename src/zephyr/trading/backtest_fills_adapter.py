# [BLUEPRINT] MOD-TRADING-006 | docs/03_modules/_domain_trading/backtest_fills_adapter/blueprint.md
# [MODULE] zephyr.trading.backtest_fills_adapter
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.backtest.io.result_repository; zephyr.shared.contracts.fill; zephyr.trading.broker_settlement_adapter
# [CONSUMERS] zephyr.trading.recon_runner
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 配对键口径=broker_settlement_adapter.make_business_pair_key; 适配纯转换不修改source状态; Decimal全程; 持仓重放buy+sell-零持仓过滤
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ArtifactNotFoundError(透传 result_repository)
# [TESTS] tests/trading/test_backtest_fills_adapter.py
# [A_module] module_id=MOD-TRADING-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_TRADING — 回测侧对账适配层（适配层 A，56号文 §2 G5）

读 data/backtest_artifacts/{run_id}.json 的 trade_log（TradeRecord 口径），
适配成 SettlementReconciler 系统侧输入（list[Fill]，CTR-005 契约）；
回测日终持仓由 trade_log 重放推导（buy + / sell −，零持仓过滤）。

设计真源: docs/.../design_memos/56_backtest_vs_sim_reconciliation_plan.md §2（适配层 A）
前置不变量: I4 逐笔可得——跑批必须经 backtest_result_sink 落 artifact（56号文 §1）。

字段映射（TradeRecord → Fill）
------------------------------
  timestamp  → fill_timestamp（ISO8601 解析；naive 一律按 UTC 归一，仅用于
               排序/交易日推导——同一 artifact 内时间戳由 sink 同源产出，格式一致）
  symbol     → symbol
  side       → 不入 Fill（CTR-005 无方向字段）；持仓重放时使用（buy +/sell −）
  price      → fill_price（Decimal(str()) 转换，禁 float 直传）
  quantity   → filled_quantity（同上）
  commission → commission（参考列，56号文 C9：仅记录不判定）
  配对键     → order_id = make_business_pair_key(symbol, 组内时间序)
              （broker_fill_id=None，SettlementReconciler 回退 order_id 配对；
              口径真源=broker_settlement_adapter，两侧同款方能逐笔对上）
  fill_id    → f"bt-{run_id}-{symbol}-{seq:03d}"（回测侧全局唯一）
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Final

from zephyr.backtest.io.result_repository import get_artifact
from zephyr.shared.contracts.fill import Fill
from zephyr.trading.broker_settlement_adapter import make_business_pair_key

_logger = logging.getLogger(__name__)

__all__: Final = [
    "load_backtest_fills",
    "load_backtest_trade_log",
    "replay_positions_from_trade_log",
    "trades_to_fills",
]

# 买卖方向字面量（backtest_result_sink.TradeRecord.side 口径）
_SIDE_BUY: Final = "buy"
_SIDE_SELL: Final = "sell"


def _parse_ts(ts: str) -> datetime:
    """ISO8601 时间戳解析；naive 按 UTC 归一（仅排序/日期推导用，见模块头口径）。"""
    dt = datetime.fromisoformat(ts)
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def trades_to_fills(
    trade_log: list[dict[str, Any]],
    strategy_id: str,
    run_id: str,
) -> list[Fill]:
    """回测 trade_log（list[dict]，TradeRecord 口径）→ 系统侧 Fill 列表。

    Args:
        trade_log: BacktestRunArtifact.trade_log 原生 dict 列表
        strategy_id: 策略 ID（artifact.strategy_id）
        run_id: 回测运行 ID（fill_id/idempotency_key 唯一性来源）

    Returns:
        list[Fill]：按成交时间升序；order_id=业务配对键（组内时间序）。
    """
    sorted_trades = sorted(trade_log, key=lambda t: _parse_ts(t["timestamp"]))
    seq_by_symbol: dict[str, int] = {}
    fills: list[Fill] = []
    for trade in sorted_trades:
        symbol = str(trade["symbol"])
        seq = seq_by_symbol.get(symbol, 0) + 1
        seq_by_symbol[symbol] = seq
        unique_suffix = f"{symbol}-{seq:03d}"
        fills.append(
            Fill(
                fill_id=f"bt-{run_id}-{unique_suffix}",
                fill_price=Decimal(str(trade["price"])),
                fill_timestamp=_parse_ts(trade["timestamp"]),
                filled_quantity=Decimal(str(trade["quantity"])),
                idempotency_key=f"bt-{run_id}-{unique_suffix}",
                order_id=make_business_pair_key(symbol, seq),
                strategy_id=strategy_id,
                symbol=symbol,
                broker_fill_id=None,  # 回测无券商成交号，回退 order_id 配对
                commission=Decimal(str(trade.get("commission", 0) or 0)),
            )
        )
    _logger.info(
        "回测侧适配: run_id=%s trades=%d fills=%d symbols=%d",
        run_id,
        len(trade_log),
        len(fills),
        len(seq_by_symbol),
    )
    return fills


def load_backtest_trade_log(
    run_id: str,
    storage_path: Path | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """读 backtest_artifacts/{run_id}.json，返回 (trade_log, strategy_id)。

    Raises:
        ArtifactNotFoundError: run_id 不存在或文件损坏（透传 result_repository）。
    """
    artifact = get_artifact(run_id, storage_path=storage_path)
    return artifact.trade_log, artifact.strategy_id


def load_backtest_fills(
    run_id: str,
    storage_path: Path | None = None,
) -> list[Fill]:
    """读回测产物并适配为系统侧 Fill 列表（适配层 A 主入口）。

    Args:
        run_id: 回测运行 ID（save_artifact 返回值）
        storage_path: 产物目录（默认 data/backtest_artifacts/，测试注入 tmp）
    """
    trade_log, strategy_id = load_backtest_trade_log(run_id, storage_path=storage_path)
    return trades_to_fills(trade_log, strategy_id, run_id)


def replay_positions_from_trade_log(trade_log: list[dict[str, Any]]) -> dict[str, Decimal]:
    """由 trade_log 重放推导日终持仓（56号文 §2 L2 基准侧持仓来源）。

    buy 加 / sell 减，净零持仓标的剔除（语义对齐 portfolio 重放口径）。
    """
    holdings: dict[str, Decimal] = {}
    for trade in trade_log:
        symbol = str(trade["symbol"])
        qty = Decimal(str(trade["quantity"]))
        side = str(trade.get("side", "")).lower()
        if side == _SIDE_BUY:
            holdings[symbol] = holdings.get(symbol, Decimal("0")) + qty
        elif side == _SIDE_SELL:
            holdings[symbol] = holdings.get(symbol, Decimal("0")) - qty
        else:
            _logger.warning("trade_log 存在未知 side=%s，跳过该笔: %s", side, trade)
    return {symbol: qty for symbol, qty in holdings.items() if qty != 0}
