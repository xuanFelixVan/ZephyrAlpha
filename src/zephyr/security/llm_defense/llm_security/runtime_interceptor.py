# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.runtime_interceptor
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.layers.__init__
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 所有 LLM 调用必须经 LSGSecurityGateway（RULE-LSG-001）；ZEPHYR_RUNTIME_GATE=0 关闭
# [MODIFY-GUARD] RULE-LSG-001; GATE-20; sitecustomize.py 引导链
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/llm_security/test_runtime_interceptor.py
# [A_module] module_id=MOD-SEC_runtime_interceptor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
runtime_interceptor.py — 运行时 LLM 裸调拦截器（GATE-20 后备防线）

对标：RULE-LSG-001 — 所有 LLM 调用必须经过 LSGSecurityGateway。

GATE-20 是 pre-commit AST 静态门禁，存在不可修复的静态分析上限：当代码内容在运行时
从外部（文件/网络/数据库）获取再 exec 时，AST 层面不可见。本模块作为 GATE-20 的运行时
后备防线，在 Python 进程运行时拦截所有绕过 LSG 的裸调 LLM API 调用。

机制（方案 A+B 融合：sitecustomize 自动引导 + sys.meta_path 导入钩子）：
1. sitecustomize.py 在 Python 解释器启动时自动调用 install()（零业务侵入）。
2. install() 注册 sys.meta_path finder，拦截 openai/anthropic/litellm/langchain 的导入，
   在真实模块加载后 monkey-patch 其核心调用方法（chat.completions.create /
   messages.create / litellm.completion 等）。
3. 被 patch 的方法在调用时检查“LSG 放行令牌”：存在且未过期->放行（LSG 扫描已通过）；
   缺失->抛 BareLLMCallError 硬阻断。
4. LSG 的 scan_input/full_scan/scan_agent_action 在返回 ALLOW 时调用 grant_allowance()
   颁发放行令牌（TTL 30s），使合法的“LSG 扫描->LLM 调用”链路畅通。

放行令牌采用混合存储（覆盖同步与异步两种合法调用链）：
- contextvar：异步路径（await gw.scan_input() 后直接 await async_openai.create()），
  按任务隔离，防止并发请求串扰。
- threading.local：同步路径（_lsg_scan_input_sync 经 asyncio.run 后再调用 openai.create），
  asyncio.run 创建子 context，contextvar 不会回传到同步调用方，故用 thread-local 兜底
  （asyncio.run 在同一线程内执行，thread-local 跨 asyncio.run 边界存活）。

kill-switch：ZEPHYR_RUNTIME_GATE=0 关闭（sitecustomize 引导与 install() 内部双重尊重）。

