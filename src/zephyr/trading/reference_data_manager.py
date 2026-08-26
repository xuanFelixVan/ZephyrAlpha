# [BLUEPRINT] MOD-TRADING-014 | docs/03_modules/_domain_trading/reference_data_manager/blueprint.md
# [MODULE] zephyr.trading.reference_data_manager
# [DOMAIN] D_TRADING
# [DEPENDENCIES] sqlite3（连接注入，未注入 Fail-Closed）；无其他（clock/audit_sink 全注入）
# [CONSUMERS] 运行时装配批（监控与风控经查询 API 统一引用 / 日终刷新任务链 / 审计路由接线）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sqlite 连接强制注入(未注入 Fail-Closed); 证券主数据 SSOT 全量快照替换; 每次日终刷新版本号严格 +1; Decimal 以 TEXT 保真存取; 查询结果按 code/day 确定性排序; 变更审计回调异常吞没不阻断刷新; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_trading/reference_data_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ReferenceDataError(占位 ZA-TR-UNREGISTERED-REFERENCE-DATA)——连接缺失/空代码名称行业/非法涨跌停/快照内重复代码/空快照/未知代码查询/非法日历输入时抛
# [TESTS] tests/trading/test_reference_data_manager.py
# [A_module] module_id=MOD-TRADING-014 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ReferenceDataManager — 证券主数据管理器（MOD-TRADING-014）。

B14-04639（AUD-DRAFT-001-DIGEST P2 波 P2-W08，CAND-TRD-013，A9 D-TRADING-14）：
主数据 SSOT——代码/名称/行业分类/涨跌停规则/ST 与退市标记/交易日历统一登记
（注入 sqlite 连接，未注入 Fail-Closed）+ 日终刷新（全量快照替换，空快照拒
绝）+ 版本号递增（每次刷新严格 +1）+ 查询 API（监控与风控经 API 统一引用，
禁止各自维护副本语义）+ 变更审计回调（差异 ChangeSet 留痕，回调异常吞没不
阻断刷新）。

查重分工（蓝图 §0）：trading_contracts.market.instrument=Instrument 契约类
型（本件=主数据存储/版本/查询运行时，复用其代码语义不重建契约）；
eod_processor=日终任务链（本件被其调度执行日终刷新，零交集）。
"""

from __future__ import annotations

import datetime
import logging
import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Final, Iterable

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChangeSet",
    "RefDataAuditEvent",
    "ReferenceDataError",
    "ReferenceDataManager",
    "SecurityRecord",
]

_SCHEMA: Final = (
    """
    CREATE TABLE IF NOT EXISTS securities (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        industry TEXT NOT NULL,
        limit_up_pct TEXT NOT NULL,
        limit_down_pct TEXT NOT NULL,
        is_st INTEGER NOT NULL,
        is_delisted INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS calendar_days (
        cal_name TEXT NOT NULL,
        day TEXT NOT NULL,
        PRIMARY KEY (cal_name, day)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
)

_COLUMNS: Final = "code, name, industry, limit_up_pct, limit_down_pct, is_st, is_delisted"


class ReferenceDataError(Exception):
    """证券主数据输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-TR-UNREGISTERED-REFERENCE-DATA。
    """


@dataclass(frozen=True)
class SecurityRecord:
    """证券主数据记录（SSOT 条目，frozen；涨跌停幅度 Decimal-only）。"""

    code: str
    name: str
    industry: str
    limit_up_pct: Decimal
    limit_down_pct: Decimal
    is_st: bool
    is_delisted: bool


@dataclass(frozen=True)
class ChangeSet:
    """日终刷新差异（各集合按代码确定性排序，frozen）。"""

    from_version: int
    to_version: int
    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]
    refreshed_at: datetime.datetime


@dataclass(frozen=True)
class RefDataAuditEvent:
    """变更审计事件（审计回调载荷，frozen）。"""

    change: ChangeSet
    occurred_at: datetime.datetime


