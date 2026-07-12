# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.trigger_router
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.trading.__init__; zephyr.governance.rule_enforcement.drift_detector; zephyr.trading.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_trigger_router | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TriggerRouter — RI-03 触发路由器（M3 跨模块触发分派）
=====================================================
任务编号 : T-V2-007（experimental RI-03）
权限层级 : Human-Gated（M3 路由表修改 = 关键架构变更，R84 修正）
真源声明 : ai_autonomy_authority_registry.yaml §2.9（RI-03）+ §2.10（三件套）
关联决策 : rationale-log R84（RI-02/03 偏松 -> Human-Gated 修正）
           B6 §2.4（RI-03 设计）+ §3.4（experimental 部署）
创建日期 : 2026-04-27
版本     : v1.0.0

功能说明
--------
根据 ``trigger_type`` 从 ``config/trigger_router.yaml`` 路由表分派到对应的处理器函数：

1. **启动时一次性加载**：``TriggerRouter()`` 构造时读取 YAML，运行期不再 IO
2. **延迟解析处理器**：处理器函数路径在首次 dispatch 时 import；import 失败 -> 审计 + 跳过
3. **路由失败静默**：未注册 ``trigger_type`` / 处理器 disabled -> 写审计日志 + 返回 SKIPPED 不抛异常
4. **CBAC 兼容**：路由本身是读操作不走 ``capability_check``；处理器内部按需自查
5. **审计可观察**：每次 dispatch 通过 ``AuditLogger.log_rule_trigger`` 写 JSONL（可选注入）

experimental 起始集（5 种 trigger_type）
-----------------------------------
- ``onboarding``         — 新会话/Agent 注册触发上下文加载
- ``drift_detected``     — 偏移检测器报告偏移触发恢复
- ``compression_needed`` — Token 预算紧张触发文档压缩
- ``cleanup_due``        — 周期性清理任务
- ``blueprint_published`` — 新蓝图发布触发反思循环

设计原则
--------
- **零跨模块硬依赖**：处理器路径以字符串配置，运行时 ``importlib.import_module`` 解析
- **失败即跳过**：所有失败路径返回 ``RouterDispatchResult(success=False, skipped=True)``
- **可注入测试**：``handlers`` 参数允许直接注入 callable 字典，绕过 YAML/import
"""

from __future__ import annotations

from typing import Final
import importlib
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from threading import RLock
from typing import Any, Protocol, runtime_checkable

import yaml
from pydantic import BaseModel, ConfigDict, Field


@runtime_checkable
class AuditLoggerProtocol(Protocol):
    """触发路由审计日志 duck-typed 接口（5.145.11 修复：Any->Protocol）。

    真源实现：``zephyr.security.llm_defense.llm_security.behavior_audit_logger.AuditLogger``。
    本 Protocol 仅声明 trigger_router 实际消费的 ``log_rule_trigger`` 方法。
    """

    def log_rule_trigger(
        self,
        *,
        target: str,
        result: str,
        extra: dict[str, Any] | None = None,
    ) -> None: ...

__all__ = [
    "DEFAULT_ROUTER_YAML_PATH",
    "PHASE1D_TRIGGER_TYPES",
    "RouterDispatchResult",
    "TriggerHandlerSpec",
    "TriggerRouter",
    "TriggerRouterConfigError",
    "TriggerSafety",
    "get_trigger_router",
    "handle_blueprint_lookup_stub",
    "handle_blueprint_stub",
    "handle_cleanup_stub",
    "handle_drift_detected",
    "handle_onboarding_stub",
    "load_router_config",
    "reset_trigger_router",
]

_logger = logging.getLogger(__name__)
_UTC = UTC

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

# 路径解析：trigger_router.py 位于 src/zephyr/orchestrator/，
# parents[3] = （项目根，与 capability.py 一致）
DEFAULT_ROUTER_YAML_PATH: Final[Path] = REPO_ROOT / "config" / "trigger_router.yaml"

PHASE1D_TRIGGER_TYPES: Final[frozenset[str]] = frozenset(
    {
        "onboarding",
        "drift_detected",
        "compression_needed",
        "cleanup_due",
        "blueprint_published",
        "blueprint_lookup",
    }
)

# ---------------------------------------------------------------------------
# 异常与枚举
# ---------------------------------------------------------------------------


class TriggerRouterConfigError(RuntimeError):
    """``config/trigger_router.yaml`` 加载或校验失败。"""

    error_code = "ZA-TR-0005"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class TriggerSafety(str, Enum):
    """触发器安全等级（与 schemas.SafetyLevel 一致：L/M/H，向后兼容别名）。"""

    L = "L"
    M = "M"
    H = "H"


# ---------------------------------------------------------------------------
# 数据契约
# ---------------------------------------------------------------------------


class TriggerHandlerSpec(BaseModel):
    """单条 trigger_type 的处理器规格（YAML 反序列化目标）。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    handler: str = Field(min_length=1, description="完全限定函数路径，如 'pkg.mod.func'")
    description: str = Field(default="", max_length=200)
    safety: TriggerSafety = Field(default=TriggerSafety.M)
    enabled: bool = Field(default=True)
    priority: int = Field(default=0, ge=0, description="调度优先级（数值小优先，与 YAML 对齐）")
    required: bool = Field(default=False, description="若为 True，缺失处理器视为配置错误")
    retry: bool = Field(default=False, description="失败时是否允许重试")
    notes: str = Field(default="", max_length=2000, description="人读备注 / 真源 trace")


