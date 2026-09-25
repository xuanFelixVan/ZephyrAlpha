# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] tests.ai_layer.cleaning.test_auditor
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.auditor; zephyr.ai_layer.cleaning.policy
# [CONSUMERS] pytest tests/ai_layer/cleaning/test_auditor.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] judge/rewasher/journal/卡写全注入（零真实外呼）；时间锚显式注入
#              （cold_started_at/as_of，零隐式时钟判）；采样断言用确定性分桶复算
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.5
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] tests/ai_layer/cleaning/test_auditor.py
# [TTL] permanent
"""test_auditor - 抽验审计器验收（C6）：采样/机检前置/独立性拒卷/rubric/两级流转。"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

from zephyr.ai_layer.cleaning.auditor import (
    AuditorDeps,
    JudgeRequest,
    CleaningJudgeResult,
    SamplingAuditor,
    check_judge_independence,
    judge_quality_watch,
    machine_precheck,
    model_vendor,
    rubric_pass,
    sample_decision,
)
from zephyr.ai_layer.cleaning.policy import load_cleaning_policy

POLICY = load_cleaning_policy()
ANCHOR = datetime(2026, 9, 1, tzinfo=timezone.utc)
LATE = ANCHOR + timedelta(days=30)
WASH = {"session": "st-washer-a", "model_id": "deepseek-chat", "model_tier": "standard"}
GOOD_SCORES = {"fidelity": 2, "completeness": 1, "reproducibility": 2}


def _spec(card_id: str = "CC-A1", **overrides: Any) -> SimpleNamespace:
    base: dict[str, Any] = {
        "spec_id": f"SP-{card_id}-v1",
        "card_id": card_id,
        "version": 1,
        "status": "active",
        "mechanism_one_liner": "动量因子在趋势市的加速入场效应",
        "mechanism_detail": "价格动量在高趋势 regime 下入场加速，回撤靠波动率滤窗控制。",
        "reproduction_notes": "伪代码：动量排名前 10% 等权持有，月度再平衡。",
        "applicability": {"regime": "趋势", "frequency": "日", "universe": "沪深300"},
        "ashare_precheck": {"overall": "pass"},
        "risk_flags": ["overfit_history"],
        "data_fields": [{"field": "close", "source_ref": "tushare", "quality_note": "ok"}],
        "source_quotes": ["momentum accelerates in trending markets"],
        "source_name": "arxiv", "source_url": "https://arxiv.org/abs/x",
        "source_publisher": "arXiv", "source_year": 2025,
        "wash": dict(WASH),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


L2_CARD = {
    "source_name": "arxiv", "source_url": "https://arxiv.org/abs/x",
    "source_publisher": "arXiv", "source_year": 2025, "four_gates": {},
}


class FakeStore:
    def __init__(self, spec: Any, total: int = 5) -> None:
        self._spec = spec
        self._total = total
        self.reviews: dict[str, dict[str, Any]] = {}
        self.statuses: dict[str, str] = {}

    def get_active(self, card_id: str) -> Any:
        return self._spec

    def set_review(self, spec_id: str, review: dict[str, Any]) -> None:
        self.reviews[spec_id] = review

    def mark_status(self, spec_id: str, status: str, policy: Any = None) -> None:
        self.statuses[spec_id] = status

    def count_cards(self) -> int:
        return self._total


class FakeJournal:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def emit(self, kind: str, payload: dict[str, Any]) -> Any:
        self.events.append((kind, payload))
        return SimpleNamespace(id="E-1", kind=kind)


class FakeWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    def transition(self, card_id: str, stage: str, **refs: Any) -> str:
        self.calls.append((card_id, stage, refs))
        return stage


def _judge(session: str = "st-judge-b", model: str = "claude-sonnet", tier: str = "premium",
           scores: dict[str, float] | None = None) -> Any:
    calls: list[JudgeRequest] = []

    def judge(request: JudgeRequest) -> CleaningJudgeResult:
        calls.append(request)
        return CleaningJudgeResult(scores=dict(scores or GOOD_SCORES), model=model, session=session, tier=tier)

    judge.calls = calls  # type: ignore[attr-defined]
    return judge


def _deps(store: FakeStore, judge: Any, **kw: Any) -> AuditorDeps:
    return AuditorDeps(
        session_id="st-judge-b",
        store=store,
        policy=POLICY,
        judge=judge,
        rewasher=kw.get("rewasher"),
        journal=kw.get("journal", FakeJournal()),
        card_writer=kw.get("card_writer", FakeWriter()),
    )


# ---------------------------------------------------------------- 采样


def _bucket(card_id: str) -> int:
    return int(hashlib.sha256(card_id.encode("utf-8")).hexdigest(), 16) % 100


def test_sample_cold_start_window_and_count() -> None:
    near = sample_decision(POLICY, card_id="CC-X", cards_washed_total=1,
                           cold_started_at=ANCHOR, as_of=ANCHOR + timedelta(days=3),
                           four_gates={})
    assert near.sampled and near.reason == "cold_start", "冷启动窗内 100% 复核"
    count_based = sample_decision(POLICY, card_id="CC-X", cards_washed_total=50,
                                  cold_started_at=ANCHOR, as_of=LATE, four_gates={})
    assert count_based.sampled and count_based.reason == "cold_start", "前 100 张先到者全检"


def test_sample_high_impact_forced_full_check() -> None:
    hot = sample_decision(POLICY, card_id="CC-X", cards_washed_total=500,
                          cold_started_at=ANCHOR, as_of=LATE,
                          four_gates={"cross_validation": {"status": "已验证"}})
    assert hot.sampled and hot.reason == "high_impact", "高影响卡强制全检"


def test_sample_periodic_deterministic_bucket() -> None:
    # 用确定性复算钉住分桶判据（零随机零时钟）
    forced_low = next(f"CC-L{i}" for i in range(200) if _bucket(f"CC-L{i}") < 20)
    decision = sample_decision(POLICY, card_id=forced_low, cards_washed_total=500,
                               cold_started_at=ANCHOR, as_of=LATE, four_gates={})
    assert decision.sampled and decision.reason == "periodic_sample"
    forced_high = next(f"CC-H{i}" for i in range(200) if _bucket(f"CC-H{i}") >= 20)
    skipped = sample_decision(POLICY, card_id=forced_high, cards_washed_total=500,
                              cold_started_at=ANCHOR, as_of=LATE, four_gates={})
    assert not skipped.sampled and skipped.reason == "skip"


# ---------------------------------------------------------------- 机检与独立性


def test_machine_precheck_pass_and_placeholder_fail() -> None:
    ok, failures = machine_precheck(_spec().__dict__, L2_CARD, POLICY)
    assert ok and failures == ()
    bad, failures = machine_precheck(_spec(reproduction_notes="同上").__dict__, L2_CARD, POLICY)
    assert not bad and any(f.startswith("placeholder_word") for f in failures)


def test_machine_precheck_source_drift_and_empty_groups() -> None:
    drifted, failures = machine_precheck(
        _spec(source_url="https://evil.example/rewritten").__dict__, L2_CARD, POLICY)
    assert not drifted and any(f.startswith("source_drift") for f in failures), "洗后断源即拒"
    empty, failures = machine_precheck(_spec(data_fields=[]).__dict__, L2_CARD, POLICY)
    assert not empty and "empty_group:data_fields" in failures


def test_independence_refusals() -> None:
    assert check_judge_independence(WASH, reviewer_session="st-washer-a",
                                    reviewer_model="claude-sonnet", reviewer_tier="premium",
                                    policy=POLICY) == (False, "same_session")
    assert check_judge_independence(WASH, reviewer_session="st-judge-b",
                                    reviewer_model="deepseek-reasoner", reviewer_tier="premium",
                                    policy=POLICY) == (False, "same_vendor")
    assert check_judge_independence(WASH, reviewer_session="st-judge-b",
                                    reviewer_model="claude-sonnet", reviewer_tier="standard",
                                    policy=POLICY) == (False, "same_tier")
    ok, why = check_judge_independence(WASH, reviewer_session="st-judge-b",
                                       reviewer_model="claude-sonnet", reviewer_tier="premium",
                                       policy=POLICY)
    assert ok and why == ""


def test_model_vendor_prefixes() -> None:
    assert model_vendor("deepseek-chat") == "deepseek"
    assert model_vendor("claude-sonnet-4") == "anthropic"
    assert model_vendor("glm-4-plus") == "zhipu"
    assert model_vendor("qwen3:8b") == "alibaba"
    assert model_vendor("mystery-model") == "unknown"


def test_rubric_rules() -> None:
    assert rubric_pass({"fidelity": 2, "completeness": 1, "reproducibility": 2}, POLICY) == (True, "")
    fail = rubric_pass({"fidelity": 2, "completeness": 1, "reproducibility": 0}, POLICY)
    assert not fail[0] and fail[1] == "rubric_zero_score:reproducibility", "禁 0 分通过"
    missing = rubric_pass({"fidelity": 2, "completeness": 1}, POLICY)
    assert not missing[0] and missing[1] == "rubric_dim_missing:reproducibility"
    offscale = rubric_pass({"fidelity": 3, "completeness": 1, "reproducibility": 1}, POLICY)
    assert not offscale[0]


def test_judge_quality_watch_threshold() -> None:
    calm = judge_quality_watch(0.05, POLICY)
    assert calm["alert"] is False and calm["suggestion"] == "none"
    loud = judge_quality_watch(0.2, POLICY)
    assert loud["alert"] is True and "downgrade" in loud["suggestion"]


# ---------------------------------------------------------------- 编排流转


def test_audit_pass_records_review() -> None:
    store = FakeStore(_spec())
    judge = _judge()
    outcome = SamplingAuditor(_deps(store, judge)).audit("CC-A1", l2_card=L2_CARD,
                                                         cold_started_at=ANCHOR, as_of=ANCHOR)
    assert outcome.verdict == "pass" and outcome.next_action == "none"
    review = store.reviews["SP-CC-A1-v1"]
    assert review["verdict"] == "pass" and review["reviewer_model"] == "claude-sonnet"
    assert review["rubric_scores"] == GOOD_SCORES


def test_audit_not_sampled_records_trace_only() -> None:
    bucket_safe = next(f"CC-H{i}" for i in range(200) if _bucket(f"CC-H{i}") >= 20)
    store = FakeStore(_spec(card_id=bucket_safe), total=500)
    judge = _judge()
    outcome = SamplingAuditor(_deps(store, judge)).audit(
        bucket_safe, l2_card=L2_CARD, cold_started_at=ANCHOR, as_of=LATE)
    assert outcome.verdict == "not_sampled"
    trace = store.reviews[f"SP-{bucket_safe}-v1"]
    assert trace == {"sampled": False, "verdict": None}, "未采样只留痕不动卡"
    assert not judge.calls, "未采样零裁判消耗"


def test_audit_same_vendor_judge_refused() -> None:
    store = FakeStore(_spec())
    judge = _judge(model="deepseek-reasoner", session="st-judge-b", tier="premium")
    outcome = SamplingAuditor(_deps(store, judge)).audit("CC-A1", l2_card=L2_CARD,
                                                         cold_started_at=ANCHOR, as_of=ANCHOR)
    assert outcome.verdict == "error" and outcome.next_action == "rejudge"
    assert "judge_refused:same_vendor" in outcome.note
    assert store.reviews == {}, "拒卷不落 review（运动员不兼任裁判）"


def test_audit_machine_fail_consumes_no_judge() -> None:
    store = FakeStore(_spec(reproduction_notes="待填"))
    judge = _judge()
    outcome = SamplingAuditor(_deps(store, judge)).audit("CC-A1", l2_card=L2_CARD,
                                                         cold_started_at=ANCHOR, as_of=ANCHOR)
    assert outcome.verdict == "rework" and outcome.next_action == "rewash_upgrade"
    assert not judge.calls, "机检不过直接 rework，不耗裁判"
    assert store.reviews["SP-CC-A1-v1"]["verdict"] == "rework"


def test_two_level_flow_fail_rewash_then_reject() -> None:
    """核心验收：fail→升级重洗一次→再 fail→rejected_wash+intake_reject_due 留痕。"""
    store = FakeStore(_spec())
    judge = _judge(scores={"fidelity": 2, "completeness": 2, "reproducibility": 0})
    journal = FakeJournal()
    writer = FakeWriter()
    rewash_calls: list[str] = []
    outcome = SamplingAuditor(_deps(store, judge, rewasher=lambda cid: rewash_calls.append(cid),
                                    journal=journal, card_writer=writer)).audit_and_route(
        "CC-A1", l2_card=L2_CARD, cold_started_at=ANCHOR, as_of=ANCHOR)
    assert rewash_calls == ["CC-A1"], "级联升级重洗恰一次"
    assert outcome.verdict == "fail" and outcome.next_action == "reject"
    assert store.statuses.get("SP-CC-A1-v1") == "rejected_wash"
    kind, payload = journal.events[0]
    assert kind == "intake_reject_due" and payload["stage"] == "L3"
    assert payload["rejection_reason"] == "wash_failed"
    assert ("CC-A1", "rejected", {
        "rejection_reason": "wash_failed", "evidence_ref": payload["evidence_ref"]}) in writer.calls


def test_finalize_reject_injection_suspect_flag() -> None:
    store = FakeStore(_spec(risk_flags=["injection_suspect"]))
    judge = _judge(scores={"fidelity": 1, "completeness": 1, "reproducibility": 0})
    journal = FakeJournal()
    outcome = SamplingAuditor(_deps(store, judge, journal=journal,
                                    rewasher=lambda cid: None)).audit_and_route(
        "CC-A1", l2_card=L2_CARD, cold_started_at=ANCHOR, as_of=ANCHOR)
    assert outcome.note == "injection_suspect"
    assert journal.events[0][1]["rejection_reason"] == "injection_suspect"


def test_audit_missing_active_spec_is_error() -> None:
    store = FakeStore(None)
    outcome = SamplingAuditor(_deps(store, _judge())).audit("CC-ghost")
    assert outcome.verdict == "error" and outcome.note == "no_active_spec"
