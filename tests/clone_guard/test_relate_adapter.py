# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_relate_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_relate_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""RelateAdapter 单元测试——mock subprocess 调用，不依赖真实 relate CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.relate_adapter import RelateAdapter


def _make_candidate(
    similarity: float = 0.85,
    file: str = "src/new.py",
    function: str = "calc",
    line: int = 10,
    matched_file: str = "src/old.py",
    matched_function: str = "compute",
    matched_line: int = 20,
    import_path: str = "src.old.compute",
) -> dict:
    """构造 relate JSON 输出的单个 candidate 项。"""
    return {
        "file": file,
        "function": function,
        "line": line,
        "similarity": similarity,
        "matched_file": matched_file,
        "matched_function": matched_function,
        "matched_line": matched_line,
        "import_path": import_path,
    }


class TestRelateAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """relate CLI 未安装时返回 False。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_cli_present_no_index_returns_false(self, tmp_path: Path):
        """CLI 存在但索引未建时返回 False。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/relate"):
            assert adapter.health_check() is False

    def test_cli_and_index_present_returns_true(self, tmp_path: Path):
        """CLI 存在且索引已建时返回 True。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/relate"):
            assert adapter.health_check() is True


class TestRelateAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config(self, tmp_path: Path):
        """relate_enabled=False 时降级。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=False))
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_index_not_built_degraded(self, tmp_path: Path):
        """索引未建时降级。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        with patch("shutil.which", return_value="/fake/relate"):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="relate", timeout=300)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_generic_exception_degraded(self, tmp_path: Path):
        """subprocess.run 抛非预期异常时降级。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_bad_exit_code_degraded(self, tmp_path: Path):
        """退出码非 0/1 时降级。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        mock_result = MagicMock(returncode=2, stdout="", stderr="error")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_candidates_returns_empty(self, tmp_path: Path):
        """正常执行但无候选（exit 0）。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"candidates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_candidate_parsed_to_finding(self, tmp_path: Path):
        """正常 candidate 正确解析为 Finding。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        data = {"candidates": [_make_candidate(similarity=0.85)]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.severity == "review"  # 0.85 >= 0.7 → review
        assert f.clone_type == "T2"
        assert f.similarity == 0.85
        assert f.source_file == "src/new.py"
        assert f.source_function == "calc"
        assert f.source_lineno == 10
        assert f.existing_file == "src/old.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 20
        assert f.import_suggestion == "src.old.compute"
        assert f.finding_id == "RL-0-src/new.py-src/old.py"

    def test_severity_never_extract(self, tmp_path: Path):
        """sim=1.0 时 severity 仍为 review（预筛器永不 extract）。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        data = {"candidates": [_make_candidate(similarity=1.0)]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "review"  # 永不 extract

    def test_high_sim_review(self, tmp_path: Path):
        """sim>=0.7 → review。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        data = {"candidates": [_make_candidate(similarity=0.7)]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "review"

    def test_low_sim_acknowledged(self, tmp_path: Path):
        """sim<0.7 → acknowledged。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        data = {"candidates": [_make_candidate(similarity=0.69)]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "acknowledged"

    def test_env_injected(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        cfg = CloneGuardConfig(relate_enabled=True, env={"CUSTOM_VAR": "1"})
        adapter = RelateAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"candidates": []}), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"

    def test_absolute_path_converted_to_relative(self, tmp_path: Path):
        """绝对路径转为相对仓库根目录。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        abs_new = str(tmp_path / "src" / "new.py")
        abs_old = str(tmp_path / "src" / "old.py")
        candidate = _make_candidate(file=abs_new, matched_file=abs_old)
        mock_result = MagicMock(returncode=1, stdout=json.dumps({"candidates": [candidate]}), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/new.py"])
        assert findings[0].source_file == "src/new.py"
        assert findings[0].existing_file == "src/old.py"


class TestRelateSearch:
    """search 测试。"""

    def test_disabled_returns_empty(self, tmp_path: Path):
        """relate_enabled=False 时返回空。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=False))
        assert adapter.search("query") == []

    def test_cli_missing_returns_empty(self, tmp_path: Path):
        """CLI 未安装时返回空。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        with patch("shutil.which", return_value=None):
            assert adapter.search("query") == []

    def test_search_results_parsed(self, tmp_path: Path):
        """search 结果正确解析为 Finding（severity=acknowledged）。"""
        index_path = tmp_path / ".relate" / "index"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.touch()
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        data = {"candidates": [_make_candidate(similarity=0.5)]}  # < 0.7 → acknowledged
        mock_result = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/relate"):
            with patch("subprocess.run", return_value=mock_result):
                results = adapter.search("query")
        assert len(results) == 1
        assert results[0].severity == "acknowledged"
        assert results[0].clone_type == "T2"
