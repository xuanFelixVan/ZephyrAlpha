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


_es_dir = _SRC / "zephyr" / "escalation_engine"

_ensure_pkg("zephyr.escalation_engine", _es_dir)

_load_mod("zephyr.escalation_engine.escalation_models", _es_dir / "escalation_models.py")
_load_mod("zephyr.escalation_engine.circuit_breaker", _es_dir / "circuit_breaker.py")
_load_mod("zephyr.escalation_engine.escalation_metrics", _es_dir / "escalation_metrics.py")
_load_mod("zephyr.escalation_engine.delegation_engine", _es_dir / "delegation_engine.py")

sys.modules.setdefault("zephyr.llm_security", MagicMock())
sys.modules.setdefault("zephyr.llm_security.gateway", MagicMock())

_load_mod("zephyr.escalation_engine.escalation_engine", _es_dir / "escalation_engine.py")
