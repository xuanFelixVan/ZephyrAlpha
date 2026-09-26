#!/usr/bin/env python3
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §5.1 限流三参数+§7.1 校验顺序+§7.3 审计事件
# [MODULE] scripts.governance.meta_question.wo001_003.intake_batch
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.meta_question.meta_question_registry（MetaQuestionRegistry=登记唯一写入口+五要素机检真检判定复用，禁在本件复刻判据）;
#                zephyr.governance.depgraph_schema（限流读数=PG 审计 register 事件只读聚合）; PyYAML
# [CONSUMERS] PQ-0099 持续入题面（WO-003②：破 answered 单态 100% 结构异常的输入侧机制）;
#             未答看板《12§1 入板对象》registered 态供给方; 定桩/复考各批次作业（候选批 YAML 的消费端）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 默认 dry-run，--apply 才写（写=经 register() 唯一正门，禁直连 SQL 插主表）；
#              限流三参数取裁定#402 定案值且只计 registered 动作（单批 12／会话日 40／全库日 120，
#              读数=当日 PG 审计 register 事件聚合，可复算）；
#              时间分层铁律（[纪要§8.2]）：批 YAML generated_date 必须早于今日 UTC，
#              同日产出同日入库=自循环，--allow-same-day 不是逃生旗（本件无该参数）；
#              幂等：高相似查重由 registry 短路（subcode=dup_high_similarity）计 skip_dup 不计失败；
#              五要素判定复用 registry._check_five_elements（本件不自建判据，防 extract 级克隆）；
#              零越界：只产 registered 态，禁 transition/禁考试回写（那是《13 考试回填闭环》/B1 writeback 的地盘）；
#              批 YAML 契约=W6 批次快照同构（batch_id/session/generated_date/count/questions[]），禁另立格式
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md §5/§7（改限流或校验顺序先改设计稿+裁定）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=批内全部有定论（入库/跳过/按判据拒收）且零异常；EXIT 1=存在拒收或限流截断（清单逐条打印，已入库部分不回滚——一问一事务是 registry 契约）；EXIT 2=异常（批文件缺失/PG 不可读/registry 不可导入，fail-closed 零写）
# [TESTS] tests/governance/meta_question/wo001_003/test_intake_batch.py（tmp 批 YAML+SQLite mock 注入口：限流截断/幂等重跑/同日批必拒/状态带反馈数字可复算）
# [TTL] permanent
"""intake_batch — meta_question 持续入题驱动器（WO-003②，10§5.1/§7）。

缺口本质（PQ-0099）：283 问一次性应考后全表钉死 ``answered=100%``，双 regime 皆破带；
健康带要回正，缺的不是"把 100% 洗进带内"的判据放宽，而是**新问题按批持续进门**的输入侧机制。
本件即该机制的执行体：候选批 YAML →（契约预检→限流→查重→五要素真检）→ ``register()`` 唯一正门。

批次来源（真源边界，本件不代建）：《11 模板生成器》按取值域展开的候选、挖矿会话产出的
新问、复考族回灌——统统落成 W6 同构批 YAML 再进本件（禁在本件里造第二套问题生成器）。

用法::

    python scripts/governance/meta_question/wo001_003/intake_batch.py --batch <批.yaml>              # dry-run 预检+投影
    python scripts/governance/meta_question/wo001_003/intake_batch.py --batch <批.yaml> --apply      # 真入库（过正门）
    python ... --session sid-x --report out.yaml                                                   # 留痕报告
"""

from __future__ import annotations

import argparse
import inspect
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Final

import yaml

_BOOT_ROOT = Path(__file__).resolve().parents[4]
if str(_BOOT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_BOOT_ROOT / "src"))

# 限流三参数：真源=裁定#402 定案值（10§5.1 建议值经裁定批转正），只计 registered 动作
BATCH_CAP: Final[int] = 12
SESSION_DAY_CAP: Final[int] = 40
GLOBAL_DAY_CAP: Final[int] = 120

EXIT_DONE: Final = 0
EXIT_REJECTED: Final = 1
EXIT_ERROR: Final = 2

