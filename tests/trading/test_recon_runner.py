# [A_test] module_id: MOD-GOV_recon_runner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.trading.test_recon_runner
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.recon_runner; zephyr.shared.contracts.fill; zephyr.shared.contracts.position
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全tmp/mock隔离(不连真QMT/不写真governance.db); 临时库夹具复刻生产schema
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""56号文 G7 测试：recon_runner 日终对账编排器。

覆盖：三层串联（L1 交易级/L2 持仓级/L3 PnL 级）、归因三分类
（A 滑点/B 部分成交/C 拒单缺失 + 费用参考列不归类）、
reconciliation_differences 落库（trade/position/cash 三层，tmp 库复刻生产
schema）、L3 SKIPPED/MISMATCH、db_error 降级路径、C 类当日告警清单。
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.trading.recon_runner import (
    AttributionClass,
    ReconDailyResult,
    run_daily_reconciliation,
)

TRADE_DATE = "2026-08-21"
RUN_ID = "bt-recon01"

# 生产 reconciliation_differences DDL（#234 已执行）——夹具复刻生产 schema
# （trend_analyzer db_path 隔离先例：测试库结构 MUST 与生产一致）
_PROD_DDL = """
CREATE TABLE reconciliation_differences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,
    recon_layer TEXT NOT NULL,
    trade_id TEXT,
    symbol TEXT NOT NULL,
    drift_type TEXT NOT NULL,
    system_value TEXT,
    broker_value TEXT,
    diff TEXT,
    detected_at TEXT NOT NULL,
    schema_version TEXT NOT NULL DEFAULT '1.0'
)
"""


# ──────────────────────────────────────────────────────────────────────────────
# 夹具：tmp 回测产物 + tmp governance 库 + Mock broker
# ──────────────────────────────────────────────────────────────────────────────


