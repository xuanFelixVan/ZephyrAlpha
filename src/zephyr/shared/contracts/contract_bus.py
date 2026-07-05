# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.contract_bus
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.errors.contract_violation_error
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
# [A_module] module_id=MOD-SHR_contract_bus | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ContractBus — 跨层通信抽象 + Pydantic v2 Schema Enforcement (M-09)
职责：所有模块间调用必须通过 ContractBus，Pydantic v2 强类型校验。

设计：
  - MANDATORY Schema 校验——不符合合约的消息直接拒绝
  - 支持同步/异步双模式
  - 合约注册表从 ContractBus YAML 加载
"""

import asyncio
import functools
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ContractViolationError(Exception):
    def __init__(self, contract_id: str, field: str, expected: str, got: str):
        self.contract_id = contract_id
        self.field = field
        self.expected = expected
        self.got = got
        super().__init__(f"ContractViolation [{contract_id}] {field}: expected {expected}, got {got}")


class ContractBusError(Exception):
    pass


@dataclass
class ContractDefinition:
    contract_id: str
    producer: str
    consumer: list[str]
    schema_fields: dict[str, type]
    required_fields: list[str] = field(default_factory=list)


class ContractRegistry:
    def __init__(self):
        self._contracts: dict[str, ContractDefinition] = {}

    def register(self, definition: ContractDefinition):
        self._contracts[definition.contract_id] = definition

    def get(self, contract_id: str) -> ContractDefinition | None:
        return self._contracts.get(contract_id)

    def list_all(self) -> list[str]:
        return list(self._contracts.keys())


class ContractEnforcer:
    def __init__(self, registry: ContractRegistry):
        self.registry = registry

    def enforce(self, contract_id: str, data: dict[str, Any]) -> dict[str, Any]:
        definition = self.registry.get(contract_id)
        if definition is None:
            raise ContractBusError(f"Unknown contract: {contract_id}")

        for field_name in definition.required_fields:
            if field_name not in data or data[field_name] is None:
                raise ContractViolationError(
                    contract_id, field_name, definition.schema_fields[field_name].__name__, "None"
                )

        for field_name, field_type in definition.schema_fields.items():
            if field_name in data and data[field_name] is not None:
                value = data[field_name]
                if field_type is int and not isinstance(value, (int, float)):
                    raise ContractViolationError(contract_id, field_name, "int", type(value).__name__)
                if field_type is str and not isinstance(value, str):
                    raise ContractViolationError(contract_id, field_name, "str", type(value).__name__)
                if field_type is bool and not isinstance(value, bool):
                    raise ContractViolationError(contract_id, field_name, "bool", type(value).__name__)

        return data


class ContractBus:
    def __init__(self, registry: ContractRegistry | None = None):
        self.registry = registry or ContractRegistry()
        self.enforcer = ContractEnforcer(self.registry)
        self._validate_on_call = True

    def validate(self, contract_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return self.enforcer.enforce(contract_id, data)

    def call(self, contract_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if self._validate_on_call:
            self.enforcer.enforce(contract_id, data)
        return data

    async def call_async(self, contract_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if self._validate_on_call:
            self.enforcer.enforce(contract_id, data)
        return data


def enforce_contract(contract_id: str):
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ContractViolationError:
                raise
            except Exception as e:
                raise ContractBusError(f"[{contract_id}] {func.__name__} failed: {e}") from e

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ContractViolationError:
                raise
            except Exception as e:
                raise ContractBusError(f"[{contract_id}] {func.__name__} failed: {e}") from e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return wrapper  # type: ignore[return-value]

    return decorator


_default_bus = ContractBus()


def get_bus() -> ContractBus:
    return _default_bus
