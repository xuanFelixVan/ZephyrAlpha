# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §chaos_hooks
# [MODULE] zephyr.trading.orchestrator.fault_tolerance.chaos_hooks
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.shared.contracts.orchestration_protocol
# [CONSUMERS] zephyr.trading.orchestrator.core.agent_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pre_step_hook MUST NOT block orchestrator execution; post_step_hook MUST recover all injected faults
# [MODIFY-GUARD] Adding hook behaviors MUST update ChaosHookPolicy
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ChaosHookError on hook execution failure
# [TESTS] tests/test_chaos_hooks.py
# [A_module] module_id=MOD-ORC_chaos_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ChaosHook — integrates ChaosEngine with the orchestrator execution loop."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from zephyr.shared.contracts.orchestration_protocol import ChaosEngineProtocol
from zephyr.trading.orchestrator.fault_tolerance.chaos_engine import ChaosEngine, FaultRecord
from zephyr.trading.orchestrator.fault_tolerance.fault_types import FaultTypeRegistry, get_default_registry

logger = logging.getLogger(__name__)

__all__: list[str] = [
    "ChaosHook",
    "ChaosHookError",
    "ChaosHookPolicy",
]


class ChaosHookError(RuntimeError):
    error_code = "ZA-TR-0014"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass
class ChaosHookPolicy:
    step_faults: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    enabled: bool = True

    def add_step_fault(
        self, step_name: str, fault_type: str, target: str, params: dict[str, Any] | None = None
    ) -> None:
        if step_name not in self.step_faults:
            self.step_faults[step_name] = []
        self.step_faults[step_name].append(
            {
                "fault_type": fault_type,
                "target": target,
                "params": params or {},
            }
        )


@dataclass
class HookContext:
    step_name: str
    step_data: dict[str, Any] = field(default_factory=dict)
    fault_records: list[FaultRecord] = field(default_factory=list)


class ChaosHook:
    def __init__(
        self,
        engine: ChaosEngineProtocol | None = None,
        registry: FaultTypeRegistry | None = None,
    ) -> None:
        self._engine = engine or ChaosEngine()
        self._registry = registry or get_default_registry()
        self._policy: ChaosHookPolicy = ChaosHookPolicy()
        self._active_step_faults: dict[str, list[FaultRecord]] = {}

    def configure(self, policy: ChaosHookPolicy) -> None:
        self._policy = policy
        logger.info("ChaosHook: configured with policy enabled=%s steps=%d", policy.enabled, len(policy.step_faults))

    def pre_step_hook(self, context: HookContext) -> HookContext:
        if not self._policy.enabled:
            return context

        step_faults = self._policy.step_faults.get(context.step_name, [])
        records: list[FaultRecord] = []

        for fault_spec in step_faults:
            fault_type = fault_spec["fault_type"]
            target = fault_spec["target"]
            params = fault_spec.get("params", {})

            try:
                handler = self._registry.get(fault_type)
                handler.inject(target, params)
                record = self._engine.fault_inject(target, fault_type, params)
                records.append(record)
                logger.info(
                    "ChaosHook: pre_step step=%s fault=%s target=%s fault_id=%s",
                    context.step_name,
                    fault_type,
                    target,
                    record.fault_id,
                )
            except Exception as exc:
                logger.error(
                    "ChaosHook: pre_step inject failed step=%s fault=%s: %s",
                    context.step_name,
                    fault_type,
                    exc, exc_info=True
                )

        context.fault_records = records
        self._active_step_faults[context.step_name] = records
        return context

    def post_step_hook(self, context: HookContext) -> HookContext:
        if not self._policy.enabled:
            return context

        records = self._active_step_faults.pop(context.step_name, context.fault_records)

        for record in records:
            try:
                handler = self._registry.get(record.fault_type)
                handler.recover(record.target, record.params)
                self._engine.recover(record.target)
                logger.info(
                    "ChaosHook: post_step recovered step=%s fault_id=%s target=%s",
                    context.step_name,
                    record.fault_id,
                    record.target,
                )
            except Exception as exc:
                logger.error(
                    "ChaosHook: post_step recover failed step=%s fault_id=%s: %s",
                    context.step_name,
                    record.fault_id,
                    exc, exc_info=True
                )

        context.fault_records = []
        return context

    def get_engine(self) -> ChaosEngineProtocol:
        return self._engine
