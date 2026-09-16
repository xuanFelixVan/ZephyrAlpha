# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.risk.test_bankruptcy_floor_wiring
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""破产底线接进单一熔断仲裁点（H5-P0 链1，35号 §4.10 static 腿 / §3.5 第五类触发源）。

实证目标（真实组件，仅 broker 外部边界替身——check_bankruptcy_floor /
DrawdownController / DrawdownTracker / VaRCalculator / TailRiskMonitor /
DefaultRiskValidator 全真实实例）：
  1. 装配方未注入初始本金 = 未武装：开机 WARNING 大声出声 + 全轮次不判定
     （绝不拿 tracker 峰值猜 static 锚——猜了就把"绝对破产防护"偷换成"会话内回撤防护"）
  2. 注入非法本金（≤0 / NaN / Inf）= 构造期 fail-fast 抛 ZA-RK-0067（拒绝带错底线开盘）
  3. nav < 本金×floor_ratio → 击穿：走回撤梯子**同一个** _engage_kill_switch
     （状态层 kill_switch_active 真实置位 + 真实清算卖单），快照
     position_cap=0 / allow_new_position=False / bankruptcy_floor_breached=True
  4. 底线击穿早于回撤梯子判定（evaluate_intraday 步 0），且**两口径正交**：
     trailing 回撤梯子 EMERGENCY 线=-15%（真源 alert_threshold_registry
     THD-DRAWDOWN-003），故把会话峰值锚（DrawdownTracker 初始净值）置于本金之下
     ——回撤仅 WARNING（-6%）而 static 底线已穿（845k < 1M×0.85）——照样熔断，
     仲裁日志出自破产底线而非回撤梯子（第五类触发源独立充分）
  5. 同一轮双源（回撤 EMERGENCY + 破产底线）只清算一次（单一仲裁点重入闩）
  6. 逐轮按实时 nav 重判：nav 回到底线之上后底线不再置位，但 KILL 闩锁
     不自动解除（35号 人工复位不变式，fail-closed 方向=停交易）
