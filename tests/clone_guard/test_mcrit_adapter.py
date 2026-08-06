# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_mcrit_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_mcrit_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_autonomy
# [TTL] permanent
"""McritAdapter 单元测试——mock subprocess 调用，不依赖真实 mcrit CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.mcrit_adapter import McritAdapter


def _make_match(
    similarity: float = 0.9,
    file: str = "src/new.py",
    function: str = "calc",
    line: int = 10,
    matched_file: str = "src/old.py",
    matched_function: str = "compute",
    matched_line: int = 20,
) -> dict:
    """构造 mcrit JSON 输出的单个 match 项。"""
    return {
        "function": function,
        "file": file,
        "line": line,
        "similarity": similarity,
        "matched_function": matched_function,
        "matched_file": matched_file,
        "matched_line": matched_line,
    }


def _ensure_index(tmp_path: Path) -> None:
    """在 tmp_path 下创建 .mcrit/index.db 占位文件，使 _index_path.exists() 为 True。"""
    index_path = tmp_path / ".mcrit" / "index.db"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.touch()


class TestMcritAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """mcrit CLI 未安装时返回 False。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_cli_present_no_index_returns_false(self, tmp_path: Path):
        """CLI 存在但索引未建时返回 False。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/mcrit"):
            assert adapter.health_check() is False

    def test_cli_and_index_present_returns_true(self, tmp_path: Path):
        """CLI 存在且索引已建时返回 True。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/mcrit"):
            assert adapter.health_check() is True


class TestMcritAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config(self, tmp_path: Path):
        """mcrit_enabled=False（默认配置）时降级。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())  # mcrit_enabled 默认 False
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_index_not_built_degraded(self, tmp_path: Path):
        """索引未建时降级。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("shutil.which", return_value="/fake/mcrit"):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="mcrit", timeout=300)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_generic_exception_degraded(self, tmp_path: Path):
        """subprocess.run 抛非预期异常时降级。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_bad_exit_code_degraded(self, tmp_path: Path):
        """退出码非 0 时降级。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        mock_result = MagicMock(returncode=2, stdout="", stderr="error")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_matches_returns_empty(self, tmp_path: Path):
        """正常执行但无匹配（exit 0）。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"matches": []}), stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_match_parsed_to_finding(self, tmp_path: Path):
        """正常 match 正确解析为 Finding。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        data = {"matches": [_make_match(similarity=0.9)]}
        mock_result = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.severity == "extract"  # 0.9 >= 0.85
        assert f.clone_type == "T2"
        assert f.similarity == 0.9
        assert f.source_file == "src/new.py"
        assert f.source_function == "calc"
        assert f.source_lineno == 10
        assert f.existing_file == "src/old.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 20
        assert f.import_suggestion is None
        assert f.finding_id == "MC-0-src/new.py-src/old.py"

    def test_severity_by_similarity(self, tmp_path: Path):
        """按相似度映射 severity：>=0.85→extract, >=0.7→review, else acknowledged。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        data = {"matches": [
            _make_match(similarity=0.9, file="src/a.py", matched_file="src/b.py"),    # extract
            _make_match(similarity=0.85, file="src/c.py", matched_file="src/d.py"),   # extract (边界)
            _make_match(similarity=0.75, file="src/e.py", matched_file="src/f.py"),   # review
            _make_match(similarity=0.7, file="src/g.py", matched_file="src/h.py"),    # review (边界)
            _make_match(similarity=0.6, file="src/i.py", matched_file="src/j.py"),    # acknowledged
        ]}
        mock_result = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert len(findings) == 5
        assert findings[0].severity == "extract"        # 0.9
        assert findings[1].severity == "extract"        # 0.85
        assert findings[2].severity == "review"         # 0.75
        assert findings[3].severity == "review"         # 0.7
        assert findings[4].severity == "acknowledged"   # 0.6

    def test_env_injected(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        _ensure_index(tmp_path)
        cfg = CloneGuardConfig(mcrit_enabled=True, env={"CUSTOM_VAR": "1"})
        adapter = McritAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"matches": []}), stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"

    def test_absolute_path_converted_to_relative(self, tmp_path: Path):
        """绝对路径转为相对仓库根目录。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        abs_new = str(tmp_path / "src" / "new.py")
        abs_old = str(tmp_path / "src" / "old.py")
        data = {"matches": [_make_match(file=abs_new, matched_file=abs_old)]}
        mock_result = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/new.py"])
        assert findings[0].source_file == "src/new.py"
        assert findings[0].existing_file == "src/old.py"


class TestMcritSearch:
    """search 测试。"""

    def test_disabled_returns_empty(self, tmp_path: Path):
        """mcrit_enabled=False（默认配置）时返回空。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())  # mcrit_enabled 默认 False
        assert adapter.search("def foo():") == []

    def test_cli_missing_returns_empty(self, tmp_path: Path):
        """CLI 未安装时返回空。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("shutil.which", return_value=None):
            assert adapter.search("def foo():") == []

    def test_search_results_parsed(self, tmp_path: Path):
        """正常 search 结果解析为 Finding（severity=acknowledged）。"""
        _ensure_index(tmp_path)
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        data = {"results": [
            {
                "file": "src/lib.py",
                "function": "compute",
                "line": 42,
                "similarity": 0.88,
                "import_path": "lib.compute",
            },
        ]}
        mock_result = MagicMock(returncode=0, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/mcrit"):
            with patch("subprocess.run", return_value=mock_result):
                findings = adapter.search("def compute():")
        assert len(findings) == 1
        f = findings[0]
        assert f.severity == "acknowledged"  # 预筛结果不阻断
        assert f.clone_type == "T2"
        assert f.similarity == 0.88
        assert f.source_file == ""  # 搜索场景无 source
        assert f.source_function == ""
        assert f.source_lineno == 0
        assert f.existing_file == "src/lib.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 42
        assert f.import_suggestion == "lib.compute"
        assert f.finding_id == "MC-S0"
