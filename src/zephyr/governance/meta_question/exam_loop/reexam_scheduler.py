# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §3 复考周期（§3.1 窗口与逾期判定 / §3.2 双通道禁 sleep-loop / §3.3 时间分层）
# [MODULE] zephyr.governance.meta_question.exam_loop.reexam_scheduler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.yaml_utils (load_vocabulary_values：频度枚举与窗册同源动态加载); zephyr.shared.utils.time_utils (now_utc); zephyr.governance.meta_question.meta_question_registry (连接注入口径复用); .ledger; .exam_lifecycle (descendants_of 状态集机算，禁字面量枚举)
# [CONSUMERS] scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py（--reconcile 产到期/逾期清单）; .probes（PQ-0054/0108 判据读取）; tests/governance/meta_question/test_exam_loop_scheduler.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 频率→窗口语义唯一真源=config/examloop_reexam_window_rules.yaml，加载即与 meta_question_frequencies_vocabulary.yaml 键集全等断言（漂移 fail-closed，禁本件补默认档）；
#              拉取式对账器只产"该考了"的欠账清单，不发考试指令（13§3.2 分工闭环：领题执行归各考尺，完成后走 writeback 落账）；
#              禁 cron/Timer/sleep-loop（宪法§9.3）：本件全部为事件触发的一次性函数（回填完成/日切/挂起消除），无常驻入口；
#              逾期判定按窗册 kind 分档：trading_days/natural_period 计逾期，event/none 档逾期不适用（事件驱动缺 event_source_ref=不合格，由 writeback 拒收不在本件放行）；
#              新鲜窗（PQ-0108 月度滚动 20 日）语义=fresh_window_trading_days 字段，到期与逾期同一窗长口径；
#              账=审计事件（what=reexam 已落地码，after JSONB 带 due/overdue/window/days_since），主表零改动（13§7 净零：不为清单撑字段）；
#              终态与盲区跳过：merged/retired 不进复考台账（13§4.3 第 3 条）
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §3.1（改窗口口径先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 窗册与频度词表不等=ValueError（fail-closed，禁静默丢档）；
#                  last_exam 为 naive 时戳=ValueError（RULE-SCHEMA-TZ）；PG 不可达=原样上抛（禁降级出"全部不逾期"假结论）
# [TESTS] tests/governance/meta_question/test_exam_loop_scheduler.py（红腿：跨月未考必判逾期并落 reexam 账；蓝腿：窗内不产欠账；词表漂移必炸）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""reexam_scheduler — 新鲜窗复考调度（到期/逾期台账 + 事件触发对账，13§3）。

补齐 PQ-0054/PQ-0057/PQ-0108 的载体缺口：283 问首轮回填后**无人盘逾期**，复考分母为零。
本件是拉取式对账器（禁 sleep-loop，宪法§9.3）：事件触发 → 盘 ``last_exam`` vs 频度窗口 →
产出欠账清单并落 ``reexam`` 审计账，消费方=未答看板的复考队列视图（12§1 接口）。

用法::

    sched = ReexamScheduler(registry)
    report = sched.reconcile(actor="st-wo-b1-examloop|AI")   # 落账 + 返回清单
    for item in report["overdue"]:
        ...  # 由考尺侧领题执行，完成后 ExamLoopWriteback.writeback(...)
# #
# # 边:
# # I1 -.->|断点| F1
# # I2 -.->|断点| F1
# # I3 -.->|断点| F1
# # I4 -.->|断点| F1
# # F1 --> A1
# # A1 --> O1
# [/ALGO_FLOW]
# target: src/zephyr/governance/meta_question/exam_loop/reexam_scheduler.py (docstring 1544 字, 12 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/reexam_scheduler.yaml
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Final

from zephyr.governance.meta_question.exam_ops import TERMINAL_STATUSES
from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry
from zephyr.shared.io.yaml_utils import load_vocabulary_values
from zephyr.shared.utils.time_utils import now_utc

from .exam_lifecycle import ExamLoopStateMachine
from .ledger import ExamLoopLedger

__all__: Final = ["REEXAM_EVENT_CODE", "ReexamScheduler", "due_state", "load_window_rules"]

_CONFIG_DIR: Final[Path] = Path(__file__).resolve().parent / "config"
WINDOW_RULES_FILE: Final[str] = "examloop_reexam_window_rules.yaml"
FREQUENCY_VOCAB_FILE: Final[str] = "meta_question_frequencies_vocabulary.yaml"
#: 到期账落盘事件码（已落地词表，无需扩展）
REEXAM_EVENT_CODE: Final[str] = "reexam"
#: 自然周期档的近似天数（monthly=自然月最长 31 日 / quarterly=自然季最长 92 日；窗册内声明，本件只读）
_KIND_TRADING = "trading_days"
_KIND_NATURAL = "natural_period"
_KIND_EVENT = "event"
_KIND_NONE = "none"


# NO-BARE-SQL：SQL 集中于此（§5.160.2）；{s} 由调用方注入 registry.schema，禁写死日期。
_SQL_LAST_ARBITRATION = "SELECT q_id, created_at FROM {s}.meta_question_audit WHERE what = %s ORDER BY id DESC LIMIT %s"


