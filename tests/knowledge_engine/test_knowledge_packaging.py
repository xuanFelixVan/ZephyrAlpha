# [A_test] module_id: SRC-TST-1200 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_knowledge_packaging
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.knowledge_packaging
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_knowledge_packaging.py
# [TTL] task_bound

from zephyr.feedback_loop.collectors.knowledge_packaging import KnowledgePackaging


class TestKnowledgePackagingInstantiation:
    def test_default_instantiation(self):
        kp = KnowledgePackaging()
        assert kp is not None


class TestKnowledgePackagingPackage:
    def test_package_returns_packaged_true(self):
        kp = KnowledgePackaging()
        result = kp.package({"topic": "risk", "content": "volatility spike"})
        assert result["packaged"] is True

    def test_package_preserves_original_keys(self):
        kp = KnowledgePackaging()
        raw = {"topic": "risk", "content": "volatility spike", "severity": 3}
        result = kp.package(raw)
        assert result["topic"] == "risk"
        assert result["content"] == "volatility spike"
        assert result["severity"] == 3

    def test_package_with_empty_dict(self):
        kp = KnowledgePackaging()
        result = kp.package({})
        assert result == {"packaged": True}

    def test_package_does_not_mutate_input(self):
        kp = KnowledgePackaging()
        raw = {"topic": "risk"}
        result = kp.package(raw)
        assert "packaged" not in raw
        assert result["packaged"] is True

    def test_package_existing_packaged_key_preserved_by_spread(self):
        kp = KnowledgePackaging()
        raw = {"packaged": False, "topic": "test"}
        result = kp.package(raw)
        assert result["packaged"] is False
        assert result["topic"] == "test"

    def test_package_with_none_value_in_dict(self):
        kp = KnowledgePackaging()
        raw = {"topic": None, "content": "value"}
        result = kp.package(raw)
        assert result["packaged"] is True
        assert result["topic"] is None
        assert result["content"] == "value"


class TestKnowledgePackagingBoundaries:
    def test_package_with_nested_dict(self):
        kp = KnowledgePackaging()
        raw = {"meta": {"source": "detector", "version": 2}}
        result = kp.package(raw)
        assert result["packaged"] is True
        assert result["meta"]["source"] == "detector"

    def test_package_with_list_value(self):
        kp = KnowledgePackaging()
        raw = {"tags": ["risk", "volatility"]}
        result = kp.package(raw)
        assert result["tags"] == ["risk", "volatility"]

    def test_package_with_numeric_zero(self):
        kp = KnowledgePackaging()
        raw = {"confidence": 0.0}
        result = kp.package(raw)
        assert result["confidence"] == 0.0