class RouterDispatchResult(BaseModel):
    """``TriggerRouter.dispatch`` 的统一返回类型。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    trigger_type: str = Field(min_length=1)
    handler_path: str | None = Field(default=None)
    success: bool = Field(default=False)
    skipped: bool = Field(default=False, description="True 表示路由未匹配 / disabled / import 失败")
    skip_reason: str = Field(default="", description="跳过原因，便于审计追踪")
    error: str | None = Field(default=None, description="异常信息（成功时为 None）")
    handler_result: object = Field(default=None, description="处理器返回值（透传）")
    dispatched_at: str = Field(default="", description="UTC ISO 8601 分派时间")
    latency_ms: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# YAML 加载器
# ---------------------------------------------------------------------------


def load_router_config(
    path: Path | None = None,
) -> dict[str, TriggerHandlerSpec]:
    """从 ``config/trigger_router.yaml`` 加载触发器规格字典。

    Parameters
    ----------
    path : Path | None
        YAML 路径；None 时使用 ``DEFAULT_ROUTER_YAML_PATH``。

    Returns
    -------
    dict[str, TriggerHandlerSpec]
        ``trigger_type -> TriggerHandlerSpec`` 字典。

    Raises
    ------
    TriggerRouterConfigError
        文件不存在 / YAML 解析失败 / 必填字段缺失。
    """
    resolved = path or DEFAULT_ROUTER_YAML_PATH
    if not resolved.exists():
        raise TriggerRouterConfigError(f"trigger_router.yaml not found: {resolved}")

    try:
        with resolved.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except Exception as exc:
        raise TriggerRouterConfigError(f"YAML parse failed: {exc}") from exc

    triggers_raw = data.get("triggers")
    if not isinstance(triggers_raw, dict):
        raise TriggerRouterConfigError("trigger_router.yaml 必须包含顶层 'triggers' 映射")

    specs: dict[str, TriggerHandlerSpec] = {}
    for trigger_type, raw in triggers_raw.items():
        if not isinstance(trigger_type, str) or not trigger_type.strip():
            raise TriggerRouterConfigError(f"trigger_type 必须为非空字符串，实际：{trigger_type!r}")
        if not isinstance(raw, dict):
            raise TriggerRouterConfigError(
                f"trigger_type='{trigger_type}' 的规格必须为映射，实际：{type(raw).__name__}"
            )
        try:
            specs[trigger_type] = TriggerHandlerSpec(**raw)
        except Exception as exc:
            raise TriggerRouterConfigError(f"trigger_type='{trigger_type}' 规格非法：{exc}") from exc

    return specs


# ---------------------------------------------------------------------------
# TriggerRouter 主类
# ---------------------------------------------------------------------------


class TriggerRouter:
    """触发路由器：根据 trigger_type 分派到处理器函数。

    Parameters
    ----------
    config_path : Path | None
        路由表 YAML 路径；None 使用默认路径。
    handlers : dict[str, Callable] | None
        直接注入 ``trigger_type -> callable`` 映射（优先级最高，跳过 YAML 解析）。
        测试 / 集成场景使用；生产建议保留 None 让 YAML 真源生效。
    audit_logger : AuditLoggerProtocol | None
        ``AuditLogger`` 实例（zephyr.security.llm_defense.llm_security.behavior_audit_logger）；
        None 时仅写 stdlib logging。Duck-typed 接口：
        ``audit_logger.log_rule_trigger(target=str, result=str, extra=dict)``.
    session_id : str
        审计日志默认 session_id。
    model : str
        审计日志默认 model 标识（如 "M3:trigger_router"）。
    auto_load : bool
        构造时立即加载 YAML（默认 True）；False 时延迟到首个 dispatch。
    """

    def __init__(
        self,
        config_path: Path | None = None,
        *,
        handlers: dict[str, Callable[..., Any]] | None = None,
        audit_logger: AuditLoggerProtocol | None = None,
        session_id: str = "",
        model: str = "M3:trigger_router",
        auto_load: bool = True,
    ) -> None:
        self._config_path = config_path or DEFAULT_ROUTER_YAML_PATH
        self._injected_handlers: dict[str, Callable[..., Any]] = dict(handlers or {})
        self._audit = audit_logger
        self._session_id = session_id
        self._model = model
        self._lock = RLock()
        self._specs: dict[str, TriggerHandlerSpec] = {}
        self._resolved_handlers: dict[str, Callable[..., Any]] = {}
        self._loaded = False
        if auto_load:
            self._load()

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """加载 YAML 路由表（幂等）。

        - 注入的 ``handlers`` 始终覆盖 YAML 中的同名条目；
        - YAML 加载失败但有注入 handlers 时以注入为准（允许测试/离线运行）。
        """
        with self._lock:
            if self._loaded:
                return
            specs: dict[str, TriggerHandlerSpec] = {}
            try:
                specs = load_router_config(self._config_path)
            except TriggerRouterConfigError as exc:
                if not self._injected_handlers:
                    raise
                _logger.warning("TriggerRouter YAML 加载失败但已注入 handlers，继续运行：%s", exc)
            self._specs = specs

            for ttype, fn in self._injected_handlers.items():
                self._resolved_handlers[ttype] = fn
                if ttype not in self._specs:
                    self._specs[ttype] = TriggerHandlerSpec(
                        handler=f"<injected:{getattr(fn, '__name__', 'callable')}>",
                        description="injected handler (test/integration)",
                        safety=TriggerSafety.L,
                        enabled=True,
                    )
            self._loaded = True

    def reload(self) -> None:
        """强制重新加载 YAML（测试 / Owner 手动触发使用）。"""
        with self._lock:
            self._loaded = False
            self._specs.clear()
            self._resolved_handlers.clear()
            for ttype, fn in self._injected_handlers.items():
                self._resolved_handlers[ttype] = fn
            self._load()

    # ------------------------------------------------------------------
    # 查询接口
    # ------------------------------------------------------------------

    @property
    def trigger_types(self) -> list[str]:
        """已注册的全部 trigger_type 列表。"""
        with self._lock:
            return list(self._specs.keys())

    def get_spec(self, trigger_type: str) -> TriggerHandlerSpec | None:
        """返回指定 trigger_type 的规格；不存在返回 None。"""
        with self._lock:
            return self._specs.get(trigger_type)

    def is_registered(self, trigger_type: str) -> bool:
        return self.get_spec(trigger_type) is not None

    # ------------------------------------------------------------------
    # 处理器解析
    # ------------------------------------------------------------------

    def _resolve_handler(self, trigger_type: str, spec: TriggerHandlerSpec) -> Callable[..., Any] | None:
        """按优先级解析处理器：注入字典 -> import 字符串。失败返回 None。"""
        with self._lock:
            cached = self._resolved_handlers.get(trigger_type)
            if cached is not None:
                return cached

        handler_path = spec.handler
        if not handler_path or "." not in handler_path:
            _logger.warning(
                "TriggerRouter handler path invalid: trigger_type=%s path=%r",
                trigger_type,
                handler_path,
            )
            return None
        if handler_path.startswith("<injected:"):
            return None

        module_path, _, attr = handler_path.rpartition(".")
        try:
            module = importlib.import_module(module_path)
            fn = getattr(module, attr)
        except (ImportError, AttributeError) as exc:
            _logger.warning(
                "TriggerRouter handler import failed: trigger_type=%s path=%s err=%s",
                trigger_type,
                handler_path,
                exc,
            )
            return None
        if not callable(fn):
            _logger.warning(
                "TriggerRouter handler not callable: trigger_type=%s path=%s",
                trigger_type,
                handler_path,
            )
            return None

        with self._lock:
            self._resolved_handlers[trigger_type] = fn
        return fn

    # ------------------------------------------------------------------
    # 主入口：dispatch
    # ------------------------------------------------------------------

    def dispatch(
        self,
        trigger_type: str,
        payload: dict[str, Any] | None = None,
        *,
        session_id: str | None = None,
        **context: Any,
    ) -> RouterDispatchResult:
        """根据 trigger_type 分派到处理器。

        Parameters
        ----------
        trigger_type : str
            触发类型；不存在或被禁用时返回 ``skipped=True``。
        payload : dict | None
            处理器主参数（透传第一个位置参数）。
        session_id : str | None
            本次分派的 session_id（覆盖默认）。
        **context
            透传到 handler 的关键字参数。

        Returns
        -------
        RouterDispatchResult
            分派结果（永不抛出 — 失败也仅写审计 + ``success=False``）。
        """
        if not self._loaded:
            self._load()

        started = datetime.now(_UTC)
        sid = session_id if session_id is not None else self._session_id
        payload = payload or {}

        spec = self.get_spec(trigger_type)
        if spec is None:
            result = self._build_result(
                trigger_type=trigger_type,
                handler_path=None,
                success=False,
                skipped=True,
                skip_reason="unknown_trigger_type",
                error=None,
                handler_result=None,
                started=started,
            )
            self._audit_dispatch(result, sid, payload, context)
            return result

        if not spec.enabled:
            result = self._build_result(
                trigger_type=trigger_type,
                handler_path=spec.handler,
                success=False,
                skipped=True,
                skip_reason="disabled",
                error=None,
                handler_result=None,
                started=started,
            )
            self._audit_dispatch(result, sid, payload, context)
            return result

        handler = self._resolve_handler(trigger_type, spec)
        if handler is None:
            result = self._build_result(
                trigger_type=trigger_type,
                handler_path=spec.handler,
                success=False,
                skipped=True,
                skip_reason="handler_unresolvable",
                error=None,
                handler_result=None,
                started=started,
            )
            self._audit_dispatch(result, sid, payload, context)
            return result

        try:
            handler_result = handler(payload, **context)
        except Exception as exc:  # — 处理器异常必须被收敛
            result = self._build_result(
                trigger_type=trigger_type,
                handler_path=spec.handler,
                success=False,
                skipped=False,
                skip_reason="",
                error=f"{type(exc).__name__}: {exc}",
                handler_result=None,
                started=started,
            )
            self._audit_dispatch(result, sid, payload, context)
            return result

        result = self._build_result(
            trigger_type=trigger_type,
            handler_path=spec.handler,
            success=True,
            skipped=False,
            skip_reason="",
            error=None,
            handler_result=handler_result,
            started=started,
        )
        self._audit_dispatch(result, sid, payload, context)
        return result

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------

    def _build_result(
        self,
        *,
        trigger_type: str,
        handler_path: str | None,
        success: bool,
        skipped: bool,
        skip_reason: str,
        error: str | None,
        handler_result: Any,
        started: datetime,
    ) -> RouterDispatchResult:
        ended = datetime.now(_UTC)
        latency_ms = max(0, int((ended - started).total_seconds() * 1000))
        return RouterDispatchResult(
            trigger_type=trigger_type,
            handler_path=handler_path,
            success=success,
            skipped=skipped,
            skip_reason=skip_reason,
            error=error,
            handler_result=handler_result,
            dispatched_at=started.isoformat(),
            latency_ms=latency_ms,
        )

    def _audit_dispatch(
        self,
        result: RouterDispatchResult,
        session_id: str,
        payload: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        """通过审计日志记录一次 dispatch（无 logger 时仅 stdlib logging）。"""
        target = f"trigger:{result.trigger_type}"
        if result.success:
            outcome = "dispatched"
        elif result.skipped:
            outcome = f"skipped:{result.skip_reason}"
        else:
            outcome = "failed"

        extra = {
            "handler_path": result.handler_path,
            "skip_reason": result.skip_reason,
            "error": result.error,
            "latency_ms": result.latency_ms,
            "payload_keys": sorted(payload.keys()),
            "context_keys": sorted(context.keys()),
        }

        if self._audit is not None and hasattr(self._audit, "log_rule_trigger"):
            try:
                self._audit.log_rule_trigger(
                    target=target,
                    result=outcome,
                    session_id=session_id or None,
                    model=self._model,
                    extra=extra,
                )
            except Exception as exc:
                _logger.warning("TriggerRouter audit log 写入失败：%s", exc, exc_info=True)

        _logger.info(
            "TriggerRouter dispatch: trigger=%s outcome=%s handler=%s latency_ms=%d",
            result.trigger_type,
            outcome,
            result.handler_path,
            result.latency_ms,
        )


# ---------------------------------------------------------------------------
# 模块级单例
# ---------------------------------------------------------------------------

_singleton_lock = RLock()
_singleton_router: TriggerRouter | None = None


def get_trigger_router(
    *,
    config_path: Path | None = None,
    handlers: dict[str, Callable[..., Any]] | None = None,
    audit_logger: Any | None = None,
    session_id: str = "",
    reset: bool = False,
) -> TriggerRouter:
    """返回 TriggerRouter 模块级单例（线程安全）。

    生产入口：``router = get_trigger_router()``，构造时一次性加载 YAML。
    测试入口：传 ``reset=True`` + ``handlers=...`` 覆盖默认配置。
    """
    global _singleton_router
    with _singleton_lock:
        if reset or _singleton_router is None:
            _singleton_router = TriggerRouter(
                config_path=config_path,
                handlers=handlers,
                audit_logger=audit_logger,
                session_id=session_id,
            )
        return _singleton_router


def reset_trigger_router() -> None:
    """清空模块级单例（仅测试使用）。"""
    global _singleton_router
    with _singleton_lock:
        _singleton_router = None


# ---------------------------------------------------------------------------
# 默认 stub 处理器
# ---------------------------------------------------------------------------
# experimental 占位：真实处理器由后续 Phase 实现并在 YAML 中替换为 zephyr.<module>.<func>
# 这些 stub 保证 trigger_router.yaml 默认配置可被解析 + dispatch 不会失败。


def _stub_response(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "handler": name,
        "phase": "1d-stub",
        "received_keys": sorted((payload or {}).keys()),
        "note": "experimental 占位处理器 — 真实实现见后续 Phase",
    }


def handle_onboarding_stub(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """``onboarding`` — 新会话上下文注入。"""
    return _stub_response("onboarding", payload)


def handle_drift_detected(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """``drift_detected`` — 触发 DriftDetector 恢复流程。

    调用 zephyr.governance.rule_enforcement.drift_detector 模块执行偏移恢复。
    对标 MOD-INF-023 (drift-detector)。
    """
    try:
        from zephyr.governance.rule_enforcement.drift_detector import trigger_recovery

        result = trigger_recovery(payload)
        return {
            "handler": "drift_detected",
            "phase": "operational",
            "recovery_result": result,
        }
    except Exception as exc:
        _logger.warning("drift handler fallback to stub: %s", exc, exc_info=True)
        return _stub_response("drift_detected", payload)


def handle_cleanup_stub(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """``cleanup_due`` — 周期性清理孤儿快照和过期审计日志。

    调用 scripts/governance/archive_drafts_zone 执行归档。
    对标 MOD-TASK_SYSTEM (task-system) §9。
    """
    try:
        import subprocess

        result = subprocess.run(
            ["python", "scripts/governance/archive_drafts_zone.py", "--auto"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        return {
            "handler": "cleanup_due",
            "phase": "operational",
            "exit_code": result.returncode,
            "stdout_preview": result.stdout[:200] if result.stdout else "",
        }
    except Exception as exc:
        _logger.warning("cleanup handler fallback to stub: %s", exc, exc_info=True)
        return _stub_response("cleanup_due", payload)


def handle_blueprint_stub(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """``blueprint_published`` — 新蓝图发布后触发反思循环与 KE 索引。

    调用 zephyr.trading.feedback_loop.decision_engine 触发蓝图反思。
    对标 MOD-CONTEXT_ENGINE (feedback-loop) §4。
    """
    try:
        from zephyr.trading.feedback_loop.decision_engine import reflect_on_blueprint

        result = reflect_on_blueprint(payload)
        return {
            "handler": "blueprint_published",
            "phase": "operational",
            "reflection_result": result,
        }
    except Exception as exc:
        _logger.warning("blueprint_published handler fallback to stub: %s", exc, exc_info=True)
        return _stub_response("blueprint_published", payload)


def handle_blueprint_lookup_stub(payload: dict[str, Any], **_: Any) -> dict[str, Any]:
    """``blueprint_lookup`` — 根据文件路径/任务关键字匹配蓝图路由。

    此 handler 读取 ``config/blueprint_routing.yaml`` 并执行两级匹配：
    1. **path_patterns**（精确）—— glob 匹配当前改动的文件路径
    2. **task_keywords**（模糊）—— 关键字命中计数

    返回匹配的蓝图列表，按 priority 降序排列。
    对标 Codified Context (arXiv 2602.20478) §3.1.1 Orchestration Protocols。

    统一打分逻辑：shared/blueprint_scorer.py（与 MCP blueprint_search_server 共用）。
    """
    from zephyr.orchestrator.quality.blueprint_scorer import score_and_rank_routes

    routing_yaml_path = REPO_ROOT / "config" / "blueprint_routing.yaml"
    if not routing_yaml_path.exists():
        _logger.warning("blueprint_routing.yaml not found at %s", routing_yaml_path)
        return {
            "matched": [],
            "source": "blueprint_routing.yaml",
            "error": "routing_file_not_found",
        }

    try:
        with open(routing_yaml_path, encoding="utf-8") as fh:
            # 5.155.8 修复: 添加类型校验, 防止空YAML返回None时.get()抛AttributeError
            routing_config = yaml.safe_load(fh)
            if not isinstance(routing_config, dict):
                routing_config = {}
    except Exception as exc:
        _logger.error("failed to load blueprint_routing.yaml: %s", exc, exc_info=True)
        return {
            "matched": [],
            "source": "blueprint_routing.yaml",
            "error": f"parse_error: {exc}",
        }

    routes = routing_config.get("routes", [])
    path_patterns = payload.get("path_patterns", []) or []
    task_keywords = payload.get("task_keywords", []) or []
    task_text = payload.get("task_text", "") or ""

    scored = score_and_rank_routes(routes, path_patterns, task_keywords, task_text)

    matched = []
    for match_score, match_priority, route in scored:
        matched.append(
            {
                "blueprint_id": route["blueprint_id"],
                "blueprint_level": route.get("blueprint_level", "module"),
                "route_id": route.get("route_id", ""),
                "match_score": match_score,
                "route_priority": match_priority,
                "description": route.get("description", ""),
            }
        )

    return {
        "matched": matched,
        "count": len(matched),
        "source": "config/blueprint_routing.yaml",
        "strategy": "unified_path_and_keyword_scorer",
        "hint": "AI SHOULD read top-3 blueprints §1 (system boundary + topology) before code changes",
    }
