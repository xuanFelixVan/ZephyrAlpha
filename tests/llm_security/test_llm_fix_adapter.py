# [A_test] module_id: MOD-GOV_llm_fix_adapter | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_llm_fix_adapter
# [INVARIANTS] LLM输出MUST经SecretLeakGuard扫描;置信度<MEDIUM不自动应用
# [MODIFY-GUARD] blueprint.md §3;_fixer-registry.yaml llm_fix_adapter段
# [CONSUMERS] CI/CD;pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_llm_fix_adapter.py
# [TTL] task_bound

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.infrastructure.auto_fix_engine.llm_fix_adapter import LLMFixAdapter
from zephyr.infrastructure.auto_fix_engine.models import FixLevel, FixStatus


class TestLLMFixAdapterInstantiation:
    def test_creates_instance_with_correct_fixer_id(self):
        adapter = LLMFixAdapter()
        assert adapter.fixer_id == "llm_fix_adapter"

    def test_creates_instance_with_correct_action_type(self):
        adapter = LLMFixAdapter()
        assert adapter.action_type == "llm_fix"

    def test_creates_instance_with_correct_level(self):
        adapter = LLMFixAdapter()
        assert adapter.level == FixLevel.L2_LLM

    def test_creates_instance_with_correct_dimension(self):
        adapter = LLMFixAdapter()
        assert adapter.dimension == "DIM-SEMANTIC-001"

    def test_secret_guard_initialized(self):
        adapter = LLMFixAdapter()
        assert adapter.secret_guard is not None


class TestLLMFixAdapterScan:
    def test_scan_returns_empty_list(self):
        adapter = LLMFixAdapter()
        assert adapter.scan() == []


class TestLLMFixAdapterFix:
    def test_fix_returns_failed_when_llm_bridge_unavailable(self):
        adapter = LLMFixAdapter()
        adapter.llm_bridge = None
        with patch.object(adapter, "_get_llm_bridge", return_value=None):
            action = adapter.fix("some_file.py")
        assert action.status == FixStatus.FAILED
        assert "LLM bridge not available" in action.metadata.get("error", "")

    def test_fix_returns_failed_for_nonexistent_target(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        with patch.object(adapter, "_get_llm_bridge", return_value=mock_bridge):
            action = adapter.fix("/nonexistent/file.py")
        assert action.status == FixStatus.FAILED
        assert "Target not found" in action.metadata.get("error", "")

    def test_fix_returns_failed_when_llm_returns_empty(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("x = 1\n", encoding="utf-8")
            with patch.object(adapter, "_get_llm_bridge", return_value=mock_bridge):
                with patch.object(adapter, "_call_llm", return_value=""):
                    action = adapter.fix(str(target_file))
            assert action.status == FixStatus.FAILED
            assert "empty response" in action.metadata.get("error", "")

    def test_fix_returns_failed_when_secret_leak_detected(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("x = 1\n", encoding="utf-8")
            leaked_content = 'api_key = "sk-abcdefghijklmnopqrstuvwxyz1234567890"\n'
            with patch.object(adapter, "_get_llm_bridge", return_value=mock_bridge):
                with patch.object(adapter, "_call_llm", return_value=leaked_content):
                    action = adapter.fix(str(target_file))
            assert action.status == FixStatus.FAILED
            assert action.escalated is True
            assert "Secret leak" in action.metadata.get("error", "")

    def test_fix_succeeds_with_clean_llm_output(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("x = 1\n", encoding="utf-8")
            clean_output = "x = 2\n"
            with patch.object(adapter, "_get_llm_bridge", return_value=mock_bridge):
                with patch.object(adapter, "_call_llm", return_value=clean_output):
                    action = adapter.fix(str(target_file), dry_run=True)
            assert action.status == FixStatus.COMPLETED
            assert action.after == clean_output

    def test_fix_dry_run_does_not_modify_file(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            original = "x = 1\n"
            target_file.write_text(original, encoding="utf-8")
            clean_output = "x = 2\n"
            with patch.object(adapter, "_get_llm_bridge", return_value=mock_bridge):
                with patch.object(adapter, "_call_llm", return_value=clean_output):
                    adapter.fix(str(target_file), dry_run=True)
            assert target_file.read_text(encoding="utf-8") == original


class TestLLMFixAdapterBuildFixPrompt:
    def test_build_fix_prompt_contains_target(self):
        adapter = LLMFixAdapter()
        prompt = adapter.build_fix_prompt("test.py", "x = 1")
        assert "test.py" in prompt

    def test_build_fix_prompt_contains_content(self):
        adapter = LLMFixAdapter()
        prompt = adapter.build_fix_prompt("test.py", "x = 1")
        assert "x = 1" in prompt


class TestLLMFixAdapterCallLLM:
    def test_call_llm_with_generate_method(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        mock_bridge.generate.return_value = "fixed code"
        result = adapter.call_llm(mock_bridge, "fix this")
        assert result == "fixed code"

    def test_call_llm_with_call_method(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock(spec=["call"])
        mock_bridge.call.return_value = "fixed code"
        result = adapter.call_llm(mock_bridge, "fix this")
        assert result == "fixed code"

    def test_call_llm_returns_empty_on_exception(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock()
        mock_bridge.generate.side_effect = RuntimeError("API error")
        result = adapter.call_llm(mock_bridge, "fix this")
        assert result == ""

    def test_call_llm_returns_empty_for_bridge_without_methods(self):
        adapter = LLMFixAdapter()
        mock_bridge = MagicMock(spec=[])
        result = adapter.call_llm(mock_bridge, "fix this")
        assert result == ""


class TestLLMFixAdapterValidate:
    def test_validate_returns_invalid_for_nonexistent_target(self):
        adapter = LLMFixAdapter()
        result = adapter.validate("/nonexistent/file.py")
        assert result.valid is False
        assert "Target not found" in result.error

    def test_validate_returns_valid_for_clean_syntax(self):
        adapter = LLMFixAdapter()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("x = 1\n", encoding="utf-8")
            result = adapter.validate(str(target_file))
            assert result.valid is True

    def test_validate_returns_invalid_for_syntax_error(self):
        adapter = LLMFixAdapter()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text("def foo(\n", encoding="utf-8")
            result = adapter.validate(str(target_file))
            assert result.valid is False
            assert "Syntax error" in result.error

    def test_validate_returns_invalid_for_secret_leak(self):
        adapter = LLMFixAdapter()
        with tempfile.TemporaryDirectory() as tmpdir:
            target_file = Path(tmpdir) / "sample.py"
            target_file.write_text('api_key = "sk-abcdefghijklmnopqrstuvwxyz1234567890"\n', encoding="utf-8")
            result = adapter.validate(str(target_file))
            assert result.valid is False


class TestLLMFixAdapterRollback:
    def test_rollback_returns_false(self):
        adapter = LLMFixAdapter()
        assert adapter.rollback("any_target") is False
