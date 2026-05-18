# [BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

# [MODULE] zephyr.gates.check_types.check_type_registry

# [INVARIANTS] MOD-INF-007 门禁 exit code 不可伪造; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; _registry.yaml; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.gates 内部模块; zephyr.orchestrator

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] GateError

# [TESTS] tests/gates/

"""[BLUEPRINT] MOD-INF-007 | docs/03_modules/_cross_layer/gate-engine/blueprint.md | §3-§7

CheckTypeHandler — CheckTypeHandler

依据: 蓝图 MOD-INF-007 §3-§7

"""






from __future__ import annotations





from abc import ABC, abstractmethod


from typing import Any





from zephyr.gates.task_types import Task





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


    ) -> list[dict[str, Any]]:


        ...








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


    from zephyr.gates import check_types as pkg





    for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):


        if modname.startswith("_"):


            continue


        importlib.import_module(f"zephyr.gates.check_types.{modname}")








_auto_import()


