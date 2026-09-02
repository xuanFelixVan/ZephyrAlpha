# [BLUEPRINT] MOD-DATA_GOV-011 | docs/03_modules/_domain_data_governance/openlineage_exporter/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-011 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_governance.test_openlineage_exporter
# [TESTS] src/zephyr/data_governance/openlineage_exporter.py
"""MOD-DATA_GOV-011 单元测试：openlineage_exporter OpenLineage 事件导出器。

蓝图验收（B10-02320/CAND-DATGOV-008，A1 M8-NEW-01）：
RunEvent 五要素（eventType/run/job/inputs/outputs/facets）+ 内部边转换器 +
JSONL 导出（追加写注入 root / line_sink 内存替身）+ 必填校验闭合。
line_sink 注入内存替身为主，落盘路径仅用 tmp_path 验证追加语义。
"""

from __future__ import annotations

import datetime
import json

import pytest

pytest.importorskip(
    "zephyr.data_governance.openlineage_exporter",
    reason="openlineage_exporter not importable",
)

from zephyr.data_governance.openlineage_exporter import (  # noqa: E402
    EventType,
    OpenLineageError,
    OpenLineageExporter,
    RunEvent,
    edge_to_event,
    event_to_jsonl,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _event(**kw) -> RunEvent:
    base = {
        "event_type": EventType.COMPLETE,
        "run_id": "run-001",
        "job_namespace": "zephyr.lineage",
        "job_name": "compute",
        "inputs": ("market.kline",),
        "outputs": ("factor.mom20",),
        "facets": {"engine": "duckdb"},
        "event_time": _T0,
    }
    base.update(kw)
    return RunEvent(**base)


def _exporter(lines: list) -> OpenLineageExporter:
    return OpenLineageExporter(clock=lambda: _T0, line_sink=lines.append)


# ──────────────────────────────────────────────────────────────────────────────
# RunEvent 校验（必填闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestValidate:
    def test_event_frozen(self) -> None:
        e = _event()
        with pytest.raises(AttributeError):
            e.run_id = "x"  # type: ignore[misc]

    def test_valid_event_passes(self) -> None:
        line = event_to_jsonl(_event())
        assert json.loads(line)["eventType"] == "COMPLETE"

    def test_invalid_event_type_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            event_to_jsonl(_event(event_type="BOGUS"))

    def test_empty_run_id_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            event_to_jsonl(_event(run_id=""))

    def test_empty_job_namespace_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            event_to_jsonl(_event(job_namespace=""))

    def test_empty_job_name_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            event_to_jsonl(_event(job_name=""))

    def test_empty_dataset_name_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            event_to_jsonl(_event(inputs=("",)))


# ──────────────────────────────────────────────────────────────────────────────
# 序列化（五要素 + 确定性）
# ──────────────────────────────────────────────────────────────────────────────


class TestSerialization:
    def test_five_elements_present(self) -> None:
        payload = json.loads(event_to_jsonl(_event()))
        for key in ("eventType", "run", "job", "inputs", "outputs", "facets"):
            assert key in payload
        assert payload["run"] == {"runId": "run-001"}
        assert payload["job"] == {"namespace": "zephyr.lineage", "name": "compute"}
        assert payload["inputs"] == [{"namespace": "zephyr.lineage", "name": "market.kline"}]
        assert payload["outputs"] == [{"namespace": "zephyr.lineage", "name": "factor.mom20"}]

    def test_serialization_deterministic(self) -> None:
        e = _event()
        assert event_to_jsonl(e) == event_to_jsonl(e)

    def test_event_time_isoformat(self) -> None:
        payload = json.loads(event_to_jsonl(_event()))
        assert payload["eventTime"] == _T0.isoformat()

    def test_io_order_preserved(self) -> None:
        payload = json.loads(event_to_jsonl(_event(inputs=("b.t", "a.t"))))
        assert [d["name"] for d in payload["inputs"]] == ["b.t", "a.t"]


# ──────────────────────────────────────────────────────────────────────────────
# 边转换器
# ──────────────────────────────────────────────────────────────────────────────


class TestEdgeConversion:
    def test_edge_to_event_uses_transformation_as_job(self) -> None:
        e = edge_to_event(
            ("market.kline", "factor.mom20", "compute"),
            run_id="r1",
            job_namespace="ns",
            event_time=_T0,
        )
        assert e.job_name == "compute"
        assert e.inputs == ("market.kline",)
        assert e.outputs == ("factor.mom20",)

    def test_edge_to_event_default_job_name(self) -> None:
        e = edge_to_event(("a", "b", ""), run_id="r1", job_namespace="ns")
        assert e.job_name == "a->b"

    def test_invalid_edge_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            edge_to_event(("", "b", "t"), run_id="r1", job_namespace="ns")
        with pytest.raises(OpenLineageError):
            edge_to_event(("a", "", "t"), run_id="r1", job_namespace="ns")


# ──────────────────────────────────────────────────────────────────────────────
# 导出器
# ──────────────────────────────────────────────────────────────────────────────


class TestExporter:
    def test_no_root_no_sink_raises(self) -> None:
        with pytest.raises(OpenLineageError):
            OpenLineageExporter()

    def test_export_to_line_sink(self) -> None:
        lines: list[str] = []
        exp = _exporter(lines)
        line = exp.export(_event())
        assert lines == [line]

    def test_export_invalid_event_writes_nothing(self) -> None:
        lines: list[str] = []
        exp = _exporter(lines)
        with pytest.raises(OpenLineageError):
            exp.export(_event(run_id=""))
        assert lines == []

    def test_export_edges_batch(self) -> None:
        lines: list[str] = []
        exp = _exporter(lines)
        out = exp.export_edges(
            [("market.kline", "factor.mom20", "compute"), ("factor.mom20", "signal.alpha", "generate")],
            run_id="r1",
            job_namespace="zephyr.lineage",
        )
        assert len(out) == 2 and len(lines) == 2
        jobs = [json.loads(line)["job"]["name"] for line in lines]
        assert jobs == ["compute", "generate"]

    def test_export_edges_event_time_from_clock(self) -> None:
        lines: list[str] = []
        exp = _exporter(lines)
        exp.export_edges([("a", "b", "t")], run_id="r1", job_namespace="ns")
        assert json.loads(lines[0])["eventTime"] == _T0.isoformat()

    def test_sink_failure_wrapped(self) -> None:
        def bad_sink(line: str) -> None:
            raise OSError("disk full")

        exp = OpenLineageExporter(clock=lambda: _T0, line_sink=bad_sink)
        with pytest.raises(OpenLineageError):
            exp.export(_event())

    def test_file_append_root(self, tmp_path) -> None:
        exp = OpenLineageExporter(root=tmp_path, clock=lambda: _T0)
        exp.export(_event(run_id="r1"))
        exp.export(_event(run_id="r2"))
        path = tmp_path / "openlineage_events.jsonl"
        rows = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(rows) == 2  # 追加写
        assert json.loads(rows[1])["run"]["runId"] == "r2"

    def test_custom_file_name(self, tmp_path) -> None:
        exp = OpenLineageExporter(root=tmp_path, clock=lambda: _T0, file_name="x.jsonl")
        exp.export(_event())
        assert (tmp_path / "x.jsonl").exists()
