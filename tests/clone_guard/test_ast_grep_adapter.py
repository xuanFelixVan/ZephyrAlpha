# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_ast_grep_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_ast_grep_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""AstGrepAdapter 单元测试——mock subprocess 调用，不依赖真实 ast-grep CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.ast_grep_adapter import AstGrepAdapter


def _make_rule_file(tmp_path: Path, name: str = "test-rule.yaml") -> Path:
    """创建测试规则文件。"""
    rules_dir = tmp_path / "src" / "zephyr" / "clone_guard" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_file = rules_dir / name
    rule_file.write_text(
        "id: test-rule\nlanguage: Python\nrule:\n  kind: except_clause\nmessage: test message\nseverity: warning\n",
        encoding="utf-8",
    )
    return rules_dir


def _make_match(file_path: str, line: int = 2, rule_id: str = "no-bare-except") -> dict:
    """构造 ast-grep JSON 输出的单个 match 项。"""
    return {
        "text": "except:\n    pass",
        "range": {
            "byteOffset": {"start": 16, "end": 33},
            "start": {"line": line, "column": 0},
            "end": {"line": line + 1, "column": 8},
        },
        "file": file_path,
        "lines": "except:\n    pass\n",
        "language": "Python",
        "ruleId": rule_id,
        "severity": "warning",
        "note": None,
        "message": "bare except",
        "labels": [],
    }


class TestAstGrepAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """ast-grep CLI 未安装时返回 False。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_no_rules_dir_returns_false(self, tmp_path: Path):
        """规则目录不存在时返回 False。"""
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            assert adapter.health_check() is False

    def test_empty_rules_dir_returns_false(self, tmp_path: Path):
        """规则目录无 .yaml 文件时返回 False。"""
        (tmp_path / "clone_guard" / "rules").mkdir(parents=True)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            assert adapter.health_check() is False

    def test_cli_and_rules_present_returns_true(self, tmp_path: Path):
        """CLI 存在 + 规则文件存在时返回 True。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            assert adapter.health_check() is True


class TestAstGrepAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files_returns_empty_no_degraded(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_rules_dir_degraded(self, tmp_path: Path):
        """规则目录不存在时降级。"""
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_empty_rules_dir_degraded(self, tmp_path: Path):
        """规则目录无 .yaml 文件时降级。"""
        (tmp_path / "clone_guard" / "rules").mkdir(parents=True)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="ast-grep", timeout=30)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_rule_parse_error_exit_code_8_degraded(self, tmp_path: Path):
        """exit_code=8（规则解析错误）时降级。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=8, stdout="", stderr="parse error")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_matches_returns_empty(self, tmp_path: Path):
        """正常执行但无匹配。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout="[]", stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_match_finding_parsed(self, tmp_path: Path):
        """正常匹配的 finding 正确解析。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        match_data = [_make_match(file_path="src/foo.py", line=2, rule_id="no-bare-except")]
        mock_result = MagicMock(returncode=1, stdout=json.dumps(match_data), stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.severity == "review"  # warning → review
        assert f.clone_type == "rule"
        assert f.similarity == 1.0
        assert f.source_file == "src/foo.py"
        assert f.source_lineno == 3  # 0-indexed line=2 → 1-indexed lineno=3
        assert f.existing_function == "no-bare-except"
        assert f.import_suggestion is None
        assert f.finding_id.startswith("SG-no-bare-except-")

    def test_error_severity_mapped_to_extract(self, tmp_path: Path):
        """ast-grep severity=error → CloneGuard severity=extract。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        match_data = [_make_match(file_path="src/foo.py", rule_id="critical-rule")]
        match_data[0]["severity"] = "error"
        mock_result = MagicMock(returncode=1, stdout=json.dumps(match_data), stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "extract"

    def test_multiple_matches_parsed(self, tmp_path: Path):
        """多个匹配正确解析。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        match_data = [
            _make_match(file_path="src/foo.py", line=2, rule_id="rule-a"),
            _make_match(file_path="src/bar.py", line=10, rule_id="rule-b"),
        ]
        mock_result = MagicMock(returncode=1, stdout=json.dumps(match_data), stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py", "src/bar.py"])
        assert len(findings) == 2
        assert findings[0].source_file == "src/foo.py"
        assert findings[1].source_file == "src/bar.py"

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=1, stdout="not json{", stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_multiple_rule_files_all_scanned(self, tmp_path: Path):
        """多个规则文件都被扫描。"""
        rules_dir = _make_rule_file(tmp_path, "rule-a.yaml")
        (rules_dir / "rule-b.yaml").write_text(
            "id: rule-b\nlanguage: Python\nrule:\n  kind: pass_statement\n", encoding="utf-8"
        )
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout="[]", stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        # 2 rule files → 2 subprocess calls
        assert mock_run.call_count == 2

    def test_env_injected(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        _make_rule_file(tmp_path)
        cfg = CloneGuardConfig(env={"CUSTOM_VAR": "1"})
        adapter = AstGrepAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout="[]", stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"

    def test_absolute_path_converted_to_relative(self, tmp_path: Path):
        """绝对路径的 file 字段转为相对路径。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        abs_path = str(tmp_path / "src" / "foo.py")
        match_data = [_make_match(file_path=abs_path, line=2)]
        mock_result = MagicMock(returncode=1, stdout=json.dumps(match_data), stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].source_file == "src/foo.py"

    def test_subprocess_exception_degraded(self, tmp_path: Path):
        """subprocess.run 抛非 FileNotFoundError 异常时降级。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True


class TestPathNormalization:
    """路径归一化测试。"""

    def test_backslash_normalized(self, tmp_path: Path):
        """Windows 路径反斜杠归一化为正斜杠。"""
        _make_rule_file(tmp_path)
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        match_data = [_make_match(file_path="src\\foo.py", line=2)]
        mock_result = MagicMock(returncode=1, stdout=json.dumps(match_data), stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].source_file == "src/foo.py"

    def test_existing_file_path_normalized(self, tmp_path: Path):
        """规则文件路径归一化为正斜杠。"""
        rules_dir = _make_rule_file(tmp_path, "test-rule.yaml")
        adapter = AstGrepAdapter(tmp_path, CloneGuardConfig())
        match_data = [_make_match(file_path="src/foo.py", line=2, rule_id="test-rule")]
        mock_result = MagicMock(returncode=1, stdout=json.dumps(match_data), stderr="")
        with patch("shutil.which", return_value="/fake/ast-grep"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        # existing_file 应为 clone_guard/rules/test-rule.yaml（正斜杠）
        assert "/" in findings[0].existing_file
        assert "\\" not in findings[0].existing_file