REQUIRED_BATCH_KEYS: Final[tuple[str, ...]] = ("batch_id", "session", "generated_date", "questions")
A_LEVEL_FIELDS: Final[tuple[str, ...]] = (
    "title",
    "layer",
    "data_sources",
    "exam_plan",
    "consumers",
    "frequency",
    "pit_proof",
    "net_zero_note",
)


# NO-BARE-SQL：SQL 集中于此（§5.160.2）；{schema} 由调用方注入，禁写死日期。
_SQL_REGISTER_BY_ACTOR = (
    "SELECT actor, COUNT(*) FROM {schema}.meta_question_audit "
    "WHERE what = 'register' AND (created_at AT TIME ZONE 'UTC')::date = %s GROUP BY actor"
)
_SQL_STATUS_DIST = "SELECT status, COUNT(*) FROM {schema}.meta_question GROUP BY status"


class BatchError(RuntimeError):
    """批文件级不可执行错误（结构不合/日期铁律违例）——零写 fail-closed。"""


# ---------------------------------------------------------------------------
# 批读取与契约预检
# ---------------------------------------------------------------------------


def load_batch(path: Path, *, today: date) -> dict[str, Any]:
    """读批 YAML 并核契约（W6 同构）+ 时间分层铁律（今日输出→明日输入）。"""
    if not path.exists():
        raise BatchError("batch_file_missing")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise BatchError("batch_not_mapping")
    missing = [k for k in REQUIRED_BATCH_KEYS if not doc.get(k)]
    if missing:
        raise BatchError(f"batch_field_missing: {','.join(missing)}")
    generated = _as_date(doc["generated_date"])
    if generated >= today:
        raise BatchError(
            f"time_layer_violation: generated_date={generated.isoformat()} 不早于今日 {today.isoformat()}"
            "（[纪要§8.2] 同一时戳禁循环：批产出与入库必须隔日）"
        )
    questions = doc["questions"]
    if not isinstance(questions, list) or not questions:
        raise BatchError("batch_questions_empty")
    declared = doc.get("count")
    if declared is not None and int(declared) != len(questions):
        raise BatchError(f"batch_count_drift: 声明 {declared} ≠ 实际 {len(questions)}")
    return doc


def _as_date(raw: Any) -> date:
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    return date.fromisoformat(str(raw).strip()[:10])


def prescreen(question: dict[str, Any], checker: Any) -> tuple[str, str]:
    """单问预检：返回 (判定, 码/降级要素串)。

    判定 ``ok``=A 级+五要素真检全过（预计入库且无降级痕）；``degraded``=能入库但五要素真检
    有未成立项（返回未成立清单，供决定改题面还是改 W4 册）；``reject``=A 级/枚举不过。
    """
    try:
        degraded = checker(question)
    except Exception as exc:  # noqa: BLE001  registry 契约异常族，取 subcode 机读码
        code = getattr(exc, "subcode", None) or str(exc)
        return "reject", str(code)
    if degraded:
        return "degraded", ",".join(degraded)
    return "ok", ""


# ---------------------------------------------------------------------------
# 限流读数（PG 审计 register 事件只读聚合，可复算）
# ---------------------------------------------------------------------------


