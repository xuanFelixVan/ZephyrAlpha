# [A_test] module_id: SRC-TST-0280 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_adversarial_validation
# [INVARIANTS] Challenge output must question the input claim
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.adversarial_validation import AdversarialValidation


class TestAdversarialValidationInstantiation:
    def test_default_creation(self):
        av = AdversarialValidation()
        assert av is not None


class TestChallenge:
    def test_challenge_returns_list(self):
        av = AdversarialValidation()
        result = av.challenge("system is stable")
        assert isinstance(result, list)

    def test_challenge_contains_claim(self):
        av = AdversarialValidation()
        result = av.challenge("system is stable")
        assert len(result) >= 1
        assert "system is stable" in result[0]

    def test_challenge_questions_claim(self):
        av = AdversarialValidation()
        result = av.challenge("repair succeeded")
        assert "What if" in result[0]
        assert "wrong" in result[0]

    def test_challenge_empty_string(self):
        av = AdversarialValidation()
        result = av.challenge("")
        assert isinstance(result, list)
        assert len(result) >= 1
