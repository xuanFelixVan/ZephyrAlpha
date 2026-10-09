# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1.5 状态流转机械判定 + §2.2 冲突与仲裁
# [MODULE] tests.governance.meta_question.test_exam_loop_state_machine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] conftest 夹具 env/mq; zephyr.governance.meta_question.exam_loop.exam_lifecycle; zephyr.governance.meta_question.exam_ops (异常族/边表真源)
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 蓝腿=registered→mining→in_exam→answered 全链真跑通（含 status/version 落地复核）；
#              红腿=①非法边必抛 illegal_transition 且拒收痕独立事务落账（主表状态零漂移）
#                    ②版本冲突必落 version_conflict 痕并按上限重放（重放成功计数可核）
#                    ③变异自证：注入恒不冲突写时红腿断言必须失效（防静默成功尺）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红
# [TESTS] self
# [TTL] task_bound
"""状态机拦截器测试（红蓝双腿：非法边落痕 + 合法链跑通 + 冲突重放留痕）。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.governance.meta_question.exam_loop import event_codes
from zephyr.governance.meta_question.exam_loop.exam_lifecycle import ExamLoopStateMachine
from zephyr.governance.meta_question.exam_ops import (
    QuestionValidationError,
    VersionConflictError,
)

SQL_SELECT_STATUS_BY_QID = "SELECT status FROM main.meta_question WHERE q_id=?"
SQL_SELECT_STATUS_VERSION_BY_QID = "SELECT status, version FROM main.meta_question WHERE q_id=?"
SQL_BUMP_UPDATED_AT_BY_QID_AND_VERSION = (
    "UPDATE main.meta_question SET updated_at=%s, version=version+1 WHERE q_id=%s AND version=%s"
)


class TestLegalChain:
    def test_registered_to_in_exam_to_answered_full_chain(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """蓝腿：全链推进（registered→mining→in_exam→answered）逐态复核。"""
        registry, sm = env["registry"], env["sm"]
        q_id = registry.register(mq.question(), actor=mq.SESSION)
        sm.transition(q_id, "mining", actor=mq.SESSION, evidence="开工")
        sm.transition(q_id, "in_exam", actor=mq.SESSION, evidence="开考")
        registry.claim(q_id, mq.SESSION, lease_hours=24)
        env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)
        cur = env["raw"].execute(SQL_SELECT_STATUS_VERSION_BY_QID, (q_id,))
        status, version = cur.fetchone()
        assert status == "answered", f"全链未跑通：status={status}"
        assert version >= 4

    def test_edge_view_is_derived_not_hardcoded(self, mq: SimpleNamespace) -> None:
        """边表视图由词表派生（in_exam 之后状态集必含 answered/reexam 且不含终态出边）。"""
        after = ExamLoopStateMachine.descendants_of("in_exam")
        assert {"answered", "reexam", "suspended"} <= after
        assert ExamLoopStateMachine.registered_edges()["answered"]
        assert ExamLoopStateMachine.registered_edges()["merged"] == ()


class TestIllegalTransitionRed:
    def test_illegal_edge_rejected_and_traced(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿①：registered→answered 非法边→抛 illegal_transition + 拒收痕落账 + 主表零漂移。"""
        registry, sm = env["registry"], env["sm"]
        q_id = registry.register(mq.question(title="非法流转验证问"), actor=mq.SESSION)
        with pytest.raises(QuestionValidationError) as ei:
            sm.transition(q_id, "answered", actor=mq.SESSION, evidence="伪造直答")
        assert ei.value.subcode == "illegal_transition"
        hits = mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_ILLEGAL_TRANSITION)
        assert hits, "非法边必须落痕（零痕=拦截率无从复考）"
        assert hits[0]["after"]["rejected"] is True
        status = env["raw"].execute(SQL_SELECT_STATUS_BY_QID, (q_id,)).fetchone()[0]
        assert status == "registered"  # 拒收不改状态，但账已留

    def test_mutation_probe_trace_actually_depends_on_reject(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿①变异自证：合法边不得产生 illegal_transition 痕（否则该尺恒红/恒绿皆失真）。"""
        registry, sm = env["registry"], env["sm"]
        q_id = registry.register(mq.question(title="合法边对照问"), actor=mq.SESSION)
        sm.transition(q_id, "mining", actor=mq.SESSION)
        assert mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_ILLEGAL_TRANSITION) == []

    def test_writeback_state_mismatch_traced(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿②：in_exam 态发 outcome=reexam 之外的非法组合（answered 后重发 answered）必落痕。"""
        env, q_id = claimed["env"], claimed["q_id"]
        env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)  # in_exam→answered
        with pytest.raises(QuestionValidationError) as ei:
            env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)  # answered→answered 非法
        assert ei.value.subcode == "status_invalid"
        assert mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_ILLEGAL_TRANSITION)


class TestRulerCanGoRed:
    def test_disabling_interceptor_loses_the_trace(
        self, env: dict[str, Any], mq: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """变异自证：拦截器落痕被拆时，illegal_transition 计数归零⇒上游"零痕=无从复考"判断为真。"""
        monkeypatch.setattr(env["sm"], "trace_reject", lambda *a, **k: None)
        q_id = env["registry"].register(mq.question(title="拆痕对照问"), actor=mq.SESSION)
        with pytest.raises(QuestionValidationError):
            env["sm"].transition(q_id, "answered", actor=mq.SESSION)
        assert mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_ILLEGAL_TRANSITION) == []


class TestVersionConflictReplay:
    def test_conflict_traced_then_replay_succeeds(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红蓝合测：首轮条件写故意用旧版本→零行命中→version_conflict 痕→重放成功。"""
        env, q_id, sm = claimed["env"], claimed["q_id"], claimed["env"]["sm"]
        state = {"calls": 0}

        def write(cur: Any, expected_version: int) -> str:
            state["calls"] += 1
            use = expected_version - 1 if state["calls"] == 1 else expected_version  # 首轮模拟陈旧快照
            cur.execute(SQL_BUMP_UPDATED_AT_BY_QID_AND_VERSION, (mq.now_utc(), q_id, use))
            if cur.rowcount != 1:
                raise VersionConflictError(q_id, use)
            return "written"

        receipt = sm.with_version_replay(write, q_id=q_id, actor=mq.SESSION, evidence="重放自测")
        assert receipt["replays"] == 1 and receipt["succeeded"] is True
        hits = mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_VERSION_CONFLICT)
        assert len(hits) == 1 and hits[0]["after"]["replayed"] is True

    def test_replay_limit_exceeded_raises(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """重放有上限：恒冲突→超限上抛（禁无限重试活锁）。"""
        env, q_id, sm = claimed["env"], claimed["q_id"], claimed["env"]["sm"]

        def always_conflict(cur: Any, expected_version: int) -> str:
            raise VersionConflictError(q_id, expected_version)

        with pytest.raises(VersionConflictError):
            sm.with_version_replay(always_conflict, q_id=q_id, actor=mq.SESSION, max_replays=1)
        assert len(mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_VERSION_CONFLICT)) >= 2