def day_register_counts(schema: str = "meta_question") -> tuple[dict[str, int], str | None]:
    """今日（UTC）已 registered 动作计数：全库 + 按 actor。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    sql = _SQL_REGISTER_BY_ACTOR.format(schema=schema)  # noqa: bare-sql 表限定符经 schema 变量运行期注入，模板本身已是模块常量
    try:
        conn = get_depgraph_pg_connection(read_only=True)
    except Exception as exc:  # noqa: BLE001
        return {}, f"pg_connect_failed: {exc}"
    try:
        cur = conn.cursor()
        cur.execute(sql, (_today(),))
        per_actor = {str(actor): int(count) for actor, count in cur.fetchall()}
        return {"__total__": sum(per_actor.values()), **per_actor}, None
    except Exception as exc:  # noqa: BLE001
        return {}, f"pg_query_failed: {exc}"
    finally:
        conn.close()


def _today() -> date:
    from zephyr.shared.utils.time_utils import now_utc  # RULE-SCHEMA-TZ：禁裸 datetime.now

    return now_utc().date()


def session_id_of(actor: str) -> str:
    """actor 口径=session|角色（20§2.1 who 字段），限流按 session 段计。"""
    return str(actor).split("|", 1)[0].strip()


# ---------------------------------------------------------------------------
# 状态带反馈（把 WO-003① 与 ② 接起来：入题后健康带离带内还差几问）
# ---------------------------------------------------------------------------


def band_projection(status_counts: dict[str, int], added: int) -> dict[str, Any]:
    """入库 added 条 registered 后的 answered 占比投影（campaign 带 95／default 带 70／单态帽 80）。"""
    counts = dict(status_counts)
    counts["registered"] = counts.get("registered", 0) + added
    total = sum(counts.values())
    if total <= 0:
        return {"total": 0}
    answered = counts.get("answered", 0)
    max_status, max_count = max(counts.items(), key=lambda kv: kv[1])
    return {
        "total_after": total,
        "answered_pct": round(100.0 * answered / total, 2),
        "max_status": max_status,
        "max_status_pct": round(100.0 * max_count / total, 2),
        "in_campaign_band": bool(30.0 <= 100.0 * answered / total <= 95.0 and max_count / total <= 0.80),
        "in_default_band": bool(30.0 <= 100.0 * answered / total <= 70.0 and max_count / total <= 0.80),
        "min_added_for_cap80": _min_added_for_cap(status_counts),
    }


def _min_added_for_cap(counts: dict[str, int], cap: float = 0.80) -> int:
    """把最大单态压回帽内所需的最小入库数（机械可解不等式，禁口算）。"""
    total = sum(counts.values())
    top = max(counts.values()) if counts else 0
    if total <= 0 or top / total <= cap:
        return 0
    need = 0
    while need < 100000:
        if top / (total + need) <= cap:
            return need
        need += 1
    return -1


def current_status_counts(schema: str = "meta_question") -> tuple[dict[str, int], str | None]:
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    try:
        conn = get_depgraph_pg_connection(read_only=True)
        cur = conn.cursor()
        cur.execute(_SQL_STATUS_DIST.format(schema=schema))
        counts = {str(status): int(count) for status, count in cur.fetchall()}
        return counts, None
    except Exception as exc:  # noqa: BLE001
        return {}, f"pg_status_scan_failed: {exc}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 驱动
# ---------------------------------------------------------------------------


def _five_element_checker(registry: Any) -> Any:
    """复用 registry 的五要素真检（签名兼容未打补丁的现网版：有 register 形参才下传册）。"""
    func = type(registry)._check_five_elements
    accepts_register = "register" in inspect.signature(func).parameters

    def check(question: dict[str, Any]) -> list[str]:
        register = registry._source_line_register() if hasattr(registry, "_source_line_register") else None
        if accepts_register and register is not None:
            return func(question, register=register)
        return func(question)

    return check


def _apply_rate_limits(caps: dict[str, Any], session: str) -> None:
    """--apply 时的限流读数回填（读数不可得=禁盲写，fail-closed 抛 BatchError）。"""
    today_counts, error = day_register_counts()
    if error:
        raise BatchError(f"rate_limit_read_failed: {error}（限流读数不可得=禁盲写）")
    used_session = sum(c for a, c in today_counts.items() if a != "__total__" and session_id_of(a) == session)
    caps["session_day_used"] = used_session
    caps["global_day_used"] = today_counts.get("__total__", 0)
    caps["session_day_remaining"] = max(0, SESSION_DAY_CAP - used_session)
    caps["global_day_remaining"] = max(0, GLOBAL_DAY_CAP - caps["global_day_used"])


def _outcome_entry(index: int, question: dict[str, Any], action: str, code: Any) -> dict[str, Any]:
    """单问 outcome 行（五个分支共用同一键序：n/title/action/code）。"""
    return {"n": index, "title": str(question.get("title") or "")[:60], "action": action, "code": code}


def _process_questions(
    doc: dict[str, Any],
    *,
    checker: Any,
    registry: Any,
    actor: str,
    apply: bool,
    caps: dict[str, Any],
) -> tuple[Counter, list[dict[str, Any]]]:
    """逐问预检→限流→（可选）正门入库；返回 (counts, outcomes)。"""
    counts: Counter[str] = Counter()
    outcomes: list[dict[str, Any]] = []
    # 预算=三上限取最小（只取 *_remaining*，禁把"已用量=0"当预算——2026-09-24 本班实测红腿抓出）
    budget = (
        caps["batch"] if not apply else min(caps["batch"], caps["session_day_remaining"], caps["global_day_remaining"])
    )
    for index, question in enumerate(doc["questions"], start=1):
        verdict, code = prescreen(dict(question or {}), checker)
        if verdict == "reject":
            counts["reject"] += 1
            outcomes.append(_outcome_entry(index, question, "reject", code))
            continue
        if apply and budget <= 0:
            counts["rate_limited"] += 1
            outcomes.append(_outcome_entry(index, question, "rate_limited", "batch_or_day_cap"))
            continue
        if not apply:
            counts[verdict] += 1
            outcomes.append(_outcome_entry(index, question, "dry_run_" + verdict, code))
            continue
        try:
            q_id = registry.register(dict(question), actor=actor)
        except Exception as exc:  # noqa: BLE001  registry 契约异常族（含 dup_high_similarity）
            sub = str(getattr(exc, "subcode", "") or exc)
            bucket = "skip_dup" if "dup_high_similarity" in sub else "reject"
            counts[bucket] += 1
            outcomes.append(_outcome_entry(index, question, bucket, sub))
            continue
        budget -= 1
        counts["registered"] += 1
        outcomes.append(_outcome_entry(index, question, "registered", q_id))
    return counts, outcomes


def run_batch(
    doc: dict[str, Any],
    *,
    apply: bool,
    registry: Any,
    max_per_batch: int = BATCH_CAP,
) -> dict[str, Any]:
    """执行一批：预检→限流→（可选）正门入库；返回机读报告（不含任何绕过路径）。"""
    session = str(doc["session"])
    actor = f"{session}|AI"
    checker = _five_element_checker(registry)
    caps = {"batch": min(max_per_batch, BATCH_CAP)}
    if apply:
        _apply_rate_limits(caps, session)
    counts, outcomes = _process_questions(doc, checker=checker, registry=registry, actor=actor, apply=apply, caps=caps)
    return {
        "batch_id": doc.get("batch_id"),
        "session": session,
        "mode": "apply" if apply else "dry_run",
        "caps": caps,
        "counts": dict(counts),
        "outcomes": outcomes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", required=True, help="候选批 YAML（W6 批次快照同构）")
    parser.add_argument("--apply", action="store_true", help="真入库（缺省 dry-run）")
    parser.add_argument("--schema", default="meta_question", help="PG schema（默认 meta_question）")
    parser.add_argument("--audit-jsonl", default=None, help="审计双轨 JSONL 路径（--apply 必填，禁单轨写）")
    parser.add_argument("--report", default=None, help="报告落盘路径（禁写生产路径，建议 .runtime/tmp 下）")
    args = parser.parse_args(argv)

    try:
        doc = load_batch(Path(args.batch), today=_today())
    except BatchError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return EXIT_ERROR

    try:
        from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry

        if args.apply and not args.audit_jsonl:
            print("[ERROR] --apply 必须带 --audit-jsonl（20§2.2 双轨：单轨写 PG 违则）", file=sys.stderr)
            return EXIT_ERROR
        registry = MetaQuestionRegistry(
            schema=args.schema,
            audit_jsonl_path=Path(args.audit_jsonl) if args.audit_jsonl else None,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] registry 不可用（fail-closed 零写）：{exc}", file=sys.stderr)
        return EXIT_ERROR

    try:
        report = run_batch(doc, apply=args.apply, registry=registry)
    except BatchError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return EXIT_ERROR

    counts, error = current_status_counts(args.schema)
    if error:
        print(f"[WARN] 状态带投影跳过：{error}")
    else:
        report["band_projection"] = {
            "now": band_projection(counts, 0),
            "after_this_batch": band_projection(counts, report["counts"].get("registered", 0)),
        }

    print(yaml.safe_dump(report, allow_unicode=True, sort_keys=False))
    if args.report:
        target = Path(args.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"[REPORT] {target}")
    bad = report["counts"].get("reject", 0) + report["counts"].get("rate_limited", 0)
    if bad:
        print(
            f"批内有拒收/截断（reject={report['counts'].get('reject', 0)} "
            f"rate_limited={report['counts'].get('rate_limited', 0)}）"
        )
        return EXIT_REJECTED
    return EXIT_DONE


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
