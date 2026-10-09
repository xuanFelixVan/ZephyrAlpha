# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/13_exam_backfill_loop_design.md | §2.1 矛盾可判定式 C1-C3 + §2.2 三取二
# [MODULE] tests.governance.meta_question.test_exam_loop_arbitration
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] conftest 夹具 env/mq; zephyr.governance.meta_question.exam_loop.arbitration（纯计算）/writeback（端到端案卷链）
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 红腿：①版本不同的两次考试绝不比（方案修订≠矛盾）②同窗交叠绝不比（补录≠矛盾）
#                ③三取二归属不可判（R3 与两侧均矛盾 / 均不命中 / R3 不可判）必升级 Max，禁静默终裁；
#              蓝腿：C1/C2/C3 逐条命中 + R3 与 R1 同侧胜出转 answered + 案卷 open→resolved 无死态
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=测试红
# [TESTS] self
# [TTL] task_bound
"""矛盾检测与三取二仲裁测试（PQ-0057 载体，红蓝成对）。"""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.governance.meta_question.exam_loop import arbitration
from zephyr.governance.meta_question.exam_loop.writeback import QuestionValidationError

# 同文 SQL 逐处独立常量：对拍尺按多重集计数，共用常量会使字面量 2→1 判 RED
SQL_SELECT_STATUS_AFTER_R3_RESOLVE = "SELECT status FROM main.meta_question WHERE q_id=?"
SQL_SELECT_STATUS_AFTER_ESCALATE_MAX = "SELECT status FROM main.meta_question WHERE q_id=?"


def _plan(mq: SimpleNamespace, **over: Any) -> dict[str, Any]:
    plan = mq.structured_plan(**over)
    # 与 writeback 同口径：plan_version 来自回填载荷（版本闸的前提），阈值条款机解投影
    return {
        **plan,
        "plan_version": "v1",
        "threshold_used": None,
        "threshold_clauses": [{"op": ">=", "value": 0.02, "primary": True}, {"op": ">=", "value": 0.02}],
    }


def _row(dirn: str, value: float, *, lo: float, hi: float, conf: float = 95.0) -> dict[str, Any]:
    return {
        "conclusion": {"value": value, "dir": dirn},
        "confidence": {"level": conf, "ci_lo": lo, "ci_hi": hi},
        "data_window": {"start": "2024-01-01", "end": "2024-06-30", "exam_plan_version": "v1"},
        "outcome": "answered",
        "created_at": "2024-07-01T00:00:00+00:00",
    }


def _current(mq: SimpleNamespace, dirn: str, value: float, *, lo: float, hi: float) -> dict[str, Any]:
    return mq.exam_payload(
        conclusion_dir=dirn,
        conclusion_value=value,
        ci_lo=lo,
        ci_hi=hi,
        data_window={
            "start": "2025-01-01",
            "end": "2025-06-30",
            "fetch_ts": (mq.now_utc() - timedelta(hours=8)).isoformat(),
            "decision_ts": (mq.now_utc() - timedelta(hours=7)).isoformat(),
        },
        exam_plan_version="v1",
    )


class TestRuleHits:
    def test_c1_direction_flip(self, mq: SimpleNamespace) -> None:
        case = arbitration.detect_contradiction(
            _plan(mq), _current(mq, "证伪", -0.03, lo=-0.05, hi=-0.01), [_row("支持", 0.03, lo=0.01, hi=0.05)]
        )
        assert case and "C1" in case["rules"] and case["state"] == "open"

    def test_c2_disjoint_intervals(self, mq: SimpleNamespace) -> None:
        hits = arbitration.hits_c2(
            {"dir": "支持", "ci_lo": 0.10, "ci_hi": 0.20}, {"dir": "证伪", "ci_lo": -0.20, "ci_hi": -0.10}
        )
        assert hits is True
        assert (
            arbitration.hits_c2(
                {"dir": "支持", "ci_lo": 0.0, "ci_hi": 0.2}, {"dir": "证伪", "ci_lo": 0.1, "ci_hi": 0.3}
            )
            is False
        )

    def test_c3_threshold_opposite_sides(self, mq: SimpleNamespace) -> None:
        assert (
            arbitration.hits_c3({"value": 0.05, "dir": "支持"}, {"value": 0.001, "dir": "支持"}, threshold=0.02) is True
        )
        assert arbitration.hits_c3({"value": 0.05}, {"value": 0.04}, threshold=0.02) is False


