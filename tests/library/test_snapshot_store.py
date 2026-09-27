# [A_test] module_id: MOD-LIB-006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-006 | docs/03_modules/_domain_library/blueprint.md | §6
# [MODULE] tests.library.test_snapshot_store
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_snapshot_store.py — 图书馆本地快照层（R2 批）红蓝夹具。

四条红队判据（战役任务书 + S7 §⑤ R-2/R-5 设计落码）：
- 红①：快照截断/位翻转/manifest 指向不存在 → 读侧必须**报红并回落 PG**，禁静默返回空；
- 红②：崩溃安全序中途失败（os.replace 前抛异常）→ 上上代不得被删、不得留下半个"当前"；
- 红③：无版本列的旧快照被新读 → 必须**拒读**而非覆盖语义；
- 红④：模块内禁 cron/Timer/sleep-loop 的字面扫描断言（根宪法 §9 第 3 条）。

测试隔离：全部写 tmp_path（宪法 §9 第 6 条），PG 经 fake conn/cursor 注入，
时钟经固定 datetime 注入（S7 §④2 禁测试裸时间），零真实 PG 依赖。
"""

from __future__ import annotations

import importlib
import io
import json
import os
import re
import sys
import tokenize
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psycopg2
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pyarrow as pa  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402

import zephyr.library.snapshot_store as g  # noqa: E402

# --------------------------------------------------------------------------- 夹具


def _clock() -> datetime:
    return datetime(2026, 9, 28, 12, 0, 0, tzinfo=UTC)


_SCHEDULED_TASK_RE = re.compile(r"ZephyrAlpha_[A-Za-z]+")


def _code_surface(source: str) -> str:
    """只留可执行面（去注释/去字符串字面量）——文档措辞禁误报，判据打在代码上。"""
    kept: list[str] = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in (tokenize.COMMENT, tokenize.STRING):
            continue
        kept.append(token.string)
    return " ".join(kept)


EXPORT_COLUMNS = ("asset_id", "kind", "home", "status", "title", "built_at", "ext")
LOOKUP_COLUMNS = ("asset_id", "kind", "home", "status", "title", "built_at", "disposition_authority", "successor_of")


def _asset_rows() -> list[tuple[Any, ...]]:
    return [
        ("FILE:src/a.py", "file", "src/a.py", "active", "A 模块", "2026-09-20T00:00:00+08:00", {"k": 1}),
        ("MOD:Kline", "module", "src/kline.py", "active", "K线工厂", "2026-09-21T00:00:00+08:00", None),
        ("FILE:src/z.py", "file", "src/z.py", "stale", "Z 文件", "2026-09-22T00:00:00+08:00", {"k": 2}),
    ]


def _lookup_rows() -> list[tuple[Any, ...]]:
    return [(r[0], r[1], r[2], r[3], r[4], r[5], None, None) for r in _asset_rows()]


class _FakeCursor:
    """记录 SQL 与参数的最小游标（列集动态，与真游标同形）。"""

    def __init__(self, owner: _FakeConn) -> None:
        self._owner = owner
        self._rows: list[tuple[Any, ...]] = []
        self.description: tuple[tuple[str, ...], ...] = ()

    def execute(self, sql: str, params: object = None) -> None:
        self._owner.calls.append((sql, params))
        if "FROM lib_events" in sql:  # R1 世代指纹现读（SELECT max(event_id)）
            self.description = (("max",),)
            self._rows = []
        elif "ILIKE" in sql:
            self.description = tuple((name,) for name in LOOKUP_COLUMNS)
            self._rows = list(self._owner.lookup_rows)
        else:
            self.description = tuple((name,) for name in self._owner.export_columns)
            self._rows = list(self._owner.export_rows)

    def fetchone(self) -> tuple[Any, ...] | None:
        return (self._owner.fingerprint,)

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._rows

    def close(self) -> None:
        return None

    def __enter__(self) -> _FakeCursor:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class _FakeConn:
    def __init__(
        self,
        export_rows: list[tuple[Any, ...]] | None = None,
        *,
        export_columns: tuple[str, ...] = EXPORT_COLUMNS,
        lookup_rows: list[tuple[Any, ...]] | None = None,
    ) -> None:
        self.export_rows = _asset_rows() if export_rows is None else export_rows
        self.export_columns = export_columns
        self.lookup_rows = _lookup_rows() if lookup_rows is None else lookup_rows
        self.fingerprint = 0
        self.calls: list[tuple[str, object]] = []

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self)

    def commit(self) -> None:
        return None

    def close(self) -> None:
        return None


def _store(root: Path, *, stamp: int = 100, conn: _FakeConn | None = None) -> g.LedgerSnapshotStore:
    return g.LedgerSnapshotStore(
        root,
        conn_factory=lambda: conn or _FakeConn(),
        version_provider=lambda _conn: stamp,
        clock=_clock,
    )


@pytest.fixture()
def store(tmp_path: Path) -> g.LedgerSnapshotStore:
    subject = _store(tmp_path / "snaps")
    subject.refresh()
    return subject


def _manifest_payload(root: Path) -> dict[str, Any]:
    return json.loads((root / g.MANIFEST_NAME).read_text(encoding="utf-8"))


class _BoomPublish:
    """在指定文件改名前抛异常=崩溃窗口夹具（提交点①/②的分型注入）。"""

    def __init__(self, target_name: str) -> None:
        self.target_name = target_name
        self.original = g._atomic_publish

    def __call__(self, tmp_path: Path, final_path: Path) -> None:
        if final_path.name == self.target_name:
            raise OSError(f"simulated crash before os.replace -> {final_path.name}")
        self.original(tmp_path, final_path)

    def __enter__(self) -> _BoomPublish:
        g._atomic_publish = self  # type: ignore[assignment]
        return self

    def __exit__(self, *exc: object) -> None:
        g._atomic_publish = self.original  # type: ignore[assignment]


# --------------------------------------------------------------------------- 蓝侧：写侧规格


class TestWriteSideContract:
    def test_first_refresh_writes_versioned_pair(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        result = _store(root, stamp=100).refresh()
        assert result["status"] == "written"
        assert result["row_count"] == 3
        assert (root / "lib_snapshot.v100.parquet").exists()
        assert _manifest_payload(root)["ledger_version"] == 100

    def test_export_is_whole_table_plus_version_column(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        _store(root).refresh()
        columns = _manifest_payload(root)["columns"]
        assert columns == [*EXPORT_COLUMNS, g.VERSION_COLUMN]  # 列集动态取，非硬编码子集
        row = _store(root).load_rows()[0]
        assert row[g.VERSION_COLUMN] == 100
        assert row["ext"] == '{"k": 1}'  # jsonb 单元转文本，零结构歧义

    def test_same_version_second_refresh_is_zero_io_skip(self, store: g.LedgerSnapshotStore) -> None:
        before = _manifest_payload(store.root)["built_at_utc"]
        result = store.refresh()
        assert result["status"] == "skipped_up_to_date"
        assert _manifest_payload(store.root)["built_at_utc"] == before
        assert [v for v, _ in store.snapshot_files()] == [100]

    def test_sql_export_uses_module_constant_and_no_fingerprint_sql(self, tmp_path: Path) -> None:
        conn = _FakeConn()
        _store(tmp_path / "snaps", conn=conn).refresh()
        executed = [sql for sql, _ in conn.calls]
        assert g._SQL_EXPORT_ASSETS in executed
        assert not any("lib_events" in sql for sql in executed)  # 禁本件复制指纹 SQL

    def test_empty_export_is_refused(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        store = _store(root, conn=_FakeConn(export_rows=[]))
        with pytest.raises(g.SnapshotStoreError, match="拒落空快照"):
            store.refresh()
        assert not store.manifest_path.exists()

    def test_third_generation_deletes_oldest_only_after_commit(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        for stamp in (100, 101, 102):
            _store(root, stamp=stamp).refresh()
        assert [v for v, _ in _store(root).snapshot_files()] == [101, 102]
        assert not (root / "lib_snapshot.v100.parquet").exists()
        assert _manifest_payload(root)["ledger_version"] == 102


# --------------------------------------------------------------------------- 红②：崩溃安全序


class TestCrashSafetyOrder:
    def test_crash_before_data_rename_keeps_old_pair_intact(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        for stamp in (100, 101):
            _store(root, stamp=stamp).refresh()
        with _BoomPublish("lib_snapshot.v102.parquet"), pytest.raises(OSError, match="simulated crash"):
            _store(root, stamp=102).refresh()
        assert [v for v, _ in _store(root).snapshot_files()] == [100, 101]  # 上上代未被删
        assert _manifest_payload(root)["ledger_version"] == 101  # manifest 未换=读者恒见旧 pair
        assert not (root / "lib_snapshot.v102.parquet").exists()  # 不留半个"当前"

    def test_crash_before_manifest_rename_leaves_old_generation_serving(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        for stamp in (100, 101):
            _store(root, stamp=stamp).refresh()
        with _BoomPublish(g.MANIFEST_NAME), pytest.raises(OSError, match="simulated crash"):
            _store(root, stamp=102).refresh()
        survivor = _store(root)
        assert [v for v, _ in survivor.snapshot_files()] == [100, 101, 102]  # 提交点②未过 → 一份不删
        assert survivor.read_manifest().ledger_version == 101
        assert survivor.verify()[1] is None
        assert survivor.query("K线", limit=5)[0][g.VERSION_COLUMN] == 101

    def test_tmp_residue_never_referenced_by_reader(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        _store(root).refresh()
        (root / "lib_snapshot.v999.parquet.tmp").write_bytes(b"half written corpse")
        survivor = _store(root)
        assert survivor.verify()[1] is None
        assert [v for v, _ in survivor.snapshot_files()] == [100]

    def test_writer_lock_blocks_second_writer_then_self_heals(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        root.mkdir(parents=True, exist_ok=True)
        lock = root / g.WRITER_LOCK_NAME
        lock.write_text("alive", encoding="utf-8")
        now = _clock().timestamp()
        os.utime(lock, (now - 5, now - 5))  # TTL 窗内的在握手（时基=注入时钟，零墙钟依赖）
        with pytest.raises(g.SnapshotWriterBusyError):
            _store(root).refresh()
        assert lock.read_text(encoding="utf-8") == "alive"  # 忙时不得篡改他人在握锁
        os.utime(lock, (now - g.WRITER_LOCK_TTL_SECONDS - 5, now - g.WRITER_LOCK_TTL_SECONDS - 5))
        assert _store(root).refresh()["status"] == "written"  # 残渣锁超 TTL → 自愈接管
        assert not lock.exists()  # 用毕释放


# --------------------------------------------------------------------------- 红①：损坏必报红+回落


class TestCorruptSnapshotRed:
    def test_truncated_snapshot_falls_back_to_pg_and_reports_error(self, store: g.LedgerSnapshotStore) -> None:
        path = store.root / "lib_snapshot.v100.parquet"
        payload = path.read_bytes()[:-1]
        path.write_bytes(payload)
        result = g.query_ledger_with_fallback("kline", 5, store=store, conn_factory=lambda: _FakeConn())
        assert result.source == "pg"
        assert result.degraded is True and result.authoritative is True
        assert "SnapshotCorruptError" in (result.snapshot_load_error or "")
        assert result.rows  # 回落 PG 真源，绝不空返

    def test_bit_flip_in_middle_is_detected(self, store: g.LedgerSnapshotStore) -> None:
        path = store.root / "lib_snapshot.v100.parquet"
        data = bytearray(path.read_bytes())
        data[len(data) // 2] ^= 0xFF
        path.write_bytes(bytes(data))
        with pytest.raises(g.SnapshotCorruptError, match="校验和失配"):
            store.load_rows()

    def test_manifest_pointing_to_missing_file_is_rejected(self, store: g.LedgerSnapshotStore) -> None:
        manifest = store.read_manifest()
        stale = g.LedgerSnapshotManifest(
            ledger_version=manifest.ledger_version,
            snapshot_file="lib_snapshot.v100.parquet",
            built_at_utc=manifest.built_at_utc,
            row_count=manifest.row_count,
            sha256="0" * 64,
            columns=manifest.columns,
        )
        store.root.joinpath("lib_snapshot.v100.parquet").unlink()
        store._publish_manifest(stale)
        with pytest.raises(g.SnapshotCorruptError, match="不存在"):
            store.load_rows()
        assert store.verify()[1] is not None

    def test_manifest_file_name_generation_mismatch_is_half_commit(self, store: g.LedgerSnapshotStore) -> None:
        manifest = store.read_manifest()
        drifted = g.LedgerSnapshotManifest(
            ledger_version=manifest.ledger_version,
            snapshot_file="lib_snapshot.v999.parquet",
            built_at_utc=manifest.built_at_utc,
            row_count=manifest.row_count,
            sha256=manifest.sha256,
            columns=manifest.columns,
        )
        store._publish_manifest(drifted)
        assert _store(store.root).verify()[1] is not None
        with pytest.raises(g.SnapshotCorruptError, match="半途提交态"):
            _store(store.root).load_rows()

    def test_row_count_drift_is_rejected(self, store: g.LedgerSnapshotStore) -> None:
        payload = _manifest_payload(store.root)
        payload["row_count"] = payload["row_count"] + 1
        (store.root / g.MANIFEST_NAME).write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(g.SnapshotCorruptError, match="行数"):
            store.load_rows()


# --------------------------------------------------------------------------- 红③：版本列铁律


class TestVersionColumnIronclad:
    def _write_legacy_pair(self, root: Path, version: int) -> None:
        """造一份"旧代无版本列"快照：文件与 manifest 自洽（sha/行数全对），只缺版本列。"""
        root.mkdir(parents=True, exist_ok=True)
        rows = [{column: value for column, value in zip(EXPORT_COLUMNS, row, strict=True)} for row in _asset_rows()]
        table = pa.Table.from_pylist(rows)
        name = f"lib_snapshot.v{version}{g.SNAPSHOT_SUFFIX}"
        pq.write_table(table, root / name, compression="gzip")
        digest = g._sha256_file(root / name)
        manifest = g.LedgerSnapshotManifest(
            ledger_version=version,
            snapshot_file=name,
            built_at_utc=_clock().isoformat(),
            row_count=table.num_rows,
            sha256=digest,
            columns=tuple(table.column_names),
        )
        _store(root)._publish_manifest(manifest)

    def test_snapshot_without_version_column_is_refused(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        self._write_legacy_pair(root, 55)
        survivor = _store(root)
        with pytest.raises(g.SnapshotVersionColumnError, match="拒读"):
            survivor.load_rows()
        assert survivor.verify()[1] is not None

    def test_legacy_snapshot_cannot_masquerade_when_pg_down(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        self._write_legacy_pair(root, 55)

        def _down() -> _FakeConn:
            raise psycopg2.OperationalError("PG down")

        with pytest.raises(g.SnapshotFallbackExhaustedError, match="拒绝返回空结果"):
            g.query_ledger_with_fallback("kline", 5, store=_store(root), conn_factory=_down)

    def test_row_generation_disagrees_with_manifest_is_refused(self, tmp_path: Path) -> None:
        root = tmp_path / "snaps"
        _store(root, stamp=100).refresh()
        survivor = _store(root)
        rows = survivor.load_rows()
        for row in rows:
            row[g.VERSION_COLUMN] = 7  # 旧行覆盖修正行的同型事故面
        path = root / "lib_snapshot.v100.parquet"
        pq.write_table(pa.Table.from_pylist(rows), path, compression="gzip")
        payload = _manifest_payload(root)
        payload["sha256"] = g._sha256_file(path)
        (root / g.MANIFEST_NAME).write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(g.SnapshotVersionColumnError, match="行内代际"):
            _store(root).load_rows()


# --------------------------------------------------------------------------- 红⑤/回落语义与 PG 优先


class TestFallbackSemantics:
    def _down_factory(self) -> Any:
        def _down() -> _FakeConn:
            raise psycopg2.OperationalError("PG down")

        return _down

    def test_pg_reachable_wins_over_snapshot(self, store: g.LedgerSnapshotStore) -> None:
        conn = _FakeConn()
        result = g.query_ledger_with_fallback("kline", 5, store=store, conn_factory=lambda: conn)
        assert (result.source, result.authoritative, result.degraded) == ("pg", True, False)
        assert result.rows == [dict(zip(LOOKUP_COLUMNS, row, strict=True)) for row in _lookup_rows()]

    def test_pg_down_serves_snapshot_with_explicit_degraded_marks(self, store: g.LedgerSnapshotStore) -> None:
        result = g.query_ledger_with_fallback("kline", 5, store=store, conn_factory=self._down_factory())
        assert result.source == "snapshot"
        assert result.authoritative is False and result.degraded is True
        assert result.degraded_reason.startswith("pg_unreachable:OperationalError")
        assert result.ledger_version == 100

    def test_pg_down_without_snapshot_raises_instead_of_empty(self, tmp_path: Path) -> None:
        with pytest.raises(g.SnapshotUnavailableError):
            _store(tmp_path / "snaps").query("kline", 5)
        with pytest.raises(g.SnapshotFallbackExhaustedError):
            g.query_ledger_with_fallback(
                "kline", 5, store=_store(tmp_path / "snaps"), conn_factory=self._down_factory()
            )

    def test_snapshot_query_matches_three_axes_and_orders_by_asset_id(self, store: g.LedgerSnapshotStore) -> None:
        assert store.query("z.py", limit=5)[0]["asset_id"] == "FILE:src/z.py"
        assert store.query("K线", limit=5)[0]["asset_id"] == "MOD:Kline"
        assert [row["asset_id"] for row in store.query("FILE", limit=2)] == ["FILE:src/a.py", "FILE:src/z.py"]

    def test_snapshot_path_is_injectable_never_hardcoded_production(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(g.ROOT_ENV_VAR, str(tmp_path / "injected"))
        assert g.default_snapshot_root() == tmp_path / "injected"
        assert g.default_snapshot_root().is_relative_to(tmp_path)


# --------------------------------------------------------------------------- R1 世代指纹单点入口


class TestLedgerStampSeam:
    def test_stamp_seam_wires_to_r1_fingerprint_source(self) -> None:
        """R1 接线断言：本件只 import 世代指纹真源件，禁自带指纹 SQL。"""
        module = importlib.import_module(g._R1_STAMP_MODULE)
        assert callable(getattr(module, g._R1_STAMP_FUNC))
        surface = _code_surface(Path(g.__file__).read_text(encoding="utf-8"))
        assert "lib_events" not in surface and "max(event_id)" not in surface

    def test_missing_r1_module_raises_never_fabricates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(g, "_version_provider_override", None)
        monkeypatch.setattr(g, "_R1_STAMP_MODULE", "zephyr.library.definitely_not_landed_r1")
        with pytest.raises(g.LedgerStampUnavailable, match="真源件不可用"):
            g.read_ledger_version(object())

    def test_provider_injection_is_single_wiring_point(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(g, "_version_provider_override", lambda _conn: 4242)
        assert g.read_ledger_version(object()) == 4242

    def test_refresh_reads_stamp_through_r1_real_entry(self, tmp_path: Path) -> None:
        """活体接线：未注入 provider 时，写侧世代号必须来自 R1 真源件现读。"""
        conn = _FakeConn()
        conn.fingerprint = 777
        root = tmp_path / "snaps"
        store = g.LedgerSnapshotStore(root, conn_factory=lambda: conn, clock=_clock)
        assert store.refresh()["ledger_version"] == 777
        assert any("lib_events" in sql for sql, _ in conn.calls)

    def test_refresh_without_stamp_source_fails_closed_upwards(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """R1 件缺席/更名时写侧拒绝落盘（禁伪造世代号），且不留半个代。"""
        monkeypatch.setattr(g, "_version_provider_override", None)
        monkeypatch.setattr(g, "_R1_STAMP_MODULE", "zephyr.library.definitely_not_landed_r1")
        store = g.LedgerSnapshotStore(tmp_path / "snaps", conn_factory=lambda: _FakeConn(), clock=_clock)
        with pytest.raises(g.LedgerStampUnavailable):
            store.refresh()
        assert not store.manifest_path.exists()


# --------------------------------------------------------------------------- 红④：禁计划任务字面扫描


class TestNoSchedulerPrimitives:
    FORBIDDEN: tuple[str, ...] = (
        "threading.Timer",
        "Timer(",
        "time.sleep",
        "sleep(",
        "schedule",
        "BlockingScheduler",
        "apscheduler",
        "AsyncIOScheduler",
        "CronTrigger",
        "crontab",
        "systemd.timer",
    )

    def test_snapshot_store_executable_code_has_no_cron_or_sleep_loop(self) -> None:
        surface = _code_surface(Path(g.__file__).read_text(encoding="utf-8"))
        hits = [token for token in self.FORBIDDEN if token in surface]
        assert hits == [], f"快照层可执行面出现禁列触发原语：{hits}"

    def test_backup_host_executable_code_adds_no_new_trigger(self) -> None:
        host = (_PROJECT_ROOT / "scripts" / "backup" / "library_ledger_backup.py").read_text(encoding="utf-8")
        surface = _code_surface(host)
        hits = [token for token in self.FORBIDDEN if token in surface]
        assert hits == [], f"挂接宿主可执行面出现禁列触发原语：{hits}"

    def test_headers_declare_zero_new_scheduled_task(self) -> None:
        """文档位正向断言（红队的反面）：两件头部都必须自述"零新增计划任务/尾步挂接"。"""
        module_head = Path(g.__file__).read_text(encoding="utf-8")[:2000]
        host_head = (_PROJECT_ROOT / "scripts" / "backup" / "library_ledger_backup.py").read_text(encoding="utf-8")[
            :2000
        ]
        assert "零 cron/Timer/sleep-loop" in module_head
        assert "零新增计划任务" in module_head and "零新增计划任务" in host_head

    def test_refresh_hook_is_on_existing_backup_chain_and_fail_open(self) -> None:
        host = _PROJECT_ROOT / "scripts" / "backup" / "library_ledger_backup.py"
        source = host.read_text(encoding="utf-8")
        assert "snapshot_store" in source, "刷新未挂既有备份成功事件链（S3 案 A）"
        assert "fail-open" in source, "挂接非 fail-open：快照故障不得改备份退出码"
        tasks = set(_SCHEDULED_TASK_RE.findall(source))
        assert tasks == {
            "ZephyrAlpha_LibraryLedgerBackup",
            "ZephyrAlpha_LibraryLedgerDrill",
        }, f"刷快照不得新增计划任务，实际在册={sorted(tasks)}"

    def test_backup_hook_swallows_snapshot_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import zephyr.library.snapshot_store as snapshot_store  # noqa: PLC0415
        from scripts.backup import library_ledger_backup as host  # noqa: PLC0415

        def _boom(*_a: object, **_k: object) -> dict:
            raise g.LedgerStampUnavailable("R1 未落地")

        monkeypatch.setattr(snapshot_store, "refresh_snapshot", _boom)
        assert host._refresh_snapshot_quietly()["status"] == "failed"  # 不抛=不改备份退出码
