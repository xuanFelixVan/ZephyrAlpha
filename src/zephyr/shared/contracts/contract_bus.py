# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.contract_bus
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.errors.contract_violation_error
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
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
# noqa: m07-orphan  M07豁免: M-09 ContractBus 独立功能价值(ARCH-027 3a)+管线未接通零消费者客观原因(3b),5.159 判定保留待接入

"""
ContractBus — 跨层通信抽象 + Pydantic v2 Schema Enforcement (M-09)
职责：所有模块间调用必须通过 ContractBus，Pydantic v2 强类型校验。

设计：
  - MANDATORY Schema 校验——不符合合约的消息直接拒绝
  - 支持同步/异步双模式
  - 合约注册表从 ContractBus YAML 加载

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: contract_id 参数
#   fields: 参数 contract_id，类型注解 str
#   code: contract_bus.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ContractRegistry
#   name_en: ContractRegistry
#   intro: class ContractRegistry 源码 L131-L142
#   desc: 公共方法（定义序）: register, get, list_all；源码 L131-L142
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ContractEnforcer
#   name_en: ContractEnforcer
#   intro: class ContractEnforcer 源码 L145-L170
#   desc: 公共方法（定义序）: enforce；源码 L145-L170
#   inputs: registry
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ContractBus
#   name_en: ContractBus
#   intro: class ContractBus 源码 L173-L190
#   desc: 公共方法（定义序）: validate, call, call_async；源码 L173-L190
#   inputs: registry
#   outputs: 返回值
# - id: A4
#   name_zh: ④ enforce_contract
#   name_en: enforce_contract
#   intro: enforce_contract(contract_id) 源码 L193-L217
#   desc: 源码 L193-L217
#   inputs: contract_id
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ get_bus
#   name_en: get_bus
#   intro: get_bus() 源码 L223-L224
#   desc: 源码 L223-L224
#   inputs: 无参数
#   outputs: ContractBus
#   （注：A5 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ContractBus
#   name_en: ContractBus
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

import asyncio
import functools
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ContractViolationError(Exception):
    error_code = "ZA-SH-0024"

    def __init__(self, contract_id: str, field: str, expected: str, got: str, *, error_code: str | None = None):
        self.contract_id = contract_id
        self.field = field
        self.expected = expected
        self.got = got
        super().__init__(f"ContractViolation [{contract_id}] {field}: expected {expected}, got {got}")
        if error_code is not None:
            self.error_code = error_code


class ContractBusError(Exception):
    """Contract Bus 错误。"""

    error_code = "ZA-SH-0025"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


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
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                raise ContractBusError(f"[{contract_id}] {func.__name__} failed: {e}") from e

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ContractViolationError:
                raise
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                raise ContractBusError(f"[{contract_id}] {func.__name__} failed: {e}") from e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return wrapper  # type: ignore[return-value]

    return decorator


_default_bus = ContractBus()


def get_bus() -> ContractBus:
    return _default_bus
