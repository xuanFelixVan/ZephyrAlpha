# [A_test] module_id: MOD-INF-016 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §test
# [MODULE] tests.trading.test_kill_switch_rejection_drill
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [TTL] task_bound
"""F61 拒单演练（zc-lane-k-20260927，M7-02 B4 / G5 前置）：五级熔断全链实弹。

此前拒单演练 0 次（F61 卷缺口 4="拒单链零次实弹证明"）。本演练红绿双态：
  绿链：sim 假校验器触发 DAILY_LOSS → 拒单 + 落盘影子 → 模拟重启（内存失忆）
        → rebuild_from_disk 重臂 → 拒单维持 → rebuild 幂等复跑；
  红态：无影子无触发 → 不重臂不拒单（零重臂语义，纯加闸不加放）；
  接线：TradingSession.start() 启动链真实调 rebuild_from_disk（重启失忆窗关闭）。

测试隔离：state 影子经 monkeypatch store.default_state_path 全程落 tmp_path
（宪法 §9.6 禁写生产 data/）；KILL_SWITCHES 模块级单例前后清零。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

pytest.importorskip(
    "zephyr.trading.trading_contracts.risk.kill_switch_state_store",
    reason="kill_switch_state_store not importable",
)

from zephyr.ex_core.signal_providers import (  # noqa: E402
    make_mock_price_provider,
    make_mock_signal_provider,
)
from zephyr.ex_core.trading_session import (  # noqa: E402
    TradingSession,
    TradingSessionConfig,
)
from zephyr.governance.adapters.risk_validation_bridge import RiskViolation  # noqa: E402
from zephyr.trading.trading_contracts.risk import (  # noqa: E402
    kill_switch_state_store as store,
)
from zephyr.trading.trading_contracts.risk import trading_kill_switch as tks  # noqa: E402
from zephyr.trading.trading_contracts.risk.trading_kill_switch import (  # noqa: E402
    KillSwitchLevel,
)


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """影子路径隔离到 tmp + KILL_SWITCHES 内存态前后清零（模块级单例）。

    前置清零必须绕过 tks.reset（其落盘钩子会建出影子文件，污染红态断言），
    直翻内存旗标；后置清零用 reset 顺带把影子刷成全 inactive。
    """
    shadow = tmp_path / "trading_kill_switch_state.json"
    monkeypatch.setattr(store, "default_state_path", lambda: shadow)
    for level in KillSwitchLevel:
        tks.KILL_SWITCHES[level].active = False
    yield shadow
    for level in KillSwitchLevel:
        tks.reset(level)


class _DailyLossTriggerValidator:
    """sim 假校验器：首笔校验触发 DAILY_LOSS 五级熔断（自动落盘），此后 HALT 拒单。

    对齐 DefaultRiskValidator 语义（kill_switch_active → HALT 全拒），
    熔断真源=trading_kill_switch.KILL_SWITCHES（非自恢复级，跨重启维持）。
    """

    validator_id = "daily-loss-trigger-validator"

    def __init__(self) -> None:
        self.validate_calls = 0

    def validate_order(self, *, symbol, target_weight, current_holdings, limits):
        self.validate_calls += 1
        if self.validate_calls == 1:
            tks.trigger(KillSwitchLevel.DAILY_LOSS)  # 触发即自动落盘影子
        if tks.get_switch(KillSwitchLevel.DAILY_LOSS).active:
            return [
                RiskViolation(
                    constraint="daily_loss_kill_switch",
                    description="DAILY_LOSS 熔断演练：当日禁新单（-3%AUM 红线）",
                    limit_value=Decimal("-0.03"),
                    actual_value=Decimal(str(target_weight)),
                    severity="HALT",
                )
            ]
        return []


class _PassThroughValidator:
    """红态对照：永远放行。"""

    validator_id = "pass-through-validator"

    def validate_order(self, *, symbol, target_weight, current_holdings, limits):
        return []


def _make_session(risk_validator, broker=None) -> TradingSession:
    broker = broker or MagicMock()
    strategy = MagicMock()
    strategy.generate_target_weights.return_value = {"600519.SH": 0.10}
    config = TradingSessionConfig(
        universe=["600519.SH"],
        broker_id="test_broker",
    )
    # 禁用订单层熔断（本演练只测五级交易熔断拒单链）
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999999
    config.max_total_orders_per_day = 999999
    return TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=make_mock_signal_provider({}),
        price_provider=make_mock_price_provider({"600519.SH": Decimal("100")}),
        order_manager=MagicMock(),
        config=config,
    )


def _make_position():
    from zephyr.shared.contracts.position import PositionSnapshot

    return PositionSnapshot(
        as_of_timestamp=datetime.now(UTC),
        idempotency_key="drill-snapshot",
        portfolio_id="drill",
        cash=Decimal("1000000"),
        holdings={},
        total_market_value=Decimal("0"),
        market_values={},
    )


class TestRejectionDrillGreenChain:
    """绿链：触发→拒单→落盘→重启失忆→重臂→拒单维持→幂等。"""

    def test_trigger_block_persist_rearm_full_chain(self, _isolate) -> None:
        broker = MagicMock()
        broker.get_positions.return_value = _make_position()
        validator = _DailyLossTriggerValidator()
        session = _make_session(validator, broker)

        # ① 首笔调仓：假校验器触发 DAILY_LOSS → HALT 拒单
        orders = session.rebalance()
        assert len(orders) == 0
        report = session.get_session_report()
        assert report["blocked_count"] == 1
        assert report["submitted_count"] == 0
        assert tks.get_switch(KillSwitchLevel.DAILY_LOSS).active is True
        assert validator.validate_calls >= 1

        # ② 落盘：影子文件存在且记录 DAILY_LOSS active
        assert _isolate.exists(), "DAILY_LOSS 触发未落盘影子"
        import json

        payload = json.loads(_isolate.read_text(encoding="utf-8"))
        assert payload["switches"]["DAILY_LOSS"]["active"] is True

        # ③ 模拟重启：内存失忆（绕过持久化钩子直接翻内存旗标），磁盘影子仍在
        tks.KILL_SWITCHES[KillSwitchLevel.DAILY_LOSS].active = False
        assert tks.active_switches() == []

        # ④ 重臂：rebuild_from_disk 从影子重臂非自恢复级
        rearmed = store.rebuild_from_disk()
        assert rearmed == ["DAILY_LOSS"]
        assert tks.get_switch(KillSwitchLevel.DAILY_LOSS).active is True

        # ⑤ 拒单维持：重臂后再调仓仍被 HALT 拒
        orders2 = session.rebalance()
        assert len(orders2) == 0
        assert session.get_session_report()["submitted_count"] == 0

        # ⑥ rebuild 幂等：复跑重臂同结果、无异常、状态不回退
        assert store.rebuild_from_disk() == ["DAILY_LOSS"]
        assert tks.get_switch(KillSwitchLevel.DAILY_LOSS).active is True


class TestRejectionDrillRedState:
    """红态：无触发无影子 → 不重臂、不拒单（零重臂语义）。"""

    def test_no_shadow_no_rearm_no_block(self, _isolate) -> None:
        assert not _isolate.exists()
        assert store.rebuild_from_disk() == []
        assert tks.active_switches() == []
        broker = MagicMock()
        broker.get_positions.return_value = _make_position()
        session = _make_session(_PassThroughValidator(), broker)
        orders = session.rebalance()
        assert len(orders) == 1  # 红态：无熔断不拒单
        assert session.get_session_report()["submitted_count"] == 1

    def test_corrupt_shadow_zero_rearm(self, _isolate) -> None:
        """影子损坏 → 零重臂不阻断（fail-safe 语义，INVARIANTS）。"""
        _isolate.write_text("{not-json", encoding="utf-8")
        assert store.rebuild_from_disk() == []
        assert tks.active_switches() == []


class TestStartWiringRebuild:
    """接线实证：TradingSession.start() 启动链真实调 rebuild_from_disk。"""

    def test_start_rebuilds_from_disk_shadow(self, _isolate) -> None:
        # 造影子：触发（落盘）→ 内存失忆（模拟重启后进程）
        tks.trigger(KillSwitchLevel.DAILY_LOSS)
        tks.KILL_SWITCHES[KillSwitchLevel.DAILY_LOSS].active = False

        broker = MagicMock()
        session = _make_session(_PassThroughValidator(), broker)
        session.start()

        # 启动链重臂生效：失忆窗关闭，非自恢复级跨重启维持
        assert tks.get_switch(KillSwitchLevel.DAILY_LOSS).active is True
        assert [ks.level for ks in tks.active_switches()] == [KillSwitchLevel.DAILY_LOSS]
        session.stop()

    def test_start_without_shadow_stays_clean(self, _isolate) -> None:
        """无影子启动 → 零重臂（纯加闸不加放，不误伤正常启动）。"""
        session = _make_session(_PassThroughValidator(), MagicMock())
        session.start()
        assert store.rebuild_from_disk.__name__  # 接线件在位
        assert tks.active_switches() == []
        session.stop()
