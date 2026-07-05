# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.circuit_breaker
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.shared.utils.db_utils; zephyr.shared.security.capability
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_circuit_breaker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CircuitBreakerGateway (CBG) — 模块间调用单向熔断器
===================================================
任务编号 : T-V2-005（experimental）
权限层级 : Immutable Core
真源声明 : ai_autonomy_authority_registry.yaml §2.10
关联决策 : rationale-log R81 C-02（experimental 只实现 CLOSED→OPEN 单向）
           rationale-log R83（B6 §2.2 CBG 设计）
创建日期 : 2026-04-27
版本     : v1.0.0

设计约束（C-02 裁决）
--------------------
- experimental 只实现 CLOSED → OPEN 单向（不实现 HALF_OPEN）
- OPEN 状态后由 Owner 通过 CLI `cbg.reset(caller, target)` 手动恢复
- beta（Agent ≥ 3 时）升级为完整状态机（含 HALF_OPEN 探测）
- 零新外部依赖：全部基于 SQLite + stdlib

功能说明
--------
1. CircuitBreakerState — 状态枚举（CLOSED / OPEN，experimental 无 HALF_OPEN）
2. CircuitBreakerRecord — SQLite circuit_breaker_state 表的内存镜像
3. CircuitBreakerCheck  — 继承 gate_engine GateCheck 接口，注册第 17 种 CheckType
4. @circuit_breaker(target_module)  — 装饰器，自动统计失败次数并触发 CLOSED→OPEN
5. CBGManager — 状态查询 / 手动重置 / 批量刷新

装饰器用法
----------
    from zephyr.governance.rule_enforcement.circuit_breaker import circuit_breaker

    @circuit_breaker(target_module="M2")
    def call_m2():
        ...

