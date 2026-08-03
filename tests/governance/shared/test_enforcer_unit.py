# [A_test] module_id: MOD-GOV_enforcer_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-633 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_enforcer
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-633 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/contracts/enforcer.py
===================================================
覆盖矩阵：
  enforce_output：
    - 类型匹配通过 × 2（dataclass、primitive-like）
    - 类型不匹配拒绝 × 2（错误类型、None 当 required）
    - 字段校验 × 2（缺少必填字段、字段类型错误）
    - trace_required × 2（缺失 TraceContext、携带 TraceContext）
    - WARN 模式 × 1（违规但不抛异常）
    - None 返回值 × 1（跳过校验）
  enforce_input：
    - 自动匹配参数 × 1
    - 指定参数名 × 1
    - 参数缺失 × 1（跳过校验）
  enforce（组合）：
    - 入参+返回值同时校验 × 1
    - 入参违规阻断 × 1
  ContractViolationError：
    - 属性完整性 × 1
    - 字符串表示 × 1

Safety: HIGH（契约强制执行机制）
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

import pytest

from zephyr.shared.contracts.core.enforcer import (
    ContractViolationError,
    EnforcementMode,
    enforce,
    enforce_input,
    enforce_output,
)


@dataclass(frozen=True)
class FakeTraceContext:
    trace_id: str = "test-trace-001"
    span_id: str = "test-span-001"
    service_name: str = "test_service"
    parent_span_id: str | None = None
    created_at: str = "2026-05-04T00:00:00Z"
    schema_version: str = "1.0"


@dataclass(frozen=True)
class FakeContract:
    symbol: str
    price: Decimal
    trace_context: FakeTraceContext | None = None
    schema_version: str = "1.0"


@dataclass(frozen=True)
class OtherContract:
    symbol: str
    value: int


class TestEnforceOutput:
    def test_matching_type_passes(self):
        @enforce_output(FakeContract)
        def producer() -> FakeContract:
            return FakeContract(symbol="600519.SH", price=Decimal("100.00"))

        result = producer()
        assert result.symbol == "600519.SH"

    def test_wrong_type_raises(self):
        @enforce_output(FakeContract)
        def producer() -> OtherContract:
            return OtherContract(symbol="test", value=42)

        with pytest.raises(ContractViolationError) as exc_info:
            producer()
        assert "类型不匹配" in str(exc_info.value)
        assert "FakeContract" in str(exc_info.value)
        assert exc_info.value.violation_type == "output_contract_violation"

    def test_field_type_error_raises(self):
        @enforce_output(FakeContract)
        def producer() -> FakeContract:
            return FakeContract(
                symbol=12345,
                price="not_a_decimal",
            )

        with pytest.raises(ContractViolationError) as exc_info:
            producer()
        assert "类型不匹配" in str(exc_info.value)

    def test_trace_required_missing_raises(self):
        @enforce_output(FakeContract, trace_required=True)
        def producer() -> FakeContract:
            return FakeContract(
                symbol="600519.SH",
                price=Decimal("100.00"),
                trace_context=None,
            )

        with pytest.raises(ContractViolationError) as exc_info:
            producer()
        assert "TraceContext" in str(exc_info.value)

    def test_trace_required_present_passes(self):
        @enforce_output(FakeContract, trace_required=True)
        def producer() -> FakeContract:
            return FakeContract(
                symbol="600519.SH",
                price=Decimal("100.00"),
                trace_context=FakeTraceContext(),
            )

        result = producer()
        assert result.trace_context is not None

    def test_warn_mode_does_not_raise(self, caplog):
        @enforce_output(FakeContract, mode=EnforcementMode.WARN)
        def producer() -> OtherContract:
            return OtherContract(symbol="test", value=42)

        result = producer()
        assert result.value == 42

    def test_none_result_skips_validation(self):
        @enforce_output(FakeContract)
        def producer() -> None:
            return None

        result = producer()
        assert result is None


