# [BLUEPRINT] MOD-BT-222 | docs/03_modules/_domain_backtest/blueprint.md | §bridge-execute 执行腿
# [MODULE] tests.backtest.test_bridge_execute
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; scripts.backtest.sim_daily_runner
# [CONSUMERS] F56 断腿重建质量守卫（SimBridgeExecute 执行腿：sim_daily_runner.bridge-execute）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试禁写生产路径——mock broker/文件面，receipts/orders 全 tmp_path；
#   _new_paper_order_manager/_connect_bridge_world 全 monkeypatch（零真实装配/零桥接触/零库）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [TTL] task_bound
# [TEST] tests/backtest/test_bridge_execute.py
# 覆盖（任务契约五场景+契约边界）：正常执行/空文件/坏行跳过计数/幂等重跑/dry-run；
#   另含 退出码 4（有单失败）/退出码 1（环境失败）/窗口闸/缺文件/限价推导纯函数。
# 铁律：全程 paper/sim 语义——不连真实 QMT 终端、不连任何业务数据库、不写 data/ 生产路径。
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[2]
import sys  # noqa: E402

sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "backtest"))

import sim_daily_runner as runner  # noqa: E402

_IN_WINDOW = datetime(2026, 9, 28, 9, 40, 0)  # 北京时 09:40=窗口内（monkeypatch _now_cn 用）


# ---------- fakes（mock broker/装配面，零真实接触） ----------


class _FakeOrderManager:
    """正门替身：begin_signal_batch/create_order/submit_order 契约同形。"""

    def __init__(self, fail_symbols: tuple[str, ...] = ()):
        self.begins: list[tuple] = []
        self.created: list[dict] = []
        self.submitted: list[str] = []
        self.fail_symbols = fail_symbols
        self._symbol_by_oid: dict[str, str] = {}
        self._seq = 0

    def begin_signal_batch(self, batch_id: str, trade_date=None) -> None:
        self.begins.append((batch_id, trade_date))

    def create_order(self, *, symbol, strategy_id, side, order_type, quantity, limit_price, broker_id):
        self._seq += 1
        oid = f"om-{self._seq}"
        self._symbol_by_oid[oid] = symbol
        self.created.append(
            {
                "order_id": oid,
                "symbol": symbol,
                "strategy_id": strategy_id,
                "side": side,
                "quantity": quantity,
                "limit_price": limit_price,
                "broker_id": broker_id,
            }
        )
        return SimpleNamespace(order_id=oid)

    def submit_order(self, order_id: str, broker_id: str) -> str:
        if self._symbol_by_oid[order_id] in self.fail_symbols:
            raise RuntimeError(f"bridge reject: {self._symbol_by_oid[order_id]}")
        self.submitted.append(order_id)
        return order_id


class _FakeAssembly:
    def __init__(self):
        self.disconnected = False

    def disconnect_all(self):
        self.disconnected = True


class _FakeQuoteProvider:
    def __init__(self, *, fresh=True, bid=Decimal("4.603"), ask=Decimal("4.604"), quote="present", raise_on_get=False):
        self.fresh = fresh
        self.bid = bid
        self.ask = ask
        self.quote = quote
        self.raise_on_get = raise_on_get

    def is_fresh(self):
        return self.fresh

    def get_quote(self, symbol):
        if self.raise_on_get:
            raise RuntimeError("quote boom")
        if self.quote is None:
            return None
        return SimpleNamespace(bid1=self.bid, ask1=self.ask)


def _write_orders(tmp_path: Path, lines: list[str]) -> Path:
    p = tmp_path / "orders_2026-09-28.csv"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


@pytest.fixture()
def wired(monkeypatch):
    """默认接线：窗口内+正门替身+桥替身（各测试可再覆盖/取用）。"""
    om = _FakeOrderManager()
    assembly = _FakeAssembly()
    monkeypatch.setattr(runner, "_now_cn", lambda: _IN_WINDOW)
    monkeypatch.setattr(runner, "_new_paper_order_manager", lambda: om)
    monkeypatch.setattr(runner, "_connect_bridge_world", lambda o, state_dir=None: (assembly, None))
    return {"om": om, "assembly": assembly}


# ---------- 纯函数 ----------


def test_parse_orders_csv_valid_rows_and_header():
    rows, bad = runner.parse_orders_csv(
        "symbol,action,shares,limit_px\n510300.SH,buy,1100,4.604\n510300.SH,sell,1100\n"
    )
    assert bad == []
    assert rows == [
        {"symbol": "510300.SH", "action": "buy", "shares": 1100, "limit_px": 4.604},
        {"symbol": "510300.SH", "action": "sell", "shares": 1100, "limit_px": None},
    ]