class TestGating:
    def test_different_plan_version_never_compared(self, mq: SimpleNamespace) -> None:
        """红腿：版本不同=方案修订，不入矛盾检测。"""
        prior = [_row("证伪", -0.03, lo=-0.05, hi=-0.01)]
        prior[0]["data_window"] = {**prior[0]["data_window"], "exam_plan_version": "v9"}
        assert arbitration.detect_contradiction(_plan(mq), _current(mq, "支持", 0.03, lo=0.01, hi=0.05), prior) is None

    def test_overlapping_window_is_supplement(self, mq: SimpleNamespace) -> None:
        """红腿：窗口交叠的重复回写=补录，不触发伪仲裁。"""
        prior = [_row("证伪", -0.03, lo=-0.05, hi=-0.01)]
        prior[0]["data_window"] = {**prior[0]["data_window"], "start": "2024-01-01", "end": "2025-06-30"}
        assert arbitration.detect_contradiction(_plan(mq), _current(mq, "支持", 0.03, lo=0.01, hi=0.05), prior) is None

    def test_confidence_below_prelock_blocks_c1(self, mq: SimpleNamespace) -> None:
        assert (
            arbitration.hits_c1(
                {"dir": "支持", "confidence": 80.0}, {"dir": "证伪", "confidence": 90.0}, min_confidence=95.0
            )
            is False
        )


class TestMajority:
    def test_r3_agrees_with_r1_wins(self, mq: SimpleNamespace) -> None:
        r2 = _row("证伪", -0.03, lo=-0.05, hi=-0.01)
        r1 = _row("支持", 0.03, lo=0.01, hi=0.05)
        verdict = arbitration.resolve_majority(
            _plan(mq),
            _current(mq, "支持", 0.031, lo=0.01, hi=0.05),
            [r2, r1],
            {"case_id": "MQC-X"},
            arbitration_recheck=True,
        )
        assert verdict["verdict"] == "majority" and verdict["winner"] == "R1"

    def test_r3_conflicts_with_both_escalates(self, mq: SimpleNamespace) -> None:
        r2 = _row("证伪", -0.03, lo=-0.05, hi=-0.01)
        r1 = _row("支持", 0.03, lo=0.01, hi=0.05)
        odd = _current(mq, "支持", -0.04, lo=-0.06, hi=-0.02)  # 与两侧都异侧
        verdict = arbitration.resolve_majority(_plan(mq), odd, [r2, r1], {"case_id": "MQC-Y"}, arbitration_recheck=True)
        assert verdict["verdict"] == "escalate_max" and verdict["winner"] is None

    def test_indeterminate_r3_escalates(self, mq: SimpleNamespace) -> None:
        verdict = arbitration.resolve_majority(
            _plan(mq),
            _current(mq, "不可判", 0.0, lo=-0.01, hi=0.01),
            [_row("证伪", -0.03, lo=-0.05, hi=-0.01), _row("支持", 0.03, lo=0.01, hi=0.05)],
            {"case_id": "MQC-Z"},
            arbitration_recheck=True,
        )
        assert verdict["verdict"] == "escalate_max"

    def test_recheck_flag_required(self, mq: SimpleNamespace) -> None:
        """非复考轮次不做终裁（禁把普通回填当仲裁用）。"""
        assert (
            arbitration.resolve_majority(
                _plan(mq),
                _current(mq, "支持", 0.03, lo=0.01, hi=0.05),
                [_row("证伪", -0.03, lo=-0.05, hi=-0.01), _row("支持", 0.03, lo=0.01, hi=0.05)],
                None,
                arbitration_recheck=False,
            )
            is None
        )


