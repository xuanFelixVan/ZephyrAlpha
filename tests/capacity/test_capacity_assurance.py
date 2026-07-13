# [A_test] module_id: SRC-TST-0491 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §test
# [MODULE] zephyr.feedback_loop.capacity_assurance
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_capacity_assurance.py
# [TTL] task_bound

import sqlite3

import pytest

schema_mod = pytest.importorskip(
    "zephyr.feedback_loop.capacity_assurance.schema", reason="capacity-assurance.schema not available"
)
SchemaManager = schema_mod.SchemaManager
MetricsWriteBuffer = schema_mod.MetricsWriteBuffer
compute_hash = SchemaManager.compute_hash

sli_mod = pytest.importorskip(
    "zephyr.feedback_loop.capacity_assurance.sli_instrumentation", reason="capacity-assurance.sli_instrumentation not available"
)
SLIInstrumentation = sli_mod.SLIInstrumentation
SLIStats = sli_mod.SLIStats


class TestSchemaManager:
    def test_init_db_creates_tables(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        conn = mgr.init_db()
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()
        required = {
            "ai_provenance",
            "capacity_metrics",
            "error_budget",
            "token_budget_usage",
            "capacity_metrics_hourly",
        }
        assert required.issubset(tables)

    def test_init_db_sets_pragma(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        conn = mgr.init_db()
        journal = conn.execute("PRAGMA journal_mode").fetchone()[0]
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        conn.close()
        assert journal == "wal"
        assert fk == 1

    def test_init_db_schema_version(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        conn = mgr.init_db()
        row = conn.execute("SELECT version FROM _capacity_schema_version").fetchone()
        conn.close()
        assert row is not None
        assert row[0] == SchemaManager.SCHEMA_VERSION

    def test_verify_all_tables_exist(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db()
        result = mgr.verify()
        assert result["all_tables_exist"] is True
        assert result["missing_tables"] == []

    def test_verify_hash_chain_valid_on_empty(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db()
        result = mgr.verify()
        assert result["hash_chain_valid"] is True

    def test_migrate_idempotent(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db()
        mgr.migrate()
        result = mgr.verify()
        assert result["all_tables_exist"] is True

    def test_migrate_creates_missing_tables(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE other_table (id INTEGER)")
        conn.commit()
        conn.close()
        mgr = SchemaManager(db_path=db_path)
        mgr.migrate()
        result = mgr.verify()
        assert result["all_tables_exist"] is True

    def test_ttl_cleanup_removes_old_rows(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        conn = mgr.init_db()
        conn.execute("INSERT INTO capacity_metrics (ts, sli_id, value) VALUES ('2020-01-01T00:00:00', 'sli_1', 1.0)")
        conn.execute("INSERT INTO capacity_metrics (ts, sli_id, value) VALUES (datetime('now'), 'sli_2', 2.0)")
        conn.commit()
        conn.close()
        removed = mgr.ttl_cleanup()
        assert removed >= 1

    def test_ttl_cleanup_no_old_rows(self, tmp_path):
        db_path = str(tmp_path / "test_capacity.db")
        mgr = SchemaManager(db_path=db_path)
        conn = mgr.init_db()
        conn.execute("INSERT INTO capacity_metrics (ts, sli_id, value) VALUES (datetime('now'), 'sli_1', 1.0)")
        conn.commit()
        conn.close()
        removed = mgr.ttl_cleanup()
        assert removed == 0

    def test_compute_hash_deterministic(self):
        h1 = compute_hash("module_a", "field_b", "old", "new", "agent", "2026-01-01T00:00:00", "prev_hash")
        h2 = compute_hash("module_a", "field_b", "old", "new", "agent", "2026-01-01T00:00:00", "prev_hash")
        assert h1 == h2

    def test_compute_hash_differs_for_different_input(self):
        h1 = compute_hash("module_a", "field_b", "old", "new", "agent", "2026-01-01T00:00:00", None)
        h2 = compute_hash("module_x", "field_b", "old", "new", "agent", "2026-01-01T00:00:00", None)
        assert h1 != h2

    def test_compute_hash_with_none_values(self):
        h = compute_hash("module_a", "field_b", None, None, "agent", "2026-01-01T00:00:00", None)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_ttl_days_constant(self):
        assert SchemaManager.TTL_DAYS == 7

    def test_schema_version_constant(self):
        assert SchemaManager.SCHEMA_VERSION == "2.6.0"


class TestMetricsWriteBuffer:
    def test_add_and_flush(self, tmp_path):
        db_path = str(tmp_path / "test_buffer.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db().close()
        buf = MetricsWriteBuffer(db_path=db_path)
        buf.add("2026-01-01T00:00:00", "sli_1", 1.5, governance_layer="L1", runtime_plane="control")
        count = buf.flush()
        assert count == 1
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT * FROM capacity_metrics").fetchall()
        conn.close()
        assert len(rows) == 1

    def test_flush_empty_buffer(self, tmp_path):
        db_path = str(tmp_path / "test_buffer.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db().close()
        buf = MetricsWriteBuffer(db_path=db_path)
        count = buf.flush()
        assert count == 0

    def test_context_manager_flushes(self, tmp_path):
        db_path = str(tmp_path / "test_buffer.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db().close()
        with MetricsWriteBuffer(db_path=db_path) as buf:
            buf.add("2026-01-01T00:00:00", "sli_1", 1.0)
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT * FROM capacity_metrics").fetchall()
        conn.close()
        assert len(rows) == 1

    def test_batch_size_constant(self):
        assert MetricsWriteBuffer.BATCH_SIZE == 100

    def test_add_with_optional_fields(self, tmp_path):
        db_path = str(tmp_path / "test_buffer.db")
        mgr = SchemaManager(db_path=db_path)
        mgr.init_db().close()
        buf = MetricsWriteBuffer(db_path=db_path)
        buf.add("2026-01-01T00:00:00", "sli_1", 1.0, governance_layer="L2", runtime_plane="data", compensated=1)
        buf.flush()
        conn = sqlite3.connect(db_path)
        row = conn.execute("SELECT * FROM capacity_metrics").fetchone()
        conn.close()
        assert row is not None


class TestSLIInstrumentation:
    def test_record_insert_timing(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_test", 10.5)
        stats = inst.get_sli_stats("sli_test")
        assert stats is not None
        assert stats.count == 1
        assert stats.total_duration_ms == 10.5
        assert stats.min_duration_ms == 10.5
        assert stats.max_duration_ms == 10.5

    def test_record_insert_timing_multiple(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_test", 5.0)
        inst.record_insert_timing("sli_test", 15.0)
        inst.record_insert_timing("sli_test", 10.0)
        stats = inst.get_sli_stats("sli_test")
        assert stats.count == 3
        assert stats.total_duration_ms == 30.0
        assert stats.min_duration_ms == 5.0
        assert stats.max_duration_ms == 15.0

    def test_avg_duration_ms(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_test", 10.0)
        inst.record_insert_timing("sli_test", 20.0)
        stats = inst.get_sli_stats("sli_test")
        assert stats.avg_duration_ms == 15.0

    def test_avg_duration_ms_zero_count(self):
        stats = SLIStats(sli_id="empty_sli")
        assert stats.avg_duration_ms == 0.0

    def test_get_sli_stats_nonexistent(self):
        inst = SLIInstrumentation()
        assert inst.get_sli_stats("nonexistent") is None

    def test_record_correction_latency(self):
        inst = SLIInstrumentation()
        inst.record_correction_latency("sli_corr", 7.5)
        stats = inst.get_sli_stats("sli_corr")
        assert stats.correction_count == 1
        assert stats.correction_total_ms == 7.5

    def test_record_validation_timing(self):
        inst = SLIInstrumentation()
        inst.record_validation_timing("sli_val", 3.2)
        stats = inst.get_sli_stats("sli_val")
        assert stats.validation_count == 1
        assert stats.validation_total_ms == 3.2

    def test_reset_specific_sli(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_a", 10.0)
        inst.record_insert_timing("sli_b", 20.0)
        inst.reset("sli_a")
        assert inst.get_sli_stats("sli_a") is None
        assert inst.get_sli_stats("sli_b") is not None

    def test_reset_all(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_a", 10.0)
        inst.record_insert_timing("sli_b", 20.0)
        inst.reset()
        assert inst.get_sli_stats("sli_a") is None
        assert inst.get_sli_stats("sli_b") is None

    def test_get_all_stats(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_a", 10.0)
        inst.record_insert_timing("sli_b", 20.0)
        all_stats = inst.get_all_stats()
        assert "sli_a" in all_stats
        assert "sli_b" in all_stats

    def test_p50_equals_avg(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_test", 10.0)
        inst.record_insert_timing("sli_test", 20.0)
        stats = inst.get_sli_stats("sli_test")
        assert stats.p50_duration_ms == stats.avg_duration_ms

    def test_p99_equals_max(self):
        inst = SLIInstrumentation()
        inst.record_insert_timing("sli_test", 5.0)
        inst.record_insert_timing("sli_test", 15.0)
        stats = inst.get_sli_stats("sli_test")
        assert stats.p99_duration_ms == stats.max_duration_ms
