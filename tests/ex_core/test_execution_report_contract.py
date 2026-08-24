# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.ex_core.test_execution_report_contract
# [DOMAIN] D_SHARED
# [INVARIANTS] CTR-P1-007契约层Fail-Closed校验; 序列化往返恒等; 消费方Protocol鸭子类型满足; codegen契约字段漂移守卫
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ExecutionReportContractError
# [TESTS] self
# [TTL] permanent
"""CTR-P1-007 ExecutionReport 契约层测试（GAP-L06-003，2026-08-24 施工批）。

覆盖：字段完整性（对齐 codegen 契约）/ Fail-Closed 校验拒绝非法输入 /
A 股特性（整手/涨跌停注入校验）/ 序列化往返 / 消费方 Protocol 鸭子类型
（A1③ 归因 Source 口、A8 mSPRT delta 提取口——含对 pf_core 既有预留位
ChampionChallengerDeltaExtractor 的结构满足）。
"""

from __future__ import annotations

import dataclasses
import json
from datetime import UTC, datetime
from decimal import Decimal
from typing import Iterable, Mapping

import pytest

from zephyr.ex_core.execution_engine import ExecutionEngineRunRecord
from zephyr.ex_core.execution_report import build_execution_report
from zephyr.pf_core.core.msprt_champion_challenger import (
    ChampionChallengerDeltaExtractor,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.contracts.execution_report_contract import (
    CONTRACT_ID,
    DEFAULT_BOARD_LOT,
    SCHEMA_VERSION,
    ExecutionReportContract,
    ExecutionReportContractError,
    ExecutionReportDeltaExtractor,
    ExecutionReportSource,
    NetPnlDeltaExtractor,
    execution_report_from_payload,
    execution_report_to_payload,
    report_net_cashflow,
    validate_execution_report,
)
from zephyr.shared.contracts.order import Order


def _order(side: OrderSide = OrderSide.BUY, qty: str = "1000", limit: str = "10.00") -> Order:
    return Order(
        idempotency_key="idem-o1",
        order_id="o1",
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
        side=side,
        strategy_id="S1",
        symbol="600000",
        limit_price=Decimal(limit),
        created_at=datetime(2026, 8, 20, 10, 0, tzinfo=UTC),
    )


def _record(
    filled: str = "1000",
    avg: str = "10.02",
    total: str = "1000",
    target: str = "10.00",
) -> ExecutionEngineRunRecord:
    return ExecutionEngineRunRecord(
        report_id="rpt-b1",
        order_id="o1",
        symbol="600000",
        algo_type="TWAP",
        total_quantity=Decimal(total),
        filled_quantity=Decimal(filled),
        avg_fill_price=Decimal(avg),
        target_price=Decimal(target),
        slippage_bps=Decimal("0"),
        commission=Decimal("5.25"),
        start_time=datetime(2026, 8, 20, 10, 0, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 20, 10, 5, 0, tzinfo=UTC),
        status="FILLED",
        venue="miniqmt",
    )


def _report(**overrides: object) -> ExecutionReport:
    """以产出函数构建合法基线，再按 overrides 构造变体（绕过产出侧校验）。"""
    base = dataclasses.asdict(build_execution_report(_order(), _record()))
    base.update(overrides)
    return ExecutionReport(**base)


class TestFieldCompleteness:
    def test_payload_keys_match_codegen_contract_fields(self):
        payload = execution_report_to_payload(_report())
        codegen_fields = {f.name for f in dataclasses.fields(ExecutionReport)}
        assert set(payload.keys()) == codegen_fields
        assert len(codegen_fields) == 15

    def test_contract_constants(self):
        assert CONTRACT_ID == "CTR-P1-007"
        assert SCHEMA_VERSION == "1.0"
        assert DEFAULT_BOARD_LOT == 100


class TestValidateAccepts:
    def test_accepts_built_report(self):
        report = build_execution_report(_order(), _record())
        assert validate_execution_report(report) is report

    def test_accepts_partial_fill(self):
        report = _report(actual_quantity=600)
        assert validate_execution_report(report) is report

    def test_accepts_zero_actual_quantity(self):
        report = _report(actual_quantity=0, vwap_price=Decimal("0"))
        assert validate_execution_report(report) is report


class TestValidateRejects:
    def test_empty_order_id_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(order_id=""))

    def test_empty_symbol_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(symbol=""))

    def test_invalid_direction_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(direction="HOLD"))

    def test_non_positive_intended_quantity_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(intended_quantity=0))

    def test_negative_actual_quantity_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(actual_quantity=-1))

    def test_actual_exceeds_intended_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(actual_quantity=1001))

    def test_negative_vwap_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(vwap_price=Decimal("-0.01")))

    def test_filled_with_zero_vwap_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(vwap_price=Decimal("0")))

    def test_negative_commission_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(commission=Decimal("-0.01")))

    def test_end_before_start_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(
                _report(execution_start="2026-08-20T10:05:00+00:00", execution_end="2026-08-20T10:00:00+00:00")
            )

    def test_naive_timestamp_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(execution_start="2026-08-20 10:00:00"))

    def test_nan_slippage_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(slippage_bps=float("nan")))

    def test_inf_slippage_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(slippage_bps=float("inf")))

    def test_wrong_schema_version_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(schema_version="9.9"))


