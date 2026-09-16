# [A_test] module_id: MOD-GOV_start_paper_session | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SCRIPT-start_paper_session | scripts/start_paper_session.py | §
# [MODULE] tests.scripts.test_start_paper_session
# [DOMAIN] D_EX_CORE
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_start_paper_session.py — 57 号文 GAP-2 模拟盘交易日启动脚本单测（mock broker/session，不连真 QMT）。

覆盖：
  1. CLI 参数解析（默认值/--strategy/--dry-run/--universe/--close-time）
  2. 参数装配（默认纯保活 interval=0 空 universe；--strategy 模式 universe/interval/constraints）
  3. 收盘自动停（假钟越过 15:05 → 有界循环退出 → stop）
  4. KeyboardInterrupt 优雅停（sleeper 注入中断 → stop 仍调用）
  5. --dry-run 只连不下单（session_factory 永不被调用）
  6. 参数非法 exit 2 / 连接失败 exit 1
  7. 启动前检查项打印（C1 PASS/FAIL/SKIP 三态 + mock 信号告警）
  8. load_qmt_sim_config（tmp 配置文件解析）
  9. --service 常驻服务模式（GAP-2 残余①：assemble_session 包 slot 交 LiveStrategyAdapter）
  10. H5-P0 风控层接线（回撤基线取券商净值 / EMERGENCY→熔断落盘 / 启动恢复 Fail-Closed /
      成交→本地账→对账冻结链 / 净值不可读拒装配 exit 1）
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from datetime import time as dtime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "start_paper_session",
    _ROOT / "scripts" / "start_paper_session.py",
)
sps = importlib.util.module_from_spec(_spec)
sys.modules["start_paper_session"] = sps  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(sps)


def _sh(hour: int, minute: int, second: int = 0) -> datetime:
    """2026-08-21（交易日）北京时区时刻。"""
    return datetime(2026, 8, 21, hour, minute, second, tzinfo=sps._SHANGHAI_TZ)


class _FakeClock:
    """假钟：sleeper 推进，避免测试真睡。"""

    def __init__(self, start: datetime) -> None:
        self.t = start

    def __call__(self) -> datetime:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += timedelta(seconds=seconds)


class _MockBroker:
    """记录型 mock broker（不连真 QMT）。"""

    def __init__(self, connect_ok: bool = True) -> None:
        self.connect_ok = connect_ok
        self.connected = False
        self.disconnected = False
        self.positions_queried = False

    def connect(self) -> bool:
        self.connected = True
        return self.connect_ok

    def disconnect(self) -> None:
        self.disconnected = True

    def register_fill_callback(self, callback) -> None:
        """OrderManager.register_broker 契约件——记录不回溯。"""
        self.fill_callback = callback

    def get_positions(self):
        self.positions_queried = True
        return SimpleNamespace(cash=Decimal("10000000"), total_market_value=Decimal("0"), holdings={})


class _MockSession:
    """记录型 mock TradingSession。"""

    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def get_session_report(self) -> dict:
        """adapter 监督/心跳契约件（running 供意外停止检测）。"""
        return {"running": self.started and not self.stopped}


# ── 1. CLI 参数解析 ──


class TestParseArgs:
    def test_defaults(self):
        args = sps.parse_args([])
        assert args.strategy == ""
        assert args.dry_run is False
        assert args.universe == ""
        # --interval 已删除（B4 治本 2026-09-05：Timer 周期调仓退役）
        assert not hasattr(args, "interval")
        assert args.close_time == "15:05"
        assert args.poll == 30
        assert args.max_single == pytest.approx(0.01)

    def test_strategy_and_universe(self):
        args = sps.parse_args(["--strategy", "topn-momentum", "--universe", "600000.SH, 000001.SZ", "--dry-run"])
        assert args.strategy == "topn-momentum"
        assert args.dry_run is True
        assert sps._parse_universe(args.universe) == ["600000.SH", "000001.SZ"]


# ── 2. 参数装配（mock broker + 真 assemble_session）──


