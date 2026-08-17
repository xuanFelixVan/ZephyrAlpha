# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
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
# noqa: m10-time-trigger  M10豁免: threading.Timer用于一次性超时/延迟执行，非周期时间触发
"""


ZephyrAlpha 核心包索引 + 模块懒加载器 (M-04)

C 轨 — 14 层业务脊柱 | B 轨 — 10 横切平台能力

快速导入参考：
  核心数据模型:    from zephyr.shared.schema.schemas import Task, TaskStatus
  门禁检查:        from zephyr.gov_enforcement.rule_enforcement import gate_engine
  上下文构建:      from zephyr.autonomy_core.context.context_management import intent_parser
  向量记忆服务:    from zephyr.integration.vector_memory import InProcessVectorMemory

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: .env 环境变量文件
#   fields: KEY=VALUE 文本行（# 开头为注释）
#   code: REPO_ROOT/.env L64
# - id: I2
#   name: 包版本元数据
#   fields: importlib.metadata("zephyralpha") 或 pyproject.toml 的 version 字段（PEP 621）
#   code: L99-114
# - id: I3
#   name: 特性开关配置
#   fields: auto_bootstrap 等 flag（config/flags.yaml，经 global_flag_registry）
#   code: _feature_flag_enabled L168-180
# - id: I4
#   name: 懒加载注册条目
#   fields: 别名 → 模块路径（register_lazy 调用，如 vector-memory/autopilot/ml_train）
#   code: register_lazy L247-263
# 层: 算法
# - id: A1
#   name_zh: ① Python 3.10 标准库兼容补丁
#   name_en: datetime.UTC / typing.Self 回填
#   intro: 给标准库打最小补丁，一处修复全项目生效
#   desc: hasattr 检查缺失则回填 datetime.UTC=timezone.utc、typing.Self=typing_extensions.Self 或 TypeVar（ARCH-PYCOMPAT-001）
#   inputs: 无（进程级标准库环境）
#   outputs: 补丁后的标准库别名
# - id: A2
#   name_zh: ② .env 加载
#   name_en: _load_dotenv
#   intro: 启动时把 .env 的键值对注入进程环境变量
#   desc: 优先 python-dotenv（override=False）；无库时手工解析并 os.environ.setdefault；非源码树环境直接跳过
#   inputs: I1
#   outputs: os.environ 环境变量
# - id: A3
#   name_zh: ③ 包版本号解析
#   name_en: __version__ 解析
#   intro: 从已安装包元数据或 pyproject.toml 读出唯一版本号
#   desc: importlib.metadata.version("zephyralpha") → 回退 pyproject.toml 正则提取 → 兜底 "0.0.0+unknown"
#   inputs: I2
#   outputs: __version__ 字符串
#   invariant: 版本真源唯一 SSoT=pyproject.toml，禁止硬编码
# - id: A4
#   name_zh: ④ 包级懒加载路由
#   name_en: register_lazy / _LazyModule / __getattr__（PEP 562）
#   intro: 首次访问子模块时才真正 import，加快冷启动
#   desc: 别名命中注册表则返回 _LazyModule 代理并 setattr 缓存；__getattr__ 防 _module 未初始化递归；未知名抛 AttributeError
#   inputs: I4
#   outputs: 懒加载模块代理
# - id: A5
#   name_zh: ⑤ 延迟引导编排
#   name_en: _deferred_bootstrap / _deferred_service_registration
#   intro: 后台 daemon Timer 里做遥测注入、密钥轮换和服务注册
#   desc: flag 守护（fail-open）→ auto_bootstrap monkey-patch → secret_rotation.auto_configure → service_registration；atexit 取消未完成 Timer
#   inputs: I3
#   outputs: 进程级副作用（遥测/轮换/注册）
#   invariant: try/except 保活——任何引导失败都不阻断 import zephyr
# 层: 输出
# - id: O1
#   name_zh: 包版本常量
#   name_en: __version__
#   intro: zephyralpha 包版本号，运行时可查询
#   downstream: 全项目（import zephyr 的任何模块）
# - id: O2
#   name_zh: 懒加载包命名空间
#   name_en: _LazyModule 代理
#   intro: import zephyr 后按需加载的子模块入口
#   downstream: 全项目子包消费者（[CONSUMERS] 头未登记具体 MOD）
# - id: O3
#   name_zh: 进程级启动副作用
#   name_en: bootstrap side effects
#   intro: 环境变量注入 + 全模块遥测 patch + 密钥轮换调度 + D-DATA 服务注册
#   downstream: system_telemetry MOD-INF-015 / ServiceRegistry 消费方
# [/ALGO_FLOW]
#
# 边:
# I1 --> A2
# I2 --> A3
# I3 --> A5
# I4 --> A4
# A1 --> O3
# A2 --> O3
# A3 --> O1
# A4 --> O2
# A5 --> O3
"""

