# [A_test] module_id: MOD-GOV-CARDREVIEWAUTO | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-CARDREVIEWAUTO | docs/01_policies_and_standards/sop/construction_sop/task_card_work_order_policy.md | §interface-2
# [MODULE] tests.governance.persistence.test_card_review_automation
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] 全 mock repository（禁触生产 DB）；断言两轮 batch_review 调用与报告形态；断言自动化永不调 verify（禁代盖章）
# [MODIFY-GUARD] scripts/governance/card_review_automation.py
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError on behavior drift
# [TESTS] —
# [A_module] module_id=MOD-GOV-CARDREVIEWAUTO | layer=module | stability=volatile | safety=L | ai_modifiable
# [TTL] task_bound
"""单元测试：card_review_automation（任务卡工单制政策 v1.0 接口②）

覆盖矩阵
--------
run_card_review_automation :
  - 默认恰好两轮 batch_review（reviewer/session_id 透传）
  - 首轮有 issue 提前停（只跑 1 轮，early_stopped=True）
  - 两轮全净但 review_complete=False（历史脏轮在册）→ 不就绪
  - 报告形态（schema/stamped=False/关键字段齐全）
  - verify_ready=True 时也绝不调 verify（禁代盖章，立法 §2）
  - 轮间隔经注入 sleep 触发（轮与轮之间恰好一次）
  - 卡已 verified：already_verified=True，verify_ready=False
  - 卡不存在：ok=False + error=task_not_found（不抛穿 CLI）
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from scripts.governance.card_review_automation import run_card_review_automation
from zephyr.governance.persistence.task_repo import TaskNotFoundError

_SID = "st-tclose-cardlaw-20261004"


def _clean_review(round_no: int) -> dict:
    return {
        "task_id": "SRC-1",
        "round": round_no,
        "total_issues": 0,
        "passed": True,
        "consecutive_zero": round_no,
        "dimensions": {},
    }


def _dirty_review(round_no: int) -> dict:
    return {
        "task_id": "SRC-1",
        "round": round_no,
        "total_issues": 2,
        "passed": False,
        "consecutive_zero": 0,
        "dimensions": {"checklist_completeness": {"issues": ["a", "b"], "passed": False}},
    }


def _complete_status() -> dict:
    return {
        "task_id": "SRC-1",
        "reviewed": True,
        "total_rounds": 2,
        "consecutive_zero": 2,
        "review_complete": True,
        "rounds": {},
    }


def _make_repo(
    *, review_results: list[dict], review_status: dict, verification_status: str = "unverified"
) -> MagicMock:
    repo = MagicMock(name="TaskRepositoryMock")
    repo.batch_review.side_effect = review_results
    repo.get_review_status.return_value = review_status
    repo.get.return_value = SimpleNamespace(verification_status=verification_status)
    return repo


def test_two_rounds_by_default_with_kwargs_passthrough() -> None:
    repo = _make_repo(
        review_results=[_clean_review(1), _clean_review(2)],
        review_status=_complete_status(),
    )
    report = run_card_review_automation(repo, "SRC-1", reviewer="lane_h4", session_id=_SID)
    assert repo.batch_review.call_count == 2
    repo.batch_review.assert_any_call("SRC-1", reviewer="lane_h4", session_id=_SID)
    assert report["rounds_run"] == 2
    assert report["verify_ready"] is True


def test_early_stop_on_first_round_issues() -> None:
    repo = _make_repo(
        review_results=[_dirty_review(1), _clean_review(2)],
        review_status={"task_id": "SRC-1", "reviewed": True, "consecutive_zero": 0, "review_complete": False},
    )
    report = run_card_review_automation(repo, "SRC-1")
    assert repo.batch_review.call_count == 1
    assert report["early_stopped"] is True
    assert report["rounds_run"] == 1
    assert report["verify_ready"] is False


def test_two_clean_rounds_but_status_incomplete_not_ready() -> None:
    """两轮全净但 get_review_status 判 review_complete=False（如历史脏轮在册）——不就绪。"""
    repo = _make_repo(
        review_results=[_clean_review(1), _clean_review(2)],
        review_status={"task_id": "SRC-1", "reviewed": True, "consecutive_zero": 1, "review_complete": False},
    )
    report = run_card_review_automation(repo, "SRC-1")
    assert repo.batch_review.call_count == 2
    assert report["rounds_run"] == 2
    assert report["rounds_passed"] == 2
    assert report["early_stopped"] is False
    assert report["verify_ready"] is False


def test_report_shape_and_no_stamp() -> None:
    repo = _make_repo(
        review_results=[_clean_review(1), _clean_review(2)],
        review_status=_complete_status(),
    )
    report = run_card_review_automation(repo, "SRC-1", session_id=_SID)
    for key in (
        "schema",
        "task_id",
        "ok",
        "rounds_requested",
        "rounds_run",
        "rounds_passed",
        "early_stopped",
        "review_status",
        "verification_status",
        "already_verified",
        "verify_ready",
        "stamped",
        "conclusion",
    ):
        assert key in report, f"报告缺字段: {key}"
    assert report["schema"] == "card_review_automation/v1"
    assert report["task_id"] == "SRC-1"
    assert report["ok"] is True
    # 立法 §2：自动化只报告不代盖章——即使就绪也恒不调 verify
    repo.verify.assert_not_called()
    assert report["stamped"] is False


def test_verify_ready_never_calls_verify() -> None:
    repo = _make_repo(
        review_results=[_clean_review(1), _clean_review(2)],
        review_status=_complete_status(),
    )
    run_card_review_automation(repo, "SRC-1")
    repo.verify.assert_not_called()


def test_interval_sleep_between_rounds_only() -> None:
    repo = _make_repo(
        review_results=[_clean_review(1), _clean_review(2)],
        review_status=_complete_status(),
    )
    sleeper = MagicMock(name="sleep")
    run_card_review_automation(repo, "SRC-1", rounds=2, interval_seconds=30.0, sleep=sleeper)
    sleeper.assert_called_once_with(30.0)


def test_already_verified_card_reports_no_reverify() -> None:
    repo = _make_repo(
        review_results=[_clean_review(1), _clean_review(2)],
        review_status=_complete_status(),
        verification_status="verified",
    )
    report = run_card_review_automation(repo, "SRC-1")
    assert report["already_verified"] is True
    assert report["verify_ready"] is False
    repo.verify.assert_not_called()


def test_task_not_found_returns_error_report() -> None:
    repo = MagicMock(name="TaskRepositoryMock")
    repo.get.side_effect = TaskNotFoundError("任务不存在")
    report = run_card_review_automation(repo, "NOPE-999")
    assert report["ok"] is False
    assert report["error"] == "task_not_found"
    repo.batch_review.assert_not_called()


def test_rounds_configurable_min_one() -> None:
    repo = _make_repo(
        review_results=[_clean_review(1)],
        review_status={"task_id": "SRC-1", "reviewed": True, "consecutive_zero": 1, "review_complete": False},
    )
    report = run_card_review_automation(repo, "SRC-1", rounds=1)
    assert repo.batch_review.call_count == 1
    assert report["verify_ready"] is False


def test_invalid_rounds_rejected() -> None:
    repo = _make_repo(review_results=[], review_status={})
    with pytest.raises(ValueError):
        run_card_review_automation(repo, "SRC-1", rounds=0)
