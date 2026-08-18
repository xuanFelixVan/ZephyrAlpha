"""43 号合规模块运行时接线 红队集成测试（tracker #78，AI-ASM-001 装配批）。

三向红队向量实证（合规闸门在买入/执行链路真实触发，非 mock 闸）：
  1. 超笔数阻断：日申报 1 万笔整 → C-002（OrderManager.submit_order）拒发；
     9999 笔放行；先报告后交易（ReportGate BLOCK）同链拒发。
  2. 清单缺项 Hard Block：INTRADAY 必做清单缺项 → C-004（TradingSession）
     整批拒单；补全后放行。
  3. 纪律闸熔断：报复交易命中 → HARD_BLOCK + KillSwitchLite 落盘；
     同策略经 C-004 与 MOD-PA-006 双通道均被熔断拦截（跨链一致性）。

所有合规日志/熔断状态写 tmp_path，不污染生产证据链（MAIN_REPO_ROOT）。
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.compliance_report_registry import (
    ComplianceReportRegistry,
    ReportGate,
)
from zephyr.compliance.discipline_must_do_checker import ChecklistCompletionChecker
from zephyr.compliance.discipline_prohibition_checker import (
    DisciplineAction,
    DisciplineContext,
    DisciplineGuard,
    KillSwitchLite,
    OrderRequest,
    ProhibitedBehavior,
)
from zephyr.ex_core.cancel_rate_guard import CancelRateGuard
from zephyr.ex_core.order_manager import ComplianceGateBlockError, OrderManager
from zephyr.ex_core.signal_providers import (
    make_mock_price_provider,
    make_mock_signal_provider,
)
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
from zephyr.pf_alloc.batched_position_builder import BatchedPositionBuilder
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.position import PositionSnapshot

# ---------------------------------------------------------------------
# 测试辅助
# ---------------------------------------------------------------------


def _logger(tmp_path) -> ComplianceLogger:
    return ComplianceLogger(path=tmp_path / "compliance_log.jsonl")


def _write_registry(tmp_path, *, all_acked: bool) -> ComplianceReportRegistry:
    item = {
        "item_id": "RPT-1",
        "name": "账户基本信息",
        "required": True,
        "reported_at": "2026-08-15" if all_acked else None,
        "broker_ack": all_acked,
    }
    path = tmp_path / "compliance_report_registry.yaml"
    path.write_text(
        yaml.safe_dump({"report_items": [item]}, allow_unicode=True),
        encoding="utf-8",
    )
    return ComplianceReportRegistry(registry_path=path)


def _position(cash: Decimal = Decimal("1000000")) -> PositionSnapshot:
    return PositionSnapshot(
        as_of_timestamp=datetime.now(timezone.utc),
        idempotency_key="redteam",
        portfolio_id="redteam",
        cash=cash,
        holdings={},
        total_market_value=Decimal("0"),
        market_values={},
    )


def _discipline_ctx(**overrides) -> DisciplineContext:
    base = {
        "signal_ref_price": None,
        "surge_30min_pct": None,
        "position_pnl_pct": None,
        "win_streak": 0,
        "normal_exposure": 0.01,
        "daily_pnl_pct": 0.0,
        "projected_daily_freq": 1.0,
        "freq_baseline_20d": 1.0,
        "size_baseline_20d": 1e9,
    }
    base.update(overrides)
    return DisciplineContext(**base)


# ---------------------------------------------------------------------
# 红队向量 1：超笔数阻断 + 先报告后交易（C-002）
# ---------------------------------------------------------------------


class TestRedTeamDailyDeclarationBlock:
    """超笔数阻断：2026-06-08 新规 5000 预警 / 1 万阻断，C-002 真实拒发。"""

    def _make_om(self, tmp_path, guard, *, acked: bool = True):
        broker = MagicMock()
        broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"
        gate = ReportGate(registry=_write_registry(tmp_path, all_acked=acked), logger=_logger(tmp_path))
        om = OrderManager(report_gate=gate, declaration_guard=guard)
        om.register_broker("test_broker", broker)
        return om, broker

    def _submit_one(self, om):
        order = om.create_order(
            symbol="600519.SH",
            strategy_id="redteam",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            limit_price=Decimal("10"),
            broker_id="test_broker",
        )
        return om.submit_order(order.order_id, "test_broker")

    def test_9999_allows_10000_blocks(self, tmp_path):
        """默认阈值实证边界：9999 放行（WARNING 不阻断）→ 1 万整阻断。"""
        guard = CancelRateGuard()  # 默认 5000/10000
        om, broker = self._make_om(tmp_path, guard)
        for _ in range(9999):
            guard.record_submit()
        # 9999 ≥ 5000 → WARNING 但放行；submit 侧对称计数（AI-R2 红队 ATK-5：
        # 指令发往券商即计）→ 该笔放行后恰好计满 1 万
        assert self._submit_one(om).startswith("broker_")
        assert guard.daily_declaration_count == 10000
        with pytest.raises(ComplianceGateBlockError, match="日申报笔数"):
            self._submit_one(om)
        assert broker.submit_order.call_count == 1  # 仅放行那一笔

    def test_report_gate_block_rejects_full_chain(self, tmp_path):
        """先报告后交易：broker_ack 缺失 → C-002 拒发（43 号 §7.4 铁律）。"""
        guard = CancelRateGuard()
        om, broker = self._make_om(tmp_path, guard, acked=False)
        with pytest.raises(ComplianceGateBlockError, match="先报告后交易"):
            self._submit_one(om)
        broker.submit_order.assert_not_called()


# ---------------------------------------------------------------------
# 红队向量 2：清单缺项 Hard Block（C-004）
# ---------------------------------------------------------------------


class TestRedTeamChecklistHardBlock:
    """清单缺项：INTRADAY 必做清单是四时点唯一 Hard Block 项（43 号 §3.3）。"""

    def _make_session(self, tmp_path, completed: set[str]):
        broker = MagicMock()
        broker.get_positions.return_value = _position()
        broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"
        checker = ChecklistCompletionChecker(
            completion_provider=lambda cp, td: completed,
            logger=_logger(tmp_path),
        )
        config = TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker")
        config.max_single_order_pct = Decimal("1.0")
        config.max_symbol_orders_per_day = 999999
        config.max_total_orders_per_day = 999999
        om = OrderManager()
        om.register_broker("test_broker", broker)
        session = TradingSession(
            broker=broker,
            strategy=MagicMock(
                generate_target_weights=MagicMock(return_value={"600519.SH": 0.03})
            ),
            risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
            signal_provider=make_mock_signal_provider({}),
            price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
            order_manager=om,
            config=config,
            checklist_checker=checker,
        )
        return session, broker

    def test_missing_items_block_whole_batch(self, tmp_path):
        """缺项 → 整批拒单；补全 → 恢复下单（真实状态翻转）。"""
        session, broker = self._make_session(tmp_path, set())
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()
        # 补全清单（人工完成风控参数确认等三项）
        session._checklist_checker = ChecklistCompletionChecker(
            completion_provider=lambda cp, td: {
                "signal_compliance_check",
                "risk_param_confirm",
                "position_limit_verify",
            },
            logger=_logger(tmp_path),
        )
        assert len(session.rebalance()) == 1
        broker.submit_order.assert_called_once()


# ---------------------------------------------------------------------
# 红队向量 3：纪律闸熔断（C-004 × MOD-PA-006 跨链一致）
# ---------------------------------------------------------------------


class TestRedTeamDisciplineCircuitBreaker:
    """纪律闸熔断：报复交易 → HARD_BLOCK + KillSwitchLite 策略级熔断。"""

    def test_revenge_triggers_kill_switch_across_chains(self, tmp_path):
        """报复命中后：C-004 与 MOD-PA-006 共享熔断状态，同策略双通道全拦。"""
        ks = KillSwitchLite(
            state_path=tmp_path / "ks_state.json",
            logger=_logger(tmp_path),
        )
        guard = DisciplineGuard(kill_switch=ks, logger=_logger(tmp_path))

        # ── C-004 链：报复交易 ctx（当日亏 3% + 单笔规模 2 倍于基线）──
        broker = MagicMock()
        broker.get_positions.return_value = _position()
        broker.submit_order.side_effect = lambda order: f"broker_{order.order_id[:8]}"
        config = TradingSessionConfig(universe=["600519.SH"], broker_id="test_broker")
        config.strategy_id = "redteam_strategy"
        config.max_single_order_pct = Decimal("1.0")
        config.max_symbol_orders_per_day = 999999
        config.max_total_orders_per_day = 999999
        om = OrderManager()
        om.register_broker("test_broker", broker)
        session = TradingSession(
            broker=broker,
            strategy=MagicMock(
                generate_target_weights=MagicMock(return_value={"600519.SH": 0.03})
            ),
            risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
            signal_provider=make_mock_signal_provider({}),
            price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
            order_manager=om,
            config=config,
            kill_switch=ks,
            discipline_guard=guard,
            discipline_ctx_provider=lambda order, pos: _discipline_ctx(
                daily_pnl_pct=-0.03,  # < -2%
                size_baseline_20d=100.0,  # 本单 30000 > 1.5×100
            ),
        )
        # 第一笔：报复命中 → HARD_BLOCK + 熔断触发落盘
        assert session.rebalance() == []
        broker.submit_order.assert_not_called()
        assert ks.is_blocked("redteam_strategy", date.today())

        # 第二笔：ctx 已恢复中性，但熔断状态仍拦（KillSwitchLite 闸独立生效）
        session2 = TradingSession(
            broker=broker,
            strategy=MagicMock(
                generate_target_weights=MagicMock(return_value={"600519.SH": 0.03})
            ),
            risk_validator=MagicMock(validate_order=MagicMock(return_value=[])),
            signal_provider=make_mock_signal_provider({}),
            price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
            order_manager=om,
            config=config,
            kill_switch=ks,
            discipline_guard=guard,
            discipline_ctx_provider=lambda order, pos: _discipline_ctx(),
        )
        assert session2.rebalance() == []
        broker.submit_order.assert_not_called()

        # ── MOD-PA-006 链：同一熔断状态文件，同策略同样被拦 ──
        builder = BatchedPositionBuilder(discipline_guard=guard, kill_switch=ks)
        verdict = builder.gate_batch_order(
            OrderRequest(
                symbol="600519.SH",
                price=100.0,
                strategy_id="redteam_strategy",
                risk_exposure=0.03,
                size=30000.0,
                is_add=False,
            ),
            _discipline_ctx(),
            today=date.today(),
        )
        assert verdict.action is DisciplineAction.HARD_BLOCK
        assert verdict.kill_switch_triggered

        # 报复检测实证：第一笔的 verdict 行为类型留痕于合规日志
        records = _logger(tmp_path).read_all()
        revenge = [
            r for r in records
            if r.event_type == "DISCIPLINE_VERDICT"
            and r.payload.get("behavior") == ProhibitedBehavior.REVENGE_TRADING.value
        ]
        assert revenge, "合规日志应有 REVENGE_TRADING 判定留痕（自证清白证据链）"
        assert revenge[0].payload["kill_switch_triggered"] is True


# ---------------------------------------------------------------------
# 红队向量 4：尾盘操纵检测窗口时区口径（AI-R2-001 修复实证）
# ---------------------------------------------------------------------


class TestCloseWindowCstTimezone:
    """at_time 缺省 fallback 必须北京口径（原 UTC 口径使 14:57 窗口永不激活）。"""

    def test_cst_now_time_matches_shanghai(self):
        """_cst_now_time 与 Asia/Shanghai 独立换算一致（±2min 容差防边界翻转）。"""
        from datetime import time as dtime
        from zoneinfo import ZoneInfo

        from zephyr.ex_core.trading_session import _cst_now_time

        now_cst = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Shanghai"))
        got = _cst_now_time()
        assert isinstance(got, dtime)
        delta_min = abs(
            (got.hour * 60 + got.minute) - (now_cst.hour * 60 + now_cst.minute)
        )
        assert delta_min <= 2, f"fallback 口径漂移: got={got} expect≈{now_cst.time()}"

    def test_utc_fallback_would_never_hit_window(self):
        """反证原缺陷：UTC 交易时段（北京 09:30-15:00=UTC 01:30-07:00）
        的时刻永远 < 14:57 窗口起点——检测形同虚设。"""
        from datetime import time as dtime

        from zephyr.compliance.trading_compliance_detector import ComplianceThresholds

        t = ComplianceThresholds()
        utc_times = [dtime(h) for h in range(2, 8)]  # 北京交易时段的 UTC 投影
        assert all(ts < t.close_window_start for ts in utc_times)
