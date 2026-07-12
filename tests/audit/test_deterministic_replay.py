# [A_test] module_id: SRC-TST-0745 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_deterministic_replay
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.deterministic_replay
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_deterministic_replay.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.deterministic_replay import (
    DeterministicReplay,
    ReplayRecord,
)


class TestReplayRecord:
    def test_creation(self):
        rec = ReplayRecord(replay_id="abc", seed=42, prompt_hash="def", output="result")
        assert rec.replay_id == "abc"
        assert rec.seed == 42
        assert rec.temperature == 0.0
        assert rec.output == "result"

    def test_default_timestamp(self):
        rec = ReplayRecord(replay_id="x", seed=1, prompt_hash="y")
        assert isinstance(rec.timestamp, float)
        assert rec.timestamp > 0


class TestDeterministicReplay:
    def test_instantiation_defaults(self):
        dr = DeterministicReplay()
        assert dr.records == []

    def test_capture_creates_record(self):
        dr = DeterministicReplay()
        rec = dr.capture("prompt text", "output text", seed=42)
        assert len(dr.records) == 1
        assert rec.seed == 42
        assert rec.output == "output text"
        assert rec.temperature == 0.0

    def test_capture_auto_seed(self):
        dr = DeterministicReplay()
        rec = dr.capture("prompt", "output")
        assert rec.seed > 0
        assert isinstance(rec.seed, int)

    def test_capture_prompt_hash_deterministic(self):
        dr = DeterministicReplay()
        rec1 = dr.capture("same prompt", "out1", seed=1)
        rec2 = dr.capture("same prompt", "out2", seed=2)
        assert rec1.prompt_hash == rec2.prompt_hash

    def test_replay_found(self):
        dr = DeterministicReplay()
        rec = dr.capture("prompt", "output", seed=100)
        found = dr.replay(rec.replay_id)
        assert found is not None
        assert found.output == "output"
        assert found.seed == 100

    def test_replay_not_found(self):
        dr = DeterministicReplay()
        dr.capture("prompt", "output")
        assert dr.replay("nonexistent") is None

    def test_verify_matching_output(self):
        dr = DeterministicReplay()
        rec = dr.capture("prompt", "expected output", seed=1)
        assert dr.verify(rec.replay_id, "expected output") is True

    def test_verify_mismatched_output(self):
        dr = DeterministicReplay()
        rec = dr.capture("prompt", "original", seed=1)
        assert dr.verify(rec.replay_id, "different") is False

    def test_verify_nonexistent_id(self):
        dr = DeterministicReplay()
        assert dr.verify("nonexistent", "anything") is False

    def test_multiple_captures(self):
        dr = DeterministicReplay()
        r1 = dr.capture("p1", "o1", seed=1)
        r2 = dr.capture("p2", "o2", seed=2)
        assert len(dr.records) == 2
        assert dr.replay(r1.replay_id).output == "o1"
        assert dr.replay(r2.replay_id).output == "o2"

    def test_capture_empty_prompt(self):
        dr = DeterministicReplay()
        rec = dr.capture("", "output", seed=1)
        assert rec.prompt_hash != ""
        assert rec.output == "output"
