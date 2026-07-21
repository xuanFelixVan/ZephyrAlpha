# [A_test] module_id: MOD-GOV_position_optimizer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_position_optimizer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_position_optimizer.py -q
# [TTL] task_bound
from zephyr.autonomy_core.context.position_optimizer import PositionOptimizer, PositionScore


class TestPositionScore:
    def test_dataclass_fields(self):
        score = PositionScore(section_name="intro", page=0, priority=0.9, is_optimal=True)
        assert score.section_name == "intro"
        assert score.page == 0
        assert score.priority == 0.9
        assert score.is_optimal is True

    def test_not_optimal(self):
        score = PositionScore(section_name="appendix", page=5, priority=0.1, is_optimal=False)
        assert score.is_optimal is False

    def test_equality(self):
        a = PositionScore(section_name="s1", page=0, priority=1.0, is_optimal=True)
        b = PositionScore(section_name="s1", page=0, priority=1.0, is_optimal=True)
        assert a == b


class TestPositionOptimizerInstantiation:
    def test_create_instance(self):
        opt = PositionOptimizer()
        assert opt is not None

    def test_has_optimize_order(self):
        opt = PositionOptimizer()
        assert callable(getattr(opt, "optimize_order", None))


class TestPositionOptimizerOptimizeOrder:
    def test_returns_position_scores(self):
        opt = PositionOptimizer()
        items = [("ke1", 0.8), ("ke2", 0.5)]
        result = opt.optimize_order(items)
        assert len(result) == 2
        assert all(isinstance(r, PositionScore) for r in result)

    def test_sorted_by_priority_descending(self):
        opt = PositionOptimizer()
        items = [("low", 0.1), ("high", 0.9), ("mid", 0.5)]
        result = opt.optimize_order(items)
        priorities = [r.priority for r in result]
        assert priorities == sorted(priorities, reverse=True)

    def test_top_20_percent_optimal(self):
        opt = PositionOptimizer()
        items = [(f"ke{i}", float(i)) for i in range(10)]
        result = opt.optimize_order(items)
        optimal_count = sum(1 for r in result if r.is_optimal)
        assert optimal_count == 2

    def test_single_item_is_optimal(self):
        opt = PositionOptimizer()
        items = [("only", 1.0)]
        result = opt.optimize_order(items)
        assert len(result) == 1
        assert result[0].is_optimal is True
        assert result[0].page == 0

    def test_empty_list_returns_empty(self):
        opt = PositionOptimizer()
        result = opt.optimize_order([])
        assert result == []

    def test_section_names_preserved(self):
        opt = PositionOptimizer()
        items = [("alpha", 0.3), ("beta", 0.7)]
        result = opt.optimize_order(items)
        names = {r.section_name for r in result}
        assert names == {"alpha", "beta"}

    def test_page_numbers_sequential(self):
        opt = PositionOptimizer()
        items = [("a", 0.9), ("b", 0.6), ("c", 0.3)]
        result = opt.optimize_order(items)
        pages = [r.page for r in result]
        assert pages == [0, 1, 2]

    def test_equal_priorities(self):
        opt = PositionOptimizer()
        items = [("x", 0.5), ("y", 0.5), ("z", 0.5)]
        result = opt.optimize_order(items)
        assert len(result) == 3
        assert all(r.priority == 0.5 for r in result)

    def test_five_items_one_optimal(self):
        opt = PositionOptimizer()
        items = [(f"ke{i}", float(5 - i)) for i in range(5)]
        result = opt.optimize_order(items)
        optimal = [r for r in result if r.is_optimal]
        assert len(optimal) == 1
