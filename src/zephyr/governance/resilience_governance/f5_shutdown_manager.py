# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §2
# [MODULE] zephyr.governance.resilience_governance.f5_shutdown_manager
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES]
# [CONSUMERS] zephyr.governance.f5_boot_integration; zephyr.trading.boot_hooks
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] shutdown is idempotent; signal handlers never raise; atexit hook safe to call multiple times; persist_state writes atomic; restore_state never raises
# [MODIFY-GUARD] signal handler registration name must be "f5_shutdown_signal"; atexit registration name must be "f5_shutdown_atexit"; SQLite table must be "f5_state"
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns ShutdownResult; logs error on failure; never raises during shutdown; signal handler swallows exceptions
# [TESTS] tests/test_f5_auto_shutdown.py
# [A_module] module_id=MOD-RES_f5_shutdown_manager | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
F5ShutdownManager — F5 自动关闭/状态持久化/信号处理 (MOD-INF-022 §2).

F5 = EscalationProtocol 五件套: EscalationEngine + DelegationEngine + DeadlockDetector
+ Arbitrator + EscalationAPI. 本模块负责 F5 系统的优雅关闭:

1. shutdown 资源清理: 清理 DeadlockDetector 等待图 / 释放锁 / 清理审计日志
2. 状态持久化到 SQLite: serialize DeadlockDetector 状态 / 审计日志 / 委托历史
3. SIGINT/SIGTERM 信号处理: 注册 signal handler, 收到信号时触发 shutdown
4. atexit.register 兜底: 注册 atexit 钩子, 进程退出时确保 shutdown 执行
5. 10 分钟空闲自动回收: idle_timeout 检测, 长时间无活动自动关闭
6. 状态恢复: 从 SQLite 恢复 DeadlockDetector 状态 (供下次启动使用)
"""
from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import atexit
import json
import logging
import os
import signal
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 5.66.6 修复：表名白名单，防止 f-string 拼接表名的 SQL 注入风险。
# F5ShutdownManager 仅操作 f5_state 表（STATE_TABLE 类常量）。
_ALLOWED_TABLES = frozenset({"f5_state"})


def _validate_table_name(table: str) -> str:
    """5.66.6 修复：白名单校验表名，仅允许已知表名用于 SQL 拼接。"""
    if table not in _ALLOWED_TABLES:
        raise ValueError(f"table name not in whitelist: {table!r}")
    return table


@dataclass
class ShutdownResult:
    """关闭/持久化结果。"""
    success: bool
    component: str
    errors: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


class F5ShutdownManager:
    """F5 系统关闭/持久化/信号处理管理器。

    生命周期:
    1. install() — 注册 signal handler + atexit 钩子 + 启动 idle 监控线程
    2. shutdown() — 资源清理 + 状态持久化 (幂等, 可被 signal/atexit/idle 调用)
    3. restore_state() — 从 SQLite 恢复 DeadlockDetector 状态 (供下次启动)

    使用方式:
        integration = F5BootIntegration()
        integration.on_startup()
        manager = F5ShutdownManager(integration=integration)
        manager.install()  # 注册 signal + atexit + idle 监控
        # ... 系统运行 ...
        manager.update_activity()  # 任何 F5 操作后调用, 重置 idle 计时
        # 关闭时:
        manager.shutdown()  # 或被 signal/atexit/idle 自动调用
    """

    IDLE_TIMEOUT_SECONDS = 600.0  # 10 分钟
    SIGNAL_HANDLER_NAME = "f5_shutdown_signal"
    ATEXIT_HANDLER_NAME = "f5_shutdown_atexit"
    STATE_TABLE = "f5_state"

    def __init__(
        self,
        integration: object = None,
        project_root: Path | None = None,
        db_path: Path | None = None,
        idle_timeout_seconds: float | None = None,
    ) -> None:
        self._integration = integration
        self._project_root = project_root or Path.cwd()
        # 默认数据库路径: data/databases/governance.db
        if db_path is None:
            db_path = self._project_root / "data" / "databases" / "governance.db"
        self._db_path = db_path
        self._idle_timeout = (
            idle_timeout_seconds if idle_timeout_seconds is not None else self.IDLE_TIMEOUT_SECONDS
        )
        self._last_activity = time.monotonic()
        self._shutdown_done = False
        self._lock = threading.Lock()
        self._installed = False
        # 事件驱动 idle 计时器（debounce 模式）：每次 update_activity() 重置 timer，
        # timer 到期触发 _on_idle_timeout -> shutdown。替代原 sleep-loop 轮询线程，
        # 满足"永久系统主触发必须事件驱动"铁律。
        self._idle_timer: threading.Timer | None = None
        self._previous_sigint = None
        self._previous_sigterm = None
        self._atexit_registered = False

    # ------------------------------------------------------------------ #
    # 安装: signal + atexit + idle 监控
    # ------------------------------------------------------------------ #
    def install(self) -> ShutdownResult:
        """注册 signal handler + atexit 钩子 + 启动 idle 计时器 (幂等，事件驱动)。"""
        if self._installed:
            return ShutdownResult(
                success=True,
                component="f5_shutdown_install",
                details={"already_installed": True},
            )
        errors: list[str] = []
        details: dict = {}

        # 1. 注册 SIGINT/SIGTERM 信号处理
        try:
            self._previous_sigint = signal.getsignal(signal.SIGINT)
            self._previous_sigterm = signal.getsignal(signal.SIGTERM)
            signal.signal(signal.SIGINT, self._on_signal)
            signal.signal(signal.SIGTERM, self._on_signal)
            details["signal_handlers_registered"] = True
            logger.info("F5ShutdownManager: SIGINT/SIGTERM handlers registered")
        except (ValueError, OSError) as e:
            # 非主线程无法注册 signal handler — 仅记录, 不阻断
            errors.append(f"signal handler registration failed: {e}")
            logger.warning("F5ShutdownManager: signal handler registration failed: %s", e, exc_info=True)

        # 2. 注册 atexit 兜底
        try:
            atexit.register(self._on_atexit)
            self._atexit_registered = True
            details["atexit_registered"] = True
            logger.info("F5ShutdownManager: atexit hook registered")
        except Exception as e:
            errors.append(f"atexit registration failed: {e}")
            logger.warning("F5ShutdownManager: atexit registration failed: %s", e, exc_info=True)

        # 3. 启动 idle 计时器（事件驱动 one-shot timer）
        try:
            self._reschedule_idle_timer()
            details["idle_monitor_started"] = True
            details["idle_timeout_seconds"] = self._idle_timeout
        except Exception as e:
            errors.append(f"idle monitor start failed: {e}")
            logger.warning("F5ShutdownManager: idle monitor start failed: %s", e, exc_info=True)

        self._installed = True
        return ShutdownResult(
            success=len(errors) == 0,
            component="f5_shutdown_install",
            errors=errors,
            details=details,
        )

    def uninstall(self) -> None:
        """卸载 signal handler + 取消 idle 计时器 (供测试使用)。"""
        self._cancel_idle_timer()

        # 恢复之前的 signal handler
        try:
            if self._previous_sigint is not None:
                signal.signal(signal.SIGINT, self._previous_sigint)
            if self._previous_sigterm is not None:
                signal.signal(signal.SIGTERM, self._previous_sigterm)
        except (ValueError, OSError):
            pass

        self._installed = False

    # ------------------------------------------------------------------ #
    # 关闭: 资源清理 + 状态持久化
    # ------------------------------------------------------------------ #
    def shutdown(self) -> ShutdownResult:
        """执行 F5 关闭流程 (幂等)。

        1. 调用 F5BootIntegration.on_shutdown() 清理资源
        2. 持久化 DeadlockDetector 状态 / 审计日志 / 委托历史 到 SQLite
        3. 停止 idle 监控线程
        """
        with self._lock:
            if self._shutdown_done:
                return ShutdownResult(
                    success=True,
                    component="f5_shutdown",
                    details={"already_shutdown": True},
                )
            self._shutdown_done = True

        errors: list[str] = []
        details: dict = {}

        # 1. 取消 idle 计时器
        try:
            self._cancel_idle_timer()
        except Exception as e:
            errors.append(f"idle timer cancel failed: {e}")

        # 2. 持久化状态 (在 on_shutdown 之前, 因为 on_shutdown 会清理状态)
        try:
            persist_result = self.persist_state()
            details["persist_result"] = persist_result.details
            if not persist_result.success:
                errors.extend(persist_result.errors)
        except Exception as e:
            errors.append(f"persist_state failed: {e}")
            logger.error("F5ShutdownManager: persist_state failed: %s", e, exc_info=True)

        # 3. 调用 F5BootIntegration.on_shutdown() 清理资源
        if self._integration is not None:
            try:
                boot_result = self._integration.on_shutdown()
                details["boot_shutdown"] = boot_result.details
                if not boot_result.success:
                    errors.extend(boot_result.errors)
            except Exception as e:
                errors.append(f"integration on_shutdown failed: {e}")
                logger.error("F5ShutdownManager: integration on_shutdown failed: %s", e, exc_info=True)

        return ShutdownResult(
            success=len(errors) == 0,
            component="f5_shutdown",
            errors=errors,
            details=details,
        )

    # ------------------------------------------------------------------ #
    # 状态持久化
    # ------------------------------------------------------------------ #
    def persist_state(self) -> ShutdownResult:
        """将 F5 状态持久化到 SQLite (原子写入)。

        持久化内容:
        - DeadlockDetector.serialize() — 等待图 / 锁 / 抢占顺序
        - EscalationAPI.get_audit_log() — 审计日志
        - Arbitrator.get_audit_log() — 仲裁审计日志
        - DelegationEngine.get_delegation_history() — 委托历史
        """
        errors: list[str] = []
        details: dict = {}

        # 收集状态
        state_payload: dict[str, Any] = {
            "timestamp": time.time(),
            "deadlock_state": None,
            "escalation_audit_log": None,
            "arbitrator_audit_log": None,
            "delegation_history": None,
        }

        integration = self._integration
        if integration is not None:
            # DeadlockDetector 状态
            deadlock = getattr(integration, "deadlock_detector", None)
            if deadlock is not None:
                try:
                    state_payload["deadlock_state"] = deadlock.serialize()
                    details["deadlock_state_captured"] = True
                except Exception as e:
                    errors.append(f"deadlock serialize failed: {e}")

            # EscalationAPI 审计日志 (通过 escalation_engine 获取, 若有)
            escalation_engine = getattr(integration, "escalation_engine", None)
            if escalation_engine is not None:
                try:
                    # EscalationEngine 可能有 _recent_escalations, 不属于审计日志
                    # 真正的审计日志在 EscalationAPI 中, 但 F5BootIntegration 未直接持有
                    # 这里捕获 escalation_engine 的可序列化状态
                    active_count = escalation_engine.get_active_count() if hasattr(
                        escalation_engine, "get_active_count"
                    ) else 0
                    state_payload["escalation_audit_log"] = {
                        "active_count": int(active_count),
                    }
                    details["escalation_state_captured"] = True
                except Exception as e:
                    errors.append(f"escalation state capture failed: {e}")

            # Arbitrator 审计日志
            arbitrator = getattr(integration, "arbitrator", None)
            if arbitrator is not None:
                try:
                    state_payload["arbitrator_audit_log"] = arbitrator.get_audit_log()
                    details["arbitrator_audit_log_captured"] = True
                except Exception as e:
                    errors.append(f"arbitrator audit log capture failed: {e}")

            # DelegationEngine 委托历史
            delegation = getattr(integration, "delegation_engine", None)
            if delegation is not None:
                try:
                    history = delegation.get_delegation_history()
                    # DelegationRecord 是 dataclass, 转为 dict
                    state_payload["delegation_history"] = [
                        self._serialize_record(r) for r in history
                    ]
                    details["delegation_history_captured"] = True
                    details["delegation_history_count"] = len(history)
                except Exception as e:
                    errors.append(f"delegation history capture failed: {e}")

        # 写入 SQLite (原子写入: 先写临时文件, 再 replace)
        try:
            self._write_state_to_db(state_payload)
            details["db_path"] = str(self._db_path)
            details["state_written"] = True
        except Exception as e:
            errors.append(f"db write failed: {e}")
            logger.error("F5ShutdownManager: db write failed: %s", e, exc_info=True)

        return ShutdownResult(
            success=len(errors) == 0,
            component="f5_persist_state",
            errors=errors,
            details=details,
        )

    def _write_state_to_db(self, payload: dict[str, Any]) -> None:
        """将状态写入 SQLite (原子写入)。"""
        # 5.66.6 修复：白名单校验表名后再用于 f-string 拼接
        safe_table = _validate_table_name(self.STATE_TABLE)
        # 确保目录存在
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        # 原子写入: 先写到临时文件, 再 replace
        # SQLite 本身不支持原子 rename db 文件, 但我们可以用临时 db + replace
        # 这里直接用 sqlite3 连接 + INSERT, SQLite 的写入是原子的 (单条 INSERT)
        conn = get_db_connection(str(self._db_path), timeout=5.0)
        try:
            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {safe_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            # 清空旧状态 (单表, 只保留最新)
            conn.execute(f"DELETE FROM {safe_table}")
            # 写入新状态
            for key, value in payload.items():
                conn.execute(
                    f"INSERT INTO {safe_table} (key, value, updated_at) VALUES (?, ?, ?)",
                    (key, dumps(value), payload.get("timestamp", time.time())),
                )
            conn.commit()
        finally:
            conn.close()

    def _serialize_record(self, record: object) -> dict:
        """将 DelegationRecord (dataclass) 序列化为 dict。"""
        if hasattr(record, "__dict__"):
            result = {}
            for k, v in record.__dict__.items():
                if hasattr(v, "isoformat"):
                    result[k] = v.isoformat()
                elif hasattr(v, "value") and hasattr(v, "name"):
                    # Enum
                    result[k] = v.value
                else:
                    result[k] = v
            return result
        return {"repr": repr(record)}

    # ------------------------------------------------------------------ #
    # 状态恢复
    # ------------------------------------------------------------------ #
    def restore_state(self) -> ShutdownResult:
        """从 SQLite 恢复 F5 状态 (供下次启动使用)。

        恢复内容:
        - DeadlockDetector 状态 (等待图 / 锁 / 抢占顺序)
        - 不恢复审计日志和委托历史 (这些是历史记录, 不需要恢复)

        返回恢复的状态字典。
        """
        errors: list[str] = []
        details: dict = {}

        if not self._db_path.exists():
            return ShutdownResult(
                success=True,
                component="f5_restore_state",
                details={"db_exists": False, "restored": False},
            )

        try:
            state = self._read_state_from_db()
            details["state_read"] = True
            details["keys"] = list(state.keys())

            # 恢复 DeadlockDetector 状态
            deadlock_state = state.get("deadlock_state")
            if deadlock_state is not None and self._integration is not None:
                deadlock = getattr(self._integration, "deadlock_detector", None)
                if deadlock is not None:
                    try:
                        self._restore_deadlock_state(deadlock, deadlock_state)
                        details["deadlock_state_restored"] = True
                    except Exception as e:
                        errors.append(f"deadlock restore failed: {e}")

        except Exception as e:
            errors.append(f"db read failed: {e}")
            logger.error("F5ShutdownManager: db read failed: %s", e, exc_info=True)

        return ShutdownResult(
            success=len(errors) == 0,
            component="f5_restore_state",
            errors=errors,
            details=details,
        )

    def _read_state_from_db(self) -> dict[str, Any]:
        """从 SQLite 读取状态。"""
        # 5.66.6 修复：白名单校验表名后再用于 f-string 拼接
        safe_table = _validate_table_name(self.STATE_TABLE)
        conn = get_db_connection(str(self._db_path), timeout=5.0)
        try:
            cursor = conn.execute(
                f"SELECT key, value FROM {safe_table}"
            )
            result: dict[str, Any] = {}
            for key, value in cursor.fetchall():
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            return result
        finally:
            conn.close()

    def _restore_deadlock_state(self, deadlock: object, state: dict) -> None:
        """恢复 DeadlockDetector 状态。"""
        wait_graph = state.get("wait_graph", {})
        locks = state.get("locks", {})
        preemption_order = state.get("preemption_order", [])

        # 恢复等待图
        if hasattr(deadlock, "_wait_graph"):
            deadlock._wait_graph.clear()
            for waiter, holders in wait_graph.items():
                deadlock._wait_graph[waiter] = set(holders)

        # 恢复锁 (注意: lock_timestamps 无法恢复, 因为是 monotonic 时间)
        if hasattr(deadlock, "_locks"):
            deadlock._locks.clear()
            for resource, holder in locks.items():
                deadlock._locks[resource] = holder
            # 重建 lock_timestamps (用当前 monotonic 时间)
            if hasattr(deadlock, "_lock_timestamps"):
                deadlock._lock_timestamps.clear()
                now = time.monotonic()
                for resource in locks:
                    deadlock._lock_timestamps[resource] = now

        # 恢复抢占顺序
        if hasattr(deadlock, "_preemption_order"):
            deadlock._preemption_order = list(preemption_order)

    # ------------------------------------------------------------------ #
    # 信号处理 / atexit / idle 监控
    # ------------------------------------------------------------------ #
    def _on_signal(self, signum, frame) -> None:
        """SIGINT/SIGTERM 信号处理 (永不抛异常)。"""
        try:
            sig_name = signal.Signals(signum).name
        except (ValueError, AttributeError):
            sig_name = f"signal-{signum}"
        logger.info("F5ShutdownManager: received %s, triggering shutdown", sig_name)
        try:
            self.shutdown()
        except Exception as e:
            # 信号处理永不抛异常
            logger.error("F5ShutdownManager: shutdown in signal handler failed: %s", e, exc_info=True)

    def _on_atexit(self) -> None:
        """atexit 兜底钩子 (永不抛异常)。"""
        logger.info("F5ShutdownManager: atexit triggered, running shutdown")
        try:
            self.shutdown()
        except Exception as e:
            logger.error("F5ShutdownManager: shutdown in atexit failed: %s", e, exc_info=True)

    def _reschedule_idle_timer(self) -> None:
        """重置 idle 计时器（debounce 模式）。

        取消前一个 timer（若存在）并安排新的 one-shot timer。
        timer 到期后调用 _on_idle_timeout 触发自动关闭。
        """
        self._cancel_idle_timer()
        if self._shutdown_done:
            return
        self._last_activity = time.monotonic()
        self._idle_timer = threading.Timer(
            self._idle_timeout,
            self._on_idle_timeout,
        )
        self._idle_timer.daemon = True
        self._idle_timer.name = "f5_idle_timer"
        self._idle_timer.start()

    def _cancel_idle_timer(self) -> None:
        """取消当前 idle 计时器（若存在）。"""
        timer = self._idle_timer
        if timer is not None:
            try:
                timer.cancel()
            except Exception:
                pass
            self._idle_timer = None

    def _on_idle_timeout(self) -> None:
        """idle 计时器到期回调：触发自动关闭（事件驱动，无轮询）。"""
        if self._shutdown_done:
            return
        try:
            logger.info(
                "F5ShutdownManager: idle timeout (%.0fs) reached, auto-shutdown",
                self._idle_timeout,
            )
            self.shutdown()
        except Exception as e:
            logger.error("F5ShutdownManager: idle timeout callback error: %s", e, exc_info=True)

    def update_activity(self) -> None:
        """更新最后活动时间 (重置 idle 计时器)。

        任何 F5 操作 (escalation / delegation / arbitration) 后应调用。
        触发 timer 重排（事件驱动），替代原 sleep-loop 轮询。
        """
        self._reschedule_idle_timer()

    # ------------------------------------------------------------------ #
    # 属性
    # ------------------------------------------------------------------ #
    @property
    def is_shutdown(self) -> bool:
        return self._shutdown_done

    @property
    def is_installed(self) -> bool:
        return self._installed

    @property
    def last_activity(self) -> float:
        return self._last_activity

    @property
    def idle_timeout_seconds(self) -> float:
        return self._idle_timeout

    @property
    def db_path(self) -> Path:
        return self._db_path


def register_f5_shutdown_hook(
    integration: object = None,
    project_root: Path | None = None,
    db_path: Path | None = None,
) -> F5ShutdownManager:
    """模块级便捷函数: 创建 F5ShutdownManager 并 install。

    供 zephyr.trading.boot_hooks 在 F5 启动后调用。
    """
    manager = F5ShutdownManager(
        integration=integration,
        project_root=project_root,
        db_path=db_path,
    )
    manager.install()
    return manager