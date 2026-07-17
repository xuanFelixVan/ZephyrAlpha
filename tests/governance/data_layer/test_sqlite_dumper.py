# [A_test] module_id: SRC-TST-1673 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_sqlite_dumper
# [INVARIANTS] SqliteDumper dump/restore/verify roundtrip;Merkle root integrity;HMAC integrity
# [MODIFY-GUARD] src/zephyr/rollback/sqlite_dumper.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FileNotFoundError;ValueError
# [TESTS] tests/test_sqlite_dumper.py
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.infrastructure.rollback.sqlite_dumper import (
    HMAC_KEY_DEFAULT,
    JSONL_HEADER_PREFIX,
    DumpResult,
    RestoreResult,
    SqliteDumper,
    VerifyResult,
)


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT NOT NULL, status TEXT DEFAULT 'pending')")
    conn.execute("INSERT INTO tasks (id, name, status) VALUES (1, 'alpha', 'done')")
    conn.execute("INSERT INTO tasks (id, name, status) VALUES (2, 'beta', 'pending')")
    conn.execute("CREATE TABLE gates (id INTEGER PRIMARY KEY, gate_name TEXT, passed INTEGER DEFAULT 0)")
    conn.execute("INSERT INTO gates (id, gate_name, passed) VALUES (1, 'G1', 1)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def dumper(tmp_db: Path, output_dir: Path) -> SqliteDumper:
    return SqliteDumper(db_path=tmp_db, output_dir=output_dir, hmac_key=b"test-key-1234")


class TestSqliteDumperInstantiation:
    def test_default_construction(self, tmp_db: Path, output_dir: Path) -> None:
        d = SqliteDumper(db_path=tmp_db, output_dir=output_dir)
        assert d._db_path == tmp_db
        assert d._output_dir == output_dir
        assert d._hmac_key == HMAC_KEY_DEFAULT

    def test_custom_hmac_key(self, tmp_db: Path, output_dir: Path) -> None:
        custom_key = b"my-custom-key"
        d = SqliteDumper(db_path=tmp_db, output_dir=output_dir, hmac_key=custom_key)
        assert d._hmac_key == custom_key

    def test_none_db_path_uses_default(self) -> None:
        with patch.dict("sys.modules", {}):
            mock_db_path = Path("/fake/db.db")
            with patch("zephyr.infrastructure.rollback.sqlite_dumper.SqliteDumper.__init__", return_value=None) as m:
                SqliteDumper.__init__(dumper)
            m.assert_called_once()

    def test_none_output_dir_uses_default(self, tmp_db: Path) -> None:
        from zephyr.shared.io.paths import REPO_ROOT
        d = SqliteDumper(db_path=tmp_db, output_dir=None)
        # 治本（裁定#6 路径SSoT）：项目硬约束禁止相对路径，默认 output_dir 为 REPO_ROOT 绝对路径
        assert d._output_dir == REPO_ROOT / "data" / "rollback" / "db_snapshots"


class TestSqliteDumperDump:
    def test_dump_creates_jsonl(self, dumper: SqliteDumper, output_dir: Path) -> None:
        result = dumper.dump(commit_sha="abc1234")
        assert isinstance(result, DumpResult)
        assert result.commit_sha == "abc1234"
        assert result.output_path.exists()
        assert result.output_path.name == "abc1234.jsonl"
        assert result.table_count == 2
        assert result.total_rows == 3
        assert result.merkle_root != ""
        assert result.file_size_bytes > 0
        assert result.hmac_signature != ""

    def test_dump_jsonl_header(self, dumper: SqliteDumper, output_dir: Path) -> None:
        dumper.dump(commit_sha="hdrtest")
        output_path = output_dir / "hdrtest.jsonl"
        lines = output_path.read_text(encoding="utf-8").splitlines()
        assert lines[0].startswith(JSONL_HEADER_PREFIX)
        assert "commit: hdrtest" in lines[0]

    def test_dump_jsonl_contains_schema_and_data(self, dumper: SqliteDumper, output_dir: Path) -> None:
        dumper.dump(commit_sha="schematest")
        output_path = output_dir / "schematest.jsonl"
        lines = output_path.read_text(encoding="utf-8").splitlines()
        parsed = [json.loads(l) for l in lines if l.strip() and not l.startswith("#")]
        table_lines = [obj for obj in parsed if "table" in obj and "schema" in obj and "data" in obj]
        assert len(table_lines) == 2
        for tl in table_lines:
            assert "table" in tl
            assert "schema" in tl
            assert "data" in tl

    def test_dump_merkle_root_line(self, dumper: SqliteDumper, output_dir: Path) -> None:
        dumper.dump(commit_sha="merklechk")
        output_path = output_dir / "merklechk.jsonl"
        lines = output_path.read_text(encoding="utf-8").splitlines()
        merkle_lines = [json.loads(l) for l in lines if l.strip() and not l.startswith("#") and "merkle_root" in l]
        assert len(merkle_lines) == 1
        assert len(merkle_lines[0]["merkle_root"]) == 64

    def test_dump_empty_commit_sha_resolves(self, dumper: SqliteDumper, output_dir: Path) -> None:
        result = dumper.dump(commit_sha="")
        assert result.commit_sha != ""
        assert result.output_path.exists()


class TestSqliteDumperRestore:
    def test_restore_from_dump(self, dumper: SqliteDumper, tmp_db: Path, output_dir: Path, tmp_path: Path) -> None:
        dumper.dump(commit_sha="restore1")
        dump_path = output_dir / "restore1.jsonl"
        target_db = tmp_path / "restored.db"
        conn = sqlite3.connect(str(target_db))
        conn.execute("CREATE TABLE tasks (id INTEGER PRIMARY KEY, name TEXT NOT NULL, status TEXT DEFAULT 'pending')")
        conn.execute("CREATE TABLE gates (id INTEGER PRIMARY KEY, gate_name TEXT, passed INTEGER DEFAULT 0)")
        conn.commit()
        conn.close()

        result = dumper.restore(dump_path, target_db_path=target_db)
        assert isinstance(result, RestoreResult)
        assert result.tables_restored == 2
        assert result.rows_restored == 3
        assert result.source_path == dump_path

        conn = sqlite3.connect(str(target_db))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        assert len(rows) == 2
        assert rows[0]["name"] == "alpha"
        assert rows[1]["name"] == "beta"
        conn.close()

    def test_restore_file_not_found(self, dumper: SqliteDumper) -> None:
        with pytest.raises(FileNotFoundError, match="Dump file not found"):
            dumper.restore(Path("/nonexistent/path.jsonl"))

    def test_restore_invalid_dump_file(self, dumper: SqliteDumper, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.jsonl"
        bad_file.write_text("# header\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid dump file"):
            dumper.restore(bad_file)


class TestSqliteDumperVerify:
    def test_verify_valid_dump(self, dumper: SqliteDumper, output_dir: Path) -> None:
        dumper.dump(commit_sha="verify1")
        dump_path = output_dir / "verify1.jsonl"
        result = dumper.verify(dump_path)
        assert isinstance(result, VerifyResult)
        assert result.merkle_match is True
        assert result.hmac_match is True
        assert result.passed is True

    def test_verify_nonexistent_file(self, dumper: SqliteDumper) -> None:
        result = dumper.verify(Path("/nonexistent/file.jsonl"))
        assert result.passed is False
        assert result.merkle_match is False
        assert "File not found" in result.details

    def test_verify_tampered_merkle(self, dumper: SqliteDumper, output_dir: Path) -> None:
        dumper.dump(commit_sha="tamper1")
        dump_path = output_dir / "tamper1.jsonl"
        lines = dump_path.read_text(encoding="utf-8").splitlines()
        tampered = []
        for line in lines:
            if "merkle_root" in line and not line.startswith("#"):
                obj = json.loads(line)
                obj["merkle_root"] = "0" * 64
                tampered.append(json.dumps(obj))
            else:
                tampered.append(line)
        dump_path.write_text("\n".join(tampered) + "\n", encoding="utf-8")
        result = dumper.verify(dump_path)
        assert result.merkle_match is False
        assert result.passed is False

    def test_verify_no_merkle_root(self, dumper: SqliteDumper, tmp_path: Path) -> None:
        no_merkle = tmp_path / "no_merkle.jsonl"
        no_merkle.write_text(
            '# header\n{"schema_version":"1","table_count":0,"tables":[]}\n',
            encoding="utf-8",
        )
        result = dumper.verify(no_merkle)
        assert result.merkle_match is False
        assert "No merkle_root found in dump" in result.details

    def test_verify_invalid_json(self, dumper: SqliteDumper, tmp_path: Path) -> None:
        bad_json = tmp_path / "bad.jsonl"
        bad_json.write_text("# header\n{invalid json}\n", encoding="utf-8")
        result = dumper.verify(bad_json)
        assert result.passed is False
        assert any("JSON parse error" in d for d in result.details)


class TestSqliteDumperVerifyHmacExternal:
    def test_verify_hmac_external_correct(self, dumper: SqliteDumper, output_dir: Path) -> None:
        result = dumper.dump(commit_sha="hmac1")
        assert dumper.verify_hmac_external(result.output_path, result.hmac_signature) is True

    def test_verify_hmac_external_wrong_sig(self, dumper: SqliteDumper, output_dir: Path) -> None:
        dumper.dump(commit_sha="hmac2")
        dump_path = output_dir / "hmac2.jsonl"
        assert dumper.verify_hmac_external(dump_path, "wrong_signature") is False


class TestSqliteDumperHealthCheck:
    def test_check_sqlite_health_valid(self, dumper: SqliteDumper) -> None:
        assert dumper.check_sqlite_health() is True

    def test_check_sqlite_health_invalid_path(self, tmp_path: Path, output_dir: Path) -> None:
        d = SqliteDumper(db_path=tmp_path / "nonexistent.db", output_dir=output_dir)
        assert d.check_sqlite_health() is False

    def test_wal_checkpoint(self, dumper: SqliteDumper) -> None:
        assert dumper.wal_checkpoint() is True


class TestSqliteDumperMerkleRoot:
    def test_empty_table_hashes(self, dumper: SqliteDumper) -> None:
        result = dumper._compute_merkle_root([])
        assert result == hashlib.sha256(b"").hexdigest()

    def test_single_table_hash(self, dumper: SqliteDumper) -> None:
        h = hashlib.sha256(b"test").digest()
        result = dumper._compute_merkle_root([h])
        assert result == h.hex()

    def test_two_table_hashes(self, dumper: SqliteDumper) -> None:
        h1 = hashlib.sha256(b"table1").digest()
        h2 = hashlib.sha256(b"table2").digest()
        expected = hashlib.sha256(h1 + h2).hexdigest()
        result = dumper._compute_merkle_root([h1, h2])
        assert result == expected
