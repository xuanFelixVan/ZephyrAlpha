# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.utils.time_utils
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sqlite3 datetime/date adapter 已注册为 str()（register_sqlite_datetime_str_adapter，#SQLITE-DATETIME-ADAPTER），now_utc() 传给 sqlite3 自动适配为空格分隔 str 格式（与默认 adapter isoformat(" ") 一致，Python 3.12 deprecation 治本）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
time_utils.py —— 时间/日期工具（Phase 9 新增 | 盲点 B19 修复）

痛点修复：测试中 freeze_time 是标配，没有的话每个测试文件都要手写 mock——
  1. 没有统一的 now_utc() -> 每个模块 datetime.now(UTC) 写法不统一
  2. 没有 freeze_time() -> 测试中 time-dependent 逻辑难以测试
  3. 没有 parse_iso() -> 各种时间字符串解析方式散落各处

设计对标：
  - freezegun 库（freeze_time 测试装饰器）
  - Pendulum 库（人性化的 datetime API）
  - Python datetime + time_machine 模式

设计原则：
  - 所有时间操作统一用 UTC——禁止本地时区
  - freeze_time 用于测试——通过全局 clock 替换实现
  - 零依赖第三方库——仅 Python 标准库

AI 施工约定：
  - 任何 datetime 创建 MUST 使用 now_utc()——禁止 datetime.now()
  - 测试中 MUST 使用 freeze_time() context manager——禁止 mock datetime
  - 时间解析 MUST 使用 parse_iso()——统一格式验证

SSoT: MOD-INF-016 §2.18 shared-time-utils
Version: 0.1.0
"""

import sqlite3
import threading
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, date, datetime
from typing import Final

__all__ = [
    "MOCKED_TIME",
    "format_iso",
    "freeze_time",
    "now_iso",
    "now_utc",
    "now_utc_str",
    "parse_iso",
    "register_sqlite_datetime_str_adapter",
    "seconds_since",
    "seconds_until",
]

MOCKED_TIME: Final[datetime | None] = None
_mocked_time_lock = threading.Lock()


def register_sqlite_datetime_str_adapter() -> None:
    """注册 datetime/date→sqlite3 str 适配器（Python 3.12 default adapter deprecated 治本）。

    Python 3.12 废弃 sqlite3 默认 datetime/date adapter（未来版本将移除，届时
    ``conn.execute(sql, (now_utc(),))`` 会 TypeError）。本函数注册 ``str`` 作为
    适配器——产出空格分隔格式（如 '2026-07-23 17:42:13.539162+00:00'），与默认
    adapter 的 ``isoformat(" ")`` 行为**完全一致**，零行为变更。

    覆盖全代码库 21 处 datetime→sqlite3 调用点 + 未来新增，无需逐调用点 str() 包装。

    幂等：重复调用安全（register_adapter 覆盖式注册）。
    非 I/O 副作用：纯函数注册，不触发连接/文件/网络操作
    （NO-IMPORT-SIDE-EFFECT gate 仅检测 sqlite3.connect，不检测 register_adapter）。
    """
    sqlite3.register_adapter(datetime, str)
    sqlite3.register_adapter(date, str)


# 治本 #SQLITE-DATETIME-ADAPTER (2026-07-24): Python 3.12 废弃默认 datetime adapter，
# 显式注册 str() 适配器（空格分隔，与 now_utc()→str() 约定一致）。零行为变更
# （str(dt) == isoformat(" ") == 默认 adapter 输出）。time_utils 是时间 SSoT，被
# governance/audit 等 sqlite3 使用方广泛导入，注册于此确保进程级早期生效。
register_sqlite_datetime_str_adapter()


def now_utc() -> datetime:
    """返回当前 UTC 时间——如果 freeze_time 激活则返回冻结时间。

    Usage::

        ts = now_utc()
        assert ts.tzinfo == UTC
    """
    if MOCKED_TIME is not None:
        return MOCKED_TIME
    return datetime.now(UTC)


def now_utc_str() -> str:
    """返回当前 UTC 时间的 str 格式（空格分隔，与 sqlite3 存储格式一致）。

    用于 SQL cutoff 查询等需要显式 str 时间戳的场景。``now_utc()`` 传给 sqlite3 时
    由 ``register_sqlite_datetime_str_adapter`` 自动适配为 str，本函数供需要直接
    str 的场景（如 ``WHERE logged_at < ?`` 参数）使用。

    Usage::

        cutoff = now_utc_str()  # '2026-07-23 17:42:13.539162+00:00'
    """
    return str(now_utc())


default_now = now_utc  # 向后兼容别名——evolution_engine/hallucination_detector 等消费者


def parse_iso(iso_string: str) -> datetime:
    """解析 ISO 8601 时间字符串为 UTC datetime。

    Args:
        iso_string: ISO 8601 格式字符串（如 "2026-05-05T12:00:00Z"）。

    Returns:
        UTC datetime 对象。

    Raises:
        ValueError: 如果字符串格式无效。
    """
    dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def format_iso(dt: datetime) -> str:
    """将 datetime 格式化为 ISO 8601 UTC 字符串。

    Args:
        dt: datetime 对象（可带或不带 tzinfo）。

    Returns:
        ISO 8601 格式字符串（如 "2026-05-05T12:00:00.000000Z"）。
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    utc_dt = dt.astimezone(UTC)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def now_iso() -> str:
    """返回当前 UTC 时间的 ISO 8601 格式化字符串。

    向后兼容旧版 time_utils.py——被 db.task_repo 等消费者使用。

    Usage::

        ts = now_iso()
        # "2026-05-05T12:00:00.000000Z"
    """
    return format_iso(now_utc())


@contextmanager
def freeze_time(frozen_at: datetime | str) -> Generator[None, None, None]:
    """冻结时间——用于测试。Context manager 进入时冻结，退出时恢复。

    对标 Python freezegun 库的核心功能。

    Usage::

        with freeze_time("2026-05-05T12:00:00Z"):
            assert now_utc().isoformat().startswith("2026-05-05T12:00:00")
        assert now_utc() > datetime(2026, 1, 1, tzinfo=UTC)  # 已恢复
    """
    global MOCKED_TIME

    if isinstance(frozen_at, str):
        frozen_dt = parse_iso(frozen_at)
    else:
        frozen_dt = frozen_at
        if frozen_dt.tzinfo is None:
            frozen_dt = frozen_dt.replace(tzinfo=UTC)

    with _mocked_time_lock:
        previous = MOCKED_TIME
        MOCKED_TIME = frozen_dt
    try:
        yield
    finally:
        with _mocked_time_lock:
            MOCKED_TIME = previous


def seconds_since(dt: datetime) -> float:
    """计算从 dt 到 now_utc() 经过的秒数。"""
    return (now_utc() - dt.astimezone(UTC)).total_seconds()


def seconds_until(dt: datetime) -> float:
    """计算从 now_utc() 到 dt 剩余秒数——负值表示已过期。"""
    return (dt.astimezone(UTC) - now_utc()).total_seconds()
