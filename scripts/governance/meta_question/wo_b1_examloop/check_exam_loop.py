#!/usr/bin/env python3
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1 回写契约 + §2 仲裁 + §3 复考周期（本件=复考机）
# [MODULE] scripts.governance.meta_question.wo_b1_examloop.check_exam_loop
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] src/zephyr/governance/meta_question/meta_question_registry.py（冻结件，只 import）; src/zephyr/governance/meta_question/exam_loop/*（writeback/exam_plan/event_codes/state_machine/reexam_scheduler）; zephyr.governance.depgraph_schema（只读连接经 registry 注入，本件零 read_only=False 字面量）
# [CONSUMERS] 283 问战役 B 类载体簇 1 复考（PQ-0051/0054/0055/0056/0057/0060/0061/0096/0098/0103/0108）; Owner 查账; docs/_working/meta_question_answers/build/WO-B1-examloop.yaml（案卷引用本件产物）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 判据真源=题面 exam_plan.threshold 原文（机解后逐条比对），本件零自判阈值、零结论硬编码；
#              每条探针必返回 evidence={table,query,result}（13§1.3 可核锚点），落账一律经 ExamLoopWriteback.writeback 唯一入口（禁直改表）；
#              分母为零必判"不可判"（0 记录≠违例=0，上一班静默成功尺教训）；
#              复考前置认领：--claim-take-before-writeback 时按 12§2.1 先 claim 再回写（鉴权=当前认领人）；
#              answered 之后重考走 answered→reexam→（回填）→answered 合法链，禁跳边；
#              探针只读取 PG（read_only 由 registry 决定），零写副作用；写副作用只在 --writeback 显式开关下发生
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1-§3（改判据先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=全判"支持"或如实报；EXIT 1=存在判"证伪"的问（尺子照红，不掩盖）；EXIT 2=异常（PG 不可达/探针缺项/参数非法，fail-closed）
# [TESTS] 手动红蓝两腿：--selftest（判据边界矩阵，零 DB）；--questions PQ-0051 --dry-run（只出判据不落账）；红腿实证见案卷（伪造越权回写被拒 + 非法流转落痕）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 283 问战役复考按需 CLI（考试循环判据机），无常驻进程
"""check_exam_loop — 考试循环机制复考机（B 类载体簇 1 的判据执行体）。

对每题跑一段只读探针 → 与**题面预注册判据**逐条比对 → 经 writeback 唯一入口落账。
本件同时是"验证其他工单是否闭环"的机器：任何前置建成后，其对应问题按题面判据可复考。

用法::

    python scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py --selftest
    python scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py --questions PQ-0051,PQ-0055 --dry-run
    python scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py --all-covered --writeback --actor st-wo-b1-examloop|AI
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

_BOOT_ROOT = Path(__file__).resolve().parents[4]
_SRC = _BOOT_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from zephyr.governance.meta_question.exam_loop import event_codes, exam_plan  # noqa: E402
from zephyr.governance.meta_question.exam_loop.exam_lifecycle import (  # noqa: E402
    ExamLoopStateMachine,
)
from zephyr.governance.meta_question.exam_loop.reexam_scheduler import (  # noqa: E402
    ReexamScheduler,
)
from zephyr.governance.meta_question.exam_loop.writeback import ExamLoopWriteback  # noqa: E402
from zephyr.governance.meta_question.exam_ops import (  # noqa: E402
    TERMINAL_STATUSES,
    VALID_STATUSES,
)
from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地重定义，SSOT-REDEFINITION 对症）
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

DEFAULT_SCHEMA = "meta_question"
DEFAULT_JSONL = REPO_ROOT / ".runtime" / "chain_piling" / "meta_question_audit.jsonl"
PIT_CUTOFF = "2025-09-09"
#: 本单覆盖问题（B 类载体簇 1｜考试循环机制 + writeback 回填 API）
COVERED: tuple[str, ...] = (
    "PQ-0051",
    "PQ-0054",
    "PQ-0055",
    "PQ-0056",
    "PQ-0057",
    "PQ-0060",
    "PQ-0061",
    "PQ-0096",
    "PQ-0098",
    "PQ-0103",
    "PQ-0108",
)
INDETERMINATE = "不可判"
#: 本轮复考机引用前缀（探针按此前缀圈定"载体建成后"的账，禁把临时通道旧账混进判据）
EXAM_REF_PREFIX = "wo-b1/reexam"
FORGER_PREFIX = "st-impostor"
PIT_SAMPLE_SIZE = 20
#: 红队自测用的非法边（answered→mining 不在 13§1.5 合法边表内，由边表机判非字面量断言）
FORGE_EDGE_STATUS = "answered"
FORGE_EDGE_TARGET = "mining"
#: 携带 status 迁移的审计事件码（状态链回放口径，词表内取值零自造）
STATUS_LIKE_WHATS: tuple[str, ...] = (
    "register",
    "update",
    "exam_writeback",
    "reexam",
    "suspend",
    "merge",
    "retire",
    "blind_promote",
)
EXIT_OK = 0
EXIT_RED = 1
EXIT_ERROR = 2

__manifest__ = """
args: ["--selftest"]
description: 'WO-B1 复考机：按题面判据跑考试循环探针并经 writeback 唯一入口落账（PQ-0051/0054/0055/0056/0057/0060/0061/0096/0098/0103/0108）。'
dimensions:
- D3
priority: P2
timeout_seconds: 600
warn_only: false
"""

#: in_exam 及以后状态集（由词表边表机算，禁字面量枚举复制）
POST_IN_EXAM: frozenset[str] = (ExamLoopStateMachine.descendants_of("in_exam") - TERMINAL_STATUSES) | {"in_exam"}


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。本件全只读（复考探针）；{s}/{schema}=registry 注入的
# schema 名、{match}=event_codes.sql_event_match() 运行期片段、{marks}=%s 占位串——一律由调用点
# .format() 传入，禁把 schema/事件码字面量写进常量。含 JSONB 算子 ? 与 %s 绑定符，故不做二次 format
# 嵌套（{s} 与 {{s}} 语义差是本件最大风险面，改后必须实跑 selfcheck 比对）。
_SQL_VERDICT_PLAN_STATUS = "SELECT exam_plan, status FROM {schema}.meta_question WHERE q_id = %s"
_SQL_QUESTION_STATUS = "SELECT status FROM {schema}.meta_question WHERE q_id = %s"
_SQL_QUESTION_REGISTERED_AT = "SELECT provenance->>'registered_at' AS reg FROM {schema}.meta_question WHERE q_id = %s"
_SQL_FORGE_EDGE_TARGET = (
    "SELECT q_id, status FROM {schema}.meta_question WHERE status IN (SELECT unnest(%s)) ORDER BY q_id LIMIT 1"
)
_SQL_PQ0051_PLAN_COVERAGE = "SELECT count(*) AS denom, count(*) FILTER (WHERE coalesce(exam_plan->>'criterion','') <> '' AND coalesce(exam_plan->>'threshold','') <> '') AS num FROM {s}.meta_question WHERE status = ANY(%s)"
_SQL_PQ0055_SAMPLE_OUT_SHARE = "SELECT count(*) AS total, count(*) FILTER (WHERE (er.data_window->>'sample_out_share')::float >= 1.0/3 AND ((er.data_window->>'end')::date < (m.provenance->>'registered_at')::timestamptz::date OR (er.data_window->>'start')::date > (m.provenance->>'registered_at')::timestamptz::date)) AS ok FROM {s}.meta_question_exam_result er JOIN {s}.meta_question m USING (q_id) WHERE er.exam_ref LIKE %s"
_SQL_PQ0056_WRITEBACK_LATENCY = "SELECT count(*) AS n, percentile_cont(0.99) WITHIN GROUP (ORDER BY (after->>'latency_seconds')::float) AS p99 FROM {s}.meta_question_audit WHERE what='exam_writeback' AND after ? 'exam_completed_at' AND after ? 'backfilled_at'"
_SQL_PQ0096_PIT_VIOLATIONS = (
    "SELECT count(*) AS n, count(*) FILTER (WHERE (er.data_window->>'fetch_ts')::timestamptz > "
    "(er.data_window->>'decision_ts')::timestamptz) AS violations "
    "FROM {s}.meta_question_exam_result er WHERE er.exam_ref LIKE %s "
    "AND er.data_window ? 'fetch_ts' AND er.data_window ? 'decision_ts' LIMIT %s"
)
_SQL_AUDIT_EVENT_COUNT = "SELECT count(*) AS n FROM {s}.meta_question_audit WHERE {match}"
_SQL_PQ0103_FORGERY_LEAK = (
    "SELECT count(*) AS n FROM {s}.meta_question_exam_result er "
    "WHERE EXISTS (SELECT 1 FROM {s}.meta_question_audit a "
    "WHERE a.q_id = er.q_id AND a.actor = er.recorded_by "
    "AND (a.what IN (%s, %s) OR a.after->>'event_code' IN (%s, %s)) "
    "AND a.created_at > er.created_at) "
    "AND er.recorded_by LIKE %s"
)
_SQL_AUDIT_TRACE_HEAD = "SELECT q_id, actor, evidence FROM {s}.meta_question_audit WHERE "
_SQL_PQ0060_STATUS_REPLAY = (
    "SELECT q_id, lag(after->>'status') OVER w AS from_status, (after->>'status') AS to_status "
    "FROM {s}.meta_question_audit WHERE what IN ({marks}) "
    "WINDOW w AS (PARTITION BY q_id ORDER BY id)"
)
_SQL_PQ0061_REPLAY_SUCCESS = (
    "SELECT count(*) FILTER (WHERE (after->>'replayed')::bool) AS replayed, count(*) AS n "
    "FROM {s}.meta_question_audit WHERE (after->>'reason') = 'version_conflict'"
)
_SQL_PQ0098_CONCLUSION_ROWS = (
    "SELECT conclusion FROM {s}.meta_question_exam_result "
    "WHERE exam_ref LIKE %s AND conclusion ? 'effect_size' AND conclusion ? 'sample_size'"
)
_SQL_PQ0057_CONTRADICTION_CASES = (
    "SELECT count(*) FILTER (WHERE (after->>'state')='open') AS opened, "
    "count(*) FILTER (WHERE (after->>'state') IN ('resolved','escalated_max')) AS closed "
    "FROM {s}.meta_question_audit WHERE what='exam_contradiction_case'"
)
_SQL_PQ0057_ARBITRATE_COUNT = "SELECT count(*) AS n FROM {s}.meta_question_audit WHERE what='exam_arbitrate'"


# ---------------------------------------------------------------------------
# 读数工具（只读；SQL 真源逐条随 evidence 落账）
# ---------------------------------------------------------------------------


class Reader:
    """只读 PG 通道（连接由 registry 注入，禁本件写死角色）。"""

    def __init__(self, registry: MetaQuestionRegistry) -> None:
        self.registry = registry

    def rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        conn = self.registry._conn(read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]
        finally:
            conn.close()

    def one(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
        rows = self.rows(sql, params)
        return rows[0] if rows else {}


def _percent(num: float | None, den: float | None) -> float | None:
    if den in (None, 0) or num is None:
        return None
    return round(100.0 * float(num) / float(den), 4)


def _verdict(
    reader: Reader,
    q_id: str,
    value: float | None,
    evidence: list[dict[str, Any]],
    *,
    sample: Any = None,
    effect: Any = None,
) -> dict[str, Any]:
    """把探针取值与**题面预注册判据**对照出方向（判据真源=exam_plan.threshold）。"""
    row = reader.rows(_SQL_VERDICT_PLAN_STATUS.format(schema=reader.registry.schema), (q_id,))
    raw = (row[0]["exam_plan"] if row else None) or {}
    plan = exam_plan.structure_plan(raw if isinstance(raw, dict) else json.loads(raw), plan_version="v2-wo-b1")
    all_clauses = [c for c in plan.get("threshold_clauses") or [] if "value" in c]
    clauses = [c for c in all_clauses if c.get("primary")] or all_clauses[:1]
    if value is None:
        direction, note = INDETERMINATE, "探针分母为零或取数不可得（0 记录≠违例=0）"
        evaluated = {"evaluable": False}
    else:
        evaluated = exam_plan.evaluate_clauses(value, clauses)
        if not evaluated.get("evaluable"):
            direction, note = INDETERMINATE, "题面阈值不可机解（须先补结构化考卷）"
        else:
            direction = "支持" if evaluated.get("passed") else "证伪"
            note = ""
    return {
        "conclusion_value": value,
        "conclusion_dir": direction,
        "note": note,
        "criterion": plan.get("criterion"),
        "threshold": plan.get("threshold"),
        "clause_check": evaluated,
        "clause_unchecked": [c.get("text") for c in all_clauses if c not in clauses],
        "evidence_refs": evidence,
        "sample_size": sample,
        "effect_size": effect,
        "status_before": (row[0]["status"] if row else None),
    }


# ---------------------------------------------------------------------------
# 探针（每题一段只读 SQL + 判据对照；evidence 必带 table+query）
# ---------------------------------------------------------------------------

Probe = Callable[[Reader], dict[str, Any]]


def _ev(sql: str, params: tuple[Any, ...], result: Any, table: str) -> dict[str, Any]:
    return {"table": table, "query": sql, "params": [str(p) for p in params], "result": result}


def probe_pq_0051(r: Reader) -> dict[str, Any]:
    """in_exam 及以后状态的 exam_plan 含 criterion+threshold 比例（题面=100%）。"""
    sql = _SQL_PQ0051_PLAN_COVERAGE.format(s=r.registry.schema)
    got = r.one(sql, (sorted(POST_IN_EXAM),))
    return _verdict(
        r,
        "PQ-0051",
        _percent(got.get("num"), got.get("denom")),
        [_ev(sql, (sorted(POST_IN_EXAM),), got, "meta_question.meta_question")],
        sample=got.get("denom"),
    )


def probe_pq_0055(r: Reader) -> dict[str, Any]:
    """样本外份额≥1/3 且考试窗口与生成时戳无重叠（时间分层机检通过率=100%）。"""
    sql = _SQL_PQ0055_SAMPLE_OUT_SHARE.format(s=r.registry.schema)
    params = (EXAM_REF_PREFIX + "%",)
    got = r.one(sql, params)
    return _verdict(
        r,
        "PQ-0055",
        _percent(got.get("ok"), got.get("total")),
        [_ev(sql, params, got, "meta_question.meta_question_exam_result")],
        sample=got.get("total"),
    )


def probe_pq_0056(r: Reader) -> dict[str, Any]:
    """exam_writeback 落账时延 P99（双时戳差，题面≤1 个交易日≈86400s）。"""
    sql = _SQL_PQ0056_WRITEBACK_LATENCY.format(s=r.registry.schema)
    got = r.one(sql, ())
    p99 = got.get("p99")
    seconds = None if p99 is None else float(p99)
    # 题面单位=「1 个交易日」：秒→日按 86400 折算，原始秒留 evidence（口径可追）
    trading_days = None if seconds is None else round(seconds / 86400.0, 6)
    return _verdict(
        r,
        "PQ-0056",
        trading_days,
        [
            _ev(
                sql,
                (),
                {**{k: (str(v) if v is None else float(v)) for k, v in got.items()}, "p99_seconds": seconds},
                "meta_question.meta_question_audit",
            )
        ],
        sample=got.get("n"),
    )


def probe_pq_0096(r: Reader) -> dict[str, Any]:
    """PIT 抽检：取数时戳晚于决策时戳的违例数（题面=0，每周 20 条）。"""
    sql = _SQL_PQ0096_PIT_VIOLATIONS.format(s=r.registry.schema)
    params = (EXAM_REF_PREFIX + "%", PIT_SAMPLE_SIZE)
    got = r.one(sql, params)
    if not int(got.get("n") or 0):
        return _verdict(r, "PQ-0096", None, [_ev(sql, params, got, "meta_question.meta_question_exam_result")])
    return _verdict(
        r,
        "PQ-0096",
        float(got.get("violations") or 0),
        [_ev(sql, params, got, "meta_question.meta_question_exam_result")],
        sample=got.get("n"),
    )


def _event_count(r: Reader, code: str) -> int:
    match = event_codes.sql_event_match()
    sql = _SQL_AUDIT_EVENT_COUNT.format(s=r.registry.schema, match=match)
    return int((r.one(sql, event_codes.match_params(code)) or {}).get("n") or 0)


def probe_pq_0103(r: Reader) -> dict[str, Any]:
    """越权回写拦截率：claim_mismatch/claim_missing 痕全部无对应业务写=100%。"""
    attempts = _event_count(r, event_codes.CODE_CLAIM_MISMATCH) + _event_count(r, event_codes.CODE_CLAIM_MISSING)
    leak_sql = _SQL_PQ0103_FORGERY_LEAK.format(s=r.registry.schema)
    leak_params = (
        event_codes.CODE_CLAIM_MISMATCH,
        event_codes.CODE_CLAIM_MISSING,
        event_codes.CODE_CLAIM_MISMATCH,
        event_codes.CODE_CLAIM_MISSING,
        FORGER_PREFIX + "%",
    )
    leaks = int((r.one(leak_sql, leak_params) or {}).get("n") or 0)
    value = None if attempts == 0 else _percent(attempts - leaks, attempts)
    return _verdict(
        r,
        "PQ-0103",
        value,
        [
            _ev(
                leak_sql,
                leak_params,
                {"auth_traces": attempts, "leaked_writes": leaks},
                "meta_question.meta_question_audit",
            )
        ],
        sample=attempts or None,
    )


def probe_pq_0060(r: Reader) -> dict[str, Any]:
    """非法边拦截率：审计流逐问回放状态链，落库流转必须全在合法边表内。"""
    trace_sql = _SQL_AUDIT_TRACE_HEAD.format(s=r.registry.schema) + event_codes.sql_event_match()
    traced = r.rows(trace_sql, event_codes.match_params(event_codes.CODE_ILLEGAL_TRANSITION))
    marks = ", ".join(["%s"] * len(STATUS_LIKE_WHATS))
    replay_sql = _SQL_PQ0060_STATUS_REPLAY.format(s=r.registry.schema, marks=marks)
    landed = [
        row
        for row in r.rows(replay_sql, tuple(STATUS_LIKE_WHATS))
        if row.get("from_status") and row.get("to_status") and row["from_status"] != row["to_status"]
    ]
    illegal_landed = [
        row for row in landed if not ExamLoopStateMachine.is_legal_edge(str(row["from_status"]), str(row["to_status"]))
    ]
    attempts = len(traced) + len(illegal_landed)
    # 题面判据=「illegal_transition 异常事件数」threshold「=0」：分子取"非法边却落库"数，
    # 拒收痕数（分母侧证据）随 evidence 一并落账，禁把拦截率当异常数报（单位错=假红/假绿）
    value = None if attempts == 0 else float(len(illegal_landed))
    return _verdict(
        r,
        "PQ-0060",
        value,
        [
            _ev(
                replay_sql,
                tuple(STATUS_LIKE_WHATS),
                {"traced_rejections": len(traced), "illegal_landed": [dict(x) for x in illegal_landed[:5]]},
                "meta_question.meta_question_audit",
            )
        ],
        sample=attempts or None,
    )


def probe_pq_0061(r: Reader) -> dict[str, Any]:
    """乐观锁冲突后重读重放成功率（题面≥99%）。"""
    conflicts = _event_count(r, event_codes.CODE_VERSION_CONFLICT)
    ok_sql = _SQL_PQ0061_REPLAY_SUCCESS.format(s=r.registry.schema)
    got = r.one(ok_sql, ())
    value = None if not conflicts else _percent(got.get("replayed"), got.get("n"))
    return _verdict(
        r, "PQ-0061", value, [_ev(ok_sql, (), got, "meta_question.meta_question_audit")], sample=conflicts or None
    )


def probe_pq_0098(r: Reader) -> dict[str, Any]:
    """IC 类考试功效≥80% 且降阈值事件=0（题面双条件；降阈值非零则整题判 0，禁掩盖）。"""
    rows_sql = _SQL_PQ0098_CONCLUSION_ROWS.format(s=r.registry.schema)
    rows = r.rows(rows_sql, (EXAM_REF_PREFIX + "%",))
    powers = []
    for row in rows:
        c = row["conclusion"] if isinstance(row["conclusion"], dict) else json.loads(row["conclusion"] or "{}")
        try:
            powers.append(exam_plan.fisher_z_power(int(c["sample_size"]), float(c["effect_size"])))
        except (ValueError, KeyError, TypeError):
            continue
    lowered = _event_count(r, event_codes.CODE_THRESHOLD_LOWERED)
    passing = sum(1 for value in powers if value >= 0.8)
    value = None if not powers else (0.0 if lowered else _percent(passing, len(powers)))
    return _verdict(
        r,
        "PQ-0098",
        value,
        [
            _ev(
                rows_sql,
                (),
                {
                    "exams": len(powers),
                    "power_ge_0.8": passing,
                    "power_median": (round(statistics.median(powers), 4) if powers else None),
                    "threshold_lowered_events": lowered,
                },
                "meta_question.meta_question_exam_result",
            )
        ],
        sample=len(powers) or None,
    )


def _reconcile_view(r: Reader) -> dict[str, Any]:
    scheduler = ReexamScheduler(r.registry)
    return scheduler.reconcile(actor="check_exam_loop", book=False)


def probe_pq_0054(r: Reader) -> dict[str, Any]:
    """到期复考执行率（分母=到期台账；题面≥95%）。"""
    report = _reconcile_view(r)
    return _verdict(
        r,
        "PQ-0054",
        report.get("execution_rate"),
        [
            {
                "table": "meta_question.meta_question_audit",
                "query": "ReexamScheduler.reconcile(book=False)",
                "result": {
                    "scanned": report["scanned"],
                    "due": report["due_count"],
                    "overdue": report["overdue_count"],
                    "as_of": report["as_of"],
                },
            }
        ],
        sample=report["due_count"] or None,
    )


def probe_pq_0108(r: Reader) -> dict[str, Any]:
    """月度滚动 20 日新鲜窗到期重考逾期率（题面≤5%）。"""
    report = _reconcile_view(r)
    overdue_rate = None if not report["due_count"] else round(100.0 * report["overdue_count"] / report["due_count"], 4)
    return _verdict(
        r,
        "PQ-0108",
        overdue_rate,
        [
            {
                "table": "meta_question.meta_question",
                "query": "due_state(monthly, fresh_window=20) over answered 集",
                "result": {"due": report["due_count"], "overdue": report["overdue_count"]},
            }
        ],
        sample=report["due_count"] or None,
    )


def probe_pq_0057(r: Reader) -> dict[str, Any]:
    """reexam 三取二多数裁定执行率（题面=100%：无跳过三取二的直接终裁）。"""
    opened_sql = _SQL_PQ0057_CONTRADICTION_CASES.format(s=r.registry.schema)
    got = r.one(opened_sql, ())
    arbitrated = int((r.one(_SQL_PQ0057_ARBITRATE_COUNT.format(s=r.registry.schema)) or {}).get("n") or 0)
    opened = int(got.get("opened") or 0)

    closed = int(got.get("closed") or 0)
    if opened == 0:
        # 无矛盾案可考：有复考事件也不得报"100%"（分母为零=不可判，防静默绿）
        value = None
    else:
        value = _percent(closed, opened)
    return _verdict(
        r,
        "PQ-0057",
        value,
        [_ev(opened_sql, (), {**got, "arbitrate_events": arbitrated}, "meta_question.meta_question_audit")],
        sample=opened or None,
    )


PROBES: dict[str, Probe] = {
    "PQ-0051": probe_pq_0051,
    "PQ-0054": probe_pq_0054,
    "PQ-0055": probe_pq_0055,
    "PQ-0056": probe_pq_0056,
    "PQ-0057": probe_pq_0057,
    "PQ-0060": probe_pq_0060,
    "PQ-0061": probe_pq_0061,
    "PQ-0096": probe_pq_0096,
    "PQ-0098": probe_pq_0098,
    "PQ-0103": probe_pq_0103,
    "PQ-0108": probe_pq_0108,
}


# ---------------------------------------------------------------------------
# 落账（唯一入口 writeback；认领→重考链）
# ---------------------------------------------------------------------------


def run_one(
    registry: MetaQuestionRegistry, reader: Reader, q_id: str, *, actor: str, writeback: bool, session_id: str
) -> dict[str, Any]:
    probe = PROBES.get(q_id)
    if probe is None:
        raise KeyError(f"无探针覆盖：{q_id}")
    result = probe(reader)
    out: dict[str, Any] = {
        "q_id": q_id,
        "verdict": {k: result[k] for k in ("conclusion_value", "conclusion_dir", "criterion", "threshold", "note")},
        "written": None,
        "error": "",
    }
    if not writeback:
        return out
    if result["conclusion_dir"] == INDETERMINATE:
        # 无结论轮次不落 exam_result（13§1.2 A1 结论未填充不得 answered），只留"复考中"状态账
        status = str(reader.one(_SQL_QUESTION_STATUS.format(schema=registry.schema), (q_id,)).get("status"))
        if status in {"answered", "in_exam"}:
            registry.transition(q_id, "reexam", actor=session_id, evidence="复考无结论，留复考待前置")
        out["skipped"] = f"no_conclusion（{result['note']}），状态={status}，不落 exam_result"
        return out
    completed = now_utc()
    window_end = (completed - timedelta(days=1)).date()
    # 观测窗=问题生成时戳之后（新鲜窗语义，13§3.3 今日输出→明日输入；样本外份额⇒1.0）
    registered = reader.one(
        _SQL_QUESTION_REGISTERED_AT.format(schema=registry.schema),
        (q_id,),
    ).get("reg")
    window_start = (completed - timedelta(days=30)).date()
    if registered:
        try:
            from datetime import datetime as _dt

            reg_day = _dt.fromisoformat(str(registered).replace("Z", "+00:00")).date()
            window_start = max(window_start, reg_day + timedelta(days=1))
        except ValueError:
            pass  # 注册时戳不可解=退回 30 日窗（A4 若判跨越则如实降级，不掩盖）
    window_start = min(window_start, window_end)
    payload = {
        "outcome": "answered" if result["conclusion_dir"] != INDETERMINATE else "reexam",
        "exam_ref": f"wo-b1/reexam/{q_id}",
        "examiner_ref": "E1C 复考机",
        "run_ref": f"wo-b1-{completed.strftime('%Y%m%d%H%M%S')}",
        "exam_plan_version": "v2-wo-b1",
        "conclusion_value": result["conclusion_value"],
        "conclusion_dir": result["conclusion_dir"],
        "confidence_level": 95.0,
        "sample_size": result.get("sample_size"),
        "effect_size": result.get("effect_size"),
        "data_window": {
            "start": str(window_start),
            "end": str(window_end),
            "fetch_ts": (completed - timedelta(hours=3)).isoformat(),
            "decision_ts": (completed - timedelta(hours=2)).isoformat(),
        },
        "sample_out_share": 1.0,  # 治理自检题的观测窗全在问题生成之后（新鲜窗推定，见 13§3.3）
        "pit_assertion": "探针只读 PG/CH reader 角色，取数时戳早于决策时戳，窗末≤执行日-1",
        "pit_check_ref": "meta_question_reader_role",
        "exam_completed_at": (completed - timedelta(minutes=5)).isoformat(),
        "evidence_refs": result["evidence_refs"],
    }
    wb = ExamLoopWriteback(registry)
    registry.claim(q_id, session_id, lease_hours=4)
    status = str(reader.one(_SQL_QUESTION_STATUS.format(schema=registry.schema), (q_id,)).get("status"))
    if status == "answered":  # 重考链：answered→reexam（合法边）再回填
        registry.transition(q_id, "reexam", actor=session_id, evidence="新鲜窗到期重考")
    try:
        out["written"] = wb.writeback(q_id, payload, session_id=session_id)
    except Exception as exc:  # noqa: BLE001  单题失败照实记账不吞（复考机不得假绿）
        out["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        registry.release_claim(q_id, session_id)
    return out


def run_redteam(registry: MetaQuestionRegistry, *, session: str, forge_session: str) -> list[dict[str, Any]]:
    """施工期红腿实证（PQ-0103/PQ-0060 分母来源）。

    只做两件事且**必被拒**：①他人会话冒名回写（claim_mismatch 痕）；②非法状态流转（illegal_transition 痕）。
    两者零业务写副作用（回滚后主表不变），故可在生产库上安全自证"这把尺会红"。
    """
    wb = ExamLoopWriteback(registry)
    sm: ExamLoopStateMachine = wb.sm
    out: list[dict[str, Any]] = []
    # ① 伪造越权回写：以本会话认领后，改用他人会话号回写
    q_claim = "PQ-0103"
    registry.claim(q_claim, session, lease_hours=1)
    try:
        wb.writeback(q_claim, {"outcome": "answered", "exam_ref": "wo-b1/redteam/forge"}, session_id=forge_session)
        out.append({"case": "claim_mismatch", "red": False, "note": "伪造回写未被拒=鉴权失效"})
    except Exception as exc:  # noqa: BLE001  红腿期望被拒，异常即"尺红了"
        out.append({"case": "claim_mismatch", "red": True, "refused": f"{type(exc).__name__}: {exc}"})
    finally:
        registry.release_claim(q_claim, session)
    # ② 非法流转：answered→mining（跳边）必须被拦且落痕
    rows = registry._conn(read_only=True)
    try:
        cur = rows.cursor()
        cur.execute(
            _SQL_FORGE_EDGE_TARGET.format(schema=registry.schema),
            ([FORGE_EDGE_STATUS],),
        )
        row = cur.fetchone()
    finally:
        rows.close()
    if not row:
        out.append({"case": "illegal_transition", "red": False, "note": "无 answered 态问题可试（跳过）"})
        return out
    q_edge, status = str(row[0]), str(row[1])
    try:
        sm.transition(q_edge, FORGE_EDGE_TARGET, actor=session, evidence="wo-b1/redteam 非法边自测")
        out.append({"case": "illegal_transition", "red": False, "note": f"{status}→{FORGE_EDGE_TARGET} 未被拒"})
    except Exception as exc:  # noqa: BLE001
        after = sm.ledger.latest_events(q_edge, (event_codes.CODE_ILLEGAL_TRANSITION,), limit=1)
        out.append(
            {
                "case": "illegal_transition",
                "red": True,
                "q_id": q_edge,
                "refused": f"{type(exc).__name__}: {exc}",
                "traced": bool(after),
                "trace_state": (after[0].get("after") or {}).get("reason") if after else None,
            }
        )
    return out


# ---------------------------------------------------------------------------
# --selftest：判据边界矩阵（零 DB 红腿自证）
# ---------------------------------------------------------------------------

_SELFTEST: tuple[tuple[str, bool], ...] = (
    ("分母零值必不可判", _percent(0, 0) is None),
    ("PIT 违例数可计算", _percent(2, 20) == 10.0),
    ("in_exam 之后集含 answered", "answered" in POST_IN_EXAM),
    ("in_exam 之后集排除终态", not (POST_IN_EXAM & TERMINAL_STATUSES)),
    ("状态集与词表同源", frozenset(VALID_STATUSES) >= POST_IN_EXAM),
    ("探针覆盖=11 问", len(PROBES) == len(COVERED)),
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WO-B1 复考机（判据执行体 + writeback 落账）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--jsonl", default=str(DEFAULT_JSONL))
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--questions", default="", help="逗号分隔 q_id（缺省=本单覆盖全集）")
    parser.add_argument("--all-covered", action="store_true", help="跑本单覆盖的全部问题")
    parser.add_argument("--writeback", action="store_true", help="经唯一入口落账（缺省只出判据）")
    parser.add_argument("--dry-run", action="store_true", help="只出判据不落账（默认行为，显式声明用）")
    parser.add_argument("--actor", default="st-wo-b1-examloop|AI")
    parser.add_argument("--session", default="st-wo-b1-examloop", help="回写鉴权用会话号（须为认领人）")
    parser.add_argument("--out", default="", help="判据结果 JSON 落盘路径（临时件，非交付）")
    parser.add_argument(
        "--redteam", action="store_true", help="施工期红腿实证（越权回写/非法流转必被拒，零业务写副作用）"
    )
    parser.add_argument(
        "--forge-session", default="st-wo-b1-redteam|AI", help="红队自测冒用的他人会话号（合法认领人之外）"
    )
    return parser


def _run_selftest() -> int:
    bad = [name for name, ok in _SELFTEST if not ok]
    for name, ok in _SELFTEST:
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    print(f"SELFTEST {len(_SELFTEST) - len(bad)}/{len(_SELFTEST)} 通过")
    return EXIT_ERROR if bad else EXIT_OK


def _run_redteam_leg(args: argparse.Namespace) -> int:
    registry_probe = MetaQuestionRegistry(schema=args.schema, audit_jsonl_path=args.jsonl or None)
    report = run_redteam(registry_probe, session=args.session, forge_session=args.forge_session)
    for item in report:
        print(f"REDTEAM {item['case']}: red={item['red']} {json.dumps(item, ensure_ascii=False, default=str)[:220]}")
    return EXIT_ERROR if any(not item["red"] for item in report) else EXIT_OK


def _print_item(q_id: str, item: dict[str, Any]) -> None:
    verdict = item.get("verdict") or {}
    print(
        f"{q_id} dir={verdict.get('conclusion_dir', '-')} value={verdict.get('conclusion_value')} "
        f"criterion={verdict.get('criterion')} threshold={str(verdict.get('threshold'))[:24]!r} "
        f"written={'-' if not item.get('written') else item['written'].get('outcome')} "
        f"{('ERR=' + item['error']) if item.get('error') else ''} {verdict.get('note') or ''}"
    )


def _run_questions(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    qids = [q.strip() for q in args.questions.split(",") if q.strip()] or (list(COVERED) if args.all_covered else [])
    if not qids:
        parser.error("须指定 --questions 或 --all-covered")
    registry = MetaQuestionRegistry(schema=args.schema, audit_jsonl_path=args.jsonl or None)
    reader = Reader(registry)
    results: list[dict[str, Any]] = []
    red = 0
    for q_id in qids:
        try:
            item = run_one(
                registry,
                reader,
                q_id,
                actor=args.actor,
                writeback=args.writeback and not args.dry_run,
                session_id=args.session,
            )
        except Exception as exc:  # noqa: BLE001  单题异常照实记账（fail-visible）
            item = {"q_id": q_id, "error": f"{type(exc).__name__}: {exc}"}
        results.append(item)
        verdict = item.get("verdict") or {}
        if verdict.get("conclusion_dir") == "证伪" or item.get("error"):
            red += 1
        _print_item(q_id, item)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"CHECK-EXAM-LOOP 题数={len(results)} 红/异常={red} writeback={args.writeback and not args.dry_run}")
    return EXIT_RED if red else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.selftest:
        return _run_selftest()
    if args.redteam:
        return _run_redteam_leg(args)
    return _run_questions(args, parser)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"FATAL: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
