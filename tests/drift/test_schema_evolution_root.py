# [A_test] module_id: SRC-TST-1532 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_schema_evolution
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.schema_evolution
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_schema_evolution_root.py
# [TTL] task_bound


from zephyr.feedback_loop.collectors.schema_evolution import SchemaEvolution


class TestSchemaEvolutionInstantiation:
    def test_default_version_is_one(self):
        se = SchemaEvolution()
        assert se.version == 1

    def test_custom_version(self):
        se = SchemaEvolution(version=5)
        assert se.version == 5


class TestSchemaEvolutionVersionField:
    def test_version_can_be_set_to_zero(self):
        se = SchemaEvolution(version=0)
        assert se.version == 0

    def test_version_can_be_large(self):
        se = SchemaEvolution(version=9999)
        assert se.version == 9999

    def test_version_is_mutable(self):
        se = SchemaEvolution()
        se.version = 2
        assert se.version == 2

    def test_version_negative(self):
        se = SchemaEvolution(version=-1)
        assert se.version == -1


class TestSchemaEvolutionEquality:
    def test_two_default_instances_are_equal(self):
        a = SchemaEvolution()
        b = SchemaEvolution()
        assert a == b

    def test_different_versions_are_not_equal(self):
        a = SchemaEvolution(version=1)
        b = SchemaEvolution(version=2)
        assert a != b