def load_window_rules() -> dict[str, dict[str, Any]]:
    """读窗册 → ``{frequency: rule}``，并与频度词表全等校验（漂移 fail-closed）。"""
    raw = load_vocabulary_values(WINDOW_RULES_FILE, vocab_dir=_CONFIG_DIR, strict=True)
    if not raw:
        raise ValueError(f"窗册空值：{WINDOW_RULES_FILE}")
    import yaml  # noqa: PLC0415 ——仅取逐条规则时惰性读

    payload = yaml.safe_load((_CONFIG_DIR / WINDOW_RULES_FILE).read_text(encoding="utf-8")) or {}
    rules: dict[str, dict[str, Any]] = {}
    for entry in payload.get("values") or []:
        if not isinstance(entry, dict):
            raise ValueError(f"窗册条目须为映射：{entry!r}")
        key = str(entry.get("value") or "")
        rules[key] = {k: v for k, v in entry.items() if k != "value"}
    declared = set(load_vocabulary_values(FREQUENCY_VOCAB_FILE, strict=True))
    if set(rules) != declared:
        raise ValueError(
            f"窗册与频度词表漂移：窗册缺 {sorted(declared - set(rules))} 多 {sorted(set(rules) - declared)}"
        )
    return rules


def _as_aware(value: Any) -> datetime | None:  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    if value in (None, ""):
        return None
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"last_exam 为 naive 时戳：{value!r}（RULE-SCHEMA-TZ）")
    return parsed


def _due_state_header(
    frequency: str,
    kind: str,
    horizon: int,
    fresh: int,
    grace: int,
    stamp: datetime | None,
    day: date,
) -> dict[str, Any]:
    """到期/逾期台账的公共头部字段（各档位共用，13§3.1）。"""
    return {
        "frequency": frequency,
        "kind": kind,
        "window_days": horizon,
        "fresh_window_days": fresh,
        "grace_days": grace,
        "last_exam": None if stamp is None else stamp.date().isoformat(),
        "days_since": None if stamp is None else (day - stamp.date()).days,
        "applicable": kind in (_KIND_TRADING, _KIND_NATURAL),
        "due": False,
        "overdue": False,
        "basis": "",
    }


def _apply_natural_period_state(
    out: dict[str, Any], stamp: datetime, day: date, horizon: int, fresh: int, grace: int
) -> None:
    """自然周期档：跨自然月/季即逾期（13§3.1 原文），窗长用自然窗上限做同口径报警。"""
    crossed = _crossed_period(stamp.date(), day, months=1 if horizon <= 31 else 3)
    days = int(out["days_since"])
    out.update(
        {
            "due": crossed or days >= fresh,
            "overdue": crossed or days > fresh + grace,
            "basis": f"自然周期跨越={crossed}，日隔 {days} 对新鲜窗 {fresh}",
        }
    )


