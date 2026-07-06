# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.utils.logging
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_logging | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
logging.py —— ZephyrAlpha 结构化日志系统（Structured JSON Logger）

Phase 4 新增（盲点 B2）——解决此前各模块 print()/logging 混用、日志不可 grep、
AI 排障时无法快速定位根因的问题。

设计原则：
  - 强制结构化 JSON 输出——每条日志 MUST 包含 module_id, session_id, trace_id
  - 零外部依赖——基于 Python 标准库 logging 构建
  - contextvars 实现 trace_id 跨调用链自动传播（无需手动传参）
  - 人类可读 [控制台] 和 JSON [文件] 双模式——开发时不牺牲可读性

对标：
  - Google Cloud Logging: structured JSON with required fields
  - structlog (Python 社区标杆): 键值对日志 + 上下文绑定
  - 12-Factor App: 日志作为事件流，stdout 输出

AI 施工约定：
  - 所有模块 MUST 使用 get_logger(__name__) 获取日志器
  - 禁止直接使用 print() 或裸 logging.getLogger()
  - trace_id 通过 TraceContext 上下文管理器自动传播

SSoT: MOD-INF-016 §2.10 shared-logging
Version: 0.1.0
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import contextvars
import datetime
import logging
import sys
import uuid
from contextlib import contextmanager
from typing import Any

