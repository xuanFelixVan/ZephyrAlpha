# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.serialization
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
serialization.py —— 统一序列化/反序列化基础设施（Phase 7 新增 | 盲点 B10 修复）

痛点修复：Pydantic 的 .model_dump() 能干活，但跨模块序列化契约未统一——
  1. Decimal -> str 还是 float？datetime -> ISO 8601 还是 POSIX timestamp？
  2. 每个消费者自己决定序列化格式 -> D_DATA->D_FACTOR->D_RESEARCH 管道中可能产生不同格式
  3. cross_layer_contracts.yaml 定了类型但没定序列化规则 -> 契约半成品

设计对标：
  - Google Proto canonical JSON mapping
  - OpenAPI Spec format keywords (date-time / decimal-as-string)
  - Stripe API 的 JSON 序列化一致性（Decimal "100.50" 从不裸输出 float）

设计原则：
  - 确定性序列化——同一对象同一输入 -> 永远同一输出
  - Decimal -> str (ISO 格式，保留精度) / datetime -> ISO 8601 with Z suffix (UTC)
  - 所有序列化/反序列化经过本模块 = SSoT
  - 零依赖第三方库——仅 Python 标准库 + decimal + datetime

AI 施工约定：
  - 任何跨层数据传输 MUST 使用 to_dict() / from_dict()——禁止裸 Pydantic .model_dump()
  - 外部 API 响应解析 MUST 使用 from_dict()——自动类型转换
  - 新的序列化规则追加到本文件的 ENCODING_RULES 字典

SSoT: MOD-INF-016 §2.9 shared-serialization
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: value 参数
#   fields: 参数 value，类型注解 Decimal
#   code: serialization.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: obj 参数
#   fields: 参数 obj，类型注解 object
#   code: serialization.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: data 参数
#   fields: 参数 data，类型注解 dict[str, Any]
#   code: serialization.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: model 参数
#   fields: 参数 model（无注解）
#   code: serialization.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① serialize_decimal
#   name_en: serialize_decimal
#   intro: serialize_decimal(value) 源码 L218-L224
#   desc: 源码 L218-L224
#   inputs: value
#   outputs: str
# - id: A2
#   name_zh: ② deserialize_decimal
#   name_en: deserialize_decimal
#   intro: deserialize_decimal(value) 源码 L227-L233
#   desc: 源码 L227-L233
#   inputs: value
#   outputs: Decimal
# - id: A3
#   name_zh: ③ serialize_datetime
#   name_en: serialize_datetime
#   intro: serialize_datetime(value) 源码 L236-L245
#   desc: 源码 L236-L245
#   inputs: value
#   outputs: str
# - id: A4
#   name_zh: ④ deserialize_datetime
#   name_en: deserialize_datetime
#   intro: deserialize_datetime(value) 源码 L248-L257
#   desc: 源码 L248-L257
#   inputs: value
#   outputs: datetime
# - id: A5
#   name_zh: ⑤ to_dict
#   name_en: to_dict
#   intro: 将 Pydantic 模型或 dataclass 转换为确定性 dict。
#   desc: 将 Pydantic 模型或 dataclass 转换为确定性 dict。 Decimal -> str / datetime -> ISO 8601 UTC / Enum ->…；源码 L303-L331
#   inputs: obj
#   outputs: dict[str, Any]
# - id: A6
#   name_zh: ⑥ from_dict
#   name_en: from_dict
#   intro: 从确定性 dict 恢复为 Pydantic 模型实例或原生 dict。
#   desc: 从确定性 dict 恢复为 Pydantic 模型实例或原生 dict。 如果提供 model，则用 model(**deserialized_dict) 构造，Pydantic…；源码 L334-L360
#   inputs: data model
#   outputs: dict[str, Any] | object
# - id: A7
#   name_zh: ⑦ to_json
#   name_en: to_json
#   intro: 将对象序列化为确定性 JSON 字符串。
#   desc: 将对象序列化为确定性 JSON 字符串。 Decimal -> str / datetime -> ISO 8601 UTC / Enum -> str(value) Args:…；源码 L363-L376
#   inputs: obj indent
#   outputs: str
# - id: A8
#   name_zh: ⑧ dumps
#   name_en: dumps
#   intro: 将任意对象序列化为确定性 JSON 字符串（5.147.4 SSoT）。
#   desc: 将任意对象序列化为确定性 JSON 字符串（5.147.4 SSoT）。 替代裸 ``json.dumps(obj, default=str)``——使用 ``_serializ…；源码 L379-L416
#   inputs: obj indent ensure_ascii sort_keys
#   outputs: str
# - id: A9
#   name_zh: ⑨ filter_dataclass_fields
#   name_en: filter_dataclass_fields
#   intro: 过滤 dict，仅保留目标类实际声明的字段（5.147.5 SSoT）。
#   desc: 过滤 dict，仅保留目标类实际声明的字段（5.147.5 SSoT）。 用于 ``_from_dict`` / ``**data`` 直接展开的版本兼容： 旧持久化数据中已删除…；源码 L419-L471
#   inputs: data
#   outputs: dict
# - id: A10
#   name_zh: ⑩ from_json
#   name_en: from_json
#   intro: 从确定性 JSON 字符串恢复对象。
#   desc: 从确定性 JSON 字符串恢复对象。 Args: json_str: 由 to_json() 产出的 JSON 字符串。 model: 可选的 Pydantic 模型类——如果提…；源码 L474-L498
#   inputs: json_str model
#   outputs: dict[str, Any] | object
#   （注：A10 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: Decimal
#   name_en: Decimal
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> A9
# A9 --> A10
# A10 --> O1
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum, unique
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ENCODING_RULES",
    "SerializationError",
    "SerializationFormat",
    "deserialize_datetime",
    "deserialize_decimal",
    "dumps",
    "filter_dataclass_fields",
    "from_dict",
    "from_json",
    "serialize_datetime",
    "serialize_decimal",
    "to_dict",
    "to_json",
]

