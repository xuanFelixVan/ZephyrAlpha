# [A_test] module_id: SRC-TST-1155 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_io_serialization

# [INVARIANTS] Decimal→str保留精度;datetime→ISO8601Z;Enum→str(value);确定性序列化

# [MODIFY-GUARD] serialization.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] SerializationError

# [TESTS] pytest tests/test_io_serialization.py -q
# [TTL] task_bound

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

import pytest

from zephyr.shared.io.serialization import (
    ENCODING_RULES,
    SerializationError,
    SerializationFormat,
    deserialize_datetime,
    deserialize_decimal,
    from_dict,
    from_json,
    serialize_datetime,
    serialize_decimal,
    to_dict,
    to_json,
)


class Color(Enum):
    RED = "red"
    BLUE = "blue"


@dataclass(frozen=True)
class SampleData:
    name: str
    value: Decimal
    timestamp: datetime
    color: Color


class TestSerializeDecimal:
    def test_valid(self):
        assert serialize_decimal(Decimal("100.50")) == "100.50"

    def test_preserves_precision(self):
        assert serialize_decimal(Decimal("0.123456789")) == "0.123456789"

    def test_invalid_type_raises(self):
        with pytest.raises(SerializationError, match="Decimal"):
            serialize_decimal(100.5)

    def test_zero(self):
        assert serialize_decimal(Decimal("0")) == "0"


class TestDeserializeDecimal:
    def test_from_string(self):
        assert deserialize_decimal("100.50") == Decimal("100.50")

    def test_from_int(self):
        assert deserialize_decimal(42) == Decimal("42")

    def test_from_float(self):
        result = deserialize_decimal(3.14)
        assert isinstance(result, Decimal)

    def test_invalid_type_raises(self):
        with pytest.raises(SerializationError, match="str/int/float"):
            deserialize_decimal([])


class TestSerializeDatetime:
    def test_utc(self):
        dt = datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC)
        result = serialize_datetime(dt)
        assert result.startswith("2026-05-05T12:00:00")
        assert result.endswith("Z")

    def test_naive_gets_utc(self):
        dt = datetime(2026, 5, 5, 12, 0, 0)
        result = serialize_datetime(dt)
        assert result.endswith("Z")

    def test_invalid_type_raises(self):
        with pytest.raises(SerializationError, match="datetime"):
            serialize_datetime("2026-05-05")


class TestDeserializeDatetime:
    def test_iso_string(self):
        result = deserialize_datetime("2026-05-05T12:00:00Z")
        assert result.year == 2026
        assert result.tzinfo == UTC

    def test_invalid_type_raises(self):
        with pytest.raises(SerializationError, match="str"):
            deserialize_datetime(12345)


class TestToDict:
    def test_dataclass(self):
        data = SampleData(
            name="test",
            value=Decimal("99.99"),
            timestamp=datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC),
            color=Color.RED,
        )
        result = to_dict(data)
        assert result["name"] == "test"
        assert result["value"] == "99.99"
        assert result["color"] == "red"
        assert "2026-05-05" in result["timestamp"]

    def test_unsupported_type_raises(self):
        with pytest.raises(SerializationError, match="Pydantic BaseModel or dataclass"):
            to_dict(object())


class TestFromDict:
    def test_roundtrip_dict(self):
        data = SampleData(
            name="test",
            value=Decimal("50.00"),
            timestamp=datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC),
            color=Color.BLUE,
        )
        d = to_dict(data)
        result = from_dict(d)
        assert isinstance(result, dict)
        assert result["name"] == "test"


class TestToJson:
    def test_produces_valid_json(self):
        data = SampleData(
            name="test",
            value=Decimal("10.00"),
            timestamp=datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC),
            color=Color.RED,
        )
        result = to_json(data)
        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["value"] == "10.00"

    def test_deterministic(self):
        data = SampleData(
            name="test",
            value=Decimal("10.00"),
            timestamp=datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC),
            color=Color.RED,
        )
        first = to_json(data)
        second = to_json(data)
        assert first == second


class TestFromJson:
    def test_roundtrip(self):
        data = SampleData(
            name="test",
            value=Decimal("25.50"),
            timestamp=datetime(2026, 5, 5, 12, 0, 0, tzinfo=UTC),
            color=Color.BLUE,
        )
        json_str = to_json(data)
        result = from_json(json_str)
        assert isinstance(result, dict)
        assert result["name"] == "test"


class TestEncodingRules:
    def test_has_required_keys(self):
        assert "Decimal" in ENCODING_RULES
        assert "datetime" in ENCODING_RULES


class TestSerializationFormat:
    def test_members(self):
        assert SerializationFormat.JSON.value == "json"
        assert SerializationFormat.DICT.value == "dict"


class TestSerializationError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = SerializationError("fail", details={"type": "bad"})
        assert isinstance(err, ZephyrBaseError)