def _write_artifact(
    storage: Path,
    trade_log: list[dict],
    equity_curve: list[dict] | None = None,
) -> None:
    storage.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": RUN_ID,
        "strategy_id": "S1",
        "schema_version": "1.0.0",
        "created_at": "2026-08-21 16:00:00",
        "trade_log": trade_log,
        "equity_curve": equity_curve
        if equity_curve is not None
        else [
            {"timestamp": "2026-08-21 09:30:00", "equity": 100000.0},
            {"timestamp": "2026-08-21 15:00:00", "equity": 100000.0},
        ],
    }
    (storage / f"{RUN_ID}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _make_db(db_path: Path) -> None:
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(_PROD_DDL)
        conn.commit()
    finally:
        conn.close()


def _read_rows(db_path: Path) -> list[sqlite3.Row]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute("SELECT * FROM reconciliation_differences ORDER BY id").fetchall()
    finally:
        conn.close()


def _bt_trade(symbol: str, side: str, price: float, qty: int, ts: str, commission: float = 0.85) -> dict:
    return {
        "timestamp": ts,
        "symbol": symbol,
        "side": side,
        "price": price,
        "quantity": qty,
        "commission": commission,
    }


def _sim_fill(symbol: str, price: str, qty: str, traded_id: str, minute: int, commission: str = "0.85") -> Fill:
    return Fill(
        fill_id=f"qmt-{traded_id}",
        fill_price=Decimal(price),
        fill_timestamp=datetime(2026, 8, 21, 2, minute, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"qmt-trade-{traded_id}",
        order_id=f"ord-{traded_id}",
        strategy_id="S1",
        symbol=symbol,
        broker_fill_id=traded_id,
        commission=Decimal(commission),
    )


class MockBroker:
    """实盘侧 mock（ReconBrokerSource 协议）——不连真 QMT。"""

    def __init__(self, fills: list[Fill], holdings: dict[str, str], cash: str = "99000.00") -> None:
        self._fills = fills
        self._holdings = {s: Decimal(q) for s, q in holdings.items()}
        self._cash = Decimal(cash)
        self.trades_query_count = 0
        self.positions_query_count = 0

    def query_trades_today(self, trade_date: str | None = None) -> list[Fill]:
        self.trades_query_count += 1
        return list(self._fills)

    def get_positions(self) -> PositionSnapshot:
        self.positions_query_count += 1
        mv = {s: q * Decimal("10.0") for s, q in self._holdings.items()}
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            idempotency_key="mock-pos-1",
            portfolio_id="mock",
            cash=self._cash,
            holdings=dict(self._holdings),
            market_values=mv,
            total_market_value=sum(mv.values(), Decimal("0")),
        )


@pytest.fixture()
def env(tmp_path: Path):
    """组装对账环境：artifact 目录 + tmp governance 库。"""
    artifact_dir = tmp_path / "artifacts"
    db_path = tmp_path / "governance_test.db"
    _make_db(db_path)
    return {"artifact_dir": artifact_dir, "db_path": db_path}


def _run(env, trade_log, sim_fills, sim_holdings, equity_curve=None) -> ReconDailyResult:
    _write_artifact(env["artifact_dir"], trade_log, equity_curve=equity_curve)
    broker = MockBroker(sim_fills, sim_holdings)
    return run_daily_reconciliation(
        trade_date=TRADE_DATE,
        run_id=RUN_ID,
        broker=broker,
        db_path=env["db_path"],
        storage_path=env["artifact_dir"],
    )


# ──────────────────────────────────────────────────────────────────────────────
# 场景
# ──────────────────────────────────────────────────────────────────────────────


class TestFullMatch:
    def test_all_layers_matched(self, env):
        """两侧完全一致：L1/L2 matched，归因空，零落库，C 类空。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
            sim_fills=[_sim_fill("600000.SH", "10.0", "100", "1001", 30)],
            sim_holdings={"600000.SH": "100"},
        )
        assert result.l1_result.matched is True
        assert result.l2_result.matched is True
        # L3：bt_pnl=0（equity 平），sim_pnl=MV(1000)-净买入(1000)=0 → MATCH
        assert result.l3_result is not None and result.l3_result.status.value == "MATCH"
        assert result.attributions == ()
        assert result.c_class_items == ()
        assert result.rows_written == 0
        assert result.db_error is None
        assert _read_rows(env["db_path"]) == []


class TestAttributionClassification:
    def test_a_slippage(self, env):
        """数量一致、成交价超 0.01 容差 → A 滑点（56号文 §3）。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
            sim_fills=[_sim_fill("600000.SH", "10.05", "100", "1001", 30)],
            sim_holdings={"600000.SH": "100"},
        )
        assert result.l1_result.matched is False
        assert len(result.attributions) == 1
        item = result.attributions[0]
        assert item.category is AttributionClass.A_SLIPPAGE
        assert item.trade_id == "600000.SH|001"
        assert "滑点" in item.detail
        assert result.c_class_items == ()
        rows = _read_rows(env["db_path"])
        assert len(rows) == 1
        assert rows[0]["recon_layer"] == "trade"
        assert rows[0]["drift_type"] == "price_mismatch"
        assert rows[0]["system_value"] == "10.0"
        assert rows[0]["broker_value"] == "10.05"

    def test_b_partial_fill(self, env):
        """实盘数量 < 回测数量 → B 部分成交。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
            sim_fills=[_sim_fill("600000.SH", "10.0", "60", "1001", 30)],
            sim_holdings={"600000.SH": "60"},
        )
        assert len(result.attributions) == 1
        item = result.attributions[0]
        assert item.category is AttributionClass.B_PARTIAL_FILL
        assert item.diff == Decimal("40")
        assert "部分成交" in item.detail
        # 落库：L1 quantity_mismatch + L2 持仓差（回测持仓 100 vs 实盘 60）各 1 行
        rows = _read_rows(env["db_path"])
        assert [r["recon_layer"] for r in rows] == ["trade", "position"]
        assert rows[0]["drift_type"] == "quantity_mismatch"

    def test_c_missing_both_directions(self, env):
        """整笔缺失双向 → C 类当日告警清单（回测有实盘无 + 实盘有回测无）。"""
        result = _run(
            env,
            trade_log=[
                _bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00"),
                _bt_trade("000001.SZ", "buy", 20.0, 100, "2026-08-21 10:35:00"),
            ],
            sim_fills=[
                _sim_fill("600000.SH", "10.0", "100", "1001", 30),
                _sim_fill("000002.SZ", "30.0", "100", "1002", 40),  # 实盘多一笔
            ],
            sim_holdings={"600000.SH": "100", "000002.SZ": "100"},
        )
        assert len(result.c_class_items) == 2
        types = sorted(a.drift_type for a in result.c_class_items)
        assert types == ["missing_in_broker", "missing_in_system"]
        symbols = {a.symbol for a in result.c_class_items}
        assert symbols == {"000001.SZ", "000002.SZ"}
        # to_dict 含 C 类清单（SOP 告警消费）
        d = result.to_dict()
        assert d["attribution_counts"]["C_reject_missing"] == 2
        assert len(d["c_class_items"]) == 2

    def test_fee_diff_reference_only(self, env):
        """佣金差 → 参考列（REFERENCE_FEE），不进 A/B/C，仍落库（56号文 C9）。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00", commission=0.85)],
            sim_fills=[_sim_fill("600000.SH", "10.0", "100", "1001", 30, commission="1.20")],
            sim_holdings={"600000.SH": "100"},
        )
        assert len(result.attributions) == 1
        assert result.attributions[0].category is AttributionClass.REFERENCE_FEE
        assert result.c_class_items == ()
        rows = _read_rows(env["db_path"])
        assert len(rows) == 1
        assert rows[0]["drift_type"] == "commission_mismatch"

    def test_l2_position_drift(self, env):
        """日终持仓不一致 → L2 落库 position 层（零容差，56号文 C7）。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
            sim_fills=[_sim_fill("600000.SH", "10.0", "100", "1001", 30)],
            sim_holdings={},  # 实盘持仓缺失（T+1/同步滞后场景）
            equity_curve=[],  # L3 跳过，隔离本场景只验 L2
        )
        assert result.l1_result.matched is True  # 成交层一致
        assert result.l2_result.matched is False
        assert [d.symbol for d in result.l2_result.drifts] == ["600000.SH"]
        rows = _read_rows(env["db_path"])
        assert len(rows) == 1
        assert rows[0]["recon_layer"] == "position"
        assert rows[0]["drift_type"] == "position_qty_mismatch"
        assert rows[0]["trade_id"] is None
        assert rows[0]["system_value"] == "100"
        assert rows[0]["broker_value"] == "0"


class TestL3Pnl:
    def test_l3_mismatch_written_to_cash_layer(self, env):
        """|gap_pct|>0.001 → MISMATCH → cash 层落库（56号文 C8）。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
            sim_fills=[_sim_fill("600000.SH", "10.0", "100", "1001", 30)],
            sim_holdings={"600000.SH": "100"},
            # bt_pnl=+1000 vs sim_pnl≈0，nav=100000 → gap_pct=0.01 超容差
            equity_curve=[
                {"timestamp": "2026-08-21 09:30:00", "equity": 100000.0},
                {"timestamp": "2026-08-21 15:00:00", "equity": 101000.0},
            ],
        )
        assert result.l3_result is not None
        assert result.l3_result.status.value == "MISMATCH"
        assert abs(result.l3_result.gap_pct - 0.01) < 1e-9
        rows = _read_rows(env["db_path"])
        assert len(rows) == 1
        assert rows[0]["recon_layer"] == "cash"
        assert rows[0]["drift_type"] == "pnl_gap_mismatch"
        assert rows[0]["symbol"] == "__PORTFOLIO__"

    def test_l3_skipped_without_equity_curve(self, env):
        """equity_curve 缺失 → L3 SKIPPED（l3_result=None），不写 cash 层。"""
        result = _run(
            env,
            trade_log=[_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
            sim_fills=[_sim_fill("600000.SH", "10.0", "100", "1001", 30)],
            sim_holdings={"600000.SH": "100"},
            equity_curve=[],
        )
        assert result.l3_result is None
        assert result.to_dict()["l3_status"] == "SKIPPED"
        assert _read_rows(env["db_path"]) == []


class TestDbDegradation:
    def test_db_failure_marks_db_error(self, env, tmp_path: Path):
        """落库失败不丢对账结果：db_error 显性标记 + rows_written=0。"""
        bad_db = tmp_path / "nonexistent_dir" / "x.db"  # 目录不存在 → OperationalError
        _write_artifact(
            env["artifact_dir"],
            [_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
        )
        result = run_daily_reconciliation(
            trade_date=TRADE_DATE,
            run_id=RUN_ID,
            broker=MockBroker([_sim_fill("600000.SH", "10.05", "100", "1001", 30)], {"600000.SH": "100"}),
            db_path=bad_db,
            storage_path=env["artifact_dir"],
        )
        assert result.db_error is not None
        assert result.rows_written == 0
        # 对账结果本身仍有效（A 类归因已产出）
        assert result.attributions[0].category is AttributionClass.A_SLIPPAGE

    def test_default_db_path_is_ssot(self, env, monkeypatch, tmp_path: Path):
        """db_path=None 时走 paths.DB_PATH SSoT（重定向到 tmp 验证，不写真库）。"""
        from zephyr.trading import recon_runner

        redirected = tmp_path / "ssot_redirect.db"
        _make_db(redirected)
        monkeypatch.setattr(recon_runner, "DB_PATH", redirected)
        _write_artifact(
            env["artifact_dir"],
            [_bt_trade("600000.SH", "buy", 10.0, 100, "2026-08-21 10:30:00")],
        )
        result = run_daily_reconciliation(
            trade_date=TRADE_DATE,
            run_id=RUN_ID,
            broker=MockBroker([_sim_fill("600000.SH", "10.05", "100", "1001", 30)], {"600000.SH": "100"}),
            db_path=None,
            storage_path=env["artifact_dir"],
        )
        assert result.db_path == str(redirected)
        assert result.rows_written == 1
        assert len(_read_rows(redirected)) == 1