class TestAshareFeatures:
    def test_buy_non_board_lot_rejected(self):
        # A 股买入申报须整手（默认 100 股）：1050 非整手 → 拒绝
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(intended_quantity=1050), board_lot=100)

    def test_buy_board_lot_aligned_accepted(self):
        report = _report(intended_quantity=1100)
        assert validate_execution_report(report, board_lot=100) is report

    def test_sell_odd_lot_allowed(self):
        # A 股卖出允许零股（上交所规则）：SELL 1050 不触发整手校验
        report = _report(direction=OrderSide.SELL.value, intended_quantity=1050)
        assert validate_execution_report(report, board_lot=100) is report

    def test_vwap_above_price_limit_up_rejected(self):
        # 成交价物理上不可能突破涨停价
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(), price_limit_up=Decimal("10.01"))

    def test_vwap_below_price_limit_down_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(_report(), price_limit_down=Decimal("10.03"))

    def test_vwap_within_price_limits_accepted(self):
        report = _report()
        assert (
            validate_execution_report(
                report, price_limit_up=Decimal("11.00"), price_limit_down=Decimal("9.00")
            )
            is report
        )

    def test_inverted_price_limits_rejected(self):
        with pytest.raises(ExecutionReportContractError):
            validate_execution_report(
                _report(), price_limit_up=Decimal("9.00"), price_limit_down=Decimal("11.00")
            )


class TestSerialization:
    def test_round_trip_equality(self):
        report = build_execution_report(_order(), _record())
        restored = execution_report_from_payload(execution_report_to_payload(report))
        assert restored == report

    def test_payload_is_json_serializable(self):
        payload = execution_report_to_payload(_report())
        text = json.dumps(payload)
        assert isinstance(text, str)
        assert payload["intended_price"] == "10.00"
        assert payload["vwap_price"] == "10.02"
        assert payload["commission"] == "5.25"

    def test_decimal_precision_preserved(self):
        report = _report(vwap_price=Decimal("10.0250"))
        restored = execution_report_from_payload(execution_report_to_payload(report))
        assert restored.vwap_price == Decimal("10.0250")

    def test_missing_required_key_rejected(self):
        payload = execution_report_to_payload(_report())
        del payload["order_id"]
        with pytest.raises(ExecutionReportContractError):
            execution_report_from_payload(payload)

    def test_unknown_schema_version_rejected(self):
        payload = execution_report_to_payload(_report())
        payload["schema_version"] = "2.0"
        with pytest.raises(ExecutionReportContractError):
            execution_report_from_payload(payload)

    def test_float_for_decimal_field_rejected(self):
        # 二进制浮点污染 Decimal 精度 → Fail-Closed 拒绝
        payload = execution_report_to_payload(_report())
        payload["vwap_price"] = 10.02
        with pytest.raises(ExecutionReportContractError):
            execution_report_from_payload(payload)

    def test_bool_for_int_field_rejected(self):
        payload = execution_report_to_payload(_report())
        payload["actual_quantity"] = True
        with pytest.raises(ExecutionReportContractError):
            execution_report_from_payload(payload)

    def test_extra_keys_ignored_for_forward_compat(self):
        payload = execution_report_to_payload(_report())
        payload["future_field"] = "x"
        restored = execution_report_from_payload(payload)
        assert restored == _report()

    def test_from_payload_runs_validation(self):
        # 入站反序列化必须过 Fail-Closed 校验（非法值即使类型正确也拒绝）
        payload = execution_report_to_payload(_report(direction="HOLD"))
        with pytest.raises(ExecutionReportContractError):
            execution_report_from_payload(payload)