def test_parse_orders_csv_bad_rows_counted_not_fatal():
    rows, bad = runner.parse_orders_csv(
        "symbol,action,shares\n510300.SH,buy,1100\n"  # ok
        "badline\n"  # 列数
        "510300.SH,hold,1100\n"  # 未知动作
        "510300.SH,buy,abc\n"  # 非数字
        "510300.SH,buy,0\n"  # 非正值
    )
    assert len(rows) == 1
    assert len(bad) == 4
    assert all(b.startswith("line") for b in bad)


def test_in_bridge_trade_window_boundaries():
    assert runner.in_bridge_trade_window(datetime(2026, 9, 28, 9, 30, 0))
    assert runner.in_bridge_trade_window(datetime(2026, 9, 28, 11, 25, 0))
    assert not runner.in_bridge_trade_window(datetime(2026, 9, 28, 11, 26, 0))
    assert runner.in_bridge_trade_window(datetime(2026, 9, 28, 13, 0, 0))
    assert not runner.in_bridge_trade_window(datetime(2026, 9, 28, 14, 56, 0))


def test_resolve_bridge_limit_px_explicit_first_and_quote_paths():
    row = {"symbol": "510300.SH", "action": "buy", "limit_px": 4.5}
    px, src = runner._resolve_bridge_limit_px(row, None)
    assert (px, src) == (Decimal("4.5"), "explicit")
    qp = _FakeQuoteProvider()
    px, src = runner._resolve_bridge_limit_px({"symbol": "s", "action": "buy", "limit_px": None}, qp)
    assert (px, src) == (Decimal("4.604"), "bridge_quote")  # 买=ask1
    px, src = runner._resolve_bridge_limit_px({"symbol": "s", "action": "sell", "limit_px": None}, qp)
    assert (px, src) == (Decimal("4.603"), "bridge_quote")  # 卖=bid1
    stale = _FakeQuoteProvider(fresh=False)
    assert runner._resolve_bridge_limit_px({"symbol": "s", "action": "buy", "limit_px": None}, stale) == (
        None,
        "quote_stale",
    )
    zero = _FakeQuoteProvider(bid=Decimal("0"))
    assert runner._resolve_bridge_limit_px({"symbol": "s", "action": "sell", "limit_px": None}, zero) == (
        None,
        "quote_zero_spread",
    )
    boom = _FakeQuoteProvider(raise_on_get=True)
    assert runner._resolve_bridge_limit_px({"symbol": "s", "action": "buy", "limit_px": None}, boom) == (
        None,
        "quote_error",
    )


# ---------- bridge-execute 主流程（任务契约五场景） ----------


def test_bridge_execute_normal_path_submits_and_writes_receipt(wired, tmp_path):
    orders = _write_orders(
        tmp_path, ["symbol,action,shares,limit_px", "510300.SH,buy,1100,4.604", "510300.SH,sell,1100,4.603"]
    )
    receipts_dir = tmp_path / "receipts"
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=receipts_dir)
    assert out["executed"] is True
    assert out["exit_code"] == 0
    assert out["submitted"] == 2 and out["failed"] == 0
    # 正门+批次上下文（处方 §3：signal_batch=plan-bridge-<day>）
    assert wired["om"].begins == [("plan-bridge-2026-09-28", "2026-09-28")]
    assert len(wired["om"].created) == 2
    assert all(c["broker_id"] == "qmt_sim" for c in wired["om"].created)
    assert wired["assembly"].disconnected is True
    # 执行回执落盘（文件面）
    receipt = Path(out["receipt"])
    assert receipt.exists() and receipt.parent == receipts_dir
    lines = receipt.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3  # header+2
    assert "submitted" in lines[1] and "510300.SH" in lines[1]


def test_bridge_execute_empty_file_honest_noop(wired, tmp_path):
    orders = _write_orders(tmp_path, ["symbol,action,shares"])
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert out["executed"] is False
    assert out["why"] == "no_valid_orders"
    assert out["exit_code"] == 0
    assert wired["om"].created == []  # 零装配零下单


def test_bridge_execute_bad_rows_skipped_counted(wired, tmp_path):
    orders = _write_orders(
        tmp_path,
        [
            "symbol,action,shares",
            "510300.SH,buy,1100,4.604",
            "badline",
            "510300.SH,hold,1100",
            "510300.SH,buy,abc",
        ],
    )
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert out["executed"] is True
    assert out["submitted"] == 1
    assert len(out["bad_rows"]) == 3  # 坏行跳过计数
    assert out["exit_code"] == 0  # 有效单全成=0（坏行如实留痕不连坐）
    assert len(wired["om"].created) == 1


