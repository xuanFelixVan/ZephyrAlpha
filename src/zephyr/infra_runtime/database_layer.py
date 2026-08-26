# [BLUEPRINT] MOD-INF-077 | docs/03_modules/_domain_infrastructure_runtime/database_layer/blueprint.md
# [MODULE] zephyr.infra_runtime.database_layer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（Backend 协议鸭子校验；时钟/sleeper 全注入）
# [CONSUMERS] 运行时装配批（sqlite/duckdb/pg/clickhouse 后端注册与统一查询路由门面）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 后端名唯一且须满足 DbBackend 协议(query/execute/health/close); route 仅按注册名确定性路由; 已关闭后端拒绝路由; 连接借还成对(计数守恒); 重试 attempts≥1 且间隔经注入 sleeper(默认空操作不真睡); 超时判定=注入时钟差>timeout; 重试耗尽 Fail-Closed 抛错; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/database_layer/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DatabaseLayerError(占位 ZA-INF-UNREGISTERED-DATABASE-LAYER)——空名/重复注册/协议不符/未知或已关闭后端/借还未注册后端/非法重试参数/重试耗尽时抛
# [TESTS] tests/infra_runtime/test_database_layer.py
# [A_module] module_id=MOD-INF-077 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""DatabaseLayer — 数据库统一抽象层（MOD-INF-077）。

B13-04299（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-010，A3数据架构）：
DuckDB/SQLite/PG/ClickHouse 语义统一的后端注册（``DbBackend`` 协议：
query/execute/health/close）+ 统一查询门面 ``route(key)`` 路由 + 连接借还
上下文管理器 + 超时重试（注入时钟判定超时、注入 sleeper 退避，不真睡）。
收编直调点的适配入口（register_backend / facade 查询路由）。

纯内存确定性：本件不建真实连接池、不触网；后端实例由装配方注入。
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Callable, Final, Iterator, Protocol, runtime_checkable

_log = logging.getLogger(__name__)

__all__: Final = [
    "DatabaseLayer",
    "DatabaseLayerError",
    "DbBackend",
]


class DatabaseLayerError(Exception):
    """数据库抽象层输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-DATABASE-LAYER。
    """


@runtime_checkable
class DbBackend(Protocol):
    """数据库后端协议（query/execute/health/close 语义统一）。"""

    def query(self, sql: str, params: tuple = ()) -> list[tuple]:
        """只读查询，返回行列表。"""
        ...

    def execute(self, sql: str, params: tuple = ()) -> int:
        """写执行，返回受影响行数。"""
        ...

    def health(self) -> bool:
        """健康探针。"""
        ...

    def close(self) -> None:
        """关闭后端释放资源。"""
        ...


def _noop_sleeper(seconds: float) -> None:
    """默认 sleeper：空操作（不真睡，保证确定性）。"""


