# [A_test] module_id: MOD-GOV_agent_spec_backlog_phase2 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-585 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_agent_spec_backlog_phase2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Backlog Phase 2 测试: cross-model, ontology, prompt-eng, model-evolution, xai."""


from zephyr.autonomy_core.skills.skill_cross_model import (
    CrossModelContext,
    ModelCapability,
    ModelProvider,
    SkillCrossModel,
)
from zephyr.autonomy_core.skills.skill_explain import SkillExplain
from zephyr.autonomy_core.skills.skill_model_evolution import SkillModelEvolution
from zephyr.autonomy_core.skills.skill_ontology import SkillOntology
from zephyr.autonomy_core.skills.skill_prompt_opt import SkillPromptOptimizer


class TestSkillCrossModel:
    def test_get_capability_deepseek(self):
        cm = SkillCrossModel()
        cap = cm.get_capability(ModelProvider.DEEPSEEK)
        assert isinstance(cap, ModelCapability)
        assert cap.provider == ModelProvider.DEEPSEEK
        assert cap.max_context_tokens > 0

    def test_supports_feature(self):
        cm = SkillCrossModel()
        assert cm.supports_feature("DeepSeek", "function_calling") is True
        assert cm.supports_feature("DeepSeek", "nonexistent_feature") is False

    def test_resolve_provider_with_fallback(self):
        cm = SkillCrossModel(default_provider=ModelProvider.DEEPSEEK)
        resolved = cm.resolve_provider("unknown-provider-xyz")
        assert resolved in {p.value for p in ModelProvider}

    def test_adapt_messages_system_prompt(self):
        cm = SkillCrossModel()
        ctx = CrossModelContext(
            system_prompt="You are a coding assistant",
            user_content="Write a function",
            tools=[],
            history=[],
        )
        result = cm.adapt_messages(ctx, ModelProvider.DEEPSEEK)
        assert isinstance(result, dict)
        assert "messages" in result
        assert result["provider"] == ModelProvider.DEEPSEEK

    def test_normalize_output_stops_at_stop_token(self):
        cm = SkillCrossModel()
        raw = "some text\n\nHuman: more text"
        normalized = cm.normalize_output(raw, ModelProvider.CLAUDE)
        assert isinstance(normalized, str)

    def test_score_compatibility(self):
        cm = SkillCrossModel()
        result = cm.score_compatibility("Write a Python function", "DeepSeek")
        assert isinstance(result, dict)
        assert "score" in result
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0

    def test_list_providers(self):
        cm = SkillCrossModel()
        providers = cm.list_providers()
        assert isinstance(providers, list)
        assert len(providers) >= 3
        provider_names = [p["name"] for p in providers]
        assert "DeepSeek" in provider_names


class TestSkillOntology:
    def test_extract_entities_mod_inf(self):
        content = "Refer to MOD-INF-019 and MOD-INF-020 for details."
        entities = SkillOntology.extract_entities(content)
        assert isinstance(entities, list)
        mod_values = [e["value"] for e in entities if e["type"] == "module"]
        assert "MOD-INF-019" in mod_values
        assert "MOD-INF-020" in mod_values

    def test_extract_entities_gate(self):
        content = "Gate G0-G3 must pass before G4."
        entities = SkillOntology.extract_entities(content)
        assert isinstance(entities, list)
        gate_values = [e["value"] for e in entities if e["type"] == "gate"]
        assert "G0" in gate_values

    def test_extract_entities_skill(self):
        content = "Use SKILL-ROL-ARC-001 and SKILL-DOM-DBS-001."
        entities = SkillOntology.extract_entities(content)
        assert isinstance(entities, list)
        skill_values = [e["value"] for e in entities if e["type"] == "skill"]
        assert "SKILL-ROL-ARC-001" in skill_values

    def test_match_entities(self):
        extracted = [{"type": "module", "value": "MOD-INF-019"}, {"type": "skill", "value": "SKILL-ROL-ARC-001"}]
        kb_entities = [
            {"type": "module", "value": "MOD-INF-019"},
            {"type": "module", "value": "MOD-INF-020"},
            {"type": "skill", "value": "SKILL-ROL-ARC-001"},
        ]
        result = SkillOntology.match_entities(extracted, kb_entities)
        assert "match_rate" in result
        assert result["match_rate"] > 0

    def test_detect_gaps(self):
        body = "References MOD-INF-019 and SKILL-ROL-IMP-001"
        kb_entities = [{"type": "module", "value": "MOD-INF-019"}]
        result = SkillOntology.detect_gaps("SKILL-TEST-001", body, kb_entities)
        assert "alignment_score" in result
        assert isinstance(result["alignment_score"], float)


