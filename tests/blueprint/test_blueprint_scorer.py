# [A_test] module_id: SRC-TST-0442 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_blueprint_scorer
# [INVARIANTS] score_blueprint_route returns 0 for no match; score_and_rank_routes sorts desc by score
# [MODIFY-GUARD] src/zephyr/orchestrator/blueprint_scorer.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] score_blueprint_route/score_and_rank_routes never raise
# [TESTS] tests/test_blueprint_scorer.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.quality.blueprint_scorer import score_and_rank_routes, score_blueprint_route


class TestScoreBlueprintRouteInstantiation:
    def test_empty_route_returns_zero(self):
        result = score_blueprint_route({})
        assert result == 0


class TestScoreBlueprintRoutePathPatterns:
    def test_matching_path_pattern(self):
        route = {"path_patterns": ["src/zephyr/orchestrator/*.py"]}
        result = score_blueprint_route(route, path_patterns=["src/zephyr/orchestrator/config_manager.py"])
        assert result == 10

    def test_non_matching_path_pattern(self):
        route = {"path_patterns": ["src/zephyr/shared/*.py"]}
        result = score_blueprint_route(route, path_patterns=["src/zephyr/orchestrator/config_manager.py"])
        assert result == 0

    def test_multiple_matching_paths(self):
        route = {"path_patterns": ["src/zephyr/orchestrator/*.py"]}
        result = score_blueprint_route(
            route,
            path_patterns=[
                "src/zephyr/orchestrator/config_manager.py",
                "src/zephyr/orchestrator/feature_flag.py",
            ],
        )
        assert result == 20

    def test_glob_wildcard_match(self):
        route = {"path_patterns": ["**/*.py"]}
        result = score_blueprint_route(route, path_patterns=["src/zephyr/test.py"])
        assert result == 10

    def test_none_path_patterns(self):
        route = {"path_patterns": ["src/**/*.py"]}
        result = score_blueprint_route(route, path_patterns=None)
        assert result == 0


class TestScoreBlueprintRouteTaskKeywords:
    def test_keyword_in_task_text(self):
        route = {"task_keywords": ["blueprint", "health"]}
        result = score_blueprint_route(route, task_text="check blueprint health")
        assert result == 10

    def test_keyword_not_in_task_text(self):
        route = {"task_keywords": ["quantum"]}
        result = score_blueprint_route(route, task_text="check blueprint health")
        assert result == 0

    def test_keyword_substring_match_in_task_keywords(self):
        route = {"task_keywords": ["blue"]}
        result = score_blueprint_route(route, task_keywords=["blueprint"])
        assert result >= 2

    def test_case_insensitive_keyword_match(self):
        route = {"task_keywords": ["BLUEPRINT"]}
        result = score_blueprint_route(route, task_text="check blueprint health")
        assert result >= 5

    def test_empty_task_text_and_keywords(self):
        route = {"task_keywords": ["blueprint"]}
        result = score_blueprint_route(route, task_keywords=None, task_text="")
        assert result == 0


class TestScoreBlueprintRouteCombined:
    def test_path_and_keyword_both_match(self):
        route = {"path_patterns": ["src/zephyr/orchestrator/*.py"], "task_keywords": ["config"]}
        result = score_blueprint_route(
            route,
            path_patterns=["src/zephyr/orchestrator/config_manager.py"],
            task_text="update config",
        )
        assert result >= 15


class TestScoreAndRankRoutes:
    def test_empty_routes(self):
        result = score_and_rank_routes([])
        assert result == []

    def test_skips_disabled_routes(self):
        routes = [
            {"task_keywords": ["common"], "enabled": False},
            {"task_keywords": ["common"], "enabled": True},
        ]
        result = score_and_rank_routes(routes, task_text="common task")
        assert len(result) == 1

    def test_includes_disabled_when_skip_disabled_false(self):
        routes = [
            {"task_keywords": ["common"], "enabled": False},
        ]
        result = score_and_rank_routes(routes, task_text="common task", skip_disabled=False)
        assert len(result) == 1

    def test_sorted_by_score_desc(self):
        routes = [
            {"task_keywords": ["rare"]},
            {"task_keywords": ["common"]},
        ]
        result = score_and_rank_routes(routes, task_text="common task")
        if len(result) >= 2:
            assert result[0][0] >= result[1][0]

    def test_zero_score_excluded(self):
        routes = [
            {"task_keywords": ["xyz_unlikely_abc"]},
        ]
        result = score_and_rank_routes(routes, task_text="unrelated task")
        assert result == []

    def test_returns_tuple_format(self):
        routes = [
            {"task_keywords": ["blueprint"], "priority": 80},
        ]
        result = score_and_rank_routes(routes, task_text="check blueprint health")
        assert len(result) == 1
        score, priority, route = result[0]
        assert isinstance(score, int)
        assert isinstance(priority, int)
        assert isinstance(route, dict)


class TestBoundary:
    def test_route_with_none_path_patterns_field(self):
        route = {"path_patterns": None}
        result = score_blueprint_route(route, path_patterns=["src/test.py"])
        assert result == 0

    def test_route_with_none_task_keywords_field(self):
        route = {"task_keywords": None}
        result = score_blueprint_route(route, task_text="test")
        assert result == 0

    def test_empty_path_patterns_list(self):
        route = {"path_patterns": []}
        result = score_blueprint_route(route, path_patterns=["src/test.py"])
        assert result == 0

    def test_no_args_returns_zero(self):
        route = {"path_patterns": ["src/**/*.py"], "task_keywords": ["test"]}
        result = score_blueprint_route(route)
        assert result == 0