class DatabaseLayer:
    """数据库统一门面（后端注册表 + 路由 + 借还 + 超时重试）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], float] | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        self._clock = clock or time.monotonic
        self._sleeper = sleeper or _noop_sleeper
        self._backends: dict[str, DbBackend] = {}
        self._closed: set[str] = set()
        self._borrowed: dict[str, int] = {}

    # ── 注册与路由 ────────────────────────────────────────────────────────

    def register_backend(self, name: str, backend: DbBackend) -> None:
        """注册后端（名称唯一；协议鸭子校验，缺方法 Fail-Closed）。"""
        if not name:
            raise DatabaseLayerError("后端名为空")
        if name in self._backends:
            raise DatabaseLayerError(f"后端重复注册: {name!r}")
        if not isinstance(backend, DbBackend):
            raise DatabaseLayerError(
                f"后端协议不符: {name!r} 须实现 query/execute/health/close"
            )
        self._backends[name] = backend
        self._borrowed[name] = 0

    def route(self, key: str) -> DbBackend:
        """统一门面路由（未知/已关闭 → Fail-Closed）。"""
        backend = self._backends.get(key)
        if backend is None:
            raise DatabaseLayerError(f"未知后端: {key!r}")
        if key in self._closed:
            raise DatabaseLayerError(f"后端已关闭: {key!r}")
        return backend

    # ── 连接借还 ──────────────────────────────────────────────────────────

    @contextmanager
    def connection(self, name: str) -> Iterator[DbBackend]:
        """连接借还上下文管理器（计数守恒，异常亦归还）。"""
        backend = self.route(name)
        self._borrowed[name] += 1
        try:
            yield backend
        finally:
            self._borrowed[name] -= 1

    def borrowed(self, name: str) -> int:
        """当前借出计数（未注册 → Fail-Closed）。"""
        if name not in self._backends:
            raise DatabaseLayerError(f"未知后端: {name!r}")
        return self._borrowed[name]

    # ── 超时重试 ──────────────────────────────────────────────────────────

    def _with_retry(
        self,
        name: str,
        op: str,
        sql: str,
        params: tuple,
        attempts: int,
        backoff: float,
        timeout: float | None,
    ):
        backend = self.route(name)
        if not isinstance(attempts, int) or attempts < 1:
            raise DatabaseLayerError(f"attempts 非法: {attempts!r}（须 ≥ 1）")
        if not isinstance(backoff, (int, float)) or backoff < 0:
            raise DatabaseLayerError(f"backoff 非法: {backoff!r}（须 ≥ 0）")
        if timeout is not None and (not isinstance(timeout, (int, float)) or timeout <= 0):
            raise DatabaseLayerError(f"timeout 非法: {timeout!r}（须 > 0）")
        fn = backend.query if op == "query" else backend.execute
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            started = self._clock()
            try:
                result = fn(sql, params)
            except Exception as exc:  # noqa: BLE001 — 后端异常统一重试语义
                last_exc = exc
                _log.warning("后端 %s %s 第 %d 次失败: %s", name, op, attempt, exc)
            else:
                elapsed = self._clock() - started
                if timeout is not None and elapsed > timeout:
                    last_exc = TimeoutError(
                        f"{op} 超时: elapsed={elapsed:.6f}s > timeout={timeout}s"
                    )
                    _log.warning("后端 %s %s 第 %d 次超时", name, op, attempt)
                else:
                    return result
            if attempt < attempts:
                self._sleeper(float(backoff) * attempt)
        raise DatabaseLayerError(
            f"后端 {name!r} {op} 重试 {attempts} 次耗尽: {last_exc}"
        ) from last_exc

    def query_with_retry(
        self,
        name: str,
        sql: str,
        params: tuple = (),
        *,
        attempts: int = 3,
        backoff: float = 0.0,
        timeout: float | None = None,
    ) -> list[tuple]:
        """只读查询（超时/异常重试，耗尽 Fail-Closed）。"""
        return self._with_retry(name, "query", sql, params, attempts, backoff, timeout)

    def execute_with_retry(
        self,
        name: str,
        sql: str,
        params: tuple = (),
        *,
        attempts: int = 3,
        backoff: float = 0.0,
        timeout: float | None = None,
    ) -> int:
        """写执行（超时/异常重试，耗尽 Fail-Closed）。"""
        return self._with_retry(name, "execute", sql, params, attempts, backoff, timeout)

    # ── 健康与关闭 ────────────────────────────────────────────────────────

    def health(self) -> dict[str, bool]:
        """全后端健康视图（按名排序确定性；探针异常记 False）。"""
        out: dict[str, bool] = {}
        for name in sorted(self._backends):
            if name in self._closed:
                out[name] = False
                continue
            try:
                out[name] = bool(self._backends[name].health())
            except Exception:  # noqa: BLE001 — 健康探针异常记 False 不抛
                _log.exception("后端健康探针异常: %s", name)
                out[name] = False
        return out

    def close(self, name: str) -> None:
        """关闭单后端（幂等；关闭后拒绝路由）。"""
        backend = self._backends.get(name)
        if backend is None:
            raise DatabaseLayerError(f"未知后端: {name!r}")
        if name in self._closed:
            return
        try:
            backend.close()
        except Exception:  # noqa: BLE001 — 关闭异常不阻断登记
            _log.exception("后端关闭异常: %s", name)
        self._closed.add(name)

    def close_all(self) -> None:
        """关闭全部后端（按名排序确定性）。"""
        for name in sorted(self._backends):
            self.close(name)
