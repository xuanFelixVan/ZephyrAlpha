# [A_test] module_id: MOD-GOV_run_post_settlement | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SCRIPT-run_post_settlement | scripts/run_post_settlement.py | §
# [MODULE] tests.scripts.test_run_post_settlement
# [DOMAIN] D_TRADING
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_run_post_settlement.py — 57 号文 GAP-3 盘后结算 CLI 单测（tmp 隔离，不连真 QMT）。

覆盖：
  1. CLI 参数解析（trade_date 可选位置参数）
  2. resolve_trade_date（显式校验 / 非法格式 / 最近交易日回推）
  3. exit code 矩阵（OK=0 / DRIFT=3 / ERROR=1 / SKIPPED=0，mock reconcile/audit 注入点）
  4. 降级装配（QMT 离线 → reconcile_fn=None + 标注 + 系统侧 reader）
  5. 生产闭包 _build_reconcile_fn（tmp fills_dir + mock broker 真实对账往返）
  6. C 类异常清单打印（MISSING_IN_* → 56 号文 §3 C 类）
  7. audit_fn 包装（DailyAuditor 真空件最小输入跑通）
  8. load_qmt_sim_config（tmp 配置文件解析 / 缺键报错）
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "run_post_settlement",
    _ROOT / "scripts" / "run_post_settlement.py",
)
rps = importlib.util.module_from_spec(_spec)
sys.modules["run_post_settlement"] = rps  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(rps)

from zephyr.ex_core.fill_handler import _fill_to_json_dict  # noqa: E402
from zephyr.shared.contracts.fill import Fill  # noqa: E402
from zephyr.trading.broker_settlement_adapter import fills_to_broker_records  # noqa: E402
from zephyr.trading.settlement_reconciliation import (  # noqa: E402
    DriftType,
    ReconciliationResult,
    SettlementDrift,
)

_TRADE_DATE = "2026-08-21"  # 周五（交易日）


def _make_fill(
    symbol: str = "600000.SH",
    price: str = "10.50",
    qty: str = "100",
    *,
    broker_fill_id: str | None = "600000.SH|001",
    order_id: str = "ord-001",
) -> Fill:
    """构造测试 Fill（fill_timestamp 取本地时区 2026-08-21 10:30，落盘日=20260821）。"""
    return Fill(
        fill_id=f"fill-{symbol}-001",
        order_id=order_id,
        strategy_id="test-strategy",
        symbol=symbol,
        fill_price=Decimal(price),
        filled_quantity=Decimal(qty),
        commission=Decimal("0.01"),
        fill_timestamp=datetime(2026, 8, 21, 10, 30).astimezone(),
        idempotency_key=f"idem-{symbol}-001",
        broker_fill_id=broker_fill_id,
    )


def _write_fills_jsonl(fills_dir: Path, trade_day: str, fills: list[Fill]) -> None:
    """按 fill_handler 落盘口径写 JSONL（{"trade_date":..., "fill":...} 每行一笔）。"""
    fills_dir.mkdir(parents=True, exist_ok=True)
    path = fills_dir / f"{trade_day}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for fill in fills:
            f.write(json.dumps({"trade_date": trade_day, "fill": _fill_to_json_dict(fill)}, ensure_ascii=False) + "\n")


def _deps(**overrides) -> rps.PipelineDeps:
    """构造全 SKIPPED 基准注入件，按字段覆盖。"""
    base = {
        "reconcile_fn": None,
        "audit_fn": None,
        "alert_sink": None,
    }
    base.update(overrides)
    return rps.PipelineDeps(**base)


# ── 1. CLI 参数解析 ──


class TestParseArgs:
    def test_explicit_trade_date(self):
        assert rps.parse_args(["2026-08-21"]).trade_date == "2026-08-21"

    def test_default_trade_date_is_none(self):
        assert rps.parse_args([]).trade_date is None


# ── 2. resolve_trade_date ──


class TestResolveTradeDate:
    def test_explicit_valid(self):
        assert rps.resolve_trade_date("2026-08-21") == "2026-08-21"

    def test_explicit_invalid_format(self):
        with pytest.raises(ValueError, match="格式非法"):
            rps.resolve_trade_date("2026/08/21")

    def test_explicit_compact_digits_rejected(self):
        with pytest.raises(ValueError, match="格式非法"):
            rps.resolve_trade_date("20260821")

    def test_explicit_non_padded_rejected(self):
        # strptime 对零填充宽容会放行 "2026-8-1"——正则口径卡死四位年/两位月日
        with pytest.raises(ValueError, match="格式非法"):
            rps.resolve_trade_date("2026-8-1")

    def test_explicit_non_calendar_day_rejected(self):
        with pytest.raises(ValueError, match="合法日历日"):
            rps.resolve_trade_date("2026-02-30")

    def test_default_lookback_from_sunday(self):
        # 2026-08-23 周日回推 → 2026-08-21 周五（is_trading_day 真实件，双口径均为交易日）
        assert rps.resolve_trade_date(None, today=date(2026, 8, 23)) == "2026-08-21"

    def test_default_today_is_trading_day(self):
        # 回推含今天：周五当天 → 当天（盘后语义）
        assert rps.resolve_trade_date(None, today=date(2026, 8, 21)) == "2026-08-21"


