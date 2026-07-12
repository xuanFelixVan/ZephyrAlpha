# [A_test] module_id: SRC-TST-1197 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_knowledge_injection
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.knowledge_injection
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_knowledge_injection.py
# [TTL] task_bound


from zephyr.feedback_loop.collectors.knowledge_injection import KnowledgeInjection


class TestKnowledgeInjectionInstantiation:
    def test_default_injected_is_empty_list(self):
        ki = KnowledgeInjection()
        assert ki.injected == []
        assert isinstance(ki.injected, list)

    def test_injected_is_independent_per_instance(self):
        ki1 = KnowledgeInjection()
        ki2 = KnowledgeInjection()
        ki1.inject({"topic": "x"})
        assert len(ki1.injected) == 1
        assert len(ki2.injected) == 0


class TestKnowledgeInjectionInject:
    def test_inject_appends_knowledge(self):
        ki = KnowledgeInjection()
        knowledge = {"topic": "cpu_spike", "remedy": "scale_horizontally"}
        ki.inject(knowledge)
        assert len(ki.injected) == 1
        assert ki.injected[0] == knowledge

    def test_inject_multiple_knowledge_items(self):
        ki = KnowledgeInjection()
        k1 = {"topic": "cpu_spike", "remedy": "scale_horizontally"}
        k2 = {"topic": "mem_leak", "remedy": "restart_service"}
        ki.inject(k1)
        ki.inject(k2)
        assert len(ki.injected) == 2
        assert ki.injected[0] == k1
        assert ki.injected[1] == k2

    def test_inject_preserves_reference(self):
        ki = KnowledgeInjection()
        knowledge = {"topic": "disk_full"}
        ki.inject(knowledge)
        assert ki.injected[0] is knowledge

    def test_inject_empty_dict(self):
        ki = KnowledgeInjection()
        ki.inject({})
        assert len(ki.injected) == 1
        assert ki.injected[0] == {}

    def test_inject_dict_with_nested_structure(self):
        ki = KnowledgeInjection()
        knowledge = {
            "topic": "network_partition",
            "evidence": {"packet_loss_pct": 15.0},
            "tags": ["network", "critical"],
        }
        ki.inject(knowledge)
        assert ki.injected[0]["evidence"]["packet_loss_pct"] == 15.0
        assert ki.injected[0]["tags"] == ["network", "critical"]

    def test_inject_does_not_deduplicate(self):
        ki = KnowledgeInjection()
        knowledge = {"topic": "cpu_spike", "remedy": "scale_horizontally"}
        ki.inject(knowledge)
        ki.inject(knowledge)
        assert len(ki.injected) == 2
