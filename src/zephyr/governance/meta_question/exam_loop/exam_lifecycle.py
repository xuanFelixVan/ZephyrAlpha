# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1.5 状态流转机械判定 + §2.2 仲裁链（拦截痕/冲突痕）
# [MODULE] zephyr.governance.meta_question.exam_loop.exam_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.exam_ops (LEGAL_TRANSITIONS/TERMINAL_STATUSES/WILDCARD_TARGETS/VALID_STATUSES/QuestionValidationError/VersionConflictError——边表与异常真源，禁本件重抄); .ledger (ExamLoopLedger 落账组合口); .event_codes (illegal_transition/version_conflict 载体)
# [CONSUMERS] zephyr.governance.meta_question.exam_loop.writeback; .reexam_scheduler; scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py; tests/governance/meta_question/test_exam_loop_state_machine.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 合法边唯一真源=exam_ops.LEGAL_TRANSITIONS（含通配边 WILDCARD_TARGETS/终态 TERMINAL_STATUSES），本件零边表副本、零状态字面量；
#              拦截器只做两件事：①流转前置断言（边不合法即不落业务写，短路抛 illegal_transition）②**拒收必落账**——
#              冻结件 transition 抛错零副作用（连账都不记），故拦截痕由本件以独立事务补记（20§2.1 先账后实的对偶：拒了也要留痕）；
#              乐观锁冲突零行命中→落 version_conflict 事件（载荷带 expected/actual version + 第几次重放），重放次数有上限（默认 3），超限上抛 VersionConflictError；
#              状态推进一律走 registry.transition（认领鉴权/乐观锁/审计三闸齐走），本件禁自拼 UPDATE status
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md §1.5（改边先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法边=QuestionValidationError('illegal_transition')（拦截痕已落账后原样上抛，调用方不得吞）；
#                  乐观锁重放超限=VersionConflictError(q_id, expected_version)；
#                  账行写入失败=原样上抛（fail-closed：拦截痕落不下则本次拒收不成立，禁静默放行）
# [TESTS] tests/governance/meta_question/test_exam_loop_state_machine.py（红腿：伪造非法流转必产 illegal_transition 事件；蓝腿：registered→in_exam→answered 全链 + 冲突重放成功率）
# [A_module] module_id=MOD-METAQ-EXAMLOOP | layer=module | stability=new | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""exam_lifecycle — 考试生命周期状态机推进拦截器（合法边注册视图 + 拒收落账 + 冲突重放留痕）。

补齐 PQ-0060/PQ-0061 的载体缺口：冻结件 ``registry.transition`` 已在边不合法时抛
``illegal_transition`` 并零副作用回滚，但**零副作用=零痕**，导致"非法边拦截率"无从复考
（分母记不下来）。本件是它外层的拦截器：拒收当轮以独立事务补记 ``illegal_transition`` /
``claim_mismatch`` 事件，并提供 ``with_version_replay`` 把乐观锁冲突（``conflict``）与
重放结果关联落账。

用法::

    sm = ExamLoopStateMachine(ledger)
    sm.transition("PQ-0051", "mining", actor="st-wo-b1-examloop|AI", evidence="开工")
    sm.transition("PQ-0051", "answered", actor=...)   # → 抛 illegal_transition + 落账
    result = sm.with_version_replay(lambda cur, ver: ..., q_id="PQ-0051", actor=...)