# ── 3. exit code 矩阵（mock 注入点）──


class TestExitCodeMatrix:
    def test_ok_exit_0(self, capsys):
        deps = _deps(reconcile_fn=lambda td: SimpleNamespace(matched=True, drifts=()))
        assert rps.main([_TRADE_DATE], deps=deps) == 0
        out = capsys.readouterr().out
        assert "reconcile_status: OK" in out
        assert "trade_date:" in out and _TRADE_DATE in out

    def test_drift_exit_3(self, capsys):
        drift = SettlementDrift(
            trade_id="600000.SH|001",
            symbol="600000.SH",
            drift_type=DriftType.PRICE_MISMATCH,
            system_value=Decimal("10.50"),
            broker_value=Decimal("10.60"),
            diff=Decimal("-0.10"),
        )
        deps = _deps(reconcile_fn=lambda td: SimpleNamespace(matched=False, drifts=(drift,)))
        assert rps.main([_TRADE_DATE], deps=deps) == 3
        assert "reconcile_status: DRIFT" in capsys.readouterr().out

    def test_reconcile_error_exit_1(self, capsys):
        def _boom(td: str):
            raise RuntimeError("券商侧查询超时")

        deps = _deps(reconcile_fn=_boom)
        assert rps.main([_TRADE_DATE], deps=deps) == 1
        out = capsys.readouterr().out
        assert "reconcile_status: ERROR" in out
        assert "券商侧查询超时" in out  # errors 清单原样打印

    def test_audit_error_exit_1(self, capsys):
        def _boom(td: str):
            raise RuntimeError("审计输入异常")

        deps = _deps(
            reconcile_fn=lambda td: SimpleNamespace(matched=True, drifts=()),
            audit_fn=_boom,
        )
        assert rps.main([_TRADE_DATE], deps=deps) == 1
        out = capsys.readouterr().out
        assert "audit_status:" in out and "ERROR" in out
        assert "审计输入异常" in out

    def test_all_skipped_exit_0(self, capsys):
        assert rps.main([_TRADE_DATE], deps=_deps()) == 0
        out = capsys.readouterr().out
        assert "reconcile_status: SKIPPED" in out
        assert "audit_status:" in out and "SKIPPED" in out

    def test_invalid_trade_date_exit_1(self, capsys):
        assert rps.main(["2026/08/21"], deps=_deps()) == 1
        assert "格式非法" in capsys.readouterr().out

    def test_alert_sink_invoked_on_drift(self):
        alerts: list[tuple[str, str]] = []
        deps = _deps(
            reconcile_fn=lambda td: SimpleNamespace(matched=False, drifts=(object(),)),
            alert_sink=lambda td, msg: alerts.append((td, msg)),
        )
        assert rps.main([_TRADE_DATE], deps=deps) == 3
        assert len(alerts) == 1 and alerts[0][0] == _TRADE_DATE


# ── 4. 降级装配（QMT 离线）──