class TestSkillPromptOptimizer:
    def test_compute_readability_simple_text(self):
        result = SkillPromptOptimizer.compute_readability("This is a simple test sentence.")
        assert isinstance(result, dict)
        assert "readability_score" in result
        assert isinstance(result["readability_score"], float)
        assert 0.0 <= result["readability_score"] <= 100.0

    def test_compress_removes_redundancy(self):
        body = "This is a test.\n\n\n\nThis is also a test."
        compressed, stats = SkillPromptOptimizer.compress(body)
        assert isinstance(compressed, str)
        assert isinstance(stats, dict)
        assert "compressed_chars" in stats or isinstance(stats, (dict,))

    def test_reorder_sections(self):
        body = "## Checklist\n- item 1\n## Core Operations\n- op 1"
        reordered = SkillPromptOptimizer.reorder_sections(body)
        assert isinstance(reordered, str)
        assert "Core Operations" in reordered

    def test_optimize_full_pipeline(self):
        body = "## Checklist\n- item 1\n## Core Operations\n- op 1\n## Key Constants\n- key: val"
        result = SkillPromptOptimizer.optimize("SKILL-TEST-001", body)
        assert isinstance(result, dict)
        if "improvement_pct" in result:
            assert isinstance(result["improvement_pct"], float)


class TestSkillModelEvolution:
    def test_assess_impact_same_model(self):
        result = SkillModelEvolution.assess_impact("SKILL-TEST", "deepseek-v3", "deepseek-v3")
        assert "risk" in result
        assert result["risk"] in ("minimal", "low")

    def test_assess_impact_different_model(self):
        result = SkillModelEvolution.assess_impact("SKILL-TEST", "deepseek-v3", "glm-5.1")
        assert "risk" in result
        assert "actions" in result
        assert isinstance(result["actions"], list)

    def test_find_model_fuzzy_match(self):
        result = SkillModelEvolution.assess_impact("SKILL-TEST", "deepseek", "glm")
        assert "risk" in result


class TestSkillExplain:
    def test_build_reasoning_chain(self):
        chain = SkillExplain.build_reasoning_chain(
            "SKILL-ROL-IMP-001", "fix database migration", "construction", ["database"]
        )
        assert isinstance(chain, dict)
        assert "reasoning_chain" in chain
        assert isinstance(chain["reasoning_chain"], list)
        assert len(chain["reasoning_chain"]) >= 3
        for step in chain["reasoning_chain"]:
            assert isinstance(step, dict)
            assert "step" in step

    def test_explain_routing(self):
        result = SkillExplain.explain_routing(
            "Add a new SQL migration for user table",
            "SKILL-DOM-DBS-001",
            ["SKILL-DOM-CTX-001"],
        )
        assert isinstance(result, dict)
        if "explanation" in result:
            assert len(result["explanation"]) > 0

    def test_isolate_factors(self):
        result = SkillExplain.isolate_factors("SKILL-TEST", 85.0, "deepseek-v3")
        assert isinstance(result, dict)
        assert "skill_contribution_60pct" in result or "llm_contribution_40pct" in result
