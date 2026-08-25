# [BLUEPRINT] MOD-CON-001 | docs/03_modules/_domain_contracts/ctr002_consumer_adapter/blueprint.md | §test
# [A_test] module_id: MOD-CON-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Ctr002ConsumerAdapter 单元测试 (MOD-CON-001, MVP)。

覆盖: Schema源派生（必填/可选默认值/取值域规则）/ semver 解析 / 版本三态协商
（exact/compatible/unsupported，major 不兼容即拒）/ 字段容忍（缺可选补默认、
缺必填拒收、新增字段收编 extra 留痕）/ 批量适配 / 契约变更订阅发布
（通知计数、单订阅异常不阻断、只升不降）/ 用法 Fail-Closed / frozen。
"""

from __future__ import annotations

import dataclasses
import datetime

import pytest

from zephyr.shared.contracts.ctr002_consumer_adapter import (
    CTR002_SCHEMA,
    AdaptationVerdict,
    ContractChange,
    Ctr002AdapterError,
    Ctr002ConsumerAdapter,
    negotiate_version,
    parse_semver,
)
from zephyr.shared.contracts.factor_signal import FactorSignal

_AS_OF = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _payload(**overrides) -> dict:
    base = {
        "as_of_date": _AS_OF,
        "factor_id": "momentum_20d",
        "idempotency_key": "momentum_20d:600519:20260825",
        "raw_value": 0.83,
        "symbol": "600519",
    }
    base.update(overrides)
    return base


# ── Schema 源派生 ─────────────────────────────────────────────────────────


class TestSchemaSource:
    def test_current_version_from_contract_default(self) -> None:
        assert CTR002_SCHEMA.current_version == "1.0"

    def test_required_fields_match_contract(self) -> None:
        assert set(CTR002_SCHEMA.required_fields) == {
            "as_of_date",
            "factor_id",
            "idempotency_key",
            "raw_value",
            "symbol",
        }

    def test_optional_defaults_cover_contract(self) -> None:
        defaults = CTR002_SCHEMA.optional_default_map()
        assert defaults["confidence"] == 1.0
        assert defaults["schema_version"] == "1.0"
        assert defaults["is_valid"] is True
        assert defaults["rank_pct"] is None
        # 必填字段不得出现在可选默认值表
        for name in CTR002_SCHEMA.required_fields:
            assert name not in defaults

    def test_field_rules_cover_key_domains(self) -> None:
        rules = {(r.field, r.rule) for r in CTR002_SCHEMA.field_rules}
        assert ("confidence", "prob_range") in rules
        assert ("rank_pct", "prob_range") in rules
        assert ("raw_value", "finite_number") in rules
        assert ("factor_id", "non_empty_str") in rules
        assert ("schema_version", "semver_str") in rules
        assert ("as_of_date", "datetime_type") in rules

    def test_schema_source_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            CTR002_SCHEMA.current_version = "9.9"  # type: ignore[misc]


# ── semver 解析与版本协商 ─────────────────────────────────────────────────


class TestVersionNegotiation:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("1.0", (1, 0)), ("1.2", (1, 2)), ("2.10.3", (2, 10)), (" 1.0 ", (1, 0))],
    )
    def test_parse_semver_ok(self, raw: str, expected: tuple[int, int]) -> None:
        assert parse_semver(raw) == expected

    @pytest.mark.parametrize("raw", ["", "1", "x.y", "1.x", "1.0.0.0", None])
    def test_parse_semver_bad(self, raw) -> None:
        assert parse_semver(raw) is None

    def test_exact(self) -> None:
        assert negotiate_version("1.0", ("1.0",)) == "exact"

    def test_compatible_same_major(self) -> None:
        assert negotiate_version("1.1", ("1.0",)) == "compatible"
        assert negotiate_version("1.0", ("1.1",)) == "compatible"

    def test_unsupported_major_mismatch(self) -> None:
        assert negotiate_version("2.0", ("1.0",)) == "unsupported"
        assert negotiate_version("0.9", ("1.0",)) == "unsupported"

    def test_unsupported_invalid(self) -> None:
        assert negotiate_version("abc", ("1.0",)) == "unsupported"

    def test_multi_supported_best_wins(self) -> None:
        supported = ("1.0", "2.0")
        assert negotiate_version("2.0", supported) == "exact"
        assert negotiate_version("1.5", supported) == "compatible"
        assert negotiate_version("3.0", supported) == "unsupported"


# ── 字段容忍适配 ──────────────────────────────────────────────────────────


class TestAdapt:
    def setup_method(self) -> None:
        self.adapter = Ctr002ConsumerAdapter()

    def test_full_payload_exact(self) -> None:
        verdict = self.adapter.adapt(_payload())
        assert verdict.accepted is True
        assert verdict.version_action == "exact"
        assert verdict.signal is not None
        assert verdict.signal.factor_id == "momentum_20d"
        assert verdict.signal.symbol == "600519"
        assert verdict.signal.raw_value == 0.83

    def test_missing_optional_filled_with_defaults(self) -> None:
        verdict = self.adapter.adapt(_payload(schema_version="1.0"))
        assert verdict.accepted is True
        assert "confidence" in verdict.filled_defaults
        assert "rank_pct" in verdict.filled_defaults
        assert verdict.signal is not None
        assert verdict.signal.confidence == 1.0
        assert verdict.signal.rank_pct is None

    def test_missing_required_rejected(self) -> None:
        payload = _payload()
        del payload["symbol"]
        verdict = self.adapter.adapt(payload)
        assert verdict.accepted is False
        assert verdict.signal is None
        assert "symbol" in verdict.missing_fields
        assert "symbol" in verdict.reason

    def test_unknown_fields_absorbed_into_extra(self) -> None:
        verdict = self.adapter.adapt(_payload(new_field_x=1, another="y"))
        assert verdict.accepted is True
        assert set(verdict.absorbed_extras) == {"new_field_x", "another"}
        assert verdict.signal is not None
        assert verdict.signal.extra["new_field_x"] == 1
        assert verdict.signal.extra["another"] == "y"

    def test_unknown_fields_merge_with_explicit_extra(self) -> None:
        verdict = self.adapter.adapt(_payload(extra={"keep": 1}, hot=2))
        assert verdict.accepted is True
        assert verdict.signal is not None
        assert verdict.signal.extra == {"keep": 1, "hot": 2}

    def test_mutable_defaults_not_shared(self) -> None:
        v1 = self.adapter.adapt(_payload())
        v2 = self.adapter.adapt(_payload(symbol="000001"))
        assert v1.signal is not None and v2.signal is not None
        assert v1.signal.exceptions is not v2.signal.exceptions
        assert v1.signal.extra is not v2.signal.extra

    def test_compatible_version_accepted(self) -> None:
        verdict = self.adapter.adapt(_payload(schema_version="1.3"))
        assert verdict.accepted is True
        assert verdict.version_action == "compatible"

    def test_unsupported_major_rejected_fail_closed(self) -> None:
        verdict = self.adapter.adapt(_payload(schema_version="2.0"))
        assert verdict.accepted is False
        assert verdict.version_action == "unsupported"
        assert verdict.signal is None

    def test_invalid_version_rejected(self) -> None:
        verdict = self.adapter.adapt(_payload(schema_version="abc"))
        assert verdict.accepted is False
        assert verdict.version_action == "unsupported"

    def test_missing_version_uses_current(self) -> None:
        verdict = self.adapter.adapt(_payload())
        assert verdict.accepted is True
        assert verdict.version_action == "exact"

    def test_non_mapping_payload_fail_closed(self) -> None:
        with pytest.raises(Ctr002AdapterError):
            self.adapter.adapt(["not", "a", "mapping"])  # type: ignore[arg-type]

    def test_empty_supported_versions_fail_closed(self) -> None:
        with pytest.raises(Ctr002AdapterError):
            Ctr002ConsumerAdapter(supported_versions=())

    def test_illegal_supported_version_fail_closed(self) -> None:
        with pytest.raises(Ctr002AdapterError):
            Ctr002ConsumerAdapter(supported_versions=("bad",))

    def test_verdict_frozen(self) -> None:
        verdict = self.adapter.adapt(_payload())
        assert isinstance(verdict, AdaptationVerdict)
        with pytest.raises(dataclasses.FrozenInstanceError):
            verdict.accepted = False  # type: ignore[misc]


# ── 批量适配 ──────────────────────────────────────────────────────────────


class TestAdaptBatch:
    def test_mixed_batch(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        payloads = [
            _payload(),
            _payload(symbol="000001", schema_version="2.0"),  # major 不兼容 → 拒
            {k: v for k, v in _payload(symbol="000002").items() if k != "symbol"},  # 缺必填 → 拒
        ]
        batch = adapter.adapt_batch(payloads)
        assert batch.total == 3
        assert len(batch.accepted_signals) == 1
        assert len(batch.rejections) == 2
        assert batch.rejections[0].index == 1
        assert batch.rejections[1].index == 2
        assert batch.rejections[0].version_action == "unsupported"

    def test_empty_batch(self) -> None:
        batch = Ctr002ConsumerAdapter().adapt_batch([])
        assert batch.total == 0
        assert batch.accepted_signals == ()
        assert batch.rejections == ()


# ── 契约变更事件订阅 ──────────────────────────────────────────────────────


class TestContractChangeSubscription:
    def test_subscribe_and_publish(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        seen: list[ContractChange] = []
        adapter.subscribe(seen.append)
        notified = adapter.publish_contract_change("1.1", "新增 rank_pct 语义说明")
        assert notified == 1
        assert len(seen) == 1
        change = seen[0]
        assert change.contract_id == "CTR-002"
        assert change.old_version == "1.0"
        assert change.new_version == "1.1"
        assert change.note == "新增 rank_pct 语义说明"
        assert adapter.current_version == "1.1"

    def test_subscriber_exception_not_blocking(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        seen: list[ContractChange] = []

        def _boom(_change: ContractChange) -> None:
            raise RuntimeError("subscriber boom")

        adapter.subscribe(_boom)
        adapter.subscribe(seen.append)
        notified = adapter.publish_contract_change("1.1", "n")
        assert notified == 1
        assert len(seen) == 1

    def test_publish_downgrade_rejected(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        adapter.publish_contract_change("1.1", "n")
        with pytest.raises(Ctr002AdapterError):
            adapter.publish_contract_change("1.0", "downgrade")

    def test_publish_same_version_rejected(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        with pytest.raises(Ctr002AdapterError):
            adapter.publish_contract_change("1.0", "no-op")

    def test_publish_invalid_version_rejected(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        with pytest.raises(Ctr002AdapterError):
            adapter.publish_contract_change("abc", "bad")

    def test_subscribe_non_callable_rejected(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        with pytest.raises(Ctr002AdapterError):
            adapter.subscribe("not-callable")  # type: ignore[arg-type]

    def test_audit_log_records_changes(self) -> None:
        adapter = Ctr002ConsumerAdapter()
        adapter.publish_contract_change("1.1", "第一次")
        adapter.publish_contract_change("1.2", "第二次")
        log = adapter.audit_log
        assert len(log) == 2
        assert "1.0->1.1" in log[0]
        assert "1.1->1.2" in log[1]
