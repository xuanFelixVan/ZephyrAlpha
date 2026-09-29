# [BLUEPRINT] MOD-RPT-037 | docs/03_modules/_domain_reporting/report_archive_sink/blueprint.md | §
# [MODULE] tests.reporting.test_report_archive_sink
# [DOMAIN] D_REPORTING
# [TTL] permanent
"""F115 R2 归档链薄刀测试——JsonlArchiveSink + ReportPublisher 注入位。

覆盖：
- persist 落盘 append-only（父目录惰性构造）/ load_records 读回 / 坏行跳过
- last_record_hash 尾哈希（空盘/正常/坏行容忍）
- publisher 注入位：publish 自动落盘 / 未注入不落盘（现状不破坏）/ 持久化失败降级
- 跨进程哈希链连续（新 publisher 以盘面尾哈希接链）
- verify_chain 与 sink 共存

测试隔离：tmp_path 落点，零生产路径（data/ 业务目录禁触）；worktree 解析走
ZEPHYR_ALPHA_ROOT 环境变量（usercustomize 官方开关，禁 sys.modules 级清洗——
模块级清洗毒化同进程兄弟测试，#ARCH-107 探针领地）。
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.reporting.report_archive_sink import (  # noqa: E402
    DEFAULT_ARCHIVE_FILENAME,
    JsonlArchiveSink,
    load_report_records,
    record_to_dict,
)
from zephyr.reporting.report_publisher import ArchivedReport, ReportPublisher, ReportSource  # noqa: E402


def _make_report(report_id: str = "RPT-1", content: dict | None = None) -> ArchivedReport:
    return ArchivedReport(
        archive_id=f"ARCH-{report_id}",
        report_id=report_id,
        source=ReportSource.RISK,
        report_type="daily_risk_review",
        archived_at=datetime(2026, 9, 28, 15, 0, tzinfo=UTC),
        content=content or {"k": "v"},
        content_hash="ch",
        prev_hash="",
        record_hash=f"rh-{report_id}",
    )


class TestJsonlArchiveSink:
    def test_persist_appends_and_parent_dirs_created(self, tmp_path: Path) -> None:
        target = tmp_path / "deep" / "dir" / DEFAULT_ARCHIVE_FILENAME
        sink = JsonlArchiveSink(target)
        out = sink.persist(_make_report("R1"))
        assert out == target and target.exists()
        sink.persist(_make_report("R2"))
        lines = target.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2  # append-only：两行
        rec = json.loads(lines[0])
        assert rec["report_id"] == "R1" and rec["record_hash"] == "rh-R1"

    def test_load_records_roundtrip_and_missing_file(self, tmp_path: Path) -> None:
        sink = JsonlArchiveSink(tmp_path / "a.jsonl")
        assert sink.load_records() == []  # 文件缺失 → 空列表不抛
        sink.persist(_make_report("R1"))
        records = load_report_records(tmp_path / "a.jsonl")
        assert len(records) == 1 and records[0]["source"] == "risk"

    def test_load_records_skips_corrupt_lines(self, tmp_path: Path) -> None:
        target = tmp_path / "a.jsonl"
        sink = JsonlArchiveSink(target)
        sink.persist(_make_report("R1"))
        with target.open("a", encoding="utf-8") as fh:
            fh.write("{corrupt-json\n")
        sink.persist(_make_report("R2"))
        records = sink.load_records()
        assert [r["report_id"] for r in records] == ["R1", "R2"]  # 坏行跳过不抛

    def test_last_record_hash_empty_and_corrupt_tolerant(self, tmp_path: Path) -> None:
        sink = JsonlArchiveSink(tmp_path / "none.jsonl")
        assert sink.last_record_hash() == ""  # 空盘
        target = tmp_path / "a.jsonl"
        sink2 = JsonlArchiveSink(target)
        sink2.persist(_make_report("R1"))
        with target.open("a", encoding="utf-8") as fh:
            fh.write("garbage-line\n")
        sink2.persist(_make_report("R2"))
        assert sink2.last_record_hash() == "rh-R2"  # 尾=最后可解析记录

    def test_record_to_dict_shapes(self) -> None:
        d = record_to_dict(_make_report())
        assert d["source"] == "risk" and d["archived_at"].endswith("+00:00")


class _BoomSink:
    """persist 恒炸的病 sink——降级路径测试用。"""

    def persist(self, report: ArchivedReport) -> object:
        raise OSError("disk full")

    def last_record_hash(self) -> str:
        raise OSError("io error")


class TestPublisherSinkWiring:
    def test_publish_persists_and_no_sink_untouched(self, tmp_path: Path) -> None:
        target = tmp_path / "a.jsonl"
        pub = ReportPublisher(archive_sink=JsonlArchiveSink(target))
        archived = pub.publish(
            report_id="R1", source=ReportSource.RISK, report_type="daily_risk_review", content={"a": 1}
        )
        records = load_report_records(target)
        assert len(records) == 1 and records[0]["archive_id"] == archived.archive_id
        # 现状不破坏：未注入 sink → 不落任何盘面文件
        pub2 = ReportPublisher()
        pub2.publish(report_id="R2", source=ReportSource.RISK, report_type="t", content={"b": 2})
        assert pub2.archive_count == 1

    def test_cross_process_chain_continuity(self, tmp_path: Path) -> None:
        target = tmp_path / "a.jsonl"
        sink = JsonlArchiveSink(target)
        pub1 = ReportPublisher(archive_sink=sink)
        first = pub1.publish(report_id="R1", source=ReportSource.RISK, report_type="t", content={"n": 1})
        # 进程重启语义：全新 publisher（内存链为空）+ 同盘面 sink
        pub2 = ReportPublisher(archive_sink=JsonlArchiveSink(target))
        second = pub2.publish(report_id="R2", source=ReportSource.RISK, report_type="t", content={"n": 2})
        assert second.prev_hash == first.record_hash  # 盘面尾哈希接链（重启不再空链）

    def test_sink_failure_degrades_not_blocks(self, tmp_path: Path) -> None:
        pub = ReportPublisher(archive_sink=_BoomSink())
        archived = pub.publish(report_id="R1", source=ReportSource.RISK, report_type="t", content={"a": 1})
        assert archived.report_id == "R1"  # 持久化炸 → 内存归档主链不阻断
        assert pub.verify_chain() is True

    def test_verify_chain_with_sink_wired(self, tmp_path: Path) -> None:
        pub = ReportPublisher(archive_sink=JsonlArchiveSink(tmp_path / "a.jsonl"))
        for i in range(3):
            pub.publish(report_id=f"R{i}", source=ReportSource.RISK, report_type="t", content={"i": i})
        assert pub.verify_chain() is True

    def test_tail_prev_hash_exception_degrades_empty(self) -> None:
        pub = ReportPublisher(archive_sink=_BoomSink())
        archived = pub.publish(report_id="R1", source=ReportSource.RISK, report_type="t", content={"a": 1})
        assert archived.prev_hash == ""  # 尾哈希读取异常 → 空串起链（降级）


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-q"])
