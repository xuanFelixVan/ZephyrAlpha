# [BLUEPRINT] MOD-CMP-002 | docs/03_modules/_domain_compliance/discipline_prohibition_checker/blueprint.md | §4.3
# [TTL] permanent
"""F62 合规门"诚实起点"基线测（正门=scripts/start_paper_session.py::assemble_session）。

施工口径（Owner 原话）：诚实起点就装补仓腿+熔断锁两把，其余明示未装。
"明示未装"是被测判据的一部分，不是免责声明——本文件把未激活的腿断成可执行形状：

  1. 正门装配后 TradingSession 真持有 discipline_guard / kill_switch / discipline_ctx_provider
     （成对约束不触发装配期 raise）；
  2. 补仓腿**真触发**：浮亏达阈 → HARD_BLOCK → 该单被拒 → broker 零 submit_order，
     并带"平价对照"（同一装配、同一路径、只差均价）证明拒的是补仓腿而非别的原因；
  3. 未激活腿有落点可断：追高腿在无锚时判"不可评估"（同一单补上锚即 HARD_BLOCK 作对照），
     报复腿的未激活态由装配横幅 + DISCIPLINE_LEG_ARMING 状态表双落点宣告（哨兵 -1 非 0 占位）；
  4. KillSwitchLite 三态钉死：文件不存在=放行 / 在册=阻断 / 文件存在但 JSON 坏=全拒；
  5. provider 自身抛异常=逐单 Fail-Closed 拒（失效面，非判据面）。

全部写入落 tmp_path（根宪法 §9 第 6 条：测试禁写生产 data/；合规证据日志经
assemble_session 的 compliance_log_path 注入口，KillSwitchLite 状态文件同注 tmp）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineAction,
    DisciplineContext,
    DisciplineGuard,
    KillSwitchLite,
    OrderRequest,
    ProhibitedBehavior,
)
from zephyr.ex_core.trading_session import TradingSession
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.position import PositionSnapshot

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "start_paper_session_f62_baseline",
    _ROOT / "scripts" / "start_paper_session.py",
)
sps = importlib.util.module_from_spec(_spec)
sys.modules["start_paper_session_f62_baseline"] = sps  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(sps)

_SYMBOL = "600000.SH"
_STRATEGY_ID = "paper-keepalive"
# 数量口径刻意取"权重级"小数：DefaultRiskValidator 把 holdings 当权重读
# （_is_blocked_by_risk 的 current_holdings_float），整手数量会被判成 300 倍仓位
# 而被组合风控先拒——那会把补仓腿的因果洗掉。本批只中和执行前时段闸。
_SEED_QTY = "0.0002"
_ORDER_QTY = "0.0001"
_TARGET_WEIGHT = 0.0001


# ── 测试替身（禁连真券商/真行情）─────────────────────────────────────────────


class _PaperBroker:
    """记录型模拟券商：只给账户快照与本会话成交，submit_order 记账不成交。"""

    def __init__(
        self,
        *,
        cash: str = "10000000",
        holdings: dict[str, str] | None = None,
        price: Decimal = Decimal("10"),
    ) -> None:
        self._cash = Decimal(cash)
        self._price = price
        self.holdings = {k: Decimal(v) for k, v in (holdings or {}).items()}
        self.submitted: list[object] = []
        self.disconnected = False
        self.fill_callbacks: list[object] = []

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        self.disconnected = True

    def register_fill_callback(self, callback) -> None:
        self.fill_callbacks.append(callback)

    def submit_order(self, order) -> str:
        self.submitted.append(order)
        return f"brk-{len(self.submitted)}"

    def cancel_order(self, broker_order_id: str) -> bool:
        return True

    def get_positions(self) -> PositionSnapshot:
        market_values = {symbol: qty * self._price for symbol, qty in self.holdings.items()}
        total_market_value = sum(market_values.values(), Decimal("0"))
        return PositionSnapshot(
            as_of_timestamp=datetime(2026, 9, 27, 10, 0, tzinfo=UTC),
            idempotency_key="f62-baseline-snapshot",
            portfolio_id="paper-book",
            cash=self._cash,
            holdings=dict(self.holdings),
            market_values=market_values,
            total_market_value=total_market_value,
        )

    def query_trades_today(self, trade_date: str | None = None) -> list[Fill]:
        return []


def _assemble(tmp_path: Path, broker: _PaperBroker) -> TradingSession:
    """走生产正门装配（state_dir/compliance_log_path/checklist_evidence_dir 全注 tmp，禁写 data/）。

    DEFECT-2（2026-09-28 st-zcloseout 收口）：清单闸三腿证据目录不注入时锚主仓
    ``data/compliance_log/checklist``——装配引导即向生产路径落
    risk_param_confirm/position_limit_verify（宪法 §9.6 隔离红线），且"当日无人工
    ack"的日态会让对照组被 C-004 清单闸吞单（必红）。本测经 ``checklist_evidence_dir=``
    正门缝注入 tmp，并经生产写侧真接口在 tmp 铺满三腿完成证据（C-004 fail-closed
    熔断语义保持全武装、被真实演练，只是演练面从生产目录换成 tmp）。
    """
    evidence_dir = tmp_path / "checklist_evidence"
    session = sps.assemble_session(
        sps.parse_args([]),
        broker,
        state_dir=tmp_path / "risk_state",
        compliance_log_path=tmp_path / "compliance_log.jsonl",
        checklist_evidence_dir=evidence_dir,
    )
    # 三腿全铺满：经生产 ChecklistEvidenceWriter 落 tmp 证据（来源标注留痕，
    # ZEPHYR_COMPLIANCE_ACK_KEY 在场时走同一 HMAC 路径）——C-004 闸保持 armed 且
    # 逐单被查，对照组测的是补仓腿因果而非日态。trade_date 必须对齐 checker 的
    # UTC 日口径（trading_session._validate_and_submit 以 datetime.now(UTC).date()
    # 取证，而装配引导①②与写侧③默认北京时区今天）：北京 00:00–08:00 窗口两者
    # 差一天，不对齐则三腿全判陈旧=跨零点常红（884e5639f8 红因链跨零点实测）。
    from zephyr.compliance.checklist_evidence import ChecklistEvidenceWriter

    writer = ChecklistEvidenceWriter(evidence_dir)
    trade_date = datetime.now(UTC).date()
    writer.write_risk_param_confirm(
        "f62-baseline-snapshot",
        {"max_single_position": _TARGET_WEIGHT},
        trade_date=trade_date,
        source="test_f62_honest_gate_baseline._assemble",
    )
    writer.write_position_limit_verify(
        "f62-baseline-snapshot",
        trade_date=trade_date,
        source="test_f62_honest_gate_baseline._assemble",
        detail={"phase": "test_seed"},
    )
    writer.write_signal_compliance_ack(
        "f62-honest-baseline-test",
        note="DEFECT-2 隔离修复+UTC 日对齐：测试证据目录全注 tmp_path",
        trade_date=trade_date,
        ack_source="pytest_tmp_injection",
    )
    return session


def _buy_add_order(session: TradingSession, *, price: str = "10", qty: str = _ORDER_QTY):
    return session._order_manager.create_order(
        symbol=_SYMBOL,
        strategy_id=_STRATEGY_ID,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
        limit_price=Decimal(price),
        broker_id="miniqmt",
    )


def _fill(*, fill_id: str = "f-seed", price: str, qty: str = _SEED_QTY) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=Decimal(price),
        fill_timestamp=datetime(2026, 9, 27, 9, 35, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"ik-{fill_id}",
        order_id="ord-seed",
        strategy_id=_STRATEGY_ID,
        symbol=_SYMBOL,
    )


def _neutralize_unrelated_gates(session: TradingSession, monkeypatch) -> None:
    """中和与合规闸无关的执行前时段闸（午休/收盘后它先拒，会把补仓腿的因果洗掉）。

    两个方向（拒/放行）都走同一中和，A/B 唯一差异=均价，故结论只可能来自补仓腿。
    """
    monkeypatch.setattr(session, "_is_blocked_by_pre_execution", lambda order: False)


# ── 1. 正门真接线（非 None + 成对约束不触发）────────────────────────────────


class TestFrontDoorWiring:
    def test_both_gates_are_held_by_the_session(self, tmp_path):
        """装配不是装饰：会话确实持有两把，且 guard/provider 成对（不成对=装配期 raise）。"""
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        assert isinstance(session._discipline_guard, DisciplineGuard)
        assert isinstance(session._kill_switch, KillSwitchLite)
        assert callable(session._discipline_ctx_provider)

    def test_kill_switch_default_state_path_is_not_a_tmp_leftover(self, tmp_path):
        """默认状态路径恒锚主仓（worktree 无歧义），且当前盘上不存在→不误伤。"""
        session = _assemble(tmp_path, _PaperBroker())
        path: Path = session._kill_switch._path  # noqa: SLF001 — 断言装配锚点，非业务读口
        assert path.is_absolute()
        assert path.parts[-3:] == ("data", "compliance_log", "kill_switch_lite_state.json")
        assert str(tmp_path) not in str(path)


# ── 2. 补仓腿真触发（含平价对照，钉死拒单原因）──────────────────────────────


class TestAddingToLoserLegReallyFires:
    def test_cost_price_has_no_home_in_position_snapshot(self):
        """CTR-006 快照无成本字段→均价只能走 tracker 侧（本批不改契约的实测依据）。"""
        assert "avg_cost" not in PositionSnapshot.__dataclass_fields__
        assert "avg_costs" not in PositionSnapshot.__dataclass_fields__

    def test_underwater_position_blocks_the_add_order(self, tmp_path, monkeypatch):
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY}, price=Decimal("10"))
        session = _assemble(tmp_path, broker)
        _neutralize_unrelated_gates(session, monkeypatch)
        # 均价底档走真接口：本会话成交派生（现价 10 / 均价 20 → 浮亏 -50% < -5%）
        session._risk_layer._position_tracker.apply_fill(_fill(price="20"), OrderSide.BUY)
        positions = broker.get_positions()
        order = _buy_add_order(session)

        ctx = session._discipline_ctx_provider(order, positions)
        assert ctx.position_pnl_pct == pytest.approx(-0.5)

        request = TradingSession._make_order_request(order, positions)
        assert request.is_add is True

        verdict = session._discipline_guard.check(request, ctx)
        assert verdict.action is DisciplineAction.HARD_BLOCK
        assert verdict.behavior is ProhibitedBehavior.ADDING_TO_LOSER

        assert session._is_blocked_by_compliance_gates(order, positions) is True
        submitted = session._validate_and_submit([order], {_SYMBOL: _TARGET_WEIGHT}, positions)
        assert submitted == []
        assert broker.submitted == []  # 该单从未触达 broker
        assert order in session._blocked_orders

    def test_flat_cost_control_submits(self, tmp_path, monkeypatch):
        """对照：同装配同路径，均价=现价（浮亏 0）→ 合规闸放行并真的下单。

        没有这条，上一条的"拒"可能来自任何一道别的门——补仓腿的因果就在这对里。
        """
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY}, price=Decimal("10"))
        session = _assemble(tmp_path, broker)
        _neutralize_unrelated_gates(session, monkeypatch)
        session._risk_layer._position_tracker.apply_fill(_fill(price="10"), OrderSide.BUY)
        positions = broker.get_positions()
        order = _buy_add_order(session)

        ctx = session._discipline_ctx_provider(order, positions)
        assert ctx.position_pnl_pct == pytest.approx(0.0)
        assert session._is_blocked_by_compliance_gates(order, positions) is False
        submitted = session._validate_and_submit([order], {_SYMBOL: _TARGET_WEIGHT}, positions)
        assert len(submitted) == 1
        assert len(broker.submitted) == 1

    def test_missing_cost_is_announced_not_silently_passed(self, tmp_path, caplog):
        """有持仓但均价底档缺失（隔夜仓未经本会话成交派生）→ 明示盲区，不静默判"无亏"。"""
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        positions = broker.get_positions()
        with caplog.at_level("WARNING"):
            ctx = session._discipline_ctx_provider(_buy_add_order(session), positions)
        assert ctx.position_pnl_pct is None
        assert "补仓腿盲区" in caplog.text


# ── 3. 未激活腿必须"明示"且有可断落点────────────────────────────────────────


class TestUnarmedLegsAreDeclared:
    def test_chasing_leg_is_inevaluable_without_anchor(self, tmp_path):
        """追高腿：无锚 ctx → 不评估（PASS）；同一单补上锚 → HARD_BLOCK（对照证明是 None 跳过）。"""
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        positions = broker.get_positions()
        order = _buy_add_order(session, price="12")  # 相对 9.5 的信号锚追涨 26%
        request = TradingSession._make_order_request(order, positions)
        ctx = session._discipline_ctx_provider(order, positions)
        assert ctx.signal_ref_price is None and ctx.surge_30min_pct is None
        assert session._discipline_guard.check(request, ctx).action is DisciplineAction.PASS

        anchored = DisciplineContext(
            signal_ref_price=9.5,
            surge_30min_pct=0.06,
            position_pnl_pct=ctx.position_pnl_pct,
            win_streak=ctx.win_streak,
            normal_exposure=ctx.normal_exposure,
            daily_pnl_pct=ctx.daily_pnl_pct,
            projected_daily_freq=ctx.projected_daily_freq,
            freq_baseline_20d=ctx.freq_baseline_20d,
            size_baseline_20d=ctx.size_baseline_20d,
        )
        chasing = session._discipline_guard.check(request, anchored)
        assert chasing.action is DisciplineAction.HARD_BLOCK
        assert chasing.behavior is ProhibitedBehavior.CHASING

    def test_assembly_banner_declares_revenge_leg_inactive(self, tmp_path, capsys):
        """ "明示未装"的落点：启动横幅逐腿宣告 + 机生 JSON 状态行 + 日志各一份。"""
        _assemble(tmp_path, _PaperBroker(holdings={_SYMBOL: _SEED_QTY}))
        out = capsys.readouterr().out
        assert "[DISCIPLINE]" in out
        assert "报复腿未激活" in out
        assert "追高腿未激活" in out
        assert "骄傲腿未激活" in out
        status = json.loads(out.split("[DISCIPLINE][STATUS] ")[1].splitlines()[0])
        assert status["ADDING_TO_LOSER"] == "armed"
        assert status["REVENGE_TRADING"].startswith("not_armed")
        assert status["CHASING"].startswith("not_armed")
        assert status["OVERCONFIDENCE"].startswith("not_armed")

    def test_status_table_is_the_same_source_as_the_banner(self, tmp_path):
        """状态表是常量真源（禁散文二份）；横幅打印的正是它。"""
        assert set(sps.DISCIPLINE_LEG_ARMING) == {
            "ADDING_TO_LOSER",
            "CHASING",
            "REVENGE_TRADING",
            "OVERCONFIDENCE",
        }
        assert sps._discipline_leg_arming_status(None)["ADDING_TO_LOSER"].startswith("not_armed")
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        status = sps._discipline_leg_arming_status(session._risk_layer._position_tracker)
        assert status == sps.DISCIPLINE_LEG_ARMING

    def test_no_source_baselines_use_sentinel_not_zero(self, tmp_path):
        """双基线禁 0 占位：0 会被下游读成"测得基线确为 0"，负哨兵只表达无源。

        报复腿判据带 baseline > 0 前置（discipline_prohibition_checker.py:268/:270），
        故无论 0 还是哨兵该腿都不判——差别在于本批把它**宣告**出来了（上一条测横幅）。
        """
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        ctx = session._discipline_ctx_provider(_buy_add_order(session), broker.get_positions())
        assert ctx.freq_baseline_20d == sps._NO_SOURCE_BASELINE
        assert ctx.size_baseline_20d == sps._NO_SOURCE_BASELINE
        assert ctx.freq_baseline_20d != 0.0 and ctx.size_baseline_20d != 0.0
        assert ctx.daily_pnl_pct == 0.0 and ctx.win_streak == 0

    def test_revenge_leg_never_fires_even_with_deep_daily_loss(self, tmp_path):
        """把 ctx 的当日亏损调到触发区，双基线无源仍不判——该腿确实没装（不假装装了）。"""
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        positions = broker.get_positions()
        order = _buy_add_order(session)
        base = session._discipline_ctx_provider(order, positions)
        request = TradingSession._make_order_request(order, positions)
        revenge_shaped = DisciplineContext(
            signal_ref_price=base.signal_ref_price,
            surge_30min_pct=base.surge_30min_pct,
            position_pnl_pct=base.position_pnl_pct,
            win_streak=base.win_streak,
            normal_exposure=base.normal_exposure,
            daily_pnl_pct=-0.09,  # 深亏（<-2%）
            projected_daily_freq=99.0,  # 频率远超任何合理基线
            freq_baseline_20d=base.freq_baseline_20d,
            size_baseline_20d=base.size_baseline_20d,
        )
        verdict = session._discipline_guard.check(request, revenge_shaped)
        assert verdict.behavior is not ProhibitedBehavior.REVENGE_TRADING
        assert session._kill_switch._path.exists() is False  # noqa: SLF001 — 断言未触发落盘


# ── 4. KillSwitchLite 三态（把"真全拒路径"钉住）─────────────────────────────


class TestKillSwitchLiteStates:
    def test_absent_file_passes_present_file_blocks_and_broken_json_blocks(self, tmp_path):
        path = tmp_path / "ks_state.json"
        ks = KillSwitchLite(state_path=path, logger=ComplianceLogger(path=tmp_path / "log.jsonl"))
        assert path.exists() is False
        assert ks.is_blocked(_STRATEGY_ID, date.today()) is False  # 不存在=放行（不误伤）

        path.write_text(
            json.dumps({_STRATEGY_ID: {"reason": "R", "expiry": date.today().isoformat()}}),
            encoding="utf-8",
        )
        assert ks.is_blocked(_STRATEGY_ID, date.today()) is True  # 在册=当日禁新开仓
        assert ks.is_blocked("another-strategy", date.today()) is False  # 只停触发策略

        path.write_text("{ this is not json", encoding="utf-8")
        assert ks.is_blocked("another-strategy", date.today()) is True  # 坏 JSON=全拒

    def test_is_blocked_has_no_escalate_side_effect(self, tmp_path):
        """is_blocked 只读不升级（escalate 只在 trigger）——防把"读状态"当"触发熔断"。"""
        calls: list[tuple[str, str]] = []
        ks = KillSwitchLite(
            state_path=tmp_path / "ks.json",
            on_escalate=lambda sid, reason: calls.append((sid, reason)),
            logger=ComplianceLogger(path=tmp_path / "log.jsonl"),
        )
        assert ks.is_blocked(_STRATEGY_ID, date.today()) is False
        assert calls == []
        assert (tmp_path / "ks.json").exists() is False

    def test_session_gate_consults_the_injected_kill_switch(self, tmp_path, monkeypatch):
        """第二把在正门里真生效：策略被熔断时合规闸拒单，broker 零调用。"""
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        _neutralize_unrelated_gates(session, monkeypatch)
        ks = KillSwitchLite(
            state_path=tmp_path / "ks.json",
            logger=ComplianceLogger(path=tmp_path / "log.jsonl"),
        )
        session._kill_switch = ks
        positions = broker.get_positions()
        order = _buy_add_order(session)
        assert session._is_blocked_by_compliance_gates(order, positions) is False  # 未熔断先放行
        ks.trigger(_STRATEGY_ID, "测试注入熔断", date.today())
        assert session._is_blocked_by_compliance_gates(order, positions) is True
        submitted = session._validate_and_submit([order], {_SYMBOL: _TARGET_WEIGHT}, positions)
        assert submitted == [] and broker.submitted == []


# ── 5. provider 失效面（Fail-Closed 侧必须有测）──────────────────────────────


class TestProviderFailureFailsClosed:
    def test_provider_exception_rejects_that_order(self, tmp_path):
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        positions = broker.get_positions()
        order = _buy_add_order(session)

        def _boom(_order: object, _positions: object) -> DisciplineContext:
            raise RuntimeError("ctx 供数失效")

        session._discipline_ctx_provider = _boom
        assert session._is_blocked_by_compliance_gates(order, positions) is True

    def test_tracker_read_outage_degrades_to_unevaluated_not_exception(self, tmp_path):
        """tracker 读口炸掉时 provider 自身降级为 None（不整体上抛）——失效面与判据面分离。"""
        broker = _PaperBroker(holdings={_SYMBOL: _SEED_QTY})
        session = _assemble(tmp_path, broker)
        broken_tracker = SimpleNamespace(avg_costs=_BoomMapping())
        ctx = sps._make_discipline_ctx_provider(broken_tracker, normal_exposure=0.01)(
            _buy_add_order(session), broker.get_positions()
        )
        assert ctx.position_pnl_pct is None
        assert ctx.freq_baseline_20d == sps._NO_SOURCE_BASELINE


class _BoomMapping(dict[str, Decimal]):
    """读即抛的均价面（模拟 tracker 内部失效）。"""

    def get(self, key: object, default: object = None) -> Decimal:  # type: ignore[override]
        raise RuntimeError("tracker 均价面不可读")