"""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.risk_layer_orchestrator import RiskLayerOrchestrator
from zephyr.position.core.drawdown_controller import DrawdownController
from zephyr.risk.core.drawdown_bankruptcy_floor import (
    BankruptcyFloorConfig,
    InvalidBankruptcyFloorInputError,
)
from zephyr.risk.core.drawdown_tracker import DrawdownAlertLevel, DrawdownTracker
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

_T0 = datetime(2026, 9, 16, 10, 0, tzinfo=UTC)
_INITIAL_NAV = 1_000_000.0
# 正交性场景对（static 本金 1M / trailing 峰值锚 900k）：nav 845k 距峰值仅 -6.1%
# （回撤梯子 WARNING 段 5%~10%，EMERGENCY 线 -15% 不熔断），却已穿 static 底线 850k
# ——同一场景在"已武装/未武装"两侧分别跑，差异只来自本金是否注入
_LOW_PEAK = 900_000.0
_BREACH_NAV = 845_000.0


class FakeBroker(BrokerInterface):
    """券商替身：持仓/现金可配，记录全部提交订单与撤单。"""

    def __init__(
        self,
        cash: Decimal = Decimal("600000"),
        holdings: dict[str, Decimal] | None = None,
        cost_prices: dict[str, Decimal] | None = None,
    ) -> None:
        self._cash = cash
        self._holdings: dict[str, Decimal] = dict(holdings if holdings is not None else {"600000.SH": Decimal("4000")})
        self._costs: dict[str, Decimal] = dict(cost_prices or {"600000.SH": Decimal("100")})
        self.submitted: list[Order] = []
        self.cancelled: list[str] = []

    @property
    def broker_id(self) -> str:
        return "fake"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        self.submitted.append(order)
        return f"bk-{order.order_id}"

    def cancel_order(self, broker_order_id: str) -> bool:
        self.cancelled.append(broker_order_id)
        return True

    def query_order(self, broker_order_id: str) -> Order | None:
        return None

    def get_positions(self) -> PositionSnapshot:
        mv = {s: qty * self._costs.get(s, Decimal("0")) for s, qty in self._holdings.items() if qty != 0}
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="fake",
            idempotency_key="fake",
            cash=self._cash,
            gross_leverage=0.0,
            holdings={s: q for s, q in self._holdings.items() if q != 0},
            market_values=mv,
            total_market_value=sum(mv.values(), Decimal("0")),
        )

    def register_fill_callback(self, callback) -> None:
        pass


def _make_orchestrator(
    *,
    broker: FakeBroker,
    capital: float | None = 1_000_000.0,
    floor_config: BankruptcyFloorConfig | None = None,
    kill_owner: DefaultRiskValidator | None = None,
    tracker_initial: float = _INITIAL_NAV,
) -> RiskLayerOrchestrator:
    """装配替身。tracker_initial=会话峰值锚（trailing 口径），capital=初始本金（static 口径）——
    两者故意分开：正交性用例要把峰值锚压到本金之下（回撤不熔断而底线已穿）。"""
    return RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=tracker_initial),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=broker,
        kill_switch_owner=kill_owner,
        bankruptcy_floor_initial_capital=capital,
        bankruptcy_floor_config=floor_config,
    )


# ---------------------------------------------------------------------
# ① 未武装：大声告警 + 不判定（禁猜默认本金）
# ---------------------------------------------------------------------


class TestUnarmedDegradesLoudly:
    def test_missing_capital_warns_and_never_judges(self, caplog: pytest.LogCaptureFixture) -> None:
        """未武装=不判定（不是"判定为安全"）：与正交性用例同参数，只差本金注入与否。"""
        broker = FakeBroker()
        with caplog.at_level(logging.WARNING, logger="zephyr.ex_core.risk_layer_orchestrator"):
            orch = _make_orchestrator(broker=broker, capital=None, tracker_initial=_LOW_PEAK)
        assert any("破产底线未武装" in r.getMessage() for r in caplog.records)
        assert orch.bankruptcy_floor is None

        orch.evaluate_intraday(_LOW_PEAK, now=_T0)  # 峰值锚定
        snap = orch.evaluate_intraday(_BREACH_NAV, now=_T0)  # 同一条 nav 已武装即击穿底线
        assert snap.bankruptcy_floor_breached is False
        assert orch.kill_switch_engaged is False, "未武装轮不得经破产底线起熔断"
        assert not any(
            "KILL_SWITCH_ENGAGE" in r.getMessage() and "破产底线" in r.getMessage() for r in caplog.records
        ), "破产底线不得在未武装时出声归因"

    @pytest.mark.parametrize("bad", [0.0, -1.0, math.nan, math.inf])
    def test_illegal_capital_fails_fast_at_construction(self, bad: float) -> None:
        with pytest.raises(InvalidBankruptcyFloorInputError):
            _make_orchestrator(broker=FakeBroker(), capital=bad)


# ---------------------------------------------------------------------
# ② 武装 + 击穿 → 同一熔断仲裁点
# ---------------------------------------------------------------------


class TestBreachEngagesSharedArbiter:
    def test_arming_exposes_absolute_floor(self) -> None:
        orch = _make_orchestrator(broker=FakeBroker())
        assert orch.bankruptcy_floor == pytest.approx(850_000.0)  # 1e6 × 默认 0.85

    def test_breach_triggers_kill_switch_state_layer_and_liquidation(self) -> None:
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            holdings={"600000.SH": Decimal("4000"), "000001.SZ": Decimal("2000")},
            cost_prices={"600000.SH": Decimal("100"), "000001.SZ": Decimal("100")},
        )
        orch = _make_orchestrator(broker=broker, kill_owner=validator)
        orch.evaluate_intraday(_INITIAL_NAV, now=_T0)

        snap = orch.evaluate_intraday(840_000.0, now=_T0)  # < 850k 底线

        assert snap.bankruptcy_floor_breached is True
        # 单一仲裁点：状态层熔断真实置位（与回撤梯子同一口）
        assert validator.kill_switch_active is True
        assert orch.kill_switch_engaged is True
        assert orch.is_trading_allowed is False
        # 清算链真实执行：两持仓全平卖出
        sells = {(o.symbol, o.side, o.quantity) for o in broker.submitted if o.side is OrderSide.SELL}
        assert sells == {("600000.SH", OrderSide.SELL, Decimal("4000")), ("000001.SZ", OrderSide.SELL, Decimal("2000"))}

    def test_breach_forces_cap_zero_and_forbids_new_position(self) -> None:
        """底线击穿轮：position_cap 强制 0 + 禁新开仓（最严口径，来自底线而非回撤梯子）。

        用正交性场景（峰值锚 900k / nav 845k）：同一条 nav 序列回撤仅 WARNING，
        底线未穿的同锚点用例（test_healthy_nav_does_not_breach）cap 仍 >0——
        故本例的 0 仓位归因破产底线。
        """
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker, tracker_initial=_LOW_PEAK)
        orch.evaluate_intraday(_LOW_PEAK, now=_T0)
        snap = orch.evaluate_intraday(_BREACH_NAV, now=_T0)
        assert snap.position_cap == 0.0
        assert snap.allow_new_position is False
        assert snap.bankruptcy_floor_breached is True

    def test_floor_breach_below_drawdown_emergency_still_kills(self, caplog: pytest.LogCaptureFixture) -> None:
        """正交性用例：回撤仅 WARNING（-6.1%，EMERGENCY 线 -15%）但 static 底线已穿 → 熔断。

        与 ① 的未武装用例同参数（tracker_initial=_LOW_PEAK + nav=_BREACH_NAV），
        唯一差异是本金是否注入——故本例证明的是第五类触发源**独立充分**，
        而不是回撤梯子的又一次触发。
        """
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker, tracker_initial=_LOW_PEAK)
        orch.evaluate_intraday(_LOW_PEAK, now=_T0)
        with caplog.at_level(logging.CRITICAL, logger="zephyr.ex_core.risk_layer_orchestrator"):
            snap = orch.evaluate_intraday(_BREACH_NAV, now=_T0)
        assert snap.drawdown_level is DrawdownAlertLevel.WARNING  # 回撤梯子本身不会熔断
        assert snap.bankruptcy_floor_breached is True
        assert orch.kill_switch_engaged is True  # 第五类触发源独立充分
        engages = [r.getMessage() for r in caplog.records if "KILL_SWITCH_ENGAGE" in r.getMessage()]
        assert engages and "破产底线击穿" in engages[0]

    def test_custom_floor_ratio_is_honored(self) -> None:
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker, floor_config=BankruptcyFloorConfig(floor_ratio=0.95))
        assert orch.bankruptcy_floor == pytest.approx(950_000.0)
        orch.evaluate_intraday(_INITIAL_NAV, now=_T0)
        assert orch.evaluate_intraday(940_000.0, now=_T0).bankruptcy_floor_breached is True

    def test_healthy_nav_does_not_breach(self) -> None:
        """同锚点对照：nav 在 static 底线之上 → 不判定、不熔断、仓位帽不被强制为 0。"""
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker, tracker_initial=_LOW_PEAK)
        orch.evaluate_intraday(_LOW_PEAK, now=_T0)
        snap = orch.evaluate_intraday(880_000.0, now=_T0)  # 底线 850k 之上
        assert snap.bankruptcy_floor_breached is False
        assert orch.kill_switch_engaged is False
        assert snap.position_cap > 0.0


# ---------------------------------------------------------------------
# ③ 双源同轮 / 逐轮重判：仲裁点唯一性与人工复位语义
# ---------------------------------------------------------------------


class TestArbiterUniqueness:
    def test_two_sources_same_round_liquidate_once(self) -> None:
        """-30% 同轮既是回撤 EMERGENCY 又穿底线 → 只清算一批卖单（重入闩）。"""
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            holdings={"600000.SH": Decimal("4000"), "000001.SZ": Decimal("2000")},
            cost_prices={"600000.SH": Decimal("100"), "000001.SZ": Decimal("100")},
        )
        orch = _make_orchestrator(broker=broker, kill_owner=validator)
        orch.evaluate_intraday(_INITIAL_NAV, now=_T0)
        snap = orch.evaluate_intraday(700_000.0, now=_T0)

        assert snap.bankruptcy_floor_breached is True
        sells = [o for o in broker.submitted if o.side is OrderSide.SELL]
        assert len(sells) == 2  # 每持仓一笔，不因双源翻倍
        assert len({o.symbol for o in sells}) == 2

    def test_floor_rejudged_from_live_nav_but_latch_holds(self) -> None:
        """nav 回到底线之上：底线位撤销，KILL 闩锁不自动解除（人工复位不变式）。"""
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker)
        orch.evaluate_intraday(_INITIAL_NAV, now=_T0)
        assert orch.evaluate_intraday(820_000.0, now=_T0).bankruptcy_floor_breached is True

        recovered = orch.evaluate_intraday(900_000.0, now=_T0)
        assert recovered.bankruptcy_floor_breached is False  # 逐轮实时重判，不锁存判定
        assert orch.kill_switch_engaged is True  # 熔断态只由人工复位解除
        assert orch.is_trading_allowed is False  # fail-closed 方向=停交易
        assert recovered.position_cap > 0.0  # 底线约束随实时判定解除，层值回可见