class TestAssembleSession:
    def test_default_keepalive_safe(self, tmp_path):
        """默认=纯保活安全态：空 universe + 无定时器字段 + 策略恒空权重。"""
        args = sps.parse_args([])
        session = sps.assemble_session(args, _MockBroker(), state_dir=tmp_path)
        assert session._config.universe == []
        # B4 治本：rebalance_interval_seconds 字段已删除（无时间触发）
        assert not hasattr(session._config, "rebalance_interval_seconds")
        assert session._config.strategy_id == "paper-keepalive"
        assert session._strategy.generate_target_weights([], {}, {}) == {}
        # H5-P0 接线闸：风控层不得再是 None（None=回撤/VaR/熔断/对账四链全盲）
        assert isinstance(session._risk_layer, sps.RiskLayerOrchestrator)

    def test_strategy_mode_wiring(self, tmp_path):
        args = sps.parse_args(
            [
                "--strategy",
                "topn-momentum",
                "--universe",
                "600000.SH,000001.SZ",
                "--max-single",
                "0.02",
            ]
        )
        session = sps.assemble_session(args, _MockBroker(), state_dir=tmp_path)
        assert session._config.universe == ["600000.SH", "000001.SZ"]
        assert not hasattr(session._config, "rebalance_interval_seconds")
        assert session._config.strategy_id == "topn-momentum"
        assert session._config.strategy_constraints == {"top_n": 2, "max_single": 0.02}
        assert session._config.risk_limits.max_single_position == pytest.approx(0.02)
        # mock 信号彩排口径：全 1.0 等强
        assert session._signal_provider(["600000.SH", "000001.SZ"]) == {"600000.SH": 1.0, "000001.SZ": 1.0}
        assert isinstance(session._risk_layer, sps.RiskLayerOrchestrator)

    def test_unknown_strategy_rejected(self, tmp_path):
        args = sps.parse_args(["--strategy", "foo", "--universe", "600000.SH"])
        with pytest.raises(ValueError, match="未知策略"):
            sps.assemble_session(args, _MockBroker(), state_dir=tmp_path)


# ── 3/4/5. 保活循环三态（收盘自动停 / Ctrl+C 优雅停 / dry-run 不下单）──


