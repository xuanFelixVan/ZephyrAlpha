# [BLUEPRINT] MOD-INF-002 | 03_modules/l01_infrastructure/runtime-integration/blueprint.md | §
"""
ZephyrAlpha 核心包索引 + 模块懒加载器 (M-04)

C 轨 — 14 层业务脊柱 | B 轨 — 10 横切平台能力

快速导入参考：
  核心数据模型:    from zephyr.shared.schemas import Task, TaskStatus
  门禁检查:        from zephyr.gates import gate_engine
  上下文构建:      from zephyr.context_engine import intent_parser
  向量记忆服务:    from zephyr.vector_memory import InProcessVectorMemory
"""
import importlib
import sys
from pathlib import Path
from typing import Any, Optional

def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        parsed: dict[str, str] = {}
        with env_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if value:
                    parsed[key] = value
        import os
        for k, v in parsed.items():
            os.environ.setdefault(k, v)

_load_dotenv()

_lazy_registry: dict[str, str] = {}

_version_ = "4.6.0"


def register_lazy(name: str, module_path: str):
    _lazy_registry[name] = module_path


class _LazyModule:
    """延迟加载代理——首次访问时才加载实际模块 (M-04)"""

    def __init__(self, module_path: str):
        self._module_path = module_path
        self._module: Any = None

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._module_path)

    def __getattr__(self, name: str) -> Any:
        self._load()
        return getattr(self._module, name)

    def __dir__(self):
        self._load()
        return dir(self._module)


def __getattr__(name: str) -> Any:
    """包级懒加载入口点——PEP 562 模块级 __getattr__ (M-04)"""
    if name in _lazy_registry:
        module_path = _lazy_registry[name]
        proxy = _LazyModule(module_path)
        setattr(sys.modules[__name__], name, proxy)
        return proxy
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    return sorted(set(dir(type(__name__))) | set(_lazy_registry.keys()))


# ── 全自动遥测注入（MOD-INF-015 v0.9.0 · auto_bootstrap）─────────────────
# import zephyr 时自动执行——SessionContinuity + PhaseManager + BlueprintMetrics
# 全面 monkey-patch，零手动代码。try/except 保活——patch 失败不阻塞 import。
try:
    from zephyr.l01_infrastructure.system_telemetry.auto_bootstrap import bootstrap as _auto_bootstrap
    _auto_bootstrap_result = _auto_bootstrap()
except Exception:
    _auto_bootstrap_result = None

# ── 模块懒加载注册（M-04 · PEP 562 __getattr__）───────────────────────────
register_lazy("vector_memory", "zephyr.vector_memory")  # MOD-INF-011 VMS
register_lazy("llm_security", "zephyr.llm_security")    # MOD-INF-014 LSG — L0-L8 nine-layer defense
register_lazy("_cross_layer", "zephyr._cross_layer")    # MOD-INF-010 FLE cross-layer pipelines (AlphaSignal + MLExperiment)
register_lazy("contract_registry", "zephyr.orchestrator.contract_registry")  # MOD-MASTER-001 CT-* contract registry
register_lazy("truth_source", "zephyr.gates.truth_source_validator")  # MOD-MASTER-001 §0 truth source precedence
