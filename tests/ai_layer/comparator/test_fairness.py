"""test_fairness — C5 公平性对齐器：三轴+防假胜三条全机检全枚举 + 带星胜降级路径。"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.comparator.fairness import (
    FairnessSpec,
    check_fairness,
    downgrade_verdict,
)
from zephyr.ai_layer.comparator.policy import load_comparison_policy

VOCAB = load_comparison_policy()["fairness"]["compute_class_values"]


def spec(**over: object) -> FairnessSpec:
    values: dict = {
        "compute_class": "local",
        "mutex_group": "gpu_default",
        "quota_ref": "quota-pool-a",
        "window_spec": "IS:2020-01-01..2023-12-31|OOS:2024-01-01..2024-12-31",
        "seed": 20260923,
        "task_suite_version": "suite-v7",
        "wall_clock_cap": "2h",
        "timeout_s": 600,
        "cost_accounting_version": "tiered_weighted_v1",
        "batch_criteria_hash": "b" * 64,
    }
    values.update(over)
    return FairnessSpec(**values)  # type: ignore[arg-type]


def test_equal_specs_pass_not_starred() -> None:
    report = check_fairness(spec(), spec(champion_score_source="history"), vocab=VOCAB)
    assert report.passed and not report.starred
    assert not report.reasons and not report.notes


@pytest.mark.parametrize("field,value", [
    ("compute_class", "api"), ("mutex_group", "llm_local"), ("quota_ref", "quota-b"),
    ("window_spec", "IS:2019|OOS:2024"), ("seed", 1), ("task_suite_version", "suite-v6"),
    ("wall_clock_cap", "1h"), ("timeout_s", 60), ("cost_accounting_version", "flat_v0"),
])
def test_each_field_mismatch_fails_with_token(field: str, value: object) -> None:
    report = check_fairness(spec(), spec(**{field: value}), vocab=VOCAB)
    assert not report.passed
    assert any(f"unequal:{field}" in r for r in report.reasons), report.reasons


@pytest.mark.parametrize("field", [
    "compute_class", "mutex_group", "quota_ref", "window_spec", "seed", "task_suite_version",
    "wall_clock_cap", "timeout_s", "cost_accounting_version", "batch_criteria_hash",
])
def test_each_missing_field_fails_closed(field: str) -> None:
    champion = spec(**{field: None})
    report = check_fairness(spec(), champion, vocab=VOCAB)
    assert not report.passed
    assert any(f"missing:{field}" in r for r in report.reasons), report.reasons


def test_compute_class_out_of_vocab_rejected() -> None:
    report = check_fairness(spec(compute_class="tpu_x"), spec(compute_class="tpu_x"), vocab=VOCAB)
    assert not report.passed
    assert any("compute_class_out_of_vocab:tpu_x" in r for r in report.reasons)


def test_champion_history_cross_suite_rejected() -> None:
    # 防假胜 #1：考卷版本不同禁引 champion 历史成绩
    report = check_fairness(
        spec(task_suite_version="suite-v7"),
        spec(task_suite_version="suite-v6", champion_score_source="history"),
        vocab=VOCAB,
    )
    assert not report.passed
    assert any("champion_history_cross_suite" in r for r in report.reasons)


def test_champion_history_same_suite_allowed() -> None:
    report = check_fairness(
        spec(), spec(champion_score_source="history"), vocab=VOCAB
    )
    assert report.passed


def test_per_candidate_criteria_tuning_rejected() -> None:
    # 防假胜 #3：逐候选微调门槛=判据 hash 不一致 → 拒考
    report = check_fairness(spec(), spec(batch_criteria_hash="d" * 64), vocab=VOCAB)
    assert not report.passed
    assert any("per_candidate_criteria_tuning" in r for r in report.reasons)


def test_resource_delta_downgrades_to_starred_win() -> None:
    # 防假胜 #2：新资源通道同等开放；delta 非零=带星胜（记录不阻断，L5 排产降优先级）
    report = check_fairness(spec(resource_delta="free_window_hit"), spec(), vocab=VOCAB)
    assert report.passed and report.starred
    assert report.notes and "win*" in report.notes[0]
    assert downgrade_verdict("win", starred=True) == "win_starred"
    assert downgrade_verdict("win", starred=False) == "win"
    assert downgrade_verdict("win_starred", starred=False) == "win_starred"
    assert downgrade_verdict("draw", starred=True) == "draw"


def test_downgrade_verdict_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown_verdict"):
        downgrade_verdict("victory", starred=True)


def test_vocab_from_policy_layer_is_source() -> None:
    # 词表真源=常量层（config/comparison_policy.yaml），不在本模块复制
    assert "local" in VOCAB and "local_gpu" in VOCAB and "mixed" in VOCAB and "api" in VOCAB
