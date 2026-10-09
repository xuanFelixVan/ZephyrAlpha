# [A_test] module_id: MOD-GOV_test_decision_snapshot | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.signal_fundamental.audit.test_decision_snapshot
# [TESTS] src/zephyr/signal_fundamental/audit/decision_snapshot.py
# [TTL] task_bound
"""C-030 决策溯源链 Phase 2 候选（90 号 §22.5）：结构化决策快照最小实现 toy 断言。

裁定真源：90_methodology_open_questions.md §22.5——
  MVP 阶段先用结构化日志（决策时快照输入因子值+触发规则 id）低成本实现 80% 价值；
  契约：溯源链=决策 id → 触发信号列表+因子贡献度+数据版本引用；
  降级：可解释性缺失时降级人工复核（不阻塞交易链路）。
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from zephyr.signal_fundamental.audit.decision_snapshot import (
    DecisionSnapshot,
    DecisionSnapshotRecorder,
)

_NOW = datetime(2026, 8, 19, 14, 30, tzinfo=timezone.utc)


def _snapshot(**overrides) -> DecisionSnapshot:
    base = {
        "decision_id": "dec-001",
        "timestamp": _NOW,
        "strategy_id": "STR-DABAN-001",
        "symbol": "600000.SH",
        "action": "buy",
        "input_factors": {"seal_ratio": 0.07, "volume_ratio": 1.8},
        "triggered_rule_ids": ("RULE-SEAL-001", "RULE-VOL-002"),
        "factor_contributions": {"seal_ratio": 0.6, "volume_ratio": 0.4},
        "data_versions": {"universe": "UNI-DYNAMIC-001@2026-08-19"},
        "confidence": 0.82,
    }
    return DecisionSnapshot(**(base | overrides))


class TestSnapshot:
    def test_record_and_get_roundtrip(self):
        rec = DecisionSnapshotRecorder()
        rec.record(_snapshot())
        got = rec.get("dec-001")
        assert got is not None
        assert got.input_factors["seal_ratio"] == 0.07
        assert got.triggered_rule_ids == ("RULE-SEAL-001", "RULE-VOL-002")
        assert got.data_versions["universe"] == "UNI-DYNAMIC-001@2026-08-19"

    def test_query_by_symbol_and_strategy(self):
        rec = DecisionSnapshotRecorder()
        rec.record(_snapshot())
        rec.record(_snapshot(decision_id="dec-002", symbol="000001.SZ"))
        assert [s.decision_id for s in rec.query(symbol="600000.SH")] == ["dec-001"]
        assert [s.decision_id for s in rec.query(strategy_id="STR-DABAN-001")] == ["dec-001", "dec-002"]

    def test_jsonl_persistence(self, tmp_path):
        """结构化日志：JSONL 追加写 + 读回（Owner 复盘溯源）。"""
        log = tmp_path / "decisions.jsonl"
        rec = DecisionSnapshotRecorder(log_path=log)
        rec.record(_snapshot())
        rec.record(_snapshot(decision_id="dec-002"))
        loaded = DecisionSnapshotRecorder.load_log(log)
        assert [s.decision_id for s in loaded] == ["dec-001", "dec-002"]
        assert loaded[0].confidence == 0.82

    def test_missing_explainability_degraded_not_blocked(self):
        """降级语义：因子/规则快照缺失 → degraded=True（人工复核），仍可记录不阻塞。"""
        snap = _snapshot(input_factors={}, triggered_rule_ids=())
        assert snap.degraded is True
        rec = DecisionSnapshotRecorder()
        rec.record(snap)  # 不抛异常=不阻塞交易链路
        assert rec.get("dec-001").degraded is True

    def test_full_evidence_not_degraded(self):
        assert _snapshot().degraded is False

    def test_empty_decision_id_raises(self):
        with pytest.raises(ValueError):
            _snapshot(decision_id="")

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(ValueError):
            _snapshot(confidence=1.5)
