# [A_test] module_id: MOD-SIG-065 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SIG-065 | 待统筹登记 | 28号 memo §3.3 + 30号 §6.3
# [MODULE] tests.signal_ashare.test_sentiment_cycle_evaluator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""SentimentCycleEvaluator（MOD-SIG-065）施工验证测试。

覆盖：
- 标准签名⑥（evaluate_locator_accuracy）精确率 + 相邻容错率；
- 历史回测口径（evaluate_from_records）：分阶段召回 + 混淆矩阵；
- 零样本 → 全零不抛；
- 输入校验 fail-closed。
纯内存夹具，不触库。
"""

from __future__ import annotations

import pytest

from zephyr.signal_ashare.sentiment_cycle import SentimentPhase
from zephyr.signal_ashare.sentiment_cycle_evaluator import (
    PhasePredictionRecord,
    evaluate_from_records,
    evaluate_locator_accuracy,
)


def test_evaluate_locator_accuracy_exact_match():
    """全对 → accuracy=1.0，adjacent=0.0。"""
    phases = [SentimentPhase.FERMENTING] * 10
    result = evaluate_locator_accuracy(phases, phases)
    assert result["accuracy"] == 1.0
    assert result["adjacent_tolerance_rate"] == 0.0
    assert result["n_samples"] == 10.0


def test_evaluate_locator_accuracy_adjacent_tolerance():
    """相邻阶段错判计入容错率。"""
    predicted = [SentimentPhase.FERMENTING, SentimentPhase.CONSENSUS]
    actual = [SentimentPhase.FERMENTING, SentimentPhase.FERMENTING]
    result = evaluate_locator_accuracy(predicted, actual)
    assert result["accuracy"] == 0.5
    assert result["adjacent_tolerance_rate"] == 0.5


def test_evaluate_locator_accuracy_length_mismatch_fail_closed():
    """长度不一致 → ValueError。"""
    with pytest.raises(ValueError):
        evaluate_locator_accuracy([SentimentPhase.FERMENTING], [])


def test_evaluate_from_records_zero_samples():
    """零样本 → 全零 + notes 留痕。"""
    report = evaluate_from_records([])
    assert report.n_samples == 0
    assert report.accuracy == 0.0
    assert "零样本" in report.notes[0]


def test_evaluate_from_records_per_phase_recall():
    """分阶段召回率：各阶段独立统计。"""
    records = [
        PhasePredictionRecord("2026-08-01", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING),
        PhasePredictionRecord("2026-08-02", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING),
        PhasePredictionRecord("2026-08-03", SentimentPhase.CONSENSUS, SentimentPhase.CONSENSUS),
        PhasePredictionRecord("2026-08-04", SentimentPhase.FERMENTING, SentimentPhase.CONSENSUS),
    ]
    report = evaluate_from_records(records)
    assert report.n_samples == 4
    assert report.per_phase_recall["主升"] == 1.0   # 2/2
    assert report.per_phase_recall["疯狂"] == 0.5   # 1/2


def test_evaluate_from_records_confusion_matrix():
    """混淆矩阵计数正确。"""
    records = [
        PhasePredictionRecord("2026-08-01", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING),
        PhasePredictionRecord("2026-08-02", SentimentPhase.CONSENSUS, SentimentPhase.FERMENTING),
    ]
    report = evaluate_from_records(records)
    assert report.confusion_matrix["主升"]["主升"] == 1
    assert report.confusion_matrix["主升"]["疯狂"] == 1
    assert report.confusion_matrix["疯狂"]["疯狂"] == 0


def test_evaluate_from_records_unsorted_input_sorted():
    """乱序输入自动按 trade_date 升序重排。"""
    records = [
        PhasePredictionRecord("2026-08-02", SentimentPhase.CONSENSUS, SentimentPhase.CONSENSUS),
        PhasePredictionRecord("2026-08-01", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING),
    ]
    report = evaluate_from_records(records)
    assert report.n_samples == 2
    assert report.accuracy == 1.0


def test_evaluate_from_records_invalid_trade_date_fail_closed():
    """trade_date 非法 → ValueError。"""
    records = [
        PhasePredictionRecord("", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING),
    ]
    with pytest.raises(ValueError):
        evaluate_from_records(records)


def test_evaluate_from_records_small_sample_note():
    """样本 <30 → notes 留痕。"""
    records = [
        PhasePredictionRecord(f"2026-08-{i:02d}", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING)
        for i in range(1, 10)
    ]
    report = evaluate_from_records(records)
    assert any("< 30" in note for note in report.notes)


def test_to_dict_json_serializable():
    """报告 JSON 可序列化。"""
    import json

    records = [
        PhasePredictionRecord("2026-08-01", SentimentPhase.FERMENTING, SentimentPhase.FERMENTING),
    ]
    report = evaluate_from_records(records)
    payload = json.loads(json.dumps(report.to_dict(), ensure_ascii=False))
    assert payload["n_samples"] == 1
    assert payload["accuracy"] == 1.0