import atexit
import datetime as _datetime
import importlib
import logging
import sys
import threading
import types
from pathlib import Path
from typing import Any

# #ARCH-PYCOMPAT-001: Python 3.10 兼容补丁（集中式，一处修复全项目生效）
# 原则：只对标准库做最小补丁，确保 3.10 环境下能正常 import 和运行
# 1. datetime.UTC — Python 3.11+ 别名，本质就是 timezone.utc
if not hasattr(_datetime, "UTC"):
    _datetime.UTC = _datetime.timezone.utc

# 2. typing.Self — Python 3.11+ 新增，运行时用 TypeVar 等价替代
import typing as _typing
if not hasattr(_typing, "Self"):
    try:
        from typing_extensions import Self as _Self
        _typing.Self = _Self
    except ImportError:
        _Self = _typing.TypeVar("Self")
        _typing.Self = _Self

_log = logging.getLogger(__name__)


def _load_dotenv() -> None:
    try:
        from zephyr.shared.io.paths import REPO_ROOT
    except FileNotFoundError:
        # 非源码树环境（pip install 后的 site-packages，如 Docker 镜像内）：
        # find_repo_root() 找不到 src/zephyr/__init__.py 标记会抛 FileNotFoundError。
        # 此时无 .env 可加载（容器经 environment/env_file 注入环境变量），直接跳过。
        return

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
except Exception:  # 包未安装（开发模式/直接 import）回退到 pyproject 解析  # noqa: BLE001 — 5.135治标: broad exception catch
    try:
        from pathlib import Path as _Path

        _pyproject = _Path(__file__).resolve().parents[2] / "pyproject.toml"
        if _pyproject.exists():
            import re as _re

            __version__ = _re.search(r'version\s*=\s*"([^"]+)"', _pyproject.read_text(encoding="utf-8")).group(1)
        else:
            __version__ = "0.0.0+unknown"
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        # __getattr__('_module') -> _load() -> self._module -> __getattr__('_module') -> RecursionError
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


def _feature_flag_enabled(key: str, *, default: bool = True) -> bool:
    """5.38.8 治本：高风险功能 flag 守护点——读 canonical global_flag_registry。

    flags.yaml 未加载/flag 未注册/flag 系统异常时返回 ``default``（默认 ON 可关闭，
    守护点 fail-open 保证 import zephyr 永不因 flag 系统故障而中断）。
    """
    try:
        from zephyr.shared.foundation.flags import ensure_global_flags_loaded, global_flag_registry

        ensure_global_flags_loaded()
        return global_flag_registry.is_enabled(key, default=default)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return default


