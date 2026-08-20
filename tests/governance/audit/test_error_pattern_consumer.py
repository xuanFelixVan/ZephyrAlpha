# [BLUEPRINT] MOD-GOV_ASSET_INDEX_RECONCILER | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: SRC-TST-3004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_error_pattern_consumer.py — P4-1b error_pattern_consumer_reconciler 单测

权威依据：error_pattern_consumer_reconciler.py（#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b）
- compute_error_pattern_id: SHA1 指纹计算（EP- 前缀 + 16 字符 hex）
- aggregate_error_patterns: JSONL 扫描 + 过滤 + 聚合 + 持久化
- make_error_pattern_consumer_reconciler: post-commit reconciler 工厂

测试组：
- TestComputeErrorPatternId: 指纹计算 / 确定性 / 格式
- TestAggregateErrorPatterns: 空目录 / 单事件 / 同指纹聚合 / 异指纹分离
- TestEventFiltering: 非 ai_behavior 事件跳过 / 无 error 事件跳过
- TestPersistenceAndIdempotency: 输出文件有效 JSON / 多次运行幂等
- TestReconcilerFactory: reconciler trigger / clean / warn
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import zephyr.governance.audit.error_pattern_consumer_reconciler as consumer_mod
from zephyr.governance.audit.error_pattern_consumer_reconciler import (
    aggregate_error_patterns,
    compute_error_pattern_id,
    make_error_pattern_consumer_reconciler,
)
from zephyr.governance.audit.reconciliation_registry import ReconcileResult


def _make_event(
    error_type: str = "ConnectionError",
    persistence: str = "transient",
    source: str = "dependency",
    expectation: str = "unexpected",
    severity: str = "blocking",
    ts: str = "2026-07-20T10:00:00+00:00",
    labels_type: str = "ai_behavior_event",
    has_error: bool = True,
) -> dict[str, Any]:
    """构造一条 AI behavior event JSON（对标 event_sink.snapshot + structured_sink）。"""
    entry: dict[str, Any] = {
        "ts": ts,
        "labels": {"__type": labels_type},
        "event_id": "test-evt-001",
        "model": {"name": "test-model", "version": "1.0"},
    }
    if has_error:
        entry["error"] = {
            "error_type": error_type,
            "persistence": persistence,
            "source": source,
            "expectation": expectation,
            "severity": severity,
            "retries": 0,
            "backoff_ms": 0.0,
        }
    return entry


def _write_jsonl(telemetry_dir: Path, filename: str, events: list[dict[str, Any]]) -> Path:
    """写一个 JSONL 文件（每行一个 JSON 事件）。"""
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    path = telemetry_dir / filename
    lines = "\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\n"
    path.write_text(lines, encoding="utf-8")
    return path


class TestComputeErrorPatternId:
    """指纹计算 / 确定性 / 格式。"""

    def test_deterministic_same_inputs(self) -> None:
        id1 = compute_error_pattern_id("ConnectionError", "transient", "dependency")
        id2 = compute_error_pattern_id("ConnectionError", "transient", "dependency")
        assert id1 == id2

    def test_different_inputs_different_ids(self) -> None:
        id1 = compute_error_pattern_id("ConnectionError", "transient", "dependency")
        id2 = compute_error_pattern_id("TimeoutError", "transient", "dependency")
        assert id1 != id2

    def test_format_has_ep_prefix(self) -> None:
        pid = compute_error_pattern_id("X", "Y", "Z")
        assert pid.startswith("EP-")
        # EP- + 16 hex chars
        assert len(pid) == 3 + 16

    def test_order_matters(self) -> None:
        """persistence 和 source 交换应产生不同 ID（不同错误模式）。"""
        id1 = compute_error_pattern_id("Err", "transient", "dependency")
        id2 = compute_error_pattern_id("Err", "dependency", "transient")
        assert id1 != id2


