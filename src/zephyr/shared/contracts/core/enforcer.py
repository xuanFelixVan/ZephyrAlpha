# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.enforcer
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] governance.rule_enforcement.invariants.en_003_contract_compatibility
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_enforcer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ZephyrAlpha — shared/contracts/enforcer.py

CTR-ERR-006: ContractEnforcer / 运行时契约强制执行

提供装饰器，在层边界校验数据是否符合跨层数据契约（CTR）。
实现 CTR-VER-001 版本协商规则的运行时部分。

.. deprecated-reserved::
    本模块提供的装饰器（enforce_output / enforce_input / enforce）已实现但
    **尚未在生产代码中部署**（AUDIT-07 P1-2 确认零使用）。当前保留为架构预留，
    待跨层数据契约强制执行机制正式启用时再部署到层边界函数上。

设计原则
--------
- 装饰器模式：零侵入，不改现有代码
- 优先 isinstance 检查（快速路径）
- 回退到字段级校验（完整路径）
- 与 TraceContext（CTR-TRACE-001）集成

用法
----
    from zephyr.shared.contracts.core.enforcer import enforce_output, enforce_input
    from zephyr.trading.trading_contracts.market.market_data import NormalizedMarketData

    @enforce_output(NormalizedMarketData, trace_required=True)
    def on_market_data(raw: dict) -> NormalizedMarketData:
        ...

    @enforce_input(NormalizedMarketData, param_name="data")
    def compute_factor(data: NormalizedMarketData) -> FactorSignal:
        ...

