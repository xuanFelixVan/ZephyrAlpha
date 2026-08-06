# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_redup_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_redup_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""RedupAdapter 单元测试——mock subprocess 调用，不依赖真实 reDUP CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.redup_adapter import RedupAdapter


def _make_duplicate(
    dup_id: str = "d1",
    similarity: float = 0.9,
    clone_type: str = "T3",
    severity: str | None = "high",
    occurrences: list[dict] | None = None,
) -> dict:
    """构造 reDUP JSON 输出的单个 duplicate 项。"""
    if occurrences is None:
        occurrences = [
            {"file": "src/new.py", "function": "calc", "line": 10},
            {"file": "src/old.py", "function": "compute", "line": 20},
        ]
    return {
        "id": dup_id,
        "similarity": similarity,
        "clone_type": clone_type,
        "severity": severity,
        "saved_lines": 15,
        "refactoring_hint": "extract to shared util",
        "occurrences": occurrences,
    }


class TestRedupAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """reDUP CLI 未安装时返回 False。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_cli_present_returns_true(self, tmp_path: Path):
        """CLI 存在时返回 True（reDUP 无需预建索引）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            assert adapter.health_check() is True


class TestRedupAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files_returns_empty_no_degraded(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config_degraded(self, tmp_path: Path):
        """redup_enabled=False 时降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig(redup_enabled=False))
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="redup", timeout=30)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_file_not_found_degraded(self, tmp_path: Path):
        """FileNotFoundError 降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_generic_exception_degraded(self, tmp_path: Path):
        """subprocess.run 抛非预期异常时降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_bad_exit_code_degraded(self, tmp_path: Path):
        """退出码非 0/1 时降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=2, stdout="", stderr="error")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_duplicates_returns_empty(self, tmp_path: Path):
        """正常执行但无发现（exit 0）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"duplicates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_duplicate_parsed_to_finding(self, tmp_path: Path):
        """正常 duplicate 正确解析为 N-1 个 Finding。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = {"duplicates": [_make_duplicate(severity="high", similarity=0.92)]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 1  # 2 occurrences → 1 finding
        f = findings[0]
        assert f.severity == "extract"  # high → extract
        assert f.clone_type == "T3"
        assert f.similarity == 0.92
        assert f.source_file == "src/new.py"
        assert f.source_function == "calc"
        assert f.source_lineno == 10
        assert f.existing_file == "src/old.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 20
        assert f.import_suggestion == "extract to shared util"
        assert f.finding_id.startswith("RD-d1-")

    def test_three_occurrences_two_findings(self, tmp_path: Path):
        """3 个 occurrences → 2 个 Finding。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        dup = _make_duplicate(occurrences=[
            {"file": "src/a.py", "function": "f1", "line": 1},
            {"file": "src/b.py", "function": "f2", "line": 2},
            {"file": "src/c.py", "function": "f3", "line": 3},
        ])
        mock_result = MagicMock(returncode=1, stdout=json.dumps({"duplicates": [dup]}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/a.py"])
        assert len(findings) == 2
        assert findings[0].source_file == "src/a.py"
        assert findings[1].source_file == "src/a.py"

    def test_severity_mapping_medium_to_review(self, tmp_path: Path):
        """reDUP severity=medium → CloneGuard review。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = {"duplicates": [_make_duplicate(severity="medium", similarity=0.88)]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "review"

    def test_severity_inferred_by_occurrence_count(self, tmp_path: Path):
        """无 severity 字段时按副本数推断：3+ 副本 → extract。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        dup = _make_duplicate(
            severity=None, similarity=0.9,
            occurrences=[
                {"file": "src/a.py", "function": "f1", "line": 1},
                {"file": "src/b.py", "function": "f2", "line": 2},
                {"file": "src/c.py", "function": "f3", "line": 3},
            ],
        )
        mock_result = MagicMock(returncode=1, stdout=json.dumps({"duplicates": [dup]}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/a.py"])
        assert findings[0].severity == "extract"  # 3 occurrences → extract

    def test_changed_only_mode_command(self, tmp_path: Path):
        """L1 changed-only 模式构造正确命令。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig(redup_mode="changed-only"))
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"duplicates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert "--changed-only" in cmd
        assert "--min-sim" in cmd
        assert "--semantic" not in cmd

    def test_semantic_mode_command(self, tmp_path: Path):
        """L2 semantic 模式构造正确命令。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig(redup_mode="semantic"))
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"duplicates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert "--semantic" in cmd
        assert "--semantic-threshold" in cmd
        assert "--changed-only" not in cmd

    def test_env_injected(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        cfg = CloneGuardConfig(env={"CUSTOM_VAR": "1"})
        adapter = RedupAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"duplicates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"

    def test_max_groups_in_command(self, tmp_path: Path):
        """redup_max_groups > 0 时加入命令。"""
        cfg = CloneGuardConfig(redup_max_groups=5)
        adapter = RedupAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"duplicates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert "--max-groups" in cmd

    def test_single_occurrence_skipped(self, tmp_path: Path):
        """单个 occurrence（无克隆对）被跳过。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        dup = _make_duplicate(occurrences=[{"file": "src/a.py", "function": "f1", "line": 1}])
        mock_result = MagicMock(returncode=1, stdout=json.dumps({"duplicates": [dup]}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/a.py"])
        assert findings == []


class TestRedupPathNormalization:
    """路径归一化测试。"""

    def test_absolute_path_converted_to_relative(self, tmp_path: Path):
        """绝对路径转为相对仓库根目录。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        abs_new = str(tmp_path / "src" / "new.py")
        abs_old = str(tmp_path / "src" / "old.py")
        dup = _make_duplicate(occurrences=[
            {"file": abs_new, "function": "calc", "line": 10},
            {"file": abs_old, "function": "compute", "line": 20},
        ])
        mock_result = MagicMock(returncode=1, stdout=json.dumps({"duplicates": [dup]}), stderr="")
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/new.py"])
        assert findings[0].source_file == "src/new.py"
        assert findings[0].existing_file == "src/old.py"