def due_state(
    frequency: str,
    last_exam: Any,  # noqa: any-abuse  any-abuse豁免: DB游标/外部数据动态对象与PIT日期解析，签名无法具体化
    *,
    today: date | None = None,
    rules: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """单问到期/逾期判定（纯计算，无 IO）。

    :return: ``{"frequency","kind","window_days","fresh_window_days","last_exam","days_since",
               "due","overdue","applicable","basis"}``
    """
    table = rules or load_window_rules()
    if frequency not in table:
        raise ValueError(f"frequency 不在窗册：{frequency!r}（词表漂移须先修窗册）")
    rule = table[frequency]
    kind = str(rule.get("kind") or "")
    horizon = int(rule.get("horizon_days") or 0)
    fresh = int(rule.get("fresh_window_trading_days") or 0)
    grace = int(rule.get("grace_days") or 0)
    stamp = _as_aware(last_exam)
    day = today or now_utc().date()
    out: dict[str, Any] = _due_state_header(frequency, kind, horizon, fresh, grace, stamp, day)
    if kind in (_KIND_EVENT, _KIND_NONE):
        out["basis"] = "逾期不适用（事件驱动/静态档，13§3.1）"
        return out
    if stamp is None:
        out.update({"due": True, "overdue": True, "basis": "从未考（last_exam 为空=欠第一笔账）"})
        return out
    days = int(out["days_since"])
    limit = horizon + grace
    if kind == _KIND_NATURAL and fresh:
        _apply_natural_period_state(out, stamp, day, horizon, fresh, grace)
        return out
    out.update({"due": days >= limit, "overdue": days > limit, "basis": f"日隔 {days} 对窗长 {limit}（{kind}）"})
    return out


def _crossed_period(since: date, until: date, *, months: int) -> bool:
    """是否跨越 ≥1 个自然周期（monthly months=1 / quarterly months=3）。"""
    span = (until.year - since.year) * 12 + (until.month - since.month)
    return span >= months


class ReexamScheduler:
    """新鲜窗复考对账器（事件触发，产欠账清单并落账）。"""

    def __init__(
        self,
        registry: MetaQuestionRegistry | None = None,
        *,
        ledger: ExamLoopLedger | None = None,
        rules: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.registry: Final[MetaQuestionRegistry] = registry or MetaQuestionRegistry()
        self.ledger: Final[ExamLoopLedger] = ledger or ExamLoopLedger(self.registry)
        self.rules: Final[dict[str, dict[str, Any]]] = rules or load_window_rules()
        #: 进台账的状态集=in_exam 之后可达态去掉终态（13§4.3：墓碑问不进复考台账）
        self._live_statuses: Final[frozenset[str]] = (
            ExamLoopStateMachine.descendants_of("answered") - TERMINAL_STATUSES
        ) | {"answered"}

    # -- 拉取式对账（13§3.2 通道 1）------------------------------------------

    def candidates(self, *, statuses: frozenset[str] | None = None) -> list[dict[str, Any]]:
        """只读拉取活问题（默认 answered/reexam/… 即 in_exam 之后非终态集）。"""
        wanted = sorted(statuses or self._live_statuses)
        if not wanted:
            raise ValueError("candidates 需至少一个状态")
        marks = ", ".join(["%s"] * len(wanted))
        sql = (
            "SELECT q_id, frequency, status, last_exam, exam_plan "
            f"FROM {{s}}.meta_question WHERE status IN ({marks}) ORDER BY q_id"
        ).format(s=self.registry.schema)
        conn = self.registry._conn(read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(sql, tuple(wanted))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]
        finally:
            conn.close()

    def reconcile(
        self,
        *,
        actor: str = "",
        today: date | None = None,
        statuses: frozenset[str] | None = None,
        book: bool = True,
        limit: int = 0,
    ) -> dict[str, Any]:
        """盘逾期并落 ``reexam`` 到期账（同 q_id 同自然日幂等不重复落账）。

        :param book: False=只出清单不落账（dry-run/复考判据读取用）
        :param limit: >0 时最多处理前 N 条（分批窗，防一次性冲刷账）
        """
        rows = self.candidates(statuses=statuses)
        already = self._already_booked(today=today)
        due_list: list[dict[str, Any]] = []
        overdue_list: list[dict[str, Any]] = []
        booked = 0
        for row in rows:
            state = due_state(str(row["frequency"]), row.get("last_exam"), today=today, rules=self.rules)
            record = {"q_id": row["q_id"], "status": row["status"], **state}
            if state["due"]:
                due_list.append(record)
            if state["overdue"]:
                overdue_list.append(record)
                if book and record["q_id"] not in already:
                    if limit and booked >= int(limit):
                        continue
                    self._book_overdue(actor=actor, record=record)
                    already.add(record["q_id"])
                    booked += 1
        return {
            "scanned": len(rows),
            "due": due_list,
            "overdue": overdue_list,
            "booked": booked,
            "due_count": len(due_list),
            "overdue_count": len(overdue_list),
            "as_of": (today or now_utc().date()).isoformat(),
            "execution_rate": _execution_rate(len(due_list), len(overdue_list)),
        }

    def _book_overdue(self, *, actor: str, record: dict[str, Any]) -> None:
        """逾期落账（what=reexam 已落地码；主表零改动，13§7 净零）。"""
        self.ledger.write_event_standalone(
            REEXAM_EVENT_CODE,
            q_id=str(record["q_id"]),
            actor=actor or "reconciler",
            after={"due": True, "overdue": True, **{k: record[k] for k in _BOOKED_KEYS if k in record}},
            evidence=f"freshness_reconcile;as_of={record['last_exam'] or 'never'}",
        )

    def _already_booked(self, *, today: date | None, scan_limit: int = 5000) -> set[str]:
        """当日已落到期账的 q_id 集（幂等重跑：日切事件重复触发不冲刷账）。

        日期比对在 Python 侧做（PG 返回 aware datetime / SQLite 返回文本，两侧同口径解析），
        禁把 ``::date`` 之类方言写进共用 SQL。
        """
        day = today or now_utc().date()
        sql = _SQL_LAST_ARBITRATION.format(s=self.registry.schema)
        conn = self.registry._conn(read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(sql, (REEXAM_EVENT_CODE, int(scan_limit)))
            rows = cur.fetchall()
        finally:
            conn.close()
        return {str(q_id) for q_id, created_at in rows if _as_aware(created_at).date() == day}


_BOOKED_KEYS: Final[tuple[str, ...]] = (
    "frequency",
    "kind",
    "window_days",
    "fresh_window_days",
    "last_exam",
    "days_since",
    "basis",
    "status",
)


def _execution_rate(due_total: int, overdue_total: int) -> float | None:
    """到期复考执行率（PQ-0054 判据分子/分母口径：1-逾期/到期；分母 0=None 禁按 100% 报）。
    # #
    # # 边:
    # # I1 -.->|断点| F1
    # # I2 -.->|断点| F1
    # # I3 -.->|断点| F1
    # # I4 -.->|断点| F1
    # # F1 --> A1
    # # A1 --> O1
    # [/ALGO_FLOW]
    """
    if not due_total:
        return None
    return round(100.0 * (due_total - overdue_total) / due_total, 4)
