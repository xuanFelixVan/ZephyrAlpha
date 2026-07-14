# [A_test] module_id: SRC-TST-1864 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-490 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.drift_detector.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

import importlib.util
import sys
import types
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parent.parent.parent / "src"
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
_ensure_stub("zephyr.drift_detector", _ZEPHYR / "gov_drift")

_load("zephyr.gov_drift.drift_models", _ZEPHYR / "gov_drift" / "drift_models.py")
_load("zephyr.gov_drift.drift_infrastructure", _ZEPHYR / "gov_drift" / "drift_infrastructure.py")
_load("zephyr.gov_drift.drift_engine", _ZEPHYR / "gov_drift" / "drift_engine.py")
_load("zephyr.gov_drift.baseline_manager", _ZEPHYR / "gov_drift" / "baseline_manager.py")
