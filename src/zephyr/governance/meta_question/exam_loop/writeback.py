# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1 回写契约（§1.1 结构/§1.2 六查/§1.3 证据/§1.4 时戳/§1.5 流转）+ §33 回写鉴权
# [MODULE] zephyr.governance.meta_question.exam_loop.writeback
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.meta_question_registry/exam_ops (唯一合法写通道复用：_load_row/_SQL_INSERT_EXAM_RESULT/_SQL_EXAM_WRITEBACK/_as_json/OUTCOME_FROM_STATUSES/BYPASS_ACTORS/异常族); .ledger; .exam_lifecycle; .exam_plan (结构化+六查+时间分层+功效); .arbitration (矛盾检测与三取二); .event_codes; zephyr.shared.utils.time_utils (now_utc); zephyr.shared.io.paths (REPO_ROOT，证据可达性核验)
# [CONSUMERS] scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py（复考 runner 的落账出口）; scripts/governance/meta_question/wo_b1_examloop/check_exam_loop.py（判据复考）; tests/governance/meta_question/test_exam_loop_writeback.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 本件=回填唯一合法入口（13§1：禁直改表、禁绕过本 API 的任何写路径；上一班 Owner 任务令 SQL 直写=临时通道，本件收口）；
#              回写鉴权（13§1 严口径，比冻结件 _check_claim 更紧）：claimed_by 必须存在且租约活跃且==调用会话，
#                无认领→claim_missing、不匹配→claim_mismatch（两者皆独立事务落账后拒收），Max/Owner 角色段可越过（10§7.4①）；
#              单事务先账后实（20§2.1）：exam_writeback 审计行 → exam_result 业务行 → 主表乐观锁 UPDATE，任一失败整体回滚（拒收痕另账，见 ledger）；
#              双时戳（PQ-0056/PQ-0096）：exam_completed_at（考试完成，调用方申报 aware）+ backfilled_at（回填，now_utc()）同时入审计 after JSONB
#                与 exam_result JSONB 载荷，落账时延=backfilled_at-exam_completed_at 可机检（P99 判据源）；申报时戳晚于回填时戳=拒；
#              answered 判定=六查全过（13§1.2 A1-A6，任一失败按 13§1.5 降级：A1/A2 失败→复考，A3-A6 失败→挂起且 suspend_reason 必填）；
#              功效不足/阈值被调低=延期不复考凑数（exam_plan.assess_power 唯一出口 defer；调低事实落 threshold_lowered 事件，PQ-0098）；
#              同 exam_plan_version 且窗口交叠的重复回写标 supplement 不入矛盾检测（13§2.1 防伪仲裁）；
#              仲裁未决（最近 exam_contradiction_case 载荷 state=open）期间禁发新考（13§2.2 防矛盾滚雪球）；
#              乐观锁零行命中→version_conflict 事件（含 expected/actual/第几次重放）后按 replay_limit 重读重放（PQ-0061）
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1/§2/§33（改回写契约先改设计稿）
# [STABILITY] new
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 鉴权失败=QuestionValidationError('claim_missing'/'claim_mismatch')（已落账）；
#                  仲裁未决=QuestionValidationError('arbitration_open')；六查不过=QuestionValidationError('six_check_failed', checks=…)（outcome=answered 时）；
#                  状态不允许该 outcome=QuestionValidationError('status_invalid')（已落 illegal_transition 痕）；
#                  naive 时戳/时戳倒挂=ValueError；重放超限=VersionConflictError；连接/SQL 异常=原样上抛（fail-closed）
# [TESTS] tests/governance/meta_question/test_exam_loop_writeback.py（红腿：伪造越权 writeback 必被拒+落 claim_mismatch 痕；
#          无认领回写必被拒；answered 但证据不可核必降级挂起；降阈值必落 threshold_lowered 且强制延期；时戳倒藏必拒）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""writeback — 考试回填唯一合法入口 :func:`ExamLoopWriteback.writeback`（13§1 回写契约）。

收口上一班"Owner 任务令 SQL 直写"临时通道：本件把**鉴权→六查→降级→双时戳落账→矛盾检测→
乐观锁写**编成单事务，任何绕过本件的 ``meta_question`` 写路径都属违约（20§2.1 先账后实、
13§1 禁直改表）。

用法::

    from zephyr.governance.meta_question.exam_loop import ExamLoopWriteback

    wb = ExamLoopWriteback(registry)                    # registry=冻结件实例（连接/JSONL 注入）
    receipt = wb.writeback("PQ-0051", {
        "outcome": "answered",
        "exam_ref": "wo-b1/probe/PQ-0051",
        "exam_plan_version": "v2-wo-b1",
        "conclusion_value": 100.0,
        "conclusion_dir": "支持",
        "confidence_level": 95.0,
        "data_window": {"start": "2026-09-01", "end": "2026-09-23",
                        "fetch_ts": "2026-09-24T01:00:00+00:00",
                        "decision_ts": "2026-09-24T02:00:00+00:00"},
        "sample_out_share": 1.0,
        "pit_assertion": "各源 as-of 均早于决策时点",
        "exam_completed_at": "2026-09-24T02:05:00+00:00",
        "evidence_refs": [{"table": "meta_question.meta_question",
                           "query": "SELECT ... ", "result_digest": "sha256:..."}],
    }, session_id="st-wo-b1-examloop")