class TestKeepAliveLoop:
    def test_auto_stop_at_close(self, capsys):
        """有界循环：假钟越过收盘时点 → 自动 stop（撤未成交单语义在 session.stop 内）。"""
        clock = _FakeClock(_sh(15, 4))
        broker = _MockBroker()
        session = _MockSession()

        def _sleeper(seconds: float) -> None:
            clock.advance(120.0)  # 一觉睡过 15:05

        code = sps.main(
            [],
            broker_factory=lambda: broker,
            session_factory=lambda a, b: session,
            sleeper=_sleeper,
            now_fn=clock,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert session.started and session.stopped
        assert broker.disconnected is False  # 正常收场不断连（broker 生命周期归调用方/QMT 常开口径）
        out = capsys.readouterr().out
        assert "收盘自动停止" in out
        assert "[C1] QMT 进程: PASS" in out

    def test_keyboard_interrupt_graceful_stop(self, capsys):
        """Ctrl+C → KeyboardInterrupt → 优雅 stop 仍执行。"""
        clock = _FakeClock(_sh(10, 0))
        session = _MockSession()

        def _sleeper(seconds: float) -> None:
            raise KeyboardInterrupt

        code = sps.main(
            [],
            broker_factory=lambda: _MockBroker(),
            session_factory=lambda a, b: session,
            sleeper=_sleeper,
            now_fn=clock,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert session.started and session.stopped
        out = capsys.readouterr().out
        assert "KeyboardInterrupt" in out
        assert "人工中断" in out

    def test_start_after_close_stops_immediately(self, capsys):
        """收盘后拉起：有界循环零迭代 → 立即 stop 退出（语义保留不挂死）。"""
        clock = _FakeClock(_sh(16, 0))
        session = _MockSession()
        code = sps.main(
            [],
            broker_factory=lambda: _MockBroker(),
            session_factory=lambda a, b: session,
            sleeper=lambda s: None,
            now_fn=clock,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert session.started and session.stopped
        assert "已过保活截止时点" in capsys.readouterr().out

    def test_dry_run_connects_but_never_orders(self, capsys):
        """--dry-run：只连+探活+断连；session_factory 被调用即失败（绝不下单路径）。"""
        broker = _MockBroker()

        def _forbidden_session_factory(args, b):
            raise AssertionError("dry-run 不得装配/启动会话（只连不打任何单）")

        code = sps.main(
            ["--dry-run"],
            broker_factory=lambda: broker,
            session_factory=_forbidden_session_factory,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert broker.connected and broker.positions_queried and broker.disconnected
        out = capsys.readouterr().out
        assert "[DRY-RUN] 连接探活 OK（未打任何单）" in out
        assert "cash=10000000" in out


# ── 6. 参数非法 / 连接失败 exit code ──


class TestExitCodes:
    def test_strategy_without_universe_exit_2(self, capsys):
        code = sps.main(["--strategy", "topn-momentum"], qmt_probe=lambda: True)
        assert code == 2
        assert "--universe" in capsys.readouterr().out

    def test_bad_close_time_exit_2(self, capsys):
        code = sps.main(["--close-time", "25:99"], qmt_probe=lambda: True)
        assert code == 2
        assert "--close-time" in capsys.readouterr().out

    def test_connect_false_exit_1(self, capsys):
        code = sps.main([], broker_factory=lambda: _MockBroker(connect_ok=False), qmt_probe=lambda: True)
        assert code == 1
        assert "connect() 返回 False" in capsys.readouterr().out

    def test_connect_raises_exit_1(self, capsys):
        def _boom():
            raise RuntimeError("xtquant 未安装")

        code = sps.main([], broker_factory=_boom, qmt_probe=lambda: True)
        assert code == 1
        assert "xtquant 未安装" in capsys.readouterr().out


# ── 7. 启动前检查项打印（C1 三态 + mock 信号告警）──


class TestPrestartChecks:
    def test_c1_fail_wording(self, capsys):
        sps.print_prestart_checks(False)
        out = capsys.readouterr().out
        assert "[C1] QMT 进程: FAIL" in out
        assert "当日模拟盘应 SKIP" in out
        assert "[C2]" in out and "[C3]" in out  # 三命令口径齐全

    def test_c1_skip_wording(self, capsys):
        sps.print_prestart_checks(None)
        assert "[C1] QMT 进程: SKIP" in capsys.readouterr().out

    def test_strategy_mock_signal_warning(self, capsys):
        """--strategy 显式开启 → mock 信号大字告警（LiveStrategyAdapter 未施工标注）。"""
        broker = _MockBroker()
        code = sps.main(
            ["--strategy", "topn-momentum", "--universe", "600000.SH", "--dry-run"],
            broker_factory=lambda: broker,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert "mock 信号" in capsys.readouterr().out


# ── 8. load_qmt_sim_config ──


class TestLoadQmtSimConfig:
    def test_parse_sim_keys(self, tmp_path):
        env = tmp_path / ".env.qmt"
        env.write_text(
            "# 注释\nQMT_SIM_PATH=E:\\\\qmt\\\\userdata_mini\nQMT_SIM_ACCOUNT=8886156677\n",
            encoding="utf-8",
        )
        path, account = sps.load_qmt_sim_config(env)
        assert path == "E:\\\\qmt\\\\userdata_mini"  # 字面双反斜杠原样透传（真实 .env.qmt 口径）
        assert account == "8886156677"

    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            sps.load_qmt_sim_config(tmp_path / "nope.env")


# ── 9. --service 常驻服务模式（57 号文 GAP-2 残余①：assemble_session 包 slot 交 adapter）──


class _MockAdapter:
    """记录型 mock LiveStrategyAdapter。"""

    def __init__(self, run_code: int = 0) -> None:
        self.started = False
        self.run_called = False
        self.run_close_at = None
        self.run_code = run_code

    def start(self) -> None:
        self.started = True

    def run(self, close_at=None, *, stop_event=None) -> int:
        self.run_called = True
        self.run_close_at = close_at
        return self.run_code


class TestServiceMode:
    def test_parse_service_flag_default_off(self):
        assert sps.parse_args([]).service is False
        assert sps.parse_args(["--service"]).service is True

    def test_service_mode_routes_to_adapter(self, capsys):
        """--service：adapter.start→run(close_at) 收场 exit 0；main 不直接装配/启动 session。"""
        broker = _MockBroker()
        adapter = _MockAdapter()

        def _forbidden_session_factory(a, b):
            raise AssertionError("--service 模式 main 不直接装配 session（归 adapter slot 工厂）")

        code = sps.main(
            ["--service"],
            broker_factory=lambda: broker,
            session_factory=_forbidden_session_factory,
            adapter_factory=lambda a, b: adapter,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert adapter.started and adapter.run_called
        assert adapter.run_close_at == dtime(15, 5)
        assert "常驻服务" in capsys.readouterr().out

    def test_service_mode_close_time_passthrough(self):
        """--close-time 透传 adapter.run(close_at)。"""
        adapter = _MockAdapter()
        code = sps.main(
            ["--service", "--close-time", "14:55"],
            broker_factory=lambda: _MockBroker(),
            adapter_factory=lambda a, b: adapter,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert adapter.run_close_at == dtime(14, 55)

    def test_service_mode_assembly_failure_exit_1(self, capsys):
        """常驻服务装配失败 → broker 断连 + exit 1（与过渡形态装配失败同口径）。"""
        broker = _MockBroker()

        def _boom(a, b):
            raise RuntimeError("slots 不能为空")

        code = sps.main(
            ["--service"],
            broker_factory=lambda: broker,
            adapter_factory=_boom,
            qmt_probe=lambda: True,
        )
        assert code == 1
        assert broker.disconnected is True
        assert "常驻服务装配失败" in capsys.readouterr().out

    def test_service_mode_dry_run_precedence(self):
        """--service --dry-run：dry-run 优先（只连不打单），adapter 永不装配。"""
        broker = _MockBroker()

        def _forbidden_adapter_factory(a, b):
            raise AssertionError("dry-run 不得装配常驻服务（只连不打任何单）")

        code = sps.main(
            ["--service", "--dry-run"],
            broker_factory=lambda: broker,
            adapter_factory=_forbidden_adapter_factory,
            qmt_probe=lambda: True,
        )
        assert code == 0
        assert broker.connected and broker.positions_queried and broker.disconnected

    def test_service_mode_real_adapter_bounded_run(self, tmp_path):
        """真 adapter 链路：假钟越过收盘 → run 有界收场（session start/stop 各一次）→ exit 0。"""
        clock = _FakeClock(_sh(15, 4))
        session = _MockSession()
        hb = tmp_path / "live_strategy_biz.heartbeat"

        def _sleeper(seconds: float) -> None:
            clock.advance(120.0)  # 一觉睡过 15:05

        code = sps.main(
            ["--service"],
            broker_factory=lambda: _MockBroker(),
            session_factory=lambda a, b: session,
            sleeper=_sleeper,
            now_fn=clock,
            qmt_probe=lambda: True,
            adapter_kwargs={"heartbeat_path": hb},
        )
        assert code == 0
        assert session.started and session.stopped
        payload = json.loads(hb.read_text(encoding="utf-8"))
        assert payload["service"] == "live_strategy_adapter"
        assert payload["running"] is False  # 收场后最终心跳
        assert payload["slots"][0]["state"] == "STOPPED"


class TestAssembleAdapter:
    def test_wraps_session_factory_as_slot(self, tmp_path):
        """assemble_session 包 slot：真 adapter start→session started；biz 心跳 JSON 落盘含 slot。"""
        args = sps.parse_args([])
        sessions: list = []

        def _factory(a, b):
            s = _MockSession()
            sessions.append(s)
            return s

        hb = tmp_path / "live_strategy_biz.heartbeat"
        adapter = sps.assemble_adapter(
            args,
            _MockBroker(),
            session_factory=_factory,
            heartbeat_path=hb,
            now_fn=lambda: _sh(9, 25),
            sleeper=lambda s: None,
        )
        adapter.start()
        assert len(sessions) == 1 and sessions[0].started
        payload = json.loads(hb.read_text(encoding="utf-8"))
        assert payload["service"] == "live_strategy_adapter"
        assert payload["running"] is True
        assert payload["slots"][0]["slot_id"] == "paper-keepalive"
        adapter.stop()
        assert sessions[0].stopped

    def test_slot_factory_recreates_session_on_call(self, tmp_path):
        """slot 工厂=assemble_session 口径：每次调用重造新会话实例（崩溃重启不携残留态）。"""
        args = sps.parse_args(["--strategy", "topn-momentum", "--universe", "600000.SH"])
        adapter = sps.assemble_adapter(
            args,
            _MockBroker(),
            state_dir=tmp_path,
            heartbeat_path=tmp_path / "biz.heartbeat",
            now_fn=lambda: _sh(9, 25),
            sleeper=lambda s: None,
        )
        factory = adapter._runtimes[0].slot.session_factory
        assert factory() is not factory()
        assert adapter._runtimes[0].slot.slot_id == "paper-topn-momentum"


# ── 10. H5-P0 风控层接线（仓位上限/熔断/对账/启动恢复四链不得再是 None）──


class _RiskBroker:
    """带账户持仓 + 当日成交探针的 mock broker（风控四链端到端替身，不连真 QMT）。"""

    def __init__(self, cash: str = "10000000", holdings: dict[str, str] | None = None, *, fail_positions: bool = False):
        self._cash = Decimal(cash)
        self.holdings = {k: Decimal(v) for k, v in (holdings or {}).items()}
        self.fail_positions = fail_positions
        self.disconnected = False
        self.submitted: list = []

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        self.disconnected = True

    def register_fill_callback(self, callback) -> None:
        self.fill_callbacks = getattr(self, "fill_callbacks", [])
        self.fill_callbacks.append(callback)

    def push_fill(self, fill) -> None:
        for callback in getattr(self, "fill_callbacks", []):
            callback(fill)

    def submit_order(self, order) -> str:
        self.submitted.append(order)
        return f"brk-{len(self.submitted)}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return True

    def get_positions(self):
        if self.fail_positions:
            raise RuntimeError("XtMiniQmt 终端掉线")
        market_value = sum((q * Decimal("10") for q in self.holdings.values()), Decimal("0"))
        return SimpleNamespace(
            cash=self._cash,
            total_market_value=market_value,
            market_values={k: v * Decimal("10") for k, v in self.holdings.items()},
            holdings=dict(self.holdings),
        )

    def query_trades_today(self, trade_date: str | None = None) -> list:
        """真实 broker 的当日成交探针名（RiskLayerConfig 出厂默认 get_today_fills 系幻影）。"""
        return []


def _fill(order_id: str, *, fill_id: str = "f1", symbol: str = "600000.SH", qty: str = "100") -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=Decimal("10"),
        fill_timestamp=datetime(2026, 8, 21, 10, 0, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"ik-{fill_id}",
        order_id=order_id,
        strategy_id="paper-keepalive",
        symbol=symbol,
    )


def _order(om, symbol: str = "600000.SH", qty: str = "100"):
    order = om.create_order(
        symbol=symbol,
        strategy_id="paper-keepalive",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
    )
    order.broker_order_id = f"brk-{order.order_id[:6]}"
    return order


class TestRiskLayerBaseline:
    def test_drawdown_baseline_comes_from_broker_not_constant(self, tmp_path):
        """基线=券商实时净值：10M 起跌到 9M 应是 CRITICAL（-10%）。

        若装配处用兜底常量（1M）当基线，9M 只是"新高"→ 级别 NONE=回撤链永不觉醒。
        """
        session = sps.assemble_session(sps.parse_args([]), _RiskBroker(cash="10000000"), state_dir=tmp_path)
        snap = session._risk_layer.evaluate_intraday(9_000_000.0)
        assert snap.drawdown_level.name == "CRITICAL"
        assert snap.drawdown_pct == pytest.approx(-0.10)

    def test_emergency_drawdown_engages_kill_switch_and_persists(self, tmp_path):
        """回撤 EMERGENCY → 单一仲裁点熔断 + Crash-only 落盘（重启存活，Qwen P0-3①）。"""
        session = sps.assemble_session(sps.parse_args([]), _RiskBroker(cash="10000000"), state_dir=tmp_path)
        session._risk_layer.evaluate_intraday(7_900_000.0)  # -21% < -15%
        assert session._risk_layer.kill_switch_engaged is True
        assert session._risk_layer.is_trading_allowed is False
        record = json.loads((tmp_path / "kill_switch.json").read_text(encoding="utf-8"))
        assert record["active"] is True

    def test_fail_closed_until_startup_recovery_done(self, tmp_path):
        """装配完成≠可下单：recover_from_broker 之前恒禁单（空仓错觉防重复建仓）。"""
        session = sps.assemble_session(sps.parse_args([]), _RiskBroker(), state_dir=tmp_path)
        assert session._risk_layer.is_trading_allowed is False
        recovery = session._risk_layer.recover_from_broker()
        assert recovery.success is True
        assert session._risk_layer.is_trading_allowed is True

    def test_today_fills_probe_names_a_method_the_broker_has(self, tmp_path):
        """探针名必须落在 broker 真件上——出厂默认 get_today_fills 全仓零实现=幻影。"""
        broker = _RiskBroker()
        session = sps.assemble_session(sps.parse_args([]), broker, state_dir=tmp_path)
        probe = session._risk_layer._config.today_fills_probe
        assert probe != "get_today_fills"
        assert callable(getattr(broker, probe))


class TestRiskLayerReconcileChain:
    def test_fill_feeds_local_book_then_reconcile_matches(self, tmp_path):
        """券商推送成交（order_id=券商订单号）→ 本地账 → 对账一致=不冻结。"""
        broker = _RiskBroker(holdings={"600000.SH": "100"})
        session = sps.assemble_session(sps.parse_args([]), broker, state_dir=tmp_path)
        om = session._order_manager
        order = _order(om)
        om._on_fill(_fill(order.broker_order_id))
        assert session._risk_layer.run_reconcile_once() is True
        assert session._risk_layer.is_symbol_frozen("600000.SH") is False

    def test_fill_by_local_uuid_also_pairs(self, tmp_path):
        """本地 UUID 直配路径同权（OrderManager 以本地 order_id 为键）。"""
        broker = _RiskBroker(holdings={"600000.SH": "100"})
        session = sps.assemble_session(sps.parse_args([]), broker, state_dir=tmp_path)
        om = session._order_manager
        order = _order(om)
        om._on_fill(_fill(order.order_id))
        assert session._risk_layer.run_reconcile_once() is True

    def test_unpaired_fill_and_foreign_position_freeze_symbol(self, tmp_path):
        """券商多出的持仓（本地账未入账）=漂移 → 冻结该标的（下单前硬拦消费口）。"""
        broker = _RiskBroker(holdings={"600000.SH": "100"})
        session = sps.assemble_session(sps.parse_args([]), broker, state_dir=tmp_path)
        om = session._order_manager
        om._on_fill(_fill("brk-unknown-order"))  # 配不上单：只告警不入账
        assert session._risk_layer.run_reconcile_once() is False
        assert session._risk_layer.is_symbol_frozen("600000.SH") is True

    def test_dedup_store_is_per_assembly_not_shared(self, tmp_path):
        """两次装配各持一份去重集——共用文件会被死回调抢先登记 fill_id 致漏入账。"""
        first = sps.assemble_session(sps.parse_args([]), _RiskBroker(), state_dir=tmp_path)
        second = sps.assemble_session(sps.parse_args([]), _RiskBroker(), state_dir=tmp_path)
        for session in (first, second):
            order = _order(session._order_manager)
            session._order_manager._on_fill(_fill(order.order_id))
        files = sorted(p.name for p in tmp_path.glob("paper_fill_ids-*"))
        assert len(files) == 2
        assert all(f.endswith(".txt") for f in files)


class TestRiskLayerFailFast:
    def test_unreadable_account_rejects_assembly(self, tmp_path):
        """账户快照读不到 → 拒装配：绝不带着猜出来的基线开盘。"""
        with pytest.raises(ValueError, match="风控基线"):
            sps.assemble_session(sps.parse_args([]), _RiskBroker(fail_positions=True), state_dir=tmp_path)

    def test_non_positive_nav_rejects_assembly(self, tmp_path):
        with pytest.raises(ValueError, match="净值非法"):
            sps.assemble_session(sps.parse_args([]), _RiskBroker(cash="0"), state_dir=tmp_path)

    def test_cli_exits_1_when_risk_layer_cannot_assemble(self, tmp_path, monkeypatch, capsys):
        """CLI 边界：装配失败=exit 1 + broker 断连（不留"无风控层裸跑"的中间态）。"""
        monkeypatch.setattr(sps, "_RISK_STATE_DIR", tmp_path)  # main 不透传 state_dir，改生产根目录指 tmp
        broker = _RiskBroker(fail_positions=True)
        code = sps.main(
            [],
            broker_factory=lambda: broker,
            qmt_probe=lambda: True,
            now_fn=lambda: _sh(9, 30),
        )
        assert code == 1
        assert "会话装配失败" in capsys.readouterr().out
        assert broker.disconnected is True

    def test_startup_discloses_wired_and_unwired_chains(self, tmp_path, capsys):
        """产而不消的反面=开机自报家门：已接四链 + 未接两链都要让人看见。"""
        sps.assemble_session(sps.parse_args([]), _RiskBroker(), state_dir=tmp_path)
        out = capsys.readouterr().out
        assert "[RISK]" in out
        assert "回撤基线=10000000.00" in out
        assert "rollback_metrics_provider" in out
