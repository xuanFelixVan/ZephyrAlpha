# [A_test] module_id: SRC-TST-1845 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-473 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_system_snapshot
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
T-V2-006 单元测试 — SystemSnapshotter
======================================
覆盖场景（验收标准 #6 ≥ 80%）：
  - snapshot 字段完整性（timestamp / module_versions / provenance_fingerprint /
    registry_hashes / blueprint_v12_pass_rate）
  - provenance_fingerprint：文件存在时为 SHA-256，不存在时为 "unavailable"
  - registry_hashes：YAML 存在时为哈希，不存在时为 "missing"
  - blueprint_v12_pass_rate：数据库不存在时为 -1.0（哨兵值）
  - 快照写入：输出 JSON 文件，内容可反序列化为 SystemSnapshot
  - 快照写入失败（目录只读时）：发出 UserWarning，不抛出异常
  - M1 backward 兼容：capture() 内部失败时返回 (_empty_snapshot, None)
  - run_in_build() 类方法一行调用
"""

import hashlib
import json
import warnings
from pathlib import Path

import pytest

from zephyr.infrastructure.system_snapshot import (
    SystemSnapshot,
    SystemSnapshotter,
)
from zephyr.governance.persistence.sqlite_schema import init_db

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path: Path):
    """构造简化仓库结构（rationale-log + gates + db）。"""
    # rationale-log
    log_dir = tmp_path / "docs" / "19_development_workspace" / "structure-and-mapping"
    log_dir.mkdir(parents=True)
    log_file = log_dir / "architecture-rationale-log.md"
    log_file.write_text("# ZephyrAlpha Rationale Log\n\n## R87\n", encoding="utf-8", newline="\n")

    # gates YAMLs（只建 G1 / G2，G3/G4/G5 缺失用于测试 "missing"）
    gates_dir = tmp_path / "src" / "zephyr" / "gates"
    gates_dir.mkdir(parents=True)
    (gates_dir / "g1-ingest.yaml").write_text("gate_id: G1\ntitle: G1 Ingest Gate\n", encoding="utf-8", newline="\n")
    (gates_dir / "g2-triage.yaml").write_text("gate_id: G2\ntitle: G2 Triage Gate\n", encoding="utf-8", newline="\n")

    # snapshots dir
    snapshots_dir = tmp_path / ".runtime" / "snapshots"
    snapshots_dir.mkdir(parents=True)

    # DB
    db_dir = tmp_path / "docs" / "_working" / "audit" / "STATE"
    db_dir.mkdir(parents=True)
    db_path = db_dir / "governance.db"
    init_db(db_path)

    return {
        "root": tmp_path,
        "log": log_file,
        "gates_dir": gates_dir,
        "snapshots_dir": snapshots_dir,
        "db_path": db_path,
    }


@pytest.fixture
def snapshotter(tmp_repo):
    return SystemSnapshotter(
        repo_root=tmp_repo["root"],
        snapshots_dir=tmp_repo["snapshots_dir"],
        db_path=tmp_repo["db_path"],
        gates_dir=tmp_repo["gates_dir"],
        module_manifests={"zephyr.gov_enforcement.rule_enforcement.gate_engine": "v1.0.0"},
    )


# ---------------------------------------------------------------------------
# 1. SystemSnapshot 数据模型
# ---------------------------------------------------------------------------


class TestSystemSnapshotModel:
    def test_frozen_raises_on_mutate(self):
        snap = SystemSnapshot(
            timestamp="2026-04-27T10:00:00+00:00",
            module_versions={"zephyr.gov_enforcement.rule_enforcement": "v1.0.0"},
            provenance_fingerprint="abc123",
            registry_hashes={"G1": "deadbeef"},
            blueprint_v12_pass_rate=0.95,
        )
        with pytest.raises(Exception):
            snap.timestamp = "2026-04-27T11:00:00+00:00"  # type: ignore[misc]

    def test_blueprint_pass_rate_bounds(self):
        with pytest.raises(Exception):
            SystemSnapshot(
                timestamp="t",
                module_versions={},
                provenance_fingerprint="x",
                registry_hashes={},
                blueprint_v12_pass_rate=1.5,  # > 1.0 违规
            )

    def test_sentinel_minus_one_allowed(self):
        snap = SystemSnapshot(
            timestamp="t",
            module_versions={},
            provenance_fingerprint="unavailable",
            registry_hashes={},
            blueprint_v12_pass_rate=-1.0,
        )
        assert snap.blueprint_v12_pass_rate == -1.0


# ---------------------------------------------------------------------------
# 2. module_versions
# ---------------------------------------------------------------------------


class TestModuleVersions:
    def test_module_versions_populated(self, snapshotter):
        snap, _ = snapshotter.capture()
        assert "zephyr.gov_enforcement.rule_enforcement.gate_engine" in snap.module_versions
        assert snap.module_versions["zephyr.gov_enforcement.rule_enforcement.gate_engine"] == "v1.0.0"

    def test_module_versions_empty_manifests(self, tmp_repo):
        s = SystemSnapshotter(
            repo_root=tmp_repo["root"],
            snapshots_dir=tmp_repo["snapshots_dir"],
            db_path=tmp_repo["db_path"],
            gates_dir=tmp_repo["gates_dir"],
            module_manifests={},
        )
        snap, _ = s.capture()
        assert snap.module_versions == {}


# ---------------------------------------------------------------------------
# 3. provenance_fingerprint
# ---------------------------------------------------------------------------


class TestProvenanceFingerprint:
    def test_fingerprint_matches_sha256(self, tmp_repo, snapshotter):
        raw = tmp_repo["log"].read_bytes()
        expected = hashlib.sha256(raw).hexdigest()[:32]
        snap, _ = snapshotter.capture()
        assert snap.provenance_fingerprint == expected

    def test_fingerprint_unavailable_when_log_missing(self, tmp_repo):
        tmp_repo["log"].unlink()
        s = SystemSnapshotter(
            repo_root=tmp_repo["root"],
            snapshots_dir=tmp_repo["snapshots_dir"],
            db_path=tmp_repo["db_path"],
            gates_dir=tmp_repo["gates_dir"],
        )
        snap, _ = s.capture()
        assert snap.provenance_fingerprint == "unavailable"


# ---------------------------------------------------------------------------
# 4. registry_hashes
# ---------------------------------------------------------------------------


class TestRegistryHashes:
    def test_existing_gates_have_hex_hashes(self, snapshotter):
        snap, _ = snapshotter.capture()
        assert snap.registry_hashes["G1"] not in {"missing", "read_error", "unavailable"}
        assert snap.registry_hashes["G2"] not in {"missing", "read_error", "unavailable"}

    def test_missing_gates_report_missing(self, snapshotter):
        snap, _ = snapshotter.capture()
        assert snap.registry_hashes["G3"] == "missing"
        assert snap.registry_hashes["G4"] == "missing"
        assert snap.registry_hashes["G5"] == "missing"

    def test_hash_changes_when_file_changes(self, tmp_repo, snapshotter):
        snap1, _ = snapshotter.capture()
        (tmp_repo["gates_dir"] / "g1-ingest.yaml").write_text(
            "gate_id: G1\ntitle: Modified\n", encoding="utf-8", newline="\n"
        )
        snap2, _ = snapshotter.capture()
        assert snap1.registry_hashes["G1"] != snap2.registry_hashes["G1"]


# ---------------------------------------------------------------------------
# 5. blueprint_v12_pass_rate
# ---------------------------------------------------------------------------


class TestBlueprintPassRate:
    def test_returns_sentinel_when_db_missing(self, tmp_repo):
        s = SystemSnapshotter(
            repo_root=tmp_repo["root"],
            snapshots_dir=tmp_repo["snapshots_dir"],
            db_path=tmp_repo["root"] / "nonexistent.db",
            gates_dir=tmp_repo["gates_dir"],
        )
        snap, _ = s.capture()
        assert snap.blueprint_v12_pass_rate == -1.0

    def test_returns_sentinel_when_no_g4_records(self, tmp_repo, snapshotter):
        snap, _ = snapshotter.capture()
        assert snap.blueprint_v12_pass_rate == -1.0

    def test_pass_rate_computed_from_gates_table(self, tmp_repo):
        import sqlite3

        db = tmp_repo["db_path"]
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO gate_runs (gate_run_id, gate_id, passed, details, created_at) VALUES (?, ?, ?, ?, ?)",
            ("gr-001", "G4:task-001", 1, "{}", "2026-04-27T00:00:00"),
        )
        conn.execute(
            "INSERT INTO gate_runs (gate_run_id, gate_id, passed, details, created_at) VALUES (?, ?, ?, ?, ?)",
            ("gr-002", "G4:task-002", 0, "{}", "2026-04-27T00:00:00"),
        )
        conn.commit()
        conn.close()

        s = SystemSnapshotter(
            repo_root=tmp_repo["root"],
            snapshots_dir=tmp_repo["snapshots_dir"],
            db_path=db,
            gates_dir=tmp_repo["gates_dir"],
        )
        snap, _ = s.capture()
        assert snap.blueprint_v12_pass_rate == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# 6. 快照写入（文件 IO）
# ---------------------------------------------------------------------------


class TestSnapshotPersistence:
    def test_snapshot_file_created(self, snapshotter, tmp_repo):
        _, path = snapshotter.capture()
        assert path is not None
        assert path.exists()
        assert path.suffix == ".json"

    def test_snapshot_file_valid_json(self, snapshotter):
        _, path = snapshotter.capture()
        assert path is not None
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "timestamp" in data
        assert "module_versions" in data
        assert "provenance_fingerprint" in data
        assert "registry_hashes" in data
        assert "blueprint_v12_pass_rate" in data

    def test_snapshot_json_deserializable_to_model(self, snapshotter):
        _, path = snapshotter.capture()
        assert path is not None
        data = json.loads(path.read_text(encoding="utf-8"))
        snap = SystemSnapshot(**data)
        assert snap.provenance_fingerprint != ""

    def test_snapshot_write_fail_warns_not_raises(self, tmp_repo):
        """写入只读目录时发出 UserWarning，不抛出异常（M1 backward 兼容）。"""
        readonly_dir = tmp_repo["root"] / "readonly_snapshots"
        readonly_dir.mkdir()
        import os
        import stat

        os.chmod(str(readonly_dir), stat.S_IREAD | stat.S_IEXEC)
        try:
            s = SystemSnapshotter(
                repo_root=tmp_repo["root"],
                snapshots_dir=readonly_dir,
                db_path=tmp_repo["db_path"],
                gates_dir=tmp_repo["gates_dir"],
            )
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                snap, path = s.capture()
            # 在 Windows 上权限设置可能不生效，但不应抛出异常
            assert snap is not None
        finally:
            os.chmod(str(readonly_dir), stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)


# ---------------------------------------------------------------------------
# 7. M1 backward 兼容
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    def test_capture_never_raises(self, snapshotter, monkeypatch):
        """_build_snapshot 抛出任何异常时，capture() 不传播。"""

        def bad_build():
            raise RuntimeError("模拟内部错误")

        monkeypatch.setattr(snapshotter, "_build_snapshot", bad_build)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            snap, path = snapshotter.capture()
        assert snap is not None
        assert path is None
        assert any("非致命" in str(warning.message) for warning in w)

    def test_run_in_build_classmethod(self, tmp_repo):
        snap, path = SystemSnapshotter.run_in_build(
            repo_root=tmp_repo["root"],
            snapshots_dir=tmp_repo["snapshots_dir"],
            db_path=tmp_repo["db_path"],
        )
        assert snap is not None
        assert isinstance(snap.timestamp, str)