__all__ = [
    "LogLevel",
    "TraceContext",
    "ZephyrLogger",
    "configure_root_logger",
    "get_logger",
    "module_id_var",
    "request_id_var",
    "session_id_var",
    "trace_id_var",
]

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")
session_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("session_id", default="")
module_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("module_id", default="")
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class _StructuredFormatter(logging.Formatter):
    """JSON 行格式化器——每条日志一行 JSON，可直接 tail | jq 解析。"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.datetime.fromtimestamp(record.created, tz=datetime.UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module_id": getattr(record, "z_module_id", "") or module_id_var.get(),
            "session_id": getattr(record, "z_session_id", "") or session_id_var.get(),
            "trace_id": getattr(record, "z_trace_id", "") or trace_id_var.get(),
            "request_id": getattr(record, "z_request_id", "") or request_id_var.get(),
        }

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        extra = getattr(record, "z_extra", None)
        if extra:
            log_entry["extra"] = extra

        return dumps(log_entry, ensure_ascii=False)


class _HumanFormatter(logging.Formatter):
    """控制台人类可读格式化器——带颜色级别标记 + trace_id 截断。"""

    _COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    _RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelname, "")
        trace_id = getattr(record, "z_trace_id", "") or trace_id_var.get()
        trace_short = trace_id[:8] if trace_id else "--------"

        base = (
            f"[{self.formatTime(record, self.datefmt)}] "
            f"{color}{record.levelname:<8}{self._RESET} "
            f"[{trace_short}] "
            f"{record.name}: "
            f"{record.getMessage()}"
        )

        extra = getattr(record, "z_extra", None)
        if extra:
            base += f" | {dumps(extra, ensure_ascii=False)}"

        if record.exc_info and record.exc_info[1] is not None:
            base += f"\n  └─ {type(record.exc_info[1]).__name__}: {record.exc_info[1]}"

        return base


class ZephyrLogger:
    """ZephyrAlpha 结构化日志器。

    每次日志调用自动注入 trace_id / session_id / module_id 到 log record，
    由 formatter 统一序列化。额外上下文通过 extra= 关键字传递（可选 dict）。
    """

    def __init__(self, name: str, *, json_output: bool = False) -> None:
        self._logger = logging.getLogger(name)
        self._name = name

    def _log(
        self,
        level: int,
        msg: str,
        *,
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        trace_id = trace_id_var.get()
        session_id = session_id_var.get()
        module_id = module_id_var.get()
        request_id = request_id_var.get()

        kwargs: dict[str, Any] = {
            "extra": {
                "z_trace_id": trace_id,
                "z_session_id": session_id,
                "z_module_id": module_id,
                "z_request_id": request_id,
                "z_extra": extra,
            }
        }
        if exc_info:
            kwargs["exc_info"] = True

        self._logger.log(level, msg, **kwargs)

    def debug(self, msg: str, *, extra: dict[str, Any] | None = None) -> None:
        self._log(logging.DEBUG, msg, extra=extra)

    def info(self, msg: str, *, extra: dict[str, Any] | None = None) -> None:
        self._log(logging.INFO, msg, extra=extra)

    def warning(self, msg: str, *, extra: dict[str, Any] | None = None) -> None:
        self._log(logging.WARNING, msg, extra=extra)

    def error(
        self,
        msg: str,
        *,
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        self._log(logging.ERROR, msg, extra=extra, exc_info=exc_info)

    def critical(
        self,
        msg: str,
        *,
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        self._log(logging.CRITICAL, msg, extra=extra, exc_info=exc_info)

    def bind(self, **kwargs: Any) -> _BoundLogger:
        """返回绑定额外上下文的日志器代理——每次调用自动合并 extra。"""
        return _BoundLogger(self, kwargs)


class _BoundLogger:
    """绑定常驻上下文的日志器代理。"""

    def __init__(self, logger: ZephyrLogger, bound_extra: dict[str, Any]) -> None:
        self._logger = logger
        self._bound = bound_extra

    def _merge_extra(self, extra: dict[str, Any] | None) -> dict[str, Any]:
        merged = dict(self._bound)
        if extra:
            merged.update(extra)
        return merged

    def debug(self, msg: str, *, extra: dict[str, Any] | None = None) -> None:
        self._logger.debug(msg, extra=self._merge_extra(extra))

    def info(self, msg: str, *, extra: dict[str, Any] | None = None) -> None:
        self._logger.info(msg, extra=self._merge_extra(extra))

    def warning(self, msg: str, *, extra: dict[str, Any] | None = None) -> None:
        self._logger.warning(msg, extra=self._merge_extra(extra))

    def error(
        self,
        msg: str,
        *,
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        self._logger.error(msg, extra=self._merge_extra(extra), exc_info=exc_info)

    def critical(
        self,
        msg: str,
        *,
        extra: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        self._logger.critical(msg, extra=self._merge_extra(extra), exc_info=exc_info)


_logger_cache: dict[str, ZephyrLogger] = {}


def get_logger(
    name: str,
    *,
    session_id: str | None = None,
    module_id: str | None = None,
) -> ZephyrLogger:
    """获取或创建 ZephyrLogger 实例。

    首次调用时，自动将 session_id / module_id 注入 contextvars，
    后续该模块内所有日志调用自动携带上下文。

    Args:
        name: 日志器名称（通常传 __name__）
        session_id: 可选会话ID
        module_id: 可选模块ID

    Returns:
        ZephyrLogger 实例
    """
    if name not in _logger_cache:
        _logger_cache[name] = ZephyrLogger(name)
    logger = _logger_cache[name]

    if session_id:
        session_id_var.set(session_id)
    if module_id:
        module_id_var.set(module_id)

    return logger


@contextmanager
def TraceContext(
    trace_id: str | None = None,
    *,
    session_id: str | None = None,
    module_id: str | None = None,
    request_id: str | None = None,
):
    """trace_id 传播上下文管理器。

    在 with 块内，所有日志调用自动携带指定的 trace_id / session_id / module_id / request_id。
    嵌套 TraceContext 时，内层恢复外层 token。

    用法:
        with TraceContext() as tc:
            log.info("inside trace")
            # 也可以子函数中嵌套:
            with TraceContext() as tc2:
                log.info("sub-trace")

        with TraceContext(session_id="sess-001", module_id="MOD-INF-016", request_id="req-abc"):
            log.info("scoped log")
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    token_trace = trace_id_var.set(trace_id)
    token_session = session_id_var.set(session_id or trace_id_var.get())
    token_module = module_id_var.set(module_id or module_id_var.get())
    token_request = request_id_var.set(request_id or request_id_var.get())

    try:
        yield trace_id
    finally:
        trace_id_var.reset(token_trace)
        session_id_var.reset(token_session)
        module_id_var.reset(token_module)
        request_id_var.reset(token_request)


_root_configured = False


def configure_root_logger(
    *,
    level: str = "INFO",
    json_file: str | None = None,
    human_console: bool = True,
) -> None:
    """配置根日志器——全局生效的 handler 和 format。

    应在应用入口（如 main.py / cli.py）调用一次。

    Args:
        level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
        json_file: 可选 JSON 日志输出文件路径（None = 不写文件）
        human_console: 是否启用控制台人类可读输出
    """
    global _root_configured
    if _root_configured:
        return
    _root_configured = True

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    root.handlers.clear()

    if human_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(_HumanFormatter(datefmt="%H:%M:%S"))
        root.addHandler(console_handler)

    if json_file:
        file_handler = logging.FileHandler(json_file, encoding="utf-8")
        file_handler.setFormatter(_StructuredFormatter())
        root.addHandler(file_handler)
