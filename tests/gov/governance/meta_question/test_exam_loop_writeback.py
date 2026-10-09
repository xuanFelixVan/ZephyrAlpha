# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §1 回写契约（鉴权/双时戳/六查/证据）
# [MODULE] tests.governance.meta_question.test_exam_loop_writeback
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] conftest 夹具 env/mq/claimed; zephyr.governance.meta_question.exam_loop.writeback/event_codes
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 红腿（PQ-0103/0096/0098/0055/0056 的"能红"自证）：
#                ①无认领回写必拒并落 claim_missing 痕；②冒名会话回写必拒并落 claim_mismatch 痕；
#                ③时戳倒挂必拒（exam_completed_at > backfilled_at）；④申报阈值低于预锁必落 threshold_lowered 且强制延期；
#                ⑤证据不可核（外部 URL/未 promote 临时路径）必降级挂起且缺 suspend_reason 即拒；
#              蓝腿：合规回填真跑通——双时戳落账 + 时延可算 + exam_result 行 + 主表 status/last_exam/version 推进 + 同窗重复标 supplement
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红；拒收路径必须"账留、写回滚"（本测试双向核验）
# [TESTS] self
# [TTL] task_bound
"""writeback 唯一合法入口测试（鉴权/双时戳/六查/降阈值/补录，红蓝成对）。"""

from __future__ import annotations

import json
from datetime import timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.governance.meta_question.exam_loop import event_codes
from zephyr.governance.meta_question.exam_loop.writeback import (
    ExamLoopWriteback,
    QuestionValidationError,
    evidence_resolvable,
    six_check,
)

# 同文 SQL 逐处独立常量：对拍尺按多重集计数，共用常量会使字面量条数缩减判 RED
SQL_SELECT_STATUS_LAST_EXAM_VERSION_BY_QID = "SELECT status, last_exam, version FROM main.meta_question WHERE q_id=?"
SQL_SELECT_EXAM_RESULT_BY_QID = (
    "SELECT outcome, conclusion, confidence, data_window FROM main.meta_question_exam_result WHERE q_id=?"
)
SQL_SELECT_STATUS_AFTER_CLAIM_REFUSE = "SELECT status FROM main.meta_question WHERE q_id=?"
SQL_COUNT_EXAM_RESULT = "SELECT COUNT(*) FROM main.meta_question_exam_result"
SQL_SET_CLAIMED_UNTIL_BY_QID = "UPDATE main.meta_question SET claimed_until=? WHERE q_id=?"
SQL_SELECT_STATUS_AFTER_THRESHOLD_DEFER = "SELECT status FROM main.meta_question WHERE q_id=?"


class TestHappyPath:
    def test_answered_lands_dual_timestamps_and_rows(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """蓝腿：in_exam→answered 真跑通，双时戳与落账时延入 exam_writeback 审计载荷。"""
        env, q_id = claimed["env"], claimed["q_id"]
        payload = mq.exam_payload(exam_completed_at=(mq.now_utc() - timedelta(minutes=42)).isoformat())
        receipt = env["wb"].writeback(q_id, payload, session_id=mq.SESSION)
        assert receipt["outcome"] == "answered" and receipt["six_check"]["passed"] is True
        assert receipt["version_after"] == receipt["version_before"] + 1
        row = env["raw"].execute(SQL_SELECT_STATUS_LAST_EXAM_VERSION_BY_QID, (q_id,)).fetchone()
        assert row[0] == "answered" and row[1] and row[2] == receipt["version_after"]
        result = env["raw"].execute(SQL_SELECT_EXAM_RESULT_BY_QID, (q_id,)).fetchone()
        assert result[0] == "answered"
        confidence = json.loads(result[2])
        assert confidence["exam_completed_at"] and confidence["backfilled_at"]
        assert confidence["exam_completed_at"] <= confidence["backfilled_at"]
        checks = json.loads(result[1])["checks"]
        assert all(checks[key]["ok"] for key in ("A1", "A2", "A3", "A4", "A5", "A6"))
        events = [r for r in mq.audit_rows(env, q_id) if r["what"] == "exam_writeback"]
        assert events, "exam_writeback 事件必落账（PQ-0056 载体）"
        after = events[-1]["after"]
        assert {"exam_completed_at", "backfilled_at", "latency_seconds"} <= set(after)
        assert 0 < after["latency_seconds"] < 3600 * 24

    def test_same_window_rewrite_is_supplement_not_contradiction(
        self, claimed: dict[str, Any], mq: SimpleNamespace
    ) -> None:
        """蓝腿：同版本同窗重复回写标 supplement，不触发矛盾案卷（13§2.1 防伪仲裁）。"""
        env, q_id, registry = claimed["env"], claimed["q_id"], claimed["env"]["registry"]
        env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)
        registry.transition(q_id, "reexam", actor=mq.SESSION, evidence="盘逾期")
        second = env["wb"].writeback(q_id, mq.exam_payload(exam_ref="wo-b1/probe/supplement"), session_id=mq.SESSION)
        assert second["supplements"] >= 1
        assert second["contradiction"] is None
        cases = [r for r in mq.audit_rows(env, q_id) if r["what"] == "exam_contradiction_case"]
        assert cases == []


