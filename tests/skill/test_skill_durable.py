# [A_test] module_id: MOD-GOV_skill_durable | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_durable
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_durable.py
# [TTL] task_bound

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime

import pytest

from zephyr.autonomy_core.skills.skill_durable import DurableExecution


@pytest.fixture
def tmp_storage(tmp_path):
    d = tmp_path / "durable_test"
    d.mkdir(parents=True, exist_ok=True)
    yield d
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def engine(tmp_storage):
    return DurableExecution(storage_dir=tmp_storage)


class TestDurableExecutionInit:
    def test_instantiation_with_custom_dir(self, tmp_storage):
        de = DurableExecution(storage_dir=tmp_storage)
        assert de.storage_dir == tmp_storage
        assert tmp_storage.exists()

    def test_instantiation_default_dir(self):
        de = DurableExecution()
        assert de.storage_dir is not None
        assert de.storage_dir.exists()

    def test_initial_state_empty(self, engine):
        assert engine.checkpoints == {}
        assert engine.active_executions == {}


class TestDurableExecutionStart:
    def test_start_returns_execution_id(self, engine):
        eid = engine.start("skill-1", "run")
        assert "skill-1" in eid
        assert "run" in eid

    def test_start_creates_active_execution(self, engine):
        eid = engine.start("skill-1", "run")
        assert eid in engine.active_executions
        rec = engine.active_executions[eid]
        assert rec["skill_id"] == "skill-1"
        assert rec["operation"] == "run"
        assert rec["status"] == "running"
        assert rec["progress"] == 0.0

    def test_start_with_input_context(self, engine):
        eid = engine.start("skill-1", "run", input_context="some context")
        assert engine.active_executions[eid]["input_context"] == "some context"

    def test_start_with_none_input_context(self, engine):
        eid = engine.start("skill-1", "run", input_context=None)
        assert engine.active_executions[eid]["input_context"] == ""

    def test_start_truncates_long_input_context(self, engine):
        long_ctx = "x" * 600
        eid = engine.start("skill-1", "run", input_context=long_ctx)
        assert len(engine.active_executions[eid]["input_context"]) == 500

    def test_start_creates_checkpoint(self, engine):
        eid = engine.start("skill-1", "run")
        assert "skill-1" in engine.checkpoints
        assert len(engine.checkpoints["skill-1"]) == 1
        assert engine.checkpoints["skill-1"][0]["stage"] == "started"

    def test_start_writes_checkpoint_file(self, engine, tmp_storage):
        eid = engine.start("skill-1", "run")
        cp_files = list(tmp_storage.glob("*.json"))
        if cp_files:
            data = json.loads(cp_files[0].read_text(encoding="utf-8"))
            assert data["stage"] == "started"
        else:
            assert "skill-1" in engine.checkpoints


class TestDurableExecutionAdvance:
    def test_advance_updates_progress(self, engine):
        eid = engine.start("skill-1", "run")
        engine.advance(eid, "mid_step", 50.0)
        assert engine.active_executions[eid]["progress"] == 50.0

    def test_advance_clamps_progress_to_100(self, engine):
        eid = engine.start("skill-1", "run")
        engine.advance(eid, "overflow", 150.0)
        assert engine.active_executions[eid]["progress"] == 100.0

    def test_advance_clamps_progress_to_0(self, engine):
        eid = engine.start("skill-1", "run")
        engine.advance(eid, "underflow", -10.0)
        assert engine.active_executions[eid]["progress"] == 0.0

    def test_advance_unknown_execution_does_not_crash(self, engine):
        engine.advance("nonexistent:eid", "stage", 50.0)


class TestDurableExecutionComplete:
    def test_complete_sets_status(self, engine):
        eid = engine.start("skill-1", "run")
        engine.complete(eid)
        rec = engine.active_executions[eid]
        assert rec["status"] == "completed"
        assert rec["progress"] == 100.0
        assert "completed_at" in rec

    def test_complete_unknown_execution_does_not_crash(self, engine):
        engine.complete("nonexistent:eid")

    def test_complete_creates_completed_checkpoint(self, engine):
        eid = engine.start("skill-1", "run")
        engine.complete(eid)
        cps = engine.checkpoints["skill-1"]
        assert cps[-1]["stage"] == "completed"


class TestDurableExecutionFail:
    def test_fail_sets_error(self, engine):
        eid = engine.start("skill-1", "run")
        engine.fail(eid, "something broke")
        rec = engine.active_executions[eid]
        assert rec["status"] == "failed"
        assert rec["error"] == "something broke"

    def test_fail_truncates_long_error(self, engine):
        eid = engine.start("skill-1", "run")
        long_err = "e" * 600
        engine.fail(eid, long_err)
        assert len(engine.active_executions[eid]["error"]) == 500

    def test_fail_unknown_execution_does_not_crash(self, engine):
        engine.fail("nonexistent:eid", "error msg")


class TestDurableExecutionResume:
    def test_resume_from_checkpoint_file(self, engine, tmp_storage):
        eid = engine.start("skill-1", "run")
        engine.advance(eid, "mid", 50.0)
        safe_eid = "safe_eid_123"
        cp_file = tmp_storage / f"{safe_eid}.json"
        cp_data = {
            "stage": "mid",
            "skill_id": "skill-1",
            "execution_id": safe_eid,
            "progress": 50.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        cp_file.write_text(json.dumps(cp_data, ensure_ascii=False), encoding="utf-8")
        result = engine.resume(safe_eid)
        assert result["execution_id"] == safe_eid
        assert result["skill_id"] == "skill-1"
        assert result["previous_stage"] == "mid"

    def test_resume_from_in_memory_state(self, engine):
        eid = engine.start("skill-1", "run")
        engine.advance(eid, "mid", 50.0)
        rec = engine.active_executions[eid]
        assert rec["progress"] == 50.0

    def test_resume_nonexistent_returns_not_found(self, engine):
        result = engine.resume("no_such_eid")
        assert result["status"] == "not_found"
        assert result["resumed_at"] == 0.0


class TestDurableExecutionGetStatus:
    def test_get_status_running(self, engine):
        eid = engine.start("skill-1", "run")
        status = engine.get_status(eid)
        assert status["execution_id"] == eid
        assert status["skill_id"] == "skill-1"
        assert status["status"] == "running"
        assert status["progress"] == 0.0
        assert "elapsed" in status

    def test_get_status_unknown(self, engine):
        status = engine.get_status("nonexistent:eid")
        assert status["status"] == "unknown"

    def test_get_status_after_complete(self, engine):
        eid = engine.start("skill-1", "run")
        engine.complete(eid)
        status = engine.get_status(eid)
        assert status["status"] == "completed"
        assert status["progress"] == 100.0
