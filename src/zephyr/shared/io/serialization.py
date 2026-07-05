# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.serialization
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_serialization | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
serialization.py —— 统一序列化/反序列化基础设施（Phase 7 新增 | 盲点 B10 修复）

痛点修复：Pydantic 的 .model_dump() 能干活，但跨模块序列化契约未统一——
  1. Decimal → str 还是 float？datetime → ISO 8601 还是 POSIX timestamp？
  2. 每个消费者自己决定序列化格式 → D_DATA→D_FACTOR→D_RESEARCH 管道中可能产生不同格式
  3. cross_layer_contracts.yaml 定了类型但没定序列化规则 → 契约半成品

设计对标：
  - Google Proto canonical JSON mapping
  - OpenAPI Spec format keywords (date-time / decimal-as-string)
  - Stripe API 的 JSON 序列化一致性（Decimal "100.50" 从不裸输出 float）

设计原则：
  - 确定性序列化——同一对象同一输入 → 永远同一输出
  - Decimal → str (ISO 格式，保留精度) / datetime → ISO 8601 with Z suffix (UTC)
  - 所有序列化/反序列化经过本模块 = SSoT
  - 零依赖第三方库——仅 Python 标准库 + decimal + datetime

AI 施工约定：
  - 任何跨层数据传输 MUST 使用 to_dict() / from_dict()——禁止裸 Pydantic .model_dump()
  - 外部 API 响应解析 MUST 使用 from_dict()——自动类型转换
  - 新的序列化规则追加到本文件的 ENCODING_RULES 字典

SSoT: MOD-INF-016 §2.9 shared-serialization
Version: 0.1.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum, unique
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ENCODING_RULES",
    "SerializationError",
    "SerializationFormat",
    "deserialize_datetime",
    "deserialize_decimal",
    "from_dict",
    "from_json",
    "serialize_datetime",
    "serialize_decimal",
    "to_dict",
    "to_json",
]

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class SerializationError(ZephyrBaseError):
    """序列化/反序列化过程中类型不兼容或格式错误。"""


@unique
class SerializationFormat(str, Enum):
    JSON = "json"
    DICT = "dict"


ENCODING_RULES: dict[str, str] = {
    "Decimal": "str(ISO-decimal)——例 Decimal('100.50') → '100.50' 保留精度永不丢",
    "datetime": "ISO-8601 with Z suffix (UTC)——例 datetime(2026,5,5,12,0,0,tzinfo=UTC) → '2026-05-05T12:00:00.000000Z'",
    "date": "ISO-8601 date only——例 date(2026,5,5) → '2026-05-05'",
    "Enum": "str(value)——枚举值转换为字符串表示",
    "int/float/bool/str": "直通——原生类型无需转换",
    "None": "JSON null",
    "list/dict": "递归应用本规则",
}


def serialize_decimal(value: Decimal) -> str:
    if not isinstance(value, Decimal):
        raise SerializationError(
            f"serialize_decimal expects Decimal, got {type(value).__name__}",
            details={"value": str(value), "type": type(value).__name__},
        )
    return str(value)


def deserialize_decimal(value: str) -> Decimal:
    if not isinstance(value, (str, int, float)):
        raise SerializationError(
            f"deserialize_decimal expects str/int/float, got {type(value).__name__}",
            details={"value": str(value), "type": type(value).__name__},
        )
    return Decimal(str(value))


def serialize_datetime(value: datetime) -> str:
    if not isinstance(value, datetime):
        raise SerializationError(
            f"serialize_datetime expects datetime, got {type(value).__name__}",
            details={"value": str(value), "type": type(value).__name__},
        )
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    utc_value = value.astimezone(UTC)
    return utc_value.strftime(ISO_FORMAT)


def deserialize_datetime(value: str) -> datetime:
    if not isinstance(value, str):
        raise SerializationError(
            f"deserialize_datetime expects str (ISO 8601), got {type(value).__name__}",
            details={"value": str(value), "type": type(value).__name__},
        )
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


_SERIALIZERS: dict[type, Any] = {
    Decimal: (serialize_decimal, deserialize_decimal),
    datetime: (serialize_datetime, deserialize_datetime),
}


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    for cls, (serializer, _) in _SERIALIZERS.items():
        if isinstance(value, cls):
            return serializer(value)
    if isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    if isinstance(value, (int, float, bool, str)):
        return value
    raise SerializationError(
        f"unsupported type for serialization: {type(value).__name__}",
        details={"value": str(value)[:200], "type": type(value).__name__},
    )


