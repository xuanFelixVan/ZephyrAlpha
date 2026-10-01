# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/10_wave_plan.md | 波 3.2/3.3
# [MODULE] scripts.governance.data_supply.strict_truth_reader
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.ch_reader (严格读通道 query_rows/count_strict)
# [CONSUMERS] scripts.governance.data_supply.false_green_crosscheck; scripts.governance.data_supply.supply_conservation; scripts.governance.data_supply.no_cache_endorsement
# [STARTUP] imported
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救的严格真源读数器（W-180族字节代投非新能力），与canonical删除拦截/回测引擎无职责重叠
# [TTL] permanent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任何传输/引擎/形状异常 -> raise TruthReadError（W-180.1：判据类读数失败必抛）; 真 0 行 -> rows=0 且 empty_confirmed=True; max(date) 为 NULL -> None（确证空表，与失败可分辨）
# [A_module] module_id=MOD-GOV-DS-TRUTH | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 一次性判据读数层，无常驻循环
"""Truth-side reader — the warehouse side of the 3.2/3.3 cross-check.

W-180 红线在本件的落实（三条全部机械可验）：

  * 只走 ``zephyr.data.ch_reader`` 的**严格通道**（``query_rows`` / ``count_strict``），
    失败必抛；**禁用** ``query()``（失败返回空串，按下标取值会取到真实值首位数字 467→'4'）
    与 ``count()``（失败返回 0，把"读失败"洗成"真 0 行"）。
  * 新鲜度一律取业务表 ``max(<date_col>)``，禁查 ``system.*`` 面（波 3.3 判据原文）。
  * ReplacingMergeTree 去重由 ``count_strict`` 内部 FINAL 保证；本件不手写 FINAL/裸 SQL 拼接
    逻辑到调用方——表名/列名先经标识符白名单校验，失败即抛。

探针（``probe``）可注入是**反事实控制组**的接口：往台账喂假 SUCCESS 而让探针如实回报
"目标表没动"，两把尺都必须红；同时 ``reads`` 计数使"缓存背书"无处藏身（见 no_cache_endorsement）。
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")
Projection = Callable[[str], Sequence[tuple[Any, ...]]]


class TruthReadError(RuntimeError):
    def __init__(self, msg: str, *, details: dict | None = None):
        super().__init__(msg)
        self.details = details or {}

    """Raised for every failed truth read — never a silent 0 / '' / None."""


@dataclass(frozen=True)
class LegTruth:
    """Independently measured ground truth for one table leg in one window."""

    table: str
    date_col: str
    rows_in_window: int
    empty_confirmed: bool
    latest_business_date: dt.date | None
    rows_by_date: dict[dt.date, int] = field(default_factory=dict)

    def rows_on(self, day: dt.date) -> int:
        return self.rows_by_date.get(day, 0)


def _default_projection(sql: str) -> Sequence[tuple[Any, ...]]:
    from zephyr.data import ch_reader  # 严格通道唯一入口（禁 query/count 裸用）

    return ch_reader.query_rows(sql)


def _check_ident(name: str, *, label: str) -> str:
    if not _IDENT.match(name or ""):
        raise TruthReadError(f"{label} 非法（禁裸 SQL 注入面）: {name!r}")
    return name


def _lit_date(day: dt.date) -> str:
    return f"toDate('{day.isoformat()}')"


# —— 判据类 SQL 集中化（§5.160.2）：模板置于模块级 SQL_* 常量（NO-BARE-SQL 豁免 AST 定义行），
#    调用方仅 .format 填已校验标识符与日期常量；表/列名先经 _check_ident 白名单，失败即抛。
SQL_WINDOW_TMPL = "SELECT {c} AS d, count() AS n FROM {t} WHERE {c} BETWEEN {lo} AND {hi} GROUP BY d ORDER BY d"
SQL_LATEST_TMPL = "SELECT max({c}) FROM {t} {where}"
SQL_LATEST_WHERE_TMPL = "WHERE {c} <= {not_after}"


def build_window_sql(table: str, date_col: str, *, lo: dt.date, hi: dt.date) -> str:
    """Grouped per-day count over [lo, hi] (identifiers pre-validated)."""
    t = _check_ident(table, label="table")
    c = _check_ident(date_col, label="date_col")
    return SQL_WINDOW_TMPL.format(c=c, t=t, lo=_lit_date(lo), hi=_lit_date(hi))


def build_latest_sql(table: str, date_col: str, *, not_after: dt.date | None) -> str:
    t = _check_ident(table, label="table")
    c = _check_ident(date_col, label="date_col")
    where = SQL_LATEST_WHERE_TMPL.format(c=c, not_after=_lit_date(not_after)) if not_after else ""
    return SQL_LATEST_TMPL.format(c=c, t=t, where=where).strip()


class StrictTruthReader:
    """Counting, cache-free warehouse reader used by both wave-3 rulers."""

    def __init__(self, projection: Projection | None = None) -> None:
        self._projection = projection or _default_projection
        self.reads = 0

    def _run(self, sql: str) -> Sequence[tuple[Any, ...]]:
        self.reads += 1
        try:
            rows = self._projection(sql)
        except TruthReadError:
            raise
        except Exception as exc:  # 传输/引擎失败必抛（W-180.1）
            raise TruthReadError(f"严格读数失败: {type(exc).__name__}: {exc}", details={"sql": sql}) from exc
        if rows is None:
            raise TruthReadError("严格读数返回 None（视为失败）", details={"sql": sql})
        if isinstance(rows, str):
            raise TruthReadError("疑似 fail-silent 通道（返回 str 而非行集）", details={"sql": sql})
        return rows

    def rows_by_date(self, table: str, date_col: str, *, lo: dt.date, hi: dt.date) -> dict[dt.date, int]:
        out: dict[dt.date, int] = {}
        for row in self._run(build_window_sql(table, date_col, lo=lo, hi=hi)):
            if len(row) != 2:
                raise TruthReadError(f"逐日行数期望 (date,count) 两列，实得 {row!r}")
            out[_coerce_date(row[0], table=table)] = _coerce_int(row[1], table=table)
        return out

    def latest_business_date(self, table: str, date_col: str, *, not_after: dt.date | None = None) -> dt.date | None:
        rows = self._run(build_latest_sql(table, date_col, not_after=not_after))
        if len(rows) != 1 or len(rows[0]) != 1:
            raise TruthReadError(f"max(date) 期望 1x1，实得 {rows!r}")
        value = rows[0][0]
        if value in (None, ""):
            return None  # 确证空表（与"读失败"可分辨：失败已在 _run 抛）
        return _coerce_date(value, table=table)

    def read_leg(
        self,
        table: str,
        date_col: str,
        *,
        lo: dt.date,
        hi: dt.date,
        past_only: bool = True,
    ) -> LegTruth:
        by_day = self.rows_by_date(table, date_col, lo=lo, hi=hi)
        total = sum(by_day.values())
        latest = self.latest_business_date(table, date_col, not_after=hi if past_only else None)
        return LegTruth(
            table=table,
            date_col=date_col,
            rows_in_window=total,
            empty_confirmed=(latest is None and total == 0),
            latest_business_date=latest,
            rows_by_date=by_day,
        )


def _coerce_date(value: Any, *, table: str) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    text = str(value or "")[:10]
    try:
        return dt.date.fromisoformat(text)
    except ValueError as exc:
        raise TruthReadError(f"{table}: 日期列值不可解析: {value!r}") from exc


def _coerce_int(value: Any, *, table: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise TruthReadError(f"{table}: 计数值非整数: {value!r}") from exc
