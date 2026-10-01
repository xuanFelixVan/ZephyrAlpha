# [BLUEPRINT] MOD-GOV-DS | docs/_working/total_command_closeout/10_wave_plan.md | 波 3.2（W-31 / Z-16）
# [MODULE] scripts.governance.data_supply.false_green_crosscheck
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.data_supply.supply_sources, scripts.governance.data_supply.strict_truth_reader
# [CONSUMERS] scripts.governance.data_supply.check_false_green_ledger; scripts.governance.data_supply.check_wave3_rulers;
#             [待登记] zephyr.data.integrity_checker._reconcile_task_runs 的"真值腿"（见 registration_needs.yaml）
# [STARTUP] imported
# [MATURITY] testing
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] permanent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 读数失败 -> 冒泡 TruthReadError（禁把失败洗成空表）; 台账零行 -> 出 EMPTY_LEDGER 红项（禁"无记录即无违规"）
# [A_module] module_id=MOD-GOV-DS-FG | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；计数以现读为准禁照抄册面旧数；探测失败必报红不得静默降级
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [TESTS] 案卷内附命令原文与实测读数，可复算
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# noqa: m02-manual  M02豁免: 一次性判据计算，无常驻循环
"""3.2 假绿灯交叉尺（W-31 / Z-16）。

Z-16 口径原文：交叉尺＝**回执与真值互证**（``rows_written`` 记回执 + 独立读最终真值/最新业务日），
不符报红并**降级下游**；新增尺需自带反事实控制组。
X-24 口径：违规名单**现跑现出**——本件不携带任何历史名单常量。

既有宿主的缺口正是本件的落点：``integrity_checker._reconcile_task_runs`` 只对账
"今日应跑任务在 task_runs 是否有 SUCCESS"（台账自证），从不回读目标表真值，
所以"记了 SUCCESS 而表里 0 行"在它眼里是绿的。本件补的就是那条**真值腿**。
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, Sequence

from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader
from scripts.governance.data_supply.supply_sources import (
    DataSupplyTaskSpec,
    LedgerRun,
    SentinelLeg,
    downstream_tables,
    utc_date_of,
)

RED = "RED"
WARN = "WARN"
SUCCESS_STATUSES = frozenset({"SUCCESS"})


@dataclass(frozen=True)
class CrosscheckFinding:
    code: str
    severity: str
    task_id: str
    table: str
    detail: str


@dataclass(frozen=True)
class CrosscheckVerdict:
    findings: tuple[CrosscheckFinding, ...] = ()
    downgraded_tasks: tuple[str, ...] = ()
    downgraded_tables: tuple[str, ...] = ()
    offending_tasks: tuple[str, ...] = ()
    checked_runs: int = 0

    @property
    def red(self) -> tuple[CrosscheckFinding, ...]:
        return tuple(f for f in self.findings if f.severity == RED)

    @property
    def ok(self) -> bool:
        return not self.red


def _pick_leg(legs: Sequence[SentinelLeg], table: str) -> SentinelLeg | None:
    fresh = [x for x in legs.get(table, ()) if x.date_col]
    return fresh[0] if fresh else None


def _cross_check_run(
    run: LedgerRun,
    spec: DataSupplyTaskSpec | None,
    leg: SentinelLeg | None,
    reader: StrictTruthReader,
    as_of: dt.date,
) -> list[CrosscheckFinding]:
    out: list[CrosscheckFinding] = []
    if spec is None:
        return [CrosscheckFinding("UNKNOWN_TASK", RED, run.task_id, "", "台账记 SUCCESS 但 tasks.yaml 无此任务声明")]
    if not spec.table:
        return [CrosscheckFinding("NO_TARGET_TABLE", RED, run.task_id, "", "任务声明缺 table，回执无处互证")]
    day = utc_date_of(run.finished_at or run.started_at) or as_of
    truth = reader.read_leg(spec.table, spec.date_col or "trade_date", lo=day, hi=day, past_only=True)
    out.extend(_receipt_findings(run, spec, leg, truth))
    out.extend(_freshness_findings(run, spec, leg, truth, reader, as_of))
    return out


def _receipt_findings(
    run: LedgerRun, spec: DataSupplyTaskSpec, leg: SentinelLeg | None, truth
) -> list[CrosscheckFinding]:
    written = run.rows_written or 0
    static = bool(leg and leg.cadence == "static_backfill")
    if written <= 0:
        return _zero_receipt_findings(run, spec, leg, truth)
    if static:
        if truth.latest_business_date is None:
            return [
                CrosscheckFinding(
                    "FULL_REFRESH_EMPTY",
                    RED,
                    run.task_id,
                    spec.table,
                    "全量刷新类任务记 SUCCESS 且写了行，但表内无任何业务日",
                )
            ]
        return []
    if truth.rows_in_window == 0:
        day = _run_day(run)
        return [
            CrosscheckFinding(
                "FAKE_GREEN",
                RED,
                run.task_id,
                spec.table,
                f"回执 rows_written={written}，业务日 {day} 表侧独立回读为 0 行（写后回读不闭合）",
            )
        ]
    if truth.rows_in_window < written:
        return [
            CrosscheckFinding(
                "RECEIPT_OVERSTATES",
                RED,
                run.task_id,
                spec.table,
                f"回执 {written} 行 > 实到 {truth.rows_in_window} 行（蒸发）",
            )
        ]
    if truth.rows_in_window > written:
        return [
            CrosscheckFinding(
                "ARRIVAL_EXCEEDS_RECEIPT",
                WARN,
                run.task_id,
                spec.table,
                f"实到 {truth.rows_in_window} 行 > 回执 {written} 行（未申报的旁路写入）",
            )
        ]
    return []


def _run_day(run: LedgerRun) -> dt.date | None:
    return utc_date_of(run.finished_at or run.started_at)


def _zero_receipt_findings(
    run: LedgerRun, spec: DataSupplyTaskSpec, leg: SentinelLeg | None, truth
) -> list[CrosscheckFinding]:
    if leg and leg.allow_empty:
        if not leg.gap_id:
            return [
                CrosscheckFinding(
                    "SILENT_EMPTY_NO_GAP",
                    RED,
                    run.task_id,
                    spec.table,
                    "allow_empty 静默但无 gap_id 凭据（BRK-046 纪律）",
                )
            ]
        return [
            CrosscheckFinding("DECLARED_EMPTY", WARN, run.task_id, spec.table, f"空跑放行，凭据 gap_id={leg.gap_id}")
        ]
    if truth.rows_in_window == 0 and truth.latest_business_date is None:
        return [
            CrosscheckFinding(
                "SUCCESS_EMPTY_TABLE",
                RED,
                run.task_id,
                spec.table,
                "记 SUCCESS 且回执 0 行，目标表确证为空（0 行=读失败已被严格通道排除）",
            )
        ]
    return [
        CrosscheckFinding("SUCCESS_ZERO_ROWS", WARN, run.task_id, spec.table, "跑过无差异（表非空但本业务日无增量）")
    ]


def _freshness_findings(
    run: LedgerRun, spec: DataSupplyTaskSpec, leg: SentinelLeg | None, truth, reader: StrictTruthReader, as_of: dt.date
) -> list[CrosscheckFinding]:
    if leg is None or not leg.max_lag_days:
        return [
            CrosscheckFinding(
                "NO_FRESHNESS_LEG", WARN, run.task_id, spec.table, "该表未挂 data_supply_sentinel 新鲜度腿，滞后不可判"
            )
        ]
    latest = reader.latest_business_date(spec.table, leg.date_col, not_after=as_of if leg.past_only else None)
    if latest is None:
        return [
            CrosscheckFinding(
                "FRESHNESS_UNKNOWN_EMPTY", RED, run.task_id, spec.table, "业务表 max(date) 为空，新鲜度无从背书"
            )
        ]
    lag = (as_of - latest).days
    if lag > leg.max_lag_days:
        return [
            CrosscheckFinding(
                "STALE_BEHIND_RECEIPT",
                RED,
                run.task_id,
                spec.table,
                f"台账记 SUCCESS 但最新业务日 {latest} 落后 {lag} 天 > 声明阈值 {leg.max_lag_days} 天",
            )
        ]
    return []


def evaluate(
    runs: Iterable[LedgerRun],
    specs: dict[str, DataSupplyTaskSpec],
    legs_by_table: dict[str, list[SentinelLeg]],
    reader: StrictTruthReader,
    *,
    as_of: dt.date,
    downstream: dict[str, tuple[str, ...]] | None = None,
) -> CrosscheckVerdict:
    """Cross-check every SUCCESS receipt against independently read truth."""
    materialised = tuple(r for r in runs if r.status in SUCCESS_STATUSES)
    if not materialised:
        return CrosscheckVerdict(
            findings=(
                CrosscheckFinding("EMPTY_LEDGER", RED, "", "", "台账窗口内零 SUCCESS 回执——无回执可背书，禁判绿"),
            )
        )
    findings: list[CrosscheckFinding] = []
    red_tasks: list[str] = []
    for run in materialised:
        spec = specs.get(run.task_id)
        table = spec.table if spec else ""
        leg = _pick_leg(legs_by_table, table)
        got = _cross_check_run(run, spec, leg, reader, as_of)
        findings.extend(got)
        if any(f.severity == RED for f in got):
            red_tasks.append(run.task_id)
    return _with_downgrade(findings, red_tasks, downstream or {}, specs, materialised)


def _with_downgrade(
    findings: list[CrosscheckFinding],
    red_tasks: Sequence[str],
    downstream: dict[str, tuple[str, ...]],
    specs: dict[str, DataSupplyTaskSpec],
    runs: Sequence[LedgerRun],
) -> CrosscheckVerdict:
    tasks: set[str] = set()
    tables: set[str] = set()
    for task_id in red_tasks:
        tasks.update(downstream.get(task_id, ()))
        tables.update(downstream_tables(task_id, downstream, specs))
    return CrosscheckVerdict(
        findings=tuple(findings),
        downgraded_tasks=tuple(sorted(tasks)),
        downgraded_tables=tuple(sorted(tables)),
        offending_tasks=tuple(sorted(set(red_tasks))),
        checked_runs=len(runs),
    )


@dataclass(frozen=True)
class ControlResult:
    """反事实控制组：喂假 SUCCESS 而目标表不动 ⇒ 尺必须红；表随回执动 ⇒ 尺必须绿。

    两半缺一不可：只会红的尺与只会绿的尺同样是装饰件。
    """

    ruler: str
    reddened: bool
    greened: bool
    codes: tuple[str, ...] = ()
    detail: str = ""
    downgraded_tasks: tuple[str, ...] = ()
    observed_reads: int = 0

    @property
    def passed(self) -> bool:
        return self.reddened and self.greened


_UNTOUCHED_MAX_MARK = "max("


def _untouched_projection(sql: str) -> Sequence[tuple[object, ...]]:
    """Negative-control warehouse: it never moved (per-day counts empty, max(date) NULL)."""
    if _UNTOUCHED_MAX_MARK in sql:
        return ((None,),)
    return ()


def _moving_warehouse(written: int):
    """Positive control: a warehouse that really received the declared rows."""

    def _projection(sql: str) -> Sequence[tuple[object, ...]]:
        if "max(" in sql:
            return ((dt.date(2026, 9, 24),),)
        return ((dt.date(2026, 9, 24), written),)

    return _projection


def run_counterfactual(as_of: dt.date | None = None) -> ControlResult:
    """Z-16 / 波 3.2 判据自带控制组："喂一行假 SUCCESS 而目标表不动 ⇒ 尺必须红"。"""
    day = as_of or dt.date(2026, 9, 25)
    biz_day = day - dt.timedelta(days=1)
    specs = _control_specs()
    legs = {"c3_fundamental.suspend_status": [SentinelLeg("c3_fundamental.suspend_status", "trade_date", 5)]}
    downstream = {"suspend_derive": ("downstream_consumer",)}
    reader = StrictTruthReader(projection=_untouched_projection)
    red_verdict = evaluate([_control_run(biz_day)], specs, legs, reader, as_of=day, downstream=downstream)
    green_reader = StrictTruthReader(projection=_moving_warehouse(120))
    green_verdict = evaluate([_control_run(biz_day)], specs, legs, green_reader, as_of=day, downstream=downstream)
    return ControlResult(
        ruler="3.2_false_green",
        reddened=bool(red_verdict.red),
        greened=green_verdict.ok,
        codes=tuple(sorted({f.code for f in red_verdict.red})),
        detail=f"负控制=假 SUCCESS(rows_written=120) 表侧不动 → 红项 {len(red_verdict.red)} 条；正控制=表随回执动 → 红项 {len(green_verdict.red)} 条",
        downgraded_tasks=red_verdict.downgraded_tasks,
        observed_reads=reader.reads,
    )


def _control_specs() -> dict[str, DataSupplyTaskSpec]:
    return {
        "suspend_derive": DataSupplyTaskSpec("suspend_derive", "c3_fundamental.suspend_status", "trade_date", ()),
        "downstream_consumer": DataSupplyTaskSpec(
            "downstream_consumer", "c3_fundamental.derived_x", "trade_date", ("suspend_derive",)
        ),
    }


def _control_run(day: dt.date) -> LedgerRun:
    lo = dt.datetime.combine(day, dt.time(1, 0), tzinfo=dt.timezone.utc)
    hi = dt.datetime.combine(day, dt.time(1, 5), tzinfo=dt.timezone.utc)
    return LedgerRun(9_999_999, "suspend_derive", "SUCCESS", lo, hi, 120, 120)
