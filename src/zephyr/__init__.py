# [A_module] module_id=MOD-UNK_zephyr | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain-infra_runtime/runtime-integration/blueprint.md
# [MODULE] zephyr
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
ZephyrAlpha 核心包索引 + 模块懒加载器 (M-04)

C 轨 — 14 层业务脊柱 | B 轨 — 10 横切平台能力

快速导入参考：
  核心数据模型:    from zephyr.shared.schemas import Task, TaskStatus
  门禁检查:        from zephyr.governance.rule_enforcement import gate_engine
  上下文构建:      from zephyr.autonomy_core.context_management import intent_parser
  向量记忆服务:    from zephyr.integration.vector_memory import InProcessVectorMemory
"""

import importlib
import sys
import threading
import types
from pathlib import Path
from typing import Any, Optional


def _load_dotenv() -> None:
    from zephyr.shared.io.paths import REPO_ROOT

    env_path = REPO_ROOT / ".env"
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
        self._module: types.ModuleType | None = None

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
# 延迟到后台线程，不阻塞 import zephyr 冷启动。
_auto_bootstrap_result = None


def _deferred_bootstrap():
    global _auto_bootstrap_result
    try:
        from zephyr.infrastructure.system_telemetry.auto_bootstrap import bootstrap as _auto_bootstrap

        _auto_bootstrap_result = _auto_bootstrap()
    except Exception:
        _auto_bootstrap_result = None


_bootstrap_timer = threading.Timer(0.05, _deferred_bootstrap)
_bootstrap_timer.daemon = True
_bootstrap_timer.start()


# ── D-DATA ServiceRegistry 注册（DM-364 解耦层）────────────────────────────
# D-DATA 实现注册到 shared_core.ServiceRegistry，D-INFRA 通过 registry 获取。
# 延迟注册，避免循环导入。
def _deferred_service_registration():
    try:
        from zephyr.governance._service_registration import register_services

        register_services()
    except Exception:
        pass


_registration_timer = threading.Timer(0.1, _deferred_service_registration)
_registration_timer.daemon = True
_registration_timer.start()

# ── 模块懒加载注册（M-04 · PEP 562 __getattr__）───────────────────────────
register_lazy(
    "vector-memory", "zephyr.data_governance_governance.knowledge_management.vector_memory"
)  # MOD-INF-011 VMS
register_lazy("llm-security", "zephyr.security.llm_defense.llm_security")  # MOD-LLM_SECURITY LSG — L0-L8 nine-layer defense
register_lazy(
    "_cross_layer", "zephyr.cross_asset.cross_market_data_adapter"
)  # MOD-FEEDBACK_LOOP FLE cross-layer pipelines (AlphaSignal + MLExperiment)
register_lazy(
    "contract_registry", "zephyr.integration.runtime_core.orchestrator.contract_registry"
)  # MOD-MASTER_BLUEPRINT CT-* contract registry
register_lazy(
    "truth_source", "zephyr.governance.rule_enforcement.truth_source_validator"
)  # MOD-MASTER_BLUEPRINT §0 truth source precedence
register_lazy("autopilot", "zephyr.integration.runtime_core.autopilot")  # MOD-INF-012B AutoPilot — AI session 自动驾驶
register_lazy("signal", "zephyr.signal")  # MOD-L03-001 Signal domain
register_lazy("ml_train", "zephyr.ml_train")  # MOD-L11-001 ML Training domain
__all__ = [
    "autonomy_perm",
    "compliance",
    "cross_asset",
    "data",
    "ex_core",
    "execution",
    "factor",
    "frontend",
    "governance",
    "infrastructure",
    "integration",
    "intelligence",
    "ml_train",
    "observability",
    "orchestration",
    "pf_alloc",
    "pf_core",
    "portfolio",
    "reporting",
    "research",
    "resilience",
    "risk",
    "security",
    "semantic_auditor",
    "shared",
    "signal",
    "signal_ashare",
    "signal_quality",
    "simulation",
    "testing",
]