# #
# # 边:
# # I1 -.->|断点| F1
# # I2 -.->|断点| F1
# # I3 -.->|断点| F1
# # I4 -.->|断点| F1
# # F1 --> A1
# # A1 --> O1
# [/ALGO_FLOW]
# target: src/zephyr/governance/meta_question/exam_loop/writeback.py (docstring 2272 字, 39 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/writeback.yaml
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from zephyr.governance.meta_question.exam_ops import (
    _SQL_EXAM_WRITEBACK,
    _SQL_INSERT_EXAM_RESULT,
    BYPASS_ACTORS,
    OUTCOME_FROM_STATUSES,
    QuestionValidationError,
    VersionConflictError,
    _as_json,
)
from zephyr.governance.meta_question.meta_question_registry import MetaQuestionRegistry
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

from . import event_codes, exam_plan
from .arbitration import detect_contradiction, resolve_majority
from .exam_lifecycle import ExamLoopStateMachine
from .ledger import ExamLoopLedger

__all__: Final = ["ANSWERED_OUTCOME", "ExamLoopWriteback", "REEXAM_OUTCOME", "SUSPENDED_OUTCOME", "WritebackOutcome"]

#: outcome 语义锚（单值锚，全集在 meta_question_outcomes_vocabulary.yaml）
ANSWERED_OUTCOME: Final[str] = "answered"
REEXAM_OUTCOME: Final[str] = "reexam"
SUSPENDED_OUTCOME: Final[str] = "suspended"

#: 六查失败码 → 降级出口（13§1.5：A1/A2 类=执行无结论→复考；A3-A6 类=数据/判据/证据缺陷→挂起）
_REEXAM_CHECKS: Final[frozenset[str]] = frozenset({"A1", "A2"})
_SUSPEND_CHECKS: Final[frozenset[str]] = frozenset({"A3", "A4", "A5", "A6"})
#: 结论方向枚举（13§1.1 机械三值，禁自由文本；真源=考试器口径，本件只认"不可判"为无结论）
_INDETERMINATE_DIR: Final[str] = "不可判"
#: 证据禁指向未 promote 的临时根（13§1.3）
_TEMP_EVIDENCE_ROOTS: Final[tuple[str, ...]] = (".runtime",)


@dataclass
class _AttemptRequest:
    """单次事务尝试的入参包（原 ``_attempt`` 八参签名收口进对象，参数门禁 ≤7）。

    字段语义与原关键字参数逐一对应：``outcome``=调用方申报的请求 outcome（尚未被
    六查/矛盾降级），``replay_attempt``=乐观锁重放序号（PQ-0061 落痕用）。
    """

    q_id: str
    payload: dict[str, Any]
    actor: str
    outcome: str
    exam_completed_at: datetime
    backfilled_at: datetime
    replay_attempt: int


@dataclass
class _AttemptState:
    """单次事务尝试的进行时状态（连接生命周期内逐步填充，字段序=原局部变量出现序）。"""

    req: _AttemptRequest
    row: dict[str, Any] = field(default_factory=dict)
    recheck: bool = False
    open_case: dict[str, Any] | None = None
    old_status: str = ""
    requested_outcome: str = ""
    plan: dict[str, Any] = field(default_factory=dict)
    outcome: str = ""
    six_check: dict[str, Any] = field(default_factory=dict)
    deferred_reason: str = ""
    expected_version: int = 0
    stamps: dict[str, Any] = field(default_factory=dict)
    supplements: int = 0
    contradiction: dict[str, Any] | None = None
    arbitration: dict[str, Any] | None = None
    evidence_refs: list[Any] = field(default_factory=list)


@dataclass
class WritebackOutcome:
    """一次回写的机械结论（回执对象，调用方据此决定后续动作）。"""

    q_id: str
    outcome: str
    from_status: str
    to_status: str
    version_before: int
    version_after: int
    exam_completed_at: str
    backfilled_at: str
    latency_seconds: float
    six_check: dict[str, Any]
    evidence_refs: list[Any] = field(default_factory=list)
    contradiction: dict[str, Any] | None = None
    arbitration: dict[str, Any] | None = None
    supplements: int = 0
    replays: int = 0
    deferred_reason: str = ""
    requested_outcome: str = ""

    def as_dict(self) -> dict[str, Any]:
        payload = dict(self.__dict__)
        payload["evidence_refs"] = list(self.evidence_refs)
        return payload