class ReferenceDataManager:
    """证券主数据管理器（SSOT：sqlite 注入 + 日终刷新 + 版本递增 + 查询 API + 审计回调）。"""

    def __init__(
        self,
        *,
        conn: sqlite3.Connection,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[RefDataAuditEvent], None] | None = None,
    ) -> None:
        if conn is None:
            raise ReferenceDataError("sqlite 连接未注入（主数据 SSOT 硬依赖，Fail-Closed）")
        self._conn = conn
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        with self._conn:
            for stmt in _SCHEMA:
                self._conn.execute(stmt)
            if self._conn.execute(
                "SELECT value FROM meta WHERE key = 'version'"
            ).fetchone() is None:
                self._conn.execute("INSERT INTO meta (key, value) VALUES ('version', '0')")

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _row_to_record(row: tuple) -> SecurityRecord:
        return SecurityRecord(
            code=row[0],
            name=row[1],
            industry=row[2],
            limit_up_pct=Decimal(row[3]),
            limit_down_pct=Decimal(row[4]),
            is_st=bool(row[5]),
            is_delisted=bool(row[6]),
        )

    @staticmethod
    def _validate_record(rec: SecurityRecord) -> None:
        if not isinstance(rec, SecurityRecord):
            raise ReferenceDataError(f"非法记录类型: {type(rec)!r}")
        if not rec.code or not rec.name:
            raise ReferenceDataError("证券代码/名称为空")
        if not rec.industry:
            raise ReferenceDataError(f"行业分类为空: {rec.code!r}")
        for label, pct in (("limit_up_pct", rec.limit_up_pct), ("limit_down_pct", rec.limit_down_pct)):
            if not isinstance(pct, Decimal) or pct < 0:
                raise ReferenceDataError(f"涨跌停规则非法: {rec.code!r} {label}={pct!r}")

    @staticmethod
    def _validate_days(trading_days: Iterable[datetime.date]) -> tuple[datetime.date, ...]:
        days: set[datetime.date] = set()
        for d in trading_days:
            if not isinstance(d, datetime.date) or isinstance(d, datetime.datetime):
                raise ReferenceDataError(f"交易日历元素非法: {d!r}（须为 datetime.date）")
            days.add(d)
        return tuple(sorted(days))

    def _all_records(self) -> tuple[SecurityRecord, ...]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM securities ORDER BY code"
        ).fetchall()
        return tuple(self._row_to_record(r) for r in rows)

    def _audit(self, change: ChangeSet) -> None:
        if self._audit_sink is not None:
            try:
                self._audit_sink(RefDataAuditEvent(change=change, occurred_at=self._clock()))
            except Exception:  # noqa: BLE001 — 审计回调不阻断刷新（蓝图 §0）
                _log.exception("audit_sink 回调失败")

    # ── 日终刷新（SSOT 全量快照替换 + 版本递增） ───────────────────────────

    def eod_refresh(
        self,
        *,
        records: Iterable[SecurityRecord],
        trading_days: Iterable[datetime.date] | None = None,
        calendar_name: str = "SSE_A",
    ) -> ChangeSet:
        """日终刷新：全量快照替换 + 版本号严格 +1 + 差异审计回调。"""
        if not calendar_name:
            raise ReferenceDataError("calendar_name 为空")
        records = tuple(records)
        if not records:
            raise ReferenceDataError("刷新快照为空（疑似数据源故障，Fail-Closed）")
        seen: set[str] = set()
        for rec in records:
            self._validate_record(rec)
            if rec.code in seen:
                raise ReferenceDataError(f"快照内代码重复: {rec.code!r}")
            seen.add(rec.code)
        days: tuple[datetime.date, ...] | None = None
        if trading_days is not None:
            days = self._validate_days(trading_days)

        old = {r.code: r for r in self._all_records()}
        new = {r.code: r for r in records}
        added = tuple(sorted(c for c in new if c not in old))
        removed = tuple(sorted(c for c in old if c not in new))
        changed = tuple(sorted(c for c in new if c in old and new[c] != old[c]))

        from_version = self.version()
        to_version = from_version + 1
        with self._conn:
            self._conn.execute("DELETE FROM securities")
            self._conn.executemany(
                f"INSERT INTO securities ({_COLUMNS}) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        r.code, r.name, r.industry,
                        str(r.limit_up_pct), str(r.limit_down_pct),
                        int(r.is_st), int(r.is_delisted),
                    )
                    for r in sorted(new.values(), key=lambda x: x.code)
                ],
            )
            if days is not None:
                self._conn.execute(
                    "DELETE FROM calendar_days WHERE cal_name = ?", (calendar_name,)
                )
                self._conn.executemany(
                    "INSERT INTO calendar_days (cal_name, day) VALUES (?, ?)",
                    [(calendar_name, d.isoformat()) for d in days],
                )
            self._conn.execute(
                "UPDATE meta SET value = ? WHERE key = 'version'", (str(to_version),)
            )

        change = ChangeSet(
            from_version=from_version,
            to_version=to_version,
            added=added,
            removed=removed,
            changed=changed,
            refreshed_at=self._clock(),
        )
        _log.info(
            "主数据日终刷新: v%d -> v%d (added=%d removed=%d changed=%d)",
            from_version, to_version, len(added), len(removed), len(changed),
        )
        self._audit(change)
        return change

    # ── 查询 API（监控与风控统一引用入口） ─────────────────────────────────

    def version(self) -> int:
        """当前主数据版本号。"""
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key = 'version'"
        ).fetchone()
        return int(row[0])

    def get(self, code: str) -> SecurityRecord:
        """按代码查询（未知 → Fail-Closed）。"""
        if not code:
            raise ReferenceDataError("查询代码为空")
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM securities WHERE code = ?", (code,)
        ).fetchone()
        if row is None:
            raise ReferenceDataError(f"未知证券代码: {code!r}")
        return self._row_to_record(row)

    def exists(self, code: str) -> bool:
        """代码是否已登记（空代码 → Fail-Closed）。"""
        if not code:
            raise ReferenceDataError("查询代码为空")
        row = self._conn.execute(
            "SELECT 1 FROM securities WHERE code = ?", (code,)
        ).fetchone()
        return row is not None

    def all_codes(self) -> tuple[str, ...]:
        """全部已登记代码（按代码确定性排序）。"""
        rows = self._conn.execute("SELECT code FROM securities ORDER BY code").fetchall()
        return tuple(r[0] for r in rows)

    def list_by_industry(self, industry: str) -> tuple[SecurityRecord, ...]:
        """按行业分类查询（按代码确定性排序；空行业 → Fail-Closed）。"""
        if not industry:
            raise ReferenceDataError("行业分类查询为空")
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM securities WHERE industry = ? ORDER BY code",
            (industry,),
        ).fetchall()
        return tuple(self._row_to_record(r) for r in rows)

    def is_trading_day(self, day: datetime.date, calendar_name: str = "SSE_A") -> bool:
        """交易日判定（非法日期类型 → Fail-Closed）。"""
        if not isinstance(day, datetime.date) or isinstance(day, datetime.datetime):
            raise ReferenceDataError(f"非法日期: {day!r}（须为 datetime.date）")
        row = self._conn.execute(
            "SELECT 1 FROM calendar_days WHERE cal_name = ? AND day = ?",
            (calendar_name, day.isoformat()),
        ).fetchone()
        return row is not None

    def trading_days(self, calendar_name: str = "SSE_A") -> tuple[datetime.date, ...]:
        """交易日历查询（按日期确定性排序）。"""
        rows = self._conn.execute(
            "SELECT day FROM calendar_days WHERE cal_name = ? ORDER BY day",
            (calendar_name,),
        ).fetchall()
        return tuple(datetime.date.fromisoformat(r[0]) for r in rows)
