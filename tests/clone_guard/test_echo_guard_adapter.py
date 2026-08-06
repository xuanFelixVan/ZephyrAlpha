# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_echo_guard_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_echo_guard_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""EchoGuardAdapter 单元测试——mock subprocess 调用，不依赖真实 echo-guard CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter, Finding


class TestEchoGuardAdapterHealthCheck:
    """health_check 测试。"""

    def test_no_index_returns_false(self, tmp_path: Path):
        """索引文件不存在时返回 False。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        assert adapter.health_check() is False

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """CLI 未安装时返回 False。"""
        (tmp_path / ".echo-guard" / "index.duckdb").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert adapter.health_check() is False

    def test_cli_ok_returns_true(self, tmp_path: Path):
        """CLI 存在 + 索引存在时返回 True。"""
        (tmp_path / ".echo-guard").mkdir(parents=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            assert adapter.health_check() is True


class TestEchoGuardAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files_returns_empty_no_degraded(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_echo_guard_disabled_returns_degraded(self, tmp_path: Path):
        """echo_guard_enabled=False 时返回空 + degraded=True。"""
        cfg = CloneGuardConfig(echo_guard_enabled=False)
        adapter = EchoGuardAdapter(tmp_path, cfg)
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级（空列表 + degraded=True）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=FileNotFoundError):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="echo-guard", timeout=30)):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_index_exit_code_2_degraded(self, tmp_path: Path):
        """exit_code=2（索引不存在）时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=2, stdout="", stderr="no index")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_unknown_exit_code_degraded(self, tmp_path: Path):
        """未知退出码时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=99, stdout="", stderr="unknown error")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_findings_returns_empty(self, tmp_path: Path):
        """正常执行但无克隆发现。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_match_finding_parsed(self, tmp_path: Path):
        """type=match 的 finding 正确解析为 Finding 对象。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "match",
                    "finding_id": "F-001",
                    "severity": "extract",
                    "clone_type": "T2",
                    "similarity_score": 0.92,
                    "source": {"filepath": "src/new.py", "name": "calc", "lineno": 10},
                    "existing": {"filepath": "src/old.py", "name": "compute", "lineno": 20, "import_suggestion": "from src.old import compute"},
                }
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/new.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.finding_id == "F-001"
        assert f.severity == "extract"
        assert f.clone_type == "T2"
        assert f.similarity == pytest.approx(0.92)
        assert f.source_file == "src/new.py"
        assert f.source_function == "calc"
        assert f.source_lineno == 10
        assert f.existing_file == "src/old.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 20
        assert f.import_suggestion == "from src.old import compute"

    def test_group_finding_parsed(self, tmp_path: Path):
        """type=group 的 finding（多副本组）正确解析为多个 Finding。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "group",
                    "finding_id": "G-001",
                    "severity": "extract",
                    "clone_type": "T3",
                    "similarity_score": 0.88,
                    "functions": [
                        {"filepath": "src/a.py", "name": "fn_a", "lineno": 5},
                        {"filepath": "src/b.py", "name": "fn_b", "lineno": 15},
                        {"filepath": "src/c.py", "name": "fn_c", "lineno": 25},
                    ],
                }
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/a.py"])
        assert degraded is False
        assert len(findings) == 2  # 3 functions → 2 pairs (source vs each existing)
        assert findings[0].source_file == "src/a.py"
        assert findings[0].existing_file == "src/b.py"
        assert findings[1].existing_file == "src/c.py"

    def test_malformed_finding_skipped(self, tmp_path: Path):
        """格式错误的 finding 被跳过（不抛异常）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {"type": "match", "finding_id": "BAD"},  # 缺 source/existing
                {
                    "type": "match", "finding_id": "GOOD",
                    "severity": "review", "clone_type": "T1", "similarity_score": 0.5,
                    "source": {"filepath": "a.py", "name": "f1", "lineno": 1},
                    "existing": {"filepath": "b.py", "name": "f2", "lineno": 2},
                },
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["a.py"])
        assert degraded is False
        assert len(findings) == 1
        assert findings[0].finding_id == "GOOD"
