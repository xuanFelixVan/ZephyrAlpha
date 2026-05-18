# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.agent_rbac.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —

import importlib.util
import sys
import types
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "src"
_ZEPHYR = _SRC_ROOT / "zephyr"


def _ensure_stub(name, pkg_path=None):
    if name in sys.modules:
        return sys.modules[name]
    mod = types.ModuleType(name)
    mod.__package__ = name
    if pkg_path:
        mod.__path__ = [str(pkg_path)]
    sys.modules[name] = mod
    return mod


def _load(name, file_path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(file_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_ensure_stub("zephyr", _ZEPHYR)
_ensure_stub("zephyr.shared", _ZEPHYR / "shared")
_ensure_stub("zephyr.shared.contracts", _ZEPHYR / "shared" / "contracts")
_ensure_stub("zephyr.shared.contracts.identity", _ZEPHYR / "shared" / "contracts" / "identity")
_ensure_stub("zephyr.agent_rbac", _ZEPHYR / "agent_rbac")

_load("zephyr.shared.contracts.identity.agent_identity", _ZEPHYR / "shared" / "contracts" / "identity" / "agent_identity.py")
_load("zephyr.shared.contracts.identity.permission", _ZEPHYR / "shared" / "contracts" / "identity" / "permission.py")
_load("zephyr.agent_rbac.immutable_core", _ZEPHYR / "agent_rbac" / "immutable_core.py")
_load("zephyr.agent_rbac.exceptions", _ZEPHYR / "agent_rbac" / "exceptions.py")
_load("zephyr.agent_rbac.kill_switch", _ZEPHYR / "agent_rbac" / "kill_switch.py")
_load("zephyr.agent_rbac.input_guard", _ZEPHYR / "agent_rbac" / "input_guard.py")
_load("zephyr.agent_rbac.sequence_guard", _ZEPHYR / "agent_rbac" / "sequence_guard.py")
_load("zephyr.agent_rbac.output_guard", _ZEPHYR / "agent_rbac" / "output_guard.py")
_load("zephyr.agent_rbac.abac_guard", _ZEPHYR / "agent_rbac" / "abac_guard.py")
_load("zephyr.agent_rbac.decision_explainer", _ZEPHYR / "agent_rbac" / "decision_explainer.py")
_load("zephyr.agent_rbac.rbac_guard", _ZEPHYR / "agent_rbac" / "rbac_guard.py")
_load("zephyr.agent_rbac.engine_degradation", _ZEPHYR / "agent_rbac" / "engine_degradation.py")
