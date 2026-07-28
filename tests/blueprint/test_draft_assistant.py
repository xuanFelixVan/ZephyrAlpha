# [A_test] module_id: MOD-GOV_draft_assistant | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-380 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_draft_assistant
# [INVARIANTS] test_draft_assistant must cover DraftAssistant.generate_draft, render_blueprint_skeleton, and boundary conditions
# [MODIFY-GUARD] changes must not reduce test coverage
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all tests must pass with exit 0
# [TESTS] python -m pytest tests/test_draft_assistant.py -q
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

from zephyr.shared.draft.draft_assistant import BlueprintDraft, DraftAssistant, DraftInput


class TestBlueprintDraft:
    def test_default_template_version(self):
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-000000",
            idea_summary="test idea",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=["t1"],
            boundaries=["b1"],
            constraints=["c1"],
            generated_at="2026-01-01T00:00:00+00:00",
        )
        assert draft.template_version == "MTH-012"

    def test_custom_template_version(self):
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-000000",
            idea_summary="test idea",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=[],
            boundaries=[],
            constraints=[],
            generated_at="2026-01-01T00:00:00+00:00",
            template_version="CUSTOM-V1",
        )
        assert draft.template_version == "CUSTOM-V1"


class TestDraftInput:
    def test_defaults(self):
        inp = DraftInput(idea_text="build something")
        assert inp.author == "AI_AGENT"
        assert inp.suggested_module == ""
        assert inp.suggested_layer == "l01-infrastructure"

    def test_custom_values(self):
        inp = DraftInput(
            idea_text="rollback module",
            author="human",
            suggested_module="MOD-INF-021",
            suggested_layer="l02_platform",
        )
        assert inp.author == "human"
        assert inp.suggested_module == "MOD-INF-021"
        assert inp.suggested_layer == "l02_platform"


class TestDraftAssistantInit:
    def test_default_output_dir(self):
        assistant = DraftAssistant()
        assert assistant.output_dir == Path("data/drafts")

    def test_custom_output_dir(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path / "custom")
        assert assistant.output_dir == tmp_path / "custom"

    def test_none_output_dir(self):
        assistant = DraftAssistant(output_dir=None)
        assert assistant.output_dir == Path("data/drafts")


