# [BLUEPRINT] MOD-TEST-492 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

_SRC = Path(__file__).resolve().parent.parent.parent.parent / "src"


def _ensure_pkg(name, path):
    if name not in sys.modules:
        m = types.ModuleType(name)
        m.__path__ = [str(path)]
        m.__package__ = name
        m.__file__ = str(path / "__init__.py")
        sys.modules[name] = m
    elif not hasattr(sys.modules[name], "__path__"):
        sys.modules[name].__path__ = [str(path)]


def _load_mod(name, file_path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(file_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_gov_dir = _SRC / "zephyr" / "governance"

_ensure_pkg("zephyr.infrastructure.escalation", _gov_dir)

_load_mod("zephyr.governance.escalation.escalation_models", _gov_dir / "escalation_models.py")
_load_mod("zephyr.governance.resilience_governance.circuit_breaker", _gov_dir / "circuit_breaker.py")
_load_mod("zephyr.governance.escalation.escalation_metrics", _gov_dir / "escalation_metrics.py")
_load_mod("zephyr.governance.intelligence_governance.delegation_engine", _gov_dir / "delegation_engine.py")

try:  # 仅真实包不可用时才占位，防止 MagicMock 无 __path__ 毒化跨目录批跑
    import zephyr.security.llm_defense.llm_security.gateway  # noqa: F401
except ImportError:
    sys.modules.setdefault("zephyr.security.llm_defense.llm_security", MagicMock())
    sys.modules.setdefault("zephyr.security.llm_defense.llm_security.gateway", MagicMock())

_load_mod("zephyr.governance.escalation.escalation_engine", _gov_dir / "escalation_engine.py")