class ExamLoopWriteback:
    """考试回填 API（唯一合法入口）。"""

    def __init__(
        self,
        registry: MetaQuestionRegistry | None = None,
        *,
        ledger: ExamLoopLedger | None = None,
        state_machine: ExamLoopStateMachine | None = None,
    ) -> None:
        self.registry: Final[MetaQuestionRegistry] = registry or MetaQuestionRegistry()
        self.ledger: Final[ExamLoopLedger] = ledger or ExamLoopLedger(self.registry)
        self.sm: Final[ExamLoopStateMachine] = state_machine or ExamLoopStateMachine(self.ledger)

    # -- 公共入口 -------------------------------------------------------------

    def writeback(
        self,
        q_id: str,
        exam_result: dict[str, Any] | None,
        *,
        session_id: str = "",
        replay_limit: int = 3,
    ) -> dict[str, Any]:
        """回填一场考试（13§1 全契约）。返回回执 dict（含双时戳/六查/矛盾/重放计数）。"""
        payload = dict(exam_result or {})
        actor = str(payload.get("recorded_by") or session_id or "")
        exam_completed_at = _parse_aware(payload.get("exam_completed_at"), "exam_completed_at")
        backfilled_at = now_utc()
        if exam_completed_at > backfilled_at:
            raise ValueError(f"考试完成时戳晚于回填时戳（时戳倒挂=尺子失真）：{exam_completed_at} > {backfilled_at}")
        outcome = str(payload.get("outcome") or "")
        if outcome not in OUTCOME_FROM_STATUSES:
            raise QuestionValidationError("status_invalid", {"outcome": outcome})

        attempts = 0
        while attempts <= max(int(replay_limit), 0):
            try:
                return self._attempt(
                    _AttemptRequest(
                        q_id=q_id,
                        payload=payload,
                        actor=actor,
                        outcome=outcome,
                        exam_completed_at=exam_completed_at,
                        backfilled_at=backfilled_at,
                        replay_attempt=attempts,
                    )
                )["receipt"]
            except VersionConflictError:
                attempts += 1
                if attempts > int(replay_limit):
                    raise

    # -- 单次事务尝试（鉴权→判定→先账后实）------------------------------------

    def _attempt(self, req: _AttemptRequest) -> dict[str, Any]:
        conn = self.registry._conn(read_only=False)
        state = _AttemptState(req=req)
        try:
            self._settle_in_txn(conn, state)
        except VersionConflictError as exc:
            conn.rollback()
            # PQ-0061：冲突必落痕（expected/actual/第几次重放），否则"重读重放成功率"无从复考
            self.sm.trace_reject(
                req.q_id,
                req.actor,
                event_codes.CODE_VERSION_CONFLICT,
                "exam_writeback",
                {
                    "reason": "version_conflict",
                    "expected_version": exc.expected_version,
                    "replay_attempt": req.replay_attempt,
                },
            )
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return _attempt_receipt(req, state)

    # -- 单事务内逐步落账（原 _attempt try 块，①-⑧ 步序与文案零改动）----------

    def _settle_in_txn(self, conn: object, state: _AttemptState) -> None:
        cur = conn.cursor()
        row = self._load_or_reject(cur, state)
        self._gate_admission(row, state)
        self._reject_illegal_transition(row, state)
        self._decide_into(row, state)
        self._detect_disputes(cur, state)
        self._book_audit_events(cur, state)
        self._persist_business_row(cur, state)
        state.evidence_refs = list(state.req.payload.get("evidence_refs") or row.get("evidence_refs") or [])
        conn.commit()

    def _load_or_reject(self, cur: object, state: _AttemptState) -> dict[str, Any]:
        row = self.registry._load_row(cur, state.req.q_id)
        if row is None:
            raise QuestionValidationError("qid_not_found", {"q_id": state.req.q_id})
        state.row = row
        return row

    def _gate_admission(self, row: dict[str, Any], state: _AttemptState) -> None:
        # ① 回写鉴权（13§1 严口径：无认领/不匹配=独立事务落痕后拒收，本事务零写）
        state.recheck = bool(state.req.payload.get("arbitration_recheck"))
        self._authorize(row, actor=state.req.actor, q_id=state.req.q_id)
        # ② 仲裁未决闸（13§2.2：open 期禁发新考；步 2 的那一次复考 R3 本身放行）
        state.open_case = self._open_arbitration_case(state.req.q_id, recheck=state.recheck)

    def _reject_illegal_transition(self, row: dict[str, Any], state: _AttemptState) -> None:
        # ③ 状态-结论合法组合（13§1.5，越界=illegal_transition 痕 + 拒）
        state.old_status = str(row["status"])
        state.requested_outcome = state.req.outcome
        if state.old_status not in OUTCOME_FROM_STATUSES[state.req.outcome]:
            self.sm.trace_reject(
                state.req.q_id,
                state.req.actor,
                event_codes.CODE_ILLEGAL_TRANSITION,
                "exam_writeback",
                {"reason": "outcome_state_mismatch", "from_status": state.old_status, "outcome": state.req.outcome},
            )
            raise QuestionValidationError(
                "status_invalid", {"from_status": state.old_status, "outcome": state.req.outcome}
            )

    def _decide_into(self, row: dict[str, Any], state: _AttemptState) -> None:
        # ④ 预注册考卷结构化 + 六查 + 功效/降阈值处置（13§1.2 / PQ-0098）
        raw_plan = row.get("exam_plan")
        state.plan = exam_plan.structure_plan(
            raw_plan if isinstance(raw_plan, dict) else json.loads(raw_plan or "{}"),
            plan_version=str(state.req.payload.get("exam_plan_version") or ""),
        )
        verdict = self._decide(
            row,
            state.plan,
            state.req.payload,
            outcome=state.req.outcome,
            actor=state.req.actor,
            q_id=state.req.q_id,
        )
        state.outcome, state.six_check, state.deferred_reason = (
            verdict["outcome"],
            verdict["six_check"],
            verdict["deferred_reason"],
        )

    def _detect_disputes(self, cur: object, state: _AttemptState) -> None:
        # ⑤ 乐观锁基线（同事务重读版本，零行命中即冲突→上层重读重放）
        state.expected_version = int(state.row["version"])
        state.stamps = _attempt_stamps(state.req)
        # ⑥ 矛盾检测与三取二（13§2.1/§2.2：同版本比对，交叠窗=supplement 不入矛盾）
        prior = self._prior_results(cur, state.req.q_id, str(state.plan.get("plan_version") or ""))
        state.supplements = _count_supplements(prior, state.req.payload)
        state.contradiction = None if state.recheck else detect_contradiction(state.plan, state.req.payload, prior)
        state.arbitration = (
            resolve_majority(state.plan, state.req.payload, prior, state.open_case, arbitration_recheck=True)
            if state.recheck
            else None
        )
        state.outcome, state.deferred_reason = _demote_on_dispute(
            state.outcome, state.deferred_reason, state.contradiction, state.arbitration
        )

    def _book_audit_events(self, cur: object, state: _AttemptState) -> None:
        # ⑦ 账先行（拒收痕已在独立事务，此处为成功落账的主账）
        ledger = self.ledger
        audit_after: dict[str, Any] = {
            "status": state.outcome,
            **state.stamps,
            "outcome": state.outcome,
            "requested_outcome": state.requested_outcome,
            "exam_plan_version": state.plan.get("plan_version"),
            "six_check": state.six_check,
            "deferred_reason": state.deferred_reason,
            "supplements": state.supplements,
            "replay_attempt": state.req.replay_attempt,
            "pit_check_ref": str(state.req.payload.get("pit_check_ref") or ""),
        }
        ledger.write_event(
            cur,
            "exam_writeback",
            q_id=state.req.q_id,
            actor=state.req.actor,
            before={"status": state.old_status, "version": state.expected_version},
            after=audit_after,
            evidence=str(state.req.payload.get("exam_ref") or state.req.payload.get("examiner_ref") or ""),
            diff=[
                {"field": "status", "old": state.old_status, "new": state.outcome},
                {"field": "last_exam", "old": None, "new": state.stamps["backfilled_at"]},
                {"field": "exam_completed_at", "old": None, "new": state.stamps["exam_completed_at"]},
            ],
        )
        if state.contradiction:
            ledger.write_event(
                cur,
                "exam_contradiction_case",
                q_id=state.req.q_id,
                actor=state.req.actor,
                after={"state": "open", **state.contradiction},
                evidence=f"case={state.contradiction.get('case_id')}",
            )
        if state.arbitration:
            ledger.write_event(
                cur,
                "exam_arbitrate",
                q_id=state.req.q_id,
                actor=state.req.actor,
                after=state.arbitration,
                evidence=f"2of3={state.arbitration.get('winner') or state.arbitration.get('basis')}",
            )
            # 案卷闭合（13§2.2 无死态：open→resolved | escalated_max）
            closing_case = {**(state.open_case or {}), **(state.contradiction or {})}
            ledger.write_event(
                cur,
                "exam_contradiction_case",
                q_id=state.req.q_id,
                actor=state.req.actor,
                after={
                    "state": "resolved" if state.arbitration["verdict"] == "majority" else "escalated_max",
                    "case_id": state.arbitration.get("case_id") or closing_case.get("case_id"),
                    "basis": state.arbitration.get("basis"),
                },
                evidence=f"case={state.arbitration.get('case_id') or closing_case.get('case_id')}",
            )

    def _persist_business_row(self, cur: object, state: _AttemptState) -> None:
        # ⑧ 业务行：exam_result 记账 + 主表乐观锁推进
        cur.execute(
            _SQL_INSERT_EXAM_RESULT.format(s=self.registry.schema),
            (
                state.req.q_id,
                str(state.req.payload.get("exam_ref") or state.req.payload.get("examiner_ref") or ""),
                _as_json(self._conclusion_block(state.req.payload, state.plan, state.six_check)),
                _as_json(
                    self._confidence_block(state.req.payload, state.stamps, state.six_check, state.deferred_reason)
                ),
                _as_json(self._window_block(state.req.payload, state.plan)),
                str(state.req.payload.get("pit_assertion") or ""),
                state.outcome,
                state.req.actor,
                state.req.backfilled_at,
            ),
        )
        cur.execute(
            _SQL_EXAM_WRITEBACK.format(s=self.registry.schema),
            (state.outcome, state.req.backfilled_at, state.req.backfilled_at, state.req.q_id, state.expected_version),
        )
        if cur.rowcount != 1:
            raise VersionConflictError(state.req.q_id, state.expected_version)

    # -- 鉴权与闸 ------------------------------------------------------------

    def _authorize(self, row: dict[str, Any], *, actor: str, q_id: str) -> None:
        """回写鉴权（13§1）：claimed_by==调用会话且租约活跃；无认领/不匹配=落账后拒。"""
        principal, role = _split_actor(actor)
        if role in BYPASS_ACTORS or principal in BYPASS_ACTORS or actor in BYPASS_ACTORS:
            return
        holder = row.get("claimed_by")
        until = _as_dt(row.get("claimed_until"))
        active = bool(holder) and (until is None or until > now_utc())
        if not active:
            self.ledger.write_event_standalone(
                event_codes.CODE_CLAIM_MISSING,
                q_id=q_id,
                actor=actor or "unknown",
                after={
                    "rejected": True,
                    "reason": "claim_missing",
                    "claimed_by": holder,
                    "claimed_until": None if until is None else until.isoformat(),
                },
                evidence="writeback_auth",
            )
            raise QuestionValidationError("claim_missing", {"q_id": q_id, "claimed_by": holder})
        if str(holder) != principal and str(holder) != actor:
            self.ledger.write_event_standalone(
                event_codes.CODE_CLAIM_MISMATCH,
                q_id=q_id,
                actor=actor or "unknown",
                before={"claimed_by": holder},
                after={"rejected": True, "reason": "claim_mismatch", "claimed_by": holder},
                evidence="writeback_auth",
            )
            raise QuestionValidationError(
                "claim_mismatch", {"q_id": q_id, "claimed_by": holder, "action": "exam_writeback"}
            )

    def _open_arbitration_case(self, q_id: str, *, recheck: bool = False) -> dict[str, Any] | None:
        """仲裁未决闸（13§2.2 机检=最近 exam_contradiction_case 载荷 state=open）。

        未决期间禁发新考（防矛盾滚雪球）；唯一例外=步 2 的那一次复考 R3
        （``arbitration_recheck=True``），其落账即由 ``resolve_majority`` 把案卷置为
        resolved/escalated_max，不留死态。

        :return: 未决案卷载荷（R3 复考时据此回写 case_id 闭合），无未决案卷返回 ``None``
        """
        events = self.ledger.latest_events(q_id, ("exam_contradiction_case",), limit=1)
        if not events:
            return None
        after = events[0].get("after") or {}
        if isinstance(after, str):
            after = json.loads(after or "{}")
        if str(after.get("state") or "") != "open":
            return None
        if not recheck:
            raise QuestionValidationError(
                "arbitration_open",
                {"q_id": q_id, "case_ref": after.get("case_id"), "rule": "13§2.2 仲裁期间禁发新考"},
            )
        return after

    # -- 判定（六查 + 功效 + 降阈值）------------------------------------------

    def _decide(
        self,
        row: dict[str, Any],
        plan: dict[str, Any],
        payload: dict[str, Any],
        *,
        outcome: str,
        actor: str,
        q_id: str,
    ) -> dict[str, Any]:
        """跑 A1-A6 六查与功效核验，产出（可被降级的）最终 outcome + 六查明细。"""
        six = six_check(row, plan, payload)
        deferred_reason = ""
        lowered = _threshold_lowered(plan, payload)
        if lowered:
            self.ledger.write_event_standalone(
                event_codes.CODE_THRESHOLD_LOWERED,
                q_id=q_id,
                actor=actor,
                after={
                    "prelocked": lowered["prelocked"],
                    "used": lowered["used"],
                    "reason": "threshold_lowered",
                    "action": "force_defer",
                },
                evidence="exam_loop_power_gate",
            )
            outcome, deferred_reason = REEXAM_OUTCOME, "threshold_lowered_defer"
            six["A3"]["ok"] = False
            six["A3"]["reason"] = "threshold_lowered"
        # 功效闸适用面=PQ-0098 题面所指 IC 类考试（或调用方显式申报效应量的统计断言）；
        # 治理自检类计数题不属该适用面，不得因"未申报效应量"被强行延期（否则判据机自我空转）
        power_applies = bool(exam_plan.is_ic_like(plan)) or payload.get("effect_size") not in (None, "")
        if power_applies and outcome == ANSWERED_OUTCOME:
            power = exam_plan.assess_power(
                plan,
                sample_size=payload.get("sample_size"),
                effect_size=payload.get("effect_size"),
            )
            if power.action == "defer":
                outcome, deferred_reason = REEXAM_OUTCOME, power.reason
        elif not power_applies:
            six["power_gate"] = {"ok": True, "reason": "not_ic_like_exam（PQ-0098 适用面外，计数类自检题不核功效）"}
        if outcome == ANSWERED_OUTCOME and not six["passed"]:
            short = sorted(
                key for key in ("A1", "A2", "A3", "A4", "A5", "A6") if not bool((six.get(key) or {}).get("ok"))
            )
            if any(code in _SUSPEND_CHECKS for code in short):
                outcome = SUSPENDED_OUTCOME
                if not str(payload.get("suspend_reason") or "").strip():
                    raise QuestionValidationError(
                        "six_check_failed",
                        {"q_id": q_id, "failed": short, "need": "suspend_reason 必填（13§1.5 挂起条件）"},
                    )
            else:
                outcome = REEXAM_OUTCOME
        return {"outcome": outcome, "six_check": six, "deferred_reason": deferred_reason}

    # -- 载荷分块（无 schema 变更：新字段全进既有 JSONB，13§7 提案未过评审的降级实现）--

    @staticmethod
    def _conclusion_block(payload: dict[str, Any], plan: dict[str, Any], six: dict[str, Any]) -> dict[str, Any]:
        """结论块——必须同时承载战役规范 11 键与 13 号设计新增字段。

        规范键 `outcome` 是**裁决**（pass/fail/insufficient），与 exam_result.outcome 列
        （生命周期=answered/reexam/suspended）语义不同；全仓读出（results 镜像、闭环台账、
        三态验收）一律按 `conclusion->>'outcome'` 取裁决，缺它会让问题掉出三态桶。
        """
        return {
            # —— 规范 11 键（与 283 问原卷同构，下游唯一读出面）——
            "outcome": payload.get("verdict") or payload.get("conclusion_outcome") or "",
            "conclusion": str(payload.get("conclusion_text") or ""),
            "evidence": payload.get("evidence") or [],
            "fail_type": payload.get("fail_type"),
            "confidence": payload.get("confidence_level"),
            "data_window": payload.get("data_window") or {},
            "exam_ref": str(payload.get("exam_ref") or payload.get("examiner_ref") or ""),
            "pit_assertion": str(payload.get("pit_assertion") or ""),
            "three_check": payload.get("three_check") or {},
            "notes": str(payload.get("notes") or ""),
            "threshold": plan.get("threshold"),
            # —— 13 号设计新增（结构化判据与六查留痕）——
            "value": payload.get("conclusion_value"),
            "dir": payload.get("conclusion_dir"),
            "criterion": plan.get("criterion"),
            "threshold_used": payload.get("threshold_used"),
            "sample_size": payload.get("sample_size"),
            "effect_size": payload.get("effect_size"),
            "degraded": list(plan.get("degraded") or []),
            "checks": {k: v for k, v in six.items() if k.startswith("A")},
        }

    @staticmethod
    def _confidence_block(
        payload: dict[str, Any], stamps: dict[str, Any], six: dict[str, Any], deferred: str
    ) -> dict[str, Any]:
        return {
            "level": payload.get("confidence_level"),
            "ci_lo": payload.get("ci_lo"),
            "ci_hi": payload.get("ci_hi"),
            **stamps,
            "deferred_reason": deferred,
            "passed": bool(six.get("passed")),
        }

    @staticmethod
    def _window_block(payload: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
        window = dict(payload.get("data_window") or {})
        window.setdefault("exam_plan_version", plan.get("plan_version"))
        if payload.get("sample_out_share") is not None:
            window.setdefault("sample_out_share", payload.get("sample_out_share"))
        return window

    # -- 历次同版本结果（矛盾检测输入）----------------------------------------

    def _prior_results(self, cur: object, q_id: str, plan_version: str) -> list[dict[str, Any]]:
        sql = (
            "SELECT conclusion, confidence, data_window, outcome, recorded_by, created_at "
            f"FROM {self.registry.schema}.meta_question_exam_result WHERE q_id = %s ORDER BY id DESC LIMIT %s"
        )
        cur.execute(sql, (q_id, 12))
        cols = [d[0] for d in cur.description]
        out: list[dict[str, Any]] = []
        for raw in cur.fetchall():
            item = dict(zip(cols, raw, strict=True))
            for key in ("conclusion", "confidence", "data_window"):
                value = item.get(key)
                if isinstance(value, str):
                    try:
                        item[key] = json.loads(value)
                    except ValueError:
                        item[key] = {}
            out.append(item)
        if plan_version:
            same = [r for r in out if str((r.get("data_window") or {}).get("exam_plan_version") or "") == plan_version]
            if same:
                return same
        return out


# ---------------------------------------------------------------------------
# 模块级纯函数（可单测，无 IO）
# ---------------------------------------------------------------------------


def _attempt_stamps(req: _AttemptRequest) -> dict[str, Any]:
    """双时戳（PQ-0056/PQ-0096）：exam_completed_at + backfilled_at + 可机检时延。"""
    return {
        "exam_completed_at": req.exam_completed_at.isoformat(),
        "backfilled_at": req.backfilled_at.isoformat(),
        "latency_seconds": round((req.backfilled_at - req.exam_completed_at).total_seconds(), 6),
    }


def _demote_on_dispute(
    outcome: str,
    deferred_reason: str,
    contradiction: dict[str, Any] | None,
    arbitration: dict[str, Any] | None,
) -> tuple[str, str]:
    """矛盾/仲裁未决时 answered 就地降级为复考态（13§2.1/§2.2，降级次序与文案同原内联分支）。"""
    if contradiction and outcome == ANSWERED_OUTCOME:
        # 新案成立：不得就地宣告 answered，状态转复考等 R3（案卷 open 拦住后续新考）
        outcome = REEXAM_OUTCOME
        deferred_reason = deferred_reason or f"contradiction:{contradiction['case_id']}"
    if arbitration and arbitration.get("verdict") != "majority" and outcome == ANSWERED_OUTCOME:
        # 升级 Max 期间保持复考态（消费方可见"仲裁中"，13§2.2）
        outcome = REEXAM_OUTCOME
        deferred_reason = deferred_reason or f"escalated_max:{arbitration.get('basis')}"
    return outcome, deferred_reason


def _attempt_receipt(req: _AttemptRequest, state: _AttemptState) -> dict[str, Any]:
    """回执组装（原 ``_attempt`` 尾段：WritebackOutcome + conflict_trace，字段零增减）。"""
    receipt = WritebackOutcome(
        q_id=req.q_id,
        outcome=state.outcome,
        from_status=state.old_status,
        to_status=state.outcome,
        version_before=state.expected_version,
        version_after=state.expected_version + 1,
        exam_completed_at=state.stamps["exam_completed_at"],
        backfilled_at=state.stamps["backfilled_at"],
        latency_seconds=state.stamps["latency_seconds"],
        six_check=state.six_check,
        evidence_refs=state.evidence_refs,
        contradiction=state.contradiction,
        arbitration=state.arbitration,
        supplements=state.supplements,
        replays=req.replay_attempt,
        deferred_reason=state.deferred_reason,
        requested_outcome=state.requested_outcome,
    )
    conflict_trace_payload = {"expected_version": state.expected_version, "replay_attempt": req.replay_attempt}
    return {"receipt": receipt.as_dict(), "conflict_trace": conflict_trace_payload}


def six_check(row: dict[str, Any], plan: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    """13§1.2 answered 六查机械判定（A1-A6 全过才算"答了"）。"""
    out: dict[str, Any] = {}
    out["A1"] = _check_a1(payload)
    out["A2"] = _check_a2(plan, payload)
    out["A3"] = _check_a3(row, plan, payload)
    out["A4"] = _check_a4(row, plan, payload)
    out["A5"] = _check_a5(payload)
    out["A6"] = _check_a6(payload)
    out["passed"] = all(bool(out[key]["ok"]) for key in ("A1", "A2", "A3", "A4", "A5", "A6"))
    return out


def _check_a1(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("conclusion_value")
    direction = str(payload.get("conclusion_dir") or "").strip()
    filled = value not in (None, "") and bool(direction)
    decisive = direction != _INDETERMINATE_DIR
    ok = filled and decisive
    return {"ok": ok, "reason": "" if ok else "结论未填充或方向为不可判（13§1.2 A1）"}


def _check_a2(plan: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    required = plan.get("min_confidence")
    level = payload.get("confidence_level")
    if required in (None, ""):
        return {"ok": False, "reason": "exam_plan 未预锁最低置信阈（A2 不可核，须先结构化考卷）"}
    try:
        ok = float(level) >= float(required)
    except (TypeError, ValueError):
        return {"ok": False, "reason": f"confidence_level 非数值：{level!r}"}
    return {
        "ok": ok,
        "required": float(required),
        "observed": float(level),
        "reason": "" if ok else "置信低于预注册阈（13§1.2 A2）",
    }


def _check_a3(row: dict[str, Any], plan: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    missing = exam_plan.required_for_answered(plan)
    if missing:
        return {"ok": False, "reason": f"预注册缺判据/阈值字段：{missing}"}
    declared = payload.get("threshold_used")
    clauses = [c for c in plan.get("threshold_clauses") or [] if "value" in c]
    if declared not in (None, "") and clauses:
        primary = float(clauses[0]["value"])
        if float(declared) < primary and clauses[0].get("op") in (">=", ">", "="):
            return {"ok": False, "reason": f"回填阈值 {declared} 低于预锁 {primary}（降阈值即失真）"}
    if payload.get("conclusion_value") in (None, ""):
        return {"ok": False, "reason": "判据取值未回填，无法与阈值对照（13§1.2 A3）"}
    return {"ok": True, "reason": "", "criterion": plan.get("criterion"), "threshold": plan.get("threshold")}


def _check_a4(row: dict[str, Any], plan: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    window = payload.get("data_window") or {}
    generated_at = _row_generated_at(row)
    violations = exam_plan.check_time_layering(window, generated_at=generated_at)
    codes = {v.code for v in violations}
    if "window_straddles_generation" in codes:
        return {"ok": False, "reason": ";".join(v.detail for v in violations)}
    share, basis = exam_plan.out_of_sample_share(
        window, generated_at=generated_at, declared=payload.get("sample_out_share")
    )
    required = plan.get("out_of_sample_share_min")
    if required not in (None, ""):
        if share is None:
            return {"ok": False, "reason": f"样本外份额不可核（basis={basis}，PQ-0055 须申报或给 in_sample 边界）"}
        if share < float(required):
            return {"ok": False, "reason": f"样本外份额 {share} < 预锁 {required}（PQ-0055）"}
    other = [v for v in violations if v.code != "window_straddles_generation"]
    if other:
        return {"ok": False, "reason": ";".join(v.detail for v in other), "share": share, "basis": basis}
    return {"ok": True, "reason": "", "share": share, "basis": basis}


def _check_a5(payload: dict[str, Any]) -> dict[str, Any]:
    assertion = payload.get("pit_assertion")
    if not assertion or (isinstance(assertion, str) and not assertion.strip()):
        return {"ok": False, "reason": "PIT 断言缺失（13§3.3 第 3 条：缺断言=A5 失败）"}
    window = payload.get("data_window") or {}
    fetch_ts = _as_dt(window.get("fetch_ts"))
    decision_ts = _as_dt(window.get("decision_ts"))
    if fetch_ts is None or decision_ts is None:
        return {"ok": False, "reason": "取数/决策双时戳缺项（PQ-0096：无时戳即无法比对违例）"}
    if fetch_ts > decision_ts:
        return {"ok": False, "reason": f"取数时戳晚于决策时戳（PIT 违例：{fetch_ts} > {decision_ts}）"}
    if fetch_ts == decision_ts:
        return {"ok": False, "reason": "取数与决策同一时戳（13§3.3 第 2 条：同一时戳禁循环）"}
    return {"ok": True, "reason": "", "fetch_ts": fetch_ts.isoformat(), "decision_ts": decision_ts.isoformat()}


def _check_a6(payload: dict[str, Any]) -> dict[str, Any]:
    refs = payload.get("evidence_refs") or []
    if not isinstance(refs, list) or not refs:
        return {"ok": False, "reason": "证据引用为空（13§1.2 A6：≥1 且逐条可核）"}
    bad = [ref for ref in refs if not evidence_resolvable(ref)]
    if bad:
        return {"ok": False, "reason": f"证据不可核：{bad[:3]}（13§1.3 禁外部 URL 唯一证据/禁未 promote 临时路径）"}
    return {"ok": True, "reason": "", "count": len(refs)}


def evidence_resolvable(ref: object) -> bool:
    """证据可核性（13§1.3）：仓内路径实存（非 .runtime 未 promote）或表+查询锚。"""
    if isinstance(ref, str):
        return _path_ref_ok(ref)
    if not isinstance(ref, dict):
        return False
    path = str(ref.get("path") or "")
    if path and _path_ref_ok(path):
        return True
    table = str(ref.get("table") or "")
    query = str(ref.get("query") or "")
    if query and (table or str(ref.get("commit") or "")):
        return True
    return False


def _path_ref_ok(path: str) -> bool:
    if "://" in path:  # 外部 URL 不作唯一证据（13§1.3）
        return False
    candidate = Path(path)
    if candidate.parts and candidate.parts[0] in _TEMP_EVIDENCE_ROOTS:
        return False  # 临时产物须先 promote 方可引用（宪法§9.4）
    resolved = candidate if candidate.is_absolute() else REPO_ROOT / candidate
    return resolved.exists()


def _threshold_lowered(plan: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any] | None:
    """申报阈值低于预锁阈值 → 返回降阈值明细（PQ-0098 判据"降阈值事件=0"的落账触发点）。"""
    declared = payload.get("threshold_used")
    if declared in (None, ""):
        return None
    clauses = [c for c in plan.get("threshold_clauses") or [] if "value" in c]
    if not clauses:
        return None
    primary = clauses[0]
    try:
        used, locked = float(declared), float(primary["value"])
    except (TypeError, ValueError):
        return None
    if primary.get("op") in (">=", ">", "=") and used < locked:
        return {"prelocked": locked, "used": used, "op": primary.get("op")}
    if primary.get("op") in ("<=", "<") and used > locked:
        return {"prelocked": locked, "used": used, "op": primary.get("op")}
    return None


def _count_supplements(prior: list[dict[str, Any]], payload: dict[str, Any]) -> int:
    """同版本且数据窗口交叠的既有结果条数（13§2.1 标 supplement，不入矛盾检测）。"""
    window = payload.get("data_window") or {}
    start, end = _to_date(window.get("start")), _to_date(window.get("end"))
    if not (start and end):
        return 0
    version = str(window.get("exam_plan_version") or payload.get("exam_plan_version") or "")
    hits = 0
    for item in prior:
        prev = item.get("data_window") or {}
        if version and str(prev.get("exam_plan_version") or "") != version:
            continue
        p_start, p_end = _to_date(prev.get("start")), _to_date(prev.get("end"))
        if p_start and p_end and not (p_end < start or p_start > end):
            hits += 1
    return hits


def _row_generated_at(row: dict[str, Any]) -> str:
    """问题生成时戳：provenance.registered_at 优先，退到 created_at（PQ-0055 比对锚）。"""
    provenance = row.get("provenance")
    if isinstance(provenance, str):
        try:
            provenance = json.loads(provenance)
        except ValueError:
            provenance = {}
    provenance = provenance or {}
    return str(provenance.get("registered_at") or row.get("created_at") or "")


def _split_actor(actor: str) -> tuple[str, str]:
    """who 口径=session_id+角色（20§2.1）：``st-x|AI`` → (principal, role)。"""
    text = str(actor or "")
    if "|" in text:
        principal, _, role = text.partition("|")
        return principal.strip(), role.strip()
    return text.strip(), text.strip()


def _as_dt(value: object) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    if not exam_plan.is_aware(parsed):
        raise ValueError(f"naive 时戳：{value!r}（RULE-SCHEMA-TZ：timestamptz 须显式时区）")
    return parsed


def _parse_aware(value: object, field_name: str) -> datetime:
    parsed = _as_dt(value)
    if parsed is None:
        raise ValueError(f"{field_name} 缺失或非时戳：{value!r}（13§1.4：回填时戳由本 API 写，禁手工）")
    return parsed.astimezone(now_utc().tzinfo)


def _to_date(value: object) -> object:
    return exam_plan.to_date(value)  # 同包工具复用，禁第三份日期解析实现


def digest_payload(payload: object) -> str:
    """证据摘要（落 evidence 锚点用，sha256 前 16 位）。
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
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]
