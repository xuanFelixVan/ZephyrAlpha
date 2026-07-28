# [A_test] module_id: MOD-GOV_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-367 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_context_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_context_engine.py -q
# [TTL] task_bound

"""Test suite for zephyr.infrastructure.shared_services.context_engine."""

import os
import shutil
import tempfile

import pytest

from zephyr.shared.context.context_engine import (
    ContextAssembly,
    ContextEngine,
    ContextSlice,
    TokenBudget,
)


class TestContextSlice:
    def test_instantiation(self):
        cs = ContextSlice(
            file_path="a.py",
            content="print(1)",
            token_estimate=2,
            reason="reference",
        )
        assert cs.file_path == "a.py"
        assert cs.content == "print(1)"
        assert cs.token_estimate == 2
        assert cs.reason == "reference"

    def test_equality(self):
        a = ContextSlice(file_path="x", content="c", token_estimate=1, reason="r")
        b = ContextSlice(file_path="x", content="c", token_estimate=1, reason="r")
        assert a == b


class TestContextAssembly:
    def test_instantiation_defaults(self):
        ca = ContextAssembly(
            task_id="T-001",
            slices=[],
            total_tokens=0,
            max_tokens=20000,
            budget_remaining=20000,
        )
        assert ca.task_id == "T-001"
        assert ca.slices == []
        assert ca.truncated is False

    def test_truncated_flag(self):
        ca = ContextAssembly(
            task_id="T-002",
            slices=[],
            total_tokens=25000,
            max_tokens=20000,
            budget_remaining=-5000,
            truncated=True,
        )
        assert ca.truncated is True


class TestTokenBudget:
    def test_instantiation_defaults(self):
        tb = TokenBudget(max_tokens=20000, used_tokens=0, reserve_tokens=2000)
        assert tb.over_budget is False

    def test_over_budget_flag(self):
        tb = TokenBudget(max_tokens=20000, used_tokens=19000, reserve_tokens=2000, over_budget=True)
        assert tb.over_budget is True


class TestContextEngineInit:
    def test_default_init(self):
        engine = ContextEngine()
        assert engine.max_tokens == 20000
        assert engine.budget.reserve_tokens == 2000

    def test_custom_max_tokens(self):
        engine = ContextEngine(max_tokens=5000)
        assert engine.max_tokens == 5000
        assert engine.budget.reserve_tokens == 500

    def test_custom_project_root(self):
        engine = ContextEngine(project_root=Path("/tmp"))
        assert engine.project_root == Path("/tmp")


from pathlib import Path