class TestAggregateErrorPatterns:
    """空目录 / 单事件 / 同指纹聚合 / 异指纹分离。"""

    def test_empty_dir_returns_empty_patterns(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 0
        assert result["patterns"] == []
        assert result["version"] == "1.0"
        # 输出文件已创建
        assert output_path.exists()

    def test_nonexistent_dir_returns_empty(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "nonexistent"
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 0

    def test_single_event_produces_one_pattern(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", [_make_event()])
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 1
        assert len(result["patterns"]) == 1
        pat = result["patterns"][0]
        assert pat["error_type"] == "ConnectionError"
        assert pat["persistence"] == "transient"
        assert pat["source"] == "dependency"
        assert pat["count"] == 1
        assert pat["pattern_id"].startswith("EP-")

    def test_same_fingerprint_aggregates_count(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        events = [
            _make_event(ts="2026-07-20T10:00:00+00:00"),
            _make_event(ts="2026-07-20T11:00:00+00:00"),
            _make_event(ts="2026-07-20T12:00:00+00:00"),
        ]
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", events)
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 3
        assert len(result["patterns"]) == 1
        pat = result["patterns"][0]
        assert pat["count"] == 3
        assert pat["first_seen"] == "2026-07-20T10:00:00+00:00"
        assert pat["last_seen"] == "2026-07-20T12:00:00+00:00"

    def test_different_fingerprints_produce_multiple_patterns(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        events = [
            _make_event(error_type="ConnectionError", persistence="transient", source="dependency"),
            _make_event(error_type="TimeoutError", persistence="transient", source="dependency"),
            _make_event(error_type="ConnectionError", persistence="permanent", source="internal"),
        ]
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", events)
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 3
        assert len(result["patterns"]) == 3

    def test_distribution_accumulated(self, tmp_path: Path) -> None:
        """expectation_dist / severity_dist 累加。"""
        telemetry_dir = tmp_path / "telemetry"
        events = [
            _make_event(expectation="expected", severity="degraded"),
            _make_event(expectation="unexpected", severity="blocking"),
            _make_event(expectation="unexpected", severity="blocking"),
        ]
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", events)
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        pat = result["patterns"][0]
        assert pat["expectation_dist"] == {"expected": 1, "unexpected": 2}
        assert pat["severity_dist"] == {"degraded": 1, "blocking": 2}

    def test_multiple_jsonl_files_scanned(self, tmp_path: Path) -> None:
        """多日 JSONL 文件都被扫描。"""
        telemetry_dir = tmp_path / "telemetry"
        _write_jsonl(telemetry_dir, "telemetry_2026-07-19.jsonl", [_make_event(ts="2026-07-19T10:00:00+00:00")])
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", [_make_event(ts="2026-07-20T10:00:00+00:00")])
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 2
        assert len(result["patterns"]) == 1
        assert result["patterns"][0]["first_seen"] == "2026-07-19T10:00:00+00:00"
        assert result["patterns"][0]["last_seen"] == "2026-07-20T10:00:00+00:00"


class TestEventFiltering:
    """非 ai_behavior 事件跳过 / 无 error 事件跳过 / 损坏行跳过。"""

    def test_non_ai_behavior_event_skipped(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        events = [
            _make_event(labels_type="other_type"),
            _make_event(),  # valid
        ]
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", events)
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 1

    def test_event_without_error_skipped(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        events = [
            _make_event(has_error=False),
            _make_event(),  # valid
        ]
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", events)
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 1

    def test_event_without_labels_skipped(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        events = [
            {"ts": "2026-07-20T10:00:00+00:00", "error": {"error_type": "X"}},  # no labels
            _make_event(),  # valid
        ]
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", events)
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 1

    def test_corrupted_json_line_skipped(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        # 混合有效/损坏行
        valid_line = json.dumps(_make_event())
        corrupted_line = "{not valid json"
        empty_line = ""
        content = f"{corrupted_line}\n{empty_line}\n{valid_line}\n"
        telemetry_dir.mkdir(parents=True, exist_ok=True)
        (telemetry_dir / "telemetry_2026-07-20.jsonl").write_text(content, encoding="utf-8")
        output_path = tmp_path / "out" / "patterns.json"
        result = aggregate_error_patterns(telemetry_dir, output_path)
        assert result["total_events"] == 1


class TestPersistenceAndIdempotency:
    """输出文件有效 JSON / 多次运行幂等。"""

    def test_output_file_is_valid_json(self, tmp_path: Path) -> None:
        telemetry_dir = tmp_path / "telemetry"
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", [_make_event()])
        output_path = tmp_path / "out" / "patterns.json"
        aggregate_error_patterns(telemetry_dir, output_path)
        assert output_path.exists()
        loaded = json.loads(output_path.read_text(encoding="utf-8"))
        assert loaded["version"] == "1.0"
        assert loaded["total_events"] == 1
        assert len(loaded["patterns"]) == 1

    def test_idempotent_same_input_same_output(self, tmp_path: Path) -> None:
        """多次运行产生相同 patterns（last_updated 除外，因为每次运行会更新）。"""
        telemetry_dir = tmp_path / "telemetry"
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", [_make_event(), _make_event()])
        output_path = tmp_path / "out" / "patterns.json"
        r1 = aggregate_error_patterns(telemetry_dir, output_path)
        r2 = aggregate_error_patterns(telemetry_dir, output_path)
        # patterns 内容一致（last_updated 时间戳可能不同）
        assert r1["total_events"] == r2["total_events"]
        assert r1["patterns"] == r2["patterns"]

    def test_output_dir_auto_created(self, tmp_path: Path) -> None:
        """输出目录不存在时自动创建。"""
        telemetry_dir = tmp_path / "telemetry"
        _write_jsonl(telemetry_dir, "telemetry_2026-07-20.jsonl", [_make_event()])
        output_path = tmp_path / "deep" / "nested" / "dir" / "patterns.json"
        aggregate_error_patterns(telemetry_dir, output_path)
        assert output_path.exists()


class TestReconcilerFactory:
    """reconciler trigger / clean / warn。"""

    def test_trigger_always_true(self, tmp_path: Path) -> None:
        class _FakeGateway:
            project_root = tmp_path

        spec = make_error_pattern_consumer_reconciler(_FakeGateway())
        assert spec.gate_id == "GATE-ERROR-PATTERN-CONSUMER"
        assert spec.priority == 880
        assert spec.trigger(["any_file.py"]) is True
        assert spec.trigger([]) is True

    def test_reconcile_clean_when_no_events(self, tmp_path: Path) -> None:
        class _FakeGateway:
            project_root = tmp_path

        spec = make_error_pattern_consumer_reconciler(_FakeGateway())
        result: ReconcileResult = spec.reconcile(["file.py"], "sess-test")
        assert result.action == "clean"
        assert result.gate_id == "GATE-ERROR-PATTERN-CONSUMER"
        assert "no" in result.detail.lower() or "0" in result.detail

    def test_reconcile_clean_when_events_aggregated(self, tmp_path: Path) -> None:
        class _FakeGateway:
            project_root = tmp_path

        telemetry_dir = tmp_path / "data" / "telemetry" / "prod" / "logs"
        _write_jsonl(
            telemetry_dir, "telemetry_2026-07-20.jsonl", [_make_event(), _make_event(error_type="TimeoutError")]
        )
        spec = make_error_pattern_consumer_reconciler(_FakeGateway())
        result = spec.reconcile(["file.py"], "sess-test")
        assert result.action == "clean"
        assert "2" in result.detail  # 2 events
        # 输出文件已写到 .runtime/ai_error_patterns/aggregated_patterns.json
        output = tmp_path / ".runtime" / "ai_error_patterns" / "aggregated_patterns.json"
        assert output.exists()

    def test_reconcile_warn_on_aggregation_failure(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """aggregate_error_patterns 抛异常时降级为 warn（reconciler 永不抛异常）。"""

        class _FakeGateway:
            project_root = tmp_path

        def _boom(_telemetry_dir: Path, _output_path: Path) -> dict:
            raise RuntimeError("simulated failure")

        monkeypatch.setattr(consumer_mod, "aggregate_error_patterns", _boom)
        spec = make_error_pattern_consumer_reconciler(_FakeGateway())
        result = spec.reconcile(["file.py"], "sess-test")
        assert result.action == "warn"
        assert "simulated failure" in result.detail


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
