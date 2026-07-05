# [A_module] module_id=MOD-UNK_zephyr | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infra_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
ZephyrAlpha 核心包索引 + 模块懒加载器 (M-04)

C 轨 — 14 层业务脊柱 | B 轨 — 10 横切平台能力

快速导入参考：
  核心数据模型:    from zephyr.shared.schema.schemas import Task, TaskStatus
  门禁检查:        from zephyr.governance.rule_enforcement import gate_engine
  上下文构建:      from zephyr.autonomy_core.context.context_management import intent_parser
  向量记忆服务:    from zephyr.integration.vector_memory import InProcessVectorMemory
"""

import importlib
import logging
import sys
import threading
import types
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


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

# 5.31.4/5.31.11 修复：版本号真源统一到 pyproject.toml（唯一 SSoT）
# 原硬编码 _version_ = "4.6.0"（单下划线）与 pyproject.toml 2.0.0 不一致
# 改用 importlib.metadata 动态读取，遵循 PEP 396 / PEP 621 约定（双下划线 __version__）
try:
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("zephyralpha")
except Exception:  # 包未安装（开发模式/直接 import）回退到 pyproject 解析
    try:
        from pathlib import Path as _Path

        _pyproject = _Path(__file__).resolve().parents[2] / "pyproject.toml"
        if _pyproject.exists():
            import re as _re

            __version__ = _re.search(r'version\s*=\s*"([^"]+)"', _pyproject.read_text(encoding="utf-8")).group(1)
        else:
            __version__ = "0.0.0+unknown"
    except Exception:
        __version__ = "0.0.0+unknown"


def register_lazy(name: str, module_path: str) -> None:
    _lazy_registry[name] = module_path


class _LazyModule:
    """延迟加载代理——首次访问时才加载实际模块 (M-04)"""

    def __init__(self, module_path: str) -> None:
        self._module_path = module_path
        self._module: types.ModuleType | None = None

    def _load(self) -> None:
        if self._module is None:
            self._module = importlib.import_module(self._module_path)

    def __getattr__(self, name: str) -> Any:
        # 5.98.4 修复: 防止 _module/_module_path 未初始化时 __getattr__ 无限递归
        # 若 __init__ 被绕过(pickle/copy/测试), _module 不在 __dict__ 中,
        # __getattr__('_module') → _load() → self._module → __getattr__('_module') → RecursionError
        if name in ("_module", "_module_path"):
            raise AttributeError(name)
        self._load()
        return getattr(self._module, name)

    def __dir__(self) -> list[str]:
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


def __dir__() -> list[str]:
    return sorted(set(dir(type(__name__))) | set(_lazy_registry.keys()))


# ── 全自动遥测注入（MOD-INF-015 v0.9.0 · auto_bootstrap）─────────────────
# import zephyr 时自动执行——SessionContinuity + PhaseManager + BlueprintMetrics
# 全面 monkey-patch，零手动代码。try/except 保活——patch 失败不阻塞 import。
# 延迟到后台线程，不阻塞 import zephyr 冷启动。
_auto_bootstrap_result = None
_bootstrap_lock = threading.Lock()  # 5.165.1 修复: 保护 _auto_bootstrap_result 跨线程读写


def _deferred_bootstrap():
    global _auto_bootstrap_result
    try:
        from zephyr.infrastructure.system_telemetry.auto_bootstrap import bootstrap as _auto_bootstrap

        result = _auto_bootstrap()
    except Exception as exc:
        _log.warning("auto_bootstrap failed: %s", exc, exc_info=True)
        result = None
    with _bootstrap_lock:  # 5.165.1 修复: 加锁写入 global 变量
        _auto_bootstrap_result = result
    # §5.17.14 治本：自动接入 secret_rotation 到 SecretProvider
    # 扫描 os.environ 中的密钥变量（KEY/TOKEN/SECRET/PASSWORD等）注册轮换调度，
    # 注入后所有 get_secret* 读取时前置 needs_rotation 检查（warn 不阻断）。
    try:
        from zephyr.trading.feedback_loop.security.secret_rotation import auto_configure

        auto_configure()
    except Exception as exc:
        _log.warning("secret_rotation auto_configure failed: %s", exc, exc_info=True)


_bootstrap_timer = threading.Timer(0.05, _deferred_bootstrap)
_bootstrap_timer.daemon = True
_bootstrap_timer.start()


# ── D-DATA ServiceRegistry 注册（DM-364 解耦层）────────────────────────────
# D-DATA 实现注册到 shared_core.ServiceRegistry，D-INFRA 通过 registry 获取。
# 延迟注册，避免循环导入。
def _deferred_service_registration():
    try:
        from zephyr.governance.ops_governance.service_registration import register_services

        register_services()
    except Exception as exc:
        _log.warning("service_registration failed: %s", exc, exc_info=True)


_registration_timer = threading.Timer(0.1, _deferred_service_registration)
_registration_timer.daemon = True
_registration_timer.start()

# ── 模块懒加载注册（M-04 · PEP 562 __getattr__）───────────────────────────
# 5.22.2 修复：4个幻影路径修正为真实模块路径
register_lazy(
    "vector-memory", "zephyr.infrastructure.vector_memory_server"
)  # MOD-INF-011 VMS
register_lazy("llm-security", "zephyr.security.llm_defense.llm_security")  # MOD-LLM_SECURITY LSG — L0-L8 nine-layer defense
register_lazy(
    "_cross_layer", "zephyr.risk.cross_asset.cross_market_data_adapter"
)  # MOD-FEEDBACK_LOOP FLE cross-layer pipelines (AlphaSignal + MLExperiment)
register_lazy(
    "contract_registry", "zephyr.trading.orchestrator.contracts.contract_registry"
)  # MOD-MASTER_BLUEPRINT CT-* contract registry
register_lazy(
    "truth_source", "zephyr.governance.rule_enforcement.truth_source_validator"
)  # MOD-MASTER_BLUEPRINT §0 truth source precedence
register_lazy("autopilot", "zephyr.trading.autopilot")  # MOD-INF-012B AutoPilot — AI session 自动驾驶
# 删除 register_lazy("signal", "zephyr.signal") — D-SIGNAL 域已拆分为3个平级兄弟域
# （signal_ashare / signal_fundamental / signal_quality），无单一 zephyr.signal 包
register_lazy("ml_train", "zephyr.ml_train")  # MOD-L11-001 ML Training domain
__all__ = [  # noqa: gate-vocab  __all__ 子包导出列表，非 domain 分类
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
