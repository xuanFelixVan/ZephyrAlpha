# [A_test] module_id: MOD-GOV_migration_strategy | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-408 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_migration_strategy
# [INVARIANTS] MIGRATION_PIPELINE covers all MigrationPhase; get_next_phase returns successor or None
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_migration_strategy.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.migration_strategy import (
    MIGRATION_PIPELINE,
    MigrationPhase,
    PhaseDef,
    get_next_phase,
    get_phase_def,
)


class TestMigrationPhase:
    def test_all_phases(self):
        expected = {
            "ISSUE_TRACKING",
            "RISK_ASSESSMENT",
            "ROLLBACK_PLAN",
            "STAGING",
            "PILOT",
            "FULL_ROLLOUT",
            "POSTMORTEM",
        }
        actual = {p.value for p in MigrationPhase}
        assert actual == expected


class TestPhaseDef:
    def test_creation_defaults(self):
        pd = PhaseDef(phase=MigrationPhase.ISSUE_TRACKING, label="test")
        assert pd.predecessor is None
        assert pd.successor is None
        assert pd.confidence_threshold == 0.95


class TestMigrationPipeline:
    def test_all_phases_have_defs(self):
        for phase in MigrationPhase:
            assert phase in MIGRATION_PIPELINE

    def test_pipeline_chain(self):
        current = MigrationPhase.ISSUE_TRACKING
        visited = [current]
        while True:
            nxt = get_next_phase(current)
            if nxt is None:
                break
            visited.append(nxt)
            current = nxt
        assert visited[-1] == MigrationPhase.POSTMORTEM
        assert len(visited) == len(MigrationPhase)

    def test_first_phase_has_no_predecessor(self):
        first = MIGRATION_PIPELINE[MigrationPhase.ISSUE_TRACKING]
        assert first.predecessor is None

    def test_last_phase_has_no_successor(self):
        last = MIGRATION_PIPELINE[MigrationPhase.POSTMORTEM]
        assert last.successor is None


class TestGetPhaseDef:
    def test_known_phase(self):
        result = get_phase_def(MigrationPhase.STAGING)
        assert result is not None
        assert result.phase == MigrationPhase.STAGING

    def test_all_phases_retrievable(self):
        for phase in MigrationPhase:
            assert get_phase_def(phase) is not None


class TestGetNextPhase:
    def test_from_issue_tracking(self):
        result = get_next_phase(MigrationPhase.ISSUE_TRACKING)
        assert result == MigrationPhase.RISK_ASSESSMENT

    def test_from_postmortem(self):
        result = get_next_phase(MigrationPhase.POSTMORTEM)
        assert result is None

    def test_chain_integrity(self):
        current = MigrationPhase.ISSUE_TRACKING
        phases = []
        while current is not None:
            phases.append(current)
            current = get_next_phase(current)
        assert len(phases) == len(MigrationPhase)


class TestBoundary:
    def test_all_labels_non_empty(self):
        for phase, pd in MIGRATION_PIPELINE.items():
            assert pd.label != ""

    def test_confidence_thresholds_in_range(self):
        for phase, pd in MIGRATION_PIPELINE.items():
            assert 0.0 < pd.confidence_threshold <= 1.0
