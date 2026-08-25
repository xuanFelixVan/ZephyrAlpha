# [BLUEPRINT] MOD-CON-002 | docs/03_modules/_domain_contracts/ctr002_producer_validator/blueprint.md | §test
# [A_test] module_id: MOD-CON-002 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Ctr002ProducerValidator 单元测试 (MOD-CON-002, MVP)。

覆盖: 必填字段完整性/取值域/时间戳 PIT 校验 / 违约阻断+错误契约返回 /
验证指标入 telemetry / 与消费侧适配器共用同一 Schema 源 / frozen。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

from zephyr.shared.contracts.ctr002_consumer_adapter import CTR002_SCHEMA
from zephyr.shared.contracts.ctr002_producer_validator import (
    Ctr002ProducerValidator,
    ProducerValidationError,
    _make_error_contract,
    validate_ctr002_producer,
)
from zephyr.shared.contracts.factor_signal import FactorSignal

_TS = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _signal(**overrides) -> FactorSignal:
    base = {
        "as_of_date": _TS,
        "factor_id": "momentum_20d",
        "idempotency_key": "k1",
        "raw_value": 0.83,
        "symbol": "600519",
    }
    base.update(overrides)
    return FactorSignal(**base)


class TestValidateProducer:
    def test_valid_signal(self) -> None:
        s = _signal()
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is True
        assert report.violations == ()
        assert report.error_contract is None

    def test_missing_required_factor_id(self) -> None:
        # FactorSignal dataclass frozen=True → 无法直接删字段；通过重写构造
        with pytest.raises(TypeError):
            FactorSignal(
                as_of_date=_TS,
                # factor_id 缺失
                idempotency_key="k1",
                raw_value=0.1,
                symbol="600519",
            )

    def test_invalid_confidence_above_one(self) -> None:
        s = _signal(confidence=1.1)
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("confidence" in v for v in report.violations)

    def test_invalid_confidence_below_zero(self) -> None:
        s = _signal(confidence=-0.1)
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("confidence" in v for v in report.violations)

    def test_invalid_rank_pct(self) -> None:
        s = _signal(rank_pct=1.1)
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("rank_pct" in v for v in report.violations)

    def test_nan_raw_value(self) -> None:
        s = _signal(raw_value=float("nan"))
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("raw_value" in v for v in report.violations)

    def test_infinite_raw_value(self) -> None:
        s = _signal(raw_value=float("inf"))
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("raw_value" in v for v in report.violations)

    def test_empty_factor_id(self) -> None:
        s = _signal(factor_id="")
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("factor_id" in v for v in report.violations)

    def test_pit_future_date_rejected(self) -> None:
        future = datetime.datetime(2100, 1, 1)
        s = _signal(as_of_date=future)
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert any("as_of_date" in v for v in report.violations)
        assert "PIT" in " ".join(report.violations)

    def test_error_contract_returned(self) -> None:
        s = _signal(confidence=2.0)
        report = Ctr002ProducerValidator().validate(s)
        assert report.ok is False
        assert report.error_contract is not None
        assert report.error_contract.contract_id == "CTR-002"
        assert report.error_contract.producer_domain == "D_FACTOR"
        assert any("confidence" in v for v in report.error_contract.violations)

    def test_telemetry_counters(self) -> None:
        v = Ctr002ProducerValidator()
        v.validate(_signal())
        v.validate(_signal(confidence=2.0))
        assert v.total_validated == 2
        assert v.total_violations == 1

    def test_metrics_hook_called(self) -> None:
        seen: list[tuple[str, int]] = []
        v = Ctr002ProducerValidator(metrics_hook=lambda name, val: seen.append((name, val)))
        v.validate(_signal())
        v.validate(_signal(confidence=2.0))
        names = [n for n, _ in seen]
        assert "ctr002_producer.validated" in names
        assert "ctr002_producer.violation" in names

    def test_metrics_hook_exception_not_blocking(self) -> None:
        def _boom(_name: str, _val: int) -> None:
            raise RuntimeError("hook boom")

        v = Ctr002ProducerValidator(metrics_hook=_boom)
        report = v.validate(_signal(confidence=2.0))
        assert report.ok is False
        assert v.total_violations == 1

    def test_batch_ok(self) -> None:
        signals = [_signal(), _signal(symbol="000001")]
        results = Ctr002ProducerValidator().validate_batch(signals)
        assert len(results) == 2
        assert all(r.ok for r in results)

    def test_batch_mixed(self) -> None:
        signals = [_signal(), _signal(confidence=-1.0)]
        results = Ctr002ProducerValidator().validate_batch(signals)
        assert results[0].ok is True
        assert results[1].ok is False

    def test_report_frozen(self) -> None:
        report = Ctr002ProducerValidator().validate(_signal())
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.ok = False  # type: ignore[misc]

    def test_strict_mode_raises_with_error_contract(self) -> None:
        s = _signal(confidence=2.0)
        with pytest.raises(ProducerValidationError) as exc_info:
            Ctr002ProducerValidator().validate(s, strict=True)
        assert exc_info.value.error_contract is not None
        assert "confidence" in " ".join(exc_info.value.error_contract.violations)

    def test_shared_schema_source_identity(self) -> None:
        # 与消费侧版本适配器（MOD-CON-001）共用同一 Schema 源，不另造
        assert Ctr002ProducerValidator().schema is CTR002_SCHEMA

    def test_clock_injection_pit(self) -> None:
        now = datetime.datetime(2026, 8, 25, 12, 0, 0)
        v = Ctr002ProducerValidator(clock=lambda: now)
        past = _signal(as_of_date=datetime.datetime(2026, 8, 25, 9, 30, 0))
        assert v.validate(past).ok is True
        future = _signal(as_of_date=datetime.datetime(2026, 8, 25, 12, 0, 1))
        assert v.validate(future).ok is False

    def test_aware_datetime_normalized_for_pit(self) -> None:
        now = datetime.datetime(2026, 8, 25, 12, 0, 0)
        v = Ctr002ProducerValidator(clock=lambda: now)
        aware_future = datetime.datetime(
            2026, 8, 25, 20, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=8))
        )
        assert v.validate(_signal(as_of_date=aware_future)).ok is False
        aware_past = datetime.datetime(
            2026, 8, 25, 10, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=8))
        )
        assert v.validate(_signal(as_of_date=aware_past)).ok is True


class TestMakeErrorContract:
    def test_error_contract_contains_all_violations(self) -> None:
        ec = _make_error_contract(["confidence 越界", "rank_pct 越界"])
        assert ec.contract_id == "CTR-002"
        assert "confidence 越界" in ec.violations
        assert "rank_pct 越界" in ec.violations


class TestConvenienceFunction:
    def test_validate_ctr002_producer_ok(self) -> None:
        s = _signal()
        report = validate_ctr002_producer(s)
        assert report.ok is True

    def test_validate_ctr002_producer_fail(self) -> None:
        s = _signal(raw_value=float("inf"))
        report = validate_ctr002_producer(s)
        assert report.ok is False
