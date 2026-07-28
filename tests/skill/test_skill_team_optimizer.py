# [A_test] module_id: MOD-GOV_skill_team_optimizer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_team_optimizer
# [INVARIANTS] SkillTeamOptimizer.optimize returns dict with best_team, team_score, compatibility, coverage
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] optimize returns structured dict; _team_score returns tuple of 3 floats
# [TESTS] tests/test_skill_team_optimizer.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_team_optimizer import SkillTeamOptimizer


class TestSkillTeamOptimizerInstantiation:
    def test_class_exists(self):
        assert SkillTeamOptimizer is not None

    def test_compat_score_method(self):
        assert hasattr(SkillTeamOptimizer, "_compat_score")

    def test_coverage_method(self):
        assert hasattr(SkillTeamOptimizer, "_coverage")

    def test_team_score_method(self):
        assert hasattr(SkillTeamOptimizer, "_team_score")


class TestSkillTeamOptimizerCompatScore:
    def test_same_skill_low_score(self):
        score = SkillTeamOptimizer.compat_score("database-specialist", "database-specialist")
        assert score == 0.3

    def test_known_pair(self):
        score = SkillTeamOptimizer.compat_score("database-specialist", "implementer")
        assert score >= 0.9

    def test_unknown_pair_default(self):
        score = SkillTeamOptimizer.compat_score("unknown-a", "unknown-b")
        assert score == 0.5

    def test_slash_prefixed_skill(self):
        score = SkillTeamOptimizer.compat_score("domain/database-specialist", "implementer")
        assert score >= 0.9


class TestSkillTeamOptimizerCoverage:
    def test_full_coverage(self):
        team = ["database-specialist", "mcp-specialist"]
        keywords = ["database", "mcp"]
        cov = SkillTeamOptimizer.coverage(team, keywords)
        assert cov == 1.0

    def test_partial_coverage(self):
        team = ["database-specialist"]
        keywords = ["database", "mcp"]
        cov = SkillTeamOptimizer.coverage(team, keywords)
        assert 0.0 < cov <= 1.0

    def test_no_coverage(self):
        team = ["database-specialist"]
        keywords = ["security"]
        cov = SkillTeamOptimizer.coverage(team, keywords)
        assert cov == 0.0

    def test_empty_keywords(self):
        team = ["database-specialist"]
        cov = SkillTeamOptimizer.coverage(team, [])
        assert cov == 0.0

    def test_empty_team(self):
        cov = SkillTeamOptimizer.coverage([], ["database"])
        assert cov == 0.0


class TestSkillTeamOptimizerTeamScore:
    def test_single_member_team(self):
        total, compat, coverage = SkillTeamOptimizer.team_score(["only-one"], ["db"])
        assert total == 0.3
        assert compat == 0.5
        assert coverage == 0.4

    def test_two_member_team(self):
        total, compat, coverage = SkillTeamOptimizer.team_score(["database-specialist", "implementer"], ["database"])
        assert 0.0 <= total <= 1.0
        assert 0.0 <= compat <= 1.0
        assert 0.0 <= coverage <= 1.0

    def test_empty_team(self):
        total, compat, coverage = SkillTeamOptimizer.team_score([], [])
        assert total == 0.3


class TestSkillTeamOptimizerOptimize:
    def test_database_task(self):
        result = SkillTeamOptimizer.optimize("run database migration with sql")
        assert "database-specialist" in result["best_team"]
        assert "database" in result["task_keywords"]
        assert result["team_score"] > 0.0

    def test_security_task(self):
        result = SkillTeamOptimizer.optimize("check for security injection vulnerabilities")
        assert "lsg-security" in result["best_team"]
        assert "security" in result["task_keywords"]

    def test_empty_description(self):
        result = SkillTeamOptimizer.optimize("")
        assert isinstance(result["best_team"], list)
        assert len(result["best_team"]) > 0

    def test_custom_available_skills(self):
        skills = ["database-specialist", "implementer", "reviewer"]
        result = SkillTeamOptimizer.optimize("some task", available_skills=skills)
        assert isinstance(result["best_team"], list)
        assert len(result["best_team"]) <= 3

    def test_max_team_size(self):
        result = SkillTeamOptimizer.optimize("database task", max_team_size=2)
        assert len(result["best_team"]) <= 2

    def test_result_structure(self):
        result = SkillTeamOptimizer.optimize("fix and repair code")
        assert "task_keywords" in result
        assert "best_team" in result
        assert "team_score" in result
        assert "compatibility" in result
        assert "coverage" in result
        assert "rationale" in result
        assert "alternatives" in result

    def test_alternatives_for_three_member_team(self):
        skills = ["database-specialist", "implementer", "reviewer"]
        result = SkillTeamOptimizer.optimize("database task", available_skills=skills)
        if len(result["best_team"]) == 3:
            assert len(result["alternatives"]) > 0
            assert "team" in result["alternatives"][0]
            assert "score" in result["alternatives"][0]

    def test_rationale_not_empty(self):
        result = SkillTeamOptimizer.optimize("database migration")
        assert len(result["rationale"]) > 0
