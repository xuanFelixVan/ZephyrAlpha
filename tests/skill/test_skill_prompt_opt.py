# [A_test] module_id: MOD-GOV_skill_prompt_opt | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_prompt_opt
# [INVARIANTS] SkillPromptOptimizer methods are classmethods; no state mutation
# [MODIFY-GUARD] changes require review of skill_prompt_opt.py API
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] compute_readability returns dict; compress returns tuple; optimize returns dict
# [TESTS] pytest tests/test_skill_prompt_opt.py -q
# [TTL] task_bound


from zephyr.autonomy_core.skills.skill_prompt_opt import SkillPromptOptimizer


class TestSkillPromptOptimizerComputeReadability:
    def test_easy_text(self):
        text = "The cat sat on the mat. It was happy. The sun was bright."
        result = SkillPromptOptimizer.compute_readability(text)
        assert result["level"] in ("easy", "moderate")
        assert result["words"] > 0
        assert result["sentences"] > 0
        assert result["characters"] > 0

    def test_empty_text(self):
        result = SkillPromptOptimizer.compute_readability("")
        assert result.get("readability", result.get("readability_score", -1)) == 0.0
        assert result["level"] == "unknown"

    def test_single_word(self):
        result = SkillPromptOptimizer.compute_readability("hello")
        assert result["words"] == 1
        assert "readability_score" in result

    def test_complex_text(self):
        text = (
            "Notwithstanding the aforementioned considerations, the implementation "
            "of supplementary methodological frameworks necessitates comprehensive "
            "evaluation of multifaceted parameters."
        )
        result = SkillPromptOptimizer.compute_readability(text)
        assert result["level"] in ("difficult", "very_difficult", "moderate")

    def test_returns_required_keys(self):
        result = SkillPromptOptimizer.compute_readability("Some text here.")
        for key in ("readability_score", "level", "words", "sentences", "characters"):
            assert key in result


class TestSkillPromptOptimizerCompress:
    def test_compress_redundant_phrases(self):
        body = "It is important to note that the system works. Please be aware that it is stable."
        compressed, stats = SkillPromptOptimizer.compress(body)
        assert "It is important to note that" not in compressed
        assert "Please be aware that" not in compressed
        assert stats["chars_saved"] > 0
        assert stats["reduction_pct"] > 0.0

    def test_compress_no_redundancy(self):
        body = "The system works. It is stable."
        compressed, stats = SkillPromptOptimizer.compress(body)
        assert stats["chars_saved"] == 0
        assert stats["reduction_pct"] == 0.0

    def test_compress_empty_string(self):
        compressed, stats = SkillPromptOptimizer.compress("")
        assert compressed == ""
        assert stats["original_length"] == 0

    def test_compress_multiple_blank_lines(self):
        body = "Line one\n\n\n\nLine two"
        compressed, stats = SkillPromptOptimizer.compress(body)
        assert "\n\n\n" not in compressed

    def test_compress_in_order_to(self):
        body = "In order to proceed, click here."
        compressed, stats = SkillPromptOptimizer.compress(body)
        assert "In order to" not in compressed
        assert "to proceed" in compressed

    def test_compress_returns_stats_keys(self):
        body = "Some text here."
        _, stats = SkillPromptOptimizer.compress(body)
        for key in ("original_length", "compressed_length", "chars_saved", "reduction_pct", "reductions"):
            assert key in stats


class TestSkillPromptOptimizerReorderSections:
    def test_reorder_puts_preamble_first(self):
        body = "## 核心操作\nDo stuff\n## 前置条件\nPre-reqs"
        result = SkillPromptOptimizer.reorder_sections(body)
        preamble_pos = result.find("前置条件")
        core_pos = result.find("核心操作")
        assert preamble_pos < core_pos

    def test_reorder_no_sections(self):
        body = "Just plain text without any headers."
        result = SkillPromptOptimizer.reorder_sections(body)
        assert "Just plain text" in result

    def test_reorder_empty_string(self):
        result = SkillPromptOptimizer.reorder_sections("")
        assert result.strip() == ""

    def test_reorder_preserves_all_sections(self):
        body = "## 核心操作\nDo stuff\n## 示例\nExample here\n## 前置条件\nPre-reqs"
        result = SkillPromptOptimizer.reorder_sections(body)
        assert "核心操作" in result
        assert "示例" in result
        assert "前置条件" in result


class TestSkillPromptOptimizerOptimize:
    def test_optimize_with_body(self):
        body = "It is important to note that the system works. ## 核心操作\nDo stuff\n## 前置条件\nPre-reqs"
        result = SkillPromptOptimizer.optimize("SKILL-TEST-001", body=body)
        assert result["skill_id"] == "SKILL-TEST-001"
        assert "improvement_pct" in result
        assert "original_stats" in result
        assert "optimized_stats" in result
        assert "compression" in result
        assert "optimized" in result

    def test_optimize_minimal_body(self):
        result = SkillPromptOptimizer.optimize("SKILL-TEST-002", body="Hello world.")
        assert result["skill_id"] == "SKILL-TEST-002"
        assert "improvement_pct" in result

    def test_optimize_none_body_without_loader(self):
        result = SkillPromptOptimizer.optimize("SKILL-NONEXISTENT", body=None)
        assert result["skill_id"] == "SKILL-NONEXISTENT"
        assert result["improvement_pct"] == 0.0
        assert result["error"] == "failed_to_load_skill"

    def test_optimize_improvement_capped_at_100(self):
        body = "It is important to note that this is a test."
        result = SkillPromptOptimizer.optimize("SKILL-TEST-003", body=body)
        assert result["improvement_pct"] <= 100.0

    def test_optimize_estimated_token_saving(self):
        body = "It is important to note that the system works. Please be aware that it is stable."
        result = SkillPromptOptimizer.optimize("SKILL-TEST-004", body=body)
        assert result["estimated_token_saving"] >= 0