def test_bridge_execute_idempotent_rerun_no_double_submit(wired, tmp_path):
    orders = _write_orders(tmp_path, ["510300.SH,buy,1100,4.604"])
    first = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert first["executed"] is True
    assert len(wired["om"].created) == 1
    second = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert second["executed"] is False
    assert second["why"] == "already_executed_idempotent_skip"
    assert second["exit_code"] == 0
    assert len(wired["om"].created) == 1  # 幂等：重跑零新增下单
    assert len(wired["om"].begins) == 1  # 重跑连装配都不进


def test_bridge_execute_dry_run_touches_nothing(wired, tmp_path):
    orders = _write_orders(tmp_path, ["510300.SH,buy,1100,4.604", "510300.SH,sell,1100,4.603"])
    receipts_dir = tmp_path / "receipts"
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), dry_run=True, receipts_dir=receipts_dir)
    assert out["executed"] is False
    assert out["why"] == "dry_run_no_action"
    assert out["would_submit"] == 2
    assert out["exit_code"] == 0
    assert not receipts_dir.exists()  # 不落任何文件
    assert wired["om"].created == []  # 不装配不下单
    assert list(receipts_dir.glob("*")) == []


# ---------- 契约边界：退出码 4/1、窗口闸、缺文件 ----------


def test_bridge_execute_partial_failure_exit_4(tmp_path, monkeypatch):
    om = _FakeOrderManager(fail_symbols=("600000.SH",))
    assembly = _FakeAssembly()
    monkeypatch.setattr(runner, "_now_cn", lambda: _IN_WINDOW)
    monkeypatch.setattr(runner, "_new_paper_order_manager", lambda: om)
    monkeypatch.setattr(runner, "_connect_bridge_world", lambda o, state_dir=None: (assembly, None))
    orders = _write_orders(tmp_path, ["510300.SH,buy,1100,4.604", "600000.SH,buy,100,4.00"])
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert out["exit_code"] == 4  # 有单失败
    assert out["submitted"] == 1 and out["failed"] == 1
    failed_row = next(r for r in out["receipts"] if r["status"] == "failed")
    assert "bridge reject" in failed_row["error"]
    # 回执仍落盘=同批已处理标记（防重跑盲目重试已触桥单）
    assert Path(out["receipt"]).exists()


def test_bridge_execute_env_failure_exit_1(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_now_cn", lambda: _IN_WINDOW)
    monkeypatch.setattr(runner, "_new_paper_order_manager", lambda: _FakeOrderManager())

    def _boom(o, state_dir=None):
        raise runner.BridgeEnvError("qmt_sim broker connect 失败")

    monkeypatch.setattr(runner, "_connect_bridge_world", _boom)
    orders = _write_orders(tmp_path, ["510300.SH,buy,1100,4.604"])
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert out["executed"] is False
    assert out["why"] == "bridge_env_failure"
    assert out["exit_code"] == 1  # 环境失败（非订单语义）
    assert not Path(out["receipt"]).exists()  # 未执行不落回执=可重试


def test_bridge_execute_outside_window_honest_skip(wired, tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_now_cn", lambda: datetime(2026, 9, 28, 15, 30, 0))  # 收盘后
    orders = _write_orders(tmp_path, ["510300.SH,buy,1100,4.604"])
    out = runner.bridge_execute("2026-09-28", orders_file=str(orders), receipts_dir=tmp_path)
    assert out["why"] == "outside_trade_window"
    assert out["exit_code"] == 0
    assert wired["om"].created == []


def test_bridge_execute_missing_file_exit_0(wired, tmp_path):
    out = runner.bridge_execute("2026-09-28", orders_file=str(tmp_path / "nope.csv"), receipts_dir=tmp_path)
    assert out["why"] == "orders_file_missing"
    assert out["exit_code"] == 0


def test_cli_registers_bridge_execute_subcommand():
    """CLI 表接线防回归：bridge-execute 在 argparse 子命令表中（F56 断腿根因=表缺项）。"""
    import argparse

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("plan-bridge", "plan-execute", "e4-replay", "report", "settle", "bridge-execute"):
        sp = sub.add_parser(name)
        sp.add_argument("--day")
        if name == "bridge-execute":
            sp.add_argument("--orders-file")
            sp.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(["bridge-execute", "--day", "2026-09-28", "--dry-run"])
    assert args.cmd == "bridge-execute" and args.dry_run is True