class TestAuthRed:
    def test_unclaimed_writeback_refused_and_traced(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿①（PQ-0103）：无活跃认领的回写=claim_missing（临时通道直写的口子在此封死）。"""
        registry = env["registry"]
        q_id = registry.register(mq.question(title="无认领回写验证问"), actor=mq.SESSION)
        registry.transition(q_id, "mining", actor=mq.SESSION)
        registry.transition(q_id, "in_exam", actor=mq.SESSION)
        with pytest.raises(QuestionValidationError) as ei:
            env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)
        assert ei.value.subcode == "claim_missing"
        assert mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_CLAIM_MISSING)
        status = env["raw"].execute(SQL_SELECT_STATUS_AFTER_CLAIM_REFUSE, (q_id,)).fetchone()[0]
        assert status == "in_exam"  # 拒收零业务写，但痕已留

    def test_impostor_session_refused_and_traced(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿②：他人会话冒名回写=claim_mismatch（越权必留痕）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        with pytest.raises(QuestionValidationError) as ei:
            env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.IMPOSTOR)
        assert ei.value.subcode == "claim_mismatch"
        hits = mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_CLAIM_MISMATCH)
        assert len(hits) == 1 and hits[0]["after"]["rejected"] is True
        assert env["raw"].execute(SQL_COUNT_EXAM_RESULT).fetchone()[0] == 0

    def test_max_role_bypasses_claim(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """蓝腿对照：Max/Owner 角色段可越过认领（10§7.4①，防把合规复核也拦死）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        receipt = env["wb"].writeback(q_id, mq.exam_payload(), session_id="Max")
        assert receipt["outcome"] == "answered"

    def test_expired_lease_is_not_active_claim(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """租约过期视同无活跃认领→claim_missing（认领协议 12§2.1 与鉴权口径一致）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        env["raw"].execute(SQL_SET_CLAIMED_UNTIL_BY_QID, ("2020-01-01 00:00:00+00:00", q_id))
        env["raw"].commit()
        with pytest.raises(QuestionValidationError) as ei:
            env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.SESSION)
        assert ei.value.subcode == "claim_missing"


class TestSixCheckRed:
    def test_timestamp_inversion_refused(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿③：考试完成时戳晚于回填时戳=尺子失真，直接拒（不进事务）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        future = (mq.now_utc() + timedelta(days=3)).isoformat()
        with pytest.raises(ValueError):
            env["wb"].writeback(q_id, mq.exam_payload(exam_completed_at=future), session_id=mq.SESSION)

    def test_missing_completed_stamp_refused(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        env, q_id = claimed["env"], claimed["q_id"]
        with pytest.raises(ValueError):
            env["wb"].writeback(q_id, mq.exam_payload(exam_completed_at=None), session_id=mq.SESSION)

    def test_threshold_lowering_forces_defer(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿④（PQ-0098）：申报阈值低于预锁→落 threshold_lowered 痕且强制延期（outcome=reexam）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        receipt = env["wb"].writeback(q_id, mq.exam_payload(threshold_used=0.001), session_id=mq.SESSION)
        assert receipt["outcome"] == "reexam"
        assert "threshold_lowered" in receipt["deferred_reason"]
        hits = mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_THRESHOLD_LOWERED)
        assert len(hits) == 1 and hits[0]["after"]["action"] == "force_defer"
        status = env["raw"].execute(SQL_SELECT_STATUS_AFTER_THRESHOLD_DEFER, (q_id,)).fetchone()[0]
        assert status == "reexam"

    def test_low_power_defers_instead_of_lowering(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿④对照：样本不足/效应量小→defer（唯一出口），不得以降阈值凑通过。"""
        env, q_id = claimed["env"], claimed["q_id"]
        receipt = env["wb"].writeback(q_id, mq.exam_payload(sample_size=40, effect_size=0.05), session_id=mq.SESSION)
        assert receipt["outcome"] == "reexam" and "low_power_defer" in receipt["deferred_reason"]

    def test_unresolvable_evidence_downgrades_to_suspend(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿⑤：证据仅外部 URL/未 promote 临时路径→A6 失败→挂起（13§1.3）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        receipt = env["wb"].writeback(
            q_id,
            mq.exam_payload(
                evidence_refs=[
                    "https://example.com/结论截图.png",
                    ".runtime/tmp/not_promoted.json",
                ],
                suspend_reason="证据不可核：外链与未 promote 临时件",
            ),
            session_id=mq.SESSION,
        )
        assert receipt["outcome"] == "suspended"
        assert receipt["six_check"]["A6"]["ok"] is False

    def test_suspend_without_reason_refused(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        env, q_id = claimed["env"], claimed["q_id"]
        with pytest.raises(QuestionValidationError) as ei:
            env["wb"].writeback(q_id, mq.exam_payload(evidence_refs=[], suspend_reason=None), session_id=mq.SESSION)
        assert ei.value.subcode == "six_check_failed"

    def test_naive_dual_timestamp_refused(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿（PQ-0096）：取数/决策时戳缺时区=naive，必拒（RULE-SCHEMA-TZ 在执行侧的等价红线）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        bad = mq.exam_payload()
        bad["data_window"]["fetch_ts"] = bad["data_window"]["fetch_ts"].replace("+00:00", "")
        with pytest.raises(ValueError):
            env["wb"].writeback(q_id, bad, session_id=mq.SESSION)

    def test_fetch_after_decision_violates_pit(self, mq: SimpleNamespace) -> None:
        """红腿（PQ-0096 判据本体）：取数时戳晚于决策时戳=A5 违例，不得 answered。"""
        row = {"provenance": {"registered_at": "2020-01-01T00:00:00+00:00"}}
        payload = mq.exam_payload()
        window = dict(payload["data_window"])
        window["fetch_ts"], window["decision_ts"] = window["decision_ts"], window["fetch_ts"]
        result = six_check(row, mq.structured_plan(), {**payload, "data_window": window})
        assert result["A5"]["ok"] is False and result["passed"] is False

    def test_identical_timestamps_violate_layering(self, mq: SimpleNamespace) -> None:
        """红腿（13§3.3 第 2 条）：取数与决策同一时戳=同一时戳禁循环。"""
        row = {"provenance": {"registered_at": "2020-01-01T00:00:00+00:00"}}
        payload = mq.exam_payload()
        same = payload["data_window"]["decision_ts"]
        result = six_check(
            row, mq.structured_plan(), {**payload, "data_window": {**payload["data_window"], "fetch_ts": same}}
        )
        assert result["A5"]["ok"] is False

    def test_pure_six_check_flags_each_failure(self, mq: SimpleNamespace) -> None:
        """纯函数级红腿：逐项破坏必逐项报（防"整单绿"的静默成功尺）。"""
        row = {"provenance": {"registered_at": "2020-01-01T00:00:00+00:00"}}
        plan = mq.structured_plan()
        base = mq.exam_payload()
        assert six_check(row, plan, base)["passed"] is True
        assert six_check(row, plan, {**base, "conclusion_dir": "不可判"})["A1"]["ok"] is False
        assert six_check(row, {**plan, "min_confidence": 99.9}, base)["A2"]["ok"] is False
        assert (
            six_check(
                row, plan, {**base, "data_window": {**base["data_window"], "end": mq.now_utc().date().isoformat()}}
            )["A4"]["ok"]
            is False
        )
        assert six_check(row, plan, {**base, "pit_assertion": ""})["A5"]["ok"] is False
        assert six_check(row, plan, {**base, "evidence_refs": []})["A6"]["ok"] is False


class TestRulerCanGoRed:
    """变异自证：把守卫拆掉，红腿断言必须失效（否则该尺是静默成功尺——上一班四次死亡的教训）。"""

    def test_disabling_auth_makes_forgery_pass(
        self, claimed: dict[str, Any], mq: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env, q_id = claimed["env"], claimed["q_id"]
        monkeypatch.setattr(type(env["wb"]), "_authorize", lambda *a, **k: None)
        receipt = env["wb"].writeback(q_id, mq.exam_payload(), session_id=mq.IMPOSTOR)
        assert receipt["outcome"] == "answered", "拆掉鉴权后冒名回写必须成功——反证红腿②判据真的在拦"

    def test_disabling_trace_makes_illegal_edge_invisible(
        self, claimed: dict[str, Any], mq: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """拆掉落痕后：非法流转照旧被拒（registry 边表），但痕消失⇒"拦截率分母"确实依赖本件落痕。"""
        env, q_id = claimed["env"], claimed["q_id"]
        env["wb"].writeback(q_id, mq.exam_payload(exam_ref="R1"), session_id=mq.SESSION)  # in_exam→answered
        monkeypatch.setattr(env["sm"], "trace_reject", lambda *a, **k: None)
        with pytest.raises(QuestionValidationError):
            env["wb"].writeback(q_id, mq.exam_payload(exam_ref="R2"), session_id=mq.SESSION)  # answered→answered 非法
        assert mq.event_code_hits(mq.audit_rows(env, q_id), event_codes.CODE_ILLEGAL_TRANSITION) == []


class TestEvidenceResolvable:
    def test_external_and_temp_paths_rejected(self, tmp_path: Any) -> None:
        assert evidence_resolvable("https://x.com/a") is False
        assert evidence_resolvable(".runtime/tmp/abc.json") is False
        assert evidence_resolvable({"table": "t", "query": "SELECT 1"}) is True
        assert evidence_resolvable({"path": "AGENTS.md"}) is True  # 仓内实存文件可核
        assert evidence_resolvable({"path": "nope/does_not_exist.md"}) is False


# ---------------------------------------------------------------------------
# 落库形态契约（2026-09-24 总包回归追加）：exam_loop 曾把 conclusion 写成只含
# 新增字段、缺规范 outcome/evidence/... 11 键的形态，令 4 问从三态读出中消失。
# 本组用例是该事故的永久红证——缺任一规范键即红。
# ---------------------------------------------------------------------------

_CONCLUSION_CANONICAL_KEYS = {
    "outcome",
    "conclusion",
    "evidence",
    "fail_type",
    "confidence",
    "data_window",
    "exam_ref",
    "pit_assertion",
    "three_check",
    "notes",
    "threshold",
}


def test_conclusion_block_carries_all_canonical_keys():
    """缺规范键必须红——全仓按 conclusion->>'outcome' 取裁决。"""
    block = ExamLoopWriteback._conclusion_block(
        {"verdict": "pass", "evidence": [{"probe": "p"}], "notes": "n", "exam_ref": "r", "confidence_level": 0.8},
        {"criterion": "c", "threshold": "t"},
        {"A1": True, "passed": True},
    )
    missing = _CONCLUSION_CANONICAL_KEYS - set(block)
    assert not missing, f"conclusion 缺规范键：{sorted(missing)}"
    assert block["outcome"] == "pass", "裁决未落到 outcome 键"


def test_conclusion_block_keeps_design_additions_too():
    """补规范键不得吃掉 13 号设计新增字段（两侧都要在）。"""
    block = ExamLoopWriteback._conclusion_block(
        {
            "verdict": "fail",
            "conclusion_value": 0.4,
            "conclusion_dir": "-",
            "sample_size": 120,
            "effect_size": 0.03,
            "threshold_used": "0.02",
        },
        {"criterion": "c", "threshold": "t", "degraded": ["d1"]},
        {"A1": False, "A2": True, "passed": False},
    )
    for k in ("value", "dir", "criterion", "threshold_used", "sample_size", "effect_size", "degraded", "checks"):
        assert k in block, f"设计新增字段丢失：{k}"
    assert block["checks"] == {"A1": False, "A2": True}