CLOSED 状态：装饰器零运行时开销（仅在抛出异常时写 SQLite）。
OPEN 状态：调用立即抛出 CircuitOpenError，不执行被装饰函数。
"""

from __future__ import annotations

import functools
import os
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

from zephyr.shared.security.capability import capability_check
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.utils.db_utils import get_db_connection, init_db

__all__ = [
    "DEFAULT_THRESHOLD",
    "CBGManager",
    "CircuitBreakerCheck",
    "CircuitBreakerRecord",
    "CircuitBreakerState",
    "CircuitOpenError",
    "circuit_breaker",
]

_F = TypeVar("_F", bound=Callable[..., Any])
_UTC = UTC

# ---------------------------------------------------------------------------
# 配置常量
# ---------------------------------------------------------------------------

# 默认触发 OPEN 的连续失败次数；可用环境变量 ZEPHYR_CBG_FAILURE_THRESHOLD 覆盖。
# 5.155.3 修复: 添加 try/except 防止非整数环境变量值导致模块导入失败
try:
    DEFAULT_THRESHOLD: int = int(os.environ.get("ZEPHYR_CBG_FAILURE_THRESHOLD", "3"))
except (TypeError, ValueError):
    DEFAULT_THRESHOLD = 3

_CALLER_UNKNOWN: str = "__unknown__"

# ---------------------------------------------------------------------------
# 状态枚举（仅 CLOSED / OPEN）
# ---------------------------------------------------------------------------


class CircuitBreakerState(str, Enum):
    """熔断器状态枚举。

    experimental 约束（C-02 裁决）：
    - CLOSED：正常放行，失败计数累积中
    - OPEN：熔断，调用立即被阻断
    - HALF_OPEN：仅定义，experimental 不使用（beta 升级时启用）
    """

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"  # beta 预留，experimental 不写入数据库


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass
class CircuitBreakerRecord:
    """circuit_breaker_state 表的内存镜像。"""

    caller_module: str
    target_module: str
    state: CircuitBreakerState
    failure_count: int = 0
    last_failure_at: str | None = None
    opened_at: str | None = None
    reason: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(_UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(_UTC).isoformat())


# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class CircuitOpenError(RuntimeError):
    """OPEN 状态下调用被阻断时抛出。"""

    def __init__(self, caller: str, target: str, reason: str | None = None) -> None:
        self.caller = caller
        self.target = target
        self.reason = reason
        msg = f"CircuitBreaker OPEN: {caller} → {target}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


# ---------------------------------------------------------------------------
# CircuitBreakerCheck（GateEngine 第 17 种 CheckType 接口）
# ---------------------------------------------------------------------------


@dataclass
class CircuitBreakerCheck:
    """GateEngine 第 17 种 CheckType 实现接口。

    在 gate_engine.py `_run_check()` 分发块中以 ct == "circuit_breaker" 触发。
    本类封装针对具体 (caller_module, target_module) 对的熔断状态查询。

    典型 YAML 配置（gates/g1-ingest.yaml 等）：
        checks:
          - id: CB-L2a
            name: L2a 熔断检查
            type: circuit_breaker
            severity: error
            params:
              caller_module: RI-05
              target_module: L2a
    """

    caller_module: str
    target_module: str
    db_path: Path | None = None

    def is_open(self) -> bool:
        """返回 True 表示熔断器当前处于 OPEN 状态。"""
        manager = CBGManager(self.db_path)
        record = manager.get_state(self.caller_module, self.target_module)
        return record is not None and record.state is CircuitBreakerState.OPEN

    def violation_message(self) -> str:
        """返回熔断触发的可读违规信息（含 caller / target 标识）。"""
        return (
            f"CircuitBreaker OPEN: {self.caller_module} → {self.target_module} "
            f"（调用被熔断，请由 Owner 执行 `cbg.reset()` 后重试）"
        )


# ---------------------------------------------------------------------------
# CBGManager — 状态读写核心
# ---------------------------------------------------------------------------


class CBGManager:
    """熔断器状态管理器：SQLite circuit_breaker_state 表的 CRUD 封装。

    参数
    ----
    db_path
        SQLite 数据库路径；默认 DB_PATH。
    auto_init
        首次使用时是否幂等初始化 DB；默认 True。
    """

    def __init__(
        self,
        db_path: Path | str | None = None,
        *,
        auto_init: bool = True,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        if auto_init:
            init_db(self._db_path)
        self._conn: sqlite3.Connection = get_db_connection(self._db_path)

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def get_state(self, caller: str, target: str) -> CircuitBreakerRecord | None:
        """查询指定 (caller, target) 对的熔断状态。

        不存在记录时返回 None（视为 CLOSED）。
        """
        row = self._conn.execute(
            "SELECT * FROM circuit_breaker_state WHERE caller_module = ? AND target_module = ?",
            (caller, target),
        ).fetchone()
        if row is None:
            return None
        return CircuitBreakerRecord(
            caller_module=row["caller_module"],
            target_module=row["target_module"],
            state=CircuitBreakerState(row["state"]),
            failure_count=row["failure_count"],
            last_failure_at=row["last_failure_at"],
            opened_at=row["opened_at"],
            reason=row["reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def is_open(self, caller: str, target: str) -> bool:
        """快速判断 (caller, target) 是否处于 OPEN 状态。

        记录不存在时视为 CLOSED → 返回 False。
        """
        record = self.get_state(caller, target)
        return record is not None and record.state is CircuitBreakerState.OPEN

    def record_failure(
        self,
        caller: str,
        target: str,
        reason: str = "",
        threshold: int = DEFAULT_THRESHOLD,
    ) -> CircuitBreakerRecord:
        """记录一次调用失败，如累计失败次数 >= threshold 则触发 OPEN。

        参数
        ----
        caller
            发起调用的模块标识（如 "RI-05"）。
        target
            被调用的目标模块标识（如 "L2a"）。
        reason
            失败原因文本，写入 reason 字段。
        threshold
            触发 OPEN 的失败次数阈值；默认 DEFAULT_THRESHOLD (3)。

        返回
        ----
        CircuitBreakerRecord
            更新后的记录对象。
        """
        now = datetime.now(_UTC).isoformat()
        record = self.get_state(caller, target)

        if record is None:
            new_count = 1
            new_state = CircuitBreakerState.OPEN if new_count >= threshold else CircuitBreakerState.CLOSED
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                self._conn.execute(
                    """
                    INSERT INTO circuit_breaker_state
                        (caller_module, target_module, state, failure_count,
                         last_failure_at, opened_at, reason, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        caller,
                        target,
                        new_state.value,
                        new_count,
                        now,
                        now if new_state is CircuitBreakerState.OPEN else None,
                        reason,
                        now,
                        now,
                    ),
                )
                self._conn.execute("COMMIT")
            except Exception:
                self._conn.execute("ROLLBACK")
                raise
        else:
            new_count = record.failure_count + 1
            new_state = CircuitBreakerState.OPEN if new_count >= threshold else CircuitBreakerState.CLOSED
            opened_at = record.opened_at
            if new_state is CircuitBreakerState.OPEN and record.state is CircuitBreakerState.CLOSED:
                opened_at = now

            self._conn.execute("BEGIN IMMEDIATE")
            try:
                self._conn.execute(
                    """
                    UPDATE circuit_breaker_state
                    SET state = ?, failure_count = ?, last_failure_at = ?,
                        opened_at = ?, reason = ?, updated_at = ?
                    WHERE caller_module = ? AND target_module = ?
                    """,
                    (
                        new_state.value,
                        new_count,
                        now,
                        opened_at,
                        reason,
                        now,
                        caller,
                        target,
                    ),
                )
                self._conn.execute("COMMIT")
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

        updated = self.get_state(caller, target)
        if updated is None: raise RuntimeError("post-write fetch returned None")  # 5.88.6 修复: assert→if/raise
        return updated

    def reset(
        self,
        caller: str,
        target: str,
    ) -> bool:
        """Owner 手动将 (caller, target) 重置为 CLOSED + failure_count = 0。

        Step 4 中 GLM-5.1 负责实现 `cbg.reset()` CLI 命令包装；
        本方法是底层持久化操作，供 CLI 调用。

        返回
        ----
        bool
            True = 重置成功（记录存在），False = 记录不存在（无需重置）。
        """
        record = self.get_state(caller, target)
        if record is None:
            return False

        now = datetime.now(_UTC).isoformat()
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            self._conn.execute(
                """
                UPDATE circuit_breaker_state
                SET state = 'CLOSED', failure_count = 0,
                    opened_at = NULL, reason = NULL, updated_at = ?
                WHERE caller_module = ? AND target_module = ?
                """,
                (now, caller, target),
            )
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise
        return True

    def list_open_circuits(self) -> list[CircuitBreakerRecord]:
        """列出所有当前处于 OPEN 状态的熔断记录。"""
        rows = self._conn.execute(
            "SELECT * FROM circuit_breaker_state WHERE state = 'OPEN' ORDER BY opened_at DESC"
        ).fetchall()
        return [
            CircuitBreakerRecord(
                caller_module=row["caller_module"],
                target_module=row["target_module"],
                state=CircuitBreakerState(row["state"]),
                failure_count=row["failure_count"],
                last_failure_at=row["last_failure_at"],
                opened_at=row["opened_at"],
                reason=row["reason"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def close(self) -> None:
        """关闭底层 SQLite 连接。"""
        self._conn.close()

    def __enter__(self) -> CBGManager:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# ---------------------------------------------------------------------------
# @circuit_breaker 装饰器
# ---------------------------------------------------------------------------


def circuit_breaker(
    target_module: str,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    caller_module: str | None = None,
    db_path: Path | str | None = None,
) -> Callable[[_F], _F]:
    """装饰跨模块调用，自动统计失败并在达到阈值时触发 CLOSED→OPEN。

    参数
    ----
    target_module
        被调用模块的标识字符串（如 "M2"、"L2a"）。
    threshold
        连续失败次数阈值；默认 DEFAULT_THRESHOLD (3)。
    caller_module
        发起调用的模块名；默认从被装饰函数的 __module__ 推断。
    db_path
        SQLite 数据库路径；默认 DB_PATH。

    CLOSED 状态下的运行时开销
    -------------------------
    装饰器在调用成功时**不写 SQLite**，CLOSED 状态运行时开销接近零。
    仅在捕获到异常时写入失败计数（异步异常路径）。

    CBAC 集成
    ---------
    装饰器在执行前调用 capability_check，确保 caller→target 调用
    已在 capabilities.yaml 中被显式授权。CBAC deny 时抛出 CapabilityDenied，
    不写熔断失败计数（CBAC 拦截不计入熔断统计）。

    用法示例
    --------
        @circuit_breaker(target_module="M2")
        def call_m2_method():
            ...

        @circuit_breaker(target_module="L2a", threshold=5, caller_module="RI-05")
        def spawn_subprocess(cmd):
            ...
    """

    def decorator(func: _F) -> _F:
        _resolved_caller = caller_module or func.__module__ or _CALLER_UNKNOWN

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # CBAC 前置检查（deny 时直接抛出 CapabilityDenied，不写熔断统计）
            capability_check(
                action="call",
                target_path=f"modules/{target_module}",
            )

            manager = CBGManager(db_path)
            try:
                if manager.is_open(_resolved_caller, target_module):
                    raise CircuitOpenError(_resolved_caller, target_module)
                result = func(*args, **kwargs)
                return result
            except CircuitOpenError:
                raise
            except Exception as exc:
                manager.record_failure(
                    _resolved_caller,
                    target_module,
                    reason=f"{type(exc).__name__}: {exc}",
                    threshold=threshold,
                )
                raise
            finally:
                manager.close()

        return wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# L08 注册入口（重试 + 限流策略写入 gate_engine 注册表）
# ---------------------------------------------------------------------------

#: L08 注册表：(caller_module, target_module) → 策略配置
_L08_REGISTRY: dict[tuple[str, str], dict[str, Any]] = {}


def register_compliance(
    caller_module: str,
    target_module: str,
    *,
    max_retries: int = 3,
    retry_delay_s: float = 1.0,
    rate_limit_per_min: int = 60,
    threshold: int = DEFAULT_THRESHOLD,
) -> None:
    """注册 L08 重试 + 限流策略到 CBG 全局注册表。

    由各模块初始化代码调用，与 gate_engine 注册表协作：gate_engine
    在 circuit_breaker CheckType 检查时读取本注册表中的 threshold
    参数，确保 YAML 配置与运行时策略一致。

    参数
    ----
    caller_module
        发起调用的模块标识。
    target_module
        目标模块标识。
    max_retries
        失败后最多重试次数（不含初次调用）；默认 3。
    retry_delay_s
        每次重试间隔秒数；默认 1.0s。
    rate_limit_per_min
        每分钟最大调用次数；默认 60。
    threshold
        熔断触发失败阈值（同步到装饰器 threshold）；默认 DEFAULT_THRESHOLD。
    """
    key = (caller_module, target_module)
    _L08_REGISTRY[key] = {
        "caller_module": caller_module,
        "target_module": target_module,
        "max_retries": max_retries,
        "retry_delay_s": retry_delay_s,
        "rate_limit_per_min": rate_limit_per_min,
        "threshold": threshold,
    }


def get_compliance(caller_module: str, target_module: str) -> dict[str, Any] | None:
    """查询 L08 策略注册表。"""
    return _L08_REGISTRY.get((caller_module, target_module))
