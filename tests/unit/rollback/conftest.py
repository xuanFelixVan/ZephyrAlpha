# [A_test] module_id: SRC-TST-1936 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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


_rb_dir = _SRC / "zephyr" / "rollback"

_ensure_pkg("zephyr.rollback", _rb_dir)

_load_mod("zephyr.infrastructure.rollback.kill_switch", _rb_dir / "kill_switch.py")
_load_mod("zephyr.infrastructure.rollback.rollback_lock", _rb_dir / "rollback_lock.py")

sys.modules.setdefault("zephyr.infrastructure.rollback.sqlite_dumper", MagicMock())
sys.modules.setdefault("zephyr.governance.audit_trail", MagicMock())
sys.modules.setdefault("zephyr.governance.audit_trail.writer", MagicMock())

_load_mod("zephyr.infrastructure.rollback.rollback_executor", _rb_dir / "rollback_executor.py")