# target: src/zephyr/governance/meta_question/exam_loop/exam_lifecycle.py (docstring 616 字, 8 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/exam_lifecycle.yaml
"""

from __future__ import annotations

from typing import Any, Callable, Final

from zephyr.governance.meta_question.exam_ops import (
    LEGAL_TRANSITIONS,
    TERMINAL_STATUSES,
    VALID_STATUSES,
    WILDCARD_TARGETS,
    QuestionValidationError,
    VersionConflictError,
)

from . import event_codes
from .ledger import ExamLoopLedger

__all__: Final = ["ANSWERED_STATUS", "ExamLoopStateMachine", "IN_EXAM_STATUS", "REEXAM_STATUS"]

#: 题面语义锚（单值锚非枚举复制；加载后断言在词表内，漂移 fail-closed）
IN_EXAM_STATUS: Final[str] = "in_exam"
ANSWERED_STATUS: Final[str] = "answered"
REEXAM_STATUS: Final[str] = "reexam"
for _anchor in (IN_EXAM_STATUS, ANSWERED_STATUS, REEXAM_STATUS):
    if _anchor not in frozenset(VALID_STATUSES):
        raise ValueError(f"状态词表漂移：锚 {_anchor!r} 不在 VALID_STATUSES（先修词表再改本件）")

#: 冲突重放上限（重读重放同 git rebase，20§3.2；超限上抛由人工/上层处置）
_REPLAY_MAX: Final[int] = 3


class ExamLoopStateMachine:
    """状态机推进拦截器（边断言 + 拒收落账 + 乐观锁重放留痕）。"""

    def __init__(self, ledger: ExamLoopLedger | None = None) -> None:
        self.ledger: Final[ExamLoopLedger] = ledger or ExamLoopLedger()
        self.registry: Final[Any] = self.ledger.registry

    # -- 合法边视图（13§1.5 注册表，供机检/看板消费）-------------------------

    @staticmethod
    def registered_edges() -> dict[str, tuple[str, ...]]:
        """边表机读视图：含通配边展开（任意非终态→merged/retired）。"""
        view: dict[str, list[str]] = {src: sorted(targets) for src, targets in LEGAL_TRANSITIONS.items()}
        for src in LEGAL_TRANSITIONS:
            if src in TERMINAL_STATUSES:
                continue
            view[src] = sorted(set(view[src]) | set(WILDCARD_TARGETS))
        return {src: tuple(targets) for src, targets in view.items()}

    @staticmethod
    def is_legal_edge(from_status: str, to_status: str) -> bool:
        """纯断言（无 IO）：与冻结件 _is_legal_edge 同判据（通配边=任意非终态→终态）。"""
        if to_status in LEGAL_TRANSITIONS.get(from_status, frozenset()):
            return True
        return to_status in WILDCARD_TARGETS and from_status not in TERMINAL_STATUSES

    @staticmethod
    def descendants_of(status: str) -> frozenset[str]:
        """该态之后可达的状态集（含自身）——'in_exam 及以后'类题面的机械口径。"""
        seen: set[str] = {status}
        frontier = [status]
        while frontier:
            current = frontier.pop()
            for nxt in LEGAL_TRANSITIONS.get(current, frozenset()):
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
        return frozenset(seen) | (WILDCARD_TARGETS if status not in TERMINAL_STATUSES else frozenset())

    # -- 流转拦截（13§1.5）-------------------------------------------------

    def transition(self, q_id: str, to_status: str, *, actor: str, evidence: str = "") -> dict[str, Any]:
        """推进状态：合法边→走冻结件三闸；非法边→先落 illegal_transition 痕再上抛。"""
        if to_status not in VALID_STATUSES:
            self.trace_reject(
                q_id, actor, "illegal_transition", evidence, {"reason": "status_invalid", "to_status": to_status}
            )
            raise QuestionValidationError("status_invalid", {"to_status": to_status})
        try:
            return self.registry.transition(q_id, to_status, actor=actor, evidence=evidence)
        except QuestionValidationError as exc:
            code = self._reject_code(exc)
            self.trace_reject(
                q_id,
                actor,
                code,
                evidence,
                {"reason": exc.subcode, "to_status": to_status, **exc.details},
            )
            raise
        except VersionConflictError as exc:
            self.trace_reject(
                q_id,
                actor,
                event_codes.CODE_VERSION_CONFLICT,
                evidence,
                {
                    "reason": "version_conflict",
                    "to_status": to_status,
                    "expected_version": exc.expected_version,
                    "replay_attempt": 0,
                },
            )
            raise

    @staticmethod
    def _reject_code(exc: QuestionValidationError) -> str:
        """拒收 subcode → 落账事件码（在册码直通，其余归 illegal_transition 族痕）。"""
        if exc.subcode in event_codes.extension_codes():
            return exc.subcode
        return event_codes.CODE_ILLEGAL_TRANSITION

    def trace_reject(
        self,
        q_id: str,
        actor: str,
        code: str,
        evidence: str,
        payload: dict[str, Any],
    ) -> None:
        """拒收痕独立事务落账（业务写已回滚，账行必留——否则拦截率分母缺失）。"""
        self.ledger.write_event_standalone(
            code,
            q_id=q_id,
            actor=actor or "unknown",
            after={"rejected": True, **payload},
            evidence=f"exam_loop_reject;{evidence}" if evidence else "exam_loop_reject",
        )

    # -- 乐观锁冲突与重放（20§3.2 / PQ-0061）--------------------------------

    def with_version_replay(
        self,
        write: Callable[[Any, int], Any],
        *,
        q_id: str,
        actor: str,
        evidence: str = "",
        max_replays: int = _REPLAY_MAX,
    ) -> dict[str, Any]:
        """带冲突留痕的重读重放执行器。

        :param write: ``write(cur, expected_version) -> Any``；内部必须用
            ``WHERE q_id=%s AND version=%s`` 条件写（零行命中即抛 :class:`VersionConflictError`）。
        :return: ``{"q_id","replays","succeeded","conflicts":[...]}``（replays=冲突后重放次数）
        """
        conflicts: list[dict[str, Any]] = []
        attempt = 0
        while attempt <= max(int(max_replays), 0):
            conn = self.ledger.conn(read_only=False)
            try:
                cur = conn.cursor()
                row = self.registry._load_row(cur, q_id)
                if row is None:
                    raise QuestionValidationError("qid_not_found", {"q_id": q_id})
                expected = int(row["version"])
                outcome = write(cur, expected)
                conn.commit()
                return {
                    "q_id": q_id,
                    "replays": attempt,
                    "succeeded": True,
                    "conflicts": conflicts,
                    "outcome": outcome,
                    "final_version": expected + 1,
                }
            except VersionConflictError as exc:
                conn.rollback()
                attempt += 1
                conflicts.append({"attempt": attempt, "expected_version": exc.expected_version})
                self.trace_reject(
                    q_id,
                    actor,
                    event_codes.CODE_VERSION_CONFLICT,
                    evidence,
                    {
                        "reason": "version_conflict",
                        "expected_version": exc.expected_version,
                        "replay_attempt": attempt,
                        "replayed": attempt <= int(max_replays),
                    },
                )
                if attempt > int(max_replays):
                    raise
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