class TestAssembleContext:
    @pytest.fixture()
    def tmp_project(self):
        d = tempfile.mkdtemp(prefix="ctx_engine_test_")
        os.makedirs(os.path.join(d, "src"), exist_ok=True)
        f1 = os.path.join(d, "src", "main.py")
        with open(f1, "w", encoding="utf-8") as f:
            f.write("def main():\n    print('hello')\n")
        f2 = os.path.join(d, "src", "utils.py")
        with open(f2, "w", encoding="utf-8") as f:
            f.write("def helper():\n    return 42\n")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_empty_manifest(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        result = engine.assemble_context("T-100", [])
        assert isinstance(result, ContextAssembly)
        assert result.task_id == "T-100"
        assert result.slices == []
        assert result.total_tokens == 0
        assert result.truncated is False

    def test_single_file_manifest(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        manifest = [{"file_path": "src/main.py", "reason": "primary"}]
        result = engine.assemble_context("T-101", manifest)
        assert len(result.slices) == 1
        assert result.slices[0].file_path == "src/main.py"
        assert "print('hello')" in result.slices[0].content
        assert result.slices[0].reason == "primary"
        assert result.total_tokens > 0

    def test_multiple_files_sorted_by_reason(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        manifest = [
            {"file_path": "src/utils.py", "reason": "secondary"},
            {"file_path": "src/main.py", "reason": "primary"},
        ]
        result = engine.assemble_context("T-102", manifest)
        assert len(result.slices) == 2
        assert result.slices[0].reason == "primary"
        assert result.slices[1].reason == "secondary"

    def test_missing_file_skipped_gracefully(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        manifest = [
            {"file_path": "src/nonexistent.py", "reason": "missing"},
            {"file_path": "src/main.py", "reason": "primary"},
        ]
        result = engine.assemble_context("T-103", manifest)
        assert len(result.slices) == 2
        missing_slice = result.slices[0]
        assert missing_slice.file_path == "src/nonexistent.py"
        assert missing_slice.content == ""
        assert missing_slice.token_estimate == 0

    def test_empty_file_path_entry_skipped(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        manifest = [
            {"file_path": "", "reason": "empty"},
            {"file_path": "src/main.py", "reason": "primary"},
        ]
        result = engine.assemble_context("T-104", manifest)
        assert len(result.slices) == 1
        assert result.slices[0].file_path == "src/main.py"

    def test_truncation_when_over_budget(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project), max_tokens=10)
        big_content = "x" * 400
        big_file = os.path.join(tmp_project, "src", "big.py")
        with open(big_file, "w", encoding="utf-8") as f:
            f.write(big_content)
        manifest = [{"file_path": "src/big.py", "reason": "a"}]
        result = engine.assemble_context("T-105", manifest, truncate=True)
        assert result.total_tokens <= engine.budget.max_tokens - engine.budget.reserve_tokens

    def test_no_truncation_flag(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project), max_tokens=10)
        big_content = "y" * 400
        big_file = os.path.join(tmp_project, "src", "big2.py")
        with open(big_file, "w", encoding="utf-8") as f:
            f.write(big_content)
        manifest = [{"file_path": "src/big2.py", "reason": "a"}]
        result = engine.assemble_context("T-106", manifest, truncate=False)
        assert len(result.slices) == 1
        assert result.slices[0].token_estimate == 100


class TestCheckTokenBudget:
    def test_within_budget(self):
        engine = ContextEngine(max_tokens=20000)
        content = "a" * 400
        result = engine.check_token_budget(content)
        assert isinstance(result, TokenBudget)
        assert result.over_budget is False
        assert result.used_tokens == 100

    def test_over_budget(self):
        engine = ContextEngine(max_tokens=100)
        content = "b" * 4000
        result = engine.check_token_budget(content)
        assert result.over_budget is True

    def test_empty_content(self):
        engine = ContextEngine(max_tokens=20000)
        result = engine.check_token_budget("")
        assert result.used_tokens == 0
        assert result.over_budget is False


class TestValidatePipelineModules:
    def test_all_valid_modules(self):
        engine = ContextEngine()
        result = engine.validate_pipeline_modules(["M1", "M2", "M11"])
        assert result == {"M1": True, "M2": True, "M11": True}

    def test_invalid_module(self):
        engine = ContextEngine()
        result = engine.validate_pipeline_modules(["M1", "M99"])
        assert result == {"M1": True, "M99": False}

    def test_empty_list(self):
        engine = ContextEngine()
        result = engine.validate_pipeline_modules([])
        assert result == {}

    def test_full_pipeline(self):
        engine = ContextEngine()
        all_modules = [f"M{i}" for i in range(1, 12)]
        result = engine.validate_pipeline_modules(all_modules)
        assert all(result[k] for k in all_modules)


class TestEstimateTaskTokens:
    @pytest.fixture()
    def tmp_project(self):
        d = tempfile.mkdtemp(prefix="ctx_est_test_")
        os.makedirs(os.path.join(d, "data"), exist_ok=True)
        f1 = os.path.join(d, "data", "config.yaml")
        with open(f1, "w", encoding="utf-8") as f:
            f.write("key: value\n")
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def test_with_manifest_files(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        task_card = {
            "context_assembly_manifest": [
                {"file_path": "data/config.yaml"},
            ]
        }
        result = engine.estimate_task_tokens(task_card)
        assert result > 0

    def test_empty_manifest(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        task_card = {"context_assembly_manifest": []}
        result = engine.estimate_task_tokens(task_card)
        assert result == 0

    def test_missing_manifest_key(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        task_card = {}
        result = engine.estimate_task_tokens(task_card)
        assert result == 0

    def test_nonexistent_file_in_manifest(self, tmp_project):
        engine = ContextEngine(project_root=Path(tmp_project))
        task_card = {
            "context_assembly_manifest": [
                {"file_path": "data/does_not_exist.yaml"},
            ]
        }
        result = engine.estimate_task_tokens(task_card)
        assert result == 0