def _deserialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {k: _deserialize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deserialize_value(v) for v in value]
    if isinstance(value, (int, float, bool, str)):
        return value
    raise SerializationError(
        "deserialization without schema requires typed values. "
        "Use from_dict(value, model=YourModel) for Pydantic models, "
        "or explicit deserialize_decimal/deserialize_datetime for scalars.",
        details={"value": str(value)[:200], "type": type(value).__name__},
    )


def to_dict(obj: Any) -> dict[str, Any]:
    """将 Pydantic 模型或 dataclass 转换为确定性 dict。

    Decimal → str / datetime → ISO 8601 UTC / Enum → str(value)

    Args:
        obj: Pydantic BaseModel 实例 或 dataclass 实例。

    Returns:
        可 JSON 序列化的 dict——所有类型均已按 ENCODING_RULES 转换。

    Raises:
        SerializationError: 如果 obj 的类型无法序列化。
    """
    from pydantic import BaseModel

    if isinstance(obj, BaseModel):
        raw = obj.model_dump(mode="python")
    elif hasattr(obj, "__dict__"):
        raw = obj.__dict__.copy()
        if hasattr(obj, "__dataclass_fields__"):
            raw = {k: v for k, v in raw.items() if not k.startswith("_")}
    else:
        raise SerializationError(
            f"to_dict expects Pydantic BaseModel or dataclass, got {type(obj).__name__}",
            details={"type": type(obj).__name__},
        )

    return _serialize_value(raw)


def from_dict(
    data: dict[str, Any],
    *,
    model: type | None = None,
) -> dict[str, Any] | Any:
    """从确定性 dict 恢复为 Pydantic 模型实例或原生 dict。

    如果提供 model，则用 model(**deserialized_dict) 构造，Pydantic 会按字段类型自动还原。
    如果不提供 model，则返回 deserialized dict——5.147.8 修复: 原 docstring 声称
    "Decimal/str/datetime 已还原"与实现矛盾。实际 _deserialize_value 仅透传 str,
    不会调用 deserialize_decimal/deserialize_datetime 还原（无 schema 时无法可靠区分
    原始 str 与 datetime/Decimal 序列化后的 str, 强制转换会引入 false positive）。
    若需类型还原, 必须提供 model 参数让 Pydantic 按字段类型注解还原。

    Args:
        data: 由 to_dict() 产出的 dict。
        model: 可选的 Pydantic 模型类——如果提供则返回模型实例。

    Returns:
        反序列化后的 dict 或 Pydantic 模型实例。
    """
    from pydantic import BaseModel

    deserialized = _deserialize_value(data)
    if model is not None and issubclass(model, BaseModel):
        return model(**deserialized)
    return deserialized


def to_json(obj: Any, *, indent: int | None = None) -> str:
    """将对象序列化为确定性 JSON 字符串。

    Decimal → str / datetime → ISO 8601 UTC / Enum → str(value)

    Args:
        obj: Pydantic BaseModel 实例 或 dataclass 实例。
        indent: JSON 缩进空格数——None 为紧凑单行。

    Returns:
        确定性的 JSON 字符串。
    """
    d = to_dict(obj)
    return json.dumps(d, ensure_ascii=False, indent=indent, sort_keys=True, default=str)


def from_json(
    json_str: str,
    *,
    model: type | None = None,
) -> dict[str, Any] | Any:
    """从确定性 JSON 字符串恢复对象。

    Args:
        json_str: 由 to_json() 产出的 JSON 字符串。
        model: 可选的 Pydantic 模型类——如果提供则返回模型实例。

    Returns:
        反序列化后的 dict 或 Pydantic 模型实例。

    Raises:
        SerializationError: 当 raw 中含 _format_version 且与当前契约版本不匹配时。
    """
    raw = json.loads(json_str)
    if isinstance(raw, dict):
        raw_version = raw.get("_format_version")
        if raw_version is not None and raw_version != SerializationContract().format_version:
            raise SerializationError(
                f"format version mismatch: expected {SerializationContract().format_version}, got {raw_version}"
            )
    return from_dict(raw, model=model)


class SerializationError(Exception):
    """序列化/反序列化错误——版本不匹配或格式校验失败。"""


@dataclass(frozen=True)
class SerializationContract:
    """序列化契约文档——AI 可读的元数据描述。"""

    format_version: str = "1.0.0"
    rules: dict[str, str] = field(default_factory=lambda: dict(ENCODING_RULES))
    canonical_types: tuple[str, ...] = ("Decimal", "datetime", "str", "int", "float", "bool")