class TestGenerateDraft:
    def test_basic_generation(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(
            idea_text="Implement a rollback system for safe recovery",
            author="tester",
            suggested_module="MOD-INF-021",
            suggested_layer="l02_platform",
        )
        draft = assistant.generate_draft(inp)

        assert isinstance(draft, BlueprintDraft)
        assert draft.draft_id.startswith("DRAFT-")
        assert draft.idea_summary == inp.idea_text[:200]
        assert draft.module_id == "MOD-INF-021"
        assert draft.layer == "l02_platform"
        assert isinstance(draft.targets, list)
        assert isinstance(draft.boundaries, list)
        assert isinstance(draft.constraints, list)
        assert draft.generated_at != ""

    def test_infer_module_from_idea_text(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="Build a task-system for decomposing blueprints")
        draft = assistant.generate_draft(inp)
        assert draft.module_id == "MOD-INF-039"

    def test_infer_module_rollback_keyword(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="Create a rollback mechanism")
        draft = assistant.generate_draft(inp)
        assert draft.module_id == "MOD-INF-021"

    def test_infer_module_pipeline_keyword(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="Design a pipeline for processing")
        draft = assistant.generate_draft(inp)
        assert draft.module_id == "MOD-INF-005"

    def test_infer_module_no_match(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="Something completely unrelated")
        draft = assistant.generate_draft(inp)
        assert draft.module_id == "MOD-INF-TBD"

    def test_infer_layer_default(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="test", suggested_layer="")
        draft = assistant.generate_draft(inp)
        assert draft.layer == "l01-infrastructure"

    def test_suggested_layer_overrides(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="test", suggested_layer="l03_capability")
        draft = assistant.generate_draft(inp)
        assert draft.layer == "l03_capability"

    def test_draft_file_saved(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="Implement a gate check system")
        draft = assistant.generate_draft(inp)

        saved_path = tmp_path / f"{draft.draft_id}.json"
        assert saved_path.exists()
        data = json.loads(saved_path.read_text(encoding="utf-8"))
        assert data["draft_id"] == draft.draft_id
        assert data["module_id"] == draft.module_id
        assert data["idea_summary"] == draft.idea_summary

    def test_idea_summary_truncated_at_200(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        long_text = "A" * 300
        inp = DraftInput(idea_text=long_text)
        draft = assistant.generate_draft(inp)
        assert len(draft.idea_summary) == 200

    def test_targets_extracted_from_implement_keyword(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="Implement user authentication. Build logging system.")
        draft = assistant.generate_draft(inp)
        assert len(draft.targets) >= 1
        assert any("implement" in t.lower() or "build" in t.lower() for t in draft.targets)

    def test_targets_fallback_when_no_keywords(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="A vague idea with no action words")
        draft = assistant.generate_draft(inp)
        assert len(draft.targets) >= 1

    def test_boundaries_always_present(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="test")
        draft = assistant.generate_draft(inp)
        assert len(draft.boundaries) > 0

    def test_constraints_always_present(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="test")
        draft = assistant.generate_draft(inp)
        assert len(draft.constraints) > 0


class TestRenderBlueprintSkeleton:
    def test_renders_yaml_frontmatter(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-120000",
            idea_summary="Test idea",
            module_id="MOD-INF-039",
            layer="l01-infrastructure",
            targets=["Target A"],
            boundaries=["Boundary A"],
            constraints=["Constraint A"],
            generated_at="2026-01-01T12:00:00+00:00",
        )
        result = assistant.render_blueprint_skeleton(draft)

        assert 'module_id: "MOD-INF-039"' in result
        assert 'layer: "l01-infrastructure"' in result
        assert 'draft_id: "DRAFT-20260101-120000"' in result
        assert 'generated_at: "2026-01-01T12:00:00+00:00"' in result

    def test_renders_idea_summary(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-120000",
            idea_summary="My great idea",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=[],
            boundaries=[],
            constraints=[],
            generated_at="2026-01-01T12:00:00+00:00",
        )
        result = assistant.render_blueprint_skeleton(draft)
        assert "My great idea" in result

    def test_renders_targets(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-120000",
            idea_summary="test",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=["Build auth", "Add logging"],
            boundaries=[],
            constraints=[],
            generated_at="2026-01-01T12:00:00+00:00",
        )
        result = assistant.render_blueprint_skeleton(draft)
        assert "- Build auth" in result
        assert "- Add logging" in result

    def test_renders_boundaries_and_constraints(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-120000",
            idea_summary="test",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=[],
            boundaries=["No deletion"],
            constraints=["Python 3.10+"],
            generated_at="2026-01-01T12:00:00+00:00",
        )
        result = assistant.render_blueprint_skeleton(draft)
        assert "- No deletion" in result
        assert "- Python 3.10+" in result

    def test_renders_todo_section(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-120000",
            idea_summary="test",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=[],
            boundaries=[],
            constraints=[],
            generated_at="2026-01-01T12:00:00+00:00",
        )
        result = assistant.render_blueprint_skeleton(draft)
        assert "## TODO" in result
        assert "- [ ] Owner review" in result


class TestExtractTargets:
    def test_chinese_implement_keyword(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_targets("实现用户认证功能。构建日志系统。")
        assert len(result) >= 1

    def test_english_develop_keyword(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_targets("Develop a new module. Implement the feature.")
        assert len(result) >= 1

    def test_empty_string(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_targets("")
        assert len(result) == 1

    def test_max_five_targets(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        text = ". ".join(["Implement feature " + str(i) for i in range(10)])
        result = assistant.extract_targets(text)
        assert len(result) <= 5

    def test_target_truncated_at_100(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        long_sentence = "Implement " + "x" * 200
        result = assistant.extract_targets(long_sentence)
        for t in result:
            assert len(t) <= 100


class TestExtractBoundaries:
    def test_returns_default_boundaries(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_boundaries("any text")
        assert "Only create files, never delete" in result
        assert "Follow RULE-ZERO lock protocol" in result

    def test_empty_text(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_boundaries("")
        assert len(result) > 0


class TestExtractConstraints:
    def test_returns_default_constraints(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_constraints("any text")
        assert "Python 3.10+" in result
        assert "UTF-8 encoding required" in result

    def test_empty_text(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        result = assistant.extract_constraints("")
        assert len(result) > 0


class TestBoundaryConditions:
    def test_generate_draft_with_empty_idea(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="")
        draft = assistant.generate_draft(inp)
        assert isinstance(draft, BlueprintDraft)
        assert draft.idea_summary == ""

    def test_generate_draft_with_whitespace_idea(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        inp = DraftInput(idea_text="   ")
        draft = assistant.generate_draft(inp)
        assert isinstance(draft, BlueprintDraft)

    def test_render_skeleton_with_empty_lists(self, tmp_path):
        assistant = DraftAssistant(output_dir=tmp_path)
        draft = BlueprintDraft(
            draft_id="DRAFT-20260101-000000",
            idea_summary="",
            module_id="MOD-INF-TBD",
            layer="l01-infrastructure",
            targets=[],
            boundaries=[],
            constraints=[],
            generated_at="2026-01-01T00:00:00+00:00",
        )
        result = assistant.render_blueprint_skeleton(draft)
        assert "## Targets" in result
        assert "## Boundaries" in result
        assert "## Constraints" in result

    def test_output_dir_created_on_generate(self, tmp_path):
        nested = tmp_path / "deep" / "nested" / "dir"
        assistant = DraftAssistant(output_dir=nested)
        inp = DraftInput(idea_text="test")
        assistant.generate_draft(inp)
        assert nested.exists()
