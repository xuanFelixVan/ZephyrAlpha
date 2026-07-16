# [A_test] module_id: SRC-TST-2048 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-665 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_ocp_extension_points
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""OCP-002 / OCP-003 / OCP-001 扩展点冒烟测试。

病根：SSoT codegen 曾将 OCP 误判为 dataclass，导致 L05/L06 空壳抽象；本文件锁定
StrategyBase / BrokerInterface / FactorBase 的最小可运行形状。
"""


from datetime import UTC, datetime
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.ex_core.adapters.broker_interface import BrokerInterface
from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry
from zephyr.pf_core.strategy_base import StrategyBase, StrategyMeta, StrategyRegistry
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.trading.trading_contracts.execution.position import PositionSnapshot


@pytest.fixture(autouse=True)
def _clear_ocp_registries() -> None:
    FactorRegistry.clear()
    StrategyRegistry.clear()
    yield
    FactorRegistry.clear()
    StrategyRegistry.clear()


def test_import_l02_package_exports_factor_base() -> None:
    import zephyr.factor as l02

    assert l02.FactorBase is FactorBase
    assert callable(l02.autodiscover_factors)


def test_factor_registry_roundtrip() -> None:
    @FactorRegistry.register
    class SmokeFactor(FactorBase):
        meta = FactorMeta(
            factor_id="smoke_f1",
            name="Smoke",
            domain="technical",
            description="t",
        )

        def compute(self, data: pd.DataFrame, **kwargs):
            return data["close"].pct_change(1).fillna(0)

    cls = FactorRegistry.get("smoke_f1")
    assert cls is SmokeFactor
    df = pd.DataFrame({"close": [100.0, 101.0, 102.0]})
    series = SmokeFactor().compute(df)
    assert len(series) == 3


def test_strategy_registry_roundtrip() -> None:
    @StrategyRegistry.register
    class SmokeStrategy(StrategyBase):
        meta = StrategyMeta(
            strategy_id="smoke_s1",
            name="SmokeStrategy",
            strategy_type="custom",
            version="1.0.0",
            description="test",
        )

        def generate_target_weights(self) -> list[Order]:
            return []

    assert StrategyRegistry.get("smoke_s1") is SmokeStrategy


class _StubBroker(BrokerInterface):
    @property
    def broker_id(self) -> str:
        return "stub"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        return None

    def submit_order(self) -> str:
        return "bo-1"

    def cancel_order(self) -> bool:
        return True

    def query_order(self) -> Order:
        return Order(
            order_id="o1",
            symbol="TEST.SH",
            strategy_id="smoke_s1",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            idempotency_key="k",
            status=OrderStatus.PENDING,
        )

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="p1",
            idempotency_key="pk",
        )


def test_broker_interface_instantiable() -> None:
    b = _StubBroker()
    assert b.broker_id == "stub"
    assert isinstance(b.query_order(), Order)


def test_vector_memory_reexports_kb_facade() -> None:
    import zephyr

    vector_memory = getattr(zephyr, "vector-memory")

    assert hasattr(vector_memory, "get_unified_memory_api")
    assert hasattr(vector_memory, "UnifiedMemoryAPI")
