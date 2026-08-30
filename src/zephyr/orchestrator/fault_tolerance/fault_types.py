# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §fault_types
# [MODULE] zephyr.orchestrator.fault_tolerance.fault_types
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS] zephyr.orchestrator.chaos_engine;zephyr.orchestrator.chaos_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Registry entries MUST have inject()/recover() methods; preset templates are immutable
# [MODIFY-GUARD] Adding fault templates MUST register in FaultTypeRegistry
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FaultTypeNotFoundError on unknown type lookup
# [TESTS] tests/test_fault_types.py
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Fault type registry and preset templates for chaos engineering.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: fault_types.py
# 层: 算法
# - id: A1
#   name_zh: ① FaultHandler
#   name_en: FaultHandler
#   intro: class FaultHandler 源码 L135-L140
#   desc: 公共方法（定义序）: inject, recover；源码 L135-L140
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② FaultTypeRegistry
#   name_en: FaultTypeRegistry
#   intro: class FaultTypeRegistry 源码 L143-L162
#   desc: 公共方法（定义序）: register, get, list_types；源码 L143-L162
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ LatencyFault
#   name_en: LatencyFault
#   intro: class LatencyFault 源码 L165-L176
#   desc: 公共方法（定义序）: inject, recover；源码 L165-L176
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ ExceptionFault
#   name_en: ExceptionFault
#   intro: class ExceptionFault 源码 L179-L193
#   desc: 公共方法（定义序）: inject, recover；源码 L179-L193
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ ResourceExhaustionFault
#   name_en: ResourceExhaustionFault
#   intro: class ResourceExhaustionFault 源码 L196-L210
#   desc: 公共方法（定义序）: inject, recover；源码 L196-L210
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ NetworkPartitionFault
#   name_en: NetworkPartitionFault
#   intro: class NetworkPartitionFault 源码 L213-L227
#   desc: 公共方法（定义序）: inject, recover；源码 L213-L227
#   inputs: 无参数
#   outputs: 返回值
# - id: A7
#   name_zh: ⑦ DataCorruptionFault
#   name_en: DataCorruptionFault
#   intro: class DataCorruptionFault 源码 L230-L244
#   desc: 公共方法（定义序）: inject, recover；源码 L230-L244
#   inputs: 无参数
#   outputs: 返回值
# - id: A8
#   name_zh: ⑧ get_default_registry
#   name_en: get_default_registry
#   intro: get_default_registry() 源码 L251-L264
#   desc: 源码 L251-L264
#   inputs: 无参数
#   outputs: FaultTypeRegistry
#   （注：A8 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: FaultTypeRegistry
#   name_en: FaultTypeRegistry
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.orchestrator.chaos_engine;zephyr.orchestrator.chaos_hooks
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> A7
# A7 --> A8
# A8 --> O1
"""

from __future__ import annotations

import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "DataCorruptionFault",
    "ExceptionFault",
    "FaultTypeNotFoundError",
    "FaultTypeRegistry",
    "LatencyFault",
    "NetworkPartitionFault",
    "ResourceExhaustionFault",
]


class FaultTypeNotFoundError(KeyError):
    error_code = "ZA-TR-0013"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class FaultHandler(ABC):
    @abstractmethod
    def inject(self, target: str, params: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def recover(self, target: str, params: dict[str, Any]) -> dict[str, Any]: ...


class FaultTypeRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, FaultHandler] = {}
        self._lock = threading.Lock()

    def register(self, name: str, handler: FaultHandler) -> None:
        with self._lock:
            self._handlers[name] = handler
        logger.info("FaultTypeRegistry: registered handler for '%s'", name)

    def get(self, name: str) -> FaultHandler:
        with self._lock:
            handler = self._handlers.get(name)
        if handler is None:
            raise FaultTypeNotFoundError(name)
        return handler

    def list_types(self) -> list[str]:
        with self._lock:
            return sorted(self._handlers.keys())


class LatencyFault(FaultHandler):
    def inject(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        delay_ms = params.get("delay_ms", 500)
        jitter_ms = params.get("jitter_ms", 0)
        actual_delay = delay_ms + (jitter_ms * (0.5 if jitter_ms else 0))
        time.sleep(actual_delay / 1000.0)
        logger.info("LatencyFault: injected %dms delay on %s", int(actual_delay), target)
        return {"target": target, "delay_ms": int(actual_delay), "injected": True}

    def recover(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        logger.info("LatencyFault: recovered on %s", target)
        return {"target": target, "recovered": True}


class ExceptionFault(FaultHandler):
    def inject(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        exception_type = params.get("exception_type", "RuntimeError")
        message = params.get("message", "Chaos-injected exception")
        logger.info("ExceptionFault: injected %s on %s: %s", exception_type, target, message)
        return {
            "target": target,
            "exception_type": exception_type,
            "message": message,
            "injected": True,
        }

    def recover(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        logger.info("ExceptionFault: recovered on %s", target)
        return {"target": target, "recovered": True}


class ResourceExhaustionFault(FaultHandler):
    def inject(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        resource_type = params.get("resource_type", "memory")
        limit = params.get("limit", "80%")
        logger.info("ResourceExhaustionFault: injected on %s resource=%s limit=%s", target, resource_type, limit)
        return {
            "target": target,
            "resource_type": resource_type,
            "limit": limit,
            "injected": True,
        }

    def recover(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        logger.info("ResourceExhaustionFault: recovered on %s", target)
        return {"target": target, "recovered": True}


class NetworkPartitionFault(FaultHandler):
    def inject(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        partition_type = params.get("partition_type", "complete")
        affected_nodes = params.get("affected_nodes", [])
        logger.info("NetworkPartitionFault: injected on %s type=%s nodes=%s", target, partition_type, affected_nodes)
        return {
            "target": target,
            "partition_type": partition_type,
            "affected_nodes": affected_nodes,
            "injected": True,
        }

    def recover(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        logger.info("NetworkPartitionFault: recovered on %s", target)
        return {"target": target, "recovered": True}


class DataCorruptionFault(FaultHandler):
    def inject(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        corruption_rate = params.get("corruption_rate", 0.1)
        corruption_type = params.get("corruption_type", "bit_flip")
        logger.info("DataCorruptionFault: injected on %s rate=%.2f type=%s", target, corruption_rate, corruption_type)
        return {
            "target": target,
            "corruption_rate": corruption_rate,
            "corruption_type": corruption_type,
            "injected": True,
        }

    def recover(self, target: str, params: dict[str, Any]) -> dict[str, Any]:
        logger.info("DataCorruptionFault: recovered on %s", target)
        return {"target": target, "recovered": True}


_DEFAULT_REGISTRY: FaultTypeRegistry | None = None
_DEFAULT_REGISTRY_LOCK = threading.Lock()


def get_default_registry() -> FaultTypeRegistry:
    global _DEFAULT_REGISTRY
    # 5.16.3 修复：加锁防止并发创建多实例+多次注册
    if _DEFAULT_REGISTRY is None:
        with _DEFAULT_REGISTRY_LOCK:
            if _DEFAULT_REGISTRY is None:
                _DEFAULT_REGISTRY = FaultTypeRegistry()
                _DEFAULT_REGISTRY.register("latency", LatencyFault())
                _DEFAULT_REGISTRY.register("exception", ExceptionFault())
                _DEFAULT_REGISTRY.register("error", ExceptionFault())
                _DEFAULT_REGISTRY.register("resource_exhaustion", ResourceExhaustionFault())
                _DEFAULT_REGISTRY.register("network_partition", NetworkPartitionFault())
                _DEFAULT_REGISTRY.register("data_corruption", DataCorruptionFault())
    return _DEFAULT_REGISTRY