class TestConsumerProtocols:
    def test_source_protocol_duck_type_satisfied(self):
        class _InMemorySource:
            def __init__(self, report: ExecutionReport) -> None:
                self._report = report

            def get_execution_report(self, order_id: str) -> ExecutionReport | None:
                return self._report if self._report.order_id == order_id else None

            def iter_execution_reports(
                self, symbol: str, window_start: str, window_end: str
            ) -> Iterable[ExecutionReport]:
                return iter([self._report])

        source = _InMemorySource(_report())
        assert isinstance(source, ExecutionReportSource)
        assert source.get_execution_report("o1") is not None

    def test_source_protocol_not_satisfied_by_plain_object(self):
        assert not isinstance(object(), ExecutionReportSource)

    def test_delta_extractor_satisfies_contract_protocol(self):
        assert isinstance(NetPnlDeltaExtractor(), ExecutionReportDeltaExtractor)

    def test_delta_extractor_satisfies_pf_core_reserved_protocol(self):
        # A8 mSPRT 对接位：结构满足 pf_core 预留的 ChampionChallengerDeltaExtractor
        assert isinstance(NetPnlDeltaExtractor(), ChampionChallengerDeltaExtractor)

    def test_net_cashflow_sign_convention(self):
        buy = _report(direction="BUY", actual_quantity=1000, vwap_price=Decimal("10.00"), commission=Decimal("5"))
        sell = _report(direction="SELL", actual_quantity=1000, vwap_price=Decimal("10.00"), commission=Decimal("5"))
        assert report_net_cashflow(buy) == Decimal("-10005")
        assert report_net_cashflow(sell) == Decimal("9995")

    def test_delta_positive_when_challenger_cheaper(self):
        # 同标的同方向配对：challenger 买得更便宜 → delta > 0（更优）
        champion = _report(vwap_price=Decimal("10.02"), commission=Decimal("5.25"))
        challenger = _report(vwap_price=Decimal("10.01"), commission=Decimal("5.25"))
        delta = NetPnlDeltaExtractor().extract_delta(champion, challenger)
        assert delta == pytest.approx(10.0)

    def test_delta_negative_when_challenger_dearer(self):
        champion = _report(vwap_price=Decimal("10.01"))
        challenger = _report(vwap_price=Decimal("10.02"))
        delta = NetPnlDeltaExtractor().extract_delta(champion, challenger)
        assert delta == pytest.approx(-10.0)

    def test_delta_mismatched_symbol_rejected(self):
        champion = _report()
        challenger = _report(symbol="000001")
        with pytest.raises(ExecutionReportContractError):
            NetPnlDeltaExtractor().extract_delta(champion, challenger)

    def test_delta_mismatched_direction_rejected(self):
        champion = _report()
        challenger = _report(direction="SELL")
        with pytest.raises(ExecutionReportContractError):
            NetPnlDeltaExtractor().extract_delta(champion, challenger)


class TestContractFacade:
    def test_facade_validate_delegates(self):
        report = _report()
        assert ExecutionReportContract.validate(report) is report

    def test_facade_round_trip(self):
        report = _report()
        assert ExecutionReportContract.from_payload(ExecutionReportContract.to_payload(report)) == report

    def test_facade_constants(self):
        assert ExecutionReportContract.CONTRACT_ID == "CTR-P1-007"
        assert ExecutionReportContract.SCHEMA_VERSION == "1.0"