class TestEnforceInput:
    def test_auto_match_param(self):
        @enforce_input(FakeContract)
        def consumer(data: FakeContract) -> str:
            return data.symbol

        valid = FakeContract(symbol="600519.SH", price=Decimal("100.00"))
        result = consumer(valid)
        assert result == "600519.SH"

    def test_auto_match_rejects_wrong_type(self):
        @enforce_input(FakeContract)
        def consumer(data: FakeContract, extra: int = 0) -> str:
            return data.symbol

        wrong = OtherContract(symbol="test", value=42)
        with pytest.raises(ContractViolationError) as exc_info:
            consumer(wrong)
        assert "input_contract_violation" in exc_info.value.violation_type

    def test_explicit_param_name(self):
        @enforce_input(FakeContract, param_name="market_data")
        def consumer(market_data: FakeContract, other: str = "") -> str:
            return market_data.symbol

        valid = FakeContract(symbol="600519.SH", price=Decimal("100.00"))
        result = consumer(market_data=valid)
        assert result == "600519.SH"

    def test_param_not_found_skips(self):
        @enforce_input(FakeContract, param_name="nonexistent")
        def consumer(data: str) -> str:
            return data

        result = consumer("raw_string")
        assert result == "raw_string"

    def test_none_value_skips(self):
        @enforce_input(FakeContract, param_name="data")
        def consumer(data: FakeContract | None = None) -> str | None:
            return data.symbol if data else None

        result = consumer(None)
        assert result is None

    def test_trace_required_on_input(self):
        @enforce_input(FakeContract, trace_required=True)
        def consumer(data: FakeContract) -> str:
            return data.symbol

        missing_trace = FakeContract(
            symbol="600519.SH",
            price=Decimal("100.00"),
            trace_context=None,
        )
        with pytest.raises(ContractViolationError) as exc_info:
            consumer(missing_trace)
        assert "TraceContext" in str(exc_info.value)


class TestEnforceCombined:
    def test_both_input_and_output_valid_passes(self):
        @enforce(FakeContract)
        def passthrough(data: FakeContract) -> FakeContract:
            return data

        valid = FakeContract(symbol="600519.SH", price=Decimal("100.00"))
        result = passthrough(valid)
        assert result.symbol == "600519.SH"

    def test_input_violation_blocks(self):
        @enforce(FakeContract)
        def passthrough(data: FakeContract) -> FakeContract:
            return data

        wrong = OtherContract(symbol="test", value=42)
        with pytest.raises(ContractViolationError) as exc_info:
            passthrough(wrong)
        assert "input_contract_violation" in exc_info.value.violation_type

    def test_output_violation_blocks(self):
        @enforce(FakeContract)
        def passthrough(data: FakeContract) -> OtherContract:
            return OtherContract(symbol=data.symbol, value=42)

        valid = FakeContract(symbol="600519.SH", price=Decimal("100.00"))
        with pytest.raises(ContractViolationError) as exc_info:
            passthrough(valid)
        assert "output_contract_violation" in exc_info.value.violation_type


class TestContractViolationError:
    def test_all_fields_populated(self):
        err = ContractViolationError(
            contract_id="FakeContract",
            violation_type="type_mismatch",
            detail="测试详情",
            field_name="symbol",
            expected_type="str",
            actual_type="int",
        )
        assert err.contract_id == "FakeContract"
        assert err.violation_type == "type_mismatch"
        assert err.field_name == "symbol"
        assert err.expected_type == "str"
        assert err.actual_type == "int"
        assert err.error_id
        assert err.timestamp

    def test_string_representation(self):
        err = ContractViolationError(
            contract_id="FakeContract",
            violation_type="type_mismatch",
            detail="字段类型不匹配",
            field_name="price",
            expected_type="Decimal",
            actual_type="float",
        )
        rep = str(err)
        assert "type_mismatch" in rep
        assert "FakeContract" in rep
        assert "price" in rep
        assert "Decimal" in rep
        assert "float" in rep
