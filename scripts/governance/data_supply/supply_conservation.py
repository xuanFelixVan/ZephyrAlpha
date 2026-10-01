# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/10_wave_plan.md | 波 3.3（W-32 / EV-03 家族）
# [MODULE] scripts.governance.data_supply.supply_conservation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.data_supply.supply_sources, scripts.governance.data_supply.strict_truth_reader
# [CONSUMERS] scripts.governance.data_supply.check_supply_conservation; scripts.governance.data_supply.check_wave3_rulers;
#             [待登记] zephyr.data.supply_sentinel（L13 data_supply_sentinel 槽位的守恒腿，见 registration_needs.yaml）
# [STARTUP] imported
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救的供数守恒尺（字节代投非新能力），与canonical账目核对器职责不同域
# [TTL] permanent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读数失败 -> 冒泡 TruthReadError; 声明侧真源缺失 -> 冒泡 MissingSourceError（禁"读不到=无缺口"放行）
# [A_module] module_id=MOD-GOV-DS-CONS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 一次性判据计算，无常驻循环
"""3.3 供数守恒断言（W-32，把提交链 EV-03 的病与药搬到数据链）。

EV-03 的病＝"工人干完活、货单上也有记录，但仓库里那件东西不见了"；药＝**回执与真值互证**。
数据链同一病同一药，且**内收不造第二套**：

  * 声明侧＝既有宿主派生：``tasks.yaml``（谁该供哪张表）+ ``task_runs`` 回执（自称供了多少）
    + ``known_data_gaps.yaml``（已申报的缺口）；
  * 实到侧＝业务表真值：``count`` 逐日 + ``max(<date_col>)`` 新鲜度（**禁 system. 面**，波 3.3 判据原文）；
  * 守恒式＝声明供货日集合 △ 实到供货日集合 必须全被已申报缺口覆盖；
    交集上的行数差值不得为负（负＝蒸发）。

与 3.2 的分工（同真源、不同断言面，故不构成第二套）：
3.2 逐**回执行**交叉核对并点名降级下游；3.3 在**表×窗口**上做集合/量值守恒与缺口台账对账。
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Sequence

from scripts.governance.data_supply.false_green_crosscheck import RED, WARN, CrosscheckFinding
from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader
from scripts.governance.data_supply.supply_sources import (
    DataSupplyTaskSpec,
    LedgerRun,
    SentinelLeg,
    gap_covers,
    utc_date_of,
)


@dataclass(frozen=True)
class DeclaredSupply:
    """What the ledger claims was supplied for one table on one business day."""

    table: str
    day: dt.date
    task_ids: tuple[str, ...]
    rows_claimed: int


@dataclass
class ConservationReport:
    table: str
    findings: list[CrosscheckFinding]
    declared_days: tuple[dt.date, ...] = ()
    arrived_days: tuple[dt.date, ...] = ()
    rows_declared: int = 0
    rows_arrived: int = 0


@dataclass(frozen=True)
class Window:
    """Inclusive business-day window (bundled to keep helper arity ≤7)."""

    lo: dt.date
    hi: dt.date


def collect_declared(
    runs: list[LedgerRun], specs: dict[str, DataSupplyTaskSpec], *, lo: dt.date, hi: dt.date
) -> dict[str, dict[dt.date, DeclaredSupply]]:
    """Fold SUCCESS receipts into table -> day -> declared supply (window-filtered)."""
    acc: dict[str, dict[dt.date, tuple[int, list[str]]]] = {}
    for run in runs:
        if run.status not in {"SUCCESS"}:
            continue
        spec = specs.get(run.task_id)
        if not spec or not spec.table:
            continue
        day = utc_date_of(run.finished_at or run.started_at)
        if day is None or not (lo <= day <= hi):
            continue
        bucket = acc.setdefault(spec.table, {})
        rows, tasks = bucket.get(day, (0, []))
        bucket[day] = (rows + int(run.rows_written or 0), tasks + [run.task_id])
    return {
        table: {day: DeclaredSupply(table, day, tuple(sorted(set(tasks))), rows) for day, (rows, tasks) in days.items()}
        for table, days in acc.items()
    }


def check_table(
    table: str,
    date_col: str,
    *,
    declared: dict[dt.date, DeclaredSupply],
    reader: StrictTruthReader,
    window: Window,
    gaps: list[dict[str, object]],
    leg: SentinelLeg | None,
) -> ConservationReport:
    """Declared-vs-arrived conservation for one table over ``window``."""
    truth = reader.read_leg(table, date_col, lo=window.lo, hi=window.hi, past_only=bool(leg and leg.past_only))
    arrived_days = {d for d, n in truth.rows_by_date.items() if n > 0}
    findings: list[CrosscheckFinding] = []
    findings += _set_leg(table, declared, arrived_days, truth, gaps)
    findings += _magnitude_leg(table, declared, truth)
    return ConservationReport(
        table=table,
        findings=findings,
        declared_days=tuple(sorted(declared)),
        arrived_days=tuple(sorted(arrived_days)),
        rows_declared=sum(x.rows_claimed for x in declared.values()),
        rows_arrived=truth.rows_in_window,
    )


def _set_leg(
    table: str,
    declared: dict[dt.date, DeclaredSupply],
    arrived_days: set[dt.date],
    truth,
    gaps: list[dict[str, object]],
) -> list[CrosscheckFinding]:
    """_set_leg implementation."""
    out: list[CrosscheckFinding] = []
    for day in sorted(set(declared) - arrived_days):
        if gap_covers(gaps, table, day):
            out.append(
                CrosscheckFinding("GAP_DECLARED_MISSING_DAY", WARN, "", table, f"{day} 缺数但已在 known_data_gaps 申报")
            )
            continue
        out.append(
            CrosscheckFinding(
                "UNDECLARED_EVAPORATION",
                RED,
                "",
                table,
                f"回执声明 {day} 供货 {declared[day].rows_claimed} 行，表侧 0 行且无缺口申报（EV-03 同病）",
            )
        )
    for day in sorted(arrived_days - set(declared)):
        out.append(
            CrosscheckFinding(
                "UNDECLARED_ARRIVAL",
                WARN,
                "",
                table,
                f"表侧 {day} 有 {truth.rows_on(day)} 行，台账无 SUCCESS 回执（旁路写入/回执漏记）",
            )
        )
    return out


def _magnitude_leg(table: str, declared: dict[dt.date, DeclaredSupply], truth) -> list[CrosscheckFinding]:
    """_magnitude_leg implementation."""
    out: list[CrosscheckFinding] = []
    for day in sorted(set(declared) & {d for d, n in truth.rows_by_date.items() if n > 0}):
        claimed, arrived = declared[day].rows_claimed, truth.rows_on(day)
        if claimed <= 0:
            continue
        if arrived < claimed:
            out.append(
                CrosscheckFinding(
                    "PARTIAL_DELIVERY", RED, "", table, f"{day} 声明 {claimed} 行，实到 {arrived} 行（守恒式不闭合）"
                )
            )
        elif arrived > claimed:
            out.append(
                CrosscheckFinding(
                    "OVER_DELIVERY", WARN, "", table, f"{day} 实到 {arrived} 行 > 声明 {claimed} 行（去重前/多源同写）"
                )
            )
    return out


def evaluate(
    *,
    specs: dict[str, DataSupplyTaskSpec],
    legs_by_table: dict[str, list[SentinelLeg]],
    runs: list[LedgerRun],
    reader: StrictTruthReader,
    lo: dt.date,
    hi: dt.date,
    gap_index: dict[str, list[dict[str, object]]],
) -> list[ConservationReport]:
    """Run conservation over every table that has a receipt or a sentinel leg."""
    declared = collect_declared(runs, specs, lo=lo, hi=hi)
    tables = sorted(set(declared) | set(legs_by_table))
    reports: list[ConservationReport] = []
    for table in tables:
        date_col = _date_col_for(table, specs, legs_by_table)
        if not date_col:
            reports.append(
                ConservationReport(
                    table,
                    [
                        CrosscheckFinding(
                            "NO_BUSINESS_DATE_COL",
                            RED,
                            "",
                            table,
                            "既无 tasks.yaml date_col 也无 sentinel 腿，守恒无日期轴可判",
                        )
                    ],
                )
            )
            continue
        leg = (legs_by_table.get(table) or [None])[0]
        reports.append(
            check_table(
                table,
                date_col,
                declared=declared.get(table, {}),
                reader=reader,
                window=Window(lo, hi),
                gaps=list(gap_index.get(table, [])),
                leg=leg,  # type: ignore[arg-type]
            )
        )
    return reports


def _date_col_for(table: str, specs: dict[str, DataSupplyTaskSpec], legs_by_table: dict[str, list[SentinelLeg]]) -> str:
    """_date_col_for implementation."""
    for leg in legs_by_table.get(table, ()):
        if leg.date_col:
            return leg.date_col
    for spec in specs.values():
        if spec.table == table and spec.date_col:
            return spec.date_col
    return ""


def red_findings(reports: list[ConservationReport]) -> list[CrosscheckFinding]:
    """red_findings implementation."""
    return [f for r in reports for f in r.findings if f.severity == RED]


@dataclass(frozen=True)
class ControlResult:
    """负控制＝回执声明供数而仓库不动 ⇒ 必红；正控制＝表随回执动 ⇒ 必绿。"""

    ruler: str
    reddened: bool
    greened: bool
    codes: tuple[str, ...] = ()
    detail: str = ""
    observed_reads: int = 0

    @property
    def passed(self) -> bool:
        """passed implementation."""
        return self.reddened and self.greened


def _cons_control_fixture(rows_on_day: int | None):
    """Warehouse stub: report ``rows_on_day`` for the declared business day (None = untouched)."""
    from scripts.governance.data_supply.false_green_crosscheck import _untouched_projection

    if rows_on_day is None:
        return _untouched_projection

    def _projection(sql: str) -> Sequence[tuple[object, ...]]:
        """_projection implementation."""
        if "max(" in sql:
            return ((dt.date(2026, 9, 24),),)
        return ((dt.date(2026, 9, 24), rows_on_day),)

    return _projection


def run_counterfactual(as_of: dt.date | None = None) -> ControlResult:
    """反事实控制组：回执声明供了数、仓库纹丝不动 ⇒ 守恒尺必须红（波 3.3 判据）。"""
    hi = as_of or dt.date(2026, 9, 25)
    lo = hi - dt.timedelta(days=3)
    specs, runs, legs = _cons_control_inputs(hi)
    red_reader = StrictTruthReader(projection=_cons_control_fixture(None))
    reds = red_findings(
        evaluate(specs=specs, legs_by_table=legs, runs=runs, reader=red_reader, lo=lo, hi=hi, gap_index={})
    )
    green_reader = StrictTruthReader(projection=_cons_control_fixture(77))
    greens = red_findings(
        evaluate(specs=specs, legs_by_table=legs, runs=runs, reader=green_reader, lo=lo, hi=hi, gap_index={})
    )
    return ControlResult(
        ruler="3.3_supply_conservation",
        reddened=bool(reds),
        greened=not greens,
        codes=tuple(sorted({f.code for f in reds})),
        detail=f"负控制=声明 77 行 / 表侧不动 → 红项 {len(reds)} 条；正控制=声明与实到相等 → 红项 {len(greens)} 条",
        observed_reads=red_reader.reads,
    )


def _cons_control_inputs(hi: dt.date):
    """_cons_control_inputs implementation."""
    from zephyr.data.table_registry import get_registry

    bench_table = get_registry().table("market_etf_benchmark")  # 表名真源派生（禁硬编码 c1_market.etf_benchmark）
    day = hi - dt.timedelta(days=1)
    specs = {"etf_benchmark_build": DataSupplyTaskSpec("etf_benchmark_build", bench_table, "trade_date", ())}
    runs = [
        LedgerRun(
            1,
            "etf_benchmark_build",
            "SUCCESS",
            dt.datetime.combine(day, dt.time(2, 0), tzinfo=dt.timezone.utc),
            dt.datetime.combine(day, dt.time(2, 9), tzinfo=dt.timezone.utc),
            77,
            77,
        )
    ]
    legs = {bench_table: [SentinelLeg(bench_table, "trade_date", 10)]}
    return specs, runs, legs
