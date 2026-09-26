#!/usr/bin/env python3
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1.2 六查 / §3 复考周期 / §7 P1-P7 提案（未过评审=台账降级实现）
# [MODULE] scripts.governance.meta_question.wo_b1_examloop.run_exam_loop
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] src/zephyr/governance/meta_question/meta_question_registry.py（冻结件，只 import 不改：连接注入/审计双轨真源）; src/zephyr/governance/meta_question/exam_loop/*（本簇四件：event_codes/exam_plan/reexam_scheduler/ledger）
# [CONSUMERS] Owner 查账; 283 问战役复考排产（WO-B1 施工件运行入口）; tests/governance/meta_question/（判据边界矩阵与单测同源）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 四子命令单入口：--selftest（零 DB 判据边界矩阵，红腿自证）/--status（只读实况）/--reconcile（到期逾期落账）/--upgrade-plan（exam_plan 结构化补登，逐 q_id 乐观锁+审计留痕）；
#              全程禁在本件出现 read_only=False 字面量：写通道一律经 registry 注入（DEPGRAPH-WRITE-PATH 白名单收口在上游，见 exam_loop/PENDING_ENUM_PATCH.md）;
#              --upgrade-plan 只补登"可由题面/考尺派生"的判据字段且逐字段带 source，禁伪造无源阈值；power_min=0.80 源=PQ-0098 题面，out_of_sample_share_min=1/3 源=PQ-0055 题面，min_confidence=95 源=E1C 考尺 α=0.05 补登并标 post_hoc_amendment（待裁项 T-1）；
#              题面原文零改写：threshold/criterion/method 原值保留，只追加机解投影与 plan_version；
#              幂等：已带 plan_version 且机解一致者跳过（重跑零写）；
#              终态与退役问不进复考台账（13§4.3），对账器禁 sleep-loop/cron（宪法§9.3），本件只按需触发
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1.2/§3（改判据先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=通过；EXIT 1=判据破线（逾期存在/降级未闭合，如实报）；EXIT 2=异常（PG 不可达/参数非法/矩阵自测不符，fail-closed 不出结论）
# [TESTS] 手动红蓝两腿：--selftest 边界矩阵（含 19/20/21 日新鲜窗与功效 0.79/0.80/0.81）；--status 只读实况；--upgrade-plan --dry-run 零写自证
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: WO-B1 考试循环簇按需 CLI（复考调度+考卷补登），无常驻进程
"""run_exam_loop — 考试循环簇运行入口（复考对账 + 预注册考卷结构化补登，WO-B1）。

用法::

    python scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py --selftest
    python scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py --status
    python scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py --reconcile --actor st-wo-b1-examloop|AI
    python scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py --upgrade-plan --qids PQ-0051,PQ-0055 --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

_BOOT_ROOT = Path(__file__).resolve().parents[4]
_SRC = _BOOT_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
from zephyr.governance.meta_question.exam_loop import event_codes, exam_plan  # noqa: E402
from zephyr.governance.meta_question.exam_loop.ledger import ExamLoopLedger  # noqa: E402
from zephyr.governance.meta_question.exam_loop.reexam_scheduler import (  # noqa: E402
    ReexamScheduler,
    due_state,
)
from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  仓根唯一真源（原为本地重定义，SSOT-REDEFINITION 对症）
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

DEFAULT_SCHEMA = "meta_question"
DEFAULT_JSONL = REPO_ROOT / ".runtime" / "chain_piling" / "meta_question_audit.jsonl"
AUDIT_TABLE_SQL = "{s}.meta_question_audit"

EXIT_OK = 0
EXIT_BREACH = 1
EXIT_ERROR = 2

#: 判据补登册（每项必带题面/考尺出处；无源不登记——禁伪造预注册）
PLAN_AMENDMENTS: tuple[tuple[str, str, str], ...] = (
    ("power_min", "0.80", "PQ-0098 题面 threshold『功效≥80%』（docs/.../snapshots/question_batch_w6.yaml）"),
    ("out_of_sample_share_min", "0.3333333", "PQ-0055 题面『样本外份额≥1/3』"),
    ("min_confidence", "95", "E1C 考尺 α=0.05 换算，题面未预锁→post_hoc_amendment（WO-B1 待裁项 T-1）"),
)

__manifest__ = """
args: ["--selftest"]
description: 'WO-B1 考试循环运行入口：新鲜窗到期/逾期对账落账 + 预注册考卷结构化补登（13§1.2/§3）。'
dimensions:
- D3
priority: P2
timeout_seconds: 300
warn_only: false
"""


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{s}/{schema}=registry 注入的 schema 名、
# {table}=AUDIT_TABLE_SQL.format(s=...) 的成品表名、{match}=event_codes.sql_event_match() 运行期
# 片段、{marks}=%s 占位串——一律由调用点 .format() 传入，禁把 schema/事件码字面量写进常量。
# _SQL_PLAN_UPGRADE_UPDATE 是写面语句（仅 cmd_upgrade_plan 非干跑分支执行），本件零 DDL。
_SQL_AUDIT_CHECK_CONSTRAINTS = (
    "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = %s::regclass AND contype = 'c'"
)
_SQL_AUDIT_EVENT_HITS = "SELECT count(*) FROM {table} WHERE {match}"
_SQL_AUDIT_DUAL_TIMESTAMP = (
    "SELECT count(*), count(*) FILTER (WHERE (after->>'exam_completed_at') IS NOT NULL "
    "AND (after->>'backfilled_at') IS NOT NULL) FROM {table} WHERE what = 'exam_writeback'"
)
_SQL_QUESTION_LIVE_COUNT = (
    "SELECT count(*) FROM {schema}.meta_question WHERE status IN ('answered','reexam','suspended','in_exam')"
)
_SQL_EXAM_RESULT_COUNT = "SELECT count(*) FROM {schema}.meta_question_exam_result"
_SQL_PLAN_ROWS = "SELECT q_id, exam_plan, status, version FROM {s}.meta_question WHERE q_id IN ({marks})"
_SQL_PLAN_UPGRADE_UPDATE = (
    "UPDATE {s}.meta_question SET exam_plan=%s::jsonb, version=version+1, updated_at=%s WHERE q_id=%s AND version=%s"
)


# ---------------------------------------------------------------------------
# 连接（写通道经 registry 注入，本件零 read_only=False 字面量）
# ---------------------------------------------------------------------------


# NO-BARE-SQL：本 CLI 取数/写数 SQL 集中于此（§5.160.2）。
# 表限定符 {s}/{tbl} 一律由调用方注入 registry.schema（禁写死库名）；
# {match}/{marks} 为运行期变长谓词占位（其片段构造真源在 event_codes / 参数化 %s，不在此拼值）。
_SQL_CONSTRAINT_PROBE = (
    "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = %s::regclass AND contype = 'c'"
)
_SQL_EVENT_COUNT = "SELECT count(*) FROM {tbl} WHERE {match}"
_SQL_DUAL_STAMP_COUNT = (
    "SELECT count(*), count(*) FILTER (WHERE (after->>'exam_completed_at') IS NOT NULL "
    "AND (after->>'backfilled_at') IS NOT NULL) FROM {tbl} WHERE what = 'exam_writeback'"
)
_SQL_LIVE_QUESTION_COUNT = (
    "SELECT count(*) FROM {s}.meta_question WHERE status IN ('answered','reexam','suspended','in_exam')"
)
_SQL_RESULT_COUNT = "SELECT count(*) FROM {s}.meta_question_exam_result"
_SQL_PLAN_ROWS = "SELECT q_id, exam_plan, status, version FROM {s}.meta_question WHERE q_id IN ({marks})"
_SQL_PLAN_UPGRADE_UPDATE = (
    "UPDATE {s}.meta_question SET exam_plan=%s::jsonb, version=version+1, updated_at=%s WHERE q_id=%s AND version=%s"
)


def build_registry(schema: str, jsonl: str | None) -> MetaQuestionRegistry:
    return MetaQuestionRegistry(
        schema=schema,
        audit_jsonl_path=jsonl if jsonl and jsonl.lower() != "none" else None,
    )


# ---------------------------------------------------------------------------
# --selftest：判据边界矩阵（零 DB，红腿自证"尺能红"）
# ---------------------------------------------------------------------------

_TODAY = date(2026, 9, 24)
_SELFTEST_CASES: tuple[tuple[str, bool], ...] = (
    ("新鲜窗 19 日未到期", due_state("monthly", "2026-09-05T00:00:00+00:00", today=_TODAY)["due"] is False),
    ("新鲜窗 20 日到期", due_state("monthly", "2026-09-04T00:00:00+00:00", today=_TODAY)["due"] is True),
    ("新鲜窗 21 日逾期", due_state("monthly", "2026-09-03T00:00:00+00:00", today=_TODAY)["overdue"] is True),
    ("跨自然月即逾期", due_state("monthly", "2026-08-05T00:00:00+00:00", today=_TODAY)["overdue"] is True),
    ("静态档不适用", due_state("static", None, today=_TODAY)["applicable"] is False),
    ("从未考=欠账", due_state("daily", None, today=_TODAY)["overdue"] is True),
    ("日频窗内不欠", due_state("daily", "2026-09-23T00:00:00+00:00", today=_TODAY)["overdue"] is False),
    (
        "功效 0.79 必延期",
        exam_plan.assess_power({"power_min": 0.8, "sample_size": 150, "effect_size": 0.20}).action == "defer",
    ),
    (
        "功效 0.80 边界达标",
        exam_plan.assess_power({"power_min": 0.8, "sample_size": 154, "effect_size": 0.20}).action == "pass",
    ),
    ("阈值文本机解 ≥95%", exam_plan.parse_threshold_clauses("≥95%（逾期挂起≤5%）")[1]["value"] == 95.0),
    (
        "窗口跨越生成时戳必违规",
        any(
            v.code == "window_straddles_generation"
            for v in exam_plan.check_time_layering(
                {"start": "2025-01-01", "end": "2026-01-01"},
                generated_at="2025-06-01T00:00:00+00:00",
                execution_day=_TODAY,
            )
        ),
    ),
    (
        "窗末=执行日必违规",
        any(
            v.code == "window_end_not_before_close"
            for v in exam_plan.check_time_layering(
                {"start": "2026-09-01", "end": "2026-09-24"}, generated_at=None, execution_day=_TODAY
            )
        ),
    ),
    ("份额不可核不得判通过", exam_plan.out_of_sample_share({"start": "2024-01-01", "end": "2025-01-01"})[0] is None),
    (
        "扩展码未落地走过渡载体",
        event_codes.resolve(event_codes.CODE_CLAIM_MISMATCH).what == event_codes.base_what_for_pending(),
    ),
    ("已落地码直写 what", event_codes.resolve("exam_writeback").event_code is None),
)


def cmd_selftest() -> int:
    print("SELFTEST 考试循环判据边界矩阵（零 DB）")
    failed = [name for name, ok in _SELFTEST_CASES if not ok]
    for name, ok in _SELFTEST_CASES:
        print(f"  {'PASS' if ok else 'FAIL'} {name}")
    print(f"SELFTEST {len(_SELFTEST_CASES) - len(failed)}/{len(_SELFTEST_CASES)} 通过")
    return EXIT_ERROR if failed else EXIT_OK


# ---------------------------------------------------------------------------
# --status：扩展码落地态 + 双时戳落账实况（只读）
# ---------------------------------------------------------------------------


def cmd_status(registry: MetaQuestionRegistry) -> int:
    codes = sorted(event_codes.EXTENSION_CODES)
    landed: dict[str, bool] = {}
    try:
        conn = registry._conn(read_only=True)
        cur = conn.cursor()
        cur.execute(_SQL_CONSTRAINT_PROBE, (f"{registry.schema}.meta_question_audit",))
        definitions = " ".join(str(row[1]) for row in cur.fetchall())
        for code in codes:
            landed[code] = f"'{code}'" in definitions or f"::{code}::text" in definitions
            event_codes.mark_landed(code, landed[code])
        match = event_codes.sql_event_match()
        for code in codes:
            cur.execute(
                _SQL_EVENT_COUNT.format(tbl=AUDIT_TABLE_SQL.format(s=registry.schema), match=match),
                event_codes.match_params(code),
            )
            landed[f"{code}::events"] = int(cur.fetchone()[0])
        cur.execute(_SQL_DUAL_STAMP_COUNT.format(tbl=AUDIT_TABLE_SQL.format(s=registry.schema)))
        total_dual = cur.fetchone()
        cur.execute(_SQL_LIVE_QUESTION_COUNT.format(s=registry.schema))
        live = int(cur.fetchone()[0])
        cur.execute(_SQL_RESULT_COUNT.format(s=registry.schema))
        results = int(cur.fetchone()[0])
        conn.close()
    except Exception as exc:  # noqa: BLE001  只读态异常=EXIT 2（fail-closed）
        print(f"STATUS FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(f"STATUS schema={registry.schema} 活问题={live} exam_result={results}")
    print(f"exam_writeback 事件={total_dual[0]} 双时戳齐备={total_dual[1]}")
    for code in codes:
        print(f"  {code}: landed={landed[code]} events={landed[f'{code}::events']}")
    return EXIT_OK


# ---------------------------------------------------------------------------
# --reconcile：新鲜窗到期/逾期落账
# ---------------------------------------------------------------------------


def cmd_reconcile(registry: MetaQuestionRegistry, *, actor: str, book: bool, limit: int) -> int:
    scheduler = ReexamScheduler(registry, ledger=ExamLoopLedger(registry))
    report = scheduler.reconcile(actor=actor, book=book, limit=limit)
    print(
        f"RECONCILE as_of={report['as_of']} scanned={report['scanned']} due={report['due_count']} "
        f"overdue={report['overdue_count']} booked={report['booked']} "
        f"execution_rate={report['execution_rate']}"
    )
    for item in report["overdue"][:20]:
        print(
            f"  OVERDUE {item['q_id']} freq={item['frequency']} last_exam={item['last_exam']} "
            f"days={item['days_since']} basis={item['basis']}"
        )
    if len(report["overdue"]) > 20:
        print(f"  …其余 {len(report['overdue']) - 20} 条略（总量照报）")
    return EXIT_BREACH if report["overdue_count"] else EXIT_OK


# ---------------------------------------------------------------------------
# --upgrade-plan：exam_plan 结构化补登（题面零改写，逐字段带源）
# ---------------------------------------------------------------------------


def _plan_upgrade(raw: dict[str, object]) -> dict[str, object]:
    """机解投影 + 缺项补登（带 source），返回 None 表示无需改写。"""
    plan = exam_plan.structure_plan(dict(raw or {}), plan_version="v2-wo-b1")
    sources = dict(plan.get("amendment_sources") or {})
    for key, value, source in PLAN_AMENDMENTS:
        if plan.get(key) in (None, ""):
            plan[key] = float(value)
            sources[key] = source
    plan["post_hoc_amendment"] = bool(sources)
    plan["amendment_sources"] = sources
    plan["degraded"] = [k for k in exam_plan.STRUCTURED_KEYS if plan.get(k) in (None, "")]
    return plan


def _upgrade_one_row(ctx: dict, q_id: str, raw_plan: Any, status: Any, version: Any) -> bool:
    """处理单行 exam_plan 结构化补登；返回 True=完成一次升级写（计入 changed）。"""
    cur, conn, ledger = ctx["cur"], ctx["conn"], ctx["ledger"]
    schema, dry_run = ctx["schema"], ctx["dry_run"]
    raw = raw_plan if isinstance(raw_plan, dict) else json.loads(raw_plan or "{}")
    upgraded = _plan_upgrade(raw)
    added = sorted(set(upgraded) - set(raw))
    drifted = any(raw.get(k) is not None and upgraded.get(k) != raw.get(k) for k in raw)
    if not added and not drifted:
        print(f"  SKIP {q_id}（已结构化且键集一致，幂等重跑零写）")
        return False
    if drifted:
        print(f"  DRIFT {q_id} 机解投影与原键值不一致（以题面原文为准，仅补空不覆写）")
        upgraded = {**upgraded, **{k: v for k, v in raw.items() if v not in (None, "")}}
    print(
        f"  {'DRY ' if dry_run else ''}PLAN {q_id} status={status} "
        f"criterion={upgraded.get('criterion')!r} threshold={upgraded.get('threshold')!r} "
        f"补登={sorted(upgraded.get('amendment_sources') or {})} degraded={upgraded.get('degraded')}"
    )
    if dry_run:
        return False
    cur.execute(
        _SQL_PLAN_UPGRADE_UPDATE.format(s=schema),
        (json.dumps(upgraded, ensure_ascii=False, default=str), now_utc(), q_id, int(version)),
    )
    if cur.rowcount != 1:
        conn.rollback()
        print(f"  CONFLICT {q_id} 版本已被他人推进，重读重放再来")
        return False
    ledger.write_event(
        cur,
        "update",
        q_id=q_id,
        actor="wo-b1-examloop",
        before={"exam_plan_keys": sorted(raw)},
        after={"exam_plan_keys": sorted(upgraded), "plan_version": upgraded.get("plan_version")},
        evidence="exam_plan_structured_upgrade(PQ-0098)",
        diff=[{"field": "exam_plan", "old": sorted(raw), "new": sorted(upgraded)}],
    )
    return True


def cmd_upgrade_plan(registry: MetaQuestionRegistry, qids: list[str], *, dry_run: bool) -> int:
    """逐 q_id 结构化补登（乐观锁 + update 审计；题面原文与机解不一致即报 drift）。"""
    if not qids:
        print("UPGRADE-PRECHECK qids 为空，拒绝执行（禁全表盲改）")
        return EXIT_ERROR
    ledger = ExamLoopLedger(registry)
    marks = ", ".join(["%s"] * len(qids))
    sql = _SQL_PLAN_ROWS.format(s=registry.schema, marks=marks)
    conn = registry._conn(read_only=dry_run)  # 干跑=只读；真跑=写通道（角色由 registry 注入，禁本件写死）
    changed = 0
    found: list[str] = []
    try:
        cur = conn.cursor()
        cur.execute(sql.format(s=registry.schema), tuple(qids))
        rows = cur.fetchall()
        ctx = {"cur": cur, "conn": conn, "ledger": ledger, "schema": registry.schema, "dry_run": dry_run}
        for q_id, raw_plan, status, version in rows:
            found.append(str(q_id))
            if _upgrade_one_row(ctx, q_id, raw_plan, status, version):
                changed += 1
        if not dry_run:
            conn.commit()
    except Exception as exc:  # noqa: BLE001
        conn.rollback()
        print(f"UPGRADE FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR
    finally:
        conn.close()
    missing = [q for q in qids if q not in found]
    print(f"UPGRADE-PLAN changed={changed} dry_run={dry_run} 请求={len(qids)} 未命中={missing}")
    return EXIT_OK


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WO-B1 考试循环运行入口（复考对账/考卷结构化补登）")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--jsonl", default=str(DEFAULT_JSONL), help="审计 JSONL 双轨路径（none=只写 PG）")
    parser.add_argument("--selftest", action="store_true", help="零 DB 判据边界矩阵（红腿自证）")
    parser.add_argument("--status", action="store_true", help="只读：扩展码落地态与双时戳落账实况")
    parser.add_argument("--reconcile", action="store_true", help="新鲜窗到期/逾期对账（默认落账）")
    parser.add_argument("--no-book", action="store_true", help="对账只出清单不落账")
    parser.add_argument("--limit", type=int, default=0, help="对账落账条数上限（0=不限）")
    parser.add_argument("--actor", default="st-wo-b1-examloop|AI")
    parser.add_argument("--upgrade-plan", action="store_true", help="exam_plan 结构化补登")
    parser.add_argument("--qids", default="", help="逗号分隔 q_id 清单（--upgrade-plan 必填，禁全表盲改）")
    parser.add_argument("--dry-run", action="store_true", help="补登只报不改")
    args = parser.parse_args(argv)

    if args.selftest:
        return cmd_selftest()
    registry = build_registry(args.schema, args.jsonl)
    if args.status:
        return cmd_status(registry)
    if args.reconcile:
        return cmd_reconcile(registry, actor=args.actor, book=not args.no_book, limit=args.limit)
    if args.upgrade_plan:
        qids = [q.strip() for q in args.qids.split(",") if q.strip()]
        return cmd_upgrade_plan(registry, qids, dry_run=args.dry_run)
    parser.error("须指定 --selftest/--status/--reconcile/--upgrade-plan 之一")
    return EXIT_ERROR


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001  fail-closed：未预期异常=EXIT 2
        print(f"FATAL: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