class TestDegradedAssembly:
    def test_degraded_when_qmt_offline(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(rps, "_try_connect_sim_broker", lambda: (None, "XtMiniQmt 未在线"))
        monkeypatch.setattr(rps, "_DEFAULT_FILLS_DIR", tmp_path / "fills")
        deps, broker = rps.build_production_deps()
        assert broker is None
        assert deps.reconcile_fn is None  # 降级=SKIPPED 而非假比对
        assert deps.system_fills_reader is not None
        assert any("降级为仅系统侧+标注" in n for n in deps.notes)
        # 端到端：降级路径 exit 0（SKIPPED）+ 标注打印
        assert rps.main([_TRADE_DATE], deps=deps) == 0
        out = capsys.readouterr().out
        assert "降级" in out
        assert "系统侧当日 Fill: 0 笔" in out

    def test_degraded_system_fills_count(self, monkeypatch, tmp_path, capsys):
        monkeypatch.setattr(rps, "_DEFAULT_FILLS_DIR", tmp_path / "fills")
        deps = _deps(system_fills_reader=rps.FillHandler(fills_dir=tmp_path / "fills").query_fills_by_date)
        _write_fills_jsonl(tmp_path / "fills", "20260821", [_make_fill()])
        assert rps.main([_TRADE_DATE], deps=deps) == 0
        assert "系统侧当日 Fill: 1 笔" in capsys.readouterr().out


# ── 5. 生产闭包 _build_reconcile_fn（tmp 隔离 + mock broker）──


class TestBuildReconcileFn:
    def test_matched_roundtrip(self, tmp_path):
        """系统侧 JSONL 一笔 + mock 券商侧同一笔 → matched=True，结果入 holder。"""
        system_fill = _make_fill()
        _write_fills_jsonl(tmp_path / "fills", "20260821", [system_fill])
        # mock 券商：返回同一笔成交（业务配对键口径由适配器生成 symbol|001）
        broker = SimpleNamespace(query_trades_today=lambda td=None: [_make_fill(order_id="qmt-ord-1")])
        deps = _deps()
        reconcile = rps._build_reconcile_fn(broker, deps, fills_dir=tmp_path / "fills")
        result = reconcile(_TRADE_DATE)
        assert isinstance(result, ReconciliationResult)
        assert result.matched is True
        assert result.total_system_trades == 1
        assert result.total_broker_trades == 1
        assert len(deps.reconcile_results) == 1

    def test_missing_in_broker_drift(self, tmp_path):
        """券商侧空 → 系统侧整笔 MISSING_IN_BROKER（C 类）→ matched=False。"""
        _write_fills_jsonl(tmp_path / "fills", "20260821", [_make_fill()])
        broker = SimpleNamespace(query_trades_today=lambda td=None: [])
        deps = _deps()
        reconcile = rps._build_reconcile_fn(broker, deps, fills_dir=tmp_path / "fills")
        result = reconcile(_TRADE_DATE)
        assert result.matched is False
        assert result.drifts[0].drift_type is DriftType.MISSING_IN_BROKER

    def test_no_fills_file_matched_empty(self, tmp_path):
        """当日 JSONL 不存在 → 空对账 matched=True（57 号文彩排口径）。"""
        broker = SimpleNamespace(query_trades_today=lambda td=None: [])
        deps = _deps()
        reconcile = rps._build_reconcile_fn(broker, deps, fills_dir=tmp_path / "fills")
        assert reconcile(_TRADE_DATE).matched is True


# ── 6. C 类异常清单打印 ──


class TestCClassDriftPrint:
    def test_c_class_listed(self, capsys):
        c_drift = SettlementDrift(
            trade_id="600000.SH|001",
            symbol="600000.SH",
            drift_type=DriftType.MISSING_IN_BROKER,
            system_value=Decimal("10.50"),
            broker_value=None,
            diff=None,
        )
        a_drift = SettlementDrift(
            trade_id="000001.SZ|001",
            symbol="000001.SZ",
            drift_type=DriftType.PRICE_MISMATCH,
            system_value=Decimal("9.00"),
            broker_value=Decimal("9.01"),
            diff=Decimal("-0.01"),
        )
        now = datetime(2026, 8, 21, 15, 40).astimezone()
        result = ReconciliationResult(
            timestamp=now,
            settlement_date=_TRADE_DATE,
            matched=False,
            drifts=(c_drift, a_drift),
            total_system_trades=2,
            total_broker_trades=1,
            matched_trades=0,
        )
        deps = _deps(reconcile_results=[result])
        rps._print_c_class_drifts(deps)
        out = capsys.readouterr().out
        assert "C 类异常清单" in out
        assert "missing_in_broker" in out
        assert "600000.SH|001" in out
        # A 类（价格差）不进 C 类清单
        assert "000001.SZ|001" not in out

    def test_no_c_class_no_print(self, capsys):
        rps._print_c_class_drifts(_deps())
        assert "C 类" not in capsys.readouterr().out


# ── 7. audit_fn 包装（真 DailyAuditor，最小输入）──


class TestAuditFnWrapper:
    def test_audit_wrapper_real_auditor(self):
        report = rps._build_audit_fn()(_TRADE_DATE)
        assert report.portfolio_id == "miniqmt-sim"
        assert report.trading_date == date(2026, 8, 21)
        # 空快照最小输入：PnL 对账 MATCH、整体非 FAIL（五件套链路跑通）
        assert report.pnl_reconciliation.total_pnl == 0.0
        assert report.overall_status.value in {"PASS", "PASS_WITH_WARNINGS"}


# ── 8. load_qmt_sim_config ──


class TestLoadQmtSimConfig:
    def test_parse_sim_keys(self, tmp_path):
        # 真实 config/.env.qmt 口径：路径值含字面双反斜杠，loader 原样透传不规范化
        env = tmp_path / ".env.qmt"
        env.write_text(
            "# 注释行\nQMT_SIM_PATH=E:\\\\qmt\\\\userdata_mini\nQMT_SIM_ACCOUNT=8886156677\nQMT_REAL_ACCOUNT=999\n",
            encoding="utf-8",
        )
        path, account = rps.load_qmt_sim_config(env)
        assert path == "E:\\\\qmt\\\\userdata_mini"
        assert account == "8886156677"

    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            rps.load_qmt_sim_config(tmp_path / "nope.env")

    def test_missing_keys(self, tmp_path):
        env = tmp_path / ".env.qmt"
        env.write_text("QMT_SIM_PATH=E:\\\\qmt\n", encoding="utf-8")
        with pytest.raises(ValueError, match="QMT_SIM"):
            rps.load_qmt_sim_config(env)
