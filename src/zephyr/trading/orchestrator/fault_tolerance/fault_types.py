# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §fault_types
# [MODULE] zephyr.trading.orchestrator.fault_tolerance.fault_types
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS] zephyr.trading.orchestrator.chaos_engine;zephyr.trading.orchestrator.chaos_hooks
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Registry entries MUST have inject()/recover() methods; preset templates are immutable
# [MODIFY-GUARD] Adding fault templates MUST register in FaultTypeRegistry
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] FaultTypeNotFoundError on unknown type lookup
# [TESTS] tests/test_fault_types.py
# [A_module] module_id=MOD-ORC_fault_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Fault type registry and preset templates for chaos engineering."""

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
    pass


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
