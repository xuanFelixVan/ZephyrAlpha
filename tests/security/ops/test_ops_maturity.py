# [BLUEPRINT] MOD-INF-055 | docs/03_modules/MOD-INF-055/
# [MODULE] tests.security.ops.test_ops_maturity
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/security/ops/test_ops_maturity.py -q
# [TTL] permanent

"""自治运维成熟度 A-L0→A-L2 状态机（MOD-INF-055）测试。

验收对照（16号文 §4.4 P2-2）：
- 事件流只记录（A-L0）→ 告警（A-L1）→ 自愈建议（A-L2）逐级上线；
- 每级解锁有连续 N 周零 TNR 违规记录，解锁判定留痕（批准与拒绝均留痕）；
- A-L2 状态下人工采纳率留痕；
- A-L3 不在本件范围（请求 MUST 拒绝）。

DB/网络全 mock：状态与台账落盘路径指向 tmp_path。
"""

from __future__ import annotations

import json

import pytest

from zephyr.security.ops.ops_maturity import (
    MaturityConfig,
    OpsMaturityError,
    OpsMaturityLevel,
    OpsMaturityTracker,
    UnlockEvidence,
)


def _tracker(tmp_path, *, required_weeks: int = 2) -> OpsMaturityTracker:
    config = MaturityConfig(
        state_path=tmp_path / "maturity_state.json",
        ledger_path=tmp_path / "maturity_ledger.jsonl",
        required_weeks_zero_tnr=required_weeks,
    )
    return OpsMaturityTracker(config)


def _read_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


class TestInitialState:
    def test_initial_level_is_a_l0(self, tmp_path):
        tracker = _tracker(tmp_path)
        assert tracker.current_level() is OpsMaturityLevel.A_L0
        assert tracker.weeks_zero_tnr_streak() == 0


class TestUnlock:
    def test_unlock_a_l1_with_sufficient_zero_tnr_weeks(self, tmp_path):
        tracker = _tracker(tmp_path, required_weeks=2)
        decision = tracker.request_unlock(
            OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=2, note="连续2周零TNR违规")
        )
        assert decision.approved
        assert tracker.current_level() is OpsMaturityLevel.A_L1
        state = json.loads((tmp_path / "maturity_state.json").read_text(encoding="utf-8"))
        assert state["level"] == "A-L1", "解锁后状态 MUST 持久化"

    def test_unlock_denied_when_weeks_insufficient(self, tmp_path):
        tracker = _tracker(tmp_path, required_weeks=2)
        decision = tracker.request_unlock(OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=1))
        assert not decision.approved
        assert tracker.current_level() is OpsMaturityLevel.A_L0

    def test_unlock_decisions_audited(self, tmp_path):
        tracker = _tracker(tmp_path, required_weeks=2)
        tracker.request_unlock(OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=1))
        tracker.request_unlock(OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=3))
        entries = _read_jsonl(tmp_path / "maturity_ledger.jsonl")
        decisions = [e for e in entries if e["kind"] == "unlock_decision"]
        assert len(decisions) == 2, "解锁判定（批准与拒绝）MUST 全部留痕"
        assert decisions[0]["approved"] is False
        assert decisions[1]["approved"] is True

    def test_no_skip_unlock(self, tmp_path):
        tracker = _tracker(tmp_path)
        with pytest.raises(OpsMaturityError):
            tracker.request_unlock(OpsMaturityLevel.A_L2, UnlockEvidence(weeks_zero_tnr=99))

    def test_a_l3_out_of_scope(self, tmp_path):
        tracker = _tracker(tmp_path)
        with pytest.raises(OpsMaturityError):
            tracker.request_unlock("A-L3", UnlockEvidence(weeks_zero_tnr=99))

    def test_progression_to_a_l2(self, tmp_path):
        tracker = _tracker(tmp_path, required_weeks=2)
        tracker.request_unlock(OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=2))
        decision = tracker.request_unlock(OpsMaturityLevel.A_L2, UnlockEvidence(weeks_zero_tnr=4))
        assert decision.approved
        assert tracker.current_level() is OpsMaturityLevel.A_L2


class TestTnrViolation:
    def test_tnr_violation_resets_streak_and_logged(self, tmp_path):
        tracker = _tracker(tmp_path)
        tracker.request_unlock(OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=5))
        assert tracker.weeks_zero_tnr_streak() == 5
        tracker.record_tnr_violation("自动修复后回归测试红")
        assert tracker.weeks_zero_tnr_streak() == 0, "TNR 违规 MUST 归零连续周数"
        entries = _read_jsonl(tmp_path / "maturity_ledger.jsonl")
        violations = [e for e in entries if e["kind"] == "tnr_violation"]
        assert len(violations) == 1
        assert violations[0]["description"]


class TestAdoptionTracking:
    def _at_a_l2(self, tmp_path) -> OpsMaturityTracker:
        tracker = _tracker(tmp_path, required_weeks=1)
        tracker.request_unlock(OpsMaturityLevel.A_L1, UnlockEvidence(weeks_zero_tnr=1))
        tracker.request_unlock(OpsMaturityLevel.A_L2, UnlockEvidence(weeks_zero_tnr=1))
        assert tracker.current_level() is OpsMaturityLevel.A_L2
        return tracker

    def test_adoption_rate_recorded_at_a_l2(self, tmp_path):
        tracker = self._at_a_l2(tmp_path)
        tracker.record_adoption("SUG-1", adopted=True, reviewer="owner")
        tracker.record_adoption("SUG-2", adopted=True, reviewer="owner")
        tracker.record_adoption("SUG-3", adopted=False, reviewer="owner")
        stats = tracker.adoption_stats()
        assert stats["total"] == 3
        assert stats["adopted"] == 2
        assert stats["rate"] == pytest.approx(2 / 3)
        entries = _read_jsonl(tmp_path / "maturity_ledger.jsonl")
        adoptions = [e for e in entries if e["kind"] == "adoption"]
        assert len(adoptions) == 3
        assert all(e["level"] == "A-L2" for e in adoptions), "A-L2 状态下采纳 MUST 带等级留痕"
        assert all(e["reviewer"] == "owner" for e in adoptions)

    def test_adoption_requires_reviewer(self, tmp_path):
        tracker = self._at_a_l2(tmp_path)
        with pytest.raises(OpsMaturityError):
            tracker.record_adoption("SUG-4", adopted=True, reviewer="")

    def test_adoption_stats_empty(self, tmp_path):
        tracker = _tracker(tmp_path)
        stats = tracker.adoption_stats()
        assert stats["total"] == 0
        assert stats["rate"] is None
