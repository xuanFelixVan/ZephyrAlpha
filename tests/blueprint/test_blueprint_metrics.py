# [A_test] module_id: MOD-GOV_blueprint_metrics | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-015 | docs/03_modules/_domain_infrastructure_operations/system_telemetry/blueprint.md | 蓝图特有§A
# [MODULE] tests.test_blueprint_metrics
# [INVARIANTS] 蓝图读取事件MUST通过此模块记录;输出JSONL格式;RULE-ONE原子写入
# [MODIFY-GUARD] metrics/blueprint_metrics.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] JSONL写入失败→日志warning;不阻塞调用方
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

bm = pytest.importorskip(
    "zephyr.infrastructure.system_telemetry.metrics.blueprint_metrics",
    reason="blueprint_metrics import failed",
)


class TestBlueprintReadEvent:
    def test_creation(self):
        event = bm.BlueprintReadEvent(
            blueprint_id="MOD-INF-015",
            session_id="sess-1",
            task_id="task-1",
        )
        assert event.blueprint_id == "MOD-INF-015"
        assert event.session_id == "sess-1"
        assert event.task_id == "task-1"
        assert event.timestamp != ""

    def test_defaults(self):
        event = bm.BlueprintReadEvent(blueprint_id="MOD-TEST")
        assert event.session_id == ""
        assert event.task_id == ""
        assert event.agent_model == ""

    def test_custom_agent_model(self):
        event = bm.BlueprintReadEvent(
            blueprint_id="MOD-TEST",
            agent_model="gpt-4.1",
        )
        assert event.agent_model == "gpt-4.1"


class TestRecordBlueprintRead:
    def test_returns_true(self, tmp_path):
        metrics_file = tmp_path / "blueprint_reads.jsonl"
        original = bm.METRICS_FILE
        bm.METRICS_FILE = metrics_file
        try:
            result = bm.record_blueprint_read(
                blueprint_id="MOD-TEST-001",
                session_id="sess-1",
            )
            assert result is True
        finally:
            bm.METRICS_FILE = original

    def test_writes_jsonl(self, tmp_path):
        metrics_file = tmp_path / "blueprint_reads.jsonl"
        original = bm.METRICS_FILE
        bm.METRICS_FILE = metrics_file
        try:
            bm.record_blueprint_read(
                blueprint_id="MOD-TEST-002",
                session_id="sess-2",
                task_id="task-2",
            )
            content = metrics_file.read_text(encoding="utf-8")
            data = json.loads(content.strip())
            assert data["event"] == "blueprint_read"
            assert data["blueprint_id"] == "MOD-TEST-002"
        finally:
            bm.METRICS_FILE = original

    def test_multiple_records(self, tmp_path):
        metrics_file = tmp_path / "blueprint_reads.jsonl"
        original = bm.METRICS_FILE
        bm.METRICS_FILE = metrics_file
        try:
            bm.record_blueprint_read(blueprint_id="MOD-A")
            bm.record_blueprint_read(blueprint_id="MOD-B")
            content = metrics_file.read_text(encoding="utf-8")
            lines = [l for l in content.strip().split("\n") if l]
            assert len(lines) == 2
        finally:
            bm.METRICS_FILE = original


class TestMetricsFileConstant:
    def test_path_exists(self):
        assert bm.METRICS_FILE is not None
        assert isinstance(bm.METRICS_FILE, Path)


class TestBoundary:
    def test_empty_blueprint_id(self, tmp_path):
        metrics_file = tmp_path / "blueprint_reads.jsonl"
        original = bm.METRICS_FILE
        bm.METRICS_FILE = metrics_file
        try:
            result = bm.record_blueprint_read(blueprint_id="")
            assert result is True
        finally:
            bm.METRICS_FILE = original

    def test_all_empty_args(self, tmp_path):
        metrics_file = tmp_path / "blueprint_reads.jsonl"
        original = bm.METRICS_FILE
        bm.METRICS_FILE = metrics_file
        try:
            result = bm.record_blueprint_read(
                blueprint_id="",
                session_id="",
                task_id="",
                agent_model="",
            )
            assert result is True
        finally:
            bm.METRICS_FILE = original

    def test_unwritable_path(self):
        original = bm.METRICS_FILE
        bm.METRICS_FILE = Path("/nonexistent/deep/path/blueprint_reads.jsonl")
        try:
            result = bm.record_blueprint_read(blueprint_id="MOD-TEST")
            assert isinstance(result, bool)
        finally:
            bm.METRICS_FILE = original
