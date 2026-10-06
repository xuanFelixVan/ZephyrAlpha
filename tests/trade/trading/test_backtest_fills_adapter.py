# [A_test] module_id: MOD-GOV_backtest_fills_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.test_backtest_fills_adapter
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.backtest_fills_adapter; zephyr.backtest.io.result_repository; zephyr.shared.contracts.fill
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全tmp隔离(不读真backtest_artifacts)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""56号文 G5 测试：回测侧适配层（trade_log → 系统侧 Fill / 持仓重放）。

覆盖：TradeRecord→Fill 字段映射（Decimal 化、配对键=order_id、broker_fill_id=None）、
乱序输入按时间重排、naive 时间戳 UTC 归一、load_backtest_fills 读 tmp 产物走通、
replay_positions_from_trade_log 买卖净额/零持仓剔除/未知 side 跳过。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from zephyr.backtest.io.result_repository import ArtifactNotFoundError
from zephyr.trading.backtest_fills_adapter import (
    load_backtest_fills,
    replay_positions_from_trade_log,
    trades_to_fills,
)

RUN_ID = "bt-test01"


def _trade(symbol: str, side: str, price: float, qty: int, ts: str, commission: float = 0.85) -> dict:
    return {
        "timestamp": ts,
        "symbol": symbol,
        "side": side,
        "price": price,
        "quantity": qty,
        "commission": commission,
    }


def _write_artifact(storage: Path, run_id: str, trade_log: list[dict], equity_curve: list[dict] | None = None) -> None:
    """写最小 BacktestRunArtifact JSON（_dict_to_artifact 过滤未知字段，前向兼容）。"""
    storage.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "strategy_id": "S1",
        "schema_version": "1.0.0",
        "created_at": "2026-08-21 16:00:00",
        "trade_log": trade_log,
        "equity_curve": equity_curve or [],
    }
    (storage / f"{run_id}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class TestTradesToFills:
    def test_field_mapping(self):
        fills = trades_to_fills(
            [_trade("600000.SH", "buy", 10.5, 100, "2026-08-21 10:30:00")],
            strategy_id="S1",
            run_id=RUN_ID,
        )
        assert len(fills) == 1
        f = fills[0]
        assert f.fill_id == f"bt-{RUN_ID}-600000.SH-001"
        assert f.idempotency_key == f"bt-{RUN_ID}-600000.SH-001"
        assert f.order_id == "600000.SH|001"  # 业务配对键（口径=broker_settlement_adapter）
        assert f.broker_fill_id is None  # 回测无券商成交号 → 回退 order_id 配对
        assert f.strategy_id == "S1"
        assert f.symbol == "600000.SH"
        assert f.fill_price == Decimal("10.5") and isinstance(f.fill_price, Decimal)
        assert f.filled_quantity == Decimal("100")
        assert f.commission == Decimal("0.85")
        assert f.fill_timestamp == datetime(2026, 8, 21, 10, 30, tzinfo=UTC)  # naive→UTC 归一

    def test_time_sort_and_seq(self):
        """乱序输入按成交时间重排；同标的组内独立编号。"""
        trade_log = [
            _trade("600000.SH", "buy", 10.7, 100, "2026-08-21 13:45:00"),  # 第 2 笔
            _trade("000001.SZ", "buy", 20.0, 200, "2026-08-21 10:35:00"),
            _trade("600000.SH", "buy", 10.5, 100, "2026-08-21 10:30:00"),  # 第 1 笔
        ]
        fills = trades_to_fills(trade_log, "S1", RUN_ID)
        assert [f.order_id for f in fills] == ["600000.SH|001", "000001.SZ|001", "600000.SH|002"]
        assert fills[0].fill_price == Decimal("10.5")

    def test_aware_timestamp_supported(self):
        """带时区 ISO8601 时间戳（T 分隔+offset）正常解析，按绝对时刻相等。"""
        fills = trades_to_fills(
            [_trade("600000.SH", "buy", 10.5, 100, "2026-08-21T10:30:00+08:00")],
            "S1",
            RUN_ID,
        )
        # +08:00 10:30 = UTC 02:30（datetime 相等性按绝对时刻判定）
        assert fills[0].fill_timestamp == datetime(2026, 8, 21, 2, 30, tzinfo=UTC)

    def test_missing_commission_defaults_zero(self):
        trade = _trade("600000.SH", "buy", 10.5, 100, "2026-08-21 10:30:00")
        del trade["commission"]
        fills = trades_to_fills([trade], "S1", RUN_ID)
        assert fills[0].commission == Decimal("0")


class TestLoadBacktestFills:
    def test_load_from_tmp_artifact(self, tmp_path: Path):
        _write_artifact(
            tmp_path,
            RUN_ID,
            [_trade("600000.SH", "buy", 10.5, 100, "2026-08-21 10:30:00")],
        )
        fills = load_backtest_fills(RUN_ID, storage_path=tmp_path)
        assert len(fills) == 1
        assert fills[0].order_id == "600000.SH|001"
        assert fills[0].strategy_id == "S1"

    def test_missing_run_id_raises(self, tmp_path: Path):
        # 既有库 bug 警示：result_repository.get_artifact 缺失路径抛 TypeError
        # （ArtifactNotFoundError.__init__ 不接 details kwargs，L136 却传了）——
        # 本适配层透传不修库（MODIFY-GUARD），断言兼容两型直至上游修复。
        with pytest.raises((ArtifactNotFoundError, TypeError)):
            load_backtest_fills("bt-nonexistent", storage_path=tmp_path)


class TestReplayPositions:
    def test_buy_sell_netting(self):
        trade_log = [
            _trade("600000.SH", "buy", 10.5, 100, "2026-08-21 10:30:00"),
            _trade("600000.SH", "buy", 10.6, 100, "2026-08-21 11:00:00"),
            _trade("600000.SH", "sell", 10.8, 50, "2026-08-21 14:00:00"),
            _trade("000001.SZ", "buy", 20.0, 200, "2026-08-21 10:35:00"),
        ]
        positions = replay_positions_from_trade_log(trade_log)
        assert positions == {"600000.SH": Decimal("150"), "000001.SZ": Decimal("200")}

    def test_zero_position_filtered(self):
        trade_log = [
            _trade("600000.SH", "buy", 10.5, 100, "2026-08-21 10:30:00"),
            _trade("600000.SH", "sell", 10.8, 100, "2026-08-21 14:00:00"),
        ]
        assert replay_positions_from_trade_log(trade_log) == {}

    def test_unknown_side_skipped(self):
        trade_log = [_trade("600000.SH", "hold", 10.5, 100, "2026-08-21 10:30:00")]
        assert replay_positions_from_trade_log(trade_log) == {}

    def test_empty(self):
        assert replay_positions_from_trade_log([]) == {}