性能：patch 仅在目标库首次导入时执行一次；运行时仅在被 patch 的方法调用时做一次
令牌检查（O(1)，纳秒级）。LSG 扫描路径不被 patch，扫描耗时不受影响。
"""

from __future__ import annotations

import functools
import importlib.abc
import importlib.machinery
import os
import logging
import sys
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar

logger = logging.getLogger(__name__)

__all__ = [
    "BareLLMCallError",
    "install",
    "uninstall",
    "is_installed",
    "grant_allowance",
    "revoke_allowance",
    "reset_allowance_for_request",
    "allow_llm_call",
    "allow_llm_call_async",
    "is_allowance_active",
]

# ── kill-switch ──
# ZEPHYR_RUNTIME_GATE=0 -> 完全关闭运行时拦截（sitecustomize 与 install 内部双重尊重）
_KILL_SWITCH_ENV = "ZEPHYR_RUNTIME_GATE"
# 默认放行令牌 TTL（秒）：LSG 扫描通过后 30s 内允许发起 LLM 调用
_DEFAULT_TTL = 30.0


class BareLLMCallError(RuntimeError):
    """裸调 LLM API 被运行时拦截器阻断。

    当未持有有效 LSG 放行令牌而直接调用 openai/anthropic/litellm/langchain 的
    核心 LLM 方法时抛出。对标 RULE-LSG-001。
    """

    error_code = "ZA-SC-0022"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# ============================================================================
# 放行令牌（allowance token）—— 混合 contextvar + threading.local
# ============================================================================

# contextvar：异步路径隔离（每个 asyncio task 独立上下文）
_ctx_allowance: ContextVar[tuple[float, str] | None] = ContextVar(
    "zephyr_lsg_allowance", default=None
)
# threading.local：同步路径兜底（跨 asyncio.run 边界）
_tls = threading.local()


def _tls_get() -> tuple[float, str] | None:
    return getattr(_tls, "allowance", None)


def _tls_set(value: tuple[float, str] | None) -> None:
    if value is None:
        try:
            del _tls.allowance
        except AttributeError:
            pass
    else:
        _tls.allowance = value


def is_allowance_active() -> bool:
    """检查当前是否存在有效（未过期）的 LSG 放行令牌。

    优先查 contextvar（异步隔离），其次查 thread-local（同步兜底）。过期则清除。
    """
    tok = _ctx_allowance.get()
    if tok is None:
        tok = _tls_get()
    if tok is None:
        return False
    expiry, _ = tok
    if time.monotonic() >= expiry:
        # 过期令牌：惰性清除
        if _ctx_allowance.get() is tok:
            _ctx_allowance.set(None)
        if _tls_get() is tok:
            _tls_set(None)
        return False
    return True


def grant_allowance(request_id: str | None = None, ttl: float = _DEFAULT_TTL) -> None:
    """颁发 LSG 放行令牌。LSG 扫描通过后调用，使后续 LLM 调用放行。

    同时写入 contextvar 与 thread-local，覆盖同步与异步两种合法调用链。
    幂等：重复调用以最新令牌覆盖。

    Args:
        request_id: 关联的 LSG 请求 ID（用于审计/调试）。
        ttl: 令牌有效期（秒），默认 30s。
    """
    token = (time.monotonic() + ttl, request_id or "")
    try:
        _ctx_allowance.set(token)
    except Exception as e:
        logger.warning("grant_allowance: contextvar set 失败(%s: %s)，异步路径放行令牌未生效", type(e).__name__, e, exc_info=True)
    try:
        _tls_set(token)
    except Exception as e:
        logger.warning("grant_allowance: thread-local set 失败(%s: %s)，同步路径放行令牌未生效", type(e).__name__, e, exc_info=True)


def revoke_allowance() -> None:
    """立即撤销放行令牌（用于测试或显式收尾）。"""
    try:
        _ctx_allowance.set(None)
    except Exception as e:
        logger.critical("revoke_allowance: contextvar 清除失败(%s: %s)，异步路径放行令牌可能残留=授权绕过风险", type(e).__name__, e, exc_info=True)
    try:
        _tls_set(None)
    except Exception as e:
        logger.critical("revoke_allowance: thread-local 清除失败(%s: %s)，同步路径放行令牌可能残留=授权绕过风险", type(e).__name__, e, exc_info=True)


def reset_allowance_for_request() -> None:
    """5.132.1 修复: 请求边界重置放行令牌, 防止线程池复用导致跨请求安全上下文泄漏。

    线程池复用线程时, 上一个请求的 _tls.allowance 可能未过期(默认30s TTL),
    新请求会读到上一个请求的令牌——绕过 RULE-LSG-001 安全网关。

    在请求中间件/拦截器入口调用本函数, 确保每个请求从干净状态开始。
    与 revoke_allowance() 的区别: 本函数用于预防性重置(请求开始时),
    revoke_allowance() 用于显式收尾(请求结束时)。
    """
    _ctx_allowance.set(None)
    _tls_set(None)


@contextmanager
def allow_llm_call(ttl: float = _DEFAULT_TTL):
    """同步上下文管理器：在代码块内允许裸调 LLM（供测试/显式受控调用）。

    用法::

        with allow_llm_call():
            client.chat.completions.create(...)  # 放行
    """
    grant_allowance(request_id="allow_llm_call_ctx", ttl=ttl)
    try:
        yield
    finally:
        revoke_allowance()


@asynccontextmanager
async def allow_llm_call_async(ttl: float = _DEFAULT_TTL):
    """异步上下文管理器：在代码块内允许裸调 LLM（异步版本）。"""
    grant_allowance(request_id="allow_llm_call_async_ctx", ttl=ttl)
    try:
        yield
    finally:
        revoke_allowance()


# ============================================================================
# 方法包装器（guard wrappers）
# ============================================================================

def _make_guard(orig_func, label: str):
    """包装同步 LLM 调用方法：无令牌->raise，有令牌->调原方法。"""

    @functools.wraps(orig_func)
    def _wrapper(*args, **kwargs):
        if not is_allowance_active():
            raise BareLLMCallError(
                f"裸调 {label} 被运行时 Gate 拦截——必须经过 LSGSecurityGateway"
                f"（RULE-LSG-001）。若为受控调用，请用 allow_llm_call() 上下文或"
                f"先经 LSG scan_input 颁发放行令牌。"
            )
        return orig_func(*args, **kwargs)

    _wrapper.__zephyr_runtime_guard__ = True  # 标记，防重复 patch
    return _wrapper


def _make_async_guard(orig_func, label: str):
    """包装异步 LLM 调用方法。"""

    @functools.wraps(orig_func)
    async def _wrapper(*args, **kwargs):
        if not is_allowance_active():
            raise BareLLMCallError(
                f"裸调 {label} 被运行时 Gate 拦截——必须经过 LSGSecurityGateway"
                f"（RULE-LSG-001）。若为受控调用，请用 allow_llm_call_async() 上下文或"
                f"先经 LSG scan_input 颁发放行令牌。"
            )
        return await orig_func(*args, **kwargs)

    _wrapper.__zephyr_runtime_guard__ = True
    return _wrapper


def _is_guarded(func) -> bool:
    return getattr(func, "__zephyr_runtime_guard__", False) is True


# ============================================================================
# 各 LLM 库 patcher（防御式：任何失败均 no-op，绝不阻断导入）
# ============================================================================

def _patch_openai(module) -> None:
    """patch openai v1/v2 的 chat.completions.create（同步+异步）。"""
    try:
        from openai.resources.chat.completions import AsyncCompletions, Completions
    except Exception:
        return
    if not _is_guarded(Completions.create):
        Completions.create = _make_guard(Completions.create, "openai.chat.completions.create")
    if not _is_guarded(AsyncCompletions.create):
        AsyncCompletions.create = _make_async_guard(
            AsyncCompletions.create, "openai.chat.completions.create (async)"
        )


def _patch_anthropic(module) -> None:
    """patch anthropic 的 messages.create（同步+异步）。"""
    try:
        from anthropic.resources.messages import AsyncMessages, Messages
    except Exception:
        return
    if not _is_guarded(Messages.create):
        Messages.create = _make_guard(Messages.create, "anthropic.messages.create")
    if not _is_guarded(AsyncMessages.create):
        AsyncMessages.create = _make_async_guard(
            AsyncMessages.create, "anthropic.messages.create (async)"
        )


def _patch_litellm(module) -> None:
    """patch litellm 的 completion / acompletion（模块级函数）。"""
    try:
        completion = getattr(module, "completion", None)
        if completion is not None and not _is_guarded(completion):
            module.completion = _make_guard(completion, "litellm.completion")
    except Exception as e:
        logger.critical("_patch_litellm: completion patch 失败(%s: %s)，LLM 裸调守卫未挂载=安全绕过", type(e).__name__, e, exc_info=True)
    try:
        acompletion = getattr(module, "acompletion", None)
        if acompletion is not None and not _is_guarded(acompletion):
            module.acompletion = _make_async_guard(acompletion, "litellm.acompletion")
    except Exception as e:
        logger.critical("_patch_litellm: acompletion patch 失败(%s: %s)，异步 LLM 裸调守卫未挂载=安全绕过", type(e).__name__, e, exc_info=True)


def _import_chat_classes() -> list:
    """5.97.12 修复：抽取 _patch_langchain 内嵌 try-except 的 helper。

    尝试两种 langchain 路径导入 ChatOpenAI/ChatAnthropic，失败返回空列表。
    """
    try:
        from langchain.chat_models import ChatAnthropic, ChatOpenAI  # noqa: F401
        return [ChatOpenAI, ChatAnthropic]
    except Exception:
        try:
            from langchain_community.chat_models import ChatAnthropic, ChatOpenAI  # noqa: F401
            return [ChatOpenAI, ChatAnthropic]
        except Exception:
            return []


def _patch_langchain(module) -> None:
    """patch langchain 的 ChatOpenAI / ChatAnthropic（best-effort）。

    langchain 未安装时 no-op。版本结构差异较大，仅 best-effort patch .invoke。
    """
    targets = _import_chat_classes()
    if not targets:
        return
    for cls in targets:
        try:
            invoke = getattr(cls, "invoke", None)
            if invoke is not None and not _is_guarded(invoke):
                label = f"langchain.{cls.__name__}.invoke"
                setattr(cls, "invoke", _make_guard(invoke, label))
        except Exception as e:
            logger.critical("_patch_langchain: %s.invoke patch 失败(%s: %s)，LLM 裸调守卫未挂载=安全绕过", cls.__name__, type(e).__name__, e, exc_info=True)
            continue


# 顶层目标模块名 -> patcher
_PATCHERS: dict[str, callable] = {
    "openai": _patch_openai,
    "anthropic": _patch_anthropic,
    "litellm": _patch_litellm,
    "langchain": _patch_langchain,
}


# ============================================================================
# sys.meta_path 导入钩子（拦截目标库导入 -> 加载后 patch）
# ============================================================================

class _LLMGuardLoader(importlib.abc.Loader):
    """包装真实 loader：执行原 loader 后立即 patch 目标模块。"""

    def __init__(self, orig_loader, patcher):
        self._orig = orig_loader
        self._patcher = patcher

    def create_module(self, spec):
        if hasattr(self._orig, "create_module"):
            return self._orig.create_module(spec)
        return None

    def exec_module(self, module):
        self._orig.exec_module(module)
        try:
            self._patcher(module)
        except Exception:
            # patch 失败绝不阻断模块导入——宁可漏拦也不破坏导入链
            pass


class _LLMGuardFinder(importlib.abc.MetaPathFinder):
    """meta_path finder：仅拦截 _PATCHERS 中的顶层目标模块，其余交给默认机制。"""

    def find_spec(self, fullname, path=None, target=None):
        patcher = _PATCHERS.get(fullname)
        if patcher is None:
            return None  # 非目标模块：交给后续 finder
        # 用 PathFinder 找真实 spec（绕过自身，避免递归）
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            return None
        spec.loader = _LLMGuardLoader(spec.loader, patcher)
        return spec


# ============================================================================
# install / uninstall
# ============================================================================

_FINDER_INSTALLED = False
_orig_imports: dict[str, dict] = {}  # 记录已 patch 的原始引用（供 uninstall 回滚）


def _eager_patch_loaded() -> None:
    """对已导入的目标模块立即 patch（install 时尚未导入则由 finder 兜底）。"""
    for name, patcher in _PATCHERS.items():
        mod = sys.modules.get(name)
        if mod is not None:
            try:
                patcher(mod)
            except Exception as e:
                logger.critical("_eager_patch_loaded: %s patch 失败(%s: %s)，LLM 裸调守卫未挂载=安全绕过", name, type(e).__name__, e, exc_info=True)


def install() -> bool:
    """安装运行时 LLM 裸调拦截器。

    - 尊重 kill-switch：ZEPHYR_RUNTIME_GATE=0 -> 不安装，返回 False。
    - 幂等：重复调用安全。
    - 注册 sys.meta_path finder + 对已导入的目标库立即 patch。

    Returns:
        True 表示已安装（或已处于安装状态）；False 表示因 kill-switch 未安装。
    """
    global _FINDER_INSTALLED
    if os.environ.get(_KILL_SWITCH_ENV, "1") == "0":
        return False
    if _FINDER_INSTALLED:
        return True
    try:
        # finder 插入到最前，确保目标库导入时优先被拦截
        sys.meta_path.insert(0, _LLMGuardFinder())
        _eager_patch_loaded()
        _FINDER_INSTALLED = True
        return True
    except Exception:
        # 安装失败也不破坏解释器启动
        return False


def uninstall() -> None:
    """卸载拦截器（供测试隔离）。

    仅移除 finder 与令牌；已 patch 的方法不回滚（测试应使用独立子进程隔离，
    或在测试内自行 monkeypatch）。保持简单：uninstall 主要用于停止“未来导入”的 patch。
    """
    global _FINDER_INSTALLED
    try:
        sys.meta_path = [f for f in sys.meta_path if not isinstance(f, _LLMGuardFinder)]
    except Exception as e:
        logger.warning("suppressed error in runtime_interceptor", exc_info=True)
    _FINDER_INSTALLED = False
    revoke_allowance()


def is_installed() -> bool:
    """拦截器 finder 是否已注册。"""
    return _FINDER_INSTALLED