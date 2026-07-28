# [A_test] module_id: MOD-GOV_skill_translator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_translator
# [INVARIANTS] translate returns dict with status key; unknown target_model_family returns translation_failed
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_skill_translator.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_translator import _MODEL_ADAPTATIONS, SkillTranslator


class TestSkillTranslatorInstantiation:
    def test_class_exists(self):
        assert SkillTranslator is not None

    def test_model_adaptations_has_required_families(self):
        for family in ["deepseek", "claude", "openai", "glm"]:
            assert family in _MODEL_ADAPTATIONS

    def test_each_adaptation_has_style_and_phrases(self):
        for family, adapt in _MODEL_ADAPTATIONS.items():
            assert "style" in adapt
            assert "phrases" in adapt


class TestInferSourceFamily:
    def test_detects_claude(self):
        result = SkillTranslator.infer_source_family("This uses Claude and Anthropic models")
        assert result == "claude"

    def test_detects_glm(self):
        result = SkillTranslator.infer_source_family("基于智谱 GLM 模型")
        assert result == "glm"

    def test_detects_openai(self):
        result = SkillTranslator.infer_source_family("Using GPT and OpenAI APIs")
        assert result == "openai"

    def test_defaults_to_deepseek(self):
        result = SkillTranslator.infer_source_family("普通文本没有关键词")
        assert result == "deepseek"

    def test_empty_string_defaults_deepseek(self):
        result = SkillTranslator.infer_source_family("")
        assert result == "deepseek"

    def test_claude_takes_priority_over_openai(self):
        result = SkillTranslator.infer_source_family("Claude is better than GPT")
        assert result == "claude"


class TestTranslate:
    def test_translate_with_custom_body(self):
        body = "MUST ensure all invariants hold"
        result = SkillTranslator.translate("test_skill", "claude", custom_body=body)
        assert result["status"] == "translated"
        assert result["source_family"] == "deepseek"
        assert result["target_model_family"] == "claude"
        assert "Auto-translated" in result["translated"]

    def test_translate_unknown_target_family(self):
        body = "MUST do something"
        result = SkillTranslator.translate("test_skill", "unknown_model", custom_body=body)
        assert result["status"] == "translation_failed"
        assert "Unknown target model family" in result["error"]

    def test_translate_deepseek_to_openai(self):
        body = "MUST ensure quality"
        result = SkillTranslator.translate("s1", "openai", custom_body=body)
        assert result["status"] == "translated"
        assert result["target_model_family"] == "openai"

    def test_translate_deepseek_to_glm(self):
        body = "CRITICAL rule"
        result = SkillTranslator.translate("s2", "glm", custom_body=body)
        assert result["status"] == "translated"
        assert result["target_model_family"] == "glm"

    def test_translate_preserves_length_info(self):
        body = "Some content here"
        result = SkillTranslator.translate("s3", "claude", custom_body=body)
        assert result["original_length"] == len(body)
        assert result["translated_length"] > 0

    def test_translate_with_claude_source_body(self):
        body = "Claude MUST ALWAYS ensure that quality is maintained"
        result = SkillTranslator.translate("s4", "openai", custom_body=body)
        assert result["status"] == "translated"
        assert result["source_family"] == "claude"

    def test_translate_with_glm_source_body(self):
        body = "智谱 GLM 要求: 严格执行"
        result = SkillTranslator.translate("s5", "claude", custom_body=body)
        assert result["status"] == "translated"
        assert result["source_family"] == "glm"

    def test_translate_without_custom_body_skill_loader_fails(self):
        result = SkillTranslator.translate("nonexistent_skill_xyz", "claude")
        assert result["status"] == "translation_failed"
        assert result["error"] == "failed_to_load_skill"

    def test_translate_empty_body(self):
        result = SkillTranslator.translate("s6", "claude", custom_body="")
        assert result["status"] == "translated"

    def test_translate_same_family(self):
        body = "MUST do something"
        result = SkillTranslator.translate("s7", "deepseek", custom_body=body)
        assert result["status"] == "translated"
        assert result["source_family"] == "deepseek"


class TestApplyAdaptation:
    def test_phrase_replacement_appends_target(self):
        body = "MUST ensure quality"
        source = _MODEL_ADAPTATIONS["deepseek"]
        target = _MODEL_ADAPTATIONS["claude"]
        result = SkillTranslator.apply_adaptation(body, target, source)
        assert "MUST" in result
        assert "MUST ALWAYS ensure that" in result

    def test_style_replacement(self):
        body = "structured, step-by-step, table-heavy approach"
        source = _MODEL_ADAPTATIONS["deepseek"]
        target = _MODEL_ADAPTATIONS["claude"]
        result = SkillTranslator.apply_adaptation(body, target, source)
        assert "section-by-section, chain-of-thought, descriptive" in result
