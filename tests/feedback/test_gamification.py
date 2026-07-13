# [A_test] module_id: SRC-TST-1038 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_gamification
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cognitive.gamification
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_gamification.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.cognitive.gamification import Gamification


class TestGamificationInstantiation:
    def test_default_values(self):
        g = Gamification()
        assert g.score == 0
        assert g.streak == 0

    def test_custom_values(self):
        g = Gamification(score=100, streak=5)
        assert g.score == 100
        assert g.streak == 5


class TestReward:
    def test_reward_adds_points(self):
        g = Gamification()
        g.reward(10)
        assert g.score == 10

    def test_reward_increments_streak(self):
        g = Gamification()
        g.reward(5)
        assert g.streak == 1

    def test_multiple_rewards_accumulate(self):
        g = Gamification()
        g.reward(10)
        g.reward(20)
        g.reward(5)
        assert g.score == 35
        assert g.streak == 3

    def test_reward_zero_points(self):
        g = Gamification()
        g.reward(0)
        assert g.score == 0
        assert g.streak == 1

    def test_reward_negative_points(self):
        g = Gamification()
        g.reward(-5)
        assert g.score == -5
        assert g.streak == 1

    def test_reward_large_points(self):
        g = Gamification()
        g.reward(1000000)
        assert g.score == 1000000

    def test_reward_from_nonzero_start(self):
        g = Gamification(score=50, streak=3)
        g.reward(10)
        assert g.score == 60
        assert g.streak == 4

    def test_streak_increments_each_reward(self):
        g = Gamification()
        for i in range(10):
            g.reward(1)
        assert g.streak == 10
        assert g.score == 10