def _deferred_bootstrap():
    global _auto_bootstrap_result
    # 5.38.8: auto_bootstrap（monkey-patch 全模块遥测注入）属高风险功能，加 flag 守护。
    # config/flags.yaml auto_bootstrap.enabled=false 时跳过 patch（默认 ON 可关闭）。
    if not _feature_flag_enabled("auto_bootstrap"):
        _log.info("auto_bootstrap skipped: feature flag 'auto_bootstrap' is OFF (config/flags.yaml)")
        result = None
    else:
        try:
            from zephyr.infrastructure.system_telemetry.auto_bootstrap import bootstrap as _auto_bootstrap

            result = _auto_bootstrap()
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _log.warning("auto_bootstrap failed: %s", exc, exc_info=True)
            result = None
    with _bootstrap_lock:  # 5.165.1 修复: 加锁写入 global 变量
        _auto_bootstrap_result = result
    # §5.17.14 治本：自动接入 secret_rotation 到 SecretProvider
    # 扫描 os.environ 中的密钥变量（KEY/TOKEN/SECRET/PASSWORD等）注册轮换调度，
    # 注入后所有 get_secret* 读取时前置 needs_rotation 检查（warn 不阻断）。
    try:
        from zephyr.feedback_loop.security.secret_rotation import auto_configure

        auto_configure()
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        _log.warning("service_registration failed: %s", exc, exc_info=True)


_registration_timer = threading.Timer(0.1, _deferred_service_registration)
_registration_timer.daemon = True
_registration_timer.start()


# 5.77.1 修复: import 副作用——daemon Timer 线程在 import 时启动。
# 注册 atexit cleanup 取消未完成的 daemon Timer，避免进程退出时遗留线程资源。
def _cleanup_bootstrap_timers() -> None:
    for timer in (_bootstrap_timer, _registration_timer):
        try:
            timer.cancel()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass


atexit.register(_cleanup_bootstrap_timers)

# ── 模块懒加载注册（M-04 · PEP 562 __getattr__）───────────────────────────
# 5.22.2 修复：4个幻影路径修正为真实模块路径
register_lazy(
    "vector-memory", "zephyr.integration.vector_memory"
)  # MOD-INF-011 VMS — P0-4: 真源是 vector_memory 包（reexport UnifiedMemoryAPI/get_unified_memory_api），非 mcp.vector_memory_server（仅定义 Server 类）
register_lazy("llm-security", "zephyr.security.llm_defense.llm_security")  # MOD-LLM_SECURITY LSG — L0-L8 nine-layer defense
register_lazy(
    "_cross_layer", "zephyr.risk.cross_asset.cross_market_data_adapter"
)  # MOD-FEEDBACK_LOOP FLE cross-layer pipelines (AlphaSignal + MLExperiment)
register_lazy(
    "contract_registry", "zephyr.orchestrator.contracts.contract_registry"
)  # MOD-MASTER_BLUEPRINT CT-* contract registry
register_lazy(
    "truth_source", "zephyr.gov_enforcement.rule_enforcement.truth_source_validator"
)  # MOD-MASTER_BLUEPRINT §0 truth source precedence
register_lazy("autopilot", "zephyr.trading.autopilot")  # MOD-INF-012B AutoPilot — AI session 自动驾驶
# 删除 register_lazy("signal", "zephyr.signal") — D-SIGNAL 域已拆分为3个平级兄弟域
# （signal_ashare / signal_fundamental / signal_quality），无单一 zephyr.signal 包
register_lazy("ml_train", "zephyr.ml_train")  # MOD-L11-001 ML Training domain
# 5.93.2 修复（R70）：移除 9 个不存在的子包名（data/execution/observability/
# orchestration/portfolio/resilience/semantic_auditor/signal/testing），
# 补入 signal_fundamental（D-SIGNAL 拆分3兄弟之一，原遗漏）
__all__ = [  # noqa: gate-vocab  __all__ 子包导出列表，非 domain 分类
    "compliance",
    "cross_asset",
    "ex_core",
    "factor",
    "frontend",
    "governance",
    "infrastructure",
    "integration",
    "intelligence",
    "ml_train",
    "pf_alloc",
    "pf_core",
    "reporting",
    "research",
    "risk",
    "security",
    "shared",
    "signal_ashare",
    "signal_fundamental",
    "signal_quality",
    "simulation",
]
auto_bootstrap_result = _auto_bootstrap_result  # public alias（Stage 4 公共化）