class TestEndToEndArbitration:
    """案卷全链（13§2.2 四步）：R1 支持→R2 证伪矛盾开案转复考→新考被闸拒→R3 三取二胜出转 answered。"""

    def _window(self, mq: SimpleNamespace, start: str, end: str, hours_ago: int) -> dict[str, Any]:
        return {
            "start": start,
            "end": end,
            "fetch_ts": (mq.now_utc() - timedelta(hours=hours_ago + 1)).isoformat(),
            "decision_ts": (mq.now_utc() - timedelta(hours=hours_ago)).isoformat(),
        }

    def test_contradiction_blocks_new_exam_then_r3_resolves(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        env, q_id = claimed["env"], claimed["q_id"]
        registry, wb = env["registry"], env["wb"]
        wb.writeback(q_id, mq.exam_payload(exam_ref="R1"), session_id=mq.SESSION)  # in_exam→answered（支持）
        registry.transition(q_id, "reexam", actor=mq.SESSION, evidence="盘到新鲜窗到期")  # answered→复考
        r2 = mq.exam_payload(
            exam_ref="R2",
            conclusion_dir="证伪",
            conclusion_value=-0.03,
            ci_lo=-0.05,
            ci_hi=-0.01,
            data_window=self._window(mq, "2025-01-01", "2025-06-30", 9),
        )
        second = wb.writeback(q_id, r2, session_id=mq.SESSION)
        assert second["outcome"] == "reexam", "矛盾命中必转复考（不得就地 answered）"
        assert second["contradiction"] and second["contradiction"]["state"] == "open"
        rows = [r for r in mq.audit_rows(env, q_id) if r["what"] == "exam_contradiction_case"]
        assert len(rows) == 1 and rows[0]["after"]["state"] == "open"
        with pytest.raises(QuestionValidationError) as ei:
            wb.writeback(q_id, mq.exam_payload(exam_ref="抢跑考"), session_id=mq.SESSION)
        assert ei.value.subcode == "arbitration_open"  # 13§2.2 仲裁期间禁发新考
        r3 = mq.exam_payload(
            exam_ref="R3",
            arbitration_recheck=True,
            data_window=self._window(mq, "2025-07-01", "2025-12-31", 4),
        )
        third = wb.writeback(q_id, r3, session_id=mq.SESSION)
        assert third["arbitration"] and third["arbitration"]["verdict"] == "majority"
        assert third["arbitration"]["winner"] == "R1"
        assert third["outcome"] == "answered"
        closed = [r for r in mq.audit_rows(env, q_id) if r["what"] == "exam_contradiction_case"]
        assert any(r["after"].get("state") == "resolved" for r in closed), "案卷必闭合（无死态）"
        arbitrate = [r for r in mq.audit_rows(env, q_id) if r["what"] == "exam_arbitrate"]
        assert len(arbitrate) == 1, "三取二必落 exam_arbitrate 账（PQ-0057 判据分子）"
        status = env["raw"].execute(SQL_SELECT_STATUS_AFTER_R3_RESOLVE, (q_id,)).fetchone()[0]
        assert status == "answered"

    def test_escalate_max_keeps_reexam_state(self, claimed: dict[str, Any], mq: SimpleNamespace) -> None:
        """红腿：R3 与两侧都矛盾⇒升级 Max，状态保持复考（禁静默终裁）。"""
        env, q_id = claimed["env"], claimed["q_id"]
        registry, wb = env["registry"], env["wb"]
        wb.writeback(q_id, mq.exam_payload(exam_ref="R1"), session_id=mq.SESSION)
        registry.transition(q_id, "reexam", actor=mq.SESSION)
        wb.writeback(
            q_id,
            mq.exam_payload(
                exam_ref="R2",
                conclusion_dir="证伪",
                conclusion_value=-0.03,
                ci_lo=-0.05,
                ci_hi=-0.01,
                data_window=self._window(mq, "2025-01-01", "2025-06-30", 9),
            ),
            session_id=mq.SESSION,
        )
        # R3 与 R1 阈值异侧（C3）、与 R2 方向相反（C1）⇒ 两侧都矛盾=归属不可判→升级 Max
        odd = mq.exam_payload(
            exam_ref="R3",
            arbitration_recheck=True,
            conclusion_dir="支持",
            conclusion_value=0.001,
            ci_lo=0.0,
            ci_hi=0.002,
            data_window=self._window(mq, "2025-07-01", "2025-12-31", 4),
        )
        third = wb.writeback(q_id, odd, session_id=mq.SESSION)
        assert third["arbitration"]["verdict"] == "escalate_max"
        assert third["outcome"] == "reexam"
        status = env["raw"].execute(SQL_SELECT_STATUS_AFTER_ESCALATE_MAX, (q_id,)).fetchone()[0]
        assert status == "reexam"
