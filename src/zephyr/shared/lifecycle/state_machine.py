# [BLUEPRINT] MOD-INF-038 | docs/03_modules/_domain_infrastructure_runtime/state_machine_engine/blueprint.md | §4
# [MODULE] zephyr.shared.lifecycle.state_machine
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-TASK_SYSTEM(task);MOD-INF-023(drift);MOD-INF-021(rollback);MOD-INF-019(skill);MOD-INF-025(a2a);MOD-INF-018(rbac);MOD-RESOURCE_OPTIMIZATION_ENGINE(resource);MOD-INF-015(telemetry);governance.drift_detection.state_machine;infrastructure_runtime_integration.auto_fix_engine.state_machine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 状态转换必须合法;转换守卫必须同步;命名冲突必须注册
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__; _state-machine-registry.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidTransitionError;TransitionGuardError;StateMachineRegistryError
# [TESTS] tests/test_state_machine.py
# [A_module] module_id=MOD-SHR_state_machine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StateMachine[S] — 通用状态机泛型基类 (MOD-INF-038)

全项目 11+ 状态机实例的统一基类。采用 DDD Value Object 组合模式：
  - 通用 StateMachine[S] 基类（本文件）
  - 各领域专用状态/转换定义（消费者模块）
  - 聚合根持有 StateMachine 实例

解决问题：
  - 4 处同名 InvalidTransitionError -> 统一为 zephyr.shared.state_machine.InvalidTransitionError
  - 2 处同名 SessionState -> 各领域独立命名空间
  - 11+ 零复用状态机实现 -> 统一基类

SSoT: MOD-INF-038 blueprint.md §4
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any, Generic, TypeVar

import yaml

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ConflictReport",
    "InvalidTransitionError",
    "SideEffect",
    "StateDefinition",
    "StateMachine",
    "StateMachineConfig",
    "StateMachineRegistry",
    "StateMachineRegistryError",
    "Transition",
    "TransitionGuard",
    "TransitionGuardError",
    "get_state_machine_registry",
]

logger = logging.getLogger(__name__)

S = TypeVar("S")

_REGISTRY_PATH = Path(__file__).parent / "_state-machine-registry.yaml"


class InvalidTransitionError(ZephyrBaseError):
    error_code = "ZA-SH-0027"

    def __init__(self, fsm_id: str, current: str, target: str, allowed: set[Any] | None = None, *, error_code: str | None = None):
        self.fsm_id = fsm_id
        self.current_state = current
        self.target_state = target
        self.allowed_transitions = allowed
        allowed_str = f" allowed: {allowed}" if allowed else ""
        super().__init__(f"[{fsm_id}] invalid transition: {current!r} -> {target!r}{allowed_str}")
        if error_code is not None:
            self.error_code = error_code


class TransitionGuardError(ZephyrBaseError):
    error_code = "ZA-SH-0028"

    def __init__(self, fsm_id: str, source: str, target: str, reason: str, *, error_code: str | None = None):
        self.fsm_id = fsm_id
        self.source_state = source
        self.target_state = target
        self.reason = reason
        super().__init__(f"[{fsm_id}] guard rejected: {source!r} -> {target!r}: {reason}")
        if error_code is not None:
            self.error_code = error_code


class StateMachineRegistryError(ZephyrBaseError):
    """状态机注册表错误。"""
    error_code = "ZA-SH-0029"


@dataclass(frozen=True)
class ConflictReport:
    name: str
    fsm_ids: list[str]
    conflict_type: str


