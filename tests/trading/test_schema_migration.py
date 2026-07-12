# [A_test] module_id: SRC-TST-1533 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §test
# [MODULE] tests.test_schema_migration
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_schema_migration.py
# [TTL] task_bound


from zephyr.orchestrator.governance.schema_migration import SchemaMigration


class TestSchemaMigrationInstantiation:
    def test_create_instance(self):
        sm = SchemaMigration()
        assert sm is not None

    def test_initial_version_is_one(self):
        sm = SchemaMigration()
        assert sm.current_version() == 1

    def test_has_migrate_method(self):
        sm = SchemaMigration()
        assert callable(sm.migrate)

    def test_has_rollback_method(self):
        sm = SchemaMigration()
        assert callable(sm.rollback)

    def test_has_current_version_method(self):
        sm = SchemaMigration()
        assert callable(sm.current_version)


class TestCurrentVersion:
    def test_starts_at_one(self):
        sm = SchemaMigration()
        assert sm.current_version() == 1


class TestMigrate:
    def test_migrate_to_higher_version(self):
        sm = SchemaMigration()
        result = sm.migrate(3)
        assert result is True
        assert sm.current_version() == 3

    def test_migrate_to_same_version_fails(self):
        sm = SchemaMigration()
        result = sm.migrate(1)
        assert result is False
        assert sm.current_version() == 1

    def test_migrate_to_lower_version_fails(self):
        sm = SchemaMigration()
        sm.migrate(5)
        result = sm.migrate(3)
        assert result is False
        assert sm.current_version() == 5

    def test_migrate_records_history(self):
        sm = SchemaMigration()
        sm.migrate(2)
        sm.migrate(5)
        assert len(sm._history) == 2
        assert sm._history[0] == {"from": 1, "to": 2}
        assert sm._history[1] == {"from": 2, "to": 5}

    def test_migrate_sequential(self):
        sm = SchemaMigration()
        sm.migrate(2)
        sm.migrate(3)
        sm.migrate(4)
        assert sm.current_version() == 4

    def test_migrate_skip_versions(self):
        sm = SchemaMigration()
        result = sm.migrate(10)
        assert result is True
        assert sm.current_version() == 10


class TestRollback:
    def test_rollback_to_lower_version(self):
        sm = SchemaMigration()
        sm.migrate(5)
        result = sm.rollback(3)
        assert result is True
        assert sm.current_version() == 3

    def test_rollback_to_same_version_fails(self):
        sm = SchemaMigration()
        sm.migrate(5)
        result = sm.rollback(5)
        assert result is False
        assert sm.current_version() == 5

    def test_rollback_to_higher_version_fails(self):
        sm = SchemaMigration()
        sm.migrate(3)
        result = sm.rollback(5)
        assert result is False
        assert sm.current_version() == 3

    def test_rollback_to_one(self):
        sm = SchemaMigration()
        sm.migrate(10)
        result = sm.rollback(1)
        assert result is True
        assert sm.current_version() == 1

    def test_rollback_to_zero(self):
        sm = SchemaMigration()
        result = sm.rollback(0)
        assert result is True
        assert sm.current_version() == 0


class TestMigrateRollbackSequence:
    def test_migrate_then_rollback(self):
        sm = SchemaMigration()
        sm.migrate(5)
        assert sm.current_version() == 5
        sm.rollback(2)
        assert sm.current_version() == 2

    def test_rollback_then_migrate_again(self):
        sm = SchemaMigration()
        sm.migrate(5)
        sm.rollback(2)
        sm.migrate(4)
        assert sm.current_version() == 4
