# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §3-§7
# [MODULE] zephyr.governance.rule_enforcement.check_types.check_type_registry
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.task_types; zephyr.governance.rule_enforcement.__init__
# [CONSUMERS] blueprint.md §0; zephyr.governance.rule_enforcement 内部模块; zephyr.trading.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MOD-GATE_ENGINE 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] GateError
# [TESTS] tests/gates/
# [A_module] module_id=MOD-GOV_check_type_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

CheckTypeHandler — CheckTypeHandler

依据: 蓝图 MOD-GATE_ENGINE §3-§7

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from zephyr.governance.rule_enforcement.task_types import Task

_REGISTRY: dict[str, type[CheckTypeHandler]] = {}


class CheckTypeHandler(ABC):
    name: str = ""

    @abstractmethod
    def run(
        self,
        task: Task,
        params: dict[str, Any],
        check: Any,
        project_root: Any,
    ) -> list[dict[str, Any]]: ...


def register_check_type(cls: type[CheckTypeHandler]) -> type[CheckTypeHandler]:
    _REGISTRY[cls.name] = cls

    return cls


def get_check_type(name: str) -> type[CheckTypeHandler] | None:
    return _REGISTRY.get(name)


def list_check_types() -> list[str]:
    return sorted(_REGISTRY.keys())


def _auto_import():
    import importlib
    import pkgutil

    from zephyr.governance.rule_enforcement import check_types as pkg

    for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):
        if modname.startswith("_"):
            continue
        importlib.import_module(f"zephyr.governance.rule_enforcement.check_types.{modname}")


_auto_import()

_STABILITY_FROZEN = True
_FROZEN_PUBLIC_API = frozenset(
    {
        "CheckTypeHandler",
        "register_check_type",
        "get_check_type",
        "list_check_types",
    }
)


def __getattr__(name: str):
    if name in _FROZEN_PUBLIC_API:
        import logging

        logging.getLogger("zephyr.stability_guard").warning(
            "STABILITY VIOLATION: Public API attribute '%s' removed from frozen module zephyr.governance.rule_enforcement.check_types.check_type_registry",
            name,
        )
    raise AttributeError(
        f"module 'zephyr.governance.rule_enforcement.check_types.check_type_registry' has no attribute {name!r}"
    )