@dataclass(frozen=True)
class StateDefinition(Generic[S]):
    state: S
    is_terminal: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Transition(Generic[S]):
    source: S
    target: S
    guard: TransitionGuard[S] | None = None
    side_effects: list[SideEffect[S]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class TransitionGuard(Generic[S]):
    def check(self, source: S, target: S, context: dict[str, Any] | None = None) -> bool:
        raise NotImplementedError


class SideEffect(Generic[S]):
    def on_enter(self, state: S, context: dict[str, Any] | None = None) -> None:
        pass

    def on_exit(self, state: S, context: dict[str, Any] | None = None) -> None:
        pass

    def on_transition(self, source: S, target: S, context: dict[str, Any] | None = None) -> None:
        pass


@dataclass
class StateMachineConfig(Generic[S]):
    fsm_id: str
    states: list[StateDefinition[S]]
    transitions: list[Transition[S]]
    initial: S
    owner_module: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        state_values = {sd.state for sd in self.states}
        if self.initial not in state_values:
            raise StateMachineRegistryError(f"[{self.fsm_id}] initial state {self.initial!r} not in defined states")
        for t in self.transitions:
            if t.source not in state_values:
                raise StateMachineRegistryError(f"[{self.fsm_id}] transition source not in defined states")  # noqa: MSG-EXPOSURE — source是状态机状态名非敏感信息
            if t.target not in state_values:
                raise StateMachineRegistryError(f"[{self.fsm_id}] transition target not in defined states")  # noqa: MSG-EXPOSURE — target是状态机状态名非敏感信息

    @property
    def state_names(self) -> set[str]:
        return {str(s.state) for s in self.states}

    @property
    def transition_map(self) -> dict[S, set[S]]:
        m: dict[S, set[S]] = {}
        for t in self.transitions:
            m.setdefault(t.source, set()).add(t.target)
        return m


class StateMachine(Generic[S]):
    def __init__(self, config: StateMachineConfig[S], initial: S | None = None) -> None:
        self._config = config
        self._current: S = initial if initial is not None else config.initial
        self._lock = RLock()
        self._history: list[tuple[S, S, dict[str, Any] | None]] = []
        self._side_effect_map: dict[tuple[S, S], list[SideEffect[S]]] = {}
        for t in config.transitions:
            key = (t.source, t.target)
            self._side_effect_map.setdefault(key, []).extend(t.side_effects)

    @property
    def fsm_id(self) -> str:
        return self._config.fsm_id

    @property
    def current_state(self) -> S:
        with self._lock:
            return self._current

    @property
    def config(self) -> StateMachineConfig[S]:
        return self._config

    @property
    def history(self) -> list[tuple[S, S, dict[str, Any] | None]]:
        with self._lock:
            return list(self._history)

    def can_transition(self, target: S) -> bool:
        with self._lock:
            allowed = self._config.transition_map.get(self._current, set())
            return target in allowed

    def can_transition_from(self, source: S, target: S) -> bool:
        allowed = self._config.transition_map.get(source, set())
        return target in allowed

    @property
    def available_transitions(self) -> list[S]:
        with self._lock:
            return list(self._config.transition_map.get(self._current, set()))

    def transition(self, target: S, context: dict[str, Any] | None = None) -> S:
        with self._lock:
            allowed = self._config.transition_map.get(self._current, set())
            if target not in allowed:
                raise InvalidTransitionError(self._config.fsm_id, self._current, target, allowed)
            key = (self._current, target)
            matching = [t for t in self._config.transitions if t.source == self._current and t.target == target]
            if matching and matching[0].guard is not None:
                if not matching[0].guard.check(self._current, target, context):
                    raise TransitionGuardError(self._config.fsm_id, self._current, target, "guard rejected")
            old = self._current
            effects = self._side_effect_map.get(key, [])
            for eff in effects:
                try:
                    eff.on_exit(old, context)
                except Exception as exc:
                    logger.error("[%s] on_exit error: %s", self._config.fsm_id, exc, exc_info=True)
            for eff in effects:
                try:
                    eff.on_transition(old, target, context)
                except Exception as exc:
                    logger.error("[%s] on_transition error: %s", self._config.fsm_id, exc, exc_info=True)
            self._current = target
            self._history.append((old, target, context))
            for eff in effects:
                try:
                    eff.on_enter(target, context)
                except Exception as exc:
                    logger.error("[%s] on_enter error: %s", self._config.fsm_id, exc, exc_info=True)
            logger.info("[%s] %s -> %s", self._config.fsm_id, old, target)
            return self._current

    def is_terminal(self) -> bool:
        with self._lock:
            for sd in self._config.states:
                if sd.state == self._current and sd.is_terminal:
                    return True
            return False

    def reset(self, initial: S | None = None) -> S:
        with self._lock:
            self._current = initial if initial is not None else self._config.initial
            self._history.clear()
            return self._current


class StateMachineRegistry:
    def __init__(self, registry_path: Path = _REGISTRY_PATH) -> None:
        self._configs: dict[str, StateMachineConfig[Any]] = {}
        self._registry_path = registry_path
        self._lock = RLock()
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        if not self._registry_path.exists():
            return
        try:
            with open(self._registry_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data or "state_machines" not in data:
                return
            for entry in data.get("state_machines", []):
                fsm_id = entry.get("fsm_id", "")
                if fsm_id:
                    self._configs[fsm_id] = entry
        except Exception as exc:
            logger.warning("Failed to load state machine registry: %s", exc, exc_info=True)

    def register(self, config: StateMachineConfig[Any]) -> str:
        with self._lock:
            if config.fsm_id in self._configs:
                existing = self._configs[config.fsm_id]
                if isinstance(existing, StateMachineConfig):
                    raise StateMachineRegistryError(f"Duplicate fsm_id: {config.fsm_id!r} already registered")
            self._configs[config.fsm_id] = config
            self._persist_entry(config)
            logger.info("Registered state machine: %s (owner: %s)", config.fsm_id, config.owner_module)
            return config.fsm_id

    def _persist_entry(self, config: StateMachineConfig[Any]) -> None:
        entry = {
            "fsm_id": config.fsm_id,
            "owner_module": config.owner_module,
            "states": [str(sd.state) for sd in config.states],
            "transitions": [{"source": str(t.source), "target": str(t.target)} for t in config.transitions],
            "initial": str(config.initial),
        }
        if not self._registry_path.exists():
            data: dict[str, Any] = {"state_machines": []}
        else:
            try:
                with open(self._registry_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {"state_machines": []}
            except Exception:
                data = {"state_machines": []}
        machines = data.setdefault("state_machines", [])
        machines.append(entry)
        tmp_path = f"{self._registry_path}.{id(self)}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            import os

            os.replace(tmp_path, str(self._registry_path))
        except PermissionError:
            try:
                import os

                os.remove(tmp_path)
            except OSError:
                pass
            raise

    def get(self, fsm_id: str) -> StateMachineConfig[Any]:
        with self._lock:
            if fsm_id not in self._configs:
                raise StateMachineRegistryError(f"State machine not found: {fsm_id!r}")
            return self._configs[fsm_id]

    def list_all(self) -> list[str]:
        with self._lock:
            return list(self._configs.keys())

    def detect_conflicts(self) -> list[ConflictReport]:
        with self._lock:
            configs = {k: v for k, v in self._configs.items() if isinstance(v, StateMachineConfig)}
            state_names: dict[str, list[str]] = {}
            for fsm_id, cfg in configs.items():
                for sn in cfg.state_names:
                    state_names.setdefault(sn, []).append(fsm_id)
            conflicts: list[ConflictReport] = []
            for name, fsm_ids in state_names.items():
                if len(fsm_ids) > 1:
                    conflicts.append(ConflictReport(name=name, fsm_ids=fsm_ids, conflict_type="state_name"))
            return conflicts


_registry: StateMachineRegistry | None = None


def get_state_machine_registry() -> StateMachineRegistry:
    global _registry
    if _registry is None:
        _registry = StateMachineRegistry()
    return _registry