ISO_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S.%fZ"


class SerializationError(ZephyrBaseError):
    """序列化/反序列化过程中类型不兼容或格式错误。"""

    error_code = "ZA-SH-0034"


@unique
class SerializationFormat(str, Enum):
    JSON = "json"
    DICT = "dict"


ENCODING_RULES: Final[dict[str, str]] = {
    "Decimal": "str(ISO-decimal)——例 Decimal('100.50') -> '100.50' 保留精度永不丢",
    "datetime": "ISO-8601 with Z suffix (UTC)——例 datetime(2026,5,5,12,0,0,tzinfo=UTC) -> '2026-05-05T12:00:00.000000Z'",
    "date": "ISO-8601 date only——例 date(2026,5,5) -> '2026-05-05'",
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


def _serialize_value(value: object) -> object:
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


def _deserialize_value(value: object) -> object:
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


def to_dict(obj: object) -> dict[str, Any]:
    """将 Pydantic 模型或 dataclass 转换为确定性 dict。

    Decimal -> str / datetime -> ISO 8601 UTC / Enum -> str(value)

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
) -> dict[str, Any] | object:
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


def to_json(obj: object, *, indent: int | None = None) -> str:
    """将对象序列化为确定性 JSON 字符串。

    Decimal -> str / datetime -> ISO 8601 UTC / Enum -> str(value)

    Args:
        obj: Pydantic BaseModel 实例 或 dataclass 实例。
        indent: JSON 缩进空格数——None 为紧凑单行。

    Returns:
        确定性的 JSON 字符串。
    """
    d = to_dict(obj)
    return json.dumps(d, ensure_ascii=False, indent=indent, sort_keys=True, default=str)


def dumps(
    obj: object,
    *,
    indent: int | None = None,
    ensure_ascii: bool = True,
    sort_keys: bool = False,
) -> str:
    """将任意对象序列化为确定性 JSON 字符串（5.147.4 SSoT）。

    替代裸 ``json.dumps(obj, default=str)``——使用 ``_serialize_value`` 正确处理
    datetime->ISO 8601 / Decimal->str / Enum->value，未知类型回退 ``str()`` 保持兼容。

    与 ``to_json`` 的区别：``to_json`` 要求 Pydantic/dataclass 输入，
    ``dumps`` 接受 dict/list/Any 原生对象。

    Args:
        obj: 任意可 JSON 序列化的对象（dict/list/datetime/Decimal/Enum/原生类型）。
        indent: JSON 缩进空格数——None 为紧凑单行。
        ensure_ascii: 是否转义非 ASCII 字符——False 保留中文等原样输出。
        sort_keys: 是否按 key 排序——True 用于确定性哈希/签名场景。

    Returns:
        JSON 字符串。
    """

    def _default(o: object) -> object:
        try:
            return _serialize_value(o)
        except SerializationError:
            return str(o)

    return json.dumps(
        obj,
        ensure_ascii=ensure_ascii,
        indent=indent,
        sort_keys=sort_keys,
        default=_default,
    )


def filter_dataclass_fields(cls: type, data: dict | None) -> dict:
    """过滤 dict，仅保留目标类实际声明的字段（5.147.5 SSoT）。

    用于 ``_from_dict`` / ``**data`` 直接展开的版本兼容：
    旧持久化数据中已删除/重命名的字段会被静默丢弃，避免 ``TypeError``；
    新增字段缺失时由 dataclass 默认值或 Pydantic 默认值兜底。

    支持两种类类型：
        - ``@dataclass`` 装饰的类（用 ``dataclasses.fields()``）
        - Pydantic ``BaseModel`` 子类（用 ``model_fields`` 属性，兼容 ``extra="forbid"``）

    Args:
        cls: 目标类类型（dataclass 或 Pydantic BaseModel 子类）。
        data: 原始 dict（来自 JSON/YAML/DB 反序列化）。``None`` 视为空 dict。

    Returns:
        过滤后的 dict——仅包含 ``cls`` 实际声明的字段名。
        多余键丢弃并记 debug 日志（通过 ``logging`` 模块）。
        若 ``cls`` 既非 dataclass 也非 Pydantic 模型，返回原数据副本（调用方自行处理）。
    """
    if not data:
        return {}

    valid_names: set[str] | None = None
    # 1. 尝试 dataclass
    try:
        from dataclasses import fields as _dc_fields

        valid_names = {f.name for f in _dc_fields(cls)}
    except TypeError:
        pass

    # 2. 尝试 Pydantic BaseModel
    if valid_names is None:
        model_fields = getattr(cls, "model_fields", None)
        if model_fields is not None:
            valid_names = set(model_fields.keys())

    # 3. 都不是，返回原数据
    if valid_names is None:
        return dict(data)

    filtered = {k: v for k, v in data.items() if k in valid_names}
    dropped = set(data.keys()) - valid_names
    if dropped:
        import logging

        logging.getLogger(__name__).debug(
            "filter_dataclass_fields: %s dropped unknown fields %s",
            getattr(cls, "__name__", cls),
            dropped,
        )
    return filtered


def from_json(
    json_str: str,
    *,
    model: type | None = None,
) -> dict[str, Any] | object:
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


# 注：此处曾有第二个 SerializationError(Exception, ZA-SH-0035) 重复定义遮蔽 L77 正确版
# （ZephyrBaseError, ZA-SH-0034），致全部 raise 点 TypeError——已删（#ARCH-089）


@dataclass(frozen=True)
class SerializationContract:
    """序列化契约文档——AI 可读的元数据描述。"""

    format_version: str = "1.0.0"
    rules: dict[str, str] = field(default_factory=lambda: dict(ENCODING_RULES))
    canonical_types: tuple[str, ...] = ("Decimal", "datetime", "str", "int", "float", "bool")
