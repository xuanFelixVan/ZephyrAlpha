"""test_executor — C3 对比执行器：三锁机检正反枚举 + 预检聚合 + 裁定卡签发权 + 锦标赛截断。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.ai_layer.comparator import RefuseExam, VenueUnavailable, VENUE_IDS
from zephyr.ai_layer.comparator.experiment_store import (
    ComparisonExperimentRecord,
    canonical_criteria_text,
    criteria_hash,
)
from zephyr.ai_layer.comparator.executor import (
    VerdictRuling,
    check_hash_lock,
    check_session_mutuality,
    check_time_lock,
    claim_exam,
    issue_verdict_card,
    parse_criteria_ref,
    run_preflight,
    shortlist_top_k,
    verify_criteria_integrity,
)

T0 = datetime(2026, 9, 20, 12, 0, 0, tzinfo=UTC)
T1 = T0 + timedelta(days=1)
T2 = T0 + timedelta(days=2)
ISO0, ISO1, ISO2 = T0.isoformat(), T1.isoformat(), T2.isoformat()
HASH = criteria_hash(canonical_criteria_text({"alpha": 0.05}))


def make_record(**over: object) -> ComparisonExperimentRecord:
    values: dict = {
        "experiment_id": "EX-20260923-demo",
        "challenger_ref": "cand-v1",
        "champion_ref": "champ-current",
        "venue_ref": "venue_c4",
        "criteria_yaml": canonical_criteria_text({"alpha": 0.05}),
        "criteria_hash": HASH,
        "status": "frozen",
        "evaluator_session": "eval-sid",
        "contractor_session": "ctor-sid",
        "frozen_at": ISO0,
    }
    values.update(over)
    return ComparisonExperimentRecord(**values)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 机检①会话互斥
# ---------------------------------------------------------------------------

def test_session_mutuality() -> None:
    assert check_session_mutuality("ctor", "eval").passed
    bad = check_session_mutuality("same", "same")
    assert not bad.passed and "session_mutuality_violation" in bad.reason
    assert not check_session_mutuality("", "eval").passed


# ---------------------------------------------------------------------------
# 机检③时序锁（frozen < dispatched < first_commit）
# ---------------------------------------------------------------------------

def test_time_lock_ok_with_strings_and_datetimes() -> None:
    assert check_time_lock(ISO0, ISO1, ISO2).passed
    assert check_time_lock(T0, T1, T2).passed
    assert check_time_lock(T0, ISO1, T2).passed  # 混合形态


@pytest.mark.parametrize("frozen,disp,commit", [
    (ISO1, ISO0, ISO2),   # frozen 晚于派发（倒挂）
    (ISO0, ISO2, ISO1),   # 派发晚于首 commit（倒挂）
    (ISO0, ISO0, ISO2),   # 相等（须严格小于）
    (ISO0, ISO1, ISO1),   # 相等（须严格小于）
])
def test_time_lock_inverted_rejected(frozen: str, disp: str, commit: str) -> None:
    bad = check_time_lock(frozen, disp, commit)
    assert not bad.passed and "time_lock_inverted" in bad.reason


@pytest.mark.parametrize("frozen,disp,commit", [
    (None, ISO1, ISO2), ("", ISO1, ISO2), (ISO0, None, ISO2), (ISO0, ISO1, "not-a-time"),
    (datetime(2026, 9, 20, tzinfo=None), ISO1, ISO2),  # naive 拒收
])
def test_time_lock_missing_or_naive_rejected(frozen: object, disp: object, commit: object) -> None:
    bad = check_time_lock(frozen, disp, commit)
    assert not bad.passed and "time_lock" in bad.reason


# ---------------------------------------------------------------------------
# 机检④哈希锁 / 卡内一致性 / criteria_ref 解析
# ---------------------------------------------------------------------------

def test_hash_lock_and_integrity() -> None:
    assert check_hash_lock(HASH, HASH).passed
    bad = check_hash_lock(HASH, "f" * 64)
    assert not bad.passed and bad.reason == "hash_mismatch"
    record = make_record()
    assert verify_criteria_integrity(record.criteria_yaml, record.criteria_hash).passed
    tampered = verify_criteria_integrity(record.criteria_yaml + "#tampered\n", record.criteria_hash)
    assert not tampered.passed  # DB 外篡改检出


def test_parse_criteria_ref() -> None:
    ref = f"EX-20260923-demo#{HASH}"
    assert parse_criteria_ref(ref) == ("EX-20260923-demo", HASH)
    with pytest.raises(ValueError, match="criteria_ref"):
        parse_criteria_ref("EX-20260923-demo")
    with pytest.raises(ValueError):
        parse_criteria_ref(f"EX-20260923-demo#nothex")


# ---------------------------------------------------------------------------
# 锦标赛截断（D-L4-02 纯函数全枚举）
# ---------------------------------------------------------------------------

def test_shortlist_below_trigger_keeps_all_order() -> None:
    items = [{"n": i, "is_score": float(i)} for i in range(4)]
    out = shortlist_top_k(items, k=2, trigger_n=5)
    assert out == items  # N<trigger 全保留原序


def test_shortlist_sorts_desc_and_takes_k() -> None:
    items = [{"n": "a", "is_score": 1.0}, {"n": "b", "is_score": 3.0},
             {"n": "c", "is_score": 2.0}, {"n": "d", "is_score": 2.0},
             {"n": "e", "is_score": 0.5}]
    out = shortlist_top_k(items, k=3, trigger_n=5)
    assert [x["n"] for x in out] == ["b", "c", "d"]  # 降序取前 K，同分稳定保持原序


def test_shortlist_k_zero() -> None:
    items = [{"n": "a", "is_score": 1.0}, {"n": "b", "is_score": 2.0}]
    assert shortlist_top_k(items, k=0, trigger_n=1) == []


# ---------------------------------------------------------------------------
# 领考预检（全过才开考；任一不过 RefuseExam 聚合拒考）
# ---------------------------------------------------------------------------

REF = f"EX-20260923-demo#{HASH}"


def test_preflight_all_pass() -> None:
    report = run_preflight(
        make_record(), task_criteria_ref=REF, fairness_passed=True,
        dispatched_at=ISO1, first_commit_at=ISO2,
    )
    assert report.passed and not report.reasons
    assert report.ensure_pass() is report


def test_preflight_every_failure_mode_collected() -> None:
    # 全部机检同时失败：会话互斥/判据被篡改/ref id 不匹配/缺 criteria_ref/时序倒挂/公平性未检
    record = make_record(
        contractor_session="eval-sid",
        criteria_yaml=canonical_criteria_text({"alpha": 0.10}),
        frozen_at=ISO1,
    )
    report = run_preflight(
        record, task_criteria_ref=None, fairness_passed=None,
        dispatched_at=ISO0, first_commit_at=ISO2,
    )
    assert not report.passed
    joined = ";".join(report.reasons)
    for token in (
        "session_mutuality_violation", "hash_mismatch", "criteria_ref_missing",
        "time_lock_inverted", "fairness_not_checked",
    ):
        assert token in joined, token
    with pytest.raises(RefuseExam) as excinfo:
        report.ensure_pass()
    assert list(report.reasons) == excinfo.value.reasons


def test_preflight_ref_id_mismatch_detected() -> None:
    other = f"EX-20260923-other#{HASH}"
    report = run_preflight(
        make_record(), task_criteria_ref=other, fairness_passed=True,
        dispatched_at=ISO1, first_commit_at=ISO2,
    )
    assert not report.passed
    assert any("criteria_ref_id_mismatch" in r for r in report.reasons)


def test_preflight_fairness_failed_vs_not_checked() -> None:
    kw = {"task_criteria_ref": REF, "dispatched_at": ISO1, "first_commit_at": ISO2}
    failed = run_preflight(make_record(), fairness_passed=False, **kw)
    assert any("fairness_failed" in r for r in failed.reasons)
    unchecked = run_preflight(make_record(), fairness_passed=None, **kw)
    assert any("fairness_not_checked" in r for r in unchecked.reasons)


# ---------------------------------------------------------------------------
# 裁定卡签发（仅 evaluator 会话；E3 必附归因）
# ---------------------------------------------------------------------------

def test_verdict_card_by_evaluator_ok() -> None:
    card = issue_verdict_card(
        make_record(), "win", ruled_by_session="eval-sid",
        ruling=VerdictRuling(
            evidence_pack={"experiment_id": "EX-20260923-demo"}, significance="p=0.01",
        ),
        issued_at=ISO1,
    )
    assert card.verdict == "win" and card.evaluator_session == "eval-sid"
    assert card.evidence_pack["experiment_id"] == "EX-20260923-demo"


def test_verdict_card_contractor_signing_rejected() -> None:
    with pytest.raises(ValueError, match="evaluator_session"):
        issue_verdict_card(make_record(), "win", ruled_by_session="ctor-sid")


def test_verdict_card_e3_requires_attribution_and_valid_exit() -> None:
    with pytest.raises(ValueError, match="attribution"):
        issue_verdict_card(
            make_record(), "rejected_too_good", ruled_by_session="eval-sid",
            ruling=VerdictRuling(too_good_exit="E3"),
        )
    ok = issue_verdict_card(
        make_record(), "rejected_too_good", ruled_by_session="eval-sid",
        ruling=VerdictRuling(too_good_exit="E3", attribution="luck_or_gaming"),
    )
    assert ok.attribution == "luck_or_gaming" and ok.too_good_exit == "E3"
    with pytest.raises(ValueError, match="too_good_exit"):
        issue_verdict_card(
            make_record(), "win", ruled_by_session="eval-sid",
            ruling=VerdictRuling(too_good_exit="E9"),
        )


# ---------------------------------------------------------------------------
# 领考 fail-closed
# ---------------------------------------------------------------------------

class FakeVenue:
    def __init__(self, ok: bool) -> None:
        self._ok = ok
        self.venue_id = "venue_fake"

    def available(self) -> bool:
        return self._ok


def test_claim_exam_dispatch_and_fail_closed() -> None:
    good = FakeVenue(ok=True)
    assert claim_exam("venue_c4", {"venue_c4": good}) is good
    with pytest.raises(ValueError, match="unknown_venue"):
        claim_exam("venue_nope", {"venue_c4": good})
    with pytest.raises(VenueUnavailable, match="venue_not_registered"):
        claim_exam("venue_c4", {})
    with pytest.raises(VenueUnavailable, match="venue_ruler_unreachable"):
        claim_exam("venue_c4", {"venue_c4": FakeVenue(ok=False)})


def test_venue_ids_registry_shape() -> None:
    assert VENUE_IDS == ("venue_c4", "venue_replay", "venue_dual_run", "venue_tool_bench")
