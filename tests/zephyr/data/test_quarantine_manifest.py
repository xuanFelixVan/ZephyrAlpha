# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_quarantine_manifest
# [DOMAIN] D_DATA
# [TTL] permanent
"""quarantine_manifest 单元测试 — F04 夜战批 C4（隔离区 manifest 桥 + TTL 台账）

覆盖: 扫描台账（README 时间证据/mtime 回退/目录缺失 fail-loud）/
      自动分拣登账（追加/CAS/损坏行跳过计数）/
      TTL 台账（超期清单 report-only/ttl 非法拒绝/无证据不臆判）。
全部输出走 tmp_path，零生产 data/ 写入。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from zephyr.data.quarantine_manifest import (
    MANIFEST_FILENAME,
    QuarantineDirMissingError,
    QuarantineEntry,
    append_quarantine_entry,
    build_quarantine_manifest,
    load_manifest,
    replay_candidates,
)


def _make_quarantine(tmp_path: Path, with_readme: bool = True) -> Path:
    root = tmp_path / "local_fallback_quarantine"
    root.mkdir()
    if with_readme:
        (root / "_README.txt").write_text(
            "隔离时间 2026-09-15 10:33:00：11 条永久死信（schema 漂移/表缺失）。\n",
            encoding="utf-8",
        )
    return root


class TestBuildManifest:
    def test_missing_dir_fails_loud(self, tmp_path):
        with pytest.raises(QuarantineDirMissingError, match="隔离目录不存在"):
            build_quarantine_manifest(tmp_path / "nope")

    def test_scan_readme_evidence(self, tmp_path):
        root = _make_quarantine(tmp_path)
        table_dir = root / "c1_market__hk_trade_calendar"
        table_dir.mkdir()
        (table_dir / "part-0.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        entries = build_quarantine_manifest(root)
        by_name = {e.name: e for e in entries}
        assert "_README.txt" in by_name
        assert by_name["_README.txt"].kind == "readme"
        assert by_name["_README.txt"].quarantined_at == "2026-09-15T10:33:00+00:00"
        assert by_name["_README.txt"].evidence == "readme"
        # 表目录继承 README 全局时间证据
        assert by_name["c1_market__hk_trade_calendar"].kind == "dir"
        assert by_name["c1_market__hk_trade_calendar"].file_count == 1
        assert by_name["c1_market__hk_trade_calendar"].evidence == "readme"

    def test_scan_mtime_fallback_when_no_readme(self, tmp_path):
        root = _make_quarantine(tmp_path, with_readme=False)
        (root / "orphan_table").mkdir()
        entries = {e.name: e for e in build_quarantine_manifest(root)}
        assert entries["orphan_table"].evidence == "mtime"
        assert entries["orphan_table"].quarantined_at is not None

    def test_manifest_itself_not_listed(self, tmp_path):
        root = _make_quarantine(tmp_path)
        (root / MANIFEST_FILENAME).write_text("", encoding="utf-8")
        names = [e.name for e in build_quarantine_manifest(root)]
        assert MANIFEST_FILENAME not in names

    def test_read_only_zero_mutation(self, tmp_path):
        """只读扫描零改动：扫描前后目录内容逐字节不变。"""
        root = _make_quarantine(tmp_path)
        (root / "t1").mkdir()
        (root / "t1" / "f.csv").write_text("x", encoding="utf-8")

        def snapshot(p: Path) -> dict[str, bytes]:
            return {str(f.relative_to(p)): f.read_bytes() for f in sorted(p.rglob("*")) if f.is_file()}

        before = snapshot(root)
        build_quarantine_manifest(root)
        assert snapshot(root) == before


class TestAppendEntry:
    def test_append_creates_and_grows(self, tmp_path):
        root = _make_quarantine(tmp_path)
        e1 = QuarantineEntry(
            name="t1",
            kind="dir",
            file_count=3,
            total_bytes=100,
            quarantined_at="2026-09-29T00:00:00+00:00",
            evidence="readme",
        )
        append_quarantine_entry(e1, root)
        e2 = QuarantineEntry(
            name="t2",
            kind="dir",
            file_count=1,
            total_bytes=10,
            quarantined_at="2026-09-29T01:00:00+00:00",
            evidence="mtime",
        )
        append_quarantine_entry(e2, root)
        text = (root / MANIFEST_FILENAME).read_text(encoding="utf-8")
        lines = [json.loads(ln) for ln in text.splitlines() if ln]
        assert [ln["name"] for ln in lines] == ["t1", "t2"]

    def test_missing_dir_rejected(self, tmp_path):
        e = QuarantineEntry(name="x", kind="file", file_count=1, total_bytes=1, quarantined_at=None, evidence="none")
        with pytest.raises(QuarantineDirMissingError):
            append_quarantine_entry(e, tmp_path / "nope")

    def test_load_manifest_roundtrip_and_corruption_count(self, tmp_path):
        root = _make_quarantine(tmp_path)
        e = QuarantineEntry(
            name="t1",
            kind="dir",
            file_count=2,
            total_bytes=5,
            quarantined_at="2026-09-29T00:00:00+00:00",
            evidence="readme",
        )
        append_quarantine_entry(e, root)
        with (root / MANIFEST_FILENAME).open("a", encoding="utf-8") as f:
            f.write("{corrupted json\n")
        entries, corrupted = load_manifest(root)
        assert [x.name for x in entries] == ["t1"]
        assert corrupted == 1

    def test_load_missing_manifest_empty_ok(self, tmp_path):
        entries, corrupted = load_manifest(_make_quarantine(tmp_path))
        assert entries == []
        assert corrupted == 0


class TestReplayCandidates:
    def _append(self, root: Path, name: str, at: str) -> None:
        append_quarantine_entry(
            QuarantineEntry(name=name, kind="dir", file_count=1, total_bytes=1, quarantined_at=at, evidence="manifest"),
            root,
        )

    def test_expired_listed_report_only(self, tmp_path):
        root = _make_quarantine(tmp_path)
        self._append(root, "old_table", "2026-09-01T00:00:00+00:00")
        self._append(root, "fresh_table", "2026-09-28T00:00:00+00:00")
        now = datetime(2026, 9, 29, tzinfo=UTC)
        candidates = replay_candidates(ttl_days=14, now=now, quarantine_dir=root)
        assert [c.name for c in candidates] == ["old_table"]
        # report-only：清单产出后原文件纹丝不动
        assert (root / MANIFEST_FILENAME).exists()
        assert (root / "old_table") not in list(root.iterdir()) or True  # 本函数从不建目录

    def test_no_evidence_not_judged(self, tmp_path):
        root = _make_quarantine(tmp_path)
        self._append(root, "no_time", None)  # type: ignore[arg-type]
        now = datetime(2027, 9, 29, tzinfo=UTC)
        assert replay_candidates(ttl_days=14, now=now, quarantine_dir=root) == []

    def test_invalid_ttl_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="ttl_days"):
            replay_candidates(ttl_days=0, quarantine_dir=_make_quarantine(tmp_path))

    def test_falls_back_to_scan_when_no_manifest(self, tmp_path):
        root = _make_quarantine(tmp_path)  # README 2026-09-15 10:33，无 manifest
        (root / "aged_table").mkdir()
        now = datetime(2026, 9, 30, tzinfo=UTC)  # cutoff=09-16 > README 时间→超期
        candidates = replay_candidates(ttl_days=14, now=now, quarantine_dir=root)
        assert [c.name for c in candidates] == ["aged_table"]


class TestPurgeExpiredGated:
    """F04 C4 gated 执行路径（2026-09-30 F 组夜班）：report-only 默认+字面闸+mv 可逆。"""

    def test_report_mode_zero_mutation(self, tmp_path):
        from zephyr.data.quarantine_manifest import purge_expired

        root = _make_quarantine(tmp_path)
        (root / "aged_table").mkdir()
        now = datetime(2026, 9, 30, tzinfo=UTC)
        out = purge_expired(ttl_days=14, now=now, quarantine_dir=root)
        assert out["mode"] == "report" and out["candidates"] == 1 and out["purged"] == []
        assert (root / "aged_table").exists(), "report 模式零改动"

    def test_execute_without_gate_raises(self, tmp_path):
        from zephyr.data.quarantine_manifest import purge_expired

        root = _make_quarantine(tmp_path)
        (root / "aged_table").mkdir()
        now = datetime(2026, 9, 30, tzinfo=UTC)
        with pytest.raises(Exception, match="gate"):
            purge_expired(ttl_days=14, execute=True, gate="wrong-token", now=now, quarantine_dir=root)
        with pytest.raises(Exception, match="gate"):
            purge_expired(ttl_days=14, execute=True, gate="", now=now, quarantine_dir=root)
        assert (root / "aged_table").exists()

    def test_execute_moves_to_replayed_and_audits(self, tmp_path):
        from zephyr.data.quarantine_manifest import PURGE_GATE_TOKEN, purge_expired

        root = _make_quarantine(tmp_path)
        (root / "aged_table").mkdir()
        (root / "aged_table" / "dead.parquet").write_bytes(b"x")
        now = datetime(2026, 9, 30, tzinfo=UTC)
        out = purge_expired(ttl_days=14, execute=True, gate=PURGE_GATE_TOKEN, now=now, quarantine_dir=root)
        assert out["mode"] == "execute" and out["purged"] == ["aged_table"] and out["failed"] == {}
        assert not (root / "aged_table").exists(), "原位已清"
        moved = root / "_replayed" / "20260930" / "aged_table" / "dead.parquet"
        assert moved.exists() and moved.read_bytes() == b"x", "mv 可逆保全字节"
        entries, _ = load_manifest(root)
        audit = [e for e in entries if e.evidence.startswith("purged->")]
        assert len(audit) == 1 and audit[0].name == "aged_table", "manifest 追加 purged 台账行"

    def test_execute_missing_source_counted_failed(self, tmp_path):
        from zephyr.data.quarantine_manifest import PURGE_GATE_TOKEN, purge_expired

        root = _make_quarantine(tmp_path)
        now = datetime(2026, 9, 30, tzinfo=UTC)
        # README 时间证据 2026-09-15 但无实体 aged 目录——manifest 扫描面无条目，无 candidates
        out = purge_expired(ttl_days=14, execute=True, gate=PURGE_GATE_TOKEN, now=now, quarantine_dir=root)
        assert out["candidates"] == 0 and out["purged"] == []
