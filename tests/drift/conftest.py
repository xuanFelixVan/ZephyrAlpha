# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-490 | docs/03_modules/_domain_governance/blueprint.md | §
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
# 治本（AI-AUDIT12）：删除 zephyr.shared.contracts.identity 空 stub——该 stub 无
# __spec__（types.ModuleType 裸对象），同进程后续真实导入链（如 drift_hotfix_bypass →
# shared.contracts.__init__ → from ...identity import AgentIdentity）命中此 stub 即
# ImportError "unknown location"，导致 test_drift_hotfix_bypass / test_audit_spec_auditor
# 收集期爆雷。identity 真实包可正常导入，无需 stub（实证：单独 import OK）。
_ensure_stub("zephyr.drift_detector", _ZEPHYR / "gov_drift")

_load("zephyr.gov_drift.drift_models", _ZEPHYR / "gov_drift" / "drift_models.py")
_load("zephyr.gov_drift.drift_infrastructure", _ZEPHYR / "gov_drift" / "drift_infrastructure.py")
_load("zephyr.gov_drift.drift_engine", _ZEPHYR / "gov_drift" / "drift_engine.py")
_load("zephyr.gov_drift.baseline_manager", _ZEPHYR / "gov_drift" / "baseline_manager.py")
