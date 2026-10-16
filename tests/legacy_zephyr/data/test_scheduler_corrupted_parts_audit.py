# [BLUEPRINT] MOD-L00-004 | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""scheduler 破损 part 检测建档单测（图12 F1z E-7 首触发即建档，Owner 批 2026-10-04）。

红绿测试（呈批件 F1Z E-7）：
- 红→绿：构造 text_log 破损 part 记录 → 断言 corrupted_parts_audit.jsonl
  首触发即建档（首条 action=detect；隔离成功后追加 action=detach）；part 不在
  active 列表也必须落档——修复前零病历的病根（只有隔离完成才写档）。
- 绿：无破损探测 → 不写档、档案文件保持不存在。
不依赖真实 ClickHouse/Alerter——query/find/isolate/notify 全部注入 stub。
"""

import json

from src.zephyr.data.scheduler import (
    _detect_corrupted_parts_from_log,
    _run_corrupted_part_cycle,
)


def _log_text(part_name: str) -> str:
    """模拟 system.text_log 中一条 CHECKSUM_DOESNT_MATCH 记录。"""
    return (
        "2026.10.04 12:00:00 [MergeThread] <Error> executeQuery: Code: 246. "
        f"Checksum doesn't match for part {part_name}"
    )


class TestFirstTriggerArchive:
    """E-7 红绿主锚：探测即建档 / 无损坏不建档。"""

    def test_detect_creates_archive_on_first_trigger(self, tmp_path):
        """构造损坏分区 → 断言建档：首条 action=detect，隔离成功追加 detach。"""
        audit_log = tmp_path / "local_fallback" / "corrupted_parts_audit.jsonl"
        processed: set[str] = set()
        notified: list[tuple] = []

        entries = _run_corrupted_part_cycle(
            audit_log=audit_log,
            query_log_fn=lambda: _log_text("202609_1_5_abc"),
            find_part_fn=lambda p: ("db_x", "t_y"),
            isolate_fn=lambda p, db, t: True,
            notify_fn=lambda *a, **k: notified.append(a),
            processed_parts=processed,
        )

        assert audit_log.exists(), "首触发必须建档"
        records = [json.loads(line) for line in audit_log.read_text(encoding="utf-8").splitlines()]
        assert [r["action"] for r in records] == ["detect", "detach"]
        assert records[0]["part_name"] == "202609_1_5_abc"
        assert records[0]["database"] == "db_x"
        assert records[0]["table"] == "t_y"
        assert records[0]["success"] is True
        assert records[0]["timestamp"]
        assert records[1]["success"] is True
        assert [e["action"] for e in entries] == ["detect", "detach"]
        assert processed == {"202609_1_5_abc"}
        assert len(notified) == 1, "隔离路径告警行为保留"

    def test_detect_archives_even_when_part_not_active(self, tmp_path):
        """part 不在 active 列表（修复前零病历病根）也必须落 detect 档案。"""
        audit_log = tmp_path / "audit.jsonl"

        def _isolate_must_not_run(p: str, db: str, t: str) -> bool:
            raise AssertionError("find=None 分支禁止触发隔离")

        entries = _run_corrupted_part_cycle(
            audit_log=audit_log,
            query_log_fn=lambda: _log_text("202610_2_6_def"),
            find_part_fn=lambda p: None,
            isolate_fn=_isolate_must_not_run,
            notify_fn=None,
            processed_parts=set(),
        )

        assert audit_log.exists(), "find=None 分支也必须建档"
        record = json.loads(audit_log.read_text(encoding="utf-8").splitlines()[0])
        assert record["action"] == "detect"
        assert record["success"] is False
        assert record["note"] == "part_not_in_active"
        assert len(entries) == 1

    def test_no_corruption_no_archive(self, tmp_path):
        """无损坏 → 不建：不写档，档案文件保持不存在。"""
        audit_log = tmp_path / "audit.jsonl"

        entries = _run_corrupted_part_cycle(
            audit_log=audit_log,
            query_log_fn=lambda: "2026.10.04 12:00:00 all normal, no checksum errors",
            find_part_fn=lambda p: ("db", "t"),
            isolate_fn=lambda p, db, t: True,
            notify_fn=None,
            processed_parts=set(),
        )

        assert not audit_log.exists()
        assert entries == []

    def test_repeat_detection_not_reprocessed(self, tmp_path):
        """已处理 part 不重复建档（processed_parts 去重语义保留）。"""
        audit_log = tmp_path / "audit.jsonl"
        processed = {"202609_3_7_ghi"}

        entries = _run_corrupted_part_cycle(
            audit_log=audit_log,
            query_log_fn=lambda: _log_text("202609_3_7_ghi"),
            find_part_fn=lambda p: ("db", "t"),
            isolate_fn=lambda p, db, t: True,
            notify_fn=None,
            processed_parts=processed,
        )

        assert not audit_log.exists()
        assert entries == []

    def test_isolation_failure_still_archived(self, tmp_path):
        """隔离失败（success=False）同样落全档案——成败皆有病历。"""
        audit_log = tmp_path / "audit.jsonl"

        entries = _run_corrupted_part_cycle(
            audit_log=audit_log,
            query_log_fn=lambda: _log_text("202609_4_8_jkl"),
            find_part_fn=lambda p: ("db", "t"),
            isolate_fn=lambda p, db, t: False,
            notify_fn=None,
            processed_parts=set(),
        )

        records = [json.loads(line) for line in audit_log.read_text(encoding="utf-8").splitlines()]
        assert [r["action"] for r in records] == ["detect", "detach"]
        assert records[1]["success"] is False
        assert len(entries) == 2


class TestDetectFromLog:
    """纯函数探测逻辑（自闭包上移，行为不变）。"""

    def test_extracts_parts_in_order(self):
        text = _log_text("202609_1_5_abc") + "\n" + _log_text("202610_2_6_def")
        assert _detect_corrupted_parts_from_log(text) == [
            "202609_1_5_abc",
            "202610_2_6_def",
        ]

    def test_dedup_same_part(self):
        text = _log_text("202609_1_5_abc") + "\n" + _log_text("202609_1_5_abc")
        assert _detect_corrupted_parts_from_log(text) == ["202609_1_5_abc"]

    def test_requires_checksum_marker(self):
        assert _detect_corrupted_parts_from_log("part 202609_1_5_abc fine") == []

    def test_empty_or_unmatched_log(self):
        assert _detect_corrupted_parts_from_log("") == []
        assert _detect_corrupted_parts_from_log("no match at all") == []