SSoT: cross_layer_contracts.yaml -> CTR-ERR-006
"""

from __future__ import annotations

import dataclasses
import functools
import inspect
import logging
import sys
import types
import typing
import uuid
from collections.abc import Callable
from dataclasses import is_dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError

F = TypeVar("F", bound=Callable[..., Any])

_logger = logging.getLogger("zephyr.shared.contracts.enforcer")


class EnforcementMode(str, Enum):
    STRICT = "strict"
    WARN = "warn"


class ContractViolationError(TypeError):
    """CTR-ERR-006: 运行时跨层数据契约校验失败。

    属性
    ----
    error_id : str
        错误唯一 ID（UUID）
    contract_id : str
        被违反的契约名称
    violation_type : str
        违规类型
    detail : str
        详细描述
    """
    error_code = "ZA-SH-0022"

    def __init__(
        self,
        contract_id: str,
        violation_type: str,
        detail: str,
        field_name: str | None = None,
        expected_type: str | None = None,
        actual_type: str | None = None,
        *,
        error_code: str | None = None,
    ) -> None:
        self.error_id = str(uuid.uuid4())
        self.contract_id = contract_id
        self.violation_type = violation_type
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.detail = detail
        self.timestamp = datetime.now(UTC)

        msg_parts = [f"[{violation_type}] {contract_id}"]
        if field_name:
            msg_parts.append(f"  field={field_name}")
        if expected_type and actual_type:
            msg_parts.append(f"  expected={expected_type}, actual={actual_type}")
        msg_parts.append(f"  {detail}")
        super().__init__("\n".join(msg_parts))
        if error_code is not None:
            self.error_code = error_code


def enforce_output(
    contract_type: type[Any],
    mode: EnforcementMode = EnforcementMode.STRICT,
    trace_required: bool = False,
) -> Callable[[F], F]:
    """装饰器——校验函数返回值是否符合指定契约类型。

    参数
    ----
    contract_type : type
        契约类型：frozen dataclass，或 Pydantic v2 BaseModel（如 Task）
    mode : EnforcementMode
        STRICT = 抛出 ContractViolationError
        WARN   = 记录 warning 日志，继续执行
    trace_required : bool
        如果为 True，返回值必须包含非空的 trace_context 字段
    """

    contract_name = getattr(contract_type, "__name__", str(contract_type))

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if result is None:
                return result

            violations = _validate_value(result, contract_type, contract_name, trace_required)

            if violations:
                report = _format_violations(contract_name, func.__qualname__, violations)
                if mode is EnforcementMode.STRICT:
                    raise ContractViolationError(
                        contract_id=contract_name,
                        violation_type="output_contract_violation",
                        detail=report,
                    )
                else:
                    _logger.warning(
                        "[ContractEnforcer:WARN] %s.%s -> %s",
                        contract_name,
                        func.__qualname__,
                        report,
                    )

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def enforce_input(
    contract_type: type[Any],
    param_name: str | None = None,
    mode: EnforcementMode = EnforcementMode.STRICT,
    trace_required: bool = False,
) -> Callable[[F], F]:
    """装饰器——校验函数入参是否符合指定契约类型。

    参数
    ----
    contract_type : type
        契约类型：dataclass 或 Pydantic BaseModel 子类
    param_name : str or None
        要校验的参数名。为 None 时自动取第一个匹配 contract_type 的参数。
    mode : EnforcementMode
        STRICT / WARN
    trace_required : bool
        如果为 True，入参必须包含非空的 trace_context
    """

    contract_name = getattr(contract_type, "__name__", str(contract_type))

    def decorator(func: F) -> F:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            target_name = param_name
            if target_name is None:
                target_name = _find_param_by_type(bound.arguments, contract_type, sig)

            if target_name is None:
                _logger.debug(
                    "[ContractEnforcer] %s: 未找到类型为 %s 的入参，跳过校验",
                    func.__qualname__,
                    contract_name,
                )
                return func(*args, **kwargs)

            if target_name not in bound.arguments:
                _logger.debug(
                    "[ContractEnforcer] %s: 参数 '%s' 未在调用中传递，跳过校验",
                    func.__qualname__,
                    target_name,
                )
                return func(*args, **kwargs)

            value = bound.arguments[target_name]

            if value is None:
                return func(*args, **kwargs)

            violations = _validate_value(value, contract_type, contract_name, trace_required)

            if violations:
                report = _format_violations(contract_name, func.__qualname__, violations)
                if mode is EnforcementMode.STRICT:
                    raise ContractViolationError(
                        contract_id=contract_name,
                        violation_type="input_contract_violation",
                        detail=f"param '{target_name}': {report}",
                    )
                else:
                    _logger.warning(
                        "[ContractEnforcer:WARN] %s.%s param=%s -> %s",
                        contract_name,
                        func.__qualname__,
                        target_name,
                        report,
                    )

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def enforce(
    contract_type: type[Any],
    input_param: str | None = None,
    mode: EnforcementMode = EnforcementMode.STRICT,
    trace_required: bool = False,
) -> Callable[[F], F]:
    """组合装饰器——同时校验入参和返回值。

    等效于 @enforce_input + @enforce_output 的组合。
    enforce_input 在外层，确保入参校验先于返回值校验执行。
    """

    def decorator(func: F) -> F:
        fn = enforce_output(contract_type, mode, trace_required)(func)
        fn = enforce_input(contract_type, input_param, mode, trace_required)(fn)
        return fn

    return decorator


def _validate_value(
    value: Any,
    contract_type: type[Any],
    contract_name: str,
    trace_required: bool,
) -> list[str]:
    """校验单个值是否符合契约定义。返回违规描述列表（空列表 = 通过）。"""

    violations: list[str] = []

    if inspect.isclass(contract_type) and issubclass(contract_type, PydanticBaseModel):
        if not isinstance(value, contract_type):
            violations.append(
                f"类型不匹配: 期望 {contract_name} 或其子类，实际收到 {type(value).__qualname__}",
            )
            return violations
        try:
            contract_type.model_validate(value.model_dump(mode="python"))
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(x) for x in err.get("loc", ()))
                violations.append(f"Pydantic [{loc}]: {err.get('msg')}")
        if trace_required:
            trace_ctx = _get_trace_context(value)
            if trace_ctx is None:
                violations.append("缺少 TraceContext: CTR-TRACE-001 强制要求非空 trace_context 字段")
        return violations

    if not isinstance(value, contract_type):
        actual_type_name = type(value).__qualname__
        violations.append(f"类型不匹配: 期望 {contract_name} 或其子类，实际收到 {actual_type_name}")
        return violations

    if is_dataclass(contract_type):
        _validate_dataclass_fields(value, contract_type, violations)

    if trace_required:
        trace_ctx = _get_trace_context(value)
        if trace_ctx is None:
            violations.append("缺少 TraceContext: CTR-TRACE-001 强制要求非空 trace_context 字段")

    if is_dataclass(contract_type):
        is_frozen = getattr(contract_type, "__dataclass_params__", None)
        if is_frozen and is_frozen.frozen if hasattr(is_frozen, "frozen") else False:
            _check_deep_mutable_nesting(value, contract_type, violations)

    return violations


def _validate_dataclass_fields(
    value: Any,
    contract_type: type[Any],
    violations: list[str],
) -> None:
    """校验 dataclass 字段的类型和必填性。"""

    try:
        fields = dataclasses.fields(contract_type)
    except TypeError:
        return

    type_hints = _resolve_type_hints(contract_type)

    for fld in fields:
        field_value = getattr(value, fld.name, dataclasses.MISSING)

        if field_value is dataclasses.MISSING and _is_required(fld):
            violations.append(f"缺少必填字段 '{fld.name}'")
            continue

        declared_type = type_hints.get(fld.name)
        if field_value is not None and declared_type is not None:
            _check_field_type(fld.name, field_value, declared_type, violations)


def _resolve_type_hints(contract_type: type[Any]) -> dict[str, Any]:
    """解析 dataclass 的类型注解（处理 PEP 563 字符串注解）。"""

    try:
        module = sys.modules.get(contract_type.__module__)
        globalns = getattr(module, "__dict__", {}) if module else {}
        return typing.get_type_hints(contract_type, globalns=globalns, include_extras=False)
    except Exception as e:
        _logger.warning("suppressed error in enforcer", exc_info=True)

    hints: dict[str, Any] = {}
    try:
        module = sys.modules.get(contract_type.__module__)
        globalns = getattr(module, "__dict__", {}) if module else {}
    except Exception:
        globalns = {}

    for fld in dataclasses.fields(contract_type):
        ftype = fld.type
        if isinstance(ftype, str):
            try:
                # 5.45.2 修复：使用 typing._eval_type 替代 eval() 解析字符串类型注解
                # typing._eval_type 仅处理类型表达式，不会执行任意代码
                hints[fld.name] = typing._eval_type(
                    typing.ForwardRef(ftype), globalns, None
                )
            except Exception:
                hints[fld.name] = ftype
        else:
            hints[fld.name] = ftype
    return hints


def _check_field_type(
    field_name: str,
    value: Any,
    declared_type: Any,
    violations: list[str],
) -> None:
    """检查字段值的类型是否匹配声明类型。"""

    origin = get_origin(declared_type)
    args = get_args(declared_type)

    origin_type = origin or declared_type

    if isinstance(origin_type, type) and origin_type is not type(None):
        if origin_type is not types.UnionType and not isinstance(value, origin_type):
            violations.append(
                f"字段 '{field_name}' 类型不匹配: 期望 {origin_type.__name__}, 实际 {type(value).__name__}"
            )
            return

    if origin is Union or origin is types.UnionType:
        if len(args) == 2 and type(None) in args:
            # 5.109.1 修复：next() 提供 default=None 防御 StopIteration（当前由上方守卫保护，但守卫若被重构将暴露缺陷）
            non_none = next((a for a in args if a is not type(None)), None)
            if value is not None:
                _check_field_type(field_name, value, non_none, violations)


def _is_required(fld: dataclasses.Field) -> bool:
    """判断 dataclass 字段是否必填（无默认值且非 Optional 包裹）。"""

    if fld.default is not dataclasses.MISSING:
        return False
    if fld.default_factory is not dataclasses.MISSING:
        return False

    origin = get_origin(fld.type)
    if origin is Union or origin is types.UnionType:
        args = get_args(fld.type)
        if type(None) in args:
            return False

    return True


def _get_trace_context(value: Any) -> Any | None:
    """从数据对象中提取 trace_context 字段。"""

    try:
        return getattr(value, "trace_context", None)
    except Exception:
        return None


def _check_deep_mutable_nesting(
    value: Any,
    contract_type: type[Any],
    violations: list[str],
) -> None:
    """检测 frozen dataclass 中的可变容器字段（浅层不可变性陷阱）。

    仅检查 Dict/List/Set 作为容器时的情况，不检查其内容是否可变——
    那是运行时 ContractEnforcer 的职责。此检查提供静态阶段的告警。
    """

    mutable_types = {dict, list, set, dict, list}

    try:
        fields = dataclasses.fields(contract_type)
    except TypeError:
        return

    type_hints = _resolve_type_hints(contract_type)
    mutable_container_fields: list[str] = []

    for fld in fields:
        declared_type = type_hints.get(fld.name)
        if declared_type is None:
            continue

        origin = get_origin(declared_type)
        base = origin if origin is not None else declared_type
        if base in mutable_types or (hasattr(base, "__origin__") and base.__origin__ in mutable_types):
            mutable_container_fields.append(fld.name)

    if mutable_container_fields:
        violations.append(
            "浅层不可变性警告: frozen dataclass 包含可变容器字段 "
            f"({', '.join(mutable_container_fields)})——"
            "跨层传递时建议做 deep copy 防护，防止下游意外修改嵌套容器"
        )


def _find_param_by_type(
    arguments: dict[str, Any],
    contract_type: type[Any],
    sig: inspect.Signature | None = None,
) -> str | None:
    """在函数参数中找到 contract_type 对应的参数名。

    优先级：
    1. isinstance 匹配（运行时类型）
    2. 注解匹配（声明类型，处理 PEP 563 字符串注解）
    """

    for name, val in arguments.items():
        if isinstance(val, contract_type):
            return name

    if sig is not None:
        contract_name = getattr(contract_type, "__name__", str(contract_type))
        for name, param in sig.parameters.items():
            if param.annotation is not inspect.Parameter.empty:
                anno = param.annotation
                if isinstance(anno, str):
                    if contract_name in anno or anno.replace(" | None", "").strip() == contract_name:
                        return name
                elif inspect.isclass(anno) and inspect.isclass(contract_type):
                    try:
                        if issubclass(anno, contract_type):
                            return name
                    except TypeError:
                        pass
                else:
                    origin = get_origin(anno)
                    if origin is not None:
                        args = get_args(anno)
                        if contract_type in args or contract_type is origin:
                            return name
                    if origin is Union or origin is types.UnionType:
                        args = get_args(anno)
                        if contract_type in args:
                            return name

    return None


def _format_violations(
    contract_name: str,
    func_name: str,
    violations: list[str],
) -> str:
    """格式化违规报告。"""

    lines = [f"{contract_name} 校验失败 @ {func_name} ({len(violations)} 条违规):"]
    for i, v in enumerate(violations, 1):
        lines.append(f"  [{i}] {v}")
    return "\n".join(lines)